/**
 * 心理健康知识控制器
 */
import { Request, Response } from 'express';
import { BadRequestError } from '../errors/bad-request-error';
import { NotFoundError } from '../errors/not-found-error';
import mentalHealthService from '../services/mental-health.service';
import logger from '../utils/logger';

export class MentalHealthController {
  /**
   * 创建心理健康知识条目
   * @route POST /api/knowledge/mental-health
   */
  async createMentalHealth(req: Request, res: Response) {
    try {
      const data = req.body;
      
      // 验证必填字段
      if (!data.title || !data.description || !data.content || !data.issueType) {
        throw new BadRequestError('缺少必要字段');
      }
      
      // 设置创建者ID（如果有）
      if (req.currentUser) {
        data.createdBy = req.currentUser.id;
      }
      
      const result = await mentalHealthService.createMentalHealth(data);
      
      logger.info('心理健康知识创建成功', { id: result._id });
      
      res.status(201).json({
        success: true,
        data: result
      });
    } catch (error) {
      logger.error('创建心理健康知识失败', { error: (error as Error).message });
      
      if (error instanceof BadRequestError) {
        return res.status(400).json({
          success: false,
          message: error.message
        });
      }
      
      res.status(500).json({
        success: false,
        message: '服务器错误'
      });
    }
  }

  /**
   * 获取心理健康知识条目
   * @route GET /api/knowledge/mental-health/:id
   */
  async getMentalHealth(req: Request, res: Response) {
    try {
      const { id } = req.params;
      
      const result = await mentalHealthService.getMentalHealth(id);
      
      if (!result) {
        throw new NotFoundError('未找到心理健康知识条目');
      }
      
      res.status(200).json({
        success: true,
        data: result
      });
    } catch (error) {
      logger.error('获取心理健康知识失败', { error: (error as Error).message, id: req.params.id });
      
      if (error instanceof NotFoundError) {
        return res.status(404).json({
          success: false,
          message: error.message
        });
      }
      
      res.status(500).json({
        success: false,
        message: '服务器错误'
      });
    }
  }

  /**
   * 更新心理健康知识条目
   * @route PUT /api/knowledge/mental-health/:id
   */
  async updateMentalHealth(req: Request, res: Response) {
    try {
      const { id } = req.params;
      const data = req.body;
      
      const result = await mentalHealthService.updateMentalHealth(id, data);
      
      if (!result) {
        throw new NotFoundError('未找到心理健康知识条目');
      }
      
      logger.info('心理健康知识更新成功', { id });
      
      res.status(200).json({
        success: true,
        data: result
      });
    } catch (error) {
      logger.error('更新心理健康知识失败', { error: (error as Error).message, id: req.params.id });
      
      if (error instanceof NotFoundError) {
        return res.status(404).json({
          success: false,
          message: error.message
        });
      }
      
      res.status(500).json({
        success: false,
        message: '服务器错误'
      });
    }
  }

  /**
   * 删除心理健康知识条目
   * @route DELETE /api/knowledge/mental-health/:id
   */
  async deleteMentalHealth(req: Request, res: Response) {
    try {
      const { id } = req.params;
      
      const result = await mentalHealthService.deleteMentalHealth(id);
      
      if (!result) {
        throw new NotFoundError('未找到心理健康知识条目');
      }
      
      logger.info('心理健康知识删除成功', { id });
      
      res.status(200).json({
        success: true,
        message: '心理健康知识删除成功'
      });
    } catch (error) {
      logger.error('删除心理健康知识失败', { error: (error as Error).message, id: req.params.id });
      
      if (error instanceof NotFoundError) {
        return res.status(404).json({
          success: false,
          message: error.message
        });
      }
      
      res.status(500).json({
        success: false,
        message: '服务器错误'
      });
    }
  }

  /**
   * 获取心理健康知识列表
   * @route GET /api/knowledge/mental-health
   */
  async getMentalHealthList(req: Request, res: Response) {
    try {
      const { page = 1, limit = 20, issueType, ageGroup, interventionMethod, keyword } = req.query;
      
      let filter: any = {};
      
      // 应用过滤条件
      if (issueType) {
        filter.issueType = issueType;
      }
      
      if (ageGroup) {
        filter.targetAgeGroups = ageGroup;
      }
      
      if (interventionMethod) {
        filter.interventionMethods = interventionMethod;
      }
      
      let result;
      
      // 如果有关键词，使用搜索功能
      if (keyword) {
        result = await mentalHealthService.searchMentalHealth(
          keyword as string,
          parseInt(page as string),
          parseInt(limit as string)
        );
      } else {
        result = await mentalHealthService.getMentalHealthList(
          filter,
          parseInt(page as string),
          parseInt(limit as string)
        );
      }
      
      res.status(200).json({
        success: true,
        ...result
      });
    } catch (error) {
      logger.error('获取心理健康知识列表失败', { error: (error as Error).message, query: req.query });
      
      res.status(500).json({
        success: false,
        message: '服务器错误'
      });
    }
  }

  /**
   * 按心理问题类型获取心理健康知识
   * @route GET /api/knowledge/mental-health/issue/:type
   */
  async getMentalHealthByIssueType(req: Request, res: Response) {
    try {
      const { type } = req.params;
      const { page = 1, limit = 20 } = req.query;
      
      const result = await mentalHealthService.getMentalHealthByIssueType(
        type,
        parseInt(page as string),
        parseInt(limit as string)
      );
      
      res.status(200).json({
        success: true,
        ...result
      });
    } catch (error) {
      logger.error('按心理问题类型获取心理健康知识失败', { 
        error: (error as Error).message, 
        type: req.params.type 
      });
      
      res.status(500).json({
        success: false,
        message: '服务器错误'
      });
    }
  }

  /**
   * 按年龄组获取心理健康知识
   * @route GET /api/knowledge/mental-health/age-group/:ageGroup
   */
  async getMentalHealthByAgeGroup(req: Request, res: Response) {
    try {
      const { ageGroup } = req.params;
      const { page = 1, limit = 20 } = req.query;
      
      const result = await mentalHealthService.getMentalHealthByAgeGroup(
        ageGroup,
        parseInt(page as string),
        parseInt(limit as string)
      );
      
      res.status(200).json({
        success: true,
        ...result
      });
    } catch (error) {
      logger.error('按年龄组获取心理健康知识失败', { 
        error: (error as Error).message, 
        ageGroup: req.params.ageGroup 
      });
      
      res.status(500).json({
        success: false,
        message: '服务器错误'
      });
    }
  }

  /**
   * 按干预方法获取心理健康知识
   * @route GET /api/knowledge/mental-health/intervention/:method
   */
  async getMentalHealthByInterventionMethod(req: Request, res: Response) {
    try {
      const { method } = req.params;
      const { page = 1, limit = 20 } = req.query;
      
      const result = await mentalHealthService.getMentalHealthByInterventionMethod(
        method,
        parseInt(page as string),
        parseInt(limit as string)
      );
      
      res.status(200).json({
        success: true,
        ...result
      });
    } catch (error) {
      logger.error('按干预方法获取心理健康知识失败', { 
        error: (error as Error).message, 
        method: req.params.method 
      });
      
      res.status(500).json({
        success: false,
        message: '服务器错误'
      });
    }
  }

  /**
   * 搜索心理健康知识
   * @route GET /api/knowledge/mental-health/search/:keyword
   */
  async searchMentalHealth(req: Request, res: Response) {
    try {
      const { keyword } = req.params;
      const { page = 1, limit = 20 } = req.query;
      
      const result = await mentalHealthService.searchMentalHealth(
        keyword,
        parseInt(page as string),
        parseInt(limit as string)
      );
      
      res.status(200).json({
        success: true,
        ...result
      });
    } catch (error) {
      logger.error('搜索心理健康知识失败', { 
        error: (error as Error).message, 
        keyword: req.params.keyword 
      });
      
      res.status(500).json({
        success: false,
        message: '服务器错误'
      });
    }
  }
}

export default new MentalHealthController();