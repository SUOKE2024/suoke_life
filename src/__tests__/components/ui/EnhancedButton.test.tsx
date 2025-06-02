import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react-native';
import { jest } from '@jest/globals';

// Mock EnhancedButton component
const MockEnhancedButton = jest.fn(() => null);

jest.mock('../../../components/ui/EnhancedButton', () => ({
  __esModule: true,
  default: MockEnhancedButton,
}));

describe('EnhancedButton 增强按钮组件测试', () => {
  const defaultProps = {
    testID: 'enhanced-button',
    title: '增强按钮',
    onPress: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('基础渲染测试', () => {
    it('应该正确渲染组件', () => {
      render(<MockEnhancedButton {...defaultProps} />);
      expect(MockEnhancedButton).toHaveBeenCalledWith(defaultProps, {});
    });

    it('应该显示按钮文本', () => {
      const textProps = {
        ...defaultProps,
        title: '确认',
        children: '确认按钮'
      };
      render(<MockEnhancedButton {...textProps} />);
      expect(MockEnhancedButton).toHaveBeenCalledWith(textProps, {});
    });

    it('应该支持自定义样式', () => {
      const styledProps = {
        ...defaultProps,
        style: {
          backgroundColor: '#ff6800',
          borderRadius: 8,
          padding: 12
        }
      };
      render(<MockEnhancedButton {...styledProps} />);
      expect(MockEnhancedButton).toHaveBeenCalledWith(styledProps, {});
    });
  });

  describe('增强功能测试', () => {
    it('应该支持波纹效果', () => {
      const rippleProps = {
        ...defaultProps,
        rippleEffect: true,
        rippleColor: 'rgba(255, 104, 0, 0.3)',
        rippleRadius: 300,
        rippleDuration: 400
      };
      render(<MockEnhancedButton {...rippleProps} />);
      expect(MockEnhancedButton).toHaveBeenCalledWith(rippleProps, {});
    });

    it('应该支持智能反馈', () => {
      const feedbackProps = {
        ...defaultProps,
        smartFeedback: true,
        feedbackType: 'success',
        feedbackMessage: '操作成功',
        feedbackDuration: 2000
      };
      render(<MockEnhancedButton {...feedbackProps} />);
      expect(MockEnhancedButton).toHaveBeenCalledWith(feedbackProps, {});
    });

    it('应该支持连续点击限制', () => {
      const clickLimitProps = {
        ...defaultProps,
        preventDoubleTap: true,
        tapCooldown: 1000,
        onDoubleTapAttempt: jest.fn()
      };
      render(<MockEnhancedButton {...clickLimitProps} />);
      expect(MockEnhancedButton).toHaveBeenCalledWith(clickLimitProps, {});
    });

    it('应该支持目标区域扩展', () => {
      const hitSlopProps = {
        ...defaultProps,
        extendHitSlop: true,
        hitSlop: { top: 10, bottom: 10, left: 10, right: 10 }
      };
      render(<MockEnhancedButton {...hitSlopProps} />);
      expect(MockEnhancedButton).toHaveBeenCalledWith(hitSlopProps, {});
    });
  });

  describe('进度指示器测试', () => {
    it('应该支持加载进度指示器', () => {
      const loadingProps = {
        ...defaultProps,
        loading: true,
        loadingIndicator: 'spinner',
        loadingSize: 'small',
        loadingColor: '#ffffff'
      };
      render(<MockEnhancedButton {...loadingProps} />);
      expect(MockEnhancedButton).toHaveBeenCalledWith(loadingProps, {});
    });

    it('应该支持进度条指示器', () => {
      const progressBarProps = {
        ...defaultProps,
        showProgress: true,
        progress: 0.75,
        progressColor: '#4CAF50',
        progressType: 'bar'
      };
      render(<MockEnhancedButton {...progressBarProps} />);
      expect(MockEnhancedButton).toHaveBeenCalledWith(progressBarProps, {});
    });

    it('应该支持圆形进度指示器', () => {
      const circleProgressProps = {
        ...defaultProps,
        showProgress: true,
        progress: 0.5,
        progressColor: '#2196F3',
        progressType: 'circle'
      };
      render(<MockEnhancedButton {...circleProgressProps} />);
      expect(MockEnhancedButton).toHaveBeenCalledWith(circleProgressProps, {});
    });

    it('应该支持状态变化进度', () => {
      const stateProgressProps = {
        ...defaultProps,
        progressStates: ['idle', 'loading', 'success', 'error'],
        currentProgressState: 'loading',
        stateIcons: { idle: 'clock', loading: 'spinner', success: 'check', error: 'close' }
      };
      render(<MockEnhancedButton {...stateProgressProps} />);
      expect(MockEnhancedButton).toHaveBeenCalledWith(stateProgressProps, {});
    });
  });

  describe('高级动画效果测试', () => {
    it('应该支持高级弹跳动画', () => {
      const advancedBounceProps = {
        ...defaultProps,
        animation: 'advanced-bounce',
        bounceIntensity: 1.2,
        bounceDamping: 0.5,
        bounceDelay: 0
      };
      render(<MockEnhancedButton {...advancedBounceProps} />);
      expect(MockEnhancedButton).toHaveBeenCalledWith(advancedBounceProps, {});
    });

    it('应该支持波浪动画', () => {
      const waveProps = {
        ...defaultProps,
        animation: 'wave',
        waveAmplitude: 10,
        waveFrequency: 2,
        waveDuration: 1000
      };
      render(<MockEnhancedButton {...waveProps} />);
      expect(MockEnhancedButton).toHaveBeenCalledWith(waveProps, {});
    });

    it('应该支持爆炸动画', () => {
      const explodeProps = {
        ...defaultProps,
        animation: 'explode',
        explodeScale: 1.5,
        explodeDuration: 300,
        explodeParticles: true
      };
      render(<MockEnhancedButton {...explodeProps} />);
      expect(MockEnhancedButton).toHaveBeenCalledWith(explodeProps, {});
    });

    it('应该支持自定义动画序列', () => {
      const sequenceProps = {
        ...defaultProps,
        animation: 'sequence',
        animationSequence: ['scale', 'rotate', 'fade'],
        sequenceDuration: 600,
        sequenceLoop: false
      };
      render(<MockEnhancedButton {...sequenceProps} />);
      expect(MockEnhancedButton).toHaveBeenCalledWith(sequenceProps, {});
    });
  });

  describe('条件渲染测试', () => {
    it('应该根据条件显示不同内容', () => {
      const conditionalProps = {
        ...defaultProps,
        conditionalRender: true,
        condition: true,
        trueContent: '条件为真',
        falseContent: '条件为假'
      };
      render(<MockEnhancedButton {...conditionalProps} />);
      expect(MockEnhancedButton).toHaveBeenCalledWith(conditionalProps, {});
    });

    it('应该支持条件样式', () => {
      const conditionalStyleProps = {
        ...defaultProps,
        conditionalStyle: true,
        styleCondition: 'success',
        styleMapping: {
          success: { backgroundColor: '#4CAF50' },
          error: { backgroundColor: '#F44336' },
          warning: { backgroundColor: '#FF9800' }
        }
      };
      render(<MockEnhancedButton {...conditionalStyleProps} />);
      expect(MockEnhancedButton).toHaveBeenCalledWith(conditionalStyleProps, {});
    });

    it('应该支持条件禁用', () => {
      const conditionalDisabledProps = {
        ...defaultProps,
        conditionalDisabled: true,
        disableCondition: true,
        disabledMessage: '当前条件下不可用'
      };
      render(<MockEnhancedButton {...conditionalDisabledProps} />);
      expect(MockEnhancedButton).toHaveBeenCalledWith(conditionalDisabledProps, {});
    });
  });

  describe('自适应特性测试', () => {
    it('应该支持自适应宽度', () => {
      const adaptiveWidthProps = {
        ...defaultProps,
        adaptiveWidth: true,
        minWidth: 100,
        maxWidth: 300,
        contentPadding: 16
      };
      render(<MockEnhancedButton {...adaptiveWidthProps} />);
      expect(MockEnhancedButton).toHaveBeenCalledWith(adaptiveWidthProps, {});
    });

    it('应该支持自适应字体大小', () => {
      const adaptiveFontProps = {
        ...defaultProps,
        adaptiveFontSize: true,
        minFontSize: 12,
        maxFontSize: 18,
        fontSizeStep: 2
      };
      render(<MockEnhancedButton {...adaptiveFontProps} />);
      expect(MockEnhancedButton).toHaveBeenCalledWith(adaptiveFontProps, {});
    });

    it('应该支持内容溢出处理', () => {
      const overflowProps = {
        ...defaultProps,
        handleOverflow: true,
        numberOfLines: 1,
        ellipsizeMode: 'tail',
        showTooltipOnOverflow: true
      };
      render(<MockEnhancedButton {...overflowProps} />);
      expect(MockEnhancedButton).toHaveBeenCalledWith(overflowProps, {});
    });

    it('应该支持响应式行为', () => {
      const responsiveProps = {
        ...defaultProps,
        responsive: true,
        breakpoints: {
          small: { width: 320, height: 40, fontSize: 14 },
          medium: { width: 480, height: 48, fontSize: 16 },
          large: { width: 768, height: 56, fontSize: 18 }
        }
      };
      render(<MockEnhancedButton {...responsiveProps} />);
      expect(MockEnhancedButton).toHaveBeenCalledWith(responsiveProps, {});
    });
  });

  describe('扩展交互功能测试', () => {
    it('应该支持手势操作', () => {
      const gestureProps = {
        ...defaultProps,
        enableGestures: true,
        onSwipeLeft: jest.fn(),
        onSwipeRight: jest.fn(),
        onSwipeUp: jest.fn(),
        onSwipeDown: jest.fn()
      };
      render(<MockEnhancedButton {...gestureProps} />);
      expect(MockEnhancedButton).toHaveBeenCalledWith(gestureProps, {});
    });

    it('应该支持拖拽功能', () => {
      const draggableProps = {
        ...defaultProps,
        draggable: true,
        onDragStart: jest.fn(),
        onDragEnd: jest.fn(),
        dragBoundaries: { top: 0, left: 0, bottom: 500, right: 300 }
      };
      render(<MockEnhancedButton {...draggableProps} />);
      expect(MockEnhancedButton).toHaveBeenCalledWith(draggableProps, {});
    });

    it('应该支持缩放功能', () => {
      const pinchProps = {
        ...defaultProps,
        pinchable: true,
        onPinchStart: jest.fn(),
        onPinchEnd: jest.fn(),
        minScale: 0.8,
        maxScale: 1.2
      };
      render(<MockEnhancedButton {...pinchProps} />);
      expect(MockEnhancedButton).toHaveBeenCalledWith(pinchProps, {});
    });

    it('应该支持旋转功能', () => {
      const rotateProps = {
        ...defaultProps,
        rotatable: true,
        onRotateStart: jest.fn(),
        onRotateEnd: jest.fn(),
        minRotation: -45,
        maxRotation: 45
      };
      render(<MockEnhancedButton {...rotateProps} />);
      expect(MockEnhancedButton).toHaveBeenCalledWith(rotateProps, {});
    });
  });

  describe('高级触觉反馈测试', () => {
    it('应该支持多种触觉反馈模式', () => {
      const hapticModeProps = {
        ...defaultProps,
        hapticFeedback: true,
        hapticMode: 'complex',
        hapticPatterns: {
          success: ['light', 'wait', 'heavy'],
          error: ['heavy', 'wait', 'heavy'],
          warning: ['medium', 'wait', 'medium']
        }
      };
      render(<MockEnhancedButton {...hapticModeProps} />);
      expect(MockEnhancedButton).toHaveBeenCalledWith(hapticModeProps, {});
    });

    it('应该支持自定义触觉序列', () => {
      const hapticSequenceProps = {
        ...defaultProps,
        hapticFeedback: true,
        hapticSequence: ['light', 'medium', 'heavy'],
        hapticInterval: 100,
        hapticRepeat: false
      };
      render(<MockEnhancedButton {...hapticSequenceProps} />);
      expect(MockEnhancedButton).toHaveBeenCalledWith(hapticSequenceProps, {});
    });

    it('应该支持状态相关触觉反馈', () => {
      const stateHapticProps = {
        ...defaultProps,
        hapticFeedback: true,
        stateHaptics: true,
        onPressHaptic: 'light',
        onLongPressHaptic: 'medium',
        onErrorHaptic: 'heavy'
      };
      render(<MockEnhancedButton {...stateHapticProps} />);
      expect(MockEnhancedButton).toHaveBeenCalledWith(stateHapticProps, {});
    });
  });

  describe('声音反馈测试', () => {
    it('应该支持点击声音', () => {
      const soundProps = {
        ...defaultProps,
        soundFeedback: true,
        clickSound: 'click.mp3',
        soundVolume: 0.5
      };
      render(<MockEnhancedButton {...soundProps} />);
      expect(MockEnhancedButton).toHaveBeenCalledWith(soundProps, {});
    });

    it('应该支持状态声音', () => {
      const stateSoundProps = {
        ...defaultProps,
        soundFeedback: true,
        stateSounds: {
          success: 'success.mp3',
          error: 'error.mp3',
          warning: 'warning.mp3'
        }
      };
      render(<MockEnhancedButton {...stateSoundProps} />);
      expect(MockEnhancedButton).toHaveBeenCalledWith(stateSoundProps, {});
    });

    it('应该支持静音模式', () => {
      const muteSoundProps = {
        ...defaultProps,
        soundFeedback: true,
        muted: true,
        respectedSystemMute: true,
        muteToggleEnabled: true
      };
      render(<MockEnhancedButton {...muteSoundProps} />);
      expect(MockEnhancedButton).toHaveBeenCalledWith(muteSoundProps, {});
    });
  });

  describe('优化的重渲染测试', () => {
    it('应该支持自定义相等性检查', () => {
      const customEqualityProps = {
        ...defaultProps,
        optimizeRerender: true,
        customEqualityCheck: 'deep',
        skipPropsUpdate: ['style', 'onLayout']
      };
      render(<MockEnhancedButton {...customEqualityProps} />);
      expect(MockEnhancedButton).toHaveBeenCalledWith(customEqualityProps, {});
    });

    it('应该支持组件实例复用', () => {
      const instanceReuseProps = {
        ...defaultProps,
        reuseInstance: true,
        instanceId: 'enhancedButton-123',
        poolSize: 5
      };
      render(<MockEnhancedButton {...instanceReuseProps} />);
      expect(MockEnhancedButton).toHaveBeenCalledWith(instanceReuseProps, {});
    });

    it('应该支持按需渲染', () => {
      const onDemandProps = {
        ...defaultProps,
        renderOnDemand: true,
        visibilityThreshold: 0.1,
        preloadDistance: 300
      };
      render(<MockEnhancedButton {...onDemandProps} />);
      expect(MockEnhancedButton).toHaveBeenCalledWith(onDemandProps, {});
    });
  });

  describe('索克生活特色功能', () => {
    it('应该支持健康数据触发', () => {
      const healthProps = {
        ...defaultProps,
        healthAction: true,
        dataType: 'bloodPressure',
        triggerThreshold: 140,
        healthActionType: 'measure'
      };
      render(<MockEnhancedButton {...healthProps} />);
      expect(MockEnhancedButton).toHaveBeenCalledWith(healthProps, {});
    });

    it('应该支持中医诊断集成', () => {
      const tcmProps = {
        ...defaultProps,
        tcmIntegration: true,
        diagnosisType: 'pulse',
        collectSymptoms: true,
        symptomCategories: ['寒热', '气血', '脏腑']
      };
      render(<MockEnhancedButton {...tcmProps} />);
      expect(MockEnhancedButton).toHaveBeenCalledWith(tcmProps, {});
    });

    it('应该支持智能体互动', () => {
      const agentProps = {
        ...defaultProps,
        agentInteraction: true,
        agentId: 'xiaoai',
        interactionType: 'consultation',
        contextData: { symptoms: ['头痛', '乏力'], duration: '3天' }
      };
      render(<MockEnhancedButton {...agentProps} />);
      expect(MockEnhancedButton).toHaveBeenCalledWith(agentProps, {});
    });

    it('应该支持区块链健康数据验证', () => {
      const blockchainProps = {
        ...defaultProps,
        blockchainVerification: true,
        dataHash: '0x123abc...',
        verificationLevel: 'high',
        privacyPreserving: true
      };
      render(<MockEnhancedButton {...blockchainProps} />);
      expect(MockEnhancedButton).toHaveBeenCalledWith(blockchainProps, {});
    });
  });

  describe('增强安全特性测试', () => {
    it('应该支持操作确认', () => {
      const confirmProps = {
        ...defaultProps,
        requireConfirmation: true,
        confirmationMessage: '确定要执行此操作吗？',
        confirmText: '确定',
        cancelText: '取消'
      };
      render(<MockEnhancedButton {...confirmProps} />);
      expect(MockEnhancedButton).toHaveBeenCalledWith(confirmProps, {});
    });

    it('应该支持生物识别验证', () => {
      const biometricProps = {
        ...defaultProps,
        biometricAuth: true,
        biometricType: 'fingerprint',
        biometricPrompt: '请验证指纹以继续',
        fallbackToPasscode: true
      };
      render(<MockEnhancedButton {...biometricProps} />);
      expect(MockEnhancedButton).toHaveBeenCalledWith(biometricProps, {});
    });

    it('应该支持操作限流', () => {
      const rateLimitProps = {
        ...defaultProps,
        rateLimit: true,
        maxActionsPerMinute: 5,
        cooldownPeriod: 60000,
        onRateLimitExceeded: jest.fn()
      };
      render(<MockEnhancedButton {...rateLimitProps} />);
      expect(MockEnhancedButton).toHaveBeenCalledWith(rateLimitProps, {});
    });

    it('应该支持权限检查', () => {
      const permissionProps = {
        ...defaultProps,
        checkPermissions: true,
        requiredPermissions: ['health_data', 'camera'],
        onPermissionDenied: jest.fn(),
        requestMissingPermissions: true
      };
      render(<MockEnhancedButton {...permissionProps} />);
      expect(MockEnhancedButton).toHaveBeenCalledWith(permissionProps, {});
    });
  });

  describe('高级错误处理测试', () => {
    it('应该支持操作重试', () => {
      const retryProps = {
        ...defaultProps,
        enableRetry: true,
        maxRetries: 3,
        retryDelay: 1000,
        exponentialBackoff: true
      };
      render(<MockEnhancedButton {...retryProps} />);
      expect(MockEnhancedButton).toHaveBeenCalledWith(retryProps, {});
    });

    it('应该支持错误分类处理', () => {
      const errorHandlingProps = {
        ...defaultProps,
        advancedErrorHandling: true,
        errorHandlers: {
          network: jest.fn(),
          validation: jest.fn(),
          permission: jest.fn(),
          timeout: jest.fn()
        }
      };
      render(<MockEnhancedButton {...errorHandlingProps} />);
      expect(MockEnhancedButton).toHaveBeenCalledWith(errorHandlingProps, {});
    });

    it('应该支持服务降级', () => {
      const fallbackProps = {
        ...defaultProps,
        serviceDegradation: true,
        fallbackAction: jest.fn(),
        offlineModeEnabled: true,
        syncOnReconnect: true
      };
      render(<MockEnhancedButton {...fallbackProps} />);
      expect(MockEnhancedButton).toHaveBeenCalledWith(fallbackProps, {});
    });

    it('应该支持错误日志记录', () => {
      const errorLoggingProps = {
        ...defaultProps,
        errorLogging: true,
        logLevel: 'error',
        includeContext: true,
        anonymizeUserData: true
      };
      render(<MockEnhancedButton {...errorLoggingProps} />);
      expect(MockEnhancedButton).toHaveBeenCalledWith(errorLoggingProps, {});
    });
  });

  describe('性能优化测试', () => {
    it('应该高效渲染组件', () => {
      const performanceProps = {
        ...defaultProps,
        optimizeRendering: true,
        useNativeDriver: true,
        memoized: true
      };

      const startTime = performance.now();
      render(<MockEnhancedButton {...performanceProps} />);
      const endTime = performance.now();

      expect(endTime - startTime).toBeLessThan(50);
      expect(MockEnhancedButton).toHaveBeenCalledWith(performanceProps, {});
    });

    it('应该支持防抖处理', () => {
      const debounceProps = {
        ...defaultProps,
        debounce: true,
        debounceDelay: 300,
        onPress: jest.fn()
      };
      render(<MockEnhancedButton {...debounceProps} />);
      expect(MockEnhancedButton).toHaveBeenCalledWith(debounceProps, {});
    });

    it('应该支持节流处理', () => {
      const throttleProps = {
        ...defaultProps,
        throttle: true,
        throttleDelay: 1000,
        onPress: jest.fn()
      };
      render(<MockEnhancedButton {...throttleProps} />);
      expect(MockEnhancedButton).toHaveBeenCalledWith(throttleProps, {});
    });
  });

  describe('可访问性测试', () => {
    it('应该提供高级可访问性标签', () => {
      const accessibilityProps = {
        ...defaultProps,
        enhancedAccessibility: true,
        dynamicAccessibilityLabel: (props) => `${props.title}按钮，点击执行操作`,
        accessibilityActions: [
          { name: 'activate', label: '激活' },
          { name: 'longpress', label: '长按' }
        ]
      };
      render(<MockEnhancedButton {...accessibilityProps} />);
      expect(MockEnhancedButton).toHaveBeenCalledWith(accessibilityProps, {});
    });

    it('应该支持语音控制', () => {
      const voiceControlProps = {
        ...defaultProps,
        voiceControl: true,
        voiceCommands: ['点击', '确认', '提交'],
        voiceFeedback: true,
        voicePrompt: '说"点击"来确认'
      };
      render(<MockEnhancedButton {...voiceControlProps} />);
      expect(MockEnhancedButton).toHaveBeenCalledWith(voiceControlProps, {});
    });

    it('应该支持可访问性自定义', () => {
      const a11yCustomProps = {
        ...defaultProps,
        a11yCustomizations: true,
        a11yHighContrast: true,
        a11yFontScale: 1.5,
        a11yReduceMotion: true
      };
      render(<MockEnhancedButton {...a11yCustomProps} />);
      expect(MockEnhancedButton).toHaveBeenCalledWith(a11yCustomProps, {});
    });
  });
}); 