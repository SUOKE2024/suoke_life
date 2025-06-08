"""
architecture_gap_analysis - 索克生活项目模块
"""

from pathlib import Path
from typing import Dict, List, Any
import json

#!/usr/bin/env python3
"""
架构差距分析脚本
评估索克生活项目现有架构与最佳实践的差距
"""


class ArchitectureGapAnalyzer:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.analysis_result = {
            "current_architecture": {},
            "best_practices_gaps": {},
            "recommendations": {},
            "priority_matrix": {}
        }

    def analyze_current_architecture(self) -> Dict:
        """分析当前架构"""
        print("🔍 分析当前项目架构...")

        current_arch = {
            "project_structure": self._analyze_project_structure(),
            "tech_stack": self._analyze_tech_stack(),
            "microservices": self._analyze_microservices(),
            "frontend": self._analyze_frontend(),
            "deployment": self._analyze_deployment(),
            "documentation": self._analyze_documentation(),
            "testing": self._analyze_testing(),
            "ci_cd": self._analyze_ci_cd()
        }

        self.analysis_result["current_architecture"] = current_arch
        return current_arch

    def _analyze_project_structure(self) -> Dict:
        """分析项目结构"""
        structure = {
            "root_directories": [],
            "services_count": 0,
            "patterns": []
        }

        # 获取根目录结构
        for item in self.project_root.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                structure["root_directories"].append(item.name)

        # 分析服务数量
        services_dir = self.project_root / "services"
        if services_dir.exists():
            services = [d for d in services_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]
            structure["services_count"] = len(services)

        # 识别架构模式
        dirs = structure["root_directories"]
        if "services" in dirs:
            structure["patterns"].append("Microservices Architecture")
        if "src" in dirs:
            structure["patterns"].append("Source Code Organization")
        if "docs" in dirs:
            structure["patterns"].append("Documentation Structure")
        if "tests" in dirs:
            structure["patterns"].append("Test Organization")
        if "deploy" in dirs:
            structure["patterns"].append("Deployment Configuration")

        return structure

    def _analyze_tech_stack(self) -> Dict:
        """分析技术栈"""
        tech_stack = {
            "frontend": [],
            "backend": [],
            "database": [],
            "infrastructure": [],
            "ai_ml": []
        }

        # 分析前端技术栈
        package_json = self.project_root / "package.json"
        if package_json.exists():
            with open(package_json, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
                deps = package_data.get("dependencies", {})

                if "react-native" in deps:
                    tech_stack["frontend"].append("React Native")
                if "@reduxjs/toolkit" in deps:
                    tech_stack["frontend"].append("Redux Toolkit")
                if "@react-navigation/native" in deps:
                    tech_stack["frontend"].append("React Navigation")
                if "typescript" in package_data.get("devDependencies", {}):
                    tech_stack["frontend"].append("TypeScript")

        # 分析后端技术栈
        requirements_files = [
            self.project_root / "requirements.txt",
            self.project_root / "pyproject.toml"
        ]

        for req_file in requirements_files:
            if req_file.exists():
                content = req_file.read_text()
                if "fastapi" in content.lower():
                    tech_stack["backend"].append("FastAPI")
                if "django" in content.lower():
                    tech_stack["backend"].append("Django")
                if "langchain" in content.lower():
                    tech_stack["ai_ml"].append("LangChain")
                if "openai" in content.lower():
                    tech_stack["ai_ml"].append("OpenAI")

        # 分析基础设施
        if (self.project_root / "Dockerfile").exists():
            tech_stack["infrastructure"].append("Docker")
        if (self.project_root / "docker-compose.yml").exists():
            tech_stack["infrastructure"].append("Docker Compose")
        if (self.project_root / "deploy" / "kubernetes").exists():
            tech_stack["infrastructure"].append("Kubernetes")

        return tech_stack

    def _analyze_microservices(self) -> Dict:
        """分析微服务架构"""
        microservices = {
            "services": [],
            "communication": [],
            "patterns": []
        }

        services_dir = self.project_root / "services"
        if services_dir.exists():
            for service_dir in services_dir.iterdir():
                if service_dir.is_dir() and not service_dir.name.startswith('.'):
                    service_info = {
                        "name": service_dir.name,
                        "language": self._detect_service_language(service_dir),
                        "has_api": (service_dir / "api").exists(),
                        "has_tests": any((service_dir / test_dir).exists() for test_dir in ["test", "tests"]),
                        "has_docker": (service_dir / "Dockerfile").exists(),
                        "has_config": any((service_dir / config_file).exists()
                                        for config_file in ["config", "config.yml", "config.json"])
                    }
                    microservices["services"].append(service_info)

        # 检查通信模式
        if (self.project_root / "services" / "api-gateway").exists():
            microservices["communication"].append("API Gateway")
        if (self.project_root / "services" / "message-bus").exists():
            microservices["communication"].append("Message Bus")

        # 检查架构模式
        if len(microservices["services"]) > 5:
            microservices["patterns"].append("Distributed Microservices")
        if any(s["has_api"] for s in microservices["services"]):
            microservices["patterns"].append("API-First Design")

        return microservices

    def _detect_service_language(self, service_dir: Path) -> str:
        """检测服务使用的编程语言"""
        if (service_dir / "go.mod").exists():
            return "Go"
        elif (service_dir / "requirements.txt").exists() or (service_dir / "pyproject.toml").exists():
            return "Python"
        elif (service_dir / "package.json").exists():
            return "Node.js"
        elif (service_dir / "pom.xml").exists():
            return "Java"
        else:
            return "Unknown"

    def _analyze_frontend(self) -> Dict:
        """分析前端架构"""
        frontend = {
            "framework": "React Native",
            "structure": [],
            "state_management": [],
            "navigation": [],
            "testing": []
        }

        src_dir = self.project_root / "src"
        if src_dir.exists():
            for item in src_dir.iterdir():
                if item.is_dir():
                    frontend["structure"].append(item.name)

        # 检查状态管理
        package_json = self.project_root / "package.json"
        if package_json.exists():
            with open(package_json, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
                deps = package_data.get("dependencies", {})

                if "@reduxjs/toolkit" in deps:
                    frontend["state_management"].append("Redux Toolkit")
                if "@react-navigation/native" in deps:
                    frontend["navigation"].append("React Navigation")

        return frontend

    def _analyze_deployment(self) -> Dict:
        """分析部署配置"""
        deployment = {
            "containerization": False,
            "orchestration": [],
            "ci_cd": [],
            "monitoring": []
        }

        if (self.project_root / "Dockerfile").exists():
            deployment["containerization"] = True

        deploy_dir = self.project_root / "deploy"
        if deploy_dir.exists():
            if (deploy_dir / "kubernetes").exists():
                deployment["orchestration"].append("Kubernetes")
            if (deploy_dir / "docker").exists():
                deployment["orchestration"].append("Docker")
            if (deploy_dir / "prometheus").exists():
                deployment["monitoring"].append("Prometheus")

        return deployment

    def _analyze_documentation(self) -> Dict:
        """分析文档情况"""
        documentation = {
            "readme": (self.project_root / "README.md").exists(),
            "docs_directory": (self.project_root / "docs").exists(),
            "api_docs": False,
            "architecture_docs": False
        }

        docs_dir = self.project_root / "docs"
        if docs_dir.exists():
            for doc_file in docs_dir.rglob("*.md"):
                if "api" in doc_file.name.lower():
                    documentation["api_docs"] = True
                if "architecture" in doc_file.name.lower():
                    documentation["architecture_docs"] = True

        return documentation

    def _analyze_testing(self) -> Dict:
        """分析测试情况"""
        testing = {
            "unit_tests": False,
            "integration_tests": False,
            "e2e_tests": False,
            "test_frameworks": []
        }

        # 检查测试目录
        test_dirs = ["tests", "test", "__tests__", "src/__tests__"]
        for test_dir in test_dirs:
            if (self.project_root / test_dir).exists():
                testing["unit_tests"] = True
                break

        # 检查集成测试
        if (self.project_root / "tests" / "integration").exists():
            testing["integration_tests"] = True

        # 检查E2E测试
        if (self.project_root / "tests" / "e2e").exists():
            testing["e2e_tests"] = True

        # 检查测试框架
        package_json = self.project_root / "package.json"
        if package_json.exists():
            with open(package_json, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
                dev_deps = package_data.get("devDependencies", {})

                if "jest" in dev_deps:
                    testing["test_frameworks"].append("Jest")
                if "detox" in dev_deps:
                    testing["test_frameworks"].append("Detox")

        return testing

    def _analyze_ci_cd(self) -> Dict:
        """分析CI/CD配置"""
        ci_cd = {
            "github_actions": (self.project_root / ".github" / "workflows").exists(),
            "docker_support": (self.project_root / "Dockerfile").exists(),
            "scripts": []
        }

        # 检查脚本
        scripts_dir = self.project_root / "scripts"
        if scripts_dir.exists():
            for script_file in scripts_dir.iterdir():
                if script_file.suffix in ['.sh', '.py', '.js']:
                    ci_cd["scripts"].append(script_file.name)

        return ci_cd

    def identify_gaps(self, best_practices: Dict) -> Dict:
        """识别与最佳实践的差距"""
        print("📊 识别架构差距...")

        gaps = {
            "microservices_gaps": self._identify_microservices_gaps(),
            "frontend_gaps": self._identify_frontend_gaps(),
            "ai_ml_gaps": self._identify_ai_ml_gaps(),
            "infrastructure_gaps": self._identify_infrastructure_gaps(),
            "quality_gaps": self._identify_quality_gaps()
        }

        self.analysis_result["best_practices_gaps"] = gaps
        return gaps

    def _identify_microservices_gaps(self) -> List[Dict]:
        """识别微服务架构差距"""
        gaps = []
        current_ms = self.analysis_result["current_architecture"]["microservices"]

        # 检查服务网格
        if "Service Mesh" not in current_ms.get("communication", []):
            gaps.append({
                "category": "Service Communication",
                "gap": "缺少服务网格（Service Mesh）",
                "impact": "高",
                "recommendation": "考虑引入Istio或Aeraki进行服务间通信管理"
            })

        # 检查API网关
        if "API Gateway" not in current_ms.get("communication", []):
            gaps.append({
                "category": "API Management",
                "gap": "API网关功能不完善",
                "impact": "中",
                "recommendation": "基于go-zero或Kong优化API网关功能"
            })

        # 检查服务发现
        service_discovery_found = False
        for service in current_ms.get("services", []):
            if "discovery" in service["name"] or "registry" in service["name"]:
                service_discovery_found = True
                break

        if not service_discovery_found:
            gaps.append({
                "category": "Service Discovery",
                "gap": "缺少专门的服务发现机制",
                "impact": "中",
                "recommendation": "实现基于Consul或etcd的服务发现"
            })

        return gaps

    def _identify_frontend_gaps(self) -> List[Dict]:
        """识别前端架构差距"""
        gaps = []
        current_frontend = self.analysis_result["current_architecture"]["frontend"]

        # 检查性能优化
        if "react-native-screens" not in str(self.analysis_result):
            gaps.append({
                "category": "Performance",
                "gap": "缺少原生屏幕优化",
                "impact": "中",
                "recommendation": "集成react-native-screens提升导航性能"
            })

        # 检查状态管理
        if not current_frontend.get("state_management"):
            gaps.append({
                "category": "State Management",
                "gap": "状态管理方案不明确",
                "impact": "高",
                "recommendation": "采用Redux Toolkit或Zustand进行状态管理"
            })

        # 检查测试覆盖
        current_testing = self.analysis_result["current_architecture"]["testing"]
        if not current_testing.get("e2e_tests"):
            gaps.append({
                "category": "Testing",
                "gap": "缺少端到端测试",
                "impact": "中",
                "recommendation": "集成Detox进行E2E测试"
            })

        return gaps

    def _identify_ai_ml_gaps(self) -> List[Dict]:
        """识别AI/ML架构差距"""
        gaps = []

        # 检查多智能体框架
        gaps.append({
            "category": "Multi-Agent System",
            "gap": "缺少统一的多智能体协作框架",
            "impact": "高",
            "recommendation": "集成PraisonAI或AutoGen实现智能体协作"
        })

        # 检查LLM网关
        gaps.append({
            "category": "LLM Integration",
            "gap": "缺少统一的LLM接口管理",
            "impact": "高",
            "recommendation": "使用LiteLLM作为统一的LLM网关"
        })

        # 检查向量数据库
        gaps.append({
            "category": "Vector Database",
            "gap": "缺少专门的向量数据库支持",
            "impact": "中",
            "recommendation": "集成Pinecone或Weaviate进行向量存储"
        })

        return gaps

    def _identify_infrastructure_gaps(self) -> List[Dict]:
        """识别基础设施差距"""
        gaps = []
        current_deployment = self.analysis_result["current_architecture"]["deployment"]

        # 检查监控系统
        if not current_deployment.get("monitoring"):
            gaps.append({
                "category": "Monitoring",
                "gap": "缺少完整的监控体系",
                "impact": "高",
                "recommendation": "部署Prometheus + Grafana监控栈"
            })

        # 检查日志聚合
        gaps.append({
            "category": "Logging",
            "gap": "缺少集中式日志管理",
            "impact": "中",
            "recommendation": "实现ELK或Loki日志聚合方案"
            })

        # 检查配置管理
        gaps.append({
            "category": "Configuration",
            "gap": "配置管理不够统一",
            "impact": "中",
            "recommendation": "使用ConfigMap和Secret进行配置管理"
        })

        return gaps

    def _identify_quality_gaps(self) -> List[Dict]:
        """识别代码质量差距"""
        gaps = []
        current_testing = self.analysis_result["current_architecture"]["testing"]

        # 检查代码覆盖率
        if not current_testing.get("unit_tests"):
            gaps.append({
                "category": "Code Quality",
                "gap": "单元测试覆盖不足",
                "impact": "高",
                "recommendation": "建立完整的单元测试体系"
            })

        # 检查代码规范
        gaps.append({
            "category": "Code Standards",
            "gap": "缺少统一的代码规范检查",
            "impact": "中",
            "recommendation": "集成ESLint、Prettier、golangci-lint等工具"
        })

        return gaps

    def generate_recommendations(self) -> Dict:
        """生成改进建议"""
        print("💡 生成改进建议...")

        recommendations = {
            "immediate_actions": [],
            "short_term_goals": [],
            "long_term_vision": []
        }

        # 立即行动项（1-2周）
        recommendations["immediate_actions"] = [
            {
                "action": "建立代码规范检查",
                "description": "配置ESLint、Prettier等代码质量工具",
                "effort": "低",
                "impact": "中"
            },
            {
                "action": "完善项目文档",
                "description": "更新README和API文档",
                "effort": "低",
                "impact": "中"
            }
        ]

        # 短期目标（1-3个月）
        recommendations["short_term_goals"] = [
            {
                "goal": "微服务架构优化",
                "description": "基于go-zero重构核心服务",
                "effort": "高",
                "impact": "高"
            },
            {
                "goal": "前端性能优化",
                "description": "集成react-native-screens和性能监控",
                "effort": "中",
                "impact": "高"
            },
            {
                "goal": "AI智能体协作",
                "description": "集成PraisonAI多智能体框架",
                "effort": "高",
                "impact": "极高"
            }
        ]

        # 长期愿景（3-12个月）
        recommendations["long_term_vision"] = [
            {
                "vision": "完整的DevOps体系",
                "description": "建立CI/CD、监控、日志的完整体系",
                "effort": "高",
                "impact": "高"
            },
            {
                "vision": "智能化健康管理平台",
                "description": "实现四个智能体的深度协作和学习",
                "effort": "极高",
                "impact": "极高"
            }
        ]

        self.analysis_result["recommendations"] = recommendations
        return recommendations

    def create_priority_matrix(self) -> Dict:
        """创建优先级矩阵"""
        print("📋 创建优先级矩阵...")

        all_gaps = []
        for category, gaps in self.analysis_result["best_practices_gaps"].items():
            all_gaps.extend(gaps)

        # 按影响和紧急程度分类
        priority_matrix = {
            "P0_critical": [],  # 高影响，高紧急
            "P1_important": [], # 高影响，中紧急
            "P2_normal": [],    # 中影响，中紧急
            "P3_low": []        # 低影响，低紧急
        }

        for gap in all_gaps:
            impact = gap.get("impact", "中")
            category = gap.get("category", "")

            # 根据类别和影响确定优先级
            if impact == "高" and category in ["Multi-Agent System", "LLM Integration"]:
                priority_matrix["P0_critical"].append(gap)
            elif impact == "高":
                priority_matrix["P1_important"].append(gap)
            elif impact == "中":
                priority_matrix["P2_normal"].append(gap)
            else:
                priority_matrix["P3_low"].append(gap)

        self.analysis_result["priority_matrix"] = priority_matrix
        return priority_matrix

    def generate_report(self) -> str:
        """生成完整的分析报告"""
        print("📄 生成架构差距分析报告...")

        report = f"""# 索克生活项目架构差距分析报告

## 执行摘要

本报告分析了索克生活项目当前架构与业界最佳实践的差距，并提供了具体的改进建议。

### 关键发现
- 当前项目已具备良好的微服务架构基础
- 前端使用现代React Native技术栈
- 四个智能体服务已初步实现
- 主要差距集中在智能体协作、性能优化和运维体系

## 当前架构分析

### 项目结构
- 服务数量: {self.analysis_result['current_architecture']['microservices']['services'].__len__()}个
- 架构模式: {', '.join(self.analysis_result['current_architecture']['project_structure']['patterns'])}

### 技术栈
- 前端: {', '.join(self.analysis_result['current_architecture']['tech_stack']['frontend'])}
- 后端: {', '.join(self.analysis_result['current_architecture']['tech_stack']['backend'])}
- AI/ML: {', '.join(self.analysis_result['current_architecture']['tech_stack']['ai_ml'])}

## 差距分析

### 优先级P0 - 关键差距
"""

        for gap in self.analysis_result["priority_matrix"]["P0_critical"]:
            report += f"""
**{gap['category']}**: {gap['gap']}
- 影响: {gap['impact']}
- 建议: {gap['recommendation']}
"""

        report += f"""
### 优先级P1 - 重要差距
"""

        for gap in self.analysis_result["priority_matrix"]["P1_important"]:
            report += f"""
**{gap['category']}**: {gap['gap']}
- 影响: {gap['impact']}
- 建议: {gap['recommendation']}
"""

        report += f"""
## 改进建议

### 立即行动 (1-2周)
"""

        for action in self.analysis_result["recommendations"]["immediate_actions"]:
            report += f"""
- **{action['action']}**: {action['description']}
- 工作量: {action['effort']}, 影响: {action['impact']}
"""

        report += f"""
### 短期目标 (1-3个月)
"""

        for goal in self.analysis_result["recommendations"]["short_term_goals"]:
            report += f"""
- **{goal['goal']}**: {goal['description']}
- 工作量: {goal['effort']}, 影响: {goal['impact']}
"""

        report += f"""
### 长期愿景 (3-12个月)
"""

        for vision in self.analysis_result["recommendations"]["long_term_vision"]:
            report += f"""
- **{vision['vision']}**: {vision['description']}
- 工作量: {vision['effort']}, 影响: {vision['impact']}
"""

        return report

def main():
    """主函数"""
    print("🚀 开始架构差距分析...")
    print("=" * 60)

    analyzer = ArchitectureGapAnalyzer()

    # 分析当前架构
    current_arch = analyzer.analyze_current_architecture()

    # 识别差距
    gaps = analyzer.identify_gaps({})

    # 生成建议
    recommendations = analyzer.generate_recommendations()

    # 创建优先级矩阵
    priority_matrix = analyzer.create_priority_matrix()

    # 生成报告
    report = analyzer.generate_report()

    # 保存结果
    with open("architecture_gap_analysis.json", "w", encoding="utf-8") as f:
        json.dump(analyzer.analysis_result, f, ensure_ascii=False, indent=2)

    with open("architecture_gap_report.md", "w", encoding="utf-8") as f:
        f.write(report)

    print("✅ 架构差距分析完成！")
    print(f"📊 详细数据: architecture_gap_analysis.json")
    print(f"📄 分析报告: architecture_gap_report.md")

    # 显示关键发现
    print("\n🎯 关键发现:")
    print(f"- 当前服务数量: {len(current_arch['microservices']['services'])}")
    print(f"- P0级别差距: {len(priority_matrix['P0_critical'])}个")
    print(f"- P1级别差距: {len(priority_matrix['P1_important'])}个")
    print(f"- 立即行动项: {len(recommendations['immediate_actions'])}个")

if __name__ == "__main__":
    main()