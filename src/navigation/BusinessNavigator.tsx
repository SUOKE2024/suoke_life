import { createStackNavigator } from "@react-navigation/stack";""/;,"/g"/;
import React from "react";";
import { StyleSheet, Text, View } from "react-native";";
import { BusinessStackParamList } from "./types";""/;"/g"/;

// 懒加载商业化屏幕组件"/;,"/g"/;
const  BusinessDashboard = React.lazy(')'';'';
  () () () => import('../screens/business/BusinessDashboard')'/;'/g'/;
);';,'';
const  SubscriptionPlansScreen = React.lazy(')'';'';
  () () () => import('../screens/business/SubscriptionPlansScreen')'/;'/g'/;
);

// 临时占位组件，后续可以替换为实际组件/;,/g/;
const  BPartnerListScreen = () => (<View style={styles.container}>;)    <Text style={styles.title}>B端合作伙伴列表</Text>)/;/g/;
    <Text style={styles.subtitle}>合作伙伴管理功能开发中...</Text>)/;/g/;
  </View>)/;/g/;
);
const  BPartnerDetailScreen = () => (<View style={styles.container}>;)    <Text style={styles.title}>合作伙伴详情</Text>)/;/g/;
    <Text style={styles.subtitle}>合作伙伴详情页面开发中...</Text>)/;/g/;
  </View>)/;/g/;
);
const  EcosystemProductsScreen = () => (<View style={styles.container}>;)    <Text style={styles.title}>生态产品</Text>)/;/g/;
    <Text style={styles.subtitle}>生态产品展示功能开发中...</Text>)/;/g/;
  </View>)/;/g/;
);
const  ProductDetailScreen = () => (<View style={styles.container}>;)    <Text style={styles.title}>产品详情</Text>)/;/g/;
    <Text style={styles.subtitle}>产品详情页面开发中...</Text>)/;/g/;
  </View>)/;/g/;
);
const  RevenueAnalyticsScreen = () => (<View style={styles.container}>;)    <Text style={styles.title}>收入分析</Text>)/;/g/;
    <Text style={styles.subtitle}>收入分析功能开发中...</Text>)/;/g/;
  </View>)/;/g/;
);
const  PricingManagementScreen = () => (<View style={styles.container}>;)    <Text style={styles.title}>定价管理</Text>)/;/g/;
    <Text style={styles.subtitle}>定价管理功能开发中...</Text>)/;/g/;
  </View>)/;/g/;
);
const  OrderHistoryScreen = () => (<View style={styles.container}>;)    <Text style={styles.title}>订单历史</Text>)/;/g/;
    <Text style={styles.subtitle}>订单历史功能开发中...</Text>)/;/g/;
  </View>)/;/g/;
);
const  PaymentMethodsScreen = () => (<View style={styles.container}>;)    <Text style={styles.title}>支付方式</Text>)/;/g/;
    <Text style={styles.subtitle}>支付方式管理功能开发中...</Text>)/;/g/;
  </View>)/;/g/;
);
const Stack = createStackNavigator<BusinessStackParamList>();
const  BusinessNavigator: React.FC = () => {';,}return (<Stack.Navigator,'  />/;,)initialRouteName="BusinessDashboard"";,"/g"/;
screenOptions={{";,}headerStyle: {,";}}"";
          const backgroundColor = '#2196F3';'}'';'';
        },';,'';
headerTintColor: '#fff';','';
headerTitleStyle: {,';}}'';
          const fontWeight = 'bold';'}'';'';
        }
      }}
    >';'';
      <Stack.Screen,'  />/;,'/g'/;
name="BusinessDashboard";
component={BusinessDashboard}

      />"/;"/g"/;
      <Stack.Screen,"  />/;,"/g"/;
name="SubscriptionPlans";
component={SubscriptionPlansScreen}

      />"/;"/g"/;
      <Stack.Screen,"  />/;,"/g"/;
name="BPartnerList";
component={BPartnerListScreen}

      />"/;"/g"/;
      <Stack.Screen,"  />/;,"/g"/;
name="BPartnerDetail";
component={BPartnerDetailScreen}

      />"/;"/g"/;
      <Stack.Screen,"  />/;,"/g"/;
name="EcosystemProducts";
component={EcosystemProductsScreen}

      />"/;"/g"/;
      <Stack.Screen,"  />/;,"/g"/;
name="ProductDetail";
component={ProductDetailScreen}

      />"/;"/g"/;
      <Stack.Screen,"  />/;,"/g"/;
name="RevenueAnalytics";
component={RevenueAnalyticsScreen}

      />"/;"/g"/;
      <Stack.Screen,"  />/;,"/g"/;
name="PricingManagement";
component={PricingManagementScreen}

      />"/;"/g"/;
      <Stack.Screen,"  />/;,"/g"/;
name="OrderHistory";
component={OrderHistoryScreen}

      />"/;"/g"/;
      <Stack.Screen,"  />/;,"/g"/;
name="PaymentMethods";
component={PaymentMethodsScreen}
);
      />)/;/g/;
    </Stack.Navigator>)/;/g/;
  );
};
const  styles = StyleSheet.create({)container: {,";,}flex: 1,";,"";
justifyContent: 'center';','';
alignItems: 'center';','';
backgroundColor: '#f5f5f5';','';'';
}
    const padding = 20;}
  }
title: {,';,}fontSize: 24,';,'';
fontWeight: 'bold';','';
color: '#333333';','';'';
}
    const marginBottom = 16;}
  }
subtitle: {,';,}fontSize: 16,';,'';
color: '#666666';','';
textAlign: 'center';',)'';'';
}
    const lineHeight = 24;)}
  },);
});
';,'';
export default BusinessNavigator; ''';