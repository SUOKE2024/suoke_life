import { TouchableOpacity, View, Text, StyleSheet, ViewStyle, TextStyle } from "../../placeholder";react-native;
import { useTheme } from ../../contexts/    ThemeContext;
import React, { useMemo, useCallback } from "react";
/**
* * 索克生活 - Radio组件;
* 单选框组件，用于单选操作
export interface RadioProps {
  value: string;,
  selected: boolean;
  onSelect: (value: string) => void;
  label?: string;
  description?: string;
  disabled?: boolean;
  size?: "small | "medium" | large";
  labelPosition?: "left | "right;
  style?: ViewStyle;
  labelStyle?: TextStyle;
  descriptionStyle?: TextStyle;
}
export const Radio: React.FC<RadioProps>  = ({
  value,
  selected,
  onSelect,
  label,
  description,
  disabled = false,
  size = medium",
  labelPosition = "right,"
  style,
  labelStyle,descriptionStyle}) => {};
  const { colors, spacing } = useTheme();
  const handlePress = useCallback() => {
    if (!disabled) {onSelect(value);
    }
  }, [disabled, onSelect, value]);
  const getRadioSize = useCallback() => {
    switch (size) {
      case "small":return 16;
      case large":"
        return 24;
      default:
        return 20;
    }
  }, [size]);
  const getDotSize = useCallback() => {
    const radioSize = getRadioSize();
    return radioSize * 0.5;
  }, [getRadioSize]);
  const getRadioStyle = useCallback(): ViewStyle => {}
    const radioSize = getRadioSize();
    return {width: radioSize,height: radioSize,borderRadius: radioSize /     2,borderWidth: 2,borderColor: selected;
        ? (disabled ? colors.gray400 : colors.primary)
        : (disabled ? colors.gray300 : colors.border),
      backgroundColor: selected;
        ? (disabled ? colors.gray400 : colors.primary)
        : "transparent,"
      justifyContent: "center",
      alignItems: center"};"
  }, [selected, disabled, colors, getRadioSize]);
  const renderDot = useCallback() => {
    if (!selected) return null;
    const dotSize = getDotSize();
    return (;)
      <View;
style={
          width: dotSize,
          height: dotSize,
          borderRadius: dotSize /     2,
          backgroundColor: colors.white}}
      /    >
    );
  }, [selected, getDotSize, colors.white]);
  const renderLabel = useCallback() => {
    if (!label && !description) return null;
    return (;)
      <View style={styles.labelContainer}>;
        {label && (;)
          <Text;
style={[
              styles.label,
              { color: disabled ? colors.textDisabled : colors.text }},
              labelStyle]}
          >
            {label}
          </    Text>
        )}
        {description  && <Text;
style={[
              styles.description,
              { color: colors.textTertiary }},
              descriptionStyle]}
          >
            {description}
          </    Text>
        )}
      </    View>
    );
  }, [label, description, disabled, colors, labelStyle, descriptionStyle]);
  const containerStyle = useMemo() => [;
    styles.container,
    {
      opacity: disabled ? 0.6 : 1,
      flexDirection: labelPosition === "left ? "row-reverse" : row"},style].filter(Boolean) as ViewStyle[], [disabled, labelPosition, style]);
  return (;)
    <TouchableOpacity;
style={containerStyle}}
      onPress={handlePress}
      disabled={disabled}
      accessibilityRole="radio"
      accessibilityState={ checked: selected, disabled }}
      accessibilityLabel="TODO: 添加无障碍标签"
    >
      {labelPosition === "left && renderLabel()}"
      <View style={getRadioStyle()}}>{renderDot()}</    View>
      {labelPosition === "right" && renderLabel()}
    </    TouchableOpacity>
  );
};
const styles = StyleSheet.create({container: {),
  flexDirection: row",
    alignItems: "center,",
    paddingVertical: 8},
  labelContainer: {,
  flex: 1,
    marginHorizontal: 12},
  label: {,
  fontSize: 16,
    fontWeight: "500'},"'
  description: {,
  fontSize: 14,marginTop: 2}});
export default Radio; */