import React, { useState, useCallback } from "react";
import {
  View,
  Text,
  TextInput,
  StyleSheet,
  TouchableOpacity,
  ViewStyle,
  TextInputProps;
} from "react-native";
interface InputProps extends TextInputProps {
  label?: string;
  error?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  containerStyle?: ViewStyle;
  inputStyle?: ViewStyle;
  showPassword?: boolean;
}
export const Input: React.FC<InputProps> = ({
  label,
  error,
  leftIcon,
  rightIcon,
  containerStyle,
  inputStyle,
  showPassword = false,
  secureTextEntry,
  ...props;
}) => {
  const [isPasswordVisible, setIsPasswordVisible] = useState<boolean>(!secureTextEntry);
  const togglePasswordVisibility = useCallback() => {
    setIsPasswordVisible(!isPasswordVisible);
  }, [isPasswordVisible]);
  return (
  <View style={[styles.container, containerStyle]}>
      {label && <Text style={styles.label}>{label}</Text>}
      <View style={[styles.inputContainer, error ? styles.inputError : undefined]}>
        {leftIcon && <View style={styles.leftIcon}>{leftIcon}</View>}
        <TextInput;
          style={[styles.input, inputStyle]}
          secureTextEntry={secureTextEntry && !isPasswordVisible}
          placeholderTextColor="#999"
          {...props}
        />
        {showPassword && secureTextEntry  && <TouchableOpacity;
            style={styles.rightIcon}
            onPress={togglePasswordVisibility}
            accessibilityLabel={isPasswordVisible ? "隐藏密码" : "显示密码"}
          >
            <Text style={styles.passwordToggle}>
              {isPasswordVisible ? "隐藏" : "显示"}
            </Text>
          </TouchableOpacity>
        )}
        {rightIcon && !showPassword  && <View style={styles.rightIcon}>{rightIcon}</View>
        )}
      </View>
      {error && <Text style={styles.errorText}>{error}</Text>}
    </View>
  );
};
const styles = StyleSheet.create({
  container: {,
  marginBottom: 16},
  label: {,
  fontSize: 16,
    fontWeight: "600",
    color: "#333",
    marginBottom: 8},
  inputContainer: {,
  flexDirection: "row",
    alignItems: "center",
    borderWidth: 1,
    borderColor: "#ddd",
    borderRadius: 12,
    backgroundColor: "#fff",
    paddingHorizontal: 12},
  inputError: {,
  borderColor: "#FF3B30"},
  input: {,
  flex: 1,
    paddingVertical: 12,
    fontSize: 16,
    color: "#333"},
  leftIcon: {,
  marginRight: 8},
  rightIcon: {,
  marginLeft: 8},
  passwordToggle: {,
  fontSize: 14,
    color: "#007AFF",
    fontWeight: "600"},
  errorText: {,
  fontSize: 14,
    color: "#FF3B30",
    marginTop: 4}});