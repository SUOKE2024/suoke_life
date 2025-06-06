import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  ScrollView
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { unifiedApiService } from '../../services/unifiedApiService';
import { isLoggedIn } from '../../utils/authUtils';

interface LoginFormData {
  email: string;
  password: string;
  rememberMe: boolean;
}

interface LoginFormErrors {
  email?: string;
  password?: string;
  general?: string;
}

const LoginScreen: React.FC = () => {
  const navigation = useNavigation();
  const [formData, setFormData] = useState<LoginFormData>({
    email: '',
    password: '',
    rememberMe: false
  });
  const [errors, setErrors] = useState<LoginFormErrors>({});
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  // 检查是否已登录
  useEffect(() => {
    checkAuthStatus();
  }, [])  // 检查是否需要添加依赖项;

  const checkAuthStatus = async () => {
    try {
      const loggedIn = await isLoggedIn();
      if (loggedIn) {
        // 验证token有效性
        const isValid = await unifiedApiService.getCurrentUser();
        if (isValid) {
          navigation.navigate('Main' as never);
        }
      }
    } catch (error) {
      console.log('检查认证状态失败:', error);
    }
  };

  // 表单验证
  const validateForm = (): boolean => {
    const newErrors: LoginFormErrors = {};

    // 邮箱验证
    if (!formData.email.trim()) {
      newErrors.email = '请输入邮箱';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = '请输入有效的邮箱地址';
    }

    // 密码验证
    if (!formData.password) {
      newErrors.password = '请输入密码';
    } else if (formData.password.length < 6) {
      newErrors.password = '密码至少6个字符';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // 处理登录
  const handleLogin = async () => {
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setErrors({});

    try {
      // 调用认证服务登录
      const loginResponse = await unifiedApiService.login({
        email: formData.email,
        password: formData.password,
        rememberMe: formData.rememberMe
      });

      // 获取用户信息
      const userInfo = await unifiedApiService.getCurrentUser();

      Alert.alert(
        '登录成功',
        `欢迎回来，${userInfo.data?.username || userInfo.data?.email || '用户'}！`,
        [
          {
            text: '确定',
            onPress: () => navigation.navigate('Main' as never)
          }
        ]
      );
    } catch (error: any) {
      console.error('登录失败:', error);
      setErrors({
        general: error.message || '登录失败，请检查邮箱和密码'
      });
    } finally {
      setLoading(false);
    }
  };

  // 处理忘记密码
  const handleForgotPassword = () => {
    navigation.navigate('ForgotPassword' as never);
  };

  // 处理注册
  const handleRegister = () => {
    navigation.navigate('Register' as never);
  };

  // 处理第三方登录
  const handleSocialLogin = async (provider: string) => {
    Alert.alert('提示', `${provider}登录功能即将上线`);
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView contentContainerStyle={styles.scrollContainer}>
        <View style={styles.header}>
          <Text style={styles.title}>索克生活</Text>
          <Text style={styles.subtitle}>智能健康管理平台</Text>
        </View>

        <View style={styles.form}>
          {/* 邮箱输入 */}
          <View style={styles.inputContainer}>
            <Text style={styles.label}>邮箱</Text>
            <TextInput
              style={[styles.input, errors.email && styles.inputError]}
              placeholder="请输入邮箱"
              value={formData.email}
              onChangeText={(text) =>
                setFormData({ ...formData, email: text })
              }
              keyboardType="email-address"
              autoCapitalize="none"
              autoCorrect={false}
              editable={!loading}
            />
            {errors.email && (
              <Text style={styles.errorText}>{errors.email}</Text>
            )}
          </View>

          {/* 密码输入 */}
          <View style={styles.inputContainer}>
            <Text style={styles.label}>密码</Text>
            <View style={styles.passwordContainer}>
              <TextInput
                style={[
                  styles.passwordInput,
                  errors.password && styles.inputError
                ]}
                placeholder="请输入密码"
                value={formData.password}
                onChangeText={(text) =>
                  setFormData({ ...formData, password: text })
                }
                secureTextEntry={!showPassword}
                autoCapitalize="none"
                autoCorrect={false}
                editable={!loading}
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
            {errors.password && (
              <Text style={styles.errorText}>{errors.password}</Text>
            )}
          </View>

          {/* 记住我 */}
          <View style={styles.rememberContainer}>
            <TouchableOpacity
              style={styles.checkbox}
              onPress={() =>
                setFormData({
                  ...formData,
                  rememberMe: !formData.rememberMe
                })
              }
            >
              <View style={[
                styles.checkboxInner,
                formData.rememberMe && styles.checkboxChecked
              ]}>
                {formData.rememberMe && (
                  <Text style={styles.checkmark}>✓</Text>
                )}
              </View>
            </TouchableOpacity>
            <Text style={styles.rememberText}>记住我</Text>
          </View>

          {/* 通用错误信息 */}
          {errors.general && (
            <Text style={styles.errorText}>{errors.general}</Text>
          )}

          {/* 登录按钮 */}
          <TouchableOpacity
            style={[styles.loginButton, loading && styles.loginButtonDisabled]}
            onPress={handleLogin}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color="#FFFFFF" />
            ) : (
              <Text style={styles.loginButtonText}>登录</Text>
            )}
          </TouchableOpacity>

          {/* 忘记密码 */}
          <TouchableOpacity
            style={styles.forgotPasswordButton}
            onPress={handleForgotPassword}
          >
            <Text style={styles.forgotPasswordText}>忘记密码？</Text>
          </TouchableOpacity>

          {/* 分割线 */}
          <View style={styles.divider}>
            <View style={styles.dividerLine} />
            <Text style={styles.dividerText}>或</Text>
            <View style={styles.dividerLine} />
          </View>

          {/* 第三方登录 */}
          <View style={styles.socialContainer}>
            <TouchableOpacity
              style={styles.socialButton}
              onPress={() => handleSocialLogin('微信')}
            >
              <Text style={styles.socialButtonText}>微信登录</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={styles.socialButton}
              onPress={() => handleSocialLogin('支付宝')}
            >
              <Text style={styles.socialButtonText}>支付宝登录</Text>
            </TouchableOpacity>
          </View>

          {/* 注册链接 */}
          <View style={styles.registerContainer}>
            <Text style={styles.registerText}>还没有账号？</Text>
            <TouchableOpacity onPress={handleRegister}>
              <Text style={styles.registerLink}>立即注册</Text>
            </TouchableOpacity>
          </View>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F7FA'
  },
  scrollContainer: {
    flexGrow: 1,
    justifyContent: 'center',
    padding: 20
  },
  header: {
    alignItems: 'center',
    marginBottom: 40
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#2C3E50',
    marginBottom: 8
  },
  subtitle: {
    fontSize: 16,
    color: '#7F8C8D',
    textAlign: 'center'
  },
  form: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 24,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2
    },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4
  },
  inputContainer: {
    marginBottom: 20
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2C3E50',
    marginBottom: 8
  },
  input: {
    borderWidth: 1,
    borderColor: '#E1E8ED',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    backgroundColor: '#FFFFFF'
  },
  inputError: {
    borderColor: '#E74C3C'
  },
  passwordContainer: {
    flexDirection: 'row',
    alignItems: 'center'
  },
  passwordInput: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#E1E8ED',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    backgroundColor: '#FFFFFF'
  },
  eyeButton: {
    position: 'absolute',
    right: 12,
    padding: 4
  },
  eyeText: {
    color: '#3498DB',
    fontSize: 14
  },
  rememberContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20
  },
  checkbox: {
    marginRight: 8
  },
  checkboxInner: {
    width: 20,
    height: 20,
    borderWidth: 2,
    borderColor: '#E1E8ED',
    borderRadius: 4,
    alignItems: 'center',
    justifyContent: 'center'
  },
  checkboxChecked: {
    backgroundColor: '#3498DB',
    borderColor: '#3498DB'
  },
  checkmark: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: 'bold'
  },
  rememberText: {
    fontSize: 14,
    color: '#7F8C8D'
  },
  errorText: {
    color: '#E74C3C',
    fontSize: 14,
    marginTop: 4
  },
  loginButton: {
    backgroundColor: '#3498DB',
    borderRadius: 8,
    padding: 16,
    alignItems: 'center',
    marginBottom: 16
  },
  loginButtonDisabled: {
    backgroundColor: '#BDC3C7'
  },
  loginButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600'
  },
  forgotPasswordButton: {
    alignItems: 'center',
    marginBottom: 24
  },
  forgotPasswordText: {
    color: '#3498DB',
    fontSize: 14
  },
  divider: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 24
  },
  dividerLine: {
    flex: 1,
    height: 1,
    backgroundColor: '#E1E8ED'
  },
  dividerText: {
    marginHorizontal: 16,
    color: '#7F8C8D',
    fontSize: 14
  },
  socialContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 24
  },
  socialButton: {
    flex: 1,
    backgroundColor: '#F8F9FA',
    borderRadius: 8,
    padding: 12,
    alignItems: 'center',
    marginHorizontal: 4
  },
  socialButtonText: {
    color: '#2C3E50',
    fontSize: 14,
    fontWeight: '500'
  },
  registerContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center'
  },
  registerText: {
    color: '#7F8C8D',
    fontSize: 14
  },
  registerLink: {
    color: '#3498DB',
    fontSize: 14,
    fontWeight: '600',
    marginLeft: 4
  }
});

export default LoginScreen; 
