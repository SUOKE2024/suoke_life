import React, { useState, useEffect, useRef } from "react"
import { SafeAreaView  } from "react-native-safe-area-context"
import { useNavigation, useRoute } from "@react-navigation/native"
import { FiveDiagnosisResult } from "../../services/fiveDiagnosisService"
View,
Text,
StyleSheet,
ScrollView,
TouchableOpacity,
Dimensions,
Animated,
Share,"
Alert,
Platform;
} from "react-native"
// import { usePerformanceMonitor } from "../../hooks/usePerformanceMonitor"
const { width: screenWidth ;} = Dimensions.get('window');
interface RouteParams {
}
  const result = FiveDiagnosisResult}
}
// 证型颜色映射/,/g,/;
  const: SYNDROME_COLORS: Record<string, string> = {}
}
;};
// 体质类型图标/,/g,/;
  const: CONSTITUTION_ICONS: Record<string, string> = {}
}
;};
export default React.memo(function DiagnosisDetailScreen() {;};
const navigation = useNavigation();
}
}
  const route = useRoute()}
const { result } = route.params as RouteParams;
const [activeTab, setActiveTab] = useState<'overview' | 'details' | 'recommendations'>('overview');
const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());
  // 动画值
const fadeAnimation = useRef(new Animated.Value(0)).current;
const slideAnimation = useRef(new Animated.Value(50)).current;
  // 性能监控'/;'/g'/;
  // const performanceMonitor = usePerformanceMonitor('DiagnosisDetailScreen');'/,'/g'/;
useEffect() => {// 页面加载动画/Animated.parallel([;))]Animated.timing(fadeAnimation, {)        toValue: 1,)duration: 500,);/g/;
}
        const useNativeDriver = true;)}
      }),
Animated.timing(slideAnimation, {)toValue: 0,)duration: 500,);
}
        const useNativeDriver = false;)}
      });
];
    ]).start();
  }, []);
  // 切换展开状态
const toggleSection = useCallback((sectionId: string) => {const newExpanded = new Set(expandedSections)if (newExpanded.has(sectionId)) {}
      newExpanded.delete(sectionId)}
    } else {}
      newExpanded.add(sectionId)}
    }
    setExpandedSections(newExpanded);
  };
  // 分享诊断结果
const shareResult = async () => {try {const shareContent = `;`````;}}```;
}
🎯 置信度: ${Math.round(result.overallConfidence * 100)}%;
📊 数据质量: ${Math.round(result.qualityMetrics.dataQuality * 100)}%;
🔬 结果可靠性: ${Math.round(result.qualityMetrics.resultReliability * 100)}%;
📈 完整性: ${Math.round(result.qualityMetrics.completeness * 100)}%;
      `.trim();`````,```;
const await = Share.share({ ))const message = shareContent;);
 })}
      });
    } catch (error) {}
}
    }
  };
  // 保存报告
const saveReport = useCallback(() => {Alert.alert(;)}
}
'}
const style = 'default' ;}];
    );
  };
  // 预约咨询'
const bookConsultation = useCallback(() => {Alert.alert(;}        {';}}'}
style: 'cancel' ;},{'}
style: 'default',onPress: () => {// 这里应该导航到预约页面;'/;}}'/g'/;
}
          }
        }
      ];
    );
  };
  // 渲染标签栏'
const  renderTabBar = () => (<View style={styles.tabBar}>;)      {[;]';}        {'const key = "overview;
        {"const key = "details;
        {")""const key = "recommendations);
);
];
      ].map(tab => ()));
}
        <TouchableOpacity;}  />
key={tab.key};
style={[;]}
            styles.tabItem, activeTab === tab.key && styles.tabItemActive}
];
          ]}};
onPress={() => setActiveTab(tab.key as any)};
        >;
          <Text style={ />/;}[;];/g/;
}
            styles.tabText,activeTab === tab.key && styles.tabTextActive}
];
          ]}}>;
            {tab.title};
          </Text>;
        </TouchableOpacity>;
      ))};
    </View>;
  );
  // 渲染概览页面
const  renderOverview = () => (<View style={styles.tabContent}>;)      {// 主要诊断结果}
      <View style={styles.resultCard}>;
        <View style={styles.cardHeader}>;
          <Text style={styles.cardTitle}>诊断结果</Text>)
          <View style={ />/;}[;]);/g/;
}
            styles.confidenceBadge,)}
            { backgroundColor: getConfidenceColor(result.overallConfidence) }
];
          ]}>;
            <Text style={styles.confidenceText}>;
              {Math.round(result.overallConfidence * 100)}%;
            </Text>
          </View>
        </View>
        <View style={styles.syndromeContainer}>;
          <View style={ />/;}[;]/g"/;
}
            styles.syndromeIndicator,"};
];
            { backgroundColor: SYNDROME_COLORS[result.primarySyndrome.name] || '#6c757d' }
          ]} />
          <View style={styles.syndromeInfo}>;
            <Text style={styles.syndromeName}>;
              {result.primarySyndrome.name}
            </Text>
            <Text style={styles.syndromeDescription}>;
              {result.primarySyndrome.description}
            </Text>
          </View>
        </View>
      </View>
      {// 体质分析}
      <View style={styles.resultCard}>;
        <Text style={styles.cardTitle}>体质分析</Text>
        <View style={styles.constitutionContainer}>
          <Text style={styles.constitutionIcon}>'
            {CONSTITUTION_ICONS[result.constitutionType.type] || '🧬'}
          </Text>
          <View style={styles.constitutionInfo}>;
            <Text style={styles.constitutionType}>;
              {result.constitutionType.type}
            </Text>
            <View style={styles.characteristicsContainer}>;
              {result.constitutionType.characteristics.slice(0, 3).map(char, index) => ())}
                <View key={index} style={styles.characteristicTag}>;
                  <Text style={styles.characteristicText}>{char}</Text>
                </View>
              ))}
            </View>
          </View>
        </View>
      </View>
      {// 质量指标}
      <View style={styles.resultCard}>;
        <Text style={styles.cardTitle}>检测质量</Text>;
        <View style={styles.qualityMetrics}>;
          {[;];}            {}
}
      value: result.qualityMetrics.dataQuality ;},{}
}
      value: result.qualityMetrics.resultReliability ;},{}
}
      const value = result.qualityMetrics.completeness ;};
];
          ].map(metric, index) => (;));
            <View key={index} style={styles.metricItem}>;
              <Text style={styles.metricLabel}>{metric.label}</Text>;
              <View style={styles.metricBar}>;
                <View ;  />
style={[;]}
                    styles.metricFill,{width: `${metric.value * 100;}}%`,backgroundColor: getQualityColor(metric.value);````;```;
                    }
];
                  ]}
                />
              </View>
              <Text style={styles.metricValue}>;
                {Math.round(metric.value * 100)}%;
              </Text>
            </View>
          ))}
        </View>
      </View>
    </View>;
  );
  // 渲染详情页面
const renderDetails = () => (;);
    <View style={styles.tabContent}>;
      {// 五诊结果详情};
      {Object.entries(result.diagnosticResults).map([method, data]) => {if (!data) return null;)}
        const isExpanded = expandedSections.has(method)}
        return (<View key={method} style={styles.resultCard}>);
            <TouchableOpacity;)  />
style={styles.expandableHeader});
onPress={() => toggleSection(method)};
            >;
              <Text style={styles.cardTitle}>;
                {getMethodDisplayName(method)};
              </Text>;'/;'/g'/;
              <Text style={styles.expandIcon}>;
                {isExpanded ? '▼' : '▶'};
              </Text>;
            </TouchableOpacity>;
            {isExpanded && (;)}
              <View style={styles.expandableContent}>;
                {renderMethodDetails(method, data)};
              </View>;
            )};
          </View>;
        );
      })}
      {// 融合分析}
      <View style={styles.resultCard}>;
        <TouchableOpacity;'  />/,'/g'/;
style={styles.expandableHeader}
onPress={() => toggleSection('fusion')}
        >;
          <Text style={styles.cardTitle}>融合分析</Text>'/;'/g'/;
          <Text style={styles.expandIcon}>'
            {expandedSections.has('fusion') ? '▼' : '▶'}
          </Text>'/;'/g'/;
        </TouchableOpacity>'/;'/g'/;
        {expandedSections.has('fusion')  && <View style={styles.expandableContent}>
            <Text style={styles.sectionSubtitle}>证据强度</Text>
            {Object.entries(result.fusionAnalysis.evidenceStrength).map([method, strength]) => ())}
              <View key={method} style={styles.evidenceItem}>;
                <Text style={styles.evidenceMethod}>;
                  {getMethodDisplayName(method)}
                </Text>
                <View style={styles.evidenceBar}>;
                  <View;  />
style={}[;]}
                      styles.evidenceFill,}
                      { width: `${strength * 100;}}%` }````;```;
];
                    ]}
                  />
                </View>
                <Text style={styles.evidenceValue}>;
                  {Math.round(strength * 100)}%;
                </Text>
              </View>
            ))}
            {result.fusionAnalysis.riskFactors.length > 0  && <>}
                <Text style={styles.sectionSubtitle}>风险因素</Text>
                {result.fusionAnalysis.riskFactors.map(factor, index) => ())}
                  <View key={index} style={styles.riskFactorItem}>;
                    <Text style={styles.riskFactorText}>⚠️ {factor}</Text>
                  </View>
                ))}
              < />
            )}
          </View>
        )}
      </View>
    </View>
  );
  // 渲染建议页面
const renderRecommendations = () => (;);
    <View style={styles.tabContent}>;
      {Object.entries(result.healthRecommendations).map([category, recommendations]) => {if (!recommendations || recommendations.length === 0) return null;)}
        return (;)}
          <View key={category} style={styles.resultCard}>;
            <Text style={styles.cardTitle}>;
              {getRecommendationCategoryName(category)};
            </Text>;
            {recommendations.map(recommendation, index) => (;))}
              <View key={index} style={styles.recommendationItem}>;
                <Text style={styles.recommendationIcon}>;
                  {getRecommendationIcon(category)};
                </Text>;
                <Text style={styles.recommendationText}>;
                  {recommendation};
                </Text>;
              </View>;
            ))};
          </View>;
        );
      })}
    </View>
  );
  // 渲染方法详情/,/g,/;
  renderMethodDetails: useCallback((method: string, data: any) => {// 这里应该根据不同的诊断方法渲染不同的详情;/;}    // 暂时使用通用格式;
return (;);
      <View>;
}
        {data.confidence && (;)}
          <View style={styles.detailItem}>;
            <Text style={styles.detailLabel}>置信度</Text>;
            <Text style={styles.detailValue}>;
              {Math.round(data.confidence * 100)}%;
            </Text>;
          </View>;
        )};
        {data.overallAssessment && (;)}
          <View style={styles.detailItem}>;
            <Text style={styles.detailLabel}>总体评估</Text>;
            <Text style={styles.detailValue}>{data.overallAssessment}</Text>;
          </View>;
        )};
        {data.analysisId && (;)}
          <View style={styles.detailItem}>;
            <Text style={styles.detailLabel}>分析ID</Text>;
            <Text style={styles.detailValue}>{data.analysisId}</Text>;
          </View>;
        )};
      </View>;
    );
  };
  // 辅助函数'/,'/g'/;
const getConfidenceColor = (confidence: number): string => {if (confidence >= 0.8) return '#28a745if (confidence >= 0.6) return '#ffc107';
}
    return '#dc3545}
  };
const getQualityColor = (quality: number): string => {if (quality >= 0.8) return '#28a745if (quality >= 0.6) return '#ffc107';
}
    return '#dc3545}
  };
const: getMethodDisplayName = (method: string): string => {const names: Record<string, string> = {}
}
    ;};
return names[method] || method;
  };
const: getRecommendationCategoryName = (category: string): string => {const names: Record<string, string> = {}
}
    ;};
return names[category] || category;
  };
const: getRecommendationIcon = (category: string): string => {const icons: Record<string, string> = {'lifestyle: "🏠,
}
      diet: '🍎',exercise: '🏃',treatment: '💊',prevention: '🛡️}
    };
return icons[category] || '📝';
  };
return (<SafeAreaView style={styles.container}>;)      {// 头部}
      <View style={styles.header}>);
        <TouchableOpacity;)  />
style={styles.backButton});
onPress={() => navigation.goBack()}
        >;
          <Text style={styles.backButtonText}>←</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>诊断报告</Text>
        <TouchableOpacity;  />
style={styles.shareButton}
          onPress={shareResult}
        >;
          <Text style={styles.shareButtonText}>分享</Text>
        </TouchableOpacity>
      </View>
      {// 标签栏}
      {renderTabBar()}
      {// 内容区域}
      <Animated.View;  />
style={[]styles.content,}          {}
            opacity: fadeAnimation,}
];
const transform = [{ translateY: slideAnimation ;}}];
          }
        ]}
      >;
        <ScrollView;  />
style={styles.scrollView}
          showsVerticalScrollIndicator={false}
          contentContainerStyle={styles.scrollContent}
        >'
          {activeTab === 'overview' && renderOverview()}
          {activeTab === 'details' && renderDetails()}
          {activeTab === 'recommendations' && renderRecommendations()}
        </ScrollView>
      </Animated.View>
      {// 底部操作栏}
      <View style={styles.bottomActions}>;
        <TouchableOpacity ;  />
style={styles.actionButton};
onPress={saveReport};
        >;
          <Text style={styles.actionButtonText}>保存报告</Text>;
        </TouchableOpacity>;
        <TouchableOpacity ;  />
style={[styles.actionButton, styles.primaryActionButton]};
onPress={bookConsultation};
        >;
          <Text style={[styles.actionButtonText, styles.primaryActionButtonText]}>;
          </Text>;
        </TouchableOpacity>;
      </View>;
    </SafeAreaView>;
  );
}
const  styles = StyleSheet.create({)container: {,'flex: 1,
}
    const backgroundColor = '#f8f9fa'}
  ;},'
header: {,'flexDirection: 'row,'
alignItems: 'center,'
justifyContent: 'space-between,'';
paddingHorizontal: 20,
paddingVertical: 15,'
backgroundColor: '#ffffff,'';
borderBottomWidth: 1,
}
    const borderBottomColor = '#e9ecef'}
  }
backButton: {,}
  const padding = 8}
  }
backButtonText: {,'fontSize: 24,
}
    const color = '#007AFF'}
  }
headerTitle: {,'fontSize: 18,'
fontWeight: '600,'
}
    const color = '#1a1a1a'}
  }
shareButton: {,}
  const padding = 8}
  }
shareButtonText: {,'fontSize: 16,
}
    const color = '#007AFF'}
  ;},'
tabBar: {,'flexDirection: 'row,'
backgroundColor: '#ffffff,'';
borderBottomWidth: 1,
}
    const borderBottomColor = '#e9ecef'}
  }
tabItem: {flex: 1,
paddingVertical: 15,
}
    const alignItems = 'center'}
  }
tabItemActive: {,'borderBottomWidth: 2,
}
    const borderBottomColor = '#007AFF'}
  }
tabText: {,'fontSize: 16,
}
    const color = '#6c757d'}
  ;},'
tabTextActive: {,'color: '#007AFF,'
}
    const fontWeight = '600'}
  }
content: {,}
  const flex = 1}
  }
scrollView: {,}
  const flex = 1}
  }
scrollContent: {,}
  const padding = 20}
  }
const tabContent = {}
    // 内容样式}
  ;},'
resultCard: {,'backgroundColor: '#ffffff,'';
borderRadius: 12,
padding: 20,
marginBottom: 15,'
shadowColor: '#000,'';
shadowOffset: {width: 0,
}
      const height = 2}
    }
shadowOpacity: 0.1,
shadowRadius: 4,
const elevation = 3;
  },'
cardHeader: {,'flexDirection: 'row,'
justifyContent: 'space-between,'
alignItems: 'center,'
}
    const marginBottom = 15}
  }
cardTitle: {,'fontSize: 18,'
fontWeight: '600,'
}
    const color = '#1a1a1a'}
  }
confidenceBadge: {paddingHorizontal: 12,
paddingVertical: 6,
}
    const borderRadius = 20}
  }
confidenceText: {,'fontSize: 14,'
fontWeight: '600,'
}
    const color = '#ffffff'}
  ;},'
syndromeContainer: {,'flexDirection: 'row,'
}
    const alignItems = 'center'}
  }
syndromeIndicator: {width: 8,
height: 60,
borderRadius: 4,
}
    const marginRight = 15}
  }
syndromeInfo: {,}
  const flex = 1}
  }
syndromeName: {,'fontSize: 20,'
fontWeight: '700,'
color: '#1a1a1a,'
}
    const marginBottom = 5}
  }
syndromeDescription: {,'fontSize: 16,'
color: '#6c757d,'
}
    const lineHeight = 24}
  },'
constitutionContainer: {,'flexDirection: 'row,'
}
    const alignItems = 'center'}
  }
constitutionIcon: {fontSize: 40,
}
    const marginRight = 15}
  }
constitutionInfo: {,}
  const flex = 1}
  }
constitutionType: {,'fontSize: 18,'
fontWeight: '600,'
color: '#1a1a1a,'
}
    const marginBottom = 10}
  },'
characteristicsContainer: {,'flexDirection: 'row,'
}
    const flexWrap = 'wrap'}
  ;},'
characteristicTag: {,'backgroundColor: '#e9ecef,'';
paddingHorizontal: 8,
paddingVertical: 4,
borderRadius: 12,
marginRight: 8,
}
    const marginBottom = 4}
  }
characteristicText: {,'fontSize: 12,
}
    const color = '#6c757d'}
  }
const qualityMetrics = {}
    // 质量指标样式}
  ;},'
metricItem: {,'flexDirection: 'row,'
alignItems: 'center,'
}
    const marginBottom = 12}
  }
metricLabel: {,'fontSize: 14,'
color: '#6c757d,'
}
    const width = 80}
  }
metricBar: {flex: 1,
height: 8,'
backgroundColor: '#e9ecef,'';
borderRadius: 4,
marginHorizontal: 12,
}
    const overflow = 'hidden'}
  ;},'
metricFill: {,'height: '100%,'
}
    const borderRadius = 4}
  }
metricValue: {,'fontSize: 14,'
fontWeight: '600,'
color: '#1a1a1a,'';
width: 40,
}
    const textAlign = 'right'}
  ;},'
expandableHeader: {,'flexDirection: 'row,'
justifyContent: 'space-between,'
}
    const alignItems = 'center'}
  }
expandIcon: {,'fontSize: 16,
}
    const color = '#6c757d'}
  }
expandableContent: {marginTop: 15,
paddingTop: 15,
borderTopWidth: 1,
}
    const borderTopColor = '#e9ecef'}
  }
sectionSubtitle: {,'fontSize: 16,'
fontWeight: '600,'
color: '#1a1a1a,'';
marginBottom: 10,
}
    const marginTop = 15}
  },'
detailItem: {,'flexDirection: 'row,'
justifyContent: 'space-between,'
alignItems: 'center,'
}
    const paddingVertical = 8}
  }
detailLabel: {,'fontSize: 14,
}
    const color = '#6c757d'}
  }
detailValue: {,'fontSize: 14,'
color: '#1a1a1a,'
}
    const fontWeight = '500'}
  ;},'
evidenceItem: {,'flexDirection: 'row,'
alignItems: 'center,'
}
    const marginBottom = 8}
  }
evidenceMethod: {,'fontSize: 14,'
color: '#6c757d,'
}
    const width = 60}
  }
evidenceBar: {flex: 1,
height: 6,'
backgroundColor: '#e9ecef,'';
borderRadius: 3,
marginHorizontal: 12,
}
    const overflow = 'hidden'}
  ;},'
evidenceFill: {,'height: '100%,'
backgroundColor: '#007AFF,'
}
    const borderRadius = 3}
  }
evidenceValue: {,'fontSize: 12,'
color: '#1a1a1a,'';
width: 35,
}
    const textAlign = 'right'}
  }
riskFactorItem: {,}
  const marginBottom = 8}
  }
riskFactorText: {,'fontSize: 14,
}
    const color = '#dc3545'}
  ;},'
recommendationItem: {,'flexDirection: 'row,'
alignItems: 'flex-start,'
}
    const marginBottom = 12}
  }
recommendationIcon: {fontSize: 16,
marginRight: 10,
}
    const marginTop = 2}
  }
recommendationText: {flex: 1,
fontSize: 14,'
color: '#1a1a1a,'
}
    const lineHeight = 20}
  },'
bottomActions: {,'flexDirection: 'row,'';
paddingHorizontal: 20,
paddingVertical: 15,'
backgroundColor: '#ffffff,'';
borderTopWidth: 1,
}
    const borderTopColor = '#e9ecef'}
  }
actionButton: {flex: 1,
paddingVertical: 12,
borderRadius: 8,
borderWidth: 1,'
borderColor: '#6c757d,'
}
    alignItems: 'center',marginRight: 10;'}
  },primaryActionButton: {,'backgroundColor: "#007AFF,
}
      borderColor: '#007AFF',marginRight: 0;'}
  },actionButtonText: {fontSize: 16,color: '#6c757d',fontWeight: '500)}
  },primaryActionButtonText: {color: '#ffffff)}
  };);
});
);