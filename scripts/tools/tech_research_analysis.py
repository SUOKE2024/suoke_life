#!/usr/bin/env python3
"""
技术调研分析脚本
深入研究推荐的核心项目，分析其架构模式和最佳实践
"""

import requests
import json
import os
from typing import Dict, List, Any
import time

class TechResearchAnalyzer:
    def __init__(self, token: str = None):
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "SuokeLife-TechResearch"
        }
        if token:
            self.headers["Authorization"] = f"token {token}"

    def get_repository_details(self, owner: str, repo: str) -> Dict:
        """获取仓库详细信息"""
        url = f"{self.base_url}/repos/{owner}/{repo}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"获取仓库详情失败: {e}")
            return {}

    def get_repository_structure(self, owner: str, repo: str, path: str = "") -> List[Dict]:
        """获取仓库目录结构"""
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"获取目录结构失败: {e}")
            return []

    def get_file_content(self, owner: str, repo: str, path: str) -> str:
        """获取文件内容"""
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            content = response.json()
            if content.get('encoding') == 'base64':
                import base64
                return base64.b64decode(content['content']).decode('utf-8')
            return content.get('content', '')
        except requests.RequestException as e:
            print(f"获取文件内容失败: {e}")
            return ""

    def analyze_project_architecture(self, owner: str, repo: str) -> Dict:
        """分析项目架构"""
        print(f"\n🔍 分析项目: {owner}/{repo}")
        print("=" * 50)

        # 获取基本信息
        repo_info = self.get_repository_details(owner, repo)
        if not repo_info:
            return {}

        analysis = {
            "name": f"{owner}/{repo}",
            "description": repo_info.get("description", ""),
            "language": repo_info.get("language", ""),
            "stars": repo_info.get("stargazers_count", 0),
            "forks": repo_info.get("forks_count", 0),
            "size": repo_info.get("size", 0),
            "topics": repo_info.get("topics", []),
            "architecture_patterns": [],
            "tech_stack": [],
            "best_practices": [],
            "directory_structure": {},
            "key_files": {}
        }

        # 获取目录结构
        root_contents = self.get_repository_structure(owner, repo)
        analysis["directory_structure"] = self._analyze_directory_structure(root_contents)

        # 分析关键文件
        key_files = ["README.md", "package.json", "go.mod", "requirements.txt",
                    "Dockerfile", "docker-compose.yml", "Makefile", "pyproject.toml"]

        for file_name in key_files:
            for item in root_contents:
                if item.get("name") == file_name:
                    content = self.get_file_content(owner, repo, file_name)
                    analysis["key_files"][file_name] = self._analyze_file_content(file_name, content)
                    break

        # 分析架构模式
        analysis["architecture_patterns"] = self._identify_architecture_patterns(analysis)
        analysis["tech_stack"] = self._identify_tech_stack(analysis)
        analysis["best_practices"] = self._identify_best_practices(analysis)

        return analysis

    def _analyze_directory_structure(self, contents: List[Dict]) -> Dict:
        """分析目录结构"""
        structure = {
            "directories": [],
            "files": [],
            "patterns": []
        }

        for item in contents:
            if item.get("type") == "dir":
                structure["directories"].append(item.get("name"))
            else:
                structure["files"].append(item.get("name"))

        # 识别常见模式
        dirs = structure["directories"]
        if "cmd" in dirs and "internal" in dirs:
            structure["patterns"].append("Go Standard Project Layout")
        if "src" in dirs and "tests" in dirs:
            structure["patterns"].append("Source/Test Separation")
        if "docker" in dirs or "k8s" in dirs:
            structure["patterns"].append("Container/Kubernetes Ready")
        if "docs" in dirs:
            structure["patterns"].append("Documentation Included")
        if "examples" in dirs:
            structure["patterns"].append("Example Code Provided")

        return structure

    def _analyze_file_content(self, filename: str, content: str) -> Dict:
        """分析文件内容"""
        analysis = {"type": filename, "insights": []}

        if filename == "package.json" and content:
            try:
                package_data = json.loads(content)
                analysis["insights"].append(f"Node.js项目，依赖数量: {len(package_data.get('dependencies', {}))}")
                if "react-native" in package_data.get("dependencies", {}):
                    analysis["insights"].append("React Native移动应用")
                if "@reduxjs/toolkit" in package_data.get("dependencies", {}):
                    analysis["insights"].append("使用Redux Toolkit状态管理")
                if "typescript" in package_data.get("devDependencies", {}):
                    analysis["insights"].append("TypeScript支持")
            except:
                pass

        elif filename == "go.mod" and content:
            analysis["insights"].append("Go项目")
            if "gin" in content.lower():
                analysis["insights"].append("使用Gin Web框架")
            if "grpc" in content.lower():
                analysis["insights"].append("支持gRPC")
            if "kubernetes" in content.lower():
                analysis["insights"].append("Kubernetes集成")

        elif filename == "requirements.txt" or filename == "pyproject.toml":
            analysis["insights"].append("Python项目")
            if "fastapi" in content.lower():
                analysis["insights"].append("使用FastAPI框架")
            if "django" in content.lower():
                analysis["insights"].append("使用Django框架")
            if "langchain" in content.lower():
                analysis["insights"].append("集成LangChain")

        elif filename == "Dockerfile" and content:
            analysis["insights"].append("容器化支持")
            if "multi-stage" in content.lower() or "FROM" in content and content.count("FROM") > 1:
                analysis["insights"].append("多阶段构建")

        return analysis

    def _identify_architecture_patterns(self, analysis: Dict) -> List[str]:
        """识别架构模式"""
        patterns = []

        dirs = analysis["directory_structure"]["directories"]

        # 微服务模式
        if any(d in dirs for d in ["services", "microservices", "cmd"]):
            patterns.append("Microservices Architecture")

        # 清洁架构
        if any(d in dirs for d in ["internal", "pkg", "domain", "application"]):
            patterns.append("Clean Architecture")

        # DDD模式
        if any(d in dirs for d in ["domain", "aggregate", "entity"]):
            patterns.append("Domain Driven Design")

        # API优先
        if any(d in dirs for d in ["api", "swagger", "openapi"]):
            patterns.append("API-First Design")

        # 事件驱动
        if any(d in dirs for d in ["events", "messaging", "queue"]):
            patterns.append("Event-Driven Architecture")

        return patterns

    def _identify_tech_stack(self, analysis: Dict) -> List[str]:
        """识别技术栈"""
        tech_stack = []

        # 从语言和文件推断
        if analysis["language"] == "Go":
            tech_stack.append("Go")
        if analysis["language"] == "Python":
            tech_stack.append("Python")
        if analysis["language"] == "TypeScript":
            tech_stack.append("TypeScript")
        if analysis["language"] == "JavaScript":
            tech_stack.append("JavaScript")

        # 从关键文件推断
        if "package.json" in analysis["key_files"]:
            tech_stack.append("Node.js")
        if "go.mod" in analysis["key_files"]:
            tech_stack.append("Go Modules")
        if "requirements.txt" in analysis["key_files"] or "pyproject.toml" in analysis["key_files"]:
            tech_stack.append("Python")
        if "Dockerfile" in analysis["key_files"]:
            tech_stack.append("Docker")

        return list(set(tech_stack))

    def _identify_best_practices(self, analysis: Dict) -> List[str]:
        """识别最佳实践"""
        practices = []

        dirs = analysis["directory_structure"]["directories"]
        files = analysis["directory_structure"]["files"]

        # 文档实践
        if "README.md" in files:
            practices.append("Comprehensive Documentation")
        if "docs" in dirs:
            practices.append("Dedicated Documentation Directory")

        # 测试实践
        if any(d in dirs for d in ["test", "tests", "__tests__"]):
            practices.append("Test Coverage")

        # CI/CD实践
        if ".github" in dirs:
            practices.append("GitHub Actions CI/CD")

        # 容器化实践
        if "Dockerfile" in files:
            practices.append("Containerization")
        if "docker-compose.yml" in files:
            practices.append("Multi-Container Orchestration")

        # 配置管理
        if any(f in files for f in ["config.yml", "config.json", ".env.example"]):
            practices.append("Configuration Management")

        # 代码质量
        if any(f in files for f in [".eslintrc", ".pylintrc", "golangci.yml"]):
            practices.append("Code Quality Tools")

        return practices

def main():
    """主函数：分析推荐的核心项目"""

    # 核心推荐项目列表
    core_projects = [
        # 微服务架构
        ("Mikaelemmmm", "go-zero-looklook"),
        ("aeraki-mesh", "aeraki"),
        ("vardius", "go-api-boilerplate"),

        # React Native
        ("thecodingmachine", "react-native-boilerplate"),
        ("software-mansion", "react-native-screens"),
        ("infinitered", "ignite"),

        # AI/ML多智能体
        ("MervinPraison", "PraisonAI"),
        ("BerriAI", "litellm"),
        ("microsoft", "autogen"),

        # 架构模式
        ("mehdihadeli", "awesome-software-architecture"),
        ("DovAmir", "awesome-design-patterns"),
    ]

    analyzer = TechResearchAnalyzer()
    all_analyses = []

    print("🚀 开始深入技术调研...")
    print("分析推荐的核心项目架构模式和最佳实践")
    print("=" * 60)

    for owner, repo in core_projects:
        try:
            analysis = analyzer.analyze_project_architecture(owner, repo)
            if analysis:
                all_analyses.append(analysis)

                # 显示关键信息
                print(f"📊 {analysis['name']}")
                print(f"   描述: {analysis['description'][:100]}...")
                print(f"   语言: {analysis['language']}, ⭐{analysis['stars']}")
                print(f"   架构模式: {', '.join(analysis['architecture_patterns'])}")
                print(f"   技术栈: {', '.join(analysis['tech_stack'])}")
                print(f"   最佳实践: {', '.join(analysis['best_practices'][:3])}...")
                print()

            # 避免API限制
            time.sleep(2)

        except Exception as e:
            print(f"❌ 分析 {owner}/{repo} 失败: {e}")
            continue

    # 保存详细分析结果
    output_file = "tech_research_analysis.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_analyses, f, ensure_ascii=False, indent=2)

    print(f"✅ 技术调研完成！详细分析已保存到: {output_file}")

    # 生成总结报告
    generate_summary_report(all_analyses)

def generate_summary_report(analyses: List[Dict]):
    """生成总结报告"""
    print("\n" + "="*60)
    print("📋 技术调研总结报告")
    print("="*60)

    # 统计架构模式
    all_patterns = []
    for analysis in analyses:
        all_patterns.extend(analysis.get("architecture_patterns", []))

    pattern_counts = {}
    for pattern in all_patterns:
        pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1

    print("\n🏗️ 最常见的架构模式:")
    for pattern, count in sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {pattern}: {count}个项目")

    # 统计技术栈
    all_tech = []
    for analysis in analyses:
        all_tech.extend(analysis.get("tech_stack", []))

    tech_counts = {}
    for tech in all_tech:
        tech_counts[tech] = tech_counts.get(tech, 0) + 1

    print("\n💻 最常用的技术栈:")
    for tech, count in sorted(tech_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {tech}: {count}个项目")

    # 统计最佳实践
    all_practices = []
    for analysis in analyses:
        all_practices.extend(analysis.get("best_practices", []))

    practice_counts = {}
    for practice in all_practices:
        practice_counts[practice] = practice_counts.get(practice, 0) + 1

    print("\n✨ 最常见的最佳实践:")
    for practice, count in sorted(practice_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {practice}: {count}个项目")

if __name__ == "__main__":
    main()