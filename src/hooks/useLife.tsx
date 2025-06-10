import {   Alert   } from "react-native";
react";
  LifeSuggestion,
  HealthMetric,
  LifePlan,
  LifeHabit,
  LifeGoal,
  { LifeStats } from "../types/life/      SOER_SUGGESTIONS,";
  HEALTH_METRICS,
  LIFE_PLANS,
  LIFE_HABITS,
  LIFE_GOALS,
  { LIFE_STATS } from ";../data/lifeData";/    export const useLife = () =;
> ;{
  // 性能监控
const performanceMonitor = usePerformanceMonitor(useLife", {")
    trackRender: true;
    trackMemory: true,warnThreshold: 50, // ms ;};);
  const [suggestions, setSuggestions] = useState<LifeSuggestion[] />(SOER_SUGGESTION;S;);/  const [healthMetrics, setHealthMetrics] = useState<HealthMetric[] />(HEALTH_METRIC;S;);/  const [lifePlans, setLifePlans] = useState<LifePlan[] />(LIFE_PLAN;S;);/  const [habits, setHabits] = useState<LifeHabit[] />(LIFE_HABIT;S;);/  const [goals, setGoals] = useState<LifeGoal[] />(LIFE_GOAL;S;);/  const [stats, setStats] = useState<LifeStats />(LIFE_STAT;S;)/      const [activeTab, setActiveTab] = useState<"suggestions | "metrics" | plans">("suggestions;);
  const [loading, setLoading] = useState<boolean>(fals;e;);
  const [refreshing, setRefreshing] = useState<boolean>(fals;e;);
  const completeSuggestion = useCallback(suggestion: LifeSuggestion;); => {}
    setSuggestions(prev => {})
      prev.map(item => {})
        item.id === suggestion.id;
          ? { ...item, completed: true;}
          : item;
      );
    );
    setStats(prev => ({
      ...prev,
      completedSuggestions: prev.completedSuggestions + 1;
    }));



    );
  }, []);
  const viewSuggestionDetail = useCallback(suggestion: LifeSuggestion;) => {}
    const benefitsText = suggestion.benefits?.join("、;) || ";
    const stepsText = suggestion.steps?.join(\n;";) || ";
    Alert.alert()
      suggestion.title,

      [
        {

      style: cancel";},"
        suggestion.completed;

          : {

              onPress: (); => completeSuggestion(suggestion);
            }
      ]
    );
  }, [completeSuggestion]);
  const viewPlanDetail = useCallback(plan: LifePlan;); => {}
    const milestonesText = plan.milestones;
      ?.map(m => `${m.completed ? "✅ : "⏳"} ${m.title}`);"
      .join(\n;";) || "
    Alert.alert()
      plan.title,

      [

        { text: plan.nextAction, onPress: () => executePlanAction(plan) ;}
      ]
    );
  }, []);
  const executePlanAction = useCallback(plan: LifePlan;) => {}


      [

        {

      onPress: (); => {}
            setLifePlans(prev => {})
              prev.map(item => {})
                item.id === plan.id;
                  ? { ...item, progress: Math.min(item.progress + 5, 100) ;}
                  : item;
              )
            )

          }
        }
      ]
    );
  }, []);
  const getCategoryText = useCallback(category: string;) => {}
    const categoryMap: Record<string, string> = {






    ;};
    return categoryMap[category] || catego;r;y;
  }, []);
  const getPriorityText = useCallback(priority: string;) => {}
    const priorityMap: Record<string, string> = {



    ;};
    return priorityMap[priority] || priori;t;y;
  }, []);
  const getPriorityColor = useCallback(priority: string;) => {}
    const colorMap: Record<string, string> = {
      high: "#FF3B30";
      medium: #FF9500";
      low: "#34C759"
    ;}
    return colorMap[priority] || "#8E8E9;3;";
  }, []);
  const getTrendIcon = useCallback(trend: string;) => {}
    const iconMap: Record<string, string> = {up: trending-up";
      down: "trending-down,",
      stable: "trending-neutral"
    ;}
    return iconMap[trend] || trending-neutra;l;
  }, []);
  const refreshData = useCallback(async  => {};)
    setRefreshing(true);
    try { await new Promise<void>(resolve => setTimeout(resolve, 1500;););
      setHealthMetrics(prev => {})
        prev.map(metric => ({
          ...metric,
          value: Math.max(0, Math.min(100, metric.value + (Math.random() - 0.5) * 10))
        ;}))
      )

    } catch (error) {

    } finally {
      setRefreshing(false);
    }
  }, []);
  const filterSuggestions = useCallback(;)
    category?: string;priority?: string;completed?: boolea;n;); => {}
    return suggestions.filter(suggestion => {})
      if (category && suggestion.category !== category) {return fal;s;e;}
      if (priority && suggestion.priority !== priority) {return fal;s;e;}
      if (completed !== undefined && suggestion.completed !== completed) {return fal;s;e;}
      return tr;u;e;
    });
  }, [suggestions]);
  const calculatedStats = useMemo() => {;
    const completedSuggestions = suggestions.filter(s => s.completed).leng;t;h;
    const totalSuggestions = suggestions.leng;t;h;
    const activePlans = lifePlans.filter(p => p.progress < 100).leng;t;h;
    const completedPlans = lifePlans.filter(p => p.progress >= 100).leng;t;h;
    const averageProgress = lifePlans.reduce(sum,p;); => sum + p.progress, 0) / lifePlans.length;/        const activeHabits = habits.filter(h => h.streak > 0).leng;t;h;
    return {completedSuggestions,totalSuggestions,completionRate: (completedSuggestions / totalSuggestions) * 100,/          activePlans,completedPlans,averageProgress,activeHabits,totalHabits: habits.lengt;h;};
  }, [suggestions, lifePlans, habits]);
  const getTodaySuggestions = useCallback() => {;
    return suggestions;
      .filter(s => !s.completed && s.priority === "high");
      .slice(0,3;);
  }, [suggestions]);
  const getRecommendedActions = useCallback() => {;
    const actions = ;[;];
    const urgentSuggestions = suggestions.filter(s => !s.completed && s.priority === high";) "
    if (urgentSuggestions.length > 0) {
      actions.push({
      type: "suggestion,",


        action: () => setActiveTab(suggestions");});"
    }
    const lowProgressPlans = lifePlans.filter(p => p.progress < 30;);
    if (lowProgressPlans.length > 0) {
      actions.push({
      type: "plan,",


        action: () => setActiveTab(plans");});"
    }
    return actio;n;s;
  }, [suggestions, lifePlans]);
  const updateHealthMetric = useCallback(metricId: string, value: number;) => {}
    setHealthMetrics(prev => {})
      prev.map(metric => {})
        metric.id === metricId;
          ? {
              ...metric,
              value,
              trend: value > metric.value ? "up : value < metric.value ? "down" : stable"
            ;}
          : metric;
      );
    );
  }, []);
  return {
    suggestions,
    healthMetrics,
    lifePlans,
    habits,
    goals,
    stats: calculatedStats;
    activeTab,loading,refreshing, setActiveTab,completeSuggestion,viewSuggestionDetail,viewPlanDetail,executePlanAction,refreshData,updateHealthMetric, filterSuggestions,getTodaySuggestions,getRecommendedActions, getCategoryText,getPriorityText,getPriorityColor,getTrendIcon;};
};