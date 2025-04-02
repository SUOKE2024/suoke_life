from functools import wraps
from flask import request, jsonify, current_app
import redis
import time
from datetime import datetime
import jwt
from loguru import logger
import os
import secrets
import hmac
import hashlib
import uuid
from prometheus_client import Counter, Histogram, Gauge

# 指标声明
AUTH_FAILURES = Counter('api_auth_failures_total', '认证失败总数', ['method', 'path', 'error_type'])
RATE_LIMIT_EXCEED = Counter('api_rate_limit_exceed_total', '速率限制超出总数', ['client_id'])
REQUEST_LATENCY = Histogram('api_request_latency_seconds', '请求延迟（秒）', ['method', 'path', 'status_code'])
ACTIVE_REQUESTS = Gauge('api_active_requests', '当前活跃请求数')

# Redis配置
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', None)
REDIS_DB = int(os.environ.get('REDIS_DB', 0))

try:
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        db=REDIS_DB,
        decode_responses=True,
        socket_timeout=3.0,
        socket_connect_timeout=3.0,
        retry_on_timeout=True
    )
    # 测试连接
    redis_client.ping()
    logger.info("Redis连接成功")
except redis.RedisError as e:
    logger.error(f"Redis连接失败: {e}")
    # 创建内存中的备用字典
    redis_client = None

class RateLimiter:
    def __init__(self, requests_per_minute=60, burst=10):
        self.requests_per_minute = requests_per_minute
        self.burst = burst
        self.window_size = 60  # 1分钟窗口
        self.enabled = True
        
        # 如果没有Redis，则使用内存字典作为回退
        self.local_counters = {}
        self.local_expiry = {}

    def is_allowed(self, client_id):
        """检查请求是否允许"""
        if not self.enabled:
            return True
            
        current = int(time.time())
        window_key = current // self.window_size
        key = f"rate_limit:{client_id}:{window_key}"
        
        # 使用Redis实现分布式速率限制
        if redis_client:
            try:
                # 使用Redis的原子操作进行计数
                pipe = redis_client.pipeline()
                pipe.incr(key)
                pipe.expire(key, self.window_size)
                count = pipe.execute()[0]
                
                # 当前时间窗口的请求数超过了限制
                if count > self.requests_per_minute:
                    # 检查是否在突发限制内
                    if count <= (self.requests_per_minute + self.burst):
                        # 允许突发请求，但记录指标
                        RATE_LIMIT_EXCEED.labels(client_id=client_id).inc()
                        return True
                    else:
                        logger.warning(f"客户端 {client_id} 超出速率限制: {count}/{self.requests_per_minute}")
                        RATE_LIMIT_EXCEED.labels(client_id=client_id).inc()
                        return False
                return True
            except redis.RedisError as e:
                logger.error(f"速率限制Redis错误: {e}")
                # 降级到本地实现
        
        # Redis不可用时的本地内存实现
        if key not in self.local_counters:
            self.local_counters[key] = 1
            self.local_expiry[key] = current + self.window_size
            return True
            
        # 清理过期的计数器
        for old_key in list(self.local_counters.keys()):
            if self.local_expiry.get(old_key, 0) < current:
                del self.local_counters[old_key]
                del self.local_expiry[old_key]
        
        # 检查本地计数
        self.local_counters[key] = self.local_counters.get(key, 0) + 1
        count = self.local_counters[key]
        
        if count > (self.requests_per_minute + self.burst):
            logger.warning(f"客户端 {client_id} 超出本地速率限制: {count}/{self.requests_per_minute}")
            RATE_LIMIT_EXCEED.labels(client_id=client_id).inc()
            return False
            
        return True
        
    def get_client_id(self, request):
        """获取客户端标识符"""
        # 首选API密钥
        api_key = request.headers.get('X-API-Key')
        if api_key:
            return f"api:{api_key}"
            
        # 其次是JWT中的用户ID
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            try:
                token = auth_header.split(' ')[1]
                payload = jwt.decode(token, algorithms=['HS256'], options={"verify_signature": False})
                if payload.get('sub'):
                    return f"user:{payload.get('sub')}"
            except:
                pass
                
        # 最后使用IP地址
        return f"ip:{request.remote_addr}"

def require_api_key(f):
    """API密钥验证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            AUTH_FAILURES.labels(
                method=request.method,
                path=request.path,
                error_type='missing_api_key'
            ).inc()
            return jsonify({'error': 'Missing API key', 'status': 'unauthorized'}), 401
        
        # 验证API密钥
        if not is_valid_api_key(api_key):
            AUTH_FAILURES.labels(
                method=request.method,
                path=request.path,
                error_type='invalid_api_key'
            ).inc()
            return jsonify({'error': 'Invalid API key', 'status': 'unauthorized'}), 401
            
        return f(*args, **kwargs)
    return decorated

def require_jwt(f):
    """JWT认证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            AUTH_FAILURES.labels(
                method=request.method,
                path=request.path,
                error_type='missing_token'
            ).inc()
            return jsonify({'error': 'Missing or invalid token', 'status': 'unauthorized'}), 401
        
        token = auth_header.split(' ')[1]
        try:
            # 从环境变量或配置获取密钥
            secret_key = os.environ.get('JWT_SECRET_KEY', current_app.config.get('JWT_SECRET_KEY', 'your-secret-key'))
            
            # 验证JWT
            payload = jwt.decode(
                token, 
                secret_key, 
                algorithms=['HS256'],
                options={'verify_exp': True}
            )
            request.user = payload
        except jwt.ExpiredSignatureError:
            AUTH_FAILURES.labels(
                method=request.method,
                path=request.path,
                error_type='token_expired'
            ).inc()
            return jsonify({'error': 'Token has expired', 'status': 'unauthorized'}), 401
        except jwt.InvalidTokenError as e:
            AUTH_FAILURES.labels(
                method=request.method,
                path=request.path,
                error_type='invalid_token'
            ).inc()
            return jsonify({'error': f'Invalid token: {str(e)}', 'status': 'unauthorized'}), 401
            
        return f(*args, **kwargs)
    return decorated

def audit_log(f):
    """审计日志装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
        start_time = time.time()
        
        # 增加活跃请求计数
        ACTIVE_REQUESTS.inc()
        
        # 记录请求信息
        logger.info(f"""
请求审计:
- 请求ID: {request_id}
- 时间: {datetime.now().isoformat()}
- 方法: {request.method}
- 路径: {request.path}
- IP: {request.remote_addr}
- 用户代理: {request.headers.get('User-Agent')}
- 内容长度: {request.headers.get('Content-Length', '0')}
- 内容类型: {request.headers.get('Content-Type', 'unknown')}
- 调用者: {request.headers.get('X-Caller-ID', 'unknown')}
""")
        
        try:
            # 执行实际请求
            response = f(*args, **kwargs)
            
            # 计算并记录指标
            duration = time.time() - start_time
            status_code = response.status_code if hasattr(response, 'status_code') else 200
            
            REQUEST_LATENCY.labels(
                method=request.method,
                path=request.path,
                status_code=status_code
            ).observe(duration)
            
            # 记录响应信息
            logger.info(f"""
响应审计:
- 请求ID: {request_id}
- 持续时间: {duration:.2f}s
- 状态码: {status_code}
- 响应大小: {response.headers.get('Content-Length', 'unknown') if hasattr(response, 'headers') else 'unknown'}
""")
            
            # 添加审计响应头
            if hasattr(response, 'headers'):
                response.headers['X-Request-ID'] = request_id
                response.headers['X-Response-Time'] = str(int(duration * 1000))
            
            return response
        finally:
            # 无论成功与否，都减少活跃请求计数
            ACTIVE_REQUESTS.dec()
            
    return decorated

def circuit_breaker(failure_threshold=5, reset_timeout=30):
    """熔断器装饰器"""
    def decorator(f):
        # 每个函数维护自己的熔断状态
        state = {
            'failures': 0,
            'open': False,
            'last_failure_time': 0
        }
        
        @wraps(f)
        def decorated(*args, **kwargs):
            # 检查熔断器是否打开
            current_time = time.time()
            if state['open']:
                # 检查是否到达重置时间
                if current_time - state['last_failure_time'] > reset_timeout:
                    logger.info(f"熔断器半开: {f.__name__}")
                    state['open'] = False
                    state['failures'] = 0
                else:
                    logger.warning(f"熔断器开启，快速失败: {f.__name__}")
                    return jsonify({
                        'error': 'Service temporarily unavailable',
                        'status': 'circuit_open'
                    }), 503
            
            try:
                # 尝试执行实际函数
                result = f(*args, **kwargs)
                
                # 成功执行，重置失败计数
                if state['failures'] > 0:
                    logger.info(f"熔断器重置: {f.__name__}")
                    state['failures'] = 0
                    
                return result
            except Exception as e:
                # 记录失败并更新状态
                state['failures'] += 1
                state['last_failure_time'] = current_time
                
                if state['failures'] >= failure_threshold:
                    logger.error(f"熔断器触发: {f.__name__}, 失败次数: {state['failures']}")
                    state['open'] = True
                
                # 重新抛出原始异常
                raise
                
        return decorated
    return decorator

def is_valid_api_key(api_key):
    """验证API密钥"""
    # 从环境变量或配置获取有效的API密钥列表
    valid_keys = os.environ.get('VALID_API_KEYS', '').split(',')
    
    # 也可以从当前应用配置获取
    if hasattr(current_app, 'config'):
        app_keys = current_app.config.get('VALID_API_KEYS', [])
        if isinstance(app_keys, list):
            valid_keys.extend(app_keys)
    
    # 开发环境下的默认密钥
    if os.environ.get('FLASK_ENV') == 'development' and not valid_keys:
        valid_keys = ['dev-key-123']
    
    # 进行哈希比较以防止时序攻击
    for valid_key in valid_keys:
        if valid_key and hmac.compare_digest(api_key, valid_key):
            return True
    
    return False

def generate_api_key():
    """生成安全的API密钥"""
    return secrets.token_hex(32)

# 实例化速率限制器
rate_limiter = RateLimiter(
    requests_per_minute=int(os.environ.get('RATE_LIMIT_RPM', 60)),
    burst=int(os.environ.get('RATE_LIMIT_BURST', 10))
) 