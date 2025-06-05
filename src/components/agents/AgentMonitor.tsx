import React, { useState, useEffect, useCallback } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  TouchableOpacity,
  Alert,
  Dimensions,
} from "react-native";
import { AgentType, AgentHealthStatus } from "../../agents/types";
import {
  getAgentStatus,
  getAgentMetrics,
  AgentSystemUtils,
} from "../../agents";
import { AgentMetrics } from "../../agents/AgentManager";

/**
 * 智能体监控属性
 */
interface AgentMonitorProps {
  refreshInterval?: number;
  onAgentError?: (agentType: AgentType, error: string) => void;
  style?: any;
}

/**
 * 状态卡片属性
 */
interface StatusCardProps {
  agentType: AgentType;
  status: AgentHealthStatus;
  metrics?: AgentMetrics;
  onRestart?: () => void;
}

/**
 * 状态卡片组件
 */
const StatusCard: React.FC<StatusCardProps> = ({
  agentType,
  status,
  metrics,
  onRestart,
}) => {
  const agentRole = AgentSystemUtils.getAgentRole(agentType);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "healthy":
        return "#4CAF50";
      case "degraded":
        return "#FF9800";
      case "unhealthy":
        return "#F44336";
      case "offline":
        return "#9E9E9E";
      default:
        return "#9E9E9E";
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case "healthy":
        return "健康";
      case "degraded":
        return "降级";
      case "unhealthy":
        return "异常";
      case "offline":
        return "离线";
      default:
        return "未知";
    }
  };

  return (
    <View style={styles.statusCard}>
      <View style={styles.cardHeader}>
        <View>
          <Text style={styles.agentName}>{agentRole.name}</Text>
          <Text style={styles.agentTitle}>{agentRole.title}</Text>
        </View>
        <View
          style={[
            styles.statusIndicator,
            { backgroundColor: getStatusColor(status.status) },
          ]}
        >
          <Text style={styles.statusText}>{getStatusText(status.status)}</Text>
        </View>
      </View>

      <View style={styles.metricsContainer}>
        <View style={styles.metricRow}>
          <Text style={styles.metricLabel}>负载:</Text>
          <Text style={styles.metricValue}>
            {(status.load * 100).toFixed(1)}%
          </Text>
        </View>
        <View style={styles.metricRow}>
          <Text style={styles.metricLabel}>响应时间:</Text>
          <Text style={styles.metricValue}>{status.responseTime}ms</Text>
        </View>
        <View style={styles.metricRow}>
          <Text style={styles.metricLabel}>错误率:</Text>
          <Text style={styles.metricValue}>
            {(status.errorRate * 100).toFixed(1)}%
          </Text>
        </View>
        {metrics && (
          <>
            <View style={styles.metricRow}>
              <Text style={styles.metricLabel}>处理任务:</Text>
              <Text style={styles.metricValue}>{metrics.tasksProcessed}</Text>
            </View>
            <View style={styles.metricRow}>
              <Text style={styles.metricLabel}>成功率:</Text>
              <Text style={styles.metricValue}>
                {(metrics.successRate * 100).toFixed(1)}%
              </Text>
            </View>
            <View style={styles.metricRow}>
              <Text style={styles.metricLabel}>运行时间:</Text>
              <Text style={styles.metricValue}>
                {Math.floor(metrics.uptime / 60)}分钟
              </Text>
            </View>
          </>
        )}
      </View>

      <View style={styles.capabilitiesContainer}>
        <Text style={styles.capabilitiesTitle}>能力:</Text>
        <View style={styles.capabilitiesList}>
          {status.capabilities.slice(0, 3).map((capability, index) => (
            <Text key={index} style={styles.capabilityTag}>
              {capability}
            </Text>
          ))}
          {status.capabilities.length > 3 && (
            <Text style={styles.capabilityTag}>
              +{status.capabilities.length - 3}
            </Text>
          )}
        </View>
      </View>

      {status.status === "unhealthy" && onRestart && (
        <TouchableOpacity style={styles.restartButton} onPress={onRestart}>
          <Text style={styles.restartButtonText}>重启</Text>
        </TouchableOpacity>
      )}

      <Text style={styles.lastCheck}>
        最后检查: {status.lastCheck.toLocaleTimeString()}
      </Text>
    </View>
  );
};

/**
 * 智能体监控组件
 * 显示智能体系统的健康状态和性能指标
 */
export const AgentMonitor: React.FC<AgentMonitorProps> = ({
  refreshInterval = 30000,
  onAgentError,
  style,
}) => {
  const [agentStatuses, setAgentStatuses] = useState<
    Map<AgentType, AgentHealthStatus>
  >(new Map());
  const [agentMetrics, setAgentMetrics] = useState<
    Map<AgentType, AgentMetrics>
  >(new Map());
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const [systemOverview, setSystemOverview] = useState<any>(null);

  /**
   * 获取智能体状态
   */
  const fetchAgentStatuses = useCallback(async () => {
    try {
      const statuses = (await getAgentStatus()) as Map<
        AgentType,
        AgentHealthStatus
      >;
      const metrics = (await getAgentMetrics()) as Map<AgentType, AgentMetrics>;

      setAgentStatuses(statuses);
      setAgentMetrics(metrics);
      setLastUpdate(new Date());

      // 检查错误状态
      for (const [agentType, status] of statuses) {
        if (status.status === "unhealthy" && onAgentError) {
          onAgentError(agentType, `智能体 ${agentType} 状态异常`);
        }
      }

      // 生成系统概览
      generateSystemOverview(statuses, metrics);
    } catch (error) {
      console.error("获取智能体状态失败:", error);
    }
  }, [onAgentError]);

  /**
   * 生成系统概览
   */
  const generateSystemOverview = useCallback(
    (
      statuses: Map<AgentType, AgentHealthStatus>,
      metrics: Map<AgentType, AgentMetrics>
    ) => {
      const totalAgents = statuses.size;
      const healthyAgents = Array.from(statuses.values()).filter(
        (s) => s.status === "healthy"
      ).length;
      const totalTasks = Array.from(metrics.values()).reduce(
        (sum, m) => sum + m.tasksProcessed,
        0
      );
      const avgResponseTime =
        Array.from(statuses.values()).reduce(
          (sum, s) => sum + s.responseTime,
          0
        ) / totalAgents;
      const avgSuccessRate =
        Array.from(metrics.values()).reduce(
          (sum, m) => sum + m.successRate,
          0
        ) / totalAgents;

      setSystemOverview({
        totalAgents,
        healthyAgents,
        totalTasks,
        avgResponseTime: Math.round(avgResponseTime),
        avgSuccessRate: (avgSuccessRate * 100).toFixed(1),
        systemHealth: healthyAgents / totalAgents,
      });
    },
    []
  );

  /**
   * 刷新数据
   */
  const handleRefresh = useCallback(async () => {
    setIsRefreshing(true);
    await fetchAgentStatuses();
    setIsRefreshing(false);
  }, [fetchAgentStatuses]);

  /**
   * 重启智能体
   */
  const handleAgentRestart = useCallback(
    (agentType: AgentType) => {
      Alert.alert(
        "重启智能体",
        `确定要重启 ${AgentSystemUtils.getAgentRole(agentType).name} 吗？`,
        [
          { text: "取消", style: "cancel" },
          {
            text: "确定",
            onPress: async () => {
              try {
                // 这里应该调用重启API
                console.log(`重启智能体: ${agentType}`);
                await fetchAgentStatuses();
              } catch (error) {
                Alert.alert("错误", "重启失败，请稍后再试");
              }
            },
          },
        ]
      );
    },
    [fetchAgentStatuses]
  );

  /**
   * 渲染系统概览
   */
  const renderSystemOverview = useCallback(() => {
    if (!systemOverview) {return null;}

    const healthColor =
      systemOverview.systemHealth > 0.8
        ? "#4CAF50"
        : systemOverview.systemHealth > 0.5
        ? "#FF9800"
        : "#F44336";

    return (
      <View style={styles.overviewCard}>
        <Text style={styles.overviewTitle}>系统概览</Text>
        <View style={styles.overviewGrid}>
          <View style={styles.overviewItem}>
            <Text style={styles.overviewValue}>
              {systemOverview.healthyAgents}/{systemOverview.totalAgents}
            </Text>
            <Text style={styles.overviewLabel}>健康智能体</Text>
          </View>
          <View style={styles.overviewItem}>
            <Text style={styles.overviewValue}>
              {systemOverview.totalTasks}
            </Text>
            <Text style={styles.overviewLabel}>总处理任务</Text>
          </View>
          <View style={styles.overviewItem}>
            <Text style={styles.overviewValue}>
              {systemOverview.avgResponseTime}ms
            </Text>
            <Text style={styles.overviewLabel}>平均响应时间</Text>
          </View>
          <View style={styles.overviewItem}>
            <Text style={styles.overviewValue}>
              {systemOverview.avgSuccessRate}%
            </Text>
            <Text style={styles.overviewLabel}>平均成功率</Text>
          </View>
        </View>
        <View
          style={[styles.healthIndicator, { backgroundColor: healthColor }]}
        >
          <Text style={styles.healthText}>
            系统健康度: {(systemOverview.systemHealth * 100).toFixed(0)}%
          </Text>
        </View>
      </View>
    );
  }, [systemOverview]);

  useEffect(() => {
    // 初始加载
    fetchAgentStatuses();

    // 设置定时刷新
    const interval = setInterval(fetchAgentStatuses, refreshInterval);

    return () => clearInterval(interval);
  }, [fetchAgentStatuses, refreshInterval]);

  return (
    <ScrollView
      style={[styles.container, style]}
      refreshControl={
        <RefreshControl refreshing={isRefreshing} onRefresh={handleRefresh} />
      }
    >
      {/* 系统概览 */}
      {renderSystemOverview()}

      {/* 智能体状态卡片 */}
      <View style={styles.agentsContainer}>
        <Text style={styles.sectionTitle}>智能体状态</Text>
        {Array.from(agentStatuses.entries()).map(([agentType, status]) => (
          <StatusCard
            key={agentType}
            agentType={agentType}
            status={status}
            metrics={agentMetrics.get(agentType)}
            onRestart={() => handleAgentRestart(agentType)}
          />
        ))}
      </View>

      {/* 最后更新时间 */}
      <View style={styles.footer}>
        <Text style={styles.lastUpdateText}>
          最后更新: {lastUpdate.toLocaleString()}
        </Text>
      </View>
    </ScrollView>
  );
};

const { width } = Dimensions.get("window");

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#f5f5f5",
  },
  overviewCard: {
    backgroundColor: "#fff",
    margin: 15,
    padding: 20,
    borderRadius: 12,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  overviewTitle: {
    fontSize: 18,
    fontWeight: "bold",
    color: "#333",
    marginBottom: 15,
  },
  overviewGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    justifyContent: "space-between",
  },
  overviewItem: {
    width: "48%",
    alignItems: "center",
    marginBottom: 15,
  },
  overviewValue: {
    fontSize: 24,
    fontWeight: "bold",
    color: "#007AFF",
  },
  overviewLabel: {
    fontSize: 12,
    color: "#666",
    marginTop: 5,
  },
  healthIndicator: {
    padding: 10,
    borderRadius: 8,
    alignItems: "center",
    marginTop: 10,
  },
  healthText: {
    color: "#fff",
    fontWeight: "bold",
  },
  agentsContainer: {
    paddingHorizontal: 15,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "bold",
    color: "#333",
    marginBottom: 15,
  },
  statusCard: {
    backgroundColor: "#fff",
    padding: 15,
    borderRadius: 12,
    marginBottom: 15,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  cardHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 15,
  },
  agentName: {
    fontSize: 16,
    fontWeight: "bold",
    color: "#333",
  },
  agentTitle: {
    fontSize: 12,
    color: "#666",
    marginTop: 2,
  },
  statusIndicator: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 15,
  },
  statusText: {
    color: "#fff",
    fontSize: 12,
    fontWeight: "bold",
  },
  metricsContainer: {
    marginBottom: 15,
  },
  metricRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 8,
  },
  metricLabel: {
    fontSize: 14,
    color: "#666",
  },
  metricValue: {
    fontSize: 14,
    fontWeight: "600",
    color: "#333",
  },
  capabilitiesContainer: {
    marginBottom: 15,
  },
  capabilitiesTitle: {
    fontSize: 14,
    fontWeight: "600",
    color: "#333",
    marginBottom: 8,
  },
  capabilitiesList: {
    flexDirection: "row",
    flexWrap: "wrap",
  },
  capabilityTag: {
    backgroundColor: "#f0f0f0",
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    fontSize: 12,
    color: "#666",
    marginRight: 8,
    marginBottom: 4,
  },
  restartButton: {
    backgroundColor: "#FF9800",
    paddingVertical: 8,
    paddingHorizontal: 15,
    borderRadius: 8,
    alignSelf: "flex-start",
    marginBottom: 10,
  },
  restartButtonText: {
    color: "#fff",
    fontSize: 14,
    fontWeight: "bold",
  },
  lastCheck: {
    fontSize: 12,
    color: "#999",
    textAlign: "right",
  },
  footer: {
    padding: 20,
    alignItems: "center",
  },
  lastUpdateText: {
    fontSize: 12,
    color: "#999",
  },
});

export default AgentMonitor;
