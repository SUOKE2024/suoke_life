import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { AgentAvatar, Button, Card, Loading } from '../ui';
import { colors, spacing, typography } from '../../constants/theme';
import { AgentCoordinationService, AgentType, AgentStatus } from '../../services/AgentCoordinationService';


import React, { useState, useEffect, useCallback, useMemo } from 'react';
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Dimensions,
  Animated,
  Alert,
  RefreshControl,
} from 'react-native';

const { width, height } = Dimensions.get('window');

interface AgentInfo {
  id: AgentType;
  name: string;
  description: string;
  specialties: string[];
  color: string;
  gradient: string[];
  icon: string;
  avatar: string;
}

interface AgentIntegrationHubProps {
  onAgentSelect?: (agentId: AgentType) => void;
  onStartChat?: (agentId: AgentType) => void;
  onViewDetails?: (agentId: AgentType) => void;
}

const AGENT_INFO: Record<AgentType, AgentInfo> = {
  xiaoai: {
    id: 'xiaoai',
    name: '小艾',
    description: '健康助手 & 首页聊天频道版主',
    specialties: ['健康咨询', '四诊合参', '症状分析', '健康建议'],
    color: '#4CAF50',
    gradient: ['#4CAF50', '#66BB6A'],
    icon: 'chatbubble-ellipses',
    avatar: '🤖',
  },
  xiaoke: {
    id: 'xiaoke',
    name: '小克',
    description: 'SUOKE频道版主 & 服务订阅专家',
    specialties: ['服务推荐', '订阅管理', '产品咨询', '用户支持'],
    color: '#2196F3',
    gradient: ['#2196F3', '#42A5F5'],
    icon: 'storefront',
    avatar: '🛍️',
  },
  laoke: {
    id: 'laoke',
    name: '老克',
    description: '探索频道版主 & 知识传播者',
    specialties: ['中医知识', '养生指导', '文化传承', '学术研究'],
    color: '#FF9800',
    gradient: ['#FF9800', '#FFB74D'],
    icon: 'library',
    avatar: '📚',
  },
  soer: {
    id: 'soer',
    name: '索儿',
    description: 'LIFE频道版主 & 生活陪伴者',
    specialties: ['生活指导', '情感支持', '习惯养成', '心理健康'],
    color: '#E91E63',
    gradient: ['#E91E63', '#F06292'],
    icon: 'heart',
    avatar: '💝',
  },
};

export const AgentIntegrationHub: React.FC<AgentIntegrationHubProps> = ({
  onAgentSelect,
  onStartChat,
  onViewDetails,
}) => {
  const [selectedAgent, setSelectedAgent] = useState<AgentType>('xiaoai');
  const [agentStatuses, setAgentStatuses] = useState<Record<AgentType, AgentStatus>>({} as any);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [coordinationService] = useState(() => new AgentCoordinationService());
  const [animatedValue] = useState(new Animated.Value(0));

  // 初始化服务
  useEffect(() => {
    initializeService();
  }, []) // TODO: 检查依赖项 // TODO: 检查依赖项 // TODO: 检查依赖项 // TODO: 检查依赖项 // TODO: 检查依赖项;

  // 启动动画
  useEffect(() => {
    Animated.timing(animatedValue, {
      toValue: 1,
      duration: 800,
      useNativeDriver: true,
    }).start();
  }, []);

  const initializeService = useMemo(() => useMemo(() => useMemo(() => async () => {
    try {
      setLoading(true), []), []), []);
      await coordinationService.initialize();
      await loadAgentStatuses();
    } catch (error) {
      console.error('初始化智能体服务失败:', error);
      Alert.alert('错误', '智能体服务初始化失败');
    } finally {
      setLoading(false);
    }
  };

  const loadAgentStatuses = useMemo(() => useMemo(() => useMemo(() => async () => {
    try {
      const statuses = await coordinationService.getAgentStatus() as AgentStatus[], []), []), []);
      const statusMap = useMemo(() => useMemo(() => useMemo(() => statuses.reduce((acc, status) => {
        acc[status.id] = status, []), []), []);
        return acc;
      }, {} as Record<AgentType, AgentStatus>);
      setAgentStatuses(statusMap);
    } catch (error) {
      console.error('加载智能体状态失败:', error);
    }
  };

  const onRefresh = useMemo(() => useMemo(() => useMemo(() => useCallback(async () => {
    setRefreshing(true), []), []), []);
    await loadAgentStatuses();
    setRefreshing(false);
  }, []);

  const handleAgentSelect = useMemo(() => useMemo(() => useMemo(() => useCallback((agentId: AgentType) => {
    setSelectedAgent(agentId), []), []), []);
    onAgentSelect?.(agentId);
  }, [onAgentSelect]);

  const handleStartChat = useMemo(() => useMemo(() => useMemo(() => useCallback((agentId: AgentType) => {
    onStartChat?.(agentId), []), []), []);
  }, [onStartChat]);

  const handleViewDetails = useMemo(() => useMemo(() => useMemo(() => useCallback((agentId: AgentType) => {
    onViewDetails?.(agentId), []), []), []);
  }, [onViewDetails]);

  const renderAgentCard = useMemo(() => useMemo(() => useMemo(() => useCallback((agentInfo: AgentInfo) => {
    const status = agentStatuses[agentInfo.id], []), []), []);
    const isSelected = useMemo(() => useMemo(() => useMemo(() => selectedAgent === agentInfo.id, []), []), []);
    const isOnline = useMemo(() => useMemo(() => useMemo(() => status?.isOnline ?? false, []), []), []);

    return (
      <Animated.View
        key={agentInfo.id}
        style={[
          styles.agentCard,
          isSelected && styles.selectedAgentCard,
          { backgroundColor: agentInfo.color },
          {
            opacity: animatedValue,
            transform: [
              {
                translateY: animatedValue.interpolate({
                  inputRange: [0, 1],
                  outputRange: [50, 0],
                }),
              },
            ],
          },
        ]}
      >
        <TouchableOpacity
          onPress={() => handleAgentSelect(agentInfo.id)}
          activeOpacity={0.8}
          style={styles.agentCardContent}
        >
          {/* 状态指示器 */}
          <View style={[
            styles.statusIndicator,
            { backgroundColor: isOnline ? '#4CAF50' : '#F44336' },
          ]} />

          {/* 智能体头像 */}
          <View style={styles.agentAvatarContainer}>
            <AgentAvatar
              agent={agentInfo.id}
              size={60}
              online={isOnline}
              style={styles.agentAvatar}
            />
            <Text style={styles.agentEmoji}>{agentInfo.avatar}</Text>
          </View>

          {/* 智能体信息 */}
          <View style={styles.agentInfo}>
            <Text style={styles.agentName}>{agentInfo.name}</Text>
            <Text style={styles.agentDescription}>{agentInfo.description}</Text>
            
            {/* 专长标签 */}
            <View style={styles.specialtiesContainer}>
              {agentInfo.specialties.slice(0, 2).map((specialty, index) => (
                <View key={index} style={styles.specialtyTag}>
                  <Text style={styles.specialtyText}>{specialty}</Text>
                </View>
              ))}
            </View>

            {/* 性能指标 */}
            {status && (
              <View style={styles.metricsContainer}>
                <View style={styles.metric}>
                  <Text style={styles.metricLabel}>工作负载</Text>
                  <View style={styles.progressBar}>
                    <View 
                      style={[
                        styles.progressFill,
                        { 
                          width: `${status.workload}%`,
                          backgroundColor: status.workload > 80 ? '#F44336' : 
                                         status.workload > 60 ? '#FF9800' : '#4CAF50',
                        },
                      ]} 
                    />
                  </View>
                  <Text style={styles.metricValue}>{status.workload}%</Text>
                </View>
                
                <View style={styles.metricsRow}>
                  <View style={styles.smallMetric}>
                    <Text style={styles.smallMetricLabel}>准确率</Text>
                    <Text style={styles.smallMetricValue}>
                      {(status.performance.accuracy * 100).toFixed(1)}%
                    </Text>
                  </View>
                  <View style={styles.smallMetric}>
                    <Text style={styles.smallMetricLabel}>响应</Text>
                    <Text style={styles.smallMetricValue}>
                      {status.performance.responseTime}ms
                    </Text>
                  </View>
                </View>
              </View>
            )}
          </View>

          {/* 操作按钮 */}
          <View style={styles.actionButtons}>
            <TouchableOpacity
              style={[styles.actionButton, styles.chatButton]}
              onPress={() => handleStartChat(agentInfo.id)}
            >
              <Ionicons name="chatbubble" size={16} color="white" />
              <Text style={styles.actionButtonText}>聊天</Text>
            </TouchableOpacity>
            
            <TouchableOpacity
              style={[styles.actionButton, styles.detailButton]}
              onPress={() => handleViewDetails(agentInfo.id)}
            >
              <Ionicons name="information-circle" size={16} color={agentInfo.color} />
              <Text style={[styles.actionButtonText, { color: agentInfo.color }]}>详情</Text>
            </TouchableOpacity>
          </View>
        </TouchableOpacity>
      </Animated.View>
    );
  }, [selectedAgent, agentStatuses, animatedValue, handleAgentSelect, handleStartChat, handleViewDetails]);

  const renderSelectedAgentDetails = useMemo(() => useMemo(() => useMemo(() => useMemo(() => {
    const agentInfo = AGENT_INFO[selectedAgent], []), []), []);
    const status = useMemo(() => useMemo(() => useMemo(() => agentStatuses[selectedAgent], []), []), []);

    return (
      <Card style={styles.detailsCard}>
        <View style={styles.detailsHeader}>
          <AgentAvatar agent={selectedAgent} size={40} online={status?.isOnline} />
          <View style={styles.detailsHeaderText}>
            <Text style={styles.detailsTitle}>{agentInfo.name} 详细信息</Text>
            <Text style={styles.detailsSubtitle}>
              {status?.isOnline ? '在线' : '离线'} • 
              {status?.currentTask ? ` 执行中: ${status.currentTask}` : ' 空闲中'}
            </Text>
          </View>
        </View>

        <View style={styles.detailsContent}>
          <Text style={styles.sectionTitle}>专业领域</Text>
          <View style={styles.specialtiesGrid}>
            {agentInfo.specialties.map((specialty, index) => (
              <View key={index} style={styles.specialtyChip}>
                <Text style={styles.specialtyChipText}>{specialty}</Text>
              </View>
            ))}
          </View>

          {status && (
            <>
              <Text style={styles.sectionTitle}>性能状态</Text>
              <View style={styles.performanceGrid}>
                <View style={styles.performanceItem}>
                  <Text style={styles.performanceLabel}>准确率</Text>
                  <Text style={styles.performanceValue}>
                    {(status.performance.accuracy * 100).toFixed(1)}%
                  </Text>
                </View>
                <View style={styles.performanceItem}>
                  <Text style={styles.performanceLabel}>响应时间</Text>
                  <Text style={styles.performanceValue}>
                    {status.performance.responseTime}ms
                  </Text>
                </View>
                <View style={styles.performanceItem}>
                  <Text style={styles.performanceLabel}>满意度</Text>
                  <Text style={styles.performanceValue}>
                    {(status.performance.userSatisfaction * 100).toFixed(1)}%
                  </Text>
                </View>
                <View style={styles.performanceItem}>
                  <Text style={styles.performanceLabel}>工作负载</Text>
                  <Text style={styles.performanceValue}>{status.workload}%</Text>
                </View>
              </View>
            </>
          )}
        </View>
      </Card>
    );
  }, [selectedAgent, agentStatuses]);

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <Loading text="正在初始化智能体服务..." />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      {/* 头部 */}
      <View style={styles.header}>
        <Text style={styles.title}>智能体中心</Text>
        <Text style={styles.subtitle}>四大智能体为您提供专业服务</Text>
      </View>

      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            colors={[colors.primary]}
            tintColor={colors.primary}
          />
        }
        showsVerticalScrollIndicator={false}
      >
        {/* 智能体卡片网格 */}
        <View style={styles.agentsGrid}>
          {Object.values(AGENT_INFO).map(renderAgentCard)}
        </View>

        {/* 选中智能体的详细信息 */}
        {renderSelectedAgentDetails}

        {/* 快速操作 */}
        <Card style={styles.quickActionsCard}>
          <Text style={styles.sectionTitle}>快速操作</Text>
          <View style={styles.quickActions}>
            <Button
              title="开始协作任务"
              onPress={() => Alert.alert('功能开发中', '智能体协作功能即将上线')}
              style={styles.quickActionButton}
              variant="outline"
            />
            <Button
              title="查看协作历史"
              onPress={() => Alert.alert('功能开发中', '协作历史功能即将上线')}
              style={styles.quickActionButton}
              variant="outline"
            />
          </View>
        </Card>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = useMemo(() => useMemo(() => useMemo(() => StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
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
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    padding: spacing.lg,
  },
  agentsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: spacing.lg,
  },
  agentCard: {
    width: (width - spacing.lg * 3) / 2,
    marginBottom: spacing.md,
    borderRadius: 16,
    overflow: 'hidden',
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
  },
  selectedAgentCard: {
    elevation: 8,
    shadowOpacity: 0.2,
    shadowRadius: 12,
  },
  agentCardContent: {
    padding: spacing.md,
    minHeight: 200,
  },
  statusIndicator: {
    position: 'absolute',
    top: spacing.sm,
    right: spacing.sm,
    width: 12,
    height: 12,
    borderRadius: 6,
    borderWidth: 2,
    borderColor: 'white',
  },
  agentAvatarContainer: {
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  agentAvatar: {
    marginBottom: spacing.xs,
  },
  agentEmoji: {
    fontSize: 24,
  },
  agentInfo: {
    flex: 1,
  },
  agentName: {
    fontSize: typography.fontSize.lg,
    fontWeight: '700',
    color: 'white',
    textAlign: 'center',
    marginBottom: spacing.xs,
  },
  agentDescription: {
    fontSize: typography.fontSize.xs,
    color: 'rgba(255, 255, 255, 0.9)',
    textAlign: 'center',
    marginBottom: spacing.sm,
  },
  specialtiesContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'center',
    marginBottom: spacing.sm,
  },
  specialtyTag: {
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    paddingHorizontal: spacing.xs,
    paddingVertical: 2,
    borderRadius: 8,
    margin: 2,
  },
  specialtyText: {
    fontSize: 10,
    color: 'white',
  },
  metricsContainer: {
    marginBottom: spacing.sm,
  },
  metric: {
    marginBottom: spacing.xs,
  },
  metricLabel: {
    fontSize: 10,
    color: 'rgba(255, 255, 255, 0.8)',
    marginBottom: 2,
  },
  progressBar: {
    height: 4,
    backgroundColor: 'rgba(255, 255, 255, 0.3)',
    borderRadius: 2,
    marginBottom: 2,
  },
  progressFill: {
    height: '100%',
    borderRadius: 2,
  },
  metricValue: {
    fontSize: 10,
    color: 'white',
    textAlign: 'right',
  },
  metricsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  smallMetric: {
    flex: 1,
    alignItems: 'center',
  },
  smallMetricLabel: {
    fontSize: 9,
    color: 'rgba(255, 255, 255, 0.8)',
  },
  smallMetricValue: {
    fontSize: 10,
    color: 'white',
    fontWeight: 'bold',
  },
  actionButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  actionButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: spacing.xs,
    paddingHorizontal: spacing.sm,
    borderRadius: 8,
    marginHorizontal: 2,
  },
  chatButton: {
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
  },
  detailButton: {
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
  },
  actionButtonText: {
    fontSize: 12,
    color: 'white',
    marginLeft: spacing.xs,
  },
  detailsCard: {
    marginBottom: spacing.lg,
  },
  detailsHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  detailsHeaderText: {
    marginLeft: spacing.sm,
    flex: 1,
  },
  detailsTitle: {
    fontSize: typography.fontSize.lg,
    fontWeight: '700',
    color: colors.textPrimary,
  },
  detailsSubtitle: {
    fontSize: typography.fontSize.base,
    color: colors.textSecondary,
  },
  detailsContent: {
    // 内容样式
  },
  sectionTitle: {
    fontSize: typography.fontSize.lg,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: spacing.sm,
  },
  specialtiesGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: spacing.md,
  },
  specialtyChip: {
    backgroundColor: colors.primary + '20',
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: 16,
    margin: 4,
  },
  specialtyChipText: {
    fontSize: typography.fontSize.xs,
    color: colors.primary,
  },
  performanceGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: spacing.md,
  },
  performanceItem: {
    width: '48%',
    backgroundColor: colors.surface,
    padding: spacing.sm,
    borderRadius: 8,
    marginBottom: spacing.xs,
    alignItems: 'center',
  },
  performanceLabel: {
    fontSize: typography.fontSize.xs,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
  },
  performanceValue: {
    fontSize: typography.fontSize.lg,
    fontWeight: '700',
    color: colors.textPrimary,
  },
  quickActionsCard: {
    marginBottom: spacing.lg,
  },
  quickActions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  quickActionButton: {
    flex: 1,
    marginHorizontal: spacing.xs,
  },
}), []), []), []); 