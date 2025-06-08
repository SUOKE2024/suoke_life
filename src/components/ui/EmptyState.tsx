import React from 'react';
import {
    Animated,
    StyleSheet,
    Text,
    View,
} from 'react-native';
import { useTheme } from '../../contexts/ThemeContext';

export interface EmptyStateProps {
  /** 空状态类型 */
  type?: 'noData' | 'noResults' | 'noConnection' | 'noContent' | 'custom';
  /** 标题 */
  title?: string;
  /** 描述 */
  description?: string;
  /** 图标 */
  icon?: string;
  /** 自定义样式 */
  style?: any;
  /** 是否显示动画 */
  animated?: boolean;
  /** 子组件（如操作按钮） */
  children?: React.ReactNode;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  type = 'noData',
  title,
  description,
  icon,
  style,
  animated = true,
  children,
}) => {
  const { currentTheme } = useTheme();
  const styles = createStyles(currentTheme);

  const fadeAnim = React.useRef(new Animated.Value(0)).current;
  const translateYAnim = React.useRef(new Animated.Value(20)).current;

  React.useEffect(() => {
    if (animated) {
      Animated.parallel([
        Animated.timing(fadeAnim, {
          toValue: 1,
          duration: 800,
          useNativeDriver: true,
        }),
        Animated.timing(translateYAnim, {
          toValue: 0,
          duration: 600,
          useNativeDriver: true,
        }),
      ]).start();
    }
  }, [animated, fadeAnim, translateYAnim]);

  const getEmptyConfig = () => {
    switch (type) {
      case 'noData':
        return {
          icon: icon || '📊',
          title: title || '暂无数据',
          description: description || '当前没有可显示的数据',
        };
      case 'noResults':
        return {
          icon: icon || '🔍',
          title: title || '无搜索结果',
          description: description || '没有找到符合条件的结果，请尝试其他关键词',
        };
      case 'noConnection':
        return {
          icon: icon || '📡',
          title: title || '网络连接失败',
          description: description || '请检查网络连接后重试',
        };
      case 'noContent':
        return {
          icon: icon || '📝',
          title: title || '暂无内容',
          description: description || '这里还没有任何内容',
        };
      default:
        return {
          icon: icon || '🤔',
          title: title || '空空如也',
          description: description || '这里什么都没有',
        };
    }
  };

  const emptyConfig = getEmptyConfig();

  const containerStyle = animated
    ? [
        styles.container,
        style,
        {
          opacity: fadeAnim,
          transform: [{ translateY: translateYAnim }],
        },
      ]
    : [styles.container, style];

  return (
    <Animated.View style={containerStyle}>
      <View style={styles.content}>
        <View style={styles.iconContainer}>
          <Text style={styles.icon}>{emptyConfig.icon}</Text>
        </View>

        <Text style={styles.title}>{emptyConfig.title}</Text>

        <Text style={styles.description}>{emptyConfig.description}</Text>

        {children && <View style={styles.actionsContainer}>{children}</View>}
      </View>
    </Animated.View>
  );
};

const createStyles = (theme: any) => {
  return StyleSheet.create({
    container: {
      flex: 1,
      justifyContent: 'center',
      alignItems: 'center',
      padding: theme.spacing.xl,
    },
    content: {
      alignItems: 'center',
      maxWidth: 280,
    },
    iconContainer: {
      width: 100,
      height: 100,
      borderRadius: 50,
      backgroundColor: theme.colors.surfaceVariant,
      justifyContent: 'center',
      alignItems: 'center',
      marginBottom: theme.spacing.lg,
    },
    icon: {
      fontSize: 48,
    },
    title: {
      fontSize: theme.typography.fontSize.lg,
      fontWeight: theme.typography.fontWeight.semibold,
      color: theme.colors.onSurface,
      textAlign: 'center',
      marginBottom: theme.spacing.md,
    },
    description: {
      fontSize: theme.typography.fontSize.base,
      color: theme.colors.onSurfaceVariant,
      textAlign: 'center',
      lineHeight: 22,
      marginBottom: theme.spacing.lg,
    },
    actionsContainer: {
      width: '100%',
      alignItems: 'center',
    },
  });
};

export default EmptyState; 