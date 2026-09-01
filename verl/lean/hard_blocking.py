"""Small, testable policy helpers for dominant-mode exclusion."""

from __future__ import annotations

from collections.abc import Collection

import torch


ZERO_ADVANTAGE = "zero_advantage"
REJECT_REWARD = "reject_reward"
SUPPORTED_INTERVENTIONS = frozenset({ZERO_ADVANTAGE, REJECT_REWARD})


def validate_intervention(intervention: str) -> str:
    """Return a supported hard-block intervention or fail closed."""
    if intervention not in SUPPORTED_INTERVENTIONS:
        supported = ", ".join(sorted(SUPPORTED_INTERVENTIONS))
        raise ValueError(
            f"unsupported hard-block intervention {intervention!r}; expected one of: {supported}"
        )
    return intervention


def effective_success_indices(
    success_indices: Collection[int],
    blocked_correct: Collection[bool],
    *,
    intervention: str,
) -> set[int]:
    """Return the successes accepted by the configured training environment.

    Lean correctness is not changed. Under reward rejection, verified-correct
    rollouts matching the blocked mode are simply not accepted as successful
    training outcomes.
    """
    validate_intervention(intervention)
    successes = {int(index) for index in success_indices}
    blocked = [bool(value) for value in blocked_correct]
    if any(index < 0 or index >= len(blocked) for index in successes):
        raise ValueError("success index lies outside blocked_correct metadata")
    if intervention == ZERO_ADVANTAGE:
        return successes
    return {index for index in successes if not blocked[index]}


def effective_binary_rewards(
    num_rollouts: int,
    success_indices: Collection[int],
    blocked_correct: Collection[bool],
    *,
    intervention: str,
) -> list[float]:
    """Build binary training rewards without changing Lean's verdicts."""
    blocked = [bool(value) for value in blocked_correct]
    if len(blocked) != num_rollouts:
        raise ValueError("blocked_correct must have one entry per rollout")
    accepted = effective_success_indices(
        success_indices, blocked, intervention=intervention
    )
    return [1.0 if index in accepted else 0.0 for index in range(num_rollouts)]


def advantage_summary(
    advantages: torch.Tensor,
    rewards: torch.Tensor,
    blocked_correct: Collection[bool],
    *,
    intervention: str,
) -> dict[str, float | int | str | None]:
    """Summarize the learning signal for blocked, alternative, and incorrect rollouts."""
    validate_intervention(intervention)
    if advantages.ndim != 1 or rewards.ndim != 1 or advantages.shape != rewards.shape:
        raise ValueError("advantages and rewards must be same-length one-dimensional tensors")
    blocked = torch.tensor(
        [bool(value) for value in blocked_correct],
        device=advantages.device,
        dtype=torch.bool,
    )
    if blocked.numel() != advantages.numel():
        raise ValueError("blocked_correct must have one entry per rollout")
    rewarded = rewards > 0
    masks = {
        "blocked_correct": blocked,
        "alternative_correct": rewarded & ~blocked,
        "incorrect": ~rewarded & ~blocked,
    }
    summary: dict[str, float | int | str | None] = {"intervention": intervention}
    for label, mask in masks.items():
        count = int(mask.sum().item())
        summary[f"{label}_count"] = count
        summary[f"{label}_advantage_mean"] = (
            float(advantages[mask].mean().item()) if count else None
        )
    return summary


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
