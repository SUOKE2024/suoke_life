import { useNavigation } from '@react-navigation/native';
import React, { useEffect, useRef, useState } from 'react';
import {
  Animated,
  FlatList,
  RefreshControl,
  StyleSheet,
  Text,
  TextInput,
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

interface Post {
  id: string;,
  author: {
    id: string;,
  name: string;
    avatar: string;,
  level: string;
    verified: boolean;
  };
  content: string;
  images?: string[];
  topic: string;,
  tags: string[];
  likes: number;,
  comments: number;
  shares: number;,
  timestamp: string;
  liked: boolean;,
  bookmarked: boolean;
}

interface Topic {
  id: string;,
  name: string;
  icon: string;,
  color: string;
  posts: number;,
  followers: number;
  trending: boolean;
}

interface Expert {
  id: string;,
  name: string;
  avatar: string;,
  title: string;
  specialty: string;,
  rating: number;
  consultations: number;,
  online: boolean;
}

const CommunityInteractionScreen: React.FC = () => {
  const navigation = useNavigation();
  const [refreshing, setRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState<
    'feed' | 'topics' | 'experts' | 'my'
  >('feed');
  const [searchQuery, setSearchQuery] = useState('');

  // 动画值
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(50)).current;

  // 热门话题
  const [topics] = useState<Topic[]>([
    {
      id: '1',
      name: '减肥心得',
      icon: 'scale-bathroom',
      color: colors.primary,
      posts: 1234,
      followers: 5678,
      trending: true,
    },
    {
      id: '2',
      name: '运动健身',
      icon: 'dumbbell',
      color: colors.success,
      posts: 2345,
      followers: 8901,
      trending: true,
    },
    {
      id: '3',
      name: '营养饮食',
      icon: 'food-apple',
      color: colors.warning,
      posts: 3456,
      followers: 7890,
      trending: false,
    },
    {
      id: '4',
      name: '心理健康',
      icon: 'brain',
      color: colors.info,
      posts: 1567,
      followers: 4321,
      trending: true,
    },
    {
      id: '5',
      name: '睡眠改善',
      icon: 'sleep',
      color: colors.secondary,
      posts: 987,
      followers: 2345,
      trending: false,
    },
  ]);

  // 专家列表
  const [experts] = useState<Expert[]>([
    {
      id: '1',
      name: '李医生',
      avatar: 'https://example.com/avatar1.jpg',
      title: '主任医师',
      specialty: '心血管内科',
      rating: 4.9,
      consultations: 1234,
      online: true,
    },
    {
      id: '2',
      name: '王营养师',
      avatar: 'https://example.com/avatar2.jpg',
      title: '高级营养师',
      specialty: '临床营养',
      rating: 4.8,
      consultations: 987,
      online: false,
    },
    {
      id: '3',
      name: '张教练',
      avatar: 'https://example.com/avatar3.jpg',
      title: '健身教练',
      specialty: '运动康复',
      rating: 4.7,
      consultations: 765,
      online: true,
    },
  ]);

  // 社区动态
  const [posts, setPosts] = useState<Post[]>([
    {
      id: '1',
      author: {,
  id: '1',
        name: '健康小达人',
        avatar: 'https://example.com/user1.jpg',
        level: 'Lv.5',
        verified: true,
      },
      content:
        '分享一下我的减肥心得！坚持3个月，成功减重15斤。主要是控制饮食+规律运动，每天记录体重和饮食，养成良好习惯最重要。',
      images: [
        'https://example.com/image1.jpg',
        'https://example.com/image2.jpg',
      ],
      topic: '减肥心得',
      tags: ['减肥', '饮食控制', '运动'],
      likes: 128,
      comments: 45,
      shares: 12,
      timestamp: '2小时前',
      liked: false,
      bookmarked: false,
    },
    {
      id: '2',
      author: {,
  id: '2',
        name: '运动爱好者',
        avatar: 'https://example.com/user2.jpg',
        level: 'Lv.3',
        verified: false,
      },
      content:
        '今天完成了5公里晨跑，感觉整个人都充满活力！坚持运动真的能改善心情，推荐大家都试试。',
      topic: '运动健身',
      tags: ['跑步', '晨练', '心情'],
      likes: 89,
      comments: 23,
      shares: 8,
      timestamp: '4小时前',
      liked: true,
      bookmarked: true,
    },
    {
      id: '3',
      author: {,
  id: '3',
        name: '营养师小美',
        avatar: 'https://example.com/user3.jpg',
        level: 'Lv.7',
        verified: true,
      },
      content:
        '秋季养生小贴士：多吃梨、银耳、百合等润燥食物，少吃辛辣刺激食品。记得多喝水，保持充足睡眠哦！',
      topic: '营养饮食',
      tags: ['秋季养生', '饮食建议', '健康'],
      likes: 156,
      comments: 67,
      shares: 34,
      timestamp: '6小时前',
      liked: false,
      bookmarked: false,
    },
  ]);

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
  }, []);

  // 刷新数据
  const onRefresh = async () => {
    setRefreshing(true);
    // 模拟数据加载
    setTimeout() => {
      setRefreshing(false);
    }, 1000);
  };

  // 点赞操作
  const handleLike = (postId: string) => {
    setPosts(prev) =>
      prev.map(post) =>
        post.id === postId;
          ? {
              ...post,
              liked: !post.liked,
              likes: post.liked ? post.likes - 1 : post.likes + 1,
            }
          : post;
      )
    );
  };

  // 收藏操作
  const handleBookmark = (postId: string) => {
    setPosts(prev) =>
      prev.map(post) =>
        post.id === postId ? { ...post, bookmarked: !post.bookmarked } : post;
      )
    );
  };

  // 渲染标签栏
  const renderTabs = () => {
    const tabs = [
      { key: 'feed', title: '动态', icon: 'home' },
      { key: 'topics', title: '话题', icon: 'pound' },
      { key: 'experts', title: '专家', icon: 'doctor' },
      { key: 'my', title: '我的', icon: 'account' },
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
                activeTab === tab.key && styles.activeTabText,
              ]}
            >
              {tab.title}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
    );
  };

  // 渲染搜索栏
  const renderSearchBar = () => (
    <View style={styles.searchContainer}>
      <View style={styles.searchBar}>
        <Icon name="magnify" size={20} color={colors.textSecondary} />
        <TextInput;
          style={styles.searchInput}
          placeholder="搜索话题、用户或内容..."
          value={searchQuery}
          onChangeText={setSearchQuery}
          placeholderTextColor={colors.textSecondary}
        />
      </View>
      <TouchableOpacity style={styles.publishButton}>
        <Icon name="plus" size={20} color={colors.white} />
      </TouchableOpacity>
    </View>
  );

  // 渲染动态卡片
  const renderPostCard = ({ item }: { item: Post }) => (
    <View style={styles.postCard}>
      {/* 用户信息 */}
      <View style={styles.postHeader}>
        <View style={styles.userInfo}>
          <View style={styles.avatar}>
            <Icon name="account" size={24} color={colors.primary} />
          </View>
          <View style={styles.userDetails}>
            <View style={styles.userNameRow}>
              <Text style={styles.userName}>{item.author.name}</Text>
              <Text style={styles.userLevel}>{item.author.level}</Text>
              {item.author.verified && (
                <Icon name="check-decagram" size={16} color={colors.primary} />
              )}
            </View>
            <Text style={styles.postTime}>{item.timestamp}</Text>
          </View>
        </View>
        <TouchableOpacity style={styles.moreButton}>
          <Icon name="dots-horizontal" size={20} color={colors.textSecondary} />
        </TouchableOpacity>
      </View>

      {/* 话题标签 */}
      <TouchableOpacity style={styles.topicTag}>
        <Text style={styles.topicText}>#{item.topic}</Text>
      </TouchableOpacity>

      {/* 内容 */}
      <Text style={styles.postContent}>{item.content}</Text>

      {/* 图片 */}
      {item.images && item.images.length > 0 && (
        <View style={styles.imageContainer}>
          {item.images.map(image, index) => (
            <View key={index} style={styles.imagePlaceholder}>
              <Icon name="image" size={32} color={colors.textSecondary} />
            </View>
          ))}
        </View>
      )}

      {/* 标签 */}
      <View style={styles.tagsContainer}>
        {item.tags.map(tag, index) => (
          <View key={index} style={styles.tag}>
            <Text style={styles.tagText}>{tag}</Text>
          </View>
        ))}
      </View>

      {/* 互动按钮 */}
      <View style={styles.actionBar}>
        <TouchableOpacity;
          style={styles.actionButton}
          onPress={() => handleLike(item.id)}
        >
          <Icon;
            name={item.liked ? 'heart' : 'heart-outline'}
            size={20}
            color={item.liked ? colors.error : colors.textSecondary}
          />
          <Text;
            style={[styles.actionText, item.liked && { color: colors.error }]}
          >
            {item.likes}
          </Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.actionButton}>
          <Icon name="comment-outline" size={20} color={colors.textSecondary} />
          <Text style={styles.actionText}>{item.comments}</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.actionButton}>
          <Icon name="share-outline" size={20} color={colors.textSecondary} />
          <Text style={styles.actionText}>{item.shares}</Text>
        </TouchableOpacity>

        <TouchableOpacity;
          style={styles.actionButton}
          onPress={() => handleBookmark(item.id)}
        >
          <Icon;
            name={item.bookmarked ? 'bookmark' : 'bookmark-outline'}
            size={20}
            color={item.bookmarked ? colors.warning : colors.textSecondary}
          />
        </TouchableOpacity>
      </View>
    </View>
  );

  // 渲染话题卡片
  const renderTopicCard = ({ item }: { item: Topic }) => (
    <TouchableOpacity style={styles.topicCard}>
      <View style={[styles.topicIcon, { backgroundColor: item.color + '20' }]}>
        <Icon name={item.icon} size={24} color={item.color} />
      </View>
      <View style={styles.topicInfo}>
        <View style={styles.topicHeader}>
          <Text style={styles.topicName}>{item.name}</Text>
          {item.trending && (
            <View style={styles.trendingBadge}>
              <Text style={styles.trendingText}>热门</Text>
            </View>
          )}
        </View>
        <Text style={styles.topicStats}>
          {item.posts} 帖子 • {item.followers} 关注
        </Text>
      </View>
      <TouchableOpacity style={styles.followButton}>
        <Text style={styles.followButtonText}>关注</Text>
      </TouchableOpacity>
    </TouchableOpacity>
  );

  // 渲染专家卡片
  const renderExpertCard = ({ item }: { item: Expert }) => (
    <TouchableOpacity style={styles.expertCard}>
      <View style={styles.expertHeader}>
        <View style={styles.expertAvatar}>
          <Icon name="doctor" size={24} color={colors.primary} />
          {item.online && <View style={styles.onlineIndicator} />}
        </View>
        <View style={styles.expertInfo}>
          <Text style={styles.expertName}>{item.name}</Text>
          <Text style={styles.expertTitle}>{item.title}</Text>
          <Text style={styles.expertSpecialty}>{item.specialty}</Text>
        </View>
        <View style={styles.expertStats}>
          <View style={styles.ratingContainer}>
            <Icon name="star" size={14} color={colors.warning} />
            <Text style={styles.rating}>{item.rating}</Text>
          </View>
          <Text style={styles.consultations}>{item.consultations} 咨询</Text>
        </View>
      </View>
      <View style={styles.expertActions}>
        <Button;
          title={item.online ? '立即咨询' : '预约咨询'}
          onPress={() => {
            /* 咨询专家 */
          }}
        />
      </View>
    </TouchableOpacity>
  );

  // 渲染内容
  const renderContent = () => {
    switch (activeTab) {
      case 'feed':
        return (
          <FlatList;
            data={posts}
            renderItem={renderPostCard}
            keyExtractor={(item) => item.id}
            showsVerticalScrollIndicator={false}
            refreshControl={
              <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
            }
          />
        );
      case 'topics':
        return (
          <FlatList;
            data={topics}
            renderItem={renderTopicCard}
            keyExtractor={(item) => item.id}
            showsVerticalScrollIndicator={false}
            refreshControl={
              <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
            }
          />
        );
      case 'experts':
        return (
          <FlatList;
            data={experts}
            renderItem={renderExpertCard}
            keyExtractor={(item) => item.id}
            showsVerticalScrollIndicator={false}
            refreshControl={
              <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
            }
          />
        );
      case 'my':
        return (
          <View style={styles.myContent}>
            <Text style={styles.myTitle}>我的社区</Text>
            <View style={styles.myStats}>
              <View style={styles.statItem}>
                <Text style={styles.statValue}>12</Text>
                <Text style={styles.statLabel}>发布</Text>
              </View>
              <View style={styles.statItem}>
                <Text style={styles.statValue}>89</Text>
                <Text style={styles.statLabel}>获赞</Text>
              </View>
              <View style={styles.statItem}>
                <Text style={styles.statValue}>34</Text>
                <Text style={styles.statLabel}>关注</Text>
              </View>
              <View style={styles.statItem}>
                <Text style={styles.statValue}>56</Text>
                <Text style={styles.statLabel}>粉丝</Text>
              </View>
            </View>
          </View>
        );
      default:
        return null;
    }
  };

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
        <Text style={styles.headerTitle}>健康社区</Text>
        <TouchableOpacity style={styles.notificationButton}>
          <Icon name="bell-outline" size={24} color={colors.text} />
          <View style={styles.notificationBadge}>
            <Text style={styles.notificationCount}>3</Text>
          </View>
        </TouchableOpacity>
      </View>

      {/* 搜索栏 */}
      {renderSearchBar()}

      {/* 标签栏 */}
      {renderTabs()}

      {/* 内容区域 */}
      <Animated.View;
        style={[
          styles.contentContainer,
          {
            opacity: fadeAnim,
            transform: [{ translateY: slideAnim }],
          },
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
  notificationButton: {,
  width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.gray100,
    justifyContent: 'center',
    alignItems: 'center',
    position: 'relative',
  },
  notificationBadge: {,
  position: 'absolute',
    top: 8,
    right: 8,
    width: 16,
    height: 16,
    borderRadius: 8,
    backgroundColor: colors.error,
    justifyContent: 'center',
    alignItems: 'center',
  },
  notificationCount: {,
  fontSize: 10,
    color: colors.white,
    fontWeight: '600' as const,
  },
  searchContainer: {,
  flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    backgroundColor: colors.surface,
    gap: spacing.md,
  },
  searchBar: {,
  flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.gray100,
    borderRadius: borderRadius.lg,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    gap: spacing.sm,
  },
  searchInput: {,
  flex: 1,
    fontSize: typography.fontSize.base,
    color: colors.text,
  },
  publishButton: {,
  width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
  },
  tabContainer: {,
  flexDirection: 'row',
    backgroundColor: colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  tab: {,
  flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: spacing.md,
    gap: spacing.xs,
  },
  activeTab: {,
  borderBottomWidth: 2,
    borderBottomColor: colors.primary,
  },
  tabText: {,
  fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
  },
  activeTabText: {,
  color: colors.primary,
    fontWeight: '600' as const,
  },
  contentContainer: {,
  flex: 1,
  },
  postCard: {,
  backgroundColor: colors.surface,
    marginHorizontal: spacing.lg,
    marginVertical: spacing.sm,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    ...shadows.sm,
  },
  postHeader: {,
  flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: spacing.md,
  },
  userInfo: {,
  flexDirection: 'row',
    alignItems: 'center',
  },
  avatar: {,
  width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.primary + '20',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.md,
  },
  userDetails: {,
  flex: 1,
  },
  userNameRow: {,
  flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs,
  },
  userName: {,
  fontSize: typography.fontSize.base,
    fontWeight: '600' as const,
    color: colors.text,
  },
  userLevel: {,
  fontSize: typography.fontSize.xs,
    color: colors.primary,
    backgroundColor: colors.primary + '20',
    paddingHorizontal: spacing.xs,
    paddingVertical: 2,
    borderRadius: borderRadius.sm,
  },
  postTime: {,
  fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    marginTop: 2,
  },
  moreButton: {,
  padding: spacing.xs,
  },
  topicTag: {,
  alignSelf: 'flex-start',
    marginBottom: spacing.sm,
  },
  topicText: {,
  fontSize: typography.fontSize.sm,
    color: colors.primary,
    fontWeight: '600' as const,
  },
  postContent: {,
  fontSize: typography.fontSize.base,
    color: colors.text,
    lineHeight: 22,
    marginBottom: spacing.md,
  },
  imageContainer: {,
  flexDirection: 'row',
    gap: spacing.sm,
    marginBottom: spacing.md,
  },
  imagePlaceholder: {,
  width: 80,
    height: 80,
    backgroundColor: colors.gray100,
    borderRadius: borderRadius.md,
    justifyContent: 'center',
    alignItems: 'center',
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
  actionBar: {,
  flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingTop: spacing.md,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  actionButton: {,
  flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs,
    padding: spacing.sm,
  },
  actionText: {,
  fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
  },
  topicCard: {,
  flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surface,
    marginHorizontal: spacing.lg,
    marginVertical: spacing.sm,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    ...shadows.sm,
  },
  topicIcon: {,
  width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.md,
  },
  topicInfo: {,
  flex: 1,
  },
  topicHeader: {,
  flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
    marginBottom: spacing.xs,
  },
  topicName: {,
  fontSize: typography.fontSize.base,
    fontWeight: '600' as const,
    color: colors.text,
  },
  trendingBadge: {,
  backgroundColor: colors.error,
    paddingHorizontal: spacing.xs,
    paddingVertical: 2,
    borderRadius: borderRadius.sm,
  },
  trendingText: {,
  fontSize: typography.fontSize.xs,
    color: colors.white,
    fontWeight: '600' as const,
  },
  topicStats: {,
  fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
  },
  followButton: {,
  backgroundColor: colors.primary + '20',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.md,
  },
  followButtonText: {,
  fontSize: typography.fontSize.sm,
    color: colors.primary,
    fontWeight: '600' as const,
  },
  expertCard: {,
  backgroundColor: colors.surface,
    marginHorizontal: spacing.lg,
    marginVertical: spacing.sm,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    ...shadows.sm,
  },
  expertHeader: {,
  flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  expertAvatar: {,
  width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: colors.primary + '20',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.md,
    position: 'relative',
  },
  onlineIndicator: {,
  position: 'absolute',
    bottom: 2,
    right: 2,
    width: 12,
    height: 12,
    borderRadius: 6,
    backgroundColor: colors.success,
    borderWidth: 2,
    borderColor: colors.surface,
  },
  expertInfo: {,
  flex: 1,
  },
  expertName: {,
  fontSize: typography.fontSize.base,
    fontWeight: '600' as const,
    color: colors.text,
    marginBottom: 2,
  },
  expertTitle: {,
  fontSize: typography.fontSize.sm,
    color: colors.primary,
    marginBottom: 2,
  },
  expertSpecialty: {,
  fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
  },
  expertStats: {,
  alignItems: 'flex-end',
  },
  ratingContainer: {,
  flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs,
    marginBottom: spacing.xs,
  },
  rating: {,
  fontSize: typography.fontSize.sm,
    color: colors.text,
    fontWeight: '600' as const,
  },
  consultations: {,
  fontSize: typography.fontSize.xs,
    color: colors.textSecondary,
  },
  expertActions: {,
  alignItems: 'flex-start',
  },
  myContent: {,
  padding: spacing.lg,
  },
  myTitle: {,
  fontSize: typography.fontSize.lg,
    fontWeight: '600' as const,
    color: colors.text,
    marginBottom: spacing.lg,
    textAlign: 'center',
  },
  myStats: {,
  flexDirection: 'row',
    justifyContent: 'space-around',
    backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    ...shadows.sm,
  },
  statItem: {,
  alignItems: 'center',
  },
  statValue: {,
  fontSize: typography.fontSize.xl,
    fontWeight: '700' as const,
    color: colors.primary,
    marginBottom: spacing.xs,
  },
  statLabel: {,
  fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
  },
});

export default CommunityInteractionScreen;
