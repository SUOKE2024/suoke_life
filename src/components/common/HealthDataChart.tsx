import React, { useState, useEffect } from 'react';
import { View, StyleSheet, Dimensions } from 'react-native';
import { Text, Card, useTheme, SegmentedButtons } from 'react-native-paper';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

const screenWidth = Dimensions.get('window').width;

interface HealthDataPoint {
  date: string;
  value: number;
  label?: string;
}

interface HealthDataChartProps {
  title: string;
  data: HealthDataPoint[];
  type: 'line' | 'bar' | 'pie';
  unit?: string;
  color?: string;
  showTrend?: boolean;
  onDataPointPress?: (point: HealthDataPoint) => void;
}

const HealthDataChart: React.FC<HealthDataChartProps> = ({
  title,
  data,
  type,
  unit = '',
  color,
  showTrend = true,
  onDataPointPress
}) => {
  const theme = useTheme();
  const [timeRange, setTimeRange] = useState('week');
  const [filteredData, setFilteredData] = useState<HealthDataPoint[]>([]);

  const chartColor = color || theme.colors.primary;

  useEffect(() => {
    filterDataByTimeRange();
  }, [data, timeRange]);

  const filterDataByTimeRange = () => {
    const now = new Date();
    let startDate = new Date();

    switch (timeRange) {
      case 'week':
        startDate.setDate(now.getDate() - 7);
        break;
      case 'month':
        startDate.setMonth(now.getMonth() - 1);
        break;
      case 'year':
        startDate.setFullYear(now.getFullYear() - 1);
        break;
      default:
        startDate.setDate(now.getDate() - 7);
    }

    const filtered = data.filter(point => {
      const pointDate = new Date(point.date);
      return pointDate >= startDate && pointDate <= now;
    });

    setFilteredData(filtered);
  };

  const calculateTrend = () => {
    if (filteredData.length < 2) return { direction: 'stable', percentage: 0 };

    const firstValue = filteredData[0].value;
    const lastValue = filteredData[filteredData.length - 1].value;
    const change = lastValue - firstValue;
    const percentage = Math.abs((change / firstValue) * 100);

    return {
      direction: change > 0 ? 'up' : change < 0 ? 'down' : 'stable',
      percentage: Math.round(percentage * 10) / 10
    };
  };

  const getStatistics = () => {
    if (filteredData.length === 0) return { min: 0, max: 0, avg: 0 };

    const values = filteredData.map(point => point.value);
    const min = Math.min(...values);
    const max = Math.max(...values);
    const avg = values.reduce((sum, val) => sum + val, 0) / values.length;

    return {
      min: Math.round(min * 10) / 10,
      max: Math.round(max * 10) / 10,
      avg: Math.round(avg * 10) / 10
    };
  };

  const getChartIcon = () => {
    switch (type) {
      case 'line': return 'chart-line';
      case 'bar': return 'chart-bar';
      case 'pie': return 'chart-pie';
      default: return 'chart-line';
    }
  };

  const getChartTypeName = () => {
    switch (type) {
      case 'line': return '折线图';
      case 'bar': return '柱状图';
      case 'pie': return '饼图';
      default: return '图表';
    }
  };

  const renderChart = () => {
    return (
      <View style={styles.chartPlaceholder}>
        <Icon name={getChartIcon()} size={48} color={theme.colors.outline} />
        <Text style={styles.chartPlaceholderText}>
          {getChartTypeName()}功能开发中...
        </Text>
        <Text style={styles.chartDataText}>
          数据点: {filteredData.length} 个
        </Text>
      </View>
    );
  };

  const renderTrendIndicator = () => {
    if (!showTrend || type === 'pie') return null;

    const trend = calculateTrend();
    const trendIcon = trend.direction === 'up' ? 'trending-up' :
                     trend.direction === 'down' ? 'trending-down' : 'trending-neutral';
    const trendColor = trend.direction === 'up' ? '#4CAF50' :
                       trend.direction === 'down' ? '#F44336' : '#9E9E9E';

    return (
      <View style={styles.trendContainer}>
        <Icon name={trendIcon} size={20} color={trendColor} />
        <Text style={[styles.trendText, { color: trendColor }]}>
          {trend.direction === 'stable' ? '稳定' : `${trend.percentage}%`}
        </Text>
      </View>
    );
  };

  const renderStatistics = () => {
    if (type === 'pie') return null;

    const stats = getStatistics();

    return (
      <View style={styles.statisticsContainer}>
        <View style={styles.statItem}>
          <Text style={styles.statLabel}>最小值</Text>
          <Text style={styles.statValue}>{stats.min}{unit}</Text>
        </View>
        <View style={styles.statItem}>
          <Text style={styles.statLabel}>平均值</Text>
          <Text style={styles.statValue}>{stats.avg}{unit}</Text>
        </View>
        <View style={styles.statItem}>
          <Text style={styles.statLabel}>最大值</Text>
          <Text style={styles.statValue}>{stats.max}{unit}</Text>
        </View>
      </View>
    );
  };

  return (
    <Card style={styles.container}>
      <Card.Content>
        {/* 标题和趋势 */}
        <View style={styles.header}>
          <View style={styles.titleContainer}>
            <Text style={styles.title}>{title}</Text>
            {renderTrendIndicator()}
          </View>
        </View>

        {/* 时间范围选择器 */}
        {type !== 'pie' && (
          <SegmentedButtons
            value={timeRange}
            onValueChange={setTimeRange}
            buttons={[
              { value: 'week', label: '7天' },
              { value: 'month', label: '30天' },
              { value: 'year', label: '1年' }
            ]}
            style={styles.timeRangeSelector}
          />
        )}

        {/* 图表 */}
        <View style={styles.chartContainer}>
          {filteredData.length > 0 ? (
            renderChart()
          ) : (
            <View style={styles.noDataContainer}>
              <Icon name="chart-line" size={48} color={theme.colors.outline} />
              <Text style={styles.noDataText}>暂无数据</Text>
            </View>
          )}
        </View>

        {/* 统计信息 */}
        {filteredData.length > 0 && renderStatistics()}
      </Card.Content>
    </Card>
  );
};

const styles = StyleSheet.create({
  container: {
    margin: 8,
    elevation: 2,
  },
  header: {
    marginBottom: 16,
  },
  titleContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  trendContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  trendText: {
    marginLeft: 4,
    fontSize: 14,
    fontWeight: 'bold',
  },
  timeRangeSelector: {
    marginBottom: 16,
  },
  chartContainer: {
    alignItems: 'center',
    marginBottom: 16,
  },
  chartPlaceholder: {
    height: 220,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
    borderRadius: 12,
    width: screenWidth - 60,
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
  noDataContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    height: 220,
  },
  noDataText: {
    marginTop: 8,
    fontSize: 16,
    opacity: 0.6,
  },
  statisticsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: '#E0E0E0',
  },
  statItem: {
    alignItems: 'center',
  },
  statLabel: {
    fontSize: 12,
    opacity: 0.7,
    marginBottom: 4,
  },
  statValue: {
    fontSize: 16,
    fontWeight: 'bold',
  },
});

export default HealthDataChart;