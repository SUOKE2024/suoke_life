import React, { useEffect, useRef, useState } from 'react';
import {;
  Animated,
  Dimensions,
  Modal,
  StyleSheet,
  TouchableOpacity,
  View,
  ViewStyle
} from 'react-native';
import { useTheme } from '../../contexts/ThemeContext';

export interface PopoverProps {
  children: React.ReactNode;,
  content: React.ReactNode;
  placement?: 'top' | 'bottom' | 'left' | 'right' | 'auto';
  trigger?: 'press' | 'longPress' | 'hover';
  visible?: boolean;
  onVisibilityChange?: (visible: boolean) => void;
  backgroundColor?: string;
  borderRadius?: number;
  showArrow?: boolean;
  offset?: number;
  style?: ViewStyle;
  contentStyle?: ViewStyle;
  accessible?: boolean;
  accessibilityLabel?: string;
  testID?: string;
}

export const Popover: React.FC<PopoverProps> = ({
  children,
  content,
  placement = 'auto',
  trigger = 'press',
  visible: controlledVisible,
  onVisibilityChange,
  backgroundColor,
  borderRadius = 8,
  showArrow = true,
  offset = 8,
  style,
  contentStyle,
  accessible = true,
  accessibilityLabel,
  testID
}) => {
  const { currentTheme } = useTheme();
  const [internalVisible, setInternalVisible] = useState(false);
  const [triggerLayout, setTriggerLayout] = useState({
    x: 0,
    y: 0,
    width: 0,
    height: 0
  });
  const [contentLayout, setContentLayout] = useState({ width: 0, height: 0 });
  const [actualPlacement, setActualPlacement] = useState<
    'top' | 'bottom' | 'left' | 'right'
  >('bottom');

  const fadeAnim = useRef(new Animated.Value(0)).current;
  const scaleAnim = useRef(new Animated.Value(0.8)).current;
  const triggerRef = useRef<View>(null);

  const isVisible =
    controlledVisible !== undefined ? controlledVisible : internalVisible;

  const showPopover = () => {
    if (controlledVisible === undefined) {
      setInternalVisible(true);
    }
    onVisibilityChange?.(true);

    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 200,
        useNativeDriver: true
      }),
      Animated.spring(scaleAnim, {
        toValue: 1,
        tension: 100,
        friction: 8,
        useNativeDriver: true
      })
    ]).start();
  };

  const hidePopover = () => {
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 0,
        duration: 150,
        useNativeDriver: true
      }),
      Animated.timing(scaleAnim, {
        toValue: 0.8,
        duration: 150,
        useNativeDriver: true
      })
    ]).start() => {
      if (controlledVisible === undefined) {
        setInternalVisible(false);
      }
      onVisibilityChange?.(false);
    });
  };

  const measureTrigger = () => {
    if (triggerRef.current) {
      triggerRef.current.measure(x, y, width, height, pageX, pageY) => {
        setTriggerLayout({ x: pageX, y: pageY, width, height });
      });
    }
  };

  const calculatePlacement = (): 'top' | 'bottom' | 'left' | 'right' => {
    if (placement !== 'auto') return placement;

    const screenWidth = Dimensions.get('window').width;
    const screenHeight = Dimensions.get('window').height;
    const margin = 20;

    // 检查各个方向的可用空间
    const spaceTop = triggerLayout.y;
    const spaceBottom = screenHeight - (triggerLayout.y + triggerLayout.height);
    const spaceLeft = triggerLayout.x;
    const spaceRight = screenWidth - (triggerLayout.x + triggerLayout.width);

    // 优先选择空间最大的方向
    const spaces = [
      { direction: 'bottom' as const, space: spaceBottom },
      { direction: 'top' as const, space: spaceTop },
      { direction: 'right' as const, space: spaceRight },
      { direction: 'left' as const, space: spaceLeft }
    ];

    return spaces.sort(a, b) => b.space - a.space)[0].direction;
  };

  const getPopoverPosition = () => {
    const screenWidth = Dimensions.get('window').width;
    const screenHeight = Dimensions.get('window').height;
    const margin = 10;

    let x = 0;
    let y = 0;

    switch (actualPlacement) {
      case 'top':
        x = triggerLayout.x + (triggerLayout.width - contentLayout.width) / 2;
        y = triggerLayout.y - contentLayout.height - offset;
        break;
      case 'bottom':
        x = triggerLayout.x + (triggerLayout.width - contentLayout.width) / 2;
        y = triggerLayout.y + triggerLayout.height + offset;
        break;
      case 'left':
        x = triggerLayout.x - contentLayout.width - offset;
        y = triggerLayout.y + (triggerLayout.height - contentLayout.height) / 2;
        break;
      case 'right':
        x = triggerLayout.x + triggerLayout.width + offset;
        y = triggerLayout.y + (triggerLayout.height - contentLayout.height) / 2;
        break;
    }

    // 边界检查
    if (x < margin) x = margin;
    if (x + contentLayout.width > screenWidth - margin) {
      x = screenWidth - contentLayout.width - margin;
    }
    if (y < margin) y = margin;
    if (y + contentLayout.height > screenHeight - margin) {
      y = screenHeight - contentLayout.height - margin;
    }

    return { x, y };
  };

  const getArrowStyle = () => {
    if (!showArrow) return null;

    const arrowSize = 8;
    const arrowStyle: ViewStyle = {,
  position: 'absolute',
      width: 0,
      height: 0,
      backgroundColor: 'transparent',
      borderStyle: 'solid'
    };

    switch (actualPlacement) {
      case 'top':
        return {
          ...arrowStyle,
          top: contentLayout.height - 1,
          left: contentLayout.width / 2 - arrowSize,
          borderLeftWidth: arrowSize,
          borderRightWidth: arrowSize,
          borderTopWidth: arrowSize,
          borderLeftColor: 'transparent',
          borderRightColor: 'transparent',
          borderTopColor: backgroundColor || currentTheme.colors.surface
        };
      case 'bottom':
        return {
          ...arrowStyle,
          bottom: contentLayout.height - 1,
          left: contentLayout.width / 2 - arrowSize,
          borderLeftWidth: arrowSize,
          borderRightWidth: arrowSize,
          borderBottomWidth: arrowSize,
          borderLeftColor: 'transparent',
          borderRightColor: 'transparent',
          borderBottomColor: backgroundColor || currentTheme.colors.surface
        };
      case 'left':
        return {
          ...arrowStyle,
          left: contentLayout.width - 1,
          top: contentLayout.height / 2 - arrowSize,
          borderTopWidth: arrowSize,
          borderBottomWidth: arrowSize,
          borderLeftWidth: arrowSize,
          borderTopColor: 'transparent',
          borderBottomColor: 'transparent',
          borderLeftColor: backgroundColor || currentTheme.colors.surface
        };
      case 'right':
        return {
          ...arrowStyle,
          right: contentLayout.width - 1,
          top: contentLayout.height / 2 - arrowSize,
          borderTopWidth: arrowSize,
          borderBottomWidth: arrowSize,
          borderRightWidth: arrowSize,
          borderTopColor: 'transparent',
          borderBottomColor: 'transparent',
          borderRightColor: backgroundColor || currentTheme.colors.surface
        };
    }
  };

  useEffect() => {
    if (isVisible && triggerLayout.width > 0) {
      setActualPlacement(calculatePlacement());
    }
  }, [isVisible, triggerLayout, contentLayout, placement]);

  const popoverPosition = getPopoverPosition();

  const styles = StyleSheet.create({
    trigger: {
      // 触发器样式
    },
    overlay: {,
  flex: 1,
      backgroundColor: 'transparent'
    },
    popover: {,
  position: 'absolute',
      backgroundColor: backgroundColor || currentTheme.colors.surface,
      borderRadius,
      padding: 12,
      shadowColor: currentTheme.colors.shadow,
      shadowOffset: {,
  width: 0,
        height: 4
      },
      shadowOpacity: 0.3,
      shadowRadius: 8,
      elevation: 8,
      left: popoverPosition.x,
      top: popoverPosition.y,
      ...contentStyle
    }
  });

  const handleTriggerPress = () => {
    if (trigger === 'press') {
      measureTrigger();
      if (isVisible) {
        hidePopover();
      } else {
        showPopover();
      }
    }
  };

  const handleTriggerLongPress = () => {
    if (trigger === 'longPress') {
      measureTrigger();
      if (!isVisible) {
        showPopover();
      }
    }
  };

  return (
    <>
      <TouchableOpacity;
        ref={triggerRef}
        style={[styles.trigger, style]}
        onPress={handleTriggerPress}
        onLongPress={handleTriggerLongPress}
        onLayout={measureTrigger}
        accessible={accessible}
        accessibilityLabel={accessibilityLabel}
        accessibilityRole="button"
        accessibilityHint="点击显示弹出内容"
        testID={testID}
        activeOpacity={1}
      >
        {children}
      </TouchableOpacity>

      <Modal;
        visible={isVisible}
        transparent;
        animationType="none"
        onRequestClose={hidePopover}
      >
        <TouchableOpacity;
          style={styles.overlay}
          activeOpacity={1}
          onPress={hidePopover}
        >
          <Animated.View;
            style={[
              styles.popover,
              {
                opacity: fadeAnim,
                transform: [{ scale: scaleAnim }]
              }
            ]}
            onLayout={(event) => {
              const { width, height } = event.nativeEvent.layout;
              setContentLayout({ width, height });
            }}
          >
            <TouchableOpacity activeOpacity={1} onPress={() => {}}>
              {content}
            </TouchableOpacity>
            {showArrow && <View style={getArrowStyle()} />}
          </Animated.View>
        </TouchableOpacity>
      </Modal>
    </>
  );
};

export default Popover;
