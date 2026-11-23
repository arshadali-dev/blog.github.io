---
layout: post
title: "Bring Your SQL Skills to Fabric Runtime 2.0: Spark 4.1 in Practice"
seo_title: "Spark 4.1 SQL in Fabric Runtime 2.0 | Arshad Ali"
date: 2026-11-17
published: true
description: "Reuse your SQL skills in Fabric Runtime 2.0 with hands-on Spark 4.1 examples for session variables, CTEs, recursion, SQL scripting, and safer dynamic SQL."
excerpt: "Reuse your SQL skills in Fabric Runtime 2.0 with hands-on Spark 4.1 examples for session variables, CTEs, recursion, SQL scripting, and safer dynamic SQL."
author: Arshad Ali
categories:
  - Data-Engineering
tags:
  - microsoft-fabric
  - apache-spark
  - fabric-runtime
  - data-engineering
  - delta-lake
feature-img: assets/images/spark-sql-workflows-runtime-2-0.png
feature-title: ""
---

# Bring Your SQL Skills to Fabric Runtime 2.0

You should not have to learn a new programming language before you can put your SQL skills to work on a lakehouse.

With Apache Spark 4.1 in Microsoft Fabric Runtime 2.0, we give SQL developers familiar building blocks for more capable workflows: variables, Common Table Expressions (CTEs), recursive queries, and SQL scripting. You can reuse your SQL skills rather than switch languages just to set a parameter or choose a processing branch.

That also makes Runtime 2.0 a more practical destination for existing analytical SQL and SQL-based ETL workflows. More business logic can remain in SQL while Spark handles distributed scans, joins, and aggregations. It is a migration accelerator, not drop-in T-SQL or PL/SQL compatibility: dialect differences, transaction requirements, and performance still need validation.

Runtime 2.0 is generally available. Start with the self-contained examples below, then evaluate one of your own workflows.

## The problem: a SQL workflow split across languages

Consider a sales notebook where queries are SQL, but Python supplies parameters, branches on a batch total, or repeatedly queries a hierarchy. For SQL-centric teams, those wrappers can make the workflow harder to review and maintain.

PySpark remains a good choice for Python libraries and broader application logic. The benefit here is choice: keep SQL-oriented work together when that is the clearest design.

## What is new in Spark 4.1, and what builds on existing SQL?

Not every feature in this tutorial was introduced in Spark 4.1. The value is the **combined SQL experience available in Runtime 2.0**.

| Capability | What to know | Why it matters |
|---|---|---|
| Ordinary CTEs | An existing Spark SQL capability | Preserve readable, named transformation stages |
| Session variables | Available in Runtime 2.0's Spark SQL surface | Make typed, reusable parameters explicit |
| Dynamic SQL | `EXECUTE IMMEDIATE` is available in Runtime 2.0 | Keep metadata-driven execution in SQL |
| Recursive CTEs | Added in Spark 4.1 | Express hierarchy traversal in SQL |
| SQL scripting | Introduced in Spark 4.0; generally available and enabled by default in Spark 4.1 | Coordinate statements with local variables, conditions, loops, and handlers |

No scripting-enablement flag is needed for the default Spark 4.1 configuration.

## Choose your learning path

- **Core path:** [session variables](#1-session-variables-make-your-parameters-explicit), [CTEs](#2-ctes-give-each-transformation-a-name), then [local variables and branching](#4-sql-scripting-keep-variables-and-decisions-together).
- **Go further:** [recursive CTEs](#3-recursive-ctes-walk-a-hierarchy-without-an-application-side-loop), [loops](#5-for-loops-useful-for-control-data-not-millions-of-fact-rows), [error handling](#6-error-handling-handle-a-specific-condition-deliberately), and [dynamic SQL](#7-dynamic-sql-reuse-typed-parameters).

Run the shared setup first. The core path needs only the sales view; the hierarchy section creates its own employee view.

## Download and import the companion notebook

<a href="{{ '/assets/downloads/fabric-sql-enhancements/spark-sql-runtime-2-0.ipynb' | relative_url }}" download>Download the Spark SQL enhancements tutorial notebook (.ipynb)</a>

Choose either entry path in a **development Fabric workspace**:

- **Download:** save the linked `.ipynb` file, select **Import notebook** from the workspace
  toolbar, and open it. If your browser displays JSON, save it with the `.ipynb` extension,
  not `.txt`. The download contains all **15 executable PySpark cells**, explanations, and
  expected results, with no saved outputs or workspace bindings.
- **Copy and paste:** create a blank notebook and paste each code block below into a separate cell.

### Shared setup

1. Select a **Runtime 2.0 Environment**. If you change its runtime, **Save** and **Publish** the Environment before using it. Alternatively, use the workspace's Runtime 2.0 default if there is no Environment override.
2. Keep **PySpark** as the notebook's default language. Each code cell passes SQL text to
   `spark.sql(...)`. No Lakehouse attachment, external data, or package installation is
   required.
3. Start a **fresh Spark session** and run the setup cells below. Then follow either learning path, or select **Run all** in the imported notebook for the complete tutorial.
4. Compare outputs with the expected tables. The handler example deliberately returns `REJECTED`; that is its expected result, not a notebook failure. Stop on unexpected errors rather than skipping ahead.

Optional exercises change existing cells. Restore their original values and queries, or reimport the download, before checking the baseline with **Run all** again.

<div class="note-callout" markdown="1">
<div class="note-title">Use the Spark SQL experience</div>

Run these examples in a **Fabric Spark notebook**, not a Warehouse T-SQL editor or a Lakehouse SQL analytics endpoint. Those are different execution surfaces.<br><br>
Each code block is one PySpark cell. Pass either one top-level SQL statement or one
complete `BEGIN ... END` script to `spark.sql(...)`. Keep a script together rather than
splitting it at its internal semicolons.
</div>

The business logic stays in SQL. `spark.sql(...)` returns a DataFrame; `.show(truncate=False)`
displays its results without shortening values. Setup and variable-assignment cells do
not display a result table.

Check the Spark version:

```python
spark.sql("""
SELECT version() AS spark_version;
""").show(truncate=False)
```

The version should begin with `4.1`. Record the full value if you are validating a migration.

### Create six sales rows

The amounts represent order revenue, not unit prices. Explicit decimals keep the examples appropriate for currency calculations.

```python
spark.sql("""
CREATE OR REPLACE TEMP VIEW sql_sales AS
SELECT
    order_id,
    city,
    product,
    CAST(amount AS DECIMAL(10, 2)) AS amount
FROM VALUES
    (1, 'Seattle',  'Laptop',  1500),
    (2, 'Seattle',  'Monitor',  600),
    (3, 'New York', 'Laptop',  1800),
    (4, 'New York', 'Monitor',  500),
    (5, 'Chicago',  'Laptop',  1700),
    (6, 'Chicago',  'Monitor',  700)
AS source(order_id, city, product, amount);
""")
```

Check the baseline:

```python
spark.sql("""
SELECT COUNT(*) AS order_count, SUM(amount) AS total_sales
FROM sql_sales;
""").show(truncate=False)
```

| order_count | total_sales |
|---:|---:|
| 6 | 6800.00 |

`sql_sales` is a **session-scoped temporary view**. It does not create a persistent table or write files. You can rerun the setup; the view is replaced. After restarting the session, run the setup again.

## 1. Session variables: make your parameters explicit

A threshold should be a parameter, not a string pasted into several queries.

Declare a session variable in a new cell:

```python
spark.sql("""
DECLARE OR REPLACE VARIABLE sql_min_sales DECIMAL(10, 2) DEFAULT 1000.00;
""")
```

Use it in a query:

```python
spark.sql("""
SELECT order_id, city, amount
FROM sql_sales
WHERE amount >= session.sql_min_sales
ORDER BY amount DESC, order_id;
""").show(truncate=False)
```

| order_id | city | amount |
|---:|---|---:|
| 3 | New York | 1800.00 |
| 5 | Chicago | 1700.00 |
| 1 | Seattle | 1500.00 |

Now change the parameter:

```python
spark.sql("""
SET VAR sql_min_sales = 1700.00;
""")
```

Run the query again:

```python
spark.sql("""
SELECT order_id, city, amount
FROM sql_sales
WHERE amount >= session.sql_min_sales
ORDER BY amount DESC, order_id;
""").show(truncate=False)
```

Only New York's `1800.00` order and Chicago's `1700.00` order remain. **The query is unchanged; the parameter is different.**

The same pattern works for a processing date, region, batch ID, or watermark. It reduces the need to construct SQL strings just to change a value.

Three details matter:

- **Session scope:** the value survives between cells in the same Spark session, but not a session restart. Initialize parameters in every scheduled run; do not depend on a previous interactive run.
- **Explicit assignment:** outside a script, use `SET VAR` or `SET VARIABLE` for variable values. Plain `SET` is also used for Spark configuration and is not a substitute.
- **Name resolution:** `session.sql_min_sales` makes the session variable explicit. Avoid giving a variable the same name as an input column.

`OR REPLACE` makes the declaration easy to rerun. These variables are temporary session state, not secrets storage or persistent application configuration.

## 2. CTEs: give each transformation a name

Ordinary CTEs are already familiar to many SQL developers. They let you express a multi-stage transformation without burying the logic inside nested subqueries.

Here we calculate city totals, then keep cities with at least `2300.00` in sales:

```python
spark.sql("""
WITH sales_by_city AS (
    SELECT city, SUM(amount) AS total_sales
    FROM sql_sales
    GROUP BY city
),
qualifying_cities AS (
    SELECT city, total_sales
    FROM sales_by_city
    WHERE total_sales >= 2300.00
)
SELECT city, total_sales
FROM qualifying_cities
ORDER BY total_sales DESC, city;
""").show(truncate=False)
```

| city | total_sales |
|---|---:|
| Chicago | 2400.00 |
| New York | 2300.00 |

Seattle's `2100.00` total is filtered out. The query reads as a sequence of named steps: **aggregate, apply the business threshold, return the result**.

For migration, this is useful because the transformation's structure can remain recognizable to the people who maintain it.

**A CTE is scoped to one statement, not the whole notebook.** It is not a persistent table, a cache, or a guarantee that Spark computes a result only once. Spark still optimizes the query and chooses its execution plan.

## 3. Recursive CTEs: walk a hierarchy without an application-side loop

Organizational charts, product categories, bills of materials, and dependency trees all contain parent-child relationships. Without recursive SQL, a team may need repeated joins at a fixed depth or a loop outside SQL.

Create a small employee hierarchy:

```python
spark.sql("""
CREATE OR REPLACE TEMP VIEW sql_employees AS
SELECT *
FROM VALUES
    ('Alice', CAST(NULL AS STRING)),
    ('Bob',   'Alice'),
    ('Carol', 'Alice'),
    ('David', 'Bob'),
    ('Emma',  'Bob'),
    ('Frank', 'Carol')
AS source(employee, manager);
""")
```

Alice is the root. Bob and Carol report to Alice; David and Emma report to Bob; Frank reports to Carol.

Now walk the hierarchy:

```python
spark.sql("""
WITH RECURSIVE employee_hierarchy (employee, manager, depth) AS (
    SELECT employee, manager, CAST(0 AS INT) AS depth
    FROM sql_employees
    WHERE manager IS NULL

    UNION ALL

    SELECT e.employee, e.manager, CAST(h.depth + 1 AS INT)
    FROM sql_employees e
    JOIN employee_hierarchy h
        ON e.manager = h.employee
)
SELECT employee, manager, depth
FROM employee_hierarchy
ORDER BY depth, employee;
""").show(truncate=False)
```

| employee | manager | depth |
|---|---|---:|
| Alice | NULL | 0 |
| Bob | Alice | 1 |
| Carol | Alice | 1 |
| David | Bob | 2 |
| Emma | Bob | 2 |
| Frank | Carol | 2 |

Read this as two parts:

1. The **anchor** selects the root employees.
2. The **recursive step** finds the direct reports of employees discovered in the preceding iteration.

`UNION ALL` combines those levels. The query stops when the recursive step produces no more rows, subject to Spark's recursion safeguards.

This can move hierarchy traversal out of application code and into one SQL statement. It does **not** make every graph problem inexpensive. Each level can add work, and multiple parent paths can multiply rows.

For production hierarchies, validate unique keys, missing parents, cycles, expected depth, and result size. This sample is a small, acyclic tree; it does not demonstrate general cycle detection. Do not use an arbitrary depth filter to hide incomplete results.

Spark 4.1 defaults to a recursion-level limit of `100` and a recursive-row limit of `1,000,000`, controlled by `spark.sql.cteRecursionLevelLimit` and `spark.sql.cteRecursionRowLimit`. Treat a limit error as a reason to inspect the data and query before increasing a safeguard. Keep aggregates and window functions out of the recursive step; apply them to the completed result where appropriate.

## 4. SQL scripting: keep variables and decisions together

CTEs organize **one query**. SQL scripting coordinates **multiple statements**.

A compound statement starts with `BEGIN` and ends with `END`. Inside it, you can declare
local variables, assign query results with plain `SET`, branch, and run other SQL statements.

Here is a complete script that classifies our sales batch:

```python
spark.sql("""
BEGIN
    DECLARE order_count BIGINT DEFAULT 0;
    DECLARE total_sales DECIMAL(18, 2) DEFAULT 0.00;
    DECLARE review_threshold DECIMAL(18, 2) DEFAULT 6000.00;
    DECLARE batch_status STRING DEFAULT 'NORMAL';

    SET (order_count, total_sales) = (
        SELECT COUNT(*), COALESCE(SUM(amount), 0.00)
        FROM sql_sales
    );

    IF order_count = 0 THEN
        SET batch_status = 'EMPTY';
    ELSEIF total_sales >= review_threshold THEN
        SET batch_status = 'REVIEW';
    ELSE
        SET batch_status = 'NORMAL';
    END IF;

    SELECT order_count, total_sales, review_threshold, batch_status;
END;
""").show(truncate=False)
```

| order_count | total_sales | review_threshold | batch_status |
|---:|---:|---:|---|
| 6 | 6800.00 | 6000.00 | REVIEW |

One aggregate query assigns the row count and revenue total to the two variables, in order. `IF / ELSEIF / ELSE` chooses a status, and the final `SELECT` returns one result.

**Empty means no rows, not zero revenue.** Zero-value orders or purchases offset by refunds can produce a zero total in a nonempty batch. Use `COUNT(*)` to distinguish those cases.

**Try a second branch:** change `review_threshold` to `7000.00` and rerun the whole cell. The status should become `NORMAL`.

**Try the edge cases**, one at a time, keeping the original `6000.00` threshold:

- For an empty batch, change `FROM sql_sales` in this script to `FROM sql_sales WHERE 1 = 0`.
- Restore that query, then replace `SUM(amount)` with `SUM(CAST(0 AS DECIMAL(10, 2)))` to simulate six zero-value orders without changing the source view.

| Scenario | order_count | total_sales | batch_status |
|---|---:|---:|---|
| Empty batch | 0 | 0.00 | EMPTY |
| Six zero-value orders | 6 | 0.00 | NORMAL |

Restore the original aggregate query afterward. These exercises do not modify `sql_sales` or affect the later examples.

Unlike the earlier session parameter, these variables are **local to the block**. Run the complete block each time; its variables are declared and initialized again.

In a real workflow, a branch might select a processing strategy or decide whether to run a write. Here we return a status instead, so the tutorial needs no audit tables, persistent writes, or special cleanup.

## 5. FOR loops: useful for control data, not millions of fact rows

Some workflows genuinely need iteration. SQL scripting lets you iterate over a query result without writing a Python loop.

This example visits **three city summaries**, accumulates their totals, and returns one result:

```python
spark.sql("""
BEGIN
    DECLARE cities_checked INT DEFAULT 0;
    DECLARE checked_total DECIMAL(18, 2) DEFAULT 0.00;

    FOR city_row AS
        SELECT city, SUM(amount) AS city_total
        FROM sql_sales
        GROUP BY city
        ORDER BY city
    DO
        SET cities_checked = cities_checked + 1;
        SET checked_total = checked_total + city_row.city_total;
    END FOR;

    SELECT cities_checked, checked_total;
END;
""").show(truncate=False)
```

| cities_checked | checked_total |
|---:|---:|
| 3 | 6800.00 |

`city_row.city_total` accesses a column from the current loop row.

**This is a syntax example, not an optimization.** For this particular calculation, use a single set-based query instead:

```python
spark.sql("""
SELECT
    COUNT(DISTINCT city) AS cities_checked,
    SUM(amount) AS checked_total
FROM sql_sales;
""").show(truncate=False)
```

You should get the same `3` and `6800.00`.

Use loops for small control lists when each item truly requires a separate operation. Do not translate a row-by-row database cursor over a fact table into a row-by-row Spark loop. A loop does not automatically distribute its iterations, and statements inside it can trigger repeated Spark work.

## 6. Error handling: handle a specific condition deliberately

A migration is not complete if it only preserves the happy path. SQL-centric workflows often include explicit business-rule failures and error handling.

This example rejects a batch whose total exceeds a configured limit. Read it in three steps:

1. **Calculate** the batch total in the outer block.
2. **Validate** inside a small nested block, raising and handling a specific error when the total is too high.
3. **Report** the result after leaving that nested block.

Spark's `raise_error()` raises `USER_RAISED_EXCEPTION`, with SQLSTATE `P0001`. We evaluate it inside an assignment to trigger the exception without emitting an extra query result. The cast supplies the assignment's string type; the function raises an error rather than returning a status. The handler sets the rejection status and reason.

```python
spark.sql("""
BEGIN
    DECLARE allowed_total DECIMAL(18, 2) DEFAULT 6000.00;
    DECLARE actual_total DECIMAL(18, 2) DEFAULT 0.00;
    DECLARE validation_status STRING DEFAULT 'ACCEPTED';
    DECLARE validation_reason STRING DEFAULT 'Within the configured limit';

    SET actual_total = (
        SELECT COALESCE(SUM(amount), 0.00)
        FROM sql_sales
    );

    BEGIN
        DECLARE EXIT HANDLER FOR SQLSTATE 'P0001'
        BEGIN
            SET validation_status = 'REJECTED';
            SET validation_reason =
                'Sales total exceeds the configured limit';
        END;

        IF actual_total > allowed_total THEN
            SET validation_status = CAST(
                raise_error('Sales total exceeds the configured limit')
                AS STRING
            );
        END IF;
    END;

    SELECT
        validation_status,
        actual_total,
        allowed_total,
        validation_reason;
END;
""").show(truncate=False)
```

Expected: one result with `REJECTED`, `6800.00`, `6000.00`, and the explicit rejection reason. `EXIT` leaves the inner block where the handler is declared; the outer block continues to the final `SELECT`.

Change `allowed_total` to `7000.00` and rerun to see the accepted path.

This handler demonstrates a controlled business outcome; **it turns that particular exception into a result**. If your production scheduler must mark the run as failed, let the condition propagate or rethrow it rather than treating a status row as job failure. Unexpected errors should still fail visibly; do not wrap everything in a broad handler that reports success.

Also, `BEGIN ... END` defines a script block, **not a multi-statement transaction**. A handler does not roll back earlier successful writes. Design persistent workflows for retries, idempotency, and the actual transaction guarantees of the target tables.

## 7. Dynamic SQL: reuse typed parameters

Sometimes a workflow must choose a statement at runtime. For example, a metadata-driven
job may select one approved source table from a configuration list and apply a common
validation query. `EXECUTE IMMEDIATE` executes SQL text; typed session variables keep
configurable values separate from that text.

This example keeps the source fixed to demonstrate **session parameters** and
**scalar-result capture** with `INTO`, not a case where dynamic SQL is required.
Run the entire cell: its first two calls initialize the parameters, and its final call
executes the script. `OR REPLACE` makes the declarations safe to rerun.

```python
spark.sql("""
DECLARE OR REPLACE VARIABLE sql_dynamic_city STRING DEFAULT 'Seattle';
""")

spark.sql("""
DECLARE OR REPLACE VARIABLE sql_dynamic_minimum_order DECIMAL(10, 2) DEFAULT 1000.00;
""")

spark.sql("""
BEGIN
    DECLARE qualifying_sales DECIMAL(18, 2) DEFAULT 0.00;

    EXECUTE IMMEDIATE
        'SELECT COALESCE(SUM(amount), 0.00)
         FROM sql_sales
         WHERE city = session.sql_dynamic_city
           AND amount >= session.sql_dynamic_minimum_order'
        INTO qualifying_sales;

    SELECT
        session.sql_dynamic_city AS selected_city,
        session.sql_dynamic_minimum_order AS minimum_order,
        qualifying_sales;
END;
""").show(truncate=False)
```

| selected_city | minimum_order | qualifying_sales |
|---|---:|---:|
| Seattle | 1000.00 | 1500.00 |

The executed SQL reads the two **session-scoped** variables by name. Block-local variables
are not implicitly visible inside its SQL text; `INTO` transfers the returned total to
the local `qualifying_sales` variable. Change a parameter's declaration and rerun the
whole cell to change the filter. The SQL string stays unchanged; no values are concatenated.

This is useful when migrating metadata-driven SQL workflows. But dynamic SQL is not needed for every parameterized query: **use an ordinary query with a session variable when that is enough.**

Value parameters are not raw SQL fragments or a license to access arbitrary objects. For dynamic object names, use Spark's supported `IDENTIFIER` syntax where applicable, validate the allowed targets, and retain normal authorization checks. Never concatenate untrusted input into a statement.

## What actually runs in Spark?

It helps to distinguish the **control flow** from the **data processing**:

- **Session variables** hold small parameter values; they are not distributed datasets.
- **CTEs** describe relational query structure for Spark to analyze and optimize.
- **Recursive CTEs** express an iterative query; depth and branching affect the amount of work.
- **Scripts** coordinate statements and conditions. Their queries still go through Spark's planning and execution machinery.
- **Loops** control repeated operations; they do not turn sequential business logic into parallel execution.

The scale comes from how Spark executes the underlying queries across data partitions. A variable or an `IF` statement is not a performance feature by itself, and rewriting a query as a CTE does not guarantee a faster plan.

Runtime 2.0 also supports Fabric's Native Execution Engine. Evaluate it for your workload, inspect supported operators and fallback behavior, and measure the resulting plans.

The practical improvement here is **a richer SQL programming model on top of a distributed analytical engine**. That is valuable even before you measure any execution-time change.

## Bring an existing SQL workflow across in stages

Start with one analytical batch or transformation workflow, not the most transaction-heavy application in your estate.

| Existing pattern | Runtime 2.0 starting point | What still needs attention |
|---|---|---|
| Parameters repeated in generated SQL | Session variables or bound parameters | Session initialization, types, and name resolution |
| Nested SQL transformations | Named CTEs | Result equivalence and physical plans |
| Hierarchy traversal in application code | Recursive CTEs | Cycles, missing parents, depth, and row growth |
| Python wrappers around SQL decisions | SQL scripting with local variables and `IF` | Scope, errors, and retry behavior |
| Database cursors | Set-based SQL first; small `FOR` loops only where needed | Avoid per-row Spark jobs |
| Generated SQL strings | `EXECUTE IMMEDIATE` with typed session parameters | Safe identifiers and permitted targets |
| Stored procedures and multi-statement transactions | Reworked SQL scripts plus Fabric orchestration | Procedure packaging, transaction boundaries, and operational contracts are not drop-in equivalents |

For T-SQL or PL/SQL migrations, inventory more than syntax. Check date and string functions, null behavior, decimal precision, ANSI arithmetic and cast behavior, collation and case sensitivity, temporary objects, exception semantics, and permissions. Database-specific constructs such as `@variables`, `GO`, or a procedure body will need review rather than being pasted unchanged.

For an existing Fabric Spark workload moving from Runtime 1.3, also validate Spark behavior changes, configured settings, connectors, and custom libraries. Runtime 2.0 changes major components, including Python, Java, and Scala. Use the [Fabric Runtime 2.0 migration guide](https://learn.microsoft.com/en-us/fabric/data-engineering/runtime-2-0-migration-guide), not a runtime dropdown alone, as your production migration plan.

### Validate correctness first, then representative performance

The six-row tutorial is a functional exercise, **not a benchmark**.

For your pilot:

1. Compare output schemas, row counts, duplicate handling, nulls, and monetary totals against the existing implementation.
2. Exercise the normal, empty, nonempty zero-total, rejected, and unexpected-error paths. Confirm that retries cannot duplicate successful writes.
3. Use production-representative data to compare end-to-end duration, capacity consumption, stage behavior, shuffle, spill, and concurrency.
4. Keep data, capacity, cache state, and execution settings comparable. Record whether Native Execution Engine is enabled.
5. Save the executed notebook with its full Spark version, selected Environment, runtime release channel, run timestamp, settings, and outputs. Restart the session and repeat to catch hidden state.

For this tutorial, the key checkpoints are:

| Checkpoint | Expected result |
|---|---|
| Sales baseline | 6 orders, total `6800.00` |
| Session threshold `1000.00` | 3 orders |
| Session threshold `1700.00` | 2 orders |
| CTE city threshold `2300.00` | Chicago `2400.00`; New York `2300.00` |
| Employee hierarchy | 6 employees; maximum depth 2 |
| Script review threshold `6000.00` | `REVIEW` |
| Optional empty-batch exercise | 0 orders, `0.00`, `EMPTY` |
| Optional zero-value exercise | 6 orders, `0.00`, `NORMAL` |
| City loop and set-based equivalent | 3 cities, total `6800.00` |
| Handler limit `6000.00` | Explicit `REJECTED` result |
| Dynamic Seattle query | `1500.00` |

The only objects created here are temporary views and session variables. They remain
available for experimentation until the Spark session ends. Stop the session when you
are finished; it consumes Fabric capacity while active.

## Your SQL skills are the starting point

You do not need to abandon SQL to build more capable analytical workflows in Fabric. With Runtime 2.0 and Spark 4.1, we bring more of the surrounding workflow into the SQL development experience: parameters, hierarchy traversal, decisions, iteration, and explicit error handling.

For SQL developers, that lowers the barrier to getting started. For teams migrating existing analytical SQL applications, it creates more opportunities to preserve readable business logic while adapting execution for a lakehouse and distributed processing.

**Start now with one workflow in a Runtime 2.0 development notebook.** Run these examples, replace the sample views with your own data, and validate the result. Migrate in stages, with evidence, rather than keeping avoidable language-switching workarounds simply because that was how an older runtime worked.

## References

- [Fabric Runtime 2.0](https://learn.microsoft.com/en-us/fabric/data-engineering/runtime-2-0)
- [Migrate from Fabric Runtime 1.3 to Runtime 2.0](https://learn.microsoft.com/en-us/fabric/data-engineering/runtime-2-0-migration-guide)
- [Develop and execute Fabric notebooks](https://learn.microsoft.com/en-us/fabric/data-engineering/author-execute-notebook)
- [Spark 4.1 release notes](https://spark.apache.org/releases/spark-release-4.1.0.html)
- [Spark SQL session variables](https://spark.apache.org/docs/4.1.0/sql-ref-syntax-ddl-declare-variable.html) and [variable assignment](https://spark.apache.org/docs/4.1.0/sql-ref-syntax-aux-set-var.html)
- [Common Table Expressions](https://spark.apache.org/docs/4.1.0/sql-ref-syntax-qry-select-cte.html), [recursive-query error conditions](https://spark.apache.org/docs/4.1.0/sql-error-conditions.html#invalid-recursive-cte), and [recursion configuration limits](https://spark.apache.org/docs/4.1.0/configuration.html)
- [SQL scripting](https://spark.apache.org/docs/4.1.0/sql-ref-scripting.html), [compound statements and handlers](https://spark.apache.org/docs/4.1.0/control-flow/compound-stmt.html), [IF](https://spark.apache.org/docs/4.1.0/control-flow/if-stmt.html), and [FOR](https://spark.apache.org/docs/4.1.0/control-flow/for-stmt.html)

> *Note: This blog post was written with assistance from AI*
