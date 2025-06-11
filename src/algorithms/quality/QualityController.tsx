export interface QualityIssue {;
type: 'data' | 'result' | 'consistency' | 'safety,'
severity: 'low' | 'medium' | 'high' | 'critical,'';
message: string,
}
  const suggestion = string}
}
export interface QualityReport {valid: boolean}score: number,;
warnings: string[],
medicalAdvice: string[],
followUpRecommendations: string[],
}
}
  const issues = QualityIssue[]}
}
export interface QualityControlConfig {;
thresholds: {minConfidence: number,
}
    const consistencyCheck = number}
  };
const rules = {}
    [key: string]: boolean}
  };
}
export interface ValidationRule {';
name: string,'check: (data: any) => ValidationResult | Promise<ValidationResult>,
}
  const severity = 'low' | 'medium' | 'high' | 'critical}
}
export interface ValidationResult {valid: boolean}message: string,;
}
}
  const suggestion = string}
}
export interface ValidationInput {input: any}diagnosisResults: any,;
fusionResult: any,
syndromeAnalysis: any,
constitutionAnalysis: any,
}
}
  const treatmentRecommendation = any}
}
/* 类 */
 */
export class QualityController {private config: QualityControlConfig;
private validationRules: Map<string, ValidationRule> = new Map();
constructor(config: QualityControlConfig) {this.config = config}
}
    this.initializeValidationRules()}
  }
  /* 则 */
   */
private initializeValidationRules(): void {';}    // 数据完整性规则'/,'/g'/;
this.validationRules.set('data_completeness', {')'';})
check: (data: any) => this.checkDataCompleteness(data),
}
      const severity = 'medium}
    });
    // 置信度阈值规则'/,'/g'/;
this.validationRules.set('confidence_threshold', {)')'';})
check: (data: any) => this.checkConfidenceThreshold(data),
}
      const severity = 'high}
    });
    // 结果一致性规则'/,'/g'/;
this.validationRules.set('result_consistency', {)')'';})
check: (data: any) => this.checkResultConsistency(data),
}
      const severity = 'medium}
    });
    // 安全性检查规则'/,'/g'/;
this.validationRules.set('safety_check', {)')'';})
check: (data: any) => this.checkSafety(data),
}
      const severity = 'critical}
    });
  }
  /* 果 */
   */
const public = async validate(input: ValidationInput): Promise<QualityReport> {const issues: QualityIssue[] = []const warnings: string[] = [];
const medicalAdvice: string[] = [];
const followUpRecommendations: string[] = [];
try {// 执行所有验证规则/for (const [ruleId, rule] of Array.from(this.validationRules.entries())) {if (!this.isRuleEnabled(ruleId)) {}},/g/;
continue}
        }
        try {const result = await rule.check(input)if (!result.valid) {issues.push({)type: this.getRuleType(ruleId),
severity: rule.severity,
message: result.message,
}
              const suggestion = result.suggestion}
            });
          }
        } catch (error) {'issues.push({ ',)type: 'data,''const severity = 'medium)'
);
 })}
          });
        }
      }
      // 生成警告和建议
this.generateWarningsAndAdvice(input,,)issues,
warnings,);
medicalAdvice,);
followUpRecommendations);
      );
      // 计算质量分数
const score = this.calculateQualityScore(issues);
return {'const valid = '
issues.filter((issue) => issue.severity === 'critical').length === 0;
score,
warnings,
medicalAdvice,
followUpRecommendations,
}
        issues,}
      };
    } catch (error) {return {}        valid: false,
score: 0,
const issues = [;]'
          {'type: 'data,'
const severity = 'critical';
}
}
          }
];
        ],
      };
    }
  }
  /* 性 */
   */
private checkDataCompleteness(input: ValidationInput): ValidationResult {}
    const { input: diagnosisInput ;} = input;
let completeness = 0;
let totalChecks = 0;
    // 检查各诊法数据'/,'/g'/;
const  diagnosisTypes = [;]'
      'lookingData','
      'listeningData','
      'inquiryData','
      'palpationData','
      'calculationData'];
    ];
diagnosisTypes.forEach((type) => {totalChecks++if (diagnosisInput[type]) {}
        completeness++}
      }
    });
const completenessRatio = completeness / totalChecks;
if (completenessRatio < 0.4) {return {}        const valid = false;
}
}
      };
    }
  }
  /* 值 */
   */
private checkConfidenceThreshold(input: ValidationInput): ValidationResult {}
    const { diagnosisResults ;} = input;
const minConfidence = this.config.thresholds.minConfidence;
    // 检查各诊法置信度
const confidences: number[] = [];
if (diagnosisResults.looking) {}
      confidences.push(diagnosisResults.looking.confidence)}
    }
    if (diagnosisResults.listening) {}
      confidences.push(diagnosisResults.listening.confidence)}
    }
    if (diagnosisResults.inquiry) {}
      confidences.push(diagnosisResults.inquiry.confidence)}
    }
    if (diagnosisResults.palpation) {}
      confidences.push(diagnosisResults.palpation.confidence)}
    }
    if (diagnosisResults.calculation) {}
      confidences.push(diagnosisResults.calculation.confidence)}
    }
    // 检查是否有置信度低于阈值的结果
const  lowConfidenceResults = confidences.filter();
      (conf) => conf < minConfidence;
    );
if (lowConfidenceResults.length > 0) {return {}        const valid = false;
}
}
      };
    }
  }
  /* 性 */
   */
private checkResultConsistency(input: ValidationInput): ValidationResult {}
    const { diagnosisResults, syndromeAnalysis ;} = input;
    // 简化的一致性检查逻辑
if (!diagnosisResults || !syndromeAnalysis) {return {}        const valid = false;
}
}
      };
    }
  }
  /* 性 */
   */
private checkSafety(input: ValidationInput): ValidationResult {}
    const { treatmentRecommendation ;} = input;
    // 简化的安全性检查
if (!treatmentRecommendation) {return {}        const valid = false;
}
}
      };
    }
  }
  /* 议 */
   */
private generateWarningsAndAdvice(input: ValidationInput,,)issues: QualityIssue[],
warnings: string[],);
medicalAdvice: string[],);
const followUpRecommendations = string[]);
  ): void {';}    // 根据问题生成相应的警告和建议'/,'/g'/;
if (issues.some((issue) => issue.type === 'safety')) {';}}'';
}
    }
if (issues.some((issue) => issue.type === 'consistency')) {';}}'';
}
    }
if (issues.some((issue) => issue.severity === 'high')) {';}}'';
}
    }
  }
  /* 数 */
   */
private calculateQualityScore(issues: QualityIssue[]): number {let score = 100issues.forEach((issue) => {'switch (issue.severity) {'case 'critical': 
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
}
          break}
      }
    });
return Math.max(0, score);
  }
  /* 用 */
   */
private isRuleEnabled(ruleId: string): boolean {}
    return this.config.rules[ruleId] !== false}
  }
  /* ' *//;'/g'/;
   *//,'/g'/;
private getRuleType(ruleId: string): QualityIssue['type'] {'switch (ruleId) {'case 'data_completeness': '
return 'data
case 'confidence_threshold': '
return 'result
case 'result_consistency': '
return 'consistency
case 'safety_check': '
return 'safety';
const default = 
}
        return 'data}
    }
  }
}
''
