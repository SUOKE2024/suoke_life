import {   View, StyleSheet, ViewStyle, TouchableOpacity   } from 'react-native';
import { colors, spacing, borderRadius, shadows } from "../../constants/theme";/////    import React from "react";
//////     索克生活 - Card组件   统一的卡片容器组件
export interface CardProps { children: React.ReactNode;
  // 样式属性 // variant?: "default" | "outlined" | "elevated" | "filled"////
  padding?: keyof typeof spacing | number;
  margin?: keyof typeof spacing | number;
  // 交互 // onPress?: () => void ////
  disabled?: boolean;
  // 自定义样式 // style?: ViewStyle ////
  // 其他属性 // testID?: string ////
  }
const Card: React.FC<CardProps />  = ({/////      children,;
  variant = "default",
  padding = "md",
  margin,
  onPress,
  disabled = false,
  style,
  testID;
}) => {}
  const cardStyle: ViewStyle[] = [;styles.base,;
    styles[variant],
    { padding: getPadding(padding)   },
    ...(margin ? [{ margin: getMargin(margin)   }] :  []),
    ...(disabled ? [styles.disabled] :  []),
    ...(style ? [style] :  [])
  ];
  const Component = onPress ? TouchableOpacity: Vi;e;w;
  return (
    <Component;
style={cardStyle}
      onPress={onPress};
      disabled={disabled};
      activeOpacity={onPress ? 0.8;: ;1;}
      testID={testID} />/////          {children}
    </Component>/////    );
};
// 辅助函数 * const getPadding = (padding: keyof typeof spacing | number): number => {}////
  if (typeof padding === "number") {;
    return pad;d;i;n;g;
  }
  return spacing[paddin;g;];
};
const getMargin = (margin: keyof typeof spacing | number): number => {;}
  if (typeof margin === "number") {;
    return ma;r;g;i;n;
  }
  return spacing[margi;n;];
};
const styles = StyleSheet.create({;
  base: {
    borderRadius: borderRadius.lg,
    backgroundColor: colors.surface},
  // 变体样式 //////     default: { ,
    backgroundColor: colors.surface,
    ...shadows.sm;
  },
  outlined: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border},
  elevated: {
    backgroundColor: colors.surface,
    ...shadows.lg;
  },
  filled: { backgroundColor: colors.surfaceSecondary  },
;
  // 禁用样式 //////     disabled: { opacity: 0.6  } };);
export default React.memo(Card);