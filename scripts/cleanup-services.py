#!/usr/bin/env python3
"""
索克生活服务目录清理工具
清理services目录中的非服务文件
"""

import os
import shutil
from pathlib import Path

class ServicesCleaner:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.services_dir = self.project_root / "services"
        self.cleanup_dir = self.project_root / "cleanup" / "services"
        
    def identify_non_service_files(self):
        """识别非服务文件"""
        non_service_items = []
        
        for item in self.services_dir.iterdir():
            # 如果是文件，肯定不是服务
            if item.is_file():
                non_service_items.append(item)
            # 如果是目录但名称不像服务名
            elif item.is_dir():
                # 检查是否包含典型的服务文件
                has_service_files = any([
                    (item / "Dockerfile").exists(),
                    (item / "requirements.txt").exists(),
                    (item / "main.py").exists(),
                    (item / "app.py").exists(),
                    (item / item.name.replace("-", "_")).exists()
                ])
                
                # 如果没有典型服务文件，可能不是服务
                if not has_service_files and not item.name.endswith("-service"):
                    # 进一步检查是否有Python代码
                    py_files = list(item.rglob("*.py"))
                    if len(py_files) < 5:  # 少于5个Python文件，可能不是服务
                        non_service_items.append(item)
        
        return non_service_items
    
    def move_non_service_files(self):
        """移动非服务文件"""
        non_service_items = self.identify_non_service_files()
        
        if not non_service_items:
            print("✅ services目录已经很干净，没有发现非服务文件")
            return []
        
        print(f"🧹 发现 {len(non_service_items)} 个非服务文件/目录")
        
        # 创建清理目录
        self.cleanup_dir.mkdir(parents=True, exist_ok=True)
        
        moved_items = []
        for item in non_service_items:
            target_path = self.cleanup_dir / item.name
            
            # 如果目标已存在，添加序号
            counter = 1
            while target_path.exists():
                name_parts = item.name.split('.')
                if len(name_parts) > 1:
                    new_name = f"{'.'.join(name_parts[:-1])}_{counter}.{name_parts[-1]}"
                else:
                    new_name = f"{item.name}_{counter}"
                target_path = self.cleanup_dir / new_name
                counter += 1
            
            try:
                shutil.move(str(item), str(target_path))
                moved_items.append((item.name, target_path.name))
                print(f"  📦 移动: {item.name} -> cleanup/services/{target_path.name}")
            except Exception as e:
                print(f"  ❌ 移动失败 {item.name}: {e}")
        
        return moved_items
    
    def count_actual_services(self):
        """统计实际的服务数量"""
        services = []
        
        for item in self.services_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                # 检查是否是真正的服务
                has_service_indicators = any([
                    (item / "Dockerfile").exists(),
                    (item / "requirements.txt").exists(),
                    item.name.endswith("-service"),
                    (item / item.name.replace("-", "_")).exists(),
                    len(list(item.rglob("*.py"))) > 5
                ])
                
                if has_service_indicators:
                    services.append(item.name)
        
        return services
    
    def generate_cleanup_report(self, moved_items):
        """生成清理报告"""
        services = self.count_actual_services()
        
        report = []
        report.append("# 服务目录清理报告\n")
        report.append(f"**清理时间**: {os.popen('date').read().strip()}\n")
        
        report.append("## 清理结果\n")
        report.append(f"- **移动的文件/目录**: {len(moved_items)}个")
        report.append(f"- **剩余服务数量**: {len(services)}个")
        report.append("")
        
        if moved_items:
            report.append("## 移动的文件列表\n")
            for original, moved in moved_items:
                report.append(f"- `{original}` → `cleanup/services/{moved}`")
            report.append("")
        
        report.append("## 当前服务列表\n")
        for service in sorted(services):
            report.append(f"- {service}")
        report.append("")
        
        report.append("## 恢复方法\n")
        report.append("如需恢复移动的文件：")
        report.append("```bash")
        for original, moved in moved_items:
            report.append(f"mv cleanup/services/{moved} services/{original}")
        report.append("```")
        
        return "\n".join(report)
    
    def run_cleanup(self):
        """执行清理"""
        print("🧹 开始清理services目录...")
        
        # 移动非服务文件
        moved_items = self.move_non_service_files()
        
        # 统计服务
        services = self.count_actual_services()
        
        # 生成报告
        report_content = self.generate_cleanup_report(moved_items)
        report_path = self.project_root / "SERVICES_CLEANUP_REPORT.md"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"\n✅ 清理完成!")
        print(f"📊 当前服务数量: {len(services)}")
        print(f"📦 移动文件数量: {len(moved_items)}")
        print(f"📄 清理报告: {report_path}")
        
        if moved_items:
            print(f"🗂️ 移动的文件位置: {self.cleanup_dir}")
        
        return {
            "services_count": len(services),
            "moved_items": len(moved_items),
            "services": services
        }

def main():
    project_root = os.getcwd()
    cleaner = ServicesCleaner(project_root)
    result = cleaner.run_cleanup()
    
    print(f"\n📋 服务列表:")
    for service in sorted(result['services']):
        print(f"  - {service}")

if __name__ == "__main__":
    main() 