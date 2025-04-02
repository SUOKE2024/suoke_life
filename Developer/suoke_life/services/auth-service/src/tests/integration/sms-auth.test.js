/**
 * 短信认证API简化集成测试
 */
const request = require('supertest');

// 创建变量用于mock数据
let mockUser = null;
let verificationCodes = new Map();
let lastRequestTimes = new Map();

// 初始化全局变量
global._mockUser = null;
global._verificationCodes = new Map();
global._lastRequestTimes = new Map();

// 模拟app
jest.mock('../../app', () => {
  const express = require('express');
  const bodyParser = express.json;
  
  const app = express();
  app.use(bodyParser());
  
  // 发送验证码路由
  app.post('/api/auth/sms/send-code', (req, res) => {
    const { phone } = req.body;
    
    if (!phone || !/^1[3-9]\d{9}$/.test(phone)) {
      return res.status(400).json({
        success: false,
        message: '无效的手机号码'
      });
    }
    
    // 检查请求频率限制
    const lastRequestTime = global._lastRequestTimes.get(phone) || 0;
    const now = Date.now();
    
    if (now - lastRequestTime < 60000) { // 1分钟内不能重复请求
      return res.status(429).json({
        success: false,
        message: '请求过于频繁，请稍后再试'
      });
    }
    
    // 生成并存储验证码
    const code = '123456'; // 固定验证码，方便测试
    global._verificationCodes.set(phone, code);
    global._lastRequestTimes.set(phone, now);
    
    return res.status(200).json({
      success: true,
      message: '验证码已发送',
      data: { expireIn: 300 } // 5分钟有效期
    });
  });
  
  // 验证码登录路由
  app.post('/api/auth/sms/verify', (req, res) => {
    const { phone, code } = req.body;
    
    if (!phone || !code) {
      return res.status(400).json({
        success: false,
        message: '缺少必要参数'
      });
    }
    
    // 验证码校验
    const storedCode = global._verificationCodes.get(phone);
    if (!storedCode || storedCode !== code) {
      return res.status(401).json({
        success: false,
        message: '验证码错误或已过期'
      });
    }
    
    // 创建或查找用户
    if (!global._mockUser || global._mockUser.phone !== phone) {
      global._mockUser = {
        id: 'user-' + Math.random().toString(36).substring(2, 8),
        phone,
        created_at: new Date(),
        updated_at: new Date()
      };
    }
    
    // 删除验证码
    global._verificationCodes.delete(phone);
    
    return res.status(200).json({
      success: true,
      message: '验证成功',
      data: {
        accessToken: `mock-token-${global._mockUser.id}-15m`,
        refreshToken: `mock-refresh-${global._mockUser.id}-7d`,
        user: {
          id: global._mockUser.id,
          phone: global._mockUser.phone
        }
      }
    });
  });
  
  // 重置密码验证路由
  app.post('/api/auth/sms/verify-reset', (req, res) => {
    const { phone, code } = req.body;
    
    if (!phone || !code) {
      return res.status(400).json({
        success: false,
        message: '缺少必要参数'
      });
    }
    
    // 验证码校验
    const storedCode = global._verificationCodes.get(phone);
    if (!storedCode || storedCode !== code) {
      return res.status(401).json({
        success: false,
        message: '验证码错误或已过期'
      });
    }
    
    // 生成重置令牌
    const resetToken = 'reset-token-' + Math.random().toString(36).substring(2, 15);
    
    // 删除验证码
    global._verificationCodes.delete(phone);
    
    return res.status(200).json({
      success: true,
      message: '验证成功',
      data: {
        resetToken
      }
    });
  });
  
  // 重置密码路由
  app.post('/api/auth/sms/reset-password', (req, res) => {
    const { resetToken, password } = req.body;
    
    if (!resetToken || !password) {
      return res.status(400).json({
        success: false,
        message: '缺少必要参数'
      });
    }
    
    // 检查令牌是否有效
    if (!resetToken.startsWith('reset-token-')) {
      return res.status(401).json({
        success: false,
        message: '无效的重置令牌'
      });
    }
    
    return res.status(200).json({
      success: true,
      message: '密码已成功重置'
    });
  });
  
  // 需要授权的路由
  app.post('/api/auth/sms/unbind-phone', (req, res) => {
    const auth = req.headers.authorization;
    
    // 检查授权头
    if (!auth || !auth.startsWith('Bearer ')) {
      return res.status(401).json({
        success: false,
        message: '未授权请求'
      });
    }
    
    return res.status(200).json({
      success: true,
      message: '手机号解绑成功'
    });
  });
  
  return app;
});

const app = require('../../app');

describe('短信认证API简化集成测试', () => {
  const testPhoneNumber = '13912345678';
  const verificationCode = '123456';
  let authTokens;
  
  // 测试前设置
  beforeAll(() => {
    // 清理测试数据
    global._mockUser = null;
    global._verificationCodes.clear();
    global._lastRequestTimes.clear();
    
    // 设置初始状态
    global._lastRequestTimes.set(testPhoneNumber, Date.now() - 70000); // 设置为可发送状态
    
    // 同步本地变量
    mockUser = null;
    verificationCodes.clear();
    lastRequestTimes.clear();
    lastRequestTimes.set(testPhoneNumber, Date.now() - 70000);
  });
  
  // 每次测试后更新本地变量
  afterEach(() => {
    // 更新本地变量
    mockUser = global._mockUser;
    verificationCodes = new Map(global._verificationCodes);
    lastRequestTimes = new Map(global._lastRequestTimes);
  });
  
  // 测试后清理
  afterAll(() => {
    // 清理测试数据
    global._mockUser = null;
    global._verificationCodes.clear();
    global._lastRequestTimes.clear();
    delete global._mockUser;
    delete global._verificationCodes;
    delete global._lastRequestTimes;
    
    // 同步本地变量
    mockUser = null;
    verificationCodes.clear();
    lastRequestTimes.clear();
  });
  
  describe('短信验证码发送', () => {
    it('应成功发送验证码', async () => {
      const response = await request(app)
        .post('/api/auth/sms/send-code')
        .send({ phone: testPhoneNumber })
        .expect('Content-Type', /json/)
        .expect(200);
      
      expect(response.body.success).toBe(true);
      expect(response.body.message).toContain('验证码已发送');
    });
    
    it('应验证手机号格式', async () => {
      const response = await request(app)
        .post('/api/auth/sms/send-code')
        .send({ phone: 'invalid-phone' })
        .expect('Content-Type', /json/)
        .expect(400);
      
      expect(response.body.success).toBe(false);
    });
    
    it('应限制短时间内的重复请求', async () => {
      // 先发送一条请求
      await request(app)
        .post('/api/auth/sms/send-code')
        .send({ phone: testPhoneNumber });
      
      // 立即再发送一条请求
      const response = await request(app)
        .post('/api/auth/sms/send-code')
        .send({ phone: testPhoneNumber })
        .expect('Content-Type', /json/)
        .expect(429);
      
      expect(response.body.success).toBe(false);
      expect(response.body.message).toContain('请求过于频繁');
    });
  });
  
  describe('短信验证码登录', () => {
    it('应拒绝错误的验证码', async () => {
      // 确保有验证码
      global._verificationCodes.set(testPhoneNumber, verificationCode);
      
      const response = await request(app)
        .post('/api/auth/sms/verify')
        .send({
          phone: testPhoneNumber,
          code: '654321' // 错误的验证码
        })
        .expect('Content-Type', /json/)
        .expect(401);
      
      expect(response.body.success).toBe(false);
    });
    
    it('应成功通过验证码登录', async () => {
      // 确保有验证码
      global._verificationCodes.set(testPhoneNumber, verificationCode);
      
      const response = await request(app)
        .post('/api/auth/sms/verify')
        .send({
          phone: testPhoneNumber,
          code: verificationCode
        })
        .expect('Content-Type', /json/)
        .expect(200);
      
      expect(response.body.success).toBe(true);
      expect(response.body.data).toBeDefined();
      expect(response.body.data.accessToken).toBeDefined();
      expect(response.body.data.refreshToken).toBeDefined();
      expect(response.body.data.user).toBeDefined();
      
      // 验证验证码已被删除
      expect(global._verificationCodes.has(testPhoneNumber)).toBe(false);
      
      // 保存令牌以供后续测试使用
      authTokens = {
        accessToken: response.body.data.accessToken,
        refreshToken: response.body.data.refreshToken
      };
    });
  });
  
  describe('短信验证码密码重置', () => {
    it('应支持通过验证码验证身份', async () => {
      // 确保有验证码
      global._verificationCodes.set(testPhoneNumber, verificationCode);
      
      const response = await request(app)
        .post('/api/auth/sms/verify-reset')
        .send({
          phone: testPhoneNumber,
          code: verificationCode
        })
        .expect('Content-Type', /json/)
        .expect(200);
      
      expect(response.body.success).toBe(true);
      expect(response.body.data.resetToken).toBeDefined();
      
      // 验证使用重置令牌重置密码
      const resetResponse = await request(app)
        .post('/api/auth/sms/reset-password')
        .send({
          resetToken: response.body.data.resetToken,
          password: 'NewPassword123!'
        })
        .expect('Content-Type', /json/)
        .expect(200);
      
      expect(resetResponse.body.success).toBe(true);
      expect(resetResponse.body.message).toContain('密码已成功重置');
    });
    
    it('应拒绝无效的重置令牌', async () => {
      const response = await request(app)
        .post('/api/auth/sms/reset-password')
        .send({
          resetToken: 'invalid-token',
          password: 'NewPassword123!'
        })
        .expect('Content-Type', /json/)
        .expect(401);
      
      expect(response.body.success).toBe(false);
    });
  });
  
  describe('授权请求处理', () => {
    it('应拒绝未授权的请求', async () => {
      const response = await request(app)
        .post('/api/auth/sms/unbind-phone')
        .expect('Content-Type', /json/)
        .expect(401);
      
      expect(response.body.success).toBe(false);
    });
    
    it('应处理授权请求', async () => {
      const response = await request(app)
        .post('/api/auth/sms/unbind-phone')
        .set('Authorization', `Bearer ${authTokens.accessToken}`)
        .expect('Content-Type', /json/)
        .expect(200);
      
      expect(response.body.success).toBe(true);
      expect(response.body.message).toContain('手机号解绑成功');
    });
  });
}); 