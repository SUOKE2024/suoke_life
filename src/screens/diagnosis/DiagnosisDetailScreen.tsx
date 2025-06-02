import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  Image,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation, useRoute } from '@react-navigation/native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { colors, spacing } from '../../constants/theme';

interface DiagnosisStep {
  id: string;
  name: string;
  description: string;
  icon: string;
  status: 'pending' | 'in-progress' | 'completed' | 'skipped';
  result?: string;
  confidence?: number;
  duration?: string;
}

interface DiagnosisResult {
  id: string;
  syndrome: string;
  confidence: number;
  description: string;
  recommendations: string[];
  severity: 'mild' | 'moderate' | 'severe';
}

interface DiagnosisDetailParams {
  diagnosisType: 'look' | 'listen' | 'inquiry' | 'palpation' | 'comprehensive';
  patientId?: string;
}

const DiagnosisDetailScreen: React.FC = () => {
  const navigation = useNavigation();
  const route = useRoute();
  const params = route.params as DiagnosisDetailParams;
  
  const [steps, setSteps] = useState<DiagnosisStep[]>([]);
  const [currentStep, setCurrentStep] = useState(0);
  const [results, setResults] = useState<DiagnosisResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [isCompleted, setIsCompleted] = useState(false);

  useEffect(() => {
    initializeDiagnosis();
  }, []);

  const initializeDiagnosis = () => {
    const diagnosisSteps = getDiagnosisSteps(params.diagnosisType);
    setSteps(diagnosisSteps);
  };

  const getDiagnosisSteps = (type: string): DiagnosisStep[] => {
    switch (type) {
      case 'look':
        return [
          {
            id: 'face-observation',
            name: '面部观察',
            description: '观察面色、神态、表情',
            icon: 'face-recognition',
            status: 'pending'
          },
          {
            id: 'tongue-observation',
            name: '舌诊',
            description: '观察舌质、舌苔',
            icon: 'mouth',
            status: 'pending'
          },
          {
            id: 'body-observation',
            name: '形体观察',
            description: '观察体型、姿态、动作',
            icon: 'human',
            status: 'pending'
          }
        ];
      case 'listen':
        return [
          {
            id: 'voice-analysis',
            name: '声音分析',
            description: '分析语音、语调、音量',
            icon: 'microphone',
            status: 'pending'
          },
          {
            id: 'breathing-analysis',
            name: '呼吸音分析',
            description: '听诊呼吸音',
            icon: 'lungs',
            status: 'pending'
          },
          {
            id: 'cough-analysis',
            name: '咳嗽音分析',
            description: '分析咳嗽特征',
            icon: 'cough',
            status: 'pending'
          }
        ];
      case 'inquiry':
        return [
          {
            id: 'symptom-inquiry',
            name: '症状询问',
            description: '询问主要症状和不适',
            icon: 'comment-question',
            status: 'pending'
          },
          {
            id: 'history-inquiry',
            name: '病史询问',
            description: '了解既往病史',
            icon: 'history',
            status: 'pending'
          },
          {
            id: 'lifestyle-inquiry',
            name: '生活习惯询问',
            description: '了解饮食、作息等',
            icon: 'food-apple',
            status: 'pending'
          }
        ];
      case 'palpation':
        return [
          {
            id: 'pulse-diagnosis',
            name: '脉诊',
            description: '触诊脉象',
            icon: 'heart-pulse',
            status: 'pending'
          },
          {
            id: 'acupoint-palpation',
            name: '穴位触诊',
            description: '触诊相关穴位',
            icon: 'hand-pointing-up',
            status: 'pending'
          },
          {
            id: 'abdomen-palpation',
            name: '腹部触诊',
            description: '触诊腹部',
            icon: 'stomach',
            status: 'pending'
          }
        ];
      default:
        return [
          {
            id: 'comprehensive-analysis',
            name: '综合分析',
            description: '整合四诊信息',
            icon: 'brain',
            status: 'pending'
          }
        ];
    }
  };

  const startDiagnosis = async () => {
    setLoading(true);
    
    try {
      // 模拟诊断过程
      for (let i = 0; i < steps.length; i++) {
        setCurrentStep(i);
        setSteps(prev => prev.map((step, index) => 
          index === i ? { ...step, status: 'in-progress' } : step
        ));
        
        // 模拟诊断时间
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // 模拟诊断结果
        const mockResult = generateMockResult(steps[i]);
        
        setSteps(prev => prev.map((step, index) => 
          index === i ? { 
            ...step, 
            status: 'completed',
            result: mockResult.result,
            confidence: mockResult.confidence,
            duration: mockResult.duration
          } : step
        ));
      }
      
      // 生成最终诊断结果
      const finalResults = generateFinalResults();
      setResults(finalResults);
      setIsCompleted(true);
      
    } catch (error) {
      console.error('诊断过程出错:', error);
      Alert.alert('错误', '诊断过程中出现错误，请重试');
    } finally {
      setLoading(false);
    }
  };

  const generateMockResult = (step: DiagnosisStep) => {
    const results = {
      'face-observation': {
        result: '面色微黄，神态疲倦，眼神略显无力',
        confidence: 85,
        duration: '2分钟'
      },
      'tongue-observation': {
        result: '舌质淡红，舌苔薄白，舌体略胖',
        confidence: 90,
        duration: '1分钟'
      },
      'voice-analysis': {
        result: '声音低沉，语速较慢，音量偏小',
        confidence: 78,
        duration: '3分钟'
      },
      'pulse-diagnosis': {
        result: '脉象细弱，节律规整，脉率68次/分',
        confidence: 92,
        duration: '5分钟'
      }
    };
    
    return results[step.id as keyof typeof results] || {
      result: '检查正常',
      confidence: 80,
      duration: '2分钟'
    };
  };

  const generateFinalResults = (): DiagnosisResult[] => {
    return [
      {
        id: '1',
        syndrome: '脾气虚证',
        confidence: 87,
        description: '脾气虚弱，运化失常，气血生化不足',
        recommendations: [
          '健脾益气，调理脾胃',
          '适量运动，增强体质',
          '规律作息，避免过度劳累',
          '饮食清淡，易消化为主'
        ],
        severity: 'mild'
      },
      {
        id: '2',
        syndrome: '气血不足',
        confidence: 75,
        description: '气血亏虚，脏腑功能减退',
        recommendations: [
          '补气养血，调理气血',
          '加强营养，多食补血食物',
          '适当休息，避免熬夜'
        ],
        severity: 'mild'
      }
    ];
  };

  const getSeverityColor = (severity: DiagnosisResult['severity']) => {
    switch (severity) {
      case 'mild':
        return colors.success;
      case 'moderate':
        return colors.warning;
      case 'severe':
        return colors.error;
      default:
        return colors.textSecondary;
    }
  };

  const getSeverityText = (severity: DiagnosisResult['severity']) => {
    switch (severity) {
      case 'mild':
        return '轻度';
      case 'moderate':
        return '中度';
      case 'severe':
        return '重度';
      default:
        return '未知';
    }
  };

  const getStepStatusIcon = (status: DiagnosisStep['status']) => {
    switch (status) {
      case 'completed':
        return 'check-circle';
      case 'in-progress':
        return 'clock';
      case 'pending':
        return 'circle-outline';
      case 'skipped':
        return 'close-circle';
      default:
        return 'circle-outline';
    }
  };

  const getStepStatusColor = (status: DiagnosisStep['status']) => {
    switch (status) {
      case 'completed':
        return colors.success;
      case 'in-progress':
        return colors.primary;
      case 'pending':
        return colors.textSecondary;
      case 'skipped':
        return colors.error;
      default:
        return colors.textSecondary;
    }
  };

  const renderStep = (step: DiagnosisStep, index: number) => (
    <View key={step.id} style={styles.stepCard}>
      <View style={styles.stepHeader}>
        <View style={styles.stepIcon}>
          <Icon name={step.icon} size={24} color={colors.primary} />
        </View>
        <View style={styles.stepInfo}>
          <Text style={styles.stepName}>{step.name}</Text>
          <Text style={styles.stepDescription}>{step.description}</Text>
        </View>
        <View style={styles.stepStatus}>
          <Icon 
            name={getStepStatusIcon(step.status)} 
            size={24} 
            color={getStepStatusColor(step.status)} 
          />
        </View>
      </View>
      
      {step.result && (
        <View style={styles.stepResult}>
          <Text style={styles.resultLabel}>检查结果:</Text>
          <Text style={styles.resultText}>{step.result}</Text>
          {step.confidence && (
            <View style={styles.confidenceContainer}>
              <Text style={styles.confidenceLabel}>可信度: </Text>
              <Text style={styles.confidenceValue}>{step.confidence}%</Text>
            </View>
          )}
          {step.duration && (
            <Text style={styles.durationText}>用时: {step.duration}</Text>
          )}
        </View>
      )}
    </View>
  );

  const renderResult = (result: DiagnosisResult) => (
    <View key={result.id} style={styles.resultCard}>
      <View style={styles.resultHeader}>
        <Text style={styles.syndromeName}>{result.syndrome}</Text>
        <View style={[styles.severityBadge, { backgroundColor: getSeverityColor(result.severity) }]}>
          <Text style={styles.severityText}>{getSeverityText(result.severity)}</Text>
        </View>
      </View>
      
      <View style={styles.confidenceBar}>
        <Text style={styles.confidenceLabel}>可信度</Text>
        <View style={styles.progressBar}>
          <View 
            style={[
              styles.progressFill, 
              { 
                width: `${result.confidence}%`,
                backgroundColor: result.confidence > 80 ? colors.success : result.confidence > 60 ? colors.warning : colors.error
              }
            ]} 
          />
        </View>
        <Text style={styles.confidenceValue}>{result.confidence}%</Text>
      </View>
      
      <Text style={styles.resultDescription}>{result.description}</Text>
      
      <View style={styles.recommendationsSection}>
        <Text style={styles.recommendationsTitle}>调理建议:</Text>
        {result.recommendations.map((recommendation, index) => (
          <View key={index} style={styles.recommendationItem}>
            <Icon name="check" size={16} color={colors.success} />
            <Text style={styles.recommendationText}>{recommendation}</Text>
          </View>
        ))}
      </View>
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      {/* 头部 */}
      <View style={styles.header}>
        <TouchableOpacity 
          style={styles.backButton}
          onPress={() => navigation.goBack()}
        >
          <Icon name="arrow-left" size={24} color={colors.textPrimary} />
        </TouchableOpacity>
        
        <View style={styles.headerInfo}>
          <Text style={styles.headerTitle}>
            {params.diagnosisType === 'look' ? '望诊' :
             params.diagnosisType === 'listen' ? '闻诊' :
             params.diagnosisType === 'inquiry' ? '问诊' :
             params.diagnosisType === 'palpation' ? '切诊' : '综合诊断'}
          </Text>
          <Text style={styles.headerSubtitle}>中医四诊详细检查</Text>
        </View>
        
        <TouchableOpacity style={styles.helpButton}>
          <Icon name="help-circle" size={24} color={colors.textSecondary} />
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* 诊断步骤 */}
        <View style={styles.stepsSection}>
          <Text style={styles.sectionTitle}>诊断步骤</Text>
          {steps.map(renderStep)}
        </View>

        {/* 开始诊断按钮 */}
        {!isCompleted && !loading && (
          <View style={styles.actionSection}>
            <TouchableOpacity
              style={styles.startButton}
              onPress={startDiagnosis}
            >
              <Icon name="play" size={20} color={colors.white} />
              <Text style={styles.startButtonText}>开始诊断</Text>
            </TouchableOpacity>
          </View>
        )}

        {/* 加载状态 */}
        {loading && (
          <View style={styles.loadingSection}>
            <ActivityIndicator size="large" color={colors.primary} />
            <Text style={styles.loadingText}>
              正在进行 {steps[currentStep]?.name}...
            </Text>
          </View>
        )}

        {/* 诊断结果 */}
        {isCompleted && results.length > 0 && (
          <View style={styles.resultsSection}>
            <Text style={styles.sectionTitle}>诊断结果</Text>
            {results.map(renderResult)}
            
            <TouchableOpacity style={styles.saveButton}>
              <Icon name="content-save" size={20} color={colors.primary} />
              <Text style={styles.saveButtonText}>保存诊断报告</Text>
            </TouchableOpacity>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    backgroundColor: colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  backButton: {
    padding: spacing.sm,
    marginRight: spacing.sm,
  },
  headerInfo: {
    flex: 1,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: colors.textPrimary,
  },
  headerSubtitle: {
    fontSize: 14,
    color: colors.textSecondary,
  },
  helpButton: {
    padding: spacing.sm,
  },
  content: {
    flex: 1,
  },
  stepsSection: {
    padding: spacing.lg,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: spacing.md,
  },
  stepCard: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.md,
    marginBottom: spacing.md,
    borderWidth: 1,
    borderColor: colors.border,
  },
  stepHeader: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  stepIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.primaryLight,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.md,
  },
  stepInfo: {
    flex: 1,
  },
  stepName: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: 4,
  },
  stepDescription: {
    fontSize: 14,
    color: colors.textSecondary,
  },
  stepStatus: {
    marginLeft: spacing.md,
  },
  stepResult: {
    marginTop: spacing.md,
    paddingTop: spacing.md,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  resultLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  resultText: {
    fontSize: 14,
    color: colors.textSecondary,
    lineHeight: 20,
    marginBottom: spacing.sm,
  },
  confidenceContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.xs,
  },
  confidenceLabel: {
    fontSize: 12,
    color: colors.textSecondary,
  },
  confidenceValue: {
    fontSize: 12,
    fontWeight: '600',
    color: colors.primary,
  },
  durationText: {
    fontSize: 12,
    color: colors.textSecondary,
  },
  actionSection: {
    padding: spacing.lg,
  },
  startButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.primary,
    paddingVertical: spacing.md,
    borderRadius: 12,
  },
  startButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.white,
    marginLeft: spacing.sm,
  },
  loadingSection: {
    padding: spacing.xl,
    alignItems: 'center',
  },
  loadingText: {
    fontSize: 16,
    color: colors.textSecondary,
    marginTop: spacing.md,
  },
  resultsSection: {
    padding: spacing.lg,
  },
  resultCard: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.md,
    marginBottom: spacing.md,
    borderWidth: 1,
    borderColor: colors.border,
  },
  resultHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  syndromeName: {
    fontSize: 18,
    fontWeight: '600',
    color: colors.textPrimary,
  },
  severityBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  severityText: {
    fontSize: 12,
    color: colors.white,
    fontWeight: '600',
  },
  confidenceBar: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  progressBar: {
    flex: 1,
    height: 6,
    backgroundColor: colors.gray200,
    borderRadius: 3,
    marginHorizontal: spacing.sm,
  },
  progressFill: {
    height: '100%',
    borderRadius: 3,
  },
  resultDescription: {
    fontSize: 14,
    color: colors.textSecondary,
    lineHeight: 20,
    marginBottom: spacing.md,
  },
  recommendationsSection: {
    marginTop: spacing.sm,
  },
  recommendationsTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: spacing.sm,
  },
  recommendationItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: spacing.xs,
  },
  recommendationText: {
    fontSize: 14,
    color: colors.textSecondary,
    marginLeft: spacing.sm,
    flex: 1,
    lineHeight: 20,
  },
  saveButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.primary,
    paddingVertical: spacing.md,
    borderRadius: 12,
    marginTop: spacing.md,
  },
  saveButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.primary,
    marginLeft: spacing.sm,
  },
});

export default DiagnosisDetailScreen; 