import React, { useState, useEffect } from 'react';
import {import {View;
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  RefreshControl,
  Modal,
  TextInput;
} from 'react-native';
  healthDataService,
  TCMDiagnosisData,
  TCMDiagnosisType,
  TCMObservation,
  DataSource;
} from '../../services/healthDataService';
interface TCMDiagnosisPanelProps {
  userId: string;
}
interface DiagnosisFormData {
  diagnosisType: TCMDiagnosisType;
  observations: TCMObservation[];
  conclusion: string;
  recommendations: string[];
  confidence: number;
}
export const TCMDiagnosisPanel: React.FC<TCMDiagnosisPanelProps> = ({ userId ;}) => {
  const [diagnosisData, setDiagnosisData] = useState<TCMDiagnosisData[]>([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [selectedDiagnosisType, setSelectedDiagnosisType] = useState<TCMDiagnosisType>(TCMDiagnosisType.LOOK);
  const [formData, setFormData] = useState<DiagnosisFormData>({diagnosisType: TCMDiagnosisType.LOOK,observations: [],conclusion: '',recommendations: [],confidence: 80;)
  });
  useEffect() => {
    loadDiagnosisData();
  }, [userId]);
  const loadDiagnosisData = async () => {try {setLoading(true);
      const response = await healthDataService.getTCMDiagnosis(userId);
      if (response.data) {
        setDiagnosisData(response.data);
      }
    } catch (error) {


    } finally {
      setLoading(false);
    }
  };
  const onRefresh = async () => {setRefreshing(true);
    await loadDiagnosisData();
    setRefreshing(false);
  };

    };
    return labels[type];
  };

    };
    return descriptions[type];
  };

    };
    return categories[type] || [];
  };
  const handleAddDiagnosis = (type: TCMDiagnosisType) => {setSelectedDiagnosisType(type);
    setFormData({
      diagnosisType: type;
      observations: [];
      conclusion: '';
      recommendations: [];
      confidence: 80;
    });
    setModalVisible(true);
  };
  const addObservation = () => {const newObservation: TCMObservation = {,
  category: "";
      value: '',description: '',severity: 'mild',confidence: 80;
    };
    setFormData({
      ...formData,
      observations: [...formData.observations, newObservation]
    ;});
  };
  const updateObservation = (index: number, field: keyof TCMObservation, value: any) => {const updatedObservations = [...formData.observations];
    updatedObservations[index] = {
      ...updatedObservations[index],
      [field]: value;
    };
    setFormData({
      ...formData,
      observations: updatedObservations;
    });
  };
  const removeObservation = (index: number) => {const updatedObservations = formData.observations.filter(_, i) => i !== index);
    setFormData({
      ...formData,
      observations: updatedObservations;
    });
  };

        return;
      }
      const diagnosisToSave = {userId,diagnosisType: formData.diagnosisType,observations: formData.observations,conclusion: formData.conclusion,recommendations: formData.recommendations.filter(r => r.trim() !== ''),timestamp: new Date().toISOString(),confidence: formData.confidence / 100,metadata: {source: 'manual_input';
        };
      };
      await healthDataService.createTCMDiagnosis(diagnosisToSave);

      setModalVisible(false);
      await loadDiagnosisData();
    } catch (error) {


    }
  };
  const formatDate = (timestamp: string): string => {return new Date(timestamp).toLocaleString('zh-CN');
  };
  const renderDiagnosisTypeCard = (type: TCMDiagnosisType) => {const recentData = diagnosisData;
      .filter(d => d.diagnosisType === type);
      .sort(a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
      .slice(0, 1)[0];
    return (
  <View key={type} style={styles.diagnosisCard}>
        <View style={styles.cardHeader}>
          <View>
            <Text style={styles.cardTitle}>{getDiagnosisTypeLabel(type)}</Text>
            <Text style={styles.cardDescription}>{getDiagnosisTypeDescription(type)}</Text>
          </View>
          <TouchableOpacity;
            style={styles.addButton}
            onPress={() => handleAddDiagnosis(type)}
          >
            <Text style={styles.addButtonText}>+</Text>
          </TouchableOpacity>
        </View>
        {recentData ? ()
          <View style={styles.recentData}>;
            <Text style={styles.recentDataTitle}>最近记录</Text>;
            <Text style={styles.recentDataTime}>{formatDate(recentData.timestamp)}</Text>;
            {recentData.conclusion && (;)
              <Text style={styles.recentDataConclusion}>{recentData.conclusion}</Text>;
            )};
            <Text style={styles.observationCount}>;

            </Text>;
          </View>;
        ) : (;
          <View style={styles.noData}>;
            <Text style={styles.noDataText}>暂无记录</Text>;
          </View>;
        )};
      </View>;
    );
  };
  const renderObservationForm = (observation: TCMObservation, index: number) => ()
    <View key={index;} style={styles.observationForm}>
      <View style={styles.observationHeader}>
        <Text style={styles.observationTitle}>观察记录 {index + 1}</Text>
        <TouchableOpacity;
          style={styles.removeButton}
          onPress={() => removeObservation(index)}
        >
          <Text style={styles.removeButtonText}>×</Text>
        </TouchableOpacity>
      </View>
      <View style={styles.formRow}>
        <Text style={styles.label}>类别</Text>
        <TouchableOpacity style={styles.selectButton}>
          <Text style={styles.selectText}>

          </Text>
        </TouchableOpacity>
      </View>
      <View style={styles.formRow}>
        <Text style={styles.label}>观察值</Text>
        <TextInput;
          style={styles.input}
          value={observation.value.toString()}
          onChangeText={(text) => updateObservation(index, 'value', text)}

        />
      </View>
      <View style={styles.formRow}>
        <Text style={styles.label}>描述</Text>
        <TextInput;
          style={[styles.input, styles.textArea]}
          value={observation.description}
          onChangeText={(text) => updateObservation(index, 'description', text)}

          multiline;
          numberOfLines={3}
        />
      </View>
      <View style={styles.formRow}>
        <Text style={styles.label}>严重程度</Text>
        <View style={styles.severityButtons}>
          {(["mild",moderate', 'severe'] as const).map(severity) => ()
            <TouchableOpacity;
              key={severity}
              style={[
                styles.severityButton,observation.severity === severity && styles.severityButtonActive;
              ]}};
              onPress={() => updateObservation(index, 'severity', severity)};
            >;
              <Text style={[;
                styles.severityButtonText,observation.severity === severity && styles.severityButtonTextActive;
              ]}}>;

              </Text>;
            </TouchableOpacity>;
          ))};
        </View>;
      </View>;
    </View>;
  );
  const renderDiagnosisModal = () => (
  <Modal;
      visible={modalVisible}
      animationType="slide"
      transparent={true}
      onRequestClose={() => setModalVisible(false)}
    >
      <View style={styles.modalOverlay}>
        <View style={styles.modalContent}>
          <ScrollView style={styles.modalScrollView}>;
            <Text style={styles.modalTitle}>;

            </Text>;
            {// 观察记录};
            <View style={styles.section}>;
              <View style={styles.sectionHeader}>;
                <Text style={styles.sectionTitle}>观察记录</Text>;
                <TouchableOpacity style={styles.addObservationButton} onPress={addObservation}>;
                  <Text style={styles.addObservationButtonText}>+ 添加观察</Text>;
                </TouchableOpacity>;
              </View>;
              {formData.observations.map(observation, index) =>;)
                renderObservationForm(observation, index);
              )}
            </View>
            {// 诊断结论}
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>诊断结论</Text>
              <TextInput;
                style={[styles.input, styles.textArea]}
                value={formData.conclusion}
                onChangeText={(text) => setFormData({ ...formData, conclusion: text ;})}

                multiline;
                numberOfLines={4}
              />
            </View>
            {// 建议}
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>治疗建议</Text>
              <TextInput;
                style={[styles.input, styles.textArea]}
                value={formData.recommendations.join('\n')}
                onChangeText={(text) => setFormData({
                  ...formData,
                  recommendations: text.split('\n').filter(r => r.trim() !== '')
                ;})}

                multiline;
                numberOfLines={4}
              />
            </View>
            {// 可信度}
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>诊断可信度: {formData.confidence}%</Text>
              <View style={styles.confidenceSlider}>
                <TouchableOpacity;
                  style={styles.confidenceButton}
                  onPress={() => setFormData({ ...formData, confidence: Math.max(0, formData.confidence - 10) ;})}
                >
                  <Text style={styles.confidenceButtonText}>-</Text>
                </TouchableOpacity>
                <View style={styles.confidenceDisplay}>
                  <Text style={styles.confidenceText}>{formData.confidence}%</Text>
                </View>
                <TouchableOpacity;
                  style={styles.confidenceButton}
                  onPress={() => setFormData({ ...formData, confidence: Math.min(100, formData.confidence + 10) ;})}
                >
                  <Text style={styles.confidenceButtonText}>+</Text>
                </TouchableOpacity>
              </View>
            </View>
          </ScrollView>
          <View style={styles.modalButtons}>
            <TouchableOpacity;
              style={[styles.modalButton, styles.cancelButton]}
              onPress={() => setModalVisible(false)}
            >
              <Text style={styles.modalButtonText}>取消</Text>
            </TouchableOpacity>
            <TouchableOpacity;
              style={[styles.modalButton, styles.saveButton]}
              onPress={handleSaveDiagnosis}
            >
              <Text style={styles.modalButtonText}>保存</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>;
  );
  const renderRecentDiagnosis = () => {const recentDiagnosis = diagnosisData;
      .sort(a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
      .slice(0, 5);
    return (
  <View style={styles.recentDiagnosisContainer}>
        <Text style={styles.sectionTitle}>最近诊断记录</Text>
        {recentDiagnosis.length === 0 ? ()
          <Text style={styles.emptyText}>暂无诊断记录</Text>
        ) : (
          recentDiagnosis.map(diagnosis, index) => ())
            <View key={index} style={styles.diagnosisItem}>
              <View style={styles.diagnosisItemHeader}>
                <Text style={styles.diagnosisType}>
                  {getDiagnosisTypeLabel(diagnosis.diagnosisType)}
                </Text>
                <Text style={styles.diagnosisTime}>
                  {formatDate(diagnosis.timestamp)}
                </Text>
              </View>
              {diagnosis.conclusion && (;)
                <Text style={styles.diagnosisConclusion}>{diagnosis.conclusion}</Text>;
              )};
              <View style={styles.diagnosisStats}>;
                <Text style={styles.diagnosisStat}>;

                </Text>;
                <Text style={styles.diagnosisStat}>;
                  可信度: {Math.round(diagnosis.confidence || 0) * 100)}%;
                </Text>;
              </View>;
            </View>;
          ));
        )};
      </View>;
    );
  };
  return (
  <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>中医五诊</Text>
        <Text style={styles.subtitle}>望、闻、问、切、算综合诊断</Text>
      </View>
      <ScrollView;
        style={styles.scrollView}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />;
        };
      >;
        {// 五诊类型卡片};
        <View style={styles.diagnosisGrid}>;
          {Object.values(TCMDiagnosisType).map(renderDiagnosisTypeCard)};
        </View>;
        {// 最近诊断记录};
        {renderRecentDiagnosis()};
      </ScrollView>;
      {// 诊断记录模态框};
      {renderDiagnosisModal()};
    </View>;
  );
};
const styles = StyleSheet.create({
  container: {,
  flex: 1;
    backgroundColor: '#f5f5f5'
  ;},
  header: {,
  padding: 16;
    backgroundColor: '#fff';
    borderBottomWidth: 1;
    borderBottomColor: '#e0e0e0'
  ;},
  title: {,
  fontSize: 20;
    fontWeight: 'bold';
    color: '#333';
    marginBottom: 4;
  },
  subtitle: {,
  fontSize: 14;
    color: '#666'
  ;},
  scrollView: {,
  flex: 1;
  },
  diagnosisGrid: {,
  padding: 16;
  },
  diagnosisCard: {,
  backgroundColor: '#fff';
    borderRadius: 12;
    padding: 16;
    marginBottom: 16;
    shadowColor: '#000';
    shadowOffset: { width: 0, height: 2 ;},
    shadowOpacity: 0.1;
    shadowRadius: 4;
    elevation: 3;
  },
  cardHeader: {,
  flexDirection: 'row';
    justifyContent: 'space-between';
    alignItems: 'flex-start';
    marginBottom: 12;
  },
  cardTitle: {,
  fontSize: 18;
    fontWeight: 'bold';
    color: '#333';
    marginBottom: 4;
  },
  cardDescription: {,
  fontSize: 14;
    color: '#666';
    lineHeight: 20;
  },
  addButton: {,
  width: 32;
    height: 32;
    borderRadius: 16;
    backgroundColor: '#007AFF';
    justifyContent: 'center';
    alignItems: 'center'
  ;},
  addButtonText: {,
  color: '#fff';
    fontSize: 20;
    fontWeight: 'bold'
  ;},
  recentData: {,
  borderTopWidth: 1;
    borderTopColor: '#f0f0f0';
    paddingTop: 12;
  },
  recentDataTitle: {,
  fontSize: 14;
    fontWeight: '600';
    color: '#333';
    marginBottom: 4;
  },
  recentDataTime: {,
  fontSize: 12;
    color: '#666';
    marginBottom: 8;
  },
  recentDataConclusion: {,
  fontSize: 14;
    color: '#333';
    marginBottom: 8;
    lineHeight: 20;
  },
  observationCount: {,
  fontSize: 12;
    color: '#007AFF'
  ;},
  noData: {,
  borderTopWidth: 1;
    borderTopColor: '#f0f0f0';
    paddingTop: 12;
    alignItems: 'center'
  ;},
  noDataText: {,
  fontSize: 14;
    color: '#999';
    fontStyle: 'italic'
  ;},
  modalOverlay: {,
  flex: 1;
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center';
    alignItems: 'center'
  ;},
  modalContent: {,
  backgroundColor: '#fff';
    borderRadius: 12;
    width: '95%';
    maxHeight: '90%'
  ;},
  modalScrollView: {,
  maxHeight: '85%'
  ;},
  modalTitle: {,
  fontSize: 18;
    fontWeight: 'bold';
    color: '#333';
    padding: 20;
    paddingBottom: 0;
    textAlign: 'center'
  ;},
  section: {,
  padding: 20;
    paddingTop: 16;
  },
  sectionHeader: {,
  flexDirection: 'row';
    justifyContent: 'space-between';
    alignItems: 'center';
    marginBottom: 16;
  },
  sectionTitle: {,
  fontSize: 16;
    fontWeight: 'bold';
    color: '#333'
  ;},
  addObservationButton: {,
  backgroundColor: '#4CAF50';
    paddingHorizontal: 12;
    paddingVertical: 6;
    borderRadius: 6;
  },
  addObservationButtonText: {,
  color: '#fff';
    fontSize: 12;
    fontWeight: '500'
  ;},
  observationForm: {,
  backgroundColor: '#f8f9fa';
    borderRadius: 8;
    padding: 16;
    marginBottom: 16;
  },
  observationHeader: {,
  flexDirection: 'row';
    justifyContent: 'space-between';
    alignItems: 'center';
    marginBottom: 16;
  },
  observationTitle: {,
  fontSize: 14;
    fontWeight: '600';
    color: '#333'
  ;},
  removeButton: {,
  width: 24;
    height: 24;
    borderRadius: 12;
    backgroundColor: '#f44336';
    justifyContent: 'center';
    alignItems: 'center'
  ;},
  removeButtonText: {,
  color: '#fff';
    fontSize: 16;
    fontWeight: 'bold'
  ;},
  formRow: {,
  marginBottom: 12;
  },
  label: {,
  fontSize: 14;
    fontWeight: '500';
    color: '#333';
    marginBottom: 8;
  },
  input: {,
  borderWidth: 1;
    borderColor: '#ddd';
    borderRadius: 8;
    paddingHorizontal: 12;
    paddingVertical: 10;
    fontSize: 16;
    backgroundColor: '#fff'
  ;},
  textArea: {,
  height: 80;
    textAlignVertical: 'top'
  ;},
  selectButton: {,
  borderWidth: 1;
    borderColor: '#ddd';
    borderRadius: 8;
    backgroundColor: '#fff';
    paddingHorizontal: 12;
    paddingVertical: 10;
  },
  selectText: {,
  fontSize: 16;
    color: '#333'
  ;},
  severityButtons: {,
  flexDirection: 'row';
    justifyContent: 'space-between'
  ;},
  severityButton: {,
  flex: 1;
    paddingVertical: 8;
    marginHorizontal: 4;
    borderRadius: 6;
    backgroundColor: '#f0f0f0';
    alignItems: 'center'
  ;},
  severityButtonActive: {,
  backgroundColor: '#007AFF'
  ;},
  severityButtonText: {,
  fontSize: 14;
    color: '#666';
    fontWeight: '500'
  ;},
  severityButtonTextActive: {,
  color: '#fff'
  ;},
  confidenceSlider: {,
  flexDirection: 'row';
    alignItems: 'center';
    justifyContent: 'center';
    marginTop: 8;
  },
  confidenceButton: {,
  width: 40;
    height: 40;
    borderRadius: 20;
    backgroundColor: '#007AFF';
    justifyContent: 'center';
    alignItems: 'center'
  ;},
  confidenceButtonText: {,
  color: '#fff';
    fontSize: 20;
    fontWeight: 'bold'
  ;},
  confidenceDisplay: {,
  marginHorizontal: 20;
    paddingHorizontal: 20;
    paddingVertical: 10;
    backgroundColor: '#f0f0f0';
    borderRadius: 8;
  },
  confidenceText: {,
  fontSize: 16;
    fontWeight: 'bold';
    color: '#333'
  ;},
  modalButtons: {,
  flexDirection: 'row';
    justifyContent: 'space-between';
    padding: 20;
    borderTopWidth: 1;
    borderTopColor: '#f0f0f0'
  ;},
  modalButton: {,
  flex: 1;
    paddingVertical: 12;
    borderRadius: 8;
    marginHorizontal: 8;
  },
  cancelButton: {,
  backgroundColor: '#666'
  ;},
  saveButton: {,
  backgroundColor: '#007AFF'
  ;},
  modalButtonText: {,
  color: '#fff';
    fontSize: 16;
    fontWeight: '500';
    textAlign: 'center'
  ;},
  recentDiagnosisContainer: {,
  margin: 16;
    backgroundColor: '#fff';
    borderRadius: 12;
    padding: 16;
    shadowColor: '#000';
    shadowOffset: { width: 0, height: 2 ;},
    shadowOpacity: 0.1;
    shadowRadius: 4;
    elevation: 3;
  },
  emptyText: {,
  textAlign: 'center';
    color: '#666';
    fontSize: 14;
    fontStyle: 'italic'
  ;},
  diagnosisItem: {,
  borderBottomWidth: 1;
    borderBottomColor: '#f0f0f0';
    paddingVertical: 12;
  },
  diagnosisItemHeader: {,
  flexDirection: 'row';
    justifyContent: 'space-between';
    alignItems: 'center';
    marginBottom: 8;
  },
  diagnosisType: {,
  fontSize: 16;
    fontWeight: 'bold';
    color: '#333'
  ;},
  diagnosisTime: {,
  fontSize: 12;
    color: '#666';
  },diagnosisConclusion: {fontSize: 14,color: '#333',marginBottom: 8,lineHeight: 20;
  },diagnosisStats: {,
  flexDirection: "row";
      justifyContent: 'space-between';
  },diagnosisStat: {fontSize: 12,color: '#666';
  };
});