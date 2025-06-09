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

export interface NotificationProps {
  /** 通知ID */
  id?: string;
  /** 通知标题 */
  title?: string;
  /** 通知内容 */
  message: string;
  /** 通知类型 */
  type?: 'info' | 'success' | 'warning' | 'error';
  /** 显示位置 */
  position?: 'top' | 'bottom' | 'center';
  /** 自动关闭时间（毫秒，0表示不自动关闭） */
  duration?: number;
  /** 是否可关闭 */
  closable?: boolean;
  /** 关闭回调 */
  onClose?: () => void;
  /** 点击回调 */
  onPress?: () => void;
  /** 自定义图标 */
  icon?: React.ReactNode;
  /** 自定义操作按钮 */
  actions?: Array<{
    label: string;,
  onPress: () => void;
    style?: 'primary' | 'secondary';
  }>;
  /** 自定义样式 */
  style?: any;
  /** 标题样式 */
  titleStyle?: any;
  /** 消息样式 */
  messageStyle?: any;
  /** 是否显示 */
  visible?: boolean;
  /** 动画类型 */
  animationType?: 'slide' | 'fade' | 'scale';
  /** 背景模糊 */
  backdrop?: boolean;
  /** 最大宽度 */
  maxWidth?: number;
}

export const Notification: React.FC<NotificationProps> = ({
  id,
  title,
  message,
  type = 'info',
  position = 'top',
  duration = 4000,
  closable = true,
  onClose,
  onPress,
  icon,
  actions,
  style,
  titleStyle,
  messageStyle,
  visible = true,
  animationType = 'slide',
  backdrop = false,
  maxWidth = screenWidth - 32,
}) => {
  const { currentTheme } = useTheme();
  const styles = createStyles(currentTheme, type, position);

  const translateY = useRef(new Animated.Value(getInitialTranslateY())).current;
  const opacity = useRef(new Animated.Value(0)).current;
  const scale = useRef(new Animated.Value(0.8)).current;

  const timeoutRef = useRef<NodeJS.Timeout>();

  function getInitialTranslateY() {
    switch (position) {
      case 'top':
        return -100;
      case 'bottom':
        return 100;
      default:
        return 0;
    }
  }

  // 显示动画
  const showNotification = () => {
    const animations = [];

    if (animationType === 'slide') {
      animations.push(
        Animated.spring(translateY, {
          toValue: 0,
          useNativeDriver: true,
          tension: 100,
          friction: 8,
        })
      );
    }

    if (animationType === 'fade' || animationType === 'scale') {
      animations.push(
        Animated.timing(opacity, {
          toValue: 1,
          duration: 300,
          useNativeDriver: true,
        })
      );
    }

    if (animationType === 'scale') {
      animations.push(
        Animated.spring(scale, {
          toValue: 1,
          useNativeDriver: true,
          tension: 100,
          friction: 8,
        })
      );
    }

    Animated.parallel(animations).start();
  };

  // 隐藏动画
  const hideNotification = () => {
    const animations = [];

    if (animationType === 'slide') {
      animations.push(
        Animated.timing(translateY, {
          toValue: getInitialTranslateY(),
          duration: 250,
          useNativeDriver: true,
        })
      );
    }

    if (animationType === 'fade' || animationType === 'scale') {
      animations.push(
        Animated.timing(opacity, {
          toValue: 0,
          duration: 250,
          useNativeDriver: true,
        })
      );
    }

    if (animationType === 'scale') {
      animations.push(
        Animated.timing(scale, {
          toValue: 0.8,
          duration: 250,
          useNativeDriver: true,
        })
      );
    }

    Animated.parallel(animations).start() => {
      onClose?.();
    });
  };

  // 处理关闭
  const handleClose = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    hideNotification();
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

    return <Text style={styles.defaultIcon}>{iconMap[type]}</Text>;
  };

  // 生命周期管理
  useEffect() => {
    if (visible) {
      showNotification();

      if (duration > 0) {
        timeoutRef.current = setTimeout() => {
          handleClose();
        }, duration);
      }
    } else {
      hideNotification();
    }

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [visible, duration, showNotification, hideNotification]);

  if (!visible) return null;

  // 渲染操作按钮
  const renderActions = () => {
    if (!actions || actions.length === 0) return null;

    return (
      <View style={styles.actionsContainer}>
        {actions.map(action, index) => (
          <TouchableOpacity;
            key={index}
            style={[
              styles.actionButton,
              action.style === 'primary' && styles.primaryActionButton,
            ]}
            onPress={action.onPress}
          >
            <Text;
              style={[
                styles.actionButtonText,
                action.style === 'primary' && styles.primaryActionButtonText,
              ]}
            >
              {action.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
    );
  };

  // 渲染通知内容
  const renderContent = () => (
    <View style={[styles.container, { maxWidth }, style]}>
      <View style={styles.content}>
        <View style={styles.iconContainer}>{getTypeIcon()}</View>

        <View style={styles.textContainer}>
          {title && (
            <Text style={[styles.title, titleStyle]} numberOfLines={2}>
              {title}
            </Text>
          )}
          <Text style={[styles.message, messageStyle]} numberOfLines={4}>
            {message}
          </Text>
          {renderActions()}
        </View>

        {closable && (
          <TouchableOpacity style={styles.closeButton} onPress={handleClose}>
            <Text style={styles.closeButtonText}>×</Text>
          </TouchableOpacity>
        )}
      </View>
    </View>
  );

  // 渲染通知
  const renderNotification = () => {
    const transforms = [];
    if (animationType === 'slide') {
      transforms.push({ translateY });
    }
    if (animationType === 'scale') {
      transforms.push({ scale });
    }

    const animatedStyle = {
      opacity:
        animationType === 'fade' || animationType === 'scale' ? opacity : 1,
      transform: transforms,
    };

    return (
      <Animated.View style={[styles.wrapper, animatedStyle]}>
        <TouchableOpacity;
          activeOpacity={onPress ? 0.8 : 1}
          onPress={onPress}
          disabled={!onPress}
        >
          {renderContent()}
        </TouchableOpacity>
      </Animated.View>
    );
  };

  return (
    <View style={[styles.overlay, backdrop && styles.backdropOverlay]}>
      {renderNotification()}
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
      justifyContent:
        position === 'top'
          ? 'flex-start'
          : position === 'bottom'
            ? 'flex-end'
            : 'center',
      alignItems: 'center',
      paddingTop: position === 'top' ? 50 : 0,
      paddingBottom: position === 'bottom' ? 50 : 0,
      paddingHorizontal: theme.spacing.md,
      pointerEvents: 'box-none',
      zIndex: 1000,
    },
    backdropOverlay: {,
  backgroundColor: 'rgba(0, 0, 0, 0.3)',
      pointerEvents: 'auto',
    },
    wrapper: {,
  width: '100%',
      alignItems: 'center',
    },
    container: {,
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
      alignItems: 'flex-start',
      padding: theme.spacing.md,
    },
    iconContainer: {,
  marginRight: theme.spacing.sm,
      paddingTop: theme.spacing.xs,
    },
    defaultIcon: {,
  fontSize: 20,
    },
    textContainer: {,
  flex: 1,
    },
    title: {,
  fontSize: theme.typography.fontSize.base,
      fontWeight: theme.typography.fontWeight.semibold,
      color: colors.text,
      marginBottom: theme.spacing.xs,
    },
    message: {,
  fontSize: theme.typography.fontSize.sm,
      color: colors.text,
      lineHeight: theme.typography.fontSize.sm * 1.4,
    },
    closeButton: {,
  padding: theme.spacing.xs,
      marginLeft: theme.spacing.sm,
    },
    closeButtonText: {,
  fontSize: 20,
      color: colors.text,
      fontWeight: theme.typography.fontWeight.bold,
    },
    actionsContainer: {,
  flexDirection: 'row',
      marginTop: theme.spacing.sm,
      gap: theme.spacing.sm,
    },
    actionButton: {,
  paddingHorizontal: theme.spacing.md,
      paddingVertical: theme.spacing.xs,
      borderRadius: theme.borderRadius.md,
      backgroundColor: theme.colors.surface,
      borderWidth: 1,
      borderColor: colors.border,
    },
    primaryActionButton: {,
  backgroundColor: colors.border,
      borderColor: colors.border,
    },
    actionButtonText: {,
  fontSize: theme.typography.fontSize.sm,
      color: colors.text,
      fontWeight: theme.typography.fontWeight.medium,
    },
    primaryActionButtonText: {,
  color: theme.colors.onPrimary,
    },
  });
};

export default Notification;
