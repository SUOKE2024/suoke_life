import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Image, FlatList, SafeAreaView, ActivityIndicator } from 'react-native';
import { useRoute, useNavigation, RouteProp } from '@react-navigation/native';
import { AgentType, agentInfo } from '../../api/agents';
import { lightTheme } from '../../config/theme';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

// 定义路由参数类型
type AgentChannelRouteParams = {
  agentType: AgentType;
};

// 功能项类型
interface FeatureItem {
  id: string;
  title: string;
  description: string;
  icon: string;
  screen: string;
  params?: object;
}

const AgentChannel = () => {
  const route = useRoute<RouteProp<Record<string, AgentChannelRouteParams>, string>>();
  const navigation = useNavigation<any>();
  const { agentType } = route.params;
  const agent = agentInfo[agentType];
  const colors = lightTheme.colors;

  const [loading, setLoading] = useState(true);
  const [features, setFeatures] = useState<FeatureItem[]>([]);

  // 根据智能体类型加载对应功能
  useEffect(() => {
    const loadFeatures = async () => {
      // 模拟加载数据
      setTimeout(() => {
        const agentFeatures = getAgentFeatures(agentType);
        setFeatures(agentFeatures);
        setLoading(false);
      }, 1000);
    };

    loadFeatures();
  }, [agentType]);

  // 根据智能体类型获取功能列表
  const getAgentFeatures = (type: AgentType): FeatureItem[] => {
    switch (type) {
      case AgentType.XIAOAI:
        return [
          {
            id: 'chat',
            title: '智能问诊',
            description: '与小艾进行自然语言对话，获取健康建议',
            icon: 'chat-processing',
            screen: 'XiaoaiChat'
          },
          {
            id: 'diagnosis',
            title: '四诊辨证',
            description: '通过望、闻、问、切四诊，分析您的体质状况',
            icon: 'stethoscope',
            screen: 'XiaoaiFourDiagnosis'
          },
          {
            id: 'records',
            title: '健康记录',
            description: '查看历史诊断记录与健康建议',
            icon: 'clipboard-text',
            screen: 'XiaoaiHealthRecords'
          },
          {
            id: 'constitution',
            title: '体质分析',
            description: '深入了解您的体质类型及相关调理建议',
            icon: 'account-details',
            screen: 'XiaoaiConstitution'
          }
        ];
      
      case AgentType.XIAOKE:
        return [
          {
            id: 'resources',
            title: '医疗资源',
            description: '查找并预约附近相关医疗资源',
            icon: 'hospital-building',
            screen: 'XiaokeMedicalResources'
          },
          {
            id: 'appointments',
            title: '预约管理',
            description: '管理您的医疗预约',
            icon: 'calendar-clock',
            screen: 'XiaokeAppointments'
          },
          {
            id: 'products',
            title: '农产品定制',
            description: '根据您的体质定制健康农产品',
            icon: 'food-apple',
            screen: 'XiaokeCustomProducts'
          },
          {
            id: 'trace',
            title: '产品溯源',
            description: '查看农产品全生命周期溯源信息',
            icon: 'barcode-scan',
            screen: 'XiaokeProductTrace'
          },
          {
            id: 'recommendations',
            title: '产品推荐',
            description: '获取适合您体质的产品推荐',
            icon: 'basket',
            screen: 'XiaokeProductRecommendations'
          }
        ];
      
      case AgentType.LAOKE:
        return [
          {
            id: 'knowledge',
            title: '知识图谱',
            description: '探索中医养生知识库',
            icon: 'brain',
            screen: 'LaokeKnowledge'
          },
          {
            id: 'learning',
            title: '学习路径',
            description: '个性化健康学习计划',
            icon: 'school',
            screen: 'LaokeLearningPath'
          },
          {
            id: 'community',
            title: '健康社区',
            description: '参与讨论，分享经验',
            icon: 'account-group',
            screen: 'LaokeCommunity'
          },
          {
            id: 'games',
            title: '养生游戏',
            description: '通过游戏化方式学习健康知识',
            icon: 'puzzle',
            screen: 'LaokeGames'
          }
        ];
      
      case AgentType.SOER:
        return [
          {
            id: 'healthPlan',
            title: '健康计划',
            description: '获取个性化健康管理计划',
            icon: 'calendar-check',
            screen: 'SoerHealthPlan'
          },
          {
            id: 'nutrition',
            title: '营养分析',
            description: '追踪和分析日常营养摄入',
            icon: 'food',
            screen: 'SoerNutrition'
          },
          {
            id: 'sensors',
            title: '传感器数据',
            description: '分析来自可穿戴设备的健康数据',
            icon: 'watch',
            screen: 'SoerSensorData'
          },
          {
            id: 'sleep',
            title: '睡眠管理',
            description: '分析睡眠质量并提供改善建议',
            icon: 'sleep',
            screen: 'SoerSleep'
          },
          {
            id: 'emotions',
            title: '情绪管理',
            description: '追踪情绪变化并获取平衡建议',
            icon: 'emoticon',
            screen: 'SoerEmotions'
          }
        ];
        
      default:
        return [];
    }
  };

  // 处理功能项点击
  const handleFeaturePress = (item: FeatureItem) => {
    navigation.navigate(item.screen, item.params);
  };

  // 渲染功能项
  const renderFeatureItem = ({ item }: { item: FeatureItem }) => (
    <TouchableOpacity
      style={styles.featureItem}
      onPress={() => handleFeaturePress(item)}
    >
      <View style={styles.featureIcon}>
        <Icon name={item.icon} size={28} color={colors.primary} />
      </View>
      <View style={styles.featureContent}>
        <Text style={styles.featureTitle}>{item.title}</Text>
        <Text style={styles.featureDescription}>{item.description}</Text>
      </View>
      <Icon name="chevron-right" size={24} color={colors.outline} />
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.container}>
      {/* 智能体头部 */}
      <View style={styles.header}>
        <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()}>
          <Icon name="arrow-left" size={24} color={colors.onSurface} />
        </TouchableOpacity>
        <View style={[styles.agentAvatar, { backgroundColor: agent.color + '20' }]}>
          <Icon name={agent.avatar} size={32} color={agent.color} />
        </View>
        <View style={styles.agentInfo}>
          <Text style={styles.agentName}>{agent.name}</Text>
          <Text style={styles.agentDescription}>{agent.description}</Text>
        </View>
      </View>

      {/* 功能列表 */}
      {loading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={colors.primary} />
          <Text style={styles.loadingText}>正在加载{agent.name}的功能...</Text>
        </View>
      ) : (
        <FlatList
          data={features}
          renderItem={renderFeatureItem}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.featureList}
          showsVerticalScrollIndicator={false}
        />
      )}

      {/* 智能问答入口 */}
      <TouchableOpacity
        style={styles.chatButton}
        onPress={() => navigation.navigate(`${agentType.charAt(0).toUpperCase() + agentType.slice(1)}Chat`)}
      >
        <Icon name="message-text" size={24} color="#FFFFFF" />
        <Text style={styles.chatButtonText}>开始对话</Text>
      </TouchableOpacity>
    </SafeAreaView>
  );
};

const colors = lightTheme.colors;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: colors.outlineVariant,
  },
  backButton: {
    marginRight: 16,
  },
  agentAvatar: {
    width: 60,
    height: 60,
    borderRadius: 30,
    marginRight: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  agentInfo: {
    flex: 1,
  },
  agentName: {
    fontSize: 20,
    fontWeight: 'bold',
    color: colors.onSurface,
    marginBottom: 4,
  },
  agentDescription: {
    fontSize: 14,
    color: colors.onSurfaceVariant,
    lineHeight: 18,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: colors.onSurfaceVariant,
  },
  featureList: {
    padding: 16,
  },
  featureItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 3,
    elevation: 2,
  },
  featureIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: colors.primaryContainer,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  featureContent: {
    flex: 1,
  },
  featureTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: colors.onSurface,
    marginBottom: 4,
  },
  featureDescription: {
    fontSize: 14,
    color: colors.onSurfaceVariant,
    lineHeight: 18,
  },
  chatButton: {
    position: 'absolute',
    right: 20,
    bottom: 20,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.primary,
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 4,
  },
  chatButtonText: {
    marginLeft: 8,
    fontSize: 16,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
});

export default AgentChannel; 