import { RouteProp, useNavigation, useRoute } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import React, { useCallback, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  Dimensions,
  Modal,
  ScrollView,
  StatusBar,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { useSelector } from 'react-redux';
import { RootState } from '../../store';

const { width, height } = Dimensions.get('window');

// 诊断结果类型
interface DiagnosisResult {
  id: string;,
  serviceType: string;,
  result: string;,
  confidence: number;,
  timestamp: Date;,
  details: any;
}

// 诊断服务信息类型
interface DiagnosisServiceInfo {
  id: string;,
  name: string;,
  description: string;,
  icon: string;,
  endpoint: string;,
  capabilities: string[];,
  status: 'active' | 'inactive' | 'maintenance';,
  colors: {,
  primary: string;,
  secondary: string;,
  accent: string;
  };
}

// 路由参数类型
type RootStackParamList = {
  DiagnosisService: { serviceType: string };
};

type DiagnosisServiceScreenRouteProp = RouteProp<
  RootStackParamList,
  'DiagnosisService'
>;
type DiagnosisServiceScreenNavigationProp = NativeStackNavigationProp<
  RootStackParamList,
  'DiagnosisService'
>;

const DiagnosisServiceScreen: React.FC = () => {
  const navigation = useNavigation<DiagnosisServiceScreenNavigationProp>();
  const route = useRoute<DiagnosisServiceScreenRouteProp>();
  const { serviceType } = route.params;

  const [serviceInfo, setServiceInfo] = useState<DiagnosisServiceInfo | null>(
    null;
  );
  const [diagnosisResults, setDiagnosisResults] = useState<DiagnosisResult[]>(
    []
  );
  const [loading, setLoading] = useState(true);
  const [diagnosing, setDiagnosing] = useState(false);
  const [showResultModal, setShowResultModal] = useState(false);
  const [currentResult, setCurrentResult] = useState<DiagnosisResult | null>(
    null;
  );

  // 从Redux获取用户信息
  const authState = useSelector(state: RootState) => state.auth);
  const user = 'user' in authState ? authState.user : null;

  // 诊断服务配置
  const diagnosisServices: Record<string, DiagnosisServiceInfo> = {
    calculation: {,
  id: 'calculation',
      name: '算诊服务',
      description: '基于中医理论的计算诊断，通过算法分析症状和体征',
      icon: '🔍',
      endpoint: 'http://localhost:8023',
      capabilities: ['症状分析', '证型识别', '方剂推荐', '病情评估'],
      status: 'active',
      colors: {,
  primary: '#FF6B6B',
        secondary: '#FFEBEE',
        accent: '#F44336',
      },
    },
    look: {,
  id: 'look',
      name: '望诊服务',
      description: '通过图像分析进行望诊，包括面色、舌象、体态等',
      icon: '👁️',
      endpoint: 'http://localhost:8020',
      capabilities: ['面色分析', '舌象识别', '体态评估', '皮肤检测'],
      status: 'active',
      colors: {,
  primary: '#4CAF50',
        secondary: '#E8F5E8',
        accent: '#2E7D32',
      },
    },
    listen: {,
  id: 'listen',
      name: '闻诊服务',
      description: '通过语音分析进行闻诊，包括声音、呼吸、咳嗽等',
      icon: '👂',
      endpoint: 'http://localhost:8022',
      capabilities: ['声音分析', '呼吸评估', '咳嗽识别', '语音特征'],
      status: 'active',
      colors: {,
  primary: '#2196F3',
        secondary: '#E3F2FD',
        accent: '#1976D2',
      },
    },
    inquiry: {,
  id: 'inquiry',
      name: '问诊服务',
      description: '智能问诊系统，通过对话收集症状和病史信息',
      icon: '💬',
      endpoint: 'http://localhost:8021',
      capabilities: ['症状询问', '病史收集', '智能对话', '信息整理'],
      status: 'active',
      colors: {,
  primary: '#9C27B0',
        secondary: '#F3E5F5',
        accent: '#7B1FA2',
      },
    },
    palpation: {,
  id: 'palpation',
      name: '切诊服务',
      description: '模拟切诊过程，通过传感器数据分析脉象等',
      icon: '🤲',
      endpoint: 'http://localhost:8024',
      capabilities: ['脉象分析', '触诊模拟', '压力感知', '温度检测'],
      status: 'active',
      colors: {,
  primary: '#FF9800',
        secondary: '#FFF3E0',
        accent: '#F57C00',
      },
    },
  };

  // 初始化服务信息
  useEffect() => {
    const service = diagnosisServices[serviceType];
    if (service) {
      setServiceInfo(service);
      loadDiagnosisHistory();
    }
    setLoading(false);
  }, [serviceType]);

  // 加载诊断历史
  const loadDiagnosisHistory = useCallback(async () => {
    try {
      // 模拟加载历史记录
      const mockHistory: DiagnosisResult[] = [
        {
          id: '1',
          serviceType,
          result: '根据分析，您的整体状况良好',
          confidence: 0.85,
          timestamp: new Date(Date.now() - 86400000), // 1天前
          details: { score: 85, recommendations: ['保持良好作息', '适量运动'] },
        },
        {
          id: '2',
          serviceType,
          result: '建议关注睡眠质量',
          confidence: 0.72,
          timestamp: new Date(Date.now() - 172800000), // 2天前
          details: { score: 72, recommendations: ['改善睡眠环境', '规律作息'] },
        },
      ];
      setDiagnosisResults(mockHistory);
    } catch (error) {
      console.error('加载诊断历史失败:', error);
    }
  }, [serviceType]);

  // 开始诊断
  const startDiagnosis = useCallback(async () => {
    if (!serviceInfo) return;

    setDiagnosing(true);
    try {
      // 模拟诊断过程
      await new Promise(resolve) =>
        setTimeout(resolve, 3000 + Math.random() * 2000)
      );

      const mockResult: DiagnosisResult = {,
  id: Date.now().toString(),
        serviceType: serviceInfo.id,
        result: generateMockResult(serviceInfo.id),
        confidence: 0.75 + Math.random() * 0.2,
        timestamp: new Date(),
        details: generateMockDetails(serviceInfo.id),
      };

      setDiagnosisResults(prev) => [mockResult, ...prev]);
      setCurrentResult(mockResult);
      setShowResultModal(true);
    } catch (error) {
      console.error('诊断失败:', error);
      Alert.alert('错误', '诊断过程中出现错误，请重试');
    } finally {
      setDiagnosing(false);
    }
  }, [serviceInfo]);

  // 生成模拟诊断结果
  const generateMockResult = (serviceType: string): string => {
    const results = {
      calculation: [
        '根据症状分析，建议关注脾胃调理',
        '体质偏向气虚，建议补气养血',
        '整体健康状况良好，保持现状',
      ],
      look: [
        '面色红润，气色良好',
        '舌苔略厚，建议清淡饮食',
        '眼神清亮，精神状态佳',
      ],
      listen: [
        '声音洪亮，肺气充足',
        '呼吸平稳，无异常音',
        '语音清晰，神志清楚',
      ],
      inquiry: [
        '症状描述清晰，建议进一步检查',
        '病史信息完整，诊断依据充分',
        '主诉明确，治疗方向清楚',
      ],
      palpation: [
        '脉象平和，心率正常',
        '脉搏有力，血液循环良好',
        '脉象略弦，建议放松心情',
      ],
    };

    const serviceResults =
      results[serviceType as keyof typeof results] || results.calculation;
    return serviceResults[Math.floor(Math.random() * serviceResults.length)];
  };

  // 生成模拟详细信息
  const generateMockDetails = (serviceType: string) => {
    return {
      score: Math.floor(70 + Math.random() * 25),
      metrics: {,
  accuracy: Math.floor(80 + Math.random() * 15),
        reliability: Math.floor(75 + Math.random() * 20),
        completeness: Math.floor(85 + Math.random() * 10),
      },
      recommendations: [
        '保持规律作息',
        '适量运动锻炼',
        '均衡营养饮食',
        '定期健康检查',
      ].slice(0, 2 + Math.floor(Math.random() * 2)),
    };
  };

  // 渲染服务能力
  const renderCapabilities = () => {
    if (!serviceInfo) return null;

    return (
      <View style={styles.capabilitiesContainer}>
        <Text style={styles.sectionTitle}>服务能力</Text>
        <View style={styles.capabilitiesGrid}>
          {serviceInfo.capabilities.map(capability, index) => (
            <View;
              key={index}
              style={[
                styles.capabilityItem,
                { backgroundColor: serviceInfo.colors.secondary },
              ]}
            >
              <Text;
                style={[
                  styles.capabilityText,
                  { color: serviceInfo.colors.primary },
                ]}
              >
                {capability}
              </Text>
            </View>
          ))}
        </View>
      </View>
    );
  };

  // 渲染诊断历史
  const renderDiagnosisHistory = () => {
    if (diagnosisResults.length === 0) {
      return (
        <View style={styles.emptyHistory}>
          <Icon name="history" size={48} color="#CCC" />
          <Text style={styles.emptyHistoryText}>暂无诊断记录</Text>
          <Text style={styles.emptyHistorySubtext}>开始您的第一次诊断</Text>
        </View>
      );
    }

    return (
      <View style={styles.historyContainer}>
        <Text style={styles.sectionTitle}>诊断历史</Text>
        {diagnosisResults.map(result) => (
          <TouchableOpacity;
            key={result.id}
            style={styles.historyItem}
            onPress={() => {
              setCurrentResult(result);
              setShowResultModal(true);
            }}
          >
            <View style={styles.historyHeader}>
              <Text style={styles.historyDate}>
                {result.timestamp.toLocaleDateString('zh-CN')}
              </Text>
              <View;
                style={[
                  styles.confidenceBadge,
                  { backgroundColor: getConfidenceColor(result.confidence) },
                ]}
              >
                <Text style={styles.confidenceText}>
                  {Math.round(result.confidence * 100)}%
                </Text>
              </View>
            </View>
            <Text style={styles.historyResult} numberOfLines={2}>
              {result.result}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
    );
  };

  // 获取置信度颜色
  const getConfidenceColor = (confidence: number): string => {
    if (confidence >= 0.8) return '#4CAF50';
    if (confidence >= 0.6) return '#FF9800';
    return '#F44336';
  };

  // 渲染结果模态框
  const renderResultModal = () => {
    if (!currentResult || !serviceInfo) return null;

    return (
      <Modal;
        visible={showResultModal}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setShowResultModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View;
              style={[
                styles.modalHeader,
                { backgroundColor: serviceInfo.colors.primary },
              ]}
            >
              <Text style={styles.modalTitle}>诊断结果</Text>
              <TouchableOpacity;
                style={styles.modalCloseButton}
                onPress={() => setShowResultModal(false)}
              >
                <Icon name="close" size={24} color="#FFFFFF" />
              </TouchableOpacity>
            </View>

            <ScrollView style={styles.modalBody}>
              <View style={styles.resultSection}>
                <Text style={styles.resultTitle}>诊断结论</Text>
                <Text style={styles.resultText}>{currentResult.result}</Text>
              </View>

              <View style={styles.resultSection}>
                <Text style={styles.resultTitle}>置信度</Text>
                <View style={styles.confidenceContainer}>
                  <View style={styles.confidenceBar}>
                    <View;
                      style={[
                        styles.confidenceFill,
                        {
                          width: `${currentResult.confidence * 100}%`,
                          backgroundColor: getConfidenceColor(
                            currentResult.confidence;
                          ),
                        },
                      ]}
                    />
                  </View>
                  <Text style={styles.confidencePercentage}>
                    {Math.round(currentResult.confidence * 100)}%
                  </Text>
                </View>
              </View>

              {currentResult.details?.recommendations && (
                <View style={styles.resultSection}>
                  <Text style={styles.resultTitle}>建议</Text>
                  {currentResult.details.recommendations.map(rec: string, index: number) => (
                      <View key={index} style={styles.recommendationItem}>
                        <Icon;
                          name="check-circle"
                          size={16}
                          color={serviceInfo.colors.primary}
                        />
                        <Text style={styles.recommendationText}>{rec}</Text>
                      </View>
                    )
                  )}
                </View>
              )}

              <View style={styles.resultSection}>
                <Text style={styles.resultTitle}>诊断时间</Text>
                <Text style={styles.resultText}>
                  {currentResult.timestamp.toLocaleString('zh-CN')}
                </Text>
              </View>
            </ScrollView>
          </View>
        </View>
      </Modal>
    );
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <StatusBar barStyle="light-content" backgroundColor="#4A90E2" />
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#4A90E2" />
          <Text style={styles.loadingText}>加载中...</Text>
        </View>
      </SafeAreaView>
    );
  }

  if (!serviceInfo) {
    return (
      <SafeAreaView style={styles.container}>
        <StatusBar barStyle="light-content" backgroundColor="#F44336" />
        <View style={styles.errorContainer}>
          <Icon name="alert-circle" size={64} color="#F44336" />
          <Text style={styles.errorTitle}>服务不存在</Text>
          <Text style={styles.errorSubtitle}>请检查服务类型是否正确</Text>
          <TouchableOpacity;
            style={styles.backButton}
            onPress={() => navigation.goBack()}
          >
            <Text style={styles.backButtonText}>返回</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  const colors = serviceInfo.colors;

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor={colors.primary} />

      {/* 头部 */}
      <View style={[styles.header, { backgroundColor: colors.primary }]}>
        <TouchableOpacity;
          style={styles.headerBackButton}
          onPress={() => navigation.goBack()}
        >
          <Icon name="arrow-left" size={24} color="#FFFFFF" />
        </TouchableOpacity>

        <View style={styles.headerInfo}>
          <Text style={styles.headerIcon}>{serviceInfo.icon}</Text>
          <View style={styles.headerTextContainer}>
            <Text style={styles.headerTitle}>{serviceInfo.name}</Text>
            <Text style={styles.headerSubtitle}>
              {serviceInfo.status === 'active' ? '服务正常' : '服务维护中'}
            </Text>
          </View>
        </View>

        <TouchableOpacity style={styles.moreButton}>
          <Icon name="dots-vertical" size={24} color="#FFFFFF" />
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* 服务描述 */}
        <View style={styles.descriptionContainer}>
          <Text style={styles.descriptionText}>{serviceInfo.description}</Text>
        </View>

        {/* 服务能力 */}
        {renderCapabilities()}

        {/* 开始诊断按钮 */}
        <View style={styles.actionContainer}>
          <TouchableOpacity;
            style={[
              styles.diagnosisButton,
              { backgroundColor: colors.primary },
              diagnosing && styles.diagnosisButtonDisabled,
            ]}
            onPress={startDiagnosis}
            disabled={diagnosing}
          >
            {diagnosing ? (
              <ActivityIndicator size="small" color="#FFFFFF" />
            ) : (
              <Icon name="play-circle" size={24} color="#FFFFFF" />
            )}
            <Text style={styles.diagnosisButtonText}>
              {diagnosing ? '诊断中...' : '开始诊断'}
            </Text>
          </TouchableOpacity>
        </View>

        {/* 诊断历史 */}
        {renderDiagnosisHistory()}
      </ScrollView>

      {/* 结果模态框 */}
      {renderResultModal()}
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {,
  flex: 1,
    backgroundColor: '#F8F9FA',
  },
  loadingContainer: {,
  flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {,
  marginTop: 10,
    fontSize: 16,
    color: '#666',
  },
  errorContainer: {,
  flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 40,
  },
  errorTitle: {,
  fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 16,
    marginBottom: 8,
  },
  errorSubtitle: {,
  fontSize: 14,
    color: '#666',
    textAlign: 'center',
    marginBottom: 24,
  },
  backButton: {,
  backgroundColor: '#4A90E2',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  backButtonText: {,
  color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  header: {,
  flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  headerBackButton: {,
  padding: 8,
    marginRight: 8,
  },
  headerInfo: {,
  flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
  },
  headerIcon: {,
  fontSize: 32,
    marginRight: 12,
  },
  headerTextContainer: {,
  flex: 1,
  },
  headerTitle: {,
  fontSize: 18,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  headerSubtitle: {,
  fontSize: 12,
    color: '#E3F2FD',
    marginTop: 2,
  },
  moreButton: {,
  padding: 8,
  },
  content: {,
  flex: 1,
  },
  descriptionContainer: {,
  margin: 16,
    padding: 16,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  descriptionText: {,
  fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
  capabilitiesContainer: {,
  margin: 16,
    marginTop: 0,
  },
  sectionTitle: {,
  fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 12,
  },
  capabilitiesGrid: {,
  flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  capabilityItem: {,
  paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    marginRight: 8,
    marginBottom: 8,
  },
  capabilityText: {,
  fontSize: 12,
    fontWeight: '500',
  },
  actionContainer: {,
  margin: 16,
    marginTop: 0,
  },
  diagnosisButton: {,
  flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  diagnosisButtonDisabled: {,
  opacity: 0.7,
  },
  diagnosisButtonText: {,
  color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8,
  },
  historyContainer: {,
  margin: 16,
    marginTop: 0,
  },
  historyItem: {,
  backgroundColor: '#FFFFFF',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  historyHeader: {,
  flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  historyDate: {,
  fontSize: 12,
    color: '#999',
  },
  confidenceBadge: {,
  paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 10,
  },
  confidenceText: {,
  fontSize: 10,
    color: '#FFFFFF',
    fontWeight: '600',
  },
  historyResult: {,
  fontSize: 14,
    color: '#333',
    lineHeight: 20,
  },
  emptyHistory: {,
  alignItems: 'center',
    paddingVertical: 40,
  },
  emptyHistoryText: {,
  fontSize: 16,
    color: '#666',
    marginTop: 12,
    fontWeight: '500',
  },
  emptyHistorySubtext: {,
  fontSize: 12,
    color: '#999',
    marginTop: 4,
  },
  modalOverlay: {,
  flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {,
  backgroundColor: '#FFFFFF',
    borderRadius: 16,
    width: width * 0.9,
    maxHeight: height * 0.8,
    overflow: 'hidden',
  },
  modalHeader: {,
  flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 16,
  },
  modalTitle: {,
  fontSize: 18,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  modalCloseButton: {,
  padding: 4,
  },
  modalBody: {,
  padding: 20,
  },
  resultSection: {,
  marginBottom: 20,
  },
  resultTitle: {,
  fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  resultText: {,
  fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
  confidenceContainer: {,
  flexDirection: 'row',
    alignItems: 'center',
  },
  confidenceBar: {,
  flex: 1,
    height: 8,
    backgroundColor: '#E0E0E0',
    borderRadius: 4,
    marginRight: 12,
  },
  confidenceFill: {,
  height: '100%',
    borderRadius: 4,
  },
  confidencePercentage: {,
  fontSize: 14,
    fontWeight: '600',
    color: '#333',
    minWidth: 40,
  },
  recommendationItem: {,
  flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  recommendationText: {,
  fontSize: 14,
    color: '#666',
    marginLeft: 8,
    flex: 1,
  },
});

export default DiagnosisServiceScreen;
