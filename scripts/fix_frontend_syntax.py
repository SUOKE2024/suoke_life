#!/usr/bin/env python3
"""
前端语法错误修复脚本
专门处理TypeScript/JSX语法问题
"""

import os
import re
from pathlib import Path


class FrontendSyntaxFixer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)

    def fix_app_tsx(self):
        """修复App.tsx中的语法错误"""
        app_file = self.project_root / "src" / "App.tsx"

        if not app_file.exists():
            print("❌ App.tsx文件不存在")
            return False

        try:
            with open(app_file, "r", encoding="utf-8") as f:
                content = f.read()

            # 修复空的花括号
            content = re.sub(r"\s*\{\}\s*\n", "\n", content)

            # 修复JSX语法错误
            fixes = [
                # 修复screenOptions语法
                (
                    r"screenOptions=\{\s*headerShown:\s*false\s*\}\>",
                    "screenOptions={{ headerShown: false }}>",
                ),
                # 修复样式对象语法
                (
                    r"backgroundColor:\s*\'#f5f5f5\'\}",
                    "backgroundColor: '#f5f5f5',\n  },",
                ),
                (
                    r"borderBottomColor:\s*\'#e0e0e0\'\}",
                    "borderBottomColor: '#e0e0e0',\n  },",
                ),
                (r"color:\s*\'#666\'\}", "color: '#666',\n  },"),
                (
                    r"borderBottomColor:\s*\'#2196F3\'\}",
                    "borderBottomColor: '#2196F3',\n  },",
                ),
                (r"backgroundColor:\s*\'#fff\'\}", "backgroundColor: '#fff',\n  },"),
                (r"color:\s*\'#666\'\}", "color: '#666',\n  },"),
            ]

            for pattern, replacement in fixes:
                content = re.sub(pattern, replacement, content)

            # 确保正确的JSX结构
            content = self.fix_jsx_structure(content)

            with open(app_file, "w", encoding="utf-8") as f:
                f.write(content)

            print("✅ App.tsx语法错误已修复")
            return True

        except Exception as e:
            print(f"❌ 修复App.tsx失败: {e}")
            return False

    def fix_jsx_structure(self, content: str) -> str:
        """修复JSX结构问题"""
        lines = content.split("\n")
        fixed_lines = []

        for line in lines:
            # 移除空的花括号
            if line.strip() == "{}":
                continue

            # 修复样式对象的语法
            if "flex: 1," in line and not line.strip().endswith(","):
                line = line.rstrip() + ","

            fixed_lines.append(line)

        return "\n".join(fixed_lines)

    def fix_setup_tests(self):
        """修复setupTests.ts"""
        setup_file = self.project_root / "src" / "setupTests.ts"

        if not setup_file.exists():
            print("⚠️ setupTests.ts文件不存在")
            return True

        try:
            with open(setup_file, "r", encoding="utf-8") as f:
                content = f.read()

            # 修复PERMISSIONS对象语法
            content = re.sub(r"PERMISSIONS:\s*\{\s*,", "PERMISSIONS: {", content)
            content = re.sub(r"IOS:\s*\{\s*,", "IOS: {", content)
            content = re.sub(r"ANDROID:\s*\{\s*,", "ANDROID: {", content)

            with open(setup_file, "w", encoding="utf-8") as f:
                f.write(content)

            print("✅ setupTests.ts语法错误已修复")
            return True

        except Exception as e:
            print(f"❌ 修复setupTests.ts失败: {e}")
            return False

    def update_package_json(self):
        """更新package.json添加React Native CLI依赖"""
        package_file = self.project_root / "package.json"

        if not package_file.exists():
            print("❌ package.json文件不存在")
            return False

        try:
            import json

            with open(package_file, "r", encoding="utf-8") as f:
                package_data = json.load(f)

            # 确保devDependencies存在
            if "devDependencies" not in package_data:
                package_data["devDependencies"] = {}

            # 添加React Native CLI
            package_data["devDependencies"]["@react-native-community/cli"] = "latest"

            with open(package_file, "w", encoding="utf-8") as f:
                json.dump(package_data, f, indent=2, ensure_ascii=False)

            print("✅ package.json已更新，添加了@react-native-community/cli")
            return True

        except Exception as e:
            print(f"❌ 更新package.json失败: {e}")
            return False

    def run_fixes(self):
        """运行所有修复"""
        print("🔧 开始修复前端语法错误...")

        results = []
        results.append(self.fix_app_tsx())
        results.append(self.fix_setup_tests())
        results.append(self.update_package_json())

        success_count = sum(results)
        total_count = len(results)

        print(
            f"""
📊 前端语法修复完成!
✅ 成功修复: {success_count}/{total_count}
"""
        )

        return success_count == total_count


if __name__ == "__main__":
    fixer = FrontendSyntaxFixer(".")
    fixer.run_fixes()
