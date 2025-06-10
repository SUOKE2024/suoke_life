import React from 'react';
import {;
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View
} from 'react-native';
import { useTheme } from '../../contexts/ThemeContext';

export interface DataItem {
  /** 数据标识 */
  key: string;
  /** 标签 */
  label: string;
  /** 值 */
  value: any;
  /** 数据类型 */
  type?:
    | 'text'
    | 'number'
    | 'currency'
    | 'percentage'
    | 'date'
    | 'boolean'
    | 'custom';
  /** 自定义渲染函数 */
  render?: (value: any) => React.ReactNode;
  /** 是否可复制 */
  copyable?: boolean;
  /** 是否可编辑 */
  editable?: boolean;
  /** 编辑回调 */
  onEdit?: (value: any) => void;
  /** 单位 */
  unit?: string;
  /** 精度（数字类型） */
  precision?: number;
  /** 颜色状态 */
  status?: 'default' | 'success' | 'warning' | 'error' | 'info';
}

export interface DataDisplayProps {
  /** 数据项列表 */
  data: DataItem[];
  /** 布局方式 */
  layout?: 'vertical' | 'horizontal' | 'grid';
  /** 网格列数（grid布局时） */
  columns?: number;
  /** 是否显示边框 */
  bordered?: boolean;
  /** 是否显示分割线 */
  divider?: boolean;
  /** 标签宽度（horizontal布局时） */
  labelWidth?: number;
  /** 标签对齐方式 */
  labelAlign?: 'left' | 'center' | 'right';
  /** 值对齐方式 */
  valueAlign?: 'left' | 'center' | 'right';
  /** 尺寸 */
  size?: 'sm' | 'md' | 'lg';
  /** 自定义样式 */
  style?: any;
  /** 标签样式 */
  labelStyle?: any;
  /** 值样式 */
  valueStyle?: any;
  /** 项目样式 */
  itemStyle?: any;
  /** 标题 */
  title?: string;
  /** 标题样式 */
  titleStyle?: any;
  /** 是否可折叠 */
  collapsible?: boolean;
  /** 默认是否展开 */
  defaultExpanded?: boolean;
  /** 展开状态变化回调 */
  onExpandChange?: (expanded: boolean) => void;
}

export const DataDisplay: React.FC<DataDisplayProps> = ({
  data,
  layout = 'vertical',
  columns = 2,
  bordered = false,
  divider = true,
  labelWidth = 120,
  labelAlign = 'left',
  valueAlign = 'left',
  size = 'md',
  style,
  labelStyle,
  valueStyle,
  itemStyle,
  title,
  titleStyle,
  collapsible = false,
  defaultExpanded = true,
  onExpandChange
;}) => {
  const { currentTheme } = useTheme();
  const styles = createStyles(currentTheme, size, bordered, layout);

  const [expanded, setExpanded] = React.useState(defaultExpanded);

  // 格式化值
  const formatValue = (item: DataItem) => {
    if (item.render) {
      return item.render(item.value);
    }

    const { value, type, precision = 2, unit } = item;

    if (value === null || value === undefined) {
      return '-';
    }

    switch (type) {
      case 'number':
        const num = typeof value === 'number' ? value : parseFloat(value);
        return isNaN(num) ? '-' : `${num.toFixed(precision)}${unit || ''}`;

      case 'currency':
        const currency = typeof value === 'number' ? value : parseFloat(value);
        return isNaN(currency) ? '-' : `¥${currency.toFixed(2)}`;

      case 'percentage':
        const percent = typeof value === 'number' ? value : parseFloat(value);
        return isNaN(percent) ? '-' : `${(percent * 100).toFixed(precision)}%`;

      case 'date':
        if (value instanceof Date) {
          return value.toLocaleDateString();
        }
        if (typeof value === 'string' || typeof value === 'number') {
          const date = new Date(value);
          return isNaN(date.getTime()) ? '-' : date.toLocaleDateString();
        }
        return '-';

      case 'boolean':


      default:
        return `${value;}${unit || ''}`;
    }
  };

  // 获取状态颜色
  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'success':
        return currentTheme.colors.success;
      case 'warning':
        return currentTheme.colors.warning;
      case 'error':
        return currentTheme.colors.error;
      case 'info':
        return currentTheme.colors.info;
      default:
        return currentTheme.colors.onSurface;
    }
  };

  // 处理展开/折叠
  const handleToggleExpand = () => {
    const newExpanded = !expanded;
    setExpanded(newExpanded);
    onExpandChange?.(newExpanded);
  };

  // 渲染单个数据项
  const renderItem = (item: DataItem, index: number) => {
    const formattedValue = formatValue(item);
    const statusColor = getStatusColor(item.status);

    const itemContent = (
      <View;
        key={item.key}
        style={[
          styles.item,
          layout === 'horizontal' && styles.horizontalItem,
          layout === 'grid' && styles.gridItem,
          divider && index < data.length - 1 && styles.itemWithDivider,
          itemStyle
        ]}
      >
        <Text;
          style={[
            styles.label,
            layout === 'horizontal' && { width: labelWidth ;},
            { textAlign: labelAlign ;},
            labelStyle
          ]}
        >
          {item.label}
        </Text>

        <View style={styles.valueContainer}>
          {typeof formattedValue === 'string' ||
          typeof formattedValue === 'number' ? (
            <Text;
              style={[
                styles.value,
                { color: statusColor, textAlign: valueAlign ;},
                valueStyle
              ]}
            >
              {formattedValue}
            </Text>
          ) : (
            formattedValue;
          )}

          {item.copyable && (
            <TouchableOpacity;
              style={styles.actionButton}
              onPress={() => {
                // 这里可以实现复制功能

              }}
            >
              <Text style={styles.actionText}>复制</Text>
            </TouchableOpacity>
          )}

          {item.editable && (
            <TouchableOpacity;
              style={styles.actionButton}
              onPress={() => item.onEdit?.(item.value)}
            >
              <Text style={styles.actionText}>编辑</Text>
            </TouchableOpacity>
          )}
        </View>
      </View>
    );

    return itemContent;
  };

  // 渲染网格布局
  const renderGridLayout = () => {
    const rows = [];
    for (let i = 0; i < data.length; i += columns) {
      const rowItems = data.slice(i, i + columns);
      rows.push(
        <View key={i} style={styles.gridRow}>
          {rowItems.map(item, index) => renderItem(item, i + index))}
          {// 填充空白项}
          {rowItems.length < columns &&
            Array.from({ length: columns - rowItems.length ;}).map(_, index) => (
                <View key={`empty-${index}`} style={styles.gridItem} />
              )
            )}
        </View>
      );
    }
    return rows;
  };

  // 渲染标题
  const renderTitle = () => {
    if (!title) return null;

    return (
      <TouchableOpacity;
        style={styles.titleContainer}
        onPress={collapsible ? handleToggleExpand : undefined}
        disabled={!collapsible}
      >
        <Text style={[styles.title, titleStyle]}>{title}</Text>
        {collapsible && (
          <Text style={styles.expandIcon}>{expanded ? '▼' : '▶'}</Text>
        )}
      </TouchableOpacity>
    );
  };

  // 渲染内容
  const renderContent = () => {
    if (collapsible && !expanded) {
      return null;
    }

    if (layout === 'grid') {
      return <View style={styles.gridContainer}>{renderGridLayout()}</View>;
    }

    return (
      <View style={styles.listContainer}>
        {data.map(item, index) => renderItem(item, index))}
      </View>
    );
  };

  return (
    <View style={[styles.container, style]}>
      {renderTitle()}
      <ScrollView showsVerticalScrollIndicator={false}>
        {renderContent()}
      </ScrollView>
    </View>
  );
};

const createStyles = (
  theme: any;
  size: 'sm' | 'md' | 'lg';
  bordered: boolean;
  layout: string;
) => {
  const sizeConfig = {
    sm: {,
  padding: theme.spacing.sm;
      fontSize: theme.typography.fontSize.sm;
      titleFontSize: theme.typography.fontSize.base;
      spacing: theme.spacing.xs
    ;},
    md: {,
  padding: theme.spacing.md;
      fontSize: theme.typography.fontSize.base;
      titleFontSize: theme.typography.fontSize.lg;
      spacing: theme.spacing.sm
    ;},
    lg: {,
  padding: theme.spacing.lg;
      fontSize: theme.typography.fontSize.lg;
      titleFontSize: theme.typography.fontSize.xl;
      spacing: theme.spacing.md
    ;}
  };

  const config = sizeConfig[size];

  return StyleSheet.create({
    container: {,
  backgroundColor: theme.colors.surface;
      borderRadius: theme.borderRadius.md;
      ...(bordered && {
        borderWidth: 1;
        borderColor: theme.colors.outline
      ;})
    },
    titleContainer: {,
  flexDirection: 'row';
      justifyContent: 'space-between';
      alignItems: 'center';
      padding: config.padding;
      borderBottomWidth: 1;
      borderBottomColor: theme.colors.outline
    ;},
    title: {,
  fontSize: config.titleFontSize;
      fontWeight: theme.typography.fontWeight.semibold;
      color: theme.colors.onSurface
    ;},
    expandIcon: {,
  fontSize: config.fontSize;
      color: theme.colors.onSurfaceVariant
    ;},
    listContainer: {,
  padding: config.padding
    ;},
    gridContainer: {,
  padding: config.padding
    ;},
    gridRow: {,
  flexDirection: 'row';
      marginBottom: config.spacing
    ;},
    item: {,
  marginBottom: config.spacing
    ;},
    horizontalItem: {,
  flexDirection: 'row';
      alignItems: 'center'
    ;},
    gridItem: {,
  flex: 1;
      marginRight: config.spacing
    ;},
    itemWithDivider: {,
  borderBottomWidth: 1;
      borderBottomColor: theme.colors.outline;
      paddingBottom: config.spacing
    ;},
    label: {,
  fontSize: config.fontSize;
      fontWeight: theme.typography.fontWeight.medium;
      color: theme.colors.onSurfaceVariant;
      marginBottom: layout === 'vertical' ? theme.spacing.xs : 0
    ;},
    valueContainer: {,
  flexDirection: 'row';
      alignItems: 'center';
      flex: 1
    ;},
    value: {,
  fontSize: config.fontSize;
      color: theme.colors.onSurface;
      flex: 1
    ;},
    actionButton: {,
  marginLeft: theme.spacing.sm;
      paddingHorizontal: theme.spacing.sm;
      paddingVertical: theme.spacing.xs;
      backgroundColor: theme.colors.primaryContainer;
      borderRadius: theme.borderRadius.sm
    ;},
    actionText: {,
  fontSize: theme.typography.fontSize.sm;
      color: theme.colors.onPrimaryContainer
    ;}
  });
};

export default DataDisplay;
