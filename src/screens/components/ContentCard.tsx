import React, { memo } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Animated,
} from 'react-native';
import { ContentItem } from '../../types/explore';
import { CONTENT_TYPE_CONFIG, DIFFICULTY_CONFIG } from '../../data/exploreData';
import Icon from '../../components/common/Icon';
import { colors, spacing, fonts, borderRadius, shadows } from '../../constants/theme';

interface ContentCardProps {
  item: ContentItem;
  onPress: (item: ContentItem) => void;
  onBookmark?: (item: ContentItem) => void;
  onLike?: (item: ContentItem) => void;
  isBookmarked?: boolean;
  isLiked?: boolean;
  style?: any;
}

export const ContentCard = memo<ContentCardProps>(({
  item,
  onPress,
  onBookmark,
  onLike,
  isBookmarked = false,
  isLiked = false,
  style,
}) => {
  const typeConfig = CONTENT_TYPE_CONFIG[item.type];
  const difficultyConfig = DIFFICULTY_CONFIG[item.difficulty];

  const handlePress = () => {
    onPress(item);
  };

  const handleBookmark = (e: any) => {
    e.stopPropagation();
    onBookmark?.(item);
  };

  const handleLike = (e: any) => {
    e.stopPropagation();
    onLike?.(item);
  };

  return (
    <TouchableOpacity
      style={[styles.container, style]}
      onPress={handlePress}
      activeOpacity={0.8}
    >
      {/* 特色标签 */}
      {item.featured && (
        <View style={styles.featuredBadge}>
          <Icon name="star" size={12} color={colors.white} />
          <Text style={styles.featuredText}>精选</Text>
        </View>
      )}

      {/* 头部 */}
      <View style={styles.header}>
        <View style={styles.imageContainer}>
          <Text style={styles.image}>{item.image}</Text>
        </View>
        
        <View style={styles.headerInfo}>
          <View style={styles.typeContainer}>
            <Icon 
              name={typeConfig.icon} 
              size={14} 
              color={typeConfig.color} 
            />
            <Text style={[styles.typeText, { color: typeConfig.color }]}>
              {typeConfig.name}
            </Text>
          </View>
          
          <View style={styles.metaInfo}>
            <Text style={styles.author}>{item.author}</Text>
            <Text style={styles.separator}>•</Text>
            <Text style={styles.readTime}>{item.readTime}</Text>
          </View>
        </View>

        {/* 操作按钮 */}
        <View style={styles.actions}>
          <TouchableOpacity
            style={styles.actionButton}
            onPress={handleBookmark}
          >
            <Icon
              name={isBookmarked ? "bookmark" : "bookmark-outline"}
              size={20}
              color={isBookmarked ? colors.primary : colors.textSecondary}
            />
          </TouchableOpacity>
          
          <TouchableOpacity
            style={styles.actionButton}
            onPress={handleLike}
          >
            <Icon
              name={isLiked ? "heart" : "heart-outline"}
              size={20}
              color={isLiked ? colors.error : colors.textSecondary}
            />
          </TouchableOpacity>
        </View>
      </View>

      {/* 内容 */}
      <View style={styles.content}>
        <Text style={styles.title} numberOfLines={2}>
          {item.title}
        </Text>
        <Text style={styles.subtitle} numberOfLines={2}>
          {item.subtitle}
        </Text>
        
        {item.description && (
          <Text style={styles.description} numberOfLines={3}>
            {item.description}
          </Text>
        )}
      </View>

      {/* 底部 */}
      <View style={styles.footer}>
        <View style={styles.tags}>
          {item.tags.slice(0, 3).map((tag, index) => (
            <View key={index} style={styles.tag}>
              <Text style={styles.tagText}>{tag}</Text>
            </View>
          ))}
          {item.tags.length > 3 && (
            <Text style={styles.moreTagsText}>+{item.tags.length - 3}</Text>
          )}
        </View>

        <View style={styles.stats}>
          <View style={[styles.difficultyBadge, { backgroundColor: difficultyConfig.color + '20' }]}>
            <Text style={[styles.difficultyText, { color: difficultyConfig.color }]}>
              {difficultyConfig.name}
            </Text>
          </View>
          
          <View style={styles.likesContainer}>
            <Icon name="heart-outline" size={14} color={colors.textSecondary} />
            <Text style={styles.likesText}>{item.likes}</Text>
          </View>
        </View>
      </View>
    </TouchableOpacity>
  );
});

ContentCard.displayName = 'ContentCard';

const styles = StyleSheet.create({
  container: {
    backgroundColor: colors.background,
    borderRadius: borderRadius.lg,
    padding: spacing.md,
    marginHorizontal: spacing.md,
    marginVertical: spacing.sm,
    borderWidth: 1,
    borderColor: colors.border,
    ...shadows.sm,
  },
  featuredBadge: {
    position: 'absolute',
    top: spacing.sm,
    right: spacing.sm,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.primary,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: borderRadius.sm,
    zIndex: 1,
  },
  featuredText: {
    color: colors.white,
    fontSize: fonts.size.xs,
    fontWeight: '600',
    marginLeft: spacing.xs,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: spacing.md,
  },
  imageContainer: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: colors.surface,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.md,
  },
  image: {
    fontSize: 24,
  },
  headerInfo: {
    flex: 1,
  },
  typeContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.xs,
  },
  typeText: {
    fontSize: fonts.size.sm,
    fontWeight: '600',
    marginLeft: spacing.xs,
  },
  metaInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  author: {
    fontSize: fonts.size.sm,
    color: colors.text,
    fontWeight: '500',
  },
  separator: {
    fontSize: fonts.size.sm,
    color: colors.textSecondary,
    marginHorizontal: spacing.xs,
  },
  readTime: {
    fontSize: fonts.size.sm,
    color: colors.textSecondary,
  },
  actions: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  actionButton: {
    padding: spacing.xs,
    marginLeft: spacing.xs,
  },
  content: {
    marginBottom: spacing.md,
  },
  title: {
    fontSize: fonts.size.lg,
    fontWeight: 'bold',
    color: colors.text,
    lineHeight: fonts.lineHeight.lg,
    marginBottom: spacing.xs,
  },
  subtitle: {
    fontSize: fonts.size.md,
    color: colors.textSecondary,
    lineHeight: fonts.lineHeight.md,
    marginBottom: spacing.sm,
  },
  description: {
    fontSize: fonts.size.sm,
    color: colors.textSecondary,
    lineHeight: fonts.lineHeight.sm,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-end',
  },
  tags: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
    flexWrap: 'wrap',
  },
  tag: {
    backgroundColor: colors.surface,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: borderRadius.sm,
    marginRight: spacing.xs,
    marginBottom: spacing.xs,
  },
  tagText: {
    fontSize: fonts.size.xs,
    color: colors.text,
  },
  moreTagsText: {
    fontSize: fonts.size.xs,
    color: colors.textSecondary,
    fontStyle: 'italic',
  },
  stats: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  difficultyBadge: {
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: borderRadius.sm,
    marginRight: spacing.md,
  },
  difficultyText: {
    fontSize: fonts.size.xs,
    fontWeight: '600',
  },
  likesContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  likesText: {
    fontSize: fonts.size.sm,
    color: colors.textSecondary,
    marginLeft: spacing.xs,
  },
}); 