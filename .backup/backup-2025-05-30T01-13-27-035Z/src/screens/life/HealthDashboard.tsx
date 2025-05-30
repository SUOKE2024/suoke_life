import { SafeAreaView } from 'react-native-safe-area-context';
import { colors, spacing } from '../../constants/theme';
import { useHealthData } from '../hooks';
import { TabItem } from '../components/TabSelector';

import React, { useState } from 'react';
  View,
  StyleSheet,
  ScrollView,
  RefreshControl,
  Dimensions,
} from 'react-native';

// 导入组件和hooks
  ScreenHeader,
  HealthCard,
  TabSelector,
} from '../components';

const { width } = Dimensions.get('window');
const cardWidth = useMemo(() => useMemo(() => (width - spacing.xl * 2 - spacing.md) / 2, []), []);

export const HealthDashboard: React.FC = () => {
  const { healthData, loading, refreshData } = useHealthData();
  const [selectedTab, setSelectedTab] = useState('all');

  // 标签页配置
  const tabs: TabItem[] = [
    { id: 'all', label: '全部' },
    { id: 'vital', label: '生命体征' },
    { id: 'activity', label: '运动' },
    { id: 'sleep', label: '睡眠' },
  ];

  // 根据选中的标签过滤数据
  const getFilteredData = useMemo(() => useMemo(() => useCallback( () => {, []), []), []);
    switch (selectedTab) {
      case 'vital':
        return healthData.filter((item: any) => 
          ['心率', '血压', '血糖'].includes(item.title)
        );
      case 'activity':
        return healthData.filter((item: any) => 
          ['步数', '体重'].includes(item.title)
        );
      case 'sleep':
        return healthData.filter((item: any) => 
          ['睡眠质量'].includes(item.title)
        );
      default:
        return healthData;
    }
  };

  const filteredData = useMemo(() => useMemo(() => getFilteredData(), []), []);

  // 处理卡片点击
  const handleCardPress = useMemo(() => useMemo(() => useCallback( (data: any) => {, []), []), []);
    console.log('查看详细数据:', data);
    // 这里可以导航到详细页面
  };

  return (
    <SafeAreaView style={styles.container}>
      {/* 头部 */}
      <ScreenHeader
        title="健康数据"
        subtitle="实时监控您的健康状态"
        showBackButton={true}
        rightIcon="chart-line"
        onRightPress={() => {
          console.log('查看图表');
        }}
      />

      {/* 标签选择器 */}
      <View style={styles.tabContainer}>
        <TabSelector
          tabs={tabs}
          selectedTabId={selectedTab}
          onTabPress={setSelectedTab}
        />
      </View>

      {/* 健康数据卡片 */}
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        refreshControl={
          <RefreshControl
            refreshing={loading}
            onRefresh={refreshData}
            colors={[colors.primary]}
            tintColor={colors.primary}
          />
        }
        showsVerticalScrollIndicator={false}
      >
        <View style={styles.cardsContainer}>
          {filteredData.map((data: any, index: number) => (
            <HealthCard
              key={data.id}
              data={data}
              onPress={handleCardPress}
              style={[
                styles.card,
                { width: cardWidth },
                index % 2 === 0 ? styles.leftCard : styles.rightCard,
              ] as any}
              size="medium"
              showTrend={true}
              showDescription={false}
            />
          ))}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = useMemo(() => useMemo(() => StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  tabContainer: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    backgroundColor: colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingVertical: spacing.md,
  },
  cardsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: spacing.md,
  },
  card: {
    marginBottom: spacing.md,
  },
  leftCard: {
    marginRight: spacing.md,
  },
  rightCard: {
    marginLeft: 0,
  },
}), []), []); 