// 老克智能体实现 - 探索频道版主
// 负责知识管理、教育内容、中医知识RAG等功能

export interface LaokeAgentConfig {
  knowledgeBaseUrl?: string;
  ragEnabled?: boolean;
  contentModerationEnabled?: boolean;
  learningPathsEnabled?: boolean;
}

export interface KnowledgeItem {
  id: string;
  title: string;
  content: string;
  category: string;
  tags: string[];
  difficulty: "beginner" | "intermediate" | "advanced";
  createdAt: Date;
  updatedAt: Date;
}

export interface LearningPath {
  id: string;
  name: string;
  description: string;
  items: KnowledgeItem[];
  estimatedDuration: number;
  prerequisites?: string[];
}

export interface EducationContent {
  id: string;
  type: "article" | "video" | "interactive" | "quiz";
  title: string;
  content: string;
  metadata: Record<string, unknown>;
}

/**
 * 老克智能体实现
 * 探索频道版主，负责知识管理和教育内容
 */
export class LaokeAgentImpl {
  private config: LaokeAgentConfig;
  private knowledgeBase: Map<string, KnowledgeItem> = new Map();
  private learningPaths: Map<string, LearningPath> = new Map();
  private contentCache: Map<string, EducationContent> = new Map();

  constructor(config: LaokeAgentConfig = {}) {
    this.config = {
      knowledgeBaseUrl: "https://api.suoke.life/knowledge",
      ragEnabled: true,
      contentModerationEnabled: true,
      learningPathsEnabled: true,
      ...config
    };
    
    this.initializeKnowledgeBase();
  }

  // 初始化知识库
  private async initializeKnowledgeBase(): Promise<void> {
    // 加载基础中医知识
    const basicKnowledge: KnowledgeItem[] = [
      {
        id: "tcm-001",
        title: "中医基础理论",
        content: "中医基础理论包括阴阳学说、五行学说、脏腑学说等...",
        category: "基础理论",
        tags: ["中医", "基础", "理论"],
        difficulty: "beginner",
        createdAt: new Date(),
        updatedAt: new Date()
      },
      {
        id: "tcm-002", 
        title: "四诊合参",
        content: "四诊即望、闻、问、切，是中医诊断的基本方法...",
        category: "诊断方法",
        tags: ["四诊", "诊断", "望闻问切"],
        difficulty: "intermediate",
        createdAt: new Date(),
        updatedAt: new Date()
      }
    ];

    for (const item of basicKnowledge) {
      this.knowledgeBase.set(item.id, item);
    }
  }

  // 处理消息
  async processMessage(message: string, context?: unknown): Promise<string> {
    try {
      // 解析用户意图
      const intent = this.parseIntent(message);
      
      switch (intent.type) {
        case "knowledge_query":
          return await this.handleKnowledgeQuery(intent.query, context);
        case "learning_path":
          return await this.handleLearningPathRequest(intent.topic, context);
        case "content_creation":
          return await this.handleContentCreation(intent.content, context);
        default:
          return await this.handleGeneralQuery(message, context);
      }
    } catch (error) {
      console.error("LaokeAgent处理消息时出错:", error);
      return "抱歉，我在处理您的请求时遇到了问题，请稍后再试。";
    }
  }

  // 解析用户意图
  private parseIntent(message: string): { type: string; query?: string; topic?: string; content?: string } {
    const lowerMessage = message.toLowerCase();
    
    if (lowerMessage.includes("学习路径") || lowerMessage.includes("学习计划")) {
      return { type: "learning_path", topic: message };
    }
    
    if (lowerMessage.includes("创建") || lowerMessage.includes("编写")) {
      return { type: "content_creation", content: message };
    }
    
    if (lowerMessage.includes("什么是") || lowerMessage.includes("如何") || lowerMessage.includes("?")) {
      return { type: "knowledge_query", query: message };
    }
    
    return { type: "general", query: message };
  }

  // 处理知识查询
  private async handleKnowledgeQuery(query: string, context?: unknown): Promise<string> {
    // 在知识库中搜索相关内容
    const relevantItems = this.searchKnowledgeBase(query);
    
    if (relevantItems.length === 0) {
      return "抱歉，我没有找到相关的知识内容。您可以尝试换个关键词搜索。";
    }
    
    // 返回最相关的知识项
    const topItem = relevantItems[0];
    return `关于"${query}"的信息：\n\n${topItem.title}\n\n${topItem.content}\n\n标签：${topItem.tags.join(", ")}`;
  }

  // 搜索知识库
  private searchKnowledgeBase(query: string): KnowledgeItem[] {
    const results: KnowledgeItem[] = [];
    const queryLower = query.toLowerCase();
    
    for (const item of this.knowledgeBase.values()) {
      const score = this.calculateRelevanceScore(item, queryLower);
      if (score > 0) {
        results.push(item);
      }
    }
    
    // 按相关性排序
    return results.sort((a, b) => 
      this.calculateRelevanceScore(b, queryLower) - this.calculateRelevanceScore(a, queryLower)
    );
  }

  // 计算相关性分数
  private calculateRelevanceScore(item: KnowledgeItem, query: string): number {
    let score = 0;
    
    // 标题匹配
    if (item.title.toLowerCase().includes(query)) {
      score += 10;
    }
    
    // 内容匹配
    if (item.content.toLowerCase().includes(query)) {
      score += 5;
    }
    
    // 标签匹配
    for (const tag of item.tags) {
      if (tag.toLowerCase().includes(query)) {
        score += 3;
      }
    }
    
    return score;
  }

  // 处理学习路径请求
  private async handleLearningPathRequest(topic: string, context?: unknown): Promise<string> {
    // 根据主题生成学习路径
    const path = this.generateLearningPath(topic);
    
    if (!path) {
      return "抱歉，我暂时无法为该主题生成学习路径。";
    }
    
    let response = `为您推荐"${path.name}"学习路径：\n\n`;
    response += `描述：${path.description}\n`;
    response += `预计学习时间：${path.estimatedDuration}小时\n\n`;
    response += "学习内容：\n";
    
    path.items.forEach((item, index) => {
      response += `${index + 1}. ${item.title} (${item.difficulty})\n`;
    });
    
    return response;
  }

  // 生成学习路径
  private generateLearningPath(topic: string): LearningPath | null {
    const topicLower = topic.toLowerCase();
    
    if (topicLower.includes("中医") || topicLower.includes("基础")) {
      const items = Array.from(this.knowledgeBase.values())
        .filter(item => item.category === "基础理论")
        .sort((a, b) => a.difficulty.localeCompare(b.difficulty));
      
      return {
        id: "tcm-basic-path",
        name: "中医基础学习路径",
        description: "从零开始学习中医基础理论和诊断方法",
        items,
        estimatedDuration: 40,
        prerequisites: []
      };
    }
    
    return null;
  }

  // 处理内容创建
  private async handleContentCreation(content: string, context?: unknown): Promise<string> {
    return "内容创建功能正在开发中，敬请期待！";
  }

  // 处理一般查询
  private async handleGeneralQuery(message: string, context?: unknown): Promise<string> {
    return `您好！我是老克，探索频道的版主。我可以帮您：
1. 查询中医知识和健康信息
2. 制定个性化学习路径
3. 推荐教育内容
4. 解答健康相关问题

请告诉我您想了解什么？`;
  }

  // 添加知识项
  async addKnowledgeItem(item: KnowledgeItem): Promise<void> {
    this.knowledgeBase.set(item.id, item);
  }

  // 获取知识统计
  getKnowledgeStats(): { totalItems: number; categories: string[]; } {
    const categories = new Set<string>();
    
    for (const item of this.knowledgeBase.values()) {
      categories.add(item.category);
    }
    
    return {
      totalItems: this.knowledgeBase.size,
      categories: Array.from(categories)
    };
  }

  // 获取状态
  getStatus(): { status: string; load: number; } {
    return {
      status: "active",
      load: this.knowledgeBase.size / 1000 // 简单的负载计算
    };
  }

  // 关闭智能体
  async shutdown(): Promise<void> {
    this.knowledgeBase.clear();
    this.learningPaths.clear();
    this.contentCache.clear();
  }
}

// 导出默认实例
export const laokeAgent = new LaokeAgentImpl();
export default laokeAgent; 