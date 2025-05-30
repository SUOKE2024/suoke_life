import {
import { SafeAreaView } from 'react-native-safe-area-context';
import { useChat, useContacts } from '../../hooks/useChat';
import { ChatChannel, Contact as ChatContact, AgentType } from '../../types/chat';
import { Contact as ContactsListContact } from '../../components/common/ContactsList';
import { colors, spacing, shadows } from '../../constants/theme';
import { HomeHeader } from '../components/HomeHeader';
import { SearchBar } from '../components/SearchBar';
import { ChatChannelItem } from '../components/ChatChannelItem';
import { EmptyState } from '../../components/common/EmptyState';
import { LoadingScreen } from '../../components/common/LoadingScreen';
import Icon from '../../components/common/Icon';
import NavigationTest from '../../components/NavigationTest';
import AgentChatInterface from '../../components/common/AgentChatInterface';
import ContactsList from '../../components/common/ContactsList';
import AccessibilitySettings from '../../components/common/AccessibilitySettings';



import React, { useState, useCallback, useMemo } from 'react';
  View,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  Modal,
  Alert,
} from 'react-native';

// 类型转换函数
const convertToContactsListContact = useMemo(() => useMemo(() => (contact: ChatContact): ContactsListContact | null => {
  // 过滤掉group类型，因为ContactsList不支持
  if (contact.type === 'group') {return null, []), []);}
  
  return {
    id: contact.id,
    name: contact.name,
    type: contact.type as 'agent' | 'user' | 'doctor',
    agentType: contact.agentType,
    avatar: contact.avatar,
    isOnline: contact.isOnline,
    lastSeen: contact.lastSeen,
    specialization: contact.specialization,
    department: contact.department,
    title: contact.title,
  };
};

// 组件导入

// 现有组件导入

const HomeScreen: React.FC = () => {
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
  const handleChannelPress = useMemo(() => useMemo(() => useCallback((channel: ChatChannel) => {
    if (channel.type === 'agent' && channel.agentType) {
      setSelectedAgent(channel.agentType), []), []);
      setAgentChatVisible(true);
      startAgentChat(channel.agentType);
    } else {
      // 处理其他类型的频道
      markAsRead(channel.id);
      Alert.alert('提示', `打开与 ${channel.name} 的聊天`);
    }
  }, [startAgentChat, markAsRead]);

  // 处理联系人点击
  const handleContactPress = useMemo(() => useMemo(() => useCallback((contact: ContactsListContact) => {
    setContactsVisible(false), []), []);
    
    if (contact.type === 'agent' && contact.agentType) {
      setSelectedAgent(contact.agentType);
      setAgentChatVisible(true);
      startAgentChat(contact.agentType);
    } else {
      Alert.alert('提示', `开始与 ${contact.name} 聊天`);
    }
  }, [startAgentChat]);

  // 渲染频道项
  const renderChannelItem = useMemo(() => useMemo(() => useCallback(({ item }: { item: ChatChannel }) => (
    <ChatChannelItem
      channel={item}
      onPress={handleChannelPress}
    />
  ), [handleChannelPress]), []), []);

  // 获取列表项的key
  const keyExtractor = useMemo(() => useMemo(() => useCallback((item: ChatChannel) => item.id, []), []), []);

  // 空状态组件
  const renderEmptyState = useMemo(() => useMemo(() => useMemo(() => (
    <EmptyState
      icon="message-outline"
      title="暂无聊天记录"
      subtitle="点击右上角联系人图标开始聊天"
    />
  ), []), []), []);

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

const styles = useMemo(() => useMemo(() => StyleSheet.create({
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
}), []), []);

export default HomeScreen; 