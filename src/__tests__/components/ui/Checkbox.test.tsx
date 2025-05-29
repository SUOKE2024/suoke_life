/**
 * Checkbox组件单元测试
 */

import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import Checkbox from '../../../components/ui/Checkbox';

describe('Checkbox组件', () => {
  it('应该正确渲染', () => {
    const mockOnPress = jest.fn();
    const { getByTestId } = render(
      <Checkbox
        checked={false}
        onPress={mockOnPress}
        testID="test-checkbox"
      />
    );

    expect(getByTestId('test-checkbox')).toBeTruthy();
  });

  it('应该显示标签', () => {
    const mockOnPress = jest.fn();
    const { getByText } = render(
      <Checkbox
        checked={false}
        onPress={mockOnPress}
        label="测试标签"
      />
    );

    expect(getByText('测试标签')).toBeTruthy();
  });

  it('应该处理点击事件', () => {
    const mockOnPress = jest.fn();
    const { getByTestId } = render(
      <Checkbox
        checked={false}
        onPress={mockOnPress}
        testID="test-checkbox"
      />
    );

    fireEvent.press(getByTestId('test-checkbox'));
    expect(mockOnPress).toHaveBeenCalledWith(true);
  });

  it('选中状态下点击应该取消选中', () => {
    const mockOnPress = jest.fn();
    const { getByTestId } = render(
      <Checkbox
        checked={true}
        onPress={mockOnPress}
        testID="test-checkbox"
      />
    );

    fireEvent.press(getByTestId('test-checkbox'));
    expect(mockOnPress).toHaveBeenCalledWith(false);
  });

  it('禁用状态下不应该响应点击', () => {
    const mockOnPress = jest.fn();
    const { getByTestId } = render(
      <Checkbox
        checked={false}
        onPress={mockOnPress}
        disabled={true}
        testID="test-checkbox"
      />
    );

    fireEvent.press(getByTestId('test-checkbox'));
    expect(mockOnPress).not.toHaveBeenCalled();
  });

  it('应该支持不确定状态', () => {
    const mockOnPress = jest.fn();
    const { getByTestId } = render(
      <Checkbox
        checked={false}
        onPress={mockOnPress}
        indeterminate={true}
        testID="test-checkbox"
      />
    );

    expect(getByTestId('test-checkbox')).toBeTruthy();
  });
}); 