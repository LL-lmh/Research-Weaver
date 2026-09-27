# Paper-type adaptation

Classify the paper only when type changes what counts as decisive evidence. A paper may combine types; state the dominant type and apply secondary checks selectively.

| Type | Emphasize | Question |
|---|---|---|
| method/model | mechanism, ablation, baseline fairness, compute/data | Which component causes the gain? |
| dataset/benchmark | construction, coverage, leakage, annotation, license | What population and use does it validly represent? |
| empirical/observational | sampling, variables, identification, uncertainty | Is the claim associative or causal? |
| experiment/RCT | intervention, control, randomization, attrition, effect size | What does the design identify? |
| theoretical | assumptions, definitions, proof steps, counterexamples | Where does the result cease to hold? |
| system/tool | architecture, workload, latency/cost, failure modes | Does evaluation match deployment conditions? |
| review/meta-analysis | search protocol, inclusion, synthesis, heterogeneity | What evidence may selection exclude? |

Do not force model-paper headings onto theoretical or qualitative work. Preserve the common note architecture, but rename local subheadings and replace “experiment” with the relevant evidence form. The research-translation chain still needs a testable check: counterexample, sensitivity analysis, replication, alternative coding, or deployment probe.
