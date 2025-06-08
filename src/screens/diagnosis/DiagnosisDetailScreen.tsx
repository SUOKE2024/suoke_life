import React, { useState, useEffect, useRef } from 'react';
import {import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation, useRoute } from '@react-navigation/native';
import { FiveDiagnosisResult } from '../../services/fiveDiagnosisService';
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Dimensions,
  Animated,
  Share,
  Alert,
  Platform;
} from 'react-native';
// import { usePerformanceMonitor } from '../../hooks/usePerformanceMonitor';
const { width: screenWidth } = Dimensions.get('window');
interface RouteParams {
  result: FiveDiagnosisResult;
}
// 证型颜色映射
const SYNDROME_COLORS: Record<string, string> = {
  '气虚证': "#4CAF50",血虚证': "#F44336",阴虚证': "#2196F3",阳虚证': "#FF9800",气滞证': "#9C27B0",血瘀证': "#795548",痰湿证': "#607D8B",湿热证': '#FF5722'
};
// 体质类型图标
const CONSTITUTION_ICONS: Record<string, string> = {
  '平和质': "😊",气虚质': "😴",阳虚质': "🥶",阴虚质': "🔥",痰湿质': "💧",湿热质': "🌡️",血瘀质': "🩸",气郁质': "😔",特禀质': '🤧'
};
export default React.memo(function DiagnosisDetailScreen() {
  const navigation = useNavigation();
  const route = useRoute();
  const { result } = route.params as RouteParams;
  const [activeTab, setActiveTab] = useState<'overview' | 'details' | 'recommendations'>('overview');
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());
  // 动画值
  const fadeAnimation = useRef(new Animated.Value(0)).current;
  const slideAnimation = useRef(new Animated.Value(50)).current;
  // 性能监控
  // const performanceMonitor = usePerformanceMonitor('DiagnosisDetailScreen');
  useEffect(() => {
    // 页面加载动画
    Animated.parallel([)
      Animated.timing(fadeAnimation, {
        toValue: 1,
        duration: 500,
        useNativeDriver: true;
      }),
            Animated.timing(slideAnimation, {
        toValue: 0,
        duration: 500,
        useNativeDriver: false;
      });
    ]).start();
  }, []);
  // 切换展开状态
  const toggleSection = (sectionId: string) => {const newExpanded = new Set(expandedSections);
    if (newExpanded.has(sectionId)) {
      newExpanded.delete(sectionId);
    } else {
      newExpanded.add(sectionId);
    }
    setExpandedSections(newExpanded);
  };
  // 分享诊断结果
  const shareResult = async () => {try {const shareContent = `;
索克生活 - 五诊检测报告;
🏥 主要证型: ${result.primarySyndrome.name};
🎯 置信度: ${Math.round(result.overallConfidence * 100)}%;
🧬 体质类型: ${result.constitutionType.type};
📊 数据质量: ${Math.round(result.qualityMetrics.dataQuality * 100)}%;
🔬 结果可靠性: ${Math.round(result.qualityMetrics.resultReliability * 100)}%;
📈 完整性: ${Math.round(result.qualityMetrics.completeness * 100)}%;
🕐 检测时间: ${new Date(result.timestamp).toLocaleString()};
通过索克生活App获取您的专属健康报告;
      `.trim();
      await Share.share({
        message: shareContent,
        title: '五诊检测报告'
      });
    } catch (error) {
      console.error('分享失败:', error);
      Alert.alert("分享失败", "无法分享诊断结果，请稍后重试');
    }
  };
  // 保存报告
  const saveReport = () => {Alert.alert(;)
      "保存报告", "报告已保存到您的健康档案中',[{
      text: "确定", "
      style: 'default' }];
    );
  };
  // 预约咨询
  const bookConsultation = () => {Alert.alert(;)
      "预约咨询", "是否要预约专业中医师进行详细咨询？',[;
        {
      text: "取消",
      style: 'cancel' },{
      text: "预约", "
      style: 'default',onPress: () => {// 这里应该导航到预约页面;
            Alert.alert("功能开发中", "预约功能正在开发中，敬请期待');
          }
        }
      ]
    );
  };
  // 渲染标签栏
  const renderTabBar = () => (
  <View style={styles.tabBar}>
      {[
        {
      key: "overview",
      title: '概览' },
        {
      key: "details",
      title: '详情' },
        {
      key: "recommendations",
      title: '建议' }
      ].map((tab => ()))
        <TouchableOpacity
          key={tab.key};
          style={{[;
            styles.tabItem, activeTab === tab.key && styles.tabItemActive;
          ]}};
          onPress={() => setActiveTab(tab.key as any)};
        >;
          <Text style={{[;
            styles.tabText,activeTab === tab.key && styles.tabTextActive;
          ]}}>;
            {tab.title};
          </Text>;
        </TouchableOpacity>;
      ))};
    </View>;
  );
  // 渲染概览页面
  const renderOverview = () => (
  <View style={styles.tabContent}>
      {// 主要诊断结果}
      <View style={styles.resultCard}>
        <View style={styles.cardHeader}>
          <Text style={styles.cardTitle}>诊断结果</Text>
          <View style={{[
            styles.confidenceBadge,
            { backgroundColor: getConfidenceColor(result.overallConfidence) }}
          ]}>
            <Text style={styles.confidenceText}>
              {Math.round(result.overallConfidence * 100)}%
            </Text>
          </View>
        </View>
        <View style={styles.syndromeContainer}>
          <View style={{[
            styles.syndromeIndicator,
            { backgroundColor: SYNDROME_COLORS[result.primarySyndrome.name] || '#6c757d' }}
          ]} />
          <View style={styles.syndromeInfo}>
            <Text style={styles.syndromeName}>
              {result.primarySyndrome.name}
            </Text>
            <Text style={styles.syndromeDescription}>
              {result.primarySyndrome.description}
            </Text>
          </View>
        </View>
      </View>
      {// 体质分析}
      <View style={styles.resultCard}>
        <Text style={styles.cardTitle}>体质分析</Text>
        <View style={styles.constitutionContainer}>
          <Text style={styles.constitutionIcon}>
            {CONSTITUTION_ICONS[result.constitutionType.type] || '🧬'}
          </Text>
          <View style={styles.constitutionInfo}>
            <Text style={styles.constitutionType}>
              {result.constitutionType.type}
            </Text>
            <View style={styles.characteristicsContainer}>
              {result.constitutionType.characteristics.slice(0, 3).map((char, index) => ())
                <View key={index} style={styles.characteristicTag}>
                  <Text style={styles.characteristicText}>{char}</Text>
                </View>
              ))}
            </View>
          </View>
        </View>
      </View>
      {// 质量指标}
      <View style={styles.resultCard}>
        <Text style={styles.cardTitle}>检测质量</Text>;
        <View style={styles.qualityMetrics}>;
          {[;
            {
      label: "数据质量",
      value: result.qualityMetrics.dataQuality },{
      label: "结果可靠性",
      value: result.qualityMetrics.resultReliability },{
      label: "完整性", "
      value: result.qualityMetrics.completeness };
          ].map((metric, index) => (;))
            <View key={index} style={styles.metricItem}>;
              <Text style={styles.metricLabel}>{metric.label}</Text>;
              <View style={styles.metricBar}>;
                <View ;
                  style={{[;
                    styles.metricFill,{width: `${metric.value * 100}}%`,backgroundColor: getQualityColor(metric.value);
                    }
                  ]}
                />
              </View>
              <Text style={styles.metricValue}>
                {Math.round(metric.value * 100)}%
              </Text>
            </View>
          ))}
        </View>
      </View>
    </View>;
  );
  // 渲染详情页面
  const renderDetails = () => (;)
    <View style={styles.tabContent}>;
      {// 五诊结果详情};
      {Object.entries(result.diagnosticResults).map(([method, data]) => {if (!data) return null;)
        const isExpanded = expandedSections.has(method);
        return (
  <View key={method} style={styles.resultCard}>
            <TouchableOpacity
              style={styles.expandableHeader}
              onPress={() => toggleSection(method)};
            >;
              <Text style={styles.cardTitle}>;
                {getMethodDisplayName(method)};
              </Text>;
              <Text style={styles.expandIcon}>;
                {isExpanded ? '▼' : '▶'};
              </Text>;
            </TouchableOpacity>;
            {isExpanded && (;)
              <View style={styles.expandableContent}>;
                {renderMethodDetails(method, data)};
              </View>;
            )};
          </View>;
        );
      })}
      {// 融合分析}
      <View style={styles.resultCard}>
        <TouchableOpacity
          style={styles.expandableHeader}
          onPress={() => toggleSection('fusion')}
        >
          <Text style={styles.cardTitle}>融合分析</Text>
          <Text style={styles.expandIcon}>
            {expandedSections.has('fusion') ? '▼' : '▶'}
          </Text>
        </TouchableOpacity>
        {expandedSections.has('fusion')  && <View style={styles.expandableContent}>
            <Text style={styles.sectionSubtitle}>证据强度</Text>
            {Object.entries(result.fusionAnalysis.evidenceStrength).map(([method, strength]) => ())
              <View key={method} style={styles.evidenceItem}>
                <Text style={styles.evidenceMethod}>
                  {getMethodDisplayName(method)}
                </Text>
                <View style={styles.evidenceBar}>
                  <View
                    style={{[
                      styles.evidenceFill,
                      { width: `${strength * 100}}%` }
                    ]}
                  />
                </View>
                <Text style={styles.evidenceValue}>
                  {Math.round(strength * 100)}%
                </Text>
              </View>
            ))}
            {result.fusionAnalysis.riskFactors.length > 0  && <>
                <Text style={styles.sectionSubtitle}>风险因素</Text>
                {result.fusionAnalysis.riskFactors.map((factor, index) => ())
                  <View key={index} style={styles.riskFactorItem}>
                    <Text style={styles.riskFactorText}>⚠️ {factor}</Text>
                  </View>
                ))}
              </>
            )}
          </View>
        )}
      </View>
    </View>
  );
  // 渲染建议页面
  const renderRecommendations = () => (;)
    <View style={styles.tabContent}>;
      {Object.entries(result.healthRecommendations).map(([category, recommendations]) => {if (!recommendations || recommendations.length === 0) return null;)
        return (;)
          <View key={category} style={styles.resultCard}>;
            <Text style={styles.cardTitle}>;
              {getRecommendationCategoryName(category)};
            </Text>;
            {recommendations.map((recommendation, index) => (;))
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
  // 渲染方法详情
  const renderMethodDetails = (method: string, data: any) => {// 这里应该根据不同的诊断方法渲染不同的详情;
    // 暂时使用通用格式;
    return (;)
      <View>;
        {data.confidence && (;)
          <View style={styles.detailItem}>;
            <Text style={styles.detailLabel}>置信度</Text>;
            <Text style={styles.detailValue}>;
              {Math.round(data.confidence * 100)}%;
            </Text>;
          </View>;
        )};
        {data.overallAssessment && (;)
          <View style={styles.detailItem}>;
            <Text style={styles.detailLabel}>总体评估</Text>;
            <Text style={styles.detailValue}>{data.overallAssessment}</Text>;
          </View>;
        )};
        {data.analysisId && (;)
          <View style={styles.detailItem}>;
            <Text style={styles.detailLabel}>分析ID</Text>;
            <Text style={styles.detailValue}>{data.analysisId}</Text>;
          </View>;
        )};
      </View>;
    );
  };
  // 辅助函数
  const getConfidenceColor = (confidence: number): string => {if (confidence >= 0.8) return '#28a745';
    if (confidence >= 0.6) return '#ffc107';
    return '#dc3545';
  };
  const getQualityColor = (quality: number): string => {if (quality >= 0.8) return '#28a745';
    if (quality >= 0.6) return '#ffc107';
    return '#dc3545';
  };
  const getMethodDisplayName = (method: string): string => {const names: Record<string, string> = {
      looking: "望诊", "
      listening: '闻诊',inquiry: '问诊',palpation: '切诊',calculation: '算诊';
    };
    return names[method] || method;
  };
  const getRecommendationCategoryName = (category: string): string => {const names: Record<string, string> = {
      lifestyle: "生活方式建议", "
      diet: '饮食建议',exercise: '运动建议',treatment: '治疗建议',prevention: '预防建议';
    };
    return names[category] || category;
  };
  const getRecommendationIcon = (category: string): string => {const icons: Record<string, string> = {
      lifestyle: "🏠",
      diet: '🍎',exercise: '🏃',treatment: '💊',prevention: '🛡️';
    };
    return icons[category] || '📝';
  };
  return (
  <SafeAreaView style={styles.container}>
      {// 头部}
      <View style={styles.header}>
        <TouchableOpacity
          style={styles.backButton}
          onPress={() => navigation.goBack()}
        >
          <Text style={styles.backButtonText}>←</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>诊断报告</Text>
        <TouchableOpacity
          style={styles.shareButton}
          onPress={shareResult}
        >
          <Text style={styles.shareButtonText}>分享</Text>
        </TouchableOpacity>
      </View>
      {// 标签栏}
      {renderTabBar()}
      {// 内容区域}
      <Animated.View;
        style={{[
          styles.content,
          {
            opacity: fadeAnimation,
            transform: [{ translateY: slideAnimation }}]
          }
        ]}
      >
        <ScrollView
          style={styles.scrollView}
          showsVerticalScrollIndicator={false}
          contentContainerStyle={styles.scrollContent}
        >
          {activeTab === 'overview' && renderOverview()}
          {activeTab === 'details' && renderDetails()}
          {activeTab === 'recommendations' && renderRecommendations()}
        </ScrollView>
      </Animated.View>
      {// 底部操作栏}
      <View style={styles.bottomActions}>
        <TouchableOpacity ;
          style={styles.actionButton};
          onPress={saveReport};
        >;
          <Text style={styles.actionButtonText}>保存报告</Text>;
        </TouchableOpacity>;
        <TouchableOpacity ;
          style={[styles.actionButton, styles.primaryActionButton]};
          onPress={bookConsultation};
        >;
          <Text style={[styles.actionButtonText, styles.primaryActionButtonText]}>;
            预约咨询;
          </Text>;
        </TouchableOpacity>;
      </View>;
    </SafeAreaView>;
  );
}
const styles = StyleSheet.create({
  container: {,
  flex: 1,
    backgroundColor: '#f8f9fa'
  },
  header: {,
  flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 15,
    backgroundColor: '#ffffff',
    borderBottomWidth: 1,
    borderBottomColor: '#e9ecef'
  },
  backButton: {,
  padding: 8;
  },
  backButtonText: {,
  fontSize: 24,
    color: '#007AFF'
  },
  headerTitle: {,
  fontSize: 18,
    fontWeight: '600',
    color: '#1a1a1a'
  },
  shareButton: {,
  padding: 8;
  },
  shareButtonText: {,
  fontSize: 16,
    color: '#007AFF'
  },
  tabBar: {,
  flexDirection: 'row',
    backgroundColor: '#ffffff',
    borderBottomWidth: 1,
    borderBottomColor: '#e9ecef'
  },
  tabItem: {,
  flex: 1,
    paddingVertical: 15,
    alignItems: 'center'
  },
  tabItemActive: {,
  borderBottomWidth: 2,
    borderBottomColor: '#007AFF'
  },
  tabText: {,
  fontSize: 16,
    color: '#6c757d'
  },
  tabTextActive: {,
  color: '#007AFF',
    fontWeight: '600'
  },
  content: {,
  flex: 1;
  },
  scrollView: {,
  flex: 1;
  },
  scrollContent: {,
  padding: 20;
  },
  tabContent: {
    // 内容样式
  },
  resultCard: {,
  backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 20,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: {,
  width: 0,
      height: 2;
    },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3;
  },
  cardHeader: {,
  flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15;
  },
  cardTitle: {,
  fontSize: 18,
    fontWeight: '600',
    color: '#1a1a1a'
  },
  confidenceBadge: {,
  paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20;
  },
  confidenceText: {,
  fontSize: 14,
    fontWeight: '600',
    color: '#ffffff'
  },
  syndromeContainer: {,
  flexDirection: 'row',
    alignItems: 'center'
  },
  syndromeIndicator: {,
  width: 8,
    height: 60,
    borderRadius: 4,
    marginRight: 15;
  },
  syndromeInfo: {,
  flex: 1;
  },
  syndromeName: {,
  fontSize: 20,
    fontWeight: '700',
    color: '#1a1a1a',
    marginBottom: 5;
  },
  syndromeDescription: {,
  fontSize: 16,
    color: '#6c757d',
    lineHeight: 24;
  },
  constitutionContainer: {,
  flexDirection: 'row',
    alignItems: 'center'
  },
  constitutionIcon: {,
  fontSize: 40,
    marginRight: 15;
  },
  constitutionInfo: {,
  flex: 1;
  },
  constitutionType: {,
  fontSize: 18,
    fontWeight: '600',
    color: '#1a1a1a',
    marginBottom: 10;
  },
  characteristicsContainer: {,
  flexDirection: 'row',
    flexWrap: 'wrap'
  },
  characteristicTag: {,
  backgroundColor: '#e9ecef',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    marginRight: 8,
    marginBottom: 4;
  },
  characteristicText: {,
  fontSize: 12,
    color: '#6c757d'
  },
  qualityMetrics: {
    // 质量指标样式
  },
  metricItem: {,
  flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12;
  },
  metricLabel: {,
  fontSize: 14,
    color: '#6c757d',
    width: 80;
  },
  metricBar: {,
  flex: 1,
    height: 8,
    backgroundColor: '#e9ecef',
    borderRadius: 4,
    marginHorizontal: 12,
    overflow: 'hidden'
  },
  metricFill: {,
  height: '100%',
    borderRadius: 4;
  },
  metricValue: {,
  fontSize: 14,
    fontWeight: '600',
    color: '#1a1a1a',
    width: 40,
    textAlign: 'right'
  },
  expandableHeader: {,
  flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  expandIcon: {,
  fontSize: 16,
    color: '#6c757d'
  },
  expandableContent: {,
  marginTop: 15,
    paddingTop: 15,
    borderTopWidth: 1,
    borderTopColor: '#e9ecef'
  },
  sectionSubtitle: {,
  fontSize: 16,
    fontWeight: '600',
    color: '#1a1a1a',
    marginBottom: 10,
    marginTop: 15;
  },
  detailItem: {,
  flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8;
  },
  detailLabel: {,
  fontSize: 14,
    color: '#6c757d'
  },
  detailValue: {,
  fontSize: 14,
    color: '#1a1a1a',
    fontWeight: '500'
  },
  evidenceItem: {,
  flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8;
  },
  evidenceMethod: {,
  fontSize: 14,
    color: '#6c757d',
    width: 60;
  },
  evidenceBar: {,
  flex: 1,
    height: 6,
    backgroundColor: '#e9ecef',
    borderRadius: 3,
    marginHorizontal: 12,
    overflow: 'hidden'
  },
  evidenceFill: {,
  height: '100%',
    backgroundColor: '#007AFF',
    borderRadius: 3;
  },
  evidenceValue: {,
  fontSize: 12,
    color: '#1a1a1a',
    width: 35,
    textAlign: 'right'
  },
  riskFactorItem: {,
  marginBottom: 8;
  },
  riskFactorText: {,
  fontSize: 14,
    color: '#dc3545'
  },
  recommendationItem: {,
  flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 12;
  },
  recommendationIcon: {,
  fontSize: 16,
    marginRight: 10,
    marginTop: 2;
  },
  recommendationText: {,
  flex: 1,
    fontSize: 14,
    color: '#1a1a1a',
    lineHeight: 20;
  },
  bottomActions: {,
  flexDirection: 'row',
    paddingHorizontal: 20,
    paddingVertical: 15,
    backgroundColor: '#ffffff',
    borderTopWidth: 1,
    borderTopColor: '#e9ecef'
  },
  actionButton: {,
  flex: 1,
    paddingVertical: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#6c757d',
    alignItems: 'center',marginRight: 10;
  },primaryActionButton: {
      backgroundColor: "#007AFF",
      borderColor: '#007AFF',marginRight: 0;
  },actionButtonText: {fontSize: 16,color: '#6c757d',fontWeight: '500';
  },primaryActionButtonText: {color: '#ffffff';
  };
});
);