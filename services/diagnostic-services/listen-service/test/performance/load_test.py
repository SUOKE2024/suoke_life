#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
闻诊服务负载测试脚本
测试闻诊服务在高负载下的性能表现
"""
import os
import sys
import time
import argparse
import grpc
import asyncio
import logging
import statistics
import json
import matplotlib.pyplot as plt
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from api.grpc import listen_service_pb2 as pb2
from api.grpc import listen_service_pb2_grpc as pb2_grpc

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("load_test")

class ListenServiceLoadTest:
    """闻诊服务负载测试类"""
    
    def __init__(self, host, port, test_data_dir, output_dir):
        """
        初始化负载测试
        
        参数:
            host: 服务主机地址
            port: 服务端口
            test_data_dir: 测试音频文件目录
            output_dir: 测试结果输出目录
        """
        self.host = host
        self.port = port
        self.test_data_dir = Path(test_data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载测试音频文件
        self.audio_files = list(self.test_data_dir.glob("*.wav"))
        if not self.audio_files:
            raise ValueError(f"未找到测试音频文件: {test_data_dir}")
        
        logger.info(f"找到 {len(self.audio_files)} 个测试音频文件")
        
        # 创建Channel和Stub
        self.channel = grpc.insecure_channel(f"{self.host}:{self.port}")
        self.stub = pb2_grpc.ListenServiceStub(self.channel)
        
        # 结果存储
        self.results = {
            "响应时间": [],
            "成功请求": 0,
            "失败请求": 0,
            "错误类型": {},
            "API分布": {
                "AnalyzeVoice": {"count": 0, "响应时间": []},
                "AnalyzeSound": {"count": 0, "响应时间": []},
                "AnalyzeEmotion": {"count": 0, "响应时间": []},
                "DetectDialect": {"count": 0, "响应时间": []},
                "TranscribeAudio": {"count": 0, "响应时间": []},
                "BatchAnalyze": {"count": 0, "响应时间": []}
            }
        }
    
    def load_audio_file(self, file_path):
        """加载音频文件数据"""
        with open(file_path, 'rb') as f:
            return f.read()
    
    async def run_single_request(self, api_type, audio_file):
        """运行单个API请求"""
        audio_data = self.load_audio_file(audio_file)
        start_time = time.time()
        
        try:
            if api_type == "AnalyzeVoice":
                request = pb2.VoiceAnalysisRequest(
                    user_id="loadtest",
                    session_id=f"loadtest-{int(time.time())}",
                    audio_data=audio_data,
                    audio_format="wav",
                    sample_rate=16000,
                    channels=1,
                    apply_preprocessing=True
                )
                response = self.stub.AnalyzeVoice(request)
            
            elif api_type == "AnalyzeSound":
                request = pb2.SoundAnalysisRequest(
                    user_id="loadtest",
                    session_id=f"loadtest-{int(time.time())}",
                    audio_data=audio_data,
                    audio_format="wav",
                    sample_rate=16000,
                    sound_type=pb2.SoundType.COUGH,
                    apply_preprocessing=True
                )
                response = self.stub.AnalyzeSound(request)
            
            elif api_type == "AnalyzeEmotion":
                request = pb2.EmotionAnalysisRequest(
                    user_id="loadtest",
                    session_id=f"loadtest-{int(time.time())}",
                    audio_data=audio_data,
                    audio_format="wav",
                    sample_rate=16000
                )
                response = self.stub.AnalyzeEmotion(request)
            
            elif api_type == "DetectDialect":
                request = pb2.DialectDetectionRequest(
                    user_id="loadtest",
                    session_id=f"loadtest-{int(time.time())}",
                    audio_data=audio_data,
                    audio_format="wav",
                    sample_rate=16000
                )
                response = self.stub.DetectDialect(request)
            
            elif api_type == "TranscribeAudio":
                request = pb2.TranscriptionRequest(
                    user_id="loadtest",
                    session_id=f"loadtest-{int(time.time())}",
                    audio_data=audio_data,
                    audio_format="wav",
                    sample_rate=16000,
                    language="zh-CN"
                )
                response = self.stub.TranscribeAudio(request)
            
            elif api_type == "BatchAnalyze":
                request = pb2.BatchAnalysisRequest(
                    user_id="loadtest",
                    session_id=f"loadtest-{int(time.time())}",
                    audio_data=audio_data,
                    audio_format="wav",
                    sample_rate=16000,
                    analysis_types=["voice", "sound", "emotion"]
                )
                response = self.stub.BatchAnalyze(request)
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # 转换为毫秒
            
            # 记录结果
            self.results["响应时间"].append(response_time)
            self.results["成功请求"] += 1
            self.results["API分布"][api_type]["count"] += 1
            self.results["API分布"][api_type]["响应时间"].append(response_time)
            
            return {"status": "success", "response_time": response_time, "api": api_type}
        
        except grpc.RpcError as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            # 记录错误
            self.results["失败请求"] += 1
            error_type = str(e.code())
            self.results["错误类型"][error_type] = self.results["错误类型"].get(error_type, 0) + 1
            
            return {"status": "error", "error": str(e), "response_time": response_time, "api": api_type}
    
    async def run_load_test(self, total_requests, concurrency):
        """
        运行负载测试
        
        参数:
            total_requests: 总请求数
            concurrency: 并发请求数
        """
        logger.info(f"开始负载测试: {total_requests} 请求, {concurrency} 并发")
        
        # API类型列表
        api_types = ["AnalyzeVoice", "AnalyzeSound", "AnalyzeEmotion", 
                    "DetectDialect", "TranscribeAudio", "BatchAnalyze"]
        
        # 创建任务
        tasks = []
        for i in range(total_requests):
            # 循环使用测试音频
            audio_file = self.audio_files[i % len(self.audio_files)]
            # 循环使用API类型
            api_type = api_types[i % len(api_types)]
            
            tasks.append(self.run_single_request(api_type, audio_file))
            if (i + 1) % 10 == 0:
                logger.info(f"创建任务: {i + 1}/{total_requests}")
        
        # 使用线程池执行任务
        results = []
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            # 分批执行任务
            batch_size = min(concurrency * 2, total_requests)
            for i in range(0, len(tasks), batch_size):
                batch = tasks[i:i+batch_size]
                loop = asyncio.get_event_loop()
                batch_results = await asyncio.gather(*batch)
                results.extend(batch_results)
                
                # 计算当前完成百分比
                completed = min(i + batch_size, total_requests)
                logger.info(f"完成: {completed}/{total_requests} "
                           f"({completed/total_requests*100:.1f}%)")
        
        return results
    
    def generate_report(self):
        """生成测试报告"""
        logger.info("生成测试报告...")
        
        # 计算统计数据
        response_times = self.results["响应时间"]
        
        if not response_times:
            logger.error("没有收集到响应时间数据")
            return
        
        stats = {
            "总请求数": len(response_times) + self.results["失败请求"],
            "成功请求数": len(response_times),
            "失败请求数": self.results["失败请求"],
            "成功率": len(response_times) / (len(response_times) + self.results["失败请求"]) * 100,
            "平均响应时间(ms)": statistics.mean(response_times) if response_times else 0,
            "中位数响应时间(ms)": statistics.median(response_times) if response_times else 0,
            "最小响应时间(ms)": min(response_times) if response_times else 0,
            "最大响应时间(ms)": max(response_times) if response_times else 0,
            "90%响应时间(ms)": np.percentile(response_times, 90) if response_times else 0,
            "95%响应时间(ms)": np.percentile(response_times, 95) if response_times else 0,
            "99%响应时间(ms)": np.percentile(response_times, 99) if response_times else 0,
            "标准差(ms)": statistics.stdev(response_times) if len(response_times) > 1 else 0,
            "API分布": {k: v["count"] for k, v in self.results["API分布"].items()},
            "错误类型": self.results["错误类型"]
        }
        
        # 保存结果JSON
        with open(self.output_dir / "load_test_results.json", "w") as f:
            json.dump(stats, f, indent=2)
        
        # 生成响应时间直方图
        plt.figure(figsize=(10, 6))
        plt.hist(response_times, bins=20, alpha=0.7)
        plt.axvline(stats["平均响应时间(ms)"], color='r', linestyle='dashed', linewidth=1, label=f"平均: {stats['平均响应时间(ms)']:.2f}ms")
        plt.axvline(stats["95%响应时间(ms)"], color='g', linestyle='dashed', linewidth=1, label=f"95%: {stats['95%响应时间(ms)']:.2f}ms")
        plt.xlabel("响应时间 (ms)")
        plt.ylabel("频率")
        plt.title("闻诊服务响应时间分布")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.savefig(self.output_dir / "response_time_histogram.png")
        
        # 生成API分布饼图
        api_counts = [v["count"] for v in self.results["API分布"].values()]
        api_labels = list(self.results["API分布"].keys())
        
        plt.figure(figsize=(10, 6))
        plt.pie(api_counts, labels=api_labels, autopct='%1.1f%%', startangle=90)
        plt.title("API调用分布")
        plt.axis('equal')
        plt.savefig(self.output_dir / "api_distribution.png")
        
        # 生成每个API的平均响应时间柱状图
        api_mean_times = []
        for api, data in self.results["API分布"].items():
            if data["count"] > 0:
                api_mean_times.append((api, statistics.mean(data["响应时间"])))
        
        if api_mean_times:
            apis, times = zip(*api_mean_times)
            plt.figure(figsize=(12, 6))
            plt.bar(apis, times)
            plt.xlabel("API")
            plt.ylabel("平均响应时间 (ms)")
            plt.title("各API平均响应时间")
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(self.output_dir / "api_response_times.png")
        
        # 生成文本报告
        report = f"""
# 闻诊服务负载测试报告

## 测试概述
- 总请求数: {stats['总请求数']}
- 成功请求数: {stats['成功请求数']}
- 失败请求数: {stats['失败请求数']}
- 成功率: {stats['成功率']:.2f}%

## 响应时间统计
- 平均响应时间: {stats['平均响应时间(ms)']:.2f} ms
- 中位数响应时间: {stats['中位数响应时间(ms)']:.2f} ms
- 最小响应时间: {stats['最小响应时间(ms)']:.2f} ms
- 最大响应时间: {stats['最大响应时间(ms)']:.2f} ms
- 90%响应时间: {stats['90%响应时间(ms)']:.2f} ms
- 95%响应时间: {stats['95%响应时间(ms)']:.2f} ms
- 99%响应时间: {stats['99%响应时间(ms)']:.2f} ms
- 标准差: {stats['标准差(ms)']:.2f} ms

## API调用分布
"""
        for api, count in stats["API分布"].items():
            report += f"- {api}: {count}\n"
        
        report += "\n## 错误类型分布\n"
        for error_type, count in stats["错误类型"].items():
            report += f"- {error_type}: {count}\n"
        
        with open(self.output_dir / "load_test_report.md", "w") as f:
            f.write(report)
        
        logger.info(f"测试报告已生成: {self.output_dir}")
    
    def cleanup(self):
        """清理资源"""
        if hasattr(self, 'channel') and self.channel:
            self.channel.close()


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="闻诊服务负载测试工具")
    parser.add_argument("--host", default="localhost", help="服务主机地址")
    parser.add_argument("--port", type=int, default=50052, help="服务端口")
    parser.add_argument("--test-data", required=True, help="测试音频文件目录")
    parser.add_argument("--total-requests", type=int, default=100, help="总请求数")
    parser.add_argument("--concurrency", type=int, default=10, help="并发请求数")
    parser.add_argument("--output-dir", default="./test_results", help="测试结果输出目录")
    
    args = parser.parse_args()
    
    test = ListenServiceLoadTest(
        host=args.host,
        port=args.port,
        test_data_dir=args.test_data,
        output_dir=args.output_dir
    )
    
    try:
        await test.run_load_test(args.total_requests, args.concurrency)
        test.generate_report()
    finally:
        test.cleanup()


if __name__ == "__main__":
    asyncio.run(main()) 