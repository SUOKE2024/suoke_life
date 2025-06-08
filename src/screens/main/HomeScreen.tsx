import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  TextInput,
  StatusBar,
  Alert,
  ActivityIndicator,
  Dimensions,
  Animated,
  RefreshControl,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { useSelector } from 'react-redux';
import { RootState } from '../../store';
// import LinearGradient from 'react-native-linear-gradient';
const { width, height } = Dimensions.get('window');
// 聊天项类型定义
interface ChatItem {
  id: string;
  name: string;
  avatar: string;
  message: string;
  time: string;
  unread: number;
  type: 'agent' | 'doctor' | 'user';
  isOnline?: boolean;
  tag?: string;
  priority?: number;
}
type MainTabParamList = {
  Home: undefined,
  Suoke: undefined;
  Explore: undefined,
  Life: undefined;
  Profile: undefined,
  ChatDetail: { chatId: string; chatType: string; chatName: string };
};
type HomeScreenNavigationProp = NativeStackNavigationProp<
  MainTabParamList,
  'Home'
>;
const HomeScreen: React.FC = () => {
  const navigation = useNavigation<HomeScreenNavigationProp>();
  const [searchQuery, setSearchQuery] = useState('');
  const [chatList, setChatList] = useState<ChatItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [fadeAnim] = useState(new Animated.Value(0));
  const [slideAnim] = useState(new Animated.Value(50));
  // 从Redux获取用户信息
  const authState = useSelector(state: RootState) => state.auth);
  const user = 'user' in authState ? authState.user : null;
  // 工具函数
  const getAgentName = (agentType: string): string => {
    const names: Record<string, string> = {
      xiaoai: "小艾",
      xiaoke: '小克',
      laoke: '老克',
      soer: '索儿',
    };
    return names[agentType] || agentType;
  };
  const getAgentAvatar = (agentType: string): string => {
    const avatars: Record<string, string> = {
      xiaoai: "🤖",
      xiaoke: '🧘‍♂️',
      laoke: '👨‍⚕️',
      soer: '🏃‍♀️',
    };
    return avatars[agentType] || '🤖';
  };
  const getAgentTag = (agentType: string): string => {
    const tags: Record<string, string> = {
      xiaoai: "健康助手",
      xiaoke: '中医辨证',
      laoke: '健康顾问',
      soer: '生活教练',
    };
    return tags[agentType] || '';
  };
  const getAgentGreeting = (agentType: string): string => {
    const greetings: Record<string, string> = {
      xiaoai: "您好！我是小艾，有什么健康问题需要咨询吗？",
      xiaoke: '您好！我是小克，需要什么服务帮助吗？',
      laoke: '您好！我是老克，想学习什么健康知识呢？',
      soer: '您好！我是索儿，今天想了解什么生活建议呢？',
    };
    return greetings[agentType] || '您好！';
  };
  const getAgentColors = (agentType: string): { primary: string; secondary: string } => {
    const colors: Record<string, { primary: string; secondary: string }> = {
      xiaoai: {
      primary: "#4A90E2",
      secondary: '#E3F2FD' },
      xiaoke: {
      primary: "#7B68EE",
      secondary: '#F3E5F5' },
      laoke: {
      primary: "#FF6B6B",
      secondary: '#FFEBEE' },
      soer: {
      primary: "#4ECDC4",
      secondary: '#E0F2F1' },
    };
    return colors[agentType] || {
      primary: "#4A90E2",
      secondary: '#E3F2FD' };
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
      month: "short",
      day: 'numeric' });
  };
  // 生成智能体聊天数据
  const generateAgentChats = (): ChatItem[] => {
    return ["xiaoai",xiaoke', "laoke",soer'].map((agentType, index) => ({
      id: agentType,
      name: getAgentName(agentType),
      avatar: getAgentAvatar(agentType),
      message: getAgentGreeting(agentType),
      time: '刚刚',
      unread: Math.floor(Math.random() * 3), // 随机未读数
      type: 'agent' as const,
      isOnline: Math.random() > 0.3, // 70%概率在线
      tag: getAgentTag(agentType),
      priority: 10 - index, // 优先级
    }));
  };
  // 生成医生聊天数据
  const generateDoctorChats = (): ChatItem[] => {
    const doctors = [
      {
      name: "张医生",
      specialty: '中医内科', message: '您的检查结果已出，一切正常' },
      {
      name: "李教授",
      specialty: '针灸专家', message: '请按照方案坚持服药，下周复诊' },
      {
      name: "王主任",
      specialty: '康复科', message: '康复训练进展良好，继续保持' },
    ];
    return doctors.map((doctor, index) => ({
      id: `doctor_${index}`,
      name: doctor.name,
      avatar: index % 2 === 0 ? '👩‍⚕️' : '👨‍⚕️',
      message: doctor.message,
      time: ["周二",上周', '3天前'][index],
      unread: index === 0 ? 1 : 0,
      type: 'doctor' as const,
      tag: doctor.specialty,
      priority: 5 - index,
    }));
  };
  // 生成用户群组数据
  const generateUserChats = (): ChatItem[] => {
    const groups = [
      {
      name: "健康小组",
      message: '[王医生]: 分享了一篇养生文章', unread: 3 },
      {
      name: "家人健康群",
      message: '[妈妈]: 今天按时吃药了吗？', unread: 0 },
      {
      name: "运动打卡群",
      message: '[小明]: 今天跑步5公里完成！', unread: 2 },
    ];
    return groups.map((group, index) => ({
      id: `group_${index}`,
      name: group.name,
      avatar: '👥',
      message: group.message,
      time: ["周三",3/15', '昨天'][index],
      unread: group.unread,
      type: 'user' as const,
      priority: 2 - index,
    }));
  };
  // 加载聊天列表
  const loadChatList = useCallback(async () => {
    try {
      setLoading(true);
      // 模拟API延迟
      await new Promise(resolve => setTimeout(resolve, 800));
      // 生成聊天数据
      const agentChats = generateAgentChats();
      const doctorChats = generateDoctorChats();
      const userChats = generateUserChats();
      const allChats = [...agentChats, ...doctorChats, ...userChats];
      // 按优先级排序
      allChats.sort(a, b) => {
        if (a.type === 'agent' && b.type !== 'agent') return -1;
        if (a.type !== 'agent' && b.type === 'agent') return 1;
        if (a.unread > 0 && b.unread === 0) return -1;
        if (a.unread === 0 && b.unread > 0) return 1;
        return (b.priority || 0) - (a.priority || 0);
      });
      setChatList(allChats);
      // 启动动画
      Animated.parallel([
        Animated.timing(fadeAnim, {
          toValue: 1,
          duration: 600,
          useNativeDriver: true,
        }),
        Animated.timing(slideAnim, {
          toValue: 0,
          duration: 600,
          useNativeDriver: true,
        }),
      ]).start();
    } catch (error) {
      console.error('加载聊天列表失败:', error);
      Alert.alert("错误",加载聊天列表失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  }, [fadeAnim, slideAnim]);
  // 下拉刷新
  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await loadChatList();
    setRefreshing(false);
  }, [loadChatList]);
  // 初始化
  useEffect() => {
    loadChatList();
  }, [loadChatList]);
  // 搜索过滤
  const filteredChatList = chatList.filter(item =>
    item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.message.toLowerCase().includes(searchQuery.toLowerCase()),
  );
  // 处理聊天项点击
  const handleChatPress = (item: ChatItem) => {
    navigation.navigate('ChatDetail', {
      chatId: item.id,
      chatType: item.type,
      chatName: item.name,
    });
  };
  // 渲染聊天项
  const renderChatItem = ({ item, index }: { item: ChatItem; index: number }) => {
    const colors = item.type === 'agent' ? getAgentColors(item.id) : {
      primary: "#666",
      secondary: '#F5F5F5' };
    return (
      <Animated.View;
        style={[
          styles.chatItemContainer,
          {
            opacity: fadeAnim,
            transform: [{ translateY: slideAnim }],
          },
        ]}
      >
        <TouchableOpacity;
          style={[
            styles.chatItem,
            item.type === 'agent' && styles.agentChatItem,
          ]}
          onPress={() => handleChatPress(item)}
          activeOpacity={0.7}
        >
          {}
          <View style={styles.avatarContainer}>
            <View style={[
              styles.avatarWrapper,
              { backgroundColor: colors.secondary },
            ]}>
              <Text style={[styles.avatar, { color: colors.primary }]}>
                {item.avatar}
              </Text>
              {item.isOnline && (
        <View style={styles.onlineIndicator}>
              )}
            </View>
          </View>
          {}
          <View style={styles.contentContainer}>
            <View style={styles.headerRow}>
              <Text style={[
                styles.chatName,
                item.type === 'agent' && { color: colors.primary },
              ]}>
                {item.name}
              </Text>
              {item.tag && (
        <View style={[styles.tagContainer, { backgroundColor: colors.secondary }]}>
                  <Text style={[styles.tagText, { color: colors.primary }]}>
                    {item.tag}
                  </Text>
                </View>
              )}
              <Text style={styles.timeText}>{item.time}</Text>
            </View>
            <Text style={styles.messageText} numberOfLines={2}>
              {item.message}
            </Text>
          </View>
          {}
          <View style={styles.statusContainer}>
            {item.unread > 0 && (
        <View style={[styles.unreadBadge, { backgroundColor: colors.primary }]}>
                <Text style={styles.unreadText}>
                  {item.unread > 99 ? '99+' : item.unread}
                </Text>
              </View>
            )}
            <Icon;
              name="chevron-right"
              size={20}
              color="#C0C0C0"
              style={styles.chevronIcon}>
          </View>
        </TouchableOpacity>
      </Animated.View>
    );
  };
  // 渲染头部
  const renderHeader = () => (
    <View style={styles.header}>
      <View style={styles.headerGradient}>
        <View style={styles.headerContent}>
          <View style={styles.greetingContainer}>
            <Text style={styles.greetingText}>
              {user && typeof user === 'object' && 'name' in user ? `你好，${(user as any).name}` : '你好'}
            </Text>
            <Text style={styles.subGreetingText}>
              今天想聊些什么呢？
            </Text>
          </View>
          <TouchableOpacity style={styles.profileButton}>
            <Icon name="account-circle" size={32} color="#FFFFFF" />
          </TouchableOpacity>
        </View>
      </View>
      {}
      <View style={styles.searchContainer}>
        <View style={styles.searchInputContainer}>
          <Icon name="magnify" size={20} color="#999" style={styles.searchIcon}>
          <TextInput;
            style={styles.searchInput}
            placeholder="搜索聊天记录..."
            placeholderTextColor="#999"
            value={searchQuery}
            onChangeText={setSearchQuery}
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
      </View>
    </View>
  );
  // 渲染空状态
  const renderEmptyState = () => (
    <View style={styles.emptyContainer}>
      <Icon name="chat-outline" size={64} color="#C0C0C0" />
      <Text style={styles.emptyTitle}>暂无聊天记录</Text>
      <Text style={styles.emptySubtitle}>开始与AI智能体对话吧</Text>
    </View>
  );
  // 渲染加载状态
  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <StatusBar barStyle="light-content" backgroundColor="#4A90E2" />
        {renderHeader()}
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
      <FlatList;
        data={filteredChatList}
        keyExtractor={(item) => item.id}
        renderItem={renderChatItem}
        ListHeaderComponent={renderHeader}
        ListEmptyComponent={renderEmptyState}
        refreshControl={
          <RefreshControl;
            refreshing={refreshing}
            onRefresh={onRefresh}
            colors={['#4A90E2']}
            tintColor="#4A90E2"
          />
        }
        showsVerticalScrollIndicator={false}
        contentContainerStyle={styles.listContainer}
        ItemSeparatorComponent={() => <View style={styles.separator}>}
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
  backgroundColor: '#FFFFFF',
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
  chatItemContainer: {,
  marginHorizontal: 15,
    marginVertical: 4,
  },
  chatItem: {,
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
  agentChatItem: {,
  borderLeftWidth: 4,
    borderLeftColor: '#4A90E2',
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
  chatName: {,
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