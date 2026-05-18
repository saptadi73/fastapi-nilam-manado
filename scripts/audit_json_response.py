from __future__ import annotations

import ast
from pathlib import Path
import sys
from typing import Iterable

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
ROUTE_HTTP_METHODS = {"get", "post", "put", "delete", "patch", "options"}
SCAN_FILES = [WORKSPACE_ROOT / "main.py", *sorted((WORKSPACE_ROOT / "app" / "services").glob("*.py"))]


class RouteAuditVisitor(ast.NodeVisitor):
    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path
        self.issues: list[str] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if self._is_route_handler(node):
            self._validate_route_handler(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        if self._is_route_handler(node):
            self._validate_route_handler(node)
        self.generic_visit(node)

    def _is_route_handler(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call):
                continue
            func = decorator.func
            if not isinstance(func, ast.Attribute):
                continue
            if func.attr not in ROUTE_HTTP_METHODS:
                continue
            if isinstance(func.value, ast.Name) and func.value.id.endswith("router"):
                return True
        return False

    def _validate_route_handler(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        returns = [child for child in ast.walk(node) if isinstance(child, ast.Return)]
        if not returns:
            self.issues.append(
                f"{self.file_path.relative_to(WORKSPACE_ROOT)}:{node.lineno} route '{node.name}' has no return statement"
            )
            return

        for returned in returns:
            if returned.value is None:
                self.issues.append(
                    f"{self.file_path.relative_to(WORKSPACE_ROOT)}:{returned.lineno} route '{node.name}' returns nothing"
                )
                continue
            if not self._is_json_response_handler_call(returned.value):
                self.issues.append(
                    f"{self.file_path.relative_to(WORKSPACE_ROOT)}:{returned.lineno} route '{node.name}' does not return JSONResponseHandler"
                )

    @staticmethod
    def _is_json_response_handler_call(node: ast.AST) -> bool:
        if not isinstance(node, ast.Call):
            return False
        func = node.func
        return (
            isinstance(func, ast.Attribute)
            and isinstance(func.value, ast.Name)
            and func.value.id == "JSONResponseHandler"
            and func.attr in {"success", "error"}
        )


def audit_files(paths: Iterable[Path]) -> list[str]:
    issues: list[str] = []
    for path in paths:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        visitor = RouteAuditVisitor(path)
        visitor.visit(tree)
        issues.extend(visitor.issues)
    return issues


def main() -> int:
    issues = audit_files(SCAN_FILES)
    if issues:
        print("JSONResponseHandler audit failed:\n")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print("JSONResponseHandler audit passed: all route handlers return the standard response wrapper.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
