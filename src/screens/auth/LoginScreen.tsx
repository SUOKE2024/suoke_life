import React, { useState, useEffect } from 'react';
import { View, StyleSheet, Image, TouchableOpacity, KeyboardAvoidingView, Platform, ScrollView } from 'react-native';
import { TextInput, Button, Text, Surface, Snackbar, useTheme } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useSelector } from 'react-redux';
import { useAppDispatch } from '../../hooks/redux';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { useTranslation } from 'react-i18next';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { login, clearError, setUser } from '../../store/slices/userSlice';
import { AuthStackParamList } from '../../navigation/AppNavigator';
import { RootState } from '../../store';

// 开发环境标识
const isDevelopment = __DEV__;

const LoginScreen: React.FC = () => {
  const theme = useTheme();
  const dispatch = useAppDispatch();
  const navigation = useNavigation<NativeStackNavigationProp<AuthStackParamList>>();
  const { t } = useTranslation();
  
  const { isLoading, error } = useSelector((state: RootState) => state.user);
  
  const [mobile, setMobile] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [snackbarVisible, setSnackbarVisible] = useState(false);
  
  // 处理表单提交
  const handleSubmit = () => {
    if (!mobile || !password) {
      return;
    }
    
    dispatch(login({ mobile, password }));
  };
  
  // 处理开发环境直接登录
  const handleDevLogin = () => {
    if (!isDevelopment) return;
    
    // 创建一个测试用户
    const testUser = {
      id: 'test-user-id',
      mobile: '13800138000',
      username: '测试用户',
      avatar: '',
      createTime: Date.now(),
      lastLoginTime: Date.now()
    };
    
    // 直接设置用户（绕过API调用）
    dispatch(setUser(testUser));
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
          <View style={styles.logoContainer}>
            <View style={[styles.logo, styles.logoPlaceholder]}>
              <Icon name="leaf" size={80} color={theme.colors.primary} />
            </View>
            <Text style={styles.appName}>索克生活</Text>
            <Text style={styles.appSlogan}>智慧中医，健康生活</Text>
          </View>
          
          <Surface style={styles.formContainer}>
            <Text style={styles.title}>{t('auth.login')}</Text>
            
            <TextInput
              label={t('auth.mobile')}
              value={mobile}
              onChangeText={setMobile}
              mode="outlined"
              style={styles.input}
              keyboardType="phone-pad"
              left={<TextInput.Icon icon="cellphone" />}
              autoCapitalize="none"
            />
            
            <TextInput
              label={t('auth.password')}
              value={password}
              onChangeText={setPassword}
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
            />
            
            <TouchableOpacity 
              style={styles.forgotPasswordContainer}
              onPress={() => navigation.navigate('ForgotPassword')}
            >
              <Text style={[styles.forgotPasswordText, { color: theme.colors.primary }]}>
                {t('auth.forgotPassword')}
              </Text>
            </TouchableOpacity>
            
            <Button 
              mode="contained" 
              onPress={handleSubmit} 
              style={styles.loginButton}
              loading={isLoading}
              disabled={isLoading || !mobile || !password}
            >
              {t('auth.login')}
            </Button>
            
            {isDevelopment && (
              <Button 
                mode="outlined" 
                onPress={handleDevLogin}
                style={[styles.loginButton, { marginTop: 8 }]}
              >
                开发环境登录
              </Button>
            )}
            
            <TouchableOpacity 
              style={styles.registerContainer}
              onPress={() => navigation.navigate('Register')}
            >
              <Text style={styles.registerText}>
                没有账号？ <Text style={{ color: theme.colors.primary }}>立即注册</Text>
              </Text>
            </TouchableOpacity>
          </Surface>
          
          <View style={styles.socialLoginContainer}>
            <Text style={styles.socialLoginText}>其他登录方式</Text>
            <View style={styles.socialIcons}>
              <TouchableOpacity style={styles.socialIcon}>
                <Icon name="wechat" size={28} color="#09B83E" />
              </TouchableOpacity>
              <TouchableOpacity style={styles.socialIcon}>
                <Icon name="cellphone" size={28} color={theme.colors.primary} />
              </TouchableOpacity>
            </View>
          </View>
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
    justifyContent: 'center',
  },
  logoContainer: {
    alignItems: 'center',
    marginBottom: 32,
  },
  logo: {
    width: 100,
    height: 100,
    marginBottom: 16,
  },
  logoPlaceholder: {
    backgroundColor: '#f0f0f0',
    borderRadius: 50,
    justifyContent: 'center',
    alignItems: 'center',
  },
  appName: {
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  appSlogan: {
    fontSize: 16,
    opacity: 0.7,
  },
  formContainer: {
    padding: 24,
    borderRadius: 12,
    elevation: 2,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 24,
    textAlign: 'center',
  },
  input: {
    marginBottom: 16,
  },
  forgotPasswordContainer: {
    alignSelf: 'flex-end',
    marginBottom: 24,
  },
  forgotPasswordText: {
    fontSize: 14,
  },
  loginButton: {
    paddingVertical: 8,
    borderRadius: 4,
  },
  registerContainer: {
    marginTop: 24,
    alignItems: 'center',
  },
  registerText: {
    fontSize: 14,
  },
  socialLoginContainer: {
    marginTop: 40,
    alignItems: 'center',
  },
  socialLoginText: {
    fontSize: 14,
    opacity: 0.7,
    marginBottom: 16,
  },
  socialIcons: {
    flexDirection: 'row',
    justifyContent: 'center',
  },
  socialIcon: {
    width: 50,
    height: 50,
    borderRadius: 25,
    borderWidth: 1,
    borderColor: '#E0E0E0',
    justifyContent: 'center',
    alignItems: 'center',
    marginHorizontal: 10,
  },
});

export default LoginScreen; 