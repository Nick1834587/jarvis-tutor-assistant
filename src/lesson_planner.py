"""Create first-semester Calculus I lesson outlines."""


def create_lesson_plan(topic):
    """Return a curated 60-minute lesson for a supported topic."""
    normalized_topic = topic.strip().lower().rstrip(".!?")

    if normalized_topic in {"limit", "limits"}:
        return _limits_lesson()
    if normalized_topic in {"derivative", "derivatives"}:
        return _derivatives_lesson()

    return (
        "For now, I can make Calculus I lessons about limits or derivatives. "
        "An integral lesson can be added next."
    )


def _limits_lesson():
    return "\n".join(
        [
            "Calculus I: Limits — 60-minute lesson",
            "Goal: Explain what a limit means and evaluate a simple 0/0 limit by factoring.",
            "",
            "5 min — Warm-up: Review substitution and factoring x^2 - 4.",
            (
                "15 min — What a limit means: A limit describes the value a function "
                "gets close to as x gets close to a chosen number. The function "
                "does not have to be defined at that exact number."
            ),
            (
                "15 min — Worked example: Find the limit as x approaches 2 of "
                "(x^2 - 4)/(x - 2). Substitution gives 0/0, so factor the numerator: "
                "x^2 - 4 = (x - 2)(x + 2). For x not equal to 2, cancel x - 2. "
                "The nearby values follow x + 2, which approaches 4. The limit is 4 "
                "even though the original expression is undefined at x = 2."
            ),
            (
                "15 min — Guided practice: Solve the limit as x approaches 3 of "
                "(x^2 - 9)/(x - 3). Factor, simplify for x not equal to 3, and "
                "explain why the answer is 6."
            ),
            (
                "10 min — Independent check and recap: Ask the student to find the "
                "limit as x approaches 1 of (x^2 - 1)/(x - 1), then explain why "
                "the limit can exist even though the original expression is "
                "undefined at x = 1. Answer: 2."
            ),
        ]
    )


def _derivatives_lesson():
    return "\n".join(
        [
            "Calculus I: Derivatives — 60-minute lesson",
            (
                "Goal: Explain a derivative as an instantaneous rate of change "
                "and use the power rule on simple polynomials."
            ),
            "",
            (
                "5 min — Warm-up: Find the average slope between the points "
                "(2, 4) and (3, 9) on y = x^2. Answer: 5."
            ),
            (
                "15 min — What a derivative means: A derivative is the "
                "instantaneous rate of change, or the slope of a curve at one "
                "point. It comes from looking at secant slopes as the two points "
                "move closer together. The power rule says the derivative of "
                "x^n is n times x to the power n minus 1."
            ),
            (
                "15 min — Worked example: For f(x) = x^2, the difference quotient "
                "is ((x + h)^2 - x^2)/h = 2x + h. As h approaches 0, this becomes "
                "f'(x) = 2x. At x = 3, the slope is 6."
            ),
            (
                "15 min — Guided practice: Use the power rule on f(x) = x^3. "
                "Then find the slope at x = 2. Answer: f'(x) = 3x^2, so the "
                "slope is 12."
            ),
            (
                "10 min — Independent check and recap: Differentiate "
                "f(x) = x^2 + 3x and find the slope at x = 1. Answer: "
                "f'(x) = 2x + 3, so the slope is 5. Ask the student to explain "
                "what that slope represents."
            ),
        ]
    )
