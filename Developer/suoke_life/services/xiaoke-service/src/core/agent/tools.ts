import { logger } from '../../utils/logger';
import { AgentConfig, ToolConfig, ToolCallResult } from './types';

/**
 * 工具实例缓存
 */
interface ToolCache {
  [key: string]: any;
}

const toolInstances: ToolCache = {};

/**
 * 初始化智能体工具
 * @param config 智能体配置
 */
export const initializeAgentTools = async (config: AgentConfig): Promise<void> => {
  try {
    logger.info('初始化智能体工具...');
    
    if (!config.tools || !config.tools.enabled) {
      logger.info('智能体工具已禁用');
      return;
    }
    
    if (!config.tools.list || config.tools.list.length === 0) {
      logger.warn('未配置智能体工具');
      return;
    }
    
    for (const tool of config.tools.list) {
      await registerTool(tool);
    }
    
    logger.info(`已初始化 ${Object.keys(toolInstances).length} 个工具`);
  } catch (error) {
    logger.error('智能体工具初始化失败:', error);
    throw error;
  }
};

/**
 * 注册工具
 * @param toolConfig 工具配置
 */
const registerTool = async (toolConfig: ToolConfig): Promise<void> => {
  try {
    logger.info(`注册工具: ${toolConfig.name}`);
    
    // 根据工具名称动态加载工具实现
    let toolImplementation;
    
    try {
      toolImplementation = await import(`../../services/tools/${toolConfig.name}`);
    } catch (importError) {
      logger.error(`无法加载工具实现: ${toolConfig.name}`, importError);
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
    
    logger.info(`工具注册成功: ${toolConfig.name}`);
  } catch (error) {
    logger.error(`工具注册失败: ${toolConfig.name}`, error);
    throw error;
  }
};

/**
 * 执行工具调用
 * @param toolName 工具名称
 * @param params 工具参数
 */
export const executeTool = async (toolName: string, params: any): Promise<ToolCallResult> => {
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
    logger.info(`执行工具: ${toolName}`, { params });
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
  } catch (error) {
    logger.error(`工具执行失败: ${toolName}`, error);
    
    return {
      success: false,
      error: error instanceof Error ? error.message : '未知错误',
      toolName,
      executionTime: Date.now() - startTime
    };
  }
};

/**
 * 获取可用工具列表
 */
export const getAvailableTools = (): string[] => {
  return Object.keys(toolInstances);
};

/**
 * 获取工具配置
 * @param toolName 工具名称
 */
export const getToolConfig = (toolName: string): ToolConfig | null => {
  if (!toolInstances[toolName]) {
    return null;
  }
  
  return toolInstances[toolName].config;
};

/**
 * 释放工具资源
 */
export const releaseTools = async (): Promise<void> => {
  try {
    logger.info('释放工具资源...');
    
    for (const toolName in toolInstances) {
      logger.info(`释放工具: ${toolName}`);
      
      // 如果工具有释放方法，调用它
      if (toolInstances[toolName].release && typeof toolInstances[toolName].release === 'function') {
        await toolInstances[toolName].release();
      }
      
      delete toolInstances[toolName];
    }
    
    logger.info('所有工具资源已释放');
  } catch (error) {
    logger.error('释放工具资源失败:', error);
  }
}; 