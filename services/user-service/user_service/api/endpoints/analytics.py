"""用户分析API端点"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from user_service.database import get_db
from user_service.auth import get_current_user, require_active_user
from user_service.analytics import (
    get_health_analyzer,
    get_profile_analyzer,
    get_recommendation_engine,
    HealthDataAnalyzer,
    UserProfileAnalyzer,
    RecommendationEngine
)
from user_service.performance import performance_monitor, query_cache
from user_service.models.user import User

router = APIRouter()


@router.get("/health-report/{user_id}")
@performance_monitor("generate_health_report")
@query_cache(ttl=1800)  # 缓存30分钟
async def generate_health_report(
    user_id: str,
    days: int = Query(30, ge=1, le=365, description="分析天数"),
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
    analyzer: HealthDataAnalyzer = Depends(get_health_analyzer)
):
    """生成用户健康报告"""
    
    # 权限检查：只能查看自己的报告或管理员可以查看所有
    if str(current_user.id) != user_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限访问此用户的健康报告"
        )
    
    try:
        # 模拟获取用户健康数据
        # 实际实现中应该从数据库获取
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # 模拟健康数据
        user_data = {
            "heart_rate": [
                {"value": 72, "timestamp": datetime.utcnow() - timedelta(days=i)}
                for i in range(days)
            ],
            "sleep": [
                {"duration": 7.5, "quality": 4, "timestamp": datetime.utcnow() - timedelta(days=i)}
                for i in range(days)
            ],
            "activity": [
                {"steps": 8500, "timestamp": datetime.utcnow() - timedelta(days=i)}
                for i in range(days)
            ],
            "weight": [
                {"value": 70.0, "date": datetime.utcnow() - timedelta(days=i)}
                for i in range(0, days, 7)  # 每周一次
            ]
        }
        
        # 生成综合健康报告
        report = analyzer.generate_comprehensive_report(user_data)
        
        return {
            "user_id": user_id,
            "analysis_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": days
            },
            "report": report
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成健康报告失败: {str(e)}"
        )


@router.get("/user-profile/{user_id}")
@performance_monitor("analyze_user_profile")
@query_cache(ttl=3600)  # 缓存1小时
async def analyze_user_profile(
    user_id: str,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
    analyzer: UserProfileAnalyzer = Depends(get_profile_analyzer)
):
    """分析用户画像"""
    
    # 权限检查
    if str(current_user.id) != user_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限访问此用户画像"
        )
    
    try:
        # 模拟获取用户活动数据
        # 实际实现中应该从数据库获取
        activity_data = [
            {
                "steps": 8500 + (i % 3) * 1000,
                "sleep_hours": 7.5 + (i % 2) * 0.5,
                "exercise_minutes": 30 + (i % 4) * 15,
                "date": datetime.utcnow() - timedelta(days=i)
            }
            for i in range(30)  # 最近30天
        ]
        
        # 分析用户行为生成画像
        profile = analyzer.analyze_user_behavior(user_id, activity_data)
        
        return {
            "user_id": profile.user_id,
            "age_group": profile.age_group,
            "activity_level": profile.activity_level,
            "health_goals": profile.health_goals,
            "risk_factors": profile.risk_factors,
            "preferences": profile.preferences,
            "engagement_score": profile.engagement_score,
            "last_updated": profile.last_updated.isoformat(),
            "analysis_summary": {
                "data_points": len(activity_data),
                "analysis_period_days": 30
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"用户画像分析失败: {str(e)}"
        )


@router.get("/recommendations/{user_id}")
@performance_monitor("generate_recommendations")
@query_cache(ttl=1800)  # 缓存30分钟
async def generate_recommendations(
    user_id: str,
    limit: int = Query(10, ge=1, le=50, description="推荐数量限制"),
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
    profile_analyzer: UserProfileAnalyzer = Depends(get_profile_analyzer),
    health_analyzer: HealthDataAnalyzer = Depends(get_health_analyzer),
    recommendation_engine: RecommendationEngine = Depends(get_recommendation_engine)
):
    """生成个性化推荐"""
    
    # 权限检查
    if str(current_user.id) != user_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限访问此用户的推荐"
        )
    
    try:
        # 获取用户画像
        activity_data = [
            {
                "steps": 8500 + (i % 3) * 1000,
                "sleep_hours": 7.5 + (i % 2) * 0.5,
                "exercise_minutes": 30 + (i % 4) * 15,
                "date": datetime.utcnow() - timedelta(days=i)
            }
            for i in range(30)
        ]
        
        user_profile = profile_analyzer.analyze_user_behavior(user_id, activity_data)
        
        # 获取健康洞察
        user_health_data = {
            "heart_rate": [
                {"value": 72 + (i % 5) * 2, "timestamp": datetime.utcnow() - timedelta(days=i)}
                for i in range(7)
            ],
            "sleep": [
                {"duration": 7.5 - (i % 3) * 0.5, "quality": 4 - (i % 2), "timestamp": datetime.utcnow() - timedelta(days=i)}
                for i in range(7)
            ]
        }
        
        heart_rate_insights = health_analyzer.analyze_heart_rate_trends(user_health_data["heart_rate"])
        sleep_insights = health_analyzer.analyze_sleep_patterns(user_health_data["sleep"])
        all_insights = heart_rate_insights + sleep_insights
        
        # 生成个性化推荐
        recommendations = recommendation_engine.generate_personalized_recommendations(
            user_profile, all_insights
        )
        
        return {
            "user_id": user_id,
            "recommendations": recommendations[:limit],
            "total_available": len(recommendations),
            "generated_at": datetime.utcnow().isoformat(),
            "based_on": {
                "user_profile": {
                    "activity_level": user_profile.activity_level,
                    "health_goals": user_profile.health_goals,
                    "risk_factors": user_profile.risk_factors
                },
                "health_insights_count": len(all_insights)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成推荐失败: {str(e)}"
        )


@router.get("/trends/{user_id}")
@performance_monitor("analyze_trends")
@query_cache(ttl=3600)  # 缓存1小时
async def analyze_trends(
    user_id: str,
    metric_type: str = Query(..., description="指标类型: heart_rate, sleep, activity, weight"),
    days: int = Query(30, ge=7, le=365, description="分析天数"),
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
    analyzer: HealthDataAnalyzer = Depends(get_health_analyzer)
):
    """分析健康指标趋势"""
    
    # 权限检查
    if str(current_user.id) != user_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限访问此用户的趋势分析"
        )
    
    # 验证指标类型
    valid_metrics = ["heart_rate", "sleep", "activity", "weight"]
    if metric_type not in valid_metrics:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的指标类型。支持的类型: {', '.join(valid_metrics)}"
        )
    
    try:
        # 模拟生成趋势数据
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # 根据指标类型生成不同的模拟数据
        if metric_type == "heart_rate":
            data = [
                {"value": 72 + (i % 10) - 5, "timestamp": start_date + timedelta(days=i)}
                for i in range(days)
            ]
            insights = analyzer.analyze_heart_rate_trends(data)
        elif metric_type == "sleep":
            data = [
                {"duration": 7.5 + (i % 6) * 0.2 - 0.6, "quality": 4 + (i % 3) - 1, "timestamp": start_date + timedelta(days=i)}
                for i in range(days)
            ]
            insights = analyzer.analyze_sleep_patterns(data)
        elif metric_type == "activity":
            data = [
                {"steps": 8000 + (i % 8) * 500, "timestamp": start_date + timedelta(days=i)}
                for i in range(days)
            ]
            insights = analyzer.analyze_activity_levels(data)
        elif metric_type == "weight":
            data = [
                {"value": 70.0 + (i % 14) * 0.1 - 0.7, "date": start_date + timedelta(days=i)}
                for i in range(0, days, 3)  # 每3天一次
            ]
            insights = analyzer.analyze_weight_trends(data)
        
        # 计算趋势统计
        if metric_type == "weight":
            values = [d["value"] for d in data]
        elif metric_type == "sleep":
            values = [d["duration"] for d in data]
        else:
            values = [d["value"] for d in data]
        
        trend_stats = {
            "average": sum(values) / len(values) if values else 0,
            "minimum": min(values) if values else 0,
            "maximum": max(values) if values else 0,
            "trend_direction": "stable"  # 简化的趋势方向
        }
        
        # 简单的趋势方向计算
        if len(values) >= 2:
            first_half_avg = sum(values[:len(values)//2]) / (len(values)//2)
            second_half_avg = sum(values[len(values)//2:]) / (len(values) - len(values)//2)
            
            if second_half_avg > first_half_avg * 1.05:
                trend_stats["trend_direction"] = "increasing"
            elif second_half_avg < first_half_avg * 0.95:
                trend_stats["trend_direction"] = "decreasing"
        
        return {
            "user_id": user_id,
            "metric_type": metric_type,
            "analysis_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": days
            },
            "data_points": len(data),
            "trend_statistics": trend_stats,
            "insights": [
                {
                    "title": insight.title,
                    "description": insight.description,
                    "risk_level": insight.risk_level.value,
                    "recommendations": insight.recommendations,
                    "confidence": insight.confidence
                }
                for insight in insights
            ],
            "raw_data": data[-10:] if len(data) > 10 else data  # 返回最近10个数据点
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"趋势分析失败: {str(e)}"
        )


@router.get("/dashboard/{user_id}")
@performance_monitor("generate_dashboard")
@query_cache(ttl=900)  # 缓存15分钟
async def generate_dashboard(
    user_id: str,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
    health_analyzer: HealthDataAnalyzer = Depends(get_health_analyzer),
    profile_analyzer: UserProfileAnalyzer = Depends(get_profile_analyzer)
):
    """生成用户健康仪表板"""
    
    # 权限检查
    if str(current_user.id) != user_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限访问此用户的仪表板"
        )
    
    try:
        # 获取最近7天的数据摘要
        recent_data = {
            "heart_rate": [
                {"value": 72 + (i % 5), "timestamp": datetime.utcnow() - timedelta(days=i)}
                for i in range(7)
            ],
            "sleep": [
                {"duration": 7.5 + (i % 2) * 0.5, "quality": 4, "timestamp": datetime.utcnow() - timedelta(days=i)}
                for i in range(7)
            ],
            "activity": [
                {"steps": 8500 + (i % 3) * 1000, "timestamp": datetime.utcnow() - timedelta(days=i)}
                for i in range(7)
            ]
        }
        
        # 生成快速健康评估
        health_report = health_analyzer.generate_comprehensive_report(recent_data)
        
        # 获取用户画像摘要
        activity_data = [
            {
                "steps": 8500,
                "sleep_hours": 7.5,
                "exercise_minutes": 30,
                "date": datetime.utcnow()
            }
        ]
        user_profile = profile_analyzer.analyze_user_behavior(user_id, activity_data)
        
        # 计算关键指标
        avg_heart_rate = sum(d["value"] for d in recent_data["heart_rate"]) / len(recent_data["heart_rate"])
        avg_sleep = sum(d["duration"] for d in recent_data["sleep"]) / len(recent_data["sleep"])
        avg_steps = sum(d["steps"] for d in recent_data["activity"]) / len(recent_data["activity"])
        
        return {
            "user_id": user_id,
            "dashboard_date": datetime.utcnow().isoformat(),
            "summary": {
                "health_score": health_report["health_score"],
                "activity_level": user_profile.activity_level,
                "engagement_score": user_profile.engagement_score
            },
            "key_metrics": {
                "avg_heart_rate": round(avg_heart_rate, 1),
                "avg_sleep_hours": round(avg_sleep, 1),
                "avg_daily_steps": round(avg_steps, 0),
                "data_period": "last_7_days"
            },
            "alerts": [
                insight for insight in health_report["insights"]
                if insight["risk_level"] in ["high", "critical"]
            ],
            "quick_recommendations": health_report["recommendations"][:3],
            "trends": {
                "heart_rate": "stable",
                "sleep": "improving",
                "activity": "stable"
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成仪表板失败: {str(e)}"
        )


@router.post("/insights/feedback")
@performance_monitor("record_insight_feedback")
async def record_insight_feedback(
    insight_id: str,
    feedback: Dict[str, Any],
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db)
):
    """记录用户对健康洞察的反馈"""
    
    try:
        # 验证反馈数据
        required_fields = ["rating", "helpful"]
        for field in required_fields:
            if field not in feedback:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"缺少必需字段: {field}"
                )
        
        # 验证评分范围
        if not isinstance(feedback["rating"], int) or not 1 <= feedback["rating"] <= 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="评分必须是1-5之间的整数"
            )
        
        # 记录反馈（实际实现中应该保存到数据库）
        feedback_record = {
            "insight_id": insight_id,
            "user_id": str(current_user.id),
            "rating": feedback["rating"],
            "helpful": feedback["helpful"],
            "comment": feedback.get("comment", ""),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # TODO: 保存到数据库
        
        return {
            "message": "反馈已记录",
            "feedback_id": f"fb_{insight_id}_{int(datetime.utcnow().timestamp())}",
            "recorded_at": feedback_record["timestamp"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"记录反馈失败: {str(e)}"
        ) 