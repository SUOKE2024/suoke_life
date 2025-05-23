import React, { useState, useRef, useEffect } from 'react';
import { View, StyleSheet, ScrollView, KeyboardAvoidingView, Platform, Alert } from 'react-native';
import { Text, TextInput, Button, Card, Avatar, Chip, useTheme, IconButton, Surface } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRoute, useNavigation } from '@react-navigation/native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { useTranslation } from 'react-i18next';
import { AgentType, agentInfo } from '../../api/agents';

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
  type?: 'text' | 'image' | 'audio' | 'suggestion';
  suggestions?: string[];
}

interface RouteParams {
  agentType: AgentType;
}

const AgentChat = () => {
  const theme = useTheme();
  const navigation = useNavigation();
  const route = useRoute();
  const { t } = useTranslation();
  const scrollViewRef = useRef<ScrollView>(null);
  
  const { agentType } = route.params as RouteParams;
  const agent = agentInfo[agentType];
  
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: agent.greeting,
      isUser: false,
      timestamp: new Date(),
      type: 'text',
      suggestions: ['开始健康评估', '查看我的体质', '了解养生建议', '预约服务']
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  // 模拟智能体回复
  const simulateAgentReply = (userMessage: string) => {
    setIsTyping(true);
    
    setTimeout(() => {
      let replyText = '';
      let suggestions: string[] = [];
      
      // 根据不同智能体和用户输入生成不同回复
      switch (agentType) {
        case AgentType.XIAOAI:
          if (userMessage.includes('体质') || userMessage.includes('辨证')) {
            replyText = '根据中医理论，体质分为九种基本类型。我可以通过四诊合参的方式为您进行体质辨识。您目前有什么身体不适或想了解的症状吗？';
            suggestions = ['开始望诊', '开始问诊', '查看体质报告', '了解调理方案'];
          } else if (userMessage.includes('健康评估')) {
            replyText = '我将通过望、闻、问、切四诊结合的方式为您进行全面的健康评估。建议您在光线充足、安静的环境中进行，这样能获得更准确的结果。';
            suggestions = ['开始四诊评估', '上传舌象照片', '描述症状', '查看历史记录'];
          } else {
            replyText = '我是小艾，专注于中医辨证分析。我可以帮您进行体质辨识、症状分析，并提供个性化的调理建议。您想了解什么呢？';
            suggestions = ['体质辨识', '症状分析', '健康建议', '四诊介绍'];
          }
          break;
          
        case AgentType.XIAOKE:
          if (userMessage.includes('预约') || userMessage.includes('服务')) {
            replyText = '我可以为您提供医疗预约、健康产品推荐和农产品定制服务。请告诉我您需要什么类型的服务？';
            suggestions = ['预约医生', '健康产品', '有机农产品', '体检套餐'];
          } else {
            replyText = '我是小克，您的健康服务管家。我可以帮您预约医疗服务、推荐健康产品，还能为您定制有机农产品。有什么可以为您服务的吗？';
            suggestions = ['医疗预约', '产品推荐', '农产品定制', '服务咨询'];
          }
          break;
          
        case AgentType.LAOKE:
          if (userMessage.includes('学习') || userMessage.includes('知识')) {
            replyText = '中医养生知识博大精深，我可以为您制定个性化的学习路径。您想从哪个方面开始学习呢？';
            suggestions = ['基础理论', '穴位按摩', '食疗养生', '四季养生'];
          } else {
            replyText = '我是老克，中医养生知识的传播者。我可以为您提供系统的中医学习课程，还有趣味互动和社区交流。让我们一起探索中医的奥秘吧！';
            suggestions = ['开始学习', '知识问答', '社区交流', '学习进度'];
          }
          break;
          
        case AgentType.SOER:
          if (userMessage.includes('计划') || userMessage.includes('养生')) {
            replyText = '我会根据您的体质、生活环境和个人习惯，为您制定专属的健康养生计划。让我先了解一下您的基本情况吧。';
            suggestions = ['制定计划', '生活习惯', '环境分析', '健康目标'];
          } else {
            replyText = '我是索儿，您的个人健康管家。我可以为您制定个性化的健康计划，分析生活数据，预测健康趋势。让我们开始您的健康管理之旅吧！';
            suggestions = ['健康计划', '数据分析', '生活建议', '趋势预测'];
          }
          break;
      }
      
      const newMessage: Message = {
        id: Date.now().toString(),
        text: replyText,
        isUser: false,
        timestamp: new Date(),
        type: 'text',
        suggestions
      };
      
      setMessages(prev => [...prev, newMessage]);
      setIsTyping(false);
    }, 1000 + Math.random() * 2000); // 1-3秒随机延迟
  };

  const sendMessage = () => {
    if (!inputText.trim()) return;
    
    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputText,
      isUser: true,
      timestamp: new Date(),
      type: 'text'
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    
    // 模拟智能体回复
    simulateAgentReply(inputText);
  };

  const handleSuggestionPress = (suggestion: string) => {
    setInputText(suggestion);
    setTimeout(() => sendMessage(), 100);
  };

  const handleVoiceInput = () => {
    Alert.alert('语音输入', '语音输入功能开发中...', [{ text: '确定' }]);
  };

  const handleImageInput = () => {
    Alert.alert('图片输入', '图片输入功能开发中...', [{ text: '确定' }]);
  };

  useEffect(() => {
    scrollViewRef.current?.scrollToEnd({ animated: true });
  }, [messages]);

  const renderMessage = (message: Message) => (
    <View key={message.id} style={[
      styles.messageContainer,
      message.isUser ? styles.userMessageContainer : styles.agentMessageContainer
    ]}>
      {!message.isUser && (
        <View style={[styles.agentAvatar, { backgroundColor: agent.color + '20', borderRadius: 16, justifyContent: 'center', alignItems: 'center' }]}>
          <Icon name={agent.avatar} size={20} color={agent.color} />
        </View>
      )}
      
      <Surface style={[
        styles.messageBubble,
        message.isUser ? styles.userMessageBubble : styles.agentMessageBubble,
        { backgroundColor: message.isUser ? theme.colors.primary : theme.colors.surface }
      ]}>
        <Text style={[
          styles.messageText,
          { color: message.isUser ? '#FFFFFF' : theme.colors.onSurface }
        ]}>
          {message.text}
        </Text>
        
        {message.suggestions && (
          <View style={styles.suggestionsContainer}>
            {message.suggestions.map((suggestion, index) => (
              <Chip
                key={index}
                mode="outlined"
                onPress={() => handleSuggestionPress(suggestion)}
                style={styles.suggestionChip}
                textStyle={styles.suggestionText}
              >
                {suggestion}
              </Chip>
            ))}
          </View>
        )}
      </Surface>
      
      {message.isUser && (
        <Avatar.Text
          size={32}
          label="我"
          style={[styles.userAvatar, { backgroundColor: theme.colors.primary }]}
        />
      )}
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      {/* 头部 */}
      <Surface style={styles.header}>
        <IconButton
          icon="arrow-left"
          size={24}
          onPress={() => navigation.goBack()}
        />
        <View style={styles.headerInfo}>
          <View style={{ backgroundColor: agent.color + '20', borderRadius: 20, width: 40, height: 40, justifyContent: 'center', alignItems: 'center' }}>
            <Icon name={agent.avatar} size={24} color={agent.color} />
          </View>
          <View style={styles.headerText}>
            <Text style={styles.agentName}>{agent.name}</Text>
            <Text style={styles.agentStatus}>在线</Text>
          </View>
        </View>
        <IconButton
          icon="dots-vertical"
          size={24}
          onPress={() => Alert.alert('更多选项', '功能开发中...', [{ text: '确定' }])}
        />
      </Surface>

      {/* 消息列表 */}
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.chatContainer}
      >
        <ScrollView
          ref={scrollViewRef}
          style={styles.messagesContainer}
          contentContainerStyle={styles.messagesContent}
        >
          {messages.map(renderMessage)}
          
          {isTyping && (
            <View style={styles.typingContainer}>
              <View style={[styles.agentAvatar, { backgroundColor: agent.color + '20', borderRadius: 16, justifyContent: 'center', alignItems: 'center' }]}>
                <Icon name={agent.avatar} size={20} color={agent.color} />
              </View>
              <Surface style={styles.typingBubble}>
                <Text style={styles.typingText}>正在输入...</Text>
              </Surface>
            </View>
          )}
        </ScrollView>

        {/* 输入区域 */}
        <Surface style={styles.inputContainer}>
          <IconButton
            icon="image"
            size={24}
            onPress={handleImageInput}
          />
          <TextInput
            style={styles.textInput}
            value={inputText}
            onChangeText={setInputText}
            placeholder="输入消息..."
            multiline
            maxLength={500}
            onSubmitEditing={sendMessage}
          />
          <IconButton
            icon="microphone"
            size={24}
            onPress={handleVoiceInput}
          />
          <IconButton
            icon="send"
            size={24}
            onPress={sendMessage}
            disabled={!inputText.trim()}
          />
        </Surface>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 8,
    paddingVertical: 8,
    elevation: 2,
  },
  headerInfo: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    marginLeft: 8,
  },
  headerText: {
    marginLeft: 12,
  },
  agentName: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  agentStatus: {
    fontSize: 12,
    opacity: 0.7,
    color: '#4CAF50',
  },
  chatContainer: {
    flex: 1,
  },
  messagesContainer: {
    flex: 1,
  },
  messagesContent: {
    padding: 16,
  },
  messageContainer: {
    flexDirection: 'row',
    marginBottom: 16,
    alignItems: 'flex-end',
  },
  userMessageContainer: {
    justifyContent: 'flex-end',
  },
  agentMessageContainer: {
    justifyContent: 'flex-start',
  },
  agentAvatar: {
    marginRight: 8,
    width: 32,
    height: 32,
  },
  userAvatar: {
    marginLeft: 8,
  },
  messageBubble: {
    maxWidth: '75%',
    padding: 12,
    borderRadius: 16,
    elevation: 1,
  },
  userMessageBubble: {
    borderBottomRightRadius: 4,
  },
  agentMessageBubble: {
    borderBottomLeftRadius: 4,
  },
  messageText: {
    fontSize: 16,
    lineHeight: 22,
  },
  suggestionsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginTop: 8,
  },
  suggestionChip: {
    margin: 2,
  },
  suggestionText: {
    fontSize: 12,
  },
  typingContainer: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    marginBottom: 16,
  },
  typingBubble: {
    padding: 12,
    borderRadius: 16,
    borderBottomLeftRadius: 4,
    marginLeft: 8,
  },
  typingText: {
    fontSize: 14,
    fontStyle: 'italic',
    opacity: 0.7,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    paddingHorizontal: 8,
    paddingVertical: 8,
    elevation: 4,
  },
  textInput: {
    flex: 1,
    maxHeight: 100,
    marginHorizontal: 8,
    backgroundColor: 'transparent',
  },
});

export default AgentChat;