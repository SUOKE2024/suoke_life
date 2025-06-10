import { useNavigation } from '@react-navigation/native';
import React, { useEffect, useRef, useState } from 'react';
import {;
  Animated,
  Dimensions,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import {;
  borderRadius,
  colors,
  shadows,
  spacing,
  typography
} from '../../constants/theme';

const { width } = Dimensions.get('window');

const LifestyleManagementScreen: React.FC = () => {
  const navigation = useNavigation();
  const [activeCategory, setActiveCategory] = useState<
    'diet' | 'exercise' | 'sleep' | 'habits'
  >('diet');

  // 动画值
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(50)).current;

  // 今日数据
  const todayData = {
    calories: { consumed: 1650, target: 2000 },
    water: { consumed: 6, target: 8 },
    exercise: { minutes: 45, target: 60 },
    sleep: { hours: 7.5, target: 8 },
    steps: { count: 8500, target: 10000 }
  };

  // 饮食记录
  const dietRecords = [
    {
      id: '1',
      meal: '早餐',
      time: '08:00',
      foods: ['燕麦粥', '鸡蛋', '牛奶'],
      calories: 420,
      icon: 'weather-sunny'
    },
    {
      id: '2',
      meal: '午餐',
      time: '12:30',
      foods: ['鸡胸肉沙拉', '糙米饭'],
      calories: 650,
      icon: 'weather-partly-cloudy'
    },
    {
      id: '3',
      meal: '晚餐',
      time: '18:00',
      foods: ['蒸鱼', '蔬菜汤', '红薯'],
      calories: 580,
      icon: 'weather-night'
    }
  ];

  // 运动计划
  const exercisePlans = [
    {
      id: '1',
      name: '晨跑',
      duration: 30,
      calories: 250,
      status: 'completed',
      time: '07:00',
      icon: 'run'
    },
    {
      id: '2',
      name: '力量训练',
      duration: 45,
      calories: 180,
      status: 'pending',
      time: '19:00',
      icon: 'dumbbell'
    },
    {
      id: '3',
      name: '瑜伽',
      duration: 20,
      calories: 80,
      status: 'pending',
      time: '21:00',
      icon: 'yoga'
    }
  ];

  // 睡眠数据
  const sleepData = {
    bedtime: '23:00',
    wakeup: '06:30',
    duration: 7.5,
    quality: 85,
    deepSleep: 2.1,
    lightSleep: 4.2,
    rem: 1.2
  };

  // 健康习惯
  const healthHabits = [
    {
      id: '1',
      name: '喝水提醒',
      description: '每2小时喝一杯水',
      completed: true,
      streak: 15,
      icon: 'water'
    },
    {
      id: '2',
      name: '冥想练习',
      description: '每日10分钟冥想',
      completed: false,
      streak: 8,
      icon: 'meditation'
    },
    {
      id: '3',
      name: '维生素补充',
      description: '每日维生素D',
      completed: true,
      streak: 22,
      icon: 'pill'
    },
    {
      id: '4',
      name: '护肤保养',
      description: '早晚护肤程序',
      completed: false,
      streak: 5,
      icon: 'face-woman'
    }
  ];

  useEffect() => {
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 800,
        useNativeDriver: true
      }),
      Animated.timing(slideAnim, {
        toValue: 0,
        duration: 800,
        useNativeDriver: true
      })
    ]).start();
  }, []);

  // 渲染分类标签
  const renderCategoryTabs = () => {
    const categories = [
      { key: 'diet', title: '饮食', icon: 'food-apple' },
      { key: 'exercise', title: '运动', icon: 'dumbbell' },
      { key: 'sleep', title: '睡眠', icon: 'sleep' },
      { key: 'habits', title: '习惯', icon: 'check-circle' }
    ];

    return (
      <ScrollView;
        horizontal;
        showsHorizontalScrollIndicator={false}
        style={styles.categoryContainer}
        contentContainerStyle={styles.categoryContent}
      >
        {categories.map(category) => (
          <TouchableOpacity;
            key={category.key}
            style={[
              styles.categoryTab,
              activeCategory === category.key && styles.activeCategoryTab
            ]}
            onPress={() => setActiveCategory(category.key as any)}
          >
            <Icon;
              name={category.icon}
              size={20}
              color={
                activeCategory === category.key ? colors.white : colors.primary;
              }
            />
            <Text;
              style={[
                styles.categoryText,
                activeCategory === category.key && styles.activeCategoryText
              ]}
            >
              {category.title}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>
    );
  };

  // 渲染今日概览
  const renderTodayOverview = () => (
    <View style={styles.overviewContainer}>
      <Text style={styles.sectionTitle}>今日概览</Text>
      <View style={styles.overviewGrid}>
        <View style={styles.overviewCard}>
          <Icon name="food" size={24} color={colors.primary} />
          <Text style={styles.overviewValue}>
            {todayData.calories.consumed}/{todayData.calories.target}
          </Text>
          <Text style={styles.overviewLabel}>卡路里</Text>
        </View>
        <View style={styles.overviewCard}>
          <Icon name="water" size={24} color={colors.info} />
          <Text style={styles.overviewValue}>
            {todayData.water.consumed}/{todayData.water.target}
          </Text>
          <Text style={styles.overviewLabel}>杯水</Text>
        </View>
        <View style={styles.overviewCard}>
          <Icon name="run" size={24} color={colors.success} />
          <Text style={styles.overviewValue}>
            {todayData.exercise.minutes}/{todayData.exercise.target}
          </Text>
          <Text style={styles.overviewLabel}>分钟</Text>
        </View>
        <View style={styles.overviewCard}>
          <Icon name="sleep" size={24} color={colors.secondary} />
          <Text style={styles.overviewValue}>
            {todayData.sleep.hours}/{todayData.sleep.target}
          </Text>
          <Text style={styles.overviewLabel}>小时</Text>
        </View>
      </View>
    </View>
  );

  // 渲染饮食管理
  const renderDietManagement = () => (
    <View style={styles.contentSection}>
      <View style={styles.sectionHeader}>
        <Text style={styles.sectionTitle}>饮食记录</Text>
        <TouchableOpacity style={styles.addButton}>
          <Icon name="plus" size={20} color={colors.primary} />
        </TouchableOpacity>
      </View>

      {dietRecords.map(record) => (
        <View key={record.id} style={styles.dietCard}>
          <View style={styles.dietHeader}>
            <View style={styles.mealInfo}>
              <Icon name={record.icon} size={20} color={colors.primary} />
              <Text style={styles.mealName}>{record.meal}</Text>
              <Text style={styles.mealTime}>{record.time}</Text>
            </View>
            <Text style={styles.caloriesText}>{record.calories} kcal</Text>
          </View>
          <View style={styles.foodList}>
            {record.foods.map(food, index) => (
              <Text key={index} style={styles.foodItem}>
                • {food}
              </Text>
            ))}
          </View>
        </View>
      ))}

      <View style={styles.nutritionSummary}>
        <Text style={styles.summaryTitle}>营养摄入</Text>
        <View style={styles.nutritionBar}>
          <View style={styles.nutritionItem}>
            <Text style={styles.nutritionLabel}>蛋白质</Text>
            <View style={styles.progressBar}>
              <View;
                style={[
                  styles.progressFill,
                  { width: '75%', backgroundColor: colors.primary }
                ]}
              />
            </View>
            <Text style={styles.nutritionValue}>75g</Text>
          </View>
          <View style={styles.nutritionItem}>
            <Text style={styles.nutritionLabel}>碳水化合物</Text>
            <View style={styles.progressBar}>
              <View;
                style={[
                  styles.progressFill,
                  { width: '60%', backgroundColor: colors.warning }
                ]}
              />
            </View>
            <Text style={styles.nutritionValue}>180g</Text>
          </View>
          <View style={styles.nutritionItem}>
            <Text style={styles.nutritionLabel}>脂肪</Text>
            <View style={styles.progressBar}>
              <View;
                style={[
                  styles.progressFill,
                  { width: '45%', backgroundColor: colors.error }
                ]}
              />
            </View>
            <Text style={styles.nutritionValue}>35g</Text>
          </View>
        </View>
      </View>
    </View>
  );

  // 渲染运动计划
  const renderExercisePlan = () => (
    <View style={styles.contentSection}>
      <View style={styles.sectionHeader}>
        <Text style={styles.sectionTitle}>运动计划</Text>
        <TouchableOpacity style={styles.addButton}>
          <Icon name="plus" size={20} color={colors.primary} />
        </TouchableOpacity>
      </View>

      {exercisePlans.map(plan) => (
        <View key={plan.id} style={styles.exerciseCard}>
          <View style={styles.exerciseHeader}>
            <View style={styles.exerciseInfo}>
              <Icon name={plan.icon} size={24} color={colors.primary} />
              <View style={styles.exerciseDetails}>
                <Text style={styles.exerciseName}>{plan.name}</Text>
                <Text style={styles.exerciseTime}>
                  {plan.time} • {plan.duration}分钟
                </Text>
              </View>
            </View>
            <View style={styles.exerciseStatus}>
              <Text style={styles.caloriesText}>{plan.calories} kcal</Text>
              <Icon;
                name={
                  plan.status === 'completed' ? 'check-circle' : 'clock-outline'
                }
                size={20}
                color={
                  plan.status === 'completed'
                    ? colors.success;
                    : colors.textSecondary;
                }
              />
            </View>
          </View>
        </View>
      ))}

      <View style={styles.exerciseStats}>
        <Text style={styles.summaryTitle}>运动统计</Text>
        <View style={styles.statsGrid}>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>{todayData.steps.count}</Text>
            <Text style={styles.statLabel}>步数</Text>
            <View style={styles.progressBar}>
              <View;
                style={[
                  styles.progressFill,
                  {
                    width: `${(todayData.steps.count / todayData.steps.target) * 100}%`,
                    backgroundColor: colors.success
                  }
                ]}
              />
            </View>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>510</Text>
            <Text style={styles.statLabel}>消耗卡路里</Text>
            <View style={styles.progressBar}>
              <View;
                style={[
                  styles.progressFill,
                  { width: '85%', backgroundColor: colors.error }
                ]}
              />
            </View>
          </View>
        </View>
      </View>
    </View>
  );

  // 渲染睡眠监测
  const renderSleepMonitoring = () => (
    <View style={styles.contentSection}>
      <View style={styles.sectionHeader}>
        <Text style={styles.sectionTitle}>睡眠监测</Text>
        <TouchableOpacity style={styles.addButton}>
          <Icon name="chart-line" size={20} color={colors.primary} />
        </TouchableOpacity>
      </View>

      <View style={styles.sleepCard}>
        <View style={styles.sleepHeader}>
          <View style={styles.sleepTime}>
            <Text style={styles.sleepLabel}>就寝时间</Text>
            <Text style={styles.sleepValue}>{sleepData.bedtime}</Text>
          </View>
          <View style={styles.sleepDuration}>
            <Text style={styles.sleepDurationText}>{sleepData.duration}h</Text>
            <Text style={styles.sleepQuality}>
              睡眠质量 {sleepData.quality}%
            </Text>
          </View>
          <View style={styles.sleepTime}>
            <Text style={styles.sleepLabel}>起床时间</Text>
            <Text style={styles.sleepValue}>{sleepData.wakeup}</Text>
          </View>
        </View>

        <View style={styles.sleepPhases}>
          <Text style={styles.summaryTitle}>睡眠阶段</Text>
          <View style={styles.phaseBar}>
            <View;
              style={[
                styles.phaseSegment,
                { flex: sleepData.deepSleep, backgroundColor: colors.primary }
              ]}
            />
            <View;
              style={[
                styles.phaseSegment,
                { flex: sleepData.lightSleep, backgroundColor: colors.info }
              ]}
            />
            <View;
              style={[
                styles.phaseSegment,
                { flex: sleepData.rem, backgroundColor: colors.warning }
              ]}
            />
          </View>
          <View style={styles.phaseLegend}>
            <View style={styles.legendItem}>
              <View;
                style={[
                  styles.legendColor,
                  { backgroundColor: colors.primary }
                ]}
              />
              <Text style={styles.legendText}>深睡 {sleepData.deepSleep}h</Text>
            </View>
            <View style={styles.legendItem}>
              <View;
                style={[styles.legendColor, { backgroundColor: colors.info }]}
              />
              <Text style={styles.legendText}>
                浅睡 {sleepData.lightSleep}h;
              </Text>
            </View>
            <View style={styles.legendItem}>
              <View;
                style={[
                  styles.legendColor,
                  { backgroundColor: colors.warning }
                ]}
              />
              <Text style={styles.legendText}>REM {sleepData.rem}h</Text>
            </View>
          </View>
        </View>
      </View>
    </View>
  );

  // 渲染健康习惯
  const renderHealthHabits = () => (
    <View style={styles.contentSection}>
      <View style={styles.sectionHeader}>
        <Text style={styles.sectionTitle}>健康习惯</Text>
        <TouchableOpacity style={styles.addButton}>
          <Icon name="plus" size={20} color={colors.primary} />
        </TouchableOpacity>
      </View>

      {healthHabits.map(habit) => (
        <View key={habit.id} style={styles.habitCard}>
          <View style={styles.habitHeader}>
            <View style={styles.habitInfo}>
              <Icon name={habit.icon} size={24} color={colors.primary} />
              <View style={styles.habitDetails}>
                <Text style={styles.habitName}>{habit.name}</Text>
                <Text style={styles.habitDescription}>{habit.description}</Text>
              </View>
            </View>
            <View style={styles.habitStatus}>
              <Text style={styles.streakText}>{habit.streak}天</Text>
              <TouchableOpacity style={styles.checkButton}>
                <Icon;
                  name={habit.completed ? 'check-circle' : 'circle-outline'}
                  size={24}
                  color={
                    habit.completed ? colors.success : colors.textSecondary;
                  }
                />
              </TouchableOpacity>
            </View>
          </View>
        </View>
      ))}

      <View style={styles.habitsSummary}>
        <Text style={styles.summaryTitle}>习惯完成度</Text>
        <View style={styles.completionRate}>
          <Text style={styles.completionText}>今日完成 2/4</Text>
          <View style={styles.progressBar}>
            <View;
              style={[
                styles.progressFill,
                { width: '50%', backgroundColor: colors.success }
              ]}
            />
          </View>
          <Text style={styles.completionPercentage}>50%</Text>
        </View>
      </View>
    </View>
  );

  // 渲染内容
  const renderContent = () => {
    switch (activeCategory) {
      case 'diet':
        return renderDietManagement();
      case 'exercise':
        return renderExercisePlan();
      case 'sleep':
        return renderSleepMonitoring();
      case 'habits':
        return renderHealthHabits();
      default:
        return null;
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      {// 头部}
      <View style={styles.header}>
        <TouchableOpacity;
          style={styles.backButton}
          onPress={() => navigation.goBack()}
        >
          <Icon name="arrow-left" size={24} color={colors.text} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>生活方式管理</Text>
        <TouchableOpacity style={styles.settingsButton}>
          <Icon name="cog-outline" size={24} color={colors.text} />
        </TouchableOpacity>
      </View>

      <ScrollView;
        style={styles.scrollContainer}
        showsVerticalScrollIndicator={false}
      >
        {// 今日概览}
        {renderTodayOverview()}

        {// 分类标签}
        {renderCategoryTabs()}

        {// 内容区域}
        <Animated.View;
          style={[
            styles.contentContainer,
            {
              opacity: fadeAnim,
              transform: [{ translateY: slideAnim }]
            }
          ]}
        >
          {renderContent()}
        </Animated.View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {,
  flex: 1,
    backgroundColor: colors.background
  },
  header: {,
  flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    backgroundColor: colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: colors.border
  },
  backButton: {,
  width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.gray100,
    justifyContent: 'center',
    alignItems: 'center'
  },
  headerTitle: {,
  fontSize: typography.fontSize.lg,
    fontWeight: '600' as const,
    color: colors.text
  },
  settingsButton: {,
  width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.gray100,
    justifyContent: 'center',
    alignItems: 'center'
  },
  scrollContainer: {,
  flex: 1
  },
  overviewContainer: {,
  padding: spacing.lg,
    backgroundColor: colors.surface
  },
  sectionTitle: {,
  fontSize: typography.fontSize.lg,
    fontWeight: '600' as const,
    color: colors.text,
    marginBottom: spacing.md
  },
  overviewGrid: {,
  flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.md
  },
  overviewCard: {,
  flex: 1,
    minWidth: (width - spacing.lg * 3) / 2,
    backgroundColor: colors.gray50,
    borderRadius: borderRadius.lg,
    padding: spacing.md,
    alignItems: 'center',
    ...shadows.sm
  },
  overviewValue: {,
  fontSize: typography.fontSize.lg,
    fontWeight: '700' as const,
    color: colors.text,
    marginTop: spacing.sm
  },
  overviewLabel: {,
  fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    marginTop: spacing.xs
  },
  categoryContainer: {,
  backgroundColor: colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: colors.border
  },
  categoryContent: {,
  paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    gap: spacing.md
  },
  categoryTab: {,
  flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.lg,
    backgroundColor: colors.primary + '20',
    gap: spacing.xs
  },
  activeCategoryTab: {,
  backgroundColor: colors.primary
  },
  categoryText: {,
  fontSize: typography.fontSize.sm,
    color: colors.primary,
    fontWeight: '600' as const
  },
  activeCategoryText: {,
  color: colors.white
  },
  contentContainer: {,
  flex: 1
  },
  contentSection: {,
  padding: spacing.lg
  },
  sectionHeader: {,
  flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: spacing.lg
  },
  addButton: {,
  width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: colors.primary + '20',
    justifyContent: 'center',
    alignItems: 'center'
  },
  dietCard: {,
  backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    marginBottom: spacing.md,
    ...shadows.sm
  },
  dietHeader: {,
  flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: spacing.md
  },
  mealInfo: {,
  flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm
  },
  mealName: {,
  fontSize: typography.fontSize.base,
    fontWeight: '600' as const,
    color: colors.text
  },
  mealTime: {,
  fontSize: typography.fontSize.sm,
    color: colors.textSecondary
  },
  caloriesText: {,
  fontSize: typography.fontSize.sm,
    fontWeight: '600' as const,
    color: colors.primary
  },
  foodList: {,
  gap: spacing.xs
  },
  foodItem: {,
  fontSize: typography.fontSize.sm,
    color: colors.textSecondary
  },
  nutritionSummary: {,
  backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    marginTop: spacing.md,
    ...shadows.sm
  },
  summaryTitle: {,
  fontSize: typography.fontSize.base,
    fontWeight: '600' as const,
    color: colors.text,
    marginBottom: spacing.md
  },
  nutritionBar: {,
  gap: spacing.md
  },
  nutritionItem: {,
  flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.md
  },
  nutritionLabel: {,
  fontSize: typography.fontSize.sm,
    color: colors.text,
    width: 80
  },
  progressBar: {,
  flex: 1,
    height: 8,
    backgroundColor: colors.gray200,
    borderRadius: 4,
    overflow: 'hidden'
  },
  progressFill: {,
  height: '100%',
    borderRadius: 4
  },
  nutritionValue: {,
  fontSize: typography.fontSize.sm,
    fontWeight: '600' as const,
    color: colors.text,
    width: 40,
    textAlign: 'right'
  },
  exerciseCard: {,
  backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    marginBottom: spacing.md,
    ...shadows.sm
  },
  exerciseHeader: {,
  flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between'
  },
  exerciseInfo: {,
  flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.md
  },
  exerciseDetails: {,
  flex: 1
  },
  exerciseName: {,
  fontSize: typography.fontSize.base,
    fontWeight: '600' as const,
    color: colors.text
  },
  exerciseTime: {,
  fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    marginTop: 2
  },
  exerciseStatus: {,
  alignItems: 'flex-end',
    gap: spacing.xs
  },
  exerciseStats: {,
  backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    marginTop: spacing.md,
    ...shadows.sm
  },
  statsGrid: {,
  flexDirection: 'row',
    gap: spacing.md
  },
  statCard: {,
  flex: 1,
    alignItems: 'center'
  },
  statValue: {,
  fontSize: typography.fontSize.xl,
    fontWeight: '700' as const,
    color: colors.text
  },
  statLabel: {,
  fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    marginTop: spacing.xs,
    marginBottom: spacing.sm
  },
  sleepCard: {,
  backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    ...shadows.sm
  },
  sleepHeader: {,
  flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: spacing.lg
  },
  sleepTime: {,
  alignItems: 'center'
  },
  sleepLabel: {,
  fontSize: typography.fontSize.sm,
    color: colors.textSecondary
  },
  sleepValue: {,
  fontSize: typography.fontSize.lg,
    fontWeight: '600' as const,
    color: colors.text,
    marginTop: spacing.xs
  },
  sleepDuration: {,
  alignItems: 'center'
  },
  sleepDurationText: {,
  fontSize: typography.fontSize['3xl'],
    fontWeight: '700' as const,
    color: colors.primary
  },
  sleepQuality: {,
  fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    marginTop: spacing.xs
  },
  sleepPhases: {,
  marginTop: spacing.lg
  },
  phaseBar: {,
  flexDirection: 'row',
    height: 20,
    borderRadius: 10,
    overflow: 'hidden',
    marginBottom: spacing.md
  },
  phaseSegment: {,
  height: '100%'
  },
  phaseLegend: {,
  flexDirection: 'row',
    justifyContent: 'space-around'
  },
  legendItem: {,
  flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs
  },
  legendColor: {,
  width: 12,
    height: 12,
    borderRadius: 6
  },
  legendText: {,
  fontSize: typography.fontSize.xs,
    color: colors.textSecondary
  },
  habitCard: {,
  backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    marginBottom: spacing.md,
    ...shadows.sm
  },
  habitHeader: {,
  flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between'
  },
  habitInfo: {,
  flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.md,
    flex: 1
  },
  habitDetails: {,
  flex: 1
  },
  habitName: {,
  fontSize: typography.fontSize.base,
    fontWeight: '600' as const,
    color: colors.text
  },
  habitDescription: {,
  fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    marginTop: 2
  },
  habitStatus: {,
  alignItems: 'center',
    gap: spacing.xs
  },
  streakText: {,
  fontSize: typography.fontSize.sm,
    fontWeight: '600' as const,
    color: colors.primary
  },
  checkButton: {,
  padding: spacing.xs
  },
  habitsSummary: {,
  backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    marginTop: spacing.md,
    ...shadows.sm
  },
  completionRate: {,
  flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.md
  },
  completionText: {,
  fontSize: typography.fontSize.sm,
    color: colors.text,
    width: 80
  },
  completionPercentage: {,
  fontSize: typography.fontSize.sm,
    fontWeight: '600' as const,
    color: colors.text,
    width: 40,
    textAlign: 'right'
  }
});

export default LifestyleManagementScreen;
