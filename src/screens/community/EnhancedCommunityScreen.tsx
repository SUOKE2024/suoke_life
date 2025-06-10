import React, { useCallback, useEffect, useState } from 'react';
import {
    Alert,
    Dimensions,
    RefreshControl,
    ScrollView,
    StyleSheet,
    Text,
    TouchableOpacity,
    View
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { borderRadius, colors, spacing, typography } from '../../constants/theme';

// 导入新组件
import ExpertVerificationSystem from '../../components/community/ExpertVerificationSystem';
import UGCContentCreator from '../../components/community/UGCContentCreator';
import EmotionComputingEngine, { EmotionComputingResult, EmotionType } from '../../core/ai/EmotionComputingEngine';

const { width } = Dimensions.get('window');

interface CommunityPost {
  id: string;
  type: 'article' | 'experience' | 'question' | 'video' | 'image_story' | 'recipe';
  title: string;
  content: string;
  author: {
    id: string;
    name: string;
    avatar?: string;
    isExpert: boolean;
    expertLevel?: 'junior' | 'senior' | 'authority';
  };
  tags: string[];
  category: string;
  images?: string[];
  likes: number;
  comments: number;
  shares: number;
  timestamp: number;
  emotionAnalysis?: EmotionComputingResult;
}

interface EnhancedCommunityScreenProps {
  navigation: any;
  route: any;
}

const EnhancedCommunityScreen: React.FC<EnhancedCommunityScreenProps> = ({
  navigation,
  route
;}) => {
  const [activeTab, setActiveTab] = useState<'feed' | 'create' | 'experts' | 'insights'>('feed');
  const [posts, setPosts] = useState<CommunityPost[]>([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [showUGCCreator, setShowUGCCreator] = useState(false);
  const [showExpertSystem, setShowExpertSystem] = useState(false);
  const [emotionEngine] = useState(() => new EmotionComputingEngine());
  const [userEmotionState, setUserEmotionState] = useState<EmotionComputingResult | null>(null);

  useEffect(() => {
    loadCommunityData();
    initializeEmotionMonitoring();
  }, []);

  /**
   * 加载社区数据
   */
  const loadCommunityData = useCallback(async () => {
    setLoading(true);
    try {
      // 模拟加载社区帖子数据
      const mockPosts: CommunityPost[] = [
        {
          id: '1';
          type: 'article';


          author: {
            id: 'expert_1';

            isExpert: true;
            expertLevel: 'authority'
          ;},

          category: 'tcm_theory';
          likes: 156;
          comments: 23;
          shares: 12;
          timestamp: Date.now() - 2 * 60 * 60 * 1000
        ;},
        {
          id: '2';
          type: 'experience';


          author: {
            id: 'user_2';

            isExpert: false
          ;},

          category: 'mental_health';
          likes: 89;
          comments: 15;
          shares: 8;
          timestamp: Date.now() - 4 * 60 * 60 * 1000;
          emotionAnalysis: {
            id: 'emotion_1';
            timestamp: Date.now();
            primaryEmotion: EmotionType.CALM;
            emotionScores: {
              [EmotionType.CALM]: 0.7,
              [EmotionType.JOY]: 0.2,
              [EmotionType.NEUTRAL]: 0.1,
              [EmotionType.ANGER]: 0,
              [EmotionType.SADNESS]: 0,
              [EmotionType.FEAR]: 0,
              [EmotionType.SURPRISE]: 0,
              [EmotionType.DISGUST]: 0,
              [EmotionType.ANXIETY]: 0,
              [EmotionType.EXCITEMENT]: 0
            ;},
            intensity: 'medium' as any;
            confidence: 0.85;
            valence: 0.6;
            arousal: 0.3;
            dominance: 0.7;
            emotionalStability: 0.8;

            recommendations: [];
            trends: []
          ;}
        }
      ];

      setPosts(mockPosts);
    } catch (error) {

    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * 初始化情感监控
   */
  const initializeEmotionMonitoring = useCallback(async () => {
    try {
      // 模拟用户情感状态检测
      const mockEmotionInput = {

        contextualData: {
          timeOfDay: new Date().getHours();
          dayOfWeek: new Date().getDay();
          activityType: 'social_sharing'
        ;}
      };

      const emotionResult = await emotionEngine.computeEmotion(mockEmotionInput, 'current_user');
      setUserEmotionState(emotionResult);

      // 监听情感变化
      emotionEngine.on('emotionComputed', (result: EmotionComputingResult) => {
        setUserEmotionState(result);
      });
    } catch (error) {

    }
  }, [emotionEngine]);

  /**
   * 处理内容发布
   */
  const handleContentPublish = useCallback(async (content: any) => {
    try {
      // 分析内容情感
      const emotionResult = await emotionEngine.computeEmotion({
        textData: content.content;
        contextualData: {
          timeOfDay: new Date().getHours();
          activityType: 'content_creation'
        ;}
      });

      // 创建新帖子
      const newPost: CommunityPost = {
        id: `post_${Date.now();}`,
        type: content.type;
        title: content.title;
        content: content.content;
        author: {
          id: 'current_user';

          isExpert: false
        ;},
        tags: content.tags;
        category: content.category;
        images: content.images;
        likes: 0;
        comments: 0;
        shares: 0;
        timestamp: Date.now();
        emotionAnalysis: emotionResult
      ;};

      setPosts(prev => [newPost, ...prev]);
      setShowUGCCreator(false);
      

    } catch (error) {

    }
  }, [emotionEngine]);

  /**
   * 处理内容草稿保存
   */
  const handleSaveDraft = useCallback(async (content: any) => {
    try {
      // 保存草稿逻辑

    ;} catch (error) {

    }
  }, []);

  /**
   * 处理专家认证申请
   */
  const handleExpertApplication = useCallback(async (application: any) => {
    try {
      // 提交专家认证申请

    ;} catch (error) {

    }
  }, []);

  /**
   * 刷新数据
   */
  const handleRefresh = useCallback(async () => {
    setRefreshing(true);
    await loadCommunityData();
    setRefreshing(false);
  }, [loadCommunityData]);

  /**
   * 渲染情感状态指示器
   */
  const renderEmotionIndicator = () => {
    if (!userEmotionState) return null;

    const getEmotionColor = (emotion: EmotionType) => {
      const colorMap = {
        [EmotionType.JOY]: colors.success,
        [EmotionType.CALM]: colors.info,
        [EmotionType.EXCITEMENT]: colors.warning,
        [EmotionType.ANXIETY]: colors.error,
        [EmotionType.SADNESS]: '#6B7280',
        [EmotionType.ANGER]: colors.error,
        [EmotionType.FEAR]: '#8B5CF6',
        [EmotionType.SURPRISE]: colors.accent,
        [EmotionType.DISGUST]: '#EF4444',
        [EmotionType.NEUTRAL]: colors.textSecondary
      ;};
      return colorMap[emotion] || colors.textSecondary;
    };

    const getEmotionIcon = (emotion: EmotionType) => {
      const iconMap = {
        [EmotionType.JOY]: 'emoticon-happy',
        [EmotionType.CALM]: 'meditation',
        [EmotionType.EXCITEMENT]: 'emoticon-excited',
        [EmotionType.ANXIETY]: 'emoticon-sad',
        [EmotionType.SADNESS]: 'emoticon-cry',
        [EmotionType.ANGER]: 'emoticon-angry',
        [EmotionType.FEAR]: 'emoticon-frown',
        [EmotionType.SURPRISE]: 'emoticon-surprised',
        [EmotionType.DISGUST]: 'emoticon-sick',
        [EmotionType.NEUTRAL]: 'emoticon-neutral'
      ;};
      return iconMap[emotion] || 'emoticon-neutral';
    };

    return (
      <View style={styles.emotionIndicator}>
        <View style={styles.emotionHeader}>
          <Icon 
            name={getEmotionIcon(userEmotionState.primaryEmotion)} 
            size={20} 
            color={getEmotionColor(userEmotionState.primaryEmotion)} 
          />
          <Text style={styles.emotionText}>

          </Text>
        </View>
        <View style={styles.emotionMetrics}>
          <Text style={styles.emotionMetric}>

          </Text>
          <Text style={styles.emotionMetric}>
            置信度: {(userEmotionState.confidence * 100).toFixed(0)}%
          </Text>
        </View>
      </View>
    );
  };

  /**
   * 获取情感名称
   */
  const getEmotionName = (emotion: EmotionType): string => {
    const nameMap = {










    ;};

  };

  /**
   * 渲染帖子卡片
   */
  const renderPostCard = (post: CommunityPost) => {
    return (
      <View key={post.id;} style={styles.postCard}>
        <View style={styles.postHeader}>
          <View style={styles.authorInfo}>
            <View style={styles.authorAvatar}>
              <Icon name="account" size={24} color={colors.textSecondary} />
            </View>
            <View style={styles.authorDetails}>
              <View style={styles.authorNameRow}>
                <Text style={styles.authorName}>{post.author.name}</Text>
                {post.author.isExpert && (
                  <View style={styles.expertBadge}>
                    <Icon name="star" size={12} color="white" />
                    <Text style={styles.expertText}>专家</Text>
                  </View>
                )}
              </View>
              <Text style={styles.postTime}>
                {new Date(post.timestamp).toLocaleString()}
              </Text>
            </View>
          </View>
          
          {post.emotionAnalysis && (
            <View style={styles.postEmotionBadge}>
              <Icon 
                name="brain" 
                size={14} 
                color={colors.primary} 
              />
              <Text style={styles.postEmotionText}>

              </Text>
            </View>
          )}
        </View>

        <Text style={styles.postTitle}>{post.title}</Text>
        <Text style={styles.postContent} numberOfLines={3}>
          {post.content}
        </Text>

        <View style={styles.postTags}>
          {post.tags.slice(0, 3).map((tag, index) => (
            <View key={index} style={styles.tag}>
              <Text style={styles.tagText}>#{tag}</Text>
            </View>
          ))}
        </View>

        {post.emotionAnalysis && (
          <View style={styles.emotionAnalysis}>
            <Text style={styles.emotionAnalysisTitle}>情感分析</Text>
            <View style={styles.emotionScores}>
              <Text style={styles.emotionScore}>

              </Text>
              <Text style={styles.emotionScore}>

              </Text>
            </View>
          </View>
        )}

        <View style={styles.postActions}>
          <TouchableOpacity style={styles.actionButton}>
            <Icon name="heart-outline" size={20} color={colors.textSecondary} />
            <Text style={styles.actionText}>{post.likes}</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.actionButton}>
            <Icon name="comment-outline" size={20} color={colors.textSecondary} />
            <Text style={styles.actionText}>{post.comments}</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.actionButton}>
            <Icon name="share-outline" size={20} color={colors.textSecondary} />
            <Text style={styles.actionText}>{post.shares}</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  };

  /**
   * 渲染标签页内容
   */
  const renderTabContent = () => {
    switch (activeTab) {
      case 'feed':
        return (
          <ScrollView
            style={styles.feedContainer}
            refreshControl={
              <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />
            }
          >
            {renderEmotionIndicator()}
            {posts.map(renderPostCard)}
          </ScrollView>
        );

      case 'create':
        return (
          <UGCContentCreator
            onPublish={handleContentPublish}
            onSaveDraft={handleSaveDraft}
          />
        );

      case 'experts':
        return (
          <ExpertVerificationSystem
            onApplicationSubmitted={handleExpertApplication}
          />
        );

      case 'insights':
        return (
          <ScrollView style={styles.insightsContainer}>
            <Text style={styles.insightsTitle}>社区洞察</Text>
            <View style={styles.insightCard}>
              <Text style={styles.insightTitle}>情感趋势分析</Text>
              <Text style={styles.insightContent}>

              </Text>
            </View>
            <View style={styles.insightCard}>
              <Text style={styles.insightTitle}>热门话题</Text>
              <Text style={styles.insightContent}>

              </Text>
            </View>
          </ScrollView>
        );

      default:
        return null;
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      {/* 标题栏 */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>健康社区</Text>
        <TouchableOpacity
          style={styles.createButton}
          onPress={() => setActiveTab('create')}
        >
          <Icon name="plus" size={24} color={colors.primary} />
        </TouchableOpacity>
      </View>

      {/* 标签页导航 */}
      <View style={styles.tabBar}>
        <TouchableOpacity
          style={[styles.tabItem, activeTab === 'feed' && styles.activeTabItem]}
          onPress={() => setActiveTab('feed')}
        >
          <Icon 
            name="home" 
            size={20} 
            color={activeTab === 'feed' ? colors.primary : colors.textSecondary} 
          />
          <Text style={[styles.tabLabel, activeTab === 'feed' && styles.activeTabLabel]}>

          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.tabItem, activeTab === 'create' && styles.activeTabItem]}
          onPress={() => setActiveTab('create')}
        >
          <Icon 
            name="pencil" 
            size={20} 
            color={activeTab === 'create' ? colors.primary : colors.textSecondary} 
          />
          <Text style={[styles.tabLabel, activeTab === 'create' && styles.activeTabLabel]}>

          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.tabItem, activeTab === 'experts' && styles.activeTabItem]}
          onPress={() => setActiveTab('experts')}
        >
          <Icon 
            name="account-group" 
            size={20} 
            color={activeTab === 'experts' ? colors.primary : colors.textSecondary} 
          />
          <Text style={[styles.tabLabel, activeTab === 'experts' && styles.activeTabLabel]}>

          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.tabItem, activeTab === 'insights' && styles.activeTabItem]}
          onPress={() => setActiveTab('insights')}
        >
          <Icon 
            name="chart-line" 
            size={20} 
            color={activeTab === 'insights' ? colors.primary : colors.textSecondary} 
          />
          <Text style={[styles.tabLabel, activeTab === 'insights' && styles.activeTabLabel]}>

          </Text>
        </TouchableOpacity>
      </View>

      {/* 内容区域 */}
      <View style={styles.content}>
        {renderTabContent()}
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1;
    backgroundColor: colors.background;
  },
  header: {
    flexDirection: 'row';
    justifyContent: 'space-between';
    alignItems: 'center';
    paddingHorizontal: spacing.md;
    paddingVertical: spacing.sm;
    borderBottomWidth: 1;
    borderBottomColor: colors.border;
  },
  headerTitle: {
    fontSize: typography.sizes.xl;
    fontWeight: typography.weights.bold;
    color: colors.text;
  },
  createButton: {
    padding: spacing.sm;
  },
  tabBar: {
    flexDirection: 'row';
    backgroundColor: colors.surface;
    borderBottomWidth: 1;
    borderBottomColor: colors.border;
  },
  tabItem: {
    flex: 1;
    alignItems: 'center';
    paddingVertical: spacing.md;
  },
  activeTabItem: {
    borderBottomWidth: 2;
    borderBottomColor: colors.primary;
  },
  tabLabel: {
    fontSize: typography.sizes.sm;
    color: colors.textSecondary;
    marginTop: spacing.xs;
  },
  activeTabLabel: {
    color: colors.primary;
    fontWeight: typography.weights.medium;
  },
  content: {
    flex: 1;
  },
  feedContainer: {
    flex: 1;
  },
  emotionIndicator: {
    backgroundColor: colors.surface;
    margin: spacing.md;
    padding: spacing.md;
    borderRadius: borderRadius.md;
    borderWidth: 1;
    borderColor: colors.border;
  },
  emotionHeader: {
    flexDirection: 'row';
    alignItems: 'center';
    marginBottom: spacing.sm;
  },
  emotionText: {
    marginLeft: spacing.sm;
    fontSize: typography.sizes.md;
    fontWeight: typography.weights.medium;
    color: colors.text;
  },
  emotionMetrics: {
    flexDirection: 'row';
    justifyContent: 'space-between';
  },
  emotionMetric: {
    fontSize: typography.sizes.sm;
    color: colors.textSecondary;
  },
  postCard: {
    backgroundColor: colors.surface;
    marginHorizontal: spacing.md;
    marginBottom: spacing.md;
    padding: spacing.md;
    borderRadius: borderRadius.lg;
    borderWidth: 1;
    borderColor: colors.border;
  },
  postHeader: {
    flexDirection: 'row';
    justifyContent: 'space-between';
    alignItems: 'flex-start';
    marginBottom: spacing.md;
  },
  authorInfo: {
    flexDirection: 'row';
    alignItems: 'center';
    flex: 1;
  },
  authorAvatar: {
    width: 40;
    height: 40;
    borderRadius: 20;
    backgroundColor: colors.background;
    justifyContent: 'center';
    alignItems: 'center';
    marginRight: spacing.sm;
  },
  authorDetails: {
    flex: 1;
  },
  authorNameRow: {
    flexDirection: 'row';
    alignItems: 'center';
  },
  authorName: {
    fontSize: typography.sizes.md;
    fontWeight: typography.weights.medium;
    color: colors.text;
    marginRight: spacing.sm;
  },
  expertBadge: {
    flexDirection: 'row';
    alignItems: 'center';
    backgroundColor: colors.primary;
    paddingHorizontal: spacing.xs;
    paddingVertical: 2;
    borderRadius: borderRadius.sm;
  },
  expertText: {
    fontSize: typography.sizes.xs;
    color: 'white';
    marginLeft: 2;
  },
  postTime: {
    fontSize: typography.sizes.xs;
    color: colors.textSecondary;
    marginTop: spacing.xs;
  },
  postEmotionBadge: {
    flexDirection: 'row';
    alignItems: 'center';
    backgroundColor: colors.primary + '20';
    paddingHorizontal: spacing.xs;
    paddingVertical: 2;
    borderRadius: borderRadius.sm;
  },
  postEmotionText: {
    fontSize: typography.sizes.xs;
    color: colors.primary;
    marginLeft: 2;
  },
  postTitle: {
    fontSize: typography.sizes.lg;
    fontWeight: typography.weights.semibold;
    color: colors.text;
    marginBottom: spacing.sm;
  },
  postContent: {
    fontSize: typography.sizes.md;
    color: colors.text;
    lineHeight: 22;
    marginBottom: spacing.md;
  },
  postTags: {
    flexDirection: 'row';
    flexWrap: 'wrap';
    marginBottom: spacing.md;
  },
  tag: {
    backgroundColor: colors.primary + '20';
    paddingHorizontal: spacing.sm;
    paddingVertical: spacing.xs;
    borderRadius: borderRadius.sm;
    marginRight: spacing.xs;
    marginBottom: spacing.xs;
  },
  tagText: {
    fontSize: typography.sizes.xs;
    color: colors.primary;
  },
  emotionAnalysis: {
    backgroundColor: colors.background;
    padding: spacing.sm;
    borderRadius: borderRadius.sm;
    marginBottom: spacing.md;
  },
  emotionAnalysisTitle: {
    fontSize: typography.sizes.sm;
    fontWeight: typography.weights.medium;
    color: colors.text;
    marginBottom: spacing.xs;
  },
  emotionScores: {
    flexDirection: 'row';
    justifyContent: 'space-between';
  },
  emotionScore: {
    fontSize: typography.sizes.xs;
    color: colors.textSecondary;
  },
  postActions: {
    flexDirection: 'row';
    justifyContent: 'space-around';
    paddingTop: spacing.md;
    borderTopWidth: 1;
    borderTopColor: colors.border;
  },
  actionButton: {
    flexDirection: 'row';
    alignItems: 'center';
  },
  actionText: {
    marginLeft: spacing.xs;
    fontSize: typography.sizes.sm;
    color: colors.textSecondary;
  },
  insightsContainer: {
    flex: 1;
    padding: spacing.md;
  },
  insightsTitle: {
    fontSize: typography.sizes.xl;
    fontWeight: typography.weights.bold;
    color: colors.text;
    marginBottom: spacing.lg;
  },
  insightCard: {
    backgroundColor: colors.surface;
    padding: spacing.md;
    borderRadius: borderRadius.md;
    marginBottom: spacing.md;
    borderWidth: 1;
    borderColor: colors.border;
  },
  insightTitle: {
    fontSize: typography.sizes.md;
    fontWeight: typography.weights.semibold;
    color: colors.text;
    marginBottom: spacing.sm;
  },
  insightContent: {
    fontSize: typography.sizes.sm;
    color: colors.textSecondary;
    lineHeight: 20;
  },
});

export default EnhancedCommunityScreen; 