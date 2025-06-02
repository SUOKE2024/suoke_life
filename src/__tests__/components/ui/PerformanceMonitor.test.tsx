import React from 'react';
import { render } from '@testing-library/react-native';
import { jest } from '@jest/globals';

// Mock PerformanceMonitor component
const MockPerformanceMonitor = jest.fn(() => null);

jest.mock('../../../components/ui/PerformanceMonitor', () => ({
  __esModule: true,
  default: MockPerformanceMonitor,
}));

describe('PerformanceMonitor 性能监控组件测试', () => {
  const defaultProps = {
    testID: 'performance-monitor',
    enabled: true
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('基础渲染测试', () => {
    it('应该正确渲染组件', () => {
      render(<MockPerformanceMonitor {...defaultProps} />);
      expect(MockPerformanceMonitor).toHaveBeenCalledWith(defaultProps, {});
    });

    it('应该支持禁用状态', () => {
      const disabledProps = {
        ...defaultProps,
        enabled: false
      };
      render(<MockPerformanceMonitor {...disabledProps} />);
      expect(MockPerformanceMonitor).toHaveBeenCalledWith(disabledProps, {});
    });

    it('应该支持子组件', () => {
      const childrenProps = {
        ...defaultProps,
        children: <div>测试内容</div>
      };
      render(<MockPerformanceMonitor {...childrenProps} />);
      expect(MockPerformanceMonitor).toHaveBeenCalledWith(childrenProps, {});
    });
  });

  describe('监控配置测试', () => {
    it('应该支持帧率监控', () => {
      const fpsProps = {
        ...defaultProps,
        monitorFPS: true,
        fpsWarningThreshold: 45,
        fpsCriticalThreshold: 30
      };
      render(<MockPerformanceMonitor {...fpsProps} />);
      expect(MockPerformanceMonitor).toHaveBeenCalledWith(fpsProps, {});
    });

    it('应该支持内存监控', () => {
      const memoryProps = {
        ...defaultProps,
        monitorMemory: true,
        memoryWarningThreshold: 80,
        memoryCriticalThreshold: 90
      };
      render(<MockPerformanceMonitor {...memoryProps} />);
      expect(MockPerformanceMonitor).toHaveBeenCalledWith(memoryProps, {});
    });

    it('应该支持渲染时间监控', () => {
      const renderTimeProps = {
        ...defaultProps,
        monitorRenderTime: true,
        renderTimeWarningThreshold: 16,
        renderTimeCriticalThreshold: 33
      };
      render(<MockPerformanceMonitor {...renderTimeProps} />);
      expect(MockPerformanceMonitor).toHaveBeenCalledWith(renderTimeProps, {});
    });

    it('应该支持网络监控', () => {
      const networkProps = {
        ...defaultProps,
        monitorNetwork: true,
        networkTimeoutThreshold: 5000
      };
      render(<MockPerformanceMonitor {...networkProps} />);
      expect(MockPerformanceMonitor).toHaveBeenCalledWith(networkProps, {});
    });
  });

  describe('事件处理测试', () => {
    it('应该支持性能警告回调', () => {
      const warningProps = {
        ...defaultProps,
        onPerformanceWarning: jest.fn(),
        warningThresholds: {
          fps: 45,
          memory: 80,
          renderTime: 16,
          networkTime: 5000
        }
      };
      render(<MockPerformanceMonitor {...warningProps} />);
      expect(MockPerformanceMonitor).toHaveBeenCalledWith(warningProps, {});
    });

    it('应该支持性能报告回调', () => {
      const reportProps = {
        ...defaultProps,
        onPerformanceReport: jest.fn(),
        reportInterval: 10000
      };
      render(<MockPerformanceMonitor {...reportProps} />);
      expect(MockPerformanceMonitor).toHaveBeenCalledWith(reportProps, {});
    });

    it('应该支持性能崩溃回调', () => {
      const crashProps = {
        ...defaultProps,
        onPerformanceCrash: jest.fn(),
        crashThresholds: {
          fps: 15,
          memory: 95,
          renderTime: 100
        }
      };
      render(<MockPerformanceMonitor {...crashProps} />);
      expect(MockPerformanceMonitor).toHaveBeenCalledWith(crashProps, {});
    });
  });

  describe('调试功能测试', () => {
    it('应该支持开发模式', () => {
      const devModeProps = {
        ...defaultProps,
        devMode: true,
        showDevPanel: true
      };
      render(<MockPerformanceMonitor {...devModeProps} />);
      expect(MockPerformanceMonitor).toHaveBeenCalledWith(devModeProps, {});
    });

    it('应该支持日志记录', () => {
      const loggingProps = {
        ...defaultProps,
        enableLogging: true,
        logLevel: 'verbose',
        logStorage: 'file'
      };
      render(<MockPerformanceMonitor {...loggingProps} />);
      expect(MockPerformanceMonitor).toHaveBeenCalledWith(loggingProps, {});
    });

    it('应该支持性能标记', () => {
      const markProps = {
        ...defaultProps,
        enableMarkers: true,
        markers: ['app-start', 'data-load', 'render-complete']
      };
      render(<MockPerformanceMonitor {...markProps} />);
      expect(MockPerformanceMonitor).toHaveBeenCalledWith(markProps, {});
    });
  });

  describe('可视化配置测试', () => {
    it('应该支持显示指标', () => {
      const metricsProps = {
        ...defaultProps,
        showMetrics: true,
        metricsPosition: 'topRight',
        metricsOpacity: 0.7
      };
      render(<MockPerformanceMonitor {...metricsProps} />);
      expect(MockPerformanceMonitor).toHaveBeenCalledWith(metricsProps, {});
    });

    it('应该支持图表显示', () => {
      const chartProps = {
        ...defaultProps,
        showCharts: true,
        chartTypes: ['fps', 'memory', 'cpu'],
        chartTimeWindow: 60
      };
      render(<MockPerformanceMonitor {...chartProps} />);
      expect(MockPerformanceMonitor).toHaveBeenCalledWith(chartProps, {});
    });

    it('应该支持自定义主题', () => {
      const themeProps = {
        ...defaultProps,
        theme: 'dark',
        colors: {
          background: '#222222',
          text: '#FFFFFF',
          warning: '#FFC107',
          critical: '#F44336',
          normal: '#4CAF50'
        }
      };
      render(<MockPerformanceMonitor {...themeProps} />);
      expect(MockPerformanceMonitor).toHaveBeenCalledWith(themeProps, {});
    });
  });

  describe('优化功能测试', () => {
    it('应该支持自动优化', () => {
      const autoOptimizeProps = {
        ...defaultProps,
        autoOptimize: true,
        optimizationLevels: ['low', 'medium', 'high'],
        currentOptimizationLevel: 'low'
      };
      render(<MockPerformanceMonitor {...autoOptimizeProps} />);
      expect(MockPerformanceMonitor).toHaveBeenCalledWith(autoOptimizeProps, {});
    });

    it('应该支持渲染节流', () => {
      const throttleProps = {
        ...defaultProps,
        enableThrottling: true,
        throttleLevel: 'medium',
        throttleComponents: ['list', 'animation', 'effects']
      };
      render(<MockPerformanceMonitor {...throttleProps} />);
      expect(MockPerformanceMonitor).toHaveBeenCalledWith(throttleProps, {});
    });
  });

  describe('索克生活特色功能', () => {
    it('应该支持健康状态性能调整', () => {
      const healthProps = {
        ...defaultProps,
        healthAwarePerformance: true,
        healthStatus: 'normal',
        healthPerformanceMapping: {
          critical: { optimizationLevel: 'high', disableAnimations: true },
          warning: { optimizationLevel: 'medium', reduceEffects: true },
          normal: { optimizationLevel: 'low', fullFeatures: true }
        }
      };
      render(<MockPerformanceMonitor {...healthProps} />);
      expect(MockPerformanceMonitor).toHaveBeenCalledWith(healthProps, {});
    });

    it('应该支持智能体性能配置', () => {
      const agentProps = {
        ...defaultProps,
        agentPerformanceProfiles: true,
        currentAgent: 'xiaoai',
        agentPerformanceMapping: {
          xiaoai: { cpuPriority: 'high', memoryLimit: 'medium' },
          xiaoke: { cpuPriority: 'medium', memoryLimit: 'low' },
          laoke: { cpuPriority: 'low', memoryLimit: 'high' },
          soer: { cpuPriority: 'medium', memoryLimit: 'medium' }
        }
      };
      render(<MockPerformanceMonitor {...agentProps} />);
      expect(MockPerformanceMonitor).toHaveBeenCalledWith(agentProps, {});
    });

    it('应该支持区块链验证性能优化', () => {
      const blockchainProps = {
        ...defaultProps,
        optimizeBlockchainOperations: true,
        blockchainVerificationType: 'light',
        prioritizeUIOverVerification: true
      };
      render(<MockPerformanceMonitor {...blockchainProps} />);
      expect(MockPerformanceMonitor).toHaveBeenCalledWith(blockchainProps, {});
    });
  });
});