import { Alert } from 'react-native';





import { useState, useCallback, useMemo } from 'react';
  UserProfile, 
  AgentInteraction, 
  HealthAchievement, 
  MemberBenefit,
  SettingSection,
  HealthStats,
  ActivityRecord,
} from '../types/profile';
  USER_PROFILE,
  AGENT_INTERACTIONS,
  HEALTH_ACHIEVEMENTS,
  MEMBER_BENEFITS,
  SETTINGS_SECTIONS,
  HEALTH_STATS,
  ACTIVITY_RECORDS,
} from '../data/profileData';

export const useProfile = () => {
  const [userProfile, setUserProfile] = useState<UserProfile>(USER_PROFILE);
  const [agentInteractions, setAgentInteractions] = useState<AgentInteraction[]>(AGENT_INTERACTIONS);
  const [achievements, setAchievements] = useState<HealthAchievement[]>(HEALTH_ACHIEVEMENTS);
  const [benefits, setBenefits] = useState<MemberBenefit[]>(MEMBER_BENEFITS);
  const [settingsSections] = useState<SettingSection[]>(SETTINGS_SECTIONS);
  const [healthStats, setHealthStats] = useState<HealthStats>(HEALTH_STATS);
  const [activityRecords, setActivityRecords] = useState<ActivityRecord[]>(ACTIVITY_RECORDS);
  const [activeTab, setActiveTab] = useState<'agents' | 'achievements' | 'benefits' | 'settings'>('agents');
  const [loading, setLoading] = useState(false);

  // 与智能体聊天
  const chatWithAgent = useCallback((agent: AgentInteraction) => {
    Alert.alert(
      `与${agent.agentName}聊天`,
      `即将开始与${agent.agentName}的对话，${agent.agentName}擅长${agent.favoriteFeature}`,
      [
        { text: '取消', style: 'cancel' },
        { 
          text: '开始聊天', 
          onPress: () => {
            // 更新最后交互时间
            setAgentInteractions(prev => 
              prev.map(item => 
                item.id === agent.id 
                  ? { ...item, lastInteraction: '刚刚', totalInteractions: item.totalInteractions + 1 }
                  : item
              )
            );
            console.log(`开始与${agent.agentName}聊天`);
          },
        },
      ]
    );
  }, []);

  // 查看成就详情
  const viewAchievement = useCallback((achievement: HealthAchievement) => {
    const progressText = achievement.unlocked 
      ? `已解锁 - ${achievement.unlockedDate}`
      : achievement.progress && achievement.target
        ? `进度: ${achievement.progress}/${achievement.target}`
        : '未解锁';

    Alert.alert(
      achievement.title,
      `${achievement.description}\n\n${progressText}\n积分奖励: ${achievement.points}`,
      [{ text: '确定' }]
    );
  }, []);

  // 使用会员特权
  const useBenefit = useCallback((benefit: MemberBenefit) => {
    if (!benefit.available) {
      Alert.alert('特权不可用', '该特权当前不可用');
      return;
    }

    if (benefit.limit && benefit.used && benefit.used >= benefit.limit) {
      Alert.alert('使用次数已达上限', `本月${benefit.title}使用次数已达上限`);
      return;
    }

    Alert.alert(
      `使用${benefit.title}`,
      benefit.description,
      [
        { text: '取消', style: 'cancel' },
        { 
          text: '使用', 
          onPress: () => {
            setBenefits(prev => 
              prev.map(item => 
                item.id === benefit.id 
                  ? { ...item, used: (item.used || 0) + 1 }
                  : item
              )
            );
            Alert.alert('使用成功', `${benefit.title}已成功使用`);
          },
        },
      ]
    );
  }, []);

  // 处理设置项点击
  const handleSettingPress = useCallback((settingId: string) => {
    switch (settingId) {
      case 'logout':
        Alert.alert(
          '退出登录',
          '确定要退出登录吗？',
          [
            { text: '取消', style: 'cancel' },
            { text: '退出', style: 'destructive', onPress: () => console.log('退出登录') },
          ]
        );
        break;
      case 'developer':
        console.log('打开开发者选项');
        break;
      default:
        console.log(`点击设置项: ${settingId}`);
    }
  }, []);

  // 更新用户资料
  const updateProfile = useCallback(async (updates: Partial<UserProfile>) => {
    setLoading(true);
    try {
      // 模拟API调用
      await new Promise<void>(resolve => setTimeout(resolve, 1000));
      setUserProfile(prev => ({ ...prev, ...updates }));
      Alert.alert('更新成功', '个人资料已更新');
    } catch (error) {
      Alert.alert('更新失败', '请稍后重试');
    } finally {
      setLoading(false);
    }
  }, []);

  // 获取健康分数颜色
  const getHealthScoreColor = useCallback((score: number) => {
    if (score >= 80) {return '#34C759';}
    if (score >= 60) {return '#FF9500';}
    return '#FF3B30';
  }, []);

  // 获取会员等级显示文本
  const getMemberLevelText = useCallback((level: string) => {
    const levelMap = {
      bronze: '青铜会员',
      silver: '白银会员',
      gold: '黄金会员',
      platinum: '铂金会员',
      diamond: '钻石会员',
    };
    return levelMap[level as keyof typeof levelMap] || '普通会员';
  }, []);

  // 计算统计数据
  const stats = useMemo(() => {
    const unlockedAchievements = achievements.filter(a => a.unlocked).length;
    const totalAchievements = achievements.length;
    const availableBenefits = benefits.filter(b => b.available).length;
    const recentActivities = activityRecords.slice(0, 5);

    return {
      unlockedAchievements,
      totalAchievements,
      achievementProgress: (unlockedAchievements / totalAchievements) * 100,
      availableBenefits,
      recentActivities,
      totalPoints: achievements
        .filter(a => a.unlocked)
        .reduce((sum, a) => sum + a.points, 0),
    };
  }, [achievements, benefits, activityRecords]);

  // 过滤成就
  const filterAchievements = useCallback((category?: string, unlocked?: boolean) => {
    return achievements.filter(achievement => {
      if (category && achievement.category !== category) {return false;}
      if (unlocked !== undefined && achievement.unlocked !== unlocked) {return false;}
      return true;
    });
  }, [achievements]);

  // 获取推荐操作
  const getRecommendedActions = useCallback(() => {
    const actions = [];
    
    // 检查未完成的成就
    const incompleteAchievements = achievements.filter(a => !a.unlocked && a.progress);
    if (incompleteAchievements.length > 0) {
      actions.push({
        type: 'achievement',
        title: '完成成就',
        description: `还有${incompleteAchievements.length}个成就待完成`,
        action: () => setActiveTab('achievements'),
      });
    }

    // 检查可用特权
    const unusedBenefits = benefits.filter(b => b.available && (!b.used || b.used < (b.limit || 1)));
    if (unusedBenefits.length > 0) {
      actions.push({
        type: 'benefit',
        title: '使用特权',
        description: `有${unusedBenefits.length}个特权可以使用`,
        action: () => setActiveTab('benefits'),
      });
    }

    return actions;
  }, [achievements, benefits]);

  return {
    // 状态
    userProfile,
    agentInteractions,
    achievements,
    benefits,
    settingsSections,
    healthStats,
    activityRecords,
    activeTab,
    loading,
    stats,

    // 操作
    setActiveTab,
    chatWithAgent,
    viewAchievement,
    useBenefit,
    handleSettingPress,
    updateProfile,
    filterAchievements,
    getRecommendedActions,

    // 工具函数
    getHealthScoreColor,
    getMemberLevelText,
  };
}; 