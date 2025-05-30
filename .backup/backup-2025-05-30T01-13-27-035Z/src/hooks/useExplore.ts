import { LAOKE_WISDOM, HOT_TOPICS, CATEGORIES } from "../data/exploreData";
import { useState, useCallback, useMemo } from "react";

  ContentItem,
  CategoryType,
  SearchFilters,
  HotTopic,
} from "../types/explore";

export const useExplore = () => {
  const [selectedCategory, setSelectedCategory] = useState<
    CategoryType | "all"
  >("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  // 过滤内容
  const filteredContent = useMemo(() => {
    return LAOKE_WISDOM.filter((item) => {
      if (selectedCategory !== "all" && item.category !== selectedCategory) {
        return false;
      }
      if (
        searchQuery &&
        !item.title.toLowerCase().includes(searchQuery.toLowerCase()) &&
        !item.subtitle.toLowerCase().includes(searchQuery.toLowerCase()) &&
        !item.tags.some((tag) =>
          tag.toLowerCase().includes(searchQuery.toLowerCase())
        )
      ) {
        return false;
      }
      return true;
    });
  }, [selectedCategory, searchQuery]);

  // 精选内容
  const featuredContent = useMemo(() => {
    return LAOKE_WISDOM.filter((item) => item.featured);
  }, []) // TODO: 检查依赖项 // TODO: 检查依赖项 // TODO: 检查依赖项; // TODO: 检查依赖项;

  // 热门话题
  const hotTopics = useMemo(() => HOT_TOPICS, []);

  // 搜索内容
  const searchContent = useCallback((query: string) => {
    setSearchQuery(query);
  }, []) // TODO: 检查依赖项 // TODO: 检查依赖项 // TODO: 检查依赖项; // TODO: 检查依赖项;

  // 选择分类
  const selectCategory = useCallback((category: CategoryType | "all") => {
    setSelectedCategory(category);
  }, []) // TODO: 检查依赖项 // TODO: 检查依赖项 // TODO: 检查依赖项; // TODO: 检查依赖项;

  // 刷新内容
  const refreshContent = useCallback(async () => {
    setRefreshing(true);
    try {
      // 模拟API调用
      await new Promise<void>((resolve) => setTimeout(() => resolve(), 1000));
      setError(null);
    } catch (err) {
      setError("刷新失败，请重试");
    } finally {
      setRefreshing(false);
    }
  }, []);

  return {
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
  };
};

// 内容交互Hook
export const useContentInteraction = () => {
  const [bookmarkedItems, setBookmarkedItems] = useState<Set<string>>(
    new Set()
  );
  const [likedItems, setLikedItems] = useState<Set<string>>(new Set());
  const [viewedItems, setViewedItems] = useState<Set<string>>(new Set());

  const toggleBookmark = useCallback((itemId: string) => {
    setBookmarkedItems((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(itemId)) {
        newSet.delete(itemId);
      } else {
        newSet.add(itemId);
      }
      return newSet;
    });
  }, []);

  const toggleLike = useCallback((itemId: string) => {
    setLikedItems((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(itemId)) {
        newSet.delete(itemId);
      } else {
        newSet.add(itemId);
      }
      return newSet;
    });
  }, []);

  const recordView = useCallback((itemId: string) => {
    setViewedItems((prev) => new Set(prev).add(itemId));
  }, []) // TODO: 检查依赖项 // TODO: 检查依赖项 // TODO: 检查依赖项; // TODO: 检查依赖项;

  const isBookmarked = useCallback(
    (itemId: string) => {
      return bookmarkedItems.has(itemId);
    },
    [bookmarkedItems]
  );

  const isLiked = useCallback(
    (itemId: string) => {
      return likedItems.has(itemId);
    },
    [likedItems]
  );

  const isViewed = useCallback(
    (itemId: string) => {
      return viewedItems.has(itemId);
    },
    [viewedItems]
  );

  return {
    toggleBookmark,
    toggleLike,
    recordView,
    isBookmarked,
    isLiked,
    isViewed,
  };
};
