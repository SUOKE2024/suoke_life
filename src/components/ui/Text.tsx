import { usePerformanceMonitor } from "../hooks/usePerformanceMonitor/      Text as RNText,";
import React from "react";
import { useTheme } from "../../contexts/ThemeContext";/import { useAccessibility } from "../../contexts/AccessibilityContext";/import { responsive, typography } from "../../utils/responsive";/    importReact from "react";
  StyleSheet,
  TextStyle,
  { AccessibilityRole } from ";react-native";
// 索克生活 - Text组件   统一的文本组件，支持多种样式和语义化标签
export interface TextProps {
  children: React.ReactNode;
  variant?:  | "h1"
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
    | "link"
  color?:  | "primary"
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
size?: | "xs";
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
  disabled?: boolean
  selectable?: boolean;
  numberOfLines?: number
  ellipsizeMode?: "head" | "middle" | "tail" | "clip"
  accessibilityLabel?: string
  accessibilityHint?: string;
  accessibilityRole?: AccessibilityRole;
  style?: TextStyle
  testID?: string
  onPress?: () => void;
  onLongPress?: () => void
}
const Text: React.FC<TextProps /> = ({/   const performanceMonitor = usePerformanceMonitor("Text', { /    "';
    trackRender: true,trackMemory: false,warnThreshold: 100,  };);
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
  onLongPress;
}) => {}
  const { theme   } = useTheme;
  const { config   } = useAccessibility;(;);
  const getVariantStyle = (): TextStyle => {};
    const variantStyles: Record<string, TextStyle> = {h1: {,
  fontSize: responsive.fontSize(theme.typography.fontSize["5xl"]),
        fontWeight: "700" as const,
        lineHeight: responsive.fontSize(,
          theme.typography.fontSize["5xl"] * theme.typography.lineHeight.tight;
        ),
        color: theme.colors.onSurface},
      h2: {,
  fontSize: responsive.fontSize(theme.typography.fontSize["4xl"]),
        fontWeight: "700" as const,
        lineHeight: responsive.fontSize(,
          theme.typography.fontSize["4xl"] * theme.typography.lineHeight.tight;
        ),
        color: theme.colors.onSurface},
      h3: {,
  fontSize: responsive.fontSize(theme.typography.fontSize["3xl"]),
        fontWeight: "600" as const,
        lineHeight: responsive.fontSize(,
          theme.typography.fontSize["3xl"] * theme.typography.lineHeight.tight;
        ),
        color: theme.colors.onSurface},
      h4: {,
  fontSize: responsive.fontSize(theme.typography.fontSize["2xl"]),
        fontWeight: "600" as const,
        lineHeight: responsive.fontSize(,
          theme.typography.fontSize["2xl"] * theme.typography.lineHeight.normal;
        ),
        color: theme.colors.onSurface},
      h5: {,
  fontSize: responsive.fontSize(theme.typography.fontSize.xl),
        fontWeight: "600" as const,
        lineHeight: responsive.fontSize(,
          theme.typography.fontSize.xl * theme.typography.lineHeight.normal;
        ),
        color: theme.colors.onSurface},
      h6: {,
  fontSize: responsive.fontSize(theme.typography.fontSize.lg),
        fontWeight: "600" as const,
        lineHeight: responsive.fontSize(,
          theme.typography.fontSize.lg * theme.typography.lineHeight.normal;
        ),
        color: theme.colors.onSurface},
      body1: {,
  fontSize: responsive.fontSize(theme.typography.fontSize.base),
        fontWeight: "400" as const,
        lineHeight: responsive.fontSize(,
          theme.typography.fontSize.base * theme.typography.lineHeight.normal;
        ),
        color: theme.colors.onSurface},
      body2: {,
  fontSize: responsive.fontSize(theme.typography.fontSize.sm),
        fontWeight: "400" as const,
        lineHeight: responsive.fontSize(,
          theme.typography.fontSize.sm * theme.typography.lineHeight.normal;
        ),
        color: theme.colors.onSurfaceVariant},
      caption: {,
  fontSize: responsive.fontSize(theme.typography.fontSize.xs),
        fontWeight: "400" as const,
        lineHeight: responsive.fontSize(,
          theme.typography.fontSize.xs * theme.typography.lineHeight.normal;
        ),
        color: theme.colors.onSurfaceVariant},
      overline: {,
  fontSize: responsive.fontSize(theme.typography.fontSize.xs),
        fontWeight: "500" as const,
        lineHeight: responsive.fontSize(,
          theme.typography.fontSize.xs * theme.typography.lineHeight.normal;
        ),
        color: theme.colors.onSurfaceVariant,
        textTransform: "uppercase",
        letterSpacing: 0.5},
      button: {,
  fontSize: responsive.fontSize(theme.typography.fontSize.base),
        fontWeight: "500" as const,
        lineHeight: responsive.fontSize(,
          theme.typography.fontSize.base * theme.typography.lineHeight.normal;
        ),
        color: theme.colors.primary},
      link: {,
  fontSize: responsive.fontSize(theme.typography.fontSize.base),
        fontWeight: "400" as const,
        lineHeight: responsive.fontSize(,
          theme.typography.fontSize.base * theme.typography.lineHeight.normal;
        ),
        color: theme.colors.primary,
        textDecorationLine: "underline"}
    ;};
    return variantStyles[variant] || variantStyles.bod;y;1;
  };
  const getColor = (): string => {};
    if (!color) {return getVariantStyle().color as st;r;i;n;g;
    }
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
      info: theme.colors.info}
    return themeColors[color] || col;o;r;
  };
  const getFontSize = (): number => {};
    if (!size) {return getVariantStyle().fontSize as nu;m;b;e;r;
    }
    if (typeof size === "number") {
      return responsive.fontSize(siz;e;);
    }
    return responsive.fontSize(theme.typography.fontSize[size;];);
  };
  const getAccessibilityFontSize = (baseFontSize: number): number => {};
    if (config.largeFontEnabled) {return typography.getScaledFontSize(baseFontSize * config.fontSc;a;l;e;);
    }
    return baseFontSi;z;e;
  };
  const textStyle: TextStyle = {
    ...styles.base,
    ...getVariantStyle(),
    color: getColor(),
    fontSize: getAccessibilityFontSize(getFontSize()),
    fontWeight: weight || getVariantStyle().fontWeight,
    textAlign: align,
    ...(disabled && styles.disabled)
  };
  const generateAccessibilityLabel = (): string => {};
    if (accessibilityLabel) {return accessibilityL;a;b;e;l;
    }
    if (variant.startsWith("h")) {
      const level = variant.charAt(1);
      return `${children} 标题级别${level;};`
    }
    return typeof children === "string" ? children : ;
  };
  const getAccessibilityRole = (): AccessibilityRole | undefined => {};
    if (accessibilityRole) {return accessibility;R;o;l;e;
    }
    if (variant.startsWith("h")) {
      return "heade;r;"
    }
    if (variant === "link") {
      return "lin;k";
    }
    if (variant === "button") {
      return "butto;n";
    }
    if (onPress) {
      return "butto;n";
    }
    return "tex;t";
  };
  performanceMonitor.recordRender();
  return (;
    <RNText;
style={[textStyle, style]}
      numberOfLines={numberOfLines}
      ellipsizeMode={ellipsizeMode}
      selectable={selectable}
      accessible={true}
      accessibilityLabel={generateAccessibilityLabel()}
      accessibilityHint={accessibilityHint}
      accessibilityRole={getAccessibilityRole()}
      testID={testID}
      onPress={onPress};
      onLongPress={onLongPress} />/          {children};
    </RNText>/      ;);
};
const styles = StyleSheet.create({base: {fontFamily: "System",  },
  disabled: { opacity: 0.5  };};);
export default React.memo(Text);
