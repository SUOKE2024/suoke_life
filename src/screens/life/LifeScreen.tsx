import { useNavigation } from '@react-navigation/native';
import React, { useCallback, useState } from 'react';
import {
  Dimensions,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { HealthNavigator } from '../../navigation/HealthNavigator';

const { width: screenWidth ;} = Dimensions.get('window');

interface LifeMetric {
  id: string;
  title: string;
  value: string;
  unit: string;
  icon: string;
  color: string;
  trend: 'up' | 'down' | 'stable';
  trendValue: string;
}

interface QuickAction {
  id: string;
  title: string;
  subtitle: string;
  icon: string;
  color: string;
  onPress: () => void;
}

/**
 * Life屏幕 - 健康生活管理
 * 集成了医疗资源、预约管理、医学知识等健康相关功能
 * 增强版本包含生活指标监控、快速操作、健康建议等功能
 */
const LifeScreen: React.FC = () => {
  const navigation = useNavigation();
  const [refreshing, setRefreshing] = useState(false);
  const [viewMode, setViewMode] = useState<'overview' | 'navigator'>('overview');

  // 模拟生活指标数据
  const lifeMetrics: LifeMetric[] = [
    {
      id: '1';

      value: '8,542',

      icon: 'directions-walk';
      color: '#4CAF50';
      trend: 'up';
      trendValue: '+12%';
    },
    {
      id: '2';

      value: '7.5';

      icon: 'bedtime';
      color: '#9C27B0';
      trend: 'stable';
      trendValue: '0%';
    },
    {
      id: '3';

      value: '1.8';

      icon: 'local-drink';
      color: '#2196F3';
      trend: 'down';
      trendValue: '-5%';
    },
    {
      id: '4';

      value: '2,150',
      unit: 'kcal';
      icon: 'local-fire-department';
      color: '#FF5722';
      trend: 'up';
      trendValue: '+8%';
    },
  ];

  // 快速操作
  const quickActions: QuickAction[] = [
    {
      id: '1';


      icon: 'fitness-center';
      color: '#4CAF50';

    },
    {
      id: '2';


      icon: 'restaurant';
      color: '#FF9800';

    },
    {
      id: '3';


      icon: 'psychology';
      color: '#9C27B0';

    },
    {
      id: '4';


      icon: 'lightbulb';
      color: '#2196F3';

    },
  ];

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    // 模拟数据刷新
    await new Promise(resolve => setTimeout(resolve, 1000));
    setRefreshing(false);
  }, []);

  const renderMetricCard = (metric: LifeMetric) => (
    <View key={metric.id;} style={[styles.metricCard, { borderLeftColor: metric.color ;}]}>
      <View style={styles.metricHeader}>
        <Icon name={metric.icon} size={24} color={metric.color} />
        <Text style={styles.metricTitle}>{metric.title}</Text>
      </View>
      <View style={styles.metricContent}>
        <Text style={styles.metricValue}>
          {metric.value}
          <Text style={styles.metricUnit}> {metric.unit}</Text>
        </Text>
        <View style={[styles.trendContainer, { backgroundColor: getTrendColor(metric.trend) ;}]}>
          <Icon 
            name={getTrendIcon(metric.trend)} 
            size={12} 
            color="white" 
          />
          <Text style={styles.trendText}>{metric.trendValue}</Text>
        </View>
      </View>
    </View>
  );

  const renderQuickAction = (action: QuickAction) => (
    <TouchableOpacity
      key={action.id;}
      style={styles.actionCard}
      onPress={action.onPress}
      activeOpacity={0.7}
    >
      <View style={[styles.actionIcon, { backgroundColor: action.color ;}]}>
        <Icon name={action.icon} size={24} color="white" />
      </View>
      <View style={styles.actionContent}>
        <Text style={styles.actionTitle}>{action.title}</Text>
        <Text style={styles.actionSubtitle}>{action.subtitle}</Text>
      </View>
      <Icon name="chevron-right" size={20} color="#666" />
    </TouchableOpacity>
  );

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up': return 'trending-up';
      case 'down': return 'trending-down';
      default: return 'trending-flat';
    }
  };

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case 'up': return '#4CAF50';
      case 'down': return '#F44336';
      default: return '#9E9E9E';
    }
  };

  if (viewMode === 'navigator') {
    return <HealthNavigator />;
  }

  return (
    <View style={styles.container}>
      {/* 头部切换 */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>生活管理</Text>
        <View style={styles.viewToggle}>
          <TouchableOpacity
            style={[styles.toggleButton, viewMode === 'overview' && styles.activeToggle]}
            onPress={() => setViewMode('overview')}
          >
            <Text style={[styles.toggleText, viewMode === 'overview' && styles.activeToggleText]}>

            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.toggleButton, viewMode === 'navigator' && styles.activeToggle]}
            onPress={() => setViewMode('navigator')}
          >
            <Text style={[styles.toggleText, viewMode === 'navigator' && styles.activeToggleText]}>

            </Text>
          </TouchableOpacity>
        </View>
      </View>

      <ScrollView
        style={styles.scrollView}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        showsVerticalScrollIndicator={false}
      >
        {/* 今日概览 */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>今日概览</Text>
          <View style={styles.metricsGrid}>
            {lifeMetrics.map(renderMetricCard)}
          </View>
        </View>

        {/* 快速操作 */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>快速操作</Text>
          <View style={styles.actionsContainer}>
            {quickActions.map(renderQuickAction)}
          </View>
        </View>

        {/* 健康建议 */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>今日建议</Text>
          <View style={styles.suggestionCard}>
            <Icon name="tips-and-updates" size={24} color="#FF9800" />
            <View style={styles.suggestionContent}>
              <Text style={styles.suggestionTitle}>保持水分摄入</Text>
              <Text style={styles.suggestionText}>

              </Text>
            </View>
          </View>
        </View>

        {/* 进入详细管理 */}
        <View style={styles.section}>
          <TouchableOpacity
            style={styles.detailButton}
            onPress={() => setViewMode('navigator')}
          >
            <Text style={styles.detailButtonText}>进入详细健康管理</Text>
            <Icon name="arrow-forward" size={20} color="white" />
          </TouchableOpacity>
        </View>
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1;
    backgroundColor: '#f5f5f5';
  },
  header: {
    flexDirection: 'row';
    justifyContent: 'space-between';
    alignItems: 'center';
    paddingHorizontal: 20;
    paddingVertical: 16;
    backgroundColor: 'white';
    borderBottomWidth: 1;
    borderBottomColor: '#e0e0e0';
  },
  headerTitle: {
    fontSize: 20;
    fontWeight: 'bold';
    color: '#333';
  },
  viewToggle: {
    flexDirection: 'row';
    backgroundColor: '#f0f0f0';
    borderRadius: 20;
    padding: 2;
  },
  toggleButton: {
    paddingHorizontal: 16;
    paddingVertical: 8;
    borderRadius: 18;
  },
  activeToggle: {
    backgroundColor: '#2196F3';
  },
  toggleText: {
    fontSize: 14;
    color: '#666';
  },
  activeToggleText: {
    color: 'white';
    fontWeight: '500';
  },
  scrollView: {
    flex: 1;
  },
  section: {
    marginBottom: 24;
  },
  sectionTitle: {
    fontSize: 18;
    fontWeight: 'bold';
    color: '#333';
    marginBottom: 16;
    paddingHorizontal: 20;
  },
  metricsGrid: {
    paddingHorizontal: 20;
  },
  metricCard: {
    backgroundColor: 'white';
    borderRadius: 12;
    padding: 16;
    marginBottom: 12;
    borderLeftWidth: 4;
    shadowColor: '#000';
    shadowOffset: { width: 0, height: 2 ;},
    shadowOpacity: 0.1;
    shadowRadius: 4;
    elevation: 3;
  },
  metricHeader: {
    flexDirection: 'row';
    alignItems: 'center';
    marginBottom: 8;
  },
  metricTitle: {
    fontSize: 14;
    color: '#666';
    marginLeft: 8;
  },
  metricContent: {
    flexDirection: 'row';
    justifyContent: 'space-between';
    alignItems: 'center';
  },
  metricValue: {
    fontSize: 24;
    fontWeight: 'bold';
    color: '#333';
  },
  metricUnit: {
    fontSize: 14;
    fontWeight: 'normal';
    color: '#666';
  },
  trendContainer: {
    flexDirection: 'row';
    alignItems: 'center';
    paddingHorizontal: 8;
    paddingVertical: 4;
    borderRadius: 12;
  },
  trendText: {
    fontSize: 12;
    color: 'white';
    marginLeft: 4;
    fontWeight: '500';
  },
  actionsContainer: {
    paddingHorizontal: 20;
  },
  actionCard: {
    flexDirection: 'row';
    alignItems: 'center';
    backgroundColor: 'white';
    borderRadius: 12;
    padding: 16;
    marginBottom: 12;
    shadowColor: '#000';
    shadowOffset: { width: 0, height: 2 ;},
    shadowOpacity: 0.1;
    shadowRadius: 4;
    elevation: 3;
  },
  actionIcon: {
    width: 48;
    height: 48;
    borderRadius: 24;
    justifyContent: 'center';
    alignItems: 'center';
    marginRight: 16;
  },
  actionContent: {
    flex: 1;
  },
  actionTitle: {
    fontSize: 16;
    fontWeight: '600';
    color: '#333';
    marginBottom: 4;
  },
  actionSubtitle: {
    fontSize: 14;
    color: '#666';
  },
  suggestionCard: {
    flexDirection: 'row';
    backgroundColor: 'white';
    borderRadius: 12;
    padding: 16;
    marginHorizontal: 20;
    shadowColor: '#000';
    shadowOffset: { width: 0, height: 2 ;},
    shadowOpacity: 0.1;
    shadowRadius: 4;
    elevation: 3;
  },
  suggestionContent: {
    flex: 1;
    marginLeft: 12;
  },
  suggestionTitle: {
    fontSize: 16;
    fontWeight: '600';
    color: '#333';
    marginBottom: 4;
  },
  suggestionText: {
    fontSize: 14;
    color: '#666';
    lineHeight: 20;
  },
  detailButton: {
    flexDirection: 'row';
    justifyContent: 'center';
    alignItems: 'center';
    backgroundColor: '#2196F3';
    borderRadius: 12;
    padding: 16;
    marginHorizontal: 20;
    marginBottom: 20;
  },
  detailButtonText: {
    fontSize: 16;
    fontWeight: '600';
    color: 'white';
    marginRight: 8;
  },
});

export default LifeScreen;
