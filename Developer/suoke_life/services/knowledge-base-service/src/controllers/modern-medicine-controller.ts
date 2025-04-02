/**
 * 现代医学知识控制器
 * 处理现代医学知识相关的请求
 */

import { Request, Response, NextFunction } from 'express';
import { ModernMedicineKnowledgeService } from '../services/modern-medicine-knowledge.service';
import { ApiError } from '../utils/api-error';
import { logger } from '../utils/logger';

export class ModernMedicineController {
  private modernMedicineService: ModernMedicineKnowledgeService;

  constructor() {
    this.modernMedicineService = new ModernMedicineKnowledgeService();
  }

  /**
   * 获取现代医学知识列表
   */
  async getModernMedicineKnowledgeList(req: Request, res: Response, next: NextFunction) {
    try {
      const { 
        page = '1', 
        limit = '20', 
        category,
        medicalSystem,
        researchSupport,
        sort = 'createdAt',
        order = 'desc',
        search
      } = req.query;

      const filter: any = {};
      
      if (category) {
        filter.categories = { $in: [category] };
      }
      
      if (medicalSystem) {
        filter.medicalSystem = medicalSystem;
      }
      
      if (researchSupport) {
        filter.researchSupport = researchSupport;
      }
      
      if (search) {
        filter.$or = [
          { title: { $regex: search, $options: 'i' } },
          { content: { $regex: search, $options: 'i' } },
          { summary: { $regex: search, $options: 'i' } }
        ];
      }

      const result = await this.modernMedicineService.listModernMedicineKnowledge(
        parseInt(page as string, 10),
        parseInt(limit as string, 10),
        filter,
        { [sort as string]: order === 'desc' ? -1 : 1 }
      );

      res.status(200).json(result);
    } catch (error) {
      logger.error('获取现代医学知识列表失败', error);
      next(error);
    }
  }

  /**
   * 获取现代医学知识详情
   */
  async getModernMedicineKnowledgeById(req: Request, res: Response, next: NextFunction) {
    try {
      const { id } = req.params;
      const knowledge = await this.modernMedicineService.getModernMedicineKnowledgeById(id);
      
      if (!knowledge) {
        throw new ApiError(404, '现代医学知识不存在');
      }
      
      res.status(200).json(knowledge);
    } catch (error) {
      logger.error(`获取现代医学知识详情失败, ID: ${req.params.id}`, error);
      next(error);
    }
  }

  /**
   * 创建现代医学知识
   */
  async createModernMedicineKnowledge(req: Request, res: Response, next: NextFunction) {
    try {
      const knowledgeData = req.body;
      
      // 添加创建者信息
      if (req.user) {
        knowledgeData.createdBy = req.user.id;
      }
      
      const createdKnowledge = await this.modernMedicineService.createModernMedicineKnowledge(knowledgeData);
      
      res.status(201).json(createdKnowledge);
    } catch (error) {
      logger.error('创建现代医学知识失败', error);
      next(error);
    }
  }

  /**
   * 更新现代医学知识
   */
  async updateModernMedicineKnowledge(req: Request, res: Response, next: NextFunction) {
    try {
      const { id } = req.params;
      const knowledgeData = req.body;
      
      // 添加更新者信息
      if (req.user) {
        knowledgeData.updatedBy = req.user.id;
      }
      
      const updatedKnowledge = await this.modernMedicineService.updateModernMedicineKnowledge(id, knowledgeData);
      
      if (!updatedKnowledge) {
        throw new ApiError(404, '现代医学知识不存在');
      }
      
      res.status(200).json(updatedKnowledge);
    } catch (error) {
      logger.error(`更新现代医学知识失败, ID: ${req.params.id}`, error);
      next(error);
    }
  }

  /**
   * 删除现代医学知识
   */
  async deleteModernMedicineKnowledge(req: Request, res: Response, next: NextFunction) {
    try {
      const { id } = req.params;
      const result = await this.modernMedicineService.deleteModernMedicineKnowledge(id);
      
      if (!result) {
        throw new ApiError(404, '现代医学知识不存在');
      }
      
      res.status(200).json({ message: '现代医学知识删除成功' });
    } catch (error) {
      logger.error(`删除现代医学知识失败, ID: ${req.params.id}`, error);
      next(error);
    }
  }

  /**
   * 根据医学体系获取知识
   */
  async getKnowledgeByMedicalSystem(req: Request, res: Response, next: NextFunction) {
    try {
      const { medicalSystem } = req.params;
      const { page = '1', limit = '20' } = req.query;
      
      const result = await this.modernMedicineService.getKnowledgeByMedicalSystem(
        medicalSystem,
        parseInt(page as string, 10),
        parseInt(limit as string, 10)
      );
      
      res.status(200).json(result);
    } catch (error) {
      logger.error(`获取医学体系知识失败, 体系: ${req.params.medicalSystem}`, error);
      next(error);
    }
  }

  /**
   * 根据研究支持程度获取知识
   */
  async getKnowledgeByResearchSupport(req: Request, res: Response, next: NextFunction) {
    try {
      const { level } = req.params;
      const { page = '1', limit = '20' } = req.query;
      
      const result = await this.modernMedicineService.getKnowledgeByResearchSupport(
        level,
        parseInt(page as string, 10),
        parseInt(limit as string, 10)
      );
      
      res.status(200).json(result);
    } catch (error) {
      logger.error(`获取研究支持程度知识失败, 程度: ${req.params.level}`, error);
      next(error);
    }
  }
}