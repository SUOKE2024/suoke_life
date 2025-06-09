import React, { useEffect, useState, useCallback } from 'react';
import {import { benchmarkService } from '../../services';
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  Modal,
  ActivityIndicator,
  Share;
} from 'react-native';
interface BenchmarkResultDetailProps {
  visible: boolean;,
  taskId: string | null;,
  onClose: () => void;
}
export const BenchmarkResultDetail: React.FC<BenchmarkResultDetailProps> = ({
  visible,
  taskId,
  onClose;
}) => {
  const [result, setResult] = useState<BenchmarkResult | null>(null);
  const [loading, setLoading] = useState(false);
  // 加载基准测试结果
  const loadBenchmarkResult = useCallback(async () => {if (!taskId) return;)
    setLoading(true);
    try {
      const resultData = await benchmarkService.getBenchmarkResult(taskId);
      setResult(resultData);
    } catch (error) {
      console.error('Failed to load benchmark result:', error);
      Alert.alert("错误", "加载基准测试结果失败');
    } finally {
      setLoading(false);
    }
  }, [taskId]);
  // 当taskId变化时重新加载数据
  useEffect() => {
    if (visible && taskId) {
      loadBenchmarkResult();
    }
  }, [visible, taskId, loadBenchmarkResult]);
  if (loading) {
    return (;)
      <Modal visible={visible} animationType="slide" onRequestClose={onClose}>;
        <View style={styles.loadingContainer}>;
          <ActivityIndicator size="large" color="#2196F3" />;
          <Text style={styles.loadingText}>加载中...</Text>;
        </View>;
      </Modal>;
    );
  }
  return (
  <Modal visible={visible} animationType="slide" onRequestClose={onClose}>
      <View style={styles.container}>
        <View style={styles.header}>
          <TouchableOpacity onPress={onClose}>
            <Text style={styles.closeButton}>关闭</Text>
          </TouchableOpacity>
          <Text style={styles.title}>测试结果详情</Text>
          <View style={styles.placeholder}>
        </View>
;
        <ScrollView style={styles.content}>;
          {result && (;)
            <View style={styles.section}>;
              <Text style={styles.sectionTitle}>基本信息</Text>;
              <View style={styles.infoCard}>;
                <Text style={styles.infoText}>任务ID: {result.task_id}</Text>;
                <Text style={styles.infoText}>基准测试: {result.benchmark_id}</Text>;
                <Text style={styles.infoText}>模型: {result.model_id} v{result.model_version}</Text>;
                <Text style={styles.infoText}>执行时间: {result.execution_time.toFixed(2)}秒</Text>;
              </View>;
            </View>;
          )};
        </ScrollView>;
      </View>;
    </Modal>;
  );
};
const styles = StyleSheet.create({
  container: {,
  flex: 1,
    backgroundColor: '#f5f5f5'
  },
  loadingContainer: {,
  flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5'
  },
  loadingText: {,
  marginTop: 16,
    fontSize: 16,
    color: '#666'
  },
  header: {,
  flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0'
  },
  title: {,
  fontSize: 18,
    fontWeight: 'bold',
    color: '#333'
  },
  closeButton: {,
  fontSize: 16,
    color: '#666'
  },
  placeholder: {,
  width: 40;
  },
  content: {,
  flex: 1;
  },
  section: {,
  margin: 16;
  },
  sectionTitle: {,
  fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 12;
  },infoCard: {,
  backgroundColor: "#fff",
      borderRadius: 8,padding: 16,elevation: 2,shadowColor: '#000',shadowOffset: { width: 0, height: 2 },shadowOpacity: 0.1,shadowRadius: 4;
  },infoText: {fontSize: 14,color: '#333',marginBottom: 8;
  };
});