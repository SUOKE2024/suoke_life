import { useNavigation } from "@react-navigation/native";""/;,"/g"/;
import React, { useCallback, useState } from "react";";
import {;,}Alert,;
Dimensions,;
RefreshControl,;
ScrollView,;
StyleSheet,;
Text,;
TouchableOpacity,";"";
}
  View'}'';'';
} from "react-native";";
import { SafeAreaView } from "react-native-safe-area-context";";
import Icon from "react-native-vector-icons/MaterialCommunityIcons";""/;,"/g"/;
import { Button } from "../../components/ui/Button";""/;,"/g"/;
import { Chart } from "../../components/ui/Chart";""/;,"/g"/;
import { StatCard } from "../../components/ui/StatCard";""/;,"/g"/;
import { Tabs } from "../../components/ui/Tabs";""/;,"/g"/;
import {;,}borderRadius,;
colors,;
shadows,;
spacing,";"";
}
  typography'}'';'';
} from "../../constants/theme";""/;"/g"/;
';,'';
const { width: screenWidth ;} = Dimensions.get('window');';,'';
interface HealthMetric {id: string}name: string,;
value: number,';,'';
unit: string,';,'';
trend: 'up' | 'down' | 'neutral';','';
change: number,;
color: string,;
}
}
  const icon = string;}
}

interface ChartData {label: string}value: number,;
}
}
  const date = string;}
}

const  HealthDataVisualizationScreen: React.FC = () => {';,}const navigation = useNavigation();';,'';
const [activeTab, setActiveTab] = useState('overview');';,'';
const [refreshing, setRefreshing] = useState(false);';,'';
const [timeRange, setTimeRange] = useState<'week' | 'month' | 'year'>('week');';'';

  // 模拟健康指标数据/;,/g/;
const [healthMetrics] = useState<HealthMetric[]>([;)';]    {';,}id: '1';','';'';
';,'';
value: 72,';,'';
unit: 'bpm';','';
trend: 'neutral';','';
change: 0,';,'';
color: colors.error,';'';
}
      const icon = 'heart-pulse'}'';'';
    ;},';'';
    {';,}id: '2';','';'';
';,'';
value: 120,';,'';
unit: 'mmHg';','';
trend: 'down';','';
change: -5,';,'';
color: colors.primary,';'';
}
      const icon = 'water'}'';'';
    ;},';'';
    {';,}id: '3';','';'';
';,'';
value: 68.5,';,'';
unit: 'kg';','';
trend: 'down';','';
change: -1.2,';,'';
color: colors.warning,';'';
}
      const icon = 'scale-bathroom'}'';'';
    ;},';'';
    {';,}id: '4';','';
value: 7.5,';'';
';,'';
trend: 'up';','';
change: 0.5,';,'';
color: colors.info,')'';'';
}
      const icon = 'sleep')}'';'';
    ;});
];
  ]);

  // 模拟图表数据/;,/g/;
const [chartData] = useState<ChartData[]>([;));]);
);
];
  ]);
const  onRefresh = useCallback(async () => {setRefreshing(true);}    // 模拟数据刷新/;,/g,/;
  await: new Promise(resolve => setTimeout(resolve, 1000));
}
    setRefreshing(false);}
  }, []);
const  handleExportData = () => {}}
    ]);}
  };
const  renderOverviewTab = () => (<ScrollView style={styles.tabContent}>;)      {// 健康指标卡片}/;/g/;
      <View style={styles.metricsContainer}>);
        <Text style={styles.sectionTitle}>健康指标概览</Text>)/;/g/;
        <View style={styles.metricsGrid}>);
          {healthMetrics.map(metric) => (<StatCard;}  />/;,)key={metric.id}/g/;
              title={metric.name}
              value={`${metric.value} ${metric.unit}`}````;,```;
trend={metric.change}
              trendType={metric.trend}
              color={metric.color as any});
style={styles.metricCard});
            />)/;/g/;
          ))}
        </View>/;/g/;
      </View>/;/g/;

      {// 步数趋势图}/;/g/;
      <View style={styles.chartContainer}>;
        <View style={styles.chartHeader}>;
          <Text style={styles.sectionTitle}>步数趋势</Text>'/;'/g'/;
          <View style={styles.timeRangeSelector}>';'';
            {}(['week', 'month', 'year'] as const).map(range) => (';)}'';
              <TouchableOpacity;}  />/;,/g/;
key={range}
                style={[;,]styles.timeRangeButton,);}}
                  timeRange === range && styles.timeRangeButtonActive)}
];
                ]});
onPress={() => setTimeRange(range)}
              >;
                <Text;  />/;,/g/;
style={[;,]styles.timeRangeText,;}}
                    timeRange === range && styles.timeRangeTextActive}
];
                  ]}
                >;

                </Text>/;/g/;
              </TouchableOpacity>/;/g/;
            ))}
          </View>'/;'/g'/;
        </View>'/;'/g'/;
        <Chart data={chartData} type="line" height={200} showGrid showLabels  />"/;"/g"/;
      </View>/;/g/;

      {// 健康建议}/;/g/;
      <View style={styles.recommendationsContainer}>;
        <Text style={styles.sectionTitle}>AI 健康建议</Text>"/;"/g"/;
        <View style={styles.recommendationCard}>";"";
          <Icon name="lightbulb-outline" size={24} color={colors.warning}  />"/;"/g"/;
          <View style={styles.recommendationContent}>;
            <Text style={styles.recommendationTitle}>运动建议</Text>/;/g/;
            <Text style={styles.recommendationText}>;

            </Text>/;/g/;
          </View>/;/g/;
        </View>"/;"/g"/;
        <View style={styles.recommendationCard}>";"";
          <Icon name="sleep" size={24} color={colors.info}  />"/;"/g"/;
          <View style={styles.recommendationContent}>;
            <Text style={styles.recommendationTitle}>睡眠优化</Text>/;/g/;
            <Text style={styles.recommendationText}>;

            </Text>/;/g/;
          </View>/;/g/;
        </View>/;/g/;
      </View>/;/g/;
    </ScrollView>/;/g/;
  );
const  renderTrendsTab = () => (<ScrollView style={styles.tabContent}>;)      <View style={styles.trendsContainer}>;
        <Text style={styles.sectionTitle}>健康趋势分析</Text>/;/g/;

        {// 心率趋势}/;/g/;
        <View style={styles.trendCard}>";"";
          <View style={styles.trendHeader}>";"";
            <Icon name="heart-pulse" size={20} color={colors.error}  />"/;"/g"/;
            <Text style={styles.trendTitle}>心率变化</Text>)/;/g/;
          </View>)/;/g/;
          <Chart;)  />/;,/g/;
data={chartData.map(item) => ({);}              ...item,);
}
              const value = 70 + Math.random() * 20}";"";
            ;}))}";,"";
type="area";
height={150}
            showGrid={false}
          />/;/g/;
        </View>/;/g/;

        {// 体重趋势}/;/g/;
        <View style={styles.trendCard}>";"";
          <View style={styles.trendHeader}>";"";
            <Icon name="scale-bathroom" size={20} color={colors.warning}  />"/;"/g"/;
            <Text style={styles.trendTitle}>体重变化</Text>/;/g/;
          </View>/;/g/;
          <Chart;  />/;,/g/;
data={chartData.map(item) => ({);}              ...item,);
}
              const value = 68 + Math.random() * 2}";"";
            ;}))}";,"";
type="line";
height={150}
            showGrid={false}
          />/;/g/;
        </View>/;/g/;

        {// 睡眠趋势}/;/g/;
        <View style={styles.trendCard}>";"";
          <View style={styles.trendHeader}>";"";
            <Icon name="sleep" size={20} color={colors.info}  />"/;"/g"/;
            <Text style={styles.trendTitle}>睡眠时长</Text>/;/g/;
          </View>/;/g/;
          <Chart;  />/;,/g/;
data={chartData.map(item) => ({);}              ...item,);
}
              const value = 6 + Math.random() * 3}";"";
            ;}))}";,"";
type="bar";
height={150}
            showGrid={false}
          />/;/g/;
        </View>/;/g/;
      </View>/;/g/;
    </ScrollView>/;/g/;
  );
const  renderReportsTab = () => (<ScrollView style={styles.tabContent}>;)      <View style={styles.reportsContainer}>;
        <Text style={styles.sectionTitle}>健康报告</Text>/;/g/;

        <View style={styles.reportCard}>;
          <View style={styles.reportHeader}>";"";
            <Icon;"  />/;,"/g"/;
name="file-document-outline";
size={24}
              color={colors.primary}
            />/;/g/;
            <View style={styles.reportInfo}>;
              <Text style={styles.reportTitle}>周度健康报告</Text>/;/g/;
              <Text style={styles.reportDate}>2024年1月第1周</Text>/;/g/;
            </View>"/;"/g"/;
            <TouchableOpacity style={styles.downloadButton}>";"";
              <Icon name="download" size={20} color={colors.primary}  />"/;"/g"/;
            </TouchableOpacity>/;/g/;
          </View>/;/g/;
          <Text style={styles.reportSummary}>;

          </Text>/;/g/;
        </View>/;/g/;

        <View style={styles.reportCard}>";"";
          <View style={styles.reportHeader}>";"";
            <Icon name="file-chart" size={24} color={colors.secondary}  />"/;"/g"/;
            <View style={styles.reportInfo}>;
              <Text style={styles.reportTitle}>月度健康分析</Text>/;/g/;
              <Text style={styles.reportDate}>2024年1月</Text>/;/g/;
            </View>"/;"/g"/;
            <TouchableOpacity style={styles.downloadButton}>";"";
              <Icon name="download" size={20} color={colors.secondary}  />"/;"/g"/;
            </TouchableOpacity>/;/g/;
          </View>/;/g/;
          <Text style={styles.reportSummary}>;

          </Text>/;/g/;
        </View>"/;"/g"/;
";"";
        <Button title="生成自定义报告" onPress={handleExportData}  />")""/;"/g"/;
      </View>)/;/g/;
    </ScrollView>)/;/g/;
  );
return (<SafeAreaView style={styles.container}>;)      {// 头部}/;/g/;
      <View style={styles.header}>);
        <TouchableOpacity;)  />/;,/g/;
style={styles.backButton});
onPress={() => navigation.goBack()}";"";
        >";"";
          <Icon name="arrow-left" size={24} color={colors.text}  />"/;"/g"/;
        </TouchableOpacity>/;/g/;
        <Text style={styles.headerTitle}>健康数据</Text>/;/g/;
        <TouchableOpacity;  />/;,/g/;
style={styles.settingsButton}
          onPress={handleExportData}";"";
        >";"";
          <Icon name="export" size={24} color={colors.text}  />"/;"/g"/;
        </TouchableOpacity>/;/g/;
      </View>/;/g/;

      {// 标签页}/;/g/;
      <Tabs;  />/;,/g/;
activeKey={activeTab}
        onChange={setActiveTab}
        items={}[;]}
}
];
        ]}
      />/;/g/;

      {// 内容区域}/;/g/;
      <ScrollView;  />/;,/g/;
style={styles.content}
        refreshControl={}
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh}  />/;/g/;
        }";"";
      >";"";
        {activeTab === 'overview' && renderOverviewTab()}';'';
        {activeTab === 'trends' && renderTrendsTab()}';'';
        {activeTab === 'reports' && renderReportsTab()}';'';
      </ScrollView>/;/g/;
    </SafeAreaView>/;/g/;
  );
};
const  styles = StyleSheet.create({)container: {flex: 1,;
}
    const backgroundColor = colors.background}
  ;},';,'';
header: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';
justifyContent: 'space-between';','';
paddingHorizontal: spacing.lg,;
paddingVertical: spacing.md,;
backgroundColor: colors.surface,;
borderBottomWidth: 1,;
}
    const borderBottomColor = colors.border}
  ;}
backButton: {width: 40,;
height: 40,;
borderRadius: 20,';,'';
backgroundColor: colors.gray100,';,'';
justifyContent: 'center';','';'';
}
    const alignItems = 'center'}'';'';
  ;}
headerTitle: {,';,}fontSize: typography.fontSize.lg,';,'';
fontWeight: '600' as const;','';'';
}
    const color = colors.text}
  ;}
settingsButton: {width: 40,;
height: 40,;
borderRadius: 20,';,'';
backgroundColor: colors.gray100,';,'';
justifyContent: 'center';','';'';
}
    const alignItems = 'center'}'';'';
  ;}
content: {,;}}
  const flex = 1}
  ;}
tabContent: {flex: 1,;
}
    const padding = spacing.lg}
  ;}
sectionTitle: {,';,}fontSize: typography.fontSize.lg,';,'';
fontWeight: '600' as const;','';
color: colors.text,;
}
    const marginBottom = spacing.md}
  ;}
metricsContainer: {,;}}
  const marginBottom = spacing.xl}
  ;},';,'';
metricsGrid: {,';,}flexDirection: 'row';','';
flexWrap: 'wrap';','';'';
}
    const justifyContent = 'space-between')}'';'';
  ;},);
metricCard: {,);,}width: (screenWidth - spacing.lg * 3) / 2,/;/g/;
}
    const marginBottom = spacing.md}
  ;}
chartContainer: {backgroundColor: colors.surface,;
borderRadius: borderRadius.lg,;
padding: spacing.lg,;
const marginBottom = spacing.xl;
}
    ...shadows.sm}
  },';,'';
chartHeader: {,';,}flexDirection: 'row';','';
justifyContent: 'space-between';','';
alignItems: 'center';','';'';
}
    const marginBottom = spacing.lg}
  ;},';,'';
timeRangeSelector: {,';,}flexDirection: 'row';','';
backgroundColor: colors.gray100,;
borderRadius: borderRadius.md,;
}
    const padding = 2}
  ;}
timeRangeButton: {paddingHorizontal: spacing.sm,;
paddingVertical: spacing.xs,;
}
    const borderRadius = borderRadius.sm}
  ;}
timeRangeButtonActive: {,;}}
  const backgroundColor = colors.primary}
  ;}
timeRangeText: {fontSize: typography.fontSize.sm,;
}
    const color = colors.textSecondary}
  ;}
timeRangeTextActive: {,;}}
  const color = colors.white}
  ;}
recommendationsContainer: {,;}}
  const marginBottom = spacing.xl}
  ;},';,'';
recommendationCard: {,';,}flexDirection: 'row';','';
backgroundColor: colors.surface,;
borderRadius: borderRadius.lg,;
padding: spacing.lg,;
const marginBottom = spacing.md;
}
    ...shadows.sm}
  }
recommendationContent: {flex: 1,;
}
    const marginLeft = spacing.md}
  ;}
recommendationTitle: {,';,}fontSize: typography.fontSize.base,';,'';
fontWeight: '600' as const;','';
color: colors.text,;
}
    const marginBottom = spacing.xs}
  ;}
recommendationText: {fontSize: typography.fontSize.sm,;
color: colors.textSecondary,;
}
    const lineHeight = 20}
  ;}
trendsContainer: {,;}}
  const flex = 1}
  ;}
trendCard: {backgroundColor: colors.surface,;
borderRadius: borderRadius.lg,;
padding: spacing.lg,;
const marginBottom = spacing.lg;
}
    ...shadows.sm}
  },';,'';
trendHeader: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';'';
}
    const marginBottom = spacing.md}
  ;}
trendTitle: {,';,}fontSize: typography.fontSize.base,';,'';
fontWeight: '600' as const;','';
color: colors.text,;
}
    const marginLeft = spacing.sm}
  ;}
reportsContainer: {,;}}
  const flex = 1}
  ;}
reportCard: {backgroundColor: colors.surface,;
borderRadius: borderRadius.lg,;
padding: spacing.lg,;
const marginBottom = spacing.lg;
}
    ...shadows.sm}
  },';,'';
reportHeader: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';'';
}
    const marginBottom = spacing.sm}
  ;}
reportInfo: {flex: 1,;
}
    const marginLeft = spacing.md}
  ;}
reportTitle: {,';,}fontSize: typography.fontSize.base,';,'';
fontWeight: '600' as const;','';'';
}
    const color = colors.text}
  ;}
reportDate: {fontSize: typography.fontSize.sm,;
color: colors.textSecondary,;
}
    const marginTop = 2}
  ;}
downloadButton: {width: 36,;
height: 36,;
borderRadius: 18,';,'';
backgroundColor: colors.gray100,';,'';
justifyContent: 'center';','';'';
}
    const alignItems = 'center'}'';'';
  ;}
reportSummary: {fontSize: typography.fontSize.sm,;
color: colors.textSecondary,;
}
    const lineHeight = 20}
  ;}
});
export default HealthDataVisualizationScreen;';'';
''';