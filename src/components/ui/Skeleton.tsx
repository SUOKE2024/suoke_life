import React, { useEffect, useRef } from 'react';
import {
    Animated,
    StyleSheet,
    View,
    ViewStyle,
} from 'react-native';
import { useTheme } from '../../contexts/ThemeContext';

export interface SkeletonProps {
  width?: number | string;
  height?: number | string;
  borderRadius?: number;
  variant?: 'text' | 'rectangular' | 'circular';
  animation?: 'pulse' | 'wave' | 'none';
  style?: ViewStyle;
  children?: React.ReactNode;
  testID?: string;
}

export const Skeleton: React.FC<SkeletonProps> = ({
  width = '100%',
  height = 20,
  borderRadius,
  variant = 'text',
  animation = 'pulse',
  style,
  children,
  testID,
}) => {
  const { currentTheme } = useTheme();
  const animatedValue = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    if (animation === 'none') return;

    const createAnimation = () => {
      if (animation === 'pulse') {
        return Animated.sequence([
          Animated.timing(animatedValue, {
            toValue: 1,
            duration: 1000,
            useNativeDriver: true,
          }),
          Animated.timing(animatedValue, {
            toValue: 0,
            duration: 1000,
            useNativeDriver: true,
          }),
        ]);
      } else if (animation === 'wave') {
        return Animated.timing(animatedValue, {
          toValue: 1,
          duration: 1500,
          useNativeDriver: true,
        });
      }
      return null;
    };

    const animationSequence = createAnimation();
    if (animationSequence) {
      Animated.loop(animationSequence).start();
    }

    return () => {
      animatedValue.stopAnimation();
    };
  }, [animation, animatedValue]);

  const getVariantStyles = (): ViewStyle => {
    const baseHeight = typeof height === 'number' ? height : 20;
    
    switch (variant) {
      case 'circular':
        const size = typeof width === 'number' ? width : 40;
        return {
          width: size as number,
          height: size as number,
          borderRadius: (size as number) / 2,
        };
      case 'rectangular':
        return {
          width: width as any,
          height: height as any,
          borderRadius: borderRadius || 4,
        };
      case 'text':
      default:
        return {
          width: width as any,
          height: baseHeight,
          borderRadius: borderRadius || baseHeight / 2,
        };
    }
  };

  const getAnimationStyle = () => {
    if (animation === 'none') return {};

    if (animation === 'pulse') {
      const opacity = animatedValue.interpolate({
        inputRange: [0, 1],
        outputRange: [0.3, 0.7],
      });
      return { opacity };
    }

    if (animation === 'wave') {
      const translateX = animatedValue.interpolate({
        inputRange: [0, 1],
        outputRange: [-100, 100],
      });
      return { transform: [{ translateX }] };
    }

    return {};
  };

  const variantStyles = getVariantStyles();
  const animationStyle = getAnimationStyle();

  const styles = StyleSheet.create({
    skeleton: {
      backgroundColor: currentTheme.colors.outline,
      overflow: 'hidden',
    },
    wave: {
      position: 'absolute',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: currentTheme.colors.surface,
      opacity: 0.5,
    },
  });

  if (children) {
    return (
      <View style={[styles.skeleton, variantStyles, style]} testID={testID}>
        {children}
      </View>
    );
  }

  return (
    <View style={[styles.skeleton, variantStyles, style]} testID={testID}>
      {animation === 'wave' && (
        <Animated.View style={[styles.wave, animationStyle]} />
      )}
      {animation === 'pulse' && (
        <Animated.View
          style={[
            {
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              backgroundColor: currentTheme.colors.surface,
            },
            animationStyle,
          ]}
        />
      )}
    </View>
  );
};

// 预设的骨架屏组件
export const SkeletonText: React.FC<Omit<SkeletonProps, 'variant'>> = (props) => (
  <Skeleton {...props} variant="text" />
);

export const SkeletonCircle: React.FC<Omit<SkeletonProps, 'variant'>> = (props) => (
  <Skeleton {...props} variant="circular" />
);

export const SkeletonRectangle: React.FC<Omit<SkeletonProps, 'variant'>> = (props) => (
  <Skeleton {...props} variant="rectangular" />
);

// 复合骨架屏组件
export interface SkeletonListProps {
  count?: number;
  spacing?: number;
  itemHeight?: number;
  showAvatar?: boolean;
  showTitle?: boolean;
  showSubtitle?: boolean;
  style?: ViewStyle;
}

export const SkeletonList: React.FC<SkeletonListProps> = ({
  count = 3,
  spacing = 16,
  itemHeight = 60,
  showAvatar = true,
  showTitle = true,
  showSubtitle = true,
  style,
}) => {
  const items = Array.from({ length: count }, (_, index) => (
    <View
      key={index}
      style={{
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: index < count - 1 ? spacing : 0,
        height: itemHeight,
      }}
    >
      {showAvatar && (
        <SkeletonCircle
          width={40}
          height={40}
          style={{ marginRight: 12 }}
        />
      )}
      <View style={{ flex: 1 }}>
        {showTitle && (
          <SkeletonText
            width="70%"
            height={16}
            style={{ marginBottom: showSubtitle ? 8 : 0 }}
          />
        )}
        {showSubtitle && (
          <SkeletonText
            width="50%"
            height={12}
          />
        )}
      </View>
    </View>
  ));

  return <View style={style}>{items}</View>;
};

export default Skeleton; 