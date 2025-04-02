import { Request, Response } from 'express';
import { logger } from '../utils/logger';
import { receiveSensorData, getProductEnvironmentData } from '../services/iot/supply-chain-sensors';

/**
 * 接收传感器数据
 */
export const receiveSensorDataAPI = async (req: Request, res: Response): Promise<void> => {
  try {
    const sensorData = req.body;
    
    if (!sensorData || !sensorData.sensorId || !sensorData.productId) {
      res.status(400).json({ success: false, message: '传感器数据不完整' });
      return;
    }
    
    const result = await receiveSensorData(sensorData);
    res.status(201).json({ success: true, data: result });
  } catch (error) {
    logger.error('处理传感器数据失败:', error);
    res.status(500).json({ 
      success: false, 
      message: '处理传感器数据失败', 
      error: (error as Error).message 
    });
  }
};

/**
 * 获取产品环境数据
 */
export const getEnvironmentData = async (req: Request, res: Response): Promise<void> => {
  try {
    const { productId } = req.params;
    const { type, limit } = req.query;
    
    if (!productId) {
      res.status(400).json({ success: false, message: '必须提供产品ID' });
      return;
    }
    
    const data = getProductEnvironmentData(
      productId, 
      type as string, 
      limit ? parseInt(limit as string) : undefined
    );
    
    res.status(200).json({ success: true, data });
  } catch (error) {
    logger.error('获取环境数据失败:', error);
    res.status(500).json({ 
      success: false, 
      message: '获取环境数据失败', 
      error: (error as Error).message 
    });
  }
};