import { Request, Response } from 'express';
import { logger } from '../utils/logger';
import { predictSupplyChainRisks } from '../services/ai/supply-chain-predictions';

/**
 * 预测供应链风险
 */
export const predictRisks = async (req: Request, res: Response): Promise<void> => {
  try {
    const { productId } = req.params;
    
    if (!productId) {
      res.status(400).json({ success: false, message: '必须提供产品ID' });
      return;
    }
    
    const prediction = await predictSupplyChainRisks(productId);
    res.status(200).json({ success: true, data: prediction });
  } catch (error) {
    logger.error('预测供应链风险失败:', error);
    res.status(500).json({ 
      success: false, 
      message: '预测供应链风险失败', 
      error: (error as Error).message 
    });
  }
};