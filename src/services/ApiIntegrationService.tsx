./apiClient";/""/;,"/g"/;
import React from "react";";
API服务配置接口 * interface ApiServiceConfig {baseURL: string}timeout: number,;
retries: number,;
enableCache: boolean,;
}
}
  const enableRealTime = boolean;}
}
// 健康数据接口 * interface HealthData {/;,}id: string,;,/g,/;
  userId: string,;
metrics: {heartRate: number,;}}
}
  bloodPressure: { systolic: number, diastolic: number;}
}
sleepQuality: number,;
stressLevel: number,;
activityLevel: number,;
const nutritionScore = number;};
constitution: {type: string,;}}
    percentage: number,}
    const description = string;}[];
const timestamp = string;}
// 智能体状态接口 * interface AgentStatus {/;,}id: string,";,"/g,"/;
  name: string,";,"";
status: "online" | "offline" | "busy";",";
workload: number,;
performance: {accuracy: number}responseTime: number,;
}
}
  const userSatisfaction = number;}
}
  currentTask?: string;
const lastUpdate = string;}
// 诊断结果接口 * interface DiagnosisResult {/;,}id: string,";,"/g,"/;
  userId: string,";,"";
type: "look" | "listen" | "inquiry" | "palpation" | "comprehensive";",";
results: {symptoms: string[]}constitution: string,;
recommendations: string[],;
}
}
  const confidence = number;}
}
  const timestamp = string;}
// 用户设置接口 * interface UserSettings {/;,}accessibility: {screenReader: boolean}highContrast: boolean,;,/g,/;
  largeText: boolean,;
reduceMotion: boolean,;
voiceOver: boolean,;
}
}
  const hapticFeedback = boolean;}";"";
}";,"";
personalization: {theme: "light" | "dark" | "auto";","";,}language: "zh" | "en";",";
fontSize: number,;
animationSpeed: number,;
notifications: {health: boolean,;
}
      agents: boolean,}
      const system = boolean;}
  };
privacy: {dataSharing: boolean,;}}
    analytics: boolean,}
    const locationTracking = boolean;};
}
// 区块链健康记录接口 * interface BlockchainHealthRecord {/;,}id: string,;,/g,/;
  userId: string,;
dataHash: string,;
timestamp: string,;
signature: string,;
verified: boolean,;
metadata: {dataType: string}source: string,;
}
}
  const version = string;}
}
}
// 医疗资源接口 * interface MedicalResource {/;}";,"/g,"/;
  id: string,";,"";
type: "hospital" | "clinic" | "pharmacy" | "specialist";",";
name: string,;
location: {address: string,;}}
}
  coordinates: { lat: number, lng: number;}
}
  };
services: string[],;
rating: number,;
availability: {isOpen: boolean,;}}
    hours: string,}
    const nextAvailable = string;};
const contact = {phone: string;}}
    website?: string;}
    email?: string}
}
// 知识库查询接口 * interface KnowledgeQuery {/;}";,"/g,"/;
  query: string,";,"";
const type = "symptom" | "treatment" | "medicine" | "general";";,"";
context?: {userId?: string;,}symptoms?: string[];
}
}
    constitution?: string;}
}
};
interface KnowledgeResult {id: string}title: string,;
content: string,;
relevance: number,;
source: string,;
category: string,;
tags: string[],;
}
}
  const lastUpdated = string;}
}
// 反馈接口 * interface UserFeedback {/;}";,"/g,"/;
  userId: string,";,"";
type: "bug" | "feature" | "improvement" | "general";",";
rating: number,;
const message = string;
}
}
  metadata?: unknown;}
}
// 性能指标接口 * interface PerformanceMetrics {/;,}userId: string,;,/g,/;
  renderTime: number,;
memoryUsage: number,;
networkLatency: number,;
errorCount: number,;
}
}
  const userSatisfaction = number;}
};
export class ApiIntegrationService {private eventEmitter: EventEmitter;}}
}
  private config: ApiServiceConfig;}";,"";
constructor(config: Partial<ApiServiceConfig  /> = {;}) {/;}/        this.config = {"/;,}baseURL: "http: timeout: 30000;",";,"/g,"/;
  retries: 3,;
enableCache: true,;
const enableRealTime = true;
}
      ...config;}
    }
    this.eventEmitter = new EventEmitter();
this.setupEventListeners();
  }";,"";
private setupEventListeners() {"}";
this.eventEmitter.on("api: error", (error) => {;})";"";
      });";,"";
this.eventEmitter.on("api: success", (data); => {})";"";
      });
  }
  async: login(credentials: { username: string, password: string;}) {try {}}
      const: response = await authService.login({email: credentials.username,)}";,"";
const password = credentials.passwo;r;d;};);";,"";
this.eventEmitter.emit("api: login:success", response);";,"";
return respon;s;e;";"";
    } catch (error) {";,}this.eventEmitter.emit("api: login:error", error);";"";
}
      const throw = error;}
    }
  }
  const async = logout() {try {";,}const response = await authService.logo;u;t;(;);";,"";
this.eventEmitter.emit("api: logout:success");";"";
}
      return respon;s;e;}";"";
    } catch (error) {";,}this.eventEmitter.emit("api: logout:error", error);";"";
}
      const throw = error;}
    }
  }
  const async = refreshToken() {try {}}
      return await authService.refreshAccessTok;e;n;(;)}
    } catch (error) {}}
      const throw = error;}
    }
  }
  const async = getCurrentUser() {try {}}
      return await authService.getCurrentUs;e;r;(;)}
    } catch (error) {}}
      const throw = error;}
    }
  }
  async: getHealthData(userId: string,);
timeRange?: { start: string; end: string;}): Promise<HealthData[] /    >  {/;}";"/g"/;
}
    try {"}";
response: await apiClient.get("/health-data", {/            userId,...timeRan;g;e;};);"/;,"/g"/;
return response.da;t;a;
    } catch (error) {}}
      const throw = err;o;r;}
    }";"";
  }";,"";
async: saveHealthData(data: Omit<HealthData, "id" | "timestamp"  />/  ): Promise<HealthData /    >  {/;}";"/g"/;
}
    try {"}";
response: await apiClient.post("/health-data", {/            ...data,timestamp: new Date().toISOString;};)"/;,"/g"/;
this.eventEmitter.emit("health: data:saved", response.data);";,"";
return response.da;t;a;
    } catch (error) {}}
      const throw = err;o;r;}
    }
  }
  async: getHealthMetrics(userId: string, metric: string, period: string) {}}
    try {}
      response: await apiClient.get(`/health-data/metrics/${metric;}`, {/            userId,peri;o;d;};);```/`;,`/g`/`;
return response.da;t;a;
    } catch (error) {}}
      const throw = err;o;r;}
    }
  }
  const async = exportHealthData()";,"";
userId: string,";,"";
format: "json" | "csv" | "pdf" = "json") {";}}"";
    try {}
      response: await apiClient.get(`/health-data/export`, {/            userId,form;a;t;};);```/`;,`/g`/`;
return response.da;t;a;
    } catch (error) {}}
      const throw = error;}
    }
  }
  const async = getAgentStatus(): Promise<AgentStatus[] /    > {/;}";,"/g"/;
try {";}}"";
      const response = await apiClient.get("/agents/statu;s;";);/          return response.da;t;a;"}""/;"/g"/;
    } catch (error) {}}
      const throw = err;o;r;}
    }
  }
  async: startAgentChat(agentId: string, message: string) {}}
    try {}";,"";
response: await apiClient.post(`/agents/${agentId;}/chat`, {/            message,timestamp: new Date().toISOString;};)``"/`;,`/g`/`;
this.eventEmitter.emit("agent: chat:started", { agentId, response ;});";,"";
return response.da;t;a;
    } catch (error) {}}
      const throw = err;o;r;}
    }
  }
  async: sendMessageToAgent(agentId: string, message: string, context?: unknown) {}}
    try {}
      response: await apiClient.post(`/agents/${agentId;}/message`, {/            message,context,)``}"/`;,`/g`/`;
const timestamp = new Date().toISOString;};)";,"";
this.eventEmitter.emit("agent: message:sent", {)";,}agentId,);,"";
message,);
}
        response;)}
      });
return response.da;t;a;
    } catch (error) {}}
      const throw = error;}
    }
  }
  const async = getAgentPerformance();
const agentId = string;
timeRange?: { start: string; end: string;}) {try {}}
      const response = await apiClient.get(;)}
        `/agents/${agentId}/performance`,/            timeRa;n;g;e;);```/`;,`/g`/`;
return response.da;t;a;
    } catch (error) {}}
      const throw = error;}
    }
  }
  async: updateAgentSettings(agentId: string, settings: unknown) {try {}}
      const response = await apiClient.put(;)}";"";
        `/agents/${agentId}/settings`,/            setti;n;g;s;);``"/`;,`/g`/`;
this.eventEmitter.emit("agent: settings:updated", { agentId, settings ;});";,"";
return response.da;t;a;
    } catch (error) {}}
      const throw = err;o;r;}
    }";"";
  }";,"";
async: startDiagnosis(type: "look" | "listen" | "inquiry" | "palpation",)";,"";
const data = unknown): Promise<DiagnosisResult /    >  {/;}}/g/;
    try {}";,"";
response: await apiClient.post(`/diagnosis/${type;}`, {/            ...data,timestamp: new Date().toISOString;};)``"/`;,`/g`/`;
this.eventEmitter.emit("diagnosis: started", { type, response ;});";,"";
return response.da;t;a;
    } catch (error) {}}
      const throw = error;}
    }
  }
  async: getDiagnosisHistory(userId: string,);
limit: number = 10;): Promise<DiagnosisResult[] /    >  {/;}";"/g"/;
}
    try {"}";
response: await apiClient.get("/diagnosis/history", {/            userId,lim;i;t;};);"/;,"/g"/;
return response.da;t;a;
    } catch (error) {}}
      const throw = error;}
    }
  }
  async: getComprehensiveDiagnosis(userId: string,);
const symptoms = string[];): Promise<DiagnosisResult /    >  {/;}";,"/g"/;
try {";}}"";
      const: response = await apiClient.post("/diagnosis/comprehensive", {/            userId,symptoms,)"}""/;,"/g"/;
const timestamp = new Date().toISOString;};)";,"";
this.eventEmitter.emit()";"";
        "diagnosis: comprehensive:completed";";,"";
response.data;
      );
return response.da;t;a;
    } catch (error) {}}
      const throw = error;}
    }
  }
  const async = getUserSettings(userId: string): Promise<UserSettings /    >  {/;}}/g/;
    try {}
      const response = await apiClient.get(`/users/${userId;}/setting;s;`;);/          return response.da;t;a;```/`;`/g`/`;
    } catch (error) {}}
      const throw = error;}
    }
  }
  async: updateUserSettings(userId: string,);
const settings = Partial<UserSettings  />/);: Promise<UserSettings /    >  {/;,}try {}}/g/;
      const response = await apiClient.put(;)}";"";
        `/users/${userId}/settings`,/            setti;n;g;s;);``"/`;,`/g`/`;
this.eventEmitter.emit("user: settings:updated", {)")"";}}"";
        userId,)}
        const settings = response.data;});
return response.da;t;a;
    } catch (error) {}}
      const throw = error;}
    }
  }
  const async = resetUserSettings(userId: string): Promise<UserSettings /    >  {/;}";"/g"/;
}
    try {"}";
response: await apiClient.post(`/users/${userId;}/settings/res;e;t;`;)/          this.eventEmitter.emit("user: settings:reset", { userId ;});"/`;,`/g`/`;
return response.da;t;a;
    } catch (error) {}}
      const throw = error;}
    }
  }
  async: saveHealthRecordToBlockchain(userId: string,);
const healthData = unknown): Promise<BlockchainHealthRecord /    >  {/;}";,"/g"/;
try {";}}"";
      const: response = await apiClient.post("/blockchain/health-records", {/            userId,data: healthData,)"}""/;,"/g"/;
const timestamp = new Date().toISOString;};)";,"";
this.eventEmitter.emit("blockchain: record:saved", response.data);";,"";
return response.da;t;a;
    } catch (error) {}}
      const throw = error;}
    }
  }
  const async = getBlockchainHealthRecords(userId: string;);: Promise<BlockchainHealthRecord[] /    >  {/;,}try {}}/g/;
      const response = await apiClient.get(;)}
        `/blockchain/health-records/    ${userId;};`);```/`;,`/g`/`;
return response.da;t;a;
    } catch (error) {}}
      const throw = error;}
    }
  }
  async: verifyHealthRecord(recordId: string;): Promise< { verified: boolean, details: unknown;}> {}}
    try {}
      const response = await apiClient.post(`/blockchain/verify/${recordI;d;};`;);/          return response.da;t;a;```/`;`/g`/`;
    } catch (error) {}}
      const throw = error;}
    }
  }
  const async = searchMedicalResources(query: {)}
    type?: string;)}
    location?: { lat: number; lng: number, radius: number;};);
services?: string[];);
  }): Promise<MedicalResource[] /    >  {/;}";,"/g"/;
try {";}}"";
      response: await apiClient.get("/medical-resources/search", qu;e;r;y;);/          return response.da;t;a;"}""/;"/g"/;
    } catch (error) {}}
      const throw = error;}
    }
  }
  const async = getMedicalResourceDetails(resourceId: string;): Promise<MedicalResource /    >  {/;}}/g/;
    try {}
      const response = await apiClient.get(`/medical-resources/${resourceI;d;};`;);/          return response.da;t;a;```/`;`/g`/`;
    } catch (error) {}}
      const throw = error;}
    }
  }
  const async = bookMedicalAppointment();
resourceId: string,;
appointmentData: {userId: string}serviceType: string,;
}
      const preferredTime = string;}
      notes?: string}
  ) {try {}}
      const response = await apiClient.post(;)}
        `/medical-resources/${resourceId}/appointments`,/            {...appointmentData,``}``/`;,`/g`/`;
const timestamp = new Date().toISOString;}";"";
      ;)";,"";
this.eventEmitter.emit("appointment: booked", response.data);";,"";
return response.da;t;a;
    } catch (error) {}}
      const throw = error;}
    }
  }
  const async = searchKnowledge(query: KnowledgeQuery): Promise<KnowledgeResult[] /    >  {/;}";,"/g"/;
try {";}}"";
      response: await apiClient.post("/knowledge/search", que;r;y;);/          return response.da;t;a;"}""/;"/g"/;
    } catch (error) {}}
      const throw = error;}
    }
  }
  const async = getKnowledgeDetails(knowledgeId: string): Promise<KnowledgeResult /    >  {/;}}/g/;
    try {}
      const response = await apiClient.get(`/knowledge/${knowledgeI;d;};`;);/          return response.da;t;a;```/`;`/g`/`;
    } catch (error) {}}
      const throw = error;}
    }
  }
  async: getRecommendedKnowledge(userId: string,);
context?: unknown;
  );: Promise<KnowledgeResult[] /    >  {/;,}try {}}/g/;
      const response = await apiClient.get(;)}
        `/knowledge/recommendations/${userId}`,/            { conte;x;t ;}```/`;`/g`/`;
      ;);
return response.da;t;a;
    } catch (error) {}}
      const throw = err;o;r;}
    }
  }
  async: trainPersonalModel(userId: string, trainingData: unknown) {}}
    try {}";,"";
response: await apiClient.post(`/ml/models/${userId;}/train`, {/            data: trainingData,timestamp: new Date().toISOString;};)``"/`;,`/g`/`;
this.eventEmitter.emit("ml: training:started", { userId, response ;});";,"";
return response.da;t;a;
    } catch (error) {}}
      const throw = err;o;r;}
    }
  }
  async: getModelPrediction(userId: string, inputData: unknown) {}}
    try {}
      response: await apiClient.post(`/ml/models/${userId;}/predict`, {/            input: inputData,timestamp: new Date().toISOString;};);```/`;,`/g`/`;
return response.da;t;a;
    } catch (error) {}}
      const throw = err;o;r;}
    }
  }
  const async = getModelPerformance(userId: string) {}}
    try {}
      const response = await apiClient.get(`/ml/models/${userId;}/performan;c;e;`;);/          return response.da;t;a;```/`;`/g`/`;
    } catch (error) {}}
      const throw = err;o;r;}
    }
  }
  const async = getAccessibilitySettings(userId: string) {}}
    try {}
      const response = await apiClient.get(`/accessibility/settings/${userId;};`;);/          return response.da;t;a;```/`;`/g`/`;
    } catch (error) {}}
      const throw = error;}
    }
  }
  async: updateAccessibilitySettings(userId: string, settings: unknown) {try {}}
      const response = await apiClient.put(;)}";"";
        `/accessibility/settings/${userId}`,/            setti;n;g;s;);``"/`;,`/g`/`;
this.eventEmitter.emit("accessibility: settings:updated", {)")"";,}userId,);"";
}
        settings;)}
      });
return response.da;t;a;
    } catch (error) {}}
      const throw = err;o;r;}
    }
  }
  const async = generateAccessibilityReport(userId: string) {}}
    try {}
      const response = await apiClient.get(`/accessibility/report/${userI;d;};`;);/          return response.da;t;a;```/`;`/g`/`;
    } catch (error) {}}
      const throw = err;o;r;}
    }
  }
  const async = getEcoServices() {";,}try {";}}"";
      const response = await apiClient.get("/eco-service;s;";);/          return response.da;t;a;"}""/;"/g"/;
    } catch (error) {}}
      const throw = err;o;r;}
    }
  }
  async: subscribeToEcoService(userId: string, serviceId: string, plan: string) {try {}}
      const response = await apiClient.post(;)}
        `/eco-services/${serviceId}/subscribe`,/            {/`;}````;,`/g`/`;
userId,;
}
          plan,}
          const timestamp = new Date().toISOString;}";"";
      ;)";,"";
this.eventEmitter.emit("eco: service:subscribed", {)";,}userId,);,"";
serviceId,);
}
        plan;)}
      });
return response.da;t;a;
    } catch (error) {}}
      const throw = error;}
    }
  }
  async: getEcoServiceUsage(userId: string, serviceId: string) {try {}}
      const response = await apiClient.get(;)}
        `/eco-services/${serviceId}/usage/    ${userId;};`);```/`;,`/g`/`;
return response.da;t;a;
    } catch (error) {}}
      const throw = err;o;r;}
    }
  }
  const async = submitFeedback(feedback: UserFeedback) {";}}"";
    try {"}";
response: await apiClient.post("/feedback", {/            ...feedback,timestamp: new Date().toISOString;};)"/;,"/g"/;
this.eventEmitter.emit("feedback: submitted", response.data);";,"";
return response.da;t;a;
    } catch (error) {}}
      const throw = err;o;r;}
    }
  }
  const async = getFeedbackHistory(userId: string) {}}
    try {}
      const response = await apiClient.get(`/feedback/history/${userI;d;};`;);/          return response.da;t;a;```/`;`/g`/`;
    } catch (error) {}}
      const throw = err;o;r;}
    }
  }
  const async = getSupportTickets(userId: string) {}}
    try {}
      const response = await apiClient.get(`/support/tickets/${userI;d;};`;);/          return response.da;t;a;```/`;`/g`/`;
    } catch (error) {}}
      const throw = err;o;r;}
    }
  }
  async: createSupportTicket(ticket: {)userId: string,);,}subject: string,";,"";
description: string,";"";
}
    priority: "low" | "medium" | "high" | "urgent";","}";
const category = string;}) {";}}"";
    try {"}";
response: await apiClient.post("/support/tickets", {/            ...ticket,timestamp: new Date().toISOString;};)"/;,"/g"/;
this.eventEmitter.emit("support: ticket:created", response.data);";,"";
return response.da;t;a;
    } catch (error) {}}
      const throw = err;o;r;}
    }
  }
  const async = getSystemHealth() {";,}try {";}}"";
      const response = await apiClient.get("/system/healt;h;";);/          return response.da;t;a;"}""/;"/g"/;
    } catch (error) {}}
      const throw = err;o;r;}
    }
  }
  const async = getSystemMetrics() {";,}try {";}}"";
      const response = await apiClient.get("/system/metri;c;s;";);/          return response.da;t;a;"}""/;"/g"/;
    } catch (error) {}}
      const throw = err;o;r;}
    }
  }
  const async = reportPerformanceMetrics(metrics: PerformanceMetrics) {";}}"";
    try {"}";
response: await apiClient.post("/system/performance", {/            ...metrics,timestamp: new Date().toISOString;};);"/;,"/g"/;
return response.da;t;a;
    } catch (error) {}}
      const throw = error;}
    }
  }
  // 批量API请求  async batchRequest()/;,/g,/;
  requests: Array<{ name: string, request: () => Promise<any>   ;}>;
  ) {";}  // 性能监控"/;,"/g,"/;
  const: performanceMonitor = usePerformanceMonitor(ApiIntegrationService", {")";,}trackRender: true,;"";
}
    trackMemory: false,}
    warnThreshold: 100, // ms ;};);/;,/g/;
try {}}
      const results = await Promise.allSettled(;)}
        requests.map(async ({ name, reque;s;t ;};); => {});
try {}}
            const result = await reque;s;t;}
            return { name, success: true, data: resu;l;t ;};
          } catch (error) {}
            return { name, success: false, erro;r ;};
          }
        });
      );";,"";
return results.map(result, inde;x;) => {})";,"";
if (result.status === "fulfilled") {";}}"";
          return result.val;u;e;}
        } else {}
          return {name: requests[index].name,success: false,error: result.reaso;n;};
        }
      });
    } catch (error) {}}
      const throw = error;}
    }
  }
  // 健康检查  async healthCheck(): Promise<boolean> {/;}";,"/g"/;
try {";}}"";
      const response = await apiClient.get("/healt;h;";);/          return response.succe;s;s;"}""/;"/g"/;
    } catch (error) {}}
      return fal;s;e;}
    }
  }
  // 获取API版本信息  async getApiVersion() {/;}";,"/g"/;
try {";}}"";
      const response = await apiClient.get("/versio;n;";);/          return response.da;t;a;"}""/;"/g"/;
    } catch (error) {}}
      const throw = error;}
    }
  }
  // 事件监听  on(event: string, listener: (...args: unknown[]) => void) {/;}}/g/;
    this.eventEmitter.on(event, listener);}
  }
  // 移除事件监听  off(event: string, listener: (...args: unknown[]) => void) {/;}}/g/;
    this.eventEmitter.off(event, listener);}
  }
  // 销毁服务  destroy() {/;}}/g/;
    this.eventEmitter.removeAllListeners();}
  }
}";"";
//   ;"/"/g"/;