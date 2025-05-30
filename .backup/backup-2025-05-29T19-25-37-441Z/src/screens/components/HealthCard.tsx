import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ViewStyle,
} from 'react-native';
import Icon from '../../components/common/Icon';
import { colors, spacing, borderRadius, fonts } from '../../constants/theme';

export interface HealthData {
  id: string;
  title: string;
  value: string | number;
  unit?: string;
  icon?: string;
  color?: string;
  trend?: 'up' | 'down' | 'stable';
  trendValue?: string;
  description?: string;
  status?: 'normal' | 'warning' | 'danger' | 'good';
}

interface HealthCardProps {
  data: HealthData;
  onPress?: (data: HealthData) => void;
  style?: ViewStyle;
  size?: 'small' | 'medium' | 'large';
  showTrend?: boolean;
  showDescription?: boolean;
}

export const HealthCard: React.FC<HealthCardProps> = ({
  data,
  onPress,
  style,
  size = 'medium',
  showTrend = true,
  showDescription = false,
}) => {
  const handlePress = () => {
    onPress?.(data);
  };

  const getStatusColor = () => {
    switch (data.status) {
      case 'good':
        return colors.success;
      case 'warning':
        return colors.warning;
      case 'danger':
        return colors.error;
      default:
        return colors.primary;
    }
  };

  const getTrendIcon = () => {
    switch (data.trend) {
      case 'up':
        return 'trending-up';
      case 'down':
        return 'trending-down';
      case 'stable':
        return 'trending-neutral';
      default:
        return null;
    }
  };

  const getTrendColor = () => {
    switch (data.trend) {
      case 'up':
        return colors.success;
      case 'down':
        return colors.error;
      case 'stable':
        return colors.textSecondary;
      default:
        return colors.textSecondary;
    }
  };

  const sizeStyles = {
    small: styles.smallCard,
    medium: styles.mediumCard,
    large: styles.largeCard,
  };

  const valueSizeStyles = {
    small: styles.smallValue,
    medium: styles.mediumValue,
    large: styles.largeValue,
  };

  return (
    <TouchableOpacity
      style={[
        styles.container,
        sizeStyles[size],
        { borderLeftColor: data.color || getStatusColor() },
        style,
      ]}
      onPress={handlePress}
      activeOpacity={0.8}
    >
      {/* 头部 */}
      <View style={styles.header}>
        <View style={styles.titleContainer}>
          {data.icon && (
            <Icon
              name={data.icon}
              size={20}
              color={data.color || getStatusColor()}
              style={styles.titleIcon}
            />
          )}
          <Text style={styles.title} numberOfLines={1}>
            {data.title}
          </Text>
        </View>
        
        {showTrend && data.trend && (
          <View style={styles.trendContainer}>
            <Icon
              name={getTrendIcon()!}
              size={16}
              color={getTrendColor()}
            />
            {data.trendValue && (
              <Text style={[styles.trendText, { color: getTrendColor() }]}>
                {data.trendValue}
              </Text>
            )}
          </View>
        )}
      </View>

      {/* 数值 */}
      <View style={styles.valueContainer}>
        <Text style={[styles.value, valueSizeStyles[size]]}>
          {data.value}
        </Text>
        {data.unit && (
          <Text style={styles.unit}>{data.unit}</Text>
        )}
      </View>

      {/* 描述 */}
      {showDescription && data.description && (
        <Text style={styles.description} numberOfLines={2}>
          {data.description}
        </Text>
      )}

      {/* 状态指示器 */}
      <View
        style={[
          styles.statusIndicator,
          { backgroundColor: data.color || getStatusColor() },
        ]}
      />
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.md,
    borderLeftWidth: 4,
    shadowColor: colors.black,
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 3,
    position: 'relative',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  titleContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  titleIcon: {
    marginRight: spacing.xs,
  },
  title: {
    fontSize: fonts.size.sm,
    color: colors.textSecondary,
    fontWeight: '500',
    flex: 1,
  },
  trendContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  trendText: {
    fontSize: fonts.size.xs,
    marginLeft: spacing.xs,
    fontWeight: '500',
  },
  valueContainer: {
    flexDirection: 'row',
    alignItems: 'baseline',
    marginBottom: spacing.xs,
  },
  value: {
    fontWeight: 'bold',
    color: colors.text,
  },
  unit: {
    fontSize: fonts.size.sm,
    color: colors.textSecondary,
    marginLeft: spacing.xs,
  },
  description: {
    fontSize: fonts.size.xs,
    color: colors.textSecondary,
    lineHeight: fonts.lineHeight.sm,
  },
  statusIndicator: {
    position: 'absolute',
    top: spacing.sm,
    right: spacing.sm,
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  // Size variants
  smallCard: {
    padding: spacing.sm,
  },
  mediumCard: {
    padding: spacing.md,
  },
  largeCard: {
    padding: spacing.lg,
  },
  smallValue: {
    fontSize: fonts.size.lg,
  },
  mediumValue: {
    fontSize: fonts.size.xl,
  },
  largeValue: {
    fontSize: fonts.size.xxl,
  },
}); 