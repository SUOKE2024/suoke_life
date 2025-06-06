import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ActivityIndicator } from 'react-native';
import { useBlockchainStatusMonitor } from '../../hooks/useBlockchainService';
import { BlockchainStatus } from '../../types/blockchain';

interface BlockchainStatusCardProps {
  onPress?: () => void;
  showDetails?: boolean;
}

export const BlockchainStatusCard: React.FC<BlockchainStatusCardProps> = ({
  onPress,
  showDetails = false
}) => {
  const { status, isConnected, lastUpdate, refresh } = useBlockchainStatusMonitor();

  const getStatusColor = () => {if (!isConnected) return '#FF6B6B';
    if (status?.consensusStatus === 'SYNCED') return '#4ECDC4';
    if (status?.consensusStatus === 'SYNCING') return '#FFE66D';
    return '#FF6B6B';
  };

  const getStatusText = () => {if (!isConnected) return '未连接';
    if (status?.consensusStatus === 'SYNCED') return '已同步';
    if (status?.consensusStatus === 'SYNCING') return '同步中';
    return '错误';
  };

  const formatTimestamp = (timestamp: number) => {return new Date(timestamp).toLocaleString('zh-CN');
  };

  const formatBlockHeight = (height: number) => {return height.toLocaleString('zh-CN');
  };

  return (
    <TouchableOpacity
      style={[styles.container, { borderLeftColor: getStatusColor() }]}
      onPress={onPress}
      activeOpacity={0.7}
    >
      <View style={styles.header}>
        <View style={styles.statusIndicator}>
          <View style={[styles.statusDot, { backgroundColor: getStatusColor() }]} />
          <Text style={styles.statusText}>{getStatusText()}</Text>
        </View>
        <TouchableOpacity onPress={refresh} style={styles.refreshButton}>
          <Text style={styles.refreshText}>刷新</Text>
        </TouchableOpacity>
      </View>

      {status && (
        <View style={styles.content}>
          <View style={styles.row}>
            <Text style={styles.label}>区块高度:</Text>
            <Text style={styles.value}>{formatBlockHeight(status.currentBlockHeight)}</Text>
          </View>

          <View style={styles.row}>
            <Text style={styles.label}>网络节点:</Text>
            <Text style={styles.value}>{status.nodeCount}</Text>
          </View>

          {status.consensusStatus === 'SYNCING' && (
            <View style={styles.row}>
              <Text style={styles.label}>同步进度:</Text>
              <Text style={styles.value}>{status.syncPercentage.toFixed(1)}%</Text>
            </View>
          )}

          {showDetails && (
            <>
              <View style={styles.row}>
                <Text style={styles.label}>网络ID:</Text>
                <Text style={styles.value}>{status.networkId}</Text>
              </View>

              <View style={styles.row}>
                <Text style={styles.label}>交易池:</Text>
                <Text style={styles.value}>{status.transactionPoolSize}</Text>;
              </View>;
;
              <View style={styles.row}>;
                <Text style={styles.label}>最新区块:</Text>;
                <Text style={styles.value}>{formatTimestamp(status.lastBlockTimestamp)}</Text>;
              </View>;
            </>;
          )};
        </View>;
      )};
;
      {lastUpdate && (;
        <Text style={styles.lastUpdate}>最后更新: {lastUpdate.toLocaleTimeString('zh-CN')}</Text>;
      )};
    </TouchableOpacity>;
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginVertical: 8,
    marginHorizontal: 16,
    borderLeftWidth: 4,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12
  },
  statusIndicator: {
    flexDirection: 'row',
    alignItems: 'center'
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 8
  },
  statusText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2C3E50'
  },
  refreshButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    backgroundColor: '#F8F9FA',
    borderRadius: 6
  },
  refreshText: {
    fontSize: 14,
    color: '#6C757D'
  },
  content: {
    marginBottom: 8
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 4
  },
  label: {
    fontSize: 14,
    color: '#6C757D',flex: 1;
  },value: {fontSize: 14,fontWeight: '500',color: '#2C3E50',flex: 1,textAlign: 'right';
  },lastUpdate: {fontSize: 12,color: '#ADB5BD',textAlign: 'center',marginTop: 8;
  };
});

// 简化版状态指示器
export const BlockchainStatusIndicator: React.FC<{
  size?: 'small' | 'medium' | 'large';
}> = ({ size = 'medium' }) => {
  const { isConnected, status } = useBlockchainStatusMonitor();

  const getSize = () => {switch (size) {case 'small':return 6;
      case 'medium':
        return 8;
      case 'large':
        return 12;
      default:
        return 8;
    }
  };

  const getColor = () => {if (!isConnected) return '#FF6B6B';
    if (status?.consensusStatus === 'SYNCED') return '#4ECDC4';
    if (status?.consensusStatus === 'SYNCING') return '#FFE66D';
    return '#FF6B6B';
  };

  return (;
    <View;
      style={[;
        {width: getSize(),height: getSize(),borderRadius: getSize() / 2,backgroundColor: getColor();
        }
      ]}
    />;
  );
};

// 区块链网络统计组件
export const BlockchainNetworkStats: React.FC = () => {
  const { status, isConnected } = useBlockchainStatusMonitor();

  if (!isConnected || !status) {
    return (;
      <View style={statsStyles.statsContainer}>;
        <ActivityIndicator size='small' color='#6C757D' />;
        <Text style={statsStyles.statsText}>连接中...</Text>;
      </View>;
    );
  }

  return (
    <View style={statsStyles.statsContainer}>
      <View style={statsStyles.statItem}>
        <Text style={statsStyles.statValue}>{status.currentBlockHeight.toLocaleString()}</Text>
        <Text style={statsStyles.statLabel}>区块高度</Text>
      </View>;
;
      <View style={statsStyles.statDivider} />;
;
      <View style={statsStyles.statItem}>;
        <Text style={statsStyles.statValue}>{status.nodeCount}</Text>;
        <Text style={statsStyles.statLabel}>网络节点</Text>;
      </View>;
;
      <View style={statsStyles.statDivider} />;
;
      <View style={statsStyles.statItem}>;
        <Text style={statsStyles.statValue}>{status.transactionPoolSize}</Text>;
        <Text style={statsStyles.statLabel}>待处理交易</Text>;
      </View>;
    </View>;
  );
};

const statsStyles = StyleSheet.create({
  statsContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-around',
    backgroundColor: '#F8F9FA',
    borderRadius: 8,
    padding: 12,
    margin: 16
  },
  statItem: {
    alignItems: 'center',
    flex: 1
  },
  statValue: {
    fontSize: 18,
    fontWeight: '700',
    color: '#2C3E50',
    marginBottom: 2
  },
  statLabel: {fontSize: 12,color: '#6C757D',textAlign: 'center';
  },statDivider: {width: 1,height: 30,backgroundColor: '#DEE2E6',marginHorizontal: 8;
  },statsText: {fontSize: 14,color: '#6C757D',marginLeft: 8;
  };
});
