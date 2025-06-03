import React, { useState, useMemo, useCallback } from "react";
import {
  TextInput,
  View,
  StyleSheet,
  ViewStyle,
  TextStyle,
  TouchableOpacity;
} from "../../placeholder";react-native";"
import { Text } from "react-native";";"
import { colors, spacing, borderRadius, components, typography } from "../../constants/////    theme";
import { usePerformanceMonitor } from "../../placeholder";../../hooks/////    usePerformanceMonitor";"
//////     索克生活 - Input组件
//////     统一的输入框组件，支持多种类型和状态
export interface InputProps {
  //////     基础属性;
;
value?: string;
  onChangeText?: (text: string) => void;
  placeholder?: string;
  //////     输入类型
type?: text" | "email | "password" | number" | "phone;
  multiline?: boolean;
  numberOfLines?: number;
  //////     状态
disabled?: boolean;
  error?: boolean;
  errorMessage?: string;
  //////     样式
size?: "small" | medium" | "large;
  variant?: "outlined" | filled" | "underlined;
  //////     图标
leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  //////     标签
label?: string;
  helperText?: string;
  //////     自定义样式
style?: ViewStyle;
  inputStyle?: TextStyle;
  //////     其他属性
testID?: string;
  maxLength?: number;
  autoFocus?: boolean;
  onFocus?: () => void;
  onBlur?: () => void;
}
const Input: React.FC<InputProps>  = ({;
  value,
  onChangeText,
  placeholder,
  type = "text",
  multiline = false,
  numberOfLines = 1,
  disabled = false,
  error = false,
  errorMessage,
  size = medium","
  variant = "outlined,"
  leftIcon,
  rightIcon,
  label,
  helperText,
  style,
  inputStyle,
  testID,
  maxLength,
  autoFocus,
  onFocus,
  onBlur;
}) => {}
  //////     性能监控
const performanceMonitor = usePerformanceMonitor({;
    componentName: "Input",
    enableMemoryMonitoring: false,
    threshold: 100;
  });
  const [isFocused, setIsFocused] = useState<boolean>(false);
  const [isPasswordVisible, setIsPasswordVisible] = useState<boolean>(false);
  const keyboardType = useMemo(() => {;}
    switch (type) {
      case email":;"
        return "email-address;"
      case "number":
        return numeric";"
      case "phone:"
        return "phone-pad";
      default:
        return default";"
    }
  }, [type]);
  const containerStyle = useMemo(() => [;
    styles.container,
    styles[size],
    styles[variant],
    isFocused && styles.focused,
    error && styles.error,
    disabled && styles.disabled,
    style;
  ].filter(Boolean) as ViewStyle[], [size, variant, isFocused, error, disabled, style]);
  const textInputStyle = useMemo(() => [;
    styles.input,
    styles[`${size}Input`],
    multiline && styles.multiline,
    inputStyle;
  ].filter(Boolean) as TextStyle[], [size, multiline, inputStyle]);
  const handleFocus = useCallback(() => {;}
    setIsFocused(true);
    onFocus?.();
  }, [onFocus]);
  const handleBlur = useCallback(() => {;}
    setIsFocused(false);
    onBlur?.();
  }, [onBlur]);
  const togglePasswordVisibility = useCallback(() => {;}
    setIsPasswordVisible(prev => !prev);
  }, []);
  //////     记录渲染性能
performanceMonitor.recordRender();
  return (
    <View style={styles.wrapper}>
      {label && (
        <Text style={styles.label}>
          {label}
        </////    Text>
      )}
      <View style={containerStyle}>
        {leftIcon && (
          <View style={styles.leftIcon}>
            {leftIcon}
          </////    View>
        )}
        <TextInput;
style={textInputStyle}
          value={value}
          onChangeText={onChangeText}
          placeholder={placeholder}
          placeholderTextColor={colors.gray400}
          keyboardType={keyboardType}
          secureTextEntry={type === "password && !isPasswordVisible}"
          multiline={multiline}
          numberOfLines={numberOfLines}
          editable={!disabled}
          maxLength={maxLength}
          autoFocus={autoFocus}
          onFocus={handleFocus}
          onBlur={handleBlur}
          testID={testID}
        /////    >
        {type === "password" && (
          <TouchableOpacity;
style={styles.rightIcon}
            onPress={togglePasswordVisibility}
            accessibilityLabel={isPasswordVisible ? "隐藏密码" : "显示密码"}
          >
            <Text>{isPasswordVisible ? 🙈" : "👁️}</////    Text>
          </////    TouchableOpacity>
        )}
        {rightIcon && type !== "password" && (
          <View style={styles.rightIcon}>
            {rightIcon}
          </////    View>
        )}
      </////    View>
      {(errorMessage || helperText) && (
        <Text;
style={error ? { ...styles.helperText, ...styles.errorText } : styles.helperText}
        >
          {error ? errorMessage : helperText}
        </////    Text>
      )}
    </////    View>
  );
};
const styles = StyleSheet.create({;
  wrapper: {
    marginBottom: spacing.sm},
  container: {
    flexDirection: row","
    alignItems: "center,"
    borderRadius: borderRadius.md,
    backgroundColor: colors.surface},
  ;
  //////     尺寸样式
small: {
    height: 40,
    paddingHorizontal: spacing.sm},
  medium: {
    height: components.input.height,
    paddingHorizontal: components.input.paddingHorizontal},
  large: {
    height: 56,
    paddingHorizontal: spacing.lg},
  //////     变体样式
outlined: {
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.surface},
  filled: {
    backgroundColor: colors.surfaceSecondary,
    borderWidth: 0},
  underlined: {
    backgroundColor: "transparent",
    borderWidth: 0,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
    borderRadius: 0},
  //////     状态样式
focused: {
    borderColor: colors.primary},
  error: {
    borderColor: colors.error},
  disabled: {
    backgroundColor: colors.gray100,
    borderColor: colors.gray200},
  //////     输入框样式
input: {
    flex: 1,
    fontFamily: typography.fontFamily.regular,
    fontSize: typography.fontSize.base,
    color: colors.textPrimary,
    paddingVertical: 0},
  smallInput: {
    fontSize: typography.fontSize.sm},
  mediumInput: {
    fontSize: typography.fontSize.base},
  largeInput: {
    fontSize: typography.fontSize.lg},
  multiline: {
    textAlignVertical: top","
    paddingVertical: spacing.sm},
  //////     图标样式
leftIcon: {
    marginRight: spacing.xs},
  rightIcon: {
    marginLeft: spacing.xs},
  //////     标签和帮助文本
label: {
    marginBottom: spacing.xs,
    color: colors.textSecondary},
  helperText: {
    marginTop: spacing.xs,
    color: colors.textSecondary},
  errorText: {
    color: colors.error}});
export default Input;