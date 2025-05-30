import {
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { AuthStackParamList } from '../../types/navigation';
import { colors, spacing, fonts, borderRadius, shadows } from '../../constants/theme';



import React, { useEffect, useRef } from 'react';
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  StatusBar,
  SafeAreaView,
  Animated,
  Dimensions,
} from 'react-native';

const { width, height } = Dimensions.get('window');

type WelcomeScreenNavigationProp = NativeStackNavigationProp<
  AuthStackParamList,
  'Welcome'
>;

export const WelcomeScreen: React.FC = () => {
  const navigation = useNavigation<WelcomeScreenNavigationProp>();
  
  // 动画值
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(50)).current;
  const logoScaleAnim = useRef(new Animated.Value(0.8)).current;
  const buttonSlideAnim = useRef(new Animated.Value(100)).current;
  const particleAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    // 启动动画序列
    Animated.sequence([
      // Logo动画
      Animated.parallel([
        Animated.timing(fadeAnim, {
          toValue: 1,
          duration: 1000,
          useNativeDriver: true,
        }),
        Animated.timing(logoScaleAnim, {
          toValue: 1,
          duration: 800,
          useNativeDriver: true,
        }),
      ]),
      // 文本动画
      Animated.timing(slideAnim, {
        toValue: 0,
        duration: 600,
        useNativeDriver: true,
      }),
      // 按钮动画
      Animated.timing(buttonSlideAnim, {
        toValue: 0,
        duration: 500,
        useNativeDriver: true,
      }),
    ]).start();

    // 粒子动画循环
    Animated.loop(
      Animated.timing(particleAnim, {
        toValue: 1,
        duration: 3000,
        useNativeDriver: true,
      })
    ).start();
  }, []);

  const handleLogin = useCallback( () => {, []);
    navigation.navigate('Login');
  };

  const handleRegister = useCallback( () => {, []);
    navigation.navigate('Register');
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="transparent" translucent />
      
      {/* 渐变背景 */}
      <View style={styles.gradientBackground}>
        <View style={styles.gradientOverlay} />
      </View>

      {/* 装饰性粒子元素 */}
      <Animated.View 
        style={[
          styles.decorativeElements,
          {
            opacity: particleAnim.interpolate({
              inputRange: [0, 0.5, 1],
              outputRange: [0.3, 0.8, 0.3],
            }),
          },
        ]}
      >
        <View style={[styles.particle, styles.particle1]} />
        <View style={[styles.particle, styles.particle2]} />
        <View style={[styles.particle, styles.particle3]} />
        <View style={[styles.particle, styles.particle4]} />
      </Animated.View>

      <View style={styles.content}>
        {/* Logo和标题区域 */}
        <Animated.View 
          style={[
            styles.logoContainer,
            {
              opacity: fadeAnim,
              transform: [
                { scale: logoScaleAnim },
                { translateY: slideAnim },
              ],
            },
          ]}
        >
          <View style={styles.logoWrapper}>
            <View style={styles.logoCircle}>
              <Text style={styles.logoText}>索</Text>
              <View style={styles.logoGlow} />
            </View>
          </View>
          
          <Text style={styles.appName}>索克生活</Text>
          <Text style={styles.appNameEn}>Suoke Life</Text>
          
          <Animated.View 
            style={[
              styles.taglineContainer,
              { transform: [{ translateY: slideAnim }] },
            ]}
          >
            <Text style={styles.tagline}>AI驱动的智慧健康管理平台</Text>
            <Text style={styles.subtitle}>
              融合中医智慧与现代科技{'\n'}开启您的健康新生活
            </Text>
          </Animated.View>
        </Animated.View>

        {/* 特色功能展示 */}
        <Animated.View 
          style={[
            styles.featuresContainer,
            { 
              opacity: fadeAnim,
              transform: [{ translateY: slideAnim }], 
            },
          ]}
        >
          <View style={styles.featureRow}>
            <View style={styles.featureItem}>
              <View style={[styles.featureIcon, { backgroundColor: colors.agents.xiaoai }]}>
                <Text style={styles.featureEmoji}>🤖</Text>
              </View>
              <Text style={styles.featureText}>AI智能体</Text>
              <Text style={styles.featureDesc}>四大智能助手</Text>
            </View>
            <View style={styles.featureItem}>
              <View style={[styles.featureIcon, { backgroundColor: colors.diagnosis.inspection }]}>
                <Text style={styles.featureEmoji}>🏥</Text>
              </View>
              <Text style={styles.featureText}>中医五诊</Text>
              <Text style={styles.featureDesc}>望闻问切算</Text>
            </View>
            <View style={styles.featureItem}>
              <View style={[styles.featureIcon, { backgroundColor: colors.agents.soer }]}>
                <Text style={styles.featureEmoji}>📊</Text>
              </View>
              <Text style={styles.featureText}>健康数据</Text>
              <Text style={styles.featureDesc}>智能分析</Text>
            </View>
          </View>
        </Animated.View>

        {/* 按钮区域 */}
        <Animated.View 
          style={[
            styles.buttonContainer,
            { 
              opacity: fadeAnim,
              transform: [{ translateY: buttonSlideAnim }], 
            },
          ]}
        >
          <TouchableOpacity 
            style={styles.loginButton} 
            onPress={handleLogin}
            activeOpacity={0.8}
          >
            <Text style={styles.loginButtonText}>立即登录</Text>
            <View style={styles.buttonGlow} />
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.registerButton}
            onPress={handleRegister}
            activeOpacity={0.8}
          >
            <Text style={styles.registerButtonText}>创建账户</Text>
          </TouchableOpacity>

          <Text style={styles.termsText}>
            继续即表示您同意我们的{' '}
            <Text style={styles.linkText}>服务条款</Text>
            {' '}和{' '}
            <Text style={styles.linkText}>隐私政策</Text>
          </Text>
        </Animated.View>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.primary,
  },
  gradientBackground: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: colors.primary,
  },
  gradientOverlay: {
    flex: 1,
    backgroundColor: 'rgba(15, 93, 53, 0.8)',
  },
  decorativeElements: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
  },
  particle: {
    position: 'absolute',
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: 'rgba(255, 255, 255, 0.3)',
  },
  particle1: {
    top: '20%',
    left: '15%',
  },
  particle2: {
    top: '35%',
    right: '20%',
  },
  particle3: {
    top: '60%',
    left: '25%',
  },
  particle4: {
    top: '75%',
    right: '15%',
  },
  content: {
    flex: 1,
    paddingHorizontal: spacing.lg,
    justifyContent: 'space-between',
    paddingTop: spacing.xxl * 2,
    paddingBottom: spacing.xl,
  },
  logoContainer: {
    alignItems: 'center',
    marginTop: spacing.xxl,
  },
  logoWrapper: {
    alignItems: 'center',
    marginBottom: spacing.lg,
  },
  logoCircle: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: 'rgba(255, 255, 255, 0.15)',
    justifyContent: 'center',
    alignItems: 'center',
    position: 'relative',
    borderWidth: 2,
    borderColor: 'rgba(255, 255, 255, 0.3)',
  },
  logoText: {
    fontSize: 48,
    fontWeight: 'bold',
    color: colors.white,
    textAlign: 'center',
  },
  logoGlow: {
    position: 'absolute',
    width: 140,
    height: 140,
    borderRadius: 70,
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    top: -10,
    left: -10,
  },
  appName: {
    fontSize: fonts.size.header,
    fontWeight: 'bold',
    color: colors.white,
    textAlign: 'center',
    marginBottom: spacing.xs,
  },
  appNameEn: {
    fontSize: fonts.size.lg,
    color: 'rgba(255, 255, 255, 0.8)',
    textAlign: 'center',
    marginBottom: spacing.lg,
  },
  taglineContainer: {
    alignItems: 'center',
    marginTop: spacing.md,
  },
  tagline: {
    fontSize: fonts.size.md,
    color: 'rgba(255, 255, 255, 0.9)',
    textAlign: 'center',
    marginBottom: spacing.sm,
    fontWeight: '500',
  },
  subtitle: {
    fontSize: fonts.size.sm,
    color: 'rgba(255, 255, 255, 0.7)',
    textAlign: 'center',
    lineHeight: fonts.lineHeight.md,
  },
  featuresContainer: {
    marginVertical: spacing.xl,
  },
  featureRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
  },
  featureItem: {
    alignItems: 'center',
    flex: 1,
  },
  featureIcon: {
    width: 60,
    height: 60,
    borderRadius: 30,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: spacing.sm,
    ...shadows.md,
  },
  featureEmoji: {
    fontSize: 24,
  },
  featureText: {
    fontSize: fonts.size.sm,
    color: colors.white,
    fontWeight: '600',
    textAlign: 'center',
    marginBottom: spacing.xs,
  },
  featureDesc: {
    fontSize: fonts.size.xs,
    color: 'rgba(255, 255, 255, 0.7)',
    textAlign: 'center',
  },
  buttonContainer: {
    paddingBottom: spacing.lg,
  },
  loginButton: {
    backgroundColor: colors.white,
    paddingVertical: spacing.md,
    borderRadius: borderRadius.lg,
    marginBottom: spacing.md,
    position: 'relative',
    overflow: 'hidden',
    ...shadows.lg,
  },
  loginButtonText: {
    fontSize: fonts.size.lg,
    fontWeight: 'bold',
    color: colors.primary,
    textAlign: 'center',
  },
  buttonGlow: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(53, 187, 120, 0.1)',
  },
  registerButton: {
    borderWidth: 2,
    borderColor: 'rgba(255, 255, 255, 0.5)',
    paddingVertical: spacing.md,
    borderRadius: borderRadius.lg,
    marginBottom: spacing.lg,
  },
  registerButtonText: {
    fontSize: fonts.size.lg,
    fontWeight: '600',
    color: colors.white,
    textAlign: 'center',
  },
  termsText: {
    fontSize: fonts.size.xs,
    color: 'rgba(255, 255, 255, 0.7)',
    textAlign: 'center',
    lineHeight: fonts.lineHeight.sm,
  },
  linkText: {
    color: colors.white,
    fontWeight: '500',
    textDecorationLine: 'underline',
  },
});
