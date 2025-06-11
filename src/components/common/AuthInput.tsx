import React, { forwardRef, useState } from 'react';
import {
    StyleSheet,
    Text,
    TextInput,
    TextInputProps,
    TextStyle,
    TouchableOpacity,
    View,
    ViewStyle
} from 'react-native';

// AuthInput - 认证输入组件
// 索克生活 - 用于登录、注册等认证场景的输入组件

interface AuthInputProps extends Omit<TextInputProps, 'style'> {
  label?: string;
  error?: string;
  isPassword?: boolean;
  containerStyle?: ViewStyle;
  inputStyle?: TextStyle;
  labelStyle?: TextStyle;
  errorStyle?: TextStyle;
  showPasswordToggle?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  required?: boolean;
}

const AuthInput = forwardRef<TextInput, AuthInputProps>(({
  label,
  error,
  isPassword = false,
  containerStyle,
  inputStyle,
  labelStyle,
  errorStyle,
  showPasswordToggle = true,
  leftIcon,
  rightIcon,
  required = false,
  ...textInputProps
}, ref) => {
  const [isPasswordVisible, setIsPasswordVisible] = useState(false);
  const [isFocused, setIsFocused] = useState(false);

  const togglePasswordVisibility = () => {
    setIsPasswordVisible(!isPasswordVisible);
  };

  const handleFocus = (e: any) => {
    setIsFocused(true);
    textInputProps.onFocus?.(e);
  };

  const handleBlur = (e: any) => {
    setIsFocused(false);
    textInputProps.onBlur?.(e);
  };

  const getInputStyle = () => {
    return [
      styles.input,
      isFocused && styles.inputFocused,
      error && styles.inputError,
      leftIcon && styles.inputWithLeftIcon,
      (isPassword && showPasswordToggle) || rightIcon ? styles.inputWithRightIcon : null,
      inputStyle
    ];
  };

  const getContainerStyle = () => {
    return [
      styles.container,
      containerStyle
    ];
  };

  return (
    <View style={getContainerStyle()}>
      {label && (
        <Text style={[styles.label, labelStyle]}>
          {label}
          {required && <Text style={styles.required}> *</Text>}
        </Text>
      )}
      
      <View style={styles.inputContainer}>
        {leftIcon && (
          <View style={styles.leftIconContainer}>
            {leftIcon}
          </View>
        )}
        
        <TextInput
          ref={ref}
          style={getInputStyle()}
          secureTextEntry={isPassword && !isPasswordVisible}
          onFocus={handleFocus}
          onBlur={handleBlur}
          placeholderTextColor="#999"
          {...textInputProps}
        />
        
        {isPassword && showPasswordToggle && (
          <TouchableOpacity
            style={styles.passwordToggle}
            onPress={togglePasswordVisibility}
            accessibilityLabel={isPasswordVisible ? "隐藏密码" : "显示密码"}
          >
            <Text style={styles.passwordToggleText}>
              {isPasswordVisible ? "隐藏" : "显示"}
            </Text>
          </TouchableOpacity>
        )}
        
        {rightIcon && !isPassword && (
          <View style={styles.rightIconContainer}>
            {rightIcon}
          </View>
        )}
      </View>
      
      {error && (
        <Text style={[styles.error, errorStyle]}>
          {error}
        </Text>
      )}
    </View>
  );
});

const styles = StyleSheet.create({
  container: {
    marginBottom: 16
  },
  label: {
    fontSize: 14,
    fontWeight: '500',
    color: '#333',
    marginBottom: 8
  },
  required: {
    color: '#ff3b30'
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    position: 'relative'
  },
  input: {
    flex: 1,
    height: 48,
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    paddingHorizontal: 16,
    fontSize: 16,
    backgroundColor: '#fff',
    color: '#333'
  },
  inputFocused: {
    borderColor: '#35bb78', // 索克绿
    borderWidth: 2
  },
  inputError: {
    borderColor: '#ff3b30'
  },
  inputWithLeftIcon: {
    paddingLeft: 48
  },
  inputWithRightIcon: {
    paddingRight: 48
  },
  leftIconContainer: {
    position: 'absolute',
    left: 12,
    zIndex: 1,
    justifyContent: 'center',
    alignItems: 'center'
  },
  rightIconContainer: {
    position: 'absolute',
    right: 12,
    zIndex: 1,
    justifyContent: 'center',
    alignItems: 'center'
  },
  passwordToggle: {
    position: 'absolute',
    right: 12,
    zIndex: 1,
    padding: 4
  },
  passwordToggleText: {
    fontSize: 14,
    color: '#35bb78', // 索克绿
    fontWeight: '500'
  },
  error: {
    fontSize: 12,
    color: '#ff3b30',
    marginTop: 4
  }
});

AuthInput.displayName = 'AuthInput';

export default AuthInput;