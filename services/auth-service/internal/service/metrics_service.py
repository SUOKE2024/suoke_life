"""
监控指标服务

提供Prometheus指标收集和健康检查功能。
"""
import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from prometheus_client import Counter, Histogram, Gauge, Info
import psutil

from internal.config.settings import get_settings
from internal.repository.user_repository_new import UserRepository
from internal.repository.audit_repository import AuditRepository
from internal.model.user import AuditActionEnum


class MetricsService:
    """监控指标服务类"""
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = logging.getLogger(__name__)
        
        # 初始化仓储
        self.user_repo = UserRepository()
        self.audit_repo = AuditRepository()
        # 暂时不初始化TokenRepository，因为它需要Redis连接
        self.token_repo = None
        
        # 定义Prometheus指标
        self._init_metrics()
    
    def _init_metrics(self):
        """初始化Prometheus指标"""
        # 计数器指标
        self.login_attempts_total = Counter(
            'auth_login_attempts_total',
            'Total number of login attempts',
            ['status', 'method']
        )
        
        self.registration_total = Counter(
            'auth_registration_total',
            'Total number of user registrations',
            ['status']
        )
        
        self.password_reset_total = Counter(
            'auth_password_reset_total',
            'Total number of password reset requests',
            ['status']
        )
        
        self.mfa_verification_total = Counter(
            'auth_mfa_verification_total',
            'Total number of MFA verifications',
            ['status', 'type']
        )
        
        # 直方图指标（响应时间）
        self.request_duration = Histogram(
            'auth_request_duration_seconds',
            'Request duration in seconds',
            ['method', 'endpoint']
        )
        
        self.database_query_duration = Histogram(
            'auth_database_query_duration_seconds',
            'Database query duration in seconds',
            ['operation']
        )
        
        # 仪表指标（当前状态）
        self.active_users = Gauge(
            'auth_active_users',
            'Number of active users'
        )
        
        self.active_sessions = Gauge(
            'auth_active_sessions',
            'Number of active sessions'
        )
        
        self.failed_login_rate = Gauge(
            'auth_failed_login_rate',
            'Failed login rate in the last hour'
        )
        
        # 系统指标
        self.system_cpu_usage = Gauge(
            'auth_system_cpu_usage_percent',
            'System CPU usage percentage'
        )
        
        self.system_memory_usage = Gauge(
            'auth_system_memory_usage_percent',
            'System memory usage percentage'
        )
        
        # 信息指标
        self.service_info = Info(
            'auth_service_info',
            'Authentication service information'
        )
        
        # 设置服务信息
        self.service_info.info({
            'version': '1.0.0',
            'environment': self.settings.environment,
            'service': 'auth-service'
        })
    
    def record_login_attempt(self, success: bool, method: str = 'password'):
        """记录登录尝试"""
        status = 'success' if success else 'failure'
        self.login_attempts_total.labels(status=status, method=method).inc()
    
    def record_registration(self, success: bool):
        """记录用户注册"""
        status = 'success' if success else 'failure'
        self.registration_total.labels(status=status).inc()
    
    def record_password_reset(self, success: bool):
        """记录密码重置"""
        status = 'success' if success else 'failure'
        self.password_reset_total.labels(status=status).inc()
    
    def record_mfa_verification(self, success: bool, mfa_type: str = 'totp'):
        """记录MFA验证"""
        status = 'success' if success else 'failure'
        self.mfa_verification_total.labels(status=status, type=mfa_type).inc()
    
    def record_request_duration(self, duration: float, method: str, endpoint: str):
        """记录请求持续时间"""
        self.request_duration.labels(method=method, endpoint=endpoint).observe(duration)
    
    def record_database_query_duration(self, duration: float, operation: str):
        """记录数据库查询持续时间"""
        self.database_query_duration.labels(operation=operation).observe(duration)
    
    async def update_active_users_count(self):
        """更新活跃用户数量"""
        try:
            count = await self.user_repo.count_users(is_active=True)
            self.active_users.set(count)
        except Exception as e:
            self.logger.error(f"更新活跃用户数量失败: {e}")
    
    async def update_active_sessions_count(self):
        """更新活跃会话数量"""
        try:
            # 如果TokenRepository可用，获取令牌统计
            if self.token_repo:
                stats = await self.token_repo.get_token_stats()
                self.active_sessions.set(stats.get('active', 0))
            else:
                # 暂时设置为0
                self.active_sessions.set(0)
        except Exception as e:
            self.logger.error(f"更新活跃会话数量失败: {e}")
    
    async def update_failed_login_rate(self):
        """更新失败登录率"""
        try:
            # 获取过去1小时的失败登录次数
            failed_count = await self.audit_repo.get_failed_login_count(hours=1)
            
            # 获取过去1小时的总登录次数
            total_attempts = await self.audit_repo.count_logs(
                action=AuditActionEnum.LOGIN,
                start_date=datetime.utcnow() - timedelta(hours=1)
            )
            
            if total_attempts > 0:
                rate = failed_count / total_attempts
            else:
                rate = 0
            
            self.failed_login_rate.set(rate)
        except Exception as e:
            self.logger.error(f"更新失败登录率失败: {e}")
    
    def update_system_metrics(self):
        """更新系统指标"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            self.system_cpu_usage.set(cpu_percent)
            
            # 内存使用率
            memory = psutil.virtual_memory()
            self.system_memory_usage.set(memory.percent)
            
        except Exception as e:
            self.logger.error(f"更新系统指标失败: {e}")
    
    async def collect_all_metrics(self):
        """收集所有指标"""
        await self.update_active_users_count()
        await self.update_active_sessions_count()
        await self.update_failed_login_rate()
        self.update_system_metrics()
    
    async def get_health_status(self) -> Dict[str, Any]:
        """获取健康状态"""
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {}
        }
        
        try:
            # 数据库连接检查
            start_time = time.time()
            await self.user_repo.count()
            db_duration = time.time() - start_time
            
            health_status["checks"]["database"] = {
                "status": "healthy",
                "response_time_ms": round(db_duration * 1000, 2)
            }
        except Exception as e:
            health_status["checks"]["database"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_status["status"] = "unhealthy"
        
        # 系统资源检查
        try:
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            health_status["checks"]["system"] = {
                "status": "healthy",
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent
            }
            
            # 检查资源使用率是否过高
            if cpu_percent > 90 or memory.percent > 90 or disk.percent > 90:
                health_status["checks"]["system"]["status"] = "warning"
                if health_status["status"] == "healthy":
                    health_status["status"] = "warning"
                    
        except Exception as e:
            health_status["checks"]["system"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_status["status"] = "unhealthy"
        
        return health_status
    
    async def get_service_stats(self) -> Dict[str, Any]:
        """获取服务统计信息"""
        try:
            # 用户统计
            total_users = await self.user_repo.count_users()
            active_users = await self.user_repo.count_users(is_active=True)
            
            # 令牌统计（如果可用）
            token_stats = {}
            if self.token_repo:
                try:
                    token_stats = await self.token_repo.get_token_stats()
                except:
                    token_stats = {"active": 0, "total": 0}
            else:
                token_stats = {"active": 0, "total": 0}
            
            # 审计统计（最近24小时）
            audit_stats = await self.audit_repo.get_activity_stats(
                start_date=datetime.utcnow() - timedelta(hours=24)
            )
            
            return {
                "users": {
                    "total": total_users,
                    "active": active_users,
                    "inactive": total_users - active_users
                },
                "tokens": token_stats,
                "activity": audit_stats,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"获取服务统计失败: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


# 全局指标服务实例
metrics_service = MetricsService()


def get_metrics_service() -> MetricsService:
    """获取指标服务实例"""
    return metrics_service 