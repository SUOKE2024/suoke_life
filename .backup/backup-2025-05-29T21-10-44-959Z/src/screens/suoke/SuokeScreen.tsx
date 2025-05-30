import {
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from '../../components/common/Icon';
import { colors } from '../../constants/theme';
import XiaoaiChatInterface from './components/XiaoaiChatInterface';
import DiagnosisModal from './components/DiagnosisModal';
import EcoServices from './components/EcoServices';
import SystemMonitorDashboard from './components/SystemMonitorDashboard';
import WellnessExperience from './components/WellnessExperience';
import AgentChatInterface, { AgentType } from '../../components/common/AgentChatInterface';
import { FourDiagnosisNavigator } from './components/FourDiagnosisNavigator';
import { EcoLifestyleNavigator } from './components/EcoLifestyleNavigator';
import { DiagnosisType } from '../../types';



import React, { useState } from 'react';
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  FlatList,
  Modal,
  ActivityIndicator,
} from 'react-native';

// 服务类型
interface ServiceItem {
  id: string;
  title: string;
  subtitle: string;
  icon: string;
  color: string;
  category: 'diagnosis' | 'product' | 'service' | 'subscription' | 'appointment' | 'market' | 'custom' | 'supplier';
  description: string;
  features: string[];
  price?: string;
  available: boolean;
}

// 五诊服务配置（从四诊升级为五诊）
const DIAGNOSIS_SERVICES: ServiceItem[] = [
  {
    id: 'look_diagnosis',
    title: '望诊服务',
    subtitle: '面色舌象智能分析',
    icon: 'eye',
    color: '#007AFF',
    category: 'diagnosis',
    description: '通过AI视觉技术分析面色、舌象、体态等外在表现',
    features: ['面色分析', '舌象检测', '体态评估', '精神状态评估'],
    price: '¥99',
    available: true,
  },
  {
    id: 'listen_diagnosis',
    title: '闻诊服务',
    subtitle: '声音气味智能识别',
    icon: 'ear-hearing',
    color: '#34C759',
    category: 'diagnosis',
    description: '通过声纹分析和气味识别技术进行健康评估',
    features: ['语音分析', '呼吸音检测', '咳嗽分析', '气味识别'],
    price: '¥79',
    available: true,
  },
  {
    id: 'inquiry_diagnosis',
    title: '问诊服务',
    subtitle: '智能问诊对话',
    icon: 'comment-question',
    color: '#FF9500',
    category: 'diagnosis',
    description: '基于中医理论的智能问诊系统，全面了解症状和病史',
    features: ['症状询问', '病史采集', '生活习惯评估', '家族史分析'],
    price: '¥59',
    available: true,
  },
  {
    id: 'palpation_diagnosis',
    title: '切诊服务',
    subtitle: '脉象触诊检测',
    icon: 'hand-back-right',
    color: '#FF2D92',
    category: 'diagnosis',
    description: '结合传感器技术的现代化脉诊和触诊服务',
    features: ['脉象分析', '腹部触诊', '穴位检查', '皮肤触感'],
    price: '¥129',
    available: true,
  },
  {
    id: 'calculation_diagnosis',
    title: '算诊服务',
    subtitle: '时间医学智能推演',
    icon: 'calculator',
    color: '#8E44AD',
    category: 'diagnosis',
    description: '基于传统中医算诊理论，结合五运六气、八字八卦等进行个性化健康分析',
    features: ['五运六气分析', '八字体质推算', '八卦体质分析', '子午流注时间医学'],
    price: '¥149',
    available: true,
  },
];

// 其他服务配置
const OTHER_SERVICES: ServiceItem[] = [
  {
    id: 'health_products',
    title: '健康产品',
    subtitle: '精选健康商品',
    icon: 'package-variant',
    color: '#8E44AD',
    category: 'product',
    description: '经过专业筛选的健康产品和保健用品',
    features: ['中药材', '保健品', '健康器械', '养生用品'],
    available: true,
  },
  {
    id: 'medical_services',
    title: '医疗服务',
    subtitle: '专业医疗咨询',
    icon: 'medical-bag',
    color: '#E74C3C',
    category: 'service',
    description: '提供专业的医疗咨询和健康管理服务',
    features: ['专家咨询', '健康评估', '治疗方案', '康复指导'],
    available: true,
  },
  {
    id: 'health_subscription',
    title: '健康订阅',
    subtitle: '个性化健康计划',
    icon: 'calendar-check',
    color: '#3498DB',
    category: 'subscription',
    description: '定制化的健康管理订阅服务',
    features: ['月度体检', '营养配餐', '运动计划', '健康报告'],
    price: '¥299/月',
    available: true,
  },
  {
    id: 'appointment_booking',
    title: '预约服务',
    subtitle: '便捷预约挂号',
    icon: 'calendar-clock',
    color: '#F39C12',
    category: 'appointment',
    description: '快速预约医生和健康服务',
    features: ['在线挂号', '专家预约', '体检预约', '上门服务'],
    available: true,
  },
  {
    id: 'health_market',
    title: '健康市集',
    subtitle: '健康生活商城',
    icon: 'store',
    color: '#27AE60',
    category: 'market',
    description: '一站式健康生活用品购物平台',
    features: ['有机食品', '运动器材', '美容护肤', '家居健康'],
    available: true,
  },
  {
    id: 'custom_service',
    title: '定制服务',
    subtitle: '个性化健康方案',
    icon: 'cog',
    color: '#9B59B6',
    category: 'custom',
    description: '根据个人需求定制专属健康解决方案',
    features: ['体质分析', '方案定制', '跟踪服务', '效果评估'],
    price: '¥999起',
    available: true,
  },
  {
    id: 'supplier_network',
    title: '供应商网络',
    subtitle: '优质供应商合作',
    icon: 'truck',
    color: '#34495E',
    category: 'supplier',
    description: '与优质健康产品供应商建立合作关系',
    features: ['供应商认证', '质量保证', '物流配送', '售后服务'],
    available: true,
  },
];

const SuokeScreen: React.FC = () => {
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [xiaoaiChatVisible, setXiaoaiChatVisible] = useState(false);
  const [xiaokeChatVisible, setXiaokeChatVisible] = useState(false);
  const [accessibilityEnabled, setAccessibilityEnabled] = useState(false);
  const [diagnosisModalVisible, setDiagnosisModalVisible] = useState(false);
  const [selectedDiagnosisService, setSelectedDiagnosisService] = useState<ServiceItem | null>(null);
  const [loading, setLoading] = useState(false);
  const [ecoServicesVisible, setEcoServicesVisible] = useState(false);
  const [monitorDashboardVisible, setMonitorDashboardVisible] = useState(false);
  const [wellnessExperienceVisible, setWellnessExperienceVisible] = useState(false);
  const [fourDiagnosisVisible, setFourDiagnosisVisible] = useState(false);
  const [ecoLifestyleVisible, setEcoLifestyleVisible] = useState(false);

  // 所有服务
  const allServices = useMemo(() => useMemo(() => [...DIAGNOSIS_SERVICES, ...OTHER_SERVICES], []), []);

  // 过滤服务
  const filteredServices = useMemo(() => useMemo(() => selectedCategory === 'all' 
    ? allServices 
    : allServices.filter(service => service.category === selectedCategory), []), []);

  // 分类选项
  const categories = useMemo(() => useMemo(() => [
    { key: 'all', label: '全部', icon: 'view-grid' },
    { key: 'diagnosis', label: '五诊', icon: 'stethoscope' },
    { key: 'eco', label: '生态服务', icon: 'leaf' },
    { key: 'product', label: '产品', icon: 'package-variant' },
    { key: 'service', label: '服务', icon: 'medical-bag' },
    { key: 'subscription', label: '订阅', icon: 'calendar-check' },
    { key: 'appointment', label: '预约', icon: 'calendar-clock' },
    { key: 'market', label: '市集', icon: 'store' },
    { key: 'custom', label: '定制', icon: 'cog' },
    { key: 'supplier', label: '供应商', icon: 'truck' },
  ], []), []);

  // 与小艾对话
  const chatWithXiaoai = useMemo(() => useMemo(() => async () => {
    try {
      console.log('🤖 启动小艾健康诊断对话...'), []), []);
      
      // 初始化小艾对话会话
      const response = useMemo(() => useMemo(() => await fetch('http://localhost:8080/api/agents/xiaoai/init', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          userId: 'current_user_id',
          sessionType: 'health_diagnosis',
        }),
      }), []), []);

      if (response.ok) {
        const data = useMemo(() => useMemo(() => await response.json(), []), []);
        console.log('✅ 小艾对话会话初始化成功:', data);
        setXiaoaiChatVisible(true);
      } else {
        throw new Error('初始化对话会话失败');
      }
    } catch (error) {
      console.error('❌ 启动小艾对话失败:', error);
      Alert.alert('连接失败', '无法连接到小艾服务，请稍后重试');
    }
  };

  // 与小克对话
  const chatWithXiaoke = useMemo(() => useMemo(() => useCallback( () => {, []), []), []);
    Alert.alert(
      '与小克对话',
      '小克是您的专业医疗服务管理助手，可以帮助您：\n\n• 选择合适的诊断服务\n• 预约医疗服务\n• 管理健康订阅\n• 推荐健康产品\n\n是否开始对话？',
      [
        { text: '取消', style: 'cancel' },
        { text: '开始对话', onPress: () => startXiaokeChat() },
      ]
    );
  };

  // 开始与小克对话
  const startXiaokeChat = useMemo(() => useMemo(() => useCallback( () => {, []), []), []);
    setXiaokeChatVisible(true);
    // 这里将集成实际的小克智能体服务
    console.log('Starting chat with Xiaoke agent');
  };

  // 选择服务
  const selectService = useMemo(() => useMemo(() => useCallback( (service: ServiceItem) => {, []), []), []);
    if (service.category === 'diagnosis') {
      // 五诊服务使用专门的模态框
      setSelectedDiagnosisService(service);
      setDiagnosisModalVisible(true);
    } else {
      // 其他服务显示信息弹窗
      Alert.alert(
        service.title,
        `${service.description}\n\n包含功能：\n${service.features.map(f => `• ${f}`).join('\n')}${service.price ? `\n\n价格：${service.price}` : ''}\n\n是否使用此服务？`,
        [
          { text: '取消', style: 'cancel' },
          { text: '使用服务', onPress: () => useService(service) },
        ]
      );
    }
  };

  // 开始诊断服务（现在由DiagnosisModal处理）
  const startDiagnosisService = useMemo(() => useMemo(() => async (service: ServiceItem) => {
    // 这个函数现在主要用于向后兼容，实际逻辑在DiagnosisModal中
    console.log(`Starting diagnosis service: ${service.id}`), []), []);
  };

  // 获取诊断类型
  const getDiagnosisType = useMemo(() => useMemo(() => (serviceId: string): DiagnosisType => {
    switch (serviceId) {
      case 'look_diagnosis':
        return 'inspection', []), []);
      case 'listen_diagnosis':
        return 'auscultation';
      case 'inquiry_diagnosis':
        return 'inquiry';
      case 'palpation_diagnosis':
        return 'palpation';
      case 'calculation_diagnosis':
        return 'calculation';
      default:
        return 'inquiry';
    }
  };

  // 使用服务
  const useService = useMemo(() => useMemo(() => useCallback( (service: ServiceItem) => {, []), []), []);
    Alert.alert('服务启动', `正在为您准备${service.title}服务...`);
    // 这里将集成实际的服务功能
    console.log(`Using service: ${service.id}`);
  };

  // 渲染分类过滤器
  // TODO: 将内联组件移到组件外部
const renderCategoryFilter = useMemo(() => useMemo(() => () => (
    <ScrollView 
      horizontal 
      showsHorizontalScrollIndicator={false}
      style={styles.categoryContainer}
      contentContainerStyle={styles.categoryContent}
    >
      {categories.map(category => (
        <TouchableOpacity
          key={category.key}
          style={[
            styles.categoryButton,
            selectedCategory === category.key && styles.activeCategoryButton,
          ]}
          onPress={() => {
            if (category.key === 'eco') {
              setEcoServicesVisible(true), []), []);
            } else {
              setSelectedCategory(category.key);
            }
          }}
        >
          <Icon 
            name={category.icon} 
            size={16} 
            color={selectedCategory === category.key ? 'white' : colors.textSecondary} 
          />
          <Text style={[
            styles.categoryText,
            selectedCategory === category.key && styles.activeCategoryText,
          ]}>
            {category.label}
          </Text>
        </TouchableOpacity>
      ))}
    </ScrollView>
  );

  // 渲染服务卡片
  const renderServiceCard = useMemo(() => useMemo(() => ({ item }: { item: ServiceItem }) => (
    <TouchableOpacity 
      style={[styles.serviceCard, { borderLeftColor: item.color }]}
      onPress={() => selectService(item)}
    >
      <View style={styles.cardHeader}>
        <View style={[styles.iconContainer, { backgroundColor: item.color + '20' }]}>
          <Icon name={item.icon} size={24} color={item.color} />
        </View>
        <View style={styles.cardTitleContainer}>
          <Text style={styles.cardTitle}>{item.title}</Text>
          <Text style={styles.cardSubtitle}>{item.subtitle}</Text>
        </View>
        {item.price && (
          <Text style={[styles.priceText, { color: item.color }]}>{item.price}</Text>
        )}
      </View>

      <Text style={styles.cardDescription}>{item.description}</Text>

      <View style={styles.featuresContainer}>
        {item.features.slice(0, 3).map((feature, index) => (
          <View key={index} style={styles.featureItem}>
            <Icon name="check-circle" size={12} color={item.color} />
            <Text style={styles.featureText}>{feature}</Text>
          </View>
        ))}
        {item.features.length > 3 && (
          <Text style={styles.moreFeatures}>+{item.features.length - 3} 更多功能</Text>
        )}
      </View>

      <View style={styles.cardFooter}>
        <View style={[styles.statusBadge, { backgroundColor: item.available ? '#E8F5E8' : '#FFF3E0' }]}>
          <Text style={[styles.statusText, { color: item.available ? '#27AE60' : '#F39C12' }]}>
            {item.available ? '可用' : '准备中'}
          </Text>
        </View>
        <Icon name="chevron-right" size={20} color={colors.textSecondary} />
      </View>
    </TouchableOpacity>
  ), []), []);

  return (
    <SafeAreaView style={styles.container}>
      {/* 头部 */}
      <View style={styles.header}>
        <View>
          <Text style={styles.title}>SUOKE 服务</Text>
          <Text style={styles.subtitle}>专业健康服务平台</Text>
        </View>
        <View style={styles.chatButtons}>
          <TouchableOpacity style={styles.xiaokeChatButton} onPress={chatWithXiaoai}>
            <Text style={styles.xiaokeChatEmoji}>🤖</Text>
            <Text style={styles.xiaokeChatText}>小艾</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.xiaokeChatButton} onPress={chatWithXiaoke}>
            <Text style={styles.xiaokeChatEmoji}>👨‍⚕️</Text>
            <Text style={styles.xiaokeChatText}>小克</Text>
          </TouchableOpacity>
          <TouchableOpacity 
            style={styles.xiaokeChatButton} 
            onPress={() => setFourDiagnosisVisible(true)}
          >
            <Text style={styles.xiaokeChatEmoji}>🔍</Text>
            <Text style={styles.xiaokeChatText}>四诊</Text>
          </TouchableOpacity>
          <TouchableOpacity 
            style={styles.xiaokeChatButton} 
            onPress={() => setEcoLifestyleVisible(true)}
          >
            <Text style={styles.xiaokeChatEmoji}>🌿</Text>
            <Text style={styles.xiaokeChatText}>生态</Text>
          </TouchableOpacity>
          <TouchableOpacity 
            style={styles.xiaokeChatButton} 
            onPress={() => setMonitorDashboardVisible(true)}
          >
            <Text style={styles.xiaokeChatEmoji}>📊</Text>
            <Text style={styles.xiaokeChatText}>监控</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* 小克助手卡片 */}
      <TouchableOpacity style={styles.xiaokeCard} onPress={chatWithXiaoke}>
        <View style={styles.xiaokeInfo}>
          <Text style={styles.xiaokeEmoji}>👨‍⚕️</Text>
          <View style={styles.xiaokeTextContainer}>
            <Text style={styles.xiaokeName}>小克 - 医疗服务助手</Text>
            <Text style={styles.xiaokeDesc}>为您提供专业的医疗服务管理和健康咨询</Text>
          </View>
        </View>
        <View style={styles.onlineStatus}>
          <View style={styles.onlineDot} />
          <Text style={styles.onlineText}>在线</Text>
        </View>
      </TouchableOpacity>

      {/* 分类过滤器 */}
      {renderCategoryFilter()}

      {/* 服务列表 */}
      <FlatList
        data={filteredServices}
        keyExtractor={item => item.id}
        renderItem={renderServiceCard}
        style={styles.servicesList}
        showsVerticalScrollIndicator={false}
        contentContainerStyle={styles.servicesContent}
      />

      {/* 小艾聊天界面 */}
      <XiaoaiChatInterface
        visible={xiaoaiChatVisible}
        onClose={() => setXiaoaiChatVisible(false)}
        userId="current_user"
      />

      {/* 五诊模态框 */}
      {selectedDiagnosisService && (
        <DiagnosisModal
          visible={diagnosisModalVisible}
          onClose={() => {
            setDiagnosisModalVisible(false);
            setSelectedDiagnosisService(null);
          }}
          diagnosisType={getDiagnosisType(selectedDiagnosisService.id)}
          title={selectedDiagnosisService.title}
          description={selectedDiagnosisService.description}
        />
      )}

      {/* 生态服务模态框 */}
      <EcoServices
        visible={ecoServicesVisible}
        onClose={() => setEcoServicesVisible(false)}
      />

      {/* 小克对话界面 */}
      <AgentChatInterface
        visible={xiaokeChatVisible}
        onClose={() => setXiaokeChatVisible(false)}
        agentType="xiaoke"
        userId="current_user_id"
        accessibilityEnabled={accessibilityEnabled}
      />

      {/* 系统监控仪表板 */}
      <SystemMonitorDashboard
        visible={monitorDashboardVisible}
        onClose={() => setMonitorDashboardVisible(false)}
      />

      {/* 山水养生体验 */}
      <WellnessExperience
        visible={wellnessExperienceVisible}
        onClose={() => setWellnessExperienceVisible(false)}
      />

      {/* 四诊系统导航 */}
      <FourDiagnosisNavigator
        visible={fourDiagnosisVisible}
        onClose={() => setFourDiagnosisVisible(false)}
        onDiagnosisSelect={(diagnosisId) => {
          console.log('选择诊断方法:', diagnosisId);
          // 这里可以导航到具体的诊断界面
        }}
      />

      {/* 生态生活导航 */}
      <EcoLifestyleNavigator
        visible={ecoLifestyleVisible}
        onClose={() => setEcoLifestyleVisible(false)}
        onServiceSelect={(serviceId) => {
          console.log('选择生态服务:', serviceId);
          // 这里可以导航到具体的服务界面
        }}
      />

      {/* 诊断加载中 */}
      {loading && (
        <Modal
          visible={loading}
          transparent={true}
          animationType="fade"
        >
          <View style={styles.loadingOverlay}>
            <ActivityIndicator size="large" color={colors.primary} />
          </View>
        </Modal>
      )}
    </SafeAreaView>
  );
};

const styles = useMemo(() => useMemo(() => StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 15,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: colors.textPrimary,
  },
  subtitle: {
    fontSize: 14,
    color: colors.textSecondary,
    marginTop: 2,
  },
  chatButtons: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  xiaokeChatButton: {
    alignItems: 'center',
    padding: 8,
    marginLeft: 8,
  },
  xiaokeChatEmoji: {
    fontSize: 24,
  },
  xiaokeChatText: {
    fontSize: 12,
    color: colors.primary,
    fontWeight: '600',
    marginTop: 2,
  },
  xiaokeCard: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    margin: 15,
    padding: 15,
    backgroundColor: colors.primary + '10',
    borderRadius: 12,
    borderLeftWidth: 4,
    borderLeftColor: colors.primary,
  },
  xiaokeInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  xiaokeEmoji: {
    fontSize: 32,
    marginRight: 12,
  },
  xiaokeTextContainer: {
    flex: 1,
  },
  xiaokeName: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: 4,
  },
  xiaokeDesc: {
    fontSize: 12,
    color: colors.textSecondary,
  },
  onlineStatus: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  onlineDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#34C759',
    marginRight: 4,
  },
  onlineText: {
    fontSize: 12,
    color: '#34C759',
    fontWeight: '600',
  },
  categoryContainer: {
    maxHeight: 50,
  },
  categoryContent: {
    paddingHorizontal: 15,
    paddingVertical: 10,
  },
  categoryButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 6,
    marginRight: 8,
    borderRadius: 15,
    backgroundColor: colors.surface,
  },
  activeCategoryButton: {
    backgroundColor: colors.primary,
  },
  categoryText: {
    marginLeft: 4,
    fontSize: 12,
    color: colors.textSecondary,
  },
  activeCategoryText: {
    color: 'white',
    fontWeight: '600',
  },
  servicesList: {
    flex: 1,
  },
  servicesContent: {
    padding: 15,
  },
  serviceCard: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: 15,
    marginBottom: 15,
    borderLeftWidth: 4,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  iconContainer: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  cardTitleContainer: {
    flex: 1,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: 2,
  },
  cardSubtitle: {
    fontSize: 12,
    color: colors.textSecondary,
  },
  priceText: {
    fontSize: 14,
    fontWeight: 'bold',
  },
  cardDescription: {
    fontSize: 14,
    color: colors.textSecondary,
    marginBottom: 10,
    lineHeight: 20,
  },
  featuresContainer: {
    marginBottom: 10,
  },
  featureItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  featureText: {
    fontSize: 12,
    color: colors.textSecondary,
    marginLeft: 6,
  },
  moreFeatures: {
    fontSize: 12,
    color: colors.primary,
    fontStyle: 'italic',
    marginTop: 4,
  },
  cardFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 10,
  },
  statusText: {
    fontSize: 10,
    fontWeight: '600',
  },
  loadingOverlay: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
  },
}), []), []);

export default SuokeScreen;
