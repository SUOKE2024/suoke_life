import React from "react";";
import { View, Text, StyleSheet, TouchableOpacity, ActivityIndicator } from "react-native";";
import { useBlockchainStatusMonitor } from "../../hooks/useBlockchainService";""/;,"/g"/;
import { BlockchainStatus } from "../../types/blockchain";""/;,"/g"/;
interface BlockchainStatusCardProps {onPress?: () => void;}}
}
  showDetails?: boolean;}
}
export const BlockchainStatusCard: React.FC<BlockchainStatusCardProps> = ({));,}onPress,);
}
  showDetails = false;)}
}) => {}";,"";
const { status, isConnected, lastUpdate, refresh } = useBlockchainStatusMonitor();';,'';
const getStatusColor = useCallback(() => {if (!isConnected) return '#FF6B6B';';,}if (status?.consensusStatus === 'SYNCED') return '#4ECDC4';';,'';
if (status?.consensusStatus === 'SYNCING') return '#FFE66D';';'';
}
    return '#FF6B6B';'}'';'';
  };
';'';
  };';,'';
const formatTimestamp = useCallback((timestamp: number) => {return new Date(timestamp).toLocaleString('zh-CN');'}'';'';
  };';,'';
const formatBlockHeight = useCallback((height: number) => {return height.toLocaleString('zh-CN');'}'';'';
  };
return (<TouchableOpacity;)  />/;,/g/;
style={[styles.container, { borderLeftColor: getStatusColor() ;}}]}
      onPress={onPress}
      activeOpacity={0.7}
    >;
      <View style={styles.header}>;
        <View style={styles.statusIndicator}>;
          <View style={[styles.statusDot, { backgroundColor: getStatusColor() ;}}]}  />/;/g/;
          <Text style={styles.statusText}>{getStatusText()}</Text>/;/g/;
        </View>/;/g/;
        <TouchableOpacity onPress={refresh} style={styles.refreshButton}>;
          <Text style={styles.refreshText}>刷新</Text>/;/g/;
        </TouchableOpacity>/;/g/;
      </View>/;/g/;
      {status  && <View style={styles.content}>;
          <View style={styles.row}>;
            <Text style={styles.label}>区块高度: </Text>/;/g/;
            <Text style={styles.value}>{formatBlockHeight(status.currentBlockHeight)}</Text>/;/g/;
          </View>/;/g/;
          <View style={styles.row}>;
            <Text style={styles.label}>网络节点: </Text>/;/g/;
            <Text style={styles.value}>{status.nodeCount}</Text>'/;'/g'/;
          </View>'/;'/g'/;
          {status.consensusStatus === 'SYNCING'  && <View style={styles.row}>';'';
              <Text style={styles.label}>同步进度: </Text>/;/g/;
              <Text style={styles.value}>{status.syncPercentage.toFixed(1)}%</Text>/;/g/;
            </View>/;/g/;
          )}
          {showDetails  && <>}
              <View style={styles.row}>;
                <Text style={styles.label}>网络ID: </Text>/;/g/;
                <Text style={styles.value;}>{status.networkId}</Text>/;/g/;
              </View>/;/g/;
              <View style={styles.row}>;
                <Text style={styles.label}>交易池: </Text>/;/g/;
                <Text style={styles.value}>{status.transactionPoolSize}</Text>;/;/g/;
              </View>;/;/g/;
              <View style={styles.row}>;
                <Text style={styles.label}>最新区块: </Text>;/;/g/;
                <Text style={styles.value}>{formatTimestamp(status.lastBlockTimestamp)}</Text>;/;/g/;
              </View>;/;/g/;
            < />;/;/g/;
          )};
        </View>;/;/g/;
      )};';'';
      {lastUpdate && (;)'}'';'';
        <Text style={styles.lastUpdate}>最后更新: {lastUpdate.toLocaleTimeString('zh-CN')}</Text>;'/;'/g'/;
      )};
    </TouchableOpacity>;/;/g/;
  );
};
const  styles = StyleSheet.create({)';,}container: {,';,}backgroundColor: '#FFFFFF';','';
borderRadius: 12,;
padding: 16,;
marginVertical: 8,;
marginHorizontal: 16,';,'';
borderLeftWidth: 4,';,'';
shadowColor: '#000';','';
shadowOffset: {width: 0,;
}
      const height = 2;}
    }
shadowOpacity: 0.1,;
shadowRadius: 3.84,;
const elevation = 5;
  },';,'';
header: {,';,}flexDirection: 'row';','';
justifyContent: 'space-between';','';
alignItems: 'center';','';'';
}
    const marginBottom = 12;}
  },';,'';
statusIndicator: {,';,}flexDirection: 'row';','';'';
}
    const alignItems = 'center'}'';'';
  ;}
statusDot: {width: 8,;
height: 8,;
borderRadius: 4,;
}
    const marginRight = 8;}
  }
statusText: {,';,}fontSize: 16,';,'';
fontWeight: '600';','';'';
}
    const color = '#2C3E50'}'';'';
  ;}
refreshButton: {paddingHorizontal: 12,';,'';
paddingVertical: 6,';,'';
backgroundColor: '#F8F9FA';','';'';
}
    const borderRadius = 6;}
  }
refreshText: {,';,}fontSize: 14,';'';
}
    const color = '#6C757D'}'';'';
  ;}
content: {,;}}
  const marginBottom = 8;}
  },';,'';
row: {,';,}flexDirection: 'row';','';
justifyContent: 'space-between';','';
alignItems: 'center';','';'';
}
    const paddingVertical = 4;}
  }
label: {,';,}fontSize: 14,';'';
}
    color: '#6C757D',flex: 1;'}'';'';
  },value: {fontSize: 14,fontWeight: '500',color: '#2C3E50',flex: 1,textAlign: 'right';')}'';'';
  },lastUpdate: {fontSize: 12,color: '#ADB5BD',textAlign: 'center',marginTop: 8;')}'';'';
  };);
});
// 简化版状态指示器'/;,'/g'/;
export const BlockchainStatusIndicator: React.FC<{;}';'';
}
  size?: 'small' | 'medium' | 'large';'}'';'';
}> = ({ size = 'medium' }) => {'}'';
const { isConnected, status } = useBlockchainStatusMonitor();';,'';
const getSize = useCallback(() => {switch (size) {case 'small': return 6;';,}case 'medium': ';,'';
return 8;';,'';
case 'large': ';,'';
return 12;
}
      const default = return 8;}
    }';'';
  };';,'';
const getColor = useCallback(() => {if (!isConnected) return '#FF6B6B';';,}if (status?.consensusStatus === 'SYNCED') return '#4ECDC4';';,'';
if (status?.consensusStatus === 'SYNCING') return '#FFE66D';';'';
}
    return '#FF6B6B';'}'';'';
  };
return (;);
    <View;  />/;,/g/;
style={[;];}}
        {width: getSize(),height: getSize(),borderRadius: getSize() / 2,backgroundColor: getColor();}/;/g/;
        }}
];
      ]}
    />;/;/g/;
  );
};
// 区块链网络统计组件/;,/g/;
export const BlockchainNetworkStats: React.FC = () => {};
const { status, isConnected ;} = useBlockchainStatusMonitor();
if (!isConnected || !status) {}}
    return (;)}';'';
      <View style={statsStyles.statsContainer}}>;';'';
        <ActivityIndicator size='small' color='#6C757D'  />;'/;'/g'/;
        <Text style={statsStyles.statsText}}>连接中...</Text>;/;/g/;
      </View>;/;/g/;
    );
  }
  return (<View style={statsStyles.statsContainer}}>);
      <View style={statsStyles.statItem}}>);
        <Text style={statsStyles.statValue}}>{status.currentBlockHeight.toLocaleString()}</Text>/;/g/;
        <Text style={statsStyles.statLabel}}>区块高度</Text>/;/g/;
      </View>;/;/g/;
      <View style={statsStyles.statDivider}}  />;/;/g/;
      <View style={statsStyles.statItem}}>;
        <Text style={statsStyles.statValue}}>{status.nodeCount}</Text>;/;/g/;
        <Text style={statsStyles.statLabel}}>网络节点</Text>;/;/g/;
      </View>;/;/g/;
      <View style={statsStyles.statDivider}}  />;/;/g/;
      <View style={statsStyles.statItem}}>;
        <Text style={statsStyles.statValue}}>{status.transactionPoolSize}</Text>;/;/g/;
        <Text style={statsStyles.statLabel}}>待处理交易</Text>;/;/g/;
      </View>;/;/g/;
    </View>;/;/g/;
  );
};
const  statsStyles = StyleSheet.create({)';,}statsContainer: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';
justifyContent: 'space-around';','';
backgroundColor: '#F8F9FA';','';
borderRadius: 8,;
padding: 12,;
}
    const margin = 16;}
  },';,'';
statItem: {,';,}alignItems: 'center';','';'';
}
    const flex = 1;}
  }
statValue: {,';,}fontSize: 18,';,'';
fontWeight: '700';','';
color: '#2C3E50';','';'';
}
    const marginBottom = 2;}';'';
  },';,'';
statLabel: {fontSize: 12,color: '#6C757D',textAlign: 'center';'}'';'';
  },statDivider: {width: 1,height: 30,backgroundColor: '#DEE2E6',marginHorizontal: 8;')}'';'';
  },statsText: {fontSize: 14,color: '#6C757D',marginLeft: 8;')}'';'';
  };)';'';
});