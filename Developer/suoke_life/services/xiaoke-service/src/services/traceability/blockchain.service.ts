import axios from 'axios';
import crypto from 'crypto';
import { logger } from '../../utils/logger';
import { getCache, setCache } from '../../core/cache';
import { TraceabilityModel } from '../../models/traceability.model';

// 缓存配置
const BLOCKCHAIN_CACHE_TTL = 1800; // 30分钟

/**
 * 区块链集成服务
 * 提供溯源信息上链和验证功能
 */
export class BlockchainService {
  private blockchainApiUrl: string;
  private blockchainApiKey: string;

  constructor() {
    // 从环境变量获取区块链API配置
    this.blockchainApiUrl = process.env.BLOCKCHAIN_API_URL || 'https://api.blockchain.example.com';
    this.blockchainApiKey = process.env.BLOCKCHAIN_API_KEY || '';
  }

  /**
   * 上传溯源数据到区块链
   * @param traceabilityId 溯源ID
   */
  async uploadToBlockchain(traceabilityId: string): Promise<{
    success: boolean;
    transactionId?: string;
    blockNumber?: number;
    timestamp?: string;
    dataHash?: string;
    message?: string;
  }> {
    try {
      // 获取溯源信息
      const traceability = await TraceabilityModel.findOne({ traceabilityId }).lean();
      
      if (!traceability) {
        return { 
          success: false, 
          message: '溯源信息不存在' 
        };
      }

      // 准备需要记录到区块链的关键数据
      const blockchainData = {
        traceabilityId: traceability.traceabilityId,
        productId: traceability.productId,
        productName: traceability.productName,
        productCategory: traceability.productCategory,
        origin: {
          farmName: traceability.origin.farmName,
          location: traceability.origin.location,
          farmingType: traceability.origin.farmingType
        },
        harvestDate: traceability.harvestDate,
        productionStages: traceability.productionStages.map(stage => ({
          stageName: stage.stageName,
          startDate: stage.startDate,
          endDate: stage.endDate,
          location: stage.location,
          operators: stage.operators,
          processes: stage.processes
        })),
        timestamp: new Date()
      };

      // 计算数据哈希
      const dataHash = this.calculateDataHash(blockchainData);

      // 准备上链请求数据
      const requestData = {
        data: blockchainData,
        hash: dataHash,
        metadata: {
          source: 'xiaoke-service',
          type: 'traceability',
          version: '1.0'
        }
      };

      // 连接区块链API（模拟）
      // 实际应用中，这里应该连接真实的区块链API
      let response;
      
      // 检查是否有模拟模式环境变量
      if (process.env.BLOCKCHAIN_SIMULATION === 'true') {
        // 模拟区块链响应
        response = this.simulateBlockchainResponse(dataHash);
      } else {
        // 发送实际请求
        response = await axios.post(
          `${this.blockchainApiUrl}/transactions`, 
          requestData,
          {
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${this.blockchainApiKey}`
            }
          }
        );
      }

      if (!response.data.success) {
        logger.error('区块链上传失败:', response.data.message);
        return { 
          success: false, 
          message: response.data.message || '区块链服务错误' 
        };
      }

      // 记录区块链交易信息
      const blockchainRecord = {
        blockchainType: 'ethereum', // 或其他区块链类型
        transactionId: response.data.transactionId,
        blockNumber: response.data.blockNumber,
        timestamp: new Date(),
        dataHash: dataHash,
        verificationUrl: `${this.blockchainApiUrl}/verify/${response.data.transactionId}`
      };

      // 更新溯源记录中的区块链信息
      await TraceabilityModel.findOneAndUpdate(
        { traceabilityId },
        { 
          blockchainRecord,
          verificationStatus: 'verified'
        }
      );

      return { 
        success: true,
        transactionId: response.data.transactionId,
        blockNumber: response.data.blockNumber,
        timestamp: response.data.timestamp,
        dataHash: dataHash
      };
    } catch (error) {
      logger.error('上传到区块链失败:', error);
      return { 
        success: false, 
        message: error instanceof Error ? error.message : '区块链服务连接失败' 
      };
    }
  }

  /**
   * 验证区块链记录的完整性
   * @param transactionId 区块链交易ID
   */
  async verifyBlockchainRecord(transactionId: string): Promise<{
    verified: boolean;
    traceabilityId?: string;
    productName?: string;
    details?: any;
    message?: string;
  }> {
    try {
      // 尝试从缓存获取结果
      const cacheKey = `blockchain_verify:${transactionId}`;
      const cachedResult = await getCache<any>(cacheKey);
      
      if (cachedResult) {
        logger.debug(`从缓存获取区块链验证结果: ${transactionId}`);
        return cachedResult;
      }

      // 从数据库获取区块链记录
      const traceability = await TraceabilityModel.findOne({
        'blockchainRecord.transactionId': transactionId
      }).lean();
      
      if (!traceability) {
        return { 
          verified: false, 
          message: '未找到相关区块链记录' 
        };
      }

      // 获取区块链上的数据（模拟或实际API调用）
      let blockchainData;
      
      // 检查是否有模拟模式环境变量
      if (process.env.BLOCKCHAIN_SIMULATION === 'true') {
        // 模拟获取区块链数据
        blockchainData = this.simulateBlockchainData(transactionId, traceability);
      } else {
        // 从实际区块链获取数据
        const response = await axios.get(
          `${this.blockchainApiUrl}/transactions/${transactionId}`,
          {
            headers: {
              'Authorization': `Bearer ${this.blockchainApiKey}`
            }
          }
        );
        blockchainData = response.data;
      }

      if (!blockchainData.success) {
        return { 
          verified: false, 
          message: blockchainData.message || '获取区块链数据失败' 
        };
      }

      // 验证数据哈希是否匹配
      const savedHash = traceability.blockchainRecord.dataHash;
      const retrievedHash = blockchainData.data.hash;

      const isVerified = savedHash === retrievedHash;

      // 如果验证失败，更新验证状态
      if (!isVerified) {
        await TraceabilityModel.findOneAndUpdate(
          { 'blockchainRecord.transactionId': transactionId },
          { verificationStatus: 'failed' }
        );
      }

      // 准备验证结果
      const result = {
        verified: isVerified,
        traceabilityId: traceability.traceabilityId,
        productName: traceability.productName,
        details: {
          savedHash,
          retrievedHash,
          blockNumber: blockchainData.data.blockNumber,
          timestamp: blockchainData.data.timestamp
        },
        message: isVerified ? '验证成功' : '数据哈希不匹配，数据可能已被篡改'
      };

      // 更新缓存
      await setCache(cacheKey, result, BLOCKCHAIN_CACHE_TTL);

      return result;
    } catch (error) {
      logger.error('验证区块链记录失败:', error);
      return { 
        verified: false, 
        message: error instanceof Error ? error.message : '区块链验证服务错误' 
      };
    }
  }

  /**
   * 批量将未上链的溯源信息上传到区块链
   * @param limit 处理数量限制
   */
  async batchUploadToBlockchain(limit: number = 10): Promise<{
    success: boolean;
    processed: number;
    succeeded: number;
    failed: number;
    details: any[];
  }> {
    try {
      // 查找所有没有区块链记录的溯源信息
      const traceabilities = await TraceabilityModel.find({
        blockchainRecord: { $exists: false }
      })
      .limit(limit)
      .lean();
      
      if (!traceabilities.length) {
        return {
          success: true,
          processed: 0,
          succeeded: 0,
          failed: 0,
          details: []
        };
      }

      const results = [];
      let succeeded = 0;
      let failed = 0;

      // 逐个处理上链
      for (const traceability of traceabilities) {
        const result = await this.uploadToBlockchain(traceability.traceabilityId);
        
        if (result.success) {
          succeeded++;
        } else {
          failed++;
        }
        
        results.push({
          traceabilityId: traceability.traceabilityId,
          productName: traceability.productName,
          success: result.success,
          message: result.message,
          transactionId: result.transactionId
        });
      }

      return {
        success: true,
        processed: traceabilities.length,
        succeeded,
        failed,
        details: results
      };
    } catch (error) {
      logger.error('批量上链失败:', error);
      return {
        success: false,
        processed: 0,
        succeeded: 0,
        failed: 0,
        details: [{ message: error instanceof Error ? error.message : '批量上链服务错误' }]
      };
    }
  }

  /**
   * 计算数据哈希
   * @param data 需要哈希的数据
   */
  private calculateDataHash(data: any): string {
    // 序列化数据
    const serializedData = JSON.stringify(data);
    
    // 使用SHA-256生成哈希
    return crypto
      .createHash('sha256')
      .update(serializedData)
      .digest('hex');
  }

  /**
   * 模拟区块链响应（用于开发和测试环境）
   * @param dataHash 数据哈希
   */
  private simulateBlockchainResponse(dataHash: string): any {
    // 生成模拟的交易ID
    const transactionId = 'tx_' + crypto.randomBytes(16).toString('hex');
    
    // 生成模拟的区块号
    const blockNumber = Math.floor(Math.random() * 1000000) + 8000000;
    
    return {
      data: {
        success: true,
        transactionId,
        blockNumber,
        timestamp: new Date().toISOString(),
        message: '模拟区块链记录创建成功'
      }
    };
  }

  /**
   * 模拟获取区块链数据（用于开发和测试环境）
   * @param transactionId 交易ID
   * @param traceability 溯源数据
   */
  private simulateBlockchainData(transactionId: string, traceability: any): any {
    return {
      success: true,
      data: {
        transactionId,
        blockNumber: traceability.blockchainRecord.blockNumber,
        timestamp: traceability.blockchainRecord.timestamp,
        hash: traceability.blockchainRecord.dataHash
      }
    };
  }
}

export default new BlockchainService(); 