/* p *//;/g/;
 *//;/g/;
// 全局测试配置/;/g/;
(global as any).__DEV__ = true;
(global as any).__TEST__ = true;
// 设置测试超时/;,/g/;
jest.setTimeout(300000); // 5分钟/;/g/;
// 模拟React Native基础组件/;,/g/;
jest.mock('react-native', () => ({)')'';,}Platform: {,)';,}OS: 'ios';')','';'';
}
    select: jest.fn((obj) => obj.ios || obj.default);}
  }
Dimensions: {get: jest.fn(() => ({,;,)width: 375}height: 812,);
scale: 3,);
}
      const fontScale = 1;)}
    })),;
addEventListener: jest.fn(),;
const removeEventListener = jest.fn();
  }
Alert: {,;}}
    const alert = jest.fn();}';'';
  },';,'';
View: 'View';','';
Text: 'Text';','';
TouchableOpacity: 'TouchableOpacity';','';
ScrollView: 'ScrollView';','';
FlatList: 'FlatList';','';
Image: 'Image';','';
TextInput: 'TextInput';','';
SafeAreaView: 'SafeAreaView';','';
StatusBar: 'StatusBar';','';
ActivityIndicator: 'ActivityIndicator';','';
Modal: 'Modal';','';
Pressable: 'Pressable';','';
StyleSheet: {create: jest.fn((styles) => styles),;
}
    flatten: jest.fn((style) => style);}
  }
}));';'';
// 模拟导航'/;,'/g'/;
jest.mock('@react-navigation/native', () => ({/;)')'';,}useNavigation: () => ({,);,}navigate: jest.fn(),;,'/g,'/;
  goBack: jest.fn(),;
reset: jest.fn(),;
}
    const setParams = jest.fn();}
  }),;
useRoute: () => ({,)}
    params: {;},);
  }),;
useFocusEffect: jest.fn(),;
NavigationContainer: ({ children ;}: { children: React.ReactNode ;}) =>;
children,;
}));';'';
// 模拟Redux,'/;,'/g'/;
jest.mock('react-redux', () => ({)')'';,}useSelector: jest.fn((selector) =>;,'';
selector({)      auth: {isAuthenticated: false,;
user: null,;
}
        const token = null;}
      },';,'';
agents: {,'}'';
xiaoai: { status: 'idle' ;},';,'';
xiaoke: { status: 'idle' ;},';,'';
laoke: { status: 'idle' ;},';,'';
soer: { status: 'idle' ;},';'';
      }
health: {data: [],);
}
        const diagnosis = null;)}
      },);
    });
  ),;
useDispatch: () => jest.fn(),;
Provider: ({ children ;}: { children: React.ReactNode ;}) => children,;
}));
// 模拟fetch,/;,/g/;
global.fetch = jest.fn(() =>;
Promise.resolve({));,}ok: true,);
}
    status: 200;),}';,'';
json: () => Promise.resolve({;}),';,'';
text: () => Promise.resolve(');'';'';
  });
) as jest.Mock;
// 确保fetch在每个测试前都被重置/;,/g/;
beforeEach(() => {global.fetch = jest.fn(() =>;,}Promise.resolve({);,}ok: true,);
}
      status: 200;),}';,'';
json: () => Promise.resolve({;}),';,'';
text: () => Promise.resolve(');'';'';
    });
  ) as jest.Mock;
});
// 模拟定时器/;,/g/;
jest.useFakeTimers();
// 清理函数/;,/g/;
afterEach(() => {jest.clearAllMocks();}}
  jest.clearAllTimers();}
});
// 测试环境信息/;,/g/;
export {};';'';
''';