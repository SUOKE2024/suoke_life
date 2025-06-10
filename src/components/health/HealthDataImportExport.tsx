import React, { useState } from "react";";
import {import {View;,}Text,;
StyleSheet,;
ScrollView,;
TouchableOpacity,;
Alert,;
Modal,";"";
}
  ActivityIndicator;'}'';'';
} from "react-native";";
healthDataService,;
ExportFormat,';,'';
ImportFormat;';'';
} from "../../services/healthDataService";""/;,"/g"/;
interface HealthDataImportExportProps {}}
}
  const userId = string;}
}
export const HealthDataImportExport: React.FC<HealthDataImportExportProps> = ({ userId ;}) => {const [loading, setLoading] = useState(false);';,}const [modalVisible, setModalVisible] = useState(false);';,'';
const [modalType, setModalType] = useState<'export' | 'import'>('export');';,'';
const [selectedFormat, setSelectedFormat] = useState<ExportFormat | ImportFormat>(ExportFormat.JSON);
const exportFormats = [;];

];
  ];
const importFormats = [;];

];
  ];
const handleExport = async (format: ExportFormat) => {try {setLoading(true);,}const endDate = new Date().toISOString();
const startDate = new Date();
startDate.setFullYear(startDate.getFullYear() - 1); // 导出一年的数据/;,/g/;
const response = await healthDataService.exportHealthData(;);
userId,format,startDate.toISOString(),endDate;
      );
if (response.data) {}}
        // 这里可以添加文件下载或分享逻辑}/;/g/;
      }
    } catch (error) {}}
}
    } finally {setLoading(false);}}
      setModalVisible(false);}
    }
  };
const handleImport = async (format: ImportFormat) => {try {setLoading(true);}      // 这里应该打开文件选择器/;/g/;

      // 模拟导入过程/;/g/;
}
      // response: await healthDataService.importHealthData(userId, format, fileData);}/;/g/;
    } catch (error) {}}
}
    } finally {setLoading(false);}}
      setModalVisible(false);}
    }';'';
  };';,'';
const openExportModal = useCallback(() => {setModalType('export');';,}setSelectedFormat(ExportFormat.JSON);'';
}
    setModalVisible(true);}';'';
  };';,'';
const openImportModal = useCallback(() => {setModalType('import');';,}setSelectedFormat(ImportFormat.JSON);'';
}
    setModalVisible(true);}
  };
const: renderFormatOption = (format: any, label: string, description: string) => ();
    <TouchableOpacity;  />/;,/g/;
key={format}
      style={[;,]styles.formatOption,;}}
        selectedFormat === format && styles.formatOptionSelected;}
];
      ]}}
      onPress={() => setSelectedFormat(format)}
    >;
      <View style={styles.formatOptionContent}>;
        <Text style={ />/;}[;,]styles.formatLabel,;/g/;
}
          selectedFormat === format && styles.formatLabelSelected;}
];
        ]}}>;
          {label};
        </Text>;/;/g/;
        <Text style={ />/;}[;];/g/;
}
          styles.formatDescription,selectedFormat === format && styles.formatDescriptionSelected;}
];
        ]}}>;
          {description};
        </Text>;/;/g/;
      </View>;/;/g/;
      <View style={ />/;}[;];/g/;
}
        styles.radioButton,selectedFormat === format && styles.radioButtonSelected;}
];
      ]}}>;
        {selectedFormat === format && <View style={styles.radioButtonInner}>};
      </View>;/;/g/;
    </TouchableOpacity>;/;/g/;
  );
const renderModal = () => (<Modal;'  />/;,)visible={modalVisible}')'';,'/g'/;
animationType="slide")";
transparent={true});
onRequestClose={() => setModalVisible(false)}
    >;
      <View style={styles.modalOverlay}>;
        <View style={styles.modalContent}>;
          <View style={styles.modalHeader}>;
            <Text style={styles.modalTitle}>;

            </Text>;/;/g/;
            <TouchableOpacity;  />/;,/g/;
style={styles.closeButton};
onPress={() => setModalVisible(false)};
            >;
              <Text style={styles.closeButtonText}>×</Text>;/;/g/;
            </TouchableOpacity>;/;/g/;
          </View>;/;/g/;
          <ScrollView style={styles.modalScrollView}>;";"";
            <Text style={styles.sectionTitle}>选择格式</Text>;"/;"/g"/;
            {modalType === 'export' ;';}              ? exportFormats.map(format => ;);,'';
renderFormatOption(format.value, format.label, format.description);
                );
              : importFormats.map(format =>);
renderFormatOption(format.value, format.label, format.description);
}
                )}';'';
            }';'';
            {modalType === 'export'  && <View style={styles.exportOptions}>';'';
                <Text style={styles.sectionTitle}>导出选项</Text>/;/g/;
                <View style={styles.optionItem}>;
                  <Text style={styles.optionLabel}>数据范围</Text>/;/g/;
                  <Text style={styles.optionValue}>最近一年</Text>/;/g/;
                </View>/;/g/;
                <View style={styles.optionItem}>;
                  <Text style={styles.optionLabel}>包含内容</Text>/;/g/;
                  <Text style={styles.optionValue}>所有健康数据</Text>/;/g/;
                </View>/;/g/;
              </View>'/;'/g'/;
            )}';'';
            {modalType === 'import'  && <View style={styles.importOptions}>';'';
                <Text style={styles.sectionTitle}>导入说明</Text>/;/g/;
                <Text style={styles.importNote}>;

                </Text>/;/g/;
              </View>/;/g/;
            )}
          </ScrollView>/;/g/;
          <View style={styles.modalButtons}>;
            <TouchableOpacity;  />/;,/g/;
style={[styles.modalButton, styles.cancelButton]}
              onPress={() => setModalVisible(false)}
            >;
              <Text style={styles.modalButtonText}>取消</Text>/;/g/;
            </TouchableOpacity>/;/g/;
            <TouchableOpacity;  />/;,/g/;
style={[styles.modalButton, styles.confirmButton]}';,'';
onPress={() => {';}}'';
                if (modalType === 'export') {handleExport(selectedFormat as ExportFormat);'}'';'';
                } else {}}
                  handleImport(selectedFormat as ImportFormat);}
                }
              }}
              disabled={loading}
            >';'';
              {loading ? ()';}}'';
                <ActivityIndicator color="#fff" size="small"  />"}""/;"/g"/;
              ) : (<Text style={styles.modalButtonText}>);
);
                </Text>)/;/g/;
              )}
            </TouchableOpacity>/;/g/;
          </View>/;/g/;
        </View>/;/g/;
      </View>/;/g/;
    </Modal>/;/g/;
  );
const  renderQuickActions = () => (<View style={styles.quickActionsSection}>;)      <Text style={styles.sectionTitle}>快速操作</Text>/;/g/;
      <View style={styles.quickActionsGrid}>";"";
        <TouchableOpacity style={styles.quickActionCard} onPress={openExportModal}>";"";
          <View style={[styles.quickActionIcon, { backgroundColor: '#4CAF50' ;}}]}>';'';
            <Text style={styles.quickActionIconText}>↗</Text>/;/g/;
          </View>/;/g/;
          <Text style={styles.quickActionTitle}>导出数据</Text>/;/g/;
          <Text style={styles.quickActionDescription}>备份您的健康数据</Text>/;/g/;
        </TouchableOpacity>'/;'/g'/;
        <TouchableOpacity style={styles.quickActionCard} onPress={openImportModal}>';'';
          <View style={[styles.quickActionIcon, { backgroundColor: '#2196F3' ;}}]}>';'';
            <Text style={styles.quickActionIconText}>↙</Text>/;/g/;
          </View>/;/g/;
          <Text style={styles.quickActionTitle}>导入数据</Text>/;/g/;
          <Text style={styles.quickActionDescription}>从其他平台导入数据</Text>/;/g/;
        </TouchableOpacity>/;/g/;
        <TouchableOpacity;  />/;,/g/;
style={styles.quickActionCard}
';'';
        >';'';
          <View style={[styles.quickActionIcon, { backgroundColor: '#FF9800' ;}}]}>';'';
            <Text style={styles.quickActionIconText}>⟲</Text>/;/g/;
          </View>/;/g/;
          <Text style={styles.quickActionTitle}>同步数据</Text>;/;/g/;
          <Text style={styles.quickActionDescription}>与云端同步</Text>;/;/g/;
        </TouchableOpacity>;/;/g/;
        <TouchableOpacity ;  />/;,/g/;
style={styles.quickActionCard};
';'';
        >;';'';
          <View style={[styles.quickActionIcon, { backgroundColor: '#9C27B0' ;}}]}>;';'';
            <Text style={styles.quickActionIconText}>⤴</Text>;/;/g/;
          </View>;/;/g/;
          <Text style={styles.quickActionTitle}>分享报告</Text>;/;/g/;
          <Text style={styles.quickActionDescription}>分享健康报告</Text>;/;/g/;
        </TouchableOpacity>;)/;/g/;
      </View>;)/;/g/;
    </View>;)/;/g/;
  );
const  renderDataStats = () => (<View style={styles.dataStatsSection}>;)      <Text style={styles.sectionTitle}>数据统计</Text>/;/g/;
      <View style={styles.statsGrid}>;
        <View style={styles.statCard}>;
          <Text style={styles.statNumber}>1,234</Text>/;/g/;
          <Text style={styles.statLabel}>健康记录</Text>/;/g/;
        </View>/;/g/;
        <View style={styles.statCard}>;
          <Text style={styles.statNumber}>56</Text>;/;/g/;
          <Text style={styles.statLabel}>生命体征</Text>;/;/g/;
        </View>;/;/g/;
        <View style={styles.statCard}>;
          <Text style={styles.statNumber}>12</Text>;/;/g/;
          <Text style={styles.statLabel}>中医诊断</Text>;/;/g/;
        </View>;/;/g/;
        <View style={styles.statCard}>;
          <Text style={styles.statNumber}>8</Text>;/;/g/;
          <Text style={styles.statLabel}>健康报告</Text>;/;/g/;
        </View>;)/;/g/;
      </View>;)/;/g/;
    </View>;)/;/g/;
  );
return (;);
    <View style={styles.container}>;
      <View style={styles.header}>;
        <Text style={styles.title}>数据管理</Text>;/;/g/;
        <Text style={styles.subtitle}>导入、导出和管理您的健康数据</Text>;/;/g/;
      </View>;/;/g/;
      <ScrollView style={styles.scrollView}>;
        {renderQuickActions()};
        {renderDataStats()};
      </ScrollView>;/;/g/;
      {renderModal()};
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
quickActionsSection: {,;}}
  const padding = 16;}
  }
sectionTitle: {,';,}fontSize: 18,';,'';
fontWeight: 'bold';','';
color: '#333';','';'';
}
    const marginBottom = 16;}
  },';,'';
quickActionsGrid: {,';,}flexDirection: 'row';','';
flexWrap: 'wrap';','';'';
}
    const justifyContent = 'space-between'}'';'';
  ;},';,'';
quickActionCard: {,';,}width: '48%';','';
backgroundColor: '#fff';','';
borderRadius: 12,;
padding: 16,';,'';
marginBottom: 16,';,'';
alignItems: 'center';','';'';
}
    shadowColor: '#000';','}'';
shadowOffset: { width: 0, height: 2 ;}
shadowOpacity: 0.1,;
shadowRadius: 4,;
const elevation = 3;
  }
quickActionIcon: {width: 48,;
height: 48,';,'';
borderRadius: 24,';,'';
justifyContent: 'center';','';
alignItems: 'center';','';'';
}
    const marginBottom = 12;}
  },';,'';
quickActionIconText: {,';,}color: '#fff';','';
fontSize: 20,';'';
}
    const fontWeight = 'bold'}'';'';
  ;}
quickActionTitle: {,';,}fontSize: 16,';,'';
fontWeight: 'bold';','';
color: '#333';','';
marginBottom: 4,';'';
}
    const textAlign = 'center'}'';'';
  ;}
quickActionDescription: {,';,}fontSize: 12,';,'';
color: '#666';','';'';
}
    const textAlign = 'center'}'';'';
  ;}
dataStatsSection: {padding: 16,;
}
    const paddingTop = 0;}
  },';,'';
statsGrid: {,';,}flexDirection: 'row';','';'';
}
    const justifyContent = 'space-between'}'';'';
  ;}
statCard: {,';,}flex: 1,';,'';
backgroundColor: '#fff';','';
borderRadius: 12,;
padding: 16,';,'';
marginHorizontal: 4,';,'';
alignItems: 'center';','';'';
}
    shadowColor: '#000';','}'';
shadowOffset: { width: 0, height: 2 ;}
shadowOpacity: 0.1,;
shadowRadius: 4,;
const elevation = 3;
  }
statNumber: {,';,}fontSize: 24,';,'';
fontWeight: 'bold';','';
color: '#007AFF';','';'';
}
    const marginBottom = 4;}
  }
statLabel: {,';,}fontSize: 12,';,'';
color: '#666';','';'';
}
    const textAlign = 'center'}'';'';
  ;},);
modalOverlay: {,)';,}flex: 1,)';,'';
backgroundColor: 'rgba(0, 0, 0, 0.5)',';,'';
justifyContent: 'center';','';'';
}
    const alignItems = 'center'}'';'';
  ;},';,'';
modalContent: {,';,}backgroundColor: '#fff';','';
borderRadius: 12,';,'';
width: '90%';','';'';
}
    const maxHeight = '80%'}'';'';
  ;},';,'';
modalHeader: {,';,}flexDirection: 'row';','';
justifyContent: 'space-between';','';
alignItems: 'center';','';
padding: 20,';,'';
borderBottomWidth: 1,';'';
}
    const borderBottomColor = '#f0f0f0'}'';'';
  ;}
modalTitle: {,';,}fontSize: 18,';,'';
fontWeight: 'bold';','';'';
}
    const color = '#333'}'';'';
  ;}
closeButton: {width: 30,;
height: 30,';,'';
borderRadius: 15,';,'';
backgroundColor: '#f0f0f0';','';
justifyContent: 'center';','';'';
}
    const alignItems = 'center'}'';'';
  ;}
closeButtonText: {,';,}fontSize: 20,';'';
}
    const color = '#666'}'';'';
  ;},';,'';
modalScrollView: {,';,}maxHeight: '70%';','';'';
}
    const padding = 20;}
  },';,'';
formatOption: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';
padding: 16,;
borderRadius: 8,';,'';
borderWidth: 1,';,'';
borderColor: '#e0e0e0';','';
marginBottom: 12,';'';
}
    const backgroundColor = '#fff'}'';'';
  ;},';,'';
formatOptionSelected: {,';,}borderColor: '#007AFF';','';'';
}
    const backgroundColor = '#f0f8ff'}'';'';
  ;}
formatOptionContent: {,;}}
  const flex = 1;}
  }
formatLabel: {,';,}fontSize: 16,';,'';
fontWeight: 'bold';','';
color: '#333';','';'';
}
    const marginBottom = 4;}
  },';,'';
formatLabelSelected: {,';}}'';
  const color = '#007AFF'}'';'';
  ;}
formatDescription: {,';,}fontSize: 14,';'';
}
    const color = '#666'}'';'';
  ;},';,'';
formatDescriptionSelected: {,';}}'';
  const color = '#0066cc'}'';'';
  ;}
radioButton: {width: 20,;
height: 20,;
borderRadius: 10,';,'';
borderWidth: 2,';,'';
borderColor: '#e0e0e0';','';
justifyContent: 'center';','';'';
}
    const alignItems = 'center'}'';'';
  ;},';,'';
radioButtonSelected: {,';}}'';
  const borderColor = '#007AFF'}'';'';
  ;}
radioButtonInner: {width: 10,;
height: 10,';,'';
borderRadius: 5,';'';
}
    const backgroundColor = '#007AFF'}'';'';
  ;}
exportOptions: {,;}}
  const marginTop = 20;}
  },';,'';
optionItem: {,';,}flexDirection: 'row';','';
justifyContent: 'space-between';','';
alignItems: 'center';','';
paddingVertical: 12,';,'';
borderBottomWidth: 1,';'';
}
    const borderBottomColor = '#f0f0f0'}'';'';
  ;}
optionLabel: {,';,}fontSize: 14,';'';
}
    const color = '#333'}'';'';
  ;}
optionValue: {,';,}fontSize: 14,';'';
}
    const color = '#666'}'';'';
  ;}
importOptions: {,;}}
  const marginTop = 20;}
  }
importNote: {,';,}fontSize: 14,';,'';
color: '#666';','';
lineHeight: 20,';,'';
backgroundColor: '#f8f9fa';','';
padding: 16,;
}
    const borderRadius = 8;}
  },';,'';
modalButtons: {,';,}flexDirection: 'row';','';
justifyContent: 'space-between';','';
padding: 20,';,'';
borderTopWidth: 1,';'';
}
    const borderTopColor = '#f0f0f0'}'';'';
  ;}
modalButton: {flex: 1,';,'';
paddingVertical: 12,';'';
}
    borderRadius: 8,marginHorizontal: 8,justifyContent: 'center',alignItems: 'center';'}'';'';
  },cancelButton: {backgroundColor: '#666';'}'';'';
  },confirmButton: {backgroundColor: '#007AFF';'}'';'';
  },modalButtonText: {,';,}color: "#fff";","";"";
}
      fontSize: 16,fontWeight: '500';'}'';'';
  };';'';
});