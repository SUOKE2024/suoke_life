import React, { useState, useEffect, useCallback, useRef } from 'react';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation, useFocusEffect } from '@react-navigation/native';
import { usePerformanceMonitor } from '../../hooks/usePerformanceMonitor';
import {;
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  Dimensions,
  Animated,
  Platform;
} from 'react-native';
import {;
  fiveDiagnosisService,
  FiveDiagnosisInput,
  FiveDiagnosisResult,
  FiveDiagnosisError;
} from '../../services/fiveDiagnosisService';
// 诊断步骤枚举
enum DiagnosisStep {
  PREPARATION = 'preparation',
  LOOKING = 'looking',
  LISTENING = 'listening',
  INQUIRY = 'inquiry',
  PALPATION = 'palpation',
  CALCULATION = 'calculation',
  ANALYSIS = 'analysis',
  RESULTS = 'results'
}
// 诊断状态接口
interface DiagnosisState {
  currentStep: DiagnosisStep;
  completedSteps: Set<DiagnosisStep>;
  isProcessing: boolean;
  progress: number;
  error?: string;
  sessionId?: string;
  collectedData: Partial<FiveDiagnosisInput>;
  result?: FiveDiagnosisResult;
}
// 步骤配置
const STEP_CONFIG = {
  [DiagnosisStep.PREPARATION]: {


    icon: '🔧';

  },
  [DiagnosisStep.LOOKING]: {


    icon: '👁️';

  },
  [DiagnosisStep.LISTENING]: {


    icon: '👂';

  },
  [DiagnosisStep.INQUIRY]: {


    icon: '💬';

  },
  [DiagnosisStep.PALPATION]: {


    icon: '🤚';

  },
  [DiagnosisStep.CALCULATION]: {


    icon: '🧮';

  },
  [DiagnosisStep.ANALYSIS]: {


    icon: '🧠';

  },
  [DiagnosisStep.RESULTS]: {


    icon: '📊';

  }
};
const { width: screenWidth, height: screenHeight ;} = Dimensions.get('window');
export default React.memo(function FiveDiagnosisScreen() {
  const navigation = useNavigation();
  const [diagnosisState, setDiagnosisState] = useState<DiagnosisState>({
    currentStep: DiagnosisStep.PREPARATION;
    completedSteps: new Set();
    isProcessing: false;
    progress: 0;
    collectedData: {,
  userId: 'current_user' // 应该从用户上下文获取
    ;}
  });
  // 动画值
  const progressAnimation = useRef(new Animated.Value(0)).current;
  const fadeAnimation = useRef(new Animated.Value(1)).current;
  const scaleAnimation = useRef(new Animated.Value(1)).current;
  // 性能监控
  const performanceMonitor = usePerformanceMonitor('FiveDiagnosisScreen', {
    trackRender: true;
    trackMemory: true;
    warnThreshold: 100;
  });
  // 初始化服务
  useEffect() => {
    initializeDiagnosisService();
  }, [])  // 检查是否需要添加依赖项;
  // 监听焦点变化
  useFocusEffect()
    useCallback() => {
      // 页面获得焦点时的逻辑
      return () => {
        // 页面失去焦点时的清理逻辑
      };
    }, [])
  );
  // 监听进度变化，更新动画
  useEffect() => {
    Animated.timing(progressAnimation, {
      toValue: diagnosisState.progress;
      duration: 500;
      useNativeDriver: false;
    }).start();
  }, [diagnosisState.progress]);
  // 初始化诊断服务
  const initializeDiagnosisService = async () => {
    try {
      setDiagnosisState(prev => ({ ...prev, isProcessing: true ;}));
      await fiveDiagnosisService.initialize();
      setDiagnosisState(prev => ({
        ...prev,
        isProcessing: false;
        sessionId: generateSessionId()
      ;}));
    } catch (error) {

      setDiagnosisState(prev => ({
        ...prev,
        isProcessing: false;

      }));
    }
  };
  // 开始诊断流程
  const startDiagnosis = useCallback() => {
    setDiagnosisState(prev => ({
      ...prev,
      currentStep: DiagnosisStep.LOOKING;
      progress: 12.5 // 1/8 的进度
    ;}));
  }, []);
  // 完成当前步骤
  const completeCurrentStep = useCallback(async (stepData: any) => {
    const { currentStep ;} = diagnosisState;
    try {
      setDiagnosisState(prev => ({ ...prev, isProcessing: true ;}));
      // 更新收集的数据
      const updatedData = { ...diagnosisState.collectedData };
      switch (currentStep) {
        case DiagnosisStep.LOOKING:
          updatedData.lookingData = stepData;
          break;
        case DiagnosisStep.LISTENING:
          updatedData.listeningData = stepData;
          break;
        case DiagnosisStep.INQUIRY:
          updatedData.inquiryData = stepData;
          break;
        case DiagnosisStep.PALPATION:
          updatedData.palpationData = stepData;
          break;
        case DiagnosisStep.CALCULATION:
          updatedData.calculationData = stepData;
          break;
      }
      // 更新状态
      const completedSteps = new Set(diagnosisState.completedSteps);
      completedSteps.add(currentStep);
      const nextStep = getNextStep(currentStep);
      const progress = calculateProgress(completedSteps);
      setDiagnosisState(prev => ({
        ...prev,
        currentStep: nextStep;
        completedSteps,
        progress,
        collectedData: updatedData;
        isProcessing: false;
      }));
      // 如果所有数据收集完成，开始分析
      if (nextStep === DiagnosisStep.ANALYSIS) {
        await performComprehensiveAnalysis(updatedData as FiveDiagnosisInput);
      }
    } catch (error) {

      setDiagnosisState(prev => ({
        ...prev,
        isProcessing: false;

      }));
    }
  }, [diagnosisState]);
  // 执行综合分析
  const performComprehensiveAnalysis = async (input: FiveDiagnosisInput) => {
    try {
      setDiagnosisState(prev => ({
        ...prev,
        isProcessing: true;
        currentStep: DiagnosisStep.ANALYSIS;
        progress: 87.5 // 7/8 的进度
      ;}));
      const result = await fiveDiagnosisService.performComprehensiveDiagnosis(input);
      setDiagnosisState(prev => ({
        ...prev,
        currentStep: DiagnosisStep.RESULTS;
        progress: 100;
        result,
        isProcessing: false;
      }));
      // 显示完成提示

        [{

      onPress: () => {;} }]
      );
    } catch (error) {

      setDiagnosisState(prev => ({
        ...prev,
        isProcessing: false;

      }));
    }
  };
  // 获取下一步骤
  const getNextStep = (currentStep: DiagnosisStep): DiagnosisStep => {
    const steps = Object.values(DiagnosisStep);
    const currentIndex = steps.indexOf(currentStep);
    return steps[currentIndex + 1] || DiagnosisStep.RESULTS;
  };
  // 计算进度
  const calculateProgress = (completedSteps: Set<DiagnosisStep>): number => {
    const totalSteps = Object.values(DiagnosisStep).length - 1; // 排除准备阶段
    return (completedSteps.size / totalSteps) * 100;
  };
  // 生成会话ID;
  const generateSessionId = (): string => {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  };
  // 渲染步骤指示器
  const renderStepIndicator = () => {
    const steps = Object.values(DiagnosisStep);
        return (
  <View style={styles.stepIndicator}>
        {steps.map(step, index) => {
          const isCompleted = diagnosisState.completedSteps.has(step);
          const isCurrent = diagnosisState.currentStep === step;
          const config = STEP_CONFIG[step];
                    return (
  <View key={step} style={styles.stepItem}>
              <View style={[
                styles.stepCircle,
                isCompleted && styles.stepCompleted,
                isCurrent && styles.stepCurrent;
              ]}}>
                <Text style={[
                  styles.stepIcon,
                  (isCompleted || isCurrent) && styles.stepIconActive;
                ]}}>
                  {config.icon}
                </Text>
              </View>
              <Text style={[
                styles.stepTitle,
                (isCompleted || isCurrent) && styles.stepTitleActive;
              ]}}>
                {config.title}
              </Text>
              {index < steps.length - 1  && <View style={[
                  styles.stepConnector,
                  isCompleted && styles.stepConnectorCompleted;
                ]}} />
              )}
            </View>
          );
        })}
      </View>
    );
  };
  // 渲染进度条
  const renderProgressBar = () => (
  <View style={styles.progressContainer}>
      <View style={styles.progressBar}>
        <Animated.View;
          style={[
            styles.progressFill,
            {
              width: progressAnimation.interpolate({),
  inputRange: [0, 100],
                outputRange: ["0%",100%'],
                extrapolate: 'clamp'
              ;}})
            }
          ]}
        />
      </View>
      <Text style={styles.progressText}>

      </Text>
    </View>
  );
  // 渲染当前步骤内容
  const renderCurrentStepContent = () => {
    const { currentStep } = diagnosisState;
    const config = STEP_CONFIG[currentStep];
    switch (currentStep) {
      case DiagnosisStep.PREPARATION:
        return (
  <View style={styles.stepContent;}>
            <Text style={styles.stepDescription}>{config.description}</Text>
            <Text style={styles.estimatedTime}>预计用时：{config.estimatedTime}</Text>
            <TouchableOpacity;
              style={styles.startButton}
              onPress={startDiagnosis}
              disabled={diagnosisState.isProcessing}
            >
              <Text style={styles.startButtonText}>开始五诊检测</Text>
            </TouchableOpacity>
          </View>
        );
      case DiagnosisStep.LOOKING:
        return (
  <View style={styles.stepContent;}>
            <Text style={styles.stepDescription}>{config.description}</Text>
            <Text style={styles.estimatedTime}>预计用时：{config.estimatedTime}</Text>
            <TouchableOpacity;
              style={styles.actionButton}
              onPress={() => completeCurrentStep(generateMockStepData(currentStep))}
              disabled={diagnosisState.isProcessing}
            >
              <Text style={styles.actionButtonText}>开始拍照</Text>
            </TouchableOpacity>
          </View>
        );
      case DiagnosisStep.LISTENING:
        return (
  <View style={styles.stepContent;}>
            <Text style={styles.stepDescription}>{config.description}</Text>
            <Text style={styles.estimatedTime}>预计用时：{config.estimatedTime}</Text>
            <TouchableOpacity;
              style={styles.actionButton}
              onPress={() => completeCurrentStep(generateMockStepData(currentStep))}
              disabled={diagnosisState.isProcessing}
            >
              <Text style={styles.actionButtonText}>开始录音</Text>
            </TouchableOpacity>
          </View>
        );
      case DiagnosisStep.INQUIRY:
        return (
  <View style={styles.stepContent;}>
            <Text style={styles.stepDescription}>{config.description}</Text>
            <Text style={styles.estimatedTime}>预计用时：{config.estimatedTime}</Text>
            <TouchableOpacity;
              style={styles.actionButton}
              onPress={() => completeCurrentStep(generateMockStepData(currentStep))}
              disabled={diagnosisState.isProcessing}
            >
              <Text style={styles.actionButtonText}>开始问诊</Text>
            </TouchableOpacity>
          </View>
        );
      case DiagnosisStep.PALPATION:
        return (
  <View style={styles.stepContent;}>
            <Text style={styles.stepDescription}>{config.description}</Text>
            <Text style={styles.estimatedTime}>预计用时：{config.estimatedTime}</Text>
            <TouchableOpacity;
              style={styles.actionButton}
              onPress={() => completeCurrentStep(generateMockStepData(currentStep))}
              disabled={diagnosisState.isProcessing}
            >
              <Text style={styles.actionButtonText}>开始切诊</Text>
            </TouchableOpacity>
          </View>
        );
      case DiagnosisStep.CALCULATION:
        return (
  <View style={styles.stepContent;}>
            <Text style={styles.stepDescription}>{config.description}</Text>
            <Text style={styles.estimatedTime}>预计用时：{config.estimatedTime}</Text>
            <View style={styles.calculationOptions}>
              <Text style={styles.calculationTitle}>选择算诊分析类型：</Text>
              <TouchableOpacity style={styles.calculationOption}>
                <Text style={styles.calculationOptionText}>🕐 子午流注分析</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.calculationOption}>
                <Text style={styles.calculationOptionText}>🎭 八字体质分析</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.calculationOption}>
                <Text style={styles.calculationOptionText}>☯️ 八卦配属分析</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.calculationOption}>
                <Text style={styles.calculationOptionText}>🌊 五运六气分析</Text>
              </TouchableOpacity>
            </View>
            <TouchableOpacity;
              style={styles.actionButton}
              onPress={() => completeCurrentStep(generateMockStepData(currentStep))}
              disabled={diagnosisState.isProcessing}
            >
              <Text style={styles.actionButtonText}>开始算诊</Text>
            </TouchableOpacity>
          </View>
        );
      case DiagnosisStep.ANALYSIS:
        return (
  <View style={styles.stepContent;}>
            <ActivityIndicator size="large" color="#007AFF" />
            <Text style={styles.stepDescription}>{config.description}</Text>
            <Text style={styles.estimatedTime}>预计用时：{config.estimatedTime}</Text>
          </View>
        );
      case DiagnosisStep.RESULTS:
        return (
  <View style={styles.stepContent;}>
            <Text style={styles.stepDescription}>{config.description}</Text>
            {diagnosisState.result  && <View style={styles.resultsContainer}>
                <Text style={styles.resultsTitle}>五诊分析结果</Text>
                <Text style={styles.resultsText}>

                </Text>
                <Text style={styles.resultsText}>

                </Text>
                <Text style={styles.resultsText}>

                </Text>
                <Text style={styles.resultsText}>

                </Text>
              </View>
            )}
            <TouchableOpacity;
              style={styles.actionButton}
              onPress={() => navigation.goBack()}
            >
              <Text style={styles.actionButtonText}>查看详细报告</Text>
            </TouchableOpacity>
          </View>
        );
      default:
        return null;
    }
  };
  // 生成模拟步骤数据
  const generateMockStepData = (step: DiagnosisStep) => {
    switch (step) {
      case DiagnosisStep.LOOKING:
        return {,
  faceImage: 'mock_face_image_data';
          tongueImage: 'mock_tongue_image_data';
          metadata: { timestamp: Date.now() ;}
        };
      case DiagnosisStep.LISTENING:
        return {,
  voiceRecording: 'mock_voice_data';
          breathingSound: 'mock_breathing_data';
          metadata: { timestamp: Date.now(), duration: 30 ;}
        };
      case DiagnosisStep.INQUIRY:
        return {,


          lifestyle: {,



          ;}
        };
      case DiagnosisStep.PALPATION:
        return {,
  pulseData: {,
  rate: 72;



          }
        };
      case DiagnosisStep.CALCULATION:
        return {,
  personalInfo: {,
  birthYear: 1990;
            birthMonth: 5;
            birthDay: 15;
            birthHour: 10;


          },
          analysisTypes: {,
  ziwuLiuzhu: true;
            constitution: true;
            bagua: true;
            wuyunLiuqi: true;
            comprehensive: true;
          },
          currentTime: new Date().toISOString();

        };
      default:
        return {;};
    }
  };
  return (
  <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity;
          style={styles.backButton}
          onPress={() => navigation.goBack()}
        >
          <Text style={styles.backButtonText}>←</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>五诊检测</Text>
        <TouchableOpacity;
          style={styles.restartButton}
          onPress={() => {
            setDiagnosisState({
              currentStep: DiagnosisStep.PREPARATION;
              completedSteps: new Set();
              isProcessing: false;
              progress: 0;
              collectedData: { userId: 'current_user' ;},
              sessionId: generateSessionId()
            ;});
          }}
        >
          <Text style={styles.restartButtonText}>重新开始</Text>
        </TouchableOpacity>
      </View>
      {renderProgressBar()}
      <ScrollView;
        style={styles.content}
        showsVerticalScrollIndicator={false}
        contentContainerStyle={styles.contentContainer}
      >
        {renderStepIndicator()}
        {renderCurrentStepContent()}
      </ScrollView>
    </SafeAreaView>
  );
}
const styles = StyleSheet.create({
  container: {,
  flex: 1;
    backgroundColor: '#f8f9fa'
  ;},
  header: {,
  flexDirection: 'row';
    alignItems: 'center';
    justifyContent: 'space-between';
    paddingHorizontal: 20;
    paddingVertical: 15;
    backgroundColor: '#ffffff';
    borderBottomWidth: 1;
    borderBottomColor: '#e9ecef'
  ;},
  backButton: {,
  padding: 8;
  },
  backButtonText: {,
  fontSize: 24;
    color: '#007AFF'
  ;},
  headerTitle: {,
  fontSize: 18;
    fontWeight: '600';
    color: '#1a1a1a'
  ;},
  restartButton: {,
  padding: 8;
  },
  restartButtonText: {,
  fontSize: 14;
    color: '#007AFF'
  ;},
  progressContainer: {,
  paddingHorizontal: 20;
    paddingVertical: 15;
    backgroundColor: '#ffffff'
  ;},
  progressBar: {,
  height: 8;
    backgroundColor: '#e9ecef';
    borderRadius: 4;
    overflow: 'hidden'
  ;},
  progressFill: {,
  height: '100%';
    backgroundColor: '#007AFF';
    borderRadius: 4;
  },
  progressText: {,
  fontSize: 12;
    color: '#6c757d';
    textAlign: 'center';
    marginTop: 8;
  },
  content: {,
  flex: 1;
  },
  contentContainer: {,
  padding: 20;
  },
  stepIndicator: {,
  flexDirection: 'row';
    flexWrap: 'wrap';
    justifyContent: 'space-between';
    marginBottom: 30;
  },
  stepItem: {,
  alignItems: 'center';
    width: screenWidth / 4 - 20;
    marginBottom: 15;
    position: 'relative'
  ;},
  stepCircle: {,
  width: 50;
    height: 50;
    borderRadius: 25;
    backgroundColor: '#e9ecef';
    alignItems: 'center';
    justifyContent: 'center';
    marginBottom: 8;
  },
  stepCompleted: {,
  backgroundColor: '#28a745'
  ;},
  stepCurrent: {,
  backgroundColor: '#007AFF'
  ;},
  stepIcon: {,
  fontSize: 20;
  },
  stepIconActive: {,
  color: '#ffffff'
  ;},
  stepTitle: {,
  fontSize: 12;
    color: '#6c757d';
    textAlign: 'center'
  ;},
  stepTitleActive: {,
  color: '#1a1a1a';
    fontWeight: '600'
  ;},
  stepConnector: {,
  position: 'absolute';
    top: 25;
    left: '100%';
    width: screenWidth / 4 - 40;
    height: 2;
    backgroundColor: '#e9ecef'
  ;},
  stepConnectorCompleted: {,
  backgroundColor: '#28a745'
  ;},
  stepContent: {,
  backgroundColor: '#ffffff';
    borderRadius: 12;
    padding: 30;
    alignItems: 'center';
    shadowColor: '#000';
    shadowOffset: {,
  width: 0;
      height: 2;
    },
    shadowOpacity: 0.1;
    shadowRadius: 8;
    elevation: 4;
  },
  stepDescription: {,
  fontSize: 16;
    color: '#6c757d';
    textAlign: 'center';
    marginBottom: 30;
    lineHeight: 24;
  },
  estimatedTime: {,
  fontSize: 14;
    color: '#6c757d';
    marginTop: 20;
    textAlign: 'center'
  ;},
  startButton: {,
  backgroundColor: '#007AFF';
    paddingHorizontal: 40;
    paddingVertical: 15;
    borderRadius: 8;
    marginBottom: 15;
    minWidth: 200;
  },
  startButtonText: {,
  color: '#ffffff';
    fontSize: 16;
    fontWeight: '600';
    textAlign: 'center'
  ;},
  actionButton: {,
  backgroundColor: '#007AFF';
    paddingHorizontal: 40;
    paddingVertical: 15;
    borderRadius: 8;
    marginBottom: 15;
    minWidth: 200;
  },
  actionButtonText: {,
  color: '#ffffff';
    fontSize: 16;
    fontWeight: '600';
    textAlign: 'center'
  ;},
  calculationOptions: {,
  flexDirection: 'row';
    justifyContent: 'space-between';
    marginBottom: 20;
  },
  calculationTitle: {,
  fontSize: 16;
    fontWeight: '600';
    color: '#1a1a1a'
  ;},
  calculationOption: {,
  padding: 10;
    borderWidth: 1;
    borderColor: '#e9ecef';
    borderRadius: 8;
  },
  calculationOptionText: {,
  fontSize: 16;
    color: '#1a1a1a'
  ;},
  resultsContainer: {,
  alignItems: 'center';
    marginBottom: 30;
  },
  resultsTitle: {,
  fontSize: 24;
    fontWeight: '700';
    color: '#28a745';
    marginBottom: 10;
  },
  resultsText: {,
  fontSize: 18;
    color: '#1a1a1a';
    marginBottom: 5;
  }
});