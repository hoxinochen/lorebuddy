"""LoreBuddy M1 CLI；M1-B 只增加受控 Source 摄取命令。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from lorebuddy.config import ConfigError, load_config
from lorebuddy.acquisition import (
    AcquisitionError,
    BackendUnavailableError,
    SevenZipBackend,
    inspect_artifact,
    load_acquisition_report,
    run_acquisition,
)
from lorebuddy.registry import RegistryError, SchemaRegistry
from lorebuddy.validation import DocumentLoadError, SchemaValidator, load_document
from lorebuddy.validation.source_semantics import validate_acquisition


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="lorebuddy", description="LoreBuddy M1 工具")
    commands = parser.add_subparsers(dest="command", required=True)

    schemas = commands.add_parser("schemas", help="列出或验证 Schema")
    schema_commands = schemas.add_subparsers(dest="schema_command", required=True)
    schema_commands.add_parser("list", help="列出 Registry 中的 Schema")
    validate = schema_commands.add_parser("validate", help="按 Schema 验证 JSON / YAML")
    validate.add_argument("schema_id")
    validate.add_argument("file", type=Path)

    fixtures = commands.add_parser("fixtures", help="验证 M1-A Fixture")
    fixture_commands = fixtures.add_subparsers(dest="fixture_command", required=True)
    fixture_commands.add_parser("validate", help="验证全部正反 Fixture")

    config = commands.add_parser("config", help="检查本地配置语法")
    config_commands = config.add_subparsers(dest="config_command", required=True)
    config_commands.add_parser("check", help="读取配置但不访问 Vault")

    acquire = commands.add_parser("acquire", help="M1-B 受控 CHM 摄取")
    acquire_commands = acquire.add_subparsers(dest="acquire_command", required=True)
    inspect = acquire_commands.add_parser("inspect", help="只读取原件大小与摘要")
    inspect.add_argument("chm_path", type=Path)
    inspect.add_argument("--json", action="store_true")
    run = acquire_commands.add_parser("run", help="受控解包并生成 Source Inventory")
    run.add_argument("chm_path", type=Path)
    run.add_argument("--output", type=Path, default=Path("build/acquisition"))
    run.add_argument("--backend", choices=["7zip"], default="7zip")
    run.add_argument("--executable", help="7zz/7z 可执行文件绝对路径；不修改 PATH")
    run.add_argument("--timeout", type=float, default=300.0)
    run.add_argument("--dry-run", action="store_true")
    run.add_argument("--json", action="store_true")
    validate_acquire = acquire_commands.add_parser("validate", help="校验已有摄取产物")
    validate_acquire.add_argument("artifact_dir", type=Path)
    validate_acquire.add_argument("--json", action="store_true")
    report = acquire_commands.add_parser("report", help="读取 Acquisition Report")
    report.add_argument("artifact_dir", type=Path)
    report.add_argument("--json", action="store_true")
    return parser


def _print_payload(payload: dict[str, object], as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return
    for key, value in payload.items():
        if isinstance(value, (dict, list)):
            print(f"{key}={json.dumps(value, ensure_ascii=False, sort_keys=True)}")
        else:
            print(f"{key}={value}")


def _fixture_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in {".json", ".yaml", ".yml"}
    )


def _validate_fixtures(project_root: Path, validator: SchemaValidator) -> int:
    fixture_root = project_root / "fixtures" / "m1a"
    failures: list[str] = []
    total = 0
    for expectation in ("valid", "invalid"):
        files = _fixture_files(fixture_root / expectation)
        if not files:
            failures.append(f"{expectation} Fixture 目录为空")
            continue
        for path in files:
            total += 1
            try:
                data = load_document(path)
            except DocumentLoadError as exc:
                failures.append(f"{path}: {exc}")
                continue
            schema_id = data.get("schema") if isinstance(data, dict) else None
            if not isinstance(schema_id, str):
                failures.append(f"{path}: 缺少 schema 字段")
                continue
            result = validator.validate_data(data, schema_id, file=str(path))
            expected_valid = expectation == "valid"
            if result.valid != expected_valid:
                failures.append(
                    f"{path}: expected valid={expected_valid}, actual={result.valid}"
                )
    if failures:
        for failure in failures:
            print(f"ERROR {failure}", file=sys.stderr)
        return 1
    print(f"Fixture 验证通过：{total} 个")
    return 0


def main(argv: Sequence[str] | None = None, *, project_root: Path | None = None) -> int:
    args = _parser().parse_args(argv)
    root = (project_root or Path.cwd()).resolve()
    try:
        if args.command == "acquire":
            if args.acquire_command == "inspect":
                _print_payload(inspect_artifact(args.chm_path), args.json)
                return 0
            if args.acquire_command == "run":
                if args.timeout <= 0:
                    raise AcquisitionError("timeout 必须大于 0")
                payload = run_acquisition(
                    args.chm_path,
                    args.output,
                    backend=SevenZipBackend(args.executable) if args.executable else None,
                    timeout=args.timeout,
                    dry_run=args.dry_run,
                    project_root=root,
                )
                _print_payload(payload, args.json)
                return 0
            if args.acquire_command == "validate":
                payload = validate_acquisition(args.artifact_dir, project_root=root)
                _print_payload(payload, args.json)
                return 0 if payload["valid"] else 1
            if args.acquire_command == "report":
                _print_payload(load_acquisition_report(args.artifact_dir), args.json)
                return 0

        if args.command == "config":
            config = load_config(root)
            print("本地配置有效；Vault 路径已配置但未访问。")
            print(f"test_publish_subdirectory={config.obsidian.test_publish_subdirectory}")
            print(f"publish_subdirectory={config.obsidian.publish_subdirectory}")
            print(f"staging_root={config.build.staging_root}")
            return 0

        registry = SchemaRegistry.from_project_root(root)
        if args.command == "schemas" and args.schema_command == "list":
            for entry in registry.list_entries():
                print(f"{entry.schema_id}\t{entry.status}\t{entry.path}")
            return 0
        validator = SchemaValidator(registry)
        if args.command == "schemas" and args.schema_command == "validate":
            result = validator.validate_file(args.schema_id, args.file)
            print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
            return 0 if result.valid else 1
        if args.command == "fixtures" and args.fixture_command == "validate":
            return _validate_fixtures(root, validator)
    except (AcquisitionError, BackendUnavailableError, ConfigError, RegistryError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
