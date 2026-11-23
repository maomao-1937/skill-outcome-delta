# skill-outcome-delta

Compare paired baseline and with-skill task records. The report includes success-rate changes plus median token and duration deltas, paired by the same case ID.

## Who it helps

Agent developers deciding whether a skill improves task outcomes enough to justify its token and latency cost. Unpaired averages can be misleading when the two conditions contain different tasks.

## Install and run

Python 3.10+; standard library only. Each run record has `case_id`, `condition` (`baseline` or `with_skill`), boolean `success`, integer `tokens`, and `duration_ms`.

```console
python skill_outcome_delta.py examples/runs.json
```

Output is JSON. Exit `0` means all cases have both conditions; exit `1` reports one or more unpaired cases; malformed input or no usable pair exits `2`. Repeated runs are reduced to per-case success rate and median cost before paired deltas are summarized.

## Difference and limits

This is an offline comparator for results produced elsewhere. It does not run agents, grade output quality, prove causality, or establish that two runs used identical model settings. The `success` label and run capture must be supplied consistently. No copied upstream implementation or assets; MIT license.

## Evidence

The [official skill-evaluation guide](https://github.com/agentskills/agentskills/blob/main/docs/skill-creation/evaluating-skills.mdx) describes paired with-skill/baseline cases and recording outcome quality, token count, and duration. The project turns those records into a reproducible local comparison.

## Test

```console
python -m unittest discover -s tests -v
python examples/run_examples.py
```
