import React, { useState } from 'react';
import {import {import { useSelector, useDispatch } from 'react-redux';
import {import type { AppDispatch } from '../../store';
import type { BenchmarkResult } from '../../services';
  View,
  Text,
  StyleSheet,
  ScrollView,
  Alert,
  Linking,
  Share;
} from 'react-native';
  Card,
  Button,
  Chip,
  DataTable,
  ProgressBar,
  Divider,
  IconButton;
} from 'react-native-paper';
  selectCurrentResult,
  selectBenchmarkLoading,
  generateReport;
} from '../../store/slices/benchmarkSlice';
interface BenchmarkReportProps {
  taskId: string;
  onClose?: () => void;
}
export const BenchmarkReport: React.FC<BenchmarkReportProps> = ({
  taskId,
  onClose;
}) => {
  const dispatch = useDispatch<AppDispatch>();
  const result = useSelector(selectCurrentResult);
  const loading = useSelector(selectBenchmarkLoading);
  const [reportUrls, setReportUrls] = useState<{html?: string;
    json?: string;
  }>({});
  const [generatingReport, setGeneratingReport] = useState<{html: boolean,
  json: boolean;
  }>({ html: false, json: false });
  // 生成报告
  const handleGenerateReport = async (format: 'html' | 'json') => {try {setGeneratingReport(prev => ({ ...prev, [format]: true }));
      const response = await dispatch(generateReport({taskId,format ;))
      })).unwrap();
      setReportUrls(prev => ({
        ...prev,
        [format]: response.reportUrl;
      }));
      Alert.alert('报告生成成功',
        `${format.toUpperCase()}格式报告已生成`,
        [
          { text: '确定' },
          {
      text: "打开报告", "
      onPress: () => openReport(response.reportUrl);
          }
        ]
      );
    } catch (error) {
      Alert.alert('生成失败', `生成${format.toUpperCase()}报告失败: ${error}`);
    } finally {
      setGeneratingReport(prev => ({ ...prev, [format]: false }));
    }
  };
  // 打开报告
  const openReport = async (url: string) => {try {const supported = await Linking.canOpenURL(url);
      if (supported) {
        await Linking.openURL(url);
      } else {
        Alert.alert("无法打开", "无法打开报告链接');
      }
    } catch (error) {
      Alert.alert("打开失败", "打开报告时发生错误');
    }
  };
  // 分享报告
  const shareReport = async (url: string, format: string) => {try {await Share.share({message: `基准测试报告 (${format.toUpperCase()}): ${url}`,url: url,title: '基准测试报告';)
      });
    } catch (error) {
      console.error('分享失败:', error);
    }
  };
  // 格式化时间
  const formatDuration = (seconds: number) => {const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor(seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    if (hours > 0) {
      return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${secs}s`;
    } else {
      return `${secs}s`;
    }
  };
  if (!result) {
    return (;)
      <View style={styles.container}>;
        <Card style={styles.card}>;
          <Card.Content>;
            <Text style={styles.noDataText}>暂无报告数据</Text>;
          </Card.Content>;
        </Card>;
      </View>;
    );
  }
  // 计算平均分数
  const metricsValues = result.metrics ? Object.values(result.metrics) : [];
  const averageScore = metricsValues.length > 0 ;
    ? metricsValues.reduce(sum, val) => sum + val, 0) / metricsValues.length ;
    : 0;
  return (
  <ScrollView style={styles.container}>
      {// 报告头部}
      <Card style={styles.card}>
        <Card.Title;
          title="基准测试报告"
          subtitle={`任务ID: ${taskId}`}
          right={() => onClose  && <IconButton icon="close" onPress={onClose} />
          )}
        />
        <Card.Content>
          <View style={styles.headerInfo}>
            <View style={styles.statusRow}>
              <Chip
                style={{[styles.statusChip, { backgroundColor: '#4CAF50' }}]}
                textStyle={ color: 'white' }}
              >
                已完成
              </Chip>
              <Text style={styles.timestampText}>
                {new Date(result.timestamp).toLocaleString()}
              </Text>
            </View>
            <View style={styles.durationRow}>
              <Text style={styles.durationLabel}>执行时长:</Text>
              <Text style={styles.durationValue}>
                {formatDuration(result.execution_time)}
              </Text>
            </View>
          </View>
        </Card.Content>
      </Card>
      {// 基本信息}
      <Card style={styles.card}>
        <Card.Title title="基本信息" />
        <Card.Content>
          <DataTable>
            <DataTable.Row>
              <DataTable.Cell>基准测试ID</DataTable.Cell>
              <DataTable.Cell>{result.benchmark_id}</DataTable.Cell>
            </DataTable.Row>
            <DataTable.Row>
              <DataTable.Cell>模型ID</DataTable.Cell>
              <DataTable.Cell>{result.model_id}</DataTable.Cell>
            </DataTable.Row>
            <DataTable.Row>
              <DataTable.Cell>模型版本</DataTable.Cell>
              <DataTable.Cell>{result.model_version}</DataTable.Cell>
            </DataTable.Row>
            <DataTable.Row>
              <DataTable.Cell>执行时间</DataTable.Cell>
              <DataTable.Cell>{formatDuration(result.execution_time)}</DataTable.Cell>
            </DataTable.Row>
          </DataTable>
        </Card.Content>
      </Card>
      {// 性能指标}
      {result.metrics && Object.keys(result.metrics).length > 0  && <Card style={styles.card}>
          <Card.Title title="性能指标" />
          <Card.Content>
            <View style={styles.scoreContainer}>
              <View style={styles.scoreCircle}>
                <Text style={{[styles.scoreText, { color: '#4CAF50' }}]}>
                  {averageScore.toFixed(1)}
                </Text>
                <Text style={styles.scoreLabel}>平均分</Text>
              </View>
            </View>
            <ProgressBar
              progress={Math.min(averageScore / 100, 1)}
              color="#4CAF50"
              style={styles.scoreProgress}>
            <DataTable style={styles.metricsTable}>
              <DataTable.Header>
                <DataTable.Title>指标名称</DataTable.Title>
                <DataTable.Title numeric>数值</DataTable.Title>
              </DataTable.Header>
              {Object.entries(result.metrics).map(([key, value]) => ())
                <DataTable.Row key={key}>
                  <DataTable.Cell>{key}</DataTable.Cell>
                  <DataTable.Cell numeric>
                    {typeof value === 'number' ? value.toFixed(2) : value}
                  </DataTable.Cell>
                </DataTable.Row>
              ))}
            </DataTable>
          </Card.Content>
        </Card>
      )}
      {// 预测结果}
      {result.predictions && result.predictions.length > 0  && <Card style={styles.card}>
          <Card.Title title="预测结果" />
          <Card.Content>
            <Text style={styles.predictionsCount}>
              共 {result.predictions.length} 个预测结果
            </Text>
            <DataTable>
              <DataTable.Header>
                <DataTable.Title>输入数据</DataTable.Title>
                <DataTable.Title>预测结果</DataTable.Title>
                <DataTable.Title numeric>置信度</DataTable.Title>
                <DataTable.Title numeric>处理时间(ms)</DataTable.Title>
              </DataTable.Header>
              {result.predictions.slice(0, 5).map((prediction, index) => ())
                <DataTable.Row key={index}>
                  <DataTable.Cell>
                    {typeof prediction.input_data === 'string'
                      ? prediction.input_data.substring(0, 15) + '...'
                      : JSON.stringify(prediction.input_data).substring(0, 15) + '...'
                    }
                  </DataTable.Cell>
                  <DataTable.Cell>
                    {typeof prediction.prediction === 'string'
                      ? prediction.prediction.substring(0, 15) + '...'
                      : JSON.stringify(prediction.prediction).substring(0, 15) + '...'
                    }
                  </DataTable.Cell>
                  <DataTable.Cell numeric>
                    {prediction.confidence ? (prediction.confidence * 100).toFixed(1) + '%' : 'N/A'}
                  </DataTable.Cell>
                  <DataTable.Cell numeric>
                    {prediction.processing_time.toFixed(2)}
                  </DataTable.Cell>
                </DataTable.Row>
              ))}
            </DataTable>
            {result.predictions.length > 5  && <Text style={styles.moreResultsText}>
                还有 {result.predictions.length - 5} 个结果...
              </Text>
            )}
          </Card.Content>
        </Card>;
      )};
      {// 元数据};
      {result.metadata && Object.keys(result.metadata).length > 0 && (;)
        <Card style={styles.card}>;
          <Card.Title title="元数据" />;
          <Card.Content>;
            <DataTable>;
              {Object.entries(result.metadata).map(([key, value]) => (;))
                <DataTable.Row key={key}>;
                  <DataTable.Cell>{key}</DataTable.Cell>;
                  <DataTable.Cell>;
                    {typeof value === 'object' ;
                      ? JSON.stringify(value, null, 2).substring(0, 50) + '...';
                      : String(value);
                    }
                  </DataTable.Cell>
                </DataTable.Row>
              ))}
            </DataTable>
          </Card.Content>
        </Card>
      )}
      {// 报告生成}
      <Card style={styles.card}>
        <Card.Title title="导出报告" />
        <Card.Content>
          <View style={styles.exportContainer}>
            <View style={styles.exportRow}>
              <Button
                mode="contained"
                onPress={() => handleGenerateReport('html')}
                loading={generatingReport.html}
                disabled={generatingReport.html || generatingReport.json}
                style={styles.exportButton}
              >
                生成HTML报告
              </Button>
              {reportUrls.html  && <View style={styles.reportActions}>
                  <IconButton
                    icon="open-in-new"
                    onPress={() => openReport(reportUrls.html!)}
                  />
                  <IconButton
                    icon="share"
                    onPress={() => shareReport(reportUrls.html!, 'html')}
                  />
                </View>
              )}
            </View>
            <Divider style={styles.divider}>
            <View style={styles.exportRow}>
              <Button
                mode="outlined"
                onPress={() => handleGenerateReport('json')}
                loading={generatingReport.json}
                disabled={generatingReport.html || generatingReport.json}
                style={styles.exportButton}
              >
                生成JSON报告
              </Button>
              {reportUrls.json  && <View style={styles.reportActions}>
                  <IconButton
                    icon="open-in-new"
                    onPress={() => openReport(reportUrls.json!)}
                  />
                  <IconButton
                    icon="share"
                    onPress={() => shareReport(reportUrls.json!, 'json')}
                  />
                </View>
              )}
            </View>
          </View>
        </Card.Content>
      </Card>
    </ScrollView>;
  );
};
const styles = StyleSheet.create({
  container: {,
  flex: 1,
    backgroundColor: '#f5f5f5'
  },
  card: {,
  margin: 16,
    marginBottom: 8;
  },
  noDataText: {,
  textAlign: 'center',
    color: '#666',
    fontStyle: 'italic',
    padding: 32;
  },
  headerInfo: {,
  marginTop: 8;
  },
  statusRow: {,
  flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8;
  },
  statusChip: {,
  height: 28;
  },
  timestampText: {,
  fontSize: 12,
    color: '#666'
  },
  durationRow: {,
  flexDirection: 'row',
    alignItems: 'center'
  },
  durationLabel: {,
  fontSize: 14,
    color: '#666',
    marginRight: 8;
  },
  durationValue: {,
  fontSize: 14,
    fontWeight: '500',
    color: '#333'
  },
  scoreContainer: {,
  alignItems: 'center',
    marginVertical: 16;
  },
  scoreCircle: {,
  alignItems: 'center'
  },
  scoreText: {,
  fontSize: 36,
    fontWeight: 'bold'
  },
  scoreLabel: {,
  fontSize: 14,
    color: '#666',
    marginTop: 4;
  },
  scoreProgress: {,
  height: 8,
    borderRadius: 4,
    marginTop: 16,
    marginBottom: 16;
  },
  metricsTable: {,
  marginTop: 16;
  },
  predictionsCount: {,
  fontSize: 14,
    color: '#666',
    marginBottom: 8;
  },
  moreResultsText: {,
  textAlign: 'center',
    color: '#666',
    fontStyle: 'italic',
    marginTop: 8;
  },
  exportContainer: {,
  marginTop: 8;
  },
  exportRow: {
      flexDirection: "row",
      alignItems: 'center',justifyContent: 'space-between',marginVertical: 8;
  },exportButton: {flex: 1,marginRight: 8;
  },reportActions: {flexDirection: 'row';
  },divider: {marginVertical: 8;
  };
});