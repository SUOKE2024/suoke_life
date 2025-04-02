import { Request, Response } from 'express';
import { logger } from '../utils/logger';
import { 
  verifyEventOnBlockchain, 
  getProductBlockchainProof, 
  saveEventToBlockchain 
} from '../services/blockchain/supply-chain-blockchain';

/**
 * 验证事件在区块链上的真实性
 */
export const verifyEvent = async (req: Request, res: Response): Promise<void> => {
  try {
    const { eventId } = req.params;
    
    if (!eventId) {
      res.status(400).json({ success: false, message: '必须提供事件ID' });
      return;
    }
    
    const verification = await verifyEventOnBlockchain(eventId);
    res.status(200).json({ success: true, data: verification });
  } catch (error) {
    logger.error('区块链验证失败:', error);
    res.status(500).json({ 
      success: false, 
      message: '区块链验证失败', 
      error: (error as Error).message 
    });
  }
};

/**
 * 获取产品的区块链证明
 */
export const getBlockchainProof = async (req: Request, res: Response): Promise<void> => {
  try {
    const { productId } = req.params;
    
    if (!productId) {
      res.status(400).json({ success: false, message: '必须提供产品ID' });
      return;
    }
    
    const proof = await getProductBlockchainProof(productId);
    res.status(200).json({ success: true, data: proof });
  } catch (error) {
    logger.error('获取区块链证明失败:', error);
    res.status(500).json({ 
      success: false, 
      message: '获取区块链证明失败', 
      error: (error as Error).message 
    });
  }
};

/**
 * 手动将事件保存到区块链
 */
export const saveToBlockchain = async (req: Request, res: Response): Promise<void> => {
  try {
    const event = req.body;
    
    if (!event || !event.productId || !event.type) {
      res.status(400).json({ success: false, message: '事件数据不完整' });
      return;
    }
    
    const blockchainEvent = await saveEventToBlockchain(event);
    res.status(201).json({ success: true, data: blockchainEvent });
  } catch (error) {
    logger.error('保存到区块链失败:', error);
    res.status(500).json({ 
      success: false, 
      message: '保存到区块链失败', 
      error: (error as Error).message 
    });
  }
};