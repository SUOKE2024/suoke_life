import React, { useState } from 'react';
import { View, StyleSheet, TouchableOpacity, Text } from 'react-native';
import { BenchmarkDashboard } from '../../components/benchmark/BenchmarkDashboard';
import { BenchmarkCreator } from '../../components/benchmark/BenchmarkCreator';
import { BenchmarkResultDetail } from '../../components/benchmark/BenchmarkResultDetail';
import type { BenchmarkTask } from '../../services';

export const BenchmarkScreen: React.FC = () => {
  const [showCreator, setShowCreator] = useState(false);
  const [showResultDetail, setShowResultDetail] = useState(false);
  const [selectedTaskId, setSelectedTaskId] = useState<string | null>(null);

  // 处理任务选择
  const handleTaskSelect = (task: BenchmarkTask) => {
    if (task.status === 'completed' && task.results) {
      setSelectedTaskId(task.task_id);
      setShowResultDetail(true);
    }
  };

  // 处理创建任务成功
  const handleTaskCreated = (taskId: string) => {
    console.log('基准测试任务已创建:', taskId);
    // 可以在这里添加导航到任务详情或显示成功消息
  };

  return (
    <View style={styles.container}>
      {/* 主要内容 */}
      <BenchmarkDashboard onTaskSelect={handleTaskSelect} />

      {/* 浮动操作按钮 */}
      <TouchableOpacity
        style={styles.fab}
        onPress={() => setShowCreator(true)}
      >
        <Text style={styles.fabText}>+</Text>
      </TouchableOpacity>

      {/* 创建基准测试模态框 */}
      <BenchmarkCreator
        visible={showCreator}
        onClose={() => setShowCreator(false)}
        onSubmit={handleTaskCreated}
      />

      {/* 结果详情模态框 */}
      <BenchmarkResultDetail
        visible={showResultDetail}
        taskId={selectedTaskId}
        onClose={() => {
          setShowResultDetail(false);
          setSelectedTaskId(null);
        }}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  fab: {
    position: 'absolute',
    bottom: 24,
    right: 24,
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: '#2196F3',
    justifyContent: 'center',
    alignItems: 'center',
    elevation: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
  },
  fabText: {
    fontSize: 24,
    color: '#fff',
    fontWeight: 'bold',
  },
}); 