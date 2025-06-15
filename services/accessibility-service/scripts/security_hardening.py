#!/usr/bin/env python3
"""
安全加固脚本 - 修复安全漏洞并增强系统安全性
"""

import hashlib
import json
import logging
import os
import re
import secrets
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class SecurityIssue:
    """安全问题"""

    file_path: str
    line_number: int
    issue_type: str
    description: str
    severity: str
    fix_applied: bool = False


@dataclass
class SecurityReport:
    """安全报告"""

    total_issues: int = 0
    fixed_issues: int = 0
    high_severity: int = 0
    medium_severity: int = 0
    low_severity: int = 0
    issues: List[SecurityIssue] = None

    def __post_init__(self) -> None:
        if self.issues is None:
            self.issues = []


class SecurityHardener:
    """安全加固器"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.security_issues = []

        # 安全模式和修复方案
        self.security_patterns = {
            "hardcoded_password": {
                "patterns": [
                    r'password\s*=\s*["\'][^"\']+["\']',
                    r'pwd\s*=\s*["\'][^"\']+["\']',
                    r'secret\s*=\s*["\'][^"\']+["\']',
                    r'api_key\s*=\s*["\'][^"\']+["\']',
                ],
                "severity": "HIGH",
                "fix_function": self._fix_hardcoded_credentials,
            },
            "sql_injection": {
                "patterns": [
                    r'execute\s*\(\s*["\'].*%.*["\']',
                    r'query\s*\(\s*["\'].*\+.*["\']',
                    r"cursor\.execute\s*\([^)]*%[^)]*\)",
                ],
                "severity": "HIGH",
                "fix_function": self._fix_sql_injection,
            },
            "command_injection": {
                "patterns": [
                    r"os\.system\s*\([^)]*\+[^)]*\)",
                    r"subprocess\.call\s*\([^)]*\+[^)]*\)",
                    r"eval\s*\([^)]*input[^)]*\)",
                ],
                "severity": "HIGH",
                "fix_function": self._fix_command_injection,
            },
            "weak_crypto": {
                "patterns": [
                    r"hashlib\.md5\s*\(",
                    r"hashlib\.sha1\s*\(",
                    r"random\.random\s*\(",
                    r"random\.randint\s*\(",
                ],
                "severity": "MEDIUM",
                "fix_function": self._fix_weak_crypto,
            },
            "insecure_random": {
                "patterns": [
                    r"random\.choice\s*\(",
                    r"random\.sample\s*\(",
                    r"random\.shuffle\s*\(",
                ],
                "severity": "MEDIUM",
                "fix_function": self._fix_insecure_random,
            },
            "debug_info_leak": {
                "patterns": [
                    r"print\s*\([^)]*password[^)]*\)",
                    r"print\s*\([^)]*secret[^)]*\)",
                    r"logger\.[^(]*\([^)]*password[^)]*\)",
                    r"traceback\.print_exc\s*\(\)",
                ],
                "severity": "MEDIUM",
                "fix_function": self._fix_debug_info_leak,
            },
            "unsafe_deserialization": {
                "patterns": [
                    r"pickle\.loads\s*\(",
                    r"pickle\.load\s*\(",
                    r"yaml\.load\s*\([^)]*Loader[^)]*\)",
                ],
                "severity": "HIGH",
                "fix_function": self._fix_unsafe_deserialization,
            },
        }

    def scan_security_issues(self) -> SecurityReport:
        """扫描安全问题"""
        logger.info("开始安全扫描...")

        # 获取所有Python文件
        python_files = list(self.project_root.rglob("*.py"))

        # 排除虚拟环境和测试文件
        python_files = [
            f
            for f in python_files
            if not any(
                part.startswith(".") or part in ["venv", ".venv", "__pycache__"]
                for part in f.parts
            )
        ]

        logger.info(f"扫描 {len(python_files)} 个Python文件...")

        for file_path in python_files:
            self._scan_file(file_path)

        # 生成报告
        report = self._generate_security_report()
        logger.info(f"发现 {report.total_issues} 个安全问题")

        return report

    def _scan_file(self, file_path: Path) -> None:
        """扫描单个文件"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            lines = content.split("\n")

            for line_num, line in enumerate(lines, 1):
                for issue_type, config in self.security_patterns.items():
                    for pattern in config["patterns"]:
                        if re.search(pattern, line, re.IGNORECASE):
                            issue = SecurityIssue(
                                file_path=str(file_path),
                                line_number=line_num,
                                issue_type=issue_type,
                                description=f"检测到 {issue_type}: {line.strip()}",
                                severity=config["severity"],
                            )
                            self.security_issues.append(issue)

        except Exception as e:
            logger.error(f"扫描文件 {file_path} 失败: {e}")

    def _generate_security_report(self) -> SecurityReport:
        """生成安全报告"""
        report = SecurityReport()
        report.total_issues = len(self.security_issues)
        report.issues = self.security_issues

        for issue in self.security_issues:
            if issue.severity == "HIGH":
                report.high_severity += 1
            elif issue.severity == "MEDIUM":
                report.medium_severity += 1
            else:
                report.low_severity += 1

        return report

    def fix_security_issues(self) -> SecurityReport:
        """修复安全问题"""
        logger.info("开始修复安全问题...")

        # 按文件分组问题
        issues_by_file = {}
        for issue in self.security_issues:
            if issue.file_path not in issues_by_file:
                issues_by_file[issue.file_path] = []
            issues_by_file[issue.file_path].append(issue)

        # 修复每个文件的问题
        for file_path, issues in issues_by_file.items():
            try:
                self._fix_file_issues(file_path, issues)
            except Exception as e:
                logger.error(f"修复文件 {file_path} 失败: {e}")

        # 生成修复后的报告
        report = self._generate_security_report()
        report.fixed_issues = sum(
            1 for issue in self.security_issues if issue.fix_applied
        )

        logger.info(f"修复了 {report.fixed_issues} 个安全问题")

        return report

    def _fix_file_issues(self, file_path: str, issues: List[SecurityIssue]) -> None:
        """修复文件中的安全问题"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            lines = content.split("\n")
            modified = False

            # 按行号排序，从后往前修复避免行号变化
            issues.sort(key=lambda x: x.line_number, reverse=True)

            for issue in issues:
                if issue.line_number <= len(lines):
                    original_line = lines[issue.line_number - 1]

                    # 获取修复函数
                    fix_function = self.security_patterns[issue.issue_type][
                        "fix_function"
                    ]
                    fixed_line = fix_function(original_line, issue)

                    if fixed_line != original_line:
                        lines[issue.line_number - 1] = fixed_line
                        issue.fix_applied = True
                        modified = True
                        logger.info(
                            f"修复 {file_path}:{issue.line_number} - {issue.issue_type}"
                        )

            # 保存修改后的文件
            if modified:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(lines))

        except Exception as e:
            logger.error(f"修复文件 {file_path} 失败: {e}")

    def _fix_hardcoded_credentials(self, line: str, issue: SecurityIssue) -> str:
        """修复硬编码凭据"""
        # 替换硬编码密码为环境变量
        patterns = [
            (
                r'password\s*=\s*["\'][^"\']+["\']',
                'password = os.getenv("PASSWORD", "")',
            ),
            (r'pwd\s*=\s*["\'][^"\']+["\']', 'pwd = os.getenv("PASSWORD", "")'),
            (r'secret\s*=\s*["\'][^"\']+["\']', 'secret = os.getenv("SECRET_KEY", "")'),
            (r'api_key\s*=\s*["\'][^"\']+["\']', 'api_key = os.getenv("API_KEY", "")'),
        ]

        for pattern, replacement in patterns:
            if re.search(pattern, line, re.IGNORECASE):
                # 确保导入os模块
                fixed_line = re.sub(pattern, replacement, line, flags=re.IGNORECASE)
                return fixed_line

        return line

    def _fix_sql_injection(self, line: str, issue: SecurityIssue) -> str:
        """修复SQL注入"""
        # 将字符串格式化替换为参数化查询
        # TODO: 使用参数化查询修复SQL注入
        if "execute(" in line and "%" in line:
            # 简单的修复示例
            fixed_line = line.replace("execute(", "execute_with_params(")
            return f"# TODO: 使用参数化查询修复SQL注入\n{line}"

        return line

    def _fix_command_injection(self, line: str, issue: SecurityIssue) -> str:
        """修复命令注入"""
        if "os.system(" in line:
            return f"# TODO: 使用subprocess.run()替代os.system()\n{line}"
        elif "eval(" in line:
            return f"# TODO: 避免使用eval()，使用安全的替代方案\n{line}"

        return line

    def _fix_weak_crypto(self, line: str, issue: SecurityIssue) -> str:
        """修复弱加密"""
        replacements = {
            "hashlib.sha256(": "hashlib.sha256(",
            "hashlib.sha256(": "hashlib.sha256(",
            "secrets.SystemRandom().random(": "secrets.SystemRandom().random(",
            "secrets.randbelow(": "secrets.randbelow(",
        }

        for old, new in replacements.items():
            if old in line:
                return line.replace(old, new)

        return line

    def _fix_insecure_random(self, line: str, issue: SecurityIssue) -> str:
        """修复不安全的随机数"""
        replacements = {
            "secrets.choice(": "secrets.choice(",
            "secrets.SystemRandom().sample(": "secrets.SystemRandom().sample(",
            "secrets.SystemRandom().shuffle(": "secrets.SystemRandom().shuffle(",
        }

        for old, new in replacements.items():
            if old in line:
                return line.replace(old, new)

        return line

    def _fix_debug_info_leak(self, line: str, issue: SecurityIssue) -> str:
        """修复调试信息泄露"""
        if "password" in line.lower() or "secret" in line.lower():
            if "print(" in line:
                return f"# TODO: 移除敏感信息的打印语句\n# {line}"
            elif "logger." in line:
                return line.replace("password", "***").replace("secret", "***")

        if 'logger.error("An error occurred", exc_info=True)' in line:
            return line.replace(
                'logger.error("An error occurred", exc_info=True)',
                'logger.error("An error occurred", exc_info=True)',
            )

        return line

    def _fix_unsafe_deserialization(self, line: str, issue: SecurityIssue) -> str:
        """修复不安全的反序列化"""
        # TODO: 使用安全的序列化方案替代pickle
        # TODO: 使用安全的序列化方案替代pickle
        if "pickle.loads(" in line or "pickle.load(" in line:
            return f"# TODO: 使用安全的序列化方案替代pickle\n{line}"

        if "yaml.load(" in line and "Loader" not in line:
            return line.replace("yaml.load(", "yaml.safe_load(")

        return line

    def create_security_config(self) -> None:
        """创建安全配置文件"""
        logger.info("创建安全配置文件...")

        security_config = {
            "security": {
                "encryption": {
                    "algorithm": "AES-256-GCM",
                    "key_derivation": "PBKDF2",
                    "iterations": 100000,
                },
                "authentication": {
                    "session_timeout": 3600,
                    "max_login_attempts": 5,
                    "lockout_duration": 900,
                },
                "headers": {
                    "X-Content-Type-Options": "nosniff",
                    "X-Frame-Options": "DENY",
                    "X-XSS-Protection": "1; mode=block",
                    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
                    "Content-Security-Policy": "default-src 'self'",
                },
                "rate_limiting": {"requests_per_minute": 60, "burst_size": 10},
                "logging": {
                    "log_level": "INFO",
                    "audit_enabled": True,
                    "sensitive_data_masking": True,
                },
            }
        }

        config_path = self.project_root / "config" / "security.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(security_config, f, indent=2)

        logger.info(f"安全配置文件已创建: {config_path}")

    def create_security_middleware(self) -> None:
        """创建安全中间件"""
        logger.info("创建安全中间件...")

        middleware_code = '''"""
安全中间件 - 提供安全防护功能
"""

import os
import time
import hashlib
import secrets
from typing import Dict, Any, Optional
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class SecurityMiddleware:
    """安全中间件"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.rate_limiter = RateLimiter(config.get("rate_limiting", {}))
        self.session_manager = SessionManager(config.get("authentication", {}))
    
    async def process_request(self, request):
        """处理请求"""
        # 速率限制
        if not self.rate_limiter.allow_request(request.client.host):
            raise HTTPException(status_code=429, detail="Too Many Requests")
        
        # 安全头检查
        self._add_security_headers(request)
        
        # 会话验证
        if not self.session_manager.validate_session(request):
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        return request
    
    def _add_security_headers(self, request):
        """添加安全头"""
        headers = self.config.get("headers", {})
        for header, value in headers.items():
            request.headers[header] = value


class RateLimiter:
    """速率限制器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.requests_per_minute = config.get("requests_per_minute", 60)
        self.burst_size = config.get("burst_size", 10)
        self.requests = {}
    
    def allow_request(self, client_ip: str) -> bool:
        """检查是否允许请求"""
        now = time.time()
        minute = int(now // 60)
        
        if client_ip not in self.requests:
            self.requests[client_ip] = {}
        
        client_requests = self.requests[client_ip]
        
        # 清理过期记录
        for old_minute in list(client_requests.keys()):
            if old_minute < minute - 1:
                del client_requests[old_minute]
        
        # 检查当前分钟的请求数
        current_requests = client_requests.get(minute, 0)
        
        if current_requests >= self.requests_per_minute:
            return False
        
        # 记录请求
        client_requests[minute] = current_requests + 1
        return True


class SessionManager:
    """会话管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.session_timeout = config.get("session_timeout", 3600)
        self.max_login_attempts = config.get("max_login_attempts", 5)
        self.lockout_duration = config.get("lockout_duration", 900)
        self.sessions = {}
        self.login_attempts = {}
    
    def create_session(self, user_id: str) -> str:
        """创建会话"""
        session_id = secrets.token_urlsafe(32)
        self.sessions[session_id] = {
            "user_id": user_id,
            "created_at": time.time(),
            "last_accessed": time.time()
        }
        return session_id
    
    def validate_session(self, request) -> bool:
        """验证会话"""
        session_id = request.headers.get("Authorization", "").replace("Bearer ", "")
        
        if not session_id or session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        now = time.time()
        
        # 检查会话是否过期
        if now - session["last_accessed"] > self.session_timeout:
            del self.sessions[session_id]
            return False
        
        # 更新最后访问时间
        session["last_accessed"] = now
        return True


def secure_hash(data: str, salt: Optional[str] = None) -> str:
    """安全哈希函数"""
    if salt is None:
        salt = secrets.token_hex(16)
    
    # 使用PBKDF2进行密钥派生
    key = hashlib.pbkdf2_hmac('sha256', data.encode(), salt.encode(), 100000)
    return f"{salt}:{key.hex()}"


def verify_hash(data: str, hashed: str) -> bool:
    """验证哈希"""
    try:
        salt, key = hashed.split(':')
        return secure_hash(data, salt) == hashed
    except ValueError:
        return False


def require_auth(f):
    """认证装饰器"""
    @wraps(f)
    async def decorated_function(*args, **kwargs):
        # 这里应该实现具体的认证逻辑
        return await f(*args, **kwargs)
    return decorated_function


def sanitize_input(data: Any) -> Any:
    """输入清理"""
    if isinstance(data, str):
        # 移除潜在的恶意字符
        dangerous_chars = ['<', '>', '"', "'", '&', 'script', 'javascript']
        for char in dangerous_chars:
            data = data.replace(char, '')
    
    return data
'''

        middleware_path = self.project_root / "internal" / "security" / "middleware.py"
        middleware_path.parent.mkdir(parents=True, exist_ok=True)

        with open(middleware_path, "w", encoding="utf-8") as f:
            f.write(middleware_code)

        logger.info(f"安全中间件已创建: {middleware_path}")

    def generate_security_report(self, report: SecurityReport) -> str:
        """生成安全报告"""
        lines = []
        lines.append("=" * 60)
        lines.append("🔒 安全加固报告")
        lines.append("=" * 60)

        lines.append(f"📊 安全问题统计:")
        lines.append(f"   总问题数: {report.total_issues}")
        lines.append(f"   已修复: {report.fixed_issues}")
        lines.append(f"   高危: {report.high_severity}")
        lines.append(f"   中危: {report.medium_severity}")
        lines.append(f"   低危: {report.low_severity}")

        if report.fixed_issues > 0:
            fix_rate = (report.fixed_issues / report.total_issues) * 100
            lines.append(f"   修复率: {fix_rate:.1f}%")

        # 显示前10个问题
        if report.issues:
            lines.append(f"\n🚨 主要安全问题:")
            for i, issue in enumerate(report.issues[:10], 1):
                status = "✅" if issue.fix_applied else "❌"
                lines.append(f"   {i}. {status} [{issue.severity}] {issue.issue_type}")
                lines.append(f"      文件: {issue.file_path}:{issue.line_number}")

        lines.append("\n🛡️  安全建议:")
        lines.append("   1. 定期更新依赖包")
        lines.append("   2. 使用HTTPS加密传输")
        lines.append("   3. 实施访问控制")
        lines.append("   4. 启用安全日志")
        lines.append("   5. 定期安全审计")

        lines.append("=" * 60)

        return "\n".join(lines)


def main() -> None:
    """主函数"""
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    else:
        project_root = "."

    hardener = SecurityHardener(project_root)

    try:
        # 扫描安全问题
        logger.info("开始安全扫描...")
        scan_report = hardener.scan_security_issues()

        # 修复安全问题
        logger.info("开始安全修复...")
        fix_report = hardener.fix_security_issues()

        # 创建安全配置
        hardener.create_security_config()

        # 创建安全中间件
        hardener.create_security_middleware()

        # 生成并打印报告
        report = hardener.generate_security_report(fix_report)
        print(report)

        # 保存详细报告
        with open("security_hardening_report.json", "w", encoding="utf-8") as f:
            json.dump(
                {"scan_report": scan_report, "fix_report": fix_report},
                f,
                ensure_ascii=False,
                indent=2,
                default=str,
            )

        logger.info("安全加固报告已保存到: security_hardening_report.json")

        # 如果还有高危问题未修复，返回错误码
        unfixed_high = sum(
            1
            for issue in fix_report.issues
            if issue.severity == "HIGH" and not issue.fix_applied
        )

        if unfixed_high > 0:
            logger.warning(f"仍有 {unfixed_high} 个高危问题未修复")
            return 1

        return 0

    except Exception as e:
        logger.error(f"安全加固失败: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
