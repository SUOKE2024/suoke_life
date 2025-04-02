import { TongueDiagnosisService } from '../src/services/tongue-diagnosis/tongue-diagnosis.service';
import { ImageProcessorService } from '../src/services/image-processing/image-processor.service';
import { TongueFeatures } from '../src/models/diagnosis/tongue.model';
import fs from 'fs';
import path from 'path';

// 模拟依赖
jest.mock('../src/services/image-processing/image-processor.service');

describe('TongueDiagnosisService', () => {
  let tongueDiagnosisService: TongueDiagnosisService;
  let mockImageProcessorService: jest.Mocked<ImageProcessorService>;
  
  beforeEach(() => {
    // 重置mock
    jest.clearAllMocks();
    
    // 创建模拟ImageProcessorService
    mockImageProcessorService = {
      preprocessImage: jest.fn(),
      extractRegionOfInterest: jest.fn(),
      denoiseImage: jest.fn(),
      enhanceImage: jest.fn(),
      extractImageFeatures: jest.fn(),
    } as unknown as jest.Mocked<ImageProcessorService>;
    
    // 实例化服务
    tongueDiagnosisService = new TongueDiagnosisService(mockImageProcessorService);
  });
  
  describe('analyze', () => {
    it('应该正确处理舌头图像并返回分析结果', async () => {
      // 模拟图像处理结果
      const mockImageBuffer = Buffer.from('test-image');
      const mockProcessedImage = Buffer.from('processed-image');
      const mockTongueRegion = Buffer.from('tongue-region');
      const mockDenoisedImage = Buffer.from('denoised-image');
      const mockEnhancedImage = Buffer.from('enhanced-image');
      
      mockImageProcessorService.preprocessImage.mockResolvedValue(mockProcessedImage);
      mockImageProcessorService.extractRegionOfInterest.mockResolvedValue(mockTongueRegion);
      mockImageProcessorService.denoiseImage.mockResolvedValue(mockDenoisedImage);
      mockImageProcessorService.enhanceImage.mockResolvedValue(mockEnhancedImage);
      mockImageProcessorService.extractImageFeatures.mockResolvedValue({
        colorStats: [
          { mean: 150, std: 20 }, // 红色通道
          { mean: 100, std: 15 }, // 绿色通道
          { mean: 80, std: 10 }   // 蓝色通道
        ],
        brightness: 60,
        contrast: 0.8,
        edges: { count: 100, strength: 0.7 }
      });
      
      // 模拟私有方法
      const mockExtractTongueFeatures = jest.spyOn(
        tongueDiagnosisService as any, 
        'extractTongueFeatures'
      ).mockImplementation(() => {
        return Promise.resolve({
          tongueColor: '淡红',
          tongueShape: '正常',
          tongueCoating: '薄白',
          moisture: '适中',
          cracks: false,
          spots: false,
          teethMarks: false,
          deviation: false
        } as TongueFeatures);
      });
      
      const mockAnalyzeTCMImplications = jest.spyOn(
        tongueDiagnosisService as any,
        'analyzeTCMImplications'
      ).mockImplementation(() => {
        return Promise.resolve([
          { concept: '正常', confidence: 0.9 }
        ]);
      });
      
      const mockGenerateRecommendations = jest.spyOn(
        tongueDiagnosisService as any,
        'generateRecommendations'
      ).mockImplementation(() => {
        return Promise.resolve([
          '您的舌象表现正常，继续保持良好的生活习惯。',
          '建议保持规律作息，合理饮食。'
        ]);
      });
      
      // 测试分析方法
      const sessionId = 'test-session-123';
      const metadata = { captureTime: new Date().toISOString() };
      
      const result = await tongueDiagnosisService.analyze(mockImageBuffer, sessionId, metadata);
      
      // 验证结果
      expect(result).toBeDefined();
      expect(result.sessionId).toBe(sessionId);
      expect(result.features).toBeDefined();
      expect(result.features.tongueColor).toBe('淡红');
      expect(result.tcmImplications).toHaveLength(1);
      expect(result.tcmImplications[0].concept).toBe('正常');
      expect(result.recommendations).toHaveLength(2);
      
      // 验证调用
      expect(mockImageProcessorService.preprocessImage).toHaveBeenCalledWith(mockImageBuffer);
      expect(mockImageProcessorService.extractRegionOfInterest).toHaveBeenCalledWith(mockProcessedImage, 'tongue');
      expect(mockExtractTongueFeatures).toHaveBeenCalledWith(mockEnhancedImage, expect.anything());
      expect(mockAnalyzeTCMImplications).toHaveBeenCalledWith(expect.any(Object));
      expect(mockGenerateRecommendations).toHaveBeenCalled();
    });
    
    it('当图像处理失败时应该抛出异常', async () => {
      // 模拟图像处理失败
      mockImageProcessorService.preprocessImage.mockRejectedValue(new Error('图像处理失败'));
      
      // 测试分析方法
      const mockImageBuffer = Buffer.from('test-image');
      const sessionId = 'test-session-123';
      const metadata = {};
      
      await expect(
        tongueDiagnosisService.analyze(mockImageBuffer, sessionId, metadata)
      ).rejects.toThrow('舌诊分析失败: 图像处理失败');
    });
  });
}); 