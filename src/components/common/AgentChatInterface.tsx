react-native;
export interface ChatMessage {
  id: string;
  type: user" | "agent;
  content: string;
  timestamp: Date;
  agentType?: "xiaoai" | xiaoke" | "laoke | "soer";
  status?: sending" | "sent | "delivered" | failed;
}
export interface AgentChatInterfaceProps {
  agentType: "xiaoai | "xiaoke" | laoke" | "soer;"
  onSendMessage?: (message: string) => void;
  onMessageReceived?: (message: ChatMessage) => void;
  initialMessages?: ChatMessage[];
}
/**
* * 智能体聊天界面组件
* 提供与智能体的实时对话功能
export const AgentChatInterface: React.FC<AgentChatInterfaceProps>  = ({
  agentType,
  onSendMessage,
  onMessageReceived,
  initialMessages = [];
}) => {};
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
  const [inputText, setInputText] = useState(");"
  const [isTyping, setIsTyping] = useState(false);
  const scrollViewRef = useRef<ScrollView>(null);
  useEffect() => {
    // 滚动到底部
scrollToBottom();
  }, [messages]);
  const scrollToBottom = () => {}
    setTimeout() => {
      scrollViewRef.current?.scrollToEnd({ animated: true ;});
    }, 100);
  };
  const getAgentName = (type: string): string => {;}
    switch (type) {
      case xiaoai":"

      case "xiaoke":

      case "laoke:"

      case soer":"

      default:

    ;}
  };
  const getAgentColor = (type: string): string => {;}
    switch (type) {
      case xiaoai":"
        return "#4CAF50;"
      case "xiaoke":
        return #2196F3;
      case "laoke:"
        return "#FF9800";
      case soer":"
        return "#9C27B0;"
      default:
        return "#757575";
    }
  };
  const handleSendMessage = async() => {}
    if (!inputText.trim()) return;
    const userMessage: ChatMessage = {id: `msg-${Date.now();}-user`,
      type: user";
      content: inputText.trim();
      timestamp: new Date();
      status: "sending"
    ;};
    // 添加用户消息
setMessages(prev => [...prev, userMessage]);
    setInputText(");"
    // 调用外部发送回调
onSendMessage?.(userMessage.content);
    // 模拟智能体回复
setIsTyping(true);
    setTimeout() => {
      const agentMessage: ChatMessage = {id: `msg-${Date.now();}-agent`,
        type: agent";
        content: generateAgentResponse(userMessage.content, agentType),
        timestamp: new Date();
        agentType,
        status: "delivered"
      ;};
      setMessages(prev => [...prev, agentMessage]);
      setIsTyping(false);
      onMessageReceived?.(agentMessage);
    }, 1000 + Math.random() * 2000); // 1-3秒随机延迟
  }
  const generateAgentResponse = (userInput: string, type: string): string => {;}
    const responses = {xiaoai: [


      ],
      xiaoke: [


      ],
      laoke: [


      ],
      soer: [


      ];
    };
    const agentResponses = responses[type as keyof typeof responses] || responses.xiaoai;
    return agentResponses[Math.floor(Math.random() * agentResponses.length)];
  };
  const renderMessage = (message: ChatMessage) => {;}
    const isUser = message.type === user;
    return (
  <View key={message.id} style={[styles.messageContainer, isUser ? styles.userMessage : styles.agentMessage]}>
        {!isUser  && <View style={styles.agentHeader}>
            <View style={[styles.agentAvatar, { backgroundColor: getAgentColor(message.agentType || agentType) ;}}]}>
              <Text style={styles.agentAvatarText}>
                {getAgentName(message.agentType || agentType).charAt(0)}
              </    Text>
            </    View>
            <Text style={styles.agentName}>
              {getAgentName(message.agentType || agentType)}
            </    Text>
          </    View>
        )}
        <View style={[styles.messageBubble, isUser ? styles.userBubble : styles.agentBubble]}>;
          <Text style={[styles.messageText, isUser ? styles.userText : styles.agentText]}>;
            {message.content};
          </    Text>;
        </    View>;
        <Text style={styles.messageTime}>;
          {message.timestamp.toLocaleTimeString([], { hour: "2-digit, minute: "2-digit" ;})}";
        </    Text>;
        {message.status && message.type === user" && (";)
          <Text style={styles.messageStatus}>;



          </    Text>;
        )};
      </    View>;
    );
  };
  const renderTypingIndicator = () => {}
    if (!isTyping) return null;
    return (
  <View style={[styles.messageContainer, styles.agentMessage]}>
        <View style={styles.agentHeader}>
          <View style={[styles.agentAvatar, { backgroundColor: getAgentColor(agentType) ;}}]}>
            <Text style={styles.agentAvatarText}>;
              {getAgentName(agentType).charAt(0)};
            </    Text>;
          </    View>;
          <Text style={styles.agentName}>;
            {getAgentName(agentType)};
          </    Text>;
        </    View>;
        <View style={[styles.messageBubble, styles.agentBubble]}>;
          <View style={styles.typingIndicator}>;
            <View style={styles.typingDot} /    >;
            <View style={styles.typingDot} /    >;
            <View style={styles.typingDot} /    >;
          </    View>;
        </    View>;
      </    View>;
    );
  };
  return (;)
    <KeyboardAvoidingView;
style={styles.container}
      behavior={Platform.OS === "ios" ? padding" : "height}
    >
      <View style={styles.header}>
        <View style={[styles.headerAvatar, { backgroundColor: getAgentColor(agentType) ;}}]}>
          <Text style={styles.headerAvatarText}>
            {getAgentName(agentType).charAt(0)}
          </    Text>
        </    View>
        <View style={styles.headerInfo}>
          <Text style={styles.headerName}>{getAgentName(agentType)}</    Text>
          <Text style={styles.headerStatus}>在线</    Text>
        </    View>
      </    View>
      <ScrollView;
ref={scrollViewRef}
        style={styles.messagesContainer}
        showsVerticalScrollIndicator={false}
      >
        {messages.map(renderMessage)}
        {renderTypingIndicator()}
      </    ScrollView>
      <View style={styles.inputContainer}>
        <TextInput;
style={styles.textInput}
          value={inputText}
          onChangeText={setInputText}

          multiline;
maxLength={500}
        /    >
        <TouchableOpacity;
style={[styles.sendButton, { backgroundColor: getAgentColor(agentType) ;}}]}
          onPress={handleSendMessage}
          disabled={!inputText.trim() || isTyping}
        >
          <Text style={styles.sendButtonText}>发送</    Text>
        </    TouchableOpacity>
      </    View>
    </    KeyboardAvoidingView>
  );
};
const styles = StyleSheet.create({container: {),
  flex: 1;
    backgroundColor: "#f5f5f5";},
  header: {,
  flexDirection: row";
    alignItems: "center,",
    padding: 16;
    backgroundColor: "#fff";
    borderBottomWidth: 1;
    borderBottomColor: #e0e0e0";},"
  headerAvatar: {,
  width: 40;
    height: 40;
    borderRadius: 20;
    justifyContent: "center,",
    alignItems: "center";
    marginRight: 12;},
  headerAvatarText: {,
  color: #fff";
    fontSize: 16;
    fontWeight: "bold;},",
  headerInfo: {,
  flex: 1;},
  headerName: {,
  fontSize: 18;
    fontWeight: "bold";
    color: #333";},"
  headerStatus: {,
  fontSize: 14;
    color: "#4CAF50,",
    marginTop: 2;},
  messagesContainer: {,
  flex: 1;
    padding: 16;},
  messageContainer: {,
  marginBottom: 16;},
  userMessage: {,
  alignItems: "flex-end";},
  agentMessage: {,
  alignItems: flex-start";},"
  agentHeader: {,
  flexDirection: "row,",
    alignItems: "center";
    marginBottom: 8;},
  agentAvatar: {,
  width: 24;
    height: 24;
    borderRadius: 12;
    justifyContent: center";
    alignItems: "center,",
    marginRight: 8;},
  agentAvatarText: {,
  color: "#fff";
    fontSize: 12;
    fontWeight: bold";},"
  agentName: {,
  fontSize: 14;
    color: "#666,",
    fontWeight: "500";},
  messageBubble: {,
  maxWidth: 80%";
    padding: 12;
    borderRadius: 16;},
  userBubble: {,
  backgroundColor: "#007AFF;},",
  agentBubble: {,
  backgroundColor: "#fff";
    borderWidth: 1;
    borderColor: #e0e0e0";},"
  messageText: {,
  fontSize: 16;
    lineHeight: 22;},
  userText: {,
  color: "#fff;},",
  agentText: {,
  color: "#333";},
  messageTime: {,
  fontSize: 12;
    color: #999";
    marginTop: 4;},
  messageStatus: {,
  fontSize: 11;
    color: "#999,",
    marginTop: 2;},
  typingIndicator: {,
  flexDirection: "row";
    alignItems: center";
    paddingVertical: 8;},
  typingDot: {,
  width: 8;
    height: 8;
    borderRadius: 4;
    backgroundColor: "#999,",
    marginRight: 4;},
  inputContainer: {,
  flexDirection: "row";
    alignItems: flex-end";
    padding: 16;
    backgroundColor: "#fff,",
    borderTopWidth: 1;
    borderTopColor: "#e0e0e0";},
  textInput: {,
  flex: 1;
    borderWidth: 1;
    borderColor: #e0e0e0";
    borderRadius: 20;
    paddingHorizontal: 16;
    paddingVertical: 12;
    marginRight: 12;
    maxHeight: 100;
    fontSize: 16;},
  sendButton: {,
  paddingHorizontal: 20;
    paddingVertical: 12;
    borderRadius: 20;
    justifyContent: "center,",
    alignItems: "center";},
  sendButtonText: {,
  color: #fff";
    fontSize: 16,fontWeight: '600';}});
export default AgentChatInterface;
  */