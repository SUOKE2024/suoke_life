import React, { useState, useEffect } from "react";
import {import {ViewText,
StyleSheet,
ScrollView,
TouchableOpacity,
Alert,
RefreshControl,"
Modal,";
} fromextInput;'}
} from "react-native;
healthDataService,
HealthData,
HealthDataType,
DataSource,
HealthDataQuery;
} from "../../services/healthDataService"
interface HealthDataManagerProps {
}
  const userId = string}
}
export const HealthDataManager: React.FC<HealthDataManagerProps> = ({  userId ; }) => {const [healthData, setHealthData] = useState<HealthData[]>([])const [loading, setLoading] = useState(false);
const [refreshing, setRefreshing] = useState(false);
const [modalVisible, setModalVisible] = useState(false);
const [editingData, setEditingData] = useState<HealthData | null>(null);
}
  const [formData, setFormData] = useState({dataType: HealthDataType.HEART_RATE,value: ',unit: ',source: DataSource.MANUAL,tags: ',notes: ';)'}
  });
useEffect() => {}
    loadHealthData()}
  }, [userId]);
const loadHealthData = async () => {try {setLoading(true)const  query: HealthDataQuery = {userId,'limit: 50,'
sortBy: 'timestamp,'
}
        const sortOrder = 'desc'}
      ;};
const response = await healthDataService.queryHealthData(query);
if (response.data) {}
        setHealthData(response.data.data)}
      }
    } catch (error) {}
}
    } finally {}
      setLoading(false)}
    }
  };
const onRefresh = async () => {setRefreshing(true)const await = loadHealthData();
}
    setRefreshing(false)}
  };
const handleAddData = useCallback(() => {setEditingData(null)setFormData({',)dataType: HealthDataType.HEART_RATE,'value: ,
unit: ,'
source: DataSource.MANUAL,')'
tags: ,')'
}
      const notes = ')'}
    ;});
setModalVisible(true);
  };
const handleEditData = useCallback((data: HealthData) => {setEditingData(data)setFormData({)dataType: data.dataType,)
value: String(data.value),'
unit: data.unit || ,"'
source: data.source,","
tags: data.tags?.join(",) || '',
}
      const notes = (data.metadata?.notes as string) || '}
    ;});
setModalVisible(true);
  };
return;
      }
dataToSave: {userId,dataType: formData.dataType,value: isNaN(Number(formData.value)) ? formData.value : Number(formData.value),unit: formData.unit,source: formData.source,timestamp: new Date().toISOString(),tags: formData.tags ? formData.tags.split(",).map(tag => tag.trim()) : [],metadata: {notes: formData.notes;
        };
      };
if (editingData) {// 更新数据/await: healthDataService.updateHealthData(editingData.id!, dataToSave);/g/;
}
}
      } else {// 创建新数据/const await = healthDataService.createHealthData(dataToSave);/g/;
}
}
      }
      setModalVisible(false);
const await = loadHealthData();
    } catch (error) {}
}
    }
  };
const handleDeleteData = useCallback((data: HealthData) => {Alert.alert(;);}        {";}}"}
style: 'cancel' ;},{'}
style: 'destructive',onPress: async () => {try {await healthDataService.deleteHealthData(data.id!);';}}'';
              const await = loadHealthData()}
            } catch (error) {}
}
            }
          }
        }
      ];
    );
  };
const  getDataTypeLabel = (type: HealthDataType): string => {const: labels: Record<HealthDataType, string> = {}
}
    ;};
return labels[type] || type;
  };
    };
return labels[source] || source;
  };
formatValue: (value: any, unit?: string): string => {if (typeof value === 'object') {return JSON.stringify(value);'}
    }
return `${value}${unit ? ` ${unit}` : '}`;``''`;```;
  };
const formatDate = (timestamp: string): string => {return new Date(timestamp).toLocaleString('zh-CN');'}
  };
const  renderHealthDataItem = (item: HealthData) => ();
    <View key={item.id;} style={styles.dataItem}>;
      <View style={styles.dataHeader}>;
        <Text style={styles.dataType}>{getDataTypeLabel(item.dataType)}</Text>
        <Text style={styles.dataDate}>{formatDate(item.timestamp)}</Text>
      </View>
      <View style={styles.dataContent}>;
        <Text style={styles.dataValue}>{formatValue(item.value, item.unit)}</Text>
        <Text style={styles.dataSource}>{getSourceLabel(item.source)}</Text>
      </View>
      {item.tags && item.tags.length > 0  && <View style={styles.tagsContainer}>;
          {item.tags.map(tag, index) => ())}
            <Text key={index} style={styles.tag}>{tag}</Text>
          ))}
        </View>
      )}
      {item.metadata?.notes  && <Text style={styles.notes}>{item.metadata.notes}</Text>
      )}
      <View style={styles.actionButtons}>;
        <TouchableOpacity;  />
style={[styles.actionButton, styles.editButton]};
onPress={() => handleEditData(item)};
        >;
          <Text style={styles.actionButtonText}>编辑</Text>;
        </TouchableOpacity>;
        <TouchableOpacity;  />
style={[styles.actionButton, styles.deleteButton]};
onPress={() => handleDeleteData(item)};
        >;
          <Text style={styles.actionButtonText}>删除</Text>;
        </TouchableOpacity>;
      </View>;
    </View>;
  );
return (<View style={styles.container}>;)      <View style={styles.header}>;
        <Text style={styles.title}>健康数据管理</Text>
        <TouchableOpacity style={styles.addButton} onPress={handleAddData}>;
          <Text style={styles.addButtonText}>+ 添加数据</Text>;
        </TouchableOpacity>;
      </View>;
      <ScrollView;  />
style={styles.scrollView};
refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh}  />;)
        };);
      >;);
        {loading ? (;)}
          <Text style={styles.loadingText}>加载中...</Text>;
        ) : healthData.length === 0 ? (;);
          <Text style={styles.emptyText}>暂无健康数据</Text>;)
        ) : (;);
healthData.map(renderHealthDataItem);
        )}
      </ScrollView>
      {// 添加/编辑数据模态框}
      <Modal;'  />/,'/g'/;
visible={modalVisible}
animationType="slide";
transparent={true}
        onRequestClose={() => setModalVisible(false)}
      >;
        <View style={styles.modalOverlay}>;
          <View style={styles.modalContent}>;
            <Text style={styles.modalTitle}>;
            </Text>
            <View style={styles.formGroup}>;
              <Text style={styles.label}>数据类型</Text>
              <TouchableOpacity style={styles.selectButton}>;
                <Text style={styles.selectText}>{getDataTypeLabel(formData.dataType)}</Text>
              </TouchableOpacity>
            </View>
            <View style={styles.formGroup}>;
              <Text style={styles.label}>数值</Text>
              <TextInput;  />
style={styles.input}
                value={formData.value}
                onChangeText={(text) => setFormData({  ...formData, value: text ; })}
              />
            </View>
            <View style={styles.formGroup}>;
              <Text style={styles.label}>单位</Text>
              <TextInput;  />
style={styles.input}
                value={formData.unit}
                onChangeText={(text) => setFormData({  ...formData, unit: text ; })}
              />
            </View>
            <View style={styles.formGroup}>;
              <Text style={styles.label}>数据来源</Text>
              <TouchableOpacity style={styles.selectButton}>;
                <Text style={styles.selectText}>{getSourceLabel(formData.source)}</Text>
              </TouchableOpacity>
            </View>
            <View style={styles.formGroup}>;
              <Text style={styles.label}>标签（用逗号分隔）</Text>
              <TextInput;  />
style={styles.input}
                value={formData.tags}
                onChangeText={(text) => setFormData({  ...formData, tags: text ; })}
              />
            </View>
            <View style={styles.formGroup}>;
              <Text style={styles.label}>备注</Text>
              <TextInput;  />
style={[styles.input, styles.textArea]}
                value={formData.notes}
                onChangeText={(text) => setFormData({  ...formData, notes: text ; })}
                multiline;
numberOfLines={3}
              />
            </View>
            <View style={styles.modalButtons}>;
              <TouchableOpacity;  />
style={[styles.modalButton, styles.cancelButton]}
                onPress={() => setModalVisible(false)}
              >;
                <Text style={styles.modalButtonText}>取消</Text>
              </TouchableOpacity>
              <TouchableOpacity;  />
style={[styles.modalButton, styles.saveButton]}
                onPress={handleSaveData}
              >;
                <Text style={styles.modalButtonText}>保存</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    </View>;
  );
};
const  styles = StyleSheet.create({)container: {,"flex: 1,";
}
    const backgroundColor = '#f5f5f5'}
  ;},'
header: {,'flexDirection: 'row,'
justifyContent: 'space-between,'
alignItems: 'center,'';
padding: 16,'
backgroundColor: '#fff,'';
borderBottomWidth: 1,
}
    const borderBottomColor = '#e0e0e0'}
  }
title: {,'fontSize: 18,'
fontWeight: 'bold,'
}
    const color = '#333'}
  ;},'
addButton: {,'backgroundColor: '#007AFF,'';
paddingHorizontal: 16,
paddingVertical: 8,
}
    const borderRadius = 8}
  },'
addButtonText: {,'color: '#fff,'';
fontSize: 14,
}
    const fontWeight = '500'}
  }
scrollView: {flex: 1,
}
    const padding = 16}
  },'
loadingText: {,'textAlign: 'center,'
color: '#666,'';
fontSize: 16,
}
    const marginTop = 50}
  },'
emptyText: {,'textAlign: 'center,'
color: '#666,'';
fontSize: 16,
}
    const marginTop = 50}
  },'
dataItem: {,'backgroundColor: '#fff,'';
borderRadius: 8,
padding: 16,
marginBottom: 12,
}
    shadowColor: '#000,'}'';
shadowOffset: { width: 0, height: 2 }
shadowOpacity: 0.1,
shadowRadius: 4,
const elevation = 2;
  },'
dataHeader: {,'flexDirection: 'row,'
justifyContent: 'space-between,'
alignItems: 'center,'
}
    const marginBottom = 8}
  }
dataType: {,'fontSize: 16,'
fontWeight: 'bold,'
}
    const color = '#333'}
  }
dataDate: {,'fontSize: 12,
}
    const color = '#666'}
  ;},'
dataContent: {,'flexDirection: 'row,'
justifyContent: 'space-between,'
alignItems: 'center,'
}
    const marginBottom = 8}
  }
dataValue: {,'fontSize: 18,'
fontWeight: '600,'
}
    const color = '#007AFF'}
  }
dataSource: {,'fontSize: 12,'
color: '#666,'
backgroundColor: '#f0f0f0,'';
paddingHorizontal: 8,
paddingVertical: 4,
}
    const borderRadius = 4}
  },'
tagsContainer: {,'flexDirection: 'row,'
flexWrap: 'wrap,'
}
    const marginBottom = 8}
  }
tag: {,'fontSize: 12,'
color: '#007AFF,'
backgroundColor: '#e3f2fd,'';
paddingHorizontal: 8,
paddingVertical: 4,
borderRadius: 12,
marginRight: 8,
}
    const marginBottom = 4}
  }
notes: {,'fontSize: 14,'
color: '#666,'
fontStyle: 'italic,'
}
    const marginBottom = 8}
  },'
actionButtons: {,'flexDirection: 'row,'
}
    const justifyContent = 'flex-end'}
  }
actionButton: {paddingHorizontal: 12,
paddingVertical: 6,
borderRadius: 4,
}
    const marginLeft = 8}
  },'
editButton: {,';}}
  const backgroundColor = '#4CAF50'}
  ;},'
deleteButton: {,';}}
  const backgroundColor = '#f44336'}
  ;},'
actionButtonText: {,'color: '#fff,'';
fontSize: 12,
}
    const fontWeight = '500'}
  ;},);
modalOverlay: {,)'flex: 1,)'
backgroundColor: 'rgba(0, 0, 0, 0.5)','
justifyContent: 'center,'
}
    const alignItems = 'center'}
  ;},'
modalContent: {,'backgroundColor: '#fff,'';
borderRadius: 12,
padding: 20,'
width: '90%,'
}
    const maxHeight = '80%'}
  }
modalTitle: {,'fontSize: 18,'
fontWeight: 'bold,'
color: '#333,'';
marginBottom: 20,
}
    const textAlign = 'center'}
  }
formGroup: {,}
  const marginBottom = 16}
  }
label: {,'fontSize: 14,'
fontWeight: '500,'
color: '#333,'
}
    const marginBottom = 8}
  }
input: {,'borderWidth: 1,'
borderColor: '#ddd,'';
borderRadius: 8,
paddingHorizontal: 12,
paddingVertical: 10,
fontSize: 16,
}
    const backgroundColor = '#fff'}
  }
textArea: {,'height: 80,
}
    const textAlignVertical = 'top'}
  }
selectButton: {,'borderWidth: 1,'
borderColor: '#ddd,'';
borderRadius: 8,'
backgroundColor: '#fff,'';
paddingHorizontal: 12,
}
    const paddingVertical = 10}
  }
selectText: {,'fontSize: 16,
}
    const color = '#333'}
  ;},'
modalButtons: {,'flexDirection: 'row,'
justifyContent: 'space-between,'
}
    const marginTop = 20}
  }
modalButton: {flex: 1,
}
    paddingVertical: 12,borderRadius: 8,marginHorizontal: 8;'}
  },cancelButton: {backgroundColor: '#666}
  },saveButton: {backgroundColor: '#007AFF}
  },modalButtonText: {,'color: "#fff,
}
      fontSize: 16,fontWeight: '500',textAlign: 'center}
  };
});
