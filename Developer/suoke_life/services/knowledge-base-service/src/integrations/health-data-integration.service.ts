/**
 * 健康数据集成服务
 * 提供从外部健康数据源进行数据整合的功能
 */

import { injectable, inject } from 'inversify';
import axios from 'axios';
import { Logger } from '../utils/logger';
import { ConfigService } from '../utils/config.service';
import { TYPES } from '../types';
import { 
  IMultimodalHealthKnowledge, 
  IEnvironmentalHealthKnowledge,
  IPrecisionMedicineKnowledge
} from '../interfaces';

@injectable()
export class HealthDataIntegrationService {
  private logger = new Logger('HealthDataIntegrationService');
  private ragServiceUrl: string;
  private userServiceUrl: string;
  private agentCoordinatorUrl: string;
  private xiaoaiServiceUrl: string;
  private webSearchServiceUrl: string;
  private wearableServiceUrl: string;

  constructor(
    @inject(TYPES.ConfigService) private configService: ConfigService
  ) {
    this.ragServiceUrl = this.configService.get('services.ragService');
    this.userServiceUrl = this.configService.get('services.userService');
    this.agentCoordinatorUrl = this.configService.get('services.agentCoordinatorService');
    this.xiaoaiServiceUrl = this.configService.get('services.xiaoaiService');
    this.webSearchServiceUrl = this.configService.get('services.webSearchService');
    this.wearableServiceUrl = this.configService.get('services.wearableService');
  }

  /**
   * 从可穿戴设备服务获取数据
   * @param userId 用户ID
   * @param deviceType 设备类型
   * @param startDate 开始日期
   * @param endDate 结束日期
   */
  async getWearableData(
    userId: string, 
    deviceType?: string, 
    startDate?: Date, 
    endDate?: Date
  ): Promise<any> {
    try {
      const response = await axios.get(`${this.wearableServiceUrl}/api/data`, {
        params: {
          userId,
          deviceType,
          startDate: startDate?.toISOString(),
          endDate: endDate?.toISOString()
        }
      });
      return response.data;
    } catch (error) {
      this.logger.error('Failed to fetch wearable data', error);
      throw new Error('Failed to fetch wearable data');
    }
  }

  /**
   * 获取环境健康数据
   * @param location 位置
   * @param factorTypes 环境因素类型
   */
  async getEnvironmentalData(
    location: string, 
    factorTypes?: string[]
  ): Promise<any> {
    try {
      const response = await axios.get(`${this.webSearchServiceUrl}/api/environmental`, {
        params: {
          location,
          factorTypes: factorTypes?.join(',')
        }
      });
      return response.data;
    } catch (error) {
      this.logger.error('Failed to fetch environmental data', error);
      throw new Error('Failed to fetch environmental data');
    }
  }

  /**
   * 获取用户健康状况
   * @param userId 用户ID
   */
  async getUserHealthProfile(userId: string): Promise<any> {
    try {
      const response = await axios.get(`${this.userServiceUrl}/api/users/${userId}/health-profile`);
      return response.data;
    } catch (error) {
      this.logger.error('Failed to fetch user health profile', error);
      throw new Error('Failed to fetch user health profile');
    }
  }

  /**
   * 处理和分析健康数据，生成洞察
   * @param userId 用户ID
   * @param dataType 数据类型
   * @param rawData 原始数据
   */
  async processHealthData(
    userId: string, 
    dataType: string, 
    rawData: any
  ): Promise<any> {
    try {
      const response = await axios.post(`${this.agentCoordinatorUrl}/api/analyze/health-data`, {
        userId,
        dataType,
        data: rawData
      });
      return response.data;
    } catch (error) {
      this.logger.error('Failed to process health data', error);
      throw new Error('Failed to process health data');
    }
  }

  /**
   * 为知识数据添加多模态信息
   * @param knowledge 知识数据
   * @param modalData 多模态数据
   */
  async enrichWithMultimodalData(
    knowledge: IMultimodalHealthKnowledge, 
    modalData: any
  ): Promise<IMultimodalHealthKnowledge> {
    try {
      // 根据模态类型进行不同的处理
      switch (knowledge.modalityType) {
        case 'image':
          // 处理图像相关数据
          if (modalData.imageFeatures) {
            knowledge.imageFeatures = modalData.imageFeatures;
          }
          break;
        case 'audio':
          // 处理音频相关数据
          if (modalData.audioFeatures) {
            knowledge.audioFeatures = modalData.audioFeatures;
          }
          break;
        case 'wearable':
          // 处理可穿戴设备数据
          if (modalData.wearableMetrics) {
            knowledge.wearableMetrics = modalData.wearableMetrics;
          }
          break;
        case 'environmental':
          // 处理环境数据
          if (modalData.environmentalFactors) {
            knowledge.environmentalFactors = modalData.environmentalFactors;
          }
          break;
      }
      
      // 添加分析方法和数据要求
      if (modalData.analysisMethod) {
        knowledge.analysisMethod = modalData.analysisMethod;
      }
      
      if (modalData.dataRequirements) {
        knowledge.dataRequirements = modalData.dataRequirements;
      }
      
      return knowledge;
    } catch (error) {
      this.logger.error('Failed to enrich with multimodal data', error);
      throw new Error('Failed to enrich with multimodal data');
    }
  }

  /**
   * 为环境健康知识添加实时数据
   * @param knowledge 环境健康知识
   * @param location 位置
   */
  async enrichWithEnvironmentalData(
    knowledge: IEnvironmentalHealthKnowledge, 
    location: string
  ): Promise<IEnvironmentalHealthKnowledge> {
    try {
      // 获取实时环境数据
      const envData = await this.getEnvironmentalData(location, [knowledge.factorType]);
      
      // 使用实时数据更新知识
      if (envData) {
        // 添加季节性和气候信息
        if (envData.seasonalData) {
          knowledge.seasonalVariations = envData.seasonalData.description;
        }
        
        // 添加天气依赖性
        if (envData.weatherDependence) {
          knowledge.weatherDependence = envData.weatherDependence;
        }
        
        // 根据当前环境状况更新安全标准
        if (envData.currentLevels && knowledge.safetyStandards) {
          knowledge.safetyStandards = knowledge.safetyStandards.map(standard => {
            const currentLevel = envData.currentLevels[standard.organization];
            if (currentLevel) {
              return {
                ...standard,
                currentLevel,
                status: this.compareEnvironmentalLevels(currentLevel, standard.limit)
              };
            }
            return standard;
          });
        }
      }
      
      return knowledge;
    } catch (error) {
      this.logger.error('Failed to enrich with environmental data', error);
      throw new Error('Failed to enrich with environmental data');
    }
  }

  /**
   * 为精准医学知识添加用户特定数据
   * @param knowledge 精准医学知识
   * @param userId 用户ID
   */
  async enrichWithPersonalizedData(
    knowledge: IPrecisionMedicineKnowledge, 
    userId: string
  ): Promise<IPrecisionMedicineKnowledge> {
    try {
      // 获取用户健康画像
      const userProfile = await this.getUserHealthProfile(userId);
      
      if (userProfile) {
        // 添加个性化建议
        if (knowledge.personalizationFactors && userProfile.geneticFactors) {
          // 根据用户基因特征过滤个性化因素
          const relevantFactors = knowledge.personalizationFactors.filter(factor => 
            userProfile.geneticFactors.some((gf: any) => gf.name === factor || gf.category === factor)
          );
          
          knowledge.personalizationFactors = relevantFactors;
          
          // 添加适用的生物标记物
          if (userProfile.biomarkers) {
            knowledge.applicableBiomarkers = userProfile.biomarkers
              .filter((bm: any) => bm.relevantConditions?.some((rc: string) => 
                knowledge.diseaseAssociations?.some(da => da.disease === rc)
              ))
              .map((bm: any) => bm.name);
          }
        }
      }
      
      return knowledge;
    } catch (error) {
      this.logger.error('Failed to enrich with personalized data', error);
      throw new Error('Failed to enrich with personalized data');
    }
  }

  /**
   * 比较环境水平
   * @param current 当前水平
   * @param standard 标准水平
   */
  private compareEnvironmentalLevels(current: string, standard: string): 'safe' | 'warning' | 'danger' {
    // 简化版本的环境水平比较，实际实现可能更复杂
    const currentValue = parseFloat(current);
    const standardValue = parseFloat(standard);
    
    if (isNaN(currentValue) || isNaN(standardValue)) {
      return 'warning'; // 无法比较时返回警告
    }
    
    if (currentValue <= standardValue * 0.8) {
      return 'safe';
    } else if (currentValue <= standardValue) {
      return 'warning';
    } else {
      return 'danger';
    }
  }
}