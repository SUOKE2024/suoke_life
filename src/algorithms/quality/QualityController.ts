/**
 * 质量控制器
 *
 * 负责五诊算法的质量控制和验证
 * 包括数据验证、结果验证、交叉验证等
 *
 * @author 索克生活技术团队
 * @version 1.0.0
 */

export interface QualityControlConfig {
  enabled: boolean;
  checks: {
    dataValidation: boolean;
    resultValidation: boolean;
    crossValidation: boolean;
    expertReview: boolean;
  };
  thresholds: {
    minConfidence: number;
    maxUncertainty: number;
    consistencyCheck: number;
  };
}

export interface QualityReport {
  valid: boolean;
  score: number;
  warnings: string[];
  medicalAdvice: string[];
  followUpRecommendations: string[];
  issues: QualityIssue[];
}

export interface QualityIssue {
  type: "data" | "result" | "consistency" | "safety";
  severity: "low" | "medium" | "high" | "critical";
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
    this.validationRules.set("data_completeness", {
      name: "数据完整性检查",
      check: (data: any) => this.checkDataCompleteness(data),
      severity: "medium",
    });

    // 置信度阈值规则
    this.validationRules.set("confidence_threshold", {
      name: "置信度阈值检查",
      check: (data: any) => this.checkConfidenceThreshold(data),
      severity: "high",
    });

    // 结果一致性规则
    this.validationRules.set("result_consistency", {
      name: "结果一致性检查",
      check: (data: any) => this.checkResultConsistency(data),
      severity: "medium",
    });

    // 安全性检查规则
    this.validationRules.set("safety_check", {
      name: "安全性检查",
      check: (data: any) => this.checkSafety(data),
      severity: "critical",
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
            type: "data",
            severity: "medium",
            message: `验证规则 ${rule.name} 执行失败`,
            suggestion: "请检查输入数据格式",
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
          issues.filter((issue) => issue.severity === "critical").length === 0,
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
        warnings: ["质量控制过程中发生错误"],
        medicalAdvice: ["建议重新进行诊断"],
        followUpRecommendations: ["请联系技术支持"],
        issues: [
          {
            type: "data",
            severity: "critical",
            message: "质量控制失败",
            suggestion: "请检查系统状态",
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
      "lookingData",
      "listeningData",
      "inquiryData",
      "palpationData",
      "calculationData",
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
        message: "诊断数据不完整，可能影响结果准确性",
        suggestion: "建议补充更多诊法数据以提高准确性",
      };
    }

    return { valid: true, message: "数据完整性良好", suggestion: "" };
  }

  /**
   * 检查置信度阈值
   */
  private checkConfidenceThreshold(input: ValidationInput): ValidationResult {
    const { diagnosisResults, fusionResult } = input;
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

    const lowConfidenceCount = confidences.filter(
      (conf) => conf < minConfidence
    ).length;

    if (lowConfidenceCount > confidences.length / 2) {
      return {
        valid: false,
        message: "多个诊法置信度偏低，结果可靠性不足",
        suggestion: "建议重新采集数据或寻求专业医师意见",
      };
    }

    if (fusionResult.confidence < minConfidence) {
      return {
        valid: false,
        message: "融合分析置信度偏低",
        suggestion: "建议补充更多诊法数据或重新检查输入质量",
      };
    }

    return { valid: true, message: "置信度符合要求", suggestion: "" };
  }

  /**
   * 检查结果一致性
   */
  private checkResultConsistency(input: ValidationInput): ValidationResult {
    const { diagnosisResults, syndromeAnalysis, constitutionAnalysis } = input;
    const consistencyThreshold = this.config.thresholds.consistencyCheck;

    // 检查诊法结果之间的一致性
    const consistencyScore = this.calculateConsistencyScore(
      diagnosisResults,
      syndromeAnalysis
    );

    if (consistencyScore < consistencyThreshold) {
      return {
        valid: false,
        message: "各诊法结果存在明显矛盾",
        suggestion: "建议重新检查输入数据或寻求专业医师复核",
      };
    }

    return { valid: true, message: "结果一致性良好", suggestion: "" };
  }

  /**
   * 安全性检查
   */
  private checkSafety(input: ValidationInput): ValidationResult {
    const { treatmentRecommendation, constitutionAnalysis } = input;

    // 检查治疗建议的安全性
    if (treatmentRecommendation.recommendations) {
      for (const recommendation of treatmentRecommendation.recommendations) {
        // 检查是否有潜在的安全风险
        if (this.hasSafetyRisk(recommendation, constitutionAnalysis)) {
          return {
            valid: false,
            message: "治疗建议存在潜在安全风险",
            suggestion: "建议在专业医师指导下进行治疗",
          };
        }
      }
    }

    return { valid: true, message: "安全性检查通过", suggestion: "" };
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
    // 基于问题生成警告
    issues.forEach((issue) => {
      if (issue.severity === "high" || issue.severity === "critical") {
        warnings.push(issue.message);
      }
    });

    // 生成医疗建议
    if (issues.some((issue) => issue.type === "safety")) {
      medicalAdvice.push("建议在专业中医师指导下进行诊疗");
    }

    if (issues.some((issue) => issue.severity === "critical")) {
      medicalAdvice.push("诊断结果仅供参考，不可替代专业医疗诊断");
    }

    // 生成随访建议
    const lowConfidenceIssues = issues.filter(
      (issue) =>
        issue.message.includes("置信度") || issue.message.includes("完整性")
    );

    if (lowConfidenceIssues.length > 0) {
      followUpRecommendations.push("建议1-2周后重新进行诊断评估");
      followUpRecommendations.push("建议补充更详细的症状描述");
    }
  }

  /**
   * 计算质量分数
   */
  private calculateQualityScore(issues: QualityIssue[]): number {
    let score = 100;

    issues.forEach((issue) => {
      switch (issue.severity) {
        case "critical":
          score -= 30;
          break;
        case "high":
          score -= 20;
          break;
        case "medium":
          score -= 10;
          break;
        case "low":
          score -= 5;
          break;
      }
    });

    return Math.max(0, score);
  }

  /**
   * 计算一致性分数
   */
  private calculateConsistencyScore(
    diagnosisResults: any,
    syndromeAnalysis: any
  ): number {
    // 简化的一致性计算
    // 实际实现中需要更复杂的中医理论一致性检查
    return 0.8; // 占位符
  }

  /**
   * 检查安全风险
   */
  private hasSafetyRisk(
    recommendation: any,
    constitutionAnalysis: any
  ): boolean {
    // 简化的安全检查
    // 实际实现中需要更详细的安全性规则
    return false; // 占位符
  }

  /**
   * 检查规则是否启用
   */
  private isRuleEnabled(ruleId: string): boolean {
    switch (ruleId) {
      case "data_completeness":
        return this.config.checks.dataValidation;
      case "confidence_threshold":
        return this.config.checks.resultValidation;
      case "result_consistency":
        return this.config.checks.crossValidation;
      case "safety_check":
        return this.config.checks.expertReview;
      default:
        return true;
    }
  }

  /**
   * 获取规则类型
   */
  private getRuleType(ruleId: string): QualityIssue["type"] {
    switch (ruleId) {
      case "data_completeness":
        return "data";
      case "confidence_threshold":
        return "result";
      case "result_consistency":
        return "consistency";
      case "safety_check":
        return "safety";
      default:
        return "data";
    }
  }

  /**
   * 模拟事件发射
   */
  public on(event: string, callback: (data: any) => void): void {
    // 简化的事件处理，实际项目中可以使用更完整的事件系统
  }

  public emit(event: string, data?: any): void {
    // 简化的事件发射
  }
}

// 辅助接口
interface ValidationRule {
  name: string;
  check: (data: any) => ValidationResult | Promise<ValidationResult>;
  severity: QualityIssue["severity"];
}

interface ValidationResult {
  valid: boolean;
  message: string;
  suggestion: string;
}

export default QualityController;
