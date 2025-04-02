import { Request, Response, NextFunction } from 'express';
import logger from '../utils/logger';

/**
 * 无障碍中间件
 * 处理用户的无障碍需求，调整响应格式
 */
export const accessibilityMiddleware = (req: Request, res: Response, next: NextFunction): void => {
  // 从请求中获取无障碍配置
  const accessibilityConfig = req.headers['x-accessibility-config'] 
    ? JSON.parse(req.headers['x-accessibility-config'] as string)
    : {};
    
  // 保存到请求对象中，供后续处理使用
  req.accessibilityConfig = accessibilityConfig;
  
  // 记录无障碍需求
  if (Object.keys(accessibilityConfig).length > 0) {
    logger.info('处理无障碍需求', { accessibilityConfig });
  }
  
  // 定义新的json方法，用于支持无障碍格式
  const originalJsonMethod = res.json;
  res.json = function(body) {
    // 如果启用了导盲支持，添加适合屏幕阅读器的描述
    if (accessibilityConfig.screenReader) {
      if (body.data && body.data.accessibilityDescription === undefined) {
        // 为不同类型的响应生成无障碍描述
        if (body.data.tongueAnalysis) {
          body.data.accessibilityDescription = generateTongueAccessibilityDescription(body.data.tongueAnalysis);
        } else if (body.data.faceAnalysis) {
          body.data.accessibilityDescription = generateFaceAccessibilityDescription(body.data.faceAnalysis);
        }
      }
    }
    
    // 调用原始的json方法
    return originalJsonMethod.call(this, body);
  };
  
  next();
};

/**
 * 生成舌诊无障碍描述
 */
function generateTongueAccessibilityDescription(tongueAnalysis: any): string {
  try {
    const { color, coating, shape, moisture, cracks } = tongueAnalysis;
    
    let description = '舌诊分析结果: ';
    
    if (color) description += `舌色为${color}，`;
    if (coating) description += `舌苔为${coating}，`;
    if (shape) description += `舌形为${shape}，`;
    if (moisture) description += `舌的湿润度为${moisture}，`;
    if (cracks && cracks.length > 0) description += `舌面有${cracks.join('、')}，`;
    
    // 添加健康建议
    if (tongueAnalysis.healthImplications) {
      description += `健康提示: ${tongueAnalysis.healthImplications}`;
    }
    
    return description;
  } catch (error) {
    logger.error('生成舌诊无障碍描述失败', { error });
    return '舌诊分析已完成，但无法生成详细语音描述。';
  }
}

/**
 * 生成面诊无障碍描述
 */
function generateFaceAccessibilityDescription(faceAnalysis: any): string {
  try {
    const { complexion, features, expressions, areas } = faceAnalysis;
    
    let description = '面诊分析结果: ';
    
    if (complexion) description += `面色为${complexion}，`;
    
    if (features && features.length > 0) {
      description += `面部特征: ${features.join('、')}，`;
    }
    
    if (expressions) description += `面部表情: ${expressions}，`;
    
    if (areas && Object.keys(areas).length > 0) {
      description += '面部区域分析: ';
      Object.entries(areas).forEach(([area, status]) => {
        description += `${area}显示${status}，`;
      });
    }
    
    // 添加健康建议
    if (faceAnalysis.healthImplications) {
      description += `健康提示: ${faceAnalysis.healthImplications}`;
    }
    
    return description;
  } catch (error) {
    logger.error('生成面诊无障碍描述失败', { error });
    return '面诊分析已完成，但无法生成详细语音描述。';
  }
}

// 扩展Request接口，添加accessibilityConfig属性
declare global {
  namespace Express {
    interface Request {
      accessibilityConfig?: {
        screenReader?: boolean;
        highContrast?: boolean;
        largeText?: boolean;
        simplifiedUI?: boolean;
        voiceGuidance?: boolean;
      };
    }
  }
}
