/**
 * AR宝藏图像识别服务
 * 提供高性能图像识别和检测功能
 */
const fs = require('fs');
const path = require('path');
const tf = require('@tensorflow/tfjs-node');
const sharp = require('sharp');
const crypto = require('crypto');
const logger = require('../utils/logger');
const { promisify } = require('util');
const readFileAsync = promisify(fs.readFile);
const Redis = require('redis');
const { getRedisClient } = require('../config/redis');

// 配置常量
const MODEL_PATH = path.resolve(__dirname, '../../data/models/treasure_recognition_model');
const CONFIDENCE_THRESHOLD = 0.65; // 置信度阈值
const IMAGE_SIZE = 224; // 模型输入图像大小
const CACHE_EXPIRY = 7 * 24 * 60 * 60; // 缓存过期时间：7天
const REFERENCE_IMAGES_DIR = path.resolve(__dirname, '../../data/reference_images');

// 类别映射
let classMapping = null;

// 模型实例
let model = null;
let modelLoading = false;
let modelLoadPromise = null;

/**
 * 加载类别映射文件
 * @returns {Promise<Object>} 类别映射对象
 */
const loadClassMapping = async () => {
  try {
    const mappingPath = path.join(MODEL_PATH, 'class_mapping.json');
    if (fs.existsSync(mappingPath)) {
      const data = fs.readFileSync(mappingPath, 'utf8');
      return JSON.parse(data);
    }
    
    // 如果映射文件不存在，返回默认空映射
    return {};
  } catch (error) {
    logger.error('加载类别映射失败:', error);
    return {};
  }
};

/**
 * 加载图像识别模型
 * @returns {Promise<tf.LayersModel>} 图像识别模型
 */
const loadModel = async () => {
  // 如果模型已加载，直接返回
  if (model) {
    return model;
  }
  
  // 如果模型正在加载，等待加载完成
  if (modelLoading) {
    return modelLoadPromise;
  }
  
  // 设置加载状态
  modelLoading = true;
  
  // 创建加载Promise
  modelLoadPromise = new Promise(async (resolve, reject) => {
    try {
      const startTime = Date.now();
      logger.info('开始加载图像识别模型...');
      
      // 加载模型
      const loadedModel = await tf.loadLayersModel(`file://${MODEL_PATH}/model.json`);
      
      // 预热模型
      const dummyInput = tf.zeros([1, IMAGE_SIZE, IMAGE_SIZE, 3]);
      loadedModel.predict(dummyInput);
      dummyInput.dispose();
      
      // 加载类别映射
      classMapping = await loadClassMapping();
      
      // 记录加载时间
      const loadTime = Date.now() - startTime;
      logger.info(`图像识别模型加载完成，耗时: ${loadTime}ms`);
      
      // 设置模型实例
      model = loadedModel;
      modelLoading = false;
      resolve(model);
    } catch (error) {
      logger.error('图像识别模型加载失败:', error);
      modelLoading = false;
      modelLoadPromise = null;
      reject(error);
    }
  });
  
  return modelLoadPromise;
};

/**
 * 预处理图像
 * @param {Buffer} imageBuffer - 图像缓冲区
 * @returns {Promise<Object>} 预处理结果
 */
const preprocessImage = async (imageBuffer) => {
  try {
    // 调整图像大小
    const resizedImageBuffer = await sharp(imageBuffer)
      .resize(IMAGE_SIZE, IMAGE_SIZE, {
        fit: 'cover',
        position: 'center'
      })
      .toBuffer();
    
    // 生成图像指纹
    const fingerprint = await generateImageFingerprint(imageBuffer);
    
    // 将Buffer转换为张量
    const tensor = tf.tidy(() => {
      // 解码图像
      const decodedImage = tf.node.decodeImage(resizedImageBuffer, 3);
      
      // 归一化图像
      const normalizedImage = decodedImage.div(255.0);
      
      // 添加批次维度
      return normalizedImage.expandDims(0);
    });
    
    return {
      tensor,
      fingerprint,
      width: IMAGE_SIZE,
      height: IMAGE_SIZE,
      originalMetadata: await sharp(imageBuffer).metadata()
    };
  } catch (error) {
    logger.error('图像预处理失败:', error);
    throw error;
  }
};

/**
 * 生成图像指纹
 * @param {Buffer} imageBuffer - 图像缓冲区
 * @returns {Promise<string>} 图像指纹
 */
const generateImageFingerprint = async (imageBuffer) => {
  try {
    // 生成图像的缩略图用于计算指纹
    const thumbnailBuffer = await sharp(imageBuffer)
      .resize(8, 8, { fit: 'cover' })
      .greyscale()
      .raw()
      .toBuffer();
    
    // 计算平均值
    let avg = 0;
    for (let i = 0; i < thumbnailBuffer.length; i++) {
      avg += thumbnailBuffer[i];
    }
    avg /= thumbnailBuffer.length;
    
    // 计算哈希值：比平均值大的设为1，小的设为0
    let fingerprintBits = '';
    for (let i = 0; i < thumbnailBuffer.length; i++) {
      fingerprintBits += thumbnailBuffer[i] >= avg ? '1' : '0';
    }
    
    // 将二进制字符串转换为十六进制字符串
    const fingerprint = crypto.createHash('md5').update(fingerprintBits).digest('hex');
    
    return fingerprint;
  } catch (error) {
    logger.warn('生成图像指纹失败:', error);
    
    // 返回基于当前时间的随机指纹
    return crypto.createHash('md5').update(`${Date.now()}-${Math.random()}`).digest('hex');
  }
};

/**
 * 从缓存获取识别结果
 * @param {string} fingerprint - 图像指纹
 * @returns {Promise<Object|null>} 缓存的结果或null
 */
const getCachedRecognitionResult = async (fingerprint) => {
  try {
    const redisClient = getRedisClient();
    const cacheKey = `image:recognition:${fingerprint}`;
    
    const cachedResult = await redisClient.get(cacheKey);
    if (cachedResult) {
      return JSON.parse(cachedResult);
    }
    
    return null;
  } catch (error) {
    logger.warn('获取缓存识别结果失败:', error);
    return null;
  }
};

/**
 * 缓存识别结果
 * @param {string} fingerprint - 图像指纹
 * @param {Object} result - 识别结果
 * @returns {Promise<boolean>} 是否成功
 */
const cacheRecognitionResult = async (fingerprint, result) => {
  try {
    const redisClient = getRedisClient();
    const cacheKey = `image:recognition:${fingerprint}`;
    
    await redisClient.set(cacheKey, JSON.stringify(result));
    await redisClient.expire(cacheKey, CACHE_EXPIRY);
    
    return true;
  } catch (error) {
    logger.warn('缓存识别结果失败:', error);
    return false;
  }
};

/**
 * 识别图像中的宝藏
 * @param {Buffer} imageBuffer - 图像缓冲区
 * @param {Object} options - 选项
 * @returns {Promise<Object>} 识别结果
 */
const recognizeTreasure = async (imageBuffer, options = {}) => {
  const startTime = Date.now();
  const {
    threshold = CONFIDENCE_THRESHOLD,
    useCache = true,
    returnTensor = false,
    enhancedAnalysis = false
  } = options;
  
  let tensor = null;
  let predictions = null;
  
  try {
    // 预处理图像
    const preprocessed = await preprocessImage(imageBuffer);
    tensor = preprocessed.tensor;
    
    // 尝试从缓存获取结果
    if (useCache) {
      const cachedResult = await getCachedRecognitionResult(preprocessed.fingerprint);
      if (cachedResult) {
        logger.debug(`使用缓存的识别结果: ${preprocessed.fingerprint}`);
        
        // 添加性能指标
        cachedResult.performance = {
          ...cachedResult.performance,
          totalTime: Date.now() - startTime,
          cached: true
        };
        
        return cachedResult;
      }
    }
    
    // 加载模型
    await loadModel();
    
    // 运行推理
    const inferenceStartTime = Date.now();
    predictions = model.predict(tensor);
    
    // 获取预测结果
    const probabilities = predictions.arraySync()[0];
    
    // 释放张量资源
    if (!returnTensor) {
      tensor.dispose();
      predictions.dispose();
    }
    
    // 处理预测结果
    const inferenceTime = Date.now() - inferenceStartTime;
    
    // 获取预测类别
    const topPredictions = getTopPredictions(probabilities, threshold);
    
    // 构建结果对象
    const result = {
      treasures: topPredictions.map(p => ({
        id: p.id,
        name: p.name,
        confidence: p.probability
      })),
      hasTreasure: topPredictions.length > 0,
      topMatch: topPredictions.length > 0 ? topPredictions[0] : null,
      imageInfo: {
        width: preprocessed.originalMetadata.width,
        height: preprocessed.originalMetadata.height,
        format: preprocessed.originalMetadata.format,
        fingerprint: preprocessed.fingerprint
      },
      performance: {
        inferenceTime,
        totalTime: Date.now() - startTime,
        cached: false
      }
    };
    
    // 增强分析
    if (enhancedAnalysis && topPredictions.length > 0) {
      const enhancedData = await enhanceResults(imageBuffer, topPredictions[0].id);
      result.enhancedData = enhancedData;
    }
    
    // 缓存结果
    if (useCache) {
      await cacheRecognitionResult(preprocessed.fingerprint, result);
    }
    
    logger.debug(`宝藏识别完成, 耗时: ${Date.now() - startTime}ms, 找到: ${topPredictions.length} 个宝藏`);
    
    return result;
  } catch (error) {
    // 释放资源
    if (tensor && !returnTensor) tensor.dispose();
    if (predictions && !returnTensor) predictions.dispose();
    
    logger.error('宝藏识别失败:', error);
    throw error;
  } finally {
    // 清理未释放的张量
    tf.disposeVariables();
  }
};

/**
 * 获取概率最高的预测结果
 * @param {Array<number>} probabilities - 预测概率数组
 * @param {number} threshold - 置信度阈值
 * @returns {Array<Object>} 排序后的预测结果
 */
const getTopPredictions = (probabilities, threshold) => {
  const predictions = [];
  
  // 遍历所有概率
  for (let i = 0; i < probabilities.length; i++) {
    const probability = probabilities[i];
    
    // 只保留超过阈值的预测
    if (probability >= threshold) {
      const className = classMapping[i] || `unknown_${i}`;
      predictions.push({
        id: i.toString(),
        name: className,
        probability: Math.round(probability * 100) / 100
      });
    }
  }
  
  // 按概率降序排序
  return predictions.sort((a, b) => b.probability - a.probability);
};

/**
 * 增强识别结果
 * @param {Buffer} imageBuffer - 原始图像
 * @param {string} treasureId - 宝藏ID
 * @returns {Promise<Object>} 增强数据
 */
const enhanceResults = async (imageBuffer, treasureId) => {
  try {
    // 这里可以添加额外的图像分析，例如：
    // - 物体定位
    // - 特征提取
    // - 附加属性分析
    
    return {
      location: await estimateObjectLocation(imageBuffer),
      additionalInfo: "可以添加关于宝藏的额外信息"
    };
  } catch (error) {
    logger.warn('增强识别结果失败:', error);
    return {};
  }
};

/**
 * 估计物体在图像中的位置
 * @param {Buffer} imageBuffer - 图像缓冲区
 * @returns {Promise<Object>} 物体位置
 */
const estimateObjectLocation = async (imageBuffer) => {
  try {
    // 简单实现：使用图像处理计算可能的物体位置
    const { width, height } = await sharp(imageBuffer).metadata();
    
    // 这里可以使用更复杂的算法定位物体
    // 简化实现返回图像中心
    return {
      x: Math.floor(width / 2),
      y: Math.floor(height / 2),
      width: Math.floor(width / 3),
      height: Math.floor(height / 3)
    };
  } catch (error) {
    logger.warn('估计物体位置失败:', error);
    return { x: 0, y: 0, width: 0, height: 0 };
  }
};

/**
 * 比较两个图像的相似度
 * @param {Buffer} image1 - 第一个图像
 * @param {Buffer} image2 - 第二个图像
 * @returns {Promise<number>} 相似度 (0-1)
 */
const compareImages = async (image1, image2) => {
  try {
    // 生成两个图像的指纹
    const fingerprint1 = await generateImageFingerprint(image1);
    const fingerprint2 = await generateImageFingerprint(image2);
    
    // 计算汉明距离 (两个哈希之间不同位的数量)
    const hammingDistance = calculateHammingDistance(fingerprint1, fingerprint2);
    
    // 将汉明距离转换为相似度 (0-1)
    // 对于32个字符的MD5哈希(128位)，最大汉明距离是128
    // 相似度 = 1 - 汉明距离/128
    const similarity = 1 - (hammingDistance / 128);
    
    return similarity;
  } catch (error) {
    logger.error('比较图像失败:', error);
    return 0;
  }
};

/**
 * 计算两个哈希值之间的汉明距离
 * @param {string} hash1 - 第一个哈希值
 * @param {string} hash2 - 第二个哈希值
 * @returns {number} 汉明距离
 */
const calculateHammingDistance = (hash1, hash2) => {
  let distance = 0;
  
  // 确保两个哈希值长度相同
  const len = Math.min(hash1.length, hash2.length);
  
  // 遍历每个字符
  for (let i = 0; i < len; i++) {
    // 每个十六进制字符代表4位二进制
    const binary1 = parseInt(hash1[i], 16).toString(2).padStart(4, '0');
    const binary2 = parseInt(hash2[i], 16).toString(2).padStart(4, '0');
    
    // 计算每一位的差异
    for (let j = 0; j < binary1.length; j++) {
      if (binary1[j] !== binary2[j]) {
        distance++;
      }
    }
  }
  
  return distance;
};

/**
 * 索引参考图像
 * @param {string} dirPath - 参考图像目录
 * @returns {Promise<Object>} 索引结果
 */
const indexReferenceImages = async (dirPath = REFERENCE_IMAGES_DIR) => {
  try {
    const startTime = Date.now();
    logger.info(`开始索引参考图像: ${dirPath}`);
    
    // 检查目录是否存在
    if (!fs.existsSync(dirPath)) {
      throw new Error(`参考图像目录不存在: ${dirPath}`);
    }
    
    // 获取所有图像文件
    const files = fs.readdirSync(dirPath)
      .filter(file => /\.(jpg|jpeg|png)$/i.test(file));
    
    logger.info(`找到 ${files.length} 个参考图像文件`);
    
    // 处理结果
    const results = {
      total: files.length,
      processed: 0,
      failed: 0,
      references: []
    };
    
    // 索引每个图像
    for (const file of files) {
      try {
        const filePath = path.join(dirPath, file);
        const imageBuffer = fs.readFileSync(filePath);
        
        // 识别图像
        const recognition = await recognizeTreasure(imageBuffer, {
          useCache: true,
          enhancedAnalysis: false
        });
        
        // 生成图像指纹
        const fingerprint = await generateImageFingerprint(imageBuffer);
        
        // 添加到索引
        results.references.push({
          filename: file,
          fingerprint,
          treasures: recognition.treasures,
          hasTreasure: recognition.hasTreasure
        });
        
        results.processed++;
      } catch (error) {
        logger.error(`索引参考图像失败: ${file}`, error);
        results.failed++;
      }
    }
    
    const totalTime = Date.now() - startTime;
    logger.info(`参考图像索引完成，耗时: ${totalTime}ms, 成功: ${results.processed}, 失败: ${results.failed}`);
    
    return results;
  } catch (error) {
    logger.error('索引参考图像失败:', error);
    throw error;
  }
};

/**
 * 清空图像识别缓存
 * @returns {Promise<boolean>} 是否成功
 */
const clearRecognitionCache = async () => {
  try {
    const redisClient = getRedisClient();
    const keys = await redisClient.keys('image:recognition:*');
    
    if (keys.length > 0) {
      await redisClient.del(keys);
      logger.info(`清空图像识别缓存，共 ${keys.length} 个键`);
    }
    
    return true;
  } catch (error) {
    logger.error('清空图像识别缓存失败:', error);
    return false;
  }
};

// 确保模型加载
loadModel().catch(err => logger.error('预加载图像识别模型失败:', err));

module.exports = {
  recognizeTreasure,
  compareImages,
  indexReferenceImages,
  clearRecognitionCache,
  generateImageFingerprint
}; 