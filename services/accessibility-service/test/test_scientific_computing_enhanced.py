#!/usr/bin/env python3

"""
科学计算服务增强测试
测试所有科学计算功能，包括数据分析、信号处理、机器学习和可视化
"""

import os
import sys

import pytest

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from internal.service.scientific_computing import (
    DataAnalysisEngine,
    MachineLearningEngine,
    ScientificComputingManager,
    ScientificComputingService,
    SignalProcessingEngine,
    VisualizationEngine,
    get_scientific_computing_service,
)


class TestScientificComputingManager:
    """测试科学计算管理器"""

    def test_manager_initialization(self) -> None:
        """测试管理器初始化"""
        manager = ScientificComputingManager()
        assert isinstance(manager, ScientificComputingManager)

        # 检查库检测
        available_libs = manager.get_available_libraries()
        assert isinstance(available_libs, dict)
        assert len(available_libs) > 0

        # 检查numpy是否可用（应该总是可用）
        assert manager.is_library_available("numpy")

    def test_library_availability_check(self) -> None:
        """测试库可用性检查"""
        manager = ScientificComputingManager()

        # 测试已知存在的库
        assert manager.is_library_available("numpy")

        # 测试不存在的库
        assert not manager.is_library_available("nonexistent_library")


class TestDataAnalysisEngine:
    """测试数据分析引擎"""

    def setup_method(self) -> None:
        """设置测试环境"""
        self.manager = ScientificComputingManager()
        self.engine = DataAnalysisEngine(self.manager)

        # 创建测试数据
        np.random.seed(42)
        self.test_data = np.random.normal(0, 1, 1000)
        self.test_data_2d = np.random.normal(0, 1, (100, 5))

    def test_analyze_sensor_data(self) -> None:
        """测试传感器数据分析"""
        result = self.engine.analyze_sensor_data(self.test_data)

        assert result["status"] == "success"
        assert "statistics" in result

        stats = result["statistics"]
        assert "mean" in stats
        assert "std" in stats
        assert "min" in stats
        assert "max" in stats
        assert "median" in stats
        assert "shape" in stats
        assert "dtype" in stats

        # 检查统计值的合理性
        assert abs(stats["mean"]) < 0.1  # 应该接近0
        assert 0.9 < stats["std"] < 1.1  # 应该接近1

    def test_detect_anomalies(self) -> None:
        """测试异常检测"""
        # 创建包含异常值的数据
        data_with_outliers = np.concatenate(
            [
                np.random.normal(0, 1, 950),
                np.array([10, -10, 15, -15, 20]),  # 明显的异常值
            ]
        )

        result = self.engine.detect_anomalies(data_with_outliers, threshold=3.0)

        assert result["status"] == "success"
        assert "results" in result

        results = result["results"]
        assert "total_points" in results
        assert "anomaly_count" in results
        assert "anomaly_percentage" in results
        assert "anomaly_indices" in results

        # 应该检测到一些异常值
        assert results["anomaly_count"] > 0
        assert results["anomaly_percentage"] > 0


class TestSignalProcessingEngine:
    """测试信号处理引擎"""

    def setup_method(self) -> None:
        """设置测试环境"""
        self.manager = ScientificComputingManager()
        self.engine = SignalProcessingEngine(self.manager)

        # 创建测试信号
        t = np.linspace(0, 1, 1000)
        self.test_signal = np.sin(2 * np.pi * 10 * t) + 0.5 * np.sin(2 * np.pi * 20 * t)

    def test_filter_signal(self) -> None:
        """测试信号滤波"""
        result = self.engine.filter_signal(self.test_signal, "lowpass", 0.1)

        assert result["status"] == "success"
        assert "filtered_signal" in result
        assert len(result["filtered_signal"]) == len(self.test_signal)

    def test_analyze_frequency_spectrum(self) -> None:
        """测试频谱分析"""
        result = self.engine.analyze_frequency_spectrum(
            self.test_signal, sample_rate=1000
        )

        assert result["status"] == "success"
        assert "spectrum_analysis" in result

        spectrum = result["spectrum_analysis"]
        assert "frequencies" in spectrum
        assert "magnitude" in spectrum
        assert "phase" in spectrum
        assert "sample_rate" in spectrum


class TestMachineLearningEngine:
    """测试机器学习引擎"""

    def setup_method(self) -> None:
        """设置测试环境"""
        self.manager = ScientificComputingManager()
        self.engine = MachineLearningEngine(self.manager)

        # 创建测试数据
        np.random.seed(42)
        self.X = np.random.randn(200, 4)
        self.y = (self.X[:, 0] + self.X[:, 1] > 0).astype(int)  # 简单的分类标签

    def test_train_classifier(self) -> None:
        """测试分类器训练"""
        if not self.manager.is_library_available("sklearn"):
            pytest.skip("sklearn不可用")

        result = self.engine.train_classifier(self.X, self.y, "random_forest")

        assert result["status"] == "success"
        assert "accuracy" in result
        assert "cross_validation_scores" in result
        assert "classification_report" in result
        assert "confusion_matrix" in result

        # 准确率应该合理
        assert 0.5 <= result["accuracy"] <= 1.0

    def test_cluster_data(self) -> None:
        """测试数据聚类"""
        result = self.engine.cluster_data(self.X, n_clusters=3)

        assert result["status"] == "success"

        if self.manager.is_library_available("sklearn"):
            assert "clustering_results" in result
            clustering = result["clustering_results"]
            assert "kmeans" in clustering
            assert "dbscan" in clustering
            assert "hierarchical" in clustering
        else:
            assert "labels" in result
            assert "centroids" in result


class TestVisualizationEngine:
    """测试可视化引擎"""

    def setup_method(self) -> None:
        """设置测试环境"""
        self.manager = ScientificComputingManager()
        self.engine = VisualizationEngine(self.manager)

        # 创建测试数据
        np.random.seed(42)
        self.test_data_1d = np.random.normal(0, 1, 100)
        self.test_data_2d = np.random.normal(0, 1, (50, 2))

    def test_create_line_plot(self) -> None:
        """测试线图数据创建"""
        result = self.engine.create_plot_data(self.test_data_1d, "line")

        assert result["status"] == "success"
        assert "plot_data" in result

        plot_data = result["plot_data"]
        assert plot_data["type"] == "line"
        assert "x" in plot_data
        assert "y" in plot_data
        assert len(plot_data["x"]) == len(self.test_data_1d)

    def test_create_histogram(self) -> None:
        """测试直方图数据创建"""
        result = self.engine.create_plot_data(self.test_data_1d, "histogram")

        assert result["status"] == "success"
        assert "plot_data" in result

        plot_data = result["plot_data"]
        assert plot_data["type"] == "histogram"
        assert "bins" in plot_data
        assert "counts" in plot_data

    def test_create_scatter_plot(self) -> None:
        """测试散点图数据创建"""
        result = self.engine.create_plot_data(self.test_data_2d, "scatter")

        assert result["status"] == "success"
        assert "plot_data" in result

        plot_data = result["plot_data"]
        assert plot_data["type"] == "scatter"
        assert "x" in plot_data
        assert "y" in plot_data

    def test_create_boxplot(self) -> None:
        """测试箱线图数据创建"""
        result = self.engine.create_plot_data(self.test_data_1d, "boxplot")

        assert result["status"] == "success"
        assert "plot_data" in result

        plot_data = result["plot_data"]
        assert plot_data["type"] == "boxplot"
        assert "q1" in plot_data
        assert "q2" in plot_data
        assert "q3" in plot_data
        assert "lower_whisker" in plot_data
        assert "upper_whisker" in plot_data


class TestScientificComputingService:
    """测试科学计算服务主类"""

    def setup_method(self) -> None:
        """设置测试环境"""
        self.service = ScientificComputingService()

        # 创建测试数据
        np.random.seed(42)
        self.test_data = np.random.normal(0, 1, 100).tolist()

    def test_service_initialization(self) -> None:
        """测试服务初始化"""
        assert isinstance(self.service, ScientificComputingService)
        assert hasattr(self.service, "computing_manager")
        assert hasattr(self.service, "data_analysis")
        assert hasattr(self.service, "signal_processing")
        assert hasattr(self.service, "machine_learning")
        assert hasattr(self.service, "visualization")

    def test_get_service_status(self) -> None:
        """测试获取服务状态"""
        status = self.service.get_service_status()

        assert status["service_name"] == "ScientificComputingService"
        assert status["status"] == "active"
        assert "available_libraries" in status
        assert "library_count" in status
        assert "total_libraries" in status
        assert "coverage_percentage" in status
        assert "timestamp" in status

    def test_process_data_analyze(self) -> None:
        """测试数据分析处理"""
        result = self.service.process_data(self.test_data, "analyze")

        assert result["status"] == "success"
        assert "statistics" in result

    def test_process_data_detect_anomalies(self) -> None:
        """测试异常检测处理"""
        result = self.service.process_data(
            self.test_data, "detect_anomalies", threshold=2.0
        )

        assert result["status"] == "success"
        assert "results" in result

    def test_process_data_filter(self) -> None:
        """测试信号滤波处理"""
        result = self.service.process_data(
            self.test_data, "filter", filter_type="lowpass", cutoff=0.1
        )

        assert result["status"] == "success"
        assert "filtered_signal" in result

    def test_process_data_spectrum(self) -> None:
        """测试频谱分析处理"""
        result = self.service.process_data(self.test_data, "spectrum", sample_rate=100)

        assert result["status"] == "success"
        assert "spectrum_analysis" in result

    def test_process_data_cluster(self) -> None:
        """测试聚类处理"""
        result = self.service.process_data(self.test_data, "cluster", n_clusters=3)

        assert result["status"] == "success"

    def test_process_data_plot(self) -> None:
        """测试绘图数据处理"""
        result = self.service.process_data(self.test_data, "plot", plot_type="line")

        assert result["status"] == "success"
        assert "plot_data" in result

    def test_invalid_operation(self) -> None:
        """测试无效操作"""
        result = self.service.process_data(self.test_data, "invalid_operation")

        assert result["status"] == "error"
        assert "error" in result


class TestSingletonService:
    """测试单例服务"""

    def test_singleton_pattern(self) -> None:
        """测试单例模式"""
        service1 = get_scientific_computing_service()
        service2 = get_scientific_computing_service()

        assert service1 is service2
        assert isinstance(service1, ScientificComputingService)


class TestErrorHandling:
    """测试错误处理"""

    def setup_method(self) -> None:
        """设置测试环境"""
        self.service = ScientificComputingService()

    def test_empty_data_handling(self) -> None:
        """测试空数据处理"""
        result = self.service.process_data([], "analyze")

        # 应该优雅地处理空数据
        assert "status" in result

    def test_invalid_data_handling(self) -> None:
        """测试无效数据处理"""
        result = self.service.process_data(["invalid", "data"], "analyze")

        # 应该返回错误状态
        assert result["status"] == "error"


class TestAdvancedFeatures:
    """测试高级功能"""

    def setup_method(self) -> None:
        """设置测试环境"""
        self.service = ScientificComputingService()

        # 创建更复杂的测试数据
        np.random.seed(42)
        t = np.linspace(0, 10, 1000)
        self.complex_signal = (
            np.sin(2 * np.pi * 1 * t)
            + 0.5 * np.sin(2 * np.pi * 5 * t)
            + 0.2 * np.random.randn(1000)
        ).tolist()

    def test_complex_signal_processing(self) -> None:
        """测试复杂信号处理"""
        # 滤波
        filter_result = self.service.process_data(
            self.complex_signal, "filter", filter_type="lowpass", cutoff=0.1
        )
        assert filter_result["status"] == "success"

        # 频谱分析
        spectrum_result = self.service.process_data(
            self.complex_signal, "spectrum", sample_rate=100
        )
        assert spectrum_result["status"] == "success"

    def test_multi_dimensional_analysis(self) -> None:
        """测试多维数据分析"""
        # 创建多维数据
        multi_dim_data = np.random.randn(100, 3).flatten().tolist()

        result = self.service.process_data(multi_dim_data, "analyze")
        assert result["status"] == "success"


class TestPerformanceBenchmark:
    """性能基准测试"""

    def setup_method(self) -> None:
        """设置测试环境"""
        self.service = ScientificComputingService()

    def test_large_data_processing(self) -> None:
        """测试大数据处理性能"""
        import time

        # 创建大数据集
        large_data = np.random.randn(10000).tolist()

        start_time = time.time()
        result = self.service.process_data(large_data, "analyze")
        end_time = time.time()

        assert result["status"] == "success"
        processing_time = end_time - start_time

        # 处理时间应该在合理范围内（小于5秒）
        assert processing_time < 5.0
        print(f"大数据处理时间: {processing_time:.3f}秒")


class TestIntegrationWithAccessibilityService:
    """测试与无障碍服务的集成"""

    def setup_method(self) -> None:
        """设置测试环境"""
        self.service = ScientificComputingService()

    def test_sensor_data_integration(self) -> None:
        """测试传感器数据集成"""
        # 模拟传感器数据
        sensor_data = {
            "accelerometer": np.random.randn(100).tolist(),
            "gyroscope": np.random.randn(100).tolist(),
            "magnetometer": np.random.randn(100).tolist(),
        }

        for sensor_type, data in sensor_data.items():
            result = self.service.process_data(data, "analyze")
            assert result["status"] == "success"
            print(f"{sensor_type} 数据分析完成")

    def test_accessibility_feature_support(self) -> None:
        """测试无障碍功能支持"""
        # 模拟盲人辅助中的图像特征数据
        image_features = np.random.randn(50).tolist()

        # 异常检测（用于障碍物检测）
        anomaly_result = self.service.process_data(
            image_features, "detect_anomalies", threshold=2.0
        )
        assert anomaly_result["status"] == "success"

        # 聚类分析（用于场景分类）
        cluster_result = self.service.process_data(
            image_features, "cluster", n_clusters=5
        )
        assert cluster_result["status"] == "success"


class TestComprehensiveScientificLibraries:
    """全面的科学计算库测试"""

    def setup_method(self) -> None:
        """设置测试环境"""
        self.manager = ScientificComputingManager()

    def test_all_library_categories(self) -> None:
        """测试所有库类别"""
        available_libs = self.manager.get_available_libraries()

        # 核心科学计算库
        core_libs = ["numpy", "scipy", "pandas", "matplotlib"]
        for lib in core_libs:
            if lib in available_libs:
                print(f"✅ 核心库 {lib}: {'可用' if available_libs[lib] else '不可用'}")

        # 机器学习库
        ml_libs = ["sklearn", "xgboost", "lightgbm", "tensorflow", "torch"]
        for lib in ml_libs:
            if lib in available_libs:
                print(
                    f"🤖 机器学习库 {lib}: {'可用' if available_libs[lib] else '不可用'}"
                )

        # 计算机视觉库
        cv_libs = ["cv2", "PIL", "skimage", "mediapipe"]
        for lib in cv_libs:
            if lib in available_libs:
                print(
                    f"👁️ 计算机视觉库 {lib}: {'可用' if available_libs[lib] else '不可用'}"
                )

        # 音频处理库
        audio_libs = ["librosa", "sounddevice", "pydub"]
        for lib in audio_libs:
            if lib in available_libs:
                print(
                    f"🔊 音频处理库 {lib}: {'可用' if available_libs[lib] else '不可用'}"
                )

        # 统计库覆盖率
        total_libs = len(available_libs)
        available_count = sum(available_libs.values())
        coverage = available_count / total_libs * 100

        print(f"\n📊 库覆盖率: {available_count}/{total_libs} ({coverage:.1f}%)")

        # 至少应该有基础的numpy可用
        assert available_libs.get("numpy", False)


if __name__ == "__main__":
    # 运行所有测试
    pytest.main([__file__, "-v", "--tb=short"])
