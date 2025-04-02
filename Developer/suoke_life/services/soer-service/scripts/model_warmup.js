'use strict';

/**
 * 模型预热脚本
 * 用于容器启动时预热模型，减少冷启动延迟
 */

const path = require('path');
const fs = require('fs').promises;
const ort = require('onnxruntime-node');

// 命令行参数解析
const args = process.argv.slice(2);
const options = {
  configPath: './config/agent-config.json',
  sampleDataPath: './config/sample_data.json',
  concurrency: 2,
  iterations: 3
};

// 解析命令行参数
for (let i = 0; i < args.length; i++) {
  const arg = args[i];
  if (arg === '--config-path' && i + 1 < args.length) {
    options.configPath = args[++i];
  } else if (arg === '--sample-data-path' && i + 1 < args.length) {
    options.sampleDataPath = args[++i];
  } else if (arg === '--concurrency' && i + 1 < args.length) {
    options.concurrency = parseInt(args[++i], 10);
  } else if (arg === '--iterations' && i + 1 < args.length) {
    options.iterations = parseInt(args[++i], 10);
  }
}

// 主函数
async function main() {
  console.log('开始模型预热...');
  console.log(`配置路径: ${options.configPath}`);
  console.log(`样本数据路径: ${options.sampleDataPath}`);
  console.log(`并发数: ${options.concurrency}`);
  console.log(`迭代次数: ${options.iterations}`);
  
  try {
    // 加载配置
    const configPath = path.resolve(options.configPath);
    const config = require(configPath);
    
    console.log(`已加载配置: ${configPath}`);
    
    // 加载样本数据
    const sampleDataPath = path.resolve(options.sampleDataPath);
    let sampleData;
    
    try {
      const sampleDataContent = await fs.readFile(sampleDataPath, 'utf8');
      sampleData = JSON.parse(sampleDataContent);
      console.log(`已加载样本数据: ${sampleDataPath}`);
    } catch (error) {
      console.error(`样本数据加载失败: ${error.message}`);
      console.log('使用默认样本数据');
      sampleData = getDefaultSampleData();
    }
    
    // 获取模型列表
    const models = config.models || {};
    const modelEntries = Object.entries(models);
    
    if (modelEntries.length === 0) {
      console.warn('配置中未找到模型定义');
      process.exit(0);
    }
    
    // 并发预热模型
    const batches = [];
    for (let i = 0; i < modelEntries.length; i += options.concurrency) {
      batches.push(modelEntries.slice(i, i + options.concurrency));
    }
    
    for (const [batchIndex, batch] of batches.entries()) {
      console.log(`开始处理模型批次 ${batchIndex + 1}/${batches.length}`);
      
      await Promise.all(batch.map(async ([name, model]) => {
        await warmupModel(name, model, sampleData);
      }));
    }
    
    console.log('所有模型预热完成');
    process.exit(0);
    
  } catch (error) {
    console.error(`模型预热失败: ${error.message}`);
    console.error(error.stack);
    process.exit(1);
  }
}

// 预热单个模型
async function warmupModel(name, model, sampleData) {
  console.log(`开始预热模型: ${name} (${model.type})`);
  
  try {
    // 检查模型文件是否存在
    const modelPath = model.path;
    try {
      await fs.access(modelPath);
      console.log(`模型文件存在: ${modelPath}`);
    } catch (error) {
      console.error(`模型文件不存在: ${modelPath}`);
      return;
    }
    
    // 创建ONNX会话
    const session = await ort.InferenceSession.create(modelPath);
    console.log(`已创建模型会话: ${name}`);
    
    // 根据模型类型生成测试输入
    const testInputs = generateTestInputs(model.type, sampleData);
    if (!testInputs) {
      console.warn(`无法为模型类型 ${model.type} 生成测试输入`);
      return;
    }
    
    // 执行预热迭代
    for (let i = 0; i < options.iterations; i++) {
      const startTime = process.hrtime();
      
      try {
        await session.run(testInputs);
        
        const hrTime = process.hrtime(startTime);
        const durationMs = hrTime[0] * 1000 + hrTime[1] / 1000000;
        
        console.log(`模型 ${name} 迭代 ${i + 1}/${options.iterations} 完成，耗时 ${durationMs.toFixed(2)}ms`);
      } catch (error) {
        console.error(`模型 ${name} 迭代 ${i + 1} 失败: ${error.message}`);
      }
    }
    
    console.log(`模型 ${name} 预热完成`);
    
  } catch (error) {
    console.error(`模型 ${name} 预热失败: ${error.message}`);
  }
}

// 根据模型类型生成测试输入
function generateTestInputs(modelType, sampleData) {
  // 根据不同模型类型返回不同的测试输入
  switch (modelType) {
    case 'llm':
      return generateLLMInputs(sampleData);
    case 'embedding':
      return generateEmbeddingInputs(sampleData);
    case 'analyzer':
      return generateAnalyzerInputs(sampleData);
    case 'classifier':
      return generateClassifierInputs(sampleData);
    case 'recommender':
      return generateRecommenderInputs(sampleData);
    case 'integrator':
      return generateIntegratorInputs(sampleData);
    default:
      console.warn(`未知模型类型: ${modelType}`);
      return null;
  }
}

// 生成LLM模型输入
function generateLLMInputs(sampleData) {
  // 模拟输入序列的张量
  const inputIds = new Int64Array(Array(128).fill(1));
  const attentionMask = new Int64Array(Array(128).fill(1));
  
  return {
    'input_ids': new ort.Tensor('int64', inputIds, [1, 128]),
    'attention_mask': new ort.Tensor('int64', attentionMask, [1, 128])
  };
}

// 生成Embedding模型输入
function generateEmbeddingInputs(sampleData) {
  // 模拟输入序列的张量
  const inputIds = new Int64Array(Array(64).fill(1));
  const attentionMask = new Int64Array(Array(64).fill(1));
  
  return {
    'input_ids': new ort.Tensor('int64', inputIds, [1, 64]),
    'attention_mask': new ort.Tensor('int64', attentionMask, [1, 64])
  };
}

// 生成分析器模型输入
function generateAnalyzerInputs(sampleData) {
  // 从样本数据提取健康数据特征
  const healthFeatures = extractHealthFeatures(sampleData.health_data);
  
  // 转换为浮点数组
  const features = new Float32Array(healthFeatures);
  
  return {
    'health_features': new ort.Tensor('float32', features, [1, features.length])
  };
}

// 生成分类器模型输入
function generateClassifierInputs(sampleData) {
  // 从样本数据提取生活方式特征
  const lifestyleFeatures = extractLifestyleFeatures(sampleData.lifestyle_data);
  
  // 转换为浮点数组
  const features = new Float32Array(lifestyleFeatures);
  
  return {
    'lifestyle_features': new ort.Tensor('float32', features, [1, features.length])
  };
}

// 生成推荐引擎模型输入
function generateRecommenderInputs(sampleData) {
  // 从样本数据构建用户画像特征
  const userProfileFeatures = [
    ...extractHealthFeatures(sampleData.health_data),
    ...extractLifestyleFeatures(sampleData.lifestyle_data),
    ...extractPreferenceFeatures(sampleData)
  ];
  
  // 转换为浮点数组
  const features = new Float32Array(userProfileFeatures);
  
  return {
    'user_profile': new ort.Tensor('float32', features, [1, features.length])
  };
}

// 生成感知集成模型输入
function generateIntegratorInputs(sampleData) {
  // 从样本数据提取多种感知数据
  const sensingFeatures = [
    ...extractHealthFeatures(sampleData.health_data),
    ...extractEnvironmentFeatures(sampleData.environment_data)
  ];
  
  // 转换为浮点数组
  const features = new Float32Array(sensingFeatures);
  
  return {
    'sensing_data': new ort.Tensor('float32', features, [1, features.length])
  };
}

// 提取健康特征
function extractHealthFeatures(healthData) {
  if (!healthData) return Array(20).fill(0);
  
  const features = [];
  
  // 提取生命体征特征
  if (healthData.vital_signs) {
    features.push(healthData.vital_signs.heart_rate || 70);
    features.push(healthData.vital_signs.blood_pressure?.systolic || 120);
    features.push(healthData.vital_signs.blood_pressure?.diastolic || 80);
    features.push(healthData.vital_signs.temperature || 36.5);
    features.push(healthData.vital_signs.respiratory_rate || 16);
  } else {
    features.push(...[70, 120, 80, 36.5, 16]);
  }
  
  // 提取身体指标特征
  if (healthData.body_metrics) {
    features.push(healthData.body_metrics.weight || 65);
    features.push(healthData.body_metrics.height || 170);
    features.push(healthData.body_metrics.bmi || 22.5);
    features.push(healthData.body_metrics.waist_circumference || 80);
  } else {
    features.push(...[65, 170, 22.5, 80]);
  }
  
  // 提取睡眠特征
  if (healthData.sleep_data) {
    features.push(healthData.sleep_data.duration || 7);
    features.push(healthData.sleep_data.deep_sleep || 2);
    features.push(healthData.sleep_data.rem_sleep || 1.5);
    features.push(healthData.sleep_data.light_sleep || 3.5);
  } else {
    features.push(...[7, 2, 1.5, 3.5]);
  }
  
  return features;
}

// 提取生活方式特征
function extractLifestyleFeatures(lifestyleData) {
  if (!lifestyleData) return Array(15).fill(0);
  
  const features = [];
  
  // 提取运动特征
  if (lifestyleData.exercise) {
    // 将运动类型转换为数值编码
    const exerciseTypeMap = {
      'walking': 1,
      'running': 2,
      'cycling': 3,
      'swimming': 4,
      'yoga': 5,
      'gym': 6
    };
    
    const exerciseType = exerciseTypeMap[lifestyleData.exercise.type] || 0;
    features.push(exerciseType);
    features.push(lifestyleData.exercise.duration || 0);
    
    // 将强度转换为数值
    const intensityMap = {
      'low': 1,
      'moderate': 2,
      'high': 3
    };
    
    const intensity = intensityMap[lifestyleData.exercise.intensity] || 0;
    features.push(intensity);
    features.push(lifestyleData.exercise.calories_burned || 0);
  } else {
    features.push(...[0, 0, 0, 0]);
  }
  
  // 提取饮食特征
  if (lifestyleData.diet) {
    // 计算每种食物类型的摄入量
    const foodGroups = {
      'vegetables': 0,
      'fruits': 0,
      'protein': 0,
      'grains': 0,
      'dairy': 0
    };
    
    if (lifestyleData.diet.meals && Array.isArray(lifestyleData.diet.meals)) {
      for (const meal of lifestyleData.diet.meals) {
        if (meal.food_groups && Array.isArray(meal.food_groups)) {
          for (const group of meal.food_groups) {
            if (foodGroups[group] !== undefined) {
              foodGroups[group]++;
            }
          }
        }
      }
    }
    
    features.push(foodGroups.vegetables);
    features.push(foodGroups.fruits);
    features.push(foodGroups.protein);
    features.push(foodGroups.grains);
    features.push(foodGroups.dairy);
    
    features.push(lifestyleData.diet.water_intake || 0);
  } else {
    features.push(...[0, 0, 0, 0, 0, 0]);
  }
  
  // 提取压力水平特征
  const stressMap = {
    'low': 1,
    'medium': 2,
    'high': 3
  };
  
  const stress = stressMap[lifestyleData.stress_level] || 0;
  features.push(stress);
  
  return features;
}

// 提取环境特征
function extractEnvironmentFeatures(environmentData) {
  if (!environmentData) return Array(10).fill(0);
  
  const features = [];
  
  // 将位置转换为数值编码
  const locationMap = {
    'home': 1,
    'office': 2,
    'outdoor': 3,
    'transit': 4
  };
  
  const location = locationMap[environmentData.location] || 0;
  features.push(location);
  
  // 提取环境数据
  features.push(environmentData.temperature || 22);
  features.push(environmentData.humidity || 50);
  
  // 将空气质量转换为数值
  const airQualityMap = {
    'excellent': 5,
    'good': 4,
    'moderate': 3,
    'poor': 2,
    'very_poor': 1
  };
  
  const airQuality = airQualityMap[environmentData.air_quality] || 3;
  features.push(airQuality);
  
  // 将噪音水平转换为数值
  const noiseMap = {
    'very_quiet': 1,
    'quiet': 2,
    'moderate': 3,
    'noisy': 4,
    'very_noisy': 5
  };
  
  const noise = noiseMap[environmentData.noise_level] || 3;
  features.push(noise);
  
  return features;
}

// 提取偏好特征（模拟）
function extractPreferenceFeatures(sampleData) {
  // 模拟用户偏好特征
  return Array(5).fill(0.5);
}

// 默认样本数据
function getDefaultSampleData() {
  return {
    health_data: {
      vital_signs: {
        heart_rate: 72,
        blood_pressure: { systolic: 120, diastolic: 80 },
        temperature: 36.5,
        respiratory_rate: 16
      },
      body_metrics: {
        weight: 65,
        height: 170,
        bmi: 22.5,
        waist_circumference: 80
      },
      sleep_data: {
        duration: 7.5,
        quality: 'good',
        deep_sleep: 2.1,
        rem_sleep: 1.8,
        light_sleep: 3.6
      }
    },
    lifestyle_data: {
      exercise: {
        type: 'walking',
        duration: 45,
        intensity: 'moderate',
        calories_burned: 180
      },
      diet: {
        meals: [
          { type: 'breakfast', food_groups: ['grains', 'fruits', 'dairy'] },
          { type: 'lunch', food_groups: ['vegetables', 'protein', 'grains'] },
          { type: 'dinner', food_groups: ['vegetables', 'protein'] }
        ],
        water_intake: 1800
      },
      stress_level: 'medium'
    },
    environment_data: {
      location: 'home',
      temperature: 22,
      humidity: 50,
      air_quality: 'good',
      noise_level: 'low'
    }
  };
}

// 执行主函数
main().catch(error => {
  console.error('预热过程出错:', error);
  process.exit(1);
});