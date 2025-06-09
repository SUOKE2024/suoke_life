import {import { AgentType } from "../../types/agents";
import { agentApiService } from "../../services/api/agentApiService";
import AgentMonitor from "./AgentMonitor";
import AgentAnalytics from "./AgentAnalytics";
import React, { useState, useEffect } from "react";
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Dimensions,
  RefreshControl,
  Alert;
} from "react-native";
interface AgentDashboardProps {
  initialTab?: "monitor" | "analytics" | "chat";
}
interface QuickAction {
  id: string;,
  title: string;
  description: string;,
  agentType: AgentType;
  action: () => void;,
  icon: string;
  color: string;
}
const { width } = Dimensions.get("window");
const AgentDashboard: React.FC<AgentDashboardProps> = ({
  initialTab = "monitor"
}) => {
  const [activeTab, setActiveTab] = useState(initialTab);
  const [refreshing, setRefreshing] = useState(false);
  const [systemStatus, setSystemStatus] = useState<"healthy" | "warning" | "error">("healthy");
  const agentNames = {[AgentType.XIAOAI]: "小艾",[AgentType.XIAOKE]: "小克",[AgentType.LAOKE]: "老克",[AgentType.SOER]: "索儿";
  };
  const quickActions: QuickAction[] = [
    {
      id: "xiaoai-chat",
      title: "与小艾对话",
      description: "开始健康咨询和四诊服务",
      agentType: AgentType.XIAOAI,
      action: () => handleQuickAction("chat", AgentType.XIAOAI),
      icon: "💬",
      color: "#007AFF"
    },
    {
      id: "xiaoke-service",
      title: "小克服务",
      description: "预约挂号和服务管理",
      agentType: AgentType.XIAOKE,
      action: () => handleQuickAction("service", AgentType.XIAOKE),
      icon: "🏥",
      color: "#34C759"
    },
    {
      id: "laoke-knowledge",
      title: "老克知识库",
      description: "健康知识学习和查询",
      agentType: AgentType.LAOKE,
      action: () => handleQuickAction("knowledge", AgentType.LAOKE),
      icon: "📚",
      color: "#FF9500"
    },
    {
      id: "soer-lifestyle",
      title: "索儿生活管理",
      description: "健康数据和生活方式管理",
      agentType: AgentType.SOER,
      action: () => handleQuickAction("lifestyle", AgentType.SOER),
      icon: "🌱",
      color: "#FF3B30"
    }
  ];
  const handleQuickAction = (actionType: string, agentType: AgentType) => {Alert.alert(;)
      `${agentNames[agentType]}服务`,`即将启动${actionType}功能`,[;
        {
      text: "取消",
      style: "cancel" },{
      text: "确定", "
      onPress: () => {// 这里可以导航到具体的功能页面;
            console.log(`启动${agentNames[agentType]}的${actionType}功能`);
          }
        }
      ]
    );
  };
  const checkSystemHealth = async () => {try {const healthCheck = await agentApiService.healthCheck();
      if (healthCheck.success) {
        setSystemStatus("healthy");
      } else {
        setSystemStatus("warning");
      }
    } catch (error) {
      setSystemStatus("error");
    }
  };
  const onRefresh = async () => {setRefreshing(true);
    await checkSystemHealth();
    setRefreshing(false);
  };
  useEffect() => {
    checkSystemHealth();
    const interval = setInterval(checkSystemHealth, 60000); // 每分钟检查一次
    return () => clearInterval(interval);
  }, [])  // 检查是否需要添加依赖项;
  const renderSystemStatus = () => {const statusConfig = {healthy: {,
  color: "#34C759",
      text: "系统正常", icon: "✅" },warning: {,
  color: "#FF9500",
      text: "系统警告", icon: "⚠️" },error: {,
  color: "#FF3B30",
      text: "系统异常", icon: "❌" };
    };
    const config = statusConfig[systemStatus];
    return (;)
      <View style={[styles.statusCard, { borderLeftColor: config.color }}]}>;
        <View style={styles.statusHeader}>;
          <Text style={styles.statusIcon}>{config.icon}</Text>;
          <Text style={[styles.statusText, { color: config.color }}]}>;
            {config.text};
          </Text>;
        </View>;
        <Text style={styles.statusTime}>;
          最后更新: {new Date().toLocaleTimeString()};
        </Text>;
      </View>;
    );
  };
  const renderQuickActions = () => (
  <View style={styles.quickActionsContainer}>
      <Text style={styles.sectionTitle}>快速操作</Text>
      <View style={styles.actionsGrid}>
        {quickActions.map(action) => (;)
          <TouchableOpacity;
            key={action.id};
            style={[styles.actionCard, { borderLeftColor: action.color }}]};
            onPress={action.action};
            activeOpacity={0.7};
          >;
            <View style={styles.actionHeader}>;
              <Text style={styles.actionIcon}>{action.icon}</Text>;
              <Text style={styles.actionTitle}>{action.title}</Text>;
            </View>;
            <Text style={styles.actionDescription}>{action.description}</Text>;
          </TouchableOpacity>;
        ))};
      </View>;
    </View>;
  );
  const renderTabBar = () => (
  <View style={styles.tabBar}>
      <TouchableOpacity;
        style={[styles.tab, activeTab === "monitor" && styles.activeTab]}
        onPress={() => setActiveTab("monitor")}
      >
        <Text style={[
          styles.tabText,
          activeTab === "monitor" && styles.activeTabText;
        ]}}>
          监控
        </Text>
      </TouchableOpacity>
      <TouchableOpacity;
        style={[styles.tab, activeTab === "analytics" && styles.activeTab]}
        onPress={() => setActiveTab("analytics")}
      >
        <Text style={[
          styles.tabText,
          activeTab === "analytics" && styles.activeTabText;
        ]}}>;
          分析;
        </Text>;
      </TouchableOpacity>;
      <TouchableOpacity;
        style={[styles.tab, activeTab === "chat" && styles.activeTab]};
        onPress={() => setActiveTab("chat")};
      >;
        <Text style={[;
          styles.tabText,activeTab === "chat" && styles.activeTabText;
        ]}}>;
          对话;
        </Text>;
      </TouchableOpacity>;
    </View>;
  );
  const renderTabContent = () => {switch (activeTab) {case "monitor":return <AgentMonitor />;
      case "analytics":
        return <AgentAnalytics />;
      case "chat":
        return (;)
          <View style={styles.chatContainer}>;
            <Text style={styles.chatTitle}>智能体对话</Text>;
            <Text style={styles.chatDescription}>;
              选择一个智能体开始对话，或使用上方的快速操作;
            </Text>;
            {renderQuickActions()};
          </View>;
        );
      default:
        return null;
    }
  };
  return (
  <View style={styles.container}>
      <ScrollView;
        style={styles.scrollView};
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />;
        };
      >;
        <View style={styles.header}>;
          <Text style={styles.title}>索克生活智能体中心</Text>;
          <Text style={styles.subtitle}>四智能体协同健康管理平台</Text>;
        </View>;
        {renderSystemStatus()};
        {renderTabBar()};
        {renderTabContent()};
      </ScrollView>;
    </View>;
  );
};
const styles = StyleSheet.create({
  container: {,
  flex: 1,
    backgroundColor: "#f5f5f5"
  },
  scrollView: {,
  flex: 1;
  },
  header: {,
  backgroundColor: "#fff",
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: "#e0e0e0"
  },
  title: {,
  fontSize: 28,
    fontWeight: "bold",
    color: "#333",
    marginBottom: 4;
  },
  subtitle: {,
  fontSize: 16,
    color: "#666"
  },
  statusCard: {,
  backgroundColor: "#fff",
    margin: 16,
    padding: 16,
    borderRadius: 12,
    borderLeftWidth: 4,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3;
  },
  statusHeader: {,
  flexDirection: "row",
    alignItems: "center",
    marginBottom: 8;
  },
  statusIcon: {,
  fontSize: 20,
    marginRight: 8;
  },
  statusText: {,
  fontSize: 18,
    fontWeight: "600"
  },
  statusTime: {,
  fontSize: 14,
    color: "#666"
  },
  tabBar: {,
  flexDirection: "row",
    backgroundColor: "#fff",
    marginHorizontal: 16,
    marginBottom: 16,
    borderRadius: 12,
    padding: 4,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3;
  },
  tab: {,
  flex: 1,
    paddingVertical: 12,
    alignItems: "center",
    borderRadius: 8;
  },
  activeTab: {,
  backgroundColor: "#007AFF"
  },
  tabText: {,
  fontSize: 16,
    fontWeight: "600",
    color: "#666"
  },
  activeTabText: {,
  color: "#fff"
  },
  quickActionsContainer: {,
  backgroundColor: "#fff",
    margin: 16,
    padding: 16,
    borderRadius: 12,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3;
  },
  sectionTitle: {,
  fontSize: 20,
    fontWeight: "bold",
    color: "#333",
    marginBottom: 16;
  },
  actionsGrid: {,
  flexDirection: "row",
    flexWrap: "wrap",
    justifyContent: "space-between"
  },
  actionCard: {,
  width: "48%",
    backgroundColor: "#f8f9fa",
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    borderLeftWidth: 4;
  },
  actionHeader: {,
  flexDirection: "row",
    alignItems: "center",
    marginBottom: 8;
  },
  actionIcon: {,
  fontSize: 24,
    marginRight: 8;
  },
  actionTitle: {,
  fontSize: 16,
    fontWeight: "600",
    color: "#333",
    flex: 1;
  },
  actionDescription: {,
  fontSize: 14,
    color: "#666",
    lineHeight: 20;
  },
  chatContainer: {,
  backgroundColor: "#fff",
    margin: 16,
    padding: 20,
    borderRadius: 12,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,shadowRadius: 4,elevation: 3;
  },chatTitle: {fontSize: 24,fontWeight: "bold",color: "#333",marginBottom: 8;
  },chatDescription: {fontSize: 16,color: "#666",lineHeight: 24,marginBottom: 20;
  };
});
export default AgentDashboard;