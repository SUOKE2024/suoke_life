import { useTheme } from "../../contexts/ThemeContext";
import { useAccessibility } from "../../contexts/AccessibilityContext";
import { responsive, typography } from "../../utils/responsive";
import React from "react";


  Text as RNText,
  StyleSheet,
  TextStyle,
  AccessibilityRole,
} from "react-native";

/**
 * 索克生活 - Text组件
 * 统一的文本组件，支持多种样式和语义化标签
 */

export interface TextProps {
  children: React.ReactNode;

  // 语义化标签
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

  // 样式属性
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

  // 状态
  disabled?: boolean;
  selectable?: boolean;

  // 行为
  numberOfLines?: number;
  ellipsizeMode?: "head" | "middle" | "tail" | "clip";

  // 无障碍属性
  accessibilityLabel?: string;
  accessibilityHint?: string;
  accessibilityRole?: AccessibilityRole;

  // 自定义样式
  style?: TextStyle;

  // 其他属性
  testID?: string;
  onPress?: () => void;
  onLongPress?: () => void;
}

const Text: React.FC<TextProps> = ({
  children,
  variant = "body1",
  color,
  size,
  weight,
  align = "left",
  disabled = false,
  selectable = false,
  numberOfLines,
  ellipsizeMode = "tail",
  accessibilityLabel,
  accessibilityHint,
  accessibilityRole,
  style,
  testID,
  onPress,
  onLongPress,
}) => {
  const { theme } = useTheme();
  const { config } = useAccessibility();

  // 获取变体样式
  const getVariantStyle = (): TextStyle => {
    const variantStyles: Record<string, TextStyle> = {
      h1: {
        fontSize: responsive.fontSize(theme.typography.fontSize["5xl"]),
        fontWeight: "700" as const,
        lineHeight: responsive.fontSize(
          theme.typography.fontSize["5xl"] * theme.typography.lineHeight.tight
        ),
        color: theme.colors.onSurface,
      },
      h2: {
        fontSize: responsive.fontSize(theme.typography.fontSize["4xl"]),
        fontWeight: "700" as const,
        lineHeight: responsive.fontSize(
          theme.typography.fontSize["4xl"] * theme.typography.lineHeight.tight
        ),
        color: theme.colors.onSurface,
      },
      h3: {
        fontSize: responsive.fontSize(theme.typography.fontSize["3xl"]),
        fontWeight: "600" as const,
        lineHeight: responsive.fontSize(
          theme.typography.fontSize["3xl"] * theme.typography.lineHeight.tight
        ),
        color: theme.colors.onSurface,
      },
      h4: {
        fontSize: responsive.fontSize(theme.typography.fontSize["2xl"]),
        fontWeight: "600" as const,
        lineHeight: responsive.fontSize(
          theme.typography.fontSize["2xl"] * theme.typography.lineHeight.normal
        ),
        color: theme.colors.onSurface,
      },
      h5: {
        fontSize: responsive.fontSize(theme.typography.fontSize.xl),
        fontWeight: "600" as const,
        lineHeight: responsive.fontSize(
          theme.typography.fontSize.xl * theme.typography.lineHeight.normal
        ),
        color: theme.colors.onSurface,
      },
      h6: {
        fontSize: responsive.fontSize(theme.typography.fontSize.lg),
        fontWeight: "600" as const,
        lineHeight: responsive.fontSize(
          theme.typography.fontSize.lg * theme.typography.lineHeight.normal
        ),
        color: theme.colors.onSurface,
      },
      body1: {
        fontSize: responsive.fontSize(theme.typography.fontSize.base),
        fontWeight: "400" as const,
        lineHeight: responsive.fontSize(
          theme.typography.fontSize.base * theme.typography.lineHeight.normal
        ),
        color: theme.colors.onSurface,
      },
      body2: {
        fontSize: responsive.fontSize(theme.typography.fontSize.sm),
        fontWeight: "400" as const,
        lineHeight: responsive.fontSize(
          theme.typography.fontSize.sm * theme.typography.lineHeight.normal
        ),
        color: theme.colors.onSurfaceVariant,
      },
      caption: {
        fontSize: responsive.fontSize(theme.typography.fontSize.xs),
        fontWeight: "400" as const,
        lineHeight: responsive.fontSize(
          theme.typography.fontSize.xs * theme.typography.lineHeight.normal
        ),
        color: theme.colors.onSurfaceVariant,
      },
      overline: {
        fontSize: responsive.fontSize(theme.typography.fontSize.xs),
        fontWeight: "500" as const,
        lineHeight: responsive.fontSize(
          theme.typography.fontSize.xs * theme.typography.lineHeight.normal
        ),
        color: theme.colors.onSurfaceVariant,
        textTransform: "uppercase",
        letterSpacing: 0.5,
      },
      button: {
        fontSize: responsive.fontSize(theme.typography.fontSize.base),
        fontWeight: "500" as const,
        lineHeight: responsive.fontSize(
          theme.typography.fontSize.base * theme.typography.lineHeight.normal
        ),
        color: theme.colors.primary,
      },
      link: {
        fontSize: responsive.fontSize(theme.typography.fontSize.base),
        fontWeight: "400" as const,
        lineHeight: responsive.fontSize(
          theme.typography.fontSize.base * theme.typography.lineHeight.normal
        ),
        color: theme.colors.primary,
        textDecorationLine: "underline",
      },
    };

    return variantStyles[variant] || variantStyles.body1;
  };

  // 获取颜色
  const getColor = (): string => {
    if (!color) {
      return getVariantStyle().color as string;
    }

    // 主题颜色
    const themeColors: Record<string, string> = {
      primary: theme.colors.primary,
      secondary: theme.colors.secondary,
      onSurface: theme.colors.onSurface,
      onSurfaceVariant: theme.colors.onSurfaceVariant,
      onPrimary: theme.colors.onPrimary,
      onSecondary: theme.colors.onSecondary,
      error: theme.colors.error,
      success: theme.colors.success,
      warning: theme.colors.warning,
      info: theme.colors.info,
    };

    return themeColors[color] || color;
  };

  // 获取字体大小
  const getFontSize = (): number => {
    if (!size) {
      return getVariantStyle().fontSize as number;
    }

    if (typeof size === "number") {
      return responsive.fontSize(size);
    }

    return responsive.fontSize(theme.typography.fontSize[size]);
  };

  // 应用无障碍字体缩放
  const getAccessibilityFontSize = (baseFontSize: number): number => {
    if (config.largeFontEnabled) {
      return typography.getScaledFontSize(baseFontSize * config.fontScale);
    }
    return baseFontSize;
  };

  // 构建样式
  const textStyle: TextStyle = {
    ...styles.base,
    ...getVariantStyle(),
    color: getColor(),
    fontSize: getAccessibilityFontSize(getFontSize()),
    fontWeight: weight || getVariantStyle().fontWeight,
    textAlign: align,
    ...(disabled && styles.disabled),
  };

  // 生成无障碍标签
  const generateAccessibilityLabel = (): string => {
    if (accessibilityLabel) {
      return accessibilityLabel;
    }

    // 对于标题，添加级别信息
    if (variant.startsWith("h")) {
      const level = variant.charAt(1);
      return `${children} 标题级别${level}`;
    }

    return typeof children === "string" ? children : "";
  };

  // 确定无障碍角色
  const getAccessibilityRole = (): AccessibilityRole | undefined => {
    if (accessibilityRole) {
      return accessibilityRole;
    }

    if (variant.startsWith("h")) {
      return "header";
    }
    if (variant === "link") {
      return "link";
    }
    if (variant === "button") {
      return "button";
    }
    if (onPress) {
      return "button";
    }

    return "text";
  };

  return (
    <RNText
      style={[textStyle, style]}
      numberOfLines={numberOfLines}
      ellipsizeMode={ellipsizeMode}
      selectable={selectable}
      accessible={true}
      accessibilityLabel={generateAccessibilityLabel()}
      accessibilityHint={accessibilityHint}
      accessibilityRole={getAccessibilityRole()}
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
    fontFamily: "System", // 使用系统字体
  },
  disabled: {
    opacity: 0.5,
  },
});

export default Text;
