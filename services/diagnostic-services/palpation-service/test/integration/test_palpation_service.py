"""
test_palpation_service - 索克生活项目模块
"""

from pathlib import Path
import grpc
import sys
import time

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
切诊服务集成测试
"""


# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

def test_health_check():
    """测试健康检查接口"""
    print("测试健康检查接口...")
    
    # 创建gRPC通道
    channel = grpc.insecure_channel('localhost:50051')
    stub = pb2_grpc.PalpationServiceStub(channel)
    
    try:
        # 调用健康检查
        request = pb2.HealthCheckRequest(level=pb2.HealthCheckRequest.FULL)
        response = stub.HealthCheck(request)
        
        print(f"健康检查状态: {pb2.HealthCheckResponse.ServiceStatus.Name(response.status)}")
        print(f"服务版本: {response.version}")
        print(f"组件状态:")
        for component in response.components:
            print(f"  - {component.component_name}: {pb2.HealthCheckResponse.ServiceStatus.Name(component.status)}")
            print(f"    详情: {component.details}")
            print(f"    响应时间: {component.response_time_ms}ms")
        
        return response.status == pb2.HealthCheckResponse.SERVING
        
    except grpc.RpcError as e:
        print(f"健康检查失败: {e}")
        return False
    finally:
        channel.close()

def test_pulse_session():
    """测试脉诊会话流程"""
    print("\n测试脉诊会话流程...")
    
    # 创建gRPC通道
    channel = grpc.insecure_channel('localhost:50051')
    stub = pb2_grpc.PalpationServiceStub(channel)
    
    try:
        # 1. 开始脉诊会话
        print("1. 开始脉诊会话...")
        device_info = pb2.DeviceInfo(
            device_id="test-device-001",
            model="索克WP-100",
            firmware_version="1.0.0",
            sensor_types=["pressure", "velocity"]
        )
        
        calibration_data = pb2.SensorCalibrationData(
            calibration_values=[1.0, 1.0, 1.0],
            calibration_timestamp=int(time.time()),
            calibration_operator="测试操作员"
        )
        
        start_request = pb2.StartPulseSessionRequest(
            user_id="test-user-001",
            device_info=device_info,
            calibration_data=calibration_data
        )
        
        start_response = stub.StartPulseSession(start_request)
        
        if not start_response.success:
            print(f"开始会话失败: {start_response.error_message}")
            return False
        
        session_id = start_response.session_id
        print(f"会话ID: {session_id}")
        print(f"采样配置: 采样率={start_response.sampling_config.sampling_rate}Hz")
        
        # 2. 发送脉搏数据
        print("\n2. 发送脉搏数据...")
        
        def generate_pulse_data():
            """生成模拟脉搏数据"""
            
            positions = [
                pb2.PulsePosition.CUN_LEFT,
                pb2.PulsePosition.GUAN_LEFT,
                pb2.PulsePosition.CHI_LEFT,
                pb2.PulsePosition.CUN_RIGHT,
                pb2.PulsePosition.GUAN_RIGHT,
                pb2.PulsePosition.CHI_RIGHT
            ]
            
            for position in positions:
                # 每个位置发送10个数据包
                for i in range(10):
                    # 生成模拟脉搏波形数据
                    t = np.linspace(0, 1, 100)
                    # 模拟脉搏波形：主波 + 重搏波
                    pressure = 0.5 + 0.3 * np.sin(2 * np.pi * t) + 0.1 * np.sin(4 * np.pi * t)
                    velocity = 0.3 * np.cos(2 * np.pi * t) + 0.05 * np.cos(4 * np.pi * t)
                    
                    # 添加一些噪声
                    pressure += np.random.normal(0, 0.02, len(pressure))
                    velocity += np.random.normal(0, 0.01, len(velocity))
                    
                    packet = pb2.PulseDataPacket(
                        session_id=session_id,
                        timestamp=int(time.time() * 1000) + i * 100,
                        pressure_data=pressure.tolist(),
                        velocity_data=velocity.tolist(),
                        position=position,
                        skin_temperature=36.5 + np.random.normal(0, 0.1),
                        skin_moisture=0.5 + np.random.normal(0, 0.05)
                    )
                    
                    yield packet
                    time.sleep(0.1)  # 模拟实时数据流
        
        record_response = stub.RecordPulseData(generate_pulse_data())
        
        if not record_response.success:
            print(f"记录数据失败: {record_response.error_message}")
            return False
        
        print(f"成功接收 {record_response.packets_received} 个数据包")
        
        # 3. 提取脉象特征
        print("\n3. 提取脉象特征...")
        
        extract_request = pb2.ExtractPulseFeaturesRequest(
            session_id=session_id,
            include_raw_data=False
        )
        
        extract_response = stub.ExtractPulseFeatures(extract_request)
        
        if not extract_response.success:
            print(f"提取特征失败: {extract_response.error_message}")
            return False
        
        print(f"提取到 {len(extract_response.features)} 个特征")
        print(f"信号质量: {extract_response.quality_metrics.signal_quality}")
        print(f"噪声水平: {extract_response.quality_metrics.noise_level}")
        print(f"数据有效: {extract_response.quality_metrics.is_valid}")
        
        # 显示部分特征
        for feature in extract_response.features[:5]:
            print(f"  - {feature.feature_name}: {feature.feature_value:.3f} ({feature.feature_description})")
        
        # 4. 分析脉象
        print("\n4. 分析脉象...")
        
        analyze_request = pb2.AnalyzePulseRequest(
            session_id=session_id,
            user_id="test-user-001",
            include_detailed_analysis=True,
            options=pb2.AnalysisOptions(
                use_tcm_model=True,
                use_western_model=False,
                analysis_depth="standard"
            )
        )
        
        analyze_response = stub.AnalyzePulse(analyze_request)
        
        if not analyze_response.success:
            print(f"分析脉象失败: {analyze_response.error_message}")
            return False
        
        print(f"识别到的脉象类型:")
        for pulse_type in analyze_response.pulse_types:
            print(f"  - {pb2.PulseWaveType.Name(pulse_type)}")
        
        print(f"\n中医证型:")
        for pattern in analyze_response.tcm_patterns:
            print(f"  - {pattern.pattern_name} (置信度: {pattern.confidence:.1%})")
            print(f"    描述: {pattern.description}")
        
        print(f"\n脏腑状态:")
        for condition in analyze_response.organ_conditions:
            print(f"  - {condition.organ_name}: {condition.condition} (严重程度: {condition.severity:.1f})")
        
        print(f"\n分析总结: {analyze_response.analysis_summary}")
        print(f"置信度评分: {analyze_response.confidence_score:.1%}")
        
        return True
        
    except grpc.RpcError as e:
        print(f"测试失败: {e}")
        return False
    finally:
        channel.close()

def test_abdominal_palpation():
    """测试腹诊分析"""
    print("\n测试腹诊分析...")
    
    # 创建gRPC通道
    channel = grpc.insecure_channel('localhost:50051')
    stub = pb2_grpc.PalpationServiceStub(channel)
    
    try:
        # 准备腹诊数据
        regions = [
            pb2.AbdominalRegionData(
                region_id="epigastric",
                region_name="上腹部",
                tenderness_level=0.3,
                tension_level=0.4,
                has_mass=False,
                texture_description="柔软",
                comments="轻度压痛"
            ),
            pb2.AbdominalRegionData(
                region_id="umbilical",
                region_name="脐周",
                tenderness_level=0.1,
                tension_level=0.2,
                has_mass=False,
                texture_description="正常",
                comments="无异常"
            ),
            pb2.AbdominalRegionData(
                region_id="right_hypochondriac",
                region_name="右胁部",
                tenderness_level=0.6,
                tension_level=0.7,
                has_mass=False,
                texture_description="紧张",
                comments="明显压痛"
            )
        ]
        
        request = pb2.AbdominalPalpationRequest(
            user_id="test-user-001",
            regions=regions,
            include_detailed_analysis=True
        )
        
        response = stub.AnalyzeAbdominalPalpation(request)
        
        if not response.success:
            print(f"腹诊分析失败: {response.error_message}")
            return False
        
        print(f"腹诊发现:")
        for finding in response.findings:
            print(f"  - 区域: {finding.region_id}")
            print(f"    类型: {finding.finding_type}")
            print(f"    描述: {finding.description}")
            print(f"    置信度: {finding.confidence:.1%}")
            if finding.potential_causes:
                print(f"    可能原因: {', '.join(finding.potential_causes)}")
        
        print(f"\n分析总结: {response.analysis_summary}")
        
        return True
        
    except grpc.RpcError as e:
        print(f"腹诊测试失败: {e}")
        return False
    finally:
        channel.close()

def test_skin_palpation():
    """测试皮肤触诊分析"""
    print("\n测试皮肤触诊分析...")
    
    # 创建gRPC通道
    channel = grpc.insecure_channel('localhost:50051')
    stub = pb2_grpc.PalpationServiceStub(channel)
    
    try:
        # 准备皮肤触诊数据
        regions = [
            pb2.SkinRegionData(
                region_id="face",
                region_name="面部",
                moisture_level=0.3,
                elasticity=0.4,
                texture="干燥",
                temperature=36.2,
                color="偏黄"
            ),
            pb2.SkinRegionData(
                region_id="hands",
                region_name="手部",
                moisture_level=0.2,
                elasticity=0.3,
                texture="粗糙",
                temperature=35.8,
                color="苍白"
            )
        ]
        
        request = pb2.SkinPalpationRequest(
            user_id="test-user-001",
            regions=regions
        )
        
        response = stub.AnalyzeSkinPalpation(request)
        
        if not response.success:
            print(f"皮肤触诊分析失败: {response.error_message}")
            return False
        
        print(f"皮肤触诊发现:")
        for finding in response.findings:
            print(f"  - 区域: {finding.region_id}")
            print(f"    类型: {finding.finding_type}")
            print(f"    描述: {finding.description}")
            if finding.related_conditions:
                print(f"    相关状况: {', '.join(finding.related_conditions)}")
        
        print(f"\n分析总结: {response.analysis_summary}")
        
        return True
        
    except grpc.RpcError as e:
        print(f"皮肤触诊测试失败: {e}")
        return False
    finally:
        channel.close()

def main():
    """主测试函数"""
    print("=== 切诊服务集成测试 ===\n")
    
    # 等待服务启动
    print("等待服务启动...")
    time.sleep(2)
    
    # 执行测试
    tests = [
        ("健康检查", test_health_check),
        ("脉诊会话", test_pulse_session),
        ("腹诊分析", test_abdominal_palpation),
        ("皮肤触诊", test_skin_palpation)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"执行测试: {test_name}")
        print('='*50)
        
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"测试异常: {e}")
            results.append((test_name, False))
    
    # 显示测试结果
    print(f"\n\n{'='*50}")
    print("测试结果汇总")
    print('='*50)
    
    total_tests = len(results)
    passed_tests = sum(1 for _, success in results if success)
    
    for test_name, success in results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"{test_name}: {status}")
    
    print(f"\n总计: {passed_tests}/{total_tests} 通过")
    
    return passed_tests == total_tests

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)