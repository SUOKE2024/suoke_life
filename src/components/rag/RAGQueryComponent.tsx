import React, { useState, useCallback, useEffect, useMemo } from "react";";
import {import { ragService } from "../../services/ragService";""/;,"/g"/;
const import = type {View;,}Text,;
TextInput,;
TouchableOpacity,;
ScrollView,;
StyleSheet,;
Alert,;
ActivityIndicator,;
Dimensions,";"";
}
  Platform;'}'';'';
} from "react-native";";
RAGQueryRequest,;
RAGQueryResponse,';,'';
StreamResponse;';'';
} from "../../services/ragService";""/;,"/g"/;
interface RAGQueryComponentProps {const userId = string;,}onResult?: (result: RAGQueryResponse) => void;
}
}
  onError?: (error: Error) => void;}
}
export const RAGQueryComponent: React.FC<RAGQueryComponentProps> = ({)userId,);,}onResult,);
}
  onError;)}';'';
}) => {';,}const [query, setQuery] = useState(');'';
const [isLoading, setIsLoading] = useState(false);';,'';
const [result, setResult] = useState<RAGQueryResponse | null>(null);';,'';
const [streamingText, setStreamingText] = useState(');'';
const [isStreaming, setIsStreaming] = useState(false);';,'';
const [taskType, setTaskType] = useState<'consultation' | 'diagnosis' | 'treatment' | 'prevention'>('consultation');';'';
  // 初始化RAG服务/;,/g/;
useEffect() => {}}
    const initializeService = async () => {try {await ragService.initialize();}
      } catch (error) {}}
}
      }
    };
initializeService();
    // 监听RAG服务事件/;,/g/;
const handleQueryComplete = (data: { request: RAGQueryRequest; result: RAGQueryResponse ;}) => {setResult(data.result);}}
      onResult?.(data.result);}
    };
const handleQueryError = (data: { request: RAGQueryRequest; error: Error ;}) => {onError?.(data.error);}}
}';'';
    };';,'';
ragService.on('queryComplete', handleQueryComplete);';,'';
ragService.on('queryError', handleQueryError);';,'';
return () => {ragService.off('queryComplete', handleQueryComplete);';}}'';
      ragService.off('queryError', handleQueryError);'}'';'';
    };
  }, [onResult, onError]);
  // 执行基础查询/;,/g/;
return;
    }
    setIsLoading(true);
setResult(null);
try {const: request: RAGQueryRequest = {const query = query.trim();
userId,;
taskType,;
context: {,';,}timestamp: Date.now(),';'';
}
          const source = 'mobile_app'}'';'';
        ;}
      };
const response = await ragService.query(request);
setResult(response);
onResult?.(response);
    } catch (error) {onError?.(error as Error);}}
}
    } finally {}}
      setIsLoading(false);}
    }
  }, [query, userId, taskType, onResult, onError]);
  // 执行流式查询/;,/g/;
return;
    }';,'';
setIsStreaming(true);';,'';
setStreamingText(');'';
setResult(null);
try {const: request: RAGQueryRequest = {const query = query.trim();
userId,;
taskType,;
stream: true,;
context: {,';,}timestamp: Date.now(),';'';
}
          const source = 'mobile_app'}'';'';
        ;}
      };
await: ragService.streamQuery(request, (chunk: StreamResponse) => {setStreamingText(prev => prev + chunk.answerFragment);,}if (chunk.isFinal && chunk.sources) {// 构建最终结果/;,}const: finalResult: RAGQueryResponse = {requestId: chunk.requestId,;,/g,/;
  answer: streamingText + chunk.answerFragment,;
sources: chunk.sources.map(source => ({)              ...source,)';,}score: 0.8, // 默认分数)'/;'/g'/;
}
              url: ', // 流式响应中没有URL字段')'}''/;'/g'/;
            ;})),;
confidence: 0.85,;
reasoningChain: [],;
agentInfo: {,';}';,'';
agentType: 'rag';','';'';
}
              const processingTime = 0;}
            }
processingTime: 0,;
followUpQuestions: [],;
const metadata = {;}
          };
setResult(finalResult);
onResult?.(finalResult);
        }
      });
    } catch (error) {onError?.(error as Error);}}
}
    } finally {}}
      setIsStreaming(false);}
    }
  }, [query, userId, taskType, streamingText, onResult, onError]);';'';
  // 清除结果'/;,'/g'/;
const handleClear = useCallback() => {setQuery(');'';,}setResult(null);';'';
}
    setStreamingText(');'}'';'';
  }, []);
  // 批量查询处理/;,/g/;
const handleBatchQuery = useCallback(async (queries: string[]) => {if (queries.length === 0 || isLoading || isStreaming) return;);,}setIsLoading(true);
setResult(null);
try {const: requests: RAGQueryRequest[] = queries.map(q => ({))}const query = q.trim();
userId,;
taskType,;
context: {,';,}timestamp: Date.now(),';,'';
source: 'mobile_app';','';'';
}
          const batch = true;}
        }
      }));
const responses = await ragService.batchQuery(requests);
      // 合并批量查询结果/;,/g/;
if (responses.length > 0) {}}
        const: combinedResult: RAGQueryResponse = {,}';,'';
requestId: `batch_${Date.now();}`,``'`;,```;
answer: responses.map(r, i) => `${i + 1;}. ${r.answer}`).join('\n\n'),'`;,```;
sources: responses.flatMap(r => r.sources),;
confidence: responses.reduce(sum, r) => sum + r.confidence, 0) / responses.length,/;,/g,/;
  reasoningChain: responses.flatMap(r => r.reasoningChain),;
agentInfo: {,';}';,'';
agentType: 'batch_rag';','';'';
}
            processingTime: responses.reduce(sum, r) => sum + r.processingTime, 0)}
          ;}
processingTime: responses.reduce(sum, r) => sum + r.processingTime, 0),;
followUpQuestions: responses.flatMap(r => r.followUpQuestions),;
const metadata = { batchSize: responses.length ;}
        };
setResult(combinedResult);
onResult?.(combinedResult);
      }
    } catch (error) {onError?.(error as Error);}}
}
    } finally {}}
      setIsLoading(false);}
    }
  }, [userId, taskType, isLoading, isStreaming, onResult, onError]);
  // 清除缓存/;,/g/;
const handleClearCache = useCallback() => {ragService.clearCache();}}
}
  }, []);
  // 健康检查/;,/g/;
const handleHealthCheck = useCallback(async () => {try {const health = await ragService.performHealthCheck(););}}
      );}
    } catch (err) {}}
}
    }
  }, []);
  // 获取性能指标/;,/g/;
const handleGetMetrics = useCallback() => {const metrics = ragService.getPerformanceMetrics();,}const cacheStats = ragService.getCacheStats();
}
    const metricsText = Array.from(metrics.entries());}';'';
      .map([key, value]) => `${key}: ${value}ms`);``'`;```;
      .join('\n');';'';

    );
  }, []);
return (<View style={styles.container}>;)      <Text style={styles.title}>RAG智能查询</Text>/;/g/;
      {// 任务类型选择}/;/g/;
      <View style={styles.taskTypeContainer}>);
        <Text style={styles.label}>查询类型:</Text>)'/;'/g'/;
        <View style={styles.taskTypeButtons}>)';'';
          {(["consultation",diagnosis', "treatment",prevention'] as const).map(type) => ()';}}'';
            <TouchableOpacity;}  />/;,/g/;
key={type}
              style={[;,]styles.taskTypeButton,;}}
                taskType === type && styles.taskTypeButtonActive;}
];
              ]}}
              onPress={() => setTaskType(type)}
            >;
              <Text;  />/;,/g/;
style={[;,]styles.taskTypeButtonText,;}}
                  taskType === type && styles.taskTypeButtonTextActive;}
];
                ]}}
              >;

              </Text>/;/g/;
            </TouchableOpacity>/;/g/;
          ))}
        </View>/;/g/;
      </View>/;/g/;
      {// 查询输入}/;/g/;
      <View style={styles.inputContainer}>;
        <Text style={styles.label}>查询内容: </Text>/;/g/;
        <TextInput;  />/;,/g/;
style={styles.textInput}
          value={query}
          onChangeText={setQuery}

          multiline;';,'';
numberOfLines={3}';,'';
textAlignVertical="top"";"";
        />/;/g/;
      </View>/;/g/;
      {// 操作按钮}/;/g/;
      <View style={styles.buttonContainer}>;
        <TouchableOpacity;  />/;,/g/;
style={[styles.button, styles.queryButton]}
          onPress={handleQuery}
          disabled={isLoading || isStreaming}
        >";"";
          {isLoading ? ()";}}"";
            <ActivityIndicator color="#fff"  />"}""/;"/g"/;
          ) : (<Text style={styles.buttonText}>查询</Text>)/;/g/;
          )}
        </TouchableOpacity>/;/g/;
        <TouchableOpacity;  />/;,/g/;
style={[styles.button, styles.streamButton]}
          onPress={handleStreamQuery}
          disabled={isLoading || isStreaming}
        >";"";
          {isStreaming ? ()";}}"";
            <ActivityIndicator color="#fff"  />"}""/;"/g"/;
          ) : (<Text style={styles.buttonText}>流式查询</Text>)/;/g/;
          )}
        </TouchableOpacity>/;/g/;
        <TouchableOpacity;  />/;,/g/;
style={[styles.button, styles.clearButton]}
          onPress={handleClear}
          disabled={isLoading || isStreaming}
        >;
          <Text style={styles.buttonText}>清除</Text>/;/g/;
        </TouchableOpacity>/;/g/;
      </View>/;/g/;
      {// 高级功能按钮}/;/g/;
      <View style={styles.advancedButtonContainer}>;
        <TouchableOpacity;  />/;,/g/;
style={[styles.smallButton, styles.healthButton]}
          onPress={handleHealthCheck}
          disabled={isLoading || isStreaming}
        >;
          <Text style={styles.smallButtonText}>健康检查</Text>/;/g/;
        </TouchableOpacity>/;/g/;
        <TouchableOpacity;  />/;,/g/;
style={[styles.smallButton, styles.metricsButton]}
          onPress={handleGetMetrics}
          disabled={isLoading || isStreaming}
        >;
          <Text style={styles.smallButtonText}>性能指标</Text>/;/g/;
        </TouchableOpacity>/;/g/;
        <TouchableOpacity;  />/;,/g/;
style={[styles.smallButton, styles.cacheButton]}
          onPress={handleClearCache}
          disabled={isLoading || isStreaming}
        >;
          <Text style={styles.smallButtonText}>清除缓存</Text>/;/g/;
        </TouchableOpacity>/;/g/;
      </View>/;/g/;
      {// 结果显示}/;/g/;
      <ScrollView style={styles.resultContainer}>;
        {// 流式结果}/;/g/;
        {isStreaming  && <View style={styles.streamingContainer}>;
            <Text style={styles.resultTitle}>实时回答: </Text>/;/g/;
            <Text style={styles.streamingText}>{streamingText}</Text>/;/g/;
            <ActivityIndicator style={styles.streamingIndicator}>;
          </View>/;/g/;
        )}
        {// 最终结果}/;/g/;
        {result  && <View style={styles.resultContent}>;
            <Text style={styles.resultTitle}>查询结果: </Text>/;/g/;
            {// 回答内容}/;/g/;
            <View style={styles.answerContainer}>;
              <Text style={styles.answerTitle}>回答: </Text>/;/g/;
              <Text style={styles.answerText}>{result.answer}</Text>/;/g/;
            </View>/;/g/;
            {// 置信度}/;/g/;
            <View style={styles.confidenceContainer}>;
              <Text style={styles.confidenceLabel}>;
                置信度: {(result.confidence * 100).toFixed(1)}%;
              </Text>/;/g/;
            </View>/;/g/;
            {// 来源文档}/;/g/;
            {result.sources && result.sources.length > 0  && <View style={styles.sourcesContainer}>;
                <Text style={styles.sourcesTitle}>参考来源: </Text>/;/g/;
                {result.sources.map(source, index) => ())}
                  <View key={source.id || index} style={styles.sourceItem}>;
                    <Text style={styles.sourceTitle}>{source.title}</Text>/;/g/;
                    <Text style={styles.sourceSnippet}>{source.snippet}</Text>/;/g/;
                    <Text style={styles.sourceInfo}>;
                      来源: {source.source} | 相关度: {(source.score * 100).toFixed(1)}%;
                    </Text>/;/g/;
                  </View>/;/g/;
                ))}
              </View>/;/g/;
            )}
            {// 后续问题}/;/g/;
            {result.followUpQuestions && result.followUpQuestions.length > 0  && <View style={styles.followUpContainer}>;
                <Text style={styles.followUpTitle}>相关问题: </Text>;/;/g/;
                {result.followUpQuestions.map(question, index) => (;));}}
                  <TouchableOpacity;}  />/;,/g/;
key={index};
style={styles.followUpItem};
onPress={() => setQuery(question)};
                  >;
                    <Text style={styles.followUpText}>{question}</Text>;/;/g/;
                  </TouchableOpacity>;/;/g/;
                ))};
              </View>;/;/g/;
            )};
          </View>;/;/g/;
        )};
      </ScrollView>;/;/g/;
    </View>;/;/g/;
  );
};
const  styles = StyleSheet.create({)container: {flex: 1,";,"";
padding: 16,";"";
}
    const backgroundColor = '#f5f5f5'}'';'';
  ;}
title: {,';,}fontSize: 24,';,'';
fontWeight: 'bold';','';
textAlign: 'center';','';
marginBottom: 20,';'';
}
    const color = '#333'}'';'';
  ;}
taskTypeContainer: {,;}}
  const marginBottom = 16;}
  }
label: {,';,}fontSize: 16,';,'';
fontWeight: '600';','';
marginBottom: 8,';'';
}
    const color = '#333'}'';'';
  ;},';,'';
taskTypeButtons: {,';,}flexDirection: 'row';','';
flexWrap: 'wrap';','';'';
}
    const gap = 8;}
  }
taskTypeButton: {paddingHorizontal: 12,;
paddingVertical: 6,';,'';
borderRadius: 16,';,'';
backgroundColor: '#e0e0e0';','';
borderWidth: 1,';'';
}
    const borderColor = '#ccc'}'';'';
  ;},';,'';
taskTypeButtonActive: {,';,}backgroundColor: '#007AFF';','';'';
}
    const borderColor = '#007AFF'}'';'';
  ;}
taskTypeButtonText: {,';,}fontSize: 14,';'';
}
    const color = '#666'}'';'';
  ;},';,'';
taskTypeButtonTextActive: {,';,}color: '#fff';','';'';
}
    const fontWeight = '600'}'';'';
  ;}
inputContainer: {,;}}
  const marginBottom = 16;}
  }
textInput: {,';,}borderWidth: 1,';,'';
borderColor: '#ddd';','';
borderRadius: 8,';,'';
padding: 12,';,'';
backgroundColor: '#fff';','';
fontSize: 16,;
}
    const minHeight = 80;}
  },';,'';
buttonContainer: {,';,}flexDirection: 'row';','';
gap: 12,;
}
    const marginBottom = 16;}
  }
button: {flex: 1,;
paddingVertical: 12,';,'';
borderRadius: 8,';,'';
alignItems: 'center';','';'';
}
    const justifyContent = 'center'}'';'';
  ;},';,'';
queryButton: {,';}}'';
  const backgroundColor = '#007AFF'}'';'';
  ;},';,'';
streamButton: {,';}}'';
  const backgroundColor = '#34C759'}'';'';
  ;},';,'';
clearButton: {,';}}'';
  const backgroundColor = '#FF3B30'}'';'';
  ;},';,'';
buttonText: {,';,}color: '#fff';','';
fontSize: 16,';'';
}
    const fontWeight = '600'}'';'';
  ;}
resultContainer: {,;}}
  const flex = 1;}
  },';,'';
streamingContainer: {,';,}backgroundColor: '#fff';','';
borderRadius: 8,;
padding: 16,;
marginBottom: 16,';,'';
borderLeftWidth: 4,';'';
}
    const borderLeftColor = '#34C759'}'';'';
  ;}
streamingText: {fontSize: 16,';,'';
lineHeight: 24,';,'';
color: '#333';','';'';
}
    const marginBottom = 8;}
  },';,'';
streamingIndicator: {,';}}'';
  const alignSelf = 'flex-start'}'';'';
  ;},';,'';
resultContent: {,';,}backgroundColor: '#fff';','';
borderRadius: 8,;
}
    const padding = 16;}
  }
resultTitle: {,';,}fontSize: 18,';,'';
fontWeight: 'bold';','';
marginBottom: 12,';'';
}
    const color = '#333'}'';'';
  ;}
answerContainer: {,;}}
  const marginBottom = 16;}
  }
answerTitle: {,';,}fontSize: 16,';,'';
fontWeight: '600';','';
marginBottom: 8,';'';
}
    const color = '#007AFF'}'';'';
  ;}
answerText: {fontSize: 16,';,'';
lineHeight: 24,';'';
}
    const color = '#333'}'';'';
  ;}
confidenceContainer: {,;}}
  const marginBottom = 16;}
  }
confidenceLabel: {,';,}fontSize: 14,';,'';
color: '#666';','';'';
}
    const fontWeight = '500'}'';'';
  ;}
sourcesContainer: {,;}}
  const marginBottom = 16;}
  }
sourcesTitle: {,';,}fontSize: 16,';,'';
fontWeight: '600';','';
marginBottom: 8,';'';
}
    const color = '#333'}'';'';
  ;},';,'';
sourceItem: {,';,}backgroundColor: '#f8f9fa';','';
borderRadius: 6,;
padding: 12,;
marginBottom: 8,';,'';
borderLeftWidth: 3,';'';
}
    const borderLeftColor = '#007AFF'}'';'';
  ;}
sourceTitle: {,';,}fontSize: 14,';,'';
fontWeight: '600';','';
marginBottom: 4,';'';
}
    const color = '#333'}'';'';
  ;}
sourceSnippet: {fontSize: 13,';,'';
lineHeight: 18,';,'';
color: '#666';','';'';
}
    const marginBottom = 4;}
  }
sourceInfo: {,';,}fontSize: 12,';'';
}
    const color = '#999'}'';'';
  ;}
followUpContainer: {,;}}
  const marginTop = 8;}
  }
followUpTitle: {,';,}fontSize: 16,';,'';
fontWeight: '600';','';
marginBottom: 8,';'';
}
    const color = '#333'}'';'';
  ;},';,'';
followUpItem: {,';,}backgroundColor: '#f0f8ff';','';
borderRadius: 6,;
padding: 10,;
marginBottom: 6,';,'';
borderWidth: 1,';'';
}
    const borderColor = '#e0e8f0'}'';'';
  ;}
followUpText: {,';,}fontSize: 14,';'';
}
    const color = '#007AFF'}'';'';
  ;},';,'';
advancedButtonContainer: {,';,}flexDirection: 'row';','';
gap: 8,';,'';
marginBottom: 16,';'';
}
    const justifyContent = 'space-around'}'';'';
  ;}
smallButton: {paddingHorizontal: 12,;
paddingVertical: 8,';,'';
borderRadius: 6,';,'';
alignItems: 'center';','';
justifyContent: 'center';','';'';
}
    const flex = 1;}';'';
  },smallButtonText: {,';,}color: "#fff";","";"";
}
      fontSize: 12,fontWeight: '500';'}'';'';
  },healthButton: {backgroundColor: '#FF9500';'}'';'';
  },metricsButton: {backgroundColor: '#5856D6';')}'';'';
  },cacheButton: {backgroundColor: '#FF2D92';')}'';'';
  };);
});';,'';
export default RAGQueryComponent;