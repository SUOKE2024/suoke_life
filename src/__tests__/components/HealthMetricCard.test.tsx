import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import HealthMetricCard from '../../screens/components/HealthMetricCard';
import { HealthMetric, HealthMetricHistory } from '../../types/life';

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
const mockMetric: HealthMetric = {
  id: 'mood',
  name: '心情指数',
  value: 85,
  unit: '分',
  target: 80,
  icon: 'emoticon-happy',
  color: '#4CAF50',
  trend: 'up',
  suggestion: '保持积极心态，今天心情不错！',
  history: [
    { date: '2024-01-01', value: 80 },
    { date: '2024-01-02', value: 82 },
    { date: '2024-01-03', value: 85 },
  ] as HealthMetricHistory[],
};

const mockGetTrendIcon = (trend: string) => {
  switch (trend) {
    case 'up': return 'trending-up';
    case 'down': return 'trending-down';
    default: return 'trending-neutral';
  }
};

describe('HealthMetricCard', () => {
  it('应该正确渲染健康指标信息', () => {
    const { getByText, getByTestId } = render(
      <HealthMetricCard 
        metric={mockMetric} 
        getTrendIcon={mockGetTrendIcon}
      />
    );

    // 使用testID查找元素
    expect(getByTestId('icon-emoticon-happy')).toBeTruthy();
    expect(getByText('85')).toBeTruthy();
    expect(getByText('分')).toBeTruthy();
    expect(getByText('目标: 80分')).toBeTruthy();
    expect(getByText('保持积极心态，今天心情不错！')).toBeTruthy();
  });

  it('应该在有onPress时响应点击', () => {
    const mockOnPress = jest.fn();
    const { getByTestId } = render(
      <HealthMetricCard 
        metric={mockMetric} 
        onPress={mockOnPress}
        getTrendIcon={mockGetTrendIcon}
      />
    );

    // 点击卡片容器
    const container = getByTestId('icon-emoticon-happy').parent?.parent?.parent;
    if (container) {
      fireEvent.press(container);
      expect(mockOnPress).toHaveBeenCalledTimes(1);
    }
  });

  it('应该正确显示不同的数值', () => {
    const highValueMetric = { ...mockMetric, value: 90 };
    const { getByText } = render(
      <HealthMetricCard 
        metric={highValueMetric} 
        getTrendIcon={mockGetTrendIcon}
      />
    );

    expect(getByText('90')).toBeTruthy();
    expect(getByText('目标: 80分')).toBeTruthy();

    // 测试低于目标的情况
    const lowValueMetric = { ...mockMetric, value: 70 };
    const { getByText: getByTextLow } = render(
      <HealthMetricCard 
        metric={lowValueMetric} 
        getTrendIcon={mockGetTrendIcon}
      />
    );

    expect(getByTextLow('70')).toBeTruthy();
  });

  it('应该正确显示不同趋势的图标', () => {
    const trends: ('up' | 'down' | 'stable')[] = ['up', 'down', 'stable'];
    
    trends.forEach(trend => {
      const trendMetric = { ...mockMetric, trend };
      const { getByTestId } = render(
        <HealthMetricCard 
          metric={trendMetric} 
          getTrendIcon={mockGetTrendIcon}
        />
      );
      
      // 验证趋势图标存在
      expect(getByTestId(`icon-${mockGetTrendIcon(trend)}`)).toBeTruthy();
    });
  });

  it('应该处理没有历史数据的情况', () => {
    const noHistoryMetric = { ...mockMetric, history: [] };
    const { getByText } = render(
      <HealthMetricCard 
        metric={noHistoryMetric} 
        getTrendIcon={mockGetTrendIcon}
      />
    );

    expect(getByText('85')).toBeTruthy();
  });

  it('应该在没有onPress时不响应点击', () => {
    const { getByTestId } = render(
      <HealthMetricCard 
        metric={mockMetric} 
        getTrendIcon={mockGetTrendIcon}
      />
    );

    // 点击卡片不应该有任何反应（不会抛出错误）
    const container = getByTestId('icon-emoticon-happy').parent?.parent?.parent;
    if (container) {
      fireEvent.press(container);
      // 没有onPress，所以不会有任何副作用
    }
  });
}); 