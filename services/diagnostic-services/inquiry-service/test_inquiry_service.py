#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
问诊服务功能测试脚本
"""

import asyncio
import grpc
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from api.grpc import inquiry_service_pb2 as pb2
from api.grpc import inquiry_service_pb2_grpc as pb2_grpc


async def test_inquiry_service():
    """测试问诊服务的核心功能"""
    
    # 创建gRPC通道
    channel = grpc.aio.insecure_channel('localhost:50052')
    stub = pb2_grpc.InquiryServiceStub(channel)
    
    try:
        print("=" * 50)
        print("问诊服务功能测试")
        print("=" * 50)
        
        # 1. 测试开始问诊会话
        print("\n1. 开始问诊会话...")
        start_request = pb2.StartSessionRequest(
            user_id="test_user_001",
            session_type="general",
            language_preference="zh-CN",
            context_data={"source": "test_script"}
        )
        
        session_response = await stub.StartInquirySession(start_request)
        session_id = session_response.session_id
        
        print(f"✓ 会话已创建: {session_id}")
        print(f"  欢迎消息: {session_response.welcome_message}")
        print(f"  建议问题: {', '.join(session_response.suggested_questions)}")
        
        # 2. 测试问诊交互
        print("\n2. 进行问诊交互...")
        test_messages = [
            "我最近总是感觉很累，没有精神",
            "头痛已经持续3天了，主要是偏头痛",
            "晚上睡眠不好，经常失眠，早上起来还是很疲劳"
        ]
        
        for msg in test_messages:
            print(f"\n用户: {msg}")
            
            interaction_request = pb2.InteractionRequest(
                session_id=session_id,
                user_message=msg,
                timestamp=0
            )
            
            # 接收流式响应
            async for response in stub.InteractWithUser(interaction_request):
                print(f"AI: {response.response_text}")
                if response.detected_symptoms:
                    print(f"  检测到的症状: {', '.join(response.detected_symptoms)}")
                if response.follow_up_questions:
                    print(f"  跟进问题: {response.follow_up_questions[0]}")
                    
        # 3. 测试症状提取
        print("\n3. 测试症状提取...")
        symptom_text = "我头痛欲裂，恶心想吐，还伴有胸闷气短，手脚冰凉"
        extraction_request = pb2.SymptomsExtractionRequest(
            text_content=symptom_text,
            user_id="test_user_001",
            language="zh-CN"
        )
        
        symptom_response = await stub.ExtractSymptoms(extraction_request)
        print(f"✓ 提取到 {len(symptom_response.symptoms)} 个症状:")
        for symptom in symptom_response.symptoms:
            print(f"  - {symptom.symptom_name} (严重程度: {symptom.severity}, 置信度: {symptom.confidence:.2f})")
            
        # 4. 测试中医证型映射
        print("\n4. 测试中医证型映射...")
        if symptom_response.symptoms:
            mapping_request = pb2.TCMPatternMappingRequest(
                symptoms=symptom_response.symptoms,
                user_constitution="QI_DEFICIENCY",
                body_locations=symptom_response.body_locations,
                temporal_factors=symptom_response.temporal_factors
            )
            
            pattern_response = await stub.MapToTCMPatterns(mapping_request)
            print(f"✓ 映射到 {len(pattern_response.primary_patterns)} 个主要证型:")
            for pattern in pattern_response.primary_patterns:
                print(f"  - {pattern.pattern_name} ({pattern.category}, 匹配度: {pattern.match_score:.2f})")
                print(f"    描述: {pattern.description}")
                
        # 5. 测试健康风险评估
        print("\n5. 测试健康风险评估...")
        
        # 构建测试病史
        medical_record = pb2.MedicalRecord(
            condition="高血压",
            diagnosis_time=1609459200,  # 2021-01-01
            treatment="药物治疗",
            outcome="控制良好",
            symptoms=["头晕", "耳鸣"]
        )
        
        medical_history = pb2.MedicalHistoryRequest(
            user_id="test_user_001",
            medical_records=[medical_record],
            family_history=["糖尿病", "高血压"],
            additional_info={"age": "45", "gender": "male"}
        )
        
        # 构建健康档案
        health_profile = pb2.HealthProfile(
            user_id="test_user_001",
            constitution_type=pb2.HealthProfile.QI_DEFICIENCY
        )
        
        risk_request = pb2.HealthRiskRequest(
            user_id="test_user_001",
            current_symptoms=symptom_response.symptoms,
            medical_history=medical_history,
            health_profile=health_profile
        )
        
        risk_response = await stub.AssessHealthRisks(risk_request)
        print(f"✓ 健康风险评估完成:")
        print(f"  总体风险评分: {risk_response.overall_risk_score:.2f}")
        
        if risk_response.immediate_risks:
            print(f"\n  即时风险 ({len(risk_response.immediate_risks)} 项):")
            for risk in risk_response.immediate_risks[:3]:
                print(f"    - {risk.risk_name}: {risk.probability:.2f} ({risk.severity})")
                
        if risk_response.long_term_risks:
            print(f"\n  长期风险 ({len(risk_response.long_term_risks)} 项):")
            for risk in risk_response.long_term_risks[:3]:
                print(f"    - {risk.risk_name}: {risk.probability:.2f} ({risk.severity})")
                
        if risk_response.prevention_strategies:
            print(f"\n  预防策略 ({len(risk_response.prevention_strategies)} 项):")
            for strategy in risk_response.prevention_strategies[:3]:
                print(f"    - {strategy.strategy_name}: {strategy.description}")
                print(f"      有效性: {strategy.effectiveness_score:.2f}")
                
        # 6. 结束会话
        print("\n6. 结束问诊会话...")
        end_request = pb2.EndSessionRequest(
            session_id=session_id,
            feedback="测试完成，服务运行正常"
        )
        
        summary = await stub.EndInquirySession(end_request)
        print(f"✓ 会话已结束")
        print(f"  会话持续时间: {summary.session_duration} 秒")
        print(f"  检测到的症状数: {len(summary.detected_symptoms)}")
        print(f"  识别的证型数: {len(summary.tcm_patterns)}")
        print(f"  提供的建议数: {len(summary.recommendations)}")
        
        print("\n" + "=" * 50)
        print("✅ 所有测试完成！问诊服务核心功能正常。")
        print("=" * 50)
        
    except grpc.RpcError as e:
        print(f"\n❌ gRPC错误: {e.code()} - {e.details()}")
        print("请确保问诊服务正在运行（端口: 50052）")
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
    finally:
        await channel.close()


async def test_batch_analysis():
    """测试批量分析功能"""
    channel = grpc.aio.insecure_channel('localhost:50052')
    stub = pb2_grpc.InquiryServiceStub(channel)
    
    try:
        print("\n测试批量数据分析...")
        batch_request = pb2.BatchInquiryRequest(
            session_ids=["session_001", "session_002", "session_003"],
            analysis_type="symptoms",
            analysis_parameters={"time_range": "last_month"}
        )
        
        batch_response = await stub.BatchAnalyzeInquiryData(batch_request)
        print(f"✓ 批量分析完成:")
        print(f"  聚合指标: {dict(batch_response.aggregated_metrics)}")
        print(f"  分析洞察: {len(batch_response.insights)} 项")
        
        for insight in batch_response.insights:
            print(f"    - {insight.insight_type}: {insight.description} (置信度: {insight.confidence:.2f})")
            
    except Exception as e:
        print(f"批量分析测试失败: {str(e)}")
    finally:
        await channel.close()


async def test_medical_history_analysis():
    """测试病史分析功能"""
    channel = grpc.aio.insecure_channel('localhost:50052')
    stub = pb2_grpc.InquiryServiceStub(channel)
    
    try:
        print("\n测试病史分析...")
        
        # 构建测试病史数据
        records = [
            pb2.MedicalRecord(
                condition="慢性胃炎",
                diagnosis_time=1577836800,  # 2020-01-01
                treatment="中药调理",
                outcome="症状缓解",
                symptoms=["胃痛", "腹胀", "食欲不振"]
            ),
            pb2.MedicalRecord(
                condition="失眠症",
                diagnosis_time=1593561600,  # 2020-07-01
                treatment="中西医结合",
                outcome="改善",
                symptoms=["入睡困难", "多梦", "早醒"]
            )
        ]
        
        history_request = pb2.MedicalHistoryRequest(
            user_id="test_user_002",
            medical_records=records,
            family_history=["糖尿病", "高血压", "心脏病"],
            additional_info={
                "age": "52",
                "gender": "female",
                "occupation": "教师"
            }
        )
        
        history_response = await stub.AnalyzeMedicalHistory(history_request)
        
        print(f"✓ 病史分析完成:")
        print(f"  慢性病状况: {len(history_response.chronic_conditions)} 项")
        for condition in history_response.chronic_conditions:
            print(f"    - {condition.condition_name} ({condition.severity})")
            
        print(f"  风险因素: {len(history_response.risk_factors)} 项")
        for factor in history_response.risk_factors[:3]:
            print(f"    - {factor.factor_name}: 风险评分 {factor.risk_score:.2f}")
            
        print(f"  历史证型: {len(history_response.historical_patterns)} 个")
        for pattern in history_response.historical_patterns:
            print(f"    - {pattern.pattern_name} (匹配度: {pattern.match_score:.2f})")
            
    except Exception as e:
        print(f"病史分析测试失败: {str(e)}")
    finally:
        await channel.close()


def main():
    """主函数"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--batch":
            asyncio.run(test_batch_analysis())
        elif sys.argv[1] == "--history":
            asyncio.run(test_medical_history_analysis())
        else:
            print(f"未知参数: {sys.argv[1]}")
            print("用法: python test_inquiry_service.py [--batch|--history]")
    else:
        # 运行主要测试
        asyncio.run(test_inquiry_service())


if __name__ == "__main__":
    main() 