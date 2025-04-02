import { Logger } from '../utils/logger';
import { 
  PulseType, 
  AbdominalFindingType 
} from '../interfaces/touch-diagnosis.interface';

const logger = new Logger('HealthSuggestions');

/**
 * 健康建议生成器
 * 根据触诊分析结果生成个性化健康建议
 */
export class HealthSuggestionsGenerator {
  /**
   * 生成脉诊相关健康建议
   */
  generatePulseDiagnosisSuggestions(pulseData: any[]): string[] {
    logger.debug('生成脉诊健康建议');
    
    if (!pulseData || pulseData.length === 0) {
      return ['无脉诊数据，无法提供相关建议。'];
    }
    
    const suggestions: string[] = [];
    
    // 根据不同脉象类型生成建议
    const pulseTypes = pulseData.map(item => item.pulseType);
    const uniquePulseTypes = Array.from(new Set(pulseTypes));
    
    // 根据脉象类型生成建议
    uniquePulseTypes.forEach(pulseType => {
      const suggestion = this.getSuggestionByPulseType(pulseType as PulseType);
      if (suggestion) {
        suggestions.push(suggestion);
      }
    });
    
    // 如果有脉搏过快的情况
    if (pulseData.some(item => item.frequency > 90)) {
      suggestions.push('脉搏偏快，注意保持情绪平和，减少咖啡因摄入，可尝试深呼吸放松练习。');
    }
    
    // 如果有脉搏过慢的情况
    if (pulseData.some(item => item.frequency < 60)) {
      suggestions.push('脉搏偏慢，注意保暖，可适当增加温和运动，增强心肺功能。');
    }
    
    // 如果脉象强度普遍较弱
    if (pulseData.filter(item => item.strength < 0.4).length > pulseData.length / 2) {
      suggestions.push('脉象偏弱，提示气血不足，建议注意休息，适当进补，增强体质。');
    }
    
    // 如果脉象节律不齐
    if (pulseData.some(item => item.rhythm < 0.6)) {
      suggestions.push('脉律欠佳，建议保持规律生活，避免过度劳累和情绪波动，定期检查心脏健康。');
    }
    
    return suggestions;
  }
  
  /**
   * 生成腹诊相关健康建议
   */
  generateAbdominalDiagnosisSuggestions(abdominalData: any[]): string[] {
    logger.debug('生成腹诊健康建议');
    
    if (!abdominalData || abdominalData.length === 0) {
      return ['无腹诊数据，无法提供相关建议。'];
    }
    
    const suggestions: string[] = [];
    
    // 根据不同腹诊发现类型生成建议
    const findingTypes = abdominalData.map(item => item.findingType);
    const uniqueFindingTypes = Array.from(new Set(findingTypes));
    
    // 根据腹诊发现类型生成建议
    uniqueFindingTypes.forEach(findingType => {
      const suggestion = this.getSuggestionByAbdominalFindingType(findingType as AbdominalFindingType);
      if (suggestion) {
        suggestions.push(suggestion);
      }
    });
    
    // 如果有压痛点，根据位置提出具体建议
    const tenderPoints = abdominalData.filter(item => item.findingType === AbdominalFindingType.TENDERNESS);
    if (tenderPoints.length > 0) {
      suggestions.push('腹部压痛点较多，建议保持腹部温暖，进食易消化食物，避免过度劳累。');
    }
    
    // 如果有腹胀
    if (uniqueFindingTypes.includes(AbdominalFindingType.BLOATING)) {
      suggestions.push('腹胀明显，建议少食多餐，细嚼慢咽，避免食用产气食物如豆类、洋葱等。');
    }
    
    // 如果腹部发冷
    if (uniqueFindingTypes.includes(AbdominalFindingType.COLD)) {
      suggestions.push('腹部畏寒，脾肾阳虚，应避免生冷食物，可适当食用羊肉、韭菜等温阳食物，注意腹部保暖。');
    }
    
    return suggestions;
  }
  
  /**
   * 生成综合健康建议
   */
  generateComprehensiveSuggestions(touchDiagnosisData: any): string[] {
    logger.info('生成综合健康建议');
    
    // 收集建议
    const pulseSuggestions = this.generatePulseDiagnosisSuggestions(touchDiagnosisData.pulseFindings || []);
    const abdominalSuggestions = this.generateAbdominalDiagnosisSuggestions(touchDiagnosisData.abdominalFindings || []);
    
    // 合并建议
    const allSuggestions = [...pulseSuggestions, ...abdominalSuggestions];
    
    // 添加通用建议
    allSuggestions.push('保持规律作息，避免过度劳累和熬夜。');
    allSuggestions.push('饮食宜清淡均衡，少食辛辣刺激性食物。');
    allSuggestions.push('保持适度运动，如散步、太极、八段锦等。');
    allSuggestions.push('保持心情舒畅，避免情绪激动。');
    
    // 去重
    const uniqueSuggestions = Array.from(new Set(allSuggestions));
    
    return uniqueSuggestions;
  }
  
  /**
   * 根据脉象类型获取健康建议
   */
  private getSuggestionByPulseType(pulseType: PulseType): string {
    switch(pulseType) {
      case PulseType.FLOATING:
        return '脉浮，表示表证或气虚，注意保暖，避免风邪侵袭，注意休息。';
      case PulseType.SINKING:
        return '脉沉，表示里证或寒证，注意腹部保暖，避免生冷食物。';
      case PulseType.SLOW:
        return '脉迟，表示寒证或气血不足，注意全身保暖，可食用温性食物如生姜、肉桂等。';
      case PulseType.RAPID:
        return '脉数，表示热证或阴虚，注意清热降火，可食用菊花、绿豆等食物。';
      case PulseType.SLIPPERY:
        return '脉滑，表示痰湿或食积，控制饮食量，少食油腻，可服用陈皮、山楂等理气消食。';
      case PulseType.ROUGH:
        return '脉涩，表示血瘀或气血不足，注意活血化瘀，可食用红枣、当归等食物，适当增加活动量。';
      case PulseType.WIRY:
        return '脉弦，表示肝胆疾病或疼痛，保持心情舒畅，避免情绪激动，可服用菊花、决明子等清肝明目。';
      case PulseType.SOFT:
        return '脉软，表示气血亏虚，注意休息，避免过度劳累，可食用山药、大枣等补气血食物。';
      case PulseType.EMPTY:
        return '脉虚，表示气血两虚，需多加休息，注意营养均衡，可食用人参、黄芪等补益气血。';
      case PulseType.INTERMITTENT:
        return '脉代，表示心气不足，注意休息，避免劳累，保持情绪稳定，建议就医检查心脏健康。';
      default:
        return '';
    }
  }
  
  /**
   * 根据腹诊发现类型获取健康建议
   */
  private getSuggestionByAbdominalFindingType(findingType: AbdominalFindingType): string {
    switch(findingType) {
      case AbdominalFindingType.TENDERNESS:
        return '腹部压痛，可能为气滞血瘀或有炎症，建议避免腹部受凉，饮食宜温和易消化。';
      case AbdominalFindingType.MASSES:
        return '腹部有包块，建议尽快就医进行详细检查，避免受凉和过度劳累。';
      case AbdominalFindingType.BLOATING:
        return '腹部胀满，脾胃运化不良，建议饮食规律，少食多餐，可服用焦三仙等健脾消食药物。';
      case AbdominalFindingType.RIGIDITY:
        return '腹肌紧张，可能为急性腹症，建议及时就医，避免腹部受压。';
      case AbdominalFindingType.FLUID:
        return '腹部有液波感，可能为腹水，建议限制盐分摄入，注意休息，及时就医。';
      case AbdominalFindingType.COLD:
        return '腹部畏寒，脾肾阳虚，建议腹部保暖，可进行艾灸或热敷，食用温阳食物如羊肉、生姜等。';
      case AbdominalFindingType.HEAT:
        return '腹部灼热，可能为胃肠有热，建议避免辛辣刺激性食物，可食用薏米、莲子等清热食物。';
      default:
        return '';
    }
  }
}

// 导出默认实例
export default new HealthSuggestionsGenerator(); 