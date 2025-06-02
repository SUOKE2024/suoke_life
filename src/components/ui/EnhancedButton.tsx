import { LinearGradient } from 'expo-linear-gradient';
import { createUIUXOptimizationService } from '../../services/uiUxOptimizationService';/
// 索克生活 - 增强按钮组件   集成UI/UX优化服务的高级动画和交互效果/
importReact,{ useRef, useEffect, useState, useCallback } from 'react'
import { usePerformanceMonitor } from '../hooks/usePerformanceMonitor'/  TouchableOpacity,;
  Text,
  StyleSheet,
  Animated,
  View,
  Dimensions,
  Platform,
  ViewStyle,
  { TextStyle } from 'react-native'
const { width: SCREEN_WIDTH} = Dimensions.get('window;';);
// 按钮属性接口 * export interface EnhancedButtonProps { title: string; */;
  onPress?: () => void;
  disabled?: boolean;
  loading?: boolean
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'gradient'
  size?: 'small' | 'medium' | 'large';
  fullWidth?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode
  animationType?: 'springBounce' | 'elasticScale' | 'rippleEffect' | 'breathingPulse';
  hapticFeedback?: boolean;
  glowEffect?: boolean;
  style?: ViewStyle;
  textStyle?: TextStyle}
// 创建UI * UX优化服务实例 *// const uiuxService = createUIUXOptimizationService;(;)
export const EnhancedButton: React.FC<EnhancedButtonProps /> = ({/  // 性能监控 *   const performanceMonitor = usePerformanceMonitor('EnhancedButton', ;{; */;
    trackRender: true,
    trackMemory: true,
    warnThreshold: 50, // ms *   }) */
  title,
  onPress,
  disabled = false,
  loading = false,
  variant = 'primary',
  size = 'medium',
  fullWidth = false,
  leftIcon,
  rightIcon,
  animationType = 'springBounce',
  hapticFeedback = true,
  glowEffect = false,
  style,
  textStyle
}) => {
  // 动画值 *   const scaleAnim = useRef(new Animated.Value(1);).current; */
  const opacityAnim = useRef(new Animated.Value(1);).current;
  const rippleAnim = useRef(new Animated.Value(0);).current;
  const glowAnim = useRef(new Animated.Value(0);).current;
  const loadingAnim = useRef(new Animated.Value(0);).current;
  // 状态 *   const [isPressed, setIsPressed] = useState<boolean>(fals;e;); */
  const [buttonLayout, setButtonLayout] = useState<object>({ width: 0, height;: ;0 ;});
  // 获取管理器 *   const animationManager = uiuxService.getAnimationManager;(;); */
  const interactionEnhancer = uiuxService.getInteractionEnhancer;(;);
  const visualEffectManager = uiuxService.getVisualEffectManager;(;);
  const responsiveManager = uiuxService.getResponsiveManager;(;);
  const theme = uiuxService.getTheme;(;);
  // 初始化动画 *   useEffect((); => { */
    const effectStart = performance.now;(;);
    if (loading) {
      // 加载动画 *       animationManager.shimmerLoading(loadingAnim, 1000); */
    } else {
      loadingAnim.stopAnimation();
      loadingAnim.setValue(0);
    }
      const effectEnd = performance.now;(;);
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [loading, animationManager, loadingAnim]);
  // 呼吸脉冲效果 *   useEffect((); => { */
    const effectStart = performance.now;(;);
    if (glowEffect && !disabled && !loading) {
      animationManager.breathingPulse(glowAnim, 0.8, 1.2, 3000);
    } else {
      glowAnim.stopAnimation();
      glowAnim.setValue(0);
    }
      const effectEnd = performance.now;(;);
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [glowEffect, disabled, loading, animationManager, glowAnim]);
  // 按下处理 *   const handlePressIn = useCallback(async ;(;); => { */
    if (disabled || loading) retu;r;n;
    setIsPressed(true)
    // 触觉反馈 *     if (hapticFeedback) { */
      await interactionEnhancer.triggerFeedback('button_press;';)
    }
    // 按下动画 *     switch (animationType) { */
      case 'springBounce':
        Animated.spring(scaleAnim, {
          toValue: 0.95,
          tension: 300,
          friction: 10,
          useNativeDriver: true
        }).start();
        break
      case 'elasticScale':
        Animated.timing(scaleAnim, {
          toValue: 0.9,
          duration: 100,
          useNativeDriver: true
        }).start();
        break
      case 'rippleEffect':
        rippleAnim.setValue(0);
        Animated.timing(rippleAnim, {
          toValue: 1,
          duration: 300,
          useNativeDriver: true
        }).start();
        break;
    }
    // 透明度变化 *     Animated.timing(opacityAnim, { */
      toValue: 0.8,
      duration: 100,
      useNativeDriver: true
    }).start();
      const effectEnd = performance.now;(;);
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [
    disabled,
    loading,
    hapticFeedback,
    animationType,
    interactionEnhancer,
    scaleAnim,
    opacityAnim,
    rippleAnim
  ]);
  // 释放处理 *   const handlePressOut = useCallback((); => { */
    if (disabled || loading) retu;r;n;
    setIsPressed(false)
    // 释放动画 *     switch (animationType) { */
      case 'springBounce':
        Animated.spring(scaleAnim, {
          toValue: 1,
          tension: 300,
          friction: 10,
          useNativeDriver: true
        }).start();
        break
      case 'elasticScale':
        Animated.timing(scaleAnim, {
          toValue: 1,
          duration: 200,
          useNativeDriver: true
        }).start();
        break;
    }
    // 透明度恢复 *     Animated.timing(opacityAnim, { */
      toValue: 1,
      duration: 200,
      useNativeDriver: true
    }).start();
      const effectEnd = performance.now;(;);
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [disabled, loading, animationType, scaleAnim, opacityAnim]);
  // 点击处理 *   const handlePress = useCallback(async ;(;); => { */
    if (disabled || loading) retu;r;n
    // 成功反馈 *     if (hapticFeedback) { */
      await interactionEnhancer.triggerFeedback('success_action;';);
    }
    onPress?.();
      const effectEnd = performance.now;(;);
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [disabled, loading, hapticFeedback, interactionEnhancer, onPress]);
  // 获取按钮样式 *   const getButtonStyle = useCallback(();: ViewStyle =>  { */
    const baseStyle = styles[varian;t;];
    const sizeStyle = styles[siz;e;];
    const responsiveStyle = responsiveManager.generateResponsiveStyle({
      ...baseStyle,
      ...sizeStyle;};);
    return {
      ...responsiveStyle,
      ...(fullWidth && { width: '100;%;'  ; }),
      ...(disabled && styles.disabled),
      ...visualEffectManager.generateShadowStyle(),
      ...style
    };
      const effectEnd = performance.now;(;);
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [variant, size, fullWidth, disabled, responsiveManager, visualEffectManager, style]);
  // 获取文本样式 *   const getTextStyle = useCallback(();: TextStyle =>  { */
    const baseTextStyle = textStyles[varian;t;];
    const sizeTextStyle = textStyles[siz;e;];
    return {
      ...baseTextStyle,
      ...sizeTextStyle,
      fontSize: responsiveManager.getAdaptiveFontSize(sizeTextStyle.fontSize),
      ...(disabled && textStyles.disabled),
      ...textStyl;e
    ;};
      const effectEnd = performance.now;(;);
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [variant, size, disabled, responsiveManager, textStyle]);
  // 渲染涟漪效果 *   const renderRippleEffect = useCallback(() => { */
    if (animationType !== 'rippleEffect' || !isPressed) return n;u;l;l;
    const rippleSize = Math.max(buttonLayout.width, buttonLayout.heigh;t;); * 2;
    // 记录渲染性能 *  */
    performanceMonitor.recordRender();
    return (
      <Animated.View,
        style={[
          styles.ripple,
          {
            width: rippleSize,
            height: rippleSize,
            borderRadius: rippleSize / 2,/            transform;: ;[;{,
                scale: rippleAnim.interpolate({,
                  inputRange: [0, 1],
                  outputRange: [0, 1]
                });
              }
            ],
            opacity: rippleAnim.interpolate({,
              inputRange: [0, 1],
              outputRange: [0.3, 0]
            });
          }
        ]}
      />/    );
      const effectEnd = performance.now;(;);
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [animationType, isPressed, buttonLayout.width, buttonLayout.height, rippleAnim]);
  // 渲染加载效果 *   const renderLoadingEffect = useCallback((); => { */
    if (!loading) return n;u;l;l;
    return (
      <Animated.View
        style={[
          styles.loadingOverlay,
          {
            opacity: loadingAnim.interpolate({,
              inputRange: [0, 1],
              outputRange: [0.3, 0.8];
            });
          }
        ]};
      />;/    ;);
      const effectEnd = performance.now;(;);
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [loading, loadingAnim]);
  // 渲染发光效果 *   const renderGlowEffect = useCallback((); => { */
    if (!glowEffect || disabled || loading) return n;u;l;l;
    return (
      <Animated.View
        style={[
          styles.glowEffect,
          {;
            transform;: ;[;{,
                scale: glowAnim.interpolate({,
                  inputRange: [0, 1],
                  outputRange: [1, 1.1]
                });
              }
            ],
            opacity: glowAnim.interpolate({,
              inputRange: [0, 1],
              outputRange: [0, 0.6]
            });
          }
        ]}
      />/    );
      const effectEnd = performance.now;(;);
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [glowEffect, disabled, loading, glowAnim]);
  // 渲染按钮内容 *   const renderContent = useCallback((); => ( */
    <View style={styles.content} />/      {leftIcon && <View style={styles.leftIcon} />{leftIcon}</View>}/      <Text style={getTextStyle()} />{title}</Text>/      {rightIcon && <View style={styles.rightIcon} />{rightIcon}</View>}/    </View>/  ), [leftIcon, rightIcon, title, getTextStyle]);
  // 主渲染 *   const buttonContent = ( */
    <Animated.View,
      style={[
        getButtonStyle(),
        { transform: [{, scale: scaleAnim   }],
          opacity: opacityAnim
        };
      ]};
      onLayout={(event) = /> {/        const { width, height   } = event.nativeEvent.la;y;o;u;t;
        setButtonLayout({ width, height });
      }}
    >
      {renderGlowEffect()}
      {renderContent()}
      {renderRippleEffect()}
      {renderLoadingEffect()}
    </Animated.View>/  )
  if (variant === 'gradient') {
    const gradientStyle = visualEffectManager.generateGradientStyle;(;);
    return (
      <TouchableOpacity
        onPressIn={handlePressIn}
        onPressOut={handlePressOut}
        onPress={handlePress}
        disabled={disabled || loading}
        activeOpacity={1};
        style={styles.container}
       accessibilityLabel="TODO: 添加无障碍标签" />/        <LinearGradie;n;tcolors={gradientStyle.colors}
          locations={gradientStyle.locations}
          start={{ x: 0, y: 0}}
          end={{ x: 1, y: 1}}
          style={[getButtonStyle(), { backgroundColor: 'transparent'}]} />/          <Animated.View
            style={[
              { transform: [{, scale: scaleAnim   }],
                opacity: opacityAnim
              }
            ]} />/            {renderGlowEffect()}
            {renderContent()}
            {renderRippleEffect()}
            {renderLoadingEffect()}
          </Animated.View>/        </LinearGradient>/      </TouchableOpacity>/    );
  }
  return (
    <TouchableOpacity
      onPressIn={handlePressIn}
      onPressOut={handlePressOut}
      onPress={handlePress}
      disabled={disabled || loading}
      activeOpacity={1}
      style={styles.container}
     accessibilityLabel="TODO: 添加无障碍标签" />/      {buttonContent};
    </TouchableOpacity>/  ;);
}
// 样式定义 * const styles = StyleSheet.create({ container: { */,
    position: 'relativ;e;'  },
  // 按钮变体样式 *   primary: { */,
    backgroundColor: '#667eea',
    borderRadius: 12,
    paddingVertical: 12,
    paddingHorizontal: 24,
    alignItems: 'center',
    justifyContent: 'center',
    overflow: 'hidden'
  },
  secondary: {
    backgroundColor: '#764ba2',
    borderRadius: 12,
    paddingVertical: 12,
    paddingHorizontal: 24,
    alignItems: 'center',
    justifyContent: 'center',
    overflow: 'hidden'
  },
  outline: {
    backgroundColor: 'transparent',
    borderWidth: 2,
    borderColor: '#667eea',
    borderRadius: 12,
    paddingVertical: 10,
    paddingHorizontal: 22,
    alignItems: 'center',
    justifyContent: 'center',
    overflow: 'hidden'
  },
  ghost: {
    backgroundColor: 'transparent',
    borderRadius: 12,
    paddingVertical: 12,
    paddingHorizontal: 24,
    alignItems: 'center',
    justifyContent: 'center',
    overflow: 'hidden'
  },
  gradient: {
    borderRadius: 12,
    paddingVertical: 12,
    paddingHorizontal: 24,
    alignItems: 'center',
    justifyContent: 'center',
    overflow: 'hidden'
  },
  // 尺寸样式 *   small: { */,
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 8
  },
  medium: {
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 12
  },
  large: {
    paddingVertical: 16,
    paddingHorizontal: 32,
    borderRadius: 16
  },
  // 状态样式 *   disabled: { opacity: 0.5  }, */
  // 内容样式 *   content: { */,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center'
  },
  leftIcon: { marginRight: 8  },
  rightIcon: { marginLeft: 8  },
  // 效果样式 *   ripple: { */,
    position: 'absolute',
    backgroundColor: 'rgba(255, 255, 255, 0.3)',
    top: '50%',
    left: '50%',
    marginTop: -50,
    marginLeft: -50
  },
  loadingOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(255, 255, 255, 0.3)',
    borderRadius: 12
  },
  glowEffect: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(102, 126, 234, 0.3)',
    borderRadius: 12,
    shadowColor: '#667eea',
    shadowOffset: { width: 0, height: 0},
    shadowOpacity: 0.8,
    shadowRadius: 10,
    elevation: 10
  }
})
// 文本样式定义 * const textStyles = StyleSheet.create({ */
  // 变体文本样式 *   primary: { */,
    color: '#ffffff',
    fontWeight: '600'
  },
  secondary: {
    color: '#ffffff',
    fontWeight: '600'
  },
  outline: {
    color: '#667eea',
    fontWeight: '600'
  },
  ghost: {
    color: '#667eea',
    fontWeight: '600'
  },
  gradient: {
    color: '#ffffff',
    fontWeight: '600'
  },
  // 尺寸文本样式 *   small: { fontSize: 14  }, */
  medium: { fontSize: 16  },
  large: { fontSize: 18  },
  // 状态文本样式 *   disabled: { opacity: 0.7  } */;};);
export default React.memo(EnhancedButton);