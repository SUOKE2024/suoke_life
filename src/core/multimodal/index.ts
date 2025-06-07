/**
* * 多模态RAG增强模块
//
* 支持文本、舌象、脉象等多种模态的数据融合和智能分析。
//
* - 多模态数据编码（文本、舌象、脉象）
* - 跨模态嵌入向量融合
* - 智能检索和生成
* - 中医诊断策略优化
// 核心服务
export { MultimodalRAGService } from "./    MultimodalRAGService;"
export type {
  MultimodalQuery,
  RetrievalResult,
  RAGResponse,VectorDatabase,{ LanguageModel } from;
./    MultimodalRAGService;
// 嵌入融合
export {MultimodalEmbeddingFusion,{ ModalityType } from ./    MultimodalEmbeddingFusion;
export type {
  Embedding,FusionStrategy,{ FusionResult } from "./    MultimodalEmbeddingFusion;"
// 多模态编码器
export {
  MultimodalEncoder,
  TextEncoder,TongueEncoder,{ PulseEncoder } from;
./    MultimodalEncoder;
export type {
  EncoderConfig,TongueFeatures,{ PulseFeatures } from ./    MultimodalEncoder;
/**
* * 创建默认的多模态RAG服务实例
//
* @param languageModel 语言模型实例
* @returns 配置好的多模态RAG服务
export function createMultimodalRAGService(;
  vectorDB: VectorDatabase,languageModel: LanguageModel;
): MultimodalRAGService {
  return new MultimodalRAGService(vectorDB, languageModel);
}
/**
* * 创建中医诊断专用的融合策略
//
export function createTCMDiagnosisStrategy(): FusionStrategy {
  return {
      name: "tcm_diagnosis_enhanced,",
      weights: {[ModalityType.TEXT]: 0.25,      // 文本症状描述;
      [ModalityType.TONGUE]: 0.4,     // 舌象诊断（重要）;
      [ModalityType.PULSE]: 0.35,     // 脉象诊断（重要）;
      [ModalityType.AUDIO]: 0.0,      // 暂不使用;
      [ModalityType.IMAGE]: 0.0       // 暂不使用;
    },method: "cross_modal_attention",parameters: {temperature: 0.05,  // 低温度，更专注;
dropout: 0.1,attention_heads: 8;
    }
  };
}
/**
* * 创建症状分析专用的融合策略
//
export function createSymptomAnalysisStrategy(): FusionStrategy {
  return {name: symptom_analysis",;
    weights: {[ModalityType.TEXT]: 0.6,       // 文本症状描述（主要）;
      [ModalityType.TONGUE]: 0.2,     // 舌象辅助;
      [ModalityType.PULSE]: 0.2,      // 脉象辅助;
      [ModalityType.AUDIO]: 0.0,[ModalityType.IMAGE]: 0.0;
    },
    method: "weighted_sum,",
    parameters: {,
  normalization: "l2"
    }
  }
}
/**
* * 创建体质辨识专用的融合策略
//
export function createConstitutionIdentificationStrategy(): FusionStrategy {
  return {name: constitution_identification",;
    weights: {[ModalityType.TEXT]: 0.3,       // 问诊信息;
      [ModalityType.TONGUE]: 0.35,    // 舌象特征;
      [ModalityType.PULSE]: 0.35,     // 脉象特征;
      [ModalityType.AUDIO]: 0.0,[ModalityType.IMAGE]: 0.0;
    },
    method: "attention,",
    parameters: {,
  attention_type: "multi_head",
      heads: 4;
    }
  }
}
/**
* * 多模态RAG服务的配置选项
export interface MultimodalRAGConfig {
  // 编码器配置;
encoders?: {text?: Partial<EncoderConfig>;
    tongue?: Partial<EncoderConfig>;
    pulse?: Partial<EncoderConfig>;
};
  // 融合策略
defaultStrategy?: string;
  customStrategies?: FusionStrategy[];
  // 缓存配置
cacheSize?: number;
  cacheTTL?: number;
  // 检索配置
defaultTopK?: number;
  defaultThreshold?: number;
  // 性能配置
batchSize?: number;
  maxConcurrency?: number;
}
/**
* * 使用配置创建多模态RAG服务
//
* @param languageModel 语言模型实例
* @param config 配置选项
* @returns 配置好的多模态RAG服务
export async function createConfiguredMultimodalRAGService(;
  vectorDB: VectorDatabase,languageModel: LanguageModel,config: MultimodalRAGConfig = {}
): Promise<MultimodalRAGService> {
  const service = new MultimodalRAGService(vectorDB, languageModel);
  // 添加自定义策略
if (config.customStrategies) {
    for (const strategy of config.customStrategies) {
      service.addFusionStrategy(strategy);
    }
  }
  // 添加预定义的中医策略
service.addFusionStrategy(createTCMDiagnosisStrategy());
  service.addFusionStrategy(createSymptomAnalysisStrategy());
  service.addFusionStrategy(createConstitutionIdentificationStrategy());
  // 初始化服务
await service.initialize();
  return service;
}
/**
* * 多模态RAG的使用示例
export const examples = {/**
* ;
  * 基本文本查询示例;
  basicTextQuery: {text: 患者舌质红，苔薄黄，脉数，请分析病情",;
    strategy: "tcm_diagnosis_enhanced,";
    topK: 5,threshold: 0.7;
  } as MultimodalQuery,
  /**
* * 多模态综合查询示例
  multimodalQuery: {,
  text: "患者主诉头痛、失眠，请结合舌象和脉象进行诊断",
    tongueImage: base64_encoded_tongue_image",
    pulseSignal: [/* 脉象信号数组 ],
    strategy: "tcm_diagnosis_enhanced,",
    topK: 3,
    threshold: 0.8,
    metadata: {,
  patientAge: 45,
      gender: "female",
      consultationDate: 2024-01-15""
    } */
  } as MultimodalQuery, *///
*///
  /**
* * 体质辨识查询示例
  constitutionQuery: {,
  text: "患者平素怕冷，手足不温，大便溏薄,",
    strategy: "constitution_identification",
    topK: 5,
    threshold: 0.6;
  } as MultimodalQuery;
};
// 导出常用的模态类型常量
export const MODALITY_TYPES = {TEXT: ModalityType.TEXT,TONGUE: ModalityType.TONGUE,PULSE: ModalityType.PULSE,AUDIO: ModalityType.AUDIO,IMAGE: ModalityType.IMAGE;
} as const;
// 导出预定义的融合策略名称
export const FUSION_STRATEGIES = {TCM_DIAGNOSIS: tcm_diagnosis",;
  TCM_DIAGNOSIS_ENHANCED: "tcm_diagnosis_enhanced,",COMPREHENSIVE_DIAGNOSIS: "comprehensive_diagnosis",TEXT_DOMINANT: text_dominant",;
  SYMPTOM_ANALYSIS: "symptom_analysis,";
  CONSTITUTION_IDENTIFICATION: "constitution_identification';"'
} as const;
  */
