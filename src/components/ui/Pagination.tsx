import React from 'react';
import {
    StyleSheet,
    Text,
    TouchableOpacity,
    View
} from 'react-native';
import { useTheme } from '../../contexts/ThemeContext';

export interface PaginationProps {
  /** 当前页码 */
  current: number;
  /** 总页数 */
  total: number;
  /** 页码变化回调 */
  onChange: (page: number) => void;
  /** 每页显示的页码数量 */
  pageSize?: number;
  /** 是否显示总数 */
  showTotal?: boolean;
  /** 总数据量 */
  totalItems?: number;
  /** 是否显示上一页/下一页按钮 */
  showPrevNext?: boolean;
  /** 上一页文本 */
  prevText?: string;
  /** 下一页文本 */
  nextText?: string;
  /** 分页样式 */
  variant?: 'default' | 'simple' | 'minimal';
  /** 自定义样式 */
  style?: any;
  /** 是否禁用 */
  disabled?: boolean;
  /** 尺寸 */
  size?: 'sm' | 'md' | 'lg';
}

export const Pagination: React.FC<PaginationProps> = ({
  current,
  total,
  onChange,
  pageSize = 5,
  showTotal = false,
  totalItems,
  showPrevNext = true,
  prevText = '上一页',
  nextText = '下一页',
  variant = 'default',
  style,
  disabled = false,
  size = 'md',
}) => {
  const { currentTheme } = useTheme();
  const styles = createStyles(currentTheme, size);

  const handlePageChange = (page: number) => {
    if (disabled || page === current || page < 1 || page > total) {
      return;
    }
    onChange(page);
  };

  const handlePrevious = () => {
    handlePageChange(current - 1);
  };

  const handleNext = () => {
    handlePageChange(current + 1);
  };

  if (total <= 1) {
    return null;
  }

  return (
    <View style={[styles.container, style]}>
      {showTotal && totalItems && (
        <Text style={styles.totalText}>
          共 {totalItems} 条
        </Text>
      )}

      <View style={styles.paginationContainer}>
        {showPrevNext && (
          <TouchableOpacity
            style={[
              styles.navButton,
              current <= 1 && styles.disabledNavButton,
            ]}
            onPress={handlePrevious}
            disabled={disabled || current <= 1}
          >
            <Text style={[
              styles.navButtonText,
              (disabled || current <= 1) && styles.disabledNavButtonText,
            ]}>
              ‹
            </Text>
          </TouchableOpacity>
        )}

        <View style={styles.pageInfo}>
          <Text style={styles.pageInfoText}>
            {current} / {total}
          </Text>
        </View>

        {showPrevNext && (
          <TouchableOpacity
            style={[
              styles.navButton,
              current >= total && styles.disabledNavButton,
            ]}
            onPress={handleNext}
            disabled={disabled || current >= total}
          >
            <Text style={[
              styles.navButtonText,
              (disabled || current >= total) && styles.disabledNavButtonText,
            ]}>
              ›
            </Text>
          </TouchableOpacity>
        )}
      </View>
    </View>
  );
};

const createStyles = (theme: any, size: 'sm' | 'md' | 'lg') => {
  const sizeConfig = {
    sm: {
      buttonSize: 32,
      fontSize: 14,
      spacing: 4,
    },
    md: {
      buttonSize: 40,
      fontSize: 16,
      spacing: 8,
    },
    lg: {
      buttonSize: 48,
      fontSize: 18,
      spacing: 12,
    },
  };

  const config = sizeConfig[size];

  return StyleSheet.create({
    container: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'center',
      paddingVertical: 16,
    },
    paginationContainer: {
      flexDirection: 'row',
      alignItems: 'center',
    },
    navButton: {
      width: config.buttonSize,
      height: config.buttonSize,
      borderRadius: 4,
      backgroundColor: theme.colors.surface,
      borderWidth: 1,
      borderColor: theme.colors.outline,
      justifyContent: 'center',
      alignItems: 'center',
      marginHorizontal: config.spacing,
    },
    disabledNavButton: {
      opacity: 0.5,
    },
    navButtonText: {
      fontSize: config.fontSize,
      color: theme.colors.onSurface,
      fontWeight: '500',
    },
    disabledNavButtonText: {
      color: '#999',
    },
    totalText: {
      fontSize: 14,
      color: '#666',
      marginRight: 16,
    },
    pageInfo: {
      paddingHorizontal: 16,
    },
    pageInfoText: {
      fontSize: config.fontSize,
      color: theme.colors.onSurface,
      fontWeight: '500',
    },
  });
};

export default Pagination; 