import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui';
import { colors, typography, spacing, borderRadius, shadows } from '../../constants/theme';

type AuthStackParamList = {
  Welcome: undefined;
  Login: undefined;
  Register: undefined;
  ForgotPassword: undefined;
};

type RegisterScreenNavigationProp = NativeStackNavigationProp<AuthStackParamList, 'Register'>;

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
  const [errors, setErrors] = useState<{[key: string]: string}>({});
  const [agreedToTerms, setAgreedToTerms] = useState(false);

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // 清除对应字段的错误
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const validateForm = () => {
    const newErrors: {[key: string]: string} = {};

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

    setLoading(true);
    try {
      // TODO: 实现实际的注册逻辑
      // 这里应该调用用户服务
      await new Promise(resolve => setTimeout(resolve, 2000)); // 模拟网络请求
      
      Alert.alert('注册成功', '欢迎加入索克生活！请查收邮箱验证邮件。', [
        { text: '确定', onPress: () => {
          navigation.navigate('Login');
        }}
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

  return (
    <SafeAreaView style={styles.container}>
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
            <View style={styles.inputContainer}>
              <Text style={styles.inputLabel}>用户名</Text>
              <View style={styles.inputWrapper}>
                <Text style={styles.inputText}>{formData.username || '请输入用户名'}</Text>
              </View>
              {errors.username && <Text style={styles.errorText}>{errors.username}</Text>}
            </View>

            <View style={styles.inputContainer}>
              <Text style={styles.inputLabel}>邮箱地址</Text>
              <View style={styles.inputWrapper}>
                <Text style={styles.inputText}>{formData.email || '请输入邮箱地址'}</Text>
              </View>
              {errors.email && <Text style={styles.errorText}>{errors.email}</Text>}
            </View>

            <View style={styles.inputContainer}>
              <Text style={styles.inputLabel}>手机号</Text>
              <View style={styles.inputWrapper}>
                <Text style={styles.inputText}>{formData.phone || '请输入手机号'}</Text>
              </View>
              {errors.phone && <Text style={styles.errorText}>{errors.phone}</Text>}
            </View>

            <View style={styles.inputContainer}>
              <Text style={styles.inputLabel}>密码</Text>
              <View style={styles.inputWrapper}>
                <Text style={styles.inputText}>{formData.password ? '••••••••' : '请输入密码'}</Text>
              </View>
              {errors.password && <Text style={styles.errorText}>{errors.password}</Text>}
            </View>

            <View style={styles.inputContainer}>
              <Text style={styles.inputLabel}>确认密码</Text>
              <View style={styles.inputWrapper}>
                <Text style={styles.inputText}>{formData.confirmPassword ? '••••••••' : '请再次输入密码'}</Text>
              </View>
              {errors.confirmPassword && <Text style={styles.errorText}>{errors.confirmPassword}</Text>}
            </View>

            {/* 服务条款 */}
            <View style={styles.termsContainer}>
              <TouchableOpacity style={styles.checkbox} onPress={toggleTermsAgreement}>
                <Text style={styles.checkboxText}>{agreedToTerms ? '✓' : ''}</Text>
              </TouchableOpacity>
              <Text style={styles.termsText}>
                我已阅读并同意
                <Text style={styles.termsLink}>《服务条款》</Text>
                和
                <Text style={styles.termsLink}>《隐私政策》</Text>
              </Text>
            </View>

            <Button
              title="注册"
              variant="primary"
              size="large"
              fullWidth
              loading={loading}
              onPress={handleRegister}
              style={styles.registerButton}
            />
          </View>

          {/* 健康承诺 */}
          <View style={styles.promiseSection}>
            <Text style={styles.promiseTitle}>我们的健康承诺</Text>
            <View style={styles.promiseList}>
              <View style={styles.promiseItem}>
                <Text style={styles.promiseIcon}>🔒</Text>
                <Text style={styles.promiseText}>数据安全保护</Text>
              </View>
              <View style={styles.promiseItem}>
                <Text style={styles.promiseIcon}>🧠</Text>
                <Text style={styles.promiseText}>AI智能分析</Text>
              </View>
              <View style={styles.promiseItem}>
                <Text style={styles.promiseIcon}>🌿</Text>
                <Text style={styles.promiseText}>中医智慧指导</Text>
              </View>
            </View>
          </View>

          {/* 登录提示 */}
          <View style={styles.loginSection}>
            <Text style={styles.loginText}>
              已有账户？
              <Text style={styles.loginLink} onPress={handleLogin}>
                立即登录
              </Text>
            </Text>
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
    flexGrow: 1,
    paddingHorizontal: spacing.lg,
  },

  // 头部区域
  header: {
    alignItems: 'center',
    paddingTop: spacing.lg,
    paddingBottom: spacing.xl,
  },
  backButton: {
    position: 'absolute',
    left: 0,
    top: spacing.lg,
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.gray100,
    justifyContent: 'center',
    alignItems: 'center',
  },
  backButtonText: {
    fontSize: typography.fontSize.xl,
    color: colors.textPrimary,
  },
  logoContainer: {
    marginBottom: spacing.lg,
  },
  logoPlaceholder: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
    ...shadows.md,
  },
  logoText: {
    fontSize: typography.fontSize.xl,
    fontWeight: '700',
    color: colors.white,
    fontFamily: typography.fontFamily.bold,
  },
  title: {
    fontSize: typography.fontSize['3xl'],
    fontWeight: '700',
    color: colors.textPrimary,
    marginBottom: spacing.sm,
    fontFamily: typography.fontFamily.bold,
  },
  subtitle: {
    fontSize: typography.fontSize.base,
    color: colors.textSecondary,
    textAlign: 'center',
    fontFamily: typography.fontFamily.regular,
  },

  // 表单区域
  formSection: {
    paddingVertical: spacing.lg,
  },
  inputContainer: {
    marginBottom: spacing.lg,
  },
  inputLabel: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
    fontFamily: typography.fontFamily.medium,
  },
  inputWrapper: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: borderRadius.md,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    backgroundColor: colors.surface,
    minHeight: 48,
    justifyContent: 'center',
  },
  inputText: {
    fontSize: typography.fontSize.base,
    color: colors.textPrimary,
    fontFamily: typography.fontFamily.regular,
  },
  errorText: {
    fontSize: typography.fontSize.sm,
    color: colors.error,
    marginTop: spacing.xs,
    fontFamily: typography.fontFamily.regular,
  },

  // 服务条款
  termsContainer: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: spacing.xl,
  },
  checkbox: {
    width: 20,
    height: 20,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 4,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.sm,
    backgroundColor: colors.surface,
  },
  checkboxText: {
    fontSize: typography.fontSize.sm,
    color: colors.primary,
    fontWeight: '600',
  },
  termsText: {
    flex: 1,
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    lineHeight: typography.lineHeight.normal * typography.fontSize.sm,
    fontFamily: typography.fontFamily.regular,
  },
  termsLink: {
    color: colors.primary,
    fontWeight: '600',
  },
  registerButton: {
    marginBottom: spacing.lg,
  },

  // 健康承诺
  promiseSection: {
    paddingVertical: spacing.lg,
    backgroundColor: colors.surfaceSecondary,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    marginVertical: spacing.lg,
  },
  promiseTitle: {
    fontSize: typography.fontSize.lg,
    fontWeight: '600',
    color: colors.textPrimary,
    textAlign: 'center',
    marginBottom: spacing.md,
    fontFamily: typography.fontFamily.medium,
  },
  promiseList: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  promiseItem: {
    alignItems: 'center',
    flex: 1,
  },
  promiseIcon: {
    fontSize: typography.fontSize.xl,
    marginBottom: spacing.xs,
  },
  promiseText: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    textAlign: 'center',
    fontFamily: typography.fontFamily.regular,
  },

  // 登录提示
  loginSection: {
    alignItems: 'center',
    paddingVertical: spacing.xl,
  },
  loginText: {
    fontSize: typography.fontSize.base,
    color: colors.textSecondary,
    fontFamily: typography.fontFamily.regular,
  },
  loginLink: {
    color: colors.primary,
    fontWeight: '600',
    fontFamily: typography.fontFamily.medium,
  },
});

export default RegisterScreen; 