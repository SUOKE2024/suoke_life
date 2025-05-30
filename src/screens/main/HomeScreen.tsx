import { SafeAreaView } from 'react-native-safe-area-context';
import { useChat, useContacts } from '../../hooks/useChat';
import { ChatChannel, Contact as ChatContact, AgentType } from '../../types/chat';
import { Contact as ContactsListContact } from '../../components/common/ContactsList';
import { colors, spacing, shadows } from '../../constants/theme';
import { HomeHeader } from '../components/HomeHeader';
import { SearchBar } from '../components/SearchBar';
import { EmptyState } from '../../components/common/EmptyState';
import { LoadingScreen } from '../../components/common/LoadingScreen';
import Icon from '../../components/common/Icon';
import NavigationTest from '../../components/NavigationTest';
import AgentChatInterface from '../../components/common/AgentChatInterface';
import ContactsList from '../../components/common/ContactsList';
import AccessibilitySettings from '../../components/common/AccessibilitySettings';
import {
import { useNavigation } from '@react-navigation/native';


import React, { useState, useCallback, useMemo } from 'react';
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  Image,
  Dimensions,
} from 'react-native';

// 类型转换函数
const convertToContactsListContact = useMemo(() => useMemo(() => useMemo(() => useCallback((contact: ChatContact): ContactsListContact | null => {
  if (!contact.id || !contact.name) {
    return null, []), []), []);
  }

  return {
    id: contact.id,
    name: contact.name,
    avatar: contact.avatar,
    status: contact.status || 'offline',
    lastSeen: contact.lastSeen,
    isOnline: contact.status === 'online',
    phone: contact.phone,
    email: contact.email,
    department: contact.department,
    role: contact.role,
    tags: contact.tags || [],
    notes: contact.notes,
    isFavorite: contact.isFavorite || false,
    isBlocked: contact.isBlocked || false,
    createdAt: contact.createdAt || new Date(),
    updatedAt: contact.updatedAt || new Date(),
  };
}, []);

// 组件导入

// 现有组件导入

const HomeScreen: React.FC = () => {
  const navigation = useMemo(() => useMemo(() => useMemo(() => useNavigation(), []), []), []);
  // 聊天相关状态
  const {
    channels,
    searchQuery,
    setSearchQuery,
    totalUnreadCount,
    startAgentChat,
    markAsRead,
    isLoading,
    error,
  } = useChat();

  // 联系人相关状态
  const { contacts } = useContacts();

  // 本地状态
  const [contactsVisible, setContactsVisible] = useState(false);
  const [agentChatVisible, setAgentChatVisible] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState<AgentType>('xiaoai');
  const [accessibilitySettingsVisible, setAccessibilitySettingsVisible] = useState(false);
  const [accessibilityEnabled, setAccessibilityEnabled] = useState(false);
  const [navigationTestVisible, setNavigationTestVisible] = useState(false);

  // 处理频道点击
  const handleChannelPress = useMemo(() => useMemo(() => useMemo(() => useCallback((channel: ChatChannel) => {
    console.log('频道被点击:', channel.name), []), []), []);
    
    // 根据频道类型导航到不同页面
    switch (channel.id) {
      case 'xiaoai':
        navigation.navigate('Chat', { 
          channelId: channel.id,
          channelName: channel.name,
          agentType: 'xiaoai'
        });
        break;
      case 'xiaoke':
        navigation.navigate('Chat', { 
          channelId: channel.id,
          channelName: channel.name,
          agentType: 'xiaoke'
        });
        break;
      case 'laoke':
        navigation.navigate('Chat', { 
          channelId: channel.id,
          channelName: channel.name,
          agentType: 'laoke'
        });
        break;
      case 'soer':
        navigation.navigate('Chat', { 
          channelId: channel.id,
          channelName: channel.name,
          agentType: 'soer'
        });
        break;
      default:
        navigation.navigate('Chat', { 
          channelId: channel.id,
          channelName: channel.name
        });
    }
  }, [navigation]);

  // 处理联系人点击
  const handleContactPress = useMemo(() => useMemo(() => useMemo(() => useCallback((contact: ContactsListContact) => {
    console.log('联系人被点击:', contact.name), []), []), []);
    navigation.navigate('Chat', { 
      contactId: contact.id,
      contactName: contact.name
    });
  }, [navigation]);

  // 渲染频道项
  const renderChannelItem = useMemo(() => useMemo(() => useMemo(() => useCallback(({ item }: { item: ChatChannel }) => (
    <TouchableOpacity
      style={styles.channelItem}
      onPress={() => handleChannelPress(item)}
    >
      <Text style={styles.channelIcon}>{item.icon}</Text>
      <Text style={styles.channelName}>{item.name}</Text>
    </TouchableOpacity>
  ), [handleChannelPress]), []), []), []);

  // 获取列表项的key
  const keyExtractor = useMemo(() => useMemo(() => useMemo(() => useCallback((item: ChatChannel) => item.id, []), []), []), []);

  // 空状态组件
  const renderEmptyState = useMemo(() => useMemo(() => useMemo(() => useMemo(() => (
    <View style={styles.emptyContainer}>
      <Text style={styles.emptyTitle}>欢迎来到索克生活</Text>
      <Text style={styles.emptySubtitle}>
        选择一个智能体开始您的健康管理之旅
      </Text>
      <View style={styles.agentGrid}>
        <View style={styles.agentCard}>
          <Text style={styles.agentIcon}>🤖</Text>
          <Text style={styles.agentName}>小艾</Text>
          <Text style={styles.agentDesc}>健康助手</Text>
        </View>
        <View style={styles.agentCard}>
          <Text style={styles.agentIcon}>👨‍⚕️</Text>
          <Text style={styles.agentName}>小克</Text>
          <Text style={styles.agentDesc}>诊断专家</Text>
        </View>
        <View style={styles.agentCard}>
          <Text style={styles.agentIcon}>👴</Text>
          <Text style={styles.agentName}>老克</Text>
          <Text style={styles.agentDesc}>中医大师</Text>
        </View>
        <View style={styles.agentCard}>
          <Text style={styles.agentIcon}>👧</Text>
          <Text style={styles.agentName}>索儿</Text>
          <Text style={styles.agentDesc}>生活伙伴</Text>
        </View>
      </View>
    </View>
  ), []), []), []), []);

  // 如果正在加载，显示加载屏幕
  if (isLoading && channels.length === 0) {
    return <LoadingScreen message="加载聊天记录..." />;
  }

  return (
    <SafeAreaView style={styles.container}>
      {/* 头部 */}
      <HomeHeader
        title="索克生活"
        unreadCount={totalUnreadCount}
        onContactsPress={() => setContactsVisible(true)}
        onAccessibilityPress={() => setAccessibilitySettingsVisible(true)}
        onNavigationTestPress={() => setNavigationTestVisible(true)}
      />

      {/* 搜索栏 */}
      <SearchBar
        value={searchQuery}
        onChangeText={setSearchQuery}
        placeholder="搜索聊天记录..."
      />

      {/* 聊天频道列表 */}
      <FlatList
        style={styles.channelsList}
        data={channels}
        renderItem={renderChannelItem}
        keyExtractor={keyExtractor}
        ListEmptyComponent={renderEmptyState}
        showsVerticalScrollIndicator={false}
        removeClippedSubviews={true}
        maxToRenderPerBatch={10}
        windowSize={10}
        initialNumToRender={10}
        getItemLayout={(data, index) => ({
          length: 80, // 估算的项目高度
          offset: 80 * index,
          index,
        })}
      />

      {/* 快速操作按钮 */}
      <TouchableOpacity 
        style={styles.fabButton}
        onPress={() => setContactsVisible(true)}
        activeOpacity={0.8}
      >
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
            <TouchableOpacity
              onPress={() => setContactsVisible(false)}
              style={styles.modalCloseButton}
            >
              <Icon name="close" size={24} color={colors.text} />
            </TouchableOpacity>
          </View>
          <ContactsList
            contacts={contacts.map(convertToContactsListContact).filter((contact): contact is ContactsListContact => contact !== null)}
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

      {/* 导航测试模态框 */}
      <Modal
        visible={navigationTestVisible}
        animationType="slide"
        presentationStyle="pageSheet"
        onRequestClose={() => setNavigationTestVisible(false)}
      >
        <SafeAreaView style={styles.modalContainer}>
          <View style={styles.modalHeader}>
            <TouchableOpacity
              onPress={() => setNavigationTestVisible(false)}
              style={styles.modalCloseButton}
            >
              <Icon name="close" size={24} color={colors.text} />
            </TouchableOpacity>
          </View>
          <NavigationTest />
        </SafeAreaView>
      </Modal>
    </SafeAreaView>
  );
};

const styles = useMemo(() => useMemo(() => useMemo(() => StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  channelsList: {
    flex: 1,
  },
  fabButton: {
    position: 'absolute',
    bottom: spacing.xl,
    right: spacing.xl,
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
    ...shadows.lg,
  },
  modalContainer: {
    flex: 1,
    backgroundColor: colors.background,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  modalCloseButton: {
    padding: spacing.sm,
    borderRadius: 20,
    backgroundColor: colors.surface,
    ...shadows.sm,
  },
  channelItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing.md,
  },
  channelIcon: {
    fontSize: 24,
    marginRight: spacing.md,
  },
  channelName: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: spacing.md,
  },
  emptySubtitle: {
    fontSize: 16,
    textAlign: 'center',
  },
  agentGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  agentCard: {
    width: Dimensions.get('window').width / 2 - spacing.md,
    padding: spacing.md,
    margin: spacing.md,
    backgroundColor: colors.surface,
    borderRadius: 8,
    alignItems: 'center',
  },
  agentIcon: {
    fontSize: 48,
    marginBottom: spacing.md,
  },
  agentName: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  agentDesc: {
    fontSize: 14,
    textAlign: 'center',
  },
}), []), []), []);

export default React.memo(HomeScreen); 