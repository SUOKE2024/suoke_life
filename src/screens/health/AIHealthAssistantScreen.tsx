import React, { useEffect, useRef, useState } from 'react';
import {
  Alert,
  Animated,
  Dimensions,
  FlatList,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { useTheme } from '../../contexts/ThemeContext';

const { width, height } = Dimensions.get('window');

interface Message {
  id: string;,
  text: string;,
  isUser: boolean;,
  timestamp: Date;
  type?: 'text' | 'analysis' | 'suggestion';
}

interface QuickAction {
  id: string;,
  title: string;,
  icon: string;,
  description: string;,
  action: () => void;
}

interface HealthSuggestion {
  id: string;,
  category: string;,
  title: string;,
  description: string;,
  priority: 'high' | 'medium' | 'low';,
  icon: string;
}

const AIHealthAssistantScreen: React.FC = () => {
  const { theme } = useTheme();
  const [activeTab, setActiveTab] = useState<
    'chat' | 'suggestions' | 'analysis'
  >('chat');
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: '您好！我是您的AI健康助手，很高兴为您服务。我可以帮助您分析健康状况、提供个性化建议，或回答您的健康问题。请问今天有什么可以帮助您的吗？',
      isUser: false,
      timestamp: new Date(),
      type: 'text',
    },
  ]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const scrollViewRef = useRef<ScrollView>(null);
  const fadeAnim = useRef(new Animated.Value(0)).current;

  const quickActions: QuickAction[] = [
    {
      id: '1',
      title: '症状分析',
      icon: 'search',
      description: '描述您的症状，获得AI分析',
      action: () => handleQuickAction('我想分析一下我的症状'),
    },
    {
      id: '2',
      title: '健康评估',
      icon: 'assessment',
      description: '全面评估您的健康状况',
      action: () => handleQuickAction('请帮我做一个健康评估'),
    },
    {
      id: '3',
      title: '饮食建议',
      icon: 'restaurant',
      description: '获得个性化饮食建议',
      action: () => handleQuickAction('请给我一些饮食建议'),
    },
    {
      id: '4',
      title: '运动指导',
      icon: 'fitness-center',
      description: '制定适合的运动计划',
      action: () => handleQuickAction('请为我制定运动计划'),
    },
  ];

  const healthSuggestions: HealthSuggestion[] = [
    {
      id: '1',
      category: '饮食',
      title: '增加蛋白质摄入',
      description: '根据您的体重和活动量，建议每日增加20g优质蛋白质',
      priority: 'high',
      icon: 'restaurant',
    },
    {
      id: '2',
      category: '运动',
      title: '有氧运动计划',
      description: '建议每周进行3-4次中等强度有氧运动，每次30分钟',
      priority: 'medium',
      icon: 'directions-run',
    },
    {
      id: '3',
      category: '睡眠',
      title: '改善睡眠质量',
      description: '建议调整作息时间，保证每晚7-8小时优质睡眠',
      priority: 'high',
      icon: 'bedtime',
    },
    {
      id: '4',
      category: '心理',
      title: '压力管理',
      description: '尝试冥想或深呼吸练习，有助于缓解日常压力',
      priority: 'medium',
      icon: 'psychology',
    },
  ];

  useEffect() => {
    Animated.timing(fadeAnim, {
      toValue: 1,
      duration: 500,
      useNativeDriver: true,
    }).start();
  }, []);

  const handleQuickAction = (text: string) => {
    setInputText(text);
    handleSendMessage(text);
  };

  const handleSendMessage = async (text?: string) => {
    const messageText = text || inputText.trim();
    if (!messageText) return;

    const userMessage: Message = {,
  id: Date.now().toString(),
      text: messageText,
      isUser: true,
      timestamp: new Date(),
      type: 'text',
    };

    setMessages(prev) => [...prev, userMessage]);
    setInputText('');
    setIsTyping(true);

    // 模拟AI回复
    setTimeout() => {
      const aiResponse = generateAIResponse(messageText);
      setMessages(prev) => [...prev, aiResponse]);
      setIsTyping(false);
    }, 1500);
  };

  const generateAIResponse = (userMessage: string): Message => {
    const responses = {
      症状: {
        text: '我理解您想要分析症状。请详细描述您的症状，包括：\n\n1. 症状的具体表现\n2. 持续时间\n3. 严重程度\n4. 是否有诱发因素\n\n这样我可以为您提供更准确的分析和建议。',
        type: 'analysis' as const,
      },
      健康评估: {
        text: '基于您的健康数据分析：\n\n✅ 整体健康状况：良好\n📊 BMI指数：正常范围\n💓 心率变异性：稳定\n🩸 血压水平：理想\n\n建议继续保持良好的生活习惯，定期监测健康指标。',
        type: 'analysis' as const,
      },
      饮食: {
        text: '根据您的个人情况，我为您推荐以下饮食建议：\n\n🥗 多吃新鲜蔬菜水果\n🐟 适量摄入优质蛋白质\n🌾 选择全谷物食品\n💧 保证充足水分摄入\n\n避免过度加工食品和高糖饮料。',
        type: 'suggestion' as const,
      },
      运动: {
        text: '为您制定的个性化运动计划：\n\n🏃‍♂️ 有氧运动：每周3-4次，每次30分钟\n💪 力量训练：每周2次，针对主要肌群\n🧘‍♀️ 柔韧性训练：每日10分钟拉伸\n\n请根据自身情况调整强度，循序渐进。',
        type: 'suggestion' as const,
      },
    };

    let responseKey = Object.keys(responses).find(key) =>
      userMessage.includes(key)
    );

    if (!responseKey) {
      responseKey = '症状'; // 默认回复
    }

    const response =
      responses[responseKey as keyof typeof responses] || responses.症状;

    return {
      id: Date.now().toString(),
      text: response.text,
      isUser: false,
      timestamp: new Date(),
      type: response.type,
    };
  };

  const renderMessage = ({ item }: { item: Message }) => (
    <View;
      style={[
        styles.messageContainer,
        item.isUser ? styles.userMessage : styles.aiMessage,
      ]}
    >
      {!item.isUser && (
        <View style={[styles.aiAvatar, { backgroundColor: theme.primary }]}>
          <Icon name="smart-toy" size={20} color={theme.surface} />
        </View>
      )}
      <View;
        style={[
          styles.messageBubble,
          item.isUser;
            ? { backgroundColor: theme.primary }
            : {
                backgroundColor: theme.surface,
                borderColor: theme.border,
                borderWidth: 1,
              },
        ]}
      >
        <Text;
          style={[
            styles.messageText,
            { color: item.isUser ? theme.surface : theme.text },
          ]}
        >
          {item.text}
        </Text>
        <Text;
          style={[
            styles.messageTime,
            { color: item.isUser ? theme.surface + '80' : theme.textSecondary },
          ]}
        >
          {item.timestamp.toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </Text>
      </View>
    </View>
  );

  const renderQuickAction = ({ item }: { item: QuickAction }) => (
    <TouchableOpacity;
      style={[
        styles.quickActionCard,
        { backgroundColor: theme.surface, borderColor: theme.border },
      ]}
      onPress={item.action}
    >
      <View;
        style={[
          styles.quickActionIcon,
          { backgroundColor: theme.primary + '20' },
        ]}
      >
        <Icon name={item.icon} size={24} color={theme.primary} />
      </View>
      <Text style={[styles.quickActionTitle, { color: theme.text }]}>
        {item.title}
      </Text>
      <Text;
        style={[styles.quickActionDescription, { color: theme.textSecondary }]}
      >
        {item.description}
      </Text>
    </TouchableOpacity>
  );

  const renderSuggestion = ({ item }: { item: HealthSuggestion }) => (
    <View;
      style={[
        styles.suggestionCard,
        { backgroundColor: theme.surface, borderColor: theme.border },
      ]}
    >
      <View style={styles.suggestionHeader}>
        <View;
          style={[
            styles.suggestionIcon,
            { backgroundColor: theme.primary + '20' },
          ]}
        >
          <Icon name={item.icon} size={20} color={theme.primary} />
        </View>
        <View style={styles.suggestionInfo}>
          <Text;
            style={[styles.suggestionCategory, { color: theme.textSecondary }]}
          >
            {item.category}
          </Text>
          <Text style={[styles.suggestionTitle, { color: theme.text }]}>
            {item.title}
          </Text>
        </View>
        <View;
          style={[
            styles.priorityBadge,
            {
              backgroundColor:
                item.priority === 'high'
                  ? '#FF6B6B'
                  : item.priority === 'medium'
                    ? '#4ECDC4'
                    : '#95E1D3',
            },
          ]}
        >
          <Text style={[styles.priorityText, { color: theme.surface }]}>
            {item.priority === 'high'
              ? '高'
              : item.priority === 'medium'
                ? '中'
                : '低'}
          </Text>
        </View>
      </View>
      <Text;
        style={[styles.suggestionDescription, { color: theme.textSecondary }]}
      >
        {item.description}
      </Text>
    </View>
  );

  const renderChatTab = () => (
    <View style={styles.chatContainer}>
      <FlatList;
        ref={scrollViewRef}
        data={messages}
        renderItem={renderMessage}
        keyExtractor={(item) => item.id}
        style={styles.messagesList}
        onContentSizeChange={() =>
          scrollViewRef.current?.scrollToEnd({ animated: true })
        }
      />

      {isTyping && (
        <View;
          style={[styles.typingIndicator, { backgroundColor: theme.surface }]}
        >
          <Text style={[styles.typingText, { color: theme.textSecondary }]}>
            AI助手正在输入...
          </Text>
        </View>
      )}

      <View;
        style={[
          styles.inputContainer,
          { backgroundColor: theme.surface, borderColor: theme.border },
        ]}
      >
        <TextInput;
          style={[styles.textInput, { color: theme.text }]}
          value={inputText}
          onChangeText={setInputText}
          placeholder="输入您的健康问题..."
          placeholderTextColor={theme.textSecondary}
          multiline;
          maxLength={500}
        />
        <TouchableOpacity;
          style={[styles.sendButton, { backgroundColor: theme.primary }]}
          onPress={() => handleSendMessage()}
          disabled={!inputText.trim()}
        >
          <Icon name="send" size={20} color={theme.surface} />
        </TouchableOpacity>
      </View>

      <View style={styles.quickActionsContainer}>
        <Text style={[styles.quickActionsTitle, { color: theme.text }]}>
          快捷操作
        </Text>
        <FlatList;
          data={quickActions}
          renderItem={renderQuickAction}
          keyExtractor={(item) => item.id}
          horizontal;
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.quickActionsList}
        />
      </View>
    </View>
  );

  const renderSuggestionsTab = () => (
    <ScrollView style={styles.suggestionsContainer}>
      <Text style={[styles.sectionTitle, { color: theme.text }]}>
        个性化健康建议
      </Text>
      <Text style={[styles.sectionSubtitle, { color: theme.textSecondary }]}>
        基于您的健康数据和生活习惯，为您推荐以下建议
      </Text>

      <FlatList;
        data={healthSuggestions}
        renderItem={renderSuggestion}
        keyExtractor={(item) => item.id}
        scrollEnabled={false}
        contentContainerStyle={styles.suggestionsList}
      />
    </ScrollView>
  );

  const renderAnalysisTab = () => (
    <ScrollView style={styles.analysisContainer}>
      <Text style={[styles.sectionTitle, { color: theme.text }]}>
        健康分析报告
      </Text>

      <View;
        style={[
          styles.analysisCard,
          { backgroundColor: theme.surface, borderColor: theme.border },
        ]}
      >
        <View style={styles.analysisHeader}>
          <Icon name="analytics" size={24} color={theme.primary} />
          <Text style={[styles.analysisTitle, { color: theme.text }]}>
            综合健康评分
          </Text>
        </View>
        <View style={styles.scoreContainer}>
          <Text style={[styles.scoreValue, { color: theme.primary }]}>85</Text>
          <Text style={[styles.scoreLabel, { color: theme.textSecondary }]}>
            分
          </Text>
        </View>
        <Text style={[styles.scoreDescription, { color: theme.textSecondary }]}>
          您的整体健康状况良好，建议继续保持现有的健康习惯
        </Text>
      </View>

      <View;
        style={[
          styles.analysisCard,
          { backgroundColor: theme.surface, borderColor: theme.border },
        ]}
      >
        <View style={styles.analysisHeader}>
          <Icon name="trending-up" size={24} color={theme.primary} />
          <Text style={[styles.analysisTitle, { color: theme.text }]}>
            健康趋势
          </Text>
        </View>
        <View style={styles.trendContainer}>
          <View style={styles.trendItem}>
            <Text style={[styles.trendLabel, { color: theme.textSecondary }]}>
              体重
            </Text>
            <Text style={[styles.trendValue, { color: '#4ECDC4' }]}>
              ↗ 稳定
            </Text>
          </View>
          <View style={styles.trendItem}>
            <Text style={[styles.trendLabel, { color: theme.textSecondary }]}>
              血压
            </Text>
            <Text style={[styles.trendValue, { color: '#4ECDC4' }]}>
              ↗ 改善
            </Text>
          </View>
          <View style={styles.trendItem}>
            <Text style={[styles.trendLabel, { color: theme.textSecondary }]}>
              睡眠
            </Text>
            <Text style={[styles.trendValue, { color: '#FFD93D' }]}>
              → 一般
            </Text>
          </View>
        </View>
      </View>

      <View;
        style={[
          styles.analysisCard,
          { backgroundColor: theme.surface, borderColor: theme.border },
        ]}
      >
        <View style={styles.analysisHeader}>
          <Icon name="lightbulb" size={24} color={theme.primary} />
          <Text style={[styles.analysisTitle, { color: theme.text }]}>
            AI洞察
          </Text>
        </View>
        <Text style={[styles.insightText, { color: theme.textSecondary }]}>
          根据您最近的健康数据分析，您的运动量有所增加，这对心血管健康很有益处。
          建议继续保持，同时注意补充水分和适当休息。
        </Text>
      </View>
    </ScrollView>
  );

  return (
    <SafeAreaView;
      style={[styles.container, { backgroundColor: theme.background }]}
    >
      <Animated.View style={[styles.content, { opacity: fadeAnim }]}>
        {/* Header */}
        <View;
          style={[
            styles.header,
            { backgroundColor: theme.surface, borderBottomColor: theme.border },
          ]}
        >
          <Text style={[styles.headerTitle, { color: theme.text }]}>
            AI健康助手
          </Text>
          <TouchableOpacity;
            style={[
              styles.headerButton,
              { backgroundColor: theme.primary + '20' },
            ]}
            onPress={() => Alert.alert('设置', '功能开发中...')}
          >
            <Icon name="settings" size={20} color={theme.primary} />
          </TouchableOpacity>
        </View>

        {/* Tab Navigation */}
        <View;
          style={[
            styles.tabContainer,
            { backgroundColor: theme.surface, borderBottomColor: theme.border },
          ]}
        >
          {[
            { key: 'chat', label: '智能问答', icon: 'chat' },
            { key: 'suggestions', label: '健康建议', icon: 'lightbulb' },
            { key: 'analysis', label: '健康分析', icon: 'analytics' },
          ].map(tab) => (
            <TouchableOpacity;
              key={tab.key}
              style={[
                styles.tab,
                activeTab === tab.key && {
                  borderBottomColor: theme.primary,
                  borderBottomWidth: 2,
                },
              ]}
              onPress={() => setActiveTab(tab.key as any)}
            >
              <Icon;
                name={tab.icon}
                size={20}
                color={
                  activeTab === tab.key ? theme.primary : theme.textSecondary;
                }
              />
              <Text;
                style={[
                  styles.tabLabel,
                  {
                    color:
                      activeTab === tab.key;
                        ? theme.primary;
                        : theme.textSecondary,
                  },
                ]}
              >
                {tab.label}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Tab Content */}
        <View style={styles.tabContent}>
          {activeTab === 'chat' && renderChatTab()}
          {activeTab === 'suggestions' && renderSuggestionsTab()}
          {activeTab === 'analysis' && renderAnalysisTab()}
        </View>
      </Animated.View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {,
  flex: 1,
  },
  content: {,
  flex: 1,
  },
  header: {,
  flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 15,
    borderBottomWidth: 1,
  },
  headerTitle: {,
  fontSize: 20,
    fontWeight: '600',
  },
  headerButton: {,
  width: 36,
    height: 36,
    borderRadius: 18,
    justifyContent: 'center',
    alignItems: 'center',
  },
  tabContainer: {,
  flexDirection: 'row',
    borderBottomWidth: 1,
  },
  tab: {,
  flex: 1,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 12,
    gap: 6,
  },
  tabLabel: {,
  fontSize: 14,
    fontWeight: '500',
  },
  tabContent: {,
  flex: 1,
  },
  chatContainer: {,
  flex: 1,
  },
  messagesList: {,
  flex: 1,
    paddingHorizontal: 16,
    paddingTop: 16,
  },
  messageContainer: {,
  flexDirection: 'row',
    marginBottom: 16,
    alignItems: 'flex-end',
  },
  userMessage: {,
  justifyContent: 'flex-end',
  },
  aiMessage: {,
  justifyContent: 'flex-start',
  },
  aiAvatar: {,
  width: 32,
    height: 32,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 8,
  },
  messageBubble: {,
  maxWidth: width * 0.75,
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 20,
  },
  messageText: {,
  fontSize: 16,
    lineHeight: 22,
  },
  messageTime: {,
  fontSize: 12,
    marginTop: 4,
  },
  typingIndicator: {,
  paddingHorizontal: 16,
    paddingVertical: 8,
    marginHorizontal: 16,
    borderRadius: 12,
    marginBottom: 8,
  },
  typingText: {,
  fontSize: 14,
    fontStyle: 'italic',
  },
  inputContainer: {,
  flexDirection: 'row',
    alignItems: 'flex-end',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderTopWidth: 1,
    gap: 12,
  },
  textInput: {,
  flex: 1,
    maxHeight: 100,
    fontSize: 16,
    paddingVertical: 8,
  },
  sendButton: {,
  width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  quickActionsContainer: {,
  paddingHorizontal: 16,
    paddingVertical: 12,
  },
  quickActionsTitle: {,
  fontSize: 16,
    fontWeight: '600',
    marginBottom: 12,
  },
  quickActionsList: {,
  gap: 12,
  },
  quickActionCard: {,
  width: 140,
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    alignItems: 'center',
  },
  quickActionIcon: {,
  width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 8,
  },
  quickActionTitle: {,
  fontSize: 14,
    fontWeight: '600',
    textAlign: 'center',
    marginBottom: 4,
  },
  quickActionDescription: {,
  fontSize: 12,
    textAlign: 'center',
    lineHeight: 16,
  },
  suggestionsContainer: {,
  flex: 1,
    padding: 16,
  },
  sectionTitle: {,
  fontSize: 20,
    fontWeight: '600',
    marginBottom: 8,
  },
  sectionSubtitle: {,
  fontSize: 14,
    lineHeight: 20,
    marginBottom: 20,
  },
  suggestionsList: {,
  gap: 12,
  },
  suggestionCard: {,
  padding: 16,
    borderRadius: 12,
    borderWidth: 1,
  },
  suggestionHeader: {,
  flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  suggestionIcon: {,
  width: 36,
    height: 36,
    borderRadius: 18,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  suggestionInfo: {,
  flex: 1,
  },
  suggestionCategory: {,
  fontSize: 12,
    fontWeight: '500',
    marginBottom: 2,
  },
  suggestionTitle: {,
  fontSize: 16,
    fontWeight: '600',
  },
  priorityBadge: {,
  paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  priorityText: {,
  fontSize: 12,
    fontWeight: '600',
  },
  suggestionDescription: {,
  fontSize: 14,
    lineHeight: 20,
  },
  analysisContainer: {,
  flex: 1,
    padding: 16,
  },
  analysisCard: {,
  padding: 20,
    borderRadius: 12,
    borderWidth: 1,
    marginBottom: 16,
  },
  analysisHeader: {,
  flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
    gap: 8,
  },
  analysisTitle: {,
  fontSize: 18,
    fontWeight: '600',
  },
  scoreContainer: {,
  flexDirection: 'row',
    alignItems: 'baseline',
    justifyContent: 'center',
    marginBottom: 12,
  },
  scoreValue: {,
  fontSize: 48,
    fontWeight: '700',
  },
  scoreLabel: {,
  fontSize: 18,
    marginLeft: 4,
  },
  scoreDescription: {,
  fontSize: 14,
    textAlign: 'center',
    lineHeight: 20,
  },
  trendContainer: {,
  gap: 12,
  },
  trendItem: {,
  flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  trendLabel: {,
  fontSize: 16,
  },
  trendValue: {,
  fontSize: 16,
    fontWeight: '600',
  },
  insightText: {,
  fontSize: 14,
    lineHeight: 22,
  },
});

export default AIHealthAssistantScreen;
