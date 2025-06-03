import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  FlatList,
  Image,
  Alert,
  ActivityIndicator} from "../../placeholder";react-native";"
import { SafeAreaView } from "react-native-safe-area-context";";"
import { useNavigation } from "@react-navigation/////    native";
import Icon from "../../placeholder";react-native-vector-icons/////    MaterialCommunityIcons";"
import { colors, spacing } from ../../constants/////    theme";"
interface KnowledgeItem {
  id: string;
  title: string;
  description: string;
  category: string;
  readTime: string;
  difficulty: "beginner | "intermediate" | advanced";
  tags: string[];
  thumbnail?: string;
  author: string;
  publishDate: string;
}
interface Category {
  id: string;
  name: string;
  icon: string;
  count: number;
}
const ExploreScreen: React.FC  = () => {;}
  const navigation = useNavigation();
  const [knowledgeItems, setKnowledgeItems] = useState<KnowledgeItem[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>("all);"
  const [loading, setLoading] = useState(true);
  useEffect(() => {}
    loadKnowledgeData();
  }, []);
  const loadKnowledgeData = async() => {;}
    try {;
      //////     模拟加载知识数据
const mockCategories: Category[] = [;
        { id: "all", name: 全部", icon: "view-grid, count: 24 },
        { id: "tcm-theory", name: 中医理论", icon: "book-open-variant, count: 8 },
        { id: "health-tips", name: 养生保健", icon: "heart-pulse, count: 6 },
        { id: "diet-therapy", name: 食疗药膳", icon: "food-apple, count: 5 },
        { id: "exercise", name: 运动健身", icon: "run, count: 5 }];
      const mockKnowledgeItems: KnowledgeItem[] = [;
        {
          id: "1",
          title: 中医五行学说详解","
          description: "深入了解中医五行理论，掌握五脏六腑的相互关系,"
          category: "tcm-theory",
          readTime: 15分钟","
          difficulty: "intermediate,"
          tags: ["五行", 中医基础", "理论],
          author: "老克",
          publishDate: 2024-01-15""
        },
        {
          id: "2,"
          title: "春季养生指南",
          description: 春季如何调理身体，预防疾病，保持健康","
          category: "health-tips,"
          readTime: "10分钟",
          difficulty: beginner","
          tags: ["春季, "养生", 预防"],
          author: "老克,"
          publishDate: "2024-01-14"
        },
        {
          id: 3","
          title: "太极拳入门教程,"
          description: "从基础动作开始，学习太极拳的精髓",
          category: exercise","
          readTime: "20分钟,"
          difficulty: "beginner",
          tags: [太极", "运动, "入门"],
          author: 老克","
          publishDate: "2024-01-13"
        },
        {
          id: "4",
          title: 药膳食疗配方大全","
          description: "常见疾病的食疗方法和药膳配方,"
          category: "diet-therapy",
          readTime: 25分钟","
          difficulty: "advanced,"
          tags: ["药膳", 食疗", "配方],
          author: "老克",
          publishDate: 2024-01-12""
        }];
      setCategories(mockCategories);
      setKnowledgeItems(mockKnowledgeItems);
    } catch (error) {
      Alert.alert("错误", 加载内容失败，请稍后重试");"
    } finally {
      setLoading(false);
    }
  };
  const filteredItems = selectedCategory === "all;"
    ? knowledgeItems ;
    : knowledgeItems.filter(item => item.category === selectedCategory);
  const getDifficultyColor = (difficulty: KnowledgeItem["difficulty"]) => {;}
    switch (difficulty) {
      case beginner":;"
        return colors.success;
      case "intermediate:"
        return colors.warning;
      case "advanced":
        return colors.error;
      default:
        return colors.textSecondary;
    }
  };
  const getDifficultyText = (difficulty: KnowledgeItem[difficulty"]) => {;}"
    switch (difficulty) {
      case "beginner:;"
        return "入门";
      case intermediate":"
        return "进阶;"
      case "advanced":
        return 高级";"
      default:
        return "未知;"
    }
  };
  const handleKnowledgeItemPress = (item: KnowledgeItem) => {;}
    Alert.alert(item.title, `即将阅读：${item.description}`);
  };
  const renderCategoryItem = ({ item }: { item: Category }) => (;
    <TouchableOpacity;
style={[
        styles.categoryItem,
        selectedCategory === item.id && styles.selectedCategoryItem;
      ]}
      onPress={() => setSelectedCategory(item.id)}
    >
      <Icon;
name={item.icon}
        size={20}
        color={selectedCategory === item.id ? colors.white : colors.primary}
      /////    >
      <Text style={[ ///  >
        styles.categoryText,
        selectedCategory === item.id && styles.selectedCategoryText;
      ]}>
        {item.name}
      </////    Text>
      <Text style={[ ///  >
        styles.categoryCount,
        selectedCategory === item.id && styles.selectedCategoryCount;
      ]}>
        {item.count}
      </////    Text>
    </////    TouchableOpacity>
  );
  const renderKnowledgeItem = ({ item }: { item: KnowledgeItem }) => (;
    <TouchableOpacity;
style={styles.knowledgeCard}
      onPress={() => handleKnowledgeItemPress(item)}
      activeOpacity={0.7}
    >
      <View style={styles.cardHeader}>
        <View style={styles.cardInfo}>
          <Text style={styles.cardTitle}>{item.title}</////    Text>
          <Text style={styles.cardDescription}>{item.description}</////    Text>
        </////    View>
        <View style={styles.cardMeta}>
          <View style={[styles.difficultyBadge, { backgroundColor: getDifficultyColor(item.difficulty) }]}>
            <Text style={styles.difficultyText}>{getDifficultyText(item.difficulty)}</////    Text>
          </////    View>
        </////    View>
      </////    View>
      <View style={styles.cardFooter}>
        <View style={styles.cardTags}>
          {item.tags.slice(0, 3).map((tag, index) => (
            <View key={index} style={styles.tag}>
              <Text style={styles.tagText}>{tag}</////    Text>
            </////    View>
          ))}
        </////    View>
        <View style={styles.cardStats}>
          <Icon name="clock-outline" size={14} color={colors.textSecondary} /////    >
          <Text style={styles.readTime}>{item.readTime}</////    Text>
        </////    View>
      </////    View>
    </////    TouchableOpacity>
  );
  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={colors.primary} /////    >
          <Text style={styles.loadingText}>正在加载知识内容...</////    Text>
        </////    View>
      </////    SafeAreaView>
    );
  }
  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <View style={styles.headerContent}>
          <View style={styles.agentInfo}>
            <Text style={styles.agentEmoji}>👨‍⚕️</////    Text>
            <View>
              <Text style={styles.agentName}>老克</////    Text>
              <Text style={styles.agentRole}>知识传播智能体</////    Text>
            </////    View>
          </////    View>
          <TouchableOpacity style={styles.searchButton}>
            <Icon name="magnify" size={24} color={colors.textSecondary} /////    >
          </////    TouchableOpacity>
        </////    View>
        <Text style={styles.headerDescription}>
          传播中医智慧，分享健康知识，让传统医学走进现代生活
        </////    Text>
      </////    View>
      <View style={styles.categoriesContainer}>
        <FlatList;
data={categories}
          renderItem={renderCategoryItem}
          keyExtractor={(item) => item.id}
          horizontal;
showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.categoriesList}
        /////    >
      </////    View>
      <FlatList;
data={filteredItems}
        renderItem={renderKnowledgeItem}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.knowledgeList}
        showsVerticalScrollIndicator={false}
      /////    >
    </////    SafeAreaView>
  );
};
const styles = StyleSheet.create({;
  container: {
    flex: 1,
    backgroundColor: colors.background},
  loadingContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: center"},"
  loadingText: {
    marginTop: spacing.md,
    fontSize: 16,
    color: colors.textSecondary},
  header: {
    backgroundColor: colors.surface,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border},
  headerContent: {
    flexDirection: "row,"
    justifyContent: "space-between",
    alignItems: center","
    marginBottom: spacing.sm},
  agentInfo: {
    flexDirection: "row,"
    alignItems: "center"},
  agentEmoji: {
    fontSize: 32,
    marginRight: spacing.md},
  agentName: {
    fontSize: 24,
    fontWeight: 700","
    color: colors.textPrimary},
  agentRole: {
    fontSize: 14,
    color: colors.textSecondary},
  searchButton: {
    padding: spacing.sm},
  headerDescription: {
    fontSize: 16,
    color: colors.textSecondary,
    lineHeight: 20},
  categoriesContainer: {
    backgroundColor: colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: colors.border},
  categoriesList: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.md},
  categoryItem: {
    flexDirection: "row,"
    alignItems: "center",
    backgroundColor: colors.background,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: 20,
    marginRight: spacing.sm,
    borderWidth: 1,
    borderColor: colors.border},
  selectedCategoryItem: {
    backgroundColor: colors.primary,
    borderColor: colors.primary},
  categoryText: {
    fontSize: 14,
    color: colors.textPrimary,
    marginLeft: spacing.xs,
    marginRight: spacing.xs},
  selectedCategoryText: {
    color: colors.white},
  categoryCount: {
    fontSize: 12,
    color: colors.textSecondary,
    backgroundColor: colors.gray100,
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 10,
    minWidth: 20,
    textAlign: center"},"
  selectedCategoryCount: {
    color: colors.primary,
    backgroundColor: colors.white},
  knowledgeList: {
    padding: spacing.md},
  knowledgeCard: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.md,
    marginBottom: spacing.md,
    borderWidth: 1,
    borderColor: colors.border},
  cardHeader: {
    flexDirection: "row,"
    justifyContent: "space-between",
    marginBottom: spacing.sm},
  cardInfo: {
    flex: 1,
    marginRight: spacing.md},
  cardTitle: {
    fontSize: 18,
    fontWeight: 600","
    color: colors.textPrimary,
    marginBottom: 4},
  cardDescription: {
    fontSize: 14,
    color: colors.textSecondary,
    lineHeight: 18},
  cardMeta: {
    alignItems: "flex-end},"
  difficultyBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12},
  difficultyText: {
    fontSize: 12,
    color: colors.white,
    fontWeight: "600"},
  cardFooter: {
    flexDirection: row","
    justifyContent: "space-between,"
    alignItems: "center",
    paddingTop: spacing.sm,
    borderTopWidth: 1,
    borderTopColor: colors.border},
  cardTags: {
    flexDirection: row","
    flex: 1},
  tag: {
    backgroundColor: colors.gray100,
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
    marginRight: spacing.xs},
  tagText: {
    fontSize: 12,
    color: colors.textSecondary},
  cardStats: {
    flexDirection: "row,"
    alignItems: "center'},"'
  readTime: {
    fontSize: 12,
    color: colors.textSecondary,;
    marginLeft: 4}});
export default ExploreScreen;