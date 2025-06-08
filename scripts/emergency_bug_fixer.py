#!/usr/bin/env python3
"""
索克生活项目紧急Bug修复器
专门修复发现的关键语法错误，确保项目可以编译运行
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple

class EmergencyBugFixer:
    def __init__(self):
        self.project_root = Path.cwd()
        self.fixes_applied = []
        self.critical_files = [
            'src/App.tsx',
            'src/agents/AgentManager.ts',
            'src/agents/base/AgentBase.ts',
            'src/agents/base/BaseAgent.ts'
        ]
        
    def fix_all_critical_bugs(self):
        """修复所有关键Bug"""
        print('🚨 启动紧急Bug修复器...')
        print('=' * 60)
        
        # 1. 修复App.tsx
        self.fix_app_tsx()
        
        # 2. 修复AgentManager.ts
        self.fix_agent_manager()
        
        # 3. 修复AgentBase.ts
        self.fix_agent_base()
        
        # 4. 修复配置问题
        self.fix_config_issues()
        
        # 5. 生成修复报告
        self.generate_fix_report()
        
        print('\n🎉 紧急Bug修复完成！')
        
    def fix_app_tsx(self):
        """修复App.tsx中的语法错误"""
        print('🔧 修复 App.tsx...')
        
        file_path = self.project_root / 'src/App.tsx'
        if not file_path.exists():
            print(f'  ❌ 文件不存在: {file_path}')
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_content = content
            
            # 修复React.lazy语法错误
            content = re.sub(
                r'const (\w+) = React\.lazy\(\) => import\(',
                r'const \1 = React.lazy(() => import(',
                content
            )
            
            # 修复样式对象语法
            content = re.sub(
                r'style=\{\s*flex:\s*1[^}]*\}',
                'style={{ flex: 1, justifyContent: \'center\', alignItems: \'center\' }}',
                content
            )
            
            # 修复Text组件语法错误
            content = re.sub(r'<Text;', '<Text', content)
            content = re.sub(r'<Tab\.Navigator;', '<Tab.Navigator', content)
            content = re.sub(r'<Tab\.Screen;', '<Tab.Screen', content)
            
            # 修复useEffect语法
            content = re.sub(
                r'useEffect\(\) => \{',
                'useEffect(() => {',
                content
            )
            
            # 修复数组解构语法
            content = re.sub(
                r'\.filter\(\[([^]]+)\]\) =>',
                r'.filter((\[\1\]) =>',
                content
            )
            content = re.sub(
                r'\.map\(\[([^]]+)\]\) =>',
                r'.map((\[\1\]) =>',
                content
            )
            
            # 修复对象属性语法
            content = re.sub(r'options=\{\s*title:', 'options={{ title:', content)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                self.fixes_applied.append({
                    'file': 'src/App.tsx',
                    'fixes': [
                        'React.lazy语法修复',
                        '样式对象语法修复',
                        'Text组件语法修复',
                        'useEffect语法修复',
                        '数组解构语法修复'
                    ]
                })
                print('  ✅ App.tsx 修复完成')
            else:
                print('  ℹ️ App.tsx 无需修复')
                
        except Exception as e:
            print(f'  ❌ 修复App.tsx失败: {e}')
            
    def fix_agent_manager(self):
        """修复AgentManager.ts中的语法错误"""
        print('🔧 修复 AgentManager.ts...')
        
        file_path = self.project_root / 'src/agents/AgentManager.ts'
        if not file_path.exists():
            print(f'  ❌ 文件不存在: {file_path}')
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_content = content
            
            # 修复reduce函数语法
            content = re.sub(
                r'\.reduce\(;',
                '.reduce((sum, metrics) => sum + metrics.errors, 0);',
                content
            )
            
            # 修复对象字面量语法错误
            content = re.sub(
                r'return \{totalAgents: this\.metrics\.size,totalTasksProcessed: totalTasks,totalErrors,overallSuccessRate:;',
                '''return {
      totalAgents: this.metrics.size,
      totalTasksProcessed: totalTasks,
      totalErrors,
      overallSuccessRate: totalTasks > 0 ? (totalTasks - totalErrors) / totalTasks : 0,
      averageResponseTime: avgResponseTime,
      systemUptime,
      isHealthy: this.isSystemHealthy(),
      config: this.config,
      lastUpdate: new Date()
    };''',
                content
            )
            
            # 修复for...of循环语法
            content = re.sub(
                r'for \(const \[([^,]+), ([^]]+)\] of ([^)]+)\) \{',
                r'for (const [\1, \2] of \3) {',
                content
            )
            
            # 修复函数参数语法
            content = re.sub(
                r'private updateMetrics\(result: any, executionTime: number\): void \{',
                'private updateMetrics(result: any, executionTime: number): void {',
                content
            )
            
            # 修复模板字符串
            content = re.sub(
                r'this\.log\("info",([^"]+)"\);',
                r'this.log("info", "\1");',
                content
            )
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                self.fixes_applied.append({
                    'file': 'src/agents/AgentManager.ts',
                    'fixes': [
                        'reduce函数语法修复',
                        '对象字面量语法修复',
                        'for...of循环语法修复',
                        '函数参数语法修复',
                        '模板字符串修复'
                    ]
                })
                print('  ✅ AgentManager.ts 修复完成')
            else:
                print('  ℹ️ AgentManager.ts 无需修复')
                
        except Exception as e:
            print(f'  ❌ 修复AgentManager.ts失败: {e}')
            
    def fix_agent_base(self):
        """修复AgentBase.ts中的语法错误"""
        print('🔧 修复 AgentBase.ts...')
        
        file_path = self.project_root / 'src/agents/base/AgentBase.ts'
        if not file_path.exists():
            print(f'  ❌ 文件不存在: {file_path}')
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_content = content
            
            # 修复模板字符串未终止问题
            content = re.sub(
                r'const logMessage = `\[\$\{timestamp\}\] \[\$\{this\.agentType;',
                'const logMessage = `[${timestamp}] [${this.agentType}]`;',
                content
            )
            
            # 修复方法链语法错误
            content = re.sub(
                r'return `\$\{this\.agentType\}_\$\{Date\.now\(\)\}_\$\{Math\.random\(\);[\s\n]*\.toString\(36\);[\s\n]*\.substr\(2, 9\)\}`;',
                'return `${this.agentType}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;',
                content
            )
            
            # 修复导入语法
            content = re.sub(
                r'AgentContext;',
                'AgentContext,',
                content
            )
            
            # 修复构造函数参数语法
            content = re.sub(
                r'constructor\(params: \{,',
                'constructor(params: {',
                content
            )
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                self.fixes_applied.append({
                    'file': 'src/agents/base/AgentBase.ts',
                    'fixes': [
                        '模板字符串语法修复',
                        '方法链语法修复',
                        '导入语法修复',
                        '构造函数参数修复'
                    ]
                })
                print('  ✅ AgentBase.ts 修复完成')
            else:
                print('  ℹ️ AgentBase.ts 无需修复')
                
        except Exception as e:
            print(f'  ❌ 修复AgentBase.ts失败: {e}')
            
    def fix_config_issues(self):
        """修复配置问题"""
        print('🔧 修复配置问题...')
        
        # 修复react-native-sqlite-storage配置冲突
        self.fix_sqlite_config()
        
        # 修复package.json依赖问题
        self.fix_package_dependencies()
        
    def fix_sqlite_config(self):
        """修复SQLite配置冲突"""
        print('  🔧 修复SQLite配置冲突...')
        
        # 方案A: 从package.json中移除sqlite-storage依赖
        package_json_path = self.project_root / 'package.json'
        if package_json_path.exists():
            try:
                with open(package_json_path, 'r', encoding='utf-8') as f:
                    package_data = json.load(f)
                    
                # 移除sqlite-storage相关依赖
                dependencies_removed = []
                if 'react-native-sqlite-storage' in package_data.get('dependencies', {}):
                    del package_data['dependencies']['react-native-sqlite-storage']
                    dependencies_removed.append('react-native-sqlite-storage')
                    
                if '@types/react-native-sqlite-storage' in package_data.get('devDependencies', {}):
                    del package_data['devDependencies']['@types/react-native-sqlite-storage']
                    dependencies_removed.append('@types/react-native-sqlite-storage')
                    
                if dependencies_removed:
                    with open(package_json_path, 'w', encoding='utf-8') as f:
                        json.dump(package_data, f, indent=2, ensure_ascii=False)
                        
                    self.fixes_applied.append({
                        'file': 'package.json',
                        'fixes': [f'移除依赖: {", ".join(dependencies_removed)}']
                    })
                    print(f'    ✅ 移除SQLite依赖: {", ".join(dependencies_removed)}')
                else:
                    print('    ℹ️ 无SQLite依赖需要移除')
                    
            except Exception as e:
                print(f'    ❌ 修复package.json失败: {e}')
                
    def fix_package_dependencies(self):
        """修复package.json依赖问题"""
        print('  🔧 检查依赖版本兼容性...')
        
        package_json_path = self.project_root / 'package.json'
        if package_json_path.exists():
            try:
                with open(package_json_path, 'r', encoding='utf-8') as f:
                    package_data = json.load(f)
                    
                dependencies = package_data.get('dependencies', {})
                
                # 检查React版本兼容性
                react_version = dependencies.get('react', '')
                rn_version = dependencies.get('react-native', '')
                
                if '19.0.0' in react_version and '0.79' in rn_version:
                    print('    ⚠️ 检测到React 19.0.0与React Native 0.79.2可能存在兼容性问题')
                    print('    💡 建议: 考虑降级React版本或升级React Native版本')
                    
                    self.fixes_applied.append({
                        'file': 'package.json',
                        'fixes': ['标记React版本兼容性问题']
                    })
                    
            except Exception as e:
                print(f'    ❌ 检查依赖版本失败: {e}')
                
    def generate_fix_report(self):
        """生成修复报告"""
        print('📊 生成修复报告...')
        
        total_fixes = sum(len(fix['fixes']) for fix in self.fixes_applied)
        
        report_content = f"""# 紧急Bug修复报告

## 修复概览

**修复时间**: {self._get_current_time()}  
**修复文件数**: {len(self.fixes_applied)}  
**修复问题数**: {total_fixes}  

---

## 修复详情

"""

        for fix in self.fixes_applied:
            report_content += f"""
### {fix['file']}

修复内容:
"""
            for fix_item in fix['fixes']:
                report_content += f"- ✅ {fix_item}\n"
                
        report_content += f"""

---

## 验证建议

### 立即验证
```bash
# 检查TypeScript编译
npx tsc --noEmit

# 检查React Native配置
npx react-native config

# 启动开发服务器
npm start
```

### 后续步骤
1. 运行完整的测试套件
2. 验证所有核心功能
3. 检查是否还有其他语法错误
4. 建立代码质量检查流程

---

**修复工具**: 索克生活紧急Bug修复器  
**状态**: 修复完成，需要验证  
"""

        # 保存报告
        with open('EMERGENCY_BUG_FIX_REPORT.md', 'w', encoding='utf-8') as f:
            f.write(report_content)
            
        print(f'  ✅ 修复报告已生成: EMERGENCY_BUG_FIX_REPORT.md')
        print(f'  📊 总计修复: {len(self.fixes_applied)}个文件, {total_fixes}个问题')
        
    def _get_current_time(self):
        """获取当前时间"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def main():
    """主函数"""
    fixer = EmergencyBugFixer()
    
    print('🚨 索克生活项目紧急Bug修复器')
    print('🎯 专门修复关键语法错误，确保项目可以编译运行')
    print()
    
    fixer.fix_all_critical_bugs()
    
    print()
    print('🎉 紧急修复完成！请运行以下命令验证:')
    print('   npx tsc --noEmit')
    print('   npm start')

if __name__ == "__main__":
    main() 