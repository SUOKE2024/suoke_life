import React from 'react';
import { Text as RNText, StyleSheet, TextStyle } from 'react-native';

// 索克生活 - Text组件 统一的文本组件，支持多种样式和语义化标签

export interface TextProps {
  children: React.ReactNode;
  variant?: 
    | "h1"
    | "h2"
    | "h3"
    | "h4"
    | "h5"
    | "h6"
    | "body1"
    | "body2"
    | "caption"
    | "overline"
    | "button"
    | "link";
  color?: 
    | "primary"
    | "secondary"
    | "onSurface"
    | "onSurfaceVariant"
    | "onPrimary"
    | "onSecondary"
    | "error"
    | "success"
    | "warning"
    | "info"
    | string;
  size?: 
    | "xs"
    | "sm"
    | "base"
    | "lg"
    | "xl"
    | "2xl"
    | "3xl"
    | "4xl"
    | "5xl"
    | number;
  weight?: "300" | "400" | "500" | "600" | "700";
  align?: "left" | "center" | "right" | "justify";
  disabled?: boolean;
  selectable?: boolean;
  numberOfLines?: number;
  ellipsizeMode?: "head" | "middle" | "tail" | "clip";
  accessibilityLabel?: string;
  accessibilityHint?: string;
  style?: TextStyle;
  testID?: string;
  onPress?: () => void;
  onLongPress?: () => void;
}

const Text: React.FC<TextProps> = ({
  children,
  variant = 'body1',
  color = 'onSurface',
  size,
  weight,
  align = 'left',
  disabled = false,
  selectable = false,
  numberOfLines,
  ellipsizeMode = 'tail',
  accessibilityLabel,
  accessibilityHint,
  style,
  testID,
  onPress,
  onLongPress,
}) => {
  const getVariantStyle = (): TextStyle => {
    const variantStyles: Record<string, TextStyle> = {
      h1: {
        fontSize: 32,
        fontWeight: "700",
        lineHeight: 40,
        color: '#000000',
      },
      h2: {
        fontSize: 28,
        fontWeight: "700",
        lineHeight: 36,
        color: '#000000',
      },
      h3: {
        fontSize: 24,
        fontWeight: "600",
        lineHeight: 32,
        color: '#000000',
      },
      h4: {
        fontSize: 20,
        fontWeight: "600",
        lineHeight: 28,
        color: '#000000',
      },
      h5: {
        fontSize: 18,
        fontWeight: "600",
        lineHeight: 26,
        color: '#000000',
      },
      h6: {
        fontSize: 16,
        fontWeight: "600",
        lineHeight: 24,
        color: '#000000',
      },
      body1: {
        fontSize: 16,
        fontWeight: "400",
        lineHeight: 24,
        color: '#000000',
      },
      body2: {
        fontSize: 14,
        fontWeight: "400",
        lineHeight: 20,
        color: '#666666',
      },
      caption: {
        fontSize: 12,
        fontWeight: "400",
        lineHeight: 16,
        color: '#666666',
      },
      overline: {
        fontSize: 12,
        fontWeight: "500",
        lineHeight: 16,
        color: '#666666',
        textTransform: "uppercase",
        letterSpacing: 0.5,
      },
      button: {
        fontSize: 16,
        fontWeight: "500",
        lineHeight: 24,
        color: '#35bb78', // 索克绿
      },
      link: {
        fontSize: 16,
        fontWeight: "400",
        lineHeight: 24,
        color: '#35bb78', // 索克绿
        textDecorationLine: "underline",
      },
    };
    return variantStyles[variant] || variantStyles.body1;
  };

  const getColor = (): string => {
    if (!color) {
      return getVariantStyle().color as string;
    }

    const themeColors: Record<string, string> = {
      primary: '#35bb78', // 索克绿
      secondary: '#ff6800', // 索克橙
      onSurface: '#000000',
      onSurfaceVariant: '#666666',
      onPrimary: '#FFFFFF',
      onSecondary: '#FFFFFF',
      error: '#F44336',
      success: '#4CAF50',
      warning: '#FF9800',
      info: '#2196F3',
    };
    return themeColors[color] || color;
  };

  const getFontSize = (): number => {
    if (!size) {
      return getVariantStyle().fontSize as number;
    }

    if (typeof size === "number") {
      return size;
    }

    const fontSizes: Record<string, number> = {
      xs: 12,
      sm: 14,
      base: 16,
      lg: 18,
      xl: 20,
      "2xl": 24,
      "3xl": 30,
      "4xl": 36,
      "5xl": 48,
    };

    return fontSizes[size] || 16;
  };

  const textStyle: TextStyle = {
    ...styles.base,
    ...getVariantStyle(),
    color: getColor(),
    fontSize: getFontSize(),
    fontWeight: weight || getVariantStyle().fontWeight,
    textAlign: align,
    opacity: disabled ? 0.5 : 1,
    ...style,
  };

  return (
    <RNText
      style={textStyle}
      selectable={selectable}
      numberOfLines={numberOfLines}
      ellipsizeMode={ellipsizeMode}
      accessibilityLabel={accessibilityLabel || (typeof children === 'string' ? children : undefined)}
      accessibilityHint={accessibilityHint}
      testID={testID}
      onPress={onPress}
      onLongPress={onLongPress}
    >
      {children}
    </RNText>
  );
};

const styles = StyleSheet.create({
  base: {
    fontFamily: 'System',
  },
});

export default Text;