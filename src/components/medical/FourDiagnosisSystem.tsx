import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView, Alert } from 'react-native';
import { Text, Card, Button, ProgressBar, Chip, useTheme, Surface, Avatar } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { useTranslation } from 'react-i18next';

// 导入四诊组件
import LookDiagnosis from './LookDiagnosis';
import ListenDiagnosis from './ListenDiagnosis';
import InquiryDiagnosis from './InquiryDiagnosis';
import PalpationDiagnosis from './PalpationDiagnosis';

interface DiagnosisResult {
  look?: any;
  listen?: any;
  inquiry?: any;
  palpation?: any;
  comprehensive?: any;
}

interface FourDiagnosisSystemProps {
  onComplete?: (results: DiagnosisResult) => void;
  onCancel?: () => void;
}

const FourDiagnosisSystem: React.FC<FourDiagnosisSystemProps> = ({ 
  onComplete, 
  onCancel 
}) => {
  const theme = useTheme();
  const { t } = useTranslation();
  
  const [currentStep, setCurrentStep] = useState(0);
  const [results, setResults] = useState<DiagnosisResult>({});
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  // 四诊步骤配置
  const diagnosisSteps = [
    {
      key: 'look',
      title: '望诊',
      subtitle: '观察面色、舌象、眼神',
      icon: 'eye-outline',
      color: '#FF6B6B',
      component: LookDiagnosis,
      description: '通过观察患者的神、色、形、态等外在表现，了解脏腑功能和疾病性质。'
    },
    {
      key: 'listen',
      title: '闻诊',
      subtitle: '听声音、闻气味',
      icon: 'ear-hearing',
      color: '#4ECDC4',
      component: ListenDiagnosis,
      description: '通过听患者的语言、呼吸、咳嗽等声音，以及嗅闻体味，判断病情。'
    },
    {
      key: 'inquiry',
      title: '问诊',
      subtitle: '询问症状、病史',
      icon: 'comment-question-outline',
      color: '#45B7D1',
      component: InquiryDiagnosis,
      description: '通过询问患者的症状、病史、生活习惯等，全面了解病情。'
    },
    {
      key: 'palpation',
      title: '切诊',
      subtitle: '触摸脉搏、按压穴位',
      icon: 'hand-back-left-outline',
      color: '#96CEB4',
      component: PalpationDiagnosis,
      description: '通过触摸脉搏、按压腹部等，了解脏腑功能和气血状况。'
    }
  ];

  // 计算进度
  const progress = (currentStep + 1) / diagnosisSteps.length;
  const completedSteps = Object.keys(results).length;

  // 处理单个诊断完成
  const handleStepComplete = (stepKey: string, stepResults: any) => {
    setResults(prev => ({
      ...prev,
      [stepKey]: stepResults
    }));

    // 如果不是最后一步，自动进入下一步
    if (currentStep < diagnosisSteps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      // 所有步骤完成，进行综合分析
      performComprehensiveAnalysis({
        ...results,
        [stepKey]: stepResults
      });
    }
  };

  // 处理步骤取消
  const handleStepCancel = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    } else {
      onCancel?.();
    }
  };

  // 综合分析
  const performComprehensiveAnalysis = async (allResults: DiagnosisResult) => {
    setIsAnalyzing(true);

    try {
      // 模拟综合分析过程
      await new Promise(resolve => setTimeout(resolve, 2000));

      // 生成综合分析结果
      const comprehensiveResult = generateComprehensiveAnalysis(allResults);
      
      const finalResults = {
        ...allResults,
        comprehensive: comprehensiveResult
      };

      setResults(finalResults);
      onComplete?.(finalResults);
    } catch (error) {
      console.error('Comprehensive analysis error:', error);
      Alert.alert('分析错误', '综合分析过程中出现错误，请重试。');
    } finally {
      setIsAnalyzing(false);
    }
  };

  // 生成综合分析结果
  const generateComprehensiveAnalysis = (allResults: DiagnosisResult) => {
    // 这里应该调用AI分析服务，现在使用模拟数据
    const symptoms = [];
    const recommendations = [];
    
    // 基于各诊断结果生成综合分析
    if (allResults.look) {
      symptoms.push('面色偏淡，舌质淡红');
      recommendations.push('注意补气养血');
    }
    
    if (allResults.listen) {
      symptoms.push('声音低沉，呼吸平稳');
      recommendations.push('适当运动增强肺功能');
    }
    
    if (allResults.inquiry) {
      symptoms.push('偶有疲劳，睡眠一般');
      recommendations.push('规律作息，适当休息');
    }
    
    if (allResults.palpation) {
      symptoms.push('脉象平和，略显无力');
      recommendations.push('温补脾肾，调理气血');
    }

    return {
      constitution: '气虚质偏向',
      mainSymptoms: symptoms,
      diagnosis: '轻度气血不足，脾胃功能偏弱',
      recommendations: recommendations,
      severity: 'mild',
      confidence: 0.85,
      treatmentPlan: {
        diet: ['多食用红枣、桂圆等补血食物', '避免生冷食物'],
        lifestyle: ['保证充足睡眠', '适量运动', '避免过度劳累'],
        herbs: ['建议咨询中医师，可考虑四君子汤调理'],
        followUp: '建议1个月后复查'
      }
    };
  };

  // 渲染步骤选择器
  const renderStepSelector = () => (
    <Surface style={styles.stepSelector}>
      <ScrollView horizontal showsHorizontalScrollIndicator={false}>
        {diagnosisSteps.map((step, index) => {
          const isCompleted = results[step.key as keyof DiagnosisResult];
          const isCurrent = index === currentStep;
          
          return (
            <Card
              key={step.key}
              style={[
                styles.stepCard,
                isCurrent && styles.currentStepCard,
                isCompleted && styles.completedStepCard
              ]}
              onPress={() => setCurrentStep(index)}
            >
              <View style={styles.stepCardContent}>
                <Avatar.Icon
                  size={40}
                  icon={step.icon}
                  style={[
                    styles.stepIcon,
                    { backgroundColor: step.color }
                  ]}
                />
                <Text style={[
                  styles.stepTitle,
                  isCurrent && styles.currentStepTitle
                ]}>
                  {step.title}
                </Text>
                <Text style={styles.stepSubtitle}>
                  {step.subtitle}
                </Text>
                {isCompleted && (
                  <Chip
                    icon="check"
                    style={styles.completedChip}
                    textStyle={styles.completedChipText}
                  >
                    已完成
                  </Chip>
                )}
              </View>
            </Card>
          );
        })}
      </ScrollView>
    </Surface>
  );

  // 渲染当前步骤内容
  const renderCurrentStep = () => {
    if (isAnalyzing) {
      return (
        <Card style={styles.analysisCard}>
          <Card.Content style={styles.analysisContent}>
            <Avatar.Icon
              size={60}
              icon="brain"
              style={styles.analysisIcon}
            />
            <Text style={styles.analysisTitle}>正在进行综合分析</Text>
            <Text style={styles.analysisSubtitle}>
              AI正在整合四诊信息，生成个性化健康报告...
            </Text>
            <ProgressBar
              progress={0.7}
              color={theme.colors.primary}
              style={styles.analysisProgress}
            />
          </Card.Content>
        </Card>
      );
    }

    const currentStepConfig = diagnosisSteps[currentStep];
    const StepComponent = currentStepConfig.component;

    return (
      <View style={styles.stepContent}>
        <Card style={styles.stepDescriptionCard}>
          <Card.Content>
            <Text style={styles.stepDescription}>
              {currentStepConfig.description}
            </Text>
          </Card.Content>
        </Card>
        
        <StepComponent
          onComplete={(stepResults: any) => 
            handleStepComplete(currentStepConfig.key, stepResults)
          }
          onCancel={handleStepCancel}
        />
      </View>
    );
  };

  // 渲染进度信息
  const renderProgress = () => (
    <Surface style={styles.progressContainer}>
      <View style={styles.progressHeader}>
        <Text style={styles.progressTitle}>四诊合参进度</Text>
        <Text style={styles.progressText}>
          {completedSteps}/{diagnosisSteps.length} 已完成
        </Text>
      </View>
      <ProgressBar
        progress={progress}
        color={theme.colors.primary}
        style={styles.progressBar}
      />
    </Surface>
  );

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView}>
        {/* 标题 */}
        <View style={styles.header}>
          <Text style={styles.title}>四诊合参</Text>
          <Text style={styles.subtitle}>
            中医传统诊断方法，通过望、闻、问、切四种方式全面了解您的健康状况
          </Text>
        </View>

        {/* 进度显示 */}
        {renderProgress()}

        {/* 步骤选择器 */}
        {renderStepSelector()}

        {/* 当前步骤内容 */}
        {renderCurrentStep()}
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  scrollView: {
    flex: 1,
  },
  header: {
    padding: 20,
    alignItems: 'center',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    textAlign: 'center',
    opacity: 0.7,
    lineHeight: 22,
  },
  progressContainer: {
    margin: 16,
    padding: 16,
    borderRadius: 12,
    elevation: 2,
  },
  progressHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  progressTitle: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  progressText: {
    fontSize: 14,
    opacity: 0.7,
  },
  progressBar: {
    height: 8,
    borderRadius: 4,
  },
  stepSelector: {
    margin: 16,
    padding: 16,
    borderRadius: 12,
    elevation: 2,
  },
  stepCard: {
    width: 120,
    marginRight: 12,
    elevation: 1,
  },
  currentStepCard: {
    elevation: 4,
    borderWidth: 2,
    borderColor: '#2196F3',
  },
  completedStepCard: {
    backgroundColor: '#E8F5E8',
  },
  stepCardContent: {
    padding: 12,
    alignItems: 'center',
  },
  stepIcon: {
    marginBottom: 8,
  },
  stepTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 4,
  },
  currentStepTitle: {
    color: '#2196F3',
  },
  stepSubtitle: {
    fontSize: 12,
    textAlign: 'center',
    opacity: 0.7,
    marginBottom: 8,
  },
  completedChip: {
    backgroundColor: '#4CAF50',
  },
  completedChipText: {
    color: 'white',
    fontSize: 10,
  },
  stepContent: {
    margin: 16,
  },
  stepDescriptionCard: {
    marginBottom: 16,
    elevation: 1,
  },
  stepDescription: {
    fontSize: 14,
    lineHeight: 20,
    opacity: 0.8,
  },
  analysisCard: {
    margin: 16,
    elevation: 2,
  },
  analysisContent: {
    padding: 32,
    alignItems: 'center',
  },
  analysisIcon: {
    backgroundColor: '#2196F3',
    marginBottom: 16,
  },
  analysisTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  analysisSubtitle: {
    fontSize: 14,
    textAlign: 'center',
    opacity: 0.7,
    marginBottom: 24,
  },
  analysisProgress: {
    width: '100%',
    height: 8,
    borderRadius: 4,
  },
});

export default FourDiagnosisSystem;