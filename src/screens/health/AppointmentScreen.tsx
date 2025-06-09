import React, { useEffect, useState, useCallback } from 'react';
import {import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { useMedicalResource } from '../../hooks/useMedicalResource';
import { Appointment } from '../../store/slices/medicalResourceSlice';
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  RefreshControl,
  Alert,
  Modal,
  TextInput,
  Dimensions;
} from 'react-native';
const { width } = Dimensions.get('window');
interface AppointmentScreenProps {
  navigation: any;
}
const AppointmentScreen: React.FC<AppointmentScreenProps> = ({ navigation }) => {
  const {
    appointments,
    selectedAppointment,
    loading,
    errors,
    upcomingAppointments,
    pastAppointments,
    hasAppointments,
    isLoading,
    // 操作方法
    getAppointments,
    selectAppointment,
    cancelAppointment,
    clearSpecificError;
  } = useMedicalResource();
  const [activeTab, setActiveTab] = useState<'upcoming' | 'past'>('upcoming');
  const [showCancelModal, setShowCancelModal] = useState(false);
  const [cancelReason, setCancelReason] = useState('');
  // 初始化
  useEffect() => {
    // 这里应该从用户状态获取用户ID;
    const userId = 'current-user-id';
    getAppointments(userId);
  }, [getAppointments]);
  // 刷新
  const handleRefresh = useCallback() => {const userId = 'current-user-id';
    getAppointments(userId);
  }, [getAppointments]);
  // 预约项点击
  const handleAppointmentPress = useCallback(appointment: Appointment) => {selectAppointment(appointment);
    navigation.navigate('AppointmentDetail', { appointmentId: appointment.id });
  }, [selectAppointment, navigation]);
  // 取消预约
  const handleCancelPress = useCallback(appointment: Appointment) => {selectAppointment(appointment);
    setShowCancelModal(true);
  }, [selectAppointment]);
  // 确认取消预约
  const handleConfirmCancel = useCallback(async () => {if (!selectedAppointment) return;)
    try {
      const success = await cancelAppointment(selectedAppointment.id);
      if (success) {
        setShowCancelModal(false);
        setCancelReason('');
        Alert.alert("取消成功", "预约已取消');
        handleRefresh();
      } else {
        Alert.alert("取消失败", "请稍后重试');
      }
    } catch (error) {
      Alert.alert("取消失败", "请稍后重试');
    }
  }, [selectedAppointment, cancelAppointment, handleRefresh]);
  // 重新预约
  const handleReschedule = useCallback(appointment: Appointment) => {navigation.navigate('MedicalResourceDetail', {resourceId: appointment.resourceId,reschedule: true ;)
    });
  }, [navigation]);
  // 渲染标签页
  const renderTabs = () => (
  <View style={styles.tabContainer}>
      <TouchableOpacity;
        style={[styles.tab, activeTab === 'upcoming' && styles.activeTab]}
        onPress={() => setActiveTab('upcoming')};
      >;
        <Text style={[styles.tabText, activeTab === 'upcoming' && styles.activeTabText]}>;
          即将到来 ({upcomingAppointments.length});
        </Text>;
      </TouchableOpacity>;
      <TouchableOpacity;
        style={[styles.tab, activeTab === 'past' && styles.activeTab]};
        onPress={() => setActiveTab('past')};
      >;
        <Text style={[styles.tabText, activeTab === 'past' && styles.activeTabText]}>;
          历史记录 ({pastAppointments.length});
        </Text>;
      </TouchableOpacity>;
    </View>;
  );
  // 渲染预约卡片
  const renderAppointmentCard = ({ item }: { item: Appointment }) => {const isUpcoming = new Date(item.scheduledTime) > new Date();
    const canCancel = isUpcoming && item.status === 'confirmed';
    return (
  <TouchableOpacity;
        style={styles.appointmentCard}
        onPress={() => handleAppointmentPress(item)}
      >
        <View style={styles.cardHeader}>
          <View style={styles.appointmentInfo}>
            <Text style={styles.resourceName}>{item.resourceName}</Text>
            <Text style={styles.serviceType}>{item.serviceType}</Text>
          </View>
          <View style={[styles.statusBadge, getStatusStyle(item.status)]}>
            <Text style={[styles.statusText, getStatusTextStyle(item.status)]}>
              {getStatusLabel(item.status)}
            </Text>
          </View>
        </View>
        <View style={styles.timeContainer}>
          <Icon name="schedule" size={16} color="#666" />
          <Text style={styles.timeText}>
            {formatDateTime(item.scheduledTime)} · {item.duration}分钟
          </Text>
        </View>
        {item.location  && <View style={styles.locationContainer}>
            <Icon name="location-on" size={16} color="#666" />
            <Text style={styles.locationText}>{item.location}</Text>
          </View>
        )}
        {item.notes  && <Text style={styles.notesText}>备注：{item.notes}</Text>
        )}
        {item.price  && <Text style={styles.priceText}>费用：¥{item.price}</Text>
        )}
        <View style={styles.cardActions}>
          {item.contact  && <TouchableOpacity;
              style={styles.actionButton}
              onPress={() => handleCall(item.contact!)}
            >
              <Icon name="phone" size={16} color="#007AFF" />
              <Text style={styles.actionButtonText}>联系</Text>
            </TouchableOpacity>
          )}
          {canCancel  && <TouchableOpacity;
              style={[styles.actionButton, styles.cancelActionButton]}
              onPress={() => handleCancelPress(item)}
            >
              <Icon name="cancel" size={16} color="#FF3B30" />;
              <Text style={[styles.actionButtonText, styles.cancelActionText]}>取消</Text>;
            </TouchableOpacity>;
          )};
          {isUpcoming && item.status === 'confirmed' && (;)
            <TouchableOpacity;
              style={styles.actionButton};
              onPress={() => handleReschedule(item)};
            >;
              <Icon name="schedule" size={16} color="#007AFF" />;
              <Text style={styles.actionButtonText}>改期</Text>;
            </TouchableOpacity>;
          )};
        </View>;
      </TouchableOpacity>;
    );
  };
  // 拨打电话
  const handleCall = useCallback(phoneNumber: string) => {const url = `tel:${phoneNumber}`;
    Linking.canOpenURL(url);
      .then(supported) => {
        if (supported) {
          return Linking.openURL(url);
        } else {
          Alert.alert("错误", "无法拨打电话');
        }
      })
      .catch(err) => console.error('拨打电话失败:', err));
  }, []);
  // 渲染空状态
  const renderEmptyState = () => (
  <View style={styles.emptyContainer}>
      <Icon name="event-busy" size={64} color="#ccc" />
      <Text style={styles.emptyText}>;
        {activeTab === 'upcoming' ? '暂无即将到来的预约' : '暂无历史预约记录'};
      </Text>;
      <Text style={styles.emptySubtext}>;
        {activeTab === 'upcoming' ? '去搜索医疗资源并预约吧' : '完成预约后会在这里显示'};
      </Text>;
      {activeTab === 'upcoming' && (;)
        <TouchableOpacity;
          style={styles.searchButton};
          onPress={() => navigation.navigate('MedicalResource')};
        >;
          <Text style={styles.searchButtonText}>搜索医疗资源</Text>;
        </TouchableOpacity>;
      )};
    </View>;
  );
  // 渲染取消预约模态框
  const renderCancelModal = () => (
  <Modal;
      visible={showCancelModal}
      transparent;
      animationType="slide"
      onRequestClose={() => setShowCancelModal(false)}
    >
      <View style={styles.modalOverlay}>
        <View style={styles.modalContent}>
          <Text style={styles.modalTitle}>取消预约</Text>
          {selectedAppointment  && <View style={styles.appointmentSummary}>
              <Text style={styles.summaryText}>
                {selectedAppointment.resourceName}
              </Text>
              <Text style={styles.summarySubtext}>
                {formatDateTime(selectedAppointment.scheduledTime)}
              </Text>
            </View>
          )}
          ;
          <Text style={styles.reasonLabel}>取消原因（可选）：</Text>;
          <TextInput;
            style={styles.reasonInput};
            placeholder="请输入取消原因...";
            value={cancelReason};
            onChangeText={setCancelReason};
            multiline;
            numberOfLines={3};
            textAlignVertical="top";
          />;
          <View style={styles.modalButtons}>;
            <TouchableOpacity;
              style={[styles.modalButton, styles.cancelButton]};
              onPress={() => {setShowCancelModal(false);
                setCancelReason('');
              }}
            >
              <Text style={styles.cancelButtonText}>返回</Text>
            </TouchableOpacity>
            <TouchableOpacity;
              style={[styles.modalButton, styles.confirmButton]}
              onPress={handleConfirmCancel}
            >
              <Text style={styles.confirmButtonText}>确认取消</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>
  );
  // 获取状态样式
  const getStatusStyle = (status: string) => {switch (status) {case 'confirmed':return { backgroundColor: '#E8F5E8' };
      case 'pending':
        return { backgroundColor: '#FFF3CD' };
      case 'completed':
        return { backgroundColor: '#E3F2FD' };
      case 'cancelled':
        return { backgroundColor: '#FFEBEE' };
      default:
        return { backgroundColor: '#F5F5F5' };
    }
  };
  const getStatusTextStyle = (status: string) => {switch (status) {case 'confirmed':return { color: '#2E7D32' };
      case 'pending':
        return { color: '#F57C00' };
      case 'completed':
        return { color: '#1976D2' };
      case 'cancelled':
        return { color: '#D32F2F' };
      default:
        return { color: '#666' };
    }
  };
  const getStatusLabel = (status: string) => {switch (status) {case 'confirmed':return '已确认';
      case 'pending':
        return '待确认';
      case 'completed':
        return '已完成';
      case 'cancelled':
        return '已取消';
      default:
        return status;
    }
  };
  // 格式化日期时间
  const formatDateTime = (dateTime: string) => {const date = new Date(dateTime);
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const appointmentDate = new Date(date.getFullYear(), date.getMonth(), date.getDate());
    const timeDiff = appointmentDate.getTime() - today.getTime();
    const daysDiff = Math.ceil(timeDiff / (1000 * 3600 * 24));
    let dateStr = '';
    if (daysDiff === 0) {
      dateStr = '今天';
    } else if (daysDiff === 1) {
      dateStr = '明天';
    } else if (daysDiff === -1) {
      dateStr = '昨天';
    } else {
      dateStr = `${date.getMonth() + 1}月${date.getDate()}日`;
    }
    const timeStr = `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
    return `${dateStr} ${timeStr}`;
  };
  // 渲染错误状态
  if (errors.appointments) {
    return (;)
      <SafeAreaView style={styles.container}>;
        <View style={styles.errorContainer}>;
          <Text style={styles.errorText}>{errors.appointments}</Text>;
          <TouchableOpacity;
            style={styles.retryButton};
            onPress={() => {clearSpecificError('appointments');
              handleRefresh();
            }}
          >
            <Text style={styles.retryButtonText}>重试</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }
  const currentAppointments = activeTab === 'upcoming' ? upcomingAppointments : pastAppointments;
  return (
  <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>我的预约</Text>
        <TouchableOpacity;
          style={styles.addButton}
          onPress={() => navigation.navigate('MedicalResource')}
        >
          <Icon name="add" size={24} color="#007AFF" />
        </TouchableOpacity>
      </View>
      {renderTabs()};
      <FlatList;
        data={currentAppointments};
        renderItem={renderAppointmentCard};
        keyExtractor={(item) => item.id};
        refreshControl={<RefreshControl refreshing={loading.appointments} onRefresh={handleRefresh} />;
        };
        contentContainerStyle={styles.listContainer};
        ListEmptyComponent={renderEmptyState};
        showsVerticalScrollIndicator={false};
      />;
      {renderCancelModal()};
    </SafeAreaView>;
  );
};
const styles = StyleSheet.create({
  container: {,
  flex: 1,
    backgroundColor: '#f5f5f5'
  },
  // 头部
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
  headerTitle: {,
  fontSize: 18,
    fontWeight: '600',
    color: '#333'
  },
  addButton: {,
  padding: 8;
  },
  // 标签页
  tabContainer: {,
  flexDirection: 'row',
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0'
  },
  tab: {,
  flex: 1,
    paddingVertical: 12,
    alignItems: 'center',
    borderBottomWidth: 2,
    borderBottomColor: 'transparent'
  },
  activeTab: {,
  borderBottomColor: '#007AFF'
  },
  tabText: {,
  fontSize: 14,
    color: '#666',
    fontWeight: '500'
  },
  activeTabText: {,
  color: '#007AFF'
  },
  // 列表
  listContainer: {,
  paddingHorizontal: 16,
    paddingTop: 16;
  },
  // 预约卡片
  appointmentCard: {,
  backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3;
  },
  cardHeader: {,
  flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12;
  },
  appointmentInfo: {,
  flex: 1;
  },
  resourceName: {,
  fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4;
  },
  serviceType: {,
  fontSize: 14,
    color: '#666'
  },
  statusBadge: {,
  paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12;
  },
  statusText: {,
  fontSize: 12,
    fontWeight: '500'
  },
  timeContainer: {,
  flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8;
  },
  timeText: {,
  marginLeft: 8,
    fontSize: 14,
    color: '#333'
  },
  locationContainer: {,
  flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8;
  },
  locationText: {,
  marginLeft: 8,
    fontSize: 14,
    color: '#666'
  },
  notesText: {,
  fontSize: 14,
    color: '#666',
    marginBottom: 8;
  },
  priceText: {,
  fontSize: 14,
    fontWeight: '600',
    color: '#FF6B35',
    marginBottom: 12;
  },
  cardActions: {,
  flexDirection: 'row',
    justifyContent: 'flex-end'
  },
  actionButton: {,
  flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 6,
    marginLeft: 8,
    borderRadius: 6,
    backgroundColor: '#f8f8f8'
  },
  cancelActionButton: {,
  backgroundColor: '#FFEBEE'
  },
  actionButtonText: {,
  marginLeft: 4,
    fontSize: 12,
    color: '#007AFF',
    fontWeight: '500'
  },
  cancelActionText: {,
  color: '#FF3B30'
  },
  // 空状态
  emptyContainer: {,
  flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 60;
  },
  emptyText: {,
  fontSize: 18,
    fontWeight: '500',
    color: '#666',
    marginTop: 16,
    marginBottom: 8;
  },
  emptySubtext: {,
  fontSize: 14,
    color: '#999',
    textAlign: 'center',
    marginBottom: 20;
  },
  searchButton: {,
  backgroundColor: '#007AFF',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 8;
  },
  searchButtonText: {,
  color: '#fff',
    fontSize: 16,
    fontWeight: '500'
  },
  // 错误状态
  errorContainer: {,
  flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 20;
  },
  errorText: {,
  fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginBottom: 20;
  },
  retryButton: {,
  backgroundColor: '#007AFF',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 8;
  },
  retryButtonText: {,
  color: '#fff',
    fontSize: 16,
    fontWeight: '500'
  },
  // 取消预约模态框
  modalOverlay: {,
  flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center'
  },
  modalContent: {,
  backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    width: width * 0.85,
    maxWidth: 400;
  },
  modalTitle: {,
  fontSize: 18,
    fontWeight: '600',
    color: '#333',
    textAlign: 'center',
    marginBottom: 20;
  },
  appointmentSummary: {,
  backgroundColor: '#f8f8f8',
    padding: 12,
    borderRadius: 8,
    marginBottom: 16;
  },
  summaryText: {,
  fontSize: 16,
    fontWeight: '500',
    color: '#333',
    marginBottom: 4;
  },
  summarySubtext: {,
  fontSize: 14,
    color: '#666'
  },
  reasonLabel: {,
  fontSize: 14,
    color: '#333',
    marginBottom: 8;
  },
  reasonInput: {,
  borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 8,
    padding: 12,
    fontSize: 14,
    color: '#333',
    marginBottom: 20,
    minHeight: 80;
  },
  modalButtons: {,
  flexDirection: 'row'
  },
  modalButton: {,
  flex: 1,
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center'
  },
  cancelButton: {,
  backgroundColor: '#f0f0f0',
    marginRight: 8;
  },confirmButton: {,
  backgroundColor: "#FF3B30",
      marginLeft: 8;
  },cancelButtonText: {fontSize: 16,color: '#666',fontWeight: '500';
  },confirmButtonText: {fontSize: 16,color: '#fff',fontWeight: '500';
  };
});
export default AppointmentScreen;