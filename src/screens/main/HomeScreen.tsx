import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import React, { useCallback, useEffect, useState } from 'react';
import {;
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
  View
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
  name: string;,
  avatar: string;,
  message: string;,
  time: string;,
  unread: number;,
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
  name: string;,
  contacts: Contact[];,
  type: 'agents' | 'medical' | 'community' | 'services';
}
// 微服务状态类型
interface ServiceStatus {
  name: string;,
  endpoint: string;,
  status: 'healthy' | 'unhealthy' | 'unknown';,
  lastCheck: Date;
  responseTime?: number;
}
type MainTabParamList = {
  Home: undefined;,
  Suoke: undefined;,
  Explore: undefined;,
  Life: undefined;,
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
      soer: { name: '索儿', port: 8018, description: '营养生活智能体' }
    },
    diagnosis: {,
  calculation: { name: '算诊服务', port: 8023, description: '计算诊断' },
      look: { name: '望诊服务', port: 8020, description: '图像分析诊断' },
      listen: { name: '闻诊服务', port: 8022, description: '语音分析诊断' },
      inquiry: { name: '问诊服务', port: 8021, description: '问答交互诊断' },
      palpation: { name: '切诊服务', port: 8024, description: '触诊模拟' }
    },
    core: {,
  gateway: { name: 'API网关', port: 8000, description: '统一入口' },
      user: { name: '用户管理', port: 8001, description: '用户服务' },
      knowledge: { name: '知识服务', port: 8002, description: '统一知识库' },
      health: { name: '健康数据', port: 8003, description: '健康数据管理' },
      blockchain: { name: '区块链服务', port: 8004, description: '隐私保护' },
      communication: { name: '通信服务', port: 8005, description: '消息通信' }
    }
  };
  // 工具函数
  const getAgentInfo = (agentType: string) => {
    const agentConfigs: any = {,
  xiaoai: {,
  name: '小艾',
        avatar: '🤖',
        tag: '多模态感知',
        greeting: '您好！我是小艾，可以帮您分析图像、语音等多模态数据',
        colors: { primary: '#4A90E2', secondary: '#E3F2FD' }
      },
      xiaoke: {,
  name: '小克',
        avatar: '🧘‍♂️',
        tag: '健康服务',
        greeting: '您好！我是小克，专注为您提供个性化健康服务',
        colors: { primary: '#7B68EE', secondary: '#F3E5F5' }
      },
      laoke: {,
  name: '老克',
        avatar: '👨‍⚕️',
        tag: '知识传播',
        greeting: '您好！我是老克，让我为您分享健康知识和经验',
        colors: { primary: '#FF6B6B', secondary: '#FFEBEE' }
      },
      soer: {,
  name: '索儿',
        avatar: '🏃‍♀️',
        tag: '营养生活',
        greeting: '您好！我是索儿，帮您制定营养计划和生活方式',
        colors: { primary: '#4ECDC4', secondary: '#E0F2F1' }
      }
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
      day: 'numeric'
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
        status: 'active'
      };
    });
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
      status: 'active'
    }));
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
      status: 'active'
    }));
  };
  // 生成医生联系人数据
  const generateDoctorContacts = (): Contact[] => {
    const doctors = [
      { name: '张医生', specialty: '中医内科', avatar: '👨‍⚕️' },
      { name: '李医生', specialty: '针灸推拿', avatar: '👩‍⚕️' },
      { name: '王医生', specialty: '中医妇科', avatar: '👨‍⚕️' },
      { name: '赵医生', specialty: '中医儿科', avatar: '👩‍⚕️' }
    ];
    return doctors.map(doctor, index) => ({
      id: `doctor_${index}`,
      name: doctor.name,
      avatar: doctor.avatar,
      message: `${doctor.specialty}专家，随时为您服务`,
      time: '在线',
      unread: 0,
      type: 'doctor' as const,
      isOnline: true,
      tag: doctor.specialty,
      priority: 5 - index,
      status: 'active'
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
          name: '智能体助手',
          contacts: generateAgentContacts(),
          type: 'agents'
        },
        {
          id: 'diagnosis',
          name: '诊断服务',
          contacts: generateDiagnosisContacts(),
          type: 'services'
        },
        {
          id: 'core',
          name: '核心服务',
          contacts: generateCoreServiceContacts(),
          type: 'services'
        },
        {
          id: 'doctors',
          name: '专家医生',
          contacts: generateDoctorContacts(),
          type: 'medical'
        }
      ];

      setContactGroups(groups);

      // 启动动画
      Animated.parallel([
        Animated.timing(fadeAnim, {
          toValue: 1,
          duration: 800,
          useNativeDriver: true;
        }),
        Animated.timing(slideAnim, {
          toValue: 0,
          duration: 600,
          useNativeDriver: true;
        })
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
        agentName: contact.name;
      });
    } else if (contact.type === 'service' && contact.id.startsWith('diagnosis_')) {
      const serviceType = contact.id.replace('diagnosis_', '');
      navigation.navigate('DiagnosisService', { serviceType });
    } else if (contact.type === 'service' && contact.id.startsWith('core_')) {
      handleCoreServiceNavigation(contact.id);
    } else {
      navigation.navigate('ChatDetail', {
        chatId: contact.id,
        chatType: contact.type,
        chatName: contact.name;
      });
    }
  };
  // 处理核心服务导航
  const handleCoreServiceNavigation = (serviceId: string) => {
    const serviceType = serviceId.replace('core_', '');
    
    switch (serviceType) {
      case 'health':
        navigation.navigate('HealthData');
        break;
      case 'knowledge':
        navigation.navigate('KnowledgeBase');
        break;
      default:
        Alert.alert('服务信息', `${serviceType}服务正在开发中`);
    }
  };
  // 过滤联系人
  const filteredGroups = contactGroups.map(group => ({
    ...group,
    contacts: group.contacts.filter(contact =>
      contact.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      contact.message.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (contact.tag && contact.tag.toLowerCase().includes(searchQuery.toLowerCase()))
    )
  })).filter(group => group.contacts.length > 0);
  useEffect() => {
    loadContactGroups();
  }, [loadContactGroups]);
  // 渲染联系人项
  const renderContactItem = ({ item }: { item: Contact }) => (
    <TouchableOpacity;
      style={styles.contactItem}
      onPress={() => handleContactPress(item)}
      activeOpacity={0.7}
    >
      <View style={styles.avatarContainer}>
        <Text style={styles.avatar}>{item.avatar}</Text>
        {item.isOnline && <View style={styles.onlineIndicator} />}
      </View>
      
      <View style={styles.contactInfo}>
        <View style={styles.contactHeader}>
          <Text style={styles.contactName}>{item.name}</Text>
          {item.tag && (
            <View style={styles.tagContainer}>
              <Text style={styles.tag}>{item.tag}</Text>
            </View>
          )}
          <Text style={styles.contactTime}>{item.time}</Text>
        </View>
        
        <Text style={styles.contactMessage} numberOfLines={1}>
          {item.message}
        </Text>
      </View>
      
      {item.unread > 0 && (
        <View style={styles.unreadBadge}>
          <Text style={styles.unreadText}>{item.unread}</Text>
        </View>
      )}
    </TouchableOpacity>
  );
  // 渲染联系人组
  const renderContactGroup = ({ item }: { item: ContactGroup }) => (
    <View style={styles.groupContainer}>
      <View style={styles.groupHeader}>
        <Text style={styles.groupTitle}>{item.name}</Text>
        <Text style={styles.groupCount}>({item.contacts.length})</Text>
      </View>
      
      <FlatList;
        data={item.contacts}
        renderItem={renderContactItem}
        keyExtractor={(contact) => contact.id}
        scrollEnabled={false}
        showsVerticalScrollIndicator={false}
      />
    </View>
  );
  if (loading) {
    return (
      <SafeAreaView style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#4A90E2" />
        <Text style={styles.loadingText}>正在加载索克生活...</Text>
      </SafeAreaView>
    );
  }
  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#FFFFFF" />
      
      {// 头部}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>索克生活</Text>
        <Text style={styles.headerSubtitle}>
          {user ? `欢迎回来，${user.name || '用户'}` : '智能健康管理平台'}
        </Text>
      </View>

      {// 搜索框}
      <View style={styles.searchContainer}>
        <Icon name="magnify" size={20} color="#999" style={styles.searchIcon} />
        <TextInput;
          style={styles.searchInput}
          placeholder="搜索智能体、服务或医生..."
          value={searchQuery}
          onChangeText={setSearchQuery}
          placeholderTextColor="#999"
        />
        {searchQuery.length > 0 && (
          <TouchableOpacity;
            onPress={() => setSearchQuery('')}
            style={styles.clearButton}
          >
            <Icon name="close-circle" size={20} color="#999" />
          </TouchableOpacity>
        )}
      </View>

      {// 联系人列表}
      <Animated.View;
        style={[
          styles.listContainer,
          {
            opacity: fadeAnim,
            transform: [{ translateY: slideAnim }]
          }
        ]}
      >
        <FlatList;
          data={filteredGroups}
          renderItem={renderContactGroup}
          keyExtractor={(group) => group.id}
          refreshControl={
            <RefreshControl;
              refreshing={refreshing}
              onRefresh={onRefresh}
              colors={['#4A90E2']}
              tintColor="#4A90E2"
            />
          }
          showsVerticalScrollIndicator={false}
          contentContainerStyle={styles.listContent}
        />
      </Animated.View>
    </SafeAreaView>
  );
};
const styles = StyleSheet.create({
  container: {,
  flex: 1,
    backgroundColor: '#FFFFFF'
  },
  loadingContainer: {,
  flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#FFFFFF'
  },
  loadingText: {,
  marginTop: 16,
    fontSize: 16,
    color: '#666',
    textAlign: 'center'
  },
  header: {,
  paddingHorizontal: 20,
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#F0F0F0'
  },
  headerTitle: {,
  fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4;
  },
  headerSubtitle: {,
  fontSize: 14,
    color: '#666'
  },
  searchContainer: {,
  flexDirection: 'row',
    alignItems: 'center',
    marginHorizontal: 20,
    marginVertical: 16,
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#F8F9FA',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#E9ECEF'
  },
  searchIcon: {,
  marginRight: 12;
  },
  searchInput: {,
  flex: 1,
    fontSize: 16,
    color: '#333',
    padding: 0;
  },
  clearButton: {,
  marginLeft: 8;
  },
  listContainer: {,
  flex: 1;
  },
  listContent: {,
  paddingBottom: 20;
  },
  groupContainer: {,
  marginBottom: 24;
  },
  groupHeader: {,
  flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 12,
    backgroundColor: '#F8F9FA'
  },
  groupTitle: {,
  fontSize: 16,
    fontWeight: '600',
    color: '#333'
  },
  groupCount: {,
  fontSize: 14,
    color: '#666',
    marginLeft: 8;
  },
  contactItem: {,
  flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 16,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#F0F0F0'
  },
  avatarContainer: {,
  position: 'relative',
    marginRight: 16;
  },
  avatar: {,
  fontSize: 32,
    width: 48,
    height: 48,
    textAlign: 'center',
    lineHeight: 48;
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
    borderColor: '#FFFFFF'
  },
  contactInfo: {,
  flex: 1;
  },
  contactHeader: {,
  flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4;
  },
  contactName: {,
  fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginRight: 8;
  },
  tagContainer: {,
  backgroundColor: '#E3F2FD',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 12,
    marginRight: 8;
  },
  tag: {,
  fontSize: 12,
    color: '#1976D2',
    fontWeight: '500'
  },
  contactTime: {,
  fontSize: 12,
    color: '#999',
    marginLeft: 'auto'
  },
  contactMessage: {,
  fontSize: 14,
    color: '#666',
    lineHeight: 20;
  },
  unreadBadge: {,
  backgroundColor: '#FF5722',
    borderRadius: 12,
    minWidth: 24,
    height: 24,
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: 12;
  },
  unreadText: {,
  fontSize: 12,
    color: '#FFFFFF',
    fontWeight: 'bold'
  }
});
export default HomeScreen;
