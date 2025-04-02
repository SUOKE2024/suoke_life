/**
 * 方言服务索引文件
 * 集成所有方言相关服务功能
 */

const sampleCollectionService = require('./sample-collection.service');
const modelTrainingService = require('./model-training.service');

/**
 * 方言服务
 * 包含方言样本收集、模型训练和方言识别/翻译功能
 */
const dialectService = {
  // 样本收集服务
  sample: {
    /**
     * 记录方言样本来源信息
     */
    recordSampleSource: sampleCollectionService.recordSampleSource,
    
    /**
     * 评估样本质量
     */
    evaluateSampleQuality: sampleCollectionService.evaluateSampleQuality,
    
    /**
     * 创建方言识别挑战活动
     */
    createDialectChallenge: sampleCollectionService.createDialectChallenge,
    
    /**
     * 获取特定方言的样本统计信息
     */
    getDialectSampleStats: sampleCollectionService.getDialectSampleStats,
    
    /**
     * 加入方言挑战活动
     */
    joinDialectChallenge: sampleCollectionService.joinDialectChallenge,
    
    /**
     * 更新方言样本统计信息
     */
    updateDialectSampleStats: sampleCollectionService.updateDialectSampleStats
  },
  
  // 模型训练服务
  training: {
    /**
     * 准备训练数据集
     */
    prepareTrainingData: modelTrainingService.prepareTrainingData,
    
    /**
     * 启动模型训练作业
     */
    startModelTraining: modelTrainingService.startModelTraining,
    
    /**
     * 获取训练作业状态
     */
    getTrainingStatus: modelTrainingService.getTrainingStatus,
    
    /**
     * 部署训练好的模型
     */
    deployModel: modelTrainingService.deployModel,
    
    /**
     * 评估已训练模型在指定测试集上的性能
     */
    evaluateModelPerformance: modelTrainingService.evaluateModelPerformance
  },
  
  /**
   * 指标跟踪
   */
  metrics: {
    incrementDialectSampleCounter: sampleCollectionService.incrementDialectSampleCounter
  }
};

module.exports = dialectService;