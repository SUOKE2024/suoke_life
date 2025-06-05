import React, { useState, useEffect, useCallback } from "react";
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
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { useNavigation } from "@react-navigation/native";
import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import Icon from "react-native-vector-icons/MaterialCommunityIcons";

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
};

type HomeScreenNavigationProp = NativeStackNavigationProp<
  MainTabParamList,
  "Home"
>;

const HomeScreen: React.FC = () => {
  const navigation = useNavigation<HomeScreenNavigationProp>();
  const [searchQuery, setSearchQuery] = useState("");
  const [chatList, setChatList] = useState<ChatItem[]>([]);

  // 加载聊天列表
  useEffect(() => {
    // 模拟从API获取数据
    const mockChatList: ChatItem[] = [
      // 智能体
      {
        id: "xiaoai",
        name: "小艾",
        avatar: "🤖",
        message: "您的健康报告已生成，点击查看详情",
        time: "09:30",
        unread: 1,
        type: "agent",
        isOnline: true,
        tag: "健康助手",
      },
      {
        id: "xiaoke",
        name: "小克",
        avatar: "🧘‍♂️",
        message: "根据您的脉象，建议多注意休息",
        time: "昨天",
        unread: 0,
        type: "agent",
        isOnline: true,
        tag: "中医辨证",
      },
      {
        id: "laoke",
        name: "老克",
        avatar: "👨‍⚕️",
        message: "已为您制定新的康复计划，请查收",
        time: "昨天",
        unread: 2,
        type: "agent",
        isOnline: false,
        tag: "健康顾问",
      },
      {
        id: "soer",
        name: "索儿",
        avatar: "🏃‍♀️",
        message: "今天的运动目标已完成80%，继续加油！",
        time: "周一",
        unread: 0,
        type: "agent",
        isOnline: true,
        tag: "生活教练",
      },
      // 名医
      {
        id: "doctor1",
        name: "张医生",
        avatar: "👩‍⚕️",
        message: "您的检查结果已出，一切正常",
        time: "周二",
        unread: 0,
        type: "doctor",
        tag: "中医内科",
      },
      {
        id: "doctor2",
        name: "李教授",
        avatar: "👨‍⚕️",
        message: "请按照方案坚持服药，下周复诊",
        time: "上周",
        unread: 0,
        type: "doctor",
        tag: "针灸专家",
      },
      // 用户
      {
        id: "user1",
        name: "健康小组",
        avatar: "👥",
        message: "[王医生]: 分享了一篇养生文章",
        time: "周三",
        unread: 3,
        type: "user",
      },
      {
        id: "user2",
        name: "家人健康群",
        avatar: "👪",
        message: "[妈妈]: 今天按时吃药了吗？",
        time: "3/15",
        unread: 0,
        type: "user",
      },
    ];
    setChatList(mockChatList);
  }, []);

  // 过滤聊天列表
  const filteredChatList = chatList.filter(
    (chat) =>
      chat.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      chat.message.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // 处理聊天项点击
  const handleChatItemPress = (chatItem: ChatItem) => {
    // TODO: 导航到聊天页面
    // navigation.navigate("ChatDetail", { chatId: chatItem.id });
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
        {item.type === "agent" ? (
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
              { backgroundColor: item.isOnline ? "#4CAF50" : "#9E9E9E" },
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

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#f6f6f6" />

      {/* 头部 */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>索克生活</Text>
        <TouchableOpacity style={styles.addButton}>
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
      />
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#f6f6f6",
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: "#fff",
    borderBottomWidth: 1,
    borderBottomColor: "#e0e0e0",
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: "bold",
    color: "#333",
  },
  addButton: {
    padding: 8,
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
    borderColor: "#e0e0e0",
  },
  searchIcon: {
    marginRight: 8,
  },
  searchInput: {
    flex: 1,
    height: 40,
    fontSize: 16,
    color: "#333",
  },
  chatList: {
    flex: 1,
  },
  chatItem: {
    flexDirection: "row",
    backgroundColor: "#fff",
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: "#f0f0f0",
  },
  avatarContainer: {
    position: "relative",
    marginRight: 12,
  },
  avatarText: {
    fontSize: 24,
    width: 48,
    height: 48,
    textAlign: "center",
    lineHeight: 48,
  },
  avatarImageContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: "#f0f0f0",
    justifyContent: "center",
    alignItems: "center",
  },
  onlineIndicator: {
    position: "absolute",
    bottom: 2,
    right: 2,
    width: 12,
    height: 12,
    borderRadius: 6,
    borderWidth: 2,
    borderColor: "#fff",
  },
  chatContent: {
    flex: 1,
  },
  chatHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 4,
  },
  chatName: {
    fontSize: 16,
    fontWeight: "600",
    color: "#333",
  },
  chatTime: {
    fontSize: 12,
    color: "#999",
  },
  messageRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 4,
  },
  chatMessage: {
    flex: 1,
    fontSize: 14,
    color: "#666",
    marginRight: 8,
  },
  unreadBadge: {
    backgroundColor: "#FF3B30",
    borderRadius: 10,
    minWidth: 20,
    height: 20,
    justifyContent: "center",
    alignItems: "center",
    paddingHorizontal: 6,
  },
  unreadText: {
    color: "#fff",
    fontSize: 12,
    fontWeight: "600",
  },
  tagContainer: {
    alignSelf: "flex-start",
  },
  tagText: {
    fontSize: 12,
    color: "#007AFF",
    backgroundColor: "#E3F2FD",
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 4,
  },
});

export default HomeScreen;
