#include <Python.h>
#include <numpy/arrayobject.h>
#include <math.h>
#include <string.h>
#include <omp.h>

/*
 * 索克生活 - 中医证候分析C扩展
 * 高性能中医证候分析算法实现
 */

// 中医证候分析核心算法
static PyObject* tcm_syndrome_analysis(PyObject* self, PyObject* args) {
    PyArrayObject *symptoms, *weights, *patterns;
    
    // 解析Python参数
    if (!PyArg_ParseTuple(args, "OOO", &symptoms, &weights, &patterns)) {
        return NULL;
    }
    
    // 检查数组类型和维度
    if (!PyArray_Check(symptoms) || !PyArray_Check(weights) || !PyArray_Check(patterns)) {
        PyErr_SetString(PyExc_TypeError, "输入必须是NumPy数组");
        return NULL;
    }
    
    // 获取数组维度
    int n_symptoms = PyArray_DIM(symptoms, 0);
    int n_patterns = PyArray_DIM(patterns, 0);
    
    // 创建结果数组
    npy_intp dims[1] = {n_patterns};
    PyArrayObject *result = (PyArrayObject*)PyArray_SimpleNew(1, dims, NPY_FLOAT32);
    
    // 获取数据指针
    float *symptoms_data = (float*)PyArray_DATA(symptoms);
    float *weights_data = (float*)PyArray_DATA(weights);
    float *patterns_data = (float*)PyArray_DATA(patterns);
    float *result_data = (float*)PyArray_DATA(result);
    
    // 并行计算证候得分
    #pragma omp parallel for
    for (int i = 0; i < n_patterns; i++) {
        float score = 0.0f;
        
        for (int j = 0; j < n_symptoms; j++) {
            float weighted_symptom = symptoms_data[j] * weights_data[j];
            float pattern_weight = patterns_data[i * n_symptoms + j];
            score += weighted_symptom * pattern_weight;
        }
        
        // 应用sigmoid激活函数
        result_data[i] = 1.0f / (1.0f + expf(-score));
    }
    
    return (PyObject*)result;
}

// 健康数据标准化算法
static PyObject* health_data_normalize(PyObject* self, PyObject* args) {
    PyArrayObject *data;
    
    if (!PyArg_ParseTuple(args, "O", &data)) {
        return NULL;
    }
    
    if (!PyArray_Check(data)) {
        PyErr_SetString(PyExc_TypeError, "输入必须是NumPy数组");
        return NULL;
    }
    
    int n_samples = PyArray_DIM(data, 0);
    int n_features = PyArray_DIM(data, 1);
    
    // 创建结果数组
    npy_intp dims[2] = {n_samples, n_features};
    PyArrayObject *result = (PyArrayObject*)PyArray_SimpleNew(2, dims, NPY_FLOAT32);
    
    float *data_ptr = (float*)PyArray_DATA(data);
    float *result_ptr = (float*)PyArray_DATA(result);
    
    // 计算每个特征的均值和标准差
    #pragma omp parallel for
    for (int j = 0; j < n_features; j++) {
        float mean = 0.0f;
        float variance = 0.0f;
        
        // 计算均值
        for (int i = 0; i < n_samples; i++) {
            mean += data_ptr[i * n_features + j];
        }
        mean /= n_samples;
        
        // 计算方差
        for (int i = 0; i < n_samples; i++) {
            float diff = data_ptr[i * n_features + j] - mean;
            variance += diff * diff;
        }
        variance /= n_samples;
        float std = sqrtf(variance + 1e-8f);  // 避免除零
        
        // 标准化
        for (int i = 0; i < n_samples; i++) {
            result_ptr[i * n_features + j] = (data_ptr[i * n_features + j] - mean) / std;
        }
    }
    
    return (PyObject*)result;
}

// 营养优化匹配算法
static PyObject* nutrition_optimization(PyObject* self, PyObject* args) {
    PyArrayObject *user_profile, *food_database;
    
    if (!PyArg_ParseTuple(args, "OO", &user_profile, &food_database)) {
        return NULL;
    }
    
    if (!PyArray_Check(user_profile) || !PyArray_Check(food_database)) {
        PyErr_SetString(PyExc_TypeError, "输入必须是NumPy数组");
        return NULL;
    }
    
    int n_foods = PyArray_DIM(food_database, 0);
    int n_features = PyArray_DIM(food_database, 1);
    
    // 创建结果数组
    npy_intp dims[1] = {n_foods};
    PyArrayObject *result = (PyArrayObject*)PyArray_SimpleNew(1, dims, NPY_FLOAT32);
    
    float *profile_data = (float*)PyArray_DATA(user_profile);
    float *foods_data = (float*)PyArray_DATA(food_database);
    float *result_data = (float*)PyArray_DATA(result);
    
    // 计算用户档案的L2范数
    float profile_norm = 0.0f;
    for (int i = 0; i < n_features; i++) {
        profile_norm += profile_data[i] * profile_data[i];
    }
    profile_norm = sqrtf(profile_norm);
    
    // 并行计算食物匹配度（余弦相似度）
    #pragma omp parallel for
    for (int i = 0; i < n_foods; i++) {
        float dot_product = 0.0f;
        float food_norm = 0.0f;
        
        for (int j = 0; j < n_features; j++) {
            float food_feature = foods_data[i * n_features + j];
            dot_product += profile_data[j] * food_feature;
            food_norm += food_feature * food_feature;
        }
        
        food_norm = sqrtf(food_norm);
        
        // 余弦相似度
        if (profile_norm > 0.0f && food_norm > 0.0f) {
            result_data[i] = dot_product / (profile_norm * food_norm);
        } else {
            result_data[i] = 0.0f;
        }
    }
    
    return (PyObject*)result;
}

// 生物标志物处理算法
static PyObject* biometric_processing(PyObject* self, PyObject* args) {
    PyArrayObject *biomarkers;
    float threshold;
    
    if (!PyArg_ParseTuple(args, "Of", &biomarkers, &threshold)) {
        return NULL;
    }
    
    if (!PyArray_Check(biomarkers)) {
        PyErr_SetString(PyExc_TypeError, "输入必须是NumPy数组");
        return NULL;
    }
    
    int n_samples = PyArray_DIM(biomarkers, 0);
    int n_markers = PyArray_DIM(biomarkers, 1);
    
    // 创建结果数组
    npy_intp dims[2] = {n_samples, n_markers};
    PyArrayObject *result = (PyArrayObject*)PyArray_SimpleNew(2, dims, NPY_FLOAT32);
    
    float *input_data = (float*)PyArray_DATA(biomarkers);
    float *result_data = (float*)PyArray_DATA(result);
    
    // 并行处理生物标志物
    #pragma omp parallel for
    for (int i = 0; i < n_samples; i++) {
        for (int j = 0; j < n_markers; j++) {
            float value = input_data[i * n_markers + j];
            
            // 应用阈值和非线性变换
            if (value > threshold) {
                result_data[i * n_markers + j] = tanhf(value - threshold);
            } else {
                result_data[i * n_markers + j] = value * 0.1f;  // 抑制低值
            }
        }
    }
    
    return (PyObject*)result;
}

// 模式匹配算法
static PyObject* pattern_matching(PyObject* self, PyObject* args) {
    PyArrayObject *query, *database;
    
    if (!PyArg_ParseTuple(args, "OO", &query, &database)) {
        return NULL;
    }
    
    if (!PyArray_Check(query) || !PyArray_Check(database)) {
        PyErr_SetString(PyExc_TypeError, "输入必须是NumPy数组");
        return NULL;
    }
    
    int n_patterns = PyArray_DIM(database, 0);
    int pattern_length = PyArray_DIM(database, 1);
    
    // 创建结果数组
    npy_intp dims[1] = {n_patterns};
    PyArrayObject *result = (PyArrayObject*)PyArray_SimpleNew(1, dims, NPY_FLOAT32);
    
    float *query_data = (float*)PyArray_DATA(query);
    float *db_data = (float*)PyArray_DATA(database);
    float *result_data = (float*)PyArray_DATA(result);
    
    // 并行计算模式匹配度
    #pragma omp parallel for
    for (int i = 0; i < n_patterns; i++) {
        float similarity = 0.0f;
        
        for (int j = 0; j < pattern_length; j++) {
            float diff = query_data[j] - db_data[i * pattern_length + j];
            similarity += expf(-diff * diff);  // 高斯相似度
        }
        
        result_data[i] = similarity / pattern_length;
    }
    
    return (PyObject*)result;
}

// 方法定义表
static PyMethodDef TCMAnalysisMethods[] = {
    {"tcm_syndrome_analysis", tcm_syndrome_analysis, METH_VARARGS, "中医证候分析"},
    {"health_data_normalize", health_data_normalize, METH_VARARGS, "健康数据标准化"},
    {"nutrition_optimization", nutrition_optimization, METH_VARARGS, "营养优化匹配"},
    {"biometric_processing", biometric_processing, METH_VARARGS, "生物标志物处理"},
    {"pattern_matching", pattern_matching, METH_VARARGS, "模式匹配"},
    {NULL, NULL, 0, NULL}
};

// 模块定义
static struct PyModuleDef tcm_analysis_module = {
    PyModuleDef_HEAD_INIT,
    "tcm_analysis",
    "索克生活中医证候分析C扩展模块",
    -1,
    TCMAnalysisMethods
};

// 模块初始化函数
PyMODINIT_FUNC PyInit_tcm_analysis(void) {
    PyObject *module = PyModule_Create(&tcm_analysis_module);
    
    if (module == NULL) {
        return NULL;
    }
    
    // 初始化NumPy
    import_array();
    
    // 添加版本信息
    PyModule_AddStringConstant(module, "__version__", "1.0.0");
    PyModule_AddStringConstant(module, "__author__", "索克生活团队");
    
    return module;
} 