import { Ionicons } from "@expo/vector-icons";""/;,"/g"/;
import { LinearGradient } from "expo-linear-gradient";";
import React, { useCallback, useEffect, useState } from "react";";
import {Alert}Dimensions,;
Modal,;
RefreshControl,;
SafeAreaView,;
ScrollView,;
StyleSheet,;
Text,;
TouchableOpacity,";"";
}
    View,'}'';'';
} from "react-native";";
import PerformanceMonitor from "../../components/ui/PerformanceMonitor";""/;,"/g"/;
import { usePerformanceMonitor } from "../../hooks/usePerformanceMonitor";""/;,"/g"/;
import {ModelPerformance}modelTrainingService,;
TrainingData,";"";
}
    TrainingStatus,'}'';'';
} from "../../services/ai/modelTrainingService";""/;"/g"/;
';,'';
const { width: screenWidth ;} = Dimensions.get('window');';,'';
interface TrainingCardProps {const status = TrainingStatus;,}performance?: ModelPerformance;
onStartTraining: (modelId: string) => void,;
onStopTraining: (modelId: string) => void,;
}
}
  onViewDetails: (modelId: string) => void;}
}

const  TrainingCard: React.FC<TrainingCardProps> = ({)status}performance,;
onStartTraining,);
onStopTraining,);
}
  onViewDetails,)}
;}) => {const  getStatusColor = (status: string) => {';,}switch (status) {';,}case 'training': return '#3742fa';';,'';
case 'completed': return '#2ed573';';,'';
case 'failed': return '#ff4757';';,'';
case 'preparing': return '#ffa502';';,'';
case 'validating': return '#5352ed';';'';
}
      const default = return '#747d8c';'}'';'';
    }
  };
const  getStatusText = (status: string) => {switch (status) {}}
}
    ;}
  };
const  formatTime = (seconds: number) => {}}
}
    if (seconds < 3600) return `${Math.floor(seconds / 60);}分${seconds % 60}秒`;```/`;,`/g`/`;
return `${Math.floor(seconds / 3600)}时${Math.floor((seconds % 3600) / 60)}分`;```/`;`/g`/`;
  };
return (<View style={styles.trainingCard}>)';'';
      <LinearGradient,)'  />/;,'/g'/;
colors={['rgba(255, 255, 255, 0.1)', 'rgba(255, 255, 255, 0.05)']}';,'';
style={styles.cardGradient}
      >;
        {/* Header */}/;/g/;
        <View style={styles.cardHeader}>;
          <View style={styles.cardTitleContainer}>';'';
            <View style={[styles.statusIndicator, { backgroundColor: getStatusColor(status.status) ;}]}  />'/;'/g'/;
            <Text style={styles.cardTitle}>{status.modelId.replace('_', ' ').toUpperCase()}</Text>'/;'/g'/;
          </View>/;/g/;
          <Text style={[styles.statusText, { color: getStatusColor(status.status) ;}]}>;
            {getStatusText(status.status)}
          </Text>/;/g/;
        </View>/;/g/;
';'';
        {/* Progress Bar */}'/;'/g'/;
        {status.status === 'training' && ('}'';)          <View style={styles.progressSection}>;'';
            <View style={styles.progressInfo}>;
              <Text style={styles.progressText}>;
                第 {status.currentEpoch} / {status.totalEpochs} 轮)/;/g/;
              </Text>)/;/g/;
              <Text style={styles.progressPercentage}>);
                {status.progress.toFixed(1)}%;
              </Text>/;/g/;
            </View>/;/g/;
            <View style={styles.progressBar}>;
              <View  />/;,/g/;
style={[;,]styles.progressFill,;}}
                  { }
                    width: `${status.progress;}%`,````;,```;
const backgroundColor = getStatusColor(status.status);
                  ;}
];
                ]}
              />/;/g/;
            </View>/;/g/;
            {status.estimatedTimeRemaining > 0 && (<Text style={styles.timeRemaining}>);
);
              </Text>)/;/g/;
            )}
          </View>/;/g/;
        )}

        {/* Metrics */}/;/g/;
        <View style={styles.metricsSection}>;
          <View style={styles.metricRow}>;
            <View style={styles.metricItem}>;
              <Text style={styles.metricLabel}>准确率</Text>/;/g/;
              <Text style={styles.metricValue}>;
                {(status.metrics.accuracy * 100).toFixed(1)}%;
              </Text>/;/g/;
            </View>/;/g/;
            <View style={styles.metricItem}>;
              <Text style={styles.metricLabel}>损失</Text>/;/g/;
              <Text style={styles.metricValue}>;
                {status.metrics.loss.toFixed(3)}
              </Text>/;/g/;
            </View>/;/g/;
          </View>/;/g/;

          {performance && (<View style={styles.metricRow}>;)              <View style={styles.metricItem}>);
                <Text style={styles.metricLabel}>推理时间</Text>)/;/g/;
                <Text style={styles.metricValue}>);
                  {performance.inferenceTime.toFixed(1)}ms;
                </Text>/;/g/;
              </View>/;/g/;
              <View style={styles.metricItem}>;
                <Text style={styles.metricLabel}>内存使用</Text>/;/g/;
                <Text style={styles.metricValue}>;
                  {performance.memoryUsage.toFixed(0)}MB;
                </Text>/;/g/;
              </View>/;/g/;
            </View>/;/g/;
          )}
        </View>/;/g/;

        {/* Actions */}'/;'/g'/;
        <View style={styles.cardActions}>';'';
          {status.status === 'idle' || status.status === 'failed' ? (')'';}}'';
            <TouchableOpacity,)}  />/;,/g/;
style={[styles.actionButton, styles.startButton]});
onPress={() => onStartTraining(status.modelId)}';'';
            >';'';
              <Ionicons name="play" size={16} color="#fff"  />"/;"/g"/;
              <Text style={styles.actionButtonText}>开始训练</Text>"/;"/g"/;
            </TouchableOpacity>"/;"/g"/;
          ) : status.status === 'training' ? (')'';'';
            <TouchableOpacity,)  />/;,/g/;
style={[styles.actionButton, styles.stopButton]});
onPress={() => onStopTraining(status.modelId)}';'';
            >';'';
              <Ionicons name="stop" size={16} color="#fff"  />"/;"/g"/;
              <Text style={styles.actionButtonText}>停止训练</Text>/;/g/;
            </TouchableOpacity>/;/g/;
          ) : null}

          <TouchableOpacity,  />/;,/g/;
style={[styles.actionButton, styles.detailsButton]}
            onPress={() => onViewDetails(status.modelId)}";"";
          >";"";
            <Ionicons name="analytics" size={16} color="#fff"  />"/;"/g"/;
            <Text style={styles.actionButtonText}>查看详情</Text>/;/g/;
          </TouchableOpacity>/;/g/;
        </View>/;/g/;
      </LinearGradient>/;/g/;
    </View>/;/g/;
  );
};
";,"";
const  AIModelTrainingScreen: React.FC = () => {";,}const: performanceMonitor = usePerformanceMonitor('AIModelTrainingScreen', {';,)trackRender: true,);,}trackMemory: true,);'';
}
    const enableLogging = true;)}
  });
const [trainingStatuses, setTrainingStatuses] = useState<TrainingStatus[]>([]);
const [modelPerformances, setModelPerformances] = useState<ModelPerformance[]>([]);
const [refreshing, setRefreshing] = useState(false);
const [showPerformanceMonitor, setShowPerformanceMonitor] = useState(false);
const [selectedModel, setSelectedModel] = useState<string | null>(null);
const [showDetailsModal, setShowDetailsModal] = useState(false);

  // 加载数据/;,/g/;
const  loadData = useCallback(async () => {try {}      const statuses = modelTrainingService.getAllTrainingStatus();
const performances = modelTrainingService.getAllModelPerformance();
setTrainingStatuses(statuses);
setModelPerformances(performances);';'';
      ';'';
}
      performanceMonitor.recordMetric('data_load_success', 1);'}'';'';
    } catch (error) {performanceMonitor.recordError(error as Error);}}
}
    }
  }, [performanceMonitor]);

  // 刷新数据/;,/g/;
const  onRefresh = useCallback(async () => {setRefreshing(true);,}const await = loadData();
}
    setRefreshing(false);}
  }, [loadData]);

  // 开始训练/;,/g/;
const  handleStartTraining = useCallback(async (modelId: string) => {try {}}
      // 生成模拟训练数据}/;,/g/;
const mockData: TrainingData[] = Array.from({ length: 1000 ;}, (_, i) => ({}';,)id: `${modelId;}_data_${i}`,``')''`;,```;
type: 'diagnosis' as const;',')'';
input: { symptoms: [`symptom_${i;}`, `symptom_${i + 1}`] },`)```;,```;
output: { diagnosis: `diagnosis_${i % 10;}`, confidence: Math.random() ;},````;,```;
metadata: {timestamp: Date.now() - Math.random() * 86400000,;
quality: Math.random(),;
}
          const verified = Math.random() > 0.3;}
        }
      }));
await: modelTrainingService.addTrainingData(modelId, mockData);
const await = modelTrainingService.startTraining(modelId);
      ';'';
';,'';
performanceMonitor.recordMetric('training_started', 1);';'';
    } catch (error) {performanceMonitor.recordError(error as Error);}}
}
    }
  }, [performanceMonitor]);

  // 停止训练/;,/g/;
const  handleStopTraining = useCallback(async (modelId: string) => {try {}      const await = modelTrainingService.stopTraining(modelId);';'';
';'';
}
      performanceMonitor.recordMetric('training_stopped', 1);'}'';'';
    } catch (error) {performanceMonitor.recordError(error as Error);}}
}
    }
  }, [performanceMonitor]);

  // 查看详情/;,/g/;
const  handleViewDetails = useCallback((modelId: string) => {setSelectedModel(modelId);';,}setShowDetailsModal(true);';'';
}
    performanceMonitor.recordMetric('details_viewed', 1);'}'';'';
  }, [performanceMonitor]);

  // 监听训练事件/;,/g/;
useEffect(() => {const  handleStatusUpdate = () => {}}
      loadData();}
    };
const  handleTrainingCompleted = (data: any) => {}}
      loadData();}
    };
const  handleTrainingFailed = (data: any) => {}}
      loadData();}
    };';'';
';,'';
modelTrainingService.on('statusUpdated', handleStatusUpdate);';,'';
modelTrainingService.on('trainingCompleted', handleTrainingCompleted);';,'';
modelTrainingService.on('trainingFailed', handleTrainingFailed);';'';
';,'';
return () => {';,}modelTrainingService.off('statusUpdated', handleStatusUpdate);';,'';
modelTrainingService.off('trainingCompleted', handleTrainingCompleted);';'';
}
      modelTrainingService.off('trainingFailed', handleTrainingFailed);'}'';'';
    };
  }, [loadData]);

  // 初始化加载/;,/g/;
useEffect(() => {loadData();}    // 定期刷新/;,/g,/;
  interval: setInterval(loadData, 2000);
}
    return () => clearInterval(interval);}
  }, [loadData]);

  // 记录渲染性能/;,/g/;
useEffect(() => {}}
    performanceMonitor.recordRender();}
  });
const  getSelectedModelDetails = () => {if (!selectedModel) return null;,}const status = trainingStatuses.find(s => s.modelId === selectedModel);
const performance = modelPerformances.find(p => p.modelId === selectedModel);
}
    }
    return { status, performance };
  };
return (<SafeAreaView style={styles.container}>';)      <LinearGradient,'  />/;,'/g'/;
colors={['#667eea', '#764ba2']}';,'';
style={styles.background}
      >;
        {/* Header */}/;/g/;
        <View style={styles.header}>;
          <Text style={styles.headerTitle}>AI模型训练中心</Text>/;/g/;
          <View style={styles.headerActions}>);
            <TouchableOpacity,)  />/;,/g/;
style={styles.headerButton});
onPress={() => setShowPerformanceMonitor(!showPerformanceMonitor)}';'';
            >';'';
              <Ionicons name="speedometer-outline" size={24} color="#fff"  />"/;"/g"/;
            </TouchableOpacity>/;/g/;
            <TouchableOpacity,  />/;,/g/;
style={styles.headerButton}
              onPress={onRefresh}";"";
            >";"";
              <Ionicons name="refresh" size={24} color="#fff"  />"/;"/g"/;
            </TouchableOpacity>/;/g/;
          </View>/;/g/;
        </View>/;/g/;

        {/* Stats Overview */}/;/g/;
        <View style={styles.statsContainer}>;
          <View style={styles.statCard}>";"";
            <Text style={styles.statValue}>";"";
              {trainingStatuses.filter(s => s.status === 'training').length}';'';
            </Text>/;/g/;
            <Text style={styles.statLabel}>训练中</Text>/;/g/;
          </View>/;/g/;
          <View style={styles.statCard}>';'';
            <Text style={styles.statValue}>';'';
              {trainingStatuses.filter(s => s.status === 'completed').length}';'';
            </Text>/;/g/;
            <Text style={styles.statLabel}>已完成</Text>/;/g/;
          </View>/;/g/;
          <View style={styles.statCard}>;
            <Text style={styles.statValue}>;
              {modelPerformances.length}
            </Text>/;/g/;
            <Text style={styles.statLabel}>可用模型</Text>/;/g/;
          </View>/;/g/;
        </View>/;/g/;

        {/* Training Cards */}/;/g/;
        <ScrollView,  />/;,/g/;
style={styles.scrollView}
          refreshControl={}}
            <RefreshControl,}  />/;,/g/;
refreshing={refreshing}';,'';
onRefresh={onRefresh}';,'';
tintColor="#fff"";"";
            />/;/g/;
          }
          showsVerticalScrollIndicator={false}
        >;
          {trainingStatuses.map((status) => {}            const performance = modelPerformances.find(p => p.modelId === status.modelId);
}
            return (<TrainingCard,}  />/;,)key={status.modelId}/g/;
                status={status}
                performance={performance}
                onStartTraining={handleStartTraining}
                onStopTraining={handleStopTraining});
onViewDetails={handleViewDetails});
              />)/;/g/;
            );
          })}
        </ScrollView>/;/g/;

        {/* Performance Monitor */}"/;"/g"/;
        <PerformanceMonitor,"  />/;,"/g"/;
componentName="AIModelTrainingScreen";
visible={showPerformanceMonitor}";,"";
onToggle={setShowPerformanceMonitor}";,"";
position="floating";
theme="dark"";"";
        />/;/g/;

        {/* Details Modal */}/;/g/;
        <Modal,"  />/;,"/g"/;
visible={showDetailsModal}";,"";
animationType="slide";
presentationStyle="pageSheet";
onRequestClose={() => setShowDetailsModal(false)}
        >;
          <View style={styles.modalContainer}>;
            <View style={styles.modalHeader}>;
              <Text style={styles.modalTitle}>;

              </Text>/;/g/;
              <TouchableOpacity,  />/;,/g/;
onPress={() => setShowDetailsModal(false)}
                style={styles.modalCloseButton}";"";
              >";"";
                <Ionicons name="close" size={24} color="#333"  />"/;"/g"/;
              </TouchableOpacity>/;/g/;
            </View>/;/g/;

            <ScrollView style={styles.modalContent}>;
              {(() => {}                const details = getSelectedModelDetails();
if (!details.status) return null;

}
                return (<View>})                    <Text style={styles.modalSectionTitle}>训练状态</Text>/;/g/;
                    <View style={styles.modalDetailItem}>);
                      <Text style={styles.modalDetailLabel}>当前状态:</Text>)/;/g/;
                      <Text style={styles.modalDetailValue}>);
                        {getStatusText(details.status.status)}
                      </Text>/;/g/;
                    </View>/;/g/;
                    <View style={styles.modalDetailItem}>;
                      <Text style={styles.modalDetailLabel}>训练进度: </Text>/;/g/;
                      <Text style={styles.modalDetailValue}>;
                        {details.status.progress.toFixed(1)}%;
                      </Text>/;/g/;
                    </View>/;/g/;
                    <View style={styles.modalDetailItem}>;
                      <Text style={styles.modalDetailLabel}>当前轮次: </Text>/;/g/;
                      <Text style={styles.modalDetailValue}>;
                        {details.status.currentEpoch} / {details.status.totalEpochs}/;/g/;
                      </Text>/;/g/;
                    </View>/;/g/;

                    {details.performance && (<>})                        <Text style={styles.modalSectionTitle}>性能指标</Text>/;/g/;
                        <View style={styles.modalDetailItem}>);
                          <Text style={styles.modalDetailLabel}>准确率:</Text>)/;/g/;
                          <Text style={styles.modalDetailValue}>);
                            {(details.performance.accuracy * 100).toFixed(2)}%;
                          </Text>/;/g/;
                        </View>/;/g/;
                        <View style={styles.modalDetailItem}>;
                          <Text style={styles.modalDetailLabel}>精确率: </Text>/;/g/;
                          <Text style={styles.modalDetailValue}>;
                            {(details.performance.precision * 100).toFixed(2)}%;
                          </Text>/;/g/;
                        </View>/;/g/;
                        <View style={styles.modalDetailItem}>;
                          <Text style={styles.modalDetailLabel}>召回率: </Text>/;/g/;
                          <Text style={styles.modalDetailValue}>;
                            {(details.performance.recall * 100).toFixed(2)}%;
                          </Text>/;/g/;
                        </View>/;/g/;
                        <View style={styles.modalDetailItem}>;
                          <Text style={styles.modalDetailLabel}>F1分数: </Text>/;/g/;
                          <Text style={styles.modalDetailValue}>;
                            {details.performance.f1Score.toFixed(3)}
                          </Text>/;/g/;
                        </View>/;/g/;
                        <View style={styles.modalDetailItem}>;
                          <Text style={styles.modalDetailLabel}>推理时间: </Text>/;/g/;
                          <Text style={styles.modalDetailValue}>;
                            {details.performance.inferenceTime.toFixed(1)}ms;
                          </Text>/;/g/;
                        </View>/;/g/;
                        <View style={styles.modalDetailItem}>;
                          <Text style={styles.modalDetailLabel}>吞吐量: </Text>/;/g/;
                          <Text style={styles.modalDetailValue}>;
                            {details.performance.throughput.toFixed(0)} req/s/;/g/;
                          </Text>/;/g/;
                        </View>/;/g/;
                      < />/;/g/;
                    )}
                  </View>/;/g/;
                );
              })()}
            </ScrollView>/;/g/;
          </View>/;/g/;
        </Modal>/;/g/;
      </LinearGradient>/;/g/;
    </SafeAreaView>/;/g/;
  );
};
const  getStatusText = (status: string) => {switch (status) {}}
}
  ;}
};
const  styles = StyleSheet.create({)container: {,;}}
    const flex = 1;}
  }
background: {,;}}
    const flex = 1;}
  },";,"";
header: {,";,}flexDirection: 'row';','';
justifyContent: 'space-between';','';
alignItems: 'center';','';
paddingHorizontal: 20,;
paddingTop: 20,;
}
    const paddingBottom = 10;}
  }
headerTitle: {,';,}fontSize: 24,';,'';
fontWeight: 'bold';','';'';
}
    const color = '#fff';'}'';'';
  },';,'';
headerActions: {,';}}'';
    const flexDirection = 'row';'}'';'';
  }
headerButton: {marginLeft: 15,;
}
    const padding = 8;}
  },';,'';
statsContainer: {,';,}flexDirection: 'row';','';
justifyContent: 'space-around';','';
paddingHorizontal: 20,;
}
    const paddingVertical = 15;)}
  },)';,'';
statCard: {,)';,}backgroundColor: 'rgba(255, 255, 255, 0.2)',';,'';
borderRadius: 12,';,'';
padding: 15,';,'';
alignItems: 'center';','';'';
}
    const minWidth = 80;}
  }
statValue: {,';,}fontSize: 24,';,'';
fontWeight: 'bold';','';'';
}
    const color = '#fff';'}'';'';
  }
statLabel: {,';,}fontSize: 12,';,'';
color: 'rgba(255, 255, 255, 0.8)',';'';
}
    const marginTop = 4;}
  }
scrollView: {flex: 1,;
}
    const paddingHorizontal = 20;}
  }
trainingCard: {marginBottom: 15,';,'';
borderRadius: 16,';'';
}
    const overflow = 'hidden';'}'';'';
  }
cardGradient: {,;}}
    const padding = 20;}
  },';,'';
cardHeader: {,';,}flexDirection: 'row';','';
justifyContent: 'space-between';','';
alignItems: 'center';','';'';
}
    const marginBottom = 15;}
  },';,'';
cardTitleContainer: {,';,}flexDirection: 'row';','';'';
}
    const alignItems = 'center';'}'';'';
  }
statusIndicator: {width: 8,;
height: 8,;
borderRadius: 4,;
}
    const marginRight = 8;}
  }
cardTitle: {,';,}fontSize: 16,';,'';
fontWeight: 'bold';','';'';
}
    const color = '#fff';'}'';'';
  }
statusText: {,';,}fontSize: 14,';'';
}
    const fontWeight = '600';'}'';'';
  }
progressSection: {,;}}
    const marginBottom = 15;}
  },';,'';
progressInfo: {,';,}flexDirection: 'row';','';
justifyContent: 'space-between';','';'';
}
    const marginBottom = 8;}
  }
progressText: {,';,}fontSize: 14,';'';
}
    color: 'rgba(255, 255, 255, 0.8)','}'';'';
  ;}
progressPercentage: {,';,}fontSize: 14,';,'';
fontWeight: 'bold';','';'';
}
    const color = '#fff';'}'';'';
  }
progressBar: {,';,}height: 6,';,'';
backgroundColor: 'rgba(255, 255, 255, 0.2)',';,'';
borderRadius: 3,';'';
}
    const overflow = 'hidden';'}'';'';
  },';,'';
progressFill: {,';,}height: '100%';','';'';
}
    const borderRadius = 3;}
  }
timeRemaining: {,';,}fontSize: 12,';,'';
color: 'rgba(255, 255, 255, 0.7)',';,'';
marginTop: 4,';'';
}
    const textAlign = 'center';'}'';'';
  }
metricsSection: {,;}}
    const marginBottom = 15;}
  },';,'';
metricRow: {,';,}flexDirection: 'row';','';
justifyContent: 'space-between';','';'';
}
    const marginBottom = 8;}
  }
metricItem: {,';,}flex: 1,';'';
}
    const alignItems = 'center';'}'';'';
  }
metricLabel: {,';,}fontSize: 12,';,'';
color: 'rgba(255, 255, 255, 0.7)',';'';
}
    const marginBottom = 4;}
  }
metricValue: {,';,}fontSize: 16,';,'';
fontWeight: 'bold';','';'';
}
    const color = '#fff';'}'';'';
  },';,'';
cardActions: {,';,}flexDirection: 'row';','';'';
}
    const justifyContent = 'space-between';'}'';'';
  },';,'';
actionButton: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';
paddingHorizontal: 16,;
paddingVertical: 10,;
borderRadius: 8,;
flex: 1,;
}
    const marginHorizontal = 4;}
  },';,'';
startButton: {,';}}'';
    const backgroundColor = '#2ed573';'}'';'';
  },';,'';
stopButton: {,';}}'';
    const backgroundColor = '#ff4757';'}'';'';
  },';,'';
detailsButton: {,';}}'';
    const backgroundColor = '#5352ed';'}'';'';
  },';,'';
actionButtonText: {,';,}color: '#fff';','';
fontSize: 14,';,'';
fontWeight: '600';','';'';
}
    const marginLeft = 6;}
  }
modalContainer: {,';,}flex: 1,';'';
}
    const backgroundColor = '#fff';'}'';'';
  },';,'';
modalHeader: {,';,}flexDirection: 'row';','';
justifyContent: 'space-between';','';
alignItems: 'center';','';
padding: 20,';,'';
borderBottomWidth: 1,';'';
}
    const borderBottomColor = '#e0e0e0';'}'';'';
  }
modalTitle: {,';,}fontSize: 18,';,'';
fontWeight: 'bold';','';'';
}
    const color = '#333';'}'';'';
  }
modalCloseButton: {,;}}
    const padding = 4;}
  }
modalContent: {flex: 1,;
}
    const padding = 20;}
  }
modalSectionTitle: {,';,}fontSize: 16,';,'';
fontWeight: 'bold';','';
color: '#333';','';
marginTop: 20,;
}
    const marginBottom = 10;}
  },';,'';
modalDetailItem: {,';,}flexDirection: 'row';','';
justifyContent: 'space-between';','';
paddingVertical: 8,';,'';
borderBottomWidth: 1,';'';
}
    const borderBottomColor = '#f0f0f0';'}'';'';
  }
modalDetailLabel: {,';,}fontSize: 14,';'';
}
    const color = '#666';'}'';'';
  }
modalDetailValue: {,';,}fontSize: 14,';,'';
fontWeight: '600';','';'';
}
    const color = '#333';'}'';'';
  }
});
';,'';
export default AIModelTrainingScreen; ''';