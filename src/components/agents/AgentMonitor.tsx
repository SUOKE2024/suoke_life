import { agentService } from "../../services/agentService"
import { agentCoordinationService, AgentInfo } from "../../services/agentCoordinationService"
import React, { useState, useEffect, useCallback } from "react";
View,
Text,
StyleSheet,
ScrollView,
RefreshControl,
TouchableOpacity,"
Alert,","
Dimensions;
} from "react-native;
getAgentStatus,"
getAgentMetrics,","
AgentSystemUtils;
} from "../../agents"/;"/g"/;
/* 性 */
*/
interface AgentMonitorProps {
refreshInterval?: numberonAgentError?: (agentType: AgentType; error: string) => void;
}
  style?: any}
}
/* 性 */
*/
interface StatusCardProps {agentType: AgentType}const status = AgentHealthStatus;
metrics?: AgentMetrics;
}
}
  onRestart?: () => void}
}
/* 件 */
*/
const  StatusCard: React.FC<StatusCardProps> = ({)agentType}status,);
metrics,);
}
  onRestart;)}
}) => {"const agentRole = AgentSystemUtils.getAgentRole(agentType);","
const getStatusColor = (status: string) => {switch (status) {case "healthy": return "#4CAF50case "degraded": ","
return "#FF9800,"
case "unhealthy": ","
return "#F44336,"
case "offline": ","
return "#9E9E9E,"
const default = ";
}
        return "#9E9E9E};
    }
  };
case "degraded": ,"
case "unhealthy": ,"
case "offline": ;
const default = }
  };
return (<View style={styles.statusCard}>;)      <View style={styles.cardHeader}>;
        <View>;
          <Text style={styles.agentName}>{agentRole.name}</Text>
          <Text style={styles.agentTitle}>{agentRole.title}</Text>
        </View>
        <View;)  />
style={[;])}
            styles.statusIndicator,)}
            { backgroundColor: getStatusColor(status.status) }
];
          ]}
        >;
          <Text style={styles.statusText}>{getStatusText(status.status)}</Text>
        </View>
      </View>
      <View style={styles.metricsContainer}>;
        <View style={styles.metricRow}>;
          <Text style={styles.metricLabel}>负载: </Text>
          <Text style={styles.metricValue}>;
            {(status.load * 100).toFixed(1)}%;
          </Text>
        </View>
        <View style={styles.metricRow}>;
          <Text style={styles.metricLabel}>响应时间: </Text>
          <Text style={styles.metricValue}>{status.responseTime}ms</Text>
        </View>
        <View style={styles.metricRow}>;
          <Text style={styles.metricLabel}>错误率: </Text>
          <Text style={styles.metricValue}>;
            {(status.errorRate * 100).toFixed(1)}%;
          </Text>
        </View>
        {metrics  && <>}
            <View style={styles.metricRow}>;
              <Text style={styles.metricLabel}>处理任务: </Text>
              <Text style={styles.metricValue}>{metrics.tasksProcessed}</Text>
            </View>
            <View style={styles.metricRow}>;
              <Text style={styles.metricLabel}>成功率: </Text>
              <Text style={styles.metricValue}>;
                {(metrics.successRate * 100).toFixed(1)}%;
              </Text>
            </View>
            <View style={styles.metricRow}>;
              <Text style={styles.metricLabel}>运行时间: </Text>
              <Text style={styles.metricValue}>;
                {Math.floor(metrics.uptime / 60)}分钟
              </Text>
            </View>
          < />
        )}
      </View>
      <View style={styles.capabilitiesContainer}>;
        <Text style={styles.capabilitiesTitle}>能力: </Text>
        <View style={styles.capabilitiesList}>;
          {status.capabilities.slice(0, 3).map(capability, index) => ())}
            <Text key={index} style={styles.capabilityTag}>;
              {capability}
            </Text>
          ))}
          {status.capabilities.length > 3  && <Text style={styles.capabilityTag}>;
              +{status.capabilities.length - 3};
            </Text>;
          )};
        </View>;"/;"/g"/;
      </View>;"/;"/g"/;
      {status.status === "unhealthy" && onRestart && (;)"};
        <TouchableOpacity style={styles.restartButton} onPress={onRestart}>;
          <Text style={styles.restartButtonText}>重启</Text>;
        </TouchableOpacity>;
      )};
      <Text style={styles.lastCheck}>;
      </Text>;
    </View>;
  );
};
interface AgentMonitorState {agents: AgentInfo[]}metrics: Map<string, AgentMetrics>;
collaborationStats: {total: number,
active: number,
completed: number,
failed: number,
}
}
  const averageDuration = number}
};
isLoading: boolean,
const lastUpdate = Date;
}
export const AgentMonitor: React.FC<AgentMonitorProps> = ({)refreshInterval = 30000,)onAgentError,);
}
  style;)}
}) => {}
  const [state, setState] = useState<AgentMonitorState>({agents: [],metrics: new Map(),collaborationStats: {total: 0,active: 0,completed: 0,failed: 0,averageDuration: 0;)}
    },isLoading: true,lastUpdate: new Date();
  });
const [refreshing, setRefreshing] = useState(false);
  /* 据 */
  *//,/g,/;
  loadAgentData: useCallback(async () => {try {setState(prev => ({  ...prev, isLoading: true ; })););
      // 获取智能体列表
const agents = agentCoordinationService.getAgents();
      // 获取协作统计
const collaborationStats = agentCoordinationService.getCollaborationStats();
      // 获取每个智能体的性能指标/,/g,/;
  metricsMap: new Map<string, AgentMetrics>();
for (const agent of agents) {try {const metrics = await agentService.getAgentMetrics(agent.id);
metricsMap.set(agent.id, {)            responseTime: metrics.responseTime}successRate: metrics.successRate,);
activeConnections: metrics.activeConnections,);
load: agent.load;),
}
            const uptime = Date.now() - agent.lastHeartbeat.getTime()}
          });
        } catch (error) {// 如果获取指标失败，使用默认值/metricsMap.set(agent.id, {)            responseTime: 0}successRate: 0,,/g,/;
  activeConnections: 0,);
load: agent.load,);
}
            const uptime = 0;)}
          });
        }
      }
      setState(prev => ({)...prev}agents,
const metrics = metricsMap;);
collaborationStats,);
isLoading: false,);
}
        const lastUpdate = new Date()}
      }));
    } catch (error: any) {}
}
      setState(prev => ({  ...prev, isLoading: false ; }));
    }
  }, []);
  /* 据 */
  */
const onRefresh = useCallback(async () => {setRefreshing(true);)const await = loadAgentData();
}
    setRefreshing(false)}
  }, [loadAgentData]);
  /* " *//;"/g"/;
  */"
const getStatusColor = (status: string): string => {switch (status) {case 'active': return '#4CAF50case 'busy': '
return '#FF9800
case 'inactive': '
return '#9E9E9E
case 'error': '
return '#F44336';
const default =
}
        return '#9E9E9E}
    }
  };
  /* ' *//;'/g'/;
  *//,'/g'/;
const getHealthColor = (load: number): string => {if (load < 0.3) return '#4CAF50'; // 绿色 - 健康'/if (load < 0.7) return '#FF9800'; // 橙色 - 警告'/;'/g'/;
}
    return '#F44336'; // 红色 - 危险'}''/;'/g'/;
  };
  /* 间 */
  */
const formatDuration = (ms: number): string => {const seconds = Math.floor(ms / 1000);/const minutes = Math.floor(seconds / 60);
const hours = Math.floor(minutes / 60);
}
    if (hours > 0) {}
      return `${hours}h ${minutes % 60}m`;````;```;
    } else if (minutes > 0) {}
      return `${minutes}m ${seconds % 60}s`;````;```;
    } else {}
      return `${seconds}s`;````;```;
    }
  };
  /* 比 */
  */
const formatPercentage = (value: number): string => {return `${(value * 100).toFixed(1}%`;````;```;
  };
  /* 片 */
  */
const renderAgentCard = (agent: AgentInfo) => {const metrics = state.metrics.get(agent.id)}
    return (<View key={agent.id} style={styles.agentCard}>;)        <View style={styles.agentHeader}>;
          <View style={styles.agentInfo}>;
            <Text style={styles.agentName}>{agent.name}</Text>;)
            <Text style={styles.agentType}>{agent.type}</Text>;)
          </View>;)
          <View style={[styles.statusIndicator, { backgroundColor: getStatusColor(agent.status) ;}}]}  />;
        </View>;
        <View style={styles.metricsContainer}>;
          <View style={styles.metricRow}>;
            <Text style={styles.metricLabel}>负载: </Text>;
            <View style={styles.loadBar}>;
              <View ;  />
style={[;]}
                  styles.loadFill,{width: `${agent.load * 100;}}%`,backgroundColor: getHealthColor(agent.load);````;```;
                  }
];
                ]}
              />
            </View>
            <Text style={styles.metricValue}>{formatPercentage(agent.load)}</Text>
          </View>
          {metrics  && <>}
              <View style={styles.metricRow}>;
                <Text style={styles.metricLabel}>响应时间: </Text>
                <Text style={styles.metricValue}>{metrics.responseTime}ms</Text>
              </View>
              <View style={styles.metricRow}>;
                <Text style={styles.metricLabel}>成功率: </Text>
                <Text style={styles.metricValue}>{formatPercentage(metrics.successRate)}</Text>
              </View>
              <View style={styles.metricRow}>;
                <Text style={styles.metricLabel}>活跃连接: </Text>
                <Text style={styles.metricValue}>{metrics.activeConnections}</Text>
              </View>
              <View style={styles.metricRow}>;
                <Text style={styles.metricLabel}>运行时间: </Text>
                <Text style={styles.metricValue}>{formatDuration(metrics.uptime)}</Text>
              </View>
            < />
          )}
        </View>
        <View style={styles.capabilitiesContainer}>;
          <Text style={styles.capabilitiesTitle}>能力: </Text>
          <View style={styles.capabilitiesList}>;
            {agent.capabilities.slice(0, 3).map(capability, index) => ())}
              <View key={index} style={styles.capabilityTag}>;
                <Text style={styles.capabilityText}>{capability}</Text>
              </View>
            ))}
            {agent.capabilities.length > 3  && <Text style={styles.moreCapabilities}>+{agent.capabilities.length - 3}</Text>
            )}
          </View>
        </View>
      </View>;
    );
  };
  /* 计 */
  */
const renderCollaborationStats = () => {const { collaborationStats } = state;
return (<View style={styles.statsContainer}>;)        <Text style={styles.statsTitle}>协作统计</Text>
        <View style={styles.statsGrid}>;
          <View style={styles.statItem}>;
            <Text style={styles.statValue}>{collaborationStats.total}</Text>
            <Text style={styles.statLabel}>总计</Text>'
          </View>'/;'/g'/;
          <View style={styles.statItem}>'
            <Text style={[styles.statValue, { color: '#4CAF50' ;}}]}>{collaborationStats.active}</Text>'/;'/g'/;
            <Text style={styles.statLabel}>活跃</Text>;
          </View>;'/;'/g'/;
          <View style={styles.statItem}>;
            <Text style={[styles.statValue, { color: '#2196F3' ;}}]}>{collaborationStats.completed}</Text>;'/;'/g'/;
            <Text style={styles.statLabel}>完成</Text>;
          </View>;'/;'/g'/;
          <View style={styles.statItem}>;
            <Text style={[styles.statValue, { color: '#F44336' ;}}]}>{collaborationStats.failed}</Text>;'/;'/g'/;
            <Text style={styles.statLabel}>失败</Text>;
          </View>;
        </View>;)
        <View style={styles.averageDuration}>;);
          <Text style={styles.statLabel}>平均协作时长: </Text>;)
          <Text style={styles.statValue}>{formatDuration(collaborationStats.averageDuration)}</Text>;
        </View>;
      </View>;
    );
  };
  // 组件挂载时加载数据
useEffect() => {loadAgentData(}    // 设置定时刷新/,/g,/;
  interval: setInterval(loadAgentData, 30000); // 30秒刷新一次
}
    return () => clearInterval(interval)}
  }, [loadAgentData]);
return (<ScrollView;  />/,)style={[styles.container, style]}/g/;
      refreshControl={}
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh}  />
      }
    >;
      <View style={styles.header}>;
        <Text style={styles.title}>智能体监控</Text>;
        <Text style={styles.lastUpdate}>;
);
        </Text>;)
      </View>;)
      {renderCollaborationStats()};
      <View style={styles.agentsContainer}>;
        <Text style={styles.sectionTitle}>智能体状态</Text>;
        {state.isLoading ? (;)}
          <Text style={styles.loadingText}>加载中...</Text>;
        ) : (;);
state.agents.map(renderAgentCard);
        )}
      </View>
    </ScrollView>;
  );
};
const { width } = Dimensions.get("window");","
const  styles = StyleSheet.create({)container: {,"flex: 1,";
}
    const backgroundColor = "#f5f5f5"};
  }
header: {,"padding: 16,","
backgroundColor: '#fff,'';
borderBottomWidth: 1,
}
    const borderBottomColor = '#e0e0e0'}
  }
title: {,'fontSize: 24,'
fontWeight: "bold,
}
    const color = "#333"};
  }
lastUpdate: {,"fontSize: 12,","
color: "#666,
}
    const marginTop = 4}
  }
statsContainer: {margin: 16,","
padding: 16,","
backgroundColor: "#fff,";
borderRadius: 8,
}
    const elevation = 2}
  }
statsTitle: {,"fontSize: 18,","
fontWeight: "bold,
marginBottom: 12,";
}
    const color = "#333"};
  ;},","
statsGrid: {,"flexDirection: "row,
justifyContent: "space-around,
}
    const marginBottom = 12}
  },","
statItem: {,";}}
  const alignItems = "center"};
  }
statValue: {,"fontSize: 20,","
fontWeight: "bold,
}
    const color = "#333"};
  }
statLabel: {,"fontSize: 12,","
color: "#666,
}
    const marginTop = 4}
  },","
averageDuration: {,"flexDirection: "row,
justifyContent: "center,
alignItems: "center,
paddingTop: 12,","
borderTopWidth: 1,";
}
    const borderTopColor = "#e0e0e0"};
  }
agentsContainer: {,}
  const margin = 16}
  }
sectionTitle: {,"fontSize: 18,","
fontWeight: "bold,
marginBottom: 12,";
}
    const color = "#333"};
  ;},","
agentCard: {,"backgroundColor: "#fff,";
borderRadius: 8,
padding: 16,
marginBottom: 12,
}
    const elevation = 2}
  },","
agentHeader: {,"flexDirection: "row,
justifyContent: "space-between,
alignItems: "center,
}
    const marginBottom = 12}
  }
agentInfo: {,}
  const flex = 1}
  }
agentName: {,"fontSize: 16,","
fontWeight: "bold,
}
    const color = "#333"};
  }
agentType: {,"fontSize: 12,","
color: "#666,
}
    const marginTop = 2}
  }
statusIndicator: {width: 12,
height: 12,
}
    const borderRadius = 6}
  }
metricsContainer: {,}
  const marginBottom = 12}
  },","
metricRow: {,"flexDirection: "row,
justifyContent: "space-between,
alignItems: "center,
}
    const marginBottom = 8}
  }
metricLabel: {,"fontSize: 14,","
color: "#666,
}
    const flex = 1}
  }
metricValue: {,"fontSize: 14,","
fontWeight: "500,
}
    const color = "#333"};
  }
loadBar: {flex: 2,","
height: 8,","
backgroundColor: "#e0e0e0,
borderRadius: 4,","
marginHorizontal: 8,";
}
    const overflow = "hidden"};
  ;},","
loadFill: {,"height: "100%,
}
    const borderRadius = 4}
  }
capabilitiesContainer: {,"borderTopWidth: 1,","
borderTopColor: "#e0e0e0,
}
    const paddingTop = 12}
  }
capabilitiesTitle: {,"fontSize: 14,","
fontWeight: "500,
color: "#333,
}
    const marginBottom = 8}
  },","
capabilitiesList: {,"flexDirection: "row,
flexWrap: "wrap,
}
    const alignItems = "center"};
  ;},","
capabilityTag: {,"backgroundColor: "#e3f2fd,";
paddingHorizontal: 8,
paddingVertical: 4,
borderRadius: 12,"
marginRight: 8,";
}
    const marginBottom = 4;"};
  },capabilityText: {fontSize: 12,color: "#1976d2"
  },moreCapabilities: {fontSize: 12,color: "#666",fontStyle: "italic"
  },loadingText: {,"textAlign: "center,")";
}
      color: "#666",fontSize: 16,marginTop: 20;")
  };);});
export default AgentMonitor;""