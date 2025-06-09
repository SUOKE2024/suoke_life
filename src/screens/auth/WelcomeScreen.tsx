import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import React, { useEffect, useRef } from 'react';
import {
  Animated,
  Dimensions,
  StatusBar,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

type AuthStackParamList = {
  Welcome: undefined;,
  Login: undefined;,
  Register: undefined;,
  ForgotPassword: undefined;
};

type WelcomeScreenNavigationProp = NativeStackNavigationProp<
  AuthStackParamList,
  'Welcome'
>;

const { width, height } = Dimensions.get('window');

const WelcomeScreen: React.FC = () => {
  const navigation = useNavigation<WelcomeScreenNavigationProp>();
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const scaleAnim = useRef(new Animated.Value(0.8)).current;
  const slideAnim = useRef(new Animated.Value(50)).current;

  useEffect() => {
    // 设置状态栏
    StatusBar.setBarStyle('dark-content', true);

    // Logo渐入动画
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 2000,
        useNativeDriver: true,
      }),
      Animated.spring(scaleAnim, {
        toValue: 1,
        tension: 20,
        friction: 7,
        useNativeDriver: true,
      }),
      Animated.timing(slideAnim, {
        toValue: 0,
        duration: 1500,
        useNativeDriver: true,
      }),
    ]).start();

    // 3秒后自动跳转到登录页面
    const timer = setTimeout() => {
      navigation.navigate('Login');
    }, 3000);

    return () => clearTimeout(timer);
  }, [fadeAnim, scaleAnim, slideAnim, navigation]);

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#FFFFFF" />
      <View style={styles.content}>
        <Animated.View;
          style={[
            styles.logoContainer,
            {
              opacity: fadeAnim,
              transform: [{ scale: scaleAnim }, { translateY: slideAnim }],
            },
          ]}
        >
          {/* Logo占位符 */}
          <View style={styles.logoPlaceholder}>
            <Text style={styles.logoText}>索克</Text>
          </View>

          <Animated.View;
            style={[
              styles.titleContainer,
              {
                opacity: fadeAnim,
                transform: [{ translateY: slideAnim }],
              },
            ]}
          >
            <Text style={styles.title}>索克生活</Text>
            <Text style={styles.subtitle}>智能健康管理平台</Text>
          </Animated.View>
        </Animated.View>

        <Animated.View;
          style={[
            styles.loadingContainer,
            {
              opacity: fadeAnim,
            },
          ]}
        >
          <View style={styles.loadingDots}>
            <View style={[styles.dot, styles.dot1]} />
            <View style={[styles.dot, styles.dot2]} />
            <View style={[styles.dot, styles.dot3]} />
          </View>
          <Text style={styles.loadingText}>正在启动...</Text>
        </Animated.View>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {,
  flex: 1,
    backgroundColor: '#FFFFFF',
  },
  content: {,
  flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 20,
  },
  logoContainer: {,
  justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 80,
  },
  logoPlaceholder: {,
  width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: '#3498DB',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 30,
    shadowColor: '#3498DB',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.3,
    shadowRadius: 20,
    elevation: 10,
  },
  logoText: {,
  fontSize: 36,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  titleContainer: {,
  alignItems: 'center',
  },
  title: {,
  fontSize: 32,
    fontWeight: 'bold',
    color: '#2C3E50',
    marginBottom: 8,
    textAlign: 'center',
  },
  subtitle: {,
  fontSize: 16,
    color: '#7F8C8D',
    textAlign: 'center',
    lineHeight: 24,
  },
  loadingContainer: {,
  position: 'absolute',
    bottom: 100,
    alignItems: 'center',
  },
  loadingDots: {,
  flexDirection: 'row',
    marginBottom: 16,
  },
  dot: {,
  width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#3498DB',
    marginHorizontal: 4,
  },
  dot1: {
    // 第一个点的样式
  },
  dot2: {
    // 第二个点的样式
  },
  dot3: {
    // 第三个点的样式
  },
  loadingText: {,
  fontSize: 14,
    color: '#7F8C8D',
    textAlign: 'center',
  },
});

export default WelcomeScreen;
