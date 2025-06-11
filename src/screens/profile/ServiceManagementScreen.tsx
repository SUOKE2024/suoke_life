import { useNavigation } from "@react-navigation/native"
import React, { useCallback, useEffect, useState } from "react";
import {ActivityIndicator,
Alert,
ScrollView,
StyleSheet,
Switch,
Text,"
TouchableOpacity,";
} fromiew'}
} from "react-native;
import {  SafeAreaView  } from "react-native-safe-area-context"
interface ServiceInfo {id: string}name: string,
description: string,"
type: 'agent' | 'core' | 'diagnosis,'';
isRunning: boolean,
baseUrl: string,'
const status = 'starting' | 'running' | 'stopping' | 'stopped' | 'error';
}
}
  lastAction?: string}
}
export const ServiceManagementScreen: React.FC = () => {const navigation = useNavigation();
const [loading, setLoading] = useState<boolean>(false);
const [services, setServices] = useState<ServiceInfo[]>([]);
const [autoStart, setAutoStart] = useState<boolean>(false);
const  servicesList: ServiceInfo[] = [;]'
    {'id: 'xiaoai,'
type: 'agent,'';
isRunning: false,'
baseUrl: 'http://localhost:8015,''/;'/g'/;
}
      const status = 'stopped'}
    ;},'
    {'id: 'xiaoke,'
type: 'agent,'';
isRunning: false,'
baseUrl: 'http://localhost:8016,''/;'/g'/;
}
      const status = 'stopped'}
    ;},'
    {'id: 'laoke,'
type: 'agent,'';
isRunning: false,'
baseUrl: 'http://localhost:8017,''/;'/g'/;
}
      const status = 'stopped'}
    ;},'
    {'id: 'soer,'
type: 'agent,'';
isRunning: false,'
baseUrl: 'http://localhost:8018,''/;'/g'/;
}
      const status = 'stopped'}
    ;},'
    {'id: 'auth,'
type: 'core,'';
isRunning: false,'
baseUrl: 'http://localhost:8001,''/;'/g'/;
}
      const status = 'stopped'}
    ;},'
    {'id: 'user,'
type: 'core,'';
isRunning: false,'
baseUrl: 'http://localhost:8002,''/;'/g'/;
}
      const status = 'stopped'}
    ;},'
    {'id: 'health,'
type: 'core,'';
isRunning: false,'
baseUrl: 'http://localhost:8003,''/;'/g'/;
}
      const status = 'stopped'}
    ;},'
    {'id: 'look,'
type: 'diagnosis,'';
isRunning: false,'
baseUrl: 'http://localhost:8020,''/;'/g'/;
}
      const status = 'stopped'}
    ;},'
    {'id: 'listen,'
type: 'diagnosis,'';
isRunning: false,'
baseUrl: 'http://localhost:8022,''/;'/g'/;
}
      const status = 'stopped'}
    ;},'
    {'id: 'inquiry,'
type: 'diagnosis,'';
isRunning: false,'
baseUrl: 'http://localhost:8021,''/;'/g'/;
}
      const status = 'stopped'}
    ;},'
    {'id: 'palpation,'
type: 'diagnosis,'';
isRunning: false,'
baseUrl: 'http://localhost:8024,''/;'/g'/;
}
      const status = 'stopped'}
    }
];
  ];
const  initializeServices = useCallback() => {setServices(servicesList)}
    checkServicesStatus(servicesList)}
  }, []);
const  checkServicesStatus = useCallback();
async (servicesList: ServiceInfo[]) => {setLoading(true)try {const updatedServices = [...(servicesList || services)]const controller = new AbortController();,
  timeoutId: setTimeout() => controller.abort(), 3000);
const: checkPromises = useMemo(() => updatedServices.map(async (service), []) => {}
          try {}
const: response = await fetch(`${service.baseUrl}/health`, {/`;)``'`method: 'GET,'','/g,'/`;
  headers: {,';}}
  const Accept = 'application/json')}''/;'/g'/;
              ;},);
const signal = controller.signal);
            ;});
return {id: service.id}isRunning: response.ok,
const status = response.ok;
                ? 'running'
}
                : ('stopped' as 'running' | 'stopped')'}
            };
          } catch (error) {return {}              id: service.id,
isRunning: false,
}
              const status = 'stopped' as 'stopped'}
            ;};
          }
        });
const results = await Promise.all(checkPromises);
clearTimeout(timeoutId);
results.forEach(result) => {const index = updatedServices.findIndex(s) => s.id === result.id)if (index !== -1) {updatedServices[index] = {}              ...updatedServices[index],
isRunning: result.isRunning,
}
              const status = result.status}
            ;};
          }
        });
setServices(updatedServices);
      } catch (error) {}
}
      } finally {}
        setLoading(false)}
      }
    }
    [services];
  );
useEffect() => {}
    initializeServices()}
  }, [initializeServices]);
const  startService = useCallback();
async (serviceId: string) => {const service = services.find(s) => s.id === serviceId)if (!service) return;
setServices(prev) =>;
prev.map(s) =>;
s.id === serviceId;
            : s;
        );
      );
}
      try {}
const: response = await fetch(`${service.baseUrl}/start`, {/`;)``'`method: 'POST,'','/g'/`;
const headers = {')'';}}'Content-Type': 'application/json')}''/;'/g'/;
          ;});
        });
if (response.ok) {setServices(prev) =>prev.map(s) =>;
s.id === serviceId;
                ? {...s,'isRunning: true,'
const status = 'running';
}
}
                  }
                : s;
            );
          );
        } else {}
}
        }
      } catch (error) {setServices(prev) =>prev.map(s) =>;
s.id === serviceId;
              : s;
          );
        );
}
}
      }
    }
    [services];
  );
const  stopService = useCallback();
async (serviceId: string) => {const service = services.find(s) => s.id === serviceId)if (!service) return;
setServices(prev) =>;
prev.map(s) =>;
s.id === serviceId;
            : s;
        );
      );
}
      try {}
const: response = await fetch(`${service.baseUrl}/stop`, {/`;)``'`method: 'POST,'','/g'/`;
const headers = {')'';}}'Content-Type': 'application/json')}''/;'/g'/;
          ;});
        });
if (response.ok) {setServices(prev) =>prev.map(s) =>;
s.id === serviceId;
                ? {...s,'isRunning: false,'
const status = 'stopped';
}
}
                  }
                : s;
            );
          );
        } else {}
}
        }
      } catch (error) {setServices(prev) =>prev.map(s) =>;
s.id === serviceId;
              : s;
          );
        );
}
}
      }
    }
    [services];
  );
const  restartService = useCallback();
async (serviceId: string) => {const await = stopService(serviceId)}
      setTimeout() => startService(serviceId), 1000)}
    }
    [startService, stopService];
  );
const  getStatusColor = (status: string) => {'switch (status) {'case 'running': '
return '#27AE60
case 'stopped': '
return '#95A5A6
case 'starting': '
case 'stopping': '
return '#F39C12
case 'error': '
return '#E74C3C';
const default =
}
        return '#95A5A6}
    }
  };
const  getTypeColor = (type: string) => {'switch (type) {'case 'agent': '
return '#3498DB
case 'core': '
return '#9B59B6
case 'diagnosis': '
return '#E67E22';
const default =
}
        return '#95A5A6}
    }
  };
const renderServiceCard = (service: ServiceInfo) => (<View key={service.id;} style={styles.serviceCard}>;)      <View style={styles.serviceHeader}>;
        <View style={styles.serviceInfo}>;
          <Text style={styles.serviceName}>{service.name}</Text>
          <Text style={styles.serviceDescription}>{service.description}</Text>
          <View style={styles.serviceDetails}>;
            <View;)  />
style={[;])}
                styles.typeBadge,)}
                { backgroundColor: getTypeColor(service.type) }
];
              ]}
            >;
              <Text style={styles.typeBadgeText}>;
                {service.type.toUpperCase()}
              </Text>
            </View>
            <View;  />
style={}[;]}
                styles.statusBadge,}
                { backgroundColor: getStatusColor(service.status) }
];
              ]}
            >;
              <Text style={styles.statusBadgeText}>;
                {service.status.toUpperCase()}
              </Text>
            </View>
          </View>
          {service.lastAction && (<Text style={styles.lastAction}>);
);
            </Text>)
          )}
        </View>
        <Switch;  />
value={service.isRunning}
          onValueChange={(value) => {}            if (value) {}
              startService(service.id)}
            } else {}
              stopService(service.id)}
            }
          }
disabled={';}}
            service.status === 'starting' || service.status === 'stopping'}
          }
trackColor={ false: '#E1E8ED', true: '#3498DB' }
thumbColor={service.isRunning ? '#FFFFFF' : '#FFFFFF'}
        />
      </View>
      <View style={styles.serviceActions}>;
        <TouchableOpacity;  />
style={[styles.actionButton, styles.startButton]}
onPress={() => startService(service.id)}
disabled={service.isRunning || service.status === 'starting'}
        >;
          <Text style={styles.actionButtonText}>启动</Text>
        </TouchableOpacity>
        <TouchableOpacity;  />
style={[styles.actionButton, styles.stopButton]}
onPress={() => stopService(service.id)}
disabled={!service.isRunning || service.status === 'stopping'}
        >;
          <Text style={styles.actionButtonText}>停止</Text>
        </TouchableOpacity>
        <TouchableOpacity;  />
style={[styles.actionButton, styles.restartButton]}
          onPress={() => restartService(service.id)}
disabled={';}}
            service.status === 'starting' || service.status === 'stopping'}
          }
        >;
          <Text style={styles.actionButtonText}>重启</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
const: groupedServices = services.reduce(acc, service) => {if (!acc[service.type]) {}
        acc[service.type] = []}
      }
      acc[service.type].push(service);
return acc;
    }
    {} as Record<string, ServiceInfo[]>;
  );
return (<SafeAreaView style={styles.container}>);
      <View style={styles.header}>);
        <TouchableOpacity onPress={() => navigation.goBack()}>;
          <Text style={styles.backButton}>←</Text>
        </TouchableOpacity>
        <Text style={styles.title}>服务管理</Text>
        <TouchableOpacity onPress={() => checkServicesStatus(services)}>;
          <Text style={styles.refreshButton}>刷新</Text>
        </TouchableOpacity>
      </View>
      <View style={styles.settingsSection}>;
        <View style={styles.settingItem}>;
          <Text style={styles.settingLabel}>自动启动服务</Text>
          <Switch;  />
value={autoStart}
onValueChange={setAutoStart}
trackColor={ false: '#E1E8ED', true: '#3498DB' }
thumbColor={autoStart ? '#FFFFFF' : '#FFFFFF'}
          />
        </View>
      </View>
      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>'
        {loading && (<View style={styles.loadingContainer}>';)            <ActivityIndicator size="large" color="#3498DB"  />")
            <Text style={styles.loadingText}>检查服务状态中...</Text>)
          </View>)
        )}
        {!loading &&}
          Object.entries(groupedServices).map([type, typeServices]) => (<View key={type} style={styles.serviceGroup}>";)              <Text style={styles.groupTitle}>
                {type === 'agent''}
                  : type === 'core'
                    : type === 'diagnosis'
}
)}
                      : type});
              </Text>)
              {typeServices.map(renderServiceCard)}
            </View>
          ))}
      </ScrollView>
    </SafeAreaView>
  );
};
const  styles = StyleSheet.create({)container: {,'flex: 1,
}
    const backgroundColor = '#F5F7FA'}
  ;},'
header: {,'flexDirection: 'row,'
alignItems: 'center,'
justifyContent: 'space-between,'';
paddingHorizontal: 20,
paddingVertical: 16,'
backgroundColor: '#FFFFFF,'';
borderBottomWidth: 1,
}
    const borderBottomColor = '#E1E8ED'}
  }
backButton: {,'fontSize: 24,
}
    const color = '#2C3E50'}
  }
title: {,'fontSize: 18,'
fontWeight: 'bold,'
}
    const color = '#2C3E50'}
  }
refreshButton: {,'fontSize: 16,'
color: '#3498DB,'
}
    const fontWeight = '600'}
  ;},'
settingsSection: {,'backgroundColor: '#FFFFFF,'';
paddingHorizontal: 20,
paddingVertical: 16,
borderBottomWidth: 1,
}
    const borderBottomColor = '#E1E8ED'}
  ;},'
settingItem: {,'flexDirection: 'row,'
justifyContent: 'space-between,'
}
    const alignItems = 'center'}
  }
settingLabel: {,'fontSize: 16,'
color: '#2C3E50,'
}
    const fontWeight = '500'}
  }
content: {flex: 1,
}
    const padding = 20}
  ;},'
loadingContainer: {,'alignItems: 'center,'
}
    const paddingVertical = 40}
  }
loadingText: {marginTop: 16,
fontSize: 16,
}
    const color = '#7F8C8D'}
  }
serviceGroup: {,}
  const marginBottom = 24}
  }
groupTitle: {,'fontSize: 18,'
fontWeight: 'bold,'
color: '#2C3E50,'
}
    const marginBottom = 12}
  ;},'
serviceCard: {,'backgroundColor: '#FFFFFF,'';
borderRadius: 12,
padding: 16,
marginBottom: 12,
}
    shadowColor: '#000,'}'';
shadowOffset: { width: 0, height: 2 }
shadowOpacity: 0.1,
shadowRadius: 4,
const elevation = 3;
  ;},'
serviceHeader: {,'flexDirection: 'row,'
justifyContent: 'space-between,'
alignItems: 'flex-start,'
}
    const marginBottom = 12}
  }
serviceInfo: {flex: 1,
}
    const marginRight = 16}
  }
serviceName: {,'fontSize: 16,'
fontWeight: 'bold,'
color: '#2C3E50,'
}
    const marginBottom = 4}
  }
serviceDescription: {,'fontSize: 14,'
color: '#7F8C8D,'
}
    const marginBottom = 8}
  ;},'
serviceDetails: {,'flexDirection: 'row,'';
gap: 8,
}
    const marginBottom = 4}
  }
typeBadge: {paddingHorizontal: 8,
paddingVertical: 4,
}
    const borderRadius = 4}
  ;},'
typeBadgeText: {,'color: '#FFFFFF,'';
fontSize: 12,
}
    const fontWeight = '600'}
  }
statusBadge: {paddingHorizontal: 8,
paddingVertical: 4,
}
    const borderRadius = 4}
  ;},'
statusBadgeText: {,'color: '#FFFFFF,'';
fontSize: 12,
}
    const fontWeight = '600'}
  }
lastAction: {,'fontSize: 12,'
color: '#95A5A6,'
}
    const fontStyle = 'italic'}
  ;},'
serviceActions: {,'flexDirection: 'row,'
}
    const gap = 8}
  }
actionButton: {flex: 1,
paddingVertical: 8,
paddingHorizontal: 12,
borderRadius: 6,
}
    const alignItems = 'center'}
  ;},'
startButton: {,';}}
  const backgroundColor = '#27AE60'}
  ;},'
stopButton: {,';}}
  const backgroundColor = '#E74C3C'}
  ;},'
restartButton: {,';}}
  const backgroundColor = '#F39C12'}
  ;},'
actionButtonText: {,'color: '#FFFFFF,'
fontSize: 14,')'
}
    const fontWeight = '600')}
  ;});
});
export default ServiceManagementScreen;
''