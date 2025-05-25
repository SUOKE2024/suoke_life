#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
科学计算库支持测试
验证numpy、scipy、pandas等科学计算库的集成和使用
"""

import pytest
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestScientificComputingSupport:
    """科学计算库支持测试类"""
    
    def test_numpy_support(self):
        """测试NumPy支持"""
        try:
            import numpy as np
            
            # 测试基本数组操作
            arr = np.array([1, 2, 3, 4, 5])
            assert arr.shape == (5,)
            assert np.sum(arr) == 15
            assert np.mean(arr) == 3.0
            
            # 测试矩阵运算
            matrix = np.array([[1, 2], [3, 4]])
            result = np.dot(matrix, matrix)
            expected = np.array([[7, 10], [15, 22]])
            np.testing.assert_array_equal(result, expected)
            
            print("✅ NumPy支持测试成功")
            return True
            
        except ImportError as e:
            print(f"❌ NumPy导入失败: {e}")
            return False
        except Exception as e:
            print(f"❌ NumPy测试失败: {e}")
            return False
    
    def test_scipy_support(self):
        """测试SciPy支持"""
        try:
            import scipy
            from scipy import stats
            from scipy.spatial.distance import euclidean
            
            # 测试统计功能
            data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            mean = stats.describe(data).mean
            assert abs(mean - 5.5) < 0.01
            
            # 测试距离计算
            point1 = [0, 0]
            point2 = [3, 4]
            distance = euclidean(point1, point2)
            assert abs(distance - 5.0) < 0.01
            
            print("✅ SciPy支持测试成功")
            return True
            
        except ImportError as e:
            print(f"❌ SciPy导入失败: {e}")
            return False
        except Exception as e:
            print(f"❌ SciPy测试失败: {e}")
            return False
    
    def test_pandas_support(self):
        """测试Pandas支持"""
        try:
            import pandas as pd
            import numpy as np
            
            # 测试DataFrame创建和操作
            data = {
                'name': ['Alice', 'Bob', 'Charlie'],
                'age': [25, 30, 35],
                'score': [85.5, 92.0, 78.5]
            }
            df = pd.DataFrame(data)
            
            assert len(df) == 3
            assert df['age'].mean() == 30.0
            assert df['score'].max() == 92.0
            
            # 测试数据筛选
            filtered = df[df['age'] > 25]
            assert len(filtered) == 2
            
            print("✅ Pandas支持测试成功")
            return True
            
        except ImportError as e:
            print(f"❌ Pandas导入失败: {e}")
            return False
        except Exception as e:
            print(f"❌ Pandas测试失败: {e}")
            return False
    
    def test_opencv_support(self):
        """测试OpenCV支持"""
        try:
            import cv2
            import numpy as np
            
            # 创建测试图像
            img = np.zeros((100, 100, 3), dtype=np.uint8)
            img[25:75, 25:75] = [255, 255, 255]  # 白色正方形
            
            # 测试图像处理
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            assert gray.shape == (100, 100)
            
            # 测试边缘检测
            edges = cv2.Canny(gray, 50, 150)
            assert edges.shape == (100, 100)
            
            print("✅ OpenCV支持测试成功")
            return True
            
        except ImportError as e:
            print(f"❌ OpenCV导入失败: {e}")
            return False
        except Exception as e:
            print(f"❌ OpenCV测试失败: {e}")
            return False
    
    def test_scikit_learn_support(self):
        """测试Scikit-learn支持"""
        try:
            from sklearn.linear_model import LinearRegression
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import mean_squared_error
            import numpy as np
            
            # 创建测试数据
            X = np.array([[1], [2], [3], [4], [5]])
            y = np.array([2, 4, 6, 8, 10])  # y = 2x
            
            # 训练模型
            model = LinearRegression()
            model.fit(X, y)
            
            # 测试预测
            predictions = model.predict([[6], [7]])
            expected = [12, 14]
            
            for pred, exp in zip(predictions, expected):
                assert abs(pred - exp) < 0.1
            
            print("✅ Scikit-learn支持测试成功")
            return True
            
        except ImportError as e:
            print(f"❌ Scikit-learn导入失败: {e}")
            return False
        except Exception as e:
            print(f"❌ Scikit-learn测试失败: {e}")
            return False
    
    def test_matplotlib_support(self):
        """测试Matplotlib支持"""
        try:
            import matplotlib
            matplotlib.use('Agg')  # 使用非交互式后端
            import matplotlib.pyplot as plt
            import numpy as np
            
            # 创建测试图表
            x = np.linspace(0, 10, 100)
            y = np.sin(x)
            
            fig, ax = plt.subplots()
            ax.plot(x, y)
            ax.set_title('Test Plot')
            
            # 验证图表创建成功
            assert len(ax.lines) == 1
            assert ax.get_title() == 'Test Plot'
            
            plt.close(fig)  # 清理资源
            
            print("✅ Matplotlib支持测试成功")
            return True
            
        except ImportError as e:
            print(f"❌ Matplotlib导入失败: {e}")
            return False
        except Exception as e:
            print(f"❌ Matplotlib测试失败: {e}")
            return False
    
    def test_librosa_support(self):
        """测试Librosa音频处理支持"""
        try:
            import librosa
            import numpy as np
            
            # 创建测试音频信号
            sr = 22050  # 采样率
            duration = 1.0  # 1秒
            frequency = 440  # A4音符
            
            t = np.linspace(0, duration, int(sr * duration))
            audio_signal = np.sin(2 * np.pi * frequency * t)
            
            # 测试音频特征提取
            mfccs = librosa.feature.mfcc(y=audio_signal, sr=sr, n_mfcc=13)
            assert mfccs.shape[0] == 13  # 13个MFCC系数
            
            # 测试频谱分析
            stft = librosa.stft(audio_signal)
            assert stft.shape[0] == 1025  # 默认FFT大小的一半+1
            
            print("✅ Librosa支持测试成功")
            return True
            
        except ImportError as e:
            print(f"❌ Librosa导入失败: {e}")
            return False
        except Exception as e:
            print(f"❌ Librosa测试失败: {e}")
            return False
    
    def test_geopy_support(self):
        """测试Geopy地理计算支持"""
        try:
            from geopy.distance import geodesic
            from geopy.geocoders import Nominatim
            
            # 测试地理距离计算
            beijing = (39.9042, 116.4074)
            shanghai = (31.2304, 121.4737)
            
            distance = geodesic(beijing, shanghai).kilometers
            assert 1000 < distance < 1500  # 北京到上海大约1200公里
            
            print("✅ Geopy支持测试成功")
            return True
            
        except ImportError as e:
            print(f"❌ Geopy导入失败: {e}")
            return False
        except Exception as e:
            print(f"❌ Geopy测试失败: {e}")
            return False
    
    def test_integrated_scientific_workflow(self):
        """测试集成科学计算工作流"""
        try:
            import numpy as np
            import pandas as pd
            from scipy import stats
            from sklearn.preprocessing import StandardScaler
            
            # 模拟传感器数据
            np.random.seed(42)
            n_samples = 1000
            
            # 生成模拟数据
            temperature = np.random.normal(25, 5, n_samples)  # 温度数据
            humidity = np.random.normal(60, 10, n_samples)    # 湿度数据
            pressure = np.random.normal(1013, 20, n_samples)  # 气压数据
            
            # 创建DataFrame
            sensor_data = pd.DataFrame({
                'temperature': temperature,
                'humidity': humidity,
                'pressure': pressure
            })
            
            # 数据预处理
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(sensor_data)
            
            # 统计分析
            temp_stats = stats.describe(sensor_data['temperature'])
            assert 20 < temp_stats.mean < 30
            
            # 相关性分析
            correlation_matrix = sensor_data.corr()
            assert correlation_matrix.shape == (3, 3)
            
            # 异常检测（简单的3σ规则）
            z_scores = np.abs(stats.zscore(sensor_data))
            outliers = (z_scores > 3).any(axis=1)
            outlier_count = outliers.sum()
            
            print(f"✅ 集成科学计算工作流测试成功")
            print(f"   - 数据样本数: {len(sensor_data)}")
            print(f"   - 平均温度: {temp_stats.mean:.2f}°C")
            print(f"   - 检测到异常值: {outlier_count} 个")
            
            return True
            
        except Exception as e:
            print(f"❌ 集成科学计算工作流测试失败: {e}")
            return False
    
    def test_all_scientific_libraries(self):
        """运行所有科学计算库测试"""
        tests = [
            self.test_numpy_support,
            self.test_scipy_support,
            self.test_pandas_support,
            self.test_opencv_support,
            self.test_scikit_learn_support,
            self.test_matplotlib_support,
            self.test_librosa_support,
            self.test_geopy_support,
            self.test_integrated_scientific_workflow
        ]
        
        results = []
        for test in tests:
            try:
                result = test()
                results.append(result)
            except Exception as e:
                print(f"❌ 测试 {test.__name__} 失败: {e}")
                results.append(False)
        
        success_count = sum(results)
        total_count = len(results)
        
        print(f"\n📊 科学计算库支持测试总结:")
        print(f"   - 成功: {success_count}/{total_count}")
        print(f"   - 成功率: {success_count/total_count*100:.1f}%")
        
        return success_count, total_count


if __name__ == "__main__":
    test_suite = TestScientificComputingSupport()
    success, total = test_suite.test_all_scientific_libraries()
    
    if success == total:
        print("\n🎉 所有科学计算库支持测试通过！")
        exit(0)
    else:
        print(f"\n⚠️ {total - success} 个测试失败")
        exit(1) 