import React from 'react';
import { ActivityIndicator, StyleSheet, Text, View } from 'react-native';
import { useTheme } from '../../contexts/ThemeContext';

export interface PullToRefreshProps {
  /** 子组件 */
  children: React.ReactNode;
  /** 是否正在刷新 */
  refreshing?: boolean;
  /** 刷新回调 */
  onRefresh?: () => void;
  /** 自定义样式 */
  style?: any;
  /** 刷新中文本 */
  refreshingText?: string;
  /** 是否启用 */
  enabled?: boolean;
}

export const PullToRefresh: React.FC<PullToRefreshProps> = ({
  children,
  refreshing = false,
  onRefresh,
  style,
  refreshingText = '刷新中...',
  enabled = true,
}) => {
  const { currentTheme } = useTheme();
  const styles = createStyles(currentTheme);

  const renderIndicator = () => {
    return (
      <View style={styles.indicatorContainer}>
        <ActivityIndicator size="small" color={currentTheme.colors.primary} />
        <Text style={styles.indicatorText}>{refreshingText}</Text>
      </View>
    );
  };

  return (
    <View style={[styles.container, style]}>
      {refreshing && (
        <View style={styles.refreshIndicator}>{renderIndicator()}</View>
      )}

      <View style={styles.content}>{children}</View>
    </View>
  );
};

const createStyles = (theme: any) => {
  return StyleSheet.create({
    container: {,
  flex: 1,
    },
    refreshIndicator: {,
  height: 60,
      justifyContent: 'center',
      alignItems: 'center',
      backgroundColor: theme.colors.surface,
    },
    content: {,
  flex: 1,
      backgroundColor: theme.colors.background,
    },
    indicatorContainer: {,
  alignItems: 'center',
      justifyContent: 'center',
    },
    indicatorText: {,
  fontSize: 14,
      color: '#666',
      textAlign: 'center',
      marginTop: 8,
    },
  });
};

export default PullToRefresh;
