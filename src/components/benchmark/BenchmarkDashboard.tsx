import React, { useEffect, useState, useCallback } from 'react';
import { View, Text, StyleSheet, ScrollView, RefreshControl, Alert } from 'react-native';
import { benchmarkService, benchmarkStreamingService } from '../../services';
import type { BenchmarkTask, HealthStatus, StreamEvent } from '../../services';

interface BenchmarkDashboardProps {
  onTaskSelect?: (task: BenchmarkTask) => void;
}

export const BenchmarkDashboard: React.FC<BenchmarkDashboardProps> = ({ onTaskSelect }) => {
  const [tasks, setTasks] = useState<BenchmarkTask[]>([]);
  const [healthStatus, setHealthStatus] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('CLOSED');

  // 加载基准测试任务
  const loadBenchmarkTasks = useCallback(async () => {
    try {
      const taskList = await benchmarkService.listBenchmarks();
      setTasks(taskList);
    } catch (error) {
      console.error('Failed to load benchmark tasks:', error);
      Alert.alert('错误', '加载基准测试任务失败');
    }
  }, []);

  // 加载服务健康状态
  const loadHealthStatus = useCallback(async () => {
    try {
      const status = await benchmarkService.getHealthStatus();
      setHealthStatus(status);
    } catch (error) {
      console.error('Failed to load health status:', error);
    }
  }, []);

  // 初始化数据加载
  const initializeData = useCallback(async () => {
    setLoading(true);
    try {
      await Promise.all([
        loadBenchmarkTasks(),
        loadHealthStatus()
      ]);
    } finally {
      setLoading(false);
    }
  }, [loadBenchmarkTasks, loadHealthStatus]);

  // 下拉刷新
  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    try {
      await initializeData();
    } finally {
      setRefreshing(false);
    }
  }, [initializeData]);

  // WebSocket事件处理
  const handleStreamEvent = useCallback((event: StreamEvent) => {
    switch (event.type) {
      case 'benchmark_progress':
        // 更新任务进度
        setTasks(prevTasks => 
          prevTasks.map(task => 
            task.task_id === event.data.task_id 
              ? { ...task, progress: event.data.progress, status: 'running' }
              : task
          )
        );
        break;
      case 'benchmark_complete':
        // 任务完成，重新加载任务列表
        loadBenchmarkTasks();
        break;
      case 'benchmark_error':
        // 任务错误
        setTasks(prevTasks => 
          prevTasks.map(task => 
            task.task_id === event.data.task_id 
              ? { ...task, status: 'failed', error_message: event.data.error }
              : task
          )
        );
        break;
      case 'system_status':
        // 系统状态更新
        setHealthStatus(event.data);
        break;
    }
  }, [loadBenchmarkTasks]);

  // 初始化WebSocket连接
  const initializeWebSocket = useCallback(async () => {
    try {
      await benchmarkStreamingService.connect();
      setConnectionStatus(benchmarkStreamingService.getConnectionState());
      
      // 订阅事件
      benchmarkStreamingService.subscribeToEvents([
        'benchmark_progress',
        'benchmark_complete',
        'benchmark_error',
        'system_status'
      ]);
      
      // 添加事件监听器
      benchmarkStreamingService.addEventListener('*', handleStreamEvent);
      
      // 启动心跳检测
      benchmarkStreamingService.startHeartbeat();
    } catch (error) {
      console.error('WebSocket连接失败:', error);
    }
  }, [handleStreamEvent]);

  // 组件挂载时初始化
  useEffect(() => {
    initializeData();
    initializeWebSocket();

    // 定期更新连接状态
    const statusInterval = setInterval(() => {
      setConnectionStatus(benchmarkStreamingService.getConnectionState());
    }, 5000);

    // 清理函数
    return () => {
      clearInterval(statusInterval);
      benchmarkStreamingService.removeEventListener('*', handleStreamEvent);
      benchmarkStreamingService.disconnect();
    };
  }, [initializeData, initializeWebSocket, handleStreamEvent]);

  // 获取状态颜色
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return '#4CAF50';
      case 'running':
        return '#2196F3';
      case 'failed':
        return '#F44336';
      case 'pending':
        return '#FF9800';
      default:
        return '#9E9E9E';
    }
  };

  // 获取状态文本
  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed':
        return '已完成';
      case 'running':
        return '运行中';
      case 'failed':
        return '失败';
      case 'pending':
        return '等待中';
      default:
        return '未知';
    }
  };

  // 渲染健康状态
  const renderHealthStatus = () => {
    if (!healthStatus) return null;

    return (
      <View style={styles.healthStatusContainer}>
        <Text style={styles.sectionTitle}>服务状态</Text>
        <View style={styles.healthStatusCard}>
          <View style={styles.statusRow}>
            <Text style={styles.statusLabel}>服务状态:</Text>
            <Text style={[
              styles.statusValue,
              { color: healthStatus.status === 'healthy' ? '#4CAF50' : '#F44336' }
            ]}>
              {healthStatus.status === 'healthy' ? '健康' : '异常'}
            </Text>
          </View>
          <View style={styles.statusRow}>
            <Text style={styles.statusLabel}>版本:</Text>
            <Text style={styles.statusValue}>{healthStatus.version}</Text>
          </View>
          <View style={styles.statusRow}>
            <Text style={styles.statusLabel}>运行时间:</Text>
            <Text style={styles.statusValue}>{Math.floor(healthStatus.uptime / 3600)}小时</Text>
          </View>
          <View style={styles.statusRow}>
            <Text style={styles.statusLabel}>WebSocket:</Text>
            <Text style={[
              styles.statusValue,
              { color: connectionStatus === 'OPEN' ? '#4CAF50' : '#F44336' }
            ]}>
              {connectionStatus === 'OPEN' ? '已连接' : '未连接'}
            </Text>
          </View>
        </View>
      </View>
    );
  };

  // 渲染任务列表
  const renderTaskList = () => {
    if (tasks.length === 0) {
      return (
        <View style={styles.emptyContainer}>
          <Text style={styles.emptyText}>暂无基准测试任务</Text>
        </View>
      );
    }

    return (
      <View style={styles.taskListContainer}>
        <Text style={styles.sectionTitle}>基准测试任务</Text>
        {tasks.map((task) => (
          <View key={task.task_id} style={styles.taskCard}>
            <View style={styles.taskHeader}>
              <Text style={styles.taskTitle}>{task.benchmark_id}</Text>
              <View style={[
                styles.statusBadge,
                { backgroundColor: getStatusColor(task.status) }
              ]}>
                <Text style={styles.statusBadgeText}>{getStatusText(task.status)}</Text>
              </View>
            </View>
            <Text style={styles.taskModel}>模型: {task.model_id} v{task.model_version}</Text>
            <Text style={styles.taskTime}>创建时间: {new Date(task.created_at).toLocaleString()}</Text>
            
            {task.status === 'running' && (
              <View style={styles.progressContainer}>
                <Text style={styles.progressText}>进度: {Math.round(task.progress * 100)}%</Text>
                <View style={styles.progressBar}>
                  <View style={[
                    styles.progressFill,
                    { width: `${task.progress * 100}%` }
                  ]} />
                </View>
              </View>
            )}
            
            {task.error_message && (
              <Text style={styles.errorText}>错误: {task.error_message}</Text>
            )}
          </View>
        ))}
      </View>
    );
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <Text style={styles.loadingText}>加载中...</Text>
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      {renderHealthStatus()}
      {renderTaskList()}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    fontSize: 16,
    color: '#666',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 12,
  },
  healthStatusContainer: {
    margin: 16,
  },
  healthStatusCard: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 16,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  statusRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  statusLabel: {
    fontSize: 14,
    color: '#666',
  },
  statusValue: {
    fontSize: 14,
    fontWeight: '500',
  },
  taskListContainer: {
    margin: 16,
    marginTop: 0,
  },
  taskCard: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 16,
    marginBottom: 12,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  taskHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  taskTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    flex: 1,
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusBadgeText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '500',
  },
  taskModel: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
  },
  taskTime: {
    fontSize: 12,
    color: '#999',
    marginBottom: 8,
  },
  progressContainer: {
    marginTop: 8,
  },
  progressText: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  progressBar: {
    height: 4,
    backgroundColor: '#e0e0e0',
    borderRadius: 2,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#2196F3',
  },
  errorText: {
    fontSize: 12,
    color: '#F44336',
    marginTop: 8,
  },
  emptyContainer: {
    alignItems: 'center',
    padding: 32,
  },
  emptyText: {
    fontSize: 16,
    color: '#999',
  },
}); 