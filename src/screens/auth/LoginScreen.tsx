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

type LoginScreenNavigationProp = NativeStackNavigationProp<AuthStackParamList, 'Login'>;

const LoginScreen: React.FC = () => {
  const navigation = useNavigation<LoginScreenNavigationProp>();
  
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<{[key: string]: string}>({});

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // 清除对应字段的错误
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const validateForm = () => {
    const newErrors: {[key: string]: string} = {};

    if (!formData.email.trim()) {
      newErrors.email = '请输入邮箱或手机号';
    } else if (formData.email.includes('@')) {
      // 邮箱验证
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(formData.email)) {
        newErrors.email = '请输入有效的邮箱地址';
      }
    } else {
      // 手机号验证
      const phoneRegex = /^1[3-9]\d{9}$/;
      if (!phoneRegex.test(formData.email)) {
        newErrors.email = '请输入有效的手机号';
      }
    }

    if (!formData.password.trim()) {
      newErrors.password = '请输入密码';
    } else if (formData.password.length < 6) {
      newErrors.password = '密码至少需要6位字符';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleLogin = async () => {
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    try {
      // TODO: 实现实际的登录逻辑
      // 这里应该调用认证服务
      await new Promise(resolve => setTimeout(resolve, 2000)); // 模拟网络请求
      
      Alert.alert('登录成功', '欢迎回到索克生活！', [
        { text: '确定', onPress: () => {
          // TODO: 导航到主应用
          console.log('Navigate to main app');
        }}
      ]);
    } catch (error) {
      Alert.alert('登录失败', '用户名或密码错误，请重试');
    } finally {
      setLoading(false);
    }
  };

  const handleForgotPassword = () => {
    navigation.navigate('ForgotPassword');
  };

  const handleRegister = () => {
    navigation.navigate('Register');
  };

  const handleBack = () => {
    navigation.goBack();
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
            
            <Text style={styles.title}>欢迎回来</Text>
            <Text style={styles.subtitle}>登录您的索克生活账户</Text>
          </View>

          {/* 表单区域 */}
          <View style={styles.formSection}>
                         <View style={styles.inputContainer}>
               <Input
                 label="邮箱/手机号"
                 value={formData.email}
                 onChangeText={(value) => handleInputChange('email', value)}
                 placeholder="请输入邮箱或手机号"
                 type="email"
                 error={!!errors.email}
                 errorMessage={errors.email}
               />
             </View>

             <View style={styles.inputContainer}>
               <Input
                 label="密码"
                 value={formData.password}
                 onChangeText={(value) => handleInputChange('password', value)}
                 placeholder="请输入密码"
                 type="password"
                 error={!!errors.password}
                 errorMessage={errors.password}
               />
             </View>

            <TouchableOpacity style={styles.forgotPassword} onPress={handleForgotPassword}>
              <Text style={styles.forgotPasswordText}>忘记密码？</Text>
            </TouchableOpacity>

            <Button
              title="登录"
              variant="primary"
              size="large"
              fullWidth
              loading={loading}
              onPress={handleLogin}
              style={styles.loginButton}
            />
          </View>

          {/* 其他登录方式 */}
          <View style={styles.alternativeSection}>
            <View style={styles.dividerContainer}>
              <View style={styles.divider} />
              <Text style={styles.dividerText}>或</Text>
              <View style={styles.divider} />
            </View>

            <View style={styles.socialButtons}>
              <TouchableOpacity style={styles.socialButton}>
                <Text style={styles.socialButtonText}>📱</Text>
                <Text style={styles.socialButtonLabel}>微信登录</Text>
              </TouchableOpacity>

              <TouchableOpacity style={styles.socialButton}>
                <Text style={styles.socialButtonText}>📞</Text>
                <Text style={styles.socialButtonLabel}>短信登录</Text>
              </TouchableOpacity>
            </View>
          </View>

          {/* 注册提示 */}
          <View style={styles.registerSection}>
            <Text style={styles.registerText}>
              还没有账户？
              <Text style={styles.registerLink} onPress={handleRegister}>
                立即注册
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
  forgotPassword: {
    alignSelf: 'flex-end',
    marginBottom: spacing.xl,
  },
  forgotPasswordText: {
    fontSize: typography.fontSize.sm,
    color: colors.primary,
    fontFamily: typography.fontFamily.medium,
  },
  loginButton: {
    marginBottom: spacing.lg,
  },

  // 其他登录方式
  alternativeSection: {
    paddingVertical: spacing.lg,
  },
  dividerContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.lg,
  },
  divider: {
    flex: 1,
    height: 1,
    backgroundColor: colors.border,
  },
  dividerText: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    marginHorizontal: spacing.md,
    fontFamily: typography.fontFamily.regular,
  },
  socialButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  socialButton: {
    flex: 1,
    backgroundColor: colors.surface,
    borderRadius: borderRadius.md,
    padding: spacing.lg,
    alignItems: 'center',
    marginHorizontal: spacing.xs,
    ...shadows.sm,
  },
  socialButtonText: {
    fontSize: typography.fontSize.xl,
    marginBottom: spacing.xs,
  },
  socialButtonLabel: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    fontFamily: typography.fontFamily.regular,
  },

  // 注册提示
  registerSection: {
    alignItems: 'center',
    paddingVertical: spacing.xl,
  },
  registerText: {
    fontSize: typography.fontSize.base,
    color: colors.textSecondary,
    fontFamily: typography.fontFamily.regular,
  },
  registerLink: {
    color: colors.primary,
    fontWeight: '600',
    fontFamily: typography.fontFamily.medium,
  },
});

export default LoginScreen; 