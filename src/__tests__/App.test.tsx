/**
 * App组件测试
 */

import React from 'react';
import { render } from '@testing-library/react-native';
import { LoadingScreen } from '../components/common/LoadingScreen';

describe('App Components', () => {
  it('LoadingScreen renders correctly', () => {
    const { getByText } = render(<LoadingScreen message="测试加载中..." />);
    expect(getByText('测试加载中...')).toBeTruthy();
  });

  it('LoadingScreen renders with default message', () => {
    const { getByText } = render(<LoadingScreen />);
    expect(getByText('加载中...')).toBeTruthy();
  });
});
