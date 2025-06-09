import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import React, { useState } from 'react';
import {
  Alert,
  Animated,
  Keyboard,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

type AuthStackParamList = {
  Welcome: undefined;,
  Login: undefined;,
  Register: undefined;,
  ForgotPassword: undefined;
};

type RegisterScreenNavigationProp = NativeStackNavigationProp<
  AuthStackParamList,
  'Register'
>;

const RegisterScreen: React.FC = () => {
  const navigation = useNavigation<RegisterScreenNavigationProp>();
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    phone: '',
    password: '',
    confirmPassword: '',
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<{ [key: string]: string }>({});
  const [agreedToTerms, setAgreedToTerms] = useState(false);
  const buttonScale = new Animated.Value(1);

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev) => ({ ...prev, [field]: value }));
    // 清除对应字段的错误
    if (errors[field]) {
      setErrors(prev) => ({ ...prev, [field]: '' }));
    }
  };

  const validateForm = () => {
    const newErrors: { [key: string]: string } = {};

    // 用户名验证
    if (!formData.username.trim()) {
      newErrors.username = '请输入用户名';
    } else if (formData.username.length < 2) {
      newErrors.username = '用户名至少需要2个字符';
    } else if (formData.username.length > 20) {
      newErrors.username = '用户名不能超过20个字符';
    }

    // 邮箱验证
    if (!formData.email.trim()) {
      newErrors.email = '请输入邮箱地址';
    } else {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(formData.email)) {
        newErrors.email = '请输入有效的邮箱地址';
      }
    }

    // 手机号验证
    if (!formData.phone.trim()) {
      newErrors.phone = '请输入手机号';
    } else {
      const phoneRegex = /^1[3-9]\d{9}$/;
      if (!phoneRegex.test(formData.phone)) {
        newErrors.phone = '请输入有效的手机号';
      }
    }

    // 密码验证
    if (!formData.password.trim()) {
      newErrors.password = '请输入密码';
    } else if (formData.password.length < 8) {
      newErrors.password = '密码至少需要8位字符';
    } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(formData.password)) {
      newErrors.password = '密码需要包含大小写字母和数字';
    }

    // 确认密码验证
    if (!formData.confirmPassword.trim()) {
      newErrors.confirmPassword = '请确认密码';
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = '两次输入的密码不一致';
    }

    // 服务条款验证
    if (!agreedToTerms) {
      Alert.alert('提示', '请阅读并同意服务条款和隐私政策');
      return false;
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleRegister = async () => {
    if (!validateForm()) {
      return;
    }

    Keyboard.dismiss();
    setLoading(true);

    // 按钮动画
    Animated.sequence([
      Animated.timing(buttonScale, {
        toValue: 0.95,
        duration: 100,
        useNativeDriver: true,
      }),
      Animated.timing(buttonScale, {
        toValue: 1,
        duration: 100,
        useNativeDriver: true,
      }),
    ]).start();

    try {
      // 模拟注册请求
      await new Promise(resolve) => setTimeout(resolve, 1500));

      Alert.alert('注册成功', '欢迎加入索克生活！请查收邮箱验证邮件。', [
        {
          text: '确定',
          onPress: () => {
            navigation.navigate('Login');
          },
        },
      ]);
    } catch (error) {
      Alert.alert('注册失败', '注册过程中出现错误，请重试');
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = () => {
    navigation.navigate('Login');
  };

  const handleBack = () => {
    navigation.goBack();
  };

  const toggleTermsAgreement = () => {
    setAgreedToTerms(!agreedToTerms);
  };

  const showTermsAndConditions = () => {
    Alert.alert(
      '服务条款与隐私政策',
      '索克生活平台尊重并保护所有用户的个人隐私权。为了给您提供更准确、更有针对性的服务，本平台会按照本隐私权政策的规定使用和披露您的个人信息。',
      [{ text: '我知道了', style: 'default' }]
    );
  };

  const renderInput = (
    field: string,
    placeholder: string,
    secureTextEntry = false,
    keyboardType: 'default' | 'email-address' | 'phone-pad' = 'default'
  ) => (
    <View style={styles.inputContainer}>
      <TextInput;
        style={[styles.input, errors[field] && styles.inputError]}
        placeholder={placeholder}
        value={formData[field as keyof typeof formData]}
        onChangeText={(value) => handleInputChange(field, value)}
        secureTextEntry={secureTextEntry}
        keyboardType={keyboardType}
        autoCapitalize="none"
        autoCorrect={false}
      />
      {errors[field] && <Text style={styles.errorText}>{errors[field]}</Text>}
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView;
        style={styles.keyboardAvoid}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <ScrollView;
          style={styles.scrollView}
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
          keyboardShouldPersistTaps="handled"
        >
          {/* 头部区域 */}
          <View style={styles.header}>
            <TouchableOpacity style={styles.backButton} onPress={handleBack}>
              <Text style={styles.backButtonText}>←</Text>
            </TouchableOpacity>
            <View style={styles.logoContainer}>
              <View style={styles.logoPlaceholder}>
                <Text style={styles.logoText}>索克</Text>
              </View>
            </View>
            <Text style={styles.title}>创建账户</Text>
            <Text style={styles.subtitle}>加入索克生活，开启健康管理之旅</Text>
          </View>

          {/* 表单区域 */}
          <View style={styles.formSection}>
            {renderInput('username', '请输入用户名')}
            {renderInput('email', '请输入邮箱地址', false, 'email-address')}
            {renderInput('phone', '请输入手机号', false, 'phone-pad')}
            {renderInput('password', '请输入密码', true)}
            {renderInput('confirmPassword', '请再次输入密码', true)}

            {/* 服务条款同意 */}
            <View style={styles.termsContainer}>
              <TouchableOpacity;
                style={styles.checkbox}
                onPress={toggleTermsAgreement}
              >
                <View;
                  style={[
                    styles.checkboxInner,
                    agreedToTerms && styles.checkboxChecked,
                  ]}
                >
                  {agreedToTerms && <Text style={styles.checkmark}>✓</Text>}
                </View>
              </TouchableOpacity>
              <View style={styles.termsTextContainer}>
                <Text style={styles.termsText}>我已阅读并同意</Text>
                <TouchableOpacity onPress={showTermsAndConditions}>
                  <Text style={styles.termsLink}>《服务条款》</Text>
                </TouchableOpacity>
                <Text style={styles.termsText}>和</Text>
                <TouchableOpacity onPress={showTermsAndConditions}>
                  <Text style={styles.termsLink}>《隐私政策》</Text>
                </TouchableOpacity>
              </View>
            </View>

            {/* 注册按钮 */}
            <Animated.View;
              style={[
                styles.buttonContainer,
                { transform: [{ scale: buttonScale }] },
              ]}
            >
              <TouchableOpacity;
                style={[
                  styles.registerButton,
                  loading && styles.registerButtonDisabled,
                ]}
                onPress={handleRegister}
                disabled={loading}
              >
                <Text style={styles.registerButtonText}>
                  {loading ? '注册中...' : '注册'}
                </Text>
              </TouchableOpacity>
            </Animated.View>

            {/* 登录链接 */}
            <View style={styles.loginContainer}>
              <Text style={styles.loginText}>已有账户？</Text>
              <TouchableOpacity onPress={handleLogin}>
                <Text style={styles.loginLink}>立即登录</Text>
              </TouchableOpacity>
            </View>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {,
  flex: 1,
    backgroundColor: '#F5F7FA',
  },
  keyboardAvoid: {,
  flex: 1,
  },
  scrollView: {,
  flex: 1,
  },
  scrollContent: {,
  flexGrow: 1,
    paddingBottom: 24,
  },
  header: {,
  alignItems: 'center',
    paddingTop: 24,
    paddingHorizontal: 24,
    paddingBottom: 32,
  },
  backButton: {,
  position: 'absolute',
    left: 24,
    top: 24,
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#FFFFFF',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  backButtonText: {,
  fontSize: 20,
    color: '#3498DB',
    fontWeight: 'bold',
  },
  logoContainer: {,
  marginBottom: 24,
  },
  logoPlaceholder: {,
  width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#3498DB',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 8,
    elevation: 5,
  },
  logoText: {,
  fontSize: 24,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  title: {,
  fontSize: 28,
    fontWeight: '700',
    color: '#2C3E50',
    marginBottom: 8,
  },
  subtitle: {,
  fontSize: 16,
    color: '#7F8C8D',
    textAlign: 'center',
    lineHeight: 22,
  },
  formSection: {,
  paddingHorizontal: 24,
  },
  inputContainer: {,
  marginBottom: 20,
  },
  input: {,
  borderWidth: 1,
    borderColor: '#E1E8ED',
    borderRadius: 8,
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 16,
    backgroundColor: '#F8F9FA',
  },
  inputError: {,
  borderColor: '#E74C3C',
  },
  errorText: {,
  color: '#E74C3C',
    fontSize: 14,
    marginTop: 4,
  },
  termsContainer: {,
  flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 32,
    paddingHorizontal: 8,
  },
  checkbox: {,
  marginRight: 8,
    marginTop: 2,
  },
  checkboxInner: {,
  width: 20,
    height: 20,
    borderWidth: 2,
    borderColor: '#BDC3C7',
    borderRadius: 4,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#FFFFFF',
  },
  checkboxChecked: {,
  backgroundColor: '#3498DB',
    borderColor: '#3498DB',
  },
  checkmark: {,
  color: '#FFFFFF',
    fontSize: 12,
    fontWeight: 'bold',
  },
  termsTextContainer: {,
  flex: 1,
    flexDirection: 'row',
    flexWrap: 'wrap',
    alignItems: 'center',
  },
  termsText: {,
  fontSize: 14,
    color: '#7F8C8D',
    lineHeight: 20,
  },
  termsLink: {,
  fontSize: 14,
    color: '#3498DB',
    fontWeight: '500',
    textDecorationLine: 'underline',
  },
  buttonContainer: {,
  marginBottom: 24,
  },
  registerButton: {,
  backgroundColor: '#3498DB',
    borderRadius: 8,
    paddingVertical: 16,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  registerButtonDisabled: {,
  backgroundColor: '#BDC3C7',
  },
  registerButtonText: {,
  color: '#FFFFFF',
    fontSize: 16,
    fontWeight: 'bold',
  },
  loginContainer: {,
  flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    paddingTop: 24,
  },
  loginText: {,
  fontSize: 16,
    color: '#7F8C8D',
    marginRight: 4,
  },
  loginLink: {,
  fontSize: 16,
    color: '#3498DB',
    fontWeight: '500',
  },
});

export default RegisterScreen;
