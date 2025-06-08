#!/usr/bin/env python3
"""
索克生活项目代码质量检查器
建立基础的代码检查流程
"""

import os
import subprocess
import json
from pathlib import Path
from typing import Dict, List

class CodeQualityChecker:
    def __init__(self):
        self.project_root = Path.cwd()
        self.results = {}
        
    def execute_quality_check(self):
        """执行代码质量检查"""
        print('🚀 启动代码质量检查器...')
        print('=' * 80)
        
        # 1. TypeScript编译检查
        self._check_typescript()
        
        # 2. ESLint检查
        self._check_eslint()
        
        # 3. 文件结构检查
        self._check_file_structure()
        
        # 4. 生成报告
        self._generate_report()
        
        print('\n🎉 代码质量检查完成！')
        
    def _check_typescript(self):
        """检查TypeScript编译"""
        print('\n📋 检查TypeScript编译...')
        print('-' * 50)
        
        try:
            result = subprocess.run(
                ['npx', 'tsc', '--noEmit', '--skipLibCheck'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                self.results['typescript'] = {
                    'status': 'success',
                    'errors': 0,
                    'message': 'TypeScript编译成功'
                }
                print('  ✅ TypeScript编译成功')
            else:
                error_lines = result.stderr.split('\n')
                error_count = len([line for line in error_lines if 'error TS' in line])
                
                self.results['typescript'] = {
                    'status': 'error',
                    'errors': error_count,
                    'message': f'发现 {error_count} 个TypeScript错误'
                }
                print(f'  ❌ 发现 {error_count} 个TypeScript错误')
                
        except subprocess.TimeoutExpired:
            self.results['typescript'] = {
                'status': 'timeout',
                'errors': -1,
                'message': 'TypeScript检查超时'
            }
            print('  ⏰ TypeScript检查超时')
        except Exception as e:
            self.results['typescript'] = {
                'status': 'failed',
                'errors': -1,
                'message': f'TypeScript检查失败: {e}'
            }
            print(f'  ❌ TypeScript检查失败: {e}')
            
    def _check_eslint(self):
        """检查ESLint"""
        print('\n📋 检查ESLint...')
        print('-' * 50)
        
        try:
            # 检查是否有ESLint配置
            eslint_configs = ['.eslintrc.js', '.eslintrc.json', '.eslintrc.yml']
            has_config = any((self.project_root / config).exists() for config in eslint_configs)
            
            if not has_config:
                self.results['eslint'] = {
                    'status': 'no_config',
                    'errors': 0,
                    'message': '未找到ESLint配置文件'
                }
                print('  ⚠️ 未找到ESLint配置文件')
                return
                
            result = subprocess.run(
                ['npx', 'eslint', 'src/', '--format', 'json'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.results['eslint'] = {
                    'status': 'success',
                    'errors': 0,
                    'message': 'ESLint检查通过'
                }
                print('  ✅ ESLint检查通过')
            else:
                try:
                    eslint_output = json.loads(result.stdout)
                    error_count = sum(len(file['messages']) for file in eslint_output)
                    
                    self.results['eslint'] = {
                        'status': 'error',
                        'errors': error_count,
                        'message': f'发现 {error_count} 个ESLint错误'
                    }
                    print(f'  ❌ 发现 {error_count} 个ESLint错误')
                except:
                    self.results['eslint'] = {
                        'status': 'error',
                        'errors': -1,
                        'message': 'ESLint检查失败'
                    }
                    print('  ❌ ESLint检查失败')
                    
        except subprocess.TimeoutExpired:
            self.results['eslint'] = {
                'status': 'timeout',
                'errors': -1,
                'message': 'ESLint检查超时'
            }
            print('  ⏰ ESLint检查超时')
        except Exception as e:
            self.results['eslint'] = {
                'status': 'failed',
                'errors': -1,
                'message': f'ESLint检查失败: {e}'
            }
            print(f'  ❌ ESLint检查失败: {e}')
            
    def _check_file_structure(self):
        """检查文件结构"""
        print('\n📋 检查文件结构...')
        print('-' * 50)
        
        try:
            # 检查关键目录
            required_dirs = ['src', 'src/components', 'src/screens', 'src/services']
            missing_dirs = []
            
            for dir_path in required_dirs:
                if not (self.project_root / dir_path).exists():
                    missing_dirs.append(dir_path)
                    
            # 检查关键文件
            required_files = ['package.json', 'tsconfig.json']
            missing_files = []
            
            for file_path in required_files:
                if not (self.project_root / file_path).exists():
                    missing_files.append(file_path)
                    
            # 统计文件数量
            ts_files = list(self.project_root.rglob('src/**/*.ts'))
            tsx_files = list(self.project_root.rglob('src/**/*.tsx'))
            js_files = list(self.project_root.rglob('src/**/*.js'))
            jsx_files = list(self.project_root.rglob('src/**/*.jsx'))
            
            total_files = len(ts_files) + len(tsx_files) + len(js_files) + len(jsx_files)
            
            self.results['file_structure'] = {
                'status': 'success' if not missing_dirs and not missing_files else 'warning',
                'missing_dirs': missing_dirs,
                'missing_files': missing_files,
                'total_files': total_files,
                'ts_files': len(ts_files),
                'tsx_files': len(tsx_files),
                'js_files': len(js_files),
                'jsx_files': len(jsx_files)
            }
            
            print(f'  📊 总计文件: {total_files}')
            print(f'  📄 TypeScript文件: {len(ts_files)}')
            print(f'  📄 TSX文件: {len(tsx_files)}')
            print(f'  📄 JavaScript文件: {len(js_files)}')
            print(f'  📄 JSX文件: {len(jsx_files)}')
            
            if missing_dirs:
                print(f'  ⚠️ 缺少目录: {", ".join(missing_dirs)}')
            if missing_files:
                print(f'  ⚠️ 缺少文件: {", ".join(missing_files)}')
                
        except Exception as e:
            self.results['file_structure'] = {
                'status': 'failed',
                'message': f'文件结构检查失败: {e}'
            }
            print(f'  ❌ 文件结构检查失败: {e}')
            
    def _generate_report(self):
        """生成检查报告"""
        print('\n📊 生成代码质量检查报告...')
        
        # 计算总体状态
        overall_status = 'success'
        total_errors = 0
        
        for check_name, result in self.results.items():
            if result.get('status') in ['error', 'failed']:
                overall_status = 'error'
            elif result.get('status') in ['warning', 'timeout', 'no_config'] and overall_status == 'success':
                overall_status = 'warning'
                
            if result.get('errors', 0) > 0:
                total_errors += result['errors']
                
        report_content = f"""# 代码质量检查报告

## 检查概览

**检查时间**: {self._get_current_time()}  
**总体状态**: {self._get_status_emoji(overall_status)} {overall_status.upper()}  
**总错误数**: {total_errors}  

---

## 检查详情

### TypeScript编译检查
- **状态**: {self._get_status_emoji(self.results.get('typescript', {}).get('status', 'unknown'))} {self.results.get('typescript', {}).get('status', 'unknown').upper()}
- **错误数**: {self.results.get('typescript', {}).get('errors', 0)}
- **说明**: {self.results.get('typescript', {}).get('message', '未检查')}

### ESLint检查
- **状态**: {self._get_status_emoji(self.results.get('eslint', {}).get('status', 'unknown'))} {self.results.get('eslint', {}).get('status', 'unknown').upper()}
- **错误数**: {self.results.get('eslint', {}).get('errors', 0)}
- **说明**: {self.results.get('eslint', {}).get('message', '未检查')}

### 文件结构检查
- **状态**: {self._get_status_emoji(self.results.get('file_structure', {}).get('status', 'unknown'))} {self.results.get('file_structure', {}).get('status', 'unknown').upper()}
- **总文件数**: {self.results.get('file_structure', {}).get('total_files', 0)}
- **TypeScript文件**: {self.results.get('file_structure', {}).get('ts_files', 0)}
- **TSX文件**: {self.results.get('file_structure', {}).get('tsx_files', 0)}

---

## 建议操作

"""

        if overall_status == 'error':
            report_content += """
### 🚨 紧急修复建议

1. **修复TypeScript错误**:
   ```bash
   npx tsc --noEmit
   ```

2. **运行修复工具**:
   ```bash
   python scripts/systematic_bug_fixer.py
   ```

3. **检查修复效果**:
   ```bash
   python scripts/code_quality_checker.py
   ```
"""
        elif overall_status == 'warning':
            report_content += """
### ⚠️ 改进建议

1. **配置ESLint**:
   ```bash
   npm install --save-dev eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin
   ```

2. **运行代码格式化**:
   ```bash
   npx prettier --write src/
   ```
"""
        else:
            report_content += """
### ✅ 代码质量良好

项目代码质量检查通过，建议：

1. **定期运行检查**:
   ```bash
   python scripts/code_quality_checker.py
   ```

2. **配置CI/CD**:
   ```bash
   python scripts/ci_cd_integration.py
   ```
"""

        report_content += f"""

---

**状态**: 代码质量检查完成  
**下一步**: 根据检查结果执行相应的修复操作  
"""

        # 保存报告
        with open('CODE_QUALITY_CHECK_REPORT.md', 'w', encoding='utf-8') as f:
            f.write(report_content)
            
        # 保存JSON结果
        with open('code_quality_results.json', 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
            
        print(f'  ✅ 检查报告已生成: CODE_QUALITY_CHECK_REPORT.md')
        print(f'  📊 总体状态: {overall_status.upper()}')
        print(f'  🔢 总错误数: {total_errors}')
        
    def _get_status_emoji(self, status: str) -> str:
        """获取状态表情符号"""
        emoji_map = {
            'success': '✅',
            'error': '❌',
            'warning': '⚠️',
            'failed': '💥',
            'timeout': '⏰',
            'no_config': '📝',
            'unknown': '❓'
        }
        return emoji_map.get(status, '❓')
        
    def _get_current_time(self):
        """获取当前时间"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def main():
    """主函数"""
    checker = CodeQualityChecker()
    checker.execute_quality_check()

if __name__ == "__main__":
    main() 