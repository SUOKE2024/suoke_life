"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.releaseModels = exports.getModel = exports.initializeAgentModels = void 0;
const logger_1 = require("../../utils/logger");
const modelInstances = {};
/**
 * 初始化智能体模型
 * @param config 智能体配置
 */
const initializeAgentModels = async (config) => {
    try {
        logger_1.logger.info('初始化智能体模型...');
        if (!config.models) {
            logger_1.logger.warn('未配置智能体模型');
            return;
        }
        // 处理必需的模型
        if (config.models.primary) {
            await initializeModel('primary', config.models.primary);
        }
        if (config.models.embedding) {
            await initializeModel('embedding', config.models.embedding);
        }
        // 处理可选的模型
        if (config.models.product_analyzer) {
            await initializeModel('product_analyzer', config.models.product_analyzer);
        }
        if (config.models.traceability_analyzer) {
            await initializeModel('traceability_analyzer', config.models.traceability_analyzer);
        }
        if (config.models.multimodal_processor) {
            await initializeModel('multimodal_processor', config.models.multimodal_processor);
        }
        // 处理增强的多模态模型（如果存在）
        if (config.models.enhanced_multimodal) {
            if (config.models.enhanced_multimodal.vision_analyzer) {
                await initializeModel('vision_analyzer', config.models.enhanced_multimodal.vision_analyzer);
            }
            if (config.models.enhanced_multimodal.audio_analyzer) {
                await initializeModel('audio_analyzer', config.models.enhanced_multimodal.audio_analyzer);
            }
        }
        logger_1.logger.info('智能体模型初始化完成');
    }
    catch (error) {
        logger_1.logger.error('智能体模型初始化失败:', error);
        throw error;
    }
};
exports.initializeAgentModels = initializeAgentModels;
/**
 * 初始化单个模型
 * @param modelName 模型名称
 * @param modelConfig 模型配置
 */
const initializeModel = async (modelName, modelConfig) => {
    try {
        logger_1.logger.info(`初始化模型: ${modelName} (${modelConfig.type})`);
        // 基于模型类型初始化不同的模型
        switch (modelConfig.type) {
            case 'embedding':
                await initializeEmbeddingModel(modelName, modelConfig);
                break;
            case 'llm':
                await initializeLLMModel(modelName, modelConfig);
                break;
            case 'multimodal':
                await initializeMultimodalModel(modelName, modelConfig);
                break;
            default:
                logger_1.logger.warn(`未知的模型类型: ${modelConfig.type}`);
        }
    }
    catch (error) {
        logger_1.logger.error(`模型初始化失败: ${modelName}`, error);
        throw error;
    }
};
/**
 * 初始化嵌入模型
 */
const initializeEmbeddingModel = async (modelName, modelConfig) => {
    try {
        // 实现嵌入模型初始化逻辑
        logger_1.logger.info(`嵌入模型初始化成功: ${modelName}`);
        modelInstances[modelName] = {
            type: 'embedding',
            config: modelConfig,
            // 模型实例将在这里初始化
        };
    }
    catch (error) {
        logger_1.logger.error(`嵌入模型初始化失败: ${modelName}`, error);
        throw error;
    }
};
/**
 * 初始化LLM模型
 */
const initializeLLMModel = async (modelName, modelConfig) => {
    try {
        // 实现LLM模型初始化逻辑
        logger_1.logger.info(`LLM模型初始化成功: ${modelName}`);
        modelInstances[modelName] = {
            type: 'llm',
            config: modelConfig,
            // 模型实例将在这里初始化
        };
    }
    catch (error) {
        logger_1.logger.error(`LLM模型初始化失败: ${modelName}`, error);
        throw error;
    }
};
/**
 * 初始化多模态模型
 */
const initializeMultimodalModel = async (modelName, modelConfig) => {
    try {
        // 实现多模态模型初始化逻辑
        logger_1.logger.info(`多模态模型初始化成功: ${modelName}`);
        modelInstances[modelName] = {
            type: 'multimodal',
            config: modelConfig,
            // 模型实例将在这里初始化
        };
    }
    catch (error) {
        logger_1.logger.error(`多模态模型初始化失败: ${modelName}`, error);
        throw error;
    }
};
/**
 * 获取模型实例
 * @param modelName 模型名称
 */
const getModel = (modelName) => {
    if (!modelInstances[modelName]) {
        throw new Error(`模型未初始化: ${modelName}`);
    }
    return modelInstances[modelName];
};
exports.getModel = getModel;
/**
 * 释放模型资源
 */
const releaseModels = async () => {
    try {
        logger_1.logger.info('释放模型资源...');
        for (const modelName in modelInstances) {
            logger_1.logger.info(`释放模型: ${modelName}`);
            // 在此处添加释放模型资源的逻辑
            delete modelInstances[modelName];
        }
        logger_1.logger.info('所有模型资源已释放');
    }
    catch (error) {
        logger_1.logger.error('释放模型资源失败:', error);
    }
};
exports.releaseModels = releaseModels;
