../../hooks";/../components";/    import React,{ useState, useMemo } from "react"
StyleSheet,"
ScrollView,","
RefreshControl,
  { Dimensions } from ";react-native;
HealthTrendChart,"
HealthPathwayVisualizer,","
AgentEmotionFeedback,
  { ResponsiveContainer } from "../../components";/    const { width   } = Dimensions.get("window;";);
const cardWidth = useMemo(); => useMemo(); => useMemo(); => useMemo(;);
  (); => {}
    useMemo(); => useMemo(); => (width - spacing.xl * 2 - spacing.md) / 2, []),/          []
    ),
  [];
), []);","
export const HealthDashboard: React.FC  = () => {;}","
performanceMonitor: usePerformanceMonitor("HealthDashboard', { "';)'}'';
trackRender: true,trackMemory: true,warnThreshold: 50;);
const { healthData, loading, refreshData   } = useHealthData;(;);
const [selectedTab, setSelectedTab] = useState<string>("all;";);","
const: tabs: TabItem[] = [;]{,"const id = "all;
    {"const id = "vital;
    {"const id = "activity;
    {"const id = "sleep;"";
}
];
  ]}
  getFilteredData: useMemo() => useMemo(); => useMemo(); => useCallback(); => {[]), [])))}","
switch (selectedTab) {"case "vital": ;
        )","
case "activity": ;
        )","
case "sleep": ";
        );
default: ;
}
        return healthDa;t;a}
    }
  };
filteredData: useMemo(); => useMemo(); => useMemo(); => getFilteredData(), []);));
handleCardPress: useMemo() => useMemo(); => useMemo(); => useCallback(data: unknown); => {[]), []);))}
    }
  performanceMonitor.recordRender();","
return (;)
    <ResponsiveContainer style={styles.container}>/      {/;}///          <ScreenHeader,title="健康数据  />/;"/g"/;
}
}","
showBackButton={true};","
rightIcon="chart-line,"";
onRightPress={() = /> {/              }};
      />/      {/;}///          <HealthPathwayVisualizer;"  />"
currentStage={"selectedTab === "vital;
            ? "inspection;
            : selectedTab === "activity;
            ? "regulation;
}
            : "health-preservation"};
        }
        onStagePress={(stage: string) = /> {/           ;}}
      />/      {/;}///          <HealthTrendChart;"  />"
title={"selectedTab === "vital;
            : selectedTab === "activity;
}
}
        data={filteredData.map(d: unknow;n;) = /> ({  date: d.date, value: d.value; }))}/            unit={/;}}/g/;
}
        } />/      {///          <AgentEmotionFeedback;}  />
onFeedback={(type: string) = /> {/           ;}}
      />/      {///            <TabSelector;}  />
tabs={tabs}
          selectedTabId={selectedTab}
          onTabPress={setSelectedTab} />/      </View>/          <ScrollView;  />
style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        refreshControl={}
          <RefreshControl;}  />
refreshing={loading}
            onRefresh={refreshData}
            colors={[colors.primary]}
            tintColor={colors.primary} />/            }
showsVerticalScrollIndicator={false}
      >;
        <View style={styles.cardsContainer}>/              {/filteredData.map(data: unknown, index: number) => ());/g/;
}
            <HealthCard;}  />
key={data.id}
              data={data}
              onPress={handleCardPress}
              style={}[;]}
                  styles.card,}
                  { width: cardWidth}
index % 2 === 0 ? styles.leftCard : styles.rightCard;
];
                ] as any;
              }","
size="medium";
showTrend={true}
              showDescription={false} />/              ))}
        </View>/      </ScrollView>/    </ResponsiveContainer>/      );
};
const styles = useMemo(); => useMemo(); => useMemo(); => useMemo(;);
  (); => {}
    useMemo(); => {}
        useMemo() => {StyleSheet.create({)              container: {flex: 1,
}
                const backgroundColor = colors.background}
              }
tabContainer: {paddingHorizontal: spacing.md,
paddingVertical: spacing.sm,
backgroundColor: colors.surface,
borderBottomWidth: 1,
}
                const borderBottomColor = colors.border}
              }
scrollView: { flex: 1  }
scrollContent: { paddingVertical: spacing.md  ;},","
cardsContainer: {,"flexDirection: "row,
flexWrap: "wrap,
}
                const paddingHorizontal = spacing.md}
              }
card: { marginBottom: spacing.md  ;},);
leftCard: { marginRight: spacing.md  ;},);
const rightCard = { marginLeft: 0  ;});
            }),
          [];
        ),
      [];
    ),"
  []
), []);""
