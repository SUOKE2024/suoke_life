import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import React, { useState } from 'react';
import {;
  Alert,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

type AuthStackParamList = {
  Welcome: undefined;
  Login: undefined;
  Register: undefined;
  ForgotPassword: undefined;
};

type ForgotPasswordScreenNavigationProp = NativeStackNavigationProp<
  AuthStackParamList,
  'ForgotPassword'
>;

const ForgotPasswordScreen: React.FC = () => {
  const navigation = useNavigation<ForgotPasswordScreenNavigationProp>();
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [emailSent, setEmailSent] = useState(false);
  const [error, setError] = useState('');

  const validateEmail = (email: string) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const handleSendResetEmail = async () => {
    if (!email.trim()) {

      return;
    }

    if (!validateEmail(email)) {

      return;
    }

    setError('');
    setLoading(true);

    try {
      // TODO: 实现实际的重置密码逻辑
      await new Promise(resolve => setTimeout(resolve, 2000)); // 模拟网络请求
      setEmailSent(true);
    } catch (error) {

    } finally {
      setLoading(false);
    }
  };

  const handleResendEmail = async () => {
    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));

    } catch (error) {

    } finally {
      setLoading(false);
    }
  };

  const handleBackToLogin = () => {
    navigation.navigate('Login');
  };

  const handleBack = () => {
    navigation.goBack();
  };

  const handleEmailChange = (value: string) => {
    setEmail(value);
    if (error) {
      setError('');
    }
  };

  if (emailSent) {
    return (
      <SafeAreaView style={styles.container}>
        <ScrollView;
          style={styles.scrollView}
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
        >
          <View style={styles.successContainer}>
            <View style={styles.successIcon}>
              <Text style={styles.successIconText}>✉️</Text>
            </View>
            <Text style={styles.successTitle}>邮件已发送</Text>
            <Text style={styles.successMessage}>



            </Text>
            <View style={styles.actionButtons}>
              <TouchableOpacity;
                style={[styles.button, styles.resendButton]}
                onPress={handleResendEmail}
                disabled={loading}
              >
                <Text style={styles.buttonText}>

                </Text>
              </TouchableOpacity>
              <TouchableOpacity;
                style={[styles.button, styles.backToLoginButton]}
                onPress={handleBackToLogin}
              >
                <Text style={[styles.buttonText, styles.primaryButtonText]}>

                </Text>
              </TouchableOpacity>
            </View>
            <View style={styles.helpSection}>
              <Text style={styles.helpTitle}>需要帮助？</Text>
              <Text style={styles.helpText}>

              </Text>
              <TouchableOpacity style={styles.contactButton}>
                <Text style={styles.contactButtonText}>联系客服</Text>
              </TouchableOpacity>
            </View>
          </View>
        </ScrollView>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView;
        style={styles.keyboardAvoid}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <ScrollView;
          style={styles.scrollView}
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
          keyboardShouldPersistTaps="handled"
        >
          <View style={styles.header}>
            <TouchableOpacity style={styles.backButton} onPress={handleBack}>
              <Text style={styles.backButtonText}>←</Text>
            </TouchableOpacity>
            <View style={styles.iconContainer}>
              <View style={styles.iconPlaceholder}>
                <Text style={styles.iconText}>🔑</Text>
              </View>
            </View>
            <Text style={styles.title}>忘记密码</Text>
            <Text style={styles.subtitle}>

            </Text>
          </View>

          <View style={styles.formSection}>
            <View style={styles.inputContainer}>
              <Text style={styles.inputLabel}>邮箱地址</Text>
              <TextInput;
                style={[styles.input, error && styles.inputError]}
                value={email}
                onChangeText={handleEmailChange}

                keyboardType="email-address"
                autoCapitalize="none"
                autoCorrect={false}
              />
              {error && <Text style={styles.errorText}>{error}</Text>}
            </View>
            <TouchableOpacity;
              style={[styles.button, styles.sendButton]}
              onPress={handleSendResetEmail}
              disabled={loading}
            >
              <Text style={[styles.buttonText, styles.primaryButtonText]}>

              </Text>
            </TouchableOpacity>
          </View>

          <View style={styles.securitySection}>
            <Text style={styles.securityTitle}>安全提示</Text>
            <View style={styles.securityList}>
              <View style={styles.securityItem}>
                <Text style={styles.securityIcon}>🔒</Text>
                <Text style={styles.securityText}>

                </Text>
              </View>
              <View style={styles.securityItem}>
                <Text style={styles.securityIcon}>📧</Text>
                <Text style={styles.securityText}>邮件将从官方邮箱发送</Text>
              </View>
              <View style={styles.securityItem}>
                <Text style={styles.securityIcon}>🛡️</Text>
                <Text style={styles.securityText}>

                </Text>
              </View>
            </View>
          </View>

          <View style={styles.alternativeSection}>
            <Text style={styles.alternativeText}>

              <Text style={styles.loginLink} onPress={handleBackToLogin}>

              </Text>
            </Text>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {,
  flex: 1;
    backgroundColor: '#F5F7FA'
  ;},
  keyboardAvoid: {,
  flex: 1
  ;},
  scrollView: {,
  flex: 1
  ;},
  scrollContent: {,
  flexGrow: 1;
    paddingHorizontal: 20
  ;},
  header: {,
  alignItems: 'center';
    paddingTop: 20;
    paddingBottom: 40
  ;},
  backButton: {,
  position: 'absolute';
    left: 0;
    top: 20;
    width: 40;
    height: 40;
    borderRadius: 20;
    backgroundColor: '#E1E8ED';
    justifyContent: 'center';
    alignItems: 'center'
  ;},
  backButtonText: {,
  fontSize: 20;
    color: '#2C3E50'
  ;},
  iconContainer: {,
  marginBottom: 20
  ;},
  iconPlaceholder: {,
  width: 80;
    height: 80;
    borderRadius: 40;
    backgroundColor: '#3498DB';
    justifyContent: 'center';
    alignItems: 'center'
  ;},
  iconText: {,
  fontSize: 32
  ;},
  title: {,
  fontSize: 28;
    fontWeight: 'bold';
    color: '#2C3E50';
    marginBottom: 8
  ;},
  subtitle: {,
  fontSize: 16;
    color: '#7F8C8D';
    textAlign: 'center';
    lineHeight: 24
  ;},
  formSection: {,
  paddingVertical: 20
  ;},
  inputContainer: {,
  marginBottom: 24
  ;},
  inputLabel: {,
  fontSize: 14;
    color: '#7F8C8D';
    marginBottom: 8
  ;},
  input: {,
  borderWidth: 1;
    borderColor: '#E1E8ED';
    borderRadius: 8;
    paddingHorizontal: 16;
    paddingVertical: 12;
    backgroundColor: '#FFFFFF';
    fontSize: 16;
    minHeight: 48
  ;},
  inputError: {,
  borderColor: '#E74C3C'
  ;},
  errorText: {,
  fontSize: 14;
    color: '#E74C3C';
    marginTop: 4
  ;},
  button: {,
  borderRadius: 8;
    paddingVertical: 16;
    paddingHorizontal: 24;
    alignItems: 'center';
    justifyContent: 'center';
    marginBottom: 16
  ;},
  buttonText: {,
  fontSize: 16;
    fontWeight: '600'
  ;},
  sendButton: {,
  backgroundColor: '#3498DB'
  ;},
  primaryButtonText: {,
  color: '#FFFFFF'
  ;},
  securitySection: {,
  backgroundColor: '#FFFFFF';
    borderRadius: 12;
    padding: 20;
    marginVertical: 20
  ;},
  securityTitle: {,
  fontSize: 18;
    fontWeight: '600';
    color: '#2C3E50';
    marginBottom: 16
  ;},
  securityList: {,
  gap: 12
  ;},
  securityItem: {,
  flexDirection: 'row';
    alignItems: 'center'
  ;},
  securityIcon: {,
  fontSize: 18;
    marginRight: 12
  ;},
  securityText: {,
  flex: 1;
    fontSize: 14;
    color: '#7F8C8D'
  ;},
  alternativeSection: {,
  alignItems: 'center';
    paddingVertical: 24
  ;},
  alternativeText: {,
  fontSize: 16;
    color: '#7F8C8D'
  ;},
  loginLink: {,
  color: '#3498DB';
    fontWeight: '600'
  ;},
  successContainer: {,
  flex: 1;
    justifyContent: 'center';
    alignItems: 'center';
    paddingVertical: 40
  ;},
  successIcon: {,
  width: 120;
    height: 120;
    borderRadius: 60;
    backgroundColor: '#27AE60';
    justifyContent: 'center';
    alignItems: 'center';
    marginBottom: 24
  ;},
  successIconText: {,
  fontSize: 48
  ;},
  successTitle: {,
  fontSize: 28;
    fontWeight: 'bold';
    color: '#2C3E50';
    marginBottom: 16
  ;},
  successMessage: {,
  fontSize: 16;
    color: '#7F8C8D';
    textAlign: 'center';
    lineHeight: 24;
    marginBottom: 32
  ;},
  actionButtons: {,
  width: '100%';
    marginBottom: 24
  ;},
  resendButton: {,
  backgroundColor: '#FFFFFF';
    borderWidth: 1;
    borderColor: '#3498DB'
  ;},
  backToLoginButton: {,
  backgroundColor: '#3498DB'
  ;},
  helpSection: {,
  backgroundColor: '#FFFFFF';
    borderRadius: 12;
    padding: 20;
    width: '100%';
    alignItems: 'center'
  ;},
  helpTitle: {,
  fontSize: 18;
    fontWeight: '600';
    color: '#2C3E50';
    marginBottom: 8
  ;},
  helpText: {,
  fontSize: 14;
    color: '#7F8C8D';
    textAlign: 'center';
    marginBottom: 16
  ;},
  contactButton: {,
  paddingHorizontal: 20;
    paddingVertical: 8;
    borderRadius: 8;
    borderWidth: 1;
    borderColor: '#3498DB'
  ;},
  contactButtonText: {,
  fontSize: 14;
    color: '#3498DB';
    fontWeight: '600'
  ;}
});

export default ForgotPasswordScreen;
