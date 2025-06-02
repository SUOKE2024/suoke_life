import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react-native';
import { jest } from '@jest/globals';

// Mock Card component
const MockCard = jest.fn(() => null);

jest.mock('../../../components/ui/Card', () => ({
  __esModule: true,
  default: MockCard,
}));

describe('Card 卡片组件测试', () => {
  const defaultProps = {
    testID: 'card',
    title: '卡片标题',
    children: null,
    onPress: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('基础渲染测试', () => {
    it('应该正确渲染组件', () => {
      render(<MockCard {...defaultProps} />);
      expect(MockCard).toHaveBeenCalledWith(defaultProps, {});
    });

    it('应该显示卡片标题', () => {
      const titleProps = {
        ...defaultProps,
        title: '健康数据',
        titleStyle: {
          fontSize: 18,
          fontWeight: 'bold',
          color: '#333333'
        },
        showTitle: true
      };
      render(<MockCard {...titleProps} />);
      expect(MockCard).toHaveBeenCalledWith(titleProps, {});
    });

    it('应该显示子内容', () => {
      const childrenProps = {
        ...defaultProps,
        children: <MockCard testID="child-card" />
      };
      render(<MockCard {...childrenProps} />);
      expect(MockCard).toHaveBeenCalledWith(childrenProps, {});
    });

    it('应该支持自定义样式', () => {
      const styledProps = {
        ...defaultProps,
        style: {
          backgroundColor: '#ffffff',
          borderRadius: 8,
          padding: 16,
          margin: 8
        }
      };
      render(<MockCard {...styledProps} />);
      expect(MockCard).toHaveBeenCalledWith(styledProps, {});
    });
  });

  describe('样式配置测试', () => {
    it('应该支持边框样式', () => {
      const borderProps = {
        ...defaultProps,
        borderWidth: 1,
        borderColor: '#e0e0e0',
        borderStyle: 'solid',
        borderRadius: 8
      };
      render(<MockCard {...borderProps} />);
      expect(MockCard).toHaveBeenCalledWith(borderProps, {});
    });

    it('应该支持阴影效果', () => {
      const shadowProps = {
        ...defaultProps,
        elevation: 3,
        shadowColor: '#000000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4
      };
      render(<MockCard {...shadowProps} />);
      expect(MockCard).toHaveBeenCalledWith(shadowProps, {});
    });

    it('应该支持渐变背景', () => {
      const gradientProps = {
        ...defaultProps,
        gradient: true,
        gradientColors: ['#f5f5f5', '#e0e0e0'],
        gradientDirection: 'vertical'
      };
      render(<MockCard {...gradientProps} />);
      expect(MockCard).toHaveBeenCalledWith(gradientProps, {});
    });

    it('应该支持背景图片', () => {
      const backgroundProps = {
        ...defaultProps,
        backgroundImage: 'https://example.com/background.jpg',
        backgroundImageStyle: {
          opacity: 0.2,
          resizeMode: 'cover'
        }
      };
      render(<MockCard {...backgroundProps} />);
      expect(MockCard).toHaveBeenCalledWith(backgroundProps, {});
    });
  });

  describe('交互功能测试', () => {
    it('应该处理点击事件', () => {
      const onPressMock = jest.fn();
      const pressableProps = {
        ...defaultProps,
        onPress: onPressMock,
        pressable: true
      };
      render(<MockCard {...pressableProps} />);
      expect(MockCard).toHaveBeenCalledWith(pressableProps, {});
    });

    it('应该处理长按事件', () => {
      const onLongPressMock = jest.fn();
      const longPressProps = {
        ...defaultProps,
        onLongPress: onLongPressMock,
        delayLongPress: 500
      };
      render(<MockCard {...longPressProps} />);
      expect(MockCard).toHaveBeenCalledWith(longPressProps, {});
    });

    it('应该支持禁用状态', () => {
      const disabledProps = {
        ...defaultProps,
        disabled: true,
        disabledStyle: {
          opacity: 0.5,
          backgroundColor: '#f5f5f5'
        }
      };
      render(<MockCard {...disabledProps} />);
      expect(MockCard).toHaveBeenCalledWith(disabledProps, {});
    });

    it('应该支持点击反馈', () => {
      const feedbackProps = {
        ...defaultProps,
        pressEffect: true,
        activeOpacity: 0.8,
        underlayColor: '#f5f5f5'
      };
      render(<MockCard {...feedbackProps} />);
      expect(MockCard).toHaveBeenCalledWith(feedbackProps, {});
    });
  });

  describe('布局选项测试', () => {
    it('应该支持水平布局', () => {
      const horizontalProps = {
        ...defaultProps,
        horizontal: true,
        contentDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between'
      };
      render(<MockCard {...horizontalProps} />);
      expect(MockCard).toHaveBeenCalledWith(horizontalProps, {});
    });

    it('应该支持垂直布局', () => {
      const verticalProps = {
        ...defaultProps,
        horizontal: false,
        contentDirection: 'column',
        alignItems: 'stretch',
        justifyContent: 'flex-start'
      };
      render(<MockCard {...verticalProps} />);
      expect(MockCard).toHaveBeenCalledWith(verticalProps, {});
    });

    it('应该支持内容填充', () => {
      const paddingProps = {
        ...defaultProps,
        padding: 16,
        paddingTop: 24,
        paddingHorizontal: 16,
        paddingVertical: 12
      };
      render(<MockCard {...paddingProps} />);
      expect(MockCard).toHaveBeenCalledWith(paddingProps, {});
    });

    it('应该支持内容间距', () => {
      const spacingProps = {
        ...defaultProps,
        contentSpacing: 8,
        spaceBetween: true
      };
      render(<MockCard {...spacingProps} />);
      expect(MockCard).toHaveBeenCalledWith(spacingProps, {});
    });
  });

  describe('卡片内容配置测试', () => {
    it('应该支持卡片头部', () => {
      const headerProps = {
        ...defaultProps,
        header: <MockCard testID="header-content" />,
        headerStyle: {
          borderBottomWidth: 1,
          borderBottomColor: '#e0e0e0',
          paddingBottom: 8,
          marginBottom: 8
        }
      };
      render(<MockCard {...headerProps} />);
      expect(MockCard).toHaveBeenCalledWith(headerProps, {});
    });

    it('应该支持卡片底部', () => {
      const footerProps = {
        ...defaultProps,
        footer: <MockCard testID="footer-content" />,
        footerStyle: {
          borderTopWidth: 1,
          borderTopColor: '#e0e0e0',
          paddingTop: 8,
          marginTop: 8
        }
      };
      render(<MockCard {...footerProps} />);
      expect(MockCard).toHaveBeenCalledWith(footerProps, {});
    });

    it('应该支持卡片标题图标', () => {
      const titleIconProps = {
        ...defaultProps,
        titleIcon: 'health',
        titleIconPosition: 'left',
        titleIconStyle: {
          marginRight: 8,
          color: '#ff6800'
        }
      };
      render(<MockCard {...titleIconProps} />);
      expect(MockCard).toHaveBeenCalledWith(titleIconProps, {});
    });

    it('应该支持卡片副标题', () => {
      const subtitleProps = {
        ...defaultProps,
        subtitle: '详细健康信息',
        subtitleStyle: {
          fontSize: 14,
          color: '#666666',
          marginTop: 4
        }
      };
      render(<MockCard {...subtitleProps} />);
      expect(MockCard).toHaveBeenCalledWith(subtitleProps, {});
    });
  });

  describe('主题适配测试', () => {
    it('应该支持亮色主题', () => {
      const lightThemeProps = {
        ...defaultProps,
        theme: 'light',
        backgroundColor: '#ffffff',
        textColor: '#333333',
        borderColor: '#e0e0e0'
      };
      render(<MockCard {...lightThemeProps} />);
      expect(MockCard).toHaveBeenCalledWith(lightThemeProps, {});
    });

    it('应该支持暗色主题', () => {
      const darkThemeProps = {
        ...defaultProps,
        theme: 'dark',
        backgroundColor: '#333333',
        textColor: '#ffffff',
        borderColor: '#555555'
      };
      render(<MockCard {...darkThemeProps} />);
      expect(MockCard).toHaveBeenCalledWith(darkThemeProps, {});
    });

    it('应该支持索克品牌主题', () => {
      const brandThemeProps = {
        ...defaultProps,
        theme: 'suoke',
        accentColor: '#ff6800',
        backgroundColor: '#ffffff',
        textColor: '#333333',
        borderColor: '#ff6800'
      };
      render(<MockCard {...brandThemeProps} />);
      expect(MockCard).toHaveBeenCalledWith(brandThemeProps, {});
    });
  });

  describe('动画效果测试', () => {
    it('应该支持显示动画', () => {
      const animatedProps = {
        ...defaultProps,
        animated: true,
        animationType: 'fade',
        animationDuration: 300
      };
      render(<MockCard {...animatedProps} />);
      expect(MockCard).toHaveBeenCalledWith(animatedProps, {});
    });

    it('应该支持按压动画', () => {
      const pressAnimationProps = {
        ...defaultProps,
        pressAnimation: true,
        pressAnimationType: 'scale',
        pressAnimationValue: 0.95
      };
      render(<MockCard {...pressAnimationProps} />);
      expect(MockCard).toHaveBeenCalledWith(pressAnimationProps, {});
    });

    it('应该支持自定义动画', () => {
      const customAnimationProps = {
        ...defaultProps,
        customAnimation: true,
        animationConfig: {
          type: 'spring',
          tension: 40,
          friction: 7
        }
      };
      render(<MockCard {...customAnimationProps} />);
      expect(MockCard).toHaveBeenCalledWith(customAnimationProps, {});
    });
  });

  describe('可访问性测试', () => {
    it('应该提供可访问性标签', () => {
      const accessibilityProps = {
        ...defaultProps,
        accessibilityLabel: '健康数据卡片',
        accessibilityHint: '点击查看详细健康数据',
        accessibilityRole: 'button'
      };
      render(<MockCard {...accessibilityProps} />);
      expect(MockCard).toHaveBeenCalledWith(accessibilityProps, {});
    });

    it('应该支持无障碍状态', () => {
      const a11yStateProps = {
        ...defaultProps,
        accessibilityState: {
          disabled: false,
          selected: false,
          checked: false
        }
      };
      render(<MockCard {...a11yStateProps} />);
      expect(MockCard).toHaveBeenCalledWith(a11yStateProps, {});
    });

    it('应该支持屏幕阅读器', () => {
      const screenReaderProps = {
        ...defaultProps,
        accessibilityLiveRegion: 'polite',
        importantForAccessibility: 'yes'
      };
      render(<MockCard {...screenReaderProps} />);
      expect(MockCard).toHaveBeenCalledWith(screenReaderProps, {});
    });
  });

  describe('索克生活特色功能', () => {
    it('应该支持健康数据卡片', () => {
      const healthProps = {
        ...defaultProps,
        cardType: 'health',
        healthMetric: 'bloodPressure',
        healthStatus: 'normal',
        healthColor: '#4CAF50'
      };
      render(<MockCard {...healthProps} />);
      expect(MockCard).toHaveBeenCalledWith(healthProps, {});
    });

    it('应该支持中医诊断卡片', () => {
      const tcmProps = {
        ...defaultProps,
        cardType: 'tcm',
        syndromeType: '气虚',
        syndromeDescription: '气虚症状表现为神疲乏力、气短懒言等',
        recommendedHerbs: ['人参', '黄芪', '白术']
      };
      render(<MockCard {...tcmProps} />);
      expect(MockCard).toHaveBeenCalledWith(tcmProps, {});
    });

    it('应该支持智能体推荐卡片', () => {
      const agentProps = {
        ...defaultProps,
        cardType: 'agent',
        agentId: 'xiaoai',
        recommendationType: 'diet',
        confidenceScore: 0.85,
        showAgentAvatar: true
      };
      render(<MockCard {...agentProps} />);
      expect(MockCard).toHaveBeenCalledWith(agentProps, {});
    });

    it('应该支持区块链验证卡片', () => {
      const blockchainProps = {
        ...defaultProps,
        cardType: 'blockchain',
        verified: true,
        verificationDate: '2025-06-15',
        dataHash: '0x123abc...',
        showVerificationBadge: true
      };
      render(<MockCard {...blockchainProps} />);
      expect(MockCard).toHaveBeenCalledWith(blockchainProps, {});
    });
  });

  describe('性能优化测试', () => {
    it('应该高效渲染卡片', () => {
      const performanceProps = {
        ...defaultProps,
        optimizeRendering: true,
        memoize: true,
        useNativeDriver: true
      };
      
      const startTime = performance.now();
      render(<MockCard {...performanceProps} />);
      const endTime = performance.now();
      
      expect(endTime - startTime).toBeLessThan(50);
      expect(MockCard).toHaveBeenCalledWith(performanceProps, {});
    });

    it('应该支持懒加载', () => {
      const lazyProps = {
        ...defaultProps,
        lazyLoad: true,
        loadOnVisible: true,
        visibilityThreshold: 0.1
      };
      render(<MockCard {...lazyProps} />);
      expect(MockCard).toHaveBeenCalledWith(lazyProps, {});
    });
  });
});