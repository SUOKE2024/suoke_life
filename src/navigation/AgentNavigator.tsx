import { createNativeStackNavigator } from "@react-navigation/native-stack"
import React from "react"
import {  StyleSheet, Text, View  } from "react-native"
import { AgentStackParamList } from "./types"/,'/g'/;
const AgentListScreen = React.lazy(() () () => import('../screens/agents/AgentListScreen'));'/,'/g'/;
const AgentChatScreen = React.lazy(() () () => import('../screens/agents/AgentChatScreen'));'/;'/g'/;
// 临时占位组件
const PlaceholderScreen = ({ title }: { title: string ;}) => (<View style={styles.container}>;)    <Text style={styles.title}>{title}</Text>)
    <Text style={styles.subtitle}>该功能正在开发中，敬请期待</Text>)
  </View>)
);
// 占位屏幕组件'/,'/g'/;
const AgentManagementScreen = () => <Suspense fallback={<LoadingSpinner  />}><PlaceholderScreen title="智能体管理"  /></Suspense>;
const AgentProfileScreen = () => <Suspense fallback={<LoadingSpinner  />}><PlaceholderScreen title="智能体档案"  /></Suspense>;
const AgentConfigScreen = () => <Suspense fallback={<LoadingSpinner  />}><PlaceholderScreen title="智能体配置"  /></Suspense>;
const AgentAnalyticsScreen = () => <Suspense fallback={<LoadingSpinner  />}><PlaceholderScreen title="智能体分析"  /></Suspense>;
const Stack = createNativeStackNavigator<AgentStackParamList>();
/* 航 */
 */"
export const AgentNavigator: React.FC = () => {"return (<Stack.Navigator,"  />/,)initialRouteName="AgentList"","/g"/;
screenOptions={{"headerShown: false,","
animation: 'slide_from_right,'';
gestureEnabled: true,
}
        const gestureDirection = 'horizontal}
      }
    >'
      <Stack.Screen,'  />/,'/g'/;
name="AgentList";
component={AgentListScreen}
        options={{}
          const gestureEnabled = false}
        }
      />"
      <Stack.Screen,"  />"
name="AgentManagement
component={AgentManagementScreen}","
options={{";}}
          const animation = 'slide_from_right}
        }
      />'
      <Stack.Screen,'  />/,'/g'/;
name="AgentChat
component={AgentChatScreen}","
options={{"animation: 'slide_from_bottom,'
}
          const presentation = 'modal}
        }
      />'
      <Stack.Screen,'  />/,'/g'/;
name="AgentProfile
component={AgentProfileScreen}","
options={{";}}
          const animation = 'slide_from_right}
        }
      />'
      <Stack.Screen,'  />/,'/g'/;
name="AgentConfig
component={AgentConfigScreen}","
options={{";}}
          const animation = 'slide_from_right}
        }
      />'
      <Stack.Screen,'  />/,'/g'/;
name="AgentAnalytics
component={AgentAnalyticsScreen}","
options={{";}}
          const animation = 'slide_from_right}
        }});
      />)
    </Stack.Navigator>)
  );
};
const  styles = StyleSheet.create({)container: {,'flex: 1,'
justifyContent: 'center,'
alignItems: 'center,'
backgroundColor: '#f5f5f5,'
}
    const padding = 20}
  }
title: {,'fontSize: 24,'
fontWeight: 'bold,'
color: '#333333,'
}
    const marginBottom = 16}
  }
subtitle: {,'fontSize: 16,'
color: '#666666,'
textAlign: 'center,)'
}
    const lineHeight = 24;)}
  },);
});
export default AgentNavigator;