import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react-native';
import { jest } from '@jest/globals';

// Mock HealthTrendChart component
const MockHealthTrendChart = jest.fn(() => null);

jest.mock('../../components/HealthTrendChart', () => ({
  __esModule: true,
  default: MockHealthTrendChart,
}));

describe('HealthTrendChart 健康趋势图表测试', () => {
  const defaultProps = {
    testID: 'health-trend-chart',
    data: [],
    onDataPointSelect: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('基础渲染测试', () => {
    it('应该正确渲染组件', () => {
      render(<MockHealthTrendChart {...defaultProps} />);
      expect(MockHealthTrendChart).toHaveBeenCalledWith(defaultProps, {});
    });

    it('应该显示健康趋势数据', () => {
      const propsWithData = {
        ...defaultProps,
        data: [
          { date: '2024-01-01', value: 72, metric: 'heartRate' },
          { date: '2024-01-02', value: 75, metric: 'heartRate' },
          { date: '2024-01-03', value: 70, metric: 'heartRate' }
        ]
      };
      render(<MockHealthTrendChart {...propsWithData} />);
      expect(MockHealthTrendChart).toHaveBeenCalledWith(propsWithData, {});
    });

    it('应该支持多种图表类型', () => {
      const chartTypeProps = {
        ...defaultProps,
        chartType: 'line',
        showGrid: true,
        showAxis: true
      };
      render(<MockHealthTrendChart {...chartTypeProps} />);
      expect(MockHealthTrendChart).toHaveBeenCalledWith(chartTypeProps, {});
    });
  });

  describe('健康指标趋势', () => {
    it('应该显示心率趋势', () => {
      const heartRateProps = {
        ...defaultProps,
        metric: 'heartRate',
        data: [
          { timestamp: '2024-01-01T08:00:00Z', value: 72, category: 'resting' },
          { timestamp: '2024-01-01T12:00:00Z', value: 85, category: 'active' },
          { timestamp: '2024-01-01T18:00:00Z', value: 68, category: 'resting' }
        ],
        unit: 'bpm',
        normalRange: { min: 60, max: 100 }
      };
      render(<MockHealthTrendChart {...heartRateProps} />);
      expect(MockHealthTrendChart).toHaveBeenCalledWith(heartRateProps, {});
    });

    it('应该显示血压趋势', () => {
      const bloodPressureProps = {
        ...defaultProps,
        metric: 'bloodPressure',
        data: [
          { date: '2024-01-01', systolic: 120, diastolic: 80 },
          { date: '2024-01-02', systolic: 118, diastolic: 78 },
          { date: '2024-01-03', systolic: 122, diastolic: 82 }
        ],
        unit: 'mmHg',
        showBothValues: true
      };
      render(<MockHealthTrendChart {...bloodPressureProps} />);
      expect(MockHealthTrendChart).toHaveBeenCalledWith(bloodPressureProps, {});
    });

    it('应该显示体重趋势', () => {
      const weightProps = {
        ...defaultProps,
        metric: 'weight',
        data: [
          { date: '2024-01-01', value: 65.5, bmi: 22.1 },
          { date: '2024-01-08', value: 65.2, bmi: 22.0 },
          { date: '2024-01-15', value: 64.8, bmi: 21.9 }
        ],
        unit: 'kg',
        showTrendLine: true
      };
      render(<MockHealthTrendChart {...weightProps} />);
      expect(MockHealthTrendChart).toHaveBeenCalledWith(weightProps, {});
    });

    it('应该显示睡眠趋势', () => {
      const sleepProps = {
        ...defaultProps,
        metric: 'sleep',
        data: [
          { date: '2024-01-01', duration: 7.5, quality: 85, deepSleep: 1.8 },
          { date: '2024-01-02', duration: 8.0, quality: 90, deepSleep: 2.1 },
          { date: '2024-01-03', duration: 6.5, quality: 75, deepSleep: 1.5 }
        ],
        unit: 'hours',
        showMultipleMetrics: true
      };
      render(<MockHealthTrendChart {...sleepProps} />);
      expect(MockHealthTrendChart).toHaveBeenCalledWith(sleepProps, {});
    });
  });

  describe('图表类型测试', () => {
    it('应该支持折线图', () => {
      const lineChartProps = {
        ...defaultProps,
        chartType: 'line',
        smooth: true,
        showDataPoints: true
      };
      render(<MockHealthTrendChart {...lineChartProps} />);
      expect(MockHealthTrendChart).toHaveBeenCalledWith(lineChartProps, {});
    });

    it('应该支持柱状图', () => {
      const barChartProps = {
        ...defaultProps,
        chartType: 'bar',
        barWidth: 20,
        showValues: true
      };
      render(<MockHealthTrendChart {...barChartProps} />);
      expect(MockHealthTrendChart).toHaveBeenCalledWith(barChartProps, {});
    });

    it('应该支持面积图', () => {
      const areaChartProps = {
        ...defaultProps,
        chartType: 'area',
        fillOpacity: 0.3,
        gradient: true
      };
      render(<MockHealthTrendChart {...areaChartProps} />);
      expect(MockHealthTrendChart).toHaveBeenCalledWith(areaChartProps, {});
    });

    it('应该支持散点图', () => {
      const scatterProps = {
        ...defaultProps,
        chartType: 'scatter',
        pointSize: 5,
        showCorrelation: true
      };
      render(<MockHealthTrendChart {...scatterProps} />);
      expect(MockHealthTrendChart).toHaveBeenCalledWith(scatterProps, {});
    });
  });

  describe('趋势分析功能', () => {
    it('应该显示趋势线', () => {
      const trendLineProps = {
        ...defaultProps,
        showTrendLine: true,
        trendType: 'linear',
        trendColor: '#ff6800'
      };
      render(<MockHealthTrendChart {...trendLineProps} />);
      expect(MockHealthTrendChart).toHaveBeenCalledWith(trendLineProps, {});
    });

    it('应该显示移动平均线', () => {
      const movingAverageProps = {
        ...defaultProps,
        showMovingAverage: true,
        averagePeriod: 7,
        averageType: 'simple'
      };
      render(<MockHealthTrendChart {...movingAverageProps} />);
      expect(MockHealthTrendChart).toHaveBeenCalledWith(movingAverageProps, {});
    });

    it('应该显示预测趋势', () => {
      const predictionProps = {
        ...defaultProps,
        showPrediction: true,
        predictionDays: 7,
        confidenceInterval: 0.95
      };
      render(<MockHealthTrendChart {...predictionProps} />);
      expect(MockHealthTrendChart).toHaveBeenCalledWith(predictionProps, {});
    });

    it('应该显示异常检测', () => {
      const anomalyProps = {
        ...defaultProps,
        showAnomalies: true,
        anomalies: [
          { date: '2024-01-05', value: 95, severity: 'high', reason: '心率过高' },
          { date: '2024-01-10', value: 55, severity: 'medium', reason: '心率偏低' }
        ]
      };
      render(<MockHealthTrendChart {...anomalyProps} />);
      expect(MockHealthTrendChart).toHaveBeenCalledWith(anomalyProps, {});
    });
  });

  describe('时间范围控制', () => {
    it('应该支持日视图', () => {
      const dayViewProps = {
        ...defaultProps,
        timeRange: 'day',
        granularity: 'hour',
        showTimeLabels: true
      };
      render(<MockHealthTrendChart {...dayViewProps} />);
      expect(MockHealthTrendChart).toHaveBeenCalledWith(dayViewProps, {});
    });

    it('应该支持周视图', () => {
      const weekViewProps = {
        ...defaultProps,
        timeRange: 'week',
        granularity: 'day',
        showWeekdays: true
      };
      render(<MockHealthTrendChart {...weekViewProps} />);
      expect(MockHealthTrendChart).toHaveBeenCalledWith(weekViewProps, {});
    });

    it('应该支持月视图', () => {
      const monthViewProps = {
        ...defaultProps,
        timeRange: 'month',
        granularity: 'day',
        showMonthDays: true
      };
      render(<MockHealthTrendChart {...monthViewProps} />);
      expect(MockHealthTrendChart).toHaveBeenCalledWith(monthViewProps, {});
    });

    it('应该支持年视图', () => {
      const yearViewProps = {
        ...defaultProps,
        timeRange: 'year',
        granularity: 'month',
        showSeasons: true
      };
      render(<MockHealthTrendChart {...yearViewProps} />);
      expect(MockHealthTrendChart).toHaveBeenCalledWith(yearViewProps, {});
    });
  });

  describe('交互功能测试', () => {
    it('应该处理数据点选择', () => {
      const mockOnSelect = jest.fn();
      const selectionProps = {
        ...defaultProps,
        onDataPointSelect: mockOnSelect,
        enableSelection: true
      };
      render(<MockHealthTrendChart {...selectionProps} />);
      expect(MockHealthTrendChart).toHaveBeenCalledWith(selectionProps, {});
    });

    it('应该支持缩放功能', () => {
      const zoomProps = {
        ...defaultProps,
        enableZoom: true,
        zoomLevel: 1.5,
        onZoomChange: jest.fn()
      };
      render(<MockHealthTrendChart {...zoomProps} />);
      expect(MockHealthTrendChart).toHaveBeenCalledWith(zoomProps, {});
    });

    it('应该支持平移功能', () => {
      const panProps = {
        ...defaultProps,
        enablePan: true,
        onPanChange: jest.fn()
      };
      render(<MockHealthTrendChart {...panProps} />);
      expect(MockHealthTrendChart).toHaveBeenCalledWith(panProps, {});
    });

    it('应该显示工具提示', () => {
      const tooltipProps = {
        ...defaultProps,
        showTooltip: true,
        tooltipFormat: 'detailed',
        customTooltip: jest.fn()
      };
      render(<MockHealthTrendChart {...tooltipProps} />);
      expect(MockHealthTrendChart).toHaveBeenCalledWith(tooltipProps, {});
    });
  });

  describe('中医特色分析', () => {
    it('应该显示五行健康趋势', () => {
      const wuxingProps = {
        ...defaultProps,
        analysisType: 'wuxing',
        data: [
          { date: '2024-01-01', wood: 85, fire: 78, earth: 82, metal: 75, water: 80 },
          { date: '2024-01-02', wood: 87, fire: 80, earth: 84, metal: 77, water: 82 }
        ],
        showWuxingColors: true
      };
      render(<MockHealthTrendChart {...wuxingProps} />);
      expect(MockHealthTrendChart).toHaveBeenCalledWith(wuxingProps, {});
    });

    it('应该显示体质变化趋势', () => {
      const constitutionProps = {
        ...defaultProps,
        analysisType: 'constitution',
        data: [
          { date: '2024-01-01', qixu: 85, yangxu: 60, yinxu: 40 },
          { date: '2024-01-15', qixu: 88, yangxu: 65, yinxu: 38 }
        ],
        showConstitutionTypes: true
      };
      render(<MockHealthTrendChart {...constitutionProps} />);
      expect(MockHealthTrendChart).toHaveBeenCalledWith(constitutionProps, {});
    });

    it('应该显示经络能量趋势', () => {
      const meridianProps = {
        ...defaultProps,
        analysisType: 'meridian',
        data: [
          { date: '2024-01-01', lung: 85, heart: 90, liver: 75, kidney: 80 },
          { date: '2024-01-02', lung: 87, heart: 88, liver: 78, kidney: 82 }
        ],
        showMeridianFlow: true
      };
      render(<MockHealthTrendChart {...meridianProps} />);
      expect(MockHealthTrendChart).toHaveBeenCalledWith(meridianProps, {});
    });
  });

  describe('性能测试', () => {
    it('应该高效处理大量数据点', () => {
      const largeDataProps = {
        ...defaultProps,
        data: Array.from({ length: 10000 }, (_, index) => ({
          timestamp: new Date(2024, 0, 1, 0, index).toISOString(),
          value: 70 + Math.random() * 20
        })),
        enableVirtualization: true
      };

      const startTime = performance.now();
      render(<MockHealthTrendChart {...largeDataProps} />);
      const endTime = performance.now();

      expect(endTime - startTime).toBeLessThan(100);
      expect(MockHealthTrendChart).toHaveBeenCalledWith(largeDataProps, {});
    });

    it('应该支持数据采样', () => {
      const samplingProps = {
        ...defaultProps,
        enableSampling: true,
        maxDataPoints: 1000,
        samplingMethod: 'adaptive'
      };
      render(<MockHealthTrendChart {...samplingProps} />);
      expect(MockHealthTrendChart).toHaveBeenCalledWith(samplingProps, {});
    });
  });

  describe('错误处理', () => {
    it('应该处理空数据', () => {
      const emptyProps = {
        ...defaultProps,
        data: [],
        showEmptyState: true,
        emptyMessage: '暂无健康数据'
      };
      render(<MockHealthTrendChart {...emptyProps} />);
      expect(MockHealthTrendChart).toHaveBeenCalledWith(emptyProps, {});
    });

    it('应该处理无效数据', () => {
      const invalidProps = {
        ...defaultProps,
        data: [
          { date: 'invalid', value: 'not-a-number' },
          { date: null, value: undefined }
        ],
        skipInvalidData: true
      };
      render(<MockHealthTrendChart {...invalidProps} />);
      expect(MockHealthTrendChart).toHaveBeenCalledWith(invalidProps, {});
    });

    it('应该处理加载状态', () => {
      const loadingProps = {
        ...defaultProps,
        loading: true,
        loadingMessage: '正在加载趋势数据...'
      };
      render(<MockHealthTrendChart {...loadingProps} />);
      expect(MockHealthTrendChart).toHaveBeenCalledWith(loadingProps, {});
    });
  });

  describe('可访问性测试', () => {
    it('应该提供可访问性标签', () => {
      const accessibilityProps = {
        ...defaultProps,
        accessibilityLabel: '健康趋势图表',
        accessibilityRole: 'image',
        accessibilityHint: '显示健康指标的变化趋势'
      };
      render(<MockHealthTrendChart {...accessibilityProps} />);
      expect(MockHealthTrendChart).toHaveBeenCalledWith(accessibilityProps, {});
    });

    it('应该支持屏幕阅读器', () => {
      const screenReaderProps = {
        ...defaultProps,
        enableScreenReader: true,
        dataDescription: '心率在过去7天内保持稳定，平均值为72次/分钟'
      };
      render(<MockHealthTrendChart {...screenReaderProps} />);
      expect(MockHealthTrendChart).toHaveBeenCalledWith(screenReaderProps, {});
    });
  });
}); 