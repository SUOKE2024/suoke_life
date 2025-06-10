import { useNavigation } from '@react-navigation/native';
import React, { useEffect, useRef, useState } from 'react';
import {;
  Animated,
  FlatList,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import {;
  borderRadius,
  colors,
  shadows,
  spacing,
  typography
} from '../../constants/theme';

interface Message {
  id: string;,
  type: 'user' | 'ai';,
  content: string;,
  timestamp: string;
  suggestions?: string[];
}

interface HealthTip {
  id: string;,
  title: string;,
  content: string;,
  category: string;,
  icon: string;,
  priority: 'high' | 'medium' | 'low';
}

interface QuickAction {
  id: string;,
  title: string;,
  description: string;,
  icon: string;,
  color: string;
}

const AIHealthAssistantScreen: React.FC = () => {
  const navigation = useNavigation();
  const [activeTab, setActiveTab] = useState<'chat' | 'tips' | 'analysis'>(
    'chat'
  );
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  // 动画值
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(50)).current;

  // 聊天消息
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'ai',
      content:
        '您好！我是您的AI健康助手小艾。我可以帮您分析健康状况、提供个性化建议、回答健康问题。请问今天有什么可以帮助您的吗？',
      timestamp: '09:00',
      suggestions: [
        '我想了解我的健康状况',
        '最近感觉疲劳怎么办',
        '如何改善睡眠质量'
      ]
    },
    {
      id: '2',
      type: 'user',
      content: '最近总是感觉疲劳，精神不振，这是什么原因？',
      timestamp: '09:05'
    },
    {
      id: '3',
      type: 'ai',
      content:
        '根据您的描述，疲劳可能由多种因素引起：\n\n1. 睡眠质量不佳\n2. 营养不均衡\n3. 缺乏运动\n4. 工作压力过大\n5. 可能的健康问题\n\n建议您：\n• 保证每晚7-8小时优质睡眠\n• 均衡饮食，补充维生素B群\n• 适量运动，增强体质\n• 学会放松，减轻压力\n\n如果症状持续，建议咨询医生进行详细检查。',
      timestamp: '09:06',
      suggestions: ['如何改善睡眠', '推荐营养补充', '制定运动计划']
    }
  ]);

  // 健康建议
  const healthTips = [
    {
      id: '1',
      title: '保持充足睡眠',
      content:
        '每晚保证7-8小时的优质睡眠，有助于身体恢复和免疫力提升。建议23:00前入睡，避免睡前使用电子设备。',
      category: '睡眠健康',
      icon: 'sleep',
      priority: 'high' as const
    },
    {
      id: '2',
      title: '均衡营养摄入',
      content:
        '多吃新鲜蔬果，适量摄入优质蛋白质，减少加工食品。每日饮水量保持在1.5-2升。',
      category: '营养饮食',
      icon: 'food-apple',
      priority: 'high' as const
    },
    {
      id: '3',
      title: '规律运动锻炼',
      content:
        '每周至少150分钟中等强度运动，可以选择快走、游泳、骑行等有氧运动。',
      category: '运动健身',
      icon: 'run',
      priority: 'medium' as const
    },
    {
      id: '4',
      title: '管理情绪压力',
      content:
        '学会放松技巧，如深呼吸、冥想、瑜伽等。保持积极心态，及时排解负面情绪。',
      category: '心理健康',
      icon: 'meditation',
      priority: 'medium' as const
    }
  ];

  // 快捷操作
  const quickActions = [
    {
      id: '1',
      title: '症状分析',
      description: '描述症状，获取AI分析',
      icon: 'stethoscope',
      color: colors.primary
    },
    {
      id: '2',
      title: '健康评估',
      description: '全面评估健康状况',
      icon: 'heart-pulse',
      color: colors.error
    },
    {
      id: '3',
      title: '用药咨询',
      description: '药物使用指导建议',
      icon: 'pill',
      color: colors.warning
    },
    {
      id: '4',
      title: '营养建议',
      description: '个性化饮食方案',
      icon: 'food',
      color: colors.success
    },
    {
      id: '5',
      title: '运动计划',
      description: '定制运动健身方案',
      icon: 'dumbbell',
      color: colors.info
    },
    {
      id: '6',
      title: '心理支持',
      description: '情绪管理和心理疏导',
      icon: 'brain',
      color: colors.secondary
    }
  ];

  useEffect() => {
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 800,
        useNativeDriver: true
      }),
      Animated.timing(slideAnim, {
        toValue: 0,
        duration: 800,
        useNativeDriver: true
      })
    ]).start();
  }, []);

  // 发送消息
  const sendMessage = () => {
    if (!inputText.trim()) return;

    const newMessage: Message = {,
  id: Date.now().toString(),
      type: 'user',
      content: inputText,
      timestamp: new Date().toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit'
      })
    };

    setMessages(prev) => [...prev, newMessage]);
    setInputText('');
    setIsTyping(true);

    // 模拟AI回复
    setTimeout() => {
      const aiResponse: Message = {,
  id: (Date.now() + 1).toString(),
        type: 'ai',
        content: '感谢您的问题。我正在分析您的情况，请稍等片刻...',
        timestamp: new Date().toLocaleTimeString('zh-CN', {
          hour: '2-digit',
          minute: '2-digit'
        }),
        suggestions: ['了解更多', '相关建议', '专家咨询']
      };
      setMessages(prev) => [...prev, aiResponse]);
      setIsTyping(false);
    }, 2000);
  };

  // 渲染标签栏
  const renderTabs = () => {
    const tabs = [
      { key: 'chat', title: '智能问答', icon: 'chat' },
      { key: 'tips', title: '健康建议', icon: 'lightbulb' },
      { key: 'analysis', title: '健康分析', icon: 'chart-line' }
    ];

    return (
      <View style={styles.tabContainer}>
        {tabs.map(tab) => (
          <TouchableOpacity;
            key={tab.key}
            style={[styles.tab, activeTab === tab.key && styles.activeTab]}
            onPress={() => setActiveTab(tab.key as any)}
          >
            <Icon;
              name={tab.icon}
              size={20}
              color={
                activeTab === tab.key ? colors.primary : colors.textSecondary;
              }
            />
            <Text;
              style={[
                styles.tabText,
                activeTab === tab.key && styles.activeTabText
              ]}
            >
              {tab.title}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
    );
  };

  // 渲染消息
  const renderMessage = ({ item }: { item: Message }) => (
    <View;
      style={[
        styles.messageContainer,
        item.type === 'user' ? styles.userMessage : styles.aiMessage
      ]}
    >
      {item.type === 'ai' && (
        <View style={styles.aiAvatar}>
          <Icon name="robot" size={20} color={colors.primary} />
        </View>
      )}

      <View;
        style={[
          styles.messageBubble,
          item.type === 'user' ? styles.userBubble : styles.aiBubble
        ]}
      >
        <Text;
          style={[
            styles.messageText,
            item.type === 'user' ? styles.userText : styles.aiText
          ]}
        >
          {item.content}
        </Text>
        <Text style={styles.messageTime}>{item.timestamp}</Text>

        {item.suggestions && (
          <View style={styles.suggestionsContainer}>
            {item.suggestions.map(suggestion, index) => (
              <TouchableOpacity;
                key={index}
                style={styles.suggestionButton}
                onPress={() => setInputText(suggestion)}
              >
                <Text style={styles.suggestionText}>{suggestion}</Text>
              </TouchableOpacity>
            ))}
          </View>
        )}
      </View>

      {item.type === 'user' && (
        <View style={styles.userAvatar}>
          <Icon name="account" size={20} color={colors.white} />
        </View>
      )}
    </View>
  );

  // 渲染聊天界面
  const renderChatInterface = () => (
    <View style={styles.chatContainer}>
      {// 快捷操作}
      <View style={styles.quickActionsContainer}>
        <Text style={styles.sectionTitle}>快捷咨询</Text>
        <ScrollView;
          horizontal;
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.quickActionsContent}
        >
          {quickActions.map(action) => (
            <TouchableOpacity;
              key={action.id}
              style={styles.quickActionCard}
              onPress={() => setInputText(action.title)}
            >
              <View;
                style={[
                  styles.quickActionIcon,
                  { backgroundColor: action.color + '20' }
                ]}
              >
                <Icon name={action.icon} size={24} color={action.color} />
              </View>
              <Text style={styles.quickActionTitle}>{action.title}</Text>
              <Text style={styles.quickActionDesc}>{action.description}</Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>

      {// 消息列表}
      <FlatList;
        data={messages}
        renderItem={renderMessage}
        keyExtractor={(item) => item.id}
        style={styles.messagesList}
        showsVerticalScrollIndicator={false}
      />

      {// 输入框}
      <View style={styles.inputContainer}>
        <View style={styles.inputWrapper}>
          <TextInput;
            style={styles.textInput}
            placeholder="请输入您的健康问题..."
            value={inputText}
            onChangeText={setInputText}
            multiline;
            placeholderTextColor={colors.textSecondary}
          />
          <TouchableOpacity;
            style={[
              styles.sendButton,
              inputText.trim() && styles.sendButtonActive
            ]}
            onPress={sendMessage}
            disabled={!inputText.trim()}
          >
            <Icon;
              name="send"
              size={20}
              color={inputText.trim() ? colors.white : colors.textSecondary}
            />
          </TouchableOpacity>
        </View>

        {isTyping && (
          <View style={styles.typingIndicator}>
            <Text style={styles.typingText}>AI助手正在输入...</Text>
          </View>
        )}
      </View>
    </View>
  );

  // 渲染健康建议卡片
  const renderHealthTip = ({ item }: { item: HealthTip }) => (
    <View style={styles.tipCard}>
      <View style={styles.tipHeader}>
        <View style={styles.tipIconContainer}>
          <Icon name={item.icon} size={24} color={colors.primary} />
        </View>
        <View style={styles.tipInfo}>
          <Text style={styles.tipTitle}>{item.title}</Text>
          <Text style={styles.tipCategory}>{item.category}</Text>
        </View>
        <View;
          style={[
            styles.priorityBadge,
            {
              backgroundColor:
                item.priority === 'high'
                  ? colors.error;
                  : item.priority === 'medium'
                    ? colors.warning;
                    : colors.success
            }
          ]}
        >
          <Text style={styles.priorityText}>
            {item.priority === 'high'
              ? '重要'
              : item.priority === 'medium'
                ? '一般'
                : '建议'}
          </Text>
        </View>
      </View>
      <Text style={styles.tipContent}>{item.content}</Text>
      <TouchableOpacity style={styles.tipAction}>
        <Text style={styles.tipActionText}>了解更多</Text>
        <Icon name="chevron-right" size={16} color={colors.primary} />
      </TouchableOpacity>
    </View>
  );

  // 渲染健康建议
  const renderHealthTips = () => (
    <View style={styles.tipsContainer}>
      <View style={styles.tipsHeader}>
        <Text style={styles.sectionTitle}>个性化健康建议</Text>
        <Text style={styles.sectionSubtitle}>基于您的健康数据和行为模式</Text>
      </View>

      <FlatList;
        data={healthTips}
        renderItem={renderHealthTip}
        keyExtractor={(item) => item.id}
        showsVerticalScrollIndicator={false}
      />
    </View>
  );

  // 渲染健康分析
  const renderHealthAnalysis = () => (
    <View style={styles.analysisContainer}>
      <View style={styles.analysisHeader}>
        <Text style={styles.sectionTitle}>AI健康分析</Text>
        <Text style={styles.sectionSubtitle}>综合评估您的健康状况</Text>
      </View>

      {// 健康评分}
      <View style={styles.scoreCard}>
        <View style={styles.scoreHeader}>
          <Text style={styles.scoreTitle}>综合健康评分</Text>
          <Text style={styles.scoreDate}>更新时间：今天 09:30</Text>
        </View>
        <View style={styles.scoreContent}>
          <View style={styles.scoreCircle}>
            <Text style={styles.scoreValue}>85</Text>
            <Text style={styles.scoreLabel}>分</Text>
          </View>
          <View style={styles.scoreDetails}>
            <Text style={styles.scoreStatus}>健康状况良好</Text>
            <Text style={styles.scoreDescription}>
              您的整体健康状况良好，建议继续保持良好的生活习惯，
              注意改善睡眠质量和增加运动量。
            </Text>
          </View>
        </View>
      </View>

      {// 各项指标}
      <View style={styles.metricsCard}>
        <Text style={styles.metricsTitle}>健康指标分析</Text>
        <View style={styles.metricsList}>
          {[
            {
              name: '睡眠质量',
              score: 78,
              status: '良好',
              color: colors.primary
            },
            {
              name: '运动活跃度',
              score: 65,
              status: '一般',
              color: colors.warning
            },
            {
              name: '营养均衡',
              score: 88,
              status: '优秀',
              color: colors.success
            },
            {
              name: '心理状态',
              score: 92,
              status: '优秀',
              color: colors.success
            }
          ].map(metric, index) => (
            <View key={index} style={styles.metricItem}>
              <View style={styles.metricInfo}>
                <Text style={styles.metricName}>{metric.name}</Text>
                <Text style={[styles.metricStatus, { color: metric.color }]}>
                  {metric.status}
                </Text>
              </View>
              <View style={styles.metricProgress}>
                <View style={styles.progressBar}>
                  <View;
                    style={[
                      styles.progressFill,
                      {
                        width: `${metric.score}%`,
                        backgroundColor: metric.color
                      }
                    ]}
                  />
                </View>
                <Text style={styles.metricScore}>{metric.score}</Text>
              </View>
            </View>
          ))}
        </View>
      </View>

      {// AI建议}
      <View style={styles.aiSuggestionsCard}>
        <Text style={styles.suggestionsTitle}>AI个性化建议</Text>
        <View style={styles.suggestionsList}>
          {[
            '建议每晚23:00前入睡，提高睡眠质量',
            '增加有氧运动，每周至少3次，每次30分钟',
            '保持当前的饮食习惯，营养搭配很好',
            '继续保持积极心态，适当进行放松练习'
          ].map(suggestion, index) => (
            <View key={index} style={styles.suggestionItem}>
              <Icon name="check-circle" size={16} color={colors.success} />
              <Text style={styles.suggestionText}>{suggestion}</Text>
            </View>
          ))}
        </View>
      </View>
    </View>
  );

  // 渲染内容
  const renderContent = () => {
    switch (activeTab) {
      case 'chat':
        return renderChatInterface();
      case 'tips':
        return renderHealthTips();
      case 'analysis':
        return renderHealthAnalysis();
      default:
        return null;
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      {// 头部}
      <View style={styles.header}>
        <TouchableOpacity;
          style={styles.backButton}
          onPress={() => navigation.goBack()}
        >
          <Icon name="arrow-left" size={24} color={colors.text} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>AI健康助手</Text>
        <TouchableOpacity style={styles.settingsButton}>
          <Icon name="cog-outline" size={24} color={colors.text} />
        </TouchableOpacity>
      </View>

      {// 标签栏}
      {renderTabs()}

      {// 内容区域}
      <Animated.View;
        style={[
          styles.contentContainer,
          {
            opacity: fadeAnim,
            transform: [{ translateY: slideAnim }]
          }
        ]}
      >
        {renderContent()}
      </Animated.View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {,
  flex: 1,
    backgroundColor: colors.background
  },
  header: {,
  flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    backgroundColor: colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: colors.border
  },
  backButton: {,
  width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.gray100,
    justifyContent: 'center',
    alignItems: 'center'
  },
  headerTitle: {,
  fontSize: typography.fontSize.lg,
    fontWeight: '600' as const,
    color: colors.text
  },
  settingsButton: {,
  width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.gray100,
    justifyContent: 'center',
    alignItems: 'center'
  },
  tabContainer: {,
  flexDirection: 'row',
    backgroundColor: colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: colors.border
  },
  tab: {,
  flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: spacing.md,
    gap: spacing.xs
  },
  activeTab: {,
  borderBottomWidth: 2,
    borderBottomColor: colors.primary
  },
  tabText: {,
  fontSize: typography.fontSize.sm,
    color: colors.textSecondary
  },
  activeTabText: {,
  color: colors.primary,
    fontWeight: '600' as const
  },
  contentContainer: {,
  flex: 1
  },
  sectionTitle: {,
  fontSize: typography.fontSize.lg,
    fontWeight: '600' as const,
    color: colors.text
  },
  sectionSubtitle: {,
  fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    marginTop: spacing.xs
  },
  // 聊天界面样式
  chatContainer: {,
  flex: 1
  },
  quickActionsContainer: {,
  padding: spacing.lg,
    backgroundColor: colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: colors.border
  },
  quickActionsContent: {,
  paddingVertical: spacing.md,
    gap: spacing.md
  },
  quickActionCard: {,
  width: 120,
    backgroundColor: colors.gray50,
    borderRadius: borderRadius.lg,
    padding: spacing.md,
    alignItems: 'center',
    ...shadows.sm
  },
  quickActionIcon: {,
  width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: spacing.sm
  },
  quickActionTitle: {,
  fontSize: typography.fontSize.sm,
    fontWeight: '600' as const,
    color: colors.text,
    textAlign: 'center',
    marginBottom: spacing.xs
  },
  quickActionDesc: {,
  fontSize: typography.fontSize.xs,
    color: colors.textSecondary,
    textAlign: 'center'
  },
  messagesList: {,
  flex: 1,
    paddingHorizontal: spacing.lg
  },
  messageContainer: {,
  flexDirection: 'row',
    marginVertical: spacing.sm,
    alignItems: 'flex-end'
  },
  userMessage: {,
  justifyContent: 'flex-end'
  },
  aiMessage: {,
  justifyContent: 'flex-start'
  },
  aiAvatar: {,
  width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: colors.primary + '20',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.sm
  },
  userAvatar: {,
  width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: spacing.sm
  },
  messageBubble: {,
  maxWidth: '75%',
    borderRadius: borderRadius.lg,
    padding: spacing.md
  },
  userBubble: {,
  backgroundColor: colors.primary,
    borderBottomRightRadius: 4
  },
  aiBubble: {,
  backgroundColor: colors.gray100,
    borderBottomLeftRadius: 4
  },
  messageText: {,
  fontSize: typography.fontSize.base,
    lineHeight: 20
  },
  userText: {,
  color: colors.white
  },
  aiText: {,
  color: colors.text
  },
  messageTime: {,
  fontSize: typography.fontSize.xs,
    color: colors.textSecondary,
    marginTop: spacing.xs,
    opacity: 0.7
  },
  suggestionsContainer: {,
  marginTop: spacing.md,
    gap: spacing.xs
  },
  suggestionButton: {,
  backgroundColor: colors.primary + '20',
    borderRadius: borderRadius.md,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    alignSelf: 'flex-start'
  },
  suggestionText: {,
  fontSize: typography.fontSize.sm,
    color: colors.primary
  },
  inputContainer: {,
  backgroundColor: colors.surface,
    borderTopWidth: 1,
    borderTopColor: colors.border,
    padding: spacing.lg
  },
  inputWrapper: {,
  flexDirection: 'row',
    alignItems: 'flex-end',
    backgroundColor: colors.gray100,
    borderRadius: borderRadius.lg,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm
  },
  textInput: {,
  flex: 1,
    fontSize: typography.fontSize.base,
    color: colors.text,
    maxHeight: 100,
    marginRight: spacing.sm
  },
  sendButton: {,
  width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: colors.gray300,
    justifyContent: 'center',
    alignItems: 'center'
  },
  sendButtonActive: {,
  backgroundColor: colors.primary
  },
  typingIndicator: {,
  marginTop: spacing.sm
  },
  typingText: {,
  fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    fontStyle: 'italic'
  },
  // 健康建议样式
  tipsContainer: {,
  flex: 1,
    padding: spacing.lg
  },
  tipsHeader: {,
  marginBottom: spacing.lg
  },
  tipCard: {,
  backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    marginBottom: spacing.md,
    ...shadows.sm
  },
  tipHeader: {,
  flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.md
  },
  tipIconContainer: {,
  width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.primary + '20',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.md
  },
  tipInfo: {,
  flex: 1
  },
  tipTitle: {,
  fontSize: typography.fontSize.base,
    fontWeight: '600' as const,
    color: colors.text
  },
  tipCategory: {,
  fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    marginTop: 2
  },
  priorityBadge: {,
  paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: borderRadius.sm
  },
  priorityText: {,
  fontSize: typography.fontSize.xs,
    color: colors.white,
    fontWeight: '600' as const
  },
  tipContent: {,
  fontSize: typography.fontSize.base,
    color: colors.text,
    lineHeight: 22,
    marginBottom: spacing.md
  },
  tipAction: {,
  flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'flex-end',
    gap: spacing.xs
  },
  tipActionText: {,
  fontSize: typography.fontSize.sm,
    color: colors.primary,
    fontWeight: '600' as const
  },
  // 健康分析样式
  analysisContainer: {,
  flex: 1,
    padding: spacing.lg
  },
  analysisHeader: {,
  marginBottom: spacing.lg
  },
  scoreCard: {,
  backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    marginBottom: spacing.lg,
    ...shadows.sm
  },
  scoreHeader: {,
  flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.lg
  },
  scoreTitle: {,
  fontSize: typography.fontSize.base,
    fontWeight: '600' as const,
    color: colors.text
  },
  scoreDate: {,
  fontSize: typography.fontSize.sm,
    color: colors.textSecondary
  },
  scoreContent: {,
  flexDirection: 'row',
    alignItems: 'center'
  },
  scoreCircle: {,
  width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: colors.primary + '20',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.lg
  },
  scoreValue: {,
  fontSize: typography.fontSize['2xl'],
    fontWeight: '700' as const,
    color: colors.primary
  },
  scoreLabel: {,
  fontSize: typography.fontSize.sm,
    color: colors.primary
  },
  scoreDetails: {,
  flex: 1
  },
  scoreStatus: {,
  fontSize: typography.fontSize.lg,
    fontWeight: '600' as const,
    color: colors.text,
    marginBottom: spacing.sm
  },
  scoreDescription: {,
  fontSize: typography.fontSize.base,
    color: colors.textSecondary,
    lineHeight: 20
  },
  metricsCard: {,
  backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    marginBottom: spacing.lg,
    ...shadows.sm
  },
  metricsTitle: {,
  fontSize: typography.fontSize.base,
    fontWeight: '600' as const,
    color: colors.text,
    marginBottom: spacing.lg
  },
  metricsList: {,
  gap: spacing.lg
  },
  metricItem: {,
  flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between'
  },
  metricInfo: {,
  flex: 1
  },
  metricName: {,
  fontSize: typography.fontSize.base,
    color: colors.text,
    marginBottom: spacing.xs
  },
  metricStatus: {,
  fontSize: typography.fontSize.sm,
    fontWeight: '600' as const
  },
  metricProgress: {,
  flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.md,
    width: 120
  },
  progressBar: {,
  flex: 1,
    height: 8,
    backgroundColor: colors.gray200,
    borderRadius: 4,
    overflow: 'hidden'
  },
  progressFill: {,
  height: '100%',
    borderRadius: 4
  },
  metricScore: {,
  fontSize: typography.fontSize.sm,
    fontWeight: '600' as const,
    color: colors.text,
    width: 24,
    textAlign: 'right'
  },
  aiSuggestionsCard: {,
  backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    ...shadows.sm
  },
  suggestionsTitle: {,
  fontSize: typography.fontSize.base,
    fontWeight: '600' as const,
    color: colors.text,
    marginBottom: spacing.lg
  },
  suggestionsList: {,
  gap: spacing.md
  },
  suggestionItem: {,
  flexDirection: 'row',
    alignItems: 'flex-start',
    gap: spacing.sm
  },
  suggestionText: {,
  flex: 1,
    fontSize: typography.fontSize.base,
    color: colors.text,
    lineHeight: 20
  }
});

export default AIHealthAssistantScreen;
