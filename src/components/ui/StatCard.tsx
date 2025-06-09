import React from 'react';
import {
  Animated,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import { useTheme } from '../../contexts/ThemeContext';

export interface StatCardProps {
  /** 标题 */
  title: string;
  /** 主要数值 */
  value: string | number;
  /** 副标题或描述 */
  subtitle?: string;
  /** 前缀 */
  prefix?: string;
  /** 后缀 */
  suffix?: string;
  /** 趋势值 */
  trend?: number;
  /** 趋势类型 */
  trendType?: 'up' | 'down' | 'neutral';
  /** 趋势描述 */
  trendText?: string;
  /** 图标 */
  icon?: React.ReactNode;
  /** 颜色主题 */
  color?: 'primary' | 'success' | 'warning' | 'error' | 'info' | 'neutral';
  /** 是否显示边框 */
  bordered?: boolean;
  /** 是否显示阴影 */
  shadow?: boolean;
  /** 尺寸 */
  size?: 'sm' | 'md' | 'lg';
  /** 布局方向 */
  layout?: 'vertical' | 'horizontal';
  /** 是否可点击 */
  clickable?: boolean;
  /** 点击事件 */
  onPress?: () => void;
  /** 自定义样式 */
  style?: any;
  /** 标题样式 */
  titleStyle?: any;
  /** 数值样式 */
  valueStyle?: any;
  /** 副标题样式 */
  subtitleStyle?: any;
  /** 趋势样式 */
  trendStyle?: any;
  /** 是否显示加载状态 */
  loading?: boolean;
  /** 加载占位符 */
  placeholder?: string;
  /** 是否启用动画 */
  animated?: boolean;
  /** 动画延迟 */
  animationDelay?: number;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  prefix,
  suffix,
  trend,
  trendType = 'neutral',
  trendText,
  icon,
  color = 'neutral',
  bordered = false,
  shadow = true,
  size = 'md',
  layout = 'vertical',
  clickable = false,
  onPress,
  style,
  titleStyle,
  valueStyle,
  subtitleStyle,
  trendStyle,
  loading = false,
  placeholder = '加载中...',
  animated = true,
  animationDelay = 0,
}) => {
  const { currentTheme } = useTheme();
  const styles = createStyles(
    currentTheme,
    color,
    size,
    bordered,
    shadow,
    layout;
  );

  const fadeAnim = React.useRef(new Animated.Value(animated ? 0 : 1)).current;
  const scaleAnim = React.useRef(
    new Animated.Value(animated ? 0.8 : 1)
  ).current;

  React.useEffect() => {
    if (animated) {
      Animated.parallel([
        Animated.timing(fadeAnim, {
          toValue: 1,
          duration: 600,
          delay: animationDelay,
          useNativeDriver: true,
        }),
        Animated.spring(scaleAnim, {
          toValue: 1,
          delay: animationDelay,
          useNativeDriver: true,
        }),
      ]).start();
    }
  }, [animated, animationDelay, fadeAnim, scaleAnim]);

  // 格式化数值
  const formatValue = (val: string | number) => {
    if (typeof val === 'number') {
      // 处理大数字的格式化
      if (val >= 1000000) {
        return (val / 1000000).toFixed(1) + 'M';
      } else if (val >= 1000) {
        return (val / 1000).toFixed(1) + 'K';
      }
      return val.toLocaleString();
    }
    return val;
  };

  // 获取趋势图标
  const getTrendIcon = () => {
    switch (trendType) {
      case 'up':
        return '↗';
      case 'down':
        return '↘';
      default:
        return '→';
    }
  };

  // 获取趋势颜色
  const getTrendColor = () => {
    switch (trendType) {
      case 'up':
        return currentTheme.colors.success;
      case 'down':
        return currentTheme.colors.error;
      default:
        return currentTheme.colors.onSurfaceVariant;
    }
  };

  // 渲染加载状态
  const renderLoading = () => (
    <View style={styles.loadingContainer}>
      <View style={styles.loadingPlaceholder} />
      <Text style={styles.loadingText}>{placeholder}</Text>
    </View>
  );

  // 渲染图标
  const renderIcon = () => {
    if (!icon) return null;

    return <View style={styles.iconContainer}>{icon}</View>;
  };

  // 渲染主要内容
  const renderMainContent = () => (
    <View style={styles.mainContent}>
      <Text style={[styles.title, titleStyle]} numberOfLines={2}>
        {title}
      </Text>

      <View style={styles.valueContainer}>
        {prefix && <Text style={[styles.prefix, valueStyle]}>{prefix}</Text>}
        <Text style={[styles.value, valueStyle]} numberOfLines={1}>
          {formatValue(value)}
        </Text>
        {suffix && <Text style={[styles.suffix, valueStyle]}>{suffix}</Text>}
      </View>

      {subtitle && (
        <Text style={[styles.subtitle, subtitleStyle]} numberOfLines={2}>
          {subtitle}
        </Text>
      )}
    </View>
  );

  // 渲染趋势信息
  const renderTrend = () => {
    if (trend === undefined && !trendText) return null;

    return (
      <View style={styles.trendContainer}>
        {trend !== undefined && (
          <View style={styles.trendValue}>
            <Text style={[styles.trendIcon, { color: getTrendColor() }]}>
              {getTrendIcon()}
            </Text>
            <Text;
              style={[
                styles.trendNumber,
                { color: getTrendColor() },
                trendStyle,
              ]}
            >
              {Math.abs(trend)}%
            </Text>
          </View>
        )}
        {trendText && (
          <Text style={[styles.trendText, trendStyle]} numberOfLines={1}>
            {trendText}
          </Text>
        )}
      </View>
    );
  };

  // 渲染内容
  const renderContent = () => {
    if (loading) {
      return renderLoading();
    }

    if (layout === 'horizontal') {
      return (
        <View style={styles.horizontalLayout}>
          {renderIcon()}
          <View style={styles.horizontalContent}>
            {renderMainContent()}
            {renderTrend()}
          </View>
        </View>
      );
    }

    return (
      <View style={styles.verticalLayout}>
        <View style={styles.header}>
          {renderIcon()}
          {renderTrend()}
        </View>
        {renderMainContent()}
      </View>
    );
  };

  const CardComponent = clickable ? TouchableOpacity : View;

  return (
    <Animated.View;
      style={[
        {
          opacity: fadeAnim,
          transform: [{ scale: scaleAnim }],
        },
      ]}
    >
      <CardComponent;
        style={[styles.container, style]}
        onPress={clickable ? onPress : undefined}
        activeOpacity={clickable ? 0.7 : 1}
      >
        {renderContent()}
      </CardComponent>
    </Animated.View>
  );
};

const createStyles = (
  theme: any,
  color: string,
  size: 'sm' | 'md' | 'lg',
  bordered: boolean,
  shadow: boolean,
  layout: string;
) => {
  const sizeConfig = {
    sm: {,
  padding: theme.spacing.sm,
      titleFontSize: theme.typography.fontSize.sm,
      valueFontSize: theme.typography.fontSize.lg,
      subtitleFontSize: theme.typography.fontSize.xs,
      trendFontSize: theme.typography.fontSize.xs,
      iconSize: 24,
      minHeight: 80,
    },
    md: {,
  padding: theme.spacing.md,
      titleFontSize: theme.typography.fontSize.base,
      valueFontSize: theme.typography.fontSize.xl,
      subtitleFontSize: theme.typography.fontSize.sm,
      trendFontSize: theme.typography.fontSize.sm,
      iconSize: 32,
      minHeight: 100,
    },
    lg: {,
  padding: theme.spacing.lg,
      titleFontSize: theme.typography.fontSize.lg,
      valueFontSize: theme.typography.fontSize['2xl'],
      subtitleFontSize: theme.typography.fontSize.base,
      trendFontSize: theme.typography.fontSize.base,
      iconSize: 40,
      minHeight: 120,
    },
  };

  const config = sizeConfig[size];

  // 获取颜色配置
  const getColorConfig = () => {
    switch (color) {
      case 'primary':
        return {
          background: theme.colors.primaryContainer,
          border: theme.colors.primary,
          accent: theme.colors.primary,
        };
      case 'success':
        return {
          background:
            theme.colors.successContainer || theme.colors.primaryContainer,
          border: theme.colors.success,
          accent: theme.colors.success,
        };
      case 'warning':
        return {
          background:
            theme.colors.warningContainer || theme.colors.primaryContainer,
          border: theme.colors.warning,
          accent: theme.colors.warning,
        };
      case 'error':
        return {
          background: theme.colors.errorContainer,
          border: theme.colors.error,
          accent: theme.colors.error,
        };
      case 'info':
        return {
          background:
            theme.colors.infoContainer || theme.colors.primaryContainer,
          border: theme.colors.info || theme.colors.primary,
          accent: theme.colors.info || theme.colors.primary,
        };
      default:
        return {,
  background: theme.colors.surface,
          border: theme.colors.outline,
          accent: theme.colors.onSurface,
        };
    }
  };

  const colorConfig = getColorConfig();

  return StyleSheet.create({
    container: {,
  backgroundColor: colorConfig.background,
      borderRadius: theme.borderRadius.lg,
      padding: config.padding,
      minHeight: config.minHeight,
      ...(bordered && {
        borderWidth: 1,
        borderColor: colorConfig.border,
      }),
      ...(shadow && {
        shadowColor: theme.colors.shadow,
        shadowOffset: {,
  width: 0,
          height: 2,
        },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 3,
      }),
    },
    verticalLayout: {,
  flex: 1,
    },
    horizontalLayout: {,
  flexDirection: 'row',
      alignItems: 'center',
      flex: 1,
    },
    header: {,
  flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'flex-start',
      marginBottom: theme.spacing.sm,
    },
    horizontalContent: {,
  flex: 1,
      marginLeft: theme.spacing.md,
    },
    iconContainer: {,
  width: config.iconSize,
      height: config.iconSize,
      alignItems: 'center',
      justifyContent: 'center',
    },
    mainContent: {,
  flex: 1,
    },
    title: {,
  fontSize: config.titleFontSize,
      fontWeight: theme.typography.fontWeight.medium,
      color: theme.colors.onSurface,
      marginBottom: theme.spacing.xs,
    },
    valueContainer: {,
  flexDirection: 'row',
      alignItems: 'baseline',
      marginBottom: theme.spacing.xs,
    },
    value: {,
  fontSize: config.valueFontSize,
      fontWeight: theme.typography.fontWeight.bold,
      color: colorConfig.accent,
    },
    prefix: {,
  fontSize: config.valueFontSize * 0.7,
      fontWeight: theme.typography.fontWeight.medium,
      color: colorConfig.accent,
      marginRight: theme.spacing.xs,
    },
    suffix: {,
  fontSize: config.valueFontSize * 0.7,
      fontWeight: theme.typography.fontWeight.medium,
      color: colorConfig.accent,
      marginLeft: theme.spacing.xs,
    },
    subtitle: {,
  fontSize: config.subtitleFontSize,
      color: theme.colors.onSurfaceVariant,
      lineHeight: config.subtitleFontSize * 1.4,
    },
    trendContainer: {,
  flexDirection: layout === 'horizontal' ? 'column' : 'row',
      alignItems: layout === 'horizontal' ? 'flex-end' : 'center',
    },
    trendValue: {,
  flexDirection: 'row',
      alignItems: 'center',
    },
    trendIcon: {,
  fontSize: config.trendFontSize,
      marginRight: theme.spacing.xs,
    },
    trendNumber: {,
  fontSize: config.trendFontSize,
      fontWeight: theme.typography.fontWeight.semibold,
    },
    trendText: {,
  fontSize: config.trendFontSize,
      color: theme.colors.onSurfaceVariant,
      marginTop: layout === 'horizontal' ? theme.spacing.xs : 0,
      marginLeft: layout === 'horizontal' ? 0 : theme.spacing.sm,
    },
    loadingContainer: {,
  flex: 1,
      justifyContent: 'center',
      alignItems: 'center',
    },
    loadingPlaceholder: {,
  width: '60%',
      height: config.valueFontSize,
      backgroundColor: theme.colors.outline,
      borderRadius: theme.borderRadius.sm,
      marginBottom: theme.spacing.sm,
    },
    loadingText: {,
  fontSize: config.subtitleFontSize,
      color: theme.colors.onSurfaceVariant,
    },
  });
};

export default StatCard;
