/
/
import React,{ memo } from ";react";
Text,"
StyleSheet,","
ScrollView,
  { TouchableOpacity } from "react-native;
interface CategoryTabsProps {"
"selectedCategory: CategoryType | ";all", ","
onCategorySelect: (category: CategoryType | all") => void;
}
  style?: unknown}
}
export CategoryTabs: memo<CategoryTabsProps  />({/      selectedCategory,onCategorySelect,style;)}"/;"/g"/;
}) => {}","
const categories: Array<{ key: CategoryType | "all name: string, icon: string, color: string;}> = [;];
    {"const key = "all;"";
=> ({)      key: key as CategoryType}name: config.name,);
icon: config.icon,);
}
      const color = config.color;)}
    }));
];
  ];","
const  handleCategoryPress = useCallback() => {"}
performanceMonitor: usePerformanceMonitor("CategoryTabs", {trackRender: true,trackMemory: false,warnThreshold: 50;);";
    //
onCategorySelect(category);
  };
const renderCategoryTab = useCallback(); => {}
    //
const isSelected = selectedCategory === category.k;e;y;
performanceMonitor.recordRender();
return (;);
      <TouchableOpacity,key={category.key};"  />"
style={[;];"}
styles.tab,isSelected && styles.selectedTab,isSelected && { backgroundColor: category.color + 20;"  ; }};
];
        ]}
        onPress={() = /> handleCategoryPress(category.key)}/            activeOpacity={0.7}
      >;
        <Icon;  />
name={category.icon}
          size={20}
          color={isSelected ? category.color: colors.textSecondary;} />/            <Text;  />
style={[]styles.tabText,}
            isSelected && styles.selectedTabText,}
            isSelected && { color: category.color}
];
          ]} />/              {category.name}
        </Text>/      </TouchableOpacity>/        );
  };
return (;);
    <View style={[styles.container, style]}  />/          <ScrollView;  />
horizontal;
showsHorizontalScrollIndicator={false};
contentContainerStyle={styles.scrollContent} />/            {categories.map(renderCategoryTab)};
      </ScrollView>/    </View>/      ;);"/;"/g"/;
});","
CategoryTabs.displayName = "CategoryTabs";
const: styles = StyleSheet.create({)container: {)}backgroundColor: colors.background,
borderBottomWidth: 1,
}
    const borderBottomColor = colors.border}
  }
scrollContent: {paddingHorizontal: spacing.md,
}
    const paddingVertical = spacing.sm}
  },","
tab: {,"flexDirection: "row,
alignItems: center,";
paddingHorizontal: spacing.md,
paddingVertical: spacing.sm,
marginRight: spacing.sm,
borderRadius: borderRadius.lg,
backgroundColor: colors.surface,
borderWidth: 1,
}
    const borderColor = colors.border;}
  },","
selectedTab: { borderColor: "transparent  ;},";
tabText: {fontSize: fonts.size.sm,"
color: colors.textSecondary,","
marginLeft: spacing.sm,";
}
    const fontWeight = "500"}
  ;},selectedTabText: { fontWeight: 600"  ;};);
