import { useTheme } from '../../contexts/ThemeContext';
import { useAccessibility } from '../../contexts/AccessibilityContext';
import { responsive, touchTarget } from '../../utils/responsive';
import { animations, createAnimatedValue } from '../../utils/animations';

/**
 * 索克生活 - Button组件
 * 统一的按钮组件，支持多种样式和状态
 */

import React, { useRef, useEffect } from 'react';
  TouchableOpacity,
  Text,
  StyleSheet,
  ViewStyle,
  TextStyle,
  ActivityIndicator,
  Animated,
  Platform,
  AccessibilityRole,
} from 'react-native';

// 按钮变体类型
export type ButtonVariant = 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger' | 'success' | 'warning';

// 按钮尺寸类型
export type ButtonSize = 'small' | 'medium' | 'large' | 'xlarge';

// 按钮形状类型
export type ButtonShape = 'rounded' | 'square' | 'circle';

// 按钮属性接口
export interface ButtonProps {
  // 基础属性
  title?: string;
  onPress?: () => void;
  disabled?: boolean;
  loading?: boolean;
  
  // 样式属性
  variant?: ButtonVariant;
  size?: ButtonSize;
  shape?: ButtonShape;
  fullWidth?: boolean;
  
  // 图标属性
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  iconOnly?: boolean;
  
  // 动画属性
  animationType?: 'none' | 'scale' | 'bounce' | 'pulse';
  hapticFeedback?: boolean;
  
  // 无障碍属性
  accessibilityLabel?: string;
  accessibilityHint?: string;
  accessibilityRole?: AccessibilityRole;
  
  // 自定义样式
  style?: ViewStyle;
  textStyle?: TextStyle;
  
  // 其他属性
  testID?: string;
  children?: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  title,
  onPress,
  disabled = false,
  loading = false,
  variant = 'primary',
  size = 'medium',
  shape = 'rounded',
  fullWidth = false,
  leftIcon,
  rightIcon,
  iconOnly = false,
  animationType = 'scale',
  hapticFeedback = true,
  accessibilityLabel,
  accessibilityHint,
  accessibilityRole = 'button',
  style,
  textStyle,
  testID,
  children,
}) => {
  const { theme } = useTheme();
  const { config, triggerHapticFeedback, announceForAccessibility } = useAccessibility();
  
  // 动画值
  const scaleValue = useRef(createAnimatedValue(1)).current;
  const opacityValue = useRef(createAnimatedValue(1)).current;
  
  // 处理按钮按下
  const handlePressIn = useCallback( () => {, []);
    if (disabled || loading) {return;}
    
    // 触觉反馈
    if (hapticFeedback && config.hapticFeedbackEnabled) {
      triggerHapticFeedback('light');
    }
    
    // 动画效果
    switch (animationType) {
      case 'scale':
        scaleValue.setValue(0.95);
        break;
      case 'bounce':
        animations.bounce(scaleValue).start();
        break;
      case 'pulse':
        animations.pulse(scaleValue).start();
        break;
    }
  };
  
  // 处理按钮释放
  const handlePressOut = useCallback( () => {, []);
    if (disabled || loading) {return;}
    
    // 恢复动画
    if (animationType === 'scale') {
      scaleValue.setValue(1);
    }
  };
  
  // 处理按钮点击
  const handlePress = useCallback( () => {, []);
    if (disabled || loading) {return;}
    
    // 无障碍公告
    if (config.screenReaderEnabled && title) {
      announceForAccessibility(`${title} 按钮已激活`);
    }
    
    onPress?.();
  };
  
  // 获取按钮样式
  const getButtonStyles = (): ViewStyle => {
    const baseStyles: ViewStyle = {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'center',
      borderWidth: 1,
      borderColor: 'transparent',
    };
    
    // 尺寸样式
    const sizeStyles = getSizeStyles();
    
    // 变体样式
    const variantStyles = getVariantStyles();
    
    // 形状样式
    const shapeStyles = getShapeStyles();
    
    // 响应式样式
    const responsiveStyles: ViewStyle = {
      minHeight: touchTarget.ensureMinimumSize(sizeStyles.minHeight as number || 44),
      minWidth: fullWidth ? '100%' : touchTarget.ensureMinimumSize(sizeStyles.minWidth as number || 44),
    };
    
    // 禁用状态样式
    const disabledStyles: ViewStyle = disabled ? {
      opacity: 0.5,
    } : {};
    
    return {
      ...baseStyles,
      ...sizeStyles,
      ...variantStyles,
      ...shapeStyles,
      ...responsiveStyles,
      ...disabledStyles,
    };
  };
  
  // 获取尺寸样式
  const getSizeStyles = (): ViewStyle => {
    const sizes = {
      small: {
        paddingHorizontal: responsive.width(12),
        paddingVertical: responsive.height(8),
        minHeight: responsive.height(32),
        minWidth: responsive.width(64),
      },
      medium: {
        paddingHorizontal: responsive.width(16),
        paddingVertical: responsive.height(12),
        minHeight: responsive.height(44),
        minWidth: responsive.width(88),
      },
      large: {
        paddingHorizontal: responsive.width(20),
        paddingVertical: responsive.height(16),
        minHeight: responsive.height(52),
        minWidth: responsive.width(112),
      },
      xlarge: {
        paddingHorizontal: responsive.width(24),
        paddingVertical: responsive.height(20),
        minHeight: responsive.height(60),
        minWidth: responsive.width(136),
      },
    };
    
    return sizes[size];
  };
  
  // 获取变体样式
  const getVariantStyles = (): ViewStyle => {
    const variants = {
      primary: {
        backgroundColor: theme.colors.primary,
        borderColor: theme.colors.primary,
      },
      secondary: {
        backgroundColor: theme.colors.secondary,
        borderColor: theme.colors.secondary,
      },
      outline: {
        backgroundColor: 'transparent',
        borderColor: theme.colors.primary,
        borderWidth: 1,
      },
      ghost: {
        backgroundColor: 'transparent',
        borderColor: 'transparent',
      },
      danger: {
        backgroundColor: theme.colors.error,
        borderColor: theme.colors.error,
      },
      success: {
        backgroundColor: theme.colors.success,
        borderColor: theme.colors.success,
      },
      warning: {
        backgroundColor: theme.colors.warning,
        borderColor: theme.colors.warning,
      },
    };
    
    return variants[variant];
  };
  
  // 获取形状样式
  const getShapeStyles = (): ViewStyle => {
    const shapes = {
      rounded: {
        borderRadius: theme.borderRadius.md,
      },
      square: {
        borderRadius: 0,
      },
      circle: {
        borderRadius: theme.borderRadius.full,
      },
    };
    
    return shapes[shape];
  };
  
  // 获取文本样式
  const getTextStyles = (): TextStyle => {
    const baseStyles: TextStyle = {
      fontFamily: theme.typography.fontFamily.medium,
      textAlign: 'center',
    };
    
    // 尺寸文本样式
    const sizeTextStyles = {
      small: {
        fontSize: responsive.fontSize(theme.typography.fontSize.sm),
        lineHeight: responsive.fontSize(theme.typography.fontSize.sm * 1.4),
      },
      medium: {
        fontSize: responsive.fontSize(theme.typography.fontSize.base),
        lineHeight: responsive.fontSize(theme.typography.fontSize.base * 1.4),
      },
      large: {
        fontSize: responsive.fontSize(theme.typography.fontSize.lg),
        lineHeight: responsive.fontSize(theme.typography.fontSize.lg * 1.4),
      },
      xlarge: {
        fontSize: responsive.fontSize(theme.typography.fontSize.xl),
        lineHeight: responsive.fontSize(theme.typography.fontSize.xl * 1.4),
      },
    };
    
    // 变体文本颜色
    const variantTextStyles = {
      primary: { color: theme.colors.onPrimary },
      secondary: { color: theme.colors.onSecondary },
      outline: { color: theme.colors.primary },
      ghost: { color: theme.colors.primary },
      danger: { color: theme.colors.onPrimary },
      success: { color: theme.colors.onPrimary },
      warning: { color: theme.colors.onPrimary },
    };
    
    // 无障碍字体缩放
    const accessibilityStyles: TextStyle = config.largeFontEnabled ? {
      fontSize: sizeTextStyles[size].fontSize * config.fontScale,
    } : {};
    
    return {
      ...baseStyles,
      ...sizeTextStyles[size],
      ...variantTextStyles[variant],
      ...accessibilityStyles,
    };
  };
  
  // 生成无障碍标签
  const generateAccessibilityLabel = (): string => {
    if (accessibilityLabel) {return accessibilityLabel;}
    
    let label = title || '按钮';
    
    if (loading) {
      label += ', 加载中';
    }
    
    if (disabled) {
      label += ', 已禁用';
    }
    
    return label;
  };
  
  // 生成无障碍提示
  const generateAccessibilityHint = (): string => {
    if (accessibilityHint) {return accessibilityHint;}
    
    if (disabled) {
      return '此按钮当前不可用';
    }
    
    if (loading) {
      return '正在处理，请稍候';
    }
    
    return '双击激活';
  };
  
  // 渲染按钮内容
  const renderContent = useCallback( () => {, []);
    if (loading) {
      return (
        <ActivityIndicator
          size={size === 'small' ? 'small' : 'large'}
          color={getTextStyles().color}
        />
      );
    }
    
    if (iconOnly && (leftIcon || rightIcon)) {
      return leftIcon || rightIcon;
    }
    
    return (
      <>
        {leftIcon && (
          <Animated.View style={{ marginRight: title ? responsive.width(8) : 0 }}>
            {leftIcon}
          </Animated.View>
        )}
        
        {(title || children) && (
          <Text style={[getTextStyles(), textStyle]}>
            {children || title}
          </Text>
        )}
        
        {rightIcon && (
          <Animated.View style={{ marginLeft: title ? responsive.width(8) : 0 }}>
            {rightIcon}
          </Animated.View>
        )}
      </>
    );
  };
  
  return (
    <TouchableOpacity
      style={[
        getButtonStyles(),
        style,
        {
          transform: [{ scale: scaleValue }],
          opacity: opacityValue,
        },
      ]}
      onPress={handlePress}
      onPressIn={handlePressIn}
      onPressOut={handlePressOut}
      disabled={disabled || loading}
      activeOpacity={0.8}
      accessible={true}
      accessibilityRole={accessibilityRole}
      accessibilityLabel={generateAccessibilityLabel()}
      accessibilityHint={generateAccessibilityHint()}
      accessibilityState={{
        disabled: disabled || loading,
        busy: loading,
      }}
      testID={testID}
    >
      {renderContent()}
    </TouchableOpacity>
  );
};

export default Button; 