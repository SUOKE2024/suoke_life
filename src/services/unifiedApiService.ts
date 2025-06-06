import { apiClient, ApiResponse } from './apiClient';
import { API_GATEWAY_CONFIG } from '../constants/config';

/**
 * 统一API服务
 * 所有微服务API调用的统一入口，确保通过API Gateway路由
 */
export class UnifiedApiService {
  
  // ==================== 认证服务 API ====================
  
  async login(credentials: { email: string; password: string; deviceId?: string; rememberMe?: boolean }) {
    return apiClient.post('AUTH', '/login', credentials);
  }

  async register(userData: { username: string; email: string; password: string; phone?: string; deviceId?: string }) {
    return apiClient.post('AUTH', '/register', userData);
  }

  async logout() {
    return apiClient.post('AUTH', '/logout');
  }

  async refreshToken(refreshToken: string) {
    return apiClient.post('AUTH', '/refresh', { refreshToken });
  }

  async getCurrentUser() {
    return apiClient.get('AUTH', '/me');
  }

  async forgotPassword(email: string) {
    return apiClient.post('AUTH', '/forgot-password', { email });
  }

  async resetPassword(data: { email: string; code: string; newPassword: string }) {
    return apiClient.post('AUTH', '/reset-password', data);
  }

  async changePassword(oldPassword: string, newPassword: string) {
    return apiClient.post('AUTH', '/change-password', { oldPassword, newPassword });
  }

  async verifyPassword(password: string) {
    return apiClient.post('AUTH', '/verify-password', { password });
  }

  async checkEmailExists(email: string) {
    return apiClient.get('AUTH', `/check-email?email=${encodeURIComponent(email)}`);
  }

  async checkUsernameExists(username: string) {
    return apiClient.get('AUTH', `/check-username?username=${encodeURIComponent(username)}`);
  }

  // ==================== 用户服务 API ====================
  
  async getUserProfile(userId?: string) {
    const endpoint = userId ? `/profile/${userId}` : '/profile';
    return apiClient.get('USER', endpoint);
  }

  async updateUserProfile(profileData: any) {
    return apiClient.put('USER', '/profile', profileData);
  }

  async getUserSettings() {
    return apiClient.get('USER', '/settings');
  }

  async updateUserSettings(settings: any) {
    return apiClient.put('USER', '/settings', settings);
  }

  async getUserPreferences() {
    return apiClient.get('USER', '/preferences');
  }

  async updateUserPreferences(preferences: any) {
    return apiClient.put('USER', '/preferences', preferences);
  }

  async getHealthProfile() {
    return apiClient.get('USER', '/health-profile');
  }

  async updateHealthProfile(healthProfile: any) {
    return apiClient.put('USER', '/health-profile', healthProfile);
  }

  // ==================== 健康数据服务 API ====================
  
  async getHealthData(params?: { type?: string; startDate?: string; endDate?: string; limit?: number }) {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          queryParams.append(key, value.toString());
        }
      });
    }
    const endpoint = queryParams.toString() ? `/data?${queryParams.toString()}` : '/data';
    return apiClient.get('HEALTH_DATA', endpoint);
  }

  async addHealthData(data: any) {
    return apiClient.post('HEALTH_DATA', '/data', data);
  }

  async addHealthDataBatch(dataList: any[]) {
    return apiClient.post('HEALTH_DATA', '/data/batch', { data: dataList });
  }

  async updateHealthData(id: string, updates: any) {
    return apiClient.put('HEALTH_DATA', `/data/${id}`, updates);
  }

  async deleteHealthData(id: string) {
    return apiClient.delete('HEALTH_DATA', `/data/${id}`);
  }

  async getHealthMetrics(timeRange: string) {
    return apiClient.get('HEALTH_DATA', `/metrics?timeRange=${timeRange}`);
  }

  async exportHealthData(format: string = 'json') {
    return apiClient.get('HEALTH_DATA', `/export?format=${format}`);
  }

  async syncHealthData() {
    return apiClient.get('HEALTH_DATA', '/sync');
  }

  // ==================== 智能体服务 API ====================
  
  async getAgentStatus(agentId?: string) {
    const endpoint = agentId ? `/status/${agentId}` : '/status';
    return apiClient.get('AGENTS', endpoint);
  }

  async startAgentChat(agentId: string, userId: string) {
    return apiClient.post('AGENTS', '/chat/start', { agentId, userId });
  }

  async sendAgentMessage(sessionId: string, message: string, type: string = 'text') {
    return apiClient.post('AGENTS', '/chat/message', { sessionId, message, type });
  }

  async endAgentChat(sessionId: string) {
    return apiClient.post('AGENTS', '/chat/end', { sessionId });
  }

  async getAgentPerformance(agentId?: string) {
    const endpoint = agentId ? `/performance/${agentId}` : '/performance';
    return apiClient.get('AGENTS', endpoint);
  }

  async updateAgentSettings(agentId: string, settings: any) {
    return apiClient.put('AGENTS', `/settings/${agentId}`, settings);
  }

  // ==================== 五诊服务 API (原四诊升级) ====================
  
  // 传统四诊方法
  async performLookDiagnosis(imageData: any) {
    return apiClient.post('DIAGNOSIS', '/look', imageData);
  }

  async performListenDiagnosis(audioData: any) {
    return apiClient.post('DIAGNOSIS', '/listen', audioData);
  }

  async performInquiryDiagnosis(inquiryData: any) {
    return apiClient.post('DIAGNOSIS', '/inquiry', inquiryData);
  }

  async performPalpationDiagnosis(palpationData: any) {
    return apiClient.post('DIAGNOSIS', '/palpation', palpationData);
  }

  // 新增算诊方法 (第五诊)
  async performCalculationDiagnosis(calculationData: any) {
    return apiClient.post('DIAGNOSIS', '/calculation', calculationData);
  }

  // 算诊专用方法
  async performZiwuAnalysis(birthData: { birthTime: string; currentTime?: string }) {
    return apiClient.post('DIAGNOSIS', '/ziwu', birthData);
  }

  async performConstitutionAnalysis(personalData: { 
    birthYear: number; 
    birthMonth: number; 
    birthDay: number; 
    birthHour: number;
    gender: string;
    location?: string;
  }) {
    return apiClient.post('DIAGNOSIS', '/constitution', personalData);
  }

  async performBaguaAnalysis(baguaData: {
    birthDate: string;
    gender: string;
    question?: string;
  }) {
    return apiClient.post('DIAGNOSIS', '/bagua', baguaData);
  }

  async performWuyunAnalysis(timeData: {
    year: number;
    month: number;
    day: number;
    location?: string;
  }) {
    return apiClient.post('DIAGNOSIS', '/wuyun', timeData);
  }

  async performCalculationComprehensive(comprehensiveData: {
    personalInfo: any;
    healthData?: any;
    preferences?: any;
  }) {
    return apiClient.post('DIAGNOSIS', '/calculationComprehensive', comprehensiveData);
  }

  // 五诊综合分析
  async performFiveDiagnosisComprehensive(fiveDiagnosisData: {
    lookData?: any;
    listenData?: any;
    inquiryData?: any;
    palpationData?: any;
    calculationData?: any;
    userId: string;
    sessionId?: string;
  }) {
    return apiClient.post('DIAGNOSIS', '/fiveDiagnosis', fiveDiagnosisData);
  }

  async getComprehensiveDiagnosis(diagnosisId: string) {
    return apiClient.get('DIAGNOSIS', `/comprehensive/${diagnosisId}`);
  }

  async getDiagnosisHistory(userId?: string) {
    const endpoint = userId ? `/history/${userId}` : '/history';
    return apiClient.get('DIAGNOSIS', endpoint);
  }

  // ==================== RAG服务 API ====================
  
  async queryRAG(query: string, context?: any) {
    return apiClient.post('RAG', '/query', { query, context });
  }

  async streamQueryRAG(query: string, context?: any) {
    return apiClient.post('RAG', '/stream-query', { query, context });
  }

  async multimodalQueryRAG(query: string, files?: any[], context?: any) {
    return apiClient.post('RAG', '/multimodal-query', { query, files, context });
  }

  async getTCMAnalysis(symptoms: string[], constitution?: string) {
    return apiClient.post('RAG', '/tcm/analysis', { symptoms, constitution });
  }

  async getHerbRecommendation(constitution: string, symptoms: string[]) {
    return apiClient.post('RAG', '/tcm/herbs', { constitution, symptoms });
  }

  async getSyndromeAnalysis(symptoms: string[]) {
    return apiClient.post('RAG', '/tcm/syndrome', { symptoms });
  }

  async getConstitutionAnalysis(userData: any) {
    return apiClient.post('RAG', '/tcm/constitution', userData);
  }

  // ==================== 区块链服务 API ====================
  
  async getBlockchainRecords(userId?: string) {
    const endpoint = userId ? `/records/${userId}` : '/records';
    return apiClient.get('BLOCKCHAIN', endpoint);
  }

  async verifyRecord(recordId: string) {
    return apiClient.post('BLOCKCHAIN', '/verify', { recordId });
  }

  async mintHealthNFT(healthData: any) {
    return apiClient.post('BLOCKCHAIN', '/mint', healthData);
  }

  async transferHealthNFT(tokenId: string, toAddress: string) {
    return apiClient.post('BLOCKCHAIN', '/transfer', { tokenId, toAddress });
  }

  // ==================== 消息总线服务 API ====================
  
  async publishMessage(topic: string, message: any) {
    return apiClient.post('MESSAGE_BUS', '/publish', { topic, message });
  }

  async subscribeToTopic(topic: string, callback: string) {
    return apiClient.post('MESSAGE_BUS', '/subscribe', { topic, callback });
  }

  async createTopic(topicName: string, config?: any) {
    return apiClient.post('MESSAGE_BUS', '/topics', { name: topicName, config });
  }

  async getTopics() {
    return apiClient.get('MESSAGE_BUS', '/topics');
  }

  // ==================== 其他服务 API ====================
  
  async getMedicalResources(location?: string, type?: string) {
    const params = new URLSearchParams();
    if (location) params.append('location', location);
    if (type) params.append('type', type);
    const endpoint = params.toString() ? `/resources?${params.toString()}` : '/resources';
    return apiClient.get('MEDICAL_RESOURCE', endpoint);
  }

  async getCornMazeStatus() {
    return apiClient.get('CORN_MAZE', '/status');
  }

  async startCornMazeGame(difficulty: string) {
    return apiClient.post('CORN_MAZE', '/start', { difficulty });
  }

  async getAccessibilitySettings() {
    return apiClient.get('ACCESSIBILITY', '/settings');
  }

  async updateAccessibilitySettings(settings: any) {
    return apiClient.put('ACCESSIBILITY', '/settings', settings);
  }

  async runBenchmark(config: any) {
    return apiClient.post('SUOKE_BENCH', '/run', config);
  }

  async getBenchmarkResults(benchmarkId?: string) {
    const endpoint = benchmarkId ? `/results/${benchmarkId}` : '/results';
    return apiClient.get('SUOKE_BENCH', endpoint);
  }

  // ==================== 网关管理 API ====================
  
  async getGatewayStatus() {
    return apiClient.get('', '/health');
  }

  async getServiceHealth(serviceName?: string) {
    const endpoint = serviceName ? `/services/${serviceName}/health` : '/services';
    return apiClient.get('', endpoint);
  }

  async getGatewayMetrics() {
    return apiClient.get('', '/metrics');
  }

  async getGatewayConfig() {
    return apiClient.get('', '/config');
  }

  // ==================== 工具方法 ====================
  
  /**
   * 批量API调用
   */
  async batchRequest(requests: Array<{ service: string; endpoint: string; method: 'GET' | 'POST' | 'PUT' | 'DELETE'; data?: any }>) {
    const promises = requests.map(req => {
      switch (req.method) {
        case 'GET':
          return apiClient.get(req.service, req.endpoint);
        case 'POST':
          return apiClient.post(req.service, req.endpoint, req.data);
        case 'PUT':
          return apiClient.put(req.service, req.endpoint, req.data);
        case 'DELETE':
          return apiClient.delete(req.service, req.endpoint);
        default:
          throw new Error(`Unsupported method: ${req.method}`);
      }
    });

    return Promise.allSettled(promises);
  }

  /**
   * 健康检查所有服务
   */
  async healthCheckAllServices() {
    const services = Object.keys(API_GATEWAY_CONFIG.SERVICES);
    const healthChecks = services.map(service => 
      this.getServiceHealth(service).catch(error => ({ service, error: error.message }))
    );

    return Promise.allSettled(healthChecks);
  }

  /**
   * 获取API统计信息
   */
  async getApiStats() {
    return {
      cacheStats: apiClient.getCacheStats(),
      circuitBreakerState: apiClient.getCircuitBreakerState(),
      gatewayHealth: await apiClient.healthCheck(),
    };
  }
}

// 导出单例实例
export const unifiedApiService = new UnifiedApiService();
export default unifiedApiService; 