"""
增强版监控仪表板UI
提供现代化的Web界面展示系统健康状态、性能指标和告警信息
新增功能：实时图表、告警管理、性能分析、移动端适配
"""

import asyncio
import json
import logging
import platform
import time
from dataclasses import asdict, dataclass
from typing import Any

import aiohttp_cors
import jinja2
import psutil

# Web框架
from aiohttp import WSMsgType, web
from aiohttp.web import Application, Request, Response, WebSocketResponse

# 内部模块
from .optimized_health_check import optimized_health_manager
from .optimized_performance_monitor import optimized_performance_collector
from .performance_alerting import performance_alert_manager


@dataclass
class EnhancedDashboardData:
    """增强版仪表板数据"""

    timestamp: float
    health_status: dict[str, Any]
    performance_metrics: dict[str, Any]
    active_alerts: list[dict[str, Any]]
    system_info: dict[str, Any]
    historical_data: dict[str, list[Any]]
    ai_insights: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return asdict(self)


class EnhancedDashboardServer:
    """增强版仪表板服务器"""

    def __init__(self, host: str = "0.0.0.0", port: int = 8080):
        self.host = host
        self.port = port
        self.app: Application | None = None
        self.websocket_connections: list[WebSocketResponse] = []
        self.logger = logging.getLogger("enhanced_dashboard")

        # 数据更新间隔
        self.update_interval = 1.0
        self.running = False

        # 历史数据存储（内存中保留最近1小时）
        self.historical_data = {
            "cpu_usage": [],
            "memory_usage": [],
            "response_times": [],
            "error_rates": [],
            "alert_counts": [],
        }
        self.max_history_points = 3600  # 1小时的秒级数据

        # 模板引擎
        self.jinja_env = jinja2.Environment(
            loader=jinja2.DictLoader(self._get_enhanced_templates()),
            autoescape=jinja2.select_autoescape(["html", "xml"]),
        )

    def _get_enhanced_templates(self) -> dict[str, str]:
        """获取增强版HTML模板"""
        return {
            "enhanced_dashboard.html": """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>索克生活 - 无障碍服务智能监控中心</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/date-fns@2.29.3/index.min.js"></script>
    <style>
        :root {
            --primary-color: #667eea;
            --secondary-color: #764ba2;
            --success-color: #48bb78;
            --warning-color: #ed8936;
            --error-color: #f56565;
            --info-color: #4299e1;
            --background-gradient: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            --card-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            --border-radius: 12px;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: var(--background-gradient);
            color: #333;
            min-height: 100vh;
            overflow-x: hidden;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
            animation: fadeInDown 0.8s ease;
        }

        .header h1 {
            font-size: 2.8rem;
            margin-bottom: 10px;
            font-weight: 700;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }

        .header p {
            font-size: 1.2rem;
            opacity: 0.9;
            margin-bottom: 20px;
        }

        .status-bar {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }

        .status-item {
            background: rgba(255, 255, 255, 0.2);
            padding: 10px 20px;
            border-radius: 25px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.3);
        }

        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .card {
            background: white;
            border-radius: var(--border-radius);
            padding: 25px;
            box-shadow: var(--card-shadow);
            transition: all 0.3s ease;
            animation: fadeInUp 0.6s ease;
            position: relative;
            overflow: hidden;
        }

        .card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: var(--primary-color);
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        }

        .card-title {
            font-size: 1.3rem;
            font-weight: 600;
            margin-bottom: 20px;
            color: #2d3748;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .card-icon {
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            color: white;
        }

        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }

        .status-healthy { background-color: var(--success-color); }
        .status-warning { background-color: var(--warning-color); }
        .status-error { background-color: var(--error-color); }
        .status-unknown { background-color: #a0aec0; }

        .metric-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
        }

        .metric-item {
            text-align: center;
            padding: 15px;
            background: #f7fafc;
            border-radius: 8px;
            transition: background-color 0.3s ease;
        }

        .metric-item:hover {
            background: #edf2f7;
        }

        .metric-value {
            font-size: 1.8rem;
            font-weight: 700;
            color: var(--primary-color);
            margin-bottom: 5px;
        }

        .metric-label {
            font-size: 0.9rem;
            color: #718096;
            font-weight: 500;
        }

        .chart-container {
            position: relative;
            height: 300px;
            margin-top: 20px;
        }

        .alert-item {
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 8px;
            border-left: 4px solid;
            background: #f7fafc;
            transition: all 0.3s ease;
        }

        .alert-item:hover {
            transform: translateX(5px);
        }

        .alert-critical { border-left-color: var(--error-color); }
        .alert-warning { border-left-color: var(--warning-color); }
        .alert-info { border-left-color: var(--info-color); }

        .alert-title {
            font-weight: 600;
            margin-bottom: 5px;
        }

        .alert-time {
            font-size: 0.8rem;
            color: #718096;
        }

        .connection-status {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 10px 15px;
            border-radius: 25px;
            font-size: 0.9rem;
            font-weight: 500;
            z-index: 1000;
            transition: all 0.3s ease;
        }

        .connected {
            background: var(--success-color);
            color: white;
        }

        .disconnected {
            background: var(--error-color);
            color: white;
        }

        .loading {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 200px;
        }

        .spinner {
            width: 40px;
            height: 40px;
            border: 4px solid #f3f3f3;
            border-top: 4px solid var(--primary-color);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        @keyframes fadeInDown {
            from { opacity: 0; transform: translateY(-30px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        /* 响应式设计 */
        @media (max-width: 768px) {
            .container { padding: 10px; }
            .header h1 { font-size: 2rem; }
            .dashboard-grid { grid-template-columns: 1fr; }
            .status-bar { flex-direction: column; align-items: center; }
            .metric-grid { grid-template-columns: repeat(2, 1fr); }
        }

        /* 深色模式支持 */
        @media (prefers-color-scheme: dark) {
            .card { background: #2d3748; color: white; }
            .metric-item { background: #4a5568; }
            .alert-item { background: #4a5568; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 索克生活无障碍服务</h1>
            <p>智能监控中心 - 实时系统状态与性能分析</p>
            <div class="status-bar">
                <div class="status-item">
                    <span id="system-status">🔄 连接中...</span>
                </div>
                <div class="status-item">
                    <span id="last-update">⏰ 等待数据...</span>
                </div>
                <div class="status-item">
                    <span id="uptime">⏱️ 运行时间: --</span>
                </div>
            </div>
        </div>

        <div class="connection-status" id="connection-status">🔄 连接中</div>

        <div class="dashboard-grid">
            <!-- 系统健康状态 -->
            <div class="card">
                <div class="card-title">
                    <div class="card-icon" style="background: var(--success-color);">💚</div>
                    系统健康状态
                </div>
                <div id="health-status" class="loading">
                    <div class="spinner"></div>
                </div>
            </div>

            <!-- 性能指标 -->
            <div class="card">
                <div class="card-title">
                    <div class="card-icon" style="background: var(--info-color);">📊</div>
                    实时性能指标
                </div>
                <div id="performance-metrics" class="metric-grid">
                    <div class="loading"><div class="spinner"></div></div>
                </div>
            </div>

            <!-- CPU使用率图表 -->
            <div class="card">
                <div class="card-title">
                    <div class="card-icon" style="background: var(--primary-color);">🖥️</div>
                    CPU使用率趋势
                </div>
                <div class="chart-container">
                    <canvas id="cpu-chart"></canvas>
                </div>
            </div>

            <!-- 内存使用率图表 -->
            <div class="card">
                <div class="card-title">
                    <div class="card-icon" style="background: var(--secondary-color);">💾</div>
                    内存使用率趋势
                </div>
                <div class="chart-container">
                    <canvas id="memory-chart"></canvas>
                </div>
            </div>

            <!-- 活跃告警 -->
            <div class="card">
                <div class="card-title">
                    <div class="card-icon" style="background: var(--warning-color);">⚠️</div>
                    活跃告警
                </div>
                <div id="active-alerts">
                    <div class="loading"><div class="spinner"></div></div>
                </div>
            </div>

            <!-- AI洞察 -->
            <div class="card">
                <div class="card-title">
                    <div class="card-icon" style="background: var(--secondary-color);">🤖</div>
                    AI智能洞察
                </div>
                <div id="ai-insights">
                    <div class="loading"><div class="spinner"></div></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        class EnhancedDashboard {
            constructor() {
                this.ws = null;
                this.charts = {};
                this.isConnected = false;
                this.reconnectAttempts = 0;
                this.maxReconnectAttempts = 5;
                this.reconnectDelay = 1000;

                this.initWebSocket();
                this.initCharts();
                this.updateConnectionStatus();
            }

            initWebSocket() {
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                const wsUrl = `${protocol}//${window.location.host}/ws`;

                this.ws = new WebSocket(wsUrl);

                this.ws.onopen = () => {
                    console.log('WebSocket连接已建立');
                    this.isConnected = true;
                    this.reconnectAttempts = 0;
                    this.updateConnectionStatus();
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
                    console.log('WebSocket连接已关闭');
                    this.isConnected = false;
                    this.updateConnectionStatus();
                    this.attemptReconnect();
                };

                this.ws.onerror = (error) => {
                    console.error('WebSocket错误:', error);
                    this.isConnected = false;
                    this.updateConnectionStatus();
                };
            }

            attemptReconnect() {
                if (this.reconnectAttempts < this.maxReconnectAttempts) {
                    this.reconnectAttempts++;
                    console.log(`尝试重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

                    setTimeout(() => {
                        this.initWebSocket();
                    }, this.reconnectDelay * this.reconnectAttempts);
                }
            }

            updateConnectionStatus() {
                const statusElement = document.getElementById('connection-status');
                if (this.isConnected) {
                    statusElement.textContent = '🟢 已连接';
                    statusElement.className = 'connection-status connected';
                } else {
                    statusElement.textContent = '🔴 连接断开';
                    statusElement.className = 'connection-status disconnected';
                }
            }

            initCharts() {
                // CPU使用率图表
                const cpuCtx = document.getElementById('cpu-chart').getContext('2d');
                this.charts.cpu = new Chart(cpuCtx, {
                    type: 'line',
                    data: {
                        labels: [],
                        datasets: [{
                            label: 'CPU使用率 (%)',
                            data: [],
                            borderColor: '#667eea',
                            backgroundColor: 'rgba(102, 126, 234, 0.1)',
                            tension: 0.4,
                            fill: true
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: {
                                beginAtZero: true,
                                max: 100
                            }
                        },
                        plugins: {
                            legend: {
                                display: false
                            }
                        }
                    }
                });

                // 内存使用率图表
                const memoryCtx = document.getElementById('memory-chart').getContext('2d');
                this.charts.memory = new Chart(memoryCtx, {
                    type: 'line',
                    data: {
                        labels: [],
                        datasets: [{
                            label: '内存使用率 (%)',
                            data: [],
                            borderColor: '#764ba2',
                            backgroundColor: 'rgba(118, 75, 162, 0.1)',
                            tension: 0.4,
                            fill: true
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: {
                                beginAtZero: true,
                                max: 100
                            }
                        },
                        plugins: {
                            legend: {
                                display: false
                            }
                        }
                    }
                });
            }

            updateDashboard(data) {
                this.updateSystemStatus(data);
                this.updateHealthStatus(data.health_status);
                this.updatePerformanceMetrics(data.performance_metrics);
                this.updateCharts(data.historical_data);
                this.updateActiveAlerts(data.active_alerts);
                this.updateAIInsights(data.ai_insights);
                this.updateLastUpdateTime();
            }

            updateSystemStatus(data) {
                const systemInfo = data.system_info || {};
                document.getElementById('system-status').textContent =
                    `🟢 系统正常 (${systemInfo.platform || 'Unknown'})`;

                if (systemInfo.uptime) {
                    document.getElementById('uptime').textContent =
                        `⏱️ 运行时间: ${this.formatUptime(systemInfo.uptime)}`;
                }
            }

            updateHealthStatus(healthStatus) {
                const container = document.getElementById('health-status');
                if (!healthStatus) return;

                const overallStatus = healthStatus.overall_status || 'unknown';
                const checks = healthStatus.checks || [];

                let html = `
                    <div class="metric-item">
                        <div class="metric-value">
                            <span class="status-indicator status-${overallStatus.toLowerCase()}"></span>
                            ${overallStatus.toUpperCase()}
                        </div>
                        <div class="metric-label">总体状态</div>
                    </div>
                `;

                checks.forEach(check => {
                    const status = check.status || 'unknown';
                    html += `
                        <div class="metric-item">
                            <div class="metric-value">
                                <span class="status-indicator status-${status.toLowerCase()}"></span>
                                ${check.name}
                            </div>
                            <div class="metric-label">${check.message || ''}</div>
                        </div>
                    `;
                });

                container.innerHTML = html;
            }

            updatePerformanceMetrics(metrics) {
                const container = document.getElementById('performance-metrics');
                if (!metrics) return;

                let html = '';
                Object.entries(metrics).forEach(([key, value]) => {
                    if (typeof value === 'number') {
                        html += `
                            <div class="metric-item">
                                <div class="metric-value">${value.toFixed(1)}</div>
                                <div class="metric-label">${this.formatMetricName(key)}</div>
                            </div>
                        `;
                    }
                });

                container.innerHTML = html;
            }

            updateCharts(historicalData) {
                if (!historicalData) return;

                // 更新CPU图表
                if (historicalData.cpu_usage && this.charts.cpu) {
                    const cpuData = historicalData.cpu_usage.slice(-60); // 最近60个数据点
                    const labels = cpuData.map((_, index) => {
                        const time = new Date(Date.now() - (cpuData.length - index - 1) * 1000);
                        return time.toLocaleTimeString();
                    });

                    this.charts.cpu.data.labels = labels;
                    this.charts.cpu.data.datasets[0].data = cpuData;
                    this.charts.cpu.update('none');
                }

                // 更新内存图表
                if (historicalData.memory_usage && this.charts.memory) {
                    const memoryData = historicalData.memory_usage.slice(-60);
                    const labels = memoryData.map((_, index) => {
                        const time = new Date(Date.now() - (memoryData.length - index - 1) * 1000);
                        return time.toLocaleTimeString();
                    });

                    this.charts.memory.data.labels = labels;
                    this.charts.memory.data.datasets[0].data = memoryData;
                    this.charts.memory.update('none');
                }
            }

            updateActiveAlerts(alerts) {
                const container = document.getElementById('active-alerts');
                if (!alerts || alerts.length === 0) {
                    container.innerHTML = '<div class="metric-item"><div class="metric-label">🎉 暂无活跃告警</div></div>';
                    return;
                }

                let html = '';
                alerts.forEach(alert => {
                    const level = alert.level || 'info';
                    const time = new Date(alert.timestamp * 1000).toLocaleString();
                    html += `
                        <div class="alert-item alert-${level}">
                            <div class="alert-title">${alert.message}</div>
                            <div class="alert-time">${time}</div>
                        </div>
                    `;
                });

                container.innerHTML = html;
            }

            updateAIInsights(insights) {
                const container = document.getElementById('ai-insights');
                if (!insights) {
                    container.innerHTML = '<div class="metric-item"><div class="metric-label">🤖 AI分析中...</div></div>';
                    return;
                }

                let html = '';
                Object.entries(insights).forEach(([key, value]) => {
                    html += `
                        <div class="metric-item">
                            <div class="metric-label">${this.formatInsightName(key)}</div>
                            <div style="margin-top: 5px; font-size: 0.9rem;">${value}</div>
                        </div>
                    `;
                });

                container.innerHTML = html;
            }

            updateLastUpdateTime() {
                const now = new Date().toLocaleTimeString();
                document.getElementById('last-update').textContent = `⏰ 最后更新: ${now}`;
            }

            formatMetricName(name) {
                const nameMap = {
                    'cpu_percent': 'CPU使用率 (%)',
                    'memory_percent': '内存使用率 (%)',
                    'disk_usage': '磁盘使用率 (%)',
                    'response_time': '响应时间 (ms)',
                    'error_rate': '错误率 (%)',
                    'request_count': '请求数量'
                };
                return nameMap[name] || name;
            }

            formatInsightName(name) {
                const nameMap = {
                    'performance_trend': '📈 性能趋势',
                    'anomaly_detection': '🔍 异常检测',
                    'capacity_prediction': '📊 容量预测',
                    'optimization_suggestion': '💡 优化建议'
                };
                return nameMap[name] || name;
            }

            formatUptime(seconds) {
                const days = Math.floor(seconds / 86400);
                const hours = Math.floor((seconds % 86400) / 3600);
                const minutes = Math.floor((seconds % 3600) / 60);

                if (days > 0) {
                    return `${days}天 ${hours}小时 ${minutes}分钟`;
                } else if (hours > 0) {
                    return `${hours}小时 ${minutes}分钟`;
                } else {
                    return `${minutes}分钟`;
                }
            }
        }

        // 初始化仪表板
        document.addEventListener('DOMContentLoaded', () => {
            new EnhancedDashboard();
        });
    </script>
</body>
</html>
            """
        }

    async def _collect_enhanced_data(self) -> EnhancedDashboardData:
        """收集增强版仪表板数据"""
        current_time = time.time()

        # 收集基础数据
        health_data = await self._get_health_data()
        metrics_data = await self._get_metrics_data()
        alerts_data = await self._get_alerts_data()
        system_info = await self._get_system_info()

        # 更新历史数据
        self._update_historical_data(metrics_data)

        # 生成AI洞察
        ai_insights = await self._generate_ai_insights(metrics_data, health_data)

        return EnhancedDashboardData(
            timestamp=current_time,
            health_status=health_data,
            performance_metrics=metrics_data,
            active_alerts=alerts_data,
            system_info=system_info,
            historical_data=self.historical_data.copy(),
            ai_insights=ai_insights,
        )

    def _update_historical_data(self, metrics: dict[str, Any]):
        """更新历史数据"""
        current_time = time.time()

        # 添加新数据点
        if "cpu_percent" in metrics:
            self.historical_data["cpu_usage"].append(metrics["cpu_percent"])
        if "memory_percent" in metrics:
            self.historical_data["memory_usage"].append(metrics["memory_percent"])
        if "response_time" in metrics:
            self.historical_data["response_times"].append(metrics["response_time"])
        if "error_rate" in metrics:
            self.historical_data["error_rates"].append(metrics["error_rate"])

        # 限制历史数据长度
        for key in self.historical_data:
            if len(self.historical_data[key]) > self.max_history_points:
                self.historical_data[key] = self.historical_data[key][
                    -self.max_history_points :
                ]

    async def _generate_ai_insights(
        self, metrics: dict[str, Any], health: dict[str, Any]
    ) -> dict[str, str]:
        """生成AI洞察"""
        insights = {}

        # 性能趋势分析
        if self.historical_data["cpu_usage"]:
            recent_cpu = self.historical_data["cpu_usage"][-10:]
            if len(recent_cpu) >= 5:
                trend = "上升" if recent_cpu[-1] > recent_cpu[0] else "下降"
                avg_cpu = sum(recent_cpu) / len(recent_cpu)
                insights["performance_trend"] = (
                    f"CPU使用率呈{trend}趋势，平均值{avg_cpu:.1f}%"
                )

        # 异常检测
        anomalies = []
        if metrics.get("cpu_percent", 0) > 80:
            anomalies.append("CPU使用率过高")
        if metrics.get("memory_percent", 0) > 90:
            anomalies.append("内存使用率过高")
        if metrics.get("error_rate", 0) > 5:
            anomalies.append("错误率异常")

        if anomalies:
            insights["anomaly_detection"] = f"检测到异常: {', '.join(anomalies)}"
        else:
            insights["anomaly_detection"] = "系统运行正常，未检测到异常"

        # 容量预测
        if self.historical_data["memory_usage"]:
            recent_memory = self.historical_data["memory_usage"][-30:]
            if len(recent_memory) >= 10:
                avg_growth = (recent_memory[-1] - recent_memory[0]) / len(recent_memory)
                if avg_growth > 0.1:
                    insights["capacity_prediction"] = (
                        "内存使用量持续增长，建议关注内存泄漏"
                    )
                else:
                    insights["capacity_prediction"] = "内存使用量稳定，容量充足"

        # 优化建议
        suggestions = []
        if metrics.get("cpu_percent", 0) > 70:
            suggestions.append("考虑优化CPU密集型任务")
        if metrics.get("response_time", 0) > 1000:
            suggestions.append("响应时间较长，建议优化查询性能")
        if len(health.get("checks", [])) > 0:
            failed_checks = [
                c for c in health["checks"] if c.get("status") != "healthy"
            ]
            if failed_checks:
                suggestions.append(f"修复{len(failed_checks)}个健康检查问题")

        if suggestions:
            insights["optimization_suggestion"] = "; ".join(suggestions)
        else:
            insights["optimization_suggestion"] = "系统运行良好，暂无优化建议"

        return insights

    async def _get_health_data(self) -> dict[str, Any]:
        """获取健康检查数据"""
        try:
            health_result = await optimized_health_manager.check_health()
            return {
                "overall_status": health_result.overall_status.value,
                "checks": [
                    {
                        "name": check.name,
                        "status": check.status.value,
                        "message": check.message,
                        "timestamp": check.timestamp,
                    }
                    for check in health_result.checks
                ],
            }
        except Exception as e:
            self.logger.error(f"获取健康数据失败: {e}")
            return {"overall_status": "unknown", "checks": []}

    async def _get_metrics_data(self) -> dict[str, Any]:
        """获取性能指标数据"""
        try:
            # 获取系统指标
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            # 获取应用指标
            app_metrics = optimized_performance_collector.get_current_metrics()

            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_usage": disk.percent,
                "response_time": app_metrics.get("response_time", 0),
                "error_rate": app_metrics.get("error_rate", 0),
                "request_count": app_metrics.get("request_count", 0),
            }
        except Exception as e:
            self.logger.error(f"获取性能指标失败: {e}")
            return {}

    async def _get_alerts_data(self) -> list[dict[str, Any]]:
        """获取告警数据"""
        try:
            active_alerts = performance_alert_manager.get_active_alerts()
            return [
                {
                    "message": alert.message,
                    "level": alert.level.value,
                    "timestamp": alert.timestamp,
                    "source": alert.source,
                }
                for alert in active_alerts
            ]
        except Exception as e:
            self.logger.error(f"获取告警数据失败: {e}")
            return []

    async def _get_system_info(self) -> dict[str, Any]:
        """获取系统信息"""
        try:
            boot_time = psutil.boot_time()
            uptime = time.time() - boot_time

            return {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "uptime": uptime,
                "boot_time": boot_time,
            }
        except Exception as e:
            self.logger.error(f"获取系统信息失败: {e}")
            return {}

    async def websocket_handler(self, request: Request) -> WebSocketResponse:
        """WebSocket处理器"""
        ws = WebSocketResponse()
        await ws.prepare(request)

        self.websocket_connections.append(ws)
        self.logger.info(
            f"新的WebSocket连接，当前连接数: {len(self.websocket_connections)}"
        )

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
            if ws in self.websocket_connections:
                self.websocket_connections.remove(ws)
            self.logger.info(
                f"WebSocket连接断开，当前连接数: {len(self.websocket_connections)}"
            )

        return ws

    async def dashboard_handler(self, request: Request) -> Response:
        """仪表板页面处理器"""
        template = self.jinja_env.get_template("enhanced_dashboard.html")
        html = template.render()
        return Response(text=html, content_type="text/html")

    async def broadcast_data(self):
        """广播数据到所有WebSocket连接"""
        if not self.websocket_connections:
            return

        try:
            data = await self._collect_enhanced_data()
            message = json.dumps(data.to_dict(), ensure_ascii=False, default=str)

            disconnected = []
            for ws in self.websocket_connections:
                try:
                    await ws.send_str(message)
                except Exception as e:
                    self.logger.error(f"发送WebSocket消息失败: {e}")
                    disconnected.append(ws)

            # 清理断开的连接
            for ws in disconnected:
                if ws in self.websocket_connections:
                    self.websocket_connections.remove(ws)

        except Exception as e:
            self.logger.error(f"广播数据失败: {e}")

    async def _data_update_loop(self):
        """数据更新循环"""
        while self.running:
            try:
                await self.broadcast_data()
                await asyncio.sleep(self.update_interval)
            except Exception as e:
                self.logger.error(f"数据更新循环异常: {e}")
                await asyncio.sleep(5)

    async def create_app(self) -> Application:
        """创建Web应用"""
        app = Application()

        # 添加路由
        app.router.add_get("/", self.dashboard_handler)
        app.router.add_get("/dashboard", self.dashboard_handler)
        app.router.add_get("/ws", self.websocket_handler)

        # 配置CORS
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

        for route in list(app.router.routes()):
            cors.add(route)

        return app

    async def start(self):
        """启动仪表板服务器"""
        self.app = await self.create_app()
        self.running = True

        # 启动数据更新循环
        asyncio.create_task(self._data_update_loop())

        # 启动Web服务器
        runner = web.AppRunner(self.app)
        await runner.setup()

        site = web.TCPSite(runner, self.host, self.port)
        await site.start()

        self.logger.info(f"增强版监控仪表板已启动: http://{self.host}:{self.port}")
        print(f"🚀 增强版监控仪表板已启动: http://{self.host}:{self.port}")
        print("📊 实时图表、AI洞察、移动端适配")

    async def stop(self):
        """停止仪表板服务器"""
        self.running = False
        if self.app:
            await self.app.cleanup()


# 全局实例
enhanced_dashboard_server = EnhancedDashboardServer()


async def demo_enhanced_dashboard():
    """演示增强版仪表板"""
    print("🚀 启动增强版监控仪表板演示...")

    try:
        await enhanced_dashboard_server.start()

        print("✅ 仪表板已启动，按 Ctrl+C 停止")

        # 保持运行
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        print("\n🛑 正在停止仪表板...")
        await enhanced_dashboard_server.stop()
        print("✅ 仪表板已停止")
    except Exception as e:
        print(f"❌ 仪表板运行异常: {e}")
        await enhanced_dashboard_server.stop()


if __name__ == "__main__":
    asyncio.run(demo_enhanced_dashboard())
