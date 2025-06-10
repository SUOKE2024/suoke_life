import { createStackNavigator } from '@react-navigation/stack';
import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { BusinessStackParamList } from './types';

// 懒加载商业化屏幕组件
const BusinessDashboard = React.lazy(
  () => import('../screens/business/BusinessDashboard')
);
const SubscriptionPlansScreen = React.lazy(
  () => import('../screens/business/SubscriptionPlansScreen')
);

// 临时占位组件，后续可以替换为实际组件
const BPartnerListScreen = () => (
  <View style={styles.container}>
    <Text style={styles.title}>B端合作伙伴列表</Text>
    <Text style={styles.subtitle}>合作伙伴管理功能开发中...</Text>
  </View>
);

const BPartnerDetailScreen = () => (
  <View style={styles.container}>
    <Text style={styles.title}>合作伙伴详情</Text>
    <Text style={styles.subtitle}>合作伙伴详情页面开发中...</Text>
  </View>
);

const EcosystemProductsScreen = () => (
  <View style={styles.container}>
    <Text style={styles.title}>生态产品</Text>
    <Text style={styles.subtitle}>生态产品展示功能开发中...</Text>
  </View>
);

const ProductDetailScreen = () => (
  <View style={styles.container}>
    <Text style={styles.title}>产品详情</Text>
    <Text style={styles.subtitle}>产品详情页面开发中...</Text>
  </View>
);

const RevenueAnalyticsScreen = () => (
  <View style={styles.container}>
    <Text style={styles.title}>收入分析</Text>
    <Text style={styles.subtitle}>收入分析功能开发中...</Text>
  </View>
);

const PricingManagementScreen = () => (
  <View style={styles.container}>
    <Text style={styles.title}>定价管理</Text>
    <Text style={styles.subtitle}>定价管理功能开发中...</Text>
  </View>
);

const OrderHistoryScreen = () => (
  <View style={styles.container}>
    <Text style={styles.title}>订单历史</Text>
    <Text style={styles.subtitle}>订单历史功能开发中...</Text>
  </View>
);

const PaymentMethodsScreen = () => (
  <View style={styles.container}>
    <Text style={styles.title}>支付方式</Text>
    <Text style={styles.subtitle}>支付方式管理功能开发中...</Text>
  </View>
);

const Stack = createStackNavigator<BusinessStackParamList>();

const BusinessNavigator: React.FC = () => {
  return (
    <Stack.Navigator
      initialRouteName="BusinessDashboard"
      screenOptions={{
        headerStyle: {
          backgroundColor: '#2196F3';
        },
        headerTintColor: '#fff';
        headerTitleStyle: {
          fontWeight: 'bold';
        },
      }}
    >
      <Stack.Screen
        name="BusinessDashboard"
        component={BusinessDashboard}

      />
      <Stack.Screen
        name="SubscriptionPlans"
        component={SubscriptionPlansScreen}

      />
      <Stack.Screen
        name="BPartnerList"
        component={BPartnerListScreen}

      />
      <Stack.Screen
        name="BPartnerDetail"
        component={BPartnerDetailScreen}

      />
      <Stack.Screen
        name="EcosystemProducts"
        component={EcosystemProductsScreen}

      />
      <Stack.Screen
        name="ProductDetail"
        component={ProductDetailScreen}

      />
      <Stack.Screen
        name="RevenueAnalytics"
        component={RevenueAnalyticsScreen}

      />
      <Stack.Screen
        name="PricingManagement"
        component={PricingManagementScreen}

      />
      <Stack.Screen
        name="OrderHistory"
        component={OrderHistoryScreen}

      />
      <Stack.Screen
        name="PaymentMethods"
        component={PaymentMethodsScreen}

      />
    </Stack.Navigator>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1;
    justifyContent: 'center';
    alignItems: 'center';
    backgroundColor: '#f5f5f5';
    padding: 20;
  },
  title: {
    fontSize: 24;
    fontWeight: 'bold';
    color: '#333333';
    marginBottom: 16;
  },
  subtitle: {
    fontSize: 16;
    color: '#666666';
    textAlign: 'center';
    lineHeight: 24;
  },
});

export default BusinessNavigator; 