/**
 * AR障碍物检测服务
 * 提供实时环境感知和障碍物识别功能
 */
const sharp = require('sharp');
const cv = require('opencv4nodejs');
const tf = require('@tensorflow/tfjs-node');
const logger = require('../../utils/logger');
const { getRedisClient } = require('../../config/redis');
const path = require('path');
const fs = require('fs');

// 缓存配置
const DETECTION_CACHE_TTL = 60; // 结果缓存60秒
const MODEL_CACHE_KEY = 'ar:obstacle:model'; // 模型缓存键

// 检测配置
const DEFAULT_CONFIG = {
  confidenceThreshold: 0.65,  // 最低置信度
  iouThreshold: 0.5,         // 非最大抑制IOU阈值
  deviceMemoryThreshold: 4,  // 设备内存阈值(GB)，低于此值使用优化模型
  maxDetections: 20,         // 最大检测数量
  imageSize: 416,            // 模型输入大小
  useCache: true             // 是否使用缓存
};

// 障碍物类型
const OBSTACLE_TYPES = {
  CORN_STALK: 'corn_stalk',        // 玉米秸秆
  ROCK: 'rock',                    // 石头
  WATER: 'water',                  // 水坑
  FALLEN_BRANCH: 'fallen_branch',  // 倒下的树枝
  FENCE: 'fence',                  // 围栏
  HOLE: 'hole',                    // 坑洞
  PERSON: 'person'                 // 人
};

// 模型路径
const MODEL_PATHS = {
  standard: path.resolve(__dirname, '../../../data/models/obstacle_detection_full.json'),
  optimized: path.resolve(__dirname, '../../../data/models/obstacle_detection_optimized.json')
};

// 类别映射
const CLASS_MAPPING = [
  OBSTACLE_TYPES.CORN_STALK,
  OBSTACLE_TYPES.ROCK,
  OBSTACLE_TYPES.WATER,
  OBSTACLE_TYPES.FALLEN_BRANCH,
  OBSTACLE_TYPES.FENCE,
  OBSTACLE_TYPES.HOLE,
  OBSTACLE_TYPES.PERSON
];

// 模型实例
let model = null;
let isModelLoading = false;
let modelLoadPromise = null;

/**
 * 加载障碍物检测模型
 * @param {Boolean} useOptimized - 是否使用优化模型
 * @returns {Promise<Object>} TensorFlow模型
 */
const loadModel = async (useOptimized = false) => {
  // 如果模型已经在加载，则返回加载Promise
  if (isModelLoading) {
    return modelLoadPromise;
  }
  
  // 如果模型已加载，直接返回
  if (model) {
    return model;
  }
  
  // 设置加载状态
  isModelLoading = true;
  
  try {
    const startTime = Date.now();
    logger.info(`开始加载${useOptimized ? '优化' : '标准'}障碍物检测模型...`);
    
    // 创建加载Promise
    modelLoadPromise = new Promise(async (resolve, reject) => {
      try {
        // 选择模型路径
        const modelPath = useOptimized ? MODEL_PATHS.optimized : MODEL_PATHS.standard;
        
        // 检查模型文件是否存在
        if (!fs.existsSync(modelPath)) {
          throw new Error(`模型文件不存在: ${modelPath}`);
        }
        
        // 加载模型
        const loadedModel = await tf.loadLayersModel(`file://${modelPath}`);
        
        // 预热模型 - 运行一次推理以初始化内部状态
        const dummyInput = tf.zeros([1, DEFAULT_CONFIG.imageSize, DEFAULT_CONFIG.imageSize, 3]);
        loadedModel.predict(dummyInput);
        dummyInput.dispose();
        
        // 记录加载时间
        const loadTime = Date.now() - startTime;
        logger.info(`障碍物检测模型加载完成，耗时: ${loadTime}ms`);
        
        // 设置加载完成状态
        model = loadedModel;
        isModelLoading = false;
        modelLoadPromise = null;
        
        resolve(model);
      } catch (error) {
        logger.error('障碍物检测模型加载失败:', error);
        isModelLoading = false;
        modelLoadPromise = null;
        reject(error);
      }
    });
    
    return modelLoadPromise;
  } catch (error) {
    logger.error('障碍物检测模型加载失败:', error);
    isModelLoading = false;
    modelLoadPromise = null;
    throw error;
  }
};

/**
 * 获取设备可用内存
 * @returns {Number} 可用内存(GB)
 */
const getAvailableMemory = () => {
  try {
    // Node.js中获取可用内存
    const freeMem = process.memoryUsage().heapTotal / (1024 * 1024 * 1024);
    return Math.round(freeMem * 10) / 10;
  } catch (error) {
    logger.warn('获取内存信息失败:', error);
    return 8; // 假设默认8GB
  }
};

/**
 * 预处理图像
 * @param {Buffer} imageBuffer - 图像缓冲区
 * @returns {Promise<Object>} 预处理结果
 */
const preprocessImage = async (imageBuffer) => {
  try {
    const startTime = Date.now();
    
    // 使用Sharp调整图像大小
    const resizedImageBuffer = await sharp(imageBuffer)
      .resize(DEFAULT_CONFIG.imageSize, DEFAULT_CONFIG.imageSize, {
        fit: 'cover',
        position: 'center'
      })
      .toBuffer();
    
    // 计算图像指纹(用于缓存)
    const hash = await sharp(imageBuffer)
      .resize(8, 8)
      .grayscale()
      .raw()
      .toBuffer();
    
    // 转换为二进制指纹
    let imageFingerprint = '';
    for (let i = 0; i < hash.length - 1; i++) {
      imageFingerprint += hash[i] < hash[i + 1] ? '1' : '0';
    }
    
    // 创建TensorFlow张量
    const tensor = tf.tidy(() => {
      // 解码图像
      const decodedImage = tf.node.decodeImage(resizedImageBuffer, 3);
      
      // 归一化到[0,1]
      const normalizedImage = decodedImage.div(255.0);
      
      // 扩展批次维度
      return normalizedImage.expandDims(0);
    });
    
    const preprocessTime = Date.now() - startTime;
    logger.debug(`图像预处理完成，耗时: ${preprocessTime}ms`);
    
    return {
      tensor,
      width: DEFAULT_CONFIG.imageSize,
      height: DEFAULT_CONFIG.imageSize,
      originalWidth: (await sharp(imageBuffer).metadata()).width,
      originalHeight: (await sharp(imageBuffer).metadata()).height,
      fingerprint: imageFingerprint,
      preprocessTime
    };
  } catch (error) {
    logger.error('图像预处理失败:', error);
    throw error;
  }
};

/**
 * 在Redis中获取缓存的检测结果
 * @param {String} fingerprint - 图像指纹
 * @returns {Promise<Object|null>} 缓存的结果或null
 */
const getCachedDetection = async (fingerprint) => {
  try {
    const redisClient = getRedisClient();
    const cacheKey = `ar:obstacle:${fingerprint}`;
    
    const cachedResult = await redisClient.get(cacheKey);
    if (cachedResult) {
      return JSON.parse(cachedResult);
    }
    
    return null;
  } catch (error) {
    logger.warn('获取缓存检测结果失败:', error);
    return null;
  }
};

/**
 * 将检测结果存入缓存
 * @param {String} fingerprint - 图像指纹
 * @param {Object} result - 检测结果
 * @returns {Promise<Boolean>} 是否成功
 */
const cacheDetectionResult = async (fingerprint, result) => {
  try {
    const redisClient = getRedisClient();
    const cacheKey = `ar:obstacle:${fingerprint}`;
    
    await redisClient.set(cacheKey, JSON.stringify(result));
    await redisClient.expire(cacheKey, DETECTION_CACHE_TTL);
    
    return true;
  } catch (error) {
    logger.warn('缓存检测结果失败:', error);
    return false;
  }
};

/**
 * 在图像中检测障碍物
 * @param {Buffer} imageBuffer - 图像缓冲区
 * @param {Object} options - 检测选项
 * @returns {Promise<Object>} 检测结果
 */
const detectObstacles = async (imageBuffer, options = {}) => {
  const config = { ...DEFAULT_CONFIG, ...options };
  const startTime = Date.now();
  let detectionSource = 'realtime';
  
  try {
    // 预处理图像
    const preprocessed = await preprocessImage(imageBuffer);
    
    // 检查缓存
    if (config.useCache) {
      const cachedResult = await getCachedDetection(preprocessed.fingerprint);
      if (cachedResult) {
        // 添加性能指标
        cachedResult.performance = {
          ...cachedResult.performance,
          totalTime: Date.now() - startTime,
          cached: true
        };
        
        logger.debug(`使用缓存的障碍物检测结果, 指纹: ${preprocessed.fingerprint}`);
        detectionSource = 'cache';
        return cachedResult;
      }
    }
    
    // 检查可用内存并加载相应模型
    const availableMemory = getAvailableMemory();
    const useOptimized = availableMemory < config.deviceMemoryThreshold;
    
    logger.debug(`可用内存: ${availableMemory}GB, 使用${useOptimized ? '优化' : '标准'}模型`);
    
    // 加载模型(如果尚未加载)
    const detectionModel = await loadModel(useOptimized);
    
    // 执行推理
    const inferenceStartTime = Date.now();
    
    // 使用TensorFlow进行预测
    const predictions = tf.tidy(() => {
      return detectionModel.predict(preprocessed.tensor);
    });
    
    // 释放输入张量
    preprocessed.tensor.dispose();
    
    // 处理预测结果
    const [boxes, scores, classes] = tf.tidy(() => {
      // 假设模型输出为 [boxes, scores, classes]
      // 取前N个检测结果
      const boxesTensor = predictions[0].squeeze();
      const scoresTensor = predictions[1].squeeze();
      const classesTensor = predictions[2].squeeze();
      
      return [
        boxesTensor.arraySync(),
        scoresTensor.arraySync(),
        classesTensor.arraySync()
      ];
    });
    
    // 释放预测张量
    predictions.forEach(tensor => tensor.dispose());
    
    const inferenceTime = Date.now() - inferenceStartTime;
    
    // 应用非最大抑制
    const nmsStartTime = Date.now();
    const validDetections = [];
    
    for (let i = 0; i < boxes.length; i++) {
      if (scores[i] >= config.confidenceThreshold) {
        const classId = Math.round(classes[i]);
        if (classId >= 0 && classId < CLASS_MAPPING.length) {
          validDetections.push({
            box: boxes[i],
            score: scores[i],
            class: CLASS_MAPPING[classId],
            classId
          });
        }
      }
    }
    
    // 按置信度排序
    validDetections.sort((a, b) => b.score - a.score);
    
    // 应用非最大抑制
    const selectedIndices = [];
    for (let i = 0; i < validDetections.length; i++) {
      let keep = true;
      
      for (let j = 0; j < selectedIndices.length; j++) {
        const iou = calculateIOU(
          validDetections[i].box,
          validDetections[selectedIndices[j]].box
        );
        
        if (iou > config.iouThreshold) {
          keep = false;
          break;
        }
      }
      
      if (keep) {
        selectedIndices.push(i);
        if (selectedIndices.length >= config.maxDetections) {
          break;
        }
      }
    }
    
    // 筛选出最终检测结果
    const finalDetections = selectedIndices.map(index => {
      const detection = validDetections[index];
      
      // 从归一化坐标转换回原始坐标
      const [y1, x1, y2, x2] = detection.box;
      const originalBox = {
        x: Math.round(x1 * preprocessed.originalWidth),
        y: Math.round(y1 * preprocessed.originalHeight),
        width: Math.round((x2 - x1) * preprocessed.originalWidth),
        height: Math.round((y2 - y1) * preprocessed.originalHeight)
      };
      
      return {
        type: detection.class,
        confidence: Math.round(detection.score * 100) / 100,
        location: originalBox
      };
    });
    
    const nmsTime = Date.now() - nmsStartTime;
    const totalTime = Date.now() - startTime;
    
    // 构建结果
    const result = {
      obstacles: finalDetections,
      obstacleCount: finalDetections.length,
      performance: {
        preprocessTime: preprocessed.preprocessTime,
        inferenceTime,
        nmsTime,
        totalTime,
        cached: false,
        modelType: useOptimized ? 'optimized' : 'standard'
      },
      imageInfo: {
        width: preprocessed.originalWidth,
        height: preprocessed.originalHeight,
        fingerprint: preprocessed.fingerprint
      }
    };
    
    // 缓存结果
    if (config.useCache) {
      await cacheDetectionResult(preprocessed.fingerprint, result);
    }
    
    logger.debug(`障碍物检测完成，找到${finalDetections.length}个障碍物，耗时: ${totalTime}ms`);
    
    return result;
  } catch (error) {
    const errorTime = Date.now() - startTime;
    logger.error(`障碍物检测失败，耗时: ${errorTime}ms:`, error);
    
    // 尝试进行基本的OpenCV检测作为后备
    try {
      logger.info('尝试使用备用检测方法...');
      return await fallbackObstacleDetection(imageBuffer);
    } catch (fallbackError) {
      logger.error('备用障碍物检测失败:', fallbackError);
      throw error; // 抛出原始错误
    }
  } finally {
    // 记录检测源
    logger.debug(`障碍物检测源: ${detectionSource}`);
    
    // 清理任何未释放的张量
    tf.disposeVariables();
  }
};

/**
 * 计算两个边界框的IOU(交并比)
 * @param {Array} box1 - 第一个框 [y1, x1, y2, x2]
 * @param {Array} box2 - 第二个框 [y1, x1, y2, x2]
 * @returns {Number} IOU值
 */
const calculateIOU = (box1, box2) => {
  const [y1_1, x1_1, y2_1, x2_1] = box1;
  const [y1_2, x1_2, y2_2, x2_2] = box2;
  
  // 计算交集区域
  const x_left = Math.max(x1_1, x1_2);
  const y_top = Math.max(y1_1, y1_2);
  const x_right = Math.min(x2_1, x2_2);
  const y_bottom = Math.min(y2_1, y2_2);
  
  if (x_right < x_left || y_bottom < y_top) {
    return 0.0; // 没有交集
  }
  
  const intersectionArea = (x_right - x_left) * (y_bottom - y_top);
  
  // 计算两个框的面积
  const box1Area = (x2_1 - x1_1) * (y2_1 - y1_1);
  const box2Area = (x2_2 - x1_2) * (y2_2 - y1_2);
  
  // 计算并集面积
  const unionArea = box1Area + box2Area - intersectionArea;
  
  return intersectionArea / unionArea;
};

/**
 * 后备障碍物检测方法(使用OpenCV)
 * @param {Buffer} imageBuffer - 图像缓冲区
 * @returns {Promise<Object>} 检测结果
 */
const fallbackObstacleDetection = async (imageBuffer) => {
  const startTime = Date.now();
  
  try {
    // 将Buffer转换为cv.Mat
    const image = cv.imdecode(Buffer.from(imageBuffer));
    
    // 转换为灰度图
    const grayImage = image.cvtColor(cv.COLOR_BGR2GRAY);
    
    // 应用高斯模糊减少噪声
    const blurredImage = grayImage.gaussianBlur(new cv.Size(5, 5), 0);
    
    // 使用Canny边缘检测器
    const edges = blurredImage.canny(50, 150);
    
    // 使用霍夫线变换检测线条
    const lines = edges.houghLinesP(1, Math.PI / 180, 50, 50, 10);
    
    // 使用轮廓检测
    const contours = edges.findContours(cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE);
    
    // 筛选有意义的轮廓(面积大于阈值)
    const significantContours = contours.filter(contour => {
      const area = contour.area;
      return area > 100; // 最小面积阈值
    });
    
    // 提取障碍物信息
    const obstacles = [];
    
    significantContours.forEach(contour => {
      const boundingRect = contour.boundingRect();
      
      // 简单分类
      let type = OBSTACLE_TYPES.CORN_STALK; // 默认为玉米秸秆
      
      // 基于形状的简单分类
      const aspectRatio = boundingRect.width / boundingRect.height;
      if (aspectRatio > 1.5) {
        type = OBSTACLE_TYPES.FALLEN_BRANCH;
      } else if (aspectRatio < 0.5) {
        type = OBSTACLE_TYPES.CORN_STALK;
      } else if (contour.area / (boundingRect.width * boundingRect.height) > 0.8) {
        type = OBSTACLE_TYPES.ROCK;
      }
      
      obstacles.push({
        type,
        confidence: 0.6, // 固定置信度，因为这是后备方法
        location: {
          x: boundingRect.x,
          y: boundingRect.y,
          width: boundingRect.width,
          height: boundingRect.height
        }
      });
    });
    
    const totalTime = Date.now() - startTime;
    
    logger.debug(`后备障碍物检测完成，找到${obstacles.length}个障碍物，耗时: ${totalTime}ms`);
    
    return {
      obstacles: obstacles.slice(0, DEFAULT_CONFIG.maxDetections), // 限制最大数量
      obstacleCount: obstacles.length,
      performance: {
        totalTime,
        cached: false,
        modelType: 'opencv_fallback'
      },
      imageInfo: {
        width: image.cols,
        height: image.rows,
        fingerprint: 'fallback_' + Date.now()
      },
      isFallback: true
    };
  } catch (error) {
    logger.error('后备障碍物检测失败:', error);
    throw error;
  }
};

/**
 * 处理深度数据和障碍物检测结果合并
 * @param {Object} detectionResult - 障碍物检测结果
 * @param {Float32Array} depthData - 深度数据
 * @param {Number} depthWidth - 深度图宽度
 * @param {Number} depthHeight - 深度图高度
 * @returns {Object} 增强的检测结果
 */
const enhanceWithDepthData = (detectionResult, depthData, depthWidth, depthHeight) => {
  // 如果没有深度数据，直接返回原检测结果
  if (!depthData || !depthWidth || !depthHeight) {
    return detectionResult;
  }
  
  const { obstacles, imageInfo } = detectionResult;
  const enhancedObstacles = [];
  
  // 计算图像和深度数据之间的缩放比例
  const scaleX = depthWidth / imageInfo.width;
  const scaleY = depthHeight / imageInfo.height;
  
  // 处理每个检测到的障碍物
  for (const obstacle of obstacles) {
    const { location } = obstacle;
    
    // 计算障碍物在深度图中的位置
    const depthX = Math.floor(location.x * scaleX);
    const depthY = Math.floor(location.y * scaleY);
    const depthWidth = Math.floor(location.width * scaleX);
    const depthHeight = Math.floor(location.height * scaleY);
    
    // 计算该区域的平均深度
    let totalDepth = 0;
    let validPoints = 0;
    
    for (let y = depthY; y < depthY + depthHeight && y < depthData.height; y++) {
      for (let x = depthX; x < depthX + depthWidth && x < depthData.width; x++) {
        const index = y * depthWidth + x;
        if (index < depthData.length) {
          const depth = depthData[index];
          if (depth > 0) { // 忽略无效的深度值
            totalDepth += depth;
            validPoints++;
          }
        }
      }
    }
    
    // 计算平均深度
    const averageDepth = validPoints > 0 ? totalDepth / validPoints : 0;
    
    // 添加深度信息到障碍物
    enhancedObstacles.push({
      ...obstacle,
      distance: averageDepth > 0 ? Math.round(averageDepth * 100) / 100 : null,
      depthCoverage: validPoints > 0 ? Math.round((validPoints / (depthWidth * depthHeight)) * 100) / 100 : 0
    });
  }
  
  // 返回增强的结果
  return {
    ...detectionResult,
    obstacles: enhancedObstacles,
    hasDepthData: true
  };
};

/**
 * 清除障碍物检测缓存
 * @returns {Promise<Boolean>} 是否成功
 */
const clearDetectionCache = async () => {
  try {
    const redisClient = getRedisClient();
    const keys = await redisClient.keys('ar:obstacle:*');
    
    if (keys.length > 0) {
      await redisClient.del(keys);
      logger.info(`清除障碍物检测缓存，共${keys.length}个键`);
    }
    
    return true;
  } catch (error) {
    logger.error('清除障碍物检测缓存失败:', error);
    return false;
  }
};

/**
 * 检测障碍物并计算安全路径
 * @param {Buffer} imageBuffer - 图像缓冲区
 * @param {Object} options - 选项
 * @returns {Promise<Object>} 带有安全路径的检测结果
 */
const detectObstaclesWithSafePath = async (imageBuffer, options = {}) => {
  // 首先检测障碍物
  const detectionResult = await detectObstacles(imageBuffer, options);
  
  // 计算安全路径
  const safePath = calculateSafePath(detectionResult);
  
  // 返回增强的结果
  return {
    ...detectionResult,
    safePath
  };
};

/**
 * 计算避开障碍物的安全路径
 * @param {Object} detectionResult - 检测结果
 * @returns {Object} 安全路径信息
 */
const calculateSafePath = (detectionResult) => {
  const { obstacles, imageInfo } = detectionResult;
  
  // 如果没有检测到障碍物，整个图像都是安全的
  if (!obstacles || obstacles.length === 0) {
    return {
      isSafe: true,
      safeRegions: [{
        x: 0,
        y: 0,
        width: imageInfo.width,
        height: imageInfo.height
      }],
      recommended: {
        x: Math.floor(imageInfo.width / 2), 
        y: Math.floor(imageInfo.height / 2)
      }
    };
  }
  
  // 创建图像尺寸的安全度矩阵 (0表示不安全，1表示安全)
  const { width, height } = imageInfo;
  const safetyMap = Array(height).fill().map(() => Array(width).fill(1));
  
  // 标记所有障碍物区域为不安全
  for (const obstacle of obstacles) {
    const { location } = obstacle;
    
    // 扩展边界以创建安全边距
    const margin = 20; // 20像素的安全边距
    const x1 = Math.max(0, location.x - margin);
    const y1 = Math.max(0, location.y - margin);
    const x2 = Math.min(width - 1, location.x + location.width + margin);
    const y2 = Math.min(height - 1, location.y + location.height + margin);
    
    // 将障碍物区域标记为不安全 (0)
    for (let y = y1; y <= y2; y++) {
      for (let x = x1; x <= x2; x++) {
        safetyMap[y][x] = 0;
      }
    }
  }
  
  // 寻找最大安全区域
  const safeRegions = [];
  const visited = Array(height).fill().map(() => Array(width).fill(false));
  
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      if (safetyMap[y][x] === 1 && !visited[y][x]) {
        // 发现未访问的安全点，使用BFS查找连通区域
        const region = {
          x, y, width: 0, height: 0,
          area: 0, 
          points: []
        };
        
        const queue = [{x, y}];
        visited[y][x] = true;
        
        let minX = x, minY = y, maxX = x, maxY = y;
        
        while (queue.length > 0) {
          const point = queue.shift();
          region.points.push(point);
          region.area++;
          
          // 更新边界
          minX = Math.min(minX, point.x);
          minY = Math.min(minY, point.y);
          maxX = Math.max(maxX, point.x);
          maxY = Math.max(maxY, point.y);
          
          // 检查相邻点
          const directions = [
            {dx: -1, dy: 0}, {dx: 1, dy: 0}, 
            {dx: 0, dy: -1}, {dx: 0, dy: 1}
          ];
          
          for (const {dx, dy} of directions) {
            const nx = point.x + dx;
            const ny = point.y + dy;
            
            if (nx >= 0 && nx < width && ny >= 0 && ny < height && 
                safetyMap[ny][nx] === 1 && !visited[ny][nx]) {
              queue.push({x: nx, y: ny});
              visited[ny][nx] = true;
            }
          }
        }
        
        // 计算区域的宽度和高度
        region.width = maxX - minX + 1;
        region.height = maxY - minY + 1;
        
        // 如果区域足够大，添加到安全区域列表
        if (region.area > 1000) { // 最小面积阈值
          safeRegions.push({
            x: minX,
            y: minY,
            width: region.width,
            height: region.height,
            area: region.area,
            center: {
              x: Math.floor(minX + region.width / 2),
              y: Math.floor(minY + region.height / 2)
            }
          });
        }
      }
    }
  }
  
  // 按面积排序安全区域
  safeRegions.sort((a, b) => b.area - a.area);
  
  // 如果没有找到安全区域，使用图像中间
  if (safeRegions.length === 0) {
    return {
      isSafe: false,
      safeRegions: [],
      recommended: {
        x: Math.floor(width / 2),
        y: Math.floor(height / 2)
      }
    };
  }
  
  // 返回安全路径信息
  return {
    isSafe: safeRegions.length > 0,
    safeRegions: safeRegions.map(({x, y, width, height, center}) => ({
      x, y, width, height, center
    })),
    recommended: safeRegions[0].center
  };
};

/**
 * 获取障碍物类型详情
 * @param {String} type - 障碍物类型
 * @returns {Object} 障碍物类型详情
 */
const getObstacleTypeInfo = (type) => {
  const typeInfoMap = {
    [OBSTACLE_TYPES.CORN_STALK]: {
      name: '玉米秸秆',
      description: '高大的玉米植物，有茎、叶和可能的玉米穗',
      riskLevel: 'low',
      avoidanceStrategy: 'walk_around'
    },
    [OBSTACLE_TYPES.ROCK]: {
      name: '石头',
      description: '地面上的岩石，可能会绊倒人',
      riskLevel: 'medium',
      avoidanceStrategy: 'step_over'
    },
    [OBSTACLE_TYPES.WATER]: {
      name: '水坑',
      description: '地面上的积水区域',
      riskLevel: 'medium',
      avoidanceStrategy: 'walk_around'
    },
    [OBSTACLE_TYPES.FALLEN_BRANCH]: {
      name: '倒下的树枝',
      description: '地面上的树枝或树干',
      riskLevel: 'medium',
      avoidanceStrategy: 'step_over'
    },
    [OBSTACLE_TYPES.FENCE]: {
      name: '围栏',
      description: '标记边界的栅栏',
      riskLevel: 'high',
      avoidanceStrategy: 'walk_around'
    },
    [OBSTACLE_TYPES.HOLE]: {
      name: '坑洞',
      description: '地面上的坑洞或凹陷',
      riskLevel: 'high',
      avoidanceStrategy: 'walk_around'
    },
    [OBSTACLE_TYPES.PERSON]: {
      name: '人',
      description: '其他游客或工作人员',
      riskLevel: 'medium',
      avoidanceStrategy: 'walk_around'
    }
  };
  
  return typeInfoMap[type] || {
    name: '未知障碍物',
    description: '无法识别的障碍物',
    riskLevel: 'unknown',
    avoidanceStrategy: 'walk_around'
  };
};

module.exports = {
  detectObstacles,
  detectObstaclesWithSafePath,
  enhanceWithDepthData,
  clearDetectionCache,
  getObstacleTypeInfo,
  OBSTACLE_TYPES
};