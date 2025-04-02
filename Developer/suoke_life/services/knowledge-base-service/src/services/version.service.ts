/**
 * 版本管理服务
 * 处理知识条目的版本控制
 */
import mongoose from 'mongoose';
import { diff as deepDiff } from 'deep-diff';
import { NotFoundError } from '../errors/not-found-error';
import { BadRequestError } from '../errors/bad-request-error';
import logger from '../utils/logger';
import VersionModel from '../models/version.model';
import KnowledgeModel from '../models/knowledge.model';
import NutritionModel from '../models/nutrition.model';
import LifestyleModel from '../models/lifestyle.model';
import MedicalModel from '../models/medical.model';
import TcmModel from '../models/tcm.model';
import EnvironmentalHealthModel from '../models/environmental-health.model';
import PsychologicalHealthModel from '../models/psychological-health.model';

export class VersionService {
  /**
   * 获取对应类型的模型
   * @param knowledgeType 知识类型
   * @returns 对应的模型
   */
  private getModelByType(knowledgeType: string): mongoose.Model<any> {
    switch (knowledgeType.toLowerCase()) {
      case 'knowledge':
        return KnowledgeModel;
      case 'nutrition':
        return NutritionModel;
      case 'lifestyle':
        return LifestyleModel;
      case 'medical':
        return MedicalModel;
      case 'tcm':
        return TcmModel;
      case 'environmental-health':
      case 'environmentalhealth':
        return EnvironmentalHealthModel;
      case 'mental-health':
      case 'mentalhealth':
      case 'psychological-health':
      case 'psychologicalhealth':
        return PsychologicalHealthModel;
      default:
        throw new BadRequestError(`未知的知识类型: ${knowledgeType}`);
    }
  }

  /**
   * 保存新版本
   * @param knowledgeType 知识类型
   * @param documentId 知识条目ID
   * @param data 版本数据
   * @param versionNumber 版本号
   * @param userId 用户ID
   */
  async saveVersion(
    knowledgeType: string,
    documentId: string,
    data: any,
    versionNumber: number,
    userId?: string
  ): Promise<void> {
    try {
      logger.info('保存新版本', { knowledgeType, documentId, versionNumber });
      
      // 创建版本记录
      const version = new VersionModel({
        knowledgeType,
        documentId,
        version: versionNumber,
        data: JSON.parse(JSON.stringify(data)), // 深拷贝数据
        createdBy: userId,
        createdAt: new Date()
      });
      
      await version.save();
      
      logger.info('版本保存成功', { knowledgeType, documentId, versionNumber });
    } catch (error) {
      logger.error('保存版本失败', { 
        error: (error as Error).message, 
        knowledgeType, 
        documentId, 
        versionNumber 
      });
      throw error;
    }
  }

  /**
   * 获取版本历史
   * @param knowledgeType 知识类型
   * @param documentId 知识条目ID
   * @returns 版本历史列表
   */
  async getVersionHistory(knowledgeType: string, documentId: string): Promise<any[]> {
    try {
      logger.info('获取版本历史', { knowledgeType, documentId });
      
      // 检查知识条目是否存在
      const model = this.getModelByType(knowledgeType);
      const document = await model.findById(documentId);
      
      if (!document) {
        throw new NotFoundError(`未找到${knowledgeType}知识条目`);
      }
      
      // 获取所有版本
      const versions = await VersionModel.find({ 
        knowledgeType, 
        documentId 
      }).sort({ version: -1 }).select('-data');
      
      // 添加当前版本
      const currentVersion = {
        _id: 'current',
        knowledgeType,
        documentId,
        version: document.version,
        createdBy: document.updatedBy || document.createdBy,
        createdAt: document.updatedAt,
        current: true
      };
      
      return [currentVersion, ...versions];
    } catch (error) {
      logger.error('获取版本历史失败', { error: (error as Error).message, knowledgeType, documentId });
      throw error;
    }
  }

  /**
   * 获取特定版本
   * @param knowledgeType 知识类型
   * @param documentId 知识条目ID
   * @param versionNumber 版本号
   * @returns 特定版本的知识条目
   */
  async getSpecificVersion(knowledgeType: string, documentId: string, versionNumber: number): Promise<any> {
    try {
      logger.info('获取特定版本', { knowledgeType, documentId, versionNumber });
      
      // 检查知识条目是否存在
      const model = this.getModelByType(knowledgeType);
      const document = await model.findById(documentId);
      
      if (!document) {
        throw new NotFoundError(`未找到${knowledgeType}知识条目`);
      }
      
      // 如果是当前版本，直接返回
      if (document.version === versionNumber) {
        return document;
      }
      
      // 获取特定版本
      const version = await VersionModel.findOne({ 
        knowledgeType, 
        documentId,
        version: versionNumber
      });
      
      if (!version) {
        throw new NotFoundError(`未找到版本 ${versionNumber}`);
      }
      
      return version.data;
    } catch (error) {
      logger.error('获取特定版本失败', { 
        error: (error as Error).message, 
        knowledgeType, 
        documentId, 
        versionNumber 
      });
      throw error;
    }
  }

  /**
   * 回滚到特定版本
   * @param knowledgeType 知识类型
   * @param documentId 知识条目ID
   * @param versionNumber 版本号
   * @param userId 用户ID
   * @returns 回滚后的知识条目
   */
  async rollbackToVersion(
    knowledgeType: string, 
    documentId: string, 
    versionNumber: number,
    userId?: string
  ): Promise<any> {
    try {
      logger.info('回滚到特定版本', { knowledgeType, documentId, versionNumber });
      
      // 检查知识条目是否存在
      const model = this.getModelByType(knowledgeType);
      const document = await model.findById(documentId);
      
      if (!document) {
        throw new NotFoundError(`未找到${knowledgeType}知识条目`);
      }
      
      // 如果是当前版本，无需回滚
      if (document.version === versionNumber) {
        throw new BadRequestError('无法回滚到当前版本');
      }
      
      // 获取要回滚到的版本
      const version = await VersionModel.findOne({ 
        knowledgeType, 
        documentId,
        version: versionNumber
      });
      
      if (!version) {
        throw new NotFoundError(`未找到版本 ${versionNumber}`);
      }
      
      // 保存当前版本
      await this.saveVersion(
        knowledgeType,
        documentId,
        document.toObject(),
        document.version,
        userId
      );
      
      // 回滚数据
      const rollbackData = version.data;
      
      // 保留ID和一些元数据
      rollbackData._id = document._id;
      rollbackData.version = document.version + 1;
      rollbackData.updatedAt = new Date();
      if (userId) {
        rollbackData.updatedBy = userId;
      }
      
      // 更新文档
      const updated = await model.findByIdAndUpdate(
        documentId,
        rollbackData,
        { new: true }
      );
      
      logger.info('成功回滚到版本', { knowledgeType, documentId, versionNumber });
      
      return updated;
    } catch (error) {
      logger.error('回滚到特定版本失败', { 
        error: (error as Error).message, 
        knowledgeType, 
        documentId, 
        versionNumber 
      });
      throw error;
    }
  }

  /**
   * 比较两个版本的差异
   * @param knowledgeType 知识类型
   * @param documentId 知识条目ID
   * @param fromVersion 起始版本
   * @param toVersion 目标版本
   * @returns 差异对象
   */
  async compareVersions(
    knowledgeType: string, 
    documentId: string, 
    fromVersion: number, 
    toVersion: number
  ): Promise<any> {
    try {
      logger.info('比较版本差异', { knowledgeType, documentId, fromVersion, toVersion });
      
      // 获取起始版本数据
      const fromData = await this.getSpecificVersion(knowledgeType, documentId, fromVersion);
      
      // 获取目标版本数据
      const toData = await this.getSpecificVersion(knowledgeType, documentId, toVersion);
      
      // 移除不需要比较的字段
      const cleanFromData = this.cleanDataForComparison(fromData);
      const cleanToData = this.cleanDataForComparison(toData);
      
      // 计算差异
      const differences = deepDiff(cleanFromData, cleanToData);
      
      return {
        fromVersion,
        toVersion,
        differences
      };
    } catch (error) {
      logger.error('比较版本差异失败', { 
        error: (error as Error).message, 
        knowledgeType, 
        documentId, 
        fromVersion, 
        toVersion 
      });
      throw error;
    }
  }

  /**
   * 清理数据以便比较
   * 移除_id, createdAt, updatedAt等字段
   * @param data 原始数据
   * @returns 清理后的数据
   */
  private cleanDataForComparison(data: any): any {
    const cleanData = JSON.parse(JSON.stringify(data));
    
    // 移除不需要比较的字段
    delete cleanData._id;
    delete cleanData.__v;
    delete cleanData.createdAt;
    delete cleanData.updatedAt;
    delete cleanData.createdBy;
    delete cleanData.updatedBy;
    
    return cleanData;
  }
}

export default new VersionService();