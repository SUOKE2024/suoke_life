import { useNavigation } from '@react-navigation/native';
import React, { useCallback, useEffect, useState } from 'react';
import {
  Alert,
  Dimensions,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import { colors, spacing } from '../../constants/theme';
import { fiveDiagnosisService } from '../../services/fiveDiagnosisService';
import {
  DiagnosisInput,
  DiagnosisStep,
  FiveDiagnosisResult,
} from '../../types/diagnosis';
import Icon from '../common/Icon';
import CalculationDiagnosisComponent from './CalculationDiagnosisComponent';
import { InquiryDiagnosisComponent } from './components/InquiryDiagnosisComponent';
import { ListenDiagnosisComponent } from './components/ListenDiagnosisComponent';
import { LookDiagnosisComponent } from './components/LookDiagnosisComponent';
import { PalpationDiagnosisComponent } from './components/PalpationDiagnosisComponent';

const { width } = Dimensions.get('window');

interface FiveDiagnosisScreenProps {
  onComplete?: (result: FiveDiagnosisResult) => void;
}

const FiveDiagnosisScreen: React.FC<FiveDiagnosisScreenProps> = ({
  onComplete,
}) => {
  const navigation = useNavigation();
  const [currentStep, setCurrentStep] = useState<number>(0);
  const [stepData, setStepData] = useState<Record<number, any>>({});
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [analysisResult, setAnalysisResult] =
    useState<FiveDiagnosisResult | null>(null);
  const [isServiceInitialized, setIsServiceInitialized] =
    useState<boolean>(false);

  const diagnosisSteps: DiagnosisStep[] = [
    {
      id: 'look',
      title: '望诊',
      description: '观察面色、舌象、体态等',
      icon: 'eye',
      component: LookDiagnosisComponent,
    },
    {
      id: 'listen',
      title: '闻诊',
      description: '听声音、闻气味',
      icon: 'ear',
      component: ListenDiagnosisComponent,
    },
    {
      id: 'inquiry',
      title: '问诊',
      description: '询问症状、病史等',
      icon: 'message-circle',
      component: InquiryDiagnosisComponent,
    },
    {
      id: 'palpation',
      title: '切诊',
      description: '脉诊、按诊等',
      icon: 'hand',
      component: PalpationDiagnosisComponent,
    },
    {
      id: 'calculation',
      title: '算诊',
      description: '数据分析、量化诊断',
      icon: 'bar-chart',
      component: CalculationDiagnosisComponent,
    },
  ];

  const initializeDiagnosisService = useCallback(async () => {
    try {
      await fiveDiagnosisService.initialize();
      setIsServiceInitialized(true);
    } catch (error) {
      Alert.alert('错误', '初始化诊断服务失败，请重试');
    }
  }, []);

  useEffect() => {
    initializeDiagnosisService();
  }, [initializeDiagnosisService]);

  const handleStepPress = useCallback(stepIndex: number) => {
      if (stepIndex <= currentStep + 1) {
        setCurrentStep(stepIndex);
      }
    },
    [currentStep]
  );

  const handleStepComplete = useCallback(stepIndex: number, data: unknown) => {
      setStepData(prev) => ({
        ...prev,
        [stepIndex]: data,
      }));

      if (stepIndex === currentStep && stepIndex < diagnosisSteps.length - 1) {
        setCurrentStep(stepIndex + 1);
      }
    },
    [currentStep, diagnosisSteps.length]
  );

  const canPerformAnalysis = useCallback() => {
    return Object.keys(stepData).length >= 3; // 至少完成3个步骤
  }, [stepData]);

  const performAnalysis = useCallback(async () => {
    if (!canPerformAnalysis() || !isServiceInitialized) {
      Alert.alert('提示', '请至少完成3个诊断步骤后再进行分析');
      return;
    }

    setIsAnalyzing(true);
    try {
      const input: DiagnosisInput = {,
  lookData: stepData[0],
        listenData: stepData[1],
        inquiryData: stepData[2],
        palpationData: stepData[3],
        calculationData: stepData[4],
        timestamp: Date.now(),
      };

      const result = await fiveDiagnosisService.performDiagnosis(input);
      setAnalysisResult(result);
      showAnalysisResult(result);

      if (onComplete) {
        onComplete(result);
      }
    } catch (error) {
      Alert.alert('错误', '诊断分析失败，请重试');
    } finally {
      setIsAnalyzing(false);
    }
  }, [canPerformAnalysis, isServiceInitialized, stepData, onComplete]);

  const showAnalysisResult = useCallback(result: FiveDiagnosisResult) => {
    Alert.alert(
      '诊断结果',
      `综合评估: ${result.overallAssessment}\n\n主要症候: ${result.primarySyndrome}`,
      [
        {
          text: '查看详情',
          onPress: () => showDetailedResult(result),
        },
        {
          text: '确定',
          style: 'default',
        },
      ]
    );
  }, []);

  const showDetailedResult = useCallback(result: FiveDiagnosisResult) => {
    // 这里可以导航到详细结果页面
  }, []);

  const resetDiagnosis = useCallback() => {
    Alert.alert('重置诊断', '确定要重置所有诊断数据吗？', [
      {
        text: '取消',
        style: 'cancel',
      },
      {
        text: '确定',
        style: 'destructive',
        onPress: () => {
          setCurrentStep(0);
          setStepData({});
          setAnalysisResult(null);
        },
      },
    ]);
  }, []);

  const getCompletedStepsCount = useCallback() => {
    return Object.keys(stepData).length;
  }, [stepData]);

  const getProgressPercentage = useCallback() => {
    return (getCompletedStepsCount() / diagnosisSteps.length) * 100;
  }, [getCompletedStepsCount, diagnosisSteps.length]);

  const renderStepIndicator = useCallback() => {
    return (
      <View style={styles.stepIndicator}>
        {diagnosisSteps.map(step, index) => {
          const isCompleted = stepData[index] !== undefined;
          const isCurrent = index === currentStep;
          const isAccessible = index <= currentStep + 1;

          return (
            <TouchableOpacity;
              key={step.id}
              style={[
                styles.stepButton,
                isCompleted && styles.stepCompleted,
                isCurrent && styles.stepCurrent,
                !isAccessible && styles.stepDisabled,
              ]}
              onPress={() => handleStepPress(index)}
              accessibilityLabel={`${step.title}诊断步骤`}
              disabled={!isAccessible}
            >
              <Icon;
                name={step.icon}
                size={20}
                color={
                  isCompleted;
                    ? colors.white;
                    : isCurrent;
                      ? colors.primary;
                      : isAccessible;
                        ? colors.textSecondary;
                        : colors.border;
                }
              />
              <Text;
                style={[
                  styles.stepTitle,
                  isCompleted && styles.stepTitleCompleted,
                  isCurrent && styles.stepTitleCurrent,
                  !isAccessible && styles.stepTitleDisabled,
                ]}
              >
                {step.title}
              </Text>
            </TouchableOpacity>
          );
        })}
      </View>
    );
  }, [diagnosisSteps, stepData, currentStep, handleStepPress]);

  const renderCurrentStep = useCallback() => {
    const step = diagnosisSteps[currentStep];
    if (!step) return null;

    const StepComponent = step.component;

    return (
      <View style={styles.stepContent}>
        <View style={styles.stepHeader}>
          <Icon name={step.icon} size={32} color={colors.primary} />
          <View style={styles.stepInfo}>
            <Text style={styles.stepName}>{step.title}</Text>
            <Text style={styles.stepDescription}>{step.description}</Text>
          </View>
        </View>
        <View style={styles.stepComponent}>
          <StepComponent;
            onComplete={(data: any) => handleStepComplete(currentStep, data)}
            onCancel={() => {}}
          />
        </View>
      </View>
    );
  }, [diagnosisSteps, currentStep, handleStepComplete]);

  const renderProgressBar = useCallback() => {
    const progress = getProgressPercentage();
    return (
      <View style={styles.progressContainer}>
        <View style={styles.progressBar}>
          <View style={[styles.progressFill, { width: `${progress}%` }]} />
        </View>
        <Text style={styles.progressText}>
          {getCompletedStepsCount()}/{diagnosisSteps.length} 步骤完成
        </Text>
      </View>
    );
  }, [getProgressPercentage, getCompletedStepsCount, diagnosisSteps.length]);

  const renderActionButtons = useCallback() => {
    return (
      <View style={styles.actionButtons}>
        <TouchableOpacity;
          style={[styles.actionButton, styles.resetButton]}
          onPress={resetDiagnosis}
          accessibilityLabel="重置诊断数据"
        >
          <Icon name="refresh-cw" size={16} color={colors.textSecondary} />
          <Text style={styles.resetButtonText}>重置</Text>
        </TouchableOpacity>
        <TouchableOpacity;
          style={[
            styles.actionButton,
            styles.analyzeButton,
            (!canPerformAnalysis() || isAnalyzing) &&
              styles.analyzeButtonDisabled,
          ]}
          onPress={performAnalysis}
          disabled={!canPerformAnalysis() || isAnalyzing}
          accessibilityLabel="开始五诊分析"
        >
          <Icon;
            name="zap"
            size={16}
            color={
              !canPerformAnalysis() || isAnalyzing;
                ? colors.textSecondary;
                : colors.white;
            }
          />
          <Text;
            style={[
              styles.analyzeButtonText,
              (!canPerformAnalysis() || isAnalyzing) &&
                styles.analyzeButtonTextDisabled,
            ]}
          >
            {isAnalyzing ? '分析中...' : '开始分析'}
          </Text>
        </TouchableOpacity>
      </View>
    );
  }, [resetDiagnosis, canPerformAnalysis, isAnalyzing, performAnalysis]);

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* 头部 */}
      <View style={styles.header}>
        <TouchableOpacity;
          onPress={() => navigation.goBack()}
          style={styles.backButton}
          accessibilityLabel="返回上一页"
        >
          <Icon name="arrow-left" size={24} color={colors.textPrimary} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>五诊合参</Text>
        <View style={styles.headerRight} />
      </View>

      {/* 进度条 */}
      {renderProgressBar()}

      {/* 步骤指示器 */}
      {renderStepIndicator()}

      {/* 当前步骤内容 */}
      {renderCurrentStep()}

      {/* 操作按钮 */}
      {renderActionButtons()}

      {/* 结果显示 */}
      {analysisResult && (
        <View style={styles.resultContainer}>
          <Text style={styles.resultTitle}>诊断结果</Text>
          <Text style={styles.resultText}>
            {analysisResult.overallAssessment}
          </Text>
        </View>
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {,
  flex: 1,
    backgroundColor: colors.background,
  },
  header: {,
  flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  backButton: {,
  padding: spacing.sm,
  },
  headerTitle: {,
  fontSize: 18,
    fontWeight: '600',
    color: colors.textPrimary,
  },
  headerRight: {,
  width: 40,
  },
  progressContainer: {,
  paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
  },
  progressBar: {,
  height: 4,
    backgroundColor: colors.border,
    borderRadius: 2,
    marginBottom: spacing.sm,
  },
  progressFill: {,
  height: '100%',
    backgroundColor: colors.primary,
    borderRadius: 2,
  },
  progressText: {,
  fontSize: 12,
    color: colors.textSecondary,
    textAlign: 'center',
  },
  stepIndicator: {,
  flexDirection: 'row',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
  },
  stepButton: {,
  flex: 1,
    alignItems: 'center',
    paddingVertical: spacing.sm,
    marginHorizontal: spacing.xs,
    borderRadius: 8,
    backgroundColor: colors.surface,
  },
  stepCompleted: {,
  backgroundColor: colors.primary,
  },
  stepCurrent: {,
  backgroundColor: colors.surface,
    borderWidth: 2,
    borderColor: colors.primary,
  },
  stepDisabled: {,
  backgroundColor: colors.border,
  },
  stepTitle: {,
  fontSize: 12,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  stepTitleCompleted: {,
  color: colors.white,
  },
  stepTitleCurrent: {,
  color: colors.primary,
    fontWeight: '600',
  },
  stepTitleDisabled: {,
  color: colors.textTertiary,
  },
  stepContent: {,
  margin: spacing.lg,
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.lg,
  },
  stepHeader: {,
  flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.lg,
  },
  stepInfo: {,
  marginLeft: spacing.md,
    flex: 1,
  },
  stepName: {,
  fontSize: 18,
    fontWeight: '600',
    color: colors.textPrimary,
  },
  stepDescription: {,
  fontSize: 14,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  stepComponent: {,
  minHeight: 200,
  },
  actionButtons: {,
  flexDirection: 'row',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    gap: spacing.md,
  },
  actionButton: {,
  flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: spacing.md,
    borderRadius: 8,
    gap: spacing.sm,
  },
  resetButton: {,
  backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
  },
  resetButtonText: {,
  color: colors.textSecondary,
    fontSize: 16,
    fontWeight: '600',
  },
  analyzeButton: {,
  backgroundColor: colors.primary,
  },
  analyzeButtonDisabled: {,
  backgroundColor: colors.border,
  },
  analyzeButtonText: {,
  color: colors.white,
    fontSize: 16,
    fontWeight: '600',
  },
  analyzeButtonTextDisabled: {,
  color: colors.textSecondary,
  },
  resultContainer: {,
  margin: spacing.lg,
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.lg,
    borderLeftWidth: 4,
    borderLeftColor: colors.success,
  },
  resultTitle: {,
  fontSize: 18,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: spacing.md,
  },
  resultText: {,
  fontSize: 16,
    color: colors.textSecondary,
    lineHeight: 24,
  },
});

export default React.memo(FiveDiagnosisScreen);
