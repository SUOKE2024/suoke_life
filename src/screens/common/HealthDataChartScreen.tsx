import React, { useState } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  Dimensions,
} from 'react-native';
import {
  Appbar,
  Card,
  Title,
  Text,
  Button,
  SegmentedButtons,
  Surface,
  Chip,
} from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { useTheme } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
// import { LineChart, BarChart, PieChart } from 'react-native-chart-kit';

const { width } = Dimensions.get('window');

interface HealthDataChartScreenProps {
  navigation?: any;
}

const HealthDataChartScreen: React.FC<HealthDataChartScreenProps> = ({ navigation }) => {
  const theme = useTheme();
  const { t } = useTranslation();
  
  const [selectedPeriod, setSelectedPeriod] = useState('7days');
  const [selectedMetric, setSelectedMetric] = useState('steps');

  // 时间段选项
  const periodOptions = [
    { value: '7days', label: '7天' },
    { value: '30days', label: '30天' },
    { value: '1year', label: '1年' },
  ];

  // 健康指标选项
  const metricOptions = [
    { id: 'steps', name: '步数', icon: 'walk', color: '#4CAF50' },
    { id: 'weight', name: '体重', icon: 'scale-bathroom', color: '#2196F3' },
    { id: 'sleep', name: '睡眠', icon: 'sleep', color: '#9C27B0' },
    { id: 'heartRate', name: '心率', icon: 'heart', color: '#F44336' },
    { id: 'bloodPressure', name: '血压', icon: 'heart-pulse', color: '#FF9800' },
    { id: 'water', name: '饮水', icon: 'cup-water', color: '#00BCD4' },
  ];

  // 模拟数据
  const generateMockData = (metric: string, period: string) => {
    const days = period === '7days' ? 7 : period === '30days' ? 30 : 365;
    const labels = [];
    const data = [];

    for (let i = days - 1; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      
      if (period === '7days') {
        labels.push(date.toLocaleDateString('zh-CN', { month: 'numeric', day: 'numeric' }));
      } else if (period === '30days') {
        labels.push(date.toLocaleDateString('zh-CN', { month: 'numeric', day: 'numeric' }));
      } else {
        labels.push(date.toLocaleDateString('zh-CN', { month: 'numeric' }));
      }

      // 根据指标生成不同范围的数据
      let value;
      switch (metric) {
        case 'steps':
          value = Math.floor(Math.random() * 5000) + 5000;
          break;
        case 'weight':
          value = Math.random() * 10 + 65;
          break;
        case 'sleep':
          value = Math.random() * 3 + 6;
          break;
        case 'heartRate':
          value = Math.floor(Math.random() * 30) + 60;
          break;
        case 'bloodPressure':
          value = Math.floor(Math.random() * 20) + 110;
          break;
        case 'water':
          value = Math.floor(Math.random() * 1000) + 1000;
          break;
        default:
          value = Math.random() * 100;
      }
      data.push(value);
    }

    return { labels, data };
  };

  const chartData = generateMockData(selectedMetric, selectedPeriod);
  const currentMetric = metricOptions.find(m => m.id === selectedMetric);

  // 统计信息
  const getStatistics = () => {
    const values = chartData.data;
    const avg = values.reduce((a, b) => a + b, 0) / values.length;
    const max = Math.max(...values);
    const min = Math.min(...values);
    const latest = values[values.length - 1];
    const previous = values[values.length - 2];
    const change = latest - previous;
    const changePercent = (change / previous) * 100;

    return {
      average: avg.toFixed(1),
      maximum: max.toFixed(1),
      minimum: min.toFixed(1),
      latest: latest.toFixed(1),
      change: change.toFixed(1),
      changePercent: changePercent.toFixed(1),
    };
  };

  const stats = getStatistics();

  const renderChart = () => {
    const chartConfig = {
      backgroundColor: theme.colors.surface,
      backgroundGradientFrom: theme.colors.surface,
      backgroundGradientTo: theme.colors.surface,
      decimalPlaces: selectedMetric === 'weight' || selectedMetric === 'sleep' ? 1 : 0,
      color: (opacity = 1) => currentMetric?.color || theme.colors.primary,
      labelColor: (opacity = 1) => theme.colors.onSurface,
      style: {
        borderRadius: 16,
      },
      propsForDots: {
        r: '4',
        strokeWidth: '2',
        stroke: currentMetric?.color || theme.colors.primary,
      },
    };

    return (
      <Card style={styles.chartCard}>
        <Card.Content>
          <View style={styles.chartHeader}>
            <View style={styles.metricInfo}>
              <Icon 
                name={currentMetric?.icon || 'chart-line'} 
                size={24} 
                color={currentMetric?.color || theme.colors.primary} 
              />
              <Title style={styles.chartTitle}>{currentMetric?.name}</Title>
            </View>
            <Text style={styles.latestValue}>
              {stats.latest}
              {selectedMetric === 'weight' && ' kg'}
              {selectedMetric === 'sleep' && ' h'}
              {selectedMetric === 'heartRate' && ' bpm'}
              {selectedMetric === 'bloodPressure' && ' mmHg'}
              {selectedMetric === 'water' && ' ml'}
            </Text>
          </View>

          <View style={styles.chartPlaceholder}>
            <Icon name="chart-line" size={48} color={theme.colors.outline} />
            <Text style={styles.chartPlaceholderText}>图表功能开发中...</Text>
            <Text style={styles.chartDataText}>
              数据点: {chartData.data.length} 个
            </Text>
          </View>
        </Card.Content>
      </Card>
    );
  };

  const renderStatistics = () => (
    <Card style={styles.statsCard}>
      <Card.Content>
        <Title style={styles.cardTitle}>统计信息</Title>
        <View style={styles.statsGrid}>
          <View style={styles.statItem}>
            <Text style={styles.statLabel}>平均值</Text>
            <Text style={styles.statValue}>{stats.average}</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statLabel}>最大值</Text>
            <Text style={styles.statValue}>{stats.maximum}</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statLabel}>最小值</Text>
            <Text style={styles.statValue}>{stats.minimum}</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statLabel}>变化</Text>
            <Text style={[
              styles.statValue,
              { color: parseFloat(stats.change) >= 0 ? '#4CAF50' : '#F44336' }
            ]}>
              {parseFloat(stats.change) >= 0 ? '+' : ''}{stats.change}
            </Text>
          </View>
        </View>
      </Card.Content>
    </Card>
  );

  const renderTrends = () => (
    <Card style={styles.trendsCard}>
      <Card.Content>
        <Title style={styles.cardTitle}>趋势分析</Title>
        <View style={styles.trendItem}>
          <Icon 
            name={parseFloat(stats.changePercent) >= 0 ? 'trending-up' : 'trending-down'} 
            size={20} 
            color={parseFloat(stats.changePercent) >= 0 ? '#4CAF50' : '#F44336'} 
          />
          <Text style={styles.trendText}>
            相比昨天{parseFloat(stats.changePercent) >= 0 ? '上升' : '下降'}了 
            <Text style={[
              styles.trendPercent,
              { color: parseFloat(stats.changePercent) >= 0 ? '#4CAF50' : '#F44336' }
            ]}>
              {Math.abs(parseFloat(stats.changePercent))}%
            </Text>
          </Text>
        </View>
        
        <Text style={styles.trendDescription}>
          {parseFloat(stats.changePercent) >= 0 ? 
            '保持良好的趋势，继续努力！' : 
            '需要关注这个指标的变化，建议调整生活习惯。'
          }
        </Text>
      </Card.Content>
    </Card>
  );

  return (
    <SafeAreaView style={styles.container}>
      <Appbar.Header>
        <Appbar.BackAction onPress={() => navigation?.goBack()} />
        <Appbar.Content title="健康数据分析" />
        <Appbar.Action icon="export" onPress={() => {/* 导出功能 */}} />
      </Appbar.Header>

      <ScrollView style={styles.content}>
        {/* 时间段选择 */}
        <Surface style={styles.periodSelector}>
          <SegmentedButtons
            value={selectedPeriod}
            onValueChange={setSelectedPeriod}
            buttons={periodOptions}
          />
        </Surface>

        {/* 指标选择 */}
        <View style={styles.metricsSelector}>
          <ScrollView horizontal showsHorizontalScrollIndicator={false}>
            {metricOptions.map(metric => (
              <Chip
                key={metric.id}
                selected={selectedMetric === metric.id}
                onPress={() => setSelectedMetric(metric.id)}
                style={[
                  styles.metricChip,
                  selectedMetric === metric.id && { backgroundColor: metric.color + '20' }
                ]}
                textStyle={selectedMetric === metric.id && { color: metric.color }}
                icon={metric.icon}
              >
                {metric.name}
              </Chip>
            ))}
          </ScrollView>
        </View>

        {/* 图表 */}
        {renderChart()}

        {/* 统计信息 */}
        {renderStatistics()}

        {/* 趋势分析 */}
        {renderTrends()}
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  content: {
    flex: 1,
    padding: 16,
  },
  periodSelector: {
    padding: 16,
    marginBottom: 16,
    borderRadius: 12,
  },
  metricsSelector: {
    marginBottom: 16,
  },
  metricChip: {
    marginRight: 8,
  },
  chartCard: {
    marginBottom: 16,
    borderRadius: 12,
  },
  chartHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  metricInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  chartTitle: {
    marginLeft: 8,
    fontSize: 18,
    fontWeight: 'bold',
  },
  latestValue: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  chart: {
    marginVertical: 8,
    borderRadius: 16,
  },
  chartPlaceholder: {
    height: 220,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
    borderRadius: 12,
    marginVertical: 8,
  },
  chartPlaceholderText: {
    marginTop: 12,
    fontSize: 16,
    color: '#666',
  },
  chartDataText: {
    marginTop: 8,
    fontSize: 14,
    color: '#999',
  },
  statsCard: {
    marginBottom: 16,
    borderRadius: 12,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  statsGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  statItem: {
    alignItems: 'center',
    flex: 1,
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  statValue: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  trendsCard: {
    marginBottom: 16,
    borderRadius: 12,
  },
  trendItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  trendText: {
    marginLeft: 8,
    fontSize: 14,
  },
  trendPercent: {
    fontWeight: 'bold',
  },
  trendDescription: {
    fontSize: 12,
    color: '#666',
    fontStyle: 'italic',
  },
});

export default HealthDataChartScreen;