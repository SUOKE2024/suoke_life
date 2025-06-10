import React, { useEffect, useState, useCallback } from "react";";
import {import { SafeAreaView } from "react-native-safe-area-context";";
import Icon from "react-native-vector-icons/MaterialIcons";""/;,"/g"/;
import { useMedicalResource } from "../../hooks/useMedicalResource";""/;,"/g"/;
import { Appointment } from "../../store/slices/medicalResourceSlice";""/;,"/g"/;
View,;
Text,;
StyleSheet,;
FlatList,;
TouchableOpacity,;
RefreshControl,;
Alert,;
Modal,;
TextInput,";,"";
Dimensions;';'';
} from "react-native";";
const { width } = Dimensions.get('window');';,'';
interface AppointmentScreenProps {}}
}
  const navigation = any;}
}
const AppointmentScreen: React.FC<Suspense fallback={<LoadingSpinner  />}><AppointmentScreenProps></Suspense> = ({ navigation ;}) => {/;,}const {appointments}selectedAppointment,;,/g/;
loading,;
errors,;
upcomingAppointments,;
pastAppointments,;
hasAppointments,;
isLoading,;
    // 操作方法/;,/g/;
getAppointments,;
selectAppointment,;
cancelAppointment,;
};
clearSpecificError;}';'';
  } = useMedicalResource();';,'';
const [activeTab, setActiveTab] = useState<'upcoming' | 'past'>('upcoming');';,'';
const [showCancelModal, setShowCancelModal] = useState(false);';,'';
const [cancelReason, setCancelReason] = useState(');'';'';
  // 初始化/;,/g/;
useEffect() => {';}    // 这里应该从用户状态获取用户ID;'/;,'/g'/;
const userId = 'current-user-id';';'';
}
    getAppointments(userId);}
  }, [getAppointments]);';'';
  // 刷新'/;,'/g'/;
const handleRefresh = useCallback() => {const userId = 'current-user-id';';}}'';
    getAppointments(userId);}
  }, [getAppointments]);
  // 预约项点击'/;,'/g'/;
const handleAppointmentPress = useCallback(appointment: Appointment) => {selectAppointment(appointment);'}'';
navigation.navigate('AppointmentDetail', { appointmentId: appointment.id ;});';'';
  }, [selectAppointment, navigation]);
  // 取消预约/;,/g/;
const handleCancelPress = useCallback(appointment: Appointment) => {selectAppointment(appointment);}}
    setShowCancelModal(true);}
  }, [selectAppointment]);
  // 确认取消预约/;,/g/;
const handleConfirmCancel = useCallback(async () => {if (!selectedAppointment) return;);,}try {const success = await cancelAppointment(selectedAppointment.id);,}if (success) {';,}setShowCancelModal(false);';,'';
setCancelReason(');'';'';

}
        handleRefresh();}
      } else {}}
}
      }
    } catch (error) {}}
}
    }
  }, [selectedAppointment, cancelAppointment, handleRefresh]);';'';
  // 重新预约'/;,'/g,'/;
  handleReschedule: useCallback(appointment: Appointment) => {navigation.navigate('MedicalResourceDetail', {resourceId: appointment.resourceId,reschedule: true ;)'}'';'';
    });
  }, [navigation]);
  // 渲染标签页/;,/g/;
const  renderTabs = () => (<View style={styles.tabContainer}>)';'';
      <TouchableOpacity;)'  />/;,'/g'/;
style={[styles.tab, activeTab === 'upcoming' && styles.activeTab]}')'';
onPress={() => setActiveTab('upcoming')};';'';
      >;';'';
        <Text style={[styles.tabText, activeTab === 'upcoming' && styles.activeTabText]}>;';'';

        </Text>;/;/g/;
      </TouchableOpacity>;'/;'/g'/;
      <TouchableOpacity;'  />/;,'/g'/;
style={[styles.tab, activeTab === 'past' && styles.activeTab]};';,'';
onPress={() => setActiveTab('past')};';'';
      >;';'';
        <Text style={[styles.tabText, activeTab === 'past' && styles.activeTabText]}>;';'';

        </Text>;/;/g/;
      </TouchableOpacity>;/;/g/;
    </View>;/;/g/;
  );
  // 渲染预约卡片'/;,'/g'/;
const renderAppointmentCard = ({ item }: { item: Appointment ;}) => {const isUpcoming = new Date(item.scheduledTime) > new Date();';,}const canCancel = isUpcoming && item.status === 'confirmed';';'';
}
    return (<TouchableOpacity;)}  />/;,/g/;
style={styles.appointmentCard});
onPress={() => handleAppointmentPress(item)}
      >;
        <View style={styles.cardHeader}>;
          <View style={styles.appointmentInfo}>;
            <Text style={styles.resourceName}>{item.resourceName}</Text>/;/g/;
            <Text style={styles.serviceType}>{item.serviceType}</Text>/;/g/;
          </View>/;/g/;
          <View style={[styles.statusBadge, getStatusStyle(item.status)]}>;
            <Text style={[styles.statusText, getStatusTextStyle(item.status)]}>;
              {getStatusLabel(item.status)}
            </Text>/;/g/;
          </View>/;/g/;
        </View>'/;'/g'/;
        <View style={styles.timeContainer}>';'';
          <Icon name="schedule" size={16} color="#666"  />"/;"/g"/;
          <Text style={styles.timeText}>;

          </Text>/;/g/;
        </View>"/;"/g"/;
        {item.location  && <View style={styles.locationContainer}>";"";
            <Icon name="location-on" size={16} color="#666"  />"/;"/g"/;
            <Text style={styles.locationText}>{item.location}</Text>/;/g/;
          </View>/;/g/;
        )}
        {item.notes  && <Text style={styles.notesText}>备注：{item.notes}</Text>/;/g/;
        )}
        {item.price  && <Text style={styles.priceText}>费用：¥{item.price}</Text>/;/g/;
        )}
        <View style={styles.cardActions}>;
          {item.contact  && <TouchableOpacity;}  />/;,/g/;
style={styles.actionButton}
              onPress={() => handleCall(item.contact!)}";"";
            >";"";
              <Icon name="phone" size={16} color="#007AFF"  />"/;"/g"/;
              <Text style={styles.actionButtonText}>联系</Text>/;/g/;
            </TouchableOpacity>/;/g/;
          )}
          {canCancel  && <TouchableOpacity;}  />/;,/g/;
style={[styles.actionButton, styles.cancelActionButton]}
              onPress={() => handleCancelPress(item)}";"";
            >";"";
              <Icon name="cancel" size={16} color="#FF3B30"  />;"/;"/g"/;
              <Text style={[styles.actionButtonText, styles.cancelActionText]}>取消</Text>;/;/g/;
            </TouchableOpacity>;"/;"/g"/;
          )};";"";
          {isUpcoming && item.status === 'confirmed' && (;)';}}'';
            <TouchableOpacity;}  />/;,/g/;
style={styles.actionButton};
onPress={() => handleReschedule(item)};';'';
            >;';'';
              <Icon name="schedule" size={16} color="#007AFF"  />;"/;"/g"/;
              <Text style={styles.actionButtonText}>改期</Text>;/;/g/;
            </TouchableOpacity>;/;/g/;
          )};
        </View>;/;/g/;
      </TouchableOpacity>;/;/g/;
    );
  };
  // 拨打电话/;,/g/;
const handleCall = useCallback(phoneNumber: string) => {const url = `tel: ${phoneNumber;}`;````;,```;
Linking.canOpenURL(url);
      .then(supported) => {if (supported) {}}
          return Linking.openURL(url);}
        } else {}}
}
        }
      });

  }, []);
  // 渲染空状态"/;,"/g"/;
const  renderEmptyState = () => (<View style={styles.emptyContainer}>";)      <Icon name="event-busy" size={64} color="#ccc"  />"/;"/g"/;
      <Text style={styles.emptyText}>;

      </Text>;/;/g/;
      <Text style={styles.emptySubtext}>;);
)";"";
      </Text>;)"/;"/g"/;
      {activeTab === 'upcoming' && (;)';}}'';
        <TouchableOpacity;}'  />/;,'/g'/;
style={styles.searchButton};';,'';
onPress={() => navigation.navigate('MedicalResource')};';'';
        >;
          <Text style={styles.searchButtonText}>搜索医疗资源</Text>;/;/g/;
        </TouchableOpacity>;/;/g/;
      )};
    </View>;/;/g/;
  );
  // 渲染取消预约模态框/;,/g/;
const renderCancelModal = () => (<Modal;  />/;,)visible={showCancelModal})';,'/g'/;
transparent;)';,'';
animationType="slide")";,"";
onRequestClose={() => setShowCancelModal(false)}
    >;
      <View style={styles.modalOverlay}>;
        <View style={styles.modalContent}>;
          <Text style={styles.modalTitle}>取消预约</Text>/;/g/;
          {selectedAppointment  && <View style={styles.appointmentSummary}>;
              <Text style={styles.summaryText}>;
                {selectedAppointment.resourceName}
              </Text>/;/g/;
              <Text style={styles.summarySubtext}>;
                {formatDateTime(selectedAppointment.scheduledTime)}
              </Text>/;/g/;
            </View>/;/g/;
          )}
          ;
          <Text style={styles.reasonLabel}>取消原因（可选）：</Text>;/;/g/;
          <TextInput;  />/;,/g/;
style={styles.reasonInput};
value={cancelReason};
onChangeText={setCancelReason};
multiline;";,"";
numberOfLines={3};";,"";
textAlignVertical="top";";"";
          />;/;/g/;
          <View style={styles.modalButtons}>;
            <TouchableOpacity;  />/;,/g/;
style={[styles.modalButton, styles.cancelButton]};";,"";
onPress={() => {setShowCancelModal(false);";}}"";
                setCancelReason('');'}'';'';
              }}
            >;
              <Text style={styles.cancelButtonText}>返回</Text>/;/g/;
            </TouchableOpacity>/;/g/;
            <TouchableOpacity;  />/;,/g/;
style={[styles.modalButton, styles.confirmButton]}
              onPress={handleConfirmCancel}
            >;
              <Text style={styles.confirmButtonText}>确认取消</Text>/;/g/;
            </TouchableOpacity>/;/g/;
          </View>/;/g/;
        </View>/;/g/;
      </View>/;/g/;
    </Modal>/;/g/;
  );';'';
  // 获取状态样式'/;,'/g'/;
const getStatusStyle = (status: string) => {switch (status) {case 'confirmed': return { backgroundColor: '#E8F5E8' ;};';,'';
case 'pending': ';,'';
return { backgroundColor: '#FFF3CD' ;};';,'';
case 'completed': ';,'';
return { backgroundColor: '#E3F2FD' ;};';,'';
case 'cancelled': ';,'';
return { backgroundColor: '#FFEBEE' ;};';,'';
const default = ';,'';
return { backgroundColor: '#F5F5F5' ;};';'';
    }';'';
  };';,'';
const getStatusTextStyle = (status: string) => {switch (status) {case 'confirmed': return { color: '#2E7D32' ;};';,'';
case 'pending': ';,'';
return { color: '#F57C00' ;};';,'';
case 'completed': ';,'';
return { color: '#1976D2' ;};';,'';
case 'cancelled': ';,'';
return { color: '#D32F2F' ;};';,'';
const default = ';,'';
return { color: '#666' ;};';'';
    }
  };';'';
';,'';
case 'pending': ';'';
';,'';
case 'completed': ';'';
';,'';
case 'cancelled': ';,'';
default: ;
return status;
    }
  };
  // 格式化日期时间/;,/g/;
const formatDateTime = (dateTime: string) => {const date = new Date(dateTime);,}const now = new Date();
today: new Date(now.getFullYear(), now.getMonth(), now.getDate());
appointmentDate: new Date(date.getFullYear(), date.getMonth(), date.getDate());
const timeDiff = appointmentDate.getTime() - today.getTime();';,'';
const daysDiff = Math.ceil(timeDiff / (1000 * 3600 * 24));'/;,'/g'/;
let dateStr = ';'';
if (daysDiff === 0) {}}
}
    } else if (daysDiff === 1) {}}
}
    } else if (daysDiff === -1) {}}
}
    } else {}}
}';'';
    }';,'';
timeStr: `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;````;,```;
return `${dateStr} ${timeStr}`;````;```;
  };
  // 渲染错误状态/;,/g/;
if (errors.appointments) {}}
    return (;)}
      <SafeAreaView style={styles.container}>;
        <View style={styles.errorContainer}>;
          <Text style={styles.errorText}>{errors.appointments}</Text>;/;/g/;
          <TouchableOpacity;'  />/;,'/g'/;
style={styles.retryButton};';,'';
onPress={() => {clearSpecificError('appointments');';}}'';
              handleRefresh();}
            }}
          >;
            <Text style={styles.retryButtonText}>重试</Text>/;/g/;
          </TouchableOpacity>/;/g/;
        </View>/;/g/;
      </SafeAreaView>/;/g/;
    );';'';
  }';,'';
const currentAppointments = activeTab === 'upcoming' ? upcomingAppointments : pastAppointments;';,'';
return (<SafeAreaView style={styles.container}>;)      <View style={styles.header}>;
        <Text style={styles.headerTitle}>我的预约</Text>)/;/g/;
        <TouchableOpacity;)'  />/;,'/g'/;
style={styles.addButton})';,'';
onPress={() => navigation.navigate('MedicalResource')}';'';
        >';'';
          <Icon name="add" size={24} color="#007AFF"  />"/;"/g"/;
        </TouchableOpacity>/;/g/;
      </View>/;/g/;
      {renderTabs()};
      <FlatList removeClippedSubviews={true} maxToRenderPerBatch={10} windowSize={10};  />/;,/g/;
data={currentAppointments};
renderItem={renderAppointmentCard};
keyExtractor={(item) => item.id};
refreshControl={<RefreshControl refreshing={loading.appointments} onRefresh={handleRefresh}  />;/;/g/;
        };
contentContainerStyle={styles.listContainer};
ListEmptyComponent={renderEmptyState};
showsVerticalScrollIndicator={false};
      />;/;/g/;
      {renderCancelModal()};
    </SafeAreaView>;/;/g/;
  );
};
const  styles = StyleSheet.create({)container: {,";,}flex: 1,";"";
}
    const backgroundColor = '#f5f5f5'}'';'';
  ;}
  // 头部'/;,'/g,'/;
  header: {,';,}flexDirection: 'row';','';
justifyContent: 'space-between';','';
alignItems: 'center';','';
paddingHorizontal: 16,';,'';
paddingVertical: 12,';,'';
backgroundColor: '#fff';','';
borderBottomWidth: 1,';'';
}
    const borderBottomColor = '#e0e0e0'}'';'';
  ;}
headerTitle: {,';,}fontSize: 18,';,'';
fontWeight: '600';','';'';
}
    const color = '#333'}'';'';
  ;}
addButton: {,;}}
  const padding = 8;}
  }
  // 标签页'/;,'/g,'/;
  tabContainer: {,';,}flexDirection: 'row';','';
backgroundColor: '#fff';','';
borderBottomWidth: 1,';'';
}
    const borderBottomColor = '#e0e0e0'}'';'';
  ;}
tab: {flex: 1,';,'';
paddingVertical: 12,';,'';
alignItems: 'center';','';
borderBottomWidth: 2,';'';
}
    const borderBottomColor = 'transparent'}'';'';
  ;},';,'';
activeTab: {,';}}'';
  const borderBottomColor = '#007AFF'}'';'';
  ;}
tabText: {,';,}fontSize: 14,';,'';
color: '#666';','';'';
}
    const fontWeight = '500'}'';'';
  ;},';,'';
activeTabText: {,';}}'';
  const color = '#007AFF'}'';'';
  ;}
  // 列表/;,/g,/;
  listContainer: {paddingHorizontal: 16,;
}
    const paddingTop = 16;}
  }
  // 预约卡片'/;,'/g,'/;
  appointmentCard: {,';,}backgroundColor: '#fff';','';
borderRadius: 12,;
padding: 16,';,'';
marginBottom: 12,';'';
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
appointmentInfo: {,;}}
  const flex = 1;}
  }
resourceName: {,';,}fontSize: 16,';,'';
fontWeight: '600';','';
color: '#333';','';'';
}
    const marginBottom = 4;}
  }
serviceType: {,';,}fontSize: 14,';'';
}
    const color = '#666'}'';'';
  ;}
statusBadge: {paddingHorizontal: 8,;
paddingVertical: 4,;
}
    const borderRadius = 12;}
  }
statusText: {,';,}fontSize: 12,';'';
}
    const fontWeight = '500'}'';'';
  ;},';,'';
timeContainer: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';'';
}
    const marginBottom = 8;}
  }
timeText: {marginLeft: 8,';,'';
fontSize: 14,';'';
}
    const color = '#333'}'';'';
  ;},';,'';
locationContainer: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';'';
}
    const marginBottom = 8;}
  }
locationText: {marginLeft: 8,';,'';
fontSize: 14,';'';
}
    const color = '#666'}'';'';
  ;}
notesText: {,';,}fontSize: 14,';,'';
color: '#666';','';'';
}
    const marginBottom = 8;}
  }
priceText: {,';,}fontSize: 14,';,'';
fontWeight: '600';','';
color: '#FF6B35';','';'';
}
    const marginBottom = 12;}
  },';,'';
cardActions: {,';,}flexDirection: 'row';','';'';
}
    const justifyContent = 'flex-end'}'';'';
  ;},';,'';
actionButton: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';
paddingHorizontal: 12,;
paddingVertical: 6,;
marginLeft: 8,';,'';
borderRadius: 6,';'';
}
    const backgroundColor = '#f8f8f8'}'';'';
  ;},';,'';
cancelActionButton: {,';}}'';
  const backgroundColor = '#FFEBEE'}'';'';
  ;}
actionButtonText: {marginLeft: 4,';,'';
fontSize: 12,';,'';
color: '#007AFF';','';'';
}
    const fontWeight = '500'}'';'';
  ;},';,'';
cancelActionText: {,';}}'';
  const color = '#FF3B30'}'';'';
  ;}
  // 空状态/;,/g,/;
  emptyContainer: {,';,}flex: 1,';,'';
justifyContent: 'center';','';
alignItems: 'center';','';'';
}
    const paddingVertical = 60;}
  }
emptyText: {,';,}fontSize: 18,';,'';
fontWeight: '500';','';
color: '#666';','';
marginTop: 16,;
}
    const marginBottom = 8;}
  }
emptySubtext: {,';,}fontSize: 14,';,'';
color: '#999';','';
textAlign: 'center';','';'';
}
    const marginBottom = 20;}
  },';,'';
searchButton: {,';,}backgroundColor: '#007AFF';','';
paddingHorizontal: 20,;
paddingVertical: 12,;
}
    const borderRadius = 8;}
  },';,'';
searchButtonText: {,';,}color: '#fff';','';
fontSize: 16,';'';
}
    const fontWeight = '500'}'';'';
  ;}
  // 错误状态/;,/g,/;
  errorContainer: {,';,}flex: 1,';,'';
justifyContent: 'center';','';
alignItems: 'center';','';'';
}
    const paddingHorizontal = 20;}
  }
errorText: {,';,}fontSize: 16,';,'';
color: '#666';','';
textAlign: 'center';','';'';
}
    const marginBottom = 20;}
  },';,'';
retryButton: {,';,}backgroundColor: '#007AFF';','';
paddingHorizontal: 20,;
paddingVertical: 10,;
}
    const borderRadius = 8;}
  },';,'';
retryButtonText: {,';,}color: '#fff';','';
fontSize: 16,';'';
}
    const fontWeight = '500'}'';'';
  ;}
  // 取消预约模态框)/;,/g,/;
  modalOverlay: {,)';,}flex: 1,)';,'';
backgroundColor: 'rgba(0, 0, 0, 0.5)',';,'';
justifyContent: 'center';','';'';
}
    const alignItems = 'center'}'';'';
  ;},';,'';
modalContent: {,';,}backgroundColor: '#fff';','';
borderRadius: 12,;
padding: 20,;
width: width * 0.85,;
}
    const maxWidth = 400;}
  }
modalTitle: {,';,}fontSize: 18,';,'';
fontWeight: '600';','';
color: '#333';','';
textAlign: 'center';','';'';
}
    const marginBottom = 20;}
  },';,'';
appointmentSummary: {,';,}backgroundColor: '#f8f8f8';','';
padding: 12,;
borderRadius: 8,;
}
    const marginBottom = 16;}
  }
summaryText: {,';,}fontSize: 16,';,'';
fontWeight: '500';','';
color: '#333';','';'';
}
    const marginBottom = 4;}
  }
summarySubtext: {,';,}fontSize: 14,';'';
}
    const color = '#666'}'';'';
  ;}
reasonLabel: {,';,}fontSize: 14,';,'';
color: '#333';','';'';
}
    const marginBottom = 8;}
  }
reasonInput: {,';,}borderWidth: 1,';,'';
borderColor: '#e0e0e0';','';
borderRadius: 8,;
padding: 12,';,'';
fontSize: 14,';,'';
color: '#333';','';
marginBottom: 20,;
}
    const minHeight = 80;}
  },';,'';
modalButtons: {,';}}'';
  const flexDirection = 'row'}'';'';
  ;}
modalButton: {flex: 1,;
paddingVertical: 12,';,'';
borderRadius: 8,';'';
}
    const alignItems = 'center'}'';'';
  ;},';,'';
cancelButton: {,';,}backgroundColor: '#f0f0f0';','';'';
}
    const marginRight = 8;}';'';
  },confirmButton: {,';,}backgroundColor: "#FF3B30";","";"";
}
      const marginLeft = 8;"}"";"";
  },cancelButtonText: {fontSize: 16,color: '#666',fontWeight: '500';'}'';'';
  },confirmButtonText: {fontSize: 16,color: '#fff',fontWeight: '500';'}'';'';
  };
});';,'';
export default AppointmentScreen;