import shlex
import tempfile
import unittest
from pathlib import Path

import yaml

from scripts.project.analyze_c2_unlikeliness import (
    decision_classification,
    validate_intervention_invariants,
    validate_mechanism_configs,
)


ROOT = Path(__file__).resolve().parents[1]


def trainer_arguments(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    command = text.split("exec python -m verl.trainer.main_lean", 1)[1]
    return shlex.split(command.replace("\\\n", " "))


def overall(c2_modes, c3_modes, c2_correct=100, c3_correct=100, rare_delta=0.06):
    return {
        "c2": {"correct_mode_coverage": c2_modes, "correct": c2_correct},
        "c3": {"correct_mode_coverage": c3_modes, "correct": c3_correct},
        "correct_draw_rarefaction": {
            "16": {"relative_delta_c3_minus_c2": rare_delta}
        },
    }


class C2LauncherTests(unittest.TestCase):
    def test_c2_differs_from_matched_control_only_by_rank_penalty(self):
        c2 = trainer_arguments(ROOT / "scripts/project/launch_c2.sh")
        control = trainer_arguments(ROOT / "scripts/project/launch_c3_matched_control.sh")

        def normalized(args):
            return [
                arg for arg in args
                if not arg.lstrip("+").startswith("lean.rank_penalty=")
                and not arg.lstrip("+").startswith("lean.max_workers=")
            ]

        self.assertEqual(normalized(c2), normalized(control))
        self.assertIn("+lean.rank_penalty=0.25", c2)
        self.assertIn("+lean.rank_penalty=0.0", control)

    def test_c2_enforces_pristine_restart_and_no_archive(self):
        args = trainer_arguments(ROOT / "scripts/project/launch_c2.sh")
        self.assertIn("actor_rollout_ref.model.path=${BASE_MODEL_PATH}", args)
        self.assertIn("+trainer.resume=False", args)
        self.assertIn("lean.hard_blocking.enabled=False", args)
        self.assertNotIn("archive_path", " ".join(args))


class C2AnalysisTests(unittest.TestCase):
    def test_material_rule_requires_mode_rarefaction_and_correctness_guard(self):
        result = decision_classification(overall(100, 106), 1000)
        self.assertEqual(
            result["classification"],
            "material_training_support_for_hard_over_soft_exploration",
        )
        result = decision_classification(overall(100, 106, rare_delta=0.01), 1000)
        self.assertEqual(result["classification"], "mixed_or_intermediate_hard_versus_soft_result")
        result = decision_classification(overall(100, 106, 100, 40), 1000)
        self.assertEqual(result["classification"], "mixed_or_intermediate_hard_versus_soft_result")

    def test_practical_null_and_soft_superiority_are_explicit(self):
        self.assertEqual(
            decision_classification(overall(100, 103, rare_delta=0.02), 1000)["classification"],
            "practically_null_hard_versus_soft_difference",
        )
        self.assertEqual(
            decision_classification(overall(100, 90, rare_delta=-0.01), 1000)["classification"],
            "soft_unlikeliness_outperforms_hard_blocking",
        )

    def test_intervention_invariants_reject_c2_blocking(self):
        c2 = {
            "condition": "c2_unlikeliness_2",
            "blocked_correct_zero_advantage": 0,
            "physical_blocked_correct_zero_advantage": 0,
            "skipped_all_blocked_prompts": 0,
            "archive_sha256": None,
        }
        c3 = {
            "condition": "c3_hardblock_restart",
            "archive_sha256": "fcffb4a3dc9baf837d4780ec30855308ebc7f0c5086d607162889938b5e426d3",
        }
        validate_intervention_invariants(c2, c3)
        with self.assertRaises(ValueError):
            validate_intervention_invariants({**c2, "archive_sha256": "unexpected"}, c3)

    def test_resolved_configs_enforce_the_single_mechanism_contrast(self):
        base = {
            "data": {"train_files": "train.parquet"},
            "actor_rollout_ref": {
                "actor": {"ppo_epochs": 2, "kl_loss_coef": 0.1},
                "rollout": {"response_length": 512},
            },
            "lean": {"num_samples": 32},
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            c2 = root / "c2/hydra/.hydra"
            c3 = root / "c3/hydra/.hydra"
            c2.mkdir(parents=True)
            c3.mkdir(parents=True)
            (c2 / "config.yaml").write_text(
                yaml.safe_dump({**base, "lean": {**base["lean"], "rank_penalty": 0.25, "hard_blocking": {"enabled": False}}})
            )
            (c3 / "config.yaml").write_text(
                yaml.safe_dump({**base, "lean": {**base["lean"], "rank_penalty": 0.0, "hard_blocking": {"enabled": True}}})
            )
            validate_mechanism_configs(root / "c2", root / "c3")
            bad = yaml.safe_load((c2 / "config.yaml").read_text())
            bad["lean"]["rank_penalty"] = 0.1
            (c2 / "config.yaml").write_text(yaml.safe_dump(bad))
            with self.assertRaises(ValueError):
                validate_mechanism_configs(root / "c2", root / "c3")


if __name__ == "__main__":
    unittest.main()
