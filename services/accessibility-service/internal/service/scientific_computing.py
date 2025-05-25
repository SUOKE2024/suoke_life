#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
科学计算库集成模块
提供统一的科学计算接口，支持数据分析、机器学习、信号处理等功能
"""

import logging
import warnings
from typing import Dict, List, Optional, Tuple, Any, Union
import numpy as np
from datetime import datetime, timezone

# 配置日志
logger = logging.getLogger(__name__)

class ScientificComputingManager:
    """科学计算管理器"""
    
    def __init__(self):
        """初始化科学计算管理器"""
        self._available_libraries = {}
        self._check_available_libraries()
        
    def _check_available_libraries(self) -> None:
        """检查可用的科学计算库"""
        libraries_to_check = {
            # 核心科学计算库
            'numpy': 'numpy',
            'scipy': 'scipy',
            'pandas': 'pandas',
            'matplotlib': 'matplotlib.pyplot',
            'seaborn': 'seaborn',
            'plotly': 'plotly.graph_objects',
            
            # 机器学习库
            'sklearn': 'sklearn',
            'xgboost': 'xgboost',
            'lightgbm': 'lightgbm',
            'catboost': 'catboost',
            'tensorflow': 'tensorflow',
            'torch': 'torch',
            
            # 计算机视觉库
            'cv2': 'cv2',
            'PIL': 'PIL',
            'skimage': 'skimage',
            'mediapipe': 'mediapipe',
            
            # 音频处理库
            'librosa': 'librosa',
            'sounddevice': 'sounddevice',
            'pydub': 'pydub',
            
            # 信号处理库
            'filterpy': 'filterpy',
            'pywavelets': 'pywt',
            
            # 地理信息库
            'geopy': 'geopy',
            'shapely': 'shapely',
            'folium': 'folium',
            'haversine': 'haversine',
            
            # 统计和数学库
            'statsmodels': 'statsmodels.api',
            'sympy': 'sympy',
            'networkx': 'networkx',
            
            # 性能优化库
            'numba': 'numba',
            'joblib': 'joblib',
            
            # 数据存储库
            'h5py': 'h5py'
        }
        
        for lib_name, import_path in libraries_to_check.items():
            try:
                __import__(import_path)
                self._available_libraries[lib_name] = True
                logger.info(f"✅ {lib_name} 库可用")
            except ImportError:
                self._available_libraries[lib_name] = False
                logger.warning(f"⚠️ {lib_name} 库不可用")
    
    def get_available_libraries(self) -> Dict[str, bool]:
        """获取可用库列表"""
        return self._available_libraries.copy()
    
    def is_library_available(self, library_name: str) -> bool:
        """检查特定库是否可用"""
        return self._available_libraries.get(library_name, False)


class DataAnalysisEngine:
    """数据分析引擎"""
    
    def __init__(self, computing_manager: ScientificComputingManager):
        """初始化数据分析引擎"""
        self.computing_manager = computing_manager
        
    def analyze_sensor_data(self, data: np.ndarray) -> Dict[str, Any]:
        """分析传感器数据"""
        try:
            # 基本统计分析
            stats = {
                'mean': float(np.mean(data)),
                'std': float(np.std(data)),
                'min': float(np.min(data)),
                'max': float(np.max(data)),
                'median': float(np.median(data)),
                'shape': data.shape,
                'dtype': str(data.dtype)
            }
            
            # 如果scipy可用，添加更多统计信息
            if self.computing_manager.is_library_available('scipy'):
                from scipy import stats as scipy_stats
                stats['skewness'] = float(scipy_stats.skew(data.flatten()))
                stats['kurtosis'] = float(scipy_stats.kurtosis(data.flatten()))
                
                # 正态性检验
                if len(data.flatten()) > 3:
                    shapiro_stat, shapiro_p = scipy_stats.shapiro(data.flatten()[:5000])  # 限制样本数量
                    stats['normality_test'] = {
                        'shapiro_stat': float(shapiro_stat),
                        'shapiro_p_value': float(shapiro_p),
                        'is_normal': shapiro_p > 0.05
                    }
            
            # 如果pandas可用，创建DataFrame进行分析
            if self.computing_manager.is_library_available('pandas'):
                import pandas as pd
                df = pd.DataFrame(data.flatten(), columns=['value'])
                stats['quantiles'] = {
                    '25%': float(df['value'].quantile(0.25)),
                    '50%': float(df['value'].quantile(0.50)),
                    '75%': float(df['value'].quantile(0.75))
                }
                
                # 缺失值分析
                stats['missing_values'] = {
                    'count': int(df['value'].isna().sum()),
                    'percentage': float(df['value'].isna().sum() / len(df) * 100)
                }
            
            return {
                'status': 'success',
                'statistics': stats,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"传感器数据分析失败: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    def detect_anomalies(self, data: np.ndarray, threshold: float = 3.0) -> Dict[str, Any]:
        """异常检测"""
        try:
            # Z-score异常检测
            z_scores = np.abs((data - np.mean(data)) / np.std(data))
            anomalies = z_scores > threshold
            
            result = {
                'total_points': len(data),
                'anomaly_count': int(np.sum(anomalies)),
                'anomaly_percentage': float(np.sum(anomalies) / len(data) * 100),
                'anomaly_indices': np.where(anomalies)[0].tolist(),
                'threshold': threshold
            }
            
            # 如果sklearn可用，使用更高级的异常检测
            if self.computing_manager.is_library_available('sklearn'):
                from sklearn.ensemble import IsolationForest
                from sklearn.svm import OneClassSVM
                from sklearn.covariance import EllipticEnvelope
                
                # 重塑数据用于sklearn
                data_reshaped = data.reshape(-1, 1)
                
                # 使用Isolation Forest
                iso_forest = IsolationForest(contamination=0.1, random_state=42)
                outliers_iso = iso_forest.fit_predict(data_reshaped)
                
                # 使用One-Class SVM
                one_class_svm = OneClassSVM(nu=0.1)
                outliers_svm = one_class_svm.fit_predict(data_reshaped)
                
                # 使用椭圆包络
                elliptic_env = EllipticEnvelope(contamination=0.1)
                outliers_elliptic = elliptic_env.fit_predict(data_reshaped)
                
                result['advanced_detection'] = {
                    'isolation_forest': {
                        'outlier_count': int(np.sum(outliers_iso == -1)),
                        'outlier_indices': np.where(outliers_iso == -1)[0].tolist()
                    },
                    'one_class_svm': {
                        'outlier_count': int(np.sum(outliers_svm == -1)),
                        'outlier_indices': np.where(outliers_svm == -1)[0].tolist()
                    },
                    'elliptic_envelope': {
                        'outlier_count': int(np.sum(outliers_elliptic == -1)),
                        'outlier_indices': np.where(outliers_elliptic == -1)[0].tolist()
                    }
                }
            
            return {
                'status': 'success',
                'results': result,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"异常检测失败: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }


class SignalProcessingEngine:
    """信号处理引擎"""
    
    def __init__(self, computing_manager: ScientificComputingManager):
        """初始化信号处理引擎"""
        self.computing_manager = computing_manager
    
    def filter_signal(self, signal: np.ndarray, filter_type: str = 'lowpass', 
                     cutoff: float = 0.1) -> Dict[str, Any]:
        """信号滤波"""
        try:
            if not self.computing_manager.is_library_available('scipy'):
                # 简单的移动平均滤波
                window_size = max(1, int(len(signal) * cutoff))
                filtered_signal = np.convolve(signal, np.ones(window_size)/window_size, mode='same')
                
                return {
                    'status': 'success',
                    'filtered_signal': filtered_signal.tolist(),
                    'filter_type': 'moving_average',
                    'window_size': window_size,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            
            # 使用scipy进行高级滤波
            from scipy import signal as scipy_signal
            
            # 设计滤波器
            if filter_type == 'lowpass':
                b, a = scipy_signal.butter(4, cutoff, btype='low')
            elif filter_type == 'highpass':
                b, a = scipy_signal.butter(4, cutoff, btype='high')
            elif filter_type == 'bandpass':
                b, a = scipy_signal.butter(4, [cutoff, cutoff*2], btype='band')
            elif filter_type == 'bandstop':
                b, a = scipy_signal.butter(4, [cutoff, cutoff*2], btype='bandstop')
            else:
                raise ValueError(f"不支持的滤波器类型: {filter_type}")
            
            # 应用滤波器
            filtered_signal = scipy_signal.filtfilt(b, a, signal)
            
            return {
                'status': 'success',
                'filtered_signal': filtered_signal.tolist(),
                'filter_type': filter_type,
                'cutoff_frequency': cutoff,
                'filter_order': 4,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"信号滤波失败: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    def analyze_frequency_spectrum(self, signal: np.ndarray, 
                                 sample_rate: float = 1.0) -> Dict[str, Any]:
        """频谱分析"""
        try:
            # 使用numpy进行基本FFT
            fft_result = np.fft.fft(signal)
            frequencies = np.fft.fftfreq(len(signal), 1/sample_rate)
            magnitude = np.abs(fft_result)
            phase = np.angle(fft_result)
            
            # 只取正频率部分
            positive_freq_idx = frequencies >= 0
            frequencies = frequencies[positive_freq_idx]
            magnitude = magnitude[positive_freq_idx]
            phase = phase[positive_freq_idx]
            
            result = {
                'frequencies': frequencies.tolist(),
                'magnitude': magnitude.tolist(),
                'phase': phase.tolist(),
                'sample_rate': sample_rate,
                'signal_length': len(signal)
            }
            
            # 如果scipy可用，添加更多频谱分析
            if self.computing_manager.is_library_available('scipy'):
                from scipy import signal as scipy_signal
                
                # 功率谱密度
                freqs_psd, psd = scipy_signal.welch(signal, sample_rate)
                result['power_spectral_density'] = {
                    'frequencies': freqs_psd.tolist(),
                    'psd': psd.tolist()
                }
                
                # 短时傅里叶变换
                freqs_stft, times_stft, stft = scipy_signal.stft(signal, sample_rate)
                result['short_time_fft'] = {
                    'frequencies': freqs_stft.tolist(),
                    'times': times_stft.tolist(),
                    'magnitude': np.abs(stft).tolist()
                }
            
            return {
                'status': 'success',
                'spectrum_analysis': result,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"频谱分析失败: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }


class MachineLearningEngine:
    """机器学习引擎"""
    
    def __init__(self, computing_manager: ScientificComputingManager):
        """初始化机器学习引擎"""
        self.computing_manager = computing_manager
        
    def train_classifier(self, X: np.ndarray, y: np.ndarray, 
                        model_type: str = 'random_forest') -> Dict[str, Any]:
        """训练分类器"""
        try:
            if not self.computing_manager.is_library_available('sklearn'):
                return {
                    'status': 'error',
                    'error': 'scikit-learn库不可用',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            
            from sklearn.model_selection import train_test_split, cross_val_score
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.svm import SVC
            from sklearn.linear_model import LogisticRegression
            from sklearn.metrics import classification_report, confusion_matrix
            
            # 分割数据
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # 选择模型
            if model_type == 'random_forest':
                model = RandomForestClassifier(n_estimators=100, random_state=42)
            elif model_type == 'svm':
                model = SVC(random_state=42)
            elif model_type == 'logistic_regression':
                model = LogisticRegression(random_state=42)
            else:
                raise ValueError(f"不支持的模型类型: {model_type}")
            
            # 训练模型
            model.fit(X_train, y_train)
            
            # 预测和评估
            y_pred = model.predict(X_test)
            accuracy = model.score(X_test, y_test)
            
            # 交叉验证
            cv_scores = cross_val_score(model, X, y, cv=5)
            
            # 分类报告
            class_report = classification_report(y_test, y_pred, output_dict=True)
            
            # 混淆矩阵
            conf_matrix = confusion_matrix(y_test, y_pred)
            
            return {
                'status': 'success',
                'model_type': model_type,
                'accuracy': float(accuracy),
                'cross_validation_scores': cv_scores.tolist(),
                'cv_mean': float(cv_scores.mean()),
                'cv_std': float(cv_scores.std()),
                'classification_report': class_report,
                'confusion_matrix': conf_matrix.tolist(),
                'feature_importance': getattr(model, 'feature_importances_', []).tolist(),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"分类器训练失败: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    def cluster_data(self, X: np.ndarray, n_clusters: int = 3) -> Dict[str, Any]:
        """数据聚类"""
        try:
            if not self.computing_manager.is_library_available('sklearn'):
                # 简单的K-means实现
                centroids = X[np.random.choice(X.shape[0], n_clusters, replace=False)]
                
                for _ in range(100):  # 最大迭代次数
                    # 分配点到最近的中心
                    distances = np.sqrt(((X - centroids[:, np.newaxis])**2).sum(axis=2))
                    labels = np.argmin(distances, axis=0)
                    
                    # 更新中心点
                    new_centroids = np.array([X[labels == i].mean(axis=0) for i in range(n_clusters)])
                    
                    # 检查收敛
                    if np.allclose(centroids, new_centroids):
                        break
                    centroids = new_centroids
                
                return {
                    'status': 'success',
                    'algorithm': 'simple_kmeans',
                    'n_clusters': n_clusters,
                    'labels': labels.tolist(),
                    'centroids': centroids.tolist(),
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            
            # 使用sklearn进行聚类
            from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
            from sklearn.metrics import silhouette_score, calinski_harabasz_score
            
            # K-means聚类
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            kmeans_labels = kmeans.fit_predict(X)
            
            # DBSCAN聚类
            dbscan = DBSCAN(eps=0.5, min_samples=5)
            dbscan_labels = dbscan.fit_predict(X)
            
            # 层次聚类
            hierarchical = AgglomerativeClustering(n_clusters=n_clusters)
            hierarchical_labels = hierarchical.fit_predict(X)
            
            # 评估指标
            kmeans_silhouette = silhouette_score(X, kmeans_labels)
            kmeans_calinski = calinski_harabasz_score(X, kmeans_labels)
            
            result = {
                'kmeans': {
                    'labels': kmeans_labels.tolist(),
                    'centroids': kmeans.cluster_centers_.tolist(),
                    'inertia': float(kmeans.inertia_),
                    'silhouette_score': float(kmeans_silhouette),
                    'calinski_harabasz_score': float(kmeans_calinski)
                },
                'dbscan': {
                    'labels': dbscan_labels.tolist(),
                    'n_clusters': len(set(dbscan_labels)) - (1 if -1 in dbscan_labels else 0),
                    'n_noise': list(dbscan_labels).count(-1)
                },
                'hierarchical': {
                    'labels': hierarchical_labels.tolist(),
                    'n_clusters': n_clusters
                }
            }
            
            return {
                'status': 'success',
                'clustering_results': result,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"数据聚类失败: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }


class VisualizationEngine:
    """可视化引擎"""
    
    def __init__(self, computing_manager: ScientificComputingManager):
        """初始化可视化引擎"""
        self.computing_manager = computing_manager
    
    def create_plot_data(self, data: np.ndarray, plot_type: str = 'line') -> Dict[str, Any]:
        """创建绘图数据"""
        try:
            if plot_type == 'line':
                x = np.arange(len(data))
                y = data
                
                plot_data = {
                    'x': x.tolist(),
                    'y': y.tolist(),
                    'type': 'line'
                }
            
            elif plot_type == 'histogram':
                if self.computing_manager.is_library_available('numpy'):
                    hist, bin_edges = np.histogram(data, bins=20)
                    plot_data = {
                        'bins': bin_edges.tolist(),
                        'counts': hist.tolist(),
                        'type': 'histogram'
                    }
                else:
                    # 简单的直方图
                    min_val, max_val = np.min(data), np.max(data)
                    bins = np.linspace(min_val, max_val, 21)
                    hist = np.zeros(20)
                    
                    for value in data:
                        bin_idx = min(19, int((value - min_val) / (max_val - min_val) * 20))
                        hist[bin_idx] += 1
                    
                    plot_data = {
                        'bins': bins.tolist(),
                        'counts': hist.tolist(),
                        'type': 'histogram'
                    }
            
            elif plot_type == 'scatter':
                if data.ndim >= 2:
                    plot_data = {
                        'x': data[:, 0].tolist(),
                        'y': data[:, 1].tolist(),
                        'type': 'scatter'
                    }
                else:
                    x = np.arange(len(data))
                    plot_data = {
                        'x': x.tolist(),
                        'y': data.tolist(),
                        'type': 'scatter'
                    }
            
            elif plot_type == 'boxplot':
                # 箱线图数据
                q1 = np.percentile(data, 25)
                q2 = np.percentile(data, 50)  # 中位数
                q3 = np.percentile(data, 75)
                iqr = q3 - q1
                lower_whisker = q1 - 1.5 * iqr
                upper_whisker = q3 + 1.5 * iqr
                
                outliers = data[(data < lower_whisker) | (data > upper_whisker)]
                
                plot_data = {
                    'q1': float(q1),
                    'q2': float(q2),
                    'q3': float(q3),
                    'lower_whisker': float(max(np.min(data), lower_whisker)),
                    'upper_whisker': float(min(np.max(data), upper_whisker)),
                    'outliers': outliers.tolist(),
                    'type': 'boxplot'
                }
            
            elif plot_type == 'heatmap' and data.ndim == 2:
                plot_data = {
                    'data': data.tolist(),
                    'shape': data.shape,
                    'type': 'heatmap'
                }
            
            else:
                raise ValueError(f"不支持的绘图类型: {plot_type}")
            
            return {
                'status': 'success',
                'plot_data': plot_data,
                'data_shape': data.shape,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"创建绘图数据失败: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }


class ScientificComputingService:
    """科学计算服务主类"""
    
    def __init__(self):
        """初始化科学计算服务"""
        self.computing_manager = ScientificComputingManager()
        self.data_analysis = DataAnalysisEngine(self.computing_manager)
        self.signal_processing = SignalProcessingEngine(self.computing_manager)
        self.machine_learning = MachineLearningEngine(self.computing_manager)
        self.visualization = VisualizationEngine(self.computing_manager)
        
        logger.info("科学计算服务初始化完成")
    
    def get_service_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        available_libs = self.computing_manager.get_available_libraries()
        
        return {
            'service_name': 'ScientificComputingService',
            'status': 'active',
            'available_libraries': available_libs,
            'library_count': sum(available_libs.values()),
            'total_libraries': len(available_libs),
            'coverage_percentage': sum(available_libs.values()) / len(available_libs) * 100,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    def process_data(self, data: List[float], operation: str, **kwargs) -> Dict[str, Any]:
        """处理数据的统一接口"""
        try:
            # 转换为numpy数组
            np_data = np.array(data)
            
            if operation == 'analyze':
                return self.data_analysis.analyze_sensor_data(np_data)
            elif operation == 'detect_anomalies':
                threshold = kwargs.get('threshold', 3.0)
                return self.data_analysis.detect_anomalies(np_data, threshold)
            elif operation == 'filter':
                filter_type = kwargs.get('filter_type', 'lowpass')
                cutoff = kwargs.get('cutoff', 0.1)
                return self.signal_processing.filter_signal(np_data, filter_type, cutoff)
            elif operation == 'spectrum':
                sample_rate = kwargs.get('sample_rate', 1.0)
                return self.signal_processing.analyze_frequency_spectrum(np_data, sample_rate)
            elif operation == 'cluster':
                n_clusters = kwargs.get('n_clusters', 3)
                return self.machine_learning.cluster_data(np_data.reshape(-1, 1), n_clusters)
            elif operation == 'plot':
                plot_type = kwargs.get('plot_type', 'line')
                return self.visualization.create_plot_data(np_data, plot_type)
            else:
                raise ValueError(f"不支持的操作: {operation}")
                
        except Exception as e:
            logger.error(f"数据处理失败: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'operation': operation,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }


# 全局服务实例
_scientific_computing_service = None

def get_scientific_computing_service() -> ScientificComputingService:
    """获取科学计算服务实例（单例模式）"""
    global _scientific_computing_service
    if _scientific_computing_service is None:
        _scientific_computing_service = ScientificComputingService()
    return _scientific_computing_service 