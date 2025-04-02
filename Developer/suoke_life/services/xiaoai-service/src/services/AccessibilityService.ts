import { IUser } from '../models/User';
import { logger } from '../index';

/**
 * 无障碍功能服务 - 负责提供无障碍支持功能
 */
export class AccessibilityService {
  /**
   * 检查用户是否需要无障碍功能支持
   */
  public checkUserNeedsAssistance(user: IUser): boolean {
    return (
      user.accessibilityNeeds.visuallyImpaired ||
      user.accessibilityNeeds.hearingImpaired ||
      user.accessibilityNeeds.mobilityImpaired ||
      user.accessibilityNeeds.cognitiveImpaired ||
      user.accessibilityNeeds.needsVoiceGuidance
    );
  }
  
  /**
   * 自动检测用户可能的无障碍需求
   * 基于用户交互模式和历史记录推断可能的无障碍需求
   */
  public async detectPotentialAccessibilityNeeds(
    userId: string,
    interactionHistory: any[]
  ): Promise<Partial<IUser['accessibilityNeeds']>> {
    try {
      const potentialNeeds: Partial<IUser['accessibilityNeeds']> = {};
      
      // 分析交互历史中的模式
      const voiceInteractions = interactionHistory.filter(
        (interaction) => interaction.messageType === 'voice'
      ).length;
      
      const totalInteractions = interactionHistory.length;
      
      // 如果用户主要使用语音交互，可能需要视觉辅助
      if (totalInteractions > 5 && voiceInteractions / totalInteractions > 0.7) {
        potentialNeeds.needsVoiceGuidance = true;
        potentialNeeds.visuallyImpaired = true;
      }
      
      // 检测是否有直接请求无障碍功能的消息
      const accessibilityRequests = interactionHistory.filter((interaction) =>
        typeof interaction.content === 'string' &&
        (
          interaction.content.includes('无法看清') ||
          interaction.content.includes('看不见') ||
          interaction.content.includes('听不清') ||
          interaction.content.includes('语音引导') ||
          interaction.content.includes('盲人') ||
          interaction.content.includes('视障') ||
          interaction.content.includes('听障') ||
          interaction.content.includes('残障') ||
          interaction.content.includes('辅助功能') ||
          interaction.content.includes('无障碍')
        )
      );
      
      if (accessibilityRequests.length > 0) {
        // 分析具体请求内容
        for (const request of accessibilityRequests) {
          const content = request.content.toLowerCase();
          
          if (
            content.includes('看不见') ||
            content.includes('无法看清') ||
            content.includes('视障') ||
            content.includes('盲人')
          ) {
            potentialNeeds.visuallyImpaired = true;
            potentialNeeds.needsVoiceGuidance = true;
          }
          
          if (
            content.includes('听不清') ||
            content.includes('听障') ||
            content.includes('听力')
          ) {
            potentialNeeds.hearingImpaired = true;
          }
          
          if (content.includes('大字') || content.includes('字体大小')) {
            potentialNeeds.largeTextMode = true;
          }
          
          if (content.includes('对比度') || content.includes('看不清颜色')) {
            potentialNeeds.highContrastMode = true;
          }
        }
      }
      
      logger.info(`为用户${userId}检测到的潜在无障碍需求:`, potentialNeeds);
      return potentialNeeds;
    } catch (error) {
      logger.error('检测潜在无障碍需求失败:', error);
      return {};
    }
  }
  
  /**
   * 为用户提供无障碍访问提示
   */
  public generateAccessibilityTips(user: IUser): string[] {
    const tips: string[] = [];
    
    // 为视障用户提供提示
    if (user.accessibilityNeeds.visuallyImpaired) {
      tips.push(
        '您可以随时说"小艾，请开启语音引导"来启用详细的语音描述。',
        '您可以通过说"放大文字"或"缩小文字"来调整文字大小。',
        '通过说"增加对比度"可以切换到高对比度模式，使文字更清晰。'
      );
    }
    
    // 为听障用户提供提示
    if (user.accessibilityNeeds.hearingImpaired) {
      tips.push(
        '所有语音内容都会自动显示文字记录。',
        '您可以通过说"打开字幕"启用更大的实时字幕。',
        '您可以通过文字输入与小艾进行沟通。'
      );
    }
    
    // 为行动不便的用户提供提示
    if (user.accessibilityNeeds.mobilityImpaired) {
      tips.push(
        '您可以使用语音命令控制大部分功能，无需触摸屏幕。',
        '说"小艾，显示语音命令"可以查看所有可用的语音指令。'
      );
    }
    
    // 通用提示
    if (this.checkUserNeedsAssistance(user)) {
      tips.push(
        '随时可以说"小艾，帮助"获取无障碍功能帮助。',
        '说"小艾，调整无障碍设置"可以随时修改您的无障碍偏好。'
      );
    }
    
    return tips;
  }
  
  /**
   * 为特定内容生成无障碍增强版本
   */
  public enhanceContentForAccessibility(
    content: string,
    accessibilityNeeds: IUser['accessibilityNeeds']
  ): string {
    let enhancedContent = content;
    
    // 为视障用户增强内容
    if (accessibilityNeeds.visuallyImpaired) {
      // 增加更详细的文本描述
      enhancedContent = this.enhanceWithDetailedDescriptions(enhancedContent);
    }
    
    // 为认知障碍用户简化内容
    if (accessibilityNeeds.cognitiveImpaired) {
      // 简化复杂说明
      enhancedContent = this.simplifyContent(enhancedContent);
    }
    
    return enhancedContent;
  }
  
  /**
   * 增加详细描述
   */
  private enhanceWithDetailedDescriptions(content: string): string {
    // 识别内容中可能需要更详细描述的部分
    // 这里简化实现，实际中可能需要更复杂的NLP或模板系统
    
    // 替换简单描述为更详细的描述
    let enhancedContent = content;
    
    // 替换简单按钮描述
    enhancedContent = enhancedContent.replace(
      /点击([^按钮，。；]+)按钮/g,
      '点击屏幕下方的$1按钮，这是一个矩形按钮，位于屏幕底部'
    );
    
    // 增强导航说明
    enhancedContent = enhancedContent.replace(
      /进入([^页面，。；]+)页面/g,
      '进入$1页面，新页面将会完全替换当前屏幕内容'
    );
    
    return enhancedContent;
  }
  
  /**
   * 简化内容
   */
  private simplifyContent(content: string): string {
    // 将长段落分解为更短的句子
    let simplifiedContent = content.replace(/([。！？；])\s*/g, '$1\n');
    
    // 去除专业术语和复杂词汇（这里简化实现）
    const complexTerms = {
      '四诊合参': '综合诊断',
      '辨证论治': '针对性治疗',
      '寒热虚实': '身体状态',
      '气血津液': '身体能量和液体',
    };
    
    Object.entries(complexTerms).forEach(([complex, simple]) => {
      simplifiedContent = simplifiedContent.replace(new RegExp(complex, 'g'), simple);
    });
    
    return simplifiedContent;
  }
}