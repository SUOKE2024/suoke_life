
import React, { useState, useEffect, useCallback, useRef } from "react";";
View,;
Text,;
TextInput,;
TouchableOpacity,;
ScrollView,;
StyleSheet,;
Alert,;
ActivityIndicator,;
Animated,";,"";
Dimensions;";"";
} from "react-native";"";"";
/* 性 *//;/g/;
*//;,/g/;
interface AgentInterfaceProps {agentType?: AgentType;,}currentChannel?: string;
const userId = string;
onResponse?: (response: AgentResponse) => void;
onError?: (error: Error) => void;
}
}
  style?: any;}
}
/* 型 *//;/g/;
*//;,/g/;
interface Message {";,}id: string,";,"";
type: "user" | "agent";",";
content: string,;
const timestamp = Date;
agentType?: AgentType;
}
}
  metadata?: any;}
}
/* 面 *//;/g/;
*//;,/g/;
export const AgentInterface: React.FC<AgentInterfaceProps> = ({)";,}agentType,";,"";
currentChannel = 'chat','';
userId,;
onResponse,);
onError,);
}
  style;)}
}) => {';,}const [messages, setMessages] = useState<Message[]>([]);";,"";
const [inputText, setInputText] = useState(");";
const [isLoading, setIsLoading] = useState(false);
const [currentAgent, setCurrentAgent] = useState<AgentType>(;);
agentType || AgentSystemUtils.getAgentByChannel(currentChannel);
}
  );}
  const [sessionId] = useState(`session_${Date.now()}`);````;,```;
const scrollViewRef = useRef<ScrollView>(null);
const fadeAnim = useRef(new Animated.Value(0)).current;
useEffect() => {// 组件挂载时的淡入动画/;,}Animated.timing(fadeAnim, {)      toValue: 1,);,}duration: 500,);/g/;
}
      const useNativeDriver = true;)}
    }).start();
    // 添加欢迎消息/;,/g/;
addWelcomeMessage();
  }, []);
useEffect() => {// 当频道改变时更新智能体/;,}if (!agentType) {const newAgent = AgentSystemUtils.getAgentByChannel(currentChannel);}}/g/;
      setCurrentAgent(newAgent);}
    }
  }, [currentChannel, agentType]);
  /* 息 *//;/g/;
  *//;,/g/;
const addWelcomeMessage = useCallback() => {const agentRole = AgentSystemUtils.getAgentRole(currentAgent);}}
    const: welcomeMessage: Message = {,}";,"";
id: `welcome_${Date.now();}`,``"`;,```;
type: "agent";",";
timestamp: new Date(),;
const agentType = currentAgent;
    };
setMessages([welcomeMessage]);
  }, [currentAgent]);
  /* 息 *//;/g/;
  *//;,/g/;
const sendMessage = useCallback(async () => {if (!inputText.trim() || isLoading) {return;});
const: userMessage: Message = {,}";,"";
id: `user_${Date.now();}`,``"`;,```;
type: "user";",";
content: inputText.trim(),;
const timestamp = new Date();
    };";,"";
setMessages(prev) => [...prev, userMessage]);";,"";
setInputText(");";
setIsLoading(true);
try {const  context: AgentContext = {}        userId,;
sessionId,;
currentChannel,;
timestamp: new Date(),;
}
        previousMessages: messages.slice(-5), // 最近5条消息作为上下文}/;/g/;
      ;};
response: await executeAgentTask(inputText.trim(), context);
const: agentMessage: Message = {,}";,"";
id: `agent_${Date.now();}`,``"`;,```;
type: "agent";",";
content: response.response,;
timestamp: new Date(),;
agentType: currentAgent,;
const metadata = response.metadata;
      };
setMessages(prev) => [...prev, agentMessage]);
if (onResponse) {}}
        onResponse(response);}
      }
    } catch (error) {}}
      const: errorMessage: Message = {,}";,"";
id: `error_${Date.now();}`,``"`;,```;
type: "agent";",";
timestamp: new Date(),;
const agentType = currentAgent;
      };
setMessages(prev) => [...prev, errorMessage]);
if (onError) {}}
        onError(error as Error);}
      }
    } finally {}}
      setIsLoading(false);}
    }
  }, [;,]inputText,;
isLoading,;
userId,;
sessionId,;
currentChannel,;
messages,;
currentAgent,;
onResponse,;
onError;
];
  ]);
  /* 体 *//;/g/;
  *//;,/g/;
const switchAgent = useCallback(newAgentType: AgentType) => {setCurrentAgent(newAgentType);,}const agentRole = AgentSystemUtils.getAgentRole(newAgentType);
}
    const: switchMessage: Message = {,}";,"";
id: `switch_${Date.now();}`,``"`;,```;
type: "agent";",";
timestamp: new Date(),;
const agentType = newAgentType;
    };
setMessages(prev) => [...prev, switchMessage]);
  }, []);
  /* 话 *//;/g/;
  *//;/g/;

      {";}}"";
"}";
style: "cancel" ;},{";,}onPress: () => {setMessages([]);}}"";
          addWelcomeMessage();}
        }
      }
    ]);
  }, [addWelcomeMessage]);
  /* " *//;"/g"/;
  */"/;,"/g"/;
const renderMessage = useCallback(message: Message) => {const isUser = message.type === "user";";,}const agentRole = message.agentType;"";
      ? AgentSystemUtils.getAgentRole(message.agentType);
      : null;
}
    return (<View;}  />/;,)key={message.id}/g/;
        style={[;,]styles.messageContainer,;}}
          isUser ? styles.userMessage : styles.agentMessage;)}
];
        ]}});
      >;);
        {!isUser && agentRole && (;)}
          <Text style={styles.agentName}>{agentRole.name}</Text>;/;/g/;
        )};
        <Text;  />/;,/g/;
style={[;];}}
            styles.messageText,isUser ? styles.userMessageText : styles.agentMessageText;}
];
          ]}};
        >;
          {message.content};
        </Text>;/;/g/;
        <Text style={styles.timestamp}>;
          {message.timestamp.toLocaleTimeString()};
        </Text>;/;/g/;
      </View>;/;/g/;
    );
  }, []);
  /* 器 *//;/g/;
  *//;,/g/;
const renderAgentSelector = useCallback() => {const agents = [;];,}AgentType.XIAOAI,AgentType.XIAOKE,AgentType.LAOKE,AgentType.SOER;
];
    ];
return (;);
      <ScrollView;  />/;/g/;
}
        horizontal;}
        showsHorizontalScrollIndicator={false};
style={styles.agentSelector};
      >;
        {agents.map(agent) => {const role = AgentSystemUtils.getAgentRole(agent);,}const isSelected = agent === currentAgent;
}
          return (<TouchableOpacity;}  />/;,)key={agent};,/g/;
style={[;];);}}
                styles.agentButton,isSelected && styles.selectedAgentButton;)}
];
              ]}};);
onPress={() => switchAgent(agent)};
            >;
              <Text;  />/;,/g/;
style={[;];}}
                  styles.agentButtonText,isSelected && styles.selectedAgentButtonText;}
];
                ]}};
              >;
                {role.name};
              </Text>;/;/g/;
            </TouchableOpacity>;/;/g/;
          );
        })}
      </ScrollView>/;/g/;
    );
  }, [currentAgent, switchAgent]);
return (;);
    <Animated.View style={[styles.container, { opacity: fadeAnim ;}}, style]}>;
      {// 智能体选择器};/;/g/;
      {renderAgentSelector()};
      {// 消息列表};/;/g/;
      <ScrollView;  />/;,/g/;
ref={scrollViewRef};
style={styles.messagesContainer};
onContentSizeChange={() =>;}
          scrollViewRef.current?.scrollToEnd({ animated: true ;});
        }
      >;
        {messages.map(renderMessage)}";"";
        {isLoading  && <View style={styles.loadingContainer}>";"";
            <ActivityIndicator size="small" color="#007AFF"  />"/;"/g"/;
            <Text style={styles.loadingText}>正在思考...</Text>/;/g/;
          </View>/;/g/;
        )}
      </ScrollView>/;/g/;
      {// 输入区域}/;/g/;
      <View style={styles.inputContainer}>;
        <TextInput;  />/;,/g/;
style={styles.textInput}
          value={inputText}
          onChangeText={setInputText}

          multiline;
maxLength={500}
          editable={!isLoading}
        />/;/g/;
        <TouchableOpacity;  />/;,/g/;
style={[;,]styles.sendButton,;}}
            (!inputText.trim() || isLoading) && styles.disabledButton;}
];
          ]}}
          onPress={sendMessage}
          disabled={!inputText.trim() || isLoading}
        >;
          <Text style={styles.sendButtonText}>发送</Text>/;/g/;
        </TouchableOpacity>/;/g/;
        <TouchableOpacity style={styles.clearButton} onPress={clearMessages}>;
          <Text style={styles.clearButtonText}>清空</Text>/;/g/;
        </TouchableOpacity>/;/g/;
      </View>/;/g/;
    </Animated.View>;/;/g/;
  );";"";
};";,"";
const { width } = Dimensions.get("window");";,"";
const  styles = StyleSheet.create({)container: {,";,}flex: 1,";"";
}
    const backgroundColor = "#f5f5f5"}"";"";
  ;},";,"";
agentSelector: {,";,}backgroundColor: "#fff";",";
paddingVertical: 10,;
paddingHorizontal: 15,";,"";
borderBottomWidth: 1,";"";
}
    const borderBottomColor = "#e0e0e0"}"";"";
  ;}
agentButton: {paddingHorizontal: 15,;
paddingVertical: 8,";,"";
marginRight: 10,";,"";
backgroundColor: "#f0f0f0";",";
borderRadius: 20,";,"";
borderWidth: 1,";"";
}
    const borderColor = "#d0d0d0"}"";"";
  ;},";,"";
selectedAgentButton: {,";,}backgroundColor: "#007AFF";","";"";
}
    const borderColor = "#007AFF"}"";"";
  ;}
agentButtonText: {,";,}fontSize: 14,";,"";
color: "#333";","";"";
}
    const fontWeight = "500"}"";"";
  ;},";,"";
selectedAgentButtonText: {,";}}"";
  const color = "#fff"}"";"";
  ;}
messagesContainer: {flex: 1,;
}
    const padding = 15;}
  }
messageContainer: {marginBottom: 15,;
}
    const maxWidth = width * 0.8;}
  },";,"";
userMessage: {,";}}"";
  const alignSelf = "flex-end"}"";"";
  ;},";,"";
agentMessage: {,";}}"";
  const alignSelf = "flex-start"}"";"";
  ;}
agentName: {,";,}fontSize: 12,";,"";
color: "#666";",";
marginBottom: 5,";"";
}
    const fontWeight = "600"}"";"";
  ;}
messageText: {fontSize: 16,;
lineHeight: 22,;
padding: 12,;
}
    const borderRadius = 18;}
  },";,"";
userMessageText: {,";,}backgroundColor: "#007AFF";","";"";
}
    const color = "#fff"}"";"";
  ;},";,"";
agentMessageText: {,";,}backgroundColor: "#fff";",";
color: "#333";",";
borderWidth: 1,";"";
}
    const borderColor = "#e0e0e0"}"";"";
  ;}
timestamp: {,";,}fontSize: 11,";,"";
color: "#999";",";
marginTop: 5,";"";
}
    const textAlign = "center"}"";"";
  ;},";,"";
loadingContainer: {,";,}flexDirection: "row";",";
alignItems: "center";",";
justifyContent: "center";","";"";
}
    const padding = 15;}
  }
loadingText: {marginLeft: 10,";,"";
fontSize: 14,";"";
}
    const color = "#666"}"";"";
  ;},";,"";
inputContainer: {,";,}flexDirection: "row";",";
padding: 15,";,"";
backgroundColor: "#fff";",";
borderTopWidth: 1,";,"";
borderTopColor: "#e0e0e0";","";"";
}
    const alignItems = "flex-end"}"";"";
  ;}
textInput: {flex: 1,";,"";
borderWidth: 1,";,"";
borderColor: "#d0d0d0";",";
borderRadius: 20,;
paddingHorizontal: 15,;
paddingVertical: 10,;
fontSize: 16,;
maxHeight: 100,;
}
    const marginRight = 10;}
  },";,"";
sendButton: {,";,}backgroundColor: "#007AFF";",";
paddingHorizontal: 20,;
paddingVertical: 12,;
borderRadius: 20,;
}
    const marginRight = 5;}
  },";,"";
disabledButton: {,";}}"";
  const backgroundColor = "#ccc"}"";"";
  ;},";,"";
sendButtonText: {,";,}color: "#fff";","";"";
}
      fontSize: 16,fontWeight: "600";"}"";"";
  },clearButton: {,";,}backgroundColor: "#ff3b30";","";"";
}
      paddingHorizontal: 15,paddingVertical: 12,borderRadius: 20;}";"";
  },clearButtonText: {,";,}color: "#fff";",")";"";
}
      fontSize: 14,fontWeight: "600";")}"";"";
  };);
});";,"";
export default AgentInterface;""";