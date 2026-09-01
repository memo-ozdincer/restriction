import shlex
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def trainer_arguments(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    command = text.split("exec python -m verl.trainer.main_lean", 1)[1]
    return shlex.split(command.replace("\\\n", " "))


class C3MatchedControlTests(unittest.TestCase):
    def test_control_differs_from_c3_only_in_hard_blocking_arguments(self):
        c3 = trainer_arguments(ROOT / "scripts/project/launch_c3.sh")
        control = trainer_arguments(ROOT / "scripts/project/launch_c3_matched_control.sh")
        c3_common = [arg for arg in c3 if not arg.startswith("lean.hard_blocking.")]
        control_common = [arg for arg in control if not arg.startswith("lean.hard_blocking.")]
        self.assertEqual(control_common, c3_common)
        self.assertEqual(
            [arg for arg in control if arg.startswith("lean.hard_blocking.")],
            ["lean.hard_blocking.enabled=False"],
        )
        self.assertIn("lean.hard_blocking.enabled=True", c3)

    def test_control_enforces_fresh_base_initialization_in_launcher(self):
        args = trainer_arguments(ROOT / "scripts/project/launch_c3_matched_control.sh")
        self.assertIn('actor_rollout_ref.model.path=${BASE_MODEL_PATH}', args)
        self.assertIn("+trainer.resume=False", args)
        self.assertNotIn("trainer.resume_train_batch_buffer", " ".join(args))

    def test_control_and_c3_share_the_operational_worker_override(self):
        for name in ("launch_c3.sh", "launch_c3_matched_control.sh"):
            launcher = (ROOT / "scripts/project" / name).read_text(encoding="utf-8")
            self.assertIn(
                'MAX_WORKERS="${RESTRICTION_LEAN_MAX_WORKERS:-64}"', launcher
            )
            self.assertIn('lean.max_workers="${MAX_WORKERS}"', launcher)


if __name__ == "__main__":
    unittest.main()
