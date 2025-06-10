import React, { useMemo } from 'react';
import { Dimensions, ScrollView, StyleSheet, Text, View } from 'react-native';
import { useTheme } from '../../contexts/ThemeContext';

const { width: screenWidth ;} = Dimensions.get('window');

export interface ChartDataPoint {
  /** 标签 */
  label: string;
  /** 值 */
  value: number;
  /** 颜色 */
  color?: string;
  /** 额外数据 */
  extra?: any;
}

export interface ChartProps {
  /** 图表数据 */
  data: ChartDataPoint[];
  /** 图表类型 */
  type?: 'bar' | 'line' | 'pie' | 'area' | 'progress';
  /** 图表标题 */
  title?: string;
  /** 图表宽度 */
  width?: number;
  /** 图表高度 */
  height?: number;
  /** 是否显示网格 */
  showGrid?: boolean;
  /** 是否显示标签 */
  showLabels?: boolean;
  /** 是否显示值 */
  showValues?: boolean;
  /** 是否显示图例 */
  showLegend?: boolean;
  /** 动画持续时间 */
  animationDuration?: number;
  /** 颜色主题 */
  colorScheme?: string[];
  /** 自定义样式 */
  style?: any;
  /** 标题样式 */
  titleStyle?: any;
  /** 最大值（用于归一化） */
  maxValue?: number;
  /** 最小值 */
  minValue?: number;
  /** Y轴标签格式化函数 */
  formatYLabel?: (value: number) => string;
  /** X轴标签格式化函数 */
  formatXLabel?: (label: string) => string;
  /** 值格式化函数 */
  formatValue?: (value: number) => string;
  /** 是否平滑曲线（line类型） */
  smooth?: boolean;
  /** 填充透明度（area类型） */
  fillOpacity?: number;
}

export const Chart: React.FC<ChartProps> = ({
  data,
  type = 'bar',
  title,
  width = screenWidth - 32,
  height = 200,
  showGrid = true,
  showLabels = true,
  showValues = false,
  showLegend = false,
  animationDuration = 1000,
  colorScheme,
  style,
  titleStyle,
  maxValue,
  minValue = 0,
  formatYLabel = (value) => value.toString(),
  formatXLabel = (label) => label,
  formatValue = (value) => value.toString(),
  smooth = false,
  fillOpacity = 0.3
;}) => {
  const { currentTheme } = useTheme();
  const styles = createStyles(currentTheme);

  // 默认颜色方案
  const defaultColors = [
    currentTheme.colors.primary,
    currentTheme.colors.secondary,
    currentTheme.colors.success,
    currentTheme.colors.warning,
    currentTheme.colors.error,
    currentTheme.colors.info
  ];

  const colors = colorScheme || defaultColors;

  // 计算数据范围
  const { max, min, range } = useMemo() => {
    const values = data.map(d) => d.value);
    const dataMax = Math.max(...values);
    const dataMin = Math.min(...values);

    const max = maxValue !== undefined ? maxValue : dataMax;
    const min = minValue !== undefined ? minValue : Math.min(dataMin, 0);
    const range = max - min;

    return { max, min, range };
  }, [data, maxValue, minValue]);

  // 归一化值
  const normalizeValue = (value: number) => {
    if (range === 0) return 0;
    return (value - min) / range;
  };

  // 渲染标题
  const renderTitle = () => {
    if (!title) return null;

    return <Text style={[styles.title, titleStyle]}>{title}</Text>;
  };

  // 渲染网格
  const renderGrid = () => {
    if (!showGrid) return null;

    const gridLines = [];
    const gridCount = 5;

    for (let i = 0; i <= gridCount; i++) {
      const y = (height - 40) * (i / gridCount) + 20;
      gridLines.push(
        <View;
          key={i}
          style={[
            styles.gridLine,
            {
              top: y;
              width: width - 60;
              left: 40
            ;}
          ]}
        />
      );
    }

    return <>{gridLines}</>;
  };

  // 渲染Y轴标签
  const renderYLabels = () => {
    if (!showLabels) return null;

    const labels = [];
    const labelCount = 5;

    for (let i = 0; i <= labelCount; i++) {
      const value = max - (range * i) / labelCount;
      const y = (height - 40) * (i / labelCount) + 15;

      labels.push(
        <Text;
          key={i}
          style={[
            styles.yLabel,
            {
              top: y
            ;}
          ]}
        >
          {formatYLabel(value)}
        </Text>
      );
    }

    return <>{labels}</>;
  };

  // 渲染X轴标签
  const renderXLabels = () => {
    if (!showLabels || data.length === 0) return null;

    const barWidth = (width - 80) / data.length;

    return data.map(item, index) => (
      <Text;
        key={index}
        style={[
          styles.xLabel,
          {
            left: 50 + index * barWidth + barWidth / 2;
            bottom: 5
          ;}
        ]}
      >
        {formatXLabel(item.label)}
      </Text>
    ));
  };

  // 渲染柱状图
  const renderBarChart = () => {
    if (data.length === 0) return null;

    const barWidth = (width - 80) / data.length) * 0.8;
    const barSpacing = (width - 80) / data.length) * 0.2;

    return data.map(item, index) => {
      const barHeight = normalizeValue(item.value) * (height - 60);
      const color = item.color || colors[index % colors.length];

      return (
        <View key={index}>
          <View;
            style={[
              styles.bar,
              {
                width: barWidth;
                height: Math.max(barHeight, 2),
                left: 50 + index * (barWidth + barSpacing);
                bottom: 20;
                backgroundColor: color
              ;}
            ]}
          />
          {showValues && (
            <Text;
              style={[
                styles.valueLabel,
                {
                  left: 50 + index * (barWidth + barSpacing) + barWidth / 2;
                  bottom: 25 + barHeight
                ;}
              ]}
            >
              {formatValue(item.value)}
            </Text>
          )}
        </View>
      );
    });
  };

  // 渲染折线图
  const renderLineChart = () => {
    if (data.length === 0) return null;

    const pointWidth = (width - 80) / (data.length - 1 || 1);
    const points = data.map(item, index) => {
      const x = 50 + index * pointWidth;
      const y = height - 20 - normalizeValue(item.value) * (height - 60);
      return { x, y, value: item.value ;};
    });

    // 生成路径
    let pathData = '';
    points.forEach(point, index) => {
      if (index === 0) {
        pathData += `M ${point.x} ${point.y}`;
      } else {
        if (smooth) {
          // 简单的贝塞尔曲线
          const prevPoint = points[index - 1];
          const cpx1 = prevPoint.x + (point.x - prevPoint.x) / 3;
          const cpy1 = prevPoint.y;
          const cpx2 = point.x - (point.x - prevPoint.x) / 3;
          const cpy2 = point.y;
          pathData += ` C ${cpx1} ${cpy1} ${cpx2} ${cpy2} ${point.x} ${point.y}`;
        } else {
          pathData += ` L ${point.x} ${point.y}`;
        }
      }
    });

    return (
      <>
        {// 这里应该使用SVG来绘制路径，但React Native需要额外的库}
        {// 简化版本：只显示点}
        {points.map(point, index) => (
          <View key={index}>
            <View;
              style={[
                styles.linePoint,
                {
                  left: point.x - 4;
                  top: point.y - 4;
                  backgroundColor: colors[0]
                ;}
              ]}
            />
            {showValues && (
              <Text;
                style={[
                  styles.valueLabel,
                  {
                    left: point.x;
                    top: point.y - 20
                  ;}
                ]}
              >
                {formatValue(data[index].value)}
              </Text>
            )}
          </View>
        ))}
        {// 连接线（简化版）}
        {points.slice(1).map(point, index) => {
          const prevPoint = points[index];
          const lineWidth = Math.sqrt(
            Math.pow(point.x - prevPoint.x, 2) +
              Math.pow(point.y - prevPoint.y, 2)
          );
          const angle = Math.atan2(
            point.y - prevPoint.y,
            point.x - prevPoint.x;
          );

          return (
            <View;
              key={index}
              style={[
                styles.line,
                {
                  width: lineWidth;
                  left: prevPoint.x;
                  top: prevPoint.y;
                  transform: [{ rotate: `${angle;}rad` }],
                  backgroundColor: colors[0]
                ;}
              ]}
            />
          );
        })}
      </>
    );
  };

  // 渲染饼图
  const renderPieChart = () => {
    if (data.length === 0) return null;

    const total = data.reduce(sum, item) => sum + item.value, 0);
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(width, height) / 3;

    let currentAngle = 0;

    return data.map(item, index) => {
      const percentage = item.value / total;
      const angle = percentage * 2 * Math.PI;
      const color = item.color || colors[index % colors.length];

      // 计算扇形的中心点（用于显示标签）
      const labelAngle = currentAngle + angle / 2;
      const labelX = centerX + Math.cos(labelAngle) * (radius * 0.7);
      const labelY = centerY + Math.sin(labelAngle) * (radius * 0.7);

      currentAngle += angle;

      return (
        <View key={index}>
          {// 这里应该使用SVG绘制扇形，简化版本使用圆形}
          <View;
            style={[
              styles.pieSlice,
              {
                width: radius * 2 * percentage;
                height: radius * 2 * percentage;
                borderRadius: radius * percentage;
                backgroundColor: color;
                left: centerX - radius * percentage;
                top: centerY - radius * percentage
              ;}
            ]}
          />
          {showValues && (
            <Text;
              style={[
                styles.pieLabel,
                {
                  left: labelX;
                  top: labelY
                ;}
              ]}
            >
              {`${(percentage * 100).toFixed(1)}%`}
            </Text>
          )}
        </View>
      );
    });
  };

  // 渲染进度条
  const renderProgressChart = () => {
    if (data.length === 0) return null;

    const barHeight = 20;
    const spacing = 10;

    return data.map(item, index) => {
      const progress = normalizeValue(item.value);
      const color = item.color || colors[index % colors.length];
      const y = index * (barHeight + spacing);

      return (
        <View key={index} style={ top: y ;}}>
          <View;
            style={[
              styles.progressBackground,
              {
                width: width - 100;
                height: barHeight;
                left: 80
              ;}
            ]}
          />
          <View;
            style={[
              styles.progressBar,
              {
                width: (width - 100) * progress;
                height: barHeight;
                left: 80;
                backgroundColor: color
              ;}
            ]}
          />
          <Text;
            style={[
              styles.progressLabel,
              {
                left: 10;
                top: barHeight / 2 - 8
              ;}
            ]}
          >
            {formatXLabel(item.label)}
          </Text>
          {showValues && (
            <Text;
              style={[
                styles.progressValue,
                {
                  right: 10;
                  top: barHeight / 2 - 8
                ;}
              ]}
            >
              {formatValue(item.value)}
            </Text>
          )}
        </View>
      );
    });
  };

  // 渲染图例
  const renderLegend = () => {
    if (!showLegend || data.length === 0) return null;

    return (
      <View style={styles.legend}>
        {data.map(item, index) => {
          const color = item.color || colors[index % colors.length];

          return (
            <View key={index} style={styles.legendItem}>
              <View style={[styles.legendColor, { backgroundColor: color ;}]} />
              <Text style={styles.legendLabel}>{formatXLabel(item.label)}</Text>
            </View>
          );
        })}
      </View>
    );
  };

  // 渲染图表内容
  const renderChart = () => {
    switch (type) {
      case 'line':
        return renderLineChart();
      case 'pie':
        return renderPieChart();
      case 'progress':
        return renderProgressChart();
      case 'area':
        // 区域图可以基于折线图实现
        return renderLineChart();
      default:
        return renderBarChart();
    }
  };

  return (
    <View style={[styles.container, style]}>
      {renderTitle()}
      <ScrollView horizontal showsHorizontalScrollIndicator={false}>
        <View style={[styles.chartContainer, { width, height }]}>
          {renderGrid()}
          {renderYLabels()}
          {renderChart()}
          {renderXLabels()}
        </View>
      </ScrollView>
      {renderLegend()}
    </View>
  );
};

const createStyles = (theme: any) => {
  return StyleSheet.create({
    container: {,
  backgroundColor: theme.colors.surface;
      borderRadius: theme.borderRadius.md;
      padding: theme.spacing.md
    ;},
    title: {,
  fontSize: theme.typography.fontSize.lg;
      fontWeight: theme.typography.fontWeight.semibold;
      color: theme.colors.onSurface;
      textAlign: 'center';
      marginBottom: theme.spacing.md
    ;},
    chartContainer: {,
  position: 'relative';
      backgroundColor: theme.colors.surface
    ;},
    gridLine: {,
  position: 'absolute';
      height: 1;
      backgroundColor: theme.colors.outline;
      opacity: 0.3
    ;},
    yLabel: {,
  position: 'absolute';
      left: 5;
      fontSize: theme.typography.fontSize.xs;
      color: theme.colors.onSurfaceVariant;
      textAlign: 'right';
      width: 30
    ;},
    xLabel: {,
  position: 'absolute';
      fontSize: theme.typography.fontSize.xs;
      color: theme.colors.onSurfaceVariant;
      textAlign: 'center';
      transform: [{ translateX: -20 ;}],
      width: 40
    ;},
    bar: {,
  position: 'absolute';
      borderRadius: theme.borderRadius.sm
    ;},
    valueLabel: {,
  position: 'absolute';
      fontSize: theme.typography.fontSize.xs;
      color: theme.colors.onSurface;
      textAlign: 'center';
      transform: [{ translateX: -15 ;}],
      width: 30
    ;},
    linePoint: {,
  position: 'absolute';
      width: 8;
      height: 8;
      borderRadius: 4;
      borderWidth: 2;
      borderColor: theme.colors.surface
    ;},
    line: {,
  position: 'absolute';
      height: 2;
      transformOrigin: 'left center'
    ;},
    pieSlice: {,
  position: 'absolute'
    ;},
    pieLabel: {,
  position: 'absolute';
      fontSize: theme.typography.fontSize.xs;
      color: theme.colors.onSurface;
      textAlign: 'center';
      transform: [{ translateX: -15 ;}, { translateY: -8 ;}],
      width: 30
    ;},
    progressBackground: {,
  position: 'absolute';
      backgroundColor: theme.colors.surfaceVariant;
      borderRadius: theme.borderRadius.sm
    ;},
    progressBar: {,
  position: 'absolute';
      borderRadius: theme.borderRadius.sm
    ;},
    progressLabel: {,
  position: 'absolute';
      fontSize: theme.typography.fontSize.sm;
      color: theme.colors.onSurface
    ;},
    progressValue: {,
  position: 'absolute';
      fontSize: theme.typography.fontSize.sm;
      color: theme.colors.onSurface
    ;},
    legend: {,
  flexDirection: 'row';
      flexWrap: 'wrap';
      justifyContent: 'center';
      marginTop: theme.spacing.md
    ;},
    legendItem: {,
  flexDirection: 'row';
      alignItems: 'center';
      marginRight: theme.spacing.md;
      marginBottom: theme.spacing.xs
    ;},
    legendColor: {,
  width: 12;
      height: 12;
      borderRadius: 6;
      marginRight: theme.spacing.xs
    ;},
    legendLabel: {,
  fontSize: theme.typography.fontSize.sm;
      color: theme.colors.onSurface
    ;}
  });
};

export default Chart;
