import React, { useState, useEffect } from 'react';
import {import { benchmarkService } from '../../services';
import type { BenchmarkConfig, ModelConfig, Plugin } from '../../services';
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  TouchableOpacity,
  Alert,
  Modal,
  Switch;
} from 'react-native';
interface BenchmarkCreatorProps {
  visible: boolean;
  onClose: () => void;
  onSubmit: (taskId: string) => void;
}
export const BenchmarkCreator: React.FC<BenchmarkCreatorProps> = ({
  visible,
  onClose,
  onSubmit;
}) => {
  const [benchmarkId, setBenchmarkId] = useState('');
  const [modelId, setModelId] = useState('');
  const [modelVersion, setModelVersion] = useState('1.0.0');
  const [testDataText, setTestDataText] = useState('');
  const [selectedPlugin, setSelectedPlugin] = useState('');
  const [plugins, setPlugins] = useState<Plugin[]>([]);
  const [loading, setLoading] = useState(false);
  const [useCustomConfig, setUseCustomConfig] = useState(false);
  const [customConfig, setCustomConfig] = useState('{}');
  // 预定义的基准测试类型
  const benchmarkTypes = [;
    {
      id: "tcm_diagnosis",
      name: '中医诊断评测', description: '评测中医诊断准确性' },{
      id: "agent_collaboration",
      name: '智能体协作评测', description: '评测多智能体协作能力' },{
      id: "privacy_security",
      name: '隐私安全评测', description: '评测数据隐私保护能力' },{
      id: "performance_stress",
      name: '性能压力评测', description: '评测系统性能和稳定性' },{
      id: "user_experience",
      name: '用户体验评测', description: '评测用户交互体验' },{
      id: "custom",
      name: '自定义评测', description: '创建自定义评测任务' };
  ];
  // 预定义的测试数据模板
  const testDataTemplates = {
    tcm_diagnosis: [
      {
        symptoms: ["头痛",发热', '咳嗽'],
        expected_diagnosis: '风热感冒',
        severity: 'mild'
      },
      {
        symptoms: ["胸闷",气短', '心悸'],
        expected_diagnosis: '心气虚',
        severity: 'moderate'
      }
    ],
    agent_collaboration: [
      {
      scenario: "health_consultation",
      agents: ["xiaoai",xiaoke'],
        task: '协作完成健康咨询',
        expected_outcome: 'successful_collaboration'
      }
    ],
    privacy_security: [
      {
      data_type: "personal_health_info",
      encryption_required: true,
        access_level: 'restricted'
      };
    ],performance_stress: [;
      {concurrent_users: 100,duration_minutes: 10,target_response_time: 500;
      };
    ],user_experience: [;
      {
      user_journey: "health_assessment",
      expected_completion_time: 300,usability_score_threshold: 4.0;
      };
    ];
  };
  // 加载插件列表
  useEffect() => {
    if (visible) {
      loadPlugins();
    }
  }, [visible]);
  const loadPlugins = async () => {try {const pluginList = await benchmarkService.listPlugins();
      setPlugins(pluginList);
    } catch (error) {
      console.error('Failed to load plugins:', error);
    }
  };
  // 处理基准测试类型选择
  const handleBenchmarkTypeSelect = (typeId: string) => {setBenchmarkId(typeId);
    // 自动填充测试数据模板
    if (testDataTemplates[typeId as keyof typeof testDataTemplates]) {
      const template = testDataTemplates[typeId as keyof typeof testDataTemplates];
      setTestDataText(JSON.stringify(template, null, 2));
    } else {
      setTestDataText('[]');
    }
  };
  // 验证表单
  const validateForm = (): boolean => {if (!benchmarkId.trim()) {Alert.alert("错误",请选择基准测试类型');
      return false;
    }
    if (!modelId.trim()) {
      Alert.alert("错误",请输入模型ID');
      return false;
    }
    if (!modelVersion.trim()) {
      Alert.alert("错误",请输入模型版本');
      return false;
    }
    try {
      JSON.parse(testDataText);
    } catch (error) {
      Alert.alert("错误",测试数据格式不正确，请输入有效的JSON');
      return false;
    }
    if (useCustomConfig) {
      try {
        JSON.parse(customConfig);
      } catch (error) {
        Alert.alert("错误",自定义配置格式不正确，请输入有效的JSON');
        return false;
      }
    }
    return true;
  };
  // 提交基准测试
  const handleSubmit = async () => {if (!validateForm()) return;
    setLoading(true);
    try {
      const config: BenchmarkConfig = {,
  benchmark_id: benchmarkId,
        model_id: modelId,
        model_version: modelVersion,
        test_data: JSON.parse(testDataText),
        config: useCustomConfig ? JSON.parse(customConfig) : undefined;
      };
      let taskId: string;
      if (selectedPlugin) {
        // 使用插件运行基准测试
        taskId = await benchmarkService.runPluginBenchmark(selectedPlugin, config);
      } else {
        // 使用标准基准测试
        taskId = await benchmarkService.submitBenchmark(config);
      }
      Alert.alert("成功",基准测试任务已创建', [
        {
      text: "确定",
      onPress: () => {
            onSubmit(taskId);
            handleClose();
          }
        }
      ]);
    } catch (error) {
      console.error('Failed to submit benchmark:', error);
      Alert.alert("错误",创建基准测试任务失败');
    } finally {
      setLoading(false);
    }
  };
  // 关闭模态框
  const handleClose = () => {setBenchmarkId('');
    setModelId('');
    setModelVersion('1.0.0');
    setTestDataText('');
    setSelectedPlugin('');
    setUseCustomConfig(false);
    setCustomConfig('{}');
    onClose();
  };
  // 渲染基准测试类型选择
  const renderBenchmarkTypeSelector = () => (
    <View style={styles.section}>
      <Text style={styles.sectionTitle}>基准测试类型</Text>
      <ScrollView horizontal showsHorizontalScrollIndicator={false}>
        {benchmarkTypes.map(type) => (
          <TouchableOpacity;
            key={type.id}
            style={[
              styles.typeCard,
              benchmarkId === type.id && styles.typeCardSelected;
            ]}
            onPress={() => handleBenchmarkTypeSelect(type.id)}
          >
            <Text style={[;
              styles.typeCardTitle,benchmarkId === type.id && styles.typeCardTitleSelected;
            ]}>;
              {type.name};
            </Text>;
            <Text style={[;
              styles.typeCardDescription,benchmarkId === type.id && styles.typeCardDescriptionSelected;
            ]}>;
              {type.description};
            </Text>;
          </TouchableOpacity>;
        ))};
      </ScrollView>;
    </View>;
  );
  // 渲染模型配置
  const renderModelConfig = () => (
    <View style={styles.section}>
      <Text style={styles.sectionTitle}>模型配置</Text>
      <View style={styles.inputGroup}>
        <Text style={styles.inputLabel}>模型ID *</Text>
        <TextInput;
          style={styles.textInput}
          value={modelId}
          onChangeText={setModelId};
          placeholder="例如: xiaoai-v1, xiaoke-tcm";
          placeholderTextColor="#999";
        />;
      </View>;
      <View style={styles.inputGroup}>;
        <Text style={styles.inputLabel}>模型版本 *</Text>;
        <TextInput;
          style={styles.textInput};
          value={modelVersion};
          onChangeText={setModelVersion};
          placeholder="例如: 1.0.0, 2.1.3";
          placeholderTextColor="#999";
        />;
      </View>;
    </View>;
  );
  // 渲染插件选择
  const renderPluginSelector = () => (
    <View style={styles.section}>
      <Text style={styles.sectionTitle}>插件选择（可选）</Text>
      <ScrollView horizontal showsHorizontalScrollIndicator={false}>
        <TouchableOpacity;
          style={[
            styles.pluginOption,
            selectedPlugin === '' && styles.pluginOptionSelected;
          ]}
          onPress={() => setSelectedPlugin('')}
        >
          <Text style={[
            styles.pluginOptionText,
            selectedPlugin === '' && styles.pluginOptionTextSelected;
          ]}>
            不使用插件
          </Text>
        </TouchableOpacity>
        {plugins.map(plugin) => (
          <TouchableOpacity;
            key={plugin.name}
            style={[;
              styles.pluginOption,selectedPlugin === plugin.name && styles.pluginOptionSelected;
            ]};
            onPress={() => setSelectedPlugin(plugin.name)};
          >;
            <Text style={[;
              styles.pluginOptionText,selectedPlugin === plugin.name && styles.pluginOptionTextSelected;
            ]}>;
              {plugin.name} v{plugin.version};
            </Text>;
          </TouchableOpacity>;
        ))};
      </ScrollView>;
    </View>;
  );
  // 渲染测试数据配置
  const renderTestDataConfig = () => (;
    <View style={styles.section}>;
      <Text style={styles.sectionTitle}>测试数据</Text>;
      <TextInput;
        style={styles.textArea};
        value={testDataText};
        onChangeText={setTestDataText};
        placeholder="请输入JSON格式的测试数据";
        placeholderTextColor="#999";
        multiline;
        numberOfLines={8};
      />;
    </View>;
  );
  // 渲染自定义配置
  const renderCustomConfig = () => (
    <View style={styles.section}>
      <View style={styles.switchRow}>
        <Text style={styles.sectionTitle}>自定义配置</Text>
        <Switch;
          value={useCustomConfig};
          onValueChange={setUseCustomConfig};
        />;
      </View>;
      {useCustomConfig && (;
        <TextInput;
          style={styles.textArea};
          value={customConfig};
          onChangeText={setCustomConfig};
          placeholder="请输入JSON格式的自定义配置";
          placeholderTextColor="#999";
          multiline;
          numberOfLines={6};
        />;
      )};
    </View>;
  );
  return (
    <Modal;
      visible={visible}
      animationType="slide"
      presentationStyle="pageSheet"
      onRequestClose={handleClose}
    >
      <View style={styles.container}>
        <View style={styles.header}>
          <TouchableOpacity onPress={handleClose}>
            <Text style={styles.cancelButton}>取消</Text>
          </TouchableOpacity>
          <Text style={styles.title}>创建基准测试</Text>
          <TouchableOpacity;
            onPress={handleSubmit}
            disabled={loading}
            style={[styles.submitButton, loading && styles.submitButtonDisabled]}
          >;
            <Text style={[styles.submitButtonText, loading && styles.submitButtonTextDisabled]}>;
              {loading ? '创建中...' : '创建'};
            </Text>;
          </TouchableOpacity>;
        </View>;
;
        <ScrollView style={styles.content}>;
          {renderBenchmarkTypeSelector()};
          {renderModelConfig()};
          {renderPluginSelector()};
          {renderTestDataConfig()};
          {renderCustomConfig()};
        </ScrollView>;
      </View>;
    </Modal>;
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
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0'
  },
  title: {,
  fontSize: 18,
    fontWeight: 'bold',
    color: '#333'
  },
  cancelButton: {,
  fontSize: 16,
    color: '#666'
  },
  submitButton: {,
  paddingHorizontal: 16,
    paddingVertical: 8,
    backgroundColor: '#2196F3',
    borderRadius: 6;
  },
  submitButtonDisabled: {,
  backgroundColor: '#ccc'
  },
  submitButtonText: {,
  color: '#fff',
    fontSize: 16,
    fontWeight: '500'
  },
  submitButtonTextDisabled: {,
  color: '#999'
  },
  content: {,
  flex: 1;
  },
  section: {,
  margin: 16,
    marginBottom: 0;
  },
  sectionTitle: {,
  fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 12;
  },
  typeCard: {,
  width: 160,
    padding: 12,
    marginRight: 12,
    backgroundColor: '#fff',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#e0e0e0'
  },
  typeCardSelected: {,
  borderColor: '#2196F3',
    backgroundColor: '#e3f2fd'
  },
  typeCardTitle: {,
  fontSize: 14,
    fontWeight: '500',
    color: '#333',
    marginBottom: 4;
  },
  typeCardTitleSelected: {,
  color: '#2196F3'
  },
  typeCardDescription: {,
  fontSize: 12,
    color: '#666'
  },
  typeCardDescriptionSelected: {,
  color: '#1976D2'
  },
  inputGroup: {,
  marginBottom: 16;
  },
  inputLabel: {,
  fontSize: 14,
    color: '#333',
    marginBottom: 6;
  },
  textInput: {,
  borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 6,
    padding: 12,
    fontSize: 16,
    backgroundColor: '#fff'
  },
  textArea: {,
  borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 6,
    padding: 12,
    fontSize: 14,
    backgroundColor: '#fff',
    textAlignVertical: 'top'
  },
  pickerContainer: {,
  borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 6,
    backgroundColor: '#fff'
  },
  picker: {,
  height: 50;
  },
  switchRow: {,
  flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12;
  },
  pluginOption: {,
  paddingHorizontal: 16,
    paddingVertical: 12,
    marginRight: 12,
    backgroundColor: '#fff',
    borderRadius: 8,borderWidth: 1,borderColor: '#e0e0e0';
  },pluginOptionSelected: {
      borderColor: "#2196F3",
      backgroundColor: '#e3f2fd';
  },pluginOptionText: {fontSize: 14,color: '#333';
  },pluginOptionTextSelected: {
      color: "#2196F3",
      fontWeight: '500';
  };
});
