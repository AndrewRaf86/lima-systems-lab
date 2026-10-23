"""Calibration metrics for any probabilistic classifier, including the fast model."""


def brier_score(probs: list[float], outcomes: list[int]) -> float:
    if not probs or len(probs) != len(outcomes):
        raise ValueError("equal-length, non-empty inputs required")
    return sum((p - o) ** 2 for p, o in zip(probs, outcomes)) / len(probs)


def reliability_bins(probs, outcomes, n_bins: int = 10):
    """Return [(bin_lo, bin_hi, count, mean_pred, observed_freq)] for non-empty bins."""
    bins = [[] for _ in range(n_bins)]
    for p, o in zip(probs, outcomes):
        bins[min(int(p * n_bins), n_bins - 1)].append((p, o))
    return [(i / n_bins, (i + 1) / n_bins, len(b),
             sum(p for p, _ in b) / len(b), sum(o for _, o in b) / len(b))
            for i, b in enumerate(bins) if b]


def base_rate_brier(outcomes: list[int]) -> float:
    """Brier of always predicting the base rate: the bar a model must beat."""
    p = sum(outcomes) / len(outcomes)
    return brier_score([p] * len(outcomes), outcomes)
