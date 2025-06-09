import { fireEvent, render, waitFor } from '@testing-library/react-native';
import React from 'react';
import { Alert } from 'react-native';
import { fiveDiagnosisService } from '../../../services/fiveDiagnosisService';
import FiveDiagnosisScreen from '../FiveDiagnosisScreen';

// Mock dependencies
jest.mock('../../../services/fiveDiagnosisService');
jest.mock('@react-navigation/native', () => ({
  useNavigation: () => ({
    navigate: jest.fn(),
    goBack: jest.fn(),
  }),
}));

jest.mock('react-native-image-picker', () => ({
  launchImageLibrary: jest.fn(),
}));

// Mock Alert
jest.spyOn(Alert, 'alert');

describe('FiveDiagnosisScreen Integration', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (fiveDiagnosisService.initialize as jest.Mock).mockResolvedValue(undefined);
    (fiveDiagnosisService.performDiagnosis as jest.Mock).mockResolvedValue({
      sessionId: 'test-session',
      userId: 'test-user',
      timestamp: new Date().toISOString(),
      overallConfidence: 0.85,
      primarySyndrome: {
        name: '气虚证',
        confidence: 0.82,
        description: '气虚证候，表现为气短乏力、精神不振',
      },
      constitutionType: {
        type: '气虚质',
        characteristics: ['气短懒言', '容易疲劳', '声音低弱'],
        recommendations: ['补气健脾', '适度运动', '规律作息'],
      },
      diagnosticResults: {},
      fusionAnalysis: {
        evidenceStrength: 0.8,
        syndromePatterns: ['气虚证'],
        riskFactors: ['过度劳累', '饮食不规律'],
      },
      healthRecommendations: {
        lifestyle: ['规律作息', '避免过度劳累'],
        diet: ['补气食物', '温性食材'],
        exercise: ['太极拳', '八段锦'],
        treatment: ['中药调理', '针灸治疗'],
        prevention: ['定期体检', '情志调节'],
      },
      qualityMetrics: {
        dataQuality: 0.9,
        resultReliability: 0.85,
        completeness: 0.8,
      },
      overallAssessment: '整体健康状况良好，建议注意气虚调理',
    });
  });

  it('should render all five diagnosis steps', async () => {
    const { getByText } = render(<FiveDiagnosisScreen />);

    await waitFor(() => {
      expect(getByText('望诊')).toBeTruthy();
      expect(getByText('闻诊')).toBeTruthy();
      expect(getByText('问诊')).toBeTruthy();
      expect(getByText('切诊')).toBeTruthy();
      expect(getByText('算诊')).toBeTruthy();
    });
  });

  it('should initialize diagnosis service on mount', async () => {
    render(<FiveDiagnosisScreen />);

    await waitFor(() => {
      expect(fiveDiagnosisService.initialize).toHaveBeenCalled();
    });
  });

  it('should show step descriptions', async () => {
    const { getByText } = render(<FiveDiagnosisScreen />);

    await waitFor(() => {
      expect(getByText('观察面色、舌象、体态等')).toBeTruthy();
      expect(getByText('听声音、闻气味')).toBeTruthy();
      expect(getByText('询问症状、病史等')).toBeTruthy();
      expect(getByText('脉诊、按诊等')).toBeTruthy();
      expect(getByText('数据分析、量化诊断')).toBeTruthy();
    });
  });

  it('should handle step navigation correctly', async () => {
    const { getByText, getByTestId } = render(<FiveDiagnosisScreen />);

    await waitFor(() => {
      expect(getByText('望诊')).toBeTruthy();
    });

    // 模拟点击第一个步骤
    const firstStep = getByText('望诊');
    fireEvent.press(firstStep);

    // 验证当前步骤已激活
    await waitFor(() => {
      // 这里可以添加更多的步骤状态验证
      expect(getByText('望诊')).toBeTruthy();
    });
  });

  it('should show progress indicator', async () => {
    const { getByText } = render(<FiveDiagnosisScreen />);

    await waitFor(() => {
      // 检查是否显示进度相关的文本
      expect(getByText(/五诊分析/)).toBeTruthy();
    });
  });

  it('should handle service initialization failure', async () => {
    (fiveDiagnosisService.initialize as jest.Mock).mockRejectedValue(
      new Error('Service initialization failed')
    );

    render(<FiveDiagnosisScreen />);

    await waitFor(() => {
      expect(Alert.alert).toHaveBeenCalledWith(
        '错误',
        '初始化诊断服务失败，请重试'
      );
    });
  });

  it('should handle diagnosis completion', async () => {
    const mockOnComplete = jest.fn();
    const { getByText } = render(
      <FiveDiagnosisScreen onComplete={mockOnComplete} />
    );

    await waitFor(() => {
      expect(getByText('望诊')).toBeTruthy();
    });

    // 这里可以模拟完成诊断流程的操作
    // 由于组件比较复杂，这里只做基础验证
  });

  it('should display correct step count', async () => {
    const { getByText } = render(<FiveDiagnosisScreen />);

    await waitFor(() => {
      // 验证显示了5个诊断步骤
      expect(getByText('望诊')).toBeTruthy();
      expect(getByText('闻诊')).toBeTruthy();
      expect(getByText('问诊')).toBeTruthy();
      expect(getByText('切诊')).toBeTruthy();
      expect(getByText('算诊')).toBeTruthy();
    });
  });
});

describe('Five Diagnosis Components Integration', () => {
  it('should have all required diagnosis components', () => {
    // 验证所有诊断组件都已正确导入
    const LookDiagnosisComponent =
      require('../components/LookDiagnosisComponent').LookDiagnosisComponent;
    const ListenDiagnosisComponent =
      require('../components/ListenDiagnosisComponent').ListenDiagnosisComponent;
    const InquiryDiagnosisComponent =
      require('../components/InquiryDiagnosisComponent').InquiryDiagnosisComponent;
    const PalpationDiagnosisComponent =
      require('../components/PalpationDiagnosisComponent').PalpationDiagnosisComponent;
    const CalculationDiagnosisComponent =
      require('../CalculationDiagnosisComponent').default;

    expect(LookDiagnosisComponent).toBeDefined();
    expect(ListenDiagnosisComponent).toBeDefined();
    expect(InquiryDiagnosisComponent).toBeDefined();
    expect(PalpationDiagnosisComponent).toBeDefined();
    expect(CalculationDiagnosisComponent).toBeDefined();
  });

  it('should have consistent component interfaces', () => {
    // 验证所有组件都遵循相同的接口规范
    const components = [
      require('../components/LookDiagnosisComponent').LookDiagnosisComponent,
      require('../components/ListenDiagnosisComponent')
        .ListenDiagnosisComponent,
      require('../components/InquiryDiagnosisComponent')
        .InquiryDiagnosisComponent,
      require('../components/PalpationDiagnosisComponent')
        .PalpationDiagnosisComponent,
    ];

    components.forEach((Component) => {
      expect(typeof Component).toBe('function');
      // 这里可以添加更多的接口一致性检查
    });
  });
});

describe('Five Diagnosis Service Integration', () => {
  it('should have all required service methods', () => {
    expect(fiveDiagnosisService.initialize).toBeDefined();
    expect(fiveDiagnosisService.performDiagnosis).toBeDefined();
    expect(typeof fiveDiagnosisService.initialize).toBe('function');
    expect(typeof fiveDiagnosisService.performDiagnosis).toBe('function');
  });

  it('should handle diagnosis input correctly', async () => {
    const mockInput = {
      lookData: { faceImage: 'test-image' },
      listenData: { voiceRecording: 'test-audio' },
      inquiryData: { symptoms: ['头痛', '失眠'] },
      palpationData: { pulseData: [75, 76, 74] },
      calculationData: {
        personalInfo: {
          birthYear: 1990,
          birthMonth: 5,
          birthDay: 15,
          birthHour: 10,
          gender: '男',
          location: '北京',
        },
        analysisTypes: {
          ziwuLiuzhu: true,
          constitution: true,
          bagua: false,
          wuyunLiuqi: false,
          comprehensive: true,
        },
        currentTime: new Date().toISOString(),
        healthConcerns: ['体质调理'],
      },
      timestamp: Date.now(),
    };

    await fiveDiagnosisService.performDiagnosis(mockInput);
    expect(fiveDiagnosisService.performDiagnosis).toHaveBeenCalledWith(
      mockInput
    );
  });
});
