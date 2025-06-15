/**
 * AI 使用示例组件
 * 展示如何使用升级后的AI功能
 */

import { AICoordinator, LLMService } from '@/ai';
import type { HealthAnalysisRequest } from '@/ai/types/AITypes';
import { AITaskType, LLMModelType } from '@/ai/types/AITypes';
import React, { useState } from 'react';
import { ScrollView, StyleSheet, Text, TextInput, TouchableOpacity, View } from 'react-native';

const AIUsageExample: React.FC = () => {
  const [input, setInput] = useState('');
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedModel, setSelectedModel] = useState(LLMModelType.GPT4O);

  // 初始化AI服务
  const aiCoordinator = new AICoordinator();
  const llmService = new LLMService();

  // 基础文本生成示例
  const handleTextGeneration = async () => {
    if (!input.trim()) return;

    setLoading(true);
    try {
      const response = await aiCoordinator.process({
        taskType: AITaskType.TEXT_GENERATION,
        input: input,
        modelConfig: {
          modelType: selectedModel,
          temperature: 0.7,
          maxTokens: 500
        }
      });

      if (response.success) {
        setResult(response.data);
      } else {
        setResult(`错误: ${response.error}`);
      }
    } catch (error) {
      setResult(`处理失败: ${(error as Error).message}`);
    } finally {
      setLoading(false);
    }
  };

  // 健康分析示例
  const handleHealthAnalysis = async () => {
    setLoading(true);
    try {
      const healthRequest: HealthAnalysisRequest = {
        taskType: AITaskType.HEALTH_ANALYSIS,
        input: '健康分析请求',
        patientData: {
          age: 35,
          gender: 'female',
          symptoms: ['头痛', '失眠', '疲劳'],
          vitalSigns: {
            bloodPressure: 120,
            heartRate: 75,
            temperature: 36.5
          }
        },
        analysisType: 'integrated'
      };

      const response = await aiCoordinator.analyzeHealthIntelligently(healthRequest);

      if (response.success) {
        const analysis = response.data;
        const formattedResult = `
诊断建议: ${analysis.diagnosis}
置信度: ${(analysis.confidence * 100).toFixed(1)}%

治疗建议:
${analysis.recommendations.map(r => `• ${r}`).join('\n')}

风险因素:
${analysis.riskFactors.map(r => `• ${r}`).join('\n')}

后续行动:
${analysis.followUpActions.map(a => `• ${a}`).join('\n')}

${analysis.tcmAnalysis ? `
中医分析:
• 证候: ${analysis.tcmAnalysis.syndrome}
• 体质: ${analysis.tcmAnalysis.constitution}
• 治法: ${analysis.tcmAnalysis.treatment}
` : ''}
        `;
        setResult(formattedResult);
      } else {
        setResult(`分析失败: ${response.error}`);
      }
    } catch (error) {
      setResult(`健康分析失败: ${(error as Error).message}`);
    } finally {
      setLoading(false);
    }
  };

  // 中医诊断示例
  const handleTCMDiagnosis = async () => {
    setLoading(true);
    try {
      const tcmRequest: HealthAnalysisRequest = {
        taskType: AITaskType.TCM_DIAGNOSIS,
        input: '中医诊断请求',
        patientData: {
          age: 40,
          gender: 'male',
          symptoms: ['舌苔厚腻', '脉滑数', '口苦', '胸闷'],
          medicalHistory: ['高血压', '糖尿病']
        },
        analysisType: 'tcm'
      };

      const response = await llmService.analyzeHealth(tcmRequest);

      if (response.success) {
        setResult(JSON.stringify(response.data, null, 2));
      } else {
        setResult(`中医诊断失败: ${response.error}`);
      }
    } catch (error) {
      setResult(`中医诊断失败: ${(error as Error).message}`);
    } finally {
      setLoading(false);
    }
  };

  // 批量处理示例
  const handleBatchProcessing = async () => {
    setLoading(true);
    try {
      const requests = [
        {
          taskType: AITaskType.SUMMARIZATION,
          input: '这是一段很长的医疗报告文本，需要进行总结...'
        },
        {
          taskType: AITaskType.TRANSLATION,
          input: 'This is a medical report that needs to be translated to Chinese.'
        },
        {
          taskType: AITaskType.SENTIMENT_ANALYSIS,
          input: '患者对治疗效果很满意，症状明显改善。'
        }
      ];

      const results = await aiCoordinator.processBatch(requests);
      
      const formattedResults = results.map((result, index) => 
        `请求 ${index + 1}: ${result.success ? result.data : result.error}`
      ).join('\n\n');

      setResult(formattedResults);
    } catch (error) {
      setResult(`批量处理失败: ${(error as Error).message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>AI 功能演示</Text>
      
      {/* 模型选择 */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>选择AI模型:</Text>
        <View style={styles.modelSelector}>
          {[
            LLMModelType.GPT4O,
            LLMModelType.CLAUDE_3_SONNET,
            LLMModelType.GEMINI_PRO
          ].map((model) => (
            <TouchableOpacity
              key={model}
              style={[
                styles.modelButton,
                selectedModel === model && styles.selectedModel
              ]}
              onPress={() => setSelectedModel(model)}
            >
              <Text style={styles.modelButtonText}>{model}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* 输入区域 */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>输入文本:</Text>
        <TextInput
          style={styles.textInput}
          value={input}
          onChangeText={setInput}
          placeholder="请输入要处理的文本..."
          multiline
          numberOfLines={4}
        />
      </View>

      {/* 功能按钮 */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>AI 功能:</Text>
        
        <TouchableOpacity
          style={[styles.button, loading && styles.buttonDisabled]}
          onPress={handleTextGeneration}
          disabled={loading}
        >
          <Text style={styles.buttonText}>文本生成</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.button, loading && styles.buttonDisabled]}
          onPress={handleHealthAnalysis}
          disabled={loading}
        >
          <Text style={styles.buttonText}>智能健康分析</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.button, loading && styles.buttonDisabled]}
          onPress={handleTCMDiagnosis}
          disabled={loading}
        >
          <Text style={styles.buttonText}>中医诊断</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.button, loading && styles.buttonDisabled]}
          onPress={handleBatchProcessing}
          disabled={loading}
        >
          <Text style={styles.buttonText}>批量处理</Text>
        </TouchableOpacity>
      </View>

      {/* 结果显示 */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>处理结果:</Text>
        <View style={styles.resultContainer}>
          {loading ? (
            <Text style={styles.loadingText}>AI 正在处理中...</Text>
          ) : (
            <Text style={styles.resultText}>{result || '暂无结果'}</Text>
          )}
        </View>
      </View>

      {/* 服务状态 */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>服务状态:</Text>
        <TouchableOpacity
          style={styles.statusButton}
          onPress={async () => {
            try {
              const status = aiCoordinator.getServiceStatus();
              const loadBalancer = aiCoordinator.getLoadBalancerInfo();
              
              setResult(`
服务状态:
${Object.entries(status).map(([name, healthy]) => 
  `• ${name}: ${healthy ? '✅ 正常' : '❌ 异常'}`
).join('\n')}

负载均衡配置:
${Object.entries(loadBalancer).map(([task, models]) => 
  `• ${task}: ${models.join(', ')}`
).join('\n')}
              `);
            } catch (error) {
              setResult(`状态检查失败: ${(error as Error).message}`);
            }
          }}
        >
          <Text style={styles.buttonText}>检查服务状态</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    backgroundColor: '#f5f5f5',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 20,
    color: '#333',
  },
  section: {
    marginBottom: 20,
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 12,
    color: '#333',
  },
  modelSelector: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  modelButton: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    backgroundColor: '#e0e0e0',
    borderRadius: 6,
    marginRight: 8,
    marginBottom: 8,
  },
  selectedModel: {
    backgroundColor: '#007AFF',
  },
  modelButtonText: {
    fontSize: 12,
    color: '#333',
  },
  textInput: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    textAlignVertical: 'top',
    minHeight: 100,
  },
  button: {
    backgroundColor: '#007AFF',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
    alignItems: 'center',
  },
  buttonDisabled: {
    backgroundColor: '#ccc',
  },
  statusButton: {
    backgroundColor: '#34C759',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  resultContainer: {
    backgroundColor: '#f8f8f8',
    padding: 16,
    borderRadius: 8,
    minHeight: 100,
  },
  resultText: {
    fontSize: 14,
    color: '#333',
    lineHeight: 20,
  },
  loadingText: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    fontStyle: 'italic',
  },
});

export default AIUsageExample; 