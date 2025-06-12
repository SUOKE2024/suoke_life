#!/usr/bin/env python3
"""
索克生活微服务全面分析和测试脚本

深入分析各微服务的代码结构、实现质量和功能完整性
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import importlib.util

class ServiceAnalyzer:
    """微服务分析器"""
    
    def __init__(self):
        self.services_root = Path(".")
        self.analysis_results = {}
        
    def analyze_all_services(self) -> Dict[str, Any]:
        """分析所有微服务"""
        
        services = {
            "agent-services": {
                "xiaoai-service": "agent-services/xiaoai-service",
                "xiaoke-service": "agent-services/xiaoke-service", 
                "laoke-service": "agent-services/laoke-service",
                "soer-service": "agent-services/soer-service"
            },
            "core-services": {
                "api-gateway": "api-gateway",
                "user-management-service": "user-management-service",
                "blockchain-service": "blockchain-service",
                "ai-model-service": "ai-model-service"
            },
            "data-services": {
                "unified-health-data-service": "unified-health-data-service",
                "unified-knowledge-service": "unified-knowledge-service",
                "communication-service": "communication-service"
            },
            "support-services": {
                "unified-support-service": "unified-support-service",
                "utility-services": "utility-services",
                "diagnostic-services": "diagnostic-services"
            }
        }
        
        analysis_report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {},
            "services": {},
            "recommendations": []
        }
        
        total_services = 0
        functional_services = 0
        
        for category, service_list in services.items():
            print(f"\n🔍 分析 {category} 类别服务:")
            category_results = {}
            
            for service_name, service_path in service_list.items():
                total_services+=1
                print(f"  📦 分析 {service_name}...")
                
                service_analysis = self.analyze_single_service(service_name, service_path)
                category_results[service_name] = service_analysis
                
                if service_analysis["status"] in ["functional", "excellent"]:
                    functional_services+=1
                    
            analysis_report["services"][category] = category_results
        
        # 生成总结
        analysis_report["summary"] = {
            "total_services": total_services,
            "functional_services": functional_services,
            "functionality_rate": (functional_services / total_services * 100) if total_services > 0 else 0,
            "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 生成建议
        analysis_report["recommendations"] = self.generate_recommendations(analysis_report)
        
        return analysis_report
    
    def analyze_single_service(self, service_name: str, service_path: str) -> Dict[str, Any]:
        """分析单个微服务"""
        
        analysis = {
            "name": service_name,
            "path": service_path,
            "status": "unknown",
            "structure": {},
            "implementation": {},
            "tests": {},
            "issues": [],
            "strengths": []
        }
        
        # 检查服务目录是否存在
        if not os.path.exists(service_path):
            analysis["status"] = "missing"
            analysis["issues"].append("服务目录不存在")
            return analysis
        
        # 分析目录结构
        analysis["structure"] = self.analyze_directory_structure(service_path)
        
        # 分析实现质量
        analysis["implementation"] = self.analyze_implementation(service_path, service_name)
        
        # 分析测试覆盖
        analysis["tests"] = self.analyze_tests(service_path)
        
        # 确定服务状态
        analysis["status"] = self.determine_service_status(analysis)
        
        # 识别优势和问题
        analysis["strengths"], analysis["issues"] = self.identify_strengths_and_issues(analysis)
        
        return analysis
    
    def analyze_directory_structure(self, service_path: str) -> Dict[str, Any]:
        """分析目录结构"""
        
        structure = {
            "has_main_module": False,
            "has_config": False,
            "has_tests": False,
            "has_docs": False,
            "has_dockerfile": False,
            "has_requirements": False,
            "python_files_count": 0,
            "directories": [],
            "key_files": []
        }
        
        try:
            for root, dirs, files in os.walk(service_path):
                # 记录目录
                rel_path = os.path.relpath(root, service_path)
                if rel_path!=".":
                    structure["directories"].append(rel_path)
                
                # 检查关键文件
                for file in files:
                    if file.endswith(".py"):
                        structure["python_files_count"]+=1
                        
                        # 检查主模块
                        if file in ["__init__.py", "main.py", "app.py"]:
                            structure["has_main_module"] = True
                            structure["key_files"].append(os.path.join(rel_path, file))
                    
                    elif file in ["Dockerfile", "Dockerfile.optimized"]:
                        structure["has_dockerfile"] = True
                        structure["key_files"].append(os.path.join(rel_path, file))
                    
                    elif file in ["requirements.txt", "pyproject.toml", "uv.lock"]:
                        structure["has_requirements"] = True
                        structure["key_files"].append(os.path.join(rel_path, file))
                    
                    elif file in ["README.md", "README.rst"]:
                        structure["has_docs"] = True
                        structure["key_files"].append(os.path.join(rel_path, file))
                
                # 检查关键目录
                if "config" in dirs:
                    structure["has_config"] = True
                if "tests" in dirs or "test" in dirs:
                    structure["has_tests"] = True
                    
        except Exception as e:
            structure["error"] = str(e)
        
        return structure
    
    def analyze_implementation(self, service_path: str, service_name: str) -> Dict[str, Any]:
        """分析实现质量"""
        
        implementation = {
            "import_success": False,
            "syntax_errors": 0,
            "code_quality": "unknown",
            "main_classes": [],
            "dependencies": [],
            "core_modules": []
        }
        
        # 测试导入
        try:
            # 根据服务类型查找主模块
            main_module_candidates = []
            
            if "agent-services" in service_path:
                # 智能体服务的特殊结构
                agent_name = service_name.replace("-service", "")
                main_module_candidates = [
                    os.path.join(service_path, agent_name, "__init__.py"),
                    os.path.join(service_path, agent_name, "core", "__init__.py"),
                    os.path.join(service_path, "__init__.py")
                ]
            else:
                # 其他服务的标准结构
                service_module = service_name.replace("-", "_")
                main_module_candidates = [
                    os.path.join(service_path, service_module, "__init__.py"),
                    os.path.join(service_path, "src", service_module, "__init__.py"),
                    os.path.join(service_path, "__init__.py"),
                    os.path.join(service_path, "main.py"),
                    os.path.join(service_path, "app.py")
                ]
            
            for module_path in main_module_candidates:
                if os.path.exists(module_path):
                    implementation["core_modules"].append(module_path)
                    # 简单的语法检查
                    try:
                        with open(module_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            compile(content, module_path, 'exec')
                            implementation["import_success"] = True
                            
                            # 提取类名
                            lines = content.split('\n')
                            for line in lines:
                                if line.strip().startswith('class '):
                                    class_name = line.strip().split()[1].split('(')[0].rstrip(':')
                                    implementation["main_classes"].append(class_name)
                                    
                    except SyntaxError as e:
                        implementation["syntax_errors"]+=1
                        
        except Exception as e:
            implementation["import_error"] = str(e)
        
        # 检查依赖文件
        requirements_files = [
            os.path.join(service_path, "requirements.txt"),
            os.path.join(service_path, "pyproject.toml")
        ]
        
        for req_file in requirements_files:
            if os.path.exists(req_file):
                try:
                    with open(req_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if "requirements.txt" in req_file:
                            deps = [line.strip() for line in content.split('\n') 
                                   if line.strip() and not line.startswith('#')]
                            implementation["dependencies"].extend(deps[:10])  # 限制显示数量
                except Exception:
                    pass
        
        return implementation
    
    def analyze_tests(self, service_path: str) -> Dict[str, Any]:
        """分析测试覆盖"""
        
        tests = {
            "has_tests": False,
            "test_files_count": 0,
            "test_directories": [],
            "test_frameworks": []
        }
        
        test_dirs = ["tests", "test"]
        
        for test_dir in test_dirs:
            test_path = os.path.join(service_path, test_dir)
            if os.path.exists(test_path):
                tests["has_tests"] = True
                tests["test_directories"].append(test_dir)
                
                # 统计测试文件
                for root, dirs, files in os.walk(test_path):
                    for file in files:
                        if file.startswith("test_") and file.endswith(".py"):
                            tests["test_files_count"]+=1
        
        # 检查测试框架
        config_files = [
            os.path.join(service_path, "pytest.ini"),
            os.path.join(service_path, "pyproject.toml"),
            os.path.join(service_path, "conftest.py")
        ]
        
        for config_file in config_files:
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        content = f.read().lower()
                        if "pytest" in content:
                            tests["test_frameworks"].append("pytest")
                        if "unittest" in content:
                            tests["test_frameworks"].append("unittest")
                except Exception:
                    pass
        
        return tests
    
    def determine_service_status(self, analysis: Dict[str, Any]) -> str:
        """确定服务状态"""
        
        structure = analysis["structure"]
        implementation = analysis["implementation"]
        tests = analysis["tests"]
        
        # 计算功能完整性分数
        score = 0
        
        # 结构分数 (40%)
        if structure.get("has_main_module"):
            score+=10
        if structure.get("has_config"):
            score+=5
        if structure.get("has_dockerfile"):
            score+=5
        if structure.get("has_requirements"):
            score+=5
        if structure.get("python_files_count", 0) > 5:
            score+=10
        if structure.get("has_docs"):
            score+=5
        
        # 实现分数 (40%)
        if implementation.get("import_success"):
            score+=20
        if implementation.get("syntax_errors", 0)==0:
            score+=10
        if len(implementation.get("dependencies", [])) > 0:
            score+=10
        
        # 测试分数 (20%)
        if tests.get("has_tests"):
            score+=10
        if tests.get("test_files_count", 0) > 0:
            score+=10
        
        # 确定状态
        if score>=80:
            return "excellent"
        elif score>=60:
            return "functional"
        elif score>=40:
            return "developing"
        elif score>=20:
            return "basic"
        else:
            return "incomplete"
    
    def identify_strengths_and_issues(self, analysis: Dict[str, Any]) -> tuple[List[str], List[str]]:
        """识别优势和问题"""
        
        strengths = []
        issues = []
        
        structure = analysis["structure"]
        implementation = analysis["implementation"]
        tests = analysis["tests"]
        
        # 识别优势
        if implementation.get("import_success"):
            strengths.append("核心模块可正常导入")
        
        if structure.get("has_dockerfile"):
            strengths.append("支持容器化部署")
        
        if structure.get("has_requirements"):
            strengths.append("依赖管理完善")
        
        if tests.get("has_tests"):
            strengths.append("包含测试代码")
        
        if structure.get("python_files_count", 0) > 10:
            strengths.append("代码结构较为完整")
        
        # 识别问题
        if not implementation.get("import_success"):
            issues.append("核心模块导入失败")
        
        if implementation.get("syntax_errors", 0) > 0:
            issues.append(f"存在 {implementation['syntax_errors']} 个语法错误")
        
        if not structure.get("has_tests"):
            issues.append("缺少测试代码")
        
        if not structure.get("has_docs"):
            issues.append("缺少文档")
        
        if not structure.get("has_config"):
            issues.append("缺少配置管理")
        
        return strengths, issues
    
    def generate_recommendations(self, analysis_report: Dict[str, Any]) -> List[str]:
        """生成优化建议"""
        
        recommendations = []
        
        # 分析整体状况
        summary = analysis_report["summary"]
        functionality_rate = summary["functionality_rate"]
        
        if functionality_rate < 50:
            recommendations.append("🔧 优先完善核心服务的基础功能实现")
        
        if functionality_rate < 80:
            recommendations.append("📝 增加服务文档和配置管理")
        
        # 分析具体服务问题
        incomplete_services = []
        missing_tests = []
        import_failed = []
        
        for category, services in analysis_report["services"].items():
            for service_name, service_data in services.items():
                if service_data["status"] in ["incomplete", "basic"]:
                    incomplete_services.append(service_name)
                
                if not service_data["tests"].get("has_tests"):
                    missing_tests.append(service_name)
                
                if not service_data["implementation"].get("import_success"):
                    import_failed.append(service_name)
        
        if incomplete_services:
            recommendations.append(f"⚠️ 需要重点优化的服务: {', '.join(incomplete_services[:5])}")
        
        if import_failed:
            recommendations.append(f"🚨 导入失败需修复的服务: {', '.join(import_failed[:5])}")
        
        if missing_tests:
            recommendations.append(f"🧪 需要添加测试的服务: {', '.join(missing_tests[:5])}")
        
        recommendations.append("🚀 建议优先完善API网关和用户管理服务作为基础设施")
        recommendations.append("🔄 建议建立持续集成和自动化测试流程")
        
        return recommendations

def main():
    """主函数"""
    
    print("🔍 索克生活微服务全面分析报告")
    print("=" * 60)
    
    analyzer = ServiceAnalyzer()
    analysis_report = analyzer.analyze_all_services()
    
    # 显示总结
    summary = analysis_report["summary"]
    print(f"\n📊 分析总结:")
    print(f"  总服务数量: {summary['total_services']}")
    print(f"  功能完整服务: {summary['functional_services']}")
    print(f"  功能完整率: {summary['functionality_rate']:.1f}%")
    
    # 显示各类别服务状态
    print(f"\n📦 各类别服务状态:")
    for category, services in analysis_report["services"].items():
        print(f"  {category}:")
        for service_name, service_data in services.items():
            status = service_data["status"]
            status_emoji = {
                "excellent": "🌟",
                "functional": "✅", 
                "developing": "🔄",
                "basic": "⚠️",
                "incomplete": "❌",
                "missing": "🚫"
            }.get(status, "❓")
            
            # 显示关键信息
            structure = service_data["structure"]
            implementation = service_data["implementation"]
            
            info_parts = []
            if structure.get("python_files_count", 0) > 0:
                info_parts.append(f"{structure['python_files_count']}个Python文件")
            if implementation.get("import_success"):
                info_parts.append("可导入")
            if len(implementation.get("main_classes", [])) > 0:
                info_parts.append(f"{len(implementation['main_classes'])}个主类")
            
            info_str = f" ({', '.join(info_parts)})" if info_parts else ""
            
            print(f"    {status_emoji} {service_name}: {status}{info_str}")
    
    # 显示建议
    print(f"\n💡 优化建议:")
    for i, recommendation in enumerate(analysis_report["recommendations"], 1):
        print(f"  {i}. {recommendation}")
    
    # 保存详细报告
    report_file = f"service_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 详细报告已保存到: {report_file}")
    
    # 总体评估
    functionality_rate = summary['functionality_rate']
    if functionality_rate>=80:
        print(f"\n🎉 微服务架构整体状况良好！")
    elif functionality_rate>=60:
        print(f"\n👍 微服务架构基本可用，继续优化中...")
    elif functionality_rate>=40:
        print(f"\n🔧 微服务架构需要进一步完善")
    else:
        print(f"\n⚠️ 微服务架构需要大量开发工作")

if __name__=="__main__":
    main() 