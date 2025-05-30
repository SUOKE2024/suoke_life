import {
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { AgentIntegrationHub } from '../../components/agents/AgentIntegrationHub';
import { EnhancedHealthVisualization } from '../../components/health/EnhancedHealthVisualization';
import { UserExperienceOptimizer } from '../../components/common/UserExperienceOptimizer';
import { colors, spacing, typography } from '../../constants/theme';
import { AgentType } from '../../services/AgentCoordinationService';


import React, { useState, useCallback } from 'react';
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Dimensions,
  Alert,
} from 'react-native';


const { width } = Dimensions.get('window');

type TabType = 'agents' | 'health' | 'experience';

interface TabItem {
  id: TabType;
  title: string;
  icon: string;
  description: string;
}

const TABS: TabItem[] = [
  {
    id: 'agents',
    title: '智能体中心',
    icon: 'people',
    description: '四大智能体协作服务',
  },
  {
    id: 'health',
    title: '健康数据',
    icon: 'fitness',
    description: '全面健康状态监控',
  },
  {
    id: 'experience',
    title: '体验优化',
    icon: 'settings',
    description: '个性化使用体验',
  },
];

export const IntegratedExperienceScreen: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('agents');

  const handleAgentSelect = useMemo(() => useMemo(() => useCallback((agentId: AgentType) => {
    console.log('选择智能体:', agentId), []), []);
    // 这里可以添加智能体选择的逻辑
  }, []) // TODO: 检查依赖项 // TODO: 检查依赖项;

  const handleStartChat = useMemo(() => useMemo(() => useCallback((agentId: AgentType) => {
    Alert.alert('开始聊天', `即将与${agentId}开始对话`), []), []);
    // 这里可以添加跳转到聊天界面的逻辑
  }, []);

  const handleViewDetails = useMemo(() => useMemo(() => useCallback((agentId: AgentType) => {
    Alert.alert('查看详情', `查看${agentId}的详细信息`), []), []);
    // 这里可以添加查看智能体详情的逻辑
  }, []);

  const handleMetricPress = useMemo(() => useMemo(() => useCallback((metric: any) => {
    console.log('选择健康指标:', metric), []), []);
    // 这里可以添加健康指标详情的逻辑
  }, []) // TODO: 检查依赖项 // TODO: 检查依赖项;

  const handleExportData = useMemo(() => useMemo(() => useCallback(() => {
    Alert.alert('导出数据', '健康数据导出功能即将上线'), []), []);
    // 这里可以添加数据导出的逻辑
  }, []) // TODO: 检查依赖项 // TODO: 检查依赖项;

  const handleShareInsights = useMemo(() => useMemo(() => useCallback(() => {
    Alert.alert('分享洞察', '健康洞察分享功能即将上线'), []), []);
    // 这里可以添加分享功能的逻辑
  }, []) // TODO: 检查依赖项 // TODO: 检查依赖项;

  const handleSettingsChange = useMemo(() => useMemo(() => useCallback((settings: any) => {
    console.log('设置变更:', settings), []), []);
    // 这里可以添加设置变更的处理逻辑
  }, []) // TODO: 检查依赖项 // TODO: 检查依赖项;

  const handleFeedbackSubmit = useMemo(() => useMemo(() => useCallback((feedback: any) => {
    console.log('提交反馈:', feedback), []), []);
    // 这里可以添加反馈提交的逻辑
  }, []) // TODO: 检查依赖项 // TODO: 检查依赖项;

  const handlePerformanceAlert = useMemo(() => useMemo(() => useCallback((metrics: any) => {
    console.log('性能警告:', metrics), []), []);
    // 这里可以添加性能警告的处理逻辑
  }, []) // TODO: 检查依赖项 // TODO: 检查依赖项;

  // TODO: 将内联组件移到组件外部
const renderTabBar = useMemo(() => useMemo(() => () => (
    <View style={styles.tabBar}>
      {TABS.map((tab) => (
        <TouchableOpacity
          key={tab.id}
          style={[
            styles.tabItem,
            activeTab === tab.id && styles.activeTabItem,
          ]}
          onPress={() => setActiveTab(tab.id)}
        >
          <View style={[
            styles.tabIconContainer,
            activeTab === tab.id && styles.activeTabIconContainer,
          ]}>
            <Ionicons
              name={tab.icon as any}
              size={24}
              color={activeTab === tab.id ? colors.white : colors.textSecondary}
            />
          </View>
          <Text style={[
            styles.tabTitle,
            activeTab === tab.id && styles.activeTabTitle,
          ]}>
            {tab.title}
          </Text>
          <Text style={[
            styles.tabDescription,
            activeTab === tab.id && styles.activeTabDescription,
          ]}>
            {tab.description}
          </Text>
        </TouchableOpacity>
      ))}
    </View>
  ), []), []);

  const renderContent = useMemo(() => useMemo(() => useCallback( () => {, []), []), []);
    switch (activeTab) {
      case 'agents':
        return (
          <AgentIntegrationHub
            onAgentSelect={handleAgentSelect}
            onStartChat={handleStartChat}
            onViewDetails={handleViewDetails}
          />
        );
      case 'health':
        return (
          <EnhancedHealthVisualization
            onMetricPress={handleMetricPress}
            onExportData={handleExportData}
            onShareInsights={handleShareInsights}
          />
        );
      case 'experience':
        return (
          <UserExperienceOptimizer
            onSettingsChange={handleSettingsChange}
            onFeedbackSubmit={handleFeedbackSubmit}
            onPerformanceAlert={handlePerformanceAlert}
          />
        );
      default:
        return null;
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      {/* 头部 */}
      <View style={styles.header}>
        <View>
          <Text style={styles.title}>索克生活</Text>
          <Text style={styles.subtitle}>智能健康管理平台</Text>
        </View>
        <TouchableOpacity
          style={styles.notificationButton}
          onPress={() => Alert.alert('通知', '暂无新通知')}
        >
          <Ionicons name="notifications" size={24} color={colors.textPrimary} />
          <View style={styles.notificationBadge}>
            <Text style={styles.notificationBadgeText}>3</Text>
          </View>
        </TouchableOpacity>
      </View>

      {/* 标签栏 */}
      {renderTabBar()}

      {/* 内容区域 */}
      <View style={styles.contentContainer}>
        {renderContent()}
      </View>
    </SafeAreaView>
  );
};

const styles = useMemo(() => useMemo(() => StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    backgroundColor: colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  title: {
    fontSize: typography.fontSize['2xl'],
    fontWeight: '700',
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  subtitle: {
    fontSize: typography.fontSize.base,
    color: colors.textSecondary,
  },
  notificationButton: {
    position: 'relative',
    padding: spacing.sm,
  },
  notificationBadge: {
    position: 'absolute',
    top: spacing.xs,
    right: spacing.xs,
    backgroundColor: colors.error,
    borderRadius: 10,
    minWidth: 20,
    height: 20,
    alignItems: 'center',
    justifyContent: 'center',
  },
  notificationBadgeText: {
    fontSize: typography.fontSize.xs,
    color: colors.white,
    fontWeight: '600',
  },
  tabBar: {
    flexDirection: 'row',
    backgroundColor: colors.surface,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  tabItem: {
    flex: 1,
    alignItems: 'center',
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.sm,
    marginHorizontal: spacing.xs,
    borderRadius: 12,
    backgroundColor: colors.background,
  },
  activeTabItem: {
    backgroundColor: colors.primary,
  },
  tabIconContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: colors.gray100,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.sm,
  },
  activeTabIconContainer: {
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
  },
  tabTitle: {
    fontSize: typography.fontSize.sm,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: spacing.xs,
    textAlign: 'center',
  },
  activeTabTitle: {
    color: colors.white,
  },
  tabDescription: {
    fontSize: typography.fontSize.xs,
    color: colors.textSecondary,
    textAlign: 'center',
    lineHeight: 16,
  },
  activeTabDescription: {
    color: 'rgba(255, 255, 255, 0.8)',
  },
  contentContainer: {
    flex: 1,
  },
}), []), []); 