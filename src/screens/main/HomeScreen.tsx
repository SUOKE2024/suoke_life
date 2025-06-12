import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
  Dimensions,
  Alert,
  TextInput,
  FlatList,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { useNavigation } from '@react-navigation/native';

// 导入服务
import { IntegratedApiService } from '../../services/IntegratedApiService';

const { width: screenWidth } = Dimensions.get('window');

// 聊天对象类型定义
interface ChatContact {
  id: string;
  name: string;
  type: 'agent' | 'user' | 'doctor' | 'service_provider' | 'supplier';
  avatar: string;
  status: 'online' | 'offline' | 'busy';
  lastMessage?: string;
  lastMessageTime?: string;
  unreadCount?: number;
  description?: string;
  specialties?: string[];
  rating?: number;
  isTop?: boolean; // 是否置顶
}

const HomeScreen: React.FC = () => {
  const navigation = useNavigation();
  const [refreshing, setRefreshing] = useState(false);
  const [chatList, setChatList] = useState<ChatContact[]>([]);
  const [searchText, setSearchText] = useState('');
  const [filteredChatList, setFilteredChatList] = useState<ChatContact[]>([]);
  const apiService = new IntegratedApiService();

  // 初始化聊天列表数据
  useEffect(() => {
    initializeChatList();
  }, []);

  // 搜索过滤
  useEffect(() => {
    if (searchText.trim()) {
      const filtered = chatList.filter(contact =>
        contact.name.toLowerCase().includes(searchText.toLowerCase()) ||
        contact.description?.toLowerCase().includes(searchText.toLowerCase())
      );
      setFilteredChatList(filtered);
    } else {
      setFilteredChatList(chatList);
    }
  }, [searchText, chatList]);

  const initializeChatList = useCallback(async () => {
    try {
      // 模拟聊天列表数据，类似微信聊天列表
      const contacts: ChatContact[] = [
        // 智能体助手（置顶）
        {
          id: 'xiaoai',
          name: '小艾',
          type: 'agent',
          avatar: '🤖',
          status: 'online',
          lastMessage: '您好！我是小艾，您的健康管理助手。有什么可以帮您的吗？',
          lastMessageTime: '刚刚',
          unreadCount: 0,
          description: '多模态感知专家，擅长图像分析、语音处理和健康监测',
          specialties: ['图像分析', '语音识别', '健康监测', '五诊协调'],
          rating: 4.9,
          isTop: true,
        },
        {
          id: 'xiaoke',
          name: '小克',
          type: 'agent',
          avatar: '🏥',
          status: 'online',
          lastMessage: '为您推荐了几个优质的健康服务',
          lastMessageTime: '5分钟前',
          unreadCount: 2,
          description: '健康服务专家，提供产品推荐和预约管理',
          specialties: ['健康服务', '产品推荐', '预约管理', '用户体验'],
          rating: 4.8,
          isTop: true,
        },
        {
          id: 'laoke',
          name: '老克',
          type: 'agent',
          avatar: '👨‍⚕️',
          status: 'busy',
          lastMessage: '今天的中医养生知识分享已更新',
          lastMessageTime: '1小时前',
          unreadCount: 1,
          description: '知识传播专家，专注中医文化和社区管理',
          specialties: ['中医知识', '文化传播', '社区管理', '教育服务'],
          rating: 4.9,
          isTop: true,
        },
        {
          id: 'soer',
          name: '索儿',
          type: 'agent',
          avatar: '📊',
          status: 'online',
          lastMessage: '您的营养计划已优化完成',
          lastMessageTime: '30分钟前',
          unreadCount: 0,
          description: '营养管理专家，优化生活方式和饮食搭配',
          specialties: ['营养管理', '生活方式', '数据分析', '个性化推荐'],
          rating: 4.7,
          isTop: true,
        },
        // 名医专家
        {
          id: 'dr_zhang',
          name: '张主任',
          type: 'doctor',
          avatar: '👨‍⚕️',
          status: 'online',
          lastMessage: '您的检查报告我已经看过了，建议...',
          lastMessageTime: '2小时前',
          unreadCount: 1,
          description: '中医内科主任医师，30年临床经验',
          specialties: ['中医内科', '慢性病调理', '体质辨识'],
          rating: 4.9,
        },
        {
          id: 'dr_li',
          name: '李医生',
          type: 'doctor',
          avatar: '👩‍⚕️',
          status: 'offline',
          lastMessage: '明天上午10点记得来复诊',
          lastMessageTime: '昨天',
          unreadCount: 0,
          description: '营养科副主任医师，擅长营养调理',
          specialties: ['营养科', '饮食调理', '代谢疾病'],
          rating: 4.8,
        },
        // 服务商
        {
          id: 'health_center',
          name: '康复中心',
          type: 'service_provider',
          avatar: '🏥',
          status: 'online',
          lastMessage: '新的康复课程已上线，欢迎预约体验',
          lastMessageTime: '1小时前',
          unreadCount: 3,
          description: '专业康复理疗中心',
          specialties: ['康复理疗', '运动康复', '慢病管理'],
          rating: 4.6,
        },
        {
          id: 'wellness_spa',
          name: '养生会所',
          type: 'service_provider',
          avatar: '🧘‍♀️',
          status: 'online',
          lastMessage: '本周养生套餐优惠活动开始啦',
          lastMessageTime: '3小时前',
          unreadCount: 1,
          description: '高端养生理疗会所',
          specialties: ['中医养生', '理疗按摩', '健康管理'],
          rating: 4.7,
        },
        // 供应商
        {
          id: 'herb_supplier',
          name: '本草堂',
          type: 'supplier',
          avatar: '🌿',
          status: 'online',
          lastMessage: '您订购的中药材已发货，预计明天到达',
          lastMessageTime: '4小时前',
          unreadCount: 0,
          description: '优质中药材供应商',
          specialties: ['中药材', '养生茶', '保健品'],
          rating: 4.8,
        },
        {
          id: 'organic_farm',
          name: '有机农场',
          type: 'supplier',
          avatar: '🥬',
          status: 'offline',
          lastMessage: '新鲜有机蔬菜配送服务',
          lastMessageTime: '昨天',
          unreadCount: 0,
          description: '有机农产品直供',
          specialties: ['有机蔬菜', '健康食材', '农场直供'],
          rating: 4.5,
        },
        // 普通用户
        {
          id: 'user_wang',
          name: '王女士',
          type: 'user',
          avatar: '👩',
          status: 'online',
          lastMessage: '谢谢您的建议，我会按时服药的',
          lastMessageTime: '6小时前',
          unreadCount: 0,
          description: '健康管理用户',
        },
      ];

      // 按置顶和时间排序
      const sortedContacts = contacts.sort((a, b) => {
        if (a.isTop && !b.isTop) return -1;
        if (!a.isTop && b.isTop) return 1;
        // 这里可以添加更复杂的时间排序逻辑
        return 0;
      });

      setChatList(sortedContacts);
    } catch (error) {
      console.error('初始化聊天列表失败:', error);
      Alert.alert('错误', '加载聊天列表失败，请稍后重试');
    }
  }, []);

  // 刷新数据
  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    try {
      await initializeChatList();
    } catch (error) {
      console.error('刷新失败:', error);
    } finally {
      setRefreshing(false);
    }
  }, [initializeChatList]);

  // 开始聊天
  const startChat = useCallback(async (contact: ChatContact) => {
    try {
      if (contact.type === 'agent') {
        // 智能体聊天
        navigation.navigate('AgentChat' as never, {
          agentId: contact.id,
          agentName: contact.name,
          agentType: contact.type,
        } as never);
      } else {
        // 其他类型聊天
        navigation.navigate('Chat' as never, {
          contactId: contact.id,
          contactName: contact.name,
          contactType: contact.type,
        } as never);
      }
    } catch (error) {
      console.error('启动聊天失败:', error);
      Alert.alert('错误', '无法启动聊天，请稍后重试');
    }
  }, [navigation]);

  // 获取状态颜色
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online':
        return '#4CAF50';
      case 'busy':
        return '#FF9800';
      case 'offline':
        return '#9E9E9E';
      default:
        return '#9E9E9E';
    }
  };

  // 获取类型标签
  const getTypeLabel = (type: string) => {
    switch (type) {
      case 'agent':
        return '智能体';
      case 'doctor':
        return '名医';
      case 'service_provider':
        return '服务商';
      case 'supplier':
        return '供应商';
      case 'user':
        return '用户';
      default:
        return '';
    }
  };

  // 获取类型颜色
  const getTypeColor = (type: string) => {
    switch (type) {
      case 'agent':
        return '#2196F3';
      case 'doctor':
        return '#4CAF50';
      case 'service_provider':
        return '#FF9800';
      case 'supplier':
        return '#9C27B0';
      case 'user':
        return '#607D8B';
      default:
        return '#999';
    }
  };

  // 渲染聊天项目
  const renderChatItem = ({ item }: { item: ChatContact }) => (
    <TouchableOpacity
      style={[styles.chatItem, item.isTop && styles.topChatItem]}
      onPress={() => startChat(item)}
      activeOpacity={0.7}
    >
      <View style={styles.avatarContainer}>
        <Text style={styles.avatar}>{item.avatar}</Text>
        <View
          style={[
            styles.statusDot,
            { backgroundColor: getStatusColor(item.status) },
          ]}
        />
        {item.unreadCount && item.unreadCount > 0 && (
          <View style={styles.unreadBadge}>
            <Text style={styles.unreadText}>
              {item.unreadCount > 99 ? '99+' : item.unreadCount}
            </Text>
          </View>
        )}
      </View>

      <View style={styles.chatContent}>
        <View style={styles.chatHeader}>
          <View style={styles.nameContainer}>
            <Text style={styles.contactName}>{item.name}</Text>
            {item.isTop && (
              <Icon name="push-pin" size={12} color="#FF9800" style={styles.topIcon} />
            )}
            <View style={[styles.typeTag, { backgroundColor: getTypeColor(item.type) }]}>
              <Text style={styles.typeText}>{getTypeLabel(item.type)}</Text>
            </View>
          </View>
          <Text style={styles.lastMessageTime}>{item.lastMessageTime}</Text>
        </View>

        <View style={styles.messageContainer}>
          <Text style={styles.lastMessage} numberOfLines={1}>
            {item.lastMessage || '暂无消息'}
          </Text>
          {item.unreadCount && item.unreadCount > 0 && (
            <View style={styles.unreadIndicator} />
          )}
        </View>
      </View>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      {/* 头部搜索栏 */}
      <View style={styles.header}>
        <View style={styles.searchContainer}>
          <Icon name="search" size={20} color="#999" style={styles.searchIcon} />
          <TextInput
            style={styles.searchInput}
            value={searchText}
            onChangeText={setSearchText}
            placeholder="搜索联系人"
            placeholderTextColor="#999"
          />
          {searchText.length > 0 && (
            <TouchableOpacity
              style={styles.clearButton}
              onPress={() => setSearchText('')}
            >
              <Icon name="clear" size={20} color="#999" />
            </TouchableOpacity>
          )}
        </View>
        <TouchableOpacity
          style={styles.addButton}
          onPress={() => navigation.navigate('NewChat' as never)}
        >
          <Icon name="add" size={24} color="#2196F3" />
        </TouchableOpacity>
      </View>

      {/* 聊天列表 */}
      <FlatList
        data={filteredChatList}
        renderItem={renderChatItem}
        keyExtractor={(item) => item.id}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        showsVerticalScrollIndicator={false}
        contentContainerStyle={styles.listContainer}
        ItemSeparatorComponent={() => <View style={styles.separator} />}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#ffffff',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#ffffff',
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  searchContainer: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
    borderRadius: 20,
    paddingHorizontal: 12,
    marginRight: 12,
  },
  searchIcon: {
    marginRight: 8,
  },
  searchInput: {
    flex: 1,
    height: 36,
    fontSize: 16,
    color: '#333',
  },
  clearButton: {
    padding: 4,
  },
  addButton: {
    padding: 4,
  },
  listContainer: {
    paddingVertical: 8,
  },
  chatItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#ffffff',
  },
  topChatItem: {
    backgroundColor: '#fafafa',
  },
  avatarContainer: {
    position: 'relative',
    marginRight: 12,
  },
  avatar: {
    fontSize: 24,
    width: 48,
    height: 48,
    textAlign: 'center',
    lineHeight: 48,
  },
  statusDot: {
    position: 'absolute',
    bottom: 2,
    right: 2,
    width: 12,
    height: 12,
    borderRadius: 6,
    borderWidth: 2,
    borderColor: '#ffffff',
  },
  unreadBadge: {
    position: 'absolute',
    top: -4,
    right: -4,
    backgroundColor: '#FF4444',
    borderRadius: 10,
    minWidth: 20,
    height: 20,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 6,
  },
  unreadText: {
    color: '#ffffff',
    fontSize: 10,
    fontWeight: 'bold',
  },
  chatContent: {
    flex: 1,
  },
  chatHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  nameContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  contactName: {
    fontSize: 16,
    fontWeight: '500',
    color: '#333',
    marginRight: 6,
  },
  topIcon: {
    marginRight: 6,
  },
  typeTag: {
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 8,
    marginRight: 8,
  },
  typeText: {
    fontSize: 10,
    color: '#ffffff',
    fontWeight: '500',
  },
  lastMessageTime: {
    fontSize: 12,
    color: '#999',
  },
  messageContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  lastMessage: {
    flex: 1,
    fontSize: 14,
    color: '#666',
    marginRight: 8,
  },
  unreadIndicator: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#FF4444',
  },
  separator: {
    height: 1,
    backgroundColor: '#f0f0f0',
    marginLeft: 76,
  },
});

export default HomeScreen;