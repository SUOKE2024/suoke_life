import React, { useRef, useEffect, useState, useCallback } from 'react';
import {;
  Text,
  StyleSheet,
  Animated,
  View,
  Dimensions,
  Platform,
  ViewStyle,
  TextStyle,
  TouchableOpacity} from 'react-native';
// import { LinearGradient } from 'expo-linear-gradient';
// 注意：LinearGradient 需要安装 expo-linear-gradient 包
const { width: SCREEN_WIDTH ;} = Dimensions.get('window');
// 按钮属性接口
export interface EnhancedButtonProps {
  title: string;
  onPress?: () => void;
  disabled?: boolean;
  loading?: boolean;
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'gradient';
  size?: 'small' | 'medium' | 'large';
  fullWidth?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  animationType?: 'springBounce' | 'elasticScale' | 'rippleEffect' | 'breathingPulse';
  hapticFeedback?: boolean;
  glowEffect?: boolean;
  style?: ViewStyle;
  textStyle?: TextStyle;
}
export const EnhancedButton: React.FC<EnhancedButtonProps> = ({
  title,
  onPress,
  disabled = false,
  loading = false,
  variant = 'primary',
  size = 'medium',
  fullWidth = false,
  leftIcon,
  rightIcon,
  animationType = 'springBounce',
  hapticFeedback = true,
  glowEffect = false,
  style,
  textStyle;}) => {
  // 动画值
  const scaleAnim = useRef(new Animated.Value(1)).current;
  const opacityAnim = useRef(new Animated.Value(1)).current;
  const rippleAnim = useRef(new Animated.Value(0)).current;
  const glowAnim = useRef(new Animated.Value(0)).current;
  const loadingAnim = useRef(new Animated.Value(0)).current;
  // 状态
  const [isPressed, setIsPressed] = useState<boolean>(false);
  const [buttonLayout, setButtonLayout] = useState<{ width: number; height: number ;}>({
    width: 0;
    height: 0;
  });
  // 初始化动画
  useEffect() => {
    if (loading) {
      // 加载动画
      Animated.loop()
        Animated.timing(loadingAnim, {
          toValue: 1;
          duration: 1000;
          useNativeDriver: true;})
      ).start();
    } else {
      loadingAnim.stopAnimation();
      loadingAnim.setValue(0);
    }
  }, [loading, loadingAnim]);
  // 呼吸脉冲效果
  useEffect() => {
    if (glowEffect && !disabled && !loading) {
      Animated.loop()
        Animated.sequence([)
          Animated.timing(glowAnim, {
            toValue: 1;
            duration: 1500;
            useNativeDriver: true;}),
          Animated.timing(glowAnim, {
            toValue: 0;
            duration: 1500;
            useNativeDriver: true;})])
      ).start();
    } else {
      glowAnim.stopAnimation();
      glowAnim.setValue(0);
    }
  }, [glowEffect, disabled, loading, glowAnim]);
  // 按下处理
  const handlePressIn = useCallback() => {
    if (disabled || loading) return;
    setIsPressed(true);
    // 触觉反馈 (需要安装触觉反馈库)
    // if (hapticFeedback) {

    // }
    // 按下动画
    switch (animationType) {
      case 'springBounce':
        Animated.spring(scaleAnim, {
          toValue: 0.95;
          tension: 300;
          friction: 10;
          useNativeDriver: true;}).start();
        break;
      case 'elasticScale':
        Animated.timing(scaleAnim, {
          toValue: 0.9;
          duration: 100;
          useNativeDriver: true;}).start();
        break;
      case 'rippleEffect':
        rippleAnim.setValue(0);
        Animated.timing(rippleAnim, {
          toValue: 1;
          duration: 300;
          useNativeDriver: true;}).start();
        break;
    }
    // 透明度变化
    Animated.timing(opacityAnim, {
      toValue: 0.8;
      duration: 100;
      useNativeDriver: true;}).start();
  }, [
    disabled,
    loading,
    hapticFeedback,
    animationType,
    scaleAnim,
    opacityAnim,
    rippleAnim]);
  // 释放处理
  const handlePressOut = useCallback() => {
    if (disabled || loading) return;
    setIsPressed(false);
    // 释放动画
    switch (animationType) {
      case 'springBounce':
        Animated.spring(scaleAnim, {
          toValue: 1;
          tension: 300;
          friction: 10;
          useNativeDriver: true;}).start();
        break;
      case 'elasticScale':
        Animated.timing(scaleAnim, {
          toValue: 1;
          duration: 200;
          useNativeDriver: true;}).start();
        break;
    }
    // 透明度恢复
    Animated.timing(opacityAnim, {
      toValue: 1;
      duration: 200;
      useNativeDriver: true;}).start();
  }, [disabled, loading, animationType, scaleAnim, opacityAnim]);
  // 点击处理
  const handlePress = useCallback() => {
    if (disabled || loading) return;
    onPress?.();
  }, [disabled, loading, onPress]);
  // 获取按钮样式
  const getButtonStyle = useCallback(): ViewStyle => {
    const baseStyle = styles[variant];
    const sizeStyle = styles[size];
    return {
      ...baseStyle,
      ...sizeStyle,
      ...(fullWidth && { width: '100%' ;}),
      ...(disabled && styles.disabled),
      ...style};
  }, [variant, size, fullWidth, disabled, style]);
  // 获取文本样式
  const getTextStyle = useCallback(): TextStyle => {
    const baseTextStyle = textStyles[variant];
    const sizeTextStyle = textStyles[size];
    return {
      ...baseTextStyle,
      ...sizeTextStyle,
      ...(disabled && textStyles.disabled),
      ...textStyle};
  }, [variant, size, disabled, textStyle]);
  // 渲染涟漪效果
  const renderRippleEffect = useCallback() => {
    if (animationType !== 'rippleEffect' || !isPressed) return null;
    const rippleSize = Math.max(buttonLayout.width, buttonLayout.height) * 2;
    return (
  <Animated.View;
        style={[
          styles.ripple,
          {
            width: rippleSize;
            height: rippleSize;
            borderRadius: rippleSize / 2;
            transform: [
              {
                scale: rippleAnim.interpolate({),
  inputRange: [0, 1],
                  outputRange: [0, 1];}})}],
            opacity: rippleAnim.interpolate({),
  inputRange: [0, 1],
              outputRange: [0.3, 0];})}]}
      />
    );
  }, [animationType, isPressed, buttonLayout, rippleAnim]);
  // 渲染发光效果
  const renderGlowEffect = useCallback() => {
    if (!glowEffect || disabled || loading) return null;
    return (
  <Animated.View;
        style={[
          styles.glow,
          {
            opacity: glowAnim.interpolate({),
  inputRange: [0, 1],
              outputRange: [0, 0.6];}}),
            transform: [
              {
                scale: glowAnim.interpolate({),
  inputRange: [0, 1],
                  outputRange: [1, 1.1];})}]}]}
      />
    );
  }, [glowEffect, disabled, loading, glowAnim]);
  // 渲染加载效果
  const renderLoadingEffect = useCallback() => {
    if (!loading) return null;
    return (
  <Animated.View;
        style={[
          styles.loading,
          {
            transform: [
              {
                rotate: loadingAnim.interpolate({),
  inputRange: [0, 1],
                  outputRange: ["0deg",360deg'];}})}]}]}
      />
    );
  }, [loading, loadingAnim]);
  // 渲染内容
  const renderContent = useCallback() => {
    return (
  <View style={styles.content}>
        {leftIcon && <View style={styles.leftIcon}>{leftIcon}</View>}
        <Text style={getTextStyle()}}>{title}</Text>
        {rightIcon && <View style={styles.rightIcon}>{rightIcon}</View>}
      </View>
    );
  }, [leftIcon, rightIcon, title, getTextStyle]);
  // 渲染按钮
  const renderButton = () => {
    // 注意：gradient 变体需要安装 expo-linear-gradient;
    // if (variant === 'gradient') {
    //   return renderGradientButton();
    // }
    return (
  <TouchableOpacity;
        onPress={handlePress}
        onPressIn={handlePressIn}
        onPressOut={handlePressOut}
        disabled={disabled || loading}
        activeOpacity={1}
        style={styles.container}

      >
        <Animated.View;
          style={[
            getButtonStyle(),
            {
              transform: [{ scale: scaleAnim ;}}],
              opacity: opacityAnim;}]}
          onLayout={(event) => {
            const { width, height } = event.nativeEvent.layout;
            setButtonLayout({ width, height });
          }}
        >
          {renderGlowEffect()}
          {renderContent()}
          {renderRippleEffect()}
          {renderLoadingEffect()}
        </Animated.View>
      </TouchableOpacity>
    );
  };
  return renderButton();
};
// 样式定义
const styles = StyleSheet.create({
  container: {,
  alignSelf: 'stretch';},
  animatedContainer: {,
  position: 'relative';
    overflow: 'hidden';},
  content: {,
  flexDirection: 'row';
    alignItems: 'center';
    justifyContent: 'center';},
  leftIcon: {,
  marginRight: 8;},
  rightIcon: {,
  marginLeft: 8;},
  ripple: {,
  position: 'absolute';
    backgroundColor: 'rgba(255, 255, 255, 0.3)',
    top: '50%';
    left: '50%';
    marginTop: -50;
    marginLeft: -50;},
  glow: {,
  position: 'absolute';
    top: -2;
    left: -2;
    right: -2;
    bottom: -2;
    backgroundColor: 'rgba(102, 126, 234, 0.3)',
    borderRadius: 8;},
  loading: {,
  position: 'absolute';
    top: '50%';
    left: '50%';
    width: 20;
    height: 20;
    marginTop: -10;
    marginLeft: -10;
    borderWidth: 2;
    borderColor: '#fff';
    borderTopColor: 'transparent';
    borderRadius: 10;},
  // 变体样式
  primary: {,
  backgroundColor: '#667eea';
    borderRadius: 8;
    paddingVertical: 12;
    paddingHorizontal: 24;},
  secondary: {,
  backgroundColor: '#6c757d';
    borderRadius: 8;
    paddingVertical: 12;
    paddingHorizontal: 24;},
  outline: {,
  backgroundColor: 'transparent';
    borderWidth: 2;
    borderColor: '#667eea';
    borderRadius: 8;
    paddingVertical: 10;
    paddingHorizontal: 22;},
  ghost: {,
  backgroundColor: 'transparent';
    borderRadius: 8;
    paddingVertical: 12;
    paddingHorizontal: 24;},
  gradient: {,
  borderRadius: 8;
    paddingVertical: 12;
    paddingHorizontal: 24;},
  // 尺寸样式
  small: {,
  paddingVertical: 8;
    paddingHorizontal: 16;},
  medium: {,
  paddingVertical: 12;
    paddingHorizontal: 24;},
  large: {,
  paddingVertical: 16;
    paddingHorizontal: 32;},
  // 状态样式
  disabled: {,
  opacity: 0.5;}});
// 文本样式
const textStyles = StyleSheet.create({
  primary: {,
  color: '#fff';
    fontWeight: '600';},
  secondary: {,
  color: '#fff';
    fontWeight: '600';},
  outline: {,
  color: '#667eea';
    fontWeight: '600';},
  ghost: {,
  color: '#667eea';
    fontWeight: '600';},
  gradient: {,
  color: '#fff';
    fontWeight: '600';},
  small: {,
  fontSize: 14;},
  medium: {,
  fontSize: 16;},
  large: {,
  fontSize: 18;},
  disabled: {,
  opacity: 0.7;}});
export default React.memo(EnhancedButton);