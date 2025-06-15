"""
短信服务

处理短信发送功能，包括验证码短信、通知短信等。
"""
import logging
import re
from typing import Optional, Dict, Any
from twilio.rest import Client
from twilio.base.exceptions import TwilioException

from internal.config.settings import get_settings


class SMSService:
    """短信服务类"""
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = logging.getLogger(__name__)
        
        # 初始化Twilio客户端
        if self.settings.twilio_account_sid and self.settings.twilio_auth_token:
            self.client = Client(
                self.settings.twilio_account_sid,
                self.settings.twilio_auth_token
            )
        else:
            self.client = None
            self.logger.warning("Twilio配置缺失，短信服务不可用")
    
    def _validate_phone_number(self, phone_number: str) -> bool:
        """
        验证手机号格式
        
        Args:
            phone_number: 手机号
            
        Returns:
            bool: 是否有效
        """
        # 简单的手机号验证（支持国际格式）
        pattern = r'^\+?[1-9]\d{1,14}$'
        return bool(re.match(pattern, phone_number))
    
    def _format_phone_number(self, phone_number: str) -> str:
        """
        格式化手机号
        
        Args:
            phone_number: 原始手机号
            
        Returns:
            str: 格式化后的手机号
        """
        # 移除所有非数字字符
        cleaned = re.sub(r'\D', '', phone_number)
        
        # 如果是中国手机号（11位），添加+86前缀
        if len(cleaned) == 11 and cleaned.startswith(('13', '14', '15', '16', '17', '18', '19')):
            return f"+86{cleaned}"
        
        # 如果已经有+号，直接返回
        if phone_number.startswith('+'):
            return phone_number
        
        # 默认添加+号
        return f"+{cleaned}"
    
    async def send_sms(
        self,
        phone_number: str,
        message: str,
        template_id: Optional[str] = None,
        template_params: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        发送短信
        
        Args:
            phone_number: 手机号
            message: 短信内容
            template_id: 模板ID（可选）
            template_params: 模板参数（可选）
            
        Returns:
            bool: 发送是否成功
        """
        if not self.client:
            self.logger.error("短信服务未配置")
            return False
        
        # 验证手机号
        if not self._validate_phone_number(phone_number):
            self.logger.error(f"无效的手机号: {phone_number}")
            return False
        
        # 格式化手机号
        formatted_phone = self._format_phone_number(phone_number)
        
        try:
            # 发送短信
            message_obj = self.client.messages.create(
                body=message,
                from_=self.settings.twilio_phone_number,
                to=formatted_phone
            )
            
            self.logger.info(f"短信发送成功: {formatted_phone}, SID: {message_obj.sid}")
            return True
            
        except TwilioException as e:
            self.logger.error(f"Twilio短信发送失败: {e}")
            return False
        except Exception as e:
            self.logger.error(f"短信发送失败: {e}")
            return False
    
    async def send_verification_code(
        self,
        phone_number: str,
        verification_code: str
    ) -> bool:
        """
        发送验证码短信
        
        Args:
            phone_number: 手机号
            verification_code: 验证码
            
        Returns:
            bool: 发送是否成功
        """
        message = f"【索克生活】您的验证码是：{verification_code}，5分钟内有效。请勿泄露给他人。"
        
        return await self.send_sms(phone_number, message)
    
    async def send_login_notification(
        self,
        phone_number: str,
        username: str,
        ip_address: str,
        login_time: str
    ) -> bool:
        """
        发送登录通知短信
        
        Args:
            phone_number: 手机号
            username: 用户名
            ip_address: IP地址
            login_time: 登录时间
            
        Returns:
            bool: 发送是否成功
        """
        message = f"【索克生活】{username}，您的账户于{login_time}在IP {ip_address}登录。如非本人操作，请立即修改密码。"
        
        return await self.send_sms(phone_number, message)
    
    async def send_password_reset_code(
        self,
        phone_number: str,
        reset_code: str
    ) -> bool:
        """
        发送密码重置验证码
        
        Args:
            phone_number: 手机号
            reset_code: 重置码
            
        Returns:
            bool: 发送是否成功
        """
        message = f"【索克生活】您的密码重置验证码是：{reset_code}，10分钟内有效。请勿泄露给他人。"
        
        return await self.send_sms(phone_number, message)
    
    async def send_account_locked_notification(
        self,
        phone_number: str,
        username: str,
        locked_until: str
    ) -> bool:
        """
        发送账户锁定通知
        
        Args:
            phone_number: 手机号
            username: 用户名
            locked_until: 锁定到期时间
            
        Returns:
            bool: 发送是否成功
        """
        message = f"【索克生活】{username}，您的账户因多次登录失败已被锁定至{locked_until}。如有疑问请联系客服。"
        
        return await self.send_sms(phone_number, message)
    
    async def send_welcome_message(
        self,
        phone_number: str,
        username: str
    ) -> bool:
        """
        发送欢迎短信
        
        Args:
            phone_number: 手机号
            username: 用户名
            
        Returns:
            bool: 发送是否成功
        """
        message = f"【索克生活】{username}，欢迎加入索克生活！开始您的健康管理之旅吧。"
        
        return await self.send_sms(phone_number, message)
    
    async def test_connection(self) -> bool:
        """
        测试短信服务连接
        
        Returns:
            bool: 连接是否成功
        """
        if not self.client:
            return False
        
        try:
            # 获取账户信息来测试连接
            account = self.client.api.accounts(self.settings.twilio_account_sid).fetch()
            
            self.logger.info(f"短信服务连接测试成功，账户状态: {account.status}")
            return account.status == 'active'
            
        except TwilioException as e:
            self.logger.error(f"短信服务连接测试失败: {e}")
            return False
        except Exception as e:
            self.logger.error(f"短信服务连接测试失败: {e}")
            return False
    
    async def get_message_status(self, message_sid: str) -> Optional[Dict[str, Any]]:
        """
        获取短信状态
        
        Args:
            message_sid: 消息SID
            
        Returns:
            Optional[Dict]: 消息状态信息
        """
        if not self.client:
            return None
        
        try:
            message = self.client.messages(message_sid).fetch()
            
            return {
                "sid": message.sid,
                "status": message.status,
                "error_code": message.error_code,
                "error_message": message.error_message,
                "date_sent": message.date_sent.isoformat() if message.date_sent else None,
                "date_updated": message.date_updated.isoformat() if message.date_updated else None,
                "price": message.price,
                "price_unit": message.price_unit
            }
            
        except TwilioException as e:
            self.logger.error(f"获取短信状态失败: {e}")
            return None
        except Exception as e:
            self.logger.error(f"获取短信状态失败: {e}")
            return None 