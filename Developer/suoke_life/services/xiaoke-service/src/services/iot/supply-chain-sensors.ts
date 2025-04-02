import { v4 as uuidv4 } from 'uuid';
import { logger } from '../../utils/logger';
import { trackEvent } from '../supply-chain/tracking';
import { sendAlert } from '../supply-chain/alerts';
import { SupplyChainEvent } from '../../models/supply-chain.model';

// 传感器数据类型
export interface SensorData {
  sensorId: string;
  productId: string;
  type: 'temperature' | 'humidity' | 'light' | 'pressure' | 'motion' | 'gas' | 'location';
  value: number;
  unit: string;
  timestamp: string;
  location?: string;
  batchId?: string;
  metadata?: Record<string, any>;
}

// 存储传感器历史数据
const sensorDataStore: SensorData[] = [];

// 传感器阈值配置
const thresholdConfig: Record<string, {min: number, max: number, unit: string}> = {
  temperature: { min: 0, max: 30, unit: '°C' },
  humidity: { min: 20, max: 80, unit: '%' },
  light: { min: 0, max: 1000, unit: 'lux' },
  pressure: { min: 900, max: 1100, unit: 'hPa' },
  gas: { min: 0, max: 100, unit: 'ppm' }
};

/**
 * 接收传感器数据
 */
export const receiveSensorData = async (data: SensorData): Promise<SensorData> => {
  try {
    logger.info(`接收传感器数据: ${data.type} - ${data.productId}`);
    
    // 验证数据
    if (!data.sensorId || !data.productId || !data.type || data.value === undefined) {
      throw new Error('传感器数据不完整');
    }
    
    // 添加时间戳（如果未提供）
    if (!data.timestamp) {
      data.timestamp = new Date().toISOString();
    }
    
    // 存储数据
    sensorDataStore.push(data);
    
    // 检查阈值，判断是否需要创建事件或警报
    await checkThresholds(data);
    
    logger.info(`传感器数据已保存: ${data.sensorId}`);
    return data;
  } catch (error) {
    logger.error('处理传感器数据失败:', error);
    throw new Error(`处理传感器数据失败: ${(error as Error).message}`);
  }
};

/**
 * 检查传感器数据阈值
 */
const checkThresholds = async (data: SensorData): Promise<void> => {
  try {
    const config = thresholdConfig[data.type];
    
    if (!config) {
      return;
    }
    
    // 检查是否超出阈值
    if (data.value < config.min || data.value > config.max) {
      logger.warn(`传感器数据超出阈值: ${data.type} - ${data.value}${config.unit}`);
      
      // 创建供应链事件
      const event: SupplyChainEvent = {
        productId: data.productId,
        type: 'quality_issue',
        description: `环境条件异常: ${data.type} ${data.value}${config.unit}`,
        timestamp: data.timestamp,
        location: data.location,
        metadata: {
          sensorId: data.sensorId,
          sensorType: data.type,
          value: data.value,
          unit: data.unit,
          threshold: `${config.min}-${config.max}${config.unit}`,
          batchId: data.batchId
        }
      };
      
      // 记录事件
      const recordedEvent = trackEvent(event);
      
      // 发送警报
      await sendAlert({
        title: '环境条件异常',
        message: `产品 ${data.productId} 的 ${getChineseSensorType(data.type)} 超出安全范围: ${data.value}${config.unit}`,
        level: getSeverityLevel(data),
        productId: data.productId,
        eventId: recordedEvent.id,
        timestamp: data.timestamp,
        status: 'pending'
      });
    }
  } catch (error) {
    logger.error('检查传感器阈值失败:', error);
  }
};

/**
 * 获取传感器数据的严重性级别
 */
const getSeverityLevel = (data: SensorData): 'info' | 'warning' | 'critical' => {
  const config = thresholdConfig[data.type];
  
  if (!config) {
    return 'info';
  }
  
  const range = config.max - config.min;
  const deviation = Math.max(data.value - config.max, config.min - data.value);
  const deviationPercentage = (deviation / range) * 100;
  
  if (deviationPercentage > 50) {
    return 'critical';
  } else if (deviationPercentage > 20) {
    return 'warning';
  } else {
    return 'info';
  }
};

/**
 * 获取产品的环境数据历史
 */
export const getProductEnvironmentData = (productId: string, type?: string, limit: number = 100): SensorData[] => {
  let data = sensorDataStore.filter(d => d.productId === productId);
  
  if (type) {
    data = data.filter(d => d.type === type);
  }
  
  // 按时间排序，最新的在前
  data.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
  
  return data.slice(0, limit);
};

/**
 * 获取传感器类型的中文名称
 */
const getChineseSensorType = (type: string): string => {
  const typeNames: Record<string, string> = {
    'temperature': '温度',
    'humidity': '湿度',
    'light': '光照',
    'pressure': '气压',
    'motion': '移动',
    'gas': '气体',
    'location': '位置'
  };
  
  return typeNames[type] || type;
};