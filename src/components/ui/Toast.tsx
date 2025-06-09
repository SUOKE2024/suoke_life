import React, { useEffect, useRef } from 'react';
import {
  Animated,
  Dimensions,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import { useTheme } from '../../contexts/ThemeContext';

const { width: screenWidth } = Dimensions.get('window');

export interface ToastProps {
  /** Toast内容 */
  message: string;
  /** Toast类型 */
  type?: 'info' | 'success' | 'warning' | 'error';
  /** 显示位置 */
  position?: 'top' | 'bottom';
  /** 自动关闭时间（毫秒） */
  duration?: number;
  /** 是否显示 */
  visible?: boolean;
  /** 关闭回调 */
  onClose?: () => void;
  /** 点击回调 */
  onPress?: () => void;
  /** 自定义图标 */
  icon?: React.ReactNode;
  /** 自定义样式 */
  style?: any;
  /** 文本样式 */
  textStyle?: any;
}

export const Toast: React.FC<ToastProps> = ({
  message,
  type = 'info',
  position = 'top',
  duration = 3000,
  visible = true,
  onClose,
  onPress,
  icon,
  style,
  textStyle,
}) => {
  const { currentTheme } = useTheme();
  const styles = createStyles(currentTheme, type, position);

  const translateY = useRef(
    new Animated.Value(position === 'top' ? -100 : 100)
  ).current;
  const opacity = useRef(new Animated.Value(0)).current;
  const timeoutRef = useRef<NodeJS.Timeout>();

  // 显示动画
  const showToast = () => {
    Animated.parallel([
      Animated.spring(translateY, {
        toValue: 0,
        useNativeDriver: true,
        tension: 100,
        friction: 8,
      }),
      Animated.timing(opacity, {
        toValue: 1,
        duration: 300,
        useNativeDriver: true,
      }),
    ]).start();
  };

  // 隐藏动画
  const hideToast = () => {
    Animated.parallel([
      Animated.timing(translateY, {
        toValue: position === 'top' ? -100 : 100,
        duration: 250,
        useNativeDriver: true,
      }),
      Animated.timing(opacity, {
        toValue: 0,
        duration: 250,
        useNativeDriver: true,
      }),
    ]).start() => {
      onClose?.();
    });
  };

  // 处理关闭
  const handleClose = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    hideToast();
  };

  // 获取类型图标
  const getTypeIcon = () => {
    if (icon) return icon;

    const iconMap = {
      info: 'ℹ️',
      success: '✅',
      warning: '⚠️',
      error: '❌',
    };

    return <Text style={styles.icon}>{iconMap[type]}</Text>;
  };

  useEffect() => {
    if (visible) {
      showToast();

      if (duration > 0) {
        timeoutRef.current = setTimeout() => {
          handleClose();
        }, duration);
      }
    } else {
      hideToast();
    }

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [visible, duration]);

  if (!visible) return null;

  return (
    <View style={styles.overlay}>
      <Animated.View;
        style={[
          styles.container,
          {
            opacity,
            transform: [{ translateY }],
          },
          style,
        ]}
      >
        <TouchableOpacity;
          style={styles.content}
          onPress={onPress}
          activeOpacity={onPress ? 0.8 : 1}
          disabled={!onPress}
        >
          {getTypeIcon()}
          <Text style={[styles.message, textStyle]} numberOfLines={3}>
            {message}
          </Text>
          <TouchableOpacity style={styles.closeButton} onPress={handleClose}>
            <Text style={styles.closeText}>×</Text>
          </TouchableOpacity>
        </TouchableOpacity>
      </Animated.View>
    </View>
  );
};

const createStyles = (theme: any, type: string, position: string) => {
  // 获取类型颜色
  const getTypeColors = () => {
    switch (type) {
      case 'success':
        return {
          background:
            theme.colors.successContainer || theme.colors.primaryContainer,
          border: theme.colors.success,
          text:
            theme.colors.onSuccessContainer || theme.colors.onPrimaryContainer,
        };
      case 'warning':
        return {
          background:
            theme.colors.warningContainer || theme.colors.primaryContainer,
          border: theme.colors.warning,
          text:
            theme.colors.onWarningContainer || theme.colors.onPrimaryContainer,
        };
      case 'error':
        return {
          background: theme.colors.errorContainer,
          border: theme.colors.error,
          text: theme.colors.onErrorContainer,
        };
      default:
        return {,
  background: theme.colors.surfaceVariant,
          border: theme.colors.primary,
          text: theme.colors.onSurfaceVariant,
        };
    }
  };

  const colors = getTypeColors();

  return StyleSheet.create({
    overlay: {,
  position: 'absolute',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      justifyContent: position === 'top' ? 'flex-start' : 'flex-end',
      alignItems: 'center',
      paddingTop: position === 'top' ? 50 : 0,
      paddingBottom: position === 'bottom' ? 50 : 0,
      paddingHorizontal: theme.spacing.md,
      pointerEvents: 'box-none',
      zIndex: 1000,
    },
    container: {,
  maxWidth: screenWidth - 32,
      backgroundColor: colors.background,
      borderRadius: theme.borderRadius.lg,
      borderLeftWidth: 4,
      borderLeftColor: colors.border,
      shadowColor: theme.colors.shadow,
      shadowOffset: {,
  width: 0,
        height: 4,
      },
      shadowOpacity: 0.15,
      shadowRadius: 8,
      elevation: 8,
    },
    content: {,
  flexDirection: 'row',
      alignItems: 'center',
      padding: theme.spacing.md,
    },
    icon: {,
  fontSize: 20,
      marginRight: theme.spacing.sm,
    },
    message: {,
  flex: 1,
      fontSize: theme.typography.fontSize.sm,
      color: colors.text,
      lineHeight: theme.typography.fontSize.sm * 1.4,
    },
    closeButton: {,
  padding: theme.spacing.xs,
      marginLeft: theme.spacing.sm,
    },
    closeText: {,
  fontSize: 18,
      color: colors.text,
      fontWeight: theme.typography.fontWeight.bold,
    },
  });
};

export default Toast;
