/**
 * 索克生活 - Text组件
 * 统一的文本组件，支持多种样式和语义化标签
 */

import React from 'react';
import { Text as RNText, StyleSheet, TextStyle } from 'react-native';
import { colors, typography } from '../../constants/theme';

export interface TextProps {
  children: React.ReactNode;
  
  // 语义化标签
  variant?: 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6' | 'body1' | 'body2' | 'caption' | 'overline';
  
  // 样式属性
  color?: keyof typeof colors | string;
  size?: keyof typeof typography.fontSize | number;
  weight?: '300' | '400' | '500' | '600' | '700';
  align?: 'left' | 'center' | 'right' | 'justify';
  
  // 状态
  disabled?: boolean;
  
  // 行为
  numberOfLines?: number;
  ellipsizeMode?: 'head' | 'middle' | 'tail' | 'clip';
  
  // 自定义样式
  style?: TextStyle;
  
  // 其他属性
  testID?: string;
  onPress?: () => void;
}

const Text: React.FC<TextProps> = ({
  children,
  variant = 'body1',
  color,
  size,
  weight,
  align = 'left',
  disabled = false,
  numberOfLines,
  ellipsizeMode = 'tail',
  style,
  testID,
  onPress,
}) => {
  const textStyle = [
    styles.base,
    styles[variant],
    color && { color: getColor(color) },
    size && { fontSize: getSize(size) },
    weight && { fontWeight: weight },
    align && { textAlign: align },
    disabled && styles.disabled,
    style,
  ].filter(Boolean);

  return (
    <RNText
      style={textStyle as TextStyle[]}
      numberOfLines={numberOfLines}
      ellipsizeMode={ellipsizeMode}
      testID={testID}
      onPress={onPress}
    >
      {children}
    </RNText>
  );
};

// 辅助函数
const getColor = (color: string): string => {
  if (color in colors) {
    return (colors as any)[color];
  }
  return color;
};

const getSize = (size: keyof typeof typography.fontSize | number): number => {
  if (typeof size === 'number') {
    return size;
  }
  return typography.fontSize[size];
};

const styles = StyleSheet.create({
  base: {
    fontFamily: typography.fontFamily.regular,
    color: colors.textPrimary,
  },
  
  // 标题样式
  h1: {
    fontSize: typography.fontSize['5xl'],
    fontWeight: '700',
    lineHeight: typography.fontSize['5xl'] * typography.lineHeight.tight,
    color: colors.textPrimary,
  },
  h2: {
    fontSize: typography.fontSize['4xl'],
    fontWeight: '700',
    lineHeight: typography.fontSize['4xl'] * typography.lineHeight.tight,
    color: colors.textPrimary,
  },
  h3: {
    fontSize: typography.fontSize['3xl'],
    fontWeight: '600',
    lineHeight: typography.fontSize['3xl'] * typography.lineHeight.tight,
    color: colors.textPrimary,
  },
  h4: {
    fontSize: typography.fontSize['2xl'],
    fontWeight: '600',
    lineHeight: typography.fontSize['2xl'] * typography.lineHeight.normal,
    color: colors.textPrimary,
  },
  h5: {
    fontSize: typography.fontSize.xl,
    fontWeight: '600',
    lineHeight: typography.fontSize.xl * typography.lineHeight.normal,
    color: colors.textPrimary,
  },
  h6: {
    fontSize: typography.fontSize.lg,
    fontWeight: '600',
    lineHeight: typography.fontSize.lg * typography.lineHeight.normal,
    color: colors.textPrimary,
  },
  
  // 正文样式
  body1: {
    fontSize: typography.fontSize.base,
    fontWeight: '400',
    lineHeight: typography.fontSize.base * typography.lineHeight.normal,
    color: colors.textPrimary,
  },
  body2: {
    fontSize: typography.fontSize.sm,
    fontWeight: '400',
    lineHeight: typography.fontSize.sm * typography.lineHeight.normal,
    color: colors.textSecondary,
  },
  
  // 辅助文本样式
  caption: {
    fontSize: typography.fontSize.xs,
    fontWeight: '400',
    lineHeight: typography.fontSize.xs * typography.lineHeight.normal,
    color: colors.textTertiary,
  },
  overline: {
    fontSize: typography.fontSize.xs,
    fontWeight: '500',
    lineHeight: typography.fontSize.xs * typography.lineHeight.normal,
    color: colors.textSecondary,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  
  // 禁用样式
  disabled: {
    color: colors.gray400,
  },
});

export default Text; 