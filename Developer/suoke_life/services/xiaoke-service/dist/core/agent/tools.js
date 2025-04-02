"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.releaseTools = exports.getToolConfig = exports.getAvailableTools = exports.executeTool = exports.initializeAgentTools = void 0;
const logger_1 = require("../../utils/logger");
const toolInstances = {};
/**
 * 初始化智能体工具
 * @param config 智能体配置
 */
const initializeAgentTools = async (config) => {
    try {
        logger_1.logger.info('初始化智能体工具...');
        if (!config.tools || !config.tools.enabled) {
            logger_1.logger.info('智能体工具已禁用');
            return;
        }
        if (!config.tools.list || config.tools.list.length === 0) {
            logger_1.logger.warn('未配置智能体工具');
            return;
        }
        for (const tool of config.tools.list) {
            await registerTool(tool);
        }
        logger_1.logger.info(`已初始化 ${Object.keys(toolInstances).length} 个工具`);
    }
    catch (error) {
        logger_1.logger.error('智能体工具初始化失败:', error);
        throw error;
    }
};
exports.initializeAgentTools = initializeAgentTools;
/**
 * 注册工具
 * @param toolConfig 工具配置
 */
const registerTool = async (toolConfig) => {
    try {
        logger_1.logger.info(`注册工具: ${toolConfig.name}`);
        // 根据工具名称动态加载工具实现
        let toolImplementation;
        try {
            toolImplementation = await Promise.resolve(`${`../../services/tools/${toolConfig.name}`}`).then(s => __importStar(require(s)));
        }
        catch (importError) {
            logger_1.logger.error(`无法加载工具实现: ${toolConfig.name}`, importError);
            throw new Error(`工具实现不存在: ${toolConfig.name}`);
        }
        // 校验工具实现
        if (!toolImplementation.execute || typeof toolImplementation.execute !== 'function') {
            throw new Error(`工具 ${toolConfig.name} 缺少 execute 方法`);
        }
        // 注册工具
        toolInstances[toolConfig.name] = {
            config: toolConfig,
            execute: toolImplementation.execute
        };
        logger_1.logger.info(`工具注册成功: ${toolConfig.name}`);
    }
    catch (error) {
        logger_1.logger.error(`工具注册失败: ${toolConfig.name}`, error);
        throw error;
    }
};
/**
 * 执行工具调用
 * @param toolName 工具名称
 * @param params 工具参数
 */
const executeTool = async (toolName, params) => {
    const startTime = Date.now();
    try {
        // 检查工具是否存在
        if (!toolInstances[toolName]) {
            return {
                success: false,
                error: `工具不存在: ${toolName}`,
                toolName,
                executionTime: Date.now() - startTime
            };
        }
        // 获取工具实例
        const tool = toolInstances[toolName];
        // 执行工具
        logger_1.logger.info(`执行工具: ${toolName}`, { params });
        const result = await tool.execute(params);
        // 计算执行时间
        const executionTime = Date.now() - startTime;
        // 构建返回结果
        return {
            success: true,
            data: result,
            toolName,
            executionTime
        };
    }
    catch (error) {
        logger_1.logger.error(`工具执行失败: ${toolName}`, error);
        return {
            success: false,
            error: error instanceof Error ? error.message : '未知错误',
            toolName,
            executionTime: Date.now() - startTime
        };
    }
};
exports.executeTool = executeTool;
/**
 * 获取可用工具列表
 */
const getAvailableTools = () => {
    return Object.keys(toolInstances);
};
exports.getAvailableTools = getAvailableTools;
/**
 * 获取工具配置
 * @param toolName 工具名称
 */
const getToolConfig = (toolName) => {
    if (!toolInstances[toolName]) {
        return null;
    }
    return toolInstances[toolName].config;
};
exports.getToolConfig = getToolConfig;
/**
 * 释放工具资源
 */
const releaseTools = async () => {
    try {
        logger_1.logger.info('释放工具资源...');
        for (const toolName in toolInstances) {
            logger_1.logger.info(`释放工具: ${toolName}`);
            // 如果工具有释放方法，调用它
            if (toolInstances[toolName].release && typeof toolInstances[toolName].release === 'function') {
                await toolInstances[toolName].release();
            }
            delete toolInstances[toolName];
        }
        logger_1.logger.info('所有工具资源已释放');
    }
    catch (error) {
        logger_1.logger.error('释放工具资源失败:', error);
    }
};
exports.releaseTools = releaseTools;
