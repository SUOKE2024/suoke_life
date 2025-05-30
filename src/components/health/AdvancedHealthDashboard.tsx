import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { LineChart, BarChart, PieChart, ProgressChart } from 'react-native-chart-kit';
import { Card, Button, Loading } from '../ui';
import { colors, spacing, typography } from '../../constants/theme';
import { useAppSelector, useAppDispatch } from '../../store';


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
  Platform,
} from 'react-native';

const { width, height } = Dimensions.get('window');
const chartWidth = useMemo(() => useMemo(() => useMemo(() => width - spacing.lg * 2, []), []), []);

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
  status: 'excellent' | 'good' | 'fair' | 'poor' | 'critical';
  target?: number;
  description?: string;
  aiInsight?: string;
  prediction?: {
    nextWeek: number;
    confidence: number;
    recommendation: string;
  };
}

interface HealthAlert {
  id: string;
  type: 'warning' | 'info' | 'success' | 'error';
  title: string;
  message: string;
  timestamp: Date;
  priority: 'high' | 'medium' | 'low';
  actionRequired: boolean;
}

interface AIInsight {
  id: string;
  category: 'nutrition' | 'exercise' | 'sleep' | 'stress' | 'general';
  title: string;
  content: string;
  confidence: number;
  recommendations: string[];
  timestamp: Date;
}

interface AdvancedHealthDashboardProps {
  onMetricPress?: (metric: HealthMetric) => void;
  onAlertPress?: (alert: HealthAlert) => void;
  onInsightPress?: (insight: AIInsight) => void;
  onExportData?: () => void;
  onShareInsights?: () => void;
}

export const AdvancedHealthDashboard: React.FC<AdvancedHealthDashboardProps> = ({
  onMetricPress,
  onAlertPress,
  onInsightPress,
  onExportData,
  onShareInsights,
}) => {
  const dispatch = useMemo(() => useMemo(() => useMemo(() => useAppDispatch(), []), []), []);
  const { data: healthData, loading } = useAppSelector(state => state.health);
  const { profile: user } = useAppSelector(state => state.user);
  
  const [selectedPeriod, setSelectedPeriod] = useState<'day' | 'week' | 'month' | 'year'>('week');
  const [selectedView, setSelectedView] = useState<'overview' | 'detailed' | 'trends' | 'insights'>('overview');
  const [refreshing, setRefreshing] = useState(false);
  const [animatedValue] = useState(new Animated.Value(0));
  const [pulseAnimation] = useState(new Animated.Value(1));

  // 高级健康指标数据
  const [healthMetrics] = useState<HealthMetric[]>([
    {
      id: 'heart_rate_variability',
      name: '心率变异性',
      value: 45,
      unit: 'ms',
      trend: 'up',
      trendValue: '+8%',
      color: '#FF6B6B',
      icon: 'heart-circle',
      data: [38, 40, 42, 45, 43, 45, 47],
      status: 'good',
      target: 50,
      description: '心率变异性良好，自主神经功能正常',
      aiInsight: '您的心率变异性呈上升趋势，表明心血管健康状况正在改善',
      prediction: {
        nextWeek: 48,
        confidence: 85,
        recommendation: '继续保持规律运动，预计下周将达到更优水平',
      },
    },
    {
      id: 'metabolic_age',
      name: '代谢年龄',
      value: 28,
      unit: '岁',
      trend: 'down',
      trendValue: '-2岁',
      color: '#4ECDC4',
      icon: 'flame',
      data: [32, 31, 30, 28, 29, 28, 27],
      status: 'excellent',
      description: '代谢年龄低于实际年龄，代谢功能优秀',
      aiInsight: '您的代谢年龄持续下降，说明生活方式调整效果显著',
      prediction: {
        nextWeek: 27,
        confidence: 78,
        recommendation: '保持当前饮食和运动习惯，代谢年龄有望继续改善',
      },
    },
    {
      id: 'stress_resilience',
      name: '压力恢复力',
      value: 78,
      unit: '分',
      trend: 'up',
      trendValue: '+12%',
      color: '#96CEB4',
      icon: 'shield-checkmark',
      data: [65, 68, 72, 78, 75, 78, 82],
      status: 'good',
      target: 85,
      description: '压力恢复能力良好，心理韧性较强',
      aiInsight: '您的压力恢复能力显著提升，冥想练习效果明显',
      prediction: {
        nextWeek: 82,
        confidence: 82,
        recommendation: '继续进行正念练习，压力管理能力将进一步提升',
      },
    },
    {
      id: 'inflammation_index',
      name: '炎症指数',
      value: 2.1,
      unit: 'mg/L',
      trend: 'down',
      trendValue: '-15%',
      color: '#58D68D',
      icon: 'medical',
      data: [2.8, 2.6, 2.4, 2.1, 2.3, 2.1, 1.9],
      status: 'good',
      target: 1.5,
      description: '炎症水平控制良好，免疫系统平衡',
      aiInsight: '炎症指数持续下降，抗炎饮食策略效果显著',
      prediction: {
        nextWeek: 1.9,
        confidence: 88,
        recommendation: '继续摄入富含Omega-3的食物，炎症水平将进一步改善',
      },
    },
    {
      id: 'cognitive_performance',
      name: '认知表现',
      value: 92,
      unit: '分',
      trend: 'stable',
      trendValue: '±1%',
      color: '#F39C12',
      icon: 'brain',
      data: [88, 90, 91, 92, 91, 92, 93],
      status: 'excellent',
      target: 95,
      description: '认知功能优秀，注意力和记忆力良好',
      aiInsight: '认知表现保持稳定高水平，大脑健康状况良好',
      prediction: {
        nextWeek: 93,
        confidence: 75,
        recommendation: '增加阅读和学习新技能，有助于进一步提升认知能力',
      },
    },
    {
      id: 'energy_efficiency',
      name: '能量效率',
      value: 85,
      unit: '%',
      trend: 'up',
      trendValue: '+7%',
      color: '#E74C3C',
      icon: 'battery-charging',
      data: [75, 78, 82, 85, 83, 85, 88],
      status: 'good',
      target: 90,
      description: '能量利用效率良好，疲劳感减少',
      aiInsight: '能量效率提升明显，线粒体功能改善',
      prediction: {
        nextWeek: 88,
        confidence: 80,
        recommendation: '适当增加有氧运动，能量效率将持续提升',
      },
    },
  ]);

  // 健康警报数据
  const [healthAlerts] = useState<HealthAlert[]>([
    {
      id: 'alert_1',
      type: 'warning',
      title: '睡眠质量下降',
      message: '过去3天睡眠质量评分低于平均水平，建议调整作息时间',
      timestamp: new Date(),
      priority: 'medium',
      actionRequired: true,
    },
    {
      id: 'alert_2',
      type: 'info',
      title: '运动目标达成',
      message: '恭喜！本周运动目标已完成，保持良好习惯',
      timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
      priority: 'low',
      actionRequired: false,
    },
    {
      id: 'alert_3',
      type: 'success',
      title: '体重管理良好',
      message: '体重保持在健康范围内，营养计划执行效果良好',
      timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000),
      priority: 'low',
      actionRequired: false,
    },
  ]);

  // AI洞察数据
  const [aiInsights] = useState<AIInsight[]>([
    {
      id: 'insight_1',
      category: 'nutrition',
      title: '营养摄入优化建议',
      content: '基于您的代谢数据分析，建议增加蛋白质摄入量至每日1.2g/kg体重',
      confidence: 92,
      recommendations: [
        '早餐增加鸡蛋或希腊酸奶',
        '午餐选择瘦肉或豆类',
        '晚餐适量鱼类或坚果',
      ],
      timestamp: new Date(),
    },
    {
      id: 'insight_2',
      category: 'exercise',
      title: '运动强度调整',
      content: '您的心率变异性数据显示可以适当增加高强度间歇训练',
      confidence: 88,
      recommendations: [
        '每周增加1-2次HIIT训练',
        '单次训练时间控制在20-30分钟',
        '注意训练后的恢复监测',
      ],
      timestamp: new Date(Date.now() - 1 * 60 * 60 * 1000),
    },
    {
      id: 'insight_3',
      category: 'sleep',
      title: '睡眠优化策略',
      content: '睡眠数据分析显示您的深度睡眠比例可以进一步提升',
      confidence: 85,
      recommendations: [
        '睡前1小时避免蓝光暴露',
        '保持卧室温度在18-20°C',
        '尝试睡前冥想或深呼吸练习',
      ],
      timestamp: new Date(Date.now() - 3 * 60 * 60 * 1000),
    },
  ]);

  useEffect(() => {
    // 启动入场动画
    Animated.timing(animatedValue, {
      toValue: 1,
      duration: 1000,
      useNativeDriver: true,
    }).start();

    // 启动脉冲动画
    const pulseAnimationLoop = useMemo(() => useMemo(() => useMemo(() => useCallback( () => {, []), []), []), []);
      Animated.sequence([
        Animated.timing(pulseAnimation, {
          toValue: 1.1,
          duration: 1000,
          useNativeDriver: true,
        }),
        Animated.timing(pulseAnimation, {
          toValue: 1,
          duration: 1000,
          useNativeDriver: true,
        }),
      ]).start(() => pulseAnimationLoop());
    };
    pulseAnimationLoop();
  }, []);

  const onRefresh = useMemo(() => useMemo(() => useMemo(() => useCallback(async () => {
    setRefreshing(true), []), []), []);
    // 模拟数据刷新
    await new Promise<void>(resolve => setTimeout(() => resolve(), 1500));
    setRefreshing(false);
  }, []);

  const handleMetricPress = useMemo(() => useMemo(() => useMemo(() => useCallback((metric: HealthMetric) => {
    onMetricPress?.(metric), []), []), []);
  }, [onMetricPress]);

  const handleAlertPress = useMemo(() => useMemo(() => useMemo(() => useCallback((alert: HealthAlert) => {
    onAlertPress?.(alert), []), []), []);
  }, [onAlertPress]);

  const handleInsightPress = useMemo(() => useMemo(() => useMemo(() => useCallback((insight: AIInsight) => {
    onInsightPress?.(insight), []), []), []);
  }, [onInsightPress]);

  const getStatusColor = useMemo(() => useMemo(() => useMemo(() => useCallback( (status: string) => {, []), []), []), []);
    switch (status) {
      case 'excellent': return colors.success;
      case 'good': return colors.primary;
      case 'fair': return colors.warning;
      case 'poor': return colors.error;
      case 'critical': return colors.error;
      default: return colors.textSecondary;
    }
  };

  const getAlertColor = useMemo(() => useMemo(() => useMemo(() => useCallback( (type: string) => {, []), []), []), []);
    switch (type) {
      case 'warning': return colors.warning;
      case 'info': return colors.info;
      case 'success': return colors.success;
      case 'error': return colors.error;
      default: return colors.textSecondary;
    }
  };

  // TODO: 将内联组件移到组件外部
const renderPeriodSelector = useMemo(() => useMemo(() => useMemo(() => () => (
    <View style={styles.periodSelector}>
      {(['day', 'week', 'month', 'year'] as const).map((period) => (
        <TouchableOpacity
          key={period}
          style={[
            styles.periodButton,
            selectedPeriod === period && styles.periodButtonActive,
          ]}
          onPress={() => setSelectedPeriod(period)}
        >
          <Text
            style={[
              styles.periodButtonText,
              selectedPeriod === period && styles.periodButtonTextActive,
            ]}
          >
            {period === 'day' ? '日' : period === 'week' ? '周' : period === 'month' ? '月' : '年'}
          </Text>
        </TouchableOpacity>
      ))}
    </View>
  ), []), []), []);

  // TODO: 将内联组件移到组件外部
const renderViewSelector = useMemo(() => useMemo(() => useMemo(() => () => (
    <View style={styles.viewSelector}>
      {(['overview', 'detailed', 'trends', 'insights'] as const).map((view) => (
        <TouchableOpacity
          key={view}
          style={[
            styles.viewButton,
            selectedView === view && styles.viewButtonActive,
          ]}
          onPress={() => setSelectedView(view)}
        >
          <Ionicons
            name={
              view === 'overview' ? 'grid' :
              view === 'detailed' ? 'list' :
              view === 'trends' ? 'trending-up' : 'bulb'
            }
            size={20}
            color={selectedView === view ? colors.white : colors.textSecondary}
          />
          <Text
            style={[
              styles.viewButtonText,
              selectedView === view && styles.viewButtonTextActive,
            ]}
          >
            {view === 'overview' ? '概览' :
             view === 'detailed' ? '详细' :
             view === 'trends' ? '趋势' : '洞察'}
          </Text>
        </TouchableOpacity>
      ))}
    </View>
  ), []), []), []);

  const renderHealthScore = useMemo(() => useMemo(() => useMemo(() => useCallback( () => {, []), []), []), []);
    const overallScore = useMemo(() => useMemo(() => useMemo(() => Math.round(
      healthMetrics.reduce((sum, metric) => {
        if (typeof metric.value === 'number') {
          return sum + (metric.value / (metric.target || 100)) * 100, []), []), []);
        }
        return sum + 75; // 默认分数
      }, 0) / healthMetrics.length
    );

    return (
      <Animated.View
        style={[
          styles.healthScoreCard,
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
        <View style={styles.blurContainer}>
          <View style={styles.scoreContainer}>
            <Animated.View
              style={[
                styles.scoreCircle,
                { transform: [{ scale: pulseAnimation }] },
              ]}
            >
              <Text style={styles.scoreValue}>{overallScore}</Text>
              <Text style={styles.scoreLabel}>健康评分</Text>
            </Animated.View>
            <View style={styles.scoreDetails}>
              <Text style={styles.scoreTitle}>整体健康状况</Text>
              <Text style={styles.scoreDescription}>
                {overallScore >= 90 ? '优秀' :
                 overallScore >= 80 ? '良好' :
                 overallScore >= 70 ? '一般' : '需要改善'}
              </Text>
              <View style={styles.scoreProgress}>
                <View
                  style={[
                    styles.scoreProgressBar,
                    { width: `${overallScore}%` },
                  ]}
                />
              </View>
            </View>
          </View>
        </View>
      </Animated.View>
    );
  };

  const renderMetricCard = useMemo(() => useMemo(() => useMemo(() => (metric: HealthMetric, index: number) => (
    <Animated.View
      key={metric.id}
      style={[
        styles.metricCard,
        {
          opacity: animatedValue,
          transform: [
            {
              translateX: animatedValue.interpolate({
                inputRange: [0, 1],
                outputRange: [100, 0],
              }),
            },
          ],
        },
      ]}
    >
      <TouchableOpacity
        style={styles.metricCardContent}
        onPress={() => handleMetricPress(metric)}
        activeOpacity={0.8}
      >
        <View style={styles.metricHeader}>
          <View style={[styles.metricIcon, { backgroundColor: metric.color + '20' }]}>
            <Ionicons name={metric.icon as any} size={24} color={metric.color} />
          </View>
          <View style={styles.metricInfo}>
            <Text style={styles.metricName}>{metric.name}</Text>
            <View style={styles.metricValueContainer}>
              <Text style={styles.metricValue}>
                {metric.value} {metric.unit}
              </Text>
              <View style={[styles.trendIndicator, { backgroundColor: getStatusColor(metric.status) }]}>
                <Ionicons
                  name={
                    metric.trend === 'up' ? 'trending-up' :
                    metric.trend === 'down' ? 'trending-down' : 'remove'
                  }
                  size={12}
                  color={colors.white}
                />
                <Text style={styles.trendValue}>{metric.trendValue}</Text>
              </View>
            </View>
          </View>
        </View>
        
        {selectedView === 'detailed' && (
          <View style={styles.metricDetails}>
            <Text style={styles.metricDescription}>{metric.description}</Text>
            {metric.aiInsight && (
              <View style={styles.aiInsightContainer}>
                <Ionicons name="bulb" size={16} color={colors.primary} />
                <Text style={styles.aiInsightText}>{metric.aiInsight}</Text>
              </View>
            )}
            {metric.prediction && (
              <View style={styles.predictionContainer}>
                <Text style={styles.predictionTitle}>预测分析</Text>
                <Text style={styles.predictionText}>
                  下周预测值: {metric.prediction.nextWeek} {metric.unit}
                </Text>
                <Text style={styles.predictionConfidence}>
                  置信度: {metric.prediction.confidence}%
                </Text>
                <Text style={styles.predictionRecommendation}>
                  {metric.prediction.recommendation}
                </Text>
              </View>
            )}
          </View>
        )}

        {selectedView === 'trends' && (
          <View style={styles.chartContainer}>
            <LineChart
              data={{
                labels: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
                datasets: [{
                  data: metric.data,
                  color: () => metric.color,
                  strokeWidth: 2,
                }],
              }}
              width={chartWidth - 40}
              height={120}
              chartConfig={{
                backgroundColor: 'transparent',
                backgroundGradientFrom: 'transparent',
                backgroundGradientTo: 'transparent',
                decimalPlaces: 0,
                color: (opacity = 1) => `rgba(255, 255, 255, ${opacity})`,
                labelColor: (opacity = 1) => `rgba(255, 255, 255, ${opacity * 0.7})`,
                style: {
                  borderRadius: 16,
                },
                propsForDots: {
                  r: '4',
                  strokeWidth: '2',
                  stroke: metric.color,
                },
              }}
              bezier
              style={styles.chart}
            />
          </View>
        )}
      </TouchableOpacity>
    </Animated.View>
  ), []), []), []);

  // TODO: 将内联组件移到组件外部
const renderAlerts = useMemo(() => useMemo(() => useMemo(() => () => (
    <View style={styles.alertsSection}>
      <Text style={styles.sectionTitle}>健康提醒</Text>
      {healthAlerts.map((alert, index) => (
        <TouchableOpacity
          key={alert.id}
          style={[styles.alertCard, { borderLeftColor: getAlertColor(alert.type) }]}
          onPress={() => handleAlertPress(alert)}
        >
          <View style={styles.alertHeader}>
            <Ionicons
              name={
                alert.type === 'warning' ? 'warning' :
                alert.type === 'info' ? 'information-circle' :
                alert.type === 'success' ? 'checkmark-circle' : 'close-circle'
              }
              size={20}
              color={getAlertColor(alert.type)}
            />
            <Text style={styles.alertTitle}>{alert.title}</Text>
            <Text style={styles.alertTime}>
              {alert.timestamp.toLocaleTimeString('zh-CN', { 
                hour: '2-digit', 
                minute: '2-digit', 
              })}
            </Text>
          </View>
          <Text style={styles.alertMessage}>{alert.message}</Text>
          {alert.actionRequired && (
            <View style={styles.alertAction}>
              <Text style={styles.actionRequiredText}>需要处理</Text>
            </View>
          )}
        </TouchableOpacity>
      ))}
    </View>
  ), []), []), []);

  // TODO: 将内联组件移到组件外部
const renderInsights = useMemo(() => useMemo(() => useMemo(() => () => (
    <View style={styles.insightsSection}>
      <Text style={styles.sectionTitle}>AI 健康洞察</Text>
      {aiInsights.map((insight, index) => (
        <TouchableOpacity
          key={insight.id}
          style={styles.insightCard}
          onPress={() => handleInsightPress(insight)}
        >
          <View style={styles.insightHeader}>
            <View style={styles.insightCategory}>
              <Ionicons
                name={
                  insight.category === 'nutrition' ? 'nutrition' :
                  insight.category === 'exercise' ? 'fitness' :
                  insight.category === 'sleep' ? 'moon' :
                  insight.category === 'stress' ? 'shield' : 'bulb'
                }
                size={16}
                color={colors.primary}
              />
              <Text style={styles.insightCategoryText}>
                {insight.category === 'nutrition' ? '营养' :
                 insight.category === 'exercise' ? '运动' :
                 insight.category === 'sleep' ? '睡眠' :
                 insight.category === 'stress' ? '压力' : '综合'}
              </Text>
            </View>
            <View style={styles.confidenceIndicator}>
              <Text style={styles.confidenceText}>{insight.confidence}%</Text>
            </View>
          </View>
          <Text style={styles.insightTitle}>{insight.title}</Text>
          <Text style={styles.insightContent}>{insight.content}</Text>
          <View style={styles.recommendationsContainer}>
            {insight.recommendations.map((rec, recIndex) => (
              <View key={recIndex} style={styles.recommendationItem}>
                <Ionicons name="checkmark" size={14} color={colors.success} />
                <Text style={styles.recommendationText}>{rec}</Text>
              </View>
            ))}
          </View>
        </TouchableOpacity>
      ))}
    </View>
  ), []), []), []);

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <Loading />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            tintColor={colors.primary}
            colors={[colors.primary]}
          />
        }
        showsVerticalScrollIndicator={false}
      >
        {/* 头部控制区域 */}
        <View style={styles.header}>
          <Text style={styles.title}>高级健康仪表板</Text>
          <View style={styles.headerControls}>
            <TouchableOpacity
              style={styles.exportButton}
              onPress={onExportData}
            >
              <Ionicons name="download" size={20} color={colors.primary} />
            </TouchableOpacity>
            <TouchableOpacity
              style={styles.shareButton}
              onPress={onShareInsights}
            >
              <Ionicons name="share" size={20} color={colors.primary} />
            </TouchableOpacity>
          </View>
        </View>

        {/* 时间周期选择器 */}
        {renderPeriodSelector()}

        {/* 视图选择器 */}
        {renderViewSelector()}

        {/* 健康评分卡片 */}
        {renderHealthScore()}

        {/* 健康指标网格 */}
        <View style={styles.metricsGrid}>
          {healthMetrics.map((metric, index) => renderMetricCard(metric, index))}
        </View>

        {/* 健康提醒 */}
        {selectedView === 'overview' && renderAlerts()}

        {/* AI洞察 */}
        {selectedView === 'insights' && renderInsights()}
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = useMemo(() => useMemo(() => useMemo(() => StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  scrollView: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
  },
  title: {
    fontSize: typography.fontSize['2xl'],
    color: colors.textPrimary,
    fontWeight: '700',
  },
  headerControls: {
    flexDirection: 'row',
    gap: spacing.sm,
  },
  exportButton: {
    padding: spacing.sm,
    borderRadius: 8,
    backgroundColor: colors.surfaceSecondary,
  },
  shareButton: {
    padding: spacing.sm,
    borderRadius: 8,
    backgroundColor: colors.surfaceSecondary,
  },
  periodSelector: {
    flexDirection: 'row',
    marginHorizontal: spacing.lg,
    marginBottom: spacing.md,
    backgroundColor: colors.surfaceSecondary,
    borderRadius: 12,
    padding: spacing.xs,
  },
  periodButton: {
    flex: 1,
    paddingVertical: spacing.sm,
    alignItems: 'center',
    borderRadius: 8,
  },
  periodButtonActive: {
    backgroundColor: colors.primary,
  },
  periodButtonText: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    fontWeight: '500',
  },
  periodButtonTextActive: {
    color: colors.white,
    fontWeight: '600',
  },
  viewSelector: {
    flexDirection: 'row',
    marginHorizontal: spacing.lg,
    marginBottom: spacing.lg,
    backgroundColor: colors.surfaceSecondary,
    borderRadius: 12,
    padding: spacing.xs,
  },
  viewButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: spacing.sm,
    borderRadius: 8,
    gap: spacing.xs,
  },
  viewButtonActive: {
    backgroundColor: colors.primary,
  },
  viewButtonText: {
    fontSize: typography.fontSize.xs,
    color: colors.textSecondary,
    fontWeight: '500',
  },
  viewButtonTextActive: {
    color: colors.white,
    fontWeight: '600',
  },
  healthScoreCard: {
    marginHorizontal: spacing.lg,
    marginBottom: spacing.lg,
    borderRadius: 20,
    overflow: 'hidden',
    backgroundColor: colors.surface,
  },
  blurContainer: {
    padding: spacing.lg,
  },
  scoreContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  scoreCircle: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.lg,
  },
  scoreValue: {
    fontSize: typography.fontSize['3xl'],
    color: colors.white,
    fontWeight: '700',
  },
  scoreLabel: {
    fontSize: typography.fontSize.xs,
    color: colors.white,
    opacity: 0.8,
  },
  scoreDetails: {
    flex: 1,
  },
  scoreTitle: {
    fontSize: typography.fontSize.lg,
    color: colors.textPrimary,
    fontWeight: '600',
    marginBottom: spacing.xs,
  },
  scoreDescription: {
    fontSize: typography.fontSize.base,
    color: colors.textSecondary,
    marginBottom: spacing.sm,
  },
  scoreProgress: {
    height: 8,
    backgroundColor: colors.gray200,
    borderRadius: 4,
    overflow: 'hidden',
  },
  scoreProgressBar: {
    height: '100%',
    backgroundColor: colors.primary,
    borderRadius: 4,
  },
  metricsGrid: {
    paddingHorizontal: spacing.lg,
  },
  metricCard: {
    marginBottom: spacing.md,
    borderRadius: 16,
    backgroundColor: colors.surfaceSecondary,
    overflow: 'hidden',
  },
  metricCardContent: {
    padding: spacing.lg,
  },
  metricHeader: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  metricIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.md,
  },
  metricInfo: {
    flex: 1,
  },
  metricName: {
    fontSize: typography.fontSize.base,
    color: colors.textPrimary,
    fontWeight: '600',
    marginBottom: spacing.xs,
  },
  metricValueContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  metricValue: {
    fontSize: typography.fontSize.lg,
    color: colors.textPrimary,
    fontWeight: '700',
  },
  trendIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: 12,
    gap: spacing.xs,
  },
  trendValue: {
    fontSize: typography.fontSize.xs,
    color: colors.white,
    fontWeight: '600',
  },
  metricDetails: {
    marginTop: spacing.md,
    paddingTop: spacing.md,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  metricDescription: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    marginBottom: spacing.sm,
  },
  aiInsightContainer: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    backgroundColor: colors.primary + '10',
    padding: spacing.sm,
    borderRadius: 8,
    marginBottom: spacing.sm,
    gap: spacing.xs,
  },
  aiInsightText: {
    fontSize: typography.fontSize.sm,
    color: colors.primary,
    flex: 1,
  },
  predictionContainer: {
    backgroundColor: colors.gray100,
    padding: spacing.sm,
    borderRadius: 8,
  },
  predictionTitle: {
    fontSize: typography.fontSize.sm,
    color: colors.textPrimary,
    fontWeight: '600',
    marginBottom: spacing.xs,
  },
  predictionText: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
  },
  predictionConfidence: {
    fontSize: typography.fontSize.xs,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
  },
  predictionRecommendation: {
    fontSize: typography.fontSize.sm,
    color: colors.primary,
    fontStyle: 'italic',
  },
  chartContainer: {
    marginTop: spacing.md,
    alignItems: 'center',
  },
  chart: {
    borderRadius: 16,
  },
  alertsSection: {
    paddingHorizontal: spacing.lg,
    marginTop: spacing.lg,
  },
  sectionTitle: {
    fontSize: typography.fontSize.lg,
    color: colors.textPrimary,
    fontWeight: '600',
    marginBottom: spacing.md,
  },
  alertCard: {
    backgroundColor: colors.surfaceSecondary,
    borderRadius: 12,
    padding: spacing.md,
    marginBottom: spacing.sm,
    borderLeftWidth: 4,
  },
  alertHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.xs,
  },
  alertTitle: {
    fontSize: typography.fontSize.base,
    color: colors.textPrimary,
    fontWeight: '600',
    flex: 1,
    marginLeft: spacing.sm,
  },
  alertTime: {
    fontSize: typography.fontSize.xs,
    color: colors.textSecondary,
  },
  alertMessage: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    marginBottom: spacing.sm,
  },
  alertAction: {
    alignSelf: 'flex-start',
  },
  actionRequiredText: {
    fontSize: typography.fontSize.xs,
    color: colors.warning,
    fontWeight: '600',
    backgroundColor: colors.warning + '20',
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: 6,
  },
  insightsSection: {
    paddingHorizontal: spacing.lg,
    marginTop: spacing.lg,
  },
  insightCard: {
    backgroundColor: colors.surfaceSecondary,
    borderRadius: 12,
    padding: spacing.md,
    marginBottom: spacing.md,
  },
  insightHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  insightCategory: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs,
  },
  insightCategoryText: {
    fontSize: typography.fontSize.xs,
    color: colors.primary,
    fontWeight: '600',
  },
  confidenceIndicator: {
    backgroundColor: colors.success + '20',
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: 6,
  },
  confidenceText: {
    fontSize: typography.fontSize.xs,
    color: colors.success,
    fontWeight: '600',
  },
  insightTitle: {
    fontSize: typography.fontSize.base,
    color: colors.textPrimary,
    fontWeight: '600',
    marginBottom: spacing.xs,
  },
  insightContent: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    marginBottom: spacing.md,
  },
  recommendationsContainer: {
    gap: spacing.xs,
  },
  recommendationItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: spacing.xs,
  },
  recommendationText: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    flex: 1,
  },
}), []), []), []);

// 导出类型
export type { HealthMetric, HealthAlert, AIInsight, AdvancedHealthDashboardProps }; 