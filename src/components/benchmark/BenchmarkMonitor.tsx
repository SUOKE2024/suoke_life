import React, { useEffect, useState } from "react"
import { Card, Button, ProgressBar, Chip, Badge  } from "react-native-paper"
import {  useSelector, useDispatch  } from "react-redux"
import { useBenchmarkStreaming } from "../../hooks"
import type { AppDispatch } from "../../store"
View,
Text,
StyleSheet,"
ScrollView,
RefreshControl;
} from "react-native;
selectTaskStats,
selectStreamingStatus,
selectHealthStatus,
fetchHealthStatus,
updateStreamingStatus;
} from "../../store/slices/benchmarkSlice"
interface BenchmarkMonitorProps {
}
  onTaskSelect?: (taskId: string) => void}
}
export const BenchmarkMonitor: React.FC<BenchmarkMonitorProps> = ({))};
  onTaskSelect;)}
}) => {const dispatch = useDispatch<AppDispatch>()const taskStats = useSelector(selectTaskStats);
const streamingStatus = useSelector(selectStreamingStatus);
const healthStatus = useSelector(selectHealthStatus);
const [refreshing, setRefreshing] = useState(false);
const {isConnected}connectionState,
events,
error,
connect,
disconnect,
clearEvents,
getEventsByType,
getLatestEvent,
};
eventCount}
  } = useBenchmarkStreaming({autoConnect: true,maxEvents: 50;)}
  });
  // 同步流式状态到Redux;
useEffect() => {dispatch(updateStreamingStatus({)isConnected,);
connectionState,);
}
      const lastEvent = getLatestEvent()}
    }));
  }, [isConnected, connectionState, events, dispatch, getLatestEvent]);
  // 刷新数据
const handleRefresh = async () => {setRefreshing(true)try {}
      const await = dispatch(fetchHealthStatus()).unwrap()}
    } catch (error) {}
}
    } finally {}
      setRefreshing(false)}
    }
  };
  // 连接状态指示器'/,'/g'/;
const getConnectionStatusColor = useCallback(() => {switch (connectionState) {case 'OPEN': return '#4CAF50case 'CONNECTING': return '#FF9800
case 'CLOSED': return '#F44336';
}
      const default = return '#9E9E9E}
    }
  };
  // 获取系统状态'/,'/g'/;
const getSystemStatus = useCallback(() => {if (!healthStatus) return 'unknown}'';
const { cpu_usage, memory_usage, disk_usage } = healthStatus.system_info;
if (cpu_usage > 90 || memory_usage > 90 || disk_usage > 90) {';}}
      return 'critical}
    } else if (cpu_usage > 70 || memory_usage > 70 || disk_usage > 70) {';}}
      return 'warning}
    }
return 'healthy';
  };
  // 获取状态颜色'/,'/g'/;
const getStatusColor = useCallback((status: string) => {switch (status) {case 'healthy': return '#4CAF50case 'warning': return '#FF9800
case 'critical': return '#F44336';
}
      const default = return '#9E9E9E}
    }
  };
  // 处理连接操作
const handleConnectionToggle = useCallback(() => {if (isConnected) {disconnect()}
    } else {}
      connect()}
    }
  };
  // 获取最近的错误事件'/,'/g'/;
const errorEvents = getEventsByType('benchmark_error');
const progressEvents = getEventsByType('benchmark_progress');
const completeEvents = getEventsByType('benchmark_complete');
return (<ScrollView;  />/,)style={styles.container}/g/;
      refreshControl={}
        <RefreshControl refreshing={refreshing} onRefresh={handleRefresh}  />
      }
    >;
      {// 连接状态卡片}'/;'/g'/;
      <Card style={styles.card}>'
        <Card.Title title="实时连接状态"  />"/;"/g"/;
        <Card.Content>;
          <View style={styles.statusRow}>);
            <View style={styles.statusItem}>);
              <Badge;)  />
style={[styles.statusBadge, { backgroundColor: getConnectionStatusColor() ;}}]}
              />
              <Text style={styles.statusText}>;
              </Text>"
            </View>"/;"/g"/;
            <Button;"  />"
mode={isConnected ? 'outlined' : 'contained'}
onPress={handleConnectionToggle}
              compact;
            >;
            </Button>
          </View>
          {error  && <Text style={styles.errorText}>连接错误: {error}</Text>
          )}
          <View style={styles.metricsRow}>'
            <Text style={styles.metricText}>事件数量: {eventCount}</Text>'/;'/g'/;
            <Button mode="text" onPress={clearEvents} compact>";
            </Button>
          </View>
        </Card.Content>
      </Card>"
      {// 任务统计卡片}"/;"/g"/;
      <Card style={styles.card}>
        <Card.Title title="任务统计"  />"/;"/g"/;
        <Card.Content>;
          <View style={styles.statsGrid}>;
            <View style={styles.statItem}>;
              <Text style={styles.statNumber}>{taskStats.total}</Text>
              <Text style={styles.statLabel}>总计</Text>"
            </View>"/;"/g"/;
            <View style={styles.statItem}>
              <Text style={[styles.statNumber, { color: '#FF9800' ;}}]}>
                {taskStats.running}
              </Text>
              <Text style={styles.statLabel}>运行中</Text>'
            </View>'/;'/g'/;
            <View style={styles.statItem}>'
              <Text style={[styles.statNumber, { color: '#4CAF50' ;}}]}>
                {taskStats.completed}
              </Text>
              <Text style={styles.statLabel}>已完成</Text>'
            </View>'/;'/g'/;
            <View style={styles.statItem}>'
              <Text style={[styles.statNumber, { color: '#F44336' ;}}]}>
                {taskStats.failed}
              </Text>
              <Text style={styles.statLabel}>失败</Text>
            </View>
          </View>
        </Card.Content>
      </Card>
      {// 系统健康状态}
      {healthStatus  && <Card style={styles.card}>;
          <Card.Title;  />
right={() => ()}
              <Chip;}'  />/,'/g'/;
style={[styles.statusChip, { backgroundColor: getStatusColor(getSystemStatus()) ;}}]}
textStyle={ color: 'white' }
              >;
              </Chip>
            )}
          />
          <Card.Content>;
            <View style={styles.metricsContainer}>;
              <View style={styles.metricItem}>;
                <Text style={styles.metricLabel}>CPU使用率</Text>'
                <ProgressBar;'  />/,'/g'/;
progress={healthStatus.system_info.cpu_usage / 100}'/,'/g'/;
color={healthStatus.system_info.cpu_usage > 80 ? '#F44336' : '#4CAF50'}
style={styles.progressBar}>;
                <Text style={styles.metricValue}>;
                  {healthStatus.system_info.cpu_usage.toFixed(1)}%;
                </Text>
              </View>
              <View style={styles.metricItem}>;
                <Text style={styles.metricLabel}>内存使用率</Text>'
                <ProgressBar;'  />/,'/g'/;
progress={healthStatus.system_info.memory_usage / 100}'/,'/g'/;
color={healthStatus.system_info.memory_usage > 80 ? '#F44336' : '#4CAF50'}
style={styles.progressBar}>;
                <Text style={styles.metricValue}>;
                  {healthStatus.system_info.memory_usage.toFixed(1)}%;
                </Text>
              </View>
              <View style={styles.metricItem}>;
                <Text style={styles.metricLabel}>磁盘使用率</Text>'
                <ProgressBar;'  />/,'/g'/;
progress={healthStatus.system_info.disk_usage / 100}'/,'/g'/;
color={healthStatus.system_info.disk_usage > 80 ? '#F44336' : '#4CAF50'}
style={styles.progressBar}>;
                <Text style={styles.metricValue}>;
                  {healthStatus.system_info.disk_usage.toFixed(1)}%;
                </Text>
              </View>
            </View>
            <View style={styles.serviceStatus}>;
              <Text style={styles.serviceLabel}>服务状态: </Text>'
              <Chip;'  />/,'/g'/;
style={[]styles.serviceChip, {';}}
                  backgroundColor: healthStatus.status === 'healthy' ? '#4CAF50' : '#F44336'}
];
                ;}}]}
textStyle={ color: 'white' }
              >;
              </Chip>
            </View>
          </Card.Content>
        </Card>
      )}
      {// 最近事件}'/;'/g'/;
      <Card style={styles.card}>'
        <Card.Title title="最近事件"  />"/;"/g"/;
        <Card.Content>;
          {events.length === 0 ? ()}
            <Text style={styles.noEventsText}>暂无事件</Text>
          ) : (<View style={styles.eventsContainer}>);
              {events.slice(0, 5).map(event, index) => ())}
                <View key={index} style={styles.eventItem}>;
                  <View style={styles.eventHeader}>;
                    <Chip;  />"
style={[]styles.eventTypeChip, {"const backgroundColor = ","
event.type === 'benchmark_error' ? '#F44336' : '
event.type === 'benchmark_complete' ? '#4CAF50' :
}
                          event.type === 'benchmark_progress' ? '#FF9800' : '#2196F3'}
];
                      ;}}]}
textStyle={';}}
      color: "white,"}";
const fontSize = 10 }
                    >;
                      {event.type}
                    </Chip>
                    <Text style={styles.eventTime}>;
                      {new Date(event.timestamp).toLocaleTimeString()}
                    </Text>
                  </View>
                  <Text style={styles.eventData} numberOfLines={2}>;
                    {JSON.stringify(event.data, null, 2)}
                  </Text>
                </View>
              ))}
            </View>
          )}
        </Card.Content>
      </Card>"
      {// 事件统计}"/;"/g"/;
      <Card style={styles.card}>
        <Card.Title title="事件统计"  />"/;"/g"/;
        <Card.Content>;
          <View style={styles.eventStatsGrid}>
            <View style={styles.eventStatItem}>
              <Text style={[styles.eventStatNumber, { color: '#F44336' ;}}]}>
                {errorEvents.length}
              </Text>
              <Text style={styles.eventStatLabel}>错误</Text>'
            </View>'/;'/g'/;
            <View style={styles.eventStatItem}>;
              <Text style={[styles.eventStatNumber, { color: '#FF9800' ;}}]}>;
                {progressEvents.length};
              </Text>;
              <Text style={styles.eventStatLabel}>进度</Text>;
            </View>;'/;'/g'/;
            <View style={styles.eventStatItem}>;
              <Text style={[styles.eventStatNumber, { color: '#4CAF50' ;}}]}>;
                {completeEvents.length};
              </Text>;
              <Text style={styles.eventStatLabel}>完成</Text>;
            </View>;
          </View>;
        </Card.Content>;
      </Card>;
    </ScrollView>;
  );
};
const  styles = StyleSheet.create({)container: {,'flex: 1,
}
    const backgroundColor = '#f5f5f5'}
  }
card: {margin: 16,
}
    const marginBottom = 8}
  },'
statusRow: {,'flexDirection: 'row,'
justifyContent: 'space-between,'
alignItems: 'center,'
}
    const marginBottom = 8}
  },'
statusItem: {,'flexDirection: 'row,'
}
    const alignItems = 'center'}
  }
statusBadge: {width: 12,
height: 12,
borderRadius: 6,
}
    const marginRight = 8}
  }
statusText: {,'fontSize: 16,
}
    const fontWeight = '500'}
  ;},'
errorText: {,'color: '#F44336,'';
fontSize: 12,
}
    const marginTop = 4}
  },'
metricsRow: {,'flexDirection: 'row,'
justifyContent: 'space-between,'
alignItems: 'center,'
}
    const marginTop = 8}
  }
metricText: {,'fontSize: 14,
}
    const color = '#666'}
  ;},'
statsGrid: {,'flexDirection: 'row,'
}
    const justifyContent = 'space-around'}
  ;},'
statItem: {,';}}
  const alignItems = 'center'}
  }
statNumber: {,'fontSize: 24,'
fontWeight: 'bold,'
}
    const color = '#333'}
  }
statLabel: {,'fontSize: 12,'
color: '#666,'
}
    const marginTop = 4}
  }
statusChip: {,}
  const marginRight = 16}
  }
metricsContainer: {,}
  const marginTop = 8}
  }
metricItem: {,}
  const marginBottom = 16}
  }
metricLabel: {,'fontSize: 14,'
color: '#666,'
}
    const marginBottom = 4}
  }
progressBar: {height: 8,
borderRadius: 4,
}
    const marginBottom = 4}
  }
metricValue: {,'fontSize: 12,'
color: '#333,'
}
    const textAlign = 'right'}
  ;},'
serviceStatus: {,'flexDirection: 'row,'
alignItems: 'center,'
}
    const marginTop = 8}
  }
serviceLabel: {,'fontSize: 14,'
color: '#666,'
}
    const marginRight = 8}
  }
serviceChip: {,}
  const height = 24}
  },'
noEventsText: {,'textAlign: 'center,'
color: '#666,'
fontStyle: 'italic,'
}
    const padding = 16}
  }
eventsContainer: {,}
  const marginTop = 8}
  },'
eventItem: {,'backgroundColor: '#f9f9f9,'';
padding: 12,
borderRadius: 8,
}
    const marginBottom = 8}
  },'
eventHeader: {,'flexDirection: 'row,'
justifyContent: 'space-between,'
alignItems: 'center,'
}
    const marginBottom = 4}
  }
eventTypeChip: {,}
  const height = 20}
  }
eventTime: {,'fontSize: 10,
}
    const color = '#666'}
  }
eventData: {,'fontSize: 10,'
color: '#333,'
}
    const fontFamily = 'monospace'}
  ;},'
eventStatsGrid: {,'flexDirection: "row,
}
      const justifyContent = 'space-around}
  },eventStatItem: {alignItems: 'center}
  },eventStatNumber: {fontSize: 20,fontWeight: 'bold)}
  },eventStatLabel: {fontSize: 12,color: '#666',marginTop: 4;')}
  };)
});