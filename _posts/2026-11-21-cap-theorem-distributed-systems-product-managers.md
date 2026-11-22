---
layout: post
title: "CAP and Beyond: A Product Manager's Guide to Distributed-System Trade-offs"
seo_title: "CAP Theorem and System Design for PMs | Arshad Ali"
date: 2026-11-21
published: false
description: "Understand CAP, PACELC, consistency, replication, sharding, caching, and global availability through practical product decisions and failure scenarios."
excerpt: "Understand CAP, PACELC, consistency, replication, sharding, caching, and global availability through practical product decisions and failure scenarios."
author: Arshad Ali
categories:
  - Product-Management
tags:
  - product-management
  - software-architecture
feature-img: assets/images/cap-theorem-for-product-managers-v2.png
feature-title: ""
---

# CAP and Beyond: A Product Manager's Guide to Distributed-System Trade-offs

The Seattle and London stores sell tickets from **one shared pool for the same concert**.
Their systems keep separate copies of that inventory. Seattle sells the last ticket,
but London's copy still displays **1 available** after the connection breaks.
A customer presses **Buy** at the London store. Can it honestly confirm the purchase?

A PM need not implement the algorithms, but should define **what must stay correct,
what can be stale, what may stop working, and how the product recovers**.

Follow that checkout from the basic trade-off to recovery. **Advanced detail** passages
retain the deeper theory; read them after the examples if this is your first encounter
with distributed systems. For the broader process, see the
[system-design framework for product managers]({% post_url 2026-11-14-system-design-framework-product-managers %}).

> All scenarios and numerical targets below are hypothetical teaching examples, not claims
> about a particular company's implementation or measured results.

Select any diagram to open it at full size.

**Reading path:** [Understand CAP](#cap-what-happens-when-the-network-breaks) ·
[Define the customer promise](#what-should-checkout-promise) ·
[Choose mechanisms](#replication-consensus-and-quorums) ·
[Test recovery](#put-it-together-a-global-checkout).

## CAP: What happens when the network breaks?

A store with one inventory database has one place to check stock. But distant shoppers
wait for that database, and its failure can stop checkout. Keeping another copy, a
**replica**, near London can make reads faster and support recovery.

Now multiple computers exchange messages to deliver one service: a **distributed system**.
A Seattle sale must reach London's copy. A **network partition** prevents some computers
from communicating even while they are healthy. Messages may be delayed or lost;
a timeout cannot reliably distinguish a crashed server from a slow network.

The [CAP theorem, proved by Gilbert and Lynch in 2002](https://cs.nyu.edu/~apanda/classes/sp25/papers/gilbert02brewers.pdf),
establishes that a distributed read/write data service cannot guarantee both
**linearizable consistency** and **availability** in all executions with network partitions.

| Property | Precise meaning | What it does not mean |
| --- | --- | --- |
| **C: Consistency** | Operations behave as though executed atomically on one copy, in an order respecting real-time precedence: **linearizability**. | Every replica physically updates at the same instant, or all business rules are automatically enforced. |
| **A: Availability** | Every operation received by a non-failing node eventually completes with a result permitted by the operation's contract. | Returning an infrastructure error counts as completing a read/write, or the service meets a particular uptime percentage. |
| **P: Partition tolerance** | The design accounts for communication failures that prevent nodes from exchanging messages. | Every operation remains available, or the system survives every possible failure. |

CAP availability sets no response-time deadline. A practical product needs one. Conversely,
a legitimate "sold out" result from a correct reservation is not the same as refusing to
operate because the service cannot coordinate.

### A two-region example

Start with `inventory = 1` in both copies, then break the link. Assume Seattle can complete
the sale, setting inventory to zero; a configuration requiring London's acknowledgment
would instead have to wait or reject the write. A later read reaches London.

London cannot distinguish "Seattle sold the item" from "Seattle did nothing." Guessing
zero is wrong in the second history; returning one is wrong in the first. Waiting helps
if the link heals, but cannot guarantee completion if it never does.

- Returning London's old value preserves a read response but violates linearizability.
- Waiting indefinitely, or rejecting the read because coordination is unavailable,
  preserves consistency but gives up CAP availability.

<figure class="system-design-diagram">
<a href="{{ '/assets/images/cap-theorem/partition-choice.svg' | relative_url }}">
<img src="{{ '/assets/images/cap-theorem/partition-choice.svg' | relative_url }}"
alt="After a partition, Seattle completes a write to zero. London's later read can return stale inventory one or wait or reject because it cannot coordinate."
loading="lazy" width="900" height="780">
</a>
<figcaption>Figure 1. The choice applies to this disconnected read, not automatically to
every operation in the product.</figcaption>
</figure>

CAP is not "pick any two": **CA** assumes partitions away. When communication is healthy,
a service can provide both C and A; during a partition, decide which operations can proceed.

### Choose behavior per operation

**CP-oriented behavior** protects linearizability and may block or reject operations on
the side that cannot coordinate. It need not shut down every region.
**AP-oriented behavior** allows operations to complete on separated sides with weaker
consistency; conflicting updates may then require reconciliation. Neither label promises
immunity to overload or unrelated outages.

Browse a possibly stale catalog, but pause an exclusive reservation if it cannot be made
safely. The product remains partly usable without claiming every operation satisfies CAP
availability. [Brewer's 2012 clarification](https://www.infoq.com/articles/cap-twelve-years-later-how-the-rules-have-changed/)
emphasizes these operation-level choices and recovery after a partition.

## PACELC: The trade-off on a healthy day

CAP does not tell you how fast a global write should be.
[Daniel Abadi's PACELC framework](https://www.cs.umd.edu/~abadi/papers/abadi-pacelc.pdf)
adds the everyday trade-off:

**If a Partition occurs, consider Availability versus Consistency; Else, consider
Latency versus Consistency.**

A Singapore profile update can be acknowledged locally and replicated later, allowing
other regions to read the old profile. A protocol providing global linearizability must
coordinate somewhere in the read/write path. That communication can add latency even
without failures; it does not necessarily require every write to wait for every replica.

<figure class="system-design-diagram">
<a href="{{ '/assets/images/cap-theorem/pacelc.svg' | relative_url }}">
<img src="{{ '/assets/images/cap-theorem/pacelc.svg' | relative_url }}"
alt="PACELC branches on network conditions: during a partition, availability versus consistency; otherwise, latency versus consistency in the read/write path."
loading="lazy" width="900" height="690">
</a>
<figcaption>Figure 2. Partition behavior and everyday latency are separate decisions.
Neither is fully described by a database's name.</figcaption>
</figure>

### Advanced detail: PACELC shorthand

PA/PC describe the partition policy; EL/EC describe the healthy-operation policy:

| Shorthand | During a partition | Otherwise |
| --- | --- | --- |
| PA/EL | Favor availability | Favor lower latency with weaker consistency |
| PC/EC | Preserve consistency | Preserve consistency despite coordination cost |
| PA/EC | Relax consistency to remain available | Provide stronger consistency while coordination works |
| PC/EL | Restrict operations to preserve consistency | Permit lower-latency, weaker-consistency operations |

These are policies, not database identities. Evaluate the operation, configuration, and
topology. Weaker consistency may reduce coordination but add reconciliation and support work.

## What should checkout promise?

Before selecting components, agree on what the product can honestly tell the shopper.
**Authoritative inventory** is the record allowed to decide ownership. An **atomic
reservation** checks and consumes stock together, or does neither. **Allocated rights**
give each region an exclusive subset of inventory to sell without asking the other.

| Operation | Intended degraded behavior | Recovery obligation |
| --- | --- | --- |
| Browse | Serve permitted cached listings without promising stock, or route to a healthy region. | Refresh stale content without flooding the origin. |
| Edit cart | Distinguish local pending edits from confirmed saves under the merge/session contract. | Reconcile conflicts and restore the promised session view. |
| Reserve last item | Confirm only after an atomic check-and-reserve against authoritative inventory or locally allocated rights; otherwise pause. | Establish safe ownership and reconcile reservation state before reopening. |
| Pay | Preserve the attempt ID; show **Checking payment** when the outcome is unknown. | Query or retry within the provider's idempotency contract and reconcile. |
| Notify | Keep durable notification intent even if publication or delivery is unavailable. | Replay safely and monitor backlog age. |

The checkout design must distinguish **a current value**, **an exclusive reservation**,
and **a known payment outcome**. Those are three different promises.

## Choose a consistency contract, not a label

"Strong" needs a defined scope. For overlapping reads and writes, linearizability permits
either ordering; a read starting after a completed write must reflect it or a later write.

For shipping addresses, **read-your-writes** means the customer sees their own saved
edit within the guarantee's scope. A venue description might tolerate **eventual
consistency**: replicas converge after updates stop and communication and reconciliation
succeed. **Bounded staleness** adds an explicit time or version limit.

### Advanced detail: visibility and ordering contracts

These guarantees answer different questions rather than forming a single ladder:

| Contract | What the reader can rely on | PM consideration |
| --- | --- | --- |
| **Read-your-writes** | A client sees its own completed updates within the guarantee's scope. | Carry session/version context across retries and region changes. |
| **Eventual consistency** | Replicas converge if updates stop and the protocol's communication and reconciliation assumptions hold. | No fixed convergence deadline or protection against lost concurrent updates is implied. |
| **Bounded staleness** | Reads lag by no more than a specified time or version bound. | Maintaining the bound can require stopping reads or writes when replication falls behind. |
| **Monotonic reads** | A client does not move backward to an older observed version. | Session routing and failover can affect the guarantee. |
| **Sequential consistency** | One shared order preserving each client's program order, not necessarily cross-client real time. | Ordered does not necessarily mean current. |
| **Causal consistency** | Dependencies appear in order: a reply follows the comment it depends on. | Unrelated concurrent changes need not have a single global order. |
| **Consistent prefix** | Reads expose a prefix of the defined write order, rather than skipping earlier writes. | Not a general substitute for application-wide causal guarantees. |

Session consistency bundles scoped guarantees, not a universal global order.
[Azure Cosmos DB's documented choices](https://learn.microsoft.com/en-us/azure/cosmos-db/consistency-levels)
provide a concrete example of why the exact service definition matters.

### Convergence needs a conflict policy

If two regions independently save different shipping addresses, reconnecting them does not
tell the application which one the customer intended.

- **Last-write-wins:** choose by a defined timestamp/order. Clock skew can affect
  timestamp-based ordering, and legitimate edits can be discarded.
- **Versions or version vectors:** detect stale or concurrent changes; detection does not
  itself resolve the conflict.
- **Application or user resolution:** merge compatible fields or ask which address to keep.
- **CRDTs:** conflict-free replicated data types merge supported operations deterministically,
  under their delivery/merge assumptions. Counters and some collaborative structures fit;
  arbitrary rules such as "only one owner of this seat" do not automatically fit.

Preallocating inventory rights to regions can permit local sales within each allocation,
but an exhausted region must stop or coordinate a transfer. This changes the coordination
boundary; it does not disprove CAP or provide unlimited availability.

## ACID, BASE, and business correctness

**Fresh reads alone do not prevent overselling.** Two clients can each read `inventory = 1`
and then make separate writes. The reservation must atomically check and consume inventory,
using a suitable conditional update, lock, or transaction.

ACID describes transaction properties:

- **Atomicity:** all transaction changes take effect, or none do.
- **Consistency:** transactions preserve declared integrity constraints; application logic
  must still encode the intended business rules.
- **Isolation:** concurrent transactions interact according to the selected isolation level.
- **Durability:** committed changes survive the failures covered by the storage contract.

ACID's C is not CAP's C. Local ACID transactions can coexist with asynchronously replicated,
stale regional reads.

### Advanced detail: transaction isolation

**Read uncommitted** may allow dirty reads; **read committed**
prevents them but permits other anomalies. **Repeatable read** stabilizes repeated reads,
with implementation-specific guarantees. **Snapshot isolation** gives a consistent snapshot
but can allow write skew: concurrent transactions change different rows and collectively
violate a rule. **Serializable** transactions behave like some serial execution;
**strict serializability** additionally respects real-time ordering.
[Jepsen's consistency guide](https://jepsen.io/consistency) distinguishes these guarantees.

**BASE** means Basically Available, Soft state, Eventually consistent. It is a design
philosophy, not a theorem or a requirement to abandon transactions.

### Back to checkout: transactions across services

| Approach | What it provides | What the PM must allow for |
| --- | --- | --- |
| **Two-phase commit (2PC)** | Participants prepare, then follow one commit/abort decision across transactional resources. | Coordination latency; classic 2PC can leave prepared participants blocked while the coordinator/decision is unavailable. It does not independently choose transaction isolation. |
| **Saga** | A sequence of local transactions, with compensating actions when later steps fail. | Intermediate states are visible; compensation can fail or need manual intervention. A refund is not an invisible rollback. |

For example, reserve inventory, attempt payment, then release the reservation after a
**definitive decline**. A timeout may hide a successful charge: keep an explicit pending
state and reconcile before releasing, or follow a defined cancellation/refund policy.
Specify hold expiry and late payment outcomes so a charged buyer is not silently left
without a seat. Define what happens if releasing the hold also fails. A
[saga](https://learn.microsoft.com/en-us/azure/architecture/patterns/saga) needs ownership,
retries, and reconciliation, not just a diagram.

## Replication, consensus, and quorums

**Replication copies the same data** for resilience, locality, or read capacity.
**Sharding splits different data** across nodes for capacity and throughput. Systems often
replicate each shard.

For our store, shards can hold different concerts and replicas can copy each concert's
records. This spreads independent sales, not contention for one final seat.

With **synchronous replication**, acknowledgment waits for specified replicas or a quorum.
With **asynchronous replication**, it can precede propagation to other replicas, lowering
write-path coordination but allowing stale reads and possible acknowledged-write loss if
failover promotes a lagging copy.

Ask what acknowledgment means: received in memory, persisted, or committed under a
protocol? Replication is not a backup: deletion and corruption propagate too.

### Agreement is a protocol, not a replica count

**Consensus** lets servers agree on decisions such as which reservations committed.
A **quorum** is a set of participants sufficient for a particular protocol step.

Paxos and [Raft](https://raft.github.io/) support agreement on decisions such as a replicated
log. In a conventional majority-based group, **five voting members require three**.
Two may be unavailable while the remaining communicating majority makes progress, subject
to the protocol's timing and recovery assumptions. Standard Raft/Paxos are not Byzantine
fault-tolerance protocols: they do not cover arbitrary malicious behavior.

Voters, non-voting read replicas, and witnesses are not interchangeable. Placing three of
five voters in one region makes that region's loss fatal to majority availability.
Spreading voters changes both failure tolerance and coordination latency.

### Advanced detail: quorum overlap

In quorum-based storage, let **N** be the replica count, **R** the read set size, and
**W** the write acknowledgment set size. With fixed replica membership, **R + W > N**
ensures read/write overlap; **W > N/2** ensures write/write overlap. For N = 3,
R = 2 and W = 2 satisfy both. These inequalities alone do **not** establish linearizability:
version ordering, concurrent writes, recovery, and the actual quorum protocol still matter.

<figure class="system-design-diagram">
<a href="{{ '/assets/images/cap-theorem/replication-sharding.svg' | relative_url }}">
<img src="{{ '/assets/images/cap-theorem/replication-sharding.svg' | relative_url }}"
alt="Replicas hold the same keys; shards hold different subsets and can each have replicas. A separate five-voter example needs three communicating voters plus protocol rules for progress."
loading="lazy" width="900" height="820">
</a>
<figcaption>Figure 3. Data placement, redundant copies, and agreement solve different
problems. Replica count alone does not establish consistency or durability.</figcaption>
</figure>

### Back to checkout: who may write after failover?

Prevent **split brain**, where two writers believe they are authoritative.
Storage-enforced **fencing** tokens or epochs reject a former owner's writes after
ownership changes. Simply rerouting shoppers to London cannot enforce that rule.

## Sharding: Scale data without hiding the boundaries

[Sharding](https://learn.microsoft.com/en-us/azure/architecture/patterns/sharding)
can relieve storage and write-throughput limits, but the shard key becomes a product
constraint: it determines locality, hot spots, migration work, and transaction boundaries.

### Advanced detail: shard placement strategies

| Strategy | Strength | Trade-off |
| --- | --- | --- |
| **Range** | Efficient scans over adjacent keys | Sequential writes or popular ranges can create hot shards. |
| **Hash** | Often spreads keys more evenly | Range queries fan out; simple modulo placement can move many keys when shard count changes. |
| **Consistent hashing** | Limits redistribution when membership changes | Movement and balance depend on implementation; a single hot key remains hot. |
| **Directory-based** | Explicit tenant placement and migration | The routing directory becomes a critical dependency. |
| **Geographic** | Locality and approved regional placement | Uneven demand, cross-region access, and relocation become harder. |

### Back to checkout: a popular concert is still a hot key

A large tenant or viral item can overload one shard while others sit idle. Options include
key redesign, splitting, dedicated capacity, caching, read replicas, or partitioned counters
where merging is valid. Resharding needs safe routing changes and online migration plans.

Cross-shard joins and transactions can add fan-out or coordination. Co-locate related data
where practical, without creating an oversized tenant shard. Before sharding, test simpler
options: indexes, query/data-model improvements, vertical scaling, and read replicas.
Those can postpone sharding, but replicas do not remove a primary write bottleneck.

## Global availability and load balancing

Multiple regions address distance and regional failures, but deployment count is not an
availability guarantee.

| Topology | Benefit | Critical question |
| --- | --- | --- |
| **Active-passive** | One serving region with a recovery destination; simpler write ownership | How warm is the standby, how far behind is its data, and how long does promotion take? |
| **Active-active applications** | Multiple regions serve traffic | Do all writes still depend on one authoritative region? |
| **Multi-region data writes** | Potentially local write acceptance | Are writes globally coordinated, assigned to per-entity owners, or independently accepted and merged? |

A data service can accept writes through multiple regional endpoints yet coordinate them
globally. Independent multi-writer replication is a different contract. Neither automatically
provides conflict-free updates or zero downtime.

Routing has three levels: **global traffic management** selects a region, **regional load
balancing** selects an instance, and **application routing** selects a service or data owner.
Layer 4 routing uses transport information such as IP/port; Layer 7 understands HTTP hosts,
paths, and headers.

Round robin rotates requests; weights favor higher-capacity instances; least-connections
or response-time routing uses observed load. Hash affinity keeps related traffic together
but can create hot spots. Proximity helps only if the region has healthy dependencies
and spare capacity.

Failover depends on health detection, routing propagation, DNS caches, existing connections,
client retries, and spare regional capacity. Sticky sessions are not durable storage.
Load balancers neither fix an overloaded shared database nor decide which replica is safe
to promote.

Residency applies to **replicas, caches, backups, logs, and recovery destinations**, not
just the primary database. Review tenant isolation, authentication, encryption, secrets,
and auditability across regions. A global identity or control-plane dependency can defeat
otherwise independent deployments.

## Caching: Fast does not mean current

A **cache** keeps a previously fetched answer to avoid repeating the original work.
For checkout, that can make the listing faster without making its stock count authoritative.
Browser caches, CDNs, application-local caches, distributed caches, and database page caches
reuse data at different layers; a CDN places cacheable content near readers.

With [cache-aside](https://learn.microsoft.com/en-us/azure/architecture/patterns/cache-aside),
read the cache first; on a miss, read the database and populate the cache. On updates,
write the authoritative database and invalidate the entry. Even this can race: an earlier
reader can insert an old value *after* invalidation.

<figure class="system-design-diagram">
<a href="{{ '/assets/images/cap-theorem/cache-race.svg' | relative_url }}">
<img src="{{ '/assets/images/cap-theorem/cache-race.svg' | relative_url }}"
alt="A reader fetches inventory one; a writer commits zero and invalidates the cache; the delayed reader then repopulates the cache with one. Checkout still needs an authoritative reservation."
loading="lazy" width="900" height="780">
</a>
<figcaption>Figure 4. Correct database state does not guarantee a current cache.
Freshness controls and authoritative reservation checks address different risks.</figcaption>
</figure>

### Advanced detail: cache writes and expiry

- **Write-through:** the write path updates the backing store and cache; added latency and
  partial failures still need handling.
- **Write-behind:** persist after accepting the cached write; durability depends on what
  happens if the cache or pending-write log fails.
- **Write-around:** bypass the cache for writes; handle existing stale entries and expect
  later misses.

Use time-to-live (TTL), versioned keys, explicit/event-driven invalidation, or refresh.
TTL limits an entry's residence time, not necessarily source-data staleness: a lagging
replica can supply old data again. Invalidation events can also be delayed or lost.

Combine duplicate fetches (**request coalescing** or **single-flight**), stagger expiry
times (**TTL jitter**), or preload likely reads (**warming**) to avoid a **cache stampede**:
many misses hitting the database together. **Stale-while-revalidate** serves an old answer
while refreshing it; use it only with explicit freshness limits.

### Back to checkout: recheck before confirming

Stale imagery may be acceptable; price and inventory require authoritative validation.
Scope private cache keys to the user, tenant, and permissions. Measure stale responses
and customer latency, not just cache hits.

## Messaging, retries, and asynchronous work

Queues and event streams separate a critical transaction from slower notifications,
analytics, or fulfillment work. They absorb bursts, not a permanent capacity deficit.
They also introduce backlog, duplicates, ordering constraints, and delayed completion.

**At-most-once** delivery may lose messages. **At-least-once** delivery may duplicate them.
**Exactly-once** semantics apply only within a defined processing/transaction boundary;
they do not automatically cover an external payment API.

Suppose a charge succeeds but its response disappears. The merchant cannot infer failure.
Record a logical payment attempt ID durably **before** contacting the provider. The
provider's [idempotency contract](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)
must ensure that retries with the same key and payload do not create another charge
within its documented window. Define key scope, retention, and payload-mismatch handling.
The provider must atomically protect its own effect and deduplication state; the
merchant cannot atomically commit an external charge with its local database update.
Query the original attempt or retry within the provider's contract. After the window
expires, reconcile rather than guess by submitting a new charge.

A **transactional outbox** records a database update and an event-to-publish in the same
local transaction; a relay publishes it later. The relay can retry, so consumers still
need deduplication. This avoids the gap between "order committed" and "event published"
without pretending that the database and queue share a magical transaction.

Choose ordering scope, often per order or conversation rather than globally. Provide
dead-letter handling and safe replay. Customer states such as **pending**, **confirmed**,
and **failed** should match actual durability and processing milestones. In a messaging
app, local composition, server acceptance, recipient delivery, and reading are separate
events. Infrastructure guarantees must become end-to-end product guarantees.

## Capacity, reliability, and recovery

**Vertical scaling** adds resources to one machine; **horizontal scaling** adds machines.
Stateless application instances are relatively easy to add. Stateful services need data
placement, recovery, and coordination; autoscaling also takes time to provision and warm.

Measure completed **throughput** alongside latency, saturation, and queue age. P50 is the
median; P95 and P99 reveal slower experiences that an average can hide. A high fan-out
request may wait on its slowest dependency.

**Little's Law:** average in-flight work = average throughput x average time in system.
At a stable 1,000 requests/second and 0.2 seconds average duration, that is 200 in-flight
requests, not a recommendation for 200 servers. Use consistent boundaries and long-run
averages; a continuously growing backlog is not stable operation.

Limit incoming work (**rate limits/admission control**) and queue size. Slow producers
when consumers fall behind (**backpressure**) or reject excess work (**load shedding**).
Space bounded retries farther apart with random variation (**backoff with jitter**).
Temporarily stop calls to failing dependencies (**circuit breakers**) and isolate resource
pools (**bulkheads**), so delayed receipts do not exhaust checkout capacity.

In multi-tenant products, quotas, fair scheduling, resource pools, reservations, and
tenant-aware placement reduce noisy-neighbor effects at a utilization/cost trade-off.
For analytics, checkpoints, task retries, data locality, shuffle, and recomputation also
matter. CAP alone does not explain a distributed query engine's performance.

### Make reliability measurable

An **SLI** measures behavior; an **SLO** sets its target and window; an **SLA** is an agreement
with defined consequences. [Google's SRE guidance](https://sre.google/sre-book/service-level-objectives/)
separates these terms. Define success for the customer journey, not just HTTP responses.

For a time-based target, **downtime allowance = period x (1 - availability)**:

| Availability | Allowance over a 365-day year |
| --- | --- |
| 99% | 3.65 days |
| 99.9% | 8.76 hours |
| 99.95% | 4.38 hours |
| 99.99% | 52.56 minutes |
| 99.999% | Approximately 5.26 minutes |

These are arithmetic examples, not provider SLA terms. For a request-based 99.9% SLO, the
error budget is 0.1% of eligible requests in the defined window, not automatically a number
of downtime minutes.

**RPO**, recovery point objective, bounds acceptable data loss, commonly expressed as a
time window. **RTO**, recovery time objective, targets restoration time. Neither is evidence
that recovery works. Test failover, failback, and restoration from isolated backups.
Multi-zone replication addresses different failure domains from multi-region recovery;
shared software, credentials, or control planes can still cause correlated failures.

## Put it together: A global checkout

Consider this simplified architecture. Both regions can serve application traffic, but
critical operations still need valid data authority and an idempotent payment path.

The normal journey is **reserve the seat → record a payment attempt → establish its
outcome → confirm the order and record notification work → deliver the receipt**.
An unknown payment stays pending; a definitive decline follows the hold-release policy.
Order confirmation must validate that the reservation is still valid. If payment succeeds
after a hold expires, reconcile or refund rather than promise a seat already sold.

<figure class="system-design-diagram">
<a href="{{ '/assets/images/cap-theorem/global-checkout.svg' | relative_url }}">
<img src="{{ '/assets/images/cap-theorem/global-checkout.svg' | relative_url }}"
alt="Global routing reaches regional load balancers, applications, and catalog caches. Both regions depend on replicated inventory/order authority and an idempotent payment API. A committed outbox feeds a queue and workers asynchronously."
loading="lazy" width="900" height="1080">
</a>
<figcaption>Figure 5. Solid arrows show request dependencies; dashed arrows show background
work. Serving traffic in two regions does not imply independent, safe writes.</figcaption>
</figure>

Return to the failure contract: the listing can remain useful, but reservation and payment
must meet their own guarantees. Measure them separately:

- **Processing reliability:** as a hypothetical target, 99.99% of eligible checkout
  attempts reach a correct terminal outcome within 60 seconds over 30 days. Count each
  authorized, well-formed attempt within published quota once by ID, including timeouts.
  Count overload-induced failures; do not exclude attempts because the system failed.
  A legitimate sold-out or payment-declined outcome qualifies; an infrastructure error
  or unresolved payment does not.
- **Uncertainty:** track attempts still pending after 60 seconds, with an owner to resolve
  them. Returning "pending" is not the same as completing checkout.
- **Conversion:** completed purchases divided by checkout attempts measures a different
  business outcome. No confirmed oversells or duplicate logical charges are correctness
  rules, not routine allowances inside the reliability budget.

Browsing might separately target P95 below 200 ms. Recovery might target RTO below
15 minutes and RPO below one minute **for non-ledger data**. Do not quietly apply that
loss tolerance to financial records.

Routing succeeds only if the destination has capacity, required dependencies, and the right
data authority. During recovery, fence old writers, catch up replicas, resolve conflicts,
replay work, and verify invariants before declaring success.

<figure class="system-design-diagram">
<a href="{{ '/assets/images/cap-theorem/recovery.svg' | relative_url }}">
<img src="{{ '/assets/images/cap-theorem/recovery.svg' | relative_url }}"
alt="Recovery checkpoints: detect and contain, establish safe authority and fence old writers, reconcile and replay, then verify invariants and capacity before restoring operations."
loading="lazy" width="900" height="790">
</a>
<figcaption>Figure 6. These are conceptual checkpoints, not a universal failover algorithm.
Some work can run in parallel; the protocol and tested runbook determine the sequence.</figcaption>
</figure>

The same reasoning transfers: calendar room booking needs exclusive ownership; a messaging
app's presence indicator may tolerate staleness. A financial ledger, social reaction count,
and analytical dashboard need different contracts, even inside one product.

Technology names come **after** these choices. Candidates include PostgreSQL or Azure SQL
for relational storage; Azure Cosmos DB or Amazon DynamoDB for managed NoSQL; Redis for
caching; Kafka or Azure Service Bus for asynchronous work; and NGINX or managed cloud
services for routing. These are starting points, not interchangeable guarantees or fixed
CP/AP classifications. Validate the selected service's exact mode and scope.

## Beyond CAP: FLP, CALM, and highly available transactions

**Advanced detail.** These related results sharpen the discussion; they are not loopholes
in CAP. Read them after the checkout example rather than treating them as prerequisites.

| Concept | Contribution | Product implication |
| --- | --- | --- |
| **Safety and liveness** | Safety means nothing forbidden happens; liveness means useful progress eventually happens. | "Never double-book" and "eventually complete a booking" are different obligations. |
| **FLP impossibility** | Deterministic consensus cannot guarantee termination in a fully asynchronous system with even one possible crash. | Practical protocols need additional timing/progress assumptions or randomization; short timeouts trade faster detection for false alarms. |
| **CALM** | Under its model, monotonic computations can have consistent, coordination-free implementations: new facts do not retract earlier conclusions. | Seek mergeable work that can proceed independently. Its consistency concerns convergent outcomes, not CAP linearizability. |
| **Highly Available Transactions (HATs)** | Some transactional guarantees can coexist with partition availability; stronger guarantees such as general serializability cannot. | Do not equate all transactions with unavailable operation, or assume every isolation/session guarantee survives arbitrary routing. |

Sources: [Fischer, Lynch, and Paterson](https://groups.csail.mit.edu/tds/papers/Lynch/jacm85.pdf),
[Hellerstein and Alvaro on CALM](https://ar5iv.labs.arxiv.org/html/1901.01930), and
[Bailis and colleagues on HATs](https://www.bailis.org/papers/hat-vldb2014.pdf).
CRDTs implement particular mergeable structures; they are not a blanket guarantee that an
application's invariants are coordination-free.

## A PM's architecture decision checklist

Use one record per critical operation:

1. **Customer outcome:** What improves, for whom? State latency, success, and freshness
   targets with a measurement window.
2. **Invariant:** What must never happen? Name the atomic operation and durability boundary
   that enforce it, not simply "use strong consistency."
3. **Failure contract:** What happens during partition, overload, lost response, cache
   failure, and regional loss? Specify what the customer sees.
4. **Recovery contract:** Who owns failover, fencing, reconciliation, replay, RPO/RTO, and
   customer remediation? Which tests demonstrate those promises?
5. **Scale and placement:** What bottleneck justifies replicas, shards, or more regions?
   Check hot tenants, cross-shard work, shared dependencies, and residency.
6. **Economics and evidence:** Compare compute, storage, cross-region transfer, operational
   effort, and the cost of incorrect behavior. Can a simpler design meet the requirements?

**Example — lost payment response:** show "Checking payment" against the original attempt
ID, not a second payment button. In this example, Payments Operations owns reconciliation
and gets an alert after 60 seconds of uncertainty. Drop the response after a successful
charge in a test: recovery should produce one charge, one recorded outcome, and no need
for the buyer to pay again.

Validate with representative load, safe fault injection, regional recovery exercises, and
controlled rollouts. Track customer success and P95/P99 latency alongside replication lag,
stale reads, conflicts, duplicate effects, recovery time, and cost per successful operation.
A faster benchmark is not a win if correctness or incident burden deteriorates.

For an interview, summarize the logic in one sentence: **CAP defines the partition-time
limit; PACELC adds normal-operation latency; the product's invariants determine where we
coordinate, where we tolerate staleness, and how we recover.**

Start with one critical journey and write its failure contract before choosing another
component. That is how a PM turns distributed-systems theory into a product promise the
team can defend.

## References and further reading

Start with the first three for foundations, then explore the practical patterns.
The final paper is optional mathematical depth; the FLP, CALM, and HAT papers linked
above are also advanced reading, not prerequisites.

1. **[Eric Brewer: CAP Twelve Years Later (2012)](https://www.infoq.com/articles/cap-twelve-years-later-how-the-rules-have-changed/).**
   Clarifies why "pick two" is misleading and why partition handling and recovery
   deserve explicit design decisions.
2. **[Daniel Abadi: PACELC (2012)](https://www.cs.umd.edu/~abadi/papers/abadi-pacelc.pdf).**
   Extends the discussion to consistency-versus-latency trade-offs during normal
   operation, not just network partitions.
3. **[Jepsen: Consistency Models](https://jepsen.io/consistency).**
   A reference for distinguishing linearizability, serializability, and other
   guarantees. Use it to translate "strong consistency" into a precise requirement.
4. **[Microsoft Azure Architecture Center: Saga Design Pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/saga).**
   Explains multi-service workflows, compensation, and the trade-offs between
   choreography and orchestration.
5. **[AWS Builders' Library: Making Retries Safe with Idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/).**
   Explains request identifiers, retry semantics, and late-arriving requests.
   Useful when designing recovery from an uncertain payment response.
6. **[Google SRE Book: Service Level Objectives](https://sre.google/sre-book/service-level-objectives/).**
   Shows how to choose meaningful service indicators and targets rather than
   treating infrastructure uptime as the whole customer experience.
7. **[Seth Gilbert and Nancy Lynch: The CAP Proof (2002)](https://cs.nyu.edu/~apanda/classes/sp25/papers/gilbert02brewers.pdf).**
   The formal foundation for CAP's definitions and impossibility result.
   Read it when you want the assumptions behind the simplified explanation.

> *Note: This blog post was written with assistance from AI*
