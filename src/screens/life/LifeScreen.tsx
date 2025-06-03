import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  Dimensions} from "../../placeholder";react-native";"
import { SafeAreaView } from "react-native-safe-area-context";";"
import { useNavigation } from "@react-navigation/////    native";
import Icon from "../../placeholder";react-native-vector-icons/////    MaterialCommunityIcons";"
import { colors, spacing } from ../../constants/////    theme";"
const { width } = Dimensions.get("window);"
interface LifeActivity {
  id: string;
  title: string;
  description: string;
  icon: string;
  category: "exercise" | diet" | "sleep | "mindfulness";
  duration: string;
  difficulty: easy" | "medium | "hard";
  completed: boolean;
  progress?: number;
}
interface HealthMetric {
  id: string;
  name: string;
  value: string;
  unit: string;
  icon: string;
  trend: up" | "down | "stable";
  color: string;
}
const LifeScreen: React.FC  = () => {;}
  const navigation = useNavigation();
  const [activities, setActivities] = useState<LifeActivity[]>([]);
  const [healthMetrics, setHealthMetrics] = useState<HealthMetric[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string>(all");"
  useEffect(() => {}
    loadLifeData();
  }, []);
  const loadLifeData = async() => {;}
    try {;
      //////     模拟加载生活数据
const mockActivities: LifeActivity[] = [;
        {
          id: "1,"
          title: "晨间瑜伽",
          description: 15分钟舒缓瑜伽，唤醒身体活力","
          icon: "yoga,"
          category: "exercise",
          duration: 15分钟","
          difficulty: "easy,"
          completed: true,
          progress: 100;
        },
        {
          id: "2",
          title: 营养早餐","
          description: "均衡搭配，为一天提供充足能量,"
          icon: "food-apple",
          category: diet","
          duration: "30分钟,"
          difficulty: "easy",
          completed: true,
          progress: 100;
        },
        {
          id: 3","
          title: "午间散步,"
          description: "户外散步，呼吸新鲜空气",
          icon: walk","
          category: "exercise,"
          duration: "20分钟",
          difficulty: easy","
          completed: false,
          progress: 0;
        },
        {
          id: "4,"
          title: "冥想放松",
          description: 深度冥想，释放压力","
          icon: "meditation,"
          category: "mindfulness",
          duration: 10分钟","
          difficulty: "medium,"
          completed: false,
          progress: 0;
        },
        {
          id: "5",
          title: 规律睡眠","
          description: "保持良好的睡眠习惯,"
          icon: "sleep",
          category: sleep","
          duration: "8小时,"
          difficulty: "medium",
          completed: false,
          progress: 75;
        }
      ];
      const mockHealthMetrics: HealthMetric[] = [;
        {
          id: 1","
          name: "步数,"
          value: "8,542",
          unit: 步","
          icon: "walk,"
          trend: "up",
          color: colors.success;
        },
        {
          id: 2","
          name: "心率,"
          value: "72",
          unit: bpm","
          icon: "heart-pulse,"
          trend: "stable",
          color: colors.primary;
        },
        {
          id: 3","
          name: "睡眠,"
          value: "7.5",
          unit: 小时","
          icon: "sleep,"
          trend: "up",
          color: colors.info;
        },
        {
          id: 4","
          name: "水分,"
          value: "1.8",
          unit: 升","
          icon: "water,"
          trend: "down",
          color: colors.warning;
        }
      ];
      setActivities(mockActivities);
      setHealthMetrics(mockHealthMetrics);
    } catch (error) {
      Alert.alert("错误, "加载数据失败，请稍后重试");"
    } finally {
      setLoading(false);
    }
  };
  const categories = [;
    { id: all", name: "全部, icon: "view-grid" },
    { id: exercise", name: "运动, icon: "run" },
    { id: diet", name: "饮食, icon: "food-apple" },
    { id: sleep", name: "睡眠, icon: "sleep" },
    { id: mindfulness", name: "正念, icon: "meditation" };
  ];
  const filteredActivities = selectedCategory === all";"
    ? activities ;
    : activities.filter(activity => activity.category === selectedCategory);
  const handleActivityPress = (activity: LifeActivity) => {;}
    if (activity.completed) {;
      Alert.alert("已完成, `您已经完成了${activity.title}，做得很好！`);"
    } else {
      Alert.alert(
        activity.title,
        `开始${activity.description}吗？`,
        [
          { text: "取消", style: cancel" },"
          {
            text: "开始, "
            onPress: () => startActivity(activity)
          }
        ]
      );
    }
  };
  const startActivity = (activity: LifeActivity) => {;}
    //////     模拟开始活动
Alert.alert("活动开始", `正在进行${activity.title}，请按照指导完成。`);
    //////     更新活动状态
setActivities(prev => prev.map(item => {}
      item.id === activity.id;
        ? { ...item, progress: 50 }
        : item;
    ));
  };
  const getDifficultyColor = (difficulty: LifeActivity[difficulty"]) => {;}"
    switch (difficulty) {
      case "easy:;"
        return colors.success;
      case "medium":
        return colors.warning;
      case hard":"
        return colors.error;
      default:
        return colors.textSecondary;
    }
  };
  const getTrendIcon = (trend: HealthMetric["trend]) => {;}"
    switch (trend) {
      case "up":;
        return trending-up";"
      case "down:"
        return "trending-down";
      case stable":"
        return "trending-neutral;"
      default:
        return "minus";
    }
  };
  const renderHealthMetric = (metric: HealthMetric) => (;
    <View key={metric.id} style={styles.metricCard}>
      <View style={styles.metricHeader}>
        <Icon name={metric.icon} size={24} color={metric.color} /////    >;
        <Icon;
name={getTrendIcon(metric.trend)}
          size={16}
          color={metric.trend === up" ? colors.success : metric.trend === "down ? colors.error : colors.textSecondary}
        /////    >
      </////    View>
      <Text style={styles.metricValue}>{metric.value}</////    Text>
      <Text style={styles.metricUnit}>{metric.unit}</////    Text>
      <Text style={styles.metricName}>{metric.name}</////    Text>
    </////    View>
  );
  const renderActivity = (activity: LifeActivity) => (;
    <TouchableOpacity;
key={activity.id}
      style={styles.activityCard}
      onPress={() => handleActivityPress(activity)}
      activeOpacity={0.7}
    >
      <View style={styles.activityHeader}>
        <View style={styles.activityIcon}>
          <Icon name={activity.icon} size={24} color={colors.primary} /////    >
        </////    View>
        <View style={styles.activityInfo}>
          <Text style={styles.activityTitle}>{activity.title}</////    Text>
          <Text style={styles.activityDescription}>{activity.description}</////    Text>
        </////    View>
        <View style={styles.activityMeta}>
          <View style={[styles.difficultyBadge, { backgroundColor: getDifficultyColor(activity.difficulty) }]}>
            <Text style={styles.difficultyText}>
              {activity.difficulty === "easy" ? 简单" : activity.difficulty === "medium ? "中等" : 困难"}"
            </////    Text>
          </////    View>
        </////    View>
      </////    View>
      <View style={styles.activityFooter}>
        <View style={styles.activityDuration}>
          <Icon name="clock-outline" size={16} color={colors.textSecondary} /////    >
          <Text style={styles.durationText}>{activity.duration}</////    Text>
        </////    View>
        <View style={styles.progressContainer}>
          <View style={styles.progressBar}>
            <View;
style={[
                styles.progressFill,
                {
                  width: `${activity.progress || 0}%`,
                  backgroundColor: activity.completed ? colors.success : colors.primary;
                }
              ]}
            /////    >
          </////    View>
          <Text style={styles.progressText}>{activity.progress || 0}%</////    Text>
        </////    View>
        {activity.completed && (
          <Icon name="check-circle" size={20} color={colors.success} /////    >
        )}
      </////    View>
    </////    TouchableOpacity>
  );
  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={colors.primary} /////    >
          <Text style={styles.loadingText}>正在加载生活数据...</////    Text>
        </////    View>
      </////    SafeAreaView>
    );
  }
  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        {/* 头部 }////
        <View style={styles.header}>
          <View style={styles.headerContent}>
            <View style={styles.agentInfo}>
              <Text style={styles.agentEmoji}>🏃‍♀️</////    Text>
              <View>
                <Text style={styles.agentName}>索儿</////    Text>
                <Text style={styles.agentRole}>生活健康管理智能体</////    Text>
              </////    View>
            </////    View>
            <TouchableOpacity style={styles.settingsButton}>
              <Icon name="cog" size={24} color={colors.textSecondary} /////    >
            </////    TouchableOpacity>
          </////    View>
          <Text style={styles.headerDescription}>
            陪伴您的健康生活，让每一天都充满活力和正能量
          </////    Text>
        </////    View>
        {/* 健康指标 }////
        <View style={styles.metricsSection}>
          <Text style={styles.sectionTitle}>今日健康指标</////    Text>
          <ScrollView;
horizontal;
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={styles.metricsContainer}
          >
            {healthMetrics.map(renderHealthMetric)}
          </////    ScrollView>
        </////    View>
        {/* 分类筛选 }////
        <View style={styles.categoriesSection}>
          <ScrollView;
horizontal;
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={styles.categoriesContainer}
          >
            {categories.map(category => (
              <TouchableOpacity;
key={category.id}
                style={[
                  styles.categoryButton,
                  selectedCategory === category.id && styles.selectedCategoryButton;
                ]}
                onPress={() => setSelectedCategory(category.id)}
              >
                <Icon;
name={category.icon}
                  size={20}
                  color={selectedCategory === category.id ? colors.white : colors.primary}
                /////    >
                <Text style={[ ///  >
                  styles.categoryText,
                  selectedCategory === category.id && styles.selectedCategoryText;
                ]}>
                  {category.name}
                </////    Text>
              </////    TouchableOpacity>
            ))}
          </////    ScrollView>
        </////    View>
        {/* 活动列表 }////
        <View style={styles.activitiesSection}>
          <Text style={styles.sectionTitle}>推荐活动</////    Text>
          {filteredActivities.map(renderActivity)}
        </////    View>
        {/* 底部间距 }////
        <View style={styles.bottomSpacing} /////    >
      </////    ScrollView>
    </////    SafeAreaView>
  );
};
const styles = StyleSheet.create({;
  container: {
    flex: 1,
    backgroundColor: colors.background},
  loadingContainer: {
    flex: 1,
    justifyContent: "center,"
    alignItems: "center"},
  loadingText: {
    marginTop: spacing.md,
    fontSize: 16,
    color: colors.textSecondary},
  scrollView: {
    flex: 1},
  header: {
    backgroundColor: colors.surface,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border},
  headerContent: {
    flexDirection: row","
    justifyContent: "space-between,"
    alignItems: "center",
    marginBottom: spacing.sm},
  agentInfo: {
    flexDirection: row","
    alignItems: "center},"
  agentEmoji: {
    fontSize: 32,
    marginRight: spacing.md},
  agentName: {
    fontSize: 24,
    fontWeight: "700",
    color: colors.textPrimary},
  agentRole: {
    fontSize: 14,
    color: colors.textSecondary},
  settingsButton: {
    padding: spacing.sm},
  headerDescription: {
    fontSize: 16,
    color: colors.textSecondary,
    lineHeight: 20},
  metricsSection: {
    paddingVertical: spacing.lg},
  sectionTitle: {
    fontSize: 20,
    fontWeight: 600","
    color: colors.textPrimary,
    marginBottom: spacing.md,
    paddingHorizontal: spacing.lg},
  metricsContainer: {
    paddingHorizontal: spacing.md},
  metricCard: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.md,
    marginHorizontal: spacing.xs,
    width: 100,
    alignItems: "center,"
    borderWidth: 1,
    borderColor: colors.border},
  metricHeader: {
    flexDirection: "row",
    justifyContent: space-between","
    alignItems: "center,"
    width: "100%",
    marginBottom: spacing.sm},
  metricValue: {
    fontSize: 20,
    fontWeight: bold","
    color: colors.textPrimary},
  metricUnit: {
    fontSize: 12,
    color: colors.textSecondary,
    marginBottom: spacing.xs},
  metricName: {
    fontSize: 14,
    color: colors.textSecondary,
    textAlign: "center},"
  categoriesSection: {
    paddingVertical: spacing.md,
    backgroundColor: colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: colors.border},
  categoriesContainer: {
    paddingHorizontal: spacing.md},
  categoryButton: {
    flexDirection: "row",
    alignItems: center","
    backgroundColor: colors.background,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: 20,
    marginRight: spacing.sm,
    borderWidth: 1,
    borderColor: colors.border},
  selectedCategoryButton: {
    backgroundColor: colors.primary,
    borderColor: colors.primary},
  categoryText: {
    fontSize: 14,
    color: colors.textPrimary,
    marginLeft: spacing.xs},
  selectedCategoryText: {
    color: colors.white},
  activitiesSection: {
    paddingVertical: spacing.lg,
    paddingHorizontal: spacing.lg},
  activityCard: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.md,
    marginBottom: spacing.md,
    borderWidth: 1,
    borderColor: colors.border},
  activityHeader: {
    flexDirection: "row,"
    alignItems: "flex-start",
    marginBottom: spacing.md},
  activityIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.primaryLight,
    justifyContent: center","
    alignItems: "center,"
    marginRight: spacing.md},
  activityInfo: {
    flex: 1,
    marginRight: spacing.md},
  activityTitle: {
    fontSize: 18,
    fontWeight: "600",
    color: colors.textPrimary,
    marginBottom: 4},
  activityDescription: {
    fontSize: 14,
    color: colors.textSecondary,
    lineHeight: 18},
  activityMeta: {
    alignItems: flex-end"},"
  difficultyBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12},
  difficultyText: {
    fontSize: 12,
    color: colors.white,
    fontWeight: "600},"
  activityFooter: {
    flexDirection: "row",
    justifyContent: space-between","
    alignItems: "center},"
  activityDuration: {
    flexDirection: "row",
    alignItems: center"},"
  durationText: {
    fontSize: 12,
    color: colors.textSecondary,
    marginLeft: 4},
  progressContainer: {
    flexDirection: "row,"
    alignItems: "center",
    flex: 1,
    marginHorizontal: spacing.md},
  progressBar: {
    flex: 1,
    height: 6,
    backgroundColor: colors.gray200,
    borderRadius: 3,
    marginRight: spacing.xs},
  progressFill: {
    height: 100%","
    borderRadius: 3},
  progressText: {
    fontSize: 12,
    color: colors.textSecondary,
    minWidth: 35,
    textAlign: 'right'},
  bottomSpacing: {; */
    height: spacing.xl}}); *///
 *///
export default LifeScreen; */////