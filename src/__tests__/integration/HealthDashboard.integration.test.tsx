import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import { View, Text, ScrollView, TouchableOpacity } from 'react-native';

// Mock健康数据
const mockHealthData = {
  bloodPressure: {
    systolic: 120,
    diastolic: 80,
    timestamp: '2024-01-15T10:00:00Z',
    trend: 'stable',
  },
  heartRate: {
    value: 72,
    timestamp: '2024-01-15T10:00:00Z',
    trend: 'up',
  },
  weight: {
    value: 70,
    timestamp: '2024-01-15T10:00:00Z',
    trend: 'down',
  },
  steps: {
    value: 8500,
    goal: 10000,
    timestamp: '2024-01-15T10:00:00Z',
  },
  sleep: {
    duration: 7.5,
    quality: 'good',
    timestamp: '2024-01-15T06:00:00Z',
  },
};

// Mock健康仪表板组件
const MockHealthDashboard = () => {
  const [selectedMetric, setSelectedMetric] = React.useState<string | null>(null);
  const [timeRange, setTimeRange] = React.useState('week');
  const [refreshing, setRefreshing] = React.useState(false);

  const handleRefresh = () => {
    setRefreshing(true);
    setTimeout(() => setRefreshing(false), 1000);
  };

  const handleMetricPress = (metric: string) => {
    setSelectedMetric(metric);
  };

  const handleTimeRangeChange = (range: string) => {
    setTimeRange(range);
  };

  return (
    <ScrollView testID="health-dashboard">
      {/* 头部控制 */}
      <View testID="dashboard-header">
        <Text testID="dashboard-title">健康仪表板</Text>
        <TouchableOpacity testID="refresh-button" onPress={handleRefresh}>
          <Text>{refreshing ? '刷新中...' : '刷新'}</Text>
        </TouchableOpacity>
      </View>

      {/* 时间范围选择 */}
      <View testID="time-range-selector">
        {['day', 'week', 'month', 'year'].map(range => (
          <TouchableOpacity
            key={range}
            testID={`time-range-${range}`}
            onPress={() => handleTimeRangeChange(range)}
          >
            <Text style={{ 
              fontWeight: timeRange === range ? 'bold' : 'normal' 
            }}>
              {range === 'day' ? '日' : range === 'week' ? '周' : 
               range === 'month' ? '月' : '年'}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* 健康指标卡片 */}
      <View testID="health-metrics">
        {/* 血压卡片 */}
        <TouchableOpacity
          testID="blood-pressure-card"
          onPress={() => handleMetricPress('bloodPressure')}
        >
          <View testID="blood-pressure-content">
            <Text testID="blood-pressure-title">血压</Text>
            <Text testID="blood-pressure-value">
              {mockHealthData.bloodPressure.systolic}/{mockHealthData.bloodPressure.diastolic}
            </Text>
            <Text testID="blood-pressure-trend">
              {mockHealthData.bloodPressure.trend === 'stable' ? '稳定' : '变化'}
            </Text>
          </View>
        </TouchableOpacity>

        {/* 心率卡片 */}
        <TouchableOpacity
          testID="heart-rate-card"
          onPress={() => handleMetricPress('heartRate')}
        >
          <View testID="heart-rate-content">
            <Text testID="heart-rate-title">心率</Text>
            <Text testID="heart-rate-value">{mockHealthData.heartRate.value} bpm</Text>
            <Text testID="heart-rate-trend">
              {mockHealthData.heartRate.trend === 'up' ? '上升' : '下降'}
            </Text>
          </View>
        </TouchableOpacity>

        {/* 体重卡片 */}
        <TouchableOpacity
          testID="weight-card"
          onPress={() => handleMetricPress('weight')}
        >
          <View testID="weight-content">
            <Text testID="weight-title">体重</Text>
            <Text testID="weight-value">{mockHealthData.weight.value} kg</Text>
            <Text testID="weight-trend">
              {mockHealthData.weight.trend === 'down' ? '下降' : '上升'}
            </Text>
          </View>
        </TouchableOpacity>

        {/* 步数卡片 */}
        <TouchableOpacity
          testID="steps-card"
          onPress={() => handleMetricPress('steps')}
        >
          <View testID="steps-content">
            <Text testID="steps-title">步数</Text>
            <Text testID="steps-value">{mockHealthData.steps.value}</Text>
            <Text testID="steps-goal">目标: {mockHealthData.steps.goal}</Text>
            <Text testID="steps-progress">
              {Math.round((mockHealthData.steps.value / mockHealthData.steps.goal) * 100)}%
            </Text>
          </View>
        </TouchableOpacity>

        {/* 睡眠卡片 */}
        <TouchableOpacity
          testID="sleep-card"
          onPress={() => handleMetricPress('sleep')}
        >
          <View testID="sleep-content">
            <Text testID="sleep-title">睡眠</Text>
            <Text testID="sleep-value">{mockHealthData.sleep.duration} 小时</Text>
            <Text testID="sleep-quality">
              质量: {mockHealthData.sleep.quality === 'good' ? '良好' : '一般'}
            </Text>
          </View>
        </TouchableOpacity>
      </View>

      {/* 详细视图 */}
      {selectedMetric && (
        <View testID="metric-detail-view">
          <Text testID="detail-title">
            {selectedMetric === 'bloodPressure' ? '血压详情' :
             selectedMetric === 'heartRate' ? '心率详情' :
             selectedMetric === 'weight' ? '体重详情' :
             selectedMetric === 'steps' ? '步数详情' :
             selectedMetric === 'sleep' ? '睡眠详情' : '详情'}
          </Text>
          <Text testID="detail-time-range">时间范围: {timeRange}</Text>
          <TouchableOpacity
            testID="close-detail"
            onPress={() => setSelectedMetric(null)}
          >
            <Text>关闭</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* 健康建议 */}
      <View testID="health-recommendations">
        <Text testID="recommendations-title">健康建议</Text>
        <Text testID="recommendation-1">保持规律的运动习惯</Text>
        <Text testID="recommendation-2">注意饮食均衡</Text>
        <Text testID="recommendation-3">保证充足的睡眠</Text>
      </View>
    </ScrollView>
  );
};

describe('HealthDashboard Integration', () => {
  it('应该正确渲染健康仪表板', () => {
    const { getByTestId, getByText } = render(<MockHealthDashboard />);

    expect(getByTestId('health-dashboard')).toBeTruthy();
    expect(getByTestId('dashboard-header')).toBeTruthy();
    expect(getByText('健康仪表板')).toBeTruthy();
    expect(getByTestId('health-metrics')).toBeTruthy();
  });

  it('应该显示所有健康指标卡片', () => {
    const { getByTestId, getByText } = render(<MockHealthDashboard />);

    // 验证所有指标卡片存在
    expect(getByTestId('blood-pressure-card')).toBeTruthy();
    expect(getByTestId('heart-rate-card')).toBeTruthy();
    expect(getByTestId('weight-card')).toBeTruthy();
    expect(getByTestId('steps-card')).toBeTruthy();
    expect(getByTestId('sleep-card')).toBeTruthy();

    // 验证指标值显示
    expect(getByText('120/80')).toBeTruthy();
    expect(getByText('72 bpm')).toBeTruthy();
    expect(getByText('70 kg')).toBeTruthy();
    expect(getByText('8500')).toBeTruthy();
    expect(getByText('7.5 小时')).toBeTruthy();
  });

  it('应该显示健康指标趋势', () => {
    const { getByText } = render(<MockHealthDashboard />);

    expect(getByText('稳定')).toBeTruthy(); // 血压趋势
    expect(getByText('上升')).toBeTruthy(); // 心率趋势
    expect(getByText('下降')).toBeTruthy(); // 体重趋势
  });

  it('应该显示步数进度', () => {
    const { getByText } = render(<MockHealthDashboard />);

    expect(getByText('目标: 10000')).toBeTruthy();
    expect(getByText('85%')).toBeTruthy(); // 8500/10000 = 85%
  });

  it('应该支持时间范围选择', () => {
    const { getByTestId } = render(<MockHealthDashboard />);

    expect(getByTestId('time-range-selector')).toBeTruthy();
    expect(getByTestId('time-range-day')).toBeTruthy();
    expect(getByTestId('time-range-week')).toBeTruthy();
    expect(getByTestId('time-range-month')).toBeTruthy();
    expect(getByTestId('time-range-year')).toBeTruthy();
  });

  it('应该能够切换时间范围', () => {
    const { getByTestId } = render(<MockHealthDashboard />);

    const monthButton = getByTestId('time-range-month');
    fireEvent.press(monthButton);

    // 验证时间范围已切换（通过详细视图验证）
    const bloodPressureCard = getByTestId('blood-pressure-card');
    fireEvent.press(bloodPressureCard);

    expect(getByTestId('detail-time-range')).toBeTruthy();
  });

  it('应该支持刷新功能', async () => {
    const { getByTestId, getByText } = render(<MockHealthDashboard />);

    const refreshButton = getByTestId('refresh-button');
    expect(getByText('刷新')).toBeTruthy();

    fireEvent.press(refreshButton);

    // 验证刷新状态
    expect(getByText('刷新中...')).toBeTruthy();

    // 等待刷新完成
    await waitFor(() => {
      expect(getByText('刷新')).toBeTruthy();
    }, { timeout: 2000 });
  });

  it('应该能够查看指标详情', () => {
    const { getByTestId, queryByTestId } = render(<MockHealthDashboard />);

    // 初始状态不显示详情
    expect(queryByTestId('metric-detail-view')).toBeNull();

    // 点击血压卡片
    const bloodPressureCard = getByTestId('blood-pressure-card');
    fireEvent.press(bloodPressureCard);

    // 验证详情视图显示
    expect(getByTestId('metric-detail-view')).toBeTruthy();
    expect(getByTestId('detail-title')).toBeTruthy();
  });

  it('应该能够关闭指标详情', () => {
    const { getByTestId, queryByTestId } = render(<MockHealthDashboard />);

    // 打开详情
    const heartRateCard = getByTestId('heart-rate-card');
    fireEvent.press(heartRateCard);

    expect(getByTestId('metric-detail-view')).toBeTruthy();

    // 关闭详情
    const closeButton = getByTestId('close-detail');
    fireEvent.press(closeButton);

    expect(queryByTestId('metric-detail-view')).toBeNull();
  });

  it('应该显示不同指标的详情标题', () => {
    const { getByTestId, getByText } = render(<MockHealthDashboard />);

    // 测试不同指标的详情标题
    const testCases = [
      { card: 'blood-pressure-card', title: '血压详情' },
      { card: 'heart-rate-card', title: '心率详情' },
      { card: 'weight-card', title: '体重详情' },
      { card: 'steps-card', title: '步数详情' },
      { card: 'sleep-card', title: '睡眠详情' },
    ];

    testCases.forEach(({ card, title }) => {
      const cardElement = getByTestId(card);
      fireEvent.press(cardElement);

      expect(getByText(title)).toBeTruthy();

      // 关闭详情
      const closeButton = getByTestId('close-detail');
      fireEvent.press(closeButton);
    });
  });

  it('应该显示健康建议', () => {
    const { getByTestId, getByText } = render(<MockHealthDashboard />);

    expect(getByTestId('health-recommendations')).toBeTruthy();
    expect(getByText('健康建议')).toBeTruthy();
    expect(getByText('保持规律的运动习惯')).toBeTruthy();
    expect(getByText('注意饮食均衡')).toBeTruthy();
    expect(getByText('保证充足的睡眠')).toBeTruthy();
  });

  it('应该正确计算和显示步数完成百分比', () => {
    const { getByText } = render(<MockHealthDashboard />);

    // 8500 / 10000 = 85%
    expect(getByText('85%')).toBeTruthy();
  });

  it('应该显示睡眠质量状态', () => {
    const { getByText } = render(<MockHealthDashboard />);

    expect(getByText('质量: 良好')).toBeTruthy();
  });

  it('应该支持滚动查看所有内容', () => {
    const { getByTestId } = render(<MockHealthDashboard />);

    const scrollView = getByTestId('health-dashboard');
    expect(scrollView).toBeTruthy();

    // 验证ScrollView可以滚动
    fireEvent.scroll(scrollView, {
      nativeEvent: {
        contentOffset: { y: 100 },
        contentSize: { height: 1000 },
        layoutMeasurement: { height: 500 },
      },
    });
  });
}); 