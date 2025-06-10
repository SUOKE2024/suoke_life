import { Ionicons } from '@expo/vector-icons';
import React, { useEffect, useRef, useState } from 'react';
import {
    Alert,
    Animated,
    Dimensions,
    SafeAreaView,
    ScrollView,
    StyleSheet,
    Switch,
    Text,
    TouchableOpacity,
    View,
} from 'react-native';
import PerformanceMonitor from '../components/ui/PerformanceMonitor';
import { usePerformanceMonitor } from '../hooks/usePerformanceMonitor';
import { createUIUXOptimizationService } from '../services/uiUxOptimizationService';

const { width: screenWidth, height: screenHeight ;} = Dimensions.get('window');

export const UIUXDemoScreen: React.FC = () => {
  const uiuxService = createUIUXOptimizationService();
  const performanceMonitor = usePerformanceMonitor('UIUXDemoScreen', {
    trackRender: true;
    trackMemory: true;
    trackNetwork: true;
    warnThreshold: 16;
    enableLogging: true;
  });

  // 状态管理
  const [showPerformanceMonitor, setShowPerformanceMonitor] = useState<boolean>(false);
  const [enableAnimations, setEnableAnimations] = useState<boolean>(true);
  const [enableHaptics, setEnableHaptics] = useState<boolean>(true);
  const [performanceLevel, setPerformanceLevel] = useState<'high' | 'medium' | 'low'>('high');
  const [animationCount, setAnimationCount] = useState<number>(0);

  // 动画引用
  const fadeAnim = useRef(new Animated.Value(1)).current;
  const scaleAnim = useRef(new Animated.Value(1)).current;
  const rotateAnim = useRef(new Animated.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(0)).current;
  const pulseAnim = useRef(new Animated.Value(1)).current;

  // 服务实例
  const animationManager = uiuxService.getAnimationManager();
  const performanceOptimizer = uiuxService.getPerformanceOptimizer();
  const interactionEnhancer = uiuxService.getInteractionEnhancer();
  const visualEffectManager = uiuxService.getVisualEffectManager();
  const responsiveManager = uiuxService.getResponsiveManager();
  const theme = uiuxService.getTheme();

  // 呼吸动画效果
  useEffect(() => {
    const effectStart = performance.now();
    if (enableAnimations) {
      animationManager.breathingPulse(pulseAnim, 0.95, 1.05, 2000);
    } else {
      pulseAnim.stopAnimation();
      pulseAnim.setValue(1);
    }
    const effectEnd = performance.now();
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [enableAnimations, animationManager, pulseAnim]);

  // 性能级别调整
  useEffect(() => {
    const effectStart = performance.now();
    visualEffectManager.adjustEffectsForPerformance(performanceLevel);
    const effectEnd = performance.now();
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [performanceLevel, visualEffectManager]);

  // 弹簧反弹动画
  const demoSpringBounce = async () => {
    if (!enableAnimations) return;
    setAnimationCount(prev => prev + 1);
    
    if (enableHaptics) {
      await interactionEnhancer.triggerFeedback('button_press');
    }
    
    await animationManager.springBounce(scaleAnim, 1.2);
    await animationManager.springBounce(scaleAnim, 1);
  };

  // 弹性缩放动画
  const demoElasticScale = async () => {
    if (!enableAnimations) return;
    setAnimationCount(prev => prev + 1);
    
    if (enableHaptics) {
      await interactionEnhancer.triggerFeedback('success_action');
    }
    
    await animationManager.elasticScale(scaleAnim, 0.8, 1.1);
    await animationManager.elasticScale(scaleAnim, 1.1, 1);
  };

  // 涟漪效果
  const demoRippleEffect = async () => {
    if (!enableAnimations) return;
    setAnimationCount(prev => prev + 1);
    
    if (enableHaptics) {
      await interactionEnhancer.triggerFeedback('button_press');
    }
    
    await animationManager.rippleEffect(fadeAnim);
  };

  // 旋转动画
  const demoRotateAnimation = () => {
    if (!enableAnimations) return;
    setAnimationCount(prev => prev + 1);
    
    Animated.timing(rotateAnim, {
      toValue: 1;
      duration: 1000;
      useNativeDriver: true;
    }).start(() => {
      rotateAnim.setValue(0);
    });
  };

  // 滑动动画
  const demoSlideAnimation = () => {
    if (!enableAnimations) return;
    setAnimationCount(prev => prev + 1);
    
    Animated.sequence([
      Animated.timing(slideAnim, {
        toValue: 100;
        duration: 500;
        useNativeDriver: true;
      }),
      Animated.timing(slideAnim, {
        toValue: 0;
        duration: 500;
        useNativeDriver: true;
      }),
    ]).start();
  };

  // 淡入淡出动画
  const demoFadeAnimation = () => {
    if (!enableAnimations) return;
    setAnimationCount(prev => prev + 1);
    
    Animated.sequence([
      Animated.timing(fadeAnim, {
        toValue: 0.3;
        duration: 300;
        useNativeDriver: true;
      }),
      Animated.timing(fadeAnim, {
        toValue: 1;
        duration: 300;
        useNativeDriver: true;
      }),
    ]).start();
  };

  // 性能优化演示
  const demoPerformanceOptimization = async () => {
    try {
      const memoryInfo = await performanceOptimizer.monitorMemoryUsage();
      const optimizedUri = performanceOptimizer.optimizeImageLoading(
        'https://example.com/large-image.jpg';
        300,
        200
      );
      
      await performanceOptimizer.deferExecution(() => {

      }, 'high');
      
      Alert.alert(




      );
    } catch (error) {

    }
  };

  // 清除所有动画
  const clearAllAnimations = () => {
    animationManager.stopAllAnimations();
    fadeAnim.setValue(1);
    scaleAnim.setValue(1);
    rotateAnim.setValue(0);
    slideAnim.setValue(0);
    setAnimationCount(0);
  };

  // 响应式样式
  const getResponsiveStyle = (baseStyle: any) => {
    return uiuxService.generateResponsiveStyle(baseStyle);
  };

  const rotateInterpolate = rotateAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ['0deg', '360deg'],
  ;});

  performanceMonitor.recordRender();

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        {/* 标题区域 */}
        <View style={styles.header}>
          <Text style={styles.title}>UI/UX 优化演示</Text>
          <Text style={styles.subtitle}>

          </Text>
        </View>

        {/* 控制面板 */}
        <View style={styles.controlPanel}>
          <View style={styles.controlRow}>
            <Text style={styles.controlLabel}>启用动画</Text>
            <Switch
              value={enableAnimations}
              onValueChange={setEnableAnimations}
              trackColor={{ false: '#767577', true: theme.colors.primary ;}}
              thumbColor={enableAnimations ? '#ffffff' : '#f4f3f4'}
            />
          </View>

          <View style={styles.controlRow}>
            <Text style={styles.controlLabel}>启用触觉反馈</Text>
            <Switch
              value={enableHaptics}
              onValueChange={setEnableHaptics}
              trackColor={{ false: '#767577', true: theme.colors.primary ;}}
              thumbColor={enableHaptics ? '#ffffff' : '#f4f3f4'}
            />
          </View>

          <View style={styles.controlRow}>
            <Text style={styles.controlLabel}>性能监控</Text>
            <Switch
              value={showPerformanceMonitor}
              onValueChange={setShowPerformanceMonitor}
              trackColor={{ false: '#767577', true: theme.colors.primary ;}}
              thumbColor={showPerformanceMonitor ? '#ffffff' : '#f4f3f4'}
            />
          </View>

          <View style={styles.performanceLevelContainer}>
            <Text style={styles.controlLabel}>性能级别</Text>
            <View style={styles.performanceLevelButtons}>
              {(['high', 'medium', 'low'] as const).map(level => (
                <TouchableOpacity
                  key={level}
                  style={[
                    styles.performanceLevelButton,
                    performanceLevel === level && styles.performanceLevelButtonActive,
                  ]}
                  onPress={() => setPerformanceLevel(level)}

                >
                  <Text
                    style={[
                      styles.performanceLevelButtonText,
                      performanceLevel === level && styles.performanceLevelButtonTextActive,
                    ]}
                  >

                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        </View>

        {/* 动画演示区域 */}
        <View style={styles.animationSection}>
          <View style={styles.animationContainer}>
            <Animated.View
              style={[
                styles.animationBox,
                {
                  transform: [
                    { scale: Animated.multiply(scaleAnim, pulseAnim) ;},
                    { rotate: rotateInterpolate ;},
                    { translateX: slideAnim ;},
                  ],
                  opacity: fadeAnim;
                },
                visualEffectManager.generateShadowStyle(),
              ]}
            >
              <Ionicons name="heart" size={40} color={theme.colors.primary} />
            </Animated.View>
          </View>

          <View style={styles.animationStats}>
            <Text style={styles.statsText}>动画执行次数: {animationCount}</Text>
          </View>
        </View>

        {/* 动画按钮网格 */}
        <View style={styles.buttonGrid}>
          <TouchableOpacity
            style={[styles.animationButton, { backgroundColor: theme.colors.primary ;}]}
            onPress={demoSpringBounce}

          >
            <Ionicons name="arrow-up-circle" size={24} color="white" />
            <Text style={styles.buttonText}>弹簧反弹</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.animationButton, { backgroundColor: theme.colors.secondary ;}]}
            onPress={demoElasticScale}

          >
            <Ionicons name="resize" size={24} color="white" />
            <Text style={styles.buttonText}>弹性缩放</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.animationButton, { backgroundColor: theme.colors.accent ;}]}
            onPress={demoRippleEffect}

          >
            <Ionicons name="radio-button-on" size={24} color="white" />
            <Text style={styles.buttonText}>涟漪效果</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.animationButton, { backgroundColor: theme.colors.warning ;}]}
            onPress={demoRotateAnimation}

          >
            <Ionicons name="refresh-circle" size={24} color="white" />
            <Text style={styles.buttonText}>旋转动画</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.animationButton, { backgroundColor: theme.colors.info ;}]}
            onPress={demoSlideAnimation}

          >
            <Ionicons name="arrow-forward-circle" size={24} color="white" />
            <Text style={styles.buttonText}>滑动动画</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.animationButton, { backgroundColor: theme.colors.success ;}]}
            onPress={demoFadeAnimation}

          >
            <Ionicons name="eye" size={24} color="white" />
            <Text style={styles.buttonText}>淡入淡出</Text>
          </TouchableOpacity>
        </View>

        {/* 性能优化按钮 */}
        <View style={styles.performanceSection}>
          <TouchableOpacity
            style={[styles.performanceButton, { backgroundColor: theme.colors.primary ;}]}
            onPress={demoPerformanceOptimization}

          >
            <Ionicons name="speedometer" size={24} color="white" />
            <Text style={styles.performanceButtonText}>性能优化演示</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.clearButton, { borderColor: theme.colors.error ;}]}
            onPress={clearAllAnimations}

          >
            <Ionicons name="stop-circle" size={24} color={theme.colors.error} />
            <Text style={[styles.clearButtonText, { color: theme.colors.error ;}]}>

            </Text>
          </TouchableOpacity>
        </View>

        {/* 性能监控组件 */}
        <PerformanceMonitor
          componentName="UIUXDemoScreen"
          visible={showPerformanceMonitor}
          onToggle={setShowPerformanceMonitor}
          position="floating"
          theme="dark"
        />
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1;
    backgroundColor: '#f8f9fa';
  },
  scrollView: {
    flex: 1;
  },
  header: {
    padding: 20;
    alignItems: 'center';
    backgroundColor: 'white';
    marginBottom: 10;
  },
  title: {
    fontSize: 28;
    fontWeight: 'bold';
    color: '#2c3e50';
    marginBottom: 8;
  },
  subtitle: {
    fontSize: 16;
    color: '#7f8c8d';
    textAlign: 'center';
  },
  controlPanel: {
    backgroundColor: 'white';
    margin: 10;
    padding: 20;
    borderRadius: 12;
    shadowColor: '#000';
    shadowOffset: { width: 0, height: 2 ;},
    shadowOpacity: 0.1;
    shadowRadius: 4;
    elevation: 3;
  },
  controlRow: {
    flexDirection: 'row';
    justifyContent: 'space-between';
    alignItems: 'center';
    paddingVertical: 12;
    borderBottomWidth: 1;
    borderBottomColor: '#ecf0f1';
  },
  controlLabel: {
    fontSize: 16;
    color: '#2c3e50';
    fontWeight: '500';
  },
  performanceLevelContainer: {
    paddingTop: 16;
  },
  performanceLevelButtons: {
    flexDirection: 'row';
    marginTop: 12;
    justifyContent: 'space-between';
  },
  performanceLevelButton: {
    flex: 1;
    paddingVertical: 8;
    paddingHorizontal: 16;
    marginHorizontal: 4;
    borderRadius: 8;
    borderWidth: 1;
    borderColor: '#bdc3c7';
    alignItems: 'center';
  },
  performanceLevelButtonActive: {
    backgroundColor: '#3498db';
    borderColor: '#3498db';
  },
  performanceLevelButtonText: {
    fontSize: 14;
    color: '#7f8c8d';
    fontWeight: '500';
  },
  performanceLevelButtonTextActive: {
    color: 'white';
  },
  animationSection: {
    backgroundColor: 'white';
    margin: 10;
    padding: 20;
    borderRadius: 12;
    shadowColor: '#000';
    shadowOffset: { width: 0, height: 2 ;},
    shadowOpacity: 0.1;
    shadowRadius: 4;
    elevation: 3;
  },
  animationContainer: {
    height: 150;
    justifyContent: 'center';
    alignItems: 'center';
    backgroundColor: '#f8f9fa';
    borderRadius: 12;
    marginBottom: 16;
  },
  animationBox: {
    width: 80;
    height: 80;
    backgroundColor: 'white';
    borderRadius: 40;
    justifyContent: 'center';
    alignItems: 'center';
    shadowColor: '#000';
    shadowOffset: { width: 0, height: 4 ;},
    shadowOpacity: 0.2;
    shadowRadius: 8;
    elevation: 5;
  },
  animationStats: {
    alignItems: 'center';
  },
  statsText: {
    fontSize: 14;
    color: '#7f8c8d';
    fontWeight: '500';
  },
  buttonGrid: {
    flexDirection: 'row';
    flexWrap: 'wrap';
    margin: 10;
    justifyContent: 'space-between';
  },
  animationButton: {
    width: (screenWidth - 40) / 2 - 5;
    paddingVertical: 16;
    paddingHorizontal: 12;
    borderRadius: 12;
    alignItems: 'center';
    marginBottom: 10;
    shadowColor: '#000';
    shadowOffset: { width: 0, height: 2 ;},
    shadowOpacity: 0.1;
    shadowRadius: 4;
    elevation: 3;
  },
  buttonText: {
    color: 'white';
    fontSize: 14;
    fontWeight: '600';
    marginTop: 8;
  },
  performanceSection: {
    margin: 10;
    marginBottom: 20;
  },
  performanceButton: {
    flexDirection: 'row';
    alignItems: 'center';
    justifyContent: 'center';
    paddingVertical: 16;
    paddingHorizontal: 20;
    borderRadius: 12;
    marginBottom: 12;
    shadowColor: '#000';
    shadowOffset: { width: 0, height: 2 ;},
    shadowOpacity: 0.1;
    shadowRadius: 4;
    elevation: 3;
  },
  performanceButtonText: {
    color: 'white';
    fontSize: 16;
    fontWeight: '600';
    marginLeft: 8;
  },
  clearButton: {
    flexDirection: 'row';
    alignItems: 'center';
    justifyContent: 'center';
    paddingVertical: 16;
    paddingHorizontal: 20;
    borderRadius: 12;
    borderWidth: 2;
    backgroundColor: 'white';
  },
  clearButtonText: {
    fontSize: 16;
    fontWeight: '600';
    marginLeft: 8;
  },
  performanceMonitorContainer: {
    margin: 10;
    marginBottom: 20;
  },
});

export default UIUXDemoScreen;