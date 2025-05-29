#!/usr/bin/env python3
"""
简化的算诊微服务服务器

用于测试基本API功能
"""

import sys
import os
from datetime import date
from typing import Optional

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    import uvicorn
except ImportError:
    print("请安装FastAPI和uvicorn: pip install fastapi uvicorn")
    sys.exit(1)

from calculation_service.core.algorithms.wuyun_liuqi.calculator import WuyunLiuqiCalculator
from calculation_service.utils.bazi_calculator import BaziCalculator
from calculation_service.utils.bagua_calculator import BaguaCalculator
from calculation_service.utils.ziwu_calculator import ZiwuCalculator

# 创建FastAPI应用
app = FastAPI(
    title="算诊微服务",
    description="传统中医算诊分析服务",
    version="1.0.0"
)

# 初始化计算器
wuyun_calculator = WuyunLiuqiCalculator()
bazi_calculator = BaziCalculator()
bagua_calculator = BaguaCalculator()
ziwu_calculator = ZiwuCalculator()

# 请求模型
class WuyunAnalysisRequest(BaseModel):
    year: int

class BaziAnalysisRequest(BaseModel):
    birth_date: str  # YYYY-MM-DD格式
    birth_time: Optional[str] = None  # HH:MM格式

class BaguaAnalysisRequest(BaseModel):
    birth_date: str  # YYYY-MM-DD格式
    gender: str

class ZiwuAnalysisRequest(BaseModel):
    target_date: str  # YYYY-MM-DD格式

@app.get("/")
async def root():
    """根路径"""
    return {"message": "算诊微服务运行正常", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "calculation-service",
        "version": "1.0.0"
    }

@app.post("/api/v1/wuyun-liuqi/analyze")
async def analyze_wuyun_liuqi(request: WuyunAnalysisRequest):
    """五运六气分析"""
    try:
        result = wuyun_calculator.calculate_year_analysis(request.year)
        return {
            "success": True,
            "data": result,
            "message": f"{request.year}年五运六气分析完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")

@app.post("/api/v1/bazi/analyze")
async def analyze_bazi(request: BaziAnalysisRequest):
    """八字分析"""
    try:
        # 解析日期
        birth_date = date.fromisoformat(request.birth_date)
        
        # 计算八字
        result = bazi_calculator.calculate_bazi(birth_date, request.birth_time)
        
        # 分析体质
        constitution = bazi_calculator.analyze_constitution_from_bazi(result)
        
        return {
            "success": True,
            "data": {
                "bazi": result,
                "constitution": constitution
            },
            "message": "八字分析完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")

@app.post("/api/v1/bagua/analyze")
async def analyze_bagua(request: BaguaAnalysisRequest):
    """八卦体质分析"""
    try:
        # 解析日期
        birth_date = date.fromisoformat(request.birth_date)
        
        # 计算八卦体质
        result = bagua_calculator.calculate_constitution(birth_date, request.gender)
        
        return {
            "success": True,
            "data": result,
            "message": "八卦体质分析完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")

@app.post("/api/v1/ziwu/analyze")
async def analyze_ziwu(request: ZiwuAnalysisRequest):
    """子午流注分析"""
    try:
        # 解析日期
        target_date = date.fromisoformat(request.target_date)
        
        # 计算最佳治疗时间
        result = ziwu_calculator.calculate_optimal_time(target_date)
        
        return {
            "success": True,
            "data": result,
            "message": "子午流注分析完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")

@app.post("/api/v1/comprehensive/analyze")
async def comprehensive_analyze(
    year: int,
    birth_date: str,
    gender: str,
    birth_time: Optional[str] = None
):
    """综合算诊分析"""
    try:
        # 解析日期
        birth_date_obj = date.fromisoformat(birth_date)
        
        # 五运六气分析
        wuyun_result = wuyun_calculator.calculate_year_analysis(year)
        
        # 八字分析
        bazi_result = bazi_calculator.calculate_bazi(birth_date_obj, birth_time)
        bazi_constitution = bazi_calculator.analyze_constitution_from_bazi(bazi_result)
        
        # 八卦分析
        bagua_result = bagua_calculator.calculate_constitution(birth_date_obj, gender)
        
        # 子午流注分析
        ziwu_result = ziwu_calculator.calculate_optimal_time(birth_date_obj)
        
        return {
            "success": True,
            "data": {
                "wuyun_liuqi": wuyun_result,
                "bazi": {
                    "calculation": bazi_result,
                    "constitution": bazi_constitution
                },
                "bagua": bagua_result,
                "ziwu": ziwu_result,
                "summary": {
                    "primary_constitution": bazi_constitution["constitution_type"],
                    "bagua_constitution": bagua_result["constitution_type"],
                    "year_influence": wuyun_result["wuyun"]["name"],
                    "optimal_treatment_times": ziwu_result["optimal_hours"][:2]
                }
            },
            "message": "综合算诊分析完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")

if __name__ == "__main__":
    print("启动算诊微服务...")
    print("API文档地址: http://localhost:8005/docs")
    print("健康检查: http://localhost:8005/health")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8005,
        log_level="info"
    ) 