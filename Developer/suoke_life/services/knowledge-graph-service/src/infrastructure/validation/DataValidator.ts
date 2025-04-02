import { 
  BaseEntity, 
  Herb, 
  Formula, 
  Syndrome, 
  Constitution,
  ConstitutionType 
} from '../../domain/ontology/TCMOntology';

export interface ValidationRule {
  type: 'required' | 'format' | 'range' | 'enum' | 'custom';
  field: string;
  message: string;
  validate: (value: any) => boolean;
}

export interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
  warnings: ValidationWarning[];
}

export interface ValidationError {
  field: string;
  message: string;
  code: string;
}

export interface ValidationWarning {
  field: string;
  message: string;
  suggestion?: string;
}

export class TCMDataValidator {
  private rules: Map<string, ValidationRule[]> = new Map();

  constructor() {
    this.initializeRules();
  }

  private initializeRules(): void {
    // 基础实体验证规则
    this.rules.set('BaseEntity', [
      {
        type: 'required',
        field: 'name',
        message: '名称是必需的',
        validate: (value) => !!value && value.trim().length > 0
      },
      {
        type: 'format',
        field: 'id',
        message: 'ID格式无效',
        validate: (value) => /^[a-zA-Z0-9_-]+$/.test(value)
      }
    ]);

    // 中药验证规则
    this.rules.set('Herb', [
      {
        type: 'required',
        field: 'properties',
        message: '药性信息是必需的',
        validate: (value) => !!value && Object.keys(value).length > 0
      },
      {
        type: 'custom',
        field: 'interactions',
        message: '药物相互作用信息无效',
        validate: (value) => {
          if (!Array.isArray(value)) return false;
          return value.every(interaction => 
            interaction.herb && 
            interaction.type && 
            interaction.description
          );
        }
      }
    ]);

    // 方剂验证规则
    this.rules.set('Formula', [
      {
        type: 'required',
        field: 'composition',
        message: '方剂组成是必需的',
        validate: (value) => Array.isArray(value) && value.length > 0
      },
      {
        type: 'custom',
        field: 'composition',
        message: '方剂组成信息无效',
        validate: (value) => {
          if (!Array.isArray(value)) return false;
          return value.every(herb => 
            herb.herb && 
            ['君', '臣', '佐', '使'].includes(herb.role) &&
            herb.amount
          );
        }
      }
    ]);

    // 体质验证规则
    this.rules.set('Constitution', [
      {
        type: 'enum',
        field: 'type',
        message: '体质类型无效',
        validate: (value) => Object.values(ConstitutionType).includes(value)
      },
      {
        type: 'required',
        field: 'characteristics',
        message: '体质特征是必需的',
        validate: (value) => Array.isArray(value) && value.length > 0
      }
    ]);
  }

  /**
   * 验证中药数据
   */
  public validateHerb(herb: Herb): ValidationResult {
    const baseResult = this.validateEntity(herb, 'BaseEntity');
    const herbResult = this.validateEntity(herb, 'Herb');

    return this.mergeValidationResults([baseResult, herbResult]);
  }

  /**
   * 验证方剂数据
   */
  public validateFormula(formula: Formula): ValidationResult {
    const baseResult = this.validateEntity(formula, 'BaseEntity');
    const formulaResult = this.validateEntity(formula, 'Formula');

    return this.mergeValidationResults([baseResult, formulaResult]);
  }

  /**
   * 验证体质数据
   */
  public validateConstitution(constitution: Constitution): ValidationResult {
    const baseResult = this.validateEntity(constitution, 'BaseEntity');
    const constitutionResult = this.validateEntity(constitution, 'Constitution');

    return this.mergeValidationResults([baseResult, constitutionResult]);
  }

  /**
   * 验证证候数据
   */
  public validateSyndrome(syndrome: Syndrome): ValidationResult {
    const baseResult = this.validateEntity(syndrome, 'BaseEntity');
    // 添加证候特定的验证规则
    return baseResult;
  }

  /**
   * 验证实体数据
   */
  private validateEntity(entity: any, type: string): ValidationResult {
    const rules = this.rules.get(type) || [];
    const errors: ValidationError[] = [];
    const warnings: ValidationWarning[] = [];

    for (const rule of rules) {
      const value = entity[rule.field];
      if (!rule.validate(value)) {
        errors.push({
          field: rule.field,
          message: rule.message,
          code: `${type}_${rule.type}_${rule.field}`
        });
      }
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings
    };
  }

  /**
   * 合并多个验证结果
   */
  private mergeValidationResults(results: ValidationResult[]): ValidationResult {
    const merged: ValidationResult = {
      isValid: true,
      errors: [],
      warnings: []
    };

    for (const result of results) {
      merged.isValid = merged.isValid && result.isValid;
      merged.errors.push(...result.errors);
      merged.warnings.push(...result.warnings);
    }

    return merged;
  }

  /**
   * 添加自定义验证规则
   */
  public addCustomRule(type: string, rule: ValidationRule): void {
    const rules = this.rules.get(type) || [];
    rules.push(rule);
    this.rules.set(type, rules);
  }
}