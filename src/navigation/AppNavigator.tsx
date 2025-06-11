import AsyncStorage from "@react-native-async-storage/async-storage"
import { NavigationContainer } from "@react-navigation/native"
import { createNativeStackNavigator } from "@react-navigation/native-stack"
import React, { useEffect, useState } from "react"
import {  Text, View  } from "react-native"
import {  useSelector  } from "react-redux"
import { RootState } from "../store"
import { AuthNavigator } from "./AuthNavigator"
import { linkingConfig } from "./DeepLinkConfig"
import { MainNavigator } from "./MainNavigator"
import { RootStackParamList } from "./types"/,'/g'/;
const ChatDetailScreen: React.FC = () => (<View style={ flex: 1, justifyContent: 'center', alignItems: 'center' ;}}>')'
    <Text>聊天详情页面</Text>)
  </View>)
);
const AgentChatScreen: React.FC = () => (<View style={ flex: 1, justifyContent: 'center', alignItems: 'center' ;}}>')'
    <Text>智能体聊天页面</Text>)
  </View>)
);
const DiagnosisServiceScreen: React.FC = () => (<View style={ flex: 1, justifyContent: 'center', alignItems: 'center' ;}}>')'
    <Text>诊断服务页面</Text>)
  </View>)
);
const AgentDemoScreen: React.FC = () => (<View style={ flex: 1, justifyContent: 'center', alignItems: 'center' ;}}>')'
    <Text>智能体演示页面</Text>)
  </View>)
);
// 应用主导航器 - 负责管理应用的整体导航流程，包括认证状态检查和路由分发
const Stack = createNativeStackNavigator<RootStackParamList>();
// 导航状态持久化键'/,'/g'/;
const NAVIGATION_STATE_KEY = '@navigation_state';
// 内部导航器组件/,/g,/;
  const: RootNavigator: React.FC<{isAuthenticated: boolean,
}
  const isDemoMode = boolean}
}> = ({  isAuthenticated, isDemoMode  }) => {return (<Stack.Navigator;  />/,)screenOptions={}        headerShown: false,','/g,'/;
  gestureEnabled: true,
}
        const animation = 'slide_from_right'}
      }
    >;
      {isAuthenticated || isDemoMode ? (;)        // 已认证用户或演示模式显示主应用/;}        <>/g'/;
          <Stack.Screen;'  />/;'/g'/;
}
            name="Main"}
component={MainNavigator}","
options={";}}
              const animationTypeForReplace = 'push'}
            }
          />'/;'/g'/;
          <Stack.Screen;'  />/,'/g'/;
name="ChatDetail
component={ChatDetailScreen}","
options={"presentation: 'card,'
}
              const animation = 'slide_from_right'}
            }
          />'/;'/g'/;
          <Stack.Screen;'  />/,'/g'/;
name="AgentChat
component={AgentChatScreen}","
options={"presentation: 'card,'
}
              const animation = 'slide_from_right'}
            }
          />'/;'/g'/;
          <Stack.Screen;'  />/,'/g'/;
name="DiagnosisService
component={DiagnosisServiceScreen}","
options={"presentation: 'card,'
}
              const animation = 'slide_from_right'}
            }
          />'/;'/g'/;
          <Stack.Screen;'  />/,'/g'/;
name="AgentDemo
component={AgentDemoScreen}","
options={"presentation: 'card,'
}
              const animation = 'slide_from_right'}
            ;}});
          />)
        < />)'
      ) : (// 未认证用户显示认证流程/;)        <>/g'/;
          <Stack.Screen;'  />/,'/g'/;
name="Auth
component={AuthNavigator}","
options={";}}
              const animationTypeForReplace = 'pop'}
            }
          />'/;'/g'/;
          <Stack.Screen;'  />/,'/g'/;
name="AgentDemo
component={AgentDemoScreen}","
options={"presentation: 'card,'
}
              const animation = 'slide_from_right'}
            ;}});
          />)
        < />)
      )}
    </Stack.Navigator>
  );
};
const  AppNavigator: React.FC = () => {// 从Redux获取认证状态/const authState = useSelector(state: RootState) => state.auth);','/g'/;
const  isAuthenticated ='
    'isAuthenticated' in authState ? authState.isAuthenticated : false;
  // 本地状态管理
const [isLoading, setIsLoading] = useState(true);
const [isDemoMode, setIsDemoMode] = useState(false);
const [initialState, setInitialState] = useState<any>();
const [isReady, setIsReady] = useState(false);
  // 检查认证状态和恢复导航状态
useEffect() => {const  checkAuthStatus = async () => {}      try {// 恢复导航状态/const  savedStateString =,/g/;
const await = AsyncStorage.getItem(NAVIGATION_STATE_KEY);
const savedState = savedStateString;
          ? JSON.parse(savedStateString);
          : undefined;
if (savedState) {}
          setInitialState(savedState)}
        }
        // TODO: 实际的认证状态检查逻辑'/;'/g'/;
        // 这里可以检查AsyncStorage中的token或其他认证信息'/;'/g'/;
        // const token = await AsyncStorage.getItem("authToken");"/;"/g"/;
        // setIsAuthenticated(!!token);
        // 暂时设置为未认证状态，显示欢迎页面
        // setIsAuthenticated(false);
      } catch (error) {}
}
      } finally {setIsLoading(false)}
        setIsReady(true)}
      }
    };
checkAuthStatus();
  }, []);
  // 保存导航状态
const  onStateChange = async (state: any) => {try {}
      await: AsyncStorage.setItem(NAVIGATION_STATE_KEY, JSON.stringify(state)}
    } catch (error) {";}}
      console.error('Failed to save navigation state:', error);'}
    }
  };
  // 如果正在加载，可以显示启动画面
if (isLoading || !isReady) {// TODO: 添加启动画面组件/;}}/g/;
    return null}
  }
  return (<NavigationContainer;  />/,)linking={linkingConfig}),/g/;
initialState={initialState});
onStateChange={onStateChange})'
onReady={() => {';}}
        console.log('Navigation container is ready');'}
      }
    >;
      <RootNavigator;  />
isAuthenticated={isAuthenticated}
        isDemoMode={isDemoMode}
      />
    </NavigationContainer>
  );
};
export default AppNavigator;
''