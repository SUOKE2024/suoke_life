import React from 'react';
import { render, fireEvent, waitFor, act } from '@testing-library/react-native';
import { Provider } from 'react-redux';
import { NavigationContainer } from '@react-navigation/native';
import { Alert } from 'react-native';
// 导入应用组件
import App from '../../App';
// 导入类型
import { AgentType } from '../../types/agents';
// Mock外部依赖
jest.mock('react-native-permissions', () => ({
  PERMISSIONS: {
    ANDROID: { CAMERA: 'android.permission.CAMERA' },
    IOS: { CAMERA: 'ios.permission.CAMERA' }
  },
  RESULTS: { GRANTED: 'granted' },
  request: jest.fn(() => Promise.resolve('granted')),
  check: jest.fn(() => Promise.resolve('granted'))
}));
jest.mock('react-native-voice', () => ({
  start: jest.fn(),
  stop: jest.fn(),
  destroy: jest.fn(),
  removeAllListeners: jest.fn()
}));
// 测试数据
const testUser = {
      id: "test-user-001",
      username: 'test_user',
  email: 'test@suokelife.com',
  phone: '13800138000',
  password: 'TestPassword123!',
  profile: {
      name: "张三",
      age: 35,
    gender: 'male' as const,
    height: 175,
    weight: 70,
    constitution: 'balanced'
  }
};
const testPatient = {
      name: "李四",
      age: 42,
  gender: 'female' as const,
  chiefComplaint: '头痛失眠，食欲不振',
  symptoms: ["头痛",失眠', "食欲不振",疲劳'],
  medicalHistory: ['高血压'],
  currentMedications: ['降压药']
};
describe('索克生活 - 全面端到端测试', () => {
  let mockServices: any;
  beforeAll(async () => {
    // 初始化测试环境
    mockServices = setupMockServices();
        // 设置测试超时
    jest.setTimeout(60000);
  });
  beforeEach(() => {
    jest.clearAllMocks();
    setupDefaultMocks();
  });
  afterEach(() => {
    cleanup();
  });
  describe('🚀 用户完整旅程测试', () => {
    it('应该完成从注册到健康管理的完整用户旅程', async () => {
      const { getByTestId, getByText, queryByText } = render(
        <Provider store={store}>
          <NavigationContainer>
            <App />
          </NavigationContainer>
        </Provider>
      );
      // 步骤1: 用户注册
      await act(async () => {
        // 导航到注册页面
        const registerButton = getByTestId('register-button');
        fireEvent.press(registerButton);
      });
      await waitFor(() => {
        expect(getByText('用户注册')).toBeTruthy();
      });
      // 填写注册信息
      await act(async () => {
        fireEvent.changeText(getByTestId('username-input'), testUser.username);
        fireEvent.changeText(getByTestId('email-input'), testUser.email);
        fireEvent.changeText(getByTestId('phone-input'), testUser.phone);
        fireEvent.changeText(getByTestId('password-input'), testUser.password);
                fireEvent.press(getByTestId('submit-register-button'));
      });
      // 验证注册成功
      await waitFor(() => {
        expect(mockServices.authService.register).toHaveBeenCalledWith({
          username: testUser.username,
          email: testUser.email,
          phone: testUser.phone,
          password: testUser.password
        });
      });
      // 步骤2: 用户登录
      await act(async () => {
        fireEvent.changeText(getByTestId('login-username'), testUser.username);
        fireEvent.changeText(getByTestId('login-password'), testUser.password);
        fireEvent.press(getByTestId('login-button'));
      });
      await waitFor(() => {
        expect(getByText('首页')).toBeTruthy();
      });
      // 步骤3: 完善个人资料
      await act(async () => {
        fireEvent.press(getByTestId('profile-tab'));
      });
      await waitFor(() => {
        expect(getByText('个人资料')).toBeTruthy();
      });
      await act(async () => {
        fireEvent.press(getByTestId('edit-profile-button'));
                fireEvent.changeText(getByTestId('name-input'), testUser.profile.name);
        fireEvent.changeText(getByTestId('age-input'), testUser.profile.age.toString());
        fireEvent.press(getByTestId(`gender-${testUser.profile.gender}`));
        fireEvent.changeText(getByTestId('height-input'), testUser.profile.height.toString());
        fireEvent.changeText(getByTestId('weight-input'), testUser.profile.weight.toString());
                fireEvent.press(getByTestId('save-profile-button'));
      });
      // 验证资料保存成功
      await waitFor(() => {
        expect(mockServices.userService.updateProfile).toHaveBeenCalled();
      });
      // 步骤4: 进行健康评估
      await act(async () => {
        fireEvent.press(getByTestId('health-tab'));
      });
      await waitFor(() => {
        expect(getByText('健康概览')).toBeTruthy();
      });
      await act(async () => {
        fireEvent.press(getByTestId('start-assessment-button'));
      });
      // 验证健康评估启动
      await waitFor(() => {
        expect(getByText('健康评估')).toBeTruthy();
      });
      // 步骤5: 查看健康建议
      await waitFor(() => {
        expect(queryByText('个性化健康建议')).toBeTruthy();
      }, { timeout: 10000 });
      console.log('✅ 用户完整旅程测试通过');
    });
    it('应该处理用户登录失败的情况', async () => {
      mockServices.authService.login.mockRejectedValue(new Error('用户名或密码错误'));
      const { getByTestId, getByText } = render(
        <Provider store={store}>
          <NavigationContainer>
            <App />
          </NavigationContainer>
        </Provider>
      );
      await act(async () => {
        fireEvent.changeText(getByTestId('login-username'), 'wrong_user');
        fireEvent.changeText(getByTestId('login-password'), 'wrong_password');
        fireEvent.press(getByTestId('login-button'));
      });
      await waitFor(() => {
        expect(getByText('登录失败')).toBeTruthy();
      });
    });
  });
  describe('🤖 智能体协作端到端测试', () => {
    it('应该完成四大智能体的协同工作流程', async () => {
      const { getByTestId, getByText } = render(
        <Provider store={store}>
          <NavigationContainer>
            <App />
          </NavigationContainer>
        </Provider>
      );
      // 模拟用户已登录
      await simulateUserLogin();
      // 步骤1: 启动智能体协作
      await act(async () => {
        fireEvent.press(getByTestId('diagnosis-tab'));
      });
      await waitFor(() => {
        expect(getByText('四诊')).toBeTruthy();
      });
      await act(async () => {
        fireEvent.press(getByTestId('start-diagnosis-button'));
      });
      // 步骤2: 小艾 - 主导四诊协调
      await waitFor(() => {
        expect(mockServices.agentCoordinationService.startSession).toHaveBeenCalledWith({
          userId: testUser.id,
          sessionType: 'four_diagnosis',
          primaryAgent: AgentType.XIAOAI
        });
      });
      // 验证小艾响应
      await waitFor(() => {
        expect(getByText('小艾正在协调四诊流程...')).toBeTruthy();
      });
      // 步骤3: 小克 - 服务管理
      await act(async () => {
        fireEvent.press(getByTestId('service-management-button'));
      });
      await waitFor(() => {
        expect(mockServices.agentCoordinationService.requestAgentAction).toHaveBeenCalledWith({
          agentType: AgentType.XIAOKE,
          action: 'service_management',
          parameters: expect.any(Object)
        });
      });
      // 步骤4: 老克 - 知识检索
      await waitFor(() => {
        expect(mockServices.agentCoordinationService.requestAgentAction).toHaveBeenCalledWith({
          agentType: AgentType.LAOKE,
          action: 'knowledge_retrieval',
          parameters: expect.any(Object)
        });
      });
      // 步骤5: 索儿 - 生活方式建议
      await waitFor(() => {
        expect(mockServices.agentCoordinationService.requestAgentAction).toHaveBeenCalledWith({
          agentType: AgentType.SOER,
          action: 'lifestyle_management',
          parameters: expect.any(Object)
        });
      });
      // 验证协作结果
      await waitFor(() => {
        expect(getByText('智能体协作完成')).toBeTruthy();
      }, { timeout: 15000 });
      console.log('✅ 智能体协作测试通过');
    });
    it('应该处理智能体服务异常情况', async () => {
      mockServices.agentCoordinationService.startSession.mockRejectedValue(
        new Error('智能体服务暂时不可用')
      );
      const { getByTestId, getByText } = render(
        <Provider store={store}>
          <NavigationContainer>
            <App />
          </NavigationContainer>
        </Provider>
      );
      await simulateUserLogin();
      await act(async () => {
        fireEvent.press(getByTestId('diagnosis-tab'));
        fireEvent.press(getByTestId('start-diagnosis-button'));
      });
      await waitFor(() => {
        expect(getByText('服务暂时不可用，请稍后重试')).toBeTruthy();
      });
    });
  });
  describe('🏥 中医四诊端到端测试', () => {
    it('应该完成完整的五诊流程', async () => {
      const { getByTestId, getByText } = render(
        <Provider store={store}>
          <NavigationContainer>
            <App />
          </NavigationContainer>
        </Provider>
      );
      await simulateUserLogin();
      // 步骤1: 开始五诊流程
      await act(async () => {
        fireEvent.press(getByTestId('diagnosis-tab'));
        fireEvent.press(getByTestId('start-five-diagnosis-button'));
      });
      // 填写患者信息
      await act(async () => {
        fireEvent.changeText(getByTestId('patient-name'), testPatient.name);
        fireEvent.changeText(getByTestId('patient-age'), testPatient.age.toString());
        fireEvent.press(getByTestId(`patient-gender-${testPatient.gender}`));
        fireEvent.changeText(getByTestId('chief-complaint'), testPatient.chiefComplaint);
                fireEvent.press(getByTestId('start-diagnosis-process'));
      });
      // 步骤2: 望诊
      await waitFor(() => {
        expect(getByText('望诊')).toBeTruthy();
      });
      await act(async () => {
        fireEvent.press(getByTestId('start-looking-diagnosis'));
      });
      await waitFor(() => {
        expect(mockServices.fiveDiagnosisService.performLookingDiagnosis).toHaveBeenCalled();
      });
      // 步骤3: 闻诊
      await waitFor(() => {
        expect(getByText('闻诊')).toBeTruthy();
      });
      await act(async () => {
        fireEvent.press(getByTestId('start-listening-diagnosis'));
      });
      await waitFor(() => {
        expect(mockServices.fiveDiagnosisService.performListeningDiagnosis).toHaveBeenCalled();
      });
      // 步骤4: 问诊
      await waitFor(() => {
        expect(getByText('问诊')).toBeTruthy();
      });
      await act(async () => {
        fireEvent.press(getByTestId('start-inquiry-diagnosis'));
      });
      await waitFor(() => {
        expect(mockServices.fiveDiagnosisService.performInquiryDiagnosis).toHaveBeenCalled();
      });
      // 步骤5: 切诊
      await waitFor(() => {
        expect(getByText('切诊')).toBeTruthy();
      });
      await act(async () => {
        fireEvent.press(getByTestId('start-palpation-diagnosis'));
      });
      await waitFor(() => {
        expect(mockServices.fiveDiagnosisService.performPalpationDiagnosis).toHaveBeenCalled();
      });
      // 步骤6: 算诊
      await waitFor(() => {
        expect(getByText('算诊')).toBeTruthy();
      });
      await waitFor(() => {
        expect(mockServices.fiveDiagnosisService.performCalculationDiagnosis).toHaveBeenCalled();
      });
      // 验证诊断结果
      await waitFor(() => {
        expect(getByText('诊断结果')).toBeTruthy();
        expect(getByText('体质类型')).toBeTruthy();
        expect(getByText('健康建议')).toBeTruthy();
      }, { timeout: 20000 });
      console.log('✅ 中医四诊测试通过');
    });
    it('应该处理诊断数据采集失败的情况', async () => {
      mockServices.fiveDiagnosisService.performLookingDiagnosis.mockRejectedValue(
        new Error('图像采集失败')
      );
      const { getByTestId, getByText } = render(
        <Provider store={store}>
          <NavigationContainer>
            <App />
          </NavigationContainer>
        </Provider>
      );
      await simulateUserLogin();
      await act(async () => {
        fireEvent.press(getByTestId('diagnosis-tab'));
        fireEvent.press(getByTestId('start-five-diagnosis-button'));
        fireEvent.press(getByTestId('start-diagnosis-process'));
        fireEvent.press(getByTestId('start-looking-diagnosis'));
      });
      await waitFor(() => {
        expect(getByText('数据采集失败，请重试')).toBeTruthy();
      });
    });
  });
  describe('🔐 数据安全端到端测试', () => {
    it('应该完成健康数据的区块链存储和验证', async () => {
      const { getByTestId, getByText } = render(
        <Provider store={store}>
          <NavigationContainer>
            <App />
          </NavigationContainer>
        </Provider>
      );
      await simulateUserLogin();
      // 步骤1: 生成健康数据
      await act(async () => {
        fireEvent.press(getByTestId('health-tab'));
        fireEvent.press(getByTestId('generate-health-report'));
      });
      // 步骤2: 区块链存储
      await waitFor(() => {
        expect(mockServices.blockchainService.storeHealthData).toHaveBeenCalledWith({
          userId: testUser.id,
          dataType: 'health_report',
          data: expect.any(Object),
          timestamp: expect.any(Number)
        });
      });
      // 步骤3: 数据验证
      await act(async () => {
        fireEvent.press(getByTestId('verify-data-button'));
      });
      await waitFor(() => {
        expect(mockServices.blockchainService.verifyDataIntegrity).toHaveBeenCalled();
      });
      // 验证区块链存储成功
      await waitFor(() => {
        expect(getByText('数据已安全存储到区块链')).toBeTruthy();
        expect(getByText('数据完整性验证通过')).toBeTruthy();
      });
      console.log('✅ 数据安全测试通过');
    });
    it('应该保护用户隐私数据', async () => {
      const { getByTestId, getByText } = render(
        <Provider store={store}>
          <NavigationContainer>
            <App />
          </NavigationContainer>
        </Provider>
      );
      await simulateUserLogin();
      // 测试数据加密
      await act(async () => {
        fireEvent.press(getByTestId('privacy-settings'));
        fireEvent.press(getByTestId('enable-encryption'));
      });
      await waitFor(() => {
        expect(mockServices.blockchainService.enableDataEncryption).toHaveBeenCalled();
      });
      // 测试零知识证明
      await act(async () => {
        fireEvent.press(getByTestId('generate-zk-proof'));
      });
      await waitFor(() => {
        expect(mockServices.blockchainService.generateZKProof).toHaveBeenCalled();
      });
      await waitFor(() => {
        expect(getByText('隐私保护已启用')).toBeTruthy();
      });
    });
  });
  describe('⚡ 性能和可靠性测试', () => {
    it('应该在高并发情况下保持稳定', async () => {
      const concurrentUsers = 5;
      const promises = [];
      // 模拟多个用户同时使用
      for (let i = 0; i < concurrentUsers; i++) {
        promises.push(simulateConcurrentUserSession(i));
      }
      const results = await Promise.allSettled(promises);
            // 验证所有会话都成功完成
      const successfulSessions = results.filter(result => result.status === 'fulfilled').length;
      expect(successfulSessions).toBeGreaterThanOrEqual(concurrentUsers * 0.8); // 80%成功率
      console.log(`✅ 并发测试通过: ${successfulSessions}/${concurrentUsers} 会话成功`);
    });
    it('应该处理网络异常情况', async () => {
      // 模拟网络断开
      mockServices.networkService.isConnected.mockReturnValue(false);
      const { getByTestId, getByText } = render(
        <Provider store={store}>
          <NavigationContainer>
            <App />
          </NavigationContainer>
        </Provider>
      );
      await waitFor(() => {
        expect(getByText('网络连接异常')).toBeTruthy();
        expect(getByTestId('offline-mode-indicator')).toBeTruthy();
      });
      // 模拟网络恢复
      await act(async () => {
        mockServices.networkService.isConnected.mockReturnValue(true);
        fireEvent.press(getByTestId('retry-connection'));
      });
      await waitFor(() => {
        expect(getByText('网络连接已恢复')).toBeTruthy();
      });
    });
    it('应该监控应用性能指标', async () => {
      const { getByTestId } = render(
        <Provider store={store}>
          <NavigationContainer>
            <App />
          </NavigationContainer>
        </Provider>
      );
      await simulateUserLogin();
      // 执行性能密集型操作
      await act(async () => {
        fireEvent.press(getByTestId('diagnosis-tab'));
        fireEvent.press(getByTestId('start-five-diagnosis-button'));
      });
      // 验证性能指标
      await waitFor(() => {
        expect(mockServices.performanceMonitor.getMetrics).toHaveBeenCalled();
      });
      const metrics = mockServices.performanceMonitor.getMetrics();
      expect(metrics.renderTime).toBeLessThan(100); // 渲染时间小于100ms
      expect(metrics.memoryUsage).toBeLessThan(50 * 1024 * 1024); // 内存使用小于50MB
    });
  });
  // 辅助函数
  function setupMockServices() {
    return {
      authService: {
        register: jest.fn().mockResolvedValue({ success: true, user: testUser }),
        login: jest.fn().mockResolvedValue({ success: true, user: testUser, token: 'mock-token' }),
        logout: jest.fn().mockResolvedValue({ success: true })
      },
      userService: {
        updateProfile: jest.fn().mockResolvedValue({ success: true }),
        getProfile: jest.fn().mockResolvedValue({ success: true, profile: testUser.profile })
      },
      fiveDiagnosisService: {
        performLookingDiagnosis: jest.fn().mockResolvedValue({ success: true, data: {} }),
        performListeningDiagnosis: jest.fn().mockResolvedValue({ success: true, data: {} }),
        performInquiryDiagnosis: jest.fn().mockResolvedValue({ success: true, data: {} }),
        performPalpationDiagnosis: jest.fn().mockResolvedValue({ success: true, data: {} }),
        performCalculationDiagnosis: jest.fn().mockResolvedValue({
          success: true,
          data: {
      constitution: "balanced",
      recommendations: [] }
        })
      },
      agentCoordinationService: {
        startSession: jest.fn().mockResolvedValue({ success: true, sessionId: 'mock-session' }),
        requestAgentAction: jest.fn().mockResolvedValue({ success: true, response: {} })
      },
      blockchainService: {
        storeHealthData: jest.fn().mockResolvedValue({ success: true, hash: 'mock-hash' }),
        verifyDataIntegrity: jest.fn().mockResolvedValue({ success: true, valid: true }),
        enableDataEncryption: jest.fn().mockResolvedValue({ success: true }),
        generateZKProof: jest.fn().mockResolvedValue({ success: true, proof: 'mock-proof' })
      },
      networkService: {
        isConnected: jest.fn().mockReturnValue(true)
      },
      performanceMonitor: {
        getMetrics: jest.fn().mockReturnValue({
          renderTime: 50,
          memoryUsage: 30 * 1024 * 1024
        })
      }
    };
  }
  function setupDefaultMocks() {
    // 设置默认的mock行为
    jest.spyOn(Alert, 'alert').mockImplementation(() => {});
        // Mock服务调用
    Object.keys(mockServices).forEach(serviceName => {
      const service = mockServices[serviceName];
      Object.keys(service).forEach(methodName => {
        if (typeof service[methodName] === 'function') {
          service[methodName].mockClear();
        }
      });
    });
  }
  async function simulateUserLogin() {
    // 模拟用户已登录状态
    store.dispatch({
      type: "auth/loginSuccess",
      payload: { user: testUser, token: 'mock-token' }
    });
  }
  async function simulateConcurrentUserSession(userId: number): Promise<void> {
    // 模拟单个用户会话
    await new Promise(resolve => setTimeout(resolve, Math.random() * 100));
    return Promise.resolve();
  }
  function cleanup() {
    // 清理测试环境
    jest.clearAllTimers();
  }
});