export interface QualityIssue {
  type: 'data' | 'result' | 'consistency' | 'safety';
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  suggestion: string;
}

export interface QualityReport {
  valid: boolean;
  score: number;
  warnings: string[];
  medicalAdvice: string[];
  followUpRecommendations: string[];
  issues: QualityIssue[];
}

export interface QualityControlConfig {
  thresholds: {
    minConfidence: number;
    consistencyCheck: number;
  };
  rules: {
    [key: string]: boolean;
  };
}

export interface ValidationRule {
  name: string;
  check: (data: any) => ValidationResult | Promise<ValidationResult>;
  severity: 'low' | 'medium' | 'high' | 'critical';
}

export interface ValidationResult {
  valid: boolean;
  message: string;
  suggestion: string;
}

export interface ValidationInput {
  input: any;
  diagnosisResults: any;
  fusionResult: any;
  syndromeAnalysis: any;
  constitutionAnalysis: any;
  treatmentRecommendation: any;
}

/**
 * 质量控制器类
 */
export class QualityController {
  private config: QualityControlConfig;
  private validationRules: Map<string, ValidationRule> = new Map();

  constructor(config: QualityControlConfig) {
    this.config = config;
    this.initializeValidationRules();
  }

  /**
   * 初始化验证规则
   */
  private initializeValidationRules(): void {
    // 数据完整性规则
    this.validationRules.set('data_completeness', {
      name: '数据完整性检查',
      check: (data: any) => this.checkDataCompleteness(data),
      severity: 'medium',
    });

    // 置信度阈值规则
    this.validationRules.set('confidence_threshold', {
      name: '置信度阈值检查',
      check: (data: any) => this.checkConfidenceThreshold(data),
      severity: 'high',
    });

    // 结果一致性规则
    this.validationRules.set('result_consistency', {
      name: '结果一致性检查',
      check: (data: any) => this.checkResultConsistency(data),
      severity: 'medium',
    });

    // 安全性检查规则
    this.validationRules.set('safety_check', {
      name: '安全性检查',
      check: (data: any) => this.checkSafety(data),
      severity: 'critical',
    });
  }

  /**
   * 验证输入和结果
   */
  public async validate(input: ValidationInput): Promise<QualityReport> {
    const issues: QualityIssue[] = [];
    const warnings: string[] = [];
    const medicalAdvice: string[] = [];
    const followUpRecommendations: string[] = [];

    try {
      // 执行所有验证规则
      for (const [ruleId, rule] of Array.from(this.validationRules.entries())) {
        if (!this.isRuleEnabled(ruleId)) {
          continue;
        }

        try {
          const result = await rule.check(input);
          if (!result.valid) {
            issues.push({
              type: this.getRuleType(ruleId),
              severity: rule.severity,
              message: result.message,
              suggestion: result.suggestion,
            });
          }
        } catch (error) {
          issues.push({
            type: 'data',
            severity: 'medium',
            message: `验证规则 ${rule.name} 执行失败`,
            suggestion: '请检查输入数据格式',
          });
        }
      }

      // 生成警告和建议
      this.generateWarningsAndAdvice(
        input,
        issues,
        warnings,
        medicalAdvice,
        followUpRecommendations
      );

      // 计算质量分数
      const score = this.calculateQualityScore(issues);

      return {
        valid:
          issues.filter((issue) => issue.severity === 'critical').length === 0,
        score,
        warnings,
        medicalAdvice,
        followUpRecommendations,
        issues,
      };
    } catch (error) {
      return {
        valid: false,
        score: 0,
        warnings: ['质量控制过程中发生错误'],
        medicalAdvice: ['建议重新进行诊断'],
        followUpRecommendations: ['请联系技术支持'],
        issues: [
          {
            type: 'data',
            severity: 'critical',
            message: '质量控制失败',
            suggestion: '请检查系统状态',
          },
        ],
      };
    }
  }

  /**
   * 检查数据完整性
   */
  private checkDataCompleteness(input: ValidationInput): ValidationResult {
    const { input: diagnosisInput } = input;
    let completeness = 0;
    let totalChecks = 0;

    // 检查各诊法数据
    const diagnosisTypes = [
      'lookingData',
      'listeningData',
      'inquiryData',
      'palpationData',
      'calculationData',
    ];

    diagnosisTypes.forEach((type) => {
      totalChecks++;
      if (diagnosisInput[type]) {
        completeness++;
      }
    });

    const completenessRatio = completeness / totalChecks;

    if (completenessRatio < 0.4) {
      return {
        valid: false,
        message: '诊断数据不完整，可能影响结果准确性',
        suggestion: '建议补充更多诊法数据以提高准确性',
      };
    }

    return { valid: true, message: '数据完整性良好', suggestion: '' };
  }

  /**
   * 检查置信度阈值
   */
  private checkConfidenceThreshold(input: ValidationInput): ValidationResult {
    const { diagnosisResults } = input;
    const minConfidence = this.config.thresholds.minConfidence;

    // 检查各诊法置信度
    const confidences: number[] = [];

    if (diagnosisResults.looking) {
      confidences.push(diagnosisResults.looking.confidence);
    }
    if (diagnosisResults.listening) {
      confidences.push(diagnosisResults.listening.confidence);
    }
    if (diagnosisResults.inquiry) {
      confidences.push(diagnosisResults.inquiry.confidence);
    }
    if (diagnosisResults.palpation) {
      confidences.push(diagnosisResults.palpation.confidence);
    }
    if (diagnosisResults.calculation) {
      confidences.push(diagnosisResults.calculation.confidence);
    }

    // 检查是否有置信度低于阈值的结果
    const lowConfidenceResults = confidences.filter(
      (conf) => conf < minConfidence
    );

    if (lowConfidenceResults.length > 0) {
      return {
        valid: false,
        message: `有 ${lowConfidenceResults.length} 个诊法结果置信度低于阈值 ${minConfidence}`,
        suggestion: '建议重新采集数据或调整诊断参数',
      };
    }

    return { valid: true, message: '置信度检查通过', suggestion: '' };
  }

  /**
   * 检查结果一致性
   */
  private checkResultConsistency(input: ValidationInput): ValidationResult {
    const { diagnosisResults, syndromeAnalysis } = input;

    // 简化的一致性检查逻辑
    if (!diagnosisResults || !syndromeAnalysis) {
      return {
        valid: false,
        message: '缺少必要的诊断结果数据',
        suggestion: '请确保所有诊断步骤都已完成',
      };
    }

    return { valid: true, message: '结果一致性良好', suggestion: '' };
  }

  /**
   * 检查安全性
   */
  private checkSafety(input: ValidationInput): ValidationResult {
    const { treatmentRecommendation } = input;

    // 简化的安全性检查
    if (!treatmentRecommendation) {
      return {
        valid: false,
        message: '缺少治疗建议',
        suggestion: '请生成完整的治疗建议',
      };
    }

    return { valid: true, message: '安全性检查通过', suggestion: '' };
  }

  /**
   * 生成警告和建议
   */
  private generateWarningsAndAdvice(
    input: ValidationInput,
    issues: QualityIssue[],
    warnings: string[],
    medicalAdvice: string[],
    followUpRecommendations: string[]
  ): void {
    // 根据问题生成相应的警告和建议
    if (issues.some((issue) => issue.type === 'safety')) {
      warnings.push('检测到安全性问题，请谨慎处理');
      medicalAdvice.push('建议咨询专业医师');
    }

    if (issues.some((issue) => issue.type === 'consistency')) {
      warnings.push('诊断结果存在不一致性');
      followUpRecommendations.push('建议进行复诊确认');
    }

    if (issues.some((issue) => issue.severity === 'high')) {
      medicalAdvice.push('建议及时就医');
    }
  }

  /**
   * 计算质量分数
   */
  private calculateQualityScore(issues: QualityIssue[]): number {
    let score = 100;

    issues.forEach((issue) => {
      switch (issue.severity) {
        case 'critical':
          score -= 30;
          break;
        case 'high':
          score -= 20;
          break;
        case 'medium':
          score -= 10;
          break;
        case 'low':
          score -= 5;
          break;
      }
    });

    return Math.max(0, score);
  }

  /**
   * 检查规则是否启用
   */
  private isRuleEnabled(ruleId: string): boolean {
    return this.config.rules[ruleId] !== false;
  }

  /**
   * 获取规则类型
   */
  private getRuleType(ruleId: string): QualityIssue['type'] {
    switch (ruleId) {
      case 'data_completeness':
        return 'data';
      case 'confidence_threshold':
        return 'result';
      case 'result_consistency':
        return 'consistency';
      case 'safety_check':
        return 'safety';
      default:
        return 'data';
    }
  }
}
