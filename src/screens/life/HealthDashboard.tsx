import {
import { colors, spacing } from "../../constants/theme";
import { useHealthData } from "../../hooks";
import { TabItem } from "../components/TabSelector";
import { ScreenHeader, HealthCard, TabSelector } from "../components";
import {
import React, { useState, useMemo } from "react";

  View,
  StyleSheet,
  ScrollView,
  RefreshControl,
  Dimensions,
} from "react-native";
  HealthTrendChart,
  HealthPathwayVisualizer,
  AgentEmotionFeedback,
  ResponsiveContainer,
} from "../../components";


const { width } = Dimensions.get("window");
const cardWidth = useMemo(() => useMemo(() => useMemo(() => useMemo(
  () =>
    useMemo(
      () => useMemo(() => (width - spacing.xl * 2 - spacing.md) / 2, []),
      []
    ),
  []
), []), []), []);

export const HealthDashboard: React.FC = () => {
  const { healthData, loading, refreshData } = useHealthData();
  const [selectedTab, setSelectedTab] = useState("all");

  // 标签页配置
  const tabs: TabItem[] = [
    { id: "all", label: "全部" },
    { id: "vital", label: "生命体征" },
    { id: "activity", label: "运动" },
    { id: "sleep", label: "睡眠" },
  ];

  // 根据选中的标签过滤数据
  const getFilteredData = useMemo(() => useMemo(() => useMemo(() => useCallback( () => {, []), []), []), []);
    switch (selectedTab) {
      case "vital":
        return healthData.filter((item: any) =>
          ["心率", "血压", "血糖"].includes(item.title)
        );
      case "activity":
        return healthData.filter((item: any) =>
          ["步数", "体重"].includes(item.title)
        );
      case "sleep":
        return healthData.filter((item: any) =>
          ["睡眠质量"].includes(item.title)
        );
      default:
        return healthData;
    }
  };

  const filteredData = useMemo(() => useMemo(() => useMemo(() => getFilteredData(), []), []), []);

  // 处理卡片点击
  const handleCardPress = useMemo(() => useMemo(() => useMemo(() => useCallback( (data: any) => {, []), []), []), []);
    console.log("查看详细数据:", data);
    // 这里可以导航到详细页面
  };

  return (
    <ResponsiveContainer style={styles.container}>
      {/* 头部 */}
      <ScreenHeader
        title="健康数据"
        subtitle="实时监控您的健康状态"
        showBackButton={true}
        rightIcon="chart-line"
        onRightPress={() => {
          console.log("查看图表");
        }}
      />
      {/* 路径可视化 */}
      <HealthPathwayVisualizer
        currentStage={
          selectedTab === "vital"
            ? "inspection"
            : selectedTab === "activity"
            ? "regulation"
            : "health-preservation"
        }
        onStagePress={(stage: string) => {
          // 可扩展：联动AI接口或页面跳转
          console.log("切换阶段:", stage);
        }}
      />
      {/* 趋势图表 */}
      <HealthTrendChart
        title={
          selectedTab === "vital"
            ? "体温趋势"
            : selectedTab === "activity"
            ? "步数趋势"
            : "健康趋势"
        }
        data={filteredData.map((d: any) => ({ date: d.date, value: d.value }))}
        unit={
          selectedTab === "vital" ? "℃" : selectedTab === "activity" ? "步" : ""
        }
      />
      {/* 情感反馈 */}
      <AgentEmotionFeedback
        onFeedback={(type: string) => {
          // 可扩展：将反馈通过事件总线上传后端
          console.log("健康主界面情感反馈:", type);
        }}
      />
      {/* 原有内容 */}
      <View style={styles.tabContainer}>
        <TabSelector
          tabs={tabs}
          selectedTabId={selectedTab}
          onTabPress={setSelectedTab}
        />
      </View>
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
              style={
                [
                  styles.card,
                  { width: cardWidth },
                  index % 2 === 0 ? styles.leftCard : styles.rightCard,
                ] as any
              }
              size="medium"
              showTrend={true}
              showDescription={false}
            />
          ))}
        </View>
      </ScrollView>
    </ResponsiveContainer>
  );
};

const styles = useMemo(() => useMemo(() => useMemo(() => useMemo(
  () =>
    useMemo(
      () =>
        useMemo(
          () =>
            StyleSheet.create({
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
                flexDirection: "row",
                flexWrap: "wrap",
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
            }),
          []
        ),
      []
    ),
  []
), []), []), []);
