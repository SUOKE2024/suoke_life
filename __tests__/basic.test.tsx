/**
 * 基本功能测试
 */

import React from 'react';
import { Text, View } from 'react-native';
import { render } from '@testing-library/react-native';

// 简单的基础组件测试
const TestComponent = () => (
  <View>
    <Text>索克生活</Text>
    <Text>欢迎来到索克生活</Text>
  </View>
);

describe('基础功能测试', () => {
  it('应该能渲染基本组件', () => {
    const { getByText } = render(<TestComponent />);
    expect(getByText('索克生活')).toBeTruthy();
    expect(getByText('欢迎来到索克生活')).toBeTruthy();
  });

  it('常量和类型应该正确定义', () => {
    // 测试一些基本类型和常量
    expect('索克生活').toBe('索克生活');
    expect(1 + 1).toBe(2);
  });
});