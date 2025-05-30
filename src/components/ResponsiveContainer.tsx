import { View, StyleSheet, useWindowDimensions } from "react-native";
import React from "react";

interface ResponsiveContainerProps {
  children: React.ReactNode;
  style?: any;
}

export const ResponsiveContainer: React.FC<ResponsiveContainerProps> = ({
  children,
  style,
}) => {
  const { width } = useWindowDimensions();
  const isTablet = width >= 768;
  return (
    <View
      testID="responsive-container"
      style={[styles.container, isTablet ? styles.tablet : styles.phone, style]}
    >
      {children}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingHorizontal: 16,
    backgroundColor: "#fff",
  },
  phone: {
    maxWidth: 480,
    alignSelf: "center",
  },
  tablet: {
    maxWidth: 900,
    alignSelf: "center",
    paddingHorizontal: 32,
  },
});
