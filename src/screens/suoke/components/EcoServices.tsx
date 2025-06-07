import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from '../../placeholder';react-native;
import React from 'react";
export interface EcoService {
  id: string;
  name: string;
  description: string;
  category: string;
  icon: string;
  available: boolean;
}
export interface EcoServicesProps {
  services?: EcoService[];
  onServicePress?: (service: EcoService) => void;
}
/**
* * 索克生活 - 生态服务组件
* 展示平台提供的各种生态服务
export const EcoServices: React.FC<EcoServicesProps>  = ({services = [],onServicePress;
}) => {}
  const defaultServices: EcoService[] = [;
    {
      id: health-consultation",
      name: "健康咨询,",
      description: "专业中医健康咨询服务",
      category: 健康",
      icon: "🏥,",
      available: true;
    },
    {
      id: "food-agriculture",
      name: 食农结合",
      description: "有机农产品溯源与配送,",
      category: "农业",
      icon: 🌱",
      available: true;
    },
    {
      id: "mountain-wellness,",
      name: "山水养生",
      description: 自然环境下的养生体验",
      category: "养生,",
      icon: "🏔️",
      available: true;
    },
    {
      id: tcm-diagnosis",
      name: "中医诊断,",
      description: "四诊合参智能诊断",
      category: 诊断",
      icon: "🔍,",
      available: true;
    }
  ];
  const displayServices = services.length > 0 ? services : defaultServices;
  const handleServicePress = (service: EcoService) => {}
    if (service.available && onServicePress) {onServicePress(service);
    }
  };
  const renderService = (service: EcoService) => (;
    <TouchableOpacity;
key={service.id}
      style={[
        styles.serviceCard,
        !service.available && styles.serviceCardDisabled;
      ]}
      onPress={() => handleServicePress(service)}
      disabled={!service.available}
    >
      <View style={styles.serviceIcon}>
        <Text style={styles.iconText}>{service.icon}</    Text>
      </    View>
      <View style={styles.serviceContent}>
        <Text style={styles.serviceName}>{service.name}</    Text>
        <Text style={styles.serviceDescription}>{service.description}</    Text>
        <Text style={styles.serviceCategory}>{service.category}</    Text>
      </    View>
      {!service.available && (
        <View style={styles.unavailableBadge}>
          <Text style={styles.unavailableText}>暂不可用</    Text>
        </    View>
      )}
    </    TouchableOpacity>
  );
  return (;
    <View style={styles.container}>;
      <Text style={styles.title}>生态服务</    Text>;
      <ScrollView;
style={styles.scrollView}
        showsVerticalScrollIndicator={false}
      >
        {displayServices.map(renderService)}
      </    ScrollView>
    </    View>
  );
};
const styles = StyleSheet.create({container: {,
  flex: 1,
    padding: 16,
    backgroundColor: "#f5f5f5"},
  title: {,
  fontSize: 24,
    fontWeight: bold",
    color: "#333,",
    marginBottom: 16,
    textAlign: "center"},
  scrollView: {,
  flex: 1},
  serviceCard: {,
  backgroundColor: #fff",
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    flexDirection: "row,",
    alignItems: "center",
    shadowColor: #000",
    shadowOffset: {,
  width: 0,
      height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5},
  serviceCardDisabled: {,
  opacity: 0.6,
    backgroundColor: "#f0f0f0},",
  serviceIcon: {,
  width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: "#e8f5e8",
    justifyContent: center",
    alignItems: "center,",
    marginRight: 16},
  iconText: {,
  fontSize: 24},
  serviceContent: {,
  flex: 1},
  serviceName: {,
  fontSize: 18,
    fontWeight: "600",
    color: #333",
    marginBottom: 4},
  serviceDescription: {,
  fontSize: 14,
    color: "#666,",
    marginBottom: 4},
  serviceCategory: {,
  fontSize: 12,
    color: "#999",
    backgroundColor: #f0f0f0",
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 10,
    alignSelf: "flex-start},",
  unavailableBadge: {,
  backgroundColor: "#ff6b6b",
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12},
  unavailableText: {,
  color: #fff",
    fontSize: 12,fontWeight: '500'}});
export default EcoServices; */
