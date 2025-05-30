import { HotTopic } from '../../types/explore';
import Icon from '../../components/common/Icon';
import { colors, spacing, fonts, borderRadius, shadows } from '../../constants/theme';





import React, { memo } from 'react';
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
} from 'react-native';

interface HotTopicsProps {
  topics: HotTopic[];
  onTopicPress: (topic: HotTopic) => void;
  style?: any;
}

export const HotTopics = memo<HotTopicsProps>(({
  topics,
  onTopicPress,
  style,
}) => {
  const handleTopicPress = useCallback( (topic: HotTopic) => {, []);
    onTopicPress(topic);
  };

  const renderTopic = (topic: HotTopic, index: number) => (
    <TouchableOpacity
      key={topic.id}
      style={[
        styles.topicCard,
        index === 0 && styles.firstTopic,
        topic.trending && styles.trendingTopic,
      ]}
      onPress={() => handleTopicPress(topic)}
      activeOpacity={0.8}
    >
      {topic.trending && (
        <View style={styles.trendingBadge}>
          <Icon name="trending-up" size={12} color={colors.white} />
        </View>
      )}
      
      <View style={styles.topicIcon}>
        <Text style={styles.iconText}>{topic.icon}</Text>
      </View>
      
      <View style={styles.topicInfo}>
        <Text style={styles.topicTitle} numberOfLines={1}>
          {topic.title}
        </Text>
        <View style={styles.topicStats}>
          <Icon name="account-group" size={12} color={colors.textSecondary} />
          <Text style={styles.topicCount}>
            {topic.count > 1000 ? `${(topic.count / 1000).toFixed(1)}k` : topic.count}
          </Text>
        </View>
      </View>
      
      <Icon name="chevron-right" size={16} color={colors.textSecondary} />
    </TouchableOpacity>
  );

  return (
    <View style={[styles.container, style]}>
      <View style={styles.header}>
        <Icon name="fire" size={20} color={colors.primary} />
        <Text style={styles.headerTitle}>热门话题</Text>
        <TouchableOpacity style={styles.moreButton}>
          <Text style={styles.moreText}>更多</Text>
          <Icon name="chevron-right" size={16} color={colors.primary} />
        </TouchableOpacity>
      </View>
      
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.scrollContent}
      >
        {topics.map(renderTopic)}
      </ScrollView>
    </View>
  );
});

HotTopics.displayName = 'HotTopics';

const styles = StyleSheet.create({
  container: {
    backgroundColor: colors.background,
    paddingVertical: spacing.md,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.md,
    marginBottom: spacing.md,
  },
  headerTitle: {
    fontSize: fonts.size.lg,
    fontWeight: 'bold',
    color: colors.text,
    marginLeft: spacing.sm,
    flex: 1,
  },
  moreButton: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  moreText: {
    fontSize: fonts.size.sm,
    color: colors.primary,
    marginRight: spacing.xs,
  },
  scrollContent: {
    paddingHorizontal: spacing.md,
  },
  topicCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    padding: spacing.md,
    marginRight: spacing.md,
    minWidth: 200,
    borderWidth: 1,
    borderColor: colors.border,
    ...shadows.sm,
  },
  firstTopic: {
    backgroundColor: colors.primary + '10',
    borderColor: colors.primary + '30',
  },
  trendingTopic: {
    position: 'relative',
  },
  trendingBadge: {
    position: 'absolute',
    top: -spacing.xs,
    right: -spacing.xs,
    backgroundColor: colors.error,
    borderRadius: 10,
    width: 20,
    height: 20,
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 1,
  },
  topicIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.background,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.md,
  },
  iconText: {
    fontSize: 20,
  },
  topicInfo: {
    flex: 1,
  },
  topicTitle: {
    fontSize: fonts.size.md,
    fontWeight: '600',
    color: colors.text,
    marginBottom: spacing.xs,
  },
  topicStats: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  topicCount: {
    fontSize: fonts.size.sm,
    color: colors.textSecondary,
    marginLeft: spacing.xs,
  },
}); 