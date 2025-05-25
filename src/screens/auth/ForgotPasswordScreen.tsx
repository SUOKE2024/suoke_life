import React, { useState } from 'react';
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
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
// import { useDispatch } from 'react-redux';
import { AuthStackParamList } from '../../navigation/AuthNavigator';
import { colors, spacing } from '../../constants/theme';
import { apiClient } from '../../services/apiClient';

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
}

export const ForgotPasswordScreen: React.FC = () => {
  const navigation = useNavigation<ForgotPasswordScreenNavigationProp>();
  // const dispatch = useDispatch();

  const [currentStep, setCurrentStep] = useState<Step>('email');
  const [loading, setLoading] = useState(false);
  const [countdown, setCountdown] = useState(0);

  const [formData, setFormData] = useState<FormData>({
    email: '',
    verificationCode: '',
    newPassword: '',
    confirmPassword: '',
  });

  const [errors, setErrors] = useState<FormErrors>({});
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  // 验证邮箱格式
  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  // 验证密码强度
  const validatePassword = (password: string): boolean => {
    return password.length >= 6 && /(?=.*[a-zA-Z])(?=.*\d)/.test(password);
  };

  const handleInputChange = (field: keyof FormData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    // 清除对应字段的错误
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: undefined }));
    }
  };

  // 发送重置邮件
  const handleSendResetEmail = async () => {
    const newErrors: FormErrors = {};

    if (!formData.email.trim()) {
      newErrors.email = '请输入邮箱';
    } else if (!validateEmail(formData.email)) {
      newErrors.email = '请输入有效的邮箱地址';
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setLoading(true);
    try {
      const response = await apiClient.post('/auth/forgot-password', {
        email: formData.email.trim().toLowerCase(),
      });

      if (response.success) {
        Alert.alert('发送成功', '重置密码的验证码已发送到您的邮箱，请查收');
        setCurrentStep('verification');
        startCountdown();
      } else {
        Alert.alert('发送失败', response.error?.message || '请稍后重试');
      }
    } catch (error) {
      Alert.alert('发送失败', '网络错误，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  // 验证验证码
  const handleVerifyCode = async () => {
    const newErrors: FormErrors = {};

    if (!formData.verificationCode.trim()) {
      newErrors.verificationCode = '请输入验证码';
    } else if (formData.verificationCode.length !== 6) {
      newErrors.verificationCode = '验证码应为6位数字';
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setLoading(true);
    try {
      const response = await apiClient.post('/auth/verify-reset-code', {
        email: formData.email.trim().toLowerCase(),
        code: formData.verificationCode.trim(),
      });

      if (response.success) {
        setCurrentStep('reset');
      } else {
        Alert.alert(
          '验证失败',
          response.error?.message || '验证码错误或已过期'
        );
      }
    } catch (error) {
      Alert.alert('验证失败', '网络错误，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  // 重置密码
  const handleResetPassword = async () => {
    const newErrors: FormErrors = {};

    if (!formData.newPassword) {
      newErrors.newPassword = '请输入新密码';
    } else if (!validatePassword(formData.newPassword)) {
      newErrors.newPassword = '密码必须包含字母和数字，至少6个字符';
    }

    if (!formData.confirmPassword) {
      newErrors.confirmPassword = '请确认新密码';
    } else if (formData.newPassword !== formData.confirmPassword) {
      newErrors.confirmPassword = '两次输入的密码不一致';
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setLoading(true);
    try {
      const response = await apiClient.post('/auth/reset-password', {
        email: formData.email.trim().toLowerCase(),
        code: formData.verificationCode.trim(),
        newPassword: formData.newPassword,
      });

      if (response.success) {
        Alert.alert('重置成功', '密码已重置，请使用新密码登录', [
          { text: '确定', onPress: () => navigation.navigate('Login') },
        ]);
      } else {
        Alert.alert('重置失败', response.error?.message || '请稍后重试');
      }
    } catch (error) {
      Alert.alert('重置失败', '网络错误，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  // 重新发送验证码
  const handleResendCode = async () => {
    if (countdown > 0) {
      return;
    }

    setLoading(true);
    try {
      const response = await apiClient.post('/auth/forgot-password', {
        email: formData.email.trim().toLowerCase(),
      });

      if (response.success) {
        Alert.alert('发送成功', '验证码已重新发送');
        startCountdown();
      } else {
        Alert.alert('发送失败', response.error?.message || '请稍后重试');
      }
    } catch (error) {
      Alert.alert('发送失败', '网络错误，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  // 开始倒计时
  const startCountdown = () => {
    setCountdown(60);
    const timer = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  };

  const handleBack = () => {
    if (currentStep === 'email') {
      navigation.goBack();
    } else if (currentStep === 'verification') {
      setCurrentStep('email');
    } else {
      setCurrentStep('verification');
    }
  };

  const renderEmailStep = () => (
    <>
      <View style={styles.header}>
        <Text style={styles.title}>忘记密码</Text>
        <Text style={styles.subtitle}>
          请输入您的邮箱地址，我们将发送重置密码的验证码
        </Text>
      </View>

      <View style={styles.form}>
        <View style={styles.inputContainer}>
          <Text style={styles.label}>邮箱地址</Text>
          <TextInput
            style={[styles.input, errors.email ? styles.inputError : null]}
            value={formData.email}
            onChangeText={(value) => handleInputChange('email', value)}
            placeholder="请输入您的邮箱"
            keyboardType="email-address"
            autoCapitalize="none"
            autoCorrect={false}
          />
          {errors.email && <Text style={styles.errorText}>{errors.email}</Text>}
        </View>

        <TouchableOpacity
          style={[
            styles.primaryButton,
            loading && styles.primaryButtonDisabled,
          ]}
          onPress={handleSendResetEmail}
          disabled={loading}
        >
          <Text style={styles.primaryButtonText}>
            {loading ? '发送中...' : '发送验证码'}
          </Text>
        </TouchableOpacity>
      </View>
    </>
  );

  const renderVerificationStep = () => (
    <>
      <View style={styles.header}>
        <Text style={styles.title}>验证邮箱</Text>
        <Text style={styles.subtitle}>
          验证码已发送至 {formData.email}，请查收并输入6位验证码
        </Text>
      </View>

      <View style={styles.form}>
        <View style={styles.inputContainer}>
          <Text style={styles.label}>验证码</Text>
          <TextInput
            style={[
              styles.input,
              errors.verificationCode ? styles.inputError : null,
            ]}
            value={formData.verificationCode}
            onChangeText={(value) =>
              handleInputChange('verificationCode', value)
            }
            placeholder="请输入6位验证码"
            keyboardType="number-pad"
            maxLength={6}
          />
          {errors.verificationCode && (
            <Text style={styles.errorText}>{errors.verificationCode}</Text>
          )}
        </View>

        <TouchableOpacity
          style={[
            styles.primaryButton,
            loading && styles.primaryButtonDisabled,
          ]}
          onPress={handleVerifyCode}
          disabled={loading}
        >
          <Text style={styles.primaryButtonText}>
            {loading ? '验证中...' : '验证'}
          </Text>
        </TouchableOpacity>

        <View style={styles.resendContainer}>
          <Text style={styles.resendText}>没有收到验证码？</Text>
          <TouchableOpacity
            onPress={handleResendCode}
            disabled={countdown > 0 || loading}
          >
            <Text
              style={[
                styles.resendLink,
                (countdown > 0 || loading) && styles.resendLinkDisabled,
              ]}
            >
              {countdown > 0 ? `${countdown}秒后重发` : '重新发送'}
            </Text>
          </TouchableOpacity>
        </View>
      </View>
    </>
  );

  const renderResetStep = () => (
    <>
      <View style={styles.header}>
        <Text style={styles.title}>重置密码</Text>
        <Text style={styles.subtitle}>请设置您的新密码</Text>
      </View>

      <View style={styles.form}>
        <View style={styles.inputContainer}>
          <Text style={styles.label}>新密码</Text>
          <View
            style={[
              styles.passwordContainer,
              errors.newPassword ? styles.inputError : null,
            ]}
          >
            <TextInput
              style={styles.passwordInput}
              value={formData.newPassword}
              onChangeText={(value) => handleInputChange('newPassword', value)}
              placeholder="请输入新密码"
              secureTextEntry={!showPassword}
              autoCapitalize="none"
              autoCorrect={false}
              maxLength={50}
            />
            <TouchableOpacity
              style={styles.eyeButton}
              onPress={() => setShowPassword(!showPassword)}
            >
              <Text style={styles.eyeText}>
                {showPassword ? '隐藏' : '显示'}
              </Text>
            </TouchableOpacity>
          </View>
          {errors.newPassword && (
            <Text style={styles.errorText}>{errors.newPassword}</Text>
          )}
          <Text style={styles.passwordHint}>
            密码需包含字母和数字，至少6个字符
          </Text>
        </View>

        <View style={styles.inputContainer}>
          <Text style={styles.label}>确认新密码</Text>
          <View style={styles.passwordContainer}>
            <TextInput
              style={[
                styles.passwordInput,
                errors.confirmPassword ? styles.inputError : null,
              ]}
              value={formData.confirmPassword}
              onChangeText={(value) =>
                handleInputChange('confirmPassword', value)
              }
              placeholder="请再次输入新密码"
              secureTextEntry={!showConfirmPassword}
              autoCapitalize="none"
              autoCorrect={false}
              maxLength={50}
            />
            <TouchableOpacity
              style={styles.eyeButton}
              onPress={() => setShowConfirmPassword(!showConfirmPassword)}
            >
              <Text style={styles.eyeText}>
                {showConfirmPassword ? '隐藏' : '显示'}
              </Text>
            </TouchableOpacity>
          </View>
          {errors.confirmPassword && (
            <Text style={styles.errorText}>{errors.confirmPassword}</Text>
          )}
        </View>

        <TouchableOpacity
          style={[
            styles.primaryButton,
            loading && styles.primaryButtonDisabled,
          ]}
          onPress={handleResetPassword}
          disabled={loading}
        >
          <Text style={styles.primaryButtonText}>
            {loading ? '重置中...' : '重置密码'}
          </Text>
        </TouchableOpacity>
      </View>
    </>
  );

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
        >
          {/* 返回按钮 */}
          <TouchableOpacity style={styles.backButton} onPress={handleBack}>
            <Text style={styles.backButtonText}>← 返回</Text>
          </TouchableOpacity>

          {/* 步骤指示器 */}
          <View style={styles.stepIndicator}>
            <View
              style={[
                styles.step,
                currentStep === 'email' && styles.activeStep,
              ]}
            >
              <Text
                style={[
                  styles.stepText,
                  currentStep === 'email' && styles.activeStepText,
                ]}
              >
                1
              </Text>
            </View>
            <View style={styles.stepLine} />
            <View
              style={[
                styles.step,
                currentStep === 'verification' && styles.activeStep,
              ]}
            >
              <Text
                style={[
                  styles.stepText,
                  currentStep === 'verification' && styles.activeStepText,
                ]}
              >
                2
              </Text>
            </View>
            <View style={styles.stepLine} />
            <View
              style={[
                styles.step,
                currentStep === 'reset' && styles.activeStep,
              ]}
            >
              <Text
                style={[
                  styles.stepText,
                  currentStep === 'reset' && styles.activeStepText,
                ]}
              >
                3
              </Text>
            </View>
          </View>

          {/* 根据当前步骤渲染内容 */}
          {currentStep === 'email' && renderEmailStep()}
          {currentStep === 'verification' && renderVerificationStep()}
          {currentStep === 'reset' && renderResetStep()}

          {/* 登录链接 */}
          <View style={styles.footer}>
            <Text style={styles.footerText}>想起密码了？</Text>
            <TouchableOpacity onPress={() => navigation.navigate('Login')}>
              <Text style={styles.loginLink}>立即登录</Text>
            </TouchableOpacity>
          </View>
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
    paddingHorizontal: spacing.xl,
    paddingVertical: spacing.lg,
  },
  backButton: {
    alignSelf: 'flex-start',
    paddingVertical: spacing.sm,
    marginBottom: spacing.lg,
  },
  backButtonText: {
    fontSize: 16,
    color: colors.primary,
    fontWeight: '600',
  },
  stepIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.xxl,
  },
  step: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: colors.border,
    alignItems: 'center',
    justifyContent: 'center',
  },
  activeStep: {
    backgroundColor: colors.primary,
  },
  stepText: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.textSecondary,
  },
  activeStepText: {
    color: colors.surface,
  },
  stepLine: {
    flex: 1,
    height: 2,
    backgroundColor: colors.border,
    marginHorizontal: spacing.sm,
  },
  header: {
    marginBottom: spacing.xl,
    alignItems: 'center',
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: colors.text,
    marginBottom: spacing.sm,
  },
  subtitle: {
    fontSize: 16,
    color: colors.textSecondary,
    textAlign: 'center',
    lineHeight: 24,
  },
  form: {
    flex: 1,
  },
  inputContainer: {
    marginBottom: spacing.lg,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.text,
    marginBottom: spacing.sm,
  },
  input: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 12,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.md,
    fontSize: 16,
    backgroundColor: colors.surface,
  },
  inputError: {
    borderColor: colors.error,
  },
  passwordContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 12,
    backgroundColor: colors.surface,
  },
  passwordInput: {
    flex: 1,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.md,
    fontSize: 16,
  },
  eyeButton: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
  },
  eyeText: {
    color: colors.primary,
    fontSize: 14,
  },
  errorText: {
    color: colors.error,
    fontSize: 12,
    marginTop: spacing.xs,
  },
  passwordHint: {
    color: colors.textSecondary,
    fontSize: 12,
    marginTop: spacing.xs,
  },
  primaryButton: {
    backgroundColor: colors.primary,
    paddingVertical: spacing.md,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: spacing.lg,
  },
  primaryButtonDisabled: {
    opacity: 0.6,
  },
  primaryButtonText: {
    color: colors.surface,
    fontSize: 18,
    fontWeight: '600',
  },
  resendContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: spacing.lg,
  },
  resendText: {
    fontSize: 14,
    color: colors.textSecondary,
  },
  resendLink: {
    fontSize: 14,
    color: colors.primary,
    fontWeight: '600',
    marginLeft: spacing.sm,
  },
  resendLinkDisabled: {
    color: colors.textSecondary,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: spacing.xl,
    paddingBottom: spacing.lg,
  },
  footerText: {
    fontSize: 16,
    color: colors.textSecondary,
  },
  loginLink: {
    fontSize: 16,
    color: colors.primary,
    fontWeight: '600',
    marginLeft: spacing.sm,
  },
});
