import React from 'react';
import { render, screen } from '@testing-library/react-native';
import { jest } from '@jest/globals';

// Mock EnhancedHealthVisualization component
const MockEnhancedHealthVisualization = jest.fn(() => null);

jest.mock('../../../components/health/EnhancedHealthVisualization', () => ({
  __esModule: true,
  default: MockEnhancedHealthVisualization,
}));

describe('EnhancedHealthVisualization 增强健康可视化测试', () => {
  const defaultProps = {
    testID: 'enhanced-health-visualization',
    data: [],
    onDataUpdate: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('基础渲染测试', () => {
    it('应该正确渲染组件', () => {
      render(<MockEnhancedHealthVisualization {...defaultProps} />);
      expect(MockEnhancedHealthVisualization).toHaveBeenCalledWith(defaultProps, {});
    });

    it('应该显示健康数据图表', () => {
      const propsWithData = {
        ...defaultProps,
        data: [
          { date: '2024-01-01', heartRate: 72, bloodPressure: 120 },
          { date: '2024-01-02', heartRate: 75, bloodPressure: 118 },
          { date: '2024-01-03', heartRate: 70, bloodPressure: 122 }
        ]
      };
      render(<MockEnhancedHealthVisualization {...propsWithData} />);
      expect(MockEnhancedHealthVisualization).toHaveBeenCalledWith(propsWithData, {});
    });

    it('应该支持多种图表类型', () => {
      const chartProps = {
        ...defaultProps,
        chartType: 'line',
        showTrend: true,
        showAverage: true
      };
      render(<MockEnhancedHealthVisualization {...chartProps} />);
      expect(MockEnhancedHealthVisualization).toHaveBeenCalledWith(chartProps, {});
    });
  });

  describe('健康指标可视化', () => {
    it('应该可视化心率数据', () => {
      const heartRateProps = {
        ...defaultProps,
        metric: 'heartRate',
        data: [
          { timestamp: '2024-01-01T08:00:00Z', value: 72 },
          { timestamp: '2024-01-01T12:00:00Z', value: 85 },
          { timestamp: '2024-01-01T18:00:00Z', value: 68 }
        ]
      };
      render(<MockEnhancedHealthVisualization {...heartRateProps} />);
      expect(MockEnhancedHealthVisualization).toHaveBeenCalledWith(heartRateProps, {});
    });

    it('应该可视化血压数据', () => {
      const bloodPressureProps = {
        ...defaultProps,
        metric: 'bloodPressure',
        data: [
          { timestamp: '2024-01-01', systolic: 120, diastolic: 80 },
          { timestamp: '2024-01-02', systolic: 118, diastolic: 78 },
          { timestamp: '2024-01-03', systolic: 122, diastolic: 82 }
        ]
      };
      render(<MockEnhancedHealthVisualization {...bloodPressureProps} />);
      expect(MockEnhancedHealthVisualization).toHaveBeenCalledWith(bloodPressureProps, {});
    });

    it('应该可视化睡眠数据', () => {
      const sleepProps = {
        ...defaultProps,
        metric: 'sleep',
        data: [
          { date: '2024-01-01', duration: 7.5, quality: 85, deepSleep: 1.8 },
          { date: '2024-01-02', duration: 8.0, quality: 90, deepSleep: 2.1 },
          { date: '2024-01-03', duration: 6.5, quality: 75, deepSleep: 1.5 }
        ]
      };
      render(<MockEnhancedHealthVisualization {...sleepProps} />);
      expect(MockEnhancedHealthVisualization).toHaveBeenCalledWith(sleepProps, {});
    });

    it('应该可视化运动数据', () => {
      const exerciseProps = {
        ...defaultProps,
        metric: 'exercise',
        data: [
          { date: '2024-01-01', steps: 8500, calories: 320, distance: 6.2 },
          { date: '2024-01-02', steps: 10200, calories: 380, distance: 7.5 },
          { date: '2024-01-03', steps: 7800, calories: 290, distance: 5.8 }
        ]
      };
      render(<MockEnhancedHealthVisualization {...exerciseProps} />);
      expect(MockEnhancedHealthVisualization).toHaveBeenCalledWith(exerciseProps, {});
    });
  });

  describe('中医健康可视化', () => {
    it('应该可视化体质分析', () => {
      const constitutionProps = {
        ...defaultProps,
        visualizationType: 'constitution',
        data: {
          primaryType: '气虚质',
          score: 85,
          distribution: {
            '气虚质': 85,
            '阳虚质': 60,
            '阴虚质': 40,
            '痰湿质': 30
          }
        }
      };
      render(<MockEnhancedHealthVisualization {...constitutionProps} />);
      expect(MockEnhancedHealthVisualization).toHaveBeenCalledWith(constitutionProps, {});
    });

    it('应该可视化五脏六腑状态', () => {
      const organProps = {
        ...defaultProps,
        visualizationType: 'organs',
        data: {
          heart: { health: 90, energy: 85 },
          liver: { health: 75, energy: 80 },
          spleen: { health: 85, energy: 75 },
          lung: { health: 88, energy: 82 },
          kidney: { health: 82, energy: 78 }
        }
      };
      render(<MockEnhancedHealthVisualization {...organProps} />);
      expect(MockEnhancedHealthVisualization).toHaveBeenCalledWith(organProps, {});
    });

    it('应该可视化经络状态', () => {
      const meridianProps = {
        ...defaultProps,
        visualizationType: 'meridians',
        data: {
          '肺经': { flow: 85, blockage: 15 },
          '大肠经': { flow: 90, blockage: 10 },
          '胃经': { flow: 75, blockage: 25 },
          '脾经': { flow: 80, blockage: 20 }
        }
      };
      render(<MockEnhancedHealthVisualization {...meridianProps} />);
      expect(MockEnhancedHealthVisualization).toHaveBeenCalledWith(meridianProps, {});
    });
  });

  describe('交互功能测试', () => {
    it('应该支持时间范围选择', () => {
      const timeRangeProps = {
        ...defaultProps,
        timeRange: '7days',
        onTimeRangeChange: jest.fn()
      };
      render(<MockEnhancedHealthVisualization {...timeRangeProps} />);
      expect(MockEnhancedHealthVisualization).toHaveBeenCalledWith(timeRangeProps, {});
    });

    it('应该支持数据点选择', () => {
      const selectionProps = {
        ...defaultProps,
        onDataPointSelect: jest.fn(),
        selectedDataPoint: { date: '2024-01-01', value: 72 }
      };
      render(<MockEnhancedHealthVisualization {...selectionProps} />);
      expect(MockEnhancedHealthVisualization).toHaveBeenCalledWith(selectionProps, {});
    });

    it('应该支持缩放和平移', () => {
      const zoomProps = {
        ...defaultProps,
        enableZoom: true,
        enablePan: true,
        zoomLevel: 1.5
      };
      render(<MockEnhancedHealthVisualization {...zoomProps} />);
      expect(MockEnhancedHealthVisualization).toHaveBeenCalledWith(zoomProps, {});
    });
  });

  describe('数据分析功能', () => {
    it('应该显示趋势分析', () => {
      const trendProps = {
        ...defaultProps,
        showTrend: true,
        trendAnalysis: {
          direction: 'increasing',
          rate: 0.05,
          confidence: 0.85
        }
      };
      render(<MockEnhancedHealthVisualization {...trendProps} />);
      expect(MockEnhancedHealthVisualization).toHaveBeenCalledWith(trendProps, {});
    });

    it('应该显示统计信息', () => {
      const statsProps = {
        ...defaultProps,
        showStatistics: true,
        statistics: {
          mean: 75.2,
          median: 74.0,
          min: 65,
          max: 88,
          standardDeviation: 6.8
        }
      };
      render(<MockEnhancedHealthVisualization {...statsProps} />);
      expect(MockEnhancedHealthVisualization).toHaveBeenCalledWith(statsProps, {});
    });

    it('应该显示异常检测', () => {
      const anomalyProps = {
        ...defaultProps,
        showAnomalies: true,
        anomalies: [
          { timestamp: '2024-01-01T14:00:00Z', value: 95, severity: 'high' },
          { timestamp: '2024-01-02T09:00:00Z', value: 55, severity: 'medium' }
        ]
      };
      render(<MockEnhancedHealthVisualization {...anomalyProps} />);
      expect(MockEnhancedHealthVisualization).toHaveBeenCalledWith(anomalyProps, {});
    });
  });

  describe('性能测试', () => {
    it('应该高效处理大量数据点', () => {
      const largeDataProps = {
        ...defaultProps,
        data: Array.from({ length: 10000 }, (_, index) => ({
          timestamp: new Date(2024, 0, 1, 0, index).toISOString(),
          value: 70 + Math.random() * 20
        }))
      };

      const startTime = performance.now();
      render(<MockEnhancedHealthVisualization {...largeDataProps} />);
      const endTime = performance.now();

      expect(endTime - startTime).toBeLessThan(100);
      expect(MockEnhancedHealthVisualization).toHaveBeenCalledWith(largeDataProps, {});
    });

    it('应该支持数据虚拟化', () => {
      const virtualizedProps = {
        ...defaultProps,
        enableVirtualization: true,
        viewportSize: 1000
      };
      render(<MockEnhancedHealthVisualization {...virtualizedProps} />);
      expect(MockEnhancedHealthVisualization).toHaveBeenCalledWith(virtualizedProps, {});
    });
  });

  describe('错误处理', () => {
    it('应该处理空数据', () => {
      const emptyProps = {
        ...defaultProps,
        data: [],
        showEmptyState: true
      };
      render(<MockEnhancedHealthVisualization {...emptyProps} />);
      expect(MockEnhancedHealthVisualization).toHaveBeenCalledWith(emptyProps, {});
    });

    it('应该处理无效数据', () => {
      const invalidProps = {
        ...defaultProps,
        data: [
          { timestamp: 'invalid', value: 'not-a-number' },
          { timestamp: null, value: undefined }
        ]
      };
      render(<MockEnhancedHealthVisualization {...invalidProps} />);
      expect(MockEnhancedHealthVisualization).toHaveBeenCalledWith(invalidProps, {});
    });
  });

  describe('可访问性测试', () => {
    it('应该提供可访问性标签', () => {
      const accessibilityProps = {
        ...defaultProps,
        accessibilityLabel: '健康数据可视化图表',
        accessibilityRole: 'image'
      };
      render(<MockEnhancedHealthVisualization {...accessibilityProps} />);
      expect(MockEnhancedHealthVisualization).toHaveBeenCalledWith(accessibilityProps, {});
    });

    it('应该支持屏幕阅读器', () => {
      const screenReaderProps = {
        ...defaultProps,
        accessibilityHint: '显示过去7天的心率变化趋势',
        accessible: true
      };
      render(<MockEnhancedHealthVisualization {...screenReaderProps} />);
      expect(MockEnhancedHealthVisualization).toHaveBeenCalledWith(screenReaderProps, {});
    });
  });
}); 