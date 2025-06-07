import { usePerformanceMonitor } from "../hooks/usePerformanceMonitor/      View,";
import React from "react";
importIcon from "../../components/common/Icon/import { colors, spacing, borderRadius, fonts  } from "../../placeholder";../../constants/theme";// import React,{ useState, useRef } from react""
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  ViewStyle,
  KeyboardAvoidingView,
  { Platform } from ";react-native";
interface MessageInputProps {
  onSend: (message: string) => void;
  placeholder?: string;
  disabled?: boolean;
  style?: ViewStyle;
  maxLength?: number;
  multiline?: boolean;
  showVoiceButton?: boolean;
  showAttachButton?: boolean;
  onVoicePress?: () => void;
  onAttachPress?: () => void;
isTyping?: boolean
}
export const MessageInput: React.FC<MessageInputProps /> = ({/   const performanceMonitor = usePerformanceMonitor(MessageInput",;
{/
    trackRender: true,
    trackMemory: false,
    warnThreshold: 100,  });
  onSend,
  placeholder = "输入消息...,"
  disabled = false,
  style,
  maxLength = 1000,
  multiline = true,
  showVoiceButton = true,
  showAttachButton = true,
  onVoicePress,
  onAttachPress,
  isTyping = false;
}) => {}
  const [message, setMessage] = useState<string>(");
  const [inputHeight, setInputHeight] = useState<number>(4;0;);
  const inputRef = useRef<TextInput />(nul;l;);// const handleSend = useCallback(); => {}
    //
    if (message.trim(); && !disabled) {
      onSend(message.trim(););
      setMessage(");"
      setInputHeight(40);
    }
  };
  const handleContentSizeChange = useCallback(); => {}
    //
    if (multiline) {
      const { height   } = event.nativeEvent.contentSi;z;e;
      setInputHeight(Math.min(Math.max(40, height), 120));
    }
  };
  const canSend = message.trim().length > 0 && !disabl;e;d;
  performanceMonitor.recordRender();
  return (;
    <KeyboardAvoidingView,behavior={Platform.OS === "ios ? "padding" : height"};
      style={[styles.container, style]} />/          {isTyping && (;
        <View style={styles.typingIndicator}>/          <Text style={styles.typingText}>智能体正在输入...</Text>/          <View style={styles.typingDots}>/            <View style={[styles.dot, styles.dot1]} />/            <View style={[styles.dot, styles.dot2]} />/            <View style={[styles.dot, styles.dot3]} />/          </View>/        </View>/          )};
      <View style={styles.inputContainer}>/        {///            {showAttachButton && (;
          <TouchableOpacity;
style={styles.actionButton}
            onPress={onAttachPress};
            disabled={disabled}
          accessibilityLabel="TODO: 添加无障碍标签" />/                <Ic;o;nname="attachment"
              size={24}
              color={disabled ? colors.disabled: colors.textSecondary} />/          </TouchableOpacity>/            )}
        {///              <TextInput;
ref={inputRef}
            style={[
              styles.textInput,
              multiline && { height: inputHeight},
              disabled && styles.disabledInput;
            ]}
            value={message}
            onChangeText={setMessage}
            placeholder={placeholder}
            placeholderTextColor={colors.placeholder}
            multiline={multiline}
            maxLength={maxLength}
            editable={!disabled}
            onContentSizeChange={handleContentSizeChange}
            textAlignVertical="top"
          />/
          {//
            <Text style={styles.charCount}>/              {message.length}/{maxLength}/            </Text>/              )}
        </View>/
        {///            {showVoiceButton && !canSend && (
          <TouchableOpacity;
style={styles.actionButton}
            onPress={onVoicePress}
            disabled={disabled}
          accessibilityLabel="TODO: 添加无障碍标签" />/                <Iconname="microphone"
              size={24}
              color={disabled ? colors.disabled: colors.primary} />/          </TouchableOpacity>/            )}
        {///            {canSend && (
          <TouchableOpacity;
style={[
              styles.sendButton,
              !canSend && styles.disabledSendButton;
            ]}
            onPress={handleSend}
            disabled={!canSend}
          accessibilityLabel="TODO: 添加无障碍标签" />/                <Iconname="send"
              size={20}
              color={colors.white} />/          </TouchableOpacity>/            )}
      </View>/    </KeyboardAvoidingView>/      );
}
const styles = StyleSheet.create({container: {,
  backgroundColor: colors.surface,
    borderTopWidth: 1,
    borderTopColor: colors.border;
  },
  typingIndicator: {,
  flexDirection: "row,",
    alignItems: "center",
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    backgroundColor: colors.background;
  },
  typingText: {,
  fontSize: fonts.size.sm,
    color: colors.textSecondary,
    marginRight: spacing.sm;
  },
  typingDots: { flexDirection: row"  },"
  dot: {,
  width: 4,
    height: 4,
    borderRadius: 2,
    backgroundColor: colors.textSecondary,
    marginHorizontal: 1;
  },
  dot1: { opacity: 0.4  },
  dot2: { opacity: 0.7  },
  dot3: { opacity: 1  },
  inputContainer: {,
  flexDirection: "row,",
    alignItems: "flex-end",
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    minHeight: 56;
  },
  actionButton: {,
  width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: center",
    alignItems: "center,",
    marginHorizontal: spacing.xs;
  },
  inputWrapper: {,
  flex: 1,
    backgroundColor: colors.background,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    marginHorizontal: spacing.xs,
    position: "relative"
  },
  textInput: {,
  fontSize: fonts.size.md,
    color: colors.text,
    lineHeight: fonts.lineHeight.md,
    minHeight: 40,
    maxHeight: 120;
  },
  disabledInput: {,
  color: colors.disabled,
    backgroundColor: colors.disabled + 20""
  },
  charCount: {,
  position: "absolute,",
    bottom: spacing.xs,
    right: spacing.xs,
    fontSize: fonts.size.xs,
    color: colors.textSecondary;
  },
  sendButton: {,
  width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.primary,
    justifyContent: "center",
    alignItems: center",
    marginLeft: spacing.xs,
    shadowColor: colors.primary,
    shadowOffset: {,
  width: 0,
      height: 2;
    },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 4;
  },
  disabledSendButton: {,
  backgroundColor: colors.disabled,
    shadowOpacity: 0,elevation: 0};};);
