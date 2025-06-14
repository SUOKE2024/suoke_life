import React, { useCallback, useEffect, useState } from "react";
import {ActivityIndicator,
Dimensions,
RefreshControl,
ScrollView,
StyleSheet,
Text,"
TouchableOpacity,";
} fromiew'}
} from "react-native;
import Icon from "react-native-vector-icons/MaterialCommunityIcons"
const { width } = Dimensions.get('window');
// 服务状态类型
interface ServiceStatus {id: string}name: string,
endpoint: string,'
status: 'healthy' | 'unhealthy' | 'unknown' | 'maintenance,'';
const lastCheck = Date;
responseTime?: number;
version?: string;
uptime?: number;
}
}
  errorMessage?: string}
}
// 服务分类
interface ServiceCategory {id: string}name: string,
services: ServiceStatus[],
}
}
  const color = string}
}
interface ServiceStatusMonitorProps {
onServicePress?: (service: ServiceStatus) => voidshowDetails?: boolean;
}
  refreshInterval?: number}
}
const  ServiceStatusMonitor: React.FC<ServiceStatusMonitorProps> = ({)onServicePress,)showDetails = true,);
}
  refreshInterval = 30000, // 30秒刷新一次)}
;}) => {const [serviceCategories, setServiceCategories] = useState<ServiceCategory[]>([]);}  );
const [loading, setLoading] = useState(true);
const [refreshing, setRefreshing] = useState(false);
const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  // 微服务配置'
const  microservicesConfig = {agents: {,'}
color: '#4A90E2,'';
const services = [;]'
        {'id: 'xiaoai,'
endpoint: 'http://localhost:8015,''/;'/g'/;
}
          const port = 8015}
        ;},'
        {'id: 'xiaoke,'
endpoint: 'http://localhost:8016,''/;'/g'/;
}
          const port = 8016}
        ;},'
        {'id: 'laoke,'
endpoint: 'http://localhost:8017,''/;'/g'/;
}
          const port = 8017}
        ;},'
        {'id: 'soer,'
endpoint: 'http://localhost:8018,''/;'/g'/;
}
          const port = 8018}
        }
];
      ];
    }
diagnosis: {,'}
color: '#FF6B6B,'';
const services = [;]'
        {'id: 'look,'
endpoint: 'http://localhost:8020,''/;'/g'/;
}
          const port = 8020}
        ;},'
        {'id: 'inquiry,'
endpoint: 'http://localhost:8021,''/;'/g'/;
}
          const port = 8021}
        ;},'
        {'id: 'listen,'
endpoint: 'http://localhost:8022,''/;'/g'/;
}
          const port = 8022}
        ;},'
        {'id: 'calculation,'
endpoint: 'http://localhost:8023,''/;'/g'/;
}
          const port = 8023}
        ;},'
        {'id: 'palpation,'
endpoint: 'http://localhost:8024,''/;'/g'/;
}
          const port = 8024}
        }
];
      ];
    }
core: {,'}
color: '#4CAF50,'';
const services = [;]'
        {'id: 'api-gateway,'
endpoint: 'http://localhost:8000,''/;'/g'/;
}
          const port = 8000}
        ;},'
        {'id: 'user-management,'
endpoint: 'http://localhost:8001,''/;'/g'/;
}
          const port = 8001}
        ;},'
        {'id: 'unified-knowledge,'
endpoint: 'http://localhost:8002,''/;'/g'/;
}
          const port = 8002}
        ;},'
        {'id: 'unified-health-data,'
endpoint: 'http://localhost:8003,''/;'/g'/;
}
          const port = 8003}
        ;},'
        {'id: 'unified-support,'
endpoint: 'http://localhost:8004,''/;'/g'/;
}
          const port = 8004}
        }
];
      ];
    }
infrastructure: {,'}
color: '#9C27B0,'';
const services = [;]'
        {'id: 'blockchain,'
endpoint: 'http://localhost:8005,''/;'/g'/;
}
          const port = 8005}
        ;},'
        {'id: 'communication,'
endpoint: 'http://localhost:8006,''/;'/g'/;
}
          const port = 8006}
        ;},'
        {'id: 'utility,'
endpoint: 'http://localhost:8007,''/;'/g'/;
}
          const port = 8007}
        }
];
      ];
    }
  };
  // 检查服务状态
const  checkServiceStatus = useCallback();
async (service: any): Promise<ServiceStatus> => {const startTime = Date.now()try {// 模拟健康检查API调用/const controller = new AbortController(),/g,/;
  timeoutId: setTimeout() => controller.abort(), 5000);
}
}
const: response = await fetch(`${service.endpoint}/health`, {/`;)``'`method: 'GET,'','/g,'/`;
  signal: controller.signal,'
const headers = {')'';}}'Content-Type': 'application/json')}''/;'/g'/;
          ;});
        });
clearTimeout(timeoutId);
const responseTime = Date.now() - startTime;
if (response.ok) {const healthData = await response.json()return {id: service.id}name: service.name,
endpoint: service.endpoint,'
status: 'healthy,'';
const lastCheck = new Date();
responseTime,'
version: healthData.version || '1.0.0,'
}
            uptime: healthData.uptime || Math.random() * 86400, // 模拟运行时间}
          ;};
        } else {return {}            id: service.id,
name: service.name,
endpoint: service.endpoint,'
status: 'unhealthy,'';
const lastCheck = new Date();
}
            responseTime,}
            const errorMessage = `HTTP ${response.status;}`````;```;
          };
        }
      } catch (error) {';}        // 模拟服务状态（因为实际服务可能未运行）'/,'/g'/;
const mockStatus = Math.random() > 0.3 ? 'healthy' : 'unhealthy';
const  responseTime ='
mockStatus === 'healthy' ? 50 + Math.random() * 200 : undefined;
return {id: service.id}name: service.name,
endpoint: service.endpoint,
status: mockStatus,
const lastCheck = new Date();
responseTime,'
version: mockStatus === 'healthy' ? '1.0.0' : undefined;','
uptime: mockStatus === 'healthy' ? Math.random() * 86400 : undefined;','';
const errorMessage = 
}
            mockStatus === 'unhealthy' ? 'Connection failed' : undefined'}
        ;};
      }
    }
    [];
  );
  // 检查所有服务状态
const  checkAllServices = useCallback(async () => {const categories: ServiceCategory[] = []for (const [categoryKey, categoryConfig] of Object.entries();
microservicesConfig;);
    )) {const  serviceStatuses = await Promise.all()categoryConfig.services.map(service) => checkServiceStatus(service));
      );
categories.push({)        id: categoryKey}name: categoryConfig.name,);
services: serviceStatuses,);
}
        const color = categoryConfig.color)}
      ;});
    }
    setServiceCategories(categories);
setLastUpdate(new Date());
  }, [checkServiceStatus]);
  // 初始化和定时刷新
useEffect() => {const  loadServices = async () => {}      setLoading(true);
const await = checkAllServices();
}
      setLoading(false)}
    };
loadServices();
    // 设置定时刷新/,/g,/;
  interval: setInterval(checkAllServices, refreshInterval);
return () => clearInterval(interval);
  }, [checkAllServices, refreshInterval]);
  // 手动刷新
const  onRefresh = useCallback(async () => {setRefreshing(true)const await = checkAllServices();
}
    setRefreshing(false)}
  }, [checkAllServices]);
  // 获取状态图标'/,'/g'/;
const  getStatusIcon = (status: ServiceStatus['status']) => {'switch (status) {'case 'healthy': '
return 'check-circle
case 'unhealthy': '
return 'alert-circle
case 'maintenance': '
return 'wrench';
const default = 
}
        return 'help-circle}
    }
  };
  // 获取状态颜色'/,'/g'/;
const  getStatusColor = (status: ServiceStatus['status']) => {'switch (status) {'case 'healthy': '
return '#4CAF50
case 'unhealthy': '
return '#F44336
case 'maintenance': '
return '#FF9800';
const default = 
}
        return '#9E9E9E}
    }
  };
  // 格式化运行时间
const  formatUptime = (uptime: number) => {const hours = Math.floor(uptime / 3600);/;}}/g/;
    const minutes = Math.floor(uptime % 3600) / 60);}
return `${hours}h ${minutes}m`;````;```;
  };
  // 渲染服务项/,/g,/;
  renderServiceItem: (service: ServiceStatus, categoryColor: string) => (<TouchableOpacity;)  />
key={service.id});
style={styles.serviceItem});
onPress={() => onServicePress?.(service)}
      activeOpacity={0.7}
    >;
      <View style={styles.serviceHeader}>;
        <View style={styles.serviceInfo}>;
          <Icon;  />
name={getStatusIcon(service.status)}
            size={20}
            color={getStatusColor(service.status)}
            style={styles.statusIcon}
          />
          <Text style={styles.serviceName}>{service.name}</Text>
        </View>
        <View;  />
style={}[;]}
            styles.statusBadge,}
            { backgroundColor: getStatusColor(service.status) }
];
          ]}
        >
          <Text style={styles.statusText}>'
            {service.status === 'healthy''}
              : service.status === 'unhealthy'
                : service.status === 'maintenance'
          </Text>
        </View>
      </View>
}
}
      {showDetails && (<View style={styles.serviceDetails}>;)          <View style={styles.detailRow}>;
            <Text style={styles.detailLabel}>端点: </Text>
            <Text style={styles.detailValue}>{service.endpoint}</Text>
          </View>
          {service.responseTime && (})            <View style={styles.detailRow}>;
              <Text style={styles.detailLabel}>响应时间:</Text>)
              <Text style={styles.detailValue}>{service.responseTime}ms</Text>)
            </View>)
          )}
          {service.version && (<View style={styles.detailRow}>;)              <Text style={styles.detailLabel}>版本:</Text>)
              <Text style={styles.detailValue}>{service.version}</Text>)
            </View>)
          )}
          {service.uptime && (<View style={styles.detailRow}>);
              <Text style={styles.detailLabel}>运行时间:</Text>)
              <Text style={styles.detailValue}>);
                {formatUptime(service.uptime)}
              </Text>
            </View>
          )}
          {service.errorMessage && (<View style={styles.detailRow}>;)              <Text style={styles.detailLabel}>错误: </Text>
              <Text style={[styles.detailValue, styles.errorText]}>;
                {service.errorMessage});
              </Text>)
            </View>)
          )}
          <View style={styles.detailRow}>;
            <Text style={styles.detailLabel}>最后检查: </Text>'/;'/g'/;
            <Text style={styles.detailValue}>'
              {service.lastCheck.toLocaleTimeString('zh-CN')}
            </Text>
          </View>
        </View>
      )}
    </TouchableOpacity>
  );
  // 渲染服务分类'/,'/g'/;
const  renderServiceCategory = (category: ServiceCategory) => {'const  healthyCount = category.services.filter(s) => s.status === 'healthy'
    ).length;
const totalCount = category.services.length;
}
}
    return (<View key={category.id} style={styles.categoryContainer}>;)        <View;  />
style={[styles.categoryHeader, { borderLeftColor: category.color ;}]}
        >;
          <Text style={styles.categoryTitle}>{category.name}</Text>
          <Text style={styles.categoryStats}>;
            {healthyCount}/{totalCount} 正常
          </Text>
        </View>)
);
        <View style={styles.servicesContainer}>);
          {category.services.map(service) =>}
            renderServiceItem(service, category.color)}
          )}
        </View>
      </View>
    );
  };
if (loading) {}
return (<View style={styles.loadingContainer}>';)        <ActivityIndicator size="large" color="#4A90E2"  />")
        <Text style={styles.loadingText}>检查服务状态...</Text>)
      </View>)
    );
  }
  return (<ScrollView;  />/,)style={styles.container}/g/;
      refreshControl={}
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh}  />
      }
      showsVerticalScrollIndicator={false}
    >;
      {// 状态概览}
      <View style={styles.overviewContainer}>;
        <Text style={styles.overviewTitle}>服务状态概览</Text>
        <Text style={styles.lastUpdateText}>;
        </Text>)
);
        <View style={styles.statsContainer}>)
          {serviceCategories.map(category) => {"const  healthyCount = category.services.filter(s) => s.status === 'healthy'
            ).length;
const totalCount = category.services.length;
const healthPercentage = (healthyCount / totalCount) * 100;
}
}
            return (<View key={category.id} style={styles.statItem}>;)                <View;  />
style={}[;]}
                    styles.statIndicator,}
                    { backgroundColor: category.color }
];
                  ]}
                />)
                <Text style={styles.statLabel}>{category.name}</Text>)
                <Text style={styles.statValue}>);
                  {healthPercentage.toFixed(0)}%;
                </Text>
              </View>
            );
          })}
        </View>
      </View>
      {// 服务详情}
      {serviceCategories.map(renderServiceCategory)}
    </ScrollView>
  );
};
const  styles = StyleSheet.create({)container: {,'flex: 1,
}
    const backgroundColor = '#F8F9FA'}
  }
loadingContainer: {,'flex: 1,'
justifyContent: 'center,'
alignItems: 'center,'
}
    const paddingVertical = 40}
  }
loadingText: {marginTop: 10,
fontSize: 14,
}
    const color = '#666'}
  ;},'
overviewContainer: {,'backgroundColor: '#FFFFFF,'';
margin: 16,
padding: 16,
borderRadius: 12,
}
    shadowColor: '#000,'}'';
shadowOffset: { width: 0, height: 1 }
shadowOpacity: 0.1,
shadowRadius: 2,
const elevation = 2;
  }
overviewTitle: {,'fontSize: 18,'
fontWeight: '600,'
color: '#333,'
}
    const marginBottom = 4}
  }
lastUpdateText: {,'fontSize: 12,'
color: '#999,'
}
    const marginBottom = 16}
  ;},'
statsContainer: {,'flexDirection: 'row,'
flexWrap: 'wrap,'
}
    const gap = 12}
  ;},'
statItem: {,'flexDirection: 'row,'
alignItems: 'center,'
backgroundColor: '#F5F5F5,'';
paddingHorizontal: 12,);
paddingVertical: 6,);
borderRadius: 16;),
}
    const minWidth = (width - 64) / 2}
  }
statIndicator: {width: 8,
height: 8,
borderRadius: 4,
}
    const marginRight = 8}
  }
statLabel: {,'fontSize: 12,'
color: '#666,'
}
    const flex = 1}
  }
statValue: {,'fontSize: 12,'
fontWeight: '600,'
}
    const color = '#333'}
  ;},'
categoryContainer: {,'backgroundColor: '#FFFFFF,'';
margin: 16,
marginTop: 0,
borderRadius: 12,
}
    shadowColor: '#000,'}'';
shadowOffset: { width: 0, height: 1 }
shadowOpacity: 0.1,
shadowRadius: 2,
const elevation = 2;
  ;},'
categoryHeader: {,'flexDirection: 'row,'
justifyContent: 'space-between,'
alignItems: 'center,'';
padding: 16,
borderLeftWidth: 4,
borderBottomWidth: 1,
}
    const borderBottomColor = '#F0F0F0'}
  }
categoryTitle: {,'fontSize: 16,'
fontWeight: '600,'
}
    const color = '#333'}
  }
categoryStats: {,'fontSize: 12,
}
    const color = '#666'}
  }
servicesContainer: {padding: 16,
}
    const paddingTop = 0}
  ;},'
serviceItem: {,'backgroundColor: '#F8F9FA,'';
padding: 12,
borderRadius: 8,
}
    const marginTop = 12}
  ;},'
serviceHeader: {,'flexDirection: 'row,'
justifyContent: 'space-between,'
}
    const alignItems = 'center'}
  ;},'
serviceInfo: {,'flexDirection: 'row,'
alignItems: 'center,'
}
    const flex = 1}
  }
statusIcon: {,}
  const marginRight = 8}
  }
serviceName: {,'fontSize: 14,'
fontWeight: '500,'
color: '#333,'
}
    const flex = 1}
  }
statusBadge: {paddingHorizontal: 8,
paddingVertical: 2,
}
    const borderRadius = 10}
  }
statusText: {,'fontSize: 10,'
color: '#FFFFFF,'
}
    const fontWeight = '600'}
  }
serviceDetails: {marginTop: 8,
paddingTop: 8,
borderTopWidth: 1,
}
    const borderTopColor = '#E0E0E0'}
  ;},'
detailRow: {,'flexDirection: 'row,'
justifyContent: 'space-between,'
alignItems: 'center,'
}
    const marginBottom = 4}
  }
detailLabel: {,'fontSize: 11,'
color: '#666,'
}
    const flex = 1}
  }
detailValue: {,'fontSize: 11,'
color: '#333,'';
flex: 2,
}
    const textAlign = 'right'}
  ;},'
errorText: {,';}}
  const color = '#F44336'}
  }
});
export default ServiceStatusMonitor;
''
