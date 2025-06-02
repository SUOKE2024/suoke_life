// 小艾智能体实现 - 健康助手 & 首页聊天频道版主
// 负责健康分析、四诊合参、语音交互等功能

export interface XiaoaiAgentConfig {
  enableVoiceInteraction: boolean;
  enableFourDiagnosis: boolean;
  enableAccessibilityServices: boolean;
  healthAnalysisEnabled: boolean;
}

export interface HealthProfile {
  userId: string;
  age: number;
  gender: "male" | "female" | "other";
  height: number;
  weight: number;
  medicalHistory: string[];
  allergies: string[];
  currentSymptoms: string[];
}

export interface DiagnosisResult {
  id: string;
  userId: string;
  symptoms: string[];
  diagnosis: string;
  recommendations: string[];
  confidence: number;
  timestamp: Date;
  followUpRequired: boolean;
}

export interface VoiceInteractionSession {
  sessionId: string;
  userId: string;
  startTime: Date;
  endTime?: Date;
  messages: Array<{
    type: "user" | "agent";
    content: string;
    timestamp: Date;
  }>;
}

/**
 * 小艾智能体实现
 * 健康助手和首页聊天频道版主，负责健康分析和用户交互
 */
export class XiaoaiAgentImpl {
  private config: XiaoaiAgentConfig;
  private healthProfiles: Map<string, HealthProfile> = new Map();
  private diagnosisHistory: Map<string, DiagnosisResult[]> = new Map();
  private voiceSessions: Map<string, VoiceInteractionSession> = new Map();

  constructor(config: Partial<XiaoaiAgentConfig> = {}) {
    this.config = {
      enableVoiceInteraction: true,
      enableFourDiagnosis: true,
      enableAccessibilityServices: true,
      healthAnalysisEnabled: true,
      ...config
    };
  }

  // 处理消息
  async processMessage(message: string, context?: unknown): Promise<string> {
    try {
      // 解析用户意图
      const intent = this.parseIntent(message);
      
      switch (intent.type) {
        case "health_inquiry":
          return await this.handleHealthInquiry(intent.symptoms, context);
        case "diagnosis_request":
          return await this.handleDiagnosisRequest(intent.symptoms, context);
        case "health_advice":
          return await this.handleHealthAdvice(intent.topic, context);
        case "voice_interaction":
          return await this.handleVoiceInteraction(message, context);
        default:
          return await this.handleGeneralChat(message, context);
      }
    } catch (error) {
      console.error("XiaoaiAgent处理消息时出错:", error);
      return "抱歉，我在处理您的健康咨询时遇到了问题，请稍后再试。";
    }
  }

  // 解析用户意图
  private parseIntent(message: string): { 
    type: string; 
    symptoms?: string[]; 
    topic?: string; 
  } {
    const lowerMessage = message.toLowerCase();
    
    // 健康咨询关键词
    const healthKeywords = ["头痛", "发烧", "咳嗽", "胃痛", "失眠", "疲劳"];
    const hasHealthKeywords = healthKeywords.some(keyword => 
      lowerMessage.includes(keyword)
    );
    
    if (hasHealthKeywords || lowerMessage.includes("不舒服") || lowerMessage.includes("症状")) {
      return { 
        type: "health_inquiry", 
        symptoms: this.extractSymptoms(message) 
      };
    }
    
    if (lowerMessage.includes("诊断") || lowerMessage.includes("看病")) {
      return { 
        type: "diagnosis_request", 
        symptoms: this.extractSymptoms(message) 
      };
    }
    
    if (lowerMessage.includes("建议") || lowerMessage.includes("怎么办")) {
      return { 
        type: "health_advice", 
        topic: message 
      };
    }
    
    if (lowerMessage.includes("语音") || lowerMessage.includes("说话")) {
      return { type: "voice_interaction" };
    }
    
    return { type: "general_chat" };
  }

  // 提取症状
  private extractSymptoms(message: string): string[] {
    const symptoms: string[] = [];
    const symptomKeywords = [
      "头痛", "发烧", "咳嗽", "胃痛", "失眠", "疲劳", 
      "恶心", "呕吐", "腹泻", "便秘", "心悸", "胸闷"
    ];
    
    for (const keyword of symptomKeywords) {
      if (message.includes(keyword)) {
        symptoms.push(keyword);
      }
    }
    
    return symptoms;
  }

  // 处理健康咨询
  private async handleHealthInquiry(symptoms: string[], context?: unknown): Promise<string> {
    if (!symptoms || symptoms.length === 0) {
      return "请详细描述您的症状，我会为您提供初步的健康建议。";
    }
    
    // 基于症状提供初步建议
    const advice = this.generateHealthAdvice(symptoms);
    
    return `根据您描述的症状：${symptoms.join("、")}，我的初步建议是：\n\n${advice}\n\n请注意：这只是初步建议，如症状持续或加重，请及时就医。`;
  }

  // 生成健康建议
  private generateHealthAdvice(symptoms: string[]): string {
    const adviceMap: Record<string, string> = {
      "头痛": "建议多休息，保持充足睡眠，避免过度用眼。如果是偏头痛，可以尝试冷敷或热敷。",
      "发烧": "多喝水，注意休息，可以用温水擦身降温。体温超过38.5°C建议就医。",
      "咳嗽": "多喝温水，避免刺激性食物，保持室内湿度适宜。干咳可以含润喉糖。",
      "胃痛": "注意饮食清淡，避免辛辣刺激食物，可以喝温开水或淡盐水。",
      "失眠": "建议睡前避免使用电子设备，保持规律作息，可以尝试冥想或深呼吸。",
      "疲劳": "注意劳逸结合，保证充足睡眠，适当运动，补充维生素。"
    };
    
    const advice: string[] = [];
    for (const symptom of symptoms) {
      if (adviceMap[symptom]) {
        advice.push(adviceMap[symptom]);
      }
    }
    
    if (advice.length === 0) {
      return "建议您详细记录症状的时间、程度和诱发因素，并咨询专业医生。";
    }
    
    return advice.join("\n\n");
  }

  // 处理诊断请求
  private async handleDiagnosisRequest(symptoms: string[], context?: unknown): Promise<string> {
    if (!this.config.enableFourDiagnosis) {
      return "诊断功能暂时不可用，建议您咨询专业医生。";
    }
    
    // 模拟四诊合参诊断
    const diagnosis = await this.performFourDiagnosis(symptoms);
    
    return `基于中医四诊合参的初步分析：\n\n${diagnosis}\n\n重要提醒：这只是辅助分析，不能替代专业医生诊断，请及时就医确诊。`;
  }

  // 执行四诊合参
  private async performFourDiagnosis(symptoms: string[]): Promise<string> {
    // 这里应该实现真正的中医四诊算法
    // 目前提供简化版本
    
    const constitutionTypes = ["平和质", "气虚质", "阳虚质", "阴虚质", "痰湿质", "湿热质", "血瘀质", "气郁质", "特禀质"];
    const randomConstitution = constitutionTypes[Math.floor(Math.random() * constitutionTypes.length)];
    
    return `望诊：根据症状描述分析
闻诊：需要进一步了解声音和气味
问诊：已收集症状信息 - ${symptoms.join("、")}
切诊：建议现场脉诊

初步体质判断：${randomConstitution}
建议：根据体质特点调理，具体方案需要专业中医师制定。`;
  }

  // 处理健康建议
  private async handleHealthAdvice(topic: string, context?: unknown): Promise<string> {
    return `关于"${topic}"的健康建议：

1. 保持良好的生活习惯
2. 均衡饮食，适量运动
3. 保证充足睡眠
4. 定期体检，预防为主
5. 保持心情愉悦，减少压力

如需更具体的建议，请提供更详细的信息。`;
  }

  // 处理语音交互
  private async handleVoiceInteraction(message: string, context?: unknown): Promise<string> {
    if (!this.config.enableVoiceInteraction) {
      return "语音交互功能暂时不可用。";
    }
    
    return "语音交互功能正在开发中，目前支持文字交流。请描述您的健康问题，我会为您提供帮助。";
  }

  // 处理一般聊天
  private async handleGeneralChat(message: string, context?: unknown): Promise<string> {
    const greetings = ["你好", "您好", "hi", "hello"];
    const lowerMessage = message.toLowerCase();
    
    if (greetings.some(greeting => lowerMessage.includes(greeting))) {
      return `您好！我是小艾，您的健康助手。我可以帮您：
1. 分析健康症状
2. 提供中医四诊建议
3. 制定健康计划
4. 解答健康问题

请告诉我您有什么健康方面的问题吗？`;
    }
    
    return "我是您的健康助手小艾，专注于健康咨询和中医诊断。请告诉我您的健康问题，我会尽力帮助您。";
  }

  // 创建健康档案
  async createHealthProfile(profile: HealthProfile): Promise<void> {
    this.healthProfiles.set(profile.userId, profile);
  }

  // 获取健康档案
  getHealthProfile(userId: string): HealthProfile | null {
    return this.healthProfiles.get(userId) || null;
  }

  // 保存诊断结果
  async saveDiagnosisResult(result: DiagnosisResult): Promise<void> {
    const userHistory = this.diagnosisHistory.get(result.userId) || [];
    userHistory.push(result);
    this.diagnosisHistory.set(result.userId, userHistory);
  }

  // 获取诊断历史
  getDiagnosisHistory(userId: string): DiagnosisResult[] {
    return this.diagnosisHistory.get(userId) || [];
  }

  // 获取状态
  getStatus(): { status: string; load: number; } {
    return {
      status: "active",
      load: this.healthProfiles.size / 100 // 简单的负载计算
    };
  }

  // 关闭智能体
  async shutdown(): Promise<void> {
    this.healthProfiles.clear();
    this.diagnosisHistory.clear();
    this.voiceSessions.clear();
  }
}

// 导出默认实例
export const xiaoaiAgent = new XiaoaiAgentImpl();
export default xiaoaiAgent; 