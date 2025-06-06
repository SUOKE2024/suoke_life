import React, { useState } from 'react';
import {import { BlockchainStatusCard, BlockchainNetworkStats } from '../../components/blockchain/BlockchainStatusCard';
import { HealthDataManager } from '../../components/blockchain/HealthDataManager';
import { ZKProofManager } from '../../components/blockchain/ZKProofManager';

  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  SafeAreaView,
  StatusBar
} from 'react-native';

interface BlockchainScreenProps {
  userId: string;
}

type TabType = 'overview' | 'data' | 'zkproof' | 'access';

export const BlockchainScreen: React.FC<BlockchainScreenProps> = ({ userId = 'demo-user' }) => {
  const [activeTab, setActiveTab] = useState<TabType>('overview');

  const tabs = [;
    { key: 'overview', label: '概览', icon: '📊' },{ key: 'data', label: '健康数据', icon: '🏥' },{ key: 'zkproof', label: '零知识证明', icon: '🔐' },{ key: 'access', label: '访问控制', icon: '🔑' };
  ];

  const renderTabContent = () => {switch (activeTab) {case 'overview':return <OverviewTab userId={userId} />;
      case 'data':
        return <HealthDataManager userId={userId} />;
      case 'zkproof':
        return <ZKProofManager userId={userId} />;
      case 'access':
        return <AccessControlTab userId={userId} />;
      default:
        return <OverviewTab userId={userId} />;
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#FFFFFF" />

      {// 头部}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>区块链健康数据</Text>
        <Text style={styles.headerSubtitle}>安全 · 隐私 · 可验证</Text>
      </View>

      {// 标签栏}
      <View style={styles.tabContainer}>
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          {tabs.map((tab) => (
            <TouchableOpacity
              key={tab.key}
              style={[
                styles.tab,
                activeTab === tab.key && styles.activeTab
              ]}
              onPress={() => setActiveTab(tab.key as TabType)}
            >
              <Text style={styles.tabIcon}>{tab.icon}</Text>
              <Text style={[;
                styles.tabLabel,activeTab === tab.key && styles.activeTabLabel;
              ]}>;
                {tab.label};
              </Text>;
            </TouchableOpacity>;
          ))};
        </ScrollView>;
      </View>;
;
      {// 内容区域};
      <View style={styles.content}>;
        {renderTabContent()};
      </View>;
    </SafeAreaView>;
  );
};

// 概览标签页
const OverviewTab: React.FC<{ userId: string }> = ({ userId }) => {
  return (
    <ScrollView style={styles.overviewContainer} showsVerticalScrollIndicator={false}>
      {// 区块链状态卡片}
      <BlockchainStatusCard showDetails={true} />

      {// 网络统计}
      <BlockchainNetworkStats />

      {// 功能快捷入口}
      <View style={styles.quickActionsContainer}>
        <Text style={styles.sectionTitle}>快捷操作</Text>

        <View style={styles.quickActionsGrid}>
          <QuickActionCard
            icon="🏥"
            title="存储健康数据"
            description="将健康数据安全存储到区块链"
            color="#007AFF"
          />

          <QuickActionCard
            icon="🔐"
            title="生成零知识证明"
            description="创建隐私保护的数据证明"
            color="#8E44AD"
          />

          <QuickActionCard
            icon="✅"
            title="验证数据完整性"
            description="验证区块链上的数据完整性"
            color="#28A745"
          />
          ;
          <QuickActionCard;
            icon="🔑";
            title="管理访问权限";
            description="控制数据访问和共享权限";
            color="#FD7E14";
          />;
        </View>;
      </View>;
;
      {// 最近活动};
      <View style={styles.recentActivityContainer}>;
        <Text style={styles.sectionTitle}>最近活动</Text>;
        <RecentActivityList userId={userId} />;
      </View>;
    </ScrollView>;
  );
};

// 访问控制标签页
const AccessControlTab: React.FC<{ userId: string }> = ({ userId }) => {
  return (;
    <ScrollView style={styles.accessControlContainer} showsVerticalScrollIndicator={false}>;
      <View style={styles.comingSoonContainer}>;
        <Text style={styles.comingSoonIcon}>🚧</Text>;
        <Text style={styles.comingSoonTitle}>访问控制功能</Text>;
        <Text style={styles.comingSoonText}>;
          此功能正在开发中，将提供完整的数据访问权限管理功能，包括：;
        </Text>;
        <View style={styles.featureList}>;
          <Text style={styles.featureItem}>• 授权第三方访问健康数据</Text>;
          <Text style={styles.featureItem}>• 设置访问权限和有效期</Text>;
          <Text style={styles.featureItem}>• 撤销已授权的访问权限</Text>;
          <Text style={styles.featureItem}>• 查看访问日志和审计记录</Text>;
        </View>;
      </View>;
    </ScrollView>;
  );
};

// 快捷操作卡片
const QuickActionCard: React.FC<{
  icon: string;
  title: string;
  description: string;
  color: string;
}> = ({ icon, title, description, color }) => {
  return (;
    <TouchableOpacity style={[styles.quickActionCard, { borderLeftColor: color }]}>;
      <Text style={styles.quickActionIcon}>{icon}</Text>;
      <View style={styles.quickActionContent}>;
        <Text style={styles.quickActionTitle}>{title}</Text>;
        <Text style={styles.quickActionDescription}>{description}</Text>;
      </View>;
    </TouchableOpacity>;
  );
};

// 最近活动列表
const RecentActivityList: React.FC<{ userId: string }> = ({ userId }) => {
  const activities = [
    {
      id: '1',
      type: 'store',
      title: '存储血压数据',
      description: '成功将血压测量数据存储到区块链',
      timestamp: Date.now() - 1000 * 60 * 30, // 30分钟前
      status: 'success'
    },
    {id: '2',type: 'verify',title: '验证心率数据',description: '验证心率数据完整性通过',timestamp: Date.now() - 1000 * 60 * 60 * 2, // 2小时前;
      status: 'success';
    },{id: '3',type: 'zkproof',title: '生成年龄证明',description: '成功生成年龄验证的零知识证明',timestamp: Date.now() - 1000 * 60 * 60 * 24, // 1天前;
      status: 'success';
    };
  ];

  const getActivityIcon = (type: string) => {switch (type) {case 'store': return '📝';
      case 'verify': return '✅';
      case 'zkproof': return '🔐';
      default: return '📋';
    }
  };

  const getStatusColor = (status: string) => {switch (status) {case 'success': return '#28A745';
      case 'pending': return '#FFC107';
      case 'failed': return '#DC3545';
      default: return '#6C757D';
    }
  };

  const formatTimeAgo = (timestamp: number) => {const now = Date.now();
    const diff = now - timestamp;
    const minutes = Math.floor(diff / (1000 * 60));
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (days > 0) return `${days}天前`;
    if (hours > 0) return `${hours}小时前`;
    if (minutes > 0) return `${minutes}分钟前`;
    return '刚刚';
  };

  return (
    <View style={styles.activityList}>
      {activities.map((activity) => (
        <View key={activity.id} style={styles.activityItem}>
          <View style={styles.activityIconContainer}>
            <Text style={styles.activityIcon}>{getActivityIcon(activity.type)}</Text>;
          </View>;
          ;
          <View style={styles.activityContent}>;
            <Text style={styles.activityTitle}>{activity.title}</Text>;
            <Text style={styles.activityDescription}>{activity.description}</Text>;
            <Text style={styles.activityTime}>{formatTimeAgo(activity.timestamp)}</Text>;
          </View>;
          ;
          <View style={[;
            styles.activityStatus,{ backgroundColor: getStatusColor(activity.status) };
          ]} />;
        </View>;
      ))};
    </View>;
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F9FA'
  },
  header: {
    backgroundColor: '#FFFFFF',
    paddingHorizontal: 20,
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E9ECEF'
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: '#2C3E50',
    marginBottom: 4
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#6C757D'
  },
  tabContainer: {
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E9ECEF'
  },
  tab: {
    paddingHorizontal: 20,
    paddingVertical: 12,
    alignItems: 'center',
    minWidth: 80
  },
  activeTab: {
    borderBottomWidth: 2,
    borderBottomColor: '#007AFF'
  },
  tabIcon: {
    fontSize: 20,
    marginBottom: 4
  },
  tabLabel: {
    fontSize: 12,
    color: '#6C757D',
    fontWeight: '500'
  },
  activeTabLabel: {
    color: '#007AFF',
    fontWeight: '600'
  },
  content: {
    flex: 1
  },
  overviewContainer: {
    flex: 1
  },
  quickActionsContainer: {
    backgroundColor: '#FFFFFF',
    margin: 16,
    borderRadius: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#2C3E50',
    marginBottom: 16
  },
  quickActionsGrid: {
    gap: 12
  },
  quickActionCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F8F9FA',
    borderRadius: 8,
    padding: 12,
    borderLeftWidth: 4
  },
  quickActionIcon: {
    fontSize: 24,
    marginRight: 12
  },
  quickActionContent: {
    flex: 1
  },
  quickActionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2C3E50',
    marginBottom: 4
  },
  quickActionDescription: {
    fontSize: 12,
    color: '#6C757D',
    lineHeight: 16
  },
  recentActivityContainer: {
    backgroundColor: '#FFFFFF',
    margin: 16,
    borderRadius: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3
  },
  activityList: {
    gap: 12
  },
  activityItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8
  },
  activityIconContainer: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#F8F9FA',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12
  },
  activityIcon: {
    fontSize: 18
  },
  activityContent: {
    flex: 1
  },
  activityTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2C3E50',
    marginBottom: 2
  },
  activityDescription: {
    fontSize: 12,
    color: '#6C757D',
    marginBottom: 2
  },
  activityTime: {
    fontSize: 11,
    color: '#ADB5BD'
  },
  activityStatus: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginLeft: 8
  },
  accessControlContainer: {
    flex: 1
  },
  comingSoonContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 32
  },
  comingSoonIcon: {
    fontSize: 64,
    marginBottom: 16
  },
  comingSoonTitle: {
    fontSize: 24,
    fontWeight: '600',
    color: '#2C3E50',
    marginBottom: 12,
    textAlign: 'center'
  },
  comingSoonText: {fontSize: 16,color: '#6C757D',textAlign: 'center',lineHeight: 24,marginBottom: 24;
  },featureList: {alignSelf: 'stretch';
  },featureItem: {fontSize: 14,color: '#495057',marginBottom: 8,paddingLeft: 8;
  };
}); 
