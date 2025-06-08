import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  SafeAreaView,
  TextInput,
  Modal,
  Dimensions,
  Image,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { fiveDiagnosisService, FiveDiagnosisInput, FiveDiagnosisResult } from '../../services/fiveDiagnosisService';
import { agentCoordinationService, AgentType } from '../../services/agentCoordinationService';
import { usePerformanceMonitor } from '../../hooks/usePerformanceMonitor';
const { width, height } = Dimensions.get('window');
// 诊断步骤接口
interface DiagnosisStep {
  id: string;
  name: string;
  description: string;
  status: 'pending' | 'collecting' | 'analyzing' | 'completed' | 'failed';
  data?: unknown;
  agentResponses?: Record<AgentType, string>;
  progress?: number;
  icon?: string;
}
// 患者档案接口
interface PatientProfile {
  name: string;
  age: number;
  gender: 'male' | 'female';
  chiefComplaint: string;
  symptoms: string[];
  medicalHistory?: string[];
  currentMedications?: string[];
}
export const FiveDiagnosisAgentIntegrationScreen: React.FC = () => {
  // 性能监控
  const performanceMonitor = usePerformanceMonitor('FiveDiagnosisAgentIntegrationScreen', {
    trackRender: true,
    trackMemory: true,
    warnThreshold: 50, // ms;
  });
  // 状态管理
  const [isInitialized, setIsInitialized] = useState<boolean>(false);
  const [currentStep, setCurrentStep] = useState<number>(0);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [showPatientModal, setShowPatientModal] = useState<boolean>(false);
  const [patient, setPatient] = useState<PatientProfile>({
      name: "",
      age: 0,
    gender: 'female',
    chiefComplaint: '',
    symptoms: [],
  });
  const [diagnosisSteps, setDiagnosisSteps] = useState<DiagnosisStep[]>([
    {
      id: "looking",
      name: '望诊',
      description: '观察患者面色、舌象、体态等外在表现',
      status: 'pending',
      icon: '👁️',
      progress: 0,
    },
    {
      id: "listening",
      name: '闻诊',
      description: '听取患者声音、呼吸，嗅察气味',
      status: 'pending',
      icon: '👂',
      progress: 0,
    },
    {
      id: "inquiry",
      name: '问诊',
      description: '询问患者症状、病史、生活习惯等',
      status: 'pending',
      icon: '💬',
      progress: 0,
    },
    {
      id: "palpation",
      name: '切诊',
      description: '触诊脉象、按压穴位等',
      status: 'pending',
      icon: '🤲',
      progress: 0,
    },
    {
      id: "calculation",
      name: '算诊',
      description: '综合分析，运用AI算法进行辨证论治',
      status: 'pending',
      icon: '🔮',
      progress: 0,
    },
  ]);
  const [finalDiagnosis, setFinalDiagnosis] = useState<FiveDiagnosisResult | null>(null);
  const [agentCollaboration, setAgentCollaboration] = useState<{
    sessionId: string,
  responses: Record<AgentType, any>;
    consensus: unknown;
  } | null>(null);
  // 初始化服务
  useEffect() => {
    const effectStart = performance.now();
    initializeServices();
    return () => {
      const effectEnd = performance.now();
      performanceMonitor.recordMetric('useEffect_duration', effectEnd - effectStart);
    };
  }, []);
  const initializeServices = async () => {
    try {
      await Promise.all([
        fiveDiagnosisService.initialize(),
        agentCoordinationService.initialize(),
      ]);
      setIsInitialized(true);
    } catch (error) {
      Alert.alert("初始化失败",服务初始化失败，请重试');
      console.error('Service initialization failed:', error);
    }
  };
  // 开始诊断流程
  const startDiagnosisProcess = async () => {
    if (!patient.name || !patient.chiefComplaint) {
      setShowPatientModal(true);
      return;
    }
    try {
      setIsProcessing(true);
      setCurrentStep(0);
      // 重置诊断步骤状态
      setDiagnosisSteps(prev => prev.map(step => ({
        ...step,
        status: 'pending',
        data: undefined,
        agentResponses: undefined,
        progress: 0,
      })));
      setFinalDiagnosis(null);
      setAgentCollaboration(null);
      // 开始五诊流程
      await performFiveDiagnosisWithAgents();
    } catch (error) {
      Alert.alert('诊断失败', `诊断流程执行失败: ${error}`);
    } finally {
      setIsProcessing(false);
    }
  };
  // 执行五诊流程与智能体协作
  const performFiveDiagnosisWithAgents = async () => {
    const diagnosisInput: FiveDiagnosisInput = {,
  userId: 'demo_user',
      sessionId: `session_${Date.now()}`,
      patientInfo: {,
  age: patient.age,
        gender: patient.gender,
        chiefComplaint: patient.chiefComplaint,
        symptoms: patient.symptoms,
      },
      lookingData: {},
      listeningData: {},
      inquiryData: {},
      palpationData: {},
      calculationData: {},
    };
    // 步骤1: 望诊 - 小艾主导
    await performDiagnosisStep('looking', 0, async () => {
      const lookingData = await simulateLookingDiagnosis();
      diagnosisInput.lookingData = lookingData;
      const xiaoaiResponse = await getAgentResponse(AgentType.XIAOAI, 'looking', lookingData);
      return {
        data: lookingData,
        agentResponses: { [AgentType.XIAOAI]: xiaoaiResponse },
      };
    });
    // 步骤2: 闻诊 - 小艾继续主导
    await performDiagnosisStep('listening', 1, async () => {
      const listeningData = await simulateListeningDiagnosis();
      diagnosisInput.listeningData = listeningData;
      const xiaoaiResponse = await getAgentResponse(AgentType.XIAOAI, 'listening', listeningData);
      return {
        data: listeningData,
        agentResponses: { [AgentType.XIAOAI]: xiaoaiResponse },
      };
    });
    // 步骤3: 问诊 - 小艾和老克协作
    await performDiagnosisStep('inquiry', 2, async () => {
      const inquiryData = await simulateInquiryDiagnosis();
      diagnosisInput.inquiryData = inquiryData;
      const xiaoaiResponse = await getAgentResponse(AgentType.XIAOAI, 'inquiry', inquiryData);
      const laokeResponse = await getAgentResponse(AgentType.LAOKE, 'inquiry', inquiryData);
      return {
        data: inquiryData,
        agentResponses: {
          [AgentType.XIAOAI]: xiaoaiResponse,
          [AgentType.LAOKE]: laokeResponse,
        },
      };
    });
    // 步骤4: 切诊 - 小艾主导，老克提供理论指导
    await performDiagnosisStep('palpation', 3, async () => {
      const palpationData = await simulatePalpationDiagnosis();
      diagnosisInput.palpationData = palpationData;
      const xiaoaiResponse = await getAgentResponse(AgentType.XIAOAI, 'palpation', palpationData);
      const laokeResponse = await getAgentResponse(AgentType.LAOKE, 'palpation', palpationData);
      return {
        data: palpationData,
        agentResponses: {
          [AgentType.XIAOAI]: xiaoaiResponse,
          [AgentType.LAOKE]: laokeResponse,
        },
      };
    });
    // 步骤5: 算诊 - 四大智能体全面协作
    await performDiagnosisStep('calculation', 4, async () => {
      // 执行五诊算法分析
      const diagnosisResult = await fiveDiagnosisService.performComprehensiveDiagnosis(diagnosisInput);
      setFinalDiagnosis(diagnosisResult);
      // 启动四大智能体协作分析
      const collaboration = await agentCoordinationService.initiateCollaboration({
        initiatorAgent: AgentType.XIAOAI,
        targetAgents: [AgentType.XIAOKE, AgentType.LAOKE, AgentType.SOER],
        task: 'comprehensive_diagnosis_analysis',
        priority: 'high',
        data: {
          diagnosisResult,
          patientInfo: patient,
          fiveDiagnosisData: diagnosisInput,
        },
      });
      setAgentCollaboration({
        sessionId: collaboration.collaborationId,
        responses: {
          [AgentType.XIAOAI]: await getAgentResponse(AgentType.XIAOAI, 'calculation', diagnosisResult),
          [AgentType.XIAOKE]: await getAgentResponse(AgentType.XIAOKE, 'calculation', diagnosisResult),
          [AgentType.LAOKE]: await getAgentResponse(AgentType.LAOKE, 'calculation', diagnosisResult),
          [AgentType.SOER]: await getAgentResponse(AgentType.SOER, 'calculation', diagnosisResult),
        },
        consensus: collaboration,
      });
      return {
        data: diagnosisResult,
        agentResponses: {
          [AgentType.XIAOAI]: '基于五诊分析，患者体质偏虚，建议综合调理',
          [AgentType.XIAOKE]: '已匹配相关专科医生和调理方案',
          [AgentType.LAOKE]: '根据中医理论，建议采用补益类方药',
          [AgentType.SOER]: '制定个性化生活管理和营养方案',
        },
      };
    });
    Alert.alert("诊断完成",五诊算法分析和智能体协作已完成！');
  };
  // 执行单个诊断步骤
  const performDiagnosisStep = async (
    stepId: string,
    stepIndex: number,
    stepFunction: () => Promise<{ data: unknown; agentResponses: Record<string, string> }>,
  ) => {
    setCurrentStep(stepIndex);
    // 更新步骤状态为收集中
    updateStepStatus(stepIndex, 'collecting', 25);
    await new Promise(resolve => setTimeout(resolve, 1000));
    // 更新步骤状态为分析中
    updateStepStatus(stepIndex, 'analyzing', 75);
    const result = await stepFunction();
    // 更新步骤状态为完成
    updateStepStatus(stepIndex, 'completed', 100, result.data, result.agentResponses);
    await new Promise(resolve => setTimeout(resolve, 500));
  };
  // 更新步骤状态
  const updateStepStatus = (
    stepIndex: number,
    status: DiagnosisStep['status'],
    progress: number,
    data?: unknown,
    agentResponses?: Record<string, string>,
  ) => {
    setDiagnosisSteps(prev => prev.map((step, index) =>
      index === stepIndex ? {
        ...step,
        status,
        progress,
        data,
        agentResponses,
      } : step,
    ));
  };
  // 模拟各诊法的数据收集
  const simulateLookingDiagnosis = async () => {
    await new Promise(resolve => setTimeout(resolve, 2000));
    return {
      faceColor: "面色微黄",
      tongueColor: '舌质淡红',
      tongueCoating: '苔薄白',
      spirit: '精神尚可',
      bodyType: '体型偏瘦',
    };
  };
  const simulateListeningDiagnosis = async () => {
    await new Promise(resolve => setTimeout(resolve, 1500));
    return {
      voiceQuality: "声音低微",
      breathing: '呼吸平稳',
      cough: '偶有干咳',
      bodyOdor: '无异常气味',
    };
  };
  const simulateInquiryDiagnosis = async () => {
    await new Promise(resolve => setTimeout(resolve, 2000));
    return {
      symptoms: patient.symptoms,
      duration: '3个月',
      severity: '中等',
      triggers: ["工作压力",睡眠不足'],
      appetite: '食欲一般',
      sleep: '入睡困难',
      mood: '情绪低落',
    };
  };
  const simulatePalpationDiagnosis = async () => {
    await new Promise(resolve => setTimeout(resolve, 1800));
    return {
      pulseRate: 72,
      pulseQuality: '脉细弱',
      pulseDepth: '脉位偏浮',
      abdominalPalpation: '腹部柔软',
      acupointSensitivity: '神门穴敏感',
    };
  };
  // 获取智能体响应
  const getAgentResponse = async (agentType: AgentType, diagnosisType: string, data: any): Promise<string> => {
    // 模拟智能体响应
    const responses = {
      [AgentType.XIAOAI]: {
      looking: "面色微黄，舌质淡红，苔薄白，提示脾胃虚弱",
      listening: '声音低微，呼吸平稳，符合气虚体质特征',
        inquiry: '症状持续3个月，与工作压力相关，建议调理脾胃',
        palpation: '脉细弱偏浮，神门穴敏感，确认气虚血瘀证',
        calculation: '综合五诊分析，患者为脾胃气虚证，建议补中益气',
      },
      [AgentType.XIAOKE]: {
        calculation: '数据分析显示患者健康指数偏低，需要系统性调理',
      },
      [AgentType.LAOKE]: {
      inquiry: "根据中医理论，此为脾胃虚弱，气血不足之证",
      palpation: '脉象符合《脉经》所述气虚脉象特征',
        calculation: '建议采用四君子汤加减，配合针灸调理',
      },
      [AgentType.SOER]: {
        calculation: '建议调整作息，增加运动，改善饮食结构',
      },
    };
    await new Promise(resolve => setTimeout(resolve, 500));
    return responses[agentType]?.[diagnosisType] || '正在分析中...';
  };
  // 渲染诊断步骤
  const renderDiagnosisStep = (step: DiagnosisStep, index: number) => {
    const isActive = currentStep === index;
    const isCompleted = step.status === 'completed';
    const isProcessing = step.status === 'collecting' || step.status === 'analyzing';
    return (
      <View key={step.id} style={[styles.stepContainer, isActive && styles.activeStep]}>
        <View style={styles.stepHeader}>
          <View style={[styles.stepIcon, isCompleted && styles.completedIcon]}>
            {isProcessing ? (
              <ActivityIndicator size="small" color="#fff" />
            ) : (
              <Text style={styles.stepIconText}>{step.icon}</Text>
            )}
          </View>
          <View style={styles.stepInfo}>
            <Text style={[styles.stepName, isCompleted && styles.completedText]}>
              {step.name}
            </Text>
            <Text style={styles.stepDescription}>{step.description}</Text>
            {isProcessing && (
        <View style={styles.progressContainer}>
                <View style={[styles.progressBar, { width: `${step.progress}%` }]} />
              </View>
            )}
          </View>
          <View style={styles.stepStatus}>
            {isCompleted && <Icon name="check-circle" size={24} color="#4CAF50" />}
            {step.status === 'failed' && <Icon name="error" size={24} color="#F44336" />}
          </View>
        </View>
        {step.agentResponses && (
        <View style={styles.agentResponses}>
            {Object.entries(step.agentResponses).map(([agentType, response]) => (
              <View key={agentType} style={styles.agentResponse}>
                <Text style={styles.agentName}>{getAgentName(agentType)}:</Text>
                <Text style={styles.agentResponseText}>{response}</Text>
              </View>
            ))}
          </View>
        )}
      </View>
    );
  };
  // 获取智能体名称
  const getAgentName = (agentType: string): string => {
    const names = {
      [AgentType.XIAOAI]: '小艾',
      [AgentType.XIAOKE]: '小克',
      [AgentType.LAOKE]: '老克',
      [AgentType.SOER]: '索儿',
    };
    return names[agentType] || agentType;
  };
  // 渲染患者信息模态框
  const renderPatientModal = () => (
    <Modal;
      visible={showPatientModal}
      animationType="slide"
      transparent={true}
      onRequestClose={() => setShowPatientModal(false)}
    >
      <View style={styles.modalOverlay}>
        <View style={styles.modalContent}>
          <Text style={styles.modalTitle}>患者信息</Text>
          <TextInput;
            style={styles.input}
            placeholder="患者姓名"
            value={patient.name}
            onChangeText={(text) => setPatient(prev => ({ ...prev, name: text }))}
          />
          <TextInput;
            style={styles.input}
            placeholder="年龄"
            value={patient.age.toString()}
            onChangeText={(text) => setPatient(prev => ({ ...prev, age: parseInt(text) || 0 }))}
            keyboardType="numeric"
          />
          <TextInput;
            style={[styles.input, styles.textArea]}
            placeholder="主诉症状"
            value={patient.chiefComplaint}
            onChangeText={(text) => setPatient(prev => ({ ...prev, chiefComplaint: text }))}
            multiline;
            numberOfLines={3}
          />
          <View style={styles.modalButtons}>
            <TouchableOpacity;
              style={[styles.modalButton, styles.cancelButton]}
              onPress={() => setShowPatientModal(false)}
            >
              <Text style={styles.cancelButtonText}>取消</Text>
            </TouchableOpacity>
            <TouchableOpacity;
              style={[styles.modalButton, styles.confirmButton]}
              onPress={() => {
                setShowPatientModal(false);
                startDiagnosisProcess();
              }}
            >
              <Text style={styles.confirmButtonText}>开始诊断</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>
  );
  // 渲染诊断结果
  const renderDiagnosisResult = () => {
    if (!finalDiagnosis) return null;
    return (
      <View style={styles.resultContainer}>
        <Text style={styles.resultTitle}>🎯 综合诊断结果</Text>
        <View style={styles.resultContent}>
          <Text style={styles.resultLabel}>中医证型:</Text>
          <Text style={styles.resultValue}>{finalDiagnosis.comprehensiveAnalysis.tcmSyndrome}</Text>
          <Text style={styles.resultLabel}>体质类型:</Text>
          <Text style={styles.resultValue}>{finalDiagnosis.comprehensiveAnalysis.constitution}</Text>
          <Text style={styles.resultLabel}>健康风险:</Text>
          <Text style={[styles.resultValue, { color: getRiskColor(finalDiagnosis.comprehensiveAnalysis.healthRisk) }]}>
            {finalDiagnosis.comprehensiveAnalysis.healthRisk}
          </Text>
          <Text style={styles.resultLabel}>置信度:</Text>
          <Text style={styles.resultValue}>{(finalDiagnosis.comprehensiveAnalysis.confidence * 100).toFixed(1)}%</Text>
        </View>
      </View>
    );
  };
  const getRiskColor = (risk: string): string => {
    switch (risk) {
      case 'low': return '#4CAF50';
      case 'medium': return '#FF9800';
      case 'high': return '#F44336';
      default: return '#666';
    }
  };
  if (!isInitialized) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#2196F3" />
          <Text style={styles.loadingText}>正在初始化五诊系统...</Text>
        </View>
      </SafeAreaView>
    );
  }
  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        {}
        <View style={styles.header}>
          <Text style={styles.title}>🔮 五诊智能体协作演示</Text>
          <Text style={styles.subtitle}>传统四诊 + 创新算诊 + AI智能体协作</Text>
        </View>
        {}
        <View style={styles.controlSection}>
          <TouchableOpacity;
            style={[styles.startButton, isProcessing && styles.disabledButton]}
            onPress={startDiagnosisProcess}
            disabled={isProcessing}
          >
            {isProcessing ? (
              <ActivityIndicator size="small" color="#fff" />
            ) : (
              <Icon name="play-arrow" size={24} color="#fff" />
            )}
            <Text style={styles.startButtonText}>
              {isProcessing ? '诊断进行中...' : '开始五诊流程'}
            </Text>
          </TouchableOpacity>
        </View>
        {}
        <View style={styles.stepsSection}>
          <Text style={styles.sectionTitle}>📋 诊断流程</Text>
          {diagnosisSteps.map((step, index) => renderDiagnosisStep(step, index))}
        </View>
        {}
        {renderDiagnosisResult()}
        {}
        {agentCollaboration && (
        <View style={styles.collaborationContainer}>
            <Text style={styles.sectionTitle}>🤖 智能体协作分析</Text>
            {Object.entries(agentCollaboration.responses).map(([agentType, response]) => (
              <View key={agentType} style={styles.agentCollaborationItem}>
                <Text style={styles.agentCollaborationName}>{getAgentName(agentType)}</Text>
                <Text style={styles.agentCollaborationResponse}>{response}</Text>
              </View>
            ))}
          </View>
        )}
      </ScrollView>
      {}
      {renderPatientModal()}
    </SafeAreaView>
  );
};
const styles = StyleSheet.create({
  container: {,
  flex: 1,
    backgroundColor: '#f5f5f5',
  },
  loadingContainer: {,
  flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {,
  marginTop: 16,
    fontSize: 16,
    color: '#666',
  },
  scrollView: {,
  flex: 1,
  },
  header: {,
  padding: 20,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  title: {,
  fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    textAlign: 'center',
  },
  subtitle: {,
  fontSize: 14,
    color: '#666',
    textAlign: 'center',
    marginTop: 8,
  },
  controlSection: {,
  padding: 20,
  },
  startButton: {,
  backgroundColor: '#2196F3',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
    borderRadius: 12,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  disabledButton: {,
  backgroundColor: '#ccc',
  },
  startButtonText: {,
  color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    marginLeft: 8,
  },
  stepsSection: {,
  padding: 20,
  },
  sectionTitle: {,
  fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 16,
  },
  stepContainer: {,
  backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    elevation: 1,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  activeStep: {,
  borderColor: '#2196F3',
    borderWidth: 2,
  },
  stepHeader: {,
  flexDirection: 'row',
    alignItems: 'center',
  },
  stepIcon: {,
  width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#e0e0e0',
    justifyContent: 'center',
    alignItems: 'center',
  },
  completedIcon: {,
  backgroundColor: '#4CAF50',
  },
  stepIconText: {,
  fontSize: 18,
  },
  stepInfo: {,
  flex: 1,
    marginLeft: 12,
  },
  stepName: {,
  fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  completedText: {,
  color: '#4CAF50',
  },
  stepDescription: {,
  fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  progressContainer: {,
  height: 4,
    backgroundColor: '#e0e0e0',
    borderRadius: 2,
    marginTop: 8,
    overflow: 'hidden',
  },
  progressBar: {,
  height: '100%',
    backgroundColor: '#2196F3',
  },
  stepStatus: {,
  marginLeft: 12,
  },
  agentResponses: {,
  marginTop: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
  },
  agentResponse: {,
  marginBottom: 8,
  },
  agentName: {,
  fontSize: 14,
    fontWeight: 'bold',
    color: '#2196F3',
  },
  agentResponseText: {,
  fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  resultContainer: {,
  margin: 20,
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  resultTitle: {,
  fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 16,
  },
  resultContent: {,
  gap: 8,
  },
  resultLabel: {,
  fontSize: 14,
    fontWeight: 'bold',
    color: '#666',
  },
  resultValue: {,
  fontSize: 16,
    color: '#333',
    marginBottom: 8,
  },
  collaborationContainer: {,
  margin: 20,
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  agentCollaborationItem: {,
  marginBottom: 12,
    padding: 12,
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
  },
  agentCollaborationName: {,
  fontSize: 14,
    fontWeight: 'bold',
    color: '#2196F3',
  },
  agentCollaborationResponse: {,
  fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  modalOverlay: {,
  flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {,
  backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    width: width * 0.9,
    maxHeight: height * 0.8,
  },
  modalTitle: {,
  fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    textAlign: 'center',
    marginBottom: 20,
  },
  input: {,
  borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    marginBottom: 16,
  },
  textArea: {,
  height: 80,
    textAlignVertical: 'top',
  },
  modalButtons: {,
  flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 20,
  },
  modalButton: {,
  flex: 1,
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  cancelButton: {,
  backgroundColor: '#f5f5f5',
    marginRight: 8,
  },
  confirmButton: {,
  backgroundColor: '#2196F3',
    marginLeft: 8,
  },
  cancelButtonText: {,
  color: '#666',
    fontSize: 16,
    fontWeight: 'bold',
  },
  confirmButtonText: {,
  color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
export default FiveDiagnosisAgentIntegrationScreen;