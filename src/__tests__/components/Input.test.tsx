import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import { Input } from '../../components/common/Input';

describe('Input Component', () => {
  const defaultProps = {
    placeholder: '请输入内容',
    value: '',
    onChangeText: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('基础功能', () => {
    it('应该正确渲染输入框', () => {
      const { getByPlaceholderText } = render(<Input {...defaultProps} />);
      expect(getByPlaceholderText('请输入内容')).toBeTruthy();
    });

    it('应该显示输入的值', () => {
      const { getByDisplayValue } = render(
        <Input {...defaultProps} value="测试内容" />
      );
      expect(getByDisplayValue('测试内容')).toBeTruthy();
    });

    it('应该响应文本变化事件', () => {
      const onChangeText = jest.fn();
      const { getByPlaceholderText } = render(
        <Input {...defaultProps} onChangeText={onChangeText} />
      );
      
      const input = getByPlaceholderText('请输入内容');
      fireEvent.changeText(input, '新内容');
      
      expect(onChangeText).toHaveBeenCalledWith('新内容');
    });

    it('应该支持密码输入模式', () => {
      const { getByPlaceholderText } = render(
        <Input {...defaultProps} secureTextEntry placeholder="密码" />
      );
      
      const input = getByPlaceholderText('密码');
      expect(input.props.secureTextEntry).toBe(true);
    });

    it('应该支持禁用状态', () => {
      const { getByPlaceholderText } = render(
        <Input {...defaultProps} editable={false} />
      );
      
      const input = getByPlaceholderText('请输入内容');
      expect(input.props.editable).toBe(false);
    });
  });

  describe('样式和外观', () => {
    it('应该应用自定义样式', () => {
      const customStyle = { backgroundColor: 'red' };
      const { getByPlaceholderText } = render(
        <Input {...defaultProps} style={customStyle} />
      );
      
      const input = getByPlaceholderText('请输入内容');
      expect(input.props.style).toEqual(expect.arrayContaining([
        expect.objectContaining(customStyle)
      ]));
    });

    it('应该支持多行输入', () => {
      const { getByPlaceholderText } = render(
        <Input {...defaultProps} multiline numberOfLines={4} />
      );
      
      const input = getByPlaceholderText('请输入内容');
      expect(input.props.multiline).toBe(true);
      expect(input.props.numberOfLines).toBe(4);
    });
  });

  describe('键盘和输入类型', () => {
    it('应该支持不同的键盘类型', () => {
      const { getByPlaceholderText } = render(
        <Input {...defaultProps} keyboardType="email-address" />
      );
      
      const input = getByPlaceholderText('请输入内容');
      expect(input.props.keyboardType).toBe('email-address');
    });

    it('应该支持自动完成类型', () => {
      const { getByPlaceholderText } = render(
        <Input {...defaultProps} autoComplete="email" />
      );
      
      const input = getByPlaceholderText('请输入内容');
      expect(input.props.autoComplete).toBe('email');
    });
  });

  describe('事件处理', () => {
    it('应该处理焦点事件', () => {
      const onFocus = jest.fn();
      const { getByPlaceholderText } = render(
        <Input {...defaultProps} onFocus={onFocus} />
      );
      
      const input = getByPlaceholderText('请输入内容');
      fireEvent(input, 'focus');
      
      expect(onFocus).toHaveBeenCalled();
    });

    it('应该处理失焦事件', () => {
      const onBlur = jest.fn();
      const { getByPlaceholderText } = render(
        <Input {...defaultProps} onBlur={onBlur} />
      );
      
      const input = getByPlaceholderText('请输入内容');
      fireEvent(input, 'blur');
      
      expect(onBlur).toHaveBeenCalled();
    });

    it('应该处理提交事件', () => {
      const onSubmitEditing = jest.fn();
      const { getByPlaceholderText } = render(
        <Input {...defaultProps} onSubmitEditing={onSubmitEditing} />
      );
      
      const input = getByPlaceholderText('请输入内容');
      fireEvent(input, 'submitEditing');
      
      expect(onSubmitEditing).toHaveBeenCalled();
    });
  });

  describe('可访问性', () => {
    it('应该支持可访问性标签', () => {
      const { getByLabelText } = render(
        <Input {...defaultProps} accessibilityLabel="用户名输入框" />
      );
      
      expect(getByLabelText('用户名输入框')).toBeTruthy();
    });

    it('应该支持可访问性提示', () => {
      const { getByPlaceholderText } = render(
        <Input {...defaultProps} accessibilityHint="请输入您的用户名" />
      );
      
      const input = getByPlaceholderText('请输入内容');
      expect(input.props.accessibilityHint).toBe('请输入您的用户名');
    });
  });

  describe('性能测试', () => {
    it('应该在合理时间内渲染', () => {
      const startTime = performance.now();
      render(<Input {...defaultProps} />);
      const endTime = performance.now();
      
      expect(endTime - startTime).toBeLessThan(100);
    });

    it('应该高效处理文本变化', () => {
      const onChangeText = jest.fn();
      const { getByPlaceholderText } = render(
        <Input {...defaultProps} onChangeText={onChangeText} />
      );
      
      const input = getByPlaceholderText('请输入内容');
      const startTime = performance.now();
      
      // 模拟快速输入
      for (let i = 0; i < 10; i++) {
        fireEvent.changeText(input, `文本${i}`);
      }
      
      const endTime = performance.now();
      expect(endTime - startTime).toBeLessThan(100);
      expect(onChangeText).toHaveBeenCalledTimes(10);
    });
  });

  describe('边界情况', () => {
    it('应该处理空值', () => {
      const { getByPlaceholderText } = render(
        <Input {...defaultProps} value={null as any} />
      );
      
      expect(getByPlaceholderText('请输入内容')).toBeTruthy();
    });

    it('应该处理长文本', () => {
      const longText = 'a'.repeat(1000);
      const { getByDisplayValue } = render(
        <Input {...defaultProps} value={longText} />
      );
      
      expect(getByDisplayValue(longText)).toBeTruthy();
    });

    it('应该处理特殊字符', () => {
      const specialText = '!@#$%^&*()_+{}|:"<>?[]\\;\',./ 中文 🚀';
      const onChangeText = jest.fn();
      const { getByPlaceholderText } = render(
        <Input {...defaultProps} onChangeText={onChangeText} />
      );
      
      const input = getByPlaceholderText('请输入内容');
      fireEvent.changeText(input, specialText);
      
      expect(onChangeText).toHaveBeenCalledWith(specialText);
    });
  });
}); 