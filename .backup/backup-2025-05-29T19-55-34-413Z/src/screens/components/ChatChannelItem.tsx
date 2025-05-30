import {
import { ChatChannel } from '../../types/chat';
import { colors, spacing, fonts, borderRadius } from '../../constants/theme';


import React, { memo } from 'react';
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Animated,
} from 'react-native';

interface ChatChannelItemProps {
  channel: ChatChannel;
  onPress: (channel: ChatChannel) => void;
  style?: any;
}

export const ChatChannelItem = memo<ChatChannelItemProps>(({ 
  channel, 
  onPress, 
  style, 
}) => {
  const getChannelColor = useCallback( () => {, []);
    switch (channel.type) {
      case 'agent':
        switch (channel.agentType) {
          case 'xiaoai': return '#007AFF';
          case 'xiaoke': return '#34C759';
          case 'laoke': return '#FF9500';
          case 'soer': return '#FF2D92';
          default: return colors.primary;
        }
      case 'doctor': return '#8E8E93';
      case 'group': return '#5856D6';
      case 'user': return '#6C6C70';
      default: return colors.primary;
    }
  };

  const getTypeLabel = useCallback( () => {, []);
    switch (channel.type) {
      case 'agent': return '智能体';
      case 'doctor': return '医生';
      case 'group': return '群组';
      case 'user': return '用户';
      default: return '';
    }
  };

  const handlePress = useCallback( () => {, []);
    onPress(channel);
  };

  return (
    <TouchableOpacity
      style={[styles.container, style]}
      onPress={handlePress}
      activeOpacity={0.7}
    >
      <View style={styles.avatarContainer}>
        <View style={[styles.avatar, { backgroundColor: getChannelColor() + '20' }]}>
          <Text style={styles.avatarText}>{channel.avatar}</Text>
        </View>
        {channel.isOnline && <View style={styles.onlineIndicator} />}
      </View>

      <View style={styles.content}>
        <View style={styles.header}>
          <View style={styles.nameContainer}>
            <Text style={styles.name} numberOfLines={1}>
              {channel.name}
            </Text>
            <View style={[styles.typeLabel, { backgroundColor: getChannelColor() }]}>
              <Text style={styles.typeLabelText}>{getTypeLabel()}</Text>
            </View>
          </View>
          <Text style={styles.time}>{channel.lastMessageTime}</Text>
        </View>

        <View style={styles.footer}>
          <Text style={styles.lastMessage} numberOfLines={2}>
            {channel.lastMessage}
          </Text>
          {channel.unreadCount > 0 && (
            <View style={styles.unreadBadge}>
              <Text style={styles.unreadText}>
                {channel.unreadCount > 99 ? '99+' : channel.unreadCount}
              </Text>
            </View>
          )}
        </View>

        {channel.specialization && (
          <Text style={[styles.specialization, { color: getChannelColor() }]} numberOfLines={1}>
            {channel.specialization}
          </Text>
        )}
      </View>
    </TouchableOpacity>
  );
});

ChatChannelItem.displayName = 'ChatChannelItem';

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    padding: spacing.md,
    backgroundColor: colors.background,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  avatarContainer: {
    position: 'relative',
    marginRight: spacing.md,
  },
  avatar: {
    width: 50,
    height: 50,
    borderRadius: 25,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: colors.border,
  },
  avatarText: {
    fontSize: 24,
  },
  onlineIndicator: {
    position: 'absolute',
    bottom: 2,
    right: 2,
    width: 12,
    height: 12,
    borderRadius: 6,
    backgroundColor: '#34C759',
    borderWidth: 2,
    borderColor: colors.background,
  },
  content: {
    flex: 1,
    justifyContent: 'center',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.xs,
  },
  nameContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  name: {
    fontSize: fonts.size.md,
    fontWeight: '600',
    color: colors.text,
    marginRight: spacing.sm,
  },
  typeLabel: {
    paddingHorizontal: spacing.xs,
    paddingVertical: 2,
    borderRadius: borderRadius.sm,
  },
  typeLabelText: {
    fontSize: fonts.size.xs,
    color: colors.white,
    fontWeight: '500',
  },
  time: {
    fontSize: fonts.size.xs,
    color: colors.textSecondary,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: spacing.xs,
  },
  lastMessage: {
    flex: 1,
    fontSize: fonts.size.sm,
    color: colors.textSecondary,
    lineHeight: fonts.lineHeight.sm,
    marginRight: spacing.sm,
  },
  unreadBadge: {
    backgroundColor: colors.primary,
    borderRadius: 10,
    minWidth: 20,
    height: 20,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: spacing.xs,
  },
  unreadText: {
    color: colors.white,
    fontSize: fonts.size.xs,
    fontWeight: 'bold',
  },
  specialization: {
    fontSize: fonts.size.xs,
    fontStyle: 'italic',
    fontWeight: '500',
  },
}); 