"""
算诊计算API接口

提供五运六气、八卦分析、子午流注等算诊方法的API接口
"""

from datetime import date, datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field

from ...core.algorithms.wuyun_liuqi import WuyunLiuqiCalculator
    WuyunLiuqiModel,
    BaguaAnalysisModel,
    ZiwuLiuzhuModel,
    ConstitutionAnalysisModel,
    ComprehensiveAnalysisModel
)
from ...services.calculation import CalculationService
from ...utils.validators import validate_date_range, validate_patient_info

router = APIRouter()

class WuyunLiuqiRequest(BaseModel):
    """五运六气分析请求"""
    year: int = Field(description="分析年份", ge=1900, le=2100)
    patient_birth: Optional[date] = Field(default=None, description="患者出生日期")
    analysis_date: Optional[date] = Field(default=None, description="分析日期")

class BaguaAnalysisRequest(BaseModel):
    """八卦分析请求"""
    birth_date: date = Field(description="出生日期")
    birth_time: Optional[str] = Field(default=None, description="出生时间(HH:MM)")
    birth_location: Optional[Dict] = Field(default=None, description="出生地点")

class ZiwuLiuzhuRequest(BaseModel):
    """子午流注分析请求"""
    condition: str = Field(description="病症")
    treatment_type: str = Field(description="治疗类型")
    date: Optional[date] = Field(default=None, description="分析日期")

class ComprehensiveAnalysisRequest(BaseModel):
    """综合算诊分析请求"""
    patient_info: Dict = Field(description="患者信息")
    current_symptoms: Optional[List[str]] = Field(default=None, description="当前症状")
    analysis_date: Optional[date] = Field(default=None, description="分析日期")
    analysis_options: Optional[Dict] = Field(default=None, description="分析选项")

@router.post("/wuyun-liuqi", response_model=Dict, summary="五运六气分析")
async def analyze_wuyun_liuqi(
    request: WuyunLiuqiRequest,
    background_tasks: BackgroundTasks,
    calculation_service: CalculationService = Depends()
):
    """
    五运六气分析
    
    根据指定年份和患者出生信息，分析五运六气对健康的影响
    """
    try:
        # 验证输入参数
        if request.patient_birth:
            validate_date_range(request.patient_birth)
        
        # 执行五运六气分析
        calculator = WuyunLiuqiCalculator()
        result = calculator.calculate_wuyun_liuqi(
            year=request.year,
            patient_birth=request.patient_birth
        )
        
        # 记录分析日志
        background_tasks.add_task(
            calculation_service.log_analysis,
            analysis_type="wuyun_liuqi",
            request_data=request.dict(),
            result_data=result
        )
        
        return {
            "success": True,
            "data": result,
            "message": "五运六气分析完成"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"五运六气分析失败: {str(e)}")

@router.post("/bagua-constitution", response_model=Dict, summary="八卦体质分析")
async def analyze_bagua_constitution(
    request: BaguaAnalysisRequest,
    background_tasks: BackgroundTasks,
    calculation_service: CalculationService = Depends()
):
    """
    八卦体质分析
    
    基于出生信息进行八卦体质分析，判断体质类型和健康倾向
    """
    try:
        # 验证输入参数
        validate_date_range(request.birth_date)
        
        # 执行八卦体质分析
        result = await calculation_service.analyze_bagua_constitution(
            birth_date=request.birth_date,
            birth_time=request.birth_time,
            birth_location=request.birth_location
        )
        
        # 记录分析日志
        background_tasks.add_task(
            calculation_service.log_analysis,
            analysis_type="bagua_constitution",
            request_data=request.dict(),
            result_data=result
        )
        
        return {
            "success": True,
            "data": result,
            "message": "八卦体质分析完成"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"八卦体质分析失败: {str(e)}")

@router.post("/ziwu-liuzhu", response_model=Dict, summary="子午流注时间分析")
async def analyze_ziwu_liuzhu(
    request: ZiwuLiuzhuRequest,
    background_tasks: BackgroundTasks,
    calculation_service: CalculationService = Depends()
):
    """
    子午流注时间分析
    
    根据病症和治疗类型，推荐最佳治疗时间
    """
    try:
        analysis_date = request.date or date.today()
        
        # 执行子午流注分析
        result = await calculation_service.analyze_ziwu_liuzhu(
            condition=request.condition,
            treatment_type=request.treatment_type,
            analysis_date=analysis_date
        )
        
        # 记录分析日志
        background_tasks.add_task(
            calculation_service.log_analysis,
            analysis_type="ziwu_liuzhu",
            request_data=request.dict(),
            result_data=result
        )
        
        return {
            "success": True,
            "data": result,
            "message": "子午流注分析完成"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"子午流注分析失败: {str(e)}")

@router.post("/comprehensive-analysis", response_model=Dict, summary="综合算诊分析")
async def comprehensive_analysis(
    request: ComprehensiveAnalysisRequest,
    background_tasks: BackgroundTasks,
    calculation_service: CalculationService = Depends()
):
    """
    综合算诊分析
    
    综合运用五运六气、八卦分析、子午流注等方法进行全面分析
    """
    try:
        # 验证患者信息
        validate_patient_info(request.patient_info)
        
        analysis_date = request.analysis_date or date.today()
        
        # 执行综合分析
        result = await calculation_service.comprehensive_analysis(
            patient_info=request.patient_info,
            current_symptoms=request.current_symptoms,
            analysis_date=analysis_date,
            options=request.analysis_options
        )
        
        # 记录分析日志
        background_tasks.add_task(
            calculation_service.log_analysis,
            analysis_type="comprehensive_analysis",
            request_data=request.dict(),
            result_data=result
        )
        
        return {
            "success": True,
            "data": result,
            "message": "综合算诊分析完成"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"综合算诊分析失败: {str(e)}")

@router.get("/year-ganzhi/{year}", response_model=Dict, summary="获取年份干支")
async def get_year_ganzhi(year: int):
    """
    获取指定年份的干支
    
    Args:
        year: 年份
        
    Returns:
        年份对应的干支信息
    """
    try:
        if year < 1900 or year > 2100:
            raise HTTPException(status_code=400, detail="年份必须在1900-2100之间")
        
        calculator = WuyunLiuqiCalculator()
        ganzhi = calculator.get_year_ganzhi(year)
        wuyun = calculator.get_wuyun_from_ganzhi(ganzhi)
        
        return {
            "success": True,
            "data": {
                "year": year,
                "ganzhi": ganzhi,
                "wuyun": wuyun
            },
            "message": "获取年份干支成功"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取年份干支失败: {str(e)}")

@router.get("/current-liuqi", response_model=Dict, summary="获取当前六气")
async def get_current_liuqi():
    """
    获取当前时间对应的六气
    
    Returns:
        当前六气信息
    """
    try:
        calculator = WuyunLiuqiCalculator()
        current_date = date.today()
        liuqi = calculator.get_seasonal_liuqi(current_date)
        
        return {
            "success": True,
            "data": {
                "date": current_date.isoformat(),
                "liuqi": liuqi
            },
            "message": "获取当前六气成功"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取当前六气失败: {str(e)}")

@router.get("/analysis-history/{patient_id}", response_model=Dict, summary="获取分析历史")
async def get_analysis_history(
    patient_id: str,
    limit: int = 10,
    offset: int = 0,
    calculation_service: CalculationService = Depends()
):
    """
    获取患者的算诊分析历史
    
    Args:
        patient_id: 患者ID
        limit: 返回数量限制
        offset: 偏移量
        
    Returns:
        分析历史记录
    """
    try:
        history = await calculation_service.get_analysis_history(
            patient_id=patient_id,
            limit=limit,
            offset=offset
        )
        
        return {
            "success": True,
            "data": history,
            "message": "获取分析历史成功"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取分析历史失败: {str(e)}")

@router.delete("/analysis/{analysis_id}", response_model=Dict, summary="删除分析记录")
async def delete_analysis(
    analysis_id: str,
    calculation_service: CalculationService = Depends()
):
    """
    删除指定的分析记录
    
    Args:
        analysis_id: 分析记录ID
        
    Returns:
        删除结果
    """
    try:
        success = await calculation_service.delete_analysis(analysis_id)
        
        if success:
            return {
                "success": True,
                "message": "删除分析记录成功"
            }
        else:
            raise HTTPException(status_code=404, detail="分析记录不存在")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除分析记录失败: {str(e)}") 