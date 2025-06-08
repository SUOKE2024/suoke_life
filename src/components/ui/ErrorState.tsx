import React from 'react';
import {
    Animated,
    StyleSheet,
    Text,
    TouchableOpacity,
    View
} from 'react-native';
import { useTheme } from '../../contexts/ThemeContext';
// import { Button } from './Button'; // 暂时注释掉，因为Button组件有语法错误

export interface ErrorStateProps {
  /** 错误类型 */
  type?: 'network' | 'server' | 'notFound' | 'permission' | 'generic';
  /** 错误标题 */
  title?: string;
  /** 错误描述 */
  message?: string;
  /** 是否显示重试按钮 */
  showRetry?: boolean;
  /** 重试按钮文本 */
  retryText?: string;
  /** 重试回调 */
  onRetry?: () => void;
  /** 自定义样式 */
  style?: any;
  /** 是否显示图标 */
  showIcon?: boolean;
  /** 自定义图标 */
  icon?: string;
  /** 额外操作按钮 */
  actions?: Array<{
    title: string;
    onPress: () => void;
    variant?: 'primary' | 'secondary' | 'outline';
  }>;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  type = 'generic',
  title,
  message,
  showRetry = true,
  retryText = '重试',
  onRetry,
  style,
  showIcon = true,
  icon,
  actions = [],
}) => {
  const { currentTheme } = useTheme();
  const styles = createStyles(currentTheme);

  const fadeAnim = React.useRef(new Animated.Value(0)).current;
  const scaleAnim = React.useRef(new Animated.Value(0.8)).current;

  React.useEffect(() => {
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 600,
        useNativeDriver: true,
      }),
      Animated.spring(scaleAnim, {
        toValue: 1,
        tension: 100,
        friction: 8,
        useNativeDriver: true,
      }),
    ]).start();
  }, [fadeAnim, scaleAnim]);

  const getErrorConfig = () => {
    switch (type) {
      case 'network':
        return {
          icon: icon || '📡',
          title: title || '网络连接失败',
          message: message || '请检查您的网络连接后重试',
          color: currentTheme.colors.warning,
        };
      case 'server':
        return {
          icon: icon || '🔧',
          title: title || '服务器错误',
          message: message || '服务器暂时无法响应，请稍后重试',
          color: currentTheme.colors.error,
        };
      case 'notFound':
        return {
          icon: icon || '🔍',
          title: title || '内容未找到',
          message: message || '您要查找的内容不存在或已被删除',
          color: currentTheme.colors.info,
        };
      case 'permission':
        return {
          icon: icon || '🔒',
          title: title || '权限不足',
          message: message || '您没有权限访问此内容',
          color: currentTheme.colors.warning,
        };
      default:
        return {
          icon: icon || '⚠️',
          title: title || '出现错误',
          message: message || '发生了未知错误，请重试',
          color: currentTheme.colors.error,
        };
    }
  };

  const errorConfig = getErrorConfig();

  const handleRetry = () => {
    // 添加重试动画
    Animated.sequence([
      Animated.timing(scaleAnim, {
        toValue: 0.95,
        duration: 100,
        useNativeDriver: true,
      }),
      Animated.timing(scaleAnim, {
        toValue: 1,
        duration: 100,
        useNativeDriver: true,
      }),
    ]).start();

    onRetry?.();
  };

  return (
    <Animated.View
      style={[
        styles.container,
        style,
        {
          opacity: fadeAnim,
          transform: [{ scale: scaleAnim }],
        },
      ]}
    >
      <View style={styles.content}>
        {showIcon && (
          <View style={[styles.iconContainer, { borderColor: errorConfig.color }]}>
            <Text style={styles.icon}>{errorConfig.icon}</Text>
          </View>
        )}

        <Text style={[styles.title, { color: errorConfig.color }]}>
          {errorConfig.title}
        </Text>

        <Text style={styles.message}>
          {errorConfig.message}
        </Text>

        <View style={styles.actionsContainer}>
          {showRetry && onRetry && (
            <TouchableOpacity
              onPress={handleRetry}
              style={[styles.retryButton, { backgroundColor: errorConfig.color }]}
            >
              <Text style={styles.buttonText}>{retryText}</Text>
            </TouchableOpacity>
          )}

          {actions.map((action, index) => (
            <TouchableOpacity
              key={index}
              onPress={action.onPress}
              style={styles.actionButton}
            >
              <Text style={styles.buttonText}>{action.title}</Text>
            </TouchableOpacity>
          ))}
        </View>
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
      maxWidth: 300,
    },
    iconContainer: {
      width: 80,
      height: 80,
      borderRadius: 40,
      borderWidth: 2,
      justifyContent: 'center',
      alignItems: 'center',
      marginBottom: theme.spacing.lg,
      backgroundColor: theme.colors.surface,
    },
    icon: {
      fontSize: 32,
    },
    title: {
      fontSize: theme.typography.fontSize.xl,
      fontWeight: theme.typography.fontWeight.bold,
      textAlign: 'center',
      marginBottom: theme.spacing.md,
    },
    message: {
      fontSize: theme.typography.fontSize.base,
      color: theme.colors.onSurfaceVariant,
      textAlign: 'center',
      lineHeight: 24,
      marginBottom: theme.spacing.xl,
    },
    actionsContainer: {
      width: '100%',
      gap: theme.spacing.md,
    },
    retryButton: {
      width: '100%',
      paddingVertical: theme.spacing.md,
      paddingHorizontal: theme.spacing.lg,
      borderRadius: theme.borderRadius.md,
      alignItems: 'center',
      justifyContent: 'center',
    },
    actionButton: {
      width: '100%',
      paddingVertical: theme.spacing.md,
      paddingHorizontal: theme.spacing.lg,
      borderRadius: theme.borderRadius.md,
      borderWidth: 1,
      borderColor: theme.colors.outline,
      alignItems: 'center',
      justifyContent: 'center',
    },
    buttonText: {
      fontSize: theme.typography.fontSize.base,
      fontWeight: theme.typography.fontWeight.medium,
      color: '#FFFFFF',
    },
  });
};

export default ErrorState; 