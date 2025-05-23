import React, { useState, useEffect } from 'react';
import { View, StyleSheet, KeyboardAvoidingView, Platform, TouchableOpacity } from 'react-native';
import { TextInput, Button, Text, Surface, useTheme, Snackbar, HelperText } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useSelector } from 'react-redux';
import { useAppDispatch } from '../../hooks/redux';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { useTranslation } from 'react-i18next';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { requestPasswordReset, clearError } from '../../store/slices/userSlice';
import { AuthStackParamList } from '../../navigation/AppNavigator';
import { RootState } from '../../store';

// 验证手机号的正则表达式
const MOBILE_REGEX = /^1[3-9]\d{9}$/;

const ForgotPasswordScreen = () => {
  const theme = useTheme();
  const dispatch = useAppDispatch();
  const navigation = useNavigation<NativeStackNavigationProp<AuthStackParamList>>();
  const { t } = useTranslation();
  
  const { isLoading, error } = useSelector((state: RootState) => state.user);
  
  const [mobile, setMobile] = useState('');
  const [verificationCode, setVerificationCode] = useState('');
  const [mobileError, setMobileError] = useState('');
  const [codeError, setCodeError] = useState('');
  const [codeSent, setCodeSent] = useState(false);
  const [countdown, setCountdown] = useState(0);
  const [snackbarVisible, setSnackbarVisible] = useState(false);
  
  // 验证手机号
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
  
  // 验证验证码
  const validateCode = () => {
    if (!verificationCode) {
      setCodeError('请输入验证码');
      return false;
    }
    if (verificationCode.length !== 6) {
      setCodeError('验证码应为6位数字');
      return false;
    }
    setCodeError('');
    return true;
  };
  
  // 发送验证码
  const handleSendCode = () => {
    if (validateMobile()) {
      // 这里应该有一个API调用来发送验证码
      console.log('Send verification code to', mobile);
      
      // 模拟发送成功
      setCodeSent(true);
      setCountdown(60);
      
      // 倒计时逻辑
      const timer = setInterval(() => {
        setCountdown((prevCount) => {
          if (prevCount <= 1) {
            clearInterval(timer);
            return 0;
          }
          return prevCount - 1;
        });
      }, 1000);
    }
  };
  
  // 提交重置密码请求
  const handleSubmit = () => {
    if (validateMobile() && validateCode()) {
      dispatch(requestPasswordReset({ mobile, verificationCode }));
    }
  };
  
  // 处理返回登录
  const handleBackToLogin = () => {
    navigation.navigate('Login');
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
        <View style={styles.contentContainer}>
          <View style={styles.header}>
            <TouchableOpacity 
              style={styles.backButton}
              onPress={handleBackToLogin}
            >
              <Icon name="arrow-left" size={24} color={theme.colors.primary} />
            </TouchableOpacity>
            <Text style={styles.headerTitle}>{t('auth.forgotPassword')}</Text>
          </View>
          
          <Surface style={styles.formContainer}>
            <Text style={styles.instructionText}>
              请输入您的注册手机号，我们将发送验证码用于重置密码。
            </Text>
            
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
            
            <View style={styles.verificationContainer}>
              <TextInput
                label="验证码"
                value={verificationCode}
                onChangeText={setVerificationCode}
                onBlur={validateCode}
                mode="outlined"
                style={styles.verificationInput}
                keyboardType="number-pad"
                maxLength={6}
                left={<TextInput.Icon icon="numeric" />}
                error={!!codeError}
              />
              <Button 
                mode="contained" 
                onPress={handleSendCode}
                style={styles.sendCodeButton}
                disabled={countdown > 0 || !mobile || !!mobileError}
              >
                {countdown > 0 ? `${countdown}秒` : '获取验证码'}
              </Button>
            </View>
            {codeError ? <HelperText type="error">{codeError}</HelperText> : null}
            
            <Button 
              mode="contained" 
              onPress={handleSubmit} 
              style={styles.resetButton}
              loading={isLoading}
              disabled={isLoading || !mobile || !verificationCode || !!mobileError || !!codeError}
            >
              下一步
            </Button>
            
            <TouchableOpacity 
              style={styles.loginContainer}
              onPress={handleBackToLogin}
            >
              <Text style={styles.loginText}>
                记起密码了？ <Text style={{ color: theme.colors.primary }}>返回登录</Text>
              </Text>
            </TouchableOpacity>
          </Surface>
        </View>
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
  contentContainer: {
    flex: 1,
    padding: 16,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 20,
  },
  backButton: {
    marginRight: 16,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  formContainer: {
    padding: 24,
    borderRadius: 12,
    elevation: 2,
  },
  instructionText: {
    fontSize: 16,
    marginBottom: 24,
    opacity: 0.7,
  },
  input: {
    marginBottom: 20,
  },
  verificationContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  verificationInput: {
    flex: 1,
    marginRight: 12,
  },
  sendCodeButton: {
    height: 50,
    justifyContent: 'center',
  },
  resetButton: {
    marginTop: 24,
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

export default ForgotPasswordScreen; 