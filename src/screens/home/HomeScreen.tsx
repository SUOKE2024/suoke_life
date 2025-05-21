import React, { useState, useEffect, useRef } from 'react';
import { 
  View, 
  FlatList, 
  TextInput, 
  TouchableOpacity, 
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator
} from 'react-native';
import { 
  Text, 
  Card, 
  Avatar, 
  Button, 
  IconButton, 
  useTheme,
  Divider
} from 'react-native-paper';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

import { RootStackParamList } from '../../navigation/AppNavigator';

// 临时模拟数据
const MOCK_MESSAGES = [
  {
    id: '1',
    content: '您好，我是您的健康助手小艾。请问今天有什么可以帮助您的吗？',
    sender: 'agent',
    contentType: 'text',
    timestamp: new Date().getTime() - 3600000
  },
  {
    id: '2',
    content: '我最近感觉容易疲劳，有什么建议吗？',
    sender: 'user',
    contentType: 'text',
    timestamp: new Date().getTime() - 3500000
  },
  {
    id: '3',
    content: '容易疲劳可能与多种因素有关，如睡眠质量、饮食习惯、运动状况或压力等。您的睡眠情况如何？每晚能睡够7-8小时吗？',
    sender: 'agent',
    contentType: 'text',
    timestamp: new Date().getTime() - 3400000
  }
];

// 消息类型定义
type Message = {
  id: string;
  content: string;
  sender: 'user' | 'agent';
  contentType: 'text' | 'image' | 'voice';
  fileUrl?: string;
  timestamp: number;
};

// 消息气泡组件
const MessageBubble: React.FC<{ message: Message }> = ({ message }) => {
  const theme = useTheme();
  const isUser = message.sender === 'user';
  
  return (
    <View style={[
      styles.messageBubble,
      isUser ? styles.userBubble : styles.agentBubble,
      { 
        backgroundColor: isUser 
          ? theme.colors.primaryContainer
          : theme.colors.surface
      }
    ]}>
      {!isUser && (
        <Avatar.Image 
          size={36} 
          source={require('../../assets/images/xiaoai_avatar.png')} 
          style={styles.avatar}
        />
      )}
      <View style={styles.messageContent}>
        <Text style={[
          styles.messageText,
          { color: isUser ? theme.colors.onPrimaryContainer : theme.colors.onSurface }
        ]}>
          {message.content}
        </Text>
      </View>
    </View>
  );
};

// 首页屏幕
const HomeScreen: React.FC = () => {
  const theme = useTheme();
  const navigation = useNavigation<NativeStackNavigationProp<RootStackParamList>>();
  const [messages, setMessages] = useState<Message[]>(MOCK_MESSAGES);
  const [inputText, setInputText] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const flatListRef = useRef<FlatList>(null);

  // 自动滚动到最新消息
  useEffect(() => {
    if (messages.length > 0) {
      setTimeout(() => {
        flatListRef.current?.scrollToEnd({ animated: true });
      }, 100);
    }
  }, [messages]);

  // 发送消息
  const handleSendMessage = () => {
    if (!inputText.trim()) return;
    
    // 创建用户消息
    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputText,
      sender: 'user',
      contentType: 'text',
      timestamp: Date.now()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);
    
    // 模拟API响应延迟
    setTimeout(() => {
      // 创建智能体响应
      const agentMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: `我理解您的问题是"${inputText}"。我正在思考如何回答...`,
        sender: 'agent',
        contentType: 'text',
        timestamp: Date.now()
      };
      
      setMessages(prev => [...prev, agentMessage]);
      setIsLoading(false);
    }, 1000);
  };

  // 开始四诊功能
  const handleStartDiagnosis = () => {
    navigation.navigate('Diagnosis');
  };

  // 渲染健康卡片
  const renderHealthCard = () => (
    <Card style={styles.healthCard}>
      <Card.Title 
        title="今日健康" 
        subtitle="点击了解详情" 
        left={(props) => <Icon name="heart-pulse" size={24} color={theme.colors.primary} />}
      />
      <Card.Content>
        <View style={styles.healthMetrics}>
          <View style={styles.metric}>
            <Text style={styles.metricValue}>7.2</Text>
            <Text style={styles.metricLabel}>睡眠(小时)</Text>
          </View>
          <View style={styles.metric}>
            <Text style={styles.metricValue}>6,521</Text>
            <Text style={styles.metricLabel}>步数</Text>
          </View>
          <View style={styles.metric}>
            <Text style={styles.metricValue}>72</Text>
            <Text style={styles.metricLabel}>心率(次/分)</Text>
          </View>
        </View>
      </Card.Content>
      <Card.Actions>
        <Button onPress={handleStartDiagnosis}>
          开始四诊
        </Button>
      </Card.Actions>
    </Card>
  );

  return (
    <KeyboardAvoidingView 
      style={styles.container} 
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      keyboardVerticalOffset={Platform.OS === 'ios' ? 88 : 0}
    >
      {/* 健康卡片区域 */}
      {renderHealthCard()}
      
      <Divider style={styles.divider} />
      
      {/* 消息列表 */}
      <FlatList
        ref={flatListRef}
        data={messages}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => <MessageBubble message={item} />}
        style={styles.messagesList}
        contentContainerStyle={styles.messagesContainer}
      />
      
      {/* 输入区域 */}
      <View style={styles.inputContainer}>
        <IconButton
          icon="image"
          size={24}
          onPress={() => console.log('选择图片')}
          style={styles.iconButton}
        />
        <TextInput
          style={[styles.input, { backgroundColor: theme.colors.surface }]}
          value={inputText}
          onChangeText={setInputText}
          placeholder="输入消息..."
          multiline
        />
        {inputText.trim() ? (
          <IconButton
            icon="send"
            size={24}
            onPress={handleSendMessage}
            style={styles.iconButton}
          />
        ) : (
          <IconButton
            icon="microphone"
            size={24}
            onPress={() => setIsRecording(true)}
            style={styles.iconButton}
          />
        )}
      </View>
      
      {/* 加载指示器 */}
      {isLoading && (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="small" color={theme.colors.primary} />
          <Text style={styles.loadingText}>小艾正在思考...</Text>
        </View>
      )}
      
      {/* 录音界面 - 实际项目中应该是单独的组件 */}
      {isRecording && (
        <View style={styles.recordingOverlay}>
          <View style={styles.recordingContainer}>
            <Icon name="microphone" size={48} color={theme.colors.primary} />
            <Text style={styles.recordingText}>正在录音...</Text>
            <Button 
              mode="contained" 
              onPress={() => setIsRecording(false)}
              style={styles.recordingButton}
            >
              停止录音
            </Button>
          </View>
        </View>
      )}
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F8F8',
  },
  healthCard: {
    margin: 16,
    elevation: 2,
  },
  healthMetrics: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginVertical: 8,
  },
  metric: {
    alignItems: 'center',
  },
  metricValue: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  metricLabel: {
    fontSize: 12,
    color: '#666',
  },
  divider: {
    marginHorizontal: 16,
  },
  messagesList: {
    flex: 1,
  },
  messagesContainer: {
    padding: 16,
  },
  messageBubble: {
    maxWidth: '80%',
    padding: 12,
    borderRadius: 16,
    marginBottom: 8,
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  userBubble: {
    alignSelf: 'flex-end',
    borderBottomRightRadius: 0,
  },
  agentBubble: {
    alignSelf: 'flex-start',
    borderBottomLeftRadius: 0,
  },
  avatar: {
    marginRight: 8,
  },
  messageContent: {
    flex: 1,
  },
  messageText: {
    fontSize: 16,
    lineHeight: 22,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 8,
    backgroundColor: '#F0F0F0',
  },
  iconButton: {
    margin: 0,
  },
  input: {
    flex: 1,
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 8,
    maxHeight: 120,
    marginHorizontal: 8,
  },
  loadingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 8,
    backgroundColor: 'rgba(0, 0, 0, 0.03)',
  },
  loadingText: {
    marginLeft: 8,
    fontSize: 14,
    color: '#666',
  },
  recordingOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 1000,
  },
  recordingContainer: {
    width: 200,
    height: 200,
    backgroundColor: 'white',
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 16,
  },
  recordingText: {
    marginTop: 16,
    marginBottom: 24,
    fontSize: 16,
  },
  recordingButton: {
    width: '100%',
  },
});

export default HomeScreen; 