import React from 'react';
import { View, Text, StyleSheet, ScrollView, SafeAreaView, TouchableOpacity, Image } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { AgentType, agentInfo } from '../../api/agents';
import { lightTheme } from '../../config/theme';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

const AgentCollaboration = () => {
  const navigation = useNavigation<any>();
  const colors = lightTheme.colors;

  // 协作场景
  const collaborationScenarios = [
    {
      id: 'health_analysis',
      title: '健康综合分析',
      description: '小艾进行体质辨识，索儿提供健康计划，小克调度资源，老克提供知识支持',
      agents: [AgentType.XIAOAI, AgentType.SOER, AgentType.XIAOKE, AgentType.LAOKE],
      icon: 'account-heart',
      screen: 'HealthAnalysisFlow'
    },
    {
      id: 'seasonal_care',
      title: '四季养生方案',
      description: '索儿根据季节特点提供养生计划，小克定制相应农产品，老克提供理论指导',
      agents: [AgentType.SOER, AgentType.XIAOKE, AgentType.LAOKE],
      icon: 'weather-sunny',
      screen: 'SeasonalCareFlow'
    },
    {
      id: 'chronic_management',
      title: '慢性病管理',
      description: '小艾进行症状监测，索儿调整生活方式，小克安排医疗资源，老克提供教育内容',
      agents: [AgentType.XIAOAI, AgentType.SOER, AgentType.XIAOKE, AgentType.LAOKE],
      icon: 'medical-bag',
      screen: 'ChronicManagementFlow'
    },
    {
      id: 'family_health',
      title: '家庭健康管理',
      description: '为家庭每个成员提供个性化健康方案，并协调家庭共同养生活动',
      agents: [AgentType.XIAOAI, AgentType.SOER, AgentType.XIAOKE, AgentType.LAOKE],
      icon: 'home-heart',
      screen: 'FamilyHealthFlow'
    }
  ];

  // 渲染智能体头像
  const renderAgentAvatars = (agents: AgentType[]) => (
    <View style={styles.avatarContainer}>
      {agents.map((agentType, index) => (
        <View
          key={agentType}
          style={[
            styles.scenarioAvatar,
            { 
              marginLeft: index > 0 ? -15 : 0,
              backgroundColor: agentInfo[agentType].color + '20',
              justifyContent: 'center',
              alignItems: 'center'
            }
          ]}
        >
          <Icon name={agentInfo[agentType].avatar} size={18} color={agentInfo[agentType].color} />
        </View>
      ))}
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()}>
          <Icon name="arrow-left" size={24} color={colors.onSurface} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>智能体协同</Text>
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* 介绍部分 */}
        <View style={styles.introContainer}>
          <Text style={styles.introTitle}>四大智能体协同工作</Text>
          <Text style={styles.introText}>
            "索克生活"平台通过四大智能体的分布式协同工作模式，实现"辨证论治未病"的中医理念与现代预防医学的完美结合。
            每个智能体专注于不同领域，通过数据共享与协作决策，为用户提供全方位的健康管理服务。
          </Text>
          
          <View style={styles.collaborationDiagram}>
            <View style={styles.diagramPlaceholder}>
              <Icon name="sitemap" size={100} color={colors.primary} />
              <Text style={styles.diagramPlaceholderText}>智能体协作网络</Text>
            </View>
          </View>

          <Text style={styles.sectionTitle}>智能体协同场景</Text>
          <Text style={styles.sectionDescription}>
            以下是智能体协同的典型场景，通过多智能体协作，为您提供无缝的健康体验
          </Text>
        </View>

        {/* 协作场景列表 */}
        {collaborationScenarios.map(scenario => (
          <TouchableOpacity
            key={scenario.id}
            style={styles.scenarioCard}
            onPress={() => navigation.navigate(scenario.screen)}
          >
            <View style={styles.scenarioHeader}>
              <View style={styles.scenarioIcon}>
                <Icon name={scenario.icon} size={24} color={colors.primary} />
              </View>
              <Text style={styles.scenarioTitle}>{scenario.title}</Text>
            </View>
            
            <Text style={styles.scenarioDescription}>{scenario.description}</Text>
            
            <View style={styles.scenarioFooter}>
              {renderAgentAvatars(scenario.agents)}
              <Icon name="chevron-right" size={24} color={colors.outline} />
            </View>
          </TouchableOpacity>
        ))}

        {/* 协同工作原理 */}
        <View style={styles.principlesContainer}>
          <Text style={styles.sectionTitle}>协同工作原理</Text>
          
          <View style={styles.principleItem}>
            <View style={styles.principleIcon}>
              <Icon name="puzzle" size={24} color={colors.primary} />
            </View>
            <View style={styles.principleContent}>
              <Text style={styles.principleTitle}>互补性专长</Text>
              <Text style={styles.principleDescription}>
                每个智能体拥有不同专长领域，共同覆盖健康管理的全生命周期
              </Text>
            </View>
          </View>
          
          <View style={styles.principleItem}>
            <View style={styles.principleIcon}>
              <Icon name="sync" size={24} color={colors.primary} />
            </View>
            <View style={styles.principleContent}>
              <Text style={styles.principleTitle}>无缝数据共享</Text>
              <Text style={styles.principleDescription}>
                智能体间实时共享数据与洞察，确保决策协调一致
              </Text>
            </View>
          </View>
          
          <View style={styles.principleItem}>
            <View style={styles.principleIcon}>
              <Icon name="account-switch" size={24} color={colors.primary} />
            </View>
            <View style={styles.principleContent}>
              <Text style={styles.principleTitle}>动态角色分配</Text>
              <Text style={styles.principleDescription}>
                根据用户需求自动调整智能体角色分工与协作方式
              </Text>
            </View>
          </View>
          
          <View style={styles.principleItem}>
            <View style={styles.principleIcon}>
              <Icon name="brain" size={24} color={colors.primary} />
            </View>
            <View style={styles.principleContent}>
              <Text style={styles.principleTitle}>集体决策</Text>
              <Text style={styles.principleDescription}>
                通过多智能体协商达成更全面准确的健康决策与建议
              </Text>
            </View>
          </View>
        </View>
      </ScrollView>
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
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: colors.onSurface,
  },
  scrollContent: {
    padding: 16,
  },
  introContainer: {
    marginBottom: 24,
  },
  introTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: colors.onSurface,
    marginBottom: 12,
  },
  introText: {
    fontSize: 15,
    lineHeight: 22,
    color: colors.onSurfaceVariant,
    marginBottom: 20,
  },
  collaborationDiagram: {
    height: 200,
    justifyContent: 'center',
    alignItems: 'center',
    marginVertical: 20,
  },
  diagramImage: {
    width: '100%',
    height: '100%',
  },
  diagramPlaceholder: {
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.surfaceVariant,
    borderRadius: 12,
    padding: 20,
    width: '100%',
    height: '100%',
  },
  diagramPlaceholderText: {
    marginTop: 10,
    fontSize: 16,
    color: colors.primary,
    fontWeight: '600',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: colors.onSurface,
    marginBottom: 8,
  },
  sectionDescription: {
    fontSize: 14,
    color: colors.onSurfaceVariant,
    lineHeight: 20,
    marginBottom: 16,
  },
  scenarioCard: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 3,
    elevation: 2,
  },
  scenarioHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  scenarioIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.primaryContainer,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  scenarioTitle: {
    fontSize: 17,
    fontWeight: 'bold',
    color: colors.onSurface,
  },
  scenarioDescription: {
    fontSize: 14,
    lineHeight: 20,
    color: colors.onSurfaceVariant,
    marginBottom: 12,
  },
  scenarioFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  avatarContainer: {
    flexDirection: 'row',
  },
  scenarioAvatar: {
    width: 32,
    height: 32,
    borderRadius: 16,
    borderWidth: 2,
    borderColor: colors.surface,
  },
  principlesContainer: {
    marginTop: 12,
    marginBottom: 30,
  },
  principleItem: {
    flexDirection: 'row',
    marginBottom: 16,
  },
  principleIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.primaryContainer,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  principleContent: {
    flex: 1,
  },
  principleTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: colors.onSurface,
    marginBottom: 4,
  },
  principleDescription: {
    fontSize: 14,
    lineHeight: 20,
    color: colors.onSurfaceVariant,
  },
});

export default AgentCollaboration; 