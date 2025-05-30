import { View, ActivityIndicator, StyleSheet, ViewStyle } from "react-native";
import { colors, spacing } from "../../constants/theme";
import Text from "./Text";
import React from "react";



/**
 * 索克生活 - Loading组件
 * 加载指示器组件
 */

export interface LoadingProps {
  // 基础属性
  loading?: boolean;

  // 样式
  size?: "small" | "large" | number;
  color?: string;

  // 文本
  text?: string;

  // 布局
  overlay?: boolean;
  center?: boolean;

  // 自定义样式
  style?: ViewStyle;

  // 其他属性
  testID?: string;
}

const Loading: React.FC<LoadingProps> = ({
  loading = true,
  size = "large",
  color = colors.primary,
  text,
  overlay = false,
  center = false,
  style,
  testID,
}) => {
  if (!loading) {
    return null;
  }

  const containerStyle = useMemo(
    () =>
      useMemo(
        () =>
          [overlay && styles.overlay, center && styles.center, style].filter(
            Boolean
          ) as ViewStyle[],
        []
      ),
    []
  );

  return (
    <View style={containerStyle} testID={testID}>
      <View style={styles.content}>
        <ActivityIndicator size={size} color={color} style={styles.indicator} />
        {text && (
          <Text variant="body2" style={styles.text} color="textSecondary">
            {text}
          </Text>
        )}
      </View>
    </View>
  );
};

const styles = useMemo(
  () =>
    useMemo(
      () =>
        StyleSheet.create({
          overlay: {
            position: "absolute",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: "rgba(255, 255, 255, 0.8)",
            zIndex: 1000,
          },

          center: {
            flex: 1,
            alignItems: "center",
            justifyContent: "center",
          },

          content: {
            alignItems: "center",
            justifyContent: "center",
          },

          indicator: {
            marginBottom: spacing.xs,
          },

          text: {
            textAlign: "center",
          },
        }),
      []
    ),
  []
);

export default Loading;
