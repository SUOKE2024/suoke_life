/**
 * 动作简化机制
 * 为操作困难的用户提供简化的操作方式，减少操作步骤
 */
import { AccessibilityAction, SimplifiedModeConfig } from '../types/accessibility';
import { logger } from '../utils/logger';

/**
 * 简化动作类型
 */
export enum SimplifiedActionType {
  TAP = 'tap',                  // 点击
  DOUBLE_TAP = 'doubleTap',     // 双击
  LONG_PRESS = 'longPress',     // 长按
  SWIPE = 'swipe',              // 滑动
  PINCH = 'pinch',              // 捏合
  VOICE = 'voice',              // 语音
  TILT = 'tilt',                // 倾斜
  AUTO = 'auto'                 // 自动操作
}

/**
 * 简化动作服务
 */
export class SimplifiedActionsService {
  private readonly DEFAULT_SIMPLIFICATION_LEVEL = 1;
  private simplificationConfig: SimplifiedModeConfig;
  
  constructor() {
    // 默认配置
    this.simplificationConfig = {
      level: this.DEFAULT_SIMPLIFICATION_LEVEL,
      hideNonEssentialElements: false,
      simplifyNavigation: true,
      reduceFunctionality: false,
      useSimpleLanguage: true,
      largeTargets: true,
      simplifiedLayout: true
    };
  }
  
  /**
   * 设置简化配置
   * @param config 简化配置
   */
  public setSimplificationConfig(config: Partial<SimplifiedModeConfig>): void {
    this.simplificationConfig = {
      ...this.simplificationConfig,
      ...config
    };
    
    // 确保级别在有效范围内
    this.simplificationConfig.level = Math.max(1, Math.min(3, this.simplificationConfig.level));
  }
  
  /**
   * 获取当前简化配置
   * @returns 当前简化配置
   */
  public getSimplificationConfig(): SimplifiedModeConfig {
    return { ...this.simplificationConfig };
  }
  
  /**
   * 根据简化级别生成推荐的简化配置
   * @param level 简化级别(1-3)
   * @returns 简化配置
   */
  public getConfigForLevel(level: number): SimplifiedModeConfig {
    const validLevel = Math.max(1, Math.min(3, level));
    
    switch (validLevel) {
      case 1: // 轻度简化
        return {
          level: 1,
          hideNonEssentialElements: false,
          simplifyNavigation: true,
          reduceFunctionality: false,
          useSimpleLanguage: true,
          largeTargets: true,
          simplifiedLayout: false
        };
      case 2: // 中度简化
        return {
          level: 2,
          hideNonEssentialElements: true,
          simplifyNavigation: true,
          reduceFunctionality: false,
          useSimpleLanguage: true,
          largeTargets: true,
          simplifiedLayout: true
        };
      case 3: // 高度简化
        return {
          level: 3,
          hideNonEssentialElements: true,
          simplifyNavigation: true,
          reduceFunctionality: true,
          useSimpleLanguage: true,
          largeTargets: true,
          simplifiedLayout: true
        };
      default:
        return this.getConfigForLevel(1);
    }
  }
  
  /**
   * 简化连续操作步骤
   * 将多步操作合并为更简单的流程
   * @param actions 原始操作步骤
   * @returns 简化后的操作步骤
   */
  public simplifyActionSequence(actions: AccessibilityAction[]): AccessibilityAction[] {
    try {
      if (!actions || actions.length === 0) {
        return [];
      }
      
      // 根据简化级别决定处理方式
      switch (this.simplificationConfig.level) {
        case 1: // 轻度简化：合并相似连续操作
          return this.combineConsecutiveSimilarActions(actions);
        case 2: // 中度简化：提供替代简化操作
          return this.provideAlternativeActions(actions);
        case 3: // 高度简化：最大程度自动化和简化
          return this.maximumSimplification(actions);
        default:
          return this.combineConsecutiveSimilarActions(actions);
      }
    } catch (error) {
      logger.error('简化操作序列失败', { error, actions });
      return actions; // 出错时返回原始操作
    }
  }
  
  /**
   * 合并连续的相似操作
   * @param actions 原始操作
   * @returns 合并后的操作
   */
  private combineConsecutiveSimilarActions(actions: AccessibilityAction[]): AccessibilityAction[] {
    const result: AccessibilityAction[] = [];
    let currentAction: AccessibilityAction | null = null;
    let count = 0;
    
    for (const action of actions) {
      if (!currentAction) {
        currentAction = { ...action };
        count = 1;
        continue;
      }
      
      // 检查是否可以合并
      if (action.type === currentAction.type) {
        count++;
      } else {
        // 添加之前累积的操作
        if (count > 1) {
          currentAction.description = `${count}次${currentAction.description}`;
        }
        result.push(currentAction);
        
        // 开始累积新操作
        currentAction = { ...action };
        count = 1;
      }
    }
    
    // 添加最后一组操作
    if (currentAction) {
      if (count > 1) {
        currentAction.description = `${count}次${currentAction.description}`;
      }
      result.push(currentAction);
    }
    
    return result;
  }
  
  /**
   * 提供替代简化操作
   * @param actions 原始操作
   * @returns 替代操作
   */
  private provideAlternativeActions(actions: AccessibilityAction[]): AccessibilityAction[] {
    return actions.map(action => {
      const simplifiedAction = { ...action };
      
      // 对有简化替代方案的操作进行替换
      if (action.simplifiedAlternative) {
        simplifiedAction.description = action.simplifiedAlternative;
      } else {
        // 根据操作类型提供默认的简化描述
        switch (action.type) {
          case 'swipe':
            simplifiedAction.description = `点击箭头按钮代替${action.description}`;
            break;
          case 'longPress':
            simplifiedAction.description = `点击菜单按钮代替${action.description}`;
            break;
          default:
            // 保持原始描述
            break;
        }
      }
      
      return simplifiedAction;
    });
  }
  
  /**
   * 最大程度简化操作
   * @param actions 原始操作
   * @returns 最大简化的操作
   */
  private maximumSimplification(actions: AccessibilityAction[]): AccessibilityAction[] {
    // 分析操作序列的目的
    const purpose = this.analyzePurpose(actions);
    
    // 根据目的提供最简化的操作方式
    switch (purpose) {
      case 'navigation':
        // 导航操作简化为一步
        return [{
          type: 'tap',
          description: '点击前往按钮直接到达目标页面'
        }];
      case 'selection':
        // 选择操作简化
        return [{
          type: 'tap',
          description: '点击选择按钮查看所有可选项'
        }];
      case 'input':
        // 输入操作简化
        return [{
          type: 'voice',
          description: '使用语音输入或选择预设选项'
        }];
      default:
        // 尝试将操作减少到最多2步
        if (actions.length > 2) {
          return [
            actions[0],
            {
              type: 'tap',
              description: '点击完成按钮完成剩余操作'
            }
          ];
        }
        return actions;
    }
  }
  
  /**
   * 分析操作序列的目的
   * @param actions 操作序列
   * @returns 操作目的类型
   */
  private analyzePurpose(actions: AccessibilityAction[]): 'navigation' | 'selection' | 'input' | 'other' {
    // 分析操作类型的分布
    const typeCount: Record<string, number> = {};
    for (const action of actions) {
      typeCount[action.type] = (typeCount[action.type] || 0) + 1;
    }
    
    // 分析操作描述中的关键词
    const allDescriptions = actions.map(a => a.description).join(' ').toLowerCase();
    
    if (allDescriptions.includes('前往') || allDescriptions.includes('导航') || allDescriptions.includes('打开')) {
      return 'navigation';
    }
    
    if (allDescriptions.includes('选择') || allDescriptions.includes('选项') || allDescriptions.includes('勾选')) {
      return 'selection';
    }
    
    if (allDescriptions.includes('输入') || allDescriptions.includes('填写') || allDescriptions.includes('编辑')) {
      return 'input';
    }
    
    return 'other';
  }
  
  /**
   * 为特定用户障碍生成最适合的简化配置
   * @param disabilityTypes 障碍类型数组
   * @returns 简化配置
   */
  public generateOptimalConfigForDisabilities(disabilityTypes: string[]): SimplifiedModeConfig {
    try {
      let recommendedLevel = 1;
      let needsLargeTargets = false;
      let needsSimpleLanguage = false;
      let needsSimplifiedLayout = false;
      
      // 分析用户障碍特点
      for (const disability of disabilityTypes) {
        switch (disability.toLowerCase()) {
          case 'motorimpairment':
          case 'parkinsons':
          case 'tremor':
            recommendedLevel = Math.max(recommendedLevel, 2);
            needsLargeTargets = true;
            break;
          case 'intellectualdisability':
          case 'learningdisability':
          case 'cognitiveimpairment':
          case 'dementia':
            recommendedLevel = Math.max(recommendedLevel, 2);
            needsSimpleLanguage = true;
            needsSimplifiedLayout = true;
            break;
          case 'severedisability':
          case 'multipleimpairments':
            recommendedLevel = 3;
            needsLargeTargets = true;
            needsSimpleLanguage = true;
            needsSimplifiedLayout = true;
            break;
          case 'elderly':
            needsLargeTargets = true;
            needsSimplifiedLayout = true;
            break;
        }
      }
      
      // 获取基础配置并应用特殊需求
      const baseConfig = this.getConfigForLevel(recommendedLevel);
      
      return {
        ...baseConfig,
        largeTargets: needsLargeTargets || baseConfig.largeTargets,
        useSimpleLanguage: needsSimpleLanguage || baseConfig.useSimpleLanguage,
        simplifiedLayout: needsSimplifiedLayout || baseConfig.simplifiedLayout
      };
    } catch (error) {
      logger.error('为障碍类型生成最佳配置失败', { error, disabilityTypes });
      return this.getConfigForLevel(1); // 出错时返回基础配置
    }
  }
  
  /**
   * 生成简化的手势替代操作
   * @param gestureType 原始手势类型
   * @returns 简化的替代操作描述
   */
  public getSimplifiedGestureAlternative(gestureType: string): string {
    switch (gestureType) {
      case 'pinchZoom':
        return '使用放大/缩小按钮代替捏合手势';
      case 'rotate':
        return '使用旋转按钮代替旋转手势';
      case 'multiFingerSwipe':
        return '使用切换按钮代替多指滑动';
      case 'shake':
        return '使用撤销按钮代替摇晃操作';
      case 'tilt':
        return '使用方向按钮代替倾斜操作';
      default:
        return `使用按钮代替${gestureType}手势`;
    }
  }
  
  /**
   * 简化复杂表单填写过程
   * @param formFields 表单字段数组
   * @returns 简化的表单交互说明
   */
  public simplifyFormInteraction(formFields: string[]): string[] {
    const level = this.simplificationConfig.level;
    
    if (level === 1) {
      // 轻度简化：保留所有字段，但提供更清晰的说明
      return formFields.map(field => `填写${field}`);
    } else if (level === 2) {
      // 中度简化：分组非必填字段
      const necessaryFields = formFields.slice(0, Math.min(formFields.length, 3));
      const remainingCount = formFields.length - necessaryFields.length;
      
      const result = necessaryFields.map(field => `填写${field}`);
      if (remainingCount > 0) {
        result.push(`点击"更多选项"填写其他${remainingCount}个可选项`);
      }
      
      return result;
    } else {
      // 高度简化：仅保留最关键的字段，其他用预设值
      const criticalField = formFields[0];
      return [
        `填写${criticalField}`,
        '点击"使用常用信息"自动填充其他字段',
        '点击"完成"提交表单'
      ];
    }
  }
  
  /**
   * 检测是否需要动作辅助
   * 分析操作复杂度，决定是否需要提供简化
   * @param actionSequence 操作序列
   * @returns 是否需要简化
   */
  public needsAssistance(actionSequence: AccessibilityAction[]): boolean {
    if (this.simplificationConfig.level === 3) {
      // 高级简化模式下始终提供辅助
      return true;
    }
    
    if (actionSequence.length <= 1) {
      // 单步操作通常不需要简化
      return false;
    }
    
    // 检查是否包含复杂手势
    const hasComplexGestures = actionSequence.some(action => 
      ['swipe', 'longPress', 'voice'].includes(action.type)
    );
    
    // 检查操作数量
    const tooManySteps = actionSequence.length > 3;
    
    return hasComplexGestures || tooManySteps;
  }
}

export default new SimplifiedActionsService();