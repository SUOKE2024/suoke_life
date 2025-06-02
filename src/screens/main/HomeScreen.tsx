import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  Image,
  TextInput,
  Platform,
  StatusBar,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

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
}

type MainTabParamList = {
  Home: undefined;
  Suoke: undefined;
  Explore: undefined;
  Life: undefined;
  Profile: undefined;
};

type HomeScreenNavigationProp = NativeStackNavigationProp<MainTabParamList, 'Home'>;

const HomeScreen: React.FC = () => {
  const navigation = useNavigation<HomeScreenNavigationProp>();
  const [searchQuery, setSearchQuery] = useState('');
  const [chatList, setChatList] = useState<ChatItem[]>([]);

  // 加载聊天列表
  useEffect(() => {
    // 模拟从API获取数据
    const mockChatList: ChatItem[] = [
      // 智能体
      {
        id: 'xiaoai',
        name: '小艾',
        avatar: '🤖',
        message: '您的健康报告已生成，点击查看详情',
        time: '09:30',
        unread: 1,
        type: 'agent',
        isOnline: true,
        tag: '健康助手'
      },
      {
        id: 'xiaoke',
        name: '小克',
        avatar: '🧘‍♂️',
        message: '根据您的脉象，建议多注意休息',
        time: '昨天',
        unread: 0,
        type: 'agent',
        isOnline: true,
        tag: '中医辨证'
      },
      {
        id: 'laoke',
        name: '老克',
        avatar: '👨‍⚕️',
        message: '已为您制定新的康复计划，请查收',
        time: '昨天',
        unread: 2,
        type: 'agent',
        isOnline: false,
        tag: '健康顾问'
      },
      {
        id: 'soer',
        name: '索儿',
        avatar: '🏃‍♀️',
        message: '今天的运动目标已完成80%，继续加油！',
        time: '周一',
        unread: 0,
        type: 'agent',
        isOnline: true,
        tag: '生活教练'
      },
      // 名医
      {
        id: 'doctor1',
        name: '张医生',
        avatar: '👩‍⚕️',
        message: '您的检查结果已出，一切正常',
        time: '周二',
        unread: 0,
        type: 'doctor',
        tag: '中医内科'
      },
      {
        id: 'doctor2',
        name: '李教授',
        avatar: '👨‍⚕️',
        message: '请按照方案坚持服药，下周复诊',
        time: '上周',
        unread: 0,
        type: 'doctor',
        tag: '针灸专家'
      },
      // 用户
      {
        id: 'user1',
        name: '健康小组',
        avatar: '👥',
        message: '[王医生]: 分享了一篇养生文章',
        time: '周三',
        unread: 3,
        type: 'user'
      },
      {
        id: 'user2',
        name: '家人健康群',
        avatar: '👪',
        message: '[妈妈]: 今天按时吃药了吗？',
        time: '3/15',
        unread: 0,
        type: 'user'
      },
    ];

    setChatList(mockChatList);
  }, []);

  // 过滤聊天列表
  const filteredChatList = chatList.filter(chat => 
    chat.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    chat.message.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // 处理聊天项点击
  const handleChatItemPress = (chatItem: ChatItem) => {
    console.log(`打开与${chatItem.name}的聊天`);
    // TODO: 导航到聊天页面
    // navigation.navigate('ChatDetail', { chatId: chatItem.id });
  };

  // 渲染聊天项
  const renderChatItem = ({ item }: { item: ChatItem }) => (
    <TouchableOpacity 
      style={styles.chatItem}
      onPress={() => handleChatItemPress(item)}
      activeOpacity={0.7}
    >
      {/* 头像 */}
      <View style={styles.avatarContainer}>
        {item.type === 'agent' ? (
          <Text style={styles.avatarText}>{item.avatar}</Text>
        ) : (
          <View style={styles.avatarImageContainer}>
            <Text style={styles.avatarText}>{item.avatar}</Text>
          </View>
        )}
        {item.isOnline !== undefined && (
          <View 
            style={[
              styles.onlineIndicator, 
              { backgroundColor: item.isOnline ? '#4CAF50' : '#9E9E9E' }
            ]} 
          />
        )}
      </View>

      {/* 聊天内容 */}
      <View style={styles.chatContent}>
        <View style={styles.chatHeader}>
          <Text style={styles.chatName}>{item.name}</Text>
          <Text style={styles.chatTime}>{item.time}</Text>
        </View>
        
        <View style={styles.messageRow}>
          <Text 
            style={styles.chatMessage}
            numberOfLines={1}
            ellipsizeMode="tail"
          >
            {item.message}
          </Text>
          
          {item.unread > 0 && (
            <View style={styles.unreadBadge}>
              <Text style={styles.unreadText}>
                {item.unread > 99 ? '99+' : item.unread}
              </Text>
            </View>
          )}
        </View>
        
        {item.tag && (
          <View style={styles.tagContainer}>
            <Text style={styles.tagText}>{item.tag}</Text>
          </View>
        )}
      </View>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#f6f6f6" />
      
      {/* 头部 */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>聊天</Text>
        <TouchableOpacity style={styles.headerButton}>
          <Icon name="plus" size={24} color="#2E7D32" />
        </TouchableOpacity>
      </View>
      
      {/* 搜索栏 */}
      <View style={styles.searchContainer}>
        <Icon name="magnify" size={20} color="#999999" style={styles.searchIcon} />
        <TextInput
          style={styles.searchInput}
          placeholder="搜索"
          placeholderTextColor="#999999"
          value={searchQuery}
          onChangeText={setSearchQuery}
        />
        {searchQuery !== '' && (
          <TouchableOpacity onPress={() => setSearchQuery('')}>
            <Icon name="close-circle" size={16} color="#CCCCCC" />
          </TouchableOpacity>
        )}
      </View>
      
      {/* 聊天列表 */}
      <FlatList
        data={filteredChatList}
        renderItem={renderChatItem}
        keyExtractor={item => item.id}
        style={styles.chatList}
        showsVerticalScrollIndicator={false}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>暂无聊天记录</Text>
          </View>
        }
      />
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f6f6f6',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 10,
    backgroundColor: '#f6f6f6',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333333',
  },
  headerButton: {
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#EBEBEB',
    borderRadius: 8,
    marginHorizontal: 16,
    marginVertical: 8,
    paddingHorizontal: 12,
    height: 36,
  },
  searchIcon: {
    marginRight: 6,
  },
  searchInput: {
    flex: 1,
    height: 36,
    fontSize: 14,
    color: '#333333',
    padding: 0,
  },
  chatList: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  chatItem: {
    flexDirection: 'row',
    padding: 12,
    borderBottomWidth: 0.5,
    borderBottomColor: '#EEEEEE',
  },
  avatarContainer: {
    position: 'relative',
    marginRight: 12,
  },
  avatarImageContainer: {
    width: 48,
    height: 48,
    borderRadius: 4,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f0f0f0',
    overflow: 'hidden',
  },
  avatarImage: {
    width: 48,
    height: 48,
    borderRadius: 4,
  },
  avatarText: {
    fontSize: 32,
  },
  onlineIndicator: {
    position: 'absolute',
    bottom: 0,
    right: 0,
    width: 10,
    height: 10,
    borderRadius: 5,
    borderWidth: 1,
    borderColor: '#FFFFFF',
  },
  chatContent: {
    flex: 1,
    justifyContent: 'center',
  },
  chatHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 6,
  },
  chatName: {
    fontSize: 16,
    fontWeight: '500',
    color: '#333333',
  },
  chatTime: {
    fontSize: 12,
    color: '#999999',
  },
  messageRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  chatMessage: {
    flex: 1,
    fontSize: 14,
    color: '#666666',
    marginRight: 8,
  },
  unreadBadge: {
    minWidth: 18,
    height: 18,
    borderRadius: 9,
    backgroundColor: '#FF3B30',
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 5,
  },
  unreadText: {
    fontSize: 11,
    color: '#FFFFFF',
    fontWeight: '500',
  },
  tagContainer: {
    backgroundColor: '#F0F0F0',
    borderRadius: 4,
    paddingHorizontal: 6,
    paddingVertical: 2,
    marginTop: 4,
    alignSelf: 'flex-start',
  },
  tagText: {
    fontSize: 10,
    color: '#666666',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 50,
  },
  emptyText: {
    fontSize: 14,
    color: '#999999',
    textAlign: 'center',
  },
});

export default HomeScreen; 