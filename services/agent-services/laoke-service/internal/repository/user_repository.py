#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
老克智能体服务 - 用户仓储实现
处理用户数据的存储和检索
"""

import os
import json
import uuid
from typing import Dict, List, Optional, Any
import datetime

from pkg.utils.logger import get_logger

logger = get_logger("user-repository")

class UserRepository:
    """用户仓储类，处理用户数据的存储和检索"""
    
    def __init__(self):
        """初始化用户仓储"""
        # 在实际项目中使用数据库，这里为了简化使用内存存储
        self.users = {}
        self.contribution_history = {}
        self.user_learning_paths = {}
        self.user_courses = {}
        
        # 加载示例数据
        self._load_sample_data()
    
    def _load_sample_data(self):
        """加载示例数据"""
        # 示例用户
        self.users = {
            "user_1": {
                "id": "user_1",
                "username": "zhangsan",
                "display_name": "张三",
                "avatar_url": "https://example.com/avatars/zhangsan.jpg",
                "role": "STUDENT",
                "specialization": ["中医养生", "太极"],
                "contribution_score": 120,
                "joined_at": (datetime.datetime.utcnow() - datetime.timedelta(days=30)).isoformat()
            },
            "user_2": {
                "id": "user_2",
                "username": "lisi",
                "display_name": "李四",
                "avatar_url": "https://example.com/avatars/lisi.jpg",
                "role": "INSTRUCTOR",
                "specialization": ["经络学", "针灸"],
                "contribution_score": 450,
                "joined_at": (datetime.datetime.utcnow() - datetime.timedelta(days=90)).isoformat()
            },
            "user_3": {
                "id": "user_3",
                "username": "wangwu",
                "display_name": "王五",
                "avatar_url": "https://example.com/avatars/wangwu.jpg",
                "role": "EXPERT",
                "specialization": ["中药学", "方剂学"],
                "contribution_score": 780,
                "joined_at": (datetime.datetime.utcnow() - datetime.timedelta(days=180)).isoformat()
            }
        }
        
        # 示例用户学习路径
        self.user_learning_paths = {
            "user_1": [
                {
                    "path_id": "path_1",
                    "enrolled_at": (datetime.datetime.utcnow() - datetime.timedelta(days=15)).isoformat(),
                    "progress": 0.3,
                    "last_activity": (datetime.datetime.utcnow() - datetime.timedelta(days=2)).isoformat()
                }
            ],
            "user_2": [
                {
                    "path_id": "path_2",
                    "enrolled_at": (datetime.datetime.utcnow() - datetime.timedelta(days=45)).isoformat(),
                    "progress": 0.8,
                    "last_activity": (datetime.datetime.utcnow() - datetime.timedelta(days=5)).isoformat()
                },
                {
                    "path_id": "path_3",
                    "enrolled_at": (datetime.datetime.utcnow() - datetime.timedelta(days=30)).isoformat(),
                    "progress": 0.5,
                    "last_activity": (datetime.datetime.utcnow() - datetime.timedelta(days=1)).isoformat()
                }
            ]
        }
        
        # 示例用户课程
        self.user_courses = {
            "user_1": [
                {
                    "course_id": "course_1",
                    "enrolled_at": (datetime.datetime.utcnow() - datetime.timedelta(days=10)).isoformat(),
                    "progress": 0.2,
                    "completed_modules": ["module_1_1"],
                    "last_activity": (datetime.datetime.utcnow() - datetime.timedelta(days=3)).isoformat()
                }
            ],
            "user_3": [
                {
                    "course_id": "course_2",
                    "enrolled_at": (datetime.datetime.utcnow() - datetime.timedelta(days=60)).isoformat(),
                    "progress": 1.0,
                    "completed_modules": ["module_2_1", "module_2_2", "module_2_3"],
                    "last_activity": (datetime.datetime.utcnow() - datetime.timedelta(days=15)).isoformat(),
                    "completed_at": (datetime.datetime.utcnow() - datetime.timedelta(days=15)).isoformat(),
                    "certificate_id": "cert_123456"
                }
            ]
        }
        
        # 示例贡献历史
        self.contribution_history = {
            "user_1": [
                {
                    "id": "contrib_1",
                    "type": "post_creation",
                    "points": 5,
                    "timestamp": (datetime.datetime.utcnow() - datetime.timedelta(days=10)).isoformat(),
                    "description": "创建了文章《四季养生指南》"
                },
                {
                    "id": "contrib_2",
                    "type": "comment",
                    "points": 1,
                    "timestamp": (datetime.datetime.utcnow() - datetime.timedelta(days=5)).isoformat(),
                    "description": "评论了文章《中医体质辨识》"
                }
            ],
            "user_2": [
                {
                    "id": "contrib_3",
                    "type": "course_creation",
                    "points": 50,
                    "timestamp": (datetime.datetime.utcnow() - datetime.timedelta(days=45)).isoformat(),
                    "description": "创建了课程《经络穴位详解》"
                }
            ],
            "user_3": [
                {
                    "id": "contrib_4",
                    "type": "knowledge_review",
                    "points": 30,
                    "timestamp": (datetime.datetime.utcnow() - datetime.timedelta(days=30)).isoformat(),
                    "description": "审核通过了10篇中药知识文章"
                }
            ]
        }
    
    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """获取用户信息"""
        logger.debug(f"获取用户信息: {user_id}")
        
        # 实际项目中应该从数据库中获取
        return self.users.get(user_id)
    
    async def get_users(self, user_ids: List[str]) -> List[Dict[str, Any]]:
        """批量获取用户信息"""
        logger.debug(f"批量获取用户信息: {user_ids}")
        
        users = []
        for user_id in user_ids:
            user = await self.get_user(user_id)
            if user:
                users.append(user)
        
        return users
    
    async def create_user(self, user_data: Dict[str, Any]) -> str:
        """创建用户"""
        logger.info(f"创建用户: {user_data.get('username')}")
        
        user_id = f"user_{uuid.uuid4().hex[:8]}"
        user_data["id"] = user_id
        user_data["joined_at"] = datetime.datetime.utcnow().isoformat()
        user_data["contribution_score"] = 0
        
        # 实际项目中应该保存到数据库
        self.users[user_id] = user_data
        
        return user_id
    
    async def update_user(self, user_id: str, user_data: Dict[str, Any]) -> bool:
        """更新用户信息"""
        logger.info(f"更新用户: {user_id}")
        
        if user_id not in self.users:
            logger.warning(f"用户不存在: {user_id}")
            return False
        
        # 更新用户数据
        for key, value in user_data.items():
            if key != "id" and key != "joined_at":  # 不允许修改ID和加入时间
                self.users[user_id][key] = value
        
        return True
    
    async def get_user_contribution_history(self, user_id: str) -> List[Dict[str, Any]]:
        """获取用户贡献历史"""
        logger.debug(f"获取用户贡献历史: {user_id}")
        
        # 实际项目中应该从数据库中获取
        return self.contribution_history.get(user_id, [])
    
    async def add_contribution_points(self, user_id: str, points: int, 
                                   description: str = None, 
                                   type: str = "generic") -> Dict[str, Any]:
        """添加贡献积分"""
        logger.info(f"添加贡献积分: 用户={user_id}, 积分={points}, 类型={type}")
        
        if user_id not in self.users:
            logger.warning(f"用户不存在: {user_id}")
            return {
                "success": False,
                "message": f"用户不存在: {user_id}"
            }
        
        # 添加积分
        self.users[user_id]["contribution_score"] += points
        
        # 记录贡献
        contribution = {
            "id": f"contrib_{uuid.uuid4().hex[:8]}",
            "type": type,
            "points": points,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "description": description or f"获得了{points}点贡献积分"
        }
        
        if user_id not in self.contribution_history:
            self.contribution_history[user_id] = []
        
        self.contribution_history[user_id].append(contribution)
        
        return {
            "success": True,
            "contribution_id": contribution["id"],
            "new_score": self.users[user_id]["contribution_score"]
        }
    
    async def get_user_learning_paths(self, user_id: str) -> List[Dict[str, Any]]:
        """获取用户学习路径"""
        logger.debug(f"获取用户学习路径: {user_id}")
        
        # 实际项目中应该从数据库中获取
        return self.user_learning_paths.get(user_id, [])
    
    async def enroll_learning_path(self, user_id: str, path_id: str) -> bool:
        """用户报名学习路径"""
        logger.info(f"用户报名学习路径: 用户={user_id}, 路径={path_id}")
        
        if user_id not in self.users:
            logger.warning(f"用户不存在: {user_id}")
            return False
        
        # 检查是否已报名
        existing_paths = self.user_learning_paths.get(user_id, [])
        for path in existing_paths:
            if path["path_id"] == path_id:
                logger.warning(f"用户已经报名该学习路径: 用户={user_id}, 路径={path_id}")
                return False
        
        # 添加学习路径
        enrollment = {
            "path_id": path_id,
            "enrolled_at": datetime.datetime.utcnow().isoformat(),
            "progress": 0.0,
            "last_activity": datetime.datetime.utcnow().isoformat()
        }
        
        if user_id not in self.user_learning_paths:
            self.user_learning_paths[user_id] = []
        
        self.user_learning_paths[user_id].append(enrollment)
        
        return True
    
    async def update_learning_progress(self, user_id: str, path_id: str, 
                                    progress: float) -> bool:
        """更新学习进度"""
        logger.info(f"更新学习进度: 用户={user_id}, 路径={path_id}, 进度={progress}")
        
        if user_id not in self.user_learning_paths:
            logger.warning(f"用户未报名任何学习路径: {user_id}")
            return False
        
        # 更新进度
        for path in self.user_learning_paths[user_id]:
            if path["path_id"] == path_id:
                path["progress"] = progress
                path["last_activity"] = datetime.datetime.utcnow().isoformat()
                
                # 如果完成，添加贡献积分
                if progress >= 1.0 and path.get("progress", 0) < 1.0:
                    await self.add_contribution_points(
                        user_id=user_id,
                        points=20,
                        description=f"完成学习路径",
                        type="path_completion"
                    )
                
                return True
        
        logger.warning(f"用户未报名该学习路径: 用户={user_id}, 路径={path_id}")
        return False
    
    async def get_user_courses(self, user_id: str) -> List[Dict[str, Any]]:
        """获取用户报名的课程"""
        logger.debug(f"获取用户课程: {user_id}")
        
        # 实际项目中应该从数据库中获取
        return self.user_courses.get(user_id, [])
    
    async def enroll_course(self, user_id: str, course_id: str) -> bool:
        """用户报名课程"""
        logger.info(f"用户报名课程: 用户={user_id}, 课程={course_id}")
        
        if user_id not in self.users:
            logger.warning(f"用户不存在: {user_id}")
            return False
        
        # 检查是否已报名
        existing_courses = self.user_courses.get(user_id, [])
        for course in existing_courses:
            if course["course_id"] == course_id:
                logger.warning(f"用户已经报名该课程: 用户={user_id}, 课程={course_id}")
                return False
        
        # 添加课程
        enrollment = {
            "course_id": course_id,
            "enrolled_at": datetime.datetime.utcnow().isoformat(),
            "progress": 0.0,
            "completed_modules": [],
            "last_activity": datetime.datetime.utcnow().isoformat()
        }
        
        if user_id not in self.user_courses:
            self.user_courses[user_id] = []
        
        self.user_courses[user_id].append(enrollment)
        
        return True
    
    async def complete_course_module(self, user_id: str, course_id: str, 
                                  module_id: str) -> bool:
        """完成课程模块"""
        logger.info(f"完成课程模块: 用户={user_id}, 课程={course_id}, 模块={module_id}")
        
        if user_id not in self.user_courses:
            logger.warning(f"用户未报名任何课程: {user_id}")
            return False
        
        # 查找课程
        course_found = False
        for course in self.user_courses[user_id]:
            if course["course_id"] == course_id:
                course_found = True
                
                # 检查模块是否已完成
                if module_id in course.get("completed_modules", []):
                    logger.info(f"模块已完成: 用户={user_id}, 课程={course_id}, 模块={module_id}")
                    return True
                
                # 添加已完成模块
                if "completed_modules" not in course:
                    course["completed_modules"] = []
                
                course["completed_modules"].append(module_id)
                course["last_activity"] = datetime.datetime.utcnow().isoformat()
                
                # 更新进度 (简化实现，实际应根据课程总模块数计算)
                course["progress"] = len(course["completed_modules"]) / 3  # 假设每个课程有3个模块
                
                # 如果课程完成，添加完成时间和贡献积分
                if course["progress"] >= 1.0:
                    course["completed_at"] = datetime.datetime.utcnow().isoformat()
                    course["certificate_id"] = f"cert_{uuid.uuid4().hex[:8]}"
                    
                    await self.add_contribution_points(
                        user_id=user_id,
                        points=30,
                        description=f"完成课程",
                        type="course_completion"
                    )
                
                return True
        
        if not course_found:
            logger.warning(f"用户未报名该课程: 用户={user_id}, 课程={course_id}")
        
        return False

# 创建单例实例
user_repository = UserRepository() 