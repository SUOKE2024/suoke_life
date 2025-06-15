#!/usr/bin/env python3
"""
代码质量自动修复脚本
索克生活 - 算诊服务代码质量优化工具
"""

import re
import subprocess
import sys
from pathlib import Path


class CodeQualityFixer:
    """代码质量修复器"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.fixed_files: list[str] = []
        self.errors: list[str] = []

    def fix_syntax_errors(self) -> None:
        """修复语法错误"""
        print("🔧 修复语法错误...")

        # 修复类型注解语法错误
        self._fix_type_annotations()

        # 修复缩进错误
        self._fix_indentation_errors()

        # 修复导入错误
        self._fix_import_errors()

    def _fix_type_annotations(self) -> None:
        """修复类型注解语法错误"""
        re.compile(r"(\w+\([^)]*\))\s*-\s*>\s*(\w+):")

        for py_file in self.project_root.rglob("*.py"):
            try:
                content = py_file.read_text(encoding="utf-8")
                original_content = content

                # 修复 " -> " 为 " -> "
                content = re.sub(r"\s*-\s*>\s*", " -> ", content)

                if content != original_content:
                    py_file.write_text(content, encoding="utf-8")
                    self.fixed_files.append(str(py_file))
                    print(
                        f"  ✅ 修复类型注解: {py_file.relative_to(self.project_root)}"
                    )

            except Exception as e:
                self.errors.append(f"修复类型注解失败 {py_file}: {e}")

    def _fix_indentation_errors(self) -> None:
        """修复缩进错误"""
        problem_files = [
            "run.py",
            "simple_server.py",
            "simple_test.py",
            "test_service.py",
        ]

        for filename in problem_files:
            file_path = self.project_root / filename
            if file_path.exists():
                try:
                    content = file_path.read_text(encoding="utf-8")

                    # 移除行首的多余空格
                    lines = content.split("\n")
                    fixed_lines = []

                    for line in lines:
                        # 如果行首有多余的空格，移除它们
                        if line.startswith("        ") and not line.strip().startswith(
                            "#"
                        ):
                            # 8个空格缩进改为0个
                            fixed_lines.append(line[8:])
                        elif (
                            line.startswith("    ")
                            and line.strip()
                            and not line.strip().startswith('"""')
                        ):
                            # 保持4个空格的正常缩进
                            fixed_lines.append(line)
                        else:
                            fixed_lines.append(line)

                    fixed_content = "\n".join(fixed_lines)

                    if fixed_content != content:
                        file_path.write_text(fixed_content, encoding="utf-8")
                        self.fixed_files.append(str(file_path))
                        print(f"  ✅ 修复缩进: {filename}")

                except Exception as e:
                    self.errors.append(f"修复缩进失败 {filename}: {e}")

    def _fix_import_errors(self) -> None:
        """修复导入错误"""
        # 修复 models/__init__.py 的导入问题
        models_init = self.project_root / "calculation_service/core/models/__init__.py"
        if models_init.exists():
            try:
                models_init.read_text(encoding="utf-8")

                # 修复不完整的导入语句
                fixed_content = """from .base import BaseModel, CalculationBaseModel
from .patient import PatientInfoModel, BirthInfoModel

__all__ = [
    "BaseModel",
    "CalculationBaseModel",
    "PatientInfoModel",
    "BirthInfoModel"
]
"""

                models_init.write_text(fixed_content, encoding="utf-8")
                self.fixed_files.append(str(models_init))
                print("  ✅ 修复导入: models/__init__.py")

            except Exception as e:
                self.errors.append(f"修复models/__init__.py失败: {e}")

    def clean_unused_imports(self) -> None:
        """清理未使用的导入"""
        print("🧹 清理未使用的导入...")

        try:
            # 使用ruff自动修复
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "ruff",
                    "check",
                    ".",
                    "--fix",
                    "--select",
                    "F401",
                ],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                print("  ✅ 清理未使用导入完成")
            else:
                print(f"  ⚠️ 清理导入时有警告: {result.stderr}")

        except Exception as e:
            self.errors.append(f"清理导入失败: {e}")

    def format_code(self) -> None:
        """格式化代码"""
        print("🎨 格式化代码...")

        try:
            # 使用ruff格式化
            result = subprocess.run(
                [sys.executable, "-m", "ruff", "format", "."],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                print("  ✅ 代码格式化完成")
            else:
                print(f"  ⚠️ 格式化时有警告: {result.stderr}")

        except Exception as e:
            self.errors.append(f"代码格式化失败: {e}")

    def fix_assignment_operators(self) -> None:
        """修复赋值操作符错误"""
        print("🔧 修复赋值操作符...")

        for py_file in self.project_root.rglob("*.py"):
            try:
                content = py_file.read_text(encoding="utf-8")
                original_content = content

                # 修复 " /= " 为 " /= "
                content = re.sub(r"\s*/\s*=\s*", " /= ", content)

                if content != original_content:
                    py_file.write_text(content, encoding="utf-8")
                    self.fixed_files.append(str(py_file))
                    print(
                        f"  ✅ 修复赋值操作符: {py_file.relative_to(self.project_root)}"
                    )

            except Exception as e:
                self.errors.append(f"修复赋值操作符失败 {py_file}: {e}")

    def add_missing_imports(self) -> None:
        """添加缺失的导入"""
        print("📦 添加缺失的导入...")

        # 修复validators.py中缺失的HTTPException导入
        validators_file = self.project_root / "calculation_service/utils/validators.py"
        if validators_file.exists():
            try:
                content = validators_file.read_text(encoding="utf-8")

                if "from fastapi import HTTPException" not in content:
                    # 在文件开头添加导入
                    lines = content.split("\n")
                    import_line = "from fastapi import HTTPException"

                    # 找到合适的位置插入导入
                    insert_index = 0
                    for i, line in enumerate(lines):
                        if line.startswith("from ") or line.startswith("import "):
                            insert_index = i + 1
                        elif line.strip() == "":
                            continue
                        else:
                            break

                    lines.insert(insert_index, import_line)
                    fixed_content = "\n".join(lines)

                    validators_file.write_text(fixed_content, encoding="utf-8")
                    self.fixed_files.append(str(validators_file))
                    print("  ✅ 添加HTTPException导入: validators.py")

            except Exception as e:
                self.errors.append(f"添加导入失败 validators.py: {e}")

    def run_quality_check(self) -> bool:
        """运行质量检查"""
        print("🔍 运行代码质量检查...")

        try:
            # 运行ruff检查
            result = subprocess.run(
                [sys.executable, "-m", "ruff", "check", "."],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                print("  ✅ 代码质量检查通过")
                return True
            else:
                print("  ⚠️ 仍有质量问题需要手动修复:")
                print(result.stdout)
                return False

        except Exception as e:
            self.errors.append(f"质量检查失败: {e}")
            return False

    def run_tests(self) -> bool:
        """运行测试"""
        print("🧪 运行测试...")

        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "tests/", "-v"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                print("  ✅ 所有测试通过")
                return True
            else:
                print("  ❌ 测试失败:")
                print(result.stdout)
                print(result.stderr)
                return False

        except Exception as e:
            self.errors.append(f"运行测试失败: {e}")
            return False

    def generate_report(self) -> None:
        """生成修复报告"""
        print("\n" + "=" * 60)
        print("📊 代码质量修复报告")
        print("=" * 60)

        print(f"\n✅ 修复的文件数量: {len(self.fixed_files)}")
        if self.fixed_files:
            for file_path in self.fixed_files:
                print(f"  - {file_path}")

        print(f"\n❌ 错误数量: {len(self.errors)}")
        if self.errors:
            for error in self.errors:
                print(f"  - {error}")

        print(f"\n🎯 总体状态: {'✅ 良好' if len(self.errors) == 0 else '⚠️ 需要关注'}")


def main():
    """主函数"""
    print("🚀 启动代码质量自动修复...")

    # 获取项目根目录
    project_root = Path(__file__).parent.parent

    # 创建修复器
    fixer = CodeQualityFixer(str(project_root))

    # 执行修复步骤
    fixer.fix_syntax_errors()
    fixer.fix_assignment_operators()
    fixer.add_missing_imports()
    fixer.clean_unused_imports()
    fixer.format_code()

    # 运行检查
    quality_ok = fixer.run_quality_check()
    tests_ok = fixer.run_tests()

    # 生成报告
    fixer.generate_report()

    # 返回状态
    if quality_ok and tests_ok:
        print("\n🎉 代码质量修复完成！")
        return 0
    else:
        print("\n⚠️ 修复完成，但仍有问题需要手动处理")
        return 1


if __name__ == "__main__":
    sys.exit(main())
