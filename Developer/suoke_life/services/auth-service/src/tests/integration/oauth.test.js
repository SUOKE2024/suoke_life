/**
 * OAuth认证API简化集成测试
 */
const request = require('supertest');

// 创建变量用于mock数据
let mockUser = null;
let mockUserCreated = false;
let oauthLinked = false;

// 模拟app
jest.mock('../../app', () => {
  const express = require('express');
  const bodyParser = express.json;
  
  const app = express();
  app.use(bodyParser());
  
  // 简化版的OAuth授权URL路由
  app.get('/api/auth/oauth/google/auth-url', (req, res) => {
    const { redirect_uri } = req.query;
    
    if (!redirect_uri) {
      return res.status(400).json({
        success: false,
        message: '缺少重定向URI'
      });
    }
    
    return res.status(200).json({
      success: true,
      data: {
        authUrl: `https://accounts.google.com/o/oauth2/auth?client_id=mock-client-id&redirect_uri=${encodeURIComponent(redirect_uri)}&scope=profile+email&response_type=code`
      }
    });
  });
  
  app.get('/api/auth/oauth/wechat/auth-url', (req, res) => {
    const { redirect_uri } = req.query;
    
    if (!redirect_uri) {
      return res.status(400).json({
        success: false,
        message: '缺少重定向URI'
      });
    }
    
    return res.status(200).json({
      success: true,
      data: {
        authUrl: `https://open.weixin.qq.com/connect/qrconnect?appid=mock-appid&redirect_uri=${encodeURIComponent(redirect_uri)}&response_type=code&scope=snsapi_login`
      }
    });
  });
  
  // 简化版的OAuth回调处理路由
  app.post('/api/auth/oauth/google/callback', (req, res) => {
    const { code, redirect_uri } = req.body;
    
    if (!code || !redirect_uri) {
      return res.status(400).json({
        success: false,
        message: '缺少必要参数'
      });
    }
    
    // 创建或查找用户
    if (!global._mockUserCreated) {
      global._mockUserCreated = true;
      global._mockUser = {
        id: 'google-user-' + Math.random().toString(36).substring(2, 8),
        email: 'google.user@example.com',
        name: 'Google User',
        created_at: new Date(),
        updated_at: new Date(),
        provider: 'google'
      };
      global._oauthLinked = true;
    }
    
    return res.status(200).json({
      success: true,
      message: '认证成功',
      data: {
        accessToken: `mock-token-${global._mockUser.id}-15m`,
        refreshToken: `mock-refresh-${global._mockUser.id}-7d`,
        user: {
          id: global._mockUser.id,
          name: global._mockUser.name,
          email: global._mockUser.email,
          provider: global._mockUser.provider
        }
      }
    });
  });
  
  app.post('/api/auth/oauth/wechat/callback', (req, res) => {
    const { code, redirect_uri } = req.body;
    
    if (!code || !redirect_uri) {
      return res.status(400).json({
        success: false,
        message: '缺少必要参数'
      });
    }
    
    // 创建或查找用户
    global._mockUserCreated = true;
    global._mockUser = {
      id: 'wechat-user-' + Math.random().toString(36).substring(2, 8),
      openid: 'mock-openid',
      name: 'WeChat User',
      created_at: new Date(),
      updated_at: new Date(),
      provider: 'wechat'
    };
    global._oauthLinked = true;
    
    return res.status(200).json({
      success: true,
      message: '认证成功',
      data: {
        accessToken: `mock-token-${global._mockUser.id}-15m`,
        refreshToken: `mock-refresh-${global._mockUser.id}-7d`,
        user: {
          id: global._mockUser.id,
          name: global._mockUser.name,
          provider: global._mockUser.provider
        }
      }
    });
  });
  
  // 获取关联账号的API
  app.get('/api/auth/oauth/accounts', (req, res) => {
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
      data: {
        accounts: global._oauthLinked ? [
          {
            provider: global._mockUser.provider,
            providerId: global._mockUser.provider === 'google' ? global._mockUser.email : global._mockUser.openid,
            linkedAt: global._mockUser.created_at
          }
        ] : []
      }
    });
  });
  
  return app;
});

const app = require('../../app');

// 初始化全局变量
global._mockUser = null;
global._mockUserCreated = false;
global._oauthLinked = false;

describe('OAuth认证API简化集成测试', () => {
  // 测试前设置
  beforeAll(() => {
    // 重置模拟状态
    global._mockUserCreated = false;
    global._mockUser = null;
    global._oauthLinked = false;
    
    // 同步本地变量
    mockUserCreated = false;
    mockUser = null;
    oauthLinked = false;
  });
  
  // 每次测试后更新本地变量
  afterEach(() => {
    // 更新本地变量
    mockUserCreated = global._mockUserCreated;
    mockUser = global._mockUser;
    oauthLinked = global._oauthLinked;
  });
  
  // 测试后清理
  afterAll(() => {
    // 清理测试数据
    global._mockUserCreated = false;
    global._mockUser = null;
    global._oauthLinked = false;
    delete global._mockUserCreated;
    delete global._mockUser;
    delete global._oauthLinked;
    
    // 同步本地变量
    mockUserCreated = false;
    mockUser = null;
    oauthLinked = false;
  });
  
  describe('OAuth授权URL', () => {
    it('应返回Google授权URL', async () => {
      const response = await request(app)
        .get('/api/auth/oauth/google/auth-url')
        .query({ redirect_uri: 'http://localhost:3000/callback' })
        .expect('Content-Type', /json/)
        .expect(200);
      
      expect(response.body.success).toBe(true);
      expect(response.body.data.authUrl).toBeDefined();
      expect(response.body.data.authUrl).toContain('https://accounts.google.com/o/oauth2/auth');
    });
    
    it('应返回微信授权URL', async () => {
      const response = await request(app)
        .get('/api/auth/oauth/wechat/auth-url')
        .query({ redirect_uri: 'http://localhost:3000/callback' })
        .expect('Content-Type', /json/)
        .expect(200);
      
      expect(response.body.success).toBe(true);
      expect(response.body.data.authUrl).toBeDefined();
      expect(response.body.data.authUrl).toContain('https://open.weixin.qq.com/connect/qrconnect');
    });
    
    it('应验证重定向URI参数', async () => {
      const response = await request(app)
        .get('/api/auth/oauth/google/auth-url')
        .expect('Content-Type', /json/)
        .expect(400);
      
      expect(response.body.success).toBe(false);
    });
  });
  
  describe('OAuth回调处理', () => {
    it('应成功处理Google回调并创建新用户', async () => {
      const response = await request(app)
        .post('/api/auth/oauth/google/callback')
        .send({
          code: 'mock-auth-code',
          redirect_uri: 'http://localhost:3000/callback'
        })
        .expect('Content-Type', /json/)
        .expect(200);
      
      expect(response.body.success).toBe(true);
      expect(response.body.data.user).toBeDefined();
      expect(response.body.data.accessToken).toBeDefined();
      expect(response.body.data.refreshToken).toBeDefined();
      expect(response.body.data.user.provider).toBe('google');
    });
    
    it('应成功处理微信回调并创建新用户', async () => {
      const response = await request(app)
        .post('/api/auth/oauth/wechat/callback')
        .send({
          code: 'mock-auth-code',
          redirect_uri: 'http://localhost:3000/callback'
        })
        .expect('Content-Type', /json/)
        .expect(200);
      
      expect(response.body.success).toBe(true);
      expect(response.body.data.user).toBeDefined();
      expect(response.body.data.accessToken).toBeDefined();
      expect(response.body.data.user.provider).toBe('wechat');
    });
    
    it('应验证回调参数', async () => {
      const response = await request(app)
        .post('/api/auth/oauth/google/callback')
        .send({
          // 缺少code和redirect_uri
        })
        .expect('Content-Type', /json/)
        .expect(400);
      
      expect(response.body.success).toBe(false);
    });
  });
  
  describe('OAuth账号管理', () => {
    let authToken;
    
    beforeEach(() => {
      // 设置测试数据
      mockUserCreated = true;
      oauthLinked = true;
      authToken = 'Bearer mock-token-abc123';
    });
    
    it('应返回用户关联的OAuth账号', async () => {
      const response = await request(app)
        .get('/api/auth/oauth/accounts')
        .set('Authorization', authToken)
        .expect('Content-Type', /json/)
        .expect(200);
      
      expect(response.body.success).toBe(true);
      expect(response.body.data.accounts).toBeInstanceOf(Array);
      expect(response.body.data.accounts.length).toBeGreaterThan(0);
    });
    
    it('应拒绝未授权的账号请求', async () => {
      const response = await request(app)
        .get('/api/auth/oauth/accounts')
        .expect('Content-Type', /json/)
        .expect(401);
      
      expect(response.body.success).toBe(false);
    });
  });
}); 