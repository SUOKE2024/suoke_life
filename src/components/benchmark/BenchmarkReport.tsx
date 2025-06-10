import React, { useState } from "react";";
import {import {import { useSelector, useDispatch } from "react-redux";";
import {import type { AppDispatch } from "../../store";""/;,"/g"/;
import type { BenchmarkResult } from "../../services";""/;,"/g"/;
View,;
Text,;
StyleSheet,;
ScrollView,;
Alert,;
Linking,";,"";
Share;';'';
} from "react-native";";
Card,;
Button,;
Chip,;
DataTable,;
ProgressBar,;
Divider,';,'';
IconButton;';'';
} from "react-native-paper";";
selectCurrentResult,;
selectBenchmarkLoading,';,'';
generateReport;';'';
} from "../../store/slices/benchmarkSlice";""/;,"/g"/;
interface BenchmarkReportProps {const taskId = string;}}
}
  onClose?: () => void;}
}
export const BenchmarkReport: React.FC<BenchmarkReportProps> = ({));,}taskId,);
}
  onClose;)}
}) => {const dispatch = useDispatch<AppDispatch>();,}const result = useSelector(selectCurrentResult);
const loading = useSelector(selectBenchmarkLoading);
const [reportUrls, setReportUrls] = useState<{html?: string;}}
    json?: string;}
  }>({});
const [generatingReport, setGeneratingReport] = useState<{html: boolean,;}}
  const json = boolean;}
  }>({ html: false, json: false ;});';'';
  // 生成报告'/;,'/g,'/;
  handleGenerateReport: async (format: 'html' | 'json') => {try {setGeneratingReport(prev => ({ ...prev, [format]: true ;}));';,'';
response: await dispatch(generateReport({taskId,format ;))}
      })).unwrap();
setReportUrls(prev => ({));}        ...prev,);
}
        [format]: response.reportUrl;)}
      }));

        [;]{}}
      onPress: () => openReport(response.reportUrl);}
          }
];
        ];
      );
    } catch (error) {}}
}
    } finally {}
      setGeneratingReport(prev => ({ ...prev, [format]: false }));
    }
  };
  // 打开报告/;,/g/;
const openReport = async (url: string) => {try {const supported = await Linking.canOpenURL(url);,}if (supported) {}}
        const await = Linking.openURL(url);}
      } else {}}
}
      }
    } catch (error) {}}
}
    }
  };
  // 分享报告/;/g/;

      });
    } catch (error) {}}
}
    }
  };
  // 格式化时间/;,/g/;
const formatDuration = useCallback((seconds: number) => {const hours = Math.floor(seconds / 3600);/;,}const minutes = Math.floor(seconds % 3600) / 60);/;,/g/;
const secs = Math.floor(seconds % 60);
}
    if (hours > 0) {}
      return `${hours}h ${minutes}m ${secs}s`;````;```;
    } else if (minutes > 0) {}
      return `${minutes}m ${secs}s`;````;```;
    } else {}
      return `${secs}s`;````;```;
    }
  };
if (!result) {}}
    return (;)}
      <View style={styles.container}>;
        <Card style={styles.card}>;
          <Card.Content>;
            <Text style={styles.noDataText}>暂无报告数据</Text>;/;/g/;
          </Card.Content>;/;/g/;
        </Card>;/;/g/;
      </View>;/;/g/;
    );
  }
  // 计算平均分数/;,/g/;
const metricsValues = result.metrics ? Object.values(result.metrics) : [];
const averageScore = metricsValues.length > 0 ;
    ? metricsValues.reduce(sum, val) => sum + val, 0) / metricsValues.length ;/;/g/;
    : 0;
return (<ScrollView style={styles.container}>;)      {// 报告头部}/;/g/;
      <Card style={styles.card}>;
        <Card.Title;)  />/;/g/;
)';'';
)';,'';
right={() => onClose  && <IconButton icon="close" onPress={onClose}  />"/;"/g"/;
          )}
        />/;/g/;
        <Card.Content>;
          <View style={styles.headerInfo}>;
            <View style={styles.statusRow}>";"";
              <Chip;"  />/;,"/g"/;
style={[styles.statusChip, { backgroundColor: '#4CAF50' ;}}]}';,'';
textStyle={ color: 'white' ;}}';'';
              >;

              </Chip>/;/g/;
              <Text style={styles.timestampText}>;
                {new Date(result.timestamp).toLocaleString()}
              </Text>/;/g/;
            </View>/;/g/;
            <View style={styles.durationRow}>;
              <Text style={styles.durationLabel}>执行时长: </Text>/;/g/;
              <Text style={styles.durationValue}>;
                {formatDuration(result.execution_time)}
              </Text>/;/g/;
            </View>/;/g/;
          </View>/;/g/;
        </Card.Content>/;/g/;
      </Card>/;/g/;
      {// 基本信息}'/;'/g'/;
      <Card style={styles.card}>';'';
        <Card.Title title="基本信息"  />"/;"/g"/;
        <Card.Content>;
          <DataTable>;
            <DataTable.Row>;
              <DataTable.Cell>基准测试ID</DataTable.Cell>/;/g/;
              <DataTable.Cell>{result.benchmark_id}</DataTable.Cell>/;/g/;
            </DataTable.Row>/;/g/;
            <DataTable.Row>;
              <DataTable.Cell>模型ID</DataTable.Cell>/;/g/;
              <DataTable.Cell>{result.model_id}</DataTable.Cell>/;/g/;
            </DataTable.Row>/;/g/;
            <DataTable.Row>;
              <DataTable.Cell>模型版本</DataTable.Cell>/;/g/;
              <DataTable.Cell>{result.model_version}</DataTable.Cell>/;/g/;
            </DataTable.Row>/;/g/;
            <DataTable.Row>;
              <DataTable.Cell>执行时间</DataTable.Cell>/;/g/;
              <DataTable.Cell>{formatDuration(result.execution_time)}</DataTable.Cell>/;/g/;
            </DataTable.Row>/;/g/;
          </DataTable>/;/g/;
        </Card.Content>/;/g/;
      </Card>/;/g/;
      {// 性能指标}"/;"/g"/;
      {result.metrics && Object.keys(result.metrics).length > 0  && <Card style={styles.card}>";"";
          <Card.Title title="性能指标"  />"/;"/g"/;
          <Card.Content>;
            <View style={styles.scoreContainer}>";"";
              <View style={styles.scoreCircle}>";"";
                <Text style={[styles.scoreText, { color: '#4CAF50' ;}}]}>';'';
                  {averageScore.toFixed(1)}
                </Text>/;/g/;
                <Text style={styles.scoreLabel}>平均分</Text>/;/g/;
              </View>/;/g/;
            </View>/;/g/;
            <ProgressBar;'  />/;,'/g'/;
progress={Math.min(averageScore / 100, 1)}'/;,'/g'/;
color="#4CAF50";
style={styles.scoreProgress}>;
            <DataTable style={styles.metricsTable}>;
              <DataTable.Header>;
                <DataTable.Title>指标名称</DataTable.Title>/;/g/;
                <DataTable.Title numeric>数值</DataTable.Title>/;/g/;
              </DataTable.Header>/;/g/;
              {Object.entries(result.metrics).map([key, value]) => ())}
                <DataTable.Row key={key}>;
                  <DataTable.Cell>{key}</DataTable.Cell>"/;"/g"/;
                  <DataTable.Cell numeric>";"";
                    {typeof value === 'number' ? value.toFixed(2) : value}';'';
                  </DataTable.Cell>/;/g/;
                </DataTable.Row>/;/g/;
              ))}
            </DataTable>/;/g/;
          </Card.Content>/;/g/;
        </Card>/;/g/;
      )}
      {// 预测结果}'/;'/g'/;
      {result.predictions && result.predictions.length > 0  && <Card style={styles.card}>';'';
          <Card.Title title="预测结果"  />"/;"/g"/;
          <Card.Content>;
            <Text style={styles.predictionsCount}>;

            </Text>/;/g/;
            <DataTable>;
              <DataTable.Header>;
                <DataTable.Title>输入数据</DataTable.Title>/;/g/;
                <DataTable.Title>预测结果</DataTable.Title>/;/g/;
                <DataTable.Title numeric>置信度</DataTable.Title>/;/g/;
                <DataTable.Title numeric>处理时间(ms)</DataTable.Title>/;/g/;
              </DataTable.Header>/;/g/;
              {result.predictions.slice(0, 5).map(prediction, index) => ())}
                <DataTable.Row key={index}>";"";
                  <DataTable.Cell>";"";
                    {typeof prediction.input_data === 'string'';}                      ? prediction.input_data.substring(0, 15) + '...'';'';
}
                      : JSON.stringify(prediction.input_data).substring(0, 15) + '...'}'';'';
                    }
                  </DataTable.Cell>'/;'/g'/;
                  <DataTable.Cell>';'';
                    {typeof prediction.prediction === 'string'';}                      ? prediction.prediction.substring(0, 15) + '...'';'';
}
                      : JSON.stringify(prediction.prediction).substring(0, 15) + '...'}'';'';
                    }
                  </DataTable.Cell>'/;'/g'/;
                  <DataTable.Cell numeric>';'';
                    {prediction.confidence ? (prediction.confidence * 100).toFixed(1) + '%' : 'N/A'}'/;'/g'/;
                  </DataTable.Cell>/;/g/;
                  <DataTable.Cell numeric>;
                    {prediction.processing_time.toFixed(2)}
                  </DataTable.Cell>/;/g/;
                </DataTable.Row>/;/g/;
              ))}
            </DataTable>/;/g/;
            {result.predictions.length > 5  && <Text style={styles.moreResultsText}>;

              </Text>/;/g/;
            )}
          </Card.Content>/;/g/;
        </Card>;/;/g/;
      )};
      {// 元数据};/;/g/;
      {result.metadata && Object.keys(result.metadata).length > 0 && (;)}';'';
        <Card style={styles.card}>;';'';
          <Card.Title title="元数据"  />;"/;"/g"/;
          <Card.Content>;
            <DataTable>;
              {Object.entries(result.metadata).map([key, value]) => (;))}
                <DataTable.Row key={key}>;
                  <DataTable.Cell>{key}</DataTable.Cell>;"/;"/g"/;
                  <DataTable.Cell>;";"";
                    {typeof value === 'object' ;';}                      ? JSON.stringify(value, null, 2).substring(0, 50) + '...';';'';
}
                      : String(value);}
                    }
                  </DataTable.Cell>/;/g/;
                </DataTable.Row>/;/g/;
              ))}
            </DataTable>/;/g/;
          </Card.Content>/;/g/;
        </Card>/;/g/;
      )}
      {// 报告生成}'/;'/g'/;
      <Card style={styles.card}>';'';
        <Card.Title title="导出报告"  />"/;"/g"/;
        <Card.Content>;
          <View style={styles.exportContainer}>;
            <View style={styles.exportRow}>";"";
              <Button;"  />/;,"/g"/;
mode="contained";
onPress={() => handleGenerateReport('html')}';,'';
loading={generatingReport.html}
                disabled={generatingReport.html || generatingReport.json}
                style={styles.exportButton}
              >;

              </Button>/;/g/;
              {reportUrls.html  && <View style={styles.reportActions}>';'';
                  <IconButton;'  />/;,'/g'/;
icon="open-in-new";
onPress={() => openReport(reportUrls.html!)}
                  />"/;"/g"/;
                  <IconButton;"  />/;,"/g"/;
icon="share";
onPress={() => shareReport(reportUrls.html!, 'html')}';'';
                  />/;/g/;
                </View>/;/g/;
              )}
            </View>/;/g/;
            <Divider style={styles.divider}>;
            <View style={styles.exportRow}>';'';
              <Button;'  />/;,'/g'/;
mode="outlined";
onPress={() => handleGenerateReport('json')}';,'';
loading={generatingReport.json}
                disabled={generatingReport.html || generatingReport.json}
                style={styles.exportButton}
              >;

              </Button>/;/g/;
              {reportUrls.json  && <View style={styles.reportActions}>';'';
                  <IconButton;'  />/;,'/g'/;
icon="open-in-new";
onPress={() => openReport(reportUrls.json!)}
                  />"/;"/g"/;
                  <IconButton;"  />/;,"/g"/;
icon="share";
onPress={() => shareReport(reportUrls.json!, 'json')}';'';
                  />/;/g/;
                </View>/;/g/;
              )}
            </View>/;/g/;
          </View>/;/g/;
        </Card.Content>/;/g/;
      </Card>/;/g/;
    </ScrollView>;/;/g/;
  );
};
const  styles = StyleSheet.create({)container: {,';,}flex: 1,';'';
}
    const backgroundColor = '#f5f5f5'}'';'';
  ;}
card: {margin: 16,;
}
    const marginBottom = 8;}
  },';,'';
noDataText: {,';,}textAlign: 'center';','';
color: '#666';','';
fontStyle: 'italic';','';'';
}
    const padding = 32;}
  }
headerInfo: {,;}}
  const marginTop = 8;}
  },';,'';
statusRow: {,';,}flexDirection: 'row';','';
justifyContent: 'space-between';','';
alignItems: 'center';','';'';
}
    const marginBottom = 8;}
  }
statusChip: {,;}}
  const height = 28;}
  }
timestampText: {,';,}fontSize: 12,';'';
}
    const color = '#666'}'';'';
  ;},';,'';
durationRow: {,';,}flexDirection: 'row';','';'';
}
    const alignItems = 'center'}'';'';
  ;}
durationLabel: {,';,}fontSize: 14,';,'';
color: '#666';','';'';
}
    const marginRight = 8;}
  }
durationValue: {,';,}fontSize: 14,';,'';
fontWeight: '500';','';'';
}
    const color = '#333'}'';'';
  ;},';,'';
scoreContainer: {,';,}alignItems: 'center';','';'';
}
    const marginVertical = 16;}
  },';,'';
scoreCircle: {,';}}'';
  const alignItems = 'center'}'';'';
  ;}
scoreText: {,';,}fontSize: 36,';'';
}
    const fontWeight = 'bold'}'';'';
  ;}
scoreLabel: {,';,}fontSize: 14,';,'';
color: '#666';','';'';
}
    const marginTop = 4;}
  }
scoreProgress: {height: 8,;
borderRadius: 4,;
marginTop: 16,;
}
    const marginBottom = 16;}
  }
metricsTable: {,;}}
  const marginTop = 16;}
  }
predictionsCount: {,';,}fontSize: 14,';,'';
color: '#666';','';'';
}
    const marginBottom = 8;}
  },';,'';
moreResultsText: {,';,}textAlign: 'center';','';
color: '#666';','';
fontStyle: 'italic';','';'';
}
    const marginTop = 8;}
  }
exportContainer: {,;}}
  const marginTop = 8;}
  },';,'';
exportRow: {,';,}flexDirection: "row";","";"";
}
      alignItems: 'center',justifyContent: 'space-between',marginVertical: 8;'}'';'';
  },exportButton: {flex: 1,marginRight: 8;'}'';'';
  },reportActions: {flexDirection: 'row';')}'';'';
  },divider: {marginVertical: 8;)}
  };)';'';
});