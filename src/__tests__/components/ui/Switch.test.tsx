/**
 * Switch组件单元测试
 */

import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import Switch from '../../../components/ui/Switch';

describe('Switch组件', () => {
  it('应该正确渲染', () => {
    const mockOnValueChange = jest.fn();
    const { getByTestId } = render(
      <Switch
        value={false}
        onValueChange={mockOnValueChange}
        testID="test-switch"
      />
    );

    expect(getByTestId('test-switch')).toBeTruthy();
  });

  it('应该显示标签', () => {
    const mockOnValueChange = jest.fn();
    const { getByText } = render(
      <Switch
        value={false}
        onValueChange={mockOnValueChange}
        label="测试标签"
      />
    );

    expect(getByText('测试标签')).toBeTruthy();
  });

  it('应该显示描述', () => {
    const mockOnValueChange = jest.fn();
    const { getByText } = render(
      <Switch
        value={false}
        onValueChange={mockOnValueChange}
        description="测试描述"
      />
    );

    expect(getByText('测试描述')).toBeTruthy();
  });

  it('应该处理值变化', () => {
    const mockOnValueChange = jest.fn();
    const { getByTestId } = render(
      <Switch
        value={false}
        onValueChange={mockOnValueChange}
        testID="test-switch"
      />
    );

    fireEvent(getByTestId('test-switch'), 'valueChange', true);
    expect(mockOnValueChange).toHaveBeenCalledWith(true);
  });

  it('应该正确渲染禁用状态', () => {
    const mockOnValueChange = jest.fn();
    const { getByTestId } = render(
      <Switch
        value={false}
        onValueChange={mockOnValueChange}
        disabled={true}
        testID="test-switch"
      />
    );

    expect(getByTestId('test-switch')).toBeTruthy();
  });
}); 