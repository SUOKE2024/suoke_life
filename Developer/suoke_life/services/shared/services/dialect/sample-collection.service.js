/**
 * 方言样本收集服务
 * 用于处理方言音频样本的采集、处理和管理
 */

const fs = require('fs');
const path = require('path');
const { Dialect, DialectSample, DialectChallenge } = require('../../models/dialect.model');
const logger = require('../../utils/logger');
const mongoose = require('mongoose');
const { createMetricsIncrementer } = require('../../utils/metrics');

// 创建指标计数器
const incrementDialectSampleCounter = createMetricsIncrementer('dialect_samples_total');

/**
 * 记录方言样本来源信息
 * @param {String} dialectCode - 方言代码
 * @param {Object} sourceInfo - 来源信息
 * @returns {Promise<Boolean>} - 操作是否成功
 */
const recordSampleSource = async (dialectCode, sourceInfo) => {
  try {
    // 验证方言是否存在
    const dialectExists = await Dialect.exists({ code: dialectCode });
    if (!dialectExists) {
      throw new Error(`方言代码不存在: ${dialectCode}`);
    }
    
    // 记录来源信息
    const result = await DialectSample.updateOne(
      { dialectCode },
      { 
        $push: { 
          sources: { 
            ...sourceInfo, 
            recordedAt: new Date() 
          } 
        } 
      },
      { upsert: true }
    );
    
    logger.info(`记录方言样本来源: ${dialectCode} - ${sourceInfo.method || '未知来源'}`);
    return true;
  } catch (error) {
    logger.error(`记录方言样本来源失败: ${error.message}`);
    return false;
  }
};

/**
 * 评估样本质量
 * @param {String} sampleId - 样本ID
 * @param {Object} audioFeatures - 音频特征
 * @returns {Promise<Object>} - 评估结果
 */
const evaluateSampleQuality = async (sampleId, audioFeatures) => {
  try {
    // 质量评分算法 - 将各指标归一化后加权平均
    const snrScore = Math.min(Math.max((audioFeatures.snr - 10) / 20, 0), 1) * 0.4;
    const durationScore = Math.min(Math.max((audioFeatures.duration - 3) / 17, 0), 1) * 0.2;
    const volumeScore = (1 - Math.abs(audioFeatures.volume - 0.7) / 0.7) * 0.2;
    const clarityScore = audioFeatures.speechClarity * 0.2;
    
    const qualityScore = snrScore + durationScore + volumeScore + clarityScore;
    
    // 保存评估结果
    const sample = await DialectSample.findByIdAndUpdate(
      sampleId, 
      { 
        qualityScore,
        verificationStatus: qualityScore > 0.7 ? 'verified' : 'pending',
        audioFeatures: {
          ...audioFeatures,
          processedAt: new Date()
        }
      },
      { new: true }
    );
    
    if (!sample) {
      throw new Error(`样本ID不存在: ${sampleId}`);
    }
    
    // 更新方言样本统计信息
    await updateDialectSampleStats(sample.dialectCode);
    
    logger.info(`样本质量评估完成: ${sampleId}, 得分: ${qualityScore.toFixed(2)}`);
    incrementDialectSampleCounter(audioFeatures.duration);
    
    return {
      id: sampleId,
      dialectCode: sample.dialectCode,
      qualityScore,
      status: qualityScore > 0.7 ? 'verified' : 'pending'
    };
  } catch (error) {
    logger.error(`样本质量评估失败: ${error.message}`);
    throw new Error(`样本质量评估失败: ${error.message}`);
  }
};

/**
 * 更新方言样本统计信息
 * @param {String} dialectCode - 方言代码
 * @returns {Promise<void>}
 */
const updateDialectSampleStats = async (dialectCode) => {
  try {
    const stats = await DialectSample.aggregate([
      { $match: { dialectCode } },
      { $group: {
        _id: '$verificationStatus',
        count: { $sum: 1 },
        totalDuration: { $sum: '$audioFeatures.duration' }
      }}
    ]);
    
    const sampleStats = {
      total: 0,
      verified: 0,
      pending: 0,
      duration: 0
    };
    
    stats.forEach(item => {
      sampleStats.total += item.count;
      if (item._id === 'verified') {
        sampleStats.verified = item.count;
      } else if (item._id === 'pending') {
        sampleStats.pending = item.count;
      }
      sampleStats.duration += item.totalDuration || 0;
    });
    
    await Dialect.updateOne(
      { code: dialectCode },
      { $set: { sampleStats } }
    );
    
    logger.debug(`更新方言 ${dialectCode} 样本统计: 总计${sampleStats.total}个样本`);
  } catch (error) {
    logger.error(`更新方言样本统计失败: ${error.message}`);
  }
};

/**
 * 创建方言识别挑战活动
 * @param {Object} config - 挑战配置
 * @returns {Promise<Object>} - 创建的挑战信息
 */
const createDialectChallenge = async (config) => {
  try {
    // 验证配置有效性
    if (new Date() > config.endDate) {
      throw new Error('结束日期不能早于当前日期');
    }
    
    if (!config.dialectCodes || config.dialectCodes.length === 0) {
      throw new Error('至少需要指定一种方言');
    }
    
    // 验证方言存在性
    const existingDialects = await Dialect.find({ 
      code: { $in: config.dialectCodes } 
    }).select('code');
    
    if (existingDialects.length !== config.dialectCodes.length) {
      const foundCodes = existingDialects.map(d => d.code);
      const missingCodes = config.dialectCodes.filter(code => !foundCodes.includes(code));
      throw new Error(`以下方言代码不存在: ${missingCodes.join(', ')}`);
    }
    
    // 创建挑战
    const challenge = new DialectChallenge({
      title: config.title,
      description: config.description,
      dialectCodes: config.dialectCodes,
      startDate: config.startDate,
      endDate: config.endDate,
      rewardPoints: config.rewardPoints,
      minSamplesRequired: config.minSamplesRequired || 1,
      qualityThreshold: config.qualityThreshold || 0.6,
      status: new Date() <= config.startDate ? 'upcoming' : 'active',
      participants: [],
      createdAt: new Date()
    });
    
    await challenge.save();
    
    logger.info(`创建方言挑战活动成功: ${config.title}, ID: ${challenge._id}`);
    
    return {
      id: challenge._id,
      title: config.title,
      status: challenge.status,
      dialectCodes: config.dialectCodes,
      startDate: config.startDate,
      endDate: config.endDate
    };
  } catch (error) {
    logger.error(`创建方言挑战活动失败: ${error.message}`);
    throw new Error(`创建方言挑战活动失败: ${error.message}`);
  }
};

/**
 * 获取特定方言的样本统计信息
 * @param {String} dialectCode - 方言代码
 * @returns {Promise<Object>} - 统计信息
 */
const getDialectSampleStats = async (dialectCode) => {
  try {
    const dialect = await Dialect.findOne({ code: dialectCode });
    if (!dialect) {
      throw new Error(`方言代码不存在: ${dialectCode}`);
    }
    
    const stats = await DialectSample.aggregate([
      { $match: { dialectCode } },
      { $group: {
        _id: '$verificationStatus',
        count: { $sum: 1 },
        avgQuality: { $avg: '$qualityScore' },
        totalDuration: { $sum: '$audioFeatures.duration' }
      }}
    ]);
    
    // 格式化结果
    const result = {
      dialectCode,
      dialectName: dialect.name,
      totalSamples: 0,
      verifiedSamples: 0,
      pendingSamples: 0,
      rejectedSamples: 0,
      averageQuality: 0,
      totalDuration: 0,
      supportLevel: dialect.supportLevel,
      hasTrainedModel: dialect.models && dialect.models.length > 0
    };
    
    let verifiedCount = 0;
    let verifiedQualitySum = 0;
    
    stats.forEach(item => {
      if (item._id === 'verified') {
        result.verifiedSamples = item.count;
        verifiedCount = item.count;
        verifiedQualitySum = item.avgQuality * item.count;
      } else if (item._id === 'pending') {
        result.pendingSamples = item.count;
      } else if (item._id === 'rejected') {
        result.rejectedSamples = item.count;
      }
      
      result.totalSamples += item.count;
      result.totalDuration += item.totalDuration || 0;
    });
    
    result.averageQuality = verifiedCount > 0 ? verifiedQualitySum / verifiedCount : 0;
    
    return result;
  } catch (error) {
    logger.error(`获取方言样本统计信息失败: ${error.message}`);
    throw new Error(`获取方言样本统计信息失败: ${error.message}`);
  }
};

/**
 * 加入方言挑战活动
 * @param {String} challengeId - 挑战ID
 * @param {String} userId - 用户ID
 * @returns {Promise<Object>} - 参与状态
 */
const joinDialectChallenge = async (challengeId, userId) => {
  try {
    const challenge = await DialectChallenge.findById(challengeId);
    if (!challenge) {
      throw new Error('挑战活动不存在');
    }
    
    if (challenge.status !== 'upcoming' && challenge.status !== 'active') {
      throw new Error('只能参加即将开始或进行中的挑战');
    }
    
    // 检查用户是否已参加
    const alreadyJoined = challenge.participants.some(
      p => p.userId.toString() === userId
    );
    
    if (alreadyJoined) {
      return {
        success: true,
        message: '您已经参加了此挑战',
        challengeId,
        title: challenge.title
      };
    }
    
    // 添加用户到参与者列表
    challenge.participants.push({
      userId: new mongoose.Types.ObjectId(userId),
      joinedAt: new Date(),
      submittedSamples: 0,
      acceptedSamples: 0,
      pointsEarned: 0
    });
    
    await challenge.save();
    
    logger.info(`用户 ${userId} 成功加入挑战活动 ${challengeId}`);
    
    return {
      success: true,
      message: '成功加入挑战活动',
      challengeId,
      title: challenge.title,
      dialectCodes: challenge.dialectCodes
    };
  } catch (error) {
    logger.error(`加入挑战活动失败: ${error.message}`);
    throw new Error(`加入挑战活动失败: ${error.message}`);
  }
};

module.exports = {
  recordSampleSource,
  evaluateSampleQuality,
  createDialectChallenge,
  getDialectSampleStats,
  joinDialectChallenge,
  updateDialectSampleStats,
  incrementDialectSampleCounter
};