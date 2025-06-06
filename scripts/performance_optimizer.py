"""
performance_optimizer - 索克生活项目模块
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
import asyncio
import json
import logging
import os
import re
import subprocess
import time

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
索克生活 - 性能优化器
自动优化数据库查询、API响应时间和前端性能
"""


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PerformanceOptimizer:
    """性能优化器"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.optimization_report = {
            "database": {"optimized": 0, "total": 0, "improvements": []},
            "api": {"optimized": 0, "total": 0, "improvements": []},
            "frontend": {"optimized": 0, "total": 0, "improvements": []},
            "overall_score": 0
        }
        
    def optimize_all(self) -> bool:
        """执行全面性能优化"""
        logger.info("🚀 开始性能优化...")
        
        try:
            # 数据库优化
            self.optimize_database()
            
            # API优化
            self.optimize_api()
            
            # 前端优化
            self.optimize_frontend()
            
            # 生成优化报告
            self.generate_report()
            
            logger.info("🎉 性能优化完成！")
            return True
            
        except Exception as e:
            logger.error(f"❌ 性能优化失败: {e}")
            return False
    
    def optimize_database(self):
        """数据库性能优化"""
        logger.info("📊 开始数据库优化...")
        
        # 查找数据库相关文件
        db_files = list(self.project_root.glob("**/*.py"))
        db_files = [f for f in db_files if self.is_database_file(f)]
        
        for file_path in db_files:
            try:
                optimized = self.optimize_database_file(file_path)
                if optimized:
                    self.optimization_report["database"]["optimized"] += 1
                self.optimization_report["database"]["total"] += 1
                
            except Exception as e:
                logger.warning(f"数据库文件优化失败 {file_path}: {e}")
        
        logger.info(f"✅ 数据库优化完成: {self.optimization_report['database']['optimized']}/{self.optimization_report['database']['total']}")
    
    def is_database_file(self, file_path: Path) -> bool:
        """判断是否为数据库相关文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            db_indicators = [
                'from sqlalchemy import',
                'Session(',
                'query(',
                'filter(',
                'join(',
                'select(',
                'from django.db import',
                'models.Model'
            ]
            
            return any(indicator in content for indicator in db_indicators)
            
        except Exception:
            return False
    
    def optimize_database_file(self, file_path: Path) -> bool:
        """优化单个数据库文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            optimizations = []
            
            # 优化1: 添加数据库索引建议
            if 'class ' in content and 'Model' in content:
                content = self.add_index_suggestions(content)
                optimizations.append("添加数据库索引建议")
            
            # 优化2: 优化查询语句
            content = self.optimize_queries(content)
            if content != original_content:
                optimizations.append("优化查询语句")
            
            # 优化3: 添加查询缓存
            content = self.add_query_cache(content)
            if content != original_content:
                optimizations.append("添加查询缓存")
            
            # 优化4: 批量操作优化
            content = self.optimize_batch_operations(content)
            if content != original_content:
                optimizations.append("批量操作优化")
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.optimization_report["database"]["improvements"].extend(optimizations)
                logger.info(f"✅ 优化数据库文件: {file_path.name}")
                return True
            
            return False
            
        except Exception as e:
            logger.warning(f"优化数据库文件失败 {file_path}: {e}")
            return False
    
    def add_index_suggestions(self, content: str) -> str:
        """添加数据库索引建议"""
        # 查找模型类
        model_pattern = r'class\s+(\w+)\s*\([^)]*Model[^)]*\):'
        matches = re.finditer(model_pattern, content)
        
        for match in matches:
            class_name = match.group(1)
            class_start = match.start()
            
            # 查找类的结束位置
            class_end = self.find_class_end(content, class_start)
            class_content = content[class_start:class_end]
            
            # 检查是否已有Meta类
            if 'class Meta:' not in class_content:
                # 添加Meta类和索引建议
                meta_class = f"""
    class Meta:
        # 性能优化: 添加常用查询字段的索引
        indexes = [
            # 根据实际查询需求添加索引
            # models.Index(fields=['created_at']),
            # models.Index(fields=['user_id']),
            # models.Index(fields=['status']),
        ]
        # 数据库表选项
        db_table = '{class_name.lower()}'
        ordering = ['-created_at']
"""
                
                # 在类的最后添加Meta类
                insert_pos = class_end - 1
                content = content[:insert_pos] + meta_class + content[insert_pos:]
        
        return content
    
    def find_class_end(self, content: str, class_start: int) -> int:
        """查找类的结束位置"""
        lines = content[class_start:].split('\n')
        indent_level = 0
        
        for i, line in enumerate(lines[1:], 1):
            if line.strip():
                current_indent = len(line) - len(line.lstrip())
                if current_indent <= indent_level and not line.startswith(' '):
                    return class_start + len('\n'.join(lines[:i]))
        
        return len(content)
    
    def optimize_queries(self, content: str) -> str:
        """优化查询语句"""
        optimizations = [
            # 优化N+1查询问题
            (r'\.filter\(([^)]+)\)\.all\(\)', r'.filter(\1).prefetch_related().all()[:1000]  # 限制查询结果数量'),
            
            # 添加查询限制
            (r'\.all\(\)(?!\s*\[:)', r'.all()[:1000]  # 限制查询结果数量'),
            
            # 优化exists查询
            (r'\.filter\(([^)]+)\)\.count\(\)\s*>\s*0', r'.filter(\1).exists()'),
            
            # 使用select_related优化外键查询
            (r'\.filter\(([^)]+)\)(?=.*__)', r'.select_related().filter(\1)'),
        ]
        
        for pattern, replacement in optimizations:
            content = re.sub(pattern, replacement, content)
        
        return content
    
    def add_query_cache(self, content: str) -> str:
        """添加查询缓存"""
        # 查找查询函数
        query_pattern = r'def\s+(\w*(?:get|find|search|query)\w*)\s*\([^)]*\):'
        
        matches = re.finditer(query_pattern, content)
        
        for match in matches:
            func_name = match.group(1)
            func_start = match.start()
            
            # 检查是否已有缓存装饰器
            before_func = content[:func_start]
            if '@cache' not in before_func[-200:]:
                # 添加缓存装饰器
                cache_decorator = f"""    @cache(timeout=300)  # 5分钟缓存
"""
                content = content[:func_start] + cache_decorator + content[func_start:]
        
        return content
    
    def optimize_batch_operations(self, content: str) -> str:
        """优化批量操作"""
        # 优化批量插入
        content = re.sub(
            r'for\s+\w+\s+in\s+\w+:\s*\n\s*\w+\.objects\.create\(',
            'bulk_data = []\nfor item in items:\n    bulk_data.append(Model(',
            content
        )
        
        # 添加批量创建建议
        if 'objects.create(' in content and 'bulk_create' not in content:
            content += """
# 性能优化建议: 使用bulk_create进行批量插入
# Model.objects.bulk_create(bulk_data, batch_size=1000)
"""
        
        return content
    
    def optimize_api(self):
        """API性能优化"""
        logger.info("🔧 开始API优化...")
        
        # 查找API相关文件
        api_files = []
        for pattern in ["**/main.py", "**/*api*.py", "**/*router*.py"]:
            api_files.extend(list(self.project_root.glob(pattern)))
        
        api_files = [f for f in api_files if self.is_api_file(f)]
        
        for file_path in api_files:
            try:
                optimized = self.optimize_api_file(file_path)
                if optimized:
                    self.optimization_report["api"]["optimized"] += 1
                self.optimization_report["api"]["total"] += 1
                
            except Exception as e:
                logger.warning(f"API文件优化失败 {file_path}: {e}")
        
        logger.info(f"✅ API优化完成: {self.optimization_report['api']['optimized']}/{self.optimization_report['api']['total']}")
    
    def is_api_file(self, file_path: Path) -> bool:
        """判断是否为API文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            api_indicators = [
                'from fastapi import',
                '@app.',
                'FastAPI(',
                'APIRouter(',
                '@router.',
                'app = FastAPI'
            ]
            
            return any(indicator in content for indicator in api_indicators)
            
        except Exception:
            return False
    
    def optimize_api_file(self, file_path: Path) -> bool:
        """优化单个API文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            optimizations = []
            
            # 优化1: 添加响应缓存
            content = self.add_response_cache(content)
            if content != original_content:
                optimizations.append("添加响应缓存")
            
            # 优化2: 添加请求限流
            content = self.add_rate_limiting(content)
            if content != original_content:
                optimizations.append("添加请求限流")
            
            # 优化3: 优化异步处理
            content = self.optimize_async_handling(content)
            if content != original_content:
                optimizations.append("优化异步处理")
            
            # 优化4: 添加响应压缩
            content = self.add_response_compression(content)
            if content != original_content:
                optimizations.append("添加响应压缩")
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.optimization_report["api"]["improvements"].extend(optimizations)
                logger.info(f"✅ 优化API文件: {file_path.name}")
                return True
            
            return False
            
        except Exception as e:
            logger.warning(f"优化API文件失败 {file_path}: {e}")
            return False
    
    def add_response_cache(self, content: str) -> str:
        """添加响应缓存"""
        # 查找GET路由
        get_pattern = r'@(?:app|router)\.get\s*\([^)]*\)'
        
        matches = re.finditer(get_pattern, content)
        
        for match in matches:
            route_start = match.start()
            
            # 检查是否已有缓存装饰器
            before_route = content[:route_start]
            if '@cache' not in before_route[-200:]:
                # 添加缓存装饰器
                cache_decorator = '@cache(expire=300)  # 5分钟缓存\n'
                content = content[:route_start] + cache_decorator + content[route_start:]
        
        return content
    
    def add_rate_limiting(self, content: str) -> str:
        """添加请求限流"""
        # 查找路由定义
        route_pattern = r'@(?:app|router)\.(get|post|put|delete)\s*\([^)]*\)'
        
        matches = re.finditer(route_pattern, content)
        
        for match in matches:
            route_start = match.start()
            
            # 检查是否已有限流装饰器
            before_route = content[:route_start]
            if '@limiter.limit' not in before_route[-200:]:
                # 添加限流装饰器
                limit_decorator = '@limiter.limit("100/minute")  # 每分钟100次请求\n'
                content = content[:route_start] + limit_decorator + content[route_start:]
        
        return content
    
    def optimize_async_handling(self, content: str) -> str:
        """优化异步处理"""
        # 将同步函数转换为异步函数
        sync_pattern = r'def\s+(\w+)\s*\([^)]*\):'
        
        def replace_with_async(match):
            func_name = match.group(1)
            # 只转换API路由函数
            if any(keyword in func_name.lower() for keyword in ['get', 'post', 'put', 'delete', 'api']):
                return f'async def {func_name}('
            return match.group(0)
        
        content = re.sub(sync_pattern, replace_with_async, content)
        
        return content
    
    def add_response_compression(self, content: str) -> str:
        """添加响应压缩"""
        if 'from fastapi import FastAPI' in content and 'GZipMiddleware' not in content:
            # 添加压缩中间件导入
            import_line = 'from fastapi.middleware.gzip import GZipMiddleware\n'
            content = import_line + content
            
            # 添加中间件配置
            if 'app = FastAPI(' in content:
                middleware_config = """
# 性能优化: 添加响应压缩
app.add_middleware(GZipMiddleware, minimum_size=1000)
"""
                app_line = content.find('app = FastAPI(')
                app_end = content.find('\n', app_line) + 1
                content = content[:app_end] + middleware_config + content[app_end:]
        
        return content
    
    def optimize_frontend(self):
        """前端性能优化"""
        logger.info("🎨 开始前端优化...")
        
        # 查找前端文件
        frontend_files = []
        for pattern in ["src/**/*.tsx", "src/**/*.ts", "src/**/*.js", "src/**/*.jsx"]:
            frontend_files.extend(list(self.project_root.glob(pattern)))
        
        for file_path in frontend_files:
            try:
                optimized = self.optimize_frontend_file(file_path)
                if optimized:
                    self.optimization_report["frontend"]["optimized"] += 1
                self.optimization_report["frontend"]["total"] += 1
                
            except Exception as e:
                logger.warning(f"前端文件优化失败 {file_path}: {e}")
        
        logger.info(f"✅ 前端优化完成: {self.optimization_report['frontend']['optimized']}/{self.optimization_report['frontend']['total']}")
    
    def optimize_frontend_file(self, file_path: Path) -> bool:
        """优化单个前端文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            optimizations = []
            
            # 优化1: 添加React.memo
            content = self.add_react_memo(content)
            if content != original_content:
                optimizations.append("添加React.memo")
            
            # 优化2: 优化useEffect依赖
            content = self.optimize_useeffect(content)
            if content != original_content:
                optimizations.append("优化useEffect依赖")
            
            # 优化3: 添加懒加载
            content = self.add_lazy_loading(content)
            if content != original_content:
                optimizations.append("添加懒加载")
            
            # 优化4: 优化图片加载
            content = self.optimize_images(content)
            if content != original_content:
                optimizations.append("优化图片加载")
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.optimization_report["frontend"]["improvements"].extend(optimizations)
                logger.info(f"✅ 优化前端文件: {file_path.name}")
                return True
            
            return False
            
        except Exception as e:
            logger.warning(f"优化前端文件失败 {file_path}: {e}")
            return False
    
    def add_react_memo(self, content: str) -> str:
        """添加React.memo优化"""
        # 查找函数组件
        component_pattern = r'const\s+(\w+)\s*=\s*\([^)]*\)\s*=>\s*{'
        
        matches = re.finditer(component_pattern, content)
        
        for match in matches:
            component_name = match.group(1)
            
            # 检查是否已经使用memo
            if f'React.memo({component_name})' not in content:
                # 在文件末尾添加memo导出
                export_pattern = f'export default {component_name}'
                if export_pattern in content:
                    content = content.replace(
                        export_pattern,
                        f'export default React.memo({component_name})'
                    )
        
        return content
    
    def optimize_useeffect(self, content: str) -> str:
        """优化useEffect依赖"""
        # 查找useEffect
        useeffect_pattern = r'useEffect\s*\(\s*\(\s*\)\s*=>\s*{[^}]*},\s*\[\s*\]\s*\)'
        
        # 添加依赖项建议注释
        content = re.sub(
            useeffect_pattern,
            lambda m: m.group(0) + '  // 检查是否需要添加依赖项',
            content
        )
        
        return content
    
    def add_lazy_loading(self, content: str) -> str:
        """添加懒加载"""
        # 查找组件导入
        import_pattern = r"import\s+(\w+)\s+from\s+['\"]([^'\"]+)['\"]"
        
        matches = re.finditer(import_pattern, content)
        
        for match in matches:
            component_name = match.group(1)
            import_path = match.group(2)
            
            # 如果是组件导入且路径包含screens或components
            if any(keyword in import_path for keyword in ['screens', 'components']) and component_name[0].isupper():
                # 替换为懒加载
                lazy_import = f"const {component_name} = React.lazy(() => import('{import_path}'))"
                content = content.replace(match.group(0), lazy_import)
        
        return content
    
    def optimize_images(self, content: str) -> str:
        """优化图片加载"""
        # 优化Image组件
        image_pattern = r'<Image\s+([^>]*)\s*/?>'
        
        def optimize_image_props(match):
            props = match.group(1)
            
            # 添加性能优化属性
            if 'loading=' not in props:
                props += ' loading="lazy"'
            if 'decoding=' not in props:
                props += ' decoding="async"'
            
            return f'<Image {props} />'
        
        content = re.sub(image_pattern, optimize_image_props, content)
        
        return content
    
    def generate_report(self):
        """生成优化报告"""
        # 计算总体评分
        total_optimized = (
            self.optimization_report["database"]["optimized"] +
            self.optimization_report["api"]["optimized"] +
            self.optimization_report["frontend"]["optimized"]
        )
        
        total_files = (
            self.optimization_report["database"]["total"] +
            self.optimization_report["api"]["total"] +
            self.optimization_report["frontend"]["total"]
        )
        
        if total_files > 0:
            self.optimization_report["overall_score"] = round((total_optimized / total_files) * 100, 2)
        
        # 保存报告
        report_file = self.project_root / "PERFORMANCE_OPTIMIZATION_REPORT.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.optimization_report, f, indent=2, ensure_ascii=False)
        
        # 生成Markdown报告
        self.generate_markdown_report()
        
        logger.info(f"📊 性能优化报告已生成: {report_file}")
        logger.info(f"🎯 总体优化率: {self.optimization_report['overall_score']}%")
    
    def generate_markdown_report(self):
        """生成Markdown格式的优化报告"""
        report = self.optimization_report
        
        content = f"""# 性能优化报告

## 优化概览

- **总体优化率**: {report['overall_score']}%
- **优化时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}

## 详细结果

### 📊 数据库优化
- **优化文件数**: {report['database']['optimized']}/{report['database']['total']}
- **优化率**: {round(report['database']['optimized']/max(report['database']['total'], 1)*100, 2)}%
- **优化项目**:
"""
        
        for improvement in report['database']['improvements']:
            content += f"  - {improvement}\n"
        
        content += f"""
### 🔧 API优化
- **优化文件数**: {report['api']['optimized']}/{report['api']['total']}
- **优化率**: {round(report['api']['optimized']/max(report['api']['total'], 1)*100, 2)}%
- **优化项目**:
"""
        
        for improvement in report['api']['improvements']:
            content += f"  - {improvement}\n"
        
        content += f"""
### 🎨 前端优化
- **优化文件数**: {report['frontend']['optimized']}/{report['frontend']['total']}
- **优化率**: {round(report['frontend']['optimized']/max(report['frontend']['total'], 1)*100, 2)}%
- **优化项目**:
"""
        
        for improvement in report['frontend']['improvements']:
            content += f"  - {improvement}\n"
        
        content += """
## 性能提升建议

### 数据库层面
1. 定期分析慢查询日志
2. 监控数据库连接池使用情况
3. 考虑读写分离和分库分表
4. 定期更新统计信息

### API层面
1. 实施API版本管理
2. 添加请求/响应日志
3. 监控API响应时间
4. 考虑使用CDN加速

### 前端层面
1. 实施代码分割
2. 优化打包配置
3. 使用Service Worker缓存
4. 监控Core Web Vitals

## 监控建议

建议设置以下性能监控指标：
- 数据库查询时间 < 100ms
- API响应时间 < 500ms
- 页面加载时间 < 3s
- 首屏渲染时间 < 1.5s

---

*报告生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        report_file = self.project_root / "PERFORMANCE_OPTIMIZATION_REPORT.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(content)

def main():
    """主函数"""
    project_root = os.getcwd()
    
    logger.info("🚀 启动性能优化器")
    
    optimizer = PerformanceOptimizer(project_root)
    
    try:
        success = optimizer.optimize_all()
        
        if success:
            logger.info("🎉 性能优化完成！")
            return 0
        else:
            logger.warning("⚠️ 性能优化失败")
            return 1
            
    except Exception as e:
        logger.error(f"❌ 性能优化失败: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 