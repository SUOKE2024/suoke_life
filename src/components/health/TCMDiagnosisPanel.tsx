import React, { useState, useEffect } from "react";";
import {import {View;,}Text,;
StyleSheet,;
ScrollView,;
TouchableOpacity,;
Alert,;
RefreshControl,;
Modal,";"";
}
  TextInput;'}'';'';
} from "react-native";";
healthDataService,;
TCMDiagnosisData,;
TCMDiagnosisType,;
TCMObservation,';,'';
DataSource;';'';
} from "../../services/healthDataService";""/;,"/g"/;
interface TCMDiagnosisPanelProps {}}
}
  const userId = string;}
}
interface DiagnosisFormData {diagnosisType: TCMDiagnosisType}observations: TCMObservation[],;
conclusion: string,;
recommendations: string[],;
}
}
  const confidence = number;}
}
export const TCMDiagnosisPanel: React.FC<TCMDiagnosisPanelProps> = ({ userId ;}) => {const [diagnosisData, setDiagnosisData] = useState<TCMDiagnosisData[]>([]);,}const [loading, setLoading] = useState(false);
const [refreshing, setRefreshing] = useState(false);
const [modalVisible, setModalVisible] = useState(false);';,'';
const [selectedDiagnosisType, setSelectedDiagnosisType] = useState<TCMDiagnosisType>(TCMDiagnosisType.LOOK);';'';
}
  const [formData, setFormData] = useState<DiagnosisFormData>({diagnosisType: TCMDiagnosisType.LOOK,observations: [],conclusion: ',recommendations: [],confidence: 80;)'}'';'';
  });
useEffect() => {}}
    loadDiagnosisData();}
  }, [userId]);
const loadDiagnosisData = async () => {try {setLoading(true);,}const response = await healthDataService.getTCMDiagnosis(userId);
if (response.data) {}}
        setDiagnosisData(response.data);}
      }
    } catch (error) {}}
}
    } finally {}}
      setLoading(false);}
    }
  };
const onRefresh = async () => {setRefreshing(true);,}const await = loadDiagnosisData();
}
    setRefreshing(false);}
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
const handleAddDiagnosis = useCallback((type: TCMDiagnosisType) => {setSelectedDiagnosisType(type);,}setFormData({)      diagnosisType: type,';,}observations: [],';,'';
conclusion: ';',')'';
recommendations: [],);
}
      const confidence = 80;)}
    });
setModalVisible(true);
  };';,'';
const: addObservation = useCallback(() => {const newObservation: TCMObservation = {,';,}category: "";","";"";
}
      value: '',description: ',severity: 'mild',confidence: 80;'}'';'';
    };
setFormData({));}      ...formData,);
}
      observations: [...formData.observations, newObservation])}
    ;});
  };
updateObservation: useCallback((index: number, field: keyof TCMObservation, value: any) => {const updatedObservations = [...formData.observations];,}updatedObservations[index] = {...updatedObservations[index],;}}
      [field]: value;}
    };
setFormData({));}      ...formData,);
}
      const observations = updatedObservations;)}
    });
  };
removeObservation: useCallback((index: number) => {const updatedObservations = formData.observations.filter(_, i) => i !== index);,}setFormData({);}      ...formData,);
}
      const observations = updatedObservations;)}
    });
  };
return;';'';
      }';,'';
diagnosisToSave: {userId,diagnosisType: formData.diagnosisType,observations: formData.observations,conclusion: formData.conclusion,recommendations: formData.recommendations.filter(r => r.trim() !== '),timestamp: new Date().toISOString(),confidence: formData.confidence / 100,metadata: {source: 'manual_input';'}''/;'/g'/;
        };
      };
const await = healthDataService.createTCMDiagnosis(diagnosisToSave);
setModalVisible(false);
const await = loadDiagnosisData();
    } catch (error) {}}
}
    }';'';
  };';,'';
const formatDate = (timestamp: string): string => {return new Date(timestamp).toLocaleString('zh-CN');'}'';'';
  };
const renderDiagnosisTypeCard = useCallback((type: TCMDiagnosisType) => {const recentData = diagnosisData;}      .filter(d => d.diagnosisType === type);
      .sort(a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
}
      .slice(0, 1)[0];}
    return (<View key={type} style={styles.diagnosisCard}>);
        <View style={styles.cardHeader}>);
          <View>);
            <Text style={styles.cardTitle}>{getDiagnosisTypeLabel(type)}</Text>/;/g/;
            <Text style={styles.cardDescription}>{getDiagnosisTypeDescription(type)}</Text>/;/g/;
          </View>/;/g/;
          <TouchableOpacity;  />/;,/g/;
style={styles.addButton}
            onPress={() => handleAddDiagnosis(type)}
          >;
            <Text style={styles.addButtonText}>+</Text>/;/g/;
          </TouchableOpacity>/;/g/;
        </View>/;/g/;
        {recentData ? ()}
          <View style={styles.recentData}>;
            <Text style={styles.recentDataTitle}>最近记录</Text>;/;/g/;
            <Text style={styles.recentDataTime}>{formatDate(recentData.timestamp)}</Text>;/;/g/;
            {recentData.conclusion && (;)}
              <Text style={styles.recentDataConclusion}>{recentData.conclusion}</Text>;/;/g/;
            )};
            <Text style={styles.observationCount}>;

            </Text>;/;/g/;
          </View>;/;/g/;
        ) : (;)          <View style={styles.noData}>;);
            <Text style={styles.noDataText}>暂无记录</Text>;)/;/g/;
          </View>;)/;/g/;
        )};
      </View>;/;/g/;
    );
  };
const: renderObservationForm = (observation: TCMObservation, index: number) => ();
    <View key={index;} style={styles.observationForm}>;
      <View style={styles.observationHeader}>;
        <Text style={styles.observationTitle}>观察记录 {index + 1}</Text>/;/g/;
        <TouchableOpacity;  />/;,/g/;
style={styles.removeButton}
          onPress={() => removeObservation(index)}
        >;
          <Text style={styles.removeButtonText}>×</Text>/;/g/;
        </TouchableOpacity>/;/g/;
      </View>/;/g/;
      <View style={styles.formRow}>;
        <Text style={styles.label}>类别</Text>/;/g/;
        <TouchableOpacity style={styles.selectButton}>;
          <Text style={styles.selectText}>;

          </Text>/;/g/;
        </TouchableOpacity>/;/g/;
      </View>/;/g/;
      <View style={styles.formRow}>;
        <Text style={styles.label}>观察值</Text>/;/g/;
        <TextInput;  />/;,/g/;
style={styles.input}';,'';
value={observation.value.toString()}';,'';
onChangeText={(text) => updateObservation(index, 'value', text)}';'';

        />/;/g/;
      </View>/;/g/;
      <View style={styles.formRow}>;
        <Text style={styles.label}>描述</Text>/;/g/;
        <TextInput;  />/;,/g/;
style={[styles.input, styles.textArea]}';,'';
value={observation.description}';,'';
onChangeText={(text) => updateObservation(index, 'description', text)}';,'';
multiline;
numberOfLines={3}
        />/;/g/;
      </View>/;/g/;
      <View style={styles.formRow}>;
        <Text style={styles.label}>严重程度</Text>'/;'/g'/;
        <View style={styles.severityButtons}>';'';
          {(["mild",moderate', 'severe'] as const).map(severity) => ()'';}}'';
            <TouchableOpacity;}  />/;,/g/;
key={severity}
              style={}[;]}
                styles.severityButton,observation.severity === severity && styles.severityButtonActive;}';'';
];
              ]}};';,'';
onPress={() => updateObservation(index, 'severity', severity)};';'';
            >;
              <Text style={ />/;}[;];/g/;
}
                styles.severityButtonText,observation.severity === severity && styles.severityButtonTextActive;}
];
              ]}}>;

              </Text>;/;/g/;
            </TouchableOpacity>;/;/g/;
          ))};
        </View>;/;/g/;
      </View>;/;/g/;
    </View>;/;/g/;
  );
const renderDiagnosisModal = () => (<Modal;'  />/;,)visible={modalVisible}')'';,'/g'/;
animationType="slide")";
transparent={true});
onRequestClose={() => setModalVisible(false)}
    >;
      <View style={styles.modalOverlay}>;
        <View style={styles.modalContent}>;
          <ScrollView style={styles.modalScrollView}>;
            <Text style={styles.modalTitle}>;

            </Text>;/;/g/;
            {// 观察记录};/;/g/;
            <View style={styles.section}>;
              <View style={styles.sectionHeader}>;
                <Text style={styles.sectionTitle}>观察记录</Text>;/;/g/;
                <TouchableOpacity style={styles.addObservationButton} onPress={addObservation}>;
                  <Text style={styles.addObservationButtonText}>+ 添加观察</Text>;/;/g/;
                </TouchableOpacity>;/;/g/;
              </View>;/;/g/;
              {formData.observations.map(observation, index) =>;);}}
                renderObservationForm(observation, index);}
              )}
            </View>/;/g/;
            {// 诊断结论}/;/g/;
            <View style={styles.section}>;
              <Text style={styles.sectionTitle}>诊断结论</Text>/;/g/;
              <TextInput;  />/;,/g/;
style={[styles.input, styles.textArea]}
                value={formData.conclusion}
                onChangeText={(text) => setFormData({ ...formData, conclusion: text ;})}

                multiline;
numberOfLines={4}
              />/;/g/;
            </View>/;/g/;
            {// 建议}/;/g/;
            <View style={styles.section}>;
              <Text style={styles.sectionTitle}>治疗建议</Text>/;/g/;
              <TextInput;"  />/;,"/g"/;
style={[styles.input, styles.textArea]}";,"";
value={formData.recommendations.join('\n')}';,'';
onChangeText={(text) => setFormData({)';}                  ...formData,)';'';
}
                  recommendations: text.split('\n').filter(r => r.trim() !== ')'}'';'';
                ;})}

                multiline;
numberOfLines={4}
              />/;/g/;
            </View>/;/g/;
            {// 可信度}/;/g/;
            <View style={styles.section}>;
              <Text style={styles.sectionTitle}>诊断可信度: {formData.confidence}%</Text>/;/g/;
              <View style={styles.confidenceSlider}>;
                <TouchableOpacity;  />/;,/g/;
style={styles.confidenceButton}
                  onPress={() => setFormData({ ...formData, confidence: Math.max(0, formData.confidence - 10) ;})}
                >;
                  <Text style={styles.confidenceButtonText}>-</Text>/;/g/;
                </TouchableOpacity>/;/g/;
                <View style={styles.confidenceDisplay}>;
                  <Text style={styles.confidenceText}>{formData.confidence}%</Text>/;/g/;
                </View>/;/g/;
                <TouchableOpacity;  />/;,/g/;
style={styles.confidenceButton}
                  onPress={() => setFormData({ ...formData, confidence: Math.min(100, formData.confidence + 10) ;})}
                >;
                  <Text style={styles.confidenceButtonText}>+</Text>/;/g/;
                </TouchableOpacity>/;/g/;
              </View>/;/g/;
            </View>/;/g/;
          </ScrollView>/;/g/;
          <View style={styles.modalButtons}>;
            <TouchableOpacity;  />/;,/g/;
style={[styles.modalButton, styles.cancelButton]}
              onPress={() => setModalVisible(false)}
            >;
              <Text style={styles.modalButtonText}>取消</Text>/;/g/;
            </TouchableOpacity>/;/g/;
            <TouchableOpacity;  />/;,/g/;
style={[styles.modalButton, styles.saveButton]}
              onPress={handleSaveDiagnosis}
            >;
              <Text style={styles.modalButtonText}>保存</Text>/;/g/;
            </TouchableOpacity>/;/g/;
          </View>/;/g/;
        </View>/;/g/;
      </View>/;/g/;
    </Modal>;/;/g/;
  );
const renderRecentDiagnosis = useCallback(() => {const recentDiagnosis = diagnosisData;}      .sort(a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
}
      .slice(0, 5);}
    return (<View style={styles.recentDiagnosisContainer}>);
        <Text style={styles.sectionTitle}>最近诊断记录</Text>)/;/g/;
        {recentDiagnosis.length === 0 ? ()}
          <Text style={styles.emptyText}>暂无诊断记录</Text>/;/g/;
        ) : ();
recentDiagnosis.map(diagnosis, index) => ());
            <View key={index} style={styles.diagnosisItem}>;
              <View style={styles.diagnosisItemHeader}>;
                <Text style={styles.diagnosisType}>;
                  {getDiagnosisTypeLabel(diagnosis.diagnosisType)}
                </Text>/;/g/;
                <Text style={styles.diagnosisTime}>;
                  {formatDate(diagnosis.timestamp)}
                </Text>/;/g/;
              </View>/;/g/;
              {diagnosis.conclusion && (;)}
                <Text style={styles.diagnosisConclusion}>{diagnosis.conclusion}</Text>;/;/g/;
              )};
              <View style={styles.diagnosisStats}>;
                <Text style={styles.diagnosisStat}>;

                </Text>;/;/g/;
                <Text style={styles.diagnosisStat}>;
                  可信度: {Math.round(diagnosis.confidence || 0) * 100)}%;
                </Text>;/;/g/;
              </View>;/;/g/;
            </View>;/;/g/;
          ));
        )};
      </View>;/;/g/;
    );
  };
return (<View style={styles.container}>;)      <View style={styles.header}>;
        <Text style={styles.title}>中医五诊</Text>/;/g/;
        <Text style={styles.subtitle}>望、闻、问、切、算综合诊断</Text>/;/g/;
      </View>/;/g/;
      <ScrollView;  />/;,/g/;
style={styles.scrollView}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh}  />;/;/g/;
        };
      >;);
        {// 五诊类型卡片};)/;/g/;
        <View style={styles.diagnosisGrid}>;);
          {Object.values(TCMDiagnosisType).map(renderDiagnosisTypeCard)};
        </View>;/;/g/;
        {// 最近诊断记录};/;/g/;
        {renderRecentDiagnosis()};
      </ScrollView>;/;/g/;
      {// 诊断记录模态框};/;/g/;
      {renderDiagnosisModal()};
    </View>;/;/g/;
  );
};
const  styles = StyleSheet.create({)container: {,';,}flex: 1,';'';
}
    const backgroundColor = '#f5f5f5'}'';'';
  ;}
header: {,';,}padding: 16,';,'';
backgroundColor: '#fff';','';
borderBottomWidth: 1,';'';
}
    const borderBottomColor = '#e0e0e0'}'';'';
  ;}
title: {,';,}fontSize: 20,';,'';
fontWeight: 'bold';','';
color: '#333';','';'';
}
    const marginBottom = 4;}
  }
subtitle: {,';,}fontSize: 14,';'';
}
    const color = '#666'}'';'';
  ;}
scrollView: {,;}}
  const flex = 1;}
  }
diagnosisGrid: {,;}}
  const padding = 16;}
  },';,'';
diagnosisCard: {,';,}backgroundColor: '#fff';','';
borderRadius: 12,;
padding: 16,';,'';
marginBottom: 16,';'';
}
    shadowColor: '#000';','}'';
shadowOffset: { width: 0, height: 2 ;}
shadowOpacity: 0.1,;
shadowRadius: 4,;
const elevation = 3;
  },';,'';
cardHeader: {,';,}flexDirection: 'row';','';
justifyContent: 'space-between';','';
alignItems: 'flex-start';','';'';
}
    const marginBottom = 12;}
  }
cardTitle: {,';,}fontSize: 18,';,'';
fontWeight: 'bold';','';
color: '#333';','';'';
}
    const marginBottom = 4;}
  }
cardDescription: {,';,}fontSize: 14,';,'';
color: '#666';','';'';
}
    const lineHeight = 20;}
  }
addButton: {width: 32,;
height: 32,';,'';
borderRadius: 16,';,'';
backgroundColor: '#007AFF';','';
justifyContent: 'center';','';'';
}
    const alignItems = 'center'}'';'';
  ;},';,'';
addButtonText: {,';,}color: '#fff';','';
fontSize: 20,';'';
}
    const fontWeight = 'bold'}'';'';
  ;}
recentData: {,';,}borderTopWidth: 1,';,'';
borderTopColor: '#f0f0f0';','';'';
}
    const paddingTop = 12;}
  }
recentDataTitle: {,';,}fontSize: 14,';,'';
fontWeight: '600';','';
color: '#333';','';'';
}
    const marginBottom = 4;}
  }
recentDataTime: {,';,}fontSize: 12,';,'';
color: '#666';','';'';
}
    const marginBottom = 8;}
  }
recentDataConclusion: {,';,}fontSize: 14,';,'';
color: '#333';','';
marginBottom: 8,;
}
    const lineHeight = 20;}
  }
observationCount: {,';,}fontSize: 12,';'';
}
    const color = '#007AFF'}'';'';
  ;}
noData: {,';,}borderTopWidth: 1,';,'';
borderTopColor: '#f0f0f0';','';
paddingTop: 12,';'';
}
    const alignItems = 'center'}'';'';
  ;}
noDataText: {,';,}fontSize: 14,';,'';
color: '#999';','';'';
}
    const fontStyle = 'italic'}'';'';
  ;},);
modalOverlay: {,)';,}flex: 1,)';,'';
backgroundColor: 'rgba(0, 0, 0, 0.5)',';,'';
justifyContent: 'center';','';'';
}
    const alignItems = 'center'}'';'';
  ;},';,'';
modalContent: {,';,}backgroundColor: '#fff';','';
borderRadius: 12,';,'';
width: '95%';','';'';
}
    const maxHeight = '90%'}'';'';
  ;},';,'';
modalScrollView: {,';}}'';
  const maxHeight = '85%'}'';'';
  ;}
modalTitle: {,';,}fontSize: 18,';,'';
fontWeight: 'bold';','';
color: '#333';','';
padding: 20,';,'';
paddingBottom: 0,';'';
}
    const textAlign = 'center'}'';'';
  ;}
section: {padding: 20,;
}
    const paddingTop = 16;}
  },';,'';
sectionHeader: {,';,}flexDirection: 'row';','';
justifyContent: 'space-between';','';
alignItems: 'center';','';'';
}
    const marginBottom = 16;}
  }
sectionTitle: {,';,}fontSize: 16,';,'';
fontWeight: 'bold';','';'';
}
    const color = '#333'}'';'';
  ;},';,'';
addObservationButton: {,';,}backgroundColor: '#4CAF50';','';
paddingHorizontal: 12,;
paddingVertical: 6,;
}
    const borderRadius = 6;}
  },';,'';
addObservationButtonText: {,';,}color: '#fff';','';
fontSize: 12,';'';
}
    const fontWeight = '500'}'';'';
  ;},';,'';
observationForm: {,';,}backgroundColor: '#f8f9fa';','';
borderRadius: 8,;
padding: 16,;
}
    const marginBottom = 16;}
  },';,'';
observationHeader: {,';,}flexDirection: 'row';','';
justifyContent: 'space-between';','';
alignItems: 'center';','';'';
}
    const marginBottom = 16;}
  }
observationTitle: {,';,}fontSize: 14,';,'';
fontWeight: '600';','';'';
}
    const color = '#333'}'';'';
  ;}
removeButton: {width: 24,;
height: 24,';,'';
borderRadius: 12,';,'';
backgroundColor: '#f44336';','';
justifyContent: 'center';','';'';
}
    const alignItems = 'center'}'';'';
  ;},';,'';
removeButtonText: {,';,}color: '#fff';','';
fontSize: 16,';'';
}
    const fontWeight = 'bold'}'';'';
  ;}
formRow: {,;}}
  const marginBottom = 12;}
  }
label: {,';,}fontSize: 14,';,'';
fontWeight: '500';','';
color: '#333';','';'';
}
    const marginBottom = 8;}
  }
input: {,';,}borderWidth: 1,';,'';
borderColor: '#ddd';','';
borderRadius: 8,;
paddingHorizontal: 12,;
paddingVertical: 10,';,'';
fontSize: 16,';'';
}
    const backgroundColor = '#fff'}'';'';
  ;}
textArea: {,';,}height: 80,';'';
}
    const textAlignVertical = 'top'}'';'';
  ;}
selectButton: {,';,}borderWidth: 1,';,'';
borderColor: '#ddd';','';
borderRadius: 8,';,'';
backgroundColor: '#fff';','';
paddingHorizontal: 12,;
}
    const paddingVertical = 10;}
  }
selectText: {,';,}fontSize: 16,';'';
}
    const color = '#333'}'';'';
  ;},';,'';
severityButtons: {,';,}flexDirection: 'row';','';'';
}
    const justifyContent = 'space-between'}'';'';
  ;}
severityButton: {flex: 1,;
paddingVertical: 8,;
marginHorizontal: 4,';,'';
borderRadius: 6,';,'';
backgroundColor: '#f0f0f0';','';'';
}
    const alignItems = 'center'}'';'';
  ;},';,'';
severityButtonActive: {,';}}'';
  const backgroundColor = '#007AFF'}'';'';
  ;}
severityButtonText: {,';,}fontSize: 14,';,'';
color: '#666';','';'';
}
    const fontWeight = '500'}'';'';
  ;},';,'';
severityButtonTextActive: {,';}}'';
  const color = '#fff'}'';'';
  ;},';,'';
confidenceSlider: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';
justifyContent: 'center';','';'';
}
    const marginTop = 8;}
  }
confidenceButton: {width: 40,;
height: 40,';,'';
borderRadius: 20,';,'';
backgroundColor: '#007AFF';','';
justifyContent: 'center';','';'';
}
    const alignItems = 'center'}'';'';
  ;},';,'';
confidenceButtonText: {,';,}color: '#fff';','';
fontSize: 20,';'';
}
    const fontWeight = 'bold'}'';'';
  ;}
confidenceDisplay: {marginHorizontal: 20,;
paddingHorizontal: 20,';,'';
paddingVertical: 10,';,'';
backgroundColor: '#f0f0f0';','';'';
}
    const borderRadius = 8;}
  }
confidenceText: {,';,}fontSize: 16,';,'';
fontWeight: 'bold';','';'';
}
    const color = '#333'}'';'';
  ;},';,'';
modalButtons: {,';,}flexDirection: 'row';','';
justifyContent: 'space-between';','';
padding: 20,';,'';
borderTopWidth: 1,';'';
}
    const borderTopColor = '#f0f0f0'}'';'';
  ;}
modalButton: {flex: 1,;
paddingVertical: 12,;
borderRadius: 8,;
}
    const marginHorizontal = 8;}
  },';,'';
cancelButton: {,';}}'';
  const backgroundColor = '#666'}'';'';
  ;},';,'';
saveButton: {,';}}'';
  const backgroundColor = '#007AFF'}'';'';
  ;},';,'';
modalButtonText: {,';,}color: '#fff';','';
fontSize: 16,';,'';
fontWeight: '500';','';'';
}
    const textAlign = 'center'}'';'';
  ;}
recentDiagnosisContainer: {,';,}margin: 16,';,'';
backgroundColor: '#fff';','';
borderRadius: 12,';,'';
padding: 16,';'';
}
    shadowColor: '#000';','}'';
shadowOffset: { width: 0, height: 2 ;}
shadowOpacity: 0.1,;
shadowRadius: 4,;
const elevation = 3;
  },';,'';
emptyText: {,';,}textAlign: 'center';','';
color: '#666';','';
fontSize: 14,';'';
}
    const fontStyle = 'italic'}'';'';
  ;}
diagnosisItem: {,';,}borderBottomWidth: 1,';,'';
borderBottomColor: '#f0f0f0';','';'';
}
    const paddingVertical = 12;}
  },';,'';
diagnosisItemHeader: {,';,}flexDirection: 'row';','';
justifyContent: 'space-between';','';
alignItems: 'center';','';'';
}
    const marginBottom = 8;}
  }
diagnosisType: {,';,}fontSize: 16,';,'';
fontWeight: 'bold';','';'';
}
    const color = '#333'}'';'';
  ;}
diagnosisTime: {,';,}fontSize: 12,';'';
}
    const color = '#666';'}'';'';
  },diagnosisConclusion: {fontSize: 14,color: '#333',marginBottom: 8,lineHeight: 20;'}'';'';
  },diagnosisStats: {,';,}flexDirection: "row";","";"";
}
      const justifyContent = 'space-between';'}'';'';
  },diagnosisStat: {fontSize: 12,color: '#666';'}'';'';
  };';'';
});