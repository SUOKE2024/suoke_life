import { useNavigation } from '@react-navigation/native';
import React, { useEffect, useRef, useState } from 'react';
import {
  Animated,
  Dimensions,
  RefreshControl,
  ScrollView,
  Share,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { Button } from '../../components/ui/Button';
import {
  borderRadius,
  colors,
  shadows,
  spacing,
  typography,
} from '../../constants/theme';

const { width: screenWidth } = Dimensions.get('window');

interface HealthMetric {
  id: string;,
  name: string;,
  value: number;,
  unit: string;,
  status: 'excellent' | 'good' | 'normal' | 'attention' | 'warning';,
  trend: 'up' | 'down' | 'stable';,
  change: number;,
  icon: string;,
  color: string;,
  description: string;
  recommendation?: string;
}

interface HealthScore {
  overall: number;,
  categories: {,
  cardiovascular: number;,
  metabolism: number;,
  immunity: number;,
  mental: number;,
  sleep: number;
  };
}

interface AIInsight {
  id: string;,
  type: 'positive' | 'neutral' | 'warning';,
  title: string;,
  content: string;,
  priority: 'high' | 'medium' | 'low';,
  actionable: boolean;,
  icon: string;
}

const HealthReportScreen: React.FC = () => {
  const navigation = useNavigation();
  const [refreshing, setRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState<
    'overview' | 'metrics' | 'insights' | 'trends'
  >('overview');
  const [reportData, setReportData] = useState<any>(null);

  // 动画值
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(50)).current;

  // 健康评分
  const healthScore = {
    overall: 85,
    categories: {,
  cardiovascular: 88,
      metabolism: 82,
      immunity: 90,
      mental: 78,
      sleep: 85,
    },
  };

  // 健康指标
  const healthMetrics = [
    {
      id: '1',
      name: '血压',
      value: 120,
      unit: 'mmHg',
      status: 'good',
      trend: 'stable',
      change: 0,
      icon: 'heart-pulse',
      color: colors.success,
      description: '血压正常，继续保持良好的生活习惯',
      recommendation: '建议继续保持规律运动和健康饮食',
    },
    {
      id: '2',
      name: '心率',
      value: 72,
      unit: 'bpm',
      status: 'excellent',
      trend: 'down',
      change: -3,
      icon: 'heart',
      color: colors.primary,
      description: '静息心率优秀，心血管健康状况良好',
      recommendation: '可以适当增加有氧运动强度',
    },
    {
      id: '3',
      name: 'BMI',
      value: 22.5,
      unit: 'kg/m²',
      status: 'normal',
      trend: 'up',
      change: 0.3,
      icon: 'scale-bathroom',
      color: colors.info,
      description: 'BMI在正常范围内，体重控制良好',
      recommendation: '保持当前的饮食和运动习惯',
    },
    {
      id: '4',
      name: '血糖',
      value: 5.2,
      unit: 'mmol/L',
      status: 'good',
      trend: 'stable',
      change: 0.1,
      icon: 'water',
      color: colors.warning,
      description: '空腹血糖正常，代谢功能良好',
      recommendation: '注意控制糖分摄入，保持规律饮食',
    },
    {
      id: '5',
      name: '睡眠质量',
      value: 82,
      unit: '分',
      status: 'good',
      trend: 'up',
      change: 5,
      icon: 'sleep',
      color: colors.secondary,
      description: '睡眠质量良好，深度睡眠充足',
      recommendation: '建议保持规律作息，避免睡前使用电子设备',
    },
  ];

  // AI洞察
  const aiInsights = [
    {
      id: '1',
      type: 'positive',
      title: '心血管健康改善',
      content:
        '过去30天您的心率变异性提升了12%，表明心血管适应性增强。这与您坚持的有氧运动密切相关。',
      priority: 'medium',
      actionable: false,
      icon: 'heart-plus',
    },
    {
      id: '2',
      type: 'warning',
      title: '压力水平偏高',
      content:
        '检测到您的皮质醇水平在工作日明显升高，建议增加放松练习和压力管理技巧。',
      priority: 'high',
      actionable: true,
      icon: 'alert-circle',
    },
    {
      id: '3',
      type: 'neutral',
      title: '营养摄入分析',
      content:
        '您的蛋白质摄入充足，但维生素D略显不足。建议适当增加户外活动或补充维生素D。',
      priority: 'medium',
      actionable: true,
      icon: 'nutrition',
    },
  ];

  // 初始化动画
  useEffect() => {
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 800,
        useNativeDriver: true,
      }),
      Animated.timing(slideAnim, {
        toValue: 0,
        duration: 800,
        useNativeDriver: true,
      }),
    ]).start();

    loadReportData();
  }, []);

  // 加载报告数据
  const loadReportData = async () => {
    // 模拟加载数据
    setTimeout() => {
      setReportData({
        generatedAt: new Date().toISOString(),
        period: '最近30天',
        dataPoints: 847,
      });
    }, 1000);
  };

  // 刷新数据
  const onRefresh = async () => {
    setRefreshing(true);
    await loadReportData();
    setRefreshing(false);
  };

  // 获取状态颜色
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'excellent':
        return colors.success;
      case 'good':
        return colors.primary;
      case 'normal':
        return colors.info;
      case 'attention':
        return colors.warning;
      case 'warning':
        return colors.error;
      default:
        return colors.textSecondary;
    }
  };

  // 获取状态文本
  const getStatusText = (status: string) => {
    switch (status) {
      case 'excellent':
        return '优秀';
      case 'good':
        return '良好';
      case 'normal':
        return '正常';
      case 'attention':
        return '注意';
      case 'warning':
        return '警告';
      default:
        return '未知';
    }
  };

  // 获取趋势图标
  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up':
        return 'trending-up';
      case 'down':
        return 'trending-down';
      case 'stable':
        return 'trending-neutral';
      default:
        return 'minus';
    }
  };

  // 分享报告
  const shareReport = async () => {
    try {
      await Share.share({
        message: `我的健康报告 - 综合评分: ${healthScore.overall}分\n\n生成时间: ${new Date().toLocaleDateString()}\n\n索克生活健康管理平台`,
        title: '健康报告分享',
      });
    } catch (error) {
      console.error('分享失败:', error);
    }
  };

  // 渲染标签栏
  const renderTabs = () => {
    const tabs = [
      { key: 'overview', title: '概览', icon: 'view-dashboard' },
      { key: 'metrics', title: '指标', icon: 'chart-line' },
      { key: 'insights', title: '洞察', icon: 'lightbulb' },
      { key: 'trends', title: '趋势', icon: 'trending-up' },
    ];

    return (
      <View style={styles.tabContainer}>
        {tabs.map(tab) => (
          <TouchableOpacity;
            key={tab.key}
            style={[styles.tab, activeTab === tab.key && styles.activeTab]}
            onPress={() => setActiveTab(tab.key as any)}
          >
            <Icon;
              name={tab.icon}
              size={20}
              color={
                activeTab === tab.key ? colors.primary : colors.textSecondary;
              }
            />
            <Text;
              style={[
                styles.tabText,
                activeTab === tab.key && styles.activeTabText,
              ]}
            >
              {tab.title}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
    );
  };

  // 渲染健康评分
  const renderHealthScore = () => (
    <View style={styles.scoreContainer}>
      <View style={styles.overallScore}>
        <Text style={styles.scoreValue}>{healthScore.overall}</Text>
        <Text style={styles.scoreLabel}>综合评分</Text>
        <View style={styles.scoreRing}>
          <View;
            style={[
              styles.scoreProgress,
              {
                transform: [
                  { rotate: `${(healthScore.overall / 100) * 360}deg` },
                ],
              },
            ]}
          />
        </View>
      </View>

      <View style={styles.categoryScores}>
        {Object.entries(healthScore.categories).map([key, value]) => (
          <View key={key} style={styles.categoryScore}>
            <Text style={styles.categoryValue}>{value}</Text>
            <Text style={styles.categoryLabel}>
              {key === 'cardiovascular'
                ? '心血管'
                : key === 'metabolism'
                  ? '代谢'
                  : key === 'immunity'
                    ? '免疫'
                    : key === 'mental'
                      ? '心理'
                      : '睡眠'}
            </Text>
          </View>
        ))}
      </View>
    </View>
  );

  // 渲染健康指标
  const renderHealthMetrics = () => (
    <View style={styles.metricsContainer}>
      {healthMetrics.map(metric) => (
        <View key={metric.id} style={styles.metricCard}>
          <View style={styles.metricHeader}>
            <View;
              style={[
                styles.metricIcon,
                { backgroundColor: metric.color + '20' },
              ]}
            >
              <Icon name={metric.icon} size={24} color={metric.color} />
            </View>
            <View style={styles.metricInfo}>
              <Text style={styles.metricName}>{metric.name}</Text>
              <View style={styles.metricValue}>
                <Text style={styles.metricNumber}>{metric.value}</Text>
                <Text style={styles.metricUnit}>{metric.unit}</Text>
              </View>
            </View>
            <View style={styles.metricStatus}>
              <View;
                style={[
                  styles.statusBadge,
                  { backgroundColor: getStatusColor(metric.status) },
                ]}
              >
                <Text style={styles.statusText}>
                  {getStatusText(metric.status)}
                </Text>
              </View>
              <View style={styles.trendContainer}>
                <Icon;
                  name={getTrendIcon(metric.trend)}
                  size={16}
                  color={
                    metric.trend === 'up'
                      ? colors.success;
                      : metric.trend === 'down'
                        ? colors.error;
                        : colors.textSecondary;
                  }
                />
                {metric.change !== 0 && (
                  <Text;
                    style={[
                      styles.changeText,
                      {
                        color:
                          metric.change > 0 ? colors.success : colors.error,
                      },
                    ]}
                  >
                    {metric.change > 0 ? '+' : ''}
                    {metric.change}
                  </Text>
                )}
              </View>
            </View>
          </View>

          <Text style={styles.metricDescription}>{metric.description}</Text>

          {metric.recommendation && (
            <View style={styles.recommendationContainer}>
              <Icon name="lightbulb-outline" size={16} color={colors.warning} />
              <Text style={styles.recommendationText}>
                {metric.recommendation}
              </Text>
            </View>
          )}
        </View>
      ))}
    </View>
  );

  // 渲染AI洞察
  const renderAIInsights = () => (
    <View style={styles.insightsContainer}>
      {aiInsights.map(insight) => (
        <View key={insight.id} style={styles.insightCard}>
          <View style={styles.insightHeader}>
            <View;
              style={[
                styles.insightIcon,
                {
                  backgroundColor:
                    insight.type === 'positive'
                      ? colors.success + '20'
                      : insight.type === 'warning'
                        ? colors.error + '20'
                        : colors.info + '20',
                },
              ]}
            >
              <Icon;
                name={insight.icon}
                size={20}
                color={
                  insight.type === 'positive'
                    ? colors.success;
                    : insight.type === 'warning'
                      ? colors.error;
                      : colors.info;
                }
              />
            </View>
            <View style={styles.insightInfo}>
              <Text style={styles.insightTitle}>{insight.title}</Text>
              <View style={styles.insightMeta}>
                <View;
                  style={[
                    styles.priorityBadge,
                    {
                      backgroundColor:
                        insight.priority === 'high'
                          ? colors.error;
                          : insight.priority === 'medium'
                            ? colors.warning;
                            : colors.success,
                    },
                  ]}
                >
                  <Text style={styles.priorityText}>
                    {insight.priority === 'high'
                      ? '高优先级'
                      : insight.priority === 'medium'
                        ? '中优先级'
                        : '低优先级'}
                  </Text>
                </View>
                {insight.actionable && (
                  <View style={styles.actionableBadge}>
                    <Text style={styles.actionableText}>可执行</Text>
                  </View>
                )}
              </View>
            </View>
          </View>

          <Text style={styles.insightContent}>{insight.content}</Text>

          {insight.actionable && (
            <View style={styles.insightActions}>
              <Button;
                title="查看建议"
                onPress={() => {
                  /* 查看建议 */
                }}
              />
            </View>
          )}
        </View>
      ))}
    </View>
  );

  // 渲染趋势图表
  const renderTrends = () => (
    <View style={styles.trendsContainer}>
      <Text style={styles.trendsTitle}>健康趋势分析</Text>
      <View style={styles.chartPlaceholder}>
        <Icon name="chart-line" size={48} color={colors.textSecondary} />
        <Text style={styles.chartPlaceholderText}>趋势图表</Text>
        <Text style={styles.chartPlaceholderSubtext}>
          显示过去30天的健康数据变化
        </Text>
      </View>

      <View style={styles.trendSummary}>
        <Text style={styles.trendSummaryTitle}>关键趋势</Text>
        <View style={styles.trendItems}>
          <View style={styles.trendItem}>
            <Icon name="trending-up" size={16} color={colors.success} />
            <Text style={styles.trendItemText}>睡眠质量持续改善</Text>
          </View>
          <View style={styles.trendItem}>
            <Icon name="trending-down" size={16} color={colors.success} />
            <Text style={styles.trendItemText}>静息心率稳步下降</Text>
          </View>
          <View style={styles.trendItem}>
            <Icon name="trending-neutral" size={16} color={colors.info} />
            <Text style={styles.trendItemText}>血压保持稳定</Text>
          </View>
        </View>
      </View>
    </View>
  );

  // 渲染内容
  const renderContent = () => {
    switch (activeTab) {
      case 'overview':
        return (
          <>
            {renderHealthScore()}
            {renderHealthMetrics()}
          </>
        );
      case 'metrics':
        return renderHealthMetrics();
      case 'insights':
        return renderAIInsights();
      case 'trends':
        return renderTrends();
      default:
        return null;
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      {/* 头部 */}
      <View style={styles.header}>
        <TouchableOpacity;
          style={styles.backButton}
          onPress={() => navigation.goBack()}
        >
          <Icon name="arrow-left" size={24} color={colors.text} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>健康报告</Text>
        <TouchableOpacity style={styles.shareButton} onPress={shareReport}>
          <Icon name="share-variant" size={24} color={colors.text} />
        </TouchableOpacity>
      </View>

      {/* 标签栏 */}
      {renderTabs()}

      <ScrollView;
        style={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        <Animated.View;
          style={[
            styles.contentContainer,
            {
              opacity: fadeAnim,
              transform: [{ translateY: slideAnim }],
            },
          ]}
        >
          {/* 报告信息 */}
          {reportData && (
            <View style={styles.reportInfo}>
              <Text style={styles.reportInfoText}>
                报告周期: {reportData.period} • 数据点: {reportData.dataPoints}
              </Text>
              <Text style={styles.reportInfoText}>
                生成时间: {new Date(reportData.generatedAt).toLocaleString()}
              </Text>
            </View>
          )}

          {/* 内容区域 */}
          {renderContent()}
        </Animated.View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {,
  flex: 1,
    backgroundColor: colors.background,
  },
  header: {,
  flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    backgroundColor: colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  backButton: {,
  width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.gray100,
    justifyContent: 'center',
    alignItems: 'center',
  },
  headerTitle: {,
  fontSize: typography.fontSize.lg,
    fontWeight: '600' as const,
    color: colors.text,
  },
  shareButton: {,
  width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.gray100,
    justifyContent: 'center',
    alignItems: 'center',
  },
  tabContainer: {,
  flexDirection: 'row',
    backgroundColor: colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  tab: {,
  flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: spacing.md,
    gap: spacing.xs,
  },
  activeTab: {,
  borderBottomWidth: 2,
    borderBottomColor: colors.primary,
  },
  tabText: {,
  fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
  },
  activeTabText: {,
  color: colors.primary,
    fontWeight: '600' as const,
  },
  content: {,
  flex: 1,
  },
  contentContainer: {,
  padding: spacing.lg,
  },
  reportInfo: {,
  backgroundColor: colors.surface,
    padding: spacing.md,
    borderRadius: borderRadius.md,
    marginBottom: spacing.lg,
    ...shadows.sm,
  },
  reportInfoText: {,
  fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    textAlign: 'center',
  },
  scoreContainer: {,
  backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    marginBottom: spacing.lg,
    ...shadows.sm,
  },
  overallScore: {,
  alignItems: 'center',
    marginBottom: spacing.lg,
    position: 'relative',
  },
  scoreValue: {,
  fontSize: 48,
    fontWeight: '700' as const,
    color: colors.primary,
  },
  scoreLabel: {,
  fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  scoreRing: {,
  position: 'absolute',
    width: 120,
    height: 120,
    borderRadius: 60,
    borderWidth: 8,
    borderColor: colors.gray200,
    top: -10,
  },
  scoreProgress: {,
  position: 'absolute',
    width: 120,
    height: 120,
    borderRadius: 60,
    borderWidth: 8,
    borderColor: colors.primary,
    borderRightColor: 'transparent',
    borderBottomColor: 'transparent',
  },
  categoryScores: {,
  flexDirection: 'row',
    justifyContent: 'space-around',
  },
  categoryScore: {,
  alignItems: 'center',
  },
  categoryValue: {,
  fontSize: typography.fontSize.lg,
    fontWeight: '600' as const,
    color: colors.text,
  },
  categoryLabel: {,
  fontSize: typography.fontSize.xs,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  metricsContainer: {,
  gap: spacing.md,
  },
  metricCard: {,
  backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    ...shadows.sm,
  },
  metricHeader: {,
  flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  metricIcon: {,
  width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.md,
  },
  metricInfo: {,
  flex: 1,
  },
  metricName: {,
  fontSize: typography.fontSize.base,
    fontWeight: '600' as const,
    color: colors.text,
    marginBottom: spacing.xs,
  },
  metricValue: {,
  flexDirection: 'row',
    alignItems: 'baseline',
  },
  metricNumber: {,
  fontSize: typography.fontSize.xl,
    fontWeight: '700' as const,
    color: colors.text,
  },
  metricUnit: {,
  fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    marginLeft: spacing.xs,
  },
  metricStatus: {,
  alignItems: 'flex-end',
  },
  statusBadge: {,
  paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: borderRadius.sm,
    marginBottom: spacing.xs,
  },
  statusText: {,
  fontSize: typography.fontSize.xs,
    color: colors.white,
    fontWeight: '600' as const,
  },
  trendContainer: {,
  flexDirection: 'row',
    alignItems: 'center',
  },
  changeText: {,
  fontSize: typography.fontSize.xs,
    marginLeft: spacing.xs,
    fontWeight: '600' as const,
  },
  metricDescription: {,
  fontSize: typography.fontSize.sm,
    color: colors.text,
    lineHeight: 20,
    marginBottom: spacing.sm,
  },
  recommendationContainer: {,
  flexDirection: 'row',
    alignItems: 'flex-start',
    backgroundColor: colors.warning + '10',
    padding: spacing.sm,
    borderRadius: borderRadius.sm,
  },
  recommendationText: {,
  fontSize: typography.fontSize.sm,
    color: colors.text,
    marginLeft: spacing.sm,
    flex: 1,
  },
  insightsContainer: {,
  gap: spacing.md,
  },
  insightCard: {,
  backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    ...shadows.sm,
  },
  insightHeader: {,
  flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: spacing.md,
  },
  insightIcon: {,
  width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.md,
  },
  insightInfo: {,
  flex: 1,
  },
  insightTitle: {,
  fontSize: typography.fontSize.base,
    fontWeight: '600' as const,
    color: colors.text,
    marginBottom: spacing.xs,
  },
  insightMeta: {,
  flexDirection: 'row',
    gap: spacing.sm,
  },
  priorityBadge: {,
  paddingHorizontal: spacing.xs,
    paddingVertical: 2,
    borderRadius: borderRadius.sm,
  },
  priorityText: {,
  fontSize: typography.fontSize.xs,
    color: colors.white,
    fontWeight: '600' as const,
  },
  actionableBadge: {,
  backgroundColor: colors.primary + '20',
    paddingHorizontal: spacing.xs,
    paddingVertical: 2,
    borderRadius: borderRadius.sm,
  },
  actionableText: {,
  fontSize: typography.fontSize.xs,
    color: colors.primary,
    fontWeight: '600' as const,
  },
  insightContent: {,
  fontSize: typography.fontSize.sm,
    color: colors.text,
    lineHeight: 20,
    marginBottom: spacing.md,
  },
  insightActions: {,
  alignItems: 'flex-start',
  },
  trendsContainer: {,
  backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    ...shadows.sm,
  },
  trendsTitle: {,
  fontSize: typography.fontSize.lg,
    fontWeight: '600' as const,
    color: colors.text,
    marginBottom: spacing.lg,
  },
  chartPlaceholder: {,
  alignItems: 'center',
    justifyContent: 'center',
    height: 200,
    backgroundColor: colors.gray100,
    borderRadius: borderRadius.md,
    marginBottom: spacing.lg,
  },
  chartPlaceholderText: {,
  fontSize: typography.fontSize.base,
    color: colors.textSecondary,
    marginTop: spacing.sm,
  },
  chartPlaceholderSubtext: {,
  fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  trendSummary: {,
  marginTop: spacing.lg,
  },
  trendSummaryTitle: {,
  fontSize: typography.fontSize.base,
    fontWeight: '600' as const,
    color: colors.text,
    marginBottom: spacing.md,
  },
  trendItems: {,
  gap: spacing.sm,
  },
  trendItem: {,
  flexDirection: 'row',
    alignItems: 'center',
  },
  trendItemText: {,
  fontSize: typography.fontSize.sm,
    color: colors.text,
    marginLeft: spacing.sm,
  },
});

export default HealthReportScreen;
