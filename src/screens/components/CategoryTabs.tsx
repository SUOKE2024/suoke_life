import React from "react";
import { CategoryType } from "../../types/explore/import { CATEGORIES  } from ";";../../data/exploreData";/importIcon from ../../components/common/Icon"/import { colors, spacing, fonts, borderRadius } from "../../constants/////    theme";"
/////
importReact,{ memo } from ";react"
import { usePerformanceMonitor } from ../hooks/usePerformanceMonitor"/////      View,;"
  Text,
  StyleSheet,
  ScrollView,
  { TouchableOpacity } from "react-native"
interface CategoryTabsProps { selectedCategory: CategoryType | ";all",
  onCategorySelect: (category: CategoryType | all") => void;"
  style?: unknown}
export const CategoryTabs = memo<CategoryTabsProps />(({/////      selectedCategory,;
  onCategorySelect,;
  style;
}) => {}
  const categories: Array<{ key: CategoryType | "all name: string, icon: string, color: string}> = [;"
    { key: "all", name: 全部", icon: "view-grid, color: colors.primary},;
    ...Object.entries(CATEGORIES).map(([key, config]);
 => ({
      key: key as CategoryType,
      name: config.name,
      icon: config.icon,
      color: config.color;
    }))
  ];
  const handleCategoryPress = useCallback(() => {;}
  // 性能监控 //////     const performanceMonitor = usePerformanceMonitor("CategoryTabs", {
    trackRender: true,
    trackMemory: false,
    warnThreshold: 50, // ms //////     };);
    // TODO: Implement function body *}, []) ////
    onCategorySelect(category);
  };
  const renderCategoryTab = useCallback((); => {;}
    // TODO: Implement function body *}, []) ////
    const isSelected = selectedCategory === category.k;e;y;
    // 记录渲染性能 //////
    performanceMonitor.recordRender()
    return (
      <TouchableOpacity,
        key={category.key}
        style={[
          styles.tab,
          isSelected && styles.selectedTab,
          isSelected && { backgroundColor: category.color + 20;"  ; }"
        ]}
        onPress={() = /> handleCategoryPress(category.key)}/////            activeOpacity={0.7}
      >
        <Icon;
name={category.icon}
          size={20}
          color={isSelected ? category.color: colors.textSecondary} />/////            <Text;
style={[
            styles.tabText,
            isSelected && styles.selectedTabText,
            isSelected && { color: category.color}
          ]} />/////              {category.name}
        </Text>/      </TouchableOpacity>/////        );
  };
  return (
    <View style={[styles.container, style]} />/////          <ScrollView;
horizontal;
        showsHorizontalScrollIndicator={false};
        contentContainerStyle={styles.scrollContent} />/////            {categories.map(renderCategoryTab)};
      </ScrollView>/    </View>/////      ;);
});
CategoryTabs.displayName = "CategoryTabs"
const styles = StyleSheet.create({;
  container: {
    backgroundColor: colors.background,
    borderBottomWidth: 1,
    borderBottomColor: colors.border;
  },
  scrollContent: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm;
  },
  tab: {
    flexDirection: "row",
    alignItems: center","
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    marginRight: spacing.sm,
    borderRadius: borderRadius.lg,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border;
  },
  selectedTab: { borderColor: "transparent  },"
  tabText: {
    fontSize: fonts.size.sm,
    color: colors.textSecondary,
    marginLeft: spacing.sm,
    fontWeight: "500"
  },;
  selectedTabText: { fontWeight: 600"  };};);"