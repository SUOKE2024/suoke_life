import { Request as ExpressRequest, Response as ExpressResponse } from 'express';
import { logger } from '../utils/logger';
import * as supplyChainService from '../services/supply-chain';

// 扩展请求和响应类型以匹配实际使用
interface Request extends ExpressRequest {
  params: any;
  body: any;
  query: any;
}

interface Response extends ExpressResponse {
  status: (code: number) => Response;
  json: (data: any) => void;
}

/**
 * 获取供应链信息
 * @param req 请求对象
 * @param res 响应对象
 */
export const getSupplyChainInfo = async (req: Request, res: Response): Promise<void> => {
  try {
    const { productId } = req.params;
    logger.info(`获取供应链信息: ${productId}`);

    if (!productId) {
      res.status(400).json({ success: false, message: '必须提供产品ID' });
      return;
    }

    const supplyChainData = await supplyChainService.getSupplyChainInfo(productId);
    res.status(200).json({ success: true, data: supplyChainData });
  } catch (error) {
    logger.error('获取供应链信息失败:', error);
    res.status(500).json({ 
      success: false, 
      message: '获取供应链信息失败', 
      error: (error as Error).message 
    });
  }
};

/**
 * 获取供应链可视化数据
 * @param req 请求对象
 * @param res 响应对象
 */
export const getSupplyChainVisualization = async (req: Request, res: Response): Promise<void> => {
  try {
    const { productId } = req.params;
    logger.info(`获取供应链可视化数据: ${productId}`);

    if (!productId) {
      res.status(400).json({ success: false, message: '必须提供产品ID' });
      return;
    }

    const visualizationData = await supplyChainService.getSupplyChainVisualization(productId);
    res.status(200).json({ success: true, data: visualizationData });
  } catch (error) {
    logger.error('获取供应链可视化数据失败:', error);
    res.status(500).json({ 
      success: false, 
      message: '获取供应链可视化数据失败', 
      error: (error as Error).message 
    });
  }
};

/**
 * 记录供应链事件
 * @param req 请求对象
 * @param res 响应对象
 */
export const recordSupplyChainEvent = async (req: Request, res: Response): Promise<void> => {
  try {
    logger.info('记录供应链事件');

    const eventData = req.body;
    
    // 验证必要字段
    if (!eventData.productId || !eventData.type || !eventData.description) {
      res.status(400).json({ 
        success: false, 
        message: '缺少必要字段: productId, type, description' 
      });
      return;
    }

    const event = await supplyChainService.recordSupplyChainEvent(eventData);
    res.status(201).json({ success: true, data: event });
  } catch (error) {
    logger.error('记录供应链事件失败:', error);
    res.status(500).json({ 
      success: false, 
      message: '记录供应链事件失败', 
      error: (error as Error).message 
    });
  }
};

/**
 * 获取产品事件历史
 * @param req 请求对象
 * @param res 响应对象
 */
export const getProductEventHistory = async (req: Request, res: Response): Promise<void> => {
  try {
    const { productId } = req.params;
    logger.info(`获取产品事件历史: ${productId}`);

    if (!productId) {
      res.status(400).json({ success: false, message: '必须提供产品ID' });
      return;
    }

    const events = await supplyChainService.getProductEventHistory(productId);
    res.status(200).json({ success: true, data: events });
  } catch (error) {
    logger.error('获取产品事件历史失败:', error);
    res.status(500).json({ 
      success: false, 
      message: '获取产品事件历史失败', 
      error: (error as Error).message 
    });
  }
};

/**
 * 获取最近事件
 * @param req 请求对象
 * @param res 响应对象
 */
export const getRecentEvents = async (req: Request, res: Response): Promise<void> => {
  try {
    const limit = req.query.limit ? parseInt(req.query.limit as string) : 10;
    logger.info(`获取最近 ${limit} 条事件`);

    const events = await supplyChainService.getRecentEvents(limit);
    res.status(200).json({ success: true, data: events });
  } catch (error) {
    logger.error('获取最近事件失败:', error);
    res.status(500).json({ 
      success: false, 
      message: '获取最近事件失败', 
      error: (error as Error).message 
    });
  }
};

/**
 * 获取事件统计
 * @param req 请求对象
 * @param res 响应对象
 */
export const getEventStatistics = async (req: Request, res: Response): Promise<void> => {
  try {
    logger.info('获取事件统计数据');

    const statistics = await supplyChainService.getEventStatistics();
    res.status(200).json({ success: true, data: statistics });
  } catch (error) {
    logger.error('获取事件统计数据失败:', error);
    res.status(500).json({ 
      success: false, 
      message: '获取事件统计数据失败', 
      error: (error as Error).message 
    });
  }
};

/**
 * 获取警报
 * @param req 请求对象
 * @param res 响应对象
 */
export const getAlerts = async (req: Request, res: Response): Promise<void> => {
  try {
    const level = req.query.level as 'high' | 'medium' | 'low' | undefined;
    const limit = req.query.limit ? parseInt(req.query.limit as string) : 50;
    const productId = req.query.productId as string | undefined;
    
    logger.info(`获取警报列表: 级别=${level || '所有'}, 限制=${limit}, 产品ID=${productId || '所有'}`);

    const alerts = await supplyChainService.getAlerts(level, limit, productId);
    res.status(200).json({ success: true, data: alerts });
  } catch (error) {
    logger.error('获取警报列表失败:', error);
    res.status(500).json({ 
      success: false, 
      message: '获取警报列表失败', 
      error: (error as Error).message 
    });
  }
};

/**
 * 确认警报
 * @param req 请求对象
 * @param res 响应对象
 */
export const acknowledgeAlert = async (req: Request, res: Response): Promise<void> => {
  try {
    const { alertId } = req.params;
    const { userId } = req.body;
    
    logger.info(`确认警报: ${alertId}, 用户ID: ${userId}`);

    if (!alertId) {
      res.status(400).json({ success: false, message: '必须提供警报ID' });
      return;
    }

    if (!userId) {
      res.status(400).json({ success: false, message: '必须提供用户ID' });
      return;
    }

    const alert = await supplyChainService.acknowledgeAlert(alertId, userId);
    res.status(200).json({ success: true, data: alert });
  } catch (error) {
    logger.error('确认警报失败:', error);
    res.status(500).json({ 
      success: false, 
      message: '确认警报失败', 
      error: (error as Error).message 
    });
  }
};

/**
 * 解决警报
 * @param req 请求对象
 * @param res 响应对象
 */
export const resolveAlert = async (req: Request, res: Response): Promise<void> => {
  try {
    const { alertId } = req.params;
    const { userId, resolution } = req.body;
    
    logger.info(`解决警报: ${alertId}, 用户ID: ${userId}`);

    if (!alertId) {
      res.status(400).json({ success: false, message: '必须提供警报ID' });
      return;
    }

    if (!userId) {
      res.status(400).json({ success: false, message: '必须提供用户ID' });
      return;
    }

    if (!resolution) {
      res.status(400).json({ success: false, message: '必须提供解决方案' });
      return;
    }

    const alert = await supplyChainService.resolveAlert(alertId, userId, resolution);
    res.status(200).json({ success: true, data: alert });
  } catch (error) {
    logger.error('解决警报失败:', error);
    res.status(500).json({ 
      success: false, 
      message: '解决警报失败', 
      error: (error as Error).message 
    });
  }
};

/**
 * 获取警报统计
 * @param req 请求对象
 * @param res 响应对象
 */
export const getAlertStatistics = async (req: Request, res: Response): Promise<void> => {
  try {
    logger.info('获取警报统计数据');

    const statistics = await supplyChainService.getAlertStatistics();
    res.status(200).json({ success: true, data: statistics });
  } catch (error) {
    logger.error('获取警报统计数据失败:', error);
    res.status(500).json({ 
      success: false, 
      message: '获取警报统计数据失败', 
      error: (error as Error).message 
    });
  }
}; 