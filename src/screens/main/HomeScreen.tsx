import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  Image,
  TextInput,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { colors } from '../../constants/theme';

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
    specialization: '健康诊断与建议'
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
    specialization: '医疗服务管理'
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
    specialization: '中医养生教育'
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
    specialization: '生活方式指导'
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
    specialization: '内科主任医师'
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
    specialization: '中医科副主任医师'
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
    specialization: '健康话题讨论'
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
    specialization: '普通用户'
  }
];

export const HomeScreen: React.FC = () => {
  const [channels, setChannels] = useState<ChatChannel[]>(CHAT_CHANNELS);
  const [searchText, setSearchText] = useState('');
  const [selectedFilter, setSelectedFilter] = useState<'all' | 'agent' | 'doctor' | 'user' | 'group'>('all');

  // 过滤聊天频道
  const filteredChannels = channels.filter(channel => {
    const matchesSearch = channel.name.toLowerCase().includes(searchText.toLowerCase()) ||
                         channel.lastMessage.toLowerCase().includes(searchText.toLowerCase());
    const matchesFilter = selectedFilter === 'all' || channel.type === selectedFilter;
    return matchesSearch && matchesFilter;
  });

  // 打开聊天
  const openChat = (channel: ChatChannel) => {
    if (channel.type === 'agent') {
      Alert.alert(
        `与${channel.name}对话`,
        `${channel.specialization}\n\n即将进入与${channel.name}的对话界面`,
        [
          { text: '取消', style: 'cancel' },
          { text: '开始对话', onPress: () => startAgentChat(channel) }
        ]
      );
    } else {
      Alert.alert('聊天功能', `即将打开与${channel.name}的聊天`);
    }
  };

  // 开始智能体对话
  const startAgentChat = (channel: ChatChannel) => {
    // 这里将集成实际的智能体服务
    console.log(`Starting chat with agent: ${channel.agentType}`);
    
    // 清除未读消息
    setChannels(prev => prev.map(ch => 
      ch.id === channel.id ? { ...ch, unreadCount: 0 } : ch
    ));
  };

  // 渲染频道过滤器
  const renderFilters = () => {
    const filters = [
      { key: 'all', label: '全部', icon: 'view-list' },
      { key: 'agent', label: '智能体', icon: 'robot' },
      { key: 'doctor', label: '医生', icon: 'doctor' },
      { key: 'user', label: '用户', icon: 'account' },
      { key: 'group', label: '群组', icon: 'account-group' }
    ];

    return (
      <View style={styles.filtersContainer}>
        {filters.map(filter => (
          <TouchableOpacity
            key={filter.key}
            style={[
              styles.filterButton,
              selectedFilter === filter.key && styles.activeFilterButton
            ]}
            onPress={() => setSelectedFilter(filter.key as any)}
          >
            <Icon 
              name={filter.icon} 
              size={16} 
              color={selectedFilter === filter.key ? colors.primary : colors.textSecondary} 
            />
            <Text style={[
              styles.filterText,
              selectedFilter === filter.key && styles.activeFilterText
            ]}>
              {filter.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
    );
  };

  // 渲染聊天频道项
  const renderChannelItem = ({ item }: { item: ChatChannel }) => {
    const getChannelColor = () => {
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
      {/* 头部 */}
      <View style={styles.header}>
        <Text style={styles.title}>聊天</Text>
        <TouchableOpacity style={styles.addButton}>
          <Icon name="plus" size={24} color={colors.primary} />
        </TouchableOpacity>
      </View>

      {/* 搜索框 */}
      <View style={styles.searchContainer}>
        <Icon name="magnify" size={20} color={colors.textSecondary} />
        <TextInput
          style={styles.searchInput}
          placeholder="搜索聊天、联系人..."
          value={searchText}
          onChangeText={setSearchText}
          placeholderTextColor={colors.textSecondary}
        />
      </View>

      {/* 过滤器 */}
      {renderFilters()}

      {/* 聊天频道列表 */}
      <FlatList
        data={filteredChannels}
        keyExtractor={item => item.id}
        renderItem={renderChannelItem}
        style={styles.channelsList}
        showsVerticalScrollIndicator={false}
        ItemSeparatorComponent={() => <View style={styles.separator} />}
      />

      {/* 快速操作按钮 */}
      <TouchableOpacity style={styles.fabButton}>
        <Icon name="message-plus" size={24} color="white" />
      </TouchableOpacity>
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
  addButton: {
    padding: 8,
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
  filtersContainer: {
    flexDirection: 'row',
    paddingHorizontal: 15,
    marginBottom: 10,
  },
  filterButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 6,
    marginRight: 8,
    borderRadius: 15,
    backgroundColor: colors.surface,
  },
  activeFilterButton: {
    backgroundColor: colors.primary + '20',
  },
  filterText: {
    marginLeft: 4,
    fontSize: 12,
    color: colors.textSecondary,
  },
  activeFilterText: {
    color: colors.primary,
    fontWeight: '600',
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
});
