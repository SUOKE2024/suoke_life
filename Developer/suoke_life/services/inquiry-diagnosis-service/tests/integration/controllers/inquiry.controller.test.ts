import 'reflect-metadata';
import express from 'express';
import request from 'supertest';
import { Container } from 'typedi';
import { InquiryController } from '../../../src/controllers/inquiry.controller';
import { InquiryService } from '../../../src/services/inquiry.service';
import { errorMiddleware } from '../../../src/middlewares/error.middleware';
import { validationMiddleware } from '../../../src/middlewares/validation.middleware';
import * as inquiryValidation from '../../../src/validations/inquiry-validation';

// 模拟依赖
jest.mock('../../../src/services/inquiry.service');

describe('InquiryController (集成测试)', () => {
  let app: express.Application;
  let mockInquiryService: jest.Mocked<InquiryService>;

  beforeAll(() => {
    // 创建Express应用
    app = express();
    app.use(express.json());
    
    // 设置模拟实例
    mockInquiryService = {
      createSession: jest.fn(),
      processInquiry: jest.fn(),
      getExtractedSymptoms: jest.fn(),
      endSession: jest.fn(),
      getUserHealthRecords: jest.fn(),
      createHealthRecord: jest.fn(),
      updateSessionPreferences: jest.fn(),
    } as unknown as jest.Mocked<InquiryService>;
    
    // 注册模拟实例到容器
    Container.set(InquiryService, mockInquiryService);
    
    // 设置路由
    const controller = new InquiryController();
    
    // 创建会话路由
    app.post(
      '/api/inquiry/sessions',
      validationMiddleware(inquiryValidation.createInquirySessionSchema),
      controller.createSession
    );
    
    // 处理问诊请求路由
    app.post(
      '/api/inquiry/sessions/:sessionId/inquiries',
      validationMiddleware(inquiryValidation.processInquirySchema),
      controller.processInquiry
    );
    
    // 获取症状列表路由
    app.get(
      '/api/inquiry/sessions/:sessionId/symptoms',
      controller.getExtractedSymptoms
    );
    
    // 结束会话路由
    app.post(
      '/api/inquiry/sessions/:sessionId/end',
      validationMiddleware(inquiryValidation.endSessionSchema),
      controller.endSession
    );
    
    // 设置错误处理中间件
    app.use(errorMiddleware);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('POST /api/inquiry/sessions', () => {
    it('应创建新的问诊会话并返回201状态码', async () => {
      // 准备测试数据
      const requestBody = {
        userId: 'user123',
        patientInfo: { age: 30, gender: 'male' },
        preferences: { language: 'zh-CN' }
      };
      
      const mockSession = {
        sessionId: 'session123',
        userId: 'user123',
        status: 'active',
        patientInfo: { age: 30, gender: 'male' },
        preferences: { language: 'zh-CN' },
        exchanges: [],
        createdAt: new Date(),
        updatedAt: new Date()
      };
      
      // 设置模拟服务返回值
      mockInquiryService.createSession.mockResolvedValue(mockSession);
      
      // 发送请求
      const response = await request(app)
        .post('/api/inquiry/sessions')
        .send(requestBody)
        .expect('Content-Type', /json/)
        .expect(201);
      
      // 验证响应
      expect(response.body).toEqual({
        success: true,
        message: '问诊会话创建成功',
        data: expect.objectContaining({
          sessionId: 'session123',
          userId: 'user123',
          status: 'active'
        })
      });
      
      // 验证服务调用
      expect(mockInquiryService.createSession).toHaveBeenCalledWith(
        'user123',
        { age: 30, gender: 'male' },
        { language: 'zh-CN' }
      );
    });

    it('请求体缺少必要参数时应返回400状态码', async () => {
      // 发送缺少userId的请求
      const response = await request(app)
        .post('/api/inquiry/sessions')
        .send({
          patientInfo: { age: 30 }
        })
        .expect('Content-Type', /json/)
        .expect(400);
      
      // 验证响应包含错误信息
      expect(response.body).toHaveProperty('message');
      expect(response.body.message).toContain('userId');
      
      // 验证服务未被调用
      expect(mockInquiryService.createSession).not.toHaveBeenCalled();
    });
  });

  describe('POST /api/inquiry/sessions/:sessionId/inquiries', () => {
    it('应处理问诊请求并返回200状态码', async () => {
      // 准备测试数据
      const sessionId = 'session123';
      const requestBody = {
        content: '我最近头痛得厉害，而且有点发热'
      };
      
      const mockResponse = {
        sessionId,
        exchangeId: 'exchange123',
        response: {
          content: '您可能感冒了，建议多休息',
          extractedSymptoms: ['头痛', '发热'],
          suggestedFollowUp: ['头痛持续多久了？']
        },
        sessionStatus: 'active',
        metadata: {}
      };
      
      // 设置模拟服务返回值
      mockInquiryService.processInquiry.mockResolvedValue(mockResponse);
      
      // 发送请求
      const response = await request(app)
        .post(`/api/inquiry/sessions/${sessionId}/inquiries`)
        .send(requestBody)
        .expect('Content-Type', /json/)
        .expect(200);
      
      // 验证响应
      expect(response.body).toEqual({
        success: true,
        message: '问诊请求处理成功',
        data: expect.objectContaining({
          sessionId,
          exchangeId: 'exchange123',
          response: expect.objectContaining({
            content: '您可能感冒了，建议多休息',
            extractedSymptoms: ['头痛', '发热']
          })
        })
      });
      
      // 验证服务调用
      expect(mockInquiryService.processInquiry).toHaveBeenCalled();
    });

    it('请求体内容太短时应返回400状态码', async () => {
      // 发送内容太短的请求
      const response = await request(app)
        .post('/api/inquiry/sessions/session123/inquiries')
        .send({
          content: '嗯'
        })
        .expect('Content-Type', /json/)
        .expect(400);
      
      // 验证响应包含错误信息
      expect(response.body).toHaveProperty('message');
      
      // 验证服务未被调用
      expect(mockInquiryService.processInquiry).not.toHaveBeenCalled();
    });
  });

  // 更多测试...
}); 