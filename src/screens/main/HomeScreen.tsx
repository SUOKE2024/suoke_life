import React, { useState, useEffect, useCallback } from "react";
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  TextInput,
  StatusBar,
  Alert,
  ActivityIndicator
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { useNavigation } from "@react-navigation/native";
import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import Icon from "react-native-vector-icons/MaterialCommunityIcons";
import { useSelector } from 'react-redux';
import { RootState } from '../../store';

// 聊天项类型定义
interface ChatItem {
  id: string;
  name: string;
  avatar: string;
  message: string;
  time: string;
  unread: number;
  type: "agent" | "doctor" | "user";
  isOnline?: boolean;
  tag?: string;
}

type MainTabParamList = {
  Home: undefined;
  Suoke: undefined;
  Explore: undefined;
  Life: undefined;
  Profile: undefined;
  ChatDetail: { chatId: string; chatType: string; chatName: string };
};

type HomeScreenNavigationProp = NativeStackNavigationProp<
  MainTabParamList,
  "Home"
>;

const HomeScreen: React.FC = () => {
  const navigation = useNavigation<HomeScreenNavigationProp>();
  const [searchQuery, setSearchQuery] = useState("");
  const [chatList, setChatList] = useState<ChatItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  // 从Redux获取用户信息
  const authState = useSelector((state: RootState) => state.auth);
  const user = 'user' in authState ? authState.user : null;

  // 工具函数
  const getAgentName = (agentType: string): string => {
    const names: Record<string, string> = { 
      xiaoai: '小艾', 
      xiaoke: '小克', 
      laoke: '老克', 
      soer: '索儿' 
    };
    return names[agentType] || agentType;
  };

  const getAgentAvatar = (agentType: string): string => {
    const avatars: Record<string, string> = { 
      xiaoai: '🤖', 
      xiaoke: '🧘‍♂️', 
      laoke: '👨‍⚕️', 
      soer: '🏃‍♀️' 
    };
    return avatars[agentType] || '🤖';
  };

  const getAgentTag = (agentType: string): string => {
    const tags: Record<string, string> = { 
      xiaoai: '健康助手', 
      xiaoke: '中医辨证', 
      laoke: '健康顾问', 
      soer: '生活教练' 
    };
    return tags[agentType] || '';
  };

  const getAgentGreeting = (agentType: string): string => {
    const greetings: Record<string, string> = {
      xiaoai: '您好！我是小艾，有什么健康问题需要咨询吗？',
      xiaoke: '您好！我是小克，需要什么服务帮助吗？',
      laoke: '您好！我是老克，想学习什么健康知识呢？',
      soer: '您好！我是索儿，今天想了解什么生活建议呢？'
    };
    return greetings[agentType] || '您好！';
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
    
    return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
  };

  // 生成智能体聊天数据
  const generateAgentChats = (): ChatItem[] => {
    return ['xiaoai', 'xiaoke', 'laoke', 'soer'].map(agentType => ({
      id: agentType,
      name: getAgentName(agentType),
      avatar: getAgentAvatar(agentType),
      message: getAgentGreeting(agentType),
      time: '刚刚',
      unread: Math.floor(Math.random() * 3), // 随机未读数
      type: "agent" as const,
      isOnline: Math.random() > 0.3, // 70%概率在线
      tag: getAgentTag(agentType)
    }));
  };

  // 生成医生聊天数据
  const generateDoctorChats = (): ChatItem[] => {
    const doctors = [
      { name: '张医生', specialty: '中医内科', message: '您的检查结果已出，一切正常' },
      { name: '李教授', specialty: '针灸专家', message: '请按照方案坚持服药，下周复诊' },
      { name: '王主任', specialty: '康复科', message: '康复训练进展良好，继续保持' }
    ];

    return doctors.map((doctor, index) => ({
      id: `doctor_${index}`,
      name: doctor.name,
      avatar: index % 2 === 0 ? "👩‍⚕️" : "👨‍⚕️",
      message: doctor.message,
      time: ['周二', '上周', '3天前'][index],
      unread: index === 0 ? 1 : 0,
      type: "doctor" as const,
      tag: doctor.specialty
    }));
  };

  // 生成用户群组数据
  const generateUserChats = (): ChatItem[] => {
    const groups = [
      { name: '健康小组', message: '[王医生]: 分享了一篇养生文章', unread: 3 },
      { name: '家人健康群', message: '[妈妈]: 今天按时吃药了吗？', unread: 0 },
      { name: '运动打卡群', message: '[小明]: 今天跑步5公里完成！', unread: 2 }
    ];

    return groups.map((group, index) => ({
      id: `group_${index}`,
      name: group.name,
      avatar: "👥",
      message: group.message,
      time: ['周三', '3/15', '昨天'][index],
      unread: group.unread,
      type: "user" as const
    }));
  };

  // 加载聊天列表
  const loadChatList = useCallback(async () => {
    try {
      setLoading(true);
      
      // 模拟API延迟
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // 生成聊天数据
      const agentChats = generateAgentChats();
      const doctorChats = generateDoctorChats();
      const userChats = generateUserChats();
      
      const allChats = [...agentChats, ...doctorChats, ...userChats];
      
      // 按优先级排序：智能体 > 有未读消息的 > 其他
      allChats.sort((a, b) => {
        if (a.type === 'agent' && b.type !== 'agent') return -1;
        if (a.type !== 'agent' && b.type === 'agent') return 1;
        if (a.unread > 0 && b.unread === 0) return -1;
        if (a.unread === 0 && b.unread > 0) return 1;
        return 0;
      });
      
      setChatList(allChats);
    } catch (error) {
      console.error('加载聊天列表失败:', error);
      Alert.alert('错误', '加载聊天列表失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  }, []);

  // 初始化加载
  useEffect(() => {
    loadChatList();
  }, [loadChatList]);

  // 下拉刷新
  const handleRefresh = useCallback(async () => {
    setRefreshing(true);
    await loadChatList();
    setRefreshing(false);
  }, [loadChatList]);

  // 过滤聊天列表
  const filteredChatList = chatList.filter(
    (chat) =>
      chat.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      chat.message.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // 处理聊天项点击
  const handleChatItemPress = useCallback(async (chatItem: ChatItem) => {
    try {
      // 标记消息为已读
      if (chatItem.unread > 0) {
        setChatList(prev => prev.map(chat => 
          chat.id === chatItem.id ? { ...chat, unread: 0 } : chat
        ));
      }

      // 导航到聊天详情页面
      navigation.navigate("ChatDetail", { 
        chatId: chatItem.id,
        chatType: chatItem.type,
        chatName: chatItem.name
      });
    } catch (error) {
      console.error('打开聊天失败:', error);
      Alert.alert('错误', '无法打开聊天，请稍后重试');
    }
  }, [navigation]);

  // 处理添加新聊天
  const handleAddChat = useCallback(() => {
    Alert.alert(
      '新建聊天',
      '选择聊天类型',
      [
        { text: '联系医生', onPress: () => navigation.navigate('Life' as never) },
        { text: '加入群组', onPress: () => navigation.navigate('Explore' as never) },
        { text: '取消', style: 'cancel' }
      ]
    );
  }, [navigation]);

  // 渲染聊天项
  const renderChatItem = ({ item }: { item: ChatItem }) => (
    <TouchableOpacity
      style={styles.chatItem}
      onPress={() => handleChatItemPress(item)}
      activeOpacity={0.7}
    >
      {/* 头像 */}
      <View style={styles.avatarContainer}>
        <View style={styles.avatarImageContainer}>
          <Text style={styles.avatarText}>{item.avatar}</Text>
        </View>
        {item.isOnline !== undefined && (
          <View
            style={[
              styles.onlineIndicator,
              { backgroundColor: item.isOnline ? "#4CAF50" : "#9E9E9E" }
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
                {item.unread > 99 ? "99+" : item.unread}
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

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#007AFF" />
          <Text style={styles.loadingText}>加载中...</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#f6f6f6" />

      {/* 头部 */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>索克生活</Text>
        <TouchableOpacity style={styles.addButton} onPress={handleAddChat}>
          <Icon name="plus" size={24} color="#007AFF" />
        </TouchableOpacity>
      </View>

      {/* 搜索框 */}
      <View style={styles.searchContainer}>
        <Icon name="magnify" size={20} color="#999" style={styles.searchIcon} />
        <TextInput
          style={styles.searchInput}
          placeholder="搜索聊天记录"
          value={searchQuery}
          onChangeText={setSearchQuery}
          placeholderTextColor="#999"
        />
      </View>

      {/* 聊天列表 */}
      <FlatList
        data={filteredChatList}
        renderItem={renderChatItem}
        keyExtractor={(item) => item.id}
        style={styles.chatList}
        showsVerticalScrollIndicator={false}
        refreshing={refreshing}
        onRefresh={handleRefresh}
      />
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#f6f6f6"
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center'
  },
  loadingText: {
    fontSize: 16,
    color: '#666',
    marginTop: 10
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: "#fff",
    borderBottomWidth: 1,
    borderBottomColor: "#e0e0e0"
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: "bold",
    color: "#333"
  },
  addButton: {
    padding: 8
  },
  searchContainer: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#fff",
    marginHorizontal: 16,
    marginVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#e0e0e0"
  },
  searchIcon: {
    marginRight: 8
  },
  searchInput: {
    flex: 1,
    height: 40,
    fontSize: 16,
    color: "#333"
  },
  chatList: {
    flex: 1
  },
  chatItem: {
    flexDirection: "row",
    backgroundColor: "#fff",
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: "#f0f0f0"
  },
  avatarContainer: {
    position: "relative",
    marginRight: 12
  },
  avatarImageContainer: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: "#f0f0f0",
    justifyContent: "center",
    alignItems: "center"
  },
  avatarText: {
    fontSize: 24,
    textAlign: "center"
  },
  onlineIndicator: {
    position: "absolute",
    bottom: 2,
    right: 2,
    width: 12,
    height: 12,
    borderRadius: 6,
    borderWidth: 2,
    borderColor: "#fff"
  },
  chatContent: {
    flex: 1,
    justifyContent: "center"
  },
  chatHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 4
  },
  chatName: {
    fontSize: 16,
    fontWeight: "600",
    color: "#333"
  },
  chatTime: {
    fontSize: 12,
    color: "#999"
  },
  messageRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 4
  },
  chatMessage: {
    flex: 1,
    fontSize: 14,
    color: "#666",
    marginRight: 8
  },
  unreadBadge: {
    backgroundColor: "#FF3B30",
    borderRadius: 10,
    minWidth: 20,
    height: 20,
    justifyContent: "center",
    alignItems: "center",
    paddingHorizontal: 6
  },
  unreadText: {
    fontSize: 12,
    color: "#fff",
    fontWeight: "600"
  },
  tagContainer: {
    alignSelf: "flex-start"
  },
  tagText: {
    fontSize: 12,
    color: "#007AFF",
    backgroundColor: "#E3F2FD",
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 4
  }
});

export default HomeScreen;
