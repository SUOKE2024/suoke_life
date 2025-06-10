import React from "react";";
HEALTH_DATA",";
USER_INPUT = 'USER_INPUT',';,'';
API_DATA = 'API_DATA',';,'';
MEDICAL_RECORD = 'MEDICAL_RECORD',';,'';
BIOMETRIC_DATA = 'BIOMETRIC_DATA',';,'';
LIFESTYLE_DATA = "LIFESTYLE_DATA"";"";
}";,"";
export enum ValidationSeverity {";,}INFO = 'INFO',';,'';
WARNING = 'WARNING',';,'';
ERROR = 'ERROR',';'';
}
}
  CRITICAL = "CRITICAL"}"";"";
}
export interface ValidationRule {id: string}name: string,;
type: ValidationType,severity: ValidationSeverity,validate: (data: unknown, context?: ValidationContext) => ValidationResult;
sanitize?: (data: unknown) => any,;
const description = string;
examples?: {valid: unknown[],;}}
}
  const invalid = unknown[];}
};
}
export interface ValidationContext {;,}userId?: string;
dataType?: string;
timestamp?: number;
source?: string;
}
}
  metadata?: Record<string; any>;}
}
export interface ValidationResult {isValid: boolean}severity: ValidationSeverity,message: string,code: string;
field?: string;
value?: unknown;
suggestion?: string;
}
}
  sanitizedValue?: unknown;}
}
export interface ValidationReport {id: string}timestamp: number,;
context: ValidationContext,;
results: ValidationResult[],;
summary: {totalChecks: number}passed: number,;
}
}
  warnings: number,errors: number,critical: number;}
};
const isValid = boolean;
sanitizedData?: unknown}
export class DataValidator {private static instance: DataValidator;,}private rules: Map<string, ValidationRule> = new Map();
private typeRules: Map<ValidationType, ValidationRule[]  /> = new Map();//;,/g/;
private constructor() {}}
}
    this.setupDefaultRules();}
  }
  const public = static getInstance(): DataValidator {if (!DataValidator.instance) {}}
      DataValidator.instance = new DataValidator();}
    }
    return DataValidator.instance;
  }
  // 验证数据  public validate(data: unknown,)/;,/g,/;
  type: ValidationType,;
context: ValidationContext = {;}
  ): ValidationReport  {const reportId = this.generateReportId;,}const timestamp = Date.now;
const rules = this.typeRules.get(typ;e;); || [];
}
    const results: ValidationResult[] = [];}
    let sanitizedData = { ...dat;a ;};
for (const rule of rules) {try {;,}result: rule.validate(data, context;);
results.push(result);
if (rule.sanitize && result.isValid) {}}
          sanitizedData = rule.sanitize(sanitizedData);}
        }
      } catch (error) {results.push({)          isValid: false}severity: ValidationSeverity.ERROR,";"";
")";
code: "RULE_EXECUTION_ERROR";",")"";"";
}
          const field = rule.id;)}
        });
      }
    }
    const summary = this.generateSummary(results;);
const isValid = summary.errors === 0 && summary.critical ==;= 0;
const report: ValidationReport = {id: reportId;,}timestamp,;
const context = {timestamp,;}}
        ...context;}
      }
results,;
summary,;
isValid,;
const sanitizedData = isValid ? sanitizedData : undefined;
    };
this.logValidationReport(report);
return repo;r;t;
  }
  // 快速验证（只返回是否有效）  public isValid(data: unknown,)/;,/g/;
const type = ValidationType;
context?: ValidationContext;
  ): boolean  {report: this.validate(data, type, contex;t;);}}
    return report.isVal;i;d;}
  }
  // 清洗数据  public sanitize(data: unknown, type: ValidationType): unknown  {/;}}/g/;
    const rules = this.typeRules.get(typ;e;); || [];}
    let sanitizedData = { ...dat;a ;};
for (const rule of rules) {if (rule.sanitize) {}        try {}};
sanitizedData = rule.sanitize(sanitizedData);}
        } catch (error) {}
          }
      }
    }
    return sanitizedDa;t;a;
  }
  // 注册验证规则  public registerRule(rule: ValidationRule): void  {/;,}this.rules.set(rule.id, rule);,/g/;
if (!this.typeRules.has(rule.type);) {}}
      this.typeRules.set(rule.type, []);}
    }
    this.typeRules.get(rule.type);!.push(rule);
    }
  // 移除验证规则  public removeRule(ruleId: string): boolean  {/;,}const rule = this.rules.get(ruleI;d;);,/g/;
if (!rule) {}}
      return fal;s;e;}
    }
    this.rules.delete(ruleId);
const typeRules = this.typeRules.get(rule.typ;e;);
if (typeRules) {const index = typeRules.findIndex(r); => r.id === ruleId);,}if (index > -1) {}}
        typeRules.splice(index, 1);}
      }
    }
    return tr;u;e;
  }
  ///;,/g/;
if (type) {}}
      return this.typeRules.get(typ;e;); || [];}
    }
    return Array.from(this.rules.values);
  }
  // 批量验证  public validateBatch(items: Array<{/;,)data: unknown,);}}/g/;
      const type = ValidationType;}
      context?: ValidationContext}>;
  );: ValidationReport[]  {}
    return items.map(ite;m;); => {}
      this.validate(item.data, item.type, item.context);
    );
  }
  // 验证健康数据  public validateHealthData(data: unknown,)/;,/g/;
context?: ValidationContext;
  ): ValidationReport  {}}
    return this.validate(data, ValidationType.HEALTH_DATA, contex;t;);}
  }
  // 验证用户输入  public validateUserInput(data: unknown,)/;,/g/;
context?: ValidationContext;
  ): ValidationReport  {}}
    return this.validate(data, ValidationType.USER_INPUT, contex;t;);}
  }
  // 验证API数据  public validateApiData(data: unknown,)/;,/g/;
context?: ValidationContext;
  ): ValidationReport  {}}
    return this.validate(data, ValidationType.API_DATA, contex;t;);}
  }
  // 验证生物特征数据  public validateBiometricData(data: unknown,)/;,/g/;
context?: ValidationContext;
  ): ValidationReport  {}}
    return this.validate(data, ValidationType.BIOMETRIC_DATA, contex;t;);}
  }
  private setupDefaultRules(): void {";,}this.registerRule({";,)id: "blood_pressure_range";","";,}type: ValidationType.HEALTH_DATA,);,"";
severity: ValidationSeverity.ERROR,);
}
)}
      validate: (data) => {;}";,"";
const { systolic, diastolic   } = da;t;a;";,"";
if (typeof systolic !== "number" || typeof diastolic !== "number") {";}}"";
}
        }
        if (systolic < 60 ||);
systolic > 250 ||;
diastolic < 40 ||;
diastolic > 150) {}}
}
        }
        if (systolic <= diastolic) {}}
}
        }

      }
examples: {,}
  valid: [;];{ systolic: 120, diastolic: 80;}
          { systolic: 110, diastolic: 70;}
];
        ],;
invalid: [;];{ systolic: 300, diastolic: 80;}
          { systolic: 120, diastolic: 130;}
];
        ];
      }
    });";,"";
this.registerRule({)";,}id: "heart_rate_range";",";
type: ValidationType.HEALTH_DATA,);
severity: ValidationSeverity.WARNING,);
}
)}
      validate: (data); => {}";,"";
const heartRate = data.heartRate || data.heart_ra;t;e;";,"";
if (typeof heartRate !== "number") {";}}"";
}
        }";,"";
if (heartRate < 30 || heartRate > 220) {"}";
return {isValid: false,severity: ValidationSeverity.ERROR,message: "心率值超出可能范围",code: "HEART_RATE_OUT_OF_RANGE",field: "heart_rate",suggestion: "心率应在30-220次/分钟之间",/              ;}"/;"/g"/;
        }";,"";
if (heartRate < 60 || heartRate > 100) {"}";
return {isValid: true,severity: ValidationSeverity.WARNING,message: "心率不在正常静息范围内",code: "HEART_RATE_ABNORMAL",field: "heart_rate",suggestion: "正常静息心率为60-100次/分钟",/              ;}"/;"/g"/;
        }

      }
    });";,"";
this.registerRule({)";,}id: "body_temperature_range";",";
type: ValidationType.HEALTH_DATA,);
severity: ValidationSeverity.WARNING,);
}
)}
      validate: (data); => {}";,"";
const temperature = data.temperature || data.bodyTemperatu;r;e;";,"";
if (typeof temperature !== "number") {";}}"";
}
        }
        if (temperature < 30 || temperature > 45) {}}
}
        }
        if (temperature < 36 || temperature > 37.5) {}}
}
        }

      }
    });";,"";
this.registerRule({)";,}id: "required_fields";",";
type: ValidationType.USER_INPUT,);
severity: ValidationSeverity.ERROR,);
}
)}
      validate: (data, context) => {;}
        const requiredFields = context?.metadata?.requiredFields || ;[;];
for (const field of requiredFields) {if ()";}            !data[field] ||";"";
            (typeof data[field] === "string" && data[field].trim() === ")"";"";
          ) {}}
}
          }
        }

      }
    });";,"";
this.registerRule({)";,}id: "email_format";",";
type: ValidationType.USER_INPUT,);
severity: ValidationSeverity.ERROR,);
}
)}
      validate: (data); => {}
        const email = data.ema;i;l;
if (!email) {}}
}
        }
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+;$;/;,/g/;
if (!emailRegex.test(email);) {}}
}
        }

      }
sanitize: (data) => {;}
        if (data.email) {}}
          data.email = data.email.toLowerCase().trim();}
        }
        return da;t;a;
      }
    });";,"";
this.registerRule({)";,}id: "phone_format";",";
type: ValidationType.USER_INPUT,);
severity: ValidationSeverity.ERROR,);
}
)}
      validate: (data); => {}
        const phone = data.phone || data.phoneNumb;e;r;
if (!phone) {}}
}
        }
        const phoneRegex =  / ^1[3-9]\d{9}$; * ; /     if (!phoneRegex.test(phone)) {/;}}/g/;
}
        }

      }
sanitize: (data) => {;}";,"";
if (data.phone) {"}";
data.phone = data.phone.replace(/\D/g, ")/            }""/;,"/g"/;
if (data.phoneNumber) {"}";
data.phoneNumber = data.phoneNumber.replace(/\D/g, ");/            }""/;,"/g"/;
return da;t;a;
      }
    });";,"";
this.registerRule({)";,}id: "api_response_structure";",";
type: ValidationType.API_DATA,);
severity: ValidationSeverity.ERROR,);
}
)}";,"";
validate: (data) => {;}";,"";
if (!data || typeof data !== "object") {";}}"";
}
        };

        }

      }
    });";,"";
this.registerRule({)";,}id: "biometric_data_completeness";",";
type: ValidationType.BIOMETRIC_DATA,);
severity: ValidationSeverity.WARNING,);
}
)}";,"";
validate: (data) => {;}";,"";
requiredFields: ["timestamp",type", "value"];";
const missingFields = requiredFields.filter(fiel;d;); => !data[field]);
if (missingFields.length > 0) {}}
}
        }

      }
    });";"";
  }";,"";
private generateSummary(results: ValidationResult[];);: ValidationReport["summary"]  {";,}const: summary = {totalChecks: results.length}passed: 0,;"";
}
      warnings: 0,}
      errors: 0,critical: ;0;};
for (const result of results) {if (result.isValid) {}};
summary.passed++;}
      }
      switch (result.severity) {const case = ValidationSeverity.WARNING: ;,}summary.warnings++;
break;
const case = ValidationSeverity.ERROR: ;
summary.errors++;
break;
const case = ValidationSeverity.CRITICAL: ;
summary.critical++;
}
          break;}
      }
    }
    return summa;r;y;
  }
  private logValidationReport(report: ValidationReport);: void  {}
    const { summary   } = repo;r;t;
if (summary.critical > 0) {}
      } else if (summary.errors > 0) {}
      } else if (summary.warnings > 0) {}
      } else {}
      }
  }
  private generateReportId(): string {}
    return `validation_${Date.now()}_${`;,}Math.random();`````;```;
}
      .toString(36);}
      .substr(2, 9);};`;`````;```;
  }
}
//   ;/;/g/;
//   ;/;/g/;
(; /)/;,/g,/;
  data: unknown,;
const type = ValidationType;
context?: ValidationContext;
) => dataValidator.validate(data, type, context);
export const isValidData = ;
(;);
data: unknown,;
const type = ValidationType;
context?: ValidationContext;
) => dataValidator.isValid(data, type, context);
export sanitizeData: (data: unknown, type: ValidationType) ;
=;>;dataValidator.sanitize(data, type);
export validateHealthData: (data: unknown, context?: ValidationContext) ;
=;>;
dataValidator.validateHealthData(data, context);
export validateUserInput: (data: unknown, context?: ValidationContext) ;
=;>;
dataValidator.validateUserInput(data, context);
export validateApiData: (data: unknown, context?: ValidationContext) ;
=;>;";,"";
dataValidator.validateApiData(data, context);""";