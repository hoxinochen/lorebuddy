"""M1-A 基础 CLI；没有摄取、转换或发布命令。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from lorebuddy.config import ConfigError, load_config
from lorebuddy.registry import RegistryError, SchemaRegistry
from lorebuddy.validation import DocumentLoadError, SchemaValidator, load_document


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="lorebuddy", description="LoreBuddy M1-A 工具")
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
    return parser


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
    except (ConfigError, RegistryError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
