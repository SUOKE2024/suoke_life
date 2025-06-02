#!/usr/bin/env python3
"""
索克生活 - 关键算法C扩展模块
提供高性能C实现的核心算法接口
"""

import ctypes
import numpy as np
import os
import platform
from typing import Optional, Tuple, List, Dict, Any
from pathlib import Path
import logging
from dataclasses import dataclass
from enum import Enum
import subprocess
import tempfile

logger = logging.getLogger(__name__)


class AlgorithmType(Enum):
    """算法类型"""
    TCM_SYNDROME = "tcm_syndrome"           # 中医证候分析
    HEALTH_ANALYSIS = "health_analysis"     # 健康数据分析
    NUTRITION_OPT = "nutrition_opt"         # 营养优化
    BIOMETRIC_PROC = "biometric_proc"       # 生物标志物处理
    PATTERN_MATCH = "pattern_match"         # 模式匹配


@dataclass
class CExtensionConfig:
    """C扩展配置"""
    library_path: Optional[str] = None
    compile_flags: List[str] = None
    optimization_level: str = "O3"
    use_openmp: bool = True
    use_simd: bool = True
    debug_mode: bool = False


class CAlgorithmExtension:
    """C算法扩展管理器"""
    
    def __init__(self, config: Optional[CExtensionConfig] = None):
        self.config = config or CExtensionConfig()
        self.libraries = {}
        self.is_compiled = False
        self.temp_dir = None
        
        # 检测系统架构
        self.system = platform.system()
        self.architecture = platform.machine()
        
        # 初始化C扩展
        self._initialize_extensions()
    
    def _initialize_extensions(self):
        """初始化C扩展"""
        try:
            # 创建临时目录
            self.temp_dir = tempfile.mkdtemp(prefix="suoke_c_ext_")
            
            # 生成C源代码
            self._generate_c_sources()
            
            # 编译C扩展
            self._compile_extensions()
            
            # 加载动态库
            self._load_libraries()
            
            self.is_compiled = True
            logger.info("C扩展初始化成功")
            
        except Exception as e:
            logger.warning(f"C扩展初始化失败，将使用Python实现: {e}")
            self.is_compiled = False
    
    def _generate_c_sources(self):
        """生成C源代码"""
        # 中医证候分析C代码
        tcm_syndrome_c = '''
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>

#ifdef _OPENMP
#include <omp.h>
#endif

// 中医证候分析核心算法
void tcm_syndrome_analysis(
    const float* symptoms,      // 症状数据
    const float* weights,       // 权重
    const float* patterns,      // 证候模式
    float* scores,              // 输出评分
    int n_symptoms,             // 症状数量
    int n_patterns              // 证候模式数量
) {
    #pragma omp parallel for if(n_patterns > 4)
    for (int i = 0; i < n_patterns; i++) {
        float score = 0.0f;
        
        // 计算加权症状向量
        for (int j = 0; j < n_symptoms; j++) {
            float weighted_symptom = symptoms[j] * weights[j];
            score += weighted_symptom * patterns[i * n_symptoms + j];
        }
        
        scores[i] = score;
    }
    
    // 归一化评分
    float total_score = 0.0f;
    for (int i = 0; i < n_patterns; i++) {
        total_score += scores[i];
    }
    
    if (total_score > 0.0f) {
        for (int i = 0; i < n_patterns; i++) {
            scores[i] /= total_score;
        }
    }
}

// 健康数据标准化
void health_data_normalize(
    const float* input,         // 输入数据
    float* output,              // 输出数据
    int n_samples,              // 样本数量
    int n_features              // 特征数量
) {
    #pragma omp parallel for if(n_features > 10)
    for (int j = 0; j < n_features; j++) {
        // 计算均值
        float mean = 0.0f;
        for (int i = 0; i < n_samples; i++) {
            mean += input[i * n_features + j];
        }
        mean /= n_samples;
        
        // 计算标准差
        float variance = 0.0f;
        for (int i = 0; i < n_samples; i++) {
            float diff = input[i * n_features + j] - mean;
            variance += diff * diff;
        }
        float std_dev = sqrtf(variance / n_samples);
        
        // 标准化
        if (std_dev > 1e-8f) {
            for (int i = 0; i < n_samples; i++) {
                output[i * n_features + j] = 
                    (input[i * n_features + j] - mean) / std_dev;
            }
        } else {
            for (int i = 0; i < n_samples; i++) {
                output[i * n_features + j] = 0.0f;
            }
        }
    }
}

// 营养优化算法
void nutrition_optimization(
    const float* user_profile,  // 用户营养需求
    const float* food_database, // 食物营养数据库
    float* similarity_scores,   // 相似度评分
    int n_foods,                // 食物数量
    int n_nutrients             // 营养成分数量
) {
    #pragma omp parallel for if(n_foods > 100)
    for (int i = 0; i < n_foods; i++) {
        float dot_product = 0.0f;
        float user_norm = 0.0f;
        float food_norm = 0.0f;
        
        // 计算余弦相似度
        for (int j = 0; j < n_nutrients; j++) {
            float user_val = user_profile[j];
            float food_val = food_database[i * n_nutrients + j];
            
            dot_product += user_val * food_val;
            user_norm += user_val * user_val;
            food_norm += food_val * food_val;
        }
        
        user_norm = sqrtf(user_norm);
        food_norm = sqrtf(food_norm);
        
        if (user_norm > 1e-8f && food_norm > 1e-8f) {
            similarity_scores[i] = dot_product / (user_norm * food_norm);
        } else {
            similarity_scores[i] = 0.0f;
        }
    }
}

// 生物标志物处理
void biomarker_processing(
    const float* biomarkers,    // 生物标志物数据
    const float* reference,     // 参考值
    float* risk_scores,         // 风险评分
    int n_samples,              // 样本数量
    int n_markers               // 标志物数量
) {
    #pragma omp parallel for if(n_samples > 50)
    for (int i = 0; i < n_samples; i++) {
        float total_risk = 0.0f;
        
        for (int j = 0; j < n_markers; j++) {
            float marker_val = biomarkers[i * n_markers + j];
            float ref_val = reference[j];
            
            // 计算偏差风险
            float deviation = fabsf(marker_val - ref_val) / ref_val;
            float risk = 1.0f / (1.0f + expf(-5.0f * (deviation - 0.2f)));
            
            total_risk += risk;
        }
        
        risk_scores[i] = total_risk / n_markers;
    }
}

// 模式匹配算法
int pattern_matching(
    const float* data,          // 输入数据
    const float* patterns,      // 模式库
    int* matches,               // 匹配结果
    int data_length,            // 数据长度
    int n_patterns,             // 模式数量
    int pattern_length,         // 模式长度
    float threshold             // 匹配阈值
) {
    int match_count = 0;
    
    #pragma omp parallel for reduction(+:match_count)
    for (int i = 0; i <= data_length - pattern_length; i++) {
        for (int p = 0; p < n_patterns; p++) {
            float correlation = 0.0f;
            float data_norm = 0.0f;
            float pattern_norm = 0.0f;
            
            // 计算相关系数
            for (int j = 0; j < pattern_length; j++) {
                float data_val = data[i + j];
                float pattern_val = patterns[p * pattern_length + j];
                
                correlation += data_val * pattern_val;
                data_norm += data_val * data_val;
                pattern_norm += pattern_val * pattern_val;
            }
            
            data_norm = sqrtf(data_norm);
            pattern_norm = sqrtf(pattern_norm);
            
            if (data_norm > 1e-8f && pattern_norm > 1e-8f) {
                float similarity = correlation / (data_norm * pattern_norm);
                
                if (similarity >= threshold) {
                    matches[match_count * 3] = i;        // 位置
                    matches[match_count * 3 + 1] = p;    // 模式ID
                    matches[match_count * 3 + 2] = (int)(similarity * 1000); // 相似度*1000
                    match_count++;
                }
            }
        }
    }
    
    return match_count;
}
'''
        
        # 写入C源文件
        c_source_path = os.path.join(self.temp_dir, "suoke_algorithms.c")
        with open(c_source_path, 'w') as f:
            f.write(tcm_syndrome_c)
        
        # 生成头文件
        header_content = '''
#ifndef SUOKE_ALGORITHMS_H
#define SUOKE_ALGORITHMS_H

#ifdef __cplusplus
extern "C" {
#endif

void tcm_syndrome_analysis(
    const float* symptoms, const float* weights, const float* patterns,
    float* scores, int n_symptoms, int n_patterns
);

void health_data_normalize(
    const float* input, float* output, int n_samples, int n_features
);

void nutrition_optimization(
    const float* user_profile, const float* food_database,
    float* similarity_scores, int n_foods, int n_nutrients
);

void biomarker_processing(
    const float* biomarkers, const float* reference,
    float* risk_scores, int n_samples, int n_markers
);

int pattern_matching(
    const float* data, const float* patterns, int* matches,
    int data_length, int n_patterns, int pattern_length, float threshold
);

#ifdef __cplusplus
}
#endif

#endif // SUOKE_ALGORITHMS_H
'''
        
        header_path = os.path.join(self.temp_dir, "suoke_algorithms.h")
        with open(header_path, 'w') as f:
            f.write(header_content)
    
    def _compile_extensions(self):
        """编译C扩展"""
        if not self.temp_dir:
            raise RuntimeError("临时目录未创建")
        
        c_source = os.path.join(self.temp_dir, "suoke_algorithms.c")
        
        # 确定输出文件名
        if self.system == "Windows":
            lib_name = "suoke_algorithms.dll"
        elif self.system == "Darwin":
            lib_name = "suoke_algorithms.dylib"
        else:
            lib_name = "suoke_algorithms.so"
        
        self.library_path = os.path.join(self.temp_dir, lib_name)
        
        # 构建编译命令
        compile_cmd = ["gcc", "-shared", "-fPIC"]
        
        # 优化选项
        compile_cmd.extend([f"-{self.config.optimization_level}"])
        
        if self.config.use_simd:
            compile_cmd.extend(["-march=native", "-mtune=native"])
        
        if self.config.use_openmp:
            compile_cmd.extend(["-fopenmp"])
        
        if self.config.debug_mode:
            compile_cmd.extend(["-g", "-DDEBUG"])
        else:
            compile_cmd.extend(["-DNDEBUG"])
        
        # 添加源文件和输出
        compile_cmd.extend([c_source, "-o", self.library_path])
        
        # 链接数学库
        compile_cmd.extend(["-lm"])
        
        if self.config.use_openmp:
            compile_cmd.extend(["-lgomp"])
        
        # 执行编译
        try:
            result = subprocess.run(
                compile_cmd, 
                capture_output=True, 
                text=True, 
                cwd=self.temp_dir
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"编译失败: {result.stderr}")
            
            logger.info(f"C扩展编译成功: {self.library_path}")
            
        except FileNotFoundError:
            raise RuntimeError("未找到GCC编译器，请安装GCC")
    
    def _load_libraries(self):
        """加载动态库"""
        if not os.path.exists(self.library_path):
            raise RuntimeError(f"动态库不存在: {self.library_path}")
        
        try:
            # 加载动态库
            lib = ctypes.CDLL(self.library_path)
            
            # 定义函数签名
            # tcm_syndrome_analysis
            lib.tcm_syndrome_analysis.argtypes = [
                ctypes.POINTER(ctypes.c_float),  # symptoms
                ctypes.POINTER(ctypes.c_float),  # weights
                ctypes.POINTER(ctypes.c_float),  # patterns
                ctypes.POINTER(ctypes.c_float),  # scores
                ctypes.c_int,                    # n_symptoms
                ctypes.c_int                     # n_patterns
            ]
            lib.tcm_syndrome_analysis.restype = None
            
            # health_data_normalize
            lib.health_data_normalize.argtypes = [
                ctypes.POINTER(ctypes.c_float),  # input
                ctypes.POINTER(ctypes.c_float),  # output
                ctypes.c_int,                    # n_samples
                ctypes.c_int                     # n_features
            ]
            lib.health_data_normalize.restype = None
            
            # nutrition_optimization
            lib.nutrition_optimization.argtypes = [
                ctypes.POINTER(ctypes.c_float),  # user_profile
                ctypes.POINTER(ctypes.c_float),  # food_database
                ctypes.POINTER(ctypes.c_float),  # similarity_scores
                ctypes.c_int,                    # n_foods
                ctypes.c_int                     # n_nutrients
            ]
            lib.nutrition_optimization.restype = None
            
            # biomarker_processing
            lib.biomarker_processing.argtypes = [
                ctypes.POINTER(ctypes.c_float),  # biomarkers
                ctypes.POINTER(ctypes.c_float),  # reference
                ctypes.POINTER(ctypes.c_float),  # risk_scores
                ctypes.c_int,                    # n_samples
                ctypes.c_int                     # n_markers
            ]
            lib.biomarker_processing.restype = None
            
            # pattern_matching
            lib.pattern_matching.argtypes = [
                ctypes.POINTER(ctypes.c_float),  # data
                ctypes.POINTER(ctypes.c_float),  # patterns
                ctypes.POINTER(ctypes.c_int),    # matches
                ctypes.c_int,                    # data_length
                ctypes.c_int,                    # n_patterns
                ctypes.c_int,                    # pattern_length
                ctypes.c_float                   # threshold
            ]
            lib.pattern_matching.restype = ctypes.c_int
            
            self.libraries['main'] = lib
            logger.info("动态库加载成功")
            
        except Exception as e:
            raise RuntimeError(f"动态库加载失败: {e}")
    
    def tcm_syndrome_analysis(self, symptoms: np.ndarray, weights: np.ndarray, 
                             patterns: np.ndarray) -> np.ndarray:
        """中医证候分析（C扩展版本）"""
        if not self.is_compiled:
            return self._tcm_syndrome_analysis_python(symptoms, weights, patterns)
        
        # 确保数据类型
        symptoms = symptoms.astype(np.float32)
        weights = weights.astype(np.float32)
        patterns = patterns.astype(np.float32)
        
        n_symptoms = len(symptoms)
        n_patterns = patterns.shape[0]
        
        # 创建输出数组
        scores = np.zeros(n_patterns, dtype=np.float32)
        
        # 调用C函数
        lib = self.libraries['main']
        lib.tcm_syndrome_analysis(
            symptoms.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
            weights.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
            patterns.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
            scores.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
            n_symptoms,
            n_patterns
        )
        
        return scores
    
    def health_data_normalize(self, data: np.ndarray) -> np.ndarray:
        """健康数据标准化（C扩展版本）"""
        if not self.is_compiled:
            return self._health_data_normalize_python(data)
        
        # 确保数据类型和连续性
        data = np.ascontiguousarray(data, dtype=np.float32)
        n_samples, n_features = data.shape
        
        # 创建输出数组
        output = np.zeros_like(data, dtype=np.float32)
        
        # 调用C函数
        lib = self.libraries['main']
        lib.health_data_normalize(
            data.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
            output.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
            n_samples,
            n_features
        )
        
        return output
    
    def nutrition_optimization(self, user_profile: np.ndarray, 
                              food_database: np.ndarray) -> np.ndarray:
        """营养优化（C扩展版本）"""
        if not self.is_compiled:
            return self._nutrition_optimization_python(user_profile, food_database)
        
        # 确保数据类型
        user_profile = user_profile.astype(np.float32)
        food_database = np.ascontiguousarray(food_database, dtype=np.float32)
        
        n_foods, n_nutrients = food_database.shape
        
        # 创建输出数组
        scores = np.zeros(n_foods, dtype=np.float32)
        
        # 调用C函数
        lib = self.libraries['main']
        lib.nutrition_optimization(
            user_profile.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
            food_database.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
            scores.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
            n_foods,
            n_nutrients
        )
        
        return scores
    
    def biomarker_processing(self, biomarkers: np.ndarray, 
                           reference: np.ndarray) -> np.ndarray:
        """生物标志物处理（C扩展版本）"""
        if not self.is_compiled:
            return self._biomarker_processing_python(biomarkers, reference)
        
        # 确保数据类型
        biomarkers = np.ascontiguousarray(biomarkers, dtype=np.float32)
        reference = reference.astype(np.float32)
        
        n_samples, n_markers = biomarkers.shape
        
        # 创建输出数组
        risk_scores = np.zeros(n_samples, dtype=np.float32)
        
        # 调用C函数
        lib = self.libraries['main']
        lib.biomarker_processing(
            biomarkers.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
            reference.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
            risk_scores.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
            n_samples,
            n_markers
        )
        
        return risk_scores
    
    def pattern_matching(self, data: np.ndarray, patterns: np.ndarray, 
                        threshold: float = 0.8) -> List[Tuple[int, int, float]]:
        """模式匹配（C扩展版本）"""
        if not self.is_compiled:
            return self._pattern_matching_python(data, patterns, threshold)
        
        # 确保数据类型
        data = data.astype(np.float32)
        patterns = np.ascontiguousarray(patterns, dtype=np.float32)
        
        data_length = len(data)
        n_patterns, pattern_length = patterns.shape
        
        # 创建匹配结果数组（预分配足够空间）
        max_matches = min(1000, data_length * n_patterns)
        matches = np.zeros(max_matches * 3, dtype=np.int32)
        
        # 调用C函数
        lib = self.libraries['main']
        match_count = lib.pattern_matching(
            data.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
            patterns.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
            matches.ctypes.data_as(ctypes.POINTER(ctypes.c_int)),
            data_length,
            n_patterns,
            pattern_length,
            ctypes.c_float(threshold)
        )
        
        # 解析结果
        results = []
        for i in range(min(match_count, max_matches)):
            position = matches[i * 3]
            pattern_id = matches[i * 3 + 1]
            similarity = matches[i * 3 + 2] / 1000.0
            results.append((position, pattern_id, similarity))
        
        return results
    
    # Python备用实现
    def _tcm_syndrome_analysis_python(self, symptoms: np.ndarray, 
                                     weights: np.ndarray, patterns: np.ndarray) -> np.ndarray:
        """中医证候分析（Python备用实现）"""
        weighted_symptoms = symptoms * weights
        scores = np.dot(patterns, weighted_symptoms)
        total = np.sum(scores)
        return scores / total if total > 0 else scores
    
    def _health_data_normalize_python(self, data: np.ndarray) -> np.ndarray:
        """健康数据标准化（Python备用实现）"""
        mean = np.mean(data, axis=0)
        std = np.std(data, axis=0)
        std = np.where(std > 1e-8, std, 1.0)
        return (data - mean) / std
    
    def _nutrition_optimization_python(self, user_profile: np.ndarray, 
                                      food_database: np.ndarray) -> np.ndarray:
        """营养优化（Python备用实现）"""
        # 计算余弦相似度
        user_norm = np.linalg.norm(user_profile)
        food_norms = np.linalg.norm(food_database, axis=1)
        
        if user_norm > 1e-8:
            dot_products = np.dot(food_database, user_profile)
            similarities = dot_products / (user_norm * food_norms + 1e-8)
        else:
            similarities = np.zeros(len(food_database))
        
        return similarities
    
    def _biomarker_processing_python(self, biomarkers: np.ndarray, 
                                    reference: np.ndarray) -> np.ndarray:
        """生物标志物处理（Python备用实现）"""
        deviations = np.abs(biomarkers - reference) / (reference + 1e-8)
        risks = 1.0 / (1.0 + np.exp(-5.0 * (deviations - 0.2)))
        return np.mean(risks, axis=1)
    
    def _pattern_matching_python(self, data: np.ndarray, patterns: np.ndarray, 
                                threshold: float) -> List[Tuple[int, int, float]]:
        """模式匹配（Python备用实现）"""
        results = []
        data_length = len(data)
        n_patterns, pattern_length = patterns.shape
        
        for i in range(data_length - pattern_length + 1):
            segment = data[i:i + pattern_length]
            
            for p in range(n_patterns):
                pattern = patterns[p]
                
                # 计算相关系数
                correlation = np.corrcoef(segment, pattern)[0, 1]
                if not np.isnan(correlation) and correlation >= threshold:
                    results.append((i, p, correlation))
        
        return results
    
    def get_performance_info(self) -> Dict[str, Any]:
        """获取性能信息"""
        return {
            "c_extension_available": self.is_compiled,
            "system": self.system,
            "architecture": self.architecture,
            "openmp_enabled": self.config.use_openmp,
            "simd_enabled": self.config.use_simd,
            "optimization_level": self.config.optimization_level,
            "library_path": self.library_path if self.is_compiled else None
        }
    
    def benchmark_algorithms(self, data_sizes: List[int] = None) -> Dict[str, Any]:
        """算法性能基准测试"""
        if data_sizes is None:
            data_sizes = [100, 500, 1000, 2000]
        
        results = {}
        
        for size in data_sizes:
            # 生成测试数据
            symptoms = np.random.rand(20).astype(np.float32)
            weights = np.random.rand(20).astype(np.float32)
            patterns = np.random.rand(4, 20).astype(np.float32)
            health_data = np.random.rand(size, 50).astype(np.float32)
            
            # 测试中医证候分析
            import time
            start_time = time.time()
            for _ in range(100):
                self.tcm_syndrome_analysis(symptoms, weights, patterns)
            tcm_time = time.time() - start_time
            
            # 测试健康数据标准化
            start_time = time.time()
            for _ in range(10):
                self.health_data_normalize(health_data)
            normalize_time = time.time() - start_time
            
            results[f"size_{size}"] = {
                "tcm_syndrome_time": tcm_time,
                "normalize_time": normalize_time,
                "c_extension_used": self.is_compiled
            }
        
        return results
    
    def __del__(self):
        """清理资源"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            import shutil
            try:
                shutil.rmtree(self.temp_dir)
            except:
                pass


# 全局C扩展实例
_c_extension = None

def get_c_extension(config: Optional[CExtensionConfig] = None) -> CAlgorithmExtension:
    """获取C扩展实例（单例模式）"""
    global _c_extension
    if _c_extension is None:
        _c_extension = CAlgorithmExtension(config)
    return _c_extension


# 便捷函数接口
def tcm_syndrome_analysis_c(symptoms: np.ndarray, weights: np.ndarray, 
                           patterns: np.ndarray) -> np.ndarray:
    """中医证候分析（C扩展）"""
    ext = get_c_extension()
    return ext.tcm_syndrome_analysis(symptoms, weights, patterns)


def health_data_normalize_c(data: np.ndarray) -> np.ndarray:
    """健康数据标准化（C扩展）"""
    ext = get_c_extension()
    return ext.health_data_normalize(data)


def nutrition_optimization_c(user_profile: np.ndarray, 
                            food_database: np.ndarray) -> np.ndarray:
    """营养优化（C扩展）"""
    ext = get_c_extension()
    return ext.nutrition_optimization(user_profile, food_database)


def biomarker_processing_c(biomarkers: np.ndarray, 
                          reference: np.ndarray) -> np.ndarray:
    """生物标志物处理（C扩展）"""
    ext = get_c_extension()
    return ext.biomarker_processing(biomarkers, reference)


def pattern_matching_c(data: np.ndarray, patterns: np.ndarray, 
                      threshold: float = 0.8) -> List[Tuple[int, int, float]]:
    """模式匹配（C扩展）"""
    ext = get_c_extension()
    return ext.pattern_matching(data, patterns, threshold)


if __name__ == "__main__":
    # 测试C扩展
    print("索克生活 - C算法扩展测试")
    
    # 创建测试数据
    symptoms = np.random.rand(20).astype(np.float32)
    weights = np.random.rand(20).astype(np.float32)
    patterns = np.random.rand(4, 20).astype(np.float32)
    
    # 测试中医证候分析
    scores = tcm_syndrome_analysis_c(symptoms, weights, patterns)
    print(f"证候评分: {scores}")
    
    # 测试健康数据标准化
    health_data = np.random.rand(100, 30).astype(np.float32)
    normalized = health_data_normalize_c(health_data)
    print(f"标准化数据形状: {normalized.shape}")
    
    # 获取性能信息
    ext = get_c_extension()
    perf_info = ext.get_performance_info()
    print(f"性能信息: {perf_info}")
    
    # 运行基准测试
    benchmark_results = ext.benchmark_algorithms([100, 500])
    print(f"基准测试结果: {benchmark_results}") 