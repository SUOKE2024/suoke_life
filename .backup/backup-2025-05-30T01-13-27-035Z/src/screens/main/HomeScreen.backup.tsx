import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from '../../components/common/Icon';
import { colors, spacing, fonts } from '../../constants/theme';
import NavigationTest from '../../components/NavigationTest';
import AgentChatInterface, { AgentType } from '../../components/common/AgentChatInterface';
import ContactsList, { Contact } from '../../components/common/ContactsList';
import AccessibilitySettings from '../../components/common/AccessibilitySettings';

import React, { useState, useEffect } from 'react';
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  TextInput,
  Alert,
  Modal,
} from 'react-native';

// 聊天频道类型
interface ChatChannel {
  id: string;
  name: string;
  type: 'agent' | 'user' | 'doctor' | 'group';
  avatar: string;
  lastMessage: string;
  lastMessageTime: string;
  unreadCount: number;
  isOnline: boolean;
  agentType?: 'xiaoai' | 'xiaoke' | 'laoke' | 'soer';
  specialization?: string;
}

// 模拟聊天频道数据
const CHAT_CHANNELS: ChatChannel[] = [
  {
    id: 'xiaoai',
    name: '小艾',
    type: 'agent',
    agentType: 'xiaoai',
    avatar: '🤖',
    lastMessage: '您好！我是小艾，您的健康助手。有什么可以帮助您的吗？',
    lastMessageTime: '刚刚',
    unreadCount: 0,
    isOnline: true,
    specialization: '健康诊断与建议',
  },
  {
    id: 'xiaoke',
    name: '小克',
    type: 'agent',
    agentType: 'xiaoke',
    avatar: '👨‍⚕️',
    lastMessage: '我可以为您提供专业的医疗服务和健康管理',
    lastMessageTime: '5分钟前',
    unreadCount: 1,
    isOnline: true,
    specialization: '医疗服务管理',
  },
  {
    id: 'laoke',
    name: '老克',
    type: 'agent',
    agentType: 'laoke',
    avatar: '👴',
    lastMessage: '中医养生之道，在于顺应自然，调和阴阳',
    lastMessageTime: '10分钟前',
    unreadCount: 0,
    isOnline: true,
    specialization: '中医养生教育',
  },
  {
    id: 'soer',
    name: '索儿',
    type: 'agent',
    agentType: 'soer',
    avatar: '👧',
    lastMessage: '今天的生活安排我来帮您规划吧！',
    lastMessageTime: '15分钟前',
    unreadCount: 2,
    isOnline: true,
    specialization: '生活方式指导',
  },
  {
    id: 'dr_wang',
    name: '王医生',
    type: 'doctor',
    avatar: '👩‍⚕️',
    lastMessage: '您的检查报告已经出来了，整体情况良好',
    lastMessageTime: '1小时前',
    unreadCount: 0,
    isOnline: false,
    specialization: '内科主任医师',
  },
  {
    id: 'dr_li',
    name: '李中医',
    type: 'doctor',
    avatar: '🧑‍⚕️',
    lastMessage: '根据您的体质，建议调整饮食结构',
    lastMessageTime: '2小时前',
    unreadCount: 1,
    isOnline: true,
    specialization: '中医科副主任医师',
  },
  {
    id: 'health_group',
    name: '健康交流群',
    type: 'group',
    avatar: '👥',
    lastMessage: '张三: 大家有什么好的养生方法推荐吗？',
    lastMessageTime: '30分钟前',
    unreadCount: 5,
    isOnline: true,
    specialization: '健康话题讨论',
  },
  {
    id: 'user_zhang',
    name: '张小明',
    type: 'user',
    avatar: '👤',
    lastMessage: '谢谢您的建议，我会按时服药的',
    lastMessageTime: '45分钟前',
    unreadCount: 0,
    isOnline: false,
    specialization: '普通用户',
  },
];

// 联系人数据
const CONTACTS: Contact[] = [
  {
    id: 'xiaoai',
    name: '小艾',
    type: 'agent',
    agentType: 'xiaoai',
    avatar: '🤖',
    isOnline: true,
    specialization: '健康诊断与建议',
  },
  {
    id: 'xiaoke',
    name: '小克',
    type: 'agent',
    agentType: 'xiaoke',
    avatar: '👨‍⚕️',
    isOnline: true,
    specialization: '医疗服务管理',
  },
  {
    id: 'laoke',
    name: '老克',
    type: 'agent',
    agentType: 'laoke',
    avatar: '👴',
    isOnline: true,
    specialization: '中医养生教育',
  },
  {
    id: 'soer',
    name: '索儿',
    type: 'agent',
    agentType: 'soer',
    avatar: '👧',
    isOnline: true,
    specialization: '生活方式指导',
  },
  {
    id: 'dr_wang',
    name: '王医生',
    type: 'doctor',
    avatar: '👩‍⚕️',
    isOnline: false,
    lastSeen: '1小时前',
    specialization: '内科诊疗',
    department: '内科',
    title: '主任医师',
  },
  {
    id: 'dr_li',
    name: '李中医',
    type: 'doctor',
    avatar: '🧑‍⚕️',
    isOnline: true,
    specialization: '中医调理',
    department: '中医科',
    title: '副主任医师',
  },
  {
    id: 'user_zhang',
    name: '张小明',
    type: 'user',
    avatar: '👤',
    isOnline: false,
    lastSeen: '45分钟前',
  },
];

export const HomeScreen: React.FC = () => {
  const [channels, setChannels] = useState<ChatChannel[]>(CHAT_CHANNELS);
  const [searchText, setSearchText] = useState('');
  const [agentChatVisible, setAgentChatVisible] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState<AgentType>('xiaoai');
  const [contactsVisible, setContactsVisible] = useState(false);
  const [accessibilitySettingsVisible, setAccessibilitySettingsVisible] = useState(false);
  const [accessibilityEnabled, setAccessibilityEnabled] = useState(false);
  const [showNavigationTest, setShowNavigationTest] = useState(false);

  // 过滤聊天频道
  const filteredChannels = useMemo(() => useMemo(() => channels.filter(channel => {
    const matchesSearch = channel.name.toLowerCase().includes(searchText.toLowerCase()) ||
                         channel.lastMessage.toLowerCase().includes(searchText.toLowerCase()), []), []);
    return matchesSearch;
  });

  // 打开聊天
  const openChat = useMemo(() => useMemo(() => useCallback( (channel: ChatChannel) => {, []), []), []);
    if (channel.type === 'agent') {
      Alert.alert(
        `与${channel.name}对话`,
        `${channel.specialization}\n\n即将进入与${channel.name}的对话界面`,
        [
          { text: '取消', style: 'cancel' },
          { text: '开始对话', onPress: () => startAgentChat(channel) },
        ]
      );
    } else {
      Alert.alert('聊天功能', `即将打开与${channel.name}的聊天`);
    }
  };

  // 开始智能体对话
  const startAgentChat = useMemo(() => useMemo(() => async (channel: ChatChannel) => {
    try {
      console.log(`🤖 启动与${channel.name}的对话...`), []), []);
      
      // 清除未读消息
      setChannels(prev => prev.map(ch => 
        ch.id === channel.id ? { ...ch, unreadCount: 0 } : ch
      ));

      // 设置选中的智能体并显示对话界面
      if (channel.agentType) {
        setSelectedAgent(channel.agentType);
        setAgentChatVisible(true);
        console.log(`🤖 进入${channel.name}对话界面`);
      }

    } catch (error) {
      console.error('启动智能体对话失败:', error);
      Alert.alert('连接失败', `无法连接到${channel.name}服务，请稍后重试`);
    }
  };

  // 处理联系人点击
  const handleContactPress = useMemo(() => useMemo(() => useCallback( (contact: Contact) => {, []), []), []);
    if (contact.type === 'agent' && contact.agentType) {
      setSelectedAgent(contact.agentType);
      setAgentChatVisible(true);
      setContactsVisible(false);
    } else {
      Alert.alert('聊天功能', `即将打开与${contact.name}的聊天`);
    }
  };

  // 渲染聊天频道项
  const renderChannelItem = useMemo(() => useMemo(() => useCallback( ({ item }: { item: ChatChannel }) => {, []), []), []);
    const getChannelColor = useMemo(() => useMemo(() => useCallback( () => {, []), []), []);
      switch (item.type) {
        case 'agent':
          return colors.primary;
        case 'doctor':
          return '#34C759';
        case 'group':
          return '#FF9500';
        default:
          return colors.textSecondary;
      }
    };

    return (
      <TouchableOpacity style={styles.channelItem} onPress={() => openChat(item)}>
        <View style={styles.avatarContainer}>
          <Text style={styles.avatar}>{item.avatar}</Text>
          {item.isOnline && <View style={styles.onlineIndicator} />}
        </View>
        
        <View style={styles.channelContent}>
          <View style={styles.channelHeader}>
            <Text style={styles.channelName}>{item.name}</Text>
            <Text style={styles.messageTime}>{item.lastMessageTime}</Text>
          </View>
          
          <View style={styles.channelFooter}>
            <Text style={styles.lastMessage} numberOfLines={1}>
              {item.lastMessage}
            </Text>
            {item.unreadCount > 0 && (
              <View style={styles.unreadBadge}>
                <Text style={styles.unreadText}>
                  {item.unreadCount > 99 ? '99+' : item.unreadCount}
                </Text>
              </View>
            )}
          </View>
          
          <Text style={[styles.specialization, { color: getChannelColor() }]}>
            {item.specialization}
          </Text>
        </View>
      </TouchableOpacity>
    );
  };

  return (
    <SafeAreaView style={styles.container}>
        <TouchableOpacity
          style={{
            position: 'absolute',
            top: 100,
            right: 20,
            backgroundColor: '#FF9500',
            padding: 10,
            borderRadius: 5,
            zIndex: 1000,
          }}
          onPress={() => setShowNavigationTest(!showNavigationTest)}
        >
          <Text style={{ color: 'white', fontSize: 12 }}>导航测试</Text>
        </TouchableOpacity>
        
        {showNavigationTest && (
          <Modal
            visible={showNavigationTest}
            animationType="slide"
            presentationStyle="pageSheet"
          >
            <NavigationTest />
            <TouchableOpacity
              style={{
                position: 'absolute',
                top: 50,
                right: 20,
                backgroundColor: '#FF3B30',
                padding: 10,
                borderRadius: 5,
              }}
              onPress={() => setShowNavigationTest(false)}
            >
              <Text style={{ color: 'white' }}>关闭</Text>
            </TouchableOpacity>
          </Modal>
        )}
      {/* 头部 */}
      <View style={styles.header}>
        <Text style={styles.title}>聊天</Text>
        <View style={styles.headerActions}>
          <TouchableOpacity 
            style={styles.headerButton}
            onPress={() => setAccessibilitySettingsVisible(true)}
          >
            <Icon 
              name="account-voice" 
              size={24} 
              color={accessibilityEnabled ? colors.success : colors.textSecondary} 
            />
          </TouchableOpacity>
          <TouchableOpacity 
            style={styles.headerButton}
            onPress={() => setContactsVisible(true)}
          >
            <Icon name="account-multiple" size={24} color={colors.primary} />
          </TouchableOpacity>
          <TouchableOpacity style={styles.headerButton}>
            <Icon name="plus" size={24} color={colors.primary} />
          </TouchableOpacity>
        </View>
      </View>

      {/* 搜索框 */}
      <View style={styles.searchContainer}>
        <Icon name="magnify" size={20} color={colors.textSecondary} />
        <TextInput
          style={styles.searchInput}
          placeholder="搜索聊天记录..."
          value={searchText}
          onChangeText={setSearchText}
          placeholderTextColor={colors.textSecondary}
        />
      </View>

      {/* 聊天频道列表 */}
      <FlatList
        data={filteredChannels}
        keyExtractor={item => item.id}
        renderItem={renderChannelItem}
        style={styles.channelsList}
        showsVerticalScrollIndicator={false}
        ItemSeparatorComponent={() => <View style={styles.separator} />}
        ListEmptyComponent={() => (
          <View style={styles.emptyState}>
            <Icon name="message-outline" size={64} color={colors.textSecondary} />
            <Text style={styles.emptyTitle}>暂无聊天记录</Text>
            <Text style={styles.emptySubtitle}>点击右上角联系人图标开始聊天</Text>
          </View>
        )}
      />

      {/* 快速操作按钮 */}
      <TouchableOpacity style={styles.fabButton}>
        <Icon name="message-plus" size={24} color="white" />
      </TouchableOpacity>

      {/* 智能体对话界面 */}
      <AgentChatInterface
        visible={agentChatVisible}
        onClose={() => setAgentChatVisible(false)}
        agentType={selectedAgent}
        userId="current_user_id"
        accessibilityEnabled={accessibilityEnabled}
      />

      {/* 联系人列表模态框 */}
      <Modal
        visible={contactsVisible}
        animationType="slide"
        presentationStyle="pageSheet"
        onRequestClose={() => setContactsVisible(false)}
      >
        <SafeAreaView style={styles.modalContainer}>
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>联系人</Text>
            <TouchableOpacity
              onPress={() => setContactsVisible(false)}
              style={styles.modalCloseButton}
            >
              <Icon name="close" size={24} color={colors.text} />
            </TouchableOpacity>
          </View>
          <ContactsList
            contacts={CONTACTS}
            onContactPress={handleContactPress}
            showSearch={true}
            groupByType={true}
            showOnlineStatus={true}
          />
        </SafeAreaView>
      </Modal>

      {/* 无障碍设置模态框 */}
      <AccessibilitySettings
        visible={accessibilitySettingsVisible}
        onClose={() => setAccessibilitySettingsVisible(false)}
        userId="current_user_id"
        onSettingsChange={setAccessibilityEnabled}
      />
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
    color: colors.text,
  },
  headerActions: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  headerButton: {
    padding: 8,
    marginLeft: 8,
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    margin: 15,
    paddingHorizontal: 15,
    paddingVertical: 10,
    backgroundColor: colors.surface,
    borderRadius: 25,
  },
  searchInput: {
    flex: 1,
    marginLeft: 10,
    fontSize: 16,
    color: colors.text,
  },

  channelsList: {
    flex: 1,
  },
  channelItem: {
    flexDirection: 'row',
    padding: 15,
    backgroundColor: colors.background,
  },
  avatarContainer: {
    position: 'relative',
    marginRight: 12,
  },
  avatar: {
    fontSize: 40,
    width: 50,
    height: 50,
    textAlign: 'center',
    lineHeight: 50,
  },
  onlineIndicator: {
    position: 'absolute',
    bottom: 2,
    right: 2,
    width: 12,
    height: 12,
    borderRadius: 6,
    backgroundColor: '#34C759',
    borderWidth: 2,
    borderColor: colors.background,
  },
  channelContent: {
    flex: 1,
  },
  channelHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  channelName: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.text,
  },
  messageTime: {
    fontSize: 12,
    color: colors.textSecondary,
  },
  channelFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  lastMessage: {
    flex: 1,
    fontSize: 14,
    color: colors.textSecondary,
    marginRight: 8,
  },
  unreadBadge: {
    backgroundColor: colors.primary,
    borderRadius: 10,
    minWidth: 20,
    height: 20,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 6,
  },
  unreadText: {
    color: 'white',
    fontSize: 12,
    fontWeight: 'bold',
  },
  specialization: {
    fontSize: 12,
    fontStyle: 'italic',
  },
  separator: {
    height: 1,
    backgroundColor: colors.border,
    marginLeft: 77,
  },
  fabButton: {
    position: 'absolute',
    bottom: 20,
    right: 20,
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
    elevation: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 4,
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: spacing.xl,
    paddingVertical: spacing.xxl,
  },
  emptyTitle: {
    fontSize: fonts.size.lg,
    fontWeight: '600',
    color: colors.text,
    marginTop: spacing.md,
    marginBottom: spacing.sm,
  },
  emptySubtitle: {
    fontSize: fonts.size.md,
    color: colors.textSecondary,
    textAlign: 'center',
    lineHeight: 20,
  },
  modalContainer: {
    flex: 1,
    backgroundColor: colors.background,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  modalTitle: {
    fontSize: fonts.size.xl,
    fontWeight: '600',
    color: colors.text,
  },
  modalCloseButton: {
    padding: spacing.sm,
  },
}), []), []);
