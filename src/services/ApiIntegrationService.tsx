import React from 'react';
import { usePerformanceMonitor } from '../hooks/usePerformanceMonitor';
import { apiClient } from "./apiClient"/import { authService } from "./authService"/import { EventEmitter } from "../utils/eventEmitter";/;
// API服务配置接口 * interface ApiServiceConfig { baseURL: string, */
  timeout: number,
  retries: number,
  enableCache: boolean,
  enableRealTime: boolean}
// 健康数据接口 * interface HealthData { id: string, */
  userId: string,
  metrics: {heartRate: number,
    bloodPressure: { systolic: number, diastolic: number},
    sleepQuality: number,
    stressLevel: number,
    activityLevel: number,
    nutritionScore: number};
  constitution: { type: string,
    percentage: number,
    description: string}[]
  timestamp: string}
// 智能体状态接口 * interface AgentStatus { id: string, */
  name: string,
  status: "online" | "offline" | "busy",
  workload: number,
  performance: {accuracy: number,
    responseTime: number,
    userSatisfaction: number};
  currentTask?: string,
  lastUpdate: string}
// 诊断结果接口 * interface DiagnosisResult { id: string, */
  userId: string,
  type: "look" | "listen" | "inquiry" | "palpation" | "comprehensive",
  results: {symptoms: string[],
    constitution: string,
    recommendations: string[],
    confidence: number};
  timestamp: string}
// 用户设置接口 * interface UserSettings { accessibility: {screenReader: boolean, */
    highContrast: boolean,
    largeText: boolean,
    reduceMotion: boolean,
    voiceOver: boolean,
    hapticFeedback: boolean}
  personalization: { theme: "light" | "dark" | "auto",
    language: "zh" | "en",
    fontSize: number,
    animationSpeed: number,
    notifications: {
      health: boolean,
      agents: boolean,
      system: boolean};
  };
  privacy: { dataSharing: boolean,
    analytics: boolean,
    locationTracking: boolean};
}
// 区块链健康记录接口 * interface BlockchainHealthRecord { id: string, */
  userId: string,
  dataHash: string,
  timestamp: string,
  signature: string,
  verified: boolean,
  metadata: {dataType: string,
    source: string,
    version: string}
}
// 医疗资源接口 * interface MedicalResource { id: string, */
  type: "hospital" | "clinic" | "pharmacy" | "specialist",
  name: string,
  location: {address: string,
    coordinates: { lat: number, lng: number};
  };
  services: string[],
  rating: number,
  availability: { isOpen: boolean,
    hours: string,
    nextAvailable: string};
  contact: { phone: string;
    website?: string;
    email?: string}
}
// 知识库查询接口 * interface KnowledgeQuery { query: string, */
  type: "symptom" | "treatment" | "medicine" | "general";
  context?:  {
    userId?: string;
    symptoms?: string[];
    constitution?: string}
}
interface KnowledgeResult { id: string,
  title: string,
  content: string,
  relevance: number,
  source: string,
  category: string,
  tags: string[],
  lastUpdated: string}
// 反馈接口 * interface UserFeedback { userId: string, */
  type: "bug" | "feature" | "improvement" | "general",
  rating: number,
  message: string;
  metadata?: unknown}
// 性能指标接口 * interface PerformanceMetrics { userId: string, */
  renderTime: number,
  memoryUsage: number,
  networkLatency: number,
  errorCount: number,
  userSatisfaction: number}
export class ApiIntegrationService {;
  private eventEmitter: EventEmitter;
  private config: ApiServiceConfig
  constructor(config: Partial<ApiServiceConfig /> = {}) {/    this.config = {
      baseURL: "http://, localhost: 8000", *       timeout: 30000, */
      retries: 3,
      enableCache: true,
      enableRealTime: true,
      ...config
    };
    this.eventEmitter = new EventEmitter();
    this.setupEventListeners()
  }
  private setupEventListeners() {
    // 设置全局事件监听 *     this.eventEmitter.on("api: error", (error) => { */
      console.error("API错误:", error);
    })
    this.eventEmitter.on("api: success", (data); => {
      });
  }
  // ==================== 认证相关 API ==================== *  */
  async login(credentials: { username: string, password: string}) {
    try {
      const response = await authService.login({;
        email: credentials.username,
        password: credentials.passwo;r;d
      ;};)
      this.eventEmitter.emit("api: login:success", response);
      return respon;s;e
    } catch (error) {
      this.eventEmitter.emit("api: login:error", error);
      throw err;o;r;
    }
  }
  async logout() {
    try {
      const response = await authService.logo;u;t;(;)
      this.eventEmitter.emit("api: logout:success");
      return respon;s;e
    } catch (error) {
      this.eventEmitter.emit("api: logout:error", error);
      throw err;o;r;
    }
  }
  async refreshToken() {
    try {
      return await authService.refreshAccessTok;e;n;(;)
    } catch (error) {
      console.error("刷新Token失败:", error);
      throw err;o;r;
    }
  }
  async getCurrentUser() {
    try {
      return await authService.getCurrentUs;e;r;(;)
    } catch (error) {
      console.error("获取当前用户失败:", error);
      throw err;o;r;
    }
  }
  // ==================== 健康数据 API ==================== *  */
  async getHealthData(userId: string,
    timeRange?:  { start: string, end: string}): Promise<HealthData[] />  {
    try {
      const response = await apiClient.get("/health-data", {/        userId,;
        ...timeRan;g;e
      ;};);
      return response.da;t;a
    } catch (error) {
      console.error("获取健康数据失败:", error);
      throw err;o;r
    }
  }
  async saveHealthData(data: Omit<HealthData, "id" | "timestamp" />/  ): Promise<HealthData />  {
    try {
      const response = await apiClient.post("/health-data", {/        ...data,;
        timestamp: new Date().toISOString;(;)
      ;};)
      this.eventEmitter.emit("health: data:saved", response.data);
      return response.da;t;a
    } catch (error) {
      console.error("保存健康数据失败:", error);
      throw err;o;r
    }
  }
  async getHealthMetrics(userId: string, metric: string, period: string) {
    try {
      const response = await apiClient.get(`/health-data/metrics/${metric}`, {/        userId,;
        peri;o;d
      ;};);
      return response.da;t;a
    } catch (error) {
      console.error("获取健康指标失败:", error);
      throw err;o;r
    }
  }
  async exportHealthData(
    userId: string,
    format: "json" | "csv" | "pdf" = "json") {
    try {
      const response = await apiClient.get(`/health-data/export`, {/        userId,;
        form;a;t
      ;};);
      return response.da;t;a
    } catch (error) {
      console.error("导出健康数据失败:", error);
      throw err;o;r;
    }
  }
  // ==================== 智能体相关 API ==================== *  */
  async getAgentStatus(): Promise<AgentStatus[] /> {
    try {
      const response = await apiClient.get("/agents/stat;u;s;";);/      return response.da;t;a
    } catch (error) {
      console.error("获取智能体状态失败:", error);
      throw err;o;r
    }
  }
  async startAgentChat(agentId: string, message: string) {
    try {
      const response = await apiClient.post(`/agents/${agentId}/chat`, {/        message,;
        timestamp: new Date().toISOString;(;)
      ;};)
      this.eventEmitter.emit("agent: chat:started", { agentId, response });
      return response.da;t;a
    } catch (error) {
      console.error("启动智能体对话失败:", error);
      throw err;o;r
    }
  }
  async sendMessageToAgent(agentId: string, message: string, context?: unknown) {
    try {
      const response = await apiClient.post(`/agents/${agentId}/message`, {/        message,;
        context,
        timestamp: new Date().toISOString;(;)
      ;};)
      this.eventEmitter.emit("agent: message:sent", {
        agentId,
        message,
        response
      });
      return response.da;t;a
    } catch (error) {
      console.error("发送消息给智能体失败:", error);
      throw err;o;r;
    }
  }
  async getAgentPerformance(
    agentId: string,
    timeRange?:  { start: string, end: string}) {
    try {
      const response = await apiClient.get(;
        `/agents/${agentId}/performance`,/        timeRa;n;g;e
      ;);
      return response.da;t;a
    } catch (error) {
      console.error("获取智能体性能数据失败:", error);
      throw err;o;r;
    }
  }
  async updateAgentSettings(agentId: string, settings: unknown) {
    try {
      const response = await apiClient.put(;
        `/agents/${agentId}/settings`,/        setti;n;g;s
      ;)
      this.eventEmitter.emit("agent: settings:updated", { agentId, settings });
      return response.da;t;a
    } catch (error) {
      console.error("更新智能体设置失败:", error);
      throw err;o;r
    }
  }
  // ==================== 四诊相关 API ==================== *  */
  async startDiagnosis(type: "look" | "listen" | "inquiry" | "palpation",
    data: unknown;): Promise<DiagnosisResult />  {
    try {
      const response = await apiClient.post(`/diagnosis/${type}`, {/        ...data,;
        timestamp: new Date().toISOString;(;)
      ;};)
      this.eventEmitter.emit("diagnosis: started", { type, response });
      return response.da;t;a
    } catch (error) {
      console.error("启动诊断失败:", error);
      throw err;o;r;
    }
  }
  async getDiagnosisHistory(userId: string,
    limit: number = 10;): Promise<DiagnosisResult[] />  {
    try {
      const response = await apiClient.get("/diagnosis/history", {/        userId,;
        lim;i;t
      ;};);
      return response.da;t;a
    } catch (error) {
      console.error("获取诊断历史失败:", error);
      throw err;o;r;
    }
  }
  async getComprehensiveDiagnosis(userId: string,
    symptoms: string[];): Promise<DiagnosisResult />  {
    try {
      const response = await apiClient.post("/diagnosis/comprehensive", {/        userId,;
        symptoms,
        timestamp: new Date().toISOString;(;)
      ;};)
      this.eventEmitter.emit(
        "diagnosis: comprehensive:completed",
        response.data
      );
      return response.da;t;a
    } catch (error) {
      console.error("获取综合诊断失败:", error);
      throw err;o;r;
    }
  }
  // ==================== 用户设置 API ==================== *  */
  async getUserSettings(userId: string): Promise<UserSettings />  {
    try {
      const response = await apiClient.get(`/users/${userId}/settin;g;s;`;);/      return response.da;t;a
    } catch (error) {
      console.error("获取用户设置失败:", error);
      throw err;o;r;
    }
  }
  async updateUserSettings(userId: string,
    settings: Partial<UserSettings />/);: Promise<UserSettings />  {
    try {
      const response = await apiClient.put(;
        `/users/${userId}/settings`,/        setti;n;g;s
      ;)
      this.eventEmitter.emit("user: settings:updated", {
        userId,
        settings: response.data,
      });
      return response.da;t;a
    } catch (error) {
      console.error("更新用户设置失败:", error);
      throw err;o;r;
    }
  }
  async resetUserSettings(userId: string): Promise<UserSettings />  {
    try {
      const response = await apiClient.post(`/users/${userId}/settings/res;e;t;`;)/      this.eventEmitter.emit("user: settings:reset", { userId });
      return response.da;t;a
    } catch (error) {
      console.error("重置用户设置失败:", error);
      throw err;o;r;
    }
  }
  // ==================== 区块链健康记录 API ==================== *  */
  async saveHealthRecordToBlockchain(userId: string,
    healthData: unknown;): Promise<BlockchainHealthRecord />  {
    try {
      const response = await apiClient.post("/blockchain/health-records", {/        userId,;
        data: healthData,
        timestamp: new Date().toISOString;(;)
      ;};)
      this.eventEmitter.emit("blockchain: record:saved", response.data);
      return response.da;t;a
    } catch (error) {
      console.error("保存区块链健康记录失败:", error);
      throw err;o;r;
    }
  }
  async getBlockchainHealthRecords(userId: string;);: Promise<BlockchainHealthRecord[] />  {
    try {
      const response = await apiClient.get(;
        `/blockchain/health-records/${userId;};`;/      ;);
      return response.da;t;a
    } catch (error) {
      console.error("获取区块链健康记录失败:", error);
      throw err;o;r;
    }
  }
  async verifyHealthRecord(recordId: string;): Promise< {, verified: boolean, details: unknown}> {
    try {
      const response = await apiClient.post(`/blockchain/verify/${recordI;d;};`;);/      return response.da;t;a
    } catch (error) {
      console.error("验证健康记录失败:", error);
      throw err;o;r;
    }
  }
  // ==================== 医疗资源 API ==================== *  */
  async searchMedicalResources(query: {
    type?: string;
    location?:  { lat: number, lng: number, radius: number};
    services?: string[];
  }): Promise<MedicalResource[] />  {
    try {
      const response = await apiClient.get("/medical-resources/search", qu;e;r;y;);/      return response.da;t;a
    } catch (error) {
      console.error("搜索医疗资源失败:", error);
      throw err;o;r;
    }
  }
  async getMedicalResourceDetails(resourceId: string;): Promise<MedicalResource />  {
    try {
      const response = await apiClient.get(`/medical-resources/${resourceI;d;};`;);/      return response.da;t;a
    } catch (error) {
      console.error("获取医疗资源详情失败:", error);
      throw err;o;r;
    }
  }
  async bookMedicalAppointment(
    resourceId: string,
    appointmentData: { userId: string,
      serviceType: string,
      preferredTime: string,
      notes?: string}
  ) {
    try {
      const response = await apiClient.post(;
        `/medical-resources/${resourceId}/appointments`,/        {;
          ...appointmentData,
          timestamp: new Date().toISOString;(;)
        ;}
      ;)
      this.eventEmitter.emit("appointment: booked", response.data);
      return response.da;t;a
    } catch (error) {
      console.error("预约医疗服务失败:", error);
      throw err;o;r;
    }
  }
  // ==================== 知识库 API ==================== *  */
  async searchKnowledge(query: KnowledgeQuery): Promise<KnowledgeResult[] />  {
    try {
      const response = await apiClient.post("/knowledge/search", qu;e;r;y;);/      return response.da;t;a
    } catch (error) {
      console.error("搜索知识库失败:", error);
      throw err;o;r;
    }
  }
  async getKnowledgeDetails(knowledgeId: string): Promise<KnowledgeResult />  {
    try {
      const response = await apiClient.get(`/knowledge/${knowledgeI;d;};`;);/      return response.da;t;a
    } catch (error) {
      console.error("获取知识详情失败:", error);
      throw err;o;r;
    }
  }
  async getRecommendedKnowledge(userId: string,
    context?: unknown;
  );: Promise<KnowledgeResult[] />  {
    try {
      const response = await apiClient.get(;
        `/knowledge/recommendations/${userId}`,/        { conte;x;t ;}
      ;);
      return response.da;t;a
    } catch (error) {
      console.error("获取推荐知识失败:", error);
      throw err;o;r
    }
  }
  // ==================== 机器学习 API ==================== *  */
  async trainPersonalModel(userId: string, trainingData: unknown) {
    try {
      const response = await apiClient.post(`/ml/models/${userId}/train`, {/        data: trainingData,;
        timestamp: new Date().toISOString;(;)
      ;};)
      this.eventEmitter.emit("ml: training:started", { userId, response });
      return response.da;t;a
    } catch (error) {
      console.error("训练个人模型失败:", error);
      throw err;o;r
    }
  }
  async getModelPrediction(userId: string, inputData: unknown) {
    try {
      const response = await apiClient.post(`/ml/models/${userId}/predict`, {/        input: inputData,;
        timestamp: new Date().toISOString;(;)
      ;};);
      return response.da;t;a
    } catch (error) {
      console.error("获取模型预测失败:", error);
      throw err;o;r
    }
  }
  async getModelPerformance(userId: string) {
    try {
      const response = await apiClient.get(`/ml/models/${userId}/performan;c;e;`;);/      return response.da;t;a
    } catch (error) {
      console.error("获取模型性能失败:", error);
      throw err;o;r
    }
  }
  // ==================== 无障碍服务 API ==================== *  */
  async getAccessibilitySettings(userId: string) {
    try {
      const response = await apiClient.get(`/accessibility/settings/${userI;d;};`;);/      return response.da;t;a
    } catch (error) {
      console.error("获取无障碍设置失败:", error);
      throw err;o;r;
    }
  }
  async updateAccessibilitySettings(userId: string, settings: unknown) {
    try {
      const response = await apiClient.put(;
        `/accessibility/settings/${userId}`,/        setti;n;g;s
      ;)
      this.eventEmitter.emit("accessibility: settings:updated", {
        userId,
        settings
      });
      return response.da;t;a
    } catch (error) {
      console.error("更新无障碍设置失败:", error);
      throw err;o;r
    }
  }
  async generateAccessibilityReport(userId: string) {
    try {
      const response = await apiClient.get(`/accessibility/report/${userI;d;};`;);/      return response.da;t;a
    } catch (error) {
      console.error("生成无障碍报告失败:", error);
      throw err;o;r
    }
  }
  // ==================== 生态服务 API ==================== *  */
  async getEcoServices() {
    try {
      const response = await apiClient.get("/eco-servic;e;s;";);/      return response.da;t;a
    } catch (error) {
      console.error("获取生态服务失败:", error);
      throw err;o;r
    }
  }
  async subscribeToEcoService(userId: string, serviceId: string, plan: string) {
    try {
      const response = await apiClient.post(;
        `/eco-services/${serviceId}/subscribe`,/        {
          userId,
          plan,
          timestamp: new Date().toISOString;(;)
        ;}
      ;)
      this.eventEmitter.emit("eco: service:subscribed", {
        userId,
        serviceId,
        plan
      });
      return response.da;t;a
    } catch (error) {
      console.error("订阅生态服务失败:", error);
      throw err;o;r;
    }
  }
  async getEcoServiceUsage(userId: string, serviceId: string) {
    try {
      const response = await apiClient.get(;
        `/eco-services/${serviceId}/usage/${userId;};`;/      ;);
      return response.da;t;a
    } catch (error) {
      console.error("获取生态服务使用情况失败:", error);
      throw err;o;r
    }
  }
  // ==================== 反馈和支持 API ==================== *  */
  async submitFeedback(feedback: UserFeedback) {
    try {
      const response = await apiClient.post("/feedback", {/        ...feedback,;
        timestamp: new Date().toISOString;(;)
      ;};)
      this.eventEmitter.emit("feedback: submitted", response.data);
      return response.da;t;a
    } catch (error) {
      console.error("提交反馈失败:", error);
      throw err;o;r
    }
  }
  async getFeedbackHistory(userId: string) {
    try {
      const response = await apiClient.get(`/feedback/history/${userI;d;};`;);/      return response.da;t;a
    } catch (error) {
      console.error("获取反馈历史失败:", error);
      throw err;o;r
    }
  }
  async getSupportTickets(userId: string) {
    try {
      const response = await apiClient.get(`/support/tickets/${userI;d;};`;);/      return response.da;t;a
    } catch (error) {
      console.error("获取支持工单失败:", error);
      throw err;o;r
    }
  }
  async createSupportTicket(ticket: { userId: string,
    subject: string,
    description: string,
    priority: "low" | "medium" | "high" | "urgent",
    category: string}) {
    try {
      const response = await apiClient.post("/support/tickets", {/        ...ticket,;
        timestamp: new Date().toISOString;(;)
      ;};)
      this.eventEmitter.emit("support: ticket:created", response.data);
      return response.da;t;a
    } catch (error) {
      console.error("创建支持工单失败:", error);
      throw err;o;r
    }
  }
  // ==================== 系统监控 API ==================== *  */
  async getSystemHealth() {
    try {
      const response = await apiClient.get("/system/heal;t;h;";);/      return response.da;t;a
    } catch (error) {
      console.error("获取系统健康状态失败:", error);
      throw err;o;r
    }
  }
  async getSystemMetrics() {
    try {
      const response = await apiClient.get("/system/metri;c;s;";);/      return response.da;t;a
    } catch (error) {
      console.error("获取系统指标失败:", error);
      throw err;o;r
    }
  }
  async reportPerformanceMetrics(metrics: PerformanceMetrics) {
    try {
      const response = await apiClient.post("/system/performance", {/        ...metrics,;
        timestamp: new Date().toISOString;(;)
      ;};);
      return response.da;t;a
    } catch (error) {
      console.error("报告性能指标失败:", error);
      throw err;o;r;
    }
  }
  // ==================== 实用工具方法 ==================== *  */
  // /    批量API请求  async batchRequest(
    requests: Array<{, name: string, request: () => Promise<any>   }>
  ) {
  // 性能监控
  const performanceMonitor = usePerformanceMonitor('ApiIntegrationService', {;
    trackRender: true,
    trackMemory: false,
    warnThreshold: 100, // ms ;};);
    try {
      const results = await Promise.allSettled(;
        requests.map(async ({ name, reque;s;t ;};); => {
          try {
            const result = await reque;s;t;(;);
            return { name, success: true, data: resu;l;t ;};
          } catch (error) {
            return { name, success: false, erro;r ;};
          }
        })
      );
      return results.map((result, inde;x;) => {
        if (result.status === "fulfilled") {
          return result.val;u;e;
        } else {
          return {
            name: requests[index].name,
            success: false,
            error: result.reaso;n
          ;};
        }
      })
    } catch (error) {
      console.error("批量请求失败:", error);
      throw err;o;r;
    }
  }
  // /    健康检查  async healthCheck(): Promise<boolean> {
    try {
      const response = await apiClient.get("/heal;t;h;";);/      return response.succe;s;s
    } catch (error) {
      console.error("健康检查失败:", error);
      return fal;s;e
    }
  }
  // /    获取API版本信息  async getApiVersion() {
    try {
      const response = await apiClient.get("/versi;o;n;";);/      return response.da;t;a
    } catch (error) {
      console.error("获取API版本失败:", error);
      throw err;o;r;
    }
  }
  // /    事件监听  on(event: string, listener: (...args: unknown[]); => void) {
    this.eventEmitter.on(event, listener);
  }
  // /    移除事件监听  off(event: string, listener: (...args: unknown[]); => void) {
    this.eventEmitter.off(event, listener);
  }
  // /    销毁服务  destroy() {
    this.eventEmitter.removeAllListeners();
  }
}
// 创建单例实例 * export const apiIntegrationService = new ApiIntegrationService;(;); */;