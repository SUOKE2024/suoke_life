import React from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Text, Card, Title, Paragraph, useTheme, Chip, Searchbar } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { useTranslation } from 'react-i18next';
import { useNavigation } from '@react-navigation/native';

const ExploreScreen = () => {
  const navigation = useNavigation<any>();
  const theme = useTheme();
  const { t } = useTranslation();
  const [searchQuery, setSearchQuery] = React.useState('');

  // 模拟数据
  const categories = [
    { id: '1', name: '中医养生', icon: 'leaf' },
    { id: '2', name: '食疗食补', icon: 'food-apple' },
    { id: '3', name: '穴位按摩', icon: 'hand' },
    { id: '4', name: '四季养生', icon: 'weather-sunny' },
    { id: '5', name: '经络养护', icon: 'human' },
    { id: '6', name: '情志调养', icon: 'emoticon' },
  ];

  const articles = [
    {
      id: '1',
      title: '春季养生：顺应自然，养护肝脏',
      icon: 'flower-tulip',
      iconColor: '#4CAF50',
      category: '四季养生',
      summary: '春季万物生发，养生宜养肝。本文介绍春季的养生要点及适宜食材，帮助您在春季保持身心健康。',
      readCount: 1240,
      likeCount: 345,
      author: '张医师',
      publishDate: '2024-03-15',
      tags: ['春季养生', '肝脏保健', '中医理论'],
      readTime: 5,
    },
    {
      id: '2',
      title: '中医体质辨识：你是哪种体质？',
      icon: 'human',
      iconColor: '#2196F3',
      category: '中医养生',
      summary: '中医理论认为人的体质可分为九种基本类型，不同体质有不同的养生方法。了解自己的体质，选择适合的调理方案。',
      readCount: 2380,
      likeCount: 678,
      author: '李医师',
      publishDate: '2024-03-14',
      tags: ['体质辨识', '九种体质', '个性化养生'],
      readTime: 8,
    },
    {
      id: '3',
      title: '艾灸养生全指南：穴位、方法与注意事项',
      icon: 'fire',
      iconColor: '#FF5722',
      category: '穴位按摩',
      summary: '艾灸是中医传统疗法之一，具有温经通络、驱寒祛湿等功效。本文详细介绍艾灸的方法和注意事项。',
      readCount: 1560,
      likeCount: 412,
      author: '王医师',
      publishDate: '2024-03-13',
      tags: ['艾灸疗法', '穴位保健', '传统医学'],
      readTime: 10,
    },
    {
      id: '4',
      title: '五脏六腑的食疗调养秘诀',
      icon: 'food-apple',
      iconColor: '#FF9800',
      category: '食疗养生',
      summary: '根据中医理论，不同的食物对应不同的脏腑。学会食疗调养，让饮食成为最好的药物。',
      readCount: 1890,
      likeCount: 523,
      author: '赵医师',
      publishDate: '2024-03-12',
      tags: ['食疗养生', '五脏六腑', '营养调理'],
      readTime: 12,
    },
    {
      id: '5',
      title: '经络养护：打通身体的能量通道',
      icon: 'meditation',
      iconColor: '#9C27B0',
      category: '经络养护',
      summary: '经络是人体气血运行的通道，保持经络畅通对健康至关重要。了解经络养护的方法和技巧。',
      readCount: 1120,
      likeCount: 298,
      author: '孙医师',
      publishDate: '2024-03-11',
      tags: ['经络养护', '气血调理', '中医理疗'],
      readTime: 7,
    },
    {
      id: '6',
      title: '情志调养：中医心理健康之道',
      icon: 'emoticon-happy',
      iconColor: '#E91E63',
      category: '情志调养',
      summary: '中医认为情志与脏腑功能密切相关。学习情志调养的方法，维护身心健康的平衡。',
      readCount: 2100,
      likeCount: 687,
      author: '陈医师',
      publishDate: '2024-03-10',
      tags: ['情志调养', '心理健康', '身心平衡'],
      readTime: 9,
    },
  ];

  const onChangeSearch = (query: string) => setSearchQuery(query);

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Title style={styles.headerTitle}>{t('home.explore')}</Title>
        <Searchbar
          placeholder={t('common.search')}
          onChangeText={onChangeSearch}
          value={searchQuery}
          style={styles.searchBar}
          iconColor={theme.colors.primary}
        />
      </View>

      <ScrollView style={styles.content}>
        {/* 分类区域 */}
        <View style={styles.categoriesSection}>
          <Title style={styles.sectionTitle}>{t('explore.categories')}</Title>
          <View style={styles.categoriesContainer}>
            {categories.map(category => (
              <View key={category.id} style={styles.categoryItem}>
                <View style={[styles.categoryIcon, { backgroundColor: theme.colors.primaryContainer }]}>
                  <Icon name={category.icon} size={24} color={theme.colors.primary} />
                </View>
                <Text style={styles.categoryName}>{category.name}</Text>
              </View>
            ))}
          </View>
        </View>

        {/* 推荐文章区域 */}
        <View style={styles.recommendedSection}>
          <Title style={styles.sectionTitle}>{t('explore.recommended')}</Title>
          {articles.map(article => (
            <Card 
              key={article.id} 
              style={styles.articleCard}
              onPress={() => navigation.navigate('ArticleDetail', { articleId: article.id })}
            >
                              <View style={[styles.articleImage, styles.articleImagePlaceholder, { backgroundColor: article.iconColor + '20' }]}>
                <Icon name={article.icon} size={60} color={article.iconColor} />
              </View>
                              <Card.Content>
                  <View style={styles.articleHeader}>
                    <Chip style={styles.categoryChip}>{article.category}</Chip>
                    <View style={styles.readTimeContainer}>
                      <Icon name="clock-outline" size={14} color={theme.colors.onSurfaceVariant} />
                      <Text style={styles.readTimeText}>{article.readTime}分钟</Text>
                    </View>
                  </View>
                  <Title style={styles.articleTitle}>{article.title}</Title>
                  <Paragraph style={styles.articleSummary}>{article.summary}</Paragraph>
                  
                  {/* 标签 */}
                  <View style={styles.tagsContainer}>
                    {article.tags.map((tag, index) => (
                      <Chip
                        key={index}
                        mode="outlined"
                        style={styles.tagChip}
                        textStyle={styles.tagText}
                      >
                        {tag}
                      </Chip>
                    ))}
                  </View>

                  {/* 作者和发布信息 */}
                  <View style={styles.articleMeta}>
                    <View style={styles.authorInfo}>
                      <Icon name="account-circle" size={16} color={theme.colors.onSurfaceVariant} />
                      <Text style={styles.authorText}>{article.author}</Text>
                      <Text style={styles.publishDate}>{article.publishDate}</Text>
                    </View>
                  </View>

                  {/* 统计信息 */}
                  <View style={styles.articleStats}>
                    <View style={styles.statItem}>
                      <Icon name="eye" size={16} color={theme.colors.primary} />
                      <Text style={styles.statText}>{article.readCount}</Text>
                    </View>
                    <View style={styles.statItem}>
                      <Icon name="heart" size={16} color={theme.colors.error} />
                      <Text style={styles.statText}>{article.likeCount}</Text>
                    </View>
                    <View style={styles.statItem}>
                      <Icon name="share" size={16} color={theme.colors.onSurfaceVariant} />
                      <Text style={styles.statText}>分享</Text>
                    </View>
                  </View>
                </Card.Content>
            </Card>
          ))}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    padding: 16,
    paddingBottom: 8,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  searchBar: {
    elevation: 0,
    borderRadius: 8,
    height: 48,
  },
  content: {
    flex: 1,
    padding: 16,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  categoriesSection: {
    marginBottom: 24,
  },
  categoriesContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  categoryItem: {
    width: '30%',
    alignItems: 'center',
    marginBottom: 16,
  },
  categoryIcon: {
    width: 56,
    height: 56,
    borderRadius: 28,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 8,
  },
  categoryName: {
    fontSize: 14,
    textAlign: 'center',
  },
  recommendedSection: {
    marginBottom: 24,
  },
  articleCard: {
    marginBottom: 16,
    borderRadius: 12,
    overflow: 'hidden',
  },
  articleImage: {
    height: 180,
  },
  articleImagePlaceholder: {
    justifyContent: 'center',
    alignItems: 'center',
    borderTopLeftRadius: 12,
    borderTopRightRadius: 12,
  },
  categoryChip: {
    alignSelf: 'flex-start',
    marginTop: 12,
    marginBottom: 8,
  },
  articleTitle: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  articleSummary: {
    marginTop: 8,
    fontSize: 14,
    opacity: 0.7,
  },
  articleStats: {
    flexDirection: 'row',
    marginTop: 12,
  },
  statItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 16,
  },
      statText: {
      marginLeft: 4,
      fontSize: 14,
      opacity: 0.7,
    },
    articleHeader: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginTop: 12,
      marginBottom: 8,
    },
    readTimeContainer: {
      flexDirection: 'row',
      alignItems: 'center',
    },
    readTimeText: {
      marginLeft: 4,
      fontSize: 12,
      color: '#666',
    },
    tagsContainer: {
      flexDirection: 'row',
      flexWrap: 'wrap',
      marginTop: 8,
      marginBottom: 8,
    },
    tagChip: {
      marginRight: 8,
      marginBottom: 4,
      height: 24,
    },
    tagText: {
      fontSize: 10,
    },
    articleMeta: {
      marginTop: 8,
      marginBottom: 8,
    },
    authorInfo: {
      flexDirection: 'row',
      alignItems: 'center',
    },
    authorText: {
      marginLeft: 4,
      fontSize: 12,
      fontWeight: '500',
    },
    publishDate: {
      marginLeft: 8,
      fontSize: 12,
      color: '#666',
    },
  });

export default ExploreScreen; 