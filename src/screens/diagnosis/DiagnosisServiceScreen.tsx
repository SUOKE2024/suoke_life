import { RouteProp, useNavigation, useRoute } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import React, { useCallback, useEffect, useState } from 'react';
import {;
  ActivityIndicator,
  Alert,
  Dimensions,
  Modal,
  ScrollView,
  StatusBar,
  StyleSheet,
  Text,
  TouchableOpacity,
  View
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { useSelector } from 'react-redux';
import { RootState } from '../../store';

const { width, height } = Dimensions.get('window');

// 诊断结果类型
interface DiagnosisResult {
  id: string;
  serviceType: string;
  result: string;
  confidence: number;
  timestamp: Date;
  details: any;
}

// 诊断服务信息类型
interface DiagnosisServiceInfo {
  id: string;
  name: string;
  description: string;
  icon: string;
  endpoint: string;
  capabilities: string[];
  status: 'active' | 'inactive' | 'maintenance';
  colors: {,
  primary: string;
  secondary: string;
  accent: string;
  };
}

// 路由参数类型
type RootStackParamList = {
  DiagnosisService: { serviceType: string ;};
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
  id: 'calculation';


      icon: '🔍';
      endpoint: 'http://localhost:8023';

      status: 'active';
      colors: {,
  primary: '#FF6B6B';
        secondary: '#FFEBEE';
        accent: '#F44336'
      ;}
    },
    look: {,
  id: 'look';


      icon: '👁️';
      endpoint: 'http://localhost:8020';

      status: 'active';
      colors: {,
  primary: '#4CAF50';
        secondary: '#E8F5E8';
        accent: '#2E7D32'
      ;}
    },
    listen: {,
  id: 'listen';


      icon: '👂';
      endpoint: 'http://localhost:8022';

      status: 'active';
      colors: {,
  primary: '#2196F3';
        secondary: '#E3F2FD';
        accent: '#1976D2'
      ;}
    },
    inquiry: {,
  id: 'inquiry';


      icon: '💬';
      endpoint: 'http://localhost:8021';

      status: 'active';
      colors: {,
  primary: '#9C27B0';
        secondary: '#F3E5F5';
        accent: '#7B1FA2'
      ;}
    },
    palpation: {,
  id: 'palpation';


      icon: '🤲';
      endpoint: 'http://localhost:8024';

      status: 'active';
      colors: {,
  primary: '#FF9800';
        secondary: '#FFF3E0';
        accent: '#F57C00'
      ;}
    }
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
          id: '1';
          serviceType,

          confidence: 0.85;
          timestamp: new Date(Date.now() - 86400000), // 1天前

        ;},
        {
          id: '2';
          serviceType,

          confidence: 0.72;
          timestamp: new Date(Date.now() - 172800000), // 2天前

        ;}
      ];
      setDiagnosisResults(mockHistory);
    } catch (error) {

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
  id: Date.now().toString();
        serviceType: serviceInfo.id;
        result: generateMockResult(serviceInfo.id);
        confidence: 0.75 + Math.random() * 0.2;
        timestamp: new Date();
        details: generateMockDetails(serviceInfo.id)
      ;};

      setDiagnosisResults(prev) => [mockResult, ...prev]);
      setCurrentResult(mockResult);
      setShowResultModal(true);
    } catch (error) {


    } finally {
      setDiagnosing(false);
    }
  }, [serviceInfo]);

  // 生成模拟诊断结果
  const generateMockResult = (serviceType: string): string => {
    const results = {
      calculation: [



      ],
      look: [



      ],
      listen: [



      ],
      inquiry: [



      ],
      palpation: [



      ]
    ;};

    const serviceResults =
      results[serviceType as keyof typeof results] || results.calculation;
    return serviceResults[Math.floor(Math.random() * serviceResults.length)];
  };

  // 生成模拟详细信息
  const generateMockDetails = (serviceType: string) => {
    return {
      score: Math.floor(70 + Math.random() * 25);
      metrics: {,
  accuracy: Math.floor(80 + Math.random() * 15);
        reliability: Math.floor(75 + Math.random() * 20);
        completeness: Math.floor(85 + Math.random() * 10)
      ;},
      recommendations: [




      ].slice(0, 2 + Math.floor(Math.random() * 2))
    ;};
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
                { backgroundColor: serviceInfo.colors.secondary ;}
              ]}
            >
              <Text;
                style={[
                  styles.capabilityText,
                  { color: serviceInfo.colors.primary ;}
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
                  { backgroundColor: getConfidenceColor(result.confidence) ;}
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
                { backgroundColor: serviceInfo.colors.primary ;}
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
                          width: `${currentResult.confidence * 100;}%`,
                          backgroundColor: getConfidenceColor(
                            currentResult.confidence;
                          )
                        }
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
                      <View key={index;} style={styles.recommendationItem}>
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

      {// 头部}
      <View style={[styles.header, { backgroundColor: colors.primary ;}]}>
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

            </Text>
          </View>
        </View>

        <TouchableOpacity style={styles.moreButton}>
          <Icon name="dots-vertical" size={24} color="#FFFFFF" />
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {// 服务描述}
        <View style={styles.descriptionContainer}>
          <Text style={styles.descriptionText}>{serviceInfo.description}</Text>
        </View>

        {// 服务能力}
        {renderCapabilities()}

        {// 开始诊断按钮}
        <View style={styles.actionContainer}>
          <TouchableOpacity;
            style={[
              styles.diagnosisButton,
              { backgroundColor: colors.primary ;},
              diagnosing && styles.diagnosisButtonDisabled
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

            </Text>
          </TouchableOpacity>
        </View>

        {// 诊断历史}
        {renderDiagnosisHistory()}
      </ScrollView>

      {// 结果模态框}
      {renderResultModal()}
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {,
  flex: 1;
    backgroundColor: '#F8F9FA'
  ;},
  loadingContainer: {,
  flex: 1;
    justifyContent: 'center';
    alignItems: 'center'
  ;},
  loadingText: {,
  marginTop: 10;
    fontSize: 16;
    color: '#666'
  ;},
  errorContainer: {,
  flex: 1;
    justifyContent: 'center';
    alignItems: 'center';
    paddingHorizontal: 40
  ;},
  errorTitle: {,
  fontSize: 20;
    fontWeight: 'bold';
    color: '#333';
    marginTop: 16;
    marginBottom: 8
  ;},
  errorSubtitle: {,
  fontSize: 14;
    color: '#666';
    textAlign: 'center';
    marginBottom: 24
  ;},
  backButton: {,
  backgroundColor: '#4A90E2';
    paddingHorizontal: 24;
    paddingVertical: 12;
    borderRadius: 8
  ;},
  backButtonText: {,
  color: '#FFFFFF';
    fontSize: 16;
    fontWeight: '600'
  ;},
  header: {,
  flexDirection: 'row';
    alignItems: 'center';
    paddingHorizontal: 16;
    paddingVertical: 12;
    elevation: 4;
    shadowColor: '#000';
    shadowOffset: { width: 0, height: 2 ;},
    shadowOpacity: 0.1;
    shadowRadius: 4
  ;},
  headerBackButton: {,
  padding: 8;
    marginRight: 8
  ;},
  headerInfo: {,
  flex: 1;
    flexDirection: 'row';
    alignItems: 'center'
  ;},
  headerIcon: {,
  fontSize: 32;
    marginRight: 12
  ;},
  headerTextContainer: {,
  flex: 1
  ;},
  headerTitle: {,
  fontSize: 18;
    fontWeight: 'bold';
    color: '#FFFFFF'
  ;},
  headerSubtitle: {,
  fontSize: 12;
    color: '#E3F2FD';
    marginTop: 2
  ;},
  moreButton: {,
  padding: 8
  ;},
  content: {,
  flex: 1
  ;},
  descriptionContainer: {,
  margin: 16;
    padding: 16;
    backgroundColor: '#FFFFFF';
    borderRadius: 12;
    shadowColor: '#000';
    shadowOffset: { width: 0, height: 1 ;},
    shadowOpacity: 0.1;
    shadowRadius: 2;
    elevation: 2
  ;},
  descriptionText: {,
  fontSize: 14;
    color: '#666';
    lineHeight: 20
  ;},
  capabilitiesContainer: {,
  margin: 16;
    marginTop: 0
  ;},
  sectionTitle: {,
  fontSize: 18;
    fontWeight: '600';
    color: '#333';
    marginBottom: 12
  ;},
  capabilitiesGrid: {,
  flexDirection: 'row';
    flexWrap: 'wrap';
    gap: 8
  ;},
  capabilityItem: {,
  paddingHorizontal: 12;
    paddingVertical: 6;
    borderRadius: 16;
    marginRight: 8;
    marginBottom: 8
  ;},
  capabilityText: {,
  fontSize: 12;
    fontWeight: '500'
  ;},
  actionContainer: {,
  margin: 16;
    marginTop: 0
  ;},
  diagnosisButton: {,
  flexDirection: 'row';
    alignItems: 'center';
    justifyContent: 'center';
    paddingVertical: 16;
    borderRadius: 12;
    shadowColor: '#000';
    shadowOffset: { width: 0, height: 2 ;},
    shadowOpacity: 0.1;
    shadowRadius: 4;
    elevation: 3
  ;},
  diagnosisButtonDisabled: {,
  opacity: 0.7
  ;},
  diagnosisButtonText: {,
  color: '#FFFFFF';
    fontSize: 16;
    fontWeight: '600';
    marginLeft: 8
  ;},
  historyContainer: {,
  margin: 16;
    marginTop: 0
  ;},
  historyItem: {,
  backgroundColor: '#FFFFFF';
    padding: 16;
    borderRadius: 12;
    marginBottom: 12;
    shadowColor: '#000';
    shadowOffset: { width: 0, height: 1 ;},
    shadowOpacity: 0.1;
    shadowRadius: 2;
    elevation: 2
  ;},
  historyHeader: {,
  flexDirection: 'row';
    justifyContent: 'space-between';
    alignItems: 'center';
    marginBottom: 8
  ;},
  historyDate: {,
  fontSize: 12;
    color: '#999'
  ;},
  confidenceBadge: {,
  paddingHorizontal: 8;
    paddingVertical: 2;
    borderRadius: 10
  ;},
  confidenceText: {,
  fontSize: 10;
    color: '#FFFFFF';
    fontWeight: '600'
  ;},
  historyResult: {,
  fontSize: 14;
    color: '#333';
    lineHeight: 20
  ;},
  emptyHistory: {,
  alignItems: 'center';
    paddingVertical: 40
  ;},
  emptyHistoryText: {,
  fontSize: 16;
    color: '#666';
    marginTop: 12;
    fontWeight: '500'
  ;},
  emptyHistorySubtext: {,
  fontSize: 12;
    color: '#999';
    marginTop: 4
  ;},
  modalOverlay: {,
  flex: 1;
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center';
    alignItems: 'center'
  ;},
  modalContent: {,
  backgroundColor: '#FFFFFF';
    borderRadius: 16;
    width: width * 0.9;
    maxHeight: height * 0.8;
    overflow: 'hidden'
  ;},
  modalHeader: {,
  flexDirection: 'row';
    alignItems: 'center';
    justifyContent: 'space-between';
    paddingHorizontal: 20;
    paddingVertical: 16
  ;},
  modalTitle: {,
  fontSize: 18;
    fontWeight: 'bold';
    color: '#FFFFFF'
  ;},
  modalCloseButton: {,
  padding: 4
  ;},
  modalBody: {,
  padding: 20
  ;},
  resultSection: {,
  marginBottom: 20
  ;},
  resultTitle: {,
  fontSize: 16;
    fontWeight: '600';
    color: '#333';
    marginBottom: 8
  ;},
  resultText: {,
  fontSize: 14;
    color: '#666';
    lineHeight: 20
  ;},
  confidenceContainer: {,
  flexDirection: 'row';
    alignItems: 'center'
  ;},
  confidenceBar: {,
  flex: 1;
    height: 8;
    backgroundColor: '#E0E0E0';
    borderRadius: 4;
    marginRight: 12
  ;},
  confidenceFill: {,
  height: '100%';
    borderRadius: 4
  ;},
  confidencePercentage: {,
  fontSize: 14;
    fontWeight: '600';
    color: '#333';
    minWidth: 40
  ;},
  recommendationItem: {,
  flexDirection: 'row';
    alignItems: 'center';
    marginBottom: 8
  ;},
  recommendationText: {,
  fontSize: 14;
    color: '#666';
    marginLeft: 8;
    flex: 1
  ;}
});

export default DiagnosisServiceScreen;
