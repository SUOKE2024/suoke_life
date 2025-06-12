import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import Icon from 'react-native-vector-icons/MaterialIcons';

// 导入服务
import { IntegratedApiService } from '../../services/IntegratedApiService';

// 表单验证规则
const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

// 表单错误类型
interface FormErrors {
  email?: string;
  general?: string;
}

const ForgotPasswordScreen: React.FC = () => {
  const navigation = useNavigation();
  const apiService = new IntegratedApiService();

  // 表单状态
  const [email, setEmail] = useState('');
  const [errors, setErrors] = useState<FormErrors>({});
  const [isLoading, setIsLoading] = useState(false);
  const [emailSent, setEmailSent] = useState(false);

  // 验证表单
  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    if (!email.trim()) {
      newErrors.email = '请输入邮箱地址';
    } else if (!validateEmail(email)) {
      newErrors.email = '请输入有效的邮箱地址';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // 处理发送重置邮件
  const handleSendResetEmail = async () => {
    if (!validateForm()) {
      return;
    }

    setIsLoading(true);
    setErrors({});

    try {
      // 这里应该调用实际的重置密码API
      // const response = await apiService.auth.forgotPassword({ email: email.trim() });
      
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      setEmailSent(true);
      Alert.alert(
        '邮件已发送',
        `重置密码的邮件已发送到 ${email}，请查收邮件并按照指示重置密码。`,
        [{ text: '确定' }]
      );
    } catch (error) {
      console.error('Forgot password error:', error);
      setErrors({
        general: '发送重置邮件失败，请稍后重试',
      });
    } finally {
      setIsLoading(false);
    }
  };

  // 重新发送邮件
  const handleResendEmail = () => {
    setEmailSent(false);
    handleSendResetEmail();
  };

  // 返回登录页面
  const navigateToLogin = () => {
    navigation.navigate('Login' as never);
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        keyboardShouldPersistTaps="handled"
        showsVerticalScrollIndicator={false}
      >
        {/* 头部 */}
        <View style={styles.header}>
          <TouchableOpacity
            style={styles.backButton}
            onPress={() => navigation.goBack()}
          >
            <Icon name="arrow-back" size={24} color="#333" />
          </TouchableOpacity>
          <View style={styles.logoContainer}>
            <Icon name="lock-reset" size={60} color="#2196F3" />
          </View>
          <Text style={styles.title}>忘记密码</Text>
          <Text style={styles.subtitle}>
            {emailSent 
              ? '重置邮件已发送' 
              : '输入您的邮箱地址，我们将发送重置密码的链接'
            }
          </Text>
        </View>

        {/* 表单区域 */}
        <View style={styles.formContainer}>
          {!emailSent ? (
            <>
              {/* 通用错误提示 */}
              {errors.general && (
                <View style={styles.errorContainer}>
                  <Icon name="error" size={20} color="#F44336" />
                  <Text style={styles.errorText}>{errors.general}</Text>
                </View>
              )}

              {/* 邮箱输入 */}
              <View style={styles.inputContainer}>
                <Text style={styles.inputLabel}>邮箱地址</Text>
                <View style={[styles.inputWrapper, errors.email && styles.inputError]}>
                  <Icon name="email" size={20} color="#666" style={styles.inputIcon} />
                  <TextInput
                    style={styles.textInput}
                    value={email}
                    onChangeText={(text) => {
                      setEmail(text);
                      if (errors.email) {
                        setErrors(prev => ({ ...prev, email: undefined }));
                      }
                    }}
                    placeholder="请输入注册时使用的邮箱地址"
                    placeholderTextColor="#999"
                    keyboardType="email-address"
                    autoCapitalize="none"
                    autoCorrect={false}
                    returnKeyType="done"
                    onSubmitEditing={handleSendResetEmail}
                    editable={!isLoading}
                  />
                </View>
                {errors.email && (
                  <Text style={styles.fieldErrorText}>{errors.email}</Text>
                )}
              </View>

              {/* 发送重置邮件按钮 */}
              <TouchableOpacity
                style={[styles.sendButton, isLoading && styles.sendButtonDisabled]}
                onPress={handleSendResetEmail}
                disabled={isLoading}
                activeOpacity={0.8}
              >
                {isLoading ? (
                  <ActivityIndicator size="small" color="#ffffff" />
                ) : (
                  <Text style={styles.sendButtonText}>发送重置邮件</Text>
                )}
              </TouchableOpacity>
            </>
          ) : (
            /* 邮件发送成功状态 */
            <View style={styles.successContainer}>
              <View style={styles.successIconContainer}>
                <Icon name="mark-email-read" size={80} color="#4CAF50" />
              </View>
              <Text style={styles.successTitle}>邮件已发送</Text>
              <Text style={styles.successMessage}>
                我们已向 <Text style={styles.emailText}>{email}</Text> 发送了重置密码的邮件。
              </Text>
              <Text style={styles.instructionText}>
                请查收邮件并点击邮件中的链接来重置您的密码。如果您没有收到邮件，请检查垃圾邮件文件夹。
              </Text>

              {/* 重新发送按钮 */}
              <TouchableOpacity
                style={styles.resendButton}
                onPress={handleResendEmail}
                disabled={isLoading}
              >
                <Text style={styles.resendButtonText}>重新发送邮件</Text>
              </TouchableOpacity>
            </View>
          )}

          {/* 帮助信息 */}
          <View style={styles.helpContainer}>
            <Icon name="help-outline" size={20} color="#666" />
            <View style={styles.helpTextContainer}>
              <Text style={styles.helpTitle}>需要帮助？</Text>
              <Text style={styles.helpText}>
                如果您无法收到重置邮件，请联系客服或尝试使用其他方式登录。
              </Text>
            </View>
          </View>
        </View>

        {/* 底部返回登录链接 */}
        <View style={styles.bottomContainer}>
          <Text style={styles.bottomText}>想起密码了？</Text>
          <TouchableOpacity onPress={navigateToLogin}>
            <Text style={styles.loginText}>返回登录</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#ffffff',
  },
  scrollContent: {
    flexGrow: 1,
    paddingHorizontal: 24,
    paddingTop: 40,
    paddingBottom: 40,
  },
  header: {
    alignItems: 'center',
    marginBottom: 40,
  },
  backButton: {
    position: 'absolute',
    left: 0,
    top: 20,
    padding: 8,
  },
  logoContainer: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#f0f8ff',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 20,
    marginTop: 40,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    lineHeight: 22,
    paddingHorizontal: 20,
  },
  formContainer: {
    flex: 1,
  },
  errorContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#ffebee',
    padding: 12,
    borderRadius: 8,
    marginBottom: 20,
  },
  errorText: {
    color: '#F44336',
    fontSize: 14,
    marginLeft: 8,
    flex: 1,
  },
  inputContainer: {
    marginBottom: 30,
  },
  inputLabel: {
    fontSize: 16,
    fontWeight: '500',
    color: '#333',
    marginBottom: 8,
  },
  inputWrapper: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 12,
    paddingHorizontal: 16,
    backgroundColor: '#fafafa',
  },
  inputError: {
    borderColor: '#F44336',
    backgroundColor: '#ffebee',
  },
  inputIcon: {
    marginRight: 12,
  },
  textInput: {
    flex: 1,
    height: 50,
    fontSize: 16,
    color: '#333',
  },
  fieldErrorText: {
    color: '#F44336',
    fontSize: 12,
    marginTop: 4,
    marginLeft: 4,
  },
  sendButton: {
    backgroundColor: '#2196F3',
    borderRadius: 12,
    height: 50,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 30,
    shadowColor: '#2196F3',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  sendButtonDisabled: {
    backgroundColor: '#ccc',
    shadowOpacity: 0,
    elevation: 0,
  },
  sendButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  successContainer: {
    alignItems: 'center',
    paddingVertical: 20,
  },
  successIconContainer: {
    marginBottom: 20,
  },
  successTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#4CAF50',
    marginBottom: 16,
  },
  successMessage: {
    fontSize: 16,
    color: '#333',
    textAlign: 'center',
    marginBottom: 16,
    lineHeight: 22,
  },
  emailText: {
    fontWeight: 'bold',
    color: '#2196F3',
  },
  instructionText: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    lineHeight: 20,
    marginBottom: 30,
    paddingHorizontal: 10,
  },
  resendButton: {
    backgroundColor: 'transparent',
    borderWidth: 1,
    borderColor: '#2196F3',
    borderRadius: 12,
    height: 50,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 30,
  },
  resendButtonText: {
    color: '#2196F3',
    fontSize: 16,
    fontWeight: '500',
  },
  helpContainer: {
    flexDirection: 'row',
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 12,
    marginBottom: 30,
  },
  helpTextContainer: {
    flex: 1,
    marginLeft: 12,
  },
  helpTitle: {
    fontSize: 16,
    fontWeight: '500',
    color: '#333',
    marginBottom: 4,
  },
  helpText: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
  bottomContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 20,
  },
  bottomText: {
    color: '#666',
    fontSize: 14,
  },
  loginText: {
    color: '#2196F3',
    fontSize: 14,
    fontWeight: 'bold',
    marginLeft: 4,
  },
});

export default ForgotPasswordScreen;