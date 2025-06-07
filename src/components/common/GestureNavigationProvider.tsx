import React, { createContext, useContext, useRef, useCallback } from 'react';
import { View, Animated, Dimensions, Vibration, PanResponder } from 'react-native';
import { useNavigation } from '@react-navigation/native';
const { width: screenWidth, height: screenHeight } = Dimensions.get('window');
// 手势配置接口
interface GestureConfig {
  swipeThreshold: number;
  velocityThreshold: number;
  enableBackGesture: boolean;
  enableQuickActions: boolean;
  enableHapticFeedback: boolean;
  edgeSwipeWidth: number;
}
// 手势动作类型
type GestureAction =
  | 'back'
  | 'forward'
  | 'home'
  | 'menu'
  | 'search'
  | 'refresh';
// 手势方向
type GestureDirection = 'left' | 'right' | 'up' | 'down';
// 手势上下文
interface GestureContextType {
  config: GestureConfig;
  registerGestureAction: (direction: GestureDirection, action: GestureAction) => void;
  unregisterGestureAction: (direction: GestureDirection) => void;
  triggerHapticFeedback: (type?: 'light' | 'medium' | 'heavy') => void;
}
// 默认配置
const DEFAULT_CONFIG: GestureConfig = {,
  swipeThreshold: 50,
  velocityThreshold: 500,
  enableBackGesture: true,
  enableQuickActions: true,
  enableHapticFeedback: true,
  edgeSwipeWidth: 20,
};
// 创建上下文
const GestureContext = createContext<GestureContextType | null>(null);
// 手势导航提供者
export const GestureNavigationProvider: React.FC<{,
  children: React.ReactNode;
  config?: Partial<GestureConfig>;
}> = ({ children, config: userConfig = {} }) => {
  const navigation = useNavigation();
  const config = { ...DEFAULT_CONFIG, ...userConfig };
    // 手势动作映射
  const gestureActions = useRef<Map<GestureDirection, GestureAction>>(new Map([
    ["right",back'],
    ["left",forward'],
    ["up",menu'],
    ["down",refresh'],
  ]));
  // 动画值
  const translateX = useRef(new Animated.Value(0)).current;
  const translateY = useRef(new Animated.Value(0)).current;
  const opacity = useRef(new Animated.Value(1)).current;
  // 触觉反馈
  const triggerHapticFeedback = useCallback(type: 'light' | 'medium' | 'heavy' = 'light') => {
    if (config.enableHapticFeedback) {
      switch (type) {
        case 'light':
          Vibration.vibrate(10);
          break;
        case 'medium':
          Vibration.vibrate(20);
          break;
        case 'heavy':
          Vibration.vibrate([0, 30]);
          break;
      }
    }
  }, [config.enableHapticFeedback]);
  // 注册手势动作
  const registerGestureAction = useCallback(direction: GestureDirection, action: GestureAction) => {
    gestureActions.current.set(direction, action);
  }, []);
  // 注销手势动作
  const unregisterGestureAction = useCallback(direction: GestureDirection) => {
    gestureActions.current.delete(direction);
  }, []);
  // 执行手势动作
  const executeGestureAction = useCallback(action: GestureAction) => {
    switch (action) {
      case 'back':
        if (navigation.canGoBack()) {
          navigation.goBack();
        }
        break;
      case 'forward':
        console.log('Forward gesture triggered');
        break;
      case 'home':
        navigation.navigate('Home' as never);
        break;
      case 'menu':
        console.log('Menu gesture triggered');
        break;
      case 'search':
        console.log('Search gesture triggered');
        break;
      case 'refresh':
        console.log('Refresh gesture triggered');
        break;
    }
  }, [navigation]);
  // 获取手势方向
  const getGestureDirection = useCallback(dx: number, dy: number): GestureDirection | null => {
    const absDx = Math.abs(dx);
    const absDy = Math.abs(dy);
    if (absDx > absDy) {
      if (absDx > config.swipeThreshold) {
        return dx > 0 ? 'right' : 'left';
      }
    } else {
      if (absDy > config.swipeThreshold) {
        return dy > 0 ? 'down' : 'up';
      }
    }
    return null;
  }, [config.swipeThreshold]);
  // 创建PanResponder;
  const panResponder = useRef(
    PanResponder.create({
      onMoveShouldSetPanResponder: (evt, gestureState) => {
        const { dx, dy } = gestureState;
        return Math.abs(dx) > 10 || Math.abs(dy) > 10;
      },
      onPanResponderGrant: () => {
        // 手势开始
      },
      onPanResponderMove: (evt, gestureState) => {
        const { dx, dy } = gestureState;
                // 更新动画值
        translateX.setValue(dx);
        translateY.setValue(dy);
        // 根据手势距离调整透明度
        const distance = Math.sqrt(dx * dx + dy * dy);
        const maxDistance = screenWidth * 0.3;
        const newOpacity = Math.max(0.7, 1 - (distance / maxDistance) * 0.3);
        opacity.setValue(newOpacity);
      },
      onPanResponderRelease: (evt, gestureState) => {
        const { dx, dy, vx, vy } = gestureState;
        const direction = getGestureDirection(dx, dy);
                if (direction) {
          const velocity = direction === 'left' || direction === 'right' ? Math.abs(vx) : Math.abs(vy);
                    if (velocity > config.velocityThreshold / 1000) { // PanResponder的速度单位不同
            const action = gestureActions.current.get(direction);
            if (action) {
              triggerHapticFeedback('medium');
              executeGestureAction(action);
            }
          }
        }
        // 重置动画值
        Animated.parallel([
          Animated.spring(translateX, {
            toValue: 0,
            useNativeDriver: true,
          }),
          Animated.spring(translateY, {
            toValue: 0,
            useNativeDriver: true,
          }),
          Animated.spring(opacity, {
            toValue: 1,
            useNativeDriver: true,
          }),
        ]).start();
      },
    })
  ).current;
  const contextValue: GestureContextType = {
    config,
    registerGestureAction,
    unregisterGestureAction,
    triggerHapticFeedback,
  };
  return (
    <GestureContext.Provider value={contextValue}>
      <Animated.View;
        style={
          flex: 1,
          transform: [
            { translateX },
            { translateY },
          ],
          opacity,
        }}
        {...panResponder.panHandlers}
      >
        {children}
      </Animated.View>
    </GestureContext.Provider>
  );
};
// 手势导航Hook;
export const useGestureNavigation = () => {
  const context = useContext(GestureContext);
    if (!context) {
    throw new Error('useGestureNavigation must be used within GestureNavigationProvider');
  }
  return {
    config: context.config,
    registerGestureAction: context.registerGestureAction,
    unregisterGestureAction: context.unregisterGestureAction,
    triggerHapticFeedback: context.triggerHapticFeedback,
  };
};
export default GestureNavigationProvider;