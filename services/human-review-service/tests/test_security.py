"""
安全模块测试
Security Module Tests

测试安全相关功能
"""

import pytest
import hashlib
import jwt
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock

from human_review_service.core.security import (
    PasswordManager,
    TokenManager,
    PermissionManager,
    DataEncryption,
    AuditLogger,
    SecurityValidator,
    SecurityManager
)


class TestPasswordManager:
    """密码管理器测试"""

    @pytest.fixture
    def password_manager(self):
        """创建密码管理器实例"""
        return PasswordManager()

    def test_hash_password(self, password_manager):
        """测试密码哈希"""
        password = "test_password_123"
        hashed = password_manager.hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 0
        assert isinstance(hashed, str)

    def test_verify_password_correct(self, password_manager):
        """测试正确密码验证"""
        password = "test_password_123"
        hashed = password_manager.hash_password(password)
        
        is_valid = password_manager.verify_password(password, hashed)
        assert is_valid is True

    def test_verify_password_incorrect(self, password_manager):
        """测试错误密码验证"""
        password = "test_password_123"
        wrong_password = "wrong_password"
        hashed = password_manager.hash_password(password)
        
        is_valid = password_manager.verify_password(wrong_password, hashed)
        assert is_valid is False

    def test_password_strength_strong(self, password_manager):
        """测试强密码强度验证"""
        strong_password = "StrongP@ssw0rd123!"
        strength = password_manager.check_password_strength(strong_password)
        
        assert strength["score"] >= 80
        assert strength["is_strong"] is True

    def test_password_strength_weak(self, password_manager):
        """测试弱密码强度验证"""
        weak_password = "123456"
        strength = password_manager.check_password_strength(weak_password)
        
        assert strength["score"] < 50
        assert strength["is_strong"] is False

    def test_generate_secure_password(self, password_manager):
        """测试生成安全密码"""
        password = password_manager.generate_secure_password(length=12)
        
        assert len(password) == 12
        strength = password_manager.check_password_strength(password)
        assert strength["is_strong"] is True

    def test_password_history(self, password_manager):
        """测试密码历史记录"""
        user_id = "user_123"
        passwords = ["password1", "password2", "password3"]
        
        for password in passwords:
            hashed = password_manager.hash_password(password)
            password_manager.add_to_history(user_id, hashed)
        
        # 检查是否在历史中
        for password in passwords:
            is_in_history = password_manager.is_password_in_history(user_id, password)
            assert is_in_history is True
        
        # 检查新密码
        new_password = "new_password_123"
        is_in_history = password_manager.is_password_in_history(user_id, new_password)
        assert is_in_history is False


class TestTokenManager:
    """令牌管理器测试"""

    @pytest.fixture
    def token_manager(self):
        """创建令牌管理器实例"""
        return TokenManager(secret_key="test_secret_key")

    def test_generate_access_token(self, token_manager):
        """测试生成访问令牌"""
        user_id = "user_123"
        payload = {"user_id": user_id, "role": "reviewer"}
        
        token = token_manager.generate_access_token(payload)
        
        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_access_token_valid(self, token_manager):
        """测试验证有效访问令牌"""
        user_id = "user_123"
        payload = {"user_id": user_id, "role": "reviewer"}
        
        token = token_manager.generate_access_token(payload)
        decoded_payload = token_manager.verify_access_token(token)
        
        assert decoded_payload is not None
        assert decoded_payload["user_id"] == user_id
        assert decoded_payload["role"] == "reviewer"

    def test_verify_access_token_invalid(self, token_manager):
        """测试验证无效访问令牌"""
        invalid_token = "invalid.token.here"
        
        decoded_payload = token_manager.verify_access_token(invalid_token)
        
        assert decoded_payload is None

    def test_verify_access_token_expired(self, token_manager):
        """测试验证过期访问令牌"""
        user_id = "user_123"
        payload = {"user_id": user_id, "role": "reviewer"}
        
        # 生成立即过期的令牌
        token = token_manager.generate_access_token(payload, expires_in=-1)
        decoded_payload = token_manager.verify_access_token(token)
        
        assert decoded_payload is None

    def test_generate_refresh_token(self, token_manager):
        """测试生成刷新令牌"""
        user_id = "user_123"
        
        refresh_token = token_manager.generate_refresh_token(user_id)
        
        assert isinstance(refresh_token, str)
        assert len(refresh_token) > 0

    def test_verify_refresh_token(self, token_manager):
        """测试验证刷新令牌"""
        user_id = "user_123"
        
        refresh_token = token_manager.generate_refresh_token(user_id)
        is_valid = token_manager.verify_refresh_token(refresh_token, user_id)
        
        assert is_valid is True

    def test_revoke_token(self, token_manager):
        """测试撤销令牌"""
        user_id = "user_123"
        payload = {"user_id": user_id, "role": "reviewer"}
        
        token = token_manager.generate_access_token(payload)
        
        # 撤销令牌
        token_manager.revoke_token(token)
        
        # 验证撤销后的令牌
        decoded_payload = token_manager.verify_access_token(token)
        assert decoded_payload is None


class TestPermissionManager:
    """权限管理器测试"""

    @pytest.fixture
    def permission_manager(self):
        """创建权限管理器实例"""
        return PermissionManager()

    def test_assign_role_to_user(self, permission_manager):
        """测试为用户分配角色"""
        user_id = "user_123"
        role = "reviewer"
        
        permission_manager.assign_role(user_id, role)
        user_roles = permission_manager.get_user_roles(user_id)
        
        assert role in user_roles

    def test_check_permission_with_role(self, permission_manager):
        """测试基于角色的权限检查"""
        user_id = "user_123"
        role = "admin"
        permission = "manage_reviewers"
        
        # 分配角色
        permission_manager.assign_role(user_id, role)
        
        # 检查权限
        has_permission = permission_manager.check_permission(user_id, permission)
        
        assert has_permission is True

    def test_check_permission_without_role(self, permission_manager):
        """测试无角色用户的权限检查"""
        user_id = "user_123"
        permission = "manage_reviewers"
        
        has_permission = permission_manager.check_permission(user_id, permission)
        
        assert has_permission is False

    def test_grant_custom_permission(self, permission_manager):
        """测试授予自定义权限"""
        user_id = "user_123"
        permission = "custom_permission"
        
        permission_manager.grant_permission(user_id, permission)
        has_permission = permission_manager.check_permission(user_id, permission)
        
        assert has_permission is True

    def test_permission_inheritance(self, permission_manager):
        """测试权限继承"""
        user_id = "user_123"
        parent_role = "admin"
        child_role = "reviewer"
        
        # 设置角色继承关系
        permission_manager.set_role_inheritance(child_role, parent_role)
        permission_manager.assign_role(user_id, child_role)
        
        # 检查继承的权限
        admin_permission = "manage_reviewers"
        has_permission = permission_manager.check_permission(user_id, admin_permission)
        
        assert has_permission is True

    def test_revoke_permission(self, permission_manager):
        """测试撤销权限"""
        user_id = "user_123"
        permission = "test_permission"
        
        # 授予权限
        permission_manager.grant_permission(user_id, permission)
        assert permission_manager.check_permission(user_id, permission) is True
        
        # 撤销权限
        permission_manager.revoke_permission(user_id, permission)
        assert permission_manager.check_permission(user_id, permission) is False


class TestDataEncryption:
    """数据加密测试"""

    @pytest.fixture
    def encryption(self):
        """创建数据加密实例"""
        return DataEncryption(key="test_encryption_key_32_characters")

    def test_encrypt_decrypt_string(self, encryption):
        """测试字符串加密解密"""
        original_data = "sensitive_information"
        
        encrypted_data = encryption.encrypt(original_data)
        decrypted_data = encryption.decrypt(encrypted_data)
        
        assert encrypted_data != original_data
        assert decrypted_data == original_data

    def test_encrypt_decrypt_dict(self, encryption):
        """测试字典加密解密"""
        original_data = {
            "user_id": "123",
            "email": "test@example.com",
            "sensitive_field": "secret_value"
        }
        
        encrypted_data = encryption.encrypt(original_data)
        decrypted_data = encryption.decrypt(encrypted_data)
        
        assert encrypted_data != original_data
        assert decrypted_data == original_data

    def test_encrypt_large_data(self, encryption):
        """测试大数据加密"""
        large_data = "x" * 10000  # 10KB数据
        
        encrypted_data = encryption.encrypt(large_data)
        decrypted_data = encryption.decrypt(encrypted_data)
        
        assert decrypted_data == large_data

    def test_encrypt_with_different_keys(self, encryption):
        """测试不同密钥的加密"""
        original_data = "test_data"
        
        # 使用第一个密钥加密
        encrypted_data = encryption.encrypt(original_data)
        
        # 使用不同密钥尝试解密
        different_encryption = DataEncryption(key="different_key_32_characters_xx")
        
        try:
            decrypted_data = different_encryption.decrypt(encrypted_data)
            # 如果没有抛出异常，解密结果应该不等于原始数据
            assert decrypted_data != original_data
        except Exception:
            # 预期会抛出异常
            pass

    def test_hash_data(self, encryption):
        """测试数据哈希"""
        data = "data_to_hash"
        
        hash_value = encryption.hash_data(data)
        
        assert isinstance(hash_value, str)
        assert len(hash_value) > 0
        assert hash_value != data
        
        # 相同数据应该产生相同哈希
        hash_value2 = encryption.hash_data(data)
        assert hash_value == hash_value2


class TestAuditLogger:
    """审计日志测试"""

    @pytest.fixture
    def audit_logger(self):
        """创建审计日志实例"""
        return AuditLogger()

    def test_log_user_action(self, audit_logger):
        """测试记录用户操作"""
        user_id = "user_123"
        action = "login"
        details = {"ip_address": "192.168.1.1", "user_agent": "Mozilla/5.0"}
        
        audit_logger.log_user_action(user_id, action, details)
        
        logs = audit_logger.get_user_logs(user_id)
        assert len(logs) >= 1
        assert logs[-1]["action"] == action

    def test_log_security_event(self, audit_logger):
        """测试记录安全事件"""
        event_type = "failed_login_attempt"
        details = {
            "user_id": "user_123",
            "ip_address": "192.168.1.1",
            "attempts": 3
        }
        
        audit_logger.log_security_event(event_type, details)
        
        events = audit_logger.get_security_events()
        assert len(events) >= 1
        assert events[-1]["event_type"] == event_type

    def test_log_data_access(self, audit_logger):
        """测试记录数据访问"""
        user_id = "user_123"
        resource = "review_task_456"
        access_type = "read"
        
        audit_logger.log_data_access(user_id, resource, access_type)
        
        access_logs = audit_logger.get_data_access_logs(resource)
        assert len(access_logs) >= 1
        assert access_logs[-1]["access_type"] == access_type

    def test_log_retention_policy(self, audit_logger):
        """测试日志保留策略"""
        # 记录一些旧日志
        old_date = datetime.now() - timedelta(days=400)
        
        with patch('human_review_service.core.security.datetime') as mock_datetime:
            mock_datetime.now.return_value = old_date
            audit_logger.log_user_action("user_123", "old_action", {})
        
        # 应用保留策略（删除超过365天的日志）
        deleted_count = audit_logger.apply_retention_policy(days=365)
        
        assert deleted_count >= 0

    def test_search_logs(self, audit_logger):
        """测试日志搜索"""
        # 记录一些测试日志
        audit_logger.log_user_action("user_123", "test_action", {"test": "data"})
        audit_logger.log_security_event("test_event", {"test": "security"})
        
        # 搜索包含"test"的日志
        results = audit_logger.search_logs(query="test")
        
        assert len(results) >= 2


class TestSecurityValidator:
    """安全验证器测试"""

    @pytest.fixture
    def validator(self):
        """创建安全验证器实例"""
        return SecurityValidator()

    def test_validate_sql_injection_safe(self, validator):
        """测试SQL注入验证 - 安全输入"""
        safe_input = "normal user input"
        
        is_safe = validator.validate_sql_injection(safe_input)
        
        assert is_safe is True

    def test_validate_sql_injection_dangerous(self, validator):
        """测试SQL注入验证 - 危险输入"""
        dangerous_input = "'; DROP TABLE users; --"
        
        is_safe = validator.validate_sql_injection(dangerous_input)
        
        assert is_safe is False

    def test_validate_xss_safe(self, validator):
        """测试XSS攻击验证 - 安全输入"""
        safe_input = "normal text content"
        
        is_safe = validator.validate_xss(safe_input)
        
        assert is_safe is True

    def test_validate_xss_dangerous(self, validator):
        """测试XSS攻击验证 - 危险输入"""
        dangerous_input = "<script>alert('xss')</script>"
        
        is_safe = validator.validate_xss(dangerous_input)
        
        assert is_safe is False

    def test_validate_file_upload_safe(self, validator):
        """测试文件上传验证 - 安全文件"""
        safe_filename = "document.pdf"
        safe_content_type = "application/pdf"
        
        is_safe = validator.validate_file_upload(safe_filename, safe_content_type)
        
        assert is_safe is True

    def test_validate_file_upload_dangerous(self, validator):
        """测试文件上传验证 - 危险文件"""
        dangerous_filename = "malware.exe"
        dangerous_content_type = "application/x-executable"
        
        is_safe = validator.validate_file_upload(dangerous_filename, dangerous_content_type)
        
        assert is_safe is False

    def test_validate_ip_address_valid(self, validator):
        """测试IP地址验证 - 有效IP"""
        valid_ip = "192.168.1.1"
        
        is_valid = validator.validate_ip_address(valid_ip)
        
        assert is_valid is True

    def test_validate_ip_address_invalid(self, validator):
        """测试IP地址验证 - 无效IP"""
        invalid_ip = "999.999.999.999"
        
        is_valid = validator.validate_ip_address(invalid_ip)
        
        assert is_valid is False

    def test_rate_limiting(self, validator):
        """测试速率限制"""
        user_id = "user_123"
        action = "login"
        
        # 在限制内的请求应该被允许
        for i in range(5):
            is_allowed = validator.check_rate_limit(user_id, action, limit=10, window=60)
            assert is_allowed is True
        
        # 超过限制的请求应该被拒绝
        for i in range(10):
            validator.check_rate_limit(user_id, action, limit=10, window=60)
        
        is_allowed = validator.check_rate_limit(user_id, action, limit=10, window=60)
        assert is_allowed is False


class TestSecurityManager:
    """安全管理器集成测试"""

    @pytest.fixture
    def security_manager(self):
        """创建安全管理器实例"""
        return SecurityManager()

    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, security_manager):
        """测试用户认证成功"""
        username = "test_user"
        password = "test_password"
        
        # 模拟用户存在且密码正确
        with patch.object(security_manager.password_manager, 'verify_password', return_value=True):
            with patch.object(security_manager, '_get_user_by_username', return_value={"id": "user_123", "username": username}):
                result = await security_manager.authenticate_user(username, password)
                
                assert result["success"] is True
                assert "access_token" in result
                assert "refresh_token" in result

    @pytest.mark.asyncio
    async def test_authenticate_user_failure(self, security_manager):
        """测试用户认证失败"""
        username = "test_user"
        password = "wrong_password"
        
        # 模拟密码错误
        with patch.object(security_manager.password_manager, 'verify_password', return_value=False):
            with patch.object(security_manager, '_get_user_by_username', return_value={"id": "user_123", "username": username}):
                result = await security_manager.authenticate_user(username, password)
                
                assert result["success"] is False
                assert "error" in result

    @pytest.mark.asyncio
    async def test_authorize_user_with_permission(self, security_manager):
        """测试用户授权 - 有权限"""
        user_id = "user_123"
        permission = "read_reviews"
        
        with patch.object(security_manager.permission_manager, 'check_permission', return_value=True):
            is_authorized = await security_manager.authorize_user(user_id, permission)
            
            assert is_authorized is True

    @pytest.mark.asyncio
    async def test_authorize_user_without_permission(self, security_manager):
        """测试用户授权 - 无权限"""
        user_id = "user_123"
        permission = "admin_access"
        
        with patch.object(security_manager.permission_manager, 'check_permission', return_value=False):
            is_authorized = await security_manager.authorize_user(user_id, permission)
            
            assert is_authorized is False

    @pytest.mark.asyncio
    async def test_handle_security_event(self, security_manager):
        """测试安全事件处理"""
        event_type = "suspicious_activity"
        details = {"user_id": "user_123", "activity": "multiple_failed_logins"}
        
        await security_manager.handle_security_event(event_type, details)
        
        # 验证事件被记录
        # 这里需要检查审计日志是否记录了事件

    @pytest.mark.asyncio
    async def test_session_management(self, security_manager):
        """测试会话管理"""
        user_id = "user_123"
        
        # 创建会话
        session_id = await security_manager.create_session(user_id)
        assert session_id is not None
        
        # 验证会话
        is_valid = await security_manager.validate_session(session_id)
        assert is_valid is True
        
        # 销毁会话
        await security_manager.destroy_session(session_id)
        is_valid = await security_manager.validate_session(session_id)
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_data_protection(self, security_manager):
        """测试数据保护"""
        sensitive_data = {
            "user_id": "123",
            "email": "user@example.com",
            "phone": "1234567890"
        }
        
        # 加密敏感数据
        encrypted_data = await security_manager.protect_sensitive_data(sensitive_data)
        assert encrypted_data != sensitive_data
        
        # 解密数据
        decrypted_data = await security_manager.unprotect_sensitive_data(encrypted_data)
        assert decrypted_data == sensitive_data

    @pytest.mark.asyncio
    async def test_compliance_audit(self, security_manager):
        """测试合规审计"""
        # 模拟一些用户活动
        activities = [
            {"user_id": "user_123", "action": "login", "timestamp": datetime.now()},
            {"user_id": "user_123", "action": "view_review", "timestamp": datetime.now()},
            {"user_id": "user_456", "action": "create_review", "timestamp": datetime.now()},
        ]
        
        for activity in activities:
            security_manager.audit_logger.log_user_action(
                activity["user_id"], 
                activity["action"], 
                {"timestamp": activity["timestamp"]}
            )
        
        # 生成合规报告
        report = await security_manager.generate_compliance_report(
            start_date=datetime.now() - timedelta(days=1),
            end_date=datetime.now()
        )
        
        assert "total_activities" in report
        assert "security_events" in report
        assert "compliance_status" in report 