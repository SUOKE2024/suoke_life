import { View, Text, ActivityIndicator, StyleSheet } from "react-native";
import { colors, fonts, spacing } from "../../constants/theme";
import React from "react";



/**
 * 通用加载屏幕组件
 */

interface LoadingScreenProps {
  message?: string;
  size?: "small" | "large";
  color?: string;
}

export const LoadingScreen: React.FC<LoadingScreenProps> = ({
  message = "加载中...",
  size = "large",
  color = colors.primary,
}) => {
  return (
    <View style={styles.container}>
      <ActivityIndicator size={size} color={color} />
      {message && <Text style={styles.message}>{message}</Text>}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: colors.background,
  },
  message: {
    marginTop: spacing.md,
    fontSize: fonts.size.md,
    color: colors.textSecondary,
    textAlign: "center",
  },
});

export default LoadingScreen;
