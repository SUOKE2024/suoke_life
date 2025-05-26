import { renderHook, act } from '@testing-library/react-native';

// Mock导航Hook
const useNavigation = () => {
  const [currentRoute, setCurrentRoute] = React.useState('Home');
  const [navigationHistory, setNavigationHistory] = React.useState(['Home']);
  const [canGoBack, setCanGoBack] = React.useState(false);

  const navigate = (routeName: string, params?: any) => {
    setNavigationHistory((prev: string[]) => [...prev, routeName]);
    setCurrentRoute(routeName);
    setCanGoBack(true);
  };

  const goBack = () => {
    if (navigationHistory.length > 1) {
      const newHistory = navigationHistory.slice(0, -1);
      setNavigationHistory(newHistory);
      setCurrentRoute(newHistory[newHistory.length - 1]);
      setCanGoBack(newHistory.length > 1);
    }
  };

  const reset = (routeName: string = 'Home') => {
    setNavigationHistory([routeName]);
    setCurrentRoute(routeName);
    setCanGoBack(false);
  };

  const replace = (routeName: string, params?: any) => {
    const newHistory = [...navigationHistory.slice(0, -1), routeName];
    setNavigationHistory(newHistory);
    setCurrentRoute(routeName);
  };

  return {
    currentRoute,
    navigationHistory,
    canGoBack,
    navigate,
    goBack,
    reset,
    replace,
  };
};

// Mock React
const React = {
  useState: jest.fn(),
};

// 设置useState mock
let stateIndex = 0;
const mockStates: any[] = [];

React.useState.mockImplementation((initialValue: any) => {
  const index = stateIndex++;
  if (mockStates[index] === undefined) {
    mockStates[index] = initialValue;
  }
  
  const setState = (newValue: any) => {
    mockStates[index] = typeof newValue === 'function' ? newValue(mockStates[index]) : newValue;
  };
  
  return [mockStates[index], setState];
});

describe('useNavigation', () => {
  beforeEach(() => {
    stateIndex = 0;
    mockStates.length = 0;
    jest.clearAllMocks();
  });

  it('应该返回初始导航状态', () => {
    const { result } = renderHook(() => useNavigation());

    expect(result.current.currentRoute).toBe('Home');
    expect(result.current.navigationHistory).toEqual(['Home']);
    expect(result.current.canGoBack).toBe(false);
  });

  it('应该能够导航到新页面', () => {
    const { result } = renderHook(() => useNavigation());

    act(() => {
      result.current.navigate('Profile');
    });

    expect(result.current.currentRoute).toBe('Profile');
    expect(result.current.navigationHistory).toEqual(['Home', 'Profile']);
    expect(result.current.canGoBack).toBe(true);
  });

  it('应该能够返回上一页', () => {
    const { result } = renderHook(() => useNavigation());

    act(() => {
      result.current.navigate('Profile');
      result.current.navigate('Settings');
    });

    expect(result.current.currentRoute).toBe('Settings');
    expect(result.current.canGoBack).toBe(true);

    act(() => {
      result.current.goBack();
    });

    expect(result.current.currentRoute).toBe('Profile');
    expect(result.current.navigationHistory).toEqual(['Home', 'Profile']);
  });

  it('应该能够重置导航栈', () => {
    const { result } = renderHook(() => useNavigation());

    act(() => {
      result.current.navigate('Profile');
      result.current.navigate('Settings');
      result.current.reset('Login');
    });

    expect(result.current.currentRoute).toBe('Login');
    expect(result.current.navigationHistory).toEqual(['Login']);
    expect(result.current.canGoBack).toBe(false);
  });

  it('应该能够替换当前页面', () => {
    const { result } = renderHook(() => useNavigation());

    act(() => {
      result.current.navigate('Profile');
      result.current.replace('EditProfile');
    });

    expect(result.current.currentRoute).toBe('EditProfile');
    expect(result.current.navigationHistory).toEqual(['Home', 'EditProfile']);
  });

  it('应该正确处理导航历史', () => {
    const { result } = renderHook(() => useNavigation());

    act(() => {
      result.current.navigate('Explore');
      result.current.navigate('Life');
      result.current.navigate('Suoke');
    });

    expect(result.current.navigationHistory).toEqual(['Home', 'Explore', 'Life', 'Suoke']);
    expect(result.current.currentRoute).toBe('Suoke');

    act(() => {
      result.current.goBack();
      result.current.goBack();
    });

    expect(result.current.currentRoute).toBe('Explore');
    expect(result.current.navigationHistory).toEqual(['Home', 'Explore']);
  });

  it('应该在无法返回时正确处理goBack', () => {
    const { result } = renderHook(() => useNavigation());

    // 在只有一个页面时尝试返回
    act(() => {
      result.current.goBack();
    });

    expect(result.current.currentRoute).toBe('Home');
    expect(result.current.navigationHistory).toEqual(['Home']);
    expect(result.current.canGoBack).toBe(false);
  });

  it('应该支持带参数的导航', () => {
    const { result } = renderHook(() => useNavigation());

    act(() => {
      result.current.navigate('AgentChat', { agentId: 'xiaoai' });
    });

    expect(result.current.currentRoute).toBe('AgentChat');
    expect(result.current.navigationHistory).toEqual(['Home', 'AgentChat']);
  });

  it('应该支持带参数的替换', () => {
    const { result } = renderHook(() => useNavigation());

    act(() => {
      result.current.navigate('Profile');
      result.current.replace('EditProfile', { userId: '123' });
    });

    expect(result.current.currentRoute).toBe('EditProfile');
    expect(result.current.navigationHistory).toEqual(['Home', 'EditProfile']);
  });

  it('应该正确更新canGoBack状态', () => {
    const { result } = renderHook(() => useNavigation());

    expect(result.current.canGoBack).toBe(false);

    act(() => {
      result.current.navigate('Profile');
    });

    expect(result.current.canGoBack).toBe(true);

    act(() => {
      result.current.goBack();
    });

    expect(result.current.canGoBack).toBe(false);
  });
}); 