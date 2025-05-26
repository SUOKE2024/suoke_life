import React from 'react';
import {
  TouchableOpacity,
  Text,
  View,
  StyleSheet,
  TouchableOpacityProps,
} from 'react-native';
import { colors, spacing, fonts, borderRadius, shadows } from '../../constants/theme';

interface AuthButtonProps extends TouchableOpacityProps {
  title: string;
  variant?: 'primary' | 'secondary' | 'outline';
  loading?: boolean;
  icon?: string;
  size?: 'small' | 'medium' | 'large';
}

export const AuthButton: React.FC<AuthButtonProps> = ({
  title,
  variant = 'primary',
  loading = false,
  icon,
  size = 'large',
  disabled,
  style,
  ...props
}) => {
  const getButtonStyle = () => {
    const baseStyle: any[] = [styles.button];
    
    // 添加尺寸样式
    if (size === 'small') baseStyle.push(styles.button_small);
    else if (size === 'medium') baseStyle.push(styles.button_medium);
    else baseStyle.push(styles.button_large);
    
    // 添加变体样式
    if (variant === 'primary') baseStyle.push(styles.buttonPrimary);
    else if (variant === 'secondary') baseStyle.push(styles.buttonSecondary);
    else if (variant === 'outline') baseStyle.push(styles.buttonOutline);
    
    // 添加禁用样式
    if (disabled || loading) baseStyle.push(styles.buttonDisabled);
    
    return baseStyle;
  };

  const getTextStyle = () => {
    const baseStyle: any[] = [styles.buttonText];
    
    // 添加尺寸样式
    if (size === 'small') baseStyle.push(styles.buttonText_small);
    else if (size === 'medium') baseStyle.push(styles.buttonText_medium);
    else baseStyle.push(styles.buttonText_large);
    
    // 添加变体样式
    if (variant === 'primary') baseStyle.push(styles.buttonTextPrimary);
    else if (variant === 'secondary') baseStyle.push(styles.buttonTextSecondary);
    else if (variant === 'outline') baseStyle.push(styles.buttonTextOutline);
    
    return baseStyle;
  };

  return (
    <TouchableOpacity
      style={[getButtonStyle(), style]}
      disabled={disabled || loading}
      activeOpacity={0.8}
      {...props}
    >
      {icon && <Text style={styles.buttonIcon}>{icon}</Text>}
      <Text style={getTextStyle()}>
        {loading ? '加载中...' : title}
      </Text>
      {loading && <View style={styles.loadingOverlay} />}
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  button: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: borderRadius.lg,
    position: 'relative',
    overflow: 'hidden',
  },
  button_small: {
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
  },
  button_medium: {
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.lg,
  },
  button_large: {
    paddingVertical: spacing.lg,
    paddingHorizontal: spacing.xl,
  },
  buttonPrimary: {
    backgroundColor: colors.primary,
    ...shadows.md,
  },
  buttonSecondary: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
  },
  buttonOutline: {
    backgroundColor: 'transparent',
    borderWidth: 2,
    borderColor: colors.primary,
  },
  buttonDisabled: {
    opacity: 0.7,
  },
  buttonText: {
    fontWeight: 'bold',
    textAlign: 'center',
  },
  buttonText_small: {
    fontSize: fonts.size.sm,
  },
  buttonText_medium: {
    fontSize: fonts.size.md,
  },
  buttonText_large: {
    fontSize: fonts.size.lg,
  },
  buttonTextPrimary: {
    color: colors.white,
  },
  buttonTextSecondary: {
    color: colors.text,
  },
  buttonTextOutline: {
    color: colors.primary,
  },
  buttonIcon: {
    fontSize: 20,
    marginRight: spacing.sm,
  },
  loadingOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    borderRadius: borderRadius.lg,
  },
}); 