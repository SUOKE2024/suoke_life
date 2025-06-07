import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import TCMDiagnosisPanel from '../TCMDiagnosisPanel.tsx';
const mockStore = configureStore({
  reducer: { root: (state = {}) => state }
});
const renderWithProvider = (component: React.ReactElement) => {
  return render(<Provider store={mockStore}>{component}</Provider>);
};
describe('TCMDiagnosisPanel', () => {
  it('应该正确渲染', () => {
    const { getByTestId } = renderWithProvider(<TCMDiagnosisPanel />);
    expect(getByTestId('tcmdiagnosispanel')).toBeTruthy();
  });
  it('应该处理用户交互', () => {
    const mockOnPress = jest.fn();
    const { getByTestId } = renderWithProvider(
      <TCMDiagnosisPanel onPress={mockOnPress} />
    );
        fireEvent.press(getByTestId('tcmdiagnosispanel'));
    expect(mockOnPress).toHaveBeenCalled();
  });
  it('应该正确显示属性', () => {
    const testProps = {
      title: "测试标题",
      description: '测试描述'
    };
        const { getByText } = renderWithProvider(<TCMDiagnosisPanel {...testProps} />);
    expect(getByText(testProps.title)).toBeTruthy();
    expect(getByText(testProps.description)).toBeTruthy();
  });
  it('应该处理错误状态', () => {
    const { getByTestId } = renderWithProvider(
      <TCMDiagnosisPanel error="测试错误" />
    );
        expect(getByTestId('error-message')).toBeTruthy();
  });
  it('应该处理加载状态', () => {
    const { getByTestId } = renderWithProvider(
      <TCMDiagnosisPanel loading={true} />
    );
        expect(getByTestId('loading-indicator')).toBeTruthy();
  });
});
