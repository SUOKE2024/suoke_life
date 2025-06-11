import { Ionicons, MaterialIcons } from '@expo/vector-icons';
import Voice from '@react-native-voice/voice';
import { BlurView } from 'expo-blur';
import * as Haptics from 'expo-haptics';
import { LinearGradient } from 'expo-linear-gradient';
import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import {
    ActivityIndicator,
    Alert,
    Animated,
    Dimensions,
    Modal,
    PanResponder,
    Platform,
    RefreshControl,
    ScrollView,
    StatusBar,
    StyleSheet,
    Text,
    TextInput,
    TouchableOpacity,
    View
} from 'react-native';

const { width: screenWidth, height: screenHeight } = Dimensions.get('window');

interface HealthMetric {
  id: string;
  name: string;
  value: number;
  unit: string;
  trend: 'up' | 'down' | 'stable';
  status: 'excellent' | 'good' | 'warning' | 'critical';
  lastUpdated: Date;
  icon: string;
  color: string;
  target?: number;
  history: number[];
}

interface AIRecommendation {
  id: string;
  title: string;
  description: string;
  category: 'exercise' | 'nutrition' | 'sleep' | 'mental' | 'medical';
  priority: 'high' | 'medium' | 'low';
  confidence: number;
  estimatedBenefit: string;
  timeToComplete: string;
  icon: string;
}

interface VoiceCommand {
  command: string;
  action: () => void;
  description: string;
}

const AdvancedUserInterface: React.FC = () => {
  // 状态管理
  const [healthMetrics, setHealthMetrics] = useState<HealthMetric[]>([]);
  const [recommendations, setRecommendations] = useState<AIRecommendation[]>([]);
  const [isVoiceModalVisible, setIsVoiceModalVisible] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [voiceText, setVoiceText] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedMetric, setSelectedMetric] = useState<HealthMetric | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'overview' | 'metrics' | 'recommendations' | 'insights'>('overview');
  const [notificationCount, setNotificationCount] = useState(3);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [isSettingsVisible, setIsSettingsVisible] = useState(false);
  const [customizationMode, setCustomizationMode] = useState(false);

  // 动画值
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(screenHeight)).current;
  const scaleAnim = useRef(new Animated.Value(1)).current;
  const rotateAnim = useRef(new Animated.Value(0)).current;
  const pulseAnim = useRef(new Animated.Value(1)).current;
  const fabAnim = useRef(new Animated.Value(1)).current;

  // 手势响应器
  const panResponder = useRef(
    PanResponder.create({
      onMoveShouldSetPanResponder: () => true,
      onPanResponderMove: (evt, gestureState) => {
        if (gestureState.dy > 50) {
          // 下拉刷新
          handleRefresh();
        }
      },
    })
  ).current;

  // 语音命令配置
  const voiceCommands: VoiceCommand[] = useMemo(() => [
    {
      command: '显示健康数据',
      action: () => setActiveTab('metrics'),
      description: '切换到健康指标页面'
    },
    {
      command: '查看建议',
      action: () => setActiveTab('recommendations'),
      description: '查看AI个性化建议'
    },
    {
      command: '开始诊断',
      action: () => handleAIDiagnosis(),
      description: '启动AI健康诊断'
    },
    {
      command: '刷新数据',
      action: () => handleRefresh(),
      description: '刷新所有健康数据'
    },
    {
      command: '设置提醒',
      action: () => handleSetReminder(),
      description: '设置健康提醒'
    },
    {
      command: '切换主题',
      action: () => setIsDarkMode(!isDarkMode),
      description: '切换深色/浅色主题'
    },
    {
      command: '打开设置',
      action: () => setIsSettingsVisible(true),
      description: '打开应用设置'
    }
  ], [isDarkMode]);

  // 初始化
  useEffect(() => {
    initializeApp();
    setupVoiceRecognition();
    startAnimations();
    
    return () => {
      Voice.destroy().then(Voice.removeAllListeners);
    };
  }, []);

  // 主题切换效果
  useEffect(() => {
    Animated.timing(fadeAnim, {
      toValue: 1,
      duration: 300,
      useNativeDriver: true,
    }).start();
  }, [isDarkMode]);

  const initializeApp = async () => {
    setIsLoading(true);
    try {
      await Promise.all([
        loadHealthMetrics(),
        loadRecommendations(),
        loadUserPreferences()
      ]);
    } catch (error) {
      console.error('初始化失败:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadHealthMetrics = async () => {
    // 模拟加载健康指标数据
    const mockMetrics: HealthMetric[] = [
      {
        id: '1',
        name: '心率',
        value: 72,
        unit: 'bpm',
        trend: 'stable',
        status: 'good',
        lastUpdated: new Date(),
        icon: 'heart',
        color: '#FF6B6B',
        target: 70,
        history: [70, 72, 71, 73, 72, 71, 72]
      },
      {
        id: '2',
        name: '步数',
        value: 8543,
        unit: '步',
        trend: 'up',
        status: 'excellent',
        lastUpdated: new Date(),
        icon: 'walk',
        color: '#4ECDC4',
        target: 10000,
        history: [7500, 8000, 8200, 8400, 8543]
      },
      {
        id: '3',
        name: '睡眠质量',
        value: 85,
        unit: '%',
        trend: 'up',
        status: 'good',
        lastUpdated: new Date(),
        icon: 'bed',
        color: '#45B7D1',
        target: 90,
        history: [80, 82, 83, 84, 85]
      },
      {
        id: '4',
        name: '血压',
        value: 120,
        unit: 'mmHg',
        trend: 'stable',
        status: 'good',
        lastUpdated: new Date(),
        icon: 'activity',
        color: '#96CEB4',
        target: 120,
        history: [118, 120, 119, 121, 120]
      },
      {
        id: '5',
        name: '体重',
        value: 68.5,
        unit: 'kg',
        trend: 'down',
        status: 'good',
        lastUpdated: new Date(),
        icon: 'trending-down',
        color: '#FFEAA7',
        target: 65,
        history: [70, 69.5, 69, 68.8, 68.5]
      },
      {
        id: '6',
        name: '压力水平',
        value: 35,
        unit: '%',
        trend: 'down',
        status: 'excellent',
        lastUpdated: new Date(),
        icon: 'brain',
        color: '#DDA0DD',
        target: 30,
        history: [45, 42, 40, 38, 35]
      }
    ];
    
    setHealthMetrics(mockMetrics);
  };

  const loadRecommendations = async () => {
    // 模拟加载AI建议数据
    const mockRecommendations: AIRecommendation[] = [
      {
        id: '1',
        title: '增加有氧运动',
        description: '建议每周进行3-4次30分钟的有氧运动，如快走、游泳或骑行',
        category: 'exercise',
        priority: 'high',
        confidence: 92,
        estimatedBenefit: '提升心肺功能15%',
        timeToComplete: '30分钟/次',
        icon: 'fitness'
      },
      {
        id: '2',
        title: '优化睡眠时间',
        description: '建议每晚保持7-8小时的优质睡眠，建立规律的作息时间',
        category: 'sleep',
        priority: 'high',
        confidence: 88,
        estimatedBenefit: '改善睡眠质量20%',
        timeToComplete: '持续执行',
        icon: 'bed-time'
      },
      {
        id: '3',
        title: '补充维生素D',
        description: '根据您的健康数据，建议适量补充维生素D',
        category: 'nutrition',
        priority: 'medium',
        confidence: 85,
        estimatedBenefit: '增强免疫力',
        timeToComplete: '每日一次',
        icon: 'local-pharmacy'
      },
      {
        id: '4',
        title: '冥想练习',
        description: '每日10分钟的正念冥想可以有效降低压力水平',
        category: 'mental',
        priority: 'medium',
        confidence: 90,
        estimatedBenefit: '减少压力25%',
        timeToComplete: '10分钟/天',
        icon: 'self-improvement'
      }
    ];
    
    setRecommendations(mockRecommendations);
  };

  const loadUserPreferences = async () => {
    // 加载用户偏好设置
    // 这里可以从本地存储或服务器加载用户设置
  };

  const setupVoiceRecognition = () => {
    Voice.onSpeechStart = () => setIsListening(true);
    Voice.onSpeechEnd = () => setIsListening(false);
    Voice.onSpeechResults = (e) => {
      if (e.value && e.value[0]) {
        setVoiceText(e.value[0]);
        processVoiceCommand(e.value[0]);
      }
    };
    Voice.onSpeechError = (e) => {
      console.error('语音识别错误:', e);
      setIsListening(false);
    };
  };

  const startAnimations = () => {
    // 启动各种动画
    Animated.timing(fadeAnim, {
      toValue: 1,
      duration: 1000,
      useNativeDriver: true,
    }).start();

    // 脉冲动画
    Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnim, {
          toValue: 1.1,
          duration: 1000,
          useNativeDriver: true,
        }),
        Animated.timing(pulseAnim, {
          toValue: 1,
          duration: 1000,
          useNativeDriver: true,
        }),
      ])
    ).start();

    // 旋转动画
    Animated.loop(
      Animated.timing(rotateAnim, {
        toValue: 1,
        duration: 10000,
        useNativeDriver: true,
      })
    ).start();
  };

  const processVoiceCommand = (command: string) => {
    const matchedCommand = voiceCommands.find(vc => 
      command.toLowerCase().includes(vc.command.toLowerCase())
    );
    
    if (matchedCommand) {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
      matchedCommand.action();
      setIsVoiceModalVisible(false);
    } else {
      Alert.alert('未识别的命令', `无法识别命令: "${command}"`);
    }
  };

  const handleVoicePress = async () => {
    try {
      if (isListening) {
        await Voice.stop();
      } else {
        setIsVoiceModalVisible(true);
        setVoiceText('');
        await Voice.start('zh-CN');
      }
    } catch (error) {
      console.error('语音识别启动失败:', error);
    }
  };

  const handleRefresh = useCallback(async () => {
    setIsRefreshing(true);
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    
    try {
      await Promise.all([
        loadHealthMetrics(),
        loadRecommendations()
      ]);
    } catch (error) {
      console.error('刷新失败:', error);
    } finally {
      setIsRefreshing(false);
    }
  }, []);

  const handleAIDiagnosis = () => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy);
    Alert.alert(
      'AI健康诊断',
      '正在启动AI诊断系统...',
      [
        { text: '取消', style: 'cancel' },
        { text: '开始', onPress: () => console.log('开始AI诊断') }
      ]
    );
  };

  const handleSetReminder = () => {
    Alert.alert(
      '设置提醒',
      '请选择提醒类型',
      [
        { text: '运动提醒', onPress: () => console.log('设置运动提醒') },
        { text: '用药提醒', onPress: () => console.log('设置用药提醒') },
        { text: '睡眠提醒', onPress: () => console.log('设置睡眠提醒') },
        { text: '取消', style: 'cancel' }
      ]
    );
  };

  const handleMetricPress = (metric: HealthMetric) => {
    setSelectedMetric(metric);
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    
    Animated.sequence([
      Animated.timing(scaleAnim, {
        toValue: 0.95,
        duration: 100,
        useNativeDriver: true,
      }),
      Animated.timing(scaleAnim, {
        toValue: 1,
        duration: 100,
        useNativeDriver: true,
      }),
    ]).start();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'excellent': return '#4CAF50';
      case 'good': return '#8BC34A';
      case 'warning': return '#FF9800';
      case 'critical': return '#F44336';
      default: return '#9E9E9E';
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up': return 'trending-up';
      case 'down': return 'trending-down';
      case 'stable': return 'trending-flat';
      default: return 'trending-flat';
    }
  };

  const filteredMetrics = useMemo(() => {
    if (!searchQuery) return healthMetrics;
    return healthMetrics.filter(metric =>
      metric.name.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [healthMetrics, searchQuery]);

  const filteredRecommendations = useMemo(() => {
    if (!searchQuery) return recommendations;
    return recommendations.filter(rec =>
      rec.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      rec.description.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [recommendations, searchQuery]);

  const renderHealthMetric = (metric: HealthMetric) => (
    <TouchableOpacity
      key={metric.id}
      style={[styles.metricCard, { backgroundColor: isDarkMode ? '#2C2C2C' : '#FFFFFF' }]}
      onPress={() => handleMetricPress(metric)}
      activeOpacity={0.8}
    >
      <LinearGradient
        colors={[metric.color + '20', metric.color + '10']}
        style={styles.metricGradient}
      >
        <View style={styles.metricHeader}>
          <View style={styles.metricIconContainer}>
            <Ionicons name={metric.icon as any} size={24} color={metric.color} />
          </View>
          <View style={styles.metricInfo}>
            <Text style={[styles.metricName, { color: isDarkMode ? '#FFFFFF' : '#333333' }]}>
              {metric.name}
            </Text>
            <Text style={[styles.metricValue, { color: metric.color }]}>
              {metric.value} {metric.unit}
            </Text>
          </View>
          <View style={styles.metricStatus}>
            <View style={[styles.statusIndicator, { backgroundColor: getStatusColor(metric.status) }]} />
            <Ionicons 
              name={getTrendIcon(metric.trend) as any} 
              size={16} 
              color={getStatusColor(metric.status)} 
            />
          </View>
        </View>
        
        {metric.target && (
          <View style={styles.progressContainer}>
            <View style={styles.progressBar}>
              <View 
                style={[
                  styles.progressFill, 
                  { 
                    width: `${Math.min((metric.value / metric.target) * 100, 100)}%`,
                    backgroundColor: metric.color 
                  }
                ]} 
              />
            </View>
            <Text style={[styles.progressText, { color: isDarkMode ? '#CCCCCC' : '#666666' }]}>
              目标: {metric.target} {metric.unit}
            </Text>
          </View>
        )}
      </LinearGradient>
    </TouchableOpacity>
  );

  const renderRecommendation = (recommendation: AIRecommendation) => (
    <TouchableOpacity
      key={recommendation.id}
      style={[styles.recommendationCard, { backgroundColor: isDarkMode ? '#2C2C2C' : '#FFFFFF' }]}
      activeOpacity={0.8}
    >
      <View style={styles.recommendationHeader}>
        <MaterialIcons name={recommendation.icon as any} size={24} color="#4CAF50" />
        <View style={styles.recommendationInfo}>
          <Text style={[styles.recommendationTitle, { color: isDarkMode ? '#FFFFFF' : '#333333' }]}>
            {recommendation.title}
          </Text>
          <View style={styles.recommendationMeta}>
            <View style={[styles.priorityBadge, { 
              backgroundColor: recommendation.priority === 'high' ? '#FF5722' : 
                             recommendation.priority === 'medium' ? '#FF9800' : '#4CAF50' 
            }]}>
              <Text style={styles.priorityText}>{recommendation.priority}</Text>
            </View>
            <Text style={[styles.confidenceText, { color: isDarkMode ? '#CCCCCC' : '#666666' }]}>
              置信度: {recommendation.confidence}%
            </Text>
          </View>
        </View>
      </View>
      
      <Text style={[styles.recommendationDescription, { color: isDarkMode ? '#CCCCCC' : '#666666' }]}>
        {recommendation.description}
      </Text>
      
      <View style={styles.recommendationFooter}>
        <Text style={[styles.benefitText, { color: '#4CAF50' }]}>
          预期效果: {recommendation.estimatedBenefit}
        </Text>
        <Text style={[styles.timeText, { color: isDarkMode ? '#CCCCCC' : '#666666' }]}>
          {recommendation.timeToComplete}
        </Text>
      </View>
    </TouchableOpacity>
  );

  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return (
          <View style={styles.overviewContainer}>
            <Text style={[styles.sectionTitle, { color: isDarkMode ? '#FFFFFF' : '#333333' }]}>
              今日概览
            </Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.metricsScroll}>
              {healthMetrics.slice(0, 4).map(renderHealthMetric)}
            </ScrollView>
            
            <Text style={[styles.sectionTitle, { color: isDarkMode ? '#FFFFFF' : '#333333' }]}>
              重要建议
            </Text>
            {recommendations.slice(0, 2).map(renderRecommendation)}
          </View>
        );
        
      case 'metrics':
        return (
          <View style={styles.metricsContainer}>
            {filteredMetrics.map(renderHealthMetric)}
          </View>
        );
        
      case 'recommendations':
        return (
          <View style={styles.recommendationsContainer}>
            {filteredRecommendations.map(renderRecommendation)}
          </View>
        );
        
      case 'insights':
        return (
          <View style={styles.insightsContainer}>
            <Text style={[styles.sectionTitle, { color: isDarkMode ? '#FFFFFF' : '#333333' }]}>
              健康洞察
            </Text>
            <View style={[styles.insightCard, { backgroundColor: isDarkMode ? '#2C2C2C' : '#FFFFFF' }]}>
              <Text style={[styles.insightTitle, { color: isDarkMode ? '#FFFFFF' : '#333333' }]}>
                本周健康趋势
              </Text>
              <Text style={[styles.insightText, { color: isDarkMode ? '#CCCCCC' : '#666666' }]}>
                您的整体健康状况呈上升趋势，心率稳定，睡眠质量有所改善。建议继续保持当前的运动习惯。
              </Text>
            </View>
          </View>
        );
        
      default:
        return null;
    }
  };

  if (isLoading) {
    return (
      <View style={[styles.loadingContainer, { backgroundColor: isDarkMode ? '#1A1A1A' : '#F5F5F5' }]}>
        <ActivityIndicator size="large" color="#4CAF50" />
        <Text style={[styles.loadingText, { color: isDarkMode ? '#FFFFFF' : '#333333' }]}>
          正在加载健康数据...
        </Text>
      </View>
    );
  }

  return (
    <View style={[styles.container, { backgroundColor: isDarkMode ? '#1A1A1A' : '#F5F5F5' }]}>
      <StatusBar 
        barStyle={isDarkMode ? 'light-content' : 'dark-content'} 
        backgroundColor={isDarkMode ? '#1A1A1A' : '#F5F5F5'} 
      />
      
      {/* 头部 */}
      <LinearGradient
        colors={isDarkMode ? ['#2C2C2C', '#1A1A1A'] : ['#FFFFFF', '#F5F5F5']}
        style={styles.header}
      >
        <View style={styles.headerContent}>
          <View style={styles.headerLeft}>
            <Text style={[styles.headerTitle, { color: isDarkMode ? '#FFFFFF' : '#333333' }]}>
              索克生活
            </Text>
            <Text style={[styles.headerSubtitle, { color: isDarkMode ? '#CCCCCC' : '#666666' }]}>
              智能健康管理
            </Text>
          </View>
          
          <View style={styles.headerRight}>
            <TouchableOpacity 
              style={styles.headerButton}
              onPress={() => setIsDarkMode(!isDarkMode)}
            >
              <Ionicons 
                name={isDarkMode ? 'sunny' : 'moon'} 
                size={24} 
                color={isDarkMode ? '#FFFFFF' : '#333333'} 
              />
            </TouchableOpacity>
            
            <TouchableOpacity 
              style={styles.headerButton}
              onPress={() => setIsSettingsVisible(true)}
            >
              <Ionicons 
                name="notifications" 
                size={24} 
                color={isDarkMode ? '#FFFFFF' : '#333333'} 
              />
              {notificationCount > 0 && (
                <View style={styles.notificationBadge}>
                  <Text style={styles.notificationText}>{notificationCount}</Text>
                </View>
              )}
            </TouchableOpacity>
          </View>
        </View>
        
        {/* 搜索栏 */}
        <View style={[styles.searchContainer, { backgroundColor: isDarkMode ? '#3C3C3C' : '#FFFFFF' }]}>
          <Ionicons name="search" size={20} color={isDarkMode ? '#CCCCCC' : '#666666'} />
          <TextInput
            style={[styles.searchInput, { color: isDarkMode ? '#FFFFFF' : '#333333' }]}
            placeholder="搜索健康数据或建议..."
            placeholderTextColor={isDarkMode ? '#CCCCCC' : '#666666'}
            value={searchQuery}
            onChangeText={setSearchQuery}
          />
          {searchQuery.length > 0 && (
            <TouchableOpacity onPress={() => setSearchQuery('')}>
              <Ionicons name="close" size={20} color={isDarkMode ? '#CCCCCC' : '#666666'} />
            </TouchableOpacity>
          )}
        </View>
      </LinearGradient>

      {/* 标签栏 */}
      <View style={[styles.tabBar, { backgroundColor: isDarkMode ? '#2C2C2C' : '#FFFFFF' }]}>
        {[
          { key: 'overview', label: '概览', icon: 'home' },
          { key: 'metrics', label: '指标', icon: 'analytics' },
          { key: 'recommendations', label: '建议', icon: 'bulb' },
          { key: 'insights', label: '洞察', icon: 'trending-up' }
        ].map((tab) => (
          <TouchableOpacity
            key={tab.key}
            style={[
              styles.tabItem,
              activeTab === tab.key && styles.activeTabItem
            ]}
            onPress={() => setActiveTab(tab.key as any)}
          >
            <Ionicons 
              name={tab.icon as any} 
              size={20} 
              color={activeTab === tab.key ? '#4CAF50' : (isDarkMode ? '#CCCCCC' : '#666666')} 
            />
            <Text style={[
              styles.tabLabel,
              { color: activeTab === tab.key ? '#4CAF50' : (isDarkMode ? '#CCCCCC' : '#666666') }
            ]}>
              {tab.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* 主要内容 */}
      <Animated.View style={[styles.content, { opacity: fadeAnim }]} {...panResponder.panHandlers}>
        <ScrollView
          style={styles.scrollView}
          refreshControl={
            <RefreshControl
              refreshing={isRefreshing}
              onRefresh={handleRefresh}
              colors={['#4CAF50']}
              tintColor="#4CAF50"
            />
          }
          showsVerticalScrollIndicator={false}
        >
          {renderTabContent()}
        </ScrollView>
      </Animated.View>

      {/* 浮动操作按钮 */}
      <Animated.View style={[styles.fabContainer, { transform: [{ scale: fabAnim }] }]}>
        <TouchableOpacity
          style={[styles.fab, { backgroundColor: '#4CAF50' }]}
          onPress={handleVoicePress}
          onLongPress={() => setCustomizationMode(!customizationMode)}
        >
          <Animated.View style={{ transform: [{ scale: pulseAnim }] }}>
            <Ionicons name="mic" size={24} color="#FFFFFF" />
          </Animated.View>
        </TouchableOpacity>
      </Animated.View>

      {/* 语音助手模态框 */}
      <Modal
        visible={isVoiceModalVisible}
        transparent={true}
        animationType="fade"
        onRequestClose={() => setIsVoiceModalVisible(false)}
      >
        <BlurView intensity={80} style={styles.modalOverlay}>
          <Animated.View style={[styles.voiceModal, { transform: [{ scale: scaleAnim }] }]}>
            <View style={styles.voiceHeader}>
              <Text style={styles.voiceTitle}>语音助手</Text>
              <TouchableOpacity onPress={() => setIsVoiceModalVisible(false)}>
                <Ionicons name="close" size={24} color="#333333" />
              </TouchableOpacity>
            </View>
            
            <View style={styles.voiceContent}>
              <Animated.View style={[
                styles.voiceIndicator,
                { transform: [{ scale: isListening ? pulseAnim : new Animated.Value(1) }] }
              ]}>
                <Ionicons 
                  name={isListening ? "mic" : "mic-off"} 
                  size={48} 
                  color={isListening ? "#4CAF50" : "#666666"} 
                />
              </Animated.View>
              
              <Text style={styles.voiceStatus}>
                {isListening ? '正在聆听...' : '点击开始语音识别'}
              </Text>
              
              {voiceText && (
                <Text style={styles.voiceText}>识别结果: {voiceText}</Text>
              )}
              
              <View style={styles.commandsList}>
                <Text style={styles.commandsTitle}>可用命令:</Text>
                {voiceCommands.slice(0, 4).map((cmd, index) => (
                  <Text key={index} style={styles.commandItem}>
                    • {cmd.command}
                  </Text>
                ))}
              </View>
            </View>
          </Animated.View>
        </BlurView>
      </Modal>

      {/* 设置模态框 */}
      <Modal
        visible={isSettingsVisible}
        transparent={true}
        animationType="slide"
        onRequestClose={() => setIsSettingsVisible(false)}
      >
        <View style={styles.settingsOverlay}>
          <View style={[styles.settingsModal, { backgroundColor: isDarkMode ? '#2C2C2C' : '#FFFFFF' }]}>
            <View style={styles.settingsHeader}>
              <Text style={[styles.settingsTitle, { color: isDarkMode ? '#FFFFFF' : '#333333' }]}>
                设置
              </Text>
              <TouchableOpacity onPress={() => setIsSettingsVisible(false)}>
                <Ionicons name="close" size={24} color={isDarkMode ? '#FFFFFF' : '#333333'} />
              </TouchableOpacity>
            </View>
            
            <ScrollView style={styles.settingsContent}>
              <TouchableOpacity style={styles.settingItem}>
                <Text style={[styles.settingLabel, { color: isDarkMode ? '#FFFFFF' : '#333333' }]}>
                  通知设置
                </Text>
                <Ionicons name="chevron-forward" size={20} color={isDarkMode ? '#CCCCCC' : '#666666'} />
              </TouchableOpacity>
              
              <TouchableOpacity style={styles.settingItem}>
                <Text style={[styles.settingLabel, { color: isDarkMode ? '#FFFFFF' : '#333333' }]}>
                  数据同步
                </Text>
                <Ionicons name="chevron-forward" size={20} color={isDarkMode ? '#CCCCCC' : '#666666'} />
              </TouchableOpacity>
              
              <TouchableOpacity style={styles.settingItem}>
                <Text style={[styles.settingLabel, { color: isDarkMode ? '#FFFFFF' : '#333333' }]}>
                  隐私设置
                </Text>
                <Ionicons name="chevron-forward" size={20} color={isDarkMode ? '#CCCCCC' : '#666666'} />
              </TouchableOpacity>
              
              <TouchableOpacity style={styles.settingItem}>
                <Text style={[styles.settingLabel, { color: isDarkMode ? '#FFFFFF' : '#333333' }]}>
                  关于应用
                </Text>
                <Ionicons name="chevron-forward" size={20} color={isDarkMode ? '#CCCCCC' : '#666666'} />
              </TouchableOpacity>
            </ScrollView>
          </View>
        </View>
      </Modal>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
  },
  header: {
    paddingTop: Platform.OS === 'ios' ? 50 : 30,
    paddingBottom: 16,
    paddingHorizontal: 20,
  },
  headerContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  headerLeft: {
    flex: 1,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  headerSubtitle: {
    fontSize: 14,
    marginTop: 2,
  },
  headerRight: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  headerButton: {
    marginLeft: 16,
    position: 'relative',
  },
  notificationBadge: {
    position: 'absolute',
    top: -8,
    right: -8,
    backgroundColor: '#FF5722',
    borderRadius: 10,
    minWidth: 20,
    height: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  notificationText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: 'bold',
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 12,
    marginHorizontal: 4,
  },
  searchInput: {
    flex: 1,
    marginLeft: 12,
    fontSize: 16,
  },
  tabBar: {
    flexDirection: 'row',
    paddingVertical: 8,
    elevation: 2,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  tabItem: {
    flex: 1,
    alignItems: 'center',
    paddingVertical: 8,
  },
  activeTabItem: {
    borderBottomWidth: 2,
    borderBottomColor: '#4CAF50',
  },
  tabLabel: {
    fontSize: 12,
    marginTop: 4,
  },
  content: {
    flex: 1,
  },
  scrollView: {
    flex: 1,
  },
  overviewContainer: {
    padding: 20,
  },
  metricsContainer: {
    padding: 20,
  },
  recommendationsContainer: {
    padding: 20,
  },
  insightsContainer: {
    padding: 20,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  metricsScroll: {
    marginBottom: 24,
  },
  metricCard: {
    marginRight: 16,
    marginBottom: 16,
    borderRadius: 16,
    overflow: 'hidden',
    elevation: 3,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    width: screenWidth * 0.8,
  },
  metricGradient: {
    padding: 16,
  },
  metricHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  metricIconContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  metricInfo: {
    flex: 1,
  },
  metricName: {
    fontSize: 16,
    fontWeight: '600',
  },
  metricValue: {
    fontSize: 24,
    fontWeight: 'bold',
    marginTop: 4,
  },
  metricStatus: {
    alignItems: 'center',
  },
  statusIndicator: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginBottom: 4,
  },
  progressContainer: {
    marginTop: 8,
  },
  progressBar: {
    height: 6,
    backgroundColor: 'rgba(255, 255, 255, 0.3)',
    borderRadius: 3,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    borderRadius: 3,
  },
  progressText: {
    fontSize: 12,
    marginTop: 4,
  },
  recommendationCard: {
    padding: 16,
    marginBottom: 16,
    borderRadius: 16,
    elevation: 3,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  recommendationHeader: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  recommendationInfo: {
    flex: 1,
    marginLeft: 12,
  },
  recommendationTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 4,
  },
  recommendationMeta: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  priorityBadge: {
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 12,
    marginRight: 8,
  },
  priorityText: {
    color: '#FFFFFF',
    fontSize: 10,
    fontWeight: 'bold',
    textTransform: 'uppercase',
  },
  confidenceText: {
    fontSize: 12,
  },
  recommendationDescription: {
    fontSize: 14,
    lineHeight: 20,
    marginBottom: 12,
  },
  recommendationFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  benefitText: {
    fontSize: 12,
    fontWeight: '600',
  },
  timeText: {
    fontSize: 12,
  },
  insightCard: {
    padding: 16,
    borderRadius: 16,
    elevation: 3,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  insightTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8,
  },
  insightText: {
    fontSize: 14,
    lineHeight: 20,
  },
  fabContainer: {
    position: 'absolute',
    bottom: 30,
    right: 30,
  },
  fab: {
    width: 56,
    height: 56,
    borderRadius: 28,
    justifyContent: 'center',
    alignItems: 'center',
    elevation: 8,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
  },
  modalOverlay: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  voiceModal: {
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    padding: 24,
    margin: 20,
    maxWidth: screenWidth * 0.9,
    elevation: 10,
    shadowOffset: { width: 0, height: 5 },
    shadowOpacity: 0.3,
    shadowRadius: 10,
  },
  voiceHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  voiceTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333333',
  },
  voiceContent: {
    alignItems: 'center',
  },
  voiceIndicator: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#F5F5F5',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  voiceStatus: {
    fontSize: 16,
    color: '#666666',
    marginBottom: 16,
  },
  voiceText: {
    fontSize: 14,
    color: '#333333',
    textAlign: 'center',
    marginBottom: 20,
  },
  commandsList: {
    width: '100%',
  },
  commandsTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333333',
    marginBottom: 8,
  },
  commandItem: {
    fontSize: 12,
    color: '#666666',
    marginBottom: 4,
  },
  settingsOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'flex-end',
  },
  settingsModal: {
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    maxHeight: screenHeight * 0.8,
  },
  settingsHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  settingsTitle: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  settingsContent: {
    padding: 20,
  },
  settingItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  settingLabel: {
    fontSize: 16,
  },
});

export default AdvancedUserInterface; 