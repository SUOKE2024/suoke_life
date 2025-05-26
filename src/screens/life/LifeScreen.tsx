import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  FlatList,
  Modal,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from '../../components/common/Icon';
import { colors, spacing, fonts } from '../../constants/theme';
import AgentChatInterface, { AgentType } from '../../components/common/AgentChatInterface';
import BlockchainHealthData from './components/BlockchainHealthData';
import ARConstitutionVisualization from './components/ARConstitutionVisualization';

// 生活建议类型
interface LifeSuggestion {
  id: string;
  title: string;
  description: string;
  category: 'diet' | 'exercise' | 'sleep' | 'mental' | 'social' | 'work';
  priority: 'high' | 'medium' | 'low';
  icon: string;
  color: string;
  completed: boolean;
  timeEstimate: string;
}

// 健康指标类型
interface HealthMetric {
  id: string;
  name: string;
  value: number;
  unit: string;
  target: number;
  icon: string;
  color: string;
  trend: 'up' | 'down' | 'stable';
  suggestion: string;
}

// 生活计划类型
interface LifePlan {
  id: string;
  title: string;
  description: string;
  progress: number;
  duration: string;
  category: string;
  icon: string;
  color: string;
  nextAction: string;
}

// 索儿的生活建议
const SOER_SUGGESTIONS: LifeSuggestion[] = [
  {
    id: 'morning_routine',
    title: '建立晨间仪式',
    description: '每天早上花15分钟做伸展运动，喝一杯温水，为新的一天做好准备',
    category: 'exercise',
    priority: 'high',
    icon: 'weather-sunny',
    color: '#FF9500',
    completed: false,
    timeEstimate: '15分钟',
  },
  {
    id: 'healthy_lunch',
    title: '营养午餐搭配',
    description: '今日推荐：蒸蛋羹配时令蔬菜，营养均衡又美味',
    category: 'diet',
    priority: 'high',
    icon: 'food',
    color: '#34C759',
    completed: false,
    timeEstimate: '30分钟',
  },
  {
    id: 'afternoon_break',
    title: '下午茶时光',
    description: '工作间隙来一杯花茶，配点坚果，既解乏又健康',
    category: 'mental',
    priority: 'medium',
    icon: 'tea',
    color: '#5856D6',
    completed: true,
    timeEstimate: '10分钟',
  },
  {
    id: 'evening_walk',
    title: '晚间散步',
    description: '饭后一小时，到附近公园走走，有助消化和放松心情',
    category: 'exercise',
    priority: 'medium',
    icon: 'walk',
    color: '#007AFF',
    completed: false,
    timeEstimate: '30分钟',
  },
  {
    id: 'digital_detox',
    title: '数字排毒',
    description: '睡前一小时关闭电子设备，读书或听音乐，提高睡眠质量',
    category: 'sleep',
    priority: 'high',
    icon: 'cellphone-off',
    color: '#FF2D92',
    completed: false,
    timeEstimate: '60分钟',
  },
  {
    id: 'social_connection',
    title: '社交联系',
    description: '给家人朋友打个电话，分享今天的美好时光',
    category: 'social',
    priority: 'low',
    icon: 'phone',
    color: '#8E44AD',
    completed: false,
    timeEstimate: '20分钟',
  },
];

// 健康指标数据
const HEALTH_METRICS: HealthMetric[] = [
  {
    id: 'mood',
    name: '心情指数',
    value: 85,
    unit: '分',
    target: 80,
    icon: 'emoticon-happy',
    color: '#FF9500',
    trend: 'up',
    suggestion: '保持积极心态，今天心情不错！',
  },
  {
    id: 'energy',
    name: '精力水平',
    value: 72,
    unit: '分',
    target: 80,
    icon: 'lightning-bolt',
    color: '#34C759',
    trend: 'stable',
    suggestion: '适当休息，补充能量',
  },
  {
    id: 'stress',
    name: '压力水平',
    value: 35,
    unit: '分',
    target: 30,
    icon: 'head-cog',
    color: '#FF2D92',
    trend: 'down',
    suggestion: '压力稍高，建议放松一下',
  },
  {
    id: 'balance',
    name: '生活平衡',
    value: 78,
    unit: '分',
    target: 85,
    icon: 'scale-balance',
    color: '#5856D6',
    trend: 'up',
    suggestion: '工作生活平衡良好',
  },
];

// 生活计划数据
const LIFE_PLANS: LifePlan[] = [
  {
    id: 'healthy_lifestyle',
    title: '健康生活方式养成',
    description: '建立规律作息，培养健康饮食和运动习惯',
    progress: 68,
    duration: '21天',
    category: '生活习惯',
    icon: 'heart-pulse',
    color: '#FF2D92',
    nextAction: '完成今日晨练',
  },
  {
    id: 'work_life_balance',
    title: '工作生活平衡',
    description: '合理安排工作时间，留出充足的休息和娱乐时间',
    progress: 45,
    duration: '30天',
    category: '时间管理',
    icon: 'scale-balance',
    color: '#5856D6',
    nextAction: '设置工作边界',
  },
  {
    id: 'mindfulness_practice',
    title: '正念练习',
    description: '每天进行冥想和正念练习，提高专注力和内心平静',
    progress: 32,
    duration: '14天',
    category: '心理健康',
    icon: 'meditation',
    color: '#34C759',
    nextAction: '进行10分钟冥想',
  },
];

const LifeScreen: React.FC = () => {
  const [selectedTab, setSelectedTab] = useState<'overview' | 'suggestions' | 'plans' | 'blockchain' | 'ar'>('overview');
  const [soerChatVisible, setSoerChatVisible] = useState(false);
  const [accessibilityEnabled, setAccessibilityEnabled] = useState(false);
  const [blockchainModalVisible, setBlockchainModalVisible] = useState(false);
  const [arModalVisible, setArModalVisible] = useState(false);

  // 与索儿对话
  const chatWithSoer = () => {
    Alert.alert(
      '与索儿对话',
      '索儿是您的生活方式指导助手，专注于帮助您：\n\n• 制定个性化生活计划\n• 提供健康生活建议\n• 平衡工作与生活\n• 培养良好习惯\n• 提升生活质量\n\n是否开始对话？',
      [
        { text: '取消', style: 'cancel' },
        { text: '开始对话', onPress: () => startSoerChat() }
      ]
    );
  };

  // 开始与索儿对话
  const startSoerChat = () => {
    setSoerChatVisible(true);
    console.log('Starting chat with Soer agent');
  };

  // 完成建议
  const completeSuggestion = (suggestion: LifeSuggestion) => {
    Alert.alert(
      '完成建议',
      `太棒了！您完成了"${suggestion.title}"，索儿为您感到骄傲！\n\n继续保持这样的生活方式，您会越来越健康快乐的！`,
      [
        { text: '继续努力', onPress: () => console.log(`Completed: ${suggestion.id}`) }
      ]
    );
  };

  // 查看建议详情
  const viewSuggestionDetail = (suggestion: LifeSuggestion) => {
    Alert.alert(
      suggestion.title,
      `${suggestion.description}\n\n分类：${getCategoryText(suggestion.category)}\n优先级：${getPriorityText(suggestion.priority)}\n预计时间：${suggestion.timeEstimate}\n\n索儿建议您现在就开始行动！`,
      [
        { text: '稍后执行', style: 'cancel' },
        { text: '立即执行', onPress: () => completeSuggestion(suggestion) }
      ]
    );
  };

  // 查看计划详情
  const viewPlanDetail = (plan: LifePlan) => {
    Alert.alert(
      plan.title,
      `${plan.description}\n\n进度：${plan.progress}%\n持续时间：${plan.duration}\n分类：${plan.category}\n\n下一步行动：${plan.nextAction}`,
      [
        { text: '查看详情', onPress: () => console.log(`View plan: ${plan.id}`) },
        { text: '执行行动', onPress: () => executePlanAction(plan) }
      ]
    );
  };

  // 执行计划行动
  const executePlanAction = (plan: LifePlan) => {
    Alert.alert('执行行动', `正在执行：${plan.nextAction}\n\n索儿会陪伴您完成这个行动！`);
    console.log(`Execute action for plan: ${plan.id}`);
  };

  // 获取分类文本
  const getCategoryText = (category: string) => {
    const categoryMap = {
      diet: '饮食',
      exercise: '运动',
      sleep: '睡眠',
      mental: '心理',
      social: '社交',
      work: '工作'
    };
    return categoryMap[category as keyof typeof categoryMap] || category;
  };

  // 获取优先级文本
  const getPriorityText = (priority: string) => {
    const priorityMap = {
      high: '高',
      medium: '中',
      low: '低'
    };
    return priorityMap[priority as keyof typeof priorityMap] || priority;
  };

  // 渲染健康指标
  const renderHealthMetric = (metric: HealthMetric) => {
    const progress = (metric.value / metric.target) * 100;
    const isOnTarget = progress >= 100;

    return (
      <View key={metric.id} style={styles.metricCard}>
        <View style={styles.metricHeader}>
          <View style={[styles.metricIcon, { backgroundColor: metric.color + '20' }]}>
            <Icon name={metric.icon} size={20} color={metric.color} />
          </View>
          <View style={styles.metricInfo}>
            <Text style={styles.metricName}>{metric.name}</Text>
            <Text style={styles.metricValue}>
              {metric.value} {metric.unit}
            </Text>
          </View>
          <View style={styles.metricTrend}>
            <Icon
              name={metric.trend === 'up' ? 'trending-up' : metric.trend === 'down' ? 'trending-down' : 'trending-neutral'}
              size={16}
              color={metric.trend === 'up' ? '#34C759' : metric.trend === 'down' ? '#FF3B30' : colors.textSecondary}
            />
          </View>
        </View>
        <View style={styles.progressContainer}>
          <View style={styles.progressBar}>
            <View
              style={[
                styles.progressFill,
                { width: `${Math.min(progress, 100)}%`, backgroundColor: metric.color }
              ]}
            />
          </View>
          <Text style={[styles.progressText, { color: isOnTarget ? '#34C759' : colors.textSecondary }]}>
            {Math.round(progress)}%
          </Text>
        </View>
        <Text style={styles.suggestionText}>💡 {metric.suggestion}</Text>
      </View>
    );
  };

  // 渲染生活建议
  const renderSuggestion = ({ item }: { item: LifeSuggestion }) => (
    <TouchableOpacity 
      style={[styles.suggestionCard, item.completed && styles.completedCard]} 
      onPress={() => viewSuggestionDetail(item)}
    >
      <View style={styles.suggestionHeader}>
        <View style={[styles.suggestionIcon, { backgroundColor: item.color + '20' }]}>
          <Icon name={item.icon} size={24} color={item.color} />
        </View>
        <View style={styles.suggestionInfo}>
          <Text style={[styles.suggestionTitle, item.completed && styles.completedText]}>
            {item.title}
          </Text>
          <Text style={styles.suggestionCategory}>
            {getCategoryText(item.category)} • {item.timeEstimate}
          </Text>
        </View>
        <View style={[styles.priorityBadge, { backgroundColor: getPriorityColor(item.priority) }]}>
          <Text style={styles.priorityText}>{getPriorityText(item.priority)}</Text>
        </View>
      </View>
      <Text style={[styles.suggestionDescription, item.completed && styles.completedText]}>
        {item.description}
      </Text>
      {item.completed && (
        <View style={styles.completedBadge}>
          <Icon name="check-circle" size={16} color="#34C759" />
          <Text style={styles.completedBadgeText}>已完成</Text>
        </View>
      )}
    </TouchableOpacity>
  );

  // 渲染生活计划
  const renderPlan = ({ item }: { item: LifePlan }) => (
    <TouchableOpacity style={styles.planCard} onPress={() => viewPlanDetail(item)}>
      <View style={styles.planHeader}>
        <View style={[styles.planIcon, { backgroundColor: item.color + '20' }]}>
          <Icon name={item.icon} size={24} color={item.color} />
        </View>
        <View style={styles.planInfo}>
          <Text style={styles.planTitle}>{item.title}</Text>
          <Text style={styles.planCategory}>{item.category} • {item.duration}</Text>
        </View>
        <Text style={[styles.progressPercentage, { color: item.color }]}>
          {item.progress}%
        </Text>
      </View>
      <Text style={styles.planDescription}>{item.description}</Text>
      <View style={styles.progressContainer}>
        <View style={styles.progressBar}>
          <View
            style={[
              styles.progressFill,
              { width: `${item.progress}%`, backgroundColor: item.color }
            ]}
          />
        </View>
      </View>
      <View style={styles.nextActionContainer}>
        <Icon name="arrow-right-circle" size={16} color={item.color} />
        <Text style={[styles.nextActionText, { color: item.color }]}>
          下一步：{item.nextAction}
        </Text>
      </View>
    </TouchableOpacity>
  );

  // 获取优先级颜色
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return '#FF3B30';
      case 'medium': return '#FF9500';
      case 'low': return '#34C759';
      default: return colors.textSecondary;
    }
  };

  // 渲染标签栏
  const renderTabBar = () => (
    <View style={styles.tabBar}>
      {[
        { key: 'overview', label: '概览', icon: 'view-dashboard' },
        { key: 'suggestions', label: '建议', icon: 'lightbulb' },
        { key: 'plans', label: '计划', icon: 'calendar-check' },
        { key: 'blockchain', label: '区块链', icon: 'shield-check' },
        { key: 'ar', label: 'AR体质', icon: 'camera-3d' }
      ].map(tab => (
        <TouchableOpacity
          key={tab.key}
          style={[styles.tabItem, selectedTab === tab.key && styles.activeTabItem]}
          onPress={() => {
            if (tab.key === 'blockchain') {
              setBlockchainModalVisible(true);
            } else if (tab.key === 'ar') {
              setArModalVisible(true);
            } else {
              setSelectedTab(tab.key as any);
            }
          }}
        >
          <Icon
            name={tab.icon}
            size={20}
            color={selectedTab === tab.key ? colors.primary : colors.textSecondary}
          />
          <Text style={[
            styles.tabLabel,
            selectedTab === tab.key && styles.activeTabLabel
          ]}>
            {tab.label}
          </Text>
        </TouchableOpacity>
      ))}
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      {/* 头部 */}
      <View style={styles.header}>
        <View>
          <Text style={styles.title}>LIFE 生活</Text>
          <Text style={styles.subtitle}>索儿陪您享受美好生活</Text>
        </View>
        <TouchableOpacity style={styles.soerChatButton} onPress={chatWithSoer}>
          <Text style={styles.soerChatEmoji}>👧</Text>
          <Text style={styles.soerChatText}>索儿</Text>
        </TouchableOpacity>
      </View>

      {/* 索儿助手卡片 */}
      <TouchableOpacity style={styles.soerCard} onPress={chatWithSoer}>
        <View style={styles.soerInfo}>
          <Text style={styles.soerEmoji}>👧</Text>
          <View style={styles.soerTextContainer}>
            <Text style={styles.soerName}>索儿 - 生活方式指导师</Text>
            <Text style={styles.soerDesc}>让每一天都充满活力与美好</Text>
            <Text style={styles.soerQuote}>"生活不止眼前的苟且，还有诗和远方"</Text>
          </View>
        </View>
        <View style={styles.onlineStatus}>
          <View style={styles.onlineDot} />
          <Text style={styles.onlineText}>在线</Text>
        </View>
      </TouchableOpacity>

      {/* 标签栏 */}
      {renderTabBar()}

      {/* 内容区域 */}
      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {selectedTab === 'overview' && (
          <View style={styles.overviewSection}>
            <Text style={styles.sectionTitle}>📊 今日健康指标</Text>
            <View style={styles.metricsGrid}>
              {HEALTH_METRICS.map(renderHealthMetric)}
            </View>
            
            <Text style={styles.sectionTitle}>💡 今日推荐</Text>
            <FlatList
              data={SOER_SUGGESTIONS.slice(0, 3)}
              keyExtractor={item => item.id}
              renderItem={renderSuggestion}
              scrollEnabled={false}
            />
          </View>
        )}

        {selectedTab === 'suggestions' && (
          <View style={styles.suggestionsSection}>
            <Text style={styles.sectionTitle}>💡 索儿的生活建议</Text>
            <FlatList
              data={SOER_SUGGESTIONS}
              keyExtractor={item => item.id}
              renderItem={renderSuggestion}
              scrollEnabled={false}
            />
          </View>
        )}

        {selectedTab === 'plans' && (
          <View style={styles.plansSection}>
            <Text style={styles.sectionTitle}>📅 我的生活计划</Text>
            <FlatList
              data={LIFE_PLANS}
              keyExtractor={item => item.id}
              renderItem={renderPlan}
              scrollEnabled={false}
            />
          </View>
        )}
      </ScrollView>

      {/* 区块链健康数据模态框 */}
      <BlockchainHealthData
        visible={blockchainModalVisible}
        onClose={() => setBlockchainModalVisible(false)}
      />

      {/* AR体质可视化模态框 */}
      <ARConstitutionVisualization
        visible={arModalVisible}
        onClose={() => setArModalVisible(false)}
      />

      {/* 索儿对话界面 */}
      <AgentChatInterface
        visible={soerChatVisible}
        onClose={() => setSoerChatVisible(false)}
        agentType="soer"
        userId="current_user_id"
        accessibilityEnabled={accessibilityEnabled}
      />
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 15,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: colors.text,
  },
  subtitle: {
    fontSize: 14,
    color: colors.textSecondary,
    marginTop: 2,
  },
  soerChatButton: {
    alignItems: 'center',
    padding: 8,
  },
  soerChatEmoji: {
    fontSize: 24,
  },
  soerChatText: {
    fontSize: 12,
    color: colors.primary,
    fontWeight: '600',
    marginTop: 2,
  },
  soerCard: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    margin: 15,
    padding: 15,
    backgroundColor: '#FF2D92' + '10',
    borderRadius: 12,
    borderLeftWidth: 4,
    borderLeftColor: '#FF2D92',
  },
  soerInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  soerEmoji: {
    fontSize: 32,
    marginRight: 12,
  },
  soerTextContainer: {
    flex: 1,
  },
  soerName: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.text,
    marginBottom: 4,
  },
  soerDesc: {
    fontSize: 12,
    color: colors.textSecondary,
    marginBottom: 4,
  },
  soerQuote: {
    fontSize: 11,
    color: '#FF2D92',
    fontStyle: 'italic',
  },
  onlineStatus: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  onlineDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#34C759',
    marginRight: 4,
  },
  onlineText: {
    fontSize: 12,
    color: '#34C759',
    fontWeight: '600',
  },
  tabBar: {
    flexDirection: 'row',
    backgroundColor: colors.surface,
    marginHorizontal: 15,
    marginBottom: 15,
    borderRadius: 12,
    padding: 4,
  },
  tabItem: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 8,
    borderRadius: 8,
  },
  activeTabItem: {
    backgroundColor: colors.primary + '20',
  },
  tabLabel: {
    marginLeft: 4,
    fontSize: 14,
    color: colors.textSecondary,
  },
  activeTabLabel: {
    color: colors.primary,
    fontWeight: '600',
  },
  content: {
    flex: 1,
    paddingHorizontal: 15,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: colors.text,
    marginBottom: 15,
  },
  overviewSection: {
    paddingBottom: 20,
  },
  metricsGrid: {
    marginBottom: 25,
  },
  metricCard: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: 15,
    marginBottom: 10,
  },
  metricHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  metricIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  metricInfo: {
    flex: 1,
  },
  metricName: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.text,
  },
  metricValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: colors.text,
    marginTop: 2,
  },
  metricTrend: {
    padding: 4,
  },
  progressContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  progressBar: {
    flex: 1,
    height: 6,
    backgroundColor: colors.border,
    borderRadius: 3,
    marginRight: 8,
  },
  progressFill: {
    height: '100%',
    borderRadius: 3,
  },
  progressText: {
    fontSize: 12,
    fontWeight: '600',
    minWidth: 35,
  },
  suggestionText: {
    fontSize: 12,
    color: colors.textSecondary,
    fontStyle: 'italic',
  },
  suggestionsSection: {
    paddingBottom: 20,
  },
  suggestionCard: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: 15,
    marginBottom: 10,
  },
  completedCard: {
    opacity: 0.7,
    backgroundColor: '#E8F5E8',
  },
  suggestionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  suggestionIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  suggestionInfo: {
    flex: 1,
  },
  suggestionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.text,
    marginBottom: 2,
  },
  completedText: {
    textDecorationLine: 'line-through',
    color: colors.textSecondary,
  },
  suggestionCategory: {
    fontSize: 12,
    color: colors.textSecondary,
  },
  priorityBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 10,
  },
  priorityText: {
    fontSize: 10,
    color: 'white',
    fontWeight: '600',
  },
  suggestionDescription: {
    fontSize: 14,
    color: colors.textSecondary,
    lineHeight: 20,
    marginBottom: 8,
  },
  completedBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    alignSelf: 'flex-start',
  },
  completedBadgeText: {
    fontSize: 12,
    color: '#34C759',
    fontWeight: '600',
    marginLeft: 4,
  },
  plansSection: {
    paddingBottom: 20,
  },
  planCard: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: 15,
    marginBottom: 15,
  },
  planHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  planIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  planInfo: {
    flex: 1,
  },
  planTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.text,
    marginBottom: 2,
  },
  planCategory: {
    fontSize: 12,
    color: colors.textSecondary,
  },
  progressPercentage: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  planDescription: {
    fontSize: 14,
    color: colors.textSecondary,
    lineHeight: 20,
    marginBottom: 12,
  },
  nextActionContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 8,
  },
  nextActionText: {
    fontSize: 12,
    fontWeight: '600',
    marginLeft: 4,
  },
});

export default LifeScreen;
