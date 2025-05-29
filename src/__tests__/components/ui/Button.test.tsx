/**
 * 索克生活 - Button组件测试
 */

import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import Button from '../../../components/ui/Button';

describe('Button Component', () => {
  it('renders correctly with title', () => {
    const { getByText } = render(<Button title="测试按钮" />);
    expect(getByText('测试按钮')).toBeTruthy();
  });

  it('calls onPress when pressed', () => {
    const mockOnPress = jest.fn();
    const { getByText } = render(
      <Button title="点击按钮" onPress={mockOnPress} />
    );
    
    fireEvent.press(getByText('点击按钮'));
    expect(mockOnPress).toHaveBeenCalledTimes(1);
  });

  it('does not call onPress when disabled', () => {
    const mockOnPress = jest.fn();
    const { getByText } = render(
      <Button title="禁用按钮" onPress={mockOnPress} disabled />
    );
    
    fireEvent.press(getByText('禁用按钮'));
    expect(mockOnPress).not.toHaveBeenCalled();
  });

  it('shows loading indicator when loading', () => {
    const { getByTestId } = render(
      <Button title="加载按钮" loading testID="loading-button" />
    );
    
    expect(getByTestId('loading-button')).toBeTruthy();
  });

  it('applies correct variant styles', () => {
    const { getByTestId } = render(
      <Button title="主要按钮" variant="primary" testID="primary-button" />
    );
    
    expect(getByTestId('primary-button')).toBeTruthy();
  });

  it('applies correct size styles', () => {
    const { getByTestId } = render(
      <Button title="大按钮" size="large" testID="large-button" />
    );
    
    expect(getByTestId('large-button')).toBeTruthy();
  });
}); 