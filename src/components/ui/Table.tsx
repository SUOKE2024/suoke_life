import React, { useMemo, useState } from 'react';
import {
    FlatList,
    ScrollView,
    StyleSheet,
    Text,
    TouchableOpacity,
    View
} from 'react-native';
import { useTheme } from '../../contexts/ThemeContext';

export interface TableColumn {
  /** 列标识 */
  key: string;
  /** 列标题 */
  title: string;
  /** 列宽度 */
  width?: number;
  /** 是否可排序 */
  sortable?: boolean;
  /** 对齐方式 */
  align?: 'left' | 'center' | 'right';
  /** 自定义渲染函数 */
  render?: (value: any, record: any, index: number) => React.ReactNode;
  /** 是否固定列 */
  fixed?: 'left' | 'right';
}

export interface TableProps {
  /** 表格列配置 */
  columns: TableColumn[];
  /** 表格数据 */
  dataSource: any[];
  /** 行键值字段 */
  rowKey?: string;
  /** 是否显示表头 */
  showHeader?: boolean;
  /** 是否显示边框 */
  bordered?: boolean;
  /** 是否显示斑马纹 */
  striped?: boolean;
  /** 表格尺寸 */
  size?: 'sm' | 'md' | 'lg';
  /** 自定义样式 */
  style?: any;
  /** 表头样式 */
  headerStyle?: any;
  /** 行样式 */
  rowStyle?: any;
  /** 单元格样式 */
  cellStyle?: any;
  /** 是否可选择行 */
  rowSelection?: {
    type?: 'checkbox' | 'radio';
    selectedRowKeys?: string[];
    onChange?: (selectedRowKeys: string[], selectedRows: any[]) => void;
    onSelect?: (record: any, selected: boolean, selectedRows: any[]) => void;
    onSelectAll?: (selected: boolean, selectedRows: any[], changeRows: any[]) => void;
  };
  /** 排序配置 */
  sortConfig?: {
    field?: string;
    order?: 'asc' | 'desc';
    onChange?: (field: string, order: 'asc' | 'desc') => void;
  };
  /** 行点击事件 */
  onRowPress?: (record: any, index: number) => void;
  /** 空数据提示 */
  emptyText?: string;
  /** 是否正在加载 */
  loading?: boolean;
  /** 分页配置 */
  pagination?: {
    current: number;
    pageSize: number;
    total: number;
    onChange: (page: number, pageSize: number) => void;
  };
}

export const Table: React.FC<TableProps> = ({
  columns,
  dataSource,
  rowKey = 'id',
  showHeader = true,
  bordered = false,
  striped = false,
  size = 'md',
  style,
  headerStyle,
  rowStyle,
  cellStyle,
  rowSelection,
  sortConfig,
  onRowPress,
  emptyText = '暂无数据',
  loading = false,
  pagination,
}) => {
  const { currentTheme } = useTheme();
  const styles = createStyles(currentTheme, size, bordered, striped);

  const [selectedKeys, setSelectedKeys] = useState<string[]>(
    rowSelection?.selectedRowKeys || []
  );

  // 计算列宽
  const totalFixedWidth = useMemo(() => {
    return columns.reduce((total, col) => {
      return total + (col.width || 0);
    }, 0);
  }, [columns]);

  const flexColumns = useMemo(() => {
    return columns.filter(col => !col.width);
  }, [columns]);

  const getColumnWidth = (column: TableColumn) => {
    if (column.width) {
      return column.width;
    }
    // 平均分配剩余宽度
    return flexColumns.length > 0 ? undefined : 100;
  };

  // 处理排序
  const handleSort = (column: TableColumn) => {
    if (!column.sortable || !sortConfig?.onChange) return;

    const currentField = sortConfig.field;
    const currentOrder = sortConfig.order;

    let newOrder: 'asc' | 'desc' = 'asc';
    if (currentField === column.key) {
      newOrder = currentOrder === 'asc' ? 'desc' : 'asc';
    }

    sortConfig.onChange(column.key, newOrder);
  };

  // 处理行选择
  const handleRowSelect = (record: any, selected: boolean) => {
    if (!rowSelection) return;

    const key = record[rowKey];
    let newSelectedKeys: string[];

    if (rowSelection.type === 'radio') {
      newSelectedKeys = selected ? [key] : [];
    } else {
      if (selected) {
        newSelectedKeys = [...selectedKeys, key];
      } else {
        newSelectedKeys = selectedKeys.filter(k => k !== key);
      }
    }

    setSelectedKeys(newSelectedKeys);
    
    const selectedRows = dataSource.filter(item => 
      newSelectedKeys.includes(item[rowKey])
    );

    rowSelection.onChange?.(newSelectedKeys, selectedRows);
    rowSelection.onSelect?.(record, selected, selectedRows);
  };

  // 处理全选
  const handleSelectAll = (selected: boolean) => {
    if (!rowSelection) return;

    const allKeys = dataSource.map(item => item[rowKey]);
    const newSelectedKeys = selected ? allKeys : [];
    
    setSelectedKeys(newSelectedKeys);
    
    const selectedRows = selected ? dataSource : [];
    const changeRows = selected ? dataSource : dataSource.filter(item => 
      selectedKeys.includes(item[rowKey])
    );

    rowSelection.onChange?.(newSelectedKeys, selectedRows);
    rowSelection.onSelectAll?.(selected, selectedRows, changeRows);
  };

  // 渲染表头
  const renderHeader = () => {
    if (!showHeader) return null;

    return (
      <View style={[styles.headerRow, headerStyle]}>
        {rowSelection && (
          <View style={[styles.headerCell, styles.selectionCell]}>
            {rowSelection.type !== 'radio' && (
              <TouchableOpacity
                style={styles.checkbox}
                onPress={() => handleSelectAll(selectedKeys.length !== dataSource.length)}
              >
                <Text style={styles.checkboxText}>
                  {selectedKeys.length === dataSource.length ? '☑' : '☐'}
                </Text>
              </TouchableOpacity>
            )}
          </View>
        )}
        
        {columns.map((column, index) => (
          <TouchableOpacity
            key={column.key}
            style={[
              styles.headerCell,
              { width: getColumnWidth(column) },
              column.align && { alignItems: column.align === 'center' ? 'center' : column.align === 'right' ? 'flex-end' : 'flex-start' },
            ]}
            onPress={() => handleSort(column)}
            disabled={!column.sortable}
          >
            <Text style={styles.headerText}>{column.title}</Text>
            {column.sortable && (
              <Text style={styles.sortIcon}>
                {sortConfig?.field === column.key
                  ? sortConfig.order === 'asc' ? '↑' : '↓'
                  : '↕'}
              </Text>
            )}
          </TouchableOpacity>
        ))}
      </View>
    );
  };

  // 渲染单元格
  const renderCell = (column: TableColumn, record: any, index: number) => {
    const value = record[column.key];
    const content = column.render ? column.render(value, record, index) : value;

    return (
      <View
        key={column.key}
        style={[
          styles.cell,
          { width: getColumnWidth(column) },
          column.align && { alignItems: column.align === 'center' ? 'center' : column.align === 'right' ? 'flex-end' : 'flex-start' },
          cellStyle,
        ]}
      >
        {typeof content === 'string' || typeof content === 'number' ? (
          <Text style={styles.cellText}>{content}</Text>
        ) : (
          content
        )}
      </View>
    );
  };

  // 渲染行
  const renderRow = ({ item, index }: { item: any; index: number }) => {
    const key = item[rowKey];
    const isSelected = selectedKeys.includes(key);
    const isEven = index % 2 === 0;

    return (
      <TouchableOpacity
        style={[
          styles.row,
          striped && !isEven && styles.stripedRow,
          isSelected && styles.selectedRow,
          rowStyle,
        ]}
        onPress={() => onRowPress?.(item, index)}
        disabled={!onRowPress}
      >
        {rowSelection && (
          <View style={[styles.cell, styles.selectionCell]}>
            <TouchableOpacity
              style={styles.checkbox}
              onPress={() => handleRowSelect(item, !isSelected)}
            >
              <Text style={styles.checkboxText}>
                {isSelected ? (rowSelection.type === 'radio' ? '●' : '☑') : (rowSelection.type === 'radio' ? '○' : '☐')}
              </Text>
            </TouchableOpacity>
          </View>
        )}
        
        {columns.map(column => renderCell(column, item, index))}
      </TouchableOpacity>
    );
  };

  // 渲染空状态
  const renderEmpty = () => (
    <View style={styles.emptyContainer}>
      <Text style={styles.emptyText}>{emptyText}</Text>
    </View>
  );

  if (loading) {
    return (
      <View style={[styles.container, style]}>
        <Text style={styles.loadingText}>加载中...</Text>
      </View>
    );
  }

  return (
    <View style={[styles.container, style]}>
      <ScrollView horizontal showsHorizontalScrollIndicator={false}>
        <View style={styles.tableContainer}>
          {renderHeader()}
          
          {dataSource.length > 0 ? (
            <FlatList
              data={dataSource}
              renderItem={renderRow}
              keyExtractor={(item) => item[rowKey]}
              showsVerticalScrollIndicator={false}
            />
          ) : (
            renderEmpty()
          )}
        </View>
      </ScrollView>
    </View>
  );
};

const createStyles = (
  theme: any,
  size: 'sm' | 'md' | 'lg',
  bordered: boolean,
  striped: boolean
) => {
  const sizeConfig = {
    sm: {
      cellPadding: theme.spacing.xs,
      fontSize: theme.typography.fontSize.sm,
      minHeight: 32,
    },
    md: {
      cellPadding: theme.spacing.sm,
      fontSize: theme.typography.fontSize.base,
      minHeight: 40,
    },
    lg: {
      cellPadding: theme.spacing.md,
      fontSize: theme.typography.fontSize.lg,
      minHeight: 48,
    },
  };

  const config = sizeConfig[size];

  return StyleSheet.create({
    container: {
      backgroundColor: theme.colors.surface,
      borderRadius: theme.borderRadius.md,
      overflow: 'hidden',
    },
    tableContainer: {
      minWidth: '100%',
    },
    headerRow: {
      flexDirection: 'row',
      backgroundColor: theme.colors.surfaceVariant,
      borderBottomWidth: bordered ? 1 : 0,
      borderBottomColor: theme.colors.outline,
      minHeight: config.minHeight,
    },
    headerCell: {
      flex: 1,
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'space-between',
      paddingHorizontal: config.cellPadding,
      paddingVertical: config.cellPadding,
      borderRightWidth: bordered ? 1 : 0,
      borderRightColor: theme.colors.outline,
      minHeight: config.minHeight,
    },
    headerText: {
      fontSize: config.fontSize,
      fontWeight: theme.typography.fontWeight.semibold,
      color: theme.colors.onSurface,
    },
    sortIcon: {
      fontSize: config.fontSize,
      color: theme.colors.onSurfaceVariant,
      marginLeft: theme.spacing.xs,
    },
    row: {
      flexDirection: 'row',
      borderBottomWidth: bordered ? 1 : 0,
      borderBottomColor: theme.colors.outline,
      minHeight: config.minHeight,
    },
    stripedRow: {
      backgroundColor: theme.colors.surfaceVariant,
    },
    selectedRow: {
      backgroundColor: theme.colors.primaryContainer,
    },
    cell: {
      flex: 1,
      justifyContent: 'center',
      paddingHorizontal: config.cellPadding,
      paddingVertical: config.cellPadding,
      borderRightWidth: bordered ? 1 : 0,
      borderRightColor: theme.colors.outline,
      minHeight: config.minHeight,
    },
    cellText: {
      fontSize: config.fontSize,
      color: theme.colors.onSurface,
    },
    selectionCell: {
      width: 50,
      alignItems: 'center',
    },
    checkbox: {
      padding: theme.spacing.xs,
    },
    checkboxText: {
      fontSize: config.fontSize,
      color: theme.colors.primary,
    },
    emptyContainer: {
      padding: theme.spacing.xl,
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: 120,
    },
    emptyText: {
      fontSize: config.fontSize,
      color: theme.colors.onSurfaceVariant,
    },
    loadingText: {
      fontSize: config.fontSize,
      color: theme.colors.onSurfaceVariant,
      textAlign: 'center',
      padding: theme.spacing.xl,
    },
  });
};

export default Table;