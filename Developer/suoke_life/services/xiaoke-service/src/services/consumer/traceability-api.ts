import { v4 as uuidv4 } from 'uuid';
import { logger } from '../../utils/logger';
import { getSupplyChainStatus } from '../supply-chain/status';
import { getProductEventHistory } from '../supply-chain/tracking';
import { getProductBlockchainProof } from '../blockchain/supply-chain-blockchain';

// QR码数据结构
interface QRCodeData {
  id: string;
  productId: string;
  batchId?: string;
  timestamp: string;
  url: string;
}

// 存储生成的QR码信息
const qrCodes: QRCodeData[] = [];

/**
 * 为产品生成追溯QR码数据
 */
export const generateProductQRCode = (productId: string, batchId?: string): QRCodeData => {
  try {
    logger.info(`为产品生成QR码: ${productId}`);
    
    const qrId = uuidv4();
    const baseUrl = process.env.CONSUMER_APP_URL || 'https://app.suoke.life';
    const url = `${baseUrl}/trace/${qrId}`;
    
    const qrData: QRCodeData = {
      id: qrId,
      productId,
      batchId,
      timestamp: new Date().toISOString(),
      url
    };
    
    // 存储QR码数据以供后续查询
    qrCodes.push(qrData);
    
    logger.info(`产品QR码已生成: ${qrId}`);
    return qrData;
  } catch (error) {
    logger.error('生成QR码失败:', error);
    throw new Error(`生成QR码失败: ${(error as Error).message}`);
  }
};

/**
 * 从QR码ID获取产品信息
 */
export const getProductInfoFromQR = async (qrId: string): Promise<any> => {
  try {
    logger.info(`通过QR码获取产品信息: ${qrId}`);
    
    // 找到匹配的QR码
    const qrData = qrCodes.find(qr => qr.id === qrId);
    
    if (!qrData) {
      throw new Error('无效的QR码');
    }
    
    // 获取产品信息
    const productId = qrData.productId;
    const status = getSupplyChainStatus(productId);
    const events = getProductEventHistory(productId);
    
    // 获取区块链证明
    const blockchainProof = await getProductBlockchainProof(productId);
    
    // 构建消费者友好的数据格式
    return {
      product: {
        id: productId,
        name: status.productName,
        batchId: qrData.batchId
      },
      journey: {
        currentStage: status.currentStage,
        stages: status.stages.map(stage => ({
          name: getStageChineseName(stage.name),
          status: getStatusChineseName(stage.status),
          date: stage.startTime ? new Date(stage.startTime).toLocaleDateString('zh-CN') : '未开始'
        }))
      },
      keyEvents: events.slice(0, 5).map(event => ({
        type: getEventChineseName(event.type),
        date: new Date(event.timestamp).toLocaleDateString('zh-CN'),
        location: event.location || '未知',
        description: event.description
      })),
      certification: {
        verified: blockchainProof.length > 0,
        lastVerified: blockchainProof.length > 0 ? new Date(blockchainProof[0].timestamp).toLocaleDateString('zh-CN') : '未验证',
        certificationCount: blockchainProof.length
      },
      scanInfo: {
        scanTime: new Date().toISOString(),
        qrCodeId: qrId
      }
    };
  } catch (error) {
    logger.error('获取QR码产品信息失败:', error);
    throw new Error(`获取QR码产品信息失败: ${(error as Error).message}`);
  }
};

/**
 * 获取阶段中文名称
 */
const getStageChineseName = (stageName: string): string => {
  const stageNames: Record<string, string> = {
    'production': '生产',
    'quality': '质检',
    'packaging': '包装',
    'storage': '仓储',
    'shipment': '运输',
    'delivery': '配送',
    'completed': '已完成'
  };
  
  return stageNames[stageName] || stageName;
};

/**
 * 获取状态中文名称
 */
const getStatusChineseName = (status: string): string => {
  const statusNames: Record<string, string> = {
    'pending': '待处理',
    'in_progress': '进行中',
    'completed': '已完成',
    'skipped': '已跳过',
    'failed': '失败'
  };
  
  return statusNames[status] || status;
};

/**
 * 获取事件中文名称
 */
const getEventChineseName = (eventType: string): string => {
  const eventNames: Record<string, string> = {
    'production_started': '开始生产',
    'production_completed': '生产完成',
    'quality_check_passed': '质检通过',
    'packaging_completed': '包装完成',
    'shipment_started': '开始运输',
    'shipment_completed': '运输完成',
    'delivery_completed': '配送完成',
    'quality_issue': '质量问题',
    'certification_updated': '认证更新'
  };
  
  return eventNames[eventType] || eventType;
};