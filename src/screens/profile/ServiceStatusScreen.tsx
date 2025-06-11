import { useNavigation } from "@react-navigation/native"
import React, { useCallback, useEffect, useState } from "react";
import {ActivityIndicator,
Alert,
RefreshControl,
ScrollView,
StyleSheet,
Text,"
TouchableOpacity,";
} fromiew'}
} from "react-native;
import {  SafeAreaView  } from "react-native-safe-area-context";
interface ServiceStatus {"
"name: string,"
const status = 'online' | 'offline' | 'unknown';
responseTime?: number;
  lastChecked: Date,
endpoint: string,
}
  const category = 'agent' | 'core' | 'diagnosis}
}
export const ServiceStatusScreen: React.FC = () => {const navigation = useNavigation();
const [loading, setLoading] = useState<boolean>(true);
const [refreshing, setRefreshing] = useState<boolean>(false);
const [services, setServices] = useState<ServiceStatus[]>([]);
const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
const  initialServices: ServiceStatus[] = [;]{'}
status: 'unknown,'';
lastChecked: new Date(),'
endpoint: 'http://localhost:8015,''/;'/g'/;
}
      const category = 'agent'}
    }
    {'}
status: 'unknown,'';
lastChecked: new Date(),'
endpoint: 'http://localhost:8016,''/;'/g'/;
}
      const category = 'agent'}
    }
    {'}
status: 'unknown,'';
lastChecked: new Date(),'
endpoint: 'http://localhost:8017,''/;'/g'/;
}
      const category = 'agent'}
    }
    {'}
status: 'unknown,'';
lastChecked: new Date(),'
endpoint: 'http://localhost:8018,''/;'/g'/;
}
      const category = 'agent'}
    }
    {'}
status: 'unknown,'';
lastChecked: new Date(),'
endpoint: 'http://localhost:8001,''/;'/g'/;
}
      const category = 'core'}
    }
    {'}
status: 'unknown,'';
lastChecked: new Date(),'
endpoint: 'http://localhost:8002,''/;'/g'/;
}
      const category = 'core'}
    }
    {'}
status: 'unknown,'';
lastChecked: new Date(),'
endpoint: 'http://localhost:8003,''/;'/g'/;
}
      const category = 'core'}
    }
    {'}
status: 'unknown,'';
lastChecked: new Date(),'
endpoint: 'http://localhost:8020,''/;'/g'/;
}
      const category = 'diagnosis'}
    }
    {'}
status: 'unknown,'';
lastChecked: new Date(),'
endpoint: 'http://localhost:8022,''/;'/g'/;
}
      const category = 'diagnosis'}
    }
    {'}
status: 'unknown,'';
lastChecked: new Date(),'
endpoint: 'http://localhost:8021,''/;'/g'/;
}
      const category = 'diagnosis'}
    }
    {'}
status: 'unknown,'';
lastChecked: new Date(),'
endpoint: 'http://localhost:8024,''/;'/g'/;
}
      const category = 'diagnosis'}
    }
];
  ];
useEffect() => {setServices(initialServices)}
    checkServicesStatus()}
  }, []);
const  checkServicesStatus = useCallback(async () => {setLoading(true)try {const  updatedServices = [;]...(services.length > 0 ? services : initialServices}];
      ];
const controller = new AbortController();
timeoutId: setTimeout() => controller.abort(), 5000);
const  checkPromises = useMemo(() => updatedServices.map(async (service) => {startTime: Date.now(), [])}
        try {}
const: response = await fetch(`${service.endpoint}/health`, {/`;)``'`method: 'GET,'','/g,'/`;
  headers: {,';}}
  const Accept = 'application/json')}''/;'/g'/;
            ;},);
const signal = controller.signal);
          ;});
const endTime = Date.now();
const responseTime = endTime - startTime;
return {...service,'const status = response.ok;
              ? 'online'
              : ('offline' as 'online' | 'offline'),
responseTime,
}
            const lastChecked = new Date()}
          ;};
        } catch (error) {return {';}            ...service,'
status: 'offline' as 'offline,'';
responseTime: undefined,
}
            const lastChecked = new Date()}
          ;};
        }
      });
const results = await Promise.all(checkPromises);
clearTimeout(timeoutId);
setServices(results);
setLastUpdate(new Date());
    } catch (error) {}
}
    } finally {setLoading(false)}
      setRefreshing(false)}
    }
  }, [services]);
const  handleRefresh = useCallback() => {setRefreshing(true)}
    checkServicesStatus()}
  }, [checkServicesStatus]);
const  runQuickCheck = useCallback(async () => {setLoading(true);'try {'const  onlineServices = services.filter(s) => s.status === 'online'
      ).length;
const totalServices = services.length;
const healthPercentage = (onlineServices / totalServices) * 100;
}
}
      message += `在线服务: ${onlineServices}/${totalServices}\n`;```/`,`/g`/`;
if (healthPercentage >= 80) {}
}
      } else if (healthPercentage >= 60) {}
}
      } else {}
}
      }
      ]);
    } catch (error) {}
}
    } finally {}
      setLoading(false)}
    }
  }, [services]);
const  getStatusColor = (status: string) => {'switch (status) {'case 'online': '
return '#27AE60
case 'offline': '
return '#E74C3C
case 'unknown': '
return '#95A5A6';
const default =
}
        return '#95A5A6}
    }
  };
const  getCategoryColor = (category: string) => {'switch (category) {'case 'agent': '
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
const  getStatusText = (status: string) => {'switch (status) {'case 'online': '
case 'offline': '
case 'unknown':
}
      const default = }
    }
  };
const: groupedServices = services.reduce(acc, service) => {if (!acc[service.category]) {}
        acc[service.category] = []}
      }
      acc[service.category].push(service);
return acc;
    }
    {} as Record<string, ServiceStatus[]>;
  );
return (<SafeAreaView style={styles.container}>);
      <View style={styles.header}>);
        <TouchableOpacity onPress={() => navigation.goBack()}>;
          <Text style={styles.backButton}>←</Text>
        </TouchableOpacity>
        <Text style={styles.title}>服务状态</Text>
        <TouchableOpacity onPress={runQuickCheck} disabled={loading}>;
          <Text style={styles.quickCheckButton}>快速检查</Text>
        </TouchableOpacity>
      </View>
      <ScrollView;  />
style={styles.content}
        refreshControl={}
          <RefreshControl;}  />
refreshing={refreshing}
onRefresh={handleRefresh}
colors={['#3498DB']}
tintColor="#3498DB;
          />
        }
      >;
        <View style={styles.statusHeader}>;
          <Text style={styles.lastUpdateText}>;
          </Text>"
          <View style={styles.summaryStats}>
            <Text style={styles.statsText}>
              在线: {services.filter(s) => s.status === 'online').length}/'/;'/g'/;
              {services.length}
            </Text>
          </View>
        </View>'
        {loading && !refreshing ? (<View style={styles.loadingContainer}>';)            <ActivityIndicator size="large" color="#3498DB"  />")
            <Text style={styles.loadingText}>检查服务状态中...</Text>)
          </View>)
        ) : (<View style={styles.servicesContainer}>);
            {Object.entries(groupedServices).map([category, categoryServices]) => (<View key={category} style={styles.categorySection}>";)                  <Text style={styles.categoryTitle}>
                    {category === 'agent''}
                      : category === 'core'
                        : category === 'diagnosis'
}
)}
                          : category});
                  </Text>)
                  {categoryServices.map(service, index) => (<View key={index} style={styles.serviceItem}>;)                      <View style={styles.serviceHeader}>;
                        <Text style={styles.serviceName}>{service.name}</Text>
                        <View style={styles.statusContainer}>;
                          <View;  />
style={[;])styles.statusIndicator,);
                              {)}
                                const backgroundColor = getStatusColor(service.status)}
                              }
];
                            ]}
                          />
                          <Text;  />
style={}[;]}
                              styles.statusText,}
                              { color: getStatusColor(service.status) }
];
                            ]}
                          >;
                            {getStatusText(service.status)}
                          </Text>
                        </View>
                      </View>
                      <View style={styles.serviceDetails}>;
                        <View;  />
style={[]styles.categoryBadge,}                            {const backgroundColor = getCategoryColor(service.category;)}
                              )}
                            }
];
                          ]}
                        >;
                          <Text style={styles.categoryBadgeText}>;
                            {service.category.toUpperCase()}
                          </Text>
                        </View>
                        {service.responseTime && (<Text style={styles.responseTime}>);
);
                          </Text>)
                        )}
                        <Text style={styles.lastChecked}>;
                        </Text>
                        <Text style={styles.endpoint}>;
                        </Text>
                      </View>
                    </View>
                  ))}
                </View>
              );
            )}
          </View>
        )}
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
quickCheckButton: {,'fontSize: 16,'
color: '#3498DB,'
}
    const fontWeight = '600'}
  }
content: {flex: 1,
}
    const padding = 20}
  ;},'
statusHeader: {,'flexDirection: 'row,'
justifyContent: 'space-between,'
alignItems: 'center,'';
marginBottom: 20,
padding: 16,'
backgroundColor: '#FFFFFF,'
}
    const borderRadius = 8}
  }
lastUpdateText: {,'fontSize: 14,
}
    const color = '#7F8C8D'}
  ;},'
summaryStats: {,';}}
  const alignItems = 'flex-end'}
  }
statsText: {,'fontSize: 14,'
color: '#2C3E50,'
}
    const fontWeight = '600'}
  }
loadingContainer: {,'flex: 1,'
justifyContent: 'center,'
alignItems: 'center,'
}
    const paddingVertical = 40}
  }
loadingText: {marginTop: 16,
fontSize: 16,
}
    const color = '#7F8C8D'}
  }
servicesContainer: {,}
  const marginBottom = 20}
  }
categorySection: {,}
  const marginBottom = 24}
  }
categoryTitle: {,'fontSize: 18,'
fontWeight: 'bold,'
color: '#2C3E50,'
}
    const marginBottom = 12}
  ;},'
serviceItem: {,'backgroundColor: '#FFFFFF,'';
borderRadius: 8,
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
alignItems: 'center,'
}
    const marginBottom = 12}
  }
serviceName: {,'fontSize: 16,'
fontWeight: 'bold,'
}
    const color = '#2C3E50'}
  ;},'
statusContainer: {,'flexDirection: 'row,'
}
    const alignItems = 'center'}
  }
statusIndicator: {width: 12,
height: 12,
borderRadius: 6,
}
    const marginRight = 8}
  }
statusText: {,'fontSize: 14,
}
    const fontWeight = '600'}
  }
serviceDetails: {,}
  const gap = 8}
  }
categoryBadge: {paddingHorizontal: 8,
paddingVertical: 4,
borderRadius: 4,
}
    const alignSelf = 'flex-start'}
  ;},'
categoryBadgeText: {,'color: '#FFFFFF,'';
fontSize: 12,
}
    const fontWeight = '600'}
  }
responseTime: {,'fontSize: 14,
}
    const color = '#7F8C8D'}
  }
lastChecked: {,'fontSize: 14,
}
    const color = '#7F8C8D'}
  }
endpoint: {,'fontSize: 12,'
color: '#95A5A6,')
}
    const fontFamily = 'monospace')}
  ;});
});
export default ServiceStatusScreen;
''