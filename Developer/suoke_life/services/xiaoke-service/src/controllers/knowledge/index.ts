/**
 * 知识控制器模块
 */
import { 
  KnowledgeBaseService, 
  KnowledgeGraphService, 
  KnowledgeIntegrationService 
} from '../../services/knowledge';
import { KnowledgeController } from './knowledge.controller';

/**
 * 创建知识控制器
 */
export function createKnowledgeController(
  knowledgeBaseService: KnowledgeBaseService,
  knowledgeGraphService: KnowledgeGraphService,
  knowledgeIntegrationService: KnowledgeIntegrationService
): KnowledgeController {
  return new KnowledgeController(
    knowledgeBaseService,
    knowledgeGraphService,
    knowledgeIntegrationService
  );
}

// 导出控制器类
export { KnowledgeController } from './knowledge.controller';