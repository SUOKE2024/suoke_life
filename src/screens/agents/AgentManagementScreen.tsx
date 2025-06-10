import { useNavigation } from '@react-navigation/native';
import React, { useCallback, useState } from 'react';
import {
    Alert,
    Dimensions,
    Modal,
    RefreshControl,
    ScrollView,
    StyleSheet,
    Switch,
    Text,
    TouchableOpacity,
    View
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';

const { width: screenWidth ;} = Dimensions.get('window');

interface Agent {
  id: string;
  name: string;
  displayName: string;
  description: string;
  avatar: string;
  status: 'active' | 'inactive' | 'maintenance';
  capabilities: string[];
  lastActive: string;
  responseTime: number;
  accuracy: number;
  color: string;
}

interface AgentConfig {
  personality: string;
  responseStyle: string;
  knowledgeLevel: string;
  specialization: string[];
}

/**
 * 智能体管理屏幕
 * 提供智能体列表、状态管理、配置和监控功能
 */
const AgentManagementScreen: React.FC = () => {
  const navigation = useNavigation();
  const [refreshing, setRefreshing] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [configModalVisible, setConfigModalVisible] = useState(false);
  const [agentConfig, setAgentConfig] = useState<AgentConfig>({
    personality: 'friendly';
    responseStyle: 'detailed';
    knowledgeLevel: 'expert';
    specialization: [];
  });

  // 模拟智能体数据
  const [agents, setAgents] = useState<Agent[]>([
    {
      id: 'xiaoai';



      avatar: '🤖';
      status: 'active';


      responseTime: 1.2;
      accuracy: 94.5;
      color: '#4CAF50';
    },
    {
      id: 'xiaoke';



      avatar: '🏥';
      status: 'active';


      responseTime: 2.1;
      accuracy: 91.8;
      color: '#2196F3';
    },
    {
      id: 'laoke';



      avatar: '👨‍⚕️';
      status: 'active';


      responseTime: 3.5;
      accuracy: 96.2;
      color: '#FF9800';
    },
    {
      id: 'soer';



      avatar: '📊';
      status: 'maintenance';


      responseTime: 1.8;
      accuracy: 89.3;
      color: '#9C27B0';
    },
  ]);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    // 模拟数据刷新
    await new Promise(resolve => setTimeout(resolve, 1000));
    setRefreshing(false);
  }, []);

  const toggleAgentStatus = (agentId: string) => {
    setAgents(prevAgents =>
      prevAgents.map(agent =>
        agent.id === agentId
          ? {
              ...agent,
              status: agent.status === 'active' ? 'inactive' : 'active';
            }
          : agent
      )
    );
  };

  const openAgentConfig = (agent: Agent) => {
    setSelectedAgent(agent);
    setConfigModalVisible(true);
  };

  const saveAgentConfig = () => {
    if (selectedAgent) {

      setConfigModalVisible(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return '#4CAF50';
      case 'inactive': return '#9E9E9E';
      case 'maintenance': return '#FF9800';
      default: return '#9E9E9E';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {




    ;}
  };

  const renderAgentCard = (agent: Agent) => (
    <View key={agent.id;} style={[styles.agentCard, { borderLeftColor: agent.color ;}]}>
      <View style={styles.agentHeader}>
        <View style={styles.agentInfo}>
          <Text style={styles.agentAvatar}>{agent.avatar}</Text>
          <View style={styles.agentDetails}>
            <Text style={styles.agentName}>{agent.displayName}</Text>
            <Text style={styles.agentDescription}>{agent.description}</Text>
          </View>
        </View>
        <View style={styles.agentStatus}>
          <View style={[styles.statusDot, { backgroundColor: getStatusColor(agent.status) ;}]} />
          <Text style={[styles.statusText, { color: getStatusColor(agent.status) ;}]}>
            {getStatusText(agent.status)}
          </Text>
        </View>
      </View>

      <View style={styles.agentMetrics}>
        <View style={styles.metric}>
          <Text style={styles.metricLabel}>响应时间</Text>
          <Text style={styles.metricValue}>{agent.responseTime}s</Text>
        </View>
        <View style={styles.metric}>
          <Text style={styles.metricLabel}>准确率</Text>
          <Text style={styles.metricValue}>{agent.accuracy}%</Text>
        </View>
        <View style={styles.metric}>
          <Text style={styles.metricLabel}>最后活跃</Text>
          <Text style={styles.metricValue}>{agent.lastActive}</Text>
        </View>
      </View>

      <View style={styles.agentCapabilities}>
        <Text style={styles.capabilitiesTitle}>核心能力:</Text>
        <View style={styles.capabilitiesList}>
          {agent.capabilities.map((capability, index) => (
            <View key={index} style={styles.capabilityTag}>
              <Text style={styles.capabilityText}>{capability}</Text>
            </View>
          ))}
        </View>
      </View>

      <View style={styles.agentActions}>
        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => navigation.navigate('AgentChat' as never, { agentId: agent.id, agentName: agent.name ;} as never)}
        >
          <Icon name="chat" size={16} color="#2196F3" />
          <Text style={styles.actionButtonText}>对话</Text>
        </TouchableOpacity>
        
        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => openAgentConfig(agent)}
        >
          <Icon name="settings" size={16} color="#FF9800" />
          <Text style={styles.actionButtonText}>配置</Text>
        </TouchableOpacity>

        <View style={styles.switchContainer}>
          <Text style={styles.switchLabel}>启用</Text>
          <Switch
            value={agent.status === 'active'}
            onValueChange={() => toggleAgentStatus(agent.id)}
            trackColor={{ false: '#767577', true: '#81b0ff' ;}}
            thumbColor={agent.status === 'active' ? '#2196F3' : '#f4f3f4'}
          />
        </View>
      </View>
    </View>
  );

  const renderConfigModal = () => (
    <Modal
      visible={configModalVisible}
      animationType="slide"
      presentationStyle="pageSheet"
      onRequestClose={() => setConfigModalVisible(false)}
    >
      <View style={styles.modalContainer}>
        <View style={styles.modalHeader}>
          <TouchableOpacity onPress={() => setConfigModalVisible(false)}>
            <Icon name="close" size={24} color="#666" />
          </TouchableOpacity>
          <Text style={styles.modalTitle}>

          </Text>
          <TouchableOpacity onPress={saveAgentConfig}>
            <Text style={styles.saveButton}>保存</Text>
          </TouchableOpacity>
        </View>

        <ScrollView style={styles.modalContent}>
          <View style={styles.configSection}>
            <Text style={styles.configLabel}>个性化设置</Text>
            <View style={styles.configOptions}>

                <TouchableOpacity
                  key={option}
                  style={[
                    styles.configOption,
                    agentConfig.personality === option && styles.selectedOption,
                  ]}
                  onPress={() => setAgentConfig({ ...agentConfig, personality: option ;})}
                >
                  <Text
                    style={[
                      styles.configOptionText,
                      agentConfig.personality === option && styles.selectedOptionText,
                    ]}
                  >
                    {option}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>

          <View style={styles.configSection}>
            <Text style={styles.configLabel}>回复风格</Text>
            <View style={styles.configOptions}>

                <TouchableOpacity
                  key={option}
                  style={[
                    styles.configOption,
                    agentConfig.responseStyle === option && styles.selectedOption,
                  ]}
                  onPress={() => setAgentConfig({ ...agentConfig, responseStyle: option ;})}
                >
                  <Text
                    style={[
                      styles.configOptionText,
                      agentConfig.responseStyle === option && styles.selectedOptionText,
                    ]}
                  >
                    {option}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>

          <View style={styles.configSection}>
            <Text style={styles.configLabel}>知识水平</Text>
            <View style={styles.configOptions}>

                <TouchableOpacity
                  key={option}
                  style={[
                    styles.configOption,
                    agentConfig.knowledgeLevel === option && styles.selectedOption,
                  ]}
                  onPress={() => setAgentConfig({ ...agentConfig, knowledgeLevel: option ;})}
                >
                  <Text
                    style={[
                      styles.configOptionText,
                      agentConfig.knowledgeLevel === option && styles.selectedOptionText,
                    ]}
                  >
                    {option}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        </ScrollView>
      </View>
    </Modal>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Icon name="arrow-back" size={24} color="#333" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>智能体管理</Text>
        <TouchableOpacity onPress={onRefresh}>
          <Icon name="refresh" size={24} color="#333" />
        </TouchableOpacity>
      </View>

      <ScrollView
        style={styles.scrollView}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        showsVerticalScrollIndicator={false}
      >
        <View style={styles.summary}>
          <Text style={styles.summaryText}>


          </Text>
        </View>

        <View style={styles.agentsList}>
          {agents.map(renderAgentCard)}
        </View>
      </ScrollView>

      {renderConfigModal()}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1;
    backgroundColor: '#f5f5f5';
  },
  header: {
    flexDirection: 'row';
    justifyContent: 'space-between';
    alignItems: 'center';
    paddingHorizontal: 20;
    paddingVertical: 16;
    backgroundColor: 'white';
    borderBottomWidth: 1;
    borderBottomColor: '#e0e0e0';
  },
  headerTitle: {
    fontSize: 20;
    fontWeight: 'bold';
    color: '#333';
  },
  scrollView: {
    flex: 1;
  },
  summary: {
    padding: 20;
    backgroundColor: 'white';
    marginBottom: 16;
  },
  summaryText: {
    fontSize: 16;
    color: '#666';
    textAlign: 'center';
  },
  agentsList: {
    paddingHorizontal: 20;
  },
  agentCard: {
    backgroundColor: 'white';
    borderRadius: 12;
    padding: 16;
    marginBottom: 16;
    borderLeftWidth: 4;
    shadowColor: '#000';
    shadowOffset: { width: 0, height: 2 ;},
    shadowOpacity: 0.1;
    shadowRadius: 4;
    elevation: 3;
  },
  agentHeader: {
    flexDirection: 'row';
    justifyContent: 'space-between';
    alignItems: 'flex-start';
    marginBottom: 16;
  },
  agentInfo: {
    flexDirection: 'row';
    flex: 1;
  },
  agentAvatar: {
    fontSize: 32;
    marginRight: 12;
  },
  agentDetails: {
    flex: 1;
  },
  agentName: {
    fontSize: 18;
    fontWeight: 'bold';
    color: '#333';
    marginBottom: 4;
  },
  agentDescription: {
    fontSize: 14;
    color: '#666';
    lineHeight: 20;
  },
  agentStatus: {
    alignItems: 'flex-end';
  },
  statusDot: {
    width: 8;
    height: 8;
    borderRadius: 4;
    marginBottom: 4;
  },
  statusText: {
    fontSize: 12;
    fontWeight: '500';
  },
  agentMetrics: {
    flexDirection: 'row';
    justifyContent: 'space-between';
    marginBottom: 16;
    paddingVertical: 12;
    borderTopWidth: 1;
    borderBottomWidth: 1;
    borderColor: '#f0f0f0';
  },
  metric: {
    alignItems: 'center';
  },
  metricLabel: {
    fontSize: 12;
    color: '#666';
    marginBottom: 4;
  },
  metricValue: {
    fontSize: 14;
    fontWeight: 'bold';
    color: '#333';
  },
  agentCapabilities: {
    marginBottom: 16;
  },
  capabilitiesTitle: {
    fontSize: 14;
    fontWeight: '600';
    color: '#333';
    marginBottom: 8;
  },
  capabilitiesList: {
    flexDirection: 'row';
    flexWrap: 'wrap';
  },
  capabilityTag: {
    backgroundColor: '#e3f2fd';
    borderRadius: 12;
    paddingHorizontal: 8;
    paddingVertical: 4;
    marginRight: 8;
    marginBottom: 4;
  },
  capabilityText: {
    fontSize: 12;
    color: '#1976d2';
  },
  agentActions: {
    flexDirection: 'row';
    justifyContent: 'space-between';
    alignItems: 'center';
  },
  actionButton: {
    flexDirection: 'row';
    alignItems: 'center';
    paddingHorizontal: 12;
    paddingVertical: 8;
    borderRadius: 8;
    backgroundColor: '#f5f5f5';
  },
  actionButtonText: {
    fontSize: 14;
    color: '#333';
    marginLeft: 4;
  },
  switchContainer: {
    flexDirection: 'row';
    alignItems: 'center';
  },
  switchLabel: {
    fontSize: 14;
    color: '#333';
    marginRight: 8;
  },
  modalContainer: {
    flex: 1;
    backgroundColor: 'white';
  },
  modalHeader: {
    flexDirection: 'row';
    justifyContent: 'space-between';
    alignItems: 'center';
    paddingHorizontal: 20;
    paddingVertical: 16;
    borderBottomWidth: 1;
    borderBottomColor: '#e0e0e0';
  },
  modalTitle: {
    fontSize: 18;
    fontWeight: 'bold';
    color: '#333';
  },
  saveButton: {
    fontSize: 16;
    color: '#2196F3';
    fontWeight: '600';
  },
  modalContent: {
    flex: 1;
    padding: 20;
  },
  configSection: {
    marginBottom: 24;
  },
  configLabel: {
    fontSize: 16;
    fontWeight: '600';
    color: '#333';
    marginBottom: 12;
  },
  configOptions: {
    flexDirection: 'row';
    flexWrap: 'wrap';
  },
  configOption: {
    paddingHorizontal: 16;
    paddingVertical: 8;
    borderRadius: 20;
    backgroundColor: '#f5f5f5';
    marginRight: 8;
    marginBottom: 8;
  },
  selectedOption: {
    backgroundColor: '#2196F3';
  },
  configOptionText: {
    fontSize: 14;
    color: '#333';
  },
  selectedOptionText: {
    color: 'white';
  },
});

export default AgentManagementScreen; 