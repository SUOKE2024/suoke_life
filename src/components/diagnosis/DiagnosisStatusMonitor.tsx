import React, { useState, useEffect, useCallback } from "react";";
import {import { fiveDiagnosisService, FiveDiagnosisServiceStatus } from "../../services/fiveDiagnosisService";""/;,"/g"/;
View,;
Text,;
StyleSheet,;
TouchableOpacity,;
ActivityIndicator,;
Animated,";,"";
Dimensions;';'';
} from "react-native";";
interface DiagnosisStatusMonitorProps {onStatusChange?: (status: FiveDiagnosisServiceStatus) => void;,}showDetails?: boolean;
}
}
  refreshInterval?: number;}
}
interface ServiceHealth {inquiry: boolean}look: boolean,;
listen: boolean,;
palpation: boolean,;
}
}
  const calculation = boolean;}
}
export default React.memo(function DiagnosisStatusMonitor({)onStatusChange,);,}showDetails = false,);
}
  refreshInterval = 30000 // 30秒刷新一次)}/;/g/;
}: DiagnosisStatusMonitorProps) {;};
}
  const [status, setStatus] = useState<FiveDiagnosisServiceStatus>({isInitialized: false,isProcessing: false,performanceMetrics: {averageResponseTime: 0,successRate: 0,totalSessions: 0;)}
    };
  });
const [serviceHealth, setServiceHealth] = useState<ServiceHealth>({inquiry: false,look: false,listen: false,palpation: false,calculation: false;)}
  });
const [isRefreshing, setIsRefreshing] = useState(false);
const [lastUpdateTime, setLastUpdateTime] = useState<Date>(new Date());
  // 动画值/;,/g/;
const pulseAnimation = React.useRef(new Animated.Value(1)).current;
const fadeAnimation = React.useRef(new Animated.Value(1)).current;
  // 更新状态/;,/g/;
const updateStatus = useCallback(async () => {try {setIsRefreshing(true););}      // 获取服务状态/;,/g/;
const serviceStatus = fiveDiagnosisService.getServiceStatus();
setStatus(serviceStatus);
      // 检查各个服务的健康状态/;/g/;
      // 注意：这里需要实际的健康检查API;/;/g/;
      // 暂时使用模拟数据/;,/g,/;
  const: healthStatus: ServiceHealth = {inquiry: Math.random() > 0.1, // 90% 可用性/;,/g,/;
  look: Math.random() > 0.1,;
listen: Math.random() > 0.1,;
palpation: Math.random() > 0.1,;
}
        const calculation = Math.random() > 0.1;}
      };
setServiceHealth(healthStatus);
setLastUpdateTime(new Date());
      // 通知父组件状态变化/;,/g/;
if (onStatusChange) {}}
        onStatusChange(serviceStatus);}
      }
    } catch (error) {}}
}
    } finally {}}
      setIsRefreshing(false);}
    }
  }, [onStatusChange]);
  // 定期更新状态/;,/g/;
useEffect() => {updateStatus();,}interval: setInterval(updateStatus, refreshInterval);
}
    return () => clearInterval(interval);}
  }, [updateStatus, refreshInterval]);
  // 状态变化时的动画效果/;,/g/;
useEffect() => {if (status.isProcessing) {}      // 处理中的脉冲动画/;,/g/;
Animated.loop();
Animated.sequence([;));,]Animated.timing(pulseAnimation, {)            toValue: 1.2,);,}duration: 1000,);
}
            const useNativeDriver = true;)}
          }),;
Animated.timing(pulseAnimation, {)toValue: 1,);,}duration: 1000,);
}
            const useNativeDriver = true;)}
          });
];
        ]);
      ).start();
    } else {}}
      pulseAnimation.setValue(1);}
    }
  }, [status.isProcessing, pulseAnimation]);';'';
  // 获取整体健康状态'/;,'/g'/;
const getOverallHealth = (): 'healthy' | 'warning' | 'error' => {const healthyServices = Object.values(serviceHealth).filter(Boolean).length;';,}const totalServices = Object.values(serviceHealth).length;';,'';
if (healthyServices === totalServices) return 'healthy';';,'';
if (healthyServices >= totalServices * 0.8) return 'warning';';'';
}
    return 'error';'}'';'';
  };';'';
  // 获取状态颜色'/;,'/g'/;
const getStatusColor = (health: 'healthy' | 'warning' | 'error'): string => {switch (health) {case 'healthy': return '#28a745';';,}case 'warning': return '#ffc107';';'';
}
      case 'error': return '#dc3545';'}'';'';
    }
  };';'';
  // 获取状态图标'/;,'/g'/;
const getStatusIcon = (health: 'healthy' | 'warning' | 'error'): string => {switch (health) {case 'healthy': return '✅';';,}case 'warning': return '⚠️';';'';
}
      case 'error': return '❌';'}'';'';
    }
  };
  // 渲染服务健康状态/;,/g/;
const renderServiceHealth = () => {if (!showDetails) return null;}
    return (<View style={styles.serviceHealthContainer}>);
        <Text style={styles.sectionTitle}>服务状态</Text>)/;/g/;
        {Object.entries(serviceHealth).map([service, isHealthy]) => (;))}
          <View key={service} style={styles.serviceItem}>;
            <Text style={styles.serviceName}>;
              {getServiceDisplayName(service)};
            </Text>;'/;'/g'/;
            <View style={[ />/;];'}'';,'/g'/;
styles.serviceStatus,{ backgroundColor: isHealthy ? '#28a745' : '#dc3545' ;}};';'';
];
            ]}>;
              <Text style={styles.serviceStatusText}>;

              </Text>;/;/g/;
            </View>;/;/g/;
          </View>;/;/g/;
        ))};
      </View>;/;/g/;
    );
  };
  // 渲染性能指标/;,/g/;
const renderPerformanceMetrics = () => {if (!showDetails) return null;}
    const { performanceMetrics } = status;
return (<View style={styles.metricsContainer}>;)        <Text style={styles.sectionTitle}>性能指标</Text>/;/g/;
        <View style={styles.metricItem}>);
          <Text style={styles.metricLabel}>平均响应时间</Text>)/;/g/;
          <Text style={styles.metricValue}>);
            {Math.round(performanceMetrics.averageResponseTime)}ms;
          </Text>/;/g/;
        </View>/;/g/;
        <View style={styles.metricItem}>;
          <Text style={styles.metricLabel}>成功率</Text>;'/;'/g'/;
          <Text style={[ />/;];'}'';,'/g'/;
styles.metricValue,{ color: performanceMetrics.successRate > 0.9 ? '#28a745' : '#ffc107' ;}};';'';
];
          ]}>;
            {Math.round(performanceMetrics.successRate * 100)}%;
          </Text>;/;/g/;
        </View>;/;/g/;
        <View style={styles.metricItem}>;
          <Text style={styles.metricLabel}>总会话数</Text>;/;/g/;
          <Text style={styles.metricValue}>;
            {performanceMetrics.totalSessions};
          </Text>;/;/g/;
        </View>;/;/g/;
      </View>;/;/g/;
    );
  };
  // 获取服务显示名称/;,/g,/;
  const: getServiceDisplayName = (service: string): string => {const names: Record<string, string> = {}}
}
    ;};
return names[service] || service;
  };
const overallHealth = getOverallHealth();
const statusColor = getStatusColor(overallHealth);
const statusIcon = getStatusIcon(overallHealth);
return (<View style={styles.container}>;)      {// 主状态指示器}/;/g/;
      <TouchableOpacity;  />/;,/g/;
style={styles.mainStatus}
        onPress={updateStatus}
        disabled={isRefreshing}
      >;
        <Animated.View;  />/;,/g/;
style={[;,]styles.statusIndicator,;}            {}}
              backgroundColor: statusColor,}
];
const transform = [{ scale: pulseAnimation ;}}];
            });
          ]});
        >)';'';
          {isRefreshing ? ()';}}'';
            <ActivityIndicator size="small" color="#ffffff"  />"}""/;"/g"/;
          ) : (<Text style={styles.statusIcon}>{statusIcon}</Text>)/;/g/;
          )}
        </Animated.View>/;/g/;
        <View style={styles.statusInfo}>;
          <Text style={styles.statusTitle}>;

          </Text>/;/g/;
          <Text style={styles.statusSubtitle}>;

          </Text>/;/g/;
        </View>;/;/g/;
      </TouchableOpacity>;/;/g/;
      {// 详细信息};/;/g/;
      {showDetails && (;);}        <Animated.View ;  />/;/g/;
}
          style={[;];}
            styles.detailsContainer,{ opacity: fadeAnimation ;}};
];
          ]};
        >;
          {renderServiceHealth()};
          {renderPerformanceMetrics()};
        </Animated.View>;/;/g/;
      )};
    </View>;/;/g/;
  );
}
const  styles = StyleSheet.create({)";,}container: {,";,}backgroundColor: '#ffffff';','';
borderRadius: 12,;
padding: 16,';,'';
marginVertical: 8,';,'';
shadowColor: '#000';','';
shadowOffset: {width: 0,;
}
      const height = 2;}
    }
shadowOpacity: 0.1,;
shadowRadius: 4,;
const elevation = 3;
  },';,'';
mainStatus: {,';,}flexDirection: 'row';','';'';
}
    const alignItems = 'center'}'';'';
  ;}
statusIndicator: {width: 40,;
height: 40,';,'';
borderRadius: 20,';,'';
alignItems: 'center';','';
justifyContent: 'center';','';'';
}
    const marginRight = 12;}
  }
statusIcon: {,';,}fontSize: 20,';'';
}
    const color = '#ffffff'}'';'';
  ;}
statusInfo: {,;}}
  const flex = 1;}
  }
statusTitle: {,';,}fontSize: 16,';,'';
fontWeight: '600';','';
color: '#1a1a1a';','';'';
}
    const marginBottom = 2;}
  }
statusSubtitle: {,';,}fontSize: 14,';'';
}
    const color = '#6c757d'}'';'';
  ;}
detailsContainer: {marginTop: 16,;
paddingTop: 16,';,'';
borderTopWidth: 1,';'';
}
    const borderTopColor = '#e9ecef'}'';'';
  ;}
sectionTitle: {,';,}fontSize: 16,';,'';
fontWeight: '600';','';
color: '#1a1a1a';','';'';
}
    const marginBottom = 12;}
  }
serviceHealthContainer: {,;}}
  const marginBottom = 20;}
  },';,'';
serviceItem: {,';,}flexDirection: 'row';','';
justifyContent: 'space-between';','';
alignItems: 'center';','';'';
}
    const paddingVertical = 8;}
  }
serviceName: {,';,}fontSize: 14,';'';
}
    const color = '#1a1a1a'}'';'';
  ;}
serviceStatus: {paddingHorizontal: 8,;
paddingVertical: 4,;
}
    const borderRadius = 4;}
  }
serviceStatusText: {,';,}fontSize: 12,';,'';
color: '#ffffff';','';'';
}
    const fontWeight = '500'}'';'';
  ;}
const metricsContainer = {}}
    // 样式已在上面定义}'/;'/g'/;
  ;},metricItem: {,';,}flexDirection: "row";","";"";
}
      justifyContent: 'space-between',alignItems: 'center',paddingVertical: 6;'}'';'';
  },metricLabel: {fontSize: 14,color: '#6c757d';')}'';'';
  },metricValue: {fontSize: 14,fontWeight: '600',color: '#1a1a1a';')}'';'';
  };);
});';'';
);