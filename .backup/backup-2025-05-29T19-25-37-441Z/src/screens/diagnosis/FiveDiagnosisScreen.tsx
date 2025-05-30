/**
 * 五诊诊断主界面
 * 提供完整的五诊诊断流程界面
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  Dimensions,
  SafeAreaView,
} from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { fiveDiagnosisService, FiveDiagnosisInput, FiveDiagnosisResult } from '../../services/fiveDiagnosisService';

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
  const [isInitialized, setIsInitialized] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [diagnosisSteps, setDiagnosisSteps] = useState<DiagnosisStep[]>([
    {
      id: 'looking',
      title: '望诊',
      description: '观察舌象、面色、形体',
      icon: '👁️',
      completed: false,
    },
    {
      id: 'listening',
      title: '闻诊',
      description: '听声音、闻气味、观呼吸',
      icon: '👂',
      completed: false,
    },
    {
      id: 'inquiry',
      title: '问诊',
      description: '询问症状、病史、生活习惯',
      icon: '💬',
      completed: false,
    },
    {
      id: 'palpation',
      title: '切诊',
      description: '脉象诊断、触诊检查',
      icon: '✋',
      completed: false,
    },
    {
      id: 'calculation',
      title: '算诊',
      description: '五行计算、阴阳分析',
      icon: '🧮',
      completed: false,
    },
  ]);
  const [diagnosisResult, setDiagnosisResult] = useState<FiveDiagnosisResult | null>(null);
  const [serviceStatus, setServiceStatus] = useState<any>(null);

  // 初始化服务
  useFocusEffect(
    useCallback(() => {
      initializeService();
      return () => {
        // 清理工作
      };
    }, [])
  );

  const initializeService = async () => {
    try {
      setIsLoading(true);
      await fiveDiagnosisService.initialize();
      setIsInitialized(true);
      updateServiceStatus();
    } catch (error) {
      console.error('初始化五诊服务失败:', error);
      Alert.alert('初始化失败', '五诊服务初始化失败，请重试');
    } finally {
      setIsLoading(false);
    }
  };

  const updateServiceStatus = () => {
    const status = fiveDiagnosisService.getServiceStatus();
    setServiceStatus(status);
  };

  const handleStepPress = (stepIndex: number) => {
    if (!isInitialized) {
      Alert.alert('提示', '服务正在初始化，请稍候');
      return;
    }
    setCurrentStep(stepIndex);
    navigateToStepScreen(diagnosisSteps[stepIndex]);
  };

  const navigateToStepScreen = (step: DiagnosisStep) => {
    // 根据诊法类型导航到相应的界面
    switch (step.id) {
      case 'looking':
        // 导航到望诊界面
        Alert.alert('望诊', '即将开启望诊功能');
        break;
      case 'listening':
        // 导航到闻诊界面
        Alert.alert('闻诊', '即将开启闻诊功能');
        break;
      case 'inquiry':
        // 导航到问诊界面
        Alert.alert('问诊', '即将开启问诊功能');
        break;
      case 'palpation':
        // 导航到切诊界面
        Alert.alert('切诊', '即将开启切诊功能');
        break;
      case 'calculation':
        // 导航到算诊界面
        Alert.alert('算诊', '即将开启算诊功能');
        break;
    }
  };

  const performCompleteDiagnosis = async () => {
    if (!isInitialized) {
      Alert.alert('提示', '服务未初始化');
      return;
    }

    try {
      setIsLoading(true);

      // 构建诊断输入数据
      const diagnosisInput: FiveDiagnosisInput = {
        userId: 'user_123', // 实际应用中从用户状态获取
        sessionId: `session_${Date.now()}`,
        lookingData: {
          tongueImage: 'mock_tongue_image',
          faceImage: 'mock_face_image',
          metadata: { timestamp: Date.now() },
        },
        calculationData: {
          birthDate: '1990-01-01',
          birthTime: '08:00',
          currentTime: new Date().toISOString(),
          metadata: { timezone: 'Asia/Shanghai' },
        },
        inquiryData: {
          symptoms: ['疲劳', '气短', '食欲不振'],
          medicalHistory: ['无重大疾病史'],
          lifestyle: { exercise: '少', sleep: '7小时', diet: '规律' },
        },
      };

      // 执行五诊分析
      const result = await fiveDiagnosisService.performDiagnosis(diagnosisInput);
      setDiagnosisResult(result);

      // 更新步骤完成状态
      const updatedSteps = diagnosisSteps.map(step => ({
        ...step,
        completed: true,
      }));
      setDiagnosisSteps(updatedSteps);

      Alert.alert('诊断完成', '五诊分析已完成，请查看结果');
    } catch (error) {
      console.error('诊断失败:', error);
      Alert.alert('诊断失败', '五诊分析失败，请重试');
    } finally {
      setIsLoading(false);
      updateServiceStatus();
    }
  };

  const renderStepCard = (step: DiagnosisStep, index: number) => (
    <TouchableOpacity
      key={step.id}
      style={[
        styles.stepCard,
        currentStep === index && styles.activeStepCard,
        step.completed && styles.completedStepCard,
      ]}
      onPress={() => handleStepPress(index)}
    >
      <View style={styles.stepIcon}>
        <Text style={styles.stepIconText}>{step.icon}</Text>
      </View>
      <View style={styles.stepContent}>
        <Text style={styles.stepTitle}>{step.title}</Text>
        <Text style={styles.stepDescription}>{step.description}</Text>
      </View>
      <View style={styles.stepStatus}>
        {step.completed ? (
          <Text style={styles.completedText}>✓</Text>
        ) : (
          <Text style={styles.pendingText}>○</Text>
        )}
      </View>
    </TouchableOpacity>
  );

  const renderDiagnosisResult = () => {
    if (!diagnosisResult) {return null;}

    return (
      <View style={styles.resultContainer}>
        <Text style={styles.resultTitle}>诊断结果</Text>
        
        <View style={styles.resultCard}>
          <Text style={styles.resultLabel}>整体置信度</Text>
          <Text style={styles.resultValue}>
            {(diagnosisResult.overallConfidence * 100).toFixed(1)}%
          </Text>
        </View>

        <View style={styles.resultCard}>
          <Text style={styles.resultLabel}>主要证候</Text>
          <Text style={styles.resultValue}>{diagnosisResult.primarySyndrome.name}</Text>
          <Text style={styles.resultDescription}>
            {diagnosisResult.primarySyndrome.description}
          </Text>
        </View>

        <View style={styles.resultCard}>
          <Text style={styles.resultLabel}>体质类型</Text>
          <Text style={styles.resultValue}>{diagnosisResult.constitutionType.type}</Text>
          <View style={styles.characteristicsList}>
            {diagnosisResult.constitutionType.characteristics.map((char, index) => (
              <Text key={index} style={styles.characteristicItem}>• {char}</Text>
            ))}
          </View>
        </View>

        <View style={styles.resultCard}>
          <Text style={styles.resultLabel}>健康建议</Text>
          <View style={styles.recommendationsList}>
            {diagnosisResult.healthRecommendations.lifestyle.map((rec, index) => (
              <Text key={index} style={styles.recommendationItem}>• {rec}</Text>
            ))}
          </View>
        </View>
      </View>
    );
  };

  const renderServiceStatus = () => {
    if (!serviceStatus) {return null;}

    return (
      <View style={styles.statusContainer}>
        <Text style={styles.statusTitle}>服务状态</Text>
        <View style={styles.statusRow}>
          <Text style={styles.statusLabel}>初始化状态:</Text>
          <Text style={[styles.statusValue, { color: serviceStatus.isInitialized ? '#4CAF50' : '#F44336' }]}>
            {serviceStatus.isInitialized ? '已初始化' : '未初始化'}
          </Text>
        </View>
        <View style={styles.statusRow}>
          <Text style={styles.statusLabel}>处理状态:</Text>
          <Text style={styles.statusValue}>
            {serviceStatus.isProcessing ? '处理中' : '空闲'}
          </Text>
        </View>
        <View style={styles.statusRow}>
          <Text style={styles.statusLabel}>成功率:</Text>
          <Text style={styles.statusValue}>
            {(serviceStatus.performanceMetrics.successRate * 100).toFixed(1)}%
          </Text>
        </View>
      </View>
    );
  };

  if (isLoading && !isInitialized) {
    return (
      <SafeAreaView style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#2196F3" />
        <Text style={styles.loadingText}>正在初始化五诊服务...</Text>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        <View style={styles.header}>
          <Text style={styles.title}>中医五诊</Text>
          <Text style={styles.subtitle}>传统中医智能诊断系统</Text>
        </View>

        {renderServiceStatus()}

        <View style={styles.stepsContainer}>
          <Text style={styles.sectionTitle}>诊断流程</Text>
          {diagnosisSteps.map((step, index) => renderStepCard(step, index))}
        </View>

        <View style={styles.actionContainer}>
          <TouchableOpacity
            style={[styles.actionButton, !isInitialized && styles.disabledButton]}
            onPress={performCompleteDiagnosis}
            disabled={!isInitialized || isLoading}
          >
            {isLoading ? (
              <ActivityIndicator size="small" color="#FFFFFF" />
            ) : (
              <Text style={styles.actionButtonText}>开始完整诊断</Text>
            )}
          </TouchableOpacity>
        </View>

        {renderDiagnosisResult()}
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F5F5F5',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#666',
  },
  scrollView: {
    flex: 1,
  },
  header: {
    padding: 20,
    backgroundColor: '#FFFFFF',
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#2196F3',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
  },
  statusContainer: {
    margin: 16,
    padding: 16,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  statusTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 12,
  },
  statusRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  statusLabel: {
    fontSize: 14,
    color: '#666',
  },
  statusValue: {
    fontSize: 14,
    fontWeight: '500',
    color: '#333',
  },
  stepsContainer: {
    margin: 16,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 16,
  },
  stepCard: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    marginBottom: 12,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  activeStepCard: {
    borderColor: '#2196F3',
    borderWidth: 2,
  },
  completedStepCard: {
    backgroundColor: '#E8F5E8',
  },
  stepIcon: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: '#F0F0F0',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  stepIconText: {
    fontSize: 24,
  },
  stepContent: {
    flex: 1,
  },
  stepTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  stepDescription: {
    fontSize: 14,
    color: '#666',
  },
  stepStatus: {
    width: 30,
    alignItems: 'center',
  },
  completedText: {
    fontSize: 20,
    color: '#4CAF50',
    fontWeight: 'bold',
  },
  pendingText: {
    fontSize: 20,
    color: '#CCC',
  },
  actionContainer: {
    margin: 16,
  },
  actionButton: {
    backgroundColor: '#2196F3',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
  },
  disabledButton: {
    backgroundColor: '#CCC',
  },
  actionButtonText: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: 'bold',
  },
  resultContainer: {
    margin: 16,
  },
  resultTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 16,
  },
  resultCard: {
    padding: 16,
    marginBottom: 12,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  resultLabel: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  resultValue: {
    fontSize: 18,
    color: '#2196F3',
    fontWeight: '500',
    marginBottom: 4,
  },
  resultDescription: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
  characteristicsList: {
    marginTop: 8,
  },
  characteristicItem: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
  },
  recommendationsList: {
    marginTop: 8,
  },
  recommendationItem: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
  },
});

export default FiveDiagnosisScreen; 