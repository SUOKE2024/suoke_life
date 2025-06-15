"""
监控仪表板UI
提供Web界面展示系统健康状态、性能指标和告警信息
"""

import asyncio
import json
import logging
import time
from dataclasses import asdict, dataclass
from datetime import timedelta
from typing import Any

import aiohttp_cors
import jinja2

# Web框架
from aiohttp import WSMsgType, web
from aiohttp.web import Application, Request, Response, WebSocketResponse

# 内部模块
from .optimized_health_check import optimized_health_manager
from .optimized_performance_monitor import optimized_performance_collector
from .performance_alerting import performance_alert_manager


@dataclass
class DashboardData:
    """仪表板数据"""

    timestamp: float
    health_status: dict[str, Any]
    performance_metrics: dict[str, Any]
    active_alerts: list[dict[str, Any]]
    system_info: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return asdict(self)


class DashboardWebSocket:
    """仪表板WebSocket连接管理"""

    def __init__(self):
        self.connections: list[WebSocketResponse] = []
        self.logger = logging.getLogger("dashboard_websocket")

    async def add_connection(self, ws: WebSocketResponse):
        """添加WebSocket连接"""
        self.connections.append(ws)
        self.logger.info(f"新的WebSocket连接，当前连接数: {len(self.connections)}")

    async def remove_connection(self, ws: WebSocketResponse):
        """移除WebSocket连接"""
        if ws in self.connections:
            self.connections.remove(ws)
            self.logger.info(f"WebSocket连接断开，当前连接数: {len(self.connections)}")

    async def broadcast(self, data: dict[str, Any]):
        """广播数据到所有连接"""
        if not self.connections:
            return

        message = json.dumps(data, ensure_ascii=False)
        disconnected = []

        for ws in self.connections:
            try:
                await ws.send_str(message)
            except Exception as e:
                self.logger.error(f"发送WebSocket消息失败: {e}")
                disconnected.append(ws)

        # 清理断开的连接
        for ws in disconnected:
            await self.remove_connection(ws)


class DashboardServer:
    """仪表板服务器"""

    def __init__(self, host: str = "0.0.0.0", port: int = 8080):
        self.host = host
        self.port = port
        self.app: Application | None = None
        self.websocket_manager = DashboardWebSocket()
        self.logger = logging.getLogger("dashboard_server")

        # 数据更新间隔
        self.update_interval = 2.0
        self.running = False

        # 模板引擎
        self.jinja_env = jinja2.Environment(
            loader=jinja2.DictLoader(self._get_templates()),
            autoescape=jinja2.select_autoescape(["html", "xml"]),
        )

    def _get_templates(self) -> dict[str, str]:
        """获取HTML模板"""
        return {
            "dashboard.html": """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>索克生活 - 无障碍服务监控仪表板</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }

        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }

        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }

        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s ease;
        }

        .card:hover {
            transform: translateY(-2px);
        }

        .card-title {
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 15px;
            color: #2d3748;
        }

        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }

        .status-healthy { background-color: #48bb78; }
        .status-warning { background-color: #ed8936; }
        .status-error { background-color: #f56565; }
        .status-unknown { background-color: #a0aec0; }

        .metric-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid #e2e8f0;
        }

        .metric-item:last-child {
            border-bottom: none;
        }

        .metric-label {
            font-weight: 500;
            color: #4a5568;
        }

        .metric-value {
            font-weight: 600;
            color: #2d3748;
        }

        .alert-item {
            background: #fed7d7;
            border: 1px solid #feb2b2;
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 10px;
        }

        .alert-item:last-child {
            margin-bottom: 0;
        }

        .alert-title {
            font-weight: 600;
            color: #c53030;
            margin-bottom: 4px;
        }

        .alert-message {
            color: #742a2a;
            font-size: 0.9rem;
        }

        .connection-status {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 500;
        }

        .connected {
            background: #c6f6d5;
            color: #22543d;
        }

        .disconnected {
            background: #fed7d7;
            color: #c53030;
        }

        .last-update {
            text-align: center;
            color: white;
            opacity: 0.8;
            font-size: 0.9rem;
        }

        @media (max-width: 768px) {
            .dashboard-grid {
                grid-template-columns: 1fr;
            }

            .header h1 {
                font-size: 2rem;
            }
        }
    </style>
</head>
<body>
    <div class="connection-status" id="connectionStatus">连接中...</div>

    <div class="container">
        <div class="header">
            <h1>🏥 索克生活无障碍服务</h1>
            <p>实时监控仪表板</p>
        </div>

        <div class="dashboard-grid">
            <!-- 系统健康状态 -->
            <div class="card">
                <div class="card-title">🏥 系统健康状态</div>
                <div id="healthStatus">
                    <div class="metric-item">
                        <span class="metric-label">整体状态</span>
                        <span class="metric-value">
                            <span class="status-indicator status-unknown"></span>
                            加载中...
                        </span>
                    </div>
                </div>
            </div>

            <!-- 性能指标 -->
            <div class="card">
                <div class="card-title">📊 性能指标</div>
                <div id="performanceMetrics">
                    <div class="metric-item">
                        <span class="metric-label">CPU使用率</span>
                        <span class="metric-value">--%</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">内存使用率</span>
                        <span class="metric-value">--%</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">磁盘使用率</span>
                        <span class="metric-value">--%</span>
                    </div>
                </div>
            </div>

            <!-- 活跃告警 -->
            <div class="card">
                <div class="card-title">⚠️ 活跃告警</div>
                <div id="activeAlerts">
                    <p style="color: #a0aec0; text-align: center;">暂无告警</p>
                </div>
            </div>

            <!-- 系统信息 -->
            <div class="card">
                <div class="card-title">ℹ️ 系统信息</div>
                <div id="systemInfo">
                    <div class="metric-item">
                        <span class="metric-label">服务版本</span>
                        <span class="metric-value">v1.0.0</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">运行时间</span>
                        <span class="metric-value">--</span>
                    </div>
                </div>
            </div>
        </div>

        <div class="last-update" id="lastUpdate">
            最后更新: --
        </div>
    </div>

    <script>
        class DashboardClient {
            constructor() {
                this.ws = null;
                this.reconnectInterval = 5000;
                this.maxReconnectAttempts = 10;
                this.reconnectAttempts = 0;

                this.connect();
            }

            connect() {
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                const wsUrl = `${protocol}//${window.location.host}/ws`;

                this.ws = new WebSocket(wsUrl);

                this.ws.onopen = () => {
                    console.log('WebSocket连接已建立');
                    this.updateConnectionStatus(true);
                    this.reconnectAttempts = 0;
                };

                this.ws.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);
                        this.updateDashboard(data);
                    } catch (error) {
                        console.error('解析WebSocket消息失败:', error);
                    }
                };

                this.ws.onclose = () => {
                    console.log('WebSocket连接已断开');
                    this.updateConnectionStatus(false);
                    this.scheduleReconnect();
                };

                this.ws.onerror = (error) => {
                    console.error('WebSocket错误:', error);
                };
            }

            scheduleReconnect() {
                if (this.reconnectAttempts < this.maxReconnectAttempts) {
                    this.reconnectAttempts++;
                    setTimeout(() => {
                        console.log(`尝试重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
                        this.connect();
                    }, this.reconnectInterval);
                }
            }

            updateConnectionStatus(connected) {
                const statusEl = document.getElementById('connectionStatus');
                if (connected) {
                    statusEl.textContent = '已连接';
                    statusEl.className = 'connection-status connected';
                } else {
                    statusEl.textContent = '连接断开';
                    statusEl.className = 'connection-status disconnected';
                }
            }

            updateDashboard(data) {
                this.updateHealthStatus(data.health_status);
                this.updatePerformanceMetrics(data.performance_metrics);
                this.updateActiveAlerts(data.active_alerts);
                this.updateSystemInfo(data.system_info);
                this.updateLastUpdate(data.timestamp);
            }

            updateHealthStatus(healthStatus) {
                const container = document.getElementById('healthStatus');
                let html = '';

                if (healthStatus && healthStatus.overall_status) {
                    const status = healthStatus.overall_status;
                    const statusClass = this.getStatusClass(status);

                    html += `
                        <div class="metric-item">
                            <span class="metric-label">整体状态</span>
                            <span class="metric-value">
                                <span class="status-indicator ${statusClass}"></span>
                                ${status}
                            </span>
                        </div>
                    `;

                    if (healthStatus.health_rate !== undefined) {
                        html += `
                            <div class="metric-item">
                                <span class="metric-label">健康率</span>
                                <span class="metric-value">${(healthStatus.health_rate * 100).toFixed(1)}%</span>
                            </div>
                        `;
                    }
                }

                container.innerHTML = html || '<p style="color: #a0aec0;">暂无数据</p>';
            }

            updatePerformanceMetrics(metrics) {
                const container = document.getElementById('performanceMetrics');
                let html = '';

                if (metrics) {
                    const systemMetrics = metrics['system.cpu.usage'] !== undefined ? {
                        'CPU使用率': `${metrics['system.cpu.usage']?.toFixed(1) || 0}%`,
                        '内存使用率': `${metrics['system.memory.usage']?.toFixed(1) || 0}%`,
                        '磁盘使用率': `${metrics['system.disk.usage']?.toFixed(1) || 0}%`
                    } : {};

                    for (const [label, value] of Object.entries(systemMetrics)) {
                        html += `
                            <div class="metric-item">
                                <span class="metric-label">${label}</span>
                                <span class="metric-value">${value}</span>
                            </div>
                        `;
                    }
                }

                container.innerHTML = html || '<p style="color: #a0aec0;">暂无数据</p>';
            }

            updateActiveAlerts(alerts) {
                const container = document.getElementById('activeAlerts');
                let html = '';

                if (alerts && alerts.length > 0) {
                    alerts.forEach(alert => {
                        html += `
                            <div class="alert-item">
                                <div class="alert-title">${alert.title || '未知告警'}</div>
                                <div class="alert-message">${alert.message || ''}</div>
                            </div>
                        `;
                    });
                } else {
                    html = '<p style="color: #a0aec0; text-align: center;">暂无告警</p>';
                }

                container.innerHTML = html;
            }

            updateSystemInfo(systemInfo) {
                const container = document.getElementById('systemInfo');
                let html = '';

                if (systemInfo) {
                    for (const [key, value] of Object.entries(systemInfo)) {
                        html += `
                            <div class="metric-item">
                                <span class="metric-label">${key}</span>
                                <span class="metric-value">${value}</span>
                            </div>
                        `;
                    }
                }

                container.innerHTML = html || '<p style="color: #a0aec0;">暂无数据</p>';
            }

            updateLastUpdate(timestamp) {
                const lastUpdateEl = document.getElementById('lastUpdate');
                const date = new Date(timestamp * 1000);
                lastUpdateEl.textContent = `最后更新: ${date.toLocaleString('zh-CN')}`;
            }

            getStatusClass(status) {
                const statusMap = {
                    'healthy': 'status-healthy',
                    'warning': 'status-warning',
                    'error': 'status-error',
                    'critical': 'status-error'
                };
                return statusMap[status?.toLowerCase()] || 'status-unknown';
            }
        }

        // 启动仪表板客户端
        document.addEventListener('DOMContentLoaded', () => {
            new DashboardClient();
        });
    </script>
</body>
</html>
            """
        }

    async def create_app(self) -> Application:
        """创建Web应用"""
        app = web.Application()

        # 设置CORS
        cors = aiohttp_cors.setup(
            app,
            defaults={
                "*": aiohttp_cors.ResourceOptions(
                    allow_credentials=True,
                    expose_headers="*",
                    allow_headers="*",
                    allow_methods="*",
                )
            },
        )

        # 路由
        app.router.add_get("/", self.dashboard_handler)
        app.router.add_get("/ws", self.websocket_handler)
        app.router.add_get("/api/health", self.health_api_handler)
        app.router.add_get("/api/metrics", self.metrics_api_handler)
        app.router.add_get("/api/alerts", self.alerts_api_handler)

        # 添加CORS到所有路由
        for route in list(app.router.routes()):
            cors.add(route)

        return app

    async def dashboard_handler(self, request: Request) -> Response:
        """仪表板页面处理器"""
        template = self.jinja_env.get_template("dashboard.html")
        html = template.render()
        return web.Response(text=html, content_type="text/html")

    async def websocket_handler(self, request: Request) -> WebSocketResponse:
        """WebSocket处理器"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        await self.websocket_manager.add_connection(ws)

        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    # 处理客户端消息
                    pass
                elif msg.type == WSMsgType.ERROR:
                    self.logger.error(f"WebSocket错误: {ws.exception()}")
        except Exception as e:
            self.logger.error(f"WebSocket处理异常: {e}")
        finally:
            await self.websocket_manager.remove_connection(ws)

        return ws

    async def health_api_handler(self, request: Request) -> Response:
        """健康状态API"""
        try:
            health_data = await self._get_health_data()
            return web.json_response(health_data)
        except Exception as e:
            self.logger.error(f"获取健康数据失败: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def metrics_api_handler(self, request: Request) -> Response:
        """性能指标API"""
        try:
            metrics_data = await self._get_metrics_data()
            return web.json_response(metrics_data)
        except Exception as e:
            self.logger.error(f"获取指标数据失败: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def alerts_api_handler(self, request: Request) -> Response:
        """告警信息API"""
        try:
            alerts_data = await self._get_alerts_data()
            return web.json_response(alerts_data)
        except Exception as e:
            self.logger.error(f"获取告警数据失败: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def _get_health_data(self) -> dict[str, Any]:
        """获取健康数据"""
        try:
            # 获取健康检查结果
            health_results = await optimized_health_manager.run_all_checks()

            # 计算整体状态
            total_checks = len(health_results)
            healthy_checks = sum(
                1
                for result in health_results.values()
                if result.status.value == "healthy"
            )

            health_rate = healthy_checks / total_checks if total_checks > 0 else 0

            if health_rate >= 0.8:
                overall_status = "healthy"
            elif health_rate >= 0.6:
                overall_status = "warning"
            else:
                overall_status = "error"

            return {
                "overall_status": overall_status,
                "health_rate": health_rate,
                "total_checks": total_checks,
                "healthy_checks": healthy_checks,
                "details": {
                    name: {
                        "status": result.status.value,
                        "message": result.message,
                        "timestamp": result.timestamp,
                    }
                    for name, result in health_results.items()
                },
            }
        except Exception as e:
            self.logger.error(f"获取健康数据异常: {e}")
            return {"overall_status": "unknown", "error": str(e)}

    async def _get_metrics_data(self) -> dict[str, Any]:
        """获取指标数据"""
        try:
            # 获取系统指标
            system_metrics = optimized_performance_collector.get_system_metrics()

            # 获取所有指标
            all_metrics = optimized_performance_collector.get_all_metrics()

            return {**system_metrics, "custom_metrics": all_metrics}
        except Exception as e:
            self.logger.error(f"获取指标数据异常: {e}")
            return {"error": str(e)}

    async def _get_alerts_data(self) -> list[dict[str, Any]]:
        """获取告警数据"""
        try:
            # 获取活跃告警
            active_alerts = performance_alert_manager.get_active_alerts()

            return [
                {
                    "title": alert.rule_name,
                    "message": f"{alert.metric_name}: {alert.current_value}",
                    "level": alert.severity.value,
                    "timestamp": alert.triggered_at,
                }
                for alert in active_alerts
            ]
        except Exception as e:
            self.logger.error(f"获取告警数据异常: {e}")
            return []

    async def _get_system_info(self) -> dict[str, Any]:
        """获取系统信息"""
        try:
            import platform

            import psutil

            # 计算运行时间
            boot_time = psutil.boot_time()
            uptime = time.time() - boot_time
            uptime_str = str(timedelta(seconds=int(uptime)))

            return {
                "服务版本": "v1.0.0",
                "运行时间": uptime_str,
                "系统平台": platform.system(),
                "Python版本": platform.python_version(),
                "进程ID": str(os.getpid()) if "os" in globals() else "N/A",
            }
        except Exception as e:
            self.logger.error(f"获取系统信息异常: {e}")
            return {"error": str(e)}

    async def _collect_dashboard_data(self) -> DashboardData:
        """收集仪表板数据"""
        health_status = await self._get_health_data()
        performance_metrics = await self._get_metrics_data()
        active_alerts = await self._get_alerts_data()
        system_info = await self._get_system_info()

        return DashboardData(
            timestamp=time.time(),
            health_status=health_status,
            performance_metrics=performance_metrics,
            active_alerts=active_alerts,
            system_info=system_info,
        )

    async def _data_update_loop(self):
        """数据更新循环"""
        while self.running:
            try:
                # 收集数据
                dashboard_data = await self._collect_dashboard_data()

                # 广播到所有WebSocket连接
                await self.websocket_manager.broadcast(dashboard_data.to_dict())

                await asyncio.sleep(self.update_interval)

            except Exception as e:
                self.logger.error(f"数据更新循环异常: {e}")
                await asyncio.sleep(self.update_interval)

    async def start(self):
        """启动仪表板服务器"""
        if self.running:
            self.logger.warning("仪表板服务器已在运行")
            return

        self.running = True

        # 创建应用
        self.app = await self.create_app()

        # 启动数据更新循环
        asyncio.create_task(self._data_update_loop())

        # 启动Web服务器
        runner = web.AppRunner(self.app)
        await runner.setup()

        site = web.TCPSite(runner, self.host, self.port)
        await site.start()

        self.logger.info(f"仪表板服务器已启动: http://{self.host}:{self.port}")

    async def stop(self):
        """停止仪表板服务器"""
        self.running = False
        self.logger.info("仪表板服务器已停止")


# 全局仪表板服务器实例
dashboard_server = DashboardServer()


# 使用示例
if __name__ == "__main__":

    async def demo_dashboard():
        """演示仪表板"""
        print("🚀 监控仪表板演示")

        # 启动仪表板服务器
        await dashboard_server.start()

        print("📊 仪表板已启动: http://localhost:8080")
        print("请在浏览器中打开上述地址查看监控仪表板")

        # 保持运行
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n停止仪表板...")
            await dashboard_server.stop()

    asyncio.run(demo_dashboard())
