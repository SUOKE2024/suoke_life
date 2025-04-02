import fs from 'fs';
import path from 'path';
import { logger } from '../../utils/logger';
import { AgentConfig, AgentCapability } from './types';
import { initializeAgentModels } from './models';
import { initializeAgentTools } from './tools';
import { initializeAgentMemory } from './memory';
import { initializeAgentScheduler } from './scheduler';

// 智能体配置缓存
let agentConfig: AgentConfig | null = null;

/**
 * 加载智能体配置文件
 */
export const loadAgentConfig = async (): Promise<AgentConfig> => {
  try {
    // 如果已经加载过配置，直接返回
    if (agentConfig) {
      return agentConfig;
    }

    // 获取配置路径
    const configPath = process.env.AGENT_CONFIG_PATH || path.join(__dirname, '../../../config/agent-config.json');
    
    // 检查文件是否存在
    if (!fs.existsSync(configPath)) {
      throw new Error(`智能体配置文件不存在: ${configPath}`);
    }
    
    // 读取并解析配置文件
    const configData = fs.readFileSync(configPath, 'utf8');
    agentConfig = JSON.parse(configData);
    
    logger.info('已加载智能体配置', {
      agentName: agentConfig.agent.name,
      agentId: agentConfig.agent.id,
      version: agentConfig.agent.version
    });
    
    return agentConfig;
  } catch (error) {
    logger.error('加载智能体配置失败:', error);
    throw error;
  }
};

/**
 * 获取智能体支持的能力
 */
export const getAgentCapabilities = async (): Promise<AgentCapability[]> => {
  const config = await loadAgentConfig();
  const capabilities: AgentCapability[] = [];
  
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

/**
 * 初始化智能体系统
 */
export const setupAgentSystem = async (): Promise<void> => {
  try {
    logger.info('开始初始化智能体系统...');
    
    // 加载智能体配置
    const config = await loadAgentConfig();
    
    // 初始化模型
    await initializeAgentModels(config);
    
    // 初始化工具
    await initializeAgentTools(config);
    
    // 初始化记忆系统
    await initializeAgentMemory(config);
    
    // 初始化任务调度器
    await initializeAgentScheduler(config);
    
    logger.info('智能体系统初始化完成');
  } catch (error) {
    logger.error('智能体系统初始化失败:', error);
    throw error;
  }
};

/**
 * 重新加载智能体配置
 */
export const reloadAgentConfig = async (): Promise<AgentConfig> => {
  // 清除配置缓存
  agentConfig = null;
  return loadAgentConfig();
};

export default {
  loadAgentConfig,
  getAgentCapabilities,
  setupAgentSystem,
  reloadAgentConfig
}; 