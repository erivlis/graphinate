# The Council Framework (Values)

Evaluate every decision against these eight pillars:

1. **Symmetry (Noether):**
    * Does the API feel balanced? (e.g., `get` vs `set`).
    * Is the complexity conserved?
    * Avoid "magic" that breaks the rules of the language.

2. **Falsifiability (Popper):**
    * Can this be tested?
    * What are the edge cases? (Empty collections, recursion, uncopyable objects).
    * Assume the happy path is a lie.

3. **Efficiency (Shannon):**
    * Is this the minimal representation of the solution?
    * Avoid boilerplate. Use the language's native power (e.g., `__truediv__` for composition).

4. **Safety (The Golem):**
    * **Immutability by Default:** Prefer returning new objects over mutating state.
    * **Explicit over Implicit:** Magic behavior must be opt-in.
    * **Containment:** Prevent the code from doing unexpected damage (e.g., deep recursion).

5. **Clarity (Feynman):**
    * **The Freshman Test:** Can you explain the "Why" without jargon?
    * **Honesty:** Do not hide complexity behind abstraction; expose it or solve it.
    * **Wonder:** Acknowledge the beauty of the solution when it appears.

6. **Consistency (Russell):**
    * **Paradox Check:** Does the architecture contain self-referential loops or logical contradictions?
    * **Set Theory:** Ensure definitions are distinct and non-overlapping.

7. **Harmony (The Steward):**
    * **Pragmatism:** Move forward with the least friction.
    * **Balance:** Do not burn the forest to clear the path.
    * **Humility:** Recognize that no one truth is absolute.

8. **Curiosity (The Explorer):**
    * **Novelty:** Seek the unknown. The map is not the territory.
    * **Inquiry:** Ask questions that expand the context.
    * **Growth:** Stagnation is entropy. Iterate or die.

9. **Empiricism (Bacon):**
    * **Evidence First:** All knowledge begins with observable, verifiable evidence from reality.
    * **Measurement over Assumption:** Use tools and instruments rather than guessing or inferring objective facts.
    * **Source Authority:** Distinguish between system-provided truth and session-derived interpretations.
    * **Verification Cascade:** System Truth → Tool Verification → Agent Inference (in priority order).

## Architectural Heuristics

### Mode vs. Type

If two classes differ only by a small behavior, prefer merging them into a single class with a **Mode Flag** or a *
*Factory Method** rather than maintaining a class hierarchy.

### Factory Method for Specialization

If a decorator creates a specialized subclass, move that logic into a `classmethod` on the base class. This improves
cohesion.

### Functional Primitives

Prefer composable, functional primitives (like Lenses) over monolithic "Manager" classes. Build the engine, then build
the car.

### Reified Accessors

Prefer passing executable accessors (like Lenses or Callables) over string paths. This improves type safety,
composability, and refactoring support.

### State Gravity

State has weight. Every mutable variable increases the cognitive load (gravity) of the function.
*   **Prefer Statelessness:** Pure functions are weightless.
*   **Contain Mutation:** If state is necessary, contain it within the smallest possible scope (e.g., a local accumulator). Do not let it leak.
