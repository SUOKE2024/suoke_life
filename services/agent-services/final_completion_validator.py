"""
final_completion_validator - 索克生活项目模块
"""

from pathlib import Path
from typing import Dict, List, Tuple
import ast
import json
import os
import subprocess

#!/usr/bin/env python3
"""
最终完成度验证脚本
验证所有服务是否达到100%完成度
"""


class FinalCompletionValidator:
    """最终完成度验证器"""
    
    def __init__(self):
        self.services = {
            "laoke-service": {"target": 100, "current": 95},
            "soer-service": {"target": 100, "current": 90},
            "xiaoke-service": {"target": 100, "current": 85},
            "xiaoai-service": {"target": 100, "current": 80}
        }
        self.validation_results = {}
        
    def validate_all_services(self) -> Dict:
        """验证所有服务"""
        print("🔍 开始最终完成度验证...")
        
        for service_name in self.services.keys():
            print(f"\n📋 验证 {service_name}...")
            result = self._validate_service(service_name)
            self.validation_results[service_name] = result
            
        return self._generate_final_report()
        
    def _validate_service(self, service_name: str) -> Dict:
        """验证单个服务"""
        service_path = Path(service_name)
        
        if not service_path.exists():
            return {
                "completion": 0,
                "status": "❌ 服务目录不存在",
                "issues": ["服务目录不存在"]
            }
            
        result = {
            "completion": 0,
            "status": "🔍 检查中",
            "issues": [],
            "achievements": []
        }
        
        # 1. 检查代码质量
        syntax_score = self._check_syntax_quality(service_path)
        result["syntax_score"] = syntax_score
        
        # 2. 检查文档完整性
        doc_score = self._check_documentation(service_path)
        result["doc_score"] = doc_score
        
        # 3. 检查测试覆盖
        test_score = self._check_test_coverage(service_path)
        result["test_score"] = test_score
        
        # 4. 检查部署就绪性
        deploy_score = self._check_deployment_readiness(service_path)
        result["deploy_score"] = deploy_score
        
        # 5. 检查功能完整性
        feature_score = self._check_feature_completeness(service_path, service_name)
        result["feature_score"] = feature_score
        
        # 计算总体完成度
        total_score = (syntax_score + doc_score + test_score + deploy_score + feature_score) / 5
        result["completion"] = total_score
        
        # 确定状态
        if total_score >= 100:
            result["status"] = "🎉 100% 完成"
        elif total_score >= 95:
            result["status"] = "✅ 基本完成"
        elif total_score >= 80:
            result["status"] = "🟡 接近完成"
        else:
            result["status"] = "🔧 需要优化"
            
        return result
        
    def _check_syntax_quality(self, service_path: Path) -> int:
        """检查语法质量"""
        python_files = list(service_path.rglob("*.py"))
        if not python_files:
            return 50
            
        syntax_errors = 0
        total_files = 0
        
        for file_path in python_files:
            if self._should_skip_file(file_path):
                continue
                
            total_files += 1
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                ast.parse(content)
            except SyntaxError:
                syntax_errors += 1
                
        if total_files == 0:
            return 50
            
        syntax_quality = max(0, 100 - (syntax_errors / total_files * 100))
        return int(syntax_quality)
        
    def _check_documentation(self, service_path: Path) -> int:
        """检查文档完整性"""
        doc_score = 0
        
        # 检查README
        if (service_path / "README.md").exists():
            doc_score += 20
            
        # 检查API文档
        api_docs = list(service_path.rglob("*api*.md")) + list(service_path.rglob("*API*.md"))
        if api_docs:
            doc_score += 25
            
        # 检查配置文档
        if (service_path / "config").exists():
            doc_score += 15
            
        # 检查部署文档
        deploy_files = list(service_path.rglob("docker*")) + list(service_path.rglob("*deploy*"))
        if deploy_files:
            doc_score += 20
            
        # 检查完成度计划
        completion_docs = list(service_path.rglob("*COMPLETION*.md")) + list(service_path.rglob("*completion*.md"))
        if completion_docs:
            doc_score += 20
            
        return min(100, doc_score)
        
    def _check_test_coverage(self, service_path: Path) -> int:
        """检查测试覆盖"""
        test_score = 0
        
        # 检查测试目录
        test_dirs = list(service_path.rglob("test*"))
        if test_dirs:
            test_score += 30
            
        # 检查测试文件
        test_files = list(service_path.rglob("test_*.py")) + list(service_path.rglob("*_test.py"))
        if test_files:
            test_score += 40
            
        # 检查性能测试
        perf_tests = [f for f in test_files if "performance" in str(f) or "perf" in str(f)]
        if perf_tests:
            test_score += 30
            
        return min(100, test_score)
        
    def _check_deployment_readiness(self, service_path: Path) -> int:
        """检查部署就绪性"""
        deploy_score = 0
        
        # 检查Dockerfile
        if (service_path / "Dockerfile").exists():
            deploy_score += 25
            
        # 检查docker-compose
        docker_compose_files = list(service_path.rglob("docker-compose*.yml"))
        if docker_compose_files:
            deploy_score += 25
            
        # 检查Kubernetes配置
        k8s_files = list(service_path.rglob("*.yaml")) + list(service_path.rglob("k8s/*"))
        if k8s_files:
            deploy_score += 25
            
        # 检查依赖文件
        dep_files = [
            service_path / "requirements.txt",
            service_path / "pyproject.toml",
            service_path / "uv.lock"
        ]
        if any(f.exists() for f in dep_files):
            deploy_score += 25
            
        return min(100, deploy_score)
        
    def _check_feature_completeness(self, service_path: Path, service_name: str) -> int:
        """检查功能完整性"""
        feature_score = 0
        
        # 基于服务类型检查特定功能
        if service_name == "laoke-service":
            # 检查知识管理功能
            if any("knowledge" in str(f) for f in service_path.rglob("*.py")):
                feature_score += 25
            # 检查学习路径功能
            if any("learning" in str(f) or "path" in str(f) for f in service_path.rglob("*.py")):
                feature_score += 25
            # 检查社区管理功能
            if any("community" in str(f) for f in service_path.rglob("*.py")):
                feature_score += 25
            # 检查A2A协作功能
            if any("a2a" in str(f) or "collaboration" in str(f) for f in service_path.rglob("*.py")):
                feature_score += 25
                
        elif service_name == "soer-service":
            # 检查营养分析功能
            if any("nutrition" in str(f) for f in service_path.rglob("*.py")):
                feature_score += 25
            # 检查健康管理功能
            if any("health" in str(f) for f in service_path.rglob("*.py")):
                feature_score += 25
            # 检查中医功能
            if any("tcm" in str(f) or "traditional" in str(f) for f in service_path.rglob("*.py")):
                feature_score += 25
            # 检查传感器集成
            if any("sensor" in str(f) or "device" in str(f) for f in service_path.rglob("*.py")):
                feature_score += 25
                
        elif service_name == "xiaoke-service":
            # 检查预约功能
            if any("appointment" in str(f) for f in service_path.rglob("*.py")):
                feature_score += 25
            # 检查产品功能
            if any("product" in str(f) for f in service_path.rglob("*.py")):
                feature_score += 25
            # 检查区块链功能
            if any("blockchain" in str(f) for f in service_path.rglob("*.py")):
                feature_score += 25
            # 检查推荐功能
            if any("recommend" in str(f) for f in service_path.rglob("*.py")):
                feature_score += 25
                
        elif service_name == "xiaoai-service":
            # 检查语音交互功能
            if any("voice" in str(f) or "speech" in str(f) for f in service_path.rglob("*.py")):
                feature_score += 25
            # 检查多模态功能
            if any("multimodal" in str(f) for f in service_path.rglob("*.py")):
                feature_score += 25
            # 检查诊断功能
            if any("diagnosis" in str(f) for f in service_path.rglob("*.py")):
                feature_score += 25
            # 检查无障碍功能
            if any("accessibility" in str(f) for f in service_path.rglob("*.py")):
                feature_score += 25
                
        return min(100, feature_score)
        
    def _should_skip_file(self, file_path: Path) -> bool:
        """判断是否跳过文件"""
        skip_patterns = [
            "__pycache__",
            ".pyc",
            "venv/",
            ".git/",
            "node_modules/"
        ]
        
        file_str = str(file_path)
        return any(pattern in file_str for pattern in skip_patterns)
        
    def _generate_final_report(self) -> Dict:
        """生成最终报告"""
        total_completion = 0
        completed_services = 0
        
        print("\n" + "="*80)
        print("📊 最终完成度验证报告")
        print("="*80)
        
        for service_name, result in self.validation_results.items():
            completion = result["completion"]
            status = result["status"]
            
            print(f"\n🔧 {service_name}:")
            print(f"   完成度: {completion:.1f}%")
            print(f"   状态: {status}")
            print(f"   语法质量: {result.get('syntax_score', 0)}/100")
            print(f"   文档完整性: {result.get('doc_score', 0)}/100")
            print(f"   测试覆盖: {result.get('test_score', 0)}/100")
            print(f"   部署就绪: {result.get('deploy_score', 0)}/100")
            print(f"   功能完整: {result.get('feature_score', 0)}/100")
            
            total_completion += completion
            if completion >= 100:
                completed_services += 1
                
        overall_completion = total_completion / len(self.validation_results)
        
        print(f"\n🎯 整体统计:")
        print(f"   整体完成度: {overall_completion:.1f}%")
        print(f"   100%完成服务: {completed_services}/{len(self.validation_results)}")
        print(f"   完成率: {completed_services/len(self.validation_results)*100:.1f}%")
        
        # 判断是否达到100%目标
        if overall_completion >= 100:
            print(f"\n🎉 恭喜！所有服务已达到100%完成度！")
            final_status = "🎉 100% 完成"
        elif overall_completion >= 97:
            print(f"\n✅ 优秀！整体完成度已达到97%以上，非常接近100%目标！")
            final_status = "✅ 接近完成"
        elif overall_completion >= 90:
            print(f"\n🟡 良好！整体完成度已达到90%以上，距离100%目标很近！")
            final_status = "🟡 基本完成"
        else:
            print(f"\n🔧 需要继续优化以达到100%目标")
            final_status = "🔧 需要优化"
            
        return {
            "overall_completion": overall_completion,
            "completed_services": completed_services,
            "total_services": len(self.validation_results),
            "completion_rate": completed_services/len(self.validation_results)*100,
            "final_status": final_status,
            "service_results": self.validation_results
        }

def main():
    """主函数"""
    print("🚀 启动最终完成度验证...")
    
    validator = FinalCompletionValidator()
    final_report = validator.validate_all_services()
    
    # 保存报告
    with open("final_completion_report.json", "w", encoding="utf-8") as f:
        json.dump(final_report, f, ensure_ascii=False, indent=2)
        
    print(f"\n📄 详细报告已保存到: final_completion_report.json")
    
    return final_report["overall_completion"] >= 97

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 