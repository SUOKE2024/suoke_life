import React, { useEffect, useState } from 'react';
import { StatusBar, Platform, View, Text, StyleSheet, Alert } from 'react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';

// 导入主导航器
import AppNavigator from './src/navigation/AppNavigator';

// 导入AI模块
import { AICoordinator, LLMService } from './src/ai';
import type { HealthAnalysisRequest, HealthAnalysisResult } from './src/ai/types/AITypes';

const App: React.FC = () => {
  const [aiInitialized, setAiInitialized] = useState(false);
  const [healthStatus, setHealthStatus] = useState<string>('正在初始化AI系统...');

  useEffect(() => {
    initializeAI();
  }, []);

  const initializeAI = async () => {
    try {
      // 初始化AI协调器
      const coordinator = AICoordinator.getInstance();
      await coordinator.initialize();

      // 测试健康分析功能
      const healthRequest: HealthAnalysisRequest = {
        symptoms: ['轻微头痛', '疲劳'],
        vitalSigns: {
          heartRate: 72,
          bloodPressure: { systolic: 120, diastolic: 80 },
          temperature: 36.5,
          respiratoryRate: 16
        },
        lifestyle: {
          sleepHours: 7,
          exerciseMinutes: 30,
          stressLevel: 3
        },
        preferences: {
          preferredLanguage: 'zh-CN',
          treatmentPreference: 'integrated' // 中西医结合
        }
      };

      // 执行健康分析
      const result = await coordinator.analyzeHealth(healthRequest);
      
      if (result.success && result.data) {
        setHealthStatus(`AI健康分析完成 - 建议: ${result.data.recommendations[0]?.description || '保持健康生活方式'}`);
      } else {
        setHealthStatus('AI系统已就绪，等待健康数据输入');
      }

      setAiInitialized(true);
    } catch (error) {
      console.error('AI初始化失败:', error);
      setHealthStatus('AI系统初始化失败，使用基础功能');
      setAiInitialized(false);
    }
  };

  return (
    <SafeAreaProvider>
      <StatusBar
        barStyle={Platform.OS === 'ios' ? 'dark-content' : 'light-content'}
        backgroundColor="#2196F3"
        translucent={false}
      />
      
      {/* AI状态指示器 */}
      <View style={styles.aiStatusBar}>
        <View style={[styles.aiIndicator, { backgroundColor: aiInitialized ? '#4CAF50' : '#FF9800' }]} />
        <Text style={styles.aiStatusText}>{healthStatus}</Text>
      </View>

      <AppNavigator />
    </SafeAreaProvider>
  );
};

const styles = StyleSheet.create({
  aiStatusBar: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  aiIndicator: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 8,
  },
  aiStatusText: {
    fontSize: 12,
    color: '#666',
    flex: 1,
  },
});

export default App;