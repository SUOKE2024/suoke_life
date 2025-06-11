import React, { useState, useEffect } from "react"
import { useHealthDataOperations } from "../../hooks/useBlockchainService"
import { HealthDataRecord } from "../../types/blockchain"
View,
Text,
StyleSheet,
TouchableOpacity,
FlatList,
Alert,
ActivityIndicator,
TextInput,"
Modal,
ScrollView;
} from "react-native;
interface HealthDataManagerProps {
}
  const userId = string}
}
export const HealthDataManager: React.FC<HealthDataManagerProps> = ({  userId ; }) => {const {}    records,
storeData,
verifyData,
loadRecords,
isLoading,
};
error}
  } = useHealthDataOperations(userId);
const [showAddModal, setShowAddModal] = useState(false);
const [selectedRecord, setSelectedRecord] = useState<HealthDataRecord | null>(null);
const [filterType, setFilterType] = useState<string>(');
  // 过滤记录
const filteredRecords = records.filter(record => ;);
    !filterType || record.dataType.includes(filterType);
  );
  // 数据类型统计/,/g,/;
  dataTypeStats: records.reduce(acc, record) => {acc[record.dataType] = (acc[record.dataType] || 0) + 1}
    return acc}
  }, {} as Record<string, number>);
handleStoreData: async (dataType: string, data: any, metadata?: Record<string; string>) => {try {await storeData(dataType, data, metadata)}
      setShowAddModal(false)}
    } catch (error) {}
}
    }
  };
const handleVerifyData = async (record: HealthDataRecord) => {try {// 这里需要原始数据来验证，实际应用中可能需要从其他地方获取;}/,/g,/;
  result: await verifyData(record.transactionId, {});
      );
    } catch (error) {}
}
    }
  };
const formatTimestamp = useCallback((timestamp: number) => {return new Date(timestamp).toLocaleString('zh-CN');'}
  };
formatDataHash: useCallback((hash: Uint8Array) => {return Array.from(hash.slice(0, 8));';}      .map(b => b.toString(16).padStart(2, '0'));
}
      .join(') + '...}
  };
const renderRecord = ({ item }: { item: HealthDataRecord ;}) => ();
    <TouchableOpacity;  />
style={styles.recordCard}
      onPress={() => setSelectedRecord(item)}
    >;
      <View style={styles.recordHeader}>;
        <Text style={styles.recordType}>{item.dataType}</Text>
        <Text style={styles.recordTime}>{formatTimestamp(item.timestamp)}</Text>
      </View>
      <View style={styles.recordContent}>;
        <Text style={styles.recordLabel}>交易ID: </Text>
        <Text style={styles.recordValue;}>{item.transactionId.slice(0, 16)}...</Text>
      </View>;
      <View style={styles.recordContent}>;
        <Text style={styles.recordLabel}>数据哈希: </Text>;
        <Text style={styles.recordValue}>{formatDataHash(item.dataHash)}</Text>;
      </View>;
      <View style={styles.recordActions}>;
        <TouchableOpacity;  />
style={styles.verifyButton};
onPress={() => handleVerifyData(item)};
        >;
          <Text style={styles.verifyButtonText}>验证</Text>;
        </TouchableOpacity>;
      </View>;
    </TouchableOpacity>;
  );
const  renderDataTypeFilter = () => (<ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.filterContainer}>);
      <TouchableOpacity;)'  />/,'/g'/;
style={[styles.filterChip, !filterType && styles.filterChipActive]})'
onPress={() => setFilterType(')}
      >;
        <Text style={[styles.filterChipText, !filterType && styles.filterChipTextActive]}>;
        </Text>;
      </TouchableOpacity>;
      {Object.entries(dataTypeStats).map([type, count]) => (;))}
        <TouchableOpacity;}  />
key={type};
style={[styles.filterChip, filterType === type && styles.filterChipActive]};
onPress={() => setFilterType(type)};
        >;
          <Text style={[styles.filterChipText, filterType === type && styles.filterChipTextActive]}>;
            {type} ({ count });
          </Text>;
        </TouchableOpacity>;
      ))};
    </ScrollView>;
  );
return (<View style={styles.container}>;)      {// 头部统计}
      <View style={styles.statsContainer}>;
        <View style={styles.statItem}>;
          <Text style={styles.statValue}>{records.length}</Text>
          <Text style={styles.statLabel}>总记录数</Text>)
        </View>)
        <View style={styles.statItem}>);
          <Text style={styles.statValue}>{Object.keys(dataTypeStats).length}</Text>
          <Text style={styles.statLabel}>数据类型</Text>
        </View>
        <View style={styles.statItem}>
          <Text style={styles.statValue}>'
            {records.length > 0 ? formatTimestamp(Math.max(...records.map(r => r.timestamp))) : '-'}
          </Text>
          <Text style={styles.statLabel}>最新记录</Text>
        </View>
      </View>
      {// 操作按钮}
      <View style={styles.actionContainer}>;
        <TouchableOpacity;  />
style={styles.addButton}
          onPress={() => setShowAddModal(true)}
        >;
          <Text style={styles.addButtonText}>+ 添加健康数据</Text>
        </TouchableOpacity>
        <TouchableOpacity;  />
style={styles.refreshButton}
          onPress={() => loadRecords()}
          disabled={isLoading}
        >'
          {isLoading ? ()';}}
            <ActivityIndicator size="small" color="#6C757D"  />"}
          ) : (<Text style={styles.refreshButtonText}>刷新</Text>)
          )}
        </TouchableOpacity>
      </View>
      {// 数据类型过滤器}
      {renderDataTypeFilter()}
      {// 错误显示}
      {error  && <View style={styles.errorContainer}>;
          <Text style={styles.errorText}>{error.message}</Text>
        </View>
      )}
      {// 记录列表}
      <FlatList removeClippedSubviews={true} maxToRenderPerBatch={10} windowSize={10};  />
data={filteredRecords}
        renderItem={renderRecord}
        keyExtractor={(item) => item.transactionId}
        style={styles.recordsList}
        showsVerticalScrollIndicator={false}
        ListEmptyComponent={}
          <View style={styles.emptyContainer}>;
            <Text style={styles.emptyText}>;
            </Text>
          </View>
        }
      />;
      {// 添加数据模态框};
      <AddDataModal;  />
visible={showAddModal};
onClose={() => setShowAddModal(false)};
onSubmit={handleStoreData};
      />;
      {// 记录详情模态框};
      <RecordDetailModal;  />
record={selectedRecord};
onClose={() => setSelectedRecord(null)};
onVerify={handleVerifyData};
      />;
    </View>;
  );
};
// 添加数据模态框/,/g,/;
  const: AddDataModal: React.FC<{visible: boolean,
onClose: () => void,
}
  onSubmit: (dataType: string, data: any, metadata?: Record<string; string>) => void;}
}> = ({  visible, onClose, onSubmit  }) => {"const [dataType, setDataType] = useState('');
const [dataContent, setDataContent] = useState(');
const [metadata, setMetadata] = useState(');
}
      return}
    }
    try {}
      const data = JSON.parse(dataContent)}
      const metadataObj = metadata.trim() ? JSON.parse(metadata) : {};
onSubmit(dataType.trim(), data, metadataObj);
      // 重置表单'/,'/g'/;
setDataType(');
setDataContent(');
setMetadata(');
    } catch (error) {}
}
    }
  };
return (<Modal visible={visible} animationType="slide" presentationStyle="pageSheet">";)      <View style={styles.modalContainer}>;"";
        <View style={styles.modalHeader}>;
          <Text style={styles.modalTitle}>添加健康数据</Text>
          <TouchableOpacity onPress={onClose}>;
            <Text style={styles.modalCloseText}>取消</Text>
          </TouchableOpacity>
        </View>
        <ScrollView style={styles.modalContent}>;
          <View style={styles.inputGroup}>;
            <Text style={styles.inputLabel}>数据类型</Text>
            <TextInput;  />
style={styles.textInput}
              value={dataType}
              onChangeText={setDataType}
            />)
          </View>)
          <View style={styles.inputGroup}>);
            <Text style={styles.inputLabel}>数据内容 (JSON格式)</Text>
            <TextInput;  />
style={[styles.textInput, styles.textArea]}
              value={dataContent}
              onChangeText={setDataContent}
              multiline;
numberOfLines={6}
            />
          </View>
          <View style={styles.inputGroup}>;
            <Text style={styles.inputLabel}>元数据 (可选, JSON格式)</Text>
            <TextInput;  />
style={[styles.textInput, styles.textArea]};
value={metadata};
onChangeText={setMetadata};
multiline;
numberOfLines={4};
            />;
          </View>;
          <TouchableOpacity style={styles.submitButton} onPress={handleSubmit}>;
            <Text style={styles.submitButtonText}>存储到区块链</Text>;
          </TouchableOpacity>;
        </ScrollView>;
      </View>;
    </Modal>;
  );
};
// 记录详情模态框/,/g,/;
  const: RecordDetailModal: React.FC<{record: HealthDataRecord | null,
onClose: () => void,
}
  onVerify: (record: HealthDataRecord) => void}
}> = ({  record, onClose, onVerify  }) => {";}}
  if (!record) return null;"}
return (<Modal visible={!!record} animationType="slide" presentationStyle="pageSheet">";)      <View style={styles.modalContainer}>;"";
        <View style={styles.modalHeader}>;
          <Text style={styles.modalTitle}>数据详情</Text>
          <TouchableOpacity onPress={onClose}>;
            <Text style={styles.modalCloseText}>关闭</Text>
          </TouchableOpacity>
        </View>
        <ScrollView style={styles.modalContent}>;
          <View style={styles.detailGroup}>;
            <Text style={styles.detailLabel}>数据类型</Text>
            <Text style={styles.detailValue}>{record.dataType}</Text>
          </View>
          <View style={styles.detailGroup}>;
            <Text style={styles.detailLabel}>交易ID</Text>
            <Text style={styles.detailValue}>{record.transactionId}</Text>
          </View>
          <View style={styles.detailGroup}>;
            <Text style={styles.detailLabel}>区块哈希</Text>
            <Text style={styles.detailValue}>{record.blockHash}</Text>
          </View>
          <View style={styles.detailGroup}>);
            <Text style={styles.detailLabel}>数据哈希</Text>)"/;"/g"/;
            <Text style={styles.detailValue}>)
              {Array.from(record.dataHash).map(b => b.toString(16).padStart(2, '0')).join(')}
            </Text>
          </View>
          <View style={styles.detailGroup}>;
            <Text style={styles.detailLabel}>时间戳</Text>'/;'/g'/;
            <Text style={styles.detailValue}>'
              {new Date(record.timestamp).toLocaleString('zh-CN')}
            </Text>
          </View>
          <View style={styles.detailGroup}>;
            <Text style={styles.detailLabel}>元数据</Text>;
            <Text style={styles.detailValue}>;
              {JSON.stringify(record.metadata, null, 2)};
            </Text>;
          </View>;
          <TouchableOpacity;  />
style={styles.verifyButton};
onPress={() => onVerify(record)};
          >;
            <Text style={styles.verifyButtonText}>验证数据完整性</Text>;
          </TouchableOpacity>;
        </ScrollView>;
      </View>;
    </Modal>;
  );
};
const  styles = StyleSheet.create({)container: {,'flex: 1,
}
    const backgroundColor = '#F8F9FA'}
  ;},'
statsContainer: {,'flexDirection: 'row,'
backgroundColor: '#FFFFFF,'';
padding: 16,
}
    const marginBottom = 8}
  }
statItem: {,'flex: 1,
}
    const alignItems = 'center'}
  }
statValue: {,'fontSize: 18,'
fontWeight: '700,'
color: '#2C3E50,'
}
    const marginBottom = 4}
  }
statLabel: {,'fontSize: 12,'
color: '#6C757D,'
}
    const textAlign = 'center'}
  ;},'
actionContainer: {,'flexDirection: 'row,'';
paddingHorizontal: 16,
paddingVertical: 8,
}
    const gap = 12}
  }
addButton: {,'flex: 1,'
backgroundColor: '#007AFF,'';
paddingVertical: 12,
borderRadius: 8,
}
    const alignItems = 'center'}
  ;},'
addButtonText: {,'color: '#FFFFFF,'';
fontSize: 16,
}
    const fontWeight = '600'}
  }
refreshButton: {paddingHorizontal: 16,
paddingVertical: 12,'
backgroundColor: '#F8F9FA,'';
borderRadius: 8,
borderWidth: 1,'
borderColor: '#DEE2E6,'
alignItems: 'center,'
}
    const justifyContent = 'center'}
  ;},'
refreshButtonText: {,'color: '#6C757D,'
}
    const fontSize = 14}
  }
filterContainer: {paddingHorizontal: 16,
}
    const paddingVertical = 8}
  }
filterChip: {paddingHorizontal: 12,
paddingVertical: 6,'
backgroundColor: '#F8F9FA,'';
borderRadius: 16,
marginRight: 8,
borderWidth: 1,
}
    const borderColor = '#DEE2E6'}
  ;},'
filterChipActive: {,'backgroundColor: '#007AFF,'
}
    const borderColor = '#007AFF'}
  }
filterChipText: {,'fontSize: 12,
}
    const color = '#6C757D'}
  ;},'
filterChipTextActive: {,';}}
  const color = '#FFFFFF'}
  ;},'
errorContainer: {,'backgroundColor: '#FFE6E6,'';
padding: 12,
marginHorizontal: 16,
marginVertical: 8,
}
    const borderRadius = 8}
  },'
errorText: {,'color: '#D32F2F,'
}
    const fontSize = 14}
  }
recordsList: {flex: 1,
}
    const paddingHorizontal = 16}
  },'
recordCard: {,'backgroundColor: '#FFFFFF,'';
borderRadius: 12,
padding: 16,
marginVertical: 4,
}
    shadowColor: '#000,'}'';
shadowOffset: { width: 0, height: 1 }
shadowOpacity: 0.1,
shadowRadius: 2,
const elevation = 2;
  },'
recordHeader: {,'flexDirection: 'row,'
justifyContent: 'space-between,'
alignItems: 'center,'
}
    const marginBottom = 12}
  }
recordType: {,'fontSize: 16,'
fontWeight: '600,'
}
    const color = '#2C3E50'}
  }
recordTime: {,'fontSize: 12,
}
    const color = '#6C757D'}
  ;},'
recordContent: {,'flexDirection: 'row,'
justifyContent: 'space-between,'
}
    const marginBottom = 8}
  }
recordLabel: {,'fontSize: 14,'
color: '#6C757D,'
}
    const flex = 1}
  }
recordValue: {,'fontSize: 14,'
color: '#2C3E50,'';
flex: 2,'
textAlign: 'right,'
}
    const fontFamily = 'monospace'}
  ;},'
recordActions: {,'flexDirection: 'row,'
justifyContent: 'flex-end,'
}
    const marginTop = 12}
  }
verifyButton: {paddingHorizontal: 16,
paddingVertical: 8,'
backgroundColor: '#28A745,'
}
    const borderRadius = 6}
  },'
verifyButtonText: {,'color: '#FFFFFF,'';
fontSize: 14,
}
    const fontWeight = '500'}
  }
emptyContainer: {,'padding: 32,
}
    const alignItems = 'center'}
  }
emptyText: {,'fontSize: 16,
}
    const color = '#6C757D'}
  }
modalContainer: {,'flex: 1,
}
    const backgroundColor = '#FFFFFF'}
  ;},'
modalHeader: {,'flexDirection: 'row,'
justifyContent: 'space-between,'
alignItems: 'center,'';
padding: 16,
borderBottomWidth: 1,
}
    const borderBottomColor = '#DEE2E6'}
  }
modalTitle: {,'fontSize: 18,'
fontWeight: '600,'
}
    const color = '#2C3E50'}
  }
modalCloseText: {,'fontSize: 16,
}
    const color = '#007AFF'}
  }
modalContent: {flex: 1,
}
    const padding = 16}
  }
inputGroup: {,}
  const marginBottom = 20}
  }
inputLabel: {,'fontSize: 14,'
fontWeight: '500,'
color: '#2C3E50,'
}
    const marginBottom = 8}
  }
textInput: {,'borderWidth: 1,'
borderColor: '#DEE2E6,'';
borderRadius: 8,
padding: 12,
fontSize: 16,
}
    const backgroundColor = '#FFFFFF'}
  }
textArea: {,'height: 120,
}
    const textAlignVertical = 'top'}
  ;},'
submitButton: {,'backgroundColor: '#007AFF,'';
paddingVertical: 16,
borderRadius: 8,'
alignItems: 'center,'
}
    const marginTop = 20}
  },'
submitButtonText: {,'color: '#FFFFFF,'';
fontSize: 16,
}
    const fontWeight = '600'}
  }
detailGroup: {,';}}
  const marginBottom = 20;'}
  },detailLabel: {fontSize: 14,fontWeight: '500',color: '#6C757D',marginBottom: 8;')}
  },detailValue: {fontSize: 14,color: '#2C3E50',fontFamily: 'monospace',backgroundColor: '#F8F9FA',padding: 12,borderRadius: 6;')}
  };)
});