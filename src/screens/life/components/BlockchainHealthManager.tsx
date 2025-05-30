import Icon from '../../../components/common/Icon';
import { colors, spacing } from '../../../constants/theme';



/**
 * 区块链健康数据管理组件
 * 提供安全的健康数据存储和管理功能
 */

import React, { useState, useEffect } from 'react';
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Modal,
  Alert,
  Switch,
  ActivityIndicator,
} from 'react-native';

interface HealthDataRecord {
  id: string;
  type: 'diagnosis' | 'medication' | 'test_result' | 'vital_signs' | 'lifestyle';
  title: string;
  description: string;
  timestamp: Date;
  hash: string;
  verified: boolean;
  encrypted: boolean;
  shared: boolean;
  size: string;
}

interface DataPermission {
  id: string;
  entity: string;
  type: 'hospital' | 'doctor' | 'researcher' | 'insurance' | 'family';
  permissions: string[];
  expiryDate: Date;
  active: boolean;
}

interface BlockchainHealthManagerProps {
  visible: boolean;
  onClose: () => void;
}

const SAMPLE_RECORDS: HealthDataRecord[] = [
  {
    id: '1',
    type: 'diagnosis',
    title: '中医四诊报告',
    description: '2024年1月健康评估报告，包含望闻问切四诊结果',
    timestamp: new Date('2024-01-15'),
    hash: '0x1a2b3c4d5e6f...',
    verified: true,
    encrypted: true,
    shared: false,
    size: '2.3 MB',
  },
  {
    id: '2',
    type: 'vital_signs',
    title: '生命体征数据',
    description: '心率、血压、体温等生命体征监测数据',
    timestamp: new Date('2024-01-20'),
    hash: '0x2b3c4d5e6f7a...',
    verified: true,
    encrypted: true,
    shared: true,
    size: '1.8 MB',
  },
  {
    id: '3',
    type: 'medication',
    title: '用药记录',
    description: '中药处方和西药用药记录',
    timestamp: new Date('2024-01-25'),
    hash: '0x3c4d5e6f7a8b...',
    verified: true,
    encrypted: true,
    shared: false,
    size: '0.5 MB',
  },
];

const SAMPLE_PERMISSIONS: DataPermission[] = [
  {
    id: '1',
    entity: '北京中医医院',
    type: 'hospital',
    permissions: ['查看诊断记录', '查看生命体征'],
    expiryDate: new Date('2024-12-31'),
    active: true,
  },
  {
    id: '2',
    entity: '李医生',
    type: 'doctor',
    permissions: ['查看所有记录', '添加诊断'],
    expiryDate: new Date('2024-06-30'),
    active: true,
  },
  {
    id: '3',
    entity: '健康研究院',
    type: 'researcher',
    permissions: ['匿名数据分析'],
    expiryDate: new Date('2024-03-31'),
    active: false,
  },
];

export const BlockchainHealthManager: React.FC<BlockchainHealthManagerProps> = ({
  visible,
  onClose,
}) => {
  const [activeTab, setActiveTab] = useState<'records' | 'permissions' | 'security'>('records');
  const [records, setRecords] = useState<HealthDataRecord[]>(SAMPLE_RECORDS);
  const [permissions, setPermissions] = useState<DataPermission[]>(SAMPLE_PERMISSIONS);
  const [selectedRecord, setSelectedRecord] = useState<HealthDataRecord | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const getTypeIcon = useMemo(() => useMemo(() => useMemo(() => useCallback( (type: string) => {, []), []), []), []);
    switch (type) {
      case 'diagnosis': return 'medical-bag';
      case 'medication': return 'pill';
      case 'test_result': return 'test-tube';
      case 'vital_signs': return 'heart-pulse';
      case 'lifestyle': return 'leaf';
      default: return 'file-document';
    }
  };

  const getTypeColor = useMemo(() => useMemo(() => useMemo(() => useCallback( (type: string) => {, []), []), []), []);
    switch (type) {
      case 'diagnosis': return '#E74C3C';
      case 'medication': return '#3498DB';
      case 'test_result': return '#F39C12';
      case 'vital_signs': return '#E91E63';
      case 'lifestyle': return '#27AE60';
      default: return colors.textSecondary;
    }
  };

  const getEntityIcon = useMemo(() => useMemo(() => useMemo(() => useCallback( (type: string) => {, []), []), []), []);
    switch (type) {
      case 'hospital': return 'hospital-building';
      case 'doctor': return 'doctor';
      case 'researcher': return 'microscope';
      case 'insurance': return 'shield-check';
      case 'family': return 'account-group';
      default: return 'account';
    }
  };

  const toggleRecordSharing = useMemo(() => useMemo(() => useMemo(() => async (recordId: string) => {
    setIsLoading(true), []), []), []);
    try {
      // 模拟区块链操作
      await new Promise<void>(resolve => setTimeout(() => resolve(), 1000));
      
      setRecords(prev => prev.map(record => 
        record.id === recordId 
          ? { ...record, shared: !record.shared }
          : record
      ));
      
      Alert.alert('成功', '数据共享状态已更新');
    } catch (error) {
      Alert.alert('错误', '更新失败，请重试');
    } finally {
      setIsLoading(false);
    }
  };

  const togglePermission = useMemo(() => useMemo(() => useMemo(() => async (permissionId: string) => {
    setIsLoading(true), []), []), []);
    try {
      await new Promise<void>(resolve => setTimeout(() => resolve(), 1000));
      
      setPermissions(prev => prev.map(permission => 
        permission.id === permissionId 
          ? { ...permission, active: !permission.active }
          : permission
      ));
      
      Alert.alert('成功', '权限状态已更新');
    } catch (error) {
      Alert.alert('错误', '更新失败，请重试');
    } finally {
      setIsLoading(false);
    }
  };

  // TODO: 将内联组件移到组件外部
const renderTabBar = useMemo(() => useMemo(() => useMemo(() => () => (
    <View style={styles.tabBar}>
      <TouchableOpacity
        style={[styles.tab, activeTab === 'records' && styles.activeTab]}
        onPress={() => setActiveTab('records')}
      >
        <Icon 
          name="database" 
          size={20} 
          color={activeTab === 'records' ? colors.primary : colors.textSecondary} 
        />
        <Text style={[styles.tabText, activeTab === 'records' && styles.activeTabText]}>
          数据记录
        </Text>
      </TouchableOpacity>
      
      <TouchableOpacity
        style={[styles.tab, activeTab === 'permissions' && styles.activeTab]}
        onPress={() => setActiveTab('permissions')}
      >
        <Icon 
          name="key" 
          size={20} 
          color={activeTab === 'permissions' ? colors.primary : colors.textSecondary} 
        />
        <Text style={[styles.tabText, activeTab === 'permissions' && styles.activeTabText]}>
          访问权限
        </Text>
      </TouchableOpacity>
      
      <TouchableOpacity
        style={[styles.tab, activeTab === 'security' && styles.activeTab]}
        onPress={() => setActiveTab('security')}
      >
        <Icon 
          name="shield-check" 
          size={20} 
          color={activeTab === 'security' ? colors.primary : colors.textSecondary} 
        />
        <Text style={[styles.tabText, activeTab === 'security' && styles.activeTabText]}>
          安全设置
        </Text>
      </TouchableOpacity>
    </View>
  ), []), []), []);

  const renderRecordCard = useMemo(() => useMemo(() => useMemo(() => (record: HealthDataRecord) => (
    <TouchableOpacity
      key={record.id}
      style={styles.recordCard}
      onPress={() => setSelectedRecord(record)}
    >
      <View style={styles.recordHeader}>
        <View style={[styles.recordIcon, { backgroundColor: getTypeColor(record.type) + '20' }]}>
          <Icon name={getTypeIcon(record.type)} size={24} color={getTypeColor(record.type)} />
        </View>
        
        <View style={styles.recordInfo}>
          <Text style={styles.recordTitle}>{record.title}</Text>
          <Text style={styles.recordDescription}>{record.description}</Text>
          <Text style={styles.recordTimestamp}>
            {record.timestamp.toLocaleDateString('zh-CN')}
          </Text>
        </View>
        
        <View style={styles.recordStatus}>
          {record.verified && (
            <View style={styles.statusBadge}>
              <Icon name="check-circle" size={16} color={colors.success} />
              <Text style={styles.statusText}>已验证</Text>
            </View>
          )}
          {record.encrypted && (
            <View style={styles.statusBadge}>
              <Icon name="lock" size={16} color={colors.primary} />
              <Text style={styles.statusText}>已加密</Text>
            </View>
          )}
        </View>
      </View>
      
      <View style={styles.recordFooter}>
        <Text style={styles.recordHash}>哈希: {record.hash}</Text>
        <View style={styles.recordActions}>
          <Text style={styles.recordSize}>{record.size}</Text>
          <Switch
            value={record.shared}
            onValueChange={() => toggleRecordSharing(record.id)}
            trackColor={{ false: colors.gray300, true: colors.primary + '50' }}
            thumbColor={record.shared ? colors.primary : colors.gray400}
          />
          <Text style={styles.shareLabel}>共享</Text>
        </View>
      </View>
    </TouchableOpacity>
  ), []), []), []);

  const renderPermissionCard = useMemo(() => useMemo(() => useMemo(() => (permission: DataPermission) => (
    <View key={permission.id} style={styles.permissionCard}>
      <View style={styles.permissionHeader}>
        <View style={styles.permissionIcon}>
          <Icon name={getEntityIcon(permission.type)} size={24} color={colors.primary} />
        </View>
        
        <View style={styles.permissionInfo}>
          <Text style={styles.permissionEntity}>{permission.entity}</Text>
          <Text style={styles.permissionType}>
            {permission.type === 'hospital' ? '医院' :
             permission.type === 'doctor' ? '医生' :
             permission.type === 'researcher' ? '研究机构' :
             permission.type === 'insurance' ? '保险公司' : '家庭成员'}
          </Text>
          <Text style={styles.permissionExpiry}>
            到期时间: {permission.expiryDate.toLocaleDateString('zh-CN')}
          </Text>
        </View>
        
        <Switch
          value={permission.active}
          onValueChange={() => togglePermission(permission.id)}
          trackColor={{ false: colors.gray300, true: colors.primary + '50' }}
          thumbColor={permission.active ? colors.primary : colors.gray400}
        />
      </View>
      
      <View style={styles.permissionsList}>
        <Text style={styles.permissionsTitle}>授权范围:</Text>
        {permission.permissions.map((perm, index) => (
          <Text key={index} style={styles.permissionItem}>• {perm}</Text>
        ))}
      </View>
    </View>
  ), []), []), []);

  // TODO: 将内联组件移到组件外部
const renderSecuritySettings = useMemo(() => useMemo(() => useMemo(() => () => (
    <View style={styles.securityContainer}>
      <View style={styles.securityCard}>
        <View style={styles.securityHeader}>
          <Icon name="fingerprint" size={32} color={colors.primary} />
          <Text style={styles.securityTitle}>生物识别认证</Text>
        </View>
        <Text style={styles.securityDescription}>
          使用指纹或面部识别来保护您的健康数据访问
        </Text>
        <Switch
          value={true}
          trackColor={{ false: colors.gray300, true: colors.primary + '50' }}
          thumbColor={colors.primary}
        />
      </View>
      
      <View style={styles.securityCard}>
        <View style={styles.securityHeader}>
          <Icon name="key-variant" size={32} color={colors.primary} />
          <Text style={styles.securityTitle}>私钥管理</Text>
        </View>
        <Text style={styles.securityDescription}>
          您的私钥安全存储在设备中，用于数据加密和身份验证
        </Text>
        <TouchableOpacity style={styles.securityButton}>
          <Text style={styles.securityButtonText}>备份私钥</Text>
        </TouchableOpacity>
      </View>
      
      <View style={styles.securityCard}>
        <View style={styles.securityHeader}>
          <Icon name="shield-lock" size={32} color={colors.primary} />
          <Text style={styles.securityTitle}>零知识证明</Text>
        </View>
        <Text style={styles.securityDescription}>
          在不泄露具体数据的情况下，证明您的健康状态符合特定条件
        </Text>
        <Switch
          value={true}
          trackColor={{ false: colors.gray300, true: colors.primary + '50' }}
          thumbColor={colors.primary}
        />
      </View>
    </View>
  ), []), []), []);

  const renderContent = useMemo(() => useMemo(() => useMemo(() => useCallback( () => {, []), []), []), []);
    switch (activeTab) {
      case 'records':
        return (
          <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>健康数据记录</Text>
              <Text style={styles.sectionDescription}>
                您的所有健康数据都经过加密存储在区块链上，确保数据的安全性和不可篡改性。
              </Text>
              {records.map(renderRecordCard)}
            </View>
          </ScrollView>
        );
      
      case 'permissions':
        return (
          <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>数据访问权限</Text>
              <Text style={styles.sectionDescription}>
                管理谁可以访问您的健康数据，您可以随时撤销或修改权限。
              </Text>
              {permissions.map(renderPermissionCard)}
            </View>
          </ScrollView>
        );
      
      case 'security':
        return (
          <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>安全设置</Text>
              <Text style={styles.sectionDescription}>
                配置您的数据安全选项，确保只有您本人可以访问和管理健康数据。
              </Text>
              {renderSecuritySettings()}
            </View>
          </ScrollView>
        );
      
      default:
        return null;
    }
  };

  return (
    <Modal
      visible={visible}
      animationType="slide"
      presentationStyle="fullScreen"
      onRequestClose={onClose}
    >
      <View style={styles.container}>
        <View style={styles.header}>
          <TouchableOpacity onPress={onClose} style={styles.closeButton}>
            <Icon name="close" size={24} color={colors.textPrimary} />
          </TouchableOpacity>
          <Text style={styles.title}>区块链健康数据</Text>
          <TouchableOpacity style={styles.helpButton}>
            <Icon name="help-circle" size={24} color={colors.textPrimary} />
          </TouchableOpacity>
        </View>

        {renderTabBar()}
        {renderContent()}

        {isLoading && (
          <View style={styles.loadingOverlay}>
            <ActivityIndicator size="large" color={colors.primary} />
            <Text style={styles.loadingText}>处理中...</Text>
          </View>
        )}
      </View>
    </Modal>
  );
};

const styles = useMemo(() => useMemo(() => useMemo(() => StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  closeButton: {
    padding: spacing.sm,
  },
  title: {
    fontSize: 18,
    fontWeight: '600',
    color: colors.textPrimary,
  },
  helpButton: {
    padding: spacing.sm,
  },
  tabBar: {
    flexDirection: 'row',
    backgroundColor: colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  tab: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.sm,
  },
  activeTab: {
    borderBottomWidth: 2,
    borderBottomColor: colors.primary,
  },
  tabText: {
    fontSize: 14,
    fontWeight: '500',
    color: colors.textSecondary,
    marginLeft: spacing.xs,
  },
  activeTabText: {
    color: colors.primary,
  },
  content: {
    flex: 1,
    paddingHorizontal: spacing.lg,
  },
  section: {
    paddingVertical: spacing.lg,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: colors.textPrimary,
    marginBottom: spacing.sm,
  },
  sectionDescription: {
    fontSize: 14,
    color: colors.textSecondary,
    lineHeight: 20,
    marginBottom: spacing.lg,
  },
  recordCard: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.md,
    marginBottom: spacing.md,
    borderWidth: 1,
    borderColor: colors.border,
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
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.md,
  },
  recordInfo: {
    flex: 1,
  },
  recordTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  recordDescription: {
    fontSize: 14,
    color: colors.textSecondary,
    lineHeight: 20,
    marginBottom: spacing.xs,
  },
  recordTimestamp: {
    fontSize: 12,
    color: colors.textTertiary,
  },
  recordStatus: {
    alignItems: 'flex-end',
  },
  statusBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.gray100,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: 8,
    marginBottom: spacing.xs,
  },
  statusText: {
    fontSize: 12,
    color: colors.textSecondary,
    marginLeft: spacing.xs,
  },
  recordFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: spacing.md,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  recordHash: {
    fontSize: 12,
    color: colors.textTertiary,
    fontFamily: 'monospace',
    flex: 1,
  },
  recordActions: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  recordSize: {
    fontSize: 12,
    color: colors.textSecondary,
    marginRight: spacing.md,
  },
  shareLabel: {
    fontSize: 12,
    color: colors.textSecondary,
    marginLeft: spacing.sm,
  },
  permissionCard: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.md,
    marginBottom: spacing.md,
    borderWidth: 1,
    borderColor: colors.border,
  },
  permissionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  permissionIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: colors.primary + '20',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.md,
  },
  permissionInfo: {
    flex: 1,
  },
  permissionEntity: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  permissionType: {
    fontSize: 14,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
  },
  permissionExpiry: {
    fontSize: 12,
    color: colors.textTertiary,
  },
  permissionsList: {
    paddingTop: spacing.md,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  permissionsTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: spacing.sm,
  },
  permissionItem: {
    fontSize: 14,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
    lineHeight: 20,
  },
  securityContainer: {
    gap: spacing.md,
  },
  securityCard: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.lg,
    borderWidth: 1,
    borderColor: colors.border,
  },
  securityHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  securityTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.textPrimary,
    marginLeft: spacing.md,
    flex: 1,
  },
  securityDescription: {
    fontSize: 14,
    color: colors.textSecondary,
    lineHeight: 20,
    marginBottom: spacing.md,
  },
  securityButton: {
    backgroundColor: colors.primary,
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    borderRadius: 8,
    alignSelf: 'flex-start',
  },
  securityButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: 'white',
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
  loadingText: {
    fontSize: 16,
    color: 'white',
    marginTop: spacing.md,
  },
}), []), []), []); 