import React, { useState } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  Alert,
  RefreshControl,
} from 'react-native';
import {
  Appbar,
  Card,
  Title,
  Paragraph,
  Button,
  Text,
  Surface,
  Chip,
  FAB,
  Portal,
  Modal,
  TextInput,
  Divider,
  List,
} from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { useTheme } from 'react-native-paper';
import { useTranslation } from 'react-i18next';

interface ChatHistoryScreenProps {
  navigation: any;
}

interface ChatSession {
  id: string;
  agentType: 'xiaoai' | 'xiaoke' | 'laoke' | 'soer';
  title: string;
  lastMessage: string;
  timestamp: Date;
  messageCount: number;
  tags: string[];
  summary?: string;
  isBookmarked: boolean;
}

interface Message {
  id: string;
  type: 'user' | 'agent';
  content: string;
  timestamp: Date;
  agentType?: 'xiaoai' | 'xiaoke' | 'laoke' | 'soer';
}

const ChatHistoryScreen: React.FC<ChatHistoryScreenProps> = ({ navigation }) => {
  const theme = useTheme();
  const { t } = useTranslation();
  const [refreshing, setRefreshing] = useState(false);
  const [showSearchModal, setShowSearchModal] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFilter, setSelectedFilter] = useState<string>('all');

  const [chatSessions, setChatSessions] = useState<ChatSession[]>([
    {
      id: '1',
      agentType: 'xiaoai',
      title: '春季养生咨询',
      lastMessage: '建议您多食用时令蔬菜，注意调节作息时间',
      timestamp: new Date(2024, 2, 15, 14, 30),
      messageCount: 12,
      tags: ['养生', '春季', '饮食'],
      summary: '讨论了春季养生的基本原则，包括饮食调理和作息调整',
      isBookmarked: true,
    },
    {
      id: '2',
      agentType: 'xiaoke',
      title: '体检报告解读',
      lastMessage: '您的血压指标正常，建议继续保持良好的生活习惯',
      timestamp: new Date(2024, 2, 14, 10, 15),
      messageCount: 8,
      tags: ['体检', '血压', '健康指标'],
      summary: '解读了最新体检报告，各项指标基本正常',
      isBookmarked: false,
    },
    {
      id: '3',
      agentType: 'laoke',
      title: '中医基础理论学习',
      lastMessage: '阴阳五行理论是中医的核心理论基础',
      timestamp: new Date(2024, 2, 13, 16, 45),
      messageCount: 25,
      tags: ['中医理论', '阴阳五行', '学习'],
      summary: '学习了中医基础理论，重点讨论了阴阳五行的概念',
      isBookmarked: true,
    },
    {
      id: '4',
      agentType: 'soer',
      title: '健康计划制定',
      lastMessage: '已为您制定了个性化的健康管理计划',
      timestamp: new Date(2024, 2, 12, 9, 20),
      messageCount: 15,
      tags: ['健康计划', '个性化', '管理'],
      summary: '制定了包含运动、饮食、睡眠的综合健康计划',
      isBookmarked: false,
    },
    {
      id: '5',
      agentType: 'xiaoai',
      title: '失眠问题咨询',
      lastMessage: '建议您尝试睡前冥想和放松练习',
      timestamp: new Date(2024, 2, 11, 22, 10),
      messageCount: 18,
      tags: ['失眠', '睡眠', '冥想'],
      summary: '讨论了失眠的原因和改善方法',
      isBookmarked: false,
    },
  ]);

  const agentConfigs = {
    xiaoai: { name: '小艾', color: '#FF6B6B', icon: 'heart-pulse' },
    xiaoke: { name: '小克', color: '#4ECDC4', icon: 'medical-bag' },
    laoke: { name: '老克', color: '#45B7D1', icon: 'school' },
    soer: { name: '索儿', color: '#96CEB4', icon: 'account-heart' },
  };

  const filterOptions = [
    { value: 'all', label: '全部', icon: 'view-list' },
    { value: 'xiaoai', label: '小艾', icon: 'heart-pulse' },
    { value: 'xiaoke', label: '小克', icon: 'medical-bag' },
    { value: 'laoke', label: '老克', icon: 'school' },
    { value: 'soer', label: '索儿', icon: 'account-heart' },
    { value: 'bookmarked', label: '收藏', icon: 'bookmark' },
  ];

  const filteredSessions = chatSessions.filter(session => {
    if (selectedFilter === 'all') return true;
    if (selectedFilter === 'bookmarked') return session.isBookmarked;
    return session.agentType === selectedFilter;
  }).filter(session => {
    if (!searchQuery) return true;
    return session.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
           session.lastMessage.toLowerCase().includes(searchQuery.toLowerCase()) ||
           session.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
  });

  const sortedSessions = filteredSessions.sort((a, b) => 
    b.timestamp.getTime() - a.timestamp.getTime()
  );

  const handleRefresh = async () => {
    setRefreshing(true);
    // 模拟刷新数据
    setTimeout(() => {
      setRefreshing(false);
    }, 1000);
  };

  const handleDeleteSession = (sessionId: string) => {
    Alert.alert(
      '确认删除',
      '确定要删除这个对话记录吗？此操作不可恢复。',
      [
        { text: '取消', style: 'cancel' },
        {
          text: '删除',
          style: 'destructive',
          onPress: () => {
            setChatSessions(prev => prev.filter(session => session.id !== sessionId));
          },
        },
      ]
    );
  };

  const handleBookmarkSession = (sessionId: string) => {
    setChatSessions(prev => prev.map(session => 
      session.id === sessionId 
        ? { ...session, isBookmarked: !session.isBookmarked }
        : session
    ));
  };

  const formatTimestamp = (date: Date) => {
    const now = new Date();
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);
    
    if (diffInHours < 1) {
      return '刚刚';
    } else if (diffInHours < 24) {
      return `${Math.floor(diffInHours)}小时前`;
    } else if (diffInHours < 24 * 7) {
      return `${Math.floor(diffInHours / 24)}天前`;
    } else {
      return date.toLocaleDateString('zh-CN');
    }
  };

  const renderSessionCard = (session: ChatSession) => {
    const agentConfig = agentConfigs[session.agentType];
    
    return (
      <Card 
        key={session.id} 
        style={styles.sessionCard}
        onPress={() => navigation.navigate('AgentChat', { 
          agentType: session.agentType,
          sessionId: session.id 
        })}
      >
        <Card.Content>
          <View style={styles.sessionHeader}>
            <View style={styles.agentInfo}>
              <View style={[styles.agentIcon, { backgroundColor: agentConfig.color }]}>
                <Icon name={agentConfig.icon} size={20} color="white" />
              </View>
              <View style={styles.sessionInfo}>
                <Text style={styles.agentName}>{agentConfig.name}</Text>
                <Text style={styles.sessionTitle}>{session.title}</Text>
              </View>
            </View>
            
            <View style={styles.sessionMeta}>
              <Text style={styles.timestamp}>{formatTimestamp(session.timestamp)}</Text>
              <View style={styles.sessionActions}>
                <Button
                  mode="text"
                  onPress={() => handleBookmarkSession(session.id)}
                  compact
                >
                  <Icon 
                    name={session.isBookmarked ? 'bookmark' : 'bookmark-outline'} 
                    size={16} 
                    color={session.isBookmarked ? theme.colors.primary : theme.colors.onSurfaceVariant}
                  />
                </Button>
                <Button
                  mode="text"
                  onPress={() => handleDeleteSession(session.id)}
                  textColor={theme.colors.error}
                  compact
                >
                  <Icon name="delete-outline" size={16} />
                </Button>
              </View>
            </View>
          </View>

          <Paragraph style={styles.lastMessage} numberOfLines={2}>
            {session.lastMessage}
          </Paragraph>

          {session.summary && (
            <Text style={styles.summary} numberOfLines={1}>
              摘要: {session.summary}
            </Text>
          )}

          <View style={styles.sessionFooter}>
            <View style={styles.tagsContainer}>
              {session.tags.slice(0, 3).map((tag, index) => (
                <Chip key={index} style={styles.tag} textStyle={styles.tagText}>
                  {tag}
                </Chip>
              ))}
              {session.tags.length > 3 && (
                <Text style={styles.moreTagsText}>+{session.tags.length - 3}</Text>
              )}
            </View>
            
            <View style={styles.messageCount}>
              <Icon name="message-text" size={14} color={theme.colors.onSurfaceVariant} />
              <Text style={styles.messageCountText}>{session.messageCount}</Text>
            </View>
          </View>
        </Card.Content>
      </Card>
    );
  };

  const renderFilterChips = () => (
    <ScrollView 
      horizontal 
      showsHorizontalScrollIndicator={false}
      style={styles.filterContainer}
      contentContainerStyle={styles.filterContent}
    >
      {filterOptions.map(option => (
        <Chip
          key={option.value}
          mode={selectedFilter === option.value ? 'flat' : 'outlined'}
          selected={selectedFilter === option.value}
          onPress={() => setSelectedFilter(option.value)}
          style={styles.filterChip}
          icon={option.icon}
        >
          {option.label}
        </Chip>
      ))}
    </ScrollView>
  );

  const renderEmptyState = () => (
    <Surface style={styles.emptyContainer}>
      <Icon name="chat-outline" size={64} color={theme.colors.onSurfaceVariant} />
      <Title style={styles.emptyTitle}>暂无对话记录</Title>
      <Paragraph style={styles.emptyDescription}>
        开始与智能体对话，您的聊天记录将显示在这里
      </Paragraph>
      <Button
        mode="contained"
        onPress={() => navigation.navigate('AgentSelection')}
        style={styles.emptyAction}
        icon="plus"
      >
        开始对话
      </Button>
    </Surface>
  );

  return (
    <SafeAreaView style={styles.container}>
      <Appbar.Header>
        <Appbar.BackAction onPress={() => navigation.goBack()} />
        <Appbar.Content title="对话历史" />
        <Appbar.Action icon="magnify" onPress={() => setShowSearchModal(true)} />
        <Appbar.Action icon="filter-variant" onPress={() => {/* 高级筛选 */}} />
      </Appbar.Header>

      <View style={styles.content}>
        {renderFilterChips()}
        
        <ScrollView
          style={styles.sessionsList}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />
          }
        >
          {sortedSessions.length === 0 ? (
            renderEmptyState()
          ) : (
            sortedSessions.map(session => renderSessionCard(session))
          )}
        </ScrollView>

        <FAB
          icon="plus"
          style={styles.fab}
          onPress={() => navigation.navigate('AgentSelection')}
        />

        {/* 搜索模态框 */}
        <Portal>
          <Modal
            visible={showSearchModal}
            onDismiss={() => setShowSearchModal(false)}
            contentContainerStyle={styles.searchModal}
          >
            <Title style={styles.modalTitle}>搜索对话</Title>
            <TextInput
              label="搜索关键词"
              value={searchQuery}
              onChangeText={setSearchQuery}
              style={styles.searchInput}
              mode="outlined"
              placeholder="输入标题、内容或标签"
              autoFocus
            />
            <Divider style={styles.divider} />
            <View style={styles.modalActions}>
              <Button
                mode="outlined"
                onPress={() => {
                  setSearchQuery('');
                  setShowSearchModal(false);
                }}
                style={styles.modalButton}
              >
                清除
              </Button>
              <Button
                mode="contained"
                onPress={() => setShowSearchModal(false)}
                style={styles.modalButton}
              >
                搜索
              </Button>
            </View>
          </Modal>
        </Portal>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  content: {
    flex: 1,
  },
  filterContainer: {
    paddingVertical: 8,
  },
  filterContent: {
    paddingHorizontal: 16,
    gap: 8,
  },
  filterChip: {
    marginRight: 8,
  },
  sessionsList: {
    flex: 1,
    padding: 16,
  },
  sessionCard: {
    marginBottom: 12,
    borderRadius: 12,
  },
  sessionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  agentInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  agentIcon: {
    width: 36,
    height: 36,
    borderRadius: 18,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  sessionInfo: {
    flex: 1,
  },
  agentName: {
    fontSize: 12,
    color: '#666',
    marginBottom: 2,
  },
  sessionTitle: {
    fontSize: 16,
    fontWeight: '500',
    lineHeight: 20,
  },
  sessionMeta: {
    alignItems: 'flex-end',
  },
  timestamp: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  sessionActions: {
    flexDirection: 'row',
  },
  lastMessage: {
    fontSize: 14,
    lineHeight: 18,
    color: '#666',
    marginBottom: 8,
  },
  summary: {
    fontSize: 12,
    color: '#999',
    fontStyle: 'italic',
    marginBottom: 8,
  },
  sessionFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  tagsContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  tag: {
    marginRight: 6,
    height: 20,
  },
  tagText: {
    fontSize: 10,
  },
  moreTagsText: {
    fontSize: 10,
    color: '#666',
  },
  messageCount: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  messageCountText: {
    marginLeft: 4,
    fontSize: 12,
    color: '#666',
  },
  emptyContainer: {
    alignItems: 'center',
    padding: 32,
    borderRadius: 12,
    marginTop: 32,
  },
  emptyTitle: {
    marginTop: 16,
    marginBottom: 8,
  },
  emptyDescription: {
    textAlign: 'center',
    color: '#666',
    marginBottom: 16,
  },
  emptyAction: {
    marginTop: 8,
  },
  fab: {
    position: 'absolute',
    margin: 16,
    right: 0,
    bottom: 0,
  },
  searchModal: {
    backgroundColor: 'white',
    padding: 20,
    margin: 20,
    borderRadius: 12,
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 16,
    textAlign: 'center',
  },
  searchInput: {
    marginBottom: 16,
  },
  divider: {
    marginBottom: 16,
  },
  modalActions: {
    flexDirection: 'row',
    gap: 16,
  },
  modalButton: {
    flex: 1,
  },
});

export default ChatHistoryScreen;