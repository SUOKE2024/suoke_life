"""邮件服务核心模块"""

import asyncio
import smtplib
from abc import ABC, abstractmethod
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Dict, List, Optional, Union
import aiofiles
import aiosmtplib
from jinja2 import Environment, FileSystemLoader, Template
import structlog

from auth_service.config.settings import EmailSettings

logger = structlog.get_logger()


class EmailProvider(ABC):
    """邮件提供商抽象基类"""
    
    @abstractmethod
    async def send_email(
        self,
        to_email: Union[str, List[str]],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
    ) -> bool:
        """发送邮件"""
        pass


class SMTPProvider(EmailProvider):
    """SMTP邮件提供商"""
    
    def __init__(self, settings: EmailSettings):
        self.settings = settings
    
    async def send_email(
        self,
        to_email: Union[str, List[str]],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
    ) -> bool:
        """通过SMTP发送邮件"""
        try:
            # 准备收件人列表
            if isinstance(to_email, str):
                recipients = [to_email]
            else:
                recipients = to_email
            
            # 设置发件人
            sender_email = from_email or self.settings.from_email
            sender_name = from_name or self.settings.from_name
            
            # 创建邮件消息
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{sender_name} <{sender_email}>"
            message["To"] = ", ".join(recipients)
            
            # 添加文本内容
            if text_content:
                text_part = MIMEText(text_content, "plain", "utf-8")
                message.attach(text_part)
            
            # 添加HTML内容
            html_part = MIMEText(html_content, "html", "utf-8")
            message.attach(html_part)
            
            # 发送邮件
            if self.settings.use_ssl:
                await aiosmtplib.send(
                    message,
                    hostname=self.settings.smtp_host,
                    port=self.settings.smtp_port,
                    username=self.settings.smtp_username,
                    password=self.settings.smtp_password,
                    use_tls=False,
                    start_tls=False,
                )
            else:
                await aiosmtplib.send(
                    message,
                    hostname=self.settings.smtp_host,
                    port=self.settings.smtp_port,
                    username=self.settings.smtp_username,
                    password=self.settings.smtp_password,
                    use_tls=self.settings.use_tls,
                    start_tls=self.settings.use_tls,
                )
            
            logger.info(
                "Email sent successfully",
                to_email=recipients,
                subject=subject,
                provider="smtp"
            )
            return True
            
        except Exception as e:
            logger.error(
                "Failed to send email via SMTP",
                error=str(e),
                to_email=recipients,
                subject=subject
            )
            return False


class SendGridProvider(EmailProvider):
    """SendGrid邮件提供商"""
    
    def __init__(self, settings: EmailSettings):
        self.settings = settings
        self.api_key = settings.sendgrid_api_key
    
    async def send_email(
        self,
        to_email: Union[str, List[str]],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
    ) -> bool:
        """通过SendGrid发送邮件"""
        try:
            import httpx
            
            # 准备收件人列表
            if isinstance(to_email, str):
                recipients = [{"email": to_email}]
            else:
                recipients = [{"email": email} for email in to_email]
            
            # 设置发件人
            sender_email = from_email or self.settings.from_email
            sender_name = from_name or self.settings.from_name
            
            # 构建邮件数据
            mail_data = {
                "personalizations": [
                    {
                        "to": recipients,
                        "subject": subject
                    }
                ],
                "from": {
                    "email": sender_email,
                    "name": sender_name
                },
                "content": [
                    {
                        "type": "text/html",
                        "value": html_content
                    }
                ]
            }
            
            # 添加文本内容
            if text_content:
                mail_data["content"].insert(0, {
                    "type": "text/plain",
                    "value": text_content
                })
            
            # 发送请求
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.sendgrid.com/v3/mail/send",
                    json=mail_data,
                    headers=headers
                )
                
                if response.status_code == 202:
                    logger.info(
                        "Email sent successfully",
                        to_email=to_email,
                        subject=subject,
                        provider="sendgrid"
                    )
                    return True
                else:
                    logger.error(
                        "Failed to send email via SendGrid",
                        status_code=response.status_code,
                        response=response.text,
                        to_email=to_email,
                        subject=subject
                    )
                    return False
                    
        except Exception as e:
            logger.error(
                "Failed to send email via SendGrid",
                error=str(e),
                to_email=to_email,
                subject=subject
            )
            return False


class AWSProvider(EmailProvider):
    """AWS SES邮件提供商"""
    
    def __init__(self, settings: EmailSettings):
        self.settings = settings
    
    async def send_email(
        self,
        to_email: Union[str, List[str]],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
    ) -> bool:
        """通过AWS SES发送邮件"""
        try:
            import boto3
            
            # 创建SES客户端
            ses_client = boto3.client(
                'ses',
                aws_access_key_id=self.settings.aws_access_key_id,
                aws_secret_access_key=self.settings.aws_secret_access_key,
                region_name=self.settings.aws_region
            )
            
            # 准备收件人列表
            if isinstance(to_email, str):
                recipients = [to_email]
            else:
                recipients = to_email
            
            # 设置发件人
            sender_email = from_email or self.settings.from_email
            sender_name = from_name or self.settings.from_name
            sender = f"{sender_name} <{sender_email}>"
            
            # 构建邮件内容
            body = {}
            if text_content:
                body['Text'] = {'Data': text_content, 'Charset': 'UTF-8'}
            if html_content:
                body['Html'] = {'Data': html_content, 'Charset': 'UTF-8'}
            
            # 发送邮件
            response = ses_client.send_email(
                Source=sender,
                Destination={'ToAddresses': recipients},
                Message={
                    'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                    'Body': body
                }
            )
            
            logger.info(
                "Email sent successfully",
                to_email=recipients,
                subject=subject,
                provider="aws_ses",
                message_id=response['MessageId']
            )
            return True
            
        except Exception as e:
            logger.error(
                "Failed to send email via AWS SES",
                error=str(e),
                to_email=to_email,
                subject=subject
            )
            return False


class EmailTemplateManager:
    """邮件模板管理器"""
    
    def __init__(self, template_dir: str):
        self.template_dir = Path(template_dir)
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=True
        )
    
    async def render_template(
        self,
        template_name: str,
        context: Dict,
        language: str = "zh"
    ) -> tuple[str, str]:
        """渲染邮件模板"""
        try:
            # 尝试加载特定语言的模板
            template_path = f"{language}/{template_name}"
            try:
                template = self.env.get_template(template_path)
            except:
                # 回退到默认模板
                template = self.env.get_template(template_name)
            
            # 渲染HTML内容
            html_content = template.render(**context)
            
            # 尝试渲染文本版本
            text_template_name = template_name.replace('.html', '.txt')
            text_template_path = f"{language}/{text_template_name}"
            try:
                text_template = self.env.get_template(text_template_path)
                text_content = text_template.render(**context)
            except:
                try:
                    text_template = self.env.get_template(text_template_name)
                    text_content = text_template.render(**context)
                except:
                    # 如果没有文本模板，从HTML中提取文本
                    import re
                    text_content = re.sub(r'<[^>]+>', '', html_content)
                    text_content = re.sub(r'\s+', ' ', text_content).strip()
            
            return html_content, text_content
            
        except Exception as e:
            logger.error(
                "Failed to render email template",
                template_name=template_name,
                error=str(e)
            )
            raise


class EmailService:
    """邮件服务"""
    
    def __init__(self, settings: EmailSettings):
        self.settings = settings
        self.provider = self._create_provider()
        self.template_manager = EmailTemplateManager(settings.template_dir)
        self._rate_limiter = {}  # 简单的速率限制器
    
    def _create_provider(self) -> EmailProvider:
        """创建邮件提供商"""
        if self.settings.provider == "sendgrid":
            return SendGridProvider(self.settings)
        elif self.settings.provider == "aws_ses":
            return AWSProvider(self.settings)
        else:
            return SMTPProvider(self.settings)
    
    async def send_template_email(
        self,
        to_email: Union[str, List[str]],
        template_name: str,
        context: Dict,
        subject: str,
        language: str = "zh",
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
    ) -> bool:
        """发送模板邮件"""
        try:
            # 渲染模板
            html_content, text_content = await self.template_manager.render_template(
                template_name, context, language
            )
            
            # 发送邮件
            return await self.send_email(
                to_email=to_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                from_email=from_email,
                from_name=from_name
            )
            
        except Exception as e:
            logger.error(
                "Failed to send template email",
                template_name=template_name,
                to_email=to_email,
                error=str(e)
            )
            return False
    
    async def send_email(
        self,
        to_email: Union[str, List[str]],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        retry_count: int = 0,
    ) -> bool:
        """发送邮件"""
        try:
            # 检查速率限制
            if not self._check_rate_limit(to_email):
                logger.warning(
                    "Email rate limit exceeded",
                    to_email=to_email
                )
                return False
            
            # 发送邮件
            success = await self.provider.send_email(
                to_email=to_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                from_email=from_email,
                from_name=from_name
            )
            
            if not success and retry_count < self.settings.max_retries:
                # 重试发送
                logger.info(
                    "Retrying email send",
                    retry_count=retry_count + 1,
                    to_email=to_email
                )
                await asyncio.sleep(self.settings.retry_delay)
                return await self.send_email(
                    to_email=to_email,
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content,
                    from_email=from_email,
                    from_name=from_name,
                    retry_count=retry_count + 1
                )
            
            return success
            
        except Exception as e:
            logger.error(
                "Failed to send email",
                error=str(e),
                to_email=to_email,
                subject=subject
            )
            return False
    
    def _check_rate_limit(self, email: Union[str, List[str]]) -> bool:
        """检查速率限制"""
        # 这里实现简单的速率限制逻辑
        # 在生产环境中应该使用Redis等外部存储
        import time
        
        current_time = time.time()
        hour_key = int(current_time // 3600)
        
        if isinstance(email, list):
            emails = email
        else:
            emails = [email]
        
        for email_addr in emails:
            key = f"{email_addr}:{hour_key}"
            count = self._rate_limiter.get(key, 0)
            
            if count >= self.settings.rate_limit:
                return False
            
            self._rate_limiter[key] = count + 1
        
        # 清理过期的记录
        expired_keys = [
            key for key in self._rate_limiter.keys()
            if int(key.split(':')[1]) < hour_key - 1
        ]
        for key in expired_keys:
            del self._rate_limiter[key]
        
        return True
    
    async def send_verification_email(
        self,
        to_email: str,
        username: str,
        verification_token: str,
        language: str = "zh"
    ) -> bool:
        """发送邮箱验证邮件"""
        context = {
            "username": username,
            "verification_url": f"https://app.suokelife.com/verify-email?token={verification_token}",
            "app_name": "索克生活",
            "support_email": "support@suokelife.com"
        }
        
        return await self.send_template_email(
            to_email=to_email,
            template_name="email_verification.html",
            context=context,
            subject="验证您的邮箱地址 - 索克生活",
            language=language
        )
    
    async def send_password_reset_email(
        self,
        to_email: str,
        username: str,
        reset_token: str,
        language: str = "zh"
    ) -> bool:
        """发送密码重置邮件"""
        context = {
            "username": username,
            "reset_url": f"https://app.suokelife.com/reset-password?token={reset_token}",
            "app_name": "索克生活",
            "support_email": "support@suokelife.com",
            "expires_in": "24小时"
        }
        
        return await self.send_template_email(
            to_email=to_email,
            template_name="password_reset.html",
            context=context,
            subject="重置您的密码 - 索克生活",
            language=language
        )
    
    async def send_welcome_email(
        self,
        to_email: str,
        username: str,
        language: str = "zh"
    ) -> bool:
        """发送欢迎邮件"""
        context = {
            "username": username,
            "app_name": "索克生活",
            "app_url": "https://app.suokelife.com",
            "support_email": "support@suokelife.com"
        }
        
        return await self.send_template_email(
            to_email=to_email,
            template_name="welcome.html",
            context=context,
            subject="欢迎加入索克生活！",
            language=language
        ) 