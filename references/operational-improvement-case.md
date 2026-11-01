# Operational Improvement and Work-in-Process Analysis

## Why this domain differs from earnings analysis

The central question is usually not "which KPI improved?" but **which constraint should be changed without degrading output, service, safety, product mix, or quality?** A bottleneck queue graphic is a location signal, not a causal diagnosis by itself. Many projects can "reduce" WIP merely by reducing release rates while missing customer demand. Such a report is not decision-ready.

## Mandatory evidence model

- **Flow boundary:** exact first/last stages, product families, comparable good units, reporting horizon, transfer and scrap conventions.
- **Conservation:** starting WIP + releases - good completions - explicitly measured shrinkage/other exits = ending WIP. Reconcile the process WIP snapshots and age bands to the end total.
- **Rate vs stock:** distinguish units/day (flow) from units (stock), and effective capacity (ability) from actual output (realized). Reconcile workload mix and treat the plant's constraint as hypothetical until supported by time logs, capacities and queues.
- **Demand vs output:** track customer demand, finished-goods inventory, delivery deficit and lateness. Reducing WIP at the expense of service is not a success.
- **Age and variability:** aggregate queue tails separately from stock totals. Capture line breakdowns, batch compatibility, changeovers, quality holds, exceptions, and recipes. Do not confuse age at a snapshot with measured average throughput time.
- **Economics:** state exact unit valuation basis. WIP book-value reduction is NOT the same as released cash or cost savings. Finished goods and raw materials can rise simultaneously.

## Recommended analysis flow

1. Draw the true material process and overlay stage capacities, location-specific WIP and delivery demand.
2. Identify and rank accumulation by absolute units and share. Show queues of the process, not only averages.
3. Reconcile daily releases, completions and WIP trajectory. Distinguish queue appearance from causal explanation.
4. Test at least two competing causal stories. Example: low effective capacity vs deliberate batching/release imbalance; document which measurements would falsify each.
5. Compare interventions including no-change baseline, release-only, capacity-only and combined. Calculate inventory outcomes separately from customer service, and explicitly mark assumptions for every case.
6. Quantify service guardrails, small-batch / recipe starvation, minimum WIP, quality constraints, and rollback gates before recommending a pilot.
7. End with an evidence-bounded decision. A conditional pilot can be a valid final answer; false certainty cannot.

## Visual pattern selection

- `process_capacity_queue`: stage sequence with capacity and WIP queue marks. Required: stages, same good-unit basis, release and output rates. Avoid falsely presenting nameplate capacity as actual production.
- `wip_stock_flow_bridge`: starting stock plus releases minus completions to ending stock, with exact conservation. Avoid cumulative/average conflation.
- `queue_age_distribution`: per-location queue and aging bins, clearly distinguish age from cycle time.
- `service_feasibility_scenarios`: compare future WIP, completion vs demand, constrained capacity and reversal conditions. Avoid treating deterministic scenario arithmetic as statistically validated forecast.
- `cause_intervention_gate`: causal link with observed evidence, unverified assumptions, counterexample, measurable trigger and rollback.

## Quantitative caution: Little's Law

Average WIP = throughput × average flow time under the applicable stable-flow assumptions. For a growing line, end-of-period WIP ÷ recent daily output is **only a throughput-days snapshot proxy**, not observed order lead time or a reliable causal forecast. A lower release rate by itself cannot guarantee a fixed output level when recipe composition is wrong or the bottleneck becomes starved.

## Dataset provenance and claims

A simulation/fictional dataset must be labeled `synthetic_fictional`. The cover and source/notes page must both say that the factory and data are fictional. Methodology references may be external literature but DO NOT imply the fictional numbers were obtained from those references. Keep all detailed simulation tables and QA logs in producer files.

## Distinct QA classes

Deterministic numeric QA supports reconciliation only. AI visual review checks the **actual** rendered PPTX/PDF. External reader two-second tests are separate and must not be claimed without participants.
