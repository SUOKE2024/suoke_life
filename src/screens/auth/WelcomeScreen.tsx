import React, { useEffect, useRef, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Animated,
  Dimensions,
  StatusBar,
  TouchableOpacity,
  Image,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import Icon from 'react-native-vector-icons/MaterialIcons';

const { width: screenWidth, height: screenHeight } = Dimensions.get('window');

const WelcomeScreen: React.FC = () => {
  const navigation = useNavigation();
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const scaleAnim = useRef(new Animated.Value(0.3)).current;
  const slideAnim = useRef(new Animated.Value(50)).current;
  const [animationComplete, setAnimationComplete] = useState(false);

  useEffect(() => {
    // Logo渐入动画序列
    const animationSequence = Animated.sequence([
      // Logo缩放和渐入
      Animated.parallel([
        Animated.timing(fadeAnim, {
          toValue: 1,
          duration: 1000,
          useNativeDriver: true,
        }),
        Animated.spring(scaleAnim, {
          toValue: 1,
          tension: 50,
          friction: 7,
          useNativeDriver: true,
        }),
      ]),
      // 文字滑入
      Animated.timing(slideAnim, {
        toValue: 0,
        duration: 800,
        useNativeDriver: true,
      }),
    ]);

    animationSequence.start(() => {
      setAnimationComplete(true);
      // 3秒后自动跳转到登录页面
      setTimeout(() => {
        navigation.navigate('Login' as never);
      }, 2000);
    });
  }, [fadeAnim, scaleAnim, slideAnim, navigation]);

  const handleSkip = () => {
    navigation.navigate('Login' as never);
  };

  const handleGetStarted = () => {
    navigation.navigate('Login' as never);
  };

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#2196F3" />
      
      {/* 背景渐变 */}
      <View style={styles.backgroundGradient} />
      
      {/* 跳过按钮 */}
      {animationComplete && (
        <TouchableOpacity style={styles.skipButton} onPress={handleSkip}>
          <Text style={styles.skipText}>跳过</Text>
        </TouchableOpacity>
      )}

      {/* 主要内容 */}
      <View style={styles.content}>
        {/* Logo区域 */}
        <View style={styles.logoContainer}>
          <Animated.View
            style={[
              styles.logoWrapper,
              {
                opacity: fadeAnim,
                transform: [{ scale: scaleAnim }],
              },
            ]}
          >
            {/* 索克生活Logo */}
            <View style={styles.logoBackground}>
              <Icon name="healing" size={40} color="#ffffff" />
              <Text style={styles.logoText}>索克</Text>
            </View>
          </Animated.View>
          
          {/* 应用名称 */}
          <Animated.View
            style={[
              styles.titleContainer,
              {
                opacity: fadeAnim,
                transform: [{ translateY: slideAnim }],
              },
            ]}
          >
            <Text style={styles.appTitle}>索克生活</Text>
            <Text style={styles.appSubtitle}>SUOKE LIFE</Text>
          </Animated.View>
        </View>

        {/* 描述文字 */}
        <Animated.View
          style={[
            styles.descriptionContainer,
            {
              opacity: fadeAnim,
              transform: [{ translateY: slideAnim }],
            },
          ]}
        >
          <Text style={styles.description}>
            AI驱动的健康管理平台
          </Text>
          <Text style={styles.subDescription}>
            将中医智慧数字化，融入现代生活场景
          </Text>
          <Text style={styles.subDescription}>
            打造个性化的全生命周期健康管理服务
          </Text>
        </Animated.View>

        {/* 特色功能展示 */}
        {animationComplete && (
          <Animated.View
            style={[
              styles.featuresContainer,
              {
                opacity: fadeAnim,
              },
            ]}
          >
            <View style={styles.featureItem}>
              <Icon name="smart-toy" size={24} color="#ffffff" />
              <Text style={styles.featureText}>四大智能体</Text>
            </View>
            <View style={styles.featureItem}>
              <Icon name="healing" size={24} color="#ffffff" />
              <Text style={styles.featureText}>中医辨证</Text>
            </View>
            <View style={styles.featureItem}>
              <Icon name="security" size={24} color="#ffffff" />
              <Text style={styles.featureText}>区块链安全</Text>
            </View>
          </Animated.View>
        )}
      </View>

      {/* 底部按钮 */}
      {animationComplete && (
        <Animated.View
          style={[
            styles.bottomContainer,
            {
              opacity: fadeAnim,
              transform: [{ translateY: slideAnim }],
            },
          ]}
        >
          <TouchableOpacity
            style={styles.getStartedButton}
            onPress={handleGetStarted}
            activeOpacity={0.8}
          >
            <Text style={styles.getStartedText}>开始体验</Text>
            <Icon name="arrow-forward" size={20} color="#2196F3" />
          </TouchableOpacity>
          
          <View style={styles.indicatorContainer}>
            <View style={[styles.indicator, styles.activeIndicator]} />
            <View style={styles.indicator} />
            <View style={styles.indicator} />
          </View>
        </Animated.View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#2196F3',
  },
  backgroundGradient: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: '#2196F3',
    // 可以添加渐变背景
  },
  skipButton: {
    position: 'absolute',
    top: 50,
    right: 20,
    zIndex: 10,
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
  },
  skipText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '500',
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 40,
  },
  logoContainer: {
    alignItems: 'center',
    marginBottom: 60,
  },
  logoWrapper: {
    marginBottom: 30,
  },
  logoBackground: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 8,
    },
    shadowOpacity: 0.3,
    shadowRadius: 10,
    elevation: 15,
  },
  logoText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#ffffff',
    marginTop: 4,
  },
  logoImage: {
    width: 120,
    height: 120,
    borderRadius: 60,
  },
  titleContainer: {
    alignItems: 'center',
  },
  appTitle: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 8,
    textAlign: 'center',
  },
  appSubtitle: {
    fontSize: 16,
    color: 'rgba(255, 255, 255, 0.8)',
    letterSpacing: 2,
    textAlign: 'center',
  },
  descriptionContainer: {
    alignItems: 'center',
    marginBottom: 40,
  },
  description: {
    fontSize: 18,
    color: '#ffffff',
    textAlign: 'center',
    marginBottom: 16,
    fontWeight: '500',
  },
  subDescription: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.8)',
    textAlign: 'center',
    lineHeight: 20,
    marginBottom: 4,
  },
  featuresContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    width: '100%',
    marginBottom: 40,
  },
  featureItem: {
    alignItems: 'center',
    flex: 1,
  },
  featureText: {
    color: '#ffffff',
    fontSize: 12,
    marginTop: 8,
    textAlign: 'center',
  },
  bottomContainer: {
    paddingHorizontal: 40,
    paddingBottom: 50,
    alignItems: 'center',
  },
  getStartedButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#ffffff',
    paddingHorizontal: 32,
    paddingVertical: 16,
    borderRadius: 30,
    marginBottom: 30,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 10,
  },
  getStartedText: {
    color: '#2196F3',
    fontSize: 16,
    fontWeight: 'bold',
    marginRight: 8,
  },
  indicatorContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  indicator: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: 'rgba(255, 255, 255, 0.3)',
    marginHorizontal: 4,
  },
  activeIndicator: {
    backgroundColor: '#ffffff',
    width: 24,
  },
});

export default WelcomeScreen;