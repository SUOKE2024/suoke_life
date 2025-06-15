"""
邮件服务

处理邮件发送功能，包括验证邮件、密码重置邮件等。
"""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict, Any
import aiosmtplib
from jinja2 import Environment, FileSystemLoader, Template
from pathlib import Path

from internal.config.settings import get_settings


class EmailService:
    """邮件服务类"""
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = logging.getLogger(__name__)
        
        # 初始化模板引擎
        template_dir = Path(__file__).parent.parent.parent / "templates" / "email"
        if template_dir.exists():
            self.jinja_env = Environment(loader=FileSystemLoader(str(template_dir)))
        else:
            self.jinja_env = None
            self.logger.warning(f"邮件模板目录不存在: {template_dir}")
    
    async def send_email(
        self,
        to_emails: List[str],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """
        发送邮件
        
        Args:
            to_emails: 收件人邮箱列表
            subject: 邮件主题
            html_content: HTML内容
            text_content: 纯文本内容
            attachments: 附件列表
            
        Returns:
            bool: 发送是否成功
        """
        try:
            # 创建邮件消息
            message = MIMEMultipart("alternative")
            message["From"] = self.settings.smtp_from_email
            message["To"] = ", ".join(to_emails)
            message["Subject"] = subject
            
            # 添加文本内容
            if text_content:
                text_part = MIMEText(text_content, "plain", "utf-8")
                message.attach(text_part)
            
            # 添加HTML内容
            html_part = MIMEText(html_content, "html", "utf-8")
            message.attach(html_part)
            
            # 添加附件
            if attachments:
                for attachment in attachments:
                    await self._add_attachment(message, attachment)
            
            # 发送邮件
            await aiosmtplib.send(
                message,
                hostname=self.settings.smtp_host,
                port=self.settings.smtp_port,
                start_tls=self.settings.smtp_use_tls,
                username=self.settings.smtp_username,
                password=self.settings.smtp_password,
            )
            
            self.logger.info(f"邮件发送成功: {to_emails}")
            return True
            
        except Exception as e:
            self.logger.error(f"邮件发送失败: {e}")
            return False
    
    async def _add_attachment(self, message: MIMEMultipart, attachment: Dict[str, Any]):
        """添加附件"""
        try:
            filename = attachment.get("filename")
            content = attachment.get("content")
            content_type = attachment.get("content_type", "application/octet-stream")
            
            if not filename or not content:
                return
            
            part = MIMEBase(*content_type.split("/"))
            part.set_payload(content)
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {filename}",
            )
            message.attach(part)
            
        except Exception as e:
            self.logger.error(f"添加附件失败: {e}")
    
    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        渲染邮件模板
        
        Args:
            template_name: 模板名称
            context: 模板上下文
            
        Returns:
            str: 渲染后的HTML内容
        """
        if not self.jinja_env:
            return self._get_default_template(template_name, context)
        
        try:
            template = self.jinja_env.get_template(f"{template_name}.html")
            return template.render(**context)
        except Exception as e:
            self.logger.error(f"模板渲染失败: {e}")
            return self._get_default_template(template_name, context)
    
    def _get_default_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """获取默认模板"""
        if template_name == "verification":
            return f"""
            <html>
            <body>
                <h2>邮箱验证</h2>
                <p>您好 {context.get('username', '')}，</p>
                <p>请点击以下链接验证您的邮箱：</p>
                <p><a href="{context.get('verification_url', '')}">验证邮箱</a></p>
                <p>验证码：{context.get('verification_code', '')}</p>
                <p>此链接将在24小时后过期。</p>
                <p>如果您没有注册账户，请忽略此邮件。</p>
                <p>索克生活团队</p>
            </body>
            </html>
            """
        elif template_name == "password_reset":
            return f"""
            <html>
            <body>
                <h2>密码重置</h2>
                <p>您好 {context.get('username', '')}，</p>
                <p>您请求重置密码。请点击以下链接重置密码：</p>
                <p><a href="{context.get('reset_url', '')}">重置密码</a></p>
                <p>重置码：{context.get('reset_code', '')}</p>
                <p>此链接将在1小时后过期。</p>
                <p>如果您没有请求重置密码，请忽略此邮件。</p>
                <p>索克生活团队</p>
            </body>
            </html>
            """
        elif template_name == "welcome":
            return f"""
            <html>
            <body>
                <h2>欢迎加入索克生活</h2>
                <p>您好 {context.get('username', '')}，</p>
                <p>欢迎加入索克生活！您的账户已成功创建。</p>
                <p>您可以开始探索我们的健康管理平台了。</p>
                <p>如有任何问题，请联系我们的客服团队。</p>
                <p>索克生活团队</p>
            </body>
            </html>
            """
        else:
            return f"""
            <html>
            <body>
                <h2>索克生活通知</h2>
                <p>您好，</p>
                <p>这是来自索克生活的通知。</p>
                <p>索克生活团队</p>
            </body>
            </html>
            """
    
    async def send_verification_email(
        self, 
        email: str, 
        username: str, 
        verification_code: str,
        verification_url: str
    ) -> bool:
        """发送验证邮件"""
        context = {
            "username": username,
            "verification_code": verification_code,
            "verification_url": verification_url
        }
        
        html_content = self.render_template("verification", context)
        text_content = f"""
        您好 {username}，
        
        请使用以下验证码验证您的邮箱：{verification_code}
        
        或点击链接：{verification_url}
        
        此验证码将在24小时后过期。
        
        索克生活团队
        """
        
        return await self.send_email(
            to_emails=[email],
            subject="索克生活 - 邮箱验证",
            html_content=html_content,
            text_content=text_content
        )
    
    async def send_password_reset_email(
        self, 
        email: str, 
        username: str, 
        reset_code: str,
        reset_url: str
    ) -> bool:
        """发送密码重置邮件"""
        context = {
            "username": username,
            "reset_code": reset_code,
            "reset_url": reset_url
        }
        
        html_content = self.render_template("password_reset", context)
        text_content = f"""
        您好 {username}，
        
        您请求重置密码。请使用以下重置码：{reset_code}
        
        或点击链接：{reset_url}
        
        此重置码将在1小时后过期。
        
        如果您没有请求重置密码，请忽略此邮件。
        
        索克生活团队
        """
        
        return await self.send_email(
            to_emails=[email],
            subject="索克生活 - 密码重置",
            html_content=html_content,
            text_content=text_content
        )
    
    async def send_welcome_email(self, email: str, username: str) -> bool:
        """发送欢迎邮件"""
        context = {
            "username": username
        }
        
        html_content = self.render_template("welcome", context)
        text_content = f"""
        您好 {username}，
        
        欢迎加入索克生活！您的账户已成功创建。
        
        您可以开始探索我们的健康管理平台了。
        
        如有任何问题，请联系我们的客服团队。
        
        索克生活团队
        """
        
        return await self.send_email(
            to_emails=[email],
            subject="欢迎加入索克生活",
            html_content=html_content,
            text_content=text_content
        )
    
    async def send_login_notification(
        self, 
        email: str, 
        username: str, 
        ip_address: str,
        device_info: str,
        login_time: str
    ) -> bool:
        """发送登录通知邮件"""
        context = {
            "username": username,
            "ip_address": ip_address,
            "device_info": device_info,
            "login_time": login_time
        }
        
        html_content = f"""
        <html>
        <body>
            <h2>登录通知</h2>
            <p>您好 {username}，</p>
            <p>您的账户在以下时间和地点登录：</p>
            <ul>
                <li>时间：{login_time}</li>
                <li>IP地址：{ip_address}</li>
                <li>设备信息：{device_info}</li>
            </ul>
            <p>如果这不是您的操作，请立即更改密码并联系我们。</p>
            <p>索克生活团队</p>
        </body>
        </html>
        """
        
        text_content = f"""
        您好 {username}，
        
        您的账户在以下时间和地点登录：
        时间：{login_time}
        IP地址：{ip_address}
        设备信息：{device_info}
        
        如果这不是您的操作，请立即更改密码并联系我们。
        
        索克生活团队
        """
        
        return await self.send_email(
            to_emails=[email],
            subject="索克生活 - 登录通知",
            html_content=html_content,
            text_content=text_content
        )
    
    async def test_connection(self) -> bool:
        """测试邮件服务连接"""
        try:
            # 创建SMTP连接测试
            smtp = aiosmtplib.SMTP(
                hostname=self.settings.smtp_host,
                port=self.settings.smtp_port,
                start_tls=self.settings.smtp_use_tls
            )
            
            await smtp.connect()
            
            if self.settings.smtp_username and self.settings.smtp_password:
                await smtp.login(
                    self.settings.smtp_username, 
                    self.settings.smtp_password
                )
            
            await smtp.quit()
            
            self.logger.info("邮件服务连接测试成功")
            return True
            
        except Exception as e:
            self.logger.error(f"邮件服务连接测试失败: {e}")
            return False 