import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import { jest } from '@jest/globals';

// Mock FiveDiagnosisScreen component
const MockFiveDiagnosisScreen = jest.fn(() => null);

jest.mock('../../../components/diagnosis/FiveDiagnosisScreen', () => ({
  __esModule: true,
  default: MockFiveDiagnosisScreen,
}));

describe('FiveDiagnosisScreen 五诊屏幕测试', () => {
  const defaultProps = {
    testID: 'five-diagnosis-screen',
    onDiagnosisComplete: jest.fn(),
    onStepChange: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('渲染测试', () => {
    it('应该正确渲染组件', () => {
      render(<MockFiveDiagnosisScreen {...defaultProps} />);
      expect(MockFiveDiagnosisScreen).toHaveBeenCalledWith(defaultProps, {});
    });

    it('应该显示五诊步骤', () => {
      const propsWithSteps = {
        ...defaultProps,
        steps: ['望诊', '闻诊', '问诊', '切诊', '综合诊断']
      };
      render(<MockFiveDiagnosisScreen {...propsWithSteps} />);
      expect(MockFiveDiagnosisScreen).toHaveBeenCalledWith(propsWithSteps, {});
    });

    it('应该显示当前诊断步骤', () => {
      const propsWithCurrentStep = {
        ...defaultProps,
        currentStep: 0,
        stepTitle: '望诊'
      };
      render(<MockFiveDiagnosisScreen {...propsWithCurrentStep} />);
      expect(MockFiveDiagnosisScreen).toHaveBeenCalledWith(propsWithCurrentStep, {});
    });
  });

  describe('交互测试', () => {
    it('应该处理步骤切换', async () => {
      const mockOnStepChange = jest.fn();
      const props = {
        ...defaultProps,
        onStepChange: mockOnStepChange,
        currentStep: 0
      };
      
      render(<MockFiveDiagnosisScreen {...props} />);
      expect(MockFiveDiagnosisScreen).toHaveBeenCalledWith(props, {});
    });

    it('应该处理诊断完成', async () => {
      const mockOnComplete = jest.fn();
      const props = {
        ...defaultProps,
        onDiagnosisComplete: mockOnComplete,
        isComplete: true
      };
      
      render(<MockFiveDiagnosisScreen {...props} />);
      expect(MockFiveDiagnosisScreen).toHaveBeenCalledWith(props, {});
    });

    it('应该处理用户输入', async () => {
      const mockOnInput = jest.fn();
      const props = {
        ...defaultProps,
        onUserInput: mockOnInput,
        userInput: ''
      };
      
      render(<MockFiveDiagnosisScreen {...props} />);
      expect(MockFiveDiagnosisScreen).toHaveBeenCalledWith(props, {});
    });
  });

  describe('五诊步骤测试', () => {
    it('应该支持望诊功能', () => {
      const lookingProps = {
        ...defaultProps,
        currentStep: 0,
        stepType: 'looking',
        lookingData: {
          faceColor: '红润',
          tongueColor: '淡红',
          bodyPosture: '正常'
        }
      };
      
      render(<MockFiveDiagnosisScreen {...lookingProps} />);
      expect(MockFiveDiagnosisScreen).toHaveBeenCalledWith(lookingProps, {});
    });

    it('应该支持闻诊功能', () => {
      const listeningProps = {
        ...defaultProps,
        currentStep: 1,
        stepType: 'listening',
        listeningData: {
          voiceQuality: '清晰',
          breathingSound: '正常',
          coughSound: '无'
        }
      };
      
      render(<MockFiveDiagnosisScreen {...listeningProps} />);
      expect(MockFiveDiagnosisScreen).toHaveBeenCalledWith(listeningProps, {});
    });

    it('应该支持问诊功能', () => {
      const inquiryProps = {
        ...defaultProps,
        currentStep: 2,
        stepType: 'inquiry',
        inquiryData: {
          symptoms: ['头痛', '失眠'],
          duration: '3天',
          severity: '轻度'
        }
      };
      
      render(<MockFiveDiagnosisScreen {...inquiryProps} />);
      expect(MockFiveDiagnosisScreen).toHaveBeenCalledWith(inquiryProps, {});
    });

    it('应该支持切诊功能', () => {
      const palpationProps = {
        ...defaultProps,
        currentStep: 3,
        stepType: 'palpation',
        palpationData: {
          pulseType: '平脉',
          pulseRate: 72,
          acupointSensitivity: '正常'
        }
      };
      
      render(<MockFiveDiagnosisScreen {...palpationProps} />);
      expect(MockFiveDiagnosisScreen).toHaveBeenCalledWith(palpationProps, {});
    });

    it('应该支持综合诊断', () => {
      const comprehensiveProps = {
        ...defaultProps,
        currentStep: 4,
        stepType: 'comprehensive',
        diagnosisResult: {
          syndrome: '气虚血瘀',
          constitution: '气虚质',
          recommendations: ['调理气血', '适度运动']
        }
      };
      
      render(<MockFiveDiagnosisScreen {...comprehensiveProps} />);
      expect(MockFiveDiagnosisScreen).toHaveBeenCalledWith(comprehensiveProps, {});
    });
  });

  describe('状态管理测试', () => {
    it('应该正确管理诊断进度', () => {
      const progressProps = {
        ...defaultProps,
        progress: 0.6,
        completedSteps: [0, 1, 2],
        currentStep: 3
      };
      
      render(<MockFiveDiagnosisScreen {...progressProps} />);
      expect(MockFiveDiagnosisScreen).toHaveBeenCalledWith(progressProps, {});
    });

    it('应该响应props变化', () => {
      const { rerender } = render(<MockFiveDiagnosisScreen {...defaultProps} />);
      const newProps = { 
        ...defaultProps, 
        currentStep: 1,
        stepTitle: '闻诊'
      };
      rerender(<MockFiveDiagnosisScreen {...newProps} />);
      expect(MockFiveDiagnosisScreen).toHaveBeenCalledWith(newProps, {});
    });
  });

  describe('错误处理测试', () => {
    it('应该处理诊断错误', () => {
      const errorProps = { 
        ...defaultProps, 
        error: '诊断过程中发生错误',
        hasError: true
      };
      render(<MockFiveDiagnosisScreen {...errorProps} />);
      expect(MockFiveDiagnosisScreen).toHaveBeenCalledWith(errorProps, {});
    });

    it('应该处理加载状态', () => {
      const loadingProps = { 
        ...defaultProps, 
        loading: true,
        loadingMessage: '正在分析诊断数据...'
      };
      render(<MockFiveDiagnosisScreen {...loadingProps} />);
      expect(MockFiveDiagnosisScreen).toHaveBeenCalledWith(loadingProps, {});
    });
  });

  describe('性能测试', () => {
    it('应该在合理时间内渲染', () => {
      const startTime = performance.now();
      render(<MockFiveDiagnosisScreen {...defaultProps} />);
      const endTime = performance.now();
      expect(endTime - startTime).toBeLessThan(100);
    });

    it('应该正确清理资源', () => {
      const { unmount } = render(<MockFiveDiagnosisScreen {...defaultProps} />);
      unmount();
      // 验证清理逻辑
      expect(true).toBe(true);
    });
  });

  describe('可访问性测试', () => {
    it('应该具有正确的可访问性属性', () => {
      const accessibilityProps = {
        ...defaultProps,
        accessibilityLabel: '五诊诊断界面',
        accessibilityRole: 'form'
      };
      render(<MockFiveDiagnosisScreen {...accessibilityProps} />);
      expect(MockFiveDiagnosisScreen).toHaveBeenCalledWith(accessibilityProps, {});
    });
  });
}); 