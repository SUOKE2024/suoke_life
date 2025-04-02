import { Logger } from '../utils/logger';
import { 
  ConstitutionType, 
  YinYangBalance,
  FiveElement
} from '../interfaces/four-diagnosis.interface';

const logger = new Logger('HealthSuggestions');

/**
 * 健康建议生成器
 * 根据四诊合参分析结果生成个性化健康建议
 */
export class HealthSuggestionsGenerator {
  /**
   * 根据阴阳平衡状态生成建议
   */
  generateYinYangBalanceSuggestions(balance: YinYangBalance): string[] {
    logger.debug(`生成阴阳平衡建议: ${balance}`);
    
    const suggestions: string[] = [];
    
    switch (balance) {
      case YinYangBalance.BALANCED:
        suggestions.push('保持现有的健康生活方式，注意起居作息规律。');
        suggestions.push('建议每日清晨进行缓和的太极或气功锻炼，促进气血运行。');
        break;
        
      case YinYangBalance.SLIGHT_YIN_DEFICIENCY:
      case YinYangBalance.MODERATE_YIN_DEFICIENCY:
      case YinYangBalance.SEVERE_YIN_DEFICIENCY:
        suggestions.push('注意休息，避免过度劳累和熬夜。');
        suggestions.push('饮食宜清淡滋阴，可多食用黑芝麻、百合、银耳等食物。');
        suggestions.push('保持情绪平和，避免过度兴奋。');
        
        if (balance === YinYangBalance.MODERATE_YIN_DEFICIENCY || 
            balance === YinYangBalance.SEVERE_YIN_DEFICIENCY) {
          suggestions.push('建议适当减少高强度运动，选择瑜伽、慢走等温和运动。');
          suggestions.push('可在医生指导下服用滋阴类中药。');
        }
        break;
        
      case YinYangBalance.SLIGHT_YANG_DEFICIENCY:
      case YinYangBalance.MODERATE_YANG_DEFICIENCY:
      case YinYangBalance.SEVERE_YANG_DEFICIENCY:
        suggestions.push('保暖防寒，特别注意脚部和腰腹部的保暖。');
        suggestions.push('饮食宜温补，可适当食用羊肉、韭菜、生姜等温性食物。');
        suggestions.push('适当增加运动量，促进阳气生发。');
        
        if (balance === YinYangBalance.MODERATE_YANG_DEFICIENCY || 
            balance === YinYangBalance.SEVERE_YANG_DEFICIENCY) {
          suggestions.push('建议进行艾灸或刮痧等温阳活血的外治法。');
          suggestions.push('可在医生指导下服用温阳类中药。');
        }
        break;
        
      case YinYangBalance.SLIGHT_YIN_EXCESS:
      case YinYangBalance.MODERATE_YIN_EXCESS:
      case YinYangBalance.SEVERE_YIN_EXCESS:
        suggestions.push('保持居室干燥通风，避免湿冷环境。');
        suggestions.push('饮食宜温阳化湿，可食用白萝卜、茯苓、薏米等食材。');
        suggestions.push('增加适当运动，帮助水湿代谢。');
        
        if (balance === YinYangBalance.MODERATE_YIN_EXCESS || 
            balance === YinYangBalance.SEVERE_YIN_EXCESS) {
          suggestions.push('建议进行温热类理疗。');
          suggestions.push('可在医生指导下服用化湿类中药。');
        }
        break;
        
      case YinYangBalance.SLIGHT_YANG_EXCESS:
      case YinYangBalance.MODERATE_YANG_EXCESS:
      case YinYangBalance.SEVERE_YANG_EXCESS:
        suggestions.push('注意清热降火，避免辛辣刺激性食物。');
        suggestions.push('保持情绪平和，避免过度激动和生气。');
        suggestions.push('可多食用绿豆、荸荠、苦瓜等清热食物。');
        
        if (balance === YinYangBalance.MODERATE_YANG_EXCESS || 
            balance === YinYangBalance.SEVERE_YANG_EXCESS) {
          suggestions.push('建议进行冷敷或足浴等清热方法。');
          suggestions.push('可在医生指导下服用清热类中药。');
        }
        break;
        
      default:
        suggestions.push('建议定期进行中医体质检查，关注阴阳平衡变化。');
        break;
    }
    
    return suggestions;
  }
  
  /**
   * 根据五行状态生成建议
   */
  generateFiveElementsSuggestions(dominantElement: FiveElement, deficientElement: FiveElement): string[] {
    logger.debug(`生成五行建议: 优势元素-${dominantElement}, 不足元素-${deficientElement}`);
    
    const suggestions: string[] = [];
    
    // 基于优势元素的建议
    switch (dominantElement) {
      case FiveElement.WOOD:
        suggestions.push('注意控制情绪波动，特别是愤怒情绪。');
        suggestions.push('建议适当进行舒展性运动，如太极拳、瑜伽等。');
        break;
        
      case FiveElement.FIRE:
        suggestions.push('避免过度兴奋和情绪激动，保持心情舒畅。');
        suggestions.push('注意规律作息，避免熬夜。');
        break;
        
      case FiveElement.EARTH:
        suggestions.push('饮食规律，避免过度思虑和担忧。');
        suggestions.push('适当增加户外活动，亲近大自然。');
        break;
        
      case FiveElement.METAL:
        suggestions.push('注意呼吸系统保健，避免烟尘污染环境。');
        suggestions.push('可尝试练习腹式呼吸和八段锦等呼吸功法。');
        break;
        
      case FiveElement.WATER:
        suggestions.push('注意肾脏保健，避免过度劳累。');
        suggestions.push('保持充足睡眠，早睡早起。');
        break;
    }
    
    // 基于不足元素的建议
    switch (deficientElement) {
      case FiveElement.WOOD:
        suggestions.push('可多食用绿色蔬菜和富含维生素的食物，如菠菜、青椒等。');
        suggestions.push('建议增加适度的肝脏滋养，如枸杞、菊花茶等。');
        break;
        
      case FiveElement.FIRE:
        suggestions.push('多食用红色食物，如红枣、山楂、番茄等。');
        suggestions.push('适当参加社交活动，保持心情愉悦。');
        break;
        
      case FiveElement.EARTH:
        suggestions.push('饮食宜温补脾胃，如山药、莲子、大枣等。');
        suggestions.push('避免过食生冷和油腻食物。');
        break;
        
      case FiveElement.METAL:
        suggestions.push('可多食用白色食物，如白萝卜、梨、白木耳等。');
        suggestions.push('居住环境保持空气清新，可使用加湿器。');
        break;
        
      case FiveElement.WATER:
        suggestions.push('适当食用黑色食物，如黑豆、黑芝麻、黑木耳等。');
        suggestions.push('注意保暖，特别是腰腹部位。');
        break;
    }
    
    return suggestions;
  }
  
  /**
   * 根据体质类型生成建议
   */
  generateConstitutionTypeSuggestions(constitutionType: ConstitutionType): string[] {
    logger.debug(`生成体质类型建议: ${constitutionType}`);
    
    const suggestions: string[] = [];
    
    switch (constitutionType) {
      case ConstitutionType.BALANCED:
        suggestions.push('保持均衡饮食、规律作息和适度运动。');
        suggestions.push('注意四季养生，根据季节变化调整生活习惯。');
        suggestions.push('建议定期进行中医体质检查，预防疾病发生。');
        break;
        
      case ConstitutionType.QI_DEFICIENCY:
        suggestions.push('避免过度劳累，注意劳逸结合。');
        suggestions.push('饮食宜补气健脾，如山药、大枣、黄芪等。');
        suggestions.push('可进行八段锦、太极等缓和运动，增强体质。');
        suggestions.push('注意保暖，避免受凉。');
        break;
        
      case ConstitutionType.YANG_DEFICIENCY:
        suggestions.push('注重保暖，特别是背部和腹部。');
        suggestions.push('饮食宜温阳，可适当食用羊肉、桂圆、生姜等温性食物。');
        suggestions.push('避免长时间处于寒冷潮湿环境。');
        suggestions.push('可在医生指导下进行艾灸、刮痧等温阳疗法。');
        break;
        
      case ConstitutionType.YIN_DEFICIENCY:
        suggestions.push('保持充足睡眠，避免熬夜。');
        suggestions.push('饮食宜滋阴润燥，可食用银耳、百合、豆浆等。');
        suggestions.push('避免辛辣刺激性食物。');
        suggestions.push('保持情绪平稳，避免过度兴奋。');
        break;
        
      case ConstitutionType.PHLEGM_DAMPNESS:
        suggestions.push('控制饮食量，避免过食油腻和甜食。');
        suggestions.push('增加运动量，促进代谢。');
        suggestions.push('饮食宜清淡健脾化湿，如薏米、红豆、白萝卜等。');
        suggestions.push('保持居室干燥通风。');
        break;
        
      case ConstitutionType.DAMP_HEAT:
        suggestions.push('饮食宜清淡，避免辛辣油腻和烧烤食物。');
        suggestions.push('保持情绪平和，避免过度劳累。');
        suggestions.push('多饮水，促进湿热排出。');
        suggestions.push('可适当食用绿豆、苦瓜、莲子等清热化湿食物。');
        break;
        
      case ConstitutionType.BLOOD_STASIS:
        suggestions.push('保持适度运动，促进血液循环。');
        suggestions.push('避免长时间保持同一姿势。');
        suggestions.push('可食用红枣、桃仁、当归等活血食物。');
        suggestions.push('保持情绪平和，避免过度忧郁。');
        break;
        
      case ConstitutionType.QI_STAGNATION:
        suggestions.push('保持心情舒畅，学习情绪管理技巧。');
        suggestions.push('适当进行有氧运动，如慢跑、游泳等。');
        suggestions.push('可食用玫瑰花、佛手、柑橘等理气食物。');
        suggestions.push('培养兴趣爱好，增加社交活动。');
        break;
        
      case ConstitutionType.SPECIAL_CONSTITUTION:
        suggestions.push('根据具体特禀情况，避免接触过敏原。');
        suggestions.push('饮食宜温和平淡，避免刺激性食物。');
        suggestions.push('保持居住环境清洁，减少过敏源。');
        suggestions.push('建议在医生指导下进行体质调理。');
        break;
        
      default:
        suggestions.push('建议进行全面的中医体质辨识，获取更精准的健康指导。');
        break;
    }
    
    return suggestions;
  }
  
  /**
   * 根据脏腑状态生成建议
   */
  generateOrganSuggestions(organData: any): string[] {
    logger.debug('生成脏腑健康建议');
    
    const suggestions: string[] = [];
    const { heart, liver, spleen, lung, kidney, stomach, gallbladder, anomalies } = organData;
    
    // 心脏相关建议
    if (heart < 40) {
      suggestions.push('注意心脏保养，保持情绪稳定，避免过度焦虑。');
      suggestions.push('可适当食用红枣、桂圆等补心安神的食物。');
    }
    
    // 肝脏相关建议
    if (liver < 40) {
      suggestions.push('注意肝脏保健，保持情绪舒畅，避免过度愤怒。');
      suggestions.push('可食用青色蔬果，如菠菜、青椒、青鱼等。');
    }
    
    // 脾胃相关建议
    if (spleen < 40 || stomach < 40) {
      suggestions.push('注意脾胃保健，饮食规律，避免过食生冷和油腻食物。');
      suggestions.push('可食用山药、莲子、大枣等健脾食物。');
    }
    
    // 肺部相关建议
    if (lung < 40) {
      suggestions.push('注意肺部保健，避免烟尘和空气污染。');
      suggestions.push('可食用白色食物，如百合、白萝卜、梨等润肺食物。');
    }
    
    // 肾脏相关建议
    if (kidney < 40) {
      suggestions.push('注意肾脏保健，保持充足睡眠，避免过度劳累。');
      suggestions.push('可食用黑色食物，如黑芝麻、黑豆、核桃等补肾食物。');
    }
    
    // 胆囊相关建议
    if (gallbladder < 40) {
      suggestions.push('注意胆囊保健，避免高脂肪食物。');
      suggestions.push('保持情绪稳定，增强决断力。');
    }
    
    // 如果所有脏腑功能正常
    if (heart >= 60 && liver >= 60 && spleen >= 60 && lung >= 60 && kidney >= 60 && stomach >= 60 && gallbladder >= 60) {
      suggestions.push('脏腑功能整体良好，继续保持健康的生活方式。');
    }
    
    // 针对异常情况的建议
    if (anomalies && anomalies.length > 0) {
      suggestions.push('发现脏腑功能异常，建议咨询中医师进行详细评估。');
    }
    
    return suggestions;
  }
  
  /**
   * 生成综合健康建议
   */
  generateComprehensiveSuggestions(diagnosisData: any): string[] {
    logger.info('生成综合健康建议');
    
    const bodyCondition = diagnosisData.integratedAssessment?.bodyCondition;
    if (!bodyCondition) {
      logger.warn('缺少身体状况数据，无法生成综合建议');
      return ['暂无足够数据生成健康建议。请完成完整的四诊评估。'];
    }
    
    // 收集各方面的建议
    const yinYangSuggestions = this.generateYinYangBalanceSuggestions(
      bodyCondition.balance?.yinYang?.balance || YinYangBalance.BALANCED
    );
    
    const fiveElementsSuggestions = this.generateFiveElementsSuggestions(
      bodyCondition.balance?.fiveElements?.dominantElement || FiveElement.EARTH,
      bodyCondition.balance?.fiveElements?.deficientElement || FiveElement.METAL
    );
    
    const constitutionSuggestions = this.generateConstitutionTypeSuggestions(
      bodyCondition.constitutionType as ConstitutionType || ConstitutionType.BALANCED
    );
    
    const organSuggestions = this.generateOrganSuggestions(
      bodyCondition.balance?.organs || {}
    );
    
    // 整合所有建议并去重
    const allSuggestions = [
      ...yinYangSuggestions,
      ...fiveElementsSuggestions,
      ...constitutionSuggestions,
      ...organSuggestions
    ];
    
    // 去重
    const uniqueSuggestions = Array.from(new Set(allSuggestions));
    
    // 添加总结性建议
    uniqueSuggestions.unshift('基于四诊合参分析结果，为您提供以下健康建议：');
    uniqueSuggestions.push('以上建议仅供参考，具体调理方案请在中医师指导下进行。');
    
    return uniqueSuggestions;
  }
}

// 导出默认实例
export default new HealthSuggestionsGenerator(); 