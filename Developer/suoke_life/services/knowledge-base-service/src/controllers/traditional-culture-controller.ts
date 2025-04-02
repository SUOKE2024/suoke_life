/**
 * 传统文化知识控制器
 * 处理传统文化知识相关的请求
 */

import { Request, Response, NextFunction } from 'express';
import { TraditionalCultureKnowledgeService } from '../services/traditional-culture-knowledge.service';
import { ApiError } from '../utils/api-error';
import { logger } from '../utils/logger';

export class TraditionalCultureController {
  private traditionalCultureService: TraditionalCultureKnowledgeService;

  constructor() {
    this.traditionalCultureService = new TraditionalCultureKnowledgeService();
  }

  /**
   * 获取传统文化知识列表
   */
  async getTraditionalCultureKnowledgeList(req: Request, res: Response, next: NextFunction) {
    try {
      const { 
        page = '1', 
        limit = '20', 
        category,
        culturalSystem,
        historicalPeriod,
        sort = 'createdAt',
        order = 'desc',
        search
      } = req.query;

      const filter: any = {};
      
      if (category) {
        filter.categories = { $in: [category] };
      }
      
      if (culturalSystem) {
        filter.culturalSystem = culturalSystem;
      }
      
      if (historicalPeriod) {
        filter.historicalPeriod = historicalPeriod;
      }
      
      if (search) {
        filter.$or = [
          { title: { $regex: search, $options: 'i' } },
          { content: { $regex: search, $options: 'i' } },
          { summary: { $regex: search, $options: 'i' } }
        ];
      }

      const result = await this.traditionalCultureService.listTraditionalCultureKnowledge(
        parseInt(page as string, 10),
        parseInt(limit as string, 10),
        filter,
        { [sort as string]: order === 'desc' ? -1 : 1 }
      );

      res.status(200).json(result);
    } catch (error) {
      logger.error('获取传统文化知识列表失败', error);
      next(error);
    }
  }

  /**
   * 获取传统文化知识详情
   */
  async getTraditionalCultureKnowledgeById(req: Request, res: Response, next: NextFunction) {
    try {
      const { id } = req.params;
      const knowledge = await this.traditionalCultureService.getTraditionalCultureKnowledgeById(id);
      
      if (!knowledge) {
        throw new ApiError(404, '传统文化知识不存在');
      }
      
      res.status(200).json(knowledge);
    } catch (error) {
      logger.error(`获取传统文化知识详情失败, ID: ${req.params.id}`, error);
      next(error);
    }
  }

  /**
   * 创建传统文化知识
   */
  async createTraditionalCultureKnowledge(req: Request, res: Response, next: NextFunction) {
    try {
      const knowledgeData = req.body;
      
      // 添加创建者信息
      if (req.user) {
        knowledgeData.createdBy = req.user.id;
      }
      
      const createdKnowledge = await this.traditionalCultureService.createTraditionalCultureKnowledge(knowledgeData);
      
      res.status(201).json(createdKnowledge);
    } catch (error) {
      logger.error('创建传统文化知识失败', error);
      next(error);
    }
  }

  /**
   * 更新传统文化知识
   */
  async updateTraditionalCultureKnowledge(req: Request, res: Response, next: NextFunction) {
    try {
      const { id } = req.params;
      const knowledgeData = req.body;
      
      // 添加更新者信息
      if (req.user) {
        knowledgeData.updatedBy = req.user.id;
      }
      
      const updatedKnowledge = await this.traditionalCultureService.updateTraditionalCultureKnowledge(id, knowledgeData);
      
      if (!updatedKnowledge) {
        throw new ApiError(404, '传统文化知识不存在');
      }
      
      res.status(200).json(updatedKnowledge);
    } catch (error) {
      logger.error(`更新传统文化知识失败, ID: ${req.params.id}`, error);
      next(error);
    }
  }

  /**
   * 删除传统文化知识
   */
  async deleteTraditionalCultureKnowledge(req: Request, res: Response, next: NextFunction) {
    try {
      const { id } = req.params;
      const result = await this.traditionalCultureService.deleteTraditionalCultureKnowledge(id);
      
      if (!result) {
        throw new ApiError(404, '传统文化知识不存在');
      }
      
      res.status(200).json({ message: '传统文化知识删除成功' });
    } catch (error) {
      logger.error(`删除传统文化知识失败, ID: ${req.params.id}`, error);
      next(error);
    }
  }

  /**
   * 根据文化体系获取知识
   */
  async getKnowledgeByCulturalSystem(req: Request, res: Response, next: NextFunction) {
    try {
      const { culturalSystem } = req.params;
      const { page = '1', limit = '20' } = req.query;
      
      const result = await this.traditionalCultureService.getKnowledgeByCulturalSystem(
        culturalSystem,
        parseInt(page as string, 10),
        parseInt(limit as string, 10)
      );
      
      res.status(200).json(result);
    } catch (error) {
      logger.error(`获取文化体系知识失败, 体系: ${req.params.culturalSystem}`, error);
      next(error);
    }
  }

  /**
   * 获取易经卦象知识
   */
  async getHexagramKnowledge(req: Request, res: Response, next: NextFunction) {
    try {
      const { name } = req.query;
      
      const result = await this.traditionalCultureService.getHexagramKnowledge(name as string);
      
      res.status(200).json(result);
    } catch (error) {
      logger.error('获取易经卦象知识失败', error);
      next(error);
    }
  }

  /**
   * 根据历史时期获取知识
   */
  async getKnowledgeByHistoricalPeriod(req: Request, res: Response, next: NextFunction) {
    try {
      const { historicalPeriod } = req.params;
      const { page = '1', limit = '20' } = req.query;
      
      const result = await this.traditionalCultureService.getKnowledgeByHistoricalPeriod(
        historicalPeriod,
        parseInt(page as string, 10),
        parseInt(limit as string, 10)
      );
      
      res.status(200).json(result);
    } catch (error) {
      logger.error(`获取历史时期知识失败, 时期: ${req.params.historicalPeriod}`, error);
      next(error);
    }
  }
}