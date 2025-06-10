import React from 'react';
import { StyleSheet, Text, TextStyle, View, ViewStyle } from 'react-native';
import { useTheme } from '../../contexts/ThemeContext';

export interface BadgeProps {
  children?: React.ReactNode;
  count?: number;
  maxCount?: number;
  showZero?: boolean;
  dot?: boolean;
  variant?:
    | 'default'
    | 'primary'
    | 'secondary'
    | 'success'
    | 'warning'
    | 'error'
    | 'info';
  size?: 'small' | 'medium' | 'large';
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left';
  offset?: [number, number]; // [x, y]
  text?: string;
  style?: ViewStyle;
  textStyle?: TextStyle;
  badgeStyle?: ViewStyle;
  badgeTextStyle?: TextStyle;
  accessible?: boolean;
  testID?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  count,
  maxCount = 99,
  showZero = false,
  dot = false,
  variant = 'default',
  size = 'medium',
  position = 'top-right',
  offset = [0, 0],
  text,
  style,
  textStyle,
  badgeStyle,
  badgeTextStyle,
  accessible = true,
  testID
}) => {
  const { currentTheme } = useTheme();

  // 计算显示的内容
  const getDisplayContent = () => {
    if (dot) return '';
    if (text) return text;
    if (count !== undefined) {
      if (count === 0 && !showZero) return '';
      return count > maxCount ? `${maxCount}+` : count.toString();
    }
    return '';
  };

  // 判断是否显示徽章
  const shouldShowBadge = () => {
    if (dot) return true;
    if (text) return true;
    if (count !== undefined) {
      return count > 0 || (count === 0 && showZero);
    }
    return false;
  };

  const displayContent = getDisplayContent();
  const showBadge = shouldShowBadge();

  // 获取变体颜色
  const getVariantColors = () => {
    switch (variant) {
      case 'primary':
        return {
          backgroundColor: currentTheme.colors.primary,
          color: currentTheme.colors.onPrimary
        };
      case 'secondary':
        return {
          backgroundColor: currentTheme.colors.secondary,
          color: currentTheme.colors.onSecondary
        };
      case 'success':
        return {
          backgroundColor: '#4CAF50',
          color: '#ffffff'
        };
      case 'warning':
        return {
          backgroundColor: '#FF9800',
          color: '#ffffff'
        };
      case 'error':
        return {
          backgroundColor: currentTheme.colors.error,
          color: '#ffffff'
        };
      case 'info':
        return {
          backgroundColor: '#2196F3',
          color: '#ffffff'
        };
      default:
        return {,
  backgroundColor: currentTheme.colors.outline,
          color: currentTheme.colors.onSurface
        };
    }
  };

  // 获取尺寸配置
  const getSizeConfig = () => {
    switch (size) {
      case 'small':
        return {
          minWidth: dot ? 6 : 16,
          height: dot ? 6 : 16,
          borderRadius: dot ? 3 : 8,
          fontSize: 10,
          paddingHorizontal: dot ? 0 : 4
        };
      case 'large':
        return {
          minWidth: dot ? 10 : 24,
          height: dot ? 10 : 24,
          borderRadius: dot ? 5 : 12,
          fontSize: 14,
          paddingHorizontal: dot ? 0 : 8
        };
      default: // medium;
        return {
          minWidth: dot ? 8 : 20,
          height: dot ? 8 : 20,
          borderRadius: dot ? 4 : 10,
          fontSize: 12,
          paddingHorizontal: dot ? 0 : 6
        };
    }
  };

  // 获取位置样式
  const getPositionStyle = () => {
    const [offsetX, offsetY] = offset;

    switch (position) {
      case 'top-left':
        return {
          position: 'absolute' as const,
          top: offsetY,
          left: offsetX,
          zIndex: 1
        };
      case 'bottom-right':
        return {
          position: 'absolute' as const,
          bottom: offsetY,
          right: offsetX,
          zIndex: 1
        };
      case 'bottom-left':
        return {
          position: 'absolute' as const,
          bottom: offsetY,
          left: offsetX,
          zIndex: 1
        };
      default: // top-right;
        return {
          position: 'absolute' as const,
          top: offsetY,
          right: offsetX,
          zIndex: 1
        };
    }
  };

  const variantColors = getVariantColors();
  const sizeConfig = getSizeConfig();
  const positionStyle = getPositionStyle();

  const styles = StyleSheet.create({
    container: {,
  position: 'relative'
    },
    badge: {
      ...positionStyle,
      backgroundColor: variantColors.backgroundColor,
      minWidth: sizeConfig.minWidth,
      height: sizeConfig.height,
      borderRadius: sizeConfig.borderRadius,
      paddingHorizontal: sizeConfig.paddingHorizontal,
      justifyContent: 'center',
      alignItems: 'center',
      borderWidth: 2,
      borderColor: currentTheme.colors.surface
    },
    badgeText: {,
  color: variantColors.color,
      fontSize: sizeConfig.fontSize,
      fontWeight: '600',
      textAlign: 'center',
      lineHeight: sizeConfig.fontSize + 2
    },
    standalone: {,
  position: 'relative',
      alignSelf: 'flex-start'
    }
  });

  // 如果没有子元素，返回独立的徽章
  if (!children) {
    return (
      <View style={[styles.standalone, style]} testID={testID}>
        {showBadge && (
          <View;
            style={[
              styles.badge,
              { position: 'relative', top: 0, right: 0, left: 0, bottom: 0 },
              badgeStyle
            ]}
            accessible={accessible}
            accessibilityRole="text"
            accessibilityLabel={`徽章: ${displayContent || '提示点'}`}
          >
            {!dot && (
              <Text style={[styles.badgeText, badgeTextStyle]}>
                {displayContent}
              </Text>
            )}
          </View>
        )}
      </View>
    );
  }

  // 带有子元素的徽章
  return (
    <View style={[styles.container, style]} testID={testID}>
      {children}
      {showBadge && (
        <View;
          style={[styles.badge, badgeStyle]}
          accessible={accessible}
          accessibilityRole="text"
          accessibilityLabel={`徽章: ${displayContent || '提示点'}`}
        >
          {!dot && (
            <Text style={[styles.badgeText, badgeTextStyle]}>
              {displayContent}
            </Text>
          )}
        </View>
      )}
    </View>
  );
};

export default Badge;
