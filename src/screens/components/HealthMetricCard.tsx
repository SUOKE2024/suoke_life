import {   View, Text, StyleSheet, TouchableOpacity   } from 'react-native';
import React from "react";
// HealthMetricCard.tsx   索克生活APP - 自动生成的类型安全文件     @description TODO: 添加文件描述 @author 索克生活开发团队   @version 1.0.0;
importIcon from "../../components/common/Icon";/import { HealthMetric } from "../../types/life";/    importReact from "react";
  colors,
  spacing,
  typography,{ borderRadius } from "../../constants/theme";/    interface HealthMetricCardProps {
  metric: HealthMetric;
  onPress?: () => void;
  getTrendIcon: (trend: string) => string;
}
const HealthMetricCard: React.FC<HealthMetricCardProps />  = ({/      metric,onPress,)
  getTrendIcon;
}) => {}
  const progressPercentage = (metric.value / metric.target) * 1/      const isAboveTarget = metric.value >= metric.targ;e;t;
return (;)
    <TouchableOpacity;
style={styles.container}
      onPress={onPress}
      disabled={!onPress}
    accessibilityLabel="TODO: 添加无障碍标签" />/      <View style={styles.header}>/            <View;
style={[
            styles.iconContainer,
            { backgroundColor: metric.color + "2;0;"   }}
          ]} />/          <Icon name={metric.icon} size={20} color={metric.color} />/        </View>/        <View style={styles.headerInfo}>/          <Text style={styles.name}>{metric.name}</Text>/          <View style={styles.trendContainer}>/                <Icon;
name={getTrendIcon(metric.trend)}
              size={16}
              color={
                metric.trend === "up"
                  ? colors.success: metric.trend === "down"? colors.error: colors.textSecondary} />/          </View>/        </View>/      </View>/
      <View style={styles.valueContainer}>/        <Text style={[styles.value, { color: metric.color}}]} />/              {metric.value}
        </Text>/        <Text style={styles.unit}>{metric.unit}</Text>/      </View>/
      <View style={styles.progressContainer}>/        <View style={styles.progressBackground}>/              <View;
style={[
              styles.progressFill,
              {
                width: `${Math.min(progressPercentage, 100)}}%`,
                backgroundColor: isAboveTarget ? colors.success : metric.color;
              }
            ]}
          />/        </View>/        <Text style={styles.target}>/              目标: {metric.target}
          {metric.unit}
        </Text>/      </View>/
      <Text style={styles.suggestion} numberOfLines={2} />/            {metric.suggestion}
      </Text>/    </TouchableOpacity>/      );
};
const styles = StyleSheet.create({container: {),
  backgroundColor: colors.white,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    marginHorizontal: spacing.sm,
    marginVertical: spacing.sm,
    shadowColor: colors.black,shadowOffset: { width: 0, height;: ;2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
    minWidth: 200;
  },
  header: {,
  flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: spacing.md;
  },
  iconContainer: {,
  width: 40,
    height: 40,
    borderRadius: borderRadius.md,
    justifyContent: "center",
    alignItems: "center"
  },
  headerInfo: {,
  flex: 1,
    marginLeft: spacing.md;
  },
  name: {,
  fontSize: typography.fontSize.base,
    fontWeight: "500" as any,
    color: colors.textPrimary;
  },
  trendContainer: { marginTop: spacing.xs  },
  valueContainer: {,
  flexDirection: "row",
    alignItems: "baseline",
    marginBottom: spacing.md;
  },
  value: {,
  fontSize: typography.fontSize["3xl"],
    fontWeight: "700" as any;
  },
  unit: {,
  fontSize: typography.fontSize.base,
    color: colors.textSecondary,
    marginLeft: spacing.xs;
  },
  progressContainer: { marginBottom: spacing.md  },
  progressBackground: {,
  height: 6,
    backgroundColor: colors.border,
    borderRadius: 3,
    marginBottom: spacing.xs;
  },
  progressFill: {,
  height: "100%",
    borderRadius: 3;
  },
  target: {,
  fontSize: typography.fontSize.sm,
    color: colors.textSecondary;
  },
  suggestion: {,
  fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    lineHeight: typography.fontSize.sm * typography.lineHeight.normal;
  }
});
export default React.memo(HealthMetricCard);