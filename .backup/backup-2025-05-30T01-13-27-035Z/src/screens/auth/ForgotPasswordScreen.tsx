import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { AuthStackParamList } from '../../types/navigation';
import { colors, spacing, fonts, borderRadius, shadows } from '../../constants/theme';
import { AuthInput } from '../../components/common/AuthInput';
import { AuthButton } from '../../components/common/AuthButton';
import { LoadingScreen } from '../../components/common/LoadingScreen';
import { authService } from '../../services/authService';

import React, { useState, useRef, useEffect } from 'react';
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

type ForgotPasswordScreenNavigationProp = NativeStackNavigationProp<
  AuthStackParamList,
  'ForgotPassword'
>;

type Step = 'email' | 'verification' | 'reset';

interface FormData {
  email: string;
  verificationCode: string;
  newPassword: string;
  confirmPassword: string;
}

interface FormErrors {
  email?: string;
  verificationCode?: string;
  newPassword?: string;
  confirmPassword?: string;
  general?: string;
}

export const ForgotPasswordScreen: React.FC = () => {
  const navigation = useNavigation<ForgotPasswordScreenNavigationProp>();

  const [currentStep, setCurrentStep] = useState<Step>('email');
  const [formData, setFormData] = useState<FormData>({
    email: '',
    verificationCode: '',
    newPassword: '',
    confirmPassword: '',
  });
  const [errors, setErrors] = useState<FormErrors>({});
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [countdown, setCountdown] = useState(0);

  // 动画值
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(30)).current;
  const shakeAnim = useRef(new Animated.Value(0)).current;
  const stepProgressAnim = useRef(new Animated.Value(0)).current;

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
    // 更新步骤进度动画
    const stepValue = currentStep === 'email' ? 0 : currentStep === 'verification' ? 0.5 : 1;
    Animated.timing(stepProgressAnim, {
      toValue: stepValue,
      duration: 300,
      useNativeDriver: false,
    }).start();
  }, [currentStep]);

  useEffect(() => {
    // 倒计时逻辑
    let timer: ReturnType<typeof setTimeout>;
    if (countdown > 0) {
      timer = setTimeout(() => setCountdown(countdown - 1), 1000);
    }
    return () => {
      if (timer) {clearTimeout(timer);}
    };
  }, [countdown]);

  // 表单验证
  const validateEmail = (): boolean => {
    const newErrors: FormErrors = {};

    if (!formData.email.trim()) {
      newErrors.email = '请输入邮箱地址';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = '请输入有效的邮箱地址';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const validateVerificationCode = (): boolean => {
    const newErrors: FormErrors = {};

    if (!formData.verificationCode.trim()) {
      newErrors.verificationCode = '请输入验证码';
    } else if (formData.verificationCode.length !== 6) {
      newErrors.verificationCode = '验证码应为6位数字';
    } else if (!/^\d{6}$/.test(formData.verificationCode)) {
      newErrors.verificationCode = '验证码只能包含数字';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const validatePassword = (): boolean => {
    const newErrors: FormErrors = {};

    if (!formData.newPassword) {
      newErrors.newPassword = '请输入新密码';
    } else if (formData.newPassword.length < 8) {
      newErrors.newPassword = '密码至少需要8位字符';
    } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(formData.newPassword)) {
      newErrors.newPassword = '密码需要包含大小写字母和数字';
    }

    if (!formData.confirmPassword) {
      newErrors.confirmPassword = '请确认新密码';
    } else if (formData.newPassword !== formData.confirmPassword) {
      newErrors.confirmPassword = '两次输入的密码不一致';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // 震动动画
  const triggerShakeAnimation = useCallback( () => {, []);
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

  // 发送验证码
  const handleSendVerificationCode = async () => {
    if (!validateEmail()) {
      triggerShakeAnimation();
      return;
    }

    setIsLoading(true);
    setErrors({});

    try {
      await authService.forgotPassword({ email: formData.email.trim() });
      setCurrentStep('verification');
      setCountdown(60); // 60秒倒计时
      Alert.alert('验证码已发送', '请查看您的邮箱并输入验证码');
    } catch (error: any) {
      console.error('发送验证码失败:', error.message);
      setErrors({ general: error.message || '发送验证码失败，请重试' });
      triggerShakeAnimation();
    } finally {
      setIsLoading(false);
    }
  };

  // 验证验证码
  const handleVerifyCode = async () => {
    if (!validateVerificationCode()) {
      triggerShakeAnimation();
      return;
    }

    setIsLoading(true);
    setErrors({});

    try {
      await authService.verifyResetCode({
        email: formData.email.trim(),
        code: formData.verificationCode.trim(),
      });
      setCurrentStep('reset');
    } catch (error: any) {
      console.error('验证码验证失败:', error.message);
      setErrors({ general: error.message || '验证码错误，请重试' });
      triggerShakeAnimation();
    } finally {
      setIsLoading(false);
    }
  };

  // 重置密码
  const handleResetPassword = async () => {
    if (!validatePassword()) {
      triggerShakeAnimation();
      return;
    }

    setIsLoading(true);
    setErrors({});

    try {
      await authService.resetPassword({
        email: formData.email.trim(),
        code: formData.verificationCode.trim(),
        newPassword: formData.newPassword,
      });

      Alert.alert(
        '密码重置成功',
        '您的密码已成功重置，请使用新密码登录',
        [
          {
            text: '去登录',
            onPress: () => navigation.navigate('Login'),
          },
        ]
      );
    } catch (error: any) {
      console.error('密码重置失败:', error.message);
      setErrors({ general: error.message || '密码重置失败，请重试' });
      triggerShakeAnimation();
    } finally {
      setIsLoading(false);
    }
  };

  // 重新发送验证码
  const handleResendCode = async () => {
    if (countdown > 0) {return;}

    setIsLoading(true);
    try {
      await authService.forgotPassword({ email: formData.email.trim() });
      setCountdown(60);
      Alert.alert('验证码已重新发送', '请查看您的邮箱');
    } catch (error: any) {
      Alert.alert('发送失败', error.message || '重新发送验证码失败');
    } finally {
      setIsLoading(false);
    }
  };

  // 返回上一步
  const handleBack = useCallback( () => {, []);
    if (currentStep === 'email') {
      navigation.goBack();
    } else if (currentStep === 'verification') {
      setCurrentStep('email');
    } else {
      setCurrentStep('verification');
    }
  };

  // 更新表单数据
  const updateFormData = useCallback( (field: keyof FormData, value: string) => {, []);
    setFormData(prev => ({ ...prev, [field]: value }));
    // 清除对应字段的错误
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  // 获取当前步骤信息
  const getStepInfo = useCallback( () => {, []);
    switch (currentStep) {
      case 'email':
        return {
          title: '忘记密码',
          subtitle: '请输入您的邮箱地址，我们将发送验证码',
          buttonText: '发送验证码',
          onPress: handleSendVerificationCode,
        };
      case 'verification':
        return {
          title: '验证邮箱',
          subtitle: `验证码已发送至 ${formData.email}`,
          buttonText: '验证',
          onPress: handleVerifyCode,
        };
      case 'reset':
        return {
          title: '重置密码',
          subtitle: '请设置您的新密码',
          buttonText: '重置密码',
          onPress: handleResetPassword,
        };
    }
  };

  const stepInfo = getStepInfo();

  if (isLoading) {
    return <LoadingScreen message="处理中..." />;
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
              <Text style={styles.title}>{stepInfo.title}</Text>
              <Text style={styles.subtitle}>{stepInfo.subtitle}</Text>
            </View>

            {/* 步骤进度指示器 */}
            <View style={styles.progressContainer}>
              <View style={styles.progressBar}>
                <Animated.View
                  style={[
                    styles.progressFill,
                    {
                      width: stepProgressAnim.interpolate({
                        inputRange: [0, 1],
                        outputRange: ['33%', '100%'],
                      }),
                    },
                  ]}
                />
              </View>
              <View style={styles.stepIndicators}>
                <View style={[styles.stepDot, styles.stepDotActive]}>
                  <Text style={styles.stepDotText}>1</Text>
                </View>
                <View style={[styles.stepDot, currentStep !== 'email' && styles.stepDotActive]}>
                  <Text style={[styles.stepDotText, currentStep !== 'email' && styles.stepDotTextActive]}>2</Text>
                </View>
                <View style={[styles.stepDot, currentStep === 'reset' && styles.stepDotActive]}>
                  <Text style={[styles.stepDotText, currentStep === 'reset' && styles.stepDotTextActive]}>3</Text>
                </View>
              </View>
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

            {/* 步骤1: 邮箱输入 */}
            {currentStep === 'email' && (
              <View style={styles.stepContent}>
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
              </View>
            )}

            {/* 步骤2: 验证码输入 */}
            {currentStep === 'verification' && (
              <View style={styles.stepContent}>
                <AuthInput
                  label="验证码"
                  placeholder="请输入6位验证码"
                  value={formData.verificationCode}
                  onChangeText={(value) => updateFormData('verificationCode', value)}
                  error={errors.verificationCode}
                  keyboardType="number-pad"
                  maxLength={6}
                  icon="🔢"
                />

                {/* 重新发送验证码 */}
                <View style={styles.resendContainer}>
                  <Text style={styles.resendText}>
                    没有收到验证码？{' '}
                  </Text>
                  <TouchableOpacity
                    onPress={handleResendCode}
                    disabled={countdown > 0}
                  >
                    <Text style={[styles.resendLink, countdown > 0 && styles.resendLinkDisabled]}>
                      {countdown > 0 ? `${countdown}s后重新发送` : '重新发送'}
                    </Text>
                  </TouchableOpacity>
                </View>
              </View>
            )}

            {/* 步骤3: 密码重置 */}
            {currentStep === 'reset' && (
              <View style={styles.stepContent}>
                <AuthInput
                  label="新密码"
                  placeholder="请输入新密码"
                  value={formData.newPassword}
                  onChangeText={(value) => updateFormData('newPassword', value)}
                  error={errors.newPassword}
                  secureTextEntry={!showPassword}
                  icon="🔒"
                  rightIcon={showPassword ? "👁️" : "👁️‍🗨️"}
                  onRightIconPress={() => setShowPassword(!showPassword)}
                />

                <AuthInput
                  label="确认新密码"
                  placeholder="请再次输入新密码"
                  value={formData.confirmPassword}
                  onChangeText={(value) => updateFormData('confirmPassword', value)}
                  error={errors.confirmPassword}
                  secureTextEntry={!showConfirmPassword}
                  icon="🔒"
                  rightIcon={showConfirmPassword ? "👁️" : "👁️‍🗨️"}
                  onRightIconPress={() => setShowConfirmPassword(!showConfirmPassword)}
                />

                {/* 密码要求提示 */}
                <View style={styles.passwordRequirements}>
                  <Text style={styles.requirementsTitle}>密码要求：</Text>
                  <Text style={styles.requirementItem}>• 至少8位字符</Text>
                  <Text style={styles.requirementItem}>• 包含大写字母</Text>
                  <Text style={styles.requirementItem}>• 包含小写字母</Text>
                  <Text style={styles.requirementItem}>• 包含数字</Text>
                </View>
              </View>
            )}

            {/* 操作按钮 */}
            <AuthButton
              title={stepInfo.buttonText}
              onPress={stepInfo.onPress}
              loading={isLoading}
              style={styles.actionButton}
            />
          </Animated.View>

          {/* 底部帮助信息 */}
          <Animated.View
            style={[
              styles.footer,
              {
                opacity: fadeAnim,
                transform: [{ translateY: slideAnim }],
              },
            ]}
          >
            <View style={styles.helpContainer}>
              <Text style={styles.helpText}>
                遇到问题？{' '}
                <Text style={styles.helpLink}>联系客服</Text>
              </Text>
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
    marginBottom: spacing.lg,
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
    lineHeight: fonts.lineHeight.md,
  },
  progressContainer: {
    marginTop: spacing.lg,
  },
  progressBar: {
    height: 4,
    backgroundColor: colors.border,
    borderRadius: 2,
    overflow: 'hidden',
    marginBottom: spacing.md,
  },
  progressFill: {
    height: '100%',
    backgroundColor: colors.primary,
    borderRadius: 2,
  },
  stepIndicators: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  stepDot: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: colors.border,
    justifyContent: 'center',
    alignItems: 'center',
  },
  stepDotActive: {
    backgroundColor: colors.primary,
  },
  stepDotText: {
    fontSize: fonts.size.sm,
    fontWeight: 'bold',
    color: colors.textSecondary,
  },
  stepDotTextActive: {
    color: colors.white,
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
  stepContent: {
    marginBottom: spacing.lg,
  },
  resendContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: spacing.md,
  },
  resendText: {
    fontSize: fonts.size.sm,
    color: colors.textSecondary,
  },
  resendLink: {
    fontSize: fonts.size.sm,
    color: colors.primary,
    fontWeight: '500',
    textDecorationLine: 'underline',
  },
  resendLinkDisabled: {
    color: colors.textSecondary,
    textDecorationLine: 'none',
  },
  passwordRequirements: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.md,
    padding: spacing.md,
    marginTop: spacing.md,
    borderWidth: 1,
    borderColor: colors.border,
  },
  requirementsTitle: {
    fontSize: fonts.size.sm,
    fontWeight: '600',
    color: colors.text,
    marginBottom: spacing.sm,
  },
  requirementItem: {
    fontSize: fonts.size.xs,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
  },
  actionButton: {
    marginTop: spacing.lg,
  },
  footer: {
    paddingVertical: spacing.xl,
    alignItems: 'center',
  },
  helpContainer: {
    alignItems: 'center',
  },
  helpText: {
    fontSize: fonts.size.sm,
    color: colors.textSecondary,
  },
  helpLink: {
    color: colors.primary,
    fontWeight: '500',
    textDecorationLine: 'underline',
  },
}); 