import { TouchableOpacity, View, StyleSheet, ViewStyle } from "react-native";
import { colors, spacing, borderRadius } from "../../constants/theme";
import Text from "./Text";
import React, { useState, useMemo, useCallback } from "react";

/**
 * 索克生活 - Checkbox组件
 * 复选框组件，用于多选操作
 */

export interface CheckboxProps {
  // 基础属性
  checked: boolean;
  onPress: (checked: boolean) => void;

  // 样式
  size?: "small" | "medium" | "large";
  color?: string;

  // 状态
  disabled?: boolean;
  indeterminate?: boolean;

  // 标签
  label?: string;
  description?: string;
  labelPosition?: "left" | "right";
  labelStyle?: any;

  // 容器样式
  style?: ViewStyle;

  // 测试
  testID?: string;
}

export const Checkbox: React.FC<CheckboxProps> = ({
  checked = false,
  onPress,
  label,
  size = "medium",
  color = "#007AFF",
  disabled = false,
  style,
  labelStyle,
  testID,
}) => {
  const getCheckboxSize = useCallback(() => {
    switch (size) {
      case "small":
        return 16;
      case "large":
        return 28;
      default:
        return 20;
    }
  }, [size]);

  const checkboxSize = useMemo(() => getCheckboxSize(), [getCheckboxSize]);

  const handlePress = useCallback(() => {
    if (!disabled && onPress) {
      onPress(!checked);
    }
  }, [disabled, onPress, checked]);

  const getCheckboxStyle = useCallback(() => {
    const baseStyle = {
      width: checkboxSize,
      height: checkboxSize,
      borderRadius: 4,
      borderWidth: 2,
      borderColor: checked ? color : "#D1D5DB",
      backgroundColor: checked ? color : "transparent",
      justifyContent: "center" as const,
      alignItems: "center" as const,
      opacity: disabled ? 0.5 : 1,
    };

    return baseStyle;
  }, [checkboxSize, checked, color, disabled]);

  const renderCheckIcon = useCallback(() => {
    if (!checked) return null;

    const iconSize = checkboxSize * 0.6;

    return (
      <View
        style={{
          width: iconSize,
          height: iconSize,
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        <Text
          style={{
            color: "white",
            fontSize: iconSize * 0.8,
            fontWeight: "bold",
          }}
        >
          ✓
        </Text>
      </View>
    );
  }, [checked, checkboxSize]);

  const renderLabel = useCallback(() => {
    if (!label) return null;

    return (
      <Text
        style={[
          styles.label,
          {
            fontSize: size === "small" ? 12 : size === "large" ? 18 : 14,
            color: disabled ? "#9CA3AF" : "#374151",
          },
          labelStyle,
        ]}
      >
        {label}
      </Text>
    );
  }, [label, size, disabled, labelStyle]);

  const containerStyle = useMemo(
    () => [
      styles.container,
      {
        opacity: disabled ? 0.6 : 1,
      },
      style,
    ],
    [disabled, style]
  );

  return (
    <TouchableOpacity
      style={containerStyle}
      onPress={handlePress}
      disabled={disabled}
      testID={testID}
      activeOpacity={0.7}
    >
      <View style={getCheckboxStyle()}>{renderCheckIcon()}</View>
      {renderLabel()}
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    alignItems: "center",
    marginVertical: spacing.xs,
  },

  containerReverse: {
    justifyContent: "space-between",
  },

  labelContainer: {
    flex: 1,
    marginLeft: spacing.sm,
  },

  label: {
    marginBottom: spacing.xs / 2,
  },

  description: {
    color: colors.textTertiary,
  },

  disabledText: {
    color: colors.gray400,
  },
});
