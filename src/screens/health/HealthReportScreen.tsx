import { useNavigation } from "@react-navigation/native"
import React, { useEffect, useRef, useState } from "react";
import {Animated,
Dimensions,
RefreshControl,
ScrollView,
Share,
StyleSheet,
Text,"
TouchableOpacity,";
} fromiew'}
} from "react-native;
import {  SafeAreaView  } from "react-native-safe-area-context"
import Icon from "react-native-vector-icons/MaterialCommunityIcons"
import { Button } from "../../components/ui/Button"
import {borderRadius,
colors,
shadows,"
spacing,";
} fromypography'}
} from "../../constants/theme"/;"/g"/;
const { width: screenWidth ;} = Dimensions.get('window');
interface HealthMetric {id: string}name: string,
value: number,
unit: string,'
status: 'excellent' | 'good' | 'normal' | 'attention' | 'warning,'
trend: 'up' | 'down' | 'stable,'';
change: number,
icon: string,
color: string,
const description = string;
}
}
  recommendation?: string}
}
interface HealthScore {overall: number}categories: {cardiovascular: number,
metabolism: number,
immunity: number,
mental: number,
}
}
  const sleep = number}
  };
}
interface AIInsight {'
'id: string,'
type: 'positive' | 'neutral' | 'warning,'';
title: string,
content: string,'
priority: 'high' | 'medium' | 'low,'';
actionable: boolean,
}
  const icon = string}
}
const  HealthReportScreen: React.FC = () => {const navigation = useNavigation()const [refreshing, setRefreshing] = useState(false);
const [activeTab, setActiveTab] = useState<'
    'overview' | 'metrics' | 'insights' | 'trends'
  >('overview');
const [reportData, setReportData] = useState<any>(null);
  // 动画值
const fadeAnim = useRef(new Animated.Value(0)).current;
const slideAnim = useRef(new Animated.Value(50)).current;
  // 健康评分
const  healthScore = {overall: 85}categories: {cardiovascular: 88,
metabolism: 82,
immunity: 90,
mental: 78,
}
      const sleep = 85}
    }
  };
  // 健康指标
const  healthMetrics = [;]'
    {'id: '1,'
value: 120,'
unit: 'mmHg,'
status: 'good,'
trend: 'stable,'';
change: 0,'
icon: 'heart-pulse,'';
const color = colors.success;
}
}
    },'
    {'id: '2,'
value: 72,'
unit: 'bpm,'
status: 'excellent,'
trend: 'down,'';
change: -3,'
icon: 'heart,'';
const color = colors.primary;
}
}
    },'
    {'id: '3,'
name: 'BMI,'';
value: 22.5,'
unit: 'kg/m²,''/,'/g,'/;
  status: 'normal,'
trend: 'up,'';
change: 0.3,'
icon: 'scale-bathroom,'';
const color = colors.info;
}
}
    },'
    {'id: '4,'
value: 5.2,'
unit: 'mmol/L,''/,'/g,'/;
  status: 'good,'
trend: 'stable,'';
change: 0.1,'
icon: 'water,'';
const color = colors.warning;
}
}
    },'
    {'id: '5,'';
value: 82,'
status: 'good,'
trend: 'up,'';
change: 5,'
icon: 'sleep,'';
const color = colors.secondary;
}
}
    }
];
  ];
  // AI洞察
const  aiInsights = [;]'
    {'id: '1,'
type: 'positive,'';
const content = '
priority: 'medium,'';
actionable: false,
}
      const icon = 'heart-plus'}
    ;},'
    {'id: '2,'
type: 'warning,'';
const content = '
priority: 'high,'';
actionable: true,
}
      const icon = 'alert-circle'}
    ;},'
    {'id: '3,'
type: 'neutral,'';
const content = '
priority: 'medium,'';
actionable: true,
}
      const icon = 'nutrition'}
    }
];
  ];
  // 初始化动画
useEffect() => {Animated.parallel([)Animated.timing(fadeAnim, {)        toValue: 1,)]duration: 800,)}
        const useNativeDriver = true)}
      ;}),
Animated.timing(slideAnim, {)toValue: 0,)duration: 800,);
}
        const useNativeDriver = true)}
      ;});
];
    ]).start();
loadReportData();
  }, []);
  // 加载报告数据
const  loadReportData = async () => {// 模拟加载数据/setTimeout() => {setReportData({)generatedAt: new Date().toISOString(),/g/;
}
        const dataPoints = 847}
      ;});
    }, 1000);
  };
  // 刷新数据
const  onRefresh = async () => {setRefreshing(true)const await = loadReportData();
}
    setRefreshing(false)}
  };
  // 获取状态颜色'
const  getStatusColor = useCallback((status: string) => {'switch (status) {'case 'excellent':
return colors.success;
case 'good':
return colors.primary;
case 'normal':
return colors.info;
case 'attention':
return colors.warning;
case 'warning': return colors.error;
  default: ;
}
        return colors.textSecondary}
    }
  };
  // 获取状态文本'
const  getStatusText = useCallback((status: string) => {'switch (status) {'case 'excellent': '
case 'good': '
case 'normal': '
case 'attention': '
case 'warning':
}
      const default = }
    }
  };
  // 获取趋势图标'
const  getTrendIcon = useCallback((trend: string) => {'switch (trend) {'case 'up': '
return 'trending-up
case 'down': '
return 'trending-down
case 'stable': '
return 'trending-neutral';
const default =
}
        return 'minus}
    }
  };
  // 分享报告
const  shareReport = async () => {try {}      const await = Share.share({ ); });
}
)}
      });
    } catch (error) {}
}
    }
  };
  // 渲染标签栏
const  renderTabs = useCallback(() => {const  tabs = [;]];}    ];
}
}
    return (<View style={styles.tabContainer}>);
        {tabs.map(tab) => (<TouchableOpacity;)}  />
key={tab.key});
style={[styles.tab, activeTab === tab.key && styles.activeTab]});
onPress={() => setActiveTab(tab.key as any)}
          >;
            <Icon;  />
name={tab.icon}
              size={20}
              color={}
                activeTab === tab.key ? colors.primary : colors.textSecondary}
              }
            />
            <Text;  />
style={[]styles.tabText,}
                activeTab === tab.key && styles.activeTabText}
];
              ]}
            >;
              {tab.title}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
    );
  };
  // 渲染健康评分
const  renderHealthScore = () => (<View style={styles.scoreContainer}>;)      <View style={styles.overallScore}>;
        <Text style={styles.scoreValue}>{healthScore.overall}</Text>
        <Text style={styles.scoreLabel}>综合评分</Text>
        <View style={styles.scoreRing}>;
          <View;  />
style={[]styles.scoreProgress,}              {)}
                const transform = [)}]                  { rotate: `${(healthScore.overall / 100) * 360;}deg` }```/`;`/g`/`;
];
                ];
              }
            ]}
          />
        </View>
      </View>
      <View style={styles.categoryScores}>;
        {Object.entries(healthScore.categories).map([key, value]) => (<View key={key} style={styles.categoryScore}>;)            <Text style={styles.categoryValue}>{value}</Text>'/;'/g'/;
            <Text style={styles.categoryLabel}>'
              {key === 'cardiovascular''}
                : key === 'metabolism'
                  : key === 'immunity'
                    : key === 'mental'
);
            </Text>)
}
          </View>)}
        ))}
      </View>
    </View>
  );
  // 渲染健康指标
const  renderHealthMetrics = () => (<View style={styles.metricsContainer}>);
      {healthMetrics.map(metric) => (<View key={metric.id} style={styles.metricCard}>;)          <View style={styles.metricHeader}>;
            <View;  />'
style={[;]';}}
                styles.metricIcon,'}
                { backgroundColor: metric.color + '20' }
];
              ]}
            >;
              <Icon name={metric.icon} size={24} color={metric.color}  />
            </View>
            <View style={styles.metricInfo}>;
              <Text style={styles.metricName}>{metric.name}</Text>
              <View style={styles.metricValue}>;
                <Text style={styles.metricNumber}>{metric.value}</Text>
                <Text style={styles.metricUnit}>{metric.unit}</Text>
              </View>
            </View>
            <View style={styles.metricStatus}>;
              <View;)  />
style={[;])}
                  styles.statusBadge,)}
                  { backgroundColor: getStatusColor(metric.status) }
];
                ]}
              >;
                <Text style={styles.statusText}>;
                  {getStatusText(metric.status)}
                </Text>
              </View>
              <View style={styles.trendContainer}>;
                <Icon;  />
name={getTrendIcon(metric.trend)}
                  size={16}
color={'metric.trend === 'up'
                      ? colors.success;
                      : metric.trend === 'down'
                        ? colors.error;
}
                        : colors.textSecondary}
                  }
                />
                {metric.change !== 0 && (<Text;  />/,)style={[]styles.changeText,}                      {}}/g/;
                        const color = metric.change > 0 ? colors.success : colors.error}
                      }
];
                    ]}
                  >'
                    {metric.change > 0 ? '+' : '}')'
                    {metric.change});
                  </Text>)
                )}
              </View>
            </View>
          </View>
          <Text style={styles.metricDescription}>{metric.description}</Text>'
          {metric.recommendation && (<View style={styles.recommendationContainer}>';)              <Icon name="lightbulb-outline" size={16} color={colors.warning}  />"/;"/g"/;
              <Text style={styles.recommendationText}>;
                {metric.recommendation});
              </Text>)
            </View>)
          )}
        </View>
      ))}
    </View>
  );
  // 渲染AI洞察
const  renderAIInsights = () => (<View style={styles.insightsContainer}>);
      {aiInsights.map(insight) => (<View key={insight.id} style={styles.insightCard}>;)          <View style={styles.insightHeader}>;
            <View;  />"
style={[]styles.insightIcon,}                {"const backgroundColor = ","
insight.type === 'positive'
                      ? colors.success + '20'
                      : insight.type === 'warning'
                        ? colors.error + '20'
}
                        : colors.info + '20'}
                }
];
              ]}
            >;
              <Icon;  />
name={insight.icon}
                size={20}
color={'insight.type === 'positive'
                    ? colors.success;
                    : insight.type === 'warning'
                      ? colors.error;
}
                      : colors.info}
                }
              />
            </View>
            <View style={styles.insightInfo}>;
              <Text style={styles.insightTitle}>{insight.title}</Text>
              <View style={styles.insightMeta}>;
                <View;  />'
style={[]styles.priorityBadge,}                    {'const backgroundColor = '
insight.priority === 'high'
                          ? colors.error;
                          : insight.priority === 'medium'
                            ? colors.warning;
}
                            : colors.success}
                    }
];
                  ]}
                >
                  <Text style={styles.priorityText}>'
                    {insight.priority === 'high''}
                      : insight.priority === 'medium'
                  </Text>
                </View>
}
                {insight.actionable && (})                  <View style={styles.actionableBadge}>);
                    <Text style={styles.actionableText}>可执行</Text>)
                  </View>)
                )}
              </View>
            </View>
          </View>
          <Text style={styles.insightContent}>{insight.content}</Text>
          {insight.actionable && (<View style={styles.insightActions}>);
              <Button;)  />
);
onPress={() => {}
                  // 查看建议}
                }
              />
            </View>
          )}
        </View>
      ))}
    </View>
  );
  // 渲染趋势图表'
const  renderTrends = () => (<View style={styles.trendsContainer}>;)      <Text style={styles.trendsTitle}>健康趋势分析</Text>'/;'/g'/;
      <View style={styles.chartPlaceholder}>'
        <Icon name="chart-line" size={48} color={colors.textSecondary}  />"/;"/g"/;
        <Text style={styles.chartPlaceholderText}>趋势图表</Text>
        <Text style={styles.chartPlaceholderSubtext}>;
        </Text>
      </View>
      <View style={styles.trendSummary}>;
        <Text style={styles.trendSummaryTitle}>关键趋势</Text>"
        <View style={styles.trendItems}>
          <View style={styles.trendItem}>
            <Icon name="trending-up" size={16} color={colors.success}  />"/;"/g"/;
            <Text style={styles.trendItemText}>睡眠质量持续改善</Text>"
          </View>"/;"/g"/;
          <View style={styles.trendItem}>
            <Icon name="trending-down" size={16} color={colors.success}  />"/;"/g"/;
            <Text style={styles.trendItemText}>静息心率稳步下降</Text>"
          </View>"/;"/g"/;
          <View style={styles.trendItem}>
            <Icon name="trending-neutral" size={16} color={colors.info}  />"/;"/g"/;
            <Text style={styles.trendItemText}>血压保持稳定</Text>
          </View>
        </View>)
      </View>)
    </View>)
  );
  // 渲染内容"
const  renderContent = useCallback(() => {"switch (activeTab) {"case 'overview':
}
        return (<>)}
            {renderHealthScore()}
            {renderHealthMetrics()}
          < />'/;'/g'/;
        );
case 'metrics':
return renderHealthMetrics();
case 'insights':
return renderAIInsights();
case 'trends': return renderTrends();
  default: ;
return null;
    }
  };
return (<SafeAreaView style={styles.container}>;)      {// 头部}
      <View style={styles.header}>);
        <TouchableOpacity;)  />
style={styles.backButton});
onPress={() => navigation.goBack()}
        >'
          <Icon name="arrow-left" size={24} color={colors.text}  />"/;"/g"/;
        </TouchableOpacity>"
        <Text style={styles.headerTitle}>健康报告</Text>"/;"/g"/;
        <TouchableOpacity style={styles.shareButton} onPress={shareReport}>
          <Icon name="share-variant" size={24} color={colors.text}  />"/;"/g"/;
        </TouchableOpacity>
      </View>
      {// 标签栏}
      {renderTabs()}
      <ScrollView;  />
style={styles.content}
        refreshControl={}
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh}  />
        }
      >;
        <Animated.View;  />
style={[]styles.contentContainer,}            {}
              opacity: fadeAnim,}
];
const transform = [{ translateY: slideAnim ;}];
            }
          ]}
        >;
          {// 报告信息}
          {reportData && (<View style={styles.reportInfo}>;)              <Text style={styles.reportInfoText}>;
              </Text>
              <Text style={styles.reportInfoText}>;
);
              </Text>)
            </View>)
          )}
          {// 内容区域}
          {renderContent()}
        </Animated.View>
      </ScrollView>
    </SafeAreaView>
  );
};
const  styles = StyleSheet.create({)container: {flex: 1,
}
    const backgroundColor = colors.background}
  ;},","
header: {,"flexDirection: 'row,'
alignItems: 'center,'
justifyContent: 'space-between,'';
paddingHorizontal: spacing.lg,
paddingVertical: spacing.md,
backgroundColor: colors.surface,
borderBottomWidth: 1,
}
    const borderBottomColor = colors.border}
  }
backButton: {width: 40,
height: 40,
borderRadius: 20,
backgroundColor: colors.gray100,'
justifyContent: 'center,'
}
    const alignItems = 'center'}
  }
headerTitle: {,'fontSize: typography.fontSize.lg,'
fontWeight: '600' as const;','
}
    const color = colors.text}
  }
shareButton: {width: 40,
height: 40,
borderRadius: 20,
backgroundColor: colors.gray100,'
justifyContent: 'center,'
}
    const alignItems = 'center'}
  ;},'
tabContainer: {,'flexDirection: 'row,'';
backgroundColor: colors.surface,
borderBottomWidth: 1,
}
    const borderBottomColor = colors.border}
  }
tab: {,'flex: 1,'
flexDirection: 'row,'
alignItems: 'center,'
justifyContent: 'center,'';
paddingVertical: spacing.md,
}
    const gap = spacing.xs}
  }
activeTab: {borderBottomWidth: 2,
}
    const borderBottomColor = colors.primary}
  }
tabText: {fontSize: typography.fontSize.sm,
}
    const color = colors.textSecondary}
  }
activeTabText: {,'color: colors.primary,
}
    const fontWeight = '600' as const'}
  }
content: {,}
  const flex = 1}
  }
contentContainer: {,}
  const padding = spacing.lg}
  }
reportInfo: {backgroundColor: colors.surface,
padding: spacing.md,
borderRadius: borderRadius.md,
const marginBottom = spacing.lg;
}
    ...shadows.sm}
  }
reportInfoText: {fontSize: typography.fontSize.sm,
color: colors.textSecondary,
}
    const textAlign = 'center'}
  }
scoreContainer: {backgroundColor: colors.surface,
borderRadius: borderRadius.lg,
padding: spacing.lg,
const marginBottom = spacing.lg;
}
    ...shadows.sm}
  },'
overallScore: {,'alignItems: 'center,'';
marginBottom: spacing.lg,
}
    const position = 'relative'}
  }
scoreValue: {,'fontSize: 48,'
fontWeight: '700' as const;','
}
    const color = colors.primary}
  }
scoreLabel: {fontSize: typography.fontSize.sm,
color: colors.textSecondary,
}
    const marginTop = spacing.xs}
  ;},'
scoreRing: {,'position: 'absolute,'';
width: 120,
height: 120,
borderRadius: 60,
borderWidth: 8,
borderColor: colors.gray200,
}
    const top = -10}
  ;},'
scoreProgress: {,'position: 'absolute,'';
width: 120,
height: 120,
borderRadius: 60,
borderWidth: 8,
borderColor: colors.primary,'
borderRightColor: 'transparent,'
}
    const borderBottomColor = 'transparent'}
  ;},'
categoryScores: {,'flexDirection: 'row,'
}
    const justifyContent = 'space-around'}
  ;},'
categoryScore: {,';}}
  const alignItems = 'center'}
  }
categoryValue: {,'fontSize: typography.fontSize.lg,'
fontWeight: '600' as const;','
}
    const color = colors.text}
  }
categoryLabel: {fontSize: typography.fontSize.xs,
color: colors.textSecondary,
}
    const marginTop = spacing.xs}
  }
metricsContainer: {,}
  const gap = spacing.md}
  }
metricCard: {backgroundColor: colors.surface,
borderRadius: borderRadius.lg,
const padding = spacing.lg;
}
    ...shadows.sm}
  },'
metricHeader: {,'flexDirection: 'row,'
alignItems: 'center,'
}
    const marginBottom = spacing.md}
  }
metricIcon: {width: 48,
height: 48,
borderRadius: 24,'
justifyContent: 'center,'
alignItems: 'center,'
}
    const marginRight = spacing.md}
  }
metricInfo: {,}
  const flex = 1}
  }
metricName: {,'fontSize: typography.fontSize.base,'
fontWeight: '600' as const;','';
color: colors.text,
}
    const marginBottom = spacing.xs}
  ;},'
metricValue: {,'flexDirection: 'row,'
}
    const alignItems = 'baseline'}
  }
metricNumber: {,'fontSize: typography.fontSize.xl,'
fontWeight: '700' as const;','
}
    const color = colors.text}
  }
metricUnit: {fontSize: typography.fontSize.sm,
color: colors.textSecondary,
}
    const marginLeft = spacing.xs}
  ;},'
metricStatus: {,';}}
  const alignItems = 'flex-end'}
  }
statusBadge: {paddingHorizontal: spacing.sm,
paddingVertical: spacing.xs,
borderRadius: borderRadius.sm,
}
    const marginBottom = spacing.xs}
  }
statusText: {fontSize: typography.fontSize.xs,
color: colors.white,
}
    const fontWeight = '600' as const'}
  ;},'
trendContainer: {,'flexDirection: 'row,'
}
    const alignItems = 'center'}
  }
changeText: {fontSize: typography.fontSize.xs,
marginLeft: spacing.xs,
}
    const fontWeight = '600' as const'}
  }
metricDescription: {fontSize: typography.fontSize.sm,
color: colors.text,
lineHeight: 20,
}
    const marginBottom = spacing.sm}
  ;},'
recommendationContainer: {,'flexDirection: 'row,'
alignItems: 'flex-start,'
backgroundColor: colors.warning + '10,'';
padding: spacing.sm,
}
    const borderRadius = borderRadius.sm}
  }
recommendationText: {fontSize: typography.fontSize.sm,
color: colors.text,
marginLeft: spacing.sm,
}
    const flex = 1}
  }
insightsContainer: {,}
  const gap = spacing.md}
  }
insightCard: {backgroundColor: colors.surface,
borderRadius: borderRadius.lg,
const padding = spacing.lg;
}
    ...shadows.sm}
  },'
insightHeader: {,'flexDirection: 'row,'
alignItems: 'flex-start,'
}
    const marginBottom = spacing.md}
  }
insightIcon: {width: 40,
height: 40,
borderRadius: 20,'
justifyContent: 'center,'
alignItems: 'center,'
}
    const marginRight = spacing.md}
  }
insightInfo: {,}
  const flex = 1}
  }
insightTitle: {,'fontSize: typography.fontSize.base,'
fontWeight: '600' as const;','';
color: colors.text,
}
    const marginBottom = spacing.xs}
  ;},'
insightMeta: {,'flexDirection: 'row,'
}
    const gap = spacing.sm}
  }
priorityBadge: {paddingHorizontal: spacing.xs,
paddingVertical: 2,
}
    const borderRadius = borderRadius.sm}
  }
priorityText: {fontSize: typography.fontSize.xs,
color: colors.white,
}
    const fontWeight = '600' as const'}
  ;},'
actionableBadge: {,'backgroundColor: colors.primary + '20,'';
paddingHorizontal: spacing.xs,
paddingVertical: 2,
}
    const borderRadius = borderRadius.sm}
  }
actionableText: {fontSize: typography.fontSize.xs,
color: colors.primary,
}
    const fontWeight = '600' as const'}
  }
insightContent: {fontSize: typography.fontSize.sm,
color: colors.text,
lineHeight: 20,
}
    const marginBottom = spacing.md}
  ;},'
insightActions: {,';}}
  const alignItems = 'flex-start'}
  }
trendsContainer: {backgroundColor: colors.surface,
borderRadius: borderRadius.lg,
const padding = spacing.lg;
}
    ...shadows.sm}
  }
trendsTitle: {,'fontSize: typography.fontSize.lg,'
fontWeight: '600' as const;','';
color: colors.text,
}
    const marginBottom = spacing.lg}
  ;},'
chartPlaceholder: {,'alignItems: 'center,'
justifyContent: 'center,'';
height: 200,
backgroundColor: colors.gray100,
borderRadius: borderRadius.md,
}
    const marginBottom = spacing.lg}
  }
chartPlaceholderText: {fontSize: typography.fontSize.base,
color: colors.textSecondary,
}
    const marginTop = spacing.sm}
  }
chartPlaceholderSubtext: {fontSize: typography.fontSize.sm,
color: colors.textSecondary,
}
    const marginTop = spacing.xs}
  }
trendSummary: {,}
  const marginTop = spacing.lg}
  }
trendSummaryTitle: {,'fontSize: typography.fontSize.base,'
fontWeight: '600' as const;','';
color: colors.text,
}
    const marginBottom = spacing.md}
  }
trendItems: {,}
  const gap = spacing.sm}
  ;},'
trendItem: {,'flexDirection: 'row,'
}
    const alignItems = 'center'}
  }
trendItemText: {fontSize: typography.fontSize.sm,
color: colors.text,);
}
    const marginLeft = spacing.sm)}
  ;});
});
export default HealthReportScreen;
''