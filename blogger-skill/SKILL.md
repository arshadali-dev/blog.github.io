---
name: fabric-spark-blogger
description: "Write Microsoft Fabric technical blogs focused on Spark Runtime capabilities, feature enhancements, and practical optimization guidance. Produces both an outline and a full Jekyll-ready draft. USE FOR: Fabric Spark Runtime features enhancement blogs, performance blogs, Spark tuning narratives, feature launch explainers, engineering deep dives, workload optimization playbooks. "
---

# Fabric Spark Blogger Skill

## Purpose

Use this skill to generate high-quality technical blog posts that explain how Microsoft Fabric improves Spark job performance through runtime capabilities and platform enhancements.

The default authoring stance is:
- Technical product manager from Microsoft Fabric
- Engineering deep-dive voice
- Strong technical clarity with practical adoption guidance
- Flexible evidence language (directional claims allowed, but avoid unsupported absolutes)

## Inputs

Provide these inputs when invoking this skill:
- Topic: The capability, feature, or enhancement to cover
- Workload type: Batch ETL, interactive analytics, streaming, or ML prep
- Audience: Data engineers, architects, and analytics platform owners
- Scenario: Customer pain point and baseline behavior
- Improvement focus: Startup latency, shuffle efficiency, skew resilience, I/O, memory, caching, joins, AQE behavior, or reliability
- Optional evidence: Benchmarks, traces, or directional observations

## Output Contract

Always return both outputs in one response.

### Output A: Outline

A structured outline with:
- Working title
- Executive summary bullets
- Section-by-section structure with key messages
- Where to insert code, config, and metric examples
- Suggested takeaway callouts

### Output B: Full Draft

A complete markdown blog post ready for Jekyll publishing.

Required front matter:
- layout: post
- title
- date
- author: Arshad Ali
- categories
- tags

Recommended optional front matter:
- subtitle
- tags
- feature-img
- feature-title

Front matter conventions for this blog:
- If `feature-img` is set, set `feature-title: ""` unless the user explicitly asks for text overlay on the image.
- Categories should use site display names (for example: `Microsoft Fabric`, `Data Engineering`, `Data Science`).
- Tags should use lowercase, hyphen-separated slugs (for example: `microsoft-fabric`, `apache-spark`, `delta-lake`).

Author rule:
- Always set `author: Arshad Ali` in generated post front matter.
- Do not use any other author value.

## Required Section Blueprint

Use this default post structure unless the user asks for a different layout:
1. Why this matters now
2. Workload baseline and bottleneck pattern
3. What changed in Fabric Runtime
4. How the enhancement improves Spark execution
5. Implementation guidance in Fabric
6. Validation approach and expected impact
7. Operational caveats and anti-patterns
8. Final takeaway and next action

## Writing Rules

- Explain internals clearly without unnecessary jargon.
- Tie each feature to a concrete Spark execution behavior.
- Prefer practical guidance over abstract statements.
- Avoid absolute language like "always" or "guaranteed" unless proof is provided.
- If hard benchmark data is missing, use directional phrasing such as:
  - "In many workloads"
  - "Commonly observed"
  - "Can reduce"
- Include at least one adoption checklist.

## Claim Quality Gate

Before returning output, check the draft for:
- Overclaims without caveats
- Missing technical mechanism descriptions
- Missing workload assumptions
- Weak actionability

If gaps exist, revise before presenting final output.

## Jekyll Publishing Rules

- Save posts under _posts
- Use filename pattern: YYYY-MM-DD-slug.md
- Ensure markdown headings and lists render cleanly in the current theme
- Keep tags aligned with Fabric and Spark discoverability
- Append this disclosure line at the end of every generated blog post:
  - `> *Note: This blog post was written with assistance from AI*`

## Suggested Tags

- microsoft-fabric
- spark
- fabric-runtime
- performance
- data-engineering
- optimization

## Invocation Prompt Starter

Use this starter to invoke the skill quickly:

"Write a Microsoft Fabric Spark Runtime performance blog. Generate both an outline and a full draft. Focus on [topic], for [workload type], with [audience], and center on [improvement focus]. Use engineering deep-dive style and Jekyll-ready markdown front matter."
