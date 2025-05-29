/**
 * 索克生活 - Button组件
 * 统一的按钮组件，支持多种样式和状态
 */

import React from 'react';
import {
  TouchableOpacity,
  Text,
  StyleSheet,
  ViewStyle,
  TextStyle,
  ActivityIndicator,
  View,
} from 'react-native';
import { colors, typography, spacing, borderRadius, shadows } from '../../constants/theme';

export interface ButtonProps {
  // 基础属性
  title: string;
  onPress?: () => void;
  disabled?: boolean;
  loading?: boolean;
  
  // 样式属性
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'small' | 'medium' | 'large';
  fullWidth?: boolean;
  
  // 图标
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  
  // 自定义样式
  style?: ViewStyle;
  textStyle?: TextStyle;
  
  // 其他属性
  testID?: string;
}

const Button: React.FC<ButtonProps> = ({
  title,
  onPress,
  disabled = false,
  loading = false,
  variant = 'primary',
  size = 'medium',
  fullWidth = false,
  leftIcon,
  rightIcon,
  style,
  textStyle,
  testID,
}) => {
  const buttonStyle = [
    styles.base,
    styles[variant],
    styles[size],
    fullWidth && styles.fullWidth,
    disabled && styles.disabled,
    style,
  ];

  const textStyleCombined = [
    styles.text,
    styles[`${variant}Text`],
    styles[`${size}Text`],
    disabled && styles.disabledText,
    textStyle,
  ];

  const handlePress = () => {
    if (!disabled && !loading && onPress) {
      onPress();
    }
  };

  return (
    <TouchableOpacity
      style={buttonStyle}
      onPress={handlePress}
      disabled={disabled || loading}
      activeOpacity={0.8}
      testID={testID}
    >
      <View style={styles.content}>
        {loading ? (
          <ActivityIndicator
            size="small"
            color={variant === 'primary' ? colors.white : colors.primary}
            style={styles.loading}
          />
        ) : (
          <>
            {leftIcon && <View style={styles.leftIcon}>{leftIcon}</View>}
            <Text style={textStyleCombined}>{title}</Text>
            {rightIcon && <View style={styles.rightIcon}>{rightIcon}</View>}
          </>
        )}
      </View>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  base: {
    borderRadius: borderRadius.md,
    alignItems: 'center',
    justifyContent: 'center',
    flexDirection: 'row',
    ...shadows.sm,
  },
  
  // 变体样式
  primary: {
    backgroundColor: colors.primary,
  },
  secondary: {
    backgroundColor: colors.secondary,
  },
  outline: {
    backgroundColor: 'transparent',
    borderWidth: 1,
    borderColor: colors.primary,
  },
  ghost: {
    backgroundColor: 'transparent',
  },
  danger: {
    backgroundColor: colors.error,
  },
  
  // 尺寸样式
  small: {
    height: 36,
    paddingHorizontal: spacing.md,
  },
  medium: {
    height: 48,
    paddingHorizontal: spacing.lg,
  },
  large: {
    height: 56,
    paddingHorizontal: spacing.xl,
  },
  
  // 全宽样式
  fullWidth: {
    width: '100%',
  },
  
  // 禁用样式
  disabled: {
    backgroundColor: colors.gray300,
    ...shadows.none,
  },
  
  // 内容容器
  content: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  
  // 文本样式
  text: {
    fontFamily: typography.fontFamily.medium,
    fontWeight: '500' as const,
    textAlign: 'center',
  },
  
  // 变体文本样式
  primaryText: {
    color: colors.white,
    fontSize: typography.fontSize.base,
  },
  secondaryText: {
    color: colors.white,
    fontSize: typography.fontSize.base,
  },
  outlineText: {
    color: colors.primary,
    fontSize: typography.fontSize.base,
  },
  ghostText: {
    color: colors.primary,
    fontSize: typography.fontSize.base,
  },
  dangerText: {
    color: colors.white,
    fontSize: typography.fontSize.base,
  },
  
  // 尺寸文本样式
  smallText: {
    fontSize: typography.fontSize.sm,
  },
  mediumText: {
    fontSize: typography.fontSize.base,
  },
  largeText: {
    fontSize: typography.fontSize.lg,
  },
  
  // 禁用文本样式
  disabledText: {
    color: colors.gray500,
  },
  
  // 图标样式
  leftIcon: {
    marginRight: spacing.xs,
  },
  rightIcon: {
    marginLeft: spacing.xs,
  },
  
  // 加载样式
  loading: {
    marginHorizontal: spacing.xs,
  },
});

export default Button; 