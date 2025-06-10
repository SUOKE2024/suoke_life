import React, { useState, useEffect, useCallback } from "react";";
import {import { messageBusService, Topic } from "../../services/messageBusService";""/;"/g"/;
/* 择 *//;/g/;
*//;,/g/;
View,;
Text,;
StyleSheet,;
TouchableOpacity,;
FlatList,;
TextInput,;
Alert,;
Modal,;
ActivityIndicator,;
RefreshControl,";,"";
ViewStyle;';'';
} from "react-native";";
interface TopicManagerProps {onTopicSelect?: (topic: Topic) => void;}}
}
  style?: ViewStyle;}
}
interface TopicItemProps {topic: Topic}onSelect: (topic: Topic) => void,;
onDelete: (topicName: string) => void,;
}
}
  onViewDetails: (topic: Topic) => void;}
}
const  TopicItem: React.FC<TopicItemProps> = ({)topic}onSelect,);
onDelete,);
}
  onViewDetails;)}
}) => {const handleDelete = () => {Alert.alert(;);}        {';}}'';
'}'';
style: 'cancel' ;},{';}';'';
}
      style: 'destructive',onPress: () => onDelete(topic.name);'}'';'';
        }
      ];
    );
  };
return (<View style={styles.topicItem}>;)      <View style={styles.topicInfo}>;
        <Text style={styles.topicName}>{topic.name}</Text>/;/g/;
        <Text style={styles.topicDescription}>;

        </Text>/;/g/;
        <Text style={styles.topicMeta}>;

        </Text>/;/g/;
      </View>/;/g/;
      <View style={styles.topicActions}>);
        <TouchableOpacity;)  />/;,/g/;
style={[styles.actionButton, styles.selectButton]});
onPress={() => onSelect(topic)}
        >;
          <Text style={styles.selectButtonText}>选择</Text>/;/g/;
        </TouchableOpacity>/;/g/;
        ;
        <TouchableOpacity;  />/;,/g/;
style={[styles.actionButton, styles.detailButton]};
onPress={() => onViewDetails(topic)};
        >;
          <Text style={styles.detailButtonText}>详情</Text>;/;/g/;
        </TouchableOpacity>;/;/g/;
        <TouchableOpacity;  />/;,/g/;
style={[styles.actionButton, styles.deleteButton]};
onPress={handleDelete};
        >;
          <Text style={styles.deleteButtonText}>删除</Text>;/;/g/;
        </TouchableOpacity>;/;/g/;
      </View>;/;/g/;
    </View>;/;/g/;
  );
};
const  TopicManager: React.FC<TopicManagerProps> = ({));,}onTopicSelect,);
}
  style;)}
}) => {const [topics, setTopics] = useState<Topic[]>([]);,}const [loading, setLoading] = useState(false);
const [refreshing, setRefreshing] = useState(false);
const [showCreateModal, setShowCreateModal] = useState(false);
const [showDetailModal, setShowDetailModal] = useState(false);';,'';
const [selectedTopic, setSelectedTopic] = useState<Topic | null>(null);';,'';
const [newTopicName, setNewTopicName] = useState(');'';
const [newTopicDescription, setNewTopicDescription] = useState(');'';
const [creating, setCreating] = useState(false);
const loadTopics = useCallback(async () => {try {setLoading(true););,}const response = await messageBusService.listTopics();
}
      setTopics(response.topics);}';'';
    } catch (error) {';,}console.error('Failed to load topics:', error);';'';
}
}
    } finally {}}
      setLoading(false);}
    }
  }, []);
const handleRefresh = useCallback(async () => {setRefreshing(true););,}const await = loadTopics();
}
    setRefreshing(false);}
  }, [loadTopics]);
return;
    }
    try {setCreating(true);,}const await = messageBusService.createTopic({);,}name: newTopicName.trim(),;
}
        const description = newTopicDescription.trim() || undefined;}';'';
      });';,'';
setNewTopicName(');'';
setNewTopicDescription(');'';
setShowCreateModal(false);
const await = loadTopics();
';'';
    } catch (error) {';,}console.error('Failed to create topic:', error);';'';
}
}
    } finally {}}
      setCreating(false);}
    }
  }, [newTopicName, newTopicDescription, loadTopics]);
const handleDeleteTopic = useCallback(async (topicName: string) => {try {await messageBusService.deleteTopic(topicName););,}const await = loadTopics();
}
}';'';
    } catch (error) {';,}console.error('Failed to delete topic:', error);';'';
}
}
    }
  }, [loadTopics]);
const handleTopicSelect = useCallback(topic: Topic) => {onTopicSelect?.(topic);}
  }, [onTopicSelect]);
const handleViewDetails = useCallback(async (topic: Topic) => {try {const detailTopic = await messageBusService.getTopic(topic.name););,}setSelectedTopic(detailTopic);
}
      setShowDetailModal(true);}';'';
    } catch (error) {';,}console.error('Failed to get topic details:', error);';'';
}
}
    }
  }, []);
useEffect() => {}}
    loadTopics();}
  }, [loadTopics]);
const renderTopicItem = ({ item }: { item: Topic ;}) => (;);
    <TopicItem;  />/;,/g/;
topic={item};
onSelect={handleTopicSelect};
onDelete={handleDeleteTopic};
onViewDetails={handleViewDetails};
    />;/;/g/;
  );
return (<View style={[styles.container, style]}>;)      {// 头部操作栏}/;/g/;
      <View style={styles.header}>;
        <Text style={styles.headerTitle}>主题列表</Text>)/;/g/;
        <TouchableOpacity;)  />/;,/g/;
style={styles.createButton});
onPress={() => setShowCreateModal(true)}
        >;
          <Text style={styles.createButtonText}>+ 创建主题</Text>/;/g/;
        </TouchableOpacity>/;/g/;
      </View>/;/g/;
      {// 主题列表}/;/g/;
      {loading && topics.length === 0 ? ()}';'';
        <View style={styles.loadingContainer}>';'';
          <ActivityIndicator size="large" color="#007bff"  />"/;"/g"/;
          <Text style={styles.loadingText}>加载中...</Text>/;/g/;
        </View>/;/g/;
      ) : (<FlatList removeClippedSubviews={true} maxToRenderPerBatch={10} windowSize={10};)  />/;,/g/;
data={topics});
renderItem={renderTopicItem});
keyExtractor={(item) => item.name}
          style={styles.list}
          contentContainerStyle={styles.listContent}
          refreshControl={}}
            <RefreshControl;}  />/;,/g/;
refreshing={refreshing}";,"";
onRefresh={handleRefresh}";,"";
colors={['#007bff']}';'';
            />/;/g/;
          }
          ListEmptyComponent={}
            <View style={styles.emptyContainer}>;
              <Text style={styles.emptyText}>暂无主题</Text>/;/g/;
              <TouchableOpacity;  />/;,/g/;
style={styles.createFirstButton}
                onPress={() => setShowCreateModal(true)}
              >;
                <Text style={styles.createFirstButtonText}>创建第一个主题</Text>/;/g/;
              </TouchableOpacity>/;/g/;
            </View>/;/g/;
          }
        />/;/g/;
      )}
      {// 创建主题模态框}/;/g/;
      <Modal;'  />/;,'/g'/;
visible={showCreateModal}';,'';
animationType="slide";
transparent={true}
        onRequestClose={() => setShowCreateModal(false)}
      >;
        <View style={styles.modalOverlay}>;
          <View style={styles.modalContent}>;
            <Text style={styles.modalTitle}>创建新主题</Text>/;/g/;
            <TextInput;  />/;,/g/;
style={styles.input}

              value={newTopicName}
              onChangeText={setNewTopicName}
              autoFocus;
            />/;/g/;
            <TextInput;  />/;,/g/;
style={[styles.input, styles.textArea]}

              value={newTopicDescription}
              onChangeText={setNewTopicDescription}
              multiline;
numberOfLines={3}
            />/;/g/;
            <View style={styles.modalActions}>;
              <TouchableOpacity;  />/;,/g/;
style={[styles.modalButton, styles.cancelButton]}
                onPress={() => setShowCreateModal(false)}
                disabled={creating}
              >;
                <Text style={styles.cancelButtonText}>取消</Text>/;/g/;
              </TouchableOpacity>/;/g/;
              <TouchableOpacity;  />/;,/g/;
style={[styles.modalButton, styles.confirmButton]}
                onPress={handleCreateTopic}
                disabled={creating}
              >";"";
                {creating ? ()";}}"";
                  <ActivityIndicator size="small" color="#fff"  />"}""/;"/g"/;
                ) : (<Text style={styles.confirmButtonText}>创建</Text>)/;/g/;
                )}
              </TouchableOpacity>/;/g/;
            </View>/;/g/;
          </View>/;/g/;
        </View>/;/g/;
      </Modal>/;/g/;
      {// 主题详情模态框}/;/g/;
      <Modal;"  />/;,"/g"/;
visible={showDetailModal}";,"";
animationType="slide";
transparent={true}
        onRequestClose={() => setShowDetailModal(false)}
      >;
        <View style={styles.modalOverlay}>;
          <View style={styles.modalContent}>;
            <Text style={styles.modalTitle}>主题详情</Text>/;/g/;
            {selectedTopic  && <View style={styles.detailContent}>;
                <View style={styles.detailRow}>;
                  <Text style={styles.detailLabel}>名称: </Text>/;/g/;
                  <Text style={styles.detailValue}>{selectedTopic.name}</Text>/;/g/;
                </View>/;/g/;
                <View style={styles.detailRow}>;
                  <Text style={styles.detailLabel}>描述: </Text>/;/g/;
                  <Text style={styles.detailValue}>;

                  </Text>/;/g/;
                </View>/;/g/;
                                <View style={styles.detailRow}>;
                  <Text style={styles.detailLabel}>创建时间: </Text>/;/g/;
                  <Text style={styles.detailValue}>;
                    {new Date(selectedTopic.creationTime).toLocaleString()}
                  </Text>/;/g/;
                </View>/;/g/;
                <View style={styles.detailRow}>;
                  <Text style={styles.detailLabel}>分区数: </Text>/;/g/;
                  <Text style={styles.detailValue}>;
                    {selectedTopic.partitionCount}
                  </Text>/;/g/;
                </View>/;/g/;
                <View style={styles.detailRow}>;
                  <Text style={styles.detailLabel}>保留时间: </Text>/;/g/;
                  <Text style={styles.detailValue}>;

                  </Text>/;/g/;
                </View>;/;/g/;
              </View>;/;/g/;
            )};
            <View style={styles.modalActions}>;
              <TouchableOpacity;  />/;,/g/;
style={[styles.modalButton, styles.confirmButton]};
onPress={() => setShowDetailModal(false)};
              >;
                <Text style={styles.confirmButtonText}>关闭</Text>;/;/g/;
              </TouchableOpacity>;/;/g/;
            </View>;/;/g/;
          </View>;/;/g/;
        </View>;/;/g/;
      </Modal>;/;/g/;
    </View>;/;/g/;
  );
};
const  styles = StyleSheet.create({)container: {,";,}flex: 1,";"";
}
    const backgroundColor = '#f5f5f5'}'';'';
  ;},';,'';
header: {,';,}flexDirection: 'row';','';
justifyContent: 'space-between';','';
alignItems: 'center';','';
padding: 16,';,'';
backgroundColor: '#fff';','';
borderBottomWidth: 1,';'';
}
    const borderBottomColor = '#e9ecef'}'';'';
  ;}
headerTitle: {,';,}fontSize: 18,';,'';
fontWeight: 'bold';','';'';
}
    const color = '#333'}'';'';
  ;},';,'';
createButton: {,';,}backgroundColor: '#007bff';','';
paddingHorizontal: 16,;
paddingVertical: 8,;
}
    const borderRadius = 6;}
  },';,'';
createButtonText: {,';,}color: '#fff';','';
fontSize: 14,';'';
}
    const fontWeight = '600'}'';'';
  ;}
list: {,;}}
  const flex = 1;}
  }
listContent: {,;}}
  const padding = 16;}
  },';,'';
topicItem: {,';,}backgroundColor: '#fff';','';
borderRadius: 8,;
padding: 16,';,'';
marginBottom: 12,';'';
}
    shadowColor: '#000';','}'';
shadowOffset: { width: 0, height: 1 ;}
shadowOpacity: 0.1,;
shadowRadius: 2,;
const elevation = 2;
  }
topicInfo: {,;}}
  const marginBottom = 12;}
  }
topicName: {,';,}fontSize: 16,';,'';
fontWeight: 'bold';','';
color: '#333';','';'';
}
    const marginBottom = 4;}
  }
topicDescription: {,';,}fontSize: 14,';,'';
color: '#6c757d';','';'';
}
    const marginBottom = 8;}
  }
topicMeta: {,';,}fontSize: 12,';'';
}
    const color = '#adb5bd'}'';'';
  ;},';,'';
topicActions: {,';,}flexDirection: 'row';','';'';
}
    const justifyContent = 'flex-end'}'';'';
  ;}
actionButton: {paddingHorizontal: 12,;
paddingVertical: 6,;
borderRadius: 4,;
}
    const marginLeft = 8;}
  },';,'';
selectButton: {,';}}'';
  const backgroundColor = '#28a745'}'';'';
  ;},';,'';
selectButtonText: {,';,}color: '#fff';','';
fontSize: 12,';'';
}
    const fontWeight = '600'}'';'';
  ;},';,'';
detailButton: {,';}}'';
  const backgroundColor = '#17a2b8'}'';'';
  ;},';,'';
detailButtonText: {,';,}color: '#fff';','';
fontSize: 12,';'';
}
    const fontWeight = '600'}'';'';
  ;},';,'';
deleteButton: {,';}}'';
  const backgroundColor = '#dc3545'}'';'';
  ;},';,'';
deleteButtonText: {,';,}color: '#fff';','';
fontSize: 12,';'';
}
    const fontWeight = '600'}'';'';
  ;}
loadingContainer: {,';,}flex: 1,';,'';
justifyContent: 'center';','';'';
}
    const alignItems = 'center'}'';'';
  ;}
loadingText: {marginTop: 12,';,'';
fontSize: 16,';'';
}
    const color = '#6c757d'}'';'';
  ;}
emptyContainer: {,';,}flex: 1,';,'';
justifyContent: 'center';','';
alignItems: 'center';','';'';
}
    const paddingVertical = 64;}
  }
emptyText: {,';,}fontSize: 16,';,'';
color: '#6c757d';','';'';
}
    const marginBottom = 24;}
  },';,'';
createFirstButton: {,';,}backgroundColor: '#007bff';','';
paddingHorizontal: 24,;
paddingVertical: 12,;
}
    const borderRadius = 8;}
  },';,'';
createFirstButtonText: {,';,}color: '#fff';','';
fontSize: 16,';'';
}
    const fontWeight = '600'}'';'';
  ;},);
modalOverlay: {,)';,}flex: 1,)';,'';
backgroundColor: 'rgba(0, 0, 0, 0.5)',';,'';
justifyContent: 'center';','';'';
}
    const alignItems = 'center'}'';'';
  ;},';,'';
modalContent: {,';,}backgroundColor: '#fff';','';
borderRadius: 12,';,'';
padding: 24,';,'';
width: '90%';','';'';
}
    const maxWidth = 400;}
  }
modalTitle: {,';,}fontSize: 18,';,'';
fontWeight: 'bold';','';
color: '#333';','';
marginBottom: 20,';'';
}
    const textAlign = 'center'}'';'';
  ;}
input: {,';,}borderWidth: 1,';,'';
borderColor: '#ced4da';','';
borderRadius: 6,;
padding: 12,;
fontSize: 16,;
}
    const marginBottom = 16;}
  }
textArea: {,';,}height: 80,';'';
}
    const textAlignVertical = 'top'}'';'';
  ;},';,'';
modalActions: {,';,}flexDirection: 'row';','';
justifyContent: 'space-between';','';'';
}
    const marginTop = 20;}
  }
modalButton: {flex: 1,;
paddingVertical: 12,';,'';
borderRadius: 6,';'';
}
    const alignItems = 'center'}'';'';
  ;},';,'';
cancelButton: {,';,}backgroundColor: '#6c757d';','';'';
}
    const marginRight = 8;}
  },';,'';
cancelButtonText: {,';,}color: '#fff';','';
fontSize: 16,';'';
}
    const fontWeight = '600'}'';'';
  ;},';,'';
confirmButton: {,';,}backgroundColor: '#007bff';','';'';
}
    const marginLeft = 8;}
  },';,'';
confirmButtonText: {,';,}color: '#fff';','';
fontSize: 16,';'';
}
    const fontWeight = '600'}'';'';
  ;}
detailContent: {,;}}
  const marginBottom = 20;}';'';
  },detailRow: {,';,}flexDirection: "row";","";"";
}
      const marginBottom = 12;"}"";"";
  },detailLabel: {fontSize: 14,fontWeight: '600',color: '#495057',width: 80;'}'';'';
  },detailValue: {fontSize: 14,color: '#6c757d',flex: 1;'}'';'';
  };
});';,'';
export default TopicManager;