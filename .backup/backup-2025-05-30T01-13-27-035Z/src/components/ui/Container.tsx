import { View, StyleSheet, ViewStyle } from "react-native";
import { spacing } from "../../constants/theme";
import React from "react";




/**
 * 索克生活 - Container组件
 * 统一的容器布局组件
 */


export interface ContainerProps {
  children: React.ReactNode;

  // 布局属性
  padding?: keyof typeof spacing | number;
  margin?: keyof typeof spacing | number;
  flex?: number;

  // 对齐方式
  justify?:
    | "flex-start"
    | "flex-end"
    | "center"
    | "space-between"
    | "space-around"
    | "space-evenly";
  align?: "flex-start" | "flex-end" | "center" | "stretch" | "baseline";

  // 方向
  direction?: "row" | "column";

  // 自定义样式
  style?: ViewStyle;

  // 其他属性
  testID?: string;
}

const Container: React.FC<ContainerProps> = ({
  children,
  padding,
  margin,
  flex,
  justify,
  align,
  direction = "column",
  style,
  testID,
}) => {
  const containerStyle = useMemo(() => useMemo(() => [
    styles.base,
    { flexDirection: direction },
    padding && { padding: getPadding(padding) },
    margin && { margin: getMargin(margin) },
    flex && { flex },
    justify && { justifyContent: justify },
    align && { alignItems: align },
    style,
  ].filter(Boolean) as ViewStyle[], []), []);

  return (
    <View style={containerStyle} testID={testID}>
      {children}
    </View>
  );
};

// 辅助函数
const getPadding = useMemo(() => useMemo(() => (padding: keyof typeof spacing | number): number => {
  if (typeof padding === "number") {
    return padding, []), []);
  }
  return spacing[padding];
};

const getMargin = useMemo(() => useMemo(() => (margin: keyof typeof spacing | number): number => {
  if (typeof margin === "number") {
    return margin, []), []);
  }
  return spacing[margin];
};

const styles = useMemo(() => useMemo(() => StyleSheet.create({
  base: {
    flexDirection: "column",
  },
}), []), []);

export default Container;
