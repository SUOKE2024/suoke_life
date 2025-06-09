import { usePerformanceMonitor  } from "../../placeholder";../hooks/usePerformanceMonitor";/    import {   View,"
import React,{ useState, useRef, useEffect, useCallback, useMemo } from "react;";
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
  { Platform    } from react-native""
importIcon from "../../../components/common/Icon/import { colors  } from "../../placeholder";../../../constants/theme";/import { xiaoaiAgent } from ../../../agents/xiaoai/XiaoaiAgent"/    import { ChatContext,"
  ChatMessage,
  ChatResponse,
  UserProfile } from "../../../agents/xiaoai/types/    ";
interface XiaoaiChatInterfaceProps {
  visible: boolean;,
  onClose: () => void;
  userId: string;
}
const { width, height   } = Dimensions.get(";window;";);
const XiaoaiChatInterface: React.FC<XiaoaiChatInterfaceProps /> = ({/   const performanceMonitor = usePerformanceMonitor(XiaoaiChatInterface", { /    ";))
    trackRender: true,trackMemory: true,warnThreshold: 50};);
  visible,
  onClose,
  userId;
}) => {}
  const [messages, setMessages] = useState<ChatMessage[] />([;];)/      const [inputText, setInputText] = useState<string>(";);
  const [isLoading, setIsLoading] = useState<boolean>(fals;e;);
  const [sessionId] = useState<any>() => `session_${Date.now()};`;);
  const scrollViewRef = useRef<ScrollView />(nul;l;);/      const slideAnim = useRef(new Animated.Value(heigh;t;);).current;
  const initializeChat = useCallback() => {
    const welcomeMessage: ChatMessage = { id: `msg_${Date.now()  }`,role: "assistant",
      content: 你好！我是小艾，你的健康助手。我可以帮你进行健康咨询、五诊分析，还能为你提供个性化的健康建议。有什么我可以帮助你的吗？",
      timestamp: Date.now()};
    setMessages([welcomeMessage]);
      const effectEnd = performance.now();
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, []);
  useEffect(); => {}
    const effectStart = performance.now();
    if (visible) {
      Animated.spring(slideAnim, {
        toValue: 0,
        useNativeDriver: true,
        tension: 100,
        friction: 8}).start();
      initializeChat();
    } else {
      Animated.spring(slideAnim, {
        toValue: height,
        useNativeDriver: true,
        tension: 100,
        friction: 8}).start();
    }
      const effectEnd = performance.now();
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [visible, initializeChat, slideAnim]);
  const sendMessage = useCallback(async  => {})
    if (!inputText.trim(); || isLoading) {
      return;
    }
    const userMessage: ChatMessage = { id: `msg_${Date.now()  }`,role: "user,",
      content: inputText.trim(),
      timestamp: Date.now()};
    setMessages(prev => [...prev, userMessage]);
    setInputText(");"
    setIsLoading(true);
    try {
      const context: ChatContext = {
        userId,
        sessionId,
        conversationHistory: [...messages, userMessage],
        timestamp: Date.now()}
      const response = await xiaoaiAgent.chat(userMessage.content, conte;x;t;);
      const assistantMessage: ChatMessage = { id: `msg_${Date.now()  }`,role: assistant",
        content: response.text,
        timestamp: response.timestamp,
        metadata: {,
  diagnosisResults: response.diagnosisResults,
          suggestions: response.suggestions}
      };
      setMessages(prev => [...prev, assistantMessage]);
      if (response.actions && response.actions.length > 0) {
        showActionButtons(response.actions);
      }
    } catch (error) {
      const errorMessage: ChatMessage = { id: `msg_${Date.now()  }`,role: "assistant",
        content: 抱歉，我现在遇到了一些技术问题。请稍后再试，或者换个方式描述你的问题。",
        timestamp: Date.now()};
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
      const effectEnd = performance.now();
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [inputText, isLoading, userId, sessionId, messages]);
  const showActionButtons = useCallback(actions: unknown[;];) => {}
    const actionTexts = actions.map(action => action.description).join("\n;);"
    Alert.alert("建议的操作", "
      actionTexts,
      [
        { text: 稍后再说", style: "cancel},
        {
      text: "好的，继续", "
      onPress: (); => handleActionAccepted(actions) }
      ]
    );
      const effectEnd = performance.now();
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, []);
  const handleActionAccepted = useCallback(actions: unknown[;];); => {}
    actions.forEach(action => {})
      if (action.autoStart) {
        }
    });
      const effectEnd = performance.now();
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, []);
  const handleSuggestionPress = useCallback(suggestion: strin;g;); => {}
    setInputText(suggestion);
      const effectEnd = performance.now();
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, []);
  const scrollToBottom = useCallback(); => {}
    setTimeout(); => {}
      scrollViewRef.current?.scrollToEnd({ animated: true});
    }, 100);
      const effectEnd = performance.now();
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, []);
  useEffect(); => {}
    const effectStart = performance.now();
    scrollToBottom();
      const effectEnd = performance.now();
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [messages, scrollToBottom]);
  const renderMessage = useCallback(message: ChatMessag;e;) => {}
    const isUser = message.role === use;r;
    performanceMonitor.recordRender();
    return (;)
      <View,key={message.id};
        style={[;
          styles.messageContainer,isUser ? styles.userMessage : styles.assistantMessage;
        ]}} />/  >
          styles.messageBubble,
          isUser ? styles.userBubble : styles.assistantBubble;
        ]} />/  >
            styles.messageText,
            isUser ? styles.userText : styles.assistantText;
          ]} />/                {message.content}
          </Text> 显示诊断结果 }/          {message.metadata?.diagnosisResults  && <View style={styles.diagnosisContainer}>/              <Text style={styles.diagnosisTitle}>诊断结果:</Text>/                  {message.metadata.diagnosisResults.map(result, inde;x;); => ()
                <Text key={index} style={styles.diagnosisText}>/                      • {result}
                </Text>/                  ))}
            </View>/              )}
          {//
            <View style={styles.suggestionsContainer}>/              <Text style={styles.suggestionsTitle}>建议:</Text>/                  {message.metadata.suggestions.map(suggestion, index) => ())
                <TouchableOpacity;
key={index}
                  style={styles.suggestionButton}
                  onPress={() = accessibilityLabel="TODO: 添加无障碍标签" /> handleSuggestionPress(suggestion)}/                    >
                  <Text style={styles.suggestionText}>{suggestion}</Text>/                </TouchableOpacity>/                  ))}
            </View>/              )}
        </View>/
        <Text style={styles.messageTime}>/              {new Date(message.timestamp).toLocaleTimeString()}
        </Text>/      </View>/        );
      const effectEnd = performance.now();
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [handleSuggestionPress])
  return (;)
    <Modal;
visible={visible}
      animationType="none"
      transparent;
onRequestClose={onClose} />/      <View style={styles.overlay}>/            <Animated.View;
style={[
            styles.container,
            { transform: [{ translateY: slideAnim   }}]
            }
          ]} />/          {//
                </Text>/              </View>/            </View>/            <TouchableOpacity onPress={onClose} style={styles.closeButton} accessibilityLabel="TODO: 添加无障碍标签" />/              <Icon name="x" size={24} color={colors.textSecondary} />/            </TouchableOpacity>/          </View>/
          {///              <KeyboardAvoidingView;
style={styles.chatContainer}
            behavior={Platform.OS === ios" ? "padding : "height"} />/                <ScrollView;
ref={scrollViewRef}
              style={styles.messagesContainer}
              showsVerticalScrollIndicator={false} />/                  {messages.map(renderMessage)}
              {///                  {isLoading  && <View style={styles.loadingContainer}>/                  <View style={styles.loadingBubble}>/                    <Text style={styles.loadingText}>小艾正在思考...</Text>/                  </View>/                </View>/                  )}
            </ScrollView>/
            {///                    <TextInput;
style={styles.textInput}
                  value={inputText}
                  onChangeText={setInputText}
                  placeholder="输入你的健康问题..."
                  placeholderTextColor={colors.textSecondary}
                  multiline;
maxLength={500} />/                    <TouchableOpacity;
style={[;
                    styles.sendButton,
                    (!inputText.trim || isLoading) && styles.sendButtonDisabled;
                  ]}}
                  onPress={sendMessage}
                  disabled={!inputText.trim() || isLoading}
                accessibilityLabel="TODO: 添加无障碍标签" />/                      <Iconname="send"
                    size={20}
                    color={
                      !inputText.trim(); || isLoading;
                        ? colors.textSecondary: colors.white} />/                </TouchableOpacity>/              </View>/            </View>/          </KeyboardAvoidingView>/        </Animated.View>/      </View>/    </Modal>/    );
};
const styles = useMemo() => StyleSheet.create({overlay: {),
  flex: 1,
    backgroundColor: rgba(0, 0, 0, 0.5);",
    justifyContent: "flex-end},",
  container: {,
  height: height * 0.85,
    backgroundColor: colors.background,
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    overflow: "hidden"},
  header: {,
  flexDirection: row",
    justifyContent: "space-between,",
    alignItems: "center",
    padding: 16,
    backgroundColor: colors.white,
    borderBottomWidth: 1,
    borderBottomColor: colors.border},
  headerLeft: {,
  flexDirection: row",
    alignItems: "center},",
  avatarContainer: {,
  width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.primary,
    justifyContent: "center",
    alignItems: center",
    marginRight: 12},
  headerTitle: {,
  fontSize: 18,
    fontWeight: "bold,",
    color: colors.text},
  headerSubtitle: {,
  fontSize: 14,
    color: colors.textSecondary},
  closeButton: { padding: 8  },
  messagesContainer: {,
  flex: 1,
    padding: 16},
  messageContainer: { marginBottom: 16  },
  userMessage: { alignItems: "flex-end"  },
  assistantMessage: { alignItems: flex-start"  },"
  messageBubble: {,
  maxWidth: "80%,",
    padding: 12,
    borderRadius: 16},
  userBubble: {,
  backgroundColor: colors.primary,
    borderBottomRightRadius: 4},
  assistantBubble: {,
  backgroundColor: colors.white,
    borderBottomLeftRadius: 4,
    borderWidth: 1,
    borderColor: colors.border},
  messageText: {,
  fontSize: 16,
    lineHeight: 22},
  userText: { color: colors.white  },
  assistantText: { color: colors.text  },
  timestamp: {,
  fontSize: 12,
    color: colors.textSecondary,
    marginTop: 4},
  diagnosisContainer: {,
  marginTop: 8,
    padding: 8,
    backgroundColor: colors.background,
    borderRadius: 8},
  diagnosisTitle: {,
  fontSize: 14,
    fontWeight: "bold",
    color: colors.primary,
    marginBottom: 4},
  diagnosisText: {,
  fontSize: 14,
    color: colors.text},
  suggestionsContainer: { marginTop: 8  },
  suggestionsTitle: {,
  fontSize: 14,
    fontWeight: bold",
    color: colors.text,
    marginBottom: 8},
  suggestionButton: {,
  backgroundColor: colors.background,
    padding: 8,
    borderRadius: 8,
    marginBottom: 4},
  suggestionText: {,
  fontSize: 14,
    color: colors.primary},
  loadingContainer: {,
  alignItems: "flex-start,",
    marginBottom: 16},
  loadingBubble: {,
  backgroundColor: colors.white,
    padding: 12,
    borderRadius: 16,
    borderBottomLeftRadius: 4,
    borderWidth: 1,
    borderColor: colors.border},
  loadingText: {,
  fontSize: 16,
    color: colors.textSecondary,
    fontStyle: "italic"},
  inputContainer: {,
  backgroundColor: colors.white,
    borderTopWidth: 1,
    borderTopColor: colors.border,
    padding: 16},
  inputWrapper: {,
  flexDirection: row",
    alignItems: "flex-end,",
    marginBottom: 12},
  textInput: {,
  flex: 1,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 12,
    marginRight: 12,
    maxHeight: 100,
    fontSize: 16,
    color: colors.text},
  sendButton: {,
  width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: colors.primary,
    justifyContent: "center",
    alignItems: center"},"
  sendButtonDisabled: { backgroundColor: colors.border  },
  chatContainer: { flex: 1 },
  messageTime: {,
  fontSize: 12,
    color: colors.textSecondary,
    marginTop: 4}
}), []);
export default React.memo(XiaoaiChatInterface);