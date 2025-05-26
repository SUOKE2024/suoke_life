import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  FlatList,
  Alert,
  TextInput,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from '../../components/common/Icon';
import { colors, spacing, fonts } from '../../constants/theme';
import AgentChatInterface, { AgentType } from '../../components/common/AgentChatInterface';

// 内容类型
type ContentType = 'article' | 'video' | 'course' | 'recipe' | 'wisdom' | 'theory';

// 分类类型
type CategoryType = 'tcm' | 'nutrition' | 'exercise' | 'mental' | 'lifestyle' | 'herbs' | 'acupoints';

// 内容项接口
interface ContentItem {
  id: string;
  title: string;
  subtitle: string;
  type: ContentType;
  category: CategoryType;
  author: string;
  readTime: string;
  likes: number;
  image: string;
  tags: string[];
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  featured?: boolean;
}

// 分类配置
const CATEGORIES = {
  tcm: {
    name: '中医理论',
    icon: 'leaf',
    color: '#34C759',
    description: '传统中医理论与现代应用',
  },
  nutrition: {
    name: '食疗养生',
    icon: 'food-apple',
    color: '#FF9500',
    description: '药食同源，食疗养生',
  },
  exercise: {
    name: '运动养生',
    icon: 'run',
    color: '#007AFF',
    description: '太极、八段锦等传统运动',
  },
  mental: {
    name: '心神调养',
    icon: 'brain',
    color: '#FF2D92',
    description: '情志调节与心神安宁',
  },
  lifestyle: {
    name: '起居养生',
    icon: 'home-heart',
    color: '#5856D6',
    description: '顺应自然的生活方式',
  },
  herbs: {
    name: '本草药材',
    icon: 'flower',
    color: '#8E44AD',
    description: '中药材识别与应用',
  },
  acupoints: {
    name: '经络穴位',
    icon: 'human-handsup',
    color: '#E74C3C',
    description: '经络穴位与按摩保健',
  },
};

// 老克的智慧内容
const LAOKE_WISDOM: ContentItem[] = [
  {
    id: 'wisdom_1',
    title: '春养肝，夏养心，秋养肺，冬养肾',
    subtitle: '四季养生的根本法则',
    type: 'wisdom',
    category: 'tcm',
    author: '老克',
    readTime: '8分钟',
    likes: 456,
    image: '🌸',
    tags: ['四季养生', '脏腑调养', '中医理论'],
    difficulty: 'beginner',
    featured: true,
  },
  {
    id: 'wisdom_2',
    title: '药食同源话山药',
    subtitle: '山药的药用价值与食疗方法',
    type: 'article',
    category: 'herbs',
    author: '老克',
    readTime: '6分钟',
    likes: 234,
    image: '🍠',
    tags: ['山药', '药食同源', '脾胃调养'],
    difficulty: 'intermediate',
  },
  {
    id: 'wisdom_3',
    title: '太极拳入门心法',
    subtitle: '以意导气，以气运身',
    type: 'video',
    category: 'exercise',
    author: '老克',
    readTime: '25分钟',
    likes: 789,
    image: '🥋',
    tags: ['太极拳', '气功', '养生运动'],
    difficulty: 'beginner',
    featured: true,
  },
  {
    id: 'wisdom_4',
    title: '足三里穴的妙用',
    subtitle: '常按足三里，胜吃老母鸡',
    type: 'course',
    category: 'acupoints',
    author: '老克',
    readTime: '12分钟',
    likes: 567,
    image: '🦵',
    tags: ['足三里', '穴位按摩', '保健养生'],
    difficulty: 'beginner',
  },
  {
    id: 'wisdom_5',
    title: '五行学说与体质调养',
    subtitle: '根据五行体质制定养生方案',
    type: 'theory',
    category: 'tcm',
    author: '老克',
    readTime: '15分钟',
    likes: 345,
    image: '☯️',
    tags: ['五行学说', '体质辨识', '个性化养生'],
    difficulty: 'advanced',
  },
  {
    id: 'wisdom_6',
    title: '枸杞菊花茶的养生秘密',
    subtitle: '明目养肝的经典搭配',
    type: 'recipe',
    category: 'nutrition',
    author: '老克',
    readTime: '4分钟',
    likes: 123,
    image: '🍵',
    tags: ['枸杞', '菊花', '明目养肝'],
    difficulty: 'beginner',
  },
];

// 热门话题
const HOT_TOPICS = [
  { id: '1', title: '春季养肝', count: 1234, icon: '🌱' },
  { id: '2', title: '中医体质', count: 987, icon: '⚖️' },
  { id: '3', title: '食疗养生', count: 756, icon: '🥗' },
  { id: '4', title: '穴位按摩', count: 654, icon: '👋' },
  { id: '5', title: '太极养生', count: 543, icon: '🥋' },
  { id: '6', title: '本草识别', count: 432, icon: '🌿' },
];

const ExploreScreen: React.FC = () => {
  const [selectedCategory, setSelectedCategory] = useState<CategoryType | 'all'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [agentChatVisible, setAgentChatVisible] = useState(false);
  const [accessibilityEnabled, setAccessibilityEnabled] = useState(false);

  // 过滤内容
  const filteredContent = LAOKE_WISDOM.filter((item) => {
    if (selectedCategory !== 'all' && item.category !== selectedCategory) {
      return false;
    }
    if (searchQuery && !item.title.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false;
    }
    return true;
  });

  // 精选内容
  const featuredContent = LAOKE_WISDOM.filter(item => item.featured);

  // 与老克对话
  const chatWithLaoke = () => {
    Alert.alert(
      '与老克对话',
      '老克是您的中医养生教育导师，拥有深厚的中医理论功底，可以为您提供：\n\n• 中医理论解读\n• 个性化养生指导\n• 食疗方案推荐\n• 穴位按摩教学\n• 传统运动指导\n\n是否开始对话？',
      [
        { text: '取消', style: 'cancel' },
        { text: '开始对话', onPress: () => startLaokeChat() }
      ]
    );
  };

  // 开始与老克对话
  const startLaokeChat = () => {
    setAgentChatVisible(true);
    console.log('Starting chat with Laoke agent');
  };

  // 查看内容详情
  const viewContent = (item: ContentItem) => {
    Alert.alert(
      item.title,
      `${item.subtitle}\n\n作者：${item.author}\n阅读时间：${item.readTime}\n难度：${getDifficultyText(item.difficulty)}\n\n标签：${item.tags.join(' • ')}\n\n${item.likes} 人觉得有用`,
      [
        { text: '收藏', onPress: () => console.log(`Bookmark ${item.id}`) },
        { text: '开始学习', onPress: () => startLearning(item) }
      ]
    );
  };

  // 开始学习
  const startLearning = (item: ContentItem) => {
    Alert.alert('开始学习', `正在为您准备《${item.title}》的学习内容...`);
    console.log(`Starting learning: ${item.id}`);
  };

  // 获取难度文本
  const getDifficultyText = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return '入门';
      case 'intermediate': return '进阶';
      case 'advanced': return '高级';
      default: return '未知';
    }
  };

  // 获取内容类型文本
  const getContentTypeText = (type: ContentType) => {
    switch (type) {
      case 'article': return '文章';
      case 'video': return '视频';
      case 'course': return '课程';
      case 'recipe': return '食谱';
      case 'wisdom': return '智慧';
      case 'theory': return '理论';
      default: return '内容';
    }
  };

  // 渲染分类标签
  const renderCategoryTab = (category: CategoryType | 'all') => {
    const isSelected = selectedCategory === category;
    const config = category === 'all'
      ? { name: '全部', icon: 'view-grid', color: colors.primary }
      : CATEGORIES[category];

    return (
      <TouchableOpacity
        key={category}
        style={[
          styles.categoryTab,
          isSelected && styles.selectedCategoryTab,
          isSelected && { backgroundColor: config.color + '20', borderColor: config.color },
        ]}
        onPress={() => setSelectedCategory(category)}
      >
        <Icon
          name={config.icon}
          size={16}
          color={isSelected ? config.color : colors.textSecondary}
        />
        <Text style={[styles.categoryTabText, isSelected && { color: config.color }]}>
          {config.name}
        </Text>
      </TouchableOpacity>
    );
  };

  // 渲染内容卡片
  const renderContentCard = ({ item }: { item: ContentItem }) => {
    const categoryConfig = CATEGORIES[item.category];

    return (
      <TouchableOpacity style={styles.contentCard} onPress={() => viewContent(item)}>
        <View style={styles.contentHeader}>
          <View style={styles.contentImageContainer}>
            <Text style={styles.contentEmoji}>{item.image}</Text>
            {item.featured && (
              <View style={styles.featuredBadge}>
                <Icon name="star" size={12} color="white" />
              </View>
            )}
          </View>
          <View style={styles.contentInfo}>
            <Text style={styles.contentTitle} numberOfLines={2}>{item.title}</Text>
            <Text style={styles.contentSubtitle} numberOfLines={1}>{item.subtitle}</Text>
            <View style={styles.contentMeta}>
              <Text style={styles.authorText}>👴 {item.author}</Text>
              <Text style={styles.readTimeText}>⏱️ {item.readTime}</Text>
            </View>
          </View>
        </View>

        <View style={styles.contentFooter}>
          <View style={styles.tagsContainer}>
            {item.tags.slice(0, 2).map((tag, index) => (
              <View key={index} style={[styles.tag, { backgroundColor: categoryConfig.color + '20' }]}>
                <Text style={[styles.tagText, { color: categoryConfig.color }]}>{tag}</Text>
              </View>
            ))}
          </View>
          <View style={styles.contentStats}>
            <View style={[styles.typeBadge, { backgroundColor: categoryConfig.color }]}>
              <Text style={styles.typeText}>{getContentTypeText(item.type)}</Text>
            </View>
            <View style={styles.likesContainer}>
              <Icon name="heart" size={14} color={colors.textSecondary} />
              <Text style={styles.likesText}>{item.likes}</Text>
            </View>
          </View>
        </View>
      </TouchableOpacity>
    );
  };

  // 渲染热门话题
  const renderHotTopic = (topic: typeof HOT_TOPICS[0], index: number) => (
    <TouchableOpacity key={topic.id} style={styles.hotTopicItem}>
      <Text style={styles.topicRank}>{index + 1}</Text>
      <Text style={styles.topicIcon}>{topic.icon}</Text>
      <View style={styles.topicInfo}>
        <Text style={styles.topicTitle}>{topic.title}</Text>
        <Text style={styles.topicCount}>{topic.count} 讨论</Text>
      </View>
      <Icon name="trending-up" size={16} color={colors.primary} />
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.container}>
      {/* 头部 */}
      <View style={styles.header}>
        <View>
          <Text style={styles.title}>健康探索</Text>
          <Text style={styles.subtitle}>跟随老克学习中医养生智慧</Text>
        </View>
        <TouchableOpacity style={styles.laokeChatButton} onPress={chatWithLaoke}>
          <Text style={styles.laokeChatEmoji}>👴</Text>
          <Text style={styles.laokeChatText}>老克</Text>
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        {/* 老克导师卡片 */}
        <TouchableOpacity style={styles.laokeCard} onPress={chatWithLaoke}>
          <View style={styles.laokeInfo}>
            <Text style={styles.laokeEmoji}>👴</Text>
            <View style={styles.laokeTextContainer}>
              <Text style={styles.laokeName}>老克 - 中医养生导师</Text>
              <Text style={styles.laokeDesc}>传承千年中医智慧，指导现代养生之道</Text>
              <Text style={styles.laokeQuote}>"上医治未病，中医治欲病，下医治已病"</Text>
            </View>
          </View>
          <View style={styles.onlineStatus}>
            <View style={styles.onlineDot} />
            <Text style={styles.onlineText}>在线</Text>
          </View>
        </TouchableOpacity>

        {/* 搜索框 */}
        <View style={styles.searchContainer}>
          <Icon name="magnify" size={20} color={colors.textSecondary} />
          <TextInput
            style={styles.searchInput}
            placeholder="搜索养生知识、中医理论..."
            value={searchQuery}
            onChangeText={setSearchQuery}
            placeholderTextColor={colors.textSecondary}
          />
        </View>

        {/* 精选内容 */}
        {featuredContent.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>🌟 精选推荐</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false}>
              {featuredContent.map(item => (
                <TouchableOpacity key={item.id} style={styles.featuredCard} onPress={() => viewContent(item)}>
                  <Text style={styles.featuredEmoji}>{item.image}</Text>
                  <Text style={styles.featuredTitle} numberOfLines={2}>{item.title}</Text>
                  <Text style={styles.featuredAuthor}>👴 {item.author}</Text>
                </TouchableOpacity>
              ))}
            </ScrollView>
          </View>
        )}

        {/* 热门话题 */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>🔥 热门话题</Text>
          <View style={styles.hotTopicsContainer}>
            {HOT_TOPICS.slice(0, 6).map(renderHotTopic)}
          </View>
        </View>

        {/* 分类标签 */}
        <ScrollView 
          horizontal 
          showsHorizontalScrollIndicator={false}
          style={styles.categoriesContainer}
          contentContainerStyle={styles.categoriesContent}
        >
          {renderCategoryTab('all')}
          {(Object.keys(CATEGORIES) as CategoryType[]).map(renderCategoryTab)}
        </ScrollView>

        {/* 内容列表 */}
        <View style={styles.contentSection}>
          <Text style={styles.sectionTitle}>
            📚 {selectedCategory === 'all' ? '全部内容' : CATEGORIES[selectedCategory as CategoryType]?.name}
          </Text>
          <FlatList
            data={filteredContent}
            keyExtractor={item => item.id}
            renderItem={renderContentCard}
            scrollEnabled={false}
            ItemSeparatorComponent={() => <View style={styles.separator} />}
          />
        </View>
      </ScrollView>

      {/* 老克对话界面 */}
      <AgentChatInterface
        visible={agentChatVisible}
        onClose={() => setAgentChatVisible(false)}
        agentType="laoke"
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
  laokeChatButton: {
    alignItems: 'center',
    padding: 8,
  },
  laokeChatEmoji: {
    fontSize: 24,
  },
  laokeChatText: {
    fontSize: 12,
    color: colors.primary,
    fontWeight: '600',
    marginTop: 2,
  },
  scrollView: {
    flex: 1,
  },
  laokeCard: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    margin: 15,
    padding: 15,
    backgroundColor: '#34C759' + '10',
    borderRadius: 12,
    borderLeftWidth: 4,
    borderLeftColor: '#34C759',
  },
  laokeInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  laokeEmoji: {
    fontSize: 32,
    marginRight: 12,
  },
  laokeTextContainer: {
    flex: 1,
  },
  laokeName: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.text,
    marginBottom: 4,
  },
  laokeDesc: {
    fontSize: 12,
    color: colors.textSecondary,
    marginBottom: 4,
  },
  laokeQuote: {
    fontSize: 11,
    color: '#34C759',
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
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    margin: 15,
    paddingHorizontal: 15,
    paddingVertical: 10,
    backgroundColor: colors.surface,
    borderRadius: 25,
  },
  searchInput: {
    flex: 1,
    marginLeft: 10,
    fontSize: 16,
    color: colors.text,
  },
  section: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: colors.text,
    marginHorizontal: 15,
    marginBottom: 10,
  },
  featuredCard: {
    width: 140,
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: 12,
    marginLeft: 15,
    alignItems: 'center',
  },
  featuredEmoji: {
    fontSize: 32,
    marginBottom: 8,
  },
  featuredTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.text,
    textAlign: 'center',
    marginBottom: 6,
  },
  featuredAuthor: {
    fontSize: 12,
    color: colors.textSecondary,
  },
  hotTopicsContainer: {
    paddingHorizontal: 15,
  },
  hotTopicItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    paddingHorizontal: 12,
    marginBottom: 6,
    backgroundColor: colors.surface,
    borderRadius: 8,
  },
  topicRank: {
    fontSize: 14,
    fontWeight: 'bold',
    color: colors.primary,
    width: 20,
  },
  topicIcon: {
    fontSize: 16,
    marginHorizontal: 8,
  },
  topicInfo: {
    flex: 1,
  },
  topicTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.text,
  },
  topicCount: {
    fontSize: 12,
    color: colors.textSecondary,
  },
  categoriesContainer: {
    maxHeight: 50,
  },
  categoriesContent: {
    paddingHorizontal: 15,
    paddingVertical: 10,
  },
  categoryTab: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 6,
    marginRight: 8,
    borderRadius: 15,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
  },
  selectedCategoryTab: {
    borderWidth: 1,
  },
  categoryTabText: {
    marginLeft: 4,
    fontSize: 12,
    color: colors.textSecondary,
  },
  contentSection: {
    paddingHorizontal: 15,
    paddingBottom: 20,
  },
  contentCard: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: 15,
    marginBottom: 10,
  },
  contentHeader: {
    flexDirection: 'row',
    marginBottom: 10,
  },
  contentImageContainer: {
    position: 'relative',
    marginRight: 12,
  },
  contentEmoji: {
    fontSize: 32,
  },
  featuredBadge: {
    position: 'absolute',
    top: -4,
    right: -4,
    backgroundColor: colors.primary,
    borderRadius: 8,
    width: 16,
    height: 16,
    justifyContent: 'center',
    alignItems: 'center',
  },
  contentInfo: {
    flex: 1,
  },
  contentTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.text,
    marginBottom: 4,
  },
  contentSubtitle: {
    fontSize: 14,
    color: colors.textSecondary,
    marginBottom: 6,
  },
  contentMeta: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  authorText: {
    fontSize: 12,
    color: colors.textSecondary,
  },
  readTimeText: {
    fontSize: 12,
    color: colors.textSecondary,
  },
  contentFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  tagsContainer: {
    flexDirection: 'row',
    flex: 1,
  },
  tag: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 10,
    marginRight: 6,
  },
  tagText: {
    fontSize: 10,
    fontWeight: '600',
  },
  contentStats: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  typeBadge: {
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 8,
    marginRight: 8,
  },
  typeText: {
    fontSize: 10,
    color: 'white',
    fontWeight: '600',
  },
  likesContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  likesText: {
    fontSize: 12,
    color: colors.textSecondary,
    marginLeft: 4,
  },
  separator: {
    height: 1,
    backgroundColor: colors.border,
    marginVertical: 5,
  },
});

export default ExploreScreen;
