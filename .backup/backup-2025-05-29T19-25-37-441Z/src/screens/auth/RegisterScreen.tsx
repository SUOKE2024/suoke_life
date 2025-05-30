import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  StatusBar,
  SafeAreaView,
  Animated,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  Alert,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { useDispatch, useSelector } from 'react-redux';
import { AuthStackParamList } from '../../types/navigation';
import { RootState } from '../../types';
import { colors, spacing, fonts, borderRadius, shadows } from '../../constants/theme';
import { AuthInput } from '../../components/common/AuthInput';
import { AuthButton } from '../../components/common/AuthButton';
import { LoadingScreen } from '../../components/common/LoadingScreen';
import { authService } from '../../services/authService';

type RegisterScreenNavigationProp = NativeStackNavigationProp<
  AuthStackParamList,
  'Register'
>;

interface FormData {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
  phone?: string;
}

interface FormErrors {
  username?: string;
  email?: string;
  password?: string;
  confirmPassword?: string;
  phone?: string;
  general?: string;
}

export const RegisterScreen: React.FC = () => {
  const navigation = useNavigation<RegisterScreenNavigationProp>();
  const dispatch = useDispatch();
  const { loading } = useSelector((state: RootState) => state.auth);

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
  const [agreeToTerms, setAgreeToTerms] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // 动画值
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(30)).current;
  const shakeAnim = useRef(new Animated.Value(0)).current;

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

  // 表单验证
  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    // 用户名验证
    if (!formData.username.trim()) {
      newErrors.username = '请输入用户名';
    } else if (formData.username.length < 2) {
      newErrors.username = '用户名至少需要2个字符';
    } else if (formData.username.length > 20) {
      newErrors.username = '用户名不能超过20个字符';
    } else if (!/^[a-zA-Z0-9\u4e00-\u9fa5_]+$/.test(formData.username)) {
      newErrors.username = '用户名只能包含字母、数字、中文和下划线';
    }

    // 邮箱验证
    if (!formData.email.trim()) {
      newErrors.email = '请输入邮箱地址';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = '请输入有效的邮箱地址';
    }

    // 密码验证
    if (!formData.password) {
      newErrors.password = '请输入密码';
    } else if (formData.password.length < 8) {
      newErrors.password = '密码至少需要8位字符';
    } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(formData.password)) {
      newErrors.password = '密码需要包含大小写字母和数字';
    }

    // 确认密码验证
    if (!formData.confirmPassword) {
      newErrors.confirmPassword = '请确认密码';
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = '两次输入的密码不一致';
    }

    // 手机号验证（可选）
    if (formData.phone && formData.phone.trim()) {
      if (!/^1[3-9]\d{9}$/.test(formData.phone)) {
        newErrors.phone = '请输入有效的手机号码';
      }
    }

    // 用户协议验证
    if (!agreeToTerms) {
      newErrors.general = '请阅读并同意用户协议和隐私政策';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // 震动动画
  const triggerShakeAnimation = () => {
    Animated.sequence([
      Animated.timing(shakeAnim, {
        toValue: 10,
        duration: 100,
        useNativeDriver: true,
      }),
      Animated.timing(shakeAnim, {
        toValue: -10,
        duration: 100,
        useNativeDriver: true,
      }),
      Animated.timing(shakeAnim, {
        toValue: 10,
        duration: 100,
        useNativeDriver: true,
      }),
      Animated.timing(shakeAnim, {
        toValue: 0,
        duration: 100,
        useNativeDriver: true,
      }),
    ]).start();
  };

  // 处理注册
  const handleRegister = async () => {
    if (!validateForm()) {
      triggerShakeAnimation();
      return;
    }

    setIsLoading(true);
    setErrors({});

    try {
      const response = await authService.register({
        username: formData.username.trim(),
        email: formData.email.trim(),
        password: formData.password,
        phone: formData.phone?.trim() || undefined,
      });

      // 注册成功
      console.log('注册成功:', response.user.username);
      Alert.alert(
        '注册成功',
        '欢迎加入索克生活！',
        [
          {
            text: '开始体验',
            onPress: () => {
              // 这里应该通过Redux更新认证状态
              // dispatch(registerSuccess(response));
            },
          },
        ]
      );
      
    } catch (error: any) {
      console.error('注册失败:', error.message);
      setErrors({ general: error.message || '注册失败，请重试' });
      triggerShakeAnimation();
    } finally {
      setIsLoading(false);
    }
  };

  // 处理登录
  const handleLogin = () => {
    navigation.navigate('Login');
  };

  // 返回欢迎页
  const handleBack = () => {
    navigation.goBack();
  };

  // 更新表单数据
  const updateFormData = (field: keyof FormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // 清除对应字段的错误
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  // 检查密码强度
  const getPasswordStrength = (password: string): { level: number; text: string; color: string } => {
    if (!password) {return { level: 0, text: '', color: colors.textSecondary };}
    
    let score = 0;
    if (password.length >= 8) {score++;}
    if (/[a-z]/.test(password)) {score++;}
    if (/[A-Z]/.test(password)) {score++;}
    if (/\d/.test(password)) {score++;}
    if (/[^a-zA-Z\d]/.test(password)) {score++;}

    if (score <= 2) {return { level: 1, text: '弱', color: colors.error };}
    if (score <= 3) {return { level: 2, text: '中', color: colors.warning };}
    return { level: 3, text: '强', color: colors.success };
  };

  const passwordStrength = getPasswordStrength(formData.password);

  if (isLoading) {
    return <LoadingScreen message="正在注册..." />;
  }

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor={colors.background} />
      
      <KeyboardAvoidingView
        style={styles.keyboardAvoid}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <ScrollView
          style={styles.scrollView}
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
          keyboardShouldPersistTaps="handled"
        >
          {/* 头部区域 */}
          <Animated.View
            style={[
              styles.header,
              {
                opacity: fadeAnim,
                transform: [{ translateY: slideAnim }],
              },
            ]}
          >
            <TouchableOpacity style={styles.backButton} onPress={handleBack}>
              <Text style={styles.backButtonText}>←</Text>
            </TouchableOpacity>
            
            <View style={styles.titleContainer}>
              <Text style={styles.title}>创建账户</Text>
              <Text style={styles.subtitle}>加入索克生活，开启健康之旅</Text>
            </View>
          </Animated.View>

          {/* 表单区域 */}
          <Animated.View
            style={[
              styles.formContainer,
              {
                opacity: fadeAnim,
                transform: [
                  { translateY: slideAnim },
                  { translateX: shakeAnim },
                ],
              },
            ]}
          >
            {/* 错误提示 */}
            {errors.general && (
              <View style={styles.errorContainer}>
                <Text style={styles.errorText}>{errors.general}</Text>
              </View>
            )}

            {/* 用户名输入 */}
            <AuthInput
              label="用户名"
              placeholder="请输入用户名"
              value={formData.username}
              onChangeText={(value) => updateFormData('username', value)}
              error={errors.username}
              autoCapitalize="none"
              icon="👤"
              maxLength={20}
              counter
            />

            {/* 邮箱输入 */}
            <AuthInput
              label="邮箱地址"
              placeholder="请输入您的邮箱"
              value={formData.email}
              onChangeText={(value) => updateFormData('email', value)}
              error={errors.email}
              keyboardType="email-address"
              autoCapitalize="none"
              autoComplete="email"
              icon="📧"
            />

            {/* 手机号输入（可选） */}
            <AuthInput
              label="手机号码（可选）"
              placeholder="请输入您的手机号"
              value={formData.phone}
              onChangeText={(value) => updateFormData('phone', value)}
              error={errors.phone}
              keyboardType="phone-pad"
              icon="📱"
              maxLength={11}
            />

            {/* 密码输入 */}
            <View style={styles.passwordContainer}>
              <AuthInput
                label="密码"
                placeholder="请输入密码"
                value={formData.password}
                onChangeText={(value) => updateFormData('password', value)}
                error={errors.password}
                secureTextEntry={!showPassword}
                icon="🔒"
                rightIcon={showPassword ? "👁️" : "👁️‍🗨️"}
                onRightIconPress={() => setShowPassword(!showPassword)}
              />
              {/* 密码强度指示器 */}
              {formData.password && (
                <View style={styles.passwordStrengthContainer}>
                  <Text style={styles.passwordStrengthLabel}>密码强度：</Text>
                  <View style={styles.passwordStrengthBar}>
                    <View
                      style={[
                        styles.passwordStrengthFill,
                        {
                          width: `${(passwordStrength.level / 3) * 100}%`,
                          backgroundColor: passwordStrength.color,
                        },
                      ]}
                    />
                  </View>
                  <Text style={[styles.passwordStrengthText, { color: passwordStrength.color }]}>
                    {passwordStrength.text}
                  </Text>
                </View>
              )}
            </View>

            {/* 确认密码输入 */}
            <AuthInput
              label="确认密码"
              placeholder="请再次输入密码"
              value={formData.confirmPassword}
              onChangeText={(value) => updateFormData('confirmPassword', value)}
              error={errors.confirmPassword}
              secureTextEntry={!showConfirmPassword}
              icon="🔒"
              rightIcon={showConfirmPassword ? "👁️" : "👁️‍🗨️"}
              onRightIconPress={() => setShowConfirmPassword(!showConfirmPassword)}
            />

            {/* 用户协议 */}
            <View style={styles.termsContainer}>
              <TouchableOpacity
                style={styles.checkboxContainer}
                onPress={() => setAgreeToTerms(!agreeToTerms)}
              >
                <View style={[styles.checkbox, agreeToTerms && styles.checkboxChecked]}>
                  {agreeToTerms && <Text style={styles.checkmark}>✓</Text>}
                </View>
                <Text style={styles.termsText}>
                  我已阅读并同意{' '}
                  <Text style={styles.linkText}>《用户协议》</Text>
                  {' '}和{' '}
                  <Text style={styles.linkText}>《隐私政策》</Text>
                </Text>
              </TouchableOpacity>
            </View>

            {/* 注册按钮 */}
            <AuthButton
              title="创建账户"
              onPress={handleRegister}
              loading={isLoading}
              style={styles.registerButton}
            />

            {/* 分割线 */}
            <View style={styles.dividerContainer}>
              <View style={styles.divider} />
              <Text style={styles.dividerText}>或</Text>
              <View style={styles.divider} />
            </View>

            {/* 第三方注册 */}
            <View style={styles.socialLoginContainer}>
              <TouchableOpacity style={styles.socialButton}>
                <Text style={styles.socialButtonText}>🍎 Apple注册</Text>
              </TouchableOpacity>
              
              <TouchableOpacity style={styles.socialButton}>
                <Text style={styles.socialButtonText}>📱 微信注册</Text>
              </TouchableOpacity>
            </View>
          </Animated.View>

          {/* 底部登录链接 */}
          <Animated.View
            style={[
              styles.footer,
              {
                opacity: fadeAnim,
                transform: [{ translateY: slideAnim }],
              },
            ]}
          >
            <Text style={styles.footerText}>
              已有账户？{' '}
              <TouchableOpacity onPress={handleLogin}>
                <Text style={styles.loginLink}>立即登录</Text>
              </TouchableOpacity>
            </Text>
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
  keyboardAvoid: {
    flex: 1,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    paddingHorizontal: spacing.lg,
  },
  header: {
    paddingTop: spacing.lg,
    paddingBottom: spacing.xl,
  },
  backButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.surface,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: spacing.lg,
    ...shadows.sm,
  },
  backButtonText: {
    fontSize: 20,
    color: colors.text,
  },
  titleContainer: {
    alignItems: 'center',
  },
  title: {
    fontSize: fonts.size.header,
    fontWeight: 'bold',
    color: colors.text,
    marginBottom: spacing.sm,
  },
  subtitle: {
    fontSize: fonts.size.md,
    color: colors.textSecondary,
    textAlign: 'center',
  },
  formContainer: {
    flex: 1,
    paddingVertical: spacing.lg,
  },
  errorContainer: {
    backgroundColor: colors.error + '20',
    borderColor: colors.error,
    borderWidth: 1,
    borderRadius: borderRadius.md,
    padding: spacing.md,
    marginBottom: spacing.lg,
  },
  errorText: {
    color: colors.error,
    fontSize: fonts.size.sm,
    textAlign: 'center',
  },
  passwordContainer: {
    marginBottom: spacing.lg,
  },
  passwordStrengthContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: spacing.sm,
    paddingHorizontal: spacing.sm,
  },
  passwordStrengthLabel: {
    fontSize: fonts.size.xs,
    color: colors.textSecondary,
    marginRight: spacing.sm,
  },
  passwordStrengthBar: {
    flex: 1,
    height: 4,
    backgroundColor: colors.border,
    borderRadius: 2,
    marginRight: spacing.sm,
    overflow: 'hidden',
  },
  passwordStrengthFill: {
    height: '100%',
    borderRadius: 2,
  },
  passwordStrengthText: {
    fontSize: fonts.size.xs,
    fontWeight: '500',
    minWidth: 20,
  },
  termsContainer: {
    marginVertical: spacing.lg,
  },
  checkboxContainer: {
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  checkbox: {
    width: 20,
    height: 20,
    borderWidth: 2,
    borderColor: colors.border,
    borderRadius: 4,
    marginRight: spacing.sm,
    marginTop: 2,
    justifyContent: 'center',
    alignItems: 'center',
  },
  checkboxChecked: {
    backgroundColor: colors.primary,
    borderColor: colors.primary,
  },
  checkmark: {
    color: colors.white,
    fontSize: 12,
    fontWeight: 'bold',
  },
  termsText: {
    flex: 1,
    fontSize: fonts.size.sm,
    color: colors.text,
    lineHeight: fonts.lineHeight.md,
  },
  linkText: {
    color: colors.primary,
    fontWeight: '500',
    textDecorationLine: 'underline',
  },
  registerButton: {
    marginTop: spacing.lg,
  },
  dividerContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: spacing.xl,
  },
  divider: {
    flex: 1,
    height: 1,
    backgroundColor: colors.border,
  },
  dividerText: {
    marginHorizontal: spacing.md,
    fontSize: fonts.size.sm,
    color: colors.textSecondary,
  },
  socialLoginContainer: {
    gap: spacing.md,
  },
  socialButton: {
    backgroundColor: colors.surface,
    paddingVertical: spacing.md,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    ...shadows.sm,
  },
  socialButtonText: {
    fontSize: fonts.size.md,
    color: colors.text,
    textAlign: 'center',
    fontWeight: '500',
  },
  footer: {
    paddingVertical: spacing.xl,
    alignItems: 'center',
  },
  footerText: {
    fontSize: fonts.size.sm,
    color: colors.textSecondary,
  },
  loginLink: {
    color: colors.primary,
    fontWeight: '600',
    textDecorationLine: 'underline',
  },
});
