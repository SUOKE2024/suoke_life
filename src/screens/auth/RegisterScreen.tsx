import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  SafeAreaView,
  StatusBar,
  Alert,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  Animated,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { useDispatch, useSelector } from 'react-redux';
import { AuthStackParamList } from '../../navigation/AuthNavigator';
import { register } from '../../store/slices/authSlice';
import {
  selectAuthLoading,
} from '../../store/slices/authSlice';
import { colors, spacing, fonts, borderRadius, shadows } from '../../constants/theme';

type RegisterScreenNavigationProp = NativeStackNavigationProp<
  AuthStackParamList,
  'Register'
>;

interface FormData {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
  phone: string;
}

interface FormErrors {
  username?: string;
  email?: string;
  password?: string;
  confirmPassword?: string;
  phone?: string;
}

interface FieldFocus {
  username: boolean;
  email: boolean;
  password: boolean;
  confirmPassword: boolean;
  phone: boolean;
}

export const RegisterScreen: React.FC = () => {
  const navigation = useNavigation<RegisterScreenNavigationProp>();
  const dispatch = useDispatch();
  const loading = useSelector(selectAuthLoading);

  const [formData, setFormData] = useState<FormData>({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    phone: '',
  });

  const [errors, setErrors] = useState<FormErrors>({});
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [currentStep, setCurrentStep] = useState(1);
  const [fieldFocus, setFieldFocus] = useState<FieldFocus>({
    username: false,
    email: false,
    password: false,
    confirmPassword: false,
    phone: false,
  });

  // 动画值
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(30)).current;
  const progressAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    // 启动入场动画
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 800,
        useNativeDriver: true,
      }),
      Animated.timing(slideAnim, {
        toValue: 0,
        duration: 600,
        useNativeDriver: true,
      }),
    ]).start();
  }, []);

  useEffect(() => {
    // 更新进度条
    const progress = calculateProgress();
    Animated.timing(progressAnim, {
      toValue: progress,
      duration: 300,
      useNativeDriver: false,
    }).start();
  }, [formData]);

  const calculateProgress = (): number => {
    const fields = ['username', 'email', 'password', 'confirmPassword'];
    const filledFields = fields.filter(field => formData[field as keyof FormData].trim() !== '');
    return filledFields.length / fields.length;
  };

  // 表单验证
  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    // 用户名验证
    if (!formData.username.trim()) {
      newErrors.username = '请输入用户名';
    } else if (formData.username.length < 2) {
      newErrors.username = '用户名至少2个字符';
    } else if (formData.username.length > 20) {
      newErrors.username = '用户名不能超过20个字符';
    }

    // 邮箱验证
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!formData.email.trim()) {
      newErrors.email = '请输入邮箱';
    } else if (!emailRegex.test(formData.email)) {
      newErrors.email = '请输入有效的邮箱地址';
    }

    // 密码验证
    if (!formData.password) {
      newErrors.password = '请输入密码';
    } else if (formData.password.length < 6) {
      newErrors.password = '密码至少6个字符';
    } else if (formData.password.length > 50) {
      newErrors.password = '密码不能超过50个字符';
    } else if (!/(?=.*[a-zA-Z])(?=.*\d)/.test(formData.password)) {
      newErrors.password = '密码必须包含字母和数字';
    }

    // 确认密码验证
    if (!formData.confirmPassword) {
      newErrors.confirmPassword = '请确认密码';
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = '两次输入的密码不一致';
    }

    // 手机号验证（可选）
    if (formData.phone.trim()) {
      const phoneRegex = /^1[3-9]\d{9}$/;
      if (!phoneRegex.test(formData.phone)) {
        newErrors.phone = '请输入有效的手机号';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleInputChange = (field: keyof FormData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    // 清除对应字段的错误
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: undefined }));
    }
  };

  const handleFocus = (field: keyof FieldFocus) => {
    setFieldFocus(prev => ({ ...prev, [field]: true }));
  };

  const handleBlur = (field: keyof FieldFocus) => {
    setFieldFocus(prev => ({ ...prev, [field]: false }));
  };

  const handleRegister = async () => {
    if (!validateForm()) {
      return;
    }

    try {
      const registerData = {
        username: formData.username.trim(),
        email: formData.email.trim().toLowerCase(),
        password: formData.password,
        phone: formData.phone.trim() || undefined,
      };

      await dispatch(register(registerData) as any);
      Alert.alert('注册成功', '欢迎加入索克生活！', [
        { text: '确定', onPress: () => navigation.navigate('Login') },
      ]);
    } catch (registerError) {
      Alert.alert('注册失败', '请检查您的信息并重试');
    }
  };

  const handleLogin = () => {
    navigation.navigate('Login');
  };

  const handleBack = () => {
    navigation.goBack();
  };

  const getPasswordStrength = (password: string): { strength: number; text: string; color: string } => {
    if (!password) return { strength: 0, text: '', color: colors.textSecondary };
    
    let strength = 0;
    if (password.length >= 6) strength += 1;
    if (password.length >= 8) strength += 1;
    if (/[A-Z]/.test(password)) strength += 1;
    if (/[a-z]/.test(password)) strength += 1;
    if (/\d/.test(password)) strength += 1;
    if (/[^A-Za-z0-9]/.test(password)) strength += 1;

    if (strength <= 2) return { strength: strength / 6, text: '弱', color: colors.error };
    if (strength <= 4) return { strength: strength / 6, text: '中', color: colors.warning };
    return { strength: strength / 6, text: '强', color: colors.success };
  };

  const passwordStrength = getPasswordStrength(formData.password);

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor={colors.background} />

      {/* 返回按钮 */}
      <TouchableOpacity style={styles.backButton} onPress={handleBack}>
        <Text style={styles.backButtonText}>←</Text>
      </TouchableOpacity>

      {/* 进度条 */}
      <View style={styles.progressContainer}>
        <View style={styles.progressBar}>
          <Animated.View 
            style={[
              styles.progressFill,
              {
                width: progressAnim.interpolate({
                  inputRange: [0, 1],
                  outputRange: ['0%', '100%'],
                })
              }
            ]} 
          />
        </View>
        <Text style={styles.progressText}>
          {Math.round(calculateProgress() * 100)}% 完成
        </Text>
      </View>

      <KeyboardAvoidingView
        style={styles.keyboardAvoid}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <ScrollView
          style={styles.scrollView}
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
        >
          <Animated.View 
            style={[
              styles.content,
              {
                opacity: fadeAnim,
                transform: [{ translateY: slideAnim }]
              }
            ]}
          >
            {/* 标题区域 */}
            <View style={styles.header}>
              <Text style={styles.title}>创建账户</Text>
              <Text style={styles.subtitle}>加入索克生活，开启健康之旅</Text>
            </View>

            {/* 表单区域 */}
            <View style={styles.form}>
              {/* 用户名 */}
              <View style={styles.inputContainer}>
                <Text style={[styles.label, fieldFocus.username && styles.labelFocused]}>
                  用户名 *
                </Text>
                <View style={[
                  styles.inputWrapper,
                  fieldFocus.username && styles.inputWrapperFocused,
                  errors.username && styles.inputWrapperError
                ]}>
                  <Text style={styles.inputIcon}>👤</Text>
                  <TextInput
                    style={styles.input}
                    value={formData.username}
                    onChangeText={(value) => handleInputChange('username', value)}
                    placeholder="请输入用户名"
                    placeholderTextColor={colors.placeholder}
                    autoCapitalize="none"
                    autoCorrect={false}
                    maxLength={20}
                    onFocus={() => handleFocus('username')}
                    onBlur={() => handleBlur('username')}
                  />
                  {formData.username.length > 0 && (
                    <Text style={styles.inputCounter}>{formData.username.length}/20</Text>
                  )}
                </View>
                {errors.username && (
                  <Animated.View style={styles.errorContainer}>
                    <Text style={styles.errorText}>{errors.username}</Text>
                  </Animated.View>
                )}
              </View>

              {/* 邮箱 */}
              <View style={styles.inputContainer}>
                <Text style={[styles.label, fieldFocus.email && styles.labelFocused]}>
                  邮箱地址 *
                </Text>
                <View style={[
                  styles.inputWrapper,
                  fieldFocus.email && styles.inputWrapperFocused,
                  errors.email && styles.inputWrapperError
                ]}>
                  <Text style={styles.inputIcon}>📧</Text>
                  <TextInput
                    style={styles.input}
                    value={formData.email}
                    onChangeText={(value) => handleInputChange('email', value)}
                    placeholder="请输入邮箱地址"
                    placeholderTextColor={colors.placeholder}
                    keyboardType="email-address"
                    autoCapitalize="none"
                    autoCorrect={false}
                    onFocus={() => handleFocus('email')}
                    onBlur={() => handleBlur('email')}
                  />
                </View>
                {errors.email && (
                  <Animated.View style={styles.errorContainer}>
                    <Text style={styles.errorText}>{errors.email}</Text>
                  </Animated.View>
                )}
              </View>

              {/* 密码 */}
              <View style={styles.inputContainer}>
                <Text style={[styles.label, fieldFocus.password && styles.labelFocused]}>
                  密码 *
                </Text>
                <View style={[
                  styles.inputWrapper,
                  fieldFocus.password && styles.inputWrapperFocused,
                  errors.password && styles.inputWrapperError
                ]}>
                  <Text style={styles.inputIcon}>🔒</Text>
                  <TextInput
                    style={styles.input}
                    value={formData.password}
                    onChangeText={(value) => handleInputChange('password', value)}
                    placeholder="请输入密码"
                    placeholderTextColor={colors.placeholder}
                    secureTextEntry={!showPassword}
                    autoCapitalize="none"
                    autoCorrect={false}
                    onFocus={() => handleFocus('password')}
                    onBlur={() => handleBlur('password')}
                  />
                  <TouchableOpacity
                    style={styles.eyeButton}
                    onPress={() => setShowPassword(!showPassword)}
                  >
                    <Text style={styles.eyeIcon}>
                      {showPassword ? '👁️' : '👁️‍🗨️'}
                    </Text>
                  </TouchableOpacity>
                </View>
                
                {/* 密码强度指示器 */}
                {formData.password.length > 0 && (
                  <View style={styles.passwordStrengthContainer}>
                    <View style={styles.passwordStrengthBar}>
                      <View 
                        style={[
                          styles.passwordStrengthFill,
                          { 
                            width: `${passwordStrength.strength * 100}%`,
                            backgroundColor: passwordStrength.color 
                          }
                        ]} 
                      />
                    </View>
                    <Text style={[styles.passwordStrengthText, { color: passwordStrength.color }]}>
                      密码强度: {passwordStrength.text}
                    </Text>
                  </View>
                )}
                
                {errors.password && (
                  <Animated.View style={styles.errorContainer}>
                    <Text style={styles.errorText}>{errors.password}</Text>
                  </Animated.View>
                )}
              </View>

              {/* 确认密码 */}
              <View style={styles.inputContainer}>
                <Text style={[styles.label, fieldFocus.confirmPassword && styles.labelFocused]}>
                  确认密码 *
                </Text>
                <View style={[
                  styles.inputWrapper,
                  fieldFocus.confirmPassword && styles.inputWrapperFocused,
                  errors.confirmPassword && styles.inputWrapperError
                ]}>
                  <Text style={styles.inputIcon}>🔐</Text>
                  <TextInput
                    style={styles.input}
                    value={formData.confirmPassword}
                    onChangeText={(value) => handleInputChange('confirmPassword', value)}
                    placeholder="请再次输入密码"
                    placeholderTextColor={colors.placeholder}
                    secureTextEntry={!showConfirmPassword}
                    autoCapitalize="none"
                    autoCorrect={false}
                    onFocus={() => handleFocus('confirmPassword')}
                    onBlur={() => handleBlur('confirmPassword')}
                  />
                  <TouchableOpacity
                    style={styles.eyeButton}
                    onPress={() => setShowConfirmPassword(!showConfirmPassword)}
                  >
                    <Text style={styles.eyeIcon}>
                      {showConfirmPassword ? '👁️' : '👁️‍🗨️'}
                    </Text>
                  </TouchableOpacity>
                </View>
                {errors.confirmPassword && (
                  <Animated.View style={styles.errorContainer}>
                    <Text style={styles.errorText}>{errors.confirmPassword}</Text>
                  </Animated.View>
                )}
              </View>

              {/* 手机号（可选） */}
              <View style={styles.inputContainer}>
                <Text style={[styles.label, fieldFocus.phone && styles.labelFocused]}>
                  手机号 (可选)
                </Text>
                <View style={[
                  styles.inputWrapper,
                  fieldFocus.phone && styles.inputWrapperFocused,
                  errors.phone && styles.inputWrapperError
                ]}>
                  <Text style={styles.inputIcon}>📱</Text>
                  <TextInput
                    style={styles.input}
                    value={formData.phone}
                    onChangeText={(value) => handleInputChange('phone', value)}
                    placeholder="请输入手机号"
                    placeholderTextColor={colors.placeholder}
                    keyboardType="phone-pad"
                    maxLength={11}
                    onFocus={() => handleFocus('phone')}
                    onBlur={() => handleBlur('phone')}
                  />
                </View>
                {errors.phone && (
                  <Animated.View style={styles.errorContainer}>
                    <Text style={styles.errorText}>{errors.phone}</Text>
                  </Animated.View>
                )}
              </View>

              {/* 注册按钮 */}
              <TouchableOpacity
                style={[
                  styles.registerButton,
                  loading && styles.registerButtonDisabled
                ]}
                onPress={handleRegister}
                disabled={loading}
                activeOpacity={0.8}
              >
                <Text style={styles.registerButtonText}>
                  {loading ? '注册中...' : '创建账户'}
                </Text>
                {loading && <View style={styles.loadingOverlay} />}
              </TouchableOpacity>

              {/* 服务条款 */}
              <Text style={styles.termsText}>
                注册即表示您同意我们的{' '}
                <Text style={styles.termsLink}>服务条款</Text>
                {' '}和{' '}
                <Text style={styles.termsLink}>隐私政策</Text>
              </Text>
            </View>

            {/* 登录链接 */}
            <View style={styles.footer}>
              <Text style={styles.footerText}>已有账户？</Text>
              <TouchableOpacity onPress={handleLogin}>
                <Text style={styles.loginLink}>立即登录</Text>
              </TouchableOpacity>
            </View>
          </Animated.View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  backButton: {
    position: 'absolute',
    top: spacing.lg,
    left: spacing.lg,
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: colors.surface,
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 1,
    ...shadows.sm,
  },
  backButtonText: {
    fontSize: 24,
    color: colors.text,
  },
  progressContainer: {
    paddingHorizontal: spacing.xl,
    paddingTop: spacing.xxl,
    paddingBottom: spacing.md,
  },
  progressBar: {
    height: 4,
    backgroundColor: colors.border,
    borderRadius: 2,
    overflow: 'hidden',
    marginBottom: spacing.sm,
  },
  progressFill: {
    height: '100%',
    backgroundColor: colors.primary,
    borderRadius: 2,
  },
  progressText: {
    fontSize: fonts.size.sm,
    color: colors.textSecondary,
    textAlign: 'center',
  },
  keyboardAvoid: {
    flex: 1,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
  },
  content: {
    flex: 1,
    paddingHorizontal: spacing.xl,
    paddingBottom: spacing.xl,
  },
  header: {
    marginBottom: spacing.xl,
    alignItems: 'center',
  },
  title: {
    fontSize: fonts.size.header,
    fontWeight: 'bold',
    color: colors.text,
    marginBottom: spacing.sm,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: fonts.size.lg,
    color: colors.textSecondary,
    textAlign: 'center',
  },
  form: {
    flex: 1,
  },
  inputContainer: {
    marginBottom: spacing.lg,
  },
  label: {
    fontSize: fonts.size.md,
    fontWeight: '600',
    color: colors.textSecondary,
    marginBottom: spacing.sm,
  },
  labelFocused: {
    color: colors.primary,
  },
  inputWrapper: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    borderWidth: 2,
    borderColor: colors.border,
    paddingHorizontal: spacing.md,
    ...shadows.sm,
  },
  inputWrapperFocused: {
    borderColor: colors.primary,
    ...shadows.md,
  },
  inputWrapperError: {
    borderColor: colors.error,
  },
  inputIcon: {
    fontSize: 20,
    marginRight: spacing.sm,
  },
  input: {
    flex: 1,
    paddingVertical: spacing.lg,
    fontSize: fonts.size.md,
    color: colors.text,
  },
  inputCounter: {
    fontSize: fonts.size.sm,
    color: colors.textSecondary,
    marginLeft: spacing.sm,
  },
  eyeButton: {
    padding: spacing.sm,
  },
  eyeIcon: {
    fontSize: 20,
  },
  passwordStrengthContainer: {
    marginTop: spacing.sm,
  },
  passwordStrengthBar: {
    height: 3,
    backgroundColor: colors.border,
    borderRadius: 1.5,
    overflow: 'hidden',
    marginBottom: spacing.xs,
  },
  passwordStrengthFill: {
    height: '100%',
    borderRadius: 1.5,
  },
  passwordStrengthText: {
    fontSize: fonts.size.xs,
    fontWeight: '500',
  },
  errorContainer: {
    marginTop: spacing.sm,
  },
  errorText: {
    fontSize: fonts.size.sm,
    color: colors.error,
    marginLeft: spacing.sm,
  },
  registerButton: {
    backgroundColor: colors.primary,
    paddingVertical: spacing.lg,
    borderRadius: borderRadius.lg,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: spacing.lg,
    position: 'relative',
    overflow: 'hidden',
    ...shadows.md,
  },
  registerButtonDisabled: {
    opacity: 0.7,
  },
  registerButtonText: {
    color: colors.white,
    fontSize: fonts.size.lg,
    fontWeight: 'bold',
  },
  loadingOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    borderRadius: borderRadius.lg,
  },
  termsText: {
    fontSize: fonts.size.sm,
    color: colors.textSecondary,
    textAlign: 'center',
    marginTop: spacing.md,
    lineHeight: 20,
  },
  termsLink: {
    color: colors.primary,
    fontWeight: '600',
    textDecorationLine: 'underline',
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: spacing.xl,
    paddingTop: spacing.lg,
  },
  footerText: {
    fontSize: fonts.size.md,
    color: colors.textSecondary,
    marginRight: spacing.sm,
  },
  loginLink: {
    fontSize: fonts.size.md,
    color: colors.primary,
    fontWeight: 'bold',
  },
});
