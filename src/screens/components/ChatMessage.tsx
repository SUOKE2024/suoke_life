import { colors, spacing, borderRadius, fonts } from '../../constants/theme';
import { AgentType, AGENTS } from './AgentCard';





import React, { memo } from 'react';
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ViewStyle,
} from 'react-native';

export interface Message {
  id: string;
  text: string;
  sender: 'user' | AgentType;
  timestamp: Date;
  type?: 'text' | 'image' | 'voice';
  status?: 'sending' | 'sent' | 'delivered' | 'read' | 'failed';
}

interface ChatMessageProps {
  message: Message;
  onPress?: (message: Message) => void;
  onLongPress?: (message: Message) => void;
  style?: ViewStyle;
  showTimestamp?: boolean;
  showAvatar?: boolean;
}

export const ChatMessage: React.FC<ChatMessageProps> = memo(({
  message,
  onPress,
  onLongPress,
  style,
  showTimestamp = true,
  showAvatar = true,
}) => {
  const isUser = message.sender === 'user';
  const agent = isUser ? null : AGENTS[message.sender as AgentType];

  const handlePress = useCallback( () => {, []);
    onPress?.(message);
  };

  const handleLongPress = useCallback( () => {, []);
    onLongPress?.(message);
  };

  const formatTimestamp = useCallback( (timestamp: Date) => {, []);
    return timestamp.toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getStatusIcon = useCallback( () => {, []);
    switch (message.status) {
      case 'sending':
        return '⏳';
      case 'sent':
        return '✓';
      case 'delivered':
        return '✓✓';
      case 'read':
        return '✓✓';
      case 'failed':
        return '❌';
      default:
        return '';
    }
  };

  return (
    <View
      style={[
        styles.container,
        isUser ? styles.userContainer : styles.agentContainer,
        style,
      ]}
    >
      {/* 智能体信息 */}
      {!isUser && showAvatar && (
        <View style={styles.agentInfo}>
          <View style={[styles.agentAvatar, { backgroundColor: agent?.color + '20' }]}>
            <Text style={styles.agentAvatarText}>{agent?.avatar}</Text>
          </View>
          <Text style={styles.agentName}>{agent?.name}</Text>
        </View>
      )}

      {/* 消息气泡 */}
      <TouchableOpacity
        style={[
          styles.messageBubble,
          isUser ? styles.userBubble : styles.agentBubble,
          !isUser && agent && { borderLeftColor: agent.color },
        ]}
        onPress={handlePress}
        onLongPress={handleLongPress}
        activeOpacity={0.8}
      >
        <Text
          style={[
            styles.messageText,
            isUser ? styles.userText : styles.agentText,
          ]}
        >
          {message.text}
        </Text>

        {/* 时间戳和状态 */}
        {showTimestamp && (
          <View style={styles.messageFooter}>
            <Text style={styles.timestamp}>
              {formatTimestamp(message.timestamp)}
            </Text>
            {isUser && message.status && (
              <Text style={[
                styles.statusIcon,
                message.status === 'read' && styles.readStatus,
                message.status === 'failed' && styles.failedStatus,
              ]}>
                {getStatusIcon()}
              </Text>
            )}
          </View>
        )}
      </TouchableOpacity>
    </View>
  );
});

ChatMessage.displayName = 'ChatMessage';

const styles = StyleSheet.create({
  container: {
    marginVertical: spacing.xs,
    paddingHorizontal: spacing.md,
  },
  userContainer: {
    alignItems: 'flex-end',
  },
  agentContainer: {
    alignItems: 'flex-start',
  },
  agentInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.xs,
    marginLeft: spacing.sm,
  },
  agentAvatar: {
    width: 24,
    height: 24,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.xs,
  },
  agentAvatarText: {
    fontSize: 12,
  },
  agentName: {
    fontSize: fonts.size.xs,
    color: colors.textSecondary,
    fontWeight: '500',
  },
  messageBubble: {
    maxWidth: '80%',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.lg,
    shadowColor: colors.black,
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  userBubble: {
    backgroundColor: colors.primary,
    borderBottomRightRadius: spacing.xs,
  },
  agentBubble: {
    backgroundColor: colors.surface,
    borderBottomLeftRadius: spacing.xs,
    borderLeftWidth: 3,
  },
  messageText: {
    fontSize: fonts.size.md,
    lineHeight: fonts.lineHeight.md,
  },
  userText: {
    color: colors.white,
  },
  agentText: {
    color: colors.text,
  },
  messageFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: spacing.xs,
  },
  timestamp: {
    fontSize: fonts.size.xs,
    color: colors.textSecondary,
    opacity: 0.8,
  },
  statusIcon: {
    fontSize: fonts.size.xs,
    color: colors.textSecondary,
    marginLeft: spacing.xs,
  },
  readStatus: {
    color: colors.primary,
  },
  failedStatus: {
    color: colors.error,
  },
}); 