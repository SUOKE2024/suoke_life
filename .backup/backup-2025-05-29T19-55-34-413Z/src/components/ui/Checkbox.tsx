import { TouchableOpacity, View, StyleSheet, ViewStyle } from "react-native";
import { colors, spacing, borderRadius } from "../../constants/theme";
import Text from "./Text";
import React from "react";


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

  // 布局
  labelPosition?: "left" | "right";

  // 自定义样式
  style?: ViewStyle;

  // 其他属性
  testID?: string;
}

const Checkbox: React.FC<CheckboxProps> = ({
  checked,
  onPress,
  size = "medium",
  color = colors.primary,
  disabled = false,
  indeterminate = false,
  label,
  description,
  labelPosition = "right",
  style,
  testID,
}) => {
  const getCheckboxSize = useMemo(() => useMemo(() => useCallback( () => {, []), []), []);
    switch (size) {
      case "small":
        return 16;
      case "large":
        return 24;
      default:
        return 20;
    }
  };

  const checkboxSize = useMemo(() => useMemo(() => getCheckboxSize(), []), []);

  const handlePress = useMemo(() => useMemo(() => useCallback( () => {, []), []), []);
    if (!disabled) {
      onPress(!checked);
    }
  };

  const getCheckboxStyle = useMemo(() => useMemo(() => useCallback( () => {, []), []), []);
    const baseStyle = useMemo(() => useMemo(() => {
      width: checkboxSize,
      height: checkboxSize,
      borderRadius: borderRadius.sm,
      borderWidth: 2,
      alignItems: "center" as const,
      justifyContent: "center" as const,
    }, []) // TODO: 检查依赖项 // TODO: 检查依赖项, []);

    if (disabled) {
      return {
        ...baseStyle,
        backgroundColor: colors.gray100,
        borderColor: colors.gray300,
      };
    }

    if (checked || indeterminate) {
      return {
        ...baseStyle,
        backgroundColor: color,
        borderColor: color,
      };
    }

    return {
      ...baseStyle,
      backgroundColor: colors.surface,
      borderColor: colors.border,
    };
  };

  const renderCheckIcon = useMemo(() => useMemo(() => useCallback( () => {, []), []), []);
    if (indeterminate) {
      return (
        <View
          style={{
            width: checkboxSize * 0.5,
            height: 2,
            backgroundColor: colors.white,
          }}
        />
      );
    }

    if (checked) {
      return (
        <Text
          style={{
            color: colors.white,
            fontSize: checkboxSize * 0.7,
            fontWeight: "bold",
          }}
        >
          ✓
        </Text>
      );
    }

    return null;
  };

  const renderLabel = useMemo(() => useMemo(() => useCallback( () => {, []), []), []);
    if (!label && !description) {
      return null;
    }

    return (
      <View style={styles.labelContainer}>
        {label && (
          <Text
            variant="body1"
            style={
              disabled
                ? { ...styles.label, ...styles.disabledText }
                : styles.label
            }
          >
            {label}
          </Text>
        )}
        {description && (
          <Text
            variant="caption"
            style={
              disabled
                ? { ...styles.description, ...styles.disabledText }
                : styles.description
            }
          >
            {description}
          </Text>
        )}
      </View>
    );
  };

  const containerStyle = useMemo(() => useMemo(() => [
    styles.container,
    labelPosition === "left" && styles.containerReverse,
    style,
  ].filter(Boolean) as ViewStyle[], []), []);

  return (
    <TouchableOpacity
      style={containerStyle}
      onPress={handlePress}
      disabled={disabled}
      activeOpacity={0.7}
      testID={testID}
    >
      {labelPosition === "left" && renderLabel()}
      <View style={getCheckboxStyle()}>{renderCheckIcon()}</View>
      {labelPosition === "right" && renderLabel()}
    </TouchableOpacity>
  );
};

const styles = useMemo(() => useMemo(() => StyleSheet.create({
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
}), []), []);

export default Checkbox;
