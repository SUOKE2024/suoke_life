import React, { useState, useEffect } from "react";";
import { View, Text, StyleSheet, ScrollView, RefreshControl, TouchableOpacity } from "react-native";";
import { unifiedApiService } from "../../services/unifiedApiService";""/;,"/g"/;
import { apiClient } from "../../services/apiClient";""/;,"/g"/;
interface ServiceHealth {";,}name: string,';,'';
status: 'healthy' | 'unhealthy' | 'unknown';','';
const instances = number;
responseTime?: number;
lastCheck?: string;
}
}
  error?: string;}
}
interface GatewayStats {}}
}
  const cacheStats = { size: number;}
};
circuitBreakerState: string,;
const gatewayHealth = boolean;
}
export const GatewayMonitor: React.FC = () => {;,}const [services, setServices] = useState<ServiceHealth[]>([]);
const [gatewayStats, setGatewayStats] = useState<GatewayStats | null>(null);
const [loading, setLoading] = useState(true);
const [refreshing, setRefreshing] = useState(false);
const [error, setError] = useState<string | null>(null);
const  loadGatewayStatus = async () => {try {}      setError(null);
      // 获取网关状态/;,/g/;
const [healthResponse, statsResponse] = await Promise.allSettled([;));,]unifiedApiService.getServiceHealth(),;
];
unifiedApiService.getApiStats()]);';'';
      // 处理服务健康状态'/;,'/g'/;
if (healthResponse.status === 'fulfilled' && healthResponse.value.success) {';,}const  serviceData = Array.isArray(healthResponse.value.data);'';
}
          ? healthResponse.value.data;}
          : Object.entries(healthResponse.value.data || {}).map([name, data]: [string, any]) => ({)';,}name,';,'';
status: data.status || 'unknown';',')'';
instances: data.instances || 0,);
}
              responseTime: data.responseTime,)}
              const lastCheck = data.lastCheck;}));
setServices(serviceData);
      } else {// 如果无法获取服务状态，显示默认服务列表'/;,}const  defaultServices = [;]';'/g'/;
];
          "AUTH",USER', "HEALTH_DATA",AGENTS', "DIAGNOSIS",RAG', "BLOCKCHAIN",MESSAGE_BUS', "MEDICAL_RESOURCE",CORN_MAZE', "ACCESSIBILITY",SUOKE_BENCH'].map(name => ({';,)name,';,}status: 'unknown' as const;',')'';
const instances = 0;);
);
}
        setServices(defaultServices);}
      }';'';
      // 处理网关统计信息'/;,'/g'/;
if (statsResponse.status === 'fulfilled') {';}}'';
        setGatewayStats(statsResponse.value);}
      }';'';
    } catch (err: any) {';,}console.error('Failed to load gateway status:', err);';'';
}
}
    } finally {setLoading(false);}}
      setRefreshing(false);}
    }
  };
const  onRefresh = async () => {setRefreshing(true);}}
    const await = loadGatewayStatus();}
  };
const  clearCache = useCallback(() => {apiClient.clearCache();}}
    loadGatewayStatus();}
  };
useEffect() => {loadGatewayStatus();}    // 每30秒自动刷新/;,/g,/;
  interval: setInterval(loadGatewayStatus, 30000);
}
    return () => clearInterval(interval);}
  }, []);  // 检查是否需要添加依赖项;/;,/g/;
const  getStatusColor = useCallback((status: string) => {';,}switch (status) {';,}case 'healthy': return '#4CAF50';';,'';
case 'unhealthy': return '#F44336';';,'';
case 'unknown': return '#FF9800';';'';
}
      const default = return '#9E9E9E';'}'';'';
    }
  };
const  getStatusText = useCallback((status: string) => {switch (status) {}}
}
    ;}
  };
const  getCircuitBreakerColor = useCallback((state: string) => {';,}switch (state) {';,}case 'CLOSED': return '#4CAF50';';,'';
case 'OPEN': return '#F44336';';,'';
case 'HALF_OPEN': return '#FF9800';';'';
}
      const default = return '#9E9E9E';'}'';'';
    }
  };
if (loading && !refreshing) {}
    return (<View style={styles.container}>);
        <Text style={styles.loadingText}>加载网关状态中...</Text>)/;/g/;
      </View>)/;/g/;
    );
  }
  return (<ScrollView;  />/;,)style={styles.container}/g/;
      refreshControl={}
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh}  />/;/g/;
      }
    >;
      <View style={styles.header}>;
        <Text style={styles.title}>API Gateway 监控</Text>/;/g/;
        <TouchableOpacity style={styles.clearButton} onPress={clearCache}>;
          <Text style={styles.clearButtonText}>清除缓存</Text>/;/g/;
        </TouchableOpacity>/;/g/;
      </View>/;/g/;
      {error  && <View style={styles.errorContainer}>);
          <Text style={styles.errorText}>⚠️ {error}</Text>)/;/g/;
        </View>)/;/g/;
      )}
      {}
      {gatewayStats  && <View style={styles.statsContainer}>;
          <Text style={styles.sectionTitle}>网关统计</Text>/;/g/;
          <View style={styles.statRow}>;
            <Text style={styles.statLabel}>网关状态: </Text>'/;'/g'/;
            <View style={[ />/;,]styles.statusDot, {'}'';'/g'/;
];
const backgroundColor = gatewayStats.gatewayHealth ? '#4CAF50' : '#F44336';}}]} />'/;'/g'/;
            <Text style={styles.statValue}>;

            </Text>/;/g/;
          </View>/;/g/;
          <View style={styles.statRow}>;
            <Text style={styles.statLabel}>熔断器状态: </Text>/;/g/;
            <View style={[ />/;,]styles.statusDot, {}/g/;
];
const backgroundColor = getCircuitBreakerColor(gatewayStats.circuitBreakerState);}}]} />/;/g/;
            <Text style={styles.statValue}>{gatewayStats.circuitBreakerState}</Text>/;/g/;
          </View>/;/g/;
          <View style={styles.statRow}>;
            <Text style={styles.statLabel}>缓存大小: </Text>/;/g/;
            <Text style={styles.statValue}>{gatewayStats.cacheStats.size} 项</Text>/;/g/;
          </View>/;/g/;
        </View>/;/g/;
      )}
      {}
      <View style={styles.servicesContainer}>;
        <Text style={styles.sectionTitle}>微服务状态</Text>/;/g/;
        {services.map(service, index) => ())}
          <View key={index} style={styles.serviceItem}>;
            <View style={styles.serviceHeader}>;
              <View style={[styles.statusDot, { backgroundColor: getStatusColor(service.status) ;}}]}  />/;/g/;
              <Text style={styles.serviceName}>{service.name}</Text>/;/g/;
              <Text style={[styles.serviceStatus, { color: getStatusColor(service.status) ;}}]}>;
                {getStatusText(service.status)}
              </Text>/;/g/;
            </View>/;/g/;
            <View style={styles.serviceDetails}>;
              <Text style={styles.serviceDetail}>实例数: {service.instances}</Text>/;/g/;
              {service.responseTime  && <Text style={styles.serviceDetail}>响应时间: {service.responseTime}ms</Text>/;/g/;
              )}
              {service.lastCheck  && <Text style={styles.serviceDetail}>;

                </Text>/;/g/;
              )}
              {service.error  && <Text style={styles.errorDetail}>错误: {service.error}</Text>/;/g/;
              )}
            </View>/;/g/;
          </View>/;/g/;
        ))}
      </View>/;/g/;
      <View style={styles.footer}>;
        <Text style={styles.footerText}>;

        </Text>/;/g/;
        <Text style={styles.footerText}>;

        </Text>/;/g/;
      </View>/;/g/;
    </ScrollView>/;/g/;
  );
};
const  styles = StyleSheet.create({)container: {,';}}'';
  flex: 1,'}'';
backgroundColor: '#f5f5f5';},';,'';
header: {,';,}flexDirection: 'row';','';
justifyContent: 'space-between';','';
alignItems: 'center';','';
padding: 16,';,'';
backgroundColor: '#fff';','';'';
}
    borderBottomWidth: 1,'}'';
borderBottomColor: '#e0e0e0';},';,'';
title: {,';,}fontSize: 20,';'';
}
    fontWeight: 'bold';','}';,'';
color: '#333';},';,'';
clearButton: {,';,}backgroundColor: '#2196F3';','';
paddingHorizontal: 12,;
}
    paddingVertical: 6,}
    borderRadius: 4;},';,'';
clearButtonText: {,';,}color: '#fff';','';'';
}
    fontSize: 12,'}'';
fontWeight: '500';},';,'';
loadingText: {,';,}textAlign: 'center';','';
marginTop: 50,';'';
}
    fontSize: 16,'}'';
color: '#666';},';,'';
errorContainer: {margin: 16,';,'';
padding: 12,';,'';
backgroundColor: '#ffebee';','';
borderRadius: 8,';'';
}
    borderLeftWidth: 4,'}'';
borderLeftColor: '#f44336';},';,'';
errorText: {,';}}'';
  color: '#c62828';','}'';
fontSize: 14;}
statsContainer: {margin: 16,';,'';
padding: 16,';,'';
backgroundColor: '#fff';','';
borderRadius: 8,';,'';
elevation: 2,';'';
}
    shadowColor: '#000';',}'';
shadowOffset: { width: 0, height: 2 ;}
shadowOpacity: 0.1,;
shadowRadius: 4;}
sectionTitle: {,';,}fontSize: 18,';,'';
fontWeight: 'bold';','';'';
}
    color: '#333';','}'';
marginBottom: 12;},';,'';
statRow: {,';,}flexDirection: 'row';','';'';
}
    alignItems: 'center';',}'';
marginBottom: 8;}
statLabel: {,';,}fontSize: 14,';'';
}
    color: '#666';',}'';
minWidth: 100;}
statValue: {,';,}fontSize: 14,';,'';
color: '#333';','';'';
}
    fontWeight: '500';','}'';
marginLeft: 8;}
statusDot: {width: 8,;
height: 8,;
}
    borderRadius: 4,}
    marginRight: 8;}
servicesContainer: {,;}}
  margin: 16,}
    marginTop: 0;},';,'';
serviceItem: {,';,}backgroundColor: '#fff';','';
borderRadius: 8,;
padding: 16,;
marginBottom: 8,';,'';
elevation: 1,';'';
}
    shadowColor: '#000';',}'';
shadowOffset: { width: 0, height: 1 ;}
shadowOpacity: 0.05,;
shadowRadius: 2;},';,'';
serviceHeader: {,';,}flexDirection: 'row';','';'';
}
    alignItems: 'center';',}'';
marginBottom: 8;}
serviceName: {,';,}fontSize: 16,';,'';
fontWeight: '600';','';'';
}
    color: '#333';','}'';
flex: 1;}
serviceStatus: {,';}}'';
  fontSize: 14,'}'';
fontWeight: '500';},';,'';
serviceDetails: {,}
  paddingLeft: 16;}
serviceDetail: {,';,}fontSize: 12,';'';
}
    color: '#666';',}'';
marginBottom: 2;}
errorDetail: {,';,}fontSize: 12,';'';
}
    color: '#f44336';',}'';
marginTop: 4;}
footer: {,';}}'';
  padding: 16,'}'';
alignItems: 'center';},';,'';
footerText: {,)';,}fontSize: 12,)';'';
}
    color: '#999';')',}'';
const marginBottom = 4;}});';,'';
export default GatewayMonitor;