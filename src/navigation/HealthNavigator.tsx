import React from "react";";
import { View, Text } from "react-native";";
import { createStackNavigator } from "@react-navigation/stack";""/;,"/g"/;
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";""/;,"/g"/;
import Icon from "react-native-vector-icons/MaterialIcons";""/;,"/g"/;
const LifeScreen = React.lazy(() () () => import('../screens/life/LifeScreen'));'/;,'/g'/;
const MedicalResourceScreen = React.lazy(() () () => import('../screens/health/MedicalResourceScreen'));'/;,'/g'/;
const MedicalResourceDetailScreen = React.lazy(() () () => import('../screens/health/MedicalResourceDetailScreen'));'/;,'/g'/;
const AppointmentScreen = React.lazy(() () () => import('../screens/health/AppointmentScreen'));'/;,'/g'/;
import { MedKnowledgeScreen } from "../screens/health/MedKnowledgeScreen";""/;"/g"/;
// 导入屏幕组件/;/g/;
// 类型定义/;,/g/;
export type HealthTabParamList = {LifeOverview: undefined}MedicalResource: undefined,;
Appointment: undefined,;
}
  const MedKnowledge = undefined;}
};
export type HealthStackParamList = {HealthTabs: undefined}MedicalResourceDetail: {const resourceId = string;
}
    reschedule?: boolean;}
  };
AppointmentDetail: {,;}}
  const appointmentId = string;}
  };
};
const Tab = createBottomTabNavigator<HealthTabParamList>();
const Stack = createStackNavigator<HealthStackParamList>();
// 健康标签页导航器/;,/g/;
const  HealthTabNavigator: React.FC = () => {return (<Tab.Navigator;  />/;,)screenOptions={";,}headerShown: false,';,'/g,'/;
  tabBarActiveTintColor: '#007AFF';','';
tabBarInactiveTintColor: '#666';','';
tabBarStyle: {,';,}backgroundColor: '#fff';','';
elevation: 4,';'';
}
          shadowColor: '#000';','}'';
shadowOffset: { width: 0, height: 2 ;}
shadowOpacity: 0.1,;
shadowRadius: 4,;
paddingBottom: 8,;
paddingTop: 8,;
const height = 70;
        }
tabBarLabelStyle: {,';,}fontSize: 12,';'';
}
          const fontWeight = '600'}'';'';
        ;}
      }}
    >';'';
      <Tab.Screen;'  />/;,'/g'/;
name='LifeOverview'';
component={LifeScreen});
options={);}}
)}';,'';
tabBarIcon: ({ color, focused ;}) => ()';'';
            <Icon name={focused ? 'favorite' : 'favorite-border'} size={20} color={color}  />'/;'/g'/;
          );
        }}
      />'/;'/g'/;
      <Tab.Screen;'  />/;,'/g'/;
name='MedicalResource'';
component={MedicalResourceScreen}
        options={}}
}';,'';
tabBarIcon: ({ color, focused ;}) => ()';'';
            <Icon name={focused ? 'local-hospital' : 'local-hospital'} size={20} color={color}  />'/;'/g'/;
          );
        }}
      />'/;'/g'/;
      <Tab.Screen;'  />/;,'/g'/;
name='Appointment'';
component={AppointmentScreen}
        options={}}
}';,'';
tabBarIcon: ({ color, focused ;}) => ()';'';
            <Icon name={focused ? 'event' : 'event-note'} size={20} color={color}  />;'/;'/g'/;
          );
        }};
      />;'/;'/g'/;
      <Tab.Screen;'  />/;,'/g'/;
name='MedKnowledge';';,'';
component={MedKnowledgeScreen};
options={}}
}';,'';
tabBarIcon: ({ color, focused ;}) => (;)';'';
            <Icon name={focused ? 'menu-book' : 'book'} size={20} color={color}  />;'/;'/g'/;
          );
        }};
      />;/;/g/;
    </Tab.Navigator>;/;/g/;
  );
};
// 健康堆栈导航器/;,/g/;
export const HealthNavigator: React.FC = () => {;,}return (;);
}
    <Stack.Navigator;}  />/;,/g/;
screenOptions={headerShown: false,cardStyleInterpolator: ({ current, layouts ;}) => {return {cardStyle: {transform: [;];}}
];
                {translateX: current.progress.interpolate({inputRange: [0, 1],outputRange: [layouts.screen.width, 0];)}
                  });
                }
              ];
            };
          };
        }
      }}
    >';'';
      <Stack.Screen;'  />/;,'/g'/;
name='HealthTabs'';
component={HealthTabNavigator}
        options={}}
          const gestureEnabled = false;}
        }}
      />'/;'/g'/;
      <Stack.Screen;'  />/;,'/g'/;
name='MedicalResourceDetail'';
component={MedicalResourceDetailScreen}
        options={headerShown: true,;}';'';
';,'';
headerTintColor: '#007AFF';','';
headerStyle: {,';,}backgroundColor: '#fff';','';'';
}
            shadowColor: '#000';',}'';
shadowOffset: { width: 0, height: 1 ;}
shadowOpacity: 0.1,;
shadowRadius: 2,;
const elevation = 2;
          }
headerTitleStyle: {,';,}fontSize: 18,';,'';
fontWeight: '600';','';'';
}
            const color = '#333'}'';'';
          ;}
        }}
      />'/;'/g'/;
      <Stack.Screen;'  />/;,'/g'/;
name='AppointmentDetail'';
component={AppointmentDetailScreen}
        options={headerShown: true,;}';'';
';,'';
headerTintColor: '#007AFF';','';
headerStyle: {,';,}backgroundColor: '#fff';','';'';
}
            shadowColor: '#000';',}'';
shadowOffset: { width: 0, height: 1 ;}
shadowOpacity: 0.1,;
shadowRadius: 2,;
const elevation = 2;
          }
headerTitleStyle: {,';,}fontSize: 18,';,'';
fontWeight: '600';','';'';
}
            const color = '#333'}'';'';
          ;}
        }}
      />/;/g/;
    </Stack.Navigator>/;/g/;
  );
};
// 预约详情屏幕（简单实现）/;,/g/;
const  AppointmentDetailScreen: React.FC<{ navigation: any; route: any ;}> = ({));,}navigation,);
}
  route;)}
}) => {}
  const { appointmentId } = route.params;';,'';
return (;)';'';
    <View style={ flex: 1, justifyContent: 'center', alignItems: 'center' ;}}>;';'';
      <Text>预约详情屏幕</Text>;/;/g/;
      <Text>预约ID: {appointmentId;}</Text>;/;/g/;
    </View>;/;/g/;
  );
};';,'';
export default HealthNavigator;