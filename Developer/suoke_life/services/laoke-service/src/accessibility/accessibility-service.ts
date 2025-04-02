/**
 * 无障碍服务
 * 负责文字转语音、语音引导等无障碍功能
 */
import { logger } from '../utils/logger';

/**
 * 语音选项
 */
interface VoiceOption {
  id: string;             // 语音ID
  name: string;           // 语音名称
  language: string;       // 语言
  gender: 'male' | 'female' | 'neutral'; // 性别
  ageGroup?: 'child' | 'young' | 'adult' | 'senior'; // 年龄组
  description?: string;   // 描述
  premium: boolean;       // 是否高级语音
  sampleRate: number;     // 采样率
}

/**
 * 语音参数
 */
interface VoiceParams {
  pitch?: number;        // 音调(0.5-2.0)
  rate?: number;         // 语速(0.5-2.0)
  volume?: number;       // 音量(0-1.0)
}

/**
 * 朗读项目
 */
interface ReadingItem {
  id: string;            // 项目ID
  text: string;          // 文本内容
  voiceId?: string;      // 语音ID
  params?: VoiceParams;  // 语音参数
  priority: number;      // 优先级(越小越高)
  timestamp: Date;       // 时间戳
  processed: boolean;    // 是否已处理
  audioData?: string;    // 音频数据(Base64)
}

/**
 * 无障碍偏好设置
 */
interface AccessibilityPreferences {
  userId: string;        // 用户ID
  textToSpeechEnabled: boolean; // 是否启用文字转语音
  screenReaderEnabled: boolean; // 是否启用屏幕阅读
  highContrastEnabled: boolean; // 是否启用高对比度
  fontScaleFactor: number;      // 字体缩放因子
  autoPlayAudio: boolean;       // 是否自动播放音频
  preferredVoiceId?: string;    // 首选语音ID
  voiceParams?: VoiceParams;    // 语音参数
  createdAt: Date;              // 创建时间
  updatedAt: Date;              // 更新时间
}

/**
 * 朗读事件
 */
interface ReadingEvent {
  id: string;            // 事件ID
  userId: string;        // 用户ID
  text: string;          // 文本内容
  source: string;        // 来源
  timestamp: Date;       // 时间戳
  duration?: number;     // 持续时间(毫秒)
  completed: boolean;    // 是否完成
}

class AccessibilityService {
  // 可用语音列表
  private voices: VoiceOption[] = [];
  
  // 朗读队列
  private readingQueue: ReadingItem[] = [];
  
  // 用户偏好设置
  private userPreferences: Map<string, AccessibilityPreferences> = new Map();
  
  // 朗读历史
  private readingHistory: ReadingEvent[] = [];
  
  // 是否正在朗读
  private isReading: boolean = false;
  
  /**
   * 构造函数
   */
  constructor() {
    logger.info('无障碍服务初始化');
    
    // 初始化默认语音
    this.initDefaultVoices();
  }
  
  /**
   * 初始化默认语音
   */
  private initDefaultVoices(): void {
    this.voices = [
      {
        id: 'zh-CN-XiaoxiaoNeural',
        name: '晓晓',
        language: 'zh-CN',
        gender: 'female',
        ageGroup: 'young',
        description: '温柔的女声，适合一般内容朗读',
        premium: false,
        sampleRate: 24000
      },
      {
        id: 'zh-CN-YunxiNeural',
        name: '云溪',
        language: 'zh-CN',
        gender: 'male',
        ageGroup: 'adult',
        description: '稳重的男声，适合知识讲解',
        premium: false,
        sampleRate: 24000
      },
      {
        id: 'zh-CN-YunyangNeural',
        name: '云扬',
        language: 'zh-CN',
        gender: 'male',
        ageGroup: 'adult',
        description: '正式的男声，适合官方内容',
        premium: false,
        sampleRate: 24000
      },
      {
        id: 'zh-CN-XiaohanNeural',
        name: '小涵',
        language: 'zh-CN',
        gender: 'female',
        ageGroup: 'young',
        description: '活泼的女声，适合轻松内容',
        premium: true,
        sampleRate: 48000
      },
      {
        id: 'zh-CN-XiaomoNeural',
        name: '小墨',
        language: 'zh-CN',
        gender: 'female',
        ageGroup: 'adult',
        description: '专业的女声，适合医疗健康内容',
        premium: true,
        sampleRate: 48000
      },
      {
        id: 'zh-CN-XiaoxuanNeural',
        name: '小暄',
        language: 'zh-CN',
        gender: 'female',
        ageGroup: 'child',
        description: '童声，适合儿童内容',
        premium: true,
        sampleRate: 48000
      }
    ];
    
    logger.info(`初始化默认语音，共${this.voices.length}个`);
  }
  
  /**
   * 获取可用语音
   * @returns 语音选项列表
   */
  public async getAvailableVoices(): Promise<VoiceOption[]> {
    logger.info(`获取可用语音列表，共${this.voices.length}个`);
    return this.voices;
  }
  
  /**
   * 文字转语音
   * @param text 文本内容
   * @param voiceId 语音ID
   * @param params 语音参数
   * @returns 音频数据(Base64)
   */
  public async textToSpeech(
    text: string,
    voiceId?: string,
    params?: VoiceParams
  ): Promise<string> {
    logger.info(`文字转语音`, {
      textLength: text.length,
      voiceId,
      params
    });
    
    // 如果没有指定语音，使用默认语音
    const actualVoiceId = voiceId || 'zh-CN-XiaoxiaoNeural';
    
    // 检查语音是否存在
    const voice = this.voices.find(v => v.id === actualVoiceId);
    if (!voice) {
      logger.warn(`语音不存在: ${actualVoiceId}，将使用默认语音`);
    }
    
    // 实际应用中，这里应该调用文字转语音API或本地引擎
    // 由于是示例，这里模拟生成Base64音频数据
    // 正式实现应该整合讯飞、百度等语音合成服务
    
    // 模拟处理延迟
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // 生成模拟的Base64音频数据
    const audioData = `data:audio/mp3;base64,${Buffer.from(`TTS_${Date.now()}_${actualVoiceId}_${text.substring(0, 20)}`).toString('base64')}`;
    
    logger.info(`文字转语音完成`, {
      voiceId: actualVoiceId,
      audioDataLength: audioData.length
    });
    
    return audioData;
  }
  
  /**
   * 添加文本到朗读队列
   * @param text 文本内容
   * @param userId 用户ID
   * @param voiceId 语音ID
   * @param params 语音参数
   * @param priority 优先级
   * @returns 朗读项目ID
   */
  public async addToReadingQueue(
    text: string,
    userId: string,
    voiceId?: string,
    params?: VoiceParams,
    priority: number = 10
  ): Promise<string> {
    // 生成唯一ID
    const id = `reading-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
    
    // 获取用户偏好
    const userPrefs = this.getUserPreferences(userId);
    
    // 如果用户没有指定语音ID，使用用户偏好或默认语音
    const actualVoiceId = voiceId || userPrefs.preferredVoiceId || 'zh-CN-XiaoxiaoNeural';
    
    // 合并语音参数
    const actualParams: VoiceParams = {
      ...(userPrefs.voiceParams || {}),
      ...(params || {})
    };
    
    // 创建朗读项目
    const readingItem: ReadingItem = {
      id,
      text,
      voiceId: actualVoiceId,
      params: actualParams,
      priority,
      timestamp: new Date(),
      processed: false
    };
    
    // 添加到队列
    this.readingQueue.push(readingItem);
    
    // 按优先级排序队列
    this.readingQueue.sort((a, b) => a.priority - b.priority);
    
    logger.info(`添加文本到朗读队列`, {
      id,
      textLength: text.length,
      priority,
      userId
    });
    
    // 如果当前没有朗读任务，启动朗读处理
    if (!this.isReading) {
      this.processReadingQueue();
    }
    
    return id;
  }
  
  /**
   * 处理朗读队列
   */
  private async processReadingQueue(): Promise<void> {
    // 如果队列为空或已经在处理，直接返回
    if (this.readingQueue.length === 0 || this.isReading) {
      return;
    }
    
    this.isReading = true;
    
    try {
      // 获取下一个朗读项目
      const item = this.readingQueue[0];
      
      // 更新状态
      item.processed = true;
      
      // 转换为语音
      const audioData = await this.textToSpeech(
        item.text,
        item.voiceId,
        item.params
      );
      
      // 保存语音数据
      item.audioData = audioData;
      
      // 记录朗读事件
      this.recordReadingEvent(item);
      
      // 移除已处理项目
      this.readingQueue.shift();
      
      logger.info(`朗读项目处理完成`, {
        id: item.id,
        textLength: item.text.length
      });
    } catch (error) {
      logger.error(`朗读项目处理失败`, {
        error: error instanceof Error ? error.message : String(error),
        queueLength: this.readingQueue.length
      });
      
      // 移除出错的项目
      this.readingQueue.shift();
    } finally {
      this.isReading = false;
      
      // 如果队列中还有项目，继续处理
      if (this.readingQueue.length > 0) {
        this.processReadingQueue();
      }
    }
  }
  
  /**
   * 记录朗读事件
   * @param item 朗读项目
   */
  private recordReadingEvent(item: ReadingItem): void {
    // 估算朗读时长(简化计算：假设每分钟300字)
    const wordsPerMinute = 300;
    const textLength = item.text.length;
    const durationMinutes = textLength / wordsPerMinute;
    const durationMs = Math.round(durationMinutes * 60 * 1000);
    
    // 创建朗读事件
    const readingEvent: ReadingEvent = {
      id: `event-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
      userId: 'unknown', // 这里简化处理，实际应从item中获取
      text: item.text,
      source: 'tts-queue',
      timestamp: new Date(),
      duration: durationMs,
      completed: true
    };
    
    // 添加到历史记录
    this.readingHistory.push(readingEvent);
    
    // 如果历史记录过长，清理旧记录
    if (this.readingHistory.length > 1000) {
      this.readingHistory = this.readingHistory.slice(-1000);
    }
    
    logger.info(`记录朗读事件`, {
      eventId: readingEvent.id,
      textLength,
      durationMs
    });
  }
  
  /**
   * 获取朗读项目
   * @param id 朗读项目ID
   * @returns 朗读项目或null
   */
  public getReadingItem(id: string): ReadingItem | null {
    // 在队列中查找
    const queueItem = this.readingQueue.find(item => item.id === id);
    if (queueItem) {
      return queueItem;
    }
    
    // 在已处理的项目中查找(这里简化实现，实际应该持久化存储)
    return null;
  }
  
  /**
   * 取消朗读
   * @param id 朗读项目ID
   * @returns 是否取消成功
   */
  public cancelReading(id: string): boolean {
    const index = this.readingQueue.findIndex(item => item.id === id);
    if (index === -1) {
      logger.warn(`取消朗读失败，项目不存在或已处理: ${id}`);
      return false;
    }
    
    // 移除项目
    this.readingQueue.splice(index, 1);
    
    logger.info(`取消朗读成功`, { id });
    
    return true;
  }
  
  /**
   * 获取用户无障碍偏好设置
   * @param userId 用户ID
   * @returns 偏好设置
   */
  public getUserPreferences(userId: string): AccessibilityPreferences {
    // 如果用户没有设置，创建默认设置
    if (!this.userPreferences.has(userId)) {
      const now = new Date();
      const defaultPrefs: AccessibilityPreferences = {
        userId,
        textToSpeechEnabled: false,
        screenReaderEnabled: false,
        highContrastEnabled: false,
        fontScaleFactor: 1.0,
        autoPlayAudio: false,
        createdAt: now,
        updatedAt: now
      };
      
      this.userPreferences.set(userId, defaultPrefs);
      
      logger.info(`创建用户默认无障碍偏好设置`, { userId });
    }
    
    return this.userPreferences.get(userId)!;
  }
  
  /**
   * 更新用户无障碍偏好设置
   * @param userId 用户ID
   * @param prefs 偏好设置
   * @returns 是否更新成功
   */
  public updateUserPreferences(
    userId: string,
    prefs: Partial<Omit<AccessibilityPreferences, 'userId' | 'createdAt' | 'updatedAt'>>
  ): boolean {
    // 获取当前设置
    const currentPrefs = this.getUserPreferences(userId);
    
    // 更新设置
    const updatedPrefs: AccessibilityPreferences = {
      ...currentPrefs,
      ...prefs,
      updatedAt: new Date()
    };
    
    // 保存更新后的设置
    this.userPreferences.set(userId, updatedPrefs);
    
    logger.info(`更新用户无障碍偏好设置`, {
      userId,
      textToSpeechEnabled: updatedPrefs.textToSpeechEnabled,
      screenReaderEnabled: updatedPrefs.screenReaderEnabled
    });
    
    return true;
  }
  
  /**
   * 生成语音引导
   * @param userId 用户ID
   * @param context 上下文信息
   * @param text 文本内容
   * @returns 引导ID
   */
  public async generateVoiceGuidance(
    userId: string,
    context: {
      screen: string;
      action?: string;
      element?: string;
    },
    text?: string
  ): Promise<string> {
    // 获取用户偏好
    const userPrefs = this.getUserPreferences(userId);
    
    // 如果用户未启用语音引导，直接返回
    if (!userPrefs.textToSpeechEnabled && !userPrefs.screenReaderEnabled) {
      logger.info(`用户未启用语音引导，跳过`, { userId });
      return 'skipped';
    }
    
    // 如果没有提供文本，根据上下文生成引导文本
    const guidanceText = text || this.generateGuidanceText(context);
    
    // 添加到朗读队列，优先级高
    const readingId = await this.addToReadingQueue(
      guidanceText,
      userId,
      userPrefs.preferredVoiceId,
      userPrefs.voiceParams,
      5 // 高优先级
    );
    
    logger.info(`生成语音引导`, {
      userId,
      screen: context.screen,
      textLength: guidanceText.length,
      readingId
    });
    
    return readingId;
  }
  
  /**
   * 根据上下文生成引导文本
   * @param context 上下文信息
   * @returns 引导文本
   */
  private generateGuidanceText(
    context: {
      screen: string;
      action?: string;
      element?: string;
    }
  ): string {
    const { screen, action, element } = context;
    
    // 根据屏幕生成基本引导
    let guidance = `当前页面：${screen}。`;
    
    // 添加元素信息
    if (element) {
      guidance += `焦点位于：${element}。`;
    }
    
    // 添加动作提示
    if (action) {
      guidance += `您可以${action}。`;
    }
    
    // 根据不同屏幕添加特定指引
    switch (screen) {
      case '首页':
        guidance += '在此页面您可以浏览推荐内容，或使用底部导航切换到其他功能区。';
        break;
      case '探索':
        guidance += '在此页面您可以搜索知识内容，浏览分类文章，发现更多健康养生资讯。';
        break;
      case '个人中心':
        guidance += '在此页面您可以查看个人信息，管理偏好设置，查看历史记录等。';
        break;
      case '阅读文章':
        guidance += '系统将为您朗读文章内容，您可以随时暂停或调整朗读速度。';
        break;
    }
    
    return guidance;
  }
  
  /**
   * 特殊需求用户朗读辅助
   * @param userId 用户ID
   * @param content 内容数据
   * @returns 音频数据
   */
  public async specialNeedsReading(
    userId: string,
    content: {
      title: string;
      sections: { heading?: string; text: string }[];
      priority?: 'high' | 'normal' | 'low';
    }
  ): Promise<{
    readingId: string;
    estimatedDuration: number;
  }> {
    logger.info(`特殊需求用户朗读辅助`, {
      userId,
      title: content.title,
      sectionsCount: content.sections.length
    });
    
    // 获取用户偏好
    const userPrefs = this.getUserPreferences(userId);
    
    // 合并所有文本
    let fullText = `${content.title}。`;
    
    content.sections.forEach(section => {
      if (section.heading) {
        fullText += `${section.heading}。`;
      }
      fullText += `${section.text} `;
    });
    
    // 确定优先级
    const priorityMap = {
      high: 1,
      normal: 5,
      low: 10
    };
    const priority = priorityMap[content.priority || 'normal'];
    
    // 添加到朗读队列
    const readingId = await this.addToReadingQueue(
      fullText,
      userId,
      userPrefs.preferredVoiceId,
      userPrefs.voiceParams,
      priority
    );
    
    // 估算时长
    const wordsPerMinute = 300;
    const textLength = fullText.length;
    const durationMinutes = textLength / wordsPerMinute;
    const durationMs = Math.round(durationMinutes * 60 * 1000);
    
    return {
      readingId,
      estimatedDuration: durationMs
    };
  }
  
  /**
   * 获取用户朗读历史
   * @param userId 用户ID
   * @param limit 数量限制
   * @returns 朗读历史
   */
  public getUserReadingHistory(
    userId: string,
    limit: number = 50
  ): ReadingEvent[] {
    const userHistory = this.readingHistory
      .filter(event => event.userId === userId)
      .sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
      .slice(0, limit);
    
    logger.info(`获取用户朗读历史`, {
      userId,
      limit,
      count: userHistory.length
    });
    
    return userHistory;
  }
}

// 导出单例实例
const accessibilityService = new AccessibilityService();
export default accessibilityService;