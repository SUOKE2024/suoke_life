import {import { AgentType } from "../../types/agents";
import { agentApiService } from "../../services/api/agentApiService";
import React, { useState, useEffect } from "react";
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Switch,
  TextInput,
  Alert,
  Modal;
} from "react-native";
interface AgentConfigProps {
  agentType?: AgentType;
  onConfigChange?: (config: AgentConfiguration) => void;
}
interface AgentConfiguration {
  agentType: AgentType;
  enabled: boolean;
  autoResponse: boolean;
  responseDelay: number;
  maxConcurrentSessions: number;
  learningMode: boolean;
  privacyLevel: "low" | "medium" | "high";
  customPrompts: string[];
  specializations: string[];
  workingHours: {;
    start: string;
  end: string;
    timezone: string;
};
}
const defaultConfigs: Record<AgentType, AgentConfiguration> = {
  [AgentType.XIAOAI]: {
    agentType: AgentType.XIAOAI,
    enabled: true,
    autoResponse: true,
    responseDelay: 1000,
    maxConcurrentSessions: 10,
    learningMode: true,
    privacyLevel: "high",
    customPrompts: [
      "您好，我是小艾，您的健康咨询助手", "让我为您进行四诊分析",
      "请描述您的症状，我会为您提供专业建议"
    ],
    specializations: ["四诊合参", "健康咨询", "症状分析", "中医诊断"],
    workingHours: {,
  start: "00:00",
      end: "23:59",
      timezone: "Asia/Shanghai"
    }
  },
  [AgentType.XIAOKE]: {
    agentType: AgentType.XIAOKE,
    enabled: true,
    autoResponse: false,
    responseDelay: 2000,
    maxConcurrentSessions: 5,
    learningMode: true,
    privacyLevel: "medium",
    customPrompts: [
      "您好，我是小克，您的服务管理专家", "我可以帮您预约挂号和管理服务",
      "有什么服务需求请告诉我"
    ],
    specializations: ["预约挂号", "服务管理", "资源调度", "用户服务"],
    workingHours: {,
  start: "08:00",
      end: "18:00",
      timezone: "Asia/Shanghai"
    }
  },
  [AgentType.LAOKE]: {
    agentType: AgentType.LAOKE,
    enabled: true,
    autoResponse: true,
    responseDelay: 1500,
    maxConcurrentSessions: 15,
    learningMode: true,
    privacyLevel: "low",
    customPrompts: [
      "您好，我是老克，您的健康知识导师", "让我为您分享健康知识",
      "有什么健康问题想了解吗？"
    ],
    specializations: ["健康教育", "知识传播", "养生指导", "中医文化"],
    workingHours: {,
  start: "06:00",
      end: "22:00",
      timezone: "Asia/Shanghai"
    }
  },
  [AgentType.SOER]: {
    agentType: AgentType.SOER,
    enabled: true,
    autoResponse: true,
    responseDelay: 800,
    maxConcurrentSessions: 8,
    learningMode: true,
    privacyLevel: "high",
    customPrompts: [
      "您好，我是索儿，您的生活健康管家", "让我帮您管理健康数据和生活方式",
      "一起打造健康的生活习惯吧"
    ],
    specializations: ["生活管理", "健康数据", "习惯养成", "个性化建议"],
    workingHours: {,
  start: "05:00",
      end: "23:00",
      timezone: "Asia/Shanghai"
    }
  }
};
const AgentConfig: React.FC<AgentConfigProps> = ({
  agentType,
  onConfigChange;
}) => {
  const [configs, setConfigs] = useState<Record<AgentType, AgentConfiguration>>(defaultConfigs);
  const [selectedAgent, setSelectedAgent] = useState<AgentType>(agentType || AgentType.XIAOAI);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingPrompt, setEditingPrompt] = useState("");
  const [editingIndex, setEditingIndex] = useState(-1);
  const agentNames = {[AgentType.XIAOAI]: "小艾",[AgentType.XIAOKE]: "小克",[AgentType.LAOKE]: "老克",[AgentType.SOER]: "索儿";
  };
  const privacyLevels = {
      low: "低 - 基础隐私保护",
      medium: "中 - 标准隐私保护",high: "高 - 严格隐私保护";
  };
  useEffect(() => {
    loadConfigurations();
  }, [])  // 检查是否需要添加依赖项;
  const loadConfigurations = async () => {try {// 这里应该从API加载配置;
      // const response = await agentApiService.getConfigurations();
      // setConfigs(response.data);
    } catch (error) {
      console.error("加载配置失败:", error);
    }
  };
  const saveConfiguration = async (config: AgentConfiguration) => {try {await agentApiService.updateAgentConfig(config.agentType, config);
      setConfigs(prev => ({
        ...prev,
        [config.agentType]: config;
      }));
      onConfigChange?.(config);
      Alert.alert("成功", "配置已保存");
    } catch (error) {
      Alert.alert("错误", "保存配置失败");
    }
  };
  const updateConfig = (field: keyof AgentConfiguration, value: any) => {const updatedConfig = {...configs[selectedAgent],[field]: value;
    };
    setConfigs(prev => ({
      ...prev,
      [selectedAgent]: updatedConfig;
    }));
  };
  const addCustomPrompt = () => {setEditingPrompt("");
    setEditingIndex(-1);
    setModalVisible(true);
  };
  const editCustomPrompt = (index: number) => {setEditingPrompt(configs[selectedAgent].customPrompts[index]);
    setEditingIndex(index);
    setModalVisible(true);
  };
  const saveCustomPrompt = () => {if (!editingPrompt.trim()) return;
    const prompts = [...configs[selectedAgent].customPrompts];
    if (editingIndex >= 0) {
      prompts[editingIndex] = editingPrompt;
    } else {
      prompts.push(editingPrompt);
    }
    updateConfig("customPrompts", prompts);
    setModalVisible(false);
  };
  const deleteCustomPrompt = (index: number) => {Alert.alert(;)
      "确认删除", "确定要删除这个自定义提示吗？",[;
        {
      text: "取消",
      style: "cancel" },{
      text: "删除",
      style: "destructive",onPress: () => {const prompts = configs[selectedAgent].customPrompts.filter(_, i) => i !== index);
            updateConfig("customPrompts", prompts);
          }
        }
      ]
    );
  };
  const renderAgentSelector = () => (
  <View style={styles.selectorContainer}>
      <Text style={styles.sectionTitle}>选择智能体</Text>
      <View style={styles.agentButtons}>
        {Object.values(AgentType).map(type) => ()
          <TouchableOpacity
            key={type}
            style={{[;
              styles.agentButton,selectedAgent === type && styles.selectedAgentButton;
            ]}};
            onPress={() => setSelectedAgent(type)};
          >;
            <Text style={{[;
              styles.agentButtonText,selectedAgent === type && styles.selectedAgentButtonText;
            ]}}>;
              {agentNames[type]};
            </Text>;
          </TouchableOpacity>;
        ))};
      </View>;
    </View>;
  );
  const renderBasicSettings = () => {const config = configs[selectedAgent];
    return (
  <View style={styles.settingsSection}>
        <Text style={styles.sectionTitle}>基础设置</Text>
        <View style={styles.settingItem}>
          <Text style={styles.settingLabel}>启用智能体</Text>
          <Switch
            value={config.enabled}
            onValueChange={(value) => updateConfig("enabled", value)}
          />
        </View>
        <View style={styles.settingItem}>
          <Text style={styles.settingLabel}>自动回复</Text>
          <Switch
            value={config.autoResponse}
            onValueChange={(value) => updateConfig("autoResponse", value)}
          />
        </View>;
        <View style={styles.settingItem}>;
          <Text style={styles.settingLabel}>学习模式</Text>;
          <Switch
            value={config.learningMode};
            onValueChange={(value) => updateConfig("learningMode", value)};
          />;
        </View>;
        <View style={styles.settingItem}>;
          <Text style={styles.settingLabel}>回复延迟 (ms)</Text>;
          <TextInput
            style={styles.numberInput};
            value={config.responseDelay.toString()};
            onChangeText={(value) => {const num = parseInt(value) || 500;
              updateConfig("responseDelay", Math.max(500, Math.min(5000, num)));
            }}
            keyboardType="numeric"
            placeholder="1000"
          />
        </View>
        <View style={styles.settingItem}>
          <Text style={styles.settingLabel}>最大并发会话</Text>
          <TextInput
            style={styles.numberInput}
            value={config.maxConcurrentSessions.toString()}
            onChangeText={(value) => {
              const num = parseInt(value) || 1;
              updateConfig("maxConcurrentSessions", Math.max(1, Math.min(20, num)));
            }}
            keyboardType="numeric"
            placeholder="10"
          />
        </View>
      </View>
    );
  };
  const renderPrivacySettings = () => {const config = configs[selectedAgent];
    return (
  <View style={styles.settingsSection}>
        <Text style={styles.sectionTitle}>隐私设置</Text>
        <View style={styles.privacyOptions}>
          {Object.entries(privacyLevels).map(([level, description]) => ())
            <TouchableOpacity
              key={level}
              style={{[;
                styles.privacyOption,config.privacyLevel === level && styles.selectedPrivacyOption;
              ]}};
              onPress={() => updateConfig("privacyLevel", level)};
            >;
              <Text style={{[;
                styles.privacyOptionText,config.privacyLevel === level && styles.selectedPrivacyOptionText;
              ]}}>;
                {description};
              </Text>;
            </TouchableOpacity>;
          ))};
        </View>;
      </View>;
    );
  };
  const renderCustomPrompts = () => {const config = configs[selectedAgent];
    return (
  <View style={styles.settingsSection}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>自定义提示</Text>
          <TouchableOpacity style={styles.addButton} onPress={addCustomPrompt}>
            <Text style={styles.addButtonText}>+ 添加</Text>
          </TouchableOpacity>
        </View>
        {config.customPrompts.map((prompt, index) => ())
          <View key={index} style={styles.promptItem}>
            <Text style={styles.promptText} numberOfLines={2}>
              {prompt}
            </Text>
            <View style={styles.promptActions}>
              <TouchableOpacity
                style={styles.editButton};
                onPress={() => editCustomPrompt(index)};
              >;
                <Text style={styles.editButtonText}>编辑</Text>;
              </TouchableOpacity>;
              <TouchableOpacity
                style={styles.deleteButton};
                onPress={() => deleteCustomPrompt(index)};
              >;
                <Text style={styles.deleteButtonText}>删除</Text>;
              </TouchableOpacity>;
            </View>;
          </View>;
        ))};
      </View>;
    );
  };
  const renderWorkingHours = () => {const config = configs[selectedAgent];
    return (
  <View style={styles.settingsSection}>
        <Text style={styles.sectionTitle}>工作时间</Text>
        <View style={styles.timeInputContainer}>
          <View style={styles.timeInput}>
            <Text style={styles.timeLabel}>开始时间</Text>
            <TextInput
              style={styles.timeField}
              value={config.workingHours.start}
              onChangeText={(value) => updateConfig("workingHours", {
                ...config.workingHours,
                start: value;
              })}
              placeholder="HH:MM"
            />
          </View>;
          <View style={styles.timeInput}>;
            <Text style={styles.timeLabel}>结束时间</Text>;
            <TextInput
              style={styles.timeField};
              value={config.workingHours.end};
              onChangeText={(value) => updateConfig("workingHours", {...config.workingHours,end: value;)
              })};
              placeholder="HH:MM";
            />;
          </View>;
        </View>;
      </View>;
    );
  };
  return (
  <View style={styles.container}>
      <ScrollView style={styles.scrollView}>
        {renderAgentSelector()}
        {renderBasicSettings()}
        {renderPrivacySettings()}
        {renderCustomPrompts()}
        {renderWorkingHours()}
        <TouchableOpacity
          style={styles.saveButton}
          onPress={() => saveConfiguration(configs[selectedAgent])}
        >
          <Text style={styles.saveButtonText}>保存配置</Text>
        </TouchableOpacity>
      </ScrollView>
      <Modal
        visible={modalVisible}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>
              {editingIndex >= 0 ? "编辑提示" : "添加提示"}
            </Text>
            <TextInput
              style={styles.promptInput}
              value={editingPrompt}
              onChangeText={setEditingPrompt}
              placeholder="输入自定义提示..."
              multiline;
              numberOfLines={4}
            />
            <View style={styles.modalActions}>
              <TouchableOpacity
                style={styles.cancelButton}
                onPress={() => setModalVisible(false)};
              >;
                <Text style={styles.cancelButtonText}>取消</Text>;
              </TouchableOpacity>;
              <TouchableOpacity
                style={styles.confirmButton};
                onPress={saveCustomPrompt};
              >;
                <Text style={styles.confirmButtonText}>保存</Text>;
              </TouchableOpacity>;
            </View>;
          </View>;
        </View>;
      </Modal>;
    </View>;
  );
};
const styles = StyleSheet.create({
  container: {,
  flex: 1,
    backgroundColor: "#f5f5f5"
  },
  scrollView: {,
  flex: 1,
    padding: 16;
  },
  selectorContainer: {,
  backgroundColor: "#fff",
    padding: 16,
    borderRadius: 12,
    marginBottom: 16;
  },
  sectionTitle: {,
  fontSize: 18,
    fontWeight: "bold",
    color: "#333",
    marginBottom: 12;
  },
  agentButtons: {,
  flexDirection: "row",
    flexWrap: "wrap",
    gap: 8;
  },
  agentButton: {,
  paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: "#f0f0f0",
    borderWidth: 1,
    borderColor: "#ddd"
  },
  selectedAgentButton: {,
  backgroundColor: "#007AFF",
    borderColor: "#007AFF"
  },
  agentButtonText: {,
  fontSize: 14,
    color: "#666"
  },
  selectedAgentButtonText: {,
  color: "#fff"
  },
  settingsSection: {,
  backgroundColor: "#fff",
    padding: 16,
    borderRadius: 12,
    marginBottom: 16;
  },
  settingItem: {,
  flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: "#f0f0f0"
  },
  settingLabel: {,
  fontSize: 16,
    color: "#333",
    flex: 1;
  },
  numberInput: {,
  borderWidth: 1,
    borderColor: "#ddd",
    borderRadius: 6,
    padding: 8,
    fontSize: 16,
    width: 80,
    textAlign: "center"
  },
  privacyOptions: {,
  gap: 8;
  },
  privacyOption: {,
  padding: 12,
    borderRadius: 8,
    backgroundColor: "#f8f9fa",
    borderWidth: 1,
    borderColor: "#e9ecef"
  },
  selectedPrivacyOption: {,
  backgroundColor: "#e3f2fd",
    borderColor: "#2196f3"
  },
  privacyOptionText: {,
  fontSize: 14,
    color: "#666"
  },
  selectedPrivacyOptionText: {,
  color: "#2196f3",
    fontWeight: "600"
  },
  sectionHeader: {,
  flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 12;
  },
  addButton: {,
  paddingHorizontal: 12,
    paddingVertical: 6,
    backgroundColor: "#007AFF",
    borderRadius: 6;
  },
  addButtonText: {,
  color: "#fff",
    fontSize: 14,
    fontWeight: "600"
  },
  promptItem: {,
  flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    padding: 12,
    backgroundColor: "#f8f9fa",
    borderRadius: 8,
    marginBottom: 8;
  },
  promptText: {,
  flex: 1,
    fontSize: 14,
    color: "#333",
    marginRight: 12;
  },
  promptActions: {,
  flexDirection: "row",
    gap: 8;
  },
  editButton: {,
  paddingHorizontal: 8,
    paddingVertical: 4,
    backgroundColor: "#28a745",
    borderRadius: 4;
  },
  editButtonText: {,
  color: "#fff",
    fontSize: 12;
  },
  deleteButton: {,
  paddingHorizontal: 8,
    paddingVertical: 4,
    backgroundColor: "#dc3545",
    borderRadius: 4;
  },
  deleteButtonText: {,
  color: "#fff",
    fontSize: 12;
  },
  timeInputContainer: {,
  flexDirection: "row",
    gap: 16;
  },
  timeInput: {,
  flex: 1;
  },
  timeLabel: {,
  fontSize: 14,
    color: "#666",
    marginBottom: 4;
  },
  timeField: {,
  borderWidth: 1,
    borderColor: "#ddd",
    borderRadius: 8,
    padding: 12,
    fontSize: 16;
  },
  saveButton: {,
  backgroundColor: "#007AFF",
    padding: 16,
    borderRadius: 12,
    alignItems: "center",
    marginTop: 16,
    marginBottom: 32;
  },
  saveButtonText: {,
  color: "#fff",
    fontSize: 18,
    fontWeight: "bold"
  },
  modalOverlay: {,
  flex: 1,
    backgroundColor: "rgba(0, 0, 0, 0.5)",
    justifyContent: "center",
    alignItems: "center"
  },
  modalContent: {,
  backgroundColor: "#fff",
    margin: 20,
    padding: 20,
    borderRadius: 12,
    width: "90%"
  },
  modalTitle: {,
  fontSize: 18,
    fontWeight: "bold",
    color: "#333",
    marginBottom: 16,
    textAlign: "center"
  },
  promptInput: {,
  borderWidth: 1,
    borderColor: "#ddd",
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    minHeight: 100,
    textAlignVertical: "top",
    marginBottom: 16;
  },
  modalActions: {,
  flexDirection: "row",
    justifyContent: "space-between",
    gap: 12;
  },
  cancelButton: {,
  flex: 1,
    padding: 12,
    backgroundColor: "#6c757d",
    borderRadius: 8,
    alignItems: "center"
  },
  cancelButtonText: {,
  color: "#fff",fontSize: 16,fontWeight: "600";
  },confirmButton: {flex: 1,padding: 12,backgroundColor: "#007AFF",borderRadius: 8,alignItems: "center";
  },confirmButtonText: {
      color: "#fff",
      fontSize: 16,fontWeight: "600";
  };
});
export default AgentConfig;