import { useNavigation } from '@react-navigation/native';
import React, { useState } from 'react';
import {
    FlatList,
    StyleSheet,
    Text,
    TextInput,
    TouchableOpacity,
    View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { borderRadius, colors, shadows, spacing, typography } from '../../constants/theme';

const CommunityScreen: React.FC = () => {
  const navigation = useNavigation();
  const [activeTab, setActiveTab] = useState<'feed' | 'topics' | 'experts'>('feed');
  const [searchQuery, setSearchQuery] = useState('');

  const posts = [
    {
      id: '1',
      author: '健康小达人',
      content: '分享一下我的减肥心得！坚持3个月，成功减重15斤。',
      topic: '减肥心得',
      likes: 128,
      comments: 45,
      timestamp: '2小时前',
      liked: false,
    },
    {
      id: '2',
      author: '运动爱好者',
      content: '今天完成了5公里晨跑，感觉整个人都充满活力！',
      topic: '运动健身',
      likes: 89,
      comments: 23,
      timestamp: '4小时前',
      liked: true,
    },
  ];

  const topics = [
    {
      id: '1',
      name: '减肥心得',
      icon: 'scale-bathroom',
      posts: 1234,
      trending: true,
    },
    {
      id: '2',
      name: '运动健身',
      icon: 'dumbbell',
      posts: 2345,
      trending: true,
    },
  ];

  const experts = [
    {
      id: '1',
      name: '李医生',
      title: '主任医师',
      specialty: '心血管内科',
      rating: 4.9,
      online: true,
    },
    {
      id: '2',
      name: '王营养师',
      title: '高级营养师',
      specialty: '临床营养',
      rating: 4.8,
      online: false,
    },
  ];

  const renderTabs = () => {
    const tabs = [
      { key: 'feed', title: '动态', icon: 'home' },
      { key: 'topics', title: '话题', icon: 'pound' },
      { key: 'experts', title: '专家', icon: 'doctor' },
    ];

    return (
      <View style={styles.tabContainer}>
        {tabs.map((tab) => (
          <TouchableOpacity
            key={tab.key}
            style={[
              styles.tab,
              activeTab === tab.key && styles.activeTab,
            ]}
            onPress={() => setActiveTab(tab.key as any)}
          >
            <Icon
              name={tab.icon}
              size={20}
              color={activeTab === tab.key ? colors.primary : colors.textSecondary}
            />
            <Text
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

  const renderPostCard = ({ item }: { item: any }) => (
    <View style={styles.postCard}>
      <View style={styles.postHeader}>
        <View style={styles.userInfo}>
          <View style={styles.avatar}>
            <Icon name="account" size={24} color={colors.primary} />
          </View>
          <View>
            <Text style={styles.userName}>{item.author}</Text>
            <Text style={styles.postTime}>{item.timestamp}</Text>
          </View>
        </View>
      </View>

      <Text style={styles.topicText}>#{item.topic}</Text>
      <Text style={styles.postContent}>{item.content}</Text>

      <View style={styles.actionBar}>
        <TouchableOpacity style={styles.actionButton}>
          <Icon 
            name={item.liked ? 'heart' : 'heart-outline'} 
            size={20} 
            color={item.liked ? colors.error : colors.textSecondary} 
          />
          <Text style={styles.actionText}>{item.likes}</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.actionButton}>
          <Icon name="comment-outline" size={20} color={colors.textSecondary} />
          <Text style={styles.actionText}>{item.comments}</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.actionButton}>
          <Icon name="share-outline" size={20} color={colors.textSecondary} />
        </TouchableOpacity>
      </View>
    </View>
  );

  const renderTopicCard = ({ item }: { item: any }) => (
    <TouchableOpacity style={styles.topicCard}>
      <View style={styles.topicIcon}>
        <Icon name={item.icon} size={24} color={colors.primary} />
      </View>
      <View style={styles.topicInfo}>
        <Text style={styles.topicName}>{item.name}</Text>
        <Text style={styles.topicStats}>{item.posts} 帖子</Text>
      </View>
      {item.trending && (
        <View style={styles.trendingBadge}>
          <Text style={styles.trendingText}>热门</Text>
        </View>
      )}
    </TouchableOpacity>
  );

  const renderExpertCard = ({ item }: { item: any }) => (
    <TouchableOpacity style={styles.expertCard}>
      <View style={styles.expertAvatar}>
        <Icon name="doctor" size={24} color={colors.primary} />
        {item.online && <View style={styles.onlineIndicator} />}
      </View>
      <View style={styles.expertInfo}>
        <Text style={styles.expertName}>{item.name}</Text>
        <Text style={styles.expertTitle}>{item.title}</Text>
        <Text style={styles.expertSpecialty}>{item.specialty}</Text>
        <View style={styles.ratingContainer}>
          <Icon name="star" size={14} color={colors.warning} />
          <Text style={styles.rating}>{item.rating}</Text>
        </View>
      </View>
      <TouchableOpacity style={styles.consultButton}>
        <Text style={styles.consultButtonText}>
          {item.online ? '立即咨询' : '预约咨询'}
        </Text>
      </TouchableOpacity>
    </TouchableOpacity>
  );

  const renderContent = () => {
    switch (activeTab) {
      case 'feed':
        return (
          <FlatList
            data={posts}
            renderItem={renderPostCard}
            keyExtractor={(item) => item.id}
            showsVerticalScrollIndicator={false}
          />
        );
      case 'topics':
        return (
          <FlatList
            data={topics}
            renderItem={renderTopicCard}
            keyExtractor={(item) => item.id}
            showsVerticalScrollIndicator={false}
          />
        );
      case 'experts':
        return (
          <FlatList
            data={experts}
            renderItem={renderExpertCard}
            keyExtractor={(item) => item.id}
            showsVerticalScrollIndicator={false}
          />
        );
      default:
        return null;
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity
          style={styles.backButton}
          onPress={() => navigation.goBack()}
        >
          <Icon name="arrow-left" size={24} color={colors.text} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>健康社区</Text>
        <TouchableOpacity style={styles.publishButton}>
          <Icon name="plus" size={24} color={colors.primary} />
        </TouchableOpacity>
      </View>

      <View style={styles.searchContainer}>
        <View style={styles.searchBar}>
          <Icon name="magnify" size={20} color={colors.textSecondary} />
          <TextInput
            style={styles.searchInput}
            placeholder="搜索话题、用户或内容..."
            value={searchQuery}
            onChangeText={setSearchQuery}
            placeholderTextColor={colors.textSecondary}
          />
        </View>
      </View>

      {renderTabs()}

      <View style={styles.contentContainer}>
        {renderContent()}
      </View>
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
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    backgroundColor: colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  backButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.gray100,
    justifyContent: 'center',
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: typography.fontSize.lg,
    fontWeight: '600' as const,
    color: colors.text,
  },
  publishButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.primary + '20',
    justifyContent: 'center',
    alignItems: 'center',
  },
  searchContainer: {
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    backgroundColor: colors.surface,
  },
  searchBar: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.gray100,
    borderRadius: borderRadius.lg,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    gap: spacing.sm,
  },
  searchInput: {
    flex: 1,
    fontSize: typography.fontSize.base,
    color: colors.text,
  },
  tabContainer: {
    flexDirection: 'row',
    backgroundColor: colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  tab: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: spacing.md,
    gap: spacing.xs,
  },
  activeTab: {
    borderBottomWidth: 2,
    borderBottomColor: colors.primary,
  },
  tabText: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
  },
  activeTabText: {
    color: colors.primary,
    fontWeight: '600' as const,
  },
  contentContainer: {
    flex: 1,
  },
  postCard: {
    backgroundColor: colors.surface,
    marginHorizontal: spacing.lg,
    marginVertical: spacing.sm,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    ...shadows.sm,
  },
  postHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: spacing.md,
  },
  userInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  avatar: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.primary + '20',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.md,
  },
  userName: {
    fontSize: typography.fontSize.base,
    fontWeight: '600' as const,
    color: colors.text,
  },
  postTime: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    marginTop: 2,
  },
  topicText: {
    fontSize: typography.fontSize.sm,
    color: colors.primary,
    fontWeight: '600' as const,
    marginBottom: spacing.sm,
  },
  postContent: {
    fontSize: typography.fontSize.base,
    color: colors.text,
    lineHeight: 22,
    marginBottom: spacing.md,
  },
  actionBar: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.lg,
    paddingTop: spacing.md,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs,
  },
  actionText: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
  },
  topicCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surface,
    marginHorizontal: spacing.lg,
    marginVertical: spacing.sm,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    ...shadows.sm,
  },
  topicIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: colors.primary + '20',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.md,
  },
  topicInfo: {
    flex: 1,
  },
  topicName: {
    fontSize: typography.fontSize.base,
    fontWeight: '600' as const,
    color: colors.text,
    marginBottom: spacing.xs,
  },
  topicStats: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
  },
  trendingBadge: {
    backgroundColor: colors.error,
    paddingHorizontal: spacing.xs,
    paddingVertical: 2,
    borderRadius: borderRadius.sm,
  },
  trendingText: {
    fontSize: typography.fontSize.xs,
    color: colors.white,
    fontWeight: '600' as const,
  },
  expertCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surface,
    marginHorizontal: spacing.lg,
    marginVertical: spacing.sm,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    ...shadows.sm,
  },
  expertAvatar: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: colors.primary + '20',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.md,
    position: 'relative',
  },
  onlineIndicator: {
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
  expertInfo: {
    flex: 1,
  },
  expertName: {
    fontSize: typography.fontSize.base,
    fontWeight: '600' as const,
    color: colors.text,
    marginBottom: 2,
  },
  expertTitle: {
    fontSize: typography.fontSize.sm,
    color: colors.primary,
    marginBottom: 2,
  },
  expertSpecialty: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
  },
  ratingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs,
  },
  rating: {
    fontSize: typography.fontSize.sm,
    color: colors.text,
    fontWeight: '600' as const,
  },
  consultButton: {
    backgroundColor: colors.primary,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.md,
  },
  consultButtonText: {
    fontSize: typography.fontSize.sm,
    color: colors.white,
    fontWeight: '600' as const,
  },
});

export default CommunityScreen; 