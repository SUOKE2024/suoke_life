#!/usr/bin/env python3
"""
望诊服务负载测试脚本
- 使用Locust框架实现gRPC服务的负载测试
- 支持多种测试场景模拟真实用户行为
- 收集关键性能指标并生成报告
"""

import os
import sys
import time
import yaml
import logging
import argparse
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
import grpc
import cv2
import matplotlib.pyplot as plt
from locust import User, task, between, events
from locust.env import Environment
from locust.stats import RequestStats, stats_printer
from locust.runners import Runner

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# 导入gRPC相关模块
from api.grpc import look_service_pb2, look_service_pb2_grpc

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("look_service_load_test")

class GrpcClient:
    """gRPC客户端封装"""
    
    def __init__(self, host: str):
        self.host = host
        self.channel = grpc.insecure_channel(self.host)
        self.stub = look_service_pb2_grpc.LookServiceStub(self.channel)
        
    def analyze_tongue(self, image_data: bytes, user_id: str, analysis_type: int, 
                        save_result: bool = True, metadata: Optional[Dict[str, str]] = None) -> Any:
        """调用舌象分析接口"""
        request = look_service_pb2.TongueAnalysisRequest(
            image=image_data,
            user_id=user_id,
            analysis_type=analysis_type,
            save_result=save_result
        )
        
        if metadata:
            for key, value in metadata.items():
                request.metadata[key] = value
                
        return self.stub.AnalyzeTongue(request)
    
    def analyze_face(self, image_data: bytes, user_id: str, analysis_type: int,
                      save_result: bool = True, metadata: Optional[Dict[str, str]] = None) -> Any:
        """调用面色分析接口"""
        request = look_service_pb2.FaceAnalysisRequest(
            image=image_data,
            user_id=user_id,
            analysis_type=analysis_type,
            save_result=save_result
        )
        
        if metadata:
            for key, value in metadata.items():
                request.metadata[key] = value
                
        return self.stub.AnalyzeFace(request)
    
    def analyze_body(self, image_data: bytes, user_id: str, analysis_type: int,
                      save_result: bool = True, metadata: Optional[Dict[str, str]] = None) -> Any:
        """调用形体分析接口"""
        request = look_service_pb2.BodyAnalysisRequest(
            image=image_data,
            user_id=user_id,
            analysis_type=analysis_type,
            save_result=save_result
        )
        
        if metadata:
            for key, value in metadata.items():
                request.metadata[key] = value
                
        return self.stub.AnalyzeBody(request)
    
    def get_analysis_history(self, user_id: str, analysis_type: str, limit: int = 10,
                              start_time: int = 0, end_time: int = 0) -> Any:
        """获取分析历史记录"""
        if end_time == 0:
            end_time = int(time.time())
            
        request = look_service_pb2.AnalysisHistoryRequest(
            user_id=user_id,
            analysis_type=analysis_type,
            limit=limit,
            start_time=start_time,
            end_time=end_time
        )
        
        return self.stub.GetAnalysisHistory(request)
    
    def compare_analysis(self, user_id: str, analysis_type: str, 
                          first_analysis_id: str, second_analysis_id: str) -> Any:
        """比较两次分析结果"""
        request = look_service_pb2.CompareAnalysisRequest(
            user_id=user_id,
            analysis_type=analysis_type,
            first_analysis_id=first_analysis_id,
            second_analysis_id=second_analysis_id
        )
        
        return self.stub.CompareAnalysis(request)
    
    def health_check(self, include_details: bool = False) -> Any:
        """健康检查"""
        request = look_service_pb2.HealthCheckRequest(
            include_details=include_details
        )
        
        return self.stub.HealthCheck(request)
    
    def close(self):
        """关闭连接"""
        self.channel.close()


class LookServiceUser(User):
    """望诊服务负载测试用户"""
    
    # 模拟用户间隔1-5秒发送请求
    wait_time = between(1, 5)
    
    def __init__(self, environment: Environment):
        super().__init__(environment)
        
        # 从环境变量中获取配置
        self.config = environment.parsed_options.config
        self.host = self.config['service_urls']['look_service']
        
        # 创建gRPC客户端
        self.client = GrpcClient(self.host)
        
        # 加载测试图像
        self.test_images = self._load_test_images()
        
        # 加载测试参数
        self.test_params = self._load_test_params()
        
    def _load_test_images(self) -> Dict[str, List[bytes]]:
        """加载测试图像数据"""
        images = {
            'tongue': [],
            'face': [],
            'body': []
        }
        
        # 加载舌象图像
        tongue_files = self.config['scenarios']['tongue_analysis']['scenarios'][0]['request_files']
        for file_path in tongue_files:
            try:
                img = cv2.imread(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), file_path))
                if img is not None:
                    _, img_bytes = cv2.imencode('.jpg', img)
                    images['tongue'].append(img_bytes.tobytes())
                else:
                    logger.warning(f"无法加载图像: {file_path}")
            except Exception as e:
                logger.error(f"加载图像失败 {file_path}: {e}")
        
        # 加载面色图像
        face_files = self.config['scenarios']['face_analysis']['scenarios'][0]['request_files']
        for file_path in face_files:
            try:
                img = cv2.imread(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), file_path))
                if img is not None:
                    _, img_bytes = cv2.imencode('.jpg', img)
                    images['face'].append(img_bytes.tobytes())
                else:
                    logger.warning(f"无法加载图像: {file_path}")
            except Exception as e:
                logger.error(f"加载图像失败 {file_path}: {e}")
        
        # 加载形体图像
        body_files = self.config['scenarios']['body_analysis']['scenarios'][0]['request_files']
        for file_path in body_files:
            try:
                img = cv2.imread(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), file_path))
                if img is not None:
                    _, img_bytes = cv2.imencode('.jpg', img)
                    images['body'].append(img_bytes.tobytes())
                else:
                    logger.warning(f"无法加载图像: {file_path}")
            except Exception as e:
                logger.error(f"加载图像失败 {file_path}: {e}")
        
        # 如果任一类图像为空，使用随机生成的图像作为备用
        for image_type in images:
            if not images[image_type]:
                logger.warning(f"未能加载任何{image_type}图像，将使用随机生成的图像")
                random_img = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
                _, img_bytes = cv2.imencode('.jpg', random_img)
                images[image_type].append(img_bytes.tobytes())
        
        return images
    
    def _load_test_params(self) -> Dict[str, Dict[str, List[Any]]]:
        """加载测试参数"""
        params = {
            'tongue': {
                'user_id': self.config['scenarios']['tongue_analysis']['scenarios'][0]['metadata']['user_id'],
                'analysis_type': self.config['scenarios']['tongue_analysis']['scenarios'][0]['metadata']['analysis_type']
            },
            'face': {
                'user_id': self.config['scenarios']['face_analysis']['scenarios'][0]['metadata']['user_id'],
                'analysis_type': self.config['scenarios']['face_analysis']['scenarios'][0]['metadata']['analysis_type']
            },
            'body': {
                'user_id': self.config['scenarios']['body_analysis']['scenarios'][0]['metadata']['user_id'],
                'analysis_type': self.config['scenarios']['body_analysis']['scenarios'][0]['metadata']['analysis_type']
            },
            'history': {
                'user_id': self.config['scenarios']['analysis_history']['scenarios'][0]['params']['user_id'],
                'analysis_type': self.config['scenarios']['analysis_history']['scenarios'][0]['params']['analysis_type'],
                'limit': self.config['scenarios']['analysis_history']['scenarios'][0]['params']['limit']
            },
            'compare': {
                'user_id': self.config['scenarios']['compare_analysis']['scenarios'][0]['params']['user_id'],
                'analysis_type': self.config['scenarios']['compare_analysis']['scenarios'][0]['params']['analysis_type'],
                'first_analysis_id': self.config['scenarios']['compare_analysis']['scenarios'][0]['params']['first_analysis_id'],
                'second_analysis_id': self.config['scenarios']['compare_analysis']['scenarios'][0]['params']['second_analysis_id']
            }
        }
        
        return params
    
    def on_start(self):
        """用户启动时执行的操作"""
        # 确保gRPC连接可用
        try:
            health_response = self.client.health_check()
            if health_response.status != look_service_pb2.HealthCheckResponse.Status.SERVING:
                logger.error(f"服务健康检查失败: {health_response.status}")
        except Exception as e:
            logger.error(f"连接服务失败: {e}")
    
    def on_stop(self):
        """用户停止时执行的操作"""
        self.client.close()
    
    @task(40)
    def analyze_tongue_task(self):
        """舌象分析任务 (40% 的权重)"""
        # 随机选择一张舌象图像
        image_data = np.random.choice(self.test_images['tongue'])
        
        # 随机选择用户ID和分析类型
        user_id = np.random.choice(self.test_params['tongue']['user_id'])
        analysis_type = np.random.choice(self.test_params['tongue']['analysis_type'])
        
        # 添加会话元数据
        metadata = {
            'session_id': f"test_session_{int(time.time())}",
            'device_type': np.random.choice(['mobile', 'tablet', 'web']),
            'app_version': np.random.choice(['1.0.0', '1.1.0', '1.2.0'])
        }
        
        # 记录请求开始时间
        start_time = time.time()
        
        try:
            # 发送请求并计时
            response = self.client.analyze_tongue(image_data, user_id, analysis_type, True, metadata)
            # 请求成功
            self.environment.events.request.fire(
                request_type="grpc",
                name="AnalyzeTongue",
                response_time=(time.time() - start_time) * 1000,
                response_length=len(response.SerializeToString()),
                exception=None,
            )
        except Exception as e:
            # 请求失败
            self.environment.events.request.fire(
                request_type="grpc",
                name="AnalyzeTongue",
                response_time=(time.time() - start_time) * 1000,
                response_length=0,
                exception=e,
            )
    
    @task(40)
    def analyze_face_task(self):
        """面色分析任务 (40% 的权重)"""
        # 随机选择一张面色图像
        image_data = np.random.choice(self.test_images['face'])
        
        # 随机选择用户ID和分析类型
        user_id = np.random.choice(self.test_params['face']['user_id'])
        analysis_type = np.random.choice(self.test_params['face']['analysis_type'])
        
        # 添加会话元数据
        metadata = {
            'session_id': f"test_session_{int(time.time())}",
            'device_type': np.random.choice(['mobile', 'tablet', 'web']),
            'app_version': np.random.choice(['1.0.0', '1.1.0', '1.2.0'])
        }
        
        # 记录请求开始时间
        start_time = time.time()
        
        try:
            # 发送请求并计时
            response = self.client.analyze_face(image_data, user_id, analysis_type, True, metadata)
            # 请求成功
            self.environment.events.request.fire(
                request_type="grpc",
                name="AnalyzeFace",
                response_time=(time.time() - start_time) * 1000,
                response_length=len(response.SerializeToString()),
                exception=None,
            )
        except Exception as e:
            # 请求失败
            self.environment.events.request.fire(
                request_type="grpc",
                name="AnalyzeFace",
                response_time=(time.time() - start_time) * 1000,
                response_length=0,
                exception=e,
            )
    
    @task(10)
    def analyze_body_task(self):
        """形体分析任务 (10% 的权重)"""
        # 随机选择一张形体图像
        image_data = np.random.choice(self.test_images['body'])
        
        # 随机选择用户ID和分析类型
        user_id = np.random.choice(self.test_params['body']['user_id'])
        analysis_type = np.random.choice(self.test_params['body']['analysis_type'])
        
        # 添加会话元数据
        metadata = {
            'session_id': f"test_session_{int(time.time())}",
            'device_type': np.random.choice(['mobile', 'tablet', 'web']),
            'app_version': np.random.choice(['1.0.0', '1.1.0', '1.2.0'])
        }
        
        # 记录请求开始时间
        start_time = time.time()
        
        try:
            # 发送请求并计时
            response = self.client.analyze_body(image_data, user_id, analysis_type, True, metadata)
            # 请求成功
            self.environment.events.request.fire(
                request_type="grpc",
                name="AnalyzeBody",
                response_time=(time.time() - start_time) * 1000,
                response_length=len(response.SerializeToString()),
                exception=None,
            )
        except Exception as e:
            # 请求失败
            self.environment.events.request.fire(
                request_type="grpc",
                name="AnalyzeBody",
                response_time=(time.time() - start_time) * 1000,
                response_length=0,
                exception=e,
            )
    
    @task(5)
    def get_history_task(self):
        """获取历史记录任务 (5% 的权重)"""
        # 随机选择参数
        user_id = np.random.choice(self.test_params['history']['user_id'])
        analysis_type = np.random.choice(self.test_params['history']['analysis_type'])
        limit = np.random.choice(self.test_params['history']['limit'])
        
        # 生成随机时间范围 (过去30天内)
        end_time = int(time.time())
        start_time = end_time - (np.random.randint(1, 30) * 86400)  # 1-30天
        
        # 记录请求开始时间
        start_time_req = time.time()
        
        try:
            # 发送请求并计时
            response = self.client.get_analysis_history(user_id, analysis_type, limit, start_time, end_time)
            # 请求成功
            self.environment.events.request.fire(
                request_type="grpc",
                name="GetAnalysisHistory",
                response_time=(time.time() - start_time_req) * 1000,
                response_length=len(response.SerializeToString()),
                exception=None,
            )
        except Exception as e:
            # 请求失败
            self.environment.events.request.fire(
                request_type="grpc",
                name="GetAnalysisHistory",
                response_time=(time.time() - start_time_req) * 1000,
                response_length=0,
                exception=e,
            )
    
    @task(5)
    def compare_analysis_task(self):
        """比较分析任务 (5% 的权重)"""
        # 随机选择参数
        user_id = np.random.choice(self.test_params['compare']['user_id'])
        analysis_type = np.random.choice(self.test_params['compare']['analysis_type'])
        first_id = np.random.choice(self.test_params['compare']['first_analysis_id'])
        second_id = np.random.choice(self.test_params['compare']['second_analysis_id'])
        
        # 记录请求开始时间
        start_time = time.time()
        
        try:
            # 发送请求并计时
            response = self.client.compare_analysis(user_id, analysis_type, first_id, second_id)
            # 请求成功
            self.environment.events.request.fire(
                request_type="grpc",
                name="CompareAnalysis",
                response_time=(time.time() - start_time) * 1000,
                response_length=len(response.SerializeToString()),
                exception=None,
            )
        except Exception as e:
            # 请求失败
            self.environment.events.request.fire(
                request_type="grpc",
                name="CompareAnalysis",
                response_time=(time.time() - start_time) * 1000,
                response_length=0,
                exception=e,
            )


def generate_report(stats: RequestStats, config: Dict[str, Any], output_dir: str):
    """生成测试报告"""
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存统计数据为CSV
    stats_csv_path = os.path.join(output_dir, "stats.csv")
    with open(stats_csv_path, "w") as f:
        f.write("Name,Request Count,Failure Count,Median Response Time,Average Response Time,Min Response Time,Max Response Time,Average Content Size,RPS\n")
        for name, stat in stats.entries.items():
            f.write(f"{name},{stat.num_requests},{stat.num_failures},{stat.median_response_time},"
                    f"{stat.avg_response_time},{stat.min_response_time},{stat.max_response_time},"
                    f"{stat.avg_content_length},{stat.total_rps}\n")
    
    # 生成响应时间分布图
    plt.figure(figsize=(10, 6))
    for name, stat in stats.entries.items():
        if stat.response_times:
            response_times = sorted(stat.response_times.items())
            percentiles = [p[0] for p in response_times]
            times = [p[1] for p in response_times]
            plt.plot(percentiles, times, label=name)
    
    plt.xlabel('Percentile')
    plt.ylabel('Response Time (ms)')
    plt.title('Response Time Distribution')
    plt.legend()
    plt.grid()
    plt.savefig(os.path.join(output_dir, "response_time_distribution.png"))
    
    # 生成RPS图
    plt.figure(figsize=(10, 6))
    for name, stat in stats.entries.items():
        if hasattr(stat, 'total_rps_per_second') and stat.total_rps_per_second:
            times = sorted(stat.total_rps_per_second.keys())
            rpss = [stat.total_rps_per_second[t] for t in times]
            plt.plot(times, rpss, label=name)
    
    plt.xlabel('Time')
    plt.ylabel('Requests per Second')
    plt.title('RPS over Time')
    plt.legend()
    plt.grid()
    plt.savefig(os.path.join(output_dir, "rps_over_time.png"))
    
    # 生成HTML报告
    html_report_path = os.path.join(output_dir, "report.html")
    with open(html_report_path, "w") as f:
        f.write(f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Look Service 负载测试报告</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
                h1, h2, h3 {{ color: #333; }}
                table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
                .chart {{ margin: 20px 0; max-width: 100%; }}
                .summary {{ background-color: #e9f7ef; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                .failure {{ color: #c0392b; }}
                .success {{ color: #27ae60; }}
            </style>
        </head>
        <body>
            <h1>Look Service 负载测试报告</h1>
            <div class="summary">
                <h2>测试摘要</h2>
                <p><strong>测试时间:</strong> {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>测试持续时间:</strong> {config['global']['duration']}</p>
                <p><strong>最大虚拟用户数:</strong> {config['global']['max_vus']}</p>
                <p><strong>总请求数:</strong> {stats.total.num_requests}</p>
                <p><strong>失败请求数:</strong> {stats.total.num_failures}</p>
                <p><strong>失败率:</strong> <span class="{'failure' if stats.total.fail_ratio > 0.01 else 'success'}">{stats.total.fail_ratio:.2%}</span></p>
                <p><strong>平均RPS:</strong> {stats.total.total_rps:.2f}</p>
            </div>
            
            <h2>请求统计</h2>
            <table>
                <tr>
                    <th>接口名称</th>
                    <th>请求数</th>
                    <th>失败数</th>
                    <th>平均响应时间(ms)</th>
                    <th>中位数响应时间(ms)</th>
                    <th>最小响应时间(ms)</th>
                    <th>最大响应时间(ms)</th>
                    <th>RPS</th>
                </tr>
        """)
        
        for name, stat in stats.entries.items():
            f.write(f"""
                <tr>
                    <td>{name}</td>
                    <td>{stat.num_requests}</td>
                    <td>{stat.num_failures}</td>
                    <td>{stat.avg_response_time:.2f}</td>
                    <td>{stat.median_response_time:.2f}</td>
                    <td>{stat.min_response_time:.2f}</td>
                    <td>{stat.max_response_time:.2f}</td>
                    <td>{stat.total_rps:.2f}</td>
                </tr>
            """)
        
        f.write("""
            </table>
            
            <h2>响应时间分布</h2>
            <div class="chart">
                <img src="response_time_distribution.png" alt="Response Time Distribution" style="width:100%;">
            </div>
            
            <h2>RPS随时间变化</h2>
            <div class="chart">
                <img src="rps_over_time.png" alt="RPS over Time" style="width:100%;">
            </div>
            
            <h2>测试配置</h2>
            <pre>
        """)
        
        f.write(yaml.dump(config, default_flow_style=False))
        
        f.write("""
            </pre>
        </body>
        </html>
        """)
    
    logger.info(f"测试报告已生成: {html_report_path}")
    return html_report_path


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Look Service 负载测试工具")
    parser.add_argument('--config', '-c', type=str, 
                        default='test/performance/load_test_config.yaml',
                        help='配置文件路径')
    parser.add_argument('--duration', '-d', type=str, 
                        help='测试持续时间 (覆盖配置文件设置)')
    parser.add_argument('--users', '-u', type=int, 
                        help='虚拟用户数 (覆盖配置文件设置)')
    parser.add_argument('--output', '-o', type=str, 
                        help='输出目录 (覆盖配置文件设置)')
    parser.add_argument('--web-ui', '-w', action='store_true',
                        help='启动Web UI (默认: False)')
    parser.add_argument('--web-port', '-p', type=int, default=8089,
                        help='Web UI端口 (默认: 8089)')
    
    args = parser.parse_args()
    
    # 加载配置文件
    try:
        with open(args.config, 'r') as f:
            config = yaml.safe_load(f)
    except Exception as e:
        logger.error(f"加载配置文件失败: {e}")
        sys.exit(1)
    
    # 覆盖配置项
    if args.duration:
        config['global']['duration'] = args.duration
    if args.users:
        config['global']['max_vus'] = args.users
    if args.output:
        config['report']['output_dir'] = args.output
    
    # 创建Locust环境
    env = Environment(user_classes=[LookServiceUser])
    env.create_local_runner()
    
    # 将配置传递给用户类
    env.parsed_options = argparse.Namespace(config=config)
    
    # 启动测试
    try:
        # 设置用户数和孵化率
        user_count = config['global']['max_vus']
        spawn_rate = user_count / (60 if 'm' in config['global']['ramp_up'] else 
                                 int(config['global']['ramp_up'].replace('s', '')))
        
        # 解析持续时间
        if 'm' in config['global']['duration']:
            run_time = int(config['global']['duration'].replace('m', '')) * 60
        elif 's' in config['global']['duration']:
            run_time = int(config['global']['duration'].replace('s', ''))
        else:
            run_time = int(config['global']['duration'])
        
        # 使用Web UI或命令行运行
        if args.web_ui:
            # 启动Web UI
            env.create_web_ui(host="127.0.0.1", port=args.web_port)
            env.web_ui.update_config({"host": config['service_urls']['look_service']})
            env.runner.start(user_count, spawn_rate=spawn_rate)
            env.web_ui.start()
            env.runner.greenlet.join()
        else:
            # 设置统计数据打印器
            stats_printer_greenlet = env.create_worker_greenlet(
                lambda: stats_printer(env.stats, interval=5)
            )
            
            # 开始测试
            env.runner.start(user_count, spawn_rate=spawn_rate)
            logger.info(f"正在启动 {user_count} 个用户，孵化率: {spawn_rate} 用户/秒")
            
            # 运行指定时间
            env.runner.greenlet.join(timeout=run_time)
            
            # 生成报告
            output_dir = config['report']['output_dir']
            generate_report(env.stats, config, output_dir)
            
            # 停止统计数据打印器
            stats_printer_greenlet.kill(block=True)
    except KeyboardInterrupt:
        logger.info("测试被用户中断")
    finally:
        # 清理
        if env.runner:
            env.runner.quit()
        if hasattr(env, 'web_ui') and env.web_ui:
            env.web_ui.stop()
            
    logger.info("测试完成")


if __name__ == "__main__":
    main() 