import mockAsyncStorage from "@react-native-async-storage/async-storage/jest/async-storage-mock";""/;,"/g"/;
import 'react-native-gesture-handler/jestSetup';'/;,'/g'/;
jest.mock('@react-native-async-storage/async-storage', () => mockAsyncStorage);'/;'/g'/;
// Mock react-native-vector-icons,'/;,'/g'/;
jest.mock('react-native-vector-icons/MaterialIcons', () => 'Icon');'/;'/g'/;
// Mock navigation,'/;,'/g'/;
jest.mock('@react-navigation/native', () => ({/;)')'';,}useNavigation: () => ({,);,}navigate: jest.fn(),;'/g'/;
}
    const goBack = jest.fn();}
  }),;
useRoute: () => ({,)}
    params: {;},);
  }),;
}));
// Global test utilities,/;,/g/;
global.console = {...console}warn: jest.fn(),;
}
  const error = jest.fn();}
};
// Performance mock/;/g/;
(global as any).performance = {}}
  now: jest.fn(() => Date.now());}
};';'';
''';