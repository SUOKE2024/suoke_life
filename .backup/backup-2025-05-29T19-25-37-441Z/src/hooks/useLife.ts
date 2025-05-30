import { useState, useCallback, useMemo } from 'react';
import { Alert } from 'react-native';
import { 
  LifeSuggestion, 
  HealthMetric, 
  LifePlan, 
  LifeHabit, 
  LifeGoal,
  LifeStats, 
} from '../types/life';
import {
  SOER_SUGGESTIONS,
  HEALTH_METRICS,
  LIFE_PLANS,
  LIFE_HABITS,
  LIFE_GOALS,
  LIFE_STATS,
} from '../data/lifeData';

export const useLife = () => {
  const [suggestions, setSuggestions] = useState<LifeSuggestion[]>(SOER_SUGGESTIONS);
  const [healthMetrics, setHealthMetrics] = useState<HealthMetric[]>(HEALTH_METRICS);
  const [lifePlans, setLifePlans] = useState<LifePlan[]>(LIFE_PLANS);
  const [habits, setHabits] = useState<LifeHabit[]>(LIFE_HABITS);
  const [goals, setGoals] = useState<LifeGoal[]>(LIFE_GOALS);
  const [stats, setStats] = useState<LifeStats>(LIFE_STATS);
  const [activeTab, setActiveTab] = useState<'suggestions' | 'metrics' | 'plans'>('suggestions');
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  // 完成建议
  const completeSuggestion = useCallback((suggestion: LifeSuggestion) => {
    setSuggestions(prev => 
      prev.map(item => 
        item.id === suggestion.id 
          ? { ...item, completed: true }
          : item
      )
    );
    
    // 更新统计数据
    setStats(prev => ({
      ...prev,
      completedSuggestions: prev.completedSuggestions + 1,
    }));

    Alert.alert(
      '建议已完成！',
      `恭喜完成"${suggestion.title}"，获得积分奖励！`,
      [{ text: '太棒了！' }]
    );
  }, []);

  // 查看建议详情
  const viewSuggestionDetail = useCallback((suggestion: LifeSuggestion) => {
    const benefitsText = suggestion.benefits?.join('、') || '';
    const stepsText = suggestion.steps?.join('\n') || '';
    
    Alert.alert(
      suggestion.title,
      `${suggestion.description}\n\n💡 好处：${benefitsText}\n\n📝 步骤：\n${stepsText}\n\n⏱️ 预计时间：${suggestion.timeEstimate}`,
      [
        { text: '取消', style: 'cancel' },
        suggestion.completed 
          ? { text: '已完成', style: 'default' }
          : { 
              text: '开始执行', 
              onPress: () => completeSuggestion(suggestion),
            },
      ]
    );
  }, [completeSuggestion]);

  // 查看计划详情
  const viewPlanDetail = useCallback((plan: LifePlan) => {
    const milestonesText = plan.milestones
      ?.map(m => `${m.completed ? '✅' : '⏳'} ${m.title}`)
      .join('\n') || '';

    Alert.alert(
      plan.title,
      `${plan.description}\n\n📊 进度：${plan.progress}%\n⏰ 持续时间：${plan.duration}\n\n🎯 里程碑：\n${milestonesText}\n\n🎁 奖励：${plan.rewards?.join('、')}`,
      [
        { text: '关闭', style: 'cancel' },
        { text: plan.nextAction, onPress: () => executePlanAction(plan) },
      ]
    );
  }, []);

  // 执行计划行动
  const executePlanAction = useCallback((plan: LifePlan) => {
    Alert.alert(
      '执行行动',
      `即将执行：${plan.nextAction}`,
      [
        { text: '取消', style: 'cancel' },
        { 
          text: '开始', 
          onPress: () => {
            // 更新计划进度
            setLifePlans(prev => 
              prev.map(item => 
                item.id === plan.id 
                  ? { ...item, progress: Math.min(item.progress + 5, 100) }
                  : item
              )
            );
            Alert.alert('行动已开始', '继续保持，你做得很棒！');
          },
        },
      ]
    );
  }, []);

  // 获取分类文本
  const getCategoryText = useCallback((category: string) => {
    const categoryMap: Record<string, string> = {
      diet: '饮食',
      exercise: '运动',
      sleep: '睡眠',
      mental: '心理',
      social: '社交',
      work: '工作',
    };
    return categoryMap[category] || category;
  }, []);

  // 获取优先级文本
  const getPriorityText = useCallback((priority: string) => {
    const priorityMap: Record<string, string> = {
      high: '高',
      medium: '中',
      low: '低',
    };
    return priorityMap[priority] || priority;
  }, []);

  // 获取优先级颜色
  const getPriorityColor = useCallback((priority: string) => {
    const colorMap: Record<string, string> = {
      high: '#FF3B30',
      medium: '#FF9500',
      low: '#34C759',
    };
    return colorMap[priority] || '#8E8E93';
  }, []);

  // 获取趋势图标
  const getTrendIcon = useCallback((trend: string) => {
    const iconMap: Record<string, string> = {
      up: 'trending-up',
      down: 'trending-down',
      stable: 'trending-neutral',
    };
    return iconMap[trend] || 'trending-neutral';
  }, []);

  // 刷新数据
  const refreshData = useCallback(async () => {
    setRefreshing(true);
    try {
      // 模拟API调用
      await new Promise<void>(resolve => setTimeout(resolve, 1500));
      
      // 更新健康指标（模拟数据变化）
      setHealthMetrics(prev => 
        prev.map(metric => ({
          ...metric,
          value: Math.max(0, Math.min(100, metric.value + (Math.random() - 0.5) * 10)),
        }))
      );
      
      Alert.alert('刷新成功', '数据已更新');
    } catch (error) {
      Alert.alert('刷新失败', '请稍后重试');
    } finally {
      setRefreshing(false);
    }
  }, []);

  // 过滤建议
  const filterSuggestions = useCallback((
    category?: string, 
    priority?: string, 
    completed?: boolean
  ) => {
    return suggestions.filter(suggestion => {
      if (category && suggestion.category !== category) {return false;}
      if (priority && suggestion.priority !== priority) {return false;}
      if (completed !== undefined && suggestion.completed !== completed) {return false;}
      return true;
    });
  }, [suggestions]);

  // 计算统计数据
  const calculatedStats = useMemo(() => {
    const completedSuggestions = suggestions.filter(s => s.completed).length;
    const totalSuggestions = suggestions.length;
    const activePlans = lifePlans.filter(p => p.progress < 100).length;
    const completedPlans = lifePlans.filter(p => p.progress >= 100).length;
    const averageProgress = lifePlans.reduce((sum, p) => sum + p.progress, 0) / lifePlans.length;
    const activeHabits = habits.filter(h => h.streak > 0).length;

    return {
      completedSuggestions,
      totalSuggestions,
      completionRate: (completedSuggestions / totalSuggestions) * 100,
      activePlans,
      completedPlans,
      averageProgress,
      activeHabits,
      totalHabits: habits.length,
    };
  }, [suggestions, lifePlans, habits]);

  // 获取今日建议
  const getTodaySuggestions = useCallback(() => {
    return suggestions
      .filter(s => !s.completed && s.priority === 'high')
      .slice(0, 3);
  }, [suggestions]);

  // 获取推荐行动
  const getRecommendedActions = useCallback(() => {
    const actions = [];
    
    // 未完成的高优先级建议
    const urgentSuggestions = suggestions.filter(s => !s.completed && s.priority === 'high');
    if (urgentSuggestions.length > 0) {
      actions.push({
        type: 'suggestion',
        title: '完成重要建议',
        description: `有${urgentSuggestions.length}个重要建议待完成`,
        action: () => setActiveTab('suggestions'),
      });
    }

    // 进度较低的计划
    const lowProgressPlans = lifePlans.filter(p => p.progress < 30);
    if (lowProgressPlans.length > 0) {
      actions.push({
        type: 'plan',
        title: '推进生活计划',
        description: `有${lowProgressPlans.length}个计划需要关注`,
        action: () => setActiveTab('plans'),
      });
    }

    return actions;
  }, [suggestions, lifePlans]);

  // 更新健康指标
  const updateHealthMetric = useCallback((metricId: string, value: number) => {
    setHealthMetrics(prev => 
      prev.map(metric => 
        metric.id === metricId 
          ? { 
              ...metric, 
              value,
              trend: value > metric.value ? 'up' : value < metric.value ? 'down' : 'stable',
            }
          : metric
      )
    );
  }, []);

  return {
    // 状态
    suggestions,
    healthMetrics,
    lifePlans,
    habits,
    goals,
    stats: calculatedStats,
    activeTab,
    loading,
    refreshing,

    // 操作
    setActiveTab,
    completeSuggestion,
    viewSuggestionDetail,
    viewPlanDetail,
    executePlanAction,
    refreshData,
    updateHealthMetric,

    // 过滤和查询
    filterSuggestions,
    getTodaySuggestions,
    getRecommendedActions,

    // 工具函数
    getCategoryText,
    getPriorityText,
    getPriorityColor,
    getTrendIcon,
  };
}; 