import { SafeAreaView } from 'react-native-safe-area-context';
import { useExplore, useContentInteraction } from '../../hooks/useExplore';
import { ContentItem, HotTopic } from '../../types/explore';
import { colors, spacing } from '../../constants/theme';
import { SearchBar } from '../components/SearchBar';
import { CategoryTabs } from '../components/CategoryTabs';
import { ContentCard } from '../components/ContentCard';
import { HotTopics } from '../components/HotTopics';
import { EmptyState } from '../../components/common/EmptyState';
import { LoadingScreen } from '../../components/common/LoadingScreen';
import AgentChatInterface from '../../components/common/AgentChatInterface';





import React, { useState, useCallback } from 'react';
  View,
  StyleSheet,
  FlatList,
  RefreshControl,
  Alert,
} from 'react-native';

// 组件导入

// 现有组件导入

const ExploreScreen: React.FC = () => {
  // 探索相关状态
  const {
    selectedCategory,
    searchQuery,
    isLoading,
    error,
    refreshing,
    filteredContent,
    featuredContent,
    hotTopics,
    searchContent,
    selectCategory,
    refreshContent,
    setSearchQuery,
  } = useExplore();

  // 内容交互状态
  const {
    toggleBookmark,
    toggleLike,
    recordView,
    isBookmarked,
    isLiked,
  } = useContentInteraction();

  // 本地状态
  const [agentChatVisible, setAgentChatVisible] = useState(false);
  const [accessibilityEnabled, setAccessibilityEnabled] = useState(false);

  // 处理内容点击
  const handleContentPress = useCallback((item: ContentItem) => {
    recordView(item.id);
    
    if (item.type === 'video' || item.type === 'course') {
      Alert.alert(
        item.title,
        `即将播放${item.type === 'video' ? '视频' : '课程'}内容`,
        [
          { text: '取消', style: 'cancel' },
          { text: '播放', onPress: () => console.log('播放内容:', item.id) },
        ]
      );
    } else {
      Alert.alert(
        item.title,
        item.description || item.subtitle,
        [
          { text: '关闭', style: 'cancel' },
          { text: '阅读全文', onPress: () => console.log('阅读内容:', item.id) },
        ]
      );
    }
  }, [recordView]);

  // 处理收藏
  const handleBookmark = useCallback((item: ContentItem) => {
    toggleBookmark(item.id);
  }, [toggleBookmark]);

  // 处理点赞
  const handleLike = useCallback((item: ContentItem) => {
    toggleLike(item.id);
  }, [toggleLike]);

  // 处理热门话题点击
  const handleTopicPress = useCallback((topic: HotTopic) => {
    setSearchQuery(topic.title);
    searchContent(topic.title);
  }, [setSearchQuery, searchContent]);

  // 与老克对话
  const chatWithLaoke = useCallback(() => {
    setAgentChatVisible(true);
  }, []) // TODO: 检查依赖项 // TODO: 检查依赖项 // TODO: 检查依赖项 // TODO: 检查依赖项 // TODO: 检查依赖项 // TODO: 检查依赖项 // TODO: 检查依赖项 // TODO: 检查依赖项;

  // 渲染内容项
  const renderContentItem = useCallback(({ item }: { item: ContentItem }) => (
    <ContentCard
      item={item}
      onPress={handleContentPress}
      onBookmark={handleBookmark}
      onLike={handleLike}
      isBookmarked={isBookmarked(item.id)}
      isLiked={isLiked(item.id)}
    />
  ), [handleContentPress, handleBookmark, handleLike, isBookmarked, isLiked]);

  // 获取列表项的key
  const keyExtractor = useCallback((item: ContentItem) => item.id, []);

  // 列表头部组件
  const renderListHeader = useCallback(() => (
    <View>
      {/* 热门话题 */}
      <HotTopics
        topics={hotTopics}
        onTopicPress={handleTopicPress}
      />
      
      {/* 分类标签 */}
      <CategoryTabs
        selectedCategory={selectedCategory}
        onCategorySelect={selectCategory}
      />
    </View>
  ), [hotTopics, handleTopicPress, selectedCategory, selectCategory]);

  // 空状态组件
  const renderEmptyState = useCallback(() => (
    <EmptyState
      icon="book-open-outline"
      title={searchQuery ? "未找到相关内容" : "暂无内容"}
      subtitle={searchQuery ? "尝试调整搜索关键词" : "老克正在准备更多精彩内容"}
    />
  ), [searchQuery]);

  // 如果正在加载，显示加载屏幕
  if (isLoading && filteredContent.length === 0) {
    return <LoadingScreen message="加载内容中..." />;
  }

  return (
    <SafeAreaView style={styles.container}>
      {/* 搜索栏 */}
      <SearchBar
        value={searchQuery}
        onChangeText={setSearchQuery}
        placeholder="搜索老克的智慧..."
      />

      {/* 内容列表 */}
      <FlatList
        style={styles.contentList}
        data={filteredContent}
        renderItem={renderContentItem}
        keyExtractor={keyExtractor}
        ListHeaderComponent={renderListHeader}
        ListEmptyComponent={renderEmptyState}
        showsVerticalScrollIndicator={false}
        removeClippedSubviews={true}
        maxToRenderPerBatch={5}
        windowSize={10}
        initialNumToRender={5}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={refreshContent}
            colors={[colors.primary]}
            tintColor={colors.primary}
          />
        }
        getItemLayout={(data, index) => ({
          length: 200, // 估算的项目高度
          offset: 200 * index,
          index,
        })}
      />

      {/* 与老克对话界面 */}
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
  contentList: {
    flex: 1,
  },
});

export default React.memo(ExploreScreen); 