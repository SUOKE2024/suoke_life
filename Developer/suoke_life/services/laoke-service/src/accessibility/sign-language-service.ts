/**
 * 手语支持服务
 * 为听障用户提供手语翻译功能
 */
import { SignLanguageConfig } from '../types/accessibility';
import { logger } from '../utils/logger';

class SignLanguageService {
  private config: SignLanguageConfig = {
    enabled: true,
    type: 'csl', // 默认使用中国手语
    scale: 1.0,
    position: 'bottom-right',
    speed: 1.0
  };
  
  // 常用短语映射
  private commonPhrases: Map<string, string> = new Map();
  // 是否正在显示
  private isDisplaying: boolean = false;
  // 当前翻译ID
  private currentTranslationId: string | null = null;
  
  /**
   * 构造函数
   */
  constructor() {
    logger.info('手语支持服务初始化');
    this.initCommonPhrases();
  }
  
  /**
   * 初始化常用短语映射
   */
  private initCommonPhrases(): void {
    // 添加一些常用短语的手语视频ID映射
    this.commonPhrases.set('你好', 'sl_hello');
    this.commonPhrases.set('谢谢', 'sl_thanks');
    this.commonPhrases.set('请', 'sl_please');
    this.commonPhrases.set('是', 'sl_yes');
    this.commonPhrases.set('不', 'sl_no');
    this.commonPhrases.set('帮助', 'sl_help');
    this.commonPhrases.set('我', 'sl_i');
    this.commonPhrases.set('你', 'sl_you');
    this.commonPhrases.set('好的', 'sl_ok');
    this.commonPhrases.set('对不起', 'sl_sorry');
  }
  
  /**
   * 配置手语服务
   * @param config 手语服务配置
   */
  public configure(config: Partial<SignLanguageConfig>): void {
    this.config = {
      ...this.config,
      ...config
    };
    logger.info('手语服务配置已更新', this.config);
  }
  
  /**
   * 翻译文本为手语
   * @param text 待翻译文本
   * @param immediate 是否立即显示
   * @returns 翻译ID
   */
  public translateText(text: string, immediate: boolean = true): string {
    if (!this.config.enabled) {
      logger.info('手语服务未启用，忽略翻译请求');
      return '';
    }
    
    const translationId = `sl-${Date.now()}`;
    logger.info(`翻译文本为手语: ${text}`, { translationId, immediate });
    
    // 如果指定立即显示，则显示翻译
    if (immediate) {
      this.showTranslation(translationId, text);
    }
    
    return translationId;
  }
  
  /**
   * 显示翻译
   * @param translationId 翻译ID
   * @param text 文本内容
   * @returns 是否成功显示
   */
  public showTranslation(translationId: string, text: string): boolean {
    if (!this.config.enabled) {
      return false;
    }
    
    // 如果已经在显示，先停止当前显示
    if (this.isDisplaying && this.currentTranslationId) {
      this.stopTranslation(this.currentTranslationId);
    }
    
    this.isDisplaying = true;
    this.currentTranslationId = translationId;
    
    logger.info(`显示手语翻译: ${text}`, { translationId });
    
    // 实际显示逻辑将在客户端实现
    // 这里假设短语匹配和手语生成会在客户端进行
    
    return true;
  }
  
  /**
   * 停止翻译显示
   * @param translationId 翻译ID，如果为空则停止当前翻译
   * @returns 是否成功停止
   */
  public stopTranslation(translationId?: string): boolean {
    if (translationId && translationId !== this.currentTranslationId) {
      logger.info(`尝试停止非当前翻译: ${translationId}`);
      return false;
    }
    
    logger.info(`停止手语翻译: ${this.currentTranslationId}`);
    
    this.isDisplaying = false;
    this.currentTranslationId = null;
    
    // 实际停止逻辑将在客户端实现
    
    return true;
  }
  
  /**
   * 获取常用短语手语视频ID
   * @param phrase 短语
   * @returns 视频ID或null
   */
  public getCommonPhraseVideoId(phrase: string): string | null {
    return this.commonPhrases.get(phrase) || null;
  }
  
  /**
   * 添加常用短语映射
   * @param phrase 短语
   * @param videoId 视频ID
   */
  public addCommonPhrase(phrase: string, videoId: string): void {
    this.commonPhrases.set(phrase, videoId);
    logger.info(`添加常用短语映射: ${phrase} -> ${videoId}`);
  }
  
  /**
   * 翻译并显示通知
   * @param notification 通知内容
   * @param type 通知类型
   * @param duration 显示时长(毫秒)
   * @returns 翻译ID
   */
  public translateNotification(
    notification: string,
    type: 'info' | 'warning' | 'error' | 'success' = 'info',
    duration: number = 5000
  ): string {
    if (!this.config.enabled) {
      return '';
    }
    
    // 根据类型添加前缀
    const prefixMap: Record<string, string> = {
      info: '信息：',
      warning: '警告：',
      error: '错误：',
      success: '成功：'
    };
    
    const translationId = this.translateText(`${prefixMap[type]}${notification}`);
    
    // 设置自动隐藏
    setTimeout(() => {
      if (this.currentTranslationId === translationId) {
        this.stopTranslation(translationId);
      }
    }, duration);
    
    return translationId;
  }
  
  /**
   * 获取手语字典条目
   * @param word 单词或短语
   * @returns 手语字典条目或null
   */
  public getSignDictionaryEntry(word: string): Promise<SignDictionaryEntry | null> {
    logger.info(`获取手语字典条目: ${word}`);
    
    return new Promise((resolve) => {
      // 这里应该连接到手语字典服务
      // 目前使用模拟数据作为示例
      const mockEntry: SignDictionaryEntry = {
        word,
        signType: this.config.type,
        videoId: this.getCommonPhraseVideoId(word) || `sl_generated_${Date.now()}`,
        description: `"${word}"的${this.config.type === 'csl' ? '中国' : '美国'}手语表达`,
        difficulty: 'medium',
        relatedSigns: []
      };
      
      resolve(mockEntry);
    });
  }
  
  /**
   * 获取可用的手语类型
   * @returns 手语类型列表
   */
  public getAvailableSignTypes(): string[] {
    return ['csl', 'asl'];
  }
  
  /**
   * 获取手语学习资源
   * @param level 学习级别
   * @returns 学习资源列表
   */
  public getLearningResources(level: 'beginner' | 'intermediate' | 'advanced'): Promise<LearningResource[]> {
    logger.info(`获取手语学习资源: ${level}`);
    
    return new Promise((resolve) => {
      // 这里应该连接到学习资源服务
      // 目前使用模拟数据作为示例
      const mockResources: LearningResource[] = [
        {
          id: 'sl_lesson_1',
          title: '基础手语入门',
          type: 'video',
          level: 'beginner',
          duration: 600, // 10分钟
          url: 'https://example.com/sign-language/basics'
        },
        {
          id: 'sl_lesson_2',
          title: '常用手语词汇',
          type: 'interactive',
          level: 'beginner',
          duration: 900, // 15分钟
          url: 'https://example.com/sign-language/vocabulary'
        }
      ];
      
      resolve(mockResources.filter(r => r.level === level));
    });
  }
}

/**
 * 手语字典条目接口
 */
interface SignDictionaryEntry {
  word: string;
  signType: string;
  videoId: string;
  description: string;
  difficulty: 'easy' | 'medium' | 'hard';
  relatedSigns: string[];
}

/**
 * 学习资源接口
 */
interface LearningResource {
  id: string;
  title: string;
  type: 'video' | 'interactive' | 'document';
  level: 'beginner' | 'intermediate' | 'advanced';
  duration: number; // 秒
  url: string;
}

export default new SignLanguageService();