// Mock端到端测试框架
const createMockElement = () => ({
  tap: jest.fn().mockResolvedValue(undefined),
  typeText: jest.fn().mockResolvedValue(undefined),
  clearText: jest.fn().mockResolvedValue(undefined),
  swipe: jest.fn().mockResolvedValue(undefined),
  scroll: jest.fn().mockResolvedValue(undefined),
  waitFor: jest.fn().mockResolvedValue(true),
});

const createMockWaitFor = () => {
  const waitForObj = {
    toBeVisible: jest.fn().mockReturnThis(),
    toExist: jest.fn().mockReturnThis(),
    toHaveText: jest.fn().mockReturnThis(),
    withTimeout: jest.fn().mockResolvedValue(true),
  };
  return waitForObj;
};

const createMockExpect = () => ({
  toBeVisible: jest.fn().mockReturnValue(true),
  toExist: jest.fn().mockReturnValue(true),
  toHaveText: jest.fn().mockReturnValue(true),
  toHaveId: jest.fn().mockReturnValue(true),
});

const mockE2E = {
  device: {
    launchApp: jest.fn().mockResolvedValue(undefined),
    reloadReactNative: jest.fn().mockResolvedValue(undefined),
    terminateApp: jest.fn().mockResolvedValue(undefined),
  },
  element: jest.fn().mockImplementation(() => createMockElement()),
  by: {
    id: (id: string) => ({ id }),
    text: (text: string) => ({ text }),
    label: (label: string) => ({ label }),
    type: (type: string) => ({ type }),
  },
  waitFor: jest.fn().mockImplementation(() => createMockWaitFor()),
  expect: jest.fn().mockImplementation(() => createMockExpect()),
};

describe('用户流程端到端测试', () => {
  beforeAll(async () => {
    await mockE2E.device.launchApp();
  });

  afterAll(async () => {
    await mockE2E.device.terminateApp();
  });

  describe('用户注册流程', () => {
    it('应该完成完整的注册流程', async () => {
      // 点击注册按钮
      const registerButton = mockE2E.element(mockE2E.by.id('register-button'));
      await registerButton.tap();

      // 等待注册页面加载
      await mockE2E.waitFor(mockE2E.element(mockE2E.by.id('register-screen')))
        .toBeVisible()
        .withTimeout(5000);

      // 填写邮箱
      const emailInput = mockE2E.element(mockE2E.by.id('email-input'));
      await emailInput.typeText('test@example.com');

      // 填写密码
      const passwordInput = mockE2E.element(mockE2E.by.id('password-input'));
      await passwordInput.typeText('password123');

      // 填写确认密码
      const confirmPasswordInput = mockE2E.element(mockE2E.by.id('confirm-password-input'));
      await confirmPasswordInput.typeText('password123');

      // 填写姓名
      const nameInput = mockE2E.element(mockE2E.by.id('name-input'));
      await nameInput.typeText('测试用户');

      // 点击提交按钮
      const submitButton = mockE2E.element(mockE2E.by.id('submit-button'));
      await submitButton.tap();

      // 验证注册成功
      await mockE2E.waitFor(mockE2E.element(mockE2E.by.text('注册成功')))
        .toBeVisible()
        .withTimeout(10000);

      expect(mockE2E.expect(mockE2E.element(mockE2E.by.text('注册成功'))).toBeVisible()).toBeTruthy();
    });

    it('应该处理注册错误', async () => {
      // 使用已存在的邮箱注册
      const emailInput = mockE2E.element(mockE2E.by.id('email-input'));
      await emailInput.clearText();
      await emailInput.typeText('existing@example.com');

      const submitButton = mockE2E.element(mockE2E.by.id('submit-button'));
      await submitButton.tap();

      // 验证错误消息
      await mockE2E.waitFor(mockE2E.element(mockE2E.by.text('邮箱已被注册')))
        .toBeVisible()
        .withTimeout(5000);

      expect(mockE2E.expect(mockE2E.element(mockE2E.by.text('邮箱已被注册'))).toBeVisible()).toBeTruthy();
    });
  });

  describe('用户登录流程', () => {
    it('应该完成成功登录', async () => {
      // 点击登录按钮
      const loginButton = mockE2E.element(mockE2E.by.id('login-button'));
      await loginButton.tap();

      // 填写登录信息
      const emailInput = mockE2E.element(mockE2E.by.id('email-input'));
      await emailInput.typeText('test@example.com');

      const passwordInput = mockE2E.element(mockE2E.by.id('password-input'));
      await passwordInput.typeText('password123');

      // 点击登录
      const submitButton = mockE2E.element(mockE2E.by.id('login-submit-button'));
      await submitButton.tap();

      // 验证登录成功，进入主页面
      await mockE2E.waitFor(mockE2E.element(mockE2E.by.id('main-screen')))
        .toBeVisible()
        .withTimeout(10000);

      expect(mockE2E.expect(mockE2E.element(mockE2E.by.id('main-screen'))).toBeVisible()).toBeTruthy();
    });

    it('应该处理登录失败', async () => {
      // 使用错误密码登录
      const passwordInput = mockE2E.element(mockE2E.by.id('password-input'));
      await passwordInput.clearText();
      await passwordInput.typeText('wrongpassword');

      const submitButton = mockE2E.element(mockE2E.by.id('login-submit-button'));
      await submitButton.tap();

      // 验证错误消息
      await mockE2E.waitFor(mockE2E.element(mockE2E.by.text('用户名或密码错误')))
        .toBeVisible()
        .withTimeout(5000);

      expect(mockE2E.expect(mockE2E.element(mockE2E.by.text('用户名或密码错误'))).toBeVisible()).toBeTruthy();
    });
  });

  describe('智能体交互流程', () => {
    beforeEach(async () => {
      // 确保用户已登录
      await mockE2E.waitFor(mockE2E.element(mockE2E.by.id('main-screen')))
        .toBeVisible()
        .withTimeout(5000);
    });

    it('应该能够与小艾智能体聊天', async () => {
      // 导航到智能体页面
      const agentTab = mockE2E.element(mockE2E.by.id('agent-tab'));
      await agentTab.tap();

      // 选择小艾智能体
      const xiaoaiCard = mockE2E.element(mockE2E.by.id('xiaoai-card'));
      await xiaoaiCard.tap();

      // 等待聊天界面加载
      await mockE2E.waitFor(mockE2E.element(mockE2E.by.id('chat-screen')))
        .toBeVisible()
        .withTimeout(5000);

      // 发送消息
      const messageInput = mockE2E.element(mockE2E.by.id('message-input'));
      await messageInput.typeText('你好，我想了解一下健康管理');

      const sendButton = mockE2E.element(mockE2E.by.id('send-button'));
      await sendButton.tap();

      // 验证消息发送成功
      await mockE2E.waitFor(mockE2E.element(mockE2E.by.text('你好，我想了解一下健康管理')))
        .toBeVisible()
        .withTimeout(3000);

      // 等待智能体回复
      await mockE2E.waitFor(mockE2E.element(mockE2E.by.text('很高兴为您服务')))
        .toBeVisible()
        .withTimeout(10000);

      expect(mockE2E.expect(mockE2E.element(mockE2E.by.text('很高兴为您服务'))).toBeVisible()).toBeTruthy();
    });

    it('应该能够查看智能体详情', async () => {
      // 点击智能体详情按钮
      const detailButton = mockE2E.element(mockE2E.by.id('agent-detail-button'));
      await detailButton.tap();

      // 验证详情页面
      await mockE2E.waitFor(mockE2E.element(mockE2E.by.id('agent-detail-screen')))
        .toBeVisible()
        .withTimeout(5000);

      expect(mockE2E.expect(mockE2E.element(mockE2E.by.text('小艾'))).toBeVisible()).toBeTruthy();
      expect(mockE2E.expect(mockE2E.element(mockE2E.by.text('健康咨询专家'))).toBeVisible()).toBeTruthy();
    });
  });

  describe('健康数据管理流程', () => {
    it('应该能够添加健康数据', async () => {
      // 导航到健康数据页面
      const healthTab = mockE2E.element(mockE2E.by.id('health-tab'));
      await healthTab.tap();

      // 点击添加数据按钮
      const addButton = mockE2E.element(mockE2E.by.id('add-health-data-button'));
      await addButton.tap();

      // 选择数据类型
      const bloodPressureOption = mockE2E.element(mockE2E.by.id('blood-pressure-option'));
      await bloodPressureOption.tap();

      // 输入数据
      const systolicInput = mockE2E.element(mockE2E.by.id('systolic-input'));
      await systolicInput.typeText('120');

      const diastolicInput = mockE2E.element(mockE2E.by.id('diastolic-input'));
      await diastolicInput.typeText('80');

      // 保存数据
      const saveButton = mockE2E.element(mockE2E.by.id('save-button'));
      await saveButton.tap();

      // 验证数据保存成功
      await mockE2E.waitFor(mockE2E.element(mockE2E.by.text('数据保存成功')))
        .toBeVisible()
        .withTimeout(5000);

      expect(mockE2E.expect(mockE2E.element(mockE2E.by.text('数据保存成功'))).toBeVisible()).toBeTruthy();
    });

    it('应该能够查看健康趋势', async () => {
      // 点击趋势分析按钮
      const trendButton = mockE2E.element(mockE2E.by.id('trend-analysis-button'));
      await trendButton.tap();

      // 验证趋势图表显示
      await mockE2E.waitFor(mockE2E.element(mockE2E.by.id('trend-chart')))
        .toBeVisible()
        .withTimeout(5000);

      expect(mockE2E.expect(mockE2E.element(mockE2E.by.id('trend-chart'))).toBeVisible()).toBeTruthy();
    });
  });

  describe('个人资料管理流程', () => {
    it('应该能够更新个人资料', async () => {
      // 导航到个人资料页面
      const profileTab = mockE2E.element(mockE2E.by.id('profile-tab'));
      await profileTab.tap();

      // 点击编辑按钮
      const editButton = mockE2E.element(mockE2E.by.id('edit-profile-button'));
      await editButton.tap();

      // 更新姓名
      const nameInput = mockE2E.element(mockE2E.by.id('name-input'));
      await nameInput.clearText();
      await nameInput.typeText('更新的用户名');

      // 保存更改
      const saveButton = mockE2E.element(mockE2E.by.id('save-profile-button'));
      await saveButton.tap();

      // 验证更新成功
      await mockE2E.waitFor(mockE2E.element(mockE2E.by.text('资料更新成功')))
        .toBeVisible()
        .withTimeout(5000);

      expect(mockE2E.expect(mockE2E.element(mockE2E.by.text('更新的用户名'))).toBeVisible()).toBeTruthy();
    });
  });

  describe('应用导航流程', () => {
    it('应该能够在不同页面间导航', async () => {
      // 测试底部导航栏
      const tabs = ['home-tab', 'explore-tab', 'life-tab', 'suoke-tab', 'profile-tab'];

      for (const tabId of tabs) {
        const tab = mockE2E.element(mockE2E.by.id(tabId));
        await tab.tap();

        // 验证页面切换
        await mockE2E.waitFor(mockE2E.element(mockE2E.by.id(`${tabId.replace('-tab', '')}-screen`)))
          .toBeVisible()
          .withTimeout(3000);

        expect(mockE2E.expect(mockE2E.element(mockE2E.by.id(`${tabId.replace('-tab', '')}-screen`))).toBeVisible()).toBeTruthy();
      }
    });

    it('应该能够处理返回导航', async () => {
      // 进入详情页面
      const detailButton = mockE2E.element(mockE2E.by.id('detail-button'));
      await detailButton.tap();

      // 点击返回按钮
      const backButton = mockE2E.element(mockE2E.by.id('back-button'));
      await backButton.tap();

      // 验证返回到上一页面
      await mockE2E.waitFor(mockE2E.element(mockE2E.by.id('main-screen')))
        .toBeVisible()
        .withTimeout(3000);

      expect(mockE2E.expect(mockE2E.element(mockE2E.by.id('main-screen'))).toBeVisible()).toBeTruthy();
    });
  });
}); 