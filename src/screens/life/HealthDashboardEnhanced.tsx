/      View,"
import React from "react"
const importIcon = from ../../components/common/Icon"/ // ;""
import React,{ useState, useEffect } from "react;";
Text,
StyleSheet,
ScrollView,
TouchableOpacity,"
Dimensions,","
Alert,
  { RefreshControl } from react-native","
selectDiagnosisResults,","
selectDiagnosisSessions,
  { fetchDiagnosisHistory } from "../../store/slices/diagnosisSlice/    const { width   } = Dimensions.get(";window;";);""/,"/g,"/;
  chartWidth: useMemo() => width - spacing.lg * 2, []);;
interface HealthMetric {"
}"";
}
  performanceMonitor: usePerformanceMonitor(HealthDashboardEnhanced", { ";)"}";
trackRender: true,trackMemory: true,warnThreshold: 50;);,
  id: string,
title: string,"
value: string,","
unit: string,","
trend: "up | "down" | stable,";
trendValue: string,
color: string,
icon: string,
const data = number[];
};
interface ConstitutionData {type: ConstitutionType}name: string,
percentage: number,
color: string,
}
}
  const description = string}
};
export const HealthDashboardEnhanced: React.FC  = () => {;,
  dispatch: useMemo() => useAppDispatch(), []););
diagnosisResults: useMemo() => useAppSelector(selectDiagnosisResults), []););","
diagnosisSessions: useMemo() => useAppSelector(selectDiagnosisSessions), []);","
const [selectedPeriod, setSelectedPeriod] = useState<"week | "month" | year">("week;);
const [refreshing, setRefreshing] = useState<boolean>(fals;e;);","
const [selectedMetric, setSelectedMetric] = useState<string>("overview";);","
const [healthMetrics] = useState<HealthMetric[]  / >([/;)* {]"id: heart_rate,/g"/;
","
value: "72,
unit: bpm,","
trend: "stable,",","
trendValue: "0%,
color: #FF6B6B,","
icon: "heart,",";
}
];
data: [68, 70, 72, 71, 73, 72, 74]}
    ;},
    {"id: "blood_pressure,"
","
value: "120/80,/          unit: "mmHg,"/,"/g,"/;
  trend: down",
trendValue: "-2%,",","
color: "#4ECDC4,";
icon: medical-bag,
}
      data: [125, 123, 122, 120, 121, 120, 118]}
    ;},
    {"id: "sleep_quality,",,"
value: 85,,"
trend: "up,
trendValue: +5%,";
}
      color: "#45B7D1,",icon: "sleep",data: [78, 80, 82, 85, 83, 85, 87];"};
    },{id: stress_level,";}")
trend: "down,",trendValue: "-8%",color: #96CEB4,");
}
      icon: "brain,",data: [45, 42, 38, 35, 37, 35, 33];")"};
    };];)","
const [constitutionData] = useState<ConstitutionData[]  / >([/;)* {]"type: "balanced,"/g"/;
","
percentage: 35,","
color: "#4ECDC4,","
    {"const type = qi_deficiency;
    {"type: "yin_deficiency,","
    {"const type = "yang_deficiency);
);
}
)}
  useEffect(); => {};
const effectStart = performance.now();
loadDiagnosisHistory();
];
  }, [])  TODO: 检查依赖项  * / TODO: 检查依赖项* * *  TODO: 检查依赖项 TODO: 检查依赖项, TODO: 检查依赖项 // const loadDiagnosisHistory = useMemo() => useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo(); => async() => {}
try {}
      await: dispatch(fetchDiagnosisHistory({  limit: ;1;0  ;  });), []);
    } catch (error) {}
      }
  };
const  onRefresh = useMemo() => async() => {});
setRefreshing(true), []);
const await = loadDiagnosisHistory;
setRefreshing(false);
  };
  //
    <View style={styles.overviewContainer}>/          {/healthMetrics.map(metric) => ();/g/;
}
        <TouchableOpacity;}  />"
key={metric.id}","
style={[styles.metricCard, { borderLeftColor: metric.color;}}]}","
onPress={() = accessibilityLabel="操作按钮" /> setSelectedMetric(metric.id)}/            >"/;"/g"/;
          <View style={styles.metricHeader}>/            <Icon name={metric.icon} size={24} color={metric.color}  />/            <View style={[styles.trendBadge, { backgroundColor: getTrendColor(metric.trend)   ;}}]}  />/                  <Icon;  />"
name={getTrendIcon(metric.trend)}","
size={12}","
color="white;
              />/              <Text style={styles.trendText}>{metric.trendValue}</Text>/            </View>/          </View>/          <Text style={styles.metricTitle}>{metric.title}</Text>/          <View style={styles.metricValueContainer}>/            <Text style={[styles.metricValue, { color: metric.color;}}]}  />/                  {metric.value}
            </Text>/            <Text style={styles.metricUnit}>{metric.unit}</Text>/          </View>/        </TouchableOpacity>/    ))}
    </View>/      ), []);
const  renderChart = useCallback => {}
    if (!selectedMetricData) {return nu;l;l}
    performanceMonitor.recordRender();
return (;);
      <View style={styles.chartContainer}>/        <Text style={styles.chartTitle}>{selectedMetricData.title}趋势</Text>/            <LineChart;  />
data={datasets;: ;[;]{}                data: selectedMetricData.data,
}
                color: () = /> selectedMetricData.color,/                    strokeWidth: 3;}
              }
];
            ];
          }
          width={chartWidth}
          height={220}
          chartConfig={backgroundColor: colors.surface}backgroundGradientFrom: colors.surface,
backgroundGradientTo: colors.surface,
}
            decimalPlaces: 0,}
            color: (opacity = 1) => `rgba(0, 0, 0, ${opacity * 0.6;});`,````,```;
labelColor: (opacity = 1) => `rgba(0, 0, 0, ${opacity * 0.6;})`,````,```;
style: { borderRadius: 16  ;},","
propsForDots: {,"r: "6,
}
              strokeWidth: 2,}";
const stroke = selectedMetricData.color}
          }
          bezier;
style={styles.chart}>/      </View>/        );
  };
  //
    <View style={styles.constitutionContainer}>/      <Text style={styles.sectionTitle}>中医体质分析</Text>/      <View style={styles.constitutionChart}>/            <PieChart;  />
data={constitutionData.map(item = /> ({/                name: item.name,))/population: item.percentage,,/g,/;
  color: item.color,
}
            legendFontColor: colors.text,}
            const legendFontSize = 12;}))}
          width={chartWidth}
          height={200}
          chartConfig={}
            color: (opacity = 1) => `rgba(0, 0, 0, ${opacity;});```"`;```;
          }}","
accessor="population
backgroundColor="transparent
paddingLeft="15";
absolute;
        />/      </View>/      <View style={styles.constitutionLegend}>/            {constitutionData.map(item); => ()}
          <View key={item.type} style={styles.constitutionItem}>/            <View style={[styles.constitutionDot, { backgroundColor: item.color;}}]}  />/            <View style={styles.constitutionInfo}>/              <Text style={styles.constitutionName}>{item.name}</Text>/              <Text style={styles.constitutionDescription}>{item.description}</Text>/            </View>/            <Text style={styles.constitutionPercentage}>{item.percentage}%</Text>/          </View>/    ))}
      </View>/    </View>/      ), []);"/;"/g"/;
  //"/;"/g"/;
    <View style={styles.historyContainer}>/      <View style={styles.historyHeader}>/        <Text style={styles.sectionTitle}>五诊记录</Text>/        <TouchableOpacity onPress={() = accessibilityLabel="五诊记录"  /> Alert.alert("查看全部, "跳转到完整的诊断历史页面")}>/          <Text style={styles.viewAllText}>查看全部</Text>/        </TouchableOpacity>/      </View>/          {diagnosisSessions.slice(0, 3).map(session) => (")"}
        <TouchableOpacity key={session.id} style={styles.historyItem} accessibilityLabel="五诊检查"  />/          <View style={styles.historyIcon}>/            <Icon name="stethoscope" size={20} color={colors.primary}  />/          </View>/          <View style={styles.historyContent}>/            <Text style={styles.historyTitle}>五诊检查</Text>/            <Text style={styles.historyDate}>/                  {new Date(session.startTime).toLocaleDateString()}"/;"/g"/;
            </Text>/          </View>/          <View style={[styles.historyStatus, { backgroundColor: session.status === completed" ? colors.success : colors.warning;}}]}  />/            <Text style={styles.historyStatusText}>/              {session.status === "completed ? "已完成" : 进行中"}
            </Text>/          </View>/        </TouchableOpacity>/    ))}
    </View>/      ), []);
const  getTrendColor = useCallback() => {"switch (trend) {"case "up: return colors.succe;s;s;
case "down": return colors.error;";
}
      const default = return colors.warni;n;g}
    }
  };
const  getTrendIcon = useCallback() => {"switch (trend) {"const case = up": return "trending-u;p;","
case "down": return trending-dow;n;";
}
      const default = return "minu;s;"};
    }
  };
  //"/;"/g"/;
    <View style={styles.periodSelector}>/          {/;}(["week", month",year] as const).map(period) => ()"/g"/;
}
        <TouchableOpacity;}  />
key={period}
          style={[]styles.periodButton,}
            selectedPeriod === period && styles.activePeriodButton;}";
];
          ]}","
onPress={() = accessibilityLabel="操作按钮" /> setSelectedPeriod(period)}/            >"/;"/g"/;
          <Text;  />"
style={[]styles.periodText,";}}
              selectedPeriod === period && styles.activePeriodText;"};
];
            ]} />/            {period === "week" ? 周" : period === "month ? "月" : 年"}
          </Text>/        </TouchableOpacity>/          ))}
    </View>/      ), [])"
return (;)";
    <SafeAreaView style={styles.container}>/      {///    }
      {///          {renderPeriodSelector()};
      <ScrollView;  />
style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        refreshControl={}
          <RefreshControl;}  />
refreshing={refreshing}
            onRefresh={onRefresh}
            colors={[colors.primary]}
            tintColor={colors.primary} />/            }
showsVerticalScrollIndicator={false}
      >
        {///            {renderOverviewCards()}"/;"/g"/;
        {///            {selectedMetric !== overview" && renderChart()}
        {///            {renderConstitutionAnalysis()}
        {///            {renderDiagnosisHistory()}
      </ScrollView>/    </SafeAreaView>/      ;);
};
styles: useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo() => StyleSheet.create({)container: {),}
  flex: 1,}
    backgroundColor: colors.background;},","
header: {,"flexDirection: "row,",","
justifyContent: "space-between,
alignItems: center,";
paddingHorizontal: spacing.lg,
paddingVertical: spacing.md,
}
    borderBottomWidth: 1,}
    borderBottomColor: colors.border}
title: {,"fontSize: 24,";
}
    fontWeight: "bold,","}";
color: colors.text}
subtitle: {fontSize: 14,
}
    color: colors.textSecondary,}
    marginTop: 2;},","
periodSelector: {,"flexDirection: "row,";
paddingHorizontal: spacing.lg,
}
    paddingVertical: spacing.md,}
    backgroundColor: colors.surface}
periodButton: {flex: 1,","
paddingVertical: spacing.sm,","
alignItems: center,";
}
    borderRadius: 8,}
    marginHorizontal: spacing.xs}
activePeriodButton: { backgroundColor: colors.primary  }
periodText: {fontSize: 14,";
}
    color: colors.textSecondary,"}
fontWeight: "500;},",","
activePeriodText: { color: "white"  ;},
scrollView: { flex: 1 }
scrollContent: { paddingVertical: spacing.md  ;},","
overviewContainer: {,"flexDirection: row,","
flexWrap: "wrap,",";
}
    paddingHorizontal: spacing.lg,}
    marginBottom: spacing.lg}
metricCard: {width: (width - spacing.lg * 3) / 2,/        backgroundColor: colors.surface,/,/g,/;
  borderRadius: 12,
padding: spacing.md,
marginBottom: spacing.md,
marginRight: spacing.md,"
borderLeftWidth: 4,","
elevation: 2,";
}
    shadowColor: "#000,}";
shadowOffset: { width: 0, height: 2}
shadowOpacity: 0.1,"
shadowRadius: 4;},","
metricHeader: {,"flexDirection: row,","
justifyContent: "space-between,",";
}
    alignItems: "center,"}
marginBottom: spacing.sm;},","
trendBadge: {,"flexDirection: row,","
alignItems: "center,",
paddingHorizontal: spacing.xs,
}
    paddingVertical: 2,}
    borderRadius: 10}
trendText: {,"fontSize: 10,","
color: "white,
}
    fontWeight: 600,"}";
marginLeft: 2}
metricTitle: {fontSize: 14,
}
    color: colors.textSecondary,}
    marginBottom: spacing.xs;},","
metricValueContainer: {,";}}
  flexDirection: "row,","}
alignItems: "baseline";},","
metricValue: {,";}}
  fontSize: 24,"}
fontWeight: bold";},";
metricUnit: {fontSize: 12,
}
    color: colors.textSecondary,}
    marginLeft: spacing.xs}
chartContainer: {,}
  paddingHorizontal: spacing.lg,}
    marginBottom: spacing.lg}
chartTitle: {,"fontSize: 18,","
fontWeight: "600,",";
}
    color: colors.text,}
    marginBottom: spacing.md}
chart: { borderRadius: 16  }
sectionTitle: {,"fontSize: 18,","
fontWeight: "600,
}
    color: colors.text,}
    marginBottom: spacing.md}
constitutionContainer: {,}
  paddingHorizontal: spacing.lg,}
    marginBottom: spacing.lg;},","
constitutionChart: {,";}}
  alignItems: center,"}";
marginBottom: spacing.md}
constitutionLegend: {backgroundColor: colors.surface,
}
    borderRadius: 12,}
    padding: spacing.md;},","
constitutionItem: {,"flexDirection: "row,",";
}
    alignItems: "center,"}";
paddingVertical: spacing.sm}
constitutionDot: {width: 12,
height: 12,
}
    borderRadius: 6,}
    marginRight: spacing.sm}
constitutionInfo: { flex: 1 }
constitutionName: {,"fontSize: 14,";
}
    fontWeight: 600,}";
color: colors.text}
constitutionDescription: {fontSize: 12,
}
    color: colors.textSecondary,}
    marginTop: 2}
constitutionPercentage: {,"fontSize: 16,";
}
    fontWeight: "bold,","}";
color: colors.text}
historyContainer: {,}
  paddingHorizontal: spacing.lg,}
    marginBottom: spacing.lg;},","
historyHeader: {,"flexDirection: "row,
justifyContent: space-between,";
}
    alignItems: "center,","}";
marginBottom: spacing.md}
viewAllText: {fontSize: 14,";
}
    color: colors.primary,"}
fontWeight: "500";},","
historyItem: {,"flexDirection: row,","
alignItems: "center,",
backgroundColor: colors.surface,
borderRadius: 12,
}
    padding: spacing.md,}
    marginBottom: spacing.sm}
historyIcon: {width: 40,"
height: 40,","
borderRadius: 20,","
backgroundColor: colors.primary + "20,
justifyContent: center,";
}
    alignItems: "center,","}";
marginRight: spacing.md}
historyContent: { flex: 1 }
historyTitle: {,"fontSize: 16,";
}
    fontWeight: "600,}";
color: colors.text}
historyDate: {fontSize: 12,
}
    color: colors.textSecondary,}
    marginTop: 2}
historyStatus: {paddingHorizontal: spacing.sm,
}
    paddingVertical: spacing.xs,}
    borderRadius: 12}
historyStatusText: {,"fontSize: 12,";
}
    color: white,"}
const fontWeight = '600'}
}), []);
export default React.memo(HealthDashboardEnhanced);
