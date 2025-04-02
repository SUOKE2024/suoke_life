/**
 * 导航辅助服务
 * 提供无障碍导航支持
 */
import { NavigationAssistanceConfig } from '../types/accessibility';
import { logger } from '../utils/logger';
import visualImpairedService from './visual-impaired-service';

class NavigationAssistance {
  private config: NavigationAssistanceConfig = {
    enabled: true,
    promptMode: 'both',
    autoFocus: true,
    pageOverview: true,
    quickNavigation: true,
    navigationPattern: 'grouped'
  };
  
  // 导航历史
  private navigationHistory: string[] = [];
  // 当前页面元素映射
  private currentPageElements: Map<string, ElementInfo> = new Map();
  // 当前聚焦元素ID
  private currentFocusId: string | null = null;
  
  /**
   * 构造函数
   */
  constructor() {
    logger.info('导航辅助服务初始化');
  }
  
  /**
   * 配置导航辅助
   * @param config 导航辅助配置
   */
  public configure(config: Partial<NavigationAssistanceConfig>): void {
    this.config = {
      ...this.config,
      ...config
    };
    logger.info('导航辅助配置已更新', this.config);
  }
  
  /**
   * 页面加载时调用
   * @param pageId 页面ID
   * @param pageTitle 页面标题
   * @param elementsMap 页面元素映射
   */
  public onPageLoaded(
    pageId: string,
    pageTitle: string,
    elementsMap: Record<string, ElementInfo>
  ): void {
    if (!this.config.enabled) {
      logger.info('导航辅助未启用，忽略页面加载通知');
      return;
    }
    
    logger.info(`页面加载: ${pageTitle}`, { pageId });
    
    // 更新导航历史
    this.navigationHistory.push(pageId);
    if (this.navigationHistory.length > 10) {
      this.navigationHistory.shift();
    }
    
    // 更新当前页面元素映射
    this.currentPageElements.clear();
    Object.entries(elementsMap).forEach(([id, info]) => {
      this.currentPageElements.set(id, info);
    });
    
    // 重置当前聚焦
    this.currentFocusId = null;
    
    // 如果启用了页面概览，提供页面导航信息
    if (this.config.pageOverview) {
      this.providePageOverview(pageId, pageTitle);
    }
    
    // 如果启用了自动聚焦，聚焦到第一个可交互元素
    if (this.config.autoFocus) {
      this.focusFirstInteractiveElement();
    }
  }
  
  /**
   * 提供页面概览
   * @param pageId 页面ID
   * @param pageTitle 页面标题
   */
  private providePageOverview(pageId: string, pageTitle: string): void {
    // 计算页面统计信息
    const elementCount = this.currentPageElements.size;
    const interactiveCount = Array.from(this.currentPageElements.values())
      .filter(e => e.interactive).length;
    
    // 构建页面概览文本
    const overviewText = `页面：${pageTitle}。包含 ${elementCount} 个元素，其中 ${interactiveCount} 个可交互元素。使用导航命令浏览页面。`;
    
    // 根据提示模式提供概览
    if (this.config.promptMode === 'voice' || this.config.promptMode === 'both') {
      visualImpairedService.speak(overviewText);
    }
    
    if (this.config.promptMode === 'visual' || this.config.promptMode === 'both') {
      // 视觉提示在客户端实现
      logger.info(`提供视觉页面概览: ${pageTitle}`);
    }
  }
  
  /**
   * 聚焦到第一个可交互元素
   */
  private focusFirstInteractiveElement(): void {
    // 查找第一个可交互元素
    const firstInteractive = Array.from(this.currentPageElements.entries())
      .find(([_, info]) => info.interactive);
    
    if (firstInteractive) {
      const [id, info] = firstInteractive;
      this.focusElement(id);
    }
  }
  
  /**
   * 聚焦特定元素
   * @param elementId 元素ID
   * @returns 是否成功聚焦
   */
  public focusElement(elementId: string): boolean {
    if (!this.config.enabled || !this.currentPageElements.has(elementId)) {
      return false;
    }
    
    const elementInfo = this.currentPageElements.get(elementId)!;
    logger.info(`聚焦元素: ${elementId}`, elementInfo);
    
    // 更新当前聚焦
    this.currentFocusId = elementId;
    
    // 根据提示模式提供元素描述
    if (this.config.promptMode === 'voice' || this.config.promptMode === 'both') {
      visualImpairedService.speak(elementInfo.description || `元素 ${elementInfo.name || elementId}`);
    }
    
    return true;
  }
  
  /**
   * 导航到下一个元素
   * @returns 是否成功导航
   */
  public navigateNext(): boolean {
    if (!this.config.enabled || this.currentPageElements.size === 0) {
      return false;
    }
    
    const elementsArray = Array.from(this.currentPageElements.entries());
    
    if (!this.currentFocusId) {
      // 如果当前没有聚焦元素，聚焦第一个
      const [firstId] = elementsArray[0];
      return this.focusElement(firstId);
    }
    
    // 查找当前聚焦元素的索引
    const currentIndex = elementsArray.findIndex(([id]) => id === this.currentFocusId);
    
    if (currentIndex === -1 || currentIndex === elementsArray.length - 1) {
      // 如果当前是最后一个元素，循环到第一个
      const [firstId] = elementsArray[0];
      return this.focusElement(firstId);
    }
    
    // 聚焦下一个元素
    const [nextId] = elementsArray[currentIndex + 1];
    return this.focusElement(nextId);
  }
  
  /**
   * 导航到上一个元素
   * @returns 是否成功导航
   */
  public navigatePrevious(): boolean {
    if (!this.config.enabled || this.currentPageElements.size === 0) {
      return false;
    }
    
    const elementsArray = Array.from(this.currentPageElements.entries());
    
    if (!this.currentFocusId) {
      // 如果当前没有聚焦元素，聚焦最后一个
      const [lastId] = elementsArray[elementsArray.length - 1];
      return this.focusElement(lastId);
    }
    
    // 查找当前聚焦元素的索引
    const currentIndex = elementsArray.findIndex(([id]) => id === this.currentFocusId);
    
    if (currentIndex === -1 || currentIndex === 0) {
      // 如果当前是第一个元素，循环到最后一个
      const [lastId] = elementsArray[elementsArray.length - 1];
      return this.focusElement(lastId);
    }
    
    // 聚焦上一个元素
    const [prevId] = elementsArray[currentIndex - 1];
    return this.focusElement(prevId);
  }
  
  /**
   * 获取可用的导航命令
   * @returns 导航命令列表
   */
  public getNavigationCommands(): NavigationCommand[] {
    const commands: NavigationCommand[] = [
      { command: 'next', description: '导航到下一个元素' },
      { command: 'previous', description: '导航到上一个元素' },
      { command: 'activate', description: '激活当前元素' }
    ];
    
    if (this.config.quickNavigation) {
      commands.push(
        { command: 'home', description: '导航到首页' },
        { command: 'back', description: '返回上一页' }
      );
      
      // 添加快速导航到特定类型元素的命令
      const elementTypes = new Set(
        Array.from(this.currentPageElements.values())
          .map(info => info.type)
          .filter(Boolean)
      );
      
      elementTypes.forEach(type => {
        if (type) {
          commands.push({
            command: `goto:${type}`,
            description: `导航到${type}类型元素`
          });
        }
      });
    }
    
    return commands;
  }
  
  /**
   * 执行导航命令
   * @param command 导航命令
   * @returns 是否成功执行
   */
  public executeCommand(command: string): boolean {
    if (!this.config.enabled) {
      return false;
    }
    
    logger.info(`执行导航命令: ${command}`);
    
    switch (command) {
      case 'next':
        return this.navigateNext();
      case 'previous':
        return this.navigatePrevious();
      case 'activate':
        return this.activateCurrentElement();
      case 'home':
        // 导航到首页逻辑
        logger.info('导航到首页');
        return true;
      case 'back':
        // 返回上一页逻辑
        if (this.navigationHistory.length > 1) {
          this.navigationHistory.pop(); // 移除当前页
          const prevPage = this.navigationHistory.pop(); // 获取并移除上一页
          logger.info(`返回上一页: ${prevPage}`);
          return true;
        }
        return false;
      default:
        // 处理goto命令
        if (command.startsWith('goto:')) {
          const targetType = command.substring(5);
          return this.navigateToElementType(targetType);
        }
        return false;
    }
  }
  
  /**
   * 激活当前聚焦元素
   * @returns 是否成功激活
   */
  public activateCurrentElement(): boolean {
    if (!this.config.enabled || !this.currentFocusId) {
      return false;
    }
    
    const elementInfo = this.currentPageElements.get(this.currentFocusId);
    if (!elementInfo || !elementInfo.interactive) {
      return false;
    }
    
    logger.info(`激活元素: ${this.currentFocusId}`);
    
    // 实际激活逻辑将在客户端实现
    return true;
  }
  
  /**
   * 导航到特定类型的元素
   * @param elementType 元素类型
   * @returns 是否成功导航
   */
  public navigateToElementType(elementType: string): boolean {
    if (!this.config.enabled) {
      return false;
    }
    
    // 查找指定类型的第一个元素
    const targetElement = Array.from(this.currentPageElements.entries())
      .find(([_, info]) => info.type === elementType);
    
    if (!targetElement) {
      return false;
    }
    
    const [targetId] = targetElement;
    return this.focusElement(targetId);
  }
  
  /**
   * 获取当前位置描述
   * @returns 位置描述
   */
  public getCurrentPosition(): string {
    if (!this.config.enabled || !this.currentFocusId) {
      return '';
    }
    
    const elementInfo = this.currentPageElements.get(this.currentFocusId);
    if (!elementInfo) {
      return '';
    }
    
    // 根据导航模式构建位置描述
    if (this.config.navigationPattern === 'linear') {
      // 线性导航模式
      const elementsArray = Array.from(this.currentPageElements.entries());
      const currentIndex = elementsArray.findIndex(([id]) => id === this.currentFocusId);
      const totalElements = elementsArray.length;
      
      return `元素 ${currentIndex + 1} / ${totalElements}: ${elementInfo.name || this.currentFocusId}`;
    } else {
      // 分组导航模式
      return `区域: ${elementInfo.group || '主区域'}, 元素: ${elementInfo.name || this.currentFocusId}`;
    }
  }
}

/**
 * 元素信息接口
 */
interface ElementInfo {
  name?: string;
  type?: string;
  description?: string;
  interactive: boolean;
  group?: string;
  position?: { x: number; y: number };
}

/**
 * 导航命令接口
 */
interface NavigationCommand {
  command: string;
  description: string;
}

export default new NavigationAssistance();