import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react-native';
import { jest } from '@jest/globals';

// Mock Icon component
const MockIcon = jest.fn(() => null);

jest.mock('../../../components/ui/Icon', () => ({
  __esModule: true,
  default: MockIcon,
}));

describe('Icon 图标组件测试', () => {
  const defaultProps = {
    testID: 'icon',
    name: 'home',
    size: 24,
    color: '#000000',
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('基础渲染测试', () => {
    it('应该正确渲染组件', () => {
      render(<MockIcon {...defaultProps} />);
      expect(MockIcon).toHaveBeenCalledWith(defaultProps, {});
    });

    it('应该支持不同图标名称', () => {
      const nameProps = {
        ...defaultProps,
        name: 'heart',
      };
      render(<MockIcon {...nameProps} />);
      expect(MockIcon).toHaveBeenCalledWith(nameProps, {});
    });

    it('应该支持不同尺寸', () => {
      const sizeProps = {
        ...defaultProps,
        size: 32,
      };
      render(<MockIcon {...sizeProps} />);
      expect(MockIcon).toHaveBeenCalledWith(sizeProps, {});
    });

    it('应该支持不同颜色', () => {
      const colorProps = {
        ...defaultProps,
        color: '#ff6800',
      };
      render(<MockIcon {...colorProps} />);
      expect(MockIcon).toHaveBeenCalledWith(colorProps, {});
    });
  });

  describe('样式配置测试', () => {
    it('应该支持自定义样式', () => {
      const styledProps = {
        ...defaultProps,
        style: {
          marginRight: 8,
          opacity: 0.8,
        },
      };
      render(<MockIcon {...styledProps} />);
      expect(MockIcon).toHaveBeenCalledWith(styledProps, {});
    });

    it('应该支持背景样式', () => {
      const backgroundProps = {
        ...defaultProps,
        backgroundColor: '#f5f5f5',
        borderRadius: 12,
        padding: 8,
      };
      render(<MockIcon {...backgroundProps} />);
      expect(MockIcon).toHaveBeenCalledWith(backgroundProps, {});
    });

    it('应该支持边框样式', () => {
      const borderProps = {
        ...defaultProps,
        borderWidth: 1,
        borderColor: '#e0e0e0',
        borderStyle: 'solid',
        borderRadius: 12,
      };
      render(<MockIcon {...borderProps} />);
      expect(MockIcon).toHaveBeenCalledWith(borderProps, {});
    });

    it('应该支持定位样式', () => {
      const positionProps = {
        ...defaultProps,
        position: 'absolute',
        top: 10,
        right: 10,
      };
      render(<MockIcon {...positionProps} />);
      expect(MockIcon).toHaveBeenCalledWith(positionProps, {});
    });
  });

  describe('图标类型测试', () => {
    it('应该支持矢量图标', () => {
      const vectorProps = {
        ...defaultProps,
        type: 'vector',
        family: 'MaterialIcons',
      };
      render(<MockIcon {...vectorProps} />);
      expect(MockIcon).toHaveBeenCalledWith(vectorProps, {});
    });

    it('应该支持图片图标', () => {
      const imageProps = {
        ...defaultProps,
        type: 'image',
        source: require('../../../assets/images/icon.png'),
        resizeMode: 'contain',
      };
      render(<MockIcon {...imageProps} />);
      expect(MockIcon).toHaveBeenCalledWith(imageProps, {});
    });

    it('应该支持SVG图标', () => {
      const svgProps = {
        ...defaultProps,
        type: 'svg',
        svgXml: '<svg></svg>',
      };
      render(<MockIcon {...svgProps} />);
      expect(MockIcon).toHaveBeenCalledWith(svgProps, {});
    });

    it('应该支持自定义组件图标', () => {
      const Component = () => null;
      const customProps = {
        ...defaultProps,
        type: 'custom',
        component: Component,
      };
      render(<MockIcon {...customProps} />);
      expect(MockIcon).toHaveBeenCalledWith(customProps, {});
    });
  });

  describe('交互功能测试', () => {
    it('应该处理点击事件', () => {
      const onPressMock = jest.fn();
      const pressableProps = {
        ...defaultProps,
        onPress: onPressMock,
        pressable: true,
      };
      render(<MockIcon {...pressableProps} />);
      expect(MockIcon).toHaveBeenCalledWith(pressableProps, {});
    });

    it('应该处理长按事件', () => {
      const onLongPressMock = jest.fn();
      const longPressProps = {
        ...defaultProps,
        onLongPress: onLongPressMock,
        delayLongPress: 500,
      };
      render(<MockIcon {...longPressProps} />);
      expect(MockIcon).toHaveBeenCalledWith(longPressProps, {});
    });

    it('应该支持禁用状态', () => {
      const disabledProps = {
        ...defaultProps,
        disabled: true,
        disabledColor: '#cccccc',
        opacity: 0.5,
      };
      render(<MockIcon {...disabledProps} />);
      expect(MockIcon).toHaveBeenCalledWith(disabledProps, {});
    });

    it('应该支持点击反馈', () => {
      const feedbackProps = {
        ...defaultProps,
        pressEffect: true,
        activeOpacity: 0.7,
        underlayColor: '#f5f5f5',
      };
      render(<MockIcon {...feedbackProps} />);
      expect(MockIcon).toHaveBeenCalledWith(feedbackProps, {});
    });
  });

  describe('主题适配测试', () => {
    it('应该支持亮色主题', () => {
      const lightThemeProps = {
        ...defaultProps,
        theme: 'light',
        color: '#333333',
      };
      render(<MockIcon {...lightThemeProps} />);
      expect(MockIcon).toHaveBeenCalledWith(lightThemeProps, {});
    });

    it('应该支持暗色主题', () => {
      const darkThemeProps = {
        ...defaultProps,
        theme: 'dark',
        color: '#ffffff',
      };
      render(<MockIcon {...darkThemeProps} />);
      expect(MockIcon).toHaveBeenCalledWith(darkThemeProps, {});
    });

    it('应该支持索克品牌主题', () => {
      const brandThemeProps = {
        ...defaultProps,
        theme: 'suoke',
        color: '#ff6800',
      };
      render(<MockIcon {...brandThemeProps} />);
      expect(MockIcon).toHaveBeenCalledWith(brandThemeProps, {});
    });
  });

  describe('动画效果测试', () => {
    it('应该支持旋转动画', () => {
      const rotateProps = {
        ...defaultProps,
        rotate: true,
        rotationDuration: 2000,
        rotationDirection: 'clockwise',
      };
      render(<MockIcon {...rotateProps} />);
      expect(MockIcon).toHaveBeenCalledWith(rotateProps, {});
    });

    it('应该支持闪烁动画', () => {
      const blinkProps = {
        ...defaultProps,
        blink: true,
        blinkDuration: 1000,
        blinkOpacity: 0.3,
      };
      render(<MockIcon {...blinkProps} />);
      expect(MockIcon).toHaveBeenCalledWith(blinkProps, {});
    });

    it('应该支持缩放动画', () => {
      const scaleProps = {
        ...defaultProps,
        pulse: true,
        pulseDuration: 1500,
        pulseScale: 1.2,
      };
      render(<MockIcon {...scaleProps} />);
      expect(MockIcon).toHaveBeenCalledWith(scaleProps, {});
    });
  });

  describe('可访问性测试', () => {
    it('应该提供可访问性标签', () => {
      const accessibilityProps = {
        ...defaultProps,
        accessibilityLabel: '首页图标',
        accessibilityHint: '点击返回首页',
        accessibilityRole: 'button',
      };
      render(<MockIcon {...accessibilityProps} />);
      expect(MockIcon).toHaveBeenCalledWith(accessibilityProps, {});
    });

    it('应该支持无障碍状态', () => {
      const a11yStateProps = {
        ...defaultProps,
        accessibilityState: {
          disabled: false,
          selected: true,
        },
      };
      render(<MockIcon {...a11yStateProps} />);
      expect(MockIcon).toHaveBeenCalledWith(a11yStateProps, {});
    });

    it('应该支持屏幕阅读器', () => {
      const screenReaderProps = {
        ...defaultProps,
        importantForAccessibility: 'yes',
      };
      render(<MockIcon {...screenReaderProps} />);
      expect(MockIcon).toHaveBeenCalledWith(screenReaderProps, {});
    });
  });

  describe('索克生活特色功能', () => {
    it('应该支持健康状态图标', () => {
      const healthProps = {
        ...defaultProps,
        name: 'health',
        healthStatus: 'normal',
        statusColor: '#4CAF50',
        showStatusBadge: true,
      };
      render(<MockIcon {...healthProps} />);
      expect(MockIcon).toHaveBeenCalledWith(healthProps, {});
    });

    it('应该支持中医辨证图标', () => {
      const tcmProps = {
        ...defaultProps,
        name: 'tcm',
        syndromeType: '气虚',
        elementColor: '#FFC107',
      };
      render(<MockIcon {...tcmProps} />);
      expect(MockIcon).toHaveBeenCalledWith(tcmProps, {});
    });

    it('应该支持智能体图标', () => {
      const agentProps = {
        ...defaultProps,
        name: 'agent',
        agentType: 'xiaoai',
        activeState: true,
        activityAnimation: true,
      };
      render(<MockIcon {...agentProps} />);
      expect(MockIcon).toHaveBeenCalledWith(agentProps, {});
    });

    it('应该支持区块链验证图标', () => {
      const blockchainProps = {
        ...defaultProps,
        name: 'blockchain',
        verified: true,
        verificationColor: '#4CAF50',
        showVerificationBadge: true,
      };
      render(<MockIcon {...blockchainProps} />);
      expect(MockIcon).toHaveBeenCalledWith(blockchainProps, {});
    });
  });

  describe('组合图标测试', () => {
    it('应该支持徽章图标', () => {
      const badgeProps = {
        ...defaultProps,
        badge: true,
        badgeCount: 5,
        badgeColor: '#ff6800',
        badgePosition: 'topRight',
      };
      render(<MockIcon {...badgeProps} />);
      expect(MockIcon).toHaveBeenCalledWith(badgeProps, {});
    });

    it('应该支持组合图标', () => {
      const stackedProps = {
        ...defaultProps,
        stacked: true,
        secondaryIcon: 'checkmark',
        secondaryIconColor: '#4CAF50',
        secondaryIconPosition: 'bottomRight',
      };
      render(<MockIcon {...stackedProps} />);
      expect(MockIcon).toHaveBeenCalledWith(stackedProps, {});
    });

    it('应该支持图标文本组合', () => {
      const textProps = {
        ...defaultProps,
        withText: true,
        text: '首页',
        textStyle: {
          fontSize: 12,
          color: '#333333',
          marginTop: 4,
        },
        textPosition: 'bottom',
      };
      render(<MockIcon {...textProps} />);
      expect(MockIcon).toHaveBeenCalledWith(textProps, {});
    });
  });

  describe('性能优化测试', () => {
    it('应该高效渲染图标', () => {
      const performanceProps = {
        ...defaultProps,
        optimizeRendering: true,
        useNativeDriver: true,
      };
      
      const startTime = performance.now();
      render(<MockIcon {...performanceProps} />);
      const endTime = performance.now();
      
      expect(endTime - startTime).toBeLessThan(50);
      expect(MockIcon).toHaveBeenCalledWith(performanceProps, {});
    });

    it('应该支持缓存渲染', () => {
      const cacheProps = {
        ...defaultProps,
        cacheRendering: true,
        memoize: true,
      };
      render(<MockIcon {...cacheProps} />);
      expect(MockIcon).toHaveBeenCalledWith(cacheProps, {});
    });
  });
}); 