/**
 * 知识服务控制器
 */
import { Request, Response } from 'express';
import { Logger } from '../../utils/logger';
import {
  KnowledgeBaseService,
  KnowledgeGraphService,
  KnowledgeIntegrationService,
  KnowledgeSearchOptions
} from '../../services/knowledge';

/**
 * 知识控制器
 */
export class KnowledgeController {
  private logger = new Logger('KnowledgeController');
  private knowledgeBaseService: KnowledgeBaseService;
  private knowledgeGraphService: KnowledgeGraphService;
  private knowledgeIntegrationService: KnowledgeIntegrationService;

  constructor(
    knowledgeBaseService: KnowledgeBaseService,
    knowledgeGraphService: KnowledgeGraphService,
    knowledgeIntegrationService: KnowledgeIntegrationService
  ) {
    this.knowledgeBaseService = knowledgeBaseService;
    this.knowledgeGraphService = knowledgeGraphService;
    this.knowledgeIntegrationService = knowledgeIntegrationService;
  }

  /**
   * 搜索知识库
   */
  public searchKnowledge = async (req: Request, res: Response): Promise<void> => {
    try {
      const { query } = req.body;
      const options: KnowledgeSearchOptions = req.body.options || {};

      if (!query) {
        res.status(400).json({ error: '查询内容不能为空' });
        return;
      }

      const result = await this.knowledgeBaseService.search(query, options);
      res.json(result);
    } catch (error) {
      this.logger.error('搜索知识库失败', error);
      res.status(500).json({ error: (error as Error).message });
    }
  };

  /**
   * 获取知识条目
   */
  public getKnowledgeItem = async (req: Request, res: Response): Promise<void> => {
    try {
      const { id } = req.params;

      if (!id) {
        res.status(400).json({ error: '知识条目ID不能为空' });
        return;
      }

      const item = await this.knowledgeBaseService.getItem(id);
      res.json(item);
    } catch (error) {
      this.logger.error(`获取知识条目失败: ${req.params.id}`, error);
      res.status(500).json({ error: (error as Error).message });
    }
  };

  /**
   * 根据分类获取知识条目
   */
  public getKnowledgeByCategory = async (req: Request, res: Response): Promise<void> => {
    try {
      const { category } = req.params;
      const limit = parseInt(req.query.limit as string) || 20;

      if (!category) {
        res.status(400).json({ error: '分类名称不能为空' });
        return;
      }

      const items = await this.knowledgeBaseService.getItemsByCategory(category, limit);
      res.json(items);
    } catch (error) {
      this.logger.error(`获取分类知识失败: ${req.params.category}`, error);
      res.status(500).json({ error: (error as Error).message });
    }
  };

  /**
   * 根据标签获取知识条目
   */
  public getKnowledgeByTag = async (req: Request, res: Response): Promise<void> => {
    try {
      const { tag } = req.params;
      const limit = parseInt(req.query.limit as string) || 20;

      if (!tag) {
        res.status(400).json({ error: '标签名称不能为空' });
        return;
      }

      const items = await this.knowledgeBaseService.getItemsByTag(tag, limit);
      res.json(items);
    } catch (error) {
      this.logger.error(`获取标签知识失败: ${req.params.tag}`, error);
      res.status(500).json({ error: (error as Error).message });
    }
  };

  /**
   * 搜索图谱节点
   */
  public searchGraphNodes = async (req: Request, res: Response): Promise<void> => {
    try {
      const { query } = req.query;

      if (!query) {
        res.status(400).json({ error: '查询内容不能为空' });
        return;
      }

      const nodes = await this.knowledgeGraphService.searchNodes(query as string);
      res.json(nodes);
    } catch (error) {
      this.logger.error(`搜索图谱节点失败: ${req.query.query}`, error);
      res.status(500).json({ error: (error as Error).message });
    }
  };

  /**
   * 获取节点关系
   */
  public getNodeRelations = async (req: Request, res: Response): Promise<void> => {
    try {
      const { nodeId } = req.params;

      if (!nodeId) {
        res.status(400).json({ error: '节点ID不能为空' });
        return;
      }

      const relations = await this.knowledgeGraphService.getNodeRelations(nodeId);
      res.json(relations);
    } catch (error) {
      this.logger.error(`获取节点关系失败: ${req.params.nodeId}`, error);
      res.status(500).json({ error: (error as Error).message });
    }
  };

  /**
   * 查找最短路径
   */
  public findShortestPath = async (req: Request, res: Response): Promise<void> => {
    try {
      const { fromId, toId } = req.query;

      if (!fromId || !toId) {
        res.status(400).json({ error: '起始节点ID和目标节点ID不能为空' });
        return;
      }

      const path = await this.knowledgeGraphService.findShortestPath(
        fromId as string,
        toId as string
      );
      res.json(path);
    } catch (error) {
      this.logger.error(`查找最短路径失败: ${req.query.fromId} -> ${req.query.toId}`, error);
      res.status(500).json({ error: (error as Error).message });
    }
  };

  /**
   * 产品知识增强
   */
  public enrichProductKnowledge = async (req: Request, res: Response): Promise<void> => {
    try {
      const { productId } = req.params;

      if (!productId) {
        res.status(400).json({ error: '产品ID不能为空' });
        return;
      }

      const enrichment = await this.knowledgeIntegrationService.enrichProductKnowledge(productId);
      res.json(enrichment);
    } catch (error) {
      this.logger.error(`产品知识增强失败: ${req.params.productId}`, error);
      res.status(500).json({ error: (error as Error).message });
    }
  };

  /**
   * 搜索农产品与健康知识的关联
   */
  public searchAgricultureHealthKnowledge = async (req: Request, res: Response): Promise<void> => {
    try {
      const { query } = req.body;
      const options: KnowledgeSearchOptions = req.body.options || {};

      if (!query) {
        res.status(400).json({ error: '查询内容不能为空' });
        return;
      }

      const result = await this.knowledgeIntegrationService.searchAgricultureHealthKnowledge(
        query,
        options
      );
      res.json(result);
    } catch (error) {
      this.logger.error('搜索农产品健康知识失败', error);
      res.status(500).json({ error: (error as Error).message });
    }
  };

  /**
   * 获取产品相关健康知识
   */
  public getProductHealthKnowledge = async (req: Request, res: Response): Promise<void> => {
    try {
      const { productId } = req.params;

      if (!productId) {
        res.status(400).json({ error: '产品ID不能为空' });
        return;
      }

      const items = await this.knowledgeIntegrationService.getProductHealthKnowledge(productId);
      res.json(items);
    } catch (error) {
      this.logger.error(`获取产品健康知识失败: ${req.params.productId}`, error);
      res.status(500).json({ error: (error as Error).message });
    }
  };

  /**
   * 获取节气相关农产品知识
   */
  public getSolarTermAgricultureKnowledge = async (req: Request, res: Response): Promise<void> => {
    try {
      const { solarTerm } = req.params;

      if (!solarTerm) {
        res.status(400).json({ error: '节气名称不能为空' });
        return;
      }

      const result = await this.knowledgeIntegrationService.getSolarTermAgricultureKnowledge(
        solarTerm
      );
      res.json(result);
    } catch (error) {
      this.logger.error(`获取节气农产品知识失败: ${req.params.solarTerm}`, error);
      res.status(500).json({ error: (error as Error).message });
    }
  };

  /**
   * 服务健康检查
   */
  public healthCheck = async (_req: Request, res: Response): Promise<void> => {
    res.json({ status: 'ok', message: '知识服务正常运行' });
  };
}