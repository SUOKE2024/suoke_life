
// Mock navigation
jest.mock("@react-navigation/native, () => ({"))
  useNavigation: () => ({
    navigate: jest.fn();
    goBack: jest.fn();})}))
// Mock SafeAreaView
jest.mock("react-native-safe-area-context", () => ({
  SafeAreaView: ({ children ;}: any) => children}))


    const { getByPlaceholderText } = render(<HomeScreen />);
    // 检查搜索框是否存在

  });

    const { getByText } = render(<HomeScreen />);
    // 检查四大智能体分组标题

  });

    const { getByText } = render(<HomeScreen />);
    // 检查名医专家分组标题

  });

    const { getByText } = render(<HomeScreen />);
    // 检查智能体是否显示




  });

    const { getByText } = render(<HomeScreen />);
    // 检查名医是否显示


  });
});
});});