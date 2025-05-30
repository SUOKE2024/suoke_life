/**
 * 索克生活 - 数据验证系统
 * 提供健康数据、用户输入、API数据的验证和清洗功能
 */

import { errorHandler, ErrorType } from '../error/ErrorHandler';

export enum ValidationType {
  HEALTH_DATA = 'HEALTH_DATA',
  USER_INPUT = 'USER_INPUT',
  API_DATA = 'API_DATA',
  MEDICAL_RECORD = 'MEDICAL_RECORD',
  BIOMETRIC_DATA = 'BIOMETRIC_DATA',
  LIFESTYLE_DATA = 'LIFESTYLE_DATA'
}

export enum ValidationSeverity {
  INFO = 'INFO',
  WARNING = 'WARNING',
  ERROR = 'ERROR',
  CRITICAL = 'CRITICAL'
}

export interface ValidationRule {
  id: string;
  name: string;
  type: ValidationType;
  severity: ValidationSeverity;
  validate: (data: any, context?: ValidationContext) => ValidationResult;
  sanitize?: (data: any) => any;
  description: string;
  examples?: {
    valid: any[];
    invalid: any[];
  };
}

export interface ValidationContext {
  userId?: string;
  dataType?: string;
  timestamp?: number;
  source?: string;
  metadata?: Record<string, any>;
}

export interface ValidationResult {
  isValid: boolean;
  severity: ValidationSeverity;
  message: string;
  code: string;
  field?: string;
  value?: any;
  suggestion?: string;
  sanitizedValue?: any;
}

export interface ValidationReport {
  id: string;
  timestamp: number;
  context: ValidationContext;
  results: ValidationResult[];
  summary: {
    totalChecks: number;
    passed: number;
    warnings: number;
    errors: number;
    critical: number;
  };
  isValid: boolean;
  sanitizedData?: any;
}

export class DataValidator {
  private static instance: DataValidator;
  private rules: Map<string, ValidationRule> = new Map();
  private typeRules: Map<ValidationType, ValidationRule[]> = new Map();

  private constructor() {
    this.setupDefaultRules();
  }

  public static getInstance(): DataValidator {
    if (!DataValidator.instance) {
      DataValidator.instance = new DataValidator();
    }
    return DataValidator.instance;
  }

  /**
   * 验证数据
   */
  public validate(
    data: any,
    type: ValidationType,
    context: ValidationContext = {}
  ): ValidationReport {
    const reportId = this.generateReportId();
    const timestamp = Date.now();
    
    const rules = this.typeRules.get(type) || [];
    const results: ValidationResult[] = [];
    let sanitizedData = { ...data };

    // 执行所有相关规则
    for (const rule of rules) {
      try {
        const result = rule.validate(data, context);
        results.push(result);

        // 如果有清洗函数且验证通过，应用清洗
        if (rule.sanitize && result.isValid) {
          sanitizedData = rule.sanitize(sanitizedData);
        }
      } catch (error) {
        results.push({
          isValid: false,
          severity: ValidationSeverity.ERROR,
          message: `验证规则执行失败: ${rule.name}`,
          code: 'RULE_EXECUTION_ERROR',
          field: rule.id
        });
      }
    }

    // 生成摘要
    const summary = this.generateSummary(results);
    const isValid = summary.errors === 0 && summary.critical === 0;

    const report: ValidationReport = {
      id: reportId,
      timestamp,
      context: {
        timestamp,
        ...context
      },
      results,
      summary,
      isValid,
      sanitizedData: isValid ? sanitizedData : undefined
    };

    // 记录验证结果
    this.logValidationReport(report);

    return report;
  }

  /**
   * 快速验证（只返回是否有效）
   */
  public isValid(data: any, type: ValidationType, context?: ValidationContext): boolean {
    const report = this.validate(data, type, context);
    return report.isValid;
  }

  /**
   * 清洗数据
   */
  public sanitize(data: any, type: ValidationType): any {
    const rules = this.typeRules.get(type) || [];
    let sanitizedData = { ...data };

    for (const rule of rules) {
      if (rule.sanitize) {
        try {
          sanitizedData = rule.sanitize(sanitizedData);
        } catch (error) {
          console.warn(`数据清洗失败: ${rule.name}`, error);
        }
      }
    }

    return sanitizedData;
  }

  /**
   * 注册验证规则
   */
  public registerRule(rule: ValidationRule): void {
    this.rules.set(rule.id, rule);
    
    if (!this.typeRules.has(rule.type)) {
      this.typeRules.set(rule.type, []);
    }
    
    this.typeRules.get(rule.type)!.push(rule);
    console.log(`✅ Validation rule registered: ${rule.id}`);
  }

  /**
   * 移除验证规则
   */
  public removeRule(ruleId: string): boolean {
    const rule = this.rules.get(ruleId);
    if (!rule) {
      return false;
    }

    this.rules.delete(ruleId);
    
    const typeRules = this.typeRules.get(rule.type);
    if (typeRules) {
      const index = typeRules.findIndex(r => r.id === ruleId);
      if (index > -1) {
        typeRules.splice(index, 1);
      }
    }

    console.log(`❌ Validation rule removed: ${ruleId}`);
    return true;
  }

  /**
   * 获取规则列表
   */
  public getRules(type?: ValidationType): ValidationRule[] {
    if (type) {
      return this.typeRules.get(type) || [];
    }
    return Array.from(this.rules.values());
  }

  /**
   * 批量验证
   */
  public validateBatch(
    items: Array<{ data: any; type: ValidationType; context?: ValidationContext }>
  ): ValidationReport[] {
    return items.map(item => this.validate(item.data, item.type, item.context));
  }

  /**
   * 验证健康数据
   */
  public validateHealthData(data: any, context?: ValidationContext): ValidationReport {
    return this.validate(data, ValidationType.HEALTH_DATA, context);
  }

  /**
   * 验证用户输入
   */
  public validateUserInput(data: any, context?: ValidationContext): ValidationReport {
    return this.validate(data, ValidationType.USER_INPUT, context);
  }

  /**
   * 验证API数据
   */
  public validateApiData(data: any, context?: ValidationContext): ValidationReport {
    return this.validate(data, ValidationType.API_DATA, context);
  }

  /**
   * 验证生物特征数据
   */
  public validateBiometricData(data: any, context?: ValidationContext): ValidationReport {
    return this.validate(data, ValidationType.BIOMETRIC_DATA, context);
  }

  private setupDefaultRules(): void {
    // 健康数据验证规则
    this.registerRule({
      id: 'blood_pressure_range',
      name: '血压范围验证',
      type: ValidationType.HEALTH_DATA,
      severity: ValidationSeverity.ERROR,
      description: '验证血压值是否在合理范围内',
      validate: (data) => {
        const { systolic, diastolic } = data;
        
        if (typeof systolic !== 'number' || typeof diastolic !== 'number') {
          return {
            isValid: false,
            severity: ValidationSeverity.ERROR,
            message: '血压值必须是数字',
            code: 'INVALID_BLOOD_PRESSURE_TYPE',
            field: 'blood_pressure'
          };
        }

        if (systolic < 60 || systolic > 250 || diastolic < 40 || diastolic > 150) {
          return {
            isValid: false,
            severity: ValidationSeverity.ERROR,
            message: '血压值超出正常范围',
            code: 'BLOOD_PRESSURE_OUT_OF_RANGE',
            field: 'blood_pressure',
            suggestion: '收缩压应在60-250mmHg之间，舒张压应在40-150mmHg之间'
          };
        }

        if (systolic <= diastolic) {
          return {
            isValid: false,
            severity: ValidationSeverity.ERROR,
            message: '收缩压应大于舒张压',
            code: 'INVALID_BLOOD_PRESSURE_RELATION',
            field: 'blood_pressure'
          };
        }

        return {
          isValid: true,
          severity: ValidationSeverity.INFO,
          message: '血压值有效',
          code: 'VALID_BLOOD_PRESSURE'
        };
      },
      examples: {
        valid: [
          { systolic: 120, diastolic: 80 },
          { systolic: 110, diastolic: 70 }
        ],
        invalid: [
          { systolic: 300, diastolic: 80 },
          { systolic: 120, diastolic: 130 }
        ]
      }
    });

    this.registerRule({
      id: 'heart_rate_range',
      name: '心率范围验证',
      type: ValidationType.HEALTH_DATA,
      severity: ValidationSeverity.WARNING,
      description: '验证心率是否在正常范围内',
      validate: (data) => {
        const heartRate = data.heartRate || data.heart_rate;
        
        if (typeof heartRate !== 'number') {
          return {
            isValid: false,
            severity: ValidationSeverity.ERROR,
            message: '心率值必须是数字',
            code: 'INVALID_HEART_RATE_TYPE',
            field: 'heart_rate'
          };
        }

        if (heartRate < 30 || heartRate > 220) {
          return {
            isValid: false,
            severity: ValidationSeverity.ERROR,
            message: '心率值超出可能范围',
            code: 'HEART_RATE_OUT_OF_RANGE',
            field: 'heart_rate',
            suggestion: '心率应在30-220次/分钟之间'
          };
        }

        if (heartRate < 60 || heartRate > 100) {
          return {
            isValid: true,
            severity: ValidationSeverity.WARNING,
            message: '心率不在正常静息范围内',
            code: 'HEART_RATE_ABNORMAL',
            field: 'heart_rate',
            suggestion: '正常静息心率为60-100次/分钟'
          };
        }

        return {
          isValid: true,
          severity: ValidationSeverity.INFO,
          message: '心率值正常',
          code: 'VALID_HEART_RATE'
        };
      }
    });

    this.registerRule({
      id: 'body_temperature_range',
      name: '体温范围验证',
      type: ValidationType.HEALTH_DATA,
      severity: ValidationSeverity.WARNING,
      description: '验证体温是否在正常范围内',
      validate: (data) => {
        const temperature = data.temperature || data.bodyTemperature;
        
        if (typeof temperature !== 'number') {
          return {
            isValid: false,
            severity: ValidationSeverity.ERROR,
            message: '体温值必须是数字',
            code: 'INVALID_TEMPERATURE_TYPE',
            field: 'temperature'
          };
        }

        if (temperature < 30 || temperature > 45) {
          return {
            isValid: false,
            severity: ValidationSeverity.ERROR,
            message: '体温值超出可能范围',
            code: 'TEMPERATURE_OUT_OF_RANGE',
            field: 'temperature',
            suggestion: '体温应在30-45°C之间'
          };
        }

        if (temperature < 36 || temperature > 37.5) {
          return {
            isValid: true,
            severity: ValidationSeverity.WARNING,
            message: '体温不在正常范围内',
            code: 'TEMPERATURE_ABNORMAL',
            field: 'temperature',
            suggestion: '正常体温为36-37.5°C'
          };
        }

        return {
          isValid: true,
          severity: ValidationSeverity.INFO,
          message: '体温值正常',
          code: 'VALID_TEMPERATURE'
        };
      }
    });

    // 用户输入验证规则
    this.registerRule({
      id: 'required_fields',
      name: '必填字段验证',
      type: ValidationType.USER_INPUT,
      severity: ValidationSeverity.ERROR,
      description: '验证必填字段是否存在',
      validate: (data, context) => {
        const requiredFields = context?.metadata?.requiredFields || [];
        
        for (const field of requiredFields) {
          if (!data[field] || (typeof data[field] === 'string' && data[field].trim() === '')) {
            return {
              isValid: false,
              severity: ValidationSeverity.ERROR,
              message: `必填字段缺失: ${field}`,
              code: 'REQUIRED_FIELD_MISSING',
              field
            };
          }
        }

        return {
          isValid: true,
          severity: ValidationSeverity.INFO,
          message: '所有必填字段已填写',
          code: 'REQUIRED_FIELDS_VALID'
        };
      }
    });

    this.registerRule({
      id: 'email_format',
      name: '邮箱格式验证',
      type: ValidationType.USER_INPUT,
      severity: ValidationSeverity.ERROR,
      description: '验证邮箱地址格式',
      validate: (data) => {
        const email = data.email;
        
        if (!email) {
          return {
            isValid: true,
            severity: ValidationSeverity.INFO,
            message: '邮箱字段为空',
            code: 'EMAIL_EMPTY'
          };
        }

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        
        if (!emailRegex.test(email)) {
          return {
            isValid: false,
            severity: ValidationSeverity.ERROR,
            message: '邮箱格式不正确',
            code: 'INVALID_EMAIL_FORMAT',
            field: 'email',
            suggestion: '请输入有效的邮箱地址，如：user@example.com'
          };
        }

        return {
          isValid: true,
          severity: ValidationSeverity.INFO,
          message: '邮箱格式正确',
          code: 'VALID_EMAIL'
        };
      },
      sanitize: (data) => {
        if (data.email) {
          data.email = data.email.toLowerCase().trim();
        }
        return data;
      }
    });

    this.registerRule({
      id: 'phone_format',
      name: '手机号格式验证',
      type: ValidationType.USER_INPUT,
      severity: ValidationSeverity.ERROR,
      description: '验证手机号码格式',
      validate: (data) => {
        const phone = data.phone || data.phoneNumber;
        
        if (!phone) {
          return {
            isValid: true,
            severity: ValidationSeverity.INFO,
            message: '手机号字段为空',
            code: 'PHONE_EMPTY'
          };
        }

        // 中国手机号格式
        const phoneRegex = /^1[3-9]\d{9}$/;
        
        if (!phoneRegex.test(phone)) {
          return {
            isValid: false,
            severity: ValidationSeverity.ERROR,
            message: '手机号格式不正确',
            code: 'INVALID_PHONE_FORMAT',
            field: 'phone',
            suggestion: '请输入有效的11位手机号码'
          };
        }

        return {
          isValid: true,
          severity: ValidationSeverity.INFO,
          message: '手机号格式正确',
          code: 'VALID_PHONE'
        };
      },
      sanitize: (data) => {
        if (data.phone) {
          data.phone = data.phone.replace(/\D/g, '');
        }
        if (data.phoneNumber) {
          data.phoneNumber = data.phoneNumber.replace(/\D/g, '');
        }
        return data;
      }
    });

    // API数据验证规则
    this.registerRule({
      id: 'api_response_structure',
      name: 'API响应结构验证',
      type: ValidationType.API_DATA,
      severity: ValidationSeverity.ERROR,
      description: '验证API响应的基本结构',
      validate: (data) => {
        if (!data || typeof data !== 'object') {
          return {
            isValid: false,
            severity: ValidationSeverity.ERROR,
            message: 'API响应必须是对象',
            code: 'INVALID_API_RESPONSE_TYPE'
          };
        }

        if (!data.hasOwnProperty('success') && !data.hasOwnProperty('status')) {
          return {
            isValid: false,
            severity: ValidationSeverity.WARNING,
            message: 'API响应缺少状态字段',
            code: 'MISSING_STATUS_FIELD',
            suggestion: '建议包含success或status字段'
          };
        }

        return {
          isValid: true,
          severity: ValidationSeverity.INFO,
          message: 'API响应结构有效',
          code: 'VALID_API_RESPONSE'
        };
      }
    });

    // 生物特征数据验证规则
    this.registerRule({
      id: 'biometric_data_completeness',
      name: '生物特征数据完整性验证',
      type: ValidationType.BIOMETRIC_DATA,
      severity: ValidationSeverity.WARNING,
      description: '验证生物特征数据的完整性',
      validate: (data) => {
        const requiredFields = ['timestamp', 'type', 'value'];
        const missingFields = requiredFields.filter(field => !data[field]);

        if (missingFields.length > 0) {
          return {
            isValid: false,
            severity: ValidationSeverity.WARNING,
            message: `生物特征数据缺少字段: ${missingFields.join(', ')}`,
            code: 'INCOMPLETE_BIOMETRIC_DATA',
            suggestion: '建议包含完整的时间戳、类型和数值信息'
          };
        }

        return {
          isValid: true,
          severity: ValidationSeverity.INFO,
          message: '生物特征数据完整',
          code: 'COMPLETE_BIOMETRIC_DATA'
        };
      }
    });
  }

  private generateSummary(results: ValidationResult[]): ValidationReport['summary'] {
    const summary = {
      totalChecks: results.length,
      passed: 0,
      warnings: 0,
      errors: 0,
      critical: 0
    };

    for (const result of results) {
      if (result.isValid) {
        summary.passed++;
      }

      switch (result.severity) {
        case ValidationSeverity.WARNING:
          summary.warnings++;
          break;
        case ValidationSeverity.ERROR:
          summary.errors++;
          break;
        case ValidationSeverity.CRITICAL:
          summary.critical++;
          break;
      }
    }

    return summary;
  }

  private logValidationReport(report: ValidationReport): void {
    const { summary } = report;
    
    if (summary.critical > 0) {
      console.error('🚨 Critical validation errors:', report);
    } else if (summary.errors > 0) {
      console.warn('❌ Validation errors:', report);
    } else if (summary.warnings > 0) {
      console.info('⚠️ Validation warnings:', report);
    } else {
      console.log('✅ Validation passed:', report.id);
    }
  }

  private generateReportId(): string {
    return `validation_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}

// 导出单例实例
export const dataValidator = DataValidator.getInstance();

// 便捷函数
export const validateData = (
  data: any,
  type: ValidationType,
  context?: ValidationContext
) => dataValidator.validate(data, type, context);

export const isValidData = (
  data: any,
  type: ValidationType,
  context?: ValidationContext
) => dataValidator.isValid(data, type, context);

export const sanitizeData = (data: any, type: ValidationType) =>
  dataValidator.sanitize(data, type);

export const validateHealthData = (data: any, context?: ValidationContext) =>
  dataValidator.validateHealthData(data, context);

export const validateUserInput = (data: any, context?: ValidationContext) =>
  dataValidator.validateUserInput(data, context);

export const validateApiData = (data: any, context?: ValidationContext) =>
  dataValidator.validateApiData(data, context); 