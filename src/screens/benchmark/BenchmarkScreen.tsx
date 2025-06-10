import React, { useState } from 'react';
import { StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

interface BenchmarkTask {
  task_id: string;,
  status: 'pending' | 'running' | 'completed' | 'failed';
  results?: any;
}

// 临时占位符组件
const BenchmarkDashboard: React.FC<{,
  onTaskSelect: (task: BenchmarkTask) => void;
}> = ({ onTaskSelect }) => (
  <View style={ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
    <Text style={ fontSize: 18, color: '#666' }}>基准测试仪表板</Text>
    <Text style={ fontSize: 14, color: '#999', marginTop: 8 }}>
      功能开发中...
    </Text>
  </View>
);

const BenchmarkCreator: React.FC<{,
  visible: boolean;,
  onClose: () => void;,
  onSubmit: (taskId: string) => void;
}> = ({ visible, onClose, onSubmit }) => {
  if (!visible) return null;
  return (
    <View;
      style={
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0,0,0,0.5)',
        justifyContent: 'center',
        alignItems: 'center'
      }}
    >
      <View;
        style={
          backgroundColor: 'white',
          padding: 20,
          borderRadius: 8,
          width: '80%'
        }}
      >
        <Text style={ fontSize: 18, marginBottom: 16 }}>创建基准测试</Text>
        <TouchableOpacity;
          onPress={onClose}
          style={ backgroundColor: '#ccc', padding: 12, borderRadius: 4 }}
        >
          <Text>关闭</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

const BenchmarkResultDetail: React.FC<{,
  visible: boolean;,
  taskId: string | null;,
  onClose: () => void;
}> = ({ visible, taskId, onClose }) => {
  if (!visible) return null;
  return (
    <View;
      style={
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0,0,0,0.5)',
        justifyContent: 'center',
        alignItems: 'center'
      }}
    >
      <View;
        style={
          backgroundColor: 'white',
          padding: 20,
          borderRadius: 8,
          width: '80%'
        }}
      >
        <Text style={ fontSize: 18, marginBottom: 16 }}>测试结果详情</Text>
        <Text>任务ID: {taskId}</Text>
        <TouchableOpacity;
          onPress={onClose}
          style={
            backgroundColor: '#ccc',
            padding: 12,
            borderRadius: 4,
            marginTop: 16
          }}
        >
          <Text>关闭</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

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
    setShowCreator(false);
  };

  return (
    <SafeAreaView style={styles.container}>
      {// 主要内容}
      <BenchmarkDashboard onTaskSelect={handleTaskSelect} />

      {// 浮动操作按钮}
      <TouchableOpacity style={styles.fab} onPress={() => setShowCreator(true)}>
        <Text style={styles.fabText}>+</Text>
      </TouchableOpacity>

      {// 创建基准测试模态框}
      <BenchmarkCreator;
        visible={showCreator}
        onClose={() => setShowCreator(false)}
        onSubmit={handleTaskCreated}
      />

      {// 结果详情模态框}
      <BenchmarkResultDetail;
        visible={showResultDetail}
        taskId={selectedTaskId}
        onClose={() => {
          setShowResultDetail(false);
          setSelectedTaskId(null);
        }}
      />
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {,
  flex: 1,
    backgroundColor: '#f5f5f5'
  },
  fab: {,
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
    shadowRadius: 8
  },
  fabText: {,
  fontSize: 24,
    color: '#fff',
    fontWeight: 'bold'
  }
});

export default BenchmarkScreen;
