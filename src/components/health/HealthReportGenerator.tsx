import React, { useState, useEffect } from 'react';
import {import {View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  RefreshControl,
  Modal;
} from 'react-native';
  healthDataService,
  HealthReport,
  HealthTrend,
  HealthDataType;
} from '../../services/healthDataService';
interface HealthReportGeneratorProps {
  userId: string;
}
export const HealthReportGenerator: React.FC<HealthReportGeneratorProps> = ({ userId }) => {
  const [reports, setReports] = useState<HealthReport[]>([]);
  const [selectedReport, setSelectedReport] = useState<HealthReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [generating, setGenerating] = useState(false);
  useEffect() => {
    loadReports();
  }, [userId]);
  const loadReports = async () => {try {setLoading(true);
      const response = await healthDataService.getUserHealthReports(userId);
      if (response.data) {
        setReports(response.data);
      }
    } catch (error) {
      console.error('加载健康报告失败:', error);
      Alert.alert("错误",加载健康报告失败');
    } finally {
      setLoading(false);
    }
  };
  const onRefresh = async () => {setRefreshing(true);
    await loadReports();
    setRefreshing(false);
  };
  const generateReport = async (;
    reportType: 'comprehensive' | 'vital_signs' | 'tcm_analysis' | 'trend_analysis',period: 'week' | 'month' | 'quarter' | 'year';
  ) => {try {setGenerating(true);
      const endDate = new Date();
      const startDate = new Date();
      switch (period) {
        case 'week':
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
          break;
      }
      const response = await healthDataService.generateHealthReport(;
        userId,reportType,startDate.toISOString(),endDate.toISOString();
      );
      if (response.data) {
        Alert.alert("成功",健康报告生成完成');
        await loadReports();
      }
    } catch (error) {
      console.error('生成健康报告失败:', error);
      Alert.alert("错误",生成健康报告失败');
    } finally {
      setGenerating(false);
    }
  };
  const getReportTypeLabel = (type: string): string => {const labels: Record<string, string> = {
      comprehensive: "综合健康报告",
      vital_signs: '生命体征报告',tcm_analysis: '中医分析报告',trend_analysis: '趋势分析报告';
    };
    return labels[type] || type;
  };
  const getScoreColor = (score: number): string => {if (score >= 80) return '#4CAF50';
    if (score >= 60) return '#FF9800';
    return '#f44336';
  };
  const getScoreLabel = (score: number): string => {if (score >= 80) return '良好';
    if (score >= 60) return '一般';
    return '需要关注';
  };
  const formatDate = (timestamp: string): string => {return new Date(timestamp).toLocaleDateString('zh-CN');
  };
  const formatPeriod = (period: { startDate: string; endDate: string }): string => {
    return `${formatDate(period.startDate)} - ${formatDate(period.endDate)}`;
  };
  const renderReportCard = (report: HealthReport) => (;
    <TouchableOpacity;
      key={report.id};
      style={styles.reportCard};
      onPress={() => {setSelectedReport(report);
        setModalVisible(true);
      }}
    >
      <View style={styles.reportHeader}>
        <Text style={styles.reportTitle}>{getReportTypeLabel(report.reportType)}</Text>
        <View style={[styles.scoreContainer, { backgroundColor: getScoreColor(report.score) }]}>
          <Text style={styles.scoreText}>{report.score}</Text>
        </View>
      </View>
      <Text style={styles.reportPeriod}>{formatPeriod(report.period)}</Text>
      <Text style={styles.reportDate}>生成时间: {formatDate(report.generatedAt)}</Text>
      <View style={styles.reportPreview}>
        <Text style={styles.reportSummary} numberOfLines={2}>
          {report.summary}
        </Text>
        <View style={styles.reportStats}>
          <Text style={styles.reportStat}>洞察: {report.insights.length} 项</Text>
          <Text style={styles.reportStat}>建议: {report.recommendations.length} 项</Text>
          {report.riskFactors.length > 0 && (
            <Text style={[styles.reportStat, styles.riskStat]}>
              风险: {report.riskFactors.length} 项
            </Text>
          )}
        </View>
      </View>
    </TouchableOpacity>
  );
  const renderGenerateButtons = () => (
    <View style={styles.generateSection}>
      <Text style={styles.sectionTitle}>生成新报告</Text>
      <View style={styles.reportTypeGrid}>
        {[
          {
      type: "comprehensive",
      label: '综合报告', description: '全面健康状况分析' },
          {
      type: "vital_signs",
      label: '生命体征', description: '心率、血压等指标分析' },
          {
      type: "tcm_analysis",
      label: '中医分析', description: '中医五诊综合分析' },
          {
      type: "trend_analysis",
      label: '趋势分析', description: '健康数据变化趋势' }
        ].map(item) => (
          <View key={item.type} style={styles.reportTypeCard}>
            <Text style={styles.reportTypeTitle}>{item.label}</Text>
            <Text style={styles.reportTypeDescription}>{item.description}</Text>
            <View style={styles.periodButtons}>
              {[
                {
      period: "week",
      label: '周报告' },
                {
      period: "month",
      label: '月报告' },
                {
      period: "quarter",
      label: '季报告' },
                {
      period: "year",
      label: '年报告' }
              ].map(periodItem) => (
                <TouchableOpacity;
                  key={periodItem.period};
                  style={styles.periodButton};
                  onPress={() => generateReport(;
                    item.type as any,periodItem.period as any;
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
  const getDataTypeLabel = (type: HealthDataType): string => {const labels: Record<HealthDataType, string> = {[HealthDataType.HEART_RATE]: '心率',[HealthDataType.BLOOD_PRESSURE]: '血压',[HealthDataType.TEMPERATURE]: '体温',[HealthDataType.WEIGHT]: '体重',[HealthDataType.BMI]: 'BMI',[HealthDataType.BLOOD_GLUCOSE]: '血糖',[HealthDataType.SLEEP]: '睡眠',[HealthDataType.EXERCISE]: '运动';
    } as any;
    return labels[type] || type;
  };
  const getTrendLabel = (trend: string): string => {const labels: Record<string, string> = {
      increasing: "上升",
      decreasing: '下降',stable: '稳定';
    };
    return labels[trend] || trend;
  };
  const getTrendColor = (trend: string): string => {const colors: Record<string, string> = {
      increasing: "#f44336",
      decreasing: '#4CAF50',stable: '#666';
    };
    return colors[trend] || '#666';
  };
  const renderReportDetail = () => {if (!selectedReport) return null;
    return (
      <Modal;
        visible={modalVisible}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>
                {getReportTypeLabel(selectedReport.reportType)}
              </Text>
              <TouchableOpacity;
                style={styles.closeButton}
                onPress={() => setModalVisible(false)}
              >
                <Text style={styles.closeButtonText}>×</Text>
              </TouchableOpacity>
            </View>
            <ScrollView style={styles.modalScrollView}>
              {// 报告概览}
              <View style={styles.reportOverview}>
                <View style={styles.overviewHeader}>
                  <View style={[styles.scoreDisplay, { backgroundColor: getScoreColor(selectedReport.score) }]}>
                    <Text style={styles.scoreDisplayText}>{selectedReport.score}</Text>
                    <Text style={styles.scoreDisplayLabel}>{getScoreLabel(selectedReport.score)}</Text>
                  </View>
                  <View style={styles.overviewInfo}>
                    <Text style={styles.overviewPeriod}>{formatPeriod(selectedReport.period)}</Text>
                    <Text style={styles.overviewDate}>生成于 {formatDate(selectedReport.generatedAt)}</Text>
                  </View>
                </View>
                <Text style={styles.reportSummaryFull}>{selectedReport.summary}</Text>
              </View>
              {// 健康洞察}
              {selectedReport.insights.length > 0 && (
        <View style={styles.reportSection}>
                  <Text style={styles.reportSectionTitle}>健康洞察</Text>
                  {selectedReport.insights.map((insight, index) => (
                    <View key={index} style={styles.insightItem}>
                      <Text style={styles.insightText}>• {insight}</Text>
                    </View>
                  ))}
                </View>
              )}
              {// 健康建议}
              {selectedReport.recommendations.length > 0 && (
        <View style={styles.reportSection}>
                  <Text style={styles.reportSectionTitle}>健康建议</Text>
                  {selectedReport.recommendations.map((recommendation, index) => (
                    <View key={index} style={styles.recommendationItem}>
                      <Text style={styles.recommendationText}>• {recommendation}</Text>
                    </View>
                  ))}
                </View>
              )}
              {// 风险因素}
              {selectedReport.riskFactors.length > 0 && (
        <View style={styles.reportSection}>
                  <Text style={[styles.reportSectionTitle, styles.riskTitle]}>风险因素</Text>
                  {selectedReport.riskFactors.map((risk, index) => (
                    <View key={index} style={styles.riskItem}>
                      <Text style={styles.riskText}>⚠️ {risk}</Text>
                    </View>
                  ))}
                </View>
              )}
              {// 趋势分析}
              {selectedReport.trends.length > 0 && (
        <View style={styles.reportSection}>
                  <Text style={styles.reportSectionTitle}>趋势分析</Text>
                  {selectedReport.trends.map((trend, index) => (
                    <View key={index} style={styles.trendItem}>
                      <View style={styles.trendHeader}>
                        <Text style={styles.trendDataType}>
                          {getDataTypeLabel(trend.dataType)}
                        </Text>
                        <Text style={[
                          styles.trendDirection,
                          { color: getTrendColor(trend.trend) }
                        ]}>;
                          {getTrendLabel(trend.trend)};
                        </Text>;
                      </View>;
                      <Text style={styles.trendStats}>;
                        平均值: {trend.averageValue.toFixed(1)} | ;
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
  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>健康报告</Text>
        <Text style={styles.subtitle}>智能分析您的健康状况</Text>
      </View>
      <ScrollView;
        style={styles.scrollView}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />;
        };
      >;
        {// 生成报告按钮};
        {renderGenerateButtons()};
;
        {// 历史报告};
        <View style={styles.historySection}>;
          <Text style={styles.sectionTitle}>历史报告</Text>;
          {loading ? (;
            <Text style={styles.loadingText}>加载中...</Text>;
          ) : reports.length === 0 ? (;
            <Text style={styles.emptyText}>暂无报告，点击上方按钮生成您的第一份健康报告</Text>;
          ) : (;
            reports.map(renderReportCard);
          )}
        </View>
      </ScrollView>
      {// 报告详情模态框}
      {renderReportDetail()}
      {// 生成中提示}
      {generating && (
        <View style={styles.generatingOverlay}>
          <View style={styles.generatingModal}>
            <Text style={styles.generatingText}>正在生成报告...</Text>
            <Text style={styles.generatingSubtext}>请稍候，这可能需要几秒钟</Text>
          </View>
        </View>
      )}
    </View>;
  );
};
const styles = StyleSheet.create({
  container: {,
  flex: 1,
    backgroundColor: '#f5f5f5'
  },
  header: {,
  padding: 16,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0'
  },
  title: {,
  fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4;
  },
  subtitle: {,
  fontSize: 14,
    color: '#666'
  },
  scrollView: {,
  flex: 1;
  },
  generateSection: {,
  padding: 16;
  },
  sectionTitle: {,
  fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 16;
  },
  reportTypeGrid: {,
  gap: 16;
  },
  reportTypeCard: {,
  backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3;
  },
  reportTypeTitle: {,
  fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4;
  },
  reportTypeDescription: {,
  fontSize: 14,
    color: '#666',
    marginBottom: 12;
  },
  periodButtons: {,
  flexDirection: 'row',
    justifyContent: 'space-between'
  },
  periodButton: {,
  flex: 1,
    paddingVertical: 8,
    paddingHorizontal: 12,
    marginHorizontal: 2,
    backgroundColor: '#007AFF',
    borderRadius: 6,
    alignItems: 'center'
  },
  periodButtonText: {,
  color: '#fff',
    fontSize: 12,
    fontWeight: '500'
  },
  historySection: {,
  padding: 16;
  },
  loadingText: {,
  textAlign: 'center',
    color: '#666',
    fontSize: 16,
    marginTop: 20;
  },
  emptyText: {,
  textAlign: 'center',
    color: '#666',
    fontSize: 14,
    fontStyle: 'italic',
    lineHeight: 20,
    marginTop: 20;
  },
  reportCard: {,
  backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3;
  },
  reportHeader: {,
  flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8;
  },
  reportTitle: {,
  fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    flex: 1;
  },
  scoreContainer: {,
  width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center'
  },
  scoreText: {,
  color: '#fff',
    fontSize: 14,
    fontWeight: 'bold'
  },
  reportPeriod: {,
  fontSize: 14,
    color: '#666',
    marginBottom: 4;
  },
  reportDate: {,
  fontSize: 12,
    color: '#999',
    marginBottom: 12;
  },
  reportPreview: {,
  borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
    paddingTop: 12;
  },
  reportSummary: {,
  fontSize: 14,
    color: '#333',
    lineHeight: 20,
    marginBottom: 8;
  },
  reportStats: {,
  flexDirection: 'row',
    justifyContent: 'space-between'
  },
  reportStat: {,
  fontSize: 12,
    color: '#666'
  },
  riskStat: {,
  color: '#f44336'
  },
  modalOverlay: {,
  flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center'
  },
  modalContent: {,
  backgroundColor: '#fff',
    borderRadius: 12,
    width: '95%',
    maxHeight: '90%'
  },
  modalHeader: {,
  flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0'
  },
  modalTitle: {,
  fontSize: 18,
    fontWeight: 'bold',
    color: '#333'
  },
  closeButton: {,
  width: 30,
    height: 30,
    borderRadius: 15,
    backgroundColor: '#f0f0f0',
    justifyContent: 'center',
    alignItems: 'center'
  },
  closeButtonText: {,
  fontSize: 20,
    color: '#666'
  },
  modalScrollView: {,
  maxHeight: '85%'
  },
  reportOverview: {,
  padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0'
  },
  overviewHeader: {,
  flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16;
  },
  scoreDisplay: {,
  width: 80,
    height: 80,
    borderRadius: 40,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16;
  },
  scoreDisplayText: {,
  color: '#fff',
    fontSize: 24,
    fontWeight: 'bold'
  },
  scoreDisplayLabel: {,
  color: '#fff',
    fontSize: 12,
    fontWeight: '500'
  },
  overviewInfo: {,
  flex: 1;
  },
  overviewPeriod: {,
  fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4;
  },
  overviewDate: {,
  fontSize: 14,
    color: '#666'
  },
  reportSummaryFull: {,
  fontSize: 16,
    color: '#333',
    lineHeight: 24;
  },
  reportSection: {,
  padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0'
  },
  reportSectionTitle: {,
  fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 12;
  },
  riskTitle: {,
  color: '#f44336'
  },
  insightItem: {,
  marginBottom: 8;
  },
  insightText: {,
  fontSize: 14,
    color: '#333',
    lineHeight: 20;
  },
  recommendationItem: {,
  marginBottom: 8;
  },
  recommendationText: {,
  fontSize: 14,
    color: '#007AFF',
    lineHeight: 20;
  },
  riskItem: {,
  marginBottom: 8;
  },
  riskText: {,
  fontSize: 14,
    color: '#f44336',
    lineHeight: 20;
  },
  trendItem: {,
  backgroundColor: '#f8f9fa',
    borderRadius: 8,
    padding: 12,
    marginBottom: 8;
  },
  trendHeader: {,
  flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4;
  },
  trendDataType: {,
  fontSize: 14,
    fontWeight: '600',
    color: '#333'
  },
  trendDirection: {,
  fontSize: 14,
    fontWeight: '500'
  },
  trendStats: {,
  fontSize: 12,
    color: '#666'
  },
  generatingOverlay: {,
  position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center'
  },
  generatingModal: {
      backgroundColor: "#fff",
      borderRadius: 12,padding: 24,alignItems: 'center';
  },generatingText: {fontSize: 16,fontWeight: 'bold',color: '#333',marginBottom: 8;
  },generatingSubtext: {fontSize: 14,color: '#666';
  };
});
