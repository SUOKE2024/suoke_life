#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
索克生活人工审核 Web 仪表板
Suoke Life Human Review Web Dashboard

为审核员提供专用的审核界面和管理工具
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

from human_review_a2a_agent import create_human_review_a2a_agent, ReviewStatus, ReviewPriority

logger = logging.getLogger(__name__)

# Flask 应用
app = Flask(__name__)
app.config['SECRET_KEY'] = 'suoke_life_human_review_dashboard'
socketio = SocketIO(app, cors_allowed_origins="*")

# 全局审核智能体实例
review_agent = None

# HTML 模板
REVIEW_DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>索克生活人工审核仪表板</title>
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
            background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
            color: #333;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1600px;
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
        
        .stats-bar {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: rgba(255,255,255,0.95);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }
        
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .stat-label {
            color: #666;
            font-size: 0.9em;
        }
        
        .urgent { color: #e74c3c; }
        .high { color: #f39c12; }
        .normal { color: #3498db; }
        .low { color: #95a5a6; }
        
        .main-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }
        
        .left-panel, .right-panel {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        
        .card {
            background: rgba(255,255,255,0.95);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }
        
        .card h3 {
            color: #2c3e50;
            margin-bottom: 20px;
            font-size: 1.3em;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 10px;
        }
        
        .task-queue {
            max-height: 400px;
            overflow-y: auto;
        }
        
        .task-item {
            border: 1px solid #ecf0f1;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            transition: all 0.3s ease;
        }
        
        .task-item:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }
        
        .task-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .task-id {
            font-weight: bold;
            color: #2c3e50;
        }
        
        .task-priority {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
            color: white;
        }
        
        .priority-urgent { background-color: #e74c3c; }
        .priority-high { background-color: #f39c12; }
        .priority-normal { background-color: #3498db; }
        .priority-low { background-color: #95a5a6; }
        
        .task-content {
            background: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            font-size: 0.9em;
        }
        
        .task-actions {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }
        
        .btn {
            padding: 8px 16px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.9em;
            transition: all 0.3s ease;
        }
        
        .btn-approve {
            background-color: #27ae60;
            color: white;
        }
        
        .btn-reject {
            background-color: #e74c3c;
            color: white;
        }
        
        .btn-revise {
            background-color: #f39c12;
            color: white;
        }
        
        .btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }
        
        .reviewer-status {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
        }
        
        .reviewer-card {
            border: 1px solid #ecf0f1;
            border-radius: 10px;
            padding: 15px;
        }
        
        .reviewer-name {
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        }
        
        .reviewer-info {
            display: flex;
            justify-content: space-between;
            margin-bottom: 5px;
            font-size: 0.9em;
        }
        
        .utilization-bar {
            width: 100%;
            height: 8px;
            background-color: #ecf0f1;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 10px;
        }
        
        .utilization-fill {
            height: 100%;
            background: linear-gradient(90deg, #27ae60 0%, #f39c12 70%, #e74c3c 100%);
            transition: width 0.3s ease;
        }
        
        .review-form {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
            display: none;
        }
        
        .form-group {
            margin-bottom: 15px;
        }
        
        .form-label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #2c3e50;
        }
        
        .form-control {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 0.9em;
        }
        
        .form-control:focus {
            outline: none;
            border-color: #3498db;
            box-shadow: 0 0 5px rgba(52, 152, 219, 0.3);
        }
        
        textarea.form-control {
            resize: vertical;
            min-height: 80px;
        }
        
        .chart-container {
            position: relative;
            height: 300px;
            margin-top: 20px;
        }
        
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 5px;
            color: white;
            font-weight: bold;
            z-index: 1000;
            transform: translateX(400px);
            transition: transform 0.3s ease;
        }
        
        .notification.show {
            transform: translateX(0);
        }
        
        .notification.success { background-color: #27ae60; }
        .notification.error { background-color: #e74c3c; }
        .notification.warning { background-color: #f39c12; }
        .notification.info { background-color: #3498db; }
        
        @media (max-width: 768px) {
            .main-content {
                grid-template-columns: 1fr;
            }
            
            .stats-bar {
                grid-template-columns: repeat(2, 1fr);
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 索克生活人工审核仪表板</h1>
            <p>专业审核员工作台 - 确保医疗健康建议的安全性和准确性</p>
        </div>
        
        <div class="stats-bar">
            <div class="stat-card">
                <div class="stat-value urgent" id="urgent-count">0</div>
                <div class="stat-label">紧急任务</div>
            </div>
            <div class="stat-card">
                <div class="stat-value high" id="high-count">0</div>
                <div class="stat-label">高优先级</div>
            </div>
            <div class="stat-card">
                <div class="stat-value normal" id="pending-count">0</div>
                <div class="stat-label">待审核</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="in-progress-count">0</div>
                <div class="stat-label">审核中</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="completed-today">0</div>
                <div class="stat-label">今日完成</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="avg-time">0</div>
                <div class="stat-label">平均用时(分钟)</div>
            </div>
        </div>
        
        <div class="main-content">
            <div class="left-panel">
                <div class="card">
                    <h3>📋 待审核任务队列</h3>
                    <div class="task-queue" id="task-queue">
                        <div class="task-item">
                            <div class="task-header">
                                <span class="task-id">暂无任务</span>
                            </div>
                            <div class="task-content">
                                系统正在加载审核任务...
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <h3>📝 审核表单</h3>
                    <div class="review-form" id="review-form">
                        <div class="form-group">
                            <label class="form-label">任务ID</label>
                            <input type="text" class="form-control" id="review-task-id" readonly>
                        </div>
                        <div class="form-group">
                            <label class="form-label">审核决定</label>
                            <select class="form-control" id="review-decision">
                                <option value="approved">通过</option>
                                <option value="rejected">拒绝</option>
                                <option value="needs_revision">需要修改</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="form-label">审核意见</label>
                            <textarea class="form-control" id="review-comments" placeholder="请输入审核意见..."></textarea>
                        </div>
                        <div class="form-group">
                            <label class="form-label">修改建议 (可选)</label>
                            <textarea class="form-control" id="review-suggestions" placeholder="如需修改，请提供具体建议..."></textarea>
                        </div>
                        <div class="task-actions">
                            <button class="btn btn-approve" onclick="submitReview()">提交审核</button>
                            <button class="btn" onclick="cancelReview()">取消</button>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="right-panel">
                <div class="card">
                    <h3>👥 审核员状态</h3>
                    <div class="reviewer-status" id="reviewer-status">
                        <div class="reviewer-card">
                            <div class="reviewer-name">加载中...</div>
                            <div class="reviewer-info">
                                <span>状态:</span>
                                <span>--</span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <h3>📊 审核统计</h3>
                    <div class="chart-container">
                        <canvas id="review-chart"></canvas>
                    </div>
                </div>
                
                <div class="card">
                    <h3>🔔 实时通知</h3>
                    <div id="notifications-panel" style="max-height: 200px; overflow-y: auto;">
                        <div style="color: #666; text-align: center; padding: 20px;">
                            暂无通知
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const socket = io();
        let reviewChart = null;
        let currentReviewTask = null;
        
        // 初始化图表
        function initChart() {
            const ctx = document.getElementById('review-chart').getContext('2d');
            reviewChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['已通过', '已拒绝', '需修改', '待审核'],
                    datasets: [{
                        data: [0, 0, 0, 0],
                        backgroundColor: [
                            '#27ae60',
                            '#e74c3c',
                            '#f39c12',
                            '#3498db'
                        ],
                        borderWidth: 2,
                        borderColor: '#fff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        }
        
        // 显示通知
        function showNotification(message, type = 'info') {
            const notification = document.createElement('div');
            notification.className = `notification ${type}`;
            notification.textContent = message;
            document.body.appendChild(notification);
            
            setTimeout(() => notification.classList.add('show'), 100);
            setTimeout(() => {
                notification.classList.remove('show');
                setTimeout(() => document.body.removeChild(notification), 300);
            }, 3000);
        }
        
        // 添加通知到面板
        function addNotificationToPanel(message, type = 'info') {
            const panel = document.getElementById('notifications-panel');
            const notification = document.createElement('div');
            notification.style.cssText = `
                padding: 10px;
                margin-bottom: 10px;
                border-radius: 5px;
                border-left: 4px solid ${type === 'success' ? '#27ae60' : type === 'error' ? '#e74c3c' : '#3498db'};
                background: #f8f9fa;
                font-size: 0.9em;
            `;
            notification.innerHTML = `
                <div style="font-weight: bold; margin-bottom: 5px;">${new Date().toLocaleTimeString()}</div>
                <div>${message}</div>
            `;
            
            panel.insertBefore(notification, panel.firstChild);
            
            // 保持最近10条通知
            while (panel.children.length > 10) {
                panel.removeChild(panel.lastChild);
            }
        }
        
        // 开始审核任务
        function startReview(taskId) {
            currentReviewTask = taskId;
            document.getElementById('review-task-id').value = taskId;
            document.getElementById('review-form').style.display = 'block';
            document.getElementById('review-comments').focus();
            
            showNotification(`开始审核任务: ${taskId}`, 'info');
        }
        
        // 提交审核
        function submitReview() {
            if (!currentReviewTask) {
                showNotification('请先选择要审核的任务', 'error');
                return;
            }
            
            const decision = document.getElementById('review-decision').value;
            const comments = document.getElementById('review-comments').value;
            const suggestions = document.getElementById('review-suggestions').value;
            
            if (!comments.trim()) {
                showNotification('请输入审核意见', 'error');
                return;
            }
            
            socket.emit('submit_review', {
                task_id: currentReviewTask,
                decision: decision,
                comments: comments,
                suggestions: suggestions
            });
            
            showNotification('正在提交审核结果...', 'info');
        }
        
        // 取消审核
        function cancelReview() {
            currentReviewTask = null;
            document.getElementById('review-form').style.display = 'none';
            document.getElementById('review-comments').value = '';
            document.getElementById('review-suggestions').value = '';
        }
        
        // 更新任务队列
        function updateTaskQueue(tasks) {
            const queue = document.getElementById('task-queue');
            
            if (!tasks || tasks.length === 0) {
                queue.innerHTML = `
                    <div class="task-item">
                        <div class="task-header">
                            <span class="task-id">暂无待审核任务</span>
                        </div>
                        <div class="task-content">
                            所有任务已处理完毕
                        </div>
                    </div>
                `;
                return;
            }
            
            queue.innerHTML = tasks.map(task => `
                <div class="task-item">
                    <div class="task-header">
                        <span class="task-id">${task.task_id}</span>
                        <span class="task-priority priority-${task.priority}">${task.priority.toUpperCase()}</span>
                    </div>
                    <div class="task-content">
                        <strong>类型:</strong> ${task.type}<br>
                        <strong>创建时间:</strong> ${new Date(task.created_at).toLocaleString()}<br>
                        <strong>内容:</strong> ${JSON.stringify(task.content, null, 2).substring(0, 200)}...
                    </div>
                    <div class="task-actions">
                        <button class="btn btn-approve" onclick="startReview('${task.task_id}')">开始审核</button>
                    </div>
                </div>
            `).join('');
        }
        
        // 更新审核员状态
        function updateReviewerStatus(reviewers) {
            const container = document.getElementById('reviewer-status');
            
            container.innerHTML = Object.entries(reviewers).map(([id, reviewer]) => `
                <div class="reviewer-card">
                    <div class="reviewer-name">${reviewer.name}</div>
                    <div class="reviewer-info">
                        <span>状态:</span>
                        <span style="color: ${reviewer.is_available ? '#27ae60' : '#e74c3c'}">
                            ${reviewer.is_available ? '在线' : '离线'}
                        </span>
                    </div>
                    <div class="reviewer-info">
                        <span>当前任务:</span>
                        <span>${reviewer.current_tasks}/${reviewer.max_tasks}</span>
                    </div>
                    <div class="utilization-bar">
                        <div class="utilization-fill" style="width: ${reviewer.utilization * 100}%"></div>
                    </div>
                </div>
            `).join('');
        }
        
        // 更新统计数据
        function updateStatistics(stats) {
            document.getElementById('urgent-count').textContent = stats.urgent_tasks || 0;
            document.getElementById('high-count').textContent = stats.high_priority_tasks || 0;
            document.getElementById('pending-count').textContent = stats.total_pending || 0;
            document.getElementById('in-progress-count').textContent = stats.total_in_progress || 0;
            document.getElementById('completed-today').textContent = stats.completed_today || 0;
            document.getElementById('avg-time').textContent = Math.round(stats.average_review_time || 0);
            
            // 更新图表
            if (reviewChart && stats.overall_statistics) {
                const overall = stats.overall_statistics;
                reviewChart.data.datasets[0].data = [
                    overall.approved_count || 0,
                    overall.rejected_count || 0,
                    overall.needs_revision_count || 0,
                    overall.pending_count || 0
                ];
                reviewChart.update();
            }
        }
        
        // Socket 事件处理
        socket.on('connect', function() {
            showNotification('已连接到审核系统', 'success');
            addNotificationToPanel('审核系统连接成功', 'success');
        });
        
        socket.on('disconnect', function() {
            showNotification('与审核系统断开连接', 'error');
            addNotificationToPanel('审核系统连接断开', 'error');
        });
        
        socket.on('dashboard_update', function(data) {
            updateTaskQueue(data.recent_tasks);
            updateReviewerStatus(data.reviewer_statistics);
            updateStatistics(data.queue_statistics);
        });
        
        socket.on('new_task', function(data) {
            showNotification(`新的审核任务: ${data.task_id}`, 'info');
            addNotificationToPanel(`新任务 ${data.task_id} 需要审核`, 'info');
        });
        
        socket.on('review_submitted', function(data) {
            if (data.success) {
                showNotification('审核结果已提交', 'success');
                addNotificationToPanel(`任务 ${data.task_id} 审核完成`, 'success');
                cancelReview();
            } else {
                showNotification(`提交失败: ${data.error}`, 'error');
            }
        });
        
        socket.on('error', function(data) {
            showNotification(`错误: ${data.message}`, 'error');
            addNotificationToPanel(`系统错误: ${data.message}`, 'error');
        });
        
        // 页面加载完成后初始化
        document.addEventListener('DOMContentLoaded', function() {
            initChart();
            showNotification('人工审核仪表板已加载', 'success');
            
            // 请求初始数据
            socket.emit('request_dashboard_data');
        });
        
        // 定期刷新数据
        setInterval(() => {
            socket.emit('request_dashboard_data');
        }, 10000); // 每10秒刷新一次
    </script>
</body>
</html>
"""

class ReviewDashboardServer:
    """审核仪表板服务器"""
    
    def __init__(self):
        self.review_agent = create_human_review_a2a_agent()
        
    async def get_dashboard_data(self):
        """获取仪表板数据"""
        try:
            dashboard_data = await self.review_agent.get_review_dashboard()
            return dashboard_data
        except Exception as e:
            logger.error(f"获取仪表板数据失败: {e}")
            return {"error": str(e)}
    
    async def submit_review_result(self, task_id: str, reviewer_id: str, decision: str, comments: str, suggestions: str = ""):
        """提交审核结果"""
        try:
            # 构建修改内容
            revised_content = None
            if decision == "needs_revision" and suggestions:
                revised_content = {"suggestions": suggestions}
            
            result = await self.review_agent.complete_review(
                task_id=task_id,
                reviewer_id=reviewer_id,
                decision=decision,
                comments=comments,
                revised_content=revised_content
            )
            
            return result
        except Exception as e:
            logger.error(f"提交审核结果失败: {e}")
            return {"error": str(e)}

# 全局仪表板实例
dashboard_server = ReviewDashboardServer()

@app.route('/')
def index():
    """主页"""
    return render_template_string(REVIEW_DASHBOARD_TEMPLATE)

@app.route('/api/dashboard')
def api_dashboard():
    """API 获取仪表板数据"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        data = loop.run_until_complete(dashboard_server.get_dashboard_data())
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)})
    finally:
        loop.close()

@socketio.on('request_dashboard_data')
def handle_request_dashboard_data():
    """处理仪表板数据请求"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        data = loop.run_until_complete(dashboard_server.get_dashboard_data())
        emit('dashboard_update', data)
    except Exception as e:
        emit('error', {"message": str(e)})
    finally:
        loop.close()

@socketio.on('submit_review')
def handle_submit_review(data):
    """处理审核提交"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        task_id = data.get('task_id')
        decision = data.get('decision')
        comments = data.get('comments')
        suggestions = data.get('suggestions', '')
        
        # 这里应该从会话中获取审核员ID，简化为使用默认值
        reviewer_id = "dr_zhang"  # 实际应用中需要身份验证
        
        result = loop.run_until_complete(
            dashboard_server.submit_review_result(
                task_id=task_id,
                reviewer_id=reviewer_id,
                decision=decision,
                comments=comments,
                suggestions=suggestions
            )
        )
        
        if "error" not in result:
            emit('review_submitted', {"success": True, "task_id": task_id})
            # 通知其他客户端更新
            socketio.emit('dashboard_update', loop.run_until_complete(dashboard_server.get_dashboard_data()))
        else:
            emit('review_submitted', {"success": False, "error": result["error"]})
            
    except Exception as e:
        emit('review_submitted', {"success": False, "error": str(e)})
    finally:
        loop.close()

def run_review_dashboard(host='127.0.0.1', port=5001, debug=False):
    """运行审核仪表板服务器"""
    print(f"🔍 启动索克生活人工审核仪表板")
    print(f"📍 访问地址: http://{host}:{port}")
    print(f"🔧 调试模式: {'开启' if debug else '关闭'}")
    print(f"👥 审核员专用界面")
    print("=" * 60)
    
    socketio.run(app, host=host, port=port, debug=debug)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='索克生活人工审核仪表板')
    parser.add_argument('--host', default='127.0.0.1', help='服务器主机地址')
    parser.add_argument('--port', type=int, default=5001, help='服务器端口')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)
    run_review_dashboard(host=args.host, port=args.port, debug=args.debug) 