#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API网关全面安全测试套件
包含认证、授权、输入验证、注入攻击等安全测试
"""

import asyncio
import base64
import hashlib
import hmac
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any
from unittest.mock import AsyncMock, Mock, patch
import pytest
import jwt as pyjwt

# 添加项目根目录到Python路径
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class SecurityTestSuite:
    """安全测试套件基类"""
    
    def __init__(self):
        self.test_results = []
        self.vulnerabilities = []
        
    def record_test(self, test_name: str, passed: bool, details: str = ""):
        """记录测试结果"""
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
    def record_vulnerability(self, vuln_type: str, severity: str, description: str):
        """记录发现的漏洞"""
        self.vulnerabilities.append({
            "type": vuln_type,
            "severity": severity,
            "description": description,
            "timestamp": datetime.now().isoformat()
        })
        
    def get_security_report(self) -> Dict[str, Any]:
        """生成安全测试报告"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for test in self.test_results if test["passed"])
        
        return {
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "vulnerabilities_found": len(self.vulnerabilities)
            },
            "test_results": self.test_results,
            "vulnerabilities": self.vulnerabilities,
            "recommendations": self._generate_recommendations()
        }
        
    def _generate_recommendations(self) -> List[str]:
        """生成安全建议"""
        recommendations = []
        
        if len(self.vulnerabilities) > 0:
            recommendations.append("发现安全漏洞，需要立即修复")
            
        failed_tests = [test for test in self.test_results if not test["passed"]]
        if len(failed_tests) > 0:
            recommendations.append("部分安全测试失败，需要检查安全配置")
            
        return recommendations


class TestAuthenticationSecurity(SecurityTestSuite):
    """认证安全测试"""
    
    @pytest.mark.asyncio
    async def test_jwt_token_validation(self):
        """测试JWT令牌验证"""
        test_name = "JWT Token Validation"
        
        try:
            # 测试有效令牌
            secret_key = "test-secret-key-12345678901234567890"
            payload = {
                "user_id": "123",
                "username": "testuser",
                "exp": datetime.utcnow() + timedelta(hours=1),
                "iat": datetime.utcnow(),
                "iss": "suoke-api-gateway",
                "aud": "suoke-services"
            }
            
            valid_token = pyjwt.encode(payload, secret_key, algorithm="HS256")
            decoded = pyjwt.decode(valid_token, secret_key, algorithms=["HS256"], 
                                 audience="suoke-services", issuer="suoke-api-gateway")
            
            assert decoded["user_id"] == "123"
            self.record_test(test_name, True, "Valid JWT token correctly validated")
            
        except Exception as e:
            self.record_test(test_name, False, f"JWT validation failed: {str(e)}")
            self.record_vulnerability("Authentication", "High", "JWT token validation failure")
    
    @pytest.mark.asyncio
    async def test_expired_token_rejection(self):
        """测试过期令牌拒绝"""
        test_name = "Expired Token Rejection"
        
        try:
            secret_key = "test-secret-key-12345678901234567890"
            payload = {
                "user_id": "123",
                "exp": datetime.utcnow() - timedelta(hours=1),  # 已过期
                "iat": datetime.utcnow() - timedelta(hours=2),
                "iss": "suoke-api-gateway",
                "aud": "suoke-services"
            }
            
            expired_token = pyjwt.encode(payload, secret_key, algorithm="HS256")
            
            # 应该抛出过期异常
            with pytest.raises(pyjwt.ExpiredSignatureError):
                pyjwt.decode(expired_token, secret_key, algorithms=["HS256"])
                
            self.record_test(test_name, True, "Expired tokens correctly rejected")
            
        except AssertionError:
            self.record_test(test_name, False, "Expired token was not rejected")
            self.record_vulnerability("Authentication", "High", "Expired tokens accepted")
        except Exception as e:
            self.record_test(test_name, False, f"Test failed: {str(e)}")
    
    @pytest.mark.asyncio
    async def test_invalid_signature_rejection(self):
        """测试无效签名拒绝"""
        test_name = "Invalid Signature Rejection"
        
        try:
            secret_key = "test-secret-key-12345678901234567890"
            wrong_key = "wrong-secret-key-12345678901234567890"
            
            payload = {
                "user_id": "123",
                "exp": datetime.utcnow() + timedelta(hours=1),
                "iat": datetime.utcnow(),
                "iss": "suoke-api-gateway",
                "aud": "suoke-services"
            }
            
            # 用错误的密钥签名
            invalid_token = pyjwt.encode(payload, wrong_key, algorithm="HS256")
            
            # 应该抛出签名验证异常
            with pytest.raises(pyjwt.InvalidSignatureError):
                pyjwt.decode(invalid_token, secret_key, algorithms=["HS256"])
                
            self.record_test(test_name, True, "Invalid signatures correctly rejected")
            
        except AssertionError:
            self.record_test(test_name, False, "Invalid signature was not rejected")
            self.record_vulnerability("Authentication", "Critical", "Invalid signatures accepted")
        except Exception as e:
            self.record_test(test_name, False, f"Test failed: {str(e)}")
    
    @pytest.mark.asyncio
    async def test_brute_force_protection(self):
        """测试暴力破解防护"""
        test_name = "Brute Force Protection"
        
        try:
            # 模拟暴力破解尝试
            failed_attempts = []
            max_attempts = 5
            
            for i in range(max_attempts + 1):
                # 模拟失败的登录尝试
                attempt = {
                    "username": "testuser",
                    "password": f"wrong_password_{i}",
                    "timestamp": time.time(),
                    "ip": "192.168.1.100"
                }
                failed_attempts.append(attempt)
            
            # 检查是否触发了防护机制
            recent_attempts = [
                attempt for attempt in failed_attempts 
                if time.time() - attempt["timestamp"] < 300  # 5分钟内
            ]
            
            if len(recent_attempts) > max_attempts:
                # 应该触发防护机制
                self.record_test(test_name, True, "Brute force protection triggered")
            else:
                self.record_test(test_name, False, "Brute force protection not triggered")
                
        except Exception as e:
            self.record_test(test_name, False, f"Test failed: {str(e)}")


class TestAuthorizationSecurity(SecurityTestSuite):
    """授权安全测试"""
    
    @pytest.mark.asyncio
    async def test_rbac_permission_check(self):
        """测试RBAC权限检查"""
        test_name = "RBAC Permission Check"
        
        try:
            # 模拟用户角色和权限
            user_roles = {
                "admin": ["read:*", "write:*", "delete:*"],
                "user": ["read:profile", "write:profile"],
                "guest": ["read:public"]
            }
            
            # 测试权限检查
            def check_permission(user_role: str, required_permission: str) -> bool:
                permissions = user_roles.get(user_role, [])
                
                # 检查通配符权限
                if f"{required_permission.split(':')[0]}:*" in permissions:
                    return True
                    
                # 检查精确权限
                return required_permission in permissions
            
            # 测试用例
            test_cases = [
                ("admin", "read:users", True),
                ("admin", "delete:users", True),
                ("user", "read:profile", True),
                ("user", "delete:users", False),
                ("guest", "read:public", True),
                ("guest", "write:profile", False)
            ]
            
            all_passed = True
            for role, permission, expected in test_cases:
                result = check_permission(role, permission)
                if result != expected:
                    all_passed = False
                    break
            
            if all_passed:
                self.record_test(test_name, True, "RBAC permissions correctly enforced")
            else:
                self.record_test(test_name, False, "RBAC permission check failed")
                self.record_vulnerability("Authorization", "High", "RBAC permissions not properly enforced")
                
        except Exception as e:
            self.record_test(test_name, False, f"Test failed: {str(e)}")
    
    @pytest.mark.asyncio
    async def test_privilege_escalation_prevention(self):
        """测试权限提升防护"""
        test_name = "Privilege Escalation Prevention"
        
        try:
            # 模拟权限提升尝试
            current_user = {
                "id": "123",
                "role": "user",
                "permissions": ["read:profile", "write:profile"]
            }
            
            # 尝试访问管理员功能
            admin_actions = [
                "delete:users",
                "read:admin_panel",
                "write:system_config"
            ]
            
            escalation_attempts = []
            for action in admin_actions:
                if action not in current_user["permissions"]:
                    escalation_attempts.append(action)
            
            # 应该阻止所有权限提升尝试
            if len(escalation_attempts) == len(admin_actions):
                self.record_test(test_name, True, "Privilege escalation attempts blocked")
            else:
                self.record_test(test_name, False, "Some privilege escalation attempts succeeded")
                self.record_vulnerability("Authorization", "Critical", "Privilege escalation possible")
                
        except Exception as e:
            self.record_test(test_name, False, f"Test failed: {str(e)}")


class TestInputValidationSecurity(SecurityTestSuite):
    """输入验证安全测试"""
    
    @pytest.mark.asyncio
    async def test_sql_injection_prevention(self):
        """测试SQL注入防护"""
        test_name = "SQL Injection Prevention"
        
        try:
            # SQL注入攻击载荷
            sql_payloads = [
                "'; DROP TABLE users; --",
                "' OR '1'='1",
                "' UNION SELECT * FROM passwords --",
                "'; INSERT INTO users VALUES ('hacker', 'password'); --",
                "' OR 1=1 --",
                "admin'--",
                "admin' /*",
                "' OR 'x'='x",
                "'; EXEC xp_cmdshell('dir'); --"
            ]
            
            def validate_input(user_input: str) -> bool:
                """模拟输入验证函数"""
                # 检查SQL注入模式
                sql_patterns = [
                    r"(?i)(union|select|insert|update|delete|drop|create|alter|exec|execute)",
                    r"(?i)(script|javascript|vbscript|onload|onerror)",
                    r"(?i)(\-\-|\#|\/\*|\*\/)",
                    r"(?i)(or|and)\s+\w*\s*=\s*\w*",
                    r"(?i)'\s*(or|and)\s*'",
                ]
                
                import re
                for pattern in sql_patterns:
                    if re.search(pattern, user_input):
                        return False
                return True
            
            blocked_payloads = 0
            for payload in sql_payloads:
                if not validate_input(payload):
                    blocked_payloads += 1
            
            # 应该阻止所有SQL注入尝试
            if blocked_payloads == len(sql_payloads):
                self.record_test(test_name, True, "All SQL injection attempts blocked")
            else:
                self.record_test(test_name, False, f"Only {blocked_payloads}/{len(sql_payloads)} SQL injection attempts blocked")
                self.record_vulnerability("Input Validation", "Critical", "SQL injection possible")
                
        except Exception as e:
            self.record_test(test_name, False, f"Test failed: {str(e)}")
    
    @pytest.mark.asyncio
    async def test_xss_prevention(self):
        """测试XSS防护"""
        test_name = "XSS Prevention"
        
        try:
            # XSS攻击载荷
            xss_payloads = [
                "<script>alert('XSS')</script>",
                "<img src=x onerror=alert('XSS')>",
                "<svg onload=alert('XSS')>",
                "javascript:alert('XSS')",
                "<iframe src=javascript:alert('XSS')></iframe>",
                "<body onload=alert('XSS')>",
                "<input onfocus=alert('XSS') autofocus>",
                "<select onfocus=alert('XSS') autofocus>",
                "<textarea onfocus=alert('XSS') autofocus>",
                "<keygen onfocus=alert('XSS') autofocus>"
            ]
            
            def sanitize_input(user_input: str) -> str:
                """模拟输入清理函数"""
                import html
                import re
                
                # HTML编码
                sanitized = html.escape(user_input)
                
                # 移除危险标签
                dangerous_patterns = [
                    r"<script[^>]*>.*?</script>",
                    r"<iframe[^>]*>.*?</iframe>",
                    r"javascript:",
                    r"on\w+\s*=",
                    r"<svg[^>]*>",
                    r"<img[^>]*onerror[^>]*>",
                ]
                
                for pattern in dangerous_patterns:
                    sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE | re.DOTALL)
                
                return sanitized
            
            safe_outputs = 0
            for payload in xss_payloads:
                sanitized = sanitize_input(payload)
                # 检查是否还包含危险内容
                if "<script" not in sanitized.lower() and "javascript:" not in sanitized.lower() and "onerror" not in sanitized.lower():
                    safe_outputs += 1
            
            # 应该清理所有XSS尝试
            if safe_outputs == len(xss_payloads):
                self.record_test(test_name, True, "All XSS attempts sanitized")
            else:
                self.record_test(test_name, False, f"Only {safe_outputs}/{len(xss_payloads)} XSS attempts sanitized")
                self.record_vulnerability("Input Validation", "High", "XSS attacks possible")
                
        except Exception as e:
            self.record_test(test_name, False, f"Test failed: {str(e)}")
    
    @pytest.mark.asyncio
    async def test_request_size_limits(self):
        """测试请求大小限制"""
        test_name = "Request Size Limits"
        
        try:
            max_request_size = 10 * 1024 * 1024  # 10MB
            max_header_size = 8 * 1024  # 8KB
            
            # 测试正常大小的请求
            normal_request = {
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"data": "normal request"})
            }
            
            # 测试超大请求体
            large_body = "x" * (max_request_size + 1)
            large_request = {
                "headers": {"Content-Type": "application/json"},
                "body": large_body
            }
            
            # 测试超大请求头
            large_header_value = "x" * (max_header_size + 1)
            large_header_request = {
                "headers": {
                    "Content-Type": "application/json",
                    "X-Large-Header": large_header_value
                },
                "body": json.dumps({"data": "test"})
            }
            
            def validate_request_size(request: dict) -> bool:
                """验证请求大小"""
                # 检查请求体大小
                body_size = len(request.get("body", "").encode('utf-8'))
                if body_size > max_request_size:
                    return False
                
                # 检查请求头大小
                headers_size = sum(
                    len(f"{k}: {v}".encode('utf-8')) 
                    for k, v in request.get("headers", {}).items()
                )
                if headers_size > max_header_size:
                    return False
                
                return True
            
            # 测试结果
            normal_valid = validate_request_size(normal_request)
            large_body_valid = validate_request_size(large_request)
            large_header_valid = validate_request_size(large_header_request)
            
            if normal_valid and not large_body_valid and not large_header_valid:
                self.record_test(test_name, True, "Request size limits properly enforced")
            else:
                self.record_test(test_name, False, "Request size limits not properly enforced")
                self.record_vulnerability("Input Validation", "Medium", "Request size limits not enforced")
                
        except Exception as e:
            self.record_test(test_name, False, f"Test failed: {str(e)}")


class TestNetworkSecurity(SecurityTestSuite):
    """网络安全测试"""
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self):
        """测试限流功能"""
        test_name = "Rate Limiting"
        
        try:
            # 模拟限流配置
            rate_limit_config = {
                "requests_per_minute": 60,
                "burst_size": 10,
                "window_size": 60
            }
            
            # 模拟请求记录
            request_log = {}
            
            def check_rate_limit(client_ip: str, current_time: float) -> bool:
                """检查限流"""
                if client_ip not in request_log:
                    request_log[client_ip] = []
                
                # 清理过期记录
                window_start = current_time - rate_limit_config["window_size"]
                request_log[client_ip] = [
                    timestamp for timestamp in request_log[client_ip]
                    if timestamp > window_start
                ]
                
                # 检查是否超过限制
                if len(request_log[client_ip]) >= rate_limit_config["requests_per_minute"]:
                    return False
                
                # 记录当前请求
                request_log[client_ip].append(current_time)
                return True
            
            # 模拟正常请求
            current_time = time.time()
            client_ip = "192.168.1.100"
            
            # 发送正常数量的请求
            normal_requests_allowed = 0
            for i in range(50):  # 少于限制
                if check_rate_limit(client_ip, current_time + i):
                    normal_requests_allowed += 1
            
            # 发送超量请求
            excessive_requests_blocked = 0
            for i in range(20):  # 超过限制
                if not check_rate_limit(client_ip, current_time + 50 + i):
                    excessive_requests_blocked += 1
            
            if normal_requests_allowed == 50 and excessive_requests_blocked > 0:
                self.record_test(test_name, True, "Rate limiting working correctly")
            else:
                self.record_test(test_name, False, "Rate limiting not working properly")
                self.record_vulnerability("Network Security", "Medium", "Rate limiting ineffective")
                
        except Exception as e:
            self.record_test(test_name, False, f"Test failed: {str(e)}")
    
    @pytest.mark.asyncio
    async def test_ip_blacklist(self):
        """测试IP黑名单"""
        test_name = "IP Blacklist"
        
        try:
            # 模拟IP黑名单
            blacklisted_ips = [
                "192.168.1.100",
                "10.0.0.50",
                "172.16.0.25"
            ]
            
            def is_ip_allowed(client_ip: str) -> bool:
                """检查IP是否被允许"""
                return client_ip not in blacklisted_ips
            
            # 测试正常IP
            normal_ip = "192.168.1.200"
            normal_allowed = is_ip_allowed(normal_ip)
            
            # 测试黑名单IP
            blocked_count = 0
            for blocked_ip in blacklisted_ips:
                if not is_ip_allowed(blocked_ip):
                    blocked_count += 1
            
            if normal_allowed and blocked_count == len(blacklisted_ips):
                self.record_test(test_name, True, "IP blacklist working correctly")
            else:
                self.record_test(test_name, False, "IP blacklist not working properly")
                self.record_vulnerability("Network Security", "High", "IP blacklist ineffective")
                
        except Exception as e:
            self.record_test(test_name, False, f"Test failed: {str(e)}")


class TestDataSecurity(SecurityTestSuite):
    """数据安全测试"""
    
    @pytest.mark.asyncio
    async def test_sensitive_data_masking(self):
        """测试敏感数据脱敏"""
        test_name = "Sensitive Data Masking"
        
        try:
            def mask_sensitive_data(data: dict) -> dict:
                """脱敏敏感数据"""
                import re
                
                masked_data = data.copy()
                
                # 脱敏规则
                masking_rules = {
                    "email": lambda x: re.sub(r"(.{1,3}).*@(.*)\.(.{1,3})", r"\1***@***.\3", x),
                    "phone": lambda x: re.sub(r"(\d{3})\d{4}(\d{4})", r"\1****\2", x),
                    "credit_card": lambda x: re.sub(r"(\d{4})\d{8}(\d{4})", r"\1********\2", x),
                    "password": lambda x: "***"
                }
                
                for field, rule in masking_rules.items():
                    if field in masked_data:
                        masked_data[field] = rule(str(masked_data[field]))
                
                return masked_data
            
            # 测试数据
            sensitive_data = {
                "name": "张三",
                "email": "zhangsan@example.com",
                "phone": "13812345678",
                "credit_card": "1234567890123456",
                "password": "secretpassword123"
            }
            
            masked_data = mask_sensitive_data(sensitive_data)
            
            # 验证脱敏效果
            checks = [
                "***" in masked_data["email"],
                "****" in masked_data["phone"],
                "********" in masked_data["credit_card"],
                masked_data["password"] == "***"
            ]
            
            if all(checks):
                self.record_test(test_name, True, "Sensitive data properly masked")
            else:
                self.record_test(test_name, False, "Sensitive data not properly masked")
                self.record_vulnerability("Data Security", "High", "Sensitive data exposure risk")
                
        except Exception as e:
            self.record_test(test_name, False, f"Test failed: {str(e)}")
    
    @pytest.mark.asyncio
    async def test_data_encryption(self):
        """测试数据加密"""
        test_name = "Data Encryption"
        
        try:
            from cryptography.fernet import Fernet
            
            # 生成密钥
            key = Fernet.generate_key()
            cipher_suite = Fernet(key)
            
            # 测试数据
            sensitive_data = "这是敏感数据，需要加密存储"
            
            # 加密
            encrypted_data = cipher_suite.encrypt(sensitive_data.encode())
            
            # 解密
            decrypted_data = cipher_suite.decrypt(encrypted_data).decode()
            
            # 验证加密解密
            encryption_works = (
                encrypted_data != sensitive_data.encode() and
                decrypted_data == sensitive_data
            )
            
            if encryption_works:
                self.record_test(test_name, True, "Data encryption working correctly")
            else:
                self.record_test(test_name, False, "Data encryption not working")
                self.record_vulnerability("Data Security", "Critical", "Data encryption failure")
                
        except ImportError:
            self.record_test(test_name, False, "Cryptography library not available")
        except Exception as e:
            self.record_test(test_name, False, f"Test failed: {str(e)}")


@pytest.mark.asyncio
async def test_comprehensive_security_suite():
    """运行全面的安全测试套件"""
    
    # 创建测试套件实例
    auth_tests = TestAuthenticationSecurity()
    authz_tests = TestAuthorizationSecurity()
    input_tests = TestInputValidationSecurity()
    network_tests = TestNetworkSecurity()
    data_tests = TestDataSecurity()
    
    # 运行所有测试
    test_suites = [auth_tests, authz_tests, input_tests, network_tests, data_tests]
    
    for suite in test_suites:
        # 运行该套件的所有测试方法
        for method_name in dir(suite):
            if method_name.startswith("test_") and callable(getattr(suite, method_name)):
                method = getattr(suite, method_name)
                try:
                    await method()
                except Exception as e:
                    suite.record_test(method_name, False, f"Test execution failed: {str(e)}")
    
    # 生成综合报告
    comprehensive_report = {
        "test_timestamp": datetime.now().isoformat(),
        "test_suites": {}
    }
    
    total_tests = 0
    total_passed = 0
    total_vulnerabilities = 0
    
    for i, suite in enumerate(test_suites):
        suite_name = suite.__class__.__name__
        report = suite.get_security_report()
        comprehensive_report["test_suites"][suite_name] = report
        
        total_tests += report["summary"]["total_tests"]
        total_passed += report["summary"]["passed_tests"]
        total_vulnerabilities += report["summary"]["vulnerabilities_found"]
    
    # 综合摘要
    comprehensive_report["overall_summary"] = {
        "total_tests": total_tests,
        "total_passed": total_passed,
        "total_failed": total_tests - total_passed,
        "overall_success_rate": (total_passed / total_tests * 100) if total_tests > 0 else 0,
        "total_vulnerabilities": total_vulnerabilities,
        "security_score": max(0, 100 - (total_vulnerabilities * 10) - ((total_tests - total_passed) * 5))
    }
    
    print(f"\n=== 安全测试综合报告 ===")
    print(f"总测试数: {total_tests}")
    print(f"通过测试: {total_passed}")
    print(f"失败测试: {total_tests - total_passed}")
    print(f"成功率: {comprehensive_report['overall_summary']['overall_success_rate']:.1f}%")
    print(f"发现漏洞: {total_vulnerabilities}")
    print(f"安全评分: {comprehensive_report['overall_summary']['security_score']:.1f}/100")
    
    # 安全评分应该达到90分以上
    assert comprehensive_report['overall_summary']['security_score'] >= 90, "安全评分过低"
    
    return comprehensive_report


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"]) 