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
    TouchableOpacity,
    View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Input } from '../../components/ui';
import { Button } from '../../components/ui/Button';
import { borderRadius, colors, shadows, spacing, typography } from '../../constants/theme';

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
  const buttonScale = new Animated.Value(1);

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
      // TODO: 实现实际的注册逻辑
      // 这里应该调用用户服务
      await new Promise(resolve => setTimeout(resolve, 1500)); // 模拟网络请求
      
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
      '索克生活平台尊重并保护所有用户的个人隐私权。为了给您提供更准确、更有针对性的服务，本平台会按照本隐私权政策的规定使用和披露您的个人信息。本平台将以高度的勤勉、审慎义务对待这些信息。除本隐私权政策另有规定外，在未征得您事先许可的情况下，本平台不会将这些信息对外披露或向第三方提供。',
      [{ text: '我知道了', style: 'default' }]
    );
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
              <Input
                label="用户名"
                value={formData.username}
                onChangeText={(value) => handleInputChange('username', value)}
                placeholder="请输入用户名"
                error={!!errors.username}
                errorMessage={errors.username}
                testID="username-input"
              />
            </View>

            <View style={styles.inputContainer}>
              <Input
                label="邮箱地址"
                value={formData.email}
                onChangeText={(value) => handleInputChange('email', value)}
                placeholder="请输入邮箱地址"
                keyboardType="email-address"
                autoCapitalize="none"
                error={!!errors.email}
                errorMessage={errors.email}
                testID="email-input"
              />
            </View>

            <View style={styles.inputContainer}>
              <Input
                label="手机号"
                value={formData.phone}
                onChangeText={(value) => handleInputChange('phone', value)}
                placeholder="请输入手机号"
                keyboardType="phone-pad"
                error={!!errors.phone}
                errorMessage={errors.phone}
                testID="phone-input"
              />
            </View>

            <View style={styles.inputContainer}>
              <Input
                label="密码"
                value={formData.password}
                onChangeText={(value) => handleInputChange('password', value)}
                placeholder="请输入密码"
                secureTextEntry
                error={!!errors.password}
                errorMessage={errors.password}
                testID="password-input"
              />
            </View>

            <View style={styles.inputContainer}>
              <Input
                label="确认密码"
                value={formData.confirmPassword}
                onChangeText={(value) => handleInputChange('confirmPassword', value)}
                placeholder="请再次输入密码"
                secureTextEntry
                error={!!errors.confirmPassword}
                errorMessage={errors.confirmPassword}
                testID="confirm-password-input"
              />
            </View>

            {/* 服务条款同意 */}
            <View style={styles.termsContainer}>
              <TouchableOpacity
                style={styles.checkbox}
                onPress={toggleTermsAgreement}
                testID="terms-checkbox"
              >
                <View style={[styles.checkboxInner, agreedToTerms && styles.checkboxChecked]}>
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
            <Animated.View style={[styles.buttonContainer, { transform: [{ scale: buttonScale }] }]}>
              <Button
                title={loading ? '注册中...' : '注册'}
                onPress={handleRegister}
                disabled={loading}
                loading={loading}
              />
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
    paddingBottom: spacing.xl,
  },
  header: {
    alignItems: 'center',
    paddingTop: spacing.lg,
    paddingHorizontal: spacing.lg,
    paddingBottom: spacing.xl,
  },
  backButton: {
    position: 'absolute',
    left: spacing.lg,
    top: spacing.lg,
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.surface,
    justifyContent: 'center',
    alignItems: 'center',
    ...shadows.sm,
  },
  backButtonText: {
    fontSize: 20,
    color: colors.primary,
    fontWeight: 'bold',
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
    fontSize: 24,
    fontWeight: 'bold',
    color: colors.white,
  },
  title: {
    fontSize: typography.fontSize['2xl'],
    fontWeight: '700' as const,
    color: colors.text,
    marginBottom: spacing.sm,
  },
  subtitle: {
    fontSize: typography.fontSize.base,
    color: colors.textSecondary,
    textAlign: 'center',
    lineHeight: 22,
  },
  formSection: {
    paddingHorizontal: spacing.lg,
  },
  inputContainer: {
    marginBottom: spacing.lg,
  },
  termsContainer: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: spacing.xl,
    paddingHorizontal: spacing.sm,
  },
  checkbox: {
    marginRight: spacing.sm,
    marginTop: 2,
  },
  checkboxInner: {
    width: 20,
    height: 20,
    borderWidth: 2,
    borderColor: colors.border,
    borderRadius: 4,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.surface,
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
  termsTextContainer: {
    flex: 1,
    flexDirection: 'row',
    flexWrap: 'wrap',
    alignItems: 'center',
  },
  termsText: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    lineHeight: 20,
  },
  termsLink: {
    fontSize: typography.fontSize.sm,
    color: colors.primary,
    fontWeight: '500' as const,
    textDecorationLine: 'underline',
  },
  buttonContainer: {
    marginBottom: spacing.lg,
  },
  registerButton: {
    height: 50,
    borderRadius: borderRadius.lg,
  },
  loginContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    paddingTop: spacing.lg,
  },
  loginText: {
    fontSize: typography.fontSize.base,
    color: colors.textSecondary,
    marginRight: spacing.xs,
  },
  loginLink: {
    fontSize: typography.fontSize.base,
    color: colors.primary,
    fontWeight: '500' as const,
  },
});

export default RegisterScreen;