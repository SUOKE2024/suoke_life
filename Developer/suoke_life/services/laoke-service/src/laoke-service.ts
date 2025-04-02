/**
 * 老克服务主入口
 * 老克是索克生活APP探索频道版主，负责知识传播、知识培训、用户博客管理工作
 * 兼任索克游戏NPC，提供无障碍功能和语音引导服务
 */

import { logger } from './utils/logger';
import accessibilityService from './accessibility/accessibility-service';
import knowledgeDisseminationService from './knowledge/knowledge-dissemination';
import knowledgeTrainingService from './knowledge/knowledge-training';
import blogManagement from './blog/blog-management';
import blogInteraction from './blog/blog-interaction';
import gameNPCService from './game/game-npc';

class LaoKeService {
  private initialized: boolean = false;
  
  /**
   * 构造函数
   */
  constructor() {
    logger.info('老克服务创建');
  }
  
  /**
   * 初始化服务
   */
  public async initialize(): Promise<void> {
    if (this.initialized) {
      logger.warn('老克服务已经初始化，跳过重复初始化');
      return;
    }
    
    logger.info('开始初始化老克服务');
    
    try {
      // 初始化内部服务
      await this.initializeSubServices();
      
      // 设置服务间依赖关系
      await this.setupDependencies();
      
      // 加载初始数据
      await this.loadInitialData();
      
      this.initialized = true;
      logger.info('老克服务初始化完成');
    } catch (error) {
      logger.error('老克服务初始化失败', {
        error: error instanceof Error ? error.message : String(error)
      });
      throw error;
    }
  }
  
  /**
   * 初始化子服务
   */
  private async initializeSubServices(): Promise<void> {
    logger.info('初始化老克子服务');
    
    // 这里的子服务都是单例模式，已经在import时初始化
    // 如果有需要特殊初始化的子服务，可以在这里添加
  }
  
  /**
   * 设置服务间依赖关系
   */
  private async setupDependencies(): Promise<void> {
    logger.info('设置老克服务依赖关系');
    
    // 这里设置各服务间的依赖关系
    // 例如，博客管理服务可能需要知识培训服务的数据
  }
  
  /**
   * 加载初始数据
   */
  private async loadInitialData(): Promise<void> {
    logger.info('加载老克服务初始数据');
    
    // 加载各种初始数据
    // 例如，预设的博客模板、知识库内容等
  }
  
  /**
   * 启动服务
   */
  public async start(): Promise<void> {
    if (!this.initialized) {
      await this.initialize();
    }
    
    logger.info('老克服务启动中');
    
    // 这里可以添加服务启动时需要执行的逻辑
    // 例如，开始定时任务、启动监听器等
    
    logger.info('老克服务启动完成');
  }
  
  /**
   * 关闭服务
   */
  public async shutdown(): Promise<void> {
    if (!this.initialized) {
      logger.warn('老克服务未初始化，无需关闭');
      return;
    }
    
    logger.info('老克服务关闭中');
    
    // 这里添加服务关闭时需要执行的逻辑
    // 例如，停止定时任务、关闭连接等
    
    this.initialized = false;
    logger.info('老克服务已关闭');
  }
  
  /**
   * 获取无障碍服务
   */
  public getAccessibilityService() {
    return accessibilityService;
  }
  
  /**
   * 获取知识传播服务
   */
  public getKnowledgeDisseminationService() {
    return knowledgeDisseminationService;
  }
  
  /**
   * 获取知识培训服务
   */
  public getKnowledgeTrainingService() {
    return knowledgeTrainingService;
  }
  
  /**
   * 获取博客管理服务
   */
  public getBlogManagementService() {
    return blogManagement;
  }
  
  /**
   * 获取博客互动服务
   */
  public getBlogInteractionService() {
    return blogInteraction;
  }
  
  /**
   * 获取游戏NPC服务
   */
  public getGameNPCService() {
    return gameNPCService;
  }
  
  /**
   * 获取服务状态
   */
  public getServiceStatus(): {
    initialized: boolean;
    status: 'starting' | 'running' | 'stopping' | 'stopped';
    uptime?: number;
    startTime?: Date;
  } {
    if (!this.initialized) {
      return {
        initialized: false,
        status: 'stopped'
      };
    }
    
    // 这里可以添加更多服务状态信息
    return {
      initialized: true,
      status: 'running',
      startTime: new Date(), // 实际应该记录真实的启动时间
      uptime: 0 // 实际应该计算真实的运行时间
    };
  }
}

// 创建单例实例
const laokeService = new LaoKeService();

export default laokeService;