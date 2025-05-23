/**
 * 智能体服务集成使用示例
 * 展示如何在React Native组件中使用四个智能体服务
 */
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  ScrollView,
  Alert,
  ActivityIndicator,
  StyleSheet,
} from 'react-native';
import xiaoaiApi from '../api/agents/xiaoaiApi';
import xiaokeApi from '../api/agents/xiaokeApi';
import laokeApi from '../api/agents/laokeApi';
import soerApi from '../api/agents/soerApi';
import { runAgentIntegrationTest, quickHealthCheck } from '../utils/agentIntegrationTest';

interface ComponentState {
  loading: boolean;
  healthStatus: Record<string, boolean>;
  testResults: any;
}

export default function AgentIntegrationExample() {
  const [state, setState] = useState<ComponentState>({
    loading: false,
    healthStatus: {},
    testResults: null,
  });

  // 检查所有智能体服务健康状态
  const checkAllServicesHealth = async () => {
    setState(prev => ({ ...prev, loading: true }));
    try {
      const isHealthy = await quickHealthCheck();
      Alert.alert(
        '服务健康检查',
        isHealthy ? '所有智能体服务运行正常 ✅' : '部分服务异常 ⚠️',
        [{ text: '确定' }]
      );
    } catch (error) {
      Alert.alert('错误', '健康检查失败: ' + (error instanceof Error ? error.message : '未知错误'));
    } finally {
      setState(prev => ({ ...prev, loading: false }));
    }
  };

  // 运行完整集成测试
  const runFullIntegrationTest = async () => {
    setState(prev => ({ ...prev, loading: true }));
    try {
      const results = await runAgentIntegrationTest();
      setState(prev => ({ ...prev, testResults: results }));
      
      Alert.alert(
        '集成测试完成',
        `测试结果: ${results.summary.passed}/${results.summary.total} 个服务通过测试`,
        [{ text: '查看详情', onPress: () => console.log('详细结果:', results) }, { text: '确定' }]
      );
    } catch (error) {
      Alert.alert('错误', '集成测试失败: ' + (error instanceof Error ? error.message : '未知错误'));
    } finally {
      setState(prev => ({ ...prev, loading: false }));
    }
  };

  // 测试小艾服务
  const testXiaoaiService = async () => {
    setState(prev => ({ ...prev, loading: true }));
    try {
      // 创建诊断会话
      const session = await xiaoaiApi.createDiagnosisSession({
        user_id: 'demo-user-001',
        session_type: 'comprehensive',
        initial_symptoms: ['头痛', '失眠']
      });
      
      Alert.alert(
        '小艾服务测试成功',
        `诊断会话已创建\n会话ID: ${session.session_id}\n会话类型: ${session.session_type}`,
        [{ text: '确定' }]
      );
    } catch (error) {
      Alert.alert('小艾服务测试失败', error instanceof Error ? error.message : '未知错误');
    } finally {
      setState(prev => ({ ...prev, loading: false }));
    }
  };

  // 测试小克服务
  const testXiaokeService = async () => {
    setState(prev => ({ ...prev, loading: true }));
    try {
      // 获取产品推荐
      const recommendations = await xiaokeApi.recommendProducts({
        user_id: 'demo-user-001',
        category: 'health_supplements',
        constitution_type: '阳虚质',
        budget_range: { min: 100, max: 500 }
      });
      
      Alert.alert(
        '小克服务测试成功',
        `获得 ${recommendations.products.length} 个产品推荐`,
        [{ text: '确定' }]
      );
    } catch (error) {
      Alert.alert('小克服务测试失败', error instanceof Error ? error.message : '未知错误');
    } finally {
      setState(prev => ({ ...prev, loading: false }));
    }
  };

  // 测试老克服务
  const testLaokeService = async () => {
    setState(prev => ({ ...prev, loading: true }));
    try {
      // 获取知识文章
      const articles = await laokeApi.getKnowledgeArticles({
        category: '中医基础',
        limit: 10
      });
      
      Alert.alert(
        '老克服务测试成功',
        `获得 ${articles.length} 篇知识文章`,
        [{ text: '确定' }]
      );
    } catch (error) {
      Alert.alert('老克服务测试失败', error instanceof Error ? error.message : '未知错误');
    } finally {
      setState(prev => ({ ...prev, loading: false }));
    }
  };

  // 测试索儿服务
  const testSoerService = async () => {
    setState(prev => ({ ...prev, loading: true }));
    try {
      // 生成健康计划
      const healthPlan = await soerApi.generateHealthPlan({
        user_id: 'demo-user-001',
        constitution_type: '平和质',
        health_goals: ['改善睡眠', '增强体质', '缓解疲劳'],
        preferences: {
          exercise: ['瑜伽', '太极'],
          diet: ['清淡', '温补']
        },
        current_season: '春季'
      });
      
      Alert.alert(
        '索儿服务测试成功',
        `健康计划已生成\n计划ID: ${healthPlan.plan_id}\n信心分数: ${healthPlan.confidence_score}`,
        [{ text: '确定' }]
      );
    } catch (error) {
      Alert.alert('索儿服务测试失败', error instanceof Error ? error.message : '未知错误');
    } finally {
      setState(prev => ({ ...prev, loading: false }));
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>智能体服务集成测试</Text>
      <Text style={styles.subtitle}>测试所有四个智能体服务的连接和基本功能</Text>
      
      {state.loading && (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#4CAF50" />
          <Text style={styles.loadingText}>正在执行测试...</Text>
        </View>
      )}
      
      {/* 整体测试按钮 */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>整体测试</Text>
        
        <TouchableOpacity 
          style={styles.button} 
          onPress={checkAllServicesHealth}
          disabled={state.loading}
        >
          <Text style={styles.buttonText}>快速健康检查</Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={styles.button} 
          onPress={runFullIntegrationTest}
          disabled={state.loading}
        >
          <Text style={styles.buttonText}>完整集成测试</Text>
        </TouchableOpacity>
      </View>
      
      {/* 个别服务测试 */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>单独测试各智能体</Text>
        
        <TouchableOpacity 
          style={[styles.button, styles.xiaoaiButton]} 
          onPress={testXiaoaiService}
          disabled={state.loading}
        >
          <Text style={styles.buttonText}>测试小艾服务 (四诊协调)</Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={[styles.button, styles.xiaokeButton]} 
          onPress={testXiaokeService}
          disabled={state.loading}
        >
          <Text style={styles.buttonText}>测试小克服务 (资源调度)</Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={[styles.button, styles.laokeButton]} 
          onPress={testLaokeService}
          disabled={state.loading}
        >
          <Text style={styles.buttonText}>测试老克服务 (知识传播)</Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={[styles.button, styles.soerButton]} 
          onPress={testSoerService}
          disabled={state.loading}
        >
          <Text style={styles.buttonText}>测试索儿服务 (生活管理)</Text>
        </TouchableOpacity>
      </View>
      
      {/* 测试结果显示 */}
      {state.testResults && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>最近测试结果</Text>
          <View style={styles.resultContainer}>
            <Text style={styles.resultText}>
              测试时间: {new Date(state.testResults.timestamp).toLocaleString()}
            </Text>
            <Text style={[
              styles.resultText, 
              state.testResults.overallSuccess ? styles.successText : styles.errorText
            ]}>
              总体状态: {state.testResults.overallSuccess ? '通过 ✅' : '失败 ❌'}
            </Text>
            <Text style={styles.resultText}>
              通过率: {state.testResults.summary.passed}/{state.testResults.summary.total}
            </Text>
            
            {state.testResults.services.map((service: any, index: number) => (
              <View key={index} style={styles.serviceResult}>
                <Text style={[
                  styles.serviceText,
                  service.success ? styles.successText : styles.errorText
                ]}>
                  {service.success ? '✅' : '❌'} {service.service}
                </Text>
                {service.responseTime && (
                  <Text style={styles.responseTime}>响应时间: {service.responseTime}ms</Text>
                )}
                {service.error && (
                  <Text style={styles.errorText}>错误: {service.error}</Text>
                )}
              </View>
            ))}
          </View>
        </View>
      )}
      
      {/* 使用说明 */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>使用说明</Text>
        <Text style={styles.instructionText}>
          1. 首先运行"快速健康检查"确认服务状态{'\n'}
          2. 运行"完整集成测试"获得详细报告{'\n'}
          3. 单独测试各智能体服务的具体功能{'\n'}
          4. 查看控制台获得详细日志信息
        </Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    textAlign: 'center',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginBottom: 24,
  },
  section: {
    backgroundColor: 'white',
    borderRadius: 8,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 12,
  },
  button: {
    backgroundColor: '#4CAF50',
    padding: 12,
    borderRadius: 6,
    marginBottom: 8,
  },
  xiaoaiButton: {
    backgroundColor: '#2196F3', // 蓝色 - 小艾
  },
  xiaokeButton: {
    backgroundColor: '#FF9800', // 橙色 - 小克
  },
  laokeButton: {
    backgroundColor: '#9C27B0', // 紫色 - 老克
  },
  soerButton: {
    backgroundColor: '#4CAF50', // 绿色 - 索儿
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  loadingContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  loadingText: {
    marginTop: 8,
    fontSize: 16,
    color: '#666',
  },
  resultContainer: {
    backgroundColor: '#f9f9f9',
    padding: 12,
    borderRadius: 6,
  },
  resultText: {
    fontSize: 14,
    color: '#333',
    marginBottom: 4,
  },
  serviceResult: {
    borderLeftWidth: 3,
    borderLeftColor: '#4CAF50',
    paddingLeft: 8,
    marginTop: 8,
  },
  serviceText: {
    fontSize: 14,
    fontWeight: 'bold',
  },
  responseTime: {
    fontSize: 12,
    color: '#666',
    marginTop: 2,
  },
  successText: {
    color: '#4CAF50',
  },
  errorText: {
    color: '#F44336',
  },
  instructionText: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
});