#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
索克生活 A2A 智能体网络 Web 仪表板
Suoke Life A2A Agent Network Web Dashboard

提供实时的网络监控和管理界面
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any
from flask import Flask, render_template_string, jsonify, request
from flask_socketio import SocketIO, emit
import threading
import time

from a2a_network_monitor import A2ANetworkMonitor

logger = logging.getLogger(__name__)

# Flask 应用
app = Flask(__name__)
app.config['SECRET_KEY'] = 'suoke_life_a2a_dashboard'
socketio = SocketIO(app, cors_allowed_origins="*")

# 全局监控器实例
monitor = None
monitoring_active = False

# HTML 模板
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>索克生活 A2A 智能体网络监控仪表板</title>
    <script src="https://cdn.socket.io/4.0.0/socket.io.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
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
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .status-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            backdrop-filter: blur(10px);
        }
        
        .status-item {
            text-align: center;
            color: white;
        }
        
        .status-value {
            font-size: 1.8em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .status-label {
            font-size: 0.9em;
            opacity: 0.8;
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .card {
            background: rgba(255,255,255,0.95);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        .card h3 {
            color: #4a5568;
            margin-bottom: 15px;
            font-size: 1.2em;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 10px;
        }
        
        .agent-card {
            border-left: 4px solid #48bb78;
        }
        
        .agent-card.warning {
            border-left-color: #ed8936;
        }
        
        .agent-card.critical {
            border-left-color: #f56565;
        }
        
        .metric-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            padding: 8px 0;
            border-bottom: 1px solid #e2e8f0;
        }
        
        .metric-label {
            color: #718096;
            font-weight: 500;
        }
        
        .metric-value {
            color: #2d3748;
            font-weight: bold;
        }
        
        .health-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .health-healthy {
            background-color: #48bb78;
        }
        
        .health-warning {
            background-color: #ed8936;
        }
        
        .health-critical {
            background-color: #f56565;
        }
        
        .chart-container {
            position: relative;
            height: 300px;
            margin-top: 20px;
        }
        
        .controls {
            text-align: center;
            margin: 20px 0;
        }
        
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 1em;
            margin: 0 10px;
            transition: transform 0.2s;
        }
        
        .btn:hover {
            transform: translateY(-2px);
        }
        
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        .log-container {
            background: #1a202c;
            color: #e2e8f0;
            padding: 20px;
            border-radius: 10px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            max-height: 300px;
            overflow-y: auto;
        }
        
        .log-entry {
            margin-bottom: 5px;
            padding: 2px 0;
        }
        
        .log-timestamp {
            color: #90cdf4;
        }
        
        .log-level-info {
            color: #68d391;
        }
        
        .log-level-warning {
            color: #fbb6ce;
        }
        
        .log-level-error {
            color: #fc8181;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .pulse {
            animation: pulse 2s infinite;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 索克生活 A2A 智能体网络监控</h1>
            <p>实时监控四大智能体的运行状态和性能指标</p>
        </div>
        
        <div class="status-bar">
            <div class="status-item">
                <div class="status-value" id="network-status">离线</div>
                <div class="status-label">网络状态</div>
            </div>
            <div class="status-item">
                <div class="status-value" id="active-agents">0/4</div>
                <div class="status-label">活跃智能体</div>
            </div>
            <div class="status-item">
                <div class="status-value" id="success-rate">0%</div>
                <div class="status-label">成功率</div>
            </div>
            <div class="status-item">
                <div class="status-value" id="total-requests">0</div>
                <div class="status-label">总请求数</div>
            </div>
            <div class="status-item">
                <div class="status-value" id="uptime">0s</div>
                <div class="status-label">运行时间</div>
            </div>
        </div>
        
        <div class="controls">
            <button class="btn" onclick="startMonitoring()" id="start-btn">启动监控</button>
            <button class="btn" onclick="stopMonitoring()" id="stop-btn" disabled>停止监控</button>
            <button class="btn" onclick="runHealthCheck()">健康检查</button>
            <button class="btn" onclick="runPerformanceTest()">性能测试</button>
            <button class="btn" onclick="exportMetrics()">导出数据</button>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>🤖 智能体状态</h3>
                <div id="agents-status">
                    <div class="agent-card" id="agent-xiaoai">
                        <div class="metric-row">
                            <span class="metric-label">
                                <span class="health-indicator health-critical"></span>小艾智能体
                            </span>
                            <span class="metric-value">离线</span>
                        </div>
                    </div>
                    <div class="agent-card" id="agent-xiaoke">
                        <div class="metric-row">
                            <span class="metric-label">
                                <span class="health-indicator health-critical"></span>小克智能体
                            </span>
                            <span class="metric-value">离线</span>
                        </div>
                    </div>
                    <div class="agent-card" id="agent-laoke">
                        <div class="metric-row">
                            <span class="metric-label">
                                <span class="health-indicator health-critical"></span>老克智能体
                            </span>
                            <span class="metric-value">离线</span>
                        </div>
                    </div>
                    <div class="agent-card" id="agent-soer">
                        <div class="metric-row">
                            <span class="metric-label">
                                <span class="health-indicator health-critical"></span>索儿智能体
                            </span>
                            <span class="metric-value">离线</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h3>📊 性能指标</h3>
                <div class="chart-container">
                    <canvas id="performance-chart"></canvas>
                </div>
            </div>
            
            <div class="card">
                <h3>🏥 健康状态</h3>
                <div id="health-status">
                    <div class="metric-row">
                        <span class="metric-label">整体健康</span>
                        <span class="metric-value" id="overall-health">未知</span>
                    </div>
                    <div id="health-issues"></div>
                </div>
            </div>
            
            <div class="card">
                <h3>⚡ 实时指标</h3>
                <div id="realtime-metrics">
                    <div class="metric-row">
                        <span class="metric-label">平均响应时间</span>
                        <span class="metric-value" id="avg-response-time">0ms</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">并发请求峰值</span>
                        <span class="metric-value" id="peak-concurrent">0</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">错误率</span>
                        <span class="metric-value" id="error-rate">0%</span>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h3>📝 系统日志</h3>
            <div class="log-container" id="system-logs">
                <div class="log-entry">
                    <span class="log-timestamp">[2024-01-01 00:00:00]</span>
                    <span class="log-level-info">[INFO]</span>
                    系统启动，等待连接...
                </div>
            </div>
        </div>
    </div>

    <script>
        const socket = io();
        let performanceChart = null;
        
        // 初始化图表
        function initChart() {
            const ctx = document.getElementById('performance-chart').getContext('2d');
            performanceChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: '成功率 (%)',
                        data: [],
                        borderColor: '#48bb78',
                        backgroundColor: 'rgba(72, 187, 120, 0.1)',
                        tension: 0.4
                    }, {
                        label: '响应时间 (ms)',
                        data: [],
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        tension: 0.4,
                        yAxisID: 'y1'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            type: 'linear',
                            display: true,
                            position: 'left',
                            max: 100
                        },
                        y1: {
                            type: 'linear',
                            display: true,
                            position: 'right',
                            grid: {
                                drawOnChartArea: false,
                            }
                        }
                    }
                }
            });
        }
        
        // 更新图表
        function updateChart(metrics) {
            if (!performanceChart) return;
            
            const now = new Date().toLocaleTimeString();
            const successRate = (metrics.success_rate * 100).toFixed(1);
            const responseTime = (metrics.avg_response_time * 1000).toFixed(0);
            
            performanceChart.data.labels.push(now);
            performanceChart.data.datasets[0].data.push(successRate);
            performanceChart.data.datasets[1].data.push(responseTime);
            
            // 保持最近20个数据点
            if (performanceChart.data.labels.length > 20) {
                performanceChart.data.labels.shift();
                performanceChart.data.datasets[0].data.shift();
                performanceChart.data.datasets[1].data.shift();
            }
            
            performanceChart.update();
        }
        
        // 添加日志
        function addLog(level, message) {
            const logsContainer = document.getElementById('system-logs');
            const timestamp = new Date().toLocaleString();
            const logEntry = document.createElement('div');
            logEntry.className = 'log-entry';
            logEntry.innerHTML = `
                <span class="log-timestamp">[${timestamp}]</span>
                <span class="log-level-${level}">[${level.toUpperCase()}]</span>
                ${message}
            `;
            logsContainer.appendChild(logEntry);
            logsContainer.scrollTop = logsContainer.scrollHeight;
            
            // 保持最近50条日志
            while (logsContainer.children.length > 50) {
                logsContainer.removeChild(logsContainer.firstChild);
            }
        }
        
        // 启动监控
        function startMonitoring() {
            socket.emit('start_monitoring');
            document.getElementById('start-btn').disabled = true;
            document.getElementById('stop-btn').disabled = false;
            addLog('info', '正在启动监控...');
        }
        
        // 停止监控
        function stopMonitoring() {
            socket.emit('stop_monitoring');
            document.getElementById('start-btn').disabled = false;
            document.getElementById('stop-btn').disabled = true;
            addLog('info', '正在停止监控...');
        }
        
        // 健康检查
        function runHealthCheck() {
            socket.emit('health_check');
            addLog('info', '正在执行健康检查...');
        }
        
        // 性能测试
        function runPerformanceTest() {
            socket.emit('performance_test');
            addLog('info', '正在执行性能测试...');
        }
        
        // 导出数据
        function exportMetrics() {
            socket.emit('export_metrics');
            addLog('info', '正在导出指标数据...');
        }
        
        // Socket 事件处理
        socket.on('connect', function() {
            addLog('info', '已连接到监控服务器');
        });
        
        socket.on('disconnect', function() {
            addLog('warning', '与监控服务器断开连接');
        });
        
        socket.on('monitoring_started', function(data) {
            addLog('info', '监控已启动');
            document.getElementById('network-status').textContent = '在线';
            document.getElementById('network-status').className = 'status-value pulse';
        });
        
        socket.on('monitoring_stopped', function(data) {
            addLog('info', '监控已停止');
            document.getElementById('network-status').textContent = '离线';
            document.getElementById('network-status').className = 'status-value';
        });
        
        socket.on('metrics_update', function(data) {
            // 更新状态栏
            const networkMetrics = data.network_metrics;
            document.getElementById('active-agents').textContent = 
                `${networkMetrics.active_agents}/${networkMetrics.total_agents}`;
            document.getElementById('success-rate').textContent = 
                `${(networkMetrics.success_rate * 100).toFixed(1)}%`;
            document.getElementById('total-requests').textContent = networkMetrics.total_requests;
            document.getElementById('uptime').textContent = 
                `${Math.floor(networkMetrics.network_uptime)}s`;
            
            // 更新智能体状态
            const agentMetrics = data.agent_metrics;
            for (const [agentId, metrics] of Object.entries(agentMetrics)) {
                const agentElement = document.getElementById(`agent-${agentId}`);
                const indicator = agentElement.querySelector('.health-indicator');
                const valueElement = agentElement.querySelector('.metric-value');
                
                if (metrics.status === 'active') {
                    indicator.className = 'health-indicator health-healthy';
                    valueElement.textContent = '在线';
                } else {
                    indicator.className = 'health-indicator health-critical';
                    valueElement.textContent = '离线';
                }
            }
            
            // 更新实时指标
            document.getElementById('avg-response-time').textContent = 
                `${(networkMetrics.avg_response_time * 1000).toFixed(0)}ms`;
            document.getElementById('peak-concurrent').textContent = 
                networkMetrics.peak_concurrent_requests;
            document.getElementById('error-rate').textContent = 
                `${((1 - networkMetrics.success_rate) * 100).toFixed(1)}%`;
            
            // 更新图表
            updateChart(networkMetrics);
        });
        
        socket.on('health_check_result', function(data) {
            const healthElement = document.getElementById('overall-health');
            const issuesElement = document.getElementById('health-issues');
            
            healthElement.textContent = data.overall_health;
            healthElement.className = `metric-value health-${data.overall_health}`;
            
            issuesElement.innerHTML = '';
            if (data.issues && data.issues.length > 0) {
                data.issues.forEach(issue => {
                    const issueElement = document.createElement('div');
                    issueElement.className = 'metric-row';
                    issueElement.innerHTML = `
                        <span class="metric-label">⚠️ ${issue}</span>
                    `;
                    issuesElement.appendChild(issueElement);
                });
            }
            
            addLog('info', `健康检查完成: ${data.overall_health}`);
        });
        
        socket.on('performance_test_result', function(data) {
            addLog('info', `性能测试完成: 成功率 ${(data.success_rate * 100).toFixed(1)}%`);
        });
        
        socket.on('export_complete', function(data) {
            addLog('info', `数据导出完成: ${data.filename}`);
        });
        
        socket.on('error', function(data) {
            addLog('error', `错误: ${data.message}`);
        });
        
        // 页面加载完成后初始化
        document.addEventListener('DOMContentLoaded', function() {
            initChart();
            addLog('info', '仪表板已加载，准备就绪');
        });
    </script>
</body>
</html>
"""

class DashboardServer:
    """仪表板服务器"""
    
    def __init__(self):
        self.monitor = None
        self.monitoring_active = False
        self.metrics_thread = None
        
    async def start_monitoring(self):
        """启动监控"""
        try:
            if not self.monitor:
                self.monitor = A2ANetworkMonitor()
            
            await self.monitor.start_monitoring()
            self.monitoring_active = True
            
            # 启动指标收集线程
            if not self.metrics_thread or not self.metrics_thread.is_alive():
                self.metrics_thread = threading.Thread(target=self._metrics_loop)
                self.metrics_thread.daemon = True
                self.metrics_thread.start()
            
            return {"success": True}
            
        except Exception as e:
            logger.error(f"启动监控失败: {e}")
            return {"success": False, "error": str(e)}
    
    async def stop_monitoring(self):
        """停止监控"""
        try:
            if self.monitor:
                await self.monitor.stop_monitoring()
            
            self.monitoring_active = False
            return {"success": True}
            
        except Exception as e:
            logger.error(f"停止监控失败: {e}")
            return {"success": False, "error": str(e)}
    
    def _metrics_loop(self):
        """指标收集循环"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        while self.monitoring_active:
            try:
                if self.monitor:
                    metrics = loop.run_until_complete(self.monitor.collect_metrics())
                    socketio.emit('metrics_update', metrics)
                
                time.sleep(5)  # 每5秒更新一次
                
            except Exception as e:
                logger.error(f"指标收集失败: {e}")
                time.sleep(10)
        
        loop.close()

# 全局仪表板实例
dashboard = DashboardServer()

@app.route('/')
def index():
    """主页"""
    return render_template_string(DASHBOARD_TEMPLATE)

@app.route('/api/status')
def api_status():
    """API 状态"""
    return jsonify({
        "status": "active" if dashboard.monitoring_active else "inactive",
        "timestamp": datetime.now().isoformat()
    })

@socketio.on('start_monitoring')
def handle_start_monitoring():
    """处理启动监控请求"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(dashboard.start_monitoring())
        if result["success"]:
            emit('monitoring_started', {"message": "监控已启动"})
        else:
            emit('error', {"message": result["error"]})
    except Exception as e:
        emit('error', {"message": str(e)})
    finally:
        loop.close()

@socketio.on('stop_monitoring')
def handle_stop_monitoring():
    """处理停止监控请求"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(dashboard.stop_monitoring())
        if result["success"]:
            emit('monitoring_stopped', {"message": "监控已停止"})
        else:
            emit('error', {"message": result["error"]})
    except Exception as e:
        emit('error', {"message": str(e)})
    finally:
        loop.close()

@socketio.on('health_check')
def handle_health_check():
    """处理健康检查请求"""
    if not dashboard.monitor:
        emit('error', {"message": "监控器未初始化"})
        return
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        health_result = loop.run_until_complete(dashboard.monitor.health_check())
        emit('health_check_result', health_result)
    except Exception as e:
        emit('error', {"message": str(e)})
    finally:
        loop.close()

@socketio.on('performance_test')
def handle_performance_test():
    """处理性能测试请求"""
    if not dashboard.monitor:
        emit('error', {"message": "监控器未初始化"})
        return
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        test_requests = [{
            "user_id": "test_user",
            "message": "测试请求",
            "type": "general"
        }]
        
        # 测试所有智能体
        overall_results = []
        for agent_id in ["xiaoai", "xiaoke", "laoke", "soer"]:
            result = loop.run_until_complete(
                dashboard.monitor.test_agent_performance(agent_id, test_requests)
            )
            overall_results.append(result)
        
        # 计算总体成功率
        total_success = sum(r.get("successful_count", 0) for r in overall_results)
        total_tests = sum(r.get("test_count", 0) for r in overall_results)
        overall_success_rate = total_success / total_tests if total_tests > 0 else 0
        
        emit('performance_test_result', {
            "success_rate": overall_success_rate,
            "results": overall_results
        })
        
    except Exception as e:
        emit('error', {"message": str(e)})
    finally:
        loop.close()

@socketio.on('export_metrics')
def handle_export_metrics():
    """处理导出指标请求"""
    if not dashboard.monitor:
        emit('error', {"message": "监控器未初始化"})
        return
    
    try:
        filename = dashboard.monitor.export_metrics()
        emit('export_complete', {"filename": filename})
    except Exception as e:
        emit('error', {"message": str(e)})

def run_dashboard(host='0.0.0.0', port=5000, debug=False):
    """运行仪表板服务器"""
    print(f"🌐 启动索克生活 A2A 智能体网络监控仪表板")
    print(f"📍 访问地址: http://{host}:{port}")
    print(f"🔧 调试模式: {'开启' if debug else '关闭'}")
    
    socketio.run(app, host=host, port=port, debug=debug)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='索克生活 A2A 智能体网络监控仪表板')
    parser.add_argument('--host', default='0.0.0.0', help='服务器主机地址')
    parser.add_argument('--port', type=int, default=5000, help='服务器端口')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)
    run_dashboard(host=args.host, port=args.port, debug=args.debug) 