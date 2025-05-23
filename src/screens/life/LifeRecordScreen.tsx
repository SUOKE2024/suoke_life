import React, { useState } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  Alert,
  Dimensions,
} from 'react-native';
import {
  Appbar,
  Card,
  Title,
  Paragraph,
  Button,
  TextInput,
  Chip,
  Text,
  Surface,
  FAB,
  Portal,
  Modal,
  Divider,
  SegmentedButtons,
} from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { useTheme } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import DateTimePicker from '@react-native-community/datetimepicker';

const { width } = Dimensions.get('window');

interface LifeRecordScreenProps {
  navigation: any;
}

interface LifeRecord {
  id: string;
  type: 'diet' | 'exercise' | 'sleep' | 'mood' | 'symptom' | 'medication';
  title: string;
  description: string;
  timestamp: Date;
  tags: string[];
  data?: any;
}

const LifeRecordScreen: React.FC<LifeRecordScreenProps> = ({ navigation }) => {
  const theme = useTheme();
  const { t } = useTranslation();
  const [records, setRecords] = useState<LifeRecord[]>([
    {
      id: '1',
      type: 'diet',
      title: '早餐',
      description: '燕麦粥、鸡蛋、牛奶',
      timestamp: new Date(2024, 2, 15, 8, 0),
      tags: ['健康', '营养均衡'],
      data: { calories: 350 },
    },
    {
      id: '2',
      type: 'exercise',
      title: '晨跑',
      description: '公园慢跑30分钟',
      timestamp: new Date(2024, 2, 15, 7, 0),
      tags: ['有氧运动', '户外'],
      data: { duration: 30, distance: 3.5 },
    },
    {
      id: '3',
      type: 'sleep',
      title: '睡眠记录',
      description: '睡眠质量良好',
      timestamp: new Date(2024, 2, 14, 23, 0),
      tags: ['深度睡眠'],
      data: { duration: 8, quality: 'good' },
    },
  ]);

  const [showModal, setShowModal] = useState(false);
  const [selectedType, setSelectedType] = useState<LifeRecord['type']>('diet');
  const [newRecord, setNewRecord] = useState({
    title: '',
    description: '',
    tags: [] as string[],
  });
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [filterType, setFilterType] = useState<string>('all');

  const recordTypes = [
    { value: 'diet', label: '饮食', icon: 'food-apple', color: '#FF9800' },
    { value: 'exercise', label: '运动', icon: 'run', color: '#4CAF50' },
    { value: 'sleep', label: '睡眠', icon: 'sleep', color: '#3F51B5' },
    { value: 'mood', label: '情绪', icon: 'emoticon-happy', color: '#E91E63' },
    { value: 'symptom', label: '症状', icon: 'medical-bag', color: '#F44336' },
    { value: 'medication', label: '用药', icon: 'pill', color: '#9C27B0' },
  ];

  const filterOptions = [
    { value: 'all', label: '全部' },
    { value: 'diet', label: '饮食' },
    { value: 'exercise', label: '运动' },
    { value: 'sleep', label: '睡眠' },
    { value: 'mood', label: '情绪' },
    { value: 'symptom', label: '症状' },
    { value: 'medication', label: '用药' },
  ];

  const getTypeConfig = (type: LifeRecord['type']) => {
    return recordTypes.find(t => t.value === type) || recordTypes[0];
  };

  const filteredRecords = filterType === 'all' 
    ? records 
    : records.filter(record => record.type === filterType);

  const sortedRecords = filteredRecords.sort((a, b) => 
    b.timestamp.getTime() - a.timestamp.getTime()
  );

  const handleAddRecord = () => {
    if (!newRecord.title.trim()) {
      Alert.alert('提示', '请输入记录标题');
      return;
    }

    const record: LifeRecord = {
      id: Date.now().toString(),
      type: selectedType,
      title: newRecord.title,
      description: newRecord.description,
      timestamp: selectedDate,
      tags: newRecord.tags,
    };

    setRecords([...records, record]);
    setShowModal(false);
    setNewRecord({ title: '', description: '', tags: [] });
    setSelectedDate(new Date());
  };

  const handleDeleteRecord = (id: string) => {
    Alert.alert(
      '确认删除',
      '确定要删除这条记录吗？',
      [
        { text: '取消', style: 'cancel' },
        {
          text: '删除',
          style: 'destructive',
          onPress: () => {
            setRecords(records.filter(record => record.id !== id));
          },
        },
      ]
    );
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatDate = (date: Date) => {
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    if (date.toDateString() === today.toDateString()) {
      return '今天';
    } else if (date.toDateString() === yesterday.toDateString()) {
      return '昨天';
    } else {
      return date.toLocaleDateString('zh-CN', {
        month: 'short',
        day: 'numeric',
      });
    }
  };

  const groupRecordsByDate = (records: LifeRecord[]) => {
    const groups: { [key: string]: LifeRecord[] } = {};
    
    records.forEach(record => {
      const dateKey = record.timestamp.toDateString();
      if (!groups[dateKey]) {
        groups[dateKey] = [];
      }
      groups[dateKey].push(record);
    });

    return Object.entries(groups).map(([dateKey, records]) => ({
      date: new Date(dateKey),
      records: records.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime()),
    }));
  };

  const recordGroups = groupRecordsByDate(sortedRecords);

  const renderRecordCard = (record: LifeRecord) => {
    const typeConfig = getTypeConfig(record.type);
    
    return (
      <Card key={record.id} style={styles.recordCard}>
        <Card.Content>
          <View style={styles.recordHeader}>
            <View style={styles.recordTypeInfo}>
              <View style={[styles.typeIcon, { backgroundColor: typeConfig.color }]}>
                <Icon name={typeConfig.icon} size={20} color="white" />
              </View>
              <View style={styles.recordInfo}>
                <Text style={styles.recordTitle}>{record.title}</Text>
                <Text style={styles.recordTime}>{formatTime(record.timestamp)}</Text>
              </View>
            </View>
            <Button
              mode="text"
              onPress={() => handleDeleteRecord(record.id)}
              textColor={theme.colors.error}
              compact
            >
              删除
            </Button>
          </View>
          
          {record.description && (
            <Paragraph style={styles.recordDescription}>
              {record.description}
            </Paragraph>
          )}
          
          {record.tags.length > 0 && (
            <View style={styles.tagsContainer}>
              {record.tags.map((tag, index) => (
                <Chip key={index} style={styles.tag} textStyle={styles.tagText}>
                  {tag}
                </Chip>
              ))}
            </View>
          )}
          
          {record.data && (
            <View style={styles.dataContainer}>
              {record.type === 'diet' && record.data.calories && (
                <Text style={styles.dataText}>热量: {record.data.calories} kcal</Text>
              )}
              {record.type === 'exercise' && (
                <View style={styles.exerciseData}>
                  {record.data.duration && (
                    <Text style={styles.dataText}>时长: {record.data.duration}分钟</Text>
                  )}
                  {record.data.distance && (
                    <Text style={styles.dataText}>距离: {record.data.distance}km</Text>
                  )}
                </View>
              )}
              {record.type === 'sleep' && (
                <View style={styles.sleepData}>
                  {record.data.duration && (
                    <Text style={styles.dataText}>时长: {record.data.duration}小时</Text>
                  )}
                  {record.data.quality && (
                    <Text style={styles.dataText}>
                      质量: {record.data.quality === 'good' ? '良好' : '一般'}
                    </Text>
                  )}
                </View>
              )}
            </View>
          )}
        </Card.Content>
      </Card>
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      <Appbar.Header>
        <Appbar.BackAction onPress={() => navigation.goBack()} />
        <Appbar.Content title="生活记录" />
        <Appbar.Action icon="chart-line" onPress={() => navigation.navigate('HealthDataChart')} />
      </Appbar.Header>

      <View style={styles.content}>
        {/* 筛选器 */}
        <Surface style={styles.filterContainer}>
          <ScrollView horizontal showsHorizontalScrollIndicator={false}>
            <SegmentedButtons
              value={filterType}
              onValueChange={setFilterType}
              buttons={filterOptions}
              style={styles.segmentedButtons}
            />
          </ScrollView>
        </Surface>

        {/* 记录列表 */}
        <ScrollView style={styles.recordsList}>
          {recordGroups.length === 0 ? (
            <Surface style={styles.emptyContainer}>
              <Icon name="clipboard-text-outline" size={64} color={theme.colors.onSurfaceVariant} />
              <Title style={styles.emptyTitle}>暂无记录</Title>
              <Paragraph style={styles.emptyDescription}>
                点击右下角的按钮开始记录您的生活
              </Paragraph>
            </Surface>
          ) : (
            recordGroups.map((group, groupIndex) => (
              <View key={groupIndex} style={styles.dateGroup}>
                <Text style={styles.dateHeader}>{formatDate(group.date)}</Text>
                {group.records.map(record => renderRecordCard(record))}
              </View>
            ))
          )}
        </ScrollView>

        {/* 添加按钮 */}
        <FAB
          icon="plus"
          style={styles.fab}
          onPress={() => setShowModal(true)}
        />

        {/* 添加记录模态框 */}
        <Portal>
          <Modal
            visible={showModal}
            onDismiss={() => setShowModal(false)}
            contentContainerStyle={styles.modal}
          >
            <ScrollView>
              <Title style={styles.modalTitle}>添加生活记录</Title>
              
              {/* 记录类型选择 */}
              <Text style={styles.sectionLabel}>记录类型</Text>
              <View style={styles.typeSelector}>
                {recordTypes.map(type => (
                  <Button
                    key={type.value}
                    mode={selectedType === type.value ? 'contained' : 'outlined'}
                    onPress={() => setSelectedType(type.value as LifeRecord['type'])}
                    style={styles.typeButton}
                    icon={type.icon}
                    compact
                  >
                    {type.label}
                  </Button>
                ))}
              </View>

              {/* 时间选择 */}
              <Text style={styles.sectionLabel}>时间</Text>
              <Button
                mode="outlined"
                onPress={() => setShowDatePicker(true)}
                icon="clock-outline"
                style={styles.dateButton}
              >
                {selectedDate.toLocaleString('zh-CN')}
              </Button>

              {showDatePicker && (
                <DateTimePicker
                  value={selectedDate}
                  mode="datetime"
                  display="default"
                  onChange={(event: any, date?: Date) => {
                    setShowDatePicker(false);
                    if (date) setSelectedDate(date);
                  }}
                />
              )}

              {/* 标题输入 */}
              <TextInput
                label="标题"
                value={newRecord.title}
                onChangeText={(text) => setNewRecord({ ...newRecord, title: text })}
                style={styles.input}
                mode="outlined"
              />

              {/* 描述输入 */}
              <TextInput
                label="描述"
                value={newRecord.description}
                onChangeText={(text) => setNewRecord({ ...newRecord, description: text })}
                style={styles.input}
                mode="outlined"
                multiline
                numberOfLines={3}
              />

              <Divider style={styles.divider} />

              {/* 操作按钮 */}
              <View style={styles.modalActions}>
                <Button
                  mode="outlined"
                  onPress={() => setShowModal(false)}
                  style={styles.modalButton}
                >
                  取消
                </Button>
                <Button
                  mode="contained"
                  onPress={handleAddRecord}
                  style={styles.modalButton}
                >
                  保存
                </Button>
              </View>
            </ScrollView>
          </Modal>
        </Portal>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  content: {
    flex: 1,
  },
  filterContainer: {
    padding: 16,
    marginBottom: 8,
  },
  segmentedButtons: {
    minWidth: width - 32,
  },
  recordsList: {
    flex: 1,
    padding: 16,
  },
  dateGroup: {
    marginBottom: 16,
  },
  dateHeader: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 8,
    color: '#666',
  },
  recordCard: {
    marginBottom: 8,
    borderRadius: 12,
  },
  recordHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  recordTypeInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  typeIcon: {
    width: 36,
    height: 36,
    borderRadius: 18,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  recordInfo: {
    flex: 1,
  },
  recordTitle: {
    fontSize: 16,
    fontWeight: '500',
  },
  recordTime: {
    fontSize: 12,
    color: '#666',
    marginTop: 2,
  },
  recordDescription: {
    marginBottom: 8,
    fontSize: 14,
    lineHeight: 20,
  },
  tagsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 8,
  },
  tag: {
    marginRight: 8,
    marginBottom: 4,
    height: 24,
  },
  tagText: {
    fontSize: 10,
  },
  dataContainer: {
    marginTop: 8,
  },
  dataText: {
    fontSize: 12,
    color: '#666',
    marginBottom: 2,
  },
  exerciseData: {
    flexDirection: 'row',
    gap: 16,
  },
  sleepData: {
    flexDirection: 'row',
    gap: 16,
  },
  emptyContainer: {
    alignItems: 'center',
    padding: 32,
    borderRadius: 12,
    marginTop: 32,
  },
  emptyTitle: {
    marginTop: 16,
    marginBottom: 8,
  },
  emptyDescription: {
    textAlign: 'center',
    color: '#666',
  },
  fab: {
    position: 'absolute',
    margin: 16,
    right: 0,
    bottom: 0,
  },
  modal: {
    backgroundColor: 'white',
    padding: 20,
    margin: 20,
    borderRadius: 12,
    maxHeight: '80%',
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 16,
    textAlign: 'center',
  },
  sectionLabel: {
    fontSize: 14,
    fontWeight: '500',
    marginBottom: 8,
    marginTop: 16,
  },
  typeSelector: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginBottom: 8,
  },
  typeButton: {
    marginBottom: 8,
  },
  dateButton: {
    marginBottom: 16,
  },
  input: {
    marginBottom: 16,
  },
  divider: {
    marginVertical: 16,
  },
  modalActions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: 16,
  },
  modalButton: {
    flex: 1,
  },
});

export default LifeRecordScreen;