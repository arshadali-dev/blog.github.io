---
layout: post
title: "System Design for Product Managers: A Framework You Can Defend"
seo_title: "System Design for Product Managers | Arshad Ali"
date: 2026-11-14
description: "A reusable system design framework for product managers: learn the foundations, explore deeper trade-offs, and follow visual Calendar and messaging examples."
excerpt: "A reusable system design framework for product managers: learn the foundations, explore deeper trade-offs, and follow visual Calendar and messaging examples."
author: Arshad Ali
categories:
  - Product Management
tags:
  - product-management
  - software-architecture
feature-img: assets/images/system-design-for-product-managers.png
feature-title: ""
---

# System Design for Product Managers: A Framework You Can Defend

**System design connects a user experience to the components, data, and operating rules
needed to deliver it.** Product managers need not choose every engineering detail, but
should explain **what must work, what must stay correct, what can fail, and what it costs.**

We will follow two examples throughout:

- **Calendar:** Maya schedules a weekly meeting with Leo, changes it, and expects their
  calendars and reminders to agree.
- **Messaging:** Maya sends Leo a message while his phone is offline, then wants to know
  whether it was accepted, delivered, or read.

**The framework also applies to commerce, payments, collaboration, analytics, and other
systems**, with different workloads and correctness rules. Follow the foundations and
diagrams if new; use **Decision depth** sections to challenge familiar assumptions.

<div class="note-callout" markdown="1">
<div class="note-title">Examples, not implementation claims</div>

The designs resemble Google Calendar and WhatsApp workflows; they do not describe those
products' private infrastructure. All scale numbers, targets, and retention policies are
illustrative. Named technologies are candidates, not interchangeable guarantees.
</div>

## The reusable eight-phase framework

**Phases guide decisions; layers implement them.** A database is a layer, but deciding
what it must preserve spans several phases.

<figure class="system-design-diagram">
<a href="{{ '/assets/images/system-design/framework.svg' | relative_url }}">
<img src="{{ '/assets/images/system-design/framework.svg' | relative_url }}"
alt="Eight reusable design phases: scope, quality, scale, contracts and data, architecture, bottlenecks, failure and trust, and evolution."
width="900" height="820">
</a>
<figcaption>Figure 1. Each phase produces a decision that product and engineering can
review. Security and cost influence every phase, not only the final review.</figcaption>
</figure>

Jump to: [1. Scope](#phase-1-clarify-the-product) ·
[2. Quality](#phase-2-define-quality-and-correctness) ·
[3. Scale](#phase-3-estimate-scale) ·
[4. APIs and data](#phase-4-design-contracts-and-data) ·
[5. Architecture](#phase-5-assemble-the-architecture) ·
[6. Bottlenecks](#phase-6-find-and-relieve-bottlenecks) ·
[7. Failure and trust](#phase-7-design-for-failure-and-trust) ·
[8. Evolution](#phase-8-defend-and-evolve).

This is an iterative framework, not a waterfall. A privacy requirement can change the data
model; a recovery requirement can change latency and cost.

## First, understand the smallest working system

A **client** (browser/mobile app) sends a **request** to a **backend**, which checks
permissions, applies rules, accesses a **database**, and responds. The database holds
shared, durable state: data intended to survive a process restart.

<figure class="system-design-diagram">
<a href="{{ '/assets/images/system-design/system-basics.svg' | relative_url }}">
<img src="{{ '/assets/images/system-design/system-basics.svg' | relative_url }}"
alt="For both examples, a client requests a change, the backend validates it, and a database commits it before the backend confirms success. Recipient delivery is separate."
loading="lazy" width="900" height="550">
</a>
<figcaption>Figure 2. Start with one action and its confirmation. Add components only when
a requirement explains why they are needed. Select any diagram to open it at full size.</figcaption>
</figure>

**Authoritative state** settles what is true. Maya's local Calendar edit is not yet a
confirmed shared event; her pending message does not prove server acceptance.

The response waits for **synchronous work**, not for **asynchronous work** such as invitations
or delivery attempts. Background work can race with the response; independence, not wall-clock
order, is the distinction.

## Phase 1: Clarify the product

Define users, three to five workflows, exclusions, and limits. Personal agendas, medical
appointments, and exclusive room booking require different rules despite all using calendars.

Record the **budget, deadline, existing infrastructure, team operating capacity, and
data-location obligations**. A Calendar team reusing enterprise identity and a messaging
team without round-the-clock operations may choose differently despite similar traffic.

| Scope | Calendar example | Messaging example |
|---|---|---|
| Core workflows | Create/edit/cancel; invite and RSVP; recurring events; reminders; device sync | One-to-one and small-group text; offline delivery; linked-device sync; read receipts |
| Required protections | Calendar roles, including free/busy-only access | End-to-end encryption (E2EE) and device revocation |
| Optional behavior | Availability suggestions | Presence and typing indicators |
| Exclusions | Video calls, payments, automatic room allocation | Voice/video calls, public channels, payments |
| Limits to decide | Date-range size, attendee count, recurrence expansion | Group size, message size, linked devices, pending-message retention |
{: .system-design-table }

**Decision depth: distinguish a suggestion from a reservation.** A personal calendar may
allow overlapping meetings. A cached "free" result is a suggestion, not a guaranteed room
booking. Likewise, "online" is a hint, not proof a person can receive a message. Define the
promise before choosing the mechanism.

**Output:** agreed workflows, exclusions, limits, and owners for unresolved decisions.

## Phase 2: Define quality and correctness

**Latency** is how long an operation takes; **throughput** is work completed per unit of
time. **Availability** measures successful service; **durability** concerns preserving
committed data. A system can respond quickly and still lose the user's work.

A **service-level indicator (SLI)** is a measurement; an **SLO** is its target; an **SLA**
is a contractual commitment. **p95 below 300 ms** means at least 95% of measured operations
finish within 300 ms; p99 describes the 99th percentile.

| Requirement | Calendar example | Messaging example |
|---|---|---|
| Availability | 99.95% monthly success for eligible core API requests | 99.95% monthly acceptance success for eligible submissions |
| Latency | p95 range fetch below 300 ms; p99 save below 500 ms, at the regional API boundary | p99 acceptance below 500 ms at that boundary; p95 delivery below 300 ms for the connected cohort |
| Correctness | Do not silently overwrite a newer meeting edit | A retry must not create another visible message |
| Freshness | Own confirmed edits visible immediately; 99% of edits applied on other connected devices within 5 seconds | Conversation order converges; presence may lag |
| Durability | Confirmed saves survive the specified single-zone failure | Accepted, unexpired pending messages survive that same failure model |
{: .system-design-table }

These are illustrative targets. **Eligible** means authorized, well-formed, and within
published quotas: exclude expected validation rejections, but count capacity-induced
failures, including overload `429`s. Define the connected delivery cohort at submission:
authenticated foreground devices with active channels in the serving region. Keep later
disconnects and missing acknowledgments visible as failures, not retroactive exclusions.

An **invariant** is a rule that must remain true: only authorized people can read an event;
only authorized devices receive new message content. Unlike a latency target, violating
such a rule is not an acceptable routine error budget.

**Decision depth: measure the promise, not the convenient denominator.** Excluding
undelivered messages from delivery-latency charts can hide failure. Pair latency with
delivery success and oldest pending work. A 99.95% *time-based* target allows 21.6 minutes
in a 30-day month; that is not interchangeable with a *request-based* error budget. If
Calendar misses its freshness target over a 15-minute window, investigate and pause rollout.

**Output:** measurable targets, correctness rules, and explicit degraded behavior.

## Phase 3: Estimate scale

The figures below are a **growth stress test, not the MVP's claimed capacity**. Start from
measured launch demand; use the larger workload to expose future bottlenecks.

Estimate only what changes a decision. Average operations/second equals daily operations
divided by **86,400**; multiply by an assumed peak factor for an initial peak estimate.
**Fan-out** means one action creates work for several recipients: attendee updates for
Calendar, recipient-device deliveries for messaging.

| Assumption or estimate | Calendar example | Messaging example |
|---|---|---|
| Daily active users | 20 million | 100 million |
| Actions per user/day | 20 reads; 2 mutations | 40 submitted messages |
| Daily traffic | 400 million reads; 40 million mutations | 4 billion submissions |
| Average operations/second | About 4,630 reads; 463 mutations | About 46,296 submissions |
| Assumed peak | 4x: about 18,520 reads and 1,852 mutations/second | 3x: about 138,889 submissions/second |
| Additional delivery work | Multiply edits by affected attendees | 3 device attempts/message: about 416,667 attempts/second at peak, before retries |
| At 1 KB per change/message | 40 GB/day of changes, not net live-event growth | 4 TB/day logical ingress; 120 TB if all copies remain for 30 days |
{: .system-design-table }

Endpoint counts are not database-query counts: a Calendar range can span calendars; one
message can require multiple encrypted device envelopes.

Deleting delivered copies reduces the 120 TB retention bound; three replicas raise it to
360 TB before indexes, backups, device expansion, or overhead. At the assumed, unmeasured
1 KB size, peak ingress is roughly **139 MB/second** before overhead; fan-out adds outbound
bandwidth.

**Decision depth: count quiet users too.** Ten million live connections at a hypothetical,
load-tested 50,000 per gateway require at least 200 gateways before spare capacity.
Heartbeats every 30 seconds produce roughly 333,333 signals/second without a single new
message. Calendar sync polling can similarly dominate traffic between edits.

**Output:** a capacity worksheet with units, peak assumptions, and measurements to validate.

## Phase 4: Design contracts and data

### Choose how components communicate

An **API (application programming interface)** specifies operations, inputs, outputs, and
errors. **HTTP** provides request/response semantics; **HTTPS** protects HTTP using
Transport Layer Security (TLS). Neither proves a write was saved.

<figure class="system-design-diagram">
<a href="{{ '/assets/images/system-design/communication-patterns.svg' | relative_url }}">
<img src="{{ '/assets/images/system-design/communication-patterns.svg' | relative_url }}"
alt="REST requests resources, GraphQL selects fields, WebSockets exchange ongoing events, and webhooks notify another backend."
loading="lazy" width="900" height="900">
</a>
<figcaption>Figure 3. These patterns can coexist. An open connection is not a delivery
guarantee, and a flexible query is not automatically a fast query.</figcaption>
</figure>

| Pattern | Meaning | Calendar application | Messaging application |
|---|---|---|---|
| REST | Resource-oriented API using HTTP semantics | `GET` events, `POST` a new event, `PATCH` an edit | Manage conversations, groups, and devices |
| GraphQL | Request selected fields through a typed schema | Event title, attendee responses, and permissions in one query | Conversation membership and device metadata; optional, not needed for live delivery |
| WebSockets | Persistent, bidirectional client/server channel | Live edit notifications where useful | Messages, receipts, and typing updates |
| Webhooks | One backend calls another after an event | Notify an authorized calendar integration of a change | Optional delivery-status integration, with explicit consent and no plaintext leakage |
{: .system-design-table }

Long polling and server-sent events remain alternatives when their interaction model fits.
Implementation options appear in the technology reference.

**Authentication** establishes who the caller is; **authorization** determines what that
caller may do. **N+1 reads** means one list query followed by one query per item, in REST
or GraphQL implementations. Batch related reads and limit query complexity. Authenticate
webhook senders, deduplicate retries, and retrieve current state when notifications are hints.

### Model relationships and access patterns

An **entity** has an identity. A **primary key** uniquely identifies a record; a **foreign
key** references another key and can enforce valid relationships in a relational database.
Calendar has calendars, events, attendees, and permissions. Messaging has conversations,
memberships, devices, messages, and delivery receipts.

<figure class="system-design-diagram">
<a href="{{ '/assets/images/system-design/storage-models.svg' | relative_url }}">
<img src="{{ '/assets/images/system-design/storage-models.svg' | relative_url }}"
alt="Calendar entities relate through primary and foreign keys; messaging records can be retrieved by conversation, bucket, and sequence."
loading="lazy" width="900" height="900">
</a>
<figcaption>Figure 4. Start with what must be retrieved and changed together, not a
SQL-versus-NoSQL popularity contest.</figcaption>
</figure>

**SQL (Structured Query Language) databases**, such as **Azure SQL Database and PostgreSQL**,
fit related records, joins, constraints, and transactions. **NoSQL** includes document,
key-value, and wide-column models; **Azure Cosmos DB and Amazon DynamoDB** are examples.
SQL can scale; NoSQL can transact. Verify schemas, keys, consistency, and operating limits.

- **Calendar:** an event references its calendar; `(event_id, attendee_id)` uniquely
  identifies an invitation. The organizer controls shared time, title, and cancellation,
  and may grant editing rights. Each attendee controls their RSVP, visibility preferences,
  and personal reminders. Store these authoritative records separately from derived agenda
  views. Leo's stale view cannot override Maya's cancellation; a late RSVP cannot revive it.
- **Messaging:** retrieve pending messages by conversation and sequence; find a retry's
  saved result by sender device and stable client message ID. Keep delivery receipts
  separate from disposable "which gateway is this device using?" hints.

PostgreSQL can launch either example; justify partitioned NoSQL through measured needs.

### Define what a successful write means

A **transaction** groups database operations. **Atomicity** means all changes commit
together or none do; **idempotency** means repeating the same logical operation does not
repeat its effect. Neither implies the other.

- **Calendar:** atomically commit the event, required related records, and operation result.
  Use stable idempotency keys for both creation and edits. For a new edit, send the version
  read using `If-Match`; reject a stale version with `412 Precondition Failed`.
- **Messaging:** persist the encrypted message (ciphertext), its sequence, and retry result
  before returning **accepted**. The sender reuses the same client message ID; recipients also
  deduplicate. A socket receiving bytes is not durable acceptance.

Scope idempotency keys to the caller and operation, bind them to a request fingerprint,
and define retention. A fingerprint detects reuse of the key with different content.
After the supported retry window, require reconciliation or rejection.

**Lost-response example:** Maya edits version 7 with key K; version 8 commits, but the
response disappears. On retry, recheck authorization, then return K's stored result if its
fingerprint matches, before evaluating the now-stale `If-Match: 7`. A different operation
using version 7 still conflicts. Check and commit retry identity atomically with the edit.

For our one-to-one messaging contract, **pending** is unconfirmed local work; **accepted**
is durable server commitment; **delivered** means at least one authorized recipient device
acknowledged storing the message locally; **read** is a client-reported state subject to
privacy settings. **Failed** means a definitive rejection, not a transient timeout.
**Expired/unconfirmed** means no recipient acknowledgment arrived before the retention
deadline; delivery attempts stop, but this does not prove a device never received it.
Groups need per-member receipt aggregation rather than reusing the one-to-one badge.

### Preserve domain meaning, not just bytes

**Calendar:** 9 a.m. every Monday in Los Angeles is not "add seven days in UTC." Store local
time, an IANA time-zone identifier such as `America/Los_Angeles`, the recurrence rule, and
occurrence exceptions. Define daylight-saving ambiguity, use dates for all-day events,
and expand only a bounded time window. "This occurrence," "the series," and "this and
following" are different edits; the last may split a series. Specify how that split maps
exceptions, preserves or resets attendee responses, and cancels/reschedules reminders.

**Messaging:** choose ordering within a conversation, not across the whole product.
A server-assigned sequence records acceptance order, not the order people typed on
unsynchronized clocks. Device history and server retention differ. Our example retains
each authorized device's pending envelope until its acknowledgment, revocation, or a
30-day expiry. Leo's laptop acknowledgment changes Maya's badge to delivered and makes
that copy deletable; his offline phone's copy remains pending. Its later expiry does not
undo the delivered badge. New-device history transfer is a separate authorized feature.
Later device revocation or local corruption does not erase historical acknowledgment:
delivery is not a permanent-storage or backup guarantee.

**Decision depth: transaction scope is an architectural constraint.** DynamoDB can
atomically update distinct items across tables within one account and Region, with
documented size/count limits. Cosmos DB transactional batches require the same logical
partition **within one container**. Foreign keys likewise do not automatically enforce
relationships across independently owned services or shards.

**Output:** API guarantees, entities, access patterns, and transaction boundaries.

## Phase 5: Assemble the architecture

### Add routing and policy around the basic request

An **IP address** identifies a network endpoint; a port identifies a service endpoint
there. **DNS** resolves a service name into records used to reach it. DNS is a lookup,
not a proxy through which every request passes; cached answers also delay routing changes.

A **forward proxy** acts for clients, such as a corporate outbound proxy. A **reverse
proxy** fronts servers. A **load balancer** distributes traffic among healthy instances;
an **API gateway** applies shared authentication, quotas, and routing policy. These
responsibilities can share infrastructure.

<figure class="system-design-diagram">
<a href="{{ '/assets/images/system-design/request-path.svg' | relative_url }}">
<img src="{{ '/assets/images/system-design/request-path.svg' | relative_url }}"
alt="DNS lookup is separate from HTTPS traffic through edge routing, gateway policy, backend instances, and authoritative storage."
loading="lazy" width="900" height="960">
</a>
<figcaption>Figure 5. Both applications use this request path. The messaging application
also keeps long-lived connections; resource authorization still belongs in the backend.</figcaption>
</figure>

Logging in does not authorize every calendar read or conversation send.
TLS may terminate at the edge and be re-established internally; define the trust boundary.
The edge's web application firewall (WAF) filters common malicious web traffic, not every
application-level abuse case.

A **service** is a logical capability; an **instance** is one running copy. A **modular
monolith** deploys capabilities together; **microservices** deploy them independently,
adding network calls and distributed failure handling.

- **Calendar:** begin with event, permissions, and reminder modules in one application.
- **Messaging:** gateways may merit separate deployment because connections restart and
  scale differently from message processing. A gateway holds live connection state, so it
  is not stateless; it can still be replaceable if durable messages live elsewhere.

### Make background work recoverable

A **queue** retains work for workers to process. A **stream** retains events for replay
and independent consumers. Use **Azure Service Bus, Amazon SQS, or RabbitMQ** for jobs;
**Kafka, Azure Event Hubs, or Kinesis** for retained event streams when needed.

The **transactional outbox** is a durable "work to publish" record committed in the same
transaction as the business change. Without it, a crash between saving data and publishing
work can leave a Calendar event without invitation work, or an accepted message without
delivery work.

<figure class="system-design-diagram">
<a href="{{ '/assets/images/system-design/durable-work.svg' | relative_url }}">
<img src="{{ '/assets/images/system-design/durable-work.svg' | relative_url }}"
alt="A lost response triggers a retry with the same key; the service returns the committed result rather than creating duplicate work."
loading="lazy" width="900" height="860">
</a>
<figcaption>Figure 6. Atomicity prevents partial updates; idempotency prevents duplicate
effects. An outbox makes publication recoverable, not exactly once.</figcaption>
</figure>

An outbox publisher can publish twice; workers must deduplicate. **Ordering is separate:**
Calendar version 8 may arrive before version 7. Apply newer complete snapshots or rebuild;
incremental changes require ordered processing or gap recovery. Messaging uses sequences,
not arrival order. External email/push may still duplicate without provider idempotency.

### Trace both complete designs

The diagrams show **logical responsibilities**, not fleets sized for Phase 3. Our launch
baseline is one region, replaceable application instances, and SQL configured for the
single-zone durability target. Regional recovery is a separate decision in Phase 7.

The conversation owner is a coordination role, not necessarily a separate service.
In our SQL baseline, an ownership record maps a conversation to an instance and **epoch**
(ownership generation). If A fails, a coordinated, atomic transfer gives B epoch 18 instead
of 17. Storage checks the current epoch atomically with every authoritative write,
rejecting A's stale writes. B recovers committed sequence state; clients retry with stable
IDs. This is **fencing**: it stops competing writers, but cannot recover unreplicated data
after regional loss.

<figure class="system-design-diagram">
<a href="{{ '/assets/images/system-design/calendar-architecture.svg' | relative_url }}">
<img src="{{ '/assets/images/system-design/calendar-architecture.svg' | relative_url }}"
alt="Calendar validates permissions and versions, commits the event and outbox, then processes invitations, reminders, and derived agendas asynchronously."
loading="lazy" width="900" height="980">
</a>
<figcaption>Figure 7. Maya's save succeeds after the SQL commit, not after every attendee
has been notified. Permission checks must remain valid at commit.</figcaption>
</figure>

**Calendar:** authorize, recover matching retries, and version-check new edits; commit the
event, attendees, change record, retry result, and outbox. Confirm after commit; publish
independently. Schedule reminders durably, not with process timers, and recheck cancellation.

<figure class="system-design-diagram">
<a href="{{ '/assets/images/system-design/messaging-architecture.svg' | relative_url }}">
<img src="{{ '/assets/images/system-design/messaging-architecture.svg' | relative_url }}"
alt="The sender encrypts, the conversation owner commits acceptance, and workers deliver through a recipient gateway; device acknowledgments update durable delivery progress."
loading="lazy" width="900" height="1280">
</a>
<figcaption>Figure 8. Acceptance and recipient acknowledgment cross different boundaries.
Only endpoint devices decrypt content. One recipient acknowledgment does not delete
other devices' pending work.</figcaption>
</figure>

**Messaging:** the sender encrypts; one SQL acceptance transaction validates ownership and
membership under concurrency control and commits the message, sequence, retry result, and
outbox delivery intent. Workers deliver through gateways or retain pending work offline.
Later recipient **acknowledgments (ACKs)** update durable delivery progress in separate
transactions. **Redis** maps devices to gateways; these disposable hints are outside the
acceptance transaction.

**Decision depth: ownership must survive races.** A stale membership-cache check cannot
authorize acceptance. Retain retry records across time-bucket rollover; yesterday's
accepted operation must not become a new one today. Service-specific limits appear below.

**Output:** a trace of a write, read, retry, and background completion, with owners and
commit boundaries identified.

## Phase 6: Find and relieve bottlenecks

Measure the limiting resource before adding components. Different bottlenecks need
different techniques.

<figure class="system-design-diagram">
<a href="{{ '/assets/images/system-design/scaling-patterns.svg' | relative_url }}">
<img src="{{ '/assets/images/system-design/scaling-patterns.svg' | relative_url }}"
alt="Vertical scaling adds capacity per node, horizontal scaling adds nodes, replicas copy data, shards divide records, and vertical partitioning separates fields."
loading="lazy" width="900" height="1000">
</a>
<figcaption>Figure 9. More instances, more copies, and different data partitions solve
different problems.</figcaption>
</figure>

| Technique | What it changes | Calendar example | Messaging example |
|---|---|---|---|
| Vertical scaling | More CPU, memory, or I/O on one node; finite ceiling | Larger database instance | More gateway connection memory |
| Horizontal scaling | More instances; work must be distributable | More API instances | More gateways and delivery workers |
| Indexing | Extra lookup structure; costs writes and storage | Calendar/time index for range reads | Conversation/sequence lookup for replay |
| Read replicas | Additional copies serving suitable reads; may lag | Older agenda reads where permitted | Noncritical metadata reads, not stale authorization |
| Sharding | Distribute record subsets across database nodes | Calendar/tenant ownership key | Conversation-oriented key; hot groups remain a risk |
| Vertical partitioning | Separate fields/payloads, not larger machines | Keep long descriptions off list reads | Separate receipt metadata from large ciphertext payloads |
| Denormalization | Duplicate/precompute a read model; copies can lag | Attendee agenda and free/busy summaries | Conversation lists and unread summaries; plaintext previews stay client-side under E2EE |
{: .system-design-table }

**Replication** maintains copies; it is not sharding. Local table partitioning need not
distribute work across machines. An index on event start time also needs correct
interval-overlap logic: a long event may begin before the requested range.

### Cache repeated reads; isolate large objects

A **cache** stores reusable results. In **cache-aside**, the application checks the cache,
loads the database on a miss, and fills the cache. A **time to live (TTL)** limits how long
an entry remains eligible.

**Race example:** A reads event version 5; B commits version 6 and invalidates the cache;
A then fills it with version 5. A version label alone does not prevent stale reads.
Coordinate invalidation with generation-checked fills: reject a fill if the cache generation
changed since its read began. Bypass the cache when authoritative freshness is required;
the database write and cache invalidation still are not one atomic operation.

<figure class="system-design-diagram">
<a href="{{ '/assets/images/system-design/cache-aside.svg' | relative_url }}">
<img src="{{ '/assets/images/system-design/cache-aside.svg' | relative_url }}"
alt="The application reads Redis, loads the authoritative database on a miss, and invalidates or versions cached entries after writes."
loading="lazy" width="900" height="760">
</a>
<figcaption>Figure 10. Caching trades repeated work for freshness and invalidation
obligations. Access revocation must not wait for an ordinary cache TTL.</figcaption>
</figure>

- **Calendar:** cache bounded free/busy results, but revalidate permissions and use
  authoritative checks for exclusive reservations.
- **Messaging:** cache routing and approximate presence, not the only copy of accepted
  messages. Heartbeats and expiry indicate likely connectivity, not certain availability.

**Redis, Azure Managed Redis, and Amazon ElastiCache** are options. A **cache stampede**
occurs when many misses trigger the same expensive fetch: combine concurrent fills,
stagger expirations, and bound database concurrency during a cache outage.

**Blob/object storage**, such as **Azure Blob Storage or Amazon S3**, holds large files.
**CDNs**, such as **Azure Front Door, CloudFront, or Cloudflare**, cache suitable assets
near users. Both apps can use a CDN for static UI files; private attachments need scoped
access and deliberate cache rules. Messaging clients encrypt attachments before upload,
then send the reference and key inside the encrypted message. Clean up abandoned uploads.

### Bound fan-out, hotspots, and backlog

Calendar edits may create attendee updates and reminder jobs; messaging creates work per
recipient device. Queues absorb bounded bursts, not unlimited sustained overload.
**Backpressure** slows or rejects new work when downstream capacity is exhausted.

Measure queue age and per-key traffic, not only backlog count or average CPU. Delay
Calendar invitations or drop typing updates before sacrificing core writes. If the durable
path is full, return a retryable failure, not false success.

**Decision depth: time buckets are not capacity guarantees.** A conversation/time-bucket
key groups a time range; it does not cap bytes, message count, or traffic. Retention needs
expiry/deletion policy. One popular Calendar tenant or chat can still dominate a partition.
Test hot keys, spikes, and mass reconnects; consider product limits before assuming more
workers will fix serialized work. Large broadcasts may need delivery computed on read
instead of per-recipient writes, changing latency and privacy.

**Output:** measured bottlenecks, targeted changes, and their new operating costs.

## Phase 7: Design for failure and trust

### Recover without inventing success

A **single point of failure** can stop a required workflow by itself. **Failover** moves
responsibility to a replacement. Multiple instances do not help if all depend on the same
unprotected database or exhausted connection pool.

<figure class="system-design-diagram">
<a href="{{ '/assets/images/system-design/reliability.svg' | relative_url }}">
<img src="{{ '/assets/images/system-design/reliability.svg' | relative_url }}"
alt="Replicated state supports controlled failover with fencing; optional reminders and presence can degrade without claiming an unsafe write succeeded."
loading="lazy" width="900" height="820">
</a>
<figcaption>Figure 11. Test the transition through failure, not only the healthy diagram.
Graceful degradation preserves a safe subset of the product.</figcaption>
</figure>

| Failure | Calendar behavior | Messaging behavior |
|---|---|---|
| Commit fails | Keep an explicit pending edit; do not confirm save | Retain the sender's pending message and stable retry ID |
| Commit succeeds; response is lost | Retry the same key; return the saved result | Return the original acceptance receipt |
| Publisher/queue is unavailable | Outbox retains invitation work within safe limits | Outbox retains delivery work; stop accepting if backlog limits are reached |
| Worker runs twice | Deduplicate; account for external notification limits | Deduplicate messages and update receipts idempotently |
| Gateway fails | Reconnect and fetch missed changes | Reauthenticate, reconnect, and replay missing deliveries |
| Cache fails | Bound fallback reads or shed optional work | Presence can be unknown; durable replay must still work |
{: .system-design-table }

Use timeouts and capped retries with exponential backoff and **jitter**, a random delay
that prevents synchronized retry storms. **Circuit breakers** temporarily stop calls to
unhealthy dependencies; **bulkheads** isolate resource pools. **Dead-letter queues** hold
failed work for investigation, alerts, and controlled replay.

For Calendar, isolate reminder failures from saves. For messaging, isolate typing and
presence from acceptance. Deployments should drain connections where possible rather than
force every client to reconnect simultaneously.

### Restore the right state after disconnection

A **cursor** records synchronization progress. Calendar clients fetch a snapshot, then
committed changes including deletions, and advance their cursor only after applying them.
Snapshot creation and change capture must share a gap-free boundary. Expired/invalid cursors
require full resync while preserving unsent local edits separately.

Messaging clients resume authorized delivery from durable progress. Do not advance a
contiguous cursor past an unexplained gap. But explicitly handle server-confirmed expiry,
deletion, or entries outside a device's authorized history; otherwise replay can wait
forever. An expired envelope cannot be recovered from a server that no longer retains it.
Database TTL cleanup may lag, so enforce logical expiration when serving data.

Mobile push through **APNs or Firebase Cloud Messaging (FCM)** is a wake-up/change hint,
not proof that either application retrieved or durably stored its updates.

### Choose consistency and regional recovery deliberately

**Replica freshness** concerns whether a copy has caught up; **transaction isolation**
concerns how concurrent transactions interact. Atomic writes do not guarantee fresh reads
from an asynchronous replica. Calendar may route own-edit reads to an authoritative copy;
messaging may serialize conversation writes while letting presence lag.

A **network partition** prevents groups of nodes from communicating. CAP says a
partitioned system cannot guarantee both a single-copy, real-time-consistent view
(linearizability) and availability of every operation at non-failing nodes. This technical
availability is not the same as a monthly uptime percentage.

- **Calendar:** isolated regions must not both confirm an exclusive room reservation.
- **Messaging:** an isolated region must not create a competing conversation sequence.
- **Both:** explicitly stale reads or local pending work may remain useful.

**PACELC** adds that, even without a partition, stronger coordination can trade latency
for consistency. Apply the trade-off per operation, not as a label for the whole product.

**RPO (recovery point objective)** is the tolerable time window of committed data loss;
**RTO (recovery time objective)** is the restoration-time target. Single-zone durability
does not imply regional durability. Asynchronous regional replication with a five-minute
RPO cannot promise zero loss of all regionally acknowledged writes. Stronger cross-region
commit guarantees add latency, coordination, and availability costs for both applications.
Replication also copies mistakes: maintain backups and test restores.

### Protect users at every boundary

Use authentication, resource-level authorization, tenant isolation, least privilege,
credential rotation, and logs without private payloads. Encryption **in transit** protects
network hops; encryption **at rest** protects stored media under its key-management model.
**End-to-end encryption (E2EE)** keeps content-decryption capability at the endpoints.

- **Calendar:** distinguish owner, editor, reader, and free/busy-only access. Revoke cached
  access safely; cap invitation sending so event creation cannot become a spam service.
- **Messaging:** use reviewed encryption protocols, device identities, key verification,
  forward secrecy (protecting past messages if current keys are compromised), and defined
  membership/key changes. Removing Leo from routing lists alone is insufficient: the group
  protocol must exclude him from future key material and coordinate sending with the new
  membership state. This cannot erase plaintext already received. Server-side plaintext
  search/scanning conflicts with ordinary E2EE; backups and reports need privacy designs.

**Rate limiting** bounds caller activity. A **token bucket** allows bounded bursts with
replenishing capacity; a **sliding window** measures recent requests. Calendar free/busy
queries should cost more quota than cheap metadata reads; messaging needs send, group,
payload, and device limits. Combine these with block/report flows and abuse signals.
IP-only limits penalize users sharing a network. HTTP APIs can return `429`; persistent
channels need an equivalent retry policy.

**Decision depth: security changes the product surface.** Calendar authorization affects
cache keys and derived views. Messaging E2EE changes search, moderation, device recovery,
and attachments. Neither is a feature that can safely be bolted on after data ownership
and delivery contracts are fixed.

**Output:** tested failure/recovery behavior, access boundaries, and abuse controls.

## Phase 8: Defend and evolve

Explain each choice as **need, requirement, choice, alternative, cost, and validation**.

- **Calendar:** preserving colleagues' edits requires version checks. Choose optimistic
  concurrency over silent last-write-wins; accept conflict-resolution UX; measure failed
  saves and successful conflict recovery.
- **Messaging:** preserving accepted messages requires durable commitment before replying.
  Choose storage-backed acceptance over gateway-memory-only handling; accept write latency
  and recovery work; test acknowledged-message loss under gateway and zone failures.

Then evolve from evidence:

| Stage | Calendar | Messaging |
|---|---|---|
| MVP | Modular application, SQL, version checks, outbox, bounded sync | WebSocket-capable app, SQL, client pending work, small groups, E2EE, replay |
| Growth | Targeted caching, read optimization, dedicated reminder workers | Separate gateways, routing hints, delivery workers, partitioning if measured |
| Global | Regional ownership and explicit cross-owner sync/recovery | Conversation home regions, fenced failover, explicit cross-region durability |
{: .system-design-table }

**Release gates:** test lost responses, duplicates, out-of-order work, offline replay,
zone failure, and peak load before exposure. Roll out to a small cohort first. Stop for
any confirmed unauthorized exposure or acknowledged-write loss; pause on the defined
15-minute freshness breach or a pre-agreed acceptance/delivery SLO threshold. Roll back
only when old code remains compatible with written data; otherwise disable the feature
and reconcile. Assign an owner to each response.

Observe save/acceptance success, sync/delivery delay, overdue work, duplicates, and
reconnect failures. Separate queue waiting from processing time; avoid private payloads
in telemetry. Connect these to customer outcomes: successful scheduling without corrective
rework, or confidence that a conversation reached its recipient.

**Decision depth: price the actual work.** Distinguish cheap Calendar reads from broad
free/busy queries. Messaging cost per recipient-device delivery exposes amplification
hidden by cost per submission. Include storage, replicated writes, egress, and always-on
capacity. Managed services reduce operating work but add limits and dependency risk.
If latency improves 30% while cost doubles, verify task-completion or satisfaction gains
and opportunity cost; beating an already adequate latency target is not automatically
product progress.

**Output:** an owned decision record, rollout plan, and measurable reasons to change it.

## Technology reference: choose a coherent subset

Optional reference, not a shopping list. Wide tables scroll on smaller screens.

| Layer | Candidate technologies | Question to settle |
|---|---|---|
| Client and offline state | React, Swift, Kotlin; IndexedDB, SQLite/Room | Which actions remain pending? |
| DNS | Azure DNS, Amazon Route 53, Google Cloud DNS | How does caching affect failover? |
| Edge, reverse proxy, load balancing | Azure Front Door/Application Gateway, AWS ALB/NLB, NGINX, Envoy | Draining, TLS termination, caching? |
| API policy | Azure API Management, Amazon API Gateway, Apigee, Kong | Which checks remain application-owned? |
| API implementation | ASP.NET Core, Spring Boot, FastAPI; Apollo Server, Hot Chocolate | Which interaction pattern fits? |
| Live channels | WebSocket servers, Azure Web PubSub, Azure SignalR Service | Who implements reconnect/replay? |
| Application compute | Azure App Service/Container Apps, AWS ECS; Go, Node.js | Are independent deployments justified? |
| SQL | Azure SQL Database, PostgreSQL, MySQL, Amazon Aurora | Transaction scope and isolation? |
| NoSQL | Azure Cosmos DB, Amazon DynamoDB, MongoDB, Cassandra, ScyllaDB | Keys, transaction scope, hotspots? |
| Cache | Redis, Azure Managed Redis, Amazon ElastiCache, Memcached | Stale or unavailable behavior? |
| Jobs, streams, scheduling | Service Bus, SQS, RabbitMQ; Kafka, Event Hubs, Kinesis; Temporal, Durable Functions | Workers, replay, or timers? |
| Objects and CDN | Azure Blob Storage, Amazon S3, Google Cloud Storage; Front Door, CloudFront, Cloudflare | Authorization and expiry? |
| Identity and secrets | OpenID Connect; Entra External ID, Cognito, Auth0; Key Vault, AWS KMS | Revocation and key rotation? |
| Search, if needed | Azure AI Search, OpenSearch, Elasticsearch | Freshness, permissions, plaintext availability? |
| Notifications | APNs, FCM, Azure Notification Hubs | Hint or application acknowledgment? |
| Observability and analytics | OpenTelemetry, Application Insights, Prometheus/Grafana; Microsoft Fabric, BigQuery | Outcomes without privacy/serving-path risk? |
{: .system-design-table }

**Optional DynamoDB detail:** combine expected-sequence/epoch conditions with the metadata
`Update`; a transaction cannot condition-check and update the same item separately.
Native client-token idempotency lasts 10 minutes; longer retries require application
deduplication records. These service limits do not change the user-facing retry promise.

## Apply the framework to your next product

Apply the framework to your workflow: payments emphasize ledger correctness and
reconciliation; commerce, inventory reservations; analytics, freshness, throughput, and cost.

1. What does the user do, and what exactly does success promise?
2. Which data is authoritative, and where does the operation commit?
3. What work multiplies with users, recipients, or data size?
4. What happens after a timeout, retry, stale read, or regional failure?
5. Which measurement justifies the next layer of complexity?

Change one constraint: ten times the load, half the budget, or stricter privacy.
**Explain which decisions change, which stay, and why.**

## References and further reading

- Google Calendar: [recurrence](https://developers.google.com/workspace/calendar/api/guides/recurringevents),
  [incremental sync](https://developers.google.com/workspace/calendar/api/guides/sync),
  and [push notifications](https://developers.google.com/workspace/calendar/api/guides/push).
- Meta Engineering: [WhatsApp multi-device design](https://engineering.fb.com/2021/07/14/security/whatsapp-multi-device/)
  (historical architecture context, not a current product-limit specification).
- Azure Cosmos DB: [partitioning](https://learn.microsoft.com/en-us/azure/cosmos-db/partitioning)
  and [transactional batches](https://learn.microsoft.com/en-us/azure/cosmos-db/transactional-batch).
- Amazon DynamoDB: [transaction behavior, limits, and idempotency](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/transaction-apis.html).
- Azure Architecture Center: [transactional outbox](https://learn.microsoft.com/en-us/azure/architecture/databases/guide/transactional-out-box-cosmos)
  and [competing consumers](https://learn.microsoft.com/en-us/azure/architecture/patterns/competing-consumers).

> *Note: This blog post was written with assistance from AI*
