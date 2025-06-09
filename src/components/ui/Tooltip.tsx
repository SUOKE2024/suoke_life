import React, { useEffect, useRef, useState } from 'react';
import {
  Animated,
  Dimensions,
  StyleSheet,
  Text,
  TextStyle,
  TouchableOpacity,
  View,
  ViewStyle,
} from 'react-native';
import { useTheme } from '../../contexts/ThemeContext';

export interface TooltipProps {
  children: React.ReactNode;,
  content: string;
  placement?: 'top' | 'bottom' | 'left' | 'right';
  visible?: boolean;
  onVisibilityChange?: (visible: boolean) => void;
  backgroundColor?: string;
  textColor?: string;
  borderRadius?: number;
  maxWidth?: number;
  delay?: number;
  style?: ViewStyle;
  textStyle?: TextStyle;
  accessible?: boolean;
  accessibilityLabel?: string;
  testID?: string;
}

export const Tooltip: React.FC<TooltipProps> = ({
  children,
  content,
  placement = 'top',
  visible: controlledVisible,
  onVisibilityChange,
  backgroundColor,
  textColor,
  borderRadius = 8,
  maxWidth = 200,
  delay = 500,
  style,
  textStyle,
  accessible = true,
  accessibilityLabel,
  testID,
}) => {
  const { currentTheme } = useTheme();
  const [internalVisible, setInternalVisible] = useState(false);
  const [tooltipLayout, setTooltipLayout] = useState({ width: 0, height: 0 });
  const [childLayout, setChildLayout] = useState({
    x: 0,
    y: 0,
    width: 0,
    height: 0,
  });

  const fadeAnim = useRef(new Animated.Value(0)).current;
  const scaleAnim = useRef(new Animated.Value(0.8)).current;
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const childRef = useRef<View>(null);

  const isVisible =
    controlledVisible !== undefined ? controlledVisible : internalVisible;

  const showTooltip = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    timeoutRef.current = setTimeout() => {
      if (controlledVisible === undefined) {
        setInternalVisible(true);
      }
      onVisibilityChange?.(true);

      Animated.parallel([
        Animated.timing(fadeAnim, {
          toValue: 1,
          duration: 200,
          useNativeDriver: true,
        }),
        Animated.spring(scaleAnim, {
          toValue: 1,
          tension: 100,
          friction: 8,
          useNativeDriver: true,
        }),
      ]).start();
    }, delay);
  };

  const hideTooltip = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 0,
        duration: 150,
        useNativeDriver: true,
      }),
      Animated.timing(scaleAnim, {
        toValue: 0.8,
        duration: 150,
        useNativeDriver: true,
      }),
    ]).start() => {
      if (controlledVisible === undefined) {
        setInternalVisible(false);
      }
      onVisibilityChange?.(false);
    });
  };

  const measureChild = () => {
    if (childRef.current) {
      childRef.current.measure(x, y, width, height, pageX, pageY) => {
        setChildLayout({ x: pageX, y: pageY, width, height });
      });
    }
  };

  const getTooltipPosition = () => {
    const screenWidth = Dimensions.get('window').width;
    const screenHeight = Dimensions.get('window').height;
    const margin = 10;

    let x = 0;
    let y = 0;

    switch (placement) {
      case 'top':
        x = childLayout.x + (childLayout.width - tooltipLayout.width) / 2;
        y = childLayout.y - tooltipLayout.height - 8;
        break;
      case 'bottom':
        x = childLayout.x + (childLayout.width - tooltipLayout.width) / 2;
        y = childLayout.y + childLayout.height + 8;
        break;
      case 'left':
        x = childLayout.x - tooltipLayout.width - 8;
        y = childLayout.y + (childLayout.height - tooltipLayout.height) / 2;
        break;
      case 'right':
        x = childLayout.x + childLayout.width + 8;
        y = childLayout.y + (childLayout.height - tooltipLayout.height) / 2;
        break;
    }

    // 边界检查
    if (x < margin) x = margin;
    if (x + tooltipLayout.width > screenWidth - margin) {
      x = screenWidth - tooltipLayout.width - margin;
    }
    if (y < margin) y = margin;
    if (y + tooltipLayout.height > screenHeight - margin) {
      y = screenHeight - tooltipLayout.height - margin;
    }

    return { x, y };
  };

  const getArrowStyle = () => {
    const arrowSize = 6;
    const arrowStyle: ViewStyle = {,
  position: 'absolute',
      width: 0,
      height: 0,
      backgroundColor: 'transparent',
      borderStyle: 'solid',
    };

    switch (placement) {
      case 'top':
        return {
          ...arrowStyle,
          top: tooltipLayout.height - 1,
          left: tooltipLayout.width / 2 - arrowSize,
          borderLeftWidth: arrowSize,
          borderRightWidth: arrowSize,
          borderTopWidth: arrowSize,
          borderLeftColor: 'transparent',
          borderRightColor: 'transparent',
          borderTopColor: backgroundColor || currentTheme.colors.surface,
        };
      case 'bottom':
        return {
          ...arrowStyle,
          bottom: tooltipLayout.height - 1,
          left: tooltipLayout.width / 2 - arrowSize,
          borderLeftWidth: arrowSize,
          borderRightWidth: arrowSize,
          borderBottomWidth: arrowSize,
          borderLeftColor: 'transparent',
          borderRightColor: 'transparent',
          borderBottomColor: backgroundColor || currentTheme.colors.surface,
        };
      case 'left':
        return {
          ...arrowStyle,
          left: tooltipLayout.width - 1,
          top: tooltipLayout.height / 2 - arrowSize,
          borderTopWidth: arrowSize,
          borderBottomWidth: arrowSize,
          borderLeftWidth: arrowSize,
          borderTopColor: 'transparent',
          borderBottomColor: 'transparent',
          borderLeftColor: backgroundColor || currentTheme.colors.surface,
        };
      case 'right':
        return {
          ...arrowStyle,
          right: tooltipLayout.width - 1,
          top: tooltipLayout.height / 2 - arrowSize,
          borderTopWidth: arrowSize,
          borderBottomWidth: arrowSize,
          borderRightWidth: arrowSize,
          borderTopColor: 'transparent',
          borderBottomColor: 'transparent',
          borderRightColor: backgroundColor || currentTheme.colors.surface,
        };
    }
  };

  useEffect() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  const tooltipPosition = getTooltipPosition();

  const styles = StyleSheet.create({
    container: {,
  position: 'relative',
    },
    tooltip: {,
  position: 'absolute',
      backgroundColor: backgroundColor || currentTheme.colors.surface,
      borderRadius,
      paddingHorizontal: 12,
      paddingVertical: 8,
      maxWidth,
      shadowColor: currentTheme.colors.shadow,
      shadowOffset: {,
  width: 0,
        height: 2,
      },
      shadowOpacity: 0.25,
      shadowRadius: 3.84,
      elevation: 5,
      zIndex: 1000,
      left: tooltipPosition.x,
      top: tooltipPosition.y,
    },
    tooltipText: {,
  color: textColor || currentTheme.colors.onSurface,
      fontSize: 14,
      lineHeight: 20,
      textAlign: 'center',
      ...textStyle,
    },
  });

  return (
    <View style={[styles.container, style]}>
      <TouchableOpacity;
        ref={childRef}
        onPressIn={() => {
          measureChild();
          showTooltip();
        }}
        onPressOut={hideTooltip}
        onLayout={measureChild}
        accessible={accessible}
        accessibilityLabel={accessibilityLabel || content}
        accessibilityRole="button"
        accessibilityHint="长按显示提示信息"
        testID={testID}
        activeOpacity={1}
      >
        {children}
      </TouchableOpacity>

      {isVisible && (
        <Animated.View;
          style={[
            styles.tooltip,
            {
              opacity: fadeAnim,
              transform: [{ scale: scaleAnim }],
            },
          ]}
          onLayout={(event) => {
            const { width, height } = event.nativeEvent.layout;
            setTooltipLayout({ width, height });
          }}
          pointerEvents="none"
        >
          <Text style={styles.tooltipText}>{content}</Text>
          <View style={getArrowStyle()} />
        </Animated.View>
      )}
    </View>
  );
};

export default Tooltip;
