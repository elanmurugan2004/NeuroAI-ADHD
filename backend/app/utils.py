def generate_simple_explanation(score: float) -> str:
    if score >= 0.75:
        return "High likelihood of ADHD based on behavioral input features."
    elif score >= 0.50:
        return "Moderate likelihood of ADHD. Further clinical evaluation is recommended."
    else:
        return "Low likelihood of ADHD based on current input values."


def identify_region(score: float) -> str:
    if score >= 0.75:
        return "Prefrontal Cortex"
    elif score >= 0.50:
        return "Fronto-Striatal Circuit"
    else:
        return "No dominant abnormal region identified"