import { SafeAreaView } from 'react-native-safe-area-context';
importIcon from '../../components/common/Icon'/import { colors } from '../../constants/theme'/;
importReact,{ useState } from 'react';
import { usePerformanceMonitor } from '../hooks/usePerformanceMonitor'/  View,;
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  Switch,
  { FlatList } from 'react-native'
// 用户信息类型 * interface UserProfile { name: string, */
  avatar: string,
  age: number,
  gender: 'male' | 'female',
  constitution: string,
  memberLevel: string,
  joinDate: string,
  healthScore: number,
  totalDiagnosis: number,
  consecutiveDays: number,
  healthPoints: number}
// 设置项类型 * interface SettingItem { id: string, */
  title: string;
  subtitle?: string,
  icon: string,
  type: 'navigation' | 'switch' | 'info';
  value?: boolean,
  onPress?: () => void}
// 智能体交互记录 * interface AgentInteraction { id: string, */
  agentName: string,
  agentType: 'xiaoai' | 'xiaoke' | 'laoke' | 'soer',
  lastInteraction: string,
  totalInteractions: number,
  favoriteFeature: string,
  emoji: string,
  color: string}
// 健康成就 * interface HealthAchievement { id: string, */
  title: string,
  description: string,
  icon: string,
  color: string,
  unlocked: boolean;
  progress?: number;
  target?: number}
// 会员特权 * interface MemberBenefit { id: string, */
  title: string,
  description: string,
  icon: string,
  available: boolean;
  used?: number,
  limit?: number}
// 模拟用户数据 * const USER_PROFILE: UserProfile = {, */
  name: '张小明',
  avatar: '👤',
  age: 28,
  gender: 'male',
  constitution: '气虚质',
  memberLevel: '黄金会员',
  joinDate: '2023年3月',
  healthScore: 85,
  totalDiagnosis: 24,
  consecutiveDays: 15,
  healthPoints: 1280,
};
// 智能体交互记录 * const AGENT_INTERACTIONS: AgentInteraction[] = [{, */
    id: 'xiaoai',
    agentName: '小艾',
    agentType: 'xiaoai',
    lastInteraction: '2小时前',
    totalInteractions: 156,
    favoriteFeature: '健康诊断',
    emoji: '🤖',
    color: colors.primary,
  },
  {
    id: 'xiaoke',
    agentName: '小克',
    agentType: 'xiaoke',
    lastInteraction: '昨天',
    totalInteractions: 89,
    favoriteFeature: '四诊服务',
    emoji: '👨‍⚕️',
    color: '#34C759',
  },
  {
    id: 'laoke',
    agentName: '老克',
    agentType: 'laoke',
    lastInteraction: '3天前',
    totalInteractions: 67,
    favoriteFeature: '中医养生',
    emoji: '👴',
    color: '#FF9500',
  },
  {
    id: 'soer',
    agentName: '索儿',
    agentType: 'soer',
    lastInteraction: '1天前',
    totalInteractions: 134,
    favoriteFeature: '生活指导',
    emoji: '👧',
    color: '#FF2D92',
  }
];
// 健康成就 * const HEALTH_ACHIEVEMENTS: HealthAchievement[] = [{, */
    id: 'early_bird',
    title: '早起达人',
    description: '连续7天早起打卡',
    icon: 'weather-sunny',
    color: '#FF9500',
    unlocked: true,
  },
  {
    id: 'health_explorer',
    title: '健康探索者',
    description: '完成首次五诊体验',
    icon: 'compass',
    color: '#007AFF',
    unlocked: true,
  },
  {
    id: 'wisdom_seeker',
    title: '养生学者',
    description: '学习10个中医养生知识',
    icon: 'school',
    color: '#34C759',
    unlocked: false,
    progress: 7,
    target: 10,
  },
  {
    id: 'life_master',
    title: '生活大师',
    description: '完成30天生活计划',
    icon: 'trophy',
    color: '#FFD700',
    unlocked: false,
    progress: 15,
    target: 30,
  }
];
// 会员特权 * const MEMBER_BENEFITS: MemberBenefit[] = [{, */
    id: 'priority_diagnosis',
    title: '优先诊断',
    description: '享受优先诊断服务',
    icon: 'fast-forward',
    available: true,
    used: 3,
    limit: 10,
  },
  {
    id: 'expert_consultation',
    title: '专家咨询',
    description: '免费专家一对一咨询',
    icon: 'doctor',
    available: true,
    used: 1,
    limit: 3,
  },
  {
    id: 'premium_content',
    title: '专属内容',
    description: '访问高级养生内容',
    icon: 'crown',
    available: true,
  },
  {
    id: 'data_export',
    title: '数据导出',
    description: '导出完整健康报告',
    icon: 'download',
    available: true,
    used: 2,
    limit: 5,
  }
];
// 健康统计数据 * const HEALTH_STATS = useMemo((); => useMemo((); => useMemo((); => useMemo((); => useMemo((); => useMemo(() => [ */
  {
  // 性能监控 *   const performanceMonitor = usePerformanceMonitor('ProfileScreen', { */
    trackRender: true,
    trackMemory: true,
    warnThreshold: 50, // ms *   ;};) */
 label: '健康评分', value: USER_PROFILE.healthScore.toString(), icon: 'heart-pulse', unit: '分'},
  { label: '诊断次数', value: USER_PROFILE.totalDiagnosis.toString(), icon: 'stethoscope', unit: '次'},
  { label: '连续打卡', value: USER_PROFILE.consecutiveDays.toString(), icon: 'calendar-check', unit: '天'},
  { label: '健康积分', value: USER_PROFILE.healthPoints.toLocaleString(), icon: 'star', unit: '分'}
], []);
const ProfileScreen: React.FC = () => {;
  const [notificationsEnabled, setNotificationsEnabled] = useState<boolean>(tru;e;);
  const [dataSync, setDataSync] = useState<boolean>(tru;e;);
  const [darkMode, setDarkMode] = useState<boolean>(fals;e;)
  const [selectedTab, setSelectedTab] = useState<'overview' | 'agents' | 'achievements' | 'benefits'>('overview';);
  // 设置项配置 *   const settingsSections = useMemo((); => useMemo((); => useMemo((); => useMemo((); => useMemo((); => useMemo((); => [ */
    {
      title: '健康档案',
      items: [{,
          id: 'health_record',
          title: '健康档案',
          subtitle: '查看完整的健康记录',
          icon: 'folder-heart',
          type: 'navigation' as const,
          onPress: () => Alert.alert('健康档案', '即将跳转到健康档案页面')
        },
        {
          id: 'constitution',
          title: '体质分析',
          subtitle: `当前体质：${USER_PROFILE.constitution}`,
          icon: 'dna',
          type: 'navigation' as const,
          onPress: () => Alert.alert('体质分析', '即将跳转到体质分析页面')
        },
        {
          id: 'family_history',
          title: '家族病史',
          subtitle: '管理家族健康信息',
          icon: 'account-group',
          type: 'navigation' as const,
          onPress: () => Alert.alert('家族病史', '即将跳转到家族病史页面')
        },
        {
          id: 'health_report',
          title: '健康报告',
          subtitle: '生成个性化健康报告',
          icon: 'file-chart',
          type: 'navigation' as const,
          onPress: () => Alert.alert('健康报告', '即将生成您的个性化健康报告')
        }
      ]
    },
    {
      title: '智能体设置',
      items: [{,
          id: 'agent_preferences',
          title: '智能体偏好',
          subtitle: '自定义智能体交互方式',
          icon: 'robot',
          type: 'navigation' as const,
          onPress: () => Alert.alert('智能体偏好', '即将跳转到智能体偏好设置')
        },
        {
          id: 'voice_settings',
          title: '语音设置',
          subtitle: '配置语音交互参数',
          icon: 'microphone',
          type: 'navigation' as const,
          onPress: () => Alert.alert('语音设置', '即将跳转到语音设置页面')
        },
        {
          id: 'learning_mode',
          title: '学习模式',
          subtitle: '智能体个性化学习',
          icon: 'brain',
          type: 'navigation' as const,
          onPress: () => Alert.alert('学习模式', '即将跳转到学习模式设置')
        }
      ]
    },
    {
      title: '应用设置',
      items: [{,
          id: 'notifications',
          title: '推送通知',
          subtitle: '接收健康提醒和建议',
          icon: 'bell',
          type: 'switch' as const,
          value: notificationsEnabled,
          onPress: () => setNotificationsEnabled(!notificationsEnabled)},
        {
          id: 'data_sync',
          title: '数据同步',
          subtitle: '自动同步健康数据',
          icon: 'sync',
          type: 'switch' as const,
          value: dataSync,
          onPress: () => setDataSync(!dataSync)},
        {
          id: 'dark_mode',
          title: '深色模式',
          subtitle: '护眼模式',
          icon: 'theme-light-dark',
          type: 'switch' as const,
          value: darkMode,
          onPress: () => setDarkMode(!darkMode)},
        {
          id: 'language',
          title: '语言设置',
          subtitle: '中文（简体）',
          icon: 'translate',
          type: 'navigation' as const,
          onPress: () => Alert.alert('语言设置', '即将跳转到语言设置页面')
        }
      ]
    },
    {
      title: '账户管理',
      items: [{,
          id: 'privacy',
          title: '隐私设置',
          subtitle: '管理数据隐私',
          icon: 'shield-account',
          type: 'navigation' as const,
          onPress: () => Alert.alert('隐私设置', '即将跳转到隐私设置页面')
        },
        {
          id: 'security',
          title: '安全设置',
          subtitle: '密码和生物识别',
          icon: 'security',
          type: 'navigation' as const,
          onPress: () => Alert.alert('安全设置', '即将跳转到安全设置页面')
        },
        {
          id: 'backup',
          title: '数据备份',
          subtitle: '备份健康数据',
          icon: 'backup-restore',
          type: 'navigation' as const,
          onPress: () => Alert.alert('数据备份', '即将跳转到数据备份页面')
        },
        {
          id: 'blockchain',
          title: '区块链验证',
          subtitle: '健康数据区块链存证',
          icon: 'link-variant',
          type: 'navigation' as const,
          onPress: () => Alert.alert('区块链验证', '即将跳转到区块链验证页面')
        }
      ]
    },
    {
      title: '帮助与支持',
      items: [{,
          id: 'help',
          title: '帮助中心',
          subtitle: '常见问题解答',
          icon: 'help-circle',
          type: 'navigation' as const,
          onPress: () => Alert.alert('帮助中心', '即将跳转到帮助中心页面')
        },
        {
          id: 'feedback',
          title: '意见反馈',
          subtitle: '告诉我们您的想法',
          icon: 'message-text',
          type: 'navigation' as const,
          onPress: () => Alert.alert('意见反馈', '即将跳转到意见反馈页面')
        },
        {
          id: 'contact',
          title: '联系客服',
          subtitle: '7x24小时在线客服',
          icon: 'headset',
          type: 'navigation' as const,
          onPress: () => Alert.alert('联系客服', '即将连接在线客服')
        },
        {
          id: 'about',
          title: '关于索克生活',
          subtitle: "版本 1.0.0",
          icon: 'information',
          type: 'navigation' as const,
          onPress: () =>,
            Alert.alert(
              '关于索克生活',
              '索克生活 v1.0.0\n\n一个专注于健康管理的智能平台\n\n由四大智能体驱动：小艾、小克、老克、索儿\n\n融合中医智慧与现代科技'
            );
        }
      ]
    }
  ], []);
  // 与智能体对话 *   const chatWithAgent = useCallback(() => { */
    Alert.alert(
      `与${agent.agentName}对话`,
      `您与${agent.agentName}已经交互了${agent.totalInteractions}次\n最后交互：${agent.lastInteraction}\n最常使用：${agent.favoriteFeature}\n\n是否继续对话？`,
      [
        { text: '取消', style: 'cancel'},
        { text: '开始对话', onPress: (); => }
      ]
    );
  };
  // 查看成就详情 *   const viewAchievement = useCallback;(;) => { */
    Alert.alert(
      achievement.title,
      `${achievement.description}${progressText}`,
      [
        { text: '了解更多', onPress: (); => }
      ]
    );
  };
  // 使用会员特权 *   const useBenefit = useCallback(() => { */
    if (!benefit.available) {
      Alert.alert('特权不可用', '该特权暂时不可用');
      return;
    }
    const usageText = useMemo((); => useMemo((); => useMemo((); => useMemo((); => useMemo((); => useMemo(() => benefit.limit
      ? `\n\n使用情况：${benefit.used || 0}/${benefit.limit}`/      : '', [])
    Alert.alert(
      benefit.title,
      `${benefit.description}${usageText}`,
      [
        { text: '取消', style: 'cancel'},
        { text: '立即使用', onPress: (); => }
      ]
    );
  };
  // 渲染用户头像和基本信息 *    *// TODO: 将内联组件移到组件外部* * const renderUserHeader = useMemo((); => useMemo((); => useMemo((); => useMemo((); => useMemo((); => useMemo(() => () => ( * *//
    <View style={styles.userHeader} />/      <View style={styles.avatarContainer} />/        <Text style={styles.avatarText} />{USER_PROFILE.avatar}</Text>/        <View style={styles.memberBadge} />/          <Icon name="crown" size={12} color="#FFD700" />/        </View>/        <View style={[styles.healthScoreBadge, { backgroundColor: getHealthScoreColor()   }]} />/          <Text style={styles.healthScoreText} />{USER_PROFILE.healthScore}</Text>/        </View>/      </View>/
      <View style={styles.userInfo} />/        <Text style={styles.userName} />{USER_PROFILE.name}</Text>/        <Text style={styles.userDetails} />/          {USER_PROFILE.age}岁 • {USER_PROFILE.gender === 'male' ? '男' : '女'}{' '}
          • {USER_PROFILE.constitution}
        </Text>/        <View style={styles.memberInfo} />/          <Icon name="star" size={14} color="#FFD700" />/          <Text style={styles.memberLevel} />{USER_PROFILE.memberLevel}</Text>/          <Text style={styles.joinDate} />• 加入于{USER_PROFILE.joinDate}</Text>/        </View>/        <View style={styles.quickActions} />/          <TouchableOpacity style={styles.quickActionButton} accessibilityLabel="TODO: 添加无障碍标签" />/            <Icon name="qrcode" size={16} color={colors.primary} />/            <Text style={styles.quickActionText} />我的二维码</Text>/          </TouchableOpacity>/          <TouchableOpacity style={styles.quickActionButton} accessibilityLabel="TODO: 添加无障碍标签" />/            <Icon name="share" size={16} color={colors.primary} />/            <Text style={styles.quickActionText} />分享</Text>/          </TouchableOpacity>/        </View>/      </View>/
      <TouchableOpacity style={styles.editButton} accessibilityLabel="TODO: 添加无障碍标签" />/        <Icon name="pencil" size={20} color={colors.primary} />/      </TouchableOpacity>/    </View>/), []);
  // 获取健康评分颜色 *   const getHealthScoreColor = useCallback(() => { */
    if (USER_PROFILE.healthScore >= 80) {return '#34C75;9;'}
    if (USER_PROFILE.healthScore >= 60) {return '#FF950;0;'}
    return '#FF3B3;0;';
  };
  // 渲染健康统计 *    *// TODO: 将内联组件移到组件外部* * const renderHealthStats = useMemo((); => useMemo((); => useMemo((); => useMemo((); => useMemo((); => useMemo((); => () => ( * *//
    <View style={styles.statsContainer} />/      <Text style={styles.statsTitle} />健康统计</Text>/      <View style={styles.statsGrid} />/        {HEALTH_STATS.map((stat, index) => (
          <TouchableOpacity key={index} style={styles.statItem} accessibilityLabel="TODO: 添加无障碍标签" />/            <Icon name={stat.icon} size={24} color={colors.primary} />/            <Text style={styles.statValue} />{stat.value}</Text>/            <Text style={styles.statLabel} />{stat.label}</Text>/            {stat.unit && <Text style={styles.statUnit} />{stat.unit}</Text>}/          </TouchableOpacity>/))}
      </View>/    </View>/  ), []);
  // 渲染标签栏 *    *// TODO: 将内联组件移到组件外部* * const renderTabBar = useMemo((); => useMemo((); => useMemo((); => useMemo((); => useMemo((); => useMemo(() => () => ( * *//
    <View style={styles.tabBar} />/      {[
        { key: 'overview', label: '概览', icon: 'view-dashboard'},
        { key: 'agents', label: '智能体', icon: 'robot'},
        { key: 'achievements', label: '成就', icon: 'trophy'},
        { key: 'benefits', label: '特权', icon: 'crown'}
      ].map(tab => (
        <TouchableOpacity
          key={tab.key}
          style={[styles.tabItem, selectedTab === tab.key && styles.activeTabItem]}
          onPress={() = accessibilityLabel="TODO: 添加无障碍标签" /> setSelectedTab(tab.key as any)}/        >
          <Icon
            name={tab.icon}
            size={18}
            color={selectedTab === tab.key ? colors.primary: colors.textSecondary} />/          <Text style={[
            styles.tabLabel,
            selectedTab === tab.key && styles.activeTabLabel
          ]} />/            {tab.label}
          </Text>/        </TouchableOpacity>/      ))}
    </View>/  ), []);
  // 渲染智能体交互卡片 *   const renderAgentCard = useMemo((); => useMemo((); => useMemo((); => useMemo((); => useMemo((); => useMemo(() => ({ item }: { item: AgentInteraction}) => ( */
    <TouchableOpacity style={styles.agentCard} onPress={() = accessibilityLabel="TODO: 添加无障碍标签" /> chatWithAgent(item)}>/      <View style={styles.agentHeader} />/        <Text style={styles.agentEmoji} />{item.emoji}</Text>/        <View style={styles.agentInfo} />/          <Text style={styles.agentName} />{item.agentName}</Text>/          <Text style={styles.agentFeature} />最常使用：{item.favoriteFeature}</Text>/        </View>/        <View style={styles.agentStats} />/          <Text style={[styles.interactionCount, { color: item.color}]} />/            {item.totalInteractions}次
          </Text>/          <Text style={styles.lastInteraction} />{item.lastInteraction}</Text>/        </View>/      </View>/    </TouchableOpacity>/), []);
  // 渲染成就卡片 *   const renderAchievementCard = useMemo((); => useMemo((); => useMemo((); => useMemo((); => useMemo((); => useMemo(() => ({ item }: { item: HealthAchievement}) => ( */
    <TouchableOpacity
      style={[styles.achievementCard, !item.unlocked && styles.lockedCard]}
      onPress={() = accessibilityLabel="TODO: 添加无障碍标签" /> viewAchievement(item)}/    >
      <View style={[styles.achievementIcon, { backgroundColor: item.color + '20'}]} />/        <Icon
          name={item.icon}
          size={24}
          color={item.unlocked ? item.color: colors.textSecondary} />/      </View>/      <View style={styles.achievementInfo} />/        <Text style={[styles.achievementTitle, !item.unlocked && styles.lockedText]} />/          {item.title}
        </Text>/        <Text style={styles.achievementDesc} />{item.description}</Text>/        {!item.unlocked && item.progress && item.target && (
          <View style={styles.progressContainer} />/            <View style={styles.progressBar} />/              <View
                style={[
                  styles.progressFill,
                  { width: `${(item.progress / item.target) * 100  }%`, backgroundColor: item.color},/                ]}
              />/            </View>/            <Text style={styles.progressText} />{item.progress}/{item.target}</Text>/          </View>/        )}
      </View>/      {item.unlocked && (
        <Icon name="check-circle" size={20} color={item.color} />/      )}
    </TouchableOpacity>/  ), []);
  // 渲染会员特权卡片 *   const renderBenefitCard = useMemo((); => useMemo((); => useMemo((); => useMemo((); => useMemo((); => useMemo(() => ({ item }: { item: MemberBenefit}) => ( */
    <TouchableOpacity
      style={[styles.benefitCard, !item.available && styles.unavailableCard]}
      onPress={() = accessibilityLabel="TODO: 添加无障碍标签" /> useBenefit(item)}/    >
      <View style={styles.benefitHeader} />/        <View style={[styles.benefitIcon, { backgroundColor: colors.primary + '20'}]} />/          <Icon name={item.icon} size={20} color={colors.primary} />/        </View>/        <View style={styles.benefitInfo} />/          <Text style={styles.benefitTitle} />{item.title}</Text>/          <Text style={styles.benefitDesc} />{item.description}</Text>/        </View>/        {item.limit && (
          <View style={styles.usageInfo} />/            <Text style={styles.usageText} />/              {item.used || 0}/{item.limit}/            </Text>/          </View>/)}
      </View>/    </TouchableOpacity>/  ), []);
  // 渲染设置项 *   const renderSettingItem = useMemo((); => useMemo((); => useMemo((); => useMemo((); => useMemo((); => useMemo(() => (item: SettingItem) => ( */
    <TouchableOpacity
      key={item.id}
      style={styles.settingItem}
      onPress={item.onPress}
      disabled={item.type === 'switch'}
     accessibilityLabel="TODO: 添加无障碍标签" />/      <View style={styles.settingIcon} />/        <Icon name={item.icon} size={20} color={colors.primary} />/      </View>/
      <View style={styles.settingContent} />/        <Text style={styles.settingTitle} />{item.title}</Text>/        {item.subtitle && (
          <Text style={styles.settingSubtitle} />{item.subtitle}</Text>/)}
      </View>/
      <View style={styles.settingAction} />/        {item.type === 'switch' ? (<Switch
            value={item.value}
            onValueChange={item.onPress}
            trackColor={{ false: colors.border, true: colors.primary + '40'}}
            thumbColor={item.value ? colors.primary: colors.textSecondary} />/): (
          <Icon name="chevron-right" size= {20} color={colors.textSecondary} />/        )}
      </View>/    </TouchableOpacity>/  ), []);
  // 渲染设置分组 *   const renderSettingsSection = useMemo((); => useMemo((); => useMemo((); => useMemo((); => useMemo((); => useMemo((); => (section: (typeof settingsSections)[0]) => ( */
    <View key={section.title} style={styles.settingsSection} />/      <Text style={styles.sectionTitle} />{section.title}</Text>/      <View style={styles.sectionContent} />/        {section.items.map(renderSettingItem)}
      </View>/    </View>/  ), []);
  // 退出登录 *   const handleLogout = useCallback(() => { */
    Alert.alert('退出登录', '确定要退出当前账户吗？', [
      { text: '取消', style: 'cancel'},
      {
        text: '退出',
        style: 'destructive',
        onPress: () => Alert.alert('已退出', '您已成功退出登录');
      }
    ]);
  };
  // 记录渲染性能 *  */
  performanceMonitor.recordRender()
  return (
    <SafeAreaView style={styles.container} />/      <ScrollView
        style={styles.scrollView}
        showsVerticalScrollIndicator={false} />/        {// 用户信息头部 }/        {renderUserHeader()}
        {// 健康统计 }/        {renderHealthStats()}
        {// 标签栏 }/        {renderTabBar()}
        {// 内容区域 }/        <View style={styles.contentContainer} />/          {selectedTab === 'overview' && (
            <View />/              {settingsSections.map(renderSettingsSection)}
            </View>/          )}
          {selectedTab === 'agents' && (
            <View style={styles.agentsSection} />/              <Text style={styles.sectionTitle} />智能体交互记录</Text>/              <FlatList
                data={AGENT_INTERACTIONS}
                keyExtractor={item = /> item.id}/                renderItem={renderAgentCard}
                scrollEnabled={false} />/            </View>/          )}
          {selectedTab === 'achievements' && (
            <View style={styles.achievementsSection} />/              <Text style={styles.sectionTitle} />健康成就</Text>/              <FlatList
                data={HEALTH_ACHIEVEMENTS}
                keyExtractor={item = /> item.id}/                renderItem={renderAchievementCard}
                scrollEnabled={false} />/            </View>/          )}
          {selectedTab === 'benefits' && (
            <View style={styles.benefitsSection} />/              <Text style={styles.sectionTitle} />会员特权</Text>/              <FlatList
                data={MEMBER_BENEFITS}
                keyExtractor={item = /> item.id}/                renderItem={renderBenefitCard}
                scrollEnabled={false} />/            </View>/          )};
        </View>/
        {// 退出登录按钮 }/        <View style={styles.logoutContainer} />/          <TouchableOpacity style={styles.logoutButton} onPress={handleLogout} accessibilityLabel="TODO: 添加无障碍标签" />/            <Icon name="logout" size={20} color="#FF3B30" />/            <Text style={styles.logoutText} />退出登录</Text>/          </TouchableOpacity>/        </View>/      </ScrollView>/    </SafeAreaView>/  ;);
};
const styles = useMemo((); => useMemo((); => useMemo((); => useMemo((); => useMemo((); => useMemo(() => StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  scrollView: { flex: 1 },
  userHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 20,
    backgroundColor: colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  avatarContainer: {
    position: 'relative',
    marginRight: 16,
  },
  avatarText: {
    fontSize: 48,
    width: 80,
    height: 80,
    textAlign: 'center',
    textAlignVertical: 'center',
    backgroundColor: colors.primary + '20',
    borderRadius: 40,
    overflow: 'hidden',
  },
  memberBadge: {
    position: 'absolute',
    top: -4,
    right: -4,
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: colors.surface,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: colors.background,
  },
  healthScoreBadge: {
    position: 'absolute',
    bottom: -4,
    left: -4,
    width: 28,
    height: 28,
    borderRadius: 14,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: colors.background,
  },
  healthScoreText: {
    fontSize: 12,
    fontWeight: 'bold',
    color: 'white',
  },
  userInfo: { flex: 1 },
  userName: {
    fontSize: 20,
    fontWeight: 'bold',
    color: colors.text,
    marginBottom: 4,
  },
  userDetails: {
    fontSize: 14,
    color: colors.textSecondary,
    marginBottom: 6,
  },
  memberInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  memberLevel: {
    fontSize: 12,
    color: '#FFD700',
    marginLeft: 4,
    fontWeight: '600',
  },
  joinDate: {
    fontSize: 12,
    color: colors.textSecondary,
    marginLeft: 8,
  },
  quickActions: { flexDirection: 'row'  },
  quickActionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 8,
    paddingVertical: 4,
    marginRight: 12,
    backgroundColor: colors.primary + '10',
    borderRadius: 12,
  },
  quickActionText: {
    fontSize: 10,
    color: colors.primary,
    marginLeft: 4,
    fontWeight: '600',
  },
  editButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.primary + '20',
    justifyContent: 'center',
    alignItems: 'center',
  },
  statsContainer: {
    padding: 20,
    backgroundColor: colors.surface,
    marginTop: 8,
  },
  statsTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: colors.text,
    marginBottom: 16,
  },
  statsGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  statItem: {
    flex: 1,
    alignItems: 'center',
    paddingVertical: 12,
  },
  statValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: colors.text,
    marginTop: 8,
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: colors.textSecondary,
  },
  statUnit: {
    fontSize: 10,
    color: colors.textSecondary,
    marginTop: 2,
  },
  tabBar: {
    flexDirection: 'row',
    backgroundColor: colors.surface,
    marginHorizontal: 15,
    marginTop: 15,
    borderRadius: 12,
    padding: 4,
  },
  tabItem: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 8,
    borderRadius: 8,
  },
  activeTabItem: { backgroundColor: colors.primary + '20'  },
  tabLabel: {
    marginLeft: 4,
    fontSize: 12,
    color: colors.textSecondary,
  },
  activeTabLabel: {
    color: colors.primary,
    fontWeight: '600',
  },
  contentContainer: {
    paddingHorizontal: 15,
    paddingTop: 15,
  },
  agentsSection: { paddingBottom: 20  },
  agentCard: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: 15,
    marginBottom: 10,
  },
  agentHeader: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  agentEmoji: {
    fontSize: 32,
    marginRight: 12,
  },
  agentInfo: { flex: 1 },
  agentName: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.text,
    marginBottom: 4,
  },
  agentFeature: {
    fontSize: 12,
    color: colors.textSecondary,
  },
  agentStats: { alignItems: 'flex-end'  },
  interactionCount: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 2,
  },
  lastInteraction: {
    fontSize: 10,
    color: colors.textSecondary,
  },
  achievementsSection: { paddingBottom: 20  },
  achievementCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: 15,
    marginBottom: 10,
  },
  lockedCard: { opacity: 0.6  },
  achievementIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  achievementInfo: { flex: 1 },
  achievementTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.text,
    marginBottom: 4,
  },
  lockedText: { color: colors.textSecondary  },
  achievementDesc: {
    fontSize: 12,
    color: colors.textSecondary,
  },
  progressContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 8,
  },
  progressBar: {
    flex: 1,
    height: 4,
    backgroundColor: colors.border,
    borderRadius: 2,
    marginRight: 8,
  },
  progressFill: {
    height: '100%',
    borderRadius: 2,
  },
  progressText: {
    fontSize: 10,
    color: colors.textSecondary,
    minWidth: 30,
  },
  benefitsSection: { paddingBottom: 20  },
  benefitCard: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: 15,
    marginBottom: 10,
  },
  unavailableCard: { opacity: 0.5  },
  benefitHeader: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  benefitIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  benefitInfo: { flex: 1 },
  benefitTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.text,
    marginBottom: 4,
  },
  benefitDesc: {
    fontSize: 12,
    color: colors.textSecondary,
  },
  usageInfo: { alignItems: 'flex-end'  },
  usageText: {
    fontSize: 12,
    color: colors.primary,
    fontWeight: '600',
  },
  settingsSection: { marginBottom: 24  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.text,
    marginBottom: 12,
  },
  sectionContent: {
    backgroundColor: colors.surface,
    borderRadius: 12,
  },
  settingItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  settingIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.primary + '20',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  settingContent: { flex: 1 },
  settingTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.text,
    marginBottom: 2,
  },
  settingSubtitle: {
    fontSize: 14,
    color: colors.textSecondary,
  },
  settingAction: { marginLeft: 12  },
  logoutContainer: {
    padding: 20,
    marginTop: 24,
    marginBottom: 40,
  },
  logoutButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
    backgroundColor: colors.surface,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#FF3B30',
  },
  logoutText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FF3B30',
    marginLeft: 8,
  }
}), []);
export default React.memo(ProfileScreen);