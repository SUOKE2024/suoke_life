"""
Celery应用配置和任务定义

负责异步任务处理，包括：
- AI分析任务
- 审核工作流任务
- 通知任务
- 定时任务
"""
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from celery import Celery
from celery.schedules import crontab

from internal.config.settings import get_settings

logger = logging.getLogger(__name__)

# 获取配置
settings = get_settings()

# 创建Celery应用
celery_app = Celery(
    "human-review-service",
    broker=settings.celery.broker_url,
    backend=settings.celery.result_backend,
    include=[
        'internal.tasks.review_tasks',
        'internal.tasks.ai_tasks',
        'internal.tasks.workflow_tasks',
        'internal.tasks.notification_tasks'
    ]
)

# Celery配置
celery_app.conf.update(
    # 任务序列化
    task_serializer=settings.celery.task_serializer,
    result_serializer=settings.celery.result_serializer,
    accept_content=settings.celery.accept_content,
    
    # 时区设置
    timezone=settings.celery.timezone,
    enable_utc=settings.celery.enable_utc,
    
    # 任务路由
    task_routes={
        'internal.tasks.ai_tasks.*': {'queue': 'ai_analysis'},
        'internal.tasks.review_tasks.*': {'queue': 'review'},
        'internal.tasks.workflow_tasks.*': {'queue': 'workflow'},
        'internal.tasks.notification_tasks.*': {'queue': 'notifications'},
    },
    
    # 任务优先级
    task_default_priority=5,
    worker_prefetch_multiplier=1,
    
    # 任务超时
    task_soft_time_limit=300,  # 5分钟软超时
    task_time_limit=600,       # 10分钟硬超时
    
    # 结果过期时间
    result_expires=3600,  # 1小时
    
    # 任务重试
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    
    # 定时任务
    beat_schedule={
        # 清理过期任务
        'cleanup-expired-tasks': {
            'task': 'internal.tasks.maintenance_tasks.cleanup_expired_tasks',
            'schedule': crontab(minute=0, hour=2),  # 每天凌晨2点
        },
        
        # 生成审核统计报告
        'generate-review-stats': {
            'task': 'internal.tasks.stats_tasks.generate_daily_stats',
            'schedule': crontab(minute=30, hour=1),  # 每天凌晨1:30
        },
        
        # 检查超时任务
        'check-timeout-tasks': {
            'task': 'internal.tasks.workflow_tasks.check_timeout_tasks',
            'schedule': crontab(minute='*/15'),  # 每15分钟
        },
        
        # 健康检查
        'health-check': {
            'task': 'internal.tasks.maintenance_tasks.health_check',
            'schedule': crontab(minute='*/5'),  # 每5分钟
        },
        
        # 自动分配任务
        'auto-assign-tasks': {
            'task': 'internal.tasks.workflow_tasks.auto_assign_pending_tasks',
            'schedule': crontab(minute='*/10'),  # 每10分钟
        },
    },
)

# 任务装饰器配置
def task_with_retry(**kwargs):
    """带重试机制的任务装饰器"""
    default_kwargs = {
        'bind': True,
        'autoretry_for': (Exception,),
        'retry_kwargs': {'max_retries': 3, 'countdown': 60},
        'retry_backoff': True,
        'retry_jitter': True,
    }
    default_kwargs.update(kwargs)
    return celery_app.task(**default_kwargs)


# 任务状态回调
@celery_app.task(bind=True)
def task_success_callback(self, retval, task_id, args, kwargs):
    """任务成功回调"""
    logger.info(f"任务 {task_id} 执行成功: {retval}")


@celery_app.task(bind=True)
def task_failure_callback(self, task_id, error, traceback, args, kwargs):
    """任务失败回调"""
    logger.error(f"任务 {task_id} 执行失败: {error}")
    logger.error(f"错误堆栈: {traceback}")


# 信号处理
from celery.signals import task_prerun, task_postrun, task_failure, task_success

@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **kwds):
    """任务开始前的处理"""
    logger.info(f"任务 {task_id} 开始执行: {task.name}")


@task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, retval=None, state=None, **kwds):
    """任务结束后的处理"""
    logger.info(f"任务 {task_id} 执行完成: {state}")


@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, traceback=None, einfo=None, **kwds):
    """任务失败处理"""
    logger.error(f"任务 {task_id} 执行失败: {exception}")


@task_success.connect
def task_success_handler(sender=None, result=None, **kwds):
    """任务成功处理"""
    logger.info(f"任务执行成功: {result}")


# 工具函数
def get_task_info(task_id: str) -> Optional[Dict[str, Any]]:
    """获取任务信息"""
    try:
        result = celery_app.AsyncResult(task_id)
        return {
            'task_id': task_id,
            'status': result.status,
            'result': result.result,
            'traceback': result.traceback,
            'date_done': result.date_done,
        }
    except Exception as e:
        logger.error(f"获取任务信息失败: {e}")
        return None


def cancel_task(task_id: str) -> bool:
    """取消任务"""
    try:
        celery_app.control.revoke(task_id, terminate=True)
        return True
    except Exception as e:
        logger.error(f"取消任务失败: {e}")
        return False


def get_active_tasks() -> List[Dict[str, Any]]:
    """获取活跃任务列表"""
    try:
        inspect = celery_app.control.inspect()
        active_tasks = inspect.active()
        
        if not active_tasks:
            return []
        
        tasks = []
        for worker, task_list in active_tasks.items():
            for task in task_list:
                tasks.append({
                    'worker': worker,
                    'task_id': task['id'],
                    'name': task['name'],
                    'args': task['args'],
                    'kwargs': task['kwargs'],
                    'time_start': task.get('time_start'),
                })
        
        return tasks
    except Exception as e:
        logger.error(f"获取活跃任务失败: {e}")
        return []


def get_worker_stats() -> Dict[str, Any]:
    """获取Worker统计信息"""
    try:
        inspect = celery_app.control.inspect()
        stats = inspect.stats()
        
        if not stats:
            return {}
        
        return {
            'workers': len(stats),
            'stats': stats
        }
    except Exception as e:
        logger.error(f"获取Worker统计失败: {e}")
        return {}


# 健康检查
async def health_check() -> Dict[str, Any]:
    """Celery健康检查"""
    try:
        # 检查连接
        inspect = celery_app.control.inspect()
        stats = inspect.stats()
        
        # 检查队列
        active_queues = inspect.active_queues()
        
        # 检查活跃任务
        active_tasks = get_active_tasks()
        
        return {
            'status': 'healthy',
            'workers': len(stats) if stats else 0,
            'active_tasks': len(active_tasks),
            'queues': list(active_queues.keys()) if active_queues else [],
            'broker_url': settings.celery.broker_url,
            'backend_url': settings.celery.result_backend,
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e)
        } 