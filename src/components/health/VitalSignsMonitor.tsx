import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  RefreshControl,
  Dimensions,
} from 'react-native';
import { 
  healthDataService, 
  VitalSigns, 
  DataSource,
  HealthDataType 
} from '../../services/healthDataService';

interface VitalSignsMonitorProps {
  userId: string;
}

interface VitalSignsData {
  heartRate: number[];
  bloodPressure: Array<{ systolic: number; diastolic: number; timestamp: string }>;
  temperature: number[];
  oxygenSaturation: number[];
  timestamps: string[];
}

export const VitalSignsMonitor: React.FC<VitalSignsMonitorProps> = ({ userId }) => {
  const [vitalSigns, setVitalSigns] = useState<VitalSigns[]>([]);
  const [latestVitalSigns, setLatestVitalSigns] = useState<VitalSigns | null>(null);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedPeriod, setSelectedPeriod] = useState<'24h' | '7d' | '30d'>('24h');

  useEffect(() => {
    loadVitalSigns();
    loadLatestVitalSigns();
  }, [userId, selectedPeriod]);

  const loadVitalSigns = async () => {
    try {
      setLoading(true);
      const endDate = new Date().toISOString();
      const startDate = new Date();
      
      switch (selectedPeriod) {
        case '24h':
          startDate.setHours(startDate.getHours() - 24);
          break;
        case '7d':
          startDate.setDate(startDate.getDate() - 7);
          break;
        case '30d':
          startDate.setDate(startDate.getDate() - 30);
          break;
      }

      const response = await healthDataService.getVitalSigns(
        userId,
        startDate.toISOString(),
        endDate
      );
      
      if (response.data) {
        setVitalSigns(response.data);
      }
    } catch (error) {
      console.error('加载生命体征数据失败:', error);
      Alert.alert('错误', '加载生命体征数据失败');
    } finally {
      setLoading(false);
    }
  };

  const loadLatestVitalSigns = async () => {
    try {
      const response = await healthDataService.getLatestVitalSigns(userId);
      if (response.data) {
        setLatestVitalSigns(response.data);
      }
    } catch (error) {
      console.error('加载最新生命体征失败:', error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await Promise.all([loadVitalSigns(), loadLatestVitalSigns()]);
    setRefreshing(false);
  };

  const addVitalSigns = async (type: 'heartRate' | 'bloodPressure' | 'temperature' | 'oxygenSaturation') => {
    // 这里可以打开一个模态框来输入数据
    Alert.alert('添加数据', `添加${getVitalSignLabel(type)}数据功能待实现`);
  };

  const getVitalSignLabel = (type: string): string => {
    const labels: Record<string, string> = {
      heartRate: '心率',
      bloodPressure: '血压',
      temperature: '体温',
      oxygenSaturation: '血氧饱和度',
      respiratoryRate: '呼吸频率',
      weight: '体重',
      height: '身高',
      bmi: 'BMI'
    };
    return labels[type] || type;
  };

  const getVitalSignUnit = (type: string): string => {
    const units: Record<string, string> = {
      heartRate: 'bpm',
      temperature: '°C',
      oxygenSaturation: '%',
      respiratoryRate: '/min',
      weight: 'kg',
      height: 'cm',
      bmi: ''
    };
    return units[type] || '';
  };

  const getVitalSignStatus = (type: string, value: number): 'normal' | 'warning' | 'danger' => {
    const ranges: Record<string, { normal: [number, number]; warning: [number, number] }> = {
      heartRate: { normal: [60, 100], warning: [50, 120] },
      temperature: { normal: [36.1, 37.2], warning: [35.5, 38.0] },
      oxygenSaturation: { normal: [95, 100], warning: [90, 94] },
      respiratoryRate: { normal: [12, 20], warning: [10, 25] }
    };

    const range = ranges[type];
    if (!range) return 'normal';

    if (value >= range.normal[0] && value <= range.normal[1]) {
      return 'normal';
    } else if (value >= range.warning[0] && value <= range.warning[1]) {
      return 'warning';
    } else {
      return 'danger';
    }
  };

  const getStatusColor = (status: 'normal' | 'warning' | 'danger'): string => {
    switch (status) {
      case 'normal': return '#4CAF50';
      case 'warning': return '#FF9800';
      case 'danger': return '#f44336';
      default: return '#666';
    }
  };

  const formatBloodPressure = (systolic?: number, diastolic?: number): string => {
    if (!systolic || !diastolic) return '--/--';
    return `${systolic}/${diastolic}`;
  };

  const formatDate = (timestamp: string): string => {
    return new Date(timestamp).toLocaleString('zh-CN');
  };

  const renderVitalSignCard = (
    title: string,
    value: string | number,
    unit: string,
    status: 'normal' | 'warning' | 'danger',
    onAdd: () => void
  ) => (
    <View style={styles.vitalSignCard}>
      <View style={styles.cardHeader}>
        <Text style={styles.cardTitle}>{title}</Text>
        <TouchableOpacity style={styles.addButton} onPress={onAdd}>
          <Text style={styles.addButtonText}>+</Text>
        </TouchableOpacity>
      </View>
      
      <View style={styles.cardContent}>
        <Text style={[styles.vitalValue, { color: getStatusColor(status) }]}>
          {value}
        </Text>
        <Text style={styles.vitalUnit}>{unit}</Text>
      </View>
      
      <View style={[styles.statusIndicator, { backgroundColor: getStatusColor(status) }]}>
        <Text style={styles.statusText}>
          {status === 'normal' ? '正常' : status === 'warning' ? '注意' : '异常'}
        </Text>
      </View>
    </View>
  );

  const renderPeriodSelector = () => (
    <View style={styles.periodSelector}>
      {(['24h', '7d', '30d'] as const).map((period) => (
        <TouchableOpacity
          key={period}
          style={[
            styles.periodButton,
            selectedPeriod === period && styles.periodButtonActive
          ]}
          onPress={() => setSelectedPeriod(period)}
        >
          <Text style={[
            styles.periodButtonText,
            selectedPeriod === period && styles.periodButtonTextActive
          ]}>
            {period === '24h' ? '24小时' : period === '7d' ? '7天' : '30天'}
          </Text>
        </TouchableOpacity>
      ))}
    </View>
  );

  const renderTrendChart = () => (
    <View style={styles.chartContainer}>
      <Text style={styles.chartTitle}>生命体征趋势</Text>
      <View style={styles.chartPlaceholder}>
        <Text style={styles.chartPlaceholderText}>
          图表功能需要集成图表库
        </Text>
        <Text style={styles.chartPlaceholderSubtext}>
          显示{selectedPeriod}内的数据趋势
        </Text>
      </View>
    </View>
  );

  const renderRecentData = () => (
    <View style={styles.recentDataContainer}>
      <Text style={styles.sectionTitle}>最近记录</Text>
      {vitalSigns.length === 0 ? (
        <Text style={styles.emptyText}>暂无数据</Text>
      ) : (
        vitalSigns.slice(0, 5).map((item, index) => (
          <View key={index} style={styles.recentDataItem}>
            <Text style={styles.recentDataTime}>
              {formatDate(item.timestamp)}
            </Text>
            <View style={styles.recentDataValues}>
              {item.heartRate && (
                <Text style={styles.recentDataValue}>
                  心率: {item.heartRate} bpm
                </Text>
              )}
              {item.bloodPressure && (
                <Text style={styles.recentDataValue}>
                  血压: {formatBloodPressure(item.bloodPressure.systolic, item.bloodPressure.diastolic)} mmHg
                </Text>
              )}
              {item.temperature && (
                <Text style={styles.recentDataValue}>
                  体温: {item.temperature} °C
                </Text>
              )}
              {item.oxygenSaturation && (
                <Text style={styles.recentDataValue}>
                  血氧: {item.oxygenSaturation}%
                </Text>
              )}
            </View>
          </View>
        ))
      )}
    </View>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>生命体征监控</Text>
        <Text style={styles.subtitle}>
          {latestVitalSigns ? `最后更新: ${formatDate(latestVitalSigns.timestamp)}` : '暂无数据'}
        </Text>
      </View>

      <ScrollView
        style={styles.scrollView}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {/* 生命体征卡片 */}
        <View style={styles.vitalSignsGrid}>
          {renderVitalSignCard(
            '心率',
            latestVitalSigns?.heartRate || '--',
            'bpm',
            latestVitalSigns?.heartRate 
              ? getVitalSignStatus('heartRate', latestVitalSigns.heartRate)
              : 'normal',
            () => addVitalSigns('heartRate')
          )}
          
          {renderVitalSignCard(
            '血压',
            latestVitalSigns?.bloodPressure 
              ? formatBloodPressure(latestVitalSigns.bloodPressure.systolic, latestVitalSigns.bloodPressure.diastolic)
              : '--/--',
            'mmHg',
            'normal', // 血压状态需要特殊计算
            () => addVitalSigns('bloodPressure')
          )}
          
          {renderVitalSignCard(
            '体温',
            latestVitalSigns?.temperature || '--',
            '°C',
            latestVitalSigns?.temperature 
              ? getVitalSignStatus('temperature', latestVitalSigns.temperature)
              : 'normal',
            () => addVitalSigns('temperature')
          )}
          
          {renderVitalSignCard(
            '血氧饱和度',
            latestVitalSigns?.oxygenSaturation || '--',
            '%',
            latestVitalSigns?.oxygenSaturation 
              ? getVitalSignStatus('oxygenSaturation', latestVitalSigns.oxygenSaturation)
              : 'normal',
            () => addVitalSigns('oxygenSaturation')
          )}
        </View>

        {/* 时间段选择器 */}
        {renderPeriodSelector()}

        {/* 趋势图表 */}
        {renderTrendChart()}

        {/* 最近数据 */}
        {renderRecentData()}
      </ScrollView>
    </View>
  );
};

const { width } = Dimensions.get('window');
const cardWidth = (width - 48) / 2; // 2列布局，考虑边距

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    padding: 16,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 14,
    color: '#666',
  },
  scrollView: {
    flex: 1,
  },
  vitalSignsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    padding: 16,
    justifyContent: 'space-between',
  },
  vitalSignCard: {
    width: cardWidth,
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  cardTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  addButton: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: '#007AFF',
    justifyContent: 'center',
    alignItems: 'center',
  },
  addButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  cardContent: {
    alignItems: 'center',
    marginBottom: 12,
  },
  vitalValue: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  vitalUnit: {
    fontSize: 12,
    color: '#666',
  },
  statusIndicator: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    alignSelf: 'center',
  },
  statusText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '500',
  },
  periodSelector: {
    flexDirection: 'row',
    marginHorizontal: 16,
    marginBottom: 16,
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 4,
  },
  periodButton: {
    flex: 1,
    paddingVertical: 8,
    alignItems: 'center',
    borderRadius: 6,
  },
  periodButtonActive: {
    backgroundColor: '#007AFF',
  },
  periodButtonText: {
    fontSize: 14,
    color: '#666',
    fontWeight: '500',
  },
  periodButtonTextActive: {
    color: '#fff',
  },
  chartContainer: {
    margin: 16,
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  chartTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 16,
  },
  chartPlaceholder: {
    height: 200,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
    borderWidth: 2,
    borderColor: '#e9ecef',
    borderStyle: 'dashed',
  },
  chartPlaceholderText: {
    fontSize: 16,
    color: '#666',
    marginBottom: 8,
  },
  chartPlaceholderSubtext: {
    fontSize: 14,
    color: '#999',
  },
  recentDataContainer: {
    margin: 16,
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 16,
  },
  emptyText: {
    textAlign: 'center',
    color: '#666',
    fontSize: 14,
    fontStyle: 'italic',
  },
  recentDataItem: {
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
    paddingVertical: 12,
  },
  recentDataTime: {
    fontSize: 12,
    color: '#666',
    marginBottom: 8,
  },
  recentDataValues: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  recentDataValue: {
    fontSize: 14,
    color: '#333',
    marginRight: 16,
    marginBottom: 4,
  },
}); 