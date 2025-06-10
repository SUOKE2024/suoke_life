import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import React, { useEffect, useState } from 'react';
import {
    Dimensions,
    ScrollView,
    StyleSheet,
    Text,
    TouchableOpacity,
    View
} from 'react-native';
import { BPartnerService } from '../../services/business/BPartnerService';
import { EcosystemRevenueService } from '../../services/business/EcosystemRevenueService';
import { SubscriptionService } from '../../services/business/SubscriptionService';

const { width } = Dimensions.get('window');

interface BusinessMetrics {
  totalMRR: number;
  subscriptionMRR: number;
  partnerMRR: number;
  ecosystemMRR: number;
  growthRate: number;
  activeSubscribers: number;
  partnerCount: number;
  productCount: number;
}

export const BusinessDashboard: React.FC = () => {
  const [subscriptionService] = useState(new SubscriptionService());
  const [partnerService] = useState(new BPartnerService());
  const [ecosystemService] = useState(new EcosystemRevenueService());
  const [metrics, setMetrics] = useState<BusinessMetrics>({
    totalMRR: 0;
    subscriptionMRR: 0;
    partnerMRR: 0;
    ecosystemMRR: 0;
    growthRate: 0;
    activeSubscribers: 0;
    partnerCount: 0;
    productCount: 0
  ;});
  const [selectedTimeframe, setSelectedTimeframe] = useState<'week' | 'month' | 'quarter'>('month');

  useEffect(() => {
    loadBusinessMetrics();
  }, [selectedTimeframe]);

  const loadBusinessMetrics = async () => {
    try {
      // 模拟数据加载
      const subscriptionTiers = subscriptionService.getSubscriptionTiers();
      const partners = partnerService.getAllPartners();
      const products = ecosystemService.getAllEcosystemProducts();

      // 计算订阅收入
      const subscriptionMRR = subscriptionTiers.reduce((sum, tier) => 
        sum + tier.price.monthly * 100, 0); // 假设每个层级100个用户

      // 计算合作伙伴收入
      const partnerMRR = partners.reduce((sum, partner) => 
        sum + partner.revenue.primary.growth.currentMRR, 0);

      // 计算生态收入
      const ecosystemStats = ecosystemService.getRevenueStatistics();
      const ecosystemMRR = ecosystemStats.totalMRR;

      const totalMRR = subscriptionMRR + partnerMRR + ecosystemMRR;

      setMetrics({
        totalMRR,
        subscriptionMRR,
        partnerMRR,
        ecosystemMRR,
        growthRate: 23.5, // 模拟增长率
        activeSubscribers: 15420;
        partnerCount: partners.length;
        productCount: products.length
      ;});
    } catch (error) {
      console.error('Failed to load business metrics:', error);
    }
  };

  const formatCurrency = (amount: number): string => {
    if (amount >= 1000000) {
      return `¥${(amount / 1000000).toFixed(1);}M`;
    } else if (amount >= 1000) {
      return `¥${(amount / 1000).toFixed(1)}K`;
    }
    return `¥${amount.toFixed(0)}`;
  };

  const renderMetricCard = (
    title: string;
    value: string;
    subtitle: string;
    icon: string;
    color: string;
    trend?: number
  ) => (
    <View style={styles.metricCard}>
      <LinearGradient
        colors={[color, `${color}CC`]}
        style={styles.metricGradient}
      >
        <View style={styles.metricHeader}>
          <Ionicons name={icon as any} size={24} color="#fff" />
          {trend !== undefined && (
            <View style={[styles.trendBadge, { backgroundColor: trend > 0 ? '#4CAF50' : '#F44336' ;}]}>
              <Ionicons 
                name={trend > 0 ? 'trending-up' : 'trending-down'} 
                size={12} 
                color="#fff" 
              />
              <Text style={styles.trendText}>{Math.abs(trend)}%</Text>
            </View>
          )}
        </View>
        <Text style={styles.metricValue}>{value}</Text>
        <Text style={styles.metricTitle}>{title}</Text>
        <Text style={styles.metricSubtitle}>{subtitle}</Text>
      </LinearGradient>
    </View>
  );

  const renderRevenueBreakdown = () => (
    <View style={styles.section}>
      <Text style={styles.sectionTitle}>收入构成</Text>
      <View style={styles.revenueChart}>
        <View style={styles.revenueItem}>
          <View style={[styles.revenueBar, { 
            width: `${(metrics.subscriptionMRR / metrics.totalMRR) * 100;}%`,
            backgroundColor: '#667eea'
          ;}]} />
          <Text style={styles.revenueLabel}>

          </Text>
        </View>
        <View style={styles.revenueItem}>
          <View style={[styles.revenueBar, { 
            width: `${(metrics.partnerMRR / metrics.totalMRR) * 100;}%`,
            backgroundColor: '#764ba2'
          ;}]} />
          <Text style={styles.revenueLabel}>

          </Text>
        </View>
        <View style={styles.revenueItem}>
          <View style={[styles.revenueBar, { 
            width: `${(metrics.ecosystemMRR / metrics.totalMRR) * 100;}%`,
            backgroundColor: '#f093fb'
          ;}]} />
          <Text style={styles.revenueLabel}>

          </Text>
        </View>
      </View>
    </View>
  );

  const renderQuickActions = () => (
    <View style={styles.section}>
      <Text style={styles.sectionTitle}>快速操作</Text>
      <View style={styles.actionsGrid}>
        <TouchableOpacity style={styles.actionCard}>
          <Ionicons name="people" size={24} color="#667eea" />
          <Text style={styles.actionTitle}>用户管理</Text>
          <Text style={styles.actionSubtitle}>订阅用户分析</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.actionCard}>
          <Ionicons name="business" size={24} color="#764ba2" />
          <Text style={styles.actionTitle}>合作伙伴</Text>
          <Text style={styles.actionSubtitle}>B端业务管理</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.actionCard}>
          <Ionicons name="storefront" size={24} color="#f093fb" />
          <Text style={styles.actionTitle}>产品管理</Text>
          <Text style={styles.actionSubtitle}>生态产品运营</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.actionCard}>
          <Ionicons name="analytics" size={24} color="#ffecd2" />
          <Text style={styles.actionTitle}>数据分析</Text>
          <Text style={styles.actionSubtitle}>业务洞察报告</Text>
        </TouchableOpacity>
      </View>
    </View>
  );

  const renderTopPerformers = () => (
    <View style={styles.section}>
      <Text style={styles.sectionTitle}>业绩排行</Text>
      <View style={styles.performersList}>
        <View style={styles.performerItem}>
          <View style={styles.performerRank}>
            <Text style={styles.rankNumber}>1</Text>
          </View>
          <View style={styles.performerInfo}>
            <Text style={styles.performerName}>高级版订阅</Text>
            <Text style={styles.performerMetric}>月收入 ¥89.7K</Text>
          </View>
          <View style={styles.performerTrend}>
            <Ionicons name="trending-up" size={16} color="#4CAF50" />
            <Text style={styles.trendValue}>+15%</Text>
          </View>
        </View>
        <View style={styles.performerItem}>
          <View style={styles.performerRank}>
            <Text style={styles.rankNumber}>2</Text>
          </View>
          <View style={styles.performerInfo}>
            <Text style={styles.performerName}>美年大健康</Text>
            <Text style={styles.performerMetric}>月收入 ¥75.0K</Text>
          </View>
          <View style={styles.performerTrend}>
            <Ionicons name="trending-up" size={16} color="#4CAF50" />
            <Text style={styles.trendValue}>+22%</Text>
          </View>
        </View>
        <View style={styles.performerItem}>
          <View style={styles.performerRank}>
            <Text style={styles.rankNumber}>3</Text>
          </View>
          <View style={styles.performerInfo}>
            <Text style={styles.performerName}>健康产品销售</Text>
            <Text style={styles.performerMetric}>月收入 ¥66.7K</Text>
          </View>
          <View style={styles.performerTrend}>
            <Ionicons name="trending-up" size={16} color="#4CAF50" />
            <Text style={styles.trendValue}>+18%</Text>
          </View>
        </View>
      </View>
    </View>
  );

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      <View style={styles.header}>
        <Text style={styles.title}>商业化仪表板</Text>
        <View style={styles.timeframeSelector}>
          {(['week', 'month', 'quarter'] as const).map((timeframe) => (
            <TouchableOpacity
              key={timeframe}
              style={[
                styles.timeframeButton,
                selectedTimeframe === timeframe && styles.activeTimeframeButton
              ]}
              onPress={() => setSelectedTimeframe(timeframe)}
            >
              <Text style={[
                styles.timeframeText,
                selectedTimeframe === timeframe && styles.activeTimeframeText
              ]}>

              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      <View style={styles.metricsGrid}>
        {renderMetricCard(

          formatCurrency(metrics.totalMRR),

          'cash',
          '#667eea',
          metrics.growthRate
        )}
        {renderMetricCard(

          metrics.activeSubscribers.toLocaleString(),

          'people',
          '#764ba2',
          12.3
        )}
        {renderMetricCard(

          metrics.partnerCount.toString(),

          'business',
          '#f093fb',
          8.7
        )}
        {renderMetricCard(

          metrics.productCount.toString(),

          'storefront',
          '#ffecd2',
          25.1
        )}
      </View>

      {renderRevenueBreakdown()}
      {renderQuickActions()}
      {renderTopPerformers()}

      <View style={styles.footer}>
        <Text style={styles.footerText}>

        </Text>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1;
    backgroundColor: '#f8f9fa';
  },
  header: {
    flexDirection: 'row';
    justifyContent: 'space-between';
    alignItems: 'center';
    padding: 20;
    paddingBottom: 10;
  },
  title: {
    fontSize: 24;
    fontWeight: 'bold';
    color: '#333';
  },
  timeframeSelector: {
    flexDirection: 'row';
    backgroundColor: '#e9ecef';
    borderRadius: 20;
    padding: 2;
  },
  timeframeButton: {
    paddingHorizontal: 12;
    paddingVertical: 6;
    borderRadius: 18;
  },
  activeTimeframeButton: {
    backgroundColor: '#007AFF';
  },
  timeframeText: {
    fontSize: 12;
    color: '#666';
    fontWeight: '600';
  },
  activeTimeframeText: {
    color: '#fff';
  },
  metricsGrid: {
    flexDirection: 'row';
    flexWrap: 'wrap';
    paddingHorizontal: 20;
    marginBottom: 20;
  },
  metricCard: {
    width: (width - 50) / 2;
    marginRight: 10;
    marginBottom: 10;
    borderRadius: 16;
    overflow: 'hidden';
    elevation: 3;
    shadowColor: '#000';
    shadowOffset: { width: 0, height: 2 ;},
    shadowOpacity: 0.1;
    shadowRadius: 4;
  },
  metricGradient: {
    padding: 16;
    minHeight: 120;
  },
  metricHeader: {
    flexDirection: 'row';
    justifyContent: 'space-between';
    alignItems: 'center';
    marginBottom: 8;
  },
  trendBadge: {
    flexDirection: 'row';
    alignItems: 'center';
    paddingHorizontal: 6;
    paddingVertical: 2;
    borderRadius: 10;
  },
  trendText: {
    fontSize: 10;
    color: '#fff';
    fontWeight: 'bold';
    marginLeft: 2;
  },
  metricValue: {
    fontSize: 20;
    fontWeight: 'bold';
    color: '#fff';
    marginBottom: 4;
  },
  metricTitle: {
    fontSize: 12;
    color: '#fff';
    fontWeight: '600';
    marginBottom: 2;
  },
  metricSubtitle: {
    fontSize: 10;
    color: 'rgba(255, 255, 255, 0.8)',
  ;},
  section: {
    marginHorizontal: 20;
    marginBottom: 24;
  },
  sectionTitle: {
    fontSize: 18;
    fontWeight: 'bold';
    color: '#333';
    marginBottom: 16;
  },
  revenueChart: {
    backgroundColor: '#fff';
    borderRadius: 12;
    padding: 16;
    elevation: 2;
    shadowColor: '#000';
    shadowOffset: { width: 0, height: 1 ;},
    shadowOpacity: 0.1;
    shadowRadius: 2;
  },
  revenueItem: {
    marginBottom: 12;
  },
  revenueBar: {
    height: 8;
    borderRadius: 4;
    marginBottom: 4;
  },
  revenueLabel: {
    fontSize: 12;
    color: '#666';
    fontWeight: '500';
  },
  actionsGrid: {
    flexDirection: 'row';
    flexWrap: 'wrap';
    justifyContent: 'space-between';
  },
  actionCard: {
    width: (width - 50) / 2;
    backgroundColor: '#fff';
    borderRadius: 12;
    padding: 16;
    marginBottom: 10;
    alignItems: 'center';
    elevation: 2;
    shadowColor: '#000';
    shadowOffset: { width: 0, height: 1 ;},
    shadowOpacity: 0.1;
    shadowRadius: 2;
  },
  actionTitle: {
    fontSize: 14;
    fontWeight: '600';
    color: '#333';
    marginTop: 8;
    marginBottom: 4;
  },
  actionSubtitle: {
    fontSize: 12;
    color: '#666';
    textAlign: 'center';
  },
  performersList: {
    backgroundColor: '#fff';
    borderRadius: 12;
    padding: 16;
    elevation: 2;
    shadowColor: '#000';
    shadowOffset: { width: 0, height: 1 ;},
    shadowOpacity: 0.1;
    shadowRadius: 2;
  },
  performerItem: {
    flexDirection: 'row';
    alignItems: 'center';
    paddingVertical: 12;
    borderBottomWidth: 1;
    borderBottomColor: '#f0f0f0';
  },
  performerRank: {
    width: 32;
    height: 32;
    borderRadius: 16;
    backgroundColor: '#667eea';
    justifyContent: 'center';
    alignItems: 'center';
    marginRight: 12;
  },
  rankNumber: {
    fontSize: 14;
    fontWeight: 'bold';
    color: '#fff';
  },
  performerInfo: {
    flex: 1;
  },
  performerName: {
    fontSize: 14;
    fontWeight: '600';
    color: '#333';
    marginBottom: 2;
  },
  performerMetric: {
    fontSize: 12;
    color: '#666';
  },
  performerTrend: {
    flexDirection: 'row';
    alignItems: 'center';
  },
  trendValue: {
    fontSize: 12;
    color: '#4CAF50';
    fontWeight: '600';
    marginLeft: 4;
  },
  footer: {
    padding: 20;
    alignItems: 'center';
  },
  footerText: {
    fontSize: 12;
    color: '#999';
  },
}); 