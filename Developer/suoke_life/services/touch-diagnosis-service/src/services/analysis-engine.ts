import { Logger } from '../utils/logger';
import { 
  PulseType, 
  AbdominalFindingType, 
  TouchLocation 
} from '../interfaces/touch-diagnosis.interface';

const logger = new Logger('AnalysisEngine');

/**
 * 触诊分析引擎
 * 负责分析脉诊和腹诊数据，生成诊断结论
 */
export class AnalysisEngine {
  /**
   * 执行触诊综合分析
   */
  performIntegratedAnalysis(touchData: any): any {
    logger.info(`执行触诊综合分析: ${touchData.patientId}`);
    
    try {
      // 分析脉诊数据
      const pulseAnalysisResult = this.analyzePulseDiagnosis(touchData.pulseFindings || []);
      
      // 分析腹诊数据
      const abdominalAnalysisResult = this.analyzeAbdominalDiagnosis(touchData.abdominalFindings || []);
      
      // 整合分析结果
      const overallAssessment = this.generateOverallAssessment(pulseAnalysisResult, abdominalAnalysisResult);
      
      // 计算诊断置信度
      const confidence = this.calculateConfidence(touchData);
      
      // 生成健康建议
      const healthSuggestions = this.generateHealthSuggestions(
        pulseAnalysisResult, 
        abdominalAnalysisResult
      );
      
      return {
        overallAssessment,
        confidence,
        healthSuggestions
      };
    } catch (error) {
      logger.error('触诊综合分析失败', { error });
      throw error;
    }
  }

  /**
   * 分析脉诊数据
   */
  private analyzePulseDiagnosis(pulseFindings: any[]): any {
    logger.debug('分析脉诊数据');
    
    if (!pulseFindings || pulseFindings.length === 0) {
      return {
        conclusion: '未提供脉诊数据',
        pulseCharacteristics: [],
        organImplications: [],
        severity: 0
      };
    }
    
    // 分析每个位置的脉象特征
    const pulseCharacteristics: string[] = [];
    const organImplications: string[] = [];
    let overallSeverity = 0;
    
    // 计算各脉类型的出现频率
    const pulseTypeCounts: Record<string, number> = {};
    pulseFindings.forEach(finding => {
      const pulseType = finding.pulseType;
      pulseTypeCounts[pulseType] = (pulseTypeCounts[pulseType] || 0) + 1;
      
      // 记录各位置的脉象特征
      let locationName = '';
      switch (finding.location) {
        case TouchLocation.RIGHT_WRIST:
          locationName = '右寸';
          organImplications.push(this.getOrganImplicationByPulseType(pulseType, '肺'));
          break;
        case TouchLocation.RIGHT_MIDDLE:
          locationName = '右关';
          organImplications.push(this.getOrganImplicationByPulseType(pulseType, '脾'));
          break;
        case TouchLocation.RIGHT_CUBIT:
          locationName = '右尺';
          organImplications.push(this.getOrganImplicationByPulseType(pulseType, '肾'));
          break;
        case TouchLocation.LEFT_WRIST:
          locationName = '左寸';
          organImplications.push(this.getOrganImplicationByPulseType(pulseType, '心'));
          break;
        case TouchLocation.LEFT_MIDDLE:
          locationName = '左关';
          organImplications.push(this.getOrganImplicationByPulseType(pulseType, '肝'));
          break;
        case TouchLocation.LEFT_CUBIT:
          locationName = '左尺';
          organImplications.push(this.getOrganImplicationByPulseType(pulseType, '肾'));
          break;
      }
      
      if (locationName) {
        pulseCharacteristics.push(`${locationName}脉：${this.getPulseTypeDescription(pulseType)}`);
      }
      
      // 计算严重程度
      overallSeverity += this.getPulseSeverity(pulseType, finding.strength);
    });
    
    // 获取主要脉象类型
    const dominantPulseTypes = Object.entries(pulseTypeCounts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 2)
      .map(([type, _]) => type);
    
    // 生成脉诊结论
    const conclusion = this.generatePulseConclusion(dominantPulseTypes, pulseCharacteristics);
    
    // 计算平均严重程度
    const averageSeverity = pulseFindings.length > 0 ? 
      overallSeverity / pulseFindings.length : 0;
    
    return {
      conclusion,
      pulseCharacteristics,
      organImplications: organImplications.filter(Boolean),
      severity: averageSeverity
    };
  }

  /**
   * 分析腹诊数据
   */
  private analyzeAbdominalDiagnosis(abdominalFindings: any[]): any {
    logger.debug('分析腹诊数据');
    
    if (!abdominalFindings || abdominalFindings.length === 0) {
      return {
        conclusion: '未提供腹诊数据',
        abdominalCharacteristics: [],
        organImplications: [],
        severity: 0
      };
    }
    
    // 分析腹诊特征
    const abdominalCharacteristics: string[] = [];
    const organImplications: string[] = [];
    let overallSeverity = 0;
    
    // 计算各发现类型的出现频率
    const findingTypeCounts: Record<string, number> = {};
    abdominalFindings.forEach(finding => {
      const findingType = finding.findingType;
      findingTypeCounts[findingType] = (findingTypeCounts[findingType] || 0) + 1;
      
      // 记录各位置的腹诊特征
      let locationName = this.getAbdominalLocationName(finding.location);
      
      if (locationName) {
        abdominalCharacteristics.push(
          `${locationName}：${this.getAbdominalFindingDescription(findingType, finding.intensity)}`
        );
      }
      
      // 添加脏腑关联
      const organImplication = this.getOrganImplicationByAbdominalFinding(finding);
      if (organImplication) {
        organImplications.push(organImplication);
      }
      
      // 计算严重程度
      overallSeverity += this.getAbdominalSeverity(findingType, finding.intensity);
    });
    
    // 获取主要发现类型
    const dominantFindingTypes = Object.entries(findingTypeCounts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 2)
      .map(([type, _]) => type);
    
    // 生成腹诊结论
    const conclusion = this.generateAbdominalConclusion(dominantFindingTypes, abdominalCharacteristics);
    
    // 计算平均严重程度
    const averageSeverity = abdominalFindings.length > 0 ? 
      overallSeverity / abdominalFindings.length : 0;
    
    return {
      conclusion,
      abdominalCharacteristics,
      organImplications: organImplications.filter(Boolean),
      severity: averageSeverity
    };
  }

  /**
   * 生成综合评估
   */
  private generateOverallAssessment(pulseAnalysis: any, abdominalAnalysis: any): string {
    logger.debug('生成综合评估');
    
    let assessment = '触诊综合分析结果：\n\n';
    
    // 添加脉诊结论
    if (pulseAnalysis.conclusion) {
      assessment += `【脉诊】${pulseAnalysis.conclusion}\n\n`;
    }
    
    // 添加腹诊结论
    if (abdominalAnalysis.conclusion) {
      assessment += `【腹诊】${abdominalAnalysis.conclusion}\n\n`;
    }
    
    // 整合脏腑相关信息
    const allOrganImplications = [
      ...pulseAnalysis.organImplications,
      ...abdominalAnalysis.organImplications
    ];
    
    if (allOrganImplications.length > 0) {
      assessment += '【脏腑相关】\n';
      assessment += Array.from(new Set(allOrganImplications)).join('\n');
      assessment += '\n\n';
    }
    
    // 计算总体状况
    const averageSeverity = (pulseAnalysis.severity + abdominalAnalysis.severity) / 2;
    
    if (averageSeverity > 0.7) {
      assessment += '综合评估：患者整体状态需要关注，建议进行进一步的中医诊疗。';
    } else if (averageSeverity > 0.4) {
      assessment += '综合评估：患者存在一定健康隐患，建议适当调理。';
    } else if (averageSeverity > 0) {
      assessment += '综合评估：患者整体状态尚可，建议保持良好的生活习惯。';
    } else {
      assessment += '综合评估：未发现明显异常。';
    }
    
    return assessment;
  }

  /**
   * 计算置信度
   */
  private calculateConfidence(data: any): number {
    logger.debug('计算触诊分析置信度');
    
    // 基础置信度
    let baseConfidence = 70;
    
    // 根据数据完整性调整置信度
    const hasPulseData = data.pulseFindings && data.pulseFindings.length > 0;
    const hasAbdominalData = data.abdominalFindings && data.abdominalFindings.length > 0;
    
    if (hasPulseData && hasAbdominalData) {
      // 脉诊和腹诊数据都有，置信度最高
      baseConfidence = 85;
    } else if (hasPulseData) {
      // 只有脉诊数据
      baseConfidence = 75;
    } else if (hasAbdominalData) {
      // 只有腹诊数据
      baseConfidence = 70;
    } else {
      // 没有任何数据
      baseConfidence = 30;
    }
    
    // 数据点数量影响
    const pulseCount = data.pulseFindings?.length || 0;
    const abdominalCount = data.abdominalFindings?.length || 0;
    
    // 调整置信度（最多增加15点）
    const dataPointAdjustment = Math.min(15, (pulseCount + abdominalCount) * 2);
    
    // 最终置信度（最高100）
    const finalConfidence = Math.min(100, baseConfidence + dataPointAdjustment);
    
    return finalConfidence;
  }

  /**
   * 生成健康建议
   */
  private generateHealthSuggestions(pulseAnalysis: any, abdominalAnalysis: any): string[] {
    logger.debug('生成触诊健康建议');
    
    const suggestions = [];
    
    // 基于脉诊的建议
    if (pulseAnalysis.pulseCharacteristics.length > 0) {
      // 按脉象类型生成建议
      pulseAnalysis.pulseCharacteristics.forEach((characteristic: string) => {
        const pulseType = this.extractPulseTypeFromCharacteristic(characteristic);
        if (pulseType) {
          const suggestion = this.getSuggestionByPulseType(pulseType);
          if (suggestion) {
            suggestions.push(suggestion);
          }
        }
      });
    }
    
    // 基于腹诊的建议
    if (abdominalAnalysis.abdominalCharacteristics.length > 0) {
      // 按腹诊发现类型生成建议
      abdominalAnalysis.abdominalCharacteristics.forEach((characteristic: string) => {
        const findingType = this.extractFindingTypeFromCharacteristic(characteristic);
        if (findingType) {
          const suggestion = this.getSuggestionByAbdominalFindingType(findingType);
          if (suggestion) {
            suggestions.push(suggestion);
          }
        }
      });
    }
    
    // 添加通用建议
    suggestions.push('保持规律作息，避免过度劳累。');
    suggestions.push('饮食宜清淡，少食辛辣刺激性食物。');
    
    // 去重
    const uniqueSuggestions = Array.from(new Set(suggestions));
    
    return uniqueSuggestions;
  }

  /**
   * 获取腹部位置名称
   */
  private getAbdominalLocationName(location: TouchLocation): string {
    switch(location) {
      case TouchLocation.EPIGASTRIUM:
        return '上腹部';
      case TouchLocation.RIGHT_UPPER:
        return '右上腹';
      case TouchLocation.LEFT_UPPER:
        return '左上腹';
      case TouchLocation.UMBILICUS:
        return '脐部';
      case TouchLocation.RIGHT_LOWER:
        return '右下腹';
      case TouchLocation.LEFT_LOWER:
        return '左下腹';
      case TouchLocation.HYPOGASTRIUM:
        return '下腹部';
      default:
        return '';
    }
  }

  /**
   * 获取脉象类型描述
   */
  private getPulseTypeDescription(pulseType: PulseType): string {
    switch(pulseType) {
      case PulseType.FLOATING:
        return '浮脉（脉搏轻取即得，重按反而减弱）';
      case PulseType.SINKING:
        return '沉脉（脉搏轻取难以感知，重按有力）';
      case PulseType.SLOW:
        return '迟脉（脉搏跳动缓慢，每分钟不足60次）';
      case PulseType.RAPID:
        return '数脉（脉搏跳动频率过快）';
      case PulseType.SLIPPERY:
        return '滑脉（脉搏圆滑流利，如珠走盘）';
      case PulseType.ROUGH:
        return '涩脉（脉搏流动不畅，艰涩迟滞）';
      case PulseType.WIRY:
        return '弦脉（脉搏紧张如弦，指下挺直）';
      case PulseType.SOFT:
        return '软脉（脉搏柔软无力）';
      case PulseType.FULL:
        return '实脉（脉搏充实有力）';
      case PulseType.EMPTY:
        return '虚脉（脉搏空虚无力）';
      case PulseType.LONG:
        return '长脉（脉搏长度超过常规）';
      case PulseType.SHORT:
        return '短脉（脉搏长度不足）';
      case PulseType.FAINT:
        return '微脉（脉搏细微难辨）';
      case PulseType.LARGE:
        return '洪脉（脉搏宏大有力）';
      case PulseType.MODERATE:
        return '缓脉（脉搏和缓均匀）';
      case PulseType.HASTY:
        return '促脉（脉搏急促不均）';
      case PulseType.INTERMITTENT:
        return '代脉（脉搏时有间断）';
      case PulseType.HIDDEN:
        return '伏脉（脉搏深藏难觉）';
      default:
        return '未知脉象';
    }
  }

  /**
   * 获取腹诊发现描述
   */
  private getAbdominalFindingDescription(findingType: AbdominalFindingType, intensity: number): string {
    let description = '';
    
    switch(findingType) {
      case AbdominalFindingType.TENDERNESS:
        description = '压痛';
        break;
      case AbdominalFindingType.MASSES:
        description = '包块';
        break;
      case AbdominalFindingType.BLOATING:
        description = '腹胀';
        break;
      case AbdominalFindingType.RIGIDITY:
        description = '腹肌紧张';
        break;
      case AbdominalFindingType.FLUID:
        description = '腹水征象';
        break;
      case AbdominalFindingType.NORMAL:
        return '无异常';
      case AbdominalFindingType.COLD:
        description = '腹部畏寒';
        break;
      case AbdominalFindingType.HEAT:
        description = '腹部灼热';
        break;
      case AbdominalFindingType.PULSATION:
        description = '异常搏动';
        break;
      default:
        return '未知发现';
    }
    
    // 根据强度添加程度描述
    if (intensity > 0.8) {
      return `严重${description}`;
    } else if (intensity > 0.5) {
      return `中度${description}`;
    } else {
      return `轻度${description}`;
    }
  }

  /**
   * 根据脉象类型获取脏腑关联
   */
  private getOrganImplicationByPulseType(pulseType: PulseType, defaultOrgan: string): string {
    switch(pulseType) {
      case PulseType.FLOATING:
        return `${defaultOrgan}气不足，可能表证`;
      case PulseType.SINKING:
        return `${defaultOrgan}阴虚，可能里证`;
      case PulseType.RAPID:
        return `${defaultOrgan}热证`;
      case PulseType.SLIPPERY:
        return `${defaultOrgan}湿热或痰湿`;
      case PulseType.WIRY:
        return `${defaultOrgan}气郁或疼痛`;
      case PulseType.EMPTY:
        return `${defaultOrgan}气血不足`;
      default:
        return '';
    }
  }

  /**
   * 获取腹诊发现的脏腑关联
   */
  private getOrganImplicationByAbdominalFinding(finding: any): string {
    const location = finding.location;
    const findingType = finding.findingType;
    
    // 根据位置和发现类型判断脏腑关联
    if (location === TouchLocation.EPIGASTRIUM) {
      if (findingType === AbdominalFindingType.TENDERNESS) {
        return '胃气不和，胃炎可能性大';
      } else if (findingType === AbdominalFindingType.HEAT) {
        return '胃火上炎';
      }
    } else if (location === TouchLocation.RIGHT_UPPER) {
      if (findingType === AbdominalFindingType.TENDERNESS) {
        return '肝胆不和，胆囊疾病可能';
      }
    } else if (location === TouchLocation.LEFT_UPPER) {
      if (findingType === AbdominalFindingType.TENDERNESS) {
        return '脾气不足';
      }
    } else if (location === TouchLocation.UMBILICUS) {
      if (findingType === AbdominalFindingType.COLD) {
        return '脾肾阳虚';
      } else if (findingType === AbdominalFindingType.TENDERNESS) {
        return '中焦气滞';
      }
    } else if (location === TouchLocation.HYPOGASTRIUM) {
      if (findingType === AbdominalFindingType.COLD) {
        return '肾阳不足';
      } else if (findingType === AbdominalFindingType.TENDERNESS) {
        return '膀胱或生殖系统问题';
      }
    }
    
    return '';
  }

  /**
   * 生成脉诊结论
   */
  private generatePulseConclusion(dominantPulseTypes: string[], characteristics: string[]): string {
    if (dominantPulseTypes.length === 0) {
      return '未提供足够的脉诊数据';
    }
    
    let conclusion = '';
    
    // 根据主要脉象生成结论
    const mainType = dominantPulseTypes[0] as PulseType;
    
    switch(mainType) {
      case PulseType.FLOATING:
        conclusion = '脉浮主表证，多为外感初期或气虚';
        break;
      case PulseType.SINKING:
        conclusion = '脉沉主里证，多为寒证或病情较重';
        break;
      case PulseType.SLOW:
        conclusion = '脉迟主寒证，或为气血不足';
        break;
      case PulseType.RAPID:
        conclusion = '脉数主热证，或为阴虚火旺';
        break;
      case PulseType.SLIPPERY:
        conclusion = '脉滑主痰湿、食积或孕育';
        break;
      case PulseType.ROUGH:
        conclusion = '脉涩主血瘀气滞，或气血两虚';
        break;
      case PulseType.WIRY:
        conclusion = '脉弦主肝胆病变，或疼痛症状';
        break;
      case PulseType.EMPTY:
        conclusion = '脉虚主气血两虚，体质虚弱';
        break;
      default:
        conclusion = '脉象综合显示体质状态一般';
    }
    
    // 如果有第二主要脉象，补充说明
    if (dominantPulseTypes.length > 1) {
      const secondType = dominantPulseTypes[1] as PulseType;
      switch(secondType) {
        case PulseType.RAPID:
          conclusion += '，兼见脉数，示有内热';
          break;
        case PulseType.SLOW:
          conclusion += '，兼见脉迟，示有内寒';
          break;
        case PulseType.WIRY:
          conclusion += '，兼见脉弦，示有肝郁';
          break;
        case PulseType.SLIPPERY:
          conclusion += '，兼见脉滑，示有痰湿';
          break;
      }
    }
    
    return conclusion;
  }

  /**
   * 生成腹诊结论
   */
  private generateAbdominalConclusion(dominantFindingTypes: string[], characteristics: string[]): string {
    if (dominantFindingTypes.length === 0) {
      return '未提供足够的腹诊数据';
    }
    
    let conclusion = '';
    
    // 根据主要发现生成结论
    const mainType = dominantFindingTypes[0] as AbdominalFindingType;
    
    switch(mainType) {
      case AbdominalFindingType.TENDERNESS:
        conclusion = '腹部压痛明显，提示脏腑气机不畅，可能有炎症';
        break;
      case AbdominalFindingType.MASSES:
        conclusion = '腹部触及包块，提示有积聚，建议进一步检查';
        break;
      case AbdominalFindingType.BLOATING:
        conclusion = '腹部胀满，提示脾胃运化不良，或气机不畅';
        break;
      case AbdominalFindingType.RIGIDITY:
        conclusion = '腹肌紧张，提示有急性腹症可能，需警惕';
        break;
      case AbdominalFindingType.FLUID:
        conclusion = '腹部有液波感，提示可能有腹水';
        break;
      case AbdominalFindingType.COLD:
        conclusion = '腹部畏寒，提示脾肾阳虚';
        break;
      case AbdominalFindingType.HEAT:
        conclusion = '腹部灼热，提示胃肠有热';
        break;
      case AbdominalFindingType.NORMAL:
        conclusion = '腹诊无明显异常';
        break;
      default:
        conclusion = '腹诊结果显示一般状态';
    }
    
    // 如果有第二主要发现，补充说明
    if (dominantFindingTypes.length > 1) {
      const secondType = dominantFindingTypes[1] as AbdominalFindingType;
      switch(secondType) {
        case AbdominalFindingType.TENDERNESS:
          conclusion += '，同时伴有压痛，气滞明显';
          break;
        case AbdominalFindingType.BLOATING:
          conclusion += '，同时伴有腹胀，消化功能低下';
          break;
        case AbdominalFindingType.COLD:
          conclusion += '，同时伴有腹部寒凉，阳气不足';
          break;
        case AbdominalFindingType.HEAT:
          conclusion += '，同时伴有腹部热感，有内热表现';
          break;
      }
    }
    
    return conclusion;
  }

  /**
   * 获取脉象严重程度
   */
  private getPulseSeverity(pulseType: PulseType, strength: number): number {
    let baseSeverity = 0;
    
    // 不同脉象的基础严重程度
    switch(pulseType) {
      case PulseType.FLOATING:
      case PulseType.SINKING:
        baseSeverity = 0.3;
        break;
      case PulseType.RAPID:
      case PulseType.SLOW:
        baseSeverity = 0.4;
        break;
      case PulseType.WIRY:
      case PulseType.SLIPPERY:
        baseSeverity = 0.5;
        break;
      case PulseType.ROUGH:
      case PulseType.EMPTY:
      case PulseType.HASTY:
      case PulseType.INTERMITTENT:
        baseSeverity = 0.7;
        break;
      case PulseType.FAINT:
      case PulseType.HIDDEN:
        baseSeverity = 0.8;
        break;
      default:
        baseSeverity = 0.2;
    }
    
    // 根据强度调整严重程度
    return baseSeverity * strength;
  }

  /**
   * 获取腹诊严重程度
   */
  private getAbdominalSeverity(findingType: AbdominalFindingType, intensity: number): number {
    let baseSeverity = 0;
    
    // 不同发现类型的基础严重程度
    switch(findingType) {
      case AbdominalFindingType.NORMAL:
        baseSeverity = 0;
        break;
      case AbdominalFindingType.COLD:
      case AbdominalFindingType.HEAT:
        baseSeverity = 0.4;
        break;
      case AbdominalFindingType.BLOATING:
      case AbdominalFindingType.TENDERNESS:
        baseSeverity = 0.5;
        break;
      case AbdominalFindingType.PULSATION:
        baseSeverity = 0.6;
        break;
      case AbdominalFindingType.MASSES:
      case AbdominalFindingType.RIGIDITY:
      case AbdominalFindingType.FLUID:
        baseSeverity = 0.8;
        break;
      default:
        baseSeverity = 0.3;
    }
    
    // 根据强度调整严重程度
    return baseSeverity * intensity;
  }

  /**
   * 从脉象特征描述中提取脉象类型
   */
  private extractPulseTypeFromCharacteristic(characteristic: string): PulseType | null {
    if (characteristic.includes('浮脉')) return PulseType.FLOATING;
    if (characteristic.includes('沉脉')) return PulseType.SINKING;
    if (characteristic.includes('迟脉')) return PulseType.SLOW;
    if (characteristic.includes('数脉')) return PulseType.RAPID;
    if (characteristic.includes('滑脉')) return PulseType.SLIPPERY;
    if (characteristic.includes('涩脉')) return PulseType.ROUGH;
    if (characteristic.includes('弦脉')) return PulseType.WIRY;
    if (characteristic.includes('软脉')) return PulseType.SOFT;
    if (characteristic.includes('实脉')) return PulseType.FULL;
    if (characteristic.includes('虚脉')) return PulseType.EMPTY;
    if (characteristic.includes('长脉')) return PulseType.LONG;
    if (characteristic.includes('短脉')) return PulseType.SHORT;
    if (characteristic.includes('微脉')) return PulseType.FAINT;
    if (characteristic.includes('洪脉')) return PulseType.LARGE;
    if (characteristic.includes('缓脉')) return PulseType.MODERATE;
    if (characteristic.includes('促脉')) return PulseType.HASTY;
    if (characteristic.includes('代脉')) return PulseType.INTERMITTENT;
    if (characteristic.includes('伏脉')) return PulseType.HIDDEN;
    
    return null;
  }

  /**
   * 从腹诊特征描述中提取发现类型
   */
  private extractFindingTypeFromCharacteristic(characteristic: string): AbdominalFindingType | null {
    if (characteristic.includes('压痛')) return AbdominalFindingType.TENDERNESS;
    if (characteristic.includes('包块')) return AbdominalFindingType.MASSES;
    if (characteristic.includes('腹胀')) return AbdominalFindingType.BLOATING;
    if (characteristic.includes('紧张')) return AbdominalFindingType.RIGIDITY;
    if (characteristic.includes('腹水')) return AbdominalFindingType.FLUID;
    if (characteristic.includes('无异常')) return AbdominalFindingType.NORMAL;
    if (characteristic.includes('畏寒')) return AbdominalFindingType.COLD;
    if (characteristic.includes('灼热')) return AbdominalFindingType.HEAT;
    if (characteristic.includes('搏动')) return AbdominalFindingType.PULSATION;
    
    return null;
  }

  /**
   * 根据脉象类型获取健康建议
   */
  private getSuggestionByPulseType(pulseType: PulseType): string {
    switch(pulseType) {
      case PulseType.FLOATING:
        return '注意保暖，避免外邪侵袭，可适当服用玉屏风散增强卫气。';
      case PulseType.SINKING:
        return '注意调理脾胃，避免生冷食物，可服用理中丸温中散寒。';
      case PulseType.RAPID:
        return '清热降火，避免辛辣刺激性食物，可食用菊花、绿豆等清热食物。';
      case PulseType.SLOW:
        return '注意保暖，可适当进行温和锻炼，如八段锦，增加阳气。';
      case PulseType.SLIPPERY:
        return '控制饮食，避免过食肥甘厚味，可服用藿香正气水化湿。';
      case PulseType.ROUGH:
        return '活血化瘀，可适当食用红枣、桃仁等食物，增加活动量。';
      case PulseType.WIRY:
        return '舒肝解郁，保持情绪平和，可服用柴胡疏肝散。';
      case PulseType.EMPTY:
        return '益气补血，可食用大枣、阿胶等补益食物，注意休息。';
      default:
        return '保持规律生活，均衡饮食，适当运动。';
    }
  }

  /**
   * 根据腹诊发现类型获取健康建议
   */
  private getSuggestionByAbdominalFindingType(findingType: AbdominalFindingType): string {
    switch(findingType) {
      case AbdominalFindingType.TENDERNESS:
        return '避免腹部受凉，饮食宜温和易消化，可按摩腹部促进气血流通。';
      case AbdominalFindingType.MASSES:
        return '建议尽快就医进行详细检查，避免受凉和过度劳累。';
      case AbdominalFindingType.BLOATING:
        return '饮食宜清淡，少食多餐，可服用陈皮、山楂等理气消食。';
      case AbdominalFindingType.RIGIDITY:
        return '注意休息，避免腹部受凉，如持续不适应及时就医。';
      case AbdominalFindingType.FLUID:
        return '控制盐分摄入，避免过度劳累，建议尽快就医检查。';
      case AbdominalFindingType.COLD:
        return '腹部保暖，可使用艾灸或热敷腹部，食用生姜、肉桂等温阳食物。';
      case AbdominalFindingType.HEAT:
        return '避免辛辣刺激性食物，可食用薏米、莲子等清热食物。';
      default:
        return '保持腹部温暖，避免过食生冷，保持良好作息。';
    }
  }
}

// 导出默认实例
export default new AnalysisEngine(); 