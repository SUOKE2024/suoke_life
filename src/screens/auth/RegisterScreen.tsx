import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView, KeyboardAvoidingView, Platform, TouchableOpacity } from 'react-native';
import { TextInput, Button, Text, Surface, useTheme, Snackbar, HelperText } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useSelector } from 'react-redux';
import { useAppDispatch } from '../../hooks/redux';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { useTranslation } from 'react-i18next';
import { register, clearError } from '../../store/slices/userSlice';
import { AuthStackParamList } from '../../navigation/AppNavigator';
import { RootState } from '../../store';

// 验证手机号的正则表达式
const MOBILE_REGEX = /^1[3-9]\d{9}$/;

const RegisterScreen = () => {
  const theme = useTheme();
  const dispatch = useAppDispatch();
  const navigation = useNavigation<NativeStackNavigationProp<AuthStackParamList>>();
  const { t } = useTranslation();
  
  const { isLoading, error } = useSelector((state: RootState) => state.user);
  
  // 表单状态
  const [username, setUsername] = useState('');
  const [mobile, setMobile] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [snackbarVisible, setSnackbarVisible] = useState(false);
  
  // 错误状态
  const [usernameError, setUsernameError] = useState('');
  const [mobileError, setMobileError] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [confirmPasswordError, setConfirmPasswordError] = useState('');
  
  // 表单验证
  const validateUsername = () => {
    if (!username.trim()) {
      setUsernameError('请输入用户名');
      return false;
    }
    if (username.length < 2 || username.length > 20) {
      setUsernameError('用户名长度应为2-20个字符');
      return false;
    }
    setUsernameError('');
    return true;
  };
  
  const validateMobile = () => {
    if (!mobile) {
      setMobileError('请输入手机号');
      return false;
    }
    if (!MOBILE_REGEX.test(mobile)) {
      setMobileError('请输入有效的手机号');
      return false;
    }
    setMobileError('');
    return true;
  };
  
  const validatePassword = () => {
    if (!password) {
      setPasswordError('请输入密码');
      return false;
    }
    if (password.length < 6) {
      setPasswordError('密码长度不能少于6位');
      return false;
    }
    setPasswordError('');
    return true;
  };
  
  const validateConfirmPassword = () => {
    if (!confirmPassword) {
      setConfirmPasswordError('请确认密码');
      return false;
    }
    if (confirmPassword !== password) {
      setConfirmPasswordError('两次输入的密码不一致');
      return false;
    }
    setConfirmPasswordError('');
    return true;
  };
  
  // 提交表单
  const handleSubmit = () => {
    const isUsernameValid = validateUsername();
    const isMobileValid = validateMobile();
    const isPasswordValid = validatePassword();
    const isConfirmPasswordValid = validateConfirmPassword();
    
    if (isUsernameValid && isMobileValid && isPasswordValid && isConfirmPasswordValid) {
      dispatch(register({ 
        username, 
        mobile, 
        password,
        confirmPassword: confirmPassword,
        verificationCode: '000000' // 在实际应用中，应该使用真实的验证码
      }));
    }
  };
  
  // 处理错误显示
  useEffect(() => {
    if (error) {
      setSnackbarVisible(true);
    }
  }, [error]);
  
  // 处理关闭错误提示
  const onDismissSnackbar = () => {
    setSnackbarVisible(false);
    dispatch(clearError());
  };
  
  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView 
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardAvoidingView}
      >
        <ScrollView contentContainerStyle={styles.scrollContent}>
          <Text style={styles.headerTitle}>{t('auth.register')}</Text>
          <Text style={styles.headerSubtitle}>创建您的索克生活账号</Text>
          
          <Surface style={styles.formContainer}>
            <TextInput
              label="用户名"
              value={username}
              onChangeText={setUsername}
              onBlur={validateUsername}
              mode="outlined"
              style={styles.input}
              left={<TextInput.Icon icon="account" />}
              error={!!usernameError}
            />
            {usernameError ? <HelperText type="error">{usernameError}</HelperText> : null}
            
            <TextInput
              label="手机号"
              value={mobile}
              onChangeText={setMobile}
              onBlur={validateMobile}
              mode="outlined"
              style={styles.input}
              keyboardType="phone-pad"
              left={<TextInput.Icon icon="cellphone" />}
              error={!!mobileError}
            />
            {mobileError ? <HelperText type="error">{mobileError}</HelperText> : null}
            
            <TextInput
              label="密码"
              value={password}
              onChangeText={setPassword}
              onBlur={validatePassword}
              mode="outlined"
              style={styles.input}
              secureTextEntry={!showPassword}
              left={<TextInput.Icon icon="lock" />}
              right={
                <TextInput.Icon 
                  icon={showPassword ? "eye-off" : "eye"} 
                  onPress={() => setShowPassword(!showPassword)} 
                />
              }
              error={!!passwordError}
            />
            {passwordError ? <HelperText type="error">{passwordError}</HelperText> : null}
            
            <TextInput
              label="确认密码"
              value={confirmPassword}
              onChangeText={setConfirmPassword}
              onBlur={validateConfirmPassword}
              mode="outlined"
              style={styles.input}
              secureTextEntry={!showConfirmPassword}
              left={<TextInput.Icon icon="lock-check" />}
              right={
                <TextInput.Icon 
                  icon={showConfirmPassword ? "eye-off" : "eye"} 
                  onPress={() => setShowConfirmPassword(!showConfirmPassword)} 
                />
              }
              error={!!confirmPasswordError}
            />
            {confirmPasswordError ? <HelperText type="error">{confirmPasswordError}</HelperText> : null}
            
            <Text style={styles.privacyText}>
              注册即表示您同意索克生活的
              <Text style={{ color: theme.colors.primary }}> 服务条款 </Text>
              和
              <Text style={{ color: theme.colors.primary }}> 隐私政策</Text>
            </Text>
            
            <Button 
              mode="contained" 
              onPress={handleSubmit} 
              style={styles.registerButton}
              loading={isLoading}
              disabled={isLoading}
            >
              {t('auth.register')}
            </Button>
            
            <TouchableOpacity 
              style={styles.loginContainer}
              onPress={() => navigation.navigate('Login')}
            >
              <Text style={styles.loginText}>
                已有账号？ <Text style={{ color: theme.colors.primary }}>返回登录</Text>
              </Text>
            </TouchableOpacity>
          </Surface>
        </ScrollView>
      </KeyboardAvoidingView>
      
      <Snackbar
        visible={snackbarVisible}
        onDismiss={onDismissSnackbar}
        duration={3000}
        action={{
          label: '关闭',
          onPress: onDismissSnackbar,
        }}
      >
        {error}
      </Snackbar>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  keyboardAvoidingView: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    padding: 16,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    marginTop: 40,
    marginBottom: 8,
  },
  headerSubtitle: {
    fontSize: 16,
    opacity: 0.7,
    marginBottom: 32,
  },
  formContainer: {
    padding: 24,
    borderRadius: 12,
    elevation: 2,
  },
  input: {
    marginBottom: 8,
  },
  privacyText: {
    fontSize: 14,
    opacity: 0.7,
    marginVertical: 16,
    textAlign: 'center',
  },
  registerButton: {
    marginTop: 8,
    paddingVertical: 8,
    borderRadius: 4,
  },
  loginContainer: {
    marginTop: 24,
    alignItems: 'center',
  },
  loginText: {
    fontSize: 14,
  },
});

export default RegisterScreen;