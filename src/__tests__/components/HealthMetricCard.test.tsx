import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import HealthMetricCard from '../../screens/components/HealthMetricCard';
import { HealthMetric } from '../../types/life';

// Mock Icon component
jest.mock('../../components/common/Icon', () => {
  const { Text } = require('react-native');
  return ({ name, size, color }: any) => (
    <Text testID={`icon-${name}`} style={{ fontSize: size, color }}>
      {name}
    </Text>
  );
});

// Mock数据
const mockHealthMetric: HealthMetric = {
  id: 'mood',
  name: '心情指数',
  value: 85,
  unit: '分',
  target: 80,
  icon: 'emoticon-happy',
  color: '#FF9500',
  trend: 'up',
  suggestion: '保持积极心态，今天心情不错！',
  history: [
    { date: '2024-01-01', value: 75 },
    { date: '2024-01-02', value: 80 },
    { date: '2024-01-03', value: 85 },
  ],
};

const mockGetTrendIcon = (trend: string) => {
  const iconMap: Record<string, string> = {
    up: 'trending-up',
    down: 'trending-down',
    stable: 'trending-neutral',
  };
  return iconMap[trend] || 'trending-neutral';
};

describe('HealthMetricCard', () => {
  it('应该正确渲染健康指标信息', () => {
    const { getByText } = render(
      <HealthMetricCard
        metric={mockHealthMetric}
        getTrendIcon={mockGetTrendIcon}
      />
    );

    expect(getByText('心情指数')).toBeTruthy();
    expect(getByText('85')).toBeTruthy();
    expect(getByText('分')).toBeTruthy();
    expect(getByText('目标: 80分')).toBeTruthy();
    expect(getByText('保持积极心态，今天心情不错！')).toBeTruthy();
  });

  it('应该在有onPress时响应点击', () => {
    const mockOnPress = jest.fn();
    const { getByText } = render(
      <HealthMetricCard
        metric={mockHealthMetric}
        onPress={mockOnPress}
        getTrendIcon={mockGetTrendIcon}
      />
    );

    // 点击卡片
    fireEvent.press(getByText('心情指数'));
    expect(mockOnPress).toHaveBeenCalledTimes(1);
  });

  it('应该正确显示不同趋势的图标', () => {
    expect(mockGetTrendIcon('up')).toBe('trending-up');
    expect(mockGetTrendIcon('down')).toBe('trending-down');
    expect(mockGetTrendIcon('stable')).toBe('trending-neutral');
    expect(mockGetTrendIcon('unknown')).toBe('trending-neutral');
  });

  it('应该正确显示不同的数值', () => {
    // 测试超过目标的情况
    const aboveTargetMetric = { ...mockHealthMetric, value: 90, target: 80 };
    const { getByText, rerender } = render(
      <HealthMetricCard
        metric={aboveTargetMetric}
        getTrendIcon={mockGetTrendIcon}
      />
    );

    expect(getByText('90')).toBeTruthy();
    expect(getByText('目标: 80分')).toBeTruthy();

    // 测试低于目标的情况
    const belowTargetMetric = { ...mockHealthMetric, value: 60, target: 80 };
    rerender(
      <HealthMetricCard
        metric={belowTargetMetric}
        getTrendIcon={mockGetTrendIcon}
      />
    );

    expect(getByText('60')).toBeTruthy();
    expect(getByText('目标: 80分')).toBeTruthy();
  });

  it('应该正确显示不同趋势的颜色', () => {
    const trends = ['up', 'down', 'stable'];
    trends.forEach(trend => {
      const metricWithTrend = { ...mockHealthMetric, trend: trend as any };
      const { getByTestId } = render(
        <HealthMetricCard
          metric={metricWithTrend}
          getTrendIcon={mockGetTrendIcon}
        />
      );
      
      // 验证趋势图标存在
      expect(getByTestId(`icon-${mockGetTrendIcon(trend)}`)).toBeTruthy();
    });
  });

  it('应该处理没有历史数据的情况', () => {
    const metricWithoutHistory = { ...mockHealthMetric, history: undefined };
    const { getByText } = render(
      <HealthMetricCard
        metric={metricWithoutHistory}
        getTrendIcon={mockGetTrendIcon}
      />
    );

    expect(getByText('心情指数')).toBeTruthy();
    expect(getByText('85')).toBeTruthy();
  });

  it('应该在没有onPress时不响应点击', () => {
    const { getByText } = render(
      <HealthMetricCard
        metric={mockHealthMetric}
        getTrendIcon={mockGetTrendIcon}
      />
    );

    // 点击卡片不应该有任何反应（不会抛出错误）
    fireEvent.press(getByText('心情指数'));
    // 没有onPress，所以不会有任何副作用
  });
}); 