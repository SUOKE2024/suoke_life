import { apiClient } from "./apiClient";
import { authService } from "./authService";
import { EventEmitter } from "../utils/eventEmitter";


// API服务配置接口
interface ApiServiceConfig {
  baseURL: string;
  timeout: number;
  retries: number;
  enableCache: boolean;
  enableRealTime: boolean;
}

// 健康数据接口
interface HealthData {
  id: string;
  userId: string;
  metrics: {
    heartRate: number;
    bloodPressure: { systolic: number; diastolic: number };
    sleepQuality: number;
    stressLevel: number;
    activityLevel: number;
    nutritionScore: number;
  };
  constitution: {
    type: string;
    percentage: number;
    description: string;
  }[];
  timestamp: string;
}

// 智能体状态接口
interface AgentStatus {
  id: string;
  name: string;
  status: "online" | "offline" | "busy";
  workload: number;
  performance: {
    accuracy: number;
    responseTime: number;
    userSatisfaction: number;
  };
  currentTask?: string;
  lastUpdate: string;
}

// 诊断结果接口
interface DiagnosisResult {
  id: string;
  userId: string;
  type: "look" | "listen" | "inquiry" | "palpation" | "comprehensive";
  results: {
    symptoms: string[];
    constitution: string;
    recommendations: string[];
    confidence: number;
  };
  timestamp: string;
}

// 用户设置接口
interface UserSettings {
  accessibility: {
    screenReader: boolean;
    highContrast: boolean;
    largeText: boolean;
    reduceMotion: boolean;
    voiceOver: boolean;
    hapticFeedback: boolean;
  };
  personalization: {
    theme: "light" | "dark" | "auto";
    language: "zh" | "en";
    fontSize: number;
    animationSpeed: number;
    notifications: {
      health: boolean;
      agents: boolean;
      system: boolean;
    };
  };
  privacy: {
    dataSharing: boolean;
    analytics: boolean;
    locationTracking: boolean;
  };
}

// 区块链健康记录接口
interface BlockchainHealthRecord {
  id: string;
  userId: string;
  dataHash: string;
  timestamp: string;
  signature: string;
  verified: boolean;
  metadata: {
    dataType: string;
    source: string;
    version: string;
  };
}

// 医疗资源接口
interface MedicalResource {
  id: string;
  type: "hospital" | "clinic" | "pharmacy" | "specialist";
  name: string;
  location: {
    address: string;
    coordinates: { lat: number; lng: number };
  };
  services: string[];
  rating: number;
  availability: {
    isOpen: boolean;
    hours: string;
    nextAvailable: string;
  };
  contact: {
    phone: string;
    website?: string;
    email?: string;
  };
}

// 知识库查询接口
interface KnowledgeQuery {
  query: string;
  type: "symptom" | "treatment" | "medicine" | "general";
  context?: {
    userId?: string;
    symptoms?: string[];
    constitution?: string;
  };
}

interface KnowledgeResult {
  id: string;
  title: string;
  content: string;
  relevance: number;
  source: string;
  category: string;
  tags: string[];
  lastUpdated: string;
}

// 反馈接口
interface UserFeedback {
  userId: string;
  type: "bug" | "feature" | "improvement" | "general";
  rating: number;
  message: string;
  metadata?: any;
}

// 性能指标接口
interface PerformanceMetrics {
  userId: string;
  renderTime: number;
  memoryUsage: number;
  networkLatency: number;
  errorCount: number;
  userSatisfaction: number;
}

export class ApiIntegrationService {
  private eventEmitter: EventEmitter;
  private config: ApiServiceConfig;

  constructor(config: Partial<ApiServiceConfig> = {}) {
    this.config = {
      baseURL: "http://localhost:8000",
      timeout: 30000,
      retries: 3,
      enableCache: true,
      enableRealTime: true,
      ...config,
    };

    this.eventEmitter = new EventEmitter();
    this.setupEventListeners();
  }

  private setupEventListeners() {
    // 设置全局事件监听
    this.eventEmitter.on("api:error", (error) => {
      console.error("API错误:", error);
    });

    this.eventEmitter.on("api:success", (data) => {
      console.log("API成功:", data);
    });
  }

  // ==================== 认证相关 API ====================

  async login(credentials: { username: string; password: string }) {
    try {
      const response = await authService.login({
        email: credentials.username,
        password: credentials.password,
      });
      this.eventEmitter.emit("api:login:success", response);
      return response;
    } catch (error) {
      this.eventEmitter.emit("api:login:error", error);
      throw error;
    }
  }

  async logout() {
    try {
      const response = await authService.logout();
      this.eventEmitter.emit("api:logout:success");
      return response;
    } catch (error) {
      this.eventEmitter.emit("api:logout:error", error);
      throw error;
    }
  }

  async refreshToken() {
    try {
      return await authService.refreshAccessToken();
    } catch (error) {
      console.error("刷新Token失败:", error);
      throw error;
    }
  }

  async getCurrentUser() {
    try {
      return await authService.getCurrentUser();
    } catch (error) {
      console.error("获取当前用户失败:", error);
      throw error;
    }
  }

  // ==================== 健康数据 API ====================

  async getHealthData(
    userId: string,
    timeRange?: { start: string; end: string }
  ): Promise<HealthData[]> {
    try {
      const response = await apiClient.get("/health-data", {
        userId,
        ...timeRange,
      });
      return response.data;
    } catch (error) {
      console.error("获取健康数据失败:", error);
      throw error;
    }
  }

  async saveHealthData(
    data: Omit<HealthData, "id" | "timestamp">
  ): Promise<HealthData> {
    try {
      const response = await apiClient.post("/health-data", {
        ...data,
        timestamp: new Date().toISOString(),
      });
      this.eventEmitter.emit("health:data:saved", response.data);
      return response.data;
    } catch (error) {
      console.error("保存健康数据失败:", error);
      throw error;
    }
  }

  async getHealthMetrics(userId: string, metric: string, period: string) {
    try {
      const response = await apiClient.get(`/health-data/metrics/${metric}`, {
        userId,
        period,
      });
      return response.data;
    } catch (error) {
      console.error("获取健康指标失败:", error);
      throw error;
    }
  }

  async exportHealthData(
    userId: string,
    format: "json" | "csv" | "pdf" = "json"
  ) {
    try {
      const response = await apiClient.get(`/health-data/export`, {
        userId,
        format,
      });
      return response.data;
    } catch (error) {
      console.error("导出健康数据失败:", error);
      throw error;
    }
  }

  // ==================== 智能体相关 API ====================

  async getAgentStatus(): Promise<AgentStatus[]> {
    try {
      const response = await apiClient.get("/agents/status");
      return response.data;
    } catch (error) {
      console.error("获取智能体状态失败:", error);
      throw error;
    }
  }

  async startAgentChat(agentId: string, message: string) {
    try {
      const response = await apiClient.post(`/agents/${agentId}/chat`, {
        message,
        timestamp: new Date().toISOString(),
      });
      this.eventEmitter.emit("agent:chat:started", { agentId, response });
      return response.data;
    } catch (error) {
      console.error("启动智能体对话失败:", error);
      throw error;
    }
  }

  async sendMessageToAgent(agentId: string, message: string, context?: any) {
    try {
      const response = await apiClient.post(`/agents/${agentId}/message`, {
        message,
        context,
        timestamp: new Date().toISOString(),
      });
      this.eventEmitter.emit("agent:message:sent", {
        agentId,
        message,
        response,
      });
      return response.data;
    } catch (error) {
      console.error("发送消息给智能体失败:", error);
      throw error;
    }
  }

  async getAgentPerformance(
    agentId: string,
    timeRange?: { start: string; end: string }
  ) {
    try {
      const response = await apiClient.get(
        `/agents/${agentId}/performance`,
        timeRange
      );
      return response.data;
    } catch (error) {
      console.error("获取智能体性能数据失败:", error);
      throw error;
    }
  }

  async updateAgentSettings(agentId: string, settings: any) {
    try {
      const response = await apiClient.put(
        `/agents/${agentId}/settings`,
        settings
      );
      this.eventEmitter.emit("agent:settings:updated", { agentId, settings });
      return response.data;
    } catch (error) {
      console.error("更新智能体设置失败:", error);
      throw error;
    }
  }

  // ==================== 四诊相关 API ====================

  async startDiagnosis(
    type: "look" | "listen" | "inquiry" | "palpation",
    data: any
  ): Promise<DiagnosisResult> {
    try {
      const response = await apiClient.post(`/diagnosis/${type}`, {
        ...data,
        timestamp: new Date().toISOString(),
      });
      this.eventEmitter.emit("diagnosis:started", { type, response });
      return response.data;
    } catch (error) {
      console.error("启动诊断失败:", error);
      throw error;
    }
  }

  async getDiagnosisHistory(
    userId: string,
    limit: number = 10
  ): Promise<DiagnosisResult[]> {
    try {
      const response = await apiClient.get("/diagnosis/history", {
        userId,
        limit,
      });
      return response.data;
    } catch (error) {
      console.error("获取诊断历史失败:", error);
      throw error;
    }
  }

  async getComprehensiveDiagnosis(
    userId: string,
    symptoms: string[]
  ): Promise<DiagnosisResult> {
    try {
      const response = await apiClient.post("/diagnosis/comprehensive", {
        userId,
        symptoms,
        timestamp: new Date().toISOString(),
      });
      this.eventEmitter.emit(
        "diagnosis:comprehensive:completed",
        response.data
      );
      return response.data;
    } catch (error) {
      console.error("获取综合诊断失败:", error);
      throw error;
    }
  }

  // ==================== 用户设置 API ====================

  async getUserSettings(userId: string): Promise<UserSettings> {
    try {
      const response = await apiClient.get(`/users/${userId}/settings`);
      return response.data;
    } catch (error) {
      console.error("获取用户设置失败:", error);
      throw error;
    }
  }

  async updateUserSettings(
    userId: string,
    settings: Partial<UserSettings>
  ): Promise<UserSettings> {
    try {
      const response = await apiClient.put(
        `/users/${userId}/settings`,
        settings
      );
      this.eventEmitter.emit("user:settings:updated", {
        userId,
        settings: response.data,
      });
      return response.data;
    } catch (error) {
      console.error("更新用户设置失败:", error);
      throw error;
    }
  }

  async resetUserSettings(userId: string): Promise<UserSettings> {
    try {
      const response = await apiClient.post(`/users/${userId}/settings/reset`);
      this.eventEmitter.emit("user:settings:reset", { userId });
      return response.data;
    } catch (error) {
      console.error("重置用户设置失败:", error);
      throw error;
    }
  }

  // ==================== 区块链健康记录 API ====================

  async saveHealthRecordToBlockchain(
    userId: string,
    healthData: any
  ): Promise<BlockchainHealthRecord> {
    try {
      const response = await apiClient.post("/blockchain/health-records", {
        userId,
        data: healthData,
        timestamp: new Date().toISOString(),
      });
      this.eventEmitter.emit("blockchain:record:saved", response.data);
      return response.data;
    } catch (error) {
      console.error("保存区块链健康记录失败:", error);
      throw error;
    }
  }

  async getBlockchainHealthRecords(
    userId: string
  ): Promise<BlockchainHealthRecord[]> {
    try {
      const response = await apiClient.get(
        `/blockchain/health-records/${userId}`
      );
      return response.data;
    } catch (error) {
      console.error("获取区块链健康记录失败:", error);
      throw error;
    }
  }

  async verifyHealthRecord(
    recordId: string
  ): Promise<{ verified: boolean; details: any }> {
    try {
      const response = await apiClient.post(`/blockchain/verify/${recordId}`);
      return response.data;
    } catch (error) {
      console.error("验证健康记录失败:", error);
      throw error;
    }
  }

  // ==================== 医疗资源 API ====================

  async searchMedicalResources(query: {
    type?: string;
    location?: { lat: number; lng: number; radius: number };
    services?: string[];
  }): Promise<MedicalResource[]> {
    try {
      const response = await apiClient.get("/medical-resources/search", query);
      return response.data;
    } catch (error) {
      console.error("搜索医疗资源失败:", error);
      throw error;
    }
  }

  async getMedicalResourceDetails(
    resourceId: string
  ): Promise<MedicalResource> {
    try {
      const response = await apiClient.get(`/medical-resources/${resourceId}`);
      return response.data;
    } catch (error) {
      console.error("获取医疗资源详情失败:", error);
      throw error;
    }
  }

  async bookMedicalAppointment(
    resourceId: string,
    appointmentData: {
      userId: string;
      serviceType: string;
      preferredTime: string;
      notes?: string;
    }
  ) {
    try {
      const response = await apiClient.post(
        `/medical-resources/${resourceId}/appointments`,
        {
          ...appointmentData,
          timestamp: new Date().toISOString(),
        }
      );
      this.eventEmitter.emit("appointment:booked", response.data);
      return response.data;
    } catch (error) {
      console.error("预约医疗服务失败:", error);
      throw error;
    }
  }

  // ==================== 知识库 API ====================

  async searchKnowledge(query: KnowledgeQuery): Promise<KnowledgeResult[]> {
    try {
      const response = await apiClient.post("/knowledge/search", query);
      return response.data;
    } catch (error) {
      console.error("搜索知识库失败:", error);
      throw error;
    }
  }

  async getKnowledgeDetails(knowledgeId: string): Promise<KnowledgeResult> {
    try {
      const response = await apiClient.get(`/knowledge/${knowledgeId}`);
      return response.data;
    } catch (error) {
      console.error("获取知识详情失败:", error);
      throw error;
    }
  }

  async getRecommendedKnowledge(
    userId: string,
    context?: any
  ): Promise<KnowledgeResult[]> {
    try {
      const response = await apiClient.get(
        `/knowledge/recommendations/${userId}`,
        { context }
      );
      return response.data;
    } catch (error) {
      console.error("获取推荐知识失败:", error);
      throw error;
    }
  }

  // ==================== 机器学习 API ====================

  async trainPersonalModel(userId: string, trainingData: any) {
    try {
      const response = await apiClient.post(`/ml/models/${userId}/train`, {
        data: trainingData,
        timestamp: new Date().toISOString(),
      });
      this.eventEmitter.emit("ml:training:started", { userId, response });
      return response.data;
    } catch (error) {
      console.error("训练个人模型失败:", error);
      throw error;
    }
  }

  async getModelPrediction(userId: string, inputData: any) {
    try {
      const response = await apiClient.post(`/ml/models/${userId}/predict`, {
        input: inputData,
        timestamp: new Date().toISOString(),
      });
      return response.data;
    } catch (error) {
      console.error("获取模型预测失败:", error);
      throw error;
    }
  }

  async getModelPerformance(userId: string) {
    try {
      const response = await apiClient.get(`/ml/models/${userId}/performance`);
      return response.data;
    } catch (error) {
      console.error("获取模型性能失败:", error);
      throw error;
    }
  }

  // ==================== 无障碍服务 API ====================

  async getAccessibilitySettings(userId: string) {
    try {
      const response = await apiClient.get(`/accessibility/settings/${userId}`);
      return response.data;
    } catch (error) {
      console.error("获取无障碍设置失败:", error);
      throw error;
    }
  }

  async updateAccessibilitySettings(userId: string, settings: any) {
    try {
      const response = await apiClient.put(
        `/accessibility/settings/${userId}`,
        settings
      );
      this.eventEmitter.emit("accessibility:settings:updated", {
        userId,
        settings,
      });
      return response.data;
    } catch (error) {
      console.error("更新无障碍设置失败:", error);
      throw error;
    }
  }

  async generateAccessibilityReport(userId: string) {
    try {
      const response = await apiClient.get(`/accessibility/report/${userId}`);
      return response.data;
    } catch (error) {
      console.error("生成无障碍报告失败:", error);
      throw error;
    }
  }

  // ==================== 生态服务 API ====================

  async getEcoServices() {
    try {
      const response = await apiClient.get("/eco-services");
      return response.data;
    } catch (error) {
      console.error("获取生态服务失败:", error);
      throw error;
    }
  }

  async subscribeToEcoService(userId: string, serviceId: string, plan: string) {
    try {
      const response = await apiClient.post(
        `/eco-services/${serviceId}/subscribe`,
        {
          userId,
          plan,
          timestamp: new Date().toISOString(),
        }
      );
      this.eventEmitter.emit("eco:service:subscribed", {
        userId,
        serviceId,
        plan,
      });
      return response.data;
    } catch (error) {
      console.error("订阅生态服务失败:", error);
      throw error;
    }
  }

  async getEcoServiceUsage(userId: string, serviceId: string) {
    try {
      const response = await apiClient.get(
        `/eco-services/${serviceId}/usage/${userId}`
      );
      return response.data;
    } catch (error) {
      console.error("获取生态服务使用情况失败:", error);
      throw error;
    }
  }

  // ==================== 反馈和支持 API ====================

  async submitFeedback(feedback: UserFeedback) {
    try {
      const response = await apiClient.post("/feedback", {
        ...feedback,
        timestamp: new Date().toISOString(),
      });
      this.eventEmitter.emit("feedback:submitted", response.data);
      return response.data;
    } catch (error) {
      console.error("提交反馈失败:", error);
      throw error;
    }
  }

  async getFeedbackHistory(userId: string) {
    try {
      const response = await apiClient.get(`/feedback/history/${userId}`);
      return response.data;
    } catch (error) {
      console.error("获取反馈历史失败:", error);
      throw error;
    }
  }

  async getSupportTickets(userId: string) {
    try {
      const response = await apiClient.get(`/support/tickets/${userId}`);
      return response.data;
    } catch (error) {
      console.error("获取支持工单失败:", error);
      throw error;
    }
  }

  async createSupportTicket(ticket: {
    userId: string;
    subject: string;
    description: string;
    priority: "low" | "medium" | "high" | "urgent";
    category: string;
  }) {
    try {
      const response = await apiClient.post("/support/tickets", {
        ...ticket,
        timestamp: new Date().toISOString(),
      });
      this.eventEmitter.emit("support:ticket:created", response.data);
      return response.data;
    } catch (error) {
      console.error("创建支持工单失败:", error);
      throw error;
    }
  }

  // ==================== 系统监控 API ====================

  async getSystemHealth() {
    try {
      const response = await apiClient.get("/system/health");
      return response.data;
    } catch (error) {
      console.error("获取系统健康状态失败:", error);
      throw error;
    }
  }

  async getSystemMetrics() {
    try {
      const response = await apiClient.get("/system/metrics");
      return response.data;
    } catch (error) {
      console.error("获取系统指标失败:", error);
      throw error;
    }
  }

  async reportPerformanceMetrics(metrics: PerformanceMetrics) {
    try {
      const response = await apiClient.post("/system/performance", {
        ...metrics,
        timestamp: new Date().toISOString(),
      });
      return response.data;
    } catch (error) {
      console.error("报告性能指标失败:", error);
      throw error;
    }
  }

  // ==================== 实用工具方法 ====================

  /**
   * 批量API请求
   */
  async batchRequest(
    requests: Array<{ name: string; request: () => Promise<any> }>
  ) {
    try {
      const results = await Promise.allSettled(
        requests.map(async ({ name, request }) => {
          try {
            const result = await request();
            return { name, success: true, data: result };
          } catch (error) {
            return { name, success: false, error };
          }
        })
      );

      return results.map((result, index) => {
        if (result.status === "fulfilled") {
          return result.value;
        } else {
          return {
            name: requests[index].name,
            success: false,
            error: result.reason,
          };
        }
      });
    } catch (error) {
      console.error("批量请求失败:", error);
      throw error;
    }
  }

  /**
   * 健康检查
   */
  async healthCheck(): Promise<boolean> {
    try {
      const response = await apiClient.get("/health");
      return response.success;
    } catch (error) {
      console.error("健康检查失败:", error);
      return false;
    }
  }

  /**
   * 获取API版本信息
   */
  async getApiVersion() {
    try {
      const response = await apiClient.get("/version");
      return response.data;
    } catch (error) {
      console.error("获取API版本失败:", error);
      throw error;
    }
  }

  /**
   * 事件监听
   */
  on(event: string, listener: (...args: any[]) => void) {
    this.eventEmitter.on(event, listener);
  }

  /**
   * 移除事件监听
   */
  off(event: string, listener: (...args: any[]) => void) {
    this.eventEmitter.off(event, listener);
  }

  /**
   * 销毁服务
   */
  destroy() {
    this.eventEmitter.removeAllListeners();
  }
}

// 创建单例实例
export const apiIntegrationService = new ApiIntegrationService();
