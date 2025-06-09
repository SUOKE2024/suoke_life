import { useNavigation } from '@react-navigation/native';
import React, { useCallback, useState } from 'react';
import {
  Alert,
  Dimensions,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { Button } from '../../components/ui/Button';
import { Chart } from '../../components/ui/Chart';
import { StatCard } from '../../components/ui/StatCard';
import { Tabs } from '../../components/ui/Tabs';
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
  trend: 'up' | 'down' | 'neutral';,
  change: number;,
  color: string;,
  icon: string;
}

interface ChartData {
  label: string;,
  value: number;,
  date: string;
}

const HealthDataVisualizationScreen: React.FC = () => {
  const navigation = useNavigation();
  const [activeTab, setActiveTab] = useState('overview');
  const [refreshing, setRefreshing] = useState(false);
  const [timeRange, setTimeRange] = useState<'week' | 'month' | 'year'>('week');

  // 模拟健康指标数据
  const [healthMetrics] = useState<HealthMetric[]>([
    {
      id: '1',
      name: '心率',
      value: 72,
      unit: 'bpm',
      trend: 'neutral',
      change: 0,
      color: colors.error,
      icon: 'heart-pulse',
    },
    {
      id: '2',
      name: '血压',
      value: 120,
      unit: 'mmHg',
      trend: 'down',
      change: -5,
      color: colors.primary,
      icon: 'water',
    },
    {
      id: '3',
      name: '体重',
      value: 68.5,
      unit: 'kg',
      trend: 'down',
      change: -1.2,
      color: colors.warning,
      icon: 'scale-bathroom',
    },
    {
      id: '4',
      name: '睡眠',
      value: 7.5,
      unit: '小时',
      trend: 'up',
      change: 0.5,
      color: colors.info,
      icon: 'sleep',
    },
  ]);

  // 模拟图表数据
  const [chartData] = useState<ChartData[]>([
    { label: '周一', value: 8000, date: '2024-01-01' },
    { label: '周二', value: 9500, date: '2024-01-02' },
    { label: '周三', value: 7200, date: '2024-01-03' },
    { label: '周四', value: 10200, date: '2024-01-04' },
    { label: '周五', value: 8800, date: '2024-01-05' },
    { label: '周六', value: 12000, date: '2024-01-06' },
    { label: '周日', value: 6500, date: '2024-01-07' },
  ]);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    // 模拟数据刷新
    await new Promise(resolve) => setTimeout(resolve, 1000));
    setRefreshing(false);
  }, []);

  const handleExportData = () => {
    Alert.alert('导出数据', '选择导出格式', [
      { text: 'PDF报告', onPress: () => console.log('导出PDF') },
      { text: 'Excel表格', onPress: () => console.log('导出Excel') },
      { text: '取消', style: 'cancel' },
    ]);
  };

  const renderOverviewTab = () => (
    <ScrollView style={styles.tabContent}>
      {/* 健康指标卡片 */}
      <View style={styles.metricsContainer}>
        <Text style={styles.sectionTitle}>健康指标概览</Text>
        <View style={styles.metricsGrid}>
          {healthMetrics.map(metric) => (
            <StatCard;
              key={metric.id}
              title={metric.name}
              value={`${metric.value} ${metric.unit}`}
              trend={metric.change}
              trendType={metric.trend}
              color={metric.color as any}
              style={styles.metricCard}
            />
          ))}
        </View>
      </View>

      {/* 步数趋势图 */}
      <View style={styles.chartContainer}>
        <View style={styles.chartHeader}>
          <Text style={styles.sectionTitle}>步数趋势</Text>
          <View style={styles.timeRangeSelector}>
            {(['week', 'month', 'year'] as const).map(range) => (
              <TouchableOpacity;
                key={range}
                style={[
                  styles.timeRangeButton,
                  timeRange === range && styles.timeRangeButtonActive,
                ]}
                onPress={() => setTimeRange(range)}
              >
                <Text;
                  style={[
                    styles.timeRangeText,
                    timeRange === range && styles.timeRangeTextActive,
                  ]}
                >
                  {range === 'week' ? '周' : range === 'month' ? '月' : '年'}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>
        <Chart data={chartData} type="line" height={200} showGrid showLabels />
      </View>

      {/* 健康建议 */}
      <View style={styles.recommendationsContainer}>
        <Text style={styles.sectionTitle}>AI 健康建议</Text>
        <View style={styles.recommendationCard}>
          <Icon name="lightbulb-outline" size={24} color={colors.warning} />
          <View style={styles.recommendationContent}>
            <Text style={styles.recommendationTitle}>运动建议</Text>
            <Text style={styles.recommendationText}>
              您本周的运动量较上周减少了15%，建议增加30分钟的有氧运动。
            </Text>
          </View>
        </View>
        <View style={styles.recommendationCard}>
          <Icon name="sleep" size={24} color={colors.info} />
          <View style={styles.recommendationContent}>
            <Text style={styles.recommendationTitle}>睡眠优化</Text>
            <Text style={styles.recommendationText}>
              您的睡眠质量有所改善，建议保持规律的作息时间。
            </Text>
          </View>
        </View>
      </View>
    </ScrollView>
  );

  const renderTrendsTab = () => (
    <ScrollView style={styles.tabContent}>
      <View style={styles.trendsContainer}>
        <Text style={styles.sectionTitle}>健康趋势分析</Text>

        {/* 心率趋势 */}
        <View style={styles.trendCard}>
          <View style={styles.trendHeader}>
            <Icon name="heart-pulse" size={20} color={colors.error} />
            <Text style={styles.trendTitle}>心率变化</Text>
          </View>
          <Chart;
            data={chartData.map(item) => ({
              ...item,
              value: 70 + Math.random() * 20,
            }))}
            type="area"
            height={150}
            showGrid={false}
          />
        </View>

        {/* 体重趋势 */}
        <View style={styles.trendCard}>
          <View style={styles.trendHeader}>
            <Icon name="scale-bathroom" size={20} color={colors.warning} />
            <Text style={styles.trendTitle}>体重变化</Text>
          </View>
          <Chart;
            data={chartData.map(item) => ({
              ...item,
              value: 68 + Math.random() * 2,
            }))}
            type="line"
            height={150}
            showGrid={false}
          />
        </View>

        {/* 睡眠趋势 */}
        <View style={styles.trendCard}>
          <View style={styles.trendHeader}>
            <Icon name="sleep" size={20} color={colors.info} />
            <Text style={styles.trendTitle}>睡眠时长</Text>
          </View>
          <Chart;
            data={chartData.map(item) => ({
              ...item,
              value: 6 + Math.random() * 3,
            }))}
            type="bar"
            height={150}
            showGrid={false}
          />
        </View>
      </View>
    </ScrollView>
  );

  const renderReportsTab = () => (
    <ScrollView style={styles.tabContent}>
      <View style={styles.reportsContainer}>
        <Text style={styles.sectionTitle}>健康报告</Text>

        <View style={styles.reportCard}>
          <View style={styles.reportHeader}>
            <Icon;
              name="file-document-outline"
              size={24}
              color={colors.primary}
            />
            <View style={styles.reportInfo}>
              <Text style={styles.reportTitle}>周度健康报告</Text>
              <Text style={styles.reportDate}>2024年1月第1周</Text>
            </View>
            <TouchableOpacity style={styles.downloadButton}>
              <Icon name="download" size={20} color={colors.primary} />
            </TouchableOpacity>
          </View>
          <Text style={styles.reportSummary}>
            本周整体健康状况良好，运动量达标，睡眠质量有所改善。
          </Text>
        </View>

        <View style={styles.reportCard}>
          <View style={styles.reportHeader}>
            <Icon name="file-chart" size={24} color={colors.secondary} />
            <View style={styles.reportInfo}>
              <Text style={styles.reportTitle}>月度健康分析</Text>
              <Text style={styles.reportDate}>2024年1月</Text>
            </View>
            <TouchableOpacity style={styles.downloadButton}>
              <Icon name="download" size={20} color={colors.secondary} />
            </TouchableOpacity>
          </View>
          <Text style={styles.reportSummary}>
            月度健康指标稳定，建议继续保持良好的生活习惯。
          </Text>
        </View>

        <Button title="生成自定义报告" onPress={handleExportData} />
      </View>
    </ScrollView>
  );

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
        <Text style={styles.headerTitle}>健康数据</Text>
        <TouchableOpacity;
          style={styles.settingsButton}
          onPress={handleExportData}
        >
          <Icon name="export" size={24} color={colors.text} />
        </TouchableOpacity>
      </View>

      {/* 标签页 */}
      <Tabs;
        activeKey={activeTab}
        onChange={setActiveTab}
        items={[
          { key: 'overview', title: '概览', content: null },
          { key: 'trends', title: '趋势', content: null },
          { key: 'reports', title: '报告', content: null },
        ]}
      />

      {/* 内容区域 */}
      <ScrollView;
        style={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {activeTab === 'overview' && renderOverviewTab()}
        {activeTab === 'trends' && renderTrendsTab()}
        {activeTab === 'reports' && renderReportsTab()}
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
  settingsButton: {,
  width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.gray100,
    justifyContent: 'center',
    alignItems: 'center',
  },
  content: {,
  flex: 1,
  },
  tabContent: {,
  flex: 1,
    padding: spacing.lg,
  },
  sectionTitle: {,
  fontSize: typography.fontSize.lg,
    fontWeight: '600' as const,
    color: colors.text,
    marginBottom: spacing.md,
  },
  metricsContainer: {,
  marginBottom: spacing.xl,
  },
  metricsGrid: {,
  flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  metricCard: {,
  width: (screenWidth - spacing.lg * 3) / 2,
    marginBottom: spacing.md,
  },
  chartContainer: {,
  backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    marginBottom: spacing.xl,
    ...shadows.sm,
  },
  chartHeader: {,
  flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.lg,
  },
  timeRangeSelector: {,
  flexDirection: 'row',
    backgroundColor: colors.gray100,
    borderRadius: borderRadius.md,
    padding: 2,
  },
  timeRangeButton: {,
  paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: borderRadius.sm,
  },
  timeRangeButtonActive: {,
  backgroundColor: colors.primary,
  },
  timeRangeText: {,
  fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
  },
  timeRangeTextActive: {,
  color: colors.white,
  },
  recommendationsContainer: {,
  marginBottom: spacing.xl,
  },
  recommendationCard: {,
  flexDirection: 'row',
    backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    marginBottom: spacing.md,
    ...shadows.sm,
  },
  recommendationContent: {,
  flex: 1,
    marginLeft: spacing.md,
  },
  recommendationTitle: {,
  fontSize: typography.fontSize.base,
    fontWeight: '600' as const,
    color: colors.text,
    marginBottom: spacing.xs,
  },
  recommendationText: {,
  fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    lineHeight: 20,
  },
  trendsContainer: {,
  flex: 1,
  },
  trendCard: {,
  backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    marginBottom: spacing.lg,
    ...shadows.sm,
  },
  trendHeader: {,
  flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  trendTitle: {,
  fontSize: typography.fontSize.base,
    fontWeight: '600' as const,
    color: colors.text,
    marginLeft: spacing.sm,
  },
  reportsContainer: {,
  flex: 1,
  },
  reportCard: {,
  backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    marginBottom: spacing.lg,
    ...shadows.sm,
  },
  reportHeader: {,
  flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  reportInfo: {,
  flex: 1,
    marginLeft: spacing.md,
  },
  reportTitle: {,
  fontSize: typography.fontSize.base,
    fontWeight: '600' as const,
    color: colors.text,
  },
  reportDate: {,
  fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    marginTop: 2,
  },
  downloadButton: {,
  width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: colors.gray100,
    justifyContent: 'center',
    alignItems: 'center',
  },
  reportSummary: {,
  fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    lineHeight: 20,
  },
});

export default HealthDataVisualizationScreen;
