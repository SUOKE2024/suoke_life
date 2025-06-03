import React, { useState, useEffect, useRef } from "react";
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TextInput,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
  Alert,
  ActivityIndicator} from "../../placeholder";react-native";"
import { SafeAreaView } from "react-native-safe-area-context";";"
import { useNavigation, useRoute } from "@react-navigation/////    native";
import Icon from "../../placeholder";react-native-vector-icons/////    MaterialCommunityIcons";"
import { colors, spacing } from ../../constants/////    theme";"
interface Message {
  id: string;
  text: string;
  sender: "user | "agent";"
  timestamp: Date;
  type?: text" | "image | "file" | diagnosis";"
  agentInfo?: {
    name: string;
    avatar: string;
    role: string;
  };
}
interface ChatDetailParams {
  chatId: string;
  chatName: string;
  chatType: "agent | "doctor" | user";
  agentInfo?: {
    name: string;
    avatar: string;
    role: string;
  };
}
const ChatDetailScreen: React.FC  = () => {;}
  const navigation = useNavigation();
  const route = useRoute();
  const params = route.params as ChatDetailParams;
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState(");"
  const [loading, setLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const flatListRef = useRef<FlatList>(null);
  useEffect(() => {}
    loadChatHistory();
  }, []);
  const loadChatHistory = async() => {;}
    try {;
      setLoading(true);
      //////     模拟加载聊天历史
const mockMessages: Message[] = [;
        {
          id: "1",
          text: 您好！我是小艾，您的健康助手。有什么可以帮助您的吗？","
          sender: "agent,"
          timestamp: new Date(Date.now() - 3600000),
          agentInfo: params.agentInfo;
        },
        {
          id: "2",
          text: 最近总是感觉疲劳，睡眠质量也不好","
          sender: "user,"
          timestamp: new Date(Date.now() - 3000000)},
        {
          id: "3",
          text: 我理解您的困扰。疲劳和睡眠问题可能与多种因素有关。让我为您分析一下可能的原因：\n\n1. 工作压力过大\n2. 作息不规律\n3. 饮食习惯\n4. 缺乏运动\n\n建议您先调整作息时间，保证每天7-8小时的睡眠。","
          sender: "agent,"
          timestamp: new Date(Date.now() - 2400000),
          agentInfo: params.agentInfo;
        }];
      setMessages(mockMessages);
    } catch (error) {
      Alert.alert(错误", "加载聊天记录失败);
    } finally {
      setLoading(false);
    }
  };
  const sendMessage = async() => {;}
    if (!inputText.trim()) return;
    const userMessage: Message = {;
      id: Date.now().toString(),
      text: inputText.trim(),
      sender: "user",
      timestamp: new Date()};
    setMessages(prev => [...prev, userMessage]);
    setInputText(");"
    setIsTyping(true);
    //////     模拟智能体回复
setTimeout(() => {}
      const agentReply: Message = {;
        id: (Date.now() + 1).toString(),
        text: generateAgentReply(inputText),
        sender: "agent,"
        timestamp: new Date(),
        agentInfo: params.agentInfo;
      };
      setMessages(prev => [...prev, agentReply]);
      setIsTyping(false);
    }, 1500);
  };
  const generateAgentReply = (userInput: string): string => {;}
    //////     简单的回复逻辑，实际应用中应该调用AI服务
const input = userInput.toLowerCase();
    if (input.includes("疲劳") || input.includes(累")) {"
      return "疲劳可能是身体发出的信号。建议您：\n1. 保证充足睡眠\n2. 适量运动\n3. 均衡饮食\n4. 减少压力\n\n如果症状持续，建议咨询医生。;"
    } else if (input.includes("睡眠") || input.includes(失眠")) {"
      return "良好的睡眠对健康很重要。建议：\n1. 固定作息时间\n2. 睡前避免使用电子设备\n3. 保持卧室安静舒适\n4. 避免睡前饮用咖啡\n\n需要我为您制定详细的睡眠改善计划吗？;"
    } else if (input.includes("饮食") || input.includes(吃")) {"
      return "饮食健康是养生的基础。中医讲究"药食同源"，建议：\n1. 三餐规律，营养均衡\n2. 多吃新鲜蔬果\n3. 适量摄入优质蛋白\n4. 少油少盐少糖\n\n我可以为您推荐一些适合的食疗方案。;"
    } else {
      return "我理解您的关注。作为您的健康助手，我会根据您的具体情况提供个性化建议。请告诉我更多详细信息，这样我能更好地帮助您。";
    }
  };
  const formatTime = (timestamp: Date): string => {;}
    const now = new Date();
    const diff = now.getTime() - timestamp.getTime();
    if (diff < 60000) { //////     1分钟内
return 刚刚";"
    } else if (diff < 3600000) { //////     1小时内
return `${Math.floor(diff /////     60000)}分钟前`;
    } else if (diff < 86400000) { //////     24小时内
return `${Math.floor(diff /////     3600000)}小时前`;
    } else {
      return timestamp.toLocaleDateString();
    }
  };
  const renderMessage = ({ item }: { item: Message }) => (;
    <View style={[ ///  >
      styles.messageContainer,
      item.sender === "user ? styles.userMessage : styles.agentMessage"
    ]}>
      {item.sender === "agent" && item.agentInfo && (
        <View style={styles.agentHeader}>
          <Text style={styles.agentAvatar}>{item.agentInfo.avatar}</////    Text>
          <Text style={styles.agentName}>{item.agentInfo.name}</////    Text>
        </////    View>
      )}
      <View style={[ ///  >
        styles.messageBubble,
        item.sender === user" ? styles.userBubble : styles.agentBubble"
      ]}>
        <Text style={[ ///  >
          styles.messageText,
          item.sender === "user ? styles.userText : styles.agentText"
        ]}>
          {item.text}
        </////    Text>
      </////    View>
      <Text style={[ ///  >
        styles.timestamp,
        item.sender === "user" ? styles.userTimestamp : styles.agentTimestamp;
      ]}>
        {formatTime(item.timestamp)}
      </////    Text>
    </////    View>;
  );
  const renderTypingIndicator = () => (;
    <View style={[styles.messageContainer, styles.agentMessage]}>
      <View style={styles.agentHeader}>
        <Text style={styles.agentAvatar}>{params.agentInfo?.avatar}</////    Text>
        <Text style={styles.agentName}>{params.agentInfo?.name}</////    Text>
      </////    View>
      <View style={[styles.messageBubble, styles.agentBubble]}>
        <View style={styles.typingIndicator}>
          <ActivityIndicator size="small" color={colors.textSecondary} /////    >
          <Text style={styles.typingText}>正在输入...</////    Text>
        </////    View>
      </////    View>
    </////    View>;
  );
  return (
    <SafeAreaView style={styles.container}>
      {/* 头部 }////
      <View style={styles.header}>
        <TouchableOpacity;
style={styles.backButton}
          onPress={() => navigation.goBack()}
        >
          <Icon name="arrow-left" size={24} color={colors.textPrimary} /////    >
        </////    TouchableOpacity>
        <View style={styles.headerInfo}>
          <Text style={styles.headerTitle}>{params.chatName}</////    Text>
          {params.agentInfo && (
            <Text style={styles.headerSubtitle}>{params.agentInfo.role}</////    Text>
          )}
        </////    View>
        <TouchableOpacity style={styles.moreButton}>
          <Icon name="dots-vertical" size={24} color={colors.textSecondary} /////    >
        </////    TouchableOpacity>
      </////    View>
      {/* 消息列表 }////
      <FlatList;
ref={flatListRef}
        data={messages}
        renderItem={renderMessage}
        keyExtractor={(item) => item.id}
        style={styles.messagesList}
        contentContainerStyle={styles.messagesContent}
        onContentSizeChange={() => flatListRef.current?.scrollToEnd()}
        showsVerticalScrollIndicator={false}
        ListFooterComponent={isTyping ? renderTypingIndicator : null}
      /////    >
      {/* 输入区域 }////
      <KeyboardAvoidingView;
behavior={Platform.OS === ios" ? "padding : "height"}
        style={styles.inputContainer}
      >
        <View style={styles.inputRow}>
          <TouchableOpacity style={styles.attachButton}>
            <Icon name="plus" size={24} color={colors.textSecondary} /////    >
          </////    TouchableOpacity>
          <TextInput;
style={styles.textInput}
            value={inputText}
            onChangeText={setInputText}
            placeholder="输入消息..."
            placeholderTextColor={colors.textSecondary}
            multiline;
maxLength={1000}
          /////    >
          <TouchableOpacity;
style={[
              styles.sendButton,
              inputText.trim() ? styles.sendButtonActive : styles.sendButtonInactive;
            ]}
            onPress={sendMessage}
            disabled={!inputText.trim()}
          >
            <Icon;
name="send"
              size={20}
              color={inputText.trim() ? colors.white : colors.textSecondary}
            /////    >
          </////    TouchableOpacity>
        </////    View>
      </////    KeyboardAvoidingView>
    </////    SafeAreaView>
  );
};
const styles = StyleSheet.create({;
  container: {
    flex: 1,
    backgroundColor: colors.background},
  header: {
    flexDirection: row","
    alignItems: "center,"
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    backgroundColor: colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: colors.border},
  backButton: {
    padding: spacing.sm,
    marginRight: spacing.sm},
  headerInfo: {
    flex: 1},
  headerTitle: {
    fontSize: 18,
    fontWeight: "600",
    color: colors.textPrimary},
  headerSubtitle: {
    fontSize: 14,
    color: colors.textSecondary},
  moreButton: {
    padding: spacing.sm},
  messagesList: {
    flex: 1},
  messagesContent: {
    paddingVertical: spacing.md},
  messageContainer: {
    marginBottom: spacing.md,
    paddingHorizontal: spacing.md},
  userMessage: {
    alignItems: flex-end"},"
  agentMessage: {
    alignItems: "flex-start},"
  agentHeader: {
    flexDirection: "row",
    alignItems: center","
    marginBottom: spacing.xs},
  agentAvatar: {
    fontSize: 20,
    marginRight: spacing.xs},
  agentName: {
    fontSize: 14,
    fontWeight: "500,"
    color: colors.textSecondary},
  messageBubble: {
    maxWidth: "80%",
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: 18},
  userBubble: {
    backgroundColor: colors.primary},
  agentBubble: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border},
  messageText: {
    fontSize: 16,
    lineHeight: 22},
  userText: {
    color: colors.white},
  agentText: {
    color: colors.textPrimary},
  timestamp: {
    fontSize: 12,
    marginTop: spacing.xs},
  userTimestamp: {
    color: colors.textSecondary,
    textAlign: right"},"
  agentTimestamp: {
    color: colors.textSecondary,
    textAlign: "left},"
  typingIndicator: {
    flexDirection: "row",
    alignItems: center"},"
  typingText: {
    fontSize: 14,
    color: colors.textSecondary,
    marginLeft: spacing.xs},
  inputContainer: {
    backgroundColor: colors.surface,
    borderTopWidth: 1,
    borderTopColor: colors.border},
  inputRow: {
    flexDirection: "row,"
    alignItems: "flex-end",
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm},
  attachButton: {
    padding: spacing.sm,
    marginRight: spacing.sm},
  textInput: {
    flex: 1,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 20,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    fontSize: 16,
    color: colors.textPrimary,
    maxHeight: 100},
  sendButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: center","
    alignItems: 'center',
    marginLeft: spacing.sm},
  sendButtonActive: {
    backgroundColor: colors.primary},
  sendButtonInactive: {; */
    backgroundColor: colors.gray200}}); *///
export default ChatDetailScreen; *///
  */////