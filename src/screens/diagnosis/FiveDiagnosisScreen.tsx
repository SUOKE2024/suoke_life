import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  Dimensions,
  Animated,
  Platform
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation, useFocusEffect } from '@react-navigation/native';
import { 
  fiveDiagnosisService, 
  FiveDiagnosisInput, 
  FiveDiagnosisResult,
  FiveDiagnosisError 
} from '../../services/fiveDiagnosisService';
import { usePerformanceMonitor } from '../../hooks/usePerformanceMonitor';

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
    title: '准备阶段',
    description: '请确保环境安静，准备开始五诊检测',
    icon: '🔧',
    estimatedTime: '1分钟'
  },
  [DiagnosisStep.LOOKING]: {
    title: '望诊',
    description: '拍摄面部和舌部照片进行望诊分析',
    icon: '👁️',
    estimatedTime: '2-3分钟'
  },
  [DiagnosisStep.LISTENING]: {
    title: '闻诊',
    description: '录制语音和呼吸音进行闻诊分析',
    icon: '👂',
    estimatedTime: '2-3分钟'
  },
  [DiagnosisStep.INQUIRY]: {
    title: '问诊',
    description: '回答健康问题，描述症状和病史',
    icon: '💬',
    estimatedTime: '5-8分钟'
  },
  [DiagnosisStep.PALPATION]: {
    title: '切诊',
    description: '使用传感器进行脉象和触诊检测',
    icon: '🤚',
    estimatedTime: '3-5分钟'
  },
  [DiagnosisStep.CALCULATION]: {
    title: '算诊',
    description: '输入个人信息进行体质和运势分析',
    icon: '🧮',
    estimatedTime: '2分钟'
  },
  [DiagnosisStep.ANALYSIS]: {
    title: '综合分析',
    description: 'AI正在分析您的五诊数据...',
    icon: '🧠',
    estimatedTime: '1-2分钟'
  },
  [DiagnosisStep.RESULTS]: {
    title: '诊断结果',
    description: '查看您的健康分析报告和建议',
    icon: '📊',
    estimatedTime: '完成'
  }
};

const { width: screenWidth, height: screenHeight } = Dimensions.get('window');

export default function FiveDiagnosisScreen() {
  const navigation = useNavigation();
  const [diagnosisState, setDiagnosisState] = useState<DiagnosisState>({
    currentStep: DiagnosisStep.PREPARATION,
    completedSteps: new Set(),
    isProcessing: false,
    progress: 0,
    collectedData: {
      userId: 'current_user' // 应该从用户上下文获取
    }
  });

  // 动画值
  const progressAnimation = useRef(new Animated.Value(0)).current;
  const fadeAnimation = useRef(new Animated.Value(1)).current;
  const scaleAnimation = useRef(new Animated.Value(1)).current;

  // 性能监控
  const performanceMonitor = usePerformanceMonitor('FiveDiagnosisScreen', {
    trackRender: true,
    trackMemory: true,
    warnThreshold: 100
  });

  // 初始化服务
  useEffect(() => {
    initializeDiagnosisService();
  }, []);

  // 监听焦点变化
  useFocusEffect(
    useCallback(() => {
      // 页面获得焦点时的逻辑
      return () => {
        // 页面失去焦点时的清理逻辑
      };
    }, [])
  );

  // 监听进度变化，更新动画
  useEffect(() => {
    Animated.timing(progressAnimation, {
      toValue: diagnosisState.progress,
      duration: 500,
      useNativeDriver: false
    }).start();
  }, [diagnosisState.progress]);

  // 初始化诊断服务
  const initializeDiagnosisService = async () => {
    try {
      setDiagnosisState(prev => ({ ...prev, isProcessing: true }));
      await fiveDiagnosisService.initialize();
      setDiagnosisState(prev => ({ 
        ...prev, 
        isProcessing: false,
        sessionId: generateSessionId()
      }));
    } catch (error) {
      console.error('诊断服务初始化失败:', error);
      setDiagnosisState(prev => ({ 
        ...prev, 
        isProcessing: false,
        error: '服务初始化失败，请重试'
      }));
    }
  };

  // 开始诊断流程
  const startDiagnosis = useCallback(() => {
    setDiagnosisState(prev => ({
      ...prev,
      currentStep: DiagnosisStep.LOOKING,
      progress: 12.5 // 1/8 的进度
    }));
  }, []);

  // 完成当前步骤
  const completeCurrentStep = useCallback(async (stepData: any) => {
    const { currentStep } = diagnosisState;
    
    try {
      setDiagnosisState(prev => ({ ...prev, isProcessing: true }));

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
        currentStep: nextStep,
        completedSteps,
        progress,
        collectedData: updatedData,
        isProcessing: false
      }));

      // 如果所有数据收集完成，开始分析
      if (nextStep === DiagnosisStep.ANALYSIS) {
        await performComprehensiveAnalysis(updatedData as FiveDiagnosisInput);
      }

    } catch (error) {
      console.error('步骤完成失败:', error);
      setDiagnosisState(prev => ({
        ...prev,
        isProcessing: false,
        error: error instanceof FiveDiagnosisError ? error.message : '步骤处理失败'
      }));
    }
  }, [diagnosisState]);

  // 执行综合分析
  const performComprehensiveAnalysis = async (input: FiveDiagnosisInput) => {
    try {
      setDiagnosisState(prev => ({ 
        ...prev, 
        isProcessing: true,
        currentStep: DiagnosisStep.ANALYSIS,
        progress: 87.5 // 7/8 的进度
      }));

      const result = await fiveDiagnosisService.performDiagnosis(input);

      setDiagnosisState(prev => ({
        ...prev,
        currentStep: DiagnosisStep.RESULTS,
        progress: 100,
        result,
        isProcessing: false
      }));

      // 成功动画
      Animated.sequence([
        Animated.timing(scaleAnimation, {
          toValue: 1.1,
          duration: 200,
          useNativeDriver: true
        }),
        Animated.timing(scaleAnimation, {
          toValue: 1,
          duration: 200,
          useNativeDriver: true
        })
      ]).start();

    } catch (error) {
      console.error('综合分析失败:', error);
      setDiagnosisState(prev => ({
        ...prev,
        isProcessing: false,
        error: error instanceof FiveDiagnosisError ? error.message : '分析失败，请重试'
      }));
    }
  };

  // 跳过当前步骤
  const skipCurrentStep = useCallback(() => {
    Alert.alert(
      '跳过步骤',
      '跳过此步骤可能会影响诊断准确性，确定要跳过吗？',
      [
        { text: '取消', style: 'cancel' },
        { 
          text: '跳过', 
          style: 'destructive',
          onPress: () => completeCurrentStep(null)
        }
      ]
    );
  }, [completeCurrentStep]);

  // 重新开始诊断
  const restartDiagnosis = useCallback(() => {
    Alert.alert(
      '重新开始',
      '确定要重新开始诊断吗？当前进度将会丢失。',
      [
        { text: '取消', style: 'cancel' },
        {
          text: '确定',
          style: 'destructive',
          onPress: () => {
            setDiagnosisState({
              currentStep: DiagnosisStep.PREPARATION,
              completedSteps: new Set(),
              isProcessing: false,
              progress: 0,
              collectedData: { userId: 'current_user' },
              sessionId: generateSessionId()
            });
          }
        }
      ]
    );
  }, []);

  // 查看详细结果
  const viewDetailedResults = useCallback(() => {
    if (diagnosisState.result) {
      navigation.navigate('DiagnosisDetail', { 
        result: diagnosisState.result 
      });
    }
  }, [diagnosisState.result, navigation]);

  // 辅助函数
  const getNextStep = (currentStep: DiagnosisStep): DiagnosisStep => {
    const steps = Object.values(DiagnosisStep);
    const currentIndex = steps.indexOf(currentStep);
    return steps[currentIndex + 1] || DiagnosisStep.RESULTS;
  };

  const calculateProgress = (completedSteps: Set<DiagnosisStep>): number => {
    const totalSteps = Object.values(DiagnosisStep).length - 1; // 排除准备阶段
    return (completedSteps.size / totalSteps) * 100;
  };

  const generateSessionId = (): string => {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  };

  // 渲染步骤指示器
  const renderStepIndicator = () => {
    const steps = Object.values(DiagnosisStep);
    
    return (
      <View style={styles.stepIndicator}>
        {steps.map((step, index) => {
          const isCompleted = diagnosisState.completedSteps.has(step);
          const isCurrent = diagnosisState.currentStep === step;
          const config = STEP_CONFIG[step];
          
          return (
            <View key={step} style={styles.stepItem}>
              <View style={[
                styles.stepCircle,
                isCompleted && styles.stepCompleted,
                isCurrent && styles.stepCurrent
              ]}>
                <Text style={[
                  styles.stepIcon,
                  (isCompleted || isCurrent) && styles.stepIconActive
                ]}>
                  {config.icon}
                </Text>
              </View>
              <Text style={[
                styles.stepTitle,
                (isCompleted || isCurrent) && styles.stepTitleActive
              ]}>
                {config.title}
              </Text>
              {index < steps.length - 1 && (
                <View style={[
                  styles.stepConnector,
                  isCompleted && styles.stepConnectorCompleted
                ]} />
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
        <Animated.View 
          style={[
            styles.progressFill,
            {
              width: progressAnimation.interpolate({
                inputRange: [0, 100],
                outputRange: ['0%', '100%'],
                extrapolate: 'clamp'
              })
            }
          ]} 
        />
      </View>
      <Text style={styles.progressText}>
        {Math.round(diagnosisState.progress)}% 完成
      </Text>
    </View>
  );

  // 渲染当前步骤内容
  const renderCurrentStepContent = () => {
    const { currentStep } = diagnosisState;
    const config = STEP_CONFIG[currentStep];

    if (diagnosisState.error) {
      return (
        <View style={styles.errorContainer}>
          <Text style={styles.errorIcon}>⚠️</Text>
          <Text style={styles.errorTitle}>出现错误</Text>
          <Text style={styles.errorMessage}>{diagnosisState.error}</Text>
          <TouchableOpacity 
            style={styles.retryButton}
            onPress={() => setDiagnosisState(prev => ({ ...prev, error: undefined }))}
          >
            <Text style={styles.retryButtonText}>重试</Text>
          </TouchableOpacity>
        </View>
      );
    }

    return (
      <Animated.View 
        style={[
          styles.stepContent,
          { 
            opacity: fadeAnimation,
            transform: [{ scale: scaleAnimation }]
          }
        ]}
      >
        <Text style={styles.stepIcon}>{config.icon}</Text>
        <Text style={styles.stepTitle}>{config.title}</Text>
        <Text style={styles.stepDescription}>{config.description}</Text>
        
        {diagnosisState.isProcessing ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color="#007AFF" />
            <Text style={styles.loadingText}>处理中...</Text>
          </View>
        ) : (
          <View style={styles.actionContainer}>
            {currentStep === DiagnosisStep.PREPARATION && (
              <TouchableOpacity 
                style={styles.primaryButton}
                onPress={startDiagnosis}
              >
                <Text style={styles.primaryButtonText}>开始诊断</Text>
              </TouchableOpacity>
            )}
            
            {currentStep === DiagnosisStep.RESULTS && diagnosisState.result && (
              <>
                <View style={styles.resultSummary}>
                  <Text style={styles.resultTitle}>诊断完成</Text>
                  <Text style={styles.resultSubtitle}>
                    主要证型: {diagnosisState.result.primarySyndrome.name}
                  </Text>
                  <Text style={styles.resultConfidence}>
                    置信度: {Math.round(diagnosisState.result.overallConfidence * 100)}%
                  </Text>
                </View>
                
                <TouchableOpacity 
                  style={styles.primaryButton}
                  onPress={viewDetailedResults}
                >
                  <Text style={styles.primaryButtonText}>查看详细报告</Text>
                </TouchableOpacity>
              </>
            )}
            
            {currentStep !== DiagnosisStep.PREPARATION && 
             currentStep !== DiagnosisStep.RESULTS && 
             currentStep !== DiagnosisStep.ANALYSIS && (
              <>
                <TouchableOpacity 
                  style={styles.primaryButton}
                  onPress={() => {
                    // 这里应该导航到具体的诊断步骤页面
                    // 暂时使用模拟数据完成步骤
                    completeCurrentStep(generateMockStepData(currentStep));
                  }}
                >
                  <Text style={styles.primaryButtonText}>
                    开始{config.title}
                  </Text>
                </TouchableOpacity>
                
                <TouchableOpacity 
                  style={styles.secondaryButton}
                  onPress={skipCurrentStep}
                >
                  <Text style={styles.secondaryButtonText}>跳过此步骤</Text>
                </TouchableOpacity>
              </>
            )}
          </View>
        )}
        
        <Text style={styles.estimatedTime}>
          预计用时: {config.estimatedTime}
        </Text>
      </Animated.View>
    );
  };

  // 生成模拟步骤数据（实际应用中应该从具体的诊断页面获取）
  const generateMockStepData = (step: DiagnosisStep) => {
    switch (step) {
      case DiagnosisStep.LOOKING:
        return {
          faceImage: 'mock_face_image_data',
          tongueImage: 'mock_tongue_image_data',
          metadata: { timestamp: Date.now() }
        };
      case DiagnosisStep.LISTENING:
        return {
          voiceRecording: 'mock_voice_data',
          breathingPattern: [1, 2, 3, 4, 5],
          metadata: { timestamp: Date.now() }
        };
      case DiagnosisStep.INQUIRY:
        return {
          symptoms: ['头痛', '失眠', '食欲不振'],
          medicalHistory: ['高血压'],
          lifestyle: { exercise: 'low', diet: 'normal' },
          metadata: { timestamp: Date.now() }
        };
      case DiagnosisStep.PALPATION:
        return {
          pulseData: [70, 72, 68, 71, 69],
          touchData: { temperature: 36.5, pressure: 'normal' },
          metadata: { timestamp: Date.now() }
        };
      case DiagnosisStep.CALCULATION:
        return {
          birthDate: '1990-01-01',
          birthTime: '08:00',
          location: '北京',
          metadata: { timestamp: Date.now() }
        };
      default:
        return {};
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity 
          style={styles.backButton}
          onPress={() => navigation.goBack()}
        >
          <Text style={styles.backButtonText}>←</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>五诊检测</Text>
        <TouchableOpacity 
          style={styles.restartButton}
          onPress={restartDiagnosis}
        >
          <Text style={styles.restartButtonText}>重新开始</Text>
        </TouchableOpacity>
      </View>

      {renderProgressBar()}

      <ScrollView 
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
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa'
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 15,
    backgroundColor: '#ffffff',
    borderBottomWidth: 1,
    borderBottomColor: '#e9ecef'
  },
  backButton: {
    padding: 8
  },
  backButtonText: {
    fontSize: 24,
    color: '#007AFF'
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1a1a1a'
  },
  restartButton: {
    padding: 8
  },
  restartButtonText: {
    fontSize: 14,
    color: '#007AFF'
  },
  progressContainer: {
    paddingHorizontal: 20,
    paddingVertical: 15,
    backgroundColor: '#ffffff'
  },
  progressBar: {
    height: 8,
    backgroundColor: '#e9ecef',
    borderRadius: 4,
    overflow: 'hidden'
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#007AFF',
    borderRadius: 4
  },
  progressText: {
    fontSize: 12,
    color: '#6c757d',
    textAlign: 'center',
    marginTop: 8
  },
  content: {
    flex: 1
  },
  contentContainer: {
    padding: 20
  },
  stepIndicator: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: 30
  },
  stepItem: {
    alignItems: 'center',
    width: screenWidth / 4 - 20,
    marginBottom: 15,
    position: 'relative'
  },
  stepCircle: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: '#e9ecef',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 8
  },
  stepCompleted: {
    backgroundColor: '#28a745'
  },
  stepCurrent: {
    backgroundColor: '#007AFF'
  },
  stepIcon: {
    fontSize: 20
  },
  stepIconActive: {
    color: '#ffffff'
  },
  stepTitle: {
    fontSize: 12,
    color: '#6c757d',
    textAlign: 'center'
  },
  stepTitleActive: {
    color: '#1a1a1a',
    fontWeight: '600'
  },
  stepConnector: {
    position: 'absolute',
    top: 25,
    left: '100%',
    width: screenWidth / 4 - 40,
    height: 2,
    backgroundColor: '#e9ecef'
  },
  stepConnectorCompleted: {
    backgroundColor: '#28a745'
  },
  stepContent: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 30,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2
    },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4
  },
  stepDescription: {
    fontSize: 16,
    color: '#6c757d',
    textAlign: 'center',
    marginBottom: 30,
    lineHeight: 24
  },
  loadingContainer: {
    alignItems: 'center',
    marginVertical: 20
  },
  loadingText: {
    fontSize: 16,
    color: '#6c757d',
    marginTop: 10
  },
  actionContainer: {
    width: '100%',
    alignItems: 'center'
  },
  primaryButton: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 40,
    paddingVertical: 15,
    borderRadius: 8,
    marginBottom: 15,
    minWidth: 200
  },
  primaryButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
    textAlign: 'center'
  },
  secondaryButton: {
    backgroundColor: 'transparent',
    paddingHorizontal: 40,
    paddingVertical: 15,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#6c757d',
    minWidth: 200
  },
  secondaryButtonText: {
    color: '#6c757d',
    fontSize: 16,
    textAlign: 'center'
  },
  estimatedTime: {
    fontSize: 14,
    color: '#6c757d',
    marginTop: 20,
    textAlign: 'center'
  },
  resultSummary: {
    alignItems: 'center',
    marginBottom: 30
  },
  resultTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: '#28a745',
    marginBottom: 10
  },
  resultSubtitle: {
    fontSize: 18,
    color: '#1a1a1a',
    marginBottom: 5
  },
  resultConfidence: {
    fontSize: 16,
    color: '#6c757d'
  },
  errorContainer: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 30,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#dc3545'
  },
  errorIcon: {
    fontSize: 48,
    marginBottom: 15
  },
  errorTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#dc3545',
    marginBottom: 10
  },
  errorMessage: {
    fontSize: 16,
    color: '#6c757d',
    textAlign: 'center',
    marginBottom: 20,
    lineHeight: 24
  },
  retryButton: {
    backgroundColor: '#dc3545',
    paddingHorizontal: 30,
    paddingVertical: 12,
    borderRadius: 8
  },
  retryButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600'
  }
});