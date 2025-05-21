#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
教育服务模拟器
用于本地开发和测试，模拟教育服务API
"""

import os
import json
import time
import random
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

import uvicorn
from fastapi import FastAPI, HTTPException, Request, Depends, Header, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("edu-service-mock")

# 加载环境变量
PORT = int(os.getenv("PORT", "8000"))
MOCK_DELAY = int(os.getenv("MOCK_DELAY", "200"))  # 毫秒
RANDOM_FAILURES = os.getenv("RANDOM_FAILURES", "false").lower() == "true"
API_KEYS = ["dev-edu-api-key", "test-edu-api-key"]  # 允许的API密钥

# 创建FastAPI应用
app = FastAPI(
    title="教育服务模拟器",
    description="模拟教育服务API的接口，用于开发和测试",
    version="0.1.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据路径
DATA_DIR = Path(__file__).parent / "data"

# 加载模拟数据
def load_mock_data(filename: str) -> Dict:
    """加载模拟数据文件"""
    try:
        file_path = DATA_DIR / filename
        if not file_path.exists():
            logger.warning(f"找不到模拟数据文件: {filename}")
            return {}
        
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"加载模拟数据文件失败: {filename}, 错误: {str(e)}")
        return {}

# 模拟延迟中间件
@app.middleware("http")
async def add_mock_delay(request: Request, call_next):
    """模拟API延迟的中间件"""
    # 随机模拟失败
    if RANDOM_FAILURES and random.random() < 0.1:  # 10%概率失败
        status_code = random.choice([500, 502, 503, 504])
        return JSONResponse(
            status_code=status_code,
            content={"detail": f"模拟服务错误: {status_code}"}
        )
    
    # 添加随机延迟 (0.8-1.2倍的配置延迟)
    delay = MOCK_DELAY * (0.8 + random.random() * 0.4) / 1000.0
    time.sleep(delay)
    
    # 继续处理请求
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"请求处理错误: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": "内部服务器错误"}
        )

# API密钥验证
def verify_api_key(authorization: str = Header(...)):
    """验证API密钥"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的授权头格式"
        )
    
    api_key = authorization.split("Bearer ")[1]
    if api_key not in API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的API密钥"
        )
    
    return api_key

# 模型定义
class CourseRecommendationRequest(BaseModel):
    user_id: str
    interests: List[str]
    prev_courses: Optional[List[str]] = None
    limit: Optional[int] = 5

class LearningPathRequest(BaseModel):
    user_id: str
    goal: str
    current_level: str = "beginner"
    time_frame: Optional[str] = None

class SearchCoursesRequest(BaseModel):
    q: str
    type: Optional[str] = None
    difficulty: Optional[str] = None
    limit: Optional[int] = 10

class EducationalContentRequest(BaseModel):
    content_type: str
    topic: str
    format: str = "article"

class LearningProgressRequest(BaseModel):
    user_id: str
    course_id: str
    progress: float
    completed: bool = False
    timestamp: Optional[int] = None

# 路由: 健康检查
@app.get("/health")
def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "timestamp": int(time.time())
    }

# 路由: 获取课程推荐
@app.get("/api/v1/courses/recommendations")
def get_course_recommendations(
    user_id: str,
    interests: str,
    limit: Optional[int] = 5,
    prev_courses: Optional[str] = None,
    authorization: str = Depends(verify_api_key)
):
    """获取课程推荐"""
    # 解析兴趣列表
    interests_list = interests.split(",")
    
    # 解析之前的课程（如果有）
    prev_courses_list = prev_courses.split(",") if prev_courses else []
    
    # 加载模拟数据
    courses_data = load_mock_data("courses.json")
    all_courses = courses_data.get("courses", [])
    
    # 基于兴趣筛选课程
    filtered_courses = []
    for course in all_courses:
        course_tags = course.get("tags", [])
        if any(interest in course_tags for interest in interests_list):
            # 排除已学过的课程
            if course["id"] not in prev_courses_list:
                filtered_courses.append(course)
    
    # 如果过滤后课程太少，添加一些随机课程
    while len(filtered_courses) < limit and len(all_courses) > len(filtered_courses):
        random_course = random.choice(all_courses)
        if random_course not in filtered_courses and random_course["id"] not in prev_courses_list:
            filtered_courses.append(random_course)
    
    # 限制返回数量
    result_courses = filtered_courses[:limit]
    
    return {"courses": result_courses}

# 路由: 生成学习路径
@app.post("/api/v1/learning/path/generate")
def generate_learning_path(
    request: LearningPathRequest,
    authorization: str = Depends(verify_api_key)
):
    """生成学习路径"""
    # 加载模拟数据
    paths_data = load_mock_data("learning_paths.json")
    all_paths = paths_data.get("paths", [])
    
    # 基于目标和级别筛选学习路径
    matching_paths = [
        path for path in all_paths 
        if path.get("difficulty", "") == request.current_level
    ]
    
    # 如果没有匹配的路径，创建一个默认的
    if not matching_paths:
        # 加载课程数据以创建模块
        courses_data = load_mock_data("courses.json")
        all_courses = courses_data.get("courses", [])
        
        # 按难度筛选课程
        level_courses = [
            course for course in all_courses 
            if course.get("difficulty", "") == request.current_level
        ]
        
        # 创建模块
        modules = []
        if level_courses:
            # 分成2-3个模块
            num_modules = min(len(level_courses), random.randint(2, 3))
            courses_per_module = len(level_courses) // num_modules
            
            for i in range(num_modules):
                start_idx = i * courses_per_module
                end_idx = start_idx + courses_per_module if i < num_modules - 1 else len(level_courses)
                module_courses = level_courses[start_idx:end_idx]
                
                total_duration = sum(course.get("duration", 3600) for course in module_courses)
                
                modules.append({
                    "id": f"module-{random.randint(100, 999)}",
                    "title": f"{request.current_level.capitalize()} Module {i+1}",
                    "courses": [course["id"] for course in module_courses],
                    "duration": total_duration,
                    "order": i + 1
                })
        
        # 创建路径
        path = {
            "path_id": f"path-{random.randint(100, 999)}",
            "modules": modules,
            "estimated_duration": sum(module.get("duration", 0) for module in modules),
            "difficulty": request.current_level,
            "description": f"为'{request.goal}'目标定制的{request.current_level}级学习路径",
            "goal": request.goal
        }
    else:
        # 使用匹配的路径
        path = random.choice(matching_paths)
        path["goal"] = request.goal  # 更新目标
    
    return path

# 路由: 获取课程详情
@app.get("/api/v1/courses/{course_id}")
def get_course_details(
    course_id: str,
    authorization: str = Depends(verify_api_key)
):
    """获取课程详情"""
    # 加载模拟数据
    courses_data = load_mock_data("courses.json")
    all_courses = courses_data.get("courses", [])
    
    # 查找课程
    course = next((c for c in all_courses if c["id"] == course_id), None)
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"找不到课程: {course_id}"
        )
    
    return course

# 路由: 搜索课程
@app.get("/api/v1/courses/search")
def search_courses(
    q: str,
    type: Optional[str] = None,
    difficulty: Optional[str] = None,
    limit: Optional[int] = 10,
    authorization: str = Depends(verify_api_key)
):
    """搜索课程"""
    # 加载模拟数据
    courses_data = load_mock_data("courses.json")
    all_courses = courses_data.get("courses", [])
    
    # 基于查询筛选课程
    filtered_courses = []
    for course in all_courses:
        # 标题或描述中包含查询词
        title_match = q.lower() in course.get("title", "").lower()
        desc_match = q.lower() in course.get("description", "").lower()
        
        if title_match or desc_match:
            # 类型筛选
            if type and course.get("type", "") != type:
                continue
            
            # 难度筛选
            if difficulty and course.get("difficulty", "") != difficulty:
                continue
            
            filtered_courses.append(course)
    
    # 限制返回数量
    result_courses = filtered_courses[:limit]
    
    return {
        "results": result_courses,
        "total": len(filtered_courses)
    }

# 路由: 获取教育内容
@app.get("/api/v1/content/educational")
def get_educational_content(
    content_type: str,
    topic: str,
    format: str = "article",
    authorization: str = Depends(verify_api_key)
):
    """获取教育内容"""
    # 加载模拟数据
    content_data = load_mock_data("educational_content.json")
    all_content = content_data.get("content", [])
    
    # 基于类型、主题和格式筛选内容
    matching_content = [
        c for c in all_content 
        if c.get("type", "") == content_type and 
           c.get("topic", "") == topic and
           c.get("format", "") == format
    ]
    
    # 如果找到匹配的内容，返回第一个
    if matching_content:
        return matching_content[0]
    
    # 否则创建一个空内容
    return {
        "id": f"content-{random.randint(100, 999)}",
        "title": f"{topic.capitalize()} - {content_type}",
        "content": f"这是关于{topic}的{content_type}内容，格式为{format}。模拟数据未找到匹配的内容。",
        "format": format,
        "type": content_type,
        "topic": topic,
        "author": "系统生成",
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "tags": [topic, content_type],
        "read_time": 300  # 默认5分钟阅读时间
    }

# 路由: 跟踪学习进度
@app.post("/api/v1/learning/progress/track")
def track_learning_progress(
    request: LearningProgressRequest,
    authorization: str = Depends(verify_api_key)
):
    """跟踪学习进度"""
    # 记录学习进度（在真实系统中会保存到数据库）
    logger.info(
        f"记录学习进度: user_id={request.user_id}, course_id={request.course_id}, "
        f"progress={request.progress}, completed={request.completed}"
    )
    
    return {"success": True}

# 路由: 获取学习统计信息
@app.get("/api/v1/learning/statistics/{user_id}")
def get_learning_statistics(
    user_id: str,
    authorization: str = Depends(verify_api_key)
):
    """获取学习统计信息"""
    # 加载模拟数据
    stats_data = load_mock_data("learning_statistics.json")
    all_stats = stats_data.get("statistics", [])
    
    # 查找用户统计信息
    user_stats = next((s for s in all_stats if s.get("user_id") == user_id), None)
    
    # 如果找不到，生成随机统计信息
    if not user_stats:
        user_stats = {
            "user_id": user_id,
            "courses_started": random.randint(1, 10),
            "courses_completed": random.randint(0, 5),
            "total_learning_time": random.randint(3600, 86400),  # 1-24小时
            "average_completion_rate": random.uniform(50.0, 100.0),
            "learning_streak": random.randint(0, 14),
            "last_active": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - random.randint(0, 604800))),
            "favorite_topics": random.sample(
                ["中医基础", "针灸", "中药学", "养生保健", "经络学说", "食疗", "太极"],
                k=random.randint(1, 3)
            )
        }
    
    # 删除user_id字段（不是API响应的一部分）
    if "user_id" in user_stats:
        del user_stats["user_id"]
    
    return user_stats

# 主入口
if __name__ == "__main__":
    logger.info(f"启动教育服务模拟器, 端口: {PORT}")
    logger.info(f"模拟延迟: {MOCK_DELAY}ms, 随机失败: {RANDOM_FAILURES}")
    
    # 确保数据目录存在
    DATA_DIR.mkdir(exist_ok=True)
    
    # 启动服务
    uvicorn.run(app, host="0.0.0.0", port=PORT) 