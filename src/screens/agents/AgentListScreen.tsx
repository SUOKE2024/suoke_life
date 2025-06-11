import { useNavigation } from "@react-navigation/native"
import React, { useCallback, useState } from "react";
import {Alert} fromimensions,
RefreshControl,
ScrollView,
StyleSheet,
Switch,
Text,"
TouchableOpacity,";
}
    View,'}
} from "react-native;
import Icon from "react-native-vector-icons/MaterialIcons"
const { width: screenWidth ;} = Dimensions.get('window');
interface Agent {id: string}name: string,
displayName: string,
description: string,
avatar: string,'
status: 'online' | 'offline' | 'busy,'';
capabilities: string[],
lastActive: string,
responseTime: number,
accuracy: number,
color: string,
}
}
  const isEnabled = boolean}
}
/* 理 */
 */
const  AgentListScreen: React.FC = () => {const navigation = useNavigation()const [refreshing, setRefreshing] = useState(false);
  // 智能体数据'
const [agents, setAgents] = useState<Agent[]>([;)';]    {'id: 'xiaoai,'
avatar: '🤖,'
status: 'online,'';
responseTime: 1.2,
accuracy: 94.5,'
color: '#4CAF50,'
}
      const isEnabled = true}
    },'
    {'id: 'xiaoke,'
avatar: '🏥,'
status: 'online,'';
responseTime: 2.1,
accuracy: 91.8,'
color: '#2196F3,'
}
      const isEnabled = true}
    },'
    {'id: 'laoke,'
avatar: '👨‍⚕️,'
status: 'busy,'';
responseTime: 3.5,
accuracy: 96.2,'
color: '#FF9800,'
}
      const isEnabled = true}
    },'
    {'id: 'soer,'
avatar: '📊,'
status: 'offline,'';
responseTime: 1.8,
accuracy: 89.3,'
color: '#9C27B0,)'
}
      const isEnabled = false;)}
    },);
];
  ]);
const  onRefresh = useCallback(async () => {setRefreshing(true}    // 模拟数据刷新/,/g,/;
  await: new Promise(resolve => setTimeout(resolve, 1000));
}
    setRefreshing(false)}
  }, []);
const  toggleAgent = (agentId: string) => {}setAgents(prevAgents =>,)prevAgents.map(agent =>;)}
        agent.id === agentId)}
          ? { ...agent, isEnabled: !agent.isEnabled ;});
          : agent);
      );
    );
  };
const  startChat = (agent: Agent) => {if (!agent.isEnabled) {}
      return}
    }
navigation.navigate('AgentChat' as never, {)')''agentId: agent.id; ,);'';
}
      const agentName = agent.name )}
    ;} as never);
  };
const  getStatusColor = (status: string) => {'switch (status) {'case 'online': return '#4CAF50
case 'busy': return '#FF9800
case 'offline': return '#9E9E9E';
}
      const default = return '#9E9E9E}
    }
  };
const  getStatusText = (status: string) => {switch (status) {}
}
    }
  };
const: renderAgentCard = (agent: Agent) => (<TouchableOpacity,  />/,)key={agent.id;}/g/;
      style={}[;]}
        styles.agentCard,}
        { borderLeftColor: agent.color ;},);
        !agent.isEnabled && styles.disabledCard);
];
      ]});
onPress={() => startChat(agent)}
      activeOpacity={0.7}
    >;
      <View style={styles.cardHeader}>;
        <View style={styles.agentInfo}>;
          <Text style={styles.agentAvatar}>{agent.avatar}</Text>
          <View style={styles.agentDetails}>;
            <Text style={styles.agentName}>{agent.displayName}</Text>
            <Text style={styles.agentDescription}>{agent.description}</Text>
          </View>
        </View>
        <View style={styles.statusContainer}>;
          <View style={[styles.statusDot, { backgroundColor: getStatusColor(agent.status) ;}]}  />
          <Text style={[styles.statusText, { color: getStatusColor(agent.status) ;}]}>;
            {getStatusText(agent.status)}
          </Text>
        </View>
      </View>
      <View style={styles.metricsRow}>;
        <View style={styles.metric}>;
          <Text style={styles.metricLabel}>响应</Text>
          <Text style={styles.metricValue}>{agent.responseTime}s</Text>
        </View>
        <View style={styles.metric}>;
          <Text style={styles.metricLabel}>准确率</Text>
          <Text style={styles.metricValue}>{agent.accuracy}%</Text>
        </View>
        <View style={styles.metric}>;
          <Text style={styles.metricLabel}>最后活跃</Text>
          <Text style={styles.metricValue}>{agent.lastActive}</Text>
        </View>
      </View>
      <View style={styles.capabilitiesContainer}>;
        <Text style={styles.capabilitiesTitle}>核心能力: </Text>
        <View style={styles.capabilitiesList}>;
          {agent.capabilities.slice(0, 3).map((capability, index) => (<View key={index} style={styles.capabilityTag}>);
              <Text style={styles.capabilityText}>{capability}</Text>)
            </View>)
          ))}
        </View>
      </View>
      <View style={styles.cardActions}>;
        <TouchableOpacity,  />
style={styles.chatButton}
          onPress={() => startChat(agent)}
        >'
          <Icon name="chat" size={16} color="white"  />"/;"/g"/;
          <Text style={styles.chatButtonText}>开始对话</Text>
        </TouchableOpacity>
        <View style={styles.switchContainer}>;
          <Text style={styles.switchLabel}>启用</Text>
          <Switch,  />"
value={agent.isEnabled}","
onValueChange={() => toggleAgent(agent.id)}","
trackColor={{ false: '#767577', true: '#81b0ff' }
thumbColor={agent.isEnabled ? agent.color : '#f4f3f4'}
          />
        </View>
      </View>
    </TouchableOpacity>
  );
const onlineAgents = agents.filter(agent => agent.status === 'online' && agent.isEnabled);
const enabledAgents = agents.filter(agent => agent.isEnabled);
return (<View style={styles.container}>);
      <View style={styles.header}>)
        <TouchableOpacity onPress={() => navigation.goBack()}>'
          <Icon name="arrow-back" size={24} color="#333"  />"/;"/g"/;
        </TouchableOpacity>"
        <Text style={styles.headerTitle}>智能体助手</Text>"/;"/g"/;
        <TouchableOpacity onPress={onRefresh}>
          <Icon name="refresh" size={24} color="#333"  />"/;"/g"/;
        </TouchableOpacity>
      </View>
      <ScrollView,  />
style={styles.scrollView}
        refreshControl={}
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh}  />
        }
        showsVerticalScrollIndicator={false}
      >;
        {/* 状态概览 */}
        <View style={styles.overview}>
          <View style={styles.overviewCard}>
            <Icon name="smart-toy" size={24} color="#4CAF50"  />"/;"/g"/;
            <Text style={styles.overviewNumber}>{onlineAgents.length}</Text>
            <Text style={styles.overviewLabel}>在线助手</Text>"
          </View>"/;"/g"/;
          <View style={styles.overviewCard}>
            <Icon name="check-circle" size={24} color="#2196F3"  />"/;"/g"/;
            <Text style={styles.overviewNumber}>{enabledAgents.length}</Text>
            <Text style={styles.overviewLabel}>已启用</Text>"
          </View>"/;"/g"/;
          <View style={styles.overviewCard}>
            <Icon name="psychology" size={24} color="#FF9800"  />"/;"/g"/;
            <Text style={styles.overviewNumber}>{agents.length}</Text>
            <Text style={styles.overviewLabel}>总数</Text>
          </View>
        </View>
        {/* 智能体列表 */}
        <View style={styles.agentsList}>;
          <Text style={styles.sectionTitle}>智能体助手</Text>
          {agents.map(renderAgentCard)}
        </View>
        {/* 使用提示 */}
        <View style={styles.tipsSection}>;
          <Text style={styles.tipsTitle}>使用提示</Text>"/;"/g"/;
          <View style={styles.tipItem}>
            <Icon name="info" size={16} color="#2196F3"  />"/;"/g"/;
            <Text style={styles.tipText}>点击智能体卡片可直接开始对话</Text>"
          </View>"/;"/g"/;
          <View style={styles.tipItem}>
            <Icon name="toggle-on" size={16} color="#4CAF50"  />"/;"/g"/;
            <Text style={styles.tipText}>使用开关可启用或禁用智能体</Text>"
          </View>"/;"/g"/;
          <View style={styles.tipItem}>
            <Icon name="refresh" size={16} color="#FF9800"  />"/;"/g"/;
            <Text style={styles.tipText}>下拉可刷新智能体状态</Text>
          </View>
        </View>
      </ScrollView>
    </View>
  );
};
const  styles = StyleSheet.create({)container: {,"flex: 1,";
}
    const backgroundColor = '#f5f5f5}
  },'
header: {,'flexDirection: 'row,'
justifyContent: 'space-between,'
alignItems: 'center,'';
paddingHorizontal: 20,
paddingVertical: 16,'
backgroundColor: 'white,'';
borderBottomWidth: 1,
}
    const borderBottomColor = '#e0e0e0}
  }
headerTitle: {,'fontSize: 20,'
fontWeight: 'bold,'
}
    const color = '#333}
  }
scrollView: {,}
    const flex = 1}
  },'
overview: {,'flexDirection: 'row,'
justifyContent: 'space-around,'';
paddingVertical: 20,'
backgroundColor: 'white,'
}
    const marginBottom = 16}
  },'
overviewCard: {,';}}
    const alignItems = 'center}
  }
overviewNumber: {,'fontSize: 24,'
fontWeight: 'bold,'
color: '#333,'
}
    const marginTop = 8}
  }
overviewLabel: {,'fontSize: 12,'
color: '#666,'
}
    const marginTop = 4}
  }
sectionTitle: {,'fontSize: 18,'
fontWeight: 'bold,'
color: '#333,'';
marginBottom: 16,
}
    const paddingHorizontal = 20}
  }
agentsList: {,}
    const marginBottom = 24}
  },'
agentCard: {,'backgroundColor: 'white,'';
borderRadius: 12,
padding: 16,
marginHorizontal: 20,
marginBottom: 16,
borderLeftWidth: 4,
}
    shadowColor: '#000,}'';
shadowOffset: { width: 0, height: 2 }
shadowOpacity: 0.1,
shadowRadius: 4,
const elevation = 3;
  }
disabledCard: {,}
    const opacity = 0.6}
  },'
cardHeader: {,'flexDirection: 'row,'
justifyContent: 'space-between,'
alignItems: 'flex-start,'
}
    const marginBottom = 16}
  },'
agentInfo: {,'flexDirection: 'row,'
}
    const flex = 1}
  }
agentAvatar: {fontSize: 32,
}
    const marginRight = 12}
  }
agentDetails: {,}
    const flex = 1}
  }
agentName: {,'fontSize: 16,'
fontWeight: 'bold,'
color: '#333,'
}
    const marginBottom = 4}
  }
agentDescription: {,'fontSize: 14,'
color: '#666,'
}
    const lineHeight = 20}
  },'
statusContainer: {,';}}
    const alignItems = 'flex-end}
  }
statusDot: {width: 8,
height: 8,
borderRadius: 4,
}
    const marginBottom = 4}
  }
statusText: {,'fontSize: 12,
}
    const fontWeight = '500}
  },'
metricsRow: {,'flexDirection: 'row,'
justifyContent: 'space-between,'';
marginBottom: 16,
paddingVertical: 12,
borderTopWidth: 1,
borderBottomWidth: 1,
}
    const borderColor = '#f0f0f0}
  },'
metric: {,';}}
    const alignItems = 'center}
  }
metricLabel: {,'fontSize: 12,'
color: '#666,'
}
    const marginBottom = 4}
  }
metricValue: {,'fontSize: 14,'
fontWeight: 'bold,'
}
    const color = '#333}
  }
capabilitiesContainer: {,}
    const marginBottom = 16}
  }
capabilitiesTitle: {,'fontSize: 14,'
fontWeight: '600,'
color: '#333,'
}
    const marginBottom = 8}
  },'
capabilitiesList: {,'flexDirection: 'row,'
}
    const flexWrap = 'wrap}
  },'
capabilityTag: {,'backgroundColor: '#e3f2fd,'';
borderRadius: 12,
paddingHorizontal: 8,
paddingVertical: 4,
marginRight: 8,
}
    const marginBottom = 4}
  }
capabilityText: {,'fontSize: 12,
}
    const color = '#1976d2}
  },'
cardActions: {,'flexDirection: 'row,'
justifyContent: 'space-between,'
}
    const alignItems = 'center}
  },'
chatButton: {,'flexDirection: 'row,'
alignItems: 'center,'
backgroundColor: '#2196F3,'';
borderRadius: 8,
paddingHorizontal: 16,
}
    const paddingVertical = 8}
  }
chatButtonText: {,'fontSize: 14,'
color: 'white,'';
marginLeft: 4,
}
    const fontWeight = '500}
  },'
switchContainer: {,'flexDirection: 'row,'
}
    const alignItems = 'center}
  }
switchLabel: {,'fontSize: 14,'
color: '#333,'
}
    const marginRight = 8}
  },'
tipsSection: {,'backgroundColor: 'white,'';
padding: 20,
}
    const marginBottom = 20}
  }
tipsTitle: {,'fontSize: 16,'
fontWeight: 'bold,'
color: '#333,'
}
    const marginBottom = 12}
  },'
tipItem: {,'flexDirection: 'row,'
alignItems: 'center,'
}
    const marginBottom = 8}
  }
tipText: {,'fontSize: 14,'
color: '#666,'';
marginLeft: 8,);
}
    const flex = 1;)}
  },);
});
export default AgentListScreen; ''