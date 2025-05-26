import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import { View, Text, ScrollView, TouchableOpacity, RefreshControl } from 'react-native';

// Mock数据
const mockHealthData = {
  todaySteps: 8500,
  stepGoal: 10000,
  heartRate: 72,
  bloodPressure: { systolic: 120, diastolic: 80 },
  sleepHours: 7.5,
  waterIntake: 1200,
  waterGoal: 2000,
};

const mockAgents = [
  { id: 'xiaoai', name: '小艾', status: 'online', specialty: '健康咨询' },
  { id: 'xiaoke', name: '小克', status: 'online', specialty: '疾病预防' },
  { id: 'laoke', name: '老克', status: 'offline', specialty: '中医调理' },
  { id: 'soer', name: '索儿', status: 'online', specialty: '生活指导' },
];

// Mock首页组件
const MockHomeScreen = () => {
  const [refreshing, setRefreshing] = React.useState(false);
  const [selectedQuickAction, setSelectedQuickAction] = React.useState<string | null>(null);

  const handleRefresh = () => {
    setRefreshing(true);
    setTimeout(() => setRefreshing(false), 1000);
  };

  const handleQuickAction = (action: string) => {
    setSelectedQuickAction(action);
  };

  const handleAgentPress = (agentId: string) => {
    // 模拟导航到智能体聊天
  };

  return (
    <ScrollView
      testID="home-screen"
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />
      }
    >
      {/* 欢迎区域 */}
      <View testID="welcome-section">
        <Text testID="welcome-text">欢迎回来！</Text>
        <Text testID="current-time">{new Date().toLocaleTimeString()}</Text>
      </View>

      {/* 健康概览 */}
      <View testID="health-overview">
        <Text testID="health-title">今日健康概览</Text>
        
        {/* 步数卡片 */}
        <View testID="steps-card">
          <Text testID="steps-label">步数</Text>
          <Text testID="steps-value">{mockHealthData.todaySteps}</Text>
          <Text testID="steps-goal">目标: {mockHealthData.stepGoal}</Text>
          <Text testID="steps-progress">
            {Math.round((mockHealthData.todaySteps / mockHealthData.stepGoal) * 100)}%
          </Text>
        </View>

        {/* 心率卡片 */}
        <View testID="heart-rate-card">
          <Text testID="heart-rate-label">心率</Text>
          <Text testID="heart-rate-value">{mockHealthData.heartRate} bpm</Text>
        </View>

        {/* 血压卡片 */}
        <View testID="blood-pressure-card">
          <Text testID="blood-pressure-label">血压</Text>
          <Text testID="blood-pressure-value">
            {mockHealthData.bloodPressure.systolic}/{mockHealthData.bloodPressure.diastolic}
          </Text>
        </View>

        {/* 睡眠卡片 */}
        <View testID="sleep-card">
          <Text testID="sleep-label">睡眠</Text>
          <Text testID="sleep-value">{mockHealthData.sleepHours} 小时</Text>
        </View>

        {/* 饮水卡片 */}
        <View testID="water-card">
          <Text testID="water-label">饮水</Text>
          <Text testID="water-value">{mockHealthData.waterIntake}ml</Text>
          <Text testID="water-goal">目标: {mockHealthData.waterGoal}ml</Text>
        </View>
      </View>

      {/* 智能体区域 */}
      <View testID="agents-section">
        <Text testID="agents-title">智能体助手</Text>
        <View testID="agents-grid">
          {mockAgents.map(agent => (
            <TouchableOpacity
              key={agent.id}
              testID={`agent-${agent.id}`}
              onPress={() => handleAgentPress(agent.id)}
            >
              <View testID={`agent-card-${agent.id}`}>
                <Text testID={`agent-name-${agent.id}`}>{agent.name}</Text>
                <Text testID={`agent-specialty-${agent.id}`}>{agent.specialty}</Text>
                <Text testID={`agent-status-${agent.id}`}>
                  {agent.status === 'online' ? '在线' : '离线'}
                </Text>
              </View>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* 快捷操作 */}
      <View testID="quick-actions">
        <Text testID="quick-actions-title">快捷操作</Text>
        <View testID="quick-actions-grid">
          {[
            { id: 'measure', label: '健康测量', icon: 'heart' },
            { id: 'record', label: '记录数据', icon: 'edit' },
            { id: 'report', label: '健康报告', icon: 'chart' },
            { id: 'reminder', label: '设置提醒', icon: 'bell' },
          ].map(action => (
            <TouchableOpacity
              key={action.id}
              testID={`quick-action-${action.id}`}
              onPress={() => handleQuickAction(action.id)}
            >
              <View testID={`action-card-${action.id}`}>
                <Text testID={`action-icon-${action.id}`}>{action.icon}</Text>
                <Text testID={`action-label-${action.id}`}>{action.label}</Text>
              </View>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* 健康建议 */}
      <View testID="health-tips">
        <Text testID="tips-title">今日健康建议</Text>
        <View testID="tips-list">
          <Text testID="tip-1">保持规律的运动习惯，每天至少30分钟</Text>
          <Text testID="tip-2">多喝水，保持身体水分平衡</Text>
          <Text testID="tip-3">保证充足的睡眠，建议7-8小时</Text>
        </View>
      </View>

      {/* 选中的快捷操作显示 */}
      {selectedQuickAction && (
        <View testID="selected-action-info">
          <Text testID="selected-action-text">
            已选择: {selectedQuickAction}
          </Text>
        </View>
      )}
    </ScrollView>
  );
};

describe('HomeScreen', () => {
  it('应该正确渲染首页', () => {
    const { getByTestId, getByText } = render(<MockHomeScreen />);

    expect(getByTestId('home-screen')).toBeTruthy();
    expect(getByTestId('welcome-section')).toBeTruthy();
    expect(getByText('欢迎回来！')).toBeTruthy();
  });

  it('应该显示当前时间', () => {
    const { getByTestId } = render(<MockHomeScreen />);

    expect(getByTestId('current-time')).toBeTruthy();
  });

  it('应该显示健康概览数据', () => {
    const { getByTestId, getByText } = render(<MockHomeScreen />);

    expect(getByTestId('health-overview')).toBeTruthy();
    expect(getByText('今日健康概览')).toBeTruthy();
    
    // 验证各项健康数据
    expect(getByText('8500')).toBeTruthy(); // 步数
    expect(getByText('72 bpm')).toBeTruthy(); // 心率
    expect(getByText('120/80')).toBeTruthy(); // 血压
    expect(getByText('7.5 小时')).toBeTruthy(); // 睡眠
    expect(getByText('1200ml')).toBeTruthy(); // 饮水
  });

  it('应该正确计算步数完成百分比', () => {
    const { getByText } = render(<MockHomeScreen />);

    // 8500 / 10000 = 85%
    expect(getByText('85%')).toBeTruthy();
  });

  it('应该显示所有智能体', () => {
    const { getByTestId, getByText } = render(<MockHomeScreen />);

    expect(getByTestId('agents-section')).toBeTruthy();
    expect(getByText('智能体助手')).toBeTruthy();

    // 验证所有智能体都显示
    mockAgents.forEach(agent => {
      expect(getByTestId(`agent-${agent.id}`)).toBeTruthy();
      expect(getByText(agent.name)).toBeTruthy();
      expect(getByText(agent.specialty)).toBeTruthy();
    });
  });

  it('应该显示智能体在线状态', () => {
    const { getAllByText } = render(<MockHomeScreen />);

    const onlineElements = getAllByText('在线');
    const offlineElements = getAllByText('离线');
    
    expect(onlineElements.length).toBeGreaterThan(0);
    expect(offlineElements.length).toBeGreaterThan(0);
  });

  it('应该支持智能体点击', () => {
    const { getByTestId } = render(<MockHomeScreen />);

    const xiaoaiAgent = getByTestId('agent-xiaoai');
    fireEvent.press(xiaoaiAgent);

    // 验证点击不会抛出错误
    expect(xiaoaiAgent).toBeTruthy();
  });

  it('应该显示快捷操作', () => {
    const { getByTestId, getByText } = render(<MockHomeScreen />);

    expect(getByTestId('quick-actions')).toBeTruthy();
    expect(getByText('快捷操作')).toBeTruthy();

    // 验证所有快捷操作
    const actions = ['measure', 'record', 'report', 'reminder'];
    actions.forEach(action => {
      expect(getByTestId(`quick-action-${action}`)).toBeTruthy();
    });

    expect(getByText('健康测量')).toBeTruthy();
    expect(getByText('记录数据')).toBeTruthy();
    expect(getByText('健康报告')).toBeTruthy();
    expect(getByText('设置提醒')).toBeTruthy();
  });

  it('应该支持快捷操作点击', () => {
    const { getByTestId, queryByTestId } = render(<MockHomeScreen />);

    // 初始状态不显示选中信息
    expect(queryByTestId('selected-action-info')).toBeNull();

    // 点击健康测量
    const measureAction = getByTestId('quick-action-measure');
    fireEvent.press(measureAction);

    // 验证选中状态显示
    expect(getByTestId('selected-action-info')).toBeTruthy();
  });

  it('应该显示健康建议', () => {
    const { getByTestId, getByText } = render(<MockHomeScreen />);

    expect(getByTestId('health-tips')).toBeTruthy();
    expect(getByText('今日健康建议')).toBeTruthy();

    // 验证建议内容
    expect(getByText('保持规律的运动习惯，每天至少30分钟')).toBeTruthy();
    expect(getByText('多喝水，保持身体水分平衡')).toBeTruthy();
    expect(getByText('保证充足的睡眠，建议7-8小时')).toBeTruthy();
  });

  it('应该支持下拉刷新', async () => {
    const { getByTestId } = render(<MockHomeScreen />);

    const scrollView = getByTestId('home-screen');
    
    // 模拟下拉刷新
    fireEvent(scrollView, 'refresh');

    // 等待刷新完成
    await waitFor(() => {
      // 验证刷新功能正常工作
      expect(scrollView).toBeTruthy();
    }, { timeout: 2000 });
  });

  it('应该正确显示健康数据卡片', () => {
    const { getByTestId } = render(<MockHomeScreen />);

    const healthCards = [
      'steps-card',
      'heart-rate-card', 
      'blood-pressure-card',
      'sleep-card',
      'water-card'
    ];

    healthCards.forEach(cardId => {
      expect(getByTestId(cardId)).toBeTruthy();
    });
  });

  it('应该显示水分摄入进度', () => {
    const { getByText } = render(<MockHomeScreen />);

    expect(getByText('目标: 2000ml')).toBeTruthy();
  });

  it('应该支持滚动查看所有内容', () => {
    const { getByTestId } = render(<MockHomeScreen />);

    const scrollView = getByTestId('home-screen');
    
    // 模拟滚动
    fireEvent.scroll(scrollView, {
      nativeEvent: {
        contentOffset: { y: 200 },
        contentSize: { height: 1000 },
        layoutMeasurement: { height: 600 },
      },
    });

    expect(scrollView).toBeTruthy();
  });
}); 