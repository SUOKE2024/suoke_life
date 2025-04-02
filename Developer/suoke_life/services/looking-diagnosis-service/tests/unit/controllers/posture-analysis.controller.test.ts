import { Request, Response } from 'express';
import { Container } from 'typedi';
import { PostureAnalysisController } from '../../../src/controllers/posture-analysis.controller';
import { PostureAnalysisService } from '../../../src/services/posture-analysis/posture-analysis.service';
import { CoordinatorClientService } from '../../../src/services/four-diagnosis-coordinator/coordinator-client.service';
import { validationResult } from 'express-validator';

// 模拟依赖
jest.mock('express-validator');
jest.mock('../../../src/services/posture-analysis/posture-analysis.service');
jest.mock('../../../src/services/four-diagnosis-coordinator/coordinator-client.service');

describe('PostureAnalysisController', () => {
  let controller: PostureAnalysisController;
  let postureService: jest.Mocked<PostureAnalysisService>;
  let coordinatorService: jest.Mocked<CoordinatorClientService>;
  let req: Partial<Request>;
  let res: Partial<Response>;

  beforeEach(() => {
    // 重置所有模拟
    jest.clearAllMocks();
    
    // 初始化模拟服务
    postureService = {
      analyzePosture: jest.fn(),
      getPostureDiagnosisById: jest.fn(),
      getPostureDiagnosisByUserId: jest.fn(),
      getPostureDiagnosisBySessionId: jest.fn()
    } as any;

    coordinatorService = {
      reportDiagnosisResult: jest.fn().mockResolvedValue(true)
    } as any;

    // 模拟Container依赖注入
    (Container.get as jest.Mock) = jest.fn((serviceClass) => {
      if (serviceClass === PostureAnalysisService) {
        return postureService;
      } else if (serviceClass === CoordinatorClientService) {
        return coordinatorService;
      }
      return null;
    });

    // 创建控制器实例
    controller = new PostureAnalysisController();

    // 模拟请求和响应对象
    req = {
      params: {},
      body: {},
      query: {}
    };
    
    res = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn(),
      send: jest.fn()
    };

    // 模拟验证结果
    (validationResult as jest.Mock) = jest.fn().mockImplementation(() => ({
      isEmpty: () => true,
      array: () => []
    }));
  });

  describe('healthCheck', () => {
    it('应该返回服务健康状态', async () => {
      await controller.healthCheck(req as Request, res as Response);
      
      expect(res.status).toHaveBeenCalledWith(200);
      expect(res.json).toHaveBeenCalledWith(expect.objectContaining({
        status: 'success',
        message: '体态分析服务运行正常'
      }));
    });
  });

  describe('analyzePosture', () => {
    it('应该处理体态分析请求并返回结果', async () => {
      // 准备测试数据
      req.body = {
        imageBase64: 'base64_encoded_image',
        sessionId: 'test-session',
        userId: 'test-user',
        metadata: { captureTime: new Date() }
      };
      
      const mockResult = {
        diagnosisId: 'test-diagnosis-id',
        sessionId: 'test-session',
        userId: 'test-user',
        timestamp: new Date(),
        features: { overallPosture: '正常' },
        tcmImplications: [{ concept: '平和体质', confidence: 0.9 }],
        recommendations: ['保持良好姿势']
      };
      
      postureService.analyzePosture.mockResolvedValue(mockResult as any);
      
      // 执行请求
      await controller.analyzePosture(req as Request, res as Response);
      
      // 验证服务调用
      expect(postureService.analyzePosture).toHaveBeenCalledWith(
        'base64_encoded_image',
        'test-session',
        'test-user',
        expect.any(Object)
      );
      
      // 验证协调服务调用
      expect(coordinatorService.reportDiagnosisResult).toHaveBeenCalledWith(expect.objectContaining({
        diagnosisId: 'test-diagnosis-id',
        diagnosisType: 'posture'
      }));
      
      // 验证响应
      expect(res.status).toHaveBeenCalledWith(200);
      expect(res.json).toHaveBeenCalledWith({
        success: true,
        data: mockResult
      });
    });
    
    it('验证失败时应返回400状态码和错误信息', async () => {
      // 模拟验证失败
      (validationResult as jest.Mock).mockImplementation(() => ({
        isEmpty: () => false,
        array: () => [{ msg: '图像数据不能为空', param: 'imageBase64' }]
      }));
      
      // 执行请求
      await controller.analyzePosture(req as Request, res as Response);
      
      // 验证响应
      expect(res.status).toHaveBeenCalledWith(400);
      expect(res.json).toHaveBeenCalledWith(expect.objectContaining({
        success: false,
        errors: expect.any(Array)
      }));
      
      // 验证服务未被调用
      expect(postureService.analyzePosture).not.toHaveBeenCalled();
    });
    
    it('服务异常时应返回500状态码和错误信息', async () => {
      // 准备测试数据
      req.body = {
        imageBase64: 'base64_encoded_image',
        sessionId: 'test-session',
        userId: 'test-user'
      };
      
      // 模拟服务失败
      postureService.analyzePosture.mockRejectedValue(new Error('服务错误'));
      
      // 执行请求
      await controller.analyzePosture(req as Request, res as Response);
      
      // 验证响应
      expect(res.status).toHaveBeenCalledWith(500);
      expect(res.json).toHaveBeenCalledWith(expect.objectContaining({
        success: false,
        message: '体态分析失败',
        error: '服务错误'
      }));
    });
  });

  describe('getPostureDiagnosisById', () => {
    it('应该返回匹配ID的诊断记录', async () => {
      // 准备测试数据
      req.params = { diagnosisId: 'test-diagnosis-id' };
      
      const mockResult = {
        diagnosisId: 'test-diagnosis-id',
        sessionId: 'test-session',
        features: { overallPosture: '正常' }
      };
      
      postureService.getPostureDiagnosisById.mockResolvedValue(mockResult as any);
      
      // 执行请求
      await controller.getPostureDiagnosisById(req as Request, res as Response);
      
      // 验证服务调用
      expect(postureService.getPostureDiagnosisById).toHaveBeenCalledWith('test-diagnosis-id');
      
      // 验证响应
      expect(res.status).toHaveBeenCalledWith(200);
      expect(res.json).toHaveBeenCalledWith({
        success: true,
        data: mockResult
      });
    });
    
    it('诊断记录不存在时应返回404状态码', async () => {
      // 准备测试数据
      req.params = { diagnosisId: 'non-existent-id' };
      
      // 模拟服务返回空值
      postureService.getPostureDiagnosisById.mockResolvedValue(null);
      
      // 执行请求
      await controller.getPostureDiagnosisById(req as Request, res as Response);
      
      // 验证响应
      expect(res.status).toHaveBeenCalledWith(404);
      expect(res.json).toHaveBeenCalledWith(expect.objectContaining({
        success: false,
        message: '未找到体态诊断记录'
      }));
    });
  });

  describe('getPostureDiagnosisHistory', () => {
    it('应该返回用户的诊断历史记录', async () => {
      // 准备测试数据
      req.query = {
        userId: 'test-user',
        limit: '10',
        offset: '0'
      };
      
      const mockResults = [
        { diagnosisId: 'id-1', sessionId: 'session-1' },
        { diagnosisId: 'id-2', sessionId: 'session-2' }
      ];
      
      postureService.getPostureDiagnosisByUserId.mockResolvedValue(mockResults as any);
      
      // 执行请求
      await controller.getPostureDiagnosisHistory(req as Request, res as Response);
      
      // 验证服务调用
      expect(postureService.getPostureDiagnosisByUserId).toHaveBeenCalledWith('test-user', 10, 0);
      
      // 验证响应
      expect(res.status).toHaveBeenCalledWith(200);
      expect(res.json).toHaveBeenCalledWith({
        success: true,
        data: mockResults
      });
    });
    
    it('没有提供userId时应返回400错误', async () => {
      // 准备测试数据（缺少userId）
      req.query = {
        limit: '10',
        offset: '0'
      };
      
      // 执行请求
      await controller.getPostureDiagnosisHistory(req as Request, res as Response);
      
      // 验证响应
      expect(res.status).toHaveBeenCalledWith(400);
      expect(res.json).toHaveBeenCalledWith(expect.objectContaining({
        success: false,
        message: '必须提供userId或sessionId'
      }));
      
      // 验证服务未被调用
      expect(postureService.getPostureDiagnosisByUserId).not.toHaveBeenCalled();
    });
    
    it('提供sessionId时应调用会话历史记录服务', async () => {
      // 准备测试数据
      req.query = {
        sessionId: 'test-session',
        limit: '10',
        offset: '0'
      };
      
      const mockResults = [
        { diagnosisId: 'id-1', sessionId: 'test-session' },
        { diagnosisId: 'id-2', sessionId: 'test-session' }
      ];
      
      postureService.getPostureDiagnosisBySessionId.mockResolvedValue(mockResults as any);
      
      // 执行请求
      await controller.getPostureDiagnosisHistory(req as Request, res as Response);
      
      // 验证服务调用
      expect(postureService.getPostureDiagnosisBySessionId).toHaveBeenCalledWith('test-session', 10, 0);
      
      // 验证响应
      expect(res.status).toHaveBeenCalledWith(200);
      expect(res.json).toHaveBeenCalledWith({
        success: true,
        data: mockResults
      });
    });
  });
});