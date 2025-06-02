/**
 * ONNX Runtime 使用示例
 * 展示如何在索克生活项目中使用设备端AI推理功能
 */

import {
  ONNXRuntimeManager,
  createONNXRuntimeManager,
  deploySuokeLifeModel,
  quickDeploy,
  TensorProcessor,
  { ModelQuantizer } from '../core/onnx-runtime';
import { getQuantizationUtils, quantizeForSuokeLife } from '../utils/modelQuantization';
import { TensorData, ONNXModel } from '../core/onnx-runtime/types';

/**
 * 示例1：基础使用 - 快速部署和推理
 */
export async function basicUsageExample() {
  console.log('=== 基础使用示例 ===');

  try {
    // 1. 快速部署模型
    const { manager, model } = await quickDeploy('/models/tcm_diagnosis.onnx');
    
    console.log(`模型部署成功: ${model.name}`);
    console.log(`模型ID: ${model.id}`);

    // 2. 准备输入数据
    const inputData: TensorData = {
      data: new Float32Array([1.0, 2.0, 3.0, 4.0]),
      dims: [1, 4],
      type: 'float32'
    };

    // 3. 执行推理
    const outputs = await manager.smartInference(model.id, {
      'input': inputData
    }, {
      useCache: true,
      preprocessInputs: true,
      postprocessOutputs: true
    });

    console.log('推理结果:', outputs);

    // 4. 清理资源
    await manager.destroy();

  } catch (error) {
    console.error('基础使用示例失败:', error);
  }
}

/**
 * 示例2：索克生活专用 - 中医诊断模型
 */
export async function tcmDiagnosisExample() {
  console.log('=== 中医诊断示例 ===');

  try {
    // 1. 部署中医诊断模型
    const { manager, model } = await deploySuokeLifeModel(
      '/models/tcm_diagnosis_v2.onnx',
      'tcm'
    );

    // 2. 准备中医诊断数据
    const patientData = {
      // 四诊数据
      pulse: new Float32Array([0.8, 0.6, 0.7]), // 脉诊数据
      tongue: new Float32Array([0.5, 0.3, 0.9]), // 舌诊数据
      complexion: new Float32Array([0.4, 0.8, 0.2]), // 面诊数据
      symptoms: new Float32Array([1, 0, 1, 0, 1]) // 症状数据
    };

    // 3. 转换为张量格式
    const inputs: Record<string, TensorData> = {
      pulse: {
        data: patientData.pulse,
        dims: [1, 3],
        type: 'float32'
      },
      tongue: {
        data: patientData.tongue,
        dims: [1, 3],
        type: 'float32'
      },
      complexion: {
        data: patientData.complexion,
        dims: [1, 3],
        type: 'float32'
      },
      symptoms: {
        data: patientData.symptoms,
        dims: [1, 5],
        type: 'float32'
      }
    };

    // 4. 执行中医诊断推理
    const diagnosis = await manager.smartInference(model.id, inputs, {
      useCache: true,
      preprocessInputs: true,
      postprocessOutputs: true
    });

    // 5. 解析诊断结果
    const diagnosisResult = parseTCMDiagnosis(diagnosis);
    console.log('中医诊断结果:', diagnosisResult);

    await manager.destroy();

  } catch (error) {
    console.error('中医诊断示例失败:', error);
  }
}

/**
 * 示例3：健康评估模型
 */
export async function healthAssessmentExample() {
  console.log('=== 健康评估示例 ===');

  try {
    const { manager, model } = await deploySuokeLifeModel(
      '/models/health_assessment.onnx',
      'health'
    );

    // 健康数据
    const healthData = {
      vitals: new Float32Array([120, 80, 72, 36.5]), // 血压、心率、体温
      biomarkers: new Float32Array([5.5, 2.1, 1.8, 0.9]), // 生物标志物
      lifestyle: new Float32Array([7, 3, 1, 0]) // 生活方式评分
    };

    const inputs: Record<string, TensorData> = {
      vitals: {
        data: healthData.vitals,
        dims: [1, 4],
        type: 'float32'
      },
      biomarkers: {
        data: healthData.biomarkers,
        dims: [1, 4],
        type: 'float32'
      },
      lifestyle: {
        data: healthData.lifestyle,
        dims: [1, 4],
        type: 'float32'
      }
    };

    const assessment = await manager.smartInference(model.id, inputs);
    const healthScore = parseHealthAssessment(assessment);
    
    console.log('健康评估结果:', healthScore);

    await manager.destroy();

  } catch (error) {
    console.error('健康评估示例失败:', error);
  }
}

/**
 * 示例4：高级功能 - 模型量化和优化
 */
export async function advancedOptimizationExample() {
  console.log('=== 高级优化示例 ===');

  try {
    const manager = createONNXRuntimeManager();
    await manager.initialize();

    // 1. 加载原始模型
    const originalModel = await manager.getModelLoader().loadModel('/models/symptom_analysis.onnx');
    console.log(`原始模型大小: ${originalModel.size} bytes`);

    // 2. 模型量化
    const quantizedModel = await quantizeForSuokeLife(originalModel, 'symptom');
    console.log(`量化后模型大小: ${quantizedModel.size} bytes`);
    console.log(`压缩比: ${(originalModel.size / quantizedModel.size).toFixed(2)}x`);

    // 3. 模型优化
    const optimizer = manager.getModelOptimizer();
    const optimizedModel = await optimizer.optimizeModel(quantizedModel, {
      level: 'all',
      enableGraphOptimization: true,
      enableMemoryOptimization: true,
      enableCpuOptimization: true,
      targetDevice: 'cpu',
      preserveAccuracy: false
    });

    // 4. 性能对比测试
    await performanceComparison(manager, originalModel, optimizedModel);

    await manager.destroy();

  } catch (error) {
    console.error('高级优化示例失败:', error);
  }
}

/**
 * 示例5：批量处理和缓存
 */
export async function batchProcessingExample() {
  console.log('=== 批量处理示例 ===');

  try {
    const manager = createONNXRuntimeManager();
    await manager.initialize();

    // 部署生活方式推荐模型
    const model = await manager.deployModel('/models/lifestyle_recommendation.onnx', {
      quantize: true,
      optimize: true,
      cache: true
    });

    // 批量用户数据
    const batchUserData = [
      { age: 25, activity: 3, diet: 2, sleep: 7 },
      { age: 35, activity: 2, diet: 3, sleep: 6 },
      { age: 45, activity: 1, diet: 1, sleep: 5 },
      { age: 55, activity: 4, diet: 4, sleep: 8 }
    ];

    // 批量推理
    const recommendations = [];
    for (const userData of batchUserData) {
      const input: TensorData = {
        data: new Float32Array([userData.age, userData.activity, userData.diet, userData.sleep]),
        dims: [1, 4],
        type: 'float32'
      };

      const result = await manager.smartInference(model.id, { input }, {
        useCache: true,
        preprocessInputs: true,
        postprocessOutputs: true
      });

      recommendations.push(parseLifestyleRecommendation(result));
    }

    console.log('批量推荐结果:', recommendations);

    // 查看缓存统计
    const cacheStats = manager.getInferenceCache().getStats();
    console.log('缓存统计:', cacheStats);

    await manager.destroy();

  } catch (error) {
    console.error('批量处理示例失败:', error);
  }
}

/**
 * 示例6：张量处理和数据预处理
 */
export async function tensorProcessingExample() {
  console.log('=== 张量处理示例 ===');

  try {
    const tensorProcessor = new TensorProcessor();

    // 1. 创建测试张量
    const originalTensor = tensorProcessor.createRandomTensor([2, 3, 4], 'float32', 0, 100);
    console.log('原始张量统计:', tensorProcessor.calculateTensorStats(originalTensor));

    // 2. 预处理
    const preprocessedTensor = await tensorProcessor.preprocess(originalTensor);
    console.log('预处理后统计:', tensorProcessor.calculateTensorStats(preprocessedTensor));

    // 3. 数据类型转换
    const int8Tensor = await tensorProcessor.convertTensorType(preprocessedTensor, 'uint8');
    console.log('转换为uint8后:', tensorProcessor.calculateTensorStats(int8Tensor));

    // 4. 形状变换
    const reshapedTensor = await tensorProcessor.reshapeTensor(int8Tensor, [6, 4]);
    console.log('重塑后形状:', reshapedTensor.dims);

    // 5. 批量处理
    const tensors = [originalTensor, preprocessedTensor, int8Tensor];
    const batchProcessed = await tensorProcessor.batchProcess(tensors, 'postprocess');
    console.log(`批量处理完成，处理了 ${batchProcessed.length} 个张量`);

  } catch (error) {
    console.error('张量处理示例失败:', error);
  }
}

/**
 * 示例7：系统监控和性能分析
 */
export async function systemMonitoringExample() {
  console.log('=== 系统监控示例 ===');

  try {
    const manager = createONNXRuntimeManager();
    await manager.initialize();

    // 部署模型
    const model = await manager.deployModel('/models/tcm_diagnosis.onnx');

    // 执行多次推理以收集性能数据
    for (let i = 0; i < 10; i++) {
      const input: TensorData = {
        data: new Float32Array(Array.from({ length: 100 }, () => Math.random())),
        dims: [1, 100],
        type: 'float32'
      };

      await manager.smartInference(model.id, { input });
    }

    // 获取系统状态
    const systemStatus = manager.getSystemStatus();
    console.log('系统状态:', JSON.stringify(systemStatus, null, 2));

    // 获取设备能力
    const deviceCapabilities = manager.getDeviceCapabilityDetector().getLastDetectionResult();
    console.log('设备能力:', deviceCapabilities);

    // 获取边缘计算统计
    const edgeStats = manager.getEdgeComputeManager().getStats();
    console.log('边缘计算统计:', edgeStats);

    await manager.destroy();

  } catch (error) {
    console.error('系统监控示例失败:', error);
  }
}

// 辅助函数

function parseTCMDiagnosis(outputs: Record<string, TensorData>) {
  // 解析中医诊断结果
  const syndromeOutput = outputs['syndrome'];
  const constitutionOutput = outputs['constitution'];
  
  if (syndromeOutput && constitutionOutput) {
    const syndromeProbs = Array.from(syndromeOutput.data);
    const constitutionProbs = Array.from(constitutionOutput.data);
    
    return {
      syndrome: {
        type: getSyndromeType(syndromeProbs.indexOf(Math.max(...syndromeProbs))),
        confidence: Math.max(...syndromeProbs)
      },
      constitution: {
        type: getConstitutionType(constitutionProbs.indexOf(Math.max(...constitutionProbs))),
        confidence: Math.max(...constitutionProbs)
      }
    };
  }
  
  return { error: '诊断结果解析失败' };
}

function parseHealthAssessment(outputs: Record<string, TensorData>) {
  const scoreOutput = outputs['health_score'];
  const riskOutput = outputs['risk_factors'];
  
  if (scoreOutput && riskOutput) {
    return {
      overallScore: Array.from(scoreOutput.data)[0] * 100,
      riskFactors: Array.from(riskOutput.data),
      recommendation: getHealthRecommendation(Array.from(scoreOutput.data)[0])
    };
  }
  
  return { error: '健康评估解析失败' };
}

function parseLifestyleRecommendation(outputs: Record<string, TensorData>) {
  const recommendationOutput = outputs['recommendations'];
  
  if (recommendationOutput) {
    const recommendations = Array.from(recommendationOutput.data);
    return {
      exercise: recommendations[0],
      diet: recommendations[1],
      sleep: recommendations[2],
      stress: recommendations[3]
    };
  }
  
  return { error: '生活方式推荐解析失败' };
}

async function performanceComparison(
  manager: ONNXRuntimeManager,
  originalModel: ONNXModel,
  optimizedModel: ONNXModel
) {
  console.log('开始性能对比测试...');

  const testInput: TensorData = {
    data: new Float32Array(Array.from({ length: 100 }, () => Math.random())),
    dims: [1, 100],
    type: 'float32'
  };

  // 测试原始模型
  await manager.getInferenceEngine().loadModel(originalModel);
  const originalStart = performance.now();
  await manager.smartInference(originalModel.id, { input: testInput });
  const originalTime = performance.now() - originalStart;

  // 测试优化模型
  await manager.getInferenceEngine().loadModel(optimizedModel);
  const optimizedStart = performance.now();
  await manager.smartInference(optimizedModel.id, { input: testInput });
  const optimizedTime = performance.now() - optimizedStart;

  console.log(`原始模型推理时间: ${originalTime.toFixed(2)}ms`);
  console.log(`优化模型推理时间: ${optimizedTime.toFixed(2)}ms`);
  console.log(`性能提升: ${(originalTime / optimizedTime).toFixed(2)}x`);
}

function getSyndromeType(index: number): string {
  const syndromes = ['气虚', '血虚', '阴虚', '阳虚', '气滞', '血瘀', '痰湿', '湿热'];
  return syndromes[index] || '未知';
}

function getConstitutionType(index: number): string {
  const constitutions = ['平和质', '气虚质', '阳虚质', '阴虚质', '痰湿质', '湿热质', '血瘀质', '气郁质', '特禀质'];
  return constitutions[index] || '未知';
}

function getHealthRecommendation(score: number): string {
  if (score > 0.8) return '健康状况良好，继续保持';
  if (score > 0.6) return '健康状况一般，建议改善生活方式';
  if (score > 0.4) return '存在健康风险，建议咨询医生';
  return '健康状况较差，建议立即就医';
}

// 导出所有示例函数
export const examples = {
  basicUsageExample,
  tcmDiagnosisExample,
  healthAssessmentExample,
  advancedOptimizationExample,
  batchProcessingExample,
  tensorProcessingExample,
  systemMonitoringExample
};

// 运行所有示例的函数
export async function runAllExamples() {
  console.log('开始运行所有ONNX Runtime示例...\n');

  const exampleFunctions = Object.values(examples);
  
  for (const exampleFn of exampleFunctions) {
    try {
      await exampleFn();
      console.log('\n');
    } catch (error) {
      console.error(`示例执行失败: ${exampleFn.name}`, error);
      console.log('\n');
    }
  }

  console.log('所有示例执行完成！');
} 