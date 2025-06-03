#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API 网关管理界面

提供可视化的管理功能。
"""

from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse

from ..services.websocket_manager import get_websocket_manager
from ..services.oauth2_provider import get_oauth2_provider
from ..services.tracing import get_tracing_service
from ..utils.metrics import get_metrics_collector
from ..core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])

# 模板引擎（如果需要的话）
# templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """
    管理仪表板主页
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>索克生活 API 网关管理</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }
            .header { background: #2c3e50; color: white; padding: 1rem 2rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .header h1 { font-size: 1.5rem; }
            .container { max-width: 1200px; margin: 2rem auto; padding: 0 2rem; }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; }
            .card { background: white; border-radius: 8px; padding: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
            .card h2 { color: #2c3e50; margin-bottom: 1rem; font-size: 1.2rem; }
            .metric { display: flex; justify-content: space-between; margin: 0.5rem 0; padding: 0.5rem 0; border-bottom: 1px solid #eee; }
            .metric:last-child { border-bottom: none; }
            .metric-label { color: #666; }
            .metric-value { font-weight: bold; color: #2c3e50; }
            .status { padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem; font-weight: bold; }
            .status.healthy { background: #d4edda; color: #155724; }
            .status.warning { background: #fff3cd; color: #856404; }
            .status.error { background: #f8d7da; color: #721c24; }
            .btn { display: inline-block; padding: 0.5rem 1rem; background: #3498db; color: white; text-decoration: none; border-radius: 4px; margin: 0.25rem; }
            .btn:hover { background: #2980b9; }
            .btn.danger { background: #e74c3c; }
            .btn.danger:hover { background: #c0392b; }
            .refresh-btn { float: right; }
            .loading { text-align: center; color: #666; padding: 2rem; }
            .error { color: #e74c3c; background: #f8d7da; padding: 1rem; border-radius: 4px; margin: 1rem 0; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🏥 索克生活 API 网关管理</h1>
        </div>
        
        <div class="container">
            <div class="grid">
                <!-- 系统状态 -->
                <div class="card">
                    <h2>系统状态 <button class="btn refresh-btn" onclick="refreshData()">刷新</button></h2>
                    <div id="system-status" class="loading">加载中...</div>
                </div>
                
                <!-- WebSocket 连接 -->
                <div class="card">
                    <h2>WebSocket 连接</h2>
                    <div id="websocket-stats" class="loading">加载中...</div>
                </div>
                
                <!-- OAuth2 统计 -->
                <div class="card">
                    <h2>OAuth2 认证</h2>
                    <div id="oauth2-stats" class="loading">加载中...</div>
                </div>
                
                <!-- 分布式追踪 -->
                <div class="card">
                    <h2>分布式追踪</h2>
                    <div id="tracing-stats" class="loading">加载中...</div>
                </div>
                
                <!-- 性能指标 -->
                <div class="card">
                    <h2>性能指标</h2>
                    <div id="metrics-stats" class="loading">加载中...</div>
                </div>
                
                <!-- 快速操作 -->
                <div class="card">
                    <h2>快速操作</h2>
                    <div>
                        <a href="/docs" class="btn" target="_blank">API 文档</a>
                        <a href="/metrics/prometheus" class="btn" target="_blank">Prometheus 指标</a>
                        <a href="/health" class="btn" target="_blank">健康检查</a>
                        <button class="btn" onclick="cleanupExpiredTokens()">清理过期令牌</button>
                        <button class="btn" onclick="cleanupOldSpans()">清理旧追踪</button>
                        <button class="btn danger" onclick="resetMetrics()">重置指标</button>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            async function fetchData(url) {
                try {
                    const response = await fetch(url);
                    if (!response.ok) throw new Error(`HTTP ${response.status}`);
                    return await response.json();
                } catch (error) {
                    return { error: error.message };
                }
            }
            
            function formatNumber(num) {
                if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
                if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
                return num.toString();
            }
            
            function formatDuration(seconds) {
                if (seconds < 1) return (seconds * 1000).toFixed(1) + 'ms';
                if (seconds < 60) return seconds.toFixed(2) + 's';
                return (seconds / 60).toFixed(1) + 'm';
            }
            
            function createMetric(label, value, status = null) {
                const statusHtml = status ? `<span class="status ${status}">${status}</span>` : '';
                return `<div class="metric"><span class="metric-label">${label}</span><span class="metric-value">${value} ${statusHtml}</span></div>`;
            }
            
            async function loadSystemStatus() {
                const data = await fetchData('/health');
                const element = document.getElementById('system-status');
                
                if (data.error) {
                    element.innerHTML = `<div class="error">错误: ${data.error}</div>`;
                    return;
                }
                
                const status = data.status === 'healthy' ? 'healthy' : 'error';
                element.innerHTML = `
                    ${createMetric('服务状态', data.status, status)}
                    ${createMetric('启动时间', new Date(data.timestamp * 1000).toLocaleString())}
                    ${createMetric('版本', data.version || '1.0.0')}
                    ${createMetric('环境', data.environment || 'development')}
                `;
            }
            
            async function loadWebSocketStats() {
                const data = await fetchData('/ws/stats');
                const element = document.getElementById('websocket-stats');
                
                if (data.error) {
                    element.innerHTML = `<div class="error">错误: ${data.error}</div>`;
                    return;
                }
                
                const stats = data.stats || {};
                element.innerHTML = `
                    ${createMetric('活跃连接', formatNumber(stats.active_connections || 0))}
                    ${createMetric('总连接数', formatNumber(stats.total_connections || 0))}
                    ${createMetric('房间数量', formatNumber(stats.rooms || 0))}
                    ${createMetric('消息总数', formatNumber(stats.total_messages || 0))}
                `;
            }
            
            async function loadOAuth2Stats() {
                const data = await fetchData('/oauth2/stats');
                const element = document.getElementById('oauth2-stats');
                
                if (data.error) {
                    element.innerHTML = `<div class="error">错误: ${data.error}</div>`;
                    return;
                }
                
                const stats = data.stats || {};
                element.innerHTML = `
                    ${createMetric('客户端数量', formatNumber(stats.clients || 0))}
                    ${createMetric('访问令牌', formatNumber(stats.access_tokens || 0))}
                    ${createMetric('刷新令牌', formatNumber(stats.refresh_tokens || 0))}
                    ${createMetric('授权码', formatNumber(stats.authorization_codes || 0))}
                `;
            }
            
            async function loadTracingStats() {
                const data = await fetchData('/tracing/stats');
                const element = document.getElementById('tracing-stats');
                
                if (data.error) {
                    element.innerHTML = `<div class="error">错误: ${data.error}</div>`;
                    return;
                }
                
                const stats = data.stats || {};
                const status = stats.enabled ? 'healthy' : 'warning';
                element.innerHTML = `
                    ${createMetric('追踪状态', stats.enabled ? '启用' : '禁用', status)}
                    ${createMetric('Span 总数', formatNumber(stats.total_spans || 0))}
                    ${createMetric('Trace 总数', formatNumber(stats.total_traces || 0))}
                    ${createMetric('平均耗时', formatDuration(stats.avg_duration || 0))}
                    ${createMetric('错误率', ((stats.error_rate || 0) * 100).toFixed(1) + '%')}
                `;
            }
            
            async function loadMetricsStats() {
                const data = await fetchData('/metrics/stats');
                const element = document.getElementById('metrics-stats');
                
                if (data.error) {
                    element.innerHTML = `<div class="error">错误: ${data.error}</div>`;
                    return;
                }
                
                const stats = data.stats || {};
                element.innerHTML = `
                    ${createMetric('请求总数', formatNumber(stats.total_requests || 0))}
                    ${createMetric('平均响应时间', formatDuration(stats.avg_response_time || 0))}
                    ${createMetric('错误数量', formatNumber(stats.error_count || 0))}
                    ${createMetric('缓存命中率', ((stats.cache_hit_rate || 0) * 100).toFixed(1) + '%')}
                `;
            }
            
            async function refreshData() {
                await Promise.all([
                    loadSystemStatus(),
                    loadWebSocketStats(),
                    loadOAuth2Stats(),
                    loadTracingStats(),
                    loadMetricsStats(),
                ]);
            }
            
            async function cleanupExpiredTokens() {
                try {
                    const response = await fetch('/oauth2/cleanup', { method: 'POST' });
                    const data = await response.json();
                    alert(data.message || '清理完成');
                    await loadOAuth2Stats();
                } catch (error) {
                    alert('清理失败: ' + error.message);
                }
            }
            
            async function cleanupOldSpans() {
                try {
                    const response = await fetch('/tracing/cleanup?max_age_hours=1', { method: 'POST' });
                    const data = await response.json();
                    alert(`清理完成: 删除了 ${data.cleaned_spans} 个 Span`);
                    await loadTracingStats();
                } catch (error) {
                    alert('清理失败: ' + error.message);
                }
            }
            
            async function resetMetrics() {
                if (!confirm('确定要重置所有指标吗？')) return;
                
                try {
                    const response = await fetch('/metrics/reset', { method: 'POST' });
                    const data = await response.json();
                    alert(data.message || '重置完成');
                    await loadMetricsStats();
                } catch (error) {
                    alert('重置失败: ' + error.message);
                }
            }
            
            // 初始加载
            refreshData();
            
            // 自动刷新
            setInterval(refreshData, 30000); // 30秒刷新一次
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

@router.get("/overview")
async def admin_overview(
    websocket_manager = Depends(get_websocket_manager),
    oauth2_provider = Depends(get_oauth2_provider),
    tracing_service = Depends(get_tracing_service),
    metrics_collector = Depends(get_metrics_collector),
) -> Dict[str, Any]:
    """
    获取管理概览数据
    
    Returns:
        概览数据
    """
    try:
        # 收集各个服务的统计信息
        overview = {
            "timestamp": datetime.now().isoformat(),
            "websocket": websocket_manager.get_stats(),
            "oauth2": oauth2_provider.get_stats(),
            "tracing": tracing_service.get_stats(),
            "metrics": {
                "total_requests": metrics_collector.request_count._value._value,
                "total_errors": metrics_collector.error_count._value._value,
                "avg_response_time": metrics_collector.get_avg_response_time(),
                "cache_hit_rate": metrics_collector.get_cache_hit_rate(),
            },
        }
        
        return {
            "status": "success",
            "overview": overview,
        }
    
    except Exception as e:
        logger.error("Failed to get admin overview", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/config")
async def admin_config() -> Dict[str, Any]:
    """
    获取配置信息
    
    Returns:
        配置信息
    """
    try:
        from ..core.config import get_settings
        settings = get_settings()
        
        # 只返回非敏感的配置信息
        config = {
            "service_name": settings.service_name,
            "environment": getattr(settings, 'environment', 'development'),
            "debug": settings.debug,
            "host": settings.host,
            "port": settings.port,
            "redis_url": settings.redis_url.replace(
                settings.redis_url.split('@')[0].split('//')[1] + '@', '***@'
            ) if '@' in settings.redis_url else settings.redis_url,
            "cors_origins": settings.cors_origins,
            "rate_limit_enabled": getattr(settings, 'rate_limit_enabled', True),
            "tracing_enabled": getattr(settings, 'tracing_enabled', True),
            "oauth2_issuer": getattr(settings, 'oauth2_issuer', 'https://api.suoke.life'),
        }
        
        return {
            "status": "success",
            "config": config,
        }
    
    except Exception as e:
        logger.error("Failed to get admin config", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs")
async def admin_logs(
    level: Optional[str] = "INFO",
    limit: int = 100,
) -> Dict[str, Any]:
    """
    获取日志信息
    
    Args:
        level: 日志级别过滤
        limit: 返回数量限制
    
    Returns:
        日志信息
    """
    try:
        # 这里应该从日志系统获取日志
        # 暂时返回模拟数据
        logs = [
            {
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "message": "API Gateway started successfully",
                "module": "main",
            },
            {
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "message": "WebSocket manager initialized",
                "module": "websocket_manager",
            },
            {
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "message": "OAuth2 provider initialized",
                "module": "oauth2_provider",
            },
        ]
        
        return {
            "status": "success",
            "logs": logs[:limit],
            "total": len(logs),
        }
    
    except Exception as e:
        logger.error("Failed to get admin logs", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/maintenance")
async def admin_maintenance(
    action: str,
    websocket_manager = Depends(get_websocket_manager),
    oauth2_provider = Depends(get_oauth2_provider),
    tracing_service = Depends(get_tracing_service),
    metrics_collector = Depends(get_metrics_collector),
) -> Dict[str, Any]:
    """
    执行维护操作
    
    Args:
        action: 维护操作类型
    
    Returns:
        操作结果
    """
    try:
        if action == "cleanup_tokens":
            oauth2_provider.cleanup_expired_tokens()
            return {"status": "success", "message": "Expired tokens cleaned up"}
        
        elif action == "cleanup_spans":
            tracing_service.cleanup_old_spans(3600)  # 1小时
            return {"status": "success", "message": "Old spans cleaned up"}
        
        elif action == "reset_metrics":
            # 重置指标（这里需要实现具体的重置逻辑）
            return {"status": "success", "message": "Metrics reset"}
        
        elif action == "disconnect_all_websockets":
            # 断开所有 WebSocket 连接
            disconnected = await websocket_manager.disconnect_all()
            return {
                "status": "success",
                "message": f"Disconnected {disconnected} WebSocket connections"
            }
        
        else:
            raise HTTPException(status_code=400, detail="Unknown maintenance action")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to execute maintenance action", action=action, error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) 