#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
望诊服务性能测试脚本

测试服务在不同负载下的性能表现，包括响应时间、吞吐量等指标。
"""

import os
import sys
import time
import uuid
import statistics
import argparse
import concurrent.futures
import grpc
import cv2
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from api.grpc import look_service_pb2, look_service_pb2_grpc


class PerformanceTester:
    """望诊服务性能测试器"""
    
    def __init__(self, host="localhost", port=50053):
        """
        初始化性能测试器
        
        Args:
            host: 服务主机名
            port: 服务端口
        """
        self.host = host
        self.port = port
        self.channel = grpc.insecure_channel(f"{host}:{port}")
        self.stub = look_service_pb2_grpc.LookServiceStub(self.channel)
        
        # 创建测试图像
        self.face_image = self._create_face_test_image()
        self.body_image = self._create_body_test_image()
        
        # 性能测试结果
        self.results = {
            "face_analysis": [],
            "body_analysis": [],
            "get_face_analysis": [],
            "get_body_analysis": [],
            "get_history": []
        }
    
    def _create_face_test_image(self):
        """创建面部测试图像"""
        # 创建一个简单的彩色图像
        img = np.ones((200, 200, 3), dtype=np.uint8) * 200  # 浅灰色背景
        
        # 添加一个简单的面部图形（椭圆）
        cv2.ellipse(img, (100, 100), (60, 80), 0, 0, 360, (210, 170, 150), -1)  # 面部肤色
        
        # 添加眼睛
        cv2.circle(img, (70, 80), 10, (50, 50, 50), -1)  # 左眼
        cv2.circle(img, (130, 80), 10, (50, 50, 50), -1)  # 右眼
        
        # 添加鼻子
        cv2.ellipse(img, (100, 110), (10, 15), 0, 0, 360, (180, 140, 130), -1)
        
        # 添加嘴巴
        cv2.ellipse(img, (100, 140), (30, 10), 0, 0, 180, (150, 90, 90), 3)
        
        # 编码为JPEG
        _, buffer = cv2.imencode('.jpg', img)
        return buffer.tobytes()
    
    def _create_body_test_image(self):
        """创建身体测试图像"""
        # 创建一个简单的彩色图像
        img = np.ones((400, 200, 3), dtype=np.uint8) * 220  # 浅灰色背景
        
        # 头部
        cv2.circle(img, (100, 50), 30, (210, 170, 150), -1)
        
        # 躯干
        cv2.rectangle(img, (70, 80), (130, 220), (210, 170, 150), -1)
        
        # 手臂
        cv2.rectangle(img, (50, 90), (70, 180), (210, 170, 150), -1)  # 左臂
        cv2.rectangle(img, (130, 90), (150, 180), (210, 170, 150), -1)  # 右臂
        
        # 腿部
        cv2.rectangle(img, (80, 220), (95, 350), (210, 170, 150), -1)  # 左腿
        cv2.rectangle(img, (105, 220), (120, 350), (210, 170, 150), -1)  # 右腿
        
        # 编码为JPEG
        _, buffer = cv2.imencode('.jpg', img)
        return buffer.tobytes()
    
    def test_face_analysis(self, user_id):
        """
        测试面色分析性能
        
        Args:
            user_id: 测试用户ID
            
        Returns:
            元组 (响应时间, 分析ID)
        """
        request = look_service_pb2.FaceAnalysisRequest(
            user_id=user_id,
            image_data=self.face_image
        )
        
        start_time = time.time()
        try:
            response = self.stub.AnalyzeFace(request)
            elapsed = time.time() - start_time
            return elapsed, response.analysis_id
        except Exception as e:
            print(f"面色分析错误: {str(e)}")
            return time.time() - start_time, None
    
    def test_body_analysis(self, user_id):
        """
        测试形体分析性能
        
        Args:
            user_id: 测试用户ID
            
        Returns:
            元组 (响应时间, 分析ID)
        """
        request = look_service_pb2.BodyAnalysisRequest(
            user_id=user_id,
            image_data=self.body_image
        )
        
        start_time = time.time()
        try:
            response = self.stub.AnalyzeBody(request)
            elapsed = time.time() - start_time
            return elapsed, response.analysis_id
        except Exception as e:
            print(f"形体分析错误: {str(e)}")
            return time.time() - start_time, None
    
    def test_get_face_analysis(self, analysis_id):
        """
        测试获取面色分析性能
        
        Args:
            analysis_id: 分析ID
            
        Returns:
            响应时间
        """
        request = look_service_pb2.GetFaceAnalysisRequest(
            analysis_id=analysis_id
        )
        
        start_time = time.time()
        try:
            self.stub.GetFaceAnalysis(request)
            return time.time() - start_time
        except Exception as e:
            print(f"获取面色分析错误: {str(e)}")
            return time.time() - start_time
    
    def test_get_body_analysis(self, analysis_id):
        """
        测试获取形体分析性能
        
        Args:
            analysis_id: 分析ID
            
        Returns:
            响应时间
        """
        request = look_service_pb2.GetBodyAnalysisRequest(
            analysis_id=analysis_id
        )
        
        start_time = time.time()
        try:
            self.stub.GetBodyAnalysis(request)
            return time.time() - start_time
        except Exception as e:
            print(f"获取形体分析错误: {str(e)}")
            return time.time() - start_time
    
    def test_get_history(self, user_id):
        """
        测试获取用户分析历史性能
        
        Args:
            user_id: 用户ID
            
        Returns:
            响应时间
        """
        request = look_service_pb2.GetUserAnalysisHistoryRequest(
            user_id=user_id,
            limit=10,
            offset=0
        )
        
        start_time = time.time()
        try:
            self.stub.GetUserAnalysisHistory(request)
            return time.time() - start_time
        except Exception as e:
            print(f"获取用户分析历史错误: {str(e)}")
            return time.time() - start_time
    
    def run_sequential_test(self, num_requests=10):
        """
        运行顺序测试
        
        Args:
            num_requests: 请求数量
            
        Returns:
            测试结果字典
        """
        print(f"开始顺序测试 ({num_requests} 请求)")
        
        face_analysis_ids = []
        body_analysis_ids = []
        test_user_id = f"perf_test_user_{str(uuid.uuid4())[:8]}"
        
        # 测试面色分析
        print("测试面色分析...")
        for i in tqdm(range(num_requests)):
            elapsed, analysis_id = self.test_face_analysis(test_user_id)
            self.results["face_analysis"].append(elapsed)
            if analysis_id:
                face_analysis_ids.append(analysis_id)
        
        # 测试形体分析
        print("测试形体分析...")
        for i in tqdm(range(num_requests)):
            elapsed, analysis_id = self.test_body_analysis(test_user_id)
            self.results["body_analysis"].append(elapsed)
            if analysis_id:
                body_analysis_ids.append(analysis_id)
        
        # 如果有面色分析ID，测试获取面色分析
        if face_analysis_ids:
            print("测试获取面色分析...")
            for analysis_id in tqdm(face_analysis_ids[:num_requests]):
                elapsed = self.test_get_face_analysis(analysis_id)
                self.results["get_face_analysis"].append(elapsed)
        
        # 如果有形体分析ID，测试获取形体分析
        if body_analysis_ids:
            print("测试获取形体分析...")
            for analysis_id in tqdm(body_analysis_ids[:num_requests]):
                elapsed = self.test_get_body_analysis(analysis_id)
                self.results["get_body_analysis"].append(elapsed)
        
        # 测试获取用户分析历史
        print("测试获取用户分析历史...")
        for i in tqdm(range(num_requests)):
            elapsed = self.test_get_history(test_user_id)
            self.results["get_history"].append(elapsed)
        
        print("顺序测试完成")
        return self.results
    
    def run_concurrent_test(self, num_requests=10, concurrency=2):
        """
        运行并发测试
        
        Args:
            num_requests: 每种请求的数量
            concurrency: 并发度
            
        Returns:
            测试结果字典
        """
        print(f"开始并发测试 ({num_requests} 请求，并发度 {concurrency})")
        
        face_analysis_ids = []
        body_analysis_ids = []
        test_user_ids = [f"perf_test_user_{str(uuid.uuid4())[:8]}" for _ in range(concurrency)]
        
        # 面色分析
        print("测试面色分析...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [executor.submit(self.test_face_analysis, test_user_ids[i % len(test_user_ids)]) for i in range(num_requests)]
            for future in tqdm(concurrent.futures.as_completed(futures), total=num_requests):
                elapsed, analysis_id = future.result()
                self.results["face_analysis"].append(elapsed)
                if analysis_id:
                    face_analysis_ids.append(analysis_id)
        
        # 形体分析
        print("测试形体分析...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [executor.submit(self.test_body_analysis, test_user_ids[i % len(test_user_ids)]) for i in range(num_requests)]
            for future in tqdm(concurrent.futures.as_completed(futures), total=num_requests):
                elapsed, analysis_id = future.result()
                self.results["body_analysis"].append(elapsed)
                if analysis_id:
                    body_analysis_ids.append(analysis_id)
        
        # 获取面色分析
        if face_analysis_ids:
            print("测试获取面色分析...")
            with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
                futures = [executor.submit(self.test_get_face_analysis, analysis_id) for analysis_id in face_analysis_ids[:num_requests]]
                for future in tqdm(concurrent.futures.as_completed(futures), total=min(num_requests, len(face_analysis_ids))):
                    elapsed = future.result()
                    self.results["get_face_analysis"].append(elapsed)
        
        # 获取形体分析
        if body_analysis_ids:
            print("测试获取形体分析...")
            with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
                futures = [executor.submit(self.test_get_body_analysis, analysis_id) for analysis_id in body_analysis_ids[:num_requests]]
                for future in tqdm(concurrent.futures.as_completed(futures), total=min(num_requests, len(body_analysis_ids))):
                    elapsed = future.result()
                    self.results["get_body_analysis"].append(elapsed)
        
        # 获取用户分析历史
        print("测试获取用户分析历史...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [executor.submit(self.test_get_history, test_user_ids[i % len(test_user_ids)]) for i in range(num_requests)]
            for future in tqdm(concurrent.futures.as_completed(futures), total=num_requests):
                elapsed = future.result()
                self.results["get_history"].append(elapsed)
        
        print("并发测试完成")
        return self.results
    
    def generate_report(self, output_dir="./reports"):
        """
        生成性能测试报告
        
        Args:
            output_dir: 报告输出目录
            
        Returns:
            报告文件路径
        """
        os.makedirs(output_dir, exist_ok=True)
        report_time = time.strftime("%Y%m%d-%H%M%S")
        report_file = os.path.join(output_dir, f"performance_report_{report_time}.txt")
        chart_file = os.path.join(output_dir, f"performance_chart_{report_time}.png")
        
        # 计算统计信息
        stats = {}
        for api_name, times in self.results.items():
            if not times:
                continue
            
            stats[api_name] = {
                "count": len(times),
                "min": min(times),
                "max": max(times),
                "avg": statistics.mean(times),
                "median": statistics.median(times),
                "p95": sorted(times)[int(len(times) * 0.95)],
                "p99": sorted(times)[int(len(times) * 0.99)] if len(times) >= 100 else None
            }
        
        # 生成文本报告
        with open(report_file, "w") as f:
            f.write("============================================\n")
            f.write(f"望诊服务性能测试报告 - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("============================================\n\n")
            
            f.write("测试环境:\n")
            f.write(f"  - 主机: {self.host}\n")
            f.write(f"  - 端口: {self.port}\n\n")
            
            f.write("API响应时间统计 (单位: 秒):\n")
            for api_name, api_stats in stats.items():
                f.write(f"\n{api_name}:\n")
                f.write(f"  - 请求次数: {api_stats['count']}\n")
                f.write(f"  - 最小响应时间: {api_stats['min']:.4f}s\n")
                f.write(f"  - 最大响应时间: {api_stats['max']:.4f}s\n")
                f.write(f"  - 平均响应时间: {api_stats['avg']:.4f}s\n")
                f.write(f"  - 中位响应时间: {api_stats['median']:.4f}s\n")
                f.write(f"  - 95百分位响应时间: {api_stats['p95']:.4f}s\n")
                if api_stats['p99'] is not None:
                    f.write(f"  - 99百分位响应时间: {api_stats['p99']:.4f}s\n")
        
        # 生成图表
        plt.figure(figsize=(12, 8))
        
        # 响应时间箱线图
        plt.subplot(2, 1, 1)
        api_names = []
        api_times = []
        
        for api_name, times in self.results.items():
            if times:
                api_names.append(api_name)
                api_times.append(times)
        
        plt.boxplot(api_times, labels=api_names)
        plt.title("API响应时间分布")
        plt.ylabel("响应时间 (秒)")
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # 平均响应时间对比图
        plt.subplot(2, 1, 2)
        avgs = [statistics.mean(times) if times else 0 for times in api_times]
        plt.bar(api_names, avgs)
        plt.title("API平均响应时间")
        plt.ylabel("响应时间 (秒)")
        plt.grid(True, linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        plt.savefig(chart_file)
        
        print(f"测试报告保存至: {report_file}")
        print(f"性能图表保存至: {chart_file}")
        
        return report_file
    
    def close(self):
        """关闭通道"""
        if self.channel:
            self.channel.close()


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="望诊服务性能测试工具")
    parser.add_argument("--host", default="localhost", help="服务主机名")
    parser.add_argument("--port", type=int, default=50053, help="服务端口")
    parser.add_argument("--sequential", type=int, default=10, help="顺序测试请求数量")
    parser.add_argument("--concurrent", type=int, default=10, help="并发测试请求数量")
    parser.add_argument("--concurrency", type=int, default=5, help="并发度")
    parser.add_argument("--output", default="./reports", help="报告输出目录")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    
    tester = PerformanceTester(host=args.host, port=args.port)
    
    try:
        # 运行顺序测试
        if args.sequential > 0:
            tester.run_sequential_test(args.sequential)
        
        # 运行并发测试
        if args.concurrent > 0:
            tester.run_concurrent_test(args.concurrent, args.concurrency)
        
        # 生成报告
        tester.generate_report(args.output)
    finally:
        tester.close() 