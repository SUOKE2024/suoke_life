import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import AuthInput from '../AuthInput.tsx';
const mockStore = configureStore({
  reducer: { root: (state = {}) => state }
});
const renderWithProvider = (component: React.ReactElement) => {
  return render(<Provider store={mockStore}>{component}</Provider>);
};
describe('AuthInput', () => {
  it('应该正确渲染', () => {
    const { getByTestId } = renderWithProvider(<AuthInput />);
    expect(getByTestId('authinput')).toBeTruthy();
  });
  it('应该处理用户交互', () => {
    const mockOnPress = jest.fn();
    const { getByTestId } = renderWithProvider(
      <AuthInput onPress={mockOnPress} />
    );
        fireEvent.press(getByTestId('authinput'));
    expect(mockOnPress).toHaveBeenCalled();
  });
  it('应该正确显示属性', () => {
    const testProps = {
      title: "测试标题",
      description: '测试描述'
    };
        const { getByText } = renderWithProvider(<AuthInput {...testProps} />);
    expect(getByText(testProps.title)).toBeTruthy();
    expect(getByText(testProps.description)).toBeTruthy();
  });
  it('应该处理错误状态', () => {
    const { getByTestId } = renderWithProvider(
      <AuthInput error="测试错误" />
    );
        expect(getByTestId('error-message')).toBeTruthy();
  });
  it('应该处理加载状态', () => {
    const { getByTestId } = renderWithProvider(
      <AuthInput loading={true} />
    );
        expect(getByTestId('loading-indicator')).toBeTruthy();
  });
});
