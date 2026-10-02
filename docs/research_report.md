# VMAR-PS Historical Research Report

## Research identity

**VMAR-PS — Verified Multi-Agent ReAct for Iterative Program Synthesis**

This report reconstructs the empirical history of the repository using committed execution artifacts, source code, configuration files, and historical audit documents. It intentionally separates measured execution evidence from planned experiments and documentation.

> **Core research question:** Does combining multiple independently configured agents, ReAct-style iteration, execution feedback, and iterative refinement improve executable program-synthesis reliability under the tested conditions?

The repository does **not** contain enough valid historical evidence to answer that question causally. The useful result is a precise reconstruction of what was actually executed, what the measurements can support, and why later hardening was necessary.

---

## 1. Evidence classification

| Artifact | What it establishes | Evidence class |
|---|---|---|
| `results2.json` | 24 recorded solutions, 24 recorded iterations, raw generated code, sandbox result fields, and per-attempt execution times | **RAW EXECUTION EVIDENCE** |
| `react_docker.py` at commit `f8b8ed0` | The historical control flow: one model call per iteration, ReAct prompts, up to 3 iterations, first process-level success selected | **HISTORICAL/EXPLORATORY** |
| `sandbox.py` at commit `f8b8ed0` | The historical subprocess protocol that delayed stdin delivery until after process polling | **HISTORICAL/EXPLORATORY** |
| `problem_example.txt` and `config.json.example` | The factorial task and the intended example test cases | **DOCUMENTATION ONLY** |
| `RESULTS.md` and `RESEARCH_AUDIT.md` on `research-hardening` | Explicit later audit of the historical protocol and the statement that no corrected controlled experiment was executed | **HISTORICAL/EXPLORATORY + DOCUMENTATION ONLY** |
| `configs/*.yaml`, current `src/vmar_ps/`, and current experiment runner | The later hardened framework and its planned baselines/controls | **DOCUMENTATION ONLY** for empirical claims |
| `results/.gitkeep` | No committed machine-readable output from the new hardened runner | **DOCUMENTATION ONLY / NEGATIVE EVIDENCE** |

The report never treats a README sentence or a planned configuration as a measured result.

---

## 2. Historical experiments actually executed

### Experiment H-001 — Legacy 24-agent ReAct factorial prototype

**Repository evidence:** present in `results2.json` and the original implementation at commit `f8b8ed0` (November 9, 2025).

The execution artifact contains:

- **1 benchmark problem:** factorial from stdin.
- **24 recorded agents/candidates.**
- **24 recorded iterations:** every recorded solution contains one iteration.
- **ReAct-style generation:** the historical code constructs an initial ReAct prompt and then has a refinement path for later iterations.
- **Maximum refinement:** 3 iterations were allowed by the historical loop.
- **Observed refinement:** 0 revisions were actually recorded; every candidate stopped after its first iteration because the legacy process-level success flag was treated as sufficient.
- **Selection:** first candidate whose legacy `sandbox_result.success` was true; otherwise last attempt.
- **Execution feedback:** execution result/error was available to the refinement prompt, but only the **first declared test case** was executed inside the ReAct loop.
- **Execution mode:** the program attempted Docker first and otherwise fell back to subprocess. The raw result file does not record which mode was actually used for this run.
- **Model/provider:** the raw result file does not record the model or provider used per attempt. The committed example configuration mentions Google Gemini models, but that example is not evidence of the actual historical runtime configuration.
- **Model calls:** 24 model-generation attempts are supported by the raw trace structure (one generation per recorded iteration/candidate). The file does not contain a direct call-counter field.
- **Tokens/cost:** not recorded.
- **Run-level wall clock:** not recorded. Only per-attempt sandbox execution times are present.

### Were any later experiments executed?

No committed raw result artifact was found for the later controlled six-task Direct-vs-ReAct benchmark on `research-hardening`. That branch explicitly records:

> “No new controlled experiment has been executed in this branch.”

The newer VMAR-PS framework defines Single-pass, Single-agent ReAct, Multi-agent, Verified multi-agent, and VMAR-PS configurations, but the current repository contains no corresponding executed result set. Those conditions are therefore **planned/implemented interfaces, not historical measurements**.

---

## 3. Reconstruction of H-001

### Setup

| Field | Reconstructed value | Confidence |
|---|---|---|
| Experiment ID | H-001, retrospective label | High |
| Repository version | `f8b8ed0e1d00578c6008ab0e43f9fe4457cb847` | High |
| Repository commit date | 2025-11-09 | High |
| Actual execution timestamp | Not recorded | High |
| Benchmark | One factorial program-synthesis task | High |
| Agents | 24 recorded candidates | High |
| Agent profiles | Not recoverable from committed artifacts | High |
| ReAct | Enabled in historical code | High |
| Max refinement rounds | 3 | High |
| Observed refinement rounds | 0 | High |
| Execution feedback | Yes, but only first test case | High |
| Selection | First legacy process-level success | High |
| Execution mode | Docker-first / subprocess fallback; actual mode unknown | High |
| Model/provider | Unknown from raw artifact | High |
| Model-call budget | No explicit fixed budget | High |
| Tokens/cost | Not recorded | High |

### What the raw file actually recorded

| Metric | Raw value | Interpretation |
|---|---:|---|
| Recorded solutions | 24 | Directly stored |
| Recorded iterations | 24 | Directly stored |
| Legacy `success=true` | 24/24 | **Invalid as a correctness metric** |
| Per-attempt execution time, mean | 21.31 s | Historical sandbox timing only |
| Per-attempt execution time, sum | 511.51 s | Sum of 24 recorded attempt timings; not a run wall-clock |
| Per-attempt output | Empty for all 24 | Directly stored |
| Token/cost data | Missing | Cannot recover |

The mean and sum above are recomputed from the 24 raw `execution_time` fields. They are not presented as an overall experiment runtime.

---

## 4. Why the historical success signal is invalid

The later audit on `research-hardening` identified several concrete measurement failures in the original pipeline:

1. **stdin was supplied too late.** The subprocess runner polled the process to completion before providing stdin. Programs using `input()` could therefore stall or time out even when their code was otherwise reasonable.
2. **Only the first test case was used** in the historical ReAct loop, despite multiple cases being declared in the example configuration.
3. **Process-level success was treated as correctness.** A zero/legacy process-success signal is not equivalent to matching expected program output.
4. **The loop stopped on the legacy success flag**, so a falsely successful first attempt prevented later refinement.
5. **API quota failures could become Python source text.** The raw artifact contains four entries where Gemini quota-error text was written into the generated-code field and then reached the Python executor.
6. **The benchmark was only one trivial factorial task.**
7. **There was no one-shot control condition**, so the effect of ReAct, feedback, or multi-agent sampling could not be isolated.

For this reason, the historical `success=true` field is preserved as raw evidence but is **excluded from correctness claims**.

---

## 5. Historical result tables

### 5.1 Method-level result table

| Condition | Agents | Refinement | Tasks | Recorded candidates | Legacy success | Trustworthy solved rate | Model calls | Runtime evidence | Evidence quality |
|---|---:|---:|---:|---:|---:|---|---:|---|---|
| Legacy 24-agent ReAct factorial | 24 | max 3; observed 1 attempt/candidate | 1 | 24 | 24/24 | **Not measurable / excluded** | 24 inferred from raw trace | 21.31 s mean sandbox time per candidate; 511.51 s sum | **RAW EXECUTION EVIDENCE, correctness invalidated** |

The table deliberately does not report a success percentage. The raw artifact does not contain a valid correctness measurement.

### 5.2 Raw failure-pattern table

| Observed pattern in raw artifact | Count | What it means |
|---|---:|---|
| Execution times around 30 s | 17 | Consistent with the broken stdin/termination protocol; cannot be used as evidence that the generated programs were incorrect |
| API quota-error text converted into generated source | 4 | Provider failures were incorrectly represented as candidate code; these records are invalid for correctness |
| Process-level success with empty output | 3 | The legacy process flag says success, but no output was captured; correctness was not demonstrated |
| Entries with SyntaxError text | 4 | These are concrete evidence that the legacy success flag could disagree with actual execution errors |

The four quota-error entries are also among the SyntaxError cases; the categories are therefore overlapping descriptions, not additive independent failure classes.

### 5.3 Historical condition coverage

| Condition defined by later framework | Executed historically? | Evidence |
|---|---|---|
| Single-pass | **No evidence of execution** | No raw result artifact |
| Single-agent ReAct | **No evidence of execution** | No raw result artifact |
| Multi-agent without iteration | **No evidence of execution** | No raw result artifact |
| Multi-agent with verification/selection | **No evidence of execution** | No raw result artifact |
| VMAR-PS | **No evidence of execution** | Current framework is implemented, but no committed result set exists |

These methods remain useful as experimental interfaces, but they must not be presented as historical benchmark results.

---

## 6. Hypotheses and what can actually be learned

### H1 — Multiple agents

**Hypothesis:** independent agents may increase the chance that at least one candidate is executable and correct.

**Historical evidence:** 24 independent candidate records were produced for one task.

**Conclusion from evidence:** insufficient. There is no valid correctness label across those candidates and no single-agent control.

### H2 — Execution feedback

**Hypothesis:** execution feedback can turn failures into useful revisions.

**Historical evidence:** the historical code has a feedback/refinement path, but no candidate reached a second recorded iteration.

**Conclusion from evidence:** insufficient. The historical run did not produce a measurable repair trajectory.

### H3 — Agent diversity

**Hypothesis:** model/prompt diversity may reduce correlated failure.

**Historical evidence:** the raw artifact contains agent IDs but no committed per-agent runtime model/profile metadata.

**Conclusion from evidence:** insufficient. Diversity cannot be quantified from the preserved result file.

### H4 — Additional inference compute / refinement

**Hypothesis:** more inference can improve reliability, with diminishing returns.

**Historical evidence:** three iterations were permitted, but every recorded candidate used only one iteration.

**Conclusion from evidence:** not tested historically.

---

## 7. What the historical experiments actually show

The observed evidence supports a narrow engineering/research conclusion:

- The original repository **did execute a 24-agent, ReAct-style program-generation pipeline** and preserved 24 candidate traces.
- The execution artifact exposes a real failure mode in the original measurement protocol: the recorded legacy success field can be true even when the generated source contains a `SyntaxError`.
- The same artifact shows operational failures caused by the original stdin and API-error handling, including 30-second-scale execution attempts and quota-error text entering the code path.
- The experiment therefore demonstrates why **verified program-synthesis evaluation must use objective test outcomes rather than a process-level success flag**.

The evidence is **insufficient to conclude** that multi-agent generation, ReAct iteration, execution feedback, refinement, or diversity improved program-synthesis reliability. There was no valid control comparison and no trustworthy historical correctness metric.

---

## 8. Limitations

The historical evidence has several important limitations:

- **Single-task benchmark:** factorial is too small and too easy to support general conclusions.
- **No one-shot baseline:** the effect of ReAct or additional inference cannot be isolated.
- **Broken stdin protocol:** ordinary stdin-driven programs could be mismeasured.
- **First-test-only verification:** the historical loop did not evaluate all declared tests.
- **Invalid legacy correctness flag:** process success was not equivalent to specification-level correctness.
- **API failures mixed with code failures:** quota errors could be converted into source text.
- **No hidden tests:** the historical setup did not provide a held-out correctness signal.
- **Missing runtime configuration:** actual model/provider, agent profiles, and execution mode are not preserved in the raw artifact.
- **No token/cost metadata:** compute efficiency cannot be reconstructed beyond recorded sandbox timings.
- **No statistical replication:** one historical run is not a repeated estimate.
- **Model-call count is not FLOP equivalence:** even a future matched-call comparison would not establish equal underlying inference compute.
- **Docker and subprocess modes are not equivalent security environments.**

---

## 9. Relationship to the hardened framework

The later framework was built to address these weaknesses without rewriting the historical result.

It adds:

- explicit baseline methods
- structured attempt-level execution results
- full visible-test evaluation
- refinement and selection controls
- explicit model-call and wall-clock budgets
- token/cost fields when available
- diversity measurements
- preserved raw traces
- automated tests and CI

The hardened framework is a **future measurement instrument**, not a retroactive correction of H-001.

In particular, the presence of `configs/single_pass.yaml`, `configs/single_agent_react.yaml`, `configs/multi_agent.yaml`, `configs/verified_multi_agent.yaml`, and `configs/vmar_ps.yaml` does not mean those conditions were executed.

---

## 10. Portfolio conclusion

> **In the tested historical experiment, VMAR-PS predecessor code successfully generated and recorded 24 multi-agent candidate attempts, but the measurement protocol was too weak to establish program-synthesis correctness or causal benefits from multi-agent ReAct. The strongest defensible finding is diagnostic: execution-based program synthesis requires objective test comparison, reliable stdin handling, explicit API-failure states, and attempt-level verification.**

The historical result is therefore best presented as a **reproducible research case study of an early multi-agent ReAct prototype and its measurement failure modes**, not as a performance benchmark or proof of method superiority.

