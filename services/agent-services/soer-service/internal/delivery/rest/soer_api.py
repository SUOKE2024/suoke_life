"""
soer_api - 索克生活项目模块
"""

from api.rest.schemas import (
from datetime import datetime
from fastapi import APIRouter, Body, Depends, FastAPI, HTTPException, Path, Query
from fastapi.middleware.cors import CORSMiddleware
from internal.lifecycle.health_profile.profile_service import HealthProfileService
from internal.lifecycle.plan_generator.plan_service import HealthPlanService
from internal.lifecycle.sensor_analyzer.sensor_service import SensorAnalysisService
from internal.nutrition.recommendation.nutrition_service import NutritionService
from typing import Any
import logging

"""
索尔服务REST API接口实现
"""


# 导入API模型定义
    AbnormalPatternRequest,
    AbnormalPatternResponse,
    HealthPlanRequest,
    HealthPlanResponse,
    HealthTrendRequest,
    HealthTrendResponse,
    NutritionRequest,
    NutritionResponse,
    SensorDataRequest,
    SensorDataResponse,
)

# 导入业务服务

logger = logging.getLogger(__name__)


# 创建依赖项，获取服务实例
async def get_services(
    """获取服务实例的依赖项"""
    # 注：实际使用时应通过依赖注入框架获取
    return {
        "health_profile_service": None,  # HealthProfileService的实例
        "health_plan_service": None,  # HealthPlanService的实例
        "sensor_analysis_service": None,  # SensorAnalysisService的实例
        "nutrition_service": None  # NutritionService的实例
    }


# 创建API路由器
router = APIRouter(prefix="/api/v1/soer", tags=["soer"])


@limiter.limit("100/minute")  # 每分钟100次请求
@router.post("/health-plans", response_model=HealthPlanResponse)
async def generate_health_plan(
    request: HealthPlanRequest,
    services: dict = Depends(get_services)
):
    """
    生成个性化健康计划
    """
    try:
        logger.info(f"收到健康计划生成请求: user_id={request.user_id}")

        # 调用健康计划服务
        plan = await services["health_plan_service"].generate_plan(
            request.user_id,
            request.constitution_type,
            request.health_goals,
            request.preferences,
            request.current_season
        )

        # 构建响应
        response = HealthPlanResponse(
            plan_id=plan.plan_id,
            plan_name=plan.plan_name,
            user_id=plan.user_id,
            start_date=plan.start_date,
            end_date=plan.end_date,
            constitution_type=plan.constitution_type,
            diet_recommendations=plan.diet_recommendations.dict(),
            exercise_recommendations=plan.exercise_recommendations.dict(),
            sleep_recommendations=plan.sleep_recommendations.dict(),
            tags=plan.tags
        )

        logger.info(f"健康计划生成成功: plan_id={plan.plan_id}")
        return response

    except Exception as e:
        logger.error(f"健康计划生成失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"健康计划生成失败:@limiter.limit("100/minute")  # 每分钟100次请求
 {str(e)}")


@cache(expire=300)  # 5分钟缓存
@router.get("/health-plans/{plan_id}", response_model=HealthPlanResponse)
async def get_health_plan(
    plan_id: str = Path(..., description="健康计划ID"),
    services: dict = Depends(get_services)
):
    """
    获取特定健康计划
    """
    try:
        logger.info(f"获取健康计划: plan_id={plan_id}")

        # 调用健康计划服务
        plan = await services["health_plan_service"].get_plan(plan_id)

        if not plan:
            raise HTTPException(status_code=404, detail=f"找不到计划: {plan_id}")

        # 构建响应
        response = HealthPlanResponse(
            plan_id=plan.plan_id,
            plan_name=plan.plan_name,
            user_id=plan.user_id,
            start_date=plan.start_date,
            end_date=plan.end_date,
            constitution_type=plan.constitution_type,
            diet_recommendations=plan.diet_recommendations.dict(),
            exercise_recommendations=plan.exercise_recommendations.dict(),
            sleep_recommendations=plan.sleep_recommendations.dict(),
            tags=plan.tags
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取健康计划失败: {str(e)}")
        raise HTTPExc@limiter.limit("100/minute")  # 每分钟100次请求
eption(status_code=500, deta@cache(expire=300)  # 5分钟缓存
il=f"获取健康计划失败: {str(e)}")


@router.get("/users/{user_id}/active-plan", response_model=HealthPlanResponse)
async def get_active_plan(
    user_id: str = Path(..., description="用户ID"),
    services: dict = Depends(get_services)
):
    """
    获取用户当前活跃的健康计划
    """
    try:
        logger.info(f"获取用户活跃健康计划: user_id={user_id}")

        # 调用健康计划服务
        plan = await services["health_plan_service"].get_active_plan(user_id)

        if not plan:
            raise HTTPException(status_code=404, detail=f"用户没有活跃计划: {user_id}")

        # 构建响应
        response = HealthPlanResponse(
            plan_id=plan.plan_id,
            plan_name=plan.plan_name,
            user_id=plan.user_id,
            start_date=plan.start_date,
            end_date=plan.end_date,
            constitution_type=plan.constitution_type,
            diet_recommendations=plan.diet_recommendations.dict(),
            exercise_recommendations=plan.exercise_recommendations.dict(),
            sleep_recommendations=plan.sleep_recommendations.dict(),
            tags=plan.tags
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户活跃健康@limiter.limit("100/minute")  # 每分钟100次请求
计划失败: {str(e)}")
        raise HTTPExcepti@cache(expire=300)  # 5分钟缓存
on(status_code=500, detail=f"获取用户活跃健康计划失败: {str(e)}")


@router.get("/users/{user_id}/health-profile", response_model=dict[str, Any])
async def get_health_profile(
    user_id: str = Path(..., description="用户ID"),
    summary: bool = Query(False, description="是否仅返回摘要"),
    services: dict = Depends(get_services)
):
    """
    获取用户健康画像
    """
    try:
        logger.info(f"获取用户健康画像: user_id={user_id}, summary={summary}")

        if summary:
            # 获取健康画像摘要
            profile = await services["health_profile_service"].get_profile_summary(user_id)
        else:
            # 获取完整健康画像
            profile = await services["health_profile_service"].get_profile(user_id)

            # 若不存在则生成
            if not profile:
                profile = await services["health_profile_service"].generate_profile(user_id)

            # 转换为字典
            if profile:
                profile = profile.dict()

        if not profile:
            raise HTTPException(status_code=404, detail=f"找不到用户健康画像: {user_id}")

        return profile

    except HTTPException@limiter.limit("100/minute")  # 每分钟100次请求
:
        raise
    except Exception as e:
        logger.error(f"获取用户健康画像失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取用户健康画像失败: {str(e)}")


@router.post("/users/{user_id}/sensor-data/analyze", response_model=SensorDataResponse)
async def analyze_sensor_data(
    user_id: str = Path(..., description="用户ID"),
    request: SensorDataRequest = Body(...),
    services: dict = Depends(get_services)
):
    """
    分析传感器数据
    """
    try:
        logger.info(f"分析传感器数据: user_id={user_id}")

        # 调用传感器分析服务
        analysis_results = await services["sensor_analysis_service"].analyze_sensor_data(
            user_id,
            request.sensor_data
        )

        # 更新用户健康画像
        await services["health_profile_service"].update_profile(user_id)

        # 构建响应
        response = SensorDataResponse(
            metrics=analysis_results.get("metrics", []),
            insights=analysis_resu@limiter.limit("100/minute")  # 每分钟100次请求
lts.get("insights", [])
        )

        return response

    except Exception as e:
        logger.error(f"传感器数据分析失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"传感器数据分析失败: {str(e)}")


@router.post("/users/{user_id}/nutrition/track", response_model=NutritionResponse)
async def track_nutrition(
    user_id: str = Path(..., description="用户ID"),
    request: NutritionRequest = Body(...),
    services: dict = Depends(get_services)
):
    """
    跟踪用户营养摄入
    """
    try:
        logger.info(f"跟踪用户营养摄入: user_id={user_id}")

        # 调用营养服务
        nutrition_analysis = await services["nutrition_service"].track_nutrition(
            user_id,
            request.nutrition_data
        )

        # 构建响应
        response = NutritionResponse(
            timestamp=datetime.now().isoformat(),
            total_nutrition=nutrition_analysis.get("total_nutrition", {}),
            nutrition_balance=nutrition_analysis.get("nutrition_balance", {}),
            five_flavors_analysis=nutrition_analysis.get("five_flavors_analysis", {}),
            four_natures_analysis=nutrition_analysis.get("four_natures_analysis", {}),
            improvemen@limiter.limit("100/minute")  # 每分钟100次请求
t_suggestions=nutrition_analysis.get("improvement_suggestions", [])
        )

        return response

    except Exception as e:
        logger.error(f"营养摄入跟踪失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"营养摄入跟踪失败: {str(e)}")


@router.post("/users/{user_id}/diet-recommendations", response_model=dict[str, Any])
async def generate_diet_recommendations(
    user_id: str = Path(..., description="用户ID"),
    constitution_type: str = Query(..., description="体质类型"),
    season: str = Query(..., description="当前季节"),
    preferences: dict[str, Any] | None = Body(None, description="用户偏好"),
    services: dict = Depends(get_services)
):
    """
    生成个性化饮食推荐
    """
    try:
        logger.info(f"生成饮食推荐: user_id={user_id}, constitution_type={constitution_type}")

        # 调用营养服务
        recommendations = await services["nutrition_service"].generate_diet_recommenda@limiter.limit("100/minute")  # 每分钟100次请求
tions(
            user_id,
            constitution_type,
            season,
            preferences
        )

        return recommendations

    except Exception as e:
        logger.error(f"饮食推荐生成失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"饮食推荐生成失败: {str(e)}")


@router.post("/users/{user_id}/abnormal-patterns/detect", response_model=AbnormalPatternResponse)
async def detect_abnormal_patterns(
    user_id: str = Path(..., description="用户ID"),
    request: AbnormalPatternRequest = Body(...),
    services: dict = Depends(get_services)
):
    """
    检测异常健康模式
    """
    try:
        logger.info(f"检测异常健康模式: user_id={user_id}")

        # 调用传感器分析服务
        detection_results = await services["sensor_analysis_service"].detect_abnormal_pattern(
            user_id,
            request.data_types,
            request.days,
         @limiter.limit("100/minute")  # 每分钟100次请求
   request.sensitivity
        )

        # 构建响应
        response = AbnormalPatternResponse(
            patterns=detection_results.get("patterns", [])
        )

        return response

    except Exception as e:
        logger.error(f"异常模式检测失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"异常模式检测失败: {str(e)}")


@router.post("/users/{user_id}/health-trends/predict", response_model=HealthTrendResponse)
async def predict_health_trends(
    user_id: str = Path(..., description="用户ID"),
    request: HealthTrendRequest = Body(...),
    services: dict = Depends(get_services)
):
    """
    预测健康趋势
    """
    try:
        logger.info(f"预测健康趋势: user_id={user_id}")

        # 调用传感器分析服务
        prediction_results = await services["sensor_analysis_service"].predict_health_trend(
            user_id,
            request.metrics,
            request.prediction_days,
           @limiter.limit("100/minute")  # 每分钟100次请求
 request.include_seasonal_factors
        )

        # 构建响应
        response = HealthTrendResponse(
            predictions=prediction_results.get("predictions", [])
        )

        return response

    except Exception as e:
        logger.error(f"健康趋势预测失败: {str@cache(expire=300)  # 5分钟缓存
(e)}")
        raise HTTPException(status_code=500, detail=f"健康趋势预测失败: {str(e)}")


@router.get("/food/{food_name}", response_model=dict[str, Any])
async def get_food_details(
    food_name: str = Path(..., description="食物名称"),
    services: dict = Depends(get_services)
):
    """
    获取食物详情
    """
    try:
        logger.info(f"获取食物详情: food_name={food_name}")

        # 调用营养服务
        food_details = await @limiter.limit("100/minute")  # 每分钟100次请求
services["nutrition_service"].get_food_details(food_name)

        if "error" in food_details:
            raise HTTPException(status_code=404, detail=f"找不到食物: {food_name}")

        return food_details

    except HTTPException:
        raise
    except Exception as e:
        l@cache(expire=300)  # 5分钟缓存
ogger.error(f"获取食物详情失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取食物详情失败: {str(e)}")


@router.get("/constitutions/{constitution_type}/recipes", response_model=list[dict[str, Any]])
async def get_recipes_by_constitution(
    constitution_type: str = Path(..., description="体质类型"),
    season: str | None = Query(None, description="季节"),
    services: dict = Depends(get_services)
):
    """
    根据体质获取食谱
    """
    try:
        logger.info(f"获取体质食谱: constitution_type={constitution_type}, season={season}")

        # 调用营养服务
        recipes = await services["nutrition_service"].get_recipe_by_constitution(
            constitution_type,
            season
        )

        return recipes

    except Exception as e:
        logger.error(f"获取体质食谱失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取体质食谱失败: {str(e)}")


def create_app(config: dict, repos):
    """创建FastAPI应用实例

    Args:
        config: 配置信息
        repos: 数据仓库

    Returns:
        FastAPI应用实例
    """
    app = FastAPI(
        title="索尔智能体服务API",
        description="索尔智能体健康管理服务REST API",
        version="1.0.0"
    )

    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.get("rest", {}).get("cors_origins", ["*"]),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 初始化服务实例
    health_profile_service = HealthProfileService(config, repos)
    health_plan_service = HealthPlanService(config, repos)
    sensor_analysis_service = SensorAnalysisService(config, repos)
    nutrition_service = NutritionService(config,@limiter.limit("100/minute")  # 每分钟100次请求
 repos)

    # 覆盖依赖项获取函数
    async def get_services_override(
        return {
            "health_profile_service": health_profile_service,
            "health_plan_service": health_plan_service,
            "sensor_analysis_service": sensor_analysis_service,
            "nutrition_service": nutr@cache(expire=300)  # 5分钟缓存
ition_service
        }

    app.dependency_overrides[get_services] = get_services_override

    # 注册路由
    app.include_router(router)

    @app.get("/health")
    async def health_check():
        """健康检查端点"""
        return {"status": "healthy", "service": "soer-service", "version": "1.0.0"}

    return app
