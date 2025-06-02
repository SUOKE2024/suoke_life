/**
 * ONNX Runtime 模块测试
 * 测试设备端AI推理功能的核心组件
 */

import { 
  ONNXInferenceEngine,
  ModelLoader,
  ModelQuantizer,
  ModelOptimizer,
  EdgeComputeManager,
  DeviceCapabilityDetector,
  InferenceCache,
  TensorProcessor,
  createONNXRuntimeManager,
  quickDeploy,
  { deploySuokeLifeModel } from '../core/onnx-runtime';
import {
  ONNXModel,
  TensorData,
  QuantizationConfig,
  ModelOptimizationOptions,
  { InferenceConfig } from '../core/onnx-runtime/types';
// Mock ONNX Runtime
jest.mock('onnxruntime-react-native', () => ({
  InferenceSession: {
    create: jest.fn().mockResolvedValue({
      run: jest.fn().mockResolvedValue({
        output: {
          data: new Float32Array([0.8, 0.2]),
          dims: [1, 2],
          type: 'float32'
        }
      }),
      release: jest.fn()
    })
  }
}));

describe('ONNX Runtime 核心功能测试', () => {
  
  describe('ONNXInferenceEngine', () => {
    let engine: ONNXInferenceEngine;

    beforeEach(() => {
      engine = new ONNXInferenceEngine();
    });

    afterEach(async () => {
      if (engine) {
        await engine.destroy();
      }
    });

    test('应该能够初始化推理引擎', async () => {
      const config: InferenceConfig = {
        executionProviders: ['cpu'],
        sessionOptions: {
          intraOpNumThreads: 2,
          interOpNumThreads: 1
        }
      };

      await engine.initialize(config);
      expect(engine.isInitialized()).toBe(true);
    });

    test('应该能够加载模型', async () => {
      const config: InferenceConfig = {
        executionProviders: ['cpu'],
        sessionOptions: {}
      };

      await engine.initialize(config);
      
      const mockModelPath = '/mock/model.onnx';
      const model = await engine.loadModel(mockModelPath);
      
      expect(model).toBeDefined();
      expect(model.id).toBeDefined();
      expect(model.path).toBe(mockModelPath);
    });

    test('应该能够执行推理', async () => {
      const config: InferenceConfig = {
        executionProviders: ['cpu'],
        sessionOptions: {}
      };

      await engine.initialize(config);
      const model = await engine.loadModel('/mock/model.onnx');

      const inputs: Record<string, TensorData> = {
        input: {
          data: new Float32Array([1, 2, 3, 4]),
          dims: [1, 4],
          type: 'float32'
        }
      };

      const outputs = await engine.runInference(model.id, inputs);
      expect(outputs).toBeDefined();
      expect(outputs.output).toBeDefined();
    });
  });

  describe('ModelQuantizer', () => {
    let quantizer: ModelQuantizer;

    beforeEach(() => {
      quantizer = new ModelQuantizer();
    });

    test('应该能够量化模型', async () => {
      const mockModel: ONNXModel = {
        id: 'test-model',
        path: '/mock/model.onnx',
        metadata: {
          name: 'test-model',
          version: '1.0.0',
          description: 'Test model',
          inputNames: ['input'],
          outputNames: ['output'],
          inputShapes: [[1, 4]],
          outputShapes: [[1, 2]]
        },
        session: null,
        isLoaded: false
      };

      const config: QuantizationConfig = {
        level: 'int8',
        calibrationData: [],
        targetDevice: 'cpu'
      };

      const quantizedModel = await quantizer.quantizeModel(mockModel, config);
      expect(quantizedModel).toBeDefined();
      expect(quantizedModel.id).toContain('quantized');
    });

    test('应该能够评估量化效果', async () => {
      const mockModel: ONNXModel = {
        id: 'test-model',
        path: '/mock/model.onnx',
        metadata: {
          name: 'test-model',
          version: '1.0.0',
          description: 'Test model',
          inputNames: ['input'],
          outputNames: ['output'],
          inputShapes: [[1, 4]],
          outputShapes: [[1, 2]]
        },
        session: null,
        isLoaded: false
      };

      const quantizedModel = { ...mockModel, id: 'quantized-model' };
      const testData = [{
        input: {
          data: new Float32Array([1, 2, 3, 4]),
          dims: [1, 4],
          type: 'float32' as const
        }
      }];

      const evaluation = await quantizer.evaluateQuantization(
        mockModel,
        quantizedModel,
        testData
      );

      expect(evaluation).toBeDefined();
      expect(evaluation.accuracyLoss).toBeGreaterThanOrEqual(0);
      expect(evaluation.speedup).toBeGreaterThan(0);
      expect(evaluation.sizeReduction).toBeGreaterThan(0);
    });
  });

  describe('EdgeComputeManager', () => {
    let manager: EdgeComputeManager;

    beforeEach(() => {
      manager = new EdgeComputeManager();
    });

    afterEach(async () => {
      if (manager) {
        await manager.destroy();
      }
    });

    test('应该能够初始化边缘计算管理器', async () => {
      const config = {
        maxConcurrentTasks: 4,
        memoryLimit: 1024,
        cpuThreshold: 80,
        enableThermalManagement: true
      };

      await manager.initialize(config);
      expect(manager.isInitialized()).toBe(true);
    });

    test('应该能够调度计算任务', async () => {
      const config = {
        maxConcurrentTasks: 2,
        memoryLimit: 1024,
        cpuThreshold: 80,
        enableThermalManagement: true
      };

      await manager.initialize(config);

      const task = {
        id: 'test-task',
        type: 'inference',
        priority: 1,
        execute: jest.fn().mockResolvedValue('result')
      };

      const result = await manager.scheduleTask(task);
      expect(result).toBe('result');
      expect(task.execute).toHaveBeenCalled();
    });

    test('应该能够监控系统资源', async () => {
      const config = {
        maxConcurrentTasks: 4,
        memoryLimit: 1024,
        cpuThreshold: 80,
        enableThermalManagement: true
      };

      await manager.initialize(config);

      const metrics = manager.getResourceMetrics();
      expect(metrics).toBeDefined();
      expect(metrics.cpuUsage).toBeGreaterThanOrEqual(0);
      expect(metrics.memoryUsage).toBeGreaterThanOrEqual(0);
    });
  });

  describe('DeviceCapabilityDetector', () => {
    let detector: DeviceCapabilityDetector;

    beforeEach(() => {
      detector = new DeviceCapabilityDetector();
    });

    test('应该能够检测设备能力', async () => {
      const capabilities = await detector.detectCapabilities();
      
      expect(capabilities).toBeDefined();
      expect(capabilities.cpu).toBeDefined();
      expect(capabilities.memory).toBeDefined();
      expect(capabilities.supportedProviders).toBeDefined();
      expect(Array.isArray(capabilities.supportedProviders)).toBe(true);
    });

    test('应该能够推荐配置', async () => {
      const capabilities = await detector.detectCapabilities();
      const config = detector.recommendConfiguration(capabilities);
      
      expect(config).toBeDefined();
      expect(config.executionProviders).toBeDefined();
      expect(config.sessionOptions).toBeDefined();
    });

    test('应该能够评估模型兼容性', async () => {
      const mockModel: ONNXModel = {
        id: 'test-model',
        path: '/mock/model.onnx',
        metadata: {
          name: 'test-model',
          version: '1.0.0',
          description: 'Test model',
          inputNames: ['input'],
          outputNames: ['output'],
          inputShapes: [[1, 224, 224, 3]],
          outputShapes: [[1, 1000]]
        },
        session: null,
        isLoaded: false
      };

      const compatibility = await detector.assessModelCompatibility(mockModel);
      
      expect(compatibility).toBeDefined();
      expect(compatibility.isCompatible).toBeDefined();
      expect(compatibility.recommendedProviders).toBeDefined();
      expect(compatibility.estimatedPerformance).toBeDefined();
    });
  });

  describe('InferenceCache', () => {
    let cache: InferenceCache;

    beforeEach(() => {
      cache = new InferenceCache();
    });

    afterEach(async () => {
      if (cache) {
        await cache.destroy();
      }
    });

    test('应该能够初始化缓存', async () => {
      const config = {
        maxSize: 100,
        ttl: 3600,
        enableCompression: true,
        enableEncryption: false
      };

      await cache.initialize(config);
      expect(cache.isInitialized()).toBe(true);
    });

    test('应该能够缓存和获取推理结果', async () => {
      const config = {
        maxSize: 100,
        ttl: 3600,
        enableCompression: false,
        enableEncryption: false
      };

      await cache.initialize(config);

      const key = 'test-key';
      const result: Record<string, TensorData> = {
        output: {
          data: new Float32Array([0.8, 0.2]),
          dims: [1, 2],
          type: 'float32'
        }
      };

      await cache.setInferenceResult(key, result);
      const cachedResult = await cache.getInferenceResult(key);

      expect(cachedResult).toBeDefined();
      expect(cachedResult!.output.data).toEqual(result.output.data);
    });

    test('应该能够管理缓存统计', async () => {
      const config = {
        maxSize: 100,
        ttl: 3600,
        enableCompression: false,
        enableEncryption: false
      };

      await cache.initialize(config);

      const stats = cache.getStats();
      expect(stats).toBeDefined();
      expect(stats.hitCount).toBeGreaterThanOrEqual(0);
      expect(stats.missCount).toBeGreaterThanOrEqual(0);
      expect(stats.size).toBeGreaterThanOrEqual(0);
    });
  });

  describe('TensorProcessor', () => {
    let processor: TensorProcessor;

    beforeEach(() => {
      processor = new TensorProcessor();
    });

    test('应该能够预处理张量数据', async () => {
      const inputTensor: TensorData = {
        data: new Float32Array([1, 2, 3, 4]),
        dims: [1, 4],
        type: 'float32'
      };

      const processedTensor = await processor.preprocess(inputTensor);
      
      expect(processedTensor).toBeDefined();
      expect(processedTensor.data).toBeDefined();
      expect(processedTensor.dims).toEqual(inputTensor.dims);
      expect(processedTensor.type).toBe(inputTensor.type);
    });

    test('应该能够后处理张量数据', async () => {
      const outputTensor: TensorData = {
        data: new Float32Array([0.8, 0.2]),
        dims: [1, 2],
        type: 'float32'
      };

      const processedTensor = await processor.postprocess(outputTensor);
      
      expect(processedTensor).toBeDefined();
      expect(processedTensor.data).toBeDefined();
    });

    test('应该能够转换数据类型', async () => {
      const inputTensor: TensorData = {
        data: new Float32Array([1.5, 2.7, 3.2, 4.8]),
        dims: [1, 4],
        type: 'float32'
      };

      const convertedTensor = await processor.convertDataType(inputTensor, 'int32');
      
      expect(convertedTensor).toBeDefined();
      expect(convertedTensor.type).toBe('int32');
      expect(convertedTensor.data).toBeInstanceOf(Int32Array);
    });
  });

  describe('高级功能测试', () => {
    test('应该能够快速部署模型', async () => {
      const result = await quickDeploy('/mock/model.onnx');
      
      expect(result).toBeDefined();
      expect(result.manager).toBeDefined();
      expect(result.model).toBeDefined();
      expect(result.model.id).toBeDefined();
    });

    test('应该能够部署索克生活专用模型', async () => {
      const result = await deploySuokeLifeModel('/mock/tcm_model.onnx', 'tcm');
      
      expect(result).toBeDefined();
      expect(result.manager).toBeDefined();
      expect(result.model).toBeDefined();
      expect(result.model.metadata.name).toContain('tcm');
    });

    test('应该能够创建ONNX Runtime管理器', () => {
      const manager = createONNXRuntimeManager();
      
      expect(manager).toBeDefined();
      expect(manager.initialize).toBeDefined();
      expect(manager.deployModel).toBeDefined();
      expect(manager.smartInference).toBeDefined();
    });
  });

  describe('索克生活专用功能测试', () => {
    test('应该能够处理中医诊断数据', async () => {
      const processor = new TensorProcessor();
      
      // 模拟中医诊断输入数据
      const tcmData = {
        pulse: new Float32Array([0.8, 0.6, 0.7, 0.5]),
        tongue: new Float32Array([0.3, 0.9, 0.4, 0.6]),
        complexion: new Float32Array([0.7, 0.2, 0.8]),
        symptoms: new Float32Array([1, 0, 1, 0, 1, 1, 0])
      };

      const processedPulse = await processor.preprocess({
        data: tcmData.pulse,
        dims: [1, 4],
        type: 'float32'
      });

      expect(processedPulse).toBeDefined();
      expect(processedPulse.data.length).toBe(4);
    });

    test('应该能够处理健康评估数据', async () => {
      const processor = new TensorProcessor();
      
      // 模拟健康评估输入数据
      const healthData = {
        vitals: new Float32Array([120, 80, 72, 36.5]), // 血压、心率、体温
        biomarkers: new Float32Array([5.5, 4.2, 1.8]), // 血糖、胆固醇、炎症指标
        lifestyle: new Float32Array([7, 6, 8]) // 运动、饮食、睡眠评分
      };

      const processedVitals = await processor.preprocess({
        data: healthData.vitals,
        dims: [1, 4],
        type: 'float32'
      });

      expect(processedVitals).toBeDefined();
      expect(processedVitals.data.length).toBe(4);
    });

    test('应该能够处理症状分析数据', async () => {
      const processor = new TensorProcessor();
      
      // 模拟症状分析输入数据
      const symptomData = {
        symptoms: new Float32Array([1, 0, 1, 1, 0, 0, 1]), // 症状向量
        duration: new Float32Array([3, 0, 7, 2, 0, 0, 1]), // 持续天数
        severity: new Float32Array([2, 0, 3, 1, 0, 0, 2])  // 严重程度 1-3
      };

      const processedSymptoms = await processor.preprocess({
        data: symptomData.symptoms,
        dims: [1, 7],
        type: 'float32'
      });

      expect(processedSymptoms).toBeDefined();
      expect(processedSymptoms.data.length).toBe(7);
    });
  });

  describe('错误处理测试', () => {
    test('应该正确处理模型加载错误', async () => {
      const engine = new ONNXInferenceEngine();
      
      await expect(engine.loadModel('/invalid/path.onnx'))
        .rejects
        .toThrow();
    });

    test('应该正确处理推理错误', async () => {
      const engine = new ONNXInferenceEngine();
      
      await expect(engine.runInference('invalid-model-id', {}))
        .rejects
        .toThrow();
    });

    test('应该正确处理量化错误', async () => {
      const quantizer = new ModelQuantizer();
      const invalidModel = {} as ONNXModel;
      const config: QuantizationConfig = {
        level: 'int8',
        calibrationData: [],
        targetDevice: 'cpu'
      };
      
      await expect(quantizer.quantizeModel(invalidModel, config))
        .rejects
        .toThrow();
    });
  });

  describe('性能测试', () => {
    test('推理性能应该在可接受范围内', async () => {
      const engine = new ONNXInferenceEngine();
      const config: InferenceConfig = {
        executionProviders: ['cpu'],
        sessionOptions: {}
      };

      await engine.initialize(config);
      const model = await engine.loadModel('/mock/model.onnx');

      const inputs: Record<string, TensorData> = {
        input: {
          data: new Float32Array(224 * 224 * 3), // 模拟图像输入
          dims: [1, 224, 224, 3],
          type: 'float32'
        }
      };

      const startTime = Date.now();
      await engine.runInference(model.id, inputs);
      const endTime = Date.now();

      const inferenceTime = endTime - startTime;
      expect(inferenceTime).toBeLessThan(5000); // 推理时间应小于5秒
    });

    test('缓存命中率应该提高性能', async () => {
      const cache = new InferenceCache();
      const config = {
        maxSize: 100,
        ttl: 3600,
        enableCompression: false,
        enableEncryption: false
      };

      await cache.initialize(config);

      const key = 'performance-test-key';
      const result: Record<string, TensorData> = {
        output: {
          data: new Float32Array([0.8, 0.2]),
          dims: [1, 2],
          type: 'float32'
        }
      };

      // 第一次设置
      const setStartTime = Date.now();
      await cache.setInferenceResult(key, result);
      const setEndTime = Date.now();

      // 第二次获取（应该从缓存获取）
      const getStartTime = Date.now();
      const cachedResult = await cache.getInferenceResult(key);
      const getEndTime = Date.now();

      const setTime = setEndTime - setStartTime;
      const getTime = getEndTime - getStartTime;

      expect(cachedResult).toBeDefined();
      expect(getTime).toBeLessThan(setTime); // 获取应该比设置快
    });
  });
});

describe('集成测试', () => {
  test('完整的推理流程应该正常工作', async () => {
    // 创建管理器
    const manager = createONNXRuntimeManager();
    
    // 初始化
    await manager.initialize({
      executionProviders: ['cpu'],
      sessionOptions: {}
    });

    // 部署模型
    const model = await manager.deployModel('/mock/tcm_model.onnx', {
      quantize: true,
      optimize: true,
      cache: true
    });

    // 准备输入数据
    const inputs: Record<string, TensorData> = {
      pulse: {
        data: new Float32Array([0.8, 0.6, 0.7, 0.5]),
        dims: [1, 4],
        type: 'float32'
      },
      tongue: {
        data: new Float32Array([0.3, 0.9, 0.4, 0.6]),
        dims: [1, 4],
        type: 'float32'
      }
    };

    // 执行智能推理
    const outputs = await manager.smartInference(model.id, inputs);

    // 验证结果
    expect(outputs).toBeDefined();
    expect(Object.keys(outputs).length).toBeGreaterThan(0);

    // 清理
    await manager.destroy();
  });
}); 