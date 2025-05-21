#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试食疗管理器
"""

import pytest
import json
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

from internal.agent.food_therapy_manager import FoodTherapyManager
from internal.repository.food_repository import FoodRepository

class TestFoodTherapyManager:
    """食疗管理器测试类"""
    
    @pytest.fixture
    def food_therapy_manager(self):
        """创建食疗管理器实例"""
        with patch('internal.agent.food_therapy_manager.get_config'), \
             patch('internal.agent.food_therapy_manager.get_metrics_collector'), \
             patch('internal.agent.food_therapy_manager.FoodRepository'):
            manager = FoodTherapyManager()
            return manager
    
    @pytest.mark.asyncio
    async def test_get_products_for_constitution(self, food_therapy_manager):
        """测试获取适合体质的产品"""
        # 模拟食物存储库
        mock_foods = [
            {
                'id': 'food1',
                'name': '黑木耳',
                'description': '富含铁质和膳食纤维',
                'constitution_benefits': {
                    'QI_DEFICIENCY': 'HIGH',
                    'BLOOD_STASIS': 'MEDIUM'
                },
                'health_benefits': ['补血', '润肺'],
                'seasons': ['SPRING', 'AUTUMN'],
                'contraindications': []
            },
            {
                'id': 'food2',
                'name': '枸杞',
                'description': '滋补肝肾',
                'constitution_benefits': {
                    'YIN_DEFICIENCY': 'HIGH',
                    'QI_DEFICIENCY': 'MEDIUM'
                },
                'health_benefits': ['明目', '补肝'],
                'seasons': ['ALL'],
                'contraindications': []
            }
        ]
        
        # 模拟存储库方法
        food_therapy_manager.food_repo.get_foods_by_constitution = AsyncMock(return_value=mock_foods)
        
        # 调用被测试方法
        result = await food_therapy_manager.get_products_for_constitution(
            'QI_DEFICIENCY', ['贫血'], 'SPRING'
        )
        
        # 验证结果
        assert len(result) == 2
        assert result[0]['name'] == '黑木耳'
        assert result[1]['name'] == '枸杞'
        assert 'score' in result[0]
        assert 'score' in result[1]
        
        # 验证方法调用
        food_therapy_manager.food_repo.get_foods_by_constitution.assert_called_once_with(
            'QI_DEFICIENCY', 20
        )
    
    @pytest.mark.asyncio
    async def test_generate_diet_plan(self, food_therapy_manager):
        """测试生成食疗方案"""
        # 模拟获取适合体质的产品方法
        food_therapy_manager.get_products_for_constitution = AsyncMock(return_value=[
            {
                'id': 'food1',
                'name': '黑木耳',
                'description': '富含铁质和膳食纤维',
                'constitution_benefits': {
                    'QI_DEFICIENCY': 'HIGH'
                },
                'health_benefits': ['补血', '润肺'],
                'food_type': 'VEGETABLE',
                'suitable_meals': ['LUNCH', 'DINNER'],
                'seasons': ['SPRING', 'AUTUMN'],
                'score': 0.9
            },
            {
                'id': 'food2',
                'name': '枸杞',
                'description': '滋补肝肾',
                'constitution_benefits': {
                    'YIN_DEFICIENCY': 'HIGH',
                    'QI_DEFICIENCY': 'MEDIUM'
                },
                'health_benefits': ['明目', '补肝'],
                'food_type': 'HERB',
                'suitable_meals': ['BREAKFAST', 'SNACK'],
                'seasons': ['ALL'],
                'score': 0.7
            }
        ])
        
        # 模拟食物药物相互作用方法
        food_therapy_manager.food_repo.get_food_drug_interactions = AsyncMock(return_value=[])
        
        # 调用被测试方法
        result = await food_therapy_manager.generate_diet_plan(
            'user123', 'QI_DEFICIENCY', ['贫血'], ['素食'], ['花生'], ['补铁片'], 3
        )
        
        # 验证结果
        assert result['user_id'] == 'user123'
        assert result['constitution_type'] == 'QI_DEFICIENCY'
        assert len(result['daily_menus']) == 3
        assert 'summary' in result
        assert 'foods_to_favor' in result['summary']
        assert 'foods_to_avoid' in result['summary']
        
        # 验证方法调用
        food_therapy_manager.get_products_for_constitution.assert_called_once()
        food_therapy_manager.food_repo.get_food_drug_interactions.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_check_food_medicine_pairing(self, food_therapy_manager):
        """测试检查食物药物配伍"""
        # 模拟食物和药物信息
        mock_food = {
            'id': 'food1',
            'name': '黑木耳'
        }
        mock_medicine = {
            'id': 'med1',
            'name': '阿司匹林'
        }
        
        # 模拟相互作用信息
        mock_interaction = {
            'food_id': 'food1',
            'medicine_id': 'med1',
            'type': 'INHIBITION',
            'severity': 'MODERATE',
            'description': '可能减弱药效',
            'recommendation': '服药前后2小时内避免食用'
        }
        
        # 模拟存储库方法
        food_therapy_manager.food_repo.get_food_by_id = AsyncMock(return_value=mock_food)
        food_therapy_manager.food_repo.get_medicine_by_id = AsyncMock(return_value=mock_medicine)
        food_therapy_manager.food_repo.get_food_medicine_interaction = AsyncMock(return_value=mock_interaction)
        
        # 调用被测试方法
        result = await food_therapy_manager.check_food_medicine_pairing(
            ['food1'], ['med1']
        )
        
        # 验证结果
        assert len(result['interactions']) == 1
        assert result['has_interactions'] == True
        assert result['interactions'][0]['food_name'] == '黑木耳'
        assert result['interactions'][0]['medicine_name'] == '阿司匹林'
        
        # 验证方法调用
        food_therapy_manager.food_repo.get_food_by_id.assert_called_once_with('food1')
        food_therapy_manager.food_repo.get_medicine_by_id.assert_called_once_with('med1')
        food_therapy_manager.food_repo.get_food_medicine_interaction.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_recommend_recipes(self, food_therapy_manager):
        """测试推荐食谱"""
        # 模拟获取适合体质的产品方法
        mock_foods = [
            {'id': 'food1', 'name': '黑木耳'},
            {'id': 'food2', 'name': '枸杞'}
        ]
        food_therapy_manager.get_products_for_constitution = AsyncMock(return_value=mock_foods)
        
        # 模拟食谱
        mock_recipes = [
            {
                'id': 'recipe1',
                'name': '枸杞木耳汤',
                'description': '滋补养生汤品',
                'ingredients': ['food1', 'food2'],
                'cooking_time': 30,
                'difficulty': 'MEDIUM',
                'tags': ['养生', '滋补'],
                'cuisine_type': '中式'
            }
        ]
        food_therapy_manager.food_repo.get_recipes_by_foods = AsyncMock(return_value=mock_recipes)
        
        # 调用被测试方法
        result = await food_therapy_manager.recommend_recipes(
            'user123', 'QI_DEFICIENCY', ['贫血'], ['素食'], 'MEDIUM', 30, 5
        )
        
        # 验证结果
        assert len(result) == 1
        assert result[0]['name'] == '枸杞木耳汤'
        assert 'constitution_benefits' in result[0]
        
        # 验证方法调用
        food_therapy_manager.get_products_for_constitution.assert_called_once()
        food_therapy_manager.food_repo.get_recipes_by_foods.assert_called_once()
    
    def test_calculate_food_score(self, food_therapy_manager):
        """测试计算食物匹配分数"""
        # 测试体质高匹配
        food1 = {
            'constitution_benefits': {'QI_DEFICIENCY': 'HIGH'},
            'seasons': ['SPRING'],
            'health_benefits': ['补血', '润肺']
        }
        score1 = food_therapy_manager._calculate_food_score(
            food1, 'QI_DEFICIENCY', ['贫血'], 'SPRING'
        )
        assert score1 > 0.8
        
        # 测试体质中匹配
        food2 = {
            'constitution_benefits': {'QI_DEFICIENCY': 'MEDIUM'},
            'seasons': ['SPRING'],
            'health_benefits': ['补血']
        }
        score2 = food_therapy_manager._calculate_food_score(
            food2, 'QI_DEFICIENCY', ['贫血'], 'SPRING'
        )
        assert 0.5 < score2 < 0.8
        
        # 测试不匹配
        food3 = {
            'constitution_benefits': {'YIN_DEFICIENCY': 'HIGH'},
            'seasons': ['WINTER'],
            'health_benefits': ['明目']
        }
        score3 = food_therapy_manager._calculate_food_score(
            food3, 'QI_DEFICIENCY', ['贫血'], 'SPRING'
        )
        assert score3 < 0.5
    
    def test_select_meal_foods(self, food_therapy_manager):
        """测试为餐点选择食物"""
        foods = [
            {
                'id': 'food1',
                'name': '黑木耳',
                'food_type': 'VEGETABLE',
                'suitable_meals': ['LUNCH', 'DINNER'],
                'score': 0.9,
                'health_benefits': ['补血', '润肺']
            },
            {
                'id': 'food2',
                'name': '枸杞',
                'food_type': 'HERB',
                'suitable_meals': ['BREAKFAST', 'SNACK'],
                'score': 0.7,
                'health_benefits': ['明目', '补肝']
            },
            {
                'id': 'food3',
                'name': '燕麦',
                'food_type': 'GRAIN',
                'suitable_meals': ['BREAKFAST', 'DINNER'],
                'score': 0.8,
                'health_benefits': ['降脂', '助消化']
            }
        ]
        
        # 测试早餐
        breakfast_foods = food_therapy_manager._select_meal_foods(foods, 'BREAKFAST', 2)
        assert len(breakfast_foods) == 2
        assert any(food['name'] == '枸杞' for food in breakfast_foods)
        assert any(food['name'] == '燕麦' for food in breakfast_foods)
        
        # 测试午餐
        lunch_foods = food_therapy_manager._select_meal_foods(foods, 'LUNCH', 1)
        assert len(lunch_foods) == 1
        assert lunch_foods[0]['name'] == '黑木耳' 