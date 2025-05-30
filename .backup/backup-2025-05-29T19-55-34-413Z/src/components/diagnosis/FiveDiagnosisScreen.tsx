import {
import { useNavigation } from '@react-navigation/native';
import { fiveDiagnosisService, FiveDiagnosisInput, FiveDiagnosisResult } from '../../services/fiveDiagnosisService';


/**
 * 五诊算法主界面组件
 * 提供完整的五诊分析用户界面
 */

import React, { useState, useEffect } from 'react';
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  SafeAreaView,
  Dimensions,
} from 'react-native';

const { width, height } = Dimensions.get('window');

interface DiagnosisStep {
  id: string;
  title: string;
  description: string;
  icon: string;
  completed: boolean;
  data?: any;
}

export const FiveDiagnosisScreen: React.FC = () => {
  const navigation = useMemo(() => useMemo(() => useNavigation(), []), []);
  const [currentStep, setCurrentStep] = useState(0);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<FiveDiagnosisResult | null>(null);
  const [userId] = useState('user_123'); // 实际应该从用户状态获取

  const [diagnosisSteps, setDiagnosisSteps] = useState<DiagnosisStep[]>([
    {
      id: 'looking',
      title: '望诊',
      description: '舌象、面色、形体分析',
      icon: '👁️',
      completed: false,
    },
    {
      id: 'listening',
      title: '闻诊',
      description: '声音、气味、呼吸分析',
      icon: '👂',
      completed: false,
    },
    {
      id: 'inquiry',
      title: '问诊',
      description: '症状、病史询问',
      icon: '💬',
      completed: false,
    },
    {
      id: 'palpation',
      title: '切诊',
      description: '脉象、触诊检查',
      icon: '✋',
      completed: false,
    },
    {
      id: 'calculation',
      title: '算诊',
      description: '五行、阴阳计算',
      icon: '🧮',
      completed: false,
    },
  ]);

  useEffect(() => {
    initializeDiagnosisService();
  }, []) // TODO: 检查依赖项 // TODO: 检查依赖项;

  const initializeDiagnosisService = useMemo(() => useMemo(() => async () => {
    try {
      await fiveDiagnosisService.initialize(), []), []);
      console.log('五诊算法服务初始化完成');
    } catch (error) {
      console.error('五诊算法服务初始化失败:', error);
      Alert.alert('初始化失败', '五诊算法服务初始化失败，请重试');
    }
  };

  const handleStepPress = useMemo(() => useMemo(() => useCallback( (stepIndex: number) => {, []), []), []);
    const step = useMemo(() => useMemo(() => diagnosisSteps[stepIndex], []), []);
    
    // 暂时使用模拟数据完成步骤，实际应该导航到对应的诊断页面
    switch (step.id) {
      case 'looking':
        // 模拟望诊数据
        handleStepComplete(stepIndex, {
          tongueImage: 'mock_tongue_image_data',
          faceImage: 'mock_face_image_data',
          metadata: {
            timestamp: Date.now(),
            deviceInfo: 'iPhone',
            lightingConditions: 'natural',
          },
        });
        break;
      case 'listening':
        // 模拟闻诊数据
        handleStepComplete(stepIndex, {
          voiceRecording: 'mock_voice_data',
          breathingPattern: {
            rate: 18,
            depth: 'normal',
            rhythm: 'regular',
          },
          metadata: {
            timestamp: Date.now(),
            duration: 30,
            sampleRate: 44100,
          },
        });
        break;
      case 'inquiry':
        // 模拟问诊数据
        handleStepComplete(stepIndex, {
          symptoms: ['疲劳', '失眠', '食欲不振'],
          medicalHistory: ['高血压'],
          currentMedications: ['降压药'],
          lifestyle: {
            sleepPattern: '晚睡早起',
            dietHabits: '不规律',
            exerciseLevel: '少量',
            stressLevel: 7,
          },
          familyHistory: ['糖尿病'],
          chiefComplaint: '最近感觉疲劳乏力',
        });
        break;
      case 'palpation':
        // 模拟切诊数据
        handleStepComplete(stepIndex, {
          pulseData: {
            rate: 72,
            rhythm: 'regular',
            strength: 'moderate',
            quality: 'smooth',
          },
          temperatureData: {
            bodyTemperature: 36.5,
            skinTemperature: 32.0,
            extremityTemperature: 30.0,
          },
          touchData: {
            skinTexture: 'smooth',
            muscleTonus: 'normal',
            tenderness: [],
          },
        });
        break;
      case 'calculation':
        // 模拟算诊数据
        handleStepComplete(stepIndex, {
          birthDate: '1990-01-01',
          birthTime: '08:00',
          currentTime: new Date().toISOString(),
          location: {
            latitude: 39.9042,
            longitude: 116.4074,
          },
          seasonalFactors: {
            season: 'winter',
            climate: 'dry',
            weather: 'clear',
          },
        });
        break;
    }
  };

  const handleStepComplete = useMemo(() => useMemo(() => useCallback( (stepIndex: number, data: any) => {, []), []), []);
    const updatedSteps = useMemo(() => useMemo(() => [...diagnosisSteps], []), []);
    updatedSteps[stepIndex].completed = true;
    updatedSteps[stepIndex].data = data;
    setDiagnosisSteps(updatedSteps);
    
    // 自动进入下一步
    if (stepIndex < diagnosisSteps.length - 1) {
      setCurrentStep(stepIndex + 1);
    }
  };

  const canPerformAnalysis = useMemo(() => useMemo(() => useCallback( () => {, []), []), []);
    return diagnosisSteps.some(step => step.completed);
  };

  const performAnalysis = useMemo(() => useMemo(() => async () => {
    if (!canPerformAnalysis()) {
      Alert.alert('提示', '请至少完成一项诊断后再进行分析'), []), []);
      return;
    }

    setIsAnalyzing(true);
    
    try {
      // 构建输入数据
      const input: FiveDiagnosisInput = {
        userId,
        lookingData: diagnosisSteps.find(s => s.id === 'looking')?.data,
        listeningData: diagnosisSteps.find(s => s.id === 'listening')?.data,
        inquiryData: diagnosisSteps.find(s => s.id === 'inquiry')?.data,
        palpationData: diagnosisSteps.find(s => s.id === 'palpation')?.data,
        calculationData: diagnosisSteps.find(s => s.id === 'calculation')?.data,
      };

      // 执行五诊分析
      const result = useMemo(() => useMemo(() => await fiveDiagnosisService.performDiagnosis(input), []), []);
      setAnalysisResult(result);
      
      // 显示分析结果
      showAnalysisResult(result);
      
    } catch (error) {
      console.error('五诊分析失败:', error);
      Alert.alert('分析失败', '五诊分析过程中出现错误，请重试');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const showAnalysisResult = useMemo(() => useMemo(() => useCallback( (result: FiveDiagnosisResult) => {, []), []), []);
    const { primarySyndrome, constitutionType, healthRecommendations } = result;
    
    Alert.alert(
      '五诊分析结果',
      `主要证候: ${primarySyndrome.name}\n` +
      `体质类型: ${constitutionType.type}\n` +
      `整体置信度: ${(result.overallConfidence * 100).toFixed(1)}%\n` +
      `证候置信度: ${(primarySyndrome.confidence * 100).toFixed(1)}%\n\n` +
      `证候描述: ${primarySyndrome.description}\n\n` +
      `治疗建议:\n${healthRecommendations.lifestyle.slice(0, 3).join('\n')}`,
      [
        { text: '查看详情', onPress: () => showDetailedResult(result) },
        { text: '确定', style: 'default' },
      ]
    );
  };

  const showDetailedResult = useMemo(() => useMemo(() => useCallback( (result: FiveDiagnosisResult) => {, []), []), []);
    // 这里可以导航到详细结果页面或显示更详细的信息
    console.log('详细分析结果:', result);
    Alert.alert(
      '详细分析结果',
      `会话ID: ${result.sessionId}\n` +
      `分析时间: ${result.timestamp}\n` +
      `数据质量: ${(result.qualityMetrics.dataQuality * 100).toFixed(1)}%\n` +
      `结果可靠性: ${(result.qualityMetrics.resultReliability * 100).toFixed(1)}%\n` +
      `完整度: ${(result.qualityMetrics.completeness * 100).toFixed(1)}%\n\n` +
      `体质特征:\n${result.constitutionType.characteristics.slice(0, 3).join('\n')}\n\n` +
      `健康建议:\n${result.constitutionType.recommendations.slice(0, 3).join('\n')}`
    );
  };

  const resetDiagnosis = useMemo(() => useMemo(() => useCallback( () => {, []), []), []);
    Alert.alert(
      '重置确认',
      '确定要重置所有诊断数据吗？',
      [
        { text: '取消', style: 'cancel' },
        {
          text: '确定',
          onPress: () => {
            const resetSteps = useMemo(() => useMemo(() => diagnosisSteps.map(step => ({
              ...step,
              completed: false,
              data: undefined,
            })), []), []);
            setDiagnosisSteps(resetSteps);
            setCurrentStep(0);
            setAnalysisResult(null);
          },
        },
      ]
    );
  };

  const getCompletedStepsCount = useMemo(() => useMemo(() => useCallback( () => {, []), []), []);
    return diagnosisSteps.filter(step => step.completed).length;
  };

  const getProgressPercentage = useMemo(() => useMemo(() => useCallback( () => {, []), []), []);
    return (getCompletedStepsCount() / diagnosisSteps.length) * 100;
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        {/* 标题区域 */}
        <View style={styles.header}>
          <Text style={styles.title}>中医五诊分析</Text>
          <Text style={styles.subtitle}>
            传统中医智慧与现代AI技术的完美结合
          </Text>
        </View>

        {/* 进度指示器 */}
        <View style={styles.progressContainer}>
          <View style={styles.progressBar}>
            <View 
              style={[
                styles.progressFill, 
                { width: `${getProgressPercentage()}%` },
              ]} 
            />
          </View>
          <Text style={styles.progressText}>
            已完成 {getCompletedStepsCount()}/{diagnosisSteps.length} 项诊断
          </Text>
        </View>

        {/* 诊断步骤列表 */}
        <View style={styles.stepsContainer}>
          {diagnosisSteps.map((step, index) => (
            <TouchableOpacity
              key={step.id}
              style={[
                styles.stepCard,
                step.completed && styles.stepCardCompleted,
                currentStep === index && styles.stepCardCurrent,
              ]}
              onPress={() => handleStepPress(index)}
              disabled={isAnalyzing}
            >
              <View style={styles.stepIcon}>
                <Text style={styles.stepIconText}>{step.icon}</Text>
                {step.completed && (
                  <View style={styles.completedBadge}>
                    <Text style={styles.completedBadgeText}>✓</Text>
                  </View>
                )}
              </View>
              
              <View style={styles.stepContent}>
                <Text style={styles.stepTitle}>{step.title}</Text>
                <Text style={styles.stepDescription}>{step.description}</Text>
                {step.completed && (
                  <Text style={styles.stepStatus}>已完成</Text>
                )}
              </View>
              
              <View style={styles.stepArrow}>
                <Text style={styles.stepArrowText}>›</Text>
              </View>
            </TouchableOpacity>
          ))}
        </View>

        {/* 操作按钮区域 */}
        <View style={styles.actionContainer}>
          <TouchableOpacity
            style={[
              styles.analyzeButton,
              !canPerformAnalysis() && styles.analyzeButtonDisabled,
            ]}
            onPress={performAnalysis}
            disabled={!canPerformAnalysis() || isAnalyzing}
          >
            {isAnalyzing ? (
              <View style={styles.loadingContainer}>
                <ActivityIndicator color="#FFFFFF" size="small" />
                <Text style={styles.analyzeButtonText}>分析中...</Text>
              </View>
            ) : (
              <Text style={styles.analyzeButtonText}>开始五诊分析</Text>
            )}
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.resetButton}
            onPress={resetDiagnosis}
            disabled={isAnalyzing}
          >
            <Text style={styles.resetButtonText}>重置</Text>
          </TouchableOpacity>
        </View>

        {/* 系统状态信息 */}
        <View style={styles.statusContainer}>
          <Text style={styles.statusTitle}>系统状态</Text>
          <View style={styles.statusItem}>
            <Text style={styles.statusLabel}>算法引擎:</Text>
            <Text style={styles.statusValue}>正常运行</Text>
          </View>
          <View style={styles.statusItem}>
            <Text style={styles.statusLabel}>知识库:</Text>
            <Text style={styles.statusValue}>已加载</Text>
          </View>
          <View style={styles.statusItem}>
            <Text style={styles.statusLabel}>质量控制:</Text>
            <Text style={styles.statusValue}>已启用</Text>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = useMemo(() => useMemo(() => StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F9FA',
  },
  scrollView: {
    flex: 1,
  },
  header: {
    padding: 20,
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E9ECEF',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#2C3E50',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#6C757D',
    textAlign: 'center',
    lineHeight: 22,
  },
  progressContainer: {
    padding: 20,
    backgroundColor: '#FFFFFF',
    marginTop: 10,
  },
  progressBar: {
    height: 8,
    backgroundColor: '#E9ECEF',
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#28A745',
    borderRadius: 4,
  },
  progressText: {
    fontSize: 14,
    color: '#6C757D',
    textAlign: 'center',
    marginTop: 8,
  },
  stepsContainer: {
    padding: 20,
    paddingTop: 10,
  },
  stepCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    padding: 16,
    marginBottom: 12,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#E9ECEF',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  stepCardCompleted: {
    borderColor: '#28A745',
    backgroundColor: '#F8FFF9',
  },
  stepCardCurrent: {
    borderColor: '#007BFF',
    backgroundColor: '#F8F9FF',
  },
  stepIcon: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: '#F8F9FA',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
    position: 'relative',
  },
  stepIconText: {
    fontSize: 24,
  },
  completedBadge: {
    position: 'absolute',
    top: -4,
    right: -4,
    width: 20,
    height: 20,
    borderRadius: 10,
    backgroundColor: '#28A745',
    justifyContent: 'center',
    alignItems: 'center',
  },
  completedBadgeText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: 'bold',
  },
  stepContent: {
    flex: 1,
  },
  stepTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2C3E50',
    marginBottom: 4,
  },
  stepDescription: {
    fontSize: 14,
    color: '#6C757D',
    lineHeight: 20,
  },
  stepStatus: {
    fontSize: 12,
    color: '#28A745',
    fontWeight: 'bold',
    marginTop: 4,
  },
  stepArrow: {
    width: 24,
    height: 24,
    justifyContent: 'center',
    alignItems: 'center',
  },
  stepArrowText: {
    fontSize: 20,
    color: '#6C757D',
  },
  actionContainer: {
    padding: 20,
    paddingTop: 10,
  },
  analyzeButton: {
    backgroundColor: '#007BFF',
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 4,
  },
  analyzeButtonDisabled: {
    backgroundColor: '#6C757D',
  },
  analyzeButtonText: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: 'bold',
  },
  loadingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  resetButton: {
    backgroundColor: '#FFFFFF',
    paddingVertical: 12,
    borderRadius: 12,
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#DC3545',
  },
  resetButtonText: {
    color: '#DC3545',
    fontSize: 16,
    fontWeight: 'bold',
  },
  statusContainer: {
    margin: 20,
    marginTop: 10,
    padding: 16,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#E9ECEF',
  },
  statusTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#2C3E50',
    marginBottom: 12,
  },
  statusItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 4,
  },
  statusLabel: {
    fontSize: 14,
    color: '#6C757D',
  },
  statusValue: {
    fontSize: 14,
    color: '#28A745',
    fontWeight: 'bold',
  },
}), []), []);

export default FiveDiagnosisScreen; 