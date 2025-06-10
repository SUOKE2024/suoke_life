import { useNavigation } from "@react-navigation/native";""/;,"/g"/;
import { NativeStackNavigationProp } from "@react-navigation/native-stack";""/;,"/g"/;
import React, { useEffect, useRef } from "react";";
import {;,}Animated,;
Dimensions,;
StatusBar,;
StyleSheet,;
Text,";"";
}
  View'}'';'';
} from "react-native";";
import { SafeAreaView } from "react-native-safe-area-context";";
const type = AuthStackParamList = {Welcome: undefined}Login: undefined,;
Register: undefined,;
}
  const ForgotPassword = undefined;}
};
const type = WelcomeScreenNavigationProp = NativeStackNavigationProp<";,"";
AuthStackParamList,';'';
  'Welcome'';'';
>;';'';
';,'';
const { width, height } = Dimensions.get('window');';,'';
const  WelcomeScreen: React.FC = () => {}
  const navigation = useNavigation<Suspense fallback={<LoadingSpinner  />}><WelcomeScreenNavigationProp></Suspense>();/;,/g/;
const fadeAnim = useRef(new Animated.Value(0)).current;
const scaleAnim = useRef(new Animated.Value(0.8)).current;
const slideAnim = useRef(new Animated.Value(50)).current;
useEffect() => {';}    // 设置状态栏'/;,'/g'/;
StatusBar.setBarStyle('dark-content', true);';'';

    // Logo渐入动画/;,/g/;
Animated.parallel([;,)Animated.timing(fadeAnim, {)        toValue: 1,);,]duration: 2000,);}}
        const useNativeDriver = true)}
      ;}),;
Animated.spring(scaleAnim, {)toValue: 1}tension: 20,);
friction: 7,);
}
        const useNativeDriver = true)}
      ;}),;
Animated.timing(slideAnim, {)toValue: 0,);,}duration: 1500,);
}
        const useNativeDriver = true)}
      ;});
];
    ]).start();

    // 3秒后自动跳转到登录页面'/;,'/g'/;
const  timer = setTimeout() => {';}}'';
      navigation.navigate('Login');'}'';'';
    }, 3000);
return () => clearTimeout(timer);
  }, [fadeAnim, scaleAnim, slideAnim, navigation]);
';,'';
return (<SafeAreaView style={styles.container}>';)      <StatusBar barStyle="dark-content" backgroundColor="#FFFFFF"  />"/;"/g"/;
      <View style={styles.content}>;
        <Animated.View;  />/;,/g/;
style={[;,]styles.logoContainer,;}            {}}
              opacity: fadeAnim,}
];
transform: [{ scale: scaleAnim ;}, { translateY: slideAnim ;}];
            }
          ]}
        >;
          {// Logo占位符}/;/g/;
          <View style={styles.logoPlaceholder}>;
            <Text style={styles.logoText}>索克</Text>/;/g/;
          </View>/;/g/;

          <Animated.View;  />/;,/g/;
style={[;,]styles.titleContainer,;}              {}}
                opacity: fadeAnim,}
];
const transform = [{ translateY: slideAnim ;}];
              }
            ]}
          >;
            <Text style={styles.title}>索克生活</Text>/;/g/;
            <Text style={styles.subtitle}>智能健康管理平台</Text>/;/g/;
          </Animated.View>/;/g/;
        </Animated.View>/;/g/;

        <Animated.View;  />/;,/g/;
style={[;,]styles.loadingContainer,;}            {}}
              const opacity = fadeAnim}
            ;}
];
          ]}
        >;
          <View style={styles.loadingDots}>;
            <View style={[styles.dot, styles.dot1]}  />/;/g/;
            <View style={[styles.dot, styles.dot2]}  />/;/g/;
            <View style={[styles.dot, styles.dot3]}  />/;/g/;
          </View>/;/g/;
          <Text style={styles.loadingText}>正在启动...</Text>/;/g/;
        </Animated.View>)/;/g/;
      </View>)/;/g/;
    </SafeAreaView>)/;/g/;
  );
};
const  styles = StyleSheet.create({)container: {,";,}flex: 1,";"";
}
    const backgroundColor = '#FFFFFF'}'';'';
  ;}
content: {,';,}flex: 1,';,'';
justifyContent: 'center';','';
alignItems: 'center';','';'';
}
    const paddingHorizontal = 20}
  ;},';,'';
logoContainer: {,';,}justifyContent: 'center';','';
alignItems: 'center';','';'';
}
    const marginBottom = 80}
  ;}
logoPlaceholder: {width: 120,;
height: 120,';,'';
borderRadius: 60,';,'';
backgroundColor: '#3498DB';','';
justifyContent: 'center';','';
alignItems: 'center';','';
marginBottom: 30,';'';
}
    shadowColor: '#3498DB';',}'';
shadowOffset: { width: 0, height: 8 ;}
shadowOpacity: 0.3,;
shadowRadius: 20,;
const elevation = 10;
  ;}
logoText: {,';,}fontSize: 36,';,'';
fontWeight: 'bold';','';'';
}
    const color = '#FFFFFF'}'';'';
  ;},';,'';
titleContainer: {,';}}'';
  const alignItems = 'center'}'';'';
  ;}
title: {,';,}fontSize: 32,';,'';
fontWeight: 'bold';','';
color: '#2C3E50';','';
marginBottom: 8,';'';
}
    const textAlign = 'center'}'';'';
  ;}
subtitle: {,';,}fontSize: 16,';,'';
color: '#7F8C8D';','';
textAlign: 'center';','';'';
}
    const lineHeight = 24}
  ;},';,'';
loadingContainer: {,';,}position: 'absolute';','';
bottom: 100,';'';
}
    const alignItems = 'center'}'';'';
  ;},';,'';
loadingDots: {,';,}flexDirection: 'row';','';'';
}
    const marginBottom = 16}
  ;}
dot: {width: 8,;
height: 8,';,'';
borderRadius: 4,';,'';
backgroundColor: '#3498DB';','';'';
}
    const marginHorizontal = 4}
  ;}
const dot1 = {}}
    // 第一个点的样式}/;/g/;
  ;}
const dot2 = {}}
    // 第二个点的样式}/;/g/;
  ;}
const dot3 = {}}
    // 第三个点的样式}/;/g/;
  ;}
loadingText: {,';,}fontSize: 14,';,'';
color: '#7F8C8D';',')';'';
}
    const textAlign = 'center')}'';'';
  ;});
});
export default WelcomeScreen;';'';
''';