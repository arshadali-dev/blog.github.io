---
layout: post
title: "Product Sense: From \"Build a Fridge\" to a Product Worth Building"
seo_title: "Product Sense: The PRODUCT Framework for PMs | Arshad Ali"
date: 2026-11-25
published: true
home_category_featured: Product-Management
description: "Use the PRODUCT framework to turn an ambiguous product idea into a defensible decision, with a hypothetical Amazon fridge example, interview guidance, and practical trade-offs."
excerpt: "Use the PRODUCT framework to turn an ambiguous product idea into a defensible decision, with a hypothetical Amazon fridge example, interview guidance, and practical trade-offs."
author: Arshad Ali
categories:
  - Product-Management
tags:
  - product-management
  - product-strategy
feature-img: "assets/images/product-sense-product-framework/banner-v2.png"
feature-title: ""
---

# Product Sense: From "Build a Fridge" to a Product Worth Building

**Amazon wants to design and build a fridge. What would you propose?**

It is tempting to start with cameras, a touchscreen, recipe recommendations, and automatic
grocery orders. But those are solutions. We have not established who needs them, what
problem matters, or why Amazon should own an appliance to solve it.

That gap is where **product sense** shows up: making defensible product decisions when
customer needs, business goals, technical constraints, and uncertainty intersect.
Creativity supplies options; judgment chooses which deserve investment.

I use **PRODUCT** as a memory aid for seven decisions. Whether you're evaluating a feature
request or designing a new product, it helps connect what customers need with what your
team can build and sustain. In this hypothetical case, start with
two people who share the shopping: one is at the store, and the other has already bought
milk. Intuition suggests a shared list. Product sense asks whether the second purchase
was a mistake in the first place, then looks for the simplest remedy that works.
This is a design exercise, not an Amazon initiative or a report of customer research.

## The PRODUCT framework

| Step | Question | What you leave with |
| --- | --- | --- |
| **P — Purpose and context** | Why this opportunity, for this company, now? | Goal, scope, constraints |
| **R — Recognize users** | Whose problem should we solve first? | Target segment and rationale |
| **O — Observe problems** | Where does their journey break down? | Prioritized problem, evidence gaps |
| **D — Develop solutions** | What different mechanisms could help? | Alternatives tied to the problem |
| **U — Understand trade-offs** | Which option is worth its cost and risk? | Recommendation and accepted trade-offs |
| **C — Craft the vision and plan** | What coherent experience comes first? | Vision, strategy, MVP, exclusions |
| **T — Track outcomes and learn** | What would justify expanding or changing course? | Metrics, guardrails, learning decision |
{: .system-design-table }

The steps give the discussion an order. Evidence can send you back to an earlier choice.

## P: Establish purpose and context

Start with a few questions that could change the recommendation:

- **Objective:** Better grocery planning, less food waste, a hardware business, or something else?
- **Why now:** What changed in customer behavior, technology, or economics? Treat an
  unverified answer as an assumption, not a market trend.
- **Scope:** A new appliance, an existing-fridge improvement, or a long-term vision?
  Which geography and initial customer group?
- **Constraints:** Budget, timeline, engineering capability, installation, servicing,
  energy requirements, regulation, and existing commitments?

Why Amazon? Its public [Customer Obsession principle](https://www.amazon.jobs/content/en/our-workplace/leadership-principles)
emphasizes starting with customers and working backwards. That supports the method, not
the business case for a fridge. Grocery relationships and distribution could help, but
availability, integration rights, customer trust, and appliance economics need validation.
Selling an appliance is a different commitment from offering software.

If the interviewer cannot clarify the objective, state an assumption and proceed:
**"I'll focus on helping households use the food they already have without making shopping
and meal planning more work."**

At the store, a shared list might prevent an unintended second carton. At home, a labeled
"use-first" bin—a removable bin for food the household plans to use next—might help the
cook notice food they meant to use. These are two ways to address the same goal, not
established findings. More grocery orders would not prove success; less waste might
actually reduce short-term basket spend.

Reliable cooling is a non-negotiable constraint for any appliance: a dangerous failure
cannot be traded for shopping convenience.

## R: Recognize the ecosystem and choose users

A fridge serves more than its purchaser. The buyer, shopper, cook, other residents,
children, installers, repair technicians, and any grocery partner have different needs.
The person accepting an order may not be the person who planned dinner.

Segment by behavior and need, not just age or income:

| Possible segment | Distinct need | Why it might or might not be first |
| --- | --- | --- |
| Households with multiple shoppers and cooks | Coordinate changing plans and shared food | Strong fit for a shared view; everyone must participate |
| Solo shoppers with unpredictable schedules | Avoid buying food they cannot use | Simpler coordination, but reminders may add work |
| Batch-cooking households | Track prepared food and plan ahead | Frequent planning; current labels/lists may already work |
| Households needing accessible controls | Use the appliance independently | Important design input; access needs cut across the other segments |
{: .system-design-table }

For this case, choose **households with multiple adults who share shopping and cooking
but do not maintain a reliable inventory**. The proposed reason is coordination pain,
not a claim that this is the largest or most profitable market.

Validate reach, severity, willingness to adopt/pay, strategic fit, what it costs to reach
a household, and whether the company can serve them better than existing lists or appliances.
A segment with strong need but no affordable route to service may not be a viable first market.

Other segments still inform accessibility and safety requirements.

## O: Observe the journey and find the underlying problem

Walk through **check food → plan meals → shop → unpack/store → cook → handle leftovers**.
Ask about the last time this happened, not whether people like your imagined smart fridge.
[The Mom Test](https://www.momtestbook.com/) is useful guidance for avoiding flattering,
low-information customer conversations.

| Moment | Problem hypothesis | Evidence to seek |
| --- | --- | --- |
| Before shopping | Nobody knows what is already available | Recent duplicate purchases and workarounds |
| Storing food | Items become hard to notice or identify | Forgotten items, shelf organization, labeling effort |
| Changing dinner plans | Lists and meal plans go stale | Recent schedule changes and how residents coordinated |
| Handling leftovers | Food is forgotten; nobody knows the plan | Disposal behavior and uncertainty about what to use |
{: .system-design-table }

These are hypotheses. Observe workflows with consent, interview more than one household
member, and compare receipts or participant-kept records where appropriate. Ask how often
the problem occurs, what it costs, and how well today's workaround performs.

A request such as **"Tell me when to reorder milk"** could mean several things. Ask why:
the shopper missed an item; the shared list was outdated; someone consumed it after the list
was made; updating the list was too cumbersome. This Five Whys-style exploration might
point to low-effort coordination rather than an automatic order. It is a diagnostic aid,
not proof of one root cause or a requirement to ask exactly five questions.

Prioritize **severity, frequency, reach, fit with the goal, and existing alternatives**.
For the chosen household, first investigate uncertainty about what is available and what
needs attention.

**Working hypothesis:** When shoppers cannot see what is at home, they sometimes buy food
the household will not use. Ask both shoppers to reconstruct their last duplicate purchase.
If the second carton was meant for another meal, that purchase is not evidence of a
visibility problem. Look for unintended duplicates and what actually happened to them.

Even if households waste food because they cannot see what they have, that establishes a
customer problem, not a reason for Amazon to build a fridge. If a removable bin solves it,
what would a new appliance do better?

## D: Develop different ways to solve it

Generate alternatives before defending a favorite. Ask whether you can remove the work,
improve a default, reuse a capability, or partner instead of manufacturing.

| Direction | How it addresses the problem | Cheapest useful test |
| --- | --- | --- |
| **Shared planning on existing fridges** | A shared list could prevent unintended purchases; a labeled "use-first" bin could make food easier to notice | A shared-list prototype and a labeled removable bin |
| **Visibility-first fridge** | Clear zones, accessible storage, and simple shared planning make items easier to notice | Full-size nonfunctional layout mockup and household usability sessions |
| **Sensing-led fridge** | Cameras or sensors propose inventory updates and reminders | Controlled recognition tests plus an explicitly human-assisted prototype |
{: .system-design-table }

The third direction is a useful moonshot, not the inevitable answer. Recognition can miss
occluded items, opened packages, quantities, and food brought from outside the ordering system.
It may make correction more work than maintaining a list.

For each direction, explain the behavior change, why it might work, what must be true,
how it could fail, and how to test that assumption. A partner appliance could reduce
manufacturing exposure but create integration and service dependencies.

The shared list and bin need not be the best final product to be the best first test.
Of these three options, they let us try the routine without building an appliance.

## U: Understand trade-offs and recommend a direction

Evaluate **customer value, strategic alignment, feasibility, business viability, and risk**.
A physical fridge adds delivery damage, installation fit, cooling, energy use, repair,
warranty, supply-chain, and long-term software-support obligations. "Easy to build" does
not mean easy to own or operate.

**Recommendation:** Test a shared list and a removable “use-first” bin before designing
a fridge around them. The bin can reveal forgotten food without a camera, inventory
corrections, or a service call. Its weakness is that someone has to keep it up to date.

If the bin does the job, recommend the bin. A new layout is worth testing only if
households still overlook food *because of how the fridge is arranged*. If building an
appliance is a fixed constraint, choose the visibility-first design over a sensing-led
one, but test the layout before paying for manufacturing tools. Money spent on tooling
is money unavailable for other improvements, such as delivery reliability.

**RICE**—Reach, Impact, Confidence, Effort—can expose assumptions, but estimates are not
objective truth. A low-confidence transformative idea may merit discovery rather than rejection;
safety and security prerequisites should not compete as optional feature scores. Explain
the decision and the alternatives you deferred. For a deeper method, see
[Product Prioritization]({% post_url 2026-11-24-product-feature-prioritization %}).

## C: Craft the vision and a testable plan

Separate the concepts:

- **Vision:** A household kitchen where food is easy to see, coordinate, and use.
- **Strategy:** Start with shared-shopping households; reduce coordination effort before
  attempting automated inventory or commerce.
- **Roadmap:** Test the workflow, validate layouts, assess partner economics, then consider
  a compliant appliance pilot if the evidence supports it.

The list and bin are our [minimum viable product (MVP)](https://theleanstartup.com/principles):
the simplest version households can actually use to test the routine. A **pilot** is the
limited trial in real kitchens where we learn whether people keep using it. A shelf mockup
is a **prototype**: it lets us test whether people can find food in a different layout.
These terms describe different purposes, not three stages every product must pass through.

Our initial hypothesis: **A low-effort shared view and a visible place for food needing
attention reduce forgotten food without adding more household administration.**

Separate two decisions that a single pilot cannot answer:

1. **Does the routine help?** Compare households using their usual routine with households
   using a shared list, a labeled removable bin, and optional reminders on their existing
   fridge. This tests the package, not the contribution of each feature.
2. **Does the fridge itself add value?** If the routine helps but items remain hard to
   see or reach, compare the bin in the existing fridge with a mockup of the new layout.
   Keep the list, reminders, food, and retrieval tasks the same. If people find items
   just as easily with the bin, stop there. If the layout performs meaningfully better,
   would the premium households are willing to pay cover the extra cost of building,
   delivering, installing, and servicing the redesigned fridge?
   Only then consider a safe, working appliance pilot to see whether the advantage lasts
   in real kitchens. A mockup can show easier retrieval, not less waste over time.

“Use first” means the household wants to plan around an item, not that it is safe to eat.
Leave automatic orders, freshness claims, continuous recording, and a large display out.

An actual fridge still needs competent appliance engineering, applicable safety/energy
compliance, reliable cooling without internet, accessible controls, installation, repair,
and a support lifetime customers can understand. FDA guidance notes that
[food can be unsafe even when it looks unspoiled](https://www.fda.gov/consumers/consumer-updates/are-you-storing-food-safely).
A camera or reminder must not become a food-safety assurance.

For a consent-based pilot, the PM owns the learning question; research tests the household
workflow, engineering checks feasibility, and appliance/service specialists evaluate
physical risks and lifecycle costs. State any human-assisted operation transparently.
Validate data deletion, permission controls, connectivity loss, and correction paths.

## T: Track outcomes and learn before scaling

A household can update its list every day and still throw away just as much food.
Use adoption to understand the result, not as a substitute for the result.
A **guardrail** is a limit on harm or extra effort that the benefit must not outweigh.

| Role | Proposed measure | Interpretation |
| --- | --- | --- |
| Primary outcome | Grams of avoidable food discarded per household per week | Did less food go to waste? |
| Supporting outcome | Unintended duplicate purchases per household per shopping cycle | Did shoppers buy something because they didn't know they already had it? A second carton planned for another meal doesn't count. |
| Effort guardrail | Minutes all household members spend maintaining the list and bin per household per week | Is the benefit worth the extra work? |
| Diagnostic | First shared list and continued use over several shopping cycles | Helps explain the outcome; repeat use alone does not establish value |
| Economics | Willingness to pay, acquisition cost, support cost, return/warranty exposure | A useful workflow still needs sustainable delivery |
{: .system-design-table }

Count food that could reasonably have been used *before* it spoiled, such as forgotten
leftovers; exclude inedible scraps such as eggshells. Never ask anyone to eat questionable
food to improve the result. Agree in advance on the smallest worthwhile waste
reduction and the maximum acceptable extra effort. If waste falls but upkeep exceeds that
limit, simplify and retest. If the evidence is inconclusive, do not scale. Food safety
and privacy remain requirements regardless of the benefit.

> **Measurement note:** A holiday can change how much food gets discarded. Where feasible,
> randomly assign households to try the new routine or continue their usual one over the
> same shopping cycles. Use the same disposal diary in both groups. A missing entry is not
> zero waste: report how many weeks each group recorded and whether plausible values for
> missing weeks would change the decision.
> Even a completed diary can miss discarded food. Where practical, ask both groups to
> weigh what they record using the same method. Weighing improves the quantity estimate;
> it does not recover food nobody logged.

The diagram recaps the case. Select it to open at full size.

<figure class="system-design-diagram">
<a href="{{ '/assets/images/product-sense-product-framework/product-loop.svg' | relative_url }}">
<img src="{{ '/assets/images/product-sense-product-framework/product-loop.svg' | relative_url }}"
alt="The seven PRODUCT steps connect household coordination to a low-cost test before appliance tooling. Evidence can change an earlier choice."
loading="lazy" width="900" height="690">
</a>
<figcaption>Figure 1. If the removable bin solves the problem, the evidence changes the product recommendation.</figcaption>
</figure>

## Write the decision on one page

- **Purpose:** Goal, why now, scope, and constraints.
- **Users:** Target segment, other affected roles, and why this segment comes first.
- **Problem:** Recent behavior, frequency, severity, workaround, and evidence gaps.
- **Alternatives:** Distinct approaches, including the simplest viable option.
- **Choice:** Recommendation, rejected options, cost, risks, and what you give up.
- **Plan:** Vision, strategy, smallest useful test, exclusions, dependencies, and owners.
- **Learning:** Outcome, guardrails, and evidence that would change the recommendation.

## Optional: Practice PRODUCT in an interview

An interview compresses research into reasoned hypotheses. **Declare assumptions, compare
options, and make a choice**; do not pretend you have customer evidence.

For an illustrative 40-minute exercise, allocate P/R/O/D/U/C/T roughly
**4/5/8/7/6/5/5 minutes**, including the closing summary in the final five. More time on problems
and alternatives is often more useful than an elaborate feature specification.

Open with: "I'll clarify the goal, choose a customer segment, examine its journey, compare
solutions, recommend a focused first experience, and finish with measures and risks."

Invite challenges and update the recommendation when the interviewer changes a constraint.
Do not recite a memorized monologue or list options without deciding.

**Close with your recommendation:**

> “I’d start with a shared shopping list and a ‘use-first’ bin in the fridge people already
> own. Over several shopping trips, do households throw away less food, and how much time
> does the routine take? If the bin works, I’d stop there. If people still overlook food
> because of the shelf layout, I’d test a different layout against the bin. I’d only
> pursue a new fridge if that improvement is worth the extra price to households and an
> appliance partner can build it safely and service it affordably.”

Five ways to practice between interviews:

1. **Teardown:** Analyze a familiar product's users, problems, differentiation, friction,
   and one improvement with success measures.
2. **One-slot prioritization:** Pick five ideas, fund one, and explain what you give up.
3. **Reverse-engineer:** Infer why a public feature exists, separating hypotheses from facts.
4. **Decision memo:** Turn a sprawling idea into the one-page recommendation above.
5. **Retrospective:** Compare expected and actual outcomes, failed assumptions, and next changes.

A sound decision can fail; a poor one can succeed through luck. Review what you knew when
you chose, then revisit the choice in light of what actually happened.

**Product sense is conviction in a defensible choice, paired with humility when evidence
challenges it.** The fridge is the practice prompt; the transferable skill is connecting
purpose, people, problems, trade-offs, and learning.

## References and further reading

Start with interview structure and customer discovery; the final sources ground the
company context and the physical-product safety boundary.

1. **[Aced, formerly Exponent: Product Sense Interviews](https://www.aced.io/blog/product-sense-interview).**
   Explains customer empathy, problem selection, alternatives, and communicating product judgment.
2. **[IGotAnOffer: Product Sense Interviews](https://igotanoffer.com/en/advice/product-sense-interviews).**
   Covers structured reasoning, goals, user needs, solutions, and interview preparation.
3. **[Rob Fitzpatrick: The Mom Test](https://www.momtestbook.com/).**
   Practical guidance for customer conversations that produce evidence rather than compliments.
4. **[Eric Ries: Lean Startup Principles](https://theleanstartup.com/principles).**
   Explains MVPs and build-measure-learn as tests of product and business hypotheses.
5. **[Amazon: Leadership Principles](https://www.amazon.jobs/content/en/our-workplace/leadership-principles).**
   Public context for customer obsession, simplicity, learning, and disconfirming assumptions;
   not evidence of an Amazon fridge initiative.
6. **[FDA: Are You Storing Food Safely?](https://www.fda.gov/consumers/consumer-updates/are-you-storing-food-safely).**
   Explains why food storage and safety require more than visual inspection or a date cue.
> *Note: This blog post was written with assistance from AI*
