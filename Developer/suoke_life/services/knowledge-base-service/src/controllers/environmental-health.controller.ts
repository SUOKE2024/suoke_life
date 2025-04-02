/**
 * 环境健康知识控制器
 */
import { Request, Response } from 'express';
import { BadRequestError } from '../errors/bad-request-error';
import { NotFoundError } from '../errors/not-found-error';
import environmentalHealthService from '../services/environmental-health.service';
import logger from '../utils/logger';

export class EnvironmentalHealthController {
  /**
   * 创建环境健康知识条目
   * @route POST /api/knowledge/environmental-health
   */
  async createEnvironmentalHealth(req: Request, res: Response) {
    try {
      const data = req.body;
      
      // 验证必填字段
      if (!data.title || !data.description || !data.content || !data.environmentType || !data.riskLevel) {
        throw new BadRequestError('缺少必要字段');
      }
      
      // 设置创建者ID（如果有）
      if (req.currentUser) {
        data.createdBy = req.currentUser.id;
      }
      
      const result = await environmentalHealthService.createEnvironmentalHealth(data);
      
      logger.info('环境健康知识创建成功', { id: result._id });
      
      res.status(201).json({
        success: true,
        data: result
      });
    } catch (error) {
      logger.error('创建环境健康知识失败', { error: (error as Error).message });
      
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
   * 获取环境健康知识条目
   * @route GET /api/knowledge/environmental-health/:id
   */
  async getEnvironmentalHealth(req: Request, res: Response) {
    try {
      const { id } = req.params;
      
      const result = await environmentalHealthService.getEnvironmentalHealth(id);
      
      if (!result) {
        throw new NotFoundError('未找到环境健康知识条目');
      }
      
      res.status(200).json({
        success: true,
        data: result
      });
    } catch (error) {
      logger.error('获取环境健康知识失败', { error: (error as Error).message, id: req.params.id });
      
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
   * 更新环境健康知识条目
   * @route PUT /api/knowledge/environmental-health/:id
   */
  async updateEnvironmentalHealth(req: Request, res: Response) {
    try {
      const { id } = req.params;
      const data = req.body;
      
      const result = await environmentalHealthService.updateEnvironmentalHealth(id, data);
      
      if (!result) {
        throw new NotFoundError('未找到环境健康知识条目');
      }
      
      logger.info('环境健康知识更新成功', { id });
      
      res.status(200).json({
        success: true,
        data: result
      });
    } catch (error) {
      logger.error('更新环境健康知识失败', { error: (error as Error).message, id: req.params.id });
      
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
   * 删除环境健康知识条目
   * @route DELETE /api/knowledge/environmental-health/:id
   */
  async deleteEnvironmentalHealth(req: Request, res: Response) {
    try {
      const { id } = req.params;
      
      const result = await environmentalHealthService.deleteEnvironmentalHealth(id);
      
      if (!result) {
        throw new NotFoundError('未找到环境健康知识条目');
      }
      
      logger.info('环境健康知识删除成功', { id });
      
      res.status(200).json({
        success: true,
        message: '环境健康知识删除成功'
      });
    } catch (error) {
      logger.error('删除环境健康知识失败', { error: (error as Error).message, id: req.params.id });
      
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
   * 获取环境健康知识列表
   * @route GET /api/knowledge/environmental-health
   */
  async getEnvironmentalHealthList(req: Request, res: Response) {
    try {
      const { page = 1, limit = 20, environmentType, pollutantType, healthImpact, region, riskLevel, keyword } = req.query;
      
      let filter: any = {};
      
      // 应用过滤条件
      if (environmentType) {
        filter.environmentType = environmentType;
      }
      
      if (pollutantType) {
        filter.pollutantType = pollutantType;
      }
      
      if (healthImpact) {
        filter.healthImpacts = healthImpact;
      }
      
      if (region) {
        filter.regionSpecific = region;
      }
      
      if (riskLevel) {
        filter.riskLevel = parseInt(riskLevel as string);
      }
      
      let result;
      
      // 如果有关键词，使用搜索功能
      if (keyword) {
        result = await environmentalHealthService.searchEnvironmentalHealth(
          keyword as string,
          parseInt(page as string),
          parseInt(limit as string)
        );
      } else {
        result = await environmentalHealthService.getEnvironmentalHealthList(
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
      logger.error('获取环境健康知识列表失败', { error: (error as Error).message, query: req.query });
      
      res.status(500).json({
        success: false,
        message: '服务器错误'
      });
    }
  }

  /**
   * 按环境类型获取环境健康知识
   * @route GET /api/knowledge/environmental-health/type/:type
   */
  async getEnvironmentalHealthByType(req: Request, res: Response) {
    try {
      const { type } = req.params;
      const { page = 1, limit = 20 } = req.query;
      
      const result = await environmentalHealthService.getEnvironmentalHealthByType(
        type,
        parseInt(page as string),
        parseInt(limit as string)
      );
      
      res.status(200).json({
        success: true,
        ...result
      });
    } catch (error) {
      logger.error('按环境类型获取环境健康知识失败', { 
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
   * 按污染物类型获取环境健康知识
   * @route GET /api/knowledge/environmental-health/pollutant/:pollutant
   */
  async getEnvironmentalHealthByPollutant(req: Request, res: Response) {
    try {
      const { pollutant } = req.params;
      const { page = 1, limit = 20 } = req.query;
      
      const result = await environmentalHealthService.getEnvironmentalHealthByPollutant(
        pollutant,
        parseInt(page as string),
        parseInt(limit as string)
      );
      
      res.status(200).json({
        success: true,
        ...result
      });
    } catch (error) {
      logger.error('按污染物类型获取环境健康知识失败', { 
        error: (error as Error).message, 
        pollutant: req.params.pollutant 
      });
      
      res.status(500).json({
        success: false,
        message: '服务器错误'
      });
    }
  }

  /**
   * 按健康影响获取环境健康知识
   * @route GET /api/knowledge/environmental-health/impact/:impact
   */
  async getEnvironmentalHealthByHealthImpact(req: Request, res: Response) {
    try {
      const { impact } = req.params;
      const { page = 1, limit = 20 } = req.query;
      
      const result = await environmentalHealthService.getEnvironmentalHealthByHealthImpact(
        impact,
        parseInt(page as string),
        parseInt(limit as string)
      );
      
      res.status(200).json({
        success: true,
        ...result
      });
    } catch (error) {
      logger.error('按健康影响获取环境健康知识失败', { 
        error: (error as Error).message, 
        impact: req.params.impact 
      });
      
      res.status(500).json({
        success: false,
        message: '服务器错误'
      });
    }
  }

  /**
   * 按地区获取环境健康知识
   * @route GET /api/knowledge/environmental-health/region/:region
   */
  async getEnvironmentalHealthByRegion(req: Request, res: Response) {
    try {
      const { region } = req.params;
      const { page = 1, limit = 20 } = req.query;
      
      const result = await environmentalHealthService.getEnvironmentalHealthByRegion(
        region,
        parseInt(page as string),
        parseInt(limit as string)
      );
      
      res.status(200).json({
        success: true,
        ...result
      });
    } catch (error) {
      logger.error('按地区获取环境健康知识失败', { 
        error: (error as Error).message, 
        region: req.params.region 
      });
      
      res.status(500).json({
        success: false,
        message: '服务器错误'
      });
    }
  }

  /**
   * 按风险级别获取环境健康知识
   * @route GET /api/knowledge/environmental-health/risk/:level
   */
  async getEnvironmentalHealthByRiskLevel(req: Request, res: Response) {
    try {
      const { level } = req.params;
      const { page = 1, limit = 20 } = req.query;
      
      const result = await environmentalHealthService.getEnvironmentalHealthByRiskLevel(
        parseInt(level),
        parseInt(page as string),
        parseInt(limit as string)
      );
      
      res.status(200).json({
        success: true,
        ...result
      });
    } catch (error) {
      logger.error('按风险级别获取环境健康知识失败', { 
        error: (error as Error).message, 
        level: req.params.level 
      });
      
      res.status(500).json({
        success: false,
        message: '服务器错误'
      });
    }
  }

  /**
   * 搜索环境健康知识
   * @route GET /api/knowledge/environmental-health/search/:keyword
   */
  async searchEnvironmentalHealth(req: Request, res: Response) {
    try {
      const { keyword } = req.params;
      const { page = 1, limit = 20 } = req.query;
      
      const result = await environmentalHealthService.searchEnvironmentalHealth(
        keyword,
        parseInt(page as string),
        parseInt(limit as string)
      );
      
      res.status(200).json({
        success: true,
        ...result
      });
    } catch (error) {
      logger.error('搜索环境健康知识失败', { 
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

export default new EnvironmentalHealthController();