import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import React, { useCallback, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  Animated,
  Dimensions,
  FlatList,
  RefreshControl,
  StatusBar,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { useSelector } from 'react-redux';
import { RootState } from '../../store';
// import LinearGradient from 'react-native-linear-gradient';
const { width, height } = Dimensions.get('window');
// 联系人类型定义
export interface Contact {
  id: string;,
  name: string;
  avatar: string;,
  message: string;
  time: string;,
  unread: number;
  type: 'agent' | 'doctor' | 'user' | 'service';
  isOnline?: boolean;
  tag?: string;
  priority?: number;
  serviceEndpoint?: string;
  status?: 'active' | 'inactive' | 'maintenance';
}
// 联系人组类型定义
export interface ContactGroup {
  id: string;,
  name: string;
  contacts: Contact[];,
  type: 'agents' | 'medical' | 'community' | 'services';
}
// 微服务状态类型
interface ServiceStatus {
  name: string;,
  endpoint: string;
  status: 'healthy' | 'unhealthy' | 'unknown';,
  lastCheck: Date;
  responseTime?: number;
}
type MainTabParamList = {
  Home: undefined;,
  Suoke: undefined;
  Explore: undefined;,
  Life: undefined;
  Profile: undefined;,
  ChatDetail: { chatId: string; chatType: string; chatName: string };
  AgentChat: { agentId: string; agentName: string };
  DiagnosisService: { serviceType: string };
  HealthData: undefined;,
  KnowledgeBase: undefined;
};
type HomeScreenNavigationProp = NativeStackNavigationProp<
  MainTabParamList,
  'Home'
>;
const HomeScreen: React.FC = () => {
  const navigation = useNavigation<HomeScreenNavigationProp>();
  const [searchQuery, setSearchQuery] = useState('');
  const [contactGroups, setContactGroups] = useState<ContactGroup[]>([]);
  const [serviceStatuses, setServiceStatuses] = useState<ServiceStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [fadeAnim] = useState(new Animated.Value(0));
  const [slideAnim] = useState(new Animated.Value(50));
  // 从Redux获取用户信息
  const authState = useSelector(state: RootState) => state.auth);
  const user = 'user' in authState ? authState.user : null;
  // 微服务配置
  const microservices = {
    agents: {,
  xiaoai: { name: '小艾', port: 8015, description: '多模态感知智能体' },
      xiaoke: { name: '小克', port: 8016, description: '健康服务智能体' },
      laoke: { name: '老克', port: 8017, description: '知识传播智能体' },
      soer: { name: '索儿', port: 8018, description: '营养生活智能体' },
    },
    diagnosis: {,
  calculation: { name: '算诊服务', port: 8023, description: '计算诊断' },
      look: { name: '望诊服务', port: 8020, description: '图像分析诊断' },
      listen: { name: '闻诊服务', port: 8022, description: '语音分析诊断' },
      inquiry: { name: '问诊服务', port: 8021, description: '问答交互诊断' },
      palpation: { name: '切诊服务', port: 8024, description: '触诊模拟' },
    },
    core: {,
  gateway: { name: 'API网关', port: 8000, description: '统一入口' },
      user: { name: '用户管理', port: 8001, description: '用户服务' },
      knowledge: { name: '知识服务', port: 8002, description: '统一知识库' },
      health: { name: '健康数据', port: 8003, description: '健康数据管理' },
      blockchain: { name: '区块链服务', port: 8004, description: '隐私保护' },
      communication: { name: '通信服务', port: 8005, description: '消息通信' },
    },
  };
  // 工具函数
  const getAgentInfo = (agentType: string) => {
    const agentConfigs = {
      xiaoai: {,
  name: '小艾',
        avatar: '🤖',
        tag: '多模态感知',
        greeting: '您好！我是小艾，可以帮您分析图像、语音等多模态数据',
        colors: { primary: '#4A90E2', secondary: '#E3F2FD' },
      },
      xiaoke: {,
  name: '小克',
        avatar: '🧘‍♂️',
        tag: '健康服务',
        greeting: '您好！我是小克，专注为您提供个性化健康服务',
        colors: { primary: '#7B68EE', secondary: '#F3E5F5' },
      },
      laoke: {,
  name: '老克',
        avatar: '👨‍⚕️',
        tag: '知识传播',
        greeting: '您好！我是老克，让我为您分享健康知识和经验',
        colors: { primary: '#FF6B6B', secondary: '#FFEBEE' },
      },
      soer: {,
  name: '索儿',
        avatar: '🏃‍♀️',
        tag: '营养生活',
        greeting: '您好！我是索儿，帮您制定营养计划和生活方式',
        colors: { primary: '#4ECDC4', secondary: '#E0F2F1' },
      },
    };
    return agentConfigs[agentType] || agentConfigs.xiaoai;
  };
  const formatTime = (timestamp: string | Date | number): string => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    if (diffMins < 1) return '刚刚';
    if (diffMins < 60) return `${diffMins}分钟前`;
    if (diffHours < 24) return `${diffHours}小时前`;
    if (diffDays < 7) return `${diffDays}天前`;
    return date.toLocaleDateString('zh-CN', {
      month: 'short',
      day: 'numeric',
    });
  };
  // 生成智能体联系人数据
  const generateAgentContacts = (): Contact[] => {
    return Object.entries(microservices.agents).map([agentType, config], index) => {
        const agentInfo = getAgentInfo(agentType);
        return {
          id: agentType,
          name: agentInfo.name,
          avatar: agentInfo.avatar,
          message: agentInfo.greeting,
          time: '在线',
          unread: Math.floor(Math.random() * 3),
          type: 'agent' as const,
          isOnline: true,
          tag: agentInfo.tag,
          priority: 10 - index,
          serviceEndpoint: `http://localhost:${config.port}`,
          status: 'active',
        };
      }
    );
  };
  // 生成诊断服务联系人数据
  const generateDiagnosisContacts = (): Contact[] => {
    return Object.entries(microservices.diagnosis).map([serviceType, config], index) => ({
        id: `diagnosis_${serviceType}`,
        name: config.name,
        avatar: ['🔍', '👁️', '👂', '💬', '🤲'][index] || '🔍',
        message: `${config.description}服务已就绪`,
        time: '服务中',
        unread: 0,
        type: 'service' as const,
        isOnline: true,
        tag: '诊断服务',
        priority: 8 - index,
        serviceEndpoint: `http://localhost:${config.port}`,
        status: 'active',
      })
    );
  };
  // 生成核心服务联系人数据
  const generateCoreServiceContacts = (): Contact[] => {
    return Object.entries(microservices.core).map([serviceType, config], index) => ({
        id: `core_${serviceType}`,
        name: config.name,
        avatar: ['🌐', '👤', '📚', '💊', '🔐', '📡'][index] || '⚙️',
        message: `${config.description}运行正常`,
        time: '运行中',
        unread: 0,
        type: 'service' as const,
        isOnline: true,
        tag: '核心服务',
        priority: 6 - index,
        serviceEndpoint: `http://localhost:${config.port}`,
        status: 'active',
      })
    );
  };
  // 生成医生联系人数据
  const generateDoctorContacts = (): Contact[] => {
    const doctors = [
      {
        name: '张医生',
        specialty: '中医内科',
        message: '您的检查结果已出，一切正常',
      },
      {
        name: '李教授',
        specialty: '针灸专家',
        message: '请按照方案坚持服药，下周复诊',
      },
      {
        name: '王主任',
        specialty: '康复科',
        message: '康复训练进展良好，继续保持',
      },
    ];
    return doctors.map(doctor, index) => ({
      id: `doctor_${index}`,
      name: doctor.name,
      avatar: index % 2 === 0 ? '👩‍⚕️' : '👨‍⚕️',
      message: doctor.message,
      time: ['周二', '上周', '3天前'][index],
      unread: index === 0 ? 1 : 0,
      type: 'doctor' as const,
      tag: doctor.specialty,
      priority: 5 - index,
      status: 'active',
    }));
  };
  // 加载联系人组数据
  const loadContactGroups = useCallback(async () => {
    try {
      setLoading(true);

      // 模拟API延迟
      await new Promise(resolve) => setTimeout(resolve, 1000));

      const groups: ContactGroup[] = [
        {
          id: 'agents',
          name: '智能体服务',
          contacts: generateAgentContacts(),
          type: 'agents',
        },
        {
          id: 'diagnosis',
          name: '诊断服务',
          contacts: generateDiagnosisContacts(),
          type: 'services',
        },
        {
          id: 'core',
          name: '核心服务',
          contacts: generateCoreServiceContacts(),
          type: 'services',
        },
        {
          id: 'medical',
          name: '医疗专家',
          contacts: generateDoctorContacts(),
          type: 'medical',
        },
      ];

      setContactGroups(groups);

      // 启动动画
      Animated.parallel([
        Animated.timing(fadeAnim, {
          toValue: 1,
          duration: 800,
          useNativeDriver: true,
        }),
        Animated.timing(slideAnim, {
          toValue: 0,
          duration: 600,
          useNativeDriver: true,
        }),
      ]).start();
    } catch (error) {
      console.error('加载联系人失败:', error);
      Alert.alert('错误', '加载联系人失败，请重试');
    } finally {
      setLoading(false);
    }
  }, [fadeAnim, slideAnim]);
  // 刷新数据
  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await loadContactGroups();
    setRefreshing(false);
  }, [loadContactGroups]);
  // 处理联系人点击
  const handleContactPress = (contact: Contact) => {
    if (contact.type === 'agent') {
      navigation.navigate('AgentChat', {
        agentId: contact.id,
        agentName: contact.name,
      });
    } else if (contact.type === 'service') {
      if (contact.id.startsWith('diagnosis_')) {
        navigation.navigate('DiagnosisService', {
          serviceType: contact.id.replace('diagnosis_', ''),
        });
      } else {
        // 处理核心服务导航
        handleCoreServiceNavigation(contact.id);
      }
    } else if (contact.type === 'doctor') {
      navigation.navigate('ChatDetail', {
        chatId: contact.id,
        chatType: 'doctor',
        chatName: contact.name,
      });
    }
  };
  // 处理核心服务导航
  const handleCoreServiceNavigation = (serviceId: string) => {
    switch (serviceId) {
      case 'core_user':
        navigation.navigate('Profile');
        break;
      case 'core_knowledge':
        navigation.navigate('KnowledgeBase');
        break;
      case 'core_health':
        navigation.navigate('HealthData');
        break;
      default:
        Alert.alert('提示', `${serviceId} 服务功能开发中`);
    }
  };
  // 过滤联系人
  const filteredGroups = contactGroups;
    .map(group) => ({
      ...group,
      contacts: group.contacts.filter(contact) =>
          contact.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          contact.tag?.toLowerCase().includes(searchQuery.toLowerCase())
      ),
    }))
    .filter(group) => group.contacts.length > 0);
  useEffect() => {
    loadContactGroups();
  }, [loadContactGroups]);
  // 渲染联系人项
  const renderContactItem = ({ item: contact }: { item: Contact }) => {
    const agentInfo =
      contact.type === 'agent' ? getAgentInfo(contact.id) : null;
    const colors = agentInfo?.colors || {
      primary: '#4A90E2',
      secondary: '#E3F2FD',
    };
    return (
      <Animated.View;
        style={[
          styles.contactItemContainer,
          {
            opacity: fadeAnim,
            transform: [{ translateY: slideAnim }],
          },
        ]}
      >
        <TouchableOpacity;
          style={[
            styles.contactItem,
            contact.type === 'agent' && {
              borderLeftWidth: 4,
              borderLeftColor: colors.primary,
            },
          ]}
          onPress={() => handleContactPress(contact)}
          activeOpacity={0.7}
        >
          <View style={styles.avatarContainer}>
            <View;
              style={[
                styles.avatarWrapper,
                { backgroundColor: colors.secondary },
              ]}
            >
              <Text style={styles.avatar}>{contact.avatar}</Text>
              {contact.isOnline && <View style={styles.onlineIndicator} />}
            </View>
          </View>
          <View style={styles.contentContainer}>
            <View style={styles.headerRow}>
              <Text style={styles.contactName}>{contact.name}</Text>
              {contact.tag && (
                <View;
                  style={[
                    styles.tagContainer,
                    { backgroundColor: colors.primary },
                  ]}
                >
                  <Text style={[styles.tagText, { color: '#FFFFFF' }]}>
                    {contact.tag}
                  </Text>
                </View>
              )}
              <Text style={styles.timeText}>{contact.time}</Text>
            </View>
            <Text style={styles.messageText} numberOfLines={2}>
              {contact.message}
            </Text>
          </View>
          <View style={styles.statusContainer}>
            {contact.unread > 0 && (
              <View;
                style={[
                  styles.unreadBadge,
                  { backgroundColor: colors.primary },
                ]}
              >
                <Text style={styles.unreadText}>{contact.unread}</Text>
              </View>
            )}
            <Icon;
              name="chevron-right"
              size={20}
              color="#CCC"
              style={styles.chevronIcon}
            />
          </View>
        </TouchableOpacity>
      </Animated.View>
    );
  };
  // 渲染联系人组
  const renderContactGroup = ({ item: group }: { item: ContactGroup }) => (
    <View style={styles.groupContainer}>
      <Text style={styles.groupTitle}>{group.name}</Text>
      <FlatList;
        data={group.contacts}
        renderItem={renderContactItem}
        keyExtractor={(item) => item.id}
        scrollEnabled={false}
        ItemSeparatorComponent={() => <View style={styles.separator} />}
      />
    </View>
  );
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
  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#4A90E2" />

      {/* 头部 */}
      <View style={styles.header}>
        <View style={styles.headerGradient}>
          <View style={styles.headerContent}>
            <View style={styles.greetingContainer}>
              <Text style={styles.greetingText}>
                {user && typeof user === 'object' && 'name' in user;
                  ? `你好，${(user as any).name}`
                  : '欢迎使用索克生活'}
              </Text>
              <Text style={styles.subGreetingText}>智能健康管理平台</Text>
            </View>
            <TouchableOpacity;
              style={styles.profileButton}
              onPress={() => navigation.navigate('Profile')}
            >
              <Icon name="account-circle" size={32} color="#FFFFFF" />
            </TouchableOpacity>
          </View>
        </View>
      </View>

      {/* 搜索框 */}
      <View style={styles.searchContainer}>
        <View style={styles.searchInputContainer}>
          <Icon;
            name="magnify"
            size={20}
            color="#999"
            style={styles.searchIcon}
          />
          <TextInput;
            style={styles.searchInput}
            placeholder="搜索服务或联系人..."
            value={searchQuery}
            onChangeText={setSearchQuery}
            placeholderTextColor="#999"
          />
          {searchQuery.length > 0 && (
            <TouchableOpacity;
              style={styles.clearButton}
              onPress={() => setSearchQuery('')}
            >
              <Icon name="close-circle" size={20} color="#999" />
            </TouchableOpacity>
          )}
        </View>
      </View>

      {/* 联系人列表 */}
      <FlatList;
        data={filteredGroups}
        renderItem={renderContactGroup}
        keyExtractor={(item) => item.id}
        style={styles.listContainer}
        refreshControl={
          <RefreshControl;
            refreshing={refreshing}
            onRefresh={onRefresh}
            colors={['#4A90E2']}
            tintColor="#4A90E2"
          />
        }
        ListEmptyComponent={() => (
          <View style={styles.emptyContainer}>
            <Icon name="account-search" size={64} color="#CCC" />
            <Text style={styles.emptyTitle}>没有找到匹配的联系人</Text>
            <Text style={styles.emptySubtitle}>
              {searchQuery ? '尝试其他搜索词' : '下拉刷新重新加载'}
            </Text>
          </View>
        )}
      />
    </SafeAreaView>
  );
};
const styles = StyleSheet.create({
  container: {,
  flex: 1,
    backgroundColor: '#F8F9FA',
  },
  header: {,
  borderBottomLeftRadius: 20,
    borderBottomRightRadius: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 5,
    marginBottom: 10,
  },
  headerGradient: {,
  paddingTop: 10,
    paddingBottom: 20,
    borderBottomLeftRadius: 20,
    borderBottomRightRadius: 20,
    backgroundColor: '#4A90E2',
  },
  headerContent: {,
  flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
  },
  greetingContainer: {,
  flex: 1,
  },
  greetingText: {,
  fontSize: 24,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginBottom: 4,
  },
  subGreetingText: {,
  fontSize: 14,
    color: '#E3F2FD',
  },
  profileButton: {,
  padding: 8,
  },
  searchContainer: {,
  paddingHorizontal: 20,
    paddingVertical: 15,
  },
  searchInputContainer: {,
  flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F5F5F5',
    borderRadius: 25,
    paddingHorizontal: 15,
    height: 50,
  },
  searchIcon: {,
  marginRight: 10,
  },
  searchInput: {,
  flex: 1,
    fontSize: 16,
    color: '#333',
  },
  clearButton: {,
  padding: 5,
  },
  listContainer: {,
  paddingBottom: 20,
  },
  groupContainer: {,
  marginBottom: 20,
  },
  groupTitle: {,
  fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginHorizontal: 20,
    marginBottom: 10,
  },
  contactItemContainer: {,
  marginHorizontal: 15,
    marginVertical: 4,
  },
  contactItem: {,
  flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  avatarContainer: {,
  marginRight: 12,
  },
  avatarWrapper: {,
  width: 50,
    height: 50,
    borderRadius: 25,
    justifyContent: 'center',
    alignItems: 'center',
    position: 'relative',
  },
  avatar: {,
  fontSize: 24,
    fontWeight: 'bold',
  },
  onlineIndicator: {,
  position: 'absolute',
    bottom: 2,
    right: 2,
    width: 12,
    height: 12,
    borderRadius: 6,
    backgroundColor: '#4CAF50',
    borderWidth: 2,
    borderColor: '#FFFFFF',
  },
  contentContainer: {,
  flex: 1,
    marginRight: 8,
  },
  headerRow: {,
  flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  contactName: {,
  fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginRight: 8,
  },
  tagContainer: {,
  paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 10,
    marginRight: 8,
  },
  tagText: {,
  fontSize: 10,
    fontWeight: '500',
  },
  timeText: {,
  fontSize: 12,
    color: '#999',
    marginLeft: 'auto',
  },
  messageText: {,
  fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
  statusContainer: {,
  alignItems: 'center',
    justifyContent: 'center',
  },
  unreadBadge: {,
  minWidth: 20,
    height: 20,
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 4,
  },
  unreadText: {,
  color: '#FFFFFF',
    fontSize: 12,
    fontWeight: 'bold',
    paddingHorizontal: 6,
  },
  chevronIcon: {,
  opacity: 0.5,
  },
  separator: {,
  height: 1,
    backgroundColor: '#F0F0F0',
    marginHorizontal: 20,
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
  emptyContainer: {,
  flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 60,
  },
  emptyTitle: {,
  fontSize: 18,
    fontWeight: '600',
    color: '#666',
    marginTop: 16,
    marginBottom: 8,
  },
  emptySubtitle: {,
  fontSize: 14,
    color: '#999',
  },
});
export default HomeScreen;
