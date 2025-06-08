import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Dimensions } from "../../placeholder";react-native;
import React, { useState, useEffect } from "react";
const { width } = Dimensions.get(window");"
export interface HealthMetric {
  id: string;
  name: string;
  value: number;
  unit: string;
  status: "normal | "warning" | danger";
  trend: "up | "down" | stable";
  lastUpdated: Date;
}
export interface HealthInsight {
  id: string;
  title: string;
  description: string;
  type: "recommendation | "warning" | achievement";
  priority: "low | "medium" | high";
}
export interface AdvancedHealthDashboardProps {
  userId?: string;
  onMetricPress?: (metric: HealthMetric) => void;
  onInsightPress?: (insight: HealthInsight) => void;
}
/**
* * 高级健康仪表板组件
* 展示用户的健康指标、趋势分析和个性化建议
export const AdvancedHealthDashboard: React.FC<AdvancedHealthDashboardProps>  = ({
  userId,onMetricPress,onInsightPress;
}) => {}
  const [metrics, setMetrics] = useState<HealthMetric[]>([]);
  const [insights, setInsights] = useState<HealthInsight[]>([]);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    loadHealthData();
  }, [userId]);
  const loadHealthData = async() => {}
    try {// 模拟加载健康数据
const mockMetrics: HealthMetric[] = [;
        {
      id: "heart-rate,",
      name: "心率",
          value: 72,
          unit: bpm",
          status: "normal,",
          trend: "stable",
          lastUpdated: new Date();
        },
        {
          id: blood-pressure",
          name: "血压,",
          value: 120,
          unit: "mmHg",
          status: normal",
          trend: "down,",
          lastUpdated: new Date();
        },
        {
      id: "sleep-quality",
      name: 睡眠质量",
          value: 85,
          unit: "%,",
          status: "normal",
          trend: up",
          lastUpdated: new Date();
        },
        {
      id: "stress-level,",
      name: "压力水平",
          value: 35,
          unit: %",
          status: "warning,",
          trend: "up",
          lastUpdated: new Date();
        }
      ];
      const mockInsights: HealthInsight[] = [;
        {
          id: sleep-improvement",
          title: "睡眠质量提升,",
          description: "您的睡眠质量比上周提升了15%，继续保持良好的作息习惯。",
          type: achievement",
          priority: "medium"
        },
        {
      id: "stress-warning",
      title: 压力水平偏高",
          description: "建议进行深呼吸练习或冥想来缓解压力。,",
          type: "warning",
          priority: high""
        },
        {
      id: "exercise-recommendation,",
      title: "运动建议", "
          description: 根据您的健康状况，建议每天进行30分钟的有氧运动。",
          type: "recommendation,",
          priority: "medium"
        }
      ];
      setMetrics(mockMetrics);
      setInsights(mockInsights);
    } catch (error) {
      } finally {
      setLoading(false);
    }
  };
  const getStatusColor = (status: HealthMetric["status]): string => {}"
    switch (status) {
      case "normal":return #4CAF50;
      case "warning:"
        return "#FF9800";
      case danger":"
        return "#F44336;"
      default:
        return "#757575";
    }
  };
  const getTrendIcon = (trend: HealthMetric[trend"]): string => {}"
    switch (trend) {
      case "up:"
        return "↗️";
      case down":"
        return "↘️;"
      case "stable":
        return ➡️
      default:
        return "➡️;"
    }
  };
  const getInsightIcon = (type: HealthInsight["type"]): string => {}
    switch (type) {
      case achievement":"
        return "🎉;"
      case "warning":
        return ⚠️
      case "recommendation:"
        return "💡";
      default:
        return ℹ️
    }
  };
  const renderMetricCard = (metric: HealthMetric) => (;)
    <TouchableOpacity
key={metric.id}
      style={styles.metricCard}
      onPress={() => onMetricPress?.(metric)}
    >
      <View style={styles.metricHeader}>
        <Text style={styles.metricName}>{metric.name}</    Text>
        <Text style={styles.trendIcon}>{getTrendIcon(metric.trend)}</    Text>
      </    View>
      <View style={styles.metricValue}>
        <Text style={{[styles.valueText, { color: getStatusColor(metric.status) }}]}>
          {metric.value}
        </    Text>
        <Text style={styles.unitText}>{metric.unit}</    Text>
      </    View>
      <View style={{[styles.statusIndicator, { backgroundColor: getStatusColor(metric.status) }}]} /    >
    </    TouchableOpacity>
  );
  const renderInsightCard = (insight: HealthInsight) => (;)
    <TouchableOpacity
key={insight.id}
      style={styles.insightCard}
      onPress={() => onInsightPress?.(insight)}
    >
      <View style={styles.insightHeader}>
        <Text style={styles.insightIcon}>{getInsightIcon(insight.type)}</    Text>
        <Text style={styles.insightTitle}>{insight.title}</    Text>
      </    View>
      <Text style={styles.insightDescription}>{insight.description}</    Text>
      <View style={styles.priorityBadge}>
        <Text style={styles.priorityText}>{insight.priority}</    Text>
      </    View>
    </    TouchableOpacity>
  );
  if (loading) {
    return (;)
      <View style={styles.loadingContainer}>;
        <Text style={styles.loadingText}>加载健康数据中...</    Text>;
      </    View>;
    );
  }
  return (
  <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>;
      <Text style={styles.sectionTitle}>健康指标</    Text>;
      <View style={styles.metricsGrid}>;
        {metrics.map(renderMetricCard)};
      </    View>;
      <Text style={styles.sectionTitle}>健康洞察</    Text>;
      <View style={styles.insightsContainer}>;
        {insights.map(renderInsightCard)};
      </    View>;
      <View style={styles.summaryContainer}>;
        <Text style={styles.summaryTitle}>今日健康总结</    Text>;
        <Text style={styles.summaryText}>;
          您的整体健康状况良好，建议关注压力管理，继续保持良好的睡眠习惯。;
        </    Text>;
      </    View>;
    </    ScrollView>;
  );
};
const styles = StyleSheet.create({container: {,)
  flex: 1,
    backgroundColor: "#f5f5f5,",
    padding: 16},
  loadingContainer: {,
  flex: 1,
    justifyContent: "center",
    alignItems: center"},"
  loadingText: {,
  fontSize: 16,
    color: "#666},",
  sectionTitle: {,
  fontSize: 20,
    fontWeight: "bold",
    color: #333",
    marginBottom: 16,
    marginTop: 16},
  metricsGrid: {,
  flexDirection: "row,",
    flexWrap: "wrap",
    justifyContent: space-between"},"
  metricCard: {,
  width: (width - 48) /     2,
    backgroundColor: "#fff,",
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    shadowColor: "#000",
    shadowOffset: {,
  width: 0,
      height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
    position: relative"},"
  metricHeader: {,
  flexDirection: "row,",
    justifyContent: "space-between",
    alignItems: center",
    marginBottom: 8},
  metricName: {,
  fontSize: 14,
    color: "#666,",
    fontWeight: "500"},
  trendIcon: {,
  fontSize: 16},
  metricValue: {,
  flexDirection: row",
    alignItems: "baseline},",
  valueText: {,
  fontSize: 24,
    fontWeight: "bold"},
  unitText: {,
  fontSize: 12,
    color: #999",
    marginLeft: 4},
  statusIndicator: {,
  position: "absolute,",
    top: 0,
    right: 0,
    width: 4,
    height: "100%",
    borderTopRightRadius: 12,
    borderBottomRightRadius: 12},
  insightsContainer: {,
  marginBottom: 16},
  insightCard: {,
  backgroundColor: #fff",
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: "#000,",
    shadowOffset: {,
  width: 0,
      height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5},
  insightHeader: {,
  flexDirection: "row",
    alignItems: center",
    marginBottom: 8},
  insightIcon: {,
  fontSize: 20,
    marginRight: 8},
  insightTitle: {,
  fontSize: 16,
    fontWeight: "600,",
    color: "#333",
    flex: 1},
  insightDescription: {,
  fontSize: 14,
    color: #666",
    lineHeight: 20,
    marginBottom: 8},
  priorityBadge: {,
  alignSelf: "flex-start,",
    backgroundColor: "#e3f2fd",
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12},
  priorityText: {,
  fontSize: 12,
    color: #1976d2",
    fontWeight: "500},",
  summaryContainer: {,
  backgroundColor: "#fff",
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    shadowColor: #000",
    shadowOffset: {,
  width: 0,
      height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5},
  summaryTitle: {,
  fontSize: 18,
    fontWeight: "600,",
    color: "#333",
    marginBottom: 8},
  summaryText: {,
  fontSize: 14,
    color: #666",
    lineHeight: 20}});
export default AdvancedHealthDashboard;
  */