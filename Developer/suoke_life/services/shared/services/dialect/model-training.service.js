/**
 * 方言模型训练服务
 * 处理方言识别和翻译模型的训练、评估和部署
 */

const { Dialect, DialectSample } = require('../../models/dialect.model');
const logger = require('../../utils/logger');
const fs = require('fs');
const path = require('path');
const axios = require('axios');

// 环境变量
const MODEL_REGISTRY_PATH = process.env.MODEL_REGISTRY_PATH || '/models';
const TRAINING_FRAMEWORK = process.env.TRAINING_FRAMEWORK || 'pytorch';
const MAX_TRAINING_HOURS = parseInt(process.env.MAX_TRAINING_HOURS || '24', 10);
const MIN_SAMPLES_PER_DIALECT = parseInt(process.env.MIN_SAMPLES_PER_DIALECT || '500', 10);

// 训练作业状态跟踪
const trainingJobs = new Map();

/**
 * 准备训练数据集
 * @param {String} dialectCode - 方言代码
 * @returns {Promise<Object>} - 数据集信息
 */
const prepareTrainingData = async (dialectCode) => {
  try {
    // 获取方言信息
    const dialect = await Dialect.findOne({ code: dialectCode });
    if (!dialect) {
      throw new Error(`方言代码不存在: ${dialectCode}`);
    }
    
    // 检查样本数量是否足够
    const sampleCount = await DialectSample.countDocuments({
      dialectCode,
      verificationStatus: 'verified'
    });
    
    if (sampleCount < MIN_SAMPLES_PER_DIALECT) {
      throw new Error(`训练样本数量不足，至少需要 ${MIN_SAMPLES_PER_DIALECT} 个验证样本，当前只有 ${sampleCount} 个`);
    }
    
    // 创建数据集目录
    const datasetDir = path.join(
      MODEL_REGISTRY_PATH, 
      'datasets', 
      dialectCode,
      `v${new Date().toISOString().slice(0, 10).replace(/-/g, '')}`
    );
    
    if (!fs.existsSync(datasetDir)) {
      fs.mkdirSync(datasetDir, { recursive: true });
    }
    
    // 准备训练、验证和测试集
    const samples = await DialectSample.find({
      dialectCode,
      verificationStatus: 'verified'
    }).sort({ qualityScore: -1 });
    
    // 分割数据集 (70% 训练, 15% 验证, 15% 测试)
    const trainSize = Math.floor(sampleCount * 0.7);
    const valSize = Math.floor(sampleCount * 0.15);
    
    const trainSamples = samples.slice(0, trainSize);
    const valSamples = samples.slice(trainSize, trainSize + valSize);
    const testSamples = samples.slice(trainSize + valSize);
    
    // 生成数据集清单
    const writeDatasetManifest = (setName, setSamples) => {
      const manifestPath = path.join(datasetDir, `${setName}.json`);
      const manifest = {
        dialectCode,
        dialectName: dialect.name,
        samples: setSamples.map(sample => ({
          id: sample._id.toString(),
          audioUrl: sample.audioUrl,
          transcription: sample.transcription,
          standardTranslation: sample.standardTranslation,
          duration: sample.audioFeatures?.duration || 0,
          qualityScore: sample.qualityScore
        }))
      };
      
      fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2));
      return manifest.samples.length;
    };
    
    const trainCount = writeDatasetManifest('train', trainSamples);
    const valCount = writeDatasetManifest('val', valSamples);
    const testCount = writeDatasetManifest('test', testSamples);
    
    // 创建数据集元数据
    const metadataPath = path.join(datasetDir, 'metadata.json');
    const metadata = {
      dialectCode,
      dialectName: dialect.name,
      version: path.basename(datasetDir),
      createdAt: new Date().toISOString(),
      stats: {
        totalSamples: sampleCount,
        trainSamples: trainCount,
        valSamples: valCount,
        testSamples: testCount
      },
      region: dialect.region,
      features: dialect.features
    };
    
    fs.writeFileSync(metadataPath, JSON.stringify(metadata, null, 2));
    
    logger.info(`方言 ${dialectCode} 训练数据准备完成，共 ${sampleCount} 个样本`);
    
    return {
      success: true,
      dialectCode,
      datasetPath: datasetDir,
      stats: metadata.stats
    };
  } catch (error) {
    logger.error(`准备训练数据失败: ${error.message}`);
    throw new Error(`准备训练数据失败: ${error.message}`);
  }
};

/**
 * 启动模型训练作业
 * @param {Object} config - 训练配置
 * @returns {Promise<Object>} - 训练作业信息
 */
const startModelTraining = async (config) => {
  try {
    // 验证配置
    if (!config.dialectCode) {
      throw new Error('缺少方言代码');
    }
    
    // 准备训练数据
    const datasetInfo = await prepareTrainingData(config.dialectCode);
    
    // 创建训练作业ID
    const jobId = `train_${config.dialectCode}_${Date.now()}`;
    
    // 定义训练配置
    const trainingConfig = {
      jobId,
      dialectCode: config.dialectCode,
      modelType: config.modelType || 'speech_recognition', // speech_recognition 或 translation
      framework: TRAINING_FRAMEWORK,
      datasetPath: datasetInfo.datasetPath,
      hyperparams: {
        learningRate: config.learningRate || 0.001,
        batchSize: config.batchSize || 32,
        epochs: config.epochs || 50,
        earlyStoppingPatience: config.earlyStoppingPatience || 5,
        ...config.extraParams
      },
      maxTrainingHours: MAX_TRAINING_HOURS,
      startTime: new Date(),
      status: 'preparing',
      progress: 0,
      logs: ['初始化训练作业...']
    };
    
    // 存储训练作业状态
    trainingJobs.set(jobId, trainingConfig);
    
    // 创建模型目录
    const modelDir = path.join(
      MODEL_REGISTRY_PATH,
      'models',
      config.dialectCode,
      jobId
    );
    
    if (!fs.existsSync(modelDir)) {
      fs.mkdirSync(modelDir, { recursive: true });
    }
    
    // 保存训练配置
    fs.writeFileSync(
      path.join(modelDir, 'config.json'),
      JSON.stringify(trainingConfig, null, 2)
    );
    
    // 启动训练进程 (这里简化为异步调用训练脚本)
    setTimeout(() => {
      simulateTrainingProcess(jobId, modelDir, trainingConfig);
    }, 0);
    
    logger.info(`启动方言 ${config.dialectCode} 模型训练作业 ${jobId}`);
    
    return {
      success: true,
      jobId,
      dialectCode: config.dialectCode,
      status: 'preparing',
      modelType: trainingConfig.modelType,
      estimatedCompletionTime: new Date(Date.now() + MAX_TRAINING_HOURS * 60 * 60 * 1000)
    };
  } catch (error) {
    logger.error(`启动模型训练失败: ${error.message}`);
    throw new Error(`启动模型训练失败: ${error.message}`);
  }
};

/**
 * 模拟训练过程 (实际项目中应该调用真实的训练脚本或服务)
 * @param {String} jobId - 训练作业ID
 * @param {String} modelDir - 模型目录
 * @param {Object} config - 训练配置
 */
const simulateTrainingProcess = async (jobId, modelDir, config) => {
  try {
    // 更新作业状态
    trainingJobs.get(jobId).status = 'training';
    trainingJobs.get(jobId).logs.push('开始训练...');
    
    // 模拟训练过程
    const totalEpochs = config.hyperparams.epochs;
    const epochTime = 10 * 60 * 1000; // 10分钟/轮
    
    for (let epoch = 1; epoch <= totalEpochs; epoch++) {
      // 模拟每个epoch的训练
      await new Promise(resolve => setTimeout(resolve, 1000)); // 加速模拟
      
      // 计算模拟指标
      const loss = 0.5 * Math.exp(-0.1 * epoch);
      const accuracy = 0.5 + 0.4 * (1 - Math.exp(-0.15 * epoch));
      
      // 更新进度
      const progress = (epoch / totalEpochs) * 100;
      trainingJobs.get(jobId).progress = progress;
      trainingJobs.get(jobId).logs.push(
        `Epoch ${epoch}/${totalEpochs} - loss: ${loss.toFixed(4)}, accuracy: ${accuracy.toFixed(4)}`
      );
      
      // 每5个epoch保存一次日志
      if (epoch % 5 === 0 || epoch === totalEpochs) {
        fs.writeFileSync(
          path.join(modelDir, 'training_log.json'),
          JSON.stringify(trainingJobs.get(jobId), null, 2)
        );
      }
      
      // 模拟早停
      if (epoch > 10 && Math.random() < 0.1) {
        trainingJobs.get(jobId).logs.push('触发早停，训练结束');
        break;
      }
    }
    
    // 训练完成，评估模型
    trainingJobs.get(jobId).status = 'evaluating';
    trainingJobs.get(jobId).logs.push('训练完成，开始评估模型...');
    
    // 模拟评估过程
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // 生成模拟评估结果
    const evalResult = {
      wer: 0.15 + Math.random() * 0.1,  // 词错误率
      cer: 0.05 + Math.random() * 0.05, // 字错误率
      accuracy: 0.85 + Math.random() * 0.1,
      f1Score: 0.87 + Math.random() * 0.08
    };
    
    // 保存评估结果
    fs.writeFileSync(
      path.join(modelDir, 'eval_results.json'),
      JSON.stringify(evalResult, null, 2)
    );
    
    // 创建示例模型文件 (实际项目中应保存真实模型)
    fs.writeFileSync(
      path.join(modelDir, 'model.json'),
      JSON.stringify({ modelType: 'mock_model', createdAt: new Date() }, null, 2)
    );
    
    // 更新作业状态
    trainingJobs.get(jobId).status = 'completed';
    trainingJobs.get(jobId).endTime = new Date();
    trainingJobs.get(jobId).evalResults = evalResult;
    trainingJobs.get(jobId).logs.push('模型评估完成，训练作业结束');
    
    // 更新数据库中的方言模型信息
    await Dialect.updateOne(
      { code: config.dialectCode },
      { 
        $push: { 
          models: {
            version: jobId,
            accuracy: evalResult.accuracy,
            trainedAt: new Date(),
            parameters: config.hyperparams,
            performance: {
              wer: evalResult.wer,
              cer: evalResult.cer
            }
          } 
        },
        // 更新支持级别 (如果精度足够高)
        $max: {
          supportLevel: evalResult.accuracy > 0.9 ? 5 : 
                       evalResult.accuracy > 0.85 ? 4 :
                       evalResult.accuracy > 0.8 ? 3 :
                       evalResult.accuracy > 0.7 ? 2 : 1
        }
      }
    );
    
    // 保存最终日志
    fs.writeFileSync(
      path.join(modelDir, 'training_log.json'),
      JSON.stringify(trainingJobs.get(jobId), null, 2)
    );
    
    logger.info(`方言 ${config.dialectCode} 模型训练作业 ${jobId} 完成`);
  } catch (error) {
    // 处理训练失败
    trainingJobs.get(jobId).status = 'failed';
    trainingJobs.get(jobId).error = error.message;
    trainingJobs.get(jobId).logs.push(`训练失败: ${error.message}`);
    
    fs.writeFileSync(
      path.join(modelDir, 'training_log.json'),
      JSON.stringify(trainingJobs.get(jobId), null, 2)
    );
    
    logger.error(`方言 ${config.dialectCode} 模型训练失败: ${error.message}`);
  }
};

/**
 * 获取训练作业状态
 * @param {String} jobId - 训练作业ID
 * @returns {Promise<Object>} - 作业状态
 */
const getTrainingStatus = async (jobId) => {
  try {
    // 从内存中获取作业状态
    if (trainingJobs.has(jobId)) {
      const job = trainingJobs.get(jobId);
      return {
        jobId,
        dialectCode: job.dialectCode,
        status: job.status,
        progress: job.progress,
        startTime: job.startTime,
        endTime: job.endTime,
        evalResults: job.evalResults,
        logs: job.logs.slice(-10) // 只返回最近10条日志
      };
    }
    
    // 从文件系统获取作业状态
    const dialectCode = jobId.split('_')[1];
    const modelDir = path.join(
      MODEL_REGISTRY_PATH,
      'models',
      dialectCode,
      jobId
    );
    
    if (!fs.existsSync(modelDir)) {
      throw new Error(`训练作业 ${jobId} 不存在`);
    }
    
    const logPath = path.join(modelDir, 'training_log.json');
    if (!fs.existsSync(logPath)) {
      throw new Error(`训练作业 ${jobId} 日志不存在`);
    }
    
    const jobData = JSON.parse(fs.readFileSync(logPath, 'utf8'));
    return {
      jobId,
      dialectCode: jobData.dialectCode,
      status: jobData.status,
      progress: jobData.progress,
      startTime: jobData.startTime,
      endTime: jobData.endTime,
      evalResults: jobData.evalResults,
      logs: jobData.logs.slice(-10) // 只返回最近10条日志
    };
  } catch (error) {
    logger.error(`获取训练状态失败: ${error.message}`);
    throw new Error(`获取训练状态失败: ${error.message}`);
  }
};

/**
 * 部署训练好的模型
 * @param {String} modelId - 模型ID (通常是 jobId)
 * @param {String} environment - 部署环境 ('production', 'staging', 'dev')
 * @returns {Promise<Object>} - 部署状态
 */
const deployModel = async (modelId, environment) => {
  try {
    // 验证环境
    if (!['production', 'staging', 'dev'].includes(environment)) {
      throw new Error(`不支持的部署环境: ${environment}`);
    }
    
    // 获取模型信息
    const dialectCode = modelId.split('_')[1];
    const modelPath = path.join(
      MODEL_REGISTRY_PATH,
      'models',
      dialectCode,
      modelId
    );
    
    if (!fs.existsSync(modelPath)) {
      throw new Error(`模型 ${modelId} 不存在`);
    }
    
    // 检查评估结果
    const evalPath = path.join(modelPath, 'eval_results.json');
    if (!fs.existsSync(evalPath)) {
      throw new Error(`模型 ${modelId} 评估结果不存在`);
    }
    
    const evalResults = JSON.parse(fs.readFileSync(evalPath, 'utf8'));
    
    // 检查模型质量
    // 生产环境需要更高的质量标准
    if (environment === 'production' && evalResults.accuracy < 0.8) {
      throw new Error(`模型精度不足以部署到生产环境 (${evalResults.accuracy})`);
    }
    
    // 创建部署目录
    const deployPath = path.join(
      MODEL_REGISTRY_PATH,
      'deployed',
      environment,
      dialectCode
    );
    
    if (!fs.existsSync(deployPath)) {
      fs.mkdirSync(deployPath, { recursive: true });
    }
    
    // 模拟模型复制过程 (实际项目中可能需要格式转换等)
    const deploymentInfo = {
      modelId,
      dialectCode,
      environment,
      deployedAt: new Date().toISOString(),
      evalResults,
      sourcePath: modelPath,
      status: 'active'
    };
    
    // 保存部署信息
    fs.writeFileSync(
      path.join(deployPath, 'deployment.json'),
      JSON.stringify(deploymentInfo, null, 2)
    );
    
    // 创建符号链接 (或复制文件)
    fs.symlinkSync(
      path.join(modelPath, 'model.json'),
      path.join(deployPath, 'model.json'),
      'file'
    );
    
    // 更新数据库状态
    await Dialect.updateOne(
      { code: dialectCode, 'models.version': modelId },
      { 
        $set: { 
          'models.$.deployedTo': environment,
          'models.$.deployedAt': new Date()
        }
      }
    );
    
    logger.info(`模型 ${modelId} 已部署到 ${environment} 环境`);
    
    return {
      success: true,
      modelId,
      dialectCode,
      environment,
      deployedAt: deploymentInfo.deployedAt,
      evalResults
    };
  } catch (error) {
    logger.error(`部署模型失败: ${error.message}`);
    throw new Error(`部署模型失败: ${error.message}`);
  }
};

/**
 * 评估已训练模型在指定测试集上的性能
 * @param {String} modelId - 模型ID
 * @param {String} testSetPath - 测试集路径 (可选，默认使用模型训练时的测试集)
 * @returns {Promise<Object>} - 评估结果
 */
const evaluateModelPerformance = async (modelId, testSetPath = null) => {
  try {
    // 获取模型信息
    const dialectCode = modelId.split('_')[1];
    const modelPath = path.join(
      MODEL_REGISTRY_PATH,
      'models',
      dialectCode,
      modelId
    );
    
    if (!fs.existsSync(modelPath)) {
      throw new Error(`模型 ${modelId} 不存在`);
    }
    
    // 如果未指定测试集，使用默认的
    if (!testSetPath) {
      // 获取训练配置以找到数据集路径
      const configPath = path.join(modelPath, 'config.json');
      if (!fs.existsSync(configPath)) {
        throw new Error(`模型 ${modelId} 配置不存在`);
      }
      
      const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
      testSetPath = path.join(config.datasetPath, 'test.json');
    }
    
    if (!fs.existsSync(testSetPath)) {
      throw new Error(`测试集 ${testSetPath} 不存在`);
    }
    
    // 读取测试集
    const testSet = JSON.parse(fs.readFileSync(testSetPath, 'utf8'));
    
    // 模拟评估过程 (实际项目中应调用真实的评估脚本)
    logger.info(`开始评估模型 ${modelId} 在测试集上的性能`);
    
    // 模拟评估结果
    const evalResult = {
      wer: 0.15 + Math.random() * 0.1,  // 词错误率
      cer: 0.05 + Math.random() * 0.05, // 字错误率
      accuracy: 0.85 + Math.random() * 0.1,
      f1Score: 0.87 + Math.random() * 0.08,
      confusionMatrix: {
        // 模拟混淆矩阵
      },
      sampleResults: testSet.samples.slice(0, 5).map(sample => ({
        id: sample.id,
        reference: sample.transcription,
        hypothesis: simulateHypothesis(sample.transcription, evalResult.wer),
        wer: evalResult.wer + (Math.random() * 0.1 - 0.05)
      })),
      evaluatedAt: new Date().toISOString(),
      testSetPath
    };
    
    // 保存评估结果
    const evalOutputPath = path.join(
      modelPath, 
      `eval_${path.basename(testSetPath, '.json')}_${Date.now()}.json`
    );
    
    fs.writeFileSync(evalOutputPath, JSON.stringify(evalResult, null, 2));
    
    logger.info(`模型 ${modelId} 评估完成，结果保存在 ${evalOutputPath}`);
    
    return {
      success: true,
      modelId,
      dialectCode,
      evalResults: evalResult,
      evalPath: evalOutputPath
    };
  } catch (error) {
    logger.error(`评估模型性能失败: ${error.message}`);
    throw new Error(`评估模型性能失败: ${error.message}`);
  }
};

/**
 * 模拟生成带有错误的转写结果(用于测试)
 * @param {String} reference - 参考文本
 * @param {Number} wer - 目标词错误率
 * @returns {String} - 模拟生成的转写文本
 */
function simulateHypothesis(reference, wer) {
  const words = reference.split(' ');
  const errorCount = Math.round(words.length * wer);
  const result = [...words];
  
  // 随机替换、删除或插入单词来模拟错误
  for (let i = 0; i < errorCount; i++) {
    const errorType = Math.floor(Math.random() * 3); // 0=替换, 1=删除, 2=插入
    const pos = Math.floor(Math.random() * words.length);
    
    if (errorType === 0 && result[pos]) {
      // 替换
      result[pos] = result[pos].split('').sort(() => Math.random() - 0.5).join('');
    } else if (errorType === 1 && result[pos]) {
      // 删除
      result.splice(pos, 1);
    } else if (errorType === 2) {
      // 插入
      const randomWord = '新词' + Math.floor(Math.random() * 100);
      result.splice(pos, 0, randomWord);
    }
  }
  
  return result.join(' ');
}

module.exports = {
  prepareTrainingData,
  startModelTraining,
  getTrainingStatus,
  deployModel,
  evaluateModelPerformance
};