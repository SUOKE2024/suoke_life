const request = require('supertest');
const { app } = require('../../app');
const { db } = require('../../config/database');
const redis = require('../../utils/redis');
const { generateTestJWT } = require('../utils.test');

describe('生物识别认证API集成测试', () => {
  let testToken;
  
  beforeAll(async () => {
    // 创建测试用户和测试JWT令牌
    const testUser = {
      id: 'test-integration-user',
      email: 'biometric-test@suoke.life',
      username: 'biometricTestUser'
    };
    
    testToken = await generateTestJWT(testUser);
    
    // 确保测试用户存在
    try {
      await db('users').where('id', testUser.id).delete();
      await db('users').insert({
        id: testUser.id,
        email: testUser.email,
        username: testUser.username,
        password: 'hashed_password',
        created_at: new Date(),
        updated_at: new Date()
      });
    } catch (error) {
      console.error('测试用户创建失败', error);
    }
  });
  
  afterAll(async () => {
    // 清理测试数据
    try {
      await db('biometric_credentials').where('user_id', 'test-integration-user').delete();
      await db('users').where('id', 'test-integration-user').delete();
    } catch (error) {
      console.error('测试数据清理失败', error);
    }
  });
  
  describe('POST /api/auth/biometric/register', () => {
    it('应成功注册生物识别凭据', async () => {
      const response = await request(app)
        .post('/api/auth/biometric/register')
        .set('Authorization', `Bearer ${testToken}`)
        .send({
          userId: 'test-integration-user',
          deviceId: 'test-device-id',
          biometricType: 'fingerprint',
          publicKey: 'test-public-key',
          deviceInfo: {
            os: 'iOS',
            model: 'iPhone Test',
            osVersion: '16.0'
          },
          attestation: {
            challenge: 'test-challenge',
            attestationData: 'test-attestation-data'
          }
        });
      
      expect(response.status).toBe(201);
      expect(response.body.success).toBe(true);
      expect(response.body.data).toHaveProperty('id');
      expect(response.body.data.biometricType).toBe('fingerprint');
      expect(response.body.data.deviceId).toBe('test-device-id');
    });
    
    it('没有有效令牌时应返回401错误', async () => {
      const response = await request(app)
        .post('/api/auth/biometric/register')
        .send({
          userId: 'test-integration-user',
          deviceId: 'test-device-id',
          biometricType: 'fingerprint',
          publicKey: 'test-public-key'
        });
      
      expect(response.status).toBe(401);
    });
    
    it('缺少必要字段时应返回400错误', async () => {
      const response = await request(app)
        .post('/api/auth/biometric/register')
        .set('Authorization', `Bearer ${testToken}`)
        .send({
          // 缺少必要字段
          userId: 'test-integration-user'
        });
      
      expect(response.status).toBe(400);
    });
  });
  
  describe('POST /api/auth/biometric/challenge', () => {
    it('应成功生成生物识别挑战值', async () => {
      const response = await request(app)
        .post('/api/auth/biometric/challenge')
        .set('Authorization', `Bearer ${testToken}`)
        .send({
          userId: 'test-integration-user',
          deviceId: 'test-device-id'
        });
      
      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.data).toHaveProperty('challenge');
      expect(response.body.data.userId).toBe('test-integration-user');
      expect(response.body.data.deviceId).toBe('test-device-id');
    });
  });
  
  describe('POST /api/auth/biometric/verify', () => {
    beforeEach(async () => {
      // 设置挑战值到Redis
      await redis.set(
        `biometric:challenge:test-integration-user:test-device-id`,
        'test-challenge-123',
        'EX',
        300
      );
      
      // 确保生物识别凭据存在
      const existingCred = await db('biometric_credentials')
        .where({
          user_id: 'test-integration-user',
          device_id: 'test-device-id',
          biometric_type: 'fingerprint'
        })
        .first();
      
      if (!existingCred) {
        await db('biometric_credentials').insert({
          id: 'test-cred-id',
          user_id: 'test-integration-user',
          device_id: 'test-device-id',
          biometric_type: 'fingerprint',
          public_key: 'test-public-key',
          device_info: JSON.stringify({ os: 'iOS', model: 'iPhone Test' }),
          created_at: new Date(),
          updated_at: new Date(),
          expires_at: new Date(Date.now() + 86400000) // 明天
        });
      }
    });
    
    it('应成功验证生物识别凭据', async () => {
      // 模拟生物识别服务的验证方法
      jest.spyOn(require('../../services/biometric.service').prototype, 'verify')
        .mockResolvedValueOnce({
          isValid: true,
          userId: 'test-integration-user',
          deviceId: 'test-device-id',
          biometricType: 'fingerprint',
          verifiedAt: new Date()
        });
      
      const response = await request(app)
        .post('/api/auth/biometric/verify')
        .set('Authorization', `Bearer ${testToken}`)
        .send({
          userId: 'test-integration-user',
          deviceId: 'test-device-id',
          biometricType: 'fingerprint',
          signature: 'test-signature',
          challenge: 'test-challenge-123'
        });
      
      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.data.isValid).toBe(true);
    });
    
    it('挑战值无效时应返回400错误', async () => {
      const response = await request(app)
        .post('/api/auth/biometric/verify')
        .set('Authorization', `Bearer ${testToken}`)
        .send({
          userId: 'test-integration-user',
          deviceId: 'test-device-id',
          biometricType: 'fingerprint',
          signature: 'test-signature',
          challenge: 'invalid-challenge'
        });
      
      expect(response.status).toBe(400);
    });
  });
  
  describe('GET /api/auth/biometric/credentials', () => {
    it('应成功获取用户生物识别凭据列表', async () => {
      const response = await request(app)
        .get('/api/auth/biometric/credentials')
        .set('Authorization', `Bearer ${testToken}`)
        .query({ userId: 'test-integration-user' });
      
      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(Array.isArray(response.body.data)).toBe(true);
    });
  });
  
  describe('DELETE /api/auth/biometric/credentials/:id', () => {
    it('应成功删除生物识别凭据', async () => {
      // 首先确保至少有一个凭据存在
      let credId = 'test-cred-id';
      const existingCred = await db('biometric_credentials')
        .where({
          user_id: 'test-integration-user',
          device_id: 'test-device-id'
        })
        .first();
      
      if (existingCred) {
        credId = existingCred.id;
      } else {
        await db('biometric_credentials').insert({
          id: credId,
          user_id: 'test-integration-user',
          device_id: 'test-device-id',
          biometric_type: 'fingerprint',
          public_key: 'test-public-key',
          device_info: JSON.stringify({ os: 'iOS', model: 'iPhone Test' }),
          created_at: new Date(),
          updated_at: new Date(),
          expires_at: new Date(Date.now() + 86400000) // 明天
        });
      }
      
      const response = await request(app)
        .delete(`/api/auth/biometric/credentials/${credId}`)
        .set('Authorization', `Bearer ${testToken}`)
        .send({ userId: 'test-integration-user' });
      
      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
    });
    
    it('凭据ID不存在时应返回404错误', async () => {
      const response = await request(app)
        .delete('/api/auth/biometric/credentials/non-existent-id')
        .set('Authorization', `Bearer ${testToken}`)
        .send({ userId: 'test-integration-user' });
      
      expect(response.status).toBe(404);
    });
  });
}); 