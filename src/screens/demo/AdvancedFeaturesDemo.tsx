import { graphqlClient } from '../../services/graphql/client';
import { offlineManager } from '../../services/offline/offlineManager';
import { createWebSocketManager, WebSocketManager } from '../../services/websocket/websocketManager';
import { memoryCache, persistentCache, apiCache } from '../../services/cache/cacheManager';





/**
 * 索克生活 - 高级功能演示界面
 * 展示GraphQL API、离线模式、WebSocket实时通信和缓存策略
 */

import React, { useState, useEffect, useCallback } from 'react';
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Alert,
  Switch,
} from 'react-native';

interface DemoState {
  // GraphQL状态
  graphqlConnected: boolean;
  graphqlLoading: boolean;
  graphqlResult: string;
  
  // 离线模式状态
  offlineInitialized: boolean;
  syncStatus: string;
  operationCount: number;
  conflictCount: number;
  
  // WebSocket状态
  wsConnected: boolean;
  wsLatency: number;
  wsMessages: string[];
  
  // 缓存状态
  cacheStats: {
    memory: any;
    persistent: any;
    api: any;
  };
}

export const AdvancedFeaturesDemo: React.FC = () => {
  const [state, setState] = useState<DemoState>({
    graphqlConnected: false,
    graphqlLoading: false,
    graphqlResult: '',
    offlineInitialized: false,
    syncStatus: 'idle',
    operationCount: 0,
    conflictCount: 0,
    wsConnected: false,
    wsLatency: 0,
    wsMessages: [],
    cacheStats: {
      memory: {},
      persistent: {},
      api: {},
    },
  });

  const [wsManager, setWsManager] = useState<WebSocketManager | null>(null);
  const [testData, setTestData] = useState({
    graphqlQuery: `query GetUsers {
  users {
    id
    name
    email
  }
}`,
    cacheKey: 'test-key',
    cacheValue: 'test-value',
    wsMessage: 'Hello WebSocket!',
  });

  useEffect(() => {
    initializeServices();
    return () => {
      cleanup();
    };
  }, []);

  /**
   * 初始化服务
   */
  const initializeServices = async () => {
    try {
      // 初始化离线管理器
      await offlineManager.initialize();
      setState(prev => ({ ...prev, offlineInitialized: true }));

      // 设置离线管理器事件监听
      offlineManager.on('syncStart', () => {
        setState(prev => ({ ...prev, syncStatus: 'syncing' }));
      });

      offlineManager.on('syncComplete', () => {
        setState(prev => ({ ...prev, syncStatus: 'completed' }));
        updateOfflineStats();
      });

      offlineManager.on('syncError', () => {
        setState(prev => ({ ...prev, syncStatus: 'error' }));
      });

      // 初始化WebSocket管理器
      const ws = createWebSocketManager({
        url: 'ws://localhost:8080/ws',
        heartbeat: {
          enabled: true,
          interval: 30000,
          timeout: 5000,
        },
        reconnect: {
          enabled: true,
          maxAttempts: 5,
          delay: 1000,
          backoffMultiplier: 2,
          maxDelay: 30000,
        },
        messageQueue: {
          enabled: true,
          maxSize: 100,
        },
      });

      // 设置WebSocket事件监听
      ws.on('connected', () => {
        setState(prev => ({ ...prev, wsConnected: true }));
      });

      ws.on('disconnected', () => {
        setState(prev => ({ ...prev, wsConnected: false }));
      });

      ws.on('pong', ({ latency }) => {
        setState(prev => ({ ...prev, wsLatency: latency }));
      });

      ws.on('messageReceived', (message) => {
        setState(prev => ({
          ...prev,
          wsMessages: [...prev.wsMessages.slice(-9), JSON.stringify(message)],
        }));
      });

      setWsManager(ws);

      // 更新缓存统计
      updateCacheStats();

      // 设置定时更新
      const interval = setInterval(() => {
        updateCacheStats();
        updateOfflineStats();
      }, 5000);

      return () => clearInterval(interval);
    } catch (error) {
      console.error('初始化服务失败:', error);
      Alert.alert('错误', '初始化服务失败');
    }
  };

  /**
   * 清理资源
   */
  const cleanup = useCallback( () => {, []);
    if (wsManager) {
      wsManager.destroy();
    }
    offlineManager.removeAllListeners();
  };

  /**
   * 更新离线统计
   */
  const updateOfflineStats = useCallback( () => {, []);
    const stats = offlineManager.getOperationStats();
    const conflicts = offlineManager.getConflicts();
    setState(prev => ({
      ...prev,
      operationCount: stats.total,
      conflictCount: conflicts.length,
    }));
  };

  /**
   * 更新缓存统计
   */
  const updateCacheStats = useCallback( () => {, []);
    setState(prev => ({
      ...prev,
      cacheStats: {
        memory: memoryCache.getStats(),
        persistent: persistentCache.getStats(),
        api: apiCache.getStats(),
      },
    }));
  };

  /**
   * 测试GraphQL查询
   */
  const testGraphQLQuery = async () => {
    setState(prev => ({ ...prev, graphqlLoading: true }));
    
    try {
      const response = await graphqlClient.query(testData.graphqlQuery);
      setState(prev => ({
        ...prev,
        graphqlResult: JSON.stringify(response, null, 2),
        graphqlConnected: true,
      }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        graphqlResult: `错误: ${error}`,
        graphqlConnected: false,
      }));
    } finally {
      setState(prev => ({ ...prev, graphqlLoading: false }));
    }
  };

  /**
   * 测试GraphQL变更
   */
  const testGraphQLMutation = async () => {
    const mutation = `
      mutation CreateUser($input: CreateUserInput!) {
        createUser(input: $input) {
          id
          name
          email
        }
      }
    `;
    
    const variables = {
      input: {
        name: '测试用户',
        email: 'test@example.com',
      },
    };

    try {
      const response = await graphqlClient.mutate(mutation, variables);
      setState(prev => ({
        ...prev,
        graphqlResult: JSON.stringify(response, null, 2),
      }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        graphqlResult: `变更错误: ${error}`,
      }));
    }
  };

  /**
   * 添加离线操作
   */
  const addOfflineOperation = async () => {
    try {
      await offlineManager.addOperation(
        'create',
        'User',
        {
          name: '离线用户',
          email: 'offline@example.com',
        },
        1 // 高优先级
      );
      updateOfflineStats();
      Alert.alert('成功', '离线操作已添加');
    } catch (error) {
      Alert.alert('错误', `添加离线操作失败: ${error}`);
    }
  };

  /**
   * 手动同步
   */
  const manualSync = async () => {
    try {
      await offlineManager.sync();
      Alert.alert('成功', '同步完成');
    } catch (error) {
      Alert.alert('错误', `同步失败: ${error}`);
    }
  };

  /**
   * 连接WebSocket
   */
  const connectWebSocket = async () => {
    if (wsManager) {
      try {
        await wsManager.connect();
      } catch (error) {
        Alert.alert('错误', `WebSocket连接失败: ${error}`);
      }
    }
  };

  /**
   * 断开WebSocket
   */
  const disconnectWebSocket = useCallback( () => {, []);
    if (wsManager) {
      wsManager.disconnect();
    }
  };

  /**
   * 发送WebSocket消息
   */
  const sendWebSocketMessage = useCallback( () => {, []);
    if (wsManager && state.wsConnected) {
      wsManager.send({
        type: 'data',
        data: { message: testData.wsMessage },
      });
    } else {
      Alert.alert('错误', 'WebSocket未连接');
    }
  };

  /**
   * 订阅WebSocket频道
   */
  const subscribeChannel = useCallback( () => {, []);
    if (wsManager) {
      wsManager.subscribe({
        channel: 'test-channel',
        onMessage: (message) => {
          console.log('收到频道消息:', message);
        },
        onError: (error) => {
          console.error('频道错误:', error);
        },
      });
      Alert.alert('成功', '已订阅测试频道');
    }
  };

  /**
   * 测试缓存设置
   */
  const testCacheSet = async () => {
    try {
      await memoryCache.set(testData.cacheKey, testData.cacheValue);
      await persistentCache.set(testData.cacheKey, testData.cacheValue);
      await apiCache.set(testData.cacheKey, testData.cacheValue);
      updateCacheStats();
      Alert.alert('成功', '缓存设置完成');
    } catch (error) {
      Alert.alert('错误', `缓存设置失败: ${error}`);
    }
  };

  /**
   * 测试缓存获取
   */
  const testCacheGet = async () => {
    try {
      const memoryValue = await memoryCache.get(testData.cacheKey);
      const persistentValue = await persistentCache.get(testData.cacheKey);
      const apiValue = await apiCache.get(testData.cacheKey);
      
      Alert.alert('缓存值', `
内存缓存: ${memoryValue}
持久缓存: ${persistentValue}
API缓存: ${apiValue}
      `);
    } catch (error) {
      Alert.alert('错误', `缓存获取失败: ${error}`);
    }
  };

  /**
   * 清空缓存
   */
  const clearCaches = async () => {
    try {
      await memoryCache.clear();
      await persistentCache.clear();
      await apiCache.clear();
      updateCacheStats();
      Alert.alert('成功', '所有缓存已清空');
    } catch (error) {
      Alert.alert('错误', `清空缓存失败: ${error}`);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>高级功能演示</Text>

      {/* GraphQL API 部分 */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>GraphQL API</Text>
        <View style={styles.statusRow}>
          <Text>连接状态: </Text>
          <Text style={[styles.status, { color: state.graphqlConnected ? 'green' : 'red' }]}>
            {state.graphqlConnected ? '已连接' : '未连接'}
          </Text>
        </View>
        
        <TextInput
          style={styles.textInput}
          multiline
          value={testData.graphqlQuery}
          onChangeText={(text) => setTestData(prev => ({ ...prev, graphqlQuery: text }))}
          placeholder="输入GraphQL查询"
        />
        
        <View style={styles.buttonRow}>
          <TouchableOpacity
            style={[styles.button, state.graphqlLoading && styles.buttonDisabled]}
            onPress={testGraphQLQuery}
            disabled={state.graphqlLoading}
          >
            <Text style={styles.buttonText}>
              {state.graphqlLoading ? '查询中...' : '执行查询'}
            </Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.button} onPress={testGraphQLMutation}>
            <Text style={styles.buttonText}>测试变更</Text>
          </TouchableOpacity>
        </View>
        
        {state.graphqlResult ? (
          <Text style={styles.result}>{state.graphqlResult}</Text>
        ) : null}
      </View>

      {/* 离线模式部分 */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>离线模式</Text>
        <View style={styles.statusRow}>
          <Text>初始化状态: </Text>
          <Text style={[styles.status, { color: state.offlineInitialized ? 'green' : 'red' }]}>
            {state.offlineInitialized ? '已初始化' : '未初始化'}
          </Text>
        </View>
        
        <View style={styles.statusRow}>
          <Text>同步状态: </Text>
          <Text style={styles.status}>{state.syncStatus}</Text>
        </View>
        
        <View style={styles.statusRow}>
          <Text>待同步操作: </Text>
          <Text style={styles.status}>{state.operationCount}</Text>
        </View>
        
        <View style={styles.statusRow}>
          <Text>冲突数量: </Text>
          <Text style={styles.status}>{state.conflictCount}</Text>
        </View>
        
        <View style={styles.buttonRow}>
          <TouchableOpacity style={styles.button} onPress={addOfflineOperation}>
            <Text style={styles.buttonText}>添加离线操作</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.button} onPress={manualSync}>
            <Text style={styles.buttonText}>手动同步</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* WebSocket部分 */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>WebSocket实时通信</Text>
        <View style={styles.statusRow}>
          <Text>连接状态: </Text>
          <Text style={[styles.status, { color: state.wsConnected ? 'green' : 'red' }]}>
            {state.wsConnected ? '已连接' : '未连接'}
          </Text>
        </View>
        
        <View style={styles.statusRow}>
          <Text>延迟: </Text>
          <Text style={styles.status}>{state.wsLatency}ms</Text>
        </View>
        
        <TextInput
          style={styles.textInput}
          value={testData.wsMessage}
          onChangeText={(text) => setTestData(prev => ({ ...prev, wsMessage: text }))}
          placeholder="输入WebSocket消息"
        />
        
        <View style={styles.buttonRow}>
          <TouchableOpacity
            style={[styles.button, state.wsConnected && styles.buttonDisabled]}
            onPress={connectWebSocket}
            disabled={state.wsConnected}
          >
            <Text style={styles.buttonText}>连接</Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={[styles.button, !state.wsConnected && styles.buttonDisabled]}
            onPress={disconnectWebSocket}
            disabled={!state.wsConnected}
          >
            <Text style={styles.buttonText}>断开</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.button} onPress={sendWebSocketMessage}>
            <Text style={styles.buttonText}>发送消息</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.button} onPress={subscribeChannel}>
            <Text style={styles.buttonText}>订阅频道</Text>
          </TouchableOpacity>
        </View>
        
        <Text style={styles.subTitle}>最近消息:</Text>
        {state.wsMessages.map((message, index) => (
          <Text key={index} style={styles.message}>
            {message}
          </Text>
        ))}
      </View>

      {/* 缓存策略部分 */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>缓存策略</Text>
        
        <View style={styles.inputRow}>
          <TextInput
            style={[styles.textInput, { flex: 1, marginRight: 10 }]}
            value={testData.cacheKey}
            onChangeText={(text) => setTestData(prev => ({ ...prev, cacheKey: text }))}
            placeholder="缓存键"
          />
          <TextInput
            style={[styles.textInput, { flex: 1 }]}
            value={testData.cacheValue}
            onChangeText={(text) => setTestData(prev => ({ ...prev, cacheValue: text }))}
            placeholder="缓存值"
          />
        </View>
        
        <View style={styles.buttonRow}>
          <TouchableOpacity style={styles.button} onPress={testCacheSet}>
            <Text style={styles.buttonText}>设置缓存</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.button} onPress={testCacheGet}>
            <Text style={styles.buttonText}>获取缓存</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.button} onPress={clearCaches}>
            <Text style={styles.buttonText}>清空缓存</Text>
          </TouchableOpacity>
        </View>
        
        <Text style={styles.subTitle}>缓存统计:</Text>
        <Text style={styles.cacheStats}>
          内存缓存: {state.cacheStats.memory.size || 0} 项, 命中率: {((state.cacheStats.memory.hitRate || 0) * 100).toFixed(1)}%
        </Text>
        <Text style={styles.cacheStats}>
          持久缓存: {state.cacheStats.persistent.size || 0} 项, 命中率: {((state.cacheStats.persistent.hitRate || 0) * 100).toFixed(1)}%
        </Text>
        <Text style={styles.cacheStats}>
          API缓存: {state.cacheStats.api.size || 0} 项, 命中率: {((state.cacheStats.api.hitRate || 0) * 100).toFixed(1)}%
        </Text>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 20,
    color: '#333',
  },
  section: {
    backgroundColor: 'white',
    borderRadius: 8,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 12,
    color: '#333',
  },
  subTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginTop: 12,
    marginBottom: 8,
    color: '#555',
  },
  statusRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  status: {
    fontWeight: '600',
  },
  textInput: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 4,
    padding: 12,
    marginBottom: 12,
    backgroundColor: '#fff',
    minHeight: 40,
  },
  inputRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  buttonRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginBottom: 12,
  },
  button: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 4,
    minWidth: 80,
  },
  buttonDisabled: {
    backgroundColor: '#ccc',
  },
  buttonText: {
    color: 'white',
    fontWeight: '600',
    textAlign: 'center',
    fontSize: 14,
  },
  result: {
    backgroundColor: '#f8f8f8',
    padding: 12,
    borderRadius: 4,
    fontFamily: 'monospace',
    fontSize: 12,
    maxHeight: 200,
  },
  message: {
    backgroundColor: '#f0f0f0',
    padding: 8,
    borderRadius: 4,
    marginBottom: 4,
    fontSize: 12,
    fontFamily: 'monospace',
  },
  cacheStats: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
  },
});

export default React.memo(AdvancedFeaturesDemo); 