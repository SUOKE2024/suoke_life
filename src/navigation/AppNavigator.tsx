import AsyncStorage from "@react-native-async-storage/async-storage";""/;,"/g"/;
import { NavigationContainer } from "@react-navigation/native";""/;,"/g"/;
import { createNativeStackNavigator } from "@react-navigation/native-stack";""/;,"/g"/;
import React, { useEffect, useState } from "react";";
import { Text, View } from "react-native";";
import { useSelector } from "react-redux";";
import { RootState } from "../store";""/;,"/g"/;
import { AuthNavigator } from "./AuthNavigator";""/;,"/g"/;
import { linkingConfig } from "./DeepLinkConfig";""/;,"/g"/;
import { MainNavigator } from "./MainNavigator";""/;,"/g"/;
import { RootStackParamList } from "./types";""/;"/g"/;
";"";
// 临时占位符组件'/;,'/g'/;
const ChatDetailScreen: React.FC = () => (<View style={ flex: 1, justifyContent: 'center', alignItems: 'center' ;}}>')'';'';
    <Text>聊天详情页面</Text>)/;/g/;
  </View>)/;/g/;
);';'';
';,'';
const AgentChatScreen: React.FC = () => (<View style={ flex: 1, justifyContent: 'center', alignItems: 'center' ;}}>')'';'';
    <Text>智能体聊天页面</Text>)/;/g/;
  </View>)/;/g/;
);';'';
';,'';
const DiagnosisServiceScreen: React.FC = () => (<View style={ flex: 1, justifyContent: 'center', alignItems: 'center' ;}}>')'';'';
    <Text>诊断服务页面</Text>)/;/g/;
  </View>)/;/g/;
);';'';
';,'';
const AgentDemoScreen: React.FC = () => (<View style={ flex: 1, justifyContent: 'center', alignItems: 'center' ;}}>')'';'';
    <Text>智能体演示页面</Text>)/;/g/;
  </View>)/;/g/;
);

// 应用主导航器 - 负责管理应用的整体导航流程，包括认证状态检查和路由分发/;,/g/;
const Stack = createNativeStackNavigator<RootStackParamList>();
';'';
// 导航状态持久化键'/;,'/g'/;
const NAVIGATION_STATE_KEY = '@navigation_state';';'';

// 内部导航器组件/;,/g,/;
  const: RootNavigator: React.FC<{isAuthenticated: boolean,;
}
  const isDemoMode = boolean;}
}> = ({ isAuthenticated, isDemoMode }) => {return (<Stack.Navigator;  />/;,)screenOptions={}        headerShown: false,';,'/g,'/;
  gestureEnabled: true,';'';
}
        const animation = 'slide_from_right'}'';'';
      ;}}
    >;
      {isAuthenticated || isDemoMode ? (;)        // 已认证用户或演示模式显示主应用/;}        <>';'/g'/;
          <Stack.Screen;'  />/;'/g'/;
}
            name="Main"}";
component={MainNavigator}";,"";
options={";}}"";
              const animationTypeForReplace = 'push'}'';'';
            ;}}
          />'/;'/g'/;
          <Stack.Screen;'  />/;,'/g'/;
name="ChatDetail";
component={ChatDetailScreen}";,"";
options={";,}presentation: 'card';','';'';
}
              const animation = 'slide_from_right'}'';'';
            ;}}
          />'/;'/g'/;
          <Stack.Screen;'  />/;,'/g'/;
name="AgentChat";
component={AgentChatScreen}";,"";
options={";,}presentation: 'card';','';'';
}
              const animation = 'slide_from_right'}'';'';
            ;}}
          />'/;'/g'/;
          <Stack.Screen;'  />/;,'/g'/;
name="DiagnosisService";
component={DiagnosisServiceScreen}";,"";
options={";,}presentation: 'card';','';'';
}
              const animation = 'slide_from_right'}'';'';
            ;}}
          />'/;'/g'/;
          <Stack.Screen;'  />/;,'/g'/;
name="AgentDemo";
component={AgentDemoScreen}";,"";
options={";,}presentation: 'card';','';'';
}
              const animation = 'slide_from_right'}'';'';
            ;}});
          />)/;/g/;
        < />)/;/g/;
      ) : (// 未认证用户显示认证流程/;)        <>';'/g'/;
          <Stack.Screen;'  />/;,'/g'/;
name="Auth";
component={AuthNavigator}";,"";
options={";}}"";
              const animationTypeForReplace = 'pop'}'';'';
            ;}}
          />'/;'/g'/;
          <Stack.Screen;'  />/;,'/g'/;
name="AgentDemo";
component={AgentDemoScreen}";,"";
options={";,}presentation: 'card';','';'';
}
              const animation = 'slide_from_right'}'';'';
            ;}});
          />)/;/g/;
        < />)/;/g/;
      )}
    </Stack.Navigator>/;/g/;
  );
};
const  AppNavigator: React.FC = () => {// 从Redux获取认证状态/;,}const authState = useSelector(state: RootState) => state.auth);';,'/g'/;
const  isAuthenticated =';'';
    'isAuthenticated' in authState ? authState.isAuthenticated : false;';'';

  // 本地状态管理/;,/g/;
const [isLoading, setIsLoading] = useState(true);
const [isDemoMode, setIsDemoMode] = useState(false);
const [initialState, setInitialState] = useState<any>();
const [isReady, setIsReady] = useState(false);

  // 检查认证状态和恢复导航状态/;,/g/;
useEffect() => {const  checkAuthStatus = async () => {}      try {// 恢复导航状态/;,}const  savedStateString =;,/g/;
const await = AsyncStorage.getItem(NAVIGATION_STATE_KEY);
const savedState = savedStateString;
          ? JSON.parse(savedStateString);
          : undefined;
if (savedState) {}}
          setInitialState(savedState);}
        }

        // TODO: 实际的认证状态检查逻辑'/;'/g'/;
        // 这里可以检查AsyncStorage中的token或其他认证信息'/;'/g'/;
        // const token = await AsyncStorage.getItem("authToken");"/;"/g"/;
        // setIsAuthenticated(!!token);/;/g/;

        // 暂时设置为未认证状态，显示欢迎页面/;/g/;
        // setIsAuthenticated(false);/;/g/;
      } catch (error) {}}
}
      } finally {setIsLoading(false);}}
        setIsReady(true);}
      }
    };
checkAuthStatus();
  }, []);

  // 保存导航状态/;,/g/;
const  onStateChange = async (state: any) => {try {}}
      await: AsyncStorage.setItem(NAVIGATION_STATE_KEY, JSON.stringify(state));}";"";
    } catch (error) {";}}"";
      console.error('Failed to save navigation state:', error);'}'';'';
    }
  };

  // 如果正在加载，可以显示启动画面/;,/g/;
if (isLoading || !isReady) {// TODO: 添加启动画面组件/;}}/g/;
    return null;}
  }

  return (<NavigationContainer;  />/;,)linking={linkingConfig});,/g/;
initialState={initialState});
onStateChange={onStateChange})';,'';
onReady={() => {';}}'';
        console.log('Navigation container is ready');'}'';'';
      }}
    >;
      <RootNavigator;  />/;,/g/;
isAuthenticated={isAuthenticated}
        isDemoMode={isDemoMode}
      />/;/g/;
    </NavigationContainer>/;/g/;
  );
};
export default AppNavigator;';'';
''';