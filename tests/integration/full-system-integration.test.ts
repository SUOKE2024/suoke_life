 /**
 * 索克生活系统完整集成测试
 * 测试前后端所有核心功能的集成
 */

import { configManager } from '../../src/config/AppConfig';
import { fiveDiagnosisService } from '../../src/services/fiveDiagnosisService';
import { agentCoordinationService } from '../../src/services/agentCoordinationService';
import { IntegratedApiService } from '../../src/services/IntegratedApiService';

// 测试配置
const TEST_CONFIG = {
  timeout: 30000,
  retryAttempts: 3,
  testUser: {
    id: 'test-user-123',
    name: '测试用户',
    email: 'test@suokelife.com'
  },
  testPatient: {
    name: '张三',
    age: 35,
    gender: 'male',
    symptoms: ['乏力', '失眠', '食欲不振']
  }
};

describe('索克生活系统完整集成测试', () => {
  let apiService: IntegratedApiService;
  let sessionId: string;

  beforeAll(async () => {
    // 初始化配置
    configManager.updateConfig({
      api: {
        ...configManager.getApiConfig(),
        enableMocking: false // 使用真实API进行集成测试
      }
    });

    // 初始化API服务
    apiService = new IntegratedApiService();
    await apiService.initialize();
  }, TEST_CONFIG.timeout);

  afterAll(async () => {
    // 清理资源
    if (sessionId) {
      try {
        await fiveDiagnosisService.endDiagnosis(sessionId);
      } catch (error) {
        console.warn('清理会话失败:', error);
      }
    }
  });

  describe('🔧 系统初始化测试', () => {
    it('应该成功初始化配置管理器', () => {
      const config = configManager.getConfig();
      expect(config).toBeDefined();
      expect(config.version).toBeDefined();
      expect(config.api.baseUrl).toBeDefined();
    });

    it('应该成功验证配置', () => {
      const isValid = configManager.validateConfig();
      expect(isValid).toBe(true);
    });

    it('应该成功初始化API服务', async () => {
      expect(apiService).toBeDefined();
      
      // 测试健康检查
      const healthStatus = await apiService.healthCheck();
      expect(healthStatus.status).toBe('healthy');
    });
  });

  describe('🔐 认证服务集成测试', () => {
    it('应该成功进行用户认证', async () => {
      const loginResult = await apiService.auth.login({
        email: TEST_CONFIG.testUser.email,
        password: 'test-password'
      });

      expect(loginResult.success).toBe(true);
      expect(loginResult.token).toBeDefined();
      expect(loginResult.user).toBeDefined();
    });

    it('应该成功获取用户信息', async () => {
      const userInfo = await apiService.user.getCurrentUser();
      
      expect(userInfo).toBeDefined();
      expect(userInfo.id).toBe(TEST_CONFIG.testUser.id);
      expect(userInfo.email).toBe(TEST_CONFIG.testUser.email);
    });
  });

  describe('🤖 智能体服务集成测试', () => {
    it('应该成功获取所有智能体状态', async () => {
      const agentStatuses = await apiService.agents.getAllAgentStatuses();
      
      expect(agentStatuses).toBeDefined();
      expect(agentStatuses.xiaoai).toBeDefined();
      expect(agentStatuses.xiaoke).toBeDefined();
      expect(agentStatuses.laoke).toBeDefined();
      expect(agentStatuses.soer).toBeDefined();

      // 验证智能体状态
      Object.values(agentStatuses).forEach(status => {
        expect(['idle', 'processing', 'learning', 'error', 'offline']).toContain(status.status);
        expect(typeof status.confidence).toBe('number');
        expect(status.confidence).toBeGreaterThanOrEqual(0);
        expect(status.confidence).toBeLessThanOrEqual(1);
      });
    });

    it('应该成功与小艾智能体交互', async () => {
      const response = await apiService.agents.sendMessage('xiaoai', {
        message: '你好，我想进行中医诊断',
        userId: TEST_CONFIG.testUser.id
      });

      expect(response).toBeDefined();
      expect(response.message).toBeDefined();
      expect(response.confidence).toBeGreaterThan(0);
    });

    it('应该成功进行智能体协调', async () => {
      const coordinationResult = await agentCoordinationService.coordinateAgents({
        task: 'comprehensive_diagnosis',
        userId: TEST_CONFIG.testUser.id,
        patientInfo: TEST_CONFIG.testPatient,
        requiredAgents: ['xiaoai', 'xiaoke']
      });

      expect(coordinationResult).toBeDefined();
      expect(coordinationResult.coordination.primary_agent).toBeDefined();
      expect(coordinationResult.coordination.supporting_agents).toBeDefined();
      expect(coordinationResult.coordination.confidence).toBeGreaterThan(0);
    });
  });

  describe('🏥 五诊系统集成测试', () => {
    beforeAll(async () => {
      // 开始诊断会话
      const startResult = await fiveDiagnosisService.startDiagnosis(TEST_CONFIG.testUser.id);
      sessionId = startResult.sessionId;
      expect(sessionId).toBeDefined();
    });

    it('应该成功执行望诊', async () => {
      const lookingData = {
        face_color: 'yellow',
        tongue_color: 'pale',
        tongue_coating: 'white_thick',
        spirit: 'tired'
      };

      const result = await fiveDiagnosisService.performSingleDiagnosis(
        sessionId,
        'looking',
        lookingData
      );

      expect(result).toBeDefined();
      expect(result.result.analysis).toBeDefined();
      expect(result.result.confidence).toBeGreaterThan(0);
      expect(result.result.suggestions).toBeDefined();
      expect(Array.isArray(result.result.suggestions)).toBe(true);
    });

    it('应该成功执行闻诊', async () => {
      const listeningData = {
        voice_quality: '低微',
        breathing: '气短',
        cough: 'none'
      };

      const result = await fiveDiagnosisService.performSingleDiagnosis(
        sessionId,
        'listening',
        listeningData
      );

      expect(result).toBeDefined();
      expect(result.result.analysis).toBeDefined();
      expect(result.result.confidence).toBeGreaterThan(0);
    });

    it('应该成功执行问诊', async () => {
      const inquiryData = {
        symptoms: TEST_CONFIG.testPatient.symptoms,
        duration: '3个月',
        severity: 'moderate',
        triggers: ['工作压力', '睡眠不足']
      };

      const result = await fiveDiagnosisService.performSingleDiagnosis(
        sessionId,
        'inquiry',
        inquiryData
      );

      expect(result).toBeDefined();
      expect(result.result.analysis).toBeDefined();
      expect(result.result.confidence).toBeGreaterThan(0);
    });

    it('应该成功执行切诊', async () => {
      const palpationData = {
        pulse_quality: '细弱',
        pulse_rate: 'slow',
        acupoint_sensitivity: ['神门穴', '足三里']
      };

      const result = await fiveDiagnosisService.performSingleDiagnosis(
        sessionId,
        'palpation',
        palpationData
      );

      expect(result).toBeDefined();
      expect(result.result.analysis).toBeDefined();
      expect(result.result.confidence).toBeGreaterThan(0);
    });

    it('应该成功执行算诊（综合分析）', async () => {
      const calculationData = {
        comprehensive_analysis: true,
        include_all_previous: true
      };

      const result = await fiveDiagnosisService.performSingleDiagnosis(
        sessionId,
        'calculation',
        calculationData
      );

      expect(result).toBeDefined();
      expect(result.result.analysis).toBeDefined();
      expect(result.result.analysis.tcm_syndrome).toBeDefined();
      expect(result.result.analysis.constitution).toBeDefined();
      expect(result.result.analysis.treatment_principle).toBeDefined();
      expect(result.result.confidence).toBeGreaterThan(0);
    });

    it('应该成功获取完整诊断报告', async () => {
      const report = await fiveDiagnosisService.getComprehensiveReport(sessionId);

      expect(report).toBeDefined();
      expect(report.sessionId).toBe(sessionId);
      expect(report.patientInfo).toBeDefined();
      expect(report.diagnosisResults).toBeDefined();
      expect(report.comprehensiveAnalysis).toBeDefined();
      expect(report.recommendations).toBeDefined();
      expect(Array.isArray(report.recommendations)).toBe(true);
    });
  });

  describe('💾 数据服务集成测试', () => {
    it('应该成功保存健康数据', async () => {
      const healthData = {
        userId: TEST_CONFIG.testUser.id,
        type: 'diagnosis_result',
        data: {
          sessionId,
          timestamp: new Date().toISOString(),
          syndrome: '气虚证',
          confidence: 0.85
        }
      };

      const saveResult = await apiService.healthData.saveHealthData(healthData);
      expect(saveResult.success).toBe(true);
      expect(saveResult.id).toBeDefined();
    });

    it('应该成功获取用户健康数据', async () => {
      const healthData = await apiService.healthData.getUserHealthData(
        TEST_CONFIG.testUser.id,
        { limit: 10, offset: 0 }
      );

      expect(healthData).toBeDefined();
      expect(Array.isArray(healthData.data)).toBe(true);
      expect(healthData.total).toBeGreaterThanOrEqual(0);
    });
  });

  describe('🔗 区块链服务集成测试', () => {
    it('应该成功创建健康数据哈希', async () => {
      const healthData = {
        userId: TEST_CONFIG.testUser.id,
        diagnosisResult: '气虚证',
        timestamp: new Date().toISOString()
      };

      const hashResult = await apiService.blockchain.createHealthDataHash(healthData);
      expect(hashResult).toBeDefined();
      expect(hashResult.hash).toBeDefined();
      expect(hashResult.transactionId).toBeDefined();
    });

    it('应该成功验证数据完整性', async () => {
      const verificationData = {
        userId: TEST_CONFIG.testUser.id,
        dataHash: 'test-hash-123',
        timestamp: new Date().toISOString()
      };

      const verificationResult = await apiService.blockchain.verifyDataIntegrity(verificationData);
      expect(verificationResult).toBeDefined();
      expect(typeof verificationResult.isValid).toBe('boolean');
    });
  });

  describe('🔍 RAG服务集成测试', () => {
    it('应该成功进行知识检索', async () => {
      const query = '气虚证的治疗方法';
      const searchResult = await apiService.rag.searchKnowledge(query);

      expect(searchResult).toBeDefined();
      expect(Array.isArray(searchResult.results)).toBe(true);
      expect(searchResult.results.length).toBeGreaterThan(0);
      
      searchResult.results.forEach(result => {
        expect(result.content).toBeDefined();
        expect(result.relevance).toBeGreaterThan(0);
        expect(result.source).toBeDefined();
      });
    });

    it('应该成功生成知识增强回答', async () => {
      const question = '我被诊断为气虚证，应该如何调理？';
      const enhancedAnswer = await apiService.rag.generateEnhancedAnswer(question);

      expect(enhancedAnswer).toBeDefined();
      expect(enhancedAnswer.answer).toBeDefined();
      expect(enhancedAnswer.confidence).toBeGreaterThan(0);
      expect(Array.isArray(enhancedAnswer.sources)).toBe(true);
    });
  });

  describe('📊 性能监控集成测试', () => {
    it('应该成功记录性能指标', async () => {
      const performanceData = {
        componentName: 'FiveDiagnosisScreen',
        renderTime: 15.5,
        memoryUsage: 45.2,
        networkLatency: 120
      };

      const recordResult = await apiService.performance.recordMetrics(performanceData);
      expect(recordResult.success).toBe(true);
    });

    it('应该成功获取性能报告', async () => {
      const report = await apiService.performance.getPerformanceReport({
        timeRange: '24h',
        metrics: ['renderTime', 'memoryUsage', 'networkLatency']
      });

      expect(report).toBeDefined();
      expect(report.summary).toBeDefined();
      expect(Array.isArray(report.metrics)).toBe(true);
    });
  });

  describe('🔄 端到端工作流测试', () => {
    it('应该成功完成完整的诊断工作流', async () => {
      // 1. 用户登录
      const loginResult = await apiService.auth.login({
        email: TEST_CONFIG.testUser.email,
        password: 'test-password'
      });
      expect(loginResult.success).toBe(true);

      // 2. 开始诊断
      const startResult = await fiveDiagnosisService.startDiagnosis(TEST_CONFIG.testUser.id);
      const workflowSessionId = startResult.sessionId;

      // 3. 执行五诊
      const diagnosisSteps = [
        { type: 'looking', data: { face_color: 'yellow', tongue_color: 'pale' } },
        { type: 'listening', data: { voice_quality: '低微', breathing: '气短' } },
        { type: 'inquiry', data: { symptoms: ['乏力', '失眠'] } },
        { type: 'palpation', data: { pulse_quality: '细弱' } },
        { type: 'calculation', data: { comprehensive_analysis: true } }
      ];

      for (const step of diagnosisSteps) {
        const result = await fiveDiagnosisService.performSingleDiagnosis(
          workflowSessionId,
          step.type as any,
          step.data
        );
        expect(result.result.confidence).toBeGreaterThan(0);
      }

      // 4. 获取综合报告
      const report = await fiveDiagnosisService.getComprehensiveReport(workflowSessionId);
      expect(report.comprehensiveAnalysis).toBeDefined();

      // 5. 保存到区块链
      const blockchainResult = await apiService.blockchain.createHealthDataHash({
        userId: TEST_CONFIG.testUser.id,
        diagnosisResult: report.comprehensiveAnalysis.tcm_syndrome,
        timestamp: new Date().toISOString()
      });
      expect(blockchainResult.hash).toBeDefined();

      // 6. 清理
      await fiveDiagnosisService.endDiagnosis(workflowSessionId);
    }, TEST_CONFIG.timeout);

    it('应该成功处理并发诊断请求', async () => {
      const concurrentSessions = 3;
      const promises = [];

      for (let i = 0; i < concurrentSessions; i++) {
        const promise = (async () => {
          const startResult = await fiveDiagnosisService.startDiagnosis(`test-user-${i}`);
          const sessionId = startResult.sessionId;

          const result = await fiveDiagnosisService.performSingleDiagnosis(
            sessionId,
            'looking',
            { face_color: 'yellow' }
          );

          await fiveDiagnosisService.endDiagnosis(sessionId);
          return result;
        })();

        promises.push(promise);
      }

      const results = await Promise.all(promises);
      expect(results).toHaveLength(concurrentSessions);
      results.forEach(result => {
        expect(result.result.confidence).toBeGreaterThan(0);
      });
    });
  });

  describe('🚨 错误处理和恢复测试', () => {
    it('应该正确处理网络错误', async () => {
      // 模拟网络错误
      const originalBaseUrl = configManager.getApiConfig().baseUrl;
      configManager.updateConfig({
        api: {
          ...configManager.getApiConfig(),
          baseUrl: 'http://invalid-url'
        }
      });

      try {
        await apiService.healthCheck();
        fail('应该抛出网络错误');
      } catch (error) {
        expect(error).toBeDefined();
      }

      // 恢复配置
      configManager.updateConfig({
        api: {
          ...configManager.getApiConfig(),
          baseUrl: originalBaseUrl
        }
      });
    });

    it('应该正确处理智能体服务错误', async () => {
      try {
        await apiService.agents.sendMessage('invalid-agent' as any, {
          message: 'test',
          userId: 'test'
        });
        fail('应该抛出智能体错误');
      } catch (error) {
        expect(error).toBeDefined();
      }
    });

    it('应该正确处理诊断数据验证错误', async () => {
      const invalidSessionId = 'invalid-session-123';
      
      try {
        await fiveDiagnosisService.performSingleDiagnosis(
          invalidSessionId,
          'looking',
          {}
        );
        fail('应该抛出验证错误');
      } catch (error) {
        expect(error).toBeDefined();
      }
    });
  });

  describe('📈 性能基准测试', () => {
    it('诊断响应时间应该在可接受范围内', async () => {
      const startTime = Date.now();
      
      const startResult = await fiveDiagnosisService.startDiagnosis(TEST_CONFIG.testUser.id);
      const sessionId = startResult.sessionId;

      const result = await fiveDiagnosisService.performSingleDiagnosis(
        sessionId,
        'looking',
        { face_color: 'yellow' }
      );

      const endTime = Date.now();
      const responseTime = endTime - startTime;

      expect(responseTime).toBeLessThan(5000); // 5秒内响应
      expect(result.result.confidence).toBeGreaterThan(0);

      await fiveDiagnosisService.endDiagnosis(sessionId);
    });

    it('系统应该能够处理高并发请求', async () => {
      const concurrentRequests = 10;
      const startTime = Date.now();

      const promises = Array.from({ length: concurrentRequests }, async (_, i) => {
        return apiService.agents.sendMessage('xiaoai', {
          message: `并发测试消息 ${i}`,
          userId: `test-user-${i}`
        });
      });

      const results = await Promise.all(promises);
      const endTime = Date.now();
      const totalTime = endTime - startTime;

      expect(results).toHaveLength(concurrentRequests);
      expect(totalTime).toBeLessThan(10000); // 10秒内完成所有请求
      
      results.forEach(result => {
        expect(result.message).toBeDefined();
      });
    });
  });
});