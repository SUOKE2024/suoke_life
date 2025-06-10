import { RouteProp, useNavigation, useRoute } from "@react-navigation/native";""/;,"/g"/;
import { NativeStackNavigationProp } from "@react-navigation/native-stack";""/;,"/g"/;
import React, { useCallback, useEffect, useState } from "react";";
import {;,}ActivityIndicator,;
Alert,;
Dimensions,;
Modal,;
ScrollView,;
StatusBar,;
StyleSheet,;
Text,;
TouchableOpacity,";"";
}
  View'}'';'';
} from "react-native";";
import { SafeAreaView } from "react-native-safe-area-context";";
import Icon from "react-native-vector-icons/MaterialCommunityIcons";""/;,"/g"/;
import { useSelector } from "react-redux";";
import { RootState } from "../../store";""/;"/g"/;
';,'';
const { width, height } = Dimensions.get('window');';'';

// 诊断结果类型/;,/g/;
interface DiagnosisResult {id: string}serviceType: string,;
result: string,;
confidence: number,;
timestamp: Date,;
}
}
  const details = any;}
}

// 诊断服务信息类型/;,/g/;
interface DiagnosisServiceInfo {id: string}name: string,;
description: string,;
icon: string,;
endpoint: string,';,'';
capabilities: string[],';,'';
status: 'active' | 'inactive' | 'maintenance';','';
colors: {primary: string,;
secondary: string,;
}
}
  const accent = string;}
  };
}

// 路由参数类型/;,/g/;
const type = RootStackParamList = {}
  const DiagnosisService = { serviceType: string ;};
};
const type = DiagnosisServiceScreenRouteProp = RouteProp<';,'';
RootStackParamList,';'';
  'DiagnosisService'';'';
>;
const type = DiagnosisServiceScreenNavigationProp = NativeStackNavigationProp<';,'';
RootStackParamList,';'';
  'DiagnosisService'';'';
>;
const  DiagnosisServiceScreen: React.FC = () => {}
  const navigation = useNavigation<Suspense fallback={<LoadingSpinner  />}><DiagnosisServiceScreenNavigationProp></Suspense>();/;,/g/;
const route = useRoute<Suspense fallback={<LoadingSpinner  />}><DiagnosisServiceScreenRouteProp></Suspense>();/;,/g/;
const { serviceType } = route.params;
const [serviceInfo, setServiceInfo] = useState<DiagnosisServiceInfo | null>(null;);
  );
const [diagnosisResults, setDiagnosisResults] = useState<DiagnosisResult[]>([]);
  );
const [loading, setLoading] = useState(true);
const [diagnosing, setDiagnosing] = useState(false);
const [showResultModal, setShowResultModal] = useState(false);
const [currentResult, setCurrentResult] = useState<DiagnosisResult | null>(null;);
  );

  // 从Redux获取用户信息'/;,'/g'/;
const authState = useSelector(state: RootState) => state.auth);';,'';
const user = 'user' in authState ? authState.user : null;';'';

  // 诊断服务配置/;,/g,/;
  const: diagnosisServices: Record<string, DiagnosisServiceInfo> = {';,}calculation: {,';,}id: 'calculation';','';'';
';'';
';,'';
icon: '🔍';','';
endpoint: 'http://localhost:8023';',''/;'/g'/;
';,'';
status: 'active';','';
colors: {,';,}primary: '#FF6B6B';','';
secondary: '#FFEBEE';','';'';
}
        const accent = '#F44336'}'';'';
      ;}
    },';,'';
look: {,';,}id: 'look';','';'';
';'';
';,'';
icon: '👁️';','';
endpoint: 'http://localhost:8020';',''/;'/g'/;
';,'';
status: 'active';','';
colors: {,';,}primary: '#4CAF50';','';
secondary: '#E8F5E8';','';'';
}
        const accent = '#2E7D32'}'';'';
      ;}
    },';,'';
listen: {,';,}id: 'listen';','';'';
';'';
';,'';
icon: '👂';','';
endpoint: 'http://localhost:8022';',''/;'/g'/;
';,'';
status: 'active';','';
colors: {,';,}primary: '#2196F3';','';
secondary: '#E3F2FD';','';'';
}
        const accent = '#1976D2'}'';'';
      ;}
    },';,'';
inquiry: {,';,}id: 'inquiry';','';'';
';'';
';,'';
icon: '💬';','';
endpoint: 'http://localhost:8021';',''/;'/g'/;
';,'';
status: 'active';','';
colors: {,';,}primary: '#9C27B0';','';
secondary: '#F3E5F5';','';'';
}
        const accent = '#7B1FA2'}'';'';
      ;}
    },';,'';
palpation: {,';,}id: 'palpation';','';'';
';'';
';,'';
icon: '🤲';','';
endpoint: 'http://localhost:8024';',''/;'/g'/;
';,'';
status: 'active';','';
colors: {,';,}primary: '#FF9800';','';
secondary: '#FFF3E0';','';'';
}
        const accent = '#F57C00'}'';'';
      ;}
    }
  };

  // 初始化服务信息/;,/g/;
useEffect() => {const service = diagnosisServices[serviceType];,}if (service) {setServiceInfo(service);}}
      loadDiagnosisHistory();}
    }
    setLoading(false);
  }, [serviceType]);

  // 加载诊断历史/;,/g/;
const  loadDiagnosisHistory = useCallback(async () => {try {}      // 模拟加载历史记录/;,/g/;
const  mockHistory: DiagnosisResult[] = [;]';'';
        {';,}const id = '1';';,'';
serviceType,;
confidence: 0.85,;
timestamp: new Date(Date.now() - 86400000), // 1天前/;/g/;
}
}
        ;},';'';
        {';,}const id = '2';';,'';
serviceType,;
confidence: 0.72,;
timestamp: new Date(Date.now() - 172800000), // 2天前/;/g/;
}
}
        ;}
];
      ];
setDiagnosisResults(mockHistory);
    } catch (error) {}}
}
    }
  }, [serviceType]);

  // 开始诊断/;,/g/;
const  startDiagnosis = useCallback(async () => {if (!serviceInfo) return;,}setDiagnosing(true);
try {// 模拟诊断过程/;,}const await = new Promise(resolve) =>;,/g/;
setTimeout(resolve, 3000 + Math.random() * 2000);
      );
const: mockResult: DiagnosisResult = {id: Date.now().toString(),;
serviceType: serviceInfo.id,;
result: generateMockResult(serviceInfo.id),;
confidence: 0.75 + Math.random() * 0.2,;
timestamp: new Date(),;
}
        const details = generateMockDetails(serviceInfo.id)}
      ;};
setDiagnosisResults(prev) => [mockResult, ...prev]);
setCurrentResult(mockResult);
setShowResultModal(true);
    } catch (error) {}}
}
    } finally {}}
      setDiagnosing(false);}
    }
  }, [serviceInfo]);

  // 生成模拟诊断结果/;,/g/;
const  generateMockResult = (serviceType: string): string => {const  results = {}      const calculation = [;]];
      ],;
const look = [;]];
      ],;
const listen = [;]];
      ],;
const inquiry = [;]];
      ],;
const palpation = [;]}
];
      ]}
    ;};
const  serviceResults =;
results[serviceType as keyof typeof results] || results.calculation;
return serviceResults[Math.floor(Math.random() * serviceResults.length)];
  };

  // 生成模拟详细信息/;,/g/;
const  generateMockDetails = (serviceType: string) => {return {}      score: Math.floor(70 + Math.random() * 25),;
metrics: {accuracy: Math.floor(80 + Math.random() * 15),;
reliability: Math.floor(75 + Math.random() * 20),;
}
        const completeness = Math.floor(85 + Math.random() * 10)}
      ;}
const recommendations = [;]];
      ].slice(0, 2 + Math.floor(Math.random() * 2));
    ;};
  };

  // 渲染服务能力/;,/g/;
const  renderCapabilities = () => {if (!serviceInfo) return null;}}
}
    return (<View style={styles.capabilitiesContainer}>);
        <Text style={styles.sectionTitle}>服务能力</Text>)/;/g/;
        <View style={styles.capabilitiesGrid}>);
          {serviceInfo.capabilities.map(capability, index) => (<View;}  />/;,)key={index}/g/;
              style={}[;]}
                styles.capabilityItem,}
                { backgroundColor: serviceInfo.colors.secondary ;}
];
              ]}
            >;
              <Text;  />/;,/g/;
style={}[;]}
                  styles.capabilityText,}
                  { color: serviceInfo.colors.primary ;}
];
                ]}
              >;
                {capability});
              </Text>)/;/g/;
            </View>)/;/g/;
          ))}
        </View>/;/g/;
      </View>/;/g/;
    );
  };

  // 渲染诊断历史/;,/g/;
const  renderDiagnosisHistory = () => {}}
    if (diagnosisResults.length === 0) {}';,'';
return (<View style={styles.emptyHistory}>';)          <Icon name="history" size={48} color="#CCC"  />"/;"/g"/;
          <Text style={styles.emptyHistoryText}>暂无诊断记录</Text>)/;/g/;
          <Text style={styles.emptyHistorySubtext}>开始您的第一次诊断</Text>)/;/g/;
        </View>)/;/g/;
      );
    }

    return (<View style={styles.historyContainer}>);
        <Text style={styles.sectionTitle}>诊断历史</Text>)/;/g/;
        {diagnosisResults.map(result) => (<TouchableOpacity;)}  />/;,/g/;
key={result.id});
style={styles.historyItem});
onPress={() => {}              setCurrentResult(result);
}
              setShowResultModal(true);}
            }}
          >;
            <View style={styles.historyHeader}>";"";
              <Text style={styles.historyDate}>";"";
                {result.timestamp.toLocaleDateString('zh-CN')}';'';
              </Text>/;/g/;
              <View;  />/;,/g/;
style={}[;]}
                  styles.confidenceBadge,}
                  { backgroundColor: getConfidenceColor(result.confidence) ;}
];
                ]}
              >;
                <Text style={styles.confidenceText}>;
                  {Math.round(result.confidence * 100)}%;
                </Text>/;/g/;
              </View>/;/g/;
            </View>/;/g/;
            <Text style={styles.historyResult} numberOfLines={2}>;
              {result.result}
            </Text>/;/g/;
          </TouchableOpacity>/;/g/;
        ))}
      </View>/;/g/;
    );
  };

  // 获取置信度颜色'/;,'/g'/;
const  getConfidenceColor = (confidence: number): string => {';,}if (confidence >= 0.8) return '#4CAF50';';,'';
if (confidence >= 0.6) return '#FF9800';';'';
}
    return '#F44336';'}'';'';
  };

  // 渲染结果模态框/;,/g/;
const  renderResultModal = () => {if (!currentResult || !serviceInfo) return null;}}
    return (<Modal;}'  />/;,)visible={showResultModal}')'';,'/g'/;
animationType="slide")";
transparent={true});
onRequestClose={() => setShowResultModal(false)}
      >;
        <View style={styles.modalOverlay}>;
          <View style={styles.modalContent}>;
            <View;  />/;,/g/;
style={}[;]}
                styles.modalHeader,}
                { backgroundColor: serviceInfo.colors.primary ;}
];
              ]}
            >;
              <Text style={styles.modalTitle}>诊断结果</Text>/;/g/;
              <TouchableOpacity;  />/;,/g/;
style={styles.modalCloseButton}
                onPress={() => setShowResultModal(false)}";"";
              >";"";
                <Icon name="close" size={24} color="#FFFFFF"  />"/;"/g"/;
              </TouchableOpacity>/;/g/;
            </View>/;/g/;

            <ScrollView style={styles.modalBody}>;
              <View style={styles.resultSection}>;
                <Text style={styles.resultTitle}>诊断结论</Text>/;/g/;
                <Text style={styles.resultText}>{currentResult.result}</Text>/;/g/;
              </View>/;/g/;

              <View style={styles.resultSection}>;
                <Text style={styles.resultTitle}>置信度</Text>/;/g/;
                <View style={styles.confidenceContainer}>;
                  <View style={styles.confidenceBar}>;
                    <View;  />/;,/g/;
style={[;,]styles.confidenceFill,;}}
                        {}
                          width: `${currentResult.confidence * 100;}%`,````;,```;
const backgroundColor = getConfidenceColor(currentResult.confidence;);
                          );
                        }
];
                      ]}
                    />/;/g/;
                  </View>/;/g/;
                  <Text style={styles.confidencePercentage}>;
                    {Math.round(currentResult.confidence * 100)}%;
                  </Text>/;/g/;
                </View>/;/g/;
              </View>/;/g/;

              {currentResult.details?.recommendations && (<View style={styles.resultSection}>);
                  <Text style={styles.resultTitle}>建议</Text>)/;/g/;
                  {currentResult.details.recommendations.map(rec: string, index: number) => (<View key={index;} style={styles.recommendationItem}>";)                        <Icon;"  />/;,"/g"/;
name="check-circle";
size={16}
                          color={serviceInfo.colors.primary}
                        />)/;/g/;
                        <Text style={styles.recommendationText}>{rec}</Text>)/;/g/;
                      </View>)/;/g/;
                    );
                  )}
                </View>/;/g/;
              )}

              <View style={styles.resultSection}>;
                <Text style={styles.resultTitle}>诊断时间</Text>"/;"/g"/;
                <Text style={styles.resultText}>";"";
                  {currentResult.timestamp.toLocaleString('zh-CN')}';'';
                </Text>/;/g/;
              </View>/;/g/;
            </ScrollView>/;/g/;
          </View>/;/g/;
        </View>/;/g/;
      </Modal>/;/g/;
    );
  };
if (loading) {}';,'';
return (<SafeAreaView style={styles.container}>';)        <StatusBar barStyle="light-content" backgroundColor="#4A90E2"  />"/;"/g"/;
        <View style={styles.loadingContainer}>";"";
          <ActivityIndicator size="large" color="#4A90E2"  />"/;"/g"/;
          <Text style={styles.loadingText}>加载中...</Text>)/;/g/;
        </View>)/;/g/;
      </SafeAreaView>)/;/g/;
    );
  }

  if (!serviceInfo) {}";,"";
return (<SafeAreaView style={styles.container}>";)        <StatusBar barStyle="light-content" backgroundColor="#F44336"  />"/;"/g"/;
        <View style={styles.errorContainer}>";"";
          <Icon name="alert-circle" size={64} color="#F44336"  />"/;"/g"/;
          <Text style={styles.errorTitle}>服务不存在</Text>/;/g/;
          <Text style={styles.errorSubtitle}>请检查服务类型是否正确</Text>)/;/g/;
          <TouchableOpacity;)  />/;,/g/;
style={styles.backButton});
onPress={() => navigation.goBack()}
          >;
            <Text style={styles.backButtonText}>返回</Text>/;/g/;
          </TouchableOpacity>/;/g/;
        </View>/;/g/;
      </SafeAreaView>/;/g/;
    );
  }

  const colors = serviceInfo.colors;
";,"";
return (<SafeAreaView style={styles.container}>";)      <StatusBar barStyle="light-content" backgroundColor={colors.primary}  />"/;"/g"/;

      {// 头部}/;/g/;
      <View style={[styles.header, { backgroundColor: colors.primary ;}]}>);
        <TouchableOpacity;)  />/;,/g/;
style={styles.headerBackButton});
onPress={() => navigation.goBack()}";"";
        >";"";
          <Icon name="arrow-left" size={24} color="#FFFFFF"  />"/;"/g"/;
        </TouchableOpacity>/;/g/;

        <View style={styles.headerInfo}>;
          <Text style={styles.headerIcon}>{serviceInfo.icon}</Text>/;/g/;
          <View style={styles.headerTextContainer}>;
            <Text style={styles.headerTitle}>{serviceInfo.name}</Text>/;/g/;
            <Text style={styles.headerSubtitle}>;

            </Text>/;/g/;
          </View>/;/g/;
        </View>/;/g/;
";"";
        <TouchableOpacity style={styles.moreButton}>";"";
          <Icon name="dots-vertical" size={24} color="#FFFFFF"  />"/;"/g"/;
        </TouchableOpacity>/;/g/;
      </View>/;/g/;

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>;
        {// 服务描述}/;/g/;
        <View style={styles.descriptionContainer}>;
          <Text style={styles.descriptionText}>{serviceInfo.description}</Text>/;/g/;
        </View>/;/g/;

        {// 服务能力}/;/g/;
        {renderCapabilities()}

        {// 开始诊断按钮}/;/g/;
        <View style={styles.actionContainer}>;
          <TouchableOpacity;  />/;,/g/;
style={}[;]}
              styles.diagnosisButton,}
              { backgroundColor: colors.primary ;}
diagnosing && styles.diagnosisButtonDisabled;
];
            ]}
            onPress={startDiagnosis}
            disabled={diagnosing}";"";
          >";"";
            {diagnosing ? (<ActivityIndicator size="small" color="#FFFFFF"  />")"}"/;"/g"/;
            ) : (<Icon name="play-circle" size={24} color="#FFFFFF"  />")""/;"/g"/;
            )}
            <Text style={styles.diagnosisButtonText}>;

            </Text>/;/g/;
          </TouchableOpacity>/;/g/;
        </View>/;/g/;

        {// 诊断历史}/;/g/;
        {renderDiagnosisHistory()}
      </ScrollView>/;/g/;

      {// 结果模态框}/;/g/;
      {renderResultModal()}
    </SafeAreaView>/;/g/;
  );
};
const  styles = StyleSheet.create({)container: {,";,}flex: 1,";"";
}
    const backgroundColor = '#F8F9FA'}'';'';
  ;}
loadingContainer: {,';,}flex: 1,';,'';
justifyContent: 'center';','';'';
}
    const alignItems = 'center'}'';'';
  ;}
loadingText: {marginTop: 10,';,'';
fontSize: 16,';'';
}
    const color = '#666'}'';'';
  ;}
errorContainer: {,';,}flex: 1,';,'';
justifyContent: 'center';','';
alignItems: 'center';','';'';
}
    const paddingHorizontal = 40}
  ;}
errorTitle: {,';,}fontSize: 20,';,'';
fontWeight: 'bold';','';
color: '#333';','';
marginTop: 16,;
}
    const marginBottom = 8}
  ;}
errorSubtitle: {,';,}fontSize: 14,';,'';
color: '#666';','';
textAlign: 'center';','';'';
}
    const marginBottom = 24}
  ;},';,'';
backButton: {,';,}backgroundColor: '#4A90E2';','';
paddingHorizontal: 24,;
paddingVertical: 12,;
}
    const borderRadius = 8}
  ;},';,'';
backButtonText: {,';,}color: '#FFFFFF';','';
fontSize: 16,';'';
}
    const fontWeight = '600'}'';'';
  ;},';,'';
header: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';
paddingHorizontal: 16,;
paddingVertical: 12,';,'';
elevation: 4,';'';
}
    shadowColor: '#000';',}'';
shadowOffset: { width: 0, height: 2 ;}
shadowOpacity: 0.1,;
const shadowRadius = 4;
  ;}
headerBackButton: {padding: 8,;
}
    const marginRight = 8}
  ;}
headerInfo: {,';,}flex: 1,';,'';
flexDirection: 'row';','';'';
}
    const alignItems = 'center'}'';'';
  ;}
headerIcon: {fontSize: 32,;
}
    const marginRight = 12}
  ;}
headerTextContainer: {,;}}
  const flex = 1}
  ;}
headerTitle: {,';,}fontSize: 18,';,'';
fontWeight: 'bold';','';'';
}
    const color = '#FFFFFF'}'';'';
  ;}
headerSubtitle: {,';,}fontSize: 12,';,'';
color: '#E3F2FD';','';'';
}
    const marginTop = 2}
  ;}
moreButton: {,;}}
  const padding = 8}
  ;}
content: {,;}}
  const flex = 1}
  ;}
descriptionContainer: {margin: 16,';,'';
padding: 16,';,'';
backgroundColor: '#FFFFFF';','';
borderRadius: 12,';'';
}
    shadowColor: '#000';','}'';
shadowOffset: { width: 0, height: 1 ;}
shadowOpacity: 0.1,;
shadowRadius: 2,;
const elevation = 2;
  ;}
descriptionText: {,';,}fontSize: 14,';,'';
color: '#666';','';'';
}
    const lineHeight = 20}
  ;}
capabilitiesContainer: {margin: 16,;
}
    const marginTop = 0}
  ;}
sectionTitle: {,';,}fontSize: 18,';,'';
fontWeight: '600';','';
color: '#333';','';'';
}
    const marginBottom = 12}
  ;},';,'';
capabilitiesGrid: {,';,}flexDirection: 'row';','';
flexWrap: 'wrap';','';'';
}
    const gap = 8}
  ;}
capabilityItem: {paddingHorizontal: 12,;
paddingVertical: 6,;
borderRadius: 16,;
marginRight: 8,;
}
    const marginBottom = 8}
  ;}
capabilityText: {,';,}fontSize: 12,';'';
}
    const fontWeight = '500'}'';'';
  ;}
actionContainer: {margin: 16,;
}
    const marginTop = 0}
  ;},';,'';
diagnosisButton: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';
justifyContent: 'center';','';
paddingVertical: 16,';,'';
borderRadius: 12,';'';
}
    shadowColor: '#000';',}'';
shadowOffset: { width: 0, height: 2 ;}
shadowOpacity: 0.1,;
shadowRadius: 4,;
const elevation = 3;
  ;}
diagnosisButtonDisabled: {,;}}
  const opacity = 0.7}
  ;},';,'';
diagnosisButtonText: {,';,}color: '#FFFFFF';','';
fontSize: 16,';,'';
fontWeight: '600';','';'';
}
    const marginLeft = 8}
  ;}
historyContainer: {margin: 16,;
}
    const marginTop = 0}
  ;},';,'';
historyItem: {,';,}backgroundColor: '#FFFFFF';','';
padding: 16,;
borderRadius: 12,';,'';
marginBottom: 12,';'';
}
    shadowColor: '#000';','}'';
shadowOffset: { width: 0, height: 1 ;}
shadowOpacity: 0.1,;
shadowRadius: 2,;
const elevation = 2;
  ;},';,'';
historyHeader: {,';,}flexDirection: 'row';','';
justifyContent: 'space-between';','';
alignItems: 'center';','';'';
}
    const marginBottom = 8}
  ;}
historyDate: {,';,}fontSize: 12,';'';
}
    const color = '#999'}'';'';
  ;}
confidenceBadge: {paddingHorizontal: 8,;
paddingVertical: 2,;
}
    const borderRadius = 10}
  ;}
confidenceText: {,';,}fontSize: 10,';,'';
color: '#FFFFFF';','';'';
}
    const fontWeight = '600'}'';'';
  ;}
historyResult: {,';,}fontSize: 14,';,'';
color: '#333';','';'';
}
    const lineHeight = 20}
  ;},';,'';
emptyHistory: {,';,}alignItems: 'center';','';'';
}
    const paddingVertical = 40}
  ;}
emptyHistoryText: {,';,}fontSize: 16,';,'';
color: '#666';','';
marginTop: 12,';'';
}
    const fontWeight = '500'}'';'';
  ;}
emptyHistorySubtext: {,';,}fontSize: 12,';,'';
color: '#999';','';'';
}
    const marginTop = 4}
  ;},);
modalOverlay: {,)';,}flex: 1,)';,'';
backgroundColor: 'rgba(0, 0, 0, 0.5)',';,'';
justifyContent: 'center';','';'';
}
    const alignItems = 'center'}'';'';
  ;},';,'';
modalContent: {,';,}backgroundColor: '#FFFFFF';','';
borderRadius: 16,;
width: width * 0.9,';,'';
maxHeight: height * 0.8,';'';
}
    const overflow = 'hidden'}'';'';
  ;},';,'';
modalHeader: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';
justifyContent: 'space-between';','';
paddingHorizontal: 20,;
}
    const paddingVertical = 16}
  ;}
modalTitle: {,';,}fontSize: 18,';,'';
fontWeight: 'bold';','';'';
}
    const color = '#FFFFFF'}'';'';
  ;}
modalCloseButton: {,;}}
  const padding = 4}
  ;}
modalBody: {,;}}
  const padding = 20}
  ;}
resultSection: {,;}}
  const marginBottom = 20}
  ;}
resultTitle: {,';,}fontSize: 16,';,'';
fontWeight: '600';','';
color: '#333';','';'';
}
    const marginBottom = 8}
  ;}
resultText: {,';,}fontSize: 14,';,'';
color: '#666';','';'';
}
    const lineHeight = 20}
  ;},';,'';
confidenceContainer: {,';,}flexDirection: 'row';','';'';
}
    const alignItems = 'center'}'';'';
  ;}
confidenceBar: {flex: 1,';,'';
height: 8,';,'';
backgroundColor: '#E0E0E0';','';
borderRadius: 4,;
}
    const marginRight = 12}
  ;},';,'';
confidenceFill: {,';,}height: '100%';','';'';
}
    const borderRadius = 4}
  ;}
confidencePercentage: {,';,}fontSize: 14,';,'';
fontWeight: '600';','';
color: '#333';','';'';
}
    const minWidth = 40}
  ;},';,'';
recommendationItem: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';'';
}
    const marginBottom = 8}
  ;}
recommendationText: {,';,}fontSize: 14,';,'';
color: '#666';','';
marginLeft: 8,;
}
    const flex = 1}
  ;}
});
export default DiagnosisServiceScreen;';'';
''';