import mongoose from 'mongoose';
import { logger } from '../../utils/logger';
import { getCache, setCache } from '../../core/cache';
import { TraceabilityModel } from '../../models/traceability.model';
import { ProductModel } from '../../models/product.model';
import { traceabilityQueryCounter, traceabilityVerificationGauge } from '../../core/metrics';
import * as crypto from 'crypto';

// 缓存配置
const TRACEABILITY_CACHE_TTL = parseInt(process.env.TRACEABILITY_CACHE_TTL || '3600', 10); // 默认1小时

// 溯源信息接口
export interface Traceability {
  id: string;
  traceabilityId: string;
  productId: string;
  productName: string;
  productCategory: string;
  batchId: string;
  origin: {
    farmName: string;
    farmerId: string;
    farmerName: string;
    location: string;
    coordinates?: {
      latitude: number;
      longitude: number;
    };
    farmingType: string;
    certifications: string[];
  };
  harvestDate: string;
  processingDate?: string;
  expiryDate?: string;
  productionStages: Array<{
    stageName: string;
    startDate: string;
    endDate?: string;
    location: string;
    operators: string[];
    processes: string[];
    inputs?: any[];
    qualityTests?: any[];
    notes?: string;
    media?: string[];
    metadata?: Record<string, any>;
  }>;
  logisticRecords: Array<{
    transportType: string;
    departureLocation: string;
    departureTime: string;
    arrivalLocation: string;
    arrivalTime?: string;
    carrier: string;
    temperature?: number;
    humidity?: number;
    trackingNumber?: string;
    status: string;
    notes?: string;
    metadata?: Record<string, any>;
  }>;
  blockchainRecord?: {
    blockchainType: string;
    transactionId: string;
    blockNumber?: number;
    timestamp: string;
    dataHash: string;
    verificationUrl?: string;
  };
  verificationStatus: string;
  qualityCertificates: string[];
  scanCount: number;
  isExpired: boolean;
  productionDuration?: number;
  metadata?: Record<string, any>;
  createdAt: string;
  updatedAt: string;
}

/**
 * 溯源服务类
 * 负责处理产品溯源链相关业务逻辑
 */
export class TraceabilityService {
  /**
   * 根据溯源ID获取溯源信息
   */
  async getTraceabilityById(traceabilityId: string): Promise<Traceability | null> {
    try {
      // 尝试从缓存获取
      const cacheKey = `traceability:${traceabilityId}`;
      const cachedTraceability = await getCache<Traceability>(cacheKey);
      
      if (cachedTraceability) {
        logger.debug(`从缓存获取溯源信息: ${traceabilityId}`);
        // 更新扫描计数（异步，不影响主流程）
        this.incrementScanCount(traceabilityId).catch(error => {
          logger.error(`更新扫描计数失败: ${error.message}`);
        });
        
        // 更新指标
        traceabilityQueryCounter.inc({ 
          product_category: cachedTraceability.productCategory, 
          source: 'cache', 
          result: 'success' 
        });
        
        return cachedTraceability;
      }
      
      // 从数据库获取
      const traceability = await TraceabilityModel.findOne({ 
        traceabilityId 
      }).lean();
      
      if (!traceability) {
        logger.debug(`溯源信息不存在: ${traceabilityId}`);
        
        // 更新指标
        traceabilityQueryCounter.inc({ 
          product_category: 'unknown', 
          source: 'database', 
          result: 'not_found' 
        });
        
        return null;
      }
      
      // 更新扫描计数
      await this.incrementScanCount(traceabilityId);
      
      // 转换为Traceability类型
      const traceabilityInfo: Traceability = {
        id: traceability._id.toString(),
        traceabilityId: traceability.traceabilityId,
        productId: traceability.productId,
        productName: traceability.productName,
        productCategory: traceability.productCategory,
        batchId: traceability.batchId,
        origin: traceability.origin,
        harvestDate: traceability.harvestDate.toISOString(),
        processingDate: traceability.processingDate?.toISOString(),
        expiryDate: traceability.expiryDate?.toISOString(),
        productionStages: traceability.productionStages.map(stage => ({
          ...stage,
          startDate: stage.startDate.toISOString(),
          endDate: stage.endDate?.toISOString()
        })),
        logisticRecords: traceability.logisticRecords.map(record => ({
          ...record,
          departureTime: record.departureTime.toISOString(),
          arrivalTime: record.arrivalTime?.toISOString()
        })),
        blockchainRecord: traceability.blockchainRecord ? {
          ...traceability.blockchainRecord,
          timestamp: traceability.blockchainRecord.timestamp.toISOString()
        } : undefined,
        verificationStatus: traceability.verificationStatus,
        qualityCertificates: traceability.qualityCertificates,
        scanCount: traceability.scanCount + 1, // 因为我们已经更新了扫描计数
        isExpired: traceability.expiryDate ? new Date() > traceability.expiryDate : false,
        productionDuration: this.calculateProductionDuration(traceability.productionStages),
        metadata: traceability.metadata,
        createdAt: traceability.createdAt.toISOString(),
        updatedAt: traceability.updatedAt.toISOString()
      };
      
      // 更新缓存
      await setCache(cacheKey, traceabilityInfo, TRACEABILITY_CACHE_TTL);
      
      // 更新指标
      traceabilityQueryCounter.inc({ 
        product_category: traceabilityInfo.productCategory, 
        source: 'database', 
        result: 'success' 
      });
      
      return traceabilityInfo;
    } catch (error) {
      logger.error(`获取溯源信息失败:`, error);
      
      // 更新指标
      traceabilityQueryCounter.inc({ 
        product_category: 'unknown', 
        source: 'database', 
        result: 'error' 
      });
      
      throw error;
    }
  }

  /**
   * 根据产品ID获取溯源信息
   */
  async getTraceabilityByProductId(productId: string): Promise<Traceability | null> {
    try {
      // 从数据库获取
      const traceability = await TraceabilityModel.findOne({ 
        productId 
      }).lean();
      
      if (!traceability) {
        logger.debug(`产品溯源信息不存在: ${productId}`);
        return null;
      }
      
      // 递增扫描计数
      await this.incrementScanCount(traceability.traceabilityId);
      
      // 转换为Traceability类型
      const traceabilityInfo: Traceability = {
        id: traceability._id.toString(),
        traceabilityId: traceability.traceabilityId,
        productId: traceability.productId,
        productName: traceability.productName,
        productCategory: traceability.productCategory,
        batchId: traceability.batchId,
        origin: traceability.origin,
        harvestDate: traceability.harvestDate.toISOString(),
        processingDate: traceability.processingDate?.toISOString(),
        expiryDate: traceability.expiryDate?.toISOString(),
        productionStages: traceability.productionStages.map(stage => ({
          ...stage,
          startDate: stage.startDate.toISOString(),
          endDate: stage.endDate?.toISOString()
        })),
        logisticRecords: traceability.logisticRecords.map(record => ({
          ...record,
          departureTime: record.departureTime.toISOString(),
          arrivalTime: record.arrivalTime?.toISOString()
        })),
        blockchainRecord: traceability.blockchainRecord ? {
          ...traceability.blockchainRecord,
          timestamp: traceability.blockchainRecord.timestamp.toISOString()
        } : undefined,
        verificationStatus: traceability.verificationStatus,
        qualityCertificates: traceability.qualityCertificates,
        scanCount: traceability.scanCount + 1, // 因为我们已经更新了扫描计数
        isExpired: traceability.expiryDate ? new Date() > traceability.expiryDate : false,
        productionDuration: this.calculateProductionDuration(traceability.productionStages),
        metadata: traceability.metadata,
        createdAt: traceability.createdAt.toISOString(),
        updatedAt: traceability.updatedAt.toISOString()
      };
      
      // 更新缓存
      const cacheKey = `traceability:${traceability.traceabilityId}`;
      await setCache(cacheKey, traceabilityInfo, TRACEABILITY_CACHE_TTL);
      
      // 更新指标
      traceabilityQueryCounter.inc({ 
        product_category: traceabilityInfo.productCategory, 
        source: 'database', 
        result: 'success' 
      });
      
      return traceabilityInfo;
    } catch (error) {
      logger.error(`获取产品溯源信息失败:`, error);
      
      // 更新指标
      traceabilityQueryCounter.inc({ 
        product_category: 'unknown', 
        source: 'database', 
        result: 'error' 
      });
      
      throw error;
    }
  }

  /**
   * 创建新的溯源信息
   */
  async createTraceability(traceabilityData: Omit<Traceability, 'id' | 'traceabilityId' | 'isExpired' | 'productionDuration' | 'scanCount' | 'createdAt' | 'updatedAt'>): Promise<Traceability> {
    const session = await mongoose.startSession();
    session.startTransaction();

    try {
      // 验证产品存在
      const product = await ProductModel.findById(traceabilityData.productId).session(session);
      if (!product) {
        throw new Error(`产品不存在: ${traceabilityData.productId}`);
      }

      // 准备数据
      const preparedData = {
        ...traceabilityData,
        harvestDate: new Date(traceabilityData.harvestDate),
        processingDate: traceabilityData.processingDate ? new Date(traceabilityData.processingDate) : undefined,
        expiryDate: traceabilityData.expiryDate ? new Date(traceabilityData.expiryDate) : undefined,
        productionStages: traceabilityData.productionStages.map(stage => ({
          ...stage,
          startDate: new Date(stage.startDate),
          endDate: stage.endDate ? new Date(stage.endDate) : undefined
        })),
        logisticRecords: traceabilityData.logisticRecords.map(record => ({
          ...record,
          departureTime: new Date(record.departureTime),
          arrivalTime: record.arrivalTime ? new Date(record.arrivalTime) : undefined
        })),
        blockchainRecord: traceabilityData.blockchainRecord ? {
          ...traceabilityData.blockchainRecord,
          timestamp: new Date(traceabilityData.blockchainRecord.timestamp)
        } : undefined,
        scanCount: 0
      };

      // 创建溯源记录
      const traceability = await TraceabilityModel.create([preparedData], { session });
      
      // 更新产品记录
      await ProductModel.findByIdAndUpdate(
        traceabilityData.productId,
        { 
          traceabilityId: traceability[0].traceabilityId,
          blockchainVerified: traceabilityData.blockchainRecord ? true : false
        },
        { session }
      );

      await session.commitTransaction();
      session.endSession();

      // 转换为Traceability类型
      const createdTraceability = traceability[0];
      const result: Traceability = {
        id: createdTraceability._id.toString(),
        traceabilityId: createdTraceability.traceabilityId,
        productId: createdTraceability.productId,
        productName: createdTraceability.productName,
        productCategory: createdTraceability.productCategory,
        batchId: createdTraceability.batchId,
        origin: createdTraceability.origin,
        harvestDate: createdTraceability.harvestDate.toISOString(),
        processingDate: createdTraceability.processingDate?.toISOString(),
        expiryDate: createdTraceability.expiryDate?.toISOString(),
        productionStages: createdTraceability.productionStages.map(stage => ({
          ...stage,
          startDate: stage.startDate.toISOString(),
          endDate: stage.endDate?.toISOString()
        })),
        logisticRecords: createdTraceability.logisticRecords.map(record => ({
          ...record,
          departureTime: record.departureTime.toISOString(),
          arrivalTime: record.arrivalTime?.toISOString()
        })),
        blockchainRecord: createdTraceability.blockchainRecord ? {
          ...createdTraceability.blockchainRecord,
          timestamp: createdTraceability.blockchainRecord.timestamp.toISOString()
        } : undefined,
        verificationStatus: createdTraceability.verificationStatus,
        qualityCertificates: createdTraceability.qualityCertificates,
        scanCount: createdTraceability.scanCount,
        isExpired: createdTraceability.expiryDate ? new Date() > createdTraceability.expiryDate : false,
        productionDuration: this.calculateProductionDuration(createdTraceability.productionStages),
        metadata: createdTraceability.metadata,
        createdAt: createdTraceability.createdAt.toISOString(),
        updatedAt: createdTraceability.updatedAt.toISOString()
      };

      // 更新指标
      traceabilityVerificationGauge.set(
        { product_category: createdTraceability.productCategory, status: createdTraceability.verificationStatus },
        1
      );

      return result;
    } catch (error) {
      await session.abortTransaction();
      session.endSession();
      logger.error('创建溯源信息失败:', error);
      throw error;
    }
  }

  /**
   * 验证区块链溯源信息
   */
  async verifyBlockchainRecord(transactionId: string): Promise<{ verified: boolean; message: string; data?: any }> {
    try {
      // 查找具有该交易ID的溯源记录
      const traceability = await TraceabilityModel.findOne({ 
        'blockchainRecord.transactionId': transactionId 
      });
      
      if (!traceability) {
        return { 
          verified: false, 
          message: '找不到对应的溯源记录' 
        };
      }
      
      // 这里应该有实际的区块链验证逻辑
      // 为了演示，我们假设通过哈希比较来验证
      if (!traceability.blockchainRecord) {
        return { 
          verified: false, 
          message: '溯源记录缺少区块链信息' 
        };
      }
      
      // 计算当前数据的哈希值（为简化起见，仅使用部分字段）
      const dataToHash = {
        productId: traceability.productId,
        productName: traceability.productName,
        batchId: traceability.batchId,
        harvestDate: traceability.harvestDate
      };
      
      const currentHash = crypto
        .createHash('sha256')
        .update(JSON.stringify(dataToHash))
        .digest('hex');
      
      // 比较哈希值
      const storedHash = traceability.blockchainRecord.dataHash;
      const isVerified = currentHash === storedHash;
      
      // 更新验证状态
      const newStatus = isVerified ? 'verified' : 'failed';
      await TraceabilityModel.findByIdAndUpdate(
        traceability._id,
        { verificationStatus: newStatus }
      );
      
      // 清除缓存
      const cacheKey = `traceability:${traceability.traceabilityId}`;
      await setCache(cacheKey, null, 1);
      
      // 更新指标
      traceabilityVerificationGauge.set(
        { product_category: traceability.productCategory, status: newStatus },
        1
      );
      
      return {
        verified: isVerified,
        message: isVerified ? '溯源信息验证成功' : '溯源信息验证失败，数据已被篡改',
        data: {
          traceabilityId: traceability.traceabilityId,
          productName: traceability.productName,
          verificationStatus: newStatus,
          timestamp: new Date().toISOString()
        }
      };
    } catch (error) {
      logger.error(`验证区块链记录失败:`, error);
      throw error;
    }
  }

  /**
   * 获取溯源统计信息
   */
  async getTraceabilityStats(): Promise<{
    totalRecords: number;
    verifiedRecords: number;
    pendingRecords: number;
    failedRecords: number;
    categoryCounts: Record<string, number>;
    originCounts: Record<string, number>;
  }> {
    try {
      // 获取总记录数
      const totalRecords = await TraceabilityModel.countDocuments();
      
      // 获取各状态记录数
      const verifiedRecords = await TraceabilityModel.countDocuments({ verificationStatus: 'verified' });
      const pendingRecords = await TraceabilityModel.countDocuments({ verificationStatus: 'pending' });
      const failedRecords = await TraceabilityModel.countDocuments({ verificationStatus: 'failed' });
      
      // 获取各类别记录数
      const categoryAggregation = await TraceabilityModel.aggregate([
        { 
          $group: { 
            _id: '$productCategory', 
            count: { $sum: 1 } 
          } 
        }
      ]);
      
      const categoryCounts: Record<string, number> = {};
      categoryAggregation.forEach(item => {
        categoryCounts[item._id] = item.count;
      });
      
      // 获取各产地记录数
      const originAggregation = await TraceabilityModel.aggregate([
        { 
          $group: { 
            _id: '$origin.location', 
            count: { $sum: 1 } 
          } 
        }
      ]);
      
      const originCounts: Record<string, number> = {};
      originAggregation.forEach(item => {
        originCounts[item._id] = item.count;
      });
      
      return {
        totalRecords,
        verifiedRecords,
        pendingRecords,
        failedRecords,
        categoryCounts,
        originCounts
      };
    } catch (error) {
      logger.error(`获取溯源统计信息失败:`, error);
      throw error;
    }
  }

  /**
   * 递增扫描计数
   * @private
   */
  private async incrementScanCount(traceabilityId: string): Promise<void> {
    await TraceabilityModel.findOneAndUpdate(
      { traceabilityId },
      { $inc: { scanCount: 1 } }
    );
  }

  /**
   * 计算生产时间周期
   * @private
   */
  private calculateProductionDuration(stages: any[]): number | undefined {
    if (!stages || stages.length === 0) return undefined;
    
    const firstStage = stages[0];
    const lastStage = stages[stages.length - 1];
    
    if (!firstStage.startDate || !lastStage.endDate) return undefined;
    
    const startDate = new Date(firstStage.startDate);
    const endDate = new Date(lastStage.endDate);
    
    return (endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24); // 返回天数
  }
}

// 创建单例实例
export default new TraceabilityService(); 