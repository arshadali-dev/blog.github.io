---
layout: post
title: "Product Prioritization: Build Trust, Remove Blockers, Create Value"
seo_title: "Product Prioritization for PMs | Arshad Ali"
date: 2026-11-24
published: true
description: "A practical PM guide to prioritizing strategy, product trust, adoption blockers, and enterprise readiness without letting scores or large accounts dictate the roadmap."
excerpt: "A practical PM guide to prioritizing strategy, product trust, adoption blockers, and enterprise readiness without letting scores or large accounts dictate the roadmap."
author: Arshad Ali
categories:
  - Product-Management
tags:
  - product-management
  - product-strategy
feature-img: "assets/images/product-feature-prioritization/banner.png"
feature-title: ""
---

# Product Prioritization: Build Trust, Remove Blockers, Create Value

A new capability looks compelling in a demo. A reliability fix does not. Private connectivity,
audit logs, and deployment automation rarely make exciting launch headlines. Yet these less
visible investments can determine whether customers can use the product at all.

After more than a decade in product management and engineering, my perspective is this:
**prioritization is not about building the most features. It is about choosing the investments that make the
product valuable, trustworthy, and usable for the customers we intend to serve.**

For enterprise and consumer products, the workflow is: **set an outcome, assess obligations
and blockers, compare value and cost, commit within capacity, then measure and revisit.**
All scenarios are **hypothetical**, not accounts of specific customers, employers, or
measured results.

## 1. Start with the mission, then choose the outcome

A mission provides direction; a planning objective defines progress now. Without that link,
almost any feature can be called strategic.

I start with three questions:

- What customer problem does the company or team exist to solve?
- Which customer segment and business outcome matter most in this planning period?
- What must remain true while we pursue that outcome?

The third question defines **guardrails**: boundaries that prevent progress on one metric from
damaging something important, such as reliability, security, customer satisfaction, or cost.

For an enterprise analytics product, "ship another dashboard" is an output. "More qualified
pilots reach a defined production milestone" is an outcome.

Different contexts lead to different investments:

| Current objective | Investments worth investigating |
| --- | --- |
| Find product-market fit | Validate the core problem, improve first-use success, test demand |
| Increase enterprise adoption | Resolve verified deployment, security, and governance barriers |
| Improve retention | Address workflow failures, reliability gaps, and unmet recurring needs |
| Improve profitability | Reduce cost per successful workload and avoid unnecessary operating complexity |
{: .system-design-table }

These are starting hypotheses, not automatic rankings. A startup still needs appropriate
security; an enterprise platform still needs differentiated value.

Understand the problem before comparing solutions. A request for another setting might mean
customers need predictable performance, which better defaults could provide. Teresa Torres's
[opportunity solution trees](https://www.producttalk.org/opportunity-solution-trees/)
connect outcomes, customer needs, solutions, and assumption tests.

If the customer segment or underlying problem is still unclear, start with
[Product Sense and the PRODUCT Framework]({% post_url 2026-11-25-product-sense-product-framework %})
before ranking proposed features.

The diagram maps the decision loop. Select it to open the full-size version.

<figure class="system-design-diagram">
<a href="{{ '/assets/images/product-feature-prioritization/decision-flow.svg' | relative_url }}">
<img src="{{ '/assets/images/product-feature-prioritization/decision-flow.svg' | relative_url }}"
alt="Strategic context leads to risk assessment, required remediation or comparison of discretionary opportunities, a capacity-constrained plan, and an outcome review that feeds new evidence back into planning."
loading="lazy" width="900" height="720">
</a>
<figcaption>Figure 1. Triage required work, compare discretionary opportunities, and plan both against real capacity. The branches are decision categories, not a rule that all remediation must finish before any innovation can proceed.</figcaption>
</figure>

## 2. Protect product trust before adding marginal capability

I give material quality, reliability, and security problems priority over discretionary
feature additions. But these terms describe different failures:

- **Quality:** the product does the right thing, including correct results and usable workflows.
- **Reliability:** it does that consistently under expected operating conditions.
- **Security:** identities, systems, and data are protected against unauthorized access or misuse.

The distinction matters. A service can be available and still return incorrect results.
A feature can work correctly and still expose data to the wrong user.

With engineering, security, operations, and relevant legal or compliance owners, agree the
minimum bar: unacceptable harm, applicable obligations, and remediation severity and timing.
A high feature score cannot waive a binding requirement. NIST's
[Cybersecurity Framework and organizational profiles](https://www.nist.gov/cyberframework/profiles)
offer a structured way to compare current and desired security outcomes.

For reliability, a **service-level objective (SLO)** is a target for a customer-relevant
measure, such as the share of successful operations over a defined period. An **error budget**
represents the failures permitted by that target. An agreed policy can direct effort toward reliability
when the budget is exhausted. Google's
[example error-budget policy](https://sre.google/workbook/error-budget-policy/)
illustrates this mechanism; adapt its thresholds. Security obligations and data correctness
are not risks to spend through an availability error budget.

Not every bug outranks every feature. A cosmetic defect may wait; recurring failures that
break important workflows may not. Depending on severity and capacity, remediation might
interrupt feature work, narrow a launch, or run in parallel.

**The goal is an appropriate trust bar, not an endless pursuit of perfection before innovation.**

## 3. Treat verified adoption blockers as multipliers

A missing capability can block access to everything already built. Removing it may matter
more than adding value for existing users.

I distinguish three situations:

- **Adoption blocker:** the target customer cannot begin meaningful use.
- **Expansion blocker:** the customer can use the product but cannot extend it to the intended scale or workflow.
- **Improvement:** use is possible, but slower, harder, or less satisfying than it should be.

These are situations, not permanent priority levels. Severe friction can matter greatly;
unblocking a segment outside the strategy may have limited value.

Before accepting "we need this to adopt," validate:

- Which specific workflow, policy, or technical requirement prevents adoption?
- Who confirms the requirement, and which other target customers share it?
- Is there an acceptable, secure workaround?
- What else would still prevent deployment, purchase, or expansion?
- What concrete next step will the customer take if the barrier is removed?

Evidence might include failed deployment evaluations, purchasing requirements, or repeated
findings across qualified opportunities. A feature request alone is weaker evidence.

For consumer apps, investigate abandonment during sign-up or the first meaningful task.
Combine usage data, interviews, and usability tests: drop-offs do not explain why people leave.
Check device, accessibility, and connection constraints before proposing features.

Removing one blocker is **necessary, not necessarily sufficient**, for adoption. Pricing,
procurement, migration effort, or another missing capability may still stand in the way.
Do not count the full value of a prospective contract as guaranteed revenue from one feature,
or attribute the same deal independently to every prerequisite.

## 4. For enterprise products, operability is part of the product

An enterprise does not buy only a user experience. It must also be able to secure, govern,
integrate, deploy, and operate the product.

These can be the verified adoption blockers from Section 3. Plan them as product work, not
as miscellaneous requests addressed only after a sales escalation.

| Readiness dimension | What customers may need | Question to validate |
| --- | --- | --- |
| Identity and access | Single sign-on (SSO), role-based access control (RBAC), workload identities | Can people and applications use the product with appropriate permissions? |
| Network and data protection | Private connectivity, traffic controls, encryption, residency options | Can this deployment satisfy the customer's actual security and data policies? |
| Governance | Audit logs, administrative policies, retention controls | Can administrators understand and control how the product is used? |
| Delivery and integration, including CI/CD | Supported APIs, automated testing, environment promotion, infrastructure as code | Can the product fit the customer's change-management workflow? |
| Reliability and recovery | Monitoring, diagnostics, tested recovery procedures | Can the customer operate and recover the intended workload? |
| Scale and cost | Capacity limits, workload isolation, usage and cost visibility | Can the customer grow usage predictably without unacceptable interference or cost? |
{: .system-design-table }

**CI/CD** means continuous integration and continuous delivery: automated validation and
repeatable delivery, not necessarily deployment without approval. Supported automation and
safe environment promotion may be adoption requirements, not merely engineering conveniences.

Microsoft's
[security checklist](https://learn.microsoft.com/en-us/azure/well-architected/security/checklist)
and [safe-deployment guidance](https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/safe-deployments)
provide Azure-oriented design guidance, not a universal list of required controls.

Match readiness to the target industry, geography, workload, and customer policy.
Private connectivity does not by itself make a product secure, and one governance feature
does not establish regulatory compliance.

## 5. Use Pareto analysis without surrendering the roadmap

The **Pareto principle**, or 80/20 rule, highlights concentration: a small group of contributors
may account for a large share of an outcome.
[Juran's guide](https://www.juran.com/blog/a-guide-to-the-pareto-principle-80-20-rule-pareto-analysis/)
explains how to identify these "vital few" using observed data.

Perhaps 80% of revenue comes from 20% of customers. **Investigate; do not assume that split.**
Rank accounts by revenue over a defined period, calculate cumulative shares, and compare
segments and time windows. Apply the same analysis to support burden by failure category
or operating cost by workload.

A renewal-critical request from a major account deserves attention. But revenue concentration
is also a business risk, not a reason to give a few customers permanent roadmap control.

I examine five things together: revenue at risk, renewal timing, strategic fit, applicability
to other customers, and lifetime ownership cost. Distinguish observed revenue from forecast
opportunities, and assess how confidently the request is linked to the commercial decision.

A reusable governance capability may protect a major account while serving the broader
segment. A bespoke approval workflow for that account alone might still be justified, but
needs an explicit commercial case, support model, and boundary against product fragmentation.

**Customer count alone can undervalue enterprise needs. Revenue alone can undervalue the
next market you want to serve.** Use both, alongside strategic fit and evidence.

For a consumer subscription product, compare free and paying users, new and returning users,
and device groups. High spenders are not necessarily representative of the intended audience.
Free users may become subscribers or contribute value to others. Validate those effects;
do not assume free users are equally valuable or worthless.

## 6. Use scores within an investment strategy, not instead of one

Once required work and strategic context are clear, scoring can help compare discretionary
opportunities. I use it to expose assumptions, not to manufacture certainty.

### Use RICE for comparable opportunities

[Intercom's RICE framework](https://www.intercom.com/blog/rice-simple-prioritization-for-product-managers)
combines four inputs:

- **Reach:** affected customers or events within a defined period.
- **Impact:** expected benefit per affected customer or event.
- **Confidence:** how strongly evidence supports the estimates.
- **Effort:** estimated team time required.

**RICE = (Reach x Impact x Confidence) / Effort**

Use consistent reach units and time windows, an impact scale tied to the same outcome,
and evidence behind confidence estimates. A confidence score is not a calibrated probability
that a revenue forecast will come true. Intercom also explicitly recognizes that dependencies
and customer prerequisites can justify working out of score order.

Avoid one formula for everything. A short-term activation experiment and a multi-year
platform investment have different horizons and evidence. Discuss how much capacity should
go toward adoption, innovation, product trust, platform health, and learning. **There is no
universal allocation percentage.** Required remediation must not be capped by a convenient
portfolio quota.

### Account for value, full cost, and timing

Compare **marginal value**: what the next investment adds after costs, over the same horizon.
Revenue is not equivalent to the same amount of cost savings: serving it also costs money.
Make ongoing costs and uncertainty explicit.

Count design, development, integration, testing, documentation, support, operations,
maintenance, and eventual migration or retirement. "Two days to build" does not mean two days
to own.

Translate technical debt into consequences: customer failures, cost per successful workload,
recovery effort, or slower delivery of strategic work. Conversely, do not fund a refactor
solely because the architecture could be cleaner.

**Cost of delay** is the benefit lost or extra cost incurred by waiting. A renewal window can
make an investment time-critical even when another has greater total value. Check feasible
delivery dates first: urgency does not make an impossible deadline achievable. See
[SAFe's sequencing guidance](https://framework.scaledagile.com/wsjf/) for deeper treatment.

Sequence dependencies explicitly. The highest-value feature might need a lower-visibility
foundation first. Sometimes the better investment is simplifying or retiring a costly
capability, with impact analysis, a supported alternative, and a credible migration path.

## 7. Apply the decisions to enterprise and consumer products

### Enterprise: adoption versus a time-critical renewal

An enterprise analytics product aims to move qualified pilots into
production. Customer-impacting job failures are breaching an agreed reliability threshold,
and multiple qualified pilots have verified private-connectivity requirements.

Assume capacity for two scoped investments this cycle. Engineering has sized a reliability
fix and a private-connectivity slice, including dependencies, testing, and operational
readiness. Other access, governance, and deployment controls are adequate for these pilots.

| Candidate | Reasoning in this context | Initial decision |
| --- | --- | --- |
| Address recurring job failures | The current trust bar is breached; adding capabilities does not repair unreliable workflows | Fund the scoped remediation |
| Enable required private connectivity | A verified barrier blocks the target pilots from production | Fund the validated adoption slice |
| Add an AI-assisted analysis feature | Potential differentiation, but evidence does not yet show it advances this cycle's outcome | Defer implementation; identify the assumption to test |
| Add a bespoke integration for a major account | Commercial importance is plausible, but renewal dependence and broader applicability are unclear | Validate before committing |
| Improve infrastructure efficiency | Potential cost reduction; urgency and savings need workload evidence | Revisit with a measured business case |
{: .system-design-table }

**Then the evidence changes.** Validation shows the integration is renewal-critical,
deliverable before the deadline, and fits the second slot. After costs and uncertainty over
the same horizon, its expected incremental benefit exceeds the value lost by delaying pilots,
whose plans can wait one cycle.

Keep the reliability fix, replace connectivity with the integration, and delay the pilots one
cycle. Agree this retention exception with the decision owner: it delays the adoption goal.

Budget discovery too; a "quick win" is not a free third initiative. If the deadline is
infeasible, investigate smaller scope or an acceptable alternative rather than promising
to rescue the renewal. Reassess if reliability meets the agreed bar or connectivity does
not unlock the pilots.

### Consumer: first value versus more engagement

A reading app wants more new readers to complete a first reading
session and return the following week. Assume the team has capacity for a scoped crash fix
and one bounded experiment. Crash reports show an agreed reliability threshold is breached
on supported low-memory phones; usability tests suggest mandatory interest selection prevents
some readers from reaching an article.

| Candidate | Decision under these assumptions |
| --- | --- |
| Fix crashes on affected phones | Fund the remediation; more content does not repair a broken reading experience |
| Let readers skip interest selection | Test whether this improves first-session completion without hurting next-week return |
| Add reading streaks and more notifications | Defer implementation; evidence has not established that reminders address the underlying problem |
{: .system-design-table }

Test the onboarding change against the current flow in a randomized experiment where practical.
Define the target improvement and evaluation window before launch. Check results
by device group, with crash rates, privacy choices, and notification opt-outs as guardrails.
More opens or time in the app alone would not demonstrate reader value.

If completion improves but return weakens, investigate content relevance before declaring
success. If onboarding already works, better discovery or useful reminders may deserve
priority. Neither consumer growth nor enterprise adoption automatically outranks trust or
retention.

## 8. Make the decision durable, then close the loop

Product brings problems and value hypotheses; engineering brings scope, dependencies, and
lifecycle cost. Security, operations, and compliance owners validate risks and obligations;
sales and customer success bring commercial evidence. Agree final decision authority and
how disagreements escalate.

Use this lightweight **decision record** for each substantial commitment:

- **Outcome and target segment:** What change are we trying to create, and for whom?
- **Problem and evidence:** What is observed, estimated, or still assumed?
- **Risk and timing:** What requires action, who validates it, and by when?
- **Options and investment:** What alternatives, dependencies, and full ownership costs were considered?
- **Decision and owner:** What is funded, and who is accountable?
- **Opportunity cost:** What will wait, and why?
- **Success and guardrails:** What baseline, target, customer group, evaluation window, and guardrails will we use?
- **Review trigger:** Which date or new evidence would justify reconsideration?

A stakeholder response can be specific without being dismissive:

> "We're keeping the reliability fix and choosing the validated, renewal-critical integration
> over connectivity. With the decision owner's agreement, pilots move one cycle later. We'll
> revisit if the delivery forecast or pilot timing changes."

After delivery, check outcomes, not only completion. Did affected customers experience fewer
failures? Did eligible pilots reach production? Did cost per successful workload fall without
increasing failures or breaking compatibility?
Compare against the agreed baseline and account for changes in customer or workload mix;
a before-and-after improvement alone does not establish causation.

For defining those outcomes and guardrails before delivery, see
[Measuring Product and Feature Success]({% post_url 2026-11-25-product-success-metrics %}).

Review new evidence at an agreed cadence. Severe incidents or time-critical obligations may
warrant immediate intervention; louder requests usually do not. Reprioritization creates
interruption and unfinished work.

For the delivery side of this loop, see
[Agile and Scrum for Product Managers]({% post_url 2026-11-22-agile-scrum-execution-product-managers %}).

## The question to take into your next planning meeting

Instead of asking only "What should we build next?", ask:

**"What most prevents our target customers from realizing value, and what are we willing to
delay to address it?"**

Sometimes the answer is a new capability. Sometimes it is reliability, security, enterprise
readiness, or a simpler product. Good prioritization makes that choice explainable, funds
it realistically, and checks whether it worked.

## References and further reading

Start with outcome framing and concentration, then use the operational guidance and scoring
framework to deepen the decisions relevant to your product.

1. **[Teresa Torres / Product Talk: Opportunity Solution Trees](https://www.producttalk.org/opportunity-solution-trees/).**
   Connects business outcomes, customer needs, solutions, and assumption tests. Useful before
   turning feature requests into investment proposals.
2. **[Juran Institute: Pareto Principle and Pareto Analysis](https://www.juran.com/blog/a-guide-to-the-pareto-principle-80-20-rule-pareto-analysis/).**
   Explains concentration and ranked contribution analysis. Use your own revenue or problem
   data rather than assuming an exact 80/20 split.
3. **[NIST: Cybersecurity Framework 2.0 and Organizational Profiles](https://www.nist.gov/cyberframework).**
   The [profile resources](https://www.nist.gov/cyberframework/profiles) support comparison of
   current and target security outcomes. They inform risk planning, not a feature-score waiver.
4. **[Google SRE Workbook: Example Error Budget Policy](https://sre.google/workbook/error-budget-policy/).**
   Shows how reliability evidence can redirect work toward remediation. Adapt the policy to
   your service and customers; do not copy its example thresholds blindly.
5. **[Microsoft Azure Well-Architected: Security Checklist](https://learn.microsoft.com/en-us/azure/well-architected/security/checklist) and [Safe Deployment Practices](https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/safe-deployments).**
   Concrete guidance on access, networks, protection, and controlled releases. Useful context
   for enterprise readiness, not a universal procurement checklist.
6. **[Sean McBride / Intercom: RICE Prioritization](https://www.intercom.com/blog/rice-simple-prioritization-for-product-managers).**
   Defines reach, impact, confidence, and effort, including reasons to work out of score order.
   Use it for transparent comparisons within an explicit investment strategy.
7. **[SAFe: Weighted Shortest Job First](https://framework.scaledagile.com/wsjf/).**
   Optional depth on sequencing using cost of delay and job duration. The timing principle
   is useful without adopting another scoring process.

> *Note: This blog post was written with assistance from AI*
