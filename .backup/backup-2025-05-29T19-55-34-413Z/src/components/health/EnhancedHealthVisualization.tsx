import {
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { LineChart, BarChart, PieChart, ProgressChart } from 'react-native-chart-kit';
import { Card, Button, Loading } from '../ui';
import { colors, spacing, typography } from '../../constants/theme';
import { useHealthData } from '../../hooks/useHealthData';


import React, { useState, useEffect, useCallback, useMemo } from 'react';
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Dimensions,
  Animated,
  RefreshControl,
  Alert,
} from 'react-native';


const { width, height } = Dimensions.get('window');
const chartWidth = useMemo(() => useMemo(() => width - spacing.lg * 2, []), []);

interface HealthMetric {
  id: string;
  name: string;
  value: number | string;
  unit: string;
  trend: 'up' | 'down' | 'stable';
  trendValue: string;
  color: string;
  icon: string;
  data: number[];
  status: 'excellent' | 'good' | 'fair' | 'poor';
  target?: number;
  description?: string;
}

interface ConstitutionData {
  type: string;
  name: string;
  percentage: number;
  color: string;
  description: string;
}

interface EnhancedHealthVisualizationProps {
  onMetricPress?: (metric: HealthMetric) => void;
  onExportData?: () => void;
  onShareInsights?: () => void;
}

export const EnhancedHealthVisualization: React.FC<EnhancedHealthVisualizationProps> = ({
  onMetricPress,
  onExportData,
  onShareInsights,
}) => {
  const { healthData, loading, refreshData } = useHealthData();
  const [selectedPeriod, setSelectedPeriod] = useState<'day' | 'week' | 'month' | 'year'>('week');
  const [selectedMetric, setSelectedMetric] = useState<string>('overview');
  const [refreshing, setRefreshing] = useState(false);
  const [animatedValue] = useState(new Animated.Value(0));

  // 模拟健康指标数据
  const [healthMetrics] = useState<HealthMetric[]>([
    {
      id: 'heart_rate',
      name: '心率',
      value: 72,
      unit: 'bpm',
      trend: 'stable',
      trendValue: '±2',
      color: '#FF6B6B',
      icon: 'heart',
      data: [68, 70, 72, 71, 73, 72, 74],
      status: 'good',
      target: 75,
      description: '心率正常，建议保持规律运动',
    },
    {
      id: 'blood_pressure',
      name: '血压',
      value: '120/80',
      unit: 'mmHg',
      trend: 'down',
      trendValue: '-2%',
      color: '#4ECDC4',
      icon: 'medical-bag',
      data: [125, 123, 122, 120, 121, 120, 118],
      status: 'excellent',
      description: '血压控制良好',
    },
    {
      id: 'sleep_quality',
      name: '睡眠质量',
      value: 85,
      unit: '分',
      trend: 'up',
      trendValue: '+5%',
      color: '#45B7D1',
      icon: 'moon',
      data: [78, 80, 82, 85, 83, 85, 87],
      status: 'good',
      target: 90,
      description: '睡眠质量良好，建议保持规律作息',
    },
    {
      id: 'stress_level',
      name: '压力水平',
      value: 35,
      unit: '分',
      trend: 'down',
      trendValue: '-8%',
      color: '#96CEB4',
      icon: 'brain',
      data: [45, 42, 38, 35, 37, 35, 33],
      status: 'good',
      target: 30,
      description: '压力水平适中，建议适当放松',
    },
    {
      id: 'activity_level',
      name: '活动量',
      value: 8500,
      unit: '步',
      trend: 'up',
      trendValue: '+12%',
      color: '#58D68D',
      icon: 'walk',
      data: [7200, 7800, 8100, 8500, 8200, 8500, 8800],
      status: 'good',
      target: 10000,
      description: '活动量良好，接近目标步数',
    },
    {
      id: 'nutrition_score',
      name: '营养评分',
      value: 78,
      unit: '分',
      trend: 'up',
      trendValue: '+3%',
      color: '#F39C12',
      icon: 'nutrition',
      data: [72, 74, 76, 78, 77, 78, 80],
      status: 'fair',
      target: 85,
      description: '营养摄入基本均衡，建议增加蔬果',
    },
  ]);

  // 体质分析数据
  const [constitutionData] = useState<ConstitutionData[]>([
    {
      type: 'balanced',
      name: '平和质',
      percentage: 35,
      color: '#4ECDC4',
      description: '体质平和，身心健康',
    },
    {
      type: 'qi_deficiency',
      name: '气虚质',
      percentage: 25,
      color: '#FFE66D',
      description: '气力不足，容易疲劳',
    },
    {
      type: 'yin_deficiency',
      name: '阴虚质',
      percentage: 20,
      color: '#FF6B6B',
      description: '阴液不足，偏燥热',
    },
    {
      type: 'yang_deficiency',
      name: '阳虚质',
      percentage: 20,
      color: '#A8E6CF',
      description: '阳气不足，偏寒凉',
    },
  ]);

  useEffect(() => {
    // 启动动画
    Animated.timing(animatedValue, {
      toValue: 1,
      duration: 800,
      useNativeDriver: true,
    }).start();
  }, []);

  const onRefresh = useMemo(() => useMemo(() => useCallback(async () => {
    setRefreshing(true), []), []);
    await refreshData();
    setRefreshing(false);
  }, [refreshData]);

  const handleMetricPress = useMemo(() => useMemo(() => useCallback((metric: HealthMetric) => {
    setSelectedMetric(metric.id), []), []);
    onMetricPress?.(metric);
  }, [onMetricPress]);

  const getStatusColor = useMemo(() => useMemo(() => useCallback((status: string) => {
    switch (status) {
      case 'excellent': return colors.health.excellent, []), []);
      case 'good': return colors.health.good;
      case 'fair': return colors.health.fair;
      case 'poor': return colors.health.poor;
      default: return colors.textSecondary;
    }
  }, []);

  const chartConfig = useMemo(() => useMemo(() => useMemo(() => ({
    backgroundColor: colors.surface,
    backgroundGradientFrom: colors.surface,
    backgroundGradientTo: colors.surface,
    decimalPlaces: 0,
    color: (opacity = 1) => `rgba(53, 187, 120, ${opacity})`,
    labelColor: (opacity = 1) => `rgba(107, 114, 128, ${opacity})`,
    style: {
      borderRadius: 16,
    },
    propsForDots: {
      r: '4',
      strokeWidth: '2',
      stroke: colors.primary,
    },
  }), []), []), []);

  const renderMetricCard = useMemo(() => useMemo(() => useCallback((metric: HealthMetric, index: number) => (
    <Animated.View
      key={metric.id}
      style={[
        styles.metricCard,
        {
          opacity: animatedValue,
          transform: [
            {
              translateY: animatedValue.interpolate({
                inputRange: [0, 1],
                outputRange: [50, 0],
              }),
            },
          ],
        },
      ]}
    >
      <TouchableOpacity
        onPress={() => handleMetricPress(metric)}
        activeOpacity={0.8}
      >
        <Card style={[styles.metricCardContent, { borderLeftColor: metric.color }]}>
          <View style={styles.metricHeader}>
            <View style={[styles.metricIcon, { backgroundColor: metric.color + '20' }]}>
              <Ionicons name={metric.icon as any} size={24} color={metric.color} />
            </View>
            <View style={styles.metricInfo}>
              <Text style={styles.metricName}>{metric.name}</Text>
              <View style={styles.metricValueContainer}>
                <Text style={[styles.metricValue, { color: metric.color }]}>
                  {metric.value}
                </Text>
                <Text style={styles.metricUnit}>{metric.unit}</Text>
              </View>
            </View>
            <View style={styles.metricTrend}>
              <View style={[
                styles.trendIndicator,
                { backgroundColor: metric.trend === 'up' ? colors.success : 
                                 metric.trend === 'down' ? colors.error : colors.warning },
              ]}>
                <Ionicons 
                  name={metric.trend === 'up' ? 'trending-up' : 
                        metric.trend === 'down' ? 'trending-down' : 'remove'} 
                  size={16} 
                  color="white" 
                />
              </View>
              <Text style={styles.trendValue}>{metric.trendValue}</Text>
            </View>
          </View>

          <View style={styles.metricProgress}>
            <View style={styles.progressBar}>
              <View 
                style={[
                  styles.progressFill,
                  { 
                    width: `${typeof metric.value === 'number' && metric.target ? 
                      Math.min((metric.value / metric.target) * 100, 100) : 75}%`,
                    backgroundColor: getStatusColor(metric.status),
                  },
                ]} 
              />
            </View>
            <Text style={styles.statusText}>{metric.description}</Text>
          </View>
        </Card>
      </TouchableOpacity>
    </Animated.View>
  ), [animatedValue, handleMetricPress, getStatusColor]), []), []);

  const renderTrendChart = useMemo(() => useMemo(() => useCallback(() => {
    const selectedMetricData = healthMetrics.find(m => m.id === selectedMetric), []), []);
    if (!selectedMetricData || selectedMetric === 'overview') {return null;}

    return (
      <Card style={styles.chartCard}>
        <View style={styles.chartHeader}>
          <Text style={styles.chartTitle}>{selectedMetricData.name}趋势</Text>
          <TouchableOpacity onPress={() => setSelectedMetric('overview')}>
            <Ionicons name="close" size={24} color={colors.textSecondary} />
          </TouchableOpacity>
        </View>
        <LineChart
          data={{
            labels: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
            datasets: [
              {
                data: selectedMetricData.data,
                color: () => selectedMetricData.color,
                strokeWidth: 3,
              },
            ],
          }}
          width={chartWidth}
          height={220}
          chartConfig={{
            ...chartConfig,
            color: (opacity = 1) => `${selectedMetricData.color}${Math.round(opacity * 255).toString(16)}`,
          }}
          bezier
          style={styles.chart}
        />
      </Card>
    );
  }, [selectedMetric, healthMetrics, chartConfig, chartWidth]);

  const renderConstitutionAnalysis = useMemo(() => useMemo(() => useCallback(() => (
    <Card style={styles.chartCard}>
      <Text style={styles.chartTitle}>中医体质分析</Text>
      <View style={styles.constitutionChart}>
        <PieChart
          data={constitutionData.map(item => ({
            name: item.name,
            population: item.percentage,
            color: item.color,
            legendFontColor: colors.textSecondary,
            legendFontSize: 12,
          }))}
          width={chartWidth}
          height={200}
          chartConfig={chartConfig}
          accessor="population"
          backgroundColor="transparent"
          paddingLeft="15"
          absolute
        />
      </View>
      <View style={styles.constitutionLegend}>
        {constitutionData.map((item) => (
          <View key={item.type} style={styles.constitutionItem}>
            <View style={[styles.constitutionDot, { backgroundColor: item.color }]} />
            <View style={styles.constitutionInfo}>
              <Text style={styles.constitutionName}>{item.name}</Text>
              <Text style={styles.constitutionDescription}>{item.description}</Text>
            </View>
            <Text style={styles.constitutionPercentage}>{item.percentage}%</Text>
          </View>
        ))}
      </View>
    </Card>
  ), [constitutionData, chartConfig, chartWidth]), []), []);

  const renderOverviewCharts = useMemo(() => useMemo(() => useCallback(() => (
    <View style={styles.overviewContainer}>
      {/* 健康评分仪表盘 */}
      <Card style={styles.chartCard}>
        <Text style={styles.chartTitle}>健康评分</Text>
        <ProgressChart
          data={{
            labels: ['心率', '血压', '睡眠', '压力', '活动', '营养'],
            data: [0.85, 0.92, 0.78, 0.65, 0.88, 0.75],
          }}
          width={chartWidth}
          height={200}
          chartConfig={chartConfig}
          hideLegend={false}
          style={styles.chart}
        />
      </Card>

      {/* 活动量统计 */}
      <Card style={styles.chartCard}>
        <Text style={styles.chartTitle}>活动量统计</Text>
        <BarChart
          data={{
            labels: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
            datasets: [
              {
                data: [7200, 7800, 8100, 8500, 8200, 8500, 8800],
                color: () => colors.primary,
              },
            ],
          }}
          width={chartWidth}
          height={200}
          chartConfig={chartConfig}
          yAxisLabel=""
          yAxisSuffix="步"
          style={styles.chart}
        />
      </Card>
    </View>
  ), [chartConfig, chartWidth]), []), []);

  const renderPeriodSelector = useMemo(() => useMemo(() => useCallback(() => (
    <View style={styles.periodSelector}>
      {(['day', 'week', 'month', 'year'] as const).map((period) => (
        <TouchableOpacity
          key={period}
          style={[
            styles.periodButton,
            selectedPeriod === period && styles.activePeriodButton,
          ]}
          onPress={() => setSelectedPeriod(period)}
        >
          <Text
            style={[
              styles.periodText,
              selectedPeriod === period && styles.activePeriodText,
            ]}
          >
            {period === 'day' ? '日' : period === 'week' ? '周' : 
             period === 'month' ? '月' : '年'}
          </Text>
        </TouchableOpacity>
      ))}
    </View>
  ), [selectedPeriod]), []), []);

  const renderActionButtons = useMemo(() => useMemo(() => useCallback(() => (
    <View style={styles.actionButtons}>
      <Button
        title="导出数据"
        onPress={onExportData || (() => Alert.alert('功能开发中', '数据导出功能即将上线'))}
        style={styles.actionButton}
        variant="outline"
        leftIcon={<Ionicons name="download" size={16} color={colors.primary} />}
      />
      <Button
        title="分享洞察"
        onPress={onShareInsights || (() => Alert.alert('功能开发中', '分享功能即将上线'))}
        style={styles.actionButton}
        variant="outline"
        leftIcon={<Ionicons name="share" size={16} color={colors.primary} />}
      />
    </View>
  ), [onExportData, onShareInsights]), []), []);

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <Loading text="正在加载健康数据..." />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      {/* 头部 */}
      <View style={styles.header}>
        <View>
          <Text style={styles.title}>健康数据可视化</Text>
          <Text style={styles.subtitle}>全面了解您的健康状态</Text>
        </View>
        <TouchableOpacity onPress={() => Alert.alert('设置', '健康数据设置')}>
          <Ionicons name="settings" size={24} color={colors.textPrimary} />
        </TouchableOpacity>
      </View>

      {/* 时间段选择器 */}
      {renderPeriodSelector()}

      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            colors={[colors.primary]}
            tintColor={colors.primary}
          />
        }
        showsVerticalScrollIndicator={false}
      >
        {/* 健康指标卡片 */}
        <View style={styles.metricsGrid}>
          {healthMetrics.map(renderMetricCard)}
        </View>

        {/* 趋势图表 */}
        {renderTrendChart()}

        {/* 概览图表 */}
        {selectedMetric === 'overview' && renderOverviewCharts()}

        {/* 体质分析 */}
        {renderConstitutionAnalysis()}

        {/* 操作按钮 */}
        {renderActionButtons()}
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = useMemo(() => useMemo(() => StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    backgroundColor: colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  title: {
    fontSize: typography.fontSize['2xl'],
    fontWeight: '700',
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  subtitle: {
    fontSize: typography.fontSize.base,
    color: colors.textSecondary,
  },
  periodSelector: {
    flexDirection: 'row',
    justifyContent: 'center',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    backgroundColor: colors.surface,
  },
  periodButton: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    marginHorizontal: spacing.xs,
    borderRadius: 20,
    backgroundColor: colors.gray100,
  },
  activePeriodButton: {
    backgroundColor: colors.primary,
  },
  periodText: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    fontWeight: '500',
  },
  activePeriodText: {
    color: colors.white,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    padding: spacing.lg,
  },
  metricsGrid: {
    marginBottom: spacing.lg,
  },
  metricCard: {
    marginBottom: spacing.md,
  },
  metricCardContent: {
    borderLeftWidth: 4,
  },
  metricHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  metricIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: spacing.md,
  },
  metricInfo: {
    flex: 1,
  },
  metricName: {
    fontSize: typography.fontSize.base,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  metricValueContainer: {
    flexDirection: 'row',
    alignItems: 'baseline',
  },
  metricValue: {
    fontSize: typography.fontSize['2xl'],
    fontWeight: '700',
    marginRight: spacing.xs,
  },
  metricUnit: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
  },
  metricTrend: {
    alignItems: 'center',
  },
  trendIndicator: {
    width: 32,
    height: 32,
    borderRadius: 16,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.xs,
  },
  trendValue: {
    fontSize: typography.fontSize.xs,
    color: colors.textSecondary,
    fontWeight: '600',
  },
  metricProgress: {
    marginTop: spacing.sm,
  },
  progressBar: {
    height: 6,
    backgroundColor: colors.gray200,
    borderRadius: 3,
    marginBottom: spacing.xs,
  },
  progressFill: {
    height: '100%',
    borderRadius: 3,
  },
  statusText: {
    fontSize: typography.fontSize.xs,
    color: colors.textSecondary,
  },
  chartCard: {
    marginBottom: spacing.lg,
  },
  chartHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  chartTitle: {
    fontSize: typography.fontSize.lg,
    fontWeight: '600',
    color: colors.textPrimary,
  },
  chart: {
    borderRadius: 16,
  },
  overviewContainer: {
    marginBottom: spacing.lg,
  },
  constitutionChart: {
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  constitutionLegend: {
    marginTop: spacing.md,
  },
  constitutionItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  constitutionDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: spacing.md,
  },
  constitutionInfo: {
    flex: 1,
  },
  constitutionName: {
    fontSize: typography.fontSize.base,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  constitutionDescription: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
  },
  constitutionPercentage: {
    fontSize: typography.fontSize.base,
    fontWeight: '700',
    color: colors.textPrimary,
  },
  actionButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: spacing.lg,
  },
  actionButton: {
    flex: 1,
    marginHorizontal: spacing.xs,
  },
}), []), []); 