#!/usr/bin/env python3
"""
索克生活项目 - 硬编码密钥检测和修复工具
自动检测项目中的硬编码敏感信息并提供修复建议
"""

import os
import re
import json
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class SecretPattern:
    """敏感信息模式"""
    file_path: str
    line_number: int
    pattern_type: str
    matched_text: str
    context: str
    severity: str
    suggested_fix: str

class HardcodedSecretsFixer:
    """硬编码密钥修复器"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.secrets_found = []
        self.backup_dir = self.project_root / "backups" / "secrets_fix"
        
        # 敏感信息检测模式
        self.secret_patterns = {
            'api_key': {
                'patterns': [
                    r'api[_-]?key\s*[=:]\s*["\']([a-zA-Z0-9_-]{20,})["\']',
                    r'apikey\s*[=:]\s*["\']([a-zA-Z0-9_-]{20,})["\']',
                    r'API[_-]?KEY\s*[=:]\s*["\']([a-zA-Z0-9_-]{20,})["\']'
                ],
                'severity': 'HIGH',
                'description': 'API密钥'
            },
            'secret_key': {
                'patterns': [
                    r'secret[_-]?key\s*[=:]\s*["\']([a-zA-Z0-9_-]{20,})["\']',
                    r'SECRET[_-]?KEY\s*[=:]\s*["\']([a-zA-Z0-9_-]{20,})["\']'
                ],
                'severity': 'HIGH',
                'description': '密钥'
            },
            'password': {
                'patterns': [
                    r'password\s*[=:]\s*["\']([^"\']{8,})["\']',
                    r'PASSWORD\s*[=:]\s*["\']([^"\']{8,})["\']',
                    r'pwd\s*[=:]\s*["\']([^"\']{8,})["\']'
                ],
                'severity': 'HIGH',
                'description': '密码'
            },
            'token': {
                'patterns': [
                    r'token\s*[=:]\s*["\']([a-zA-Z0-9_-]{20,})["\']',
                    r'TOKEN\s*[=:]\s*["\']([a-zA-Z0-9_-]{20,})["\']',
                    r'access[_-]?token\s*[=:]\s*["\']([a-zA-Z0-9_-]{20,})["\']'
                ],
                'severity': 'HIGH',
                'description': '访问令牌'
            },
            'database_url': {
                'patterns': [
                    r'database[_-]?url\s*[=:]\s*["\']([^"\']+://[^"\']+)["\']',
                    r'db[_-]?url\s*[=:]\s*["\']([^"\']+://[^"\']+)["\']',
                    r'DATABASE[_-]?URL\s*[=:]\s*["\']([^"\']+://[^"\']+)["\']'
                ],
                'severity': 'MEDIUM',
                'description': '数据库连接字符串'
            },
            'private_key': {
                'patterns': [
                    r'private[_-]?key\s*[=:]\s*["\']([^"\']{50,})["\']',
                    r'PRIVATE[_-]?KEY\s*[=:]\s*["\']([^"\']{50,})["\']',
                    r'-----BEGIN PRIVATE KEY-----',
                    r'-----BEGIN RSA PRIVATE KEY-----'
                ],
                'severity': 'CRITICAL',
                'description': '私钥'
            },
            'aws_credentials': {
                'patterns': [
                    r'aws[_-]?access[_-]?key[_-]?id\s*[=:]\s*["\']([A-Z0-9]{20})["\']',
                    r'aws[_-]?secret[_-]?access[_-]?key\s*[=:]\s*["\']([a-zA-Z0-9/+=]{40})["\']'
                ],
                'severity': 'CRITICAL',
                'description': 'AWS凭证'
            },
            'jwt_secret': {
                'patterns': [
                    r'jwt[_-]?secret\s*[=:]\s*["\']([^"\']{20,})["\']',
                    r'JWT[_-]?SECRET\s*[=:]\s*["\']([^"\']{20,})["\']'
                ],
                'severity': 'HIGH',
                'description': 'JWT密钥'
            }
        }
        
        # 排除的文件和目录
        self.exclude_patterns = {
            'venv', 'env', '.env', '__pycache__', '.git', 
            'node_modules', '.pytest_cache', 'dist', 'build',
            '.idea', '.vscode', '*.pyc', '*.pyo', '*.egg-info'
        }
    
    def scan_for_secrets(self) -> List[SecretPattern]:
        """扫描项目中的硬编码敏感信息"""
        logger.info("🔍 扫描硬编码敏感信息...")
        
        python_files = self._get_python_files()
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                    for line_num, line in enumerate(lines, 1):
                        self._check_line_for_secrets(file_path, line_num, line)
                        
            except Exception as e:
                logger.warning(f"无法读取文件 {file_path}: {e}")
        
        logger.info(f"发现 {len(self.secrets_found)} 个潜在的硬编码敏感信息")
        return self.secrets_found
    
    def _get_python_files(self) -> List[Path]:
        """获取所有Python文件"""
        python_files = []
        
        for root, dirs, files in os.walk(self.project_root):
            # 排除特定目录
            dirs[:] = [d for d in dirs if not any(
                pattern in d for pattern in self.exclude_patterns
            )]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    # 排除备份文件
                    if 'backup' not in str(file_path).lower():
                        python_files.append(file_path)
        
        return python_files
    
    def _check_line_for_secrets(self, file_path: Path, line_num: int, line: str):
        """检查单行代码中的敏感信息"""
        line_stripped = line.strip()
        
        # 跳过注释行
        if line_stripped.startswith('#'):
            return
        
        for pattern_type, pattern_info in self.secret_patterns.items():
            for pattern in pattern_info['patterns']:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    # 检查是否是真正的硬编码值
                    if self._is_likely_hardcoded(match.group()):
                        secret = SecretPattern(
                            file_path=str(file_path.relative_to(self.project_root)),
                            line_number=line_num,
                            pattern_type=pattern_type,
                            matched_text=match.group(),
                            context=line.strip(),
                            severity=pattern_info['severity'],
                            suggested_fix=self._generate_fix_suggestion(
                                pattern_type, match.group()
                            )
                        )
                        self.secrets_found.append(secret)
    
    def _is_likely_hardcoded(self, text: str) -> bool:
        """判断是否可能是硬编码值"""
        # 排除明显的占位符和变量
        placeholders = [
            'your_api_key', 'your_secret', 'your_password',
            'api_key_here', 'secret_here', 'password_here',
            'changeme', 'replace_me', 'todo', 'fixme',
            'example', 'sample', 'test', 'demo'
        ]
        
        text_lower = text.lower()
        return not any(placeholder in text_lower for placeholder in placeholders)
    
    def _generate_fix_suggestion(self, pattern_type: str, matched_text: str) -> str:
        """生成修复建议"""
        env_var_name = self._suggest_env_var_name(pattern_type)
        
        return f"""
建议修复方案：
1. 在 .env 文件中添加：{env_var_name}=your_actual_value
2. 在代码中替换为：os.getenv('{env_var_name}')
3. 确保 .env 文件已添加到 .gitignore
"""
    
    def _suggest_env_var_name(self, pattern_type: str) -> str:
        """建议环境变量名称"""
        mapping = {
            'api_key': 'API_KEY',
            'secret_key': 'SECRET_KEY',
            'password': 'DATABASE_PASSWORD',
            'token': 'ACCESS_TOKEN',
            'database_url': 'DATABASE_URL',
            'private_key': 'PRIVATE_KEY',
            'aws_credentials': 'AWS_ACCESS_KEY_ID',
            'jwt_secret': 'JWT_SECRET'
        }
        return mapping.get(pattern_type, 'SECRET_VALUE')
    
    def create_env_template(self) -> str:
        """创建环境变量模板文件"""
        logger.info("📝 创建环境变量模板...")
        
        env_template_path = self.project_root / ".env.template"
        
        # 收集所有需要的环境变量
        env_vars = set()
        for secret in self.secrets_found:
            env_var_name = self._suggest_env_var_name(secret.pattern_type)
            env_vars.add(env_var_name)
        
        # 生成模板内容
        template_content = """# 索克生活项目环境变量配置模板
# 复制此文件为 .env 并填入实际值

# 数据库配置
DATABASE_URL=postgresql://user:password@localhost:5432/suoke_life
DATABASE_PASSWORD=your_database_password

# API密钥
API_KEY=your_api_key_here
SECRET_KEY=your_secret_key_here

# JWT配置
JWT_SECRET=your_jwt_secret_here

# 第三方服务
ACCESS_TOKEN=your_access_token_here

# AWS配置（如果使用）
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key

# 其他敏感配置
PRIVATE_KEY=your_private_key_here

# 注意：
# 1. 请勿将此文件中的实际值提交到版本控制
# 2. 确保 .env 文件已添加到 .gitignore
# 3. 在生产环境中使用更安全的密钥管理方案
"""
        
        with open(env_template_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        return str(env_template_path)
    
    def create_config_manager(self) -> str:
        """创建配置管理器"""
        logger.info("⚙️ 创建配置管理器...")
        
        config_dir = self.project_root / "src" / "core" / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        
        config_file = config_dir / "settings.py"
        
        config_content = '''"""
索克生活项目 - 配置管理器
统一管理项目配置和环境变量
"""

import os
import logging
from typing import Optional, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class ConfigManager:
    """配置管理器"""
    
    def __init__(self):
        self._load_environment()
        self._validate_required_settings()
    
    def _load_environment(self):
        """加载环境变量"""
        # 查找 .env 文件
        env_file = Path(__file__).parent.parent.parent.parent / ".env"
        if env_file.exists():
            load_dotenv(env_file)
            logger.info(f"已加载环境变量文件: {env_file}")
        else:
            logger.warning("未找到 .env 文件，使用系统环境变量")
    
    def _validate_required_settings(self):
        """验证必需的配置项"""
        required_settings = [
            'SECRET_KEY',
            'DATABASE_URL'
        ]
        
        missing_settings = []
        for setting in required_settings:
            if not self.get(setting):
                missing_settings.append(setting)
        
        if missing_settings:
            logger.error(f"缺少必需的配置项: {missing_settings}")
            raise ValueError(f"缺少必需的配置项: {missing_settings}")
    
    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """获取配置值"""
        value = os.getenv(key, default)
        if value is None:
            logger.warning(f"配置项 {key} 未设置")
        return value
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """获取布尔类型配置值"""
        value = self.get(key)
        if value is None:
            return default
        return value.lower() in ('true', '1', 'yes', 'on')
    
    def get_int(self, key: str, default: int = 0) -> int:
        """获取整数类型配置值"""
        value = self.get(key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            logger.warning(f"配置项 {key} 不是有效的整数: {value}")
            return default
    
    def get_list(self, key: str, separator: str = ',', default: list = None) -> list:
        """获取列表类型配置值"""
        value = self.get(key)
        if value is None:
            return default or []
        return [item.strip() for item in value.split(separator) if item.strip()]
    
    # 数据库配置
    @property
    def database_url(self) -> str:
        return self.get('DATABASE_URL', 'sqlite:///suoke_life.db')
    
    @property
    def database_password(self) -> Optional[str]:
        return self.get('DATABASE_PASSWORD')
    
    # 安全配置
    @property
    def secret_key(self) -> str:
        return self.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    @property
    def jwt_secret(self) -> str:
        return self.get('JWT_SECRET', self.secret_key)
    
    # API配置
    @property
    def api_key(self) -> Optional[str]:
        return self.get('API_KEY')
    
    @property
    def access_token(self) -> Optional[str]:
        return self.get('ACCESS_TOKEN')
    
    # AWS配置
    @property
    def aws_access_key_id(self) -> Optional[str]:
        return self.get('AWS_ACCESS_KEY_ID')
    
    @property
    def aws_secret_access_key(self) -> Optional[str]:
        return self.get('AWS_SECRET_ACCESS_KEY')
    
    # 应用配置
    @property
    def debug(self) -> bool:
        return self.get_bool('DEBUG', False)
    
    @property
    def log_level(self) -> str:
        return self.get('LOG_LEVEL', 'INFO')
    
    @property
    def host(self) -> str:
        return self.get('HOST', '0.0.0.0')
    
    @property
    def port(self) -> int:
        return self.get_int('PORT', 8000)

# 全局配置实例
config = ConfigManager()
'''
        
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        return str(config_file)
    
    def update_gitignore(self):
        """更新 .gitignore 文件"""
        logger.info("📝 更新 .gitignore 文件...")
        
        gitignore_path = self.project_root / ".gitignore"
        
        # 需要添加的忽略规则
        ignore_rules = [
            "# 环境变量和敏感信息",
            ".env",
            ".env.local",
            ".env.*.local",
            "*.key",
            "*.pem",
            "secrets/",
            "credentials/",
            "",
            "# 备份文件",
            "backups/",
            "*.backup",
            "*.bak"
        ]
        
        # 读取现有内容
        existing_content = ""
        if gitignore_path.exists():
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                existing_content = f.read()
        
        # 添加新规则
        new_rules = []
        for rule in ignore_rules:
            if rule not in existing_content:
                new_rules.append(rule)
        
        if new_rules:
            with open(gitignore_path, 'a', encoding='utf-8') as f:
                f.write('\n' + '\n'.join(new_rules) + '\n')
            logger.info(f"已向 .gitignore 添加 {len(new_rules)} 条新规则")
    
    def generate_report(self) -> str:
        """生成修复报告"""
        logger.info("📊 生成硬编码密钥修复报告...")
        
        report = f"""# 硬编码密钥检测和修复报告

## 📊 扫描结果概览

- **扫描文件数量**: {len(self._get_python_files())}
- **发现敏感信息**: {len(self.secrets_found)}
- **严重性分布**:
"""
        
        # 统计严重性分布
        severity_count = {}
        for secret in self.secrets_found:
            severity_count[secret.severity] = severity_count.get(secret.severity, 0) + 1
        
        for severity, count in severity_count.items():
            report += f"  - {severity}: {count}\n"
        
        report += "\n## 🔍 发现的敏感信息详情\n\n"
        
        # 按严重性分组
        by_severity = {}
        for secret in self.secrets_found:
            if secret.severity not in by_severity:
                by_severity[secret.severity] = []
            by_severity[secret.severity].append(secret)
        
        for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            if severity in by_severity:
                report += f"### {severity} 严重性\n\n"
                for secret in by_severity[severity]:
                    report += f"**文件**: `{secret.file_path}:{secret.line_number}`\n"
                    report += f"**类型**: {secret.pattern_type}\n"
                    report += f"**上下文**: `{secret.context}`\n"
                    report += f"**修复建议**: {secret.suggested_fix}\n\n"
        
        report += """
## 🛠️ 修复步骤

### 1. 立即行动
1. 检查上述发现的敏感信息是否为真实凭证
2. 如果是真实凭证，立即更换这些凭证
3. 确保 .env 文件已添加到 .gitignore

### 2. 使用配置管理器
```python
from src.core.config.settings import config

# 替换硬编码值
api_key = config.api_key
database_url = config.database_url
```

### 3. 环境变量设置
复制 `.env.template` 为 `.env` 并填入实际值：
```bash
cp .env.template .env
# 编辑 .env 文件填入实际值
```

### 4. 生产环境安全
- 使用密钥管理服务（如 AWS Secrets Manager）
- 定期轮换密钥
- 实施最小权限原则
- 监控密钥使用情况

## ⚠️ 安全提醒

1. **永远不要**将真实的密钥提交到版本控制
2. **定期检查**代码中的硬编码敏感信息
3. **使用工具**自动化检测敏感信息泄露
4. **培训团队**关于安全编码实践
"""
        
        return report

def main():
    """主函数"""
    project_root = os.getcwd()
    print('🔐 索克生活项目 - 硬编码密钥检测和修复工具')
    print('=' * 60)
    
    fixer = HardcodedSecretsFixer(project_root)
    
    # 1. 扫描硬编码敏感信息
    secrets = fixer.scan_for_secrets()
    
    # 2. 创建环境变量模板
    env_template = fixer.create_env_template()
    print(f"✅ 已创建环境变量模板: {env_template}")
    
    # 3. 创建配置管理器
    config_manager = fixer.create_config_manager()
    print(f"✅ 已创建配置管理器: {config_manager}")
    
    # 4. 更新 .gitignore
    fixer.update_gitignore()
    print("✅ 已更新 .gitignore 文件")
    
    # 5. 生成报告
    report = fixer.generate_report()
    
    # 保存报告
    report_file = Path(project_root) / 'hardcoded_secrets_report.md'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"📊 修复报告已保存到: {report_file}")
    
    if secrets:
        print(f"\n⚠️  发现 {len(secrets)} 个潜在的硬编码敏感信息，请查看报告详情")
    else:
        print("\n✅ 未发现硬编码敏感信息")

if __name__ == "__main__":
    main() 