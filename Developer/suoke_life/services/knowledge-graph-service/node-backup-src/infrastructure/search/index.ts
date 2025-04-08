import { FullTextIndexManager } from './FullTextIndexManager';
import { IndexUpdateManager } from './IndexUpdateManager';
import { IndexOptimizationManager } from './IndexOptimizationManager';

export type { 
  IndexConfig,
  IndexStats 
} from './FullTextIndexManager';

export type {
  IndexUpdateConfig,
  UpdateStats
} from './IndexUpdateManager';

export type {
  OptimizationStrategy,
  OptimizationResult
} from './IndexOptimizationManager';

// 导出主要类
export {
  FullTextIndexManager,
  IndexUpdateManager,
  IndexOptimizationManager
};

// 导出工厂函数
export const getFullTextIndexManager = () => FullTextIndexManager.getInstance();
export const getIndexUpdateManager = () => IndexUpdateManager.getInstance();
export const getIndexOptimizationManager = () => IndexOptimizationManager.getInstance();

// 导出常用的工具函数
export const initializeSearchSystem = async () => {
  const indexManager = getFullTextIndexManager();
  const updateManager = getIndexUpdateManager();
  const optimizationManager = getIndexOptimizationManager();

  try {
    // 确保索引存在
    await indexManager.createIndex();
    
    // 初始化优化策略
    await optimizationManager.optimize();
    
    return {
      indexManager,
      updateManager,
      optimizationManager
    };
  } catch (error) {
    throw new Error(`初始化搜索系统失败: ${error.message}`);
  }
};

// 导出常用的组合操作
export const refreshAndOptimizeIndex = async () => {
  const indexManager = getFullTextIndexManager();
  const optimizationManager = getIndexOptimizationManager();

  await indexManager.rebuildIndex();
  return optimizationManager.optimize();
};

export const updateAndValidateNodes = async (nodeIds: string[]) => {
  const updateManager = getIndexUpdateManager();
  
  await updateManager.queueForUpdate(nodeIds);
  return updateManager.validateUpdates(nodeIds);
};