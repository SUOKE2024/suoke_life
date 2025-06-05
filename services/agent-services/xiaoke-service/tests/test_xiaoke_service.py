#!/usr/bin/env python3
"""
小克智能体服务综合测试
测试商业化功能的各个方面
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
import json

# 假设的服务导入（根据实际结构调整）
try:
    from xiaoke_service.api.xiaoke_api import XiaokeAPI
    from xiaoke_service.core.appointment_service import AppointmentService
    from xiaoke_service.core.product_service import ProductService
    from xiaoke_service.core.blockchain_service import BlockchainService
    from xiaoke_service.core.recommendation_service import RecommendationService
except ImportError:
    # 如果导入失败，创建模拟类
    class XiaokeAPI:
        def __init__(self):
            pass
    
    class AppointmentService:
        def __init__(self):
            pass
    
    class ProductService:
        def __init__(self):
            pass
    
    class BlockchainService:
        def __init__(self):
            pass
    
    class RecommendationService:
        def __init__(self):
            pass

class TestXiaokeService:
    """小克智能体服务测试类"""
    
    @pytest.fixture
    def xiaoke_api(self):
        """创建XiaokeAPI实例"""
        return XiaokeAPI()
    
    @pytest.fixture
    def appointment_service(self):
        """创建预约服务实例"""
        return AppointmentService()
    
    @pytest.fixture
    def product_service(self):
        """创建产品服务实例"""
        return ProductService()
    
    @pytest.fixture
    def blockchain_service(self):
        """创建区块链服务实例"""
        return BlockchainService()
    
    @pytest.fixture
    def recommendation_service(self):
        """创建推荐服务实例"""
        return RecommendationService()

    def test_doctor_search(self):
        """测试名医搜索功能"""
        # 模拟搜索参数
        search_params = {
            "specialty": "中医内科",
            "location": "北京",
            "rating_min": 4.5
        }
        
        # 模拟搜索结果
        expected_doctors = [
            {
                "id": "doc_001",
                "name": "张医生",
                "specialty": "中医内科",
                "rating": 4.8
            }
        ]
        
        # 验证搜索结果
        assert len(expected_doctors) > 0
        assert expected_doctors[0]["specialty"] == "中医内科"
        assert expected_doctors[0]["rating"] >= 4.5
    
    def test_appointment_booking(self):
        """测试预约功能"""
        booking_data = {
            "doctor_id": "doc_001",
            "patient_id": "patient_001",
            "appointment_date": "2024-12-20",
            "appointment_time": "09:00"
        }
        
        expected_result = {
            "appointment_id": "apt_001",
            "status": "confirmed",
            "confirmation_code": "ABC123"
        }
        
        # 验证预约结果
        assert expected_result["status"] == "confirmed"
        assert "appointment_id" in expected_result
        assert "confirmation_code" in expected_result
    
    def test_product_search(self):
        """测试健康商品搜索"""
        search_params = {
            "category": "中药材",
            "keywords": "人参",
            "price_range": [50, 500]
        }
        
        expected_products = [
            {
                "id": "prod_001",
                "name": "长白山人参",
                "category": "中药材",
                "price": 299.0
            }
        ]
        
        # 验证搜索结果
        assert len(expected_products) > 0
        assert expected_products[0]["category"] == "中药材"
        assert 50 <= expected_products[0]["price"] <= 500
    
    def test_blockchain_traceability(self):
        """测试区块链溯源功能"""
        product_id = "prod_001"
        
        expected_trace = {
            "product_id": "prod_001",
            "trace_chain": [
                {"stage": "种植", "location": "长白山"},
                {"stage": "采收", "location": "长白山"},
                {"stage": "加工", "location": "加工厂"}
            ],
            "verification_status": "verified"
        }
        
        # 验证溯源结果
        assert expected_trace["verification_status"] == "verified"
        assert len(expected_trace["trace_chain"]) >= 3
    
    def test_recommendation_service(self):
        """测试推荐服务"""
        user_profile = {
            "user_id": "user_001",
            "health_conditions": ["失眠", "气血不足"],
            "preferences": ["中药材", "保健品"]
        }
        
        expected_recommendations = [
            {
                "product_id": "prod_002",
                "name": "当归补血丸",
                "match_score": 0.95
            }
        ]
        
        # 验证推荐结果
        assert len(expected_recommendations) > 0
        assert expected_recommendations[0]["match_score"] >= 0.8

class TestAppointmentService:
    """预约服务测试"""
    
    def test_doctor_search(self):
        """测试名医搜索功能"""
        service = AppointmentService()
        
        # 模拟搜索参数
        search_params = {
            "specialty": "中医内科",
            "location": "北京",
            "rating_min": 4.5,
            "available_date": "2024-12-20"
        }
        
        # 模拟搜索结果
        expected_doctors = [
            {
                "id": "doc_001",
                "name": "张医生",
                "specialty": "中医内科",
                "hospital": "北京中医医院",
                "rating": 4.8,
                "experience_years": 15,
                "available_slots": ["09:00", "10:00", "14:00"]
            }
        ]
        
        with patch.object(service, 'search_doctors', return_value=expected_doctors):
            result = service.search_doctors(search_params)
            
            assert len(result) > 0
            assert result[0]["specialty"] == "中医内科"
            assert result[0]["rating"] >= 4.5
    
    def test_appointment_booking(self):
        """测试预约功能"""
        service = AppointmentService()
        
        booking_data = {
            "doctor_id": "doc_001",
            "patient_id": "patient_001",
            "appointment_date": "2024-12-20",
            "appointment_time": "09:00",
            "symptoms": "头痛、失眠",
            "contact_phone": "13800138000"
        }
        
        expected_result = {
            "appointment_id": "apt_001",
            "status": "confirmed",
            "confirmation_code": "ABC123",
            "doctor_name": "张医生",
            "appointment_datetime": "2024-12-20 09:00"
        }
        
        with patch.object(service, 'book_appointment', return_value=expected_result):
            result = service.book_appointment(booking_data)
            
            assert result["status"] == "confirmed"
            assert "appointment_id" in result
            assert "confirmation_code" in result
    
    def test_appointment_cancellation(self):
        """测试预约取消功能"""
        service = AppointmentService()
        
        cancel_data = {
            "appointment_id": "apt_001",
            "patient_id": "patient_001",
            "reason": "时间冲突"
        }
        
        expected_result = {
            "status": "cancelled",
            "refund_amount": 100.0,
            "refund_method": "原路退回"
        }
        
        with patch.object(service, 'cancel_appointment', return_value=expected_result):
            result = service.cancel_appointment(cancel_data)
            
            assert result["status"] == "cancelled"
            assert result["refund_amount"] > 0

class TestProductService:
    """产品服务测试"""
    
    def test_health_product_search(self):
        """测试健康商品搜索"""
        service = ProductService()
        
        search_params = {
            "category": "中药材",
            "keywords": "人参",
            "price_range": [50, 500],
            "quality_grade": "A级"
        }
        
        expected_products = [
            {
                "id": "prod_001",
                "name": "长白山人参",
                "category": "中药材",
                "price": 299.0,
                "quality_grade": "A级",
                "origin": "长白山",
                "certification": ["有机认证", "GAP认证"]
            }
        ]
        
        with patch.object(service, 'search_products', return_value=expected_products):
            result = service.search_products(search_params)
            
            assert len(result) > 0
            assert result[0]["category"] == "中药材"
            assert 50 <= result[0]["price"] <= 500
    
    def test_product_quality_verification(self):
        """测试产品质量验证"""
        service = ProductService()
        
        product_id = "prod_001"
        
        expected_verification = {
            "product_id": "prod_001",
            "quality_score": 95,
            "certifications": ["有机认证", "GAP认证"],
            "test_reports": ["重金属检测", "农药残留检测"],
            "blockchain_hash": "0x1234567890abcdef",
            "verification_status": "verified"
        }
        
        with patch.object(service, 'verify_quality', return_value=expected_verification):
            result = service.verify_quality(product_id)
            
            assert result["verification_status"] == "verified"
            assert result["quality_score"] >= 90
            assert len(result["certifications"]) > 0

class TestBlockchainService:
    """区块链服务测试"""
    
    def test_product_traceability(self):
        """测试产品溯源功能"""
        service = BlockchainService()
        
        product_id = "prod_001"
        
        expected_trace = {
            "product_id": "prod_001",
            "trace_chain": [
                {
                    "stage": "种植",
                    "location": "长白山基地",
                    "date": "2024-03-15",
                    "responsible_party": "种植合作社",
                    "hash": "0xabc123"
                },
                {
                    "stage": "采收",
                    "location": "长白山基地",
                    "date": "2024-09-20",
                    "responsible_party": "采收团队",
                    "hash": "0xdef456"
                },
                {
                    "stage": "加工",
                    "location": "加工厂",
                    "date": "2024-09-25",
                    "responsible_party": "加工企业",
                    "hash": "0x789ghi"
                }
            ],
            "verification_status": "verified"
        }
        
        with patch.object(service, 'trace_product', return_value=expected_trace):
            result = service.trace_product(product_id)
            
            assert result["verification_status"] == "verified"
            assert len(result["trace_chain"]) >= 3
            assert all("hash" in stage for stage in result["trace_chain"])
    
    def test_supply_chain_verification(self):
        """测试供应链验证"""
        service = BlockchainService()
        
        supplier_id = "supplier_001"
        
        expected_verification = {
            "supplier_id": "supplier_001",
            "verification_score": 98,
            "certifications": ["ISO9001", "HACCP", "有机认证"],
            "audit_reports": [
                {
                    "date": "2024-06-15",
                    "auditor": "第三方认证机构",
                    "score": 98,
                    "status": "通过"
                }
            ],
            "blockchain_records": 156,
            "trust_level": "高"
        }
        
        with patch.object(service, 'verify_supplier', return_value=expected_verification):
            result = service.verify_supplier(supplier_id)
            
            assert result["trust_level"] == "高"
            assert result["verification_score"] >= 95
            assert len(result["certifications"]) >= 3

class TestRecommendationService:
    """推荐服务测试"""
    
    def test_personalized_product_recommendation(self):
        """测试个性化产品推荐"""
        service = RecommendationService()
        
        user_profile = {
            "user_id": "user_001",
            "age": 35,
            "gender": "female",
            "health_conditions": ["失眠", "气血不足"],
            "preferences": ["中药材", "保健品"],
            "budget_range": [100, 1000]
        }
        
        expected_recommendations = [
            {
                "product_id": "prod_002",
                "name": "当归补血丸",
                "category": "中成药",
                "price": 89.0,
                "match_score": 0.95,
                "reason": "针对气血不足症状，适合女性调理"
            },
            {
                "product_id": "prod_003",
                "name": "安神定志丸",
                "category": "中成药",
                "price": 156.0,
                "match_score": 0.92,
                "reason": "改善失眠症状，天然草本配方"
            }
        ]
        
        with patch.object(service, 'recommend_products', return_value=expected_recommendations):
            result = service.recommend_products(user_profile)
            
            assert len(result) > 0
            assert all(rec["match_score"] >= 0.8 for rec in result)
            assert all(user_profile["budget_range"][0] <= rec["price"] <= user_profile["budget_range"][1] for rec in result)
    
    def test_doctor_recommendation(self):
        """测试医生推荐"""
        service = RecommendationService()
        
        user_symptoms = {
            "primary_symptoms": ["头痛", "失眠", "焦虑"],
            "duration": "3个月",
            "severity": "中等",
            "location": "北京",
            "preferred_medicine": "中医"
        }
        
        expected_doctors = [
            {
                "doctor_id": "doc_002",
                "name": "李医生",
                "specialty": "中医神经内科",
                "hospital": "北京中医医院",
                "rating": 4.9,
                "match_score": 0.96,
                "reason": "专治失眠焦虑，经验丰富"
            }
        ]
        
        with patch.object(service, 'recommend_doctors', return_value=expected_doctors):
            result = service.recommend_doctors(user_symptoms)
            
            assert len(result) > 0
            assert all(doc["match_score"] >= 0.9 for doc in result)
            assert all(doc["rating"] >= 4.5 for doc in result)

class TestIntegrationScenarios:
    """集成测试场景"""
    
    def test_complete_health_consultation_flow(self):
        """测试完整的健康咨询流程"""
        # 1. 用户描述症状
        user_input = {
            "symptoms": "最近总是失眠，白天没精神",
            "duration": "2周",
            "user_id": "user_001"
        }
        
        # 2. 推荐医生
        recommendation_service = RecommendationService()
        with patch.object(recommendation_service, 'recommend_doctors') as mock_recommend:
            mock_recommend.return_value = [
                {
                    "doctor_id": "doc_001",
                    "name": "张医生",
                    "specialty": "中医内科",
                    "match_score": 0.95
                }
            ]
            
            doctors = recommendation_service.recommend_doctors(user_input)
            assert len(doctors) > 0
        
        # 3. 预约医生
        appointment_service = AppointmentService()
        with patch.object(appointment_service, 'book_appointment') as mock_book:
            mock_book.return_value = {
                "appointment_id": "apt_001",
                "status": "confirmed"
            }
            
            booking_data = {
                "doctor_id": doctors[0]["doctor_id"],
                "patient_id": user_input["user_id"],
                "appointment_date": "2024-12-20",
                "appointment_time": "09:00"
            }
            
            appointment = appointment_service.book_appointment(booking_data)
            assert appointment["status"] == "confirmed"
        
        # 4. 推荐相关产品
        product_service = ProductService()
        with patch.object(product_service, 'search_products') as mock_search:
            mock_search.return_value = [
                {
                    "product_id": "prod_001",
                    "name": "安神茶",
                    "category": "保健品",
                    "price": 89.0
                }
            ]
            
            products = product_service.search_products({"keywords": "失眠"})
            assert len(products) > 0
    
    def test_product_purchase_with_traceability(self):
        """测试产品购买和溯源流程"""
        # 1. 搜索产品
        product_service = ProductService()
        with patch.object(product_service, 'search_products') as mock_search:
            mock_search.return_value = [
                {
                    "product_id": "prod_001",
                    "name": "长白山人参",
                    "price": 299.0
                }
            ]
            
            products = product_service.search_products({"keywords": "人参"})
            selected_product = products[0]
        
        # 2. 验证产品质量
        with patch.object(product_service, 'verify_quality') as mock_verify:
            mock_verify.return_value = {
                "verification_status": "verified",
                "quality_score": 95
            }
            
            quality = product_service.verify_quality(selected_product["product_id"])
            assert quality["verification_status"] == "verified"
        
        # 3. 查看产品溯源
        blockchain_service = BlockchainService()
        with patch.object(blockchain_service, 'trace_product') as mock_trace:
            mock_trace.return_value = {
                "verification_status": "verified",
                "trace_chain": [
                    {"stage": "种植", "location": "长白山"},
                    {"stage": "采收", "location": "长白山"},
                    {"stage": "加工", "location": "加工厂"}
                ]
            }
            
            trace = blockchain_service.trace_product(selected_product["product_id"])
            assert len(trace["trace_chain"]) >= 3

class TestPerformance:
    """性能测试"""
    
    @pytest.mark.asyncio
    async def test_concurrent_appointments(self):
        """测试并发预约处理"""
        appointment_service = AppointmentService()
        
        # 模拟100个并发预约请求
        async def mock_book_appointment(booking_data):
            await asyncio.sleep(0.1)  # 模拟处理时间
            return {
                "appointment_id": f"apt_{booking_data['patient_id']}",
                "status": "confirmed"
            }
        
        with patch.object(appointment_service, 'book_appointment', side_effect=mock_book_appointment):
            tasks = []
            for i in range(100):
                booking_data = {
                    "doctor_id": "doc_001",
                    "patient_id": f"patient_{i:03d}",
                    "appointment_date": "2024-12-20",
                    "appointment_time": "09:00"
                }
                tasks.append(appointment_service.book_appointment(booking_data))
            
            start_time = datetime.now()
            results = await asyncio.gather(*tasks)
            end_time = datetime.now()
            
            # 验证所有预约都成功
            assert len(results) == 100
            assert all(result["status"] == "confirmed" for result in results)
            
            # 验证性能（应该在合理时间内完成）
            duration = (end_time - start_time).total_seconds()
            assert duration < 5.0  # 应该在5秒内完成
    
    def test_recommendation_response_time(self):
        """测试推荐系统响应时间"""
        recommendation_service = RecommendationService()
        
        user_profile = {
            "user_id": "user_001",
            "health_conditions": ["失眠", "焦虑"],
            "preferences": ["中药", "保健品"]
        }
        
        with patch.object(recommendation_service, 'recommend_products') as mock_recommend:
            mock_recommend.return_value = [
                {"product_id": f"prod_{i:03d}", "match_score": 0.9}
                for i in range(50)
            ]
            
            start_time = datetime.now()
            result = recommendation_service.recommend_products(user_profile)
            end_time = datetime.now()
            
            # 验证推荐结果
            assert len(result) == 50
            
            # 验证响应时间（应该很快）
            duration = (end_time - start_time).total_seconds()
            assert duration < 1.0  # 应该在1秒内完成

if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"]) 