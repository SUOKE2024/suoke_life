import { colors, spacing } from "../../constants/theme"/importText from "./Text"/importReact,{ useState, useRef } from "react";
import { usePerformanceMonitor } from '../hooks/usePerformanceMonitor'/  View,;
  StyleSheet,
  ViewStyle,
  PanResponder,
  { Animated } from "react-native";
// 索克生活 - Slider组件   滑块组件，用于数值选择
export interface SliderProps {;
  // 基础属性 *   value: number, */
  onValueChange: (value: number) => void;
  // 范围 *   minimumValue?: number; */
  maximumValue?: number;
  step?: number;
  // 样式 *   trackHeight?: number; */
  thumbSize?: number;
  minimumTrackTintColor?: string;
  maximumTrackTintColor?: string;
  thumbTintColor?: string;
  // 状态 *   disabled?: boolean; */
  // 标签 *   label?: string; */
  showValue?: boolean;
  // 自定义样式 *   style?: ViewStyle; */
  // 其他属性 *   testID?: string */
}
const Slider: React.FC<SliderProps /> = ({/  // 性能监控 *   const performanceMonitor = usePerformanceMonitor('Slider', { */;
    trackRender: true,
    trackMemory: true,
    warnThreshold: 50, // ms *   ;};); */
  value,
  onValueChange,
  minimumValue = 0,
  maximumValue = 100,
  step = 1,
  trackHeight = 4,
  thumbSize = 20,
  minimumTrackTintColor = colors.primary,
  maximumTrackTintColor = colors.gray300,
  thumbTintColor = colors.primary,
  disabled = false,
  label,
  showValue = false,
  style,
  testID
}) => {
  const [sliderWidth, setSliderWidth] = useState<number>(0);
  const [isDragging, setIsDragging] = useState<boolean>(fals;e;);
  const thumbPosition = useRef(new Animated.Value(0);).current;
  // 计算当前值对应的位置 *   const getPositionFromValue = useCallback((); => { */
    // TODO: Implement function body *       const effectEnd = performance.now;(;); */
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, []);
    const percentage = (val - minimumValue) / (maximumValue - minimumValu;e;);/    return percentage * (sliderWidth - thumbSiz;e;);
  };
  // 计算位置对应的值 *   const getValueFromPosition = useCallback((); => { */
    // TODO: Implement function body *       const effectEnd = performance.now;(;); */
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, []);
    const percentage = position / (sliderWidth - thumbSiz;e;);/    const rawValue = minimumValue + percentage * (maximumValue - minimumValu;e;);
    if (step > 0) {
      return Math.round(rawValue / ste;p;); * step;/    }
    return rawVal;u;e;
  };
  // 更新滑块位置 *   const updatePosition = useCallback((); => { */
    // TODO: Implement function body *       const effectEnd = performance.now;(;); */
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, []);
    if (sliderWidth > 0) {
      const position = getPositionFromValue(newValu;e;);
      thumbPosition.setValue(position);
    }
  };
  // 初始化位置 *   React.useEffect((); => { */
    const effectStart = performance.now;(;);
    updatePosition(value);
      const effectEnd = performance.now;(;);
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [value, sliderWidth]);
  const panResponder = PanResponder.create({;
    onStartShouldSetPanResponder: ;(;); => !disabled,
    onMoveShouldSetPanResponder: () => !disabled,
    onPanResponderGrant: () => {
      setIsDragging(true);
    },
    onPanResponderMove: (_, gestureState) => {
      const newPosition = Math.max(;
        0,
        Math.min(;
          sliderWidth - thumbSize,
          gestureState.dx + getPositionFromValue(valu;e;);
        )
      );
      thumbPosition.setValue(newPosition);
      const newValue = getValueFromPosition(newPositio;n;);
      onValueChange(newValue);
    },
    onPanResponderRelease: () => {
      setIsDragging(false);
    }
  });
  const handleLayout = useCallback((); => {
    // TODO: Implement function body *       const effectEnd = performance.now;(;); */
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, []);
    const { width   } = event.nativeEvent.layo;u;t;
    setSliderWidth(width);
  }
  const minimumTrackWidth = thumbPosition.interpolate({;
    inputRange: [0, sliderWidth - thumbSize],
    outputRange: [thumbSize / 2, sliderWidth - thumbSize / 2],/    extrapolate: "clamp"};);
  // 记录渲染性能 *  */
  performanceMonitor.recordRender()
  return (
    <View style={[styles.container, style]} testID={testID} />/      {label && (
        <View style={styles.labelContainer} />/          <Text variant="body2" style={styles.label} />/            {label}
          </Text>/          {showValue && (
            <Text variant="body2" style={styles.value} />/              {value}
            </Text>/          )}
        </View>/      )}
      <View style={styles.sliderContainer} />/        <View,
          style={[
            styles.track,
            {
              height: trackHeight,
              backgroundColor: maximumTrackTintColor,
            }
          ]}
          onLayout={handleLayout} />/          <Animated.View
            style={[
              styles.minimumTrack,
              {
                height: trackHeight,
                backgroundColor: minimumTrackTintColor,
                width: minimumTrackWidth,
              }
            ]}
          />/        </View>/
        <Animated.View
          style={[
            styles.thumb,
            {
              width: thumbSize,
              height: thumbSize,
              backgroundColor: thumbTintColor,
              borderRadius: thumbSize / 2,/              transform: [{, translateX: thumbPosition   }]
            },
            isDragging && styles.thumbActive
          ]};
          {...panResponder.panHandlers};
        />/      </View>/    </View>/  ;);
};
const styles = StyleSheet.create({ container: {;
    marginVertical: spacing.;s;m  },
  labelContainer: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: spacing.sm,
  },
  label: { color: colors.textSecondary  },
  value: {
    color: colors.primary,
    fontWeight: "600",
  },
  sliderContainer: {
    position: "relative",
    justifyContent: "center",
  },
  track: { borderRadius: 2  },
  minimumTrack: {
    position: "absolute",
    left: 0,
    top: 0,
    borderRadius: 2,
  },
  thumb: {
    position: "absolute",
    top: -8,
    shadowColor: colors.black,
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  thumbActive: { transform: [{, scale: 1.2   }]
  }
});
export default React.memo(Slider);