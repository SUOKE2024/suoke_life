import { Request, Response } from 'express';
import { logger } from '../utils/logger';
import { generateProductQRCode, getProductInfoFromQR } from '../services/consumer/traceability-api';

/**
 * 生成产品溯源QR码
 */
export const generateQRCode = async (req: Request, res: Response): Promise<void> => {
  try {
    const { productId, batchId } = req.body;
    
    if (!productId) {
      res.status(400).json({ success: false, message: '必须提供产品ID' });
      return;
    }
    
    const qrCode = generateProductQRCode(productId, batchId);
    res.status(201).json({ success: true, data: qrCode });
  } catch (error) {
    logger.error('生成QR码失败:', error);
    res.status(500).json({ 
      success: false, 
      message: '生成QR码失败', 
      error: (error as Error).message 
    });
  }
};

/**
 * 获取QR码产品信息
 */
export const getProductByQRCode = async (req: Request, res: Response): Promise<void> => {
  try {
    const { qrId } = req.params;
    
    if (!qrId) {
      res.status(400).json({ success: false, message: '必须提供QR码ID' });
      return;
    }
    
    const productInfo = await getProductInfoFromQR(qrId);
    res.status(200).json({ success: true, data: productInfo });
  } catch (error) {
    logger.error('获取QR码产品信息失败:', error);
    res.status(500).json({ 
      success: false, 
      message: '获取QR码产品信息失败', 
      error: (error as Error).message 
    });
  }
};