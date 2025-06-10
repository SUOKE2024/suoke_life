import React, { useCallback, useState } from 'react';
import {;
  Modal,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View
} from 'react-native';
import { useTheme } from '../../contexts/ThemeContext';

export interface FilterOption {
  /** 选项标识 */
  key: string;
  /** 选项标签 */
  label: string;
  /** 选项值 */
  value: any;
  /** 是否选中 */
  selected?: boolean;
  /** 子选项 */
  children?: FilterOption[];
  /** 选项类型 */
  type?: 'checkbox' | 'radio' | 'range' | 'date' | 'custom';
  /** 自定义渲染 */
  render?: (
    option: FilterOption,
    onSelect: (value: any) => void;
  ) => React.ReactNode;
}

export interface FilterGroup {
  /** 分组标识 */
  key: string;
  /** 分组标题 */
  title: string;
  /** 分组选项 */
  options: FilterOption[];
  /** 选择类型 */
  type?: 'single' | 'multiple';
  /** 是否可折叠 */
  collapsible?: boolean;
  /** 默认展开状态 */
  defaultExpanded?: boolean;
}

export interface SearchFilterProps {
  /** 搜索占位符 */
  searchPlaceholder?: string;
  /** 搜索值 */
  searchValue?: string;
  /** 搜索变化回调 */
  onSearchChange?: (value: string) => void;
  /** 过滤分组 */
  filterGroups?: FilterGroup[];
  /** 过滤变化回调 */
  onFilterChange?: (filters: Record<string, any>) => void;
  /** 是否显示搜索框 */
  showSearch?: boolean;
  /** 是否显示过滤器 */
  showFilters?: boolean;
  /** 是否显示清除按钮 */
  showClear?: boolean;
  /** 是否显示应用按钮 */
  showApply?: boolean;
  /** 清除回调 */
  onClear?: () => void;
  /** 应用回调 */
  onApply?: (searchValue: string, filters: Record<string, any>) => void;
  /** 自定义样式 */
  style?: any;
  /** 搜索框样式 */
  searchStyle?: any;
  /** 过滤器样式 */
  filterStyle?: any;
  /** 尺寸 */
  size?: 'sm' | 'md' | 'lg';
  /** 布局方向 */
  layout?: 'vertical' | 'horizontal';
  /** 是否使用模态框 */
  modal?: boolean;
  /** 模态框可见性 */
  modalVisible?: boolean;
  /** 模态框关闭回调 */
  onModalClose?: () => void;
}

export const SearchFilter: React.FC<SearchFilterProps> = ({
  searchPlaceholder = '搜索...',
  searchValue = '',
  onSearchChange,
  filterGroups = [],
  onFilterChange,
  showSearch = true,
  showFilters = true,
  showClear = true,
  showApply = false,
  onClear,
  onApply,
  style,
  searchStyle,
  filterStyle,
  size = 'md',
  layout = 'vertical',
  modal = false,
  modalVisible = false,
  onModalClose
}) => {
  const { currentTheme } = useTheme();
  const styles = createStyles(currentTheme, size, layout);

  const [localSearchValue, setLocalSearchValue] = useState(searchValue);
  const [localFilters, setLocalFilters] = useState<Record<string, any>>({});
  const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>(
    {}
  );

  // 初始化展开状态
  React.useEffect() => {
    const initialExpanded: Record<string, boolean> = {};
    filterGroups.forEach(group) => {
      initialExpanded[group.key] = group.defaultExpanded !== false;
    });
    setExpandedGroups(initialExpanded);
  }, [filterGroups]);

  // 处理搜索变化
  const handleSearchChange = useCallback(value: string) => {
      setLocalSearchValue(value);
      if (!showApply) {
        onSearchChange?.(value);
      }
    },
    [onSearchChange, showApply]
  );

  // 处理过滤器选择
  const handleFilterSelect = useCallback(groupKey: string, optionKey: string, value: any) => {
      const group = filterGroups.find(g) => g.key === groupKey);
      if (!group) return;

      const newFilters = { ...localFilters };

      if (group.type === 'single') {
        newFilters[groupKey] = value;
      } else {
        if (!newFilters[groupKey]) {
          newFilters[groupKey] = [];
        }
        const currentValues = newFilters[groupKey] as any[];
        const index = currentValues.findIndex(v) => v === value);

        if (index >= 0) {
          currentValues.splice(index, 1);
        } else {
          currentValues.push(value);
        }
      }

      setLocalFilters(newFilters);

      if (!showApply) {
        onFilterChange?.(newFilters);
      }
    },
    [filterGroups, localFilters, onFilterChange, showApply]
  );

  // 切换分组展开状态
  const toggleGroupExpanded = useCallback(groupKey: string) => {
    setExpandedGroups(prev) => ({
      ...prev,
      [groupKey]: !prev[groupKey]
    }));
  }, []);

  // 清除所有过滤器
  const handleClear = useCallback() => {
    setLocalSearchValue('');
    setLocalFilters({});
    onClear?.();
    onSearchChange?.('');
    onFilterChange?.({});
  }, [onClear, onSearchChange, onFilterChange]);

  // 应用过滤器
  const handleApply = useCallback() => {
    onApply?.(localSearchValue, localFilters);
    onModalClose?.();
  }, [localSearchValue, localFilters, onApply, onModalClose]);

  // 检查选项是否选中
  const isOptionSelected = useCallback(groupKey: string, optionValue: any) => {
      const group = filterGroups.find(g) => g.key === groupKey);
      if (!group) return false;

      const filterValue = localFilters[groupKey];

      if (group.type === 'single') {
        return filterValue === optionValue;
      } else {
        return Array.isArray(filterValue) && filterValue.includes(optionValue);
      }
    },
    [filterGroups, localFilters]
  );

  // 渲染搜索框
  const renderSearchBox = () => {
    if (!showSearch) return null;

    return (
      <View style={[styles.searchContainer, searchStyle]}>
        <TextInput;
          style={styles.searchInput}
          placeholder={searchPlaceholder}
          placeholderTextColor={currentTheme.colors.onSurfaceVariant}
          value={localSearchValue}
          onChangeText={handleSearchChange}
          clearButtonMode="while-editing"
        />
      </View>
    );
  };

  // 渲染过滤选项
  const renderFilterOption = (group: FilterGroup, option: FilterOption) => {
    const isSelected = isOptionSelected(group.key, option.value);

    if (option.render) {
      return option.render(option, (value) =>
        handleFilterSelect(group.key, option.key, value)
      );
    }

    return (
      <TouchableOpacity;
        key={option.key}
        style={[styles.filterOption, isSelected && styles.selectedFilterOption]}
        onPress={() => handleFilterSelect(group.key, option.key, option.value)}
      >
        <View style={styles.optionContent}>
          <View;
            style={[
              styles.checkbox,
              group.type === 'single' && styles.radioButton,
              isSelected && styles.checkedCheckbox
            ]}
          >
            {isSelected && (
              <Text style={styles.checkmark}>
                {group.type === 'single' ? '●' : '✓'}
              </Text>
            )}
          </View>
          <Text;
            style={[
              styles.optionLabel,
              isSelected && styles.selectedOptionLabel
            ]}
          >
            {option.label}
          </Text>
        </View>
      </TouchableOpacity>
    );
  };

  // 渲染过滤分组
  const renderFilterGroup = (group: FilterGroup) => {
    const isExpanded = expandedGroups[group.key];

    return (
      <View key={group.key} style={styles.filterGroup}>
        <TouchableOpacity;
          style={styles.groupHeader}
          onPress={() => group.collapsible && toggleGroupExpanded(group.key)}
          disabled={!group.collapsible}
        >
          <Text style={styles.groupTitle}>{group.title}</Text>
          {group.collapsible && (
            <Text style={styles.expandIcon}>{isExpanded ? '▼' : '▶'}</Text>
          )}
        </TouchableOpacity>

        {(!group.collapsible || isExpanded) && (
          <View style={styles.groupOptions}>
            {group.options.map(option) => renderFilterOption(group, option))}
          </View>
        )}
      </View>
    );
  };

  // 渲染过滤器
  const renderFilters = () => {
    if (!showFilters || filterGroups.length === 0) return null;

    return (
      <View style={[styles.filtersContainer, filterStyle]}>
        {filterGroups.map(renderFilterGroup)}
      </View>
    );
  };

  // 渲染操作按钮
  const renderActions = () => {
    if (!showClear && !showApply) return null;

    return (
      <View style={styles.actionsContainer}>
        {showClear && (
          <TouchableOpacity style={styles.clearButton} onPress={handleClear}>
            <Text style={styles.clearButtonText}>清除</Text>
          </TouchableOpacity>
        )}
        {showApply && (
          <TouchableOpacity style={styles.applyButton} onPress={handleApply}>
            <Text style={styles.applyButtonText}>应用</Text>
          </TouchableOpacity>
        )}
      </View>
    );
  };

  // 渲染内容
  const renderContent = () => (
    <View style={[styles.container, style]}>
      {renderSearchBox()}
      {renderFilters()}
      {renderActions()}
    </View>
  );

  // 如果使用模态框
  if (modal) {
    return (
      <Modal;
        visible={modalVisible}
        animationType="slide"
        presentationStyle="pageSheet"
        onRequestClose={onModalClose}
      >
        <View style={styles.modalContainer}>
          <View style={styles.modalHeader}>
            <TouchableOpacity onPress={onModalClose}>
              <Text style={styles.modalCloseText}>取消</Text>
            </TouchableOpacity>
            <Text style={styles.modalTitle}>筛选</Text>
            <TouchableOpacity onPress={handleApply}>
              <Text style={styles.modalApplyText}>确定</Text>
            </TouchableOpacity>
          </View>
          <ScrollView style={styles.modalContent}>{renderContent()}</ScrollView>
        </View>
      </Modal>
    );
  }

  return (
    <ScrollView showsVerticalScrollIndicator={false}>
      {renderContent()}
    </ScrollView>
  );
};

const createStyles = (theme: any, size: 'sm' | 'md' | 'lg', layout: string) => {
  const sizeConfig = {
    sm: {,
  padding: theme.spacing.sm,
      fontSize: theme.typography.fontSize.sm,
      inputHeight: 36,
      spacing: theme.spacing.xs
    },
    md: {,
  padding: theme.spacing.md,
      fontSize: theme.typography.fontSize.base,
      inputHeight: 44,
      spacing: theme.spacing.sm
    },
    lg: {,
  padding: theme.spacing.lg,
      fontSize: theme.typography.fontSize.lg,
      inputHeight: 52,
      spacing: theme.spacing.md
    }
  };

  const config = sizeConfig[size];

  return StyleSheet.create({
    container: {,
  backgroundColor: theme.colors.surface
    },
    searchContainer: {,
  marginBottom: config.spacing
    },
    searchInput: {,
  height: config.inputHeight,
      backgroundColor: theme.colors.surfaceVariant,
      borderRadius: theme.borderRadius.md,
      paddingHorizontal: theme.spacing.md,
      fontSize: config.fontSize,
      color: theme.colors.onSurface,
      borderWidth: 1,
      borderColor: theme.colors.outline
    },
    filtersContainer: {,
  marginBottom: config.spacing
    },
    filterGroup: {,
  marginBottom: config.spacing
    },
    groupHeader: {,
  flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      paddingVertical: config.spacing,
      borderBottomWidth: 1,
      borderBottomColor: theme.colors.outline
    },
    groupTitle: {,
  fontSize: config.fontSize,
      fontWeight: theme.typography.fontWeight.semibold,
      color: theme.colors.onSurface
    },
    expandIcon: {,
  fontSize: config.fontSize,
      color: theme.colors.onSurfaceVariant
    },
    groupOptions: {,
  paddingTop: config.spacing
    },
    filterOption: {,
  paddingVertical: config.spacing,
      paddingHorizontal: theme.spacing.sm,
      borderRadius: theme.borderRadius.sm,
      marginBottom: theme.spacing.xs
    },
    selectedFilterOption: {,
  backgroundColor: theme.colors.primaryContainer
    },
    optionContent: {,
  flexDirection: 'row',
      alignItems: 'center'
    },
    checkbox: {,
  width: 20,
      height: 20,
      borderWidth: 2,
      borderColor: theme.colors.outline,
      borderRadius: 4,
      alignItems: 'center',
      justifyContent: 'center',
      marginRight: theme.spacing.sm
    },
    radioButton: {,
  borderRadius: 10
    },
    checkedCheckbox: {,
  backgroundColor: theme.colors.primary,
      borderColor: theme.colors.primary
    },
    checkmark: {,
  color: theme.colors.onPrimary,
      fontSize: 12,
      fontWeight: theme.typography.fontWeight.bold
    },
    optionLabel: {,
  fontSize: config.fontSize,
      color: theme.colors.onSurface,
      flex: 1
    },
    selectedOptionLabel: {,
  color: theme.colors.onPrimaryContainer,
      fontWeight: theme.typography.fontWeight.medium
    },
    actionsContainer: {,
  flexDirection: 'row',
      justifyContent: 'space-between',
      paddingTop: config.spacing,
      borderTopWidth: 1,
      borderTopColor: theme.colors.outline
    },
    clearButton: {,
  flex: 1,
      paddingVertical: theme.spacing.sm,
      paddingHorizontal: theme.spacing.md,
      backgroundColor: theme.colors.surfaceVariant,
      borderRadius: theme.borderRadius.md,
      alignItems: 'center',
      marginRight: theme.spacing.sm
    },
    clearButtonText: {,
  fontSize: config.fontSize,
      color: theme.colors.onSurfaceVariant,
      fontWeight: theme.typography.fontWeight.medium
    },
    applyButton: {,
  flex: 1,
      paddingVertical: theme.spacing.sm,
      paddingHorizontal: theme.spacing.md,
      backgroundColor: theme.colors.primary,
      borderRadius: theme.borderRadius.md,
      alignItems: 'center',
      marginLeft: theme.spacing.sm
    },
    applyButtonText: {,
  fontSize: config.fontSize,
      color: theme.colors.onPrimary,
      fontWeight: theme.typography.fontWeight.medium
    },
    modalContainer: {,
  flex: 1,
      backgroundColor: theme.colors.surface
    },
    modalHeader: {,
  flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: theme.spacing.md,
      borderBottomWidth: 1,
      borderBottomColor: theme.colors.outline
    },
    modalTitle: {,
  fontSize: theme.typography.fontSize.lg,
      fontWeight: theme.typography.fontWeight.semibold,
      color: theme.colors.onSurface
    },
    modalCloseText: {,
  fontSize: config.fontSize,
      color: theme.colors.onSurfaceVariant
    },
    modalApplyText: {,
  fontSize: config.fontSize,
      color: theme.colors.primary,
      fontWeight: theme.typography.fontWeight.medium
    },
    modalContent: {,
  flex: 1,
      padding: theme.spacing.md
    }
  });
};

export default SearchFilter;
