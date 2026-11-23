---
layout: post
title: "Agile and Scrum for Product Managers: From Strategy to Reliable Delivery"
seo_title: "Agile and Scrum for Product Managers | Arshad Ali"
date: 2026-11-22
published: true
description: "A practical Agile and Scrum execution guide for PMs: plan work, coordinate dependencies, manage risks, maintain Azure DevOps hygiene, and release safely."
excerpt: "A practical Agile and Scrum execution guide for PMs: plan work, coordinate dependencies, manage risks, maintain Azure DevOps hygiene, and release safely."
author: Arshad Ali
categories:
  - Product-Management
tags:
  - product-management
feature-img: "assets/images/agile-scrum-execution/banner.png"
feature-title: ""
---

# Agile and Scrum for Product Managers: From Strategy to Reliable Delivery

The roadmap says "launch shared calendars." Engineering has started, but connecting
to the sign-in and permissions service is late and reminders remain untested.
Leadership asks whether the launch date still holds. A board full of active
tickets cannot answer that question.

Product managers need more than a good product direction when they also coordinate
delivery. They need an execution system that connects **customer value, usable
software, dependencies, decisions, and release evidence**.

This guide builds that system from first principles. Start with roles and Scrum,
then progress to planning, multi-team coordination, Azure DevOps, and safe releases.
Calendar is the running example; all scenarios, estimates, and plans are **hypothetical**.
No prior technical reading is required; the
[System Design for Product Managers guide]({% post_url 2026-11-14-system-design-framework-product-managers %})
provides optional architectural depth.

**Reading path:** [roles and Agile](#1-clarify-the-role-you-are-playing) ->
[Scrum](#3-understand-scrums-accountabilities) ->
[planning](#6-turn-product-direction-into-small-deliverable-slices) ->
[delivery controls](#9-plan-milestones-and-dependencies-not-just-tickets) ->
[metrics](#13-balance-delivery-metrics-with-quality-and-outcomes) ->
[Azure DevOps](#14-make-azure-devops-reflect-reality) ->
[release and learning](#15-release-safely-not-just-on-schedule).
Diagrams open at full size when selected.

## 1. Clarify the role you are playing

Product, project, and program management overlap, but are not the same job.
**Product management** steers a continuing product toward customer and business
outcomes. **Project management** coordinates a bounded endeavor with agreed
objectives, constraints, and completion criteria. **Program management** coordinates
related projects and other activities to realize broader benefits.

Neither product nor program management excludes execution; their decision
boundaries differ. See APM's definitions of
[project management](https://www.apm.org.uk/resources/what-is-project-management/)
and [program management](https://www.apm.org.uk/resources/what-is-project-management/what-is-programme-management/).

| Perspective | Question it must answer | Calendar example |
| --- | --- | --- |
| Product | Is this the right problem, priority, and investment? | Does shared scheduling reduce coordination effort for target users? |
| Project | Can this bounded release meet its agreed constraints? | What must be completed, by whom, before the pilot? |
| Program | Do related initiatives jointly produce the intended benefit? | Are sign-in, client rollout, training, and support aligned? |
| Engineering | Is the solution technically sound and maintainable? | Are authorization, retries, storage, and recovery correctly designed? |
{: .system-design-table }

When a dedicated delivery lead exists, partner with them. When one does not,
explicitly agree which responsibilities you absorb and which decisions remain
with engineering, security, operations, or a sponsor. Accountability without
decision authority is an escalation problem, not a personal productivity problem.

Protect customer discovery and strategy time when taking on delivery work.
Delegate routine updates and use existing reviews for decisions. If coordination
continually crowds out product work, escalate the capacity or ownership gap.

## 2. Understand Agile before choosing a framework

**Agile** is a set of values and principles for delivering value through feedback
and adaptation, not a synonym for Scrum or a promise of speed.
The [Agile Manifesto and its principles](https://agilemanifesto.org/principles.html)
emphasize collaboration, working software, responsiveness, and sustainable development.

Three terms make the delivery loop easier to follow:

- **Backlog:** an ordered, evolving list of product work.
- **Sprint:** Scrum's fixed-length period for pursuing a goal and creating usable progress.
- **Increment:** a usable addition to the product that meets its quality standard.

In practice, collaborate to resolve uncertainty, demonstrate useful software,
involve customers, and revise plans when evidence changes. Keep necessary
documentation, technical quality, and sustainable working practices inside the plan.

**Iterative** means improving a solution through feedback; **incremental** means
adding usable capability in small pieces. Combine both: polishing mockups without
shipping and shipping components without customer learning each miss part of the goal.

| Approach | Useful when | Watch out for |
| --- | --- | --- |
| Scrum | Complex product work benefits from a stable learning cadence and coherent goals | Sprints that become batches of unrelated assigned tasks |
| Kanban | Work arrives continuously and flow needs active management | A board without WIP controls, explicit policies, or improvement |
| Predictive or hybrid planning | Some commitments, procurement, or approval stages must be planned ahead | Treating uncertain requirements as permanently settled |
| Lean and XP practices | Teams need less waste and stronger engineering feedback | Expecting labels to replace small batches, testing, or collaboration |
{: .system-design-table }

**WIP** means work in progress. [Kanban](https://kanbanguides.org/the-kanban-guide/)
defines workflow boundaries, controls WIP, manages aging work, and improves flow.
A board alone is not Kanban; its practices can complement Scrum. A **service level
expectation (SLE)** forecasts completion time with a stated likelihood, using past
completion times where available. It is not an uptime guarantee.
**Lean** emphasizes value and reducing waste. **XP (Extreme Programming)** adds
engineering practices such as automated testing, refactoring, and frequent integration.

Choose a delivery approach because it fits the work. A two-week Sprint is a common
choice, not an Agile requirement. A quarterly funding decision can coexist with
short delivery and learning cycles.

<figure class="system-design-diagram">
<a href="{{ '/assets/images/agile-scrum-execution/value-delivery-loop.svg' | relative_url }}">
<img src="{{ '/assets/images/agile-scrum-execution/value-delivery-loop.svg' | relative_url }}"
alt="Product decisions become ordered small slices, Sprint work, and usable increments. Release evidence permits rollout; customer outcomes and delivery evidence feed back into priorities and the plan."
loading="lazy" width="900" height="700">
</a>
<figcaption>Figure 1. Delivery progress and product learning are connected but different.
Completed work is evidence of an output, not proof of a customer outcome.</figcaption>
</figure>

## 3. Understand Scrum's accountabilities

[The Scrum Guide](https://scrumguides.org/scrum-guide.html) defines Scrum as a
lightweight framework for complex problems. Its three pillars are **transparency**
(make reality visible), **inspection** (examine progress and results), and
**adaptation** (change based on what you learn).

Its five values are commitment, focus, openness, respect, and courage. For a PM,
that means exposing an integration risk early, protecting a coherent goal, and
welcoming evidence that challenges the roadmap.

A small, cross-functional **Scrum Team**, typically ten or fewer people in the
Guide's description, contains three accountabilities:

| Accountability | Owns | Does not mean |
| --- | --- | --- |
| Product Owner | Maximizing product value; the Product Goal and effective Product Backlog management | A committee or a person who only writes tickets |
| Developers | Creating a usable Increment; sizing work, planning it, adapting the plan, and meeting the Definition of Done | Only programmers, or people waiting for the PM to assign every task |
| Scrum Master | Establishing Scrum and improving team effectiveness; coaching and helping remove impediments | Automatically the project manager or administrative meeting organizer |
{: .system-design-table }

A PM may also be the **Product Owner (PO)**, but the titles are not interchangeable.
If someone else is the PO, resolve product priorities through that accountability,
not a competing backlog. The PO can delegate backlog work but retains accountability.

Developers self-manage their implementation plan. A **Technical Lead** typically
coordinates design and integration; an **Engineering Manager** handles people and
staffing. These organizational roles vary and are not extra Scrum accountabilities.

Agree decision rights using **RACI**: Responsible performs the work, Accountable
owns the result, Consulted supplies input, and Informed receives the outcome.
This organizational example assumes the PM also serves as PO:

| Work or decision | Responsible | Accountable | Consulted | Informed |
| --- | --- | --- | --- | --- |
| Product Backlog ordering | PM/PO | PM/PO | Developers, design | Delivery lead, stakeholders |
| Architecture decision | Developers | Agreed technical lead | Security, operations | PM/PO, delivery lead |
| Staffing allocation | Engineering manager | Engineering manager | Developers, technical lead | PM/PO, delivery lead |
| Release approval | Release lead | Agreed release authority | Engineering, security, operations, PM/PO | Support, stakeholders |
{: .system-design-table }

Use one accountable owner per defined decision, with a deadline and escalation
path. RACI clarifies organizational decisions; it does not replace Scrum's
accountabilities or Developers' control of their plan.

## 4. Know what Scrum makes visible

An **artifact** makes work or value inspectable. A **commitment** gives it a clear
focus and completion standard.

| Artifact | Commitment | Example |
| --- | --- | --- |
| Product Backlog: an evolving, ordered list of needed product improvements | Product Goal | Enable reliable shared scheduling for the initial target group |
| Sprint Backlog: the Sprint Goal, selected items, and Developers' actionable plan | Sprint Goal | An organizer can create a meeting and an authorized attendee can retrieve it |
| Increment: usable, verified capability integrated with previous work | Definition of Done | Meeting creation works end to end and satisfies agreed quality measures |
{: .system-design-table }

The Product Goal is the Scrum Team's longer-term objective. The Sprint Goal is a
single coherent objective, **not the sum of all selected ticket titles**. It allows
scope flexibility while preserving the purpose.

### Acceptance, readiness, and Done are different

**Acceptance criteria** describe a particular item's required behavior.
**Definition of Done (DoD)** describes the quality state required of an Increment.
Neither a merged pull request nor a successful happy-path demo proves both.

A **user story** describes useful behavior from a user's perspective. For Calendar:

> As an organizer, I want to create a meeting so that authorized attendees can
> retrieve the same saved event.

Illustrative acceptance criteria:

- Authorized creation saves the event; unauthorized creation is rejected.
- A retry after a lost response returns the original result without a second event.
- Attendees see only events they are authorized to access.
- Time-zone behavior follows the agreed event-time contract.

Illustrative DoD: reviewed code, relevant automated and integration tests passing,
security checks, useful **telemetry** (operational measurements and diagnostic
events), updated documentation, and integration into a usable product. Agree the
standard with the team and applicable organizational requirements.

A **Definition of Ready** is an optional team checklist, not a Scrum artifact or
mandatory approval gate. It can check that an item is understood, testable, small
enough, and has known dependencies. Do not demand that all uncertainty disappear
before development; use a focused investigation when learning is the work.

## 5. Use Scrum events as decision and learning points

The **Sprint** is the containing event, of fixed length **one month or less**.
A new Sprint begins immediately after the previous one ends.
Planning, Daily Scrums, Review, and Retrospective occur within it. Development,
testing, refinement, and integration are not separate phases after the Sprint.

| Event | Purpose and participants | Maximum timebox |
| --- | --- | --- |
| Sprint Planning | Scrum Team establishes why the Sprint is valuable, selects what is feasible, and plans how to deliver it | 8 hours for a one-month Sprint |
| Daily Scrum | Developers inspect progress toward the Sprint Goal and adapt their plan | 15 minutes each working day |
| Sprint Review | Scrum Team and stakeholders inspect the outcome and adapt future work | 4 hours for a one-month Sprint |
| Sprint Retrospective | Scrum Team improves quality and effectiveness, including its working practices and DoD | 3 hours for a one-month Sprint |
{: .system-design-table }

Planning, Review, and Retrospective are usually shorter for shorter Sprints;
the Daily Scrum remains 15 minutes. These are maximums, not meeting-duration targets.
The familiar "yesterday, today, blockers" format is optional.
The Daily Scrum is not a PM status meeting; a PO or Scrum Master working on
Sprint Backlog items participates as a Developer.

**Backlog refinement** is ongoing clarification, splitting, ordering, and sizing,
not a sixth prescribed Scrum event. Keep the next likely items understandable
without exhaustively detailing the entire roadmap.

During a Sprint, protect the Sprint Goal and do not lower quality. Developers
and the PO may renegotiate scope as they learn. If the goal becomes obsolete,
**only the PO can cancel the Sprint**. A delayed item does not automatically
justify cancellation.

A Review is a working conversation, not just a demo or release gate. Usable
Increments can be released earlier; release governance still applies.
The Retrospective improves how the team works, with actions inspected next Sprint.

<figure class="system-design-diagram">
<a href="{{ '/assets/images/agile-scrum-execution/scrum-learning-loop.svg' | relative_url }}">
<img src="{{ '/assets/images/agile-scrum-execution/scrum-learning-loop.svg' | relative_url }}"
alt="A Sprint contains Planning, ongoing development with Daily Scrums, Review, and Retrospective. Refinement continues during delivery, usable increments can be released when ready, and learning informs the next Sprint."
loading="lazy" width="900" height="740">
</a>
<figcaption>Figure 2. Scrum creates repeated inspection and adaptation, not a miniature
waterfall with testing and release postponed until after the Sprint.</figcaption>
</figure>

## 6. Turn product direction into small deliverable slices

Connect **product outcome -> goal -> capability -> backlog item -> implementation work**.
Organizations may group work as initiatives, Epics, Features, Stories, and Tasks.
These are planning conventions, not required Scrum artifacts; the Azure DevOps section
shows their hierarchy.

Start with a one-page delivery brief:

- Target user, problem, intended outcome, and measurement plan.
- Initial scope and explicit exclusions.
- Correctness, privacy, reliability, accessibility, and performance expectations.
- Constraints: dates, budget, staffing, integrations, and regulatory obligations.
- Decision owners and the evidence required for release.

Split **vertically**: each slice connects the user interface, service, storage,
and tests needed for usable behavior. Separate "database, service, then interface"
Sprints delay integrated feedback.

For Calendar, start with an authorized organizer creating a non-recurring event
that an attendee can retrieve. Add invitations, reminders, recurrence, and richer
sharing later. The first slice still needs durable saving, permissions, retry
handling, and defined time-zone behavior.

**Durable** means saved work survives the agreed failures; **deduplication**
recognizes retries without creating duplicate events. Small scope does not mean
weaker correctness or privacy.

An **MVP (minimum viable product)** tests a value hypothesis with a coherent product.
A prototype may test an interface without production guarantees; label it accordingly.

Prioritize customer value, risk reduction, dependencies, learning, and effort.
[MoSCoW](https://www.agilebusiness.org/resource/what-is-moscow-prioritization/)
distinguishes must, should, could, and not-this-time scope. Use it to separate
essential Calendar behavior from optional depth; it supports judgment, not automatic ordering.

**Technical debt** means design or implementation compromises that increase future
maintenance or change costs. Plan for it alongside security, reliability, and
accessibility. A **spike** is a time-boxed investigation with a question and an
output, such as a tested design option.

Use [Bill Wake's **INVEST** checklist](https://xp123.com/invest-in-good-stories-and-smart-tasks/)
as an optional story-quality aid: **Independent, Negotiable, Valuable, Estimable,
Small, Testable**. "Build the database" describes implementation; "save and retrieve
a meeting without duplicate retries" describes verifiable user value. Independence
does not erase real dependencies, and negotiability does not make safety optional.
INVEST is not a Scrum requirement or readiness gate.

## 7. Estimate to expose uncertainty, not manufacture certainty

The Developers doing the work are responsible for sizing it. **Story points** are
team-relative estimates, often reflecting effort, complexity, and uncertainty;
five points do not mean five days. Scrum does not require points.

**Planning Poker** combines independent estimates with discussion. If one person
sees a small service change and another sees retries and data migration, resolve
that difference before settling on a number.

Separate four concepts:

- **Estimate:** an informed assessment of a work item's size or difficulty.
- **Capacity:** realistic availability after leave, support, meetings, and skill constraints.
- **Forecast:** a likely delivery window under stated assumptions.
- **Commitment:** an agreed objective or obligation, not a claim that uncertainty vanished.

Scrum's formal commitments are the Product Goal, Sprint Goal, and DoD; selected
work and release dates are forecasts or separately agreed obligations.

For illustration, 116 remaining points divided by a historical average of 29
completed points per Sprint suggests four Sprints. This assumes comparable work,
stable sizing, similar capacity, and manageable dependencies; it excludes any
unmodeled approval or rollout delay. It is **not** a launch promise.

**Velocity** is completed estimated work per Sprint; **throughput** is completed
items per period. Use comparable historical work and a distribution, not only an
average. Do not compare teams or individual engineers by points.

Express a range, its largest uncertainty, and the next evidence that will refine it.
Distinguish the business target from the forecast; justify buffers through known
uncertainties rather than arbitrary percentages.

**Advanced option: Monte Carlo forecasting.** Repeatedly sample representative
historical throughput to model completion-time distributions. An 85th-percentile
result describes the simulation under its assumptions, not an objective guarantee
about reality. Novel work, changing scope, shared specialists, and dependent teams
need explicit treatment; a simple item-count model may be misleading.

## 8. Run the Sprint without becoming the task dispatcher

The PM resolves product questions and external dependencies; Developers maintain
the Sprint Backlog and adapt their plan. Finish valuable work before starting more,
and coordinate broader decisions outside the Daily Scrum.

### A complete illustrative Calendar Sprint

Assume a two-week Sprint with a working connection to the sign-in and permissions
service, called **Identity** below. The plan is illustrative:

1. **Prepare:** the PO proposes a candidate goal: an organizer creates a meeting
   that an authorized attendee can retrieve. Clarify that Story and a smaller
   edit-title Story. Developers assess dependencies and capacity, including one
   person's support duty. Reminders stay out of scope.
2. **Plan:** the Scrum Team creates the Sprint Goal during Planning. Developers
   select the two Stories and build a feasible plan using comparable past work,
   leaving room for learning and interruptions.
3. **Build and inspect:** Developers integrate and test early. A lost-response
   test exposes duplicate meetings; link the defect and failing test.
4. **Adapt:** Developers and PO renegotiate scope, stopping optional editing to
   fix the defect. Update the Sprint Backlog without weakening DoD or hiding
   overcommitment through overtime.
5. **Review:** create/retrieve meets DoD, including permission, retry, and time-zone
   checks. Stakeholders inspect the usable Increment and discuss next needs.
   Unfinished editing is not part of it: return it to the Product Backlog for
   reordering, not automatic carryover or partial-completion credit.
6. **Improve:** at Retrospective, choose earlier adverse-case testing. A Developer
   owns adding the retry scenario to the first integrated test run next Sprint;
   inspect whether that action surfaces defects earlier.

Achieving the Sprint Goal does not automatically authorize a customer pilot.
Release readiness and customer outcomes need their own evidence.

## 9. Plan milestones and dependencies, not just tickets

A **milestone** is an evidence-based checkpoint. "API development complete" is
weaker than "authorized clients create and retrieve an event in the integrated
environment, including the retry test." An **API** is the interface through which
software components request data or actions.

For milestones such as the integrated journey, pilot readiness, and broader
availability, define scope, evidence, an owner, and exit criteria.

A **dependency** exists when work requires another capability, decision, environment,
or approval. Track the handoff, not just the supplying team's ticket:

| Handoff field | Calendar example |
| --- | --- |
| Provider and consumer | Identity team -> Calendar API team |
| Required capability | Testable authorization contract and representative test identities |
| Needed-by checkpoint | Before integrated meeting creation is verified |
| Acceptance evidence | Authorized calls succeed; unauthorized calls fail; failure behavior is documented |
| Owner and escalation trigger | Named leads; escalate if the agreed test endpoint misses the checkpoint |
| Contingency | Resequence independent work; use only a validated, approved alternative |
{: .system-design-table }

**Contract tests** check agreed behavior between components; **mocks** simulate a
dependency. Both reduce waiting, but passing against a mock does not verify the
real integration. Book shared test environments and scarce reviewers early.

The **critical path** is the longest dependent sequence in the current schedule
model. Delaying an activity on that path delays completion unless the plan changes.
**Float** is the delay an activity can absorb without moving the modeled finish.
Shared people, changing durations, and approval queues can alter the path.

In Figure 3, Identity takes two days and storage three in parallel. Integration
takes two after both, additional integrated failure checks two, and pilot readiness
one: **3 + 2 + 2 + 1 = 8 days** on the longest path. Assume fixed durations,
available resources, and no extra waits, not a real calendar-date forecast.
Testing occurs throughout; the later checks verify failures across connected components.

<figure class="system-design-diagram">
<a href="{{ '/assets/images/agile-scrum-execution/dependency-path.svg' | relative_url }}">
<img src="{{ '/assets/images/agile-scrum-execution/dependency-path.svg' | relative_url }}"
alt="Identity and storage proceed in parallel with their own tests. Integration precedes additional cross-component failure checks and pilot readiness. The longest illustrative path is eight days."
loading="lazy" width="900" height="650">
</a>
<figcaption>Figure 3. Track accepted handoffs along the longest path. The later
failure checks supplement testing throughout development.</figcaption>
</figure>

### A dependency slips across different cadences

In a separate enterprise Calendar pilot plan, the API and client teams use
two-week Sprints. Identity maintains a separate platform product on a three-week
cadence; security and operations manage continuous review and environment queues.
Align these five groups' handoffs, not their meeting calendars.

Suppose Identity's agreed test endpoint moves from Tuesday to the following
Monday, consuming the integration buffer:

1. **Confirm the handoff:** the provider states the new test-endpoint checkpoint,
   required authorization behavior, and remaining uncertainty.
2. **Resequence:** continue independent work and contract tests without treating
   mocks as real authorization evidence.
3. **Replan:** check integration time, security-review availability, and operations
   readiness against the revised forecast.
4. **Escalate a choice:** present the pilot forecast and options to the release
   authority. Deferring reminders cannot remove the authorization prerequisite.
5. **Update the linked plan:** record the issue, provider/consumer owners,
   decision, and next checkpoint; notify affected stakeholders.

Your team's completed tickets do not establish readiness across the whole path.

## 10. Make risks, issues, and decisions actionable

A **risk** might happen; an **issue** is already happening. An **assumption** is
something the plan treats as true but needs validation. A **dependency** is a
prerequisite relationship. A **decision** records an authorized choice.
A **blocker** currently prevents progress; an issue need not block all work.

Use a small **RAID log** for risks, assumptions, issues, and dependencies, plus a
decision log. Some organizations use different RAID expansions; agree yours
explicitly. Link entries to the execution work rather than maintaining duplicate
status in several spreadsheets.

| Type | Example | Useful action |
| --- | --- | --- |
| Risk | A burst of Calendar reminders may overwhelm notification delivery | Load-test the burst; define the threshold and owner |
| Assumption | Identity test accounts will be available before integration | Confirm with the provider by a named checkpoint |
| Issue | The required test environment is unavailable now | Assign restoration and resequencing actions |
| Dependency | Pilot requires a verified authorization integration | Track provider, consumer, needed-by date, and evidence |
| Decision | Defer optional reminder customization from the pilot | Record rationale, approver, impact, and reconsideration trigger |
{: .system-design-table }

For each material risk, record likelihood, impact, owner, mitigation, observable
trigger, contingency, and next review. Avoid, reduce, transfer some exposure,
accept explicitly, or escalate as appropriate. Contractual transfer does not
erase your duty to verify customer safety.

Likelihood/impact scores support rough triage: "4" times "5" is not a probability
or expected financial loss. Prioritize credible severe consequences. A fallback
such as switching providers remains another risk until tested and authorized.

## 11. Manage change through explicit trade-offs

Agile welcomes useful change; it does not make new scope free.
Separate **Product Backlog reordering**, **Sprint scope negotiation**, and
**changes to external release commitments**.

First agree which release constraint is firm:

| Commitment model | Practical choice | Main risk |
| --- | --- | --- |
| Fixed scope, flexible date | Deliver the agreed capability; revise the window as evidence changes | Unbounded additions masquerading as the original scope |
| Fixed date, flexible scope | Protect a minimum complete user journey; defer optional depth | Cutting so much that the pilot cannot test its intended value |
| Fixed date and scope | Validate feasibility early, expose uncertainty, and agree who renegotiates a threatened commitment | Treating the target as certainty despite unresolved dependencies |
{: .system-design-table }

Budget, skills, and quality obligations constrain all three. If the forecast
contradicts a commitment, escalate a decision rather than reduce testing or safety.

Suppose delegated Calendar access is requested late in the pilot plan. Evaluate
user value, authorization/privacy implications, effort, dependencies, and regression
coverage. Present choices:

1. Add it and move the delivery target.
2. Add it and remove other nonessential scope.
3. Preserve the pilot's learning objective and deliver it later.
4. Reconsider the pilot if it cannot test the intended value without this capability.

Record **request, rationale, alternatives, forecast impact, recommendation,
decision owner, and updated plan**. Developers and the PO negotiate Sprint scope
without endangering the goal; broader commitments go to the agreed authority.

Adding people may not remove a specialist bottleneck and costs onboarding time.
For urgent incidents, make the interruption policy and forecast impact visible.

**Organizational change management** prepares people, not just scope: identify
affected users, explain new workflows, provide training or migration guidance,
pilot adoption, and inspect feedback. Calendar can work technically yet fail if
administrators misunderstand sharing policies. Assign adoption work alongside delivery.

## 12. Give stakeholders evidence and decisions, not theater

Stakeholder management starts by understanding who supplies work, who approves
release, who operates it, and who bears the customer consequences. Establish
communication cadence and escalation authority before trouble.

Use one execution record and tailor summaries: engineers need handoffs, leadership
needs trade-offs, and support needs customer behavior and recovery instructions.
Connect decisions to shared goals rather than chasing more updates.

An illustrative status update:

> **Goal:** pilot secure meeting creation and retrieval.
> **Evidence:** the durable save/retry test passes in integration.
> **Gap:** authorization verification is not yet complete.
> **Forecast:** the target remains conditional on the Identity handoff.
> **Decision needed:** confirm the review slot or resequence the pilot.
> **Next checkpoint:** report the integrated authorization result at the weekly review.

If you use red/amber/green status, define the thresholds and attach the evidence.
"Green because nobody escalated" is not a meaningful rule. Communicate changes
before a milestone is missed; specify what a decision changes, not just who is late.

## 13. Balance delivery metrics with quality and outcomes

Choose signals before configuring dashboards. Define boundaries consistently:
**lead time** runs from a specified request/commitment point to completion;
**cycle time** runs from work starting to completion. **Work-item age** is elapsed
time since an unfinished item started. Tool definitions may differ.

| Signal | What it reveals | Decision it supports |
| --- | --- | --- |
| WIP and unfinished-item age | Work accumulating or waiting too long | Finish, unblock, split, or stop starting more |
| Throughput and cycle-time distribution | Actual flow over comparable work | Forecast a range and investigate tail delays |
| Burnup | Completed work alongside total scope | Explain whether scope growth moved the forecast |
| Burndown | Remaining planned work over time | Inspect progress, while exposing scope changes |
| Sprint Goal achievement | Whether the Sprint's purpose was achieved | Revisit focus, dependencies, or selection |
| Defects, incidents, and recovery evidence | Whether speed is degrading safety | Improve tests, architecture, or release controls |
| Adoption and successful user journeys | Whether delivery created useful value | Continue, adapt, or stop the investment |
{: .system-design-table }

Delivery measures show how work moves; product measures show whether it matters.
For Calendar, measure successful scheduling and coordination effort, not just
events created or code shipped.
Define cohorts (the measured user groups), baselines, targets, time windows,
and guardrails: limits on undesirable effects. No single metric ranks productivity.

**Advanced detail: flow relationships.** Under stable, consistently measured flow,
**Little's Law** is average WIP = throughput x average cycle time. At two completed
items per day and five days average cycle time, average WIP is ten items.
Use the same workflow boundaries and long-run averages; this is not a staffing formula.
**Flow efficiency** is active work time divided by elapsed flow time. Board states
that do not record activity cannot establish individual effort.

**Advanced detail: DORA (DevOps Research and Assessment).**
[Current guidance](https://dora.dev/guides/dora-metrics/) uses five metrics,
evolving the older four-key-metrics model:

- **Change lead time:** elapsed time from a code change committed to version
  control to deployment in production.
- **Deployment frequency:** deployments per period, or time between deployments.
- **Failed deployment recovery time:** time to recover from a failed deployment
  requiring immediate intervention, not every incident's recovery time.
- **Change fail rate:** the proportion of deployments requiring immediate intervention.
- **Deployment rework rate:** the proportion of deployments that are unplanned
  and result from production incidents.

Measure at an application/service boundary and use these together, not deployment
frequency alone. Deployment is a delivery output, not proof of customer value.

## 14. Make Azure DevOps reflect reality

**Azure DevOps (ADO)** is a suite: **Boards** tracks work, **Repos** stores code,
**Pipelines** automates builds/deployments, and **Test Plans** manages testing.
The board records execution; it does not replace strategy or operational evidence.

### Choose the process and configure team scope

[Process selection](https://learn.microsoft.com/en-us/azure/devops/boards/work-items/guidance/choose-process?view=azure-devops)
sets work-item types and workflows. Selecting "Scrum" does not establish Scrum;
teams can also practice Scrum using the "Agile" process.

| Default process | Common hierarchy | Important distinction |
| --- | --- | --- |
| Agile | Epic -> Feature -> User Story -> Task | Story Points are a common sizing field |
| Scrum | Epic -> Feature -> Product Backlog Item -> Task | Effort is a common sizing field |
{: .system-design-table }

Basic uses a simpler Epic/Issue/Task hierarchy; CMMI adds formal requirements,
change, and risk work-item types.

Bugs can sit at requirement or task level. Custom states, fields, and processes
vary; check team configuration before copying a template or adding fields.

Configure **Area Paths** for team scope and **Iteration Paths** for time periods,
including selected Sprints and dates. Area Paths do not assign a person or decision
authority. Confirm permissions, board columns, completion policies, and blocker handling.

### Connect hierarchy, dependencies, and evidence

For Calendar, an **Epic** groups a broad objective: "Reliable shared scheduling."
A **Feature** is a capability: "Meeting creation." A **Story** describes user
behavior: "Authorized event save survives retry." **Tasks** implement, test, and
instrument it.

Use **Parent/Child** links for decomposition, **Predecessor/Successor** for
prerequisites, and **Related** for association. Link design, code reviews, builds,
tests, and release evidence to substantiate completion.

<figure class="system-design-diagram">
<a href="{{ '/assets/images/agile-scrum-execution/ado-traceability.svg' | relative_url }}">
<img src="{{ '/assets/images/agile-scrum-execution/ado-traceability.svg' | relative_url }}"
alt="An Agile-process Epic contains a Feature, User Story, and Tasks through parent-child links. Identity work is a predecessor rather than a parent, and design, code, tests, and rollout records provide linked evidence."
loading="lazy" width="900" height="740">
</a>
<figcaption>Figure 4. A work-item hierarchy describes decomposition. Dependency links
describe prerequisites; evidence links support completion and release decisions.</figcaption>
</figure>

[Delivery Plans](https://learn.microsoft.com/en-us/azure/devops/boards/plans/review-team-plans?view=azure-devops)
shows scheduled work across configured team backlogs; dependency visualization
needs supported links. It neither resolves resource conflicts nor certifies readiness.

### Keep the minimum useful hygiene

- **Before work starts:** clear behavior, acceptance criteria, parent, priority,
  owning team, known prerequisites, and appropriate iteration.
- **While active:** accurate state, a current contact, remaining work where used,
  linked decisions, and explicit blocker owner/next action.
- **Before completion:** acceptance and DoD evidence, tests/code links, remaining
  release obligations, and no misleading "Done" state.
- **Regularly:** remove duplicates, revisit stale items, reorder deferred work,
  and ensure dashboards reflect the latest scope.

**Assigned To** identifies a contact, not sole accountability. Define the meaning
and removal policy of a **Blocked** tag; it is not a universal default state.

Save a query for your team's active work not updated in seven days, oldest first.
Adapt states and Area Path; seven days is an illustrative review threshold. See
[Azure Boards date-query guidance](https://learn.microsoft.com/en-us/azure/devops/boards/queries/query-by-date-or-current-iteration?view=azure-devops).
Changed Date tracks updates, not progress: a comment can hide an aging blocker.
Also check missing contacts and acceptance evidence.

### A small dashboard that supports decisions

For an illustrative Calendar pilot, start with four views:

| View and evidence | Question to answer | PM response |
| --- | --- | --- |
| Query Results for active items with the team's agreed Blocked tag | Which blocker lacks an owner or next action? | Resolve the question or escalate the specific decision |
| Cumulative Flow Diagram plus an aging-work review | Is work accumulating in a workflow stage? | Investigate waiting, environments, and verification capacity |
| Query Results for unresolved pilot defects, ordered by agreed severity | Does any defect violate release criteria? | Obtain fix evidence or an authorized readiness decision |
| Delivery Plans and linked dependency handoffs | Which needed-by checkpoint is threatened? | Confirm the provider forecast and revise the dependent plan |
{: .system-design-table }

Queries and the [Analytics Cumulative Flow Diagram (CFD)](https://learn.microsoft.com/en-us/azure/devops/report/dashboards/cumulative-flow?view=azure-devops)
are built in, subject to access and service/version configuration. Tags require
team policies; aging calculations or missed-handoff alerts may require Analytics,
custom fields, or automation.

A CFD shows counts by workflow stage over time; band thickness is the number
of items in that stage. If Testing grows from two to seven while completed work
increases by one, investigate accumulation. Item age, environment failures, scope
changes, or outdated states can explain it; the chart does not prove testers are slow.

## 15. Release safely, not just on schedule

The **software development lifecycle (SDLC)** spans discovery, design, implementation,
verification, release, operation, and learning. Agile shortens feedback across it
without removing engineering or operational responsibilities.

**Continuous integration (CI)** frequently integrates changes with automated checks.
**Continuous delivery** keeps verified changes ready for release; **continuous
deployment** automatically deploys qualifying changes to production.
Neither means every change must immediately reach every customer.

Design quality throughout development: unit tests for focused logic, integration
and contract tests for boundaries, end-to-end tests for user journeys, and
risk-driven checks for performance, security, accessibility, and recovery.
Include code review, secrets protection, dependency checks, and data-migration validation.

Distinguish three states:

1. **Done:** an integrated, usable Increment meets its quality standard.
2. **Release-ready:** rollout-specific obligations and decisions are satisfied.
3. **Released and useful:** it reaches intended users, operates safely, and produces
   evidence of the outcome you wanted.

Release controls must not hide unfinished integration or quality work behind
"Done." A usable Increment may still await training or an approved launch window.

Before release, establish:

- Approved scope, accepted behavior, test evidence, and unresolved-risk decisions.
- Migration and compatibility plan, including old/new client coexistence.
- Deployment/runbook owners, monitoring, alerts, and on-call/support readiness.
- Rollout stages, observation windows, and quantitative stop/rollback triggers.
- Tested recovery, including data changes that code rollback cannot undo.
- Customer documentation, communication, access eligibility, and feedback channels.

Agree a **recovery time objective (RTO)** for restoration and a **recovery point
objective (RPO)** for acceptable data loss, usually expressed as a time window.
Match them to the customer promise; do not quietly permit loss of confirmed
Calendar events or reservations.

A **feature flag** controls exposure; it is not a substitute for authorization,
tests, or a safe schema migration. A **canary** exposes a change to a limited cohort
and evaluates it before broader rollout. See
[Google SRE's canary guidance](https://sre.google/workbook/canarying-releases/).

"Preview" and "general availability" are service policies, not Scrum events.
Define eligibility, support promises, limitations, and exit criteria.
A Preview still requires safe handling of real user data.

<figure class="system-design-diagram">
<a href="{{ '/assets/images/agile-scrum-execution/release-learning.svg' | relative_url }}">
<img src="{{ '/assets/images/agile-scrum-execution/release-learning.svg' | relative_url }}"
alt="A usable Done increment proceeds through rollout readiness, a limited pilot, and broader exposure only with evidence. Failed checks stop expansion and trigger safe recovery; customer and operational learning updates the backlog."
loading="lazy" width="900" height="700">
</a>
<figcaption>Figure 5. Done, release-ready, and successful in customers' hands are
different claims. Each needs its own evidence and decision.</figcaption>
</figure>

## 16. Walk Calendar from first slice to pilot

This sequence connects the [worked Sprint](#a-complete-illustrative-calendar-sprint)
to a pilot, **not a promised schedule**. Feedback can change the order.

| Checkpoint | Capability and evidence |
| --- | --- |
| First integrated journey | Authorized create/retrieve with durable saving and duplicate-safe retries |
| Next usable depth | Invitations, attendee responses, and recoverable background notifications |
| Further depth | Cancellation propagation and reminders; explicitly designed recurrence and sharing |
| Pilot readiness | Permission, time-zone, lost-response, and migration tests pass; support and monitoring are ready |
{: .system-design-table }

Verify behavior and readiness at each step: a fixed 24-hour interval does not
preserve local recurring-meeting time across daylight-saving changes, and scheduling
a notification does not prove delivery. After the pilot, inspect customer outcomes.

## 17. Scale execution without scaling bureaucracy

Multiple teams add coordination cost, not automatically delivery capacity.
If Scrum Teams work on the same product, the Scrum Guide calls for a shared
Product Goal, Product Backlog, and Product Owner, and a common DoD. Separate
products or organizational programs need explicitly coordinated priorities and
interfaces; do not mechanically impose one backlog on everything.

Use cross-team reviews to resolve handoffs, not replay Daily Scrums. They are
coordination practices, not prescribed Scrum events; named scaling frameworks
are options, not prerequisites.

At portfolio level, compare initiatives against strategic fit, customer impact,
urgency, risk, effort, confidence, and opportunity cost. Sequence work around
scarce security, infrastructure, and data specialists. Another frontend engineer
will not remove a security-review bottleneck.

Make maintenance, incidents, reliability, technical debt, and discovery capacity
visible. Allocation percentages are discussion aids, not universal rules.
Busy specialists are not a success if valuable work sits in queues.

AI can assist with summaries and checks. Keep private data in approved tools,
verify original evidence, and retain human approval of decisions and changes.

## 18. Putting it into practice

Use the smallest cadence that produces timely decisions:

| Cadence | Inspect | Leave with |
| --- | --- | --- |
| Daily, as needed | Material blockers, aging work, urgent incidents | A resolved question or owner and next action |
| Each Sprint | Goal, usable Increment, stakeholder feedback, team effectiveness | Adapted backlog and a concrete improvement |
| Weekly for multi-team work | Milestones, handoffs, RAID changes, forecast, decisions | Updated plan and a concise stakeholder summary |
| Monthly or at portfolio checkpoints | Outcomes, competing investments, shared capacity | Explicit priority and investment changes |
| Each release | Scope, readiness, rollout observations, support and recovery | Authorized exposure, pause, or recovery decision |
{: .system-design-table }

Reuse existing events or linked updates; inspect critical risks more frequently.

Take this checklist into your next initiative:

- [ ] Clear outcome, scope, decision owners, and small slices with an agreed DoD.
- [ ] Realistic forecast, owned dependencies, and actionable risks and decisions.
- [ ] Work items and milestone evidence that reflect actual progress.
- [ ] Release, support, monitoring, and recovery readiness.
- [ ] Customer and delivery evidence that changes priorities and working practices.

**Start with one journey, one Sprint Goal, and one release checkpoint.** Ask:
what must be true for us to call this useful, Done, and safe to expose?
Then make that evidence visible. Wearing the delivery hat should strengthen
product judgment, not replace it with ticket administration.

## References and further reading

Read the foundations first, use the tooling guidance while setting up execution,
and return to the delivery research as you improve the system.

1. **Association for Project Management: [project management](https://www.apm.org.uk/resources/what-is-project-management/)
   and [program management](https://www.apm.org.uk/resources/what-is-project-management/what-is-programme-management/).**
   Clarifies bounded delivery versus coordinated beneficial change. Useful for
   agreeing responsibilities without reducing program management to task tracking.
2. **[Agile Manifesto](https://agilemanifesto.org/) and [its twelve principles](https://agilemanifesto.org/principles.html).**
   The original foundations for collaboration, adaptation, working software, and
   sustainable delivery. Read them before equating Agile with any tool or ceremony.
3. **[Ken Schwaber and Jeff Sutherland: The Scrum Guide](https://scrumguides.org/scrum-guide.html).**
   The November 2020 definition of Scrum's accountabilities, events, artifacts,
   and commitments. Distinguishes required Scrum elements from optional practices.
4. **[The Kanban Guide](https://kanbanguides.org/the-kanban-guide/)
   and [Bill Wake: INVEST in Good Stories](https://xp123.com/invest-in-good-stories-and-smart-tasks/).**
   Kanban explains workflow, WIP, and improvement; Wake supplies an optional
   story-quality checklist. Together they help shape valuable work and keep it flowing.
   For optional prioritization depth, explore
   [RICE](https://www.intercom.com/blog/rice-simple-prioritization-for-product-managers)
   and [WSJF](https://framework.scaledagile.com/wsjf/); both require explicit assumptions
   and judgment.
5. **Microsoft Azure Boards: [process selection](https://learn.microsoft.com/en-us/azure/devops/boards/work-items/guidance/choose-process?view=azure-devops),
   [Sprint configuration](https://learn.microsoft.com/en-us/azure/devops/boards/sprints/define-sprints?view=azure-devops),
   [work-item links](https://learn.microsoft.com/en-us/azure/devops/boards/backlogs/add-link?view=azure-devops),
   [Delivery Plans](https://learn.microsoft.com/en-us/azure/devops/boards/plans/review-team-plans?view=azure-devops),
   and [Cumulative Flow Diagrams](https://learn.microsoft.com/en-us/azure/devops/report/dashboards/cumulative-flow?view=azure-devops).**
   Connects the execution model to actual work-item types, iterations, and
   dependency views. Verify process, version, access, and team configuration.
6. **[DORA: Software Delivery Performance Metrics](https://dora.dev/guides/dora-metrics/).**
   Describes the current five-metric model and common measurement pitfalls.
   Useful for improving delivery performance without turning points into a productivity score.
7. **Google SRE: [Release Engineering](https://sre.google/sre-book/release-engineering/)
   and [Canarying Releases](https://sre.google/workbook/canarying-releases/).**
   Explains reproducible release processes and evidence-driven exposure.
   Useful for turning "ready to launch" into a tested operational decision.

> *Note: This blog post was written with assistance from AI*
