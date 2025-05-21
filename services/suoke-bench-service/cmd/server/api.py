"""
SuokeBench API 接口
"""

import logging
import os
from typing import Dict, List, Optional, Union

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from internal.benchmark.benchmark_service import BenchmarkService
from internal.benchmark.model_interface import ModelRegistry, model_registry
from internal.evaluation.report_generator import ReportGenerator
from internal.metrics.basic_metrics import register_basic_metrics
from internal.suokebench.config import BenchConfig, load_config

# 初始化基础指标
register_basic_metrics()

# 初始化报告生成器
report_generator = ReportGenerator()

# 创建路由
router = APIRouter(prefix="/api", tags=["benchmark"])

# 加载配置
config_path = os.environ.get("CONFIG_PATH", "config/config.yaml")
config: BenchConfig = load_config(config_path)

# 创建服务实例
benchmark_service = BenchmarkService(config)


# 请求模型
class RunBenchmarkRequest(BaseModel):
    """运行基准测试请求"""
    benchmark_id: str = Field(..., description="基准测试ID")
    model_id: str = Field(..., description="模型ID")
    model_version: str = Field(..., description="模型版本")
    parameters: Optional[Dict[str, str]] = Field(default=None, description="附加参数")


class GetResultRequest(BaseModel):
    """获取结果请求"""
    run_id: str = Field(..., description="运行ID")
    include_details: bool = Field(default=False, description="是否包含详细结果")


class CompareBenchmarksRequest(BaseModel):
    """比较基准测试请求"""
    baseline_run_id: str = Field(..., description="基线运行ID")
    compare_run_id: str = Field(..., description="对比运行ID")


class ReportRequest(BaseModel):
    """生成报告请求"""
    run_id: str = Field(..., description="运行ID")
    format: str = Field(default="html", description="报告格式")
    include_samples: bool = Field(default=True, description="是否包含样本")
    metrics: Optional[List[str]] = Field(default=None, description="要包含的指标")


class ModelRegistrationRequest(BaseModel):
    """模型注册请求"""
    model_id: str = Field(..., description="模型ID")
    model_version: str = Field(..., description="模型版本")
    model_type: str = Field(..., description="模型类型(local或remote_api)")
    model_config: Dict[str, Union[str, int, float, bool, None]] = Field(..., description="模型配置")


class SettingsRequest(BaseModel):
    """更新设置请求"""
    data_dir: Optional[str] = Field(default=None, description="数据目录")
    report_dir: Optional[str] = Field(default=None, description="报告保存目录")
    parallel_runs: Optional[int] = Field(default=None, description="最大并行评测数")
    log_level: Optional[str] = Field(default=None, description="日志级别")


# API端点
@router.post("/run", summary="运行基准测试")
async def run_benchmark(request: RunBenchmarkRequest):
    """
    运行基准测试
    """
    try:
        # 准备请求
        grpc_request = {
            "benchmark_id": request.benchmark_id,
            "model_id": request.model_id,
            "model_version": request.model_version,
            "parameters": request.parameters or {},
        }
        
        # 调用服务
        response = benchmark_service.RunBenchmark(grpc_request, None)
        
        return {
            "run_id": response.run_id,
            "status": response.status,
            "message": response.message,
        }
    except Exception as e:
        logging.error(f"运行基准测试失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/result", summary="获取基准测试结果")
async def get_result(request: GetResultRequest):
    """
    获取基准测试结果
    """
    try:
        # 准备请求
        grpc_request = {
            "run_id": request.run_id,
            "include_details": request.include_details,
        }
        
        # 调用服务
        response = benchmark_service.GetBenchmarkResult(grpc_request, None)
        
        return {
            "run_id": response.run_id,
            "benchmark_id": response.benchmark_id,
            "model_id": response.model_id,
            "model_version": response.model_version,
            "status": response.status,
            "metrics": {k: v.to_dict() for k, v in response.metrics.items()},
            "samples": [s.to_dict() for s in response.samples] if request.include_details else [],
            "task": response.task,
            "created_at": response.created_at,
            "completed_at": response.completed_at,
        }
    except Exception as e:
        logging.error(f"获取基准测试结果失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/benchmarks", summary="列出可用基准测试")
async def list_benchmarks(
    task_filter: Optional[str] = Query(None, description="任务类型过滤"),
    tag: Optional[str] = Query(None, description="标签过滤"),
):
    """
    列出可用基准测试
    """
    try:
        # 准备请求
        grpc_request = {
            "task_filter": task_filter,
            "tag": tag,
        }
        
        # 调用服务
        response = benchmark_service.ListBenchmarks(grpc_request, None)
        
        return [b.to_dict() for b in response.benchmarks]
    except Exception as e:
        logging.error(f"列出基准测试失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare", summary="比较基准测试结果")
async def compare_benchmarks(request: CompareBenchmarksRequest):
    """
    比较基准测试结果
    """
    try:
        # 准备请求
        grpc_request = {
            "baseline_run_id": request.baseline_run_id,
            "compare_run_id": request.compare_run_id,
        }
        
        # 调用服务
        response = benchmark_service.CompareBenchmarks(grpc_request, None)
        
        return {
            "baseline_model": response.baseline_model,
            "compare_model": response.compare_model,
            "metrics": {k: v.to_dict() for k, v in response.metrics.items()},
            "case_comparisons": [c.to_dict() for c in response.case_comparisons],
            "summary": response.summary,
        }
    except Exception as e:
        logging.error(f"比较基准测试失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/report", summary="生成评测报告")
async def generate_report(request: ReportRequest):
    """
    生成评测报告
    """
    try:
        # 获取结果
        result_request = {
            "run_id": request.run_id,
            "include_details": request.include_samples,
        }
        result_response = benchmark_service.GetBenchmarkResult(result_request, None)
        
        # 将GRPC响应转换为字典
        result = {
            "run_id": result_response.run_id,
            "benchmark_id": result_response.benchmark_id,
            "model_id": result_response.model_id,
            "model_version": result_response.model_version,
            "status": result_response.status,
            "metrics": {k: v.to_dict() for k, v in result_response.metrics.items()},
            "samples": [s.to_dict() for s in result_response.samples] if request.include_samples else [],
            "task": result_response.task,
            "created_at": result_response.created_at,
            "completed_at": result_response.completed_at,
        }
        
        # 生成报告
        report_path = report_generator.generate_report(
            result=result,
            format=request.format,
            include_samples=request.include_samples,
            include_metrics=request.metrics,
        )
        
        if not report_path:
            raise HTTPException(status_code=500, detail="生成报告失败")
            
        # 返回报告URL
        base_url = "/reports/"
        filename = os.path.basename(report_path)
        report_url = f"{base_url}{filename}"
        
        return {
            "report_url": report_url,
            "message": f"报告已生成",
        }
    except Exception as e:
        logging.error(f"生成报告失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/report/{filename}", summary="获取报告文件")
async def get_report(filename: str):
    """
    获取报告文件
    """
    report_path = os.path.join("data/reports", filename)
    
    if not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail="报告不存在")
        
    return FileResponse(report_path)


@router.post("/models/register", summary="注册模型")
async def register_model(request: ModelRegistrationRequest):
    """
    注册模型
    """
    try:
        # 注册模型
        model = model_registry.register_model(
            model_id=request.model_id,
            model_version=request.model_version,
            model_type=request.model_type,
            model_config=request.model_config,
        )
        
        return {
            "status": "success",
            "message": f"模型 {request.model_id}:{request.model_version} 注册成功",
        }
    except Exception as e:
        logging.error(f"注册模型失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models", summary="列出已注册模型")
async def list_models():
    """
    列出已注册模型
    """
    try:
        models = model_registry.list_models()
        return models
    except Exception as e:
        logging.error(f"列出模型失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/models/{model_id}/{model_version}", summary="注销模型")
async def unregister_model(model_id: str, model_version: str):
    """
    注销模型
    """
    try:
        success = model_registry.unregister_model(model_id, model_version)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"模型 {model_id}:{model_version} 不存在")
            
        return {
            "status": "success",
            "message": f"模型 {model_id}:{model_version} 注销成功",
        }
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"注销模型失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-dataset", summary="上传数据集")
async def upload_dataset(
    dataset_type: str = Form(..., description="数据集类型"),
    file: UploadFile = File(..., description="数据集文件"),
):
    """
    上传数据集文件
    """
    try:
        # 确定保存路径
        save_dir = os.path.join("data", dataset_type)
        os.makedirs(save_dir, exist_ok=True)
        
        # 保存文件
        save_path = os.path.join(save_dir, file.filename)
        
        with open(save_path, "wb") as f:
            content = await file.read()
            f.write(content)
            
        return {
            "status": "success",
            "message": f"数据集 {file.filename} 上传成功",
            "path": save_path,
        }
    except Exception as e:
        logging.error(f"上传数据集失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks", summary="获取任务类型")
async def get_task_types():
    """
    获取任务类型
    """
    task_types = {
        "TCM_DIAGNOSIS": "中医辨证",
        "TONGUE_RECOGNITION": "舌象识别",
        "FACE_RECOGNITION": "面色识别",
        "PULSE_RECOGNITION": "脉象识别",
        "HEALTH_PLAN_GENERATION": "健康方案生成",
        "AGENT_COLLABORATION": "智能体协作",
        "PRIVACY_VERIFICATION": "隐私验证",
        "EDGE_PERFORMANCE": "端侧性能",
        "DIALECT_RECOGNITION": "方言识别",
    }
    
    return {
        "task_types": [
            {"id": k, "name": v} for k, v in task_types.items()
        ]
    }


@router.get("/history", summary="获取评测历史")
async def get_benchmark_history(
    benchmark_id: Optional[str] = Query(None, description="基准测试ID"),
    model_id: Optional[str] = Query(None, description="模型ID"),
    limit: int = Query(10, description="返回数量限制"),
):
    """
    获取评测历史记录
    """
    try:
        # 从服务获取历史记录
        history = benchmark_service.get_history(benchmark_id, model_id, limit)
        
        return {
            "history": [
                {
                    "run_id": h.run_id,
                    "benchmark_id": h.benchmark_id,
                    "model_id": h.model_id,
                    "model_version": h.model_version,
                    "status": h.status,
                    "created_at": h.created_at,
                    "completed_at": h.completed_at,
                    "metrics_summary": h.metrics_summary,
                }
                for h in history
            ]
        }
    except Exception as e:
        logging.error(f"获取评测历史失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/runs/{run_id}/status", summary="检查评测状态")
async def check_run_status(run_id: str):
    """
    检查评测运行状态
    """
    try:
        status = benchmark_service.get_run_status(run_id)
        
        if not status:
            raise HTTPException(status_code=404, detail=f"找不到运行ID: {run_id}")
            
        return status
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"检查运行状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/runs/{run_id}", summary="删除评测记录")
async def delete_run(run_id: str):
    """
    删除评测记录
    """
    try:
        success = benchmark_service.delete_run(run_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"找不到运行ID: {run_id}")
            
        return {
            "status": "success",
            "message": f"评测记录 {run_id} 已成功删除",
        }
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"删除评测记录失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Web UI 路由
@router.get("/ui/dashboard", summary="获取仪表盘数据")
async def get_dashboard_data():
    """
    获取仪表盘数据
    """
    try:
        # 获取最近的评测历史
        recent_runs = benchmark_service.get_history(limit=5)
        
        # 获取可用基准测试数量
        benchmarks_response = benchmark_service.ListBenchmarks({}, None)
        benchmark_count = len(benchmarks_response.benchmarks)
        
        # 获取已注册模型数量
        model_count = len(model_registry.list_models())
        
        # 计算整体性能统计
        total_runs = len(benchmark_service.get_history(limit=100))
        passing_runs = len([r for r in benchmark_service.get_history(limit=100) if r.overall_pass])
        passing_rate = passing_runs / total_runs if total_runs > 0 else 0
        
        return {
            "benchmark_count": benchmark_count,
            "model_count": model_count,
            "total_runs": total_runs,
            "passing_rate": passing_rate,
            "recent_runs": [
                {
                    "run_id": r.run_id,
                    "benchmark_id": r.benchmark_id,
                    "model_id": r.model_id,
                    "status": r.status,
                    "created_at": r.created_at,
                    "metrics_summary": r.metrics_summary,
                }
                for r in recent_runs
            ],
        }
    except Exception as e:
        logging.error(f"获取仪表盘数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ui/metrics-stats", summary="获取指标统计数据")
async def get_metrics_stats(
    benchmark_id: Optional[str] = Query(None, description="基准测试ID"),
    metric_name: Optional[str] = Query(None, description="指标名称"),
    time_range: str = Query("month", description="时间范围(week/month/year)"),
):
    """
    获取指标统计数据，用于图表显示
    """
    try:
        stats = benchmark_service.get_metrics_stats(benchmark_id, metric_name, time_range)
        
        return {
            "stats": stats,
        }
    except Exception as e:
        logging.error(f"获取指标统计数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# 新增Web界面API端点
@router.get("/stats", summary="获取统计数据")
async def get_stats():
    """
    获取系统统计数据，用于仪表盘
    """
    try:
        # 获取已完成评测数量
        completed_benchmarks = len([r for r in benchmark_service.get_history(limit=1000) if r.status == "COMPLETED"])
        
        # 获取运行中评测数量
        running_benchmarks = len([r for r in benchmark_service.get_history(limit=1000) if r.status == "RUNNING"])
        
        # 获取可用模型数量
        available_models = len(model_registry.list_models())
        
        # 获取数据集数量
        data_sets = sum(len(os.listdir(os.path.join("data", d))) for d in ["tcm-4d", "health-plan", "agent-dialogue", "privacy-zkp"] if os.path.exists(os.path.join("data", d)))
        
        return {
            "completed_benchmarks": completed_benchmarks,
            "running_benchmarks": running_benchmarks,
            "available_models": available_models,
            "data_sets": data_sets,
        }
    except Exception as e:
        logging.error(f"获取统计数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recent-runs", summary="获取最近运行记录")
async def get_recent_runs(limit: int = Query(5, description="返回数量限制")):
    """
    获取最近运行记录，用于仪表盘显示
    """
    try:
        recent_runs = benchmark_service.get_history(limit=limit)
        
        return [
            {
                "run_id": r.run_id,
                "benchmark_id": r.benchmark_id,
                "benchmark_name": r.benchmark_name,
                "model_id": r.model_id,
                "model_version": r.model_version,
                "status": r.status,
                "created_at": r.created_at,
                "completed_at": r.completed_at,
            }
            for r in recent_runs
        ]
    except Exception as e:
        logging.error(f"获取最近运行记录失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/results", summary="获取结果列表")
async def get_results_list(
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    status: str = Query("all", description="状态过滤(all/running/completed/failed)"),
):
    """
    获取结果列表，支持分页和状态过滤
    """
    try:
        # 获取所有结果
        all_results = benchmark_service.get_history(limit=1000)
        
        # 状态过滤
        if status != "all":
            status_map = {"running": "RUNNING", "completed": "COMPLETED", "failed": "FAILED"}
            all_results = [r for r in all_results if r.status == status_map.get(status, r.status)]
        
        # 计算分页
        total = len(all_results)
        total_pages = (total + page_size - 1) // page_size
        start = (page - 1) * page_size
        end = min(start + page_size, total)
        
        # 获取当前页的结果
        page_results = all_results[start:end]
        
        return {
            "results": [
                {
                    "run_id": r.run_id,
                    "benchmark_id": r.benchmark_id,
                    "benchmark_name": r.benchmark_name,
                    "model_id": r.model_id,
                    "model_version": r.model_version,
                    "status": r.status,
                    "created_at": r.created_at,
                    "completed_at": r.completed_at,
                }
                for r in page_results
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }
    except Exception as e:
        logging.error(f"获取结果列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports", summary="获取报告列表")
async def get_reports_list():
    """
    获取所有生成的报告列表
    """
    try:
        reports_dir = "data/reports"
        os.makedirs(reports_dir, exist_ok=True)
        
        # 获取所有报告文件
        report_files = [f for f in os.listdir(reports_dir) if f.endswith(".html") or f.endswith(".pdf")]
        
        # 获取报告元数据
        reports = []
        for filename in report_files:
            try:
                # 从文件名解析运行ID
                report_id = filename.split("_")[0]
                
                # 尝试获取结果数据
                result = benchmark_service.GetBenchmarkResult({"run_id": report_id, "include_details": False}, None)
                
                reports.append({
                    "report_id": report_id,
                    "report_url": f"/reports/{filename}",
                    "benchmark_id": result.benchmark_id,
                    "benchmark_name": result.benchmark_name,
                    "model_id": result.model_id,
                    "model_version": result.model_version,
                    "created_at": result.created_at,
                    "format": filename.split(".")[-1].upper(),
                })
            except Exception:
                # 如果无法获取元数据，使用文件属性
                file_path = os.path.join(reports_dir, filename)
                stat = os.stat(file_path)
                
                reports.append({
                    "report_id": report_id,
                    "report_url": f"/reports/{filename}",
                    "benchmark_id": "未知",
                    "benchmark_name": "未知",
                    "model_id": "未知",
                    "model_version": "未知",
                    "created_at": stat.st_mtime,
                    "format": filename.split(".")[-1].upper(),
                })
        
        # 按创建时间排序
        reports.sort(key=lambda r: r["created_at"], reverse=True)
        
        return reports
    except Exception as e:
        logging.error(f"获取报告列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/result-ui", summary="获取结果Web界面")
async def get_result_ui(run_id: str):
    """
    获取单个结果的Web界面展示
    """
    try:
        # 获取结果
        result = benchmark_service.GetBenchmarkResult({"run_id": run_id, "include_details": True}, None)
        
        # 生成HTML报告
        report_path = report_generator.generate_report(
            result={
                "run_id": result.run_id,
                "benchmark_id": result.benchmark_id,
                "model_id": result.model_id,
                "model_version": result.model_version,
                "status": result.status,
                "metrics": {k: v.to_dict() for k, v in result.metrics.items()},
                "samples": [s.to_dict() for s in result.samples],
                "task": result.task,
                "created_at": result.created_at,
                "completed_at": result.completed_at,
            },
            format="html",
            include_samples=True,
        )
        
        if not report_path:
            raise HTTPException(status_code=500, detail="生成报告失败")
            
        # 返回报告HTML
        with open(report_path, "r", encoding="utf-8") as f:
            html_content = f.read()
            
        return HTMLResponse(content=html_content)
    except Exception as e:
        logging.error(f"获取结果UI失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agent-performance", summary="获取智能体性能数据")
async def get_agent_performance():
    """
    获取智能体性能对比数据，用于雷达图
    """
    try:
        # 模拟数据，实际使用时需要从数据库获取
        return {
            "metrics": ["辨证准确率", "舌象识别", "面色识别", "脉象识别", "方案生成", "协作效率", "隐私安全"],
            "agents": [
                {
                    "name": "小艾",
                    "color": "#1e88e5",
                    "scores": [85, 92, 78, 88, 75, 80, 95]
                },
                {
                    "name": "小克",
                    "color": "#26a69a",
                    "scores": [75, 70, 65, 60, 90, 85, 80]
                },
                {
                    "name": "老克",
                    "color": "#ff5722",
                    "scores": [90, 85, 80, 75, 95, 90, 75]
                },
                {
                    "name": "索儿",
                    "color": "#9c27b0",
                    "scores": [80, 75, 85, 90, 85, 75, 85]
                }
            ]
        }
    except Exception as e:
        logging.error(f"获取智能体性能数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/task-distribution", summary="获取任务分布数据")
async def get_task_distribution():
    """
    获取评测任务分布数据，用于饼图
    """
    try:
        # 获取所有结果
        all_results = benchmark_service.get_history(limit=1000)
        
        # 按任务类型分组
        task_counts = {}
        task_names = {
            "TCM_DIAGNOSIS": "中医辨证",
            "TONGUE_RECOGNITION": "舌象识别",
            "FACE_RECOGNITION": "面色识别",
            "PULSE_RECOGNITION": "脉象识别",
            "HEALTH_PLAN_GENERATION": "健康方案生成",
            "AGENT_COLLABORATION": "智能体协作",
            "PRIVACY_VERIFICATION": "隐私验证",
            "EDGE_PERFORMANCE": "端侧性能",
        }
        
        for result in all_results:
            task = result.task
            task_name = task_names.get(task, task)
            if task_name in task_counts:
                task_counts[task_name] += 1
            else:
                task_counts[task_name] = 1
        
        # 转换为列表格式
        return [{"task": task, "count": count} for task, count in task_counts.items()]
    except Exception as e:
        logging.error(f"获取任务分布数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/settings", summary="获取当前设置")
async def get_settings():
    """
    获取当前系统设置
    """
    try:
        # 从配置文件获取
        settings = {
            "data_dir": config.data_dir,
            "report_dir": config.report_dir,
            "parallel_runs": config.max_parallel_runs,
            "log_level": config.log_level,
        }
        
        return settings
    except Exception as e:
        logging.error(f"获取设置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/settings", summary="更新系统设置")
async def update_settings(request: SettingsRequest):
    """
    更新系统设置
    """
    try:
        # 更新配置
        if request.data_dir:
            config.data_dir = request.data_dir
            
        if request.report_dir:
            config.report_dir = request.report_dir
            
        if request.parallel_runs:
            config.max_parallel_runs = request.parallel_runs
            
        if request.log_level:
            config.log_level = request.log_level
            
        # 保存配置到文件
        config.save_to_file(config_path)
        
        return {
            "status": "success",
            "message": "设置已更新",
        }
    except Exception as e:
        logging.error(f"更新设置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 