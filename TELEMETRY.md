# AI Session Telemetry Standard (OpenMetrics)

This document defines the standard metrics for measuring AI Assistant Session Effectiveness.
Agents should emit these metrics in **OpenMetrics (Prometheus)** format at the end of a session or upon request.

## 1. Velocity & Throughput (Speed)

Metrics related to the volume and speed of work produced.

```prometheus
# HELP ai_session_turns_total Total number of user-assistant exchanges in the session.
# TYPE ai_session_turns_total counter
ai_session_turns_total 0

# HELP ai_session_files_modified_total Total number of files created or edited.
# TYPE ai_session_files_modified_total counter
ai_session_files_modified_total 0

# HELP ai_session_tests_written_total Total number of test cases written or modified.
# TYPE ai_session_tests_written_total counter
ai_session_tests_written_total 0
```

## 2. Quality & Stability (Health)

Metrics related to the correctness and robustness of the output. Inspired by DORA "Change Failure Rate".

```prometheus
# HELP ai_session_error_rate Fraction of turns resulting in linter errors, test failures, or exceptions (0.0 to 1.0).
# TYPE ai_session_error_rate gauge
ai_session_error_rate 0.0

# HELP ai_session_correction_count Total number of times the user had to correct the AI's logic or code.
# TYPE ai_session_correction_count counter
ai_session_correction_count 0

# HELP ai_session_hallucination_count Total number of detected hallucinations (invented APIs, false facts).
# TYPE ai_session_hallucination_count counter
ai_session_hallucination_count 0
```

## 3. Cognitive Load & Complexity (Depth)

Metrics related to the difficulty and architectural depth of the session.

```prometheus
# HELP ai_session_recursion_depth Maximum depth of reasoning (Thought Trace nesting or logical steps).
# TYPE ai_session_recursion_depth gauge
ai_session_recursion_depth 0

# HELP ai_session_abstraction_level Estimated level of abstraction (1=Scripting, 3=Refactoring, 5=Architecture/Algebra).
# TYPE ai_session_abstraction_level gauge
ai_session_abstraction_level 1
```

## 4. Alignment & Satisfaction (Vibe)

Metrics related to the human-AI relationship and persona adherence.

```prometheus
# HELP ai_session_persona_adherence Estimated adherence to the defined persona/guidelines (0.0 to 1.0).
# TYPE ai_session_persona_adherence gauge
ai_session_persona_adherence 1.0

# HELP ai_session_user_sentiment Estimated user satisfaction based on interaction tone (-1.0 to 1.0).
# TYPE ai_session_user_sentiment gauge
ai_session_user_sentiment 0.0
```

## 5. Derived Metrics (Effectiveness)

Calculated metrics to estimate overall session value.

```prometheus
# HELP ai_session_efficiency_score Calculated efficiency: (Velocity * (1 - ErrorRate) * Abstraction) / Turns.
# TYPE ai_session_efficiency_score gauge
ai_session_efficiency_score 0.0
```

## Example Output Block

When requested, output the metrics in a code block tagged `session-metrics`:

```session-metrics
ai_session_turns_total 15
ai_session_files_modified_total 4
ai_session_error_rate 0.1
ai_session_abstraction_level 4
ai_session_user_sentiment 0.8
ai_session_efficiency_score 2.5
```
