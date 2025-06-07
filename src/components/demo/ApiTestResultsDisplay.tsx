import { colors, spacing, typography } from "../../constants/    theme";
import { usePerformanceMonitor } from ../hooks/usePerformanceMonitor"/      View,"
import React from "react";
/
importReact from ";react";
  Text,
  StyleSheet,
  ScrollView,
  { TouchableOpacity } from "react-native";
interface ApiTestResult {
  name: string;
  category: string;
  status: ";PASSED" | FAILED",
  duration: number;
  endpoint: string;
  method: string;
  error?: string
}
interface ApiTestSummary {
  total: number;
  passed: number;
  failed: number;
  successRate: number;
  avgDuration: number;
}
interface ApiTestCategories {
  [key: string]: { total: number;
    passed: number;
    failed: number;
};
}
interface ApiTestResultsDisplayProps {
  summary: ApiTestSummary;
  categories: ApiTestCategories;
  details: ApiTestResult[];
  onRetryTest?: (testName: string) => void;
onViewDetails?: (test: ApiTestResult) => void;
}
export const ApiTestResultsDisplay: React.FC<ApiTestResultsDisplayProps /> = ({/   const performanceMonitor = usePerformanceMonitor("ApiTestResultsDisplay, ";
{/
    trackRender: true,
    trackMemory: true,
    warnThreshold: 50,  });
  summary,
  categories,
  details,
  onRetryTest,
  onViewDetails;
}) => {}
  const getStatusColor = useCallback() => {
    switch (status) {
      case "PASSED":return colors.succe;s;s;
case FAILED":"
        return colors.error;
      default:
        return colors.textSeconda;r;y;
    }
  };
  const getStatusIcon = useCallback() => {
    switch (status) {
      case "PASSED:"
        return ";✅";
      case FAILED":"
        return ";❌;"
      default:
        return ";⏳";
    }
  };
  const getCategoryColor = useCallback(); => {}
    if (successRate === 100) {return colors.succe;s;s;}
    if (successRate >= 90) {return colors.warni;n;g;}
    return colors.error;
  };
  //
    <View style={styles.summaryCard}>/      <Text style={styles.summaryTitle}>📊 测试总览</Text>/      <View style={styles.summaryGrid}>/        <View style={styles.summaryItem}>/          <Text style={styles.summaryLabel}>总测试数</Text>/          <Text style={styles.summaryValue}>{summary.total}</Text>/        </View>/        <View style={styles.summaryItem}>/          <Text style={styles.summaryLabel}>成功</Text>/          <Text style={[styles.summaryValue, { color: colors.success}]} />/                {summary.passed}
          </Text>/        </View>/        <View style={styles.summaryItem}>/          <Text style={styles.summaryLabel}>失败</Text>/          <Text style={[styles.summaryValue, { color: colors.error}]} />/                {summary.failed}
          </Text>/        </View>/        <View style={styles.summaryItem}>/          <Text style={styles.summaryLabel}>成功率</Text>/  >
            styles.summaryValue,
            { color: getCategoryColor(summary.successRate)   }
          ]} />/                {summary.successRate.toFixed(1)}%
          </Text>/        </View>/      </View>/      <View style={styles.performanceInfo}>/        <Text style={styles.performanceLabel}>/              ⚡ 平均响应时间: {summary.avgDuration.toFixed(2)}ms;
        </Text>/      </View>/    </View>/      ), []);
  //
    <View style={styles.categoriesCard}>/      <Text style={styles.categoriesTitle}>📋 按类别统计</Text>/          {Object.entries(categories).map(); => {}
        performanceMonitor.recordRender();
        return (;
          <View key={category} style={styles.categoryItem}>/            <View style={styles.categoryHeader}>/              <Text style={styles.categoryName}>{category}</Text>/  >;
                styles.categoryRate,{ color: getCategoryColor(successRate)   };
              ]} />/                {stats.passed}/{stats.total} ({successRate.toFixed(1)}%)/              </Text>/            </View>/            <View style={styles.categoryProgress}>/                  <View;
style={[
                  styles.categoryProgressBar,
                  { width: `${successRate  }%`,
                    backgroundColor: getCategoryColor(successRate)}
                ]};
              />/            </View>/          </View>/            ;);
      })}
    </View>/      );
  //
    <View style={styles.detailsCard}>/      <Text style={styles.detailsTitle}>🔍 测试详情</Text>/          {details.map((test, index) => (
        <TouchableOpacity;
key={index}
          style={styles.testItem}
          onPress={() = accessibilityLabel="TODO: 添加无障碍标签" /> onViewDetails?.(test)}/            >
          <View style={styles.testHeader}>/            <Text style={styles.testIcon}>{getStatusIcon(test.status)}</Text>/            <View style={styles.testInfo}>/              <Text style={styles.testName}>{test.name}</Text>/              <Text style={styles.testEndpoint}>/                    {test.method} {test.endpoint}
              </Text>/            </View>/            <View style={styles.testMeta}>/              <Text style={styles.testDuration}>{test.duration}ms</Text>/  >
                styles.testStatus,
                { color: getStatusColor(test.status)   }
              ]} />/                    {test.status}
              </Text>/            </View>/          </View>/              {test.error && (
        <View style={styles.errorContainer}>/              <Text style={styles.errorText}>{test.error}</Text>/                  {onRetryTest && (
                <TouchableOpacity;
style={styles.retryButton}
                  onPress={() = accessibilityLabel="TODO: 添加无障碍标签" /> onRetryTest(test.name)}/                    >
                  <Text style={styles.retryButtonText}>重试</Text>/                </TouchableOpacity>/                  )}
            </View>/              )}
        </TouchableOpacity>/          ))}
    </View>/      ), []);
  return (;
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false} />/          {renderSummaryCard()};
      {renderCategoriesCard()};
      {renderTestDetails()};
    </ScrollView>/      ;);
};
const styles = useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo() => StyleSheet.create({container: {,
  flex: 1,
    backgroundColor: colors.background;
  },
  summaryCard: {,
  backgroundColor: colors.white,
    borderRadius: 12,
    padding: spacing.lg,
    marginBottom: spacing.md,
    shadowColor: #000",
    shadowOffset: { width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3;
  },
  summaryTitle: {,
  fontSize: typography.fontSize.lg,
    fontWeight: "bold,",
    color: colors.textPrimary,
    marginBottom: spacing.md;
  },
  summaryGrid: {,
  flexDirection: "row",
    flexWrap: wrap",
    justifyContent: "space-between"
  },
  summaryItem: {,
  width: "48%",
    alignItems: center",
    marginBottom: spacing.sm;
  },
  summaryLabel: {,
  fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    marginBottom: 4;
  },
  summaryValue: {,
  fontSize: typography.fontSize.xl,
    fontWeight: "bold,",
    color: colors.textPrimary;
  },
  performanceInfo: {,
  marginTop: spacing.md,
    paddingTop: spacing.md,
    borderTopWidth: 1,
    borderTopColor: colors.border,
    alignItems: "center"
  },
  performanceLabel: {,
  fontSize: typography.fontSize.base,
    color: colors.textSecondary;
  },
  categoriesCard: {,
  backgroundColor: colors.white,
    borderRadius: 12,
    padding: spacing.lg,
    marginBottom: spacing.md,
    shadowColor: #000",
    shadowOffset: { width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3;
  },
  categoriesTitle: {,
  fontSize: typography.fontSize.lg,
    fontWeight: "bold,",
    color: colors.textPrimary,
    marginBottom: spacing.md;
  },
  categoryItem: { marginBottom: spacing.md  },
  categoryHeader: {,
  flexDirection: "row",
    justifyContent: space-between",
    alignItems: "center,",
    marginBottom: spacing.xs;
  },
  categoryName: {,
  fontSize: typography.fontSize.base,
    fontWeight: "600",
    color: colors.textPrimary,
    textTransform: capitalize""
  },
  categoryRate: {,
  fontSize: typography.fontSize.sm,
    fontWeight: "bold"
  },
  categoryProgress: {,
  height: 6,
    backgroundColor: colors.gray200,
    borderRadius: 3,
    overflow: "hidden"
  },
  categoryProgressBar: {,
  height: 100%",
    borderRadius: 3;
  },
  detailsCard: {,
  backgroundColor: colors.white,
    borderRadius: 12,
    padding: spacing.lg,
    marginBottom: spacing.md,
    shadowColor: "#000,",
    shadowOffset: { width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3;
  },
  detailsTitle: {,
  fontSize: typography.fontSize.lg,
    fontWeight: "bold",
    color: colors.textPrimary,
    marginBottom: spacing.md;
  },
  testItem: {,
  borderBottomWidth: 1,
    borderBottomColor: colors.border,
    paddingVertical: spacing.md;
  },
  testHeader: {,
  flexDirection: row",
    alignItems: "center"
  },
  testIcon: {,
  fontSize: 20,
    marginRight: spacing.sm;
  },
  testInfo: {,
  flex: 1,
    marginRight: spacing.sm;
  },
  testName: {,
  fontSize: typography.fontSize.base,
    fontWeight: "600",
    color: colors.textPrimary,
    marginBottom: 2;
  },
  testEndpoint: {,
  fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    fontFamily: monospace""
  },
  testMeta: { alignItems: "flex-end  },"
  testDuration: {,
  fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    marginBottom: 2;
  },
  testStatus: {,
  fontSize: typography.fontSize.sm,
    fontWeight: "bold"
  },
  errorContainer: {,
  marginTop: spacing.sm,
    marginLeft: 32,
    padding: spacing.sm,
    backgroundColor: colors.gray100,
    borderRadius: 6,
    flexDirection: row",
    alignItems: "center,",
    justifyContent: "space-between",
    borderLeftWidth: 3,
    borderLeftColor: colors.error;
  },
  errorText: {,
  flex: 1,
    fontSize: typography.fontSize.sm,
    color: colors.error,
    marginRight: spacing.sm;
  },
  retryButton: {,
  backgroundColor: colors.primary,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: 4;
  },
  retryButtonText: {,
  fontSize: typography.fontSize.sm,
    color: colors.white,
    fontWeight: bold""
  }
}), []);
