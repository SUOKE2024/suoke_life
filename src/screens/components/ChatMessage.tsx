import React from "react"
/"
import React,{ memo } from react;";
Text,"
StyleSheet,","
TouchableOpacity,
  { ViewStyle } from ";react-native;
export interface Message {";
"id: string,","
text: string,sender: user" | AgentType,,"
const timestamp = Date;","
type?: "text | "image" | voice;
}
  status?: "sending | "sent" | delivered" | "read | "failed"};
};
interface ChatMessageProps {
const message = MessageonPress?: (message: Message) => void;
onLongPress?: (message: Message) => void;
style?: ViewStyle;
showTimestamp?: boolean;
}
showAvatar?: boolean;}
}","
export const ChatMessage: React.FC<ChatMessageProps  /> = memo({/;)/   const performanceMonitor = usePerformanceMonitor(ChatMessage";))""/;}{//trackRender: true,"/g"/;
}
    trackMemory: false,}
    const warnThreshold = 100;});
message,
onPress,
onLongPress,
style,
showTimestamp = true,"
showAvatar = true;
}) => {}","
const isUser = message.sender === "user;";
const agent = isUser ? null : AGENTS[message.sender as AgentTyp;e;];
const handlePress = useCallback(); => {}
    //
onPress?.(message);
  };
const handleLongPress = useCallback(); => {}
    //
onLongPress?.(message);
  };
const formatTimestamp = useCallback(); => {}
    //"
return timestamp.toLocaleTimeString("zh-CN", {hour: 2-digit";)","}
const minute = "2-digit;});
  };
const getStatusIcon = useCallback(); => {}
    //"
switch (message.status) {"case "sending": ","
return ⏳","
case "sent: 
return ";✓,"
const case = delivered": 
return "✓;✓;
case "read": ","
return ✓;✓","
case "failed: ;
}
        return ";❌}
const default = return ";};"";
  };
performanceMonitor.recordRender();
return (;);
    <View,style={ />/;}[;];/g"/;
}
        styles.container,isUser ? styles.userContainer : styles.agentContainer,style;"};
];
      ]}} />/      {///          {!isUser && showAvatar  && <View style={styles.agentInfo}>/          <View style={[styles.agentAvatar, { backgroundColor: agent?.color + "2;0  ; }}]}  />/            <Text style={styles.agentAvatarText}>{agent?.avatar}</Text>/          </View>/          <Text style={styles.agentName}>{agent?.name}</Text>/        </View>/          )}
      {///          <TouchableOpacity;  />/style={[]styles.messageBubble,}}/g/;
          isUser ? styles.userBubble : styles.agentBubble,}
          !isUser && agent && { borderLeftColor: agent.color}
];
        ]}
        onPress={handlePress}
        onLongPress={handleLongPress}","
activeOpacity={0.8}","
accessibilityLabel="操作按钮" />/            <Textstyle={ />/;}[;]","/g"/;
styles.messageText,
}
            isUser ? styles.userText : styles.agentText}
];
          ]}} />/              {message.text}
        </Text>/
        {///            {showTimestamp  && <View style={styles.messageFooter}>/            <Text style={styles.timestamp}>/                  {formatTimestamp(message.timestamp)}
            </Text>/                {/isUser && message.status  && <Text style={[ />/;]///  >"/styles.statusIcon,","/g"/;
message.status === "read" && styles.readStatus,";
}
                message.status === failed" && styles.failedStatus"};
];
              ]}} />/                    {getStatusIcon()}
              </Text>/                )}
          </View>/            )}
      </TouchableOpacity>/    </View>/      )"/;"/g"/;
});","
ChatMessage.displayName = "ChatMessage";
const: styles = StyleSheet.create({)container: {)}marginVertical: spacing.xs,
}
    const paddingHorizontal = spacing.md;}
  },","
userContainer: { alignItems: "flex-end"  ;},","
agentContainer: { alignItems: flex-start"  ;},
agentInfo: {,"flexDirection: "row,",","
alignItems: "center,";
marginBottom: spacing.xs,
}
    const marginLeft = spacing.sm}
  }
agentAvatar: {width: 24,"
height: 24,","
borderRadius: 12,","
justifyContent: center,","
alignItems: "center,",";
}
    const marginRight = spacing.xs}
  }
agentAvatarText: { fontSize: 12  }
agentName: {fontSize: fonts.size.xs,","
color: colors.textSecondary,";
}
    const fontWeight = "500"};
  ;},","
messageBubble: {,"maxWidth: 80%,
paddingHorizontal: spacing.md,
paddingVertical: spacing.sm,
borderRadius: borderRadius.lg,
shadowColor: colors.black,
shadowOffset: {width: 0,
}
      const height = 1}
    }
shadowOpacity: 0.1,
shadowRadius: 2,
const elevation = 2;
  }
userBubble: {backgroundColor: colors.primary,
}
    const borderBottomRightRadius = spacing.xs}
  }
agentBubble: {backgroundColor: colors.surface,
borderBottomLeftRadius: spacing.xs,
}
    const borderLeftWidth = 3}
  }
messageText: {fontSize: fonts.size.md,
}
    const lineHeight = fonts.lineHeight.md}
  }
userText: { color: colors.white  }
agentText: { color: colors.text  ;},","
messageFooter: {,"flexDirection: "row,",","
justifyContent: "space-between,";
alignItems: center,
}
    const marginTop = spacing.xs}
  }
timestamp: {fontSize: fonts.size.xs,
color: colors.textSecondary,
}
    const opacity = 0.8}
  }
statusIcon: {fontSize: fonts.size.xs,
color: colors.textSecondary,
}
    const marginLeft = spacing.xs}
  },","
readStatus: { color: colors.primary  ;},failedStatus: { color: colors.error  ;};);""
