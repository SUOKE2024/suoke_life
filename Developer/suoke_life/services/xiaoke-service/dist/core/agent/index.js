"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.reloadAgentConfig = exports.setupAgentSystem = exports.getAgentCapabilities = exports.loadAgentConfig = void 0;
const fs_1 = __importDefault(require("fs"));
const path_1 = __importDefault(require("path"));
const logger_1 = require("../../utils/logger");
const models_1 = require("./models");
const tools_1 = require("./tools");
const memory_1 = require("./memory");
const scheduler_1 = require("./scheduler");
// 智能体配置缓存
let agentConfig = null;
/**
 * 加载智能体配置文件
 */
const loadAgentConfig = async () => {
    try {
        // 如果已经加载过配置，直接返回
        if (agentConfig) {
            return agentConfig;
        }
        // 获取配置路径
        const configPath = process.env.AGENT_CONFIG_PATH || path_1.default.join(__dirname, '../../../config/agent-config.json');
        // 检查文件是否存在
        if (!fs_1.default.existsSync(configPath)) {
            throw new Error(`智能体配置文件不存在: ${configPath}`);
        }
        // 读取并解析配置文件
        const configData = fs_1.default.readFileSync(configPath, 'utf8');
        agentConfig = JSON.parse(configData);
        logger_1.logger.info('已加载智能体配置', {
            agentName: agentConfig.agent.name,
            agentId: agentConfig.agent.id,
            version: agentConfig.agent.version
        });
        return agentConfig;
    }
    catch (error) {
        logger_1.logger.error('加载智能体配置失败:', error);
        throw error;
    }
};
exports.loadAgentConfig = loadAgentConfig;
/**
 * 获取智能体支持的能力
 */
const getAgentCapabilities = async () => {
    const config = await (0, exports.loadAgentConfig)();
    const capabilities = [];
    if (config.agent.capabilities) {
        for (const capability of config.agent.capabilities) {
            capabilities.push({
                name: capability,
                description: `支持${capability}功能`
            });
        }
    }
    return capabilities;
};
exports.getAgentCapabilities = getAgentCapabilities;
/**
 * 初始化智能体系统
 */
const setupAgentSystem = async () => {
    try {
        logger_1.logger.info('开始初始化智能体系统...');
        // 加载智能体配置
        const config = await (0, exports.loadAgentConfig)();
        // 初始化模型
        await (0, models_1.initializeAgentModels)(config);
        // 初始化工具
        await (0, tools_1.initializeAgentTools)(config);
        // 初始化记忆系统
        await (0, memory_1.initializeAgentMemory)(config);
        // 初始化任务调度器
        await (0, scheduler_1.initializeAgentScheduler)(config);
        logger_1.logger.info('智能体系统初始化完成');
    }
    catch (error) {
        logger_1.logger.error('智能体系统初始化失败:', error);
        throw error;
    }
};
exports.setupAgentSystem = setupAgentSystem;
/**
 * 重新加载智能体配置
 */
const reloadAgentConfig = async () => {
    // 清除配置缓存
    agentConfig = null;
    return (0, exports.loadAgentConfig)();
};
exports.reloadAgentConfig = reloadAgentConfig;
exports.default = {
    loadAgentConfig: exports.loadAgentConfig,
    getAgentCapabilities: exports.getAgentCapabilities,
    setupAgentSystem: exports.setupAgentSystem,
    reloadAgentConfig: exports.reloadAgentConfig
};
