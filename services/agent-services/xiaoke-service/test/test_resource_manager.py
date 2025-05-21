#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试资源管理器
"""

import pytest
import json
import asyncio
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, AsyncMock

from internal.scheduler.resource_manager import ResourceManager
from internal.domain.models import AppointmentStatus, MedicalResourceType

class TestResourceManager:
    """资源管理器测试类"""
    
    @pytest.fixture
    def resource_manager(self):
        """创建资源管理器实例"""
        with patch('internal.scheduler.resource_manager.get_config'), \
             patch('internal.scheduler.resource_manager.get_metrics_collector'), \
             patch('internal.scheduler.resource_manager.ResourceRepository'), \
             patch('internal.scheduler.resource_manager.AppointmentRepository'):
            manager = ResourceManager()
            # 设置权重
            manager.weights = {
                'constitution_match': 0.4,
                'location_proximity': 0.2,
                'rating': 0.2,
                'availability': 0.2
            }
            return manager
    
    @pytest.mark.asyncio
    async def test_schedule_resources(self, resource_manager):
        """测试调度医疗资源"""
        # 模拟医疗资源
        mock_resources = [
            {
                'id': 'doc1',
                'name': '张医生',
                'resource_type': MedicalResourceType.TCM_DOCTOR.value,
                'location': '北京',
                'rating': 4.8,
                'description': '经验丰富的中医师',
                'price': 200.0,
                'available_times': [
                    '2023-07-01T09:00',
                    '2023-07-01T10:00',
                    '2023-07-01T15:00'
                ],
                'specialties': ['内科', '调理脾胃'],
                'supported_constitution_types': ['QI_DEFICIENCY', 'PHLEGM_DAMPNESS'],
                'metadata': {
                    'experience_years': '15',
                    'hospital': '北京中医医院'
                }
            },
            {
                'id': 'doc2',
                'name': '李医生',
                'resource_type': MedicalResourceType.TCM_DOCTOR.value,
                'location': '上海',
                'rating': 4.5,
                'description': '专注于肝胆调理',
                'price': 180.0,
                'available_times': [
                    '2023-07-01T14:00',
                    '2023-07-01T16:00'
                ],
                'specialties': ['肝胆科', '调理情绪'],
                'supported_constitution_types': ['QI_DEPRESSION', 'DAMP_HEAT'],
                'metadata': {
                    'experience_years': '10',
                    'hospital': '上海中医药大学附属医院'
                }
            }
        ]
        
        # 模拟存储库方法
        resource_manager.resource_repo.get_resources_by_type = AsyncMock(return_value=mock_resources)
        
        # 调用被测试方法
        result = await resource_manager.schedule_resources(
            user_id='user123',
            resource_type=MedicalResourceType.TCM_DOCTOR.value,
            constitution_type='QI_DEFICIENCY',
            location='北京',
            requirements=['内科'],
            page_size=10,
            page_number=1
        )
        
        # 验证结果
        assert len(result['resources']) == 2
        assert result['resources'][0]['id'] == 'doc1'  # 应该排在第一位
        assert result['resources'][1]['id'] == 'doc2'
        assert 'score' in result['resources'][0]
        assert result['resources'][0]['score'] > result['resources'][1]['score']  # 第一个医生的分数应更高
        
        # 验证方法调用
        resource_manager.resource_repo.get_resources_by_type.assert_called_once_with(
            MedicalResourceType.TCM_DOCTOR.value
        )
    
    @pytest.mark.asyncio
    async def test_manage_appointment(self, resource_manager):
        """测试预约管理"""
        # 模拟医生信息
        mock_doctor = {
            'id': 'doc1',
            'name': '张医生',
            'location': '北京中医医院',
            'available_times': [
                '2023-07-01T09:00',
                '2023-07-01T10:00',
                '2023-07-01T15:00'
            ]
        }
        
        # 模拟存储库方法
        resource_manager.resource_repo.get_resource_by_id = AsyncMock(return_value=mock_doctor)
        resource_manager.appointment_repo.get_appointments_by_time = AsyncMock(return_value=[])
        resource_manager.appointment_repo.create_appointment = AsyncMock(return_value='appt123')
        
        # 调用被测试方法 - 可用时间
        result1 = await resource_manager.manage_appointment(
            user_id='user123',
            doctor_id='doc1',
            appointment_type='ONLINE_CONSULTATION',
            preferred_time='2023-07-01T09:00',
            symptoms='感冒，咳嗽，发热',
            constitution_type='QI_DEFICIENCY'
        )
        
        # 验证结果 - 可用时间
        assert result1['status'] == AppointmentStatus.CONFIRMED.value
        assert result1['doctor_name'] == '张医生'
        assert result1['meeting_link'].startswith('https://meeting.suoke.life')
        
        # 模拟预约冲突情况
        mock_existing_appointment = [{'id': 'appt999'}]
        resource_manager.appointment_repo.get_appointments_by_time = AsyncMock(return_value=mock_existing_appointment)
        resource_manager._find_next_available_time = AsyncMock(return_value=datetime.fromisoformat('2023-07-01T10:00'))
        
        # 调用被测试方法 - 时间冲突
        result2 = await resource_manager.manage_appointment(
            user_id='user456',
            doctor_id='doc1',
            appointment_type='ONLINE_CONSULTATION',
            preferred_time='2023-07-01T09:00',
            symptoms='头晕，疲劳',
            constitution_type='YANG_DEFICIENCY'
        )
        
        # 验证结果 - 时间冲突
        assert result2['status'] == AppointmentStatus.PENDING.value
        assert result2['confirmed_time'] == '2023-07-01T10:00'
        
        # 验证方法调用
        assert resource_manager.resource_repo.get_resource_by_id.call_count == 2
        assert resource_manager.appointment_repo.create_appointment.call_count == 2
    
    def test_score_resources(self, resource_manager):
        """测试资源评分"""
        # 测试数据
        resources = [
            {
                'id': 'doc1',
                'name': '张医生',
                'location': '北京',
                'rating': 4.8,
                'available_times': ['2023-07-01T09:00', '2023-07-01T10:00'],
                'supported_constitution_types': ['QI_DEFICIENCY', 'PHLEGM_DAMPNESS'],
                'specialties': ['内科', '调理脾胃']
            },
            {
                'id': 'doc2',
                'name': '李医生',
                'location': '上海',
                'rating': 4.5,
                'available_times': ['2023-07-01T14:00'],
                'supported_constitution_types': ['QI_DEPRESSION', 'DAMP_HEAT'],
                'specialties': ['肝胆科']
            },
            {
                'id': 'doc3',
                'name': '王医生',
                'location': '北京',
                'rating': 4.2,
                'available_times': ['2023-07-01T11:00', '2023-07-01T14:00', '2023-07-01T16:00'],
                'supported_constitution_types': ['ALL'],
                'specialties': ['内科', '养生']
            }
        ]
        
        # 调用被测试方法
        result = resource_manager._score_resources(
            resources=resources,
            constitution_type='QI_DEFICIENCY',
            location='北京',
            requirements=['内科']
        )
        
        # 验证结果
        assert len(result) == 3
        assert result[0]['id'] == 'doc1'  # 张医生应该排第一
        assert result[1]['id'] == 'doc3'  # 王医生应该排第二
        assert result[2]['id'] == 'doc2'  # 李医生应该排第三
        
        # 验证分数
        assert result[0]['score'] > result[1]['score'] > result[2]['score']
        assert 'requirement_match' in result[0]
        assert result[0]['requirement_match']['内科'] == True
        assert result[2]['requirement_match']['内科'] == False
    
    def test_calculate_constitution_match(self, resource_manager):
        """测试体质匹配度计算"""
        # 完全匹配
        resource1 = {
            'supported_constitution_types': ['QI_DEFICIENCY', 'PHLEGM_DAMPNESS']
        }
        score1 = resource_manager._calculate_constitution_match(resource1, 'QI_DEFICIENCY')
        assert score1 == 1.0
        
        # 适合所有体质
        resource2 = {
            'supported_constitution_types': ['ALL']
        }
        score2 = resource_manager._calculate_constitution_match(resource2, 'QI_DEFICIENCY')
        assert score2 == 0.8
        
        # 不匹配
        resource3 = {
            'supported_constitution_types': ['YIN_DEFICIENCY', 'YANG_DEFICIENCY']
        }
        score3 = resource_manager._calculate_constitution_match(resource3, 'QI_DEFICIENCY')
        assert score3 == 0.3
        
        # 无体质信息
        resource4 = {}
        score4 = resource_manager._calculate_constitution_match(resource4, 'QI_DEFICIENCY')
        assert score4 == 0.5
    
    def test_calculate_location_proximity(self, resource_manager):
        """测试位置接近度计算"""
        # 完全匹配
        resource1 = {'location': '北京'}
        score1 = resource_manager._calculate_location_proximity(resource1, '北京')
        assert score1 == 1.0
        
        # 不匹配
        resource2 = {'location': '上海'}
        score2 = resource_manager._calculate_location_proximity(resource2, '北京')
        assert score2 == 0.4
        
        # 无位置信息
        resource3 = {}
        score3 = resource_manager._calculate_location_proximity(resource3, '北京')
        assert score3 == 0.5
        
        # 无查询位置
        score4 = resource_manager._calculate_location_proximity(resource1, '')
        assert score4 == 0.5
    
    def test_calculate_availability(self, resource_manager):
        """测试可用性计算"""
        # 多个可用时间
        resource1 = {'available_times': ['time1', 'time2', 'time3', 'time4']}
        score1 = resource_manager._calculate_availability(resource1)
        assert score1 == 0.4  # 4/10 = 0.4
        
        # 少量可用时间
        resource2 = {'available_times': ['time1']}
        score2 = resource_manager._calculate_availability(resource2)
        assert score2 == 0.1  # 1/10 = 0.1
        
        # 无可用时间
        resource3 = {'available_times': []}
        score3 = resource_manager._calculate_availability(resource3)
        assert score3 == 0.0
        
        # 无available_times字段
        resource4 = {}
        score4 = resource_manager._calculate_availability(resource4)
        assert score4 == 0.0
    
    def test_check_requirements(self, resource_manager):
        """测试需求匹配检查"""
        resource = {'specialties': ['内科', '外科', '调理脾胃']}
        
        # 完全匹配
        result1 = resource_manager._check_requirements(resource, ['内科', '外科'])
        assert result1['内科'] == True
        assert result1['外科'] == True
        
        # 部分匹配
        result2 = resource_manager._check_requirements(resource, ['内科', '骨科'])
        assert result2['内科'] == True
        assert result2['骨科'] == False
        
        # 无匹配
        result3 = resource_manager._check_requirements(resource, ['骨科', '神经科'])
        assert result3['骨科'] == False
        assert result3['神经科'] == False
        
        # 无specialties字段
        resource2 = {}
        result4 = resource_manager._check_requirements(resource2, ['内科'])
        assert result4['内科'] == False 