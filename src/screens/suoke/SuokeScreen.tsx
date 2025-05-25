import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  FlatList,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { colors } from '../../constants/theme';

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

// 四诊服务配置
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
    available: true
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
    available: true
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
    available: true
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
    available: true
  }
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
    available: true
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
    available: true
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
    available: true
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
    available: true
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
    available: true
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
    available: true
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
    available: true
  }
];

const SuokeScreen: React.FC = () => {
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [xiaokeChatVisible, setXiaokeChatVisible] = useState(false);

  // 所有服务
  const allServices = [...DIAGNOSIS_SERVICES, ...OTHER_SERVICES];

  // 过滤服务
  const filteredServices = selectedCategory === 'all' 
    ? allServices 
    : allServices.filter(service => service.category === selectedCategory);

  // 分类选项
  const categories = [
    { key: 'all', label: '全部', icon: 'view-grid' },
    { key: 'diagnosis', label: '四诊', icon: 'stethoscope' },
    { key: 'product', label: '产品', icon: 'package-variant' },
    { key: 'service', label: '服务', icon: 'medical-bag' },
    { key: 'subscription', label: '订阅', icon: 'calendar-check' },
    { key: 'appointment', label: '预约', icon: 'calendar-clock' },
    { key: 'market', label: '市集', icon: 'store' },
    { key: 'custom', label: '定制', icon: 'cog' },
    { key: 'supplier', label: '供应商', icon: 'truck' }
  ];

  // 与小克对话
  const chatWithXiaoke = () => {
    Alert.alert(
      '与小克对话',
      '小克是您的专业医疗服务管理助手，可以帮助您：\n\n• 选择合适的诊断服务\n• 预约医疗服务\n• 管理健康订阅\n• 推荐健康产品\n\n是否开始对话？',
      [
        { text: '取消', style: 'cancel' },
        { text: '开始对话', onPress: () => startXiaokeChat() }
      ]
    );
  };

  // 开始与小克对话
  const startXiaokeChat = () => {
    setXiaokeChatVisible(true);
    // 这里将集成实际的小克智能体服务
    console.log('Starting chat with Xiaoke agent');
  };

  // 选择服务
  const selectService = (service: ServiceItem) => {
    if (!service.available) {
      Alert.alert('服务暂不可用', '该服务正在准备中，敬请期待！');
      return;
    }

    if (service.category === 'diagnosis') {
      startDiagnosisService(service);
    } else {
      Alert.alert(
        service.title,
        `${service.description}\n\n主要功能：\n${service.features.map(f => `• ${f}`).join('\n')}\n\n${service.price ? `价格：${service.price}` : ''}`,
        [
          { text: '了解更多', onPress: () => console.log(`Learn more about ${service.id}`) },
          { text: '立即使用', onPress: () => useService(service) }
        ]
      );
    }
  };

  // 开始诊断服务
  const startDiagnosisService = (service: ServiceItem) => {
    Alert.alert(
      `开始${service.title}`,
      `${service.description}\n\n包含功能：\n${service.features.map(f => `• ${f}`).join('\n')}\n\n价格：${service.price}\n\n是否开始诊断？`,
      [
        { text: '取消', style: 'cancel' },
        { text: '开始诊断', onPress: () => performDiagnosis(service) }
      ]
    );
  };

  // 执行诊断
  const performDiagnosis = (service: ServiceItem) => {
    Alert.alert('诊断开始', `正在启动${service.title}，请按照指引完成诊断过程...`);
    // 这里将集成实际的四诊服务
    console.log(`Starting diagnosis service: ${service.id}`);
  };

  // 使用服务
  const useService = (service: ServiceItem) => {
    Alert.alert('服务启动', `正在为您准备${service.title}服务...`);
    // 这里将集成实际的服务功能
    console.log(`Using service: ${service.id}`);
  };

  // 渲染分类过滤器
  const renderCategoryFilter = () => (
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
            selectedCategory === category.key && styles.activeCategoryButton
          ]}
          onPress={() => setSelectedCategory(category.key)}
        >
          <Icon 
            name={category.icon} 
            size={16} 
            color={selectedCategory === category.key ? 'white' : colors.textSecondary} 
          />
          <Text style={[
            styles.categoryText,
            selectedCategory === category.key && styles.activeCategoryText
          ]}>
            {category.label}
          </Text>
        </TouchableOpacity>
      ))}
    </ScrollView>
  );

  // 渲染服务卡片
  const renderServiceCard = ({ item }: { item: ServiceItem }) => (
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
  );

  return (
    <SafeAreaView style={styles.container}>
      {/* 头部 */}
      <View style={styles.header}>
        <View>
          <Text style={styles.title}>SUOKE 服务</Text>
          <Text style={styles.subtitle}>专业健康服务平台</Text>
        </View>
        <TouchableOpacity style={styles.xiaokeChatButton} onPress={chatWithXiaoke}>
          <Text style={styles.xiaokeChatEmoji}>👨‍⚕️</Text>
          <Text style={styles.xiaokeChatText}>小克</Text>
        </TouchableOpacity>
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
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
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
    color: colors.text,
  },
  subtitle: {
    fontSize: 14,
    color: colors.textSecondary,
    marginTop: 2,
  },
  xiaokeChatButton: {
    alignItems: 'center',
    padding: 8,
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
    color: colors.text,
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
    color: colors.text,
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
});

export default SuokeScreen;
