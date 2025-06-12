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
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import Icon from 'react-native-vector-icons/MaterialIcons';

// 导入服务
import { IntegratedApiService } from '../../services/IntegratedApiService';

// 表单验证规则
const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

const validatePassword = (password: string): boolean => {
  return password.length >= 6;
};

const validatePhone = (phone: string): boolean => {
  const phoneRegex = /^1[3-9]\d{9}$/;
  return phoneRegex.test(phone);
};

const validateName = (name: string): boolean => {
  return name.trim().length >= 2;
};

// 表单错误类型
interface FormErrors {
  name?: string;
  email?: string;
  phone?: string;
  password?: string;
  confirmPassword?: string;
  agreement?: string;
  general?: string;
}

const RegisterScreen: React.FC = () => {
  const navigation = useNavigation();
  const emailRef = useRef<TextInput>(null);
  const phoneRef = useRef<TextInput>(null);
  const passwordRef = useRef<TextInput>(null);
  const confirmPasswordRef = useRef<TextInput>(null);
  const apiService = new IntegratedApiService();

  // 表单状态
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    password: '',
    confirmPassword: '',
  });
  const [errors, setErrors] = useState<FormErrors>({});
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [agreeToTerms, setAgreeToTerms] = useState(false);

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

    // 验证姓名
    if (!formData.name.trim()) {
      newErrors.name = '请输入姓名';
    } else if (!validateName(formData.name)) {
      newErrors.name = '姓名至少需要2个字符';
    }

    // 验证邮箱
    if (!formData.email.trim()) {
      newErrors.email = '请输入邮箱地址';
    } else if (!validateEmail(formData.email)) {
      newErrors.email = '请输入有效的邮箱地址';
    }

    // 验证手机号
    if (!formData.phone.trim()) {
      newErrors.phone = '请输入手机号';
    } else if (!validatePhone(formData.phone)) {
      newErrors.phone = '请输入有效的手机号';
    }

    // 验证密码
    if (!formData.password) {
      newErrors.password = '请输入密码';
    } else if (!validatePassword(formData.password)) {
      newErrors.password = '密码至少需要6位字符';
    }

    // 验证确认密码
    if (!formData.confirmPassword) {
      newErrors.confirmPassword = '请确认密码';
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = '两次输入的密码不一致';
    }

    // 验证协议同意
    if (!agreeToTerms) {
      newErrors.agreement = '请阅读并同意用户协议和隐私政策';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // 处理注册
  const handleRegister = async () => {
    if (!validateForm()) {
      return;
    }

    setIsLoading(true);
    setErrors({});

    try {
      const response = await apiService.auth.register({
        name: formData.name.trim(),
        email: formData.email.trim(),
        phone: formData.phone.trim(),
        password: formData.password,
      });

      if (response.success) {
        Alert.alert(
          '注册成功',
          '欢迎加入索克生活！请登录您的账户。',
          [
            {
              text: '确定',
              onPress: () => navigation.navigate('Login' as never),
            },
          ]
        );
      } else {
        setErrors({
          general: response.message || '注册失败，请稍后重试',
        });
      }
    } catch (error) {
      console.error('Register error:', error);
      setErrors({
        general: '网络连接失败，请稍后重试',
      });
    } finally {
      setIsLoading(false);
    }
  };

  // 导航到登录页面
  const navigateToLogin = () => {
    navigation.navigate('Login' as never);
  };

  // 查看用户协议
  const viewTerms = () => {
    Alert.alert('用户协议', '这里是用户协议的内容...');
  };

  // 查看隐私政策
  const viewPrivacyPolicy = () => {
    Alert.alert('隐私政策', '这里是隐私政策的内容...');
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
          <TouchableOpacity
            style={styles.backButton}
            onPress={() => navigation.goBack()}
          >
            <Icon name="arrow-back" size={24} color="#333" />
          </TouchableOpacity>
          <View style={styles.logoContainer}>
            <Icon name="healing" size={60} color="#2196F3" />
          </View>
          <Text style={styles.title}>创建账户</Text>
          <Text style={styles.subtitle}>加入索克生活，开启健康之旅</Text>
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

          {/* 姓名输入 */}
          <View style={styles.inputContainer}>
            <Text style={styles.inputLabel}>姓名</Text>
            <View style={[styles.inputWrapper, errors.name && styles.inputError]}>
              <Icon name="person" size={20} color="#666" style={styles.inputIcon} />
              <TextInput
                style={styles.textInput}
                value={formData.name}
                onChangeText={(text) => updateFormData('name', text)}
                placeholder="请输入您的姓名"
                placeholderTextColor="#999"
                autoCapitalize="words"
                returnKeyType="next"
                onSubmitEditing={() => emailRef.current?.focus()}
                editable={!isLoading}
              />
            </View>
            {errors.name && (
              <Text style={styles.fieldErrorText}>{errors.name}</Text>
            )}
          </View>

          {/* 邮箱输入 */}
          <View style={styles.inputContainer}>
            <Text style={styles.inputLabel}>邮箱地址</Text>
            <View style={[styles.inputWrapper, errors.email && styles.inputError]}>
              <Icon name="email" size={20} color="#666" style={styles.inputIcon} />
              <TextInput
                ref={emailRef}
                style={styles.textInput}
                value={formData.email}
                onChangeText={(text) => updateFormData('email', text)}
                placeholder="请输入邮箱地址"
                placeholderTextColor="#999"
                keyboardType="email-address"
                autoCapitalize="none"
                autoCorrect={false}
                returnKeyType="next"
                onSubmitEditing={() => phoneRef.current?.focus()}
                editable={!isLoading}
              />
            </View>
            {errors.email && (
              <Text style={styles.fieldErrorText}>{errors.email}</Text>
            )}
          </View>

          {/* 手机号输入 */}
          <View style={styles.inputContainer}>
            <Text style={styles.inputLabel}>手机号</Text>
            <View style={[styles.inputWrapper, errors.phone && styles.inputError]}>
              <Icon name="phone" size={20} color="#666" style={styles.inputIcon} />
              <TextInput
                ref={phoneRef}
                style={styles.textInput}
                value={formData.phone}
                onChangeText={(text) => updateFormData('phone', text)}
                placeholder="请输入手机号"
                placeholderTextColor="#999"
                keyboardType="phone-pad"
                returnKeyType="next"
                onSubmitEditing={() => passwordRef.current?.focus()}
                editable={!isLoading}
              />
            </View>
            {errors.phone && (
              <Text style={styles.fieldErrorText}>{errors.phone}</Text>
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
                placeholder="请输入密码（至少6位）"
                placeholderTextColor="#999"
                secureTextEntry={!showPassword}
                returnKeyType="next"
                onSubmitEditing={() => confirmPasswordRef.current?.focus()}
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

          {/* 确认密码输入 */}
          <View style={styles.inputContainer}>
            <Text style={styles.inputLabel}>确认密码</Text>
            <View style={[styles.inputWrapper, errors.confirmPassword && styles.inputError]}>
              <Icon name="lock" size={20} color="#666" style={styles.inputIcon} />
              <TextInput
                ref={confirmPasswordRef}
                style={styles.textInput}
                value={formData.confirmPassword}
                onChangeText={(text) => updateFormData('confirmPassword', text)}
                placeholder="请再次输入密码"
                placeholderTextColor="#999"
                secureTextEntry={!showConfirmPassword}
                returnKeyType="done"
                onSubmitEditing={handleRegister}
                editable={!isLoading}
              />
              <TouchableOpacity
                style={styles.passwordToggle}
                onPress={() => setShowConfirmPassword(!showConfirmPassword)}
              >
                <Icon
                  name={showConfirmPassword ? 'visibility' : 'visibility-off'}
                  size={20}
                  color="#666"
                />
              </TouchableOpacity>
            </View>
            {errors.confirmPassword && (
              <Text style={styles.fieldErrorText}>{errors.confirmPassword}</Text>
            )}
          </View>

          {/* 协议同意 */}
          <View style={styles.agreementContainer}>
            <TouchableOpacity
              style={styles.checkboxContainer}
              onPress={() => setAgreeToTerms(!agreeToTerms)}
            >
              <Icon
                name={agreeToTerms ? 'check-box' : 'check-box-outline-blank'}
                size={20}
                color={agreeToTerms ? '#2196F3' : '#ccc'}
              />
            </TouchableOpacity>
            <View style={styles.agreementTextContainer}>
              <Text style={styles.agreementText}>我已阅读并同意</Text>
              <TouchableOpacity onPress={viewTerms}>
                <Text style={styles.linkText}>《用户协议》</Text>
              </TouchableOpacity>
              <Text style={styles.agreementText}>和</Text>
              <TouchableOpacity onPress={viewPrivacyPolicy}>
                <Text style={styles.linkText}>《隐私政策》</Text>
              </TouchableOpacity>
            </View>
          </View>
          {errors.agreement && (
            <Text style={styles.fieldErrorText}>{errors.agreement}</Text>
          )}

          {/* 注册按钮 */}
          <TouchableOpacity
            style={[styles.registerButton, isLoading && styles.registerButtonDisabled]}
            onPress={handleRegister}
            disabled={isLoading}
            activeOpacity={0.8}
          >
            {isLoading ? (
              <ActivityIndicator size="small" color="#ffffff" />
            ) : (
              <Text style={styles.registerButtonText}>创建账户</Text>
            )}
          </TouchableOpacity>
        </View>

        {/* 底部登录链接 */}
        <View style={styles.bottomContainer}>
          <Text style={styles.bottomText}>已有账户？</Text>
          <TouchableOpacity onPress={navigateToLogin}>
            <Text style={styles.loginText}>立即登录</Text>
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
    paddingTop: 40,
    paddingBottom: 40,
  },
  header: {
    alignItems: 'center',
    marginBottom: 30,
  },
  backButton: {
    position: 'absolute',
    left: 0,
    top: 20,
    padding: 8,
  },
  logoContainer: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#f0f8ff',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 20,
    marginTop: 40,
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
  agreementContainer: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 30,
  },
  checkboxContainer: {
    marginRight: 8,
    marginTop: 2,
  },
  agreementTextContainer: {
    flex: 1,
    flexDirection: 'row',
    flexWrap: 'wrap',
    alignItems: 'center',
  },
  agreementText: {
    color: '#666',
    fontSize: 14,
    lineHeight: 20,
  },
  linkText: {
    color: '#2196F3',
    fontSize: 14,
    fontWeight: '500',
    lineHeight: 20,
  },
  registerButton: {
    backgroundColor: '#2196F3',
    borderRadius: 12,
    height: 50,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 20,
    shadowColor: '#2196F3',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  registerButtonDisabled: {
    backgroundColor: '#ccc',
    shadowOpacity: 0,
    elevation: 0,
  },
  registerButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: 'bold',
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
  loginText: {
    color: '#2196F3',
    fontSize: 14,
    fontWeight: 'bold',
    marginLeft: 4,
  },
});

export default RegisterScreen;