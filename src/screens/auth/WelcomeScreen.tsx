import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Image,
  Dimensions,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { Button } from '../../components/ui/Button';
import { colors, typography, spacing, borderRadius, shadows } from '../../constants/theme';

const { width: screenWidth, height: screenHeight } = Dimensions.get('window');

type AuthStackParamList = {
  Welcome: undefined;
  Login: undefined;
  Register: undefined;
  ForgotPassword: undefined;
};

type WelcomeScreenNavigationProp = NativeStackNavigationProp<AuthStackParamList, 'Welcome'>;

const WelcomeScreen: React.FC = () => {
  const navigation = useNavigation<WelcomeScreenNavigationProp>();

  const handleLogin = () => {
    navigation.navigate('Login');
  };

  const handleRegister = () => {
    navigation.navigate('Register');
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView 
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* 品牌标识区域 */}
        <View style={styles.brandSection}>
          <View style={styles.logoContainer}>
            <View style={styles.logoPlaceholder}>
              <Text style={styles.logoText}>索克</Text>
              <Text style={styles.logoSubText}>SUOKE</Text>
            </View>
          </View>
          
          <Text style={styles.brandTitle}>索克生活</Text>
          <Text style={styles.brandSubtitle}>AI驱动的智慧健康管理平台</Text>
        </View>

        {/* 核心价值展示 */}
        <View style={styles.featuresSection}>
          <View style={styles.featureCard}>
            <View style={styles.featureIcon}>
              <Text style={styles.featureIconText}>🧠</Text>
            </View>
            <Text style={styles.featureTitle}>四智能体协同</Text>
            <Text style={styles.featureDescription}>
              小艾、小克、老克、索儿四大AI智能体，为您提供全方位健康管理
            </Text>
          </View>

          <View style={styles.featureCard}>
            <View style={styles.featureIcon}>
              <Text style={styles.featureIconText}>🌿</Text>
            </View>
            <Text style={styles.featureTitle}>中医智慧数字化</Text>
            <Text style={styles.featureDescription}>
              传统中医"辨证论治未病"理念与现代预防医学完美结合
            </Text>
          </View>

          <View style={styles.featureCard}>
            <View style={styles.featureIcon}>
              <Text style={styles.featureIconText}>🔒</Text>
            </View>
            <Text style={styles.featureTitle}>区块链数据安全</Text>
            <Text style={styles.featureDescription}>
              零知识健康数据验证，保护您的隐私安全
            </Text>
          </View>
        </View>

        {/* 操作按钮区域 */}
        <View style={styles.actionSection}>
          <Button
            title="立即登录"
            variant="primary"
            size="large"
            fullWidth
            onPress={handleLogin}
            style={styles.loginButton}
          />
          
          <Button
            title="注册账号"
            variant="outline"
            size="large"
            fullWidth
            onPress={handleRegister}
            style={styles.registerButton}
          />
        </View>

        {/* 底部信息 */}
        <View style={styles.footerSection}>
          <Text style={styles.footerText}>
            开启您的智慧健康生活之旅
          </Text>
          <Text style={styles.versionText}>
            版本 1.0.0
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    paddingHorizontal: spacing.lg,
  },
  
  // 品牌标识区域
  brandSection: {
    alignItems: 'center',
    paddingTop: spacing['2xl'],
    paddingBottom: spacing.xl,
  },
  logoContainer: {
    marginBottom: spacing.lg,
  },
  logoPlaceholder: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
    ...shadows.lg,
  },
  logoText: {
    fontSize: typography.fontSize['3xl'],
    fontWeight: '700',
    color: colors.white,
    fontFamily: typography.fontFamily.bold,
  },
  logoSubText: {
    fontSize: typography.fontSize.sm,
    color: colors.white,
    opacity: 0.9,
    fontFamily: typography.fontFamily.medium,
  },
  brandTitle: {
    fontSize: typography.fontSize['4xl'],
    fontWeight: '700',
    color: colors.textPrimary,
    marginBottom: spacing.sm,
    fontFamily: typography.fontFamily.bold,
  },
  brandSubtitle: {
    fontSize: typography.fontSize.lg,
    color: colors.textSecondary,
    textAlign: 'center',
    lineHeight: typography.lineHeight.relaxed * typography.fontSize.lg,
    fontFamily: typography.fontFamily.regular,
  },

  // 功能特性区域
  featuresSection: {
    paddingVertical: spacing.xl,
  },
  featureCard: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    marginBottom: spacing.md,
    alignItems: 'center',
    ...shadows.sm,
  },
  featureIcon: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: colors.primaryLight,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  featureIconText: {
    fontSize: typography.fontSize['2xl'],
  },
  featureTitle: {
    fontSize: typography.fontSize.xl,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: spacing.sm,
    fontFamily: typography.fontFamily.medium,
  },
  featureDescription: {
    fontSize: typography.fontSize.base,
    color: colors.textSecondary,
    textAlign: 'center',
    lineHeight: typography.lineHeight.relaxed * typography.fontSize.base,
    fontFamily: typography.fontFamily.regular,
  },

  // 操作按钮区域
  actionSection: {
    paddingVertical: spacing.xl,
  },
  loginButton: {
    marginBottom: spacing.md,
  },
  registerButton: {
    marginBottom: spacing.lg,
  },

  // 底部信息
  footerSection: {
    alignItems: 'center',
    paddingBottom: spacing.xl,
  },
  footerText: {
    fontSize: typography.fontSize.base,
    color: colors.textSecondary,
    textAlign: 'center',
    marginBottom: spacing.sm,
    fontFamily: typography.fontFamily.regular,
  },
  versionText: {
    fontSize: typography.fontSize.sm,
    color: colors.textTertiary,
    fontFamily: typography.fontFamily.regular,
  },
});

export default WelcomeScreen; 