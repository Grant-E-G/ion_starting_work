"""Local, tamper-evident submission records; not a protected-label evaluator."""

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def encoded(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()


def validate(card: dict[str, Any], root: Path) -> dict[str, str]:
    template = json.loads(
        (
            Path(__file__).resolve().parents[3]
            / "sources/statistics/claim_template.json"
        ).read_text()
    )
    if set(card) != set(template):
        raise ValueError("Claim fields must match claim_template.json")
    if any(token in json.dumps(card) for token in ("REPLACE", "TODO", "TBD")):
        raise ValueError("Unresolved claim-card placeholders")
    if any(
        value is None or value == "" or value == [] or value == {}
        for value in card.values()
    ):
        raise ValueError("Empty claim field")
    if card["schema_version"] != 1 or card["evidence_tier"] not in [
        "E0",
        "E1",
        "E2",
        "E3",
        "E4",
    ]:
        raise ValueError("Unknown schema or evidence tier")
    if card["purpose"] not in [
        "development",
        "assay_feasibility",
        "exploratory_panel",
        "confirmation",
    ]:
        raise ValueError("Unknown purpose")
    if card["preprocessing_fit_scope"] != "training_only":
        raise ValueError("Preprocessing must fit training only")
    if card["exposure"] not in [
        "previously_inspected",
        "uninspected",
        "outcomes_not_yet_exist",
    ]:
        raise ValueError("Unknown exposure status")
    if (
        card["evidence_tier"] in ["E2", "E3"]
        and card["exposure"] == "previously_inspected"
    ):
        raise ValueError("Inspected labels cannot be promoted by a new split")
    if (
        card["evidence_tier"] == "E3"
        and card["protected_access"] != "externally_isolated"
    ):
        raise ValueError("E3 requires an external evaluator boundary")
    if card["evidence_tier"] == "E4" and card["exposure"] != "outcomes_not_yet_exist":
        raise ValueError("Prospective card must precede outcomes")
    if not isinstance(card["primary_metric"], str):
        raise TypeError("Declare exactly one primary metric")
    required = {
        "predictions",
        "partitions",
        "analysis",
        "data_provenance",
        "weights_provenance",
    }
    if not required <= set(card["artifacts"]):
        raise ValueError("Missing artifact role")
    hashes = {
        name: digest((root / path).read_bytes())
        for name, path in card["artifacts"].items()
    }
    columns = card["partition_columns"]
    groups: dict[tuple[str, str], str] = {}
    ids: set[str] = set()
    with (root / card["artifacts"]["partitions"]).open(newline="") as stream:
        reader = csv.DictReader(stream)
        required_columns = [columns["id"], columns["split"], *card["grouping_columns"]]
        if not set(required_columns) <= set(reader.fieldnames or []):
            raise ValueError("Missing partition/group columns")
        for row in reader:
            if any(not row[column].strip() for column in required_columns):
                raise ValueError("Missing identity, split or group")
            identity, split = row[columns["id"]], row[columns["split"]]
            if identity in ids or split not in columns["allowed"]:
                raise ValueError("Duplicate construct or unknown split")
            ids.add(identity)
            for column in card["grouping_columns"]:
                key = (column, row[column])
                if key in groups and groups[key] != split:
                    raise ValueError(f"Group crosses splits: {column}={row[column]}")
                groups[key] = split
    if not ids:
        raise ValueError("Empty partition")
    return hashes


def verify(ledger: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    previous = "0" * 64
    for line in ledger.read_text().splitlines() if ledger.exists() else []:
        record = json.loads(line)
        checksum = record.pop("record_sha256")
        if record["previous_sha256"] != previous or digest(encoded(record)) != checksum:
            raise ValueError("Broken ledger hash chain")
        previous = checksum
        record["record_sha256"] = checksum
        records.append(record)
    return records


def freeze(card_path: Path, root: Path, destination: Path) -> None:
    card = json.loads(card_path.read_text())
    hashes = validate(card, root)
    payload = {
        "card": card,
        "artifact_sha256": hashes,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    with destination.open("x") as stream:
        json.dump(payload, stream, indent=2, allow_nan=False)
        stream.write("\n")


def check(submission: Path, root: Path) -> None:
    payload = json.loads(submission.read_text())
    if validate(payload["card"], root) != payload["artifact_sha256"]:
        raise ValueError("Frozen artifact changed")


def append(ledger: Path, submission: Path, root: Path, event: str, detail: str) -> None:
    # Exclusive lock serializes this tool's writers on this Linux workspace.
    import fcntl

    check(submission, root)
    with ledger.open("a+") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        records = verify(ledger)
        submission_sha = digest(submission.read_bytes())
        if event == "submitted" and any(
            r["event"] == event and r["submission_sha256"] == submission_sha
            for r in records
        ):
            raise ValueError("Submission already recorded")
        if event in ["completed", "failed"] and not any(
            r["event"] == "submitted" and r["submission_sha256"] == submission_sha
            for r in records
        ):
            raise ValueError("Record submission before outcome")
        if event in ["completed", "failed"] and any(
            r["event"] in ["completed", "failed"]
            and r["submission_sha256"] == submission_sha
            for r in records
        ):
            raise ValueError("Outcome already recorded; use a deviation event")
        record = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "submission_sha256": submission_sha,
            "event": event,
            "detail": detail,
            "previous_sha256": records[-1]["record_sha256"] if records else "0" * 64,
        }
        record["record_sha256"] = digest(encoded(record))
        stream.write(json.dumps(record, allow_nan=False) + "\n")
        stream.flush()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", choices=["validate", "freeze", "check", "record", "verify-ledger"]
    )
    parser.add_argument("path", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path)
    parser.add_argument("--ledger", type=Path)
    parser.add_argument(
        "--event", choices=["submitted", "completed", "failed", "deviation"]
    )
    parser.add_argument("--detail")
    args = parser.parse_args()
    try:
        if args.command == "validate":
            validate(json.loads(args.path.read_text()), args.root)
        elif args.command == "freeze":
            if args.output is None:
                raise ValueError("--output required")
            freeze(args.path, args.root, args.output)
        elif args.command == "check":
            check(args.path, args.root)
        elif args.command == "verify-ledger":
            verify(args.path)
        else:
            if args.ledger is None or not args.event or not args.detail:
                raise ValueError("--ledger, --event and --detail required")
            append(args.ledger, args.path, args.root, args.event, args.detail)
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(1, f"Audit failed: {error}\n")
    print("Audit passed")


if __name__ == "__main__":
    main()
