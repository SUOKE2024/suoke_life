/**
 * 玉米生长的天气影响模型
 * 模拟不同天气条件对玉米生长的影响
 */

const axios = require('axios');
const { GrowthStage } = require('../../models/cornPlant');
const { logger } = require('../../utils/logger');

// 天气影响参数
const WEATHER_IMPACT_FACTORS = {
  // 温度影响因子 (°C)
  temperature: {
    optimal: { min: 25, max: 32 }, // 最佳生长温度范围
    growth: {
      // 各生长阶段的生长速率影响曲线参数
      [GrowthStage.SEEDLING]: { a: 0.05, b: 0.15, c: 28, d: 3 }, // 幼苗期
      [GrowthStage.VEGETATIVE]: { a: 0.08, b: 0.2, c: 30, d: 4 }, // 营养生长期
      [GrowthStage.FLOWERING]: { a: 0.06, b: 0.18, c: 27, d: 3.5 }, // 开花期
      [GrowthStage.GRAIN_FILLING]: { a: 0.04, b: 0.16, c: 26, d: 3 }, // 灌浆期
      [GrowthStage.MATURITY]: { a: 0.02, b: 0.1, c: 25, d: 4 }, // 成熟期
    },
    stress: { // 温度胁迫阈值
      cold: 10, // 低温胁迫 (°C)
      heat: 38, // 高温胁迫 (°C)
    }
  },
  
  // 降水影响因子 (mm/day)
  precipitation: {
    optimal: { min: 4, max: 25 }, // 最佳日降水量范围
    growth: {
      [GrowthStage.SEEDLING]: { min: 3, max: 15, sensitivity: 0.8 },
      [GrowthStage.VEGETATIVE]: { min: 5, max: 25, sensitivity: 1.0 },
      [GrowthStage.FLOWERING]: { min: 5, max: 20, sensitivity: 1.2 },
      [GrowthStage.GRAIN_FILLING]: { min: 4, max: 20, sensitivity: 0.9 },
      [GrowthStage.MATURITY]: { min: 2, max: 15, sensitivity: 0.6 },
    },
    stress: {
      drought: 1, // 干旱胁迫 (mm/day)
      flood: 50, // 涝灾胁迫 (mm/day)
    }
  },
  
  // 光照影响因子 (hours/day)
  sunlight: {
    optimal: { min: 8, max: 14 }, // 最佳日照时间范围
    growth: {
      [GrowthStage.SEEDLING]: { min: 6, max: 12, sensitivity: 0.7 },
      [GrowthStage.VEGETATIVE]: { min: 8, max: 14, sensitivity: 1.0 },
      [GrowthStage.FLOWERING]: { min: 9, max: 15, sensitivity: 1.1 },
      [GrowthStage.GRAIN_FILLING]: { min: 8, max: 14, sensitivity: 0.9 },
      [GrowthStage.MATURITY]: { min: 7, max: 13, sensitivity: 0.6 },
    }
  },
  
  // 湿度影响因子 (%)
  humidity: {
    optimal: { min: 50, max: 80 }, // 最佳湿度范围
    growth: {
      [GrowthStage.SEEDLING]: { min: 60, max: 85, sensitivity: 0.6 },
      [GrowthStage.VEGETATIVE]: { min: 55, max: 80, sensitivity: 0.7 },
      [GrowthStage.FLOWERING]: { min: 50, max: 75, sensitivity: 0.9 },
      [GrowthStage.GRAIN_FILLING]: { min: 45, max: 75, sensitivity: 0.8 },
      [GrowthStage.MATURITY]: { min: 40, max: 70, sensitivity: 0.5 },
    },
    disease: { // 疾病风险阈值
      risk: 85 // 高湿度疾病风险阈值 (%)
    }
  },
  
  // 风速影响因子 (m/s)
  windSpeed: {
    optimal: { min: 0, max: 4 }, // 最佳风速范围
    damage: { // 风害阈值
      risk: 8, // 风害风险阈值 (m/s)
      severe: 15 // 严重风害阈值 (m/s)
    }
  }
};

/**
 * 天气影响服务类 - 处理天气对玉米生长的影响
 */
class WeatherImpactService {
  constructor() {
    this.weatherAPIKey = process.env.WEATHER_API_KEY;
    this.weatherAPIBaseUrl = process.env.WEATHER_API_BASE_URL;
    
    // 缓存当前天气数据
    this.currentWeatherData = null;
    this.forecastWeatherData = null;
    this.lastWeatherFetch = null;
    
    // 历史天气影响数据
    this.weatherHistory = [];
  }
  
  /**
   * 获取当前天气数据
   * @param {Object} location - 位置信息 {latitude, longitude}
   * @returns {Promise<Object>} - 天气数据
   */
  async getCurrentWeather(location) {
    // 检查缓存是否有效（30分钟内）
    const now = Date.now();
    if (
      this.currentWeatherData && 
      this.lastWeatherFetch && 
      (now - this.lastWeatherFetch) < 30 * 60 * 1000
    ) {
      return this.currentWeatherData;
    }
    
    try {
      const response = await axios.get(`${this.weatherAPIBaseUrl}/current`, {
        params: {
          key: this.weatherAPIKey,
          lat: location.latitude,
          lon: location.longitude,
          units: 'metric'
        }
      });
      
      this.currentWeatherData = response.data;
      this.lastWeatherFetch = now;
      
      // 记录天气历史
      this.recordWeatherData(this.currentWeatherData);
      
      return this.currentWeatherData;
    } catch (error) {
      logger.error('获取天气数据失败', error);
      
      // 如果API请求失败但有缓存数据，继续使用缓存
      if (this.currentWeatherData) {
        return this.currentWeatherData;
      }
      
      // 返回默认天气条件
      return this.getDefaultWeatherData();
    }
  }
  
  /**
   * 记录天气数据
   * @param {Object} weatherData - 天气数据
   */
  recordWeatherData(weatherData) {
    this.weatherHistory.push({
      timestamp: Date.now(),
      data: weatherData
    });
    
    // 限制历史记录大小
    if (this.weatherHistory.length > 1000) {
      this.weatherHistory = this.weatherHistory.slice(-1000);
    }
  }
  
  /**
   * 获取默认天气数据（当API不可用时）
   * @returns {Object} - 默认天气数据
   */
  getDefaultWeatherData() {
    return {
      temperature: 25, // 摄氏度
      precipitation: 5, // 毫米/天
      humidity: 65, // 百分比
      windSpeed: 3, // 米/秒
      sunlight: 10, // 小时/天
      timestamp: Date.now()
    };
  }
  
  /**
   * 计算天气对指定生长阶段的总体影响系数
   * @param {Object} weatherData - 天气数据
   * @param {string} growthStage - 生长阶段
   * @returns {Object} - 影响系数和状态
   */
  calculateWeatherImpact(weatherData, growthStage) {
    // 计算各因素的影响系数
    const temperatureImpact = this.calculateTemperatureImpact(weatherData.temperature, growthStage);
    const precipitationImpact = this.calculatePrecipitationImpact(weatherData.precipitation, growthStage);
    const sunlightImpact = this.calculateSunlightImpact(weatherData.sunlight, growthStage);
    const humidityImpact = this.calculateHumidityImpact(weatherData.humidity, growthStage);
    const windImpact = this.calculateWindImpact(weatherData.windSpeed, growthStage);
    
    // 综合影响系数（加权平均）
    const impactWeights = {
      temperature: 0.25,
      precipitation: 0.25,
      sunlight: 0.2,
      humidity: 0.15,
      wind: 0.15
    };
    
    // 总体生长影响系数 (0-1.0范围，1.0为最佳)
    const totalGrowthImpact = 
      temperatureImpact.growthFactor * impactWeights.temperature +
      precipitationImpact.growthFactor * impactWeights.precipitation +
      sunlightImpact.growthFactor * impactWeights.sunlight +
      humidityImpact.growthFactor * impactWeights.humidity +
      windImpact.growthFactor * impactWeights.wind;
    
    // 评估胁迫状态
    const stressConditions = [];
    
    if (temperatureImpact.stress) stressConditions.push(temperatureImpact.stress);
    if (precipitationImpact.stress) stressConditions.push(precipitationImpact.stress);
    if (humidityImpact.stress) stressConditions.push(humidityImpact.stress);
    if (windImpact.stress) stressConditions.push(windImpact.stress);
    
    // 可能出现的形态变化
    const morphologicalChanges = this.predictMorphologicalChanges(
      weatherData, 
      growthStage, 
      stressConditions
    );
    
    return {
      totalGrowthImpact,
      detail: {
        temperature: temperatureImpact,
        precipitation: precipitationImpact,
        sunlight: sunlightImpact,
        humidity: humidityImpact,
        wind: windImpact
      },
      stressConditions,
      morphologicalChanges
    };
  }
  
  /**
   * 计算温度影响
   * @param {number} temperature - 温度(°C)
   * @param {string} stage - 生长阶段
   * @returns {Object} - 温度影响系数
   */
  calculateTemperatureImpact(temperature, stage) {
    const params = WEATHER_IMPACT_FACTORS.temperature.growth[stage];
    const { optimal, stress } = WEATHER_IMPACT_FACTORS.temperature;
    
    // 使用高斯响应曲线计算温度影响
    // f(x) = a + b * exp(-(x-c)^2 / (2*d^2))
    const growthFactor = params.a + params.b * 
      Math.exp(-Math.pow(temperature - params.c, 2) / (2 * Math.pow(params.d, 2)));
    
    // 评估温度胁迫
    let stressCondition = null;
    if (temperature <= stress.cold) {
      stressCondition = 'cold_stress';
    } else if (temperature >= stress.heat) {
      stressCondition = 'heat_stress';
    }
    
    return {
      growthFactor: Math.max(0, Math.min(1, growthFactor)), // 限制在0-1范围内
      stress: stressCondition,
      optimal: (temperature >= optimal.min && temperature <= optimal.max)
    };
  }
  
  /**
   * 计算降水影响
   * @param {number} precipitation - 降水量(mm/day)
   * @param {string} stage - 生长阶段
   * @returns {Object} - 降水影响系数
   */
  calculatePrecipitationImpact(precipitation, stage) {
    const params = WEATHER_IMPACT_FACTORS.precipitation.growth[stage];
    const { stress } = WEATHER_IMPACT_FACTORS.precipitation;
    
    let growthFactor;
    
    // 梯形响应曲线
    if (precipitation < params.min) {
      // 低于最低值，线性下降
      growthFactor = Math.max(0, precipitation / params.min * params.sensitivity);
    } else if (precipitation > params.max) {
      // 高于最高值，线性下降
      growthFactor = Math.max(0, (1 - (precipitation - params.max) / params.max) * params.sensitivity);
    } else {
      // 最佳范围内
      growthFactor = params.sensitivity;
    }
    
    // 评估降水胁迫
    let stressCondition = null;
    if (precipitation <= stress.drought) {
      stressCondition = 'drought_stress';
    } else if (precipitation >= stress.flood) {
      stressCondition = 'flood_stress';
    }
    
    return {
      growthFactor: Math.max(0, Math.min(1, growthFactor)), // 限制在0-1范围内
      stress: stressCondition,
      optimal: (precipitation >= params.min && precipitation <= params.max)
    };
  }
  
  /**
   * 计算光照影响
   * @param {number} sunlight - 光照时间(hours/day)
   * @param {string} stage - 生长阶段
   * @returns {Object} - 光照影响系数
   */
  calculateSunlightImpact(sunlight, stage) {
    const params = WEATHER_IMPACT_FACTORS.sunlight.growth[stage];
    
    let growthFactor;
    
    // 梯形响应曲线
    if (sunlight < params.min) {
      // 低于最低值，线性下降
      growthFactor = Math.max(0, sunlight / params.min * params.sensitivity);
    } else if (sunlight > params.max) {
      // 高于最高值，线性下降
      growthFactor = Math.max(0, (1 - (sunlight - params.max) / params.max) * params.sensitivity);
    } else {
      // 最佳范围内
      growthFactor = params.sensitivity;
    }
    
    return {
      growthFactor: Math.max(0, Math.min(1, growthFactor)), // 限制在0-1范围内
      optimal: (sunlight >= params.min && sunlight <= params.max)
    };
  }
  
  /**
   * 计算湿度影响
   * @param {number} humidity - 湿度(%)
   * @param {string} stage - 生长阶段
   * @returns {Object} - 湿度影响系数
   */
  calculateHumidityImpact(humidity, stage) {
    const params = WEATHER_IMPACT_FACTORS.humidity.growth[stage];
    const { disease } = WEATHER_IMPACT_FACTORS.humidity;
    
    let growthFactor;
    
    // 梯形响应曲线
    if (humidity < params.min) {
      // 低于最低值，线性下降
      growthFactor = Math.max(0, humidity / params.min * params.sensitivity);
    } else if (humidity > params.max) {
      // 高于最高值，线性下降
      growthFactor = Math.max(0, (1 - (humidity - params.max) / params.max) * params.sensitivity);
    } else {
      // 最佳范围内
      growthFactor = params.sensitivity;
    }
    
    // 评估湿度胁迫
    let stressCondition = null;
    if (humidity >= disease.risk) {
      stressCondition = 'disease_risk';
    }
    
    return {
      growthFactor: Math.max(0, Math.min(1, growthFactor)), // 限制在0-1范围内
      stress: stressCondition,
      optimal: (humidity >= params.min && humidity <= params.max)
    };
  }
  
  /**
   * 计算风速影响
   * @param {number} windSpeed - 风速(m/s)
   * @param {string} stage - 生长阶段
   * @returns {Object} - 风速影响系数
   */
  calculateWindImpact(windSpeed, stage) {
    const { optimal, damage } = WEATHER_IMPACT_FACTORS.windSpeed;
    
    let growthFactor;
    
    // 风速影响曲线
    if (windSpeed <= optimal.max) {
      // 正常范围内，轻微促进生长（通风效果）
      growthFactor = 0.9 + 0.1 * (windSpeed / optimal.max);
    } else if (windSpeed < damage.risk) {
      // 较高风速，线性下降
      growthFactor = 1.0 - 0.3 * ((windSpeed - optimal.max) / (damage.risk - optimal.max));
    } else if (windSpeed < damage.severe) {
      // 风害风险，显著下降
      growthFactor = 0.7 - 0.5 * ((windSpeed - damage.risk) / (damage.severe - damage.risk));
    } else {
      // 严重风害，最低生长率
      growthFactor = 0.2;
    }
    
    // 评估风速胁迫
    let stressCondition = null;
    if (windSpeed >= damage.risk) {
      stressCondition = 'wind_damage';
    }
    
    return {
      growthFactor: Math.max(0, Math.min(1, growthFactor)), // 限制在0-1范围内
      stress: stressCondition,
      optimal: (windSpeed >= optimal.min && windSpeed <= optimal.max)
    };
  }
  
  /**
   * 预测可能的形态变化
   * @param {Object} weatherData - 天气数据
   * @param {string} stage - 生长阶段
   * @param {Array} stressConditions - 胁迫条件列表
   * @returns {Array} - 可能的形态变化列表
   */
  predictMorphologicalChanges(weatherData, stage, stressConditions) {
    const changes = [];
    
    // 根据胁迫条件预测形态变化
    for (const stress of stressConditions) {
      switch (stress) {
        case 'drought_stress':
          changes.push('leaf_curling');
          changes.push('reduced_height');
          break;
        case 'flood_stress':
          changes.push('adventitious_roots');
          changes.push('chlorosis');
          break;
        case 'cold_stress':
          changes.push('purple_leaves');
          changes.push('stunted_growth');
          break;
        case 'heat_stress':
          changes.push('leaf_scorching');
          changes.push('accelerated_senescence');
          break;
        case 'disease_risk':
          changes.push('leaf_spots');
          changes.push('fungal_growth');
          break;
        case 'wind_damage':
          changes.push('broken_stems');
          changes.push('leaning_plants');
          break;
      }
    }
    
    // 特殊生长阶段特有的变化
    if (stage === GrowthStage.FLOWERING && weatherData.temperature > 35) {
      changes.push('pollen_sterility');
    }
    
    if (stage === GrowthStage.GRAIN_FILLING && weatherData.temperature < 15) {
      changes.push('delayed_maturity');
    }
    
    return [...new Set(changes)]; // 去重
  }
  
  /**
   * 应用天气影响到玉米生长模型
   * @param {Object} cornPlant - 玉米植物模型
   * @param {Object} weatherData - 天气数据
   * @param {number} timeStep - 时间步长（小时）
   * @returns {Object} - 更新后的玉米植物模型
   */
  applyWeatherImpact(cornPlant, weatherData, timeStep) {
    // 计算当前生长阶段的天气影响
    const impact = this.calculateWeatherImpact(weatherData, cornPlant.growthStage);
    
    // 计算生长速率调整因子
    const growthRateAdjustment = impact.totalGrowthImpact;
    
    // 应用生长速率调整
    cornPlant.height += cornPlant.heightGrowthRate * growthRateAdjustment * (timeStep / 24);
    cornPlant.leafCount += cornPlant.leafGrowthRate * growthRateAdjustment * (timeStep / 24);
    
    // 更新生长阶段天数
    cornPlant.daysInCurrentStage += timeStep / 24;
    
    // 应用形态变化
    cornPlant.morphologicalChanges = impact.morphologicalChanges;
    
    // 记录天气影响历史
    cornPlant.weatherImpactHistory.push({
      timestamp: Date.now(),
      impact,
      weatherData
    });
    
    // 限制历史记录大小
    if (cornPlant.weatherImpactHistory.length > 100) {
      cornPlant.weatherImpactHistory = cornPlant.weatherImpactHistory.slice(-100);
    }
    
    return cornPlant;
  }
}

module.exports = new WeatherImpactService();