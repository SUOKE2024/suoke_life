import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Animated } from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { offlineService, getSyncStatus, addSyncListener, SyncStatus } from '../../services/offlineService';
import { GATEWAY_FEATURES } from '../../constants/config';
interface OfflineIndicatorProps {
  style?: any;
  showDetails?: boolean;
  onPress?: () => void;
}
export const OfflineIndicator: React.FC<OfflineIndicatorProps> = ({
  style,
  showDetails = false,
  onPress,
}) => {
  const [syncStatus, setSyncStatus] = useState<SyncStatus>(getSyncStatus());
  const [fadeAnim] = useState(new Animated.Value(0));
  const [slideAnim] = useState(new Animated.Value(-100));
  useEffect() => {
    // 监听同步状态变化
    const unsubscribe = addSyncListener(status) => {
      setSyncStatus(status);
    });
    return unsubscribe;
  }, []);
  useEffect() => {
    // 当离线时显示指示器
    if (!syncStatus.isOnline || syncStatus.pendingOperations > 0) {
      Animated.parallel([
        Animated.timing(fadeAnim, {
          toValue: 1,
          duration: 300,
          useNativeDriver: true,
        }),
        Animated.timing(slideAnim, {
          toValue: 0,
          duration: 300,
          useNativeDriver: true,
        }),
      ]).start();
    } else {
      Animated.parallel([
        Animated.timing(fadeAnim, {
          toValue: 0,
          duration: 300,
          useNativeDriver: true,
        }),
        Animated.timing(slideAnim, {
          toValue: -100,
          duration: 300,
          useNativeDriver: true,
        }),
      ]).start();
    }
  }, [syncStatus.isOnline, syncStatus.pendingOperations, fadeAnim, slideAnim]);
  // 如果没有启用离线功能，不显示指示器
  if (!GATEWAY_FEATURES.ENABLE_OFFLINE) {
    return null;
  }
  // 如果在线且没有待处理操作，不显示指示器
  if (syncStatus.isOnline && syncStatus.pendingOperations === 0) {
    return null;
  }
  const getStatusColor = () => {
    if (!syncStatus.isOnline) return '#f44336'; // 红色 - 离线
    if (syncStatus.syncInProgress) return '#ff9800'; // 橙色 - 同步中
    if (syncStatus.pendingOperations > 0) return '#2196F3'; // 蓝色 - 有待处理操作
    return '#4CAF50'; // 绿色 - 正常
  };
  const getStatusText = () => {
    if (!syncStatus.isOnline) return '离线模式';
    if (syncStatus.syncInProgress) return '正在同步...';
    if (syncStatus.pendingOperations > 0) return `${syncStatus.pendingOperations} 个操作待同步`;
    return '已同步';
  };
  const getStatusIcon = () => {
    if (!syncStatus.isOnline) return 'cloud-off';
    if (syncStatus.syncInProgress) return 'sync';
    if (syncStatus.pendingOperations > 0) return 'cloud-queue';
    return 'cloud-done';
  };
  const handlePress = () => {
    if (onPress) {
      onPress();
    } else if (syncStatus.isOnline && syncStatus.pendingOperations > 0) {
      // 手动触发同步
      offlineService.forcSync().catch(console.error);
    }
  };
  const renderBasicIndicator = () => (
    <Animated.View;
      style={[
        styles.basicIndicator,
        { backgroundColor: getStatusColor() },
        {
          opacity: fadeAnim,
          transform: [{ translateY: slideAnim }],
        },
        style,
      ]}
    >
      <TouchableOpacity;
        style={styles.basicContent}
        onPress={handlePress}
        activeOpacity={0.8}
      >
        <Icon name={getStatusIcon()} size={16} color="#fff" />
        <Text style={styles.basicText}>{getStatusText()}</Text>
        {syncStatus.pendingOperations > 0 && (
        <View style={styles.badge}>
            <Text style={styles.badgeText}>{syncStatus.pendingOperations}</Text>
          </View>
        )}
      </TouchableOpacity>
    </Animated.View>
  );
  const renderDetailedIndicator = () => (
    <Animated.View;
      style={[
        styles.detailedIndicator,
        {
          opacity: fadeAnim,
          transform: [{ translateY: slideAnim }],
        },
        style,
      ]}
    >
      <TouchableOpacity;
        style={styles.detailedContent}
        onPress={handlePress}
        activeOpacity={0.8}
      >
        <View style={styles.statusHeader}>
          <Icon name={getStatusIcon()} size={24} color={getStatusColor()} />
          <Text style={[styles.statusTitle, { color: getStatusColor() }]}>
            {getStatusText()}
          </Text>
        </View>
        <View style={styles.statusDetails}>
          <View style={styles.statusRow}>
            <Text style={styles.statusLabel}>网络状态:</Text>
            <Text style={[styles.statusValue, { color: syncStatus.isOnline ? '#4CAF50' : '#f44336' }]}>
              {syncStatus.isOnline ? '在线' : '离线'}
            </Text>
          </View>
          {syncStatus.pendingOperations > 0 && (
        <View style={styles.statusRow}>
              <Text style={styles.statusLabel}>待同步操作:</Text>
              <Text style={styles.statusValue}>{syncStatus.pendingOperations}</Text>
            </View>
          )}
          {syncStatus.failedOperations > 0 && (
        <View style={styles.statusRow}>
              <Text style={styles.statusLabel}>失败操作:</Text>
              <Text style={[styles.statusValue, { color: '#f44336' }]}>
                {syncStatus.failedOperations}
              </Text>
            </View>
          )}
          {syncStatus.lastSyncTime && (
        <View style={styles.statusRow}>
              <Text style={styles.statusLabel}>上次同步:</Text>
              <Text style={styles.statusValue}>
                {new Date(syncStatus.lastSyncTime).toLocaleTimeString()}
              </Text>
            </View>
          )}
        </View>
        {syncStatus.isOnline && syncStatus.pendingOperations > 0 && (
        <View style={styles.actionButton}>
            <Text style={styles.actionButtonText}>点击同步</Text>
          </View>
        )}
      </TouchableOpacity>
    </Animated.View>
  );
  return showDetails ? renderDetailedIndicator() : renderBasicIndicator();
};
// 同步状态卡片组件
interface SyncStatusCardProps {
  style?: any;
}
export const SyncStatusCard: React.FC<SyncStatusCardProps> = ({ style }) => {
  const [syncStatus, setSyncStatus] = useState<SyncStatus>(getSyncStatus());
  const [cacheStats, setCacheStats] = useState<any>(null);
  useEffect() => {
    const unsubscribe = addSyncListener(setSyncStatus);
    // 获取缓存统计
    const stats = offlineService.getCacheStats();
    setCacheStats(stats);
    return unsubscribe;
  }, []);  // 检查是否需要添加依赖项;
  if (!GATEWAY_FEATURES.ENABLE_OFFLINE) {
    return null;
  }
  const handleForcSync = async () => {
    try {
      await offlineService.forcSync();
    } catch (error) {
      console.error('Force sync failed:', error);
    }
  };
  const handleClearCache = async () => {
    try {
      await offlineService.clearOfflineData();
      const stats = offlineService.getCacheStats();
      setCacheStats(stats);
    } catch (error) {
      console.error('Clear cache failed:', error);
    }
  };
  return (
    <View style={[styles.syncCard, style]}>
      <View style={styles.syncCardHeader}>
        <Icon name="sync" size={24} color="#2196F3" />
        <Text style={styles.syncCardTitle}>同步状态</Text>
      </View>
      <View style={styles.syncCardContent}>
        <View style={styles.statusGrid}>
          <View style={styles.statusItem}>
            <Text style={styles.statusItemLabel}>网络</Text>
            <Text style={[
              styles.statusItemValue,
              { color: syncStatus.isOnline ? '#4CAF50' : '#f44336' },
            ]}>
              {syncStatus.isOnline ? '在线' : '离线'}
            </Text>
          </View>
          <View style={styles.statusItem}>
            <Text style={styles.statusItemLabel}>待同步</Text>
            <Text style={styles.statusItemValue}>{syncStatus.pendingOperations}</Text>
          </View>
          <View style={styles.statusItem}>
            <Text style={styles.statusItemLabel}>失败</Text>
            <Text style={[
              styles.statusItemValue,
              { color: syncStatus.failedOperations > 0 ? '#f44336' : '#666' },
            ]}>
              {syncStatus.failedOperations}
            </Text>
          </View>
          <View style={styles.statusItem}>
            <Text style={styles.statusItemLabel}>同步中</Text>
            <Text style={[
              styles.statusItemValue,
              { color: syncStatus.syncInProgress ? '#ff9800' : '#666' },
            ]}>
              {syncStatus.syncInProgress ? '是' : '否'}
            </Text>
          </View>
        </View>
        {cacheStats && (
        <View style={styles.cacheStats}>
            <Text style={styles.cacheStatsTitle}>缓存统计</Text>
            <Text style={styles.cacheStatsText}>
              缓存项: {cacheStats.totalItems} |
              大小: {Math.round(cacheStats.totalSize / 1024)}KB |
              过期: {cacheStats.expiredItems}
            </Text>
          </View>
        )}
        <View style={styles.syncCardActions}>
          {syncStatus.isOnline && syncStatus.pendingOperations > 0 && (
            <TouchableOpacity style={styles.syncButton} onPress={handleForcSync}>
              <Icon name="sync" size={16} color="#fff" />
              <Text style={styles.syncButtonText}>立即同步</Text>
            </TouchableOpacity>
          )}
          <TouchableOpacity style={styles.clearButton} onPress={handleClearCache}>
            <Icon name="clear-all" size={16} color="#666" />
            <Text style={styles.clearButtonText}>清除缓存</Text>
          </TouchableOpacity>
        </View>
      </View>
    </View>
  );
};
const styles = StyleSheet.create({
  basicIndicator: {,
  position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    zIndex: 1000,
  },
  basicContent: {,
  flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 8,
    paddingHorizontal: 16,
    gap: 8,
  },
  basicText: {,
  color: '#fff',
    fontSize: 14,
    fontWeight: '500',
  },
  badge: {,
  backgroundColor: 'rgba(255, 255, 255, 0.3)',
    borderRadius: 10,
    paddingHorizontal: 6,
    paddingVertical: 2,
    minWidth: 20,
    alignItems: 'center',
  },
  badgeText: {,
  color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  detailedIndicator: {,
  backgroundColor: '#fff',
    margin: 16,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  detailedContent: {,
  padding: 16,
  },
  statusHeader: {,
  flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
    gap: 12,
  },
  statusTitle: {,
  fontSize: 18,
    fontWeight: 'bold',
  },
  statusDetails: {,
  gap: 8,
  },
  statusRow: {,
  flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  statusLabel: {,
  fontSize: 14,
    color: '#666',
  },
  statusValue: {,
  fontSize: 14,
    fontWeight: '500',
    color: '#333',
  },
  actionButton: {,
  marginTop: 16,
    backgroundColor: '#2196F3',
    borderRadius: 8,
    paddingVertical: 12,
    alignItems: 'center',
  },
  actionButtonText: {,
  color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  syncCard: {,
  backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  syncCardHeader: {,
  flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
    gap: 12,
  },
  syncCardTitle: {,
  fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  syncCardContent: {,
  gap: 16,
  },
  statusGrid: {,
  flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 16,
  },
  statusItem: {,
  flex: 1,
    minWidth: '40%',
    alignItems: 'center',
  },
  statusItemLabel: {,
  fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  statusItemValue: {,
  fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  cacheStats: {,
  backgroundColor: '#f5f5f5',
    borderRadius: 8,
    padding: 12,
  },
  cacheStatsTitle: {,
  fontSize: 14,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  cacheStatsText: {,
  fontSize: 12,
    color: '#666',
  },
  syncCardActions: {,
  flexDirection: 'row',
    gap: 12,
  },
  syncButton: {,
  flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#2196F3',
    borderRadius: 8,
    paddingVertical: 12,
    gap: 8,
  },
  syncButtonText: {,
  color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  clearButton: {,
  flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'transparent',
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    paddingVertical: 12,
    gap: 8,
  },
  clearButtonText: {,
  color: '#666',
    fontSize: 14,
    fontWeight: '600',
  },
});
export default OfflineIndicator;