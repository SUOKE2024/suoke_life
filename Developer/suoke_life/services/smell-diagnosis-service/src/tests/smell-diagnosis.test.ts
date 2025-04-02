import request from 'supertest';
import express from 'express';
import { Container } from 'typedi';
import { SmellDiagnosisController } from '../controllers/smell-diagnosis.controller';
import { SmellDiagnosisService } from '../services/smell-diagnosis.service';
import { SmellDiagnosisType, SampleType } from '../interfaces/smell-diagnosis.interface';
import { SmellDiagnosisResultModel } from '../models/smell-diagnosis.model';
import { errorHandler } from '../middlewares/error.middleware';

// 模拟服务
jest.mock('../services/smell-diagnosis.service');

describe('闻诊服务 API 测试', () => {
  let app: express.Application;
  let mockService: jest.Mocked<SmellDiagnosisService>;
  
  beforeEach(() => {
    // 重置模拟
    jest.resetAllMocks();
    
    // 创建应用
    app = express();
    app.use(express.json());
    
    // 设置模拟服务
    mockService = {
      analyzeSmell: jest.fn(),
      getUserDiagnosisHistory: jest.fn(),
      getDiagnosisResultById: jest.fn()
    } as unknown as jest.Mocked<SmellDiagnosisService>;
    
    // 注入模拟服务
    Container.set(SmellDiagnosisService, mockService);
    
    // 设置控制器
    const controller = new SmellDiagnosisController();
    
    // 设置路由
    app.post('/api/analyze', controller.analyze);
    app.get('/api/history/:userId', controller.getHistory);
    app.get('/api/diagnosis/:id', controller.getDiagnosisById);
    app.get('/api/health', controller.healthCheck);
    
    // 错误处理
    app.use(errorHandler);
  });
  
  describe('健康检查接口', () => {
    it('应返回正确的健康状态', async () => {
      const res = await request(app)
        .get('/api/health')
        .expect(200);
      
      expect(res.body).toHaveProperty('success', true);
      expect(res.body).toHaveProperty('service', 'smell-diagnosis-service');
      expect(res.body).toHaveProperty('status', 'OK');
      expect(res.body).toHaveProperty('timestamp');
    });
  });
  
  describe('闻诊分析接口', () => {
    it('成功分析文本描述', async () => {
      // 准备模拟数据
      const analysisResult = new SmellDiagnosisResultModel({
        userId: 'user123',
        requestId: 'req123',
        diagnosisType: SmellDiagnosisType.BREATH,
        analysisResults: [],
        tcmImplications: [],
        recommendations: ['保持良好作息'],
        confidence: 0.85
      });
      
      mockService.analyzeSmell.mockResolvedValue(analysisResult);
      
      // 发送请求
      const res = await request(app)
        .post('/api/analyze')
        .send({
          userId: 'user123',
          diagnosisType: SmellDiagnosisType.BREATH,
          description: '呼吸带有酸味',
          sampleType: SampleType.TEXT_DESCRIPTION
        })
        .expect(200);
      
      // 验证结果
      expect(res.body).toHaveProperty('success', true);
      expect(res.body).toHaveProperty('data');
      expect(mockService.analyzeSmell).toHaveBeenCalledTimes(1);
    });
    
    it('缺少用户ID时应返回错误', async () => {
      const res = await request(app)
        .post('/api/analyze')
        .send({
          diagnosisType: SmellDiagnosisType.BREATH,
          description: '呼吸带有酸味'
        })
        .expect(400);
      
      expect(res.body).toHaveProperty('success', false);
      expect(res.body).toHaveProperty('message', '缺少用户ID');
    });
    
    it('无效诊断类型时应返回错误', async () => {
      const res = await request(app)
        .post('/api/analyze')
        .send({
          userId: 'user123',
          diagnosisType: 'invalid',
          description: '呼吸带有酸味'
        })
        .expect(400);
      
      expect(res.body).toHaveProperty('success', false);
      expect(res.body).toHaveProperty('message', '无效的诊断类型');
    });
  });
  
  describe('获取历史记录接口', () => {
    it('成功获取历史记录', async () => {
      // 准备模拟数据
      const historyResults = [
        new SmellDiagnosisResultModel({
          userId: 'user123',
          requestId: 'req123',
          diagnosisType: SmellDiagnosisType.BREATH,
          analysisResults: [],
          tcmImplications: [],
          recommendations: [],
          confidence: 0.85
        }),
        new SmellDiagnosisResultModel({
          userId: 'user123',
          requestId: 'req124',
          diagnosisType: SmellDiagnosisType.MOUTH,
          analysisResults: [],
          tcmImplications: [],
          recommendations: [],
          confidence: 0.75
        })
      ];
      
      mockService.getUserDiagnosisHistory.mockResolvedValue(historyResults);
      
      // 发送请求
      const res = await request(app)
        .get('/api/history/user123')
        .expect(200);
      
      // 验证结果
      expect(res.body).toHaveProperty('success', true);
      expect(res.body).toHaveProperty('data');
      expect(res.body.data).toHaveLength(2);
      expect(mockService.getUserDiagnosisHistory).toHaveBeenCalledWith('user123', 20, 0);
    });
  });
  
  describe('获取诊断详情接口', () => {
    it('成功获取诊断详情', async () => {
      // 准备模拟数据
      const diagnosisResult = new SmellDiagnosisResultModel({
        userId: 'user123',
        requestId: 'req123',
        diagnosisType: SmellDiagnosisType.BREATH,
        analysisResults: [],
        tcmImplications: [],
        recommendations: ['保持良好作息'],
        confidence: 0.85
      });
      
      mockService.getDiagnosisResultById.mockResolvedValue(diagnosisResult);
      
      // 发送请求
      const res = await request(app)
        .get('/api/diagnosis/diag123')
        .expect(200);
      
      // 验证结果
      expect(res.body).toHaveProperty('success', true);
      expect(res.body).toHaveProperty('data');
      expect(mockService.getDiagnosisResultById).toHaveBeenCalledWith('diag123');
    });
    
    it('诊断不存在时应返回404', async () => {
      mockService.getDiagnosisResultById.mockResolvedValue(null);
      
      const res = await request(app)
        .get('/api/diagnosis/nonexistent')
        .expect(404);
      
      expect(res.body).toHaveProperty('success', false);
      expect(res.body).toHaveProperty('message', '诊断结果不存在');
    });
  });
});