#!/usr/bin/env python3
"""
索克生活无障碍服务 - Web监控仪表板

提供现代化的Web界面用于实时监控服务状态、性能指标和告警信息。
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

logger = logging.getLogger(__name__)


class WebDashboardService:
    """Web监控仪表板服务"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化Web仪表板服务

        Args:
            config: 配置字典
        """
        self.config = config
        self.app = FastAPI(
            title="索克生活无障碍服务监控仪表板",
            description="实时监控服务状态、性能指标和告警信息",
            version="2.0.0",
        )

        # WebSocket连接管理
        self.active_connections: List[WebSocket] = []

        # 数据存储
        self.metrics_history: List[Dict[str, Any]] = []
        self.alerts_history: List[Dict[str, Any]] = []
        self.health_status: Dict[str, Any] = {}

        # 服务引用
        self.health_manager = None
        self.performance_monitor = None
        self.alert_manager = None

        # 设置模板和静态文件
        self.setup_templates()
        self.setup_routes()

        logger.info("Web仪表板服务初始化完成")

    def setup_templates(self) -> None:
        """设置模板引擎"""
        # 创建模板目录
        template_dir = Path(__file__).parent / "templates"
        template_dir.mkdir(exist_ok=True)

        static_dir = Path(__file__).parent / "static"
        static_dir.mkdir(exist_ok=True)

        self.templates = Jinja2Templates(directory=str(template_dir))

        # 挂载静态文件
        self.app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    def setup_routes(self) -> None:
        """设置路由"""

        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard_home(request: Request):
            """仪表板首页"""
            return self.templates.TemplateResponse(
                "dashboard.html",
                {"request": request, "title": "索克生活无障碍服务监控"},
            )

        @self.app.get("/api/health")
        async def get_health_status() -> None:
            """获取健康状态"""
            if self.health_manager:
                try:
                    health_result = await self.health_manager.check_health()
                    return {
                        "status": (
                            "healthy" if health_result.overall_healthy else "unhealthy"
                        ),
                        "timestamp": datetime.now().isoformat(),
                        "checks": [
                            {
                                "name": check.name,
                                "status": "pass" if check.healthy else "fail",
                                "message": check.message,
                                "duration": check.duration,
                            }
                            for check in health_result.checks
                        ],
                        "summary": {
                            "total_checks": len(health_result.checks),
                            "passed_checks": sum(
                                1 for c in health_result.checks if c.healthy
                            ),
                            "total_duration": health_result.total_duration,
                        },
                    }
                except Exception as e:
                    logger.error(f"健康检查失败: {e}")
                    return {"status": "error", "message": str(e)}

            return {"status": "unavailable", "message": "健康管理器未初始化"}

        @self.app.get("/api/metrics")
        async def get_metrics() -> None:
            """获取性能指标"""
            if self.performance_monitor:
                try:
                    metrics = await self.performance_monitor.get_current_metrics()
                    return {
                        "timestamp": datetime.now().isoformat(),
                        "metrics": metrics,
                        "history": self.metrics_history[-100:],  # 最近100个数据点
                    }
                except Exception as e:
                    logger.error(f"获取指标失败: {e}")
                    return {"error": str(e)}

            return {"error": "性能监控器未初始化"}

        @self.app.get("/api/alerts")
        async def get_alerts() -> None:
            """获取告警信息"""
            if self.alert_manager:
                try:
                    active_alerts = await self.alert_manager.get_active_alerts()
                    return {
                        "timestamp": datetime.now().isoformat(),
                        "active_alerts": active_alerts,
                        "history": self.alerts_history[-50:],  # 最近50个告警
                    }
                except Exception as e:
                    logger.error(f"获取告警失败: {e}")
                    return {"error": str(e)}

            return {"error": "告警管理器未初始化"}

        @self.app.get("/api/system-info")
        async def get_system_info() -> None:
            """获取系统信息"""
            import platform

            import psutil

            try:
                return {
                    "timestamp": datetime.now().isoformat(),
                    "system": {
                        "platform": platform.system(),
                        "platform_version": platform.version(),
                        "architecture": platform.architecture()[0],
                        "processor": platform.processor(),
                        "python_version": platform.python_version(),
                    },
                    "resources": {
                        "cpu_percent": psutil.cpu_percent(interval=1),
                        "memory": {
                            "total": psutil.virtual_memory().total,
                            "available": psutil.virtual_memory().available,
                            "percent": psutil.virtual_memory().percent,
                        },
                        "disk": {
                            "total": psutil.disk_usage("/").total,
                            "free": psutil.disk_usage("/").free,
                            "percent": psutil.disk_usage("/").percent,
                        },
                    },
                }
            except Exception as e:
                logger.error(f"获取系统信息失败: {e}")
                return {"error": str(e)}

        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket端点，用于实时数据推送"""
            await self.connect(websocket)
            try:
                while True:
                    # 保持连接活跃
                    await websocket.receive_text()
            except WebSocketDisconnect:
                self.disconnect(websocket)

    async def connect(self, websocket: WebSocket):
        """接受WebSocket连接"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket连接已建立，当前连接数: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """断开WebSocket连接"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket连接已断开，当前连接数: {len(self.active_connections)}")

    async def broadcast_data(self, data: Dict[str, Any]):
        """向所有连接的客户端广播数据"""
        if not self.active_connections:
            return

        message = json.dumps(data)
        disconnected = []

        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.warning(f"发送WebSocket消息失败: {e}")
                disconnected.append(connection)

        # 清理断开的连接
        for connection in disconnected:
            self.disconnect(connection)

    def set_health_manager(self, health_manager):
        """设置健康管理器"""
        self.health_manager = health_manager
        logger.info("健康管理器已设置")

    def set_performance_monitor(self, performance_monitor):
        """设置性能监控器"""
        self.performance_monitor = performance_monitor
        logger.info("性能监控器已设置")

    def set_alert_manager(self, alert_manager):
        """设置告警管理器"""
        self.alert_manager = alert_manager
        logger.info("告警管理器已设置")

    async def start_data_collection(self) -> None:
        """启动数据收集任务"""
        logger.info("启动实时数据收集")

        async def collect_and_broadcast() -> None:
            while True:
                try:
                    # 收集健康状态
                    if self.health_manager:
                        health_data = await self.health_manager.check_health()
                        self.health_status = {
                            "timestamp": datetime.now().isoformat(),
                            "overall_healthy": health_data.overall_healthy,
                            "total_duration": health_data.total_duration,
                            "checks_count": len(health_data.checks),
                            "passed_count": sum(
                                1 for c in health_data.checks if c.healthy
                            ),
                        }

                    # 收集性能指标
                    if self.performance_monitor:
                        metrics = await self.performance_monitor.get_current_metrics()
                        metric_data = {
                            "timestamp": datetime.now().isoformat(),
                            "metrics": metrics,
                        }
                        self.metrics_history.append(metric_data)

                        # 保持历史数据在合理范围内
                        if len(self.metrics_history) > 1000:
                            self.metrics_history = self.metrics_history[-500:]

                    # 收集告警信息
                    if self.alert_manager:
                        alerts = await self.alert_manager.get_active_alerts()
                        if alerts:
                            alert_data = {
                                "timestamp": datetime.now().isoformat(),
                                "alerts": alerts,
                            }
                            self.alerts_history.append(alert_data)

                            # 保持告警历史在合理范围内
                            if len(self.alerts_history) > 200:
                                self.alerts_history = self.alerts_history[-100:]

                    # 广播实时数据
                    await self.broadcast_data(
                        {
                            "type": "realtime_update",
                            "health": self.health_status,
                            "metrics": (
                                self.metrics_history[-1]
                                if self.metrics_history
                                else None
                            ),
                            "alerts": (
                                self.alerts_history[-1] if self.alerts_history else None
                            ),
                        }
                    )

                except Exception as e:
                    logger.error(f"数据收集失败: {e}")

                # 每5秒收集一次数据
                await asyncio.sleep(5)

        # 启动后台任务
        asyncio.create_task(collect_and_broadcast())

    async def create_dashboard_template(self) -> None:
        """创建仪表板HTML模板"""
        template_content = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .card {
            @apply bg-white rounded-lg shadow-md p-6 mb-6;
        }
        .metric-card {
            @apply bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg p-4;
        }
        .status-healthy { @apply text-green-600; }
        .status-unhealthy { @apply text-red-600; }
        .status-warning { @apply text-yellow-600; }
    </style>
</head>
<body class="bg-gray-100">
    <div class="container mx-auto px-4 py-8">
        <!-- 头部 -->
        <header class="mb-8">
            <h1 class="text-3xl font-bold text-gray-800">{{ title }}</h1>
            <p class="text-gray-600 mt-2">实时监控服务状态和性能指标</p>
        </header>

        <!-- 状态概览 -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div class="metric-card">
                <h3 class="text-lg font-semibold mb-2">服务状态</h3>
                <div id="service-status" class="text-2xl font-bold">检查中...</div>
            </div>
            <div class="metric-card">
                <h3 class="text-lg font-semibold mb-2">健康检查</h3>
                <div id="health-checks" class="text-2xl font-bold">-/-</div>
            </div>
            <div class="metric-card">
                <h3 class="text-lg font-semibold mb-2">活跃告警</h3>
                <div id="active-alerts" class="text-2xl font-bold">0</div>
            </div>
            <div class="metric-card">
                <h3 class="text-lg font-semibold mb-2">响应时间</h3>
                <div id="response-time" class="text-2xl font-bold">-ms</div>
            </div>
        </div>

        <!-- 图表区域 -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <div class="card">
                <h3 class="text-xl font-semibold mb-4">性能指标趋势</h3>
                <canvas id="metricsChart" width="400" height="200"></canvas>
            </div>
            <div class="card">
                <h3 class="text-xl font-semibold mb-4">系统资源使用</h3>
                <canvas id="resourceChart" width="400" height="200"></canvas>
            </div>
        </div>

        <!-- 健康检查详情 -->
        <div class="card">
            <h3 class="text-xl font-semibold mb-4">健康检查详情</h3>
            <div id="health-details" class="space-y-2">
                <p class="text-gray-500">正在加载健康检查信息...</p>
            </div>
        </div>

        <!-- 告警历史 -->
        <div class="card">
            <h3 class="text-xl font-semibold mb-4">最近告警</h3>
            <div id="alerts-list" class="space-y-2">
                <p class="text-gray-500">正在加载告警信息...</p>
            </div>
        </div>
    </div>

    <script>
        // WebSocket连接
        const ws = new WebSocket(`ws://${window.location.host}/ws`);
        
        // 图表初始化
        const metricsCtx = document.getElementById('metricsChart').getContext('2d');
        const resourceCtx = document.getElementById('resourceChart').getContext('2d');
        
        const metricsChart = new Chart(metricsCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'CPU使用率',
                    data: [],
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                }, {
                    label: '内存使用率',
                    data: [],
                    borderColor: 'rgb(255, 99, 132)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });

        const resourceChart = new Chart(resourceCtx, {
            type: 'doughnut',
            data: {
                labels: ['已使用', '可用'],
                datasets: [{
                    data: [0, 100],
                    backgroundColor: ['#FF6384', '#36A2EB']
                }]
            },
            options: {
                responsive: true
            }
        });

        // WebSocket消息处理
        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            
            if (data.type === 'realtime_update') {
                updateDashboard(data);
            }
        };

        // 更新仪表板
        function updateDashboard(data) {
            // 更新状态卡片
            if (data.health) {
                document.getElementById('service-status').textContent = 
                    data.health.overall_healthy ? '正常' : '异常';
                document.getElementById('health-checks').textContent = 
                    `${data.health.passed_count}/${data.health.checks_count}`;
                document.getElementById('response-time').textContent = 
                    `${Math.round(data.health.total_duration * 1000)}ms`;
            }

            // 更新图表
            if (data.metrics && data.metrics.metrics) {
                const time = new Date(data.metrics.timestamp).toLocaleTimeString();
                const metrics = data.metrics.metrics;
                
                // 添加新数据点
                metricsChart.data.labels.push(time);
                metricsChart.data.datasets[0].data.push(metrics.cpu_percent || 0);
                metricsChart.data.datasets[1].data.push(metrics.memory_percent || 0);
                
                // 保持最近20个数据点
                if (metricsChart.data.labels.length > 20) {
                    metricsChart.data.labels.shift();
                    metricsChart.data.datasets[0].data.shift();
                    metricsChart.data.datasets[1].data.shift();
                }
                
                metricsChart.update();
            }
        }

        // 定期获取数据
        async function fetchData() {
            try {
                // 获取健康状态
                const healthResponse = await fetch('/api/health');
                const healthData = await healthResponse.json();
                updateHealthDetails(healthData);

                // 获取告警信息
                const alertsResponse = await fetch('/api/alerts');
                const alertsData = await alertsResponse.json();
                updateAlertsList(alertsData);

                // 获取系统信息
                const systemResponse = await fetch('/api/system-info');
                const systemData = await systemResponse.json();
                updateResourceChart(systemData);

            } catch (error) {
                console.error('获取数据失败:', error);
            }
        }

        function updateHealthDetails(data) {
            const container = document.getElementById('health-details');
            if (data.checks) {
                container.innerHTML = data.checks.map(check => `
                    <div class="flex justify-between items-center p-3 bg-gray-50 rounded">
                        <span class="font-medium">${check.name}</span>
                        <span class="status-${check.status === 'pass' ? 'healthy' : 'unhealthy'}">
                            ${check.status === 'pass' ? '✓' : '✗'} ${check.message}
                        </span>
                    </div>
                `).join('');
            }
        }

        function updateAlertsList(data) {
            const container = document.getElementById('alerts-list');
            if (data.active_alerts && data.active_alerts.length > 0) {
                document.getElementById('active-alerts').textContent = data.active_alerts.length;
                container.innerHTML = data.active_alerts.map(alert => `
                    <div class="p-3 bg-red-50 border-l-4 border-red-500 rounded">
                        <div class="font-medium text-red-800">${alert.rule_name}</div>
                        <div class="text-red-600 text-sm">${alert.message}</div>
                        <div class="text-gray-500 text-xs">${new Date(alert.timestamp).toLocaleString()}</div>
                    </div>
                `).join('');
            } else {
                document.getElementById('active-alerts').textContent = '0';
                container.innerHTML = '<p class="text-green-600">暂无活跃告警</p>';
            }
        }

        function updateResourceChart(data) {
            if (data.resources && data.resources.memory) {
                const used = data.resources.memory.percent;
                const free = 100 - used;
                resourceChart.data.datasets[0].data = [used, free];
                resourceChart.update();
            }
        }

        // 初始化
        fetchData();
        setInterval(fetchData, 10000); // 每10秒更新一次
    </script>
</body>
</html>"""

        # 保存模板文件
        template_dir = Path(__file__).parent / "templates"
        template_dir.mkdir(exist_ok=True)

        template_file = template_dir / "dashboard.html"
        with open(template_file, "w", encoding="utf-8") as f:
            f.write(template_content)

        logger.info(f"仪表板模板已创建: {template_file}")

    async def initialize(self) -> None:
        """初始化仪表板"""
        await self.create_dashboard_template()
        await self.start_data_collection()
        logger.info("Web仪表板服务初始化完成")


# 全局仪表板实例
web_dashboard = None


def get_web_dashboard(config: Dict[str, Any] = None) -> WebDashboardService:
    """获取Web仪表板实例"""
    global web_dashboard
    if web_dashboard is None:
        web_dashboard = WebDashboardService(config or {})
    return web_dashboard


async def start_web_dashboard(
    host: str = "0.0.0.0", port: int = 8080, config: Dict[str, Any] = None
):
    """启动Web仪表板服务"""
    import uvicorn

    dashboard = get_web_dashboard(config)
    await dashboard.initialize()

    logger.info(f"启动Web仪表板服务: http://{host}:{port}")

    config = uvicorn.Config(dashboard.app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(start_web_dashboard())
