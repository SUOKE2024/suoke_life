import {
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Card, Button, Switch, Slider, Modal } from '../ui';
import { colors, spacing, typography } from '../../constants/theme';


import React, { useState, useEffect, useCallback, useMemo, useRef } from 'react';
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Dimensions,
  Animated,
  Alert,
  AccessibilityInfo,
  AppState,
  AppStateStatus,
  Platform,
  Vibration,
  Linking,
} from 'react-native';


const { width, height } = Dimensions.get('window');

interface PerformanceMetrics {
  renderTime: number;
  memoryUsage: number;
  networkLatency: number;
  errorCount: number;
  crashCount: number;
  userSatisfaction: number;
}

interface AccessibilitySettings {
  screenReader: boolean;
  highContrast: boolean;
  largeText: boolean;
  reduceMotion: boolean;
  voiceOver: boolean;
  hapticFeedback: boolean;
}

interface PersonalizationSettings {
  theme: 'light' | 'dark' | 'auto';
  language: 'zh' | 'en';
  fontSize: number;
  animationSpeed: number;
  notificationPreferences: {
    health: boolean;
    agents: boolean;
    system: boolean;
  };
}

interface UserFeedback {
  id: string;
  type: 'bug' | 'feature' | 'improvement' | 'general';
  rating: number;
  message: string;
  timestamp: Date;
  resolved: boolean;
}

interface UserExperienceOptimizerProps {
  onSettingsChange?: (settings: any) => void;
  onFeedbackSubmit?: (feedback: UserFeedback) => void;
  onPerformanceAlert?: (metrics: PerformanceMetrics) => void;
}

export const UserExperienceOptimizer: React.FC<UserExperienceOptimizerProps> = ({
  onSettingsChange,
  onFeedbackSubmit,
  onPerformanceAlert,
}) => {
  const [accessibilitySettings, setAccessibilitySettings] = useState<AccessibilitySettings>({
    screenReader: false,
    highContrast: false,
    largeText: false,
    reduceMotion: false,
    voiceOver: false,
    hapticFeedback: true,
  });

  const [personalizationSettings, setPersonalizationSettings] = useState<PersonalizationSettings>({
    theme: 'auto',
    language: 'zh',
    fontSize: 16,
    animationSpeed: 1,
    notificationPreferences: {
      health: true,
      agents: true,
      system: true,
    },
  });

  const [performanceMetrics, setPerformanceMetrics] = useState<PerformanceMetrics>({
    renderTime: 0,
    memoryUsage: 0,
    networkLatency: 0,
    errorCount: 0,
    crashCount: 0,
    userSatisfaction: 4.5,
  });

  const [feedbackModal, setFeedbackModal] = useState(false);
  const [feedbackType, setFeedbackType] = useState<UserFeedback['type']>('general');
  const [feedbackRating, setFeedbackRating] = useState(5);
  const [feedbackMessage, setFeedbackMessage] = useState('');
  const [isScreenReaderEnabled, setIsScreenReaderEnabled] = useState(false);
  const [appState, setAppState] = useState<AppStateStatus>(AppState.currentState);

  const performanceTimer = useMemo(() => useMemo(() => useRef<ReturnType<typeof setTimeout>>(), []), []);
  const renderStartTime = useMemo(() => useMemo(() => useRef<number>(Date.now()), []), []);
  const animatedValue = useMemo(() => useMemo(() => useRef(new Animated.Value(0)).current, []), []);

  // 初始化
  useEffect(() => {
    initializeSettings();
    startPerformanceMonitoring();
    checkAccessibilityServices();
    setupAppStateListener();

    return () => {
      if (performanceTimer.current) {
        clearInterval(performanceTimer.current);
      }
    };
  }, []);

  // 启动动画
  useEffect(() => {
    Animated.timing(animatedValue, {
      toValue: 1,
      duration: personalizationSettings.animationSpeed * 800,
      useNativeDriver: true,
    }).start();
  }, [personalizationSettings.animationSpeed]);

  const initializeSettings = useMemo(() => useMemo(() => async () => {
    try {
      const savedAccessibility = await AsyncStorage.getItem('accessibility_settings'), []), []);
      const savedPersonalization = useMemo(() => useMemo(() => await AsyncStorage.getItem('personalization_settings'), []), []);

      if (savedAccessibility) {
        setAccessibilitySettings(JSON.parse(savedAccessibility));
      }

      if (savedPersonalization) {
        setPersonalizationSettings(JSON.parse(savedPersonalization));
      }
    } catch (error) {
      console.error('加载设置失败:', error);
    }
  };

  const saveSettings = useMemo(() => useMemo(() => async (type: 'accessibility' | 'personalization', settings: any) => {
    try {
      const key = `${type}_settings`, []), []);
      await AsyncStorage.setItem(key, JSON.stringify(settings));
      onSettingsChange?.({ type, settings });
    } catch (error) {
      console.error('保存设置失败:', error);
    }
  };

  const checkAccessibilityServices = useMemo(() => useMemo(() => async () => {
    try {
      const isScreenReaderEnabled = await AccessibilityInfo.isScreenReaderEnabled(), []), []);
      setIsScreenReaderEnabled(isScreenReaderEnabled);
      
      if (isScreenReaderEnabled) {
        setAccessibilitySettings(prev => ({ ...prev, screenReader: true }));
      }
    } catch (error) {
      console.error('检查无障碍服务失败:', error);
    }
  };

  const setupAppStateListener = useMemo(() => useMemo(() => useCallback( () => {, []), []), []);
    const handleAppStateChange = useMemo(() => useMemo(() => useCallback( (nextAppState: AppStateStatus) => {, []), []), []);
      if (appState.match(/inactive|background/) && nextAppState === 'active') {
        // 应用从后台回到前台，重新开始性能监控
        startPerformanceMonitoring();
      }
      setAppState(nextAppState);
    };

    const subscription = useMemo(() => useMemo(() => AppState.addEventListener('change', handleAppStateChange), []), []);
    return () => subscription?.remove();
  };

  const startPerformanceMonitoring = useMemo(() => useMemo(() => useCallback( () => {, []), []), []);
    renderStartTime.current = Date.now();
    
    performanceTimer.current = setInterval(() => {
      const currentMetrics = useMemo(() => useMemo(() => {
        renderTime: Date.now() - renderStartTime.current,
        memoryUsage: Math.random() * 100, // 模拟内存使用
        networkLatency: Math.random() * 200 + 50, // 模拟网络延迟
        errorCount: performanceMetrics.errorCount,
        crashCount: performanceMetrics.crashCount,
        userSatisfaction: performanceMetrics.userSatisfaction,
      }, []) // TODO: 检查依赖项 // TODO: 检查依赖项, []);

      setPerformanceMetrics(currentMetrics);

      // 性能警告
      if (currentMetrics.renderTime > 1000 || currentMetrics.memoryUsage > 80) {
        onPerformanceAlert?.(currentMetrics);
      }
    }, 5000);
  };

  const handleAccessibilityChange = useMemo(() => useMemo(() => useCallback((key: keyof AccessibilitySettings, value: boolean) => {
    const newSettings = { ...accessibilitySettings, [key]: value }, []) // TODO: 检查依赖项, []);
    setAccessibilitySettings(newSettings);
    saveSettings('accessibility', newSettings);

    // 触觉反馈
    if (newSettings.hapticFeedback && Platform.OS === 'ios') {
      Vibration.vibrate(50);
    }

    // 屏幕阅读器公告
    if (isScreenReaderEnabled) {
      AccessibilityInfo.announceForAccessibility(
        `${key === 'screenReader' ? '屏幕阅读器' : 
          key === 'highContrast' ? '高对比度' :
          key === 'largeText' ? '大字体' :
          key === 'reduceMotion' ? '减少动画' :
          key === 'voiceOver' ? '语音提示' : '触觉反馈'} ${value ? '已开启' : '已关闭'}`
      );
    }
  }, [accessibilitySettings, isScreenReaderEnabled]);

  const handlePersonalizationChange = useMemo(() => useMemo(() => useCallback((key: keyof PersonalizationSettings, value: any) => {
    const newSettings = { ...personalizationSettings, [key]: value }, []) // TODO: 检查依赖项, []);
    setPersonalizationSettings(newSettings);
    saveSettings('personalization', newSettings);
  }, [personalizationSettings]);

  const submitFeedback = useMemo(() => useMemo(() => useCallback(() => {
    if (!feedbackMessage.trim()) {
      Alert.alert('提示', '请输入反馈内容'), []), []);
      return;
    }

    const feedback: UserFeedback = {
      id: Date.now().toString(),
      type: feedbackType,
      rating: feedbackRating,
      message: feedbackMessage,
      timestamp: new Date(),
      resolved: false,
    };

    onFeedbackSubmit?.(feedback);
    setFeedbackModal(false);
    setFeedbackMessage('');
    setFeedbackRating(5);
    
    Alert.alert('感谢反馈', '您的反馈已提交，我们会尽快处理');
  }, [feedbackType, feedbackRating, feedbackMessage, onFeedbackSubmit]);

  const renderAccessibilitySettings = useMemo(() => useMemo(() => useMemo(() => (
    <Card style={styles.sectionCard}>
      <Text style={styles.sectionTitle}>无障碍设置</Text>
      <Text style={styles.sectionDescription}>
        让应用更易于使用，支持各种辅助功能
      </Text>

      <View style={styles.settingsList}>
        {Object.entries(accessibilitySettings).map(([key, value]) => (
          <View key={key} style={styles.settingItem}>
            <View style={styles.settingInfo}>
              <Text style={styles.settingLabel}>
                {key === 'screenReader' ? '屏幕阅读器' :
                 key === 'highContrast' ? '高对比度模式' :
                 key === 'largeText' ? '大字体显示' :
                 key === 'reduceMotion' ? '减少动画效果' :
                 key === 'voiceOver' ? '语音提示' : '触觉反馈'}
              </Text>
              <Text style={styles.settingDescription}>
                {key === 'screenReader' ? '为视觉障碍用户提供语音朗读' :
                 key === 'highContrast' ? '增强文字和背景的对比度' :
                 key === 'largeText' ? '放大文字以便阅读' :
                 key === 'reduceMotion' ? '减少动画以避免眩晕' :
                 key === 'voiceOver' ? '重要操作的语音提示' : '操作时的震动反馈'}
              </Text>
            </View>
            <Switch
              value={value}
              onValueChange={(newValue) => handleAccessibilityChange(key as keyof AccessibilitySettings, newValue)}
            />
          </View>
        ))}
      </View>
    </Card>
  ), [accessibilitySettings, handleAccessibilityChange]), []), []);

  const renderPersonalizationSettings = useMemo(() => useMemo(() => useMemo(() => (
    <Card style={styles.sectionCard}>
      <Text style={styles.sectionTitle}>个性化设置</Text>
      <Text style={styles.sectionDescription}>
        根据您的喜好定制应用体验
      </Text>

      <View style={styles.settingsList}>
        {/* 主题设置 */}
        <View style={styles.settingItem}>
          <View style={styles.settingInfo}>
            <Text style={styles.settingLabel}>主题模式</Text>
            <Text style={styles.settingDescription}>选择您喜欢的界面主题</Text>
          </View>
          <View style={styles.themeSelector}>
            {(['light', 'dark', 'auto'] as const).map((theme) => (
              <TouchableOpacity
                key={theme}
                style={[
                  styles.themeButton,
                  personalizationSettings.theme === theme && styles.activeThemeButton,
                ]}
                onPress={() => handlePersonalizationChange('theme', theme)}
              >
                <Text style={[
                  styles.themeText,
                  personalizationSettings.theme === theme && styles.activeThemeText,
                ]}>
                  {theme === 'light' ? '浅色' : theme === 'dark' ? '深色' : '自动'}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* 字体大小 */}
        <View style={styles.settingItem}>
          <View style={styles.settingInfo}>
            <Text style={styles.settingLabel}>字体大小</Text>
            <Text style={styles.settingDescription}>调整文字显示大小</Text>
          </View>
          <View style={styles.sliderContainer}>
            <Slider
              value={personalizationSettings.fontSize}
              minimumValue={12}
              maximumValue={24}
              step={1}
              onValueChange={(value) => handlePersonalizationChange('fontSize', value)}
              style={styles.slider}
            />
            <Text style={styles.sliderValue}>{personalizationSettings.fontSize}px</Text>
          </View>
        </View>

        {/* 动画速度 */}
        <View style={styles.settingItem}>
          <View style={styles.settingInfo}>
            <Text style={styles.settingLabel}>动画速度</Text>
            <Text style={styles.settingDescription}>调整界面动画的播放速度</Text>
          </View>
          <View style={styles.sliderContainer}>
            <Slider
              value={personalizationSettings.animationSpeed}
              minimumValue={0.5}
              maximumValue={2}
              step={0.1}
              onValueChange={(value) => handlePersonalizationChange('animationSpeed', value)}
              style={styles.slider}
            />
            <Text style={styles.sliderValue}>{personalizationSettings.animationSpeed.toFixed(1)}x</Text>
          </View>
        </View>
      </View>
    </Card>
  ), [personalizationSettings, handlePersonalizationChange]), []), []);

  const renderPerformanceMonitor = useMemo(() => useMemo(() => useMemo(() => (
    <Card style={styles.sectionCard}>
      <Text style={styles.sectionTitle}>性能监控</Text>
      <Text style={styles.sectionDescription}>
        实时监控应用性能，确保最佳体验
      </Text>

      <View style={styles.metricsGrid}>
        <View style={styles.metricItem}>
          <Ionicons name="speedometer" size={24} color={colors.primary} />
          <Text style={styles.metricLabel}>渲染时间</Text>
          <Text style={styles.metricValue}>{performanceMetrics.renderTime}ms</Text>
          <View style={[
            styles.metricStatus,
            { backgroundColor: performanceMetrics.renderTime < 500 ? colors.success : 
                             performanceMetrics.renderTime < 1000 ? colors.warning : colors.error },
          ]} />
        </View>

        <View style={styles.metricItem}>
          <Ionicons name="hardware-chip" size={24} color={colors.primary} />
          <Text style={styles.metricLabel}>内存使用</Text>
          <Text style={styles.metricValue}>{performanceMetrics.memoryUsage.toFixed(1)}%</Text>
          <View style={[
            styles.metricStatus,
            { backgroundColor: performanceMetrics.memoryUsage < 60 ? colors.success : 
                             performanceMetrics.memoryUsage < 80 ? colors.warning : colors.error },
          ]} />
        </View>

        <View style={styles.metricItem}>
          <Ionicons name="wifi" size={24} color={colors.primary} />
          <Text style={styles.metricLabel}>网络延迟</Text>
          <Text style={styles.metricValue}>{performanceMetrics.networkLatency.toFixed(0)}ms</Text>
          <View style={[
            styles.metricStatus,
            { backgroundColor: performanceMetrics.networkLatency < 100 ? colors.success : 
                             performanceMetrics.networkLatency < 200 ? colors.warning : colors.error },
          ]} />
        </View>

        <View style={styles.metricItem}>
          <Ionicons name="star" size={24} color={colors.primary} />
          <Text style={styles.metricLabel}>用户满意度</Text>
          <Text style={styles.metricValue}>{performanceMetrics.userSatisfaction.toFixed(1)}</Text>
          <View style={[
            styles.metricStatus,
            { backgroundColor: performanceMetrics.userSatisfaction > 4 ? colors.success : 
                             performanceMetrics.userSatisfaction > 3 ? colors.warning : colors.error },
          ]} />
        </View>
      </View>
    </Card>
  ), [performanceMetrics]), []), []);

  const renderFeedbackSection = useMemo(() => useMemo(() => useMemo(() => (
    <Card style={styles.sectionCard}>
      <Text style={styles.sectionTitle}>用户反馈</Text>
      <Text style={styles.sectionDescription}>
        您的意见对我们很重要，帮助我们改进产品
      </Text>

      <View style={styles.feedbackButtons}>
        <Button
          title="报告问题"
          onPress={() => {
            setFeedbackType('bug'), []), []);
            setFeedbackModal(true);
          }}
          variant="outline"
          style={styles.feedbackButton}
          leftIcon={<Ionicons name="bug" size={16} color={colors.error} />}
        />
        
        <Button
          title="功能建议"
          onPress={() => {
            setFeedbackType('feature');
            setFeedbackModal(true);
          }}
          variant="outline"
          style={styles.feedbackButton}
          leftIcon={<Ionicons name="bulb" size={16} color={colors.warning} />}
        />
        
        <Button
          title="使用体验"
          onPress={() => {
            setFeedbackType('general');
            setFeedbackModal(true);
          }}
          variant="outline"
          style={styles.feedbackButton}
          leftIcon={<Ionicons name="chatbubble" size={16} color={colors.primary} />}
        />
      </View>
    </Card>
  ), []);

  const renderQuickActions = useMemo(() => useMemo(() => useMemo(() => (
    <Card style={styles.sectionCard}>
      <Text style={styles.sectionTitle}>快速操作</Text>
      
      <View style={styles.quickActions}>
        <TouchableOpacity
          style={styles.quickAction}
          onPress={() => Alert.alert('功能开发中', '数据导出功能即将上线')}
        >
          <Ionicons name="download" size={24} color={colors.primary} />
          <Text style={styles.quickActionText}>导出数据</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.quickAction}
          onPress={() => Alert.alert('功能开发中', '备份恢复功能即将上线')}
        >
          <Ionicons name="cloud-upload" size={24} color={colors.primary} />
          <Text style={styles.quickActionText}>备份设置</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.quickAction}
          onPress={() => Linking.openURL('https://suoke.life/help')}
        >
          <Ionicons name="help-circle" size={24} color={colors.primary} />
          <Text style={styles.quickActionText}>帮助中心</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.quickAction}
          onPress={() => Alert.alert('重置设置', '确定要重置所有设置吗？', [
            { text: '取消', style: 'cancel' },
            { text: '确定', onPress: () => {
              setAccessibilitySettings({
                screenReader: false,
                highContrast: false,
                largeText: false,
                reduceMotion: false,
                voiceOver: false,
                hapticFeedback: true,
              }), []), []);
              setPersonalizationSettings({
                theme: 'auto',
                language: 'zh',
                fontSize: 16,
                animationSpeed: 1,
                notificationPreferences: {
                  health: true,
                  agents: true,
                  system: true,
                },
              });
            }},
          ])}
        >
          <Ionicons name="refresh" size={24} color={colors.error} />
          <Text style={styles.quickActionText}>重置设置</Text>
        </TouchableOpacity>
      </View>
    </Card>
  ), []);

  return (
    <SafeAreaView style={styles.container}>
      {/* 头部 */}
      <View style={styles.header}>
        <Text style={styles.title}>用户体验优化</Text>
        <Text style={styles.subtitle}>个性化定制您的使用体验</Text>
      </View>

      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        <Animated.View
          style={{
            opacity: animatedValue,
            transform: [
              {
                translateY: animatedValue.interpolate({
                  inputRange: [0, 1],
                  outputRange: [50, 0],
                }),
              },
            ],
          }}
        >
          {/* 无障碍设置 */}
          {renderAccessibilitySettings}

          {/* 个性化设置 */}
          {renderPersonalizationSettings}

          {/* 性能监控 */}
          {renderPerformanceMonitor}

          {/* 用户反馈 */}
          {renderFeedbackSection}

          {/* 快速操作 */}
          {renderQuickActions}
        </Animated.View>
      </ScrollView>

      {/* 反馈模态框 */}
      <Modal
        visible={feedbackModal}
        onClose={() => setFeedbackModal(false)}
      >
        <View style={styles.feedbackForm}>
          <Text style={styles.formLabel}>提交反馈</Text>
          <View style={styles.typeSelector}>
            {(['bug', 'feature', 'improvement', 'general'] as const).map((type) => (
              <TouchableOpacity
                key={type}
                style={[
                  styles.typeButton,
                  feedbackType === type && styles.activeTypeButton,
                ]}
                onPress={() => setFeedbackType(type)}
              >
                <Text style={[
                  styles.typeText,
                  feedbackType === type && styles.activeTypeText,
                ]}>
                  {type === 'bug' ? '问题报告' :
                   type === 'feature' ? '功能建议' :
                   type === 'improvement' ? '改进建议' : '一般反馈'}
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          <Text style={styles.formLabel}>评分</Text>
          <View style={styles.ratingContainer}>
            {[1, 2, 3, 4, 5].map((rating) => (
              <TouchableOpacity
                key={rating}
                onPress={() => setFeedbackRating(rating)}
              >
                <Ionicons
                  name={rating <= feedbackRating ? 'star' : 'star-outline'}
                  size={32}
                  color={rating <= feedbackRating ? colors.warning : colors.gray400}
                />
              </TouchableOpacity>
            ))}
          </View>

          <Text style={styles.formLabel}>详细描述</Text>
          <View style={styles.textInputContainer}>
            <Text style={styles.textInput}
              onPress={() => Alert.alert('输入', '请输入您的反馈内容')}
            >
              {feedbackMessage || '请输入您的反馈内容...'}
            </Text>
          </View>

          <View style={styles.formActions}>
            <Button
              title="取消"
              onPress={() => setFeedbackModal(false)}
              variant="outline"
              style={styles.formButton}
            />
            <Button
              title="提交"
              onPress={submitFeedback}
              style={styles.formButton}
            />
          </View>
        </View>
      </Modal>
    </SafeAreaView>
  );
};

const styles = useMemo(() => useMemo(() => StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    backgroundColor: colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  title: {
    fontSize: typography.fontSize['2xl'],
    fontWeight: '700',
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  subtitle: {
    fontSize: typography.fontSize.base,
    color: colors.textSecondary,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    padding: spacing.lg,
  },
  sectionCard: {
    marginBottom: spacing.lg,
  },
  sectionTitle: {
    fontSize: typography.fontSize.lg,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  sectionDescription: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    marginBottom: spacing.md,
  },
  settingsList: {
    // 设置列表样式
  },
  settingItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  settingInfo: {
    flex: 1,
    marginRight: spacing.md,
  },
  settingLabel: {
    fontSize: typography.fontSize.base,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  settingDescription: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
  },
  themeSelector: {
    flexDirection: 'row',
  },
  themeButton: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    marginHorizontal: spacing.xs,
    borderRadius: 20,
    backgroundColor: colors.gray100,
  },
  activeThemeButton: {
    backgroundColor: colors.primary,
  },
  themeText: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
  },
  activeThemeText: {
    color: colors.white,
  },
  sliderContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    width: 120,
  },
  slider: {
    flex: 1,
    marginRight: spacing.sm,
  },
  sliderValue: {
    fontSize: typography.fontSize.sm,
    color: colors.textPrimary,
    minWidth: 40,
    textAlign: 'right',
  },
  metricsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  metricItem: {
    width: '48%',
    backgroundColor: colors.surface,
    padding: spacing.md,
    borderRadius: 12,
    marginBottom: spacing.sm,
    alignItems: 'center',
    position: 'relative',
  },
  metricLabel: {
    fontSize: typography.fontSize.xs,
    color: colors.textSecondary,
    marginTop: spacing.xs,
    marginBottom: spacing.xs,
  },
  metricValue: {
    fontSize: typography.fontSize.lg,
    fontWeight: '700',
    color: colors.textPrimary,
  },
  metricStatus: {
    position: 'absolute',
    top: spacing.sm,
    right: spacing.sm,
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  feedbackButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  feedbackButton: {
    flex: 1,
    marginHorizontal: spacing.xs,
  },
  quickActions: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  quickAction: {
    width: '48%',
    alignItems: 'center',
    padding: spacing.md,
    backgroundColor: colors.surface,
    borderRadius: 12,
    marginBottom: spacing.sm,
  },
  quickActionText: {
    fontSize: typography.fontSize.sm,
    color: colors.textPrimary,
    marginTop: spacing.xs,
  },
  feedbackForm: {
    padding: spacing.md,
  },
  formLabel: {
    fontSize: typography.fontSize.base,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: spacing.sm,
    marginTop: spacing.md,
  },
  typeSelector: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  typeButton: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    marginRight: spacing.sm,
    marginBottom: spacing.sm,
    borderRadius: 20,
    backgroundColor: colors.gray100,
  },
  activeTypeButton: {
    backgroundColor: colors.primary,
  },
  typeText: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
  },
  activeTypeText: {
    color: colors.white,
  },
  ratingContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginVertical: spacing.md,
  },
  textInputContainer: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 8,
    padding: spacing.md,
    minHeight: 100,
    backgroundColor: colors.surface,
  },
  textInput: {
    fontSize: typography.fontSize.base,
    color: colors.textPrimary,
  },
  formActions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: spacing.lg,
  },
  formButton: {
    flex: 1,
    marginHorizontal: spacing.xs,
  },
}), []), []); 