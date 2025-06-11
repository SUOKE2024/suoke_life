/**
 * 增强用户界面组件
 * 优化移动端体验
 * 增加语音交互
 * 提升响应速度
 */

import { BlurView } from '@react-native-blur/blur';
import Voice from '@react-native-voice/voice';
import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
    ActivityIndicator,
    Alert,
    Animated,
    Dimensions,
    FlatList,
    Modal,
    ScrollView,
    StyleSheet,
    Text,
    TextInput,
    TouchableOpacity,
    View
} from 'react-native';
import LinearGradient from 'react-native-linear-gradient';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialIcons';

const { width: screenWidth, height: screenHeight } = Dimensions.get('window');

interface HealthMetric {
  id: string;
  name: string;
  value: string | number;
  unit: string;
  trend: 'up' | 'down' | 'stable';
  status: 'good' | 'warning' | 'danger';
  icon: string;
}

interface VoiceCommand {
  command: string;
  action: () => void;
  description: string;
}

interface EnhancedUIProps {
  healthData: HealthMetric[];
  onRefresh: () => Promise<void>;
  onNavigate: (screen: string) => void;
  isLoading?: boolean;
}

const EnhancedUserInterface: React.FC<EnhancedUIProps> = ({
  healthData,
  onRefresh,
  onNavigate,
  isLoading = false,
}) => {
  const insets = useSafeAreaInsets();
  
  // 动画值
  const fadeAnim = useMemo(() => new Animated.Value(0), []);
  const slideAnim = useMemo(() => new Animated.Value(50), []);
  const scaleAnim = useMemo(() => new Animated.Value(0.9), []);
  
  // 状态管理
  const [isVoiceActive, setIsVoiceActive] = useState(false);
  const [voiceText, setVoiceText] = useState('');
  const [showVoiceModal, setShowVoiceModal] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredData, setFilteredData] = useState(healthData);
  
  // 语音命令配置
  const voiceCommands: VoiceCommand[] = useMemo(() => [
    {
      command: '查看健康数据',
      action: () => onNavigate('health-dashboard'),
      description: '显示健康仪表板'
    },
    {
      command: '开始诊断',
      action: () => onNavigate('diagnosis'),
      description: '启动AI诊断'
    },
    {
      command: '查看建议',
      action: () => onNavigate('recommendations'),
      description: '显示个性化建议'
    },
    {
      command: '刷新数据',
      action: handleRefresh,
      description: '刷新健康数据'
    },
    {
      command: '设置提醒',
      action: () => onNavigate('reminders'),
      description: '设置健康提醒'
    }
  ], [onNavigate]);

  // 初始化动画
  useEffect(() => {
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 800,
        useNativeDriver: true,
      }),
      Animated.timing(slideAnim, {
        toValue: 0,
        duration: 600,
        useNativeDriver: true,
      }),
      Animated.timing(scaleAnim, {
        toValue: 1,
        duration: 500,
        useNativeDriver: true,
      }),
    ]).start();
  }, [fadeAnim, slideAnim, scaleAnim]);

  // 语音识别初始化
  useEffect(() => {
    Voice.onSpeechStart = onSpeechStart;
    Voice.onSpeechEnd = onSpeechEnd;
    Voice.onSpeechResults = onSpeechResults;
    Voice.onSpeechError = onSpeechError;

    return () => {
      Voice.destroy().then(Voice.removeAllListeners);
    };
  }, []);

  // 数据过滤
  useEffect(() => {
    if (searchQuery.trim() === '') {
      setFilteredData(healthData);
    } else {
      const filtered = healthData.filter(item =>
        item.name.toLowerCase().includes(searchQuery.toLowerCase())
      );
      setFilteredData(filtered);
    }
  }, [searchQuery, healthData]);

  // 语音识别回调
  const onSpeechStart = useCallback(() => {
    setIsVoiceActive(true);
  }, []);

  const onSpeechEnd = useCallback(() => {
    setIsVoiceActive(false);
  }, []);

  const onSpeechResults = useCallback((event: any) => {
    const result = event.value[0];
    setVoiceText(result);
    processVoiceCommand(result);
  }, [voiceCommands]);

  const onSpeechError = useCallback((event: any) => {
    console.error('语音识别错误:', event.error);
    setIsVoiceActive(false);
    Alert.alert('语音识别失败', '请重试或检查麦克风权限');
  }, []);

  // 处理语音命令
  const processVoiceCommand = useCallback((command: string) => {
    const matchedCommand = voiceCommands.find(cmd =>
      command.toLowerCase().includes(cmd.command.toLowerCase())
    );

    if (matchedCommand) {
      matchedCommand.action();
      setShowVoiceModal(false);
      Alert.alert('命令执行', `正在执行: ${matchedCommand.description}`);
    } else {
      Alert.alert('未识别命令', '请尝试说出支持的语音命令');
    }
  }, [voiceCommands]);

  // 开始语音识别
  const startVoiceRecognition = useCallback(async () => {
    try {
      setShowVoiceModal(true);
      setVoiceText('');
      await Voice.start('zh-CN');
    } catch (error) {
      console.error('启动语音识别失败:', error);
      Alert.alert('语音识别启动失败', '请检查麦克风权限');
    }
  }, []);

  // 停止语音识别
  const stopVoiceRecognition = useCallback(async () => {
    try {
      await Voice.stop();
      setShowVoiceModal(false);
    } catch (error) {
      console.error('停止语音识别失败:', error);
    }
  }, []);

  // 刷新数据
  async function handleRefresh() {
    setRefreshing(true);
    try {
      await onRefresh();
    } catch (error) {
      Alert.alert('刷新失败', '请检查网络连接');
    } finally {
      setRefreshing(false);
    }
  }

  // 获取状态颜色
  const getStatusColor = useCallback((status: string) => {
    switch (status) {
      case 'good': return '#4CAF50';
      case 'warning': return '#FF9800';
      case 'danger': return '#F44336';
      default: return '#9E9E9E';
    }
  }, []);

  // 获取趋势图标
  const getTrendIcon = useCallback((trend: string) => {
    switch (trend) {
      case 'up': return 'trending-up';
      case 'down': return 'trending-down';
      case 'stable': return 'trending-flat';
      default: return 'help';
    }
  }, []);

  // 渲染健康指标卡片
  const renderHealthMetric = useCallback(({ item, index }: { item: HealthMetric; index: number }) => {
    const animatedStyle = {
      opacity: fadeAnim,
      transform: [
        {
          translateY: slideAnim.interpolate({
            inputRange: [0, 50],
            outputRange: [0, 50],
          }),
        },
        { scale: scaleAnim },
      ],
    };

    return (
      <Animated.View style={[styles.metricCard, animatedStyle, { marginTop: index * 2 }]}>
        <LinearGradient
          colors={['#FFFFFF', '#F8F9FA']}
          style={styles.cardGradient}
        >
          <View style={styles.cardHeader}>
            <View style={styles.iconContainer}>
              <Icon
                name={item.icon}
                size={24}
                color={getStatusColor(item.status)}
              />
            </View>
            <View style={styles.trendContainer}>
              <Icon
                name={getTrendIcon(item.trend)}
                size={16}
                color={getStatusColor(item.status)}
              />
            </View>
          </View>
          
          <Text style={styles.metricName}>{item.name}</Text>
          
          <View style={styles.valueContainer}>
            <Text style={[styles.metricValue, { color: getStatusColor(item.status) }]}>
              {item.value}
            </Text>
            <Text style={styles.metricUnit}>{item.unit}</Text>
          </View>
          
          <View style={[styles.statusIndicator, { backgroundColor: getStatusColor(item.status) }]} />
        </LinearGradient>
      </Animated.View>
    );
  }, [fadeAnim, slideAnim, scaleAnim, getStatusColor, getTrendIcon]);

  // 渲染语音命令列表
  const renderVoiceCommand = useCallback(({ item }: { item: VoiceCommand }) => (
    <TouchableOpacity
      style={styles.commandItem}
      onPress={item.action}
    >
      <Text style={styles.commandText}>{item.command}</Text>
      <Text style={styles.commandDescription}>{item.description}</Text>
    </TouchableOpacity>
  ), []);

  return (
    <View style={[styles.container, { paddingTop: insets.top }]}>
      {/* 头部区域 */}
      <LinearGradient
        colors={['#667eea', '#764ba2']}
        style={styles.header}
      >
        <View style={styles.headerContent}>
          <Text style={styles.headerTitle}>索克生活</Text>
          <Text style={styles.headerSubtitle}>智能健康管理</Text>
          
          <View style={styles.headerActions}>
            <TouchableOpacity
              style={styles.actionButton}
              onPress={startVoiceRecognition}
            >
              <Icon name="mic" size={24} color="#FFFFFF" />
            </TouchableOpacity>
            
            <TouchableOpacity
              style={styles.actionButton}
              onPress={handleRefresh}
              disabled={refreshing}
            >
              {refreshing ? (
                <ActivityIndicator size="small" color="#FFFFFF" />
              ) : (
                <Icon name="refresh" size={24} color="#FFFFFF" />
              )}
            </TouchableOpacity>
          </View>
        </View>
        
        {/* 搜索框 */}
        <View style={styles.searchContainer}>
          <Icon name="search" size={20} color="#9E9E9E" style={styles.searchIcon} />
          <TextInput
            style={styles.searchInput}
            placeholder="搜索健康指标..."
            placeholderTextColor="#9E9E9E"
            value={searchQuery}
            onChangeText={setSearchQuery}
          />
        </View>
      </LinearGradient>

      {/* 主要内容区域 */}
      <ScrollView
        style={styles.content}
        showsVerticalScrollIndicator={false}
        refreshing={refreshing}
        onRefresh={handleRefresh}
      >
        {isLoading ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color="#667eea" />
            <Text style={styles.loadingText}>正在加载健康数据...</Text>
          </View>
        ) : (
          <FlatList
            data={filteredData}
            renderItem={renderHealthMetric}
            keyExtractor={(item) => item.id}
            numColumns={2}
            columnWrapperStyle={styles.row}
            scrollEnabled={false}
            showsVerticalScrollIndicator={false}
          />
        )}
        
        {/* 快速操作区域 */}
        <View style={styles.quickActions}>
          <Text style={styles.sectionTitle}>快速操作</Text>
          
          <View style={styles.actionGrid}>
            <TouchableOpacity
              style={styles.quickActionButton}
              onPress={() => onNavigate('diagnosis')}
            >
              <LinearGradient
                colors={['#FF6B6B', '#FF8E8E']}
                style={styles.actionGradient}
              >
                <Icon name="healing" size={32} color="#FFFFFF" />
                <Text style={styles.actionText}>AI诊断</Text>
              </LinearGradient>
            </TouchableOpacity>
            
            <TouchableOpacity
              style={styles.quickActionButton}
              onPress={() => onNavigate('recommendations')}
            >
              <LinearGradient
                colors={['#4ECDC4', '#44A08D']}
                style={styles.actionGradient}
              >
                <Icon name="lightbulb-outline" size={32} color="#FFFFFF" />
                <Text style={styles.actionText}>个性化建议</Text>
              </LinearGradient>
            </TouchableOpacity>
            
            <TouchableOpacity
              style={styles.quickActionButton}
              onPress={() => onNavigate('health-plan')}
            >
              <LinearGradient
                colors={['#A8E6CF', '#7FCDCD']}
                style={styles.actionGradient}
              >
                <Icon name="assignment" size={32} color="#FFFFFF" />
                <Text style={styles.actionText}>健康计划</Text>
              </LinearGradient>
            </TouchableOpacity>
            
            <TouchableOpacity
              style={styles.quickActionButton}
              onPress={() => onNavigate('community')}
            >
              <LinearGradient
                colors={['#FFD93D', '#FF6B6B']}
                style={styles.actionGradient}
              >
                <Icon name="people" size={32} color="#FFFFFF" />
                <Text style={styles.actionText}>健康社区</Text>
              </LinearGradient>
            </TouchableOpacity>
          </View>
        </View>
      </ScrollView>

      {/* 语音识别模态框 */}
      <Modal
        visible={showVoiceModal}
        transparent={true}
        animationType="fade"
        onRequestClose={stopVoiceRecognition}
      >
        <BlurView style={styles.modalOverlay} blurType="dark" blurAmount={10}>
          <View style={styles.voiceModal}>
            <LinearGradient
              colors={['#667eea', '#764ba2']}
              style={styles.modalGradient}
            >
              <View style={styles.modalHeader}>
                <Text style={styles.modalTitle}>语音助手</Text>
                <TouchableOpacity
                  style={styles.closeButton}
                  onPress={stopVoiceRecognition}
                >
                  <Icon name="close" size={24} color="#FFFFFF" />
                </TouchableOpacity>
              </View>
              
              <View style={styles.voiceIndicator}>
                <Animated.View
                  style={[
                    styles.voiceCircle,
                    {
                      transform: [
                        {
                          scale: isVoiceActive
                            ? fadeAnim.interpolate({
                                inputRange: [0, 1],
                                outputRange: [1, 1.2],
                              })
                            : 1,
                        },
                      ],
                    },
                  ]}
                >
                  <Icon
                    name={isVoiceActive ? "mic" : "mic-off"}
                    size={48}
                    color="#FFFFFF"
                  />
                </Animated.View>
                
                <Text style={styles.voiceStatus}>
                  {isVoiceActive ? '正在聆听...' : '点击开始语音识别'}
                </Text>
                
                {voiceText ? (
                  <Text style={styles.voiceText}>识别结果: {voiceText}</Text>
                ) : null}
              </View>
              
              <View style={styles.commandsList}>
                <Text style={styles.commandsTitle}>支持的语音命令:</Text>
                <FlatList
                  data={voiceCommands}
                  renderItem={renderVoiceCommand}
                  keyExtractor={(item) => item.command}
                  showsVerticalScrollIndicator={false}
                />
              </View>
            </LinearGradient>
          </View>
        </BlurView>
      </Modal>

      {/* 浮动操作按钮 */}
      <TouchableOpacity
        style={styles.fab}
        onPress={startVoiceRecognition}
      >
        <LinearGradient
          colors={['#667eea', '#764ba2']}
          style={styles.fabGradient}
        >
          <Icon name="mic" size={28} color="#FFFFFF" />
        </LinearGradient>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F7FA',
  },
  header: {
    paddingHorizontal: 20,
    paddingBottom: 20,
    borderBottomLeftRadius: 25,
    borderBottomRightRadius: 25,
  },
  headerContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#E8EAF6',
    marginTop: 4,
  },
  headerActions: {
    flexDirection: 'row',
    gap: 12,
  },
  actionButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    borderRadius: 25,
    paddingHorizontal: 16,
    height: 50,
  },
  searchIcon: {
    marginRight: 12,
  },
  searchInput: {
    flex: 1,
    fontSize: 16,
    color: '#333333',
  },
  content: {
    flex: 1,
    padding: 20,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 60,
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#666666',
  },
  row: {
    justifyContent: 'space-between',
  },
  metricCard: {
    width: (screenWidth - 60) / 2,
    marginBottom: 16,
    borderRadius: 16,
    overflow: 'hidden',
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
  },
  cardGradient: {
    padding: 16,
    minHeight: 140,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  iconContainer: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(102, 126, 234, 0.1)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  trendContainer: {
    padding: 4,
  },
  metricName: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333333',
    marginBottom: 8,
  },
  valueContainer: {
    flexDirection: 'row',
    alignItems: 'baseline',
    marginBottom: 12,
  },
  metricValue: {
    fontSize: 24,
    fontWeight: 'bold',
    marginRight: 4,
  },
  metricUnit: {
    fontSize: 12,
    color: '#666666',
  },
  statusIndicator: {
    position: 'absolute',
    top: 0,
    right: 0,
    width: 4,
    height: '100%',
  },
  quickActions: {
    marginTop: 32,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333333',
    marginBottom: 16,
  },
  actionGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  quickActionButton: {
    width: (screenWidth - 60) / 2,
    marginBottom: 16,
    borderRadius: 16,
    overflow: 'hidden',
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
  },
  actionGradient: {
    padding: 20,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 120,
  },
  actionText: {
    marginTop: 8,
    fontSize: 14,
    fontWeight: '600',
    color: '#FFFFFF',
    textAlign: 'center',
  },
  modalOverlay: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  voiceModal: {
    width: screenWidth * 0.9,
    maxHeight: screenHeight * 0.8,
    borderRadius: 20,
    overflow: 'hidden',
  },
  modalGradient: {
    padding: 24,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 24,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  closeButton: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  voiceIndicator: {
    alignItems: 'center',
    marginBottom: 32,
  },
  voiceCircle: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  voiceStatus: {
    fontSize: 16,
    color: '#FFFFFF',
    textAlign: 'center',
  },
  voiceText: {
    fontSize: 14,
    color: '#E8EAF6',
    textAlign: 'center',
    marginTop: 8,
  },
  commandsList: {
    maxHeight: 200,
  },
  commandsTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFFFFF',
    marginBottom: 12,
  },
  commandItem: {
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255, 255, 255, 0.1)',
  },
  commandText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  commandDescription: {
    fontSize: 12,
    color: '#E8EAF6',
    marginTop: 2,
  },
  fab: {
    position: 'absolute',
    bottom: 30,
    right: 20,
    width: 60,
    height: 60,
    borderRadius: 30,
    elevation: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
  },
  fabGradient: {
    width: '100%',
    height: '100%',
    borderRadius: 30,
    justifyContent: 'center',
    alignItems: 'center',
  },
});

export default EnhancedUserInterface; 