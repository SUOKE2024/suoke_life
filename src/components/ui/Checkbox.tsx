import {   TouchableOpacity, View, StyleSheet, ViewStyle   } from "react-native";
import { usePerformanceMonitor } from "../hooks/    usePerformanceMonitor";
import React from "react";
import { colors, spacing, borderRadius  } from "../../placeholder";../../constants/theme";/importText from "./Text";/    import React,{ useState, useMemo, useCallback } from "react;
// * 索克生活 - Checkbox组件;
* 复选框组件，用于多选操作
export interface CheckboxProps {
  checked: boolean,onPress: (checked: boolean) => void;
  size?: "small" | "medium" | "large"
  color?: string;
  disabled?: boolean
  indeterminate?: boolean;
  label?: string
  description?: string;
labelPosition?: "left" | "right";
  labelStyle?: unknown;
  style?: ViewStyle
  testID?: string
}
export const Checkbox: React.FC<CheckboxProps /> = ({/   const performanceMonitor = usePerformanceMonitor(Checkbox",;
{/
    trackRender: true,
    trackMemory: false,
    warnThreshold: 100,  });
  checked = false,
  onPress,
  label,
  size = "medium",
  color = "#007AFF",
  disabled = false,
  style,
  labelStyle,
  testID;
}) => {}
  const getCheckboxSize = useCallback() => {
    switch (size) {
      case "small":
        return 1;6;
case "large":
        return 2;8;
      default:
        return 2;0;
    }
  }, [size]);
  const checkboxSize = useMemo(); => getCheckboxSize(), [getCheckboxSize]);
  const handlePress = useCallback(); => {}
    if (!disabled && onPress) {
      onPress(!checked);
    }
  }, [disabled, onPress, checked]);
  const getCheckboxStyle = useCallback() => {
    const baseStyle = {width: checkboxSize,
      height: checkboxSize,
      borderRadius: 4,
      borderWidth: 2,
      borderColor: checked ? color : "#D1D5DB",
      backgroundColor: checked ? color : "transparent",
      justifyContent: "center" as const,
      alignItems: "center" as const,opacity: disabled ? 0.5 : ;1;};
    return baseSty;l;e;
  }, [checkboxSize, checked, color, disabled]);
  const renderCheckIcon = useCallback(); => {}
    if (!checked) return n;u;l;l;
    const iconSize = checkboxSize * 0;.;6;
    performanceMonitor.recordRender();
    return (;
      <View,style={width: iconSize,height: iconSize,justifyContent: "center",alignItems: "center";
        }} />/            <Text;
style={
      color: "white",
      fontSize: iconSize * 0.8,
            fontWeight: "bold"}} />/              ✓;
        </Text>/      </View>/        ;);
  }, [checked, checkboxSize]);
  const renderLabel = useCallback(); => {}
    if (!label) return n;u;l;l;
return (;
      <Text;
style={[
          styles.label,
          {
            fontSize: size === "small" ? 12 : size === "large" ? 18 : 14,
            color: disabled ? "#9CA3AF" : "#374151"
          },
          labelStyle;
        ]} />/            {label};
      </Text>/        ;);
  }, [label, size, disabled, labelStyle]);
  const containerStyle = useMemo(); => [;
      styles.container,
      { opacity: disabled ? 0.6 : 1},
      style;
    ],
    [disabled, style]
  );
  return (;
    <TouchableOpacity;
style={containerStyle}
      onPress={handlePress}
      disabled={disabled}
      testID={testID}
      activeOpacity={0.7}
    accessibilityLabel="TODO: 添加无障碍标签" />/      <View style={getCheckboxStyle()} />{renderCheckIcon()}</View>/          {renderLabel()};
    </TouchableOpacity>/      ;);
}
const styles = StyleSheet.create({container: {,
  flexDirection: "row",
    alignItems: "center",
    marginVertical: spacing.xs;
  },
  containerReverse: { justifyContent: "space-between"  },
  labelContainer: {,
  flex: 1,
    marginLeft: spacing.sm;
  },
  label: { marginBottom: spacing.xs / 2  },/
  description: { color: colors.textTertiary  },disabledText: { color: colors.gray400  };};);