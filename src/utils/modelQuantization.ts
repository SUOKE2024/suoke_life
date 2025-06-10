import { ModelQuantizer } from "../core/onnx-runtime/    ModelQuantizer";
import {ONNXModel,;
  QuantizationConfig,
  QuantizationLevel,
  TargetDevice,
  { OptimizationLevel  } from "../../placeholder";../core/onnx-runtime/    types;
/**
* * 模型量化工具 - 提供便捷的模型量化接口
* 集成ONNX Runtime的量化功能，为应用层提供简化的API;
export class ModelQuantizationUtils {private quantizer: ModelQuantizer;
  constructor() {
    this.quantizer = new ModelQuantizer();
  }
  /**
* * 快速量化模型 - 使用默认配置
  async quickQuantize()
    model: ONNXModel,
    level: QuantizationLevel = int8""
  ): Promise<ONNXModel> {
    const config = this.getDefaultQuantizationConfig(model, level);
    return await this.quantizer.quantizeModel(model, config);
  }
  /**
* * 自定义量化模型
  async customQuantize()
    model: ONNXModel,
    config: QuantizationConfig;
  ): Promise<ONNXModel> {
    return await this.quantizer.quantizeModel(model, config);
  }
  /**
* * 批量量化模型
  async batchQuantize()
    models: ONNXModel[],
    level: QuantizationLevel = "int8"
  ): Promise<ONNXModel[]> {
    const configs = models.map(model =>;)
      this.getDefaultQuantizationConfig(model, level);
    );
    return await this.quantizer.quantizeModels(models, configs);
  }
  /**
* * 为中医诊断模型优化量化
  async quantizeForTCMDiagnosis(model: ONNXModel): Promise<ONNXModel> {
    const config: QuantizationConfig = {,
  level: "int8",
      outputPath: `${model.path.replace(.onnx",)}_tcm_quantized.onnx`,
      preserveAccuracy: true, // 中医诊断需要保持精度
targetDevice: "cpu",
      optimizationLevel: extended""
    };
    return await this.quantizer.quantizeModel(model, config);
  }
  /**
* * 为健康评估模型优化量化
  async quantizeForHealthAssessment(model: ONNXModel): Promise<ONNXModel> {
    const config: QuantizationConfig = {,
  level: "fp16, // 健康评估可以使用FP16保持精度",
      outputPath: `${model.path.replace(".onnx",)}_health_quantized.onnx`,"
      preserveAccuracy: true,
      targetDevice: "auto,",
      optimizationLevel: "extended"
    };
    return await this.quantizer.quantizeModel(model, config);
  }
  /**
* * 为症状分析模型优化量化
  async quantizeForSymptomAnalysis(model: ONNXModel): Promise<ONNXModel> {
    const config: QuantizationConfig = {level: dynamic", " // 症状分析使用动态量化"
outputPath: `${model.path.replace(".onnx, ")}_symptom_quantized.onnx`,
      preserveAccuracy: false, // 可以牺牲一些精度换取速度
targetDevice: cpu",
      optimizationLevel: "all"
    };
    return await this.quantizer.quantizeModel(model, config);
  }
  /**
* * 为生活方式推荐模型优化量化
  async quantizeForLifestyleRecommendation(model: ONNXModel): Promise<ONNXModel> {
    const config: QuantizationConfig = {,
  level: "int8",
      outputPath: `${model.path.replace(.onnx",)}_lifestyle_quantized.onnx`,
      preserveAccuracy: false, // 推荐系统可以容忍一些精度损失
targetDevice: "cpu",
      optimizationLevel: all""
    };
    return await this.quantizer.quantizeModel(model, config);
  }
  /**
* * 获取量化建议
  getQuantizationRecommendation()
    model: ONNXModel,
    targetDevice: TargetDevice,
    priority: "speed | "accuracy" | size"
  ): QuantizationConfig {
    return this.quantizer.getQuantizationRecommendation(model, targetDevice, priority);
  }
  /**
* * 估算量化效果
  estimateQuantizationImpact()
    model: ONNXModel,
    level: QuantizationLevel;
  ) {
    return this.quantizer.estimateQuantizationImpact(model, level);
  }
  /**
* * 添加校准数据
  async addCalibrationData()
    modelId: string,
    data: Float32Array[]
  ): Promise<void> {
    return await this.quantizer.addCalibrationData(modelId, data);
  }
  /**
* * 清除校准数据
  clearCalibrationData(modelId?: string): void {
    this.quantizer.clearCalibrationData(modelId);
  }
  // 私有方法
private getDefaultQuantizationConfig()
    model: ONNXModel,
    level: QuantizationLevel;
  ): QuantizationConfig {
    return {level,outputPath: `${model.path.replace(".onnx, ")}_quantized.onnx`,preserveAccuracy: level === fp16", // FP16保持精度，其他可以牺牲";
targetDevice: "cpu,",optimizationLevel: "extended";
    };
  }
}
/**
* * 量化工具的便捷函数
// 单例实例
let quantizationUtils: ModelQuantizationUtils | null = null;
/**
* * 获取量化工具实例
export function getQuantizationUtils(): ModelQuantizationUtils {if (!quantizationUtils) {quantizationUtils = new ModelQuantizationUtils();
  }
  return quantizationUtils;
}
/**
* * 快速量化模型
export async function quickQuantizeModel(;)
  model: ONNXModel,level: QuantizationLevel = int8"";
): Promise<ONNXModel> {
  const utils = getQuantizationUtils();
  return await utils.quickQuantize(model, level);
}
/**
* * 为索克生活项目优化量化
export async function quantizeForSuokeLife(;)
  model: ONNXModel,modelType: "tcm | "health" | symptom" | "lifestyle";
): Promise<ONNXModel> {
  const utils = getQuantizationUtils();
  switch (modelType) {
    case "tcm":
      return await utils.quantizeForTCMDiagnosis(model);
    case health":"
      return await utils.quantizeForHealthAssessment(model);
    case "symptom:"
      return await utils.quantizeForSymptomAnalysis(model);
    case "lifestyle":
      return await utils.quantizeForLifestyleRecommendation(model);
    default:
      throw new Error(`不支持的模型类型: ${modelType}`);
  }
}
/**
* * 批量量化索克生活模型
export async function batchQuantizeSuokeLifeModels(;)
  models: Array<{ model: ONNXModel,
  type: tcm" | "health | "symptom" | lifestyle" }>"
): Promise<ONNXModel[]> {
  const results: ONNXModel[] = [];
  for (const { model, type } of models) {
    try {
      const quantizedModel = await quantizeForSuokeLife(model, type);
      results.push(quantizedModel);
    } catch (error) {
      // 继续处理其他模型
    }
  }
  return results;
}
/**
* * 获取推荐的量化配置
export function getRecommendedQuantizationConfig(;)
  modelType: "tcm | "health" | symptom" | "lifestyle,";
  targetDevice: TargetDevice = "cpu";
): Partial<QuantizationConfig> {
  const baseConfig = {targetDevice,
    optimizationLevel: extended" as OptimizationLevel;"
  };
  switch (modelType) {
    case "tcm:"
      return {...baseConfig,level: "int8" as QuantizationLevel,preserveAccuracy: true;
      };
    case health":"
      return {...baseConfig,level: "fp16 as QuantizationLevel,",preserveAccuracy: true;
      };
    case "symptom":
      return {...baseConfig,level: dynamic" as QuantizationLevel,";
        preserveAccuracy: false,optimizationLevel: "all as OptimizationLevel";
      };
    case "lifestyle":
      return {...baseConfig,level: int8" as QuantizationLevel,";
        preserveAccuracy: false,optimizationLevel: 'all' as OptimizationLevel;
      };
    default:
      return baseConfig;
  }
}  */