"""
MFA（多因子认证）服务

处理TOTP、短信验证码等多因子认证功能。
"""
import logging
import secrets
import qrcode
import io
import base64
import uuid
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy import select, and_
import pyotp

from internal.config.settings import get_settings
from internal.repository.user_repository_new import UserRepository
from internal.db.models import MFASecretModel
from internal.model.user import MFATypeEnum


class MFAService:
    """MFA服务类"""
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = logging.getLogger(__name__)
        self.user_repo = UserRepository()
    
    def generate_secret(self) -> str:
        """生成TOTP密钥"""
        return pyotp.random_base32()
    
    def generate_backup_codes(self, count: int = 10) -> List[str]:
        """
        生成备用验证码
        
        Args:
            count: 生成数量
            
        Returns:
            List[str]: 备用验证码列表
        """
        codes = []
        for _ in range(count):
            # 生成8位数字验证码
            code = ''.join([str(secrets.randbelow(10)) for _ in range(8)])
            codes.append(code)
        return codes
    
    def generate_qr_code(self, user_email: str, secret: str) -> str:
        """
        生成TOTP二维码
        
        Args:
            user_email: 用户邮箱
            secret: TOTP密钥
            
        Returns:
            str: Base64编码的二维码图片
        """
        try:
            # 创建TOTP URI
            totp = pyotp.TOTP(secret)
            provisioning_uri = totp.provisioning_uri(
                name=user_email,
                issuer_name="索克生活"
            )
            
            # 生成二维码
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(provisioning_uri)
            qr.make(fit=True)
            
            # 创建图片
            img = qr.make_image(fill_color="black", back_color="white")
            
            # 转换为Base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
            
        except Exception as e:
            self.logger.error(f"生成二维码失败: {e}")
            return ""
    
    def verify_totp_code(self, secret: str, code: str, window: int = 1) -> bool:
        """
        验证TOTP验证码
        
        Args:
            secret: TOTP密钥
            code: 用户输入的验证码
            window: 时间窗口（允许前后几个时间段）
            
        Returns:
            bool: 验证是否成功
        """
        try:
            totp = pyotp.TOTP(secret)
            return totp.verify(code, valid_window=window)
        except Exception as e:
            self.logger.error(f"TOTP验证失败: {e}")
            return False
    
    def verify_backup_code(self, backup_codes: List[str], code: str) -> Tuple[bool, List[str]]:
        """
        验证备用验证码
        
        Args:
            backup_codes: 备用验证码列表
            code: 用户输入的验证码
            
        Returns:
            Tuple[bool, List[str]]: (验证是否成功, 更新后的备用验证码列表)
        """
        if code in backup_codes:
            # 移除已使用的验证码
            updated_codes = [c for c in backup_codes if c != code]
            return True, updated_codes
        return False, backup_codes
    
    async def setup_totp(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        为用户设置TOTP
        
        Args:
            user_id: 用户ID
            
        Returns:
            Optional[Dict]: 设置信息（包含密钥和二维码）
        """
        try:
            # 获取用户信息
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                return None
            
            # 生成密钥和备用验证码
            secret = self.generate_secret()
            backup_codes = self.generate_backup_codes()
            
            # 生成二维码
            qr_code = self.generate_qr_code(user.email, secret)
            
            return {
                "secret": secret,
                "backup_codes": backup_codes,
                "qr_code": qr_code,
                "manual_entry_key": secret
            }
            
        except Exception as e:
            self.logger.error(f"设置TOTP失败: {e}")
            return None
    
    async def enable_totp(
        self, 
        user_id: str, 
        secret: str, 
        verification_code: str,
        backup_codes: List[str]
    ) -> bool:
        """
        启用TOTP
        
        Args:
            user_id: 用户ID
            secret: TOTP密钥
            verification_code: 验证码
            backup_codes: 备用验证码
            
        Returns:
            bool: 是否成功
        """
        try:
            # 验证验证码
            if not self.verify_totp_code(secret, verification_code):
                self.logger.warning(f"TOTP验证码错误: {user_id}")
                return False
            
            # 保存MFA设置
            async with await self.user_repo.get_session() as session:
                # 检查是否已存在TOTP设置
                existing = await session.execute(
                    select(MFASecretModel).where(
                        and_(
                            MFASecretModel.user_id == user_id,
                            MFASecretModel.mfa_type == MFATypeEnum.TOTP.value
                        )
                    )
                )
                mfa_secret = existing.scalar_one_or_none()
                
                if mfa_secret:
                    # 更新现有设置
                    mfa_secret.secret = secret
                    mfa_secret.backup_codes = backup_codes
                    mfa_secret.is_active = True
                    mfa_secret.updated_at = datetime.utcnow()
                else:
                    # 创建新设置
                    mfa_secret = MFASecretModel(
                        id=str(uuid.uuid4()),
                        user_id=user_id,
                        mfa_type=MFATypeEnum.TOTP.value,
                        secret=secret,
                        backup_codes=backup_codes,
                        is_active=True,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    session.add(mfa_secret)
                
                await session.commit()
            
            self.logger.info(f"TOTP启用成功: {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"启用TOTP失败: {e}")
            return False
    
    async def disable_mfa(self, user_id: str, mfa_type: MFATypeEnum) -> bool:
        """
        禁用MFA
        
        Args:
            user_id: 用户ID
            mfa_type: MFA类型
            
        Returns:
            bool: 是否成功
        """
        try:
            async with await self.user_repo.get_session() as session:
                result = await session.execute(
                    select(MFASecretModel).where(
                        and_(
                            MFASecretModel.user_id == user_id,
                            MFASecretModel.mfa_type == mfa_type.value
                        )
                    )
                )
                mfa_secret = result.scalar_one_or_none()
                
                if mfa_secret:
                    mfa_secret.is_active = False
                    mfa_secret.updated_at = datetime.utcnow()
                    await session.commit()
                    
                    self.logger.info(f"MFA禁用成功: {user_id}, 类型: {mfa_type.value}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"禁用MFA失败: {e}")
            return False
    
    async def verify_mfa(
        self, 
        user_id: str, 
        code: str, 
        mfa_type: Optional[MFATypeEnum] = None
    ) -> bool:
        """
        验证MFA代码
        
        Args:
            user_id: 用户ID
            code: 验证码
            mfa_type: MFA类型（可选，自动检测）
            
        Returns:
            bool: 验证是否成功
        """
        try:
            async with await self.user_repo.get_session() as session:
                query = select(MFASecretModel).where(
                    and_(
                        MFASecretModel.user_id == user_id,
                        MFASecretModel.is_active == True
                    )
                )
                
                if mfa_type:
                    query = query.where(MFASecretModel.mfa_type == mfa_type.value)
                
                result = await session.execute(query)
                mfa_secrets = list(result.scalars().all())
                
                for mfa_secret in mfa_secrets:
                    if mfa_secret.mfa_type == MFATypeEnum.TOTP.value:
                        # 验证TOTP
                        if self.verify_totp_code(mfa_secret.secret, code):
                            return True
                        
                        # 验证备用验证码
                        if mfa_secret.backup_codes:
                            is_valid, updated_codes = self.verify_backup_code(
                                mfa_secret.backup_codes, code
                            )
                            if is_valid:
                                # 更新备用验证码
                                mfa_secret.backup_codes = updated_codes
                                mfa_secret.updated_at = datetime.utcnow()
                                await session.commit()
                                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"MFA验证失败: {e}")
            return False
    
    async def get_user_mfa_settings(self, user_id: str) -> List[Dict[str, Any]]:
        """
        获取用户MFA设置
        
        Args:
            user_id: 用户ID
            
        Returns:
            List[Dict]: MFA设置列表
        """
        try:
            async with await self.user_repo.get_session() as session:
                result = await session.execute(
                    select(MFASecretModel).where(MFASecretModel.user_id == user_id)
                )
                mfa_secrets = list(result.scalars().all())
                
                settings = []
                for mfa_secret in mfa_secrets:
                    settings.append({
                        "id": mfa_secret.id,
                        "mfa_type": mfa_secret.mfa_type,
                        "is_active": mfa_secret.is_active,
                        "created_at": mfa_secret.created_at.isoformat(),
                        "backup_codes_count": len(mfa_secret.backup_codes) if mfa_secret.backup_codes else 0
                    })
                
                return settings
                
        except Exception as e:
            self.logger.error(f"获取MFA设置失败: {e}")
            return []
    
    async def regenerate_backup_codes(self, user_id: str, mfa_type: MFATypeEnum) -> Optional[List[str]]:
        """
        重新生成备用验证码
        
        Args:
            user_id: 用户ID
            mfa_type: MFA类型
            
        Returns:
            Optional[List[str]]: 新的备用验证码列表
        """
        try:
            async with await self.user_repo.get_session() as session:
                result = await session.execute(
                    select(MFASecretModel).where(
                        and_(
                            MFASecretModel.user_id == user_id,
                            MFASecretModel.mfa_type == mfa_type.value,
                            MFASecretModel.is_active == True
                        )
                    )
                )
                mfa_secret = result.scalar_one_or_none()
                
                if mfa_secret:
                    # 生成新的备用验证码
                    new_backup_codes = self.generate_backup_codes()
                    mfa_secret.backup_codes = new_backup_codes
                    mfa_secret.updated_at = datetime.utcnow()
                    await session.commit()
                    
                    self.logger.info(f"备用验证码重新生成成功: {user_id}")
                    return new_backup_codes
            
            return None
            
        except Exception as e:
            self.logger.error(f"重新生成备用验证码失败: {e}")
            return None
    
    async def is_mfa_enabled(self, user_id: str) -> bool:
        """
        检查用户是否启用了MFA
        
        Args:
            user_id: 用户ID
            
        Returns:
            bool: 是否启用MFA
        """
        try:
            async with await self.user_repo.get_session() as session:
                result = await session.execute(
                    select(MFASecretModel).where(
                        and_(
                            MFASecretModel.user_id == user_id,
                            MFASecretModel.is_active == True
                        )
                    )
                )
                return result.scalar_one_or_none() is not None
                
        except Exception as e:
            self.logger.error(f"检查MFA状态失败: {e}")
            return False 