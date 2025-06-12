import React, { useState, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  Alert,
  ActivityIndicator,
  Dimensions,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import Icon from 'react-native-vector-icons/MaterialIcons';

// 导入服务
import { IntegratedApiService } from '../../services/IntegratedApiService';

const { width: screenWidth } = Dimensions.get('window');

// 表单验证规则
const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

const validatePassword = (password: string): boolean => {
  return password.length >= 6;
};

// 表单错误类型
interface FormErrors {
  email?: string;
  password?: string;
  general?: string;
}

const LoginScreen: React.FC = () => {
  const navigation = useNavigation();
  const passwordRef = useRef<TextInput>(null);
  const apiService = new IntegratedApiService();

  // 表单状态
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [errors, setErrors] = useState<FormErrors>({});
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);

  // 更新表单数据
  const updateFormData = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // 清除对应字段的错误
    if (errors[field as keyof FormErrors]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  // 验证表单
  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    // 验证邮箱
    if (!formData.email.trim()) {
      newErrors.email = '请输入邮箱地址';
    } else if (!validateEmail(formData.email)) {
      newErrors.email = '请输入有效的邮箱地址';
    }

    // 验证密码
    if (!formData.password) {
      newErrors.password = '请输入密码';
    } else if (!validatePassword(formData.password)) {
      newErrors.password = '密码至少需要6位字符';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // 处理登录
  const handleLogin = async () => {
    if (!validateForm()) {
      return;
    }

    setIsLoading(true);
    setErrors({});

    try {
      const response = await apiService.auth.login({
        email: formData.email.trim(),
        password: formData.password,
      });

      if (response.success) {
        // 登录成功，跳转到主页面
        Alert.alert('登录成功', '欢迎回到索克生活！', [
          {
            text: '确定',
            onPress: () => navigation.navigate('MainApp' as never),
          },
        ]);
      } else {
        setErrors({
          general: response.message || '登录失败，请检查邮箱和密码',
        });
      }
    } catch (error) {
      console.error('Login error:', error);
      setErrors({
        general: '网络连接失败，请稍后重试',
      });
    } finally {
      setIsLoading(false);
    }
  };

  // 处理快速登录（演示用）
  const handleQuickLogin = () => {
    Alert.alert(
      '快速登录',
      '是否使用演示账号登录？',
      [
        { text: '取消', style: 'cancel' },
        {
          text: '确定',
          onPress: () => {
            setFormData({
              email: 'demo@suoke.life',
              password: 'demo123',
            });
            setTimeout(() => {
              navigation.navigate('MainApp' as never);
            }, 500);
          },
        },
      ]
    );
  };

  // 导航到注册页面
  const navigateToRegister = () => {
    navigation.navigate('Register' as never);
  };

  // 导航到忘记密码页面
  const navigateToForgotPassword = () => {
    navigation.navigate('ForgotPassword' as never);
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        keyboardShouldPersistTaps="handled"
        showsVerticalScrollIndicator={false}
      >
        {/* 头部 */}
        <View style={styles.header}>
          <View style={styles.logoContainer}>
            <Icon name="healing" size={60} color="#2196F3" />
          </View>
          <Text style={styles.title}>欢迎回来</Text>
          <Text style={styles.subtitle}>登录您的索克生活账户</Text>
        </View>

        {/* 表单区域 */}
        <View style={styles.formContainer}>
          {/* 通用错误提示 */}
          {errors.general && (
            <View style={styles.errorContainer}>
              <Icon name="error" size={20} color="#F44336" />
              <Text style={styles.errorText}>{errors.general}</Text>
            </View>
          )}

          {/* 邮箱输入 */}
          <View style={styles.inputContainer}>
            <Text style={styles.inputLabel}>邮箱地址</Text>
            <View style={[styles.inputWrapper, errors.email && styles.inputError]}>
              <Icon name="email" size={20} color="#666" style={styles.inputIcon} />
              <TextInput
                style={styles.textInput}
                value={formData.email}
                onChangeText={(text) => updateFormData('email', text)}
                placeholder="请输入邮箱地址"
                placeholderTextColor="#999"
                keyboardType="email-address"
                autoCapitalize="none"
                autoCorrect={false}
                returnKeyType="next"
                onSubmitEditing={() => passwordRef.current?.focus()}
                editable={!isLoading}
              />
            </View>
            {errors.email && (
              <Text style={styles.fieldErrorText}>{errors.email}</Text>
            )}
          </View>

          {/* 密码输入 */}
          <View style={styles.inputContainer}>
            <Text style={styles.inputLabel}>密码</Text>
            <View style={[styles.inputWrapper, errors.password && styles.inputError]}>
              <Icon name="lock" size={20} color="#666" style={styles.inputIcon} />
              <TextInput
                ref={passwordRef}
                style={styles.textInput}
                value={formData.password}
                onChangeText={(text) => updateFormData('password', text)}
                placeholder="请输入密码"
                placeholderTextColor="#999"
                secureTextEntry={!showPassword}
                returnKeyType="done"
                onSubmitEditing={handleLogin}
                editable={!isLoading}
              />
              <TouchableOpacity
                style={styles.passwordToggle}
                onPress={() => setShowPassword(!showPassword)}
              >
                <Icon
                  name={showPassword ? 'visibility' : 'visibility-off'}
                  size={20}
                  color="#666"
                />
              </TouchableOpacity>
            </View>
            {errors.password && (
              <Text style={styles.fieldErrorText}>{errors.password}</Text>
            )}
          </View>

          {/* 记住我和忘记密码 */}
          <View style={styles.optionsContainer}>
            <TouchableOpacity
              style={styles.rememberContainer}
              onPress={() => setRememberMe(!rememberMe)}
            >
              <Icon
                name={rememberMe ? 'check-box' : 'check-box-outline-blank'}
                size={20}
                color="#2196F3"
              />
              <Text style={styles.rememberText}>记住我</Text>
            </TouchableOpacity>
            <TouchableOpacity onPress={navigateToForgotPassword}>
              <Text style={styles.forgotPasswordText}>忘记密码？</Text>
            </TouchableOpacity>
          </View>

          {/* 登录按钮 */}
          <TouchableOpacity
            style={[styles.loginButton, isLoading && styles.loginButtonDisabled]}
            onPress={handleLogin}
            disabled={isLoading}
            activeOpacity={0.8}
          >
            {isLoading ? (
              <ActivityIndicator size="small" color="#ffffff" />
            ) : (
              <Text style={styles.loginButtonText}>登录</Text>
            )}
          </TouchableOpacity>

          {/* 快速登录按钮（演示用） */}
          <TouchableOpacity
            style={styles.quickLoginButton}
            onPress={handleQuickLogin}
            disabled={isLoading}
          >
            <Text style={styles.quickLoginText}>演示登录</Text>
          </TouchableOpacity>

          {/* 分割线 */}
          <View style={styles.dividerContainer}>
            <View style={styles.dividerLine} />
            <Text style={styles.dividerText}>或</Text>
            <View style={styles.dividerLine} />
          </View>

          {/* 第三方登录 */}
          <View style={styles.socialLoginContainer}>
            <TouchableOpacity style={styles.socialButton}>
              <Icon name="phone" size={24} color="#4CAF50" />
              <Text style={styles.socialButtonText}>手机号登录</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* 底部注册链接 */}
        <View style={styles.bottomContainer}>
          <Text style={styles.bottomText}>还没有账户？</Text>
          <TouchableOpacity onPress={navigateToRegister}>
            <Text style={styles.registerText}>立即注册</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#ffffff',
  },
  scrollContent: {
    flexGrow: 1,
    paddingHorizontal: 24,
    paddingTop: 60,
    paddingBottom: 40,
  },
  header: {
    alignItems: 'center',
    marginBottom: 40,
  },
  logoContainer: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#f0f8ff',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
  },
  formContainer: {
    flex: 1,
  },
  errorContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#ffebee',
    padding: 12,
    borderRadius: 8,
    marginBottom: 20,
  },
  errorText: {
    color: '#F44336',
    fontSize: 14,
    marginLeft: 8,
    flex: 1,
  },
  inputContainer: {
    marginBottom: 20,
  },
  inputLabel: {
    fontSize: 16,
    fontWeight: '500',
    color: '#333',
    marginBottom: 8,
  },
  inputWrapper: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 12,
    paddingHorizontal: 16,
    backgroundColor: '#fafafa',
  },
  inputError: {
    borderColor: '#F44336',
    backgroundColor: '#ffebee',
  },
  inputIcon: {
    marginRight: 12,
  },
  textInput: {
    flex: 1,
    height: 50,
    fontSize: 16,
    color: '#333',
  },
  passwordToggle: {
    padding: 4,
  },
  fieldErrorText: {
    color: '#F44336',
    fontSize: 12,
    marginTop: 4,
    marginLeft: 4,
  },
  optionsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 30,
  },
  rememberContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  rememberText: {
    color: '#666',
    fontSize: 14,
    marginLeft: 8,
  },
  forgotPasswordText: {
    color: '#2196F3',
    fontSize: 14,
    fontWeight: '500',
  },
  loginButton: {
    backgroundColor: '#2196F3',
    borderRadius: 12,
    height: 50,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
    shadowColor: '#2196F3',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  loginButtonDisabled: {
    backgroundColor: '#ccc',
    shadowOpacity: 0,
    elevation: 0,
  },
  loginButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  quickLoginButton: {
    backgroundColor: 'transparent',
    borderWidth: 1,
    borderColor: '#2196F3',
    borderRadius: 12,
    height: 50,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 30,
  },
  quickLoginText: {
    color: '#2196F3',
    fontSize: 16,
    fontWeight: '500',
  },
  dividerContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
  },
  dividerLine: {
    flex: 1,
    height: 1,
    backgroundColor: '#e0e0e0',
  },
  dividerText: {
    color: '#999',
    fontSize: 14,
    marginHorizontal: 16,
  },
  socialLoginContainer: {
    marginBottom: 30,
  },
  socialButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#f5f5f5',
    borderRadius: 12,
    height: 50,
    paddingHorizontal: 20,
  },
  socialButtonText: {
    color: '#333',
    fontSize: 16,
    fontWeight: '500',
    marginLeft: 12,
  },
  bottomContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 20,
  },
  bottomText: {
    color: '#666',
    fontSize: 14,
  },
  registerText: {
    color: '#2196F3',
    fontSize: 14,
    fontWeight: 'bold',
    marginLeft: 4,
  },
});

export default LoginScreen;