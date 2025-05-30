import { colors, spacing, borderRadius, typography } from '../../constants/theme';

import React from 'react';
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ViewStyle,
} from 'react-native';

export type AgentType = 'xiaoai' | 'xiaoke' | 'laoke' | 'soer';

export interface AgentInfo {
  name: string;
  avatar: string;
  color: string;
  description: string;
  specialty?: string;
}

export const AGENTS: Record<AgentType, AgentInfo> = {
  xiaoai: {
    name: '小艾',
    avatar: '🤖',
    color: '#007AFF',
    description: '健康助手',
    specialty: 'AI健康分析与建议',
  },
  xiaoke: {
    name: '小克',
    avatar: '👨‍⚕️',
    color: '#34C759',
    description: '诊断专家',
    specialty: '中医五诊与现代诊断',
  },
  laoke: {
    name: '老克',
    avatar: '👴',
    color: '#FF9500',
    description: '中医大师',
    specialty: '传统中医理论与实践',
  },
  soer: {
    name: '索儿',
    avatar: '👧',
    color: '#FF2D92',
    description: '生活顾问',
    specialty: '健康生活方式指导',
  },
};

interface AgentCardProps {
  agent: AgentType;
  isSelected?: boolean;
  onPress?: (agent: AgentType) => void;
  style?: ViewStyle;
  showSpecialty?: boolean;
  size?: 'small' | 'medium' | 'large';
}

export const AgentCard: React.FC<AgentCardProps> = ({
  agent,
  isSelected = false,
  onPress,
  style,
  showSpecialty = false,
  size = 'medium',
}) => {
  const agentInfo = AGENTS[agent];
  
  const handlePress = useCallback( () => {, []);
    onPress?.(agent);
  };

  const sizeStyles = {
    small: styles.smallCard,
    medium: styles.mediumCard,
    large: styles.largeCard,
  };

  const avatarSizeStyles = {
    small: styles.smallAvatar,
    medium: styles.mediumAvatar,
    large: styles.largeAvatar,
  };

  const nameSizeStyles = {
    small: styles.smallName,
    medium: styles.mediumName,
    large: styles.largeName,
  };

  return (
    <TouchableOpacity
      style={[
        styles.container,
        sizeStyles[size],
        isSelected && styles.selectedContainer,
        { borderLeftColor: agentInfo.color },
        style,
      ]}
      onPress={handlePress}
      activeOpacity={0.7}
    >
      <View style={styles.content}>
        <View style={[styles.avatarContainer, avatarSizeStyles[size]]}>
          <Text style={[styles.avatar, avatarSizeStyles[size]]}>
            {agentInfo.avatar}
          </Text>
        </View>
        
        <View style={styles.info}>
          <Text style={[styles.name, nameSizeStyles[size]]}>
            {agentInfo.name}
          </Text>
          <Text style={styles.description}>
            {agentInfo.description}
          </Text>
          {showSpecialty && agentInfo.specialty && (
            <Text style={styles.specialty}>
              {agentInfo.specialty}
            </Text>
          )}
        </View>
      </View>
      
      {isSelected && (
        <View style={styles.selectedIndicator}>
          <Text style={styles.selectedText}>✓</Text>
        </View>
      )}
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.md,
    borderLeftWidth: 4,
    marginVertical: spacing.xs,
    shadowColor: colors.black,
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 3,
  },
  selectedContainer: {
    backgroundColor: colors.primaryLight + '10',
    borderColor: colors.primary,
    borderWidth: 2,
  },
  content: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing.md,
  },
  avatarContainer: {
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.background,
    borderRadius: borderRadius.full,
    marginRight: spacing.md,
  },
  avatar: {
    textAlign: 'center',
  },
  info: {
    flex: 1,
  },
  name: {
    fontWeight: 'bold',
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  description: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
  },
  specialty: {
    fontSize: typography.fontSize.xs,
    color: colors.textSecondary,
    fontStyle: 'italic',
  },
  selectedIndicator: {
    position: 'absolute',
    top: spacing.sm,
    right: spacing.sm,
    backgroundColor: colors.primary,
    borderRadius: borderRadius.full,
    width: 24,
    height: 24,
    justifyContent: 'center',
    alignItems: 'center',
  },
  selectedText: {
    color: colors.white,
    fontSize: typography.fontSize.sm,
    fontWeight: 'bold',
  },
  // Size variants
  smallCard: {
    padding: spacing.sm,
  },
  mediumCard: {
    padding: spacing.md,
  },
  largeCard: {
    padding: spacing.lg,
  },
  smallAvatar: {
    width: 32,
    height: 32,
    fontSize: 16,
  },
  mediumAvatar: {
    width: 48,
    height: 48,
    fontSize: 24,
  },
  largeAvatar: {
    width: 64,
    height: 64,
    fontSize: 32,
  },
  smallName: {
    fontSize: typography.fontSize.sm,
  },
  mediumName: {
    fontSize: typography.fontSize.base,
  },
  largeName: {
    fontSize: typography.fontSize.lg,
  },
}); 