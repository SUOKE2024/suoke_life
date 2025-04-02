import axios from 'axios';
import { Logger } from '../utils/logger';

/**
 * 健康建议生成器
 * 负责根据触诊分析结果生成个性化健康建议和保健方案
 */
export class HealthSuggestionsGenerator {
  private tcmKnowledgeServiceUrl: string;

  constructor() {
    this.tcmKnowledgeServiceUrl = process.env.TCM_KNOWLEDGE_SERVICE_URL || 'http://localhost:3006/api/tcm-knowledge';
  }

  /**
   * 生成健康建议
   * @param patientId 患者ID
   * @param constitutionTypes 体质类型
   * @param healthImbalances 健康不平衡
   * @returns 健康建议列表
   */
  public async generateSuggestions(
    patientId: string,
    constitutionTypes: string[],
    healthImbalances: string[]
  ): Promise<string[]> {
    try {
      Logger.info(`为患者 ${patientId} 生成健康建议`);
      
      // 尝试从知识服务获取建议
      try {
        const externalSuggestions = await this.fetchExternalSuggestions(
          patientId,
          constitutionTypes,
          healthImbalances
        );
        
        if (externalSuggestions && externalSuggestions.length > 0) {
          return externalSuggestions;
        }
      } catch (error) {
        Logger.warn('从知识服务获取健康建议失败，使用本地生成', { error });
      }
      
      // 如果外部服务失败，使用本地生成逻辑
      const suggestions: string[] = [];
      
      // 基于体质类型生成建议
      const constitutionSuggestions = this.generateConstitutionBasedSuggestions(constitutionTypes);
      suggestions.push(...constitutionSuggestions);
      
      // 基于健康不平衡生成建议
      const imbalanceSuggestions = this.generateImbalanceBasedSuggestions(healthImbalances);
      suggestions.push(...imbalanceSuggestions);
      
      // 组合建议，确保没有重复
      const uniqueSuggestions = Array.from(new Set(suggestions));
      
      // 如果建议太少，添加一些通用建议
      if (uniqueSuggestions.length < 3) {
        uniqueSuggestions.push(...this.getGeneralHealthSuggestions());
      }
      
      return uniqueSuggestions;
    } catch (error) {
      Logger.error(`生成健康建议失败`, { error, patientId });
      // 出错时返回通用建议
      return this.getGeneralHealthSuggestions();
    }
  }

  /**
   * 从外部知识服务获取健康建议
   */
  private async fetchExternalSuggestions(
    patientId: string,
    constitutionTypes: string[],
    healthImbalances: string[]
  ): Promise<string[]> {
    const response = await axios.post(`${this.tcmKnowledgeServiceUrl}/suggestions/touch-diagnosis`, {
      patientId,
      constitutionTypes,
      healthImbalances
    });
    
    return response.data.suggestions || [];
  }

  /**
   * 基于体质类型生成建议
   */
  private generateConstitutionBasedSuggestions(constitutionTypes: string[]): string[] {
    const suggestions: string[] = [];
    
    for (const constitution of constitutionTypes) {
      switch (constitution) {
        case '气虚体质':
          suggestions.push('保持充足睡眠，避免过度劳累');
          suggestions.push('建议适量食用黄芪、人参、大枣等补气食材');
          suggestions.push('建议进行缓和的运动，如散步、太极拳等');
          break;
          
        case '阳虚体质':
          suggestions.push('注意保暖，避免受寒');
          suggestions.push('建议食用温热食物，如生姜、桂圆、羊肉等');
          suggestions.push('可适当晒太阳，增加阳气');
          break;
          
        case '阴虚体质':
          suggestions.push('避免辛辣、煎炸、酒类等温热食物');
          suggestions.push('建议食用滋阴食物，如银耳、百合、梨等');
          suggestions.push('保持情绪平和，避免过度兴奋');
          break;
          
        case '痰湿体质':
          suggestions.push('饮食宜清淡，避免油腻、甜腻食物');
          suggestions.push('建议多食用利水渗湿的食物，如薏苡仁、赤小豆等');
          suggestions.push('加强运动，促进水湿代谢');
          break;
          
        case '湿热体质':
          suggestions.push('避免辛辣、油腻、酒类等助热生湿食物');
          suggestions.push('建议食用清热利湿食物，如绿豆、冬瓜、苦瓜等');
          suggestions.push('保持情绪稳定，避免熬夜');
          break;
          
        case '血瘀体质':
          suggestions.push('建议适量运动，促进血液循环');
          suggestions.push('可食用活血化瘀食物，如黑木耳、红枣、桃仁等');
          suggestions.push('避免长时间保持同一姿势，适当按摩促进血液循环');
          break;
          
        case '肝郁体质':
          suggestions.push('保持乐观心态，学会情绪疏导');
          suggestions.push('建议食用疏肝理气食物，如柴胡、佛手、玫瑰花等');
          suggestions.push('可进行舒缓性运动，如瑜伽、太极等');
          break;
      }
    }
    
    return suggestions;
  }

  /**
   * 基于健康不平衡生成建议
   */
  private generateImbalanceBasedSuggestions(healthImbalances: string[]): string[] {
    const suggestions: string[] = [];
    
    for (const imbalance of healthImbalances) {
      if (imbalance.includes('心肺相关')) {
        suggestions.push('避免情绪波动，保持心情舒畅');
        suggestions.push('建议进行有氧运动，增强心肺功能');
      }
      
      if (imbalance.includes('肝胆相关') || imbalance.includes('肝郁气滞')) {
        suggestions.push('保持情绪稳定，避免焦虑、愤怒等情绪');
        suggestions.push('建议多食用柑橘类水果、绿叶蔬菜等');
      }
      
      if (imbalance.includes('脾胃相关') || imbalance.includes('胃脘相关')) {
        suggestions.push('饮食规律，少食多餐，细嚼慢咽');
        suggestions.push('避免过度劳累，保持适当运动');
      }
      
      if (imbalance.includes('肾与膀胱相关')) {
        suggestions.push('保持腰部温暖，避免寒冷刺激');
        suggestions.push('适量补充优质蛋白质，如鱼、瘦肉等');
      }
      
      if (imbalance.includes('表证')) {
        suggestions.push('注意防寒保暖，避免风寒侵袭');
        suggestions.push('可适当食用葱、姜等发散风寒的食物');
      }
      
      if (imbalance.includes('里证')) {
        suggestions.push('饮食宜清淡，避免过度辛辣刺激');
        suggestions.push('保持情绪平和，避免过度疲劳');
      }
      
      if (imbalance.includes('寒证')) {
        suggestions.push('注意保暖，避免受凉');
        suggestions.push('可食用温性食物，如羊肉、生姜等');
      }
      
      if (imbalance.includes('热证') || imbalance.includes('实热证')) {
        suggestions.push('避免辛辣、油腻、烟酒等刺激性食物');
        suggestions.push('可食用清热食物，如绿豆、苦瓜等');
      }
      
      if (imbalance.includes('气滞证')) {
        suggestions.push('保持心情舒畅，避免情绪抑郁');
        suggestions.push('可适当进行腹部按摩，促进气机流通');
      }
      
      if (imbalance.includes('痰湿证') || imbalance.includes('水湿内停')) {
        suggestions.push('饮食宜清淡，避免甜腻、油腻食物');
        suggestions.push('加强运动，促进水湿代谢');
      }
    }
    
    return suggestions;
  }

  /**
   * 获取通用健康建议
   */
  private getGeneralHealthSuggestions(): string[] {
    return [
      '保持规律作息，确保充足睡眠',
      '均衡饮食，多摄入蔬果、粗粮',
      '适量运动，每周至少150分钟中等强度活动',
      '保持心情愉快，避免过度紧张和焦虑',
      '避免烟酒，减少咖啡因摄入',
      '定期进行健康检查，及时了解身体状况'
    ];
  }
} 