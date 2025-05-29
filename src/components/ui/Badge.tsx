/**
 * 索克生活 - Badge组件
 * 徽章组件，用于显示状态、数量等信息
 */

import React from 'react';
import { View, StyleSheet, ViewStyle } from 'react-native';
import { colors, typography, spacing, borderRadius } from '../../constants/theme';
import Text from './Text';

export interface BadgeProps {
  // 内容
  children?: React.ReactNode;
  count?: number;
  
  // 样式
  variant?: 'default' | 'primary' | 'secondary' | 'success' | 'warning' | 'error';
  size?: 'small' | 'medium' | 'large';
  
  // 形状
  shape?: 'circle' | 'rounded' | 'square';
  
  // 状态
  dot?: boolean;
  showZero?: boolean;
  
  // 自定义样式
  style?: ViewStyle;
  
  // 其他属性
  testID?: string;
}

const Badge: React.FC<BadgeProps> = ({
  children,
  count,
  variant = 'default',
  size = 'medium',
  shape = 'rounded',
  dot = false,
  showZero = false,
  style,
  testID,
}) => {
  // 如果是数字且为0且不显示0，则不渲染
  if (count !== undefined && count === 0 && !showZero) {
    return null;
  }

  // 如果是点状徽章
  if (dot) {
    return (
      <View
        style={[
          styles.base,
          styles.dot,
          styles[variant],
          style,
        ]}
        testID={testID}
      />
    );
  }

  const badgeStyle = [
    styles.base,
    styles[variant],
    styles[size],
    styles[shape],
    style,
  ].filter(Boolean) as ViewStyle[];

  const getDisplayText = () => {
    if (count !== undefined) {
      return count > 99 ? '99+' : count.toString();
    }
    return children;
  };

  return (
    <View style={badgeStyle} testID={testID}>
      <Text
        style={{
          ...styles.text,
          ...styles[`${variant}Text`],
          ...styles[`${size}Text`],
        }}
      >
        {getDisplayText()}
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  base: {
    alignItems: 'center',
    justifyContent: 'center',
    minWidth: 20,
    paddingHorizontal: spacing.xs,
  },
  
  // 变体样式
  default: {
    backgroundColor: colors.gray500,
  },
  primary: {
    backgroundColor: colors.primary,
  },
  secondary: {
    backgroundColor: colors.secondary,
  },
  success: {
    backgroundColor: colors.success,
  },
  warning: {
    backgroundColor: colors.warning,
  },
  error: {
    backgroundColor: colors.error,
  },
  
  // 尺寸样式
  small: {
    height: 16,
    minWidth: 16,
    paddingHorizontal: 4,
  },
  medium: {
    height: 20,
    minWidth: 20,
    paddingHorizontal: spacing.xs,
  },
  large: {
    height: 24,
    minWidth: 24,
    paddingHorizontal: spacing.sm,
  },
  
  // 形状样式
  circle: {
    borderRadius: 50,
  },
  rounded: {
    borderRadius: borderRadius.sm,
  },
  square: {
    borderRadius: 0,
  },
  
  // 点状徽章
  dot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    minWidth: 8,
    paddingHorizontal: 0,
  },
  
  // 文本样式
  text: {
    fontFamily: typography.fontFamily.medium,
    fontWeight: '600',
    textAlign: 'center',
  },
  
  // 变体文本样式
  defaultText: {
    color: colors.white,
  },
  primaryText: {
    color: colors.white,
  },
  secondaryText: {
    color: colors.white,
  },
  successText: {
    color: colors.white,
  },
  warningText: {
    color: colors.white,
  },
  errorText: {
    color: colors.white,
  },
  
  // 尺寸文本样式
  smallText: {
    fontSize: 10,
    lineHeight: 12,
  },
  mediumText: {
    fontSize: typography.fontSize.xs,
    lineHeight: 14,
  },
  largeText: {
    fontSize: typography.fontSize.sm,
    lineHeight: 16,
  },
});

export default Badge; 