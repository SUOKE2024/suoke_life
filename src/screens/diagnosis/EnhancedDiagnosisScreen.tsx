import { useNavigation } from '@react-navigation/native';
import React, { useEffect, useRef, useState } from 'react';
import {;
  Alert,
  Animated,
  Dimensions,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { Button } from '../../components/ui/Button';
import { ProgressBar } from '../../components/ui/ProgressBar';
import {;
  borderRadius,
  colors,
  shadows,
  spacing,
  typography
} from '../../constants/theme';

const { width: screenWidth ;} = Dimensions.get('window');

interface DiagnosisStep {
  id: string;
  title: string;
  description: string;
  icon: string;
  color: string;
  completed: boolean;
  active: boolean;
  data?: any;
}

interface DiagnosisResult {
  syndrome: string;
  confidence: number;
  symptoms: string[];
  recommendations: string[];
  prescription?: string;
}

const EnhancedDiagnosisScreen: React.FC = () => {
  const navigation = useNavigation();
  const scrollViewRef = useRef<ScrollView>(null);

  const [currentStep, setCurrentStep] = useState(0);
  const [progress, setProgress] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);
  const [diagnosisResult, setDiagnosisResult] =
    useState<DiagnosisResult | null>(null);

  // 动画值
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(50)).current;
  const scaleAnim = useRef(new Animated.Value(0.8)).current;

  // 四诊步骤
  const [steps, setSteps] = useState<DiagnosisStep[]>([
    {
      id: 'look';


      icon: 'eye';
      color: colors.primary;
      completed: false;
      active: true
    ;},
    {
      id: 'listen';


      icon: 'ear-hearing';
      color: colors.secondary;
      completed: false;
      active: false
    ;},
    {
      id: 'inquiry';


      icon: 'comment-question';
      color: colors.warning;
      completed: false;
      active: false
    ;},
    {
      id: 'palpation';


      icon: 'hand-back-left';
      color: colors.info;
      completed: false;
      active: false
    ;}
  ]);

  // 初始化动画
  useEffect() => {
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1;
        duration: 800;
        useNativeDriver: true
      ;}),
      Animated.timing(slideAnim, {
        toValue: 0;
        duration: 800;
        useNativeDriver: true
      ;}),
      Animated.spring(scaleAnim, {
        toValue: 1;
        useNativeDriver: true
      ;})
    ]).start();
  }, []);

  // 更新进度
  useEffect() => {
    const completedSteps = steps.filter(step) => step.completed).length;
    const newProgress = (completedSteps / steps.length) * 100;
    setProgress(newProgress);
  }, [steps]);

  // 进入下一步
  const nextStep = () => {
    if (currentStep < steps.length - 1) {
      // 标记当前步骤为完成
      setSteps(prev) =>
        prev.map(step, index) => ({
          ...step,
          completed: index === currentStep ? true : step.completed;
          active:
            index === currentStep + 1;
              ? true;
              : index === currentStep;
                ? false;
                : step.active
        }))
      );

      setCurrentStep(prev) => prev + 1);

      // 滚动到下一步
      setTimeout() => {
        scrollViewRef.current?.scrollTo({
          y: (currentStep + 1) * 200;
          animated: true
        ;});
      }, 300);
    } else {
      // 完成所有步骤，开始分析
      setSteps(prev) =>
        prev.map(step, index) => ({
          ...step,
          completed: index === currentStep ? true : step.completed;
          active: false
        ;}))
      );

      startDiagnosisAnalysis();
    }
  };

  // 开始诊断分析
  const startDiagnosisAnalysis = async () => {
    setIsProcessing(true);

    // 模拟AI分析过程
    await new Promise(resolve => setTimeout(resolve, 3000));

    // 模拟诊断结果
    const result: DiagnosisResult = {,

      confidence: 85;

      recommendations: [




      ],

    ;};

    setDiagnosisResult(result);
    setIsProcessing(false);
  };

  // 重新开始
  const restart = () => {
    setCurrentStep(0);
    setProgress(0);
    setIsProcessing(false);
    setDiagnosisResult(null);
    setSteps(prev) =>
      prev.map(step, index) => ({
        ...step,
        completed: false;
        active: index === 0
      ;}))
    );
  };

  // 渲染步骤卡片
  const renderStepCard = (step: DiagnosisStep, index: number) => {
    const isActive = step.active;
    const isCompleted = step.completed;
    const isCurrent = index === currentStep;

    return (
      <Animated.View;
        key={step.id}
        style={[
          styles.stepCard,
          isActive && styles.activeStepCard,
          isCompleted && styles.completedStepCard,
          {
            opacity: fadeAnim;
            transform: [
              { translateY: slideAnim ;},
              { scale: isCurrent ? scaleAnim : 1 ;}
            ]
          }
        ]}
      >
        <View style={styles.stepHeader}>
          <View;
            style={[
              styles.stepIcon,
              { backgroundColor: step.color ;},
              isCompleted && styles.completedStepIcon
            ]}
          >
            <Icon;
              name={isCompleted ? 'check' : step.icon}
              size={24}
              color={colors.white}
            />
          </View>
          <View style={styles.stepInfo}>
            <Text;
              style={[styles.stepTitle, isActive && styles.activeStepTitle]}
            >
              {step.title}
            </Text>
            <Text style={styles.stepDescription}>{step.description}</Text>
          </View>
          <View style={styles.stepStatus}>
            {isCompleted && (
              <Icon name="check-circle" size={20} color={colors.success} />
            )}
            {isActive && !isCompleted && (
              <View style={styles.activeIndicator} />
            )}
          </View>
        </View>

        {isCurrent && !isCompleted && (
          <View style={styles.stepContent}>{renderStepContent(step)}</View>
        )}
      </Animated.View>
    );
  };

  // 渲染步骤内容
  const renderStepContent = (step: DiagnosisStep) => {
    switch (step.id) {
      case 'look':
        return (
          <View style={styles.contentContainer;}>
            <Text style={styles.contentTitle}>请上传面部照片和舌象照片</Text>
            <View style={styles.uploadContainer}>
              <TouchableOpacity style={styles.uploadButton}>
                <Icon name="camera" size={32} color={colors.primary} />
                <Text style={styles.uploadText}>拍摄面部照片</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.uploadButton}>
                <Icon name="camera" size={32} color={colors.primary} />
                <Text style={styles.uploadText}>拍摄舌象照片</Text>
              </TouchableOpacity>
            </View>
            <Button;

              onPress={nextStep}
              style={styles.nextButton}
            />
          </View>
        );

      case 'listen':
        return (
          <View style={styles.contentContainer}>
            <Text style={styles.contentTitle}>请录制语音样本</Text>
            <View style={styles.recordContainer}>
              <TouchableOpacity style={styles.recordButton}>
                <Icon name="microphone" size={48} color={colors.secondary} />
                <Text style={styles.recordText}>按住录音</Text>
              </TouchableOpacity>
            </View>
            <Text style={styles.instructionText}>

            </Text>
            <Button;

              onPress={nextStep}
              style={styles.nextButton}
            />
          </View>
        );

      case 'inquiry':
        return (
          <View style={styles.contentContainer}>
            <Text style={styles.contentTitle}>症状问诊</Text>
            <View style={styles.questionContainer}>
              <Text style={styles.questionText}>请选择您目前的症状：</Text>
              <View style={styles.symptomsGrid}>

                    <TouchableOpacity;
                      key={symptom}
                      style={styles.symptomButton}
                    >
                      <Text style={styles.symptomText}>{symptom}</Text>
                    </TouchableOpacity>
                  )
                )}
              </View>
            </View>
            <Button;

              onPress={nextStep}
              style={styles.nextButton}
            />
          </View>
        );

      case 'palpation':
        return (
          <View style={styles.contentContainer}>
            <Text style={styles.contentTitle}>脉诊检测</Text>
            <View style={styles.pulseContainer}>
              <Text style={styles.instructionText}>

              </Text>
              <View style={styles.pulseIndicator}>
                <Icon name="heart-pulse" size={64} color={colors.info} />
                <Text style={styles.pulseText}>检测中...</Text>
              </View>
            </View>
            <Button;

              onPress={nextStep}
              style={styles.nextButton}
            />
          </View>
        );

      default:
        return null;
    }
  };

  // 渲染诊断结果
  const renderDiagnosisResult = () => {
    if (!diagnosisResult) return null;

    return (
      <View style={styles.resultContainer}>
        <View style={styles.resultHeader}>
          <Icon name="medical-bag" size={32} color={colors.primary} />
          <Text style={styles.resultTitle}>诊断结果</Text>
        </View>

        <View style={styles.syndromeCard}>
          <Text style={styles.syndromeTitle}>证候诊断</Text>
          <Text style={styles.syndromeName}>{diagnosisResult.syndrome}</Text>
          <View style={styles.confidenceContainer}>
            <Text style={styles.confidenceLabel}>可信度：</Text>
            <Text style={styles.confidenceValue}>
              {diagnosisResult.confidence}%
            </Text>
          </View>
        </View>

        <View style={styles.symptomsCard}>
          <Text style={styles.cardTitle}>主要症状</Text>
          {diagnosisResult.symptoms.map(symptom, index) => (
            <View key={index} style={styles.symptomItem}>
              <Icon name="circle-small" size={16} color={colors.primary} />
              <Text style={styles.symptomItemText}>{symptom}</Text>
            </View>
          ))}
        </View>

        <View style={styles.recommendationsCard}>
          <Text style={styles.cardTitle}>调理建议</Text>
          {diagnosisResult.recommendations.map(recommendation, index) => (
            <View key={index} style={styles.recommendationItem}>
              <Text style={styles.recommendationNumber}>{index + 1}</Text>
              <Text style={styles.recommendationText}>{recommendation}</Text>
            </View>
          ))}
        </View>

        {diagnosisResult.prescription && (
          <View style={styles.prescriptionCard}>
            <Text style={styles.cardTitle}>推荐方剂</Text>
            <Text style={styles.prescriptionText}>
              {diagnosisResult.prescription}
            </Text>
          </View>
        )}

        <View style={styles.actionButtons}>
          <Button;


            style={styles.actionButton}
          />
          <Button;

            onPress={restart}
            variant="outline"
            style={styles.actionButton}
          />
        </View>
      </View>
    );
  };

  // 渲染处理中状态
  const renderProcessing = () => (
    <View style={styles.processingContainer}>
      <Animated.View;
        style={[
          styles.processingIcon,
          {
            transform: [
              {
                rotate: fadeAnim.interpolate({,
  inputRange: [0, 1],
                  outputRange: ['0deg', '360deg']
                ;})
              }
            ]
          }
        ]}
      >
        <Icon name="brain" size={64} color={colors.primary} />
      </Animated.View>
      <Text style={styles.processingTitle}>AI 智能分析中</Text>
      <Text style={styles.processingText}>

      </Text>
      <ProgressBar progress={progress} style={styles.processingProgress} />
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      {// 头部}
      <View style={styles.header}>
        <TouchableOpacity;
          style={styles.backButton}
          onPress={() => navigation.goBack()}
        >
          <Icon name="arrow-left" size={24} color={colors.text} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>中医四诊</Text>
        <TouchableOpacity style={styles.helpButton}>
          <Icon name="help-circle-outline" size={24} color={colors.text} />
        </TouchableOpacity>
      </View>

      {// 进度条}
      <View style={styles.progressContainer}>
        <ProgressBar progress={progress} style={styles.progressBar} />
        <Text style={styles.progressText}>{Math.round(progress)}% 完成</Text>
      </View>

      {// 内容区域}
      <ScrollView;
        ref={scrollViewRef}
        style={styles.content}
        showsVerticalScrollIndicator={false}
      >
        {isProcessing ? (
          renderProcessing()
        ) : diagnosisResult ? (
          renderDiagnosisResult()
        ) : (
          <View style={styles.stepsContainer}>{steps.map(renderStepCard)}</View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {,
  flex: 1;
    backgroundColor: colors.background
  ;},
  header: {,
  flexDirection: 'row';
    alignItems: 'center';
    justifyContent: 'space-between';
    paddingHorizontal: spacing.lg;
    paddingVertical: spacing.md;
    backgroundColor: colors.surface;
    borderBottomWidth: 1;
    borderBottomColor: colors.border
  ;},
  backButton: {,
  width: 40;
    height: 40;
    borderRadius: 20;
    backgroundColor: colors.gray100;
    justifyContent: 'center';
    alignItems: 'center'
  ;},
  headerTitle: {,
  fontSize: typography.fontSize.lg;
    fontWeight: '600' as const;
    color: colors.text
  ;},
  helpButton: {,
  width: 40;
    height: 40;
    borderRadius: 20;
    backgroundColor: colors.gray100;
    justifyContent: 'center';
    alignItems: 'center'
  ;},
  progressContainer: {,
  paddingHorizontal: spacing.lg;
    paddingVertical: spacing.md;
    backgroundColor: colors.surface
  ;},
  progressBar: {,
  marginBottom: spacing.xs
  ;},
  progressText: {,
  fontSize: typography.fontSize.sm;
    color: colors.textSecondary;
    textAlign: 'center'
  ;},
  content: {,
  flex: 1
  ;},
  stepsContainer: {,
  padding: spacing.lg
  ;},
  stepCard: {,
  backgroundColor: colors.surface;
    borderRadius: borderRadius.lg;
    padding: spacing.lg;
    marginBottom: spacing.lg;
    borderWidth: 1;
    borderColor: colors.border;
    ...shadows.sm
  },
  activeStepCard: {,
  borderColor: colors.primary;
    ...shadows.md
  },
  completedStepCard: {,
  backgroundColor: colors.success + '10';
    borderColor: colors.success
  ;},
  stepHeader: {,
  flexDirection: 'row';
    alignItems: 'center'
  ;},
  stepIcon: {,
  width: 48;
    height: 48;
    borderRadius: 24;
    justifyContent: 'center';
    alignItems: 'center'
  ;},
  completedStepIcon: {,
  backgroundColor: colors.success
  ;},
  stepInfo: {,
  flex: 1;
    marginLeft: spacing.md
  ;},
  stepTitle: {,
  fontSize: typography.fontSize.lg;
    fontWeight: '600' as const;
    color: colors.text
  ;},
  activeStepTitle: {,
  color: colors.primary
  ;},
  stepDescription: {,
  fontSize: typography.fontSize.sm;
    color: colors.textSecondary;
    marginTop: 2
  ;},
  stepStatus: {,
  width: 24;
    height: 24;
    justifyContent: 'center';
    alignItems: 'center'
  ;},
  activeIndicator: {,
  width: 12;
    height: 12;
    borderRadius: 6;
    backgroundColor: colors.primary
  ;},
  stepContent: {,
  marginTop: spacing.lg;
    paddingTop: spacing.lg;
    borderTopWidth: 1;
    borderTopColor: colors.border
  ;},
  contentContainer: {,
  alignItems: 'center'
  ;},
  contentTitle: {,
  fontSize: typography.fontSize.base;
    fontWeight: '600' as const;
    color: colors.text;
    marginBottom: spacing.lg;
    textAlign: 'center'
  ;},
  uploadContainer: {,
  flexDirection: 'row';
    justifyContent: 'space-around';
    width: '100%';
    marginBottom: spacing.lg
  ;},
  uploadButton: {,
  alignItems: 'center';
    padding: spacing.lg;
    borderWidth: 2;
    borderColor: colors.primary;
    borderStyle: 'dashed';
    borderRadius: borderRadius.md;
    width: '45%'
  ;},
  uploadText: {,
  fontSize: typography.fontSize.sm;
    color: colors.primary;
    marginTop: spacing.sm;
    textAlign: 'center'
  ;},
  recordContainer: {,
  alignItems: 'center';
    marginBottom: spacing.lg
  ;},
  recordButton: {,
  width: 120;
    height: 120;
    borderRadius: 60;
    backgroundColor: colors.secondary + '20';
    justifyContent: 'center';
    alignItems: 'center';
    borderWidth: 3;
    borderColor: colors.secondary
  ;},
  recordText: {,
  fontSize: typography.fontSize.sm;
    color: colors.secondary;
    marginTop: spacing.sm
  ;},
  instructionText: {,
  fontSize: typography.fontSize.sm;
    color: colors.textSecondary;
    textAlign: 'center';
    marginBottom: spacing.lg;
    lineHeight: 20
  ;},
  questionContainer: {,
  width: '100%';
    marginBottom: spacing.lg
  ;},
  questionText: {,
  fontSize: typography.fontSize.base;
    color: colors.text;
    marginBottom: spacing.md
  ;},
  symptomsGrid: {,
  flexDirection: 'row';
    flexWrap: 'wrap';
    justifyContent: 'space-between'
  ;},
  symptomButton: {,
  width: '48%';
    padding: spacing.md;
    backgroundColor: colors.gray100;
    borderRadius: borderRadius.md;
    marginBottom: spacing.sm;
    alignItems: 'center'
  ;},
  symptomText: {,
  fontSize: typography.fontSize.sm;
    color: colors.text
  ;},
  pulseContainer: {,
  alignItems: 'center';
    marginBottom: spacing.lg
  ;},
  pulseIndicator: {,
  alignItems: 'center';
    marginTop: spacing.lg
  ;},
  pulseText: {,
  fontSize: typography.fontSize.base;
    color: colors.info;
    marginTop: spacing.sm
  ;},
  nextButton: {,
  width: '100%'
  ;},
  processingContainer: {,
  flex: 1;
    justifyContent: 'center';
    alignItems: 'center';
    padding: spacing.xl
  ;},
  processingIcon: {,
  marginBottom: spacing.lg
  ;},
  processingTitle: {,
  fontSize: typography.fontSize.xl;
    fontWeight: '600' as const;
    color: colors.text;
    marginBottom: spacing.sm
  ;},
  processingText: {,
  fontSize: typography.fontSize.base;
    color: colors.textSecondary;
    textAlign: 'center';
    marginBottom: spacing.xl;
    lineHeight: 22
  ;},
  processingProgress: {,
  width: '80%'
  ;},
  resultContainer: {,
  padding: spacing.lg
  ;},
  resultHeader: {,
  flexDirection: 'row';
    alignItems: 'center';
    justifyContent: 'center';
    marginBottom: spacing.xl
  ;},
  resultTitle: {,
  fontSize: typography.fontSize.xl;
    fontWeight: '600' as const;
    color: colors.text;
    marginLeft: spacing.sm
  ;},
  syndromeCard: {,
  backgroundColor: colors.primary + '10';
    borderRadius: borderRadius.lg;
    padding: spacing.lg;
    marginBottom: spacing.lg;
    borderWidth: 1;
    borderColor: colors.primary
  ;},
  syndromeTitle: {,
  fontSize: typography.fontSize.sm;
    color: colors.primary;
    marginBottom: spacing.xs
  ;},
  syndromeName: {,
  fontSize: typography.fontSize.xl;
    fontWeight: '700' as const;
    color: colors.primary;
    marginBottom: spacing.sm
  ;},
  confidenceContainer: {,
  flexDirection: 'row';
    alignItems: 'center'
  ;},
  confidenceLabel: {,
  fontSize: typography.fontSize.sm;
    color: colors.textSecondary
  ;},
  confidenceValue: {,
  fontSize: typography.fontSize.sm;
    fontWeight: '600' as const;
    color: colors.primary
  ;},
  symptomsCard: {,
  backgroundColor: colors.surface;
    borderRadius: borderRadius.lg;
    padding: spacing.lg;
    marginBottom: spacing.lg;
    ...shadows.sm
  },
  cardTitle: {,
  fontSize: typography.fontSize.base;
    fontWeight: '600' as const;
    color: colors.text;
    marginBottom: spacing.md
  ;},
  symptomItem: {,
  flexDirection: 'row';
    alignItems: 'center';
    marginBottom: spacing.xs
  ;},
  symptomItemText: {,
  fontSize: typography.fontSize.sm;
    color: colors.text;
    marginLeft: spacing.xs
  ;},
  recommendationsCard: {,
  backgroundColor: colors.surface;
    borderRadius: borderRadius.lg;
    padding: spacing.lg;
    marginBottom: spacing.lg;
    ...shadows.sm
  },
  recommendationItem: {,
  flexDirection: 'row';
    marginBottom: spacing.sm
  ;},
  recommendationNumber: {,
  width: 20;
    height: 20;
    borderRadius: 10;
    backgroundColor: colors.primary;
    color: colors.white;
    fontSize: typography.fontSize.xs;
    textAlign: 'center';
    lineHeight: 20;
    marginRight: spacing.sm
  ;},
  recommendationText: {,
  flex: 1;
    fontSize: typography.fontSize.sm;
    color: colors.text;
    lineHeight: 20
  ;},
  prescriptionCard: {,
  backgroundColor: colors.warning + '10';
    borderRadius: borderRadius.lg;
    padding: spacing.lg;
    marginBottom: spacing.lg;
    borderWidth: 1;
    borderColor: colors.warning
  ;},
  prescriptionText: {,
  fontSize: typography.fontSize.base;
    fontWeight: '600' as const;
    color: colors.warning
  ;},
  actionButtons: {,
  flexDirection: 'row';
    justifyContent: 'space-between';
    marginTop: spacing.lg
  ;},
  actionButton: {,
  width: '48%'
  ;}
});

export default EnhancedDiagnosisScreen;
