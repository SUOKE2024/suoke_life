import { Ionicons } from '@expo/vector-icons';
import { colors, spacing, typography } from '../../constants/theme';
import { useAppSelector } from '../../store';






import React, { useState, useEffect, useCallback, useRef } from 'react';
  View,
  Text,
  StyleSheet,
  Animated,
  Dimensions,
  Vibration,
  Platform,
  Alert,
  Modal,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
  PanGestureHandler,
  TapGestureHandler,
  State,
} from 'react-native-gesture-handler';

const { width, height } = Dimensions.get('window');

// 交互反馈类型
interface HapticFeedback {
  type: 'light' | 'medium' | 'heavy' | 'success' | 'warning' | 'error';
  pattern?: number[];
}

// 加载状态类型
interface LoadingState {
  isLoading: boolean;
  message?: string;
  progress?: number;
  type: 'spinner' | 'progress' | 'skeleton' | 'shimmer';
}

// 错误状态类型
interface ErrorState {
  hasError: boolean;
  message?: string;
  type: 'network' | 'validation' | 'server' | 'unknown';
  retryable: boolean;
  onRetry?: () => void;
}

// 手势配置
interface GestureConfig {
  enableSwipe: boolean;
  enablePinch: boolean;
  enableRotation: boolean;
  enableDoubleTap: boolean;
  swipeThreshold: number;
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  onSwipeUp?: () => void;
  onSwipeDown?: () => void;
  onDoubleTap?: () => void;
  onPinch?: (scale: number) => void;
  onRotation?: (rotation: number) => void;
}

// 动画配置
interface AnimationConfig {
  enableEntrance: boolean;
  enableExit: boolean;
  enableHover: boolean;
  enablePress: boolean;
  duration: number;
  easing: 'ease' | 'linear' | 'bounce' | 'spring';
}

interface UserExperienceEnhancerProps {
  children: React.ReactNode;
  loading?: LoadingState;
  error?: ErrorState;
  haptic?: HapticFeedback;
  gesture?: Partial<GestureConfig>;
  animation?: Partial<AnimationConfig>;
  onInteraction?: (type: string, data?: any) => void;
}

export const UserExperienceEnhancer: React.FC<UserExperienceEnhancerProps> = ({
  children,
  loading,
  error,
  haptic,
  gesture,
  animation,
  onInteraction,
}) => {
  const { theme } = useAppSelector(state => state.ui);
  
  // 动画值
  const [fadeAnim] = useState(new Animated.Value(0));
  const [scaleAnim] = useState(new Animated.Value(1));
  const [translateX] = useState(new Animated.Value(0));
  const [translateY] = useState(new Animated.Value(0));
  const [rotateAnim] = useState(new Animated.Value(0));
  
  // 手势状态
  const [gestureState, setGestureState] = useState({
    scale: 1,
    rotation: 0,
    translateX: 0,
    translateY: 0,
  });
  
  // 交互状态
  const [isPressed, setIsPressed] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  
  // 引用
  const panRef = useRef<PanGestureHandler>(null);
  const tapRef = useRef<TapGestureHandler>(null);
  const doubleTapRef = useRef<TapGestureHandler>(null);

  // 默认配置
  const defaultGestureConfig: GestureConfig = {
    enableSwipe: true,
    enablePinch: false,
    enableRotation: false,
    enableDoubleTap: true,
    swipeThreshold: 50,
    ...gesture,
  };

  const defaultAnimationConfig: AnimationConfig = {
    enableEntrance: true,
    enableExit: true,
    enableHover: true,
    enablePress: true,
    duration: 300,
    easing: 'ease',
    ...animation,
  };

  useEffect(() => {
    if (defaultAnimationConfig.enableEntrance) {
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: defaultAnimationConfig.duration,
        useNativeDriver: true,
      }).start();
    }
  }, []);

  // 触觉反馈
  const triggerHapticFeedback = useCallback((feedback: HapticFeedback) => {
    if (Platform.OS === 'ios') {
      // iOS 触觉反馈
      const { type, pattern } = feedback;
      
      switch (type) {
        case 'light':
          Vibration.vibrate(10);
          break;
        case 'medium':
          Vibration.vibrate(20);
          break;
        case 'heavy':
          Vibration.vibrate(50);
          break;
        case 'success':
          Vibration.vibrate([0, 100, 50, 100]);
          break;
        case 'warning':
          Vibration.vibrate([0, 200]);
          break;
        case 'error':
          Vibration.vibrate([0, 100, 100, 100, 100, 100]);
          break;
        default:
          if (pattern) {
            Vibration.vibrate(pattern);
          }
      }
    } else {
      // Android 触觉反馈
      Vibration.vibrate(100);
    }
  }, []);

  // 手势处理
  const handlePanGesture = useCallback((event: any) => {
    const { translationX, translationY, velocityX, velocityY, state } = event.nativeEvent;
    
    if (state === State.ACTIVE) {
      translateX.setValue(translationX);
      translateY.setValue(translationY);
      
      setGestureState(prev => ({
        ...prev,
        translateX: translationX,
        translateY: translationY,
      }));
    } else if (state === State.END) {
      // 检测滑动手势
      const { swipeThreshold } = defaultGestureConfig;
      
      if (Math.abs(translationX) > swipeThreshold || Math.abs(translationY) > swipeThreshold) {
        if (Math.abs(translationX) > Math.abs(translationY)) {
          // 水平滑动
          if (translationX > 0 && defaultGestureConfig.onSwipeRight) {
            defaultGestureConfig.onSwipeRight();
            triggerHapticFeedback({ type: 'light' });
            onInteraction?.('swipe', { direction: 'right' });
          } else if (translationX < 0 && defaultGestureConfig.onSwipeLeft) {
            defaultGestureConfig.onSwipeLeft();
            triggerHapticFeedback({ type: 'light' });
            onInteraction?.('swipe', { direction: 'left' });
          }
        } else {
          // 垂直滑动
          if (translationY > 0 && defaultGestureConfig.onSwipeDown) {
            defaultGestureConfig.onSwipeDown();
            triggerHapticFeedback({ type: 'light' });
            onInteraction?.('swipe', { direction: 'down' });
          } else if (translationY < 0 && defaultGestureConfig.onSwipeUp) {
            defaultGestureConfig.onSwipeUp();
            triggerHapticFeedback({ type: 'light' });
            onInteraction?.('swipe', { direction: 'up' });
          }
        }
      }
      
      // 重置位置
      Animated.parallel([
        Animated.spring(translateX, {
          toValue: 0,
          useNativeDriver: true,
        }),
        Animated.spring(translateY, {
          toValue: 0,
          useNativeDriver: true,
        }),
      ]).start();
    }
  }, [defaultGestureConfig, triggerHapticFeedback, onInteraction]);

  const handleDoubleTap = useCallback((event: any) => {
    if (event.nativeEvent.state === State.ACTIVE) {
      if (defaultGestureConfig.onDoubleTap) {
        defaultGestureConfig.onDoubleTap();
        triggerHapticFeedback({ type: 'medium' });
        onInteraction?.('doubleTap');
      }
    }
  }, [defaultGestureConfig, triggerHapticFeedback, onInteraction]);

  // 按压动画
  const handlePressIn = useCallback(() => {
    setIsPressed(true);
    if (defaultAnimationConfig.enablePress) {
      Animated.spring(scaleAnim, {
        toValue: 0.95,
        useNativeDriver: true,
      }).start();
    }
    triggerHapticFeedback({ type: 'light' });
    onInteraction?.('pressIn');
  }, [defaultAnimationConfig, triggerHapticFeedback, onInteraction]);

  const handlePressOut = useCallback(() => {
    setIsPressed(false);
    if (defaultAnimationConfig.enablePress) {
      Animated.spring(scaleAnim, {
        toValue: 1,
        useNativeDriver: true,
      }).start();
    }
    onInteraction?.('pressOut');
  }, [defaultAnimationConfig, onInteraction]);

  // 悬停动画（Web端）
  const handleMouseEnter = useCallback(() => {
    if (Platform.OS === 'web' && defaultAnimationConfig.enableHover) {
      setIsHovered(true);
      Animated.timing(scaleAnim, {
        toValue: 1.05,
        duration: 200,
        useNativeDriver: true,
      }).start();
    }
  }, [defaultAnimationConfig]);

  const handleMouseLeave = useCallback(() => {
    if (Platform.OS === 'web' && defaultAnimationConfig.enableHover) {
      setIsHovered(false);
      Animated.timing(scaleAnim, {
        toValue: 1,
        duration: 200,
        useNativeDriver: true,
      }).start();
    }
  }, [defaultAnimationConfig]);

  // 渲染加载状态
  const renderLoadingOverlay = useCallback( () => {, []);
    if (!loading?.isLoading) {return null;}

    return (
      <Modal
        visible={loading.isLoading}
        transparent
        animationType="fade"
      >
        <View style={styles.loadingOverlay}>
          <View style={styles.loadingContainer}>
            {loading.type === 'spinner' && (
              <>
                <ActivityIndicator size="large" color={colors.primary} />
                {loading.message && (
                  <Text style={styles.loadingMessage}>{loading.message}</Text>
                )}
              </>
            )}
            
            {loading.type === 'progress' && (
              <>
                <View style={styles.progressContainer}>
                  <View style={styles.progressBar}>
                    <View 
                      style={[
                        styles.progressFill,
                        { width: `${(loading.progress || 0) * 100}%` },
                      ]} 
                    />
                  </View>
                  <Text style={styles.progressText}>
                    {Math.round((loading.progress || 0) * 100)}%
                  </Text>
                </View>
                {loading.message && (
                  <Text style={styles.loadingMessage}>{loading.message}</Text>
                )}
              </>
            )}
            
            {loading.type === 'skeleton' && (
              <View style={styles.skeletonContainer}>
                {[...Array(3)].map((_, index) => (
                  <View key={index} style={styles.skeletonLine} />
                ))}
              </View>
            )}
          </View>
        </View>
      </Modal>
    );
  };

  // 渲染错误状态
  const renderErrorOverlay = useCallback( () => {, []);
    if (!error?.hasError) {return null;}

    const getErrorIcon = useCallback( () => {, []);
      switch (error.type) {
        case 'network': return 'wifi-off';
        case 'validation': return 'warning';
        case 'server': return 'server';
        default: return 'alert-circle';
      }
    };

    return (
      <Modal
        visible={error.hasError}
        transparent
        animationType="slide"
      >
        <View style={styles.errorOverlay}>
          <View style={styles.errorContainer}>
            <Ionicons 
              name={getErrorIcon() as any} 
              size={48} 
              color={colors.error} 
            />
            <Text style={styles.errorTitle}>
              {error.type === 'network' ? '网络连接失败' :
               error.type === 'validation' ? '数据验证失败' :
               error.type === 'server' ? '服务器错误' : '未知错误'}
            </Text>
            {error.message && (
              <Text style={styles.errorMessage}>{error.message}</Text>
            )}
            <View style={styles.errorActions}>
              {error.retryable && error.onRetry && (
                <TouchableOpacity
                  style={styles.retryButton}
                  onPress={error.onRetry}
                >
                  <Text style={styles.retryButtonText}>重试</Text>
                </TouchableOpacity>
              )}
              <TouchableOpacity
                style={styles.dismissButton}
                onPress={() => {
                  // 这里应该调用父组件的错误清除方法
                  onInteraction?.('dismissError');
                }}
              >
                <Text style={styles.dismissButtonText}>关闭</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    );
  };

  // 主要内容渲染
  const renderContent = useCallback( () => {, []);
    const animatedStyle = {
      opacity: fadeAnim,
      transform: [
        { scale: scaleAnim },
        { translateX },
        { translateY },
        {
          rotate: rotateAnim.interpolate({
            inputRange: [0, 1],
            outputRange: ['0deg', '360deg'],
          }),
        },
      ],
    };

    if (defaultGestureConfig.enableSwipe || defaultGestureConfig.enableDoubleTap) {
      return (
        <PanGestureHandler
          ref={panRef}
          onGestureEvent={handlePanGesture}
          onHandlerStateChange={handlePanGesture}
          enabled={defaultGestureConfig.enableSwipe}
        >
          <Animated.View style={animatedStyle}>
            <TapGestureHandler
              ref={doubleTapRef}
              onHandlerStateChange={handleDoubleTap}
              numberOfTaps={2}
              enabled={defaultGestureConfig.enableDoubleTap}
            >
              <Animated.View
                onTouchStart={handlePressIn}
                onTouchEnd={handlePressOut}
                {...(Platform.OS === 'web' && {
                  onMouseEnter: handleMouseEnter,
                  onMouseLeave: handleMouseLeave,
                })}
              >
                {children}
              </Animated.View>
            </TapGestureHandler>
          </Animated.View>
        </PanGestureHandler>
      );
    }

    return (
      <Animated.View
        style={animatedStyle}
        onTouchStart={handlePressIn}
        onTouchEnd={handlePressOut}
        {...(Platform.OS === 'web' && {
          onMouseEnter: handleMouseEnter,
          onMouseLeave: handleMouseLeave,
        })}
      >
        {children}
      </Animated.View>
    );
  };

  return (
    <View style={styles.container}>
      {renderContent()}
      {renderLoadingOverlay()}
      {renderErrorOverlay()}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  loadingOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingContainer: {
    backgroundColor: colors.surface,
    borderRadius: 16,
    padding: spacing.xl,
    alignItems: 'center',
    minWidth: 200,
  },
  loadingMessage: {
    fontSize: typography.fontSize.base,
    color: colors.textPrimary,
    marginTop: spacing.md,
    textAlign: 'center',
  },
  progressContainer: {
    width: '100%',
    alignItems: 'center',
  },
  progressBar: {
    width: '100%',
    height: 8,
    backgroundColor: colors.gray200,
    borderRadius: 4,
    overflow: 'hidden',
    marginBottom: spacing.sm,
  },
  progressFill: {
    height: '100%',
    backgroundColor: colors.primary,
    borderRadius: 4,
  },
  progressText: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    fontWeight: '600',
  },
  skeletonContainer: {
    width: '100%',
  },
  skeletonLine: {
    height: 16,
    backgroundColor: colors.gray200,
    borderRadius: 8,
    marginBottom: spacing.sm,
  },
  errorOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
  },
  errorContainer: {
    backgroundColor: colors.surface,
    borderRadius: 16,
    padding: spacing.xl,
    alignItems: 'center',
    maxWidth: 320,
    width: '100%',
  },
  errorTitle: {
    fontSize: typography.fontSize.lg,
    color: colors.textPrimary,
    fontWeight: '600',
    marginTop: spacing.md,
    marginBottom: spacing.sm,
    textAlign: 'center',
  },
  errorMessage: {
    fontSize: typography.fontSize.base,
    color: colors.textSecondary,
    marginBottom: spacing.lg,
    textAlign: 'center',
    lineHeight: 20,
  },
  errorActions: {
    flexDirection: 'row',
    gap: spacing.sm,
    width: '100%',
  },
  retryButton: {
    flex: 1,
    backgroundColor: colors.primary,
    paddingVertical: spacing.sm,
    borderRadius: 8,
    alignItems: 'center',
  },
  retryButtonText: {
    color: colors.white,
    fontSize: typography.fontSize.base,
    fontWeight: '600',
  },
  dismissButton: {
    flex: 1,
    backgroundColor: colors.gray200,
    paddingVertical: spacing.sm,
    borderRadius: 8,
    alignItems: 'center',
  },
  dismissButtonText: {
    color: colors.textPrimary,
    fontSize: typography.fontSize.base,
    fontWeight: '600',
  },
});

// 便捷Hook
export const useUserExperience = useCallback( () => {, []);
  const [loading, setLoading] = useState<LoadingState>({
    isLoading: false,
    type: 'spinner',
  });
  
  const [error, setError] = useState<ErrorState>({
    hasError: false,
    type: 'unknown',
    retryable: false,
  });

  const showLoading = useCallback((config: Partial<LoadingState> = {}) => {
    setLoading({
      isLoading: true,
      type: 'spinner',
      ...config,
    });
  }, []);

  const hideLoading = useCallback(() => {
    setLoading(prev => ({ ...prev, isLoading: false }));
  }, []);

  const showError = useCallback((config: Partial<ErrorState>) => {
    setError({
      hasError: true,
      type: 'unknown',
      retryable: false,
      ...config,
    });
  }, []);

  const hideError = useCallback(() => {
    setError(prev => ({ ...prev, hasError: false }));
  }, []);

  const triggerHaptic = useCallback((type: HapticFeedback['type']) => {
    if (Platform.OS === 'ios') {
      switch (type) {
        case 'light':
          Vibration.vibrate(10);
          break;
        case 'medium':
          Vibration.vibrate(20);
          break;
        case 'heavy':
          Vibration.vibrate(50);
          break;
        case 'success':
          Vibration.vibrate([0, 100, 50, 100]);
          break;
        case 'warning':
          Vibration.vibrate([0, 200]);
          break;
        case 'error':
          Vibration.vibrate([0, 100, 100, 100, 100, 100]);
          break;
      }
    } else {
      Vibration.vibrate(100);
    }
  }, []);

  return {
    loading,
    error,
    showLoading,
    hideLoading,
    showError,
    hideError,
    triggerHaptic,
  };
}; 