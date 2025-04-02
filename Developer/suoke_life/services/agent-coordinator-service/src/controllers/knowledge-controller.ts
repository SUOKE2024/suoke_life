/**
 * 知识查询控制器
 */
import { Request, Response } from 'express';
import { KnowledgeService } from '../services/knowledge-service';
import { domainClassifier } from '../utils/domain-classifier';
import logger from '../utils/logger';

export class KnowledgeController {
  private knowledgeService: KnowledgeService;

  constructor() {
    this.knowledgeService = new KnowledgeService();
  }

  /**
   * 基础知识库搜索
   */
  async searchKnowledge(req: Request, res: Response): Promise<void> {
    try {
      const { 
        query, 
        domains, 
        types, 
        page = 1, 
        limit = 10,
        semanticSearch = false,
        hybridSearch = false,
        minConfidence = 0.6
      } = req.query;

      if (!query) {
        res.status(400).json({ error: '搜索查询不能为空' });
        return;
      }

      // 域名分类
      const domainClassifications = domainClassifier.classifyQuery(query as string);
      
      // 将字符串类型的过滤条件转换为数组
      const domainFilter = domains ? (domains as string).split(',') : undefined;
      const typeFilter = types ? (types as string).split(',') : undefined;

      const results = await this.knowledgeService.searchKnowledge({
        query: query as string,
        domainFilter,
        typeFilter,
        page: Number(page),
        limit: Number(limit),
        userId: req.body.userId || req.query.userId as string,
        semanticSearch: semanticSearch === 'true',
        hybridSearch: hybridSearch === 'true',
        minConfidence: Number(minConfidence)
      });

      res.json({
        results,
        meta: {
          page: Number(page),
          limit: Number(limit),
          domainClassifications
        }
      });
    } catch (error) {
      logger.error('知识搜索失败', { error });
      res.status(500).json({
        error: '知识搜索失败',
        message: error.message
      });
    }
  }

  /**
   * 知识图谱查询
   */
  async queryKnowledgeGraph(req: Request, res: Response): Promise<void> {
    try {
      const { 
        query, 
        nodeTypes, 
        relationTypes, 
        maxDepth = 2, 
        limit = 50 
      } = req.query;

      if (!query) {
        res.status(400).json({ error: '图谱查询不能为空' });
        return;
      }

      // 将字符串类型的过滤条件转换为数组
      const nodeTypesArray = nodeTypes ? (nodeTypes as string).split(',') : undefined;
      const relationTypesArray = relationTypes ? (relationTypes as string).split(',') : undefined;

      const results = await this.knowledgeService.queryKnowledgeGraph({
        query: query as string,
        nodeTypes: nodeTypesArray,
        relationTypes: relationTypesArray,
        maxDepth: Number(maxDepth),
        limit: Number(limit),
        userId: req.body.userId || req.query.userId as string
      });

      res.json(results);
    } catch (error) {
      logger.error('知识图谱查询失败', { error });
      res.status(500).json({
        error: '知识图谱查询失败',
        message: error.message
      });
    }
  }

  /**
   * RAG服务查询
   */
  async generateRAGResponse(req: Request, res: Response): Promise<void> {
    try {
      const { query, domainFilters, typeFilters, useSpecialized = true } = req.body;

      if (!query) {
        res.status(400).json({ error: 'RAG查询不能为空' });
        return;
      }

      const userId = req.body.userId || req.query.userId as string;
      const sessionId = req.body.sessionId || req.query.sessionId as string;

      const result = await this.knowledgeService.generateRAGResponse(query, {
        userId,
        sessionId,
        domainFilters,
        typeFilters,
        useSpecialized
      });

      res.json(result);
    } catch (error) {
      logger.error('RAG响应生成失败', { error });
      res.status(500).json({
        error: 'RAG响应生成失败',
        message: error.message
      });
    }
  }

  /**
   * 精准医学知识查询
   */
  async queryPrecisionMedicine(req: Request, res: Response): Promise<void> {
    try {
      const { 
        query, 
        genomeFeatures, 
        healthRisks, 
        diseaseTypes, 
        page = 1, 
        limit = 10 
      } = req.query;

      if (!query) {
        res.status(400).json({ error: '查询不能为空' });
        return;
      }

      // 将字符串类型的过滤条件转换为数组
      const genomeFeaturesArray = genomeFeatures ? (genomeFeatures as string).split(',') : undefined;
      const healthRisksArray = healthRisks ? (healthRisks as string).split(',') : undefined;
      const diseaseTypesArray = diseaseTypes ? (diseaseTypes as string).split(',') : undefined;

      const results = await this.knowledgeService.queryPrecisionMedicine({
        query: query as string,
        genomeFeatures: genomeFeaturesArray,
        healthRisks: healthRisksArray,
        diseaseTypes: diseaseTypesArray,
        page: Number(page),
        limit: Number(limit)
      });

      res.json({
        results,
        meta: {
          page: Number(page),
          limit: Number(limit)
        }
      });
    } catch (error) {
      logger.error('精准医学知识查询失败', { error });
      res.status(500).json({
        error: '精准医学知识查询失败',
        message: error.message
      });
    }
  }

  /**
   * 多模态健康数据查询
   */
  async queryMultimodalHealth(req: Request, res: Response): Promise<void> {
    try {
      const { 
        query, 
        dataTypes, 
        sources, 
        page = 1, 
        limit = 10 
      } = req.query;

      if (!query) {
        res.status(400).json({ error: '查询不能为空' });
        return;
      }

      // 将字符串类型的过滤条件转换为数组
      const dataTypesArray = dataTypes ? (dataTypes as string).split(',') as ('image' | 'audio' | 'text' | 'biosignal')[] : undefined;
      const sourcesArray = sources ? (sources as string).split(',') : undefined;

      const results = await this.knowledgeService.queryMultimodalHealth({
        query: query as string,
        dataTypes: dataTypesArray,
        sources: sourcesArray,
        page: Number(page),
        limit: Number(limit)
      });

      res.json({
        results,
        meta: {
          page: Number(page),
          limit: Number(limit)
        }
      });
    } catch (error) {
      logger.error('多模态健康数据查询失败', { error });
      res.status(500).json({
        error: '多模态健康数据查询失败',
        message: error.message
      });
    }
  }

  /**
   * 环境健康数据查询
   */
  async queryEnvironmentalHealth(req: Request, res: Response): Promise<void> {
    try {
      const { 
        query, 
        factors, 
        locations, 
        startTime, 
        endTime, 
        page = 1, 
        limit = 10 
      } = req.query;

      if (!query) {
        res.status(400).json({ error: '查询不能为空' });
        return;
      }

      // 将字符串类型的过滤条件转换为数组
      const factorsArray = factors ? (factors as string).split(',') : undefined;
      const locationsArray = locations ? (locations as string).split(',') : undefined;
      
      // 构建时间范围对象
      const timeRange = (startTime || endTime) ? {
        start: startTime as string,
        end: endTime as string
      } : undefined;

      const results = await this.knowledgeService.queryEnvironmentalHealth({
        query: query as string,
        environmentalFactors: factorsArray,
        locations: locationsArray,
        timeRange,
        page: Number(page),
        limit: Number(limit)
      });

      res.json({
        results,
        meta: {
          page: Number(page),
          limit: Number(limit)
        }
      });
    } catch (error) {
      logger.error('环境健康数据查询失败', { error });
      res.status(500).json({
        error: '环境健康数据查询失败',
        message: error.message
      });
    }
  }

  /**
   * 心理健康数据查询
   */
  async queryMentalHealth(req: Request, res: Response): Promise<void> {
    try {
      const { 
        query, 
        aspects, 
        therapies, 
        conditions, 
        page = 1, 
        limit = 10 
      } = req.query;

      if (!query) {
        res.status(400).json({ error: '查询不能为空' });
        return;
      }

      // 将字符串类型的过滤条件转换为数组
      const aspectsArray = aspects ? (aspects as string).split(',') : undefined;
      const therapiesArray = therapies ? (therapies as string).split(',') : undefined;
      const conditionsArray = conditions ? (conditions as string).split(',') : undefined;

      const results = await this.knowledgeService.queryMentalHealth({
        query: query as string,
        mentalHealthAspects: aspectsArray,
        therapyTypes: therapiesArray,
        conditions: conditionsArray,
        page: Number(page),
        limit: Number(limit)
      });

      res.json({
        results,
        meta: {
          page: Number(page),
          limit: Number(limit)
        }
      });
    } catch (error) {
      logger.error('心理健康数据查询失败', { error });
      res.status(500).json({
        error: '心理健康数据查询失败',
        message: error.message
      });
    }
  }
}