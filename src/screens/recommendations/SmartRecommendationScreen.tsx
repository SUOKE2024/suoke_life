import { useNavigation } from '@react-navigation/native';
import React, { useEffect, useRef, useState } from 'react';
import {
  Animated,
  Dimensions,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { Button } from '../../components/ui/Button';
import {
  borderRadius,
  colors,
  shadows,
  spacing,
  typography,
} from '../../constants/theme';

const { width: screenWidth } = Dimensions.get('window');

interface Recommendation {
  id: string;,
  type: 'diet' | 'exercise' | 'lifestyle' | 'medical' | 'mental';
  title: string;,
  description: string;
  priority: 'high' | 'medium' | 'low';,
  confidence: number;
  tags: string[];,
  actionable: boolean;
  estimatedTime?: string;
  difficulty?: 'easy' | 'medium' | 'hard';
  benefits: string[];,
  icon: string;
  color: string;
}

interface UserProfile {
  age: number;,
  gender: 'male' | 'female';
  healthGoals: string[];,
  currentConditions: string[];
  lifestyle: string;,
  activityLevel: string;
}

const SmartRecommendationScreen: React.FC = () => {
  const navigation = useNavigation();
  const [refreshing, setRefreshing] = useState(false);
  const [activeCategory, setActiveCategory] = useState<string>('all');
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [userProfile] = useState<UserProfile>({
    age: 28,
    gender: 'female',
    healthGoals: ['减重', '改善睡眠', '增强免疫力'],
    currentConditions: ['轻度焦虑', '颈椎不适'],
    lifestyle: '久坐办公',
    activityLevel: '轻度活跃',
  });

  // 动画值
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(50)).current;

  // 分类选项
  const categories = [
    { key: 'all', title: '全部', icon: 'view-grid', color: colors.primary },
    { key: 'diet', title: '饮食', icon: 'food-apple', color: colors.success },
    { key: 'exercise', title: '运动', icon: 'run', color: colors.warning },
    { key: 'lifestyle', title: '生活', icon: 'home-heart', color: colors.info },
    { key: 'medical', title: '医疗', icon: 'medical-bag', color: colors.error },
    { key: 'mental', title: '心理', icon: 'brain', color: colors.secondary },
  ];

  // 初始化动画
  useEffect() => {
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 800,
        useNativeDriver: true,
      }),
      Animated.timing(slideAnim, {
        toValue: 0,
        duration: 800,
        useNativeDriver: true,
      }),
    ]).start();

    loadRecommendations();
  }, []);

  // 加载推荐数据
  const loadRecommendations = async () => {
    // 模拟AI生成的个性化推荐
    const mockRecommendations: Recommendation[] = [
      {
        id: '1',
        type: 'diet',
        title: '增加富含镁的食物',
        description:
          '根据您的睡眠质量数据，建议增加富含镁的食物摄入，如坚果、绿叶蔬菜等，有助于改善睡眠质量。',
        priority: 'high',
        confidence: 92,
        tags: ['睡眠改善', '营养补充'],
        actionable: true,
        estimatedTime: '2-3周见效',
        difficulty: 'easy',
        benefits: ['改善睡眠质量', '缓解肌肉紧张', '稳定情绪'],
        icon: 'leaf',
        color: colors.success,
      },
      {
        id: '2',
        type: 'exercise',
        title: '颈椎保健操',
        description:
          '针对您的颈椎不适问题，推荐每日进行颈椎保健操，缓解长期伏案工作带来的颈椎压力。',
        priority: 'high',
        confidence: 88,
        tags: ['颈椎保健', '办公室运动'],
        actionable: true,
        estimatedTime: '每天10分钟',
        difficulty: 'easy',
        benefits: ['缓解颈椎疼痛', '改善血液循环', '预防颈椎病'],
        icon: 'neck',
        color: colors.warning,
      },
      {
        id: '3',
        type: 'mental',
        title: '正念冥想练习',
        description:
          '基于您的焦虑状况，建议进行正念冥想练习，有助于缓解压力，提升心理健康水平。',
        priority: 'medium',
        confidence: 85,
        tags: ['压力管理', '心理健康'],
        actionable: true,
        estimatedTime: '每天15分钟',
        difficulty: 'medium',
        benefits: ['减轻焦虑', '提升专注力', '改善情绪'],
        icon: 'meditation',
        color: colors.secondary,
      },
      {
        id: '4',
        type: 'lifestyle',
        title: '优化工作环境',
        description:
          '调整办公桌椅高度，使用人体工学设备，减少久坐对身体的不良影响。',
        priority: 'medium',
        confidence: 80,
        tags: ['人体工学', '办公健康'],
        actionable: true,
        estimatedTime: '立即实施',
        difficulty: 'easy',
        benefits: ['改善坐姿', '减少疲劳', '提高工作效率'],
        icon: 'desk',
        color: colors.info,
      },
      {
        id: '5',
        type: 'medical',
        title: '定期体检提醒',
        description:
          '建议每年进行一次全面体检，重点关注心血管健康和内分泌系统。',
        priority: 'low',
        confidence: 75,
        tags: ['预防医学', '健康监测'],
        actionable: true,
        estimatedTime: '年度安排',
        difficulty: 'easy',
        benefits: ['早期发现问题', '预防疾病', '健康管理'],
        icon: 'stethoscope',
        color: colors.error,
      },
    ];

    setRecommendations(mockRecommendations);
  };

  // 刷新数据
  const onRefresh = async () => {
    setRefreshing(true);
    await loadRecommendations();
    setRefreshing(false);
  };

  // 过滤推荐
  const filteredRecommendations = recommendations.filter(rec) => activeCategory === 'all' || rec.type === activeCategory;
  );

  // 获取优先级颜色
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return colors.error;
      case 'medium':
        return colors.warning;
      case 'low':
        return colors.success;
      default:
        return colors.textSecondary;
    }
  };

  // 获取难度文本
  const getDifficultyText = (difficulty?: string) => {
    switch (difficulty) {
      case 'easy':
        return '简单';
      case 'medium':
        return '中等';
      case 'hard':
        return '困难';
      default:
        return '';
    }
  };

  // 渲染分类标签
  const renderCategories = () => (
    <ScrollView;
      horizontal;
      showsHorizontalScrollIndicator={false}
      style={styles.categoriesContainer}
      contentContainerStyle={styles.categoriesContent}
    >
      {categories.map(category) => (
        <TouchableOpacity;
          key={category.key}
          style={[
            styles.categoryButton,
            activeCategory === category.key && styles.activeCategoryButton,
            { borderColor: category.color },
          ]}
          onPress={() => setActiveCategory(category.key)}
        >
          <Icon;
            name={category.icon}
            size={20}
            color={
              activeCategory === category.key ? colors.white : category.color;
            }
          />
          <Text;
            style={[
              styles.categoryText,
              activeCategory === category.key && styles.activeCategoryText,
              {
                color:
                  activeCategory === category.key;
                    ? colors.white;
                    : category.color,
              },
            ]}
          >
            {category.title}
          </Text>
        </TouchableOpacity>
      ))}
    </ScrollView>
  );

  // 渲染推荐卡片
  const renderRecommendationCard = (
    recommendation: Recommendation,
    index: number;
  ) => (
    <Animated.View;
      key={recommendation.id}
      style={[
        styles.recommendationCard,
        {
          opacity: fadeAnim,
          transform: [{ translateY: slideAnim }],
        },
      ]}
    >
      {/* 卡片头部 */}
      <View style={styles.cardHeader}>
        <View;
          style={[
            styles.iconContainer,
            { backgroundColor: recommendation.color + '20' },
          ]}
        >
          <Icon;
            name={recommendation.icon}
            size={24}
            color={recommendation.color}
          />
        </View>
        <View style={styles.headerInfo}>
          <View style={styles.titleRow}>
            <Text style={styles.cardTitle}>{recommendation.title}</Text>
            <View;
              style={[
                styles.priorityBadge,
                { backgroundColor: getPriorityColor(recommendation.priority) },
              ]}
            >
              <Text style={styles.priorityText}>
                {recommendation.priority === 'high'
                  ? '高'
                  : recommendation.priority === 'medium'
                    ? '中'
                    : '低'}
              </Text>
            </View>
          </View>
          <View style={styles.metaInfo}>
            <Text style={styles.confidenceText}>
              可信度: {recommendation.confidence}%
            </Text>
            {recommendation.difficulty && (
              <Text style={styles.difficultyText}>
                难度: {getDifficultyText(recommendation.difficulty)}
              </Text>
            )}
          </View>
        </View>
      </View>

      {/* 描述 */}
      <Text style={styles.description}>{recommendation.description}</Text>

      {/* 标签 */}
      <View style={styles.tagsContainer}>
        {recommendation.tags.map(tag, tagIndex) => (
          <View key={tagIndex} style={styles.tag}>
            <Text style={styles.tagText}>{tag}</Text>
          </View>
        ))}
      </View>

      {/* 预期效果 */}
      <View style={styles.benefitsContainer}>
        <Text style={styles.benefitsTitle}>预期效果：</Text>
        {recommendation.benefits.slice(0, 2).map(benefit, benefitIndex) => (
          <View key={benefitIndex} style={styles.benefitItem}>
            <Icon name="check-circle" size={14} color={colors.success} />
            <Text style={styles.benefitText}>{benefit}</Text>
          </View>
        ))}
      </View>

      {/* 时间信息 */}
      {recommendation.estimatedTime && (
        <View style={styles.timeInfo}>
          <Icon name="clock-outline" size={16} color={colors.textSecondary} />
          <Text style={styles.timeText}>{recommendation.estimatedTime}</Text>
        </View>
      )}

      {/* 操作按钮 */}
      <View style={styles.cardActions}>
        <Button;
          title="查看详情"
          onPress={() => {
            /* 查看详情 */
          }}
        />
        <Button;
          title="开始执行"
          onPress={() => {
            /* 开始执行 */
          }}
        />
      </View>
    </Animated.View>
  );

  // 渲染用户画像
  const renderUserProfile = () => (
    <View style={styles.profileContainer}>
      <Text style={styles.profileTitle}>个人画像</Text>
      <View style={styles.profileContent}>
        <View style={styles.profileItem}>
          <Icon name="account" size={16} color={colors.primary} />
          <Text style={styles.profileText}>
            {userProfile.age}岁{' '}
            {userProfile.gender === 'female' ? '女性' : '男性'}
          </Text>
        </View>
        <View style={styles.profileItem}>
          <Icon name="target" size={16} color={colors.primary} />
          <Text style={styles.profileText}>
            目标: {userProfile.healthGoals.join('、')}
          </Text>
        </View>
        <View style={styles.profileItem}>
          <Icon name="run" size={16} color={colors.primary} />
          <Text style={styles.profileText}>
            活跃度: {userProfile.activityLevel}
          </Text>
        </View>
      </View>
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      {/* 头部 */}
      <View style={styles.header}>
        <TouchableOpacity;
          style={styles.backButton}
          onPress={() => navigation.goBack()}
        >
          <Icon name="arrow-left" size={24} color={colors.text} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>智能推荐</Text>
        <TouchableOpacity style={styles.settingsButton}>
          <Icon name="tune" size={24} color={colors.text} />
        </TouchableOpacity>
      </View>

      <ScrollView;
        style={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {/* 用户画像 */}
        {renderUserProfile()}

        {/* 分类标签 */}
        {renderCategories()}

        {/* 推荐列表 */}
        <View style={styles.recommendationsContainer}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>
              为您推荐 ({filteredRecommendations.length})
            </Text>
            <TouchableOpacity>
              <Text style={styles.refreshText}>刷新推荐</Text>
            </TouchableOpacity>
          </View>

          {filteredRecommendations.map(renderRecommendationCard)}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {,
  flex: 1,
    backgroundColor: colors.background,
  },
  header: {,
  flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    backgroundColor: colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  backButton: {,
  width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.gray100,
    justifyContent: 'center',
    alignItems: 'center',
  },
  headerTitle: {,
  fontSize: typography.fontSize.lg,
    fontWeight: '600' as const,
    color: colors.text,
  },
  settingsButton: {,
  width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.gray100,
    justifyContent: 'center',
    alignItems: 'center',
  },
  content: {,
  flex: 1,
  },
  profileContainer: {,
  backgroundColor: colors.surface,
    margin: spacing.lg,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    ...shadows.sm,
  },
  profileTitle: {,
  fontSize: typography.fontSize.base,
    fontWeight: '600' as const,
    color: colors.text,
    marginBottom: spacing.md,
  },
  profileContent: {,
  gap: spacing.sm,
  },
  profileItem: {,
  flexDirection: 'row',
    alignItems: 'center',
  },
  profileText: {,
  fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    marginLeft: spacing.sm,
  },
  categoriesContainer: {,
  marginBottom: spacing.lg,
  },
  categoriesContent: {,
  paddingHorizontal: spacing.lg,
    gap: spacing.sm,
  },
  categoryButton: {,
  flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.full,
    borderWidth: 1,
    backgroundColor: colors.surface,
  },
  activeCategoryButton: {,
  backgroundColor: colors.primary,
  },
  categoryText: {,
  fontSize: typography.fontSize.sm,
    marginLeft: spacing.xs,
  },
  activeCategoryText: {,
  color: colors.white,
  },
  recommendationsContainer: {,
  paddingHorizontal: spacing.lg,
  },
  sectionHeader: {,
  flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.lg,
  },
  sectionTitle: {,
  fontSize: typography.fontSize.lg,
    fontWeight: '600' as const,
    color: colors.text,
  },
  refreshText: {,
  fontSize: typography.fontSize.sm,
    color: colors.primary,
  },
  recommendationCard: {,
  backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    marginBottom: spacing.lg,
    ...shadows.sm,
  },
  cardHeader: {,
  flexDirection: 'row',
    marginBottom: spacing.md,
  },
  iconContainer: {,
  width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.md,
  },
  headerInfo: {,
  flex: 1,
  },
  titleRow: {,
  flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: spacing.xs,
  },
  cardTitle: {,
  fontSize: typography.fontSize.base,
    fontWeight: '600' as const,
    color: colors.text,
    flex: 1,
    marginRight: spacing.sm,
  },
  priorityBadge: {,
  paddingHorizontal: spacing.xs,
    paddingVertical: 2,
    borderRadius: borderRadius.sm,
  },
  priorityText: {,
  fontSize: typography.fontSize.xs,
    color: colors.white,
    fontWeight: '600' as const,
  },
  metaInfo: {,
  flexDirection: 'row',
    gap: spacing.md,
  },
  confidenceText: {,
  fontSize: typography.fontSize.xs,
    color: colors.textSecondary,
  },
  difficultyText: {,
  fontSize: typography.fontSize.xs,
    color: colors.textSecondary,
  },
  description: {,
  fontSize: typography.fontSize.sm,
    color: colors.text,
    lineHeight: 20,
    marginBottom: spacing.md,
  },
  tagsContainer: {,
  flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.xs,
    marginBottom: spacing.md,
  },
  tag: {,
  backgroundColor: colors.gray100,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: borderRadius.sm,
  },
  tagText: {,
  fontSize: typography.fontSize.xs,
    color: colors.textSecondary,
  },
  benefitsContainer: {,
  marginBottom: spacing.md,
  },
  benefitsTitle: {,
  fontSize: typography.fontSize.sm,
    fontWeight: '600' as const,
    color: colors.text,
    marginBottom: spacing.xs,
  },
  benefitItem: {,
  flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.xs,
  },
  benefitText: {,
  fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    marginLeft: spacing.xs,
  },
  timeInfo: {,
  flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  timeText: {,
  fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    marginLeft: spacing.xs,
  },
  cardActions: {,
  flexDirection: 'row',
    justifyContent: 'space-between',
    gap: spacing.sm,
  },
  actionButton: {,
  flex: 1,
  },
});

export default SmartRecommendationScreen;
