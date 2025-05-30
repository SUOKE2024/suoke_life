import { AccessibilityInfo, Platform } from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import React, {


  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";

// 无障碍配置类型
interface AccessibilityConfig {
  // 屏幕阅读器
  screenReaderEnabled: boolean;

  // 高对比度模式
  highContrastEnabled: boolean;

  // 大字体模式
  largeFontEnabled: boolean;

  // 减少动画
  reduceMotionEnabled: boolean;

  // 语音导航
  voiceNavigationEnabled: boolean;

  // 触觉反馈
  hapticFeedbackEnabled: boolean;

  // 焦点指示器
  focusIndicatorEnabled: boolean;

  // 语音速度 (0.5 - 2.0)
  speechRate: number;

  // 字体缩放比例 (0.8 - 2.0)
  fontScale: number;

  // 触摸目标最小尺寸
  minimumTouchTargetSize: number;
}

// 语音选项
interface SpeechOptions {
  rate?: number;
  pitch?: number;
  language?: string;
  interrupt?: boolean;
}

// 触觉反馈类型
type HapticFeedbackType =
  | "light"
  | "medium"
  | "heavy"
  | "success"
  | "warning"
  | "error";

// 默认配置
const defaultConfig: AccessibilityConfig = {
  screenReaderEnabled: false,
  highContrastEnabled: false,
  largeFontEnabled: false,
  reduceMotionEnabled: false,
  voiceNavigationEnabled: false,
  hapticFeedbackEnabled: true,
  focusIndicatorEnabled: true,
  speechRate: 1.0,
  fontScale: 1.0,
  minimumTouchTargetSize: 44,
};

// 无障碍上下文类型
interface AccessibilityContextType {
  config: AccessibilityConfig;
  updateConfig: (updates: Partial<AccessibilityConfig>) => Promise<void>;
  resetConfig: () => Promise<void>;

  // 辅助功能
  announceForAccessibility: (message: string) => void;
  setAccessibilityFocus: (ref: any) => void;

  // 系统检测
  isScreenReaderEnabled: boolean;
  isReduceMotionEnabled: boolean;
  isBoldTextEnabled: boolean;

  // 语音功能
  speak: (text: string, options?: SpeechOptions) => void;
  stopSpeaking: () => void;

  // 触觉反馈
  triggerHapticFeedback: (type?: HapticFeedbackType) => void;
}

// 创建上下文
const AccessibilityContext = createContext<
  AccessibilityContextType | undefined
>(undefined);

// 无障碍提供者组件
interface AccessibilityProviderProps {
  children: ReactNode;
}

export const AccessibilityProvider: React.FC<AccessibilityProviderProps> = ({
  children,
}) => {
  const [config, setConfig] = useState<AccessibilityConfig>(defaultConfig);
  const [isScreenReaderEnabled, setIsScreenReaderEnabled] = useState(false);
  const [isReduceMotionEnabled, setIsReduceMotionEnabled] = useState(false);
  const [isBoldTextEnabled, setIsBoldTextEnabled] = useState(false);

  // 初始化无障碍设置
  useEffect(() => {
    const initializeAccessibility = async () => {
      try {
        // 加载保存的配置
        const savedConfig = await AsyncStorage.getItem("accessibility_config");
        if (savedConfig) {
          const parsedConfig = JSON.parse(savedConfig);
          setConfig({ ...defaultConfig, ...parsedConfig });
        }

        // 检测系统无障碍设置
        if (Platform.OS === "ios") {
          const screenReaderEnabled =
            await AccessibilityInfo.isScreenReaderEnabled();
          const reduceMotionEnabled =
            await AccessibilityInfo.isReduceMotionEnabled();
          const boldTextEnabled = await AccessibilityInfo.isBoldTextEnabled();

          setIsScreenReaderEnabled(screenReaderEnabled);
          setIsReduceMotionEnabled(reduceMotionEnabled);
          setIsBoldTextEnabled(boldTextEnabled);
        } else if (Platform.OS === "android") {
          const screenReaderEnabled =
            await AccessibilityInfo.isScreenReaderEnabled();
          setIsScreenReaderEnabled(screenReaderEnabled);
        }
      } catch (error) {
        console.warn("Failed to initialize accessibility settings:", error);
      }
    };

    initializeAccessibility();

    // 监听系统无障碍设置变化
    const screenReaderSubscription = AccessibilityInfo.addEventListener(
      "screenReaderChanged",
      setIsScreenReaderEnabled
    );

    let reduceMotionSubscription: any;
    let boldTextSubscription: any;

    if (Platform.OS === "ios") {
      reduceMotionSubscription = AccessibilityInfo.addEventListener(
        "reduceMotionChanged",
        setIsReduceMotionEnabled
      );

      boldTextSubscription = AccessibilityInfo.addEventListener(
        "boldTextChanged",
        setIsBoldTextEnabled
      );
    }

    return () => {
      screenReaderSubscription?.remove();
      reduceMotionSubscription?.remove();
      boldTextSubscription?.remove();
    };
  }, []);

  // 更新配置
  const updateConfig = async (updates: Partial<AccessibilityConfig>) => {
    const newConfig = { ...config, ...updates };
    setConfig(newConfig);

    try {
      await AsyncStorage.setItem(
        "accessibility_config",
        JSON.stringify(newConfig)
      );
    } catch (error) {
      console.warn("Failed to save accessibility config:", error);
    }
  };

  // 重置配置
  const resetConfig = async () => {
    setConfig(defaultConfig);

    try {
      await AsyncStorage.removeItem("accessibility_config");
    } catch (error) {
      console.warn("Failed to reset accessibility config:", error);
    }
  };

  // 无障碍公告
  const announceForAccessibility = (message: string) => {
    if (isScreenReaderEnabled) {
      AccessibilityInfo.announceForAccessibility(message);
    }
  };

  // 设置无障碍焦点
  const setAccessibilityFocus = (ref: any) => {
    if (ref && ref.current && isScreenReaderEnabled) {
      AccessibilityInfo.setAccessibilityFocus(ref.current);
    }
  };

  // 语音播报
  const speak = (text: string, options: SpeechOptions = {}) => {
    if (!config.voiceNavigationEnabled && !isScreenReaderEnabled) {
      return;
    }

    const speechOptions = {
      rate: options.rate || config.speechRate,
      pitch: options.pitch || 1.0,
      language: options.language || "zh-CN",
      interrupt: options.interrupt || false,
    };

    // 这里可以集成第三方TTS库，如react-native-tts
    console.log("Speaking:", text, speechOptions);

    // 如果启用了屏幕阅读器，使用系统公告
    if (isScreenReaderEnabled) {
      announceForAccessibility(text);
    }
  };

  // 停止语音
  const stopSpeaking = () => {
    // 这里可以调用TTS库的停止方法
    console.log("Stopping speech");
  };

  // 触觉反馈
  const triggerHapticFeedback = (type: HapticFeedbackType = "light") => {
    if (!config.hapticFeedbackEnabled) {
      return;
    }

    // 这里可以集成react-native-haptic-feedback
    console.log("Triggering haptic feedback:", type);

    // 简单的振动反馈
    if (Platform.OS === "ios") {
      // iOS 触觉反馈
      // HapticFeedback.trigger(type);
    } else {
      // Android 振动
      // Vibration.vibrate(100);
    }
  };

  const contextValue: AccessibilityContextType = {
    config,
    updateConfig,
    resetConfig,
    announceForAccessibility,
    setAccessibilityFocus,
    isScreenReaderEnabled,
    isReduceMotionEnabled,
    isBoldTextEnabled,
    speak,
    stopSpeaking,
    triggerHapticFeedback,
  };

  return (
    <AccessibilityContext.Provider value={contextValue}>
      {children}
    </AccessibilityContext.Provider>
  );
};

// 无障碍钩子
export const useAccessibility = (): AccessibilityContextType => {
  const context = useContext(AccessibilityContext);
  if (context === undefined) {
    throw new Error(
      "useAccessibility must be used within an AccessibilityProvider"
    );
  }
  return context;
};

// 无障碍工具函数
export const accessibilityUtils = {
  // 生成无障碍标签
  generateAccessibilityLabel: (
    label: string,
    value?: string,
    hint?: string
  ): string => {
    let accessibilityLabel = label;
    if (value) {
      accessibilityLabel += `, ${value}`;
    }
    if (hint) {
      accessibilityLabel += `. ${hint}`;
    }
    return accessibilityLabel;
  },

  // 生成无障碍提示
  generateAccessibilityHint: (action: string, result?: string): string => {
    let hint = action;
    if (result) {
      hint += `. ${result}`;
    }
    return hint;
  },

  // 检查触摸目标尺寸
  checkTouchTargetSize: (
    width: number,
    height: number,
    minSize: number = 44
  ): boolean => {
    return width >= minSize && height >= minSize;
  },

  // 计算对比度
  calculateContrast: (foreground: string, background: string): number => {
    // 简化的对比度计算，实际应用中可以使用更精确的算法
    const getLuminance = (color: string): number => {
      // 这里应该实现真正的亮度计算
      return 0.5; // 占位符
    };

    const l1 = getLuminance(foreground);
    const l2 = getLuminance(background);

    return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
  },

  // 检查对比度是否符合WCAG标准
  checkContrastRatio: (
    foreground: string,
    background: string,
    level: "AA" | "AAA" = "AA"
  ): boolean => {
    const contrast = accessibilityUtils.calculateContrast(
      foreground,
      background
    );
    const minContrast = level === "AAA" ? 7 : 4.5;
    return contrast >= minContrast;
  },
};

// 无障碍HOC
interface WithAccessibilityProps {
  accessibility?: AccessibilityContextType;
}

export const withAccessibility = <P extends object>(
  Component: React.ComponentType<P>
) => {
  return React.forwardRef<any, P & WithAccessibilityProps>((props, ref) => {
    const accessibility = useAccessibility();

    return (
      <Component {...(props as P)} ref={ref} accessibility={accessibility} />
    );
  });
};

// 导出类型
export type {
  AccessibilityConfig,
  AccessibilityContextType,
  SpeechOptions,
  HapticFeedbackType,
  WithAccessibilityProps,
};
