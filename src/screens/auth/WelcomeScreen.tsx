import React, { useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  StatusBar,
  SafeAreaView,
  Animated,
  Dimensions,
  ImageBackground,
  Image,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { useDispatch } from 'react-redux';
import { AuthStackParamList } from '../../navigation/AuthNavigator';
import { colors, spacing, fonts, borderRadius, shadows } from '../../constants/theme';
import { devLogin } from '../../store/slices/authSlice';

const { width, height } = Dimensions.get('window');

type WelcomeScreenNavigationProp = NativeStackNavigationProp<
  AuthStackParamList,
  'Welcome'
>;

export const WelcomeScreen: React.FC = () => {
  const navigation = useNavigation<WelcomeScreenNavigationProp>();
  const dispatch = useDispatch();
  
  // 动画值
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(50)).current;
  const logoScaleAnim = useRef(new Animated.Value(0.8)).current;
  const buttonSlideAnim = useRef(new Animated.Value(100)).current;

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
  }, []);

  const handleLogin = () => {
    navigation.navigate('Login');
  };

  const handleRegister = () => {
    navigation.navigate('Register');
  };

  // 测试登录功能 - 快速进入应用
  const handleTestLogin = () => {
    console.log('🚀 启动开发者模式登录...');
    dispatch(devLogin());
    console.log('✅ 开发者模式登录成功，即将进入主应用');
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="transparent" translucent />
      
      {/* 渐变背景 */}
      <View style={styles.gradientBackground}>
        <View style={styles.gradientOverlay} />
      </View>

      {/* 装饰性元素 */}
      <View style={styles.decorativeElements}>
        <View style={[styles.circle, styles.circle1]} />
        <View style={[styles.circle, styles.circle2]} />
        <View style={[styles.circle, styles.circle3]} />
      </View>

      <View style={styles.content}>
        {/* Logo和标题区域 */}
        <Animated.View 
          style={[
            styles.logoContainer,
            {
              opacity: fadeAnim,
              transform: [
                { scale: logoScaleAnim },
                { translateY: slideAnim }
              ]
            }
          ]}
        >
          <TouchableOpacity 
            style={styles.logoWrapper}
            onLongPress={handleTestLogin}
            delayLongPress={2000}
            activeOpacity={0.8}
          >
            <View style={styles.logoCircle}>
              <Image 
                source={require('../../assets/images/logo.png')}
                style={styles.logoImage}
                resizeMode="contain"
              />
            </View>
            <View style={styles.logoGlow} />
          </TouchableOpacity>
          
          <Text style={styles.appName}>索克生活</Text>
          <Text style={styles.appNameEn}>Suoke Life</Text>
          
          <Animated.View 
            style={[
              styles.taglineContainer,
              { transform: [{ translateY: slideAnim }] }
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
              transform: [{ translateY: slideAnim }] 
            }
          ]}
        >
          <View style={styles.featureRow}>
            <View style={styles.featureItem}>
              <Text style={styles.featureIcon}>🤖</Text>
              <Text style={styles.featureText}>AI智能体</Text>
            </View>
            <View style={styles.featureItem}>
              <Text style={styles.featureIcon}>🏥</Text>
              <Text style={styles.featureText}>中医四诊</Text>
            </View>
            <View style={styles.featureItem}>
              <Text style={styles.featureIcon}>📊</Text>
              <Text style={styles.featureText}>健康数据</Text>
            </View>
          </View>
        </Animated.View>

        {/* 按钮区域 */}
        <Animated.View 
          style={[
            styles.buttonContainer,
            { 
              opacity: fadeAnim,
              transform: [{ translateY: buttonSlideAnim }] 
            }
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
            <Text style={styles.termsLink}>服务条款</Text>
            {' '}和{' '}
            <Text style={styles.termsLink}>隐私政策</Text>
          </Text>

          {/* 开发者快速登录按钮 */}
          <TouchableOpacity
            style={styles.devButton}
            onPress={handleTestLogin}
            activeOpacity={0.7}
          >
            <Text style={styles.devButtonText}>🚀 开发者快速登录</Text>
          </TouchableOpacity>
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
    backgroundColor: 'rgba(53, 187, 120, 0.9)',
  },
  decorativeElements: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
  },
  circle: {
    position: 'absolute',
    borderRadius: 100,
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
  },
  circle1: {
    width: 200,
    height: 200,
    top: -100,
    right: -100,
  },
  circle2: {
    width: 150,
    height: 150,
    bottom: 100,
    left: -75,
  },
  circle3: {
    width: 100,
    height: 100,
    top: height * 0.3,
    right: 20,
  },
  content: {
    flex: 1,
    paddingHorizontal: spacing.xl,
    paddingVertical: spacing.xxl,
    justifyContent: 'space-between',
  },
  logoContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingTop: spacing.xxl,
  },
  logoWrapper: {
    position: 'relative',
    marginBottom: spacing.xl,
  },
  logoCircle: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: colors.surface,
    justifyContent: 'center',
    alignItems: 'center',
    ...shadows.lg,
  },
  logoGlow: {
    position: 'absolute',
    top: -10,
    left: -10,
    right: -10,
    bottom: -10,
    borderRadius: 70,
    backgroundColor: 'rgba(255, 255, 255, 0.3)',
    zIndex: -1,
  },
  logoIcon: {
    fontSize: 48,
  },
  logoImage: {
    width: 80,
    height: 80,
  },
  appName: {
    fontSize: fonts.size.header,
    fontWeight: 'bold',
    color: colors.surface,
    textAlign: 'center',
    marginBottom: spacing.xs,
  },
  appNameEn: {
    fontSize: fonts.size.lg,
    color: 'rgba(255, 255, 255, 0.8)',
    textAlign: 'center',
    marginBottom: spacing.xl,
  },
  taglineContainer: {
    alignItems: 'center',
  },
  tagline: {
    fontSize: fonts.size.xl,
    color: colors.surface,
    textAlign: 'center',
    fontWeight: '600',
    marginBottom: spacing.md,
  },
  subtitle: {
    fontSize: fonts.size.md,
    color: 'rgba(255, 255, 255, 0.9)',
    textAlign: 'center',
    lineHeight: 24,
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
    fontSize: 32,
    marginBottom: spacing.sm,
  },
  featureText: {
    fontSize: fonts.size.sm,
    color: colors.surface,
    textAlign: 'center',
    fontWeight: '500',
  },
  buttonContainer: {
    paddingBottom: spacing.xl,
  },
  loginButton: {
    backgroundColor: colors.surface,
    paddingVertical: spacing.lg,
    paddingHorizontal: spacing.xl,
    borderRadius: borderRadius.lg,
    alignItems: 'center',
    marginBottom: spacing.md,
    position: 'relative',
    overflow: 'hidden',
    ...shadows.md,
  },
  buttonGlow: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(53, 187, 120, 0.1)',
    borderRadius: borderRadius.lg,
  },
  loginButtonText: {
    color: colors.primary,
    fontSize: fonts.size.lg,
    fontWeight: 'bold',
    zIndex: 1,
  },
  registerButton: {
    backgroundColor: 'transparent',
    paddingVertical: spacing.lg,
    paddingHorizontal: spacing.xl,
    borderRadius: borderRadius.lg,
    borderWidth: 2,
    borderColor: colors.surface,
    alignItems: 'center',
    marginBottom: spacing.lg,
  },
  registerButtonText: {
    color: colors.surface,
    fontSize: fonts.size.lg,
    fontWeight: '600',
  },
  termsText: {
    fontSize: fonts.size.sm,
    color: 'rgba(255, 255, 255, 0.7)',
    textAlign: 'center',
    lineHeight: 20,
  },
  termsLink: {
    color: colors.surface,
    fontWeight: '600',
    textDecorationLine: 'underline',
  },
  devButton: {
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.lg,
    borderRadius: borderRadius.md,
    alignItems: 'center',
    marginTop: spacing.lg,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.3)',
  },
  devButtonText: {
    color: colors.surface,
    fontSize: fonts.size.md,
    fontWeight: '600',
  },
});
