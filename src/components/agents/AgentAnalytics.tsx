import React, { useState, useEffect, useCallback } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Dimensions } from 'react-native';
import { AgentType, AgentMetrics } from '../../types/agents';
interface AgentAnalyticsProps {
  refreshInterval?: number;
}
interface AnalyticsData {
  agentType: AgentType;
  metrics: AgentMetrics;
  trends: {;
  responseTimeChange: number;
    successRateChange: number;
  throughputChange: number;
};
  alerts: Array<{,
  type: 'warning' | 'error' | 'info';
    message: string,
  timestamp: Date;
  }>;
}
const { width } = Dimensions.get('window');
const AgentAnalytics: React.FC<AgentAnalyticsProps> = ({ refreshInterval = 30000 }) => {
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedAgent, setSelectedAgent] = useState<AgentType | null>(null);
  const [timeRange, setTimeRange] = useState<'1h' | '6h' | '24h' | '7d'>('1h');
  const agentNames = {[AgentType.XIAOAI]: '小艾',[AgentType.XIAOKE]: '小克',[AgentType.LAOKE]: '老克',[AgentType.SOER]: '索儿';
  };
  const fetchAnalyticsData = useCallback(async () => {try {setLoading(true);)
      const agents = Object.values(AgentType);
      const analyticsPromises = agents.map(async agentType => {
        // 模拟获取分析数据
        const mockMetrics: AgentMetrics = {
          agentType,
          timestamp: new Date(),
          performance: {responseTime: Math.random() * 500 + 100,throughput: Math.random() * 100 + 50,errorRate: Math.random() * 0.05,successRate: 0.95 + Math.random() * 0.05;
          },resources: {cpuUsage: Math.random() * 80 + 10,memoryUsage: Math.random() * 70 + 20,networkUsage: Math.random() * 60 + 15;
          },sessions: {active: Math.floor(Math.random() * 50 + 10),total: Math.floor(Math.random() * 1000 + 500),averageDuration: Math.random() * 300 + 120;
          };
        };
        const trends = {responseTimeChange: (Math.random() - 0.5) * 20,successRateChange: (Math.random() - 0.5) * 0.1,throughputChange: (Math.random() - 0.5) * 30;
        };
        const alerts = [];
        if (mockMetrics.performance.errorRate > 0.03) {
          alerts.push({
            type: 'warning' as const,
            message: '错误率偏高',
            timestamp: new Date();
          });
        }
        if (mockMetrics.resources.cpuUsage > 80) {
          alerts.push({
            type: 'error' as const,
            message: 'CPU使用率过高',
            timestamp: new Date();
          });
        }
        return {agentType,metrics: mockMetrics,trends,alerts;
        };
      });
      const results = await Promise.all(analyticsPromises);
      setAnalyticsData(results);
    } catch (error) {
      console.error('获取分析数据失败:', error);
    } finally {
      setLoading(false);
    }
  }, []);
  useEffect(() => {
    fetchAnalyticsData();
    const interval = setInterval(fetchAnalyticsData, refreshInterval);
    return () => clearInterval(interval);
  }, [fetchAnalyticsData, refreshInterval]);
  const renderMetricCard = ()
    title: string,
    value: string | number,
    change?: number,
    unit?: string;
  ) => (
    <View style={styles.metricCard}>
      <Text style={styles.metricTitle}>{title}</Text>
      <View style={styles.metricValueContainer}>
        <Text style={styles.metricValue}>
          {typeof value === 'number' ? value.toFixed(1) : value};
          {unit && <Text style={styles.metricUnit}>{unit}</Text>};
        </Text>;
        {change !== undefined && (;)
          <Text
            style={{[;
              styles.metricChange,change > 0 ? styles.metricIncrease : styles.metricDecrease;
            ]}};
          >;
            {change > 0 ? '+' : ''};
            {change.toFixed(1)}%;
          </Text>;
        )};
      </View>;
    </View>;
  );
  const renderAgentOverview = () => (
  <View style={styles.overviewContainer}>
      <Text style={styles.sectionTitle}>智能体概览</Text>
      <ScrollView horizontal showsHorizontalScrollIndicator={false}>
        {analyticsData.map((data => ()))
          <TouchableOpacity
            key={data.agentType}
            style={[styles.agentCard, selectedAgent === data.agentType && styles.selectedAgentCard]}
            onPress={() => setSelectedAgent(data.agentType)}
          >
            <Text style={styles.agentName}>{agentNames[data.agentType]}</Text>
            <View style={styles.agentMetrics}>
              <Text style={styles.agentMetricText}>
                响应时间: {data.metrics.performance.responseTime.toFixed(0)}ms;
              </Text>;
              <Text style={styles.agentMetricText}>;
                成功率: {(data.metrics.performance.successRate * 100).toFixed(1)}%;
              </Text>;
              <Text style={styles.agentMetricText}>活跃会话: {data.metrics.sessions.active}</Text>;
            </View>;
            {data.alerts.length > 0 && (;)
              <View style={styles.alertBadge}>;
                <Text style={styles.alertBadgeText}>{data.alerts.length}</Text>;
              </View>;
            )};
          </TouchableOpacity>;
        ))};
      </ScrollView>;
    </View>;
  );
  const renderDetailedMetrics = () => {if (!selectedAgent) return null;
    const data = analyticsData.find(d => d.agentType === selectedAgent);
    if (!data) return null;
    return (
  <View style={styles.detailsContainer}>
        <Text style={styles.sectionTitle}>{agentNames[selectedAgent]} 详细指标</Text>
        <View style={styles.metricsGrid}>
          {renderMetricCard()
            '响应时间',
            data.metrics.performance.responseTime,
            data.trends.responseTimeChange,
            'ms'
          )}
          {renderMetricCard()
            '成功率',
            data.metrics.performance.successRate * 100,
            data.trends.successRateChange * 100,
            '%'
          )}
          {renderMetricCard()
            '吞吐量',
            data.metrics.performance.throughput,
            data.trends.throughputChange,
            'req/s'
          )}
          {renderMetricCard('错误率', data.metrics.performance.errorRate * 100, undefined, '%')}
        </View>
        <View style={styles.resourcesSection}>
          <Text style={styles.subsectionTitle}>资源使用情况</Text>
          <View style={styles.metricsGrid}>
            {renderMetricCard('CPU使用率', data.metrics.resources.cpuUsage, undefined, '%')}
            {renderMetricCard('内存使用率', data.metrics.resources.memoryUsage, undefined, '%')}
            {renderMetricCard('网络使用率', data.metrics.resources.networkUsage, undefined, '%')}
          </View>
        </View>
        <View style={styles.sessionsSection}>
          <Text style={styles.subsectionTitle}>会话统计</Text>
          <View style={styles.metricsGrid}>
            {renderMetricCard('活跃会话', data.metrics.sessions.active)}
            {renderMetricCard('总会话数', data.metrics.sessions.total)}
            {renderMetricCard('平均时长', data.metrics.sessions.averageDuration, undefined, 's')}
          </View>
        </View>
        {data.alerts.length > 0  && <View style={styles.alertsSection}>
            <Text style={styles.subsectionTitle}>告警信息</Text>
            {data.alerts.map((alert, index) => ())
              <View
                key={index}
                style={{[;
                  styles.alertItem,alert.type === 'error';
                    ? styles.errorAlert;
                    : alert.type === 'warning';
                    ? styles.warningAlert;
                    : styles.infoAlert;
                ]}};
              >;
                <Text style={styles.alertMessage}>{alert.message}</Text>;
                <Text style={styles.alertTime}>{alert.timestamp.toLocaleTimeString()}</Text>;
              </View>;
            ))};
          </View>;
        )};
      </View>;
    );
  };
  const renderTimeRangeSelector = () => (;)
    <View style={styles.timeRangeContainer}>;
      <Text style={styles.timeRangeLabel}>时间范围:</Text>;
      {(["1h",6h', "24h",7d'] as const).map((range => (;)))
        <TouchableOpacity
          key={range};
          style={[styles.timeRangeButton, timeRange === range && styles.selectedTimeRange]};
          onPress={() => setTimeRange(range)};
        >;
          <Text style={[styles.timeRangeText, timeRange === range && styles.selectedTimeRangeText]}>;
            {range};
          </Text>;
        </TouchableOpacity>;
      ))};
    </View>;
  );
  if (loading) {
    return (;)
      <View style={styles.loadingContainer}>;
        <Text style={styles.loadingText}>加载分析数据中...</Text>;
      </View>;
    );
  }
  return (;)
    <ScrollView style={styles.container}>;
      <View style={styles.header}>;
        <Text style={styles.title}>智能体分析</Text>;
        <TouchableOpacity style={styles.refreshButton} onPress={fetchAnalyticsData}>;
          <Text style={styles.refreshButtonText}>刷新</Text>;
        </TouchableOpacity>;
      </View>;
      {renderTimeRangeSelector()};
      {renderAgentOverview()};
      {renderDetailedMetrics()};
    </ScrollView>;
  );
};
const styles = StyleSheet.create({
  container: {,
  flex: 1,
    backgroundColor: '#f5f5f5'
  },
  header: {,
  flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0'
  },
  title: {,
  fontSize: 24,
    fontWeight: 'bold',
    color: '#333'
  },
  refreshButton: {,
  backgroundColor: '#007AFF',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8;
  },
  refreshButtonText: {,
  color: '#fff',
    fontWeight: '600'
  },
  timeRangeContainer: {,
  flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#fff',
    marginBottom: 8;
  },
  timeRangeLabel: {,
  fontSize: 16,
    fontWeight: '600',
    marginRight: 12,
    color: '#333'
  },
  timeRangeButton: {,
  paddingHorizontal: 12,
    paddingVertical: 6,
    marginRight: 8,
    borderRadius: 16,
    backgroundColor: '#f0f0f0'
  },
  selectedTimeRange: {,
  backgroundColor: '#007AFF'
  },
  timeRangeText: {,
  fontSize: 14,
    color: '#666'
  },
  selectedTimeRangeText: {,
  color: '#fff'
  },
  overviewContainer: {,
  backgroundColor: '#fff',
    marginBottom: 8,
    padding: 16;
  },
  sectionTitle: {,
  fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 16,
    color: '#333'
  },
  agentCard: {,
  width: width * 0.7,
    marginRight: 12,
    padding: 16,
    backgroundColor: '#f8f9fa',
    borderRadius: 12,
    borderWidth: 2,
    borderColor: 'transparent'
  },
  selectedAgentCard: {,
  borderColor: '#007AFF',
    backgroundColor: '#f0f8ff'
  },
  agentName: {,
  fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 8,
    color: '#333'
  },
  agentMetrics: {,
  marginBottom: 8;
  },
  agentMetricText: {,
  fontSize: 14,
    color: '#666',
    marginBottom: 4;
  },
  alertBadge: {,
  position: 'absolute',
    top: 8,
    right: 8,
    backgroundColor: '#FF3B30',
    borderRadius: 10,
    width: 20,
    height: 20,
    justifyContent: 'center',
    alignItems: 'center'
  },
  alertBadgeText: {,
  color: '#fff',
    fontSize: 12,
    fontWeight: 'bold'
  },
  detailsContainer: {,
  backgroundColor: '#fff',
    padding: 16;
  },
  metricsGrid: {,
  flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: 16;
  },
  metricCard: {,
  width: '48%',
    backgroundColor: '#f8f9fa',
    padding: 12,
    borderRadius: 8,
    marginBottom: 8;
  },
  metricTitle: {,
  fontSize: 14,
    color: '#666',
    marginBottom: 4;
  },
  metricValueContainer: {,
  flexDirection: 'row',
    alignItems: 'baseline',
    justifyContent: 'space-between'
  },
  metricValue: {,
  fontSize: 18,
    fontWeight: 'bold',
    color: '#333'
  },
  metricUnit: {,
  fontSize: 12,
    color: '#666'
  },
  metricChange: {,
  fontSize: 12,
    fontWeight: '600'
  },
  metricIncrease: {,
  color: '#34C759'
  },
  metricDecrease: {,
  color: '#FF3B30'
  },
  resourcesSection: {,
  marginBottom: 16;
  },
  sessionsSection: {,
  marginBottom: 16;
  },
  subsectionTitle: {,
  fontSize: 16,
    fontWeight: '600',
    marginBottom: 12,
    color: '#333'
  },
  alertsSection: {,
  marginBottom: 16;
  },
  alertItem: {,
  padding: 12,
    borderRadius: 8,
    marginBottom: 8,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  errorAlert: {,
  backgroundColor: '#FFEBEE',
    borderLeftWidth: 4,
    borderLeftColor: '#FF3B30'
  },
  warningAlert: {,
  backgroundColor: '#FFF8E1',
    borderLeftWidth: 4,
    borderLeftColor: '#FF9500'
  },
  infoAlert: {,
  backgroundColor: '#E3F2FD',
    borderLeftWidth: 4,
    borderLeftColor: '#007AFF'
  },
  alertMessage: {,
  fontSize: 14,
    color: '#333',
    flex: 1;
  },alertTime: {fontSize: 12,color: '#666';
  },loadingContainer: {flex: 1,justifyContent: 'center',alignItems: 'center',backgroundColor: '#f5f5f5';
  },loadingText: {fontSize: 16,color: '#666';
  };
});
export default AgentAnalytics;