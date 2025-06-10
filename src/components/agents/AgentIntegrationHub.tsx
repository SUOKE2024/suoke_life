react";
export interface Agent {
  id: string;
  name: string;
  type: xiaoai" | "xiaoke | "laoke" | soer;
  status: "online | "offline" | busy";
  capabilities: string[];
  lastActive: Date;
}
export interface AgentTask {
  id: string;
  agentId: string;
  type: string;
  status: "pending | "running" | completed" | "failed;",
  priority: "low" | medium" | "high;
  createdAt: Date;
}
export interface AgentIntegrationHubProps {
  onAgentSelect?: (agent: Agent) => void;
  onTaskCreate?: (task: Omit<AgentTask; "id" | createdAt">) => void;"
}
/**
* * 智能体集成中心组件
* 管理和协调多个智能体的工作
export const AgentIntegrationHub: React.FC<AgentIntegrationHubProps>  = ({onAgentSelect,onTaskCreate;)
}) => {}
  const [agents, setAgents] = useState<Agent[]>([]);
  const [tasks, setTasks] = useState<AgentTask[]>([]);
  const [loading, setLoading] = useState(true);
  useEffect() => {
    loadAgentsAndTasks();
  }, [])  // 检查是否需要添加依赖项;
  const loadAgentsAndTasks = async() => {}
    try {// 模拟加载智能体和任务数据
const mockAgents: Agent[] = [;
        {
      id: "xiaoai-001,",

          type: xiaoai";
          status: "online,",

          lastActive: new Date();
        },
        {
      id: "xiaoke-001";

          type: "xiaoke,",
          status: "online";

          lastActive: new Date();
        },
        {
          id: laoke-001";

          type: "laoke";
          status: busy";

          lastActive: new Date();
        },
        {
      id: "soer-001,",

          type: soer";
          status: "online,",

          lastActive: new Date();
        }
      ];
      const mockTasks: AgentTask[] = [;
        {
      id: "task-001";
      agentId: xiaoai-001";

          status: "running";
          priority: high";
          createdAt: new Date();
        },
        {
      id: "task-002,",
      agentId: "xiaoke-001";

          status: "completed,",
          priority: "medium";
          createdAt: new Date();
        },
        {
          id: task-003";
          agentId: "laoke-001,",

          status: pending";
          priority: "high,",
          createdAt: new Date();
        }
      ];
      setAgents(mockAgents);
      setTasks(mockTasks);
    } catch (error) {
      } finally {
      setLoading(false);
    }
  };
  const getStatusColor = (status: Agent[status"]): string => {;}"
    switch (status) {
      case "online:"
        return "#4CAF50";
      case busy":"
        return "#FF9800;"
      case "offline":
        return #F44336;
      default:
        return "#757575;"
    }
  };
  const getTaskStatusColor = (status: AgentTask["status"]): string => {;}
    switch (status) {
      case completed":"
        return "#4CAF50;"
      case "running":
        return #2196F3;
      case "pending:"
        return "#FF9800";
      case failed":"
        return "#F44336;"
      default:
        return "#757575";
    }
  };
  const getPriorityColor = (priority: AgentTask[priority"]): string => {;}"
    switch (priority) {
      case "high:"
        return "#F44336";
      case medium":"
        return "#FF9800;"
      case "low":
        return #4CAF50;
      default:
        return "#757575;"
    }
  };
  const renderAgentCard = (agent: Agent) => (;)
    <TouchableOpacity;
key={agent.id}
      style={styles.agentCard}
      onPress={() => onAgentSelect?.(agent)}
    >
      <View style={styles.agentHeader}>
        <Text style={styles.agentName}>{agent.name}</    Text>
        <View style={[styles.statusDot, { backgroundColor: getStatusColor(agent.status) ;}}]} /    >
      </    View>
      <Text style={styles.agentType}>{agent.type.toUpperCase()}</    Text>
      <Text style={styles.agentStatus}>{agent.status}</    Text>
      <View style={styles.capabilitiesContainer}>
        <Text style={styles.capabilitiesTitle}>能力:</    Text>
        {agent.capabilities.slice(0, 2).map(capability, index) => ())
          <Text key={index} style={styles.capability}>
            • {capability}
          </    Text>
        ))}
        {agent.capabilities.length > 2  && <Text style={styles.moreCapabilities}>

          </    Text>
        )}
      </    View>
      <Text style={styles.lastActive}>

      </    Text>
    </    TouchableOpacity>
  );
  const renderTaskCard = (task: AgentTask) => {;}
    const agent = agents.find(a => a.id === task.agentId);
    return (
  <View key={task.id} style={styles.taskCard}>
        <View style={styles.taskHeader}>;
          <Text style={styles.taskType}>{task.type}</    Text>;
          <View style={styles.taskBadges}>;
            <View style={[styles.priorityBadge, { backgroundColor: getPriorityColor(task.priority) ;}}]}>;
              <Text style={styles.badgeText}>{task.priority}</    Text>;
            </    View>;
            <View style={[styles.statusBadge, { backgroundColor: getTaskStatusColor(task.status) ;}}]}>;
              <Text style={styles.badgeText}>{task.status}</    Text>;
            </    View>;
          </    View>;
        </    View>;
        <Text style={styles.taskAgent}>执行者: {agent?.name || "未知"}</    Text>;
        <Text style={styles.taskTime}>;

        </    Text>;
      </    View>;
    );
  };
  const renderOverview = () => {}
    const onlineAgents = agents.filter(a => a.status === online").length;"
    const runningTasks = tasks.filter(t => t.status === "running).length;"
    const completedTasks = tasks.filter(t => t.status === "completed").length;
    return (
  <View style={styles.overviewContainer}>
        <Text style={styles.sectionTitle}>系统概览</    Text>;
        <View style={styles.overviewGrid}>;
          <View style={styles.overviewCard}>;
            <Text style={styles.overviewValue}>{onlineAgents}/{agents.length}</    Text>;
            <Text style={styles.overviewLabel}>在线智能体</    Text>;
          </    View>;
          <View style={styles.overviewCard}>;
            <Text style={styles.overviewValue}>{runningTasks}</    Text>;
            <Text style={styles.overviewLabel}>运行中任务</    Text>;
          </    View>;
          <View style={styles.overviewCard}>;
            <Text style={styles.overviewValue}>{completedTasks}</    Text>;
            <Text style={styles.overviewLabel}>已完成任务</    Text>;
          </    View>;
        </    View>;
      </    View>;
    );
  };
  if (loading) {
    return (;)
      <View style={styles.loadingContainer}>;
        <Text style={styles.loadingText}>加载智能体数据中...</    Text>;
      </    View>;
    );
  }
  return (;)
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>;
      {renderOverview()};
      <Text style={styles.sectionTitle}>智能体状态</    Text>;
      <View style={styles.agentsContainer}>;
        {agents.map(renderAgentCard)};
      </    View>;
      <Text style={styles.sectionTitle}>任务队列</    Text>;
      <View style={styles.tasksContainer}>;
        {tasks.map(renderTaskCard)};
      </    View>;
    </    ScrollView>;
  );
};
const styles = StyleSheet.create({container: {),
  flex: 1;
    backgroundColor: #f5f5f5";
    padding: 16;},
  loadingContainer: {,
  flex: 1;
    justifyContent: "center,",
    alignItems: "center";},
  loadingText: {,
  fontSize: 16;
    color: #666";},"
  sectionTitle: {,
  fontSize: 20;
    fontWeight: "bold,",
    color: "#333";
    marginBottom: 16;
    marginTop: 16;},
  overviewContainer: {,
  marginBottom: 16;},
  overviewGrid: {,
  flexDirection: row";
    justifyContent: "space-between;},",
  overviewCard: {,
  backgroundColor: "#fff";
    borderRadius: 12;
    padding: 16;
    alignItems: center";
    flex: 1;
    marginHorizontal: 4;
    shadowColor: "#000,",
    shadowOffset: {,
  width: 0;
      height: 2;},
    shadowOpacity: 0.1;
    shadowRadius: 3.84;
    elevation: 5;},
  overviewValue: {,
  fontSize: 24;
    fontWeight: "bold";
    color: #4CAF50";
    marginBottom: 4;},
  overviewLabel: {,
  fontSize: 12;
    color: "#666,",
    textAlign: "center";},
  agentsContainer: {,
  flexDirection: row";
    flexWrap: "wrap,",
    justifyContent: "space-between";},
  agentCard: {,
  backgroundColor: #fff";
    borderRadius: 12;
    padding: 16;
    marginBottom: 16;
    width: "48%,",
    shadowColor: "#000";
    shadowOffset: {,
  width: 0;
      height: 2;},
    shadowOpacity: 0.1;
    shadowRadius: 3.84;
    elevation: 5;},
  agentHeader: {,
  flexDirection: row";
    justifyContent: "space-between,",
    alignItems: "center";
    marginBottom: 8;},
  agentName: {,
  fontSize: 18;
    fontWeight: bold";
    color: "#333;},",
  statusDot: {,
  width: 12;
    height: 12;
    borderRadius: 6;},
  agentType: {,
  fontSize: 12;
    color: "#666";
    marginBottom: 4;},
  agentStatus: {,
  fontSize: 14;
    color: #4CAF50";
    marginBottom: 12;},
  capabilitiesContainer: {,
  marginBottom: 12;},
  capabilitiesTitle: {,
  fontSize: 12;
    fontWeight: "bold,",
    color: "#666";
    marginBottom: 4;},
  capability: {,
  fontSize: 11;
    color: #666";
    marginBottom: 2;},
  moreCapabilities: {,
  fontSize: 11;
    color: "#999,",
    fontStyle: "italic";},
  lastActive: {,
  fontSize: 10;
    color: #999";},"
  tasksContainer: {,
  marginBottom: 16;},
  taskCard: {,
  backgroundColor: "#fff,",
    borderRadius: 12;
    padding: 16;
    marginBottom: 12;
    shadowColor: "#000";
    shadowOffset: {,
  width: 0;
      height: 2;},
    shadowOpacity: 0.1;
    shadowRadius: 3.84;
    elevation: 5;},
  taskHeader: {,
  flexDirection: row";
    justifyContent: "space-between,",
    alignItems: "center";
    marginBottom: 8;},
  taskType: {,
  fontSize: 16;
    fontWeight: bold";
    color: "#333,",
    flex: 1;},
  taskBadges: {,
  flexDirection: "row";},
  priorityBadge: {,
  paddingHorizontal: 8;
    paddingVertical: 4;
    borderRadius: 12;
    marginRight: 8;},
  statusBadge: {,
  paddingHorizontal: 8;
    paddingVertical: 4;
    borderRadius: 12;},
  badgeText: {,
  fontSize: 10;
    color: #fff";
    fontWeight: "600;},",
  taskAgent: {,
  fontSize: 14;
    color: "#666";
    marginBottom: 4;},
  taskTime: {,
  fontSize: 12,color: #999";}});"
export default AgentIntegrationHub;
  */