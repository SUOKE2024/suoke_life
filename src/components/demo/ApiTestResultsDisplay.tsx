
import React from "react";"";"";
/"/;,"/g"/;
const importReact = from ";react";";
Text,;
StyleSheet,";,"";
ScrollView,";"";
  { TouchableOpacity } from "react-native";";
interface ApiTestResult {name: string,";,}category: string,";,"";
status: ";PASSED" | FAILED",";
duration: number,;
endpoint: string,;
const method = string;
}
}
  error?: string;}
}
interface ApiTestSummary {total: number}passed: number,;
failed: number,;
successRate: number,;
}
}
  const avgDuration = number;}
}
interface ApiTestCategories {[key: string]: { total: number}passed: number,;
}
}
  const failed = number;}
};
}
interface ApiTestResultsDisplayProps {summary: ApiTestSummary}categories: ApiTestCategories,;
const details = ApiTestResult[];
onRetryTest?: (testName: string) => void;
}
}
onViewDetails?: (test: ApiTestResult) => void;}";"";
}";,"";
export const ApiTestResultsDisplay: React.FC<ApiTestResultsDisplayProps  /> = ({/;)/   performanceMonitor: usePerformanceMonitor("ApiTestResultsDisplay, ";))"/;}{//;,}trackRender: true,;"/g"/;
}
    trackMemory: true,}
    const warnThreshold = 50;});
summary,;
categories,;
details,;
onRetryTest,;
onViewDetails;
}) => {}
  const  getStatusColor = useCallback() => {";,}switch (status) {";,}case "PASSED": return colors.succe;s;s;";,"";
const case = FAILED": ";
return colors.error;
default: ;
}
        return colors.textSeconda;r;y;}
    }
  };
const  getStatusIcon = useCallback() => {";,}switch (status) {";,}case "PASSED: ";
return ";✅";";,"";
const case = FAILED": ";
return ";❌;";
const default = ";"";
}
        return ";⏳";"}"";"";
    }
  };
const getCategoryColor = useCallback(); => {}
    if (successRate === 100) {return colors.succe;s;s;}
    if (successRate >= 90) {return colors.warni;n;g;}
    return colors.error;
  };
  ///;/g/;
    <View style={styles.summaryCard}>/      <Text style={styles.summaryTitle}>📊 测试总览</Text>/      <View style={styles.summaryGrid}>/        <View style={styles.summaryItem}>/          <Text style={styles.summaryLabel}>总测试数</Text>/          <Text style={styles.summaryValue}>{summary.total}</Text>/        </View>/        <View style={styles.summaryItem}>/          <Text style={styles.summaryLabel}>成功</Text>/          <Text style={[styles.summaryValue, { color: colors.success;}}]}  />/                {summary.passed}/;/g/;
          </Text>/        </View>/        <View style={styles.summaryItem}>/          <Text style={styles.summaryLabel}>失败</Text>/          <Text style={[styles.summaryValue, { color: colors.error;}}]}  />/                {summary.failed}/;/g/;
          </Text>/        </View>/        <View style={styles.summaryItem}>/          <Text style={styles.summaryLabel}>成功率</Text>/  >/;,/g/;
styles.summaryValue,;
            { color: getCategoryColor(summary.successRate)   ;}
          ]} />/                {summary.successRate.toFixed(1)}%/;/g/;
          </Text>/        </View>/      </View>/      <View style={styles.performanceInfo}>/        <Text style={styles.performanceLabel}>/              ⚡ 平均响应时间: {summary.avgDuration.toFixed(2)}ms;/;/g/;
        </Text>/      </View>/    </View>/      ), []);/;/g/;
  ///;/g/;
    <View style={styles.categoriesCard}>/      <Text style={styles.categoriesTitle}>📋 按类别统计</Text>/          {Object.entries(categories).map(); => {}/;,/g/;
performanceMonitor.recordRender();
return (;);
          <View key={category} style={styles.categoryItem}>/            <View style={styles.categoryHeader}>/              <Text style={styles.categoryName}>{category}</Text>/  >;/;,/g/;
styles.categoryRate,{ color: getCategoryColor(successRate)   ;};
              ]} />/                {stats.passed}/{stats.total} ({successRate.toFixed(1)}%)/              </Text>/            </View>/            <View style={styles.categoryProgress}>/                  <View;  />/;,/g/;
style={}[;]}
                  styles.categoryProgressBar,}
                  { width: `${successRate  ;}}%`,````;,```;
const backgroundColor = getCategoryColor(successRate);}
];
                ]};
              />/            </View>/          </View>/            ;);/;/g/;
      })}
    </View>/      );/;/g/;
  ///;/g/;
    <View style={styles.detailsCard}>/      <Text style={styles.detailsTitle}>🔍 测试详情</Text>/          {/;,}details.map(test, index) => ());/g/;
}
        <TouchableOpacity;}  />/;,/g/;
key={index}";,"";
style={styles.testItem}";,"";
onPress={() = accessibilityLabel="操作按钮" /> onViewDetails?.(test)}/            >"/;"/g"/;
          <View style={styles.testHeader}>/            <Text style={styles.testIcon}>{getStatusIcon(test.status)}</Text>/            <View style={styles.testInfo}>/              <Text style={styles.testName}>{test.name}</Text>/              <Text style={styles.testEndpoint}>/                    {test.method} {test.endpoint}/;/g/;
              </Text>/            </View>/            <View style={styles.testMeta}>/              <Text style={styles.testDuration}>{test.duration}ms</Text>/  >/;,/g/;
styles.testStatus,;
                { color: getStatusColor(test.status)   ;}
              ]} />/                    {test.status}/;/g/;
              </Text>/            </View>/          </View>/              {test.error  && <View style={styles.errorContainer}>/              <Text style={styles.errorText}>{test.error}</Text>/                  {onRetryTest  && <TouchableOpacity;}"  />/;,"/g"/;
style={styles.retryButton}";,"";
onPress={() = accessibilityLabel="操作按钮" /> onRetryTest(test.name)}/                    >"/;"/g"/;
                  <Text style={styles.retryButtonText}>重试</Text>/                </TouchableOpacity>/                  )}/;/g/;
            </View>/              )}/;/g/;
        </TouchableOpacity>/          ))}/;/g/;
    </View>/      ), []);/;,/g/;
return (;);
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}  />/          {renderSummaryCard()};/;/g/;
      {renderCategoriesCard()};
      {renderTestDetails()};
    </ScrollView>/      ;);/;/g/;
};
styles: useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo() => StyleSheet.create({)container: {)}flex: 1,;
}
    const backgroundColor = colors.background;}
  }
summaryCard: {backgroundColor: colors.white,;
borderRadius: 12,;
padding: spacing.lg,";,"";
marginBottom: spacing.md,";"";
}
    shadowColor: #000";","}";
shadowOffset: { width: 0, height: 2;}
shadowOpacity: 0.1,;
shadowRadius: 4,;
const elevation = 3;
  }
summaryTitle: {,";,}fontSize: typography.fontSize.lg,";,"";
fontWeight: "bold,",";,"";
color: colors.textPrimary,;
}
    const marginBottom = spacing.md;}
  },";,"";
summaryGrid: {,";,}flexDirection: "row";",";
flexWrap: wrap";",";"";
}
    const justifyContent = "space-between"}"";"";
  ;},";,"";
summaryItem: {,";,}width: "48%";",";
alignItems: center";","";"";
}
    const marginBottom = spacing.sm;}
  }
summaryLabel: {fontSize: typography.fontSize.sm,;
color: colors.textSecondary,;
}
    const marginBottom = 4;}
  }
summaryValue: {,";,}fontSize: typography.fontSize.xl,";,"";
fontWeight: "bold,",";"";
}
    const color = colors.textPrimary;}
  }
performanceInfo: {marginTop: spacing.md,;
paddingTop: spacing.md,;
borderTopWidth: 1,";,"";
borderTopColor: colors.border,";"";
}
    const alignItems = "center"}"";"";
  ;}
performanceLabel: {fontSize: typography.fontSize.base,;
}
    const color = colors.textSecondary;}
  }
categoriesCard: {backgroundColor: colors.white,;
borderRadius: 12,;
padding: spacing.lg,";,"";
marginBottom: spacing.md,";"";
}
    shadowColor: #000";","}";
shadowOffset: { width: 0, height: 2;}
shadowOpacity: 0.1,;
shadowRadius: 4,;
const elevation = 3;
  }
categoriesTitle: {,";,}fontSize: typography.fontSize.lg,";,"";
fontWeight: "bold,",";,"";
color: colors.textPrimary,;
}
    const marginBottom = spacing.md;}
  }
categoryItem: { marginBottom: spacing.md  ;},";,"";
categoryHeader: {,";,}flexDirection: "row";",";
justifyContent: space-between";",";,"";
alignItems: "center,",";"";
}
    const marginBottom = spacing.xs;}
  }
categoryName: {,";,}fontSize: typography.fontSize.base,";,"";
fontWeight: "600";",";
color: colors.textPrimary,";"";
}
    const textTransform = capitalize"}"";"";
  ;}
categoryRate: {,";,}fontSize: typography.fontSize.sm,";"";
}
    const fontWeight = "bold"}"";"";
  ;}
categoryProgress: {height: 6,;
backgroundColor: colors.gray200,";,"";
borderRadius: 3,";"";
}
    const overflow = "hidden"}"";"";
  ;},";,"";
categoryProgressBar: {,";,}height: 100%";",";"";
}
    const borderRadius = 3;}
  }
detailsCard: {backgroundColor: colors.white,;
borderRadius: 12,;
padding: spacing.lg,";,"";
marginBottom: spacing.md,";"";
}
    shadowColor: "#000,","}";
shadowOffset: { width: 0, height: 2;}
shadowOpacity: 0.1,;
shadowRadius: 4,;
const elevation = 3;
  }
detailsTitle: {,";,}fontSize: typography.fontSize.lg,";,"";
fontWeight: "bold";",";
color: colors.textPrimary,;
}
    const marginBottom = spacing.md;}
  }
testItem: {borderBottomWidth: 1,;
borderBottomColor: colors.border,;
}
    const paddingVertical = spacing.md;}
  },";,"";
testHeader: {,";,}flexDirection: row";",";"";
}
    const alignItems = "center"}"";"";
  ;}
testIcon: {fontSize: 20,;
}
    const marginRight = spacing.sm;}
  }
testInfo: {flex: 1,;
}
    const marginRight = spacing.sm;}
  }
testName: {,";,}fontSize: typography.fontSize.base,";,"";
fontWeight: "600";",";
color: colors.textPrimary,;
}
    const marginBottom = 2;}
  }
testEndpoint: {fontSize: typography.fontSize.sm,";,"";
color: colors.textSecondary,";"";
}
    const fontFamily = monospace"}"";"";
  ;},";,"";
testMeta: { alignItems: "flex-end  ;},";
testDuration: {fontSize: typography.fontSize.sm,;
color: colors.textSecondary,;
}
    const marginBottom = 2;}
  }
testStatus: {,";,}fontSize: typography.fontSize.sm,";"";
}
    const fontWeight = "bold"}"";"";
  ;}
errorContainer: {marginTop: spacing.sm,;
marginLeft: 32,;
padding: spacing.sm,;
backgroundColor: colors.gray100,";,"";
borderRadius: 6,";,"";
flexDirection: row";",";,"";
alignItems: "center,",";,"";
justifyContent: "space-between";",";
borderLeftWidth: 3,;
}
    const borderLeftColor = colors.error;}
  }
errorText: {flex: 1,;
fontSize: typography.fontSize.sm,;
color: colors.error,;
}
    const marginRight = spacing.sm;}
  }
retryButton: {backgroundColor: colors.primary,;
paddingHorizontal: spacing.sm,;
paddingVertical: spacing.xs,;
}
    const borderRadius = 4;}
  }
retryButtonText: {fontSize: typography.fontSize.sm,";,"";
color: colors.white,";"";
}
    const fontWeight = bold"}"";"";
  ;}";"";
}), []);""";