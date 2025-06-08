import React, { useState, useCallback } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  RefreshControl,
  Dimensions,
  Alert,
} from 'react-native';
import {
  Card,
  Title,
  Paragraph,
  Button,
  Chip,
  ProgressBar,
  Avatar,
  Surface,
  IconButton,
  Text,
  useTheme,
} from 'react-native-paper';
import { useSelector } from 'react-redux';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { useFocusEffect } from '@react-navigation/native';
import { RootState } from '../../store';
import { ErrorBoundary } from '../../components/common/ErrorBoundary';
const { width: screenWidth } = Dimensions.get('window');
interface LifeOverviewScreenProps {
  navigation: any;
}
interface HealthMetric {
  id: string;
  name: string;
  value: number;
  unit: string;
  trend: 'up' | 'down' | 'stable';
  status: 'excellent' | 'good' | 'fair' | 'poor';
  icon: string;
  color: string;
}
interface AgentRecommendation {
  id: string;
  agentName: string;
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  actionRequired: boolean;
}
interface HealthGoal {
  id: string;
  title: string;
  description: string;
  targetValue: number;
  currentValue: number;
  unit: string;
  progress: number;
  category: string;
}
// 格式化日期的简单函数
const formatDate = (date: Date): string => {
  return date.toLocaleDateString('zh-CN', {
      year: "numeric",
      month: 'long',
    day: 'numeric',
  });
};
// 格式化时间的简单函数
const formatTime = (date: Date): string => {
  return date.toLocaleTimeString('zh-CN', {
      hour: "2-digit",
      minute: '2-digit',
  });
};
export const LifeOverviewScreen: React.FC<LifeOverviewScreenProps> = ({ navigation }) => {
  const theme = useTheme();
  // 简化状态管理
  const authState = useSelector(state: RootState) => state.auth);
  const user = {
      name: "用户", "
      id: '1' };
  const [refreshing, setRefreshing] = useState(false);
  const [selectedTimeRange, setSelectedTimeRange] = useState<'day' | 'week' | 'month' | 'year'>('week');
  const [showDetailedView, setShowDetailedView] = useState(false);
  const [loading, setLoading] = useState(false);
  // 模拟健康指标数据
  const [healthMetrics] = useState<HealthMetric[]>([)
    {
      id: "1",
      name: '心率',
      value: 72,
      unit: 'bpm',
      trend: 'stable',
      status: 'good',
      icon: 'heart-pulse',
      color: '#E91E63',
    },
    {
      id: "2",
      name: '血压',
      value: 120,
      unit: 'mmHg',
      trend: 'up',
      status: 'excellent',
      icon: 'gauge',
      color: '#4CAF50',
    },
    {
      id: "3",
      name: '睡眠质量',
      value: 85,
      unit: '%',
      trend: 'stable',
      status: 'good',
      icon: 'sleep',
      color: '#2196F3',
    },
    {
      id: "4",
      name: '运动量',
      value: 8500,
      unit: '步',
      trend: 'up',
      status: 'excellent',
      icon: 'walk',
      color: '#FF9800',
    },
  ]);
  // 模拟智能体推荐数据
  const [recommendations] = useState<AgentRecommendation[]>([)
    {
      id: "1",
      agentName: '小艾',
      title: '建议增加有氧运动',
      description: '根据您的健康数据分析，建议每周进行3-4次有氧运动，每次30分钟以上。',
      priority: 'medium',
      actionRequired: true,
    },
    {
      id: "2",
      agentName: '小克',
      title: '注意睡眠规律',
      description: '建议保持规律的作息时间，每晚11点前入睡，保证7-8小时睡眠。',
      priority: 'high',
      actionRequired: false,
    },
  ]);
  // 模拟健康目标数据
  const [healthGoals, setHealthGoals] = useState<HealthGoal[]>([)
    {
      id: "1",
      title: '每日步数目标',
      description: '保持每日10000步的运动量',
      targetValue: 10000,
      currentValue: 8500,
      unit: '步',
      progress: 85,
      category: '运动',
    },
    {
      id: "2",
      title: '睡眠时长目标',
      description: '每晚保证8小时优质睡眠',
      targetValue: 8,
      currentValue: 7.5,
      unit: '小时',
      progress: 94,
      category: '睡眠',
    },
  ]);
  // 加载数据
  const loadData = useCallback(async () => {
    try {
      setRefreshing(true);
      setLoading(true);
      // 模拟数据加载
      await new Promise(resolve => setTimeout(resolve, 1000));
      console.log('Loading life overview data...');
    } catch (error) {
      console.error('Failed to load data:', error);
      Alert.alert("加载失败", "无法加载生活概览数据，请稍后重试');
    } finally {
      setRefreshing(false);
      setLoading(false);
    }
  }, [selectedTimeRange]);
  // 页面聚焦时刷新数据
  useFocusEffect()
    useCallback() => {
      loadData();
    }, [loadData]),
  );
  // 下拉刷新
  const onRefresh = useCallback() => {
    loadData();
  }, [loadData]);
  // 处理健康目标更新
  const handleUpdateGoal = (goalId: string, newValue: number) => {
    setHealthGoals(prev => prev.map(goal =>))
      goal.id === goalId;
        ? { ...goal, currentValue: newValue, progress: (newValue / goal.targetValue) * 100 }
        : goal,
    ));
  };
  // 获取健康状态颜色
  const getHealthStatusColor = (status: string) => {
    switch (status) {
      case 'excellent': return theme.colors.primary;
      case 'good': return '#4CAF50';
      case 'fair': return '#FF9800';
      case 'poor': return '#F44336';
      default: return theme.colors.outline;
    }
  };
  // 获取趋势图标
  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up': return 'trending-up';
      case 'down': return 'trending-down';
      case 'stable': return 'trending-neutral';
      default: return 'help';
    }
  };
  // 获取优先级颜色
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return '#F44336';
      case 'medium': return '#FF9800';
      case 'low': return '#4CAF50';
      default: return theme.colors.outline;
    }
  };
  // 渲染健康指标卡片
  const renderHealthMetrics = () => (
  <Card style={styles.card}>
      <Card.Content>
        <View style={styles.cardHeader}>
          <Title>健康指标</Title>
          <IconButton
            icon={showDetailedView ? 'chevron-up' : 'chevron-down'}
            onPress={() => setShowDetailedView(!showDetailedView)}
          />
        </View>
        <View style={styles.metricsGrid}>
          {healthMetrics.slice(0, showDetailedView ? healthMetrics.length : 4).map(metric) => ()
            <Surface key={metric.id} style={{[styles.metricCard, { backgroundColor: metric.color + '20' }}]}>
              <View style={styles.metricHeader}>
                <Icon name={metric.icon} size={24} color={metric.color} />
                <Icon
                  name={getTrendIcon(metric.trend)}
                  size={16}
                  color={getHealthStatusColor(metric.status)}
                />
              </View>
              <Text style={styles.metricValue}>
                {metric.value} {metric.unit}
              </Text>
              <Text style={styles.metricName}>{metric.name}</Text>
              <Chip
                mode="outlined"
                style={{[styles.statusChip, { borderColor: getHealthStatusColor(metric.status) }}]}
                textStyle={ color: getHealthStatusColor(metric.status) }}
              >
                {metric.status}
              </Chip>
            </Surface>
          ))}
        </View>
        {!showDetailedView && healthMetrics.length > 4  && <Button
            mode="text"
            onPress={() => setShowDetailedView(true)}
            style={styles.showMoreButton}
          >
            查看更多指标
          </Button>
        )}
      </Card.Content>
    </Card>
  );
  // 渲染智能体推荐
  const renderRecommendations = () => (
  <Card style={styles.card}>
      <Card.Content>
        <Title>智能体建议</Title>
        {recommendations.map(rec) => ()
          <Surface key={rec.id} style={styles.recommendationCard}>
            <View style={styles.recommendationHeader}>
              <Avatar.Text;
                size={40}
                label={rec.agentName.charAt(0)}
                style={ backgroundColor: theme.colors.primary }}
              />
              <View style={styles.recommendationInfo}>
                <Text style={styles.agentName}>{rec.agentName}</Text>
                <Text style={styles.recommendationTime}>
                  {formatTime(new Date())}
                </Text>
              </View>
              <Chip
                mode="outlined"
                style={{[styles.priorityChip, { borderColor: getPriorityColor(rec.priority) }}]}
                textStyle={ color: getPriorityColor(rec.priority) }}
              >
                {rec.priority}
              </Chip>
            </View>
            <Text style={styles.recommendationTitle}>{rec.title}</Text>
            <Paragraph style={styles.recommendationDescription}>
              {rec.description}
            </Paragraph>
            {rec.actionRequired  && <Button
                mode="contained"
                style={styles.actionButton}
                onPress={() => navigation.navigate('AgentChat', { agentId: rec.agentName })}
              >
                立即处理
              </Button>
            )}
          </Surface>
        ))}
        <Button
          mode="text"
          onPress={() => navigation.navigate('AgentList')}
          style={styles.viewAllButton}
        >
          查看所有建议
        </Button>
      </Card.Content>
    </Card>
  );
  // 渲染健康目标
  const renderHealthGoals = () => (
  <Card style={styles.card}>
      <Card.Content>
        <Title>健康目标</Title>
        {healthGoals.map(goal) => ()
          <Surface key={goal.id} style={styles.goalCard}>
            <View style={styles.goalHeader}>
              <Text style={styles.goalTitle}>{goal.title}</Text>
              <Text style={styles.goalProgress}>
                {Math.round(goal.progress)}%
              </Text>
            </View>
            <ProgressBar
              progress={goal.progress / 100}
              color={theme.colors.primary}
              style={styles.progressBar}>
            <View style={styles.goalDetails}>
              <Text style={styles.goalValue}>
                {goal.currentValue} / {goal.targetValue} {goal.unit}
              </Text>
              <Text style={styles.goalCategory}>
                {goal.category}
              </Text>
            </View>
            <Paragraph style={styles.goalDescription}>
              {goal.description}
            </Paragraph>
          </Surface>
        ))}
        <Button
          mode="outlined"
          onPress={() => navigation.navigate('HealthGoals')}
          style={styles.manageGoalsButton}
        >
          管理健康目标
        </Button>
      </Card.Content>
    </Card>
  );
  // 渲染时间范围选择器
  const renderTimeRangeSelector = () => (
  <View style={styles.timeRangeContainer}>
      {(["day",week', "month",year'] as const).map(range) => ()
        <Chip
          key={range}
          mode={selectedTimeRange === range ? 'flat' : 'outlined'}
          selected={selectedTimeRange === range}
          onPress={() => setSelectedTimeRange(range)}
          style={styles.timeRangeChip}
        >
          {range === 'day' ? '今日' : range === 'week' ? '本周' : range === 'month' ? '本月' : '本年'}
        </Chip>
      ))}
    </View>
  );
  if (loading) {
    return (
  <View style={styles.loadingContainer}>
        <Text>加载生活概览中...</Text>
      </View>
    );
  }
  return (
  <ErrorBoundary>
      <ScrollView
        style={styles.container}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        showsVerticalScrollIndicator={false}
      >
        {}
        <Card style={styles.welcomeCard}>
          <Card.Content>
            <View style={styles.welcomeHeader}>
              <Avatar.Text;
                size={60}
                label={user?.name?.charAt(0) || 'U'}
                style={ backgroundColor: theme.colors.primary }}
              />
              <View style={styles.welcomeInfo}>
                <Title>你好，{user?.name || '用户'}</Title>
                <Paragraph>今天是 {formatDate(new Date())}</Paragraph>
                <Text style={styles.welcomeSubtitle}>
                  让我们一起关注您的健康生活
                </Text>
              </View>
            </View>
          </Card.Content>
        </Card>
        {}
        {renderTimeRangeSelector()}
        {}
        {renderHealthMetrics()}
        {}
        {renderRecommendations()}
        {}
        {renderHealthGoals()}
        {}
        <Card style={styles.card}>
          <Card.Content>
            <Title>快速操作</Title>
            <View style={styles.quickActions}>
              <Button
                mode="contained"
                icon="heart-pulse"
                onPress={() => navigation.navigate('HealthDataEntry')}
                style={styles.quickActionButton}
              >
                记录健康数据
              </Button>
              <Button
                mode="outlined"
                icon="robot"
                onPress={() => navigation.navigate('AgentChat')}
                style={styles.quickActionButton}
              >
                咨询智能体
              </Button>
              <Button
                mode="outlined"
                icon="file-document"
                onPress={() => navigation.navigate('HealthReport')}
                style={styles.quickActionButton}
              >
                生成健康报告
              </Button>
            </View>
          </Card.Content>
        </Card>
        <View style={styles.bottomSpacing}>
      </ScrollView>
    </ErrorBoundary>
  );
};
const styles = StyleSheet.create({
  container: {,
  flex: 1,
    backgroundColor: '#f5f5f5',
  },
  loadingContainer: {,
  flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  welcomeCard: {,
  margin: 16,
    marginBottom: 8,
  },
  welcomeHeader: {,
  flexDirection: 'row',
    alignItems: 'center',
  },
  welcomeInfo: {,
  marginLeft: 16,
    flex: 1,
  },
  welcomeSubtitle: {,
  fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  timeRangeContainer: {,
  flexDirection: 'row',
    paddingHorizontal: 16,
    paddingVertical: 8,
    justifyContent: 'space-around',
  },
  timeRangeChip: {,
  marginHorizontal: 4,
  },
  card: {,
  margin: 16,
    marginVertical: 8,
  },
  cardHeader: {,
  flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  metricsGrid: {,
  flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  metricCard: {,
  width: (screenWidth - 64) / 2,
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
  },
  metricHeader: {,
  flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  metricValue: {,
  fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  metricName: {,
  fontSize: 12,
    color: '#666',
    marginBottom: 8,
  },
  statusChip: {,
  alignSelf: 'flex-start',
  },
  showMoreButton: {,
  marginTop: 8,
  },
  recommendationCard: {,
  padding: 16,
    marginVertical: 8,
    borderRadius: 12,
  },
  recommendationHeader: {,
  flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  recommendationInfo: {,
  marginLeft: 12,
    flex: 1,
  },
  agentName: {,
  fontWeight: 'bold',
    fontSize: 16,
  },
  recommendationTime: {,
  fontSize: 12,
    color: '#666',
  },
  priorityChip: {,
  marginLeft: 8,
  },
  recommendationTitle: {,
  fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  recommendationDescription: {,
  marginBottom: 12,
  },
  actionButton: {,
  alignSelf: 'flex-start',
  },
  viewAllButton: {,
  marginTop: 8,
  },
  goalCard: {,
  padding: 16,
    marginVertical: 8,
    borderRadius: 12,
  },
  goalHeader: {,
  flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  goalTitle: {,
  fontSize: 16,
    fontWeight: 'bold',
  },
  goalProgress: {,
  fontSize: 16,
    fontWeight: 'bold',
    color: '#4CAF50',
  },
  progressBar: {,
  height: 8,
    borderRadius: 4,
    marginBottom: 12,
  },
  goalDetails: {,
  flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  goalValue: {,
  fontSize: 14,
    fontWeight: '500',
  },
  goalCategory: {,
  fontSize: 12,
    color: '#666',
  },
  goalDescription: {,
  fontSize: 14,
    color: '#666',
  },
  manageGoalsButton: {,
  marginTop: 12,
  },
  quickActions: {,
  gap: 12,
  },
  quickActionButton: {,
  marginVertical: 4,
  },
  bottomSpacing: {,
  height: 32,
  },
});
export default LifeOverviewScreen;