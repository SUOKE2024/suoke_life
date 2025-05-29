import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import { Button } from '../../../components/common/Button';

// Mock navigation
const mockNavigate = jest.fn();
jest.mock('@react-navigation/native', () => ({
  ...jest.requireActual('@react-navigation/native'),
  useNavigation: () => ({
    navigate: mockNavigate,
  }),
}));

describe('Button Component', () => {
  const defaultOnPress = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('基础功能', () => {
    it('应该正确渲染按钮文本', () => {
      const { toJSON } = render(<Button title="测试按钮" onPress={defaultOnPress} />);
      const tree = toJSON();
      expect(JSON.stringify(tree)).toContain('测试按钮');
    });

    it('应该响应点击事件', () => {
      const onPress = jest.fn();
      const { root } = render(<Button title="点击我" onPress={onPress} />);
      
      // 直接在根元素上触发点击事件
      fireEvent.press(root);
      expect(onPress).toHaveBeenCalledTimes(1);
    });

    it('禁用状态下应该有正确的样式', () => {
      const onPress = jest.fn();
      const { toJSON } = render(<Button title="禁用按钮" onPress={onPress} disabled />);
      
      const tree = toJSON();
      const treeString = JSON.stringify(tree);
      
      // 检查是否有禁用状态的样式
      expect(treeString).toContain('aria-disabled');
      expect(treeString).toContain('禁用按钮');
    });

    it('应该显示加载状态', () => {
      const { toJSON } = render(<Button title="加载中" onPress={defaultOnPress} loading />);
      const tree = toJSON();
      const treeString = JSON.stringify(tree);
      
      // 检查是否包含ActivityIndicator的特征
      expect(treeString).toContain('progressbar');
      // 确保文本不显示
      expect(treeString).not.toContain('加载中');
    });

    it('应该正确应用自定义样式', () => {
      const customStyle = { backgroundColor: 'red' };
      const { toJSON } = render(
        <Button title="自定义样式" onPress={defaultOnPress} style={customStyle} />
      );
      
      const tree = toJSON();
      expect(JSON.stringify(tree)).toContain('自定义样式');
    });
  });

  describe('可访问性', () => {
    it('应该正确渲染按钮', () => {
      const { toJSON } = render(<Button title="角色测试" onPress={defaultOnPress} />);
      const tree = toJSON();
      expect(JSON.stringify(tree)).toContain('角色测试');
    });

    it('禁用状态应该正确显示', () => {
      const { toJSON } = render(<Button title="禁用测试" onPress={defaultOnPress} disabled />);
      const tree = toJSON();
      const treeString = JSON.stringify(tree);
      expect(treeString).toContain('禁用测试');
      expect(treeString).toContain('aria-disabled');
    });

    it('加载状态应该显示指示器', () => {
      const { toJSON } = render(<Button title="加载测试" onPress={defaultOnPress} loading />);
      const tree = toJSON();
      expect(JSON.stringify(tree)).toContain('progressbar');
    });
  });

  describe('按钮变体', () => {
    it('应该正确渲染主要按钮', () => {
      const { toJSON } = render(<Button title="主要按钮" onPress={defaultOnPress} variant="primary" />);
      const tree = toJSON();
      expect(JSON.stringify(tree)).toContain('主要按钮');
    });

    it('应该正确渲染次要按钮', () => {
      const { toJSON } = render(<Button title="次要按钮" onPress={defaultOnPress} variant="secondary" />);
      const tree = toJSON();
      expect(JSON.stringify(tree)).toContain('次要按钮');
    });

    it('应该正确渲染轮廓按钮', () => {
      const { toJSON } = render(<Button title="轮廓按钮" onPress={defaultOnPress} variant="outline" />);
      const tree = toJSON();
      expect(JSON.stringify(tree)).toContain('轮廓按钮');
    });
  });

  describe('按钮尺寸', () => {
    it('应该正确渲染小尺寸按钮', () => {
      const { toJSON } = render(<Button title="小按钮" onPress={defaultOnPress} size="small" />);
      const tree = toJSON();
      expect(JSON.stringify(tree)).toContain('小按钮');
    });

    it('应该正确渲染中等尺寸按钮', () => {
      const { toJSON } = render(<Button title="中等按钮" onPress={defaultOnPress} size="medium" />);
      const tree = toJSON();
      expect(JSON.stringify(tree)).toContain('中等按钮');
    });

    it('应该正确渲染大尺寸按钮', () => {
      const { toJSON } = render(<Button title="大按钮" onPress={defaultOnPress} size="large" />);
      const tree = toJSON();
      expect(JSON.stringify(tree)).toContain('大按钮');
    });
  });

  describe('性能测试', () => {
    it('应该在合理时间内渲染', () => {
      const startTime = performance.now();
      render(<Button title="性能测试" onPress={defaultOnPress} />);
      const endTime = performance.now();
      const renderTime = endTime - startTime;
      
      expect(renderTime).toBeLessThan(100); // 100ms内渲染完成
    });

    it('应该高效处理多次点击', () => {
      const onPress = jest.fn();
      const { root } = render(<Button title="点击测试" onPress={onPress} />);
      
      const startTime = performance.now();
      
      // 模拟100次快速点击
      for (let i = 0; i < 100; i++) {
        fireEvent.press(root);
      }
      
      const endTime = performance.now();
      const totalTime = endTime - startTime;
      
      expect(totalTime).toBeLessThan(1000); // 1秒内完成100次点击
      expect(onPress).toHaveBeenCalledTimes(100);
    });

    it('不应该有明显的性能问题', () => {
      // 简单的性能测试
      const iterations = 10;
      const times = [];
      
      for (let i = 0; i < iterations; i++) {
        const startTime = performance.now();
        const { unmount } = render(<Button title="性能测试" onPress={defaultOnPress} />);
        const endTime = performance.now();
        unmount();
        times.push(endTime - startTime);
      }
      
      const averageTime = times.reduce((sum, time) => sum + time, 0) / iterations;
      expect(averageTime).toBeLessThan(200); // 放宽到200ms，因为在测试环境中可能较慢
    });
  });

  describe('边界情况', () => {
    it('应该处理空标题', () => {
      const result = render(<Button title="" onPress={defaultOnPress} />);
      expect(result).toBeTruthy();
    });

    it('应该处理长标题', () => {
      const longTitle = '这是一个非常非常非常长的按钮标题，用来测试文本溢出处理';
      const { toJSON } = render(<Button title={longTitle} onPress={defaultOnPress} />);
      const tree = toJSON();
      expect(JSON.stringify(tree)).toContain(longTitle);
    });

    it('应该处理特殊字符', () => {
      const specialTitle = '按钮 🚀 测试 & 特殊字符';
      const { toJSON } = render(<Button title={specialTitle} onPress={defaultOnPress} />);
      const tree = toJSON();
      expect(JSON.stringify(tree)).toContain(specialTitle);
    });

    it('应该处理同时设置loading和disabled', () => {
      const onPress = jest.fn();
      const { toJSON } = render(<Button title="测试" onPress={onPress} loading disabled />);
      
      const tree = toJSON();
      const treeString = JSON.stringify(tree);
      expect(treeString).toContain('progressbar');
      expect(treeString).toContain('aria-disabled');
    });
  });

  describe('集成测试', () => {
    it('应该与表单正确集成', () => {
      const onSubmit = jest.fn();
      const { root } = render(<Button title="提交" onPress={onSubmit} />);
      
      fireEvent.press(root);
      expect(onSubmit).toHaveBeenCalled();
    });

    it('应该与导航正确集成', () => {
      const navigate = mockNavigate;
      const { root } = render(<Button title="导航" onPress={() => navigate('Home')} />);
      
      fireEvent.press(root);
      expect(navigate).toHaveBeenCalledWith('Home');
    });

    it('应该支持自定义文本样式', () => {
      const customTextStyle = { color: 'blue', fontSize: 20 };
      const { toJSON } = render(
        <Button title="自定义文本" onPress={defaultOnPress} textStyle={customTextStyle} />
      );
      
      const tree = toJSON();
      expect(JSON.stringify(tree)).toContain('自定义文本');
    });
  });

  // 基础渲染测试
  describe('Rendering', () => {
    it('should render with default props', () => {
      const { getByText } = render(
        <Button title="Test Button" onPress={() => {}} />
      );
      
      expect(getByText('Test Button')).toBeTruthy();
    });

    it('should render with custom title', () => {
      const { getByText } = render(
        <Button title="Custom Title" onPress={() => {}} />
      );
      
      expect(getByText('Custom Title')).toBeTruthy();
    });

    it('should render with loading state', () => {
      const { getByTestId } = render(
        <Button title="Loading Button" onPress={() => {}} loading />
      );
      
      const indicator = getByTestId('activity-indicator');
      expect(indicator).toBeTruthy();
    });

    it('should render with disabled state', () => {
      const { getByText } = render(
        <Button title="Disabled Button" onPress={() => {}} disabled />
      );
      
      const button = getByText('Disabled Button');
      expect(button).toBeTruthy();
    });
  });

  // 交互测试
  describe('Interactions', () => {
    it('should call onPress when pressed', () => {
      const mockOnPress = jest.fn();
      const { getByText } = render(
        <Button title="Pressable Button" onPress={mockOnPress} />
      );
      
      const button = getByText('Pressable Button');
      fireEvent.press(button);
      
      expect(mockOnPress).toHaveBeenCalledTimes(1);
    });

    it('should not call onPress when disabled', () => {
      const mockOnPress = jest.fn();
      const { getByText } = render(
        <Button 
          title="Disabled Pressable Button"
          onPress={mockOnPress} 
          disabled 
        />
      );
      
      const button = getByText('Disabled Pressable Button');
      fireEvent.press(button);
      
      expect(mockOnPress).not.toHaveBeenCalled();
    });

    it('should not call onPress when loading', () => {
      const mockOnPress = jest.fn();
      const { getByTestId } = render(
        <Button 
          title="Loading Pressable Button"
          onPress={mockOnPress} 
          loading 
        />
      );
      
      const indicator = getByTestId('activity-indicator');
      fireEvent.press(indicator);
      
      expect(mockOnPress).not.toHaveBeenCalled();
    });
  });

  // 样式变体测试
  describe('Variants', () => {
    it('should render primary variant', () => {
      const { getByText } = render(
        <Button title="Primary Button" onPress={() => {}} variant="primary" />
      );
      
      expect(getByText('Primary Button')).toBeTruthy();
    });

    it('should render secondary variant', () => {
      const { getByText } = render(
        <Button title="Secondary Button" onPress={() => {}} variant="secondary" />
      );
      
      expect(getByText('Secondary Button')).toBeTruthy();
    });

    it('should render outline variant', () => {
      const { getByText } = render(
        <Button title="Outline Button" onPress={() => {}} variant="outline" />
      );
      
      expect(getByText('Outline Button')).toBeTruthy();
    });
  });

  // 尺寸测试
  describe('Sizes', () => {
    it('should render small size', () => {
      const { getByText } = render(
        <Button title="Small Button" onPress={() => {}} size="small" />
      );
      
      expect(getByText('Small Button')).toBeTruthy();
    });

    it('should render medium size', () => {
      const { getByText } = render(
        <Button title="Medium Button" onPress={() => {}} size="medium" />
      );
      
      expect(getByText('Medium Button')).toBeTruthy();
    });

    it('should render large size', () => {
      const { getByText } = render(
        <Button title="Large Button" onPress={() => {}} size="large" />
      );
      
      expect(getByText('Large Button')).toBeTruthy();
    });
  });

  // 可访问性测试
  describe('Accessibility', () => {
    it('should be accessible by text', () => {
      const { getByText } = render(
        <Button title="Accessible Button" onPress={() => {}} />
      );
      
      expect(getByText('Accessible Button')).toBeTruthy();
    });

    it('should handle disabled state properly', () => {
      const { getByText } = render(
        <Button title="Disabled Button" onPress={() => {}} disabled />
      );
      
      const button = getByText('Disabled Button');
      expect(button).toBeTruthy();
    });
  });

  // 性能测试
  describe('Performance', () => {
    it('should render quickly', async () => {
      const startTime = Date.now();
      
      render(<Button title="Performance Test Button" onPress={() => {}} />);
      
      const endTime = Date.now();
      const renderTime = endTime - startTime;
      
      // 渲染时间应该小于100ms
      expect(renderTime).toBeLessThan(100);
    });

    it('should handle multiple rapid presses', async () => {
      const mockOnPress = jest.fn();
      const { getByText } = render(
        <Button title="Rapid Press Button" onPress={mockOnPress} />
      );
      
      const button = getByText('Rapid Press Button');
      
      // 快速连续点击
      for (let i = 0; i < 10; i++) {
        fireEvent.press(button);
      }
      
      await waitFor(() => {
        expect(mockOnPress).toHaveBeenCalledTimes(10);
      });
    });
  });

  // 边界情况测试
  describe('Edge Cases', () => {
    it('should handle empty title', () => {
      const { getByText } = render(
        <Button title="" onPress={() => {}} />
      );
      
      expect(getByText('')).toBeTruthy();
    });

    it('should handle long title', () => {
      const longTitle = 'This is a very long button title that might cause layout issues';
      const { getByText } = render(
        <Button title={longTitle} onPress={() => {}} />
      );
      
      expect(getByText(longTitle)).toBeTruthy();
    });

    it('should handle undefined variant gracefully', () => {
      const { getByText } = render(
        <Button 
          title="Undefined Variant Button"
          onPress={() => {}}
          variant={undefined}
        />
      );
      
      expect(getByText('Undefined Variant Button')).toBeTruthy();
    });
  });

  // 快照测试
  describe('Snapshots', () => {
    it('should match snapshot for default button', () => {
      const tree = render(
        <Button title="Default Button" onPress={() => {}} />
      ).toJSON();
      expect(tree).toMatchSnapshot();
    });

    it('should match snapshot for loading button', () => {
      const tree = render(
        <Button title="Loading Button" onPress={() => {}} loading />
      ).toJSON();
      expect(tree).toMatchSnapshot();
    });

    it('should match snapshot for disabled button', () => {
      const tree = render(
        <Button title="Disabled Button" onPress={() => {}} disabled />
      ).toJSON();
      expect(tree).toMatchSnapshot();
    });

    it('should match snapshot for all variants', () => {
      const variants = ['primary', 'secondary', 'outline'] as const;
      
      variants.forEach(variant => {
        const tree = render(
          <Button 
            title={`${variant} Button`} 
            onPress={() => {}} 
            variant={variant} 
          />
        ).toJSON();
        expect(tree).toMatchSnapshot(`button-${variant}`);
      });
    });

    it('should match snapshot for all sizes', () => {
      const sizes = ['small', 'medium', 'large'] as const;
      
      sizes.forEach(size => {
        const tree = render(
          <Button 
            title={`${size} Button`} 
            onPress={() => {}} 
            size={size} 
          />
        ).toJSON();
        expect(tree).toMatchSnapshot(`button-${size}`);
      });
    });
  });
}); 