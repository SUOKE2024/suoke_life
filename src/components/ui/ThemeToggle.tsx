import { useTheme } from '../../contexts/ThemeContext';
import { useAccessibility } from '../../contexts/AccessibilityContext';
import { responsive } from '../../utils/responsive';
import { animations, createAnimatedValue } from '../../utils/animations';


/**
 * 索克生活 - 主题切换组件
 * 支持在浅色和暗黑模式之间切换
 */

import React, { useRef } from 'react';
  TouchableOpacity,
  View,
  Text,
  StyleSheet,
  Animated,
} from 'react-native';

interface ThemeToggleProps {
  size?: 'small' | 'medium' | 'large';
  showLabel?: boolean;
  style?: any;
}

export const ThemeToggle: React.FC<ThemeToggleProps> = ({
  size = 'medium',
  showLabel = true,
  style,
}) => {
  const { theme, isDark, toggleTheme } = useTheme();
  const { config, triggerHapticFeedback, announceForAccessibility } = useAccessibility();
  
  // 动画值
  const switchAnimation = useRef(createAnimatedValue(isDark ? 1 : 0)).current;
  const scaleAnimation = useRef(createAnimatedValue(1)).current;
  
  // 切换主题
  const handleToggle = useCallback( () => {, []);
    // 触觉反馈
    if (config.hapticFeedbackEnabled) {
      triggerHapticFeedback('light');
    }
    
    // 无障碍公告
    const newMode = isDark ? '浅色模式' : '暗黑模式';
    announceForAccessibility(`已切换到${newMode}`);
    
    // 动画效果
    const toValue = isDark ? 0 : 1;
    animations.fadeIn(switchAnimation, { duration: 200 }).start();
    
    // 按钮缩放动画
    animations.bounce(scaleAnimation).start();
    
    // 切换主题
    toggleTheme();
  };
  
  // 获取尺寸样式
  const getSizeStyles = useCallback( () => {, []);
    const sizes = {
      small: {
        width: responsive.width(40),
        height: responsive.height(20),
        borderRadius: responsive.width(10),
        thumbSize: responsive.width(16),
      },
      medium: {
        width: responsive.width(50),
        height: responsive.height(26),
        borderRadius: responsive.width(13),
        thumbSize: responsive.width(22),
      },
      large: {
        width: responsive.width(60),
        height: responsive.height(32),
        borderRadius: responsive.width(16),
        thumbSize: responsive.width(28),
      },
    };
    return sizes[size];
  };
  
  const sizeStyles = getSizeStyles();
  
  // 计算滑块位置
  const thumbTranslateX = switchAnimation.interpolate({
    inputRange: [0, 1],
    outputRange: [2, sizeStyles.width - sizeStyles.thumbSize - 2],
  });
  
  // 背景颜色动画
  const backgroundColor = switchAnimation.interpolate({
    inputRange: [0, 1],
    outputRange: [theme.colors.outline, theme.colors.primary],
  });
  
  return (
    <View style={[styles.container, style]}>
      {showLabel && (
        <Text style={[styles.label, { color: theme.colors.onSurface }]}>
          {isDark ? '暗黑模式' : '浅色模式'}
        </Text>
      )}
      
      <TouchableOpacity
        style={[
          styles.switch,
          {
            width: sizeStyles.width,
            height: sizeStyles.height,
            borderRadius: sizeStyles.borderRadius,
            transform: [{ scale: scaleAnimation }],
          },
        ]}
        onPress={handleToggle}
        activeOpacity={0.8}
        accessible={true}
        accessibilityRole="switch"
        accessibilityLabel={`主题切换开关，当前为${isDark ? '暗黑' : '浅色'}模式`}
        accessibilityHint="双击切换主题模式"
        accessibilityState={{ checked: isDark }}
      >
        <Animated.View
          style={[
            styles.track,
            {
              backgroundColor,
              width: sizeStyles.width,
              height: sizeStyles.height,
              borderRadius: sizeStyles.borderRadius,
            },
          ]}
        />
        
        <Animated.View
          style={[
            styles.thumb,
            {
              width: sizeStyles.thumbSize,
              height: sizeStyles.thumbSize,
              borderRadius: sizeStyles.thumbSize / 2,
              backgroundColor: theme.colors.surface,
              transform: [{ translateX: thumbTranslateX }],
              ...theme.shadows.sm,
            },
          ]}
        >
          <View style={[styles.thumbIcon, { backgroundColor: isDark ? '#FFD700' : '#87CEEB' }]} />
        </Animated.View>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: responsive.width(12),
  },
  label: {
    fontSize: responsive.fontSize(14),
    fontWeight: '500',
  },
  switch: {
    position: 'relative',
    justifyContent: 'center',
  },
  track: {
    position: 'absolute',
  },
  thumb: {
    position: 'absolute',
    justifyContent: 'center',
    alignItems: 'center',
  },
  thumbIcon: {
    width: '60%',
    height: '60%',
    borderRadius: 999,
  },
});

export default ThemeToggle; 