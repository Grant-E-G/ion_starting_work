import json
import tempfile
import unittest
from pathlib import Path

from audit import append, check, freeze, validate, verify


class AuditTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        template = (
            Path(__file__).resolve().parents[3]
            / "sources/statistics/claim_template.json"
        )
        self.card = json.loads(template.read_text().replace("REPLACE", "fixture"))
        (self.root / "artifact").write_text("fixed predictions/analysis fixture")
        (self.root / "partitions.csv").write_text(
            "construct_id,split,site\na,train,1\nb,test,2\n"
        )
        self.card["artifacts"] = {key: "artifact" for key in self.card["artifacts"]}
        self.card["artifacts"]["partitions"] = "partitions.csv"
        self.card_path = self.root / "card.json"
        self.card_path.write_text(json.dumps(self.card))
        self.submission = self.root / "submission.json"

    def test_group_leakage(self) -> None:
        (self.root / "partitions.csv").write_text(
            "construct_id,split,site\na,train,1\nb,test,1\n"
        )
        with self.assertRaisesRegex(ValueError, "Group crosses"):
            validate(self.card, self.root)

    def test_exposure_cannot_be_promoted(self) -> None:
        self.card["evidence_tier"] = "E3"
        self.card["protected_access"] = "externally_isolated"
        with self.assertRaisesRegex(ValueError, "Inspected labels"):
            validate(self.card, self.root)

    def test_external_evaluation_requires_isolation(self) -> None:
        self.card["evidence_tier"] = "E3"
        self.card["exposure"] = "uninspected"
        with self.assertRaisesRegex(ValueError, "external evaluator"):
            validate(self.card, self.root)

    def test_prospective_freeze_requires_unobserved_outcomes(self) -> None:
        self.card["evidence_tier"] = "E4"
        with self.assertRaisesRegex(ValueError, "precede outcomes"):
            validate(self.card, self.root)

    def test_frozen_predictions_changed(self) -> None:
        freeze(self.card_path, self.root, self.submission)
        (self.root / "artifact").write_text("changed after feedback")
        with self.assertRaisesRegex(ValueError, "artifact changed"):
            check(self.submission, self.root)
        with self.assertRaises(FileExistsError):
            freeze(self.card_path, self.root, self.submission)

    def test_submission_and_failed_run_preserved(self) -> None:
        freeze(self.card_path, self.root, self.submission)
        ledger = self.root / "ledger.jsonl"
        append(
            ledger,
            self.submission,
            self.root,
            "submitted",
            "seed and budget in attached analysis",
        )
        with self.assertRaisesRegex(ValueError, "already recorded"):
            append(ledger, self.submission, self.root, "submitted", "retry")
        append(ledger, self.submission, self.root, "failed", "timeout; stderr archived")
        self.assertEqual([r["event"] for r in verify(ledger)], ["submitted", "failed"])
        ledger.write_text(ledger.read_text().replace("timeout", "success"))
        with self.assertRaisesRegex(ValueError, "hash chain"):
            verify(ledger)


if __name__ == "__main__":
    unittest.main()
