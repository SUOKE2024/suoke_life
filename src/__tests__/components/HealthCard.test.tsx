import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import { View, Text, TouchableOpacity } from 'react-native';

// Mock健康卡片组件
const HealthCard: React.FC<{
  title: string;
  value: string | number;
  unit?: string;
  trend?: 'up' | 'down' | 'stable';
  status?: 'normal' | 'warning' | 'danger';
  onPress?: () => void;
  description?: string;
}> = ({ title, value, unit, trend, status = 'normal', onPress, description }) => {
  const getStatusColor = () => {
    switch (status) {
      case 'warning': return '#FFA500';
      case 'danger': return '#FF4444';
      default: return '#4CAF50';
    }
  };

  const getTrendIcon = () => {
    switch (trend) {
      case 'up': return '↗️';
      case 'down': return '↘️';
      case 'stable': return '→';
      default: return '';
    }
  };

  return (
    <TouchableOpacity testID="health-card" onPress={onPress}>
      <View style={{ borderColor: getStatusColor() }}>
        <Text testID="health-card-title">{title}</Text>
        <View testID="health-card-value-container">
          <Text testID="health-card-value">{value.toString()}</Text>
          {unit && <Text testID="health-card-unit">{unit}</Text>}
          {trend && <Text testID="health-card-trend">{getTrendIcon()}</Text>}
        </View>
        {description && (
          <Text testID="health-card-description">{description}</Text>
        )}
        <Text testID="health-card-status" style={{ color: getStatusColor() }}>
          {status}
        </Text>
      </View>
    </TouchableOpacity>
  );
};

// Mock数据
const mockHealthData = {
  title: '血压',
  value: '120/80',
  unit: 'mmHg',
  trend: 'stable' as const,
  status: 'normal' as const,
  description: '血压正常范围内',
};

describe('HealthCard', () => {
  it('应该正确渲染健康卡片基本信息', () => {
    const { getByTestId } = render(
      <HealthCard {...mockHealthData} />
    );

    expect(getByTestId('health-card-title')).toHaveTextContent('血压');
    expect(getByTestId('health-card-value')).toHaveTextContent('120/80');
    expect(getByTestId('health-card-unit')).toHaveTextContent('mmHg');
    expect(getByTestId('health-card-description')).toHaveTextContent('血压正常范围内');
  });

  it('应该正确显示趋势图标', () => {
    const { getByTestId, rerender } = render(
      <HealthCard {...mockHealthData} trend="up" />
    );

    expect(getByTestId('health-card-trend')).toHaveTextContent('↗️');

    rerender(<HealthCard {...mockHealthData} trend="down" />);
    expect(getByTestId('health-card-trend')).toHaveTextContent('↘️');

    rerender(<HealthCard {...mockHealthData} trend="stable" />);
    expect(getByTestId('health-card-trend')).toHaveTextContent('→');
  });

  it('应该正确显示不同的状态', () => {
    const { getByTestId, rerender } = render(
      <HealthCard {...mockHealthData} status="normal" />
    );

    expect(getByTestId('health-card-status')).toHaveTextContent('normal');

    rerender(<HealthCard {...mockHealthData} status="warning" />);
    expect(getByTestId('health-card-status')).toHaveTextContent('warning');

    rerender(<HealthCard {...mockHealthData} status="danger" />);
    expect(getByTestId('health-card-status')).toHaveTextContent('danger');
  });

  it('应该处理点击事件', () => {
    const mockOnPress = jest.fn();
    const { getByTestId } = render(
      <HealthCard {...mockHealthData} onPress={mockOnPress} />
    );

    fireEvent.press(getByTestId('health-card'));
    expect(mockOnPress).toHaveBeenCalledTimes(1);
  });

  it('应该处理没有可选属性的情况', () => {
    const minimalData = {
      title: '心率',
      value: 72,
    };

    const { getByTestId, queryByTestId } = render(
      <HealthCard {...minimalData} />
    );

    expect(getByTestId('health-card-title')).toHaveTextContent('心率');
    expect(getByTestId('health-card-value')).toHaveTextContent('72');
    expect(queryByTestId('health-card-unit')).toBeNull();
    expect(queryByTestId('health-card-trend')).toBeNull();
    expect(queryByTestId('health-card-description')).toBeNull();
  });

  it('应该正确处理数字类型的值', () => {
    const numericData = {
      title: '体重',
      value: 65.5,
      unit: 'kg',
    };

    const { getByTestId } = render(
      <HealthCard {...numericData} />
    );

    expect(getByTestId('health-card-value')).toHaveTextContent('65.5');
  });

  it('应该处理没有点击事件的情况', () => {
    const { getByTestId } = render(
      <HealthCard {...mockHealthData} />
    );

    // 应该不会抛出错误
    expect(() => {
      fireEvent.press(getByTestId('health-card'));
    }).not.toThrow();
  });
}); 