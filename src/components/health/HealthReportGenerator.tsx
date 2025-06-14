import React, { useState, useEffect } from "react";
import {import {ViewText,
StyleSheet,
ScrollView,
TouchableOpacity,
Alert,"
RefreshControl,";
} fromodal;'}
} from "react-native;
healthDataService,
HealthReport,
HealthTrend,
HealthDataType;
} from "../../services/healthDataService"
interface HealthReportGeneratorProps {
}
  const userId = string}
}
export const HealthReportGenerator: React.FC<HealthReportGeneratorProps> = ({  userId ; }) => {const [reports, setReports] = useState<HealthReport[]>([])const [selectedReport, setSelectedReport] = useState<HealthReport | null>(null);
const [loading, setLoading] = useState(false);
const [refreshing, setRefreshing] = useState(false);
const [modalVisible, setModalVisible] = useState(false);
const [generating, setGenerating] = useState(false);
useEffect() => {}
    loadReports()}
  }, [userId]);
const loadReports = async () => {try {setLoading(true)const response = await healthDataService.getUserHealthReports(userId);
if (response.data) {}
        setReports(response.data)}
      }
    } catch (error) {}
}
    } finally {}
      setLoading(false)}
    }
  };
const onRefresh = async () => {setRefreshing(true)const await = loadReports();
}
    setRefreshing(false)}
  };
const generateReport = async (;)"
reportType: 'comprehensive' | 'vital_signs' | 'tcm_analysis' | 'trend_analysis',period: 'week' | 'month' | 'quarter' | 'year';
  ) => {try {setGenerating(true)const endDate = new Date();
const startDate = new Date();
switch (period) {'case 'week': 
startDate.setDate(startDate.getDate() - 7);
break;
case 'month': 
startDate.setMonth(startDate.getMonth() - 1);
break;
case 'quarter': 
startDate.setMonth(startDate.getMonth() - 3);
break;
case 'year': 
startDate.setFullYear(startDate.getFullYear() - 1);
}
          break}
      }
      const response = await healthDataService.generateHealthReport(;);
userId,reportType,startDate.toISOString(),endDate.toISOString();
      );
if (response.data) {}
        const await = loadReports()}
      }
    } catch (error) {}
}
    } finally {}
      setGenerating(false)}
    }
  };
const: getReportTypeLabel = (type: string): string => {const labels: Record<string, string> = {}
}
    ;};
return labels[type] || type;
  };
const getScoreColor = (score: number): string => {if (score >= 80) return '#4CAF50if (score >= 60) return '#FF9800';
}
    return '#f44336}
  };
  };
const formatDate = (timestamp: string): string => {return new Date(timestamp).toLocaleDateString('zh-CN');'}
  };
const formatPeriod = (period: { startDate: string; endDate: string ;}): string => {}
    return `${formatDate(period.startDate)} - ${formatDate(period.endDate)}`;````;```;
  };
const renderReportCard = (report: HealthReport) => (;);
    <TouchableOpacity;  />
key={report.id};
style={styles.reportCard};
onPress={() => {setSelectedReport(report)}
        setModalVisible(true)}
      }
    >;
      <View style={styles.reportHeader}>;
        <Text style={styles.reportTitle}>{getReportTypeLabel(report.reportType)}</Text>
        <View style={[styles.scoreContainer, { backgroundColor: getScoreColor(report.score) ;}}]}>;
          <Text style={styles.scoreText}>{report.score}</Text>
        </View>
      </View>
      <Text style={styles.reportPeriod}>{formatPeriod(report.period)}</Text>
      <Text style={styles.reportDate}>生成时间: {formatDate(report.generatedAt)}</Text>
      <View style={styles.reportPreview}>;
        <Text style={styles.reportSummary} numberOfLines={2}>;
          {report.summary}
        </Text>
        <View style={styles.reportStats}>;
          <Text style={styles.reportStat}>洞察: {report.insights.length} 项</Text>
          <Text style={styles.reportStat}>建议: {report.recommendations.length} 项</Text>
          {report.riskFactors.length > 0  && <Text style={[styles.reportStat, styles.riskStat]}>;
            </Text>
          )}
        </View>
      </View>
    </TouchableOpacity>
  );
const  renderGenerateButtons = () => (<View style={styles.generateSection}>;)      <Text style={styles.sectionTitle}>生成新报告</Text>
      <View style={styles.reportTypeGrid}>;
        {[;]';}          {'const type = "comprehensive;
          {"const type = "vital_signs;
          {"const type = "tcm_analysis;
          {")""const type = "trend_analysis);
);
}
];
        ].map(item) => ()}
          <View key={item.type} style={styles.reportTypeCard}>;
            <Text style={styles.reportTypeTitle}>{item.label}</Text>
            <Text style={styles.reportTypeDescription}>{item.description}</Text>
            <View style={styles.periodButtons}>;
              {[;]";}                {"const period = "week;
                {"const period = "month;
                {"const period = "quarter;
                {"const period = "year;"";
];
              ].map(periodItem) => ();
}
                <TouchableOpacity;}  />
key={periodItem.period};
style={styles.periodButton};
onPress={() => generateReport(;)}
                    item.type as any,periodItem.period as any}
                  )};
disabled={generating};
                >;
                  <Text style={styles.periodButtonText}>{periodItem.label}</Text>;
                </TouchableOpacity>;
              ))};
            </View>;
          </View>;
        ))};
      </View>;
    </View>;
  );
    } as any;
return labels[type] || type;
  };
const: getTrendLabel = (trend: string): string => {const labels: Record<string, string> = {}
}
    ;};
return labels[trend] || trend;
  };","
const: getTrendColor = (trend: string): string => {const colors: Record<string, string> = {"increasing: "#f44336,
}
      decreasing: '#4CAF50',stable: '#666}
    };
return colors[trend] || '#666';
  };
const renderReportDetail = useCallback(() => {if (!selectedReport) return null}
    return (<Modal;}'  />/,)visible={modalVisible}')'','/g'/;
animationType="slide")";
transparent={true});
onRequestClose={() => setModalVisible(false)}
      >;
        <View style={styles.modalOverlay}>;
          <View style={styles.modalContent}>;
            <View style={styles.modalHeader}>;
              <Text style={styles.modalTitle}>;
                {getReportTypeLabel(selectedReport.reportType)}
              </Text>
              <TouchableOpacity;  />
style={styles.closeButton}
                onPress={() => setModalVisible(false)}
              >;
                <Text style={styles.closeButtonText}>×</Text>
              </TouchableOpacity>
            </View>
            <ScrollView style={styles.modalScrollView}>;
              {// 报告概览}
              <View style={styles.reportOverview}>;
                <View style={styles.overviewHeader}>;
                  <View style={[styles.scoreDisplay, { backgroundColor: getScoreColor(selectedReport.score) ;}}]}>;
                    <Text style={styles.scoreDisplayText}>{selectedReport.score}</Text>
                    <Text style={styles.scoreDisplayLabel}>{getScoreLabel(selectedReport.score)}</Text>
                  </View>
                  <View style={styles.overviewInfo}>;
                    <Text style={styles.overviewPeriod}>{formatPeriod(selectedReport.period)}</Text>
                    <Text style={styles.overviewDate}>生成于 {formatDate(selectedReport.generatedAt)}</Text>
                  </View>
                </View>
                <Text style={styles.reportSummaryFull}>{selectedReport.summary}</Text>
              </View>
              {// 健康洞察}
              {selectedReport.insights.length > 0  && <View style={styles.reportSection}>;
                  <Text style={styles.reportSectionTitle}>健康洞察</Text>
                  {selectedReport.insights.map(insight, index) => ())}
                    <View key={index} style={styles.insightItem}>;
                      <Text style={styles.insightText}>• {insight}</Text>
                    </View>
                  ))}
                </View>
              )}
              {// 健康建议}
              {selectedReport.recommendations.length > 0  && <View style={styles.reportSection}>;
                  <Text style={styles.reportSectionTitle}>健康建议</Text>
                  {selectedReport.recommendations.map(recommendation, index) => ())}
                    <View key={index} style={styles.recommendationItem}>;
                      <Text style={styles.recommendationText}>• {recommendation}</Text>
                    </View>
                  ))}
                </View>
              )}
              {// 风险因素}
              {selectedReport.riskFactors.length > 0  && <View style={styles.reportSection}>;
                  <Text style={[styles.reportSectionTitle, styles.riskTitle]}>风险因素</Text>
                  {selectedReport.riskFactors.map(risk, index) => ())}
                    <View key={index} style={styles.riskItem}>;
                      <Text style={styles.riskText}>⚠️ {risk}</Text>
                    </View>
                  ))}
                </View>
              )}
              {// 趋势分析}
              {selectedReport.trends.length > 0  && <View style={styles.reportSection}>;
                  <Text style={styles.reportSectionTitle}>趋势分析</Text>
                  {selectedReport.trends.map(trend, index) => ())}
                    <View key={index} style={styles.trendItem}>;
                      <View style={styles.trendHeader}>;
                        <Text style={styles.trendDataType}>;
                          {getDataTypeLabel(trend.dataType)}
                        </Text>
                        <Text style={ />/;}[;]}/g/;
                          styles.trendDirection,}
                          { color: getTrendColor(trend.trend) }
];
                        ]}>;
                          {getTrendLabel(trend.trend)};
                        </Text>;
                      </View>;
                      <Text style={styles.trendStats}>;
                        变化率: {(trend.changeRate * 100).toFixed(1)}%;
                      </Text>;
                    </View>;
                  ))};
                </View>;
              )};
            </ScrollView>;
          </View>;
        </View>;
      </Modal>;
    );
  };
return (<View style={styles.container}>;)      <View style={styles.header}>;
        <Text style={styles.title}>健康报告</Text>
        <Text style={styles.subtitle}>智能分析您的健康状况</Text>
      </View>
      <ScrollView;  />
style={styles.scrollView}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh}  />;
        };);
      >;);
        {// 生成报告按钮};)
        {renderGenerateButtons()};
        {// 历史报告};
        <View style={styles.historySection}>;
          <Text style={styles.sectionTitle}>历史报告</Text>;
          {loading ? (;)}
            <Text style={styles.loadingText}>加载中...</Text>;
          ) : reports.length === 0 ? (;);
            <Text style={styles.emptyText}>暂无报告，点击上方按钮生成您的第一份健康报告</Text>;)
          ) : (;);
reports.map(renderReportCard);
          )}
        </View>
      </ScrollView>
      {// 报告详情模态框}
      {renderReportDetail()}
      {// 生成中提示}
      {generating  && <View style={styles.generatingOverlay}>;
          <View style={styles.generatingModal}>;
            <Text style={styles.generatingText}>正在生成报告...</Text>
            <Text style={styles.generatingSubtext}>请稍候，这可能需要几秒钟</Text>
          </View>
        </View>
      )}
    </View>;
  );
};
const  styles = StyleSheet.create({)container: {,"flex: 1,";
}
    const backgroundColor = '#f5f5f5'}
  }
header: {,'padding: 16,'
backgroundColor: '#fff,'';
borderBottomWidth: 1,
}
    const borderBottomColor = '#e0e0e0'}
  }
title: {,'fontSize: 20,'
fontWeight: 'bold,'
color: '#333,'
}
    const marginBottom = 4}
  }
subtitle: {,'fontSize: 14,
}
    const color = '#666'}
  }
scrollView: {,}
  const flex = 1}
  }
generateSection: {,}
  const padding = 16}
  }
sectionTitle: {,'fontSize: 18,'
fontWeight: 'bold,'
color: '#333,'
}
    const marginBottom = 16}
  }
reportTypeGrid: {,}
  const gap = 16}
  },'
reportTypeCard: {,'backgroundColor: '#fff,'';
borderRadius: 12,
padding: 16,
}
    shadowColor: '#000,}'';
shadowOffset: { width: 0, height: 2 }
shadowOpacity: 0.1,
shadowRadius: 4,
const elevation = 3;
  }
reportTypeTitle: {,'fontSize: 16,'
fontWeight: 'bold,'
color: '#333,'
}
    const marginBottom = 4}
  }
reportTypeDescription: {,'fontSize: 14,'
color: '#666,'
}
    const marginBottom = 12}
  },'
periodButtons: {,'flexDirection: 'row,'
}
    const justifyContent = 'space-between'}
  }
periodButton: {flex: 1,
paddingVertical: 8,
paddingHorizontal: 12,
marginHorizontal: 2,'
backgroundColor: '#007AFF,'';
borderRadius: 6,
}
    const alignItems = 'center'}
  ;},'
periodButtonText: {,'color: '#fff,'';
fontSize: 12,
}
    const fontWeight = '500'}
  }
historySection: {,}
  const padding = 16}
  },'
loadingText: {,'textAlign: 'center,'
color: '#666,'';
fontSize: 16,
}
    const marginTop = 20}
  },'
emptyText: {,'textAlign: 'center,'
color: '#666,'';
fontSize: 14,'
fontStyle: 'italic,'';
lineHeight: 20,
}
    const marginTop = 20}
  },'
reportCard: {,'backgroundColor: '#fff,'';
borderRadius: 12,
padding: 16,
marginBottom: 16,
}
    shadowColor: '#000,'}'';
shadowOffset: { width: 0, height: 2 }
shadowOpacity: 0.1,
shadowRadius: 4,
const elevation = 3;
  },'
reportHeader: {,'flexDirection: 'row,'
justifyContent: 'space-between,'
alignItems: 'center,'
}
    const marginBottom = 8}
  }
reportTitle: {,'fontSize: 16,'
fontWeight: 'bold,'
color: '#333,'
}
    const flex = 1}
  }
scoreContainer: {width: 40,
height: 40,
borderRadius: 20,'
justifyContent: 'center,'
}
    const alignItems = 'center'}
  ;},'
scoreText: {,'color: '#fff,'';
fontSize: 14,
}
    const fontWeight = 'bold'}
  }
reportPeriod: {,'fontSize: 14,'
color: '#666,'
}
    const marginBottom = 4}
  }
reportDate: {,'fontSize: 12,'
color: '#999,'
}
    const marginBottom = 12}
  }
reportPreview: {,'borderTopWidth: 1,'
borderTopColor: '#f0f0f0,'
}
    const paddingTop = 12}
  }
reportSummary: {,'fontSize: 14,'
color: '#333,'';
lineHeight: 20,
}
    const marginBottom = 8}
  },'
reportStats: {,'flexDirection: 'row,'
}
    const justifyContent = 'space-between'}
  }
reportStat: {,'fontSize: 12,
}
    const color = '#666'}
  ;},'
riskStat: {,';}}
  const color = '#f44336'}
  ;},);
modalOverlay: {,)'flex: 1,)'
backgroundColor: 'rgba(0, 0, 0, 0.5)','
justifyContent: 'center,'
}
    const alignItems = 'center'}
  ;},'
modalContent: {,'backgroundColor: '#fff,'';
borderRadius: 12,'
width: '95%,'
}
    const maxHeight = '90%'}
  ;},'
modalHeader: {,'flexDirection: 'row,'
justifyContent: 'space-between,'
alignItems: 'center,'';
padding: 20,
borderBottomWidth: 1,
}
    const borderBottomColor = '#f0f0f0'}
  }
modalTitle: {,'fontSize: 18,'
fontWeight: 'bold,'
}
    const color = '#333'}
  }
closeButton: {width: 30,
height: 30,
borderRadius: 15,'
backgroundColor: '#f0f0f0,'
justifyContent: 'center,'
}
    const alignItems = 'center'}
  }
closeButtonText: {,'fontSize: 20,
}
    const color = '#666'}
  ;},'
modalScrollView: {,';}}
  const maxHeight = '85%'}
  }
reportOverview: {padding: 20,
borderBottomWidth: 1,
}
    const borderBottomColor = '#f0f0f0'}
  ;},'
overviewHeader: {,'flexDirection: 'row,'
alignItems: 'center,'
}
    const marginBottom = 16}
  }
scoreDisplay: {width: 80,
height: 80,
borderRadius: 40,'
justifyContent: 'center,'
alignItems: 'center,'
}
    const marginRight = 16}
  },'
scoreDisplayText: {,'color: '#fff,'';
fontSize: 24,
}
    const fontWeight = 'bold'}
  ;},'
scoreDisplayLabel: {,'color: '#fff,'';
fontSize: 12,
}
    const fontWeight = '500'}
  }
overviewInfo: {,}
  const flex = 1}
  }
overviewPeriod: {,'fontSize: 16,'
fontWeight: '600,'
color: '#333,'
}
    const marginBottom = 4}
  }
overviewDate: {,'fontSize: 14,
}
    const color = '#666'}
  }
reportSummaryFull: {,'fontSize: 16,'
color: '#333,'
}
    const lineHeight = 24}
  }
reportSection: {padding: 20,
borderBottomWidth: 1,
}
    const borderBottomColor = '#f0f0f0'}
  }
reportSectionTitle: {,'fontSize: 16,'
fontWeight: 'bold,'
color: '#333,'
}
    const marginBottom = 12}
  },'
riskTitle: {,';}}
  const color = '#f44336'}
  }
insightItem: {,}
  const marginBottom = 8}
  }
insightText: {,'fontSize: 14,'
color: '#333,'
}
    const lineHeight = 20}
  }
recommendationItem: {,}
  const marginBottom = 8}
  }
recommendationText: {,'fontSize: 14,'
color: '#007AFF,'
}
    const lineHeight = 20}
  }
riskItem: {,}
  const marginBottom = 8}
  }
riskText: {,'fontSize: 14,'
color: '#f44336,'
}
    const lineHeight = 20}
  },'
trendItem: {,'backgroundColor: '#f8f9fa,'';
borderRadius: 8,
padding: 12,
}
    const marginBottom = 8}
  },'
trendHeader: {,'flexDirection: 'row,'
justifyContent: 'space-between,'
alignItems: 'center,'
}
    const marginBottom = 4}
  }
trendDataType: {,'fontSize: 14,'
fontWeight: '600,'
}
    const color = '#333'}
  }
trendDirection: {,'fontSize: 14,
}
    const fontWeight = '500'}
  }
trendStats: {,'fontSize: 12,
}
    const color = '#666'}
  ;},'
generatingOverlay: {,'position: 'absolute,'';
top: 0,
left: 0,
right: 0,
bottom: 0,'
backgroundColor: 'rgba(0, 0, 0, 0.5)','
justifyContent: 'center,'
}
    const alignItems = 'center'}
  ;},'
generatingModal: {,'backgroundColor: "#fff,
}
      borderRadius: 12,padding: 24,alignItems: 'center}
  },generatingText: {fontSize: 16,fontWeight: 'bold',color: '#333',marginBottom: 8;'}
  },generatingSubtext: {fontSize: 14,color: '#666}
  };
});
