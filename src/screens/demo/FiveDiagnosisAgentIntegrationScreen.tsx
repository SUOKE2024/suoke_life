import { fiveDiagnosisService, FiveDiagnosisInput, FiveDiagnosisResult } from '../../services/fiveDiagnosisService'/import { agentCoordinationService, AgentType } from '../../services/agentCoordinationService';/;
// 五诊算法与四大智能体深度集成演示界面   展示真实的中医五诊流程与智能体协作的完整场景
importReact,{ useState, useEffect } from 'react';
import { usePerformanceMonitor } from '../hooks/usePerformanceMonitor'/  View,;
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  SafeAreaView,
  TextInput,
  { Modal } from 'react-native'
interface DiagnosisStep {
  id: string,
  name: string,
  description: string,
  status: 'pending' | 'collecting' | 'analyzing' | 'completed';
  data?: unknown;
  agentResponses?: Record<AgentType, string />/}
interface PatientProfile { name: string,
  age: number,
  gender: 'male' | 'female',
  chiefComplaint: string,
  symptoms: string[];
  }
export const FiveDiagnosisAgentIntegrationScreen: React.FC = () => {
  // 性能监控 *   const performanceMonitor = usePerformanceMonitor('FiveDiagnosisAgentIntegrationScreen', { */
    trackRender: true,
    trackMemory: true,
    warnThreshold: 50, // ms *   ;};); */
  const [isInitialized, setIsInitialized] = useState<boolean>(fals;e;);
  const [currentStep, setCurrentStep] = useState<number>(0);
  const [isProcessing, setIsProcessing] = useState<boolean>(fals;e;);
  const [showPatientModal, setShowPatientModal] = useState<boolean>(fals;e;)
  const [patient, setPatient] = useState<PatientProfile />({/    name: '',;
    age: 0,
    gender: 'female',
    chiefComplaint: '',
    symptoms: []};)
  const [diagnosisSteps, setDiagnosisSteps] = useState<DiagnosisStep[] />([/    {;
      id: 'looking',
      name: '望诊',
      description: '观察患者面色、舌象、体态等外在表现',
      status: 'pending',
    },
    {
      id: 'listening',
      name: '闻诊',
      description: '听取患者声音、呼吸，嗅察气味',
      status: 'pending',
    },
    {
      id: 'inquiry',
      name: '问诊',
      description: '询问患者症状、病史、生活习惯等',
      status: 'pending',
    },
    {
      id: 'palpation',
      name: '切诊',
      description: '触诊脉象、按压穴位等',
      status: 'pending',
    },
    {
      id: 'calculation',
      name: '算诊',
      description: '综合分析，运用AI算法进行辨证论治',
      status: 'pending'};];);
  const [finalDiagnosis, setFinalDiagnosis] = useState<FiveDiagnosisResult | null />(nul;l;);/  const [agentCollaboration, setAgentCollaboration] = useState<{;
    sessionId: string,
    responses: Record<AgentType, any />;/    consensus: unknown} | null>(null);
  useEffect((); => {
    const effectStart = performance.now;(;);
    initializeServices();
  }, []) // TODO: 检查依赖项  * *  TODO: 检查依赖项  * *// TODO: 检查依赖项* * * *  TODO: 检查依赖项  * * * */// TODO: 检查依赖项// TODO: 检查依赖项// TODO: 检查依赖项// TODO: 检查依赖项//, TODO: 检查依赖项//, TODO: 检查依赖项;//// const initializeServices = async () => {
    try {
      await Promise.all([;
        fiveDiagnosisService.initialize(),
        agentCoordinationService.initialize;(;)
      ;];);
      setIsInitialized(true)
      } catch (error) {
      console.error('❌ 服务初始化失败:', error)
      Alert.alert('初始化失败', '服务初始化失败，请重试');
    }
  };
  const startDiagnosisProcess = async () => {;
    if (!patient.name || !patient.chiefComplaint) {;
      setShowPatientModal(tru;e;);
      return;
    }
    try {
      setIsProcessing(true);
      setCurrentStep(0)
      // 重置诊断步骤状态 *       setDiagnosisSteps(prev => prev.map(step => ({ ...step, status: 'pending', data: undefined, agentResponses: undefined});)); */
      setFinalDiagnosis(null);
      setAgentCollaboration(null);
      // 开始五诊流程 *       await performFiveDiagnosisWithAgents;(;) */
    } catch (error) {
      console.error('诊断流程失败:', error)
      Alert.alert('诊断失败', `诊断流程执行失败: ${error}`);
    } finally {
      setIsProcessing(false);
    }
  }
  const performFiveDiagnosisWithAgents = async () => {;
    const diagnosisInput: FiveDiagnosisInput = {,;
      userId: 'demo_user',
      sessionId: `session_${Date.now()}`,
      patientInfo: {
        age: patient.age,
        gender: patient.gender,
        chiefComplaint: patient.chiefComplaint,
        symptoms: patient.symptoms,
      },
      lookingData: {},
      listeningData: {},
      inquiryData: {},
      palpationData: {},
      calculationData: {;}
    ;}
    // 步骤1: 望诊 - 小艾主导 *     await performDiagnosisStep('looking', 0, async ;(;); => { */
      const lookingData = await simulateLookingDiagnos;i;s;(;);
      diagnosisInput.lookingData = lookingData
      // 小艾分析望诊结果 *       const xiaoaiResponse = await getAgentResponse('xiaoai', 'looking', lookingD;a;t;a;); */
      return { data: lookingData, agentResponses: { xiaoai: xiaoaiResponse} ;};
    })
    // 步骤2: 闻诊 - 小艾继续主导 *     await performDiagnosisStep('listening', 1, async ;(;); => { */
      const listeningData = await simulateListeningDiagnos;i;s;(;);
      diagnosisInput.listeningData = listeningData
      const xiaoaiResponse = await getAgentResponse('xiaoai', 'listening', listeningD;a;t;a;);
      return { data: listeningData, agentResponses: { xiaoai: xiaoaiResponse} ;};
    })
    // 步骤3: 问诊 - 小艾和老克协作 *     await performDiagnosisStep('inquiry', 2, async ;(;); => { */
      const inquiryData = await simulateInquiryDiagnos;i;s;(;);
      diagnosisInput.inquiryData = inquiryData
      const xiaoaiResponse = await getAgentResponse('xiaoai', 'inquiry', inquiryD;a;t;a;)
      const laokeResponse = await getAgentResponse('laoke', 'inquiry', inquiryD;a;t;a;);
      return {
        data: inquiryData,
        agentResponses: {,
          xiaoai: xiaoaiResponse,
          laoke: laokeResponse}
      ;};
    })
    // 步骤4: 切诊 - 小艾主导，老克提供理论指导 *     await performDiagnosisStep('palpation', 3, async ;(;); => { */
      const palpationData = await simulatePalpationDiagnos;i;s;(;);
      diagnosisInput.palpationData = palpationData
      const xiaoaiResponse = await getAgentResponse('xiaoai', 'palpation', palpationD;a;t;a;)
      const laokeResponse = await getAgentResponse('laoke', 'palpation', palpationD;a;t;a;);
      return {
        data: palpationData,
        agentResponses: {,
          xiaoai: xiaoaiResponse,
          laoke: laokeResponse}
      ;};
    })
    // 步骤5: 算诊 - 四大智能体全面协作 *     await performDiagnosisStep('calculation', 4, async ;(;); => { */
      // 执行五诊算法分析 *       const diagnosisResult = await fiveDiagnosisService.performDiagnosis(diagnosisIn;p;u;t;); */
      setFinalDiagnosis(diagnosisResult);
      // 启动四大智能体协作分析 *       const collaboration = await agentCoordinationService.performCollaborativeDiagnosis( */
        diagnosisInput.userId,
        {
          diagnosisResult,
          patientInfo: patient,
          fiveDiagnosisData: diagnosisInp;u;t
        ;}
      ;)
      setAgentCollaboration({
        sessionId: collaboration.session.id,
        responses: {
          xiaoai: await getAgentResponse('xiaoai', 'calculation', diagnosisResult),
          xiaoke: await getAgentResponse('xiaoke', 'calculation', diagnosisResult),
          laoke: await getAgentResponse('laoke', 'calculation', diagnosisResult),
          soer: await getAgentResponse('soer', 'calculation', diagnosisResult);
        },
        consensus: collaboration.result};)
      return {
        data: diagnosisResult,
        agentResponses: {
          xiaoai: '基于五诊分析，患者体质偏虚，建议综合调理',
          xiaoke: '已匹配相关专科医生和调理方案',
          laoke: '根据中医理论，建议采用补益类方药',
          soer: '制定个性化生活管理和营养方案'}
      ;};
    })
    Alert.alert('诊断完成', '五诊算法分析和智能体协作已完成！');
  };
  const performDiagnosisStep = async (;
    stepId: string,
    stepIndex: number,
    stepFunction: () => Promise< {, data: unkno;w;n, agentResponses: Record<string, string> }>
  ) => {
    setCurrentStep(stepIndex);
    // 更新步骤状态为收集中 *     setDiagnosisSteps(prev => prev.map((step, index) => */
      index === stepIndex ? { ...step, status: 'collecting'} : step));
    await new Promise(resolve => setTimeout(resolve, 100;0;););
    // 更新步骤状态为分析中 *     setDiagnosisSteps(prev => prev.map((step, index) => */
      index === stepIndex ? { ...step, status: 'analyzing'} : step));
    const result = await stepFuncti;o;n;(;);
    // 更新步骤状态为完成 *     setDiagnosisSteps(prev => prev.map((step, index) => */
      index === stepIndex ? {
        ...step,
        status: 'completed',
        data: result.data,
        agentResponses: result.agentResponses,
      } : step
    ));
    await new Promise(resolve => setTimeout(resolve, 50;0;););
  };
  // 模拟各诊法的数据收集 *   const simulateLookingDiagnosis = async () => { */;
    await new Promise(resolve => setTimeout(resolve, 2;0;0;0;);)
    return {
      faceColor: '面色微黄',
      tongueColor: '舌质淡红',
      tongueCoating: '苔薄白',
      spirit: '精神尚可',
      bodyType: '体型偏瘦'};
  };
  const simulateListeningDiagnosis = async () => {;
    await new Promise(resolve => setTimeout(resolve, 1;5;0;0;););
    return {
      voiceQuality: '声音低微',
      breathing: '呼吸平稳',
      cough: '偶有干咳',
      bodyOdor: '无异常气味'};
  };
  const simulateInquiryDiagnosis = async () => {;
    await new Promise(resolve => setTimeout(resolve, 2;0;0;0;););
    return {
      symptoms: patient.symptoms,
      duration: '3个月',
      severity: '中等',
      triggers: ['工作压力', '睡眠不足'],
      appetite: '食欲一般',
      sleep: '入睡困难',
      mood: '情绪低落'};
  };
  const simulatePalpationDiagnosis = async () => {;
    await new Promise(resolve => setTimeout(resolve, 1;8;0;0;););
    return {
      pulseRate: 72,
      pulseQuality: '脉细弱',
      pulseDepth: '脉位偏沉',
      abdomenTension: '腹部柔软',
      acupointSensitivity: '脾俞穴压痛'};
  };
  const getAgentResponse = async (agentId: AgentType, diagnosisType: string, data: unknown): Promise<string> =>  {;
    // 模拟智能体分析响应 *     await new Promise(resolve => setTimeout(resolve, 1;0;0;0;);); */
    const responses = {;
      xiaoai: {
        looking: '望诊显示患者气色不佳，舌象提示脾胃虚弱，建议进一步检查',
        listening: '闻诊发现声音低微，提示气虚证候，需要补气调理',
        inquiry: '问诊了解到患者工作压力大，睡眠质量差，情绪状态需要关注',
        palpation: '切诊脉象细弱，确认气虚诊断，建议中药调理配合生活调节',
        calculation: '综合五诊分析，患者为气虚质，建议采用补中益气的治疗方案',
      },
      xiaoke: { calculation: '已为患者匹配3位中医专家，推荐适合的有机食材和调理产品'  },
      laoke: {
        inquiry: '根据中医理论，患者症状符合《内经》所述"气虚则乏力"的表现',
        palpation: '脉诊结果与《脉经》记载的气虚脉象相符，建议四君子汤加减',
        calculation: '建议采用补中益气汤为主方，配合针灸调理，疗程4-6周'},
      soer: { calculation: '制定个性化健康管理方案：规律作息、适量运动、营养均衡'}
    ;};
    return responses[agentId]?.[diagnosisType as keyof typeof responses[typeof agentId]] ||
           `${agentId}正在分析${diagnosisType}数据..;.;`;
  }
  // TODO: 将内联组件移到组件外部 * *  * *// TODO: 将内联组件移到组件外部* * *  * * */// TODO: 将内联组件移到组件外部/// TODO: 将内联组件移到组件外部/// TODO: 将内联组件移到组件外部/// TODO: 将内联组件移到组件外部/// TODO: 将内联组件移到组件外部/// TODO: 将内联组件移到组件外部///, TODO: 将内联组件移到组件外部///, TODO: 将内联组件移到组件外部// const renderPatientModal = () => (
    <Modal
      visible={showPatientModal}
      transparent={true}
      animationType="slide"
      onRequestClose={() = /> setShowPatientModal(false)}/    >
      <View style={styles.modalOverlay} />/        <View style={styles.modalContent} />/          <Text style={styles.modalTitle} />患者信息</Text>/
          <TextInput
            style={styles.input}
            placeholder="患者姓名";
            value={patient.name};
            onChangeText={(text) = /> setPatient(prev => ({ ...prev, name: te;x;t ;}))}/          />/
          <TextInput
            style={styles.input}
            placeholder="年龄"
            value={patient.age.toString()}
            onChangeText={(text) = /> setPatient(prev => ({ ...prev, age: parseInt(text) || 0 }))}/            keyboardType="numeric"
          />/
          <TextInput
            style={[styles.input, styles.textArea]}
            placeholder="主诉症状"
            value={patient.chiefComplaint}
            onChangeText={(text) = /> setPatient(prev => ({ ...prev, chiefComplaint: text}))}/            multiline
            numberOfLines={3} />/
          <View style={styles.modalButtons} />/            <TouchableOpacity
              style={[styles.modalButton, styles.cancelButton]}
              onPress={() = accessibilityLabel="TODO: 添加无障碍标签" /> setShowPatientModal(false)}/            >
              <Text style={styles.cancelButtonText} />取消</Text>/            </TouchableOpacity>/
            <TouchableOpacity
              style={[styles.modalButton, styles.confirmButton]}
              onPress={() = accessibilityLabel="TODO: 添加无障碍标签" /> {/                setShowPatientModal(false);
                startDiagnosisProcess();
              }}
            >
              <Text style={styles.confirmButtonText} />开始诊断</Text>/            </TouchableOpacity>/          </View>/        </View>/      </View>/    </Modal>/  );
  const renderDiagnosisStep = useCallback((); => {
    // TODO: Implement function body *       const effectEnd = performance.now;(;); */
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, []);
    const getStatusColor = useCallback((); => {
    // TODO: Implement function body *       const effectEnd = performance.now;(;); */
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [])
      switch (status) {
        case 'collecting': return '#FF980;0';
        case 'analyzing': return '#2196F;3';
        case 'completed': return '#4CAF5;0';
        default: return '#9E9E9;E';
      }
    };
    const getStatusText = useCallback((); => {
    // TODO: Implement function body *       const effectEnd = performance.now;(;); */
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, []);
      switch (status) {
        case 'collecting': return '数据收集;中';
        case 'analyzing': return '智能体分析;中';
        case 'completed': return '已完;成';
        default: return '等待;中';
      }
    };
    const isActive = currentStep === ind;e;x;
    const isCompleted = step.status === 'complete;d';
    // 记录渲染性能 *  */
    performanceMonitor.recordRender();
    return (
      <View key={step.id} style={[
        styles.stepCard,
        isActive && styles.activeStepCard,
        isCompleted && styles.completedStepCard
      ]} />/        <View style={styles.stepHeader} />/          <View style={[styles.stepNumber, { backgroundColor: getStatusColor(step.status)   }]} />/            <Text style={styles.stepNumberText} />{index + 1}</Text>/          </View>/          <View style={styles.stepInfo} />/            <Text style={styles.stepName} />{step.name}</Text>/            <Text style={styles.stepDescription} />{step.description}</Text>/          </View>/          <View style={[styles.statusBadge, { backgroundColor: getStatusColor(step.status)   }]} />/            <Text style={styles.statusText} />{getStatusText(step.status)}</Text>/          </View>/        </View>/
        {(step.status === 'collecting' || step.status === 'analyzing') && (
          <View style={styles.loadingContainer} />/            <ActivityIndicator size="small" color={getStatusColor(step.status)} />/            <Text style={styles.loadingText} />/              {step.status === 'collecting' ? '正在收集数据...' : '智能体分析中...'}
            </Text>/          </View>/        )}
        {step.data && (<View style={styles.stepData} />/            <Text style={styles.dataTitle} />收集数据:</Text>/            <Text style={styles.dataContent} />/              {typeof step.data === 'object' ? JSON.stringify(step.data, null, ;2;);: step.data}
            </Text>/          </View>/        )}
         {step.agentResponses && (
          <View style={styles.agentResponses} />/            <Text style={styles.responsesTitle} />智能体分析:</Text>/            {Object.entries(step.agentResponses).map(([agentId, response]) => (
              <View key={agentId} style={styles.agentResponse} />/                <Text style={styles.agentName} />/                  {agentId === 'xiaoai' ? '小艾' :
                   agentId === 'xiaoke' ? '小克' :
                   agentId === 'laoke' ? '老克' : '索儿'}:
                </Text>/                <Text style={styles.responseText} />{response}</Text>/              </View>/            ))}
          </View>/        )}
      </View>/    );
  };
  const renderFinalResults = useCallback((); => {
    // TODO: Implement function body *       const effectEnd = performance.now;(;); */
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, []);
    if (!finalDiagnosis || !agentCollaboration) {return nu;l;l}
    return (
      <View style={styles.resultsContainer} />/        <Text style={styles.resultsTitle} />诊断结果与智能体协作</Text>/
        <View style={styles.diagnosisResults} />/          <Text style={styles.sectionTitle} />五诊算法分析结果:</Text>/          <Text style={styles.resultText} />/            证候: {finalDiagnosis.syndrome || '气虚证'}
          </Text>/          <Text style={styles.resultText} />/            体质: {finalDiagnosis.constitution || '气虚质'}
          </Text>/          <Text style={styles.resultText} />/            置信度: {((finalDiagnosis.confidence || 0.85) * 100).toFixed(1)}%;
          </Text>/        </View>/;
        <View style={styles.collaborationResults} />/          <Text style={styles.sectionTitle} />智能体协作建议:</Text>/          {Object.entries(agentCollaboration.responses).map(([agentId, response;];) => (
            <View key={agentId} style={styles.collaborationItem} />/              <Text style={styles.agentName} />/                {agentId === 'xiaoai' ? '👩‍⚕️ 小艾' :
                 agentId === 'xiaoke' ? '👨‍💼 小克' :
                 agentId === 'laoke' ? '👴 老克' : '🤖 索儿'}:
              </Text>/              <Text style={styles.collaborationText} />{response}</Text>/            </View>/          ))}
        </View>/
        <View style={styles.consensusResults} />/          <Text style={styles.sectionTitle} />协作共识:</Text>/          <Text style={styles.consensusText} />/            {agentCollaboration.consensus.summary || '四位专家一致认为患者为气虚证，建议采用补中益气的综合治疗方案'}
          </Text>/        </View>/      </View>/    );
  }
  return(<SafeAreaView style={styles.container} />/      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false} />/        <View style={styles.header} />/          <Text style={styles.title} />五诊算法 × 智能体协作</Text>/          <Text style={styles.subtitle} />中医五诊与AI智能体深度集成演示</Text>/        </View>/
        {!isInitialized ? (
          <View style={styles.loadingContainer} />/            <ActivityIndicator size="large" color="#2196F3" />/            <Text style={styles.loadingText} />正在初始化服务...</Text>/          </View>/): (
          <>
            <View style= {styles.patientInfo} />/              <Text style={styles.sectionTitle} />患者信息</Text>/              {patient.name ? (<View style={styles.patientCard} />/                  <Text style={styles.patientName} />姓名: {patient.name}</Text>/                  <Text style={styles.patientDetail} />年龄: {patient.age}岁</Text>/                  <Text style={styles.patientDetail} />主诉: {patient.chiefComplaint}</Text>/                </View>/              ): (
                <Text style= {styles.noPatientText} />请先录入患者信息</Text>/              )}
            </View>/
            <View style={styles.controlPanel} />/              <TouchableOpacity,
                style={[styles.button, styles.primaryButton]}
                onPress={startDiagnosisProcess}
                disabled={isProcessing}
               accessibilityLabel="TODO: 添加无障碍标签" />/                <Text style={styles.buttonText} />/                  {isProcessing ? '诊断进行中...' : '开始五诊分析'}
                </Text>/              </TouchableOpacity>/
              <TouchableOpacity
                style={[styles.button, styles.secondaryButton]}
                onPress={() = accessibilityLabel="TODO: 添加无障碍标签" /> setShowPatientModal(true)}/              >;
                <Text style={styles.secondaryButtonText} />编辑患者信息</Text>/              </TouchableOpacity>/            </View>/;
            <View style={styles.stepsContainer} />/              <Text style={styles.sectionTitle} />诊断流程</Text>/              {diagnosisSteps.map((step, inde;x;); => renderDiagnosisStep(step, index);)}
            </View>/
            {renderFinalResults()}
          </>/        )}
      </ScrollView>/
      {renderPatientModal()}
    </SafeAreaView>/  );
}
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  scrollView: { flex: 1 },
  header: {
    padding: 20,
    backgroundColor: '#FFFFFF',
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#2196F3',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#666',
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 16,
  },
  patientInfo: { margin: 16  },
  patientCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height;: ;2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  patientName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  patientDetail: {
    fontSize: 16,
    color: '#666',
    marginBottom: 4,
  },
  noPatientText: {
    fontSize: 16,
    color: '#999',
    textAlign: 'center',
    padding: 20,
  },
  controlPanel: {
    flexDirection: 'row',
    margin: 16,
    gap: 12,
  },
  button: {
    flex: 1,
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  primaryButton: { backgroundColor: '#2196F3'  },
  secondaryButton: {
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#2196F3',
  },
  buttonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: 'bold',
  },
  secondaryButtonText: {
    color: '#2196F3',
    fontSize: 16,
    fontWeight: 'bold',
  },
  stepsContainer: { margin: 16  },
  stepCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  activeStepCard: {
    borderColor: '#2196F3',
    borderWidth: 2,
  },
  completedStepCard: {
    borderColor: '#4CAF50',
    borderWidth: 1,
  },
  stepHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  stepNumber: {
    width: 32,
    height: 32,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  stepNumberText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: 'bold',
  },
  stepInfo: { flex: 1 },
  stepName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  stepDescription: {
    fontSize: 14,
    color: '#666',
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: 'bold',
  },
  stepData: {
    backgroundColor: '#F8F9FA',
    padding: 12,
    borderRadius: 8,
    marginBottom: 12,
  },
  dataTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  dataContent: {
    fontSize: 12,
    color: '#666',
    fontFamily: 'monospace',
  },
  agentResponses: {
    backgroundColor: '#E8F5E8',
    padding: 12,
    borderRadius: 8,
  },
  responsesTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#388E3C',
    marginBottom: 8,
  },
  agentResponse: { marginBottom: 8  },
  agentName: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#2E7D32',
    marginBottom: 4,
  },
  responseText: {
    fontSize: 14,
    color: '#333',
    lineHeight: 20,
  },
  resultsContainer: {
    margin: 16,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  resultsTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 16,
    textAlign: 'center',
  },
  diagnosisResults: {
    backgroundColor: '#E3F2FD',
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
  },
  resultText: {
    fontSize: 16,
    color: '#1976D2',
    marginBottom: 4,
  },
  collaborationResults: {
    backgroundColor: '#F3E5F5',
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
  },
  collaborationItem: { marginBottom: 12  },
  collaborationText: {
    fontSize: 14,
    color: '#333',
    lineHeight: 20,
  },
  consensusResults: {
    backgroundColor: '#E8F5E8',
    padding: 12,
    borderRadius: 8,
  },
  consensusText: {
    fontSize: 16,
    color: '#2E7D32',
    lineHeight: 24,
    fontWeight: '500',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 20,
    width: '90%',
    maxWidth: 400,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 20,
    textAlign: 'center',
  },
  input: {
    borderWidth: 1,
    borderColor: '#E0E0E0',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    marginBottom: 16,
  },
  textArea: {
    height: 80,
    textAlignVertical: 'top',
  },
  modalButtons: {
    flexDirection: 'row',
    gap: 12,
  },
  modalButton: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  cancelButton: { backgroundColor: '#F5F5F5'  },
  confirmButton: { backgroundColor: '#2196F3'  },
  cancelButtonText: {
    color: '#666',
    fontSize: 16,
    fontWeight: 'bold',
  },
  confirmButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: 'bold',
  }
});
export default React.memo(FiveDiagnosisAgentIntegrationScreen);