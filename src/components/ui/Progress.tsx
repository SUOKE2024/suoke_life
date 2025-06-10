import React, { useEffect, useRef } from 'react';
import {;
  Animated,
  StyleSheet,
  Text,
  TextStyle,
  View,
  ViewStyle
} from 'react-native';
import { useTheme } from '../../contexts/ThemeContext';

export interface ProgressProps {
  value: number; // 0-100;
  max?: number;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'success' | 'warning' | 'error';
  showLabel?: boolean;
  label?: string;
  animated?: boolean;
  striped?: boolean;
  indeterminate?: boolean;
  color?: string;
  backgroundColor?: string;
  style?: ViewStyle;
  labelStyle?: TextStyle;
  accessible?: boolean;
  accessibilityLabel?: string;
  testID?: string;
}

export const Progress: React.FC<ProgressProps> = ({
  value,
  max = 100,
  size = 'md',
  variant = 'default',
  showLabel = false,
  label,
  animated = true,
  striped = false,
  indeterminate = false,
  color,
  backgroundColor,
  style,
  labelStyle,
  accessible = true,
  accessibilityLabel,
  testID
}) => {
  const { currentTheme } = useTheme();
  const progressAnim = useRef(new Animated.Value(0)).current;
  const indeterminateAnim = useRef(new Animated.Value(0)).current;

  const normalizedValue = Math.min(Math.max(value, 0), max);
  const percentage = (normalizedValue / max) * 100;

  useEffect() => {
    if (indeterminate) {
      // 不确定进度动画
      Animated.loop(
        Animated.sequence([
          Animated.timing(indeterminateAnim, {
            toValue: 1,
            duration: 1000,
            useNativeDriver: false
          }),
          Animated.timing(indeterminateAnim, {
            toValue: 0,
            duration: 1000,
            useNativeDriver: false
          })
        ])
      ).start();
    } else {
      indeterminateAnim.setValue(0);
      if (animated) {
        Animated.timing(progressAnim, {
          toValue: percentage,
          duration: 500,
          useNativeDriver: false
        }).start();
      } else {
        progressAnim.setValue(percentage);
      }
    }
  }, [
    value,
    max,
    animated,
    indeterminate,
    percentage,
    progressAnim,
    indeterminateAnim
  ]);

  const getSizeStyles = () => {
    switch (size) {
      case 'sm':
        return { height: 4, borderRadius: 2 };
      case 'lg':
        return { height: 12, borderRadius: 6 };
      default:
        return { height: 8, borderRadius: 4 };
    }
  };

  const getVariantColor = () => {
    if (color) return color;

    switch (variant) {
      case 'success':
        return currentTheme.colors.success;
      case 'warning':
        return currentTheme.colors.warning;
      case 'error':
        return currentTheme.colors.error;
      default:
        return currentTheme.colors.primary;
    }
  };

  const sizeStyles = getSizeStyles();
  const progressColor = getVariantColor();

  const styles = StyleSheet.create({
    container: {,
  width: '100%'
    },
    progressBar: {,
  width: '100%',
      backgroundColor: backgroundColor || currentTheme.colors.outline,
      borderRadius: sizeStyles.borderRadius,
      height: sizeStyles.height,
      overflow: 'hidden'
    },
    progressFill: {,
  height: '100%',
      backgroundColor: progressColor,
      borderRadius: sizeStyles.borderRadius
    },
    stripedFill: {
      // React Native不支持backgroundImage，这里可以用其他方式实现条纹效果
      opacity: 0.8
    },
    label: {,
  fontSize: 14,
      color: currentTheme.colors.onSurface,
      textAlign: 'center',
      marginTop: 4,
      ...labelStyle
    }
  });

  const renderProgressBar = () => {
    if (indeterminate) {
      const translateX = indeterminateAnim.interpolate({
        inputRange: [0, 1],
        outputRange: ['-100%', '100%']
      });

      return (
        <View style={styles.progressBar}>
          <Animated.View;
            style={[
              styles.progressFill,
              {
                width: '30%',
                transform: [{ translateX }]
              }
            ]}
          />
        </View>
      );
    }

    const width = progressAnim.interpolate({
      inputRange: [0, 100],
      outputRange: ['0%', '100%'],
      extrapolate: 'clamp'
    });

    return (
      <View style={styles.progressBar}>
        <Animated.View;
          style={[
            styles.progressFill,
            striped && styles.stripedFill,
            { width }
          ]}
        />
      </View>
    );
  };

  const getAccessibilityProps = () => ({
    accessible,
    accessibilityRole: 'progressbar' as const,
    accessibilityLabel: accessibilityLabel || `进度 ${percentage.toFixed(0)}%`,
    accessibilityValue: {,
  min: 0,
      max,
      now: normalizedValue
    }
  });

  return (
    <View;
      style={[styles.container, style]}
      testID={testID}
      {...getAccessibilityProps()}
    >
      {renderProgressBar()}
      {showLabel && (
        <Text style={styles.label}>{label || `${percentage.toFixed(0)}%`}</Text>
      )}
    </View>
  );
};

export default Progress;
