"""
SuokeBench gRPC客户端示例
"""

import argparse
import grpc
import sys
import time
from pathlib import Path

# 添加项目根目录到系统路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.grpc import benchmark_pb2, benchmark_pb2_grpc


def run_benchmark(stub, benchmark_id, model_id, model_version):
    """
    运行基准测试
    
    Args:
        stub: gRPC存根
        benchmark_id: 基准测试ID
        model_id: 模型ID
        model_version: 模型版本
        
    Returns:
        运行ID
    """
    print(f"正在运行基准测试 {benchmark_id} 与模型 {model_id}:{model_version}...")
    
    # 构建请求
    request = benchmark_pb2.RunBenchmarkRequest(
        benchmark_id=benchmark_id,
        model_id=model_id,
        model_version=model_version,
        parameters={
            "min_confidence": "0.7",
            "features": "color,coating,shape,moisture"
        }
    )
    
    # 发送请求
    response = stub.RunBenchmark(request)
    
    print(f"基准测试已启动: {response.run_id}")
    print(f"状态: {response.status}")
    print(f"消息: {response.message}")
    
    return response.run_id


def get_benchmark_result(stub, run_id, include_details=False):
    """
    获取基准测试结果
    
    Args:
        stub: gRPC存根
        run_id: 运行ID
        include_details: 是否包含详情
    """
    print(f"正在获取运行ID为 {run_id} 的结果...")
    
    # 构建请求
    request = benchmark_pb2.GetBenchmarkResultRequest(
        run_id=run_id,
        include_details=include_details
    )
    
    # 发送请求
    response = stub.GetBenchmarkResult(request)
    
    print(f"运行ID: {response.run_id}")
    print(f"基准测试ID: {response.benchmark_id}")
    print(f"模型: {response.model_id}:{response.model_version}")
    print(f"状态: {response.status}")
    print(f"创建时间: {response.created_at}")
    
    if response.completed_at:
        print(f"完成时间: {response.completed_at}")
        
    # 输出指标
    if response.metrics:
        print("\n指标:")
        for name, metric in response.metrics.items():
            print(f"  {name}: {metric.value} {metric.unit}")
            
    # 输出样本（如果请求了详情）
    if include_details and response.samples:
        print("\n样本详情:")
        for i, sample in enumerate(response.samples[:3]):  # 仅显示前3个样本
            print(f"  样本 {i+1}:")
            print(f"    ID: {sample.sample_id}")
            print(f"    输入: {sample.input[:50]}...")
            print(f"    期望: {sample.expected[:50]}...")
            print(f"    实际: {sample.actual[:50]}...")
            print(f"    正确: {sample.correct}")
            
        if len(response.samples) > 3:
            print(f"  ... 及其他 {len(response.samples) - 3} 个样本")


def list_benchmarks(stub):
    """
    列出基准测试任务
    
    Args:
        stub: gRPC存根
    """
    print("正在获取可用基准测试任务...")
    
    # 构建请求
    request = benchmark_pb2.ListBenchmarksRequest()
    
    # 发送请求
    response = stub.ListBenchmarks(request)
    
    print(f"找到 {len(response.benchmarks)} 个基准测试任务:")
    
    for bench in response.benchmarks:
        print(f"\nID: {bench.id}")
        print(f"名称: {bench.name}")
        print(f"描述: {bench.description}")
        print(f"任务类型: {bench.task}")
        print(f"样本数: {bench.sample_count}")
        print(f"标签: {', '.join(bench.tags)}")
        print(f"指标: {', '.join(bench.metrics)}")
        
        if bench.parameters:
            print("参数:")
            for name, desc in bench.parameters.items():
                print(f"  {name}: {desc}")


def monitor_benchmark(stub, run_id):
    """
    监控基准测试进度
    
    Args:
        stub: gRPC存根
        run_id: 运行ID
    """
    print(f"正在监控运行ID为 {run_id} 的进度...")
    
    # 构建请求
    request = benchmark_pb2.MonitorBenchmarkRequest(run_id=run_id)
    
    try:
        # 发送请求并获取流式响应
        for progress in stub.MonitorBenchmark(request):
            print(f"\r进度: {progress.progress:.1f}% | 阶段: {progress.current_stage} | "
                  f"样本: {progress.processed_samples}/{progress.total_samples}", end="")
            
            # 如果完成，则退出循环
            if progress.status == "COMPLETED":
                print("\n基准测试已完成!")
                break
    except KeyboardInterrupt:
        print("\n监控已停止")
    except grpc.RpcError as e:
        print(f"\n监控出错: {e}")


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="SuokeBench gRPC客户端示例")
    parser.add_argument("--host", default="localhost", help="服务器主机")
    parser.add_argument("--port", type=int, default=50051, help="服务器端口")
    parser.add_argument("--action", choices=["run", "get", "list", "monitor"], required=True, help="操作类型")
    parser.add_argument("--benchmark-id", help="基准测试ID")
    parser.add_argument("--model-id", default="default_model", help="模型ID")
    parser.add_argument("--model-version", default="1.0.0", help="模型版本")
    parser.add_argument("--run-id", help="运行ID")
    parser.add_argument("--details", action="store_true", help="包含详情")
    args = parser.parse_args()
    
    # 创建gRPC通道
    channel = grpc.insecure_channel(f"{args.host}:{args.port}")
    stub = benchmark_pb2_grpc.BenchmarkServiceStub(channel)
    
    try:
        # 根据操作类型执行相应操作
        if args.action == "run":
            if not args.benchmark_id:
                print("错误: 运行基准测试需要指定 --benchmark-id")
                return
                
            run_id = run_benchmark(stub, args.benchmark_id, args.model_id, args.model_version)
            
            # 监控进度
            time.sleep(1)  # 等待任务启动
            monitor_benchmark(stub, run_id)
            
            # 获取结果
            get_benchmark_result(stub, run_id, True)
            
        elif args.action == "get":
            if not args.run_id:
                print("错误: 获取结果需要指定 --run-id")
                return
                
            get_benchmark_result(stub, args.run_id, args.details)
            
        elif args.action == "list":
            list_benchmarks(stub)
            
        elif args.action == "monitor":
            if not args.run_id:
                print("错误: 监控进度需要指定 --run-id")
                return
                
            monitor_benchmark(stub, args.run_id)
            
    except grpc.RpcError as e:
        print(f"gRPC错误: {e.code()}: {e.details()}")
    finally:
        channel.close()


if __name__ == "__main__":
    main()