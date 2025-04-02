import { Logger } from '../utils/logger';
import { 
  ConstitutionType, 
  YinYangBalance,
  FiveElement,
  DiagnosisType,
  FivePhasesAnalysisResult,
  OrganBalanceResult
} from '../interfaces/four-diagnosis.interface';
import { AppError, ErrorType } from '../middlewares/error.middleware';

const logger = new Logger('AnalysisEngine');

/**
 * 四诊合参分析引擎
 * 负责对四诊数据进行综合分析
 */
export class AnalysisEngine {
  /**
   * 执行四诊合参分析
   */
  performIntegratedAnalysis(fourDiagnosisData: any): any {
    logger.info(`执行四诊合参分析: ${fourDiagnosisData.patientId}`);
    
    try {
      // 验证是否有足够的诊断数据
      this.validateDiagnosticData(fourDiagnosisData);
      
      // 收集各诊断的结论
      const lookingAssessment = fourDiagnosisData.looking?.overallAssessment || '';
      const smellAssessment = fourDiagnosisData.smell?.overallAssessment || '';
      const inquiryAssessment = fourDiagnosisData.inquiry?.overallAssessment || '';
      const touchAssessment = fourDiagnosisData.touch?.overallAssessment || '';
      
      // 计算阴阳平衡
      const yinYangBalance = this.calculateYinYangBalance(fourDiagnosisData);
      
      // 分析五行
      const fiveElements = this.analyzeFiveElements(fourDiagnosisData);
      
      // 分析脏腑平衡
      const organBalance = this.analyzeOrganBalance(fourDiagnosisData);
      
      // 判断体质类型
      const constitutionType = this.determineConstitutionType(fourDiagnosisData);
      
      // 计算能量水平
      const energyLevel = this.calculateEnergyLevel(fourDiagnosisData);
      
      // 解决诊断冲突
      const resolvedAssessments = this.resolveDiagnosticConflicts([
        { type: DiagnosisType.LOOKING, assessment: lookingAssessment },
        { type: DiagnosisType.SMELL, assessment: smellAssessment },
        { type: DiagnosisType.INQUIRY, assessment: inquiryAssessment },
        { type: DiagnosisType.TOUCH, assessment: touchAssessment }
      ]);
      
      // 生成总结性描述
      const summary = this.generateSummary(resolvedAssessments.map(a => a.assessment));
      
      // 计算诊断置信度
      const diagnosticConfidence = this.calculateDiagnosticConfidence(fourDiagnosisData);
      
      // 构建综合分析结果
      const integratedAssessment = {
        timestamp: new Date(),
        summary,
        bodyCondition: {
          balance: {
            yinYang: yinYangBalance,
            fiveElements,
            organs: organBalance
          },
          energyLevel,
          constitutionType
        },
        healthSuggestions: [], // 健康建议将在服务层添加
        diagnosticConfidence,
        usedDiagnostics: resolvedAssessments.map(a => a.type)
      };
      
      return integratedAssessment;
    } catch (error) {
      logger.error('四诊合参分析失败', { error });
      throw error;
    }
  }

  /**
   * 验证诊断数据完整性
   */
  private validateDiagnosticData(data: any): void {
    // 检查是否至少有一项诊断数据
    const hasDiagnosticData = 
      (data.looking && Object.keys(data.looking).length > 0) ||
      (data.smell && Object.keys(data.smell).length > 0) ||
      (data.inquiry && Object.keys(data.inquiry).length > 0) ||
      (data.touch && Object.keys(data.touch).length > 0);
    
    if (!hasDiagnosticData) {
      throw AppError.insufficientDataError(
        '需要至少一种诊断数据才能进行分析',
        [],
        data.patientId
      );
    }
    
    // 记录可用的诊断方法
    const availableDiagnoses = [];
    if (data.looking && Object.keys(data.looking).length > 0) availableDiagnoses.push(DiagnosisType.LOOKING);
    if (data.smell && Object.keys(data.smell).length > 0) availableDiagnoses.push(DiagnosisType.SMELL);
    if (data.inquiry && Object.keys(data.inquiry).length > 0) availableDiagnoses.push(DiagnosisType.INQUIRY);
    if (data.touch && Object.keys(data.touch).length > 0) availableDiagnoses.push(DiagnosisType.TOUCH);
    
    logger.info(`可用诊断数据: ${availableDiagnoses.join(', ')}`, { patientId: data.patientId });
  }

  /**
   * 解决诊断冲突
   */
  private resolveDiagnosticConflicts(assessments: Array<{type: DiagnosisType, assessment: string}>): Array<{type: DiagnosisType, assessment: string}> {
    // 过滤掉空的评估
    const validAssessments = assessments.filter(a => a.assessment.trim().length > 0);
    
    if (validAssessments.length <= 1) {
      return validAssessments;
    }
    
    // 这里可以实现更复杂的冲突解决算法
    // 当前简单实现：根据诊断的置信度权重来解决冲突
    const diagnosticWeights = {
      [DiagnosisType.LOOKING]: 0.3,
      [DiagnosisType.SMELL]: 0.2,
      [DiagnosisType.INQUIRY]: 0.25,
      [DiagnosisType.TOUCH]: 0.25
    };
    
    // 为每个有效的评估分配权重分数
    const weightedAssessments = validAssessments.map(a => ({
      ...a,
      weight: diagnosticWeights[a.type] || 0.1
    }));
    
    // 按权重排序
    weightedAssessments.sort((a, b) => b.weight - a.weight);
    
    // 记录可能的冲突，在日志中保留，但不影响返回结果
    if (weightedAssessments.length > 1) {
      const conflictAnalysis = weightedAssessments.map(a => ({
        type: a.type,
        weight: a.weight,
        keywords: this.extractKeywords(a.assessment)
      }));
      
      logger.debug('诊断评估权重分析', { conflictAnalysis });
    }
    
    return validAssessments;
  }

  /**
   * 提取评估中的关键词（简化版）
   */
  private extractKeywords(text: string): string[] {
    const keywords = [];
    const keyTerms = ['阴虚', '阳虚', '气虚', '血虚', '痰湿', '湿热', '血瘀', '气滞', '平和质'];
    
    keyTerms.forEach(term => {
      if (text.includes(term)) {
        keywords.push(term);
      }
    });
    
    return keywords;
  }

  /**
   * 分析五行
   */
  analyzeFiveElements(data: any): FivePhasesAnalysisResult {
    logger.debug('分析五行元素');
    
    // 初始化五行元素值
    const fiveElements: FivePhasesAnalysisResult = {
      wood: 50,  // 木
      fire: 50,  // 火
      earth: 50, // 土
      metal: 50, // 金
      water: 50, // 水
      dominantElement: FiveElement.EARTH,
      deficientElement: FiveElement.EARTH,
      imbalances: []
    };
    
    // 各诊断方法的权重
    const diagnosticWeights = {
      looking: 0.3,
      smell: 0.2,
      inquiry: 0.3,
      touch: 0.2
    };
    
    // 跟踪数据有效性
    let validDataCount = 0;
    let weightSum = 0;
    
    // 处理望诊数据（舌象、面色等）
    if (data.looking && data.looking.rawData) {
      validDataCount++;
      weightSum += diagnosticWeights.looking;
      this.adjustFiveElementsFromLooking(fiveElements, data.looking.rawData);
    }
    
    // 处理闻诊数据（气味）
    if (data.smell && data.smell.rawData) {
      validDataCount++;
      weightSum += diagnosticWeights.smell;
      this.adjustFiveElementsFromSmell(fiveElements, data.smell.rawData);
    }
    
    // 处理问诊数据（症状、情绪等）
    if (data.inquiry && data.inquiry.rawData) {
      validDataCount++;
      weightSum += diagnosticWeights.inquiry;
      this.adjustFiveElementsFromInquiry(fiveElements, data.inquiry.rawData);
    }
    
    // 处理切诊数据（脉象）
    if (data.touch && data.touch.rawData) {
      validDataCount++;
      weightSum += diagnosticWeights.touch;
      this.adjustFiveElementsFromTouch(fiveElements, data.touch.rawData);
    }
    
    // 如果没有任何有效数据，返回默认值
    if (validDataCount === 0) {
      return fiveElements;
    }
    
    // 根据缺失数据调整五行值
    if (validDataCount < 4) {
      // 缺少数据时，减少对五行极端值的判断信心
      const missingDataFactor = validDataCount / 4;
      
      Object.keys(fiveElements).forEach(key => {
        if (key !== 'dominantElement' && key !== 'deficientElement' && key !== 'imbalances') {
          // 将极端值拉回中间值
          const currentValue = fiveElements[key];
          const distanceFromMiddle = Math.abs(currentValue - 50);
          const adjustment = distanceFromMiddle * (1 - missingDataFactor);
          
          if (currentValue > 50) {
            fiveElements[key] = currentValue - adjustment;
          } else if (currentValue < 50) {
            fiveElements[key] = currentValue + adjustment;
          }
        }
      });
    }
    
    // 计算五行的相对平衡，确定优势元素和不足元素
    const elementsArray = [
      { element: FiveElement.WOOD, value: fiveElements.wood },
      { element: FiveElement.FIRE, value: fiveElements.fire },
      { element: FiveElement.EARTH, value: fiveElements.earth },
      { element: FiveElement.METAL, value: fiveElements.metal },
      { element: FiveElement.WATER, value: fiveElements.water }
    ];
    
    // 排序找出最高和最低的元素
    elementsArray.sort((a, b) => b.value - a.value);
    
    // 设置优势元素和不足元素
    fiveElements.dominantElement = elementsArray[0].element;
    fiveElements.deficientElement = elementsArray[elementsArray.length - 1].element;
    
    // 分析五行失衡情况
    this.analyzeFiveElementImbalances(fiveElements);
    
    return fiveElements;
  }
  
  /**
   * 根据望诊数据调整五行值
   */
  private adjustFiveElementsFromLooking(fiveElements: FivePhasesAnalysisResult, lookingData: any): void {
    const { tongueColor, tongueCoating, faceColor, eyeCondition } = lookingData;
    
    // 舌色分析
    if (tongueColor) {
      switch (tongueColor) {
        case 'pale':
          fiveElements.water += 20;
          fiveElements.metal += 10;
          fiveElements.fire -= 15;
          break;
        case 'red':
          fiveElements.fire += 25;
          fiveElements.wood += 10;
          fiveElements.water -= 15;
          break;
        case 'purple':
          fiveElements.water += 15;
          fiveElements.fire += 5;
          fiveElements.imbalances.push('血瘀');
          break;
        case 'yellow':
          fiveElements.earth += 20;
          fiveElements.fire += 10;
          break;
        case 'red_tip':
          fiveElements.fire += 30;
          fiveElements.imbalances.push('心火上炎');
          break;
        case 'red_sides':
          fiveElements.wood += 25;
          fiveElements.fire += 15;
          fiveElements.imbalances.push('肝火上炎');
          break;
      }
    }
    
    // 舌苔分析
    if (tongueCoating) {
      switch (tongueCoating) {
        case 'thin_white':
          fiveElements.metal += 15;
          break;
        case 'thick_white':
          fiveElements.metal += 20;
          fiveElements.water += 10;
          fiveElements.imbalances.push('寒湿');
          break;
        case 'yellow':
          fiveElements.earth += 15;
          fiveElements.fire += 10;
          fiveElements.imbalances.push('湿热');
          break;
        case 'thick_yellow':
          fiveElements.earth += 25;
          fiveElements.fire += 20;
          fiveElements.imbalances.push('湿热偏重');
          break;
        case 'none':
          fiveElements.fire += 15;
          fiveElements.imbalances.push('阴虚');
          break;
        case 'greasy':
          fiveElements.earth += 20;
          fiveElements.water += 10;
          fiveElements.imbalances.push('痰湿');
          break;
      }
    }
    
    // 面色分析
    if (faceColor) {
      switch (faceColor) {
        case 'red':
          fiveElements.fire += 20;
          fiveElements.wood += 10;
          break;
        case 'pale':
          fiveElements.metal += 15;
          fiveElements.water += 10;
          fiveElements.fire -= 10;
          fiveElements.imbalances.push('气血不足');
          break;
        case 'yellow':
          fiveElements.earth += 25;
          fiveElements.imbalances.push('脾虚');
          break;
        case 'blue_green':
          fiveElements.wood += 20;
          fiveElements.imbalances.push('肝郁');
          break;
        case 'dark':
          fiveElements.water += 20;
          fiveElements.imbalances.push('肾虚');
          break;
      }
    }
    
    // 眼部状况分析
    if (eyeCondition) {
      switch (eyeCondition) {
        case 'red':
          fiveElements.fire += 15;
          fiveElements.wood += 10;
          break;
        case 'dry':
          fiveElements.fire += 10;
          fiveElements.water -= 10;
          fiveElements.imbalances.push('阴虚');
          break;
        case 'watery':
          fiveElements.water += 15;
          fiveElements.imbalances.push('肾气不足');
          break;
        case 'yellow_sclera':
          fiveElements.earth += 15;
          fiveElements.wood += 10;
          fiveElements.imbalances.push('湿热');
          break;
      }
    }
  }
  
  /**
   * 根据闻诊数据调整五行值
   */
  private adjustFiveElementsFromSmell(fiveElements: FivePhasesAnalysisResult, smellData: any): void {
    const { bodyOdor, breathOdor } = smellData;
    
    // 体味分析
    if (bodyOdor) {
      switch (bodyOdor) {
        case 'sour':
          fiveElements.wood += 20;
          fiveElements.imbalances.push('肝郁');
          break;
        case 'burnt':
          fiveElements.fire += 20;
          fiveElements.imbalances.push('热症');
          break;
        case 'sweet':
          fiveElements.earth += 20;
          fiveElements.imbalances.push('湿症');
          break;
        case 'rotten':
          fiveElements.metal += 15;
          fiveElements.earth += 10;
          fiveElements.imbalances.push('湿热');
          break;
        case 'fishy':
          fiveElements.water += 20;
          fiveElements.imbalances.push('肾虚');
          break;
      }
    }
    
    // 口气分析
    if (breathOdor) {
      switch (breathOdor) {
        case 'sour':
          fiveElements.wood += 15;
          fiveElements.imbalances.push('肝胆湿热');
          break;
        case 'bitter':
          fiveElements.fire += 20;
          fiveElements.imbalances.push('心火');
          break;
        case 'sweet':
          fiveElements.earth += 15;
          fiveElements.imbalances.push('脾湿');
          break;
        case 'rotten':
          fiveElements.metal += 15;
          fiveElements.imbalances.push('肺热');
          break;
        case 'foul':
          fiveElements.earth += 10;
          fiveElements.water += 5;
          fiveElements.imbalances.push('脾胃不和');
          break;
      }
    }
  }
  
  /**
   * 根据问诊数据调整五行值
   */
  private adjustFiveElementsFromInquiry(fiveElements: FivePhasesAnalysisResult, inquiryData: any): void {
    const { 
      emotionalState, 
      sleepQuality, 
      appetiteLevel,
      urination,
      bowelMovements,
      symptoms,
      painAreas,
      energyLevel
    } = inquiryData;
    
    // 情绪状态分析
    if (emotionalState) {
      switch (emotionalState) {
        case 'irritable':
        case 'angry':
          fiveElements.wood += 25;
          fiveElements.fire += 10;
          fiveElements.imbalances.push('肝郁化火');
          break;
        case 'anxious':
        case 'overthinking':
          fiveElements.earth += 15;
          fiveElements.fire += 10;
          fiveElements.imbalances.push('心脾两虚');
          break;
        case 'sad':
        case 'grief':
          fiveElements.metal += 20;
          fiveElements.water += 5;
          fiveElements.imbalances.push('肺气郁结');
          break;
        case 'fearful':
          fiveElements.water += 25;
          fiveElements.imbalances.push('肾气不足');
          break;
        case 'joyful':
          // 平和状态，不做特别调整
          break;
      }
    }
    
    // 睡眠质量分析
    if (sleepQuality) {
      switch (sleepQuality) {
        case 'poor':
          fiveElements.fire += 15;
          fiveElements.water -= 10;
          fiveElements.imbalances.push('心神不宁');
          break;
        case 'restless':
          fiveElements.fire += 10;
          fiveElements.wood += 10;
          fiveElements.imbalances.push('肝火扰心');
          break;
        case 'excessive':
          fiveElements.earth += 15;
          fiveElements.fire -= 5;
          fiveElements.imbalances.push('脾虚痰湿');
          break;
      }
    }
    
    // 食欲分析
    if (appetiteLevel) {
      switch (appetiteLevel) {
        case 'poor':
          fiveElements.earth -= 15;
          fiveElements.imbalances.push('脾胃虚弱');
          break;
        case 'excessive':
          fiveElements.earth += 10;
          fiveElements.fire += 5;
          fiveElements.imbalances.push('胃热');
          break;
      }
    }
    
    // 症状分析
    if (symptoms && Array.isArray(symptoms)) {
      symptoms.forEach(symptom => {
        if (['headache', 'dizziness', 'red_eyes', 'irritability'].includes(symptom)) {
          fiveElements.wood += 8;
          fiveElements.fire += 3;
        } else if (['palpitations', 'insomnia', 'night_sweats'].includes(symptom)) {
          fiveElements.fire += 8;
          fiveElements.water -= 5;
          fiveElements.imbalances.push('阴虚火旺');
        } else if (['poor_appetite', 'bloating', 'fatigue'].includes(symptom)) {
          fiveElements.earth -= 8;
          fiveElements.imbalances.push('脾虚');
        } else if (['cough', 'dry_skin', 'constipation'].includes(symptom)) {
          fiveElements.metal -= 8;
          fiveElements.water -= 3;
          fiveElements.imbalances.push('肺阴不足');
        } else if (['lower_back_pain', 'tinnitus', 'frequent_urination'].includes(symptom)) {
          fiveElements.water -= 8;
          fiveElements.imbalances.push('肾虚');
        }
      });
    }
    
    // 疼痛区域分析
    if (painAreas && Array.isArray(painAreas)) {
      painAreas.forEach(area => {
        switch (area) {
          case 'head':
            fiveElements.wood += 10;
            fiveElements.fire += 5;
            break;
          case 'chest':
            fiveElements.fire += 10;
            fiveElements.metal += 5;
            break;
          case 'abdomen':
            fiveElements.earth += 10;
            break;
          case 'lower_back':
            fiveElements.water += 15;
            fiveElements.imbalances.push('肾虚');
            break;
          case 'joints':
            fiveElements.water += 5;
            fiveElements.wood += 5;
            fiveElements.imbalances.push('风湿');
            break;
        }
      });
    }
  }
  
  /**
   * 根据切诊数据调整五行值
   */
  private adjustFiveElementsFromTouch(fiveElements: FivePhasesAnalysisResult, touchData: any): void {
    const { pulseType, pulseStrength, pulseRhythm, skinTemperature } = touchData;
    
    // 脉象类型分析
    if (pulseType) {
      switch (pulseType) {
        case 'wiry':
          fiveElements.wood += 20;
          fiveElements.imbalances.push('肝郁');
          break;
        case 'rapid':
          fiveElements.fire += 20;
          fiveElements.water -= 10;
          fiveElements.imbalances.push('热症');
          break;
        case 'slippery':
          fiveElements.earth += 15;
          fiveElements.imbalances.push('痰湿');
          break;
        case 'weak':
          // 根据脉象强度进一步分析
          if (pulseStrength === 'very_weak') {
            fiveElements.water -= 15;
            fiveElements.imbalances.push('肾气虚');
          } else {
            fiveElements.metal -= 10;
            fiveElements.imbalances.push('气虚');
          }
          break;
        case 'slow':
          fiveElements.water += 15;
          fiveElements.fire -= 10;
          fiveElements.imbalances.push('寒症');
          break;
        case 'floating':
          fiveElements.metal += 10;
          fiveElements.imbalances.push('表证');
          break;
        case 'deep':
          fiveElements.water += 10;
          fiveElements.imbalances.push('里证');
          break;
      }
    }
    
    // 脉象节律分析
    if (pulseRhythm) {
      switch (pulseRhythm) {
        case 'irregular':
          fiveElements.fire += 5;
          fiveElements.imbalances.push('心神不宁');
          break;
        case 'knotted':
          fiveElements.fire -= 10;
          fiveElements.imbalances.push('血瘀');
          break;
        case 'intermittent':
          fiveElements.fire -= 15;
          fiveElements.imbalances.push('气血两虚');
          break;
      }
    }
    
    // 皮肤温度分析
    if (skinTemperature) {
      switch (skinTemperature) {
        case 'hot':
          fiveElements.fire += 15;
          fiveElements.water -= 10;
          fiveElements.imbalances.push('热症');
          break;
        case 'cold':
          fiveElements.water += 15;
          fiveElements.fire -= 10;
          fiveElements.imbalances.push('寒症');
          break;
        case 'normal':
          // 平衡状态
          break;
      }
    }
  }
  
  /**
   * 分析五行失衡情况
   */
  private analyzeFiveElementImbalances(fiveElements: FivePhasesAnalysisResult): void {
    // 去重失衡情况
    fiveElements.imbalances = [...new Set(fiveElements.imbalances)];
    
    // 五行相生相克关系分析
    const woodFireRatio = fiveElements.wood / fiveElements.fire;
    const fireEarthRatio = fiveElements.fire / fiveElements.earth;
    const earthMetalRatio = fiveElements.earth / fiveElements.metal;
    const metalWaterRatio = fiveElements.metal / fiveElements.water;
    const waterWoodRatio = fiveElements.water / fiveElements.wood;
    
    // 检查相生关系
    if (woodFireRatio > 1.5) {
      fiveElements.imbalances.push('木火失衡');
    }
    if (fireEarthRatio > 1.5) {
      fiveElements.imbalances.push('火土失衡');
    }
    if (earthMetalRatio > 1.5) {
      fiveElements.imbalances.push('土金失衡');
    }
    if (metalWaterRatio > 1.5) {
      fiveElements.imbalances.push('金水失衡');
    }
    if (waterWoodRatio > 1.5) {
      fiveElements.imbalances.push('水木失衡');
    }
    
    // 检查极端值
    Object.entries(fiveElements).forEach(([key, value]) => {
      if (typeof value === 'number') {
        if (value > 80) {
          const elementName = key.charAt(0).toUpperCase() + key.slice(1);
          fiveElements.imbalances.push(`${elementName}过盛`);
        } else if (value < 20) {
          const elementName = key.charAt(0).toUpperCase() + key.slice(1);
          fiveElements.imbalances.push(`${elementName}不足`);
        }
      }
    });
    
    // 再次去重
    fiveElements.imbalances = [...new Set(fiveElements.imbalances)];
  }

  /**
   * 分析脏腑平衡
   */
  analyzeOrganBalance(data: any): OrganBalanceResult {
    logger.debug('分析脏腑平衡');
    
    // 初始化脏腑值
    const organs = {
      heart: 20,      // 心
      liver: 20,      // 肝
      spleen: 20,     // 脾
      lung: 20,       // 肺
      kidney: 20,     // 肾
      stomach: 20,    // 胃
      gallbladder: 20, // 胆
      anomalies: []
    };
    
    // 建立五行与脏腑的对应关系
    const fiveElementOrgans = {
      [FiveElement.WOOD]: ['liver', 'gallbladder'],
      [FiveElement.FIRE]: ['heart', 'small_intestine'],
      [FiveElement.EARTH]: ['spleen', 'stomach'],
      [FiveElement.METAL]: ['lung', 'large_intestine'],
      [FiveElement.WATER]: ['kidney', 'bladder']
    };
    
    // 获取五行分析结果
    const fiveElements = this.analyzeFiveElements(data);
    
    // 根据五行结果调整脏腑值
    if (fiveElements.dominantElement) {
      const dominantOrgans = fiveElementOrgans[fiveElements.dominantElement];
      dominantOrgans?.forEach(organ => {
        if (organs[organ]) {
          organs[organ] += 10;
        }
      });
    }
    
    if (fiveElements.deficientElement) {
      const deficientOrgans = fiveElementOrgans[fiveElements.deficientElement];
      deficientOrgans?.forEach(organ => {
        if (organs[organ]) {
          organs[organ] -= 10;
        }
      });
    }
    
    // 望诊数据分析
    if (data.looking && data.looking.rawData) {
      const { faceColor, tongueColor, tongueCoating } = data.looking.rawData;
      
      // 面色分析
      if (faceColor === 'pale') {
        organs.heart -= 5;
        organs.lung += 5;
      } else if (faceColor === 'red') {
        organs.heart += 10;
        organs.liver += 5;
      } else if (faceColor === 'yellow') {
        organs.spleen += 10;
        organs.stomach += 5;
      } else if (faceColor === 'white') {
        organs.lung += 10;
      } else if (faceColor === 'dark') {
        organs.kidney += 10;
      }
      
      // 舌象特殊情况
      if (tongueColor === 'red_tip') {
        organs.heart += 15;
        organs.anomalies.push('心火上炎');
      } else if (tongueColor === 'red_sides') {
        organs.liver += 15;
        organs.gallbladder += 10;
        organs.anomalies.push('肝胆湿热');
      }
    }
    
    // 确保所有脏腑值在合理范围内
    Object.keys(organs).forEach(key => {
      if (key !== 'anomalies' && typeof organs[key] === 'number') {
        organs[key] = Math.max(0, Math.min(100, organs[key]));
      }
    });
    
    return organs;
  }

  /**
   * 判断体质类型
   */
  determineConstitutionType(data: any): ConstitutionType {
    logger.debug('判断体质类型');
    
    // 获取五行和脏腑分析结果作为依据
    const fiveElements = this.analyzeFiveElements(data);
    const organs = this.analyzeOrganBalance(data);
    const yinYang = this.calculateYinYangBalance(data);
    
    // 各种体质类型的标志特征
    const constitutionFeatures = {
      [ConstitutionType.BALANCED]: 0,
      [ConstitutionType.QI_DEFICIENCY]: 0,
      [ConstitutionType.YANG_DEFICIENCY]: 0,
      [ConstitutionType.YIN_DEFICIENCY]: 0,
      [ConstitutionType.PHLEGM_DAMPNESS]: 0,
      [ConstitutionType.DAMP_HEAT]: 0,
      [ConstitutionType.BLOOD_STASIS]: 0,
      [ConstitutionType.QI_STAGNATION]: 0,
      [ConstitutionType.SPECIAL_CONSTITUTION]: 0
    };
    
    // 五行分析影响体质判断
    if (Math.abs(fiveElements.wood - 20) <= 5 &&
        Math.abs(fiveElements.fire - 20) <= 5 &&
        Math.abs(fiveElements.earth - 20) <= 5 &&
        Math.abs(fiveElements.metal - 20) <= 5 &&
        Math.abs(fiveElements.water - 20) <= 5) {
      constitutionFeatures[ConstitutionType.BALANCED] += 20;
    }
    
    // 阴阳平衡影响体质判断
    if (yinYang.balance === YinYangBalance.BALANCED) {
      constitutionFeatures[ConstitutionType.BALANCED] += 20;
    } else if (yinYang.balance.includes('yang_deficiency')) {
      constitutionFeatures[ConstitutionType.YANG_DEFICIENCY] += 
        yinYang.balance.includes('severe') ? 30 : 
        yinYang.balance.includes('moderate') ? 20 : 10;
    } else if (yinYang.balance.includes('yin_deficiency')) {
      constitutionFeatures[ConstitutionType.YIN_DEFICIENCY] += 
        yinYang.balance.includes('severe') ? 30 : 
        yinYang.balance.includes('moderate') ? 20 : 10;
    }
    
    // 找出得分最高的体质类型
    let maxScore = 0;
    let dominantConstitution = ConstitutionType.BALANCED;
    
    Object.entries(constitutionFeatures).forEach(([constitution, score]) => {
      if (score > maxScore) {
        maxScore = score;
        dominantConstitution = constitution as ConstitutionType;
      }
    });
    
    return dominantConstitution;
  }

  /**
   * 生成总结性描述
   */
  generateSummary(assessments: string[]): string {
    // 过滤掉空字符串
    const validAssessments = assessments.filter(a => a.trim().length > 0);
    
    if (validAssessments.length === 0) {
      return '暂无足够数据进行四诊合参分析。建议完成完整的四诊评估。';
    }
    
    // 简单拼接（实际应用中应使用NLP技术进行整合）
    let summary = '四诊合参分析结果：\n\n';
    
    if (validAssessments.length >= 3) {
      summary += '通过望、闻、问、切四诊合参分析，';
    } else {
      summary += '基于现有诊断信息，';
    }
    
    // 以实际内容为基础的简单摘要
    summary += '患者当前整体情况：\n';
    summary += validAssessments.join('\n\n');
    
    return summary;
  }

  /**
   * 计算阴阳平衡
   */
  calculateYinYangBalance(data: any): any {
    // 初始化阴阳值
    let yin = 50;
    let yang = 50;
    
    // 根据四诊数据调整阴阳值
    if (data.looking && data.looking.rawData) {
      const { faceColor, tongueColor } = data.looking.rawData;
      
      if (faceColor === 'red' || tongueColor === 'red') {
        yang += 10;
        yin -= 5;
      } else if (faceColor === 'pale' || tongueColor === 'pale') {
        yin += 5;
        yang -= 5;
      }
    }
    
    if (data.inquiry && data.inquiry.rawData) {
      const { temperaturePreference, sweatPattern } = data.inquiry.rawData;
      
      if (temperaturePreference === 'cold_aversion') {
        yang -= 10;
      } else if (temperaturePreference === 'heat_aversion') {
        yin -= 10;
      }
      
      if (sweatPattern === 'night_sweats') {
        yin -= 15;
      } else if (sweatPattern === 'no_sweat') {
        yang -= 10;
      }
    }
    
    // 确定平衡状态
    let balance = YinYangBalance.BALANCED;
    const difference = yang - yin;
    
    if (difference > 20) {
      balance = YinYangBalance.SEVERE_YANG_EXCESS;
    } else if (difference > 10) {
      balance = YinYangBalance.MODERATE_YANG_EXCESS;
    } else if (difference > 5) {
      balance = YinYangBalance.SLIGHT_YANG_EXCESS;
    } else if (difference < -20) {
      balance = YinYangBalance.SEVERE_YIN_EXCESS;
    } else if (difference < -10) {
      balance = YinYangBalance.MODERATE_YIN_EXCESS;
    } else if (difference < -5) {
      balance = YinYangBalance.SLIGHT_YIN_EXCESS;
    }
    
    return {
      yin,
      yang,
      balance
    };
  }

  /**
   * 计算能量水平
   */
  calculateEnergyLevel(data: any): number {
    const baseEnergy = 50; // 基础能量水平
    let energyAdjustment = 0;
    
    // 根据四诊数据调整能量水平
    if (data.inquiry && data.inquiry.rawData) {
      const { fatigue, sleepQuality } = data.inquiry.rawData;
      
      if (fatigue === 'severe') {
        energyAdjustment -= 20;
      } else if (fatigue === 'moderate') {
        energyAdjustment -= 10;
      } else if (fatigue === 'mild') {
        energyAdjustment -= 5;
      }
      
      if (sleepQuality === 'poor') {
        energyAdjustment -= 10;
      } else if (sleepQuality === 'good') {
        energyAdjustment += 10;
      }
    }
    
    if (data.touch && data.touch.rawData) {
      const { pulseStrength } = data.touch.rawData;
      
      if (pulseStrength === 'weak') {
        energyAdjustment -= 15;
      } else if (pulseStrength === 'strong') {
        energyAdjustment += 15;
      }
    }
    
    // 确保能量水平在0-100范围内
    return Math.max(0, Math.min(100, baseEnergy + energyAdjustment));
  }

  /**
   * 计算诊断置信度
   */
  calculateDiagnosticConfidence(data: any): number {
    // 基于可用诊断方法的数量来计算置信度
    let availableDiagnosticMethods = 0;
    let totalWeight = 0;
    
    const diagnosticWeights = {
      looking: 0.3,
      smell: 0.2,
      inquiry: 0.3,
      touch: 0.2
    };
    
    if (data.looking && Object.keys(data.looking).length > 0) {
      availableDiagnosticMethods++;
      totalWeight += diagnosticWeights.looking;
    }
    
    if (data.smell && Object.keys(data.smell).length > 0) {
      availableDiagnosticMethods++;
      totalWeight += diagnosticWeights.smell;
    }
    
    if (data.inquiry && Object.keys(data.inquiry).length > 0) {
      availableDiagnosticMethods++;
      totalWeight += diagnosticWeights.inquiry;
    }
    
    if (data.touch && Object.keys(data.touch).length > 0) {
      availableDiagnosticMethods++;
      totalWeight += diagnosticWeights.touch;
    }
    
    // 计算基础置信度
    let baseConfidence = availableDiagnosticMethods / 4;
    
    // 根据权重调整置信度
    let weightedConfidence = totalWeight;
    
    // 取两种方法的平均值
    const confidence = (baseConfidence + weightedConfidence) / 2;
    
    // 转换为百分比并限制在0-100范围内
    return Math.min(100, Math.max(0, Math.round(confidence * 100)));
  }
}

// 导出单例
export default new AnalysisEngine(); 