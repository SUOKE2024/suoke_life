import request from 'supertest';
import express from 'express';
import { describe, it, expect, beforeAll, afterAll } from '@jest/globals';

// 创建一个简单的Express应用用于测试
const app = express();
app.get('/health/live', (req, res) => res.status(200).json({ status: 'UP' }));
app.get('/api/v1/test', (req, res) => res.json({ message: '测试接口' }));

describe('API集成测试', () => {
  it('健康检查端点应返回200状态码', async () => {
    const response = await request(app).get('/health/live');
    expect(response.status).toBe(200);
    expect(response.body).toEqual({ status: 'UP' });
  });

  it('测试API端点应返回正确消息', async () => {
    const response = await request(app).get('/api/v1/test');
    expect(response.status).toBe(200);
    expect(response.body).toEqual({ message: '测试接口' });
  });

  it('访问不存在的端点应返回404', async () => {
    const response = await request(app).get('/not-exists');
    expect(response.status).toBe(404);
  });
}); 