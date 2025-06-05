#!/usr/bin/env python3
"""
部署验证脚本
验证医疗资源服务的部署状态和功能完整性
"""

import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime
import importlib.util

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class DeploymentValidator:
    """部署验证器"""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "service_name": "medical-resource-service",
            "version": "1.0.0",
            "checks": {},
            "overall_status": "UNKNOWN"
        }
    
    def check_file_exists(self, file_path: str, description: str) -> bool:
        """检查文件是否存在"""
        path = project_root / file_path
        exists = path.exists()
        self.results["checks"][f"file_{file_path.replace('/', '_')}"] = {
            "description": description,
            "status": "PASS" if exists else "FAIL",
            "details": f"File {'exists' if exists else 'missing'}: {path}"
        }
        return exists
    
    def check_module_import(self, module_path: str, description: str) -> bool:
        """检查模块是否可以导入"""
        try:
            spec = importlib.util.spec_from_file_location("test_module", project_root / module_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                success = True
                details = f"Module imported successfully: {module_path}"
            else:
                success = False
                details = f"Failed to load module spec: {module_path}"
        except Exception as e:
            success = False
            details = f"Import error: {str(e)}"
        
        self.results["checks"][f"import_{module_path.replace('/', '_').replace('.py', '')}"] = {
            "description": description,
            "status": "PASS" if success else "FAIL",
            "details": details
        }
        return success
    
    def check_config_files(self) -> bool:
        """检查配置文件"""
        config_files = [
            ("config/config.yaml", "主配置文件"),
            ("docker-compose.yml", "Docker Compose配置"),
            ("Dockerfile", "Docker镜像配置"),
            ("pytest.ini", "测试配置文件"),
            ("requirements.txt", "Python依赖文件")
        ]
        
        all_passed = True
        for file_path, description in config_files:
            if not self.check_file_exists(file_path, description):
                all_passed = False
        
        return all_passed
    
    def check_core_services(self) -> bool:
        """检查核心服务文件"""
        core_services = [
            ("internal/enhanced_medical_resource_service.py", "增强医疗资源服务"),
            ("internal/service/wellness_tourism_service.py", "山水养生服务"),
            ("internal/service/enhanced_food_agriculture_service.py", "增强食农结合服务"),
            ("internal/service/famous_doctor_service.py", "名医资源管理服务"),
            ("internal/service/intelligent_appointment_service.py", "智能预约服务")
        ]
        
        all_passed = True
        for file_path, description in core_services:
            if not self.check_file_exists(file_path, description):
                all_passed = False
        
        return all_passed
    
    def check_test_files(self) -> bool:
        """检查测试文件"""
        test_files = [
            ("tests/conftest.py", "测试配置文件"),
            ("tests/unit/test_enhanced_medical_service.py", "单元测试"),
            ("tests/performance/test_load_testing.py", "性能测试"),
            ("tests/e2e/test_end_to_end.py", "端到端测试"),
            ("scripts/run_tests.py", "测试运行脚本")
        ]
        
        all_passed = True
        for file_path, description in test_files:
            if not self.check_file_exists(file_path, description):
                all_passed = False
        
        return all_passed
    
    def check_api_documentation(self) -> bool:
        """检查API文档"""
        doc_files = [
            ("docs/api/README.md", "API文档"),
            ("医疗资源服务开发完成度分析报告.md", "开发完成度分析报告")
        ]
        
        all_passed = True
        for file_path, description in doc_files:
            if not self.check_file_exists(file_path, description):
                all_passed = False
        
        return all_passed
    
    def check_module_imports(self) -> bool:
        """检查关键模块导入"""
        modules = [
            ("internal/enhanced_medical_resource_service.py", "增强医疗资源服务模块"),
            ("internal/service/wellness_tourism_service.py", "山水养生服务模块"),
            ("internal/service/enhanced_food_agriculture_service.py", "增强食农结合服务模块"),
            ("internal/service/famous_doctor_service.py", "名医资源管理服务模块"),
            ("internal/service/intelligent_appointment_service.py", "智能预约服务模块")
        ]
        
        all_passed = True
        for module_path, description in modules:
            if not self.check_module_import(module_path, description):
                all_passed = False
        
        return all_passed
    
    def check_directory_structure(self) -> bool:
        """检查目录结构"""
        required_dirs = [
            "internal",
            "internal/service",
            "tests",
            "tests/unit",
            "tests/integration", 
            "tests/performance",
            "tests/e2e",
            "scripts",
            "docs",
            "docs/api",
            "config",
            "deploy"
        ]
        
        all_passed = True
        for dir_path in required_dirs:
            path = project_root / dir_path
            exists = path.exists() and path.is_dir()
            
            self.results["checks"][f"dir_{dir_path.replace('/', '_')}"] = {
                "description": f"目录结构: {dir_path}",
                "status": "PASS" if exists else "FAIL",
                "details": f"Directory {'exists' if exists else 'missing'}: {path}"
            }
            
            if not exists:
                all_passed = False
        
        return all_passed
    
    async def run_validation(self) -> dict:
        """运行完整验证"""
        print("🔍 开始医疗资源服务部署验证...")
        print(f"📁 项目路径: {project_root}")
        print(f"⏰ 验证时间: {self.results['timestamp']}")
        print("-" * 60)
        
        # 执行各项检查
        checks = [
            ("目录结构", self.check_directory_structure),
            ("配置文件", self.check_config_files),
            ("核心服务", self.check_core_services),
            ("测试文件", self.check_test_files),
            ("API文档", self.check_api_documentation),
            ("模块导入", self.check_module_imports)
        ]
        
        total_checks = 0
        passed_checks = 0
        
        for check_name, check_func in checks:
            print(f"🔍 检查 {check_name}...")
            try:
                result = check_func()
                if result:
                    print(f"✅ {check_name} - 通过")
                    passed_checks += 1
                else:
                    print(f"❌ {check_name} - 失败")
                total_checks += 1
            except Exception as e:
                print(f"💥 {check_name} - 错误: {str(e)}")
                total_checks += 1
        
        # 计算总体状态
        success_rate = passed_checks / total_checks if total_checks > 0 else 0
        
        if success_rate >= 0.9:
            self.results["overall_status"] = "EXCELLENT"
            status_emoji = "🎉"
            status_desc = "优秀"
        elif success_rate >= 0.8:
            self.results["overall_status"] = "GOOD"
            status_emoji = "✅"
            status_desc = "良好"
        elif success_rate >= 0.6:
            self.results["overall_status"] = "FAIR"
            status_emoji = "⚠️"
            status_desc = "一般"
        else:
            self.results["overall_status"] = "POOR"
            status_emoji = "❌"
            status_desc = "差"
        
        self.results["summary"] = {
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "success_rate": success_rate,
            "status_description": status_desc
        }
        
        # 输出结果
        print("-" * 60)
        print(f"{status_emoji} 验证完成!")
        print(f"📊 总检查项: {total_checks}")
        print(f"✅ 通过检查: {passed_checks}")
        print(f"📈 成功率: {success_rate:.1%}")
        print(f"🏆 总体状态: {status_desc}")
        
        # 保存结果
        result_file = project_root / "deployment_validation_result.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"📄 详细结果已保存到: {result_file}")
        
        return self.results
    
    def print_detailed_results(self):
        """打印详细结果"""
        print("\n" + "=" * 60)
        print("📋 详细验证结果")
        print("=" * 60)
        
        for check_id, check_result in self.results["checks"].items():
            status_emoji = "✅" if check_result["status"] == "PASS" else "❌"
            print(f"{status_emoji} {check_result['description']}")
            if check_result["status"] == "FAIL":
                print(f"   💡 {check_result['details']}")
        
        print("\n" + "=" * 60)


async def main():
    """主函数"""
    validator = DeploymentValidator()
    
    try:
        results = await validator.run_validation()
        
        # 如果需要详细结果，取消注释下面这行
        # validator.print_detailed_results()
        
        # 根据验证结果设置退出码
        if results["overall_status"] in ["EXCELLENT", "GOOD"]:
            print("\n🚀 服务已准备好部署!")
            sys.exit(0)
        else:
            print("\n⚠️ 服务需要进一步完善后再部署")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 验证过程中发生错误: {str(e)}")
        sys.exit(2)


if __name__ == "__main__":
    asyncio.run(main()) 