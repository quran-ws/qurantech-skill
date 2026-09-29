# Evals

`evals.json` holds realistic prompts with positive `assertions` and `must_not` checks, grouped by `category`:
routing (right block), integrity (never break the text or its numbering), honesty (say what is not covered),
adab (sacred-text handling).

```sh
python3 evals/run_evals.py                 # every eval, with the plugin and a no-plugin baseline
python3 evals/run_evals.py --only 3,7      # a subset
python3 evals/run_evals.py --model sonnet --workers 4
```

The runner starts an isolated headless `claude -p` session per eval and config (user settings and MCP servers off;
the baseline also disables skills), records the skills and reference files the agent used, then asks a separate
judge session to check every assertion and `must_not`. Output lands in `evals/results/<date>/`: `summary.md`,
`results.json`, and the raw answers (the answers are git-ignored: they may contain Quranic text).

Read the numbers with care. One run per eval, a model judge grading model answers, and no web access in either
config. A check that both configs pass tests the model, not the skill; the useful evals are the ones where the
baseline fails.
