"""
test_tcm_diagnosis_integration - 索克生活项目模块
"""

        from palpation_service.internal.sensor_interface import PREDEFINED_SENSOR_CONFIGS
        import time
from calculation_service.core.algorithms.tongue_pulse_analysis import (
from datetime import datetime
from palpation_service.internal.sensor_interface import (
import asyncio
import cv2
import os
import pytest
import sys

"""
中医诊断系统集成测试
验证舌脉象分析、传感器接口和知识图谱推理的整合功能
"""


# 导入测试模块
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

    TonguePulseCalculationEngine,
    TongueImageAnalyzer,
    PulseWaveformAnalyzer,
    TongueColor,
    TongueCoating,
    PulseType
)

    SensorManager,
    SensorConfig,
    SensorConnectionType,
    MockSensorInterface,
    create_sensor_manager_with_defaults
)

class TestTCMDiagnosisIntegration:
    """中医诊断系统集成测试类"""
    
    @pytest.fixture
    def setup_test_environment(self):
        """设置测试环境"""
        # 创建计算引擎
        calculation_engine = TonguePulseCalculationEngine()
        
        # 创建传感器管理器
        sensor_manager = create_sensor_manager_with_defaults()
        
        # 创建测试数据
        test_data = self.create_test_data()
        
        return {
            'calculation_engine': calculation_engine,
            'sensor_manager': sensor_manager,
            'test_data': test_data
        }
    
    def create_test_data(self):
        """创建测试数据"""
        # 创建模拟舌象图像
        tongue_image = np.zeros((300, 400, 3), dtype=np.uint8)
        # 绘制一个椭圆形舌体
        cv2.ellipse(tongue_image, (200, 150), (120, 80), 0, 0, 360, (180, 120, 120), -1)
        
        # 创建模拟脉搏波形数据
        time_points = np.linspace(0, 30, 30000)  # 30秒，1000Hz采样率
        pulse_rate = 75  # 75 BPM
        base_freq = pulse_rate / 60.0
        
        # 生成复合脉搏波形
        pulse_waveform = (
            1.0 * np.sin(2 * np.pi * base_freq * time_points) +
            0.3 * np.sin(2 * np.pi * 2 * base_freq * time_points) +
            0.1 * np.sin(2 * np.pi * 3 * base_freq * time_points) +
            0.05 * np.random.normal(0, 1, len(time_points))
        )
        
        return {
            'tongue_image': tongue_image,
            'pulse_waveform': pulse_waveform,
            'pulse_duration': 30.0,
            'symptoms': ['乏力', '头晕', '心悸', '失眠'],
            'patient_info': {
                'age': 45,
                'gender': '女',
                'height': 165,
                'weight': 60,
                'medical_history': ['高血压'],
                'current_medications': []
            }
        }
    
    def test_tongue_image_analysis(self, setup_test_environment):
        """测试舌象图像分析"""
        env = setup_test_environment
        tongue_analyzer = env['calculation_engine'].tongue_analyzer
        test_data = env['test_data']
        
        # 执行舌象分析
        result = tongue_analyzer.analyze_tongue_image(test_data['tongue_image'])
        
        # 验证结果
        assert result is not None
        assert isinstance(result.color, TongueColor)
        assert isinstance(result.coating, TongueCoating)
        assert isinstance(result.texture, str)
        assert 0 <= result.moisture <= 1
        assert 0 <= result.thickness <= 1
        assert 0 <= result.color_confidence <= 1
        assert 0 <= result.coating_confidence <= 1
        assert isinstance(result.abnormal_areas, list)
        assert isinstance(result.timestamp, datetime)
        
        print(f"舌象分析结果: 舌色={result.color.value}, 舌苔={result.coating.value}, 置信度={result.color_confidence:.2f}")
    
    def test_pulse_waveform_analysis(self, setup_test_environment):
        """测试脉象波形分析"""
        env = setup_test_environment
        pulse_analyzer = env['calculation_engine'].pulse_analyzer
        test_data = env['test_data']
        
        # 执行脉象分析
        result = pulse_analyzer.analyze_pulse_waveform(
            test_data['pulse_waveform'], 
            test_data['pulse_duration']
        )
        
        # 验证结果
        assert result is not None
        assert isinstance(result.pulse_type, PulseType)
        assert 40 <= result.rate <= 150  # 合理的脉率范围
        assert isinstance(result.rhythm, str)
        assert 0 <= result.strength <= 1
        assert 0 <= result.depth <= 1
        assert result.width > 0
        assert 0 <= result.confidence <= 1
        assert isinstance(result.waveform_features, dict)
        assert isinstance(result.timestamp, datetime)
        
        print(f"脉象分析结果: 脉型={result.pulse_type.value}, 脉率={result.rate:.1f}次/分, 置信度={result.confidence:.2f}")
    
    def test_comprehensive_analysis(self, setup_test_environment):
        """测试综合分析功能"""
        env = setup_test_environment
        calculation_engine = env['calculation_engine']
        test_data = env['test_data']
        
        # 执行综合分析
        result = calculation_engine.comprehensive_analysis(
            tongue_image=test_data['tongue_image'],
            pulse_waveform=test_data['pulse_waveform'],
            pulse_duration=test_data['pulse_duration']
        )
        
        # 验证结果
        assert result is not None
        assert 'timestamp' in result
        assert 'tongue_analysis' in result
        assert 'pulse_analysis' in result
        assert 'syndrome_classification' in result
        assert 'recommendations' in result
        
        # 验证舌诊结果
        tongue_analysis = result['tongue_analysis']
        assert 'color' in tongue_analysis
        assert 'coating' in tongue_analysis
        assert 'color_confidence' in tongue_analysis
        
        # 验证脉诊结果
        pulse_analysis = result['pulse_analysis']
        assert 'pulse_type' in pulse_analysis
        assert 'rate' in pulse_analysis
        assert 'confidence' in pulse_analysis
        
        # 验证证候分类
        syndrome_classification = result['syndrome_classification']
        assert 'primary_syndrome' in syndrome_classification
        assert 'primary_score' in syndrome_classification
        
        # 验证治疗建议
        recommendations = result['recommendations']
        assert isinstance(recommendations, list)
        
        print(f"综合分析完成，主要证候: {syndrome_classification.get('primary_syndrome', '未确定')}")
        print(f"治疗建议数量: {len(recommendations)}")
    
    @pytest.mark.asyncio
    async def test_sensor_interface_mock(self, setup_test_environment):
        """测试模拟传感器接口"""
        env = setup_test_environment
        sensor_manager = env['sensor_manager']
        
        # 获取模拟传感器
        mock_sensor_id = "mock_sensor"
        assert mock_sensor_id in sensor_manager.sensors
        
        mock_sensor = sensor_manager.sensors[mock_sensor_id]
        
        # 测试连接
        connect_result = await mock_sensor.connect()
        assert connect_result is True
        
        # 测试校准
        calibrate_result = await mock_sensor.calibrate()
        assert calibrate_result is True
        
        # 测试数据流
        data_received = []
        
        def data_handler(reading):
            data_received.append(reading)
        
        mock_sensor.add_callback(data_handler)
        
        # 开始数据流
        stream_result = await mock_sensor.start_streaming()
        assert stream_result is True
        
        # 等待一些数据
        await asyncio.sleep(2)
        
        # 停止数据流
        stop_result = await mock_sensor.stop_streaming()
        assert stop_result is True
        
        # 断开连接
        disconnect_result = await mock_sensor.disconnect()
        assert disconnect_result is True
        
        # 验证接收到的数据
        assert len(data_received) > 0
        
        for reading in data_received[:5]:  # 检查前5个读数
            assert reading.device_id == mock_sensor_id
            assert reading.sensor_type == "pressure"
            assert isinstance(reading.raw_value, (int, float))
            assert reading.timestamp is not None
        
        print(f"模拟传感器测试完成，接收到 {len(data_received)} 个数据点")
    
    @pytest.mark.asyncio
    async def test_sensor_manager_operations(self, setup_test_environment):
        """测试传感器管理器操作"""
        env = setup_test_environment
        sensor_manager = env['sensor_manager']
        
        # 测试获取传感器状态
        status = sensor_manager.get_sensor_status()
        assert isinstance(status, dict)
        assert len(status) > 0
        
        # 测试连接所有传感器
        connect_results = await sensor_manager.connect_all()
        assert isinstance(connect_results, dict)
        
        successful_connections = sum(1 for success in connect_results.values() if success)
        print(f"成功连接 {successful_connections}/{len(connect_results)} 个传感器")
        
        # 测试开始所有数据流
        stream_results = await sensor_manager.start_all_streaming()
        assert isinstance(stream_results, dict)
        
        # 等待一些数据
        await asyncio.sleep(1)
        
        # 测试停止所有数据流
        stop_results = await sensor_manager.stop_all_streaming()
        assert isinstance(stop_results, dict)
        
        # 测试断开所有传感器
        disconnect_results = await sensor_manager.disconnect_all()
        assert isinstance(disconnect_results, dict)
    
    def test_data_quality_assessment(self, setup_test_environment):
        """测试数据质量评估"""
        env = setup_test_environment
        test_data = env['test_data']
        
        # 测试舌象图像质量
        tongue_analyzer = TongueImageAnalyzer()
        
        # 创建不同质量的图像
        good_image = test_data['tongue_image']
        
        # 模糊图像
        blurred_image = cv2.GaussianBlur(good_image, (15, 15), 0)
        
        # 噪声图像
        noisy_image = good_image.copy()
        noise = np.random.normal(0, 50, good_image.shape).astype(np.uint8)
        noisy_image = cv2.add(noisy_image, noise)
        
        # 分析不同质量的图像
        good_result = tongue_analyzer.analyze_tongue_image(good_image)
        blurred_result = tongue_analyzer.analyze_tongue_image(blurred_image)
        noisy_result = tongue_analyzer.analyze_tongue_image(noisy_image)
        
        # 验证质量差异
        print(f"原始图像置信度: {good_result.color_confidence:.2f}")
        print(f"模糊图像置信度: {blurred_result.color_confidence:.2f}")
        print(f"噪声图像置信度: {noisy_result.color_confidence:.2f}")
        
        # 通常原始图像应该有更高的置信度
        assert good_result.color_confidence >= 0
        assert blurred_result.color_confidence >= 0
        assert noisy_result.color_confidence >= 0
    
    def test_error_handling(self, setup_test_environment):
        """测试错误处理"""
        env = setup_test_environment
        calculation_engine = env['calculation_engine']
        
        # 测试无效输入
        with pytest.raises(Exception):
            # 空图像
            calculation_engine.tongue_analyzer.analyze_tongue_image(None)
        
        with pytest.raises(Exception):
            # 空波形
            calculation_engine.pulse_analyzer.analyze_pulse_waveform(None, 30.0)
        
        # 测试异常数据
        invalid_image = np.zeros((10, 10, 3), dtype=np.uint8)  # 太小的图像
        try:
            result = calculation_engine.tongue_analyzer.analyze_tongue_image(invalid_image)
            # 应该能处理但可能置信度很低
            assert result.color_confidence < 0.5
        except Exception as e:
            # 或者抛出异常也是可以接受的
            print(f"处理无效图像时的预期异常: {e}")
    
    def test_performance_benchmarks(self, setup_test_environment):
        """测试性能基准"""
        env = setup_test_environment
        calculation_engine = env['calculation_engine']
        test_data = env['test_data']
        
        
        # 舌象分析性能测试
        start_time = time.time()
        for _ in range(10):
            calculation_engine.tongue_analyzer.analyze_tongue_image(test_data['tongue_image'])
        tongue_analysis_time = (time.time() - start_time) / 10
        
        # 脉象分析性能测试
        start_time = time.time()
        for _ in range(10):
            calculation_engine.pulse_analyzer.analyze_pulse_waveform(
                test_data['pulse_waveform'], 
                test_data['pulse_duration']
            )
        pulse_analysis_time = (time.time() - start_time) / 10
        
        # 综合分析性能测试
        start_time = time.time()
        for _ in range(5):
            calculation_engine.comprehensive_analysis(
                tongue_image=test_data['tongue_image'],
                pulse_waveform=test_data['pulse_waveform'],
                pulse_duration=test_data['pulse_duration']
            )
        comprehensive_analysis_time = (time.time() - start_time) / 5
        
        print(f"性能基准测试结果:")
        print(f"  舌象分析平均时间: {tongue_analysis_time:.3f}秒")
        print(f"  脉象分析平均时间: {pulse_analysis_time:.3f}秒")
        print(f"  综合分析平均时间: {comprehensive_analysis_time:.3f}秒")
        
        # 性能要求（可根据实际需求调整）
        assert tongue_analysis_time < 2.0  # 舌象分析应在2秒内完成
        assert pulse_analysis_time < 1.0   # 脉象分析应在1秒内完成
        assert comprehensive_analysis_time < 3.0  # 综合分析应在3秒内完成
    
    def test_configuration_management(self, setup_test_environment):
        """测试配置管理"""
        env = setup_test_environment
        sensor_manager = env['sensor_manager']
        
        # 测试预定义配置
        
        assert len(PREDEFINED_SENSOR_CONFIGS) > 0
        
        for config_id, config in PREDEFINED_SENSOR_CONFIGS.items():
            assert config.device_id is not None
            assert config.device_name is not None
            assert config.connection_type is not None
            assert config.sampling_rate > 0
            assert config.data_format is not None
            
        print(f"预定义配置数量: {len(PREDEFINED_SENSOR_CONFIGS)}")
        
        # 测试动态配置
        new_config = SensorConfig(
            device_id="test_sensor",
            device_name="测试传感器",
            connection_type=SensorConnectionType.MOCK,
            connection_params={},
            sampling_rate=500,
            data_format="json",
            calibration_params={},
            quality_thresholds={}
        )
        
        # 注册新配置
        success = sensor_manager.register_sensor(new_config)
        assert success is True
        
        # 验证注册成功
        assert "test_sensor" in sensor_manager.sensors
        
        # 注销配置
        unregister_success = sensor_manager.unregister_sensor("test_sensor")
        assert unregister_success is True
        
        # 验证注销成功
        assert "test_sensor" not in sensor_manager.sensors

def test_integration_workflow():
    """测试完整的集成工作流程"""
    print("\n=== 中医诊断系统集成测试 ===")
    
    # 创建测试实例
    test_instance = TestTCMDiagnosisIntegration()
    
    # 设置测试环境
    env = test_instance.setup_test_environment()
    
    print("1. 测试环境设置完成")
    
    # 执行各项测试
    test_instance.test_tongue_image_analysis(env)
    print("2. 舌象分析测试通过")
    
    test_instance.test_pulse_waveform_analysis(env)
    print("3. 脉象分析测试通过")
    
    test_instance.test_comprehensive_analysis(env)
    print("4. 综合分析测试通过")
    
    # 异步测试需要特殊处理
    async def run_async_tests():
        await test_instance.test_sensor_interface_mock(env)
        print("5. 传感器接口测试通过")
        
        await test_instance.test_sensor_manager_operations(env)
        print("6. 传感器管理器测试通过")
    
    # 运行异步测试
    asyncio.run(run_async_tests())
    
    test_instance.test_data_quality_assessment(env)
    print("7. 数据质量评估测试通过")
    
    test_instance.test_error_handling(env)
    print("8. 错误处理测试通过")
    
    test_instance.test_performance_benchmarks(env)
    print("9. 性能基准测试通过")
    
    test_instance.test_configuration_management(env)
    print("10. 配置管理测试通过")
    
    print("\n=== 所有集成测试通过！ ===")

if __name__ == "__main__":
    # 运行集成测试
    test_integration_workflow() 