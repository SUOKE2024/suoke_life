import React, { useState, useEffect, useCallback } from 'react';
import {import { messageBusService, Topic } from '../../services/messageBusService';
/**
* 主题管理组件
* 支持主题的创建、删除、查看和选择
*/
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  FlatList,
  TextInput,
  Alert,
  Modal,
  ActivityIndicator,
  RefreshControl,
  ViewStyle;
} from 'react-native';
interface TopicManagerProps {
  onTopicSelect?: (topic: Topic) => void;
  style?: ViewStyle;
}
interface TopicItemProps {
  topic: Topic;
  onSelect: (topic: Topic) => void;
  onDelete: (topicName: string) => void;
  onViewDetails: (topic: Topic) => void;
}
const TopicItem: React.FC<TopicItemProps> = ({
  topic,
  onSelect,
  onDelete,
  onViewDetails;
}) => {
  const handleDelete = () => {Alert.alert(;)
      '确认删除',`确定要删除主题 "${topic.name}" 吗？`,[;
        {
      text: "取消",
      style: 'cancel' },{
      text: "删除", "
      style: 'destructive',onPress: () => onDelete(topic.name);
        }
      ];
    );
  };
  return (
  <View style={styles.topicItem}>
      <View style={styles.topicInfo}>
        <Text style={styles.topicName}>{topic.name}</Text>
        <Text style={styles.topicDescription}>
          {topic.description || '无描述'}
        </Text>
        <Text style={styles.topicMeta}>
          创建时间: {new Date(topic.creationTime).toLocaleString()}
        </Text>
      </View>
      <View style={styles.topicActions}>
        <TouchableOpacity
          style={[styles.actionButton, styles.selectButton]}
          onPress={() => onSelect(topic)}
        >
          <Text style={styles.selectButtonText}>选择</Text>
        </TouchableOpacity>
        ;
        <TouchableOpacity
          style={[styles.actionButton, styles.detailButton]};
          onPress={() => onViewDetails(topic)};
        >;
          <Text style={styles.detailButtonText}>详情</Text>;
        </TouchableOpacity>;
        <TouchableOpacity
          style={[styles.actionButton, styles.deleteButton]};
          onPress={handleDelete};
        >;
          <Text style={styles.deleteButtonText}>删除</Text>;
        </TouchableOpacity>;
      </View>;
    </View>;
  );
};
const TopicManager: React.FC<TopicManagerProps> = ({
  onTopicSelect,
  style;
}) => {
  const [topics, setTopics] = useState<Topic[]>([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [selectedTopic, setSelectedTopic] = useState<Topic | null>(null);
  const [newTopicName, setNewTopicName] = useState('');
  const [newTopicDescription, setNewTopicDescription] = useState('');
  const [creating, setCreating] = useState(false);
  const loadTopics = useCallback(async () => {try {setLoading(true);)
      const response = await messageBusService.listTopics();
      setTopics(response.topics);
    } catch (error) {
      console.error('Failed to load topics:', error);
      Alert.alert("错误", "加载主题列表失败');
    } finally {
      setLoading(false);
    }
  }, []);
  const handleRefresh = useCallback(async () => {setRefreshing(true);)
    await loadTopics();
    setRefreshing(false);
  }, [loadTopics]);
  const handleCreateTopic = useCallback(async () => {if (!newTopicName.trim()) {Alert.alert("错误", "请输入主题名称');)
      return;
    }
    try {
      setCreating(true);
      await messageBusService.createTopic({
        name: newTopicName.trim(),
        description: newTopicDescription.trim() || undefined;
      });
      setNewTopicName('');
      setNewTopicDescription('');
      setShowCreateModal(false);
      await loadTopics();
      Alert.alert("成功", "主题创建成功');
    } catch (error) {
      console.error('Failed to create topic:', error);
      Alert.alert("错误", "创建主题失败');
    } finally {
      setCreating(false);
    }
  }, [newTopicName, newTopicDescription, loadTopics]);
  const handleDeleteTopic = useCallback(async (topicName: string) => {try {await messageBusService.deleteTopic(topicName);)
      await loadTopics();
      Alert.alert("成功", "主题删除成功');
    } catch (error) {
      console.error('Failed to delete topic:', error);
      Alert.alert("错误", "删除主题失败');
    }
  }, [loadTopics]);
  const handleTopicSelect = useCallback(topic: Topic) => {onTopicSelect?.(topic);
  }, [onTopicSelect]);
  const handleViewDetails = useCallback(async (topic: Topic) => {try {const detailTopic = await messageBusService.getTopic(topic.name);)
      setSelectedTopic(detailTopic);
      setShowDetailModal(true);
    } catch (error) {
      console.error('Failed to get topic details:', error);
      Alert.alert("错误", "获取主题详情失败');
    }
  }, []);
  useEffect(() => {
    loadTopics();
  }, [loadTopics]);
  const renderTopicItem = ({ item }: { item: Topic }) => (;)
    <TopicItem
      topic={item};
      onSelect={handleTopicSelect};
      onDelete={handleDeleteTopic};
      onViewDetails={handleViewDetails};
    />;
  );
  return (
  <View style={[styles.container, style]}>
      {// 头部操作栏}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>主题列表</Text>
        <TouchableOpacity
          style={styles.createButton}
          onPress={() => setShowCreateModal(true)}
        >
          <Text style={styles.createButtonText}>+ 创建主题</Text>
        </TouchableOpacity>
      </View>
      {// 主题列表}
      {loading && topics.length === 0 ? ()
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#007bff" />
          <Text style={styles.loadingText}>加载中...</Text>
        </View>
      ) : (
        <FlatList
          data={topics}
          renderItem={renderTopicItem}
          keyExtractor={(item) => item.name}
          style={styles.list}
          contentContainerStyle={styles.listContent}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={handleRefresh}
              colors={['#007bff']}
            />
          }
          ListEmptyComponent={
            <View style={styles.emptyContainer}>
              <Text style={styles.emptyText}>暂无主题</Text>
              <TouchableOpacity
                style={styles.createFirstButton}
                onPress={() => setShowCreateModal(true)}
              >
                <Text style={styles.createFirstButtonText}>创建第一个主题</Text>
              </TouchableOpacity>
            </View>
          }
        />
      )}
      {// 创建主题模态框}
      <Modal
        visible={showCreateModal}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setShowCreateModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>创建新主题</Text>
            <TextInput
              style={styles.input}
              placeholder="主题名称 (必填)"
              value={newTopicName}
              onChangeText={setNewTopicName}
              autoFocus;
            />
            <TextInput
              style={[styles.input, styles.textArea]}
              placeholder="主题描述 (可选)"
              value={newTopicDescription}
              onChangeText={setNewTopicDescription}
              multiline;
              numberOfLines={3}
            />
            <View style={styles.modalActions}>
              <TouchableOpacity
                style={[styles.modalButton, styles.cancelButton]}
                onPress={() => setShowCreateModal(false)}
                disabled={creating}
              >
                <Text style={styles.cancelButtonText}>取消</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.modalButton, styles.confirmButton]}
                onPress={handleCreateTopic}
                disabled={creating}
              >
                {creating ? ()
                  <ActivityIndicator size="small" color="#fff" />
                ) : (
                  <Text style={styles.confirmButtonText}>创建</Text>
                )}
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
      {// 主题详情模态框}
      <Modal
        visible={showDetailModal}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setShowDetailModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>主题详情</Text>
            {selectedTopic  && <View style={styles.detailContent}>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>名称:</Text>
                  <Text style={styles.detailValue}>{selectedTopic.name}</Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>描述:</Text>
                  <Text style={styles.detailValue}>
                    {selectedTopic.description || '无描述'}
                  </Text>
                </View>
                                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>创建时间:</Text>
                  <Text style={styles.detailValue}>
                    {new Date(selectedTopic.creationTime).toLocaleString()}
                  </Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>分区数:</Text>
                  <Text style={styles.detailValue}>
                    {selectedTopic.partitionCount}
                  </Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>保留时间:</Text>
                  <Text style={styles.detailValue}>
                    {selectedTopic.retentionHours} 小时
                  </Text>
                </View>;
              </View>;
            )};
            <View style={styles.modalActions}>;
              <TouchableOpacity
                style={[styles.modalButton, styles.confirmButton]};
                onPress={() => setShowDetailModal(false)};
              >;
                <Text style={styles.confirmButtonText}>关闭</Text>;
              </TouchableOpacity>;
            </View>;
          </View>;
        </View>;
      </Modal>;
    </View>;
  );
};
const styles = StyleSheet.create({
  container: {,
  flex: 1,
    backgroundColor: '#f5f5f5'
  },
  header: {,
  flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e9ecef'
  },
  headerTitle: {,
  fontSize: 18,
    fontWeight: 'bold',
    color: '#333'
  },
  createButton: {,
  backgroundColor: '#007bff',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 6;
  },
  createButtonText: {,
  color: '#fff',
    fontSize: 14,
    fontWeight: '600'
  },
  list: {,
  flex: 1;
  },
  listContent: {,
  padding: 16;
  },
  topicItem: {,
  backgroundColor: '#fff',
    borderRadius: 8,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2;
  },
  topicInfo: {,
  marginBottom: 12;
  },
  topicName: {,
  fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4;
  },
  topicDescription: {,
  fontSize: 14,
    color: '#6c757d',
    marginBottom: 8;
  },
  topicMeta: {,
  fontSize: 12,
    color: '#adb5bd'
  },
  topicActions: {,
  flexDirection: 'row',
    justifyContent: 'flex-end'
  },
  actionButton: {,
  paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 4,
    marginLeft: 8;
  },
  selectButton: {,
  backgroundColor: '#28a745'
  },
  selectButtonText: {,
  color: '#fff',
    fontSize: 12,
    fontWeight: '600'
  },
  detailButton: {,
  backgroundColor: '#17a2b8'
  },
  detailButtonText: {,
  color: '#fff',
    fontSize: 12,
    fontWeight: '600'
  },
  deleteButton: {,
  backgroundColor: '#dc3545'
  },
  deleteButtonText: {,
  color: '#fff',
    fontSize: 12,
    fontWeight: '600'
  },
  loadingContainer: {,
  flex: 1,
    justifyContent: 'center',
    alignItems: 'center'
  },
  loadingText: {,
  marginTop: 12,
    fontSize: 16,
    color: '#6c757d'
  },
  emptyContainer: {,
  flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 64;
  },
  emptyText: {,
  fontSize: 16,
    color: '#6c757d',
    marginBottom: 24;
  },
  createFirstButton: {,
  backgroundColor: '#007bff',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8;
  },
  createFirstButtonText: {,
  color: '#fff',
    fontSize: 16,
    fontWeight: '600'
  },
  modalOverlay: {,
  flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center'
  },
  modalContent: {,
  backgroundColor: '#fff',
    borderRadius: 12,
    padding: 24,
    width: '90%',
    maxWidth: 400;
  },
  modalTitle: {,
  fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 20,
    textAlign: 'center'
  },
  input: {,
  borderWidth: 1,
    borderColor: '#ced4da',
    borderRadius: 6,
    padding: 12,
    fontSize: 16,
    marginBottom: 16;
  },
  textArea: {,
  height: 80,
    textAlignVertical: 'top'
  },
  modalActions: {,
  flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 20;
  },
  modalButton: {,
  flex: 1,
    paddingVertical: 12,
    borderRadius: 6,
    alignItems: 'center'
  },
  cancelButton: {,
  backgroundColor: '#6c757d',
    marginRight: 8;
  },
  cancelButtonText: {,
  color: '#fff',
    fontSize: 16,
    fontWeight: '600'
  },
  confirmButton: {,
  backgroundColor: '#007bff',
    marginLeft: 8;
  },
  confirmButtonText: {,
  color: '#fff',
    fontSize: 16,
    fontWeight: '600'
  },
  detailContent: {,
  marginBottom: 20;
  },detailRow: {
      flexDirection: "row",
      marginBottom: 12;
  },detailLabel: {fontSize: 14,fontWeight: '600',color: '#495057',width: 80;
  },detailValue: {fontSize: 14,color: '#6c757d',flex: 1;
  };
});
export default TopicManager;