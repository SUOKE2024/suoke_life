import Icon from './Icon';
import { colors, spacing } from '../../constants/theme';
import { accessibilityService, AgentAccessibilityHelper } from '../../services/accessibilityService';
import * as ImagePicker from 'expo-image-picker';
import * as DocumentPicker from 'expo-document-picker';
import { Audio, Video } from 'expo-av';
import {
import { AgentVoiceInput, AgentEmotionFeedback, AgentChatBubble, ResponsiveContainer } from '../index';

  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  ScrollView,
  Alert,
  Modal,
  Animated,
  Dimensions,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
  Image,
} from 'react-native';
import React, { useState, useRef, useEffect, useMemo, useCallback } from 'react';

export type AgentType = 'xiaoai' | 'xiaoke' | 'laoke' | 'soer';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
  metadata?: {
    suggestions?: string[];
    actions?: any[];
    diagnosisResults?: any;
    multimodal?: any;
  };
}

interface AgentChatInterfaceProps {
  visible: boolean;
  onClose: () => void;
  agentType: AgentType;
  userId: string;
  initialMessage?: string;
  accessibilityEnabled?: boolean;
}

const { width, height } = Dimensions.get('window');

// 智能体配置
const AGENT_CONFIG = useMemo(() => {
  xiaoai: {
    name: '小艾',
    emoji: '🤖',
    color: '#007AFF',
    specialization: '健康诊断与建议',
    welcomeMessage: '你好！我是小艾，你的健康助手。我可以帮你进行健康咨询、五诊分析，还能为你提供个性化的健康建议。有什么我可以帮助你的吗？',
    quickReplies: ['我想做健康检查', '最近感觉不舒服', '想了解我的体质', '需要健康建议'],
  },
  xiaoke: {
    name: '小克',
    emoji: '👨‍⚕️',
    color: '#34C759',
    specialization: '医疗服务管理',
    welcomeMessage: '您好！我是小克，您的专业医疗服务管理助手。我可以帮您选择合适的诊断服务、预约医疗服务、管理健康订阅，还能为您推荐健康产品。',
    quickReplies: ['预约医生', '查看健康报告', '购买健康产品', '管理订阅服务'],
  },
  laoke: {
    name: '老克',
    emoji: '👴',
    color: '#8E44AD',
    specialization: '中医养生教育',
    welcomeMessage: '小友，你好！老夫是老克，专注中医养生教育多年。中医养生之道，在于顺应自然，调和阴阳。有什么养生问题，尽管问老夫。',
    quickReplies: ['学习中医理论', '了解养生方法', '体质调养建议', '中药材知识'],
  },
  soer: {
    name: '索儿',
    emoji: '👧',
    color: '#FF2D92',
    specialization: '生活方式指导',
    welcomeMessage: '嗨！我是索儿，你的生活方式指导助手。我会帮你规划健康的生活安排，提供个性化的生活建议，让你的每一天都充满活力！',
    quickReplies: ['制定生活计划', '健康生活建议', '工作生活平衡', '心情调节方法'],
  },
}, []);

const AgentChatInterface: React.FC<AgentChatInterfaceProps> = ({
  visible,
  onClose,
  agentType,
  userId,
  initialMessage,
  accessibilityEnabled = false,
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => `session_${Date.now()}`);
  const [isVoiceMode, setIsVoiceMode] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const scrollViewRef = useMemo(() => useRef<ScrollView>(null), []);
  const slideAnim = useMemo(() => useRef(new Animated.Value(height)).current, []);
  const [selectedFiles, setSelectedFiles] = useState<any[]>([]);
  const [recording, setRecording] = useState<any>(null);
  const [audioFiles, setAudioFiles] = useState<any[]>([]);
  const [videoFiles, setVideoFiles] = useState<any[]>([]);

  const agentConfig = useMemo(() => useMemo(() => AGENT_CONFIG[agentType], [agentType]), []);
  const accessibilityHelper = useMemo(() => useMemo(() => 
    new AgentAccessibilityHelper(accessibilityService, agentType), 
    [agentType]
  ), []);

  useEffect(() => {
    if (visible) {
      // 显示动画
      Animated.spring(slideAnim, {
        toValue: 0,
        useNativeDriver: true,
        tension: 100,
        friction: 8,
      }).start();

      // 初始化对话
      initializeChat();
    } else {
      // 隐藏动画
      Animated.spring(slideAnim, {
        toValue: height,
        useNativeDriver: true,
        tension: 100,
        friction: 8,
      }).start();
    }
  }, [visible, slideAnim]);

  useEffect(() => {
    if (initialMessage && visible) {
      setInputText(initialMessage);
    }
  }, [initialMessage, visible]);

  const initializeChat = useMemo(() => useCallback(() => {
    const welcomeMessage: ChatMessage = {
      id: `msg_${Date.now()}`,
      role: 'assistant',
      content: agentConfig.welcomeMessage,
      timestamp: Date.now(),
      metadata: {
        suggestions: agentConfig.quickReplies,
      },
    }, []);
    setMessages([welcomeMessage]);
  }, [agentConfig]);

  const handlePickImage = useMemo(() => useCallback(async () => {
    const result = await ImagePicker.launchImageLibraryAsync({ mediaTypes: ImagePicker.MediaTypeOptions.All }), []);
    if (!result.canceled && result.assets && result.assets.length > 0) {
      setSelectedFiles(prev => [...prev, result.assets[0]]);
    }
  }, []);

  const handlePickFile = useMemo(() => useCallback(async () => {
    const result = await DocumentPicker.getDocumentAsync({ type: '*/*' }), []);
    if (result.type === 'success') {
      setSelectedFiles(prev => [...prev, result]);
    }
  }, []);

  const handleRecordAudio = useMemo(() => useCallback(async () => {
    try {
      const { status } = await Audio.requestPermissionsAsync(), []);
      if (status !== 'granted') {
        Alert.alert('权限不足', '请允许麦克风权限');
        return;
      }
      const rec = useMemo(() => new Audio.Recording(), []);
      await rec.prepareToRecordAsync(Audio.RECORDING_OPTIONS_PRESET_HIGH_QUALITY);
      await rec.startAsync();
      setRecording(rec);
    } catch (e) {
      Alert.alert('录音失败', String(e));
    }
  }, []);

  const handleStopAudio = useMemo(() => useCallback(async () => {
    if (!recording) return, []);
    await recording.stopAndUnloadAsync();
    const uri = useMemo(() => recording.getURI(), []);
    if (uri) {
      setAudioFiles(prev => [...prev, { uri, name: `audio_${Date.now()}.wav`, type: 'audio/wav' }]);
      setSelectedFiles(prev => [...prev, { uri, name: `audio_${Date.now()}.wav`, type: 'audio/wav' }]);
    }
    setRecording(null);
  }, [recording]);

  const handlePickVideo = useMemo(() => useCallback(async () => {
    const result = await ImagePicker.launchImageLibraryAsync({ mediaTypes: ImagePicker.MediaTypeOptions.Videos }), []);
    if (!result.canceled && result.assets && result.assets.length > 0) {
      setVideoFiles(prev => [...prev, result.assets[0]]);
      setSelectedFiles(prev => [...prev, result.assets[0]]);
    }
  }, []);

  const sendMessage = useMemo(() => useCallback(async (messageText?: string) => {
    const textToSend = messageText || inputText.trim(), []);
    if ((!textToSend && selectedFiles.length === 0) || isLoading) {return;}
    setIsLoading(true);
    try {
      let multimodalResponse;
      if (selectedFiles.length > 0) {
        // 构建FormData
        const formData = useMemo(() => new FormData(), []);
        formData.append('query', textToSend);
        selectedFiles.forEach((file, idx) => {
          formData.append('files', {
            uri: file.uri || file.file?.uri,
            name: file.name || file.file?.name || `file_${idx}`,
            type: file.mimeType || file.type || 'application/octet-stream',
          } as any);
        });
        multimodalResponse = await apiClient.post('/api/v1/rag/query_multimodal', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
      } else {
        multimodalResponse = await callAgentAPI(textToSend);
      }
      // 展示多模态响应
      const assistantMessage: ChatMessage = {
        id: `msg_${Date.now()}`,
        role: 'assistant',
        content: multimodalResponse.data?.answer || multimodalResponse.text,
        timestamp: Date.now(),
        metadata: { multimodal: multimodalResponse.data?.multimodal_context },
      };
      setMessages(prev => [...prev, assistantMessage]);
      setSelectedFiles([]);
      setInputText('');
    } catch (error) {
      console.error(`与${agentConfig.name}对话失败:`, error);
      
      const errorMessage: ChatMessage = {
        id: `msg_${Date.now()}`,
        role: 'assistant',
        content: `抱歉，我现在遇到了一些技术问题。请稍后再试，或者换个方式描述你的问题。`,
        timestamp: Date.now(),
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [inputText, selectedFiles, isLoading, apiClient, callAgentAPI]);

  const callAgentAPI = useMemo(() => useCallback(async (message: string) => {
    // 根据智能体类型调用不同的API端点
    const apiEndpoints = {
      xiaoai: 'http://localhost:8080/api/agents/xiaoai/chat',
      xiaoke: 'http://localhost:8080/api/agents/xiaoke/chat',
      laoke: 'http://localhost:8080/api/agents/laoke/chat',
      soer: 'http://localhost:8080/api/agents/soer/chat',
    }, []);

    const response = useMemo(() => await fetch(apiEndpoints[agentType], {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        userId,
        sessionId,
        context: {
          previousMessages: messages.slice(-5), // 只发送最近5条消息作为上下文
        },
      }),
    }), []);

    if (!response.ok) {
      throw new Error(`API调用失败: ${response.status}`);
    }

    return await response.json();
  }, [agentType, messages, userId, sessionId]);

  const handleQuickReply = useMemo(() => useCallback((reply: string) => {
    sendMessage(reply), []);
  }, [sendMessage]);

  // 语音输入处理
  const handleVoiceInput = useMemo(() => useCallback(async () => {
    if (!accessibilityEnabled) {return, []);}

    try {
      setIsRecording(true);
      // 这里应该集成实际的语音录制功能
      // 暂时模拟语音输入
      Alert.alert('语音输入', '语音输入功能正在开发中，请使用文字输入');
    } catch (error) {
      console.error('语音输入失败:', error);
      Alert.alert('错误', '语音输入失败，请重试');
    } finally {
      setIsRecording(false);
    }
  }, [accessibilityEnabled]);

  // 切换语音模式
  const toggleVoiceMode = useMemo(() => useCallback(() => {
    if (!accessibilityEnabled) {
      Alert.alert('提示', '请在设置中启用无障碍功能'), []);
      return;
    }
    setIsVoiceMode(!isVoiceMode);
  }, [accessibilityEnabled, isVoiceMode]);

  // 朗读消息
  const speakMessage = useMemo(() => useCallback(async (message: string) => {
    if (!accessibilityEnabled) {return, []);}

    try {
      const audioData = useMemo(() => await accessibilityHelper.generateVoiceOutput(message, userId), []);
      if (audioData) {
        // 播放语音
        console.log('播放语音:', message);
      }
    } catch (error) {
      console.error('语音播放失败:', error);
    }
  }, [accessibilityEnabled, accessibilityHelper, userId]);

  // 内容无障碍转换
  const makeContentAccessible = useMemo(() => useCallback(async (content: string, format: 'audio' | 'large-text' | 'high-contrast') => {
    if (!accessibilityEnabled) {return content, []);}

    try {
      const response = useMemo(() => await accessibilityHelper.makeContentAccessible(content, userId, format), []);
      return response.accessibleContent || content;
    } catch (error) {
      console.error('内容转换失败:', error);
      return content;
    }
  }, [accessibilityEnabled, accessibilityHelper, userId]);

  const scrollToBottom = useMemo(() => useCallback(() => {
    setTimeout(() => {
      scrollViewRef.current?.scrollToEnd({ animated: true }), []);
    }, 100);
  }, [scrollViewRef]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const renderMessage = useMemo(() => useCallback((message: ChatMessage) => {
    const isUser = message.role === 'user', []);
    
    return (
      <AgentChatBubble
        key={message.id}
        agentType={message.role === 'assistant' ? agentType : 'user'}
        message={message.content}
        isVoice={!!message.metadata?.multimodal?.voice}
        onPlayVoice={() => {/* 语音播放逻辑 */}}
      />
    );
  }, [agentType]);

  const renderQuickReplies = useMemo(() => useCallback((suggestions: string[]) => (
    <View style={styles.quickRepliesContainer}>
      <Text style={styles.quickRepliesTitle}>快速回复：</Text>
      <ScrollView horizontal showsHorizontalScrollIndicator={false}>
        {suggestions.map((suggestion, index) => (
          <TouchableOpacity
            key={index}
            style={[styles.quickReplyButton, { borderColor: agentConfig.color }]}
            onPress={() => handleQuickReply(suggestion)}
          >
            <Text style={[styles.quickReplyText, { color: agentConfig.color }]}>
              {suggestion}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>
    </View>
  ), [agentConfig, handleQuickReply]), []);

  const handleClose = useMemo(() => useCallback(() => {
    Animated.spring(slideAnim, {
      toValue: height,
      useNativeDriver: true,
      tension: 100,
      friction: 8,
    }).start(() => {
      onClose(), []);
      // 清理状态
      setMessages([]);
      setInputText('');
      setIsLoading(false);
    });
  }, [onClose, slideAnim, height]);

  return (
    <ResponsiveContainer style={{ flex: 1 }}>
      <Modal
        visible={visible}
        transparent={true}
        animationType="none"
        onRequestClose={handleClose}
      >
        <View style={styles.overlay}>
          <Animated.View
            style={[
              styles.container,
              {
                transform: [{ translateY: slideAnim }],
              },
            ]}
          >
            {/* 头部 */}
            <View style={[styles.header, { backgroundColor: agentConfig.color }]}>
              <View style={styles.headerLeft}>
                <Text style={styles.agentEmojiLarge}>{agentConfig.emoji}</Text>
                <View>
                  <Text style={styles.agentName}>{agentConfig.name}</Text>
                  <Text style={styles.agentSpecialization}>{agentConfig.specialization}</Text>
                </View>
              </View>
              <TouchableOpacity style={styles.closeButton} onPress={handleClose}>
                <Icon name="close" size={24} color="white" />
              </TouchableOpacity>
            </View>

            {/* 消息列表 */}
            <KeyboardAvoidingView
              style={styles.chatContainer}
              behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
            >
              <ScrollView
                ref={scrollViewRef}
                style={styles.messagesContainer}
                showsVerticalScrollIndicator={false}
                contentContainerStyle={styles.messagesContent}
              >
                {messages.map(msg => (
                  <AgentChatBubble
                    key={msg.id}
                    agentType={msg.role === 'assistant' ? agentType : 'user'}
                    message={msg.content}
                    isVoice={!!msg.metadata?.multimodal?.voice}
                    onPlayVoice={() => {/* 语音播放逻辑 */}}
                  />
                ))}
                {/* 显示快速回复 */}
                {messages.length > 0 && 
                  messages[messages.length - 1].role === 'assistant' && 
                  messages[messages.length - 1].metadata?.suggestions && 
                  renderQuickReplies(messages[messages.length - 1].metadata!.suggestions!)}
                {isLoading && (
                  <View style={styles.loadingContainer}>
                    <View style={styles.agentAvatar}>
                      <Text style={styles.agentEmoji}>{agentConfig.emoji}</Text>
                    </View>
                    <View style={[styles.messageBubble, styles.assistantBubble, styles.loadingBubble]}>
                      <ActivityIndicator size="small" color={agentConfig.color} />
                      <Text style={styles.loadingText}>正在思考...</Text>
                    </View>
                  </View>
                )}
              </ScrollView>

              {/* 输入框 */}
              <View style={styles.inputContainer}>
                {/* 无障碍功能切换按钮 */}
                {accessibilityEnabled && (
                  <TouchableOpacity
                    style={[styles.accessibilityToggle, isVoiceMode && { backgroundColor: agentConfig.color + '20' }]}
                    onPress={toggleVoiceMode}
                  >
                    <Icon 
                      name={isVoiceMode ? "microphone" : "microphone-off"} 
                      size={20} 
                      color={isVoiceMode ? agentConfig.color : colors.textSecondary} 
                    />
                  </TouchableOpacity>
                )}
                
                <TextInput
                  style={[styles.textInput, accessibilityEnabled && styles.textInputWithAccessibility]}
                  value={inputText}
                  onChangeText={setInputText}
                  placeholder={isVoiceMode ? `语音与${agentConfig.name}对话...` : `与${agentConfig.name}对话...`}
                  placeholderTextColor={colors.textSecondary}
                  multiline
                  maxLength={500}
                  editable={!isLoading && !isVoiceMode}
                />
                
                {/* 语音输入按钮 */}
                {accessibilityEnabled && isVoiceMode && (
                  <TouchableOpacity
                    style={[
                      styles.voiceButton,
                      { backgroundColor: isRecording ? '#FF3B30' : agentConfig.color },
                    ]}
                    onPress={handleVoiceInput}
                    disabled={isLoading}
                  >
                    <Icon 
                      name={isRecording ? "stop" : "microphone"} 
                      size={20} 
                      color="white" 
                    />
                  </TouchableOpacity>
                )}
                
                {/* 多模态输入按钮区 */}
                <View style={{ flexDirection: 'row', marginBottom: 8 }}>
                  <TouchableOpacity onPress={handlePickImage} style={{ marginRight: 8 }}>
                    <Icon name="image" size={24} color={agentConfig.color} />
                  </TouchableOpacity>
                  <TouchableOpacity onPress={handlePickFile} style={{ marginRight: 8 }}>
                    <Icon name="attachment" size={24} color={agentConfig.color} />
                  </TouchableOpacity>
                  <TouchableOpacity onPress={recording ? handleStopAudio : handleRecordAudio} style={{ marginRight: 8 }}>
                    <Icon name={recording ? "stop" : "microphone"} size={24} color={agentConfig.color} />
                  </TouchableOpacity>
                  <TouchableOpacity onPress={handlePickVideo} style={{ marginRight: 8 }}>
                    <Icon name="video" size={24} color={agentConfig.color} />
                  </TouchableOpacity>
                </View>
                
                {/* 已选文件预览 */}
                {selectedFiles.length > 0 && (
                  <ScrollView horizontal style={{ marginBottom: 8 }}>
                    {selectedFiles.map((file, idx) => (
                      <View key={idx} style={{ marginRight: 8 }}>
                        {file.uri?.match(/\.(jpg|jpeg|png|gif)$/) ? (
                          <Image source={{ uri: file.uri }} style={{ width: 48, height: 48, borderRadius: 8 }} />
                        ) : file.uri?.match(/\.(mp4|mov|avi)$/) ? (
                          <Video source={{ uri: file.uri }} style={{ width: 64, height: 48, borderRadius: 8 }} useNativeControls resizeMode="cover" />
                        ) : file.uri?.match(/\.(wav|mp3|m4a)$/) ? (
                          <TouchableOpacity onPress={() => Audio.Sound.createAsync({ uri: file.uri }).then(({ sound }) => sound.replayAsync())}>
                            <Icon name="play" size={32} color={agentConfig.color} />
                            <Text style={{ fontSize: 12 }}>音频</Text>
                          </TouchableOpacity>
                        ) : (
                          <Text style={{ fontSize: 12 }}>{file.name || file.file?.name}</Text>
                        )}
                      </View>
                    ))}
                  </ScrollView>
                )}
                
                {/* 发送按钮 */}
                {(!isVoiceMode || !accessibilityEnabled) && (
                  <TouchableOpacity
                    style={[
                      styles.sendButton,
                      { backgroundColor: agentConfig.color },
                      (!inputText.trim() || isLoading) && styles.sendButtonDisabled,
                    ]}
                    onPress={() => sendMessage()}
                    disabled={!inputText.trim() || isLoading}
                  >
                    <Icon name="send" size={20} color="white" />
                  </TouchableOpacity>
                )}
              </View>

              {/* 在输入区下方集成多模态输入和情感反馈 */}
              <View style={{ width: '100%' }}>
                <AgentVoiceInput
                  onResult={text => setInputText(text)}
                  accessibilityEnabled={accessibilityEnabled}
                  style={{ marginBottom: 8 }}
                />
                <AgentEmotionFeedback
                  onFeedback={type => {
                    // 可扩展：将反馈通过事件总线上传后端
                    console.log('用户情感反馈:', type);
                  }}
                  style={{ marginBottom: 8 }}
                />
              </View>
            </KeyboardAvoidingView>
          </Animated.View>
        </View>
      </Modal>
    </ResponsiveContainer>
  );
};

const styles = useMemo(() => StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
  },
  container: {
    flex: 1,
    backgroundColor: colors.background,
    marginTop: 50,
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: spacing.lg,
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
  },
  headerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  agentEmojiLarge: {
    fontSize: 32,
    marginRight: spacing.md,
  },
  agentName: {
    fontSize: fonts.size.lg,
    fontWeight: '600',
    color: 'white',
  },
  agentSpecialization: {
    fontSize: fonts.size.xs,
    color: 'rgba(255, 255, 255, 0.8)',
    marginTop: 2,
  },
  closeButton: {
    padding: spacing.sm,
  },
  chatContainer: {
    flex: 1,
  },
  messagesContainer: {
    flex: 1,
  },
  messagesContent: {
    padding: spacing.md,
  },
  messageContainer: {
    flexDirection: 'row',
    marginBottom: spacing.md,
    alignItems: 'flex-end',
  },
  userMessage: {
    justifyContent: 'flex-end',
  },
  assistantMessage: {
    justifyContent: 'flex-start',
  },
  agentAvatar: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: colors.surface,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.sm,
  },
  agentEmoji: {
    fontSize: 16,
  },
  userAvatar: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: spacing.sm,
  },
  messageBubble: {
    maxWidth: width * 0.7,
    padding: spacing.md,
    borderRadius: 16,
    borderWidth: 1,
  },
  userBubble: {
    backgroundColor: colors.primary,
    borderColor: colors.primary,
    borderBottomRightRadius: 4,
  },
  assistantBubble: {
    backgroundColor: colors.surface,
    borderBottomLeftRadius: 4,
  },
  messageText: {
    fontSize: fonts.size.md,
    lineHeight: 20,
  },
  userText: {
    color: 'white',
  },
  assistantText: {
    color: colors.text,
  },
  messageTime: {
    fontSize: fonts.size.xs,
    color: colors.textSecondary,
    marginTop: spacing.xs,
    textAlign: 'right',
  },
  quickRepliesContainer: {
    marginTop: spacing.md,
    marginBottom: spacing.lg,
  },
  quickRepliesTitle: {
    fontSize: fonts.size.xs,
    color: colors.textSecondary,
    marginBottom: spacing.sm,
    marginLeft: 44, // 对齐消息气泡
  },
  quickReplyButton: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: 20,
    borderWidth: 1,
    marginRight: spacing.sm,
    marginLeft: spacing.xs,
  },
  quickReplyText: {
    fontSize: fonts.size.xs,
    fontWeight: '500',
  },
  loadingContainer: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    marginBottom: spacing.md,
  },
  loadingBubble: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  loadingText: {
    fontSize: fonts.size.xs,
    color: colors.textSecondary,
    marginLeft: spacing.sm,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    padding: spacing.md,
    backgroundColor: colors.surface,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  textInput: {
    flex: 1,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 20,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    marginRight: spacing.sm,
    maxHeight: 100,
    fontSize: fonts.size.md,
    color: colors.text,
    backgroundColor: colors.background,
  },
  sendButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  sendButtonDisabled: {
    opacity: 0.5,
  },
  accessibilityButtons: {
    flexDirection: 'row',
    marginTop: spacing.xs,
    marginBottom: spacing.xs,
  },
  accessibilityButton: {
    padding: spacing.xs,
    marginRight: spacing.xs,
    borderRadius: 12,
    backgroundColor: colors.background,
    borderWidth: 1,
    borderColor: colors.border,
  },
  accessibilityToggle: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.sm,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
  },
  textInputWithAccessibility: {
    marginRight: spacing.sm,
  },
  voiceButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: spacing.sm,
  },
}), []);

export default React.memo(AgentChatInterface); 