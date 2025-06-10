import { useNavigation } from "@react-navigation/native";""/;,"/g"/;
import React, { useCallback, useState } from "react";";
import {Alert}Dimensions,;
Modal,;
RefreshControl,;
ScrollView,;
StyleSheet,;
Switch,;
Text,;
TouchableOpacity,";"";
}
    View'}'';'';
} from "react-native";";
import Icon from "react-native-vector-icons/MaterialIcons";""/;"/g"/;
';,'';
const { width: screenWidth ;} = Dimensions.get('window');';,'';
interface Agent {id: string}name: string,;
displayName: string,;
description: string,';,'';
avatar: string,';,'';
status: 'active' | 'inactive' | 'maintenance';','';
capabilities: string[],;
lastActive: string,;
responseTime: number,;
accuracy: number,;
}
}
  const color = string;}
}

interface AgentConfig {personality: string}responseStyle: string,;
knowledgeLevel: string,;
}
}
  const specialization = string[];}
}

/* 能 *//;/g/;
 *//;,/g/;
const  AgentManagementScreen: React.FC = () => {const navigation = useNavigation();,}const [refreshing, setRefreshing] = useState(false);
const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
const [configModalVisible, setConfigModalVisible] = useState(false);';,'';
const [agentConfig, setAgentConfig] = useState<AgentConfig>({';,)personality: 'friendly';','';,}responseStyle: 'detailed';',')';,'';
knowledgeLevel: 'expert';',')'';'';
}
    const specialization = [];)}
  });

  // 模拟智能体数据/;,/g/;
const [agents, setAgents] = useState<Agent[]>([;)';]    {';,}id: 'xiaoai';','';'';
';'';
';,'';
avatar: '🤖';','';
status: 'active';','';
responseTime: 1.2,';,'';
accuracy: 94.5,';'';
}
      const color = '#4CAF50';'}'';'';
    },';'';
    {';,}id: 'xiaoke';','';'';
';'';
';,'';
avatar: '🏥';','';
status: 'active';','';
responseTime: 2.1,';,'';
accuracy: 91.8,';'';
}
      const color = '#2196F3';'}'';'';
    },';'';
    {';,}id: 'laoke';','';'';
';'';
';,'';
avatar: '👨‍⚕️';','';
status: 'active';','';
responseTime: 3.5,';,'';
accuracy: 96.2,';'';
}
      const color = '#FF9800';'}'';'';
    },';'';
    {';,}id: 'soer';','';'';
';'';
';,'';
avatar: '📊';','';
status: 'maintenance';','';
responseTime: 1.8,';,'';
accuracy: 89.3,')'';'';
}
      const color = '#9C27B0';')}'';'';
    },);
];
  ]);
const  onRefresh = useCallback(async () => {setRefreshing(true);}    // 模拟数据刷新/;,/g,/;
  await: new Promise(resolve => setTimeout(resolve, 1000));
}
    setRefreshing(false);}
  }, []);
const  toggleAgentStatus = (agentId: string) => {setAgents(prevAgents =>;,)prevAgents.map(agent =>;,)agent.id === agentId;}          ? {';}              ...agent,';'';
}
              status: agent.status === 'active' ? 'inactive' : 'active';')}'';'';
            });
          : agent);
      );
    );
  };
const  openAgentConfig = (agent: Agent) => {setSelectedAgent(agent);}}
    setConfigModalVisible(true);}
  };
const  saveAgentConfig = () => {if (selectedAgent) {}}
      setConfigModalVisible(false);}
    }
  };
const  getStatusColor = (status: string) => {';,}switch (status) {';,}case 'active': return '#4CAF50';';,'';
case 'inactive': return '#9E9E9E';';,'';
case 'maintenance': return '#FF9800';';'';
}
      const default = return '#9E9E9E';'}'';'';
    }
  };
const  getStatusText = (status: string) => {switch (status) {}}
}
    ;}
  };
renderAgentCard: (agent: Agent) => (<View key={agent.id;} style={[styles.agentCard, { borderLeftColor: agent.color ;}]}>;)      <View style={styles.agentHeader}>;
        <View style={styles.agentInfo}>;
          <Text style={styles.agentAvatar}>{agent.avatar}</Text>/;/g/;
          <View style={styles.agentDetails}>;
            <Text style={styles.agentName}>{agent.displayName}</Text>/;/g/;
            <Text style={styles.agentDescription}>{agent.description}</Text>/;/g/;
          </View>)/;/g/;
        </View>)/;/g/;
        <View style={styles.agentStatus}>);
          <View style={[styles.statusDot, { backgroundColor: getStatusColor(agent.status) ;}]}  />/;/g/;
          <Text style={[styles.statusText, { color: getStatusColor(agent.status) ;}]}>;
            {getStatusText(agent.status)}
          </Text>/;/g/;
        </View>/;/g/;
      </View>/;/g/;

      <View style={styles.agentMetrics}>;
        <View style={styles.metric}>;
          <Text style={styles.metricLabel}>响应时间</Text>/;/g/;
          <Text style={styles.metricValue}>{agent.responseTime}s</Text>/;/g/;
        </View>/;/g/;
        <View style={styles.metric}>;
          <Text style={styles.metricLabel}>准确率</Text>/;/g/;
          <Text style={styles.metricValue}>{agent.accuracy}%</Text>/;/g/;
        </View>/;/g/;
        <View style={styles.metric}>;
          <Text style={styles.metricLabel}>最后活跃</Text>/;/g/;
          <Text style={styles.metricValue}>{agent.lastActive}</Text>/;/g/;
        </View>/;/g/;
      </View>/;/g/;

      <View style={styles.agentCapabilities}>;
        <Text style={styles.capabilitiesTitle}>核心能力: </Text>/;/g/;
        <View style={styles.capabilitiesList}>;
          {agent.capabilities.map((capability, index) => (<View key={index} style={styles.capabilityTag}>);
              <Text style={styles.capabilityText}>{capability}</Text>)/;/g/;
            </View>)/;/g/;
          ))}
        </View>/;/g/;
      </View>/;/g/;

      <View style={styles.agentActions}>;
        <TouchableOpacity,'  />/;,'/g'/;
style={styles.actionButton}';,'';
onPress={() => navigation.navigate('AgentChat' as never, { agentId: agent.id, agentName: agent.name ;} as never)}';'';
        >';'';
          <Icon name="chat" size={16} color="#2196F3"  />"/;"/g"/;
          <Text style={styles.actionButtonText}>对话</Text>/;/g/;
        </TouchableOpacity>/;/g/;

        <TouchableOpacity,  />/;,/g/;
style={styles.actionButton}
          onPress={() => openAgentConfig(agent)}";"";
        >";"";
          <Icon name="settings" size={16} color="#FF9800"  />"/;"/g"/;
          <Text style={styles.actionButtonText}>配置</Text>/;/g/;
        </TouchableOpacity>/;/g/;

        <View style={styles.switchContainer}>;
          <Text style={styles.switchLabel}>启用</Text>"/;"/g"/;
          <Switch,"  />/;,"/g"/;
value={agent.status === 'active'}';,'';
onValueChange={() => toggleAgentStatus(agent.id)}';,'';
trackColor={{ false: '#767577', true: '#81b0ff' ;}}';,'';
thumbColor={agent.status === 'active' ? '#2196F3' : '#f4f3f4'}';'';
          />/;/g/;
        </View>/;/g/;
      </View>/;/g/;
    </View>/;/g/;
  );
const: renderConfigModal = () => (<Modal,'  />/;,)visible={configModalVisible}')'';,'/g'/;
animationType="slide")";,"";
presentationStyle="pageSheet")";,"";
onRequestClose={() => setConfigModalVisible(false)}
    >;
      <View style={styles.modalContainer}>;
        <View style={styles.modalHeader}>";"";
          <TouchableOpacity onPress={() => setConfigModalVisible(false)}>";"";
            <Icon name="close" size={24} color="#666"  />"/;"/g"/;
          </TouchableOpacity>/;/g/;
          <Text style={styles.modalTitle}>;

          </Text>/;/g/;
          <TouchableOpacity onPress={saveAgentConfig}>;
            <Text style={styles.saveButton}>保存</Text>/;/g/;
          </TouchableOpacity>/;/g/;
        </View>/;/g/;

        <ScrollView style={styles.modalContent}>;
          <View style={styles.configSection}>;
            <Text style={styles.configLabel}>个性化设置</Text>/;/g/;
            <View style={styles.configOptions}>;

                <TouchableOpacity,  />/;,/g/;
key={option}
                  style={[;,]styles.configOption,;}}
                    agentConfig.personality === option && styles.selectedOption,}
];
                  ]}
                  onPress={() => setAgentConfig({ ...agentConfig, personality: option ;})}
                >;
                  <Text,  />/;,/g/;
style={[;,]styles.configOptionText,;}}
                      agentConfig.personality === option && styles.selectedOptionText,}
];
                    ]}
                  >;
                    {option}
                  </Text>/;/g/;
                </TouchableOpacity>/;/g/;
              ))}
            </View>/;/g/;
          </View>/;/g/;

          <View style={styles.configSection}>;
            <Text style={styles.configLabel}>回复风格</Text>/;/g/;
            <View style={styles.configOptions}>;

                <TouchableOpacity,  />/;,/g/;
key={option}
                  style={[;,]styles.configOption,;}}
                    agentConfig.responseStyle === option && styles.selectedOption,}
];
                  ]}
                  onPress={() => setAgentConfig({ ...agentConfig, responseStyle: option ;})}
                >;
                  <Text,  />/;,/g/;
style={[;,]styles.configOptionText,;}}
                      agentConfig.responseStyle === option && styles.selectedOptionText,}
];
                    ]}
                  >;
                    {option}
                  </Text>/;/g/;
                </TouchableOpacity>/;/g/;
              ))}
            </View>/;/g/;
          </View>/;/g/;

          <View style={styles.configSection}>;
            <Text style={styles.configLabel}>知识水平</Text>/;/g/;
            <View style={styles.configOptions}>;

                <TouchableOpacity,  />/;,/g/;
key={option}
                  style={[;,]styles.configOption,;}}
                    agentConfig.knowledgeLevel === option && styles.selectedOption,}
];
                  ]}
                  onPress={() => setAgentConfig({ ...agentConfig, knowledgeLevel: option ;})}
                >;
                  <Text,  />/;,/g/;
style={[;,]styles.configOptionText,;}}
                      agentConfig.knowledgeLevel === option && styles.selectedOptionText,}
];
                    ]}
                  >;
                    {option}
                  </Text>/;/g/;
                </TouchableOpacity>/;/g/;
              ))}
            </View>/;/g/;
          </View>/;/g/;
        </ScrollView>/;/g/;
      </View>/;/g/;
    </Modal>/;/g/;
  );
return (<View style={styles.container}>);
      <View style={styles.header}>)";"";
        <TouchableOpacity onPress={() => navigation.goBack()}>";"";
          <Icon name="arrow-back" size={24} color="#333"  />"/;"/g"/;
        </TouchableOpacity>/;/g/;
        <Text style={styles.headerTitle}>智能体管理</Text>"/;"/g"/;
        <TouchableOpacity onPress={onRefresh}>";"";
          <Icon name="refresh" size={24} color="#333"  />"/;"/g"/;
        </TouchableOpacity>/;/g/;
      </View>/;/g/;

      <ScrollView,  />/;,/g/;
style={styles.scrollView}
        refreshControl={}
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh}  />/;/g/;
        }
        showsVerticalScrollIndicator={false}
      >;
        <View style={styles.summary}>;
          <Text style={styles.summaryText}>;

          </Text>/;/g/;
        </View>/;/g/;

        <View style={styles.agentsList}>;
          {agents.map(renderAgentCard)}
        </View>/;/g/;
      </ScrollView>/;/g/;

      {renderConfigModal()}
    </View>/;/g/;
  );
};
const  styles = StyleSheet.create({)container: {,";,}flex: 1,";"";
}
    const backgroundColor = '#f5f5f5';'}'';'';
  },';,'';
header: {,';,}flexDirection: 'row';','';
justifyContent: 'space-between';','';
alignItems: 'center';','';
paddingHorizontal: 20,';,'';
paddingVertical: 16,';,'';
backgroundColor: 'white';','';
borderBottomWidth: 1,';'';
}
    const borderBottomColor = '#e0e0e0';'}'';'';
  }
headerTitle: {,';,}fontSize: 20,';,'';
fontWeight: 'bold';','';'';
}
    const color = '#333';'}'';'';
  }
scrollView: {,;}}
    const flex = 1;}
  }
summary: {,';,}padding: 20,';,'';
backgroundColor: 'white';','';'';
}
    const marginBottom = 16;}
  }
summaryText: {,';,}fontSize: 16,';,'';
color: '#666';','';'';
}
    const textAlign = 'center';'}'';'';
  }
agentsList: {,;}}
    const paddingHorizontal = 20;}
  },';,'';
agentCard: {,';,}backgroundColor: 'white';','';
borderRadius: 12,;
padding: 16,;
marginBottom: 16,';,'';
borderLeftWidth: 4,';'';
}
    shadowColor: '#000';','}'';
shadowOffset: { width: 0, height: 2 ;}
shadowOpacity: 0.1,;
shadowRadius: 4,;
const elevation = 3;
  },';,'';
agentHeader: {,';,}flexDirection: 'row';','';
justifyContent: 'space-between';','';
alignItems: 'flex-start';','';'';
}
    const marginBottom = 16;}
  },';,'';
agentInfo: {,';,}flexDirection: 'row';','';'';
}
    const flex = 1;}
  }
agentAvatar: {fontSize: 32,;
}
    const marginRight = 12;}
  }
agentDetails: {,;}}
    const flex = 1;}
  }
agentName: {,';,}fontSize: 18,';,'';
fontWeight: 'bold';','';
color: '#333';','';'';
}
    const marginBottom = 4;}
  }
agentDescription: {,';,}fontSize: 14,';,'';
color: '#666';','';'';
}
    const lineHeight = 20;}
  },';,'';
agentStatus: {,';}}'';
    const alignItems = 'flex-end';'}'';'';
  }
statusDot: {width: 8,;
height: 8,;
borderRadius: 4,;
}
    const marginBottom = 4;}
  }
statusText: {,';,}fontSize: 12,';'';
}
    const fontWeight = '500';'}'';'';
  },';,'';
agentMetrics: {,';,}flexDirection: 'row';','';
justifyContent: 'space-between';','';
marginBottom: 16,;
paddingVertical: 12,;
borderTopWidth: 1,';,'';
borderBottomWidth: 1,';'';
}
    const borderColor = '#f0f0f0';'}'';'';
  },';,'';
metric: {,';}}'';
    const alignItems = 'center';'}'';'';
  }
metricLabel: {,';,}fontSize: 12,';,'';
color: '#666';','';'';
}
    const marginBottom = 4;}
  }
metricValue: {,';,}fontSize: 14,';,'';
fontWeight: 'bold';','';'';
}
    const color = '#333';'}'';'';
  }
agentCapabilities: {,;}}
    const marginBottom = 16;}
  }
capabilitiesTitle: {,';,}fontSize: 14,';,'';
fontWeight: '600';','';
color: '#333';','';'';
}
    const marginBottom = 8;}
  },';,'';
capabilitiesList: {,';,}flexDirection: 'row';','';'';
}
    const flexWrap = 'wrap';'}'';'';
  },';,'';
capabilityTag: {,';,}backgroundColor: '#e3f2fd';','';
borderRadius: 12,;
paddingHorizontal: 8,;
paddingVertical: 4,;
marginRight: 8,;
}
    const marginBottom = 4;}
  }
capabilityText: {,';,}fontSize: 12,';'';
}
    const color = '#1976d2';'}'';'';
  },';,'';
agentActions: {,';,}flexDirection: 'row';','';
justifyContent: 'space-between';','';'';
}
    const alignItems = 'center';'}'';'';
  },';,'';
actionButton: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';
paddingHorizontal: 12,;
paddingVertical: 8,';,'';
borderRadius: 8,';'';
}
    const backgroundColor = '#f5f5f5';'}'';'';
  }
actionButtonText: {,';,}fontSize: 14,';,'';
color: '#333';','';'';
}
    const marginLeft = 4;}
  },';,'';
switchContainer: {,';,}flexDirection: 'row';','';'';
}
    const alignItems = 'center';'}'';'';
  }
switchLabel: {,';,}fontSize: 14,';,'';
color: '#333';','';'';
}
    const marginRight = 8;}
  }
modalContainer: {,';,}flex: 1,';'';
}
    const backgroundColor = 'white';'}'';'';
  },';,'';
modalHeader: {,';,}flexDirection: 'row';','';
justifyContent: 'space-between';','';
alignItems: 'center';','';
paddingHorizontal: 20,;
paddingVertical: 16,';,'';
borderBottomWidth: 1,';'';
}
    const borderBottomColor = '#e0e0e0';'}'';'';
  }
modalTitle: {,';,}fontSize: 18,';,'';
fontWeight: 'bold';','';'';
}
    const color = '#333';'}'';'';
  }
saveButton: {,';,}fontSize: 16,';,'';
color: '#2196F3';','';'';
}
    const fontWeight = '600';'}'';'';
  }
modalContent: {flex: 1,;
}
    const padding = 20;}
  }
configSection: {,;}}
    const marginBottom = 24;}
  }
configLabel: {,';,}fontSize: 16,';,'';
fontWeight: '600';','';
color: '#333';','';'';
}
    const marginBottom = 12;}
  },';,'';
configOptions: {,';,}flexDirection: 'row';','';'';
}
    const flexWrap = 'wrap';'}'';'';
  }
configOption: {paddingHorizontal: 16,;
paddingVertical: 8,';,'';
borderRadius: 20,';,'';
backgroundColor: '#f5f5f5';','';
marginRight: 8,;
}
    const marginBottom = 8;}
  },';,'';
selectedOption: {,';}}'';
    const backgroundColor = '#2196F3';'}'';'';
  }
configOptionText: {,';,}fontSize: 14,';'';
}
    const color = '#333';'}'';'';
  },';,'';
selectedOptionText: {,')'';}}'';
    const color = 'white';')}'';'';
  },);
});
';,'';
export default AgentManagementScreen; ''';