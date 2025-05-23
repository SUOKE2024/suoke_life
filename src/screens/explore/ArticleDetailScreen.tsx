import React, { useState } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  Dimensions,
  Share,
} from 'react-native';
import {
  Appbar,
  Card,
  Title,
  Paragraph,
  Chip,
  Button,
  IconButton,
  Text,
  Divider,
  Avatar,
  Surface,
} from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { useTheme } from 'react-native-paper';
import { useTranslation } from 'react-i18next';

const { width } = Dimensions.get('window');

interface ArticleDetailScreenProps {
  route?: {
    params?: {
      articleId?: string;
    };
  };
  navigation?: any;
}

const ArticleDetailScreen: React.FC<ArticleDetailScreenProps> = ({ route, navigation }) => {
  const articleId = route?.params?.articleId || '1';
  const theme = useTheme();
  const { t } = useTranslation();
  const [isLiked, setIsLiked] = useState(false);
  const [isBookmarked, setIsBookmarked] = useState(false);
  const [likeCount, setLikeCount] = useState(128);

  // 模拟文章数据
  const article = {
    id: articleId,
    title: '春季养生：顺应自然，调和阴阳',
    content: `
春季是万物复苏的季节，也是人体阳气生发的重要时期。中医认为，春季养生应该顺应自然规律，调和阴阳，以达到身心健康的目的。

## 春季养生的基本原则

### 1. 顺应自然，早睡早起
春季日照时间逐渐延长，人体的生物钟也应该相应调整。建议在晚上10-11点入睡，早上6-7点起床，这样有利于阳气的生发。

### 2. 饮食调养，清淡为主
春季饮食应该以清淡、甘甜为主，避免过于油腻和辛辣的食物。推荐食用：
- 绿叶蔬菜：菠菜、韭菜、芹菜等
- 时令水果：草莓、樱桃、苹果等
- 养肝食物：枸杞、红枣、山药等

### 3. 适度运动，舒展筋骨
春季是运动的好时节，但要注意适度。推荐的运动方式包括：
- 散步：每天30-45分钟
- 太极拳：调和阴阳，强身健体
- 瑜伽：舒展筋骨，放松身心

### 4. 情志调养，保持乐观
春季肝气旺盛，容易出现情绪波动。要注意：
- 保持心情愉悦
- 避免过度愤怒
- 多与朋友交流
- 培养兴趣爱好

## 春季常见问题及调理方法

### 春困
春困是春季常见的现象，主要表现为白天困倦、精神不振。调理方法：
1. 保证充足睡眠
2. 适当运动
3. 饮食清淡
4. 按摩穴位（百会、太阳穴等）

### 过敏
春季花粉较多，容易引起过敏。预防措施：
1. 减少外出时间
2. 佩戴口罩
3. 保持室内清洁
4. 增强体质

## 总结

春季养生是一个系统工程，需要从饮食、运动、作息、情志等多个方面入手。只有顺应自然规律，才能真正达到养生的目的。

记住：养生不是一朝一夕的事情，需要持之以恒。让我们在这个美好的春季，开始我们的健康之旅吧！
    `,
    author: '张中医',
    publishDate: '2024-03-15',
    readTime: 8,
    category: '养生保健',
    tags: ['春季养生', '中医理论', '生活方式'],
    icon: 'flower-tulip',
    iconColor: '#4CAF50',
    readCount: 1256,
    likeCount: 128,
  };

  const handleLike = () => {
    setIsLiked(!isLiked);
    setLikeCount(prev => isLiked ? prev - 1 : prev + 1);
  };

  const handleBookmark = () => {
    setIsBookmarked(!isBookmarked);
  };

  const handleShare = async () => {
    try {
      await Share.share({
        message: `${article.title} - 来自索克生活`,
        url: `https://suoke.life/article/${article.id}`,
      });
    } catch (error) {
      console.error('分享失败:', error);
    }
  };

  const relatedArticles = [
    {
      id: '2',
      title: '夏季养生：清热解暑，养心安神',
      category: '养生保健',
      readTime: 6,
      icon: 'weather-sunny',
      iconColor: '#FF9800',
    },
    {
      id: '3',
      title: '中医体质辨识：了解自己的体质类型',
      category: '中医理论',
      readTime: 10,
      icon: 'human',
      iconColor: '#2196F3',
    },
  ];

  return (
    <SafeAreaView style={styles.container}>
      <Appbar.Header>
        <Appbar.BackAction onPress={() => navigation?.goBack()} />
        <Appbar.Content title="文章详情" />
        <Appbar.Action icon="share" onPress={handleShare} />
        <Appbar.Action 
          icon={isBookmarked ? "bookmark" : "bookmark-outline"} 
          onPress={handleBookmark} 
        />
      </Appbar.Header>

      <ScrollView style={styles.content}>
        {/* 文章头部 */}
        <Card style={styles.headerCard}>
          <View style={[styles.headerImage, styles.headerImagePlaceholder, { backgroundColor: article.iconColor + '20' }]}>
            <Icon name={article.icon} size={80} color={article.iconColor} />
          </View>
          <Card.Content style={styles.headerContent}>
            <View style={styles.metaInfo}>
              <Chip style={styles.categoryChip}>{article.category}</Chip>
              <View style={styles.readTimeContainer}>
                <Icon name="clock-outline" size={14} color={theme.colors.onSurfaceVariant} />
                <Text style={styles.readTimeText}>{article.readTime}分钟阅读</Text>
              </View>
            </View>
            
            <Title style={styles.articleTitle}>{article.title}</Title>
            
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

            {/* 作者信息 */}
            <View style={styles.authorSection}>
              <Avatar.Text size={40} label={article.author.charAt(0)} />
              <View style={styles.authorInfo}>
                <Text style={styles.authorName}>{article.author}</Text>
                <Text style={styles.publishDate}>发布于 {article.publishDate}</Text>
              </View>
            </View>
          </Card.Content>
        </Card>

        {/* 文章内容 */}
        <Surface style={styles.contentCard}>
          <Text style={styles.articleContent}>{article.content}</Text>
        </Surface>

        {/* 互动区域 */}
        <Surface style={styles.interactionCard}>
          <View style={styles.interactionRow}>
            <View style={styles.statsContainer}>
              <View style={styles.statItem}>
                <Icon name="eye" size={20} color={theme.colors.primary} />
                <Text style={styles.statText}>{article.readCount}</Text>
              </View>
              <View style={styles.statItem}>
                <Icon name="heart" size={20} color={theme.colors.error} />
                <Text style={styles.statText}>{likeCount}</Text>
              </View>
            </View>
            
            <View style={styles.actionButtons}>
              <IconButton
                icon={isLiked ? "heart" : "heart-outline"}
                iconColor={isLiked ? theme.colors.error : theme.colors.onSurface}
                size={24}
                onPress={handleLike}
              />
              <IconButton
                icon="comment-outline"
                size={24}
                onPress={() => {/* 评论功能 */}}
              />
              <IconButton
                icon="share-variant"
                size={24}
                onPress={handleShare}
              />
            </View>
          </View>
        </Surface>

        {/* 相关文章 */}
        <View style={styles.relatedSection}>
          <Title style={styles.sectionTitle}>相关文章</Title>
          {relatedArticles.map(relatedArticle => (
            <Card 
              key={relatedArticle.id} 
              style={styles.relatedCard}
              onPress={() => navigation?.push('ArticleDetail', { articleId: relatedArticle.id })}
            >
              <View style={styles.relatedContent}>
                <View style={[styles.relatedImage, styles.relatedImagePlaceholder, { backgroundColor: relatedArticle.iconColor + '20' }]}>
                  <Icon name={relatedArticle.icon} size={40} color={relatedArticle.iconColor} />
                </View>
                <View style={styles.relatedInfo}>
                  <Chip style={styles.relatedCategory}>{relatedArticle.category}</Chip>
                  <Text style={styles.relatedTitle}>{relatedArticle.title}</Text>
                  <View style={styles.relatedMeta}>
                    <Icon name="clock-outline" size={12} color={theme.colors.onSurfaceVariant} />
                    <Text style={styles.relatedReadTime}>{relatedArticle.readTime}分钟</Text>
                  </View>
                </View>
              </View>
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
    backgroundColor: '#f5f5f5',
  },
  content: {
    flex: 1,
  },
  headerCard: {
    margin: 16,
    borderRadius: 12,
    overflow: 'hidden',
  },
  headerImage: {
    height: 200,
  },
  headerImagePlaceholder: {
    justifyContent: 'center',
    alignItems: 'center',
    borderTopLeftRadius: 12,
    borderTopRightRadius: 12,
  },
  headerContent: {
    padding: 16,
  },
  metaInfo: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  categoryChip: {
    alignSelf: 'flex-start',
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
  articleTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 12,
    lineHeight: 32,
  },
  tagsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 16,
  },
  tagChip: {
    marginRight: 8,
    marginBottom: 4,
    height: 24,
  },
  tagText: {
    fontSize: 10,
  },
  authorSection: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 8,
  },
  authorInfo: {
    marginLeft: 12,
  },
  authorName: {
    fontSize: 16,
    fontWeight: '500',
  },
  publishDate: {
    fontSize: 12,
    color: '#666',
    marginTop: 2,
  },
  contentCard: {
    margin: 16,
    marginTop: 0,
    padding: 16,
    borderRadius: 12,
  },
  articleContent: {
    fontSize: 16,
    lineHeight: 24,
    color: '#333',
  },
  interactionCard: {
    margin: 16,
    marginTop: 0,
    padding: 16,
    borderRadius: 12,
  },
  interactionRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  statsContainer: {
    flexDirection: 'row',
  },
  statItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 16,
  },
  statText: {
    marginLeft: 4,
    fontSize: 14,
  },
  actionButtons: {
    flexDirection: 'row',
  },
  relatedSection: {
    margin: 16,
    marginTop: 0,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 12,
  },
  relatedCard: {
    marginBottom: 12,
    borderRadius: 8,
  },
  relatedContent: {
    flexDirection: 'row',
    padding: 12,
  },
  relatedImage: {
    width: 80,
    height: 60,
    borderRadius: 6,
  },
  relatedImagePlaceholder: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  relatedInfo: {
    flex: 1,
    marginLeft: 12,
    justifyContent: 'space-between',
  },
  relatedCategory: {
    alignSelf: 'flex-start',
    height: 20,
    marginBottom: 4,
  },
  relatedTitle: {
    fontSize: 14,
    fontWeight: '500',
    lineHeight: 18,
  },
  relatedMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 4,
  },
  relatedReadTime: {
    marginLeft: 4,
    fontSize: 10,
    color: '#666',
  },
});

export default ArticleDetailScreen;