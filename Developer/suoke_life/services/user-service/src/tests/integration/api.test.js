/**
 * API集成测试
 * 测试主要API端点功能
 */
const request = require('supertest');
const { app } = require('../../app');
const { expect } = require('chai');
const sinon = require('sinon');
const userRepository = require('../../repositories/user.repository');
const socialShareRepository = require('../../repositories/social-share.repository');
const userMatchRepository = require('../../repositories/user-match.repository');
const jwt = require('jsonwebtoken');

describe('API集成测试', () => {
  let sandbox;
  let authToken;
  
  before(() => {
    // 创建测试用JWT令牌
    authToken = jwt.sign(
      { id: 'test-user-id', username: 'testuser', role: 'user' },
      process.env.JWT_SECRET || 'test-secret',
      { expiresIn: '1h' }
    );
  });
  
  beforeEach(() => {
    sandbox = sinon.createSandbox();
  });
  
  afterEach(() => {
    sandbox.restore();
  });
  
  describe('API文档', () => {
    it('应该返回API文档', async () => {
      const response = await request(app)
        .get('/api/api-docs')
        .expect(200);
      
      expect(response.body).to.have.property('service', 'user-service');
      expect(response.body).to.have.property('endpoints');
      expect(response.body.endpoints).to.have.property('users');
      expect(response.body.endpoints).to.have.property('socialShares');
      expect(response.body.endpoints).to.have.property('userMatches');
    });
  });
  
  describe('社交分享API', () => {
    it('应该创建分享', async () => {
      // 模拟用户存在
      sandbox.stub(userRepository, 'getUserById').resolves({ id: 'test-user-id', username: 'testuser' });
      
      // 模拟分享创建
      sandbox.stub(socialShareRepository, 'createShare').resolves({
        id: 'share-123',
        userId: 'test-user-id',
        shareType: 'content',
        title: '测试分享',
        createdAt: new Date()
      });
      
      const response = await request(app)
        .post('/api/social-shares')
        .set('Authorization', `Bearer ${authToken}`)
        .send({
          shareType: 'content',
          title: '测试分享',
          description: '测试分享描述'
        })
        .expect(201);
      
      expect(response.body).to.have.property('success', true);
      expect(response.body).to.have.property('data');
      expect(response.body.data).to.have.property('id', 'share-123');
    });
    
    it('应该获取分享列表', async () => {
      // 模拟用户存在
      sandbox.stub(userRepository, 'getUserById').resolves({ id: 'test-user-id', username: 'testuser' });
      
      // 模拟分享列表
      sandbox.stub(socialShareRepository, 'getUserShares').resolves([
        {
          id: 'share-123',
          userId: 'test-user-id',
          shareType: 'content',
          title: '测试分享1',
          createdAt: new Date()
        },
        {
          id: 'share-456',
          userId: 'test-user-id',
          shareType: 'health',
          title: '测试分享2',
          createdAt: new Date()
        }
      ]);
      
      const response = await request(app)
        .get('/api/social-shares/user/test-user-id')
        .expect(200);
      
      expect(response.body).to.have.property('success', true);
      expect(response.body).to.have.property('data');
      expect(response.body.data).to.be.an('array').with.lengthOf(2);
    });
  });
  
  describe('用户匹配API', () => {
    it('应该查找潜在匹配用户', async () => {
      // 模拟用户匹配服务
      sandbox.stub(userMatchRepository, 'getUserInterestVector').resolves({
        userId: 'test-user-id',
        vector: [0.5, 0.7, 0.3, 0.8]
      });
      
      sandbox.stub(userMatchRepository, 'findSimilarVectors').resolves([
        {
          userId: 'user-123',
          username: 'user123',
          similarity: 0.85,
          matchedInterests: ['健康', '中医']
        },
        {
          userId: 'user-456',
          username: 'user456',
          similarity: 0.75,
          matchedInterests: ['健康', '养生']
        }
      ]);
      
      const response = await request(app)
        .get('/api/user-matches/potential')
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);
      
      expect(response.body).to.have.property('success', true);
      expect(response.body).to.have.property('data');
      expect(response.body.data).to.be.an('array').with.lengthOf(2);
    });
  });
  
  describe('健康检查', () => {
    it('应该返回健康状态', async () => {
      const response = await request(app)
        .get('/health')
        .expect(200);
      
      expect(response.body).to.have.property('status', 'UP');
    });
  });
});