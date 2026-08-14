"""Small, testable policy helpers for dominant-mode exclusion."""

from __future__ import annotations

from collections.abc import Collection

import torch


def should_skip_prompt(success_indices: Collection[int], blocked_correct: Collection[bool]) -> bool:
    """Return whether every verified-correct proposal is blocked.

    A prompt with no correct proposals is deliberately not skipped: it retains
    the exact upstream incorrect-rollout treatment.
    """
    return bool(success_indices) and all(blocked_correct[index] for index in success_indices)


def zero_blocked_advantages(scores: torch.Tensor, blocked_correct: Collection[bool]) -> torch.Tensor:
    """Return a copy with only blocked-correct rollout advantages set to zero."""
    blocked = torch.tensor(
        [bool(value) for value in blocked_correct],
        device=scores.device,
        dtype=torch.bool,
    )
    if blocked.numel() != scores.numel():
        raise ValueError("blocked_correct must have one entry per rollout")
    result = scores.clone()
    result[blocked] = 0.0
    return result


def apply_hard_exclusion(
    scores: torch.Tensor, *, enabled: bool, blocked_correct: Collection[bool] | None = None
) -> torch.Tensor:
    """Leave disabled batches untouched; otherwise zero blocked-correct entries."""
    if not enabled:
        return scores
    if blocked_correct is None:
        raise ValueError("enabled hard exclusion requires blocked_correct metadata")
    return zero_blocked_advantages(scores, blocked_correct)


def assert_pristine_restart(
    *, enabled: bool, archive_path: str | None, base_model_path: str | None,
    model_path: str, resume: bool, resume_train_batch_buffer: str | None,
    is_control: bool = False,
) -> None:
    """Reject a hard-block run that would inherit a discovery checkpoint."""
    if not enabled or is_control:
        return
    if not archive_path:
        raise ValueError("hard_blocking.enabled requires lean.hard_blocking.archive_path")
    if not base_model_path:
        raise ValueError("hard_blocking.enabled requires lean.hard_blocking.base_model_path")
    if model_path != base_model_path:
        raise ValueError("hard-block restart must initialize actor from the configured pristine base model")
    if resume or resume_train_batch_buffer:
        raise ValueError("hard-block restart must use fresh optimizer state and an empty rollout buffer")
