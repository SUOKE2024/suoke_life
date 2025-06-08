import {import { AgentType, AgentContext, AgentResponse } from "../../agents/types";
import { executeAgentTask, AgentSystemUtils } from "../../agents";
import React, { useState, useEffect, useCallback, useRef } from "react";
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  StyleSheet,
  Alert,
  ActivityIndicator,
  Animated,
  Dimensions;
} from "react-native";
/**
* 智能体界面属性
*/
interface AgentInterfaceProps {
  agentType?: AgentType;
  currentChannel?: string;
  userId: string;
  onResponse?: (response: AgentResponse) => void;
  onError?: (error: Error) => void;
  style?: any;
}
/**
* 消息类型
*/
interface Message {
  id: string;
  type: "user" | "agent";
  content: string;
  timestamp: Date;
  agentType?: AgentType;
  metadata?: any;
}
/**
* 智能体界面组件
* 提供统一的智能体交互界面
*/
export const AgentInterface: React.FC<AgentInterfaceProps> = ({
  agentType,
  currentChannel = "chat",
  userId,
  onResponse,
  onError,
  style;
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [currentAgent, setCurrentAgent] = useState<AgentType>(;
    agentType || AgentSystemUtils.getAgentByChannel(currentChannel);
  );
  const [sessionId] = useState(`session_${Date.now()}`);
  const scrollViewRef = useRef<ScrollView>(null);
  const fadeAnim = useRef(new Animated.Value(0)).current;
  useEffect() => {
    // 组件挂载时的淡入动画
    Animated.timing(fadeAnim, {
      toValue: 1,
      duration: 500,
      useNativeDriver: true;
    }).start();
    // 添加欢迎消息
    addWelcomeMessage();
  }, []);
  useEffect() => {
    // 当频道改变时更新智能体
    if (!agentType) {
      const newAgent = AgentSystemUtils.getAgentByChannel(currentChannel);
      setCurrentAgent(newAgent);
    }
  }, [currentChannel, agentType]);
  /**
  * 添加欢迎消息
  */
  const addWelcomeMessage = useCallback() => {const agentRole = AgentSystemUtils.getAgentRole(currentAgent);
    const welcomeMessage: Message = {,
  id: `welcome_${Date.now()}`,
      type: "agent",
      content: `你好！我是${agentRole.name}，${agentRole.description}。有什么可以帮助您的吗？`,
      timestamp: new Date(),
      agentType: currentAgent;
    };
    setMessages([welcomeMessage]);
  }, [currentAgent]);
  /**
  * 发送消息
  */
  const sendMessage = useCallback(async () => {if (!inputText.trim() || isLoading) {return;}
    const userMessage: Message = {,
  id: `user_${Date.now()}`,
      type: "user",
      content: inputText.trim(),
      timestamp: new Date();
    };
    setMessages(prev) => [...prev, userMessage]);
    setInputText("");
    setIsLoading(true);
    try {
      const context: AgentContext = {
        userId,
        sessionId,
        currentChannel,
        timestamp: new Date(),
        previousMessages: messages.slice(-5), // 最近5条消息作为上下文
      };
      const response = await executeAgentTask(inputText.trim(), context);
      const agentMessage: Message = {,
  id: `agent_${Date.now()}`,
        type: "agent",
        content: response.response,
        timestamp: new Date(),
        agentType: currentAgent,
        metadata: response.metadata;
      };
      setMessages(prev) => [...prev, agentMessage]);
      if (onResponse) {
        onResponse(response);
      }
    } catch (error) {
      const errorMessage: Message = {,
  id: `error_${Date.now()}`,
        type: "agent",
        content: "抱歉，处理您的请求时出现了问题。请稍后再试。",
        timestamp: new Date(),
        agentType: currentAgent;
      };
      setMessages(prev) => [...prev, errorMessage]);
      if (onError) {
        onError(error as Error);
      }
    } finally {
      setIsLoading(false);
    }
  }, [
    inputText,
    isLoading,
    userId,
    sessionId,
    currentChannel,
    messages,
    currentAgent,
    onResponse,
    onError;
  ]);
  /**
  * 切换智能体
  */
  const switchAgent = useCallback(newAgentType: AgentType) => {setCurrentAgent(newAgentType);
    const agentRole = AgentSystemUtils.getAgentRole(newAgentType);
    const switchMessage: Message = {,
  id: `switch_${Date.now()}`,
      type: "agent",
      content: `已切换到${agentRole.name}。${agentRole.description}`,
      timestamp: new Date(),
      agentType: newAgentType;
    };
    setMessages(prev) => [...prev, switchMessage]);
  }, []);
  /**
  * 清空对话
  */
  const clearMessages = useCallback() => {Alert.alert("清空对话",确定要清空当前对话吗？", [;
      {
      text: "取消",
      style: "cancel" },{
      text: "确定",
      onPress: () => {setMessages([]);
          addWelcomeMessage();
        }
      }
    ]);
  }, [addWelcomeMessage]);
  /**
  * 渲染消息
  */
  const renderMessage = useCallback(message: Message) => {const isUser = message.type === "user";
    const agentRole = message.agentType;
      ? AgentSystemUtils.getAgentRole(message.agentType);
      : null;
    return (
      <View;
        key={message.id}
        style={[
          styles.messageContainer,
          isUser ? styles.userMessage : styles.agentMessage;
        ]}
      >;
        {!isUser && agentRole && (;
          <Text style={styles.agentName}>{agentRole.name}</Text>;
        )};
        <Text;
          style={[;
            styles.messageText,isUser ? styles.userMessageText : styles.agentMessageText;
          ]};
        >;
          {message.content};
        </Text>;
        <Text style={styles.timestamp}>;
          {message.timestamp.toLocaleTimeString()};
        </Text>;
      </View>;
    );
  }, []);
  /**
  * 渲染智能体选择器
  */
  const renderAgentSelector = useCallback() => {const agents = [;
      AgentType.XIAOAI,AgentType.XIAOKE,AgentType.LAOKE,AgentType.SOER;
    ];
    return (;
      <ScrollView;
        horizontal;
        showsHorizontalScrollIndicator={false};
        style={styles.agentSelector};
      >;
        {agents.map(agent) => {const role = AgentSystemUtils.getAgentRole(agent);
          const isSelected = agent === currentAgent;
          return (
            <TouchableOpacity;
              key={agent};
              style={[;
                styles.agentButton,isSelected && styles.selectedAgentButton;
              ]};
              onPress={() => switchAgent(agent)};
            >;
              <Text;
                style={[;
                  styles.agentButtonText,isSelected && styles.selectedAgentButtonText;
                ]};
              >;
                {role.name};
              </Text>;
            </TouchableOpacity>;
          );
        })}
      </ScrollView>
    );
  }, [currentAgent, switchAgent]);
  return (;
    <Animated.View style={[styles.container, { opacity: fadeAnim }, style]}>;
      {// 智能体选择器};
      {renderAgentSelector()};
      {// 消息列表};
      <ScrollView;
        ref={scrollViewRef};
        style={styles.messagesContainer};
        onContentSizeChange={() =>;
          scrollViewRef.current?.scrollToEnd({ animated: true });
        }
      >
        {messages.map(renderMessage)}
        {isLoading && (
        <View style={styles.loadingContainer}>
            <ActivityIndicator size="small" color="#007AFF" />
            <Text style={styles.loadingText}>正在思考...</Text>
          </View>
        )}
      </ScrollView>
      {// 输入区域}
      <View style={styles.inputContainer}>
        <TextInput;
          style={styles.textInput}
          value={inputText}
          onChangeText={setInputText}
          placeholder="输入您的问题..."
          multiline;
          maxLength={500}
          editable={!isLoading}
        />
        <TouchableOpacity;
          style={[
            styles.sendButton,
            (!inputText.trim() || isLoading) && styles.disabledButton;
          ]}
          onPress={sendMessage}
          disabled={!inputText.trim() || isLoading}
        >
          <Text style={styles.sendButtonText}>发送</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.clearButton} onPress={clearMessages}>
          <Text style={styles.clearButtonText}>清空</Text>
        </TouchableOpacity>
      </View>
    </Animated.View>;
  );
};
const { width } = Dimensions.get("window");
const styles = StyleSheet.create({
  container: {,
  flex: 1,
    backgroundColor: "#f5f5f5"
  },
  agentSelector: {,
  backgroundColor: "#fff",
    paddingVertical: 10,
    paddingHorizontal: 15,
    borderBottomWidth: 1,
    borderBottomColor: "#e0e0e0"
  },
  agentButton: {,
  paddingHorizontal: 15,
    paddingVertical: 8,
    marginRight: 10,
    backgroundColor: "#f0f0f0",
    borderRadius: 20,
    borderWidth: 1,
    borderColor: "#d0d0d0"
  },
  selectedAgentButton: {,
  backgroundColor: "#007AFF",
    borderColor: "#007AFF"
  },
  agentButtonText: {,
  fontSize: 14,
    color: "#333",
    fontWeight: "500"
  },
  selectedAgentButtonText: {,
  color: "#fff"
  },
  messagesContainer: {,
  flex: 1,
    padding: 15;
  },
  messageContainer: {,
  marginBottom: 15,
    maxWidth: width * 0.8;
  },
  userMessage: {,
  alignSelf: "flex-end"
  },
  agentMessage: {,
  alignSelf: "flex-start"
  },
  agentName: {,
  fontSize: 12,
    color: "#666",
    marginBottom: 5,
    fontWeight: "600"
  },
  messageText: {,
  fontSize: 16,
    lineHeight: 22,
    padding: 12,
    borderRadius: 18;
  },
  userMessageText: {,
  backgroundColor: "#007AFF",
    color: "#fff"
  },
  agentMessageText: {,
  backgroundColor: "#fff",
    color: "#333",
    borderWidth: 1,
    borderColor: "#e0e0e0"
  },
  timestamp: {,
  fontSize: 11,
    color: "#999",
    marginTop: 5,
    textAlign: "center"
  },
  loadingContainer: {,
  flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    padding: 15;
  },
  loadingText: {,
  marginLeft: 10,
    fontSize: 14,
    color: "#666"
  },
  inputContainer: {,
  flexDirection: "row",
    padding: 15,
    backgroundColor: "#fff",
    borderTopWidth: 1,
    borderTopColor: "#e0e0e0",
    alignItems: "flex-end"
  },
  textInput: {,
  flex: 1,
    borderWidth: 1,
    borderColor: "#d0d0d0",
    borderRadius: 20,
    paddingHorizontal: 15,
    paddingVertical: 10,
    fontSize: 16,
    maxHeight: 100,
    marginRight: 10;
  },
  sendButton: {,
  backgroundColor: "#007AFF",
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 20,
    marginRight: 5;
  },
  disabledButton: {,
  backgroundColor: "#ccc"
  },
  sendButtonText: {
      color: "#fff",
      fontSize: 16,fontWeight: "600";
  },clearButton: {
      backgroundColor: "#ff3b30",
      paddingHorizontal: 15,paddingVertical: 12,borderRadius: 20;
  },clearButtonText: {
      color: "#fff",
      fontSize: 14,fontWeight: "600";
  };
});
export default AgentInterface;