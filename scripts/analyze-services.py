#!/usr/bin/env python3
"""
索克生活微服务分析工具
分析当前微服务架构并提供合并建议
"""

import os
import json
import subprocess
from pathlib import Path
from collections import defaultdict

class ServiceAnalyzer:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.services_dir = self.project_root / "services"
        self.analysis_result = {
            "total_services": 0,
            "services": [],
            "merge_recommendations": [],
            "size_analysis": {},
            "dependency_analysis": {}
        }
    
    def analyze_service_size(self, service_path):
        """分析服务大小"""
        try:
            # 统计Python文件数量
            py_files = list(service_path.rglob("*.py"))
            
            # 统计总行数
            total_lines = 0
            for py_file in py_files:
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        total_lines += len(f.readlines())
                except:
                    pass
            
            # 获取目录大小
            result = subprocess.run(['du', '-sh', str(service_path)], 
                                  capture_output=True, text=True)
            size_str = result.stdout.split()[0] if result.stdout else "0K"
            
            return {
                "python_files": len(py_files),
                "total_lines": total_lines,
                "disk_size": size_str
            }
        except Exception as e:
            return {"error": str(e)}
    
    def detect_service_type(self, service_path):
        """检测服务类型"""
        service_name = service_path.name.lower()
        
        if "agent" in service_name:
            return "agent"
        elif "diagnostic" in service_name:
            return "diagnostic"
        elif "auth" in service_name or "user" in service_name:
            return "auth"
        elif "data" in service_name or "health" in service_name:
            return "data"
        elif "blockchain" in service_name:
            return "blockchain"
        elif "api" in service_name or "gateway" in service_name:
            return "gateway"
        elif "message" in service_name or "rag" in service_name:
            return "communication"
        else:
            return "utility"
    
    def analyze_dependencies(self, service_path):
        """分析服务依赖"""
        dependencies = []
        
        # 检查requirements.txt
        req_file = service_path / "requirements.txt"
        if req_file.exists():
            try:
                with open(req_file, 'r') as f:
                    dependencies = [line.strip() for line in f.readlines() 
                                  if line.strip() and not line.startswith('#')]
            except:
                pass
        
        # 检查pyproject.toml
        pyproject_file = service_path / "pyproject.toml"
        if pyproject_file.exists():
            dependencies.append("pyproject.toml found")
        
        return dependencies
    
    def analyze_all_services(self):
        """分析所有微服务"""
        if not self.services_dir.exists():
            print(f"❌ 服务目录不存在: {self.services_dir}")
            return
        
        services_by_type = defaultdict(list)
        
        for service_dir in self.services_dir.iterdir():
            if service_dir.is_dir() and not service_dir.name.startswith('.'):
                print(f"📊 分析服务: {service_dir.name}")
                
                service_info = {
                    "name": service_dir.name,
                    "path": str(service_dir),
                    "type": self.detect_service_type(service_dir),
                    "size": self.analyze_service_size(service_dir),
                    "dependencies": self.analyze_dependencies(service_dir),
                    "has_dockerfile": (service_dir / "Dockerfile").exists(),
                    "has_tests": any((service_dir / test_dir).exists() 
                                   for test_dir in ["test", "tests"]),
                    "has_api": (service_dir / "api").exists(),
                    "has_config": any((service_dir / config_file).exists()
                                    for config_file in ["config", "config.yml", "config.json"])
                }
                
                self.analysis_result["services"].append(service_info)
                services_by_type[service_info["type"]].append(service_info)
        
        self.analysis_result["total_services"] = len(self.analysis_result["services"])
        
        # 生成合并建议
        self.generate_merge_recommendations(services_by_type)
        
        return self.analysis_result
    
    def generate_merge_recommendations(self, services_by_type):
        """生成服务合并建议"""
        recommendations = []
        
        # Agent服务合并建议
        if "agent" in services_by_type and len(services_by_type["agent"]) > 1:
            agent_services = [s["name"] for s in services_by_type["agent"]]
            recommendations.append({
                "type": "merge",
                "category": "agent",
                "services": agent_services,
                "target": "agent-orchestration-service",
                "reason": "四个智能体服务可以合并为一个编排服务",
                "priority": "high"
            })
        
        # 诊断服务合并建议
        if "diagnostic" in services_by_type and len(services_by_type["diagnostic"]) > 1:
            diagnostic_services = [s["name"] for s in services_by_type["diagnostic"]]
            recommendations.append({
                "type": "merge",
                "category": "diagnostic",
                "services": diagnostic_services,
                "target": "tcm-diagnostic-service",
                "reason": "五诊服务可以合并为一个中医诊断服务",
                "priority": "high"
            })
        
        # 认证和用户服务合并
        auth_services = []
        if "auth" in services_by_type:
            auth_services.extend([s["name"] for s in services_by_type["auth"]])
        
        if len(auth_services) > 1:
            recommendations.append({
                "type": "merge",
                "category": "auth",
                "services": auth_services,
                "target": "user-management-service",
                "reason": "认证和用户管理可以合并",
                "priority": "medium"
            })
        
        # 数据服务合并
        if "data" in services_by_type and len(services_by_type["data"]) > 1:
            data_services = [s["name"] for s in services_by_type["data"]]
            recommendations.append({
                "type": "merge",
                "category": "data",
                "services": data_services,
                "target": "health-data-service",
                "reason": "健康数据相关服务可以合并",
                "priority": "medium"
            })
        
        self.analysis_result["merge_recommendations"] = recommendations
    
    def generate_report(self):
        """生成分析报告"""
        report = []
        report.append("# 索克生活微服务架构分析报告\n")
        report.append(f"📊 **总服务数量**: {self.analysis_result['total_services']}\n")
        
        # 按类型统计
        type_count = defaultdict(int)
        for service in self.analysis_result["services"]:
            type_count[service["type"]] += 1
        
        report.append("## 服务类型分布\n")
        for service_type, count in type_count.items():
            report.append(f"- **{service_type}**: {count}个服务")
        report.append("")
        
        # 大小分析
        report.append("## 服务规模分析\n")
        total_py_files = sum(s["size"].get("python_files", 0) 
                           for s in self.analysis_result["services"])
        total_lines = sum(s["size"].get("total_lines", 0) 
                        for s in self.analysis_result["services"])
        
        report.append(f"- **总Python文件数**: {total_py_files:,}")
        report.append(f"- **总代码行数**: {total_lines:,}")
        report.append("")
        
        # 合并建议
        report.append("## 🎯 服务合并建议\n")
        for rec in self.analysis_result["merge_recommendations"]:
            report.append(f"### {rec['target']}")
            report.append(f"- **合并服务**: {', '.join(rec['services'])}")
            report.append(f"- **原因**: {rec['reason']}")
            report.append(f"- **优先级**: {rec['priority']}")
            report.append("")
        
        # 详细服务列表
        report.append("## 📋 详细服务列表\n")
        for service in sorted(self.analysis_result["services"], 
                            key=lambda x: x["size"].get("total_lines", 0), reverse=True):
            report.append(f"### {service['name']}")
            report.append(f"- **类型**: {service['type']}")
            report.append(f"- **Python文件**: {service['size'].get('python_files', 0)}")
            report.append(f"- **代码行数**: {service['size'].get('total_lines', 0):,}")
            report.append(f"- **磁盘大小**: {service['size'].get('disk_size', 'N/A')}")
            report.append(f"- **有Dockerfile**: {'✅' if service['has_dockerfile'] else '❌'}")
            report.append(f"- **有测试**: {'✅' if service['has_tests'] else '❌'}")
            report.append("")
        
        return "\n".join(report)
    
    def save_report(self, filename="SERVICE_ANALYSIS_REPORT.md"):
        """保存分析报告"""
        report_content = self.generate_report()
        report_path = self.project_root / filename
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"📄 分析报告已保存: {report_path}")
        return report_path

def main():
    project_root = os.getcwd()
    analyzer = ServiceAnalyzer(project_root)
    
    print("🔍 开始分析索克生活微服务架构...")
    result = analyzer.analyze_all_services()
    
    if result:
        print(f"\n📊 分析完成!")
        print(f"- 总服务数量: {result['total_services']}")
        print(f"- 合并建议数量: {len(result['merge_recommendations'])}")
        
        # 保存报告
        report_path = analyzer.save_report()
        
        # 保存JSON数据
        json_path = Path(project_root) / "service_analysis.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"📄 JSON数据已保存: {json_path}")
        
        print(f"\n📖 查看完整报告: cat {report_path.name}")
    else:
        print("❌ 分析失败")

if __name__ == "__main__":
    main() 