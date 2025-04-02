'use strict';

/**
 * 感知路由
 * 处理全态势健康感知和环境感知的API接口
 */
module.exports = async function (fastify, opts) {
  // 获取用户健康感知数据
  fastify.get('/user/:userId/health', {
    schema: {
      params: {
        type: 'object',
        required: ['userId'],
        properties: {
          userId: { type: 'string' }
        }
      },
      querystring: {
        type: 'object',
        properties: {
          timeframe: { type: 'string', enum: ['day', 'week', 'month', 'year'] }
        }
      },
      response: {
        200: {
          type: 'object',
          properties: {
            userId: { type: 'string' },
            summary: {
              type: 'object',
              properties: {
                healthScore: { type: 'number' },
                vitalSigns: {
                  type: 'object',
                  properties: {
                    heartRate: { type: 'object' },
                    bloodPressure: { type: 'object' },
                    respiratoryRate: { type: 'object' },
                    temperature: { type: 'object' }
                  }
                },
                activities: {
                  type: 'object',
                  properties: {
                    steps: { type: 'number' },
                    activeMinutes: { type: 'number' },
                    caloriesBurned: { type: 'number' }
                  }
                },
                sleep: {
                  type: 'object',
                  properties: {
                    duration: { type: 'number' },
                    quality: { type: 'string' },
                    deepSleepPercentage: { type: 'number' }
                  }
                }
              }
            },
            insights: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  type: { type: 'string' },
                  title: { type: 'string' },
                  description: { type: 'string' },
                  confidence: { type: 'number' }
                }
              }
            },
            anomalies: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  metric: { type: 'string' },
                  description: { type: 'string' },
                  severity: { type: 'string' },
                  detectedAt: { type: 'string', format: 'date-time' }
                }
              }
            },
            generatedAt: { type: 'string', format: 'date-time' }
          }
        }
      }
    }
  }, async (request, reply) => {
    const { userId } = request.params;
    const { timeframe = 'day' } = request.query;
    
    // 验证用户ID
    if (!userId || userId.length < 3) {
      return reply.code(400).send({
        error: 'invalid_user_id',
        message: '无效的用户ID'
      });
    }
    
    try {
      // 从感知服务获取健康数据
      let healthData = null;
      if (fastify.integrations?.sensing_service) {
        try {
          const sensingClient = fastify.integrations.sensing_service.client;
          const response = await sensingClient.get(`/users/${userId}/health-sensing`, {
            params: { timeframe }
          });
          
          if (response.status === 200) {
            healthData = response.data;
          }
        } catch (error) {
          fastify.log.error(`获取健康感知数据失败: ${error.message}`);
          // 不抛出错误，使用模拟数据
        }
      }
      
      // 如果没有获取到数据，使用模拟数据
      if (!healthData) {
        healthData = getMockHealthSensingData(userId, timeframe);
      }
      
      // 分析数据
      let healthInsights = [];
      let healthAnomalies = [];
      
      if (
        fastify.agentService.models.sensing_integrator?.loaded && 
        healthData
      ) {
        try {
          // 这里应该实现使用感知集成模型分析数据
          // 以下是模拟实现
          const analysis = analyzeMockHealthData(healthData);
          healthInsights = analysis.insights;
          healthAnomalies = analysis.anomalies;
        } catch (error) {
          fastify.log.error(`分析健康感知数据失败: ${error.message}`);
          // 不抛出错误，返回空结果
        }
      }
      
      // 构建响应
      return {
        userId,
        summary: healthData.summary,
        insights: healthInsights,
        anomalies: healthAnomalies,
        generatedAt: new Date().toISOString()
      };
      
    } catch (error) {
      fastify.log.error(`处理健康感知请求失败: ${error.message}`);
      
      return reply.code(500).send({
        error: 'health_sensing_failed',
        message: '处理健康感知数据失败',
        details: process.env.NODE_ENV === 'production' ? undefined : error.message
      });
    }
  });

  // 获取环境感知数据
  fastify.get('/environment/:userId', {
    schema: {
      params: {
        type: 'object',
        required: ['userId'],
        properties: {
          userId: { type: 'string' }
        }
      },
      querystring: {
        type: 'object',
        properties: {
          location: { type: 'string' }
        }
      },
      response: {
        200: {
          type: 'object',
          properties: {
            userId: { type: 'string' },
            location: { type: 'string' },
            environment: {
              type: 'object',
              properties: {
                temperature: { type: 'number' },
                humidity: { type: 'number' },
                airQuality: {
                  type: 'object',
                  properties: {
                    index: { type: 'number' },
                    description: { type: 'string' },
                    pollutants: { type: 'object' }
                  }
                },
                noise: {
                  type: 'object',
                  properties: {
                    level: { type: 'number' },
                    description: { type: 'string' }
                  }
                },
                light: {
                  type: 'object',
                  properties: {
                    intensity: { type: 'number' },
                    description: { type: 'string' }
                  }
                }
              }
            },
            insights: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  type: { type: 'string' },
                  title: { type: 'string' },
                  description: { type: 'string' },
                  advice: { type: 'string' }
                }
              }
            },
            generatedAt: { type: 'string', format: 'date-time' }
          }
        }
      }
    }
  }, async (request, reply) => {
    const { userId } = request.params;
    const { location = 'home' } = request.query;
    
    // 验证用户ID
    if (!userId || userId.length < 3) {
      return reply.code(400).send({
        error: 'invalid_user_id',
        message: '无效的用户ID'
      });
    }
    
    try {
      // 从感知服务获取环境数据
      let environmentData = null;
      if (fastify.integrations?.sensing_service) {
        try {
          const sensingClient = fastify.integrations.sensing_service.client;
          const response = await sensingClient.get(`/users/${userId}/environment-sensing`, {
            params: { location }
          });
          
          if (response.status === 200) {
            environmentData = response.data;
          }
        } catch (error) {
          fastify.log.error(`获取环境感知数据失败: ${error.message}`);
          // 不抛出错误，使用模拟数据
        }
      }
      
      // 如果没有获取到数据，使用模拟数据
      if (!environmentData) {
        environmentData = getMockEnvironmentData(userId, location);
      }
      
      // 分析环境数据，生成洞察
      let environmentInsights = [];
      
      if (
        fastify.agentService.models.sensing_integrator?.loaded && 
        environmentData
      ) {
        try {
          // 这里应该实现使用感知集成模型分析环境数据
          // 以下是模拟实现
          environmentInsights = analyzeMockEnvironmentData(environmentData);
        } catch (error) {
          fastify.log.error(`分析环境感知数据失败: ${error.message}`);
          // 不抛出错误，返回空结果
        }
      }
      
      // 构建响应
      return {
        userId,
        location,
        environment: environmentData.environment,
        insights: environmentInsights,
        generatedAt: new Date().toISOString()
      };
      
    } catch (error) {
      fastify.log.error(`处理环境感知请求失败: ${error.message}`);
      
      return reply.code(500).send({
        error: 'environment_sensing_failed',
        message: '处理环境感知数据失败',
        details: process.env.NODE_ENV === 'production' ? undefined : error.message
      });
    }
  });

  // 获取多模态感知数据
  fastify.get('/multimodal/:userId', {
    schema: {
      params: {
        type: 'object',
        required: ['userId'],
        properties: {
          userId: { type: 'string' }
        }
      },
      querystring: {
        type: 'object',
        properties: {
          type: { type: 'string', enum: ['voice', 'facial', 'posture', 'all'] }
        }
      },
      response: {
        200: {
          type: 'object',
          properties: {
            userId: { type: 'string' },
            modalityType: { type: 'string' },
            data: {
              type: 'object',
              properties: {
                voice: {
                  type: 'object',
                  properties: {
                    tone: { type: 'string' },
                    emotion: { type: 'string' },
                    energy: { type: 'string' },
                    indicators: { type: 'object' }
                  }
                },
                facial: {
                  type: 'object',
                  properties: {
                    expression: { type: 'string' },
                    emotion: { type: 'string' },
                    indicators: { type: 'object' }
                  }
                },
                posture: {
                  type: 'object',
                  properties: {
                    position: { type: 'string' },
                    movement: { type: 'string' },
                    indicators: { type: 'object' }
                  }
                }
              }
            },
            insights: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  type: { type: 'string' },
                  title: { type: 'string' },
                  description: { type: 'string' },
                  advice: { type: 'string' },
                  confidence: { type: 'number' }
                }
              }
            },
            generatedAt: { type: 'string', format: 'date-time' }
          }
        }
      }
    }
  }, async (request, reply) => {
    const { userId } = request.params;
    const { type = 'all' } = request.query;
    
    // 验证用户ID
    if (!userId || userId.length < 3) {
      return reply.code(400).send({
        error: 'invalid_user_id',
        message: '无效的用户ID'
      });
    }
    
    try {
      // 从感知服务获取多模态数据
      let multimodalData = null;
      if (fastify.integrations?.sensing_service) {
        try {
          const sensingClient = fastify.integrations.sensing_service.client;
          const response = await sensingClient.get(`/users/${userId}/multimodal-sensing`, {
            params: { type }
          });
          
          if (response.status === 200) {
            multimodalData = response.data;
          }
        } catch (error) {
          fastify.log.error(`获取多模态感知数据失败: ${error.message}`);
          // 不抛出错误，使用模拟数据
        }
      }
      
      // 如果没有获取到数据，使用模拟数据
      if (!multimodalData) {
        multimodalData = getMockMultimodalData(userId, type);
      }
      
      // 分析多模态数据，生成洞察
      let multimodalInsights = [];
      
      if (
        fastify.agentService.models.sensing_integrator?.loaded && 
        multimodalData
      ) {
        try {
          // 这里应该实现使用感知集成模型分析多模态数据
          // 以下是模拟实现
          multimodalInsights = analyzeMockMultimodalData(multimodalData);
        } catch (error) {
          fastify.log.error(`分析多模态感知数据失败: ${error.message}`);
          // 不抛出错误，返回空结果
        }
      }
      
      // 构建响应
      return {
        userId,
        modalityType: type,
        data: multimodalData.data,
        insights: multimodalInsights,
        generatedAt: new Date().toISOString()
      };
      
    } catch (error) {
      fastify.log.error(`处理多模态感知请求失败: ${error.message}`);
      
      return reply.code(500).send({
        error: 'multimodal_sensing_failed',
        message: '处理多模态感知数据失败',
        details: process.env.NODE_ENV === 'production' ? undefined : error.message
      });
    }
  });
};

// 生成模拟健康感知数据
function getMockHealthSensingData(userId, timeframe) {
  return {
    userId,
    timeframe,
    summary: {
      healthScore: 78,
      vitalSigns: {
        heartRate: {
          average: 72,
          min: 58,
          max: 110,
          resting: 65
        },
        bloodPressure: {
          average: {
            systolic: 125,
            diastolic: 75
          },
          min: {
            systolic: 115,
            diastolic: 70
          },
          max: {
            systolic: 135,
            diastolic: 85
          }
        },
        respiratoryRate: {
          average: 16,
          min: 14,
          max: 20
        },
        temperature: {
          average: 36.5,
          min: 36.2,
          max: 36.8
        }
      },
      activities: {
        steps: 8500,
        activeMinutes: 45,
        caloriesBurned: 2100
      },
      sleep: {
        duration: 7.2,
        quality: 'moderate',
        deepSleepPercentage: 22
      }
    },
    detailedData: {
      heartRateTimeSeries: [
        { timestamp: '2023-06-01T07:00:00Z', value: 65 },
        { timestamp: '2023-06-01T10:00:00Z', value: 72 },
        { timestamp: '2023-06-01T13:00:00Z', value: 85 },
        { timestamp: '2023-06-01T16:00:00Z', value: 75 },
        { timestamp: '2023-06-01T19:00:00Z', value: 110 },
        { timestamp: '2023-06-01T22:00:00Z', value: 68 }
      ],
      stepsTimeSeries: [
        { timestamp: '2023-06-01T08:00:00Z', value: 1200 },
        { timestamp: '2023-06-01T12:00:00Z', value: 2500 },
        { timestamp: '2023-06-01T16:00:00Z', value: 3800 },
        { timestamp: '2023-06-01T20:00:00Z', value: 1000 }
      ],
      sleepStages: [
        { stage: 'awake', duration: 0.5 },
        { stage: 'light', duration: 3.8 },
        { stage: 'deep', duration: 1.6 },
        { stage: 'rem', duration: 1.3 }
      ]
    }
  };
}

// 分析模拟健康数据
function analyzeMockHealthData(healthData) {
  // 模拟分析结果
  return {
    insights: [
      {
        type: 'activity',
        title: '活动水平良好',
        description: '您的日常活动水平符合健康标准，步数达到了推荐的8000-10000步范围内。',
        confidence: 0.9
      },
      {
        type: 'sleep',
        title: '深度睡眠比例偏低',
        description: '您的深度睡眠比例为22%，略低于理想的25-30%范围，可能影响恢复质量。',
        confidence: 0.85
      },
      {
        type: 'heart',
        title: '心率波动正常',
        description: '您的心率变化在正常范围内，运动后心率上升和恢复情况良好。',
        confidence: 0.95
      }
    ],
    anomalies: [
      {
        metric: 'heartRate',
        description: '在19:00左右检测到心率明显升高至110bpm，显著高于您的正常水平。',
        severity: 'low',
        detectedAt: '2023-06-01T19:00:00Z'
      }
    ]
  };
}

// 生成模拟环境数据
function getMockEnvironmentData(userId, location) {
  const environmentData = {
    home: {
      environment: {
        temperature: 22.5,
        humidity: 45,
        airQuality: {
          index: 75,
          description: '良好',
          pollutants: {
            pm25: 15,
            pm10: 28,
            co2: 650
          }
        },
        noise: {
          level: 40,
          description: '安静'
        },
        light: {
          intensity: 350,
          description: '舒适'
        }
      }
    },
    office: {
      environment: {
        temperature: 23.8,
        humidity: 38,
        airQuality: {
          index: 65,
          description: '一般',
          pollutants: {
            pm25: 22,
            pm10: 35,
            co2: 850
          }
        },
        noise: {
          level: 58,
          description: '适中'
        },
        light: {
          intensity: 450,
          description: '适中'
        }
      }
    },
    outdoor: {
      environment: {
        temperature: 26.2,
        humidity: 60,
        airQuality: {
          index: 55,
          description: '一般',
          pollutants: {
            pm25: 25,
            pm10: 42,
            no2: 35
          }
        },
        noise: {
          level: 65,
          description: '嘈杂'
        },
        light: {
          intensity: 1200,
          description: '明亮'
        }
      }
    }
  };
  
  return {
    userId,
    location,
    ...environmentData[location] || environmentData.home
  };
}

// 分析模拟环境数据
function analyzeMockEnvironmentData(environmentData) {
  // 模拟分析结果
  const location = environmentData.location;
  const env = environmentData.environment;
  
  const insights = [];
  
  // 温度分析
  if (env.temperature < 18) {
    insights.push({
      type: 'temperature',
      title: '环境温度偏低',
      description: `当前${location}温度为${env.temperature}°C，低于舒适温度范围。`,
      advice: '建议适当提高室温或增加衣物，保持体温，避免受凉。'
    });
  } else if (env.temperature > 26) {
    insights.push({
      type: 'temperature',
      title: '环境温度偏高',
      description: `当前${location}温度为${env.temperature}°C，高于舒适温度范围。`,
      advice: '建议适当降低室温，注意补充水分，避免中暑。'
    });
  } else {
    insights.push({
      type: 'temperature',
      title: '环境温度适宜',
      description: `当前${location}温度为${env.temperature}°C，处于舒适温度范围内。`,
      advice: '温度舒适，有助于保持良好状态。'
    });
  }
  
  // 湿度分析
  if (env.humidity < 30) {
    insights.push({
      type: 'humidity',
      title: '环境湿度偏低',
      description: `当前${location}湿度为${env.humidity}%，湿度较低可能导致皮肤和呼吸道干燥。`,
      advice: '建议使用加湿器提高室内湿度，多饮水，护理皮肤。'
    });
  } else if (env.humidity > 70) {
    insights.push({
      type: 'humidity',
      title: '环境湿度偏高',
      description: `当前${location}湿度为${env.humidity}%，湿度较高可能导致霉菌滋生。`,
      advice: '建议使用除湿器降低室内湿度，保持通风，预防过敏和呼吸道问题。'
    });
  } else {
    insights.push({
      type: 'humidity',
      title: '环境湿度适宜',
      description: `当前${location}湿度为${env.humidity}%，处于舒适湿度范围内。`,
      advice: '湿度舒适，有助于维护皮肤和呼吸道健康。'
    });
  }
  
  // 空气质量分析
  if (env.airQuality.index < 50) {
    insights.push({
      type: 'airQuality',
      title: '空气质量优良',
      description: `当前${location}空气质量指数为${env.airQuality.index}，属于优良水平。`,
      advice: '空气质量良好，适合正常活动和开窗通风。'
    });
  } else if (env.airQuality.index < 100) {
    insights.push({
      type: 'airQuality',
      title: '空气质量一般',
      description: `当前${location}空气质量指数为${env.airQuality.index}，属于一般水平。`,
      advice: '空气质量一般，敏感人群应减少户外活动，考虑使用空气净化器。'
    });
  } else {
    insights.push({
      type: 'airQuality',
      title: '空气质量较差',
      description: `当前${location}空气质量指数为${env.airQuality.index}，空气质量较差。`,
      advice: '建议减少户外活动，关闭窗户，使用空气净化器，佩戴口罩出行。'
    });
  }
  
  // 噪音分析
  if (env.noise.level > 60) {
    insights.push({
      type: 'noise',
      title: '环境噪音较高',
      description: `当前${location}噪音水平为${env.noise.level}dB，可能影响注意力和休息质量。`,
      advice: '建议使用耳塞或降噪耳机，考虑调整活动位置或时间。'
    });
  }
  
  return insights;
}

// 生成模拟多模态数据
function getMockMultimodalData(userId, type) {
  const allData = {
    voice: {
      tone: 'calm',
      emotion: 'neutral',
      energy: 'moderate',
      indicators: {
        pitch: 'medium',
        rate: 'normal',
        volume: 'moderate',
        emotionalMarkers: [
          { emotion: 'neutral', confidence: 0.8 },
          { emotion: 'calm', confidence: 0.15 },
          { emotion: 'stressed', confidence: 0.05 }
        ]
      }
    },
    facial: {
      expression: 'relaxed',
      emotion: 'content',
      indicators: {
        eyeOpenness: 'normal',
        mouthPosition: 'neutral',
        browPosition: 'neutral',
        emotionalMarkers: [
          { emotion: 'content', confidence: 0.75 },
          { emotion: 'relaxed', confidence: 0.2 },
          { emotion: 'tired', confidence: 0.05 }
        ]
      }
    },
    posture: {
      position: 'seated',
      movement: 'minimal',
      indicators: {
        spineAlignment: 'slight_forward_lean',
        shoulderPosition: 'slightly_hunched',
        movementFrequency: 'low',
        posturalMarkers: [
          { posture: 'seated_desk', confidence: 0.9 },
          { posture: 'slouching', confidence: 0.6 }
        ]
      }
    }
  };
  
  // 根据请求类型返回数据
  let responseData = { data: {} };
  
  if (type === 'all') {
    responseData.data = allData;
  } else {
    responseData.data[type] = allData[type];
  }
  
  return {
    userId,
    type,
    ...responseData
  };
}

// 分析模拟多模态数据
function analyzeMockMultimodalData(multimodalData) {
  // 模拟分析结果
  const insights = [];
  const data = multimodalData.data;
  
  // 语音分析
  if (data.voice) {
    const voice = data.voice;
    
    if (voice.emotion === 'stressed' || voice.energy === 'high' || voice.tone === 'agitated') {
      insights.push({
        type: 'voice',
        title: '检测到语音压力',
        description: '您的语音模式显示压力水平较高，语速较快，音调偏高。',
        advice: '建议深呼吸放松，放慢语速，适当休息恢复精力。',
        confidence: 0.85
      });
    } else if (voice.energy === 'low' && voice.tone === 'monotone') {
      insights.push({
        type: 'voice',
        title: '检测到语音能量低',
        description: '您的语音能量水平较低，语调平坦，可能表示疲劳或情绪低落。',
        advice: '建议适当休息，进行一些愉快的活动提升情绪，必要时寻求支持。',
        confidence: 0.8
      });
    } else {
      insights.push({
        type: 'voice',
        title: '语音状态良好',
        description: '您的语音模式显示情绪平稳，语调自然，表达流畅。',
        advice: '继续保持良好的情绪状态，享受当下的交流和活动。',
        confidence: 0.9
      });
    }
  }
  
  // 面部表情分析
  if (data.facial) {
    const facial = data.facial;
    
    if (facial.emotion === 'tired' || facial.expression === 'fatigued') {
      insights.push({
        type: 'facial',
        title: '检测到面部疲劳',
        description: '您的面部表情显示疲劳迹象，眼睛半闭状态增加，眨眼频率降低。',
        advice: '建议适当休息，可以闭目养神或进行眼部放松练习，充分睡眠。',
        confidence: 0.85
      });
    } else if (facial.emotion === 'stressed' || facial.expression === 'tense') {
      insights.push({
        type: 'facial',
        title: '检测到面部紧张',
        description: '您的面部肌肉显示紧张状态，尤其是眉间和下颌区域。',
        advice: '建议进行面部放松练习，如面部按摩或温和的面部拉伸，深呼吸缓解压力。',
        confidence: 0.8
      });
    } else {
      insights.push({
        type: 'facial',
        title: '面部表情自然',
        description: '您的面部表情自然放松，表明当前情绪状态良好。',
        advice: '继续保持积极的心态和放松的状态。',
        confidence: 0.9
      });
    }
  }
  
  // 姿势分析
  if (data.posture) {
    const posture = data.posture;
    
    if (posture.spineAlignment === 'severe_forward_lean' || posture.shoulderPosition === 'hunched') {
      insights.push({
        type: 'posture',
        title: '检测到不良坐姿',
        description: '您当前的坐姿显示严重前倾和肩膀耸起，可能导致颈背部不适。',
        advice: '建议调整座椅高度和距离，保持脊柱自然弯曲，定期起身活动和拉伸。',
        confidence: 0.9
      });
    } else if (posture.movement === 'minimal' && posture.position === 'seated' && posture.indicators.movementFrequency === 'low') {
      insights.push({
        type: 'posture',
        title: '检测到久坐行为',
        description: '您已经保持相同姿势较长时间，活动量较少。',
        advice: '建议每30-45分钟起身活动5分钟，避免长时间保持同一姿势。',
        confidence: 0.85
      });
    } else {
      insights.push({
        type: 'posture',
        title: '姿势状态良好',
        description: '您的姿势总体良好，保持了适当的活动频率。',
        advice: '继续保持良好的姿势习惯，定期变换姿势和适度活动。',
        confidence: 0.8
      });
    }
  }
  
  return insights;
}