"""
Color utility functions for visualization components.
"""


def score_to_gradient_color(score: float) -> str:
    """
    Convert score to gradient color from red (0.5) to green (1.0).

    Args:
        score: Float between 0.0 and 1.0 representing the argument quality score

    Returns:
        Hex color string representing the gradient color

    Color mapping:
        - score <= 0.5: Red (#f44336)
        - 0.5 < score < 1.0: Gradient from red to green
        - score >= 1.0: Green (#4caf50)
    """
    # Clamp score to valid range
    score = max(0.0, min(1.0, score))

    # If score is below 0.5, use red
    if score < 0.5:
        return "#f44336"  # Red

    # Calculate gradient position (0.0 to 1.0) for scores 0.5 to 1.0
    gradient_pos = (score - 0.5) / 0.5

    # Interpolate between red and green
    # Red: RGB(244, 67, 54) -> Green: RGB(76, 175, 80)
    r = int(244 - (244 - 76) * gradient_pos)
    g = int(67 + (175 - 67) * gradient_pos)
    b = int(54 + (80 - 54) * gradient_pos)

    return f"#{r:02x}{g:02x}{b:02x}"
