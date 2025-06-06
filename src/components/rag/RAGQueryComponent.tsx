import React, { useState, useCallback, useEffect, useMemo } from 'react';
import {import { ragService } from '../../services/ragService';
import type {View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  StyleSheet,
  Alert,
  ActivityIndicator,
  Dimensions,
  Platform
} from 'react-native';
  RAGQueryRequest,
  RAGQueryResponse,
  StreamResponse
} from '../../services/ragService';

interface RAGQueryComponentProps {
  userId: string;
  onResult?: (result: RAGQueryResponse) => void;
  onError?: (error: Error) => void;
}

export const RAGQueryComponent: React.FC<RAGQueryComponentProps> = ({
  userId,
  onResult,
  onError
}) => {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<RAGQueryResponse | null>(null);
  const [streamingText, setStreamingText] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [taskType, setTaskType] = useState<'consultation' | 'diagnosis' | 'treatment' | 'prevention'>('consultation');

  // 初始化RAG服务
  useEffect(() => {
    const initializeService = async () => {try {await ragService.initialize();
      } catch (error) {
        console.error('RAG服务初始化失败:', error);
        Alert.alert('错误', 'RAG服务初始化失败');
      }
    };

    initializeService();

    // 监听RAG服务事件
    const handleQueryComplete = (data: { request: RAGQueryRequest; result: RAGQueryResponse }) => {
      setResult(data.result);
      onResult?.(data.result);
    };

    const handleQueryError = (data: { request: RAGQueryRequest; error: Error }) => {
      console.error('RAG查询错误:', data.error);
      onError?.(data.error);
      Alert.alert('查询失败', data.error.message);
    };

    ragService.on('queryComplete', handleQueryComplete);
    ragService.on('queryError', handleQueryError);

    return () => {ragService.off('queryComplete', handleQueryComplete);
      ragService.off('queryError', handleQueryError);
    };
  }, [onResult, onError]);

  // 执行基础查询
  const handleQuery = useCallback(async () => {if (!query.trim()) {Alert.alert('提示', '请输入查询内容');
      return;
    }

    setIsLoading(true);
    setResult(null);

    try {
      const request: RAGQueryRequest = {
        query: query.trim(),
        userId,
        taskType,
        context: {
          timestamp: Date.now(),
          source: 'mobile_app'
        }
      };

      const response = await ragService.query(request);
      setResult(response);
      onResult?.(response);
    } catch (error) {
      console.error('查询失败:', error);
      onError?.(error as Error);
      Alert.alert('查询失败', (error as Error).message);
    } finally {
      setIsLoading(false);
    }
  }, [query, userId, taskType, onResult, onError]);

  // 执行流式查询
  const handleStreamQuery = useCallback(async () => {if (!query.trim()) {Alert.alert('提示', '请输入查询内容');
      return;
    }

    setIsStreaming(true);
    setStreamingText('');
    setResult(null);

    try {
      const request: RAGQueryRequest = {
        query: query.trim(),
        userId,
        taskType,
        stream: true,
        context: {
          timestamp: Date.now(),
          source: 'mobile_app'
        }
      };

      await ragService.streamQuery(request, (chunk: StreamResponse) => {
        setStreamingText(prev => prev + chunk.answerFragment);

        if (chunk.isFinal && chunk.sources) {
          // 构建最终结果
          const finalResult: RAGQueryResponse = {
            requestId: chunk.requestId,
            answer: streamingText + chunk.answerFragment,
            sources: chunk.sources.map(source => ({
              ...source,
              score: 0.8, // 默认分数
              url: '', // 流式响应中没有URL字段
            })),
            confidence: 0.85,
            reasoningChain: [],
            agentInfo: {
              agentName: 'RAG服务',
              agentType: 'rag',
              processingTime: 0
            },
            processingTime: 0,
            followUpQuestions: [],
            metadata: {}
          };

          setResult(finalResult);
          onResult?.(finalResult);
        }
      });
    } catch (error) {
      console.error('流式查询失败:', error);
      onError?.(error as Error);
      Alert.alert('流式查询失败', (error as Error).message);
    } finally {
      setIsStreaming(false);
    }
  }, [query, userId, taskType, streamingText, onResult, onError]);

  // 清除结果
  const handleClear = useCallback(() => {setQuery('');
    setResult(null);
    setStreamingText('');
  }, []);

  // 批量查询处理
  const handleBatchQuery = useCallback(async (queries: string[]) => {if (queries.length === 0 || isLoading || isStreaming) return;

    setIsLoading(true);
    setResult(null);

    try {
      const requests: RAGQueryRequest[] = queries.map(q => ({
        query: q.trim(),
        userId,
        taskType,
        context: {
          timestamp: Date.now(),
          source: 'mobile_app',
          batch: true
        }
      }));

      const responses = await ragService.batchQuery(requests);

      // 合并批量查询结果
      if (responses.length > 0) {
        const combinedResult: RAGQueryResponse = {
          requestId: `batch_${Date.now()}`,
          answer: responses.map((r, i) => `${i + 1}. ${r.answer}`).join('\n\n'),
          sources: responses.flatMap(r => r.sources),
          confidence: responses.reduce((sum, r) => sum + r.confidence, 0) / responses.length,
          reasoningChain: responses.flatMap(r => r.reasoningChain),
          agentInfo: {
            agentName: '批量RAG服务',
            agentType: 'batch_rag',
            processingTime: responses.reduce((sum, r) => sum + r.processingTime, 0)
          },
          processingTime: responses.reduce((sum, r) => sum + r.processingTime, 0),
          followUpQuestions: responses.flatMap(r => r.followUpQuestions),
          metadata: { batchSize: responses.length }
        };

        setResult(combinedResult);
        onResult?.(combinedResult);
      }
    } catch (error) {
      console.error('批量查询失败:', error);
      onError?.(error as Error);
      Alert.alert('批量查询失败', (error as Error).message);
    } finally {
      setIsLoading(false);
    }
  }, [userId, taskType, isLoading, isStreaming, onResult, onError]);

  // 清除缓存
  const handleClearCache = useCallback(() => {ragService.clearCache();
    Alert.alert('成功', '缓存已清除');
  }, []);

  // 健康检查
  const handleHealthCheck = useCallback(async () => {try {const health = await ragService.performHealthCheck();
      Alert.alert(
        '健康检查结果',
        `服务状态: ${health.isHealthy ? '正常' : '异常'}\n` +
        `RAG服务: ${health.services.rag ? '正常' : '异常'}\n` +
        `TCM服务: ${health.services.tcm ? '正常' : '异常'}\n` +
        `延迟: ${health.latency}ms`
      );
    } catch (err) {
      Alert.alert('错误', '健康检查失败');
    }
  }, []);

  // 获取性能指标
  const handleGetMetrics = useCallback(() => {const metrics = ragService.getPerformanceMetrics();
    const cacheStats = ragService.getCacheStats();

    const metricsText = Array.from(metrics.entries());
      .map(([key, value]) => `${key}: ${value}ms`);
      .join('\n');

    Alert.alert(
      '性能指标',
      `${metricsText}\n\n缓存大小: ${cacheStats.size}\n缓存键数: ${cacheStats.keys.length}`
    );
  }, []);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>RAG智能查询</Text>

      {// 任务类型选择}
      <View style={styles.taskTypeContainer}>
        <Text style={styles.label}>查询类型:</Text>
        <View style={styles.taskTypeButtons}>
          {(['consultation', 'diagnosis', 'treatment', 'prevention'] as const).map((type) => (
            <TouchableOpacity
              key={type}
              style={[
                styles.taskTypeButton,
                taskType === type && styles.taskTypeButtonActive
              ]}
              onPress={() => setTaskType(type)}
            >
              <Text
                style={[
                  styles.taskTypeButtonText,
                  taskType === type && styles.taskTypeButtonTextActive
                ]}
              >
                {type === 'consultation' && '咨询'}
                {type === 'diagnosis' && '诊断'}
                {type === 'treatment' && '治疗'}
                {type === 'prevention' && '预防'}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {// 查询输入}
      <View style={styles.inputContainer}>
        <Text style={styles.label}>查询内容:</Text>
        <TextInput
          style={styles.textInput}
          value={query}
          onChangeText={setQuery}
          placeholder="请输入您的健康问题或症状..."
          multiline
          numberOfLines={3}
          textAlignVertical="top"
        />
      </View>

      {// 操作按钮}
      <View style={styles.buttonContainer}>
        <TouchableOpacity
          style={[styles.button, styles.queryButton]}
          onPress={handleQuery}
          disabled={isLoading || isStreaming}
        >
          {isLoading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.buttonText}>查询</Text>
          )}
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.button, styles.streamButton]}
          onPress={handleStreamQuery}
          disabled={isLoading || isStreaming}
        >
          {isStreaming ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.buttonText}>流式查询</Text>
          )}
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.button, styles.clearButton]}
          onPress={handleClear}
          disabled={isLoading || isStreaming}
        >
          <Text style={styles.buttonText}>清除</Text>
        </TouchableOpacity>
      </View>

      {// 高级功能按钮}
      <View style={styles.advancedButtonContainer}>
        <TouchableOpacity
          style={[styles.smallButton, styles.healthButton]}
          onPress={handleHealthCheck}
          disabled={isLoading || isStreaming}
        >
          <Text style={styles.smallButtonText}>健康检查</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.smallButton, styles.metricsButton]}
          onPress={handleGetMetrics}
          disabled={isLoading || isStreaming}
        >
          <Text style={styles.smallButtonText}>性能指标</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.smallButton, styles.cacheButton]}
          onPress={handleClearCache}
          disabled={isLoading || isStreaming}
        >
          <Text style={styles.smallButtonText}>清除缓存</Text>
        </TouchableOpacity>
      </View>

      {// 结果显示}
      <ScrollView style={styles.resultContainer}>
        {// 流式结果}
        {isStreaming && (
          <View style={styles.streamingContainer}>
            <Text style={styles.resultTitle}>实时回答:</Text>
            <Text style={styles.streamingText}>{streamingText}</Text>
            <ActivityIndicator style={styles.streamingIndicator} />
          </View>
        )}

        {// 最终结果}
        {result && (
          <View style={styles.resultContent}>
            <Text style={styles.resultTitle}>查询结果:</Text>

            {// 回答内容}
            <View style={styles.answerContainer}>
              <Text style={styles.answerTitle}>回答:</Text>
              <Text style={styles.answerText}>{result.answer}</Text>
            </View>

            {// 置信度}
            <View style={styles.confidenceContainer}>
              <Text style={styles.confidenceLabel}>
                置信度: {(result.confidence * 100).toFixed(1)}%
              </Text>
            </View>

            {// 来源文档}
            {result.sources && result.sources.length > 0 && (
              <View style={styles.sourcesContainer}>
                <Text style={styles.sourcesTitle}>参考来源:</Text>
                {result.sources.map((source, index) => (
                  <View key={source.id || index} style={styles.sourceItem}>
                    <Text style={styles.sourceTitle}>{source.title}</Text>
                    <Text style={styles.sourceSnippet}>{source.snippet}</Text>
                    <Text style={styles.sourceInfo}>
                      来源: {source.source} | 相关度: {(source.score * 100).toFixed(1)}%
                    </Text>
                  </View>
                ))}
              </View>
            )}

            {// 后续问题}
            {result.followUpQuestions && result.followUpQuestions.length > 0 && (
              <View style={styles.followUpContainer}>
                <Text style={styles.followUpTitle}>相关问题:</Text>;
                {result.followUpQuestions.map((question, index) => (;
                  <TouchableOpacity;
                    key={index};
                    style={styles.followUpItem};
                    onPress={() => setQuery(question)};
                  >;
                    <Text style={styles.followUpText}>{question}</Text>;
                  </TouchableOpacity>;
                ))};
              </View>;
            )};
          </View>;
        )};
      </ScrollView>;
    </View>;
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    backgroundColor: '#f5f5f5'
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 20,
    color: '#333'
  },
  taskTypeContainer: {
    marginBottom: 16
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8,
    color: '#333'
  },
  taskTypeButtons: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8
  },
  taskTypeButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    backgroundColor: '#e0e0e0',
    borderWidth: 1,
    borderColor: '#ccc'
  },
  taskTypeButtonActive: {
    backgroundColor: '#007AFF',
    borderColor: '#007AFF'
  },
  taskTypeButtonText: {
    fontSize: 14,
    color: '#666'
  },
  taskTypeButtonTextActive: {
    color: '#fff',
    fontWeight: '600'
  },
  inputContainer: {
    marginBottom: 16
  },
  textInput: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    backgroundColor: '#fff',
    fontSize: 16,
    minHeight: 80
  },
  buttonContainer: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 16
  },
  button: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center'
  },
  queryButton: {
    backgroundColor: '#007AFF'
  },
  streamButton: {
    backgroundColor: '#34C759'
  },
  clearButton: {
    backgroundColor: '#FF3B30'
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600'
  },
  resultContainer: {
    flex: 1
  },
  streamingContainer: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 16,
    marginBottom: 16,
    borderLeftWidth: 4,
    borderLeftColor: '#34C759'
  },
  streamingText: {
    fontSize: 16,
    lineHeight: 24,
    color: '#333',
    marginBottom: 8
  },
  streamingIndicator: {
    alignSelf: 'flex-start'
  },
  resultContent: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 16
  },
  resultTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 12,
    color: '#333'
  },
  answerContainer: {
    marginBottom: 16
  },
  answerTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8,
    color: '#007AFF'
  },
  answerText: {
    fontSize: 16,
    lineHeight: 24,
    color: '#333'
  },
  confidenceContainer: {
    marginBottom: 16
  },
  confidenceLabel: {
    fontSize: 14,
    color: '#666',
    fontWeight: '500'
  },
  sourcesContainer: {
    marginBottom: 16
  },
  sourcesTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8,
    color: '#333'
  },
  sourceItem: {
    backgroundColor: '#f8f9fa',
    borderRadius: 6,
    padding: 12,
    marginBottom: 8,
    borderLeftWidth: 3,
    borderLeftColor: '#007AFF'
  },
  sourceTitle: {
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 4,
    color: '#333'
  },
  sourceSnippet: {
    fontSize: 13,
    lineHeight: 18,
    color: '#666',
    marginBottom: 4
  },
  sourceInfo: {
    fontSize: 12,
    color: '#999'
  },
  followUpContainer: {
    marginTop: 8
  },
  followUpTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8,
    color: '#333'
  },
  followUpItem: {
    backgroundColor: '#f0f8ff',
    borderRadius: 6,
    padding: 10,
    marginBottom: 6,
    borderWidth: 1,
    borderColor: '#e0e8f0'
  },
  followUpText: {
    fontSize: 14,
    color: '#007AFF'
  },
  advancedButtonContainer: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 16,
    justifyContent: 'space-around'
  },
  smallButton: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 6,
    alignItems: 'center',
    justifyContent: 'center',
    flex: 1;
  },smallButtonText: {color: '#fff',fontSize: 12,fontWeight: '500';
  },healthButton: {backgroundColor: '#FF9500';
  },metricsButton: {backgroundColor: '#5856D6';
  },cacheButton: {backgroundColor: '#FF2D92';
  };
});

export default RAGQueryComponent; 
