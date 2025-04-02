import request from 'supertest';
import { createTestServer } from '../integration/test-server';
import jwt from 'jsonwebtoken';
import { randomBytes } from 'crypto';

// 测试服务器
const app = createTestServer();

// 安全测试套件
describe('API安全测试', () => {
  
  // JWT认证测试
  describe('JWT认证', () => {
    const API_ENDPOINT = '/api/agents';
    
    // 生成有效的测试JWT令牌
    const generateValidToken = () => {
      // 注意：在实际生产中应使用环境变量管理密钥
      const secret = process.env.JWT_SECRET || 'test-secret';
      return jwt.sign(
        { 
          userId: 'test-user', 
          role: 'user',
          exp: Math.floor(Date.now() / 1000) + 3600 // 1小时后过期
        }, 
        secret
      );
    };
    
    // 生成已过期的测试JWT令牌
    const generateExpiredToken = () => {
      const secret = process.env.JWT_SECRET || 'test-secret';
      return jwt.sign(
        { 
          userId: 'test-user', 
          role: 'user',
          exp: Math.floor(Date.now() / 1000) - 3600 // 1小时前过期
        }, 
        secret
      );
    };
    
    // 生成带有无效签名的JWT令牌
    const generateInvalidSignatureToken = () => {
      const wrongSecret = 'wrong-secret';
      return jwt.sign(
        { 
          userId: 'test-user', 
          role: 'user',
          exp: Math.floor(Date.now() / 1000) + 3600
        }, 
        wrongSecret
      );
    };
    
    test('应拒绝没有认证令牌的请求', async () => {
      const response = await request(app).get(API_ENDPOINT);
      expect(response.status).toBe(401);
    });
    
    test('应接受带有有效认证令牌的请求', async () => {
      const validToken = generateValidToken();
      const response = await request(app)
        .get(API_ENDPOINT)
        .set('Authorization', `Bearer ${validToken}`);
      
      expect(response.status).not.toBe(401); // 可能是200或其他状态码，但不应是401
    });
    
    test('应拒绝带有过期认证令牌的请求', async () => {
      const expiredToken = generateExpiredToken();
      const response = await request(app)
        .get(API_ENDPOINT)
        .set('Authorization', `Bearer ${expiredToken}`);
      
      expect(response.status).toBe(401);
    });
    
    test('应拒绝带有无效签名的认证令牌的请求', async () => {
      const invalidToken = generateInvalidSignatureToken();
      const response = await request(app)
        .get(API_ENDPOINT)
        .set('Authorization', `Bearer ${invalidToken}`);
      
      expect(response.status).toBe(401);
    });
    
    test('应拒绝带有篡改荷载的认证令牌的请求', async () => {
      // 获取有效令牌并篡改
      const validToken = generateValidToken();
      const parts = validToken.split('.');
      
      // 解码荷载
      const decodedPayload = JSON.parse(Buffer.from(parts[1], 'base64').toString());
      
      // 篡改荷载（提升权限）
      decodedPayload.role = 'admin';
      
      // 重新编码荷载
      const tamperedPayload = Buffer.from(JSON.stringify(decodedPayload)).toString('base64');
      
      // 构建篡改后的令牌（保持原始头部和签名）
      const tamperedToken = `${parts[0]}.${tamperedPayload}.${parts[2]}`;
      
      const response = await request(app)
        .get(API_ENDPOINT)
        .set('Authorization', `Bearer ${tamperedToken}`);
      
      expect(response.status).toBe(401);
    });
  });
  
  // CSRF保护测试
  describe('CSRF保护', () => {
    const API_ENDPOINT = '/api/knowledge/rag';
    const VALID_REFERER = 'https://suoke.life';
    const INVALID_REFERER = 'https://evil-site.com';
    
    test('应拒绝来自未授权来源的POST请求', async () => {
      const validToken = jwt.sign(
        { userId: 'test-user', role: 'user' },
        process.env.JWT_SECRET || 'test-secret'
      );
      
      const response = await request(app)
        .post(API_ENDPOINT)
        .set('Authorization', `Bearer ${validToken}`)
        .set('Referer', INVALID_REFERER)
        .set('Origin', INVALID_REFERER)
        .send({
          query: '测试查询',
          userId: 'test-user'
        });
      
      // 如果启用了CSRF保护，应返回403状态码
      // 注意：此测试可能需要根据实际CSRF保护策略调整
      expect([403, 401]).toContain(response.status);
    });
    
    test('应接受来自授权来源的POST请求', async () => {
      const validToken = jwt.sign(
        { userId: 'test-user', role: 'user' },
        process.env.JWT_SECRET || 'test-secret'
      );
      
      const response = await request(app)
        .post(API_ENDPOINT)
        .set('Authorization', `Bearer ${validToken}`)
        .set('Referer', VALID_REFERER)
        .set('Origin', VALID_REFERER)
        .send({
          query: '测试查询',
          userId: 'test-user'
        });
      
      // 如果启用了CSRF保护，且来源有效，不应返回403状态码
      expect(response.status).not.toBe(403);
    });
  });
  
  // 速率限制测试
  describe('速率限制保护', () => {
    const API_ENDPOINT = '/api/agents';
    const REQUEST_COUNT = 20; // 超过默认限制的请求数
    
    test('应在多次请求后触发速率限制', async () => {
      const validToken = jwt.sign(
        { userId: 'test-user', role: 'user' },
        process.env.JWT_SECRET || 'test-secret'
      );
      
      // 发送多个请求
      const requests = [];
      for (let i = 0; i < REQUEST_COUNT; i++) {
        requests.push(
          request(app)
            .get(API_ENDPOINT)
            .set('Authorization', `Bearer ${validToken}`)
        );
      }
      
      // 执行所有请求
      const responses = await Promise.all(requests);
      
      // 至少有一个请求应触发速率限制
      // 注意：根据实际速率限制配置可能需要调整
      const rateLimitedResponses = responses.filter(res => res.status === 429);
      expect(rateLimitedResponses.length).toBeGreaterThan(0);
    });
  });
  
  // 请求参数验证测试
  describe('输入验证', () => {
    const API_ENDPOINT = '/api/knowledge/search';
    
    test('应拒绝包含SQL注入攻击的查询', async () => {
      const validToken = jwt.sign(
        { userId: 'test-user', role: 'user' },
        process.env.JWT_SECRET || 'test-secret'
      );
      
      const sqlInjectionQuery = "'; DROP TABLE users; --";
      
      const response = await request(app)
        .get(`${API_ENDPOINT}?query=${encodeURIComponent(sqlInjectionQuery)}`)
        .set('Authorization', `Bearer ${validToken}`);
      
      // 应返回400错误，表示参数验证失败
      expect(response.status).toBe(400);
    });
    
    test('应拒绝XSS攻击负载', async () => {
      const validToken = jwt.sign(
        { userId: 'test-user', role: 'user' },
        process.env.JWT_SECRET || 'test-secret'
      );
      
      const xssPayload = "<script>alert('XSS')</script>";
      
      const response = await request(app)
        .get(`${API_ENDPOINT}?query=${encodeURIComponent(xssPayload)}`)
        .set('Authorization', `Bearer ${validToken}`);
      
      // 应返回400错误，表示参数验证失败
      expect(response.status).toBe(400);
    });
    
    test('应正确验证并清理合法的复杂查询', async () => {
      const validToken = jwt.sign(
        { userId: 'test-user', role: 'user' },
        process.env.JWT_SECRET || 'test-secret'
      );
      
      const complexQuery = "维生素D对人体的作用是什么？需要详细解释它的代谢过程。";
      
      const response = await request(app)
        .get(`${API_ENDPOINT}?query=${encodeURIComponent(complexQuery)}`)
        .set('Authorization', `Bearer ${validToken}`);
      
      // 应接受合法查询
      expect(response.status).not.toBe(400);
    });
  });
  
  // 敏感数据泄露测试
  describe('敏感数据保护', () => {
    const API_ENDPOINT = '/api/users/profile';
    
    test('错误响应不应泄露敏感的堆栈跟踪', async () => {
      const validToken = jwt.sign(
        { userId: 'test-user', role: 'user' },
        process.env.JWT_SECRET || 'test-secret'
      );
      
      // 故意发送错误请求
      const response = await request(app)
        .get(API_ENDPOINT)
        .set('Authorization', `Bearer ${validToken}`);
      
      // 可能是404或其他错误
      expect(response.status).toBeGreaterThanOrEqual(400);
      
      // 响应中不应包含敏感的堆栈跟踪
      expect(response.text).not.toContain("at ");
      expect(response.text).not.toContain("node_modules");
      expect(response.text).not.toContain("Error:");
    });
  });
}); 