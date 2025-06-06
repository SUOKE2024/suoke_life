"""
routes - 索克生活项目模块
"""

from ..core.algorithms.bagua.calculator import BaguaCalculator
from ..core.algorithms.comprehensive_calculator import ComprehensiveCalculator
from ..core.algorithms.constitution.calculator import ConstitutionCalculator
from ..core.algorithms.wuyun_liuqi.calculator import WuyunLiuqiCalculator
from ..core.algorithms.ziwu_liuzhu.calculator import ZiwuLiuzhuCalculator
from datetime import datetime, date
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional

"""
算诊服务API路由

提供五诊中"算诊"功能的REST API接口
"""



router = APIRouter(prefix="/api/v1/calculation", tags=["算诊"])

# 初始化计算器
comprehensive_calc = ComprehensiveCalculator()
ziwu_calc = ZiwuLiuzhuCalculator()
constitution_calc = ConstitutionCalculator()
bagua_calc = BaguaCalculator()
wuyun_liuqi_calc = WuyunLiuqiCalculator()


class PersonalInfo(BaseModel):
    """个人信息模型"""
    birth_year: int = Field(..., description="出生年份", ge=1900, le=2100)
    birth_month: int = Field(..., description="出生月份", ge=1, le=12)
    birth_day: int = Field(..., description="出生日期", ge=1, le=31)
    birth_hour: int = Field(..., description="出生时辰", ge=0, le=23)
    gender: str = Field(..., description="性别", pattern="^(男|女)$")
    name: Optional[str] = Field(None, description="姓名")


class CalculationRequest(BaseModel):
    """算诊请求模型"""
    personal_info: PersonalInfo
    analysis_date: Optional[str] = Field(None, description="分析日期，格式：YYYY-MM-DD")
    include_ziwu: bool = Field(True, description="是否包含子午流注分析")
    include_constitution: bool = Field(True, description="是否包含体质分析")
    include_bagua: bool = Field(True, description="是否包含八卦分析")
    include_wuyun_liuqi: bool = Field(True, description="是否包含五运六气分析")


@router.post("/comprehensive", summary="综合算诊分析")
async def comprehensive_calculation(request: CalculationRequest):
    """
    综合算诊分析
    
    整合子午流注、八字体质、八卦配属、五运六气等多种算诊方法，
    提供全面的健康分析和调养建议。
    """
    try:
        # 解析分析日期
        if request.analysis_date:
            analysis_dt = datetime.strptime(request.analysis_date, "%Y-%m-%d")
        else:
            analysis_dt = datetime.now()
        
        # 构建出生信息
        birth_info = {
            "year": request.personal_info.birth_year,
            "month": request.personal_info.birth_month,
            "day": request.personal_info.birth_day,
            "hour": request.personal_info.birth_hour,
            "gender": request.personal_info.gender,
            "name": request.personal_info.name
        }
        
        # 执行综合分析
        result = comprehensive_calc.comprehensive_analysis(
            birth_info=birth_info,
            analysis_date=analysis_dt,
            include_ziwu=request.include_ziwu,
            include_constitution=request.include_constitution,
            include_bagua=request.include_bagua,
            include_wuyun_liuqi=request.include_wuyun_liuqi
        )
        
        return {
            "success": True,
            "data": result,
            "message": "综合算诊分析完成"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"算诊分析失败: {str(e)}")


@router.get("/ziwu-liuzhu", summary="子午流注分析")
async def ziwu_liuzhu_analysis(
    current_time: Optional[str] = Query(None, description="当前时间，格式：YYYY-MM-DD HH:MM")
):
    """
    子午流注分析
    
    根据当前时间分析十二经络的气血流注情况，
    提供最佳治疗时间和养生建议。
    """
    try:
        # 解析时间
        if current_time:
            dt = datetime.strptime(current_time, "%Y-%m-%d %H:%M")
        else:
            dt = datetime.now()
        
        # 执行子午流注分析
        result = ziwu_calc.analyze_current_time(dt)
        
        return {
            "success": True,
            "data": result,
            "message": "子午流注分析完成"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"子午流注分析失败: {str(e)}")


@router.post("/constitution", summary="八字体质分析")
async def constitution_analysis(personal_info: PersonalInfo):
    """
    八字体质分析
    
    根据出生时间分析个人体质特征，
    提供体质调理和养生建议。
    """
    try:
        # 构建出生信息
        birth_info = {
            "year": personal_info.birth_year,
            "month": personal_info.birth_month,
            "day": personal_info.birth_day,
            "hour": personal_info.birth_hour,
            "gender": personal_info.gender
        }
        
        # 执行体质分析
        result = constitution_calc.analyze_constitution(birth_info)
        
        return {
            "success": True,
            "data": result,
            "message": "八字体质分析完成"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"体质分析失败: {str(e)}")


@router.post("/bagua", summary="八卦配属分析")
async def bagua_analysis(personal_info: PersonalInfo):
    """
    八卦配属分析
    
    根据出生信息计算本命卦，分析与健康的关系，
    提供方位调理和预防建议。
    """
    try:
        # 构建出生信息
        birth_info = {
            "year": personal_info.birth_year,
            "month": personal_info.birth_month,
            "day": personal_info.birth_day,
            "gender": personal_info.gender
        }
        
        # 执行八卦分析
        result = bagua_calc.analyze_personal_bagua(birth_info)
        
        return {
            "success": True,
            "data": result,
            "message": "八卦配属分析完成"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"八卦分析失败: {str(e)}")


@router.get("/wuyun-liuqi/current", summary="当前运气分析")
async def current_wuyun_liuqi_analysis(
    analysis_date: Optional[str] = Query(None, description="分析日期，格式：YYYY-MM-DD")
):
    """
    当前运气分析
    
    分析当前时期的五运六气特点，
    预测易发疾病和调养建议。
    """
    try:
        # 解析分析日期
        if analysis_date:
            dt = datetime.strptime(analysis_date, "%Y-%m-%d")
        else:
            dt = datetime.now()
        
        # 执行运气分析
        result = wuyun_liuqi_calc.analyze_current_period(dt)
        
        return {
            "success": True,
            "data": result,
            "message": "当前运气分析完成"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"运气分析失败: {str(e)}")


@router.get("/wuyun-liuqi/yearly/{year}", summary="年度运气预测")
async def yearly_wuyun_liuqi_prediction(year: int):
    """
    年度运气预测
    
    分析指定年份的五运六气特点，
    提供全年健康预测和调养建议。
    """
    try:
        if year < 1900 or year > 2100:
            raise HTTPException(status_code=400, detail="年份范围应在1900-2100之间")
        
        # 执行年度预测
        result = wuyun_liuqi_calc.get_yearly_prediction(year)
        
        return {
            "success": True,
            "data": result,
            "message": f"{year}年运气预测完成"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"年度预测失败: {str(e)}")


@router.get("/health-advice", summary="个性化健康建议")
async def personalized_health_advice(
    birth_year: int = Query(..., description="出生年份"),
    birth_month: int = Query(..., description="出生月份"),
    birth_day: int = Query(..., description="出生日期"),
    birth_hour: int = Query(..., description="出生时辰"),
    gender: str = Query(..., description="性别"),
    analysis_date: Optional[str] = Query(None, description="分析日期")
):
    """
    个性化健康建议
    
    基于个人出生信息和当前时间，
    提供个性化的健康调养建议。
    """
    try:
        # 验证参数
        if gender not in ["男", "女"]:
            raise HTTPException(status_code=400, detail="性别必须是'男'或'女'")
        
        # 解析分析日期
        if analysis_date:
            dt = datetime.strptime(analysis_date, "%Y-%m-%d")
        else:
            dt = datetime.now()
        
        # 构建个人信息
        birth_info = {
            "year": birth_year,
            "month": birth_month,
            "day": birth_day,
            "hour": birth_hour,
            "gender": gender
        }
        
        # 执行综合分析
        result = comprehensive_calc.comprehensive_analysis(
            birth_info=birth_info,
            analysis_date=dt
        )
        
        # 提取健康建议
        health_advice = {
            "个人信息": {
                "出生时间": f"{birth_year}年{birth_month}月{birth_day}日{birth_hour}时",
                "性别": gender
            },
            "分析日期": dt.strftime("%Y年%m月%d日"),
            "综合建议": result.get("综合建议", {}),
            "调养重点": result.get("调养重点", []),
            "注意事项": result.get("注意事项", []),
            "最佳调理时间": result.get("子午流注分析", {}).get("最佳治疗时间", []),
            "体质特点": result.get("体质分析", {}).get("体质特征", {}),
            "运气影响": result.get("运气分析", {}).get("总体特点", "")
        }
        
        return {
            "success": True,
            "data": health_advice,
            "message": "个性化健康建议生成完成"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"健康建议生成失败: {str(e)}")


@router.get("/health", summary="健康检查")
async def health_check():
    """服务健康检查"""
    return {
        "success": True,
        "service": "calculation-service",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "algorithms": {
            "子午流注": "正常",
            "体质分析": "正常", 
            "八卦配属": "正常",
            "五运六气": "正常",
            "综合算诊": "正常"
        }
    } 