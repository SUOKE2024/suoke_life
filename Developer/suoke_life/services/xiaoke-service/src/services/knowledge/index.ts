/**
 * 知识服务模块入口
 */
import { 
  KnowledgeBaseService,
  KnowledgeGraphService,
  KnowledgeIntegrationService
} from './types';
import { KnowledgeBaseServiceImpl } from './knowledge-base.service';
import { KnowledgeGraphServiceImpl } from './knowledge-graph.service';
import { KnowledgeIntegrationServiceImpl } from './knowledge-integration.service';

/**
 * 创建知识库服务
 */
export function createKnowledgeBaseService(): KnowledgeBaseService {
  return new KnowledgeBaseServiceImpl();
}

/**
 * 创建知识图谱服务
 */
export function createKnowledgeGraphService(): KnowledgeGraphService {
  return new KnowledgeGraphServiceImpl();
}

/**
 * 创建知识整合服务
 */
export function createKnowledgeIntegrationService(
  knowledgeBaseService: KnowledgeBaseService,
  knowledgeGraphService: KnowledgeGraphService
): KnowledgeIntegrationService {
  return new KnowledgeIntegrationServiceImpl(
    knowledgeBaseService,
    knowledgeGraphService
  );
}

/**
 * 知识服务初始化
 */
export async function initializeKnowledgeServices(): Promise<{
  knowledgeBaseService: KnowledgeBaseService;
  knowledgeGraphService: KnowledgeGraphService;
  knowledgeIntegrationService: KnowledgeIntegrationService;
}> {
  // 创建服务实例
  const knowledgeBaseService = createKnowledgeBaseService();
  const knowledgeGraphService = createKnowledgeGraphService();
  
  // 初始化基础服务
  await Promise.all([
    knowledgeBaseService.initialize(),
    knowledgeGraphService.initialize()
  ]);
  
  // 创建并初始化整合服务
  const knowledgeIntegrationService = createKnowledgeIntegrationService(
    knowledgeBaseService,
    knowledgeGraphService
  );
  
  await knowledgeIntegrationService.initialize();
  
  return {
    knowledgeBaseService,
    knowledgeGraphService,
    knowledgeIntegrationService
  };
}

// 导出类型和服务
export * from './types';
export { KnowledgeBaseServiceImpl } from './knowledge-base.service';
export { KnowledgeGraphServiceImpl } from './knowledge-graph.service';
export { KnowledgeIntegrationServiceImpl } from './knowledge-integration.service';