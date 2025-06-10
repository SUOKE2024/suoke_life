import React, { useState, useCallback, useMemo } from 'react';
import {;
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ViewStyle,
  TextStyle,
  TextInputProps;
} from 'react-native';
export interface InputProps extends TextInputProps {
  label?: string;
  error?: boolean;
  errorMessage?: string;
  size?: "small" | "medium" | "large";
  variant?: "outlined" | "filled" | "underlined";
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  helperText?: string;
  type?: "text" | "email" | "password" | "number" | "phone";
  containerStyle?: ViewStyle;
  inputStyle?: TextStyle;
  disabled?: boolean;
}
const Input: React.FC<InputProps> = ({
  value,
  onChangeText,
  placeholder,
  type = "text",
  multiline = false,
  numberOfLines = 1,
  disabled = false,
  error = false,
  errorMessage,
  size = "medium",
  variant = "outlined",
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
  onBlur,
  containerStyle,
  ...props;
}) => {
  const [isFocused, setIsFocused] = useState<boolean>(false);
  const [isPasswordVisible, setIsPasswordVisible] = useState<boolean>(false);
  const keyboardType = useMemo() => {
    switch (type) {
      case "email":
        return "email-address";
      case "number":
        return "numeric";
      case "phone":
        return "phone-pad";
      default:
        return "default";
    }
  }, [type]);
  const handleFocus = useCallback(e: any) => {
    setIsFocused(true);
    onFocus?.(e);
  }, [onFocus]);
  const handleBlur = useCallback(e: any) => {
    setIsFocused(false);
    onBlur?.(e);
  }, [onBlur]);
  const togglePasswordVisibility = useCallback() => {
    setIsPasswordVisible(prev => !prev);
  }, []);
  const getContainerStyle = (): ViewStyle[] => {
    const baseStyle = [styles.container];
        if (size === "small") baseStyle.push(styles.small);
    if (size === "large") baseStyle.push(styles.large);
    if (variant === "filled") baseStyle.push(styles.filled);
    if (variant === "underlined") baseStyle.push(styles.underlined);
    if (isFocused) baseStyle.push(styles.focused);
    if (error) baseStyle.push(styles.error);
    if (disabled) baseStyle.push(styles.disabled);
    if (containerStyle) baseStyle.push(containerStyle);
        return baseStyle;
  };
  const getInputStyle = (): TextStyle[] => {
    const baseStyle = [styles.input];
        if (size === "small") baseStyle.push(styles.smallInput);
    if (size === "large") baseStyle.push(styles.largeInput);
    if (multiline) baseStyle.push(styles.multiline);
    if (inputStyle) baseStyle.push(inputStyle);
        return baseStyle;
  };
  return (
  <View style={[styles.wrapper, style]}>
      {label  && <Text style={styles.label}>
          {label}
        </Text>
      )}
      <View style={getContainerStyle()}}>
        {leftIcon  && <View style={styles.leftIcon}>
            {leftIcon}
          </View>
        )}
        <TextInput;
          style={getInputStyle()}}
          value={value}
          onChangeText={onChangeText}
          placeholder={placeholder}
          placeholderTextColor="#999"
          keyboardType={keyboardType}
          secureTextEntry={type === "password" && !isPasswordVisible}
          multiline={multiline}
          numberOfLines={numberOfLines}
          editable={!disabled}
          maxLength={maxLength}
          autoFocus={autoFocus}
          onFocus={handleFocus}
          onBlur={handleBlur}
          testID={testID}
          {...props}
        />
        {type === "password"  && <TouchableOpacity;
            style={styles.rightIcon}
            onPress={togglePasswordVisibility}
            accessibilityLabel={isPasswordVisible ? "隐藏密码" : "显示密码"}
          >
            <Text>{isPasswordVisible ? "🙈" : "👁️"}</Text>
          </TouchableOpacity>
        )}
        {rightIcon && type !== "password"  && <View style={styles.rightIcon}>
            {rightIcon}
          </View>
        )}
      </View>
      {(errorMessage || helperText)  && <Text style={error ? [styles.helperText, styles.errorText] : styles.helperText}}>
          {error ? errorMessage : helperText}
        </Text>
      )}
    </View>
  );
};
const styles = StyleSheet.create({
  wrapper: {,
  marginBottom: 16},
  container: {,
  flexDirection: "row",
    alignItems: "center",
    borderRadius: 8,
    backgroundColor: "#fff",
    borderWidth: 1,
    borderColor: "#ddd",
    paddingHorizontal: 12,
    height: 48},
  small: {,
  height: 40,
    paddingHorizontal: 8},
  large: {,
  height: 56,
    paddingHorizontal: 16},
  filled: {,
  backgroundColor: "#f5f5f5",
    borderWidth: 0},
  underlined: {,
  backgroundColor: "transparent",
    borderWidth: 0,
    borderBottomWidth: 1,
    borderBottomColor: "#ddd",
    borderRadius: 0},
  focused: {,
  borderColor: "#007AFF"},
  error: {,
  borderColor: "#FF3B30"},
  disabled: {,
  backgroundColor: "#f0f0f0",
    borderColor: "#ccc"},
  input: {,
  flex: 1,
    fontSize: 16,
    color: "#333",
    paddingVertical: 0},
  smallInput: {,
  fontSize: 14},
  largeInput: {,
  fontSize: 18},
  multiline: {,
  textAlignVertical: "top",
    paddingVertical: 8},
  leftIcon: {,
  marginRight: 8},
  rightIcon: {,
  marginLeft: 8},
  label: {,
  marginBottom: 4,
    color: "#666",
    fontSize: 14},
  helperText: {,
  marginTop: 4,
    color: "#666",
    fontSize: 12},
  errorText: {,
  color: "#FF3B30"}});
export default Input;