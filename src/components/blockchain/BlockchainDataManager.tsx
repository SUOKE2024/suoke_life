import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { Card, Button, Loading, Input } from '../ui';
import { colors, spacing, typography } from '../../constants/theme';
import { useAppSelector, useAppDispatch } from '../../store';





import React, { useState, useEffect, useCallback } from 'react';
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Dimensions,
  Animated,
  RefreshControl,
  Alert,
  Modal,
} from 'react-native';

const { width } = Dimensions.get('window');

interface BlockchainRecord {
  id: string;
  hash: string;
  timestamp: Date;
  dataType: 'health' | 'diagnosis' | 'prescription' | 'report';
  title: string;
  description: string;
  size: number;
  status: 'pending' | 'confirmed' | 'failed';
  confirmations: number;
  gasUsed?: number;
  txHash?: string;
  encrypted: boolean;
  shared: boolean;
}

interface DataUploadRequest {
  dataType: 'health' | 'diagnosis' | 'prescription' | 'report';
  title: string;
  description: string;
  data: any;
  encrypt: boolean;
  shareWith: string[];
}

interface BlockchainDataManagerProps {
  onRecordPress?: (record: BlockchainRecord) => void;
  onUploadComplete?: (record: BlockchainRecord) => void;
}

export const BlockchainDataManager: React.FC<BlockchainDataManagerProps> = ({
  onRecordPress,
  onUploadComplete,
}) => {
  const dispatch = useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useAppDispatch(), []), []), []), []), []), []);
  const { profile: user } = useAppSelector(state => state.user);
  
  const [records, setRecords] = useState<BlockchainRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [uploadModalVisible, setUploadModalVisible] = useState(false);
  const [verifyModalVisible, setVerifyModalVisible] = useState(false);
  const [selectedTab, setSelectedTab] = useState<'all' | 'health' | 'diagnosis' | 'prescription' | 'report'>('all');
  const [animatedValue] = useState(new Animated.Value(0));

  // 模拟区块链记录数据
  const mockRecords: BlockchainRecord[] = [
    {
      id: '1',
      hash: '0x1a2b3c4d5e6f7890abcdef1234567890abcdef12',
      timestamp: new Date(),
      dataType: 'health',
      title: '健康体检报告',
      description: '2024年度全面健康体检数据',
      size: 2.5,
      status: 'confirmed',
      confirmations: 12,
      gasUsed: 21000,
      txHash: '0xabcdef1234567890abcdef1234567890abcdef12',
      encrypted: true,
      shared: false,
    },
    {
      id: '2',
      hash: '0x2b3c4d5e6f7890abcdef1234567890abcdef123a',
      timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
      dataType: 'diagnosis',
      title: '中医辨证诊断',
      description: '气虚质体质辨识及调理方案',
      size: 1.8,
      status: 'confirmed',
      confirmations: 8,
      gasUsed: 18500,
      txHash: '0xbcdef1234567890abcdef1234567890abcdef123',
      encrypted: true,
      shared: true,
    },
    {
      id: '3',
      hash: '0x3c4d5e6f7890abcdef1234567890abcdef123ab2',
      timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000),
      dataType: 'prescription',
      title: '个性化营养方案',
      description: 'AI生成的个性化营养补充建议',
      size: 0.9,
      status: 'pending',
      confirmations: 0,
      encrypted: false,
      shared: false,
    },
  ];

  useEffect(() => {
    setRecords(mockRecords);
    
    // 启动动画
    Animated.timing(animatedValue, {
      toValue: 1,
      duration: 800,
      useNativeDriver: true,
    }).start();
  }, []);

  const onRefresh = useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useCallback(async () => {
    setRefreshing(true), []), []), []), []), []), []);
    // 模拟数据刷新
    await new Promise<void>(resolve => setTimeout(() => resolve(), 1500));
    setRefreshing(false);
  }, []);

  const handleUploadData = useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useCallback(async (request: DataUploadRequest) => {
    setLoading(true), []), []), []), []), []), []);
    try {
      // 模拟上链过程
      await new Promise<void>(resolve => setTimeout(() => resolve(), 2000));
      
      const newRecord: BlockchainRecord = {
        id: Date.now().toString(),
        hash: '0x' + Math.random().toString(16).substr(2, 40),
        timestamp: new Date(),
        dataType: request.dataType,
        title: request.title,
        description: request.description,
        size: Math.random() * 3 + 0.5,
        status: 'pending',
        confirmations: 0,
        encrypted: request.encrypt,
        shared: request.shareWith.length > 0,
      };
      
      setRecords(prev => [newRecord, ...prev]);
      onUploadComplete?.(newRecord);
      setUploadModalVisible(false);
      
      Alert.alert('上链成功', '数据已成功提交到区块链网络');
    } catch (error) {
      Alert.alert('上链失败', '数据上链过程中发生错误');
    } finally {
      setLoading(false);
    }
  }, [onUploadComplete]);

  const handleVerifyData = useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useCallback(async (hash: string) => {
    setLoading(true), []), []), []), []), []), []);
    try {
      // 模拟验证过程
      await new Promise<void>(resolve => setTimeout(() => resolve(), 1000));
      Alert.alert('验证成功', '数据完整性验证通过，未发现篡改');
    } catch (error) {
      Alert.alert('验证失败', '数据验证过程中发生错误');
    } finally {
      setLoading(false);
    }
  }, []);

  const getStatusColor = useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useCallback( (status: string) => {, []), []), []), []), []), []), []);
    switch (status) {
      case 'confirmed': return colors.success;
      case 'pending': return colors.warning;
      case 'failed': return colors.error;
      default: return colors.textSecondary;
    }
  };

  const getDataTypeIcon = useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useCallback( (dataType: string) => {, []), []), []), []), []), []), []);
    switch (dataType) {
      case 'health': return 'fitness';
      case 'diagnosis': return 'medical';
      case 'prescription': return 'document-text';
      case 'report': return 'analytics';
      default: return 'document';
    }
  };

  const getDataTypeLabel = useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useCallback( (dataType: string) => {, []), []), []), []), []), []), []);
    switch (dataType) {
      case 'health': return '健康数据';
      case 'diagnosis': return '诊断记录';
      case 'prescription': return '处方方案';
      case 'report': return '检查报告';
      default: return '其他';
    }
  };

  const filteredRecords = useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => selectedTab === 'all' 
    ? records 
    : records.filter(record => record.dataType === selectedTab), []), []), []), []), []), []);

  // TODO: 将内联组件移到组件外部
const renderTabSelector = useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => () => (
    <View style={styles.tabSelector}>
      {(['all', 'health', 'diagnosis', 'prescription', 'report'] as const).map((tab) => (
        <TouchableOpacity
          key={tab}
          style={[
            styles.tabButton,
            selectedTab === tab && styles.tabButtonActive,
          ]}
          onPress={() => setSelectedTab(tab)}
        >
          <Text
            style={[
              styles.tabButtonText,
              selectedTab === tab && styles.tabButtonTextActive,
            ]}
          >
            {tab === 'all' ? '全部' : getDataTypeLabel(tab)}
          </Text>
        </TouchableOpacity>
      ))}
    </View>
  ), []), []), []), []), []), []);

  const renderStatsCards = useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useCallback( () => {, []), []), []), []), []), []), []);
    const totalRecords = useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => records.length, []), []), []), []), []), []);
    const confirmedRecords = useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => records.filter(r => r.status === 'confirmed').length, []), []), []), []), []), []);
    const encryptedRecords = useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => records.filter(r => r.encrypted).length, []), []), []), []), []), []);
    const sharedRecords = useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => records.filter(r => r.shared).length, []), []), []), []), []), []);

    return (
      <View style={styles.statsContainer}>
        <View style={styles.statsCard}>
          <Text style={styles.statsValue}>{totalRecords}</Text>
          <Text style={styles.statsLabel}>总记录数</Text>
        </View>
        <View style={styles.statsCard}>
          <Text style={styles.statsValue}>{confirmedRecords}</Text>
          <Text style={styles.statsLabel}>已确认</Text>
        </View>
        <View style={styles.statsCard}>
          <Text style={styles.statsValue}>{encryptedRecords}</Text>
          <Text style={styles.statsLabel}>已加密</Text>
        </View>
        <View style={styles.statsCard}>
          <Text style={styles.statsValue}>{sharedRecords}</Text>
          <Text style={styles.statsLabel}>已共享</Text>
        </View>
      </View>
    );
  };

  const renderRecordCard = useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => (record: BlockchainRecord, index: number) => (
    <Animated.View
      key={record.id}
      style={[
        styles.recordCard,
        {
          opacity: animatedValue,
          transform: [
            {
              translateY: animatedValue.interpolate({
                inputRange: [0, 1],
                outputRange: [50, 0],
              }),
            },
          ],
        },
      ]}
    >
      <TouchableOpacity
        style={styles.recordCardContent}
        onPress={() => onRecordPress?.(record)}
        activeOpacity={0.8}
      >
        <View style={styles.recordHeader}>
          <View style={styles.recordIcon}>
            <Ionicons 
              name={getDataTypeIcon(record.dataType) as any} 
              size={24} 
              color={colors.primary} 
            />
          </View>
          <View style={styles.recordInfo}>
            <Text style={styles.recordTitle}>{record.title}</Text>
            <Text style={styles.recordDescription}>{record.description}</Text>
          </View>
          <View style={[styles.statusBadge, { backgroundColor: getStatusColor(record.status) }]}>
            <Text style={styles.statusText}>
              {record.status === 'confirmed' ? '已确认' : 
               record.status === 'pending' ? '待确认' : '失败'}
            </Text>
          </View>
        </View>

        <View style={styles.recordDetails}>
          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>哈希值:</Text>
            <Text style={styles.detailValue} numberOfLines={1}>
              {record.hash}
            </Text>
          </View>
          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>时间:</Text>
            <Text style={styles.detailValue}>
              {record.timestamp.toLocaleString('zh-CN')}
            </Text>
          </View>
          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>大小:</Text>
            <Text style={styles.detailValue}>{record.size.toFixed(1)} MB</Text>
          </View>
          {record.confirmations > 0 && (
            <View style={styles.detailRow}>
              <Text style={styles.detailLabel}>确认数:</Text>
              <Text style={styles.detailValue}>{record.confirmations}</Text>
            </View>
          )}
        </View>

        <View style={styles.recordActions}>
          <View style={styles.recordTags}>
            {record.encrypted && (
              <View style={styles.tag}>
                <Ionicons name="lock-closed" size={12} color={colors.success} />
                <Text style={styles.tagText}>加密</Text>
              </View>
            )}
            {record.shared && (
              <View style={styles.tag}>
                <Ionicons name="share" size={12} color={colors.info} />
                <Text style={styles.tagText}>共享</Text>
              </View>
            )}
          </View>
          <TouchableOpacity
            style={styles.verifyButton}
            onPress={() => handleVerifyData(record.hash)}
          >
            <Ionicons name="shield-checkmark" size={16} color={colors.primary} />
            <Text style={styles.verifyButtonText}>验证</Text>
          </TouchableOpacity>
        </View>
      </TouchableOpacity>
    </Animated.View>
  ), []), []), []), []), []), []);

  // TODO: 将内联组件移到组件外部
const renderUploadModal = useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => () => (
    <Modal
      visible={uploadModalVisible}
      animationType="slide"
      presentationStyle="pageSheet"
      onRequestClose={() => setUploadModalVisible(false)}
    >
      <SafeAreaView style={styles.modalContainer}>
        <View style={styles.modalHeader}>
          <Text style={styles.modalTitle}>上传数据到区块链</Text>
          <TouchableOpacity
            style={styles.modalCloseButton}
            onPress={() => setUploadModalVisible(false)}
          >
            <Ionicons name="close" size={24} color={colors.textPrimary} />
          </TouchableOpacity>
        </View>
        
        <ScrollView style={styles.modalContent}>
          <Text style={styles.modalDescription}>
            将您的健康数据安全地存储到区块链上，确保数据的不可篡改性和隐私保护。
          </Text>
          
          {/* 这里可以添加上传表单 */}
          <View style={styles.uploadForm}>
            <Text style={styles.formLabel}>数据类型</Text>
            <View style={styles.typeSelector}>
              {(['health', 'diagnosis', 'prescription', 'report'] as const).map((type) => (
                <TouchableOpacity
                  key={type}
                  style={styles.typeOption}
                >
                  <Ionicons 
                    name={getDataTypeIcon(type) as any} 
                    size={20} 
                    color={colors.primary} 
                  />
                  <Text style={styles.typeOptionText}>{getDataTypeLabel(type)}</Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        </ScrollView>
        
        <View style={styles.modalActions}>
          <Button
            title="取消"
            variant="outline"
            onPress={() => setUploadModalVisible(false)}
            style={styles.modalButton}
          />
          <Button
            title="上传"
            onPress={() => {
              // 模拟上传
              handleUploadData({
                dataType: 'health',
                title: '新健康数据',
                description: '用户上传的健康数据',
                data: {},
                encrypt: true,
                shareWith: [],
              }), []), []), []), []), []), []);
            }}
            style={styles.modalButton}
          />
        </View>
      </SafeAreaView>
    </Modal>
  );

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            tintColor={colors.primary}
            colors={[colors.primary]}
          />
        }
        showsVerticalScrollIndicator={false}
      >
        {/* 头部 */}
        <View style={styles.header}>
          <Text style={styles.title}>区块链数据管理</Text>
          <View style={styles.headerActions}>
            <TouchableOpacity
              style={styles.uploadButton}
              onPress={() => setUploadModalVisible(true)}
            >
              <Ionicons name="cloud-upload" size={20} color={colors.white} />
              <Text style={styles.uploadButtonText}>上传</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* 统计卡片 */}
        {renderStatsCards()}

        {/* 标签选择器 */}
        {renderTabSelector()}

        {/* 记录列表 */}
        <View style={styles.recordsList}>
          {filteredRecords.map((record, index) => renderRecordCard(record, index))}
        </View>
      </ScrollView>

      {/* 上传模态框 */}
      {renderUploadModal()}

      {/* 加载指示器 */}
      {loading && (
        <View style={styles.loadingOverlay}>
          <Loading />
        </View>
      )}
    </SafeAreaView>
  );
};

const styles = useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => useMemo(() => StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  scrollView: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
  },
  title: {
    fontSize: typography.fontSize['2xl'],
    color: colors.textPrimary,
    fontWeight: '700',
  },
  headerActions: {
    flexDirection: 'row',
    gap: spacing.sm,
  },
  uploadButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.primary,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: 8,
    gap: spacing.xs,
  },
  uploadButtonText: {
    color: colors.white,
    fontSize: typography.fontSize.sm,
    fontWeight: '600',
  },
  statsContainer: {
    flexDirection: 'row',
    paddingHorizontal: spacing.lg,
    marginBottom: spacing.lg,
    gap: spacing.sm,
  },
  statsCard: {
    flex: 1,
    backgroundColor: colors.surfaceSecondary,
    borderRadius: 12,
    padding: spacing.md,
    alignItems: 'center',
  },
  statsValue: {
    fontSize: typography.fontSize.xl,
    color: colors.primary,
    fontWeight: '700',
    marginBottom: spacing.xs,
  },
  statsLabel: {
    fontSize: typography.fontSize.xs,
    color: colors.textSecondary,
    textAlign: 'center',
  },
  tabSelector: {
    flexDirection: 'row',
    marginHorizontal: spacing.lg,
    marginBottom: spacing.lg,
    backgroundColor: colors.surfaceSecondary,
    borderRadius: 12,
    padding: spacing.xs,
  },
  tabButton: {
    flex: 1,
    paddingVertical: spacing.sm,
    alignItems: 'center',
    borderRadius: 8,
  },
  tabButtonActive: {
    backgroundColor: colors.primary,
  },
  tabButtonText: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    fontWeight: '500',
  },
  tabButtonTextActive: {
    color: colors.white,
    fontWeight: '600',
  },
  recordsList: {
    paddingHorizontal: spacing.lg,
  },
  recordCard: {
    marginBottom: spacing.md,
    borderRadius: 16,
    backgroundColor: colors.surfaceSecondary,
    overflow: 'hidden',
  },
  recordCardContent: {
    padding: spacing.lg,
  },
  recordHeader: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: spacing.md,
  },
  recordIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: colors.primary + '20',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.md,
  },
  recordInfo: {
    flex: 1,
  },
  recordTitle: {
    fontSize: typography.fontSize.base,
    color: colors.textPrimary,
    fontWeight: '600',
    marginBottom: spacing.xs,
  },
  recordDescription: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
  },
  statusBadge: {
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: 6,
  },
  statusText: {
    fontSize: typography.fontSize.xs,
    color: colors.white,
    fontWeight: '600',
  },
  recordDetails: {
    marginBottom: spacing.md,
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.xs,
  },
  detailLabel: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    fontWeight: '500',
  },
  detailValue: {
    fontSize: typography.fontSize.sm,
    color: colors.textPrimary,
    flex: 1,
    textAlign: 'right',
    marginLeft: spacing.sm,
  },
  recordActions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  recordTags: {
    flexDirection: 'row',
    gap: spacing.xs,
  },
  tag: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.gray100,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: 6,
    gap: spacing.xs,
  },
  tagText: {
    fontSize: typography.fontSize.xs,
    color: colors.textSecondary,
    fontWeight: '500',
  },
  verifyButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.primary + '20',
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: 6,
    gap: spacing.xs,
  },
  verifyButtonText: {
    fontSize: typography.fontSize.xs,
    color: colors.primary,
    fontWeight: '600',
  },
  modalContainer: {
    flex: 1,
    backgroundColor: colors.background,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  modalTitle: {
    fontSize: typography.fontSize.lg,
    color: colors.textPrimary,
    fontWeight: '600',
  },
  modalCloseButton: {
    padding: spacing.sm,
  },
  modalContent: {
    flex: 1,
    paddingHorizontal: spacing.lg,
  },
  modalDescription: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    marginVertical: spacing.lg,
    lineHeight: 20,
  },
  uploadForm: {
    marginBottom: spacing.lg,
  },
  formLabel: {
    fontSize: typography.fontSize.base,
    color: colors.textPrimary,
    fontWeight: '600',
    marginBottom: spacing.sm,
  },
  typeSelector: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
  },
  typeOption: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surfaceSecondary,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: 8,
    gap: spacing.xs,
  },
  typeOptionText: {
    fontSize: typography.fontSize.sm,
    color: colors.textPrimary,
    fontWeight: '500',
  },
  modalActions: {
    flexDirection: 'row',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    gap: spacing.sm,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  modalButton: {
    flex: 1,
  },
  loadingOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
}), []), []), []), []), []), []);

// 导出类型
export type { BlockchainRecord, DataUploadRequest, BlockchainDataManagerProps };
export type DataType = 'health' | 'diagnosis' | 'prescription' | 'report';
export type BlockchainStatus = 'pending' | 'confirmed' | 'failed'; 