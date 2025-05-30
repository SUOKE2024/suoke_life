import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from '../../../components/common/Icon';
import { colors, spacing } from '../../../constants/theme';

import React, { useState } from 'react';
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  Modal,
  ActivityIndicator,
  Switch,
} from 'react-native';

interface HealthDataRecord {
  id: string;
  type: 'diagnosis' | 'vitals' | 'medication' | 'exercise' | 'diet';
  title: string;
  data: any;
  timestamp: string;
  hash: string;
  encrypted: boolean;
  shared: boolean;
  permissions: string[];
}

interface DataSharingRequest {
  id: string;
  requester: string;
  dataTypes: string[];
  purpose: string;
  duration: string;
  status: 'pending' | 'approved' | 'denied';
}

interface BlockchainHealthDataProps {
  visible: boolean;
  onClose: () => void;
}

export const BlockchainHealthData: React.FC<BlockchainHealthDataProps> = ({
  visible,
  onClose,
}) => {
  const [activeTab, setActiveTab] = useState<'records' | 'sharing' | 'privacy' | 'backup'>('records');
  const [loading, setLoading] = useState(false);
  const [encryptionEnabled, setEncryptionEnabled] = useState(true);
  const [autoBackup, setAutoBackup] = useState(true);
  const [dataRetention] = useState('5年');

  // 模拟健康数据记录
  const [healthRecords] = useState<HealthDataRecord[]>([
    {
      id: 'record_1',
      type: 'diagnosis',
      title: '五诊检查结果',
      data: { constitution: '平和质', symptoms: ['轻微疲劳'] },
      timestamp: '2024-01-15T10:30:00Z',
      hash: '0x1a2b3c4d5e6f...',
      encrypted: true,
      shared: false,
      permissions: [],
    },
    {
      id: 'record_2',
      type: 'vitals',
      title: '生命体征监测',
      data: { heartRate: 72, bloodPressure: '120/80', temperature: 36.5 },
      timestamp: '2024-01-15T08:00:00Z',
      hash: '0x2b3c4d5e6f7a...',
      encrypted: true,
      shared: true,
      permissions: ['doctor_zhang', 'clinic_abc'],
    },
    {
      id: 'record_3',
      type: 'medication',
      title: '用药记录',
      data: { medication: '维生素D', dosage: '1000IU', frequency: '每日一次' },
      timestamp: '2024-01-14T20:00:00Z',
      hash: '0x3c4d5e6f7a8b...',
      encrypted: true,
      shared: false,
      permissions: [],
    },
  ]);

  // 模拟数据共享请求
  const [sharingRequests] = useState<DataSharingRequest[]>([
    {
      id: 'req_1',
      requester: '张医生 - 中医科',
      dataTypes: ['五诊结果', '生命体征'],
      purpose: '制定个性化治疗方案',
      duration: '3个月',
      status: 'pending',
    },
    {
      id: 'req_2',
      requester: '健康研究院',
      dataTypes: ['运动数据', '饮食记录'],
      purpose: '健康生活方式研究',
      duration: '1年',
      status: 'pending',
    },
  ]);

  const encryptData = useMemo(() => useMemo(() => async () => {
    // 模拟数据加密
    setLoading(true), []), []);
    await new Promise<void>(resolve => setTimeout(() => resolve(), 800));
    setLoading(false);
    Alert.alert('加密完成', '数据已使用AES-256加密算法保护');
  };

  const shareData = useMemo(() => useMemo(() => async () => {
    setLoading(true), []), []);
    await new Promise<void>(resolve => setTimeout(() => resolve(), 1000));
    setLoading(false);
    Alert.alert('共享成功', '数据已安全共享给授权方');
  };

  const backupToBlockchain = useMemo(() => useMemo(() => async () => {
    setLoading(true), []), []);
    await new Promise<void>(resolve => setTimeout(() => resolve(), 2000));
    setLoading(false);
    Alert.alert('备份完成', '健康数据已备份到区块链网络');
  };

  // TODO: 将内联组件移到组件外部
const renderDataRecords = useMemo(() => useMemo(() => () => (
    <ScrollView style={styles.tabContent}>
      <View style={styles.sectionHeader}>
        <Text style={styles.sectionTitle}>健康数据记录</Text>
        <TouchableOpacity onPress={backupToBlockchain} disabled={loading}>
          <Icon name="cloud-upload" size={24} color={colors.primary} />
        </TouchableOpacity>
      </View>

      {healthRecords.map((record) => (
        <View key={record.id} style={styles.recordCard}>
          <View style={styles.recordHeader}>
            <View style={styles.recordInfo}>
              <Icon 
                name={getRecordIcon(record.type)} 
                size={24} 
                color={getRecordColor(record.type)} 
              />
              <View style={styles.recordDetails}>
                <Text style={styles.recordTitle}>{record.title}</Text>
                <Text style={styles.recordTime}>
                  {new Date(record.timestamp).toLocaleString()}
                </Text>
              </View>
            </View>
            <View style={styles.recordStatus}>
              {record.encrypted && (
                <Icon name="lock" size={16} color={colors.success} />
              )}
              {record.shared && (
                <Icon name="share" size={16} color={colors.primary} />
              )}
            </View>
          </View>

          <View style={styles.recordData}>
            <Text style={styles.dataLabel}>数据哈希:</Text>
            <Text style={styles.dataHash}>{record.hash}</Text>
          </View>

          <View style={styles.recordActions}>
            <TouchableOpacity 
              style={styles.actionButton}
              onPress={() => encryptData()}
            >
              <Icon name="shield-check" size={16} color={colors.primary} />
              <Text style={styles.actionText}>重新加密</Text>
            </TouchableOpacity>
            <TouchableOpacity 
              style={styles.actionButton}
              onPress={() => shareData()}
            >
              <Icon name="share-variant" size={16} color={colors.primary} />
              <Text style={styles.actionText}>安全共享</Text>
            </TouchableOpacity>
          </View>
        </View>
      ))}
    </ScrollView>
  ), []), []);

  // TODO: 将内联组件移到组件外部
const renderDataSharing = useMemo(() => useMemo(() => () => (
    <ScrollView style={styles.tabContent}>
      <Text style={styles.sectionTitle}>数据共享请求</Text>
      
      {sharingRequests.map((request) => (
        <View key={request.id} style={styles.requestCard}>
          <View style={styles.requestHeader}>
            <Text style={styles.requesterName}>{request.requester}</Text>
            <View style={[styles.statusBadge, { 
              backgroundColor: request.status === 'pending' ? colors.warning : colors.success, 
            }]}>
              <Text style={styles.statusBadgeText}>
                {request.status === 'pending' ? '待审批' : '已批准'}
              </Text>
            </View>
          </View>

          <View style={styles.requestDetails}>
            <Text style={styles.detailLabel}>请求数据类型:</Text>
            <Text style={styles.detailValue}>{request.dataTypes.join(', ')}</Text>
            
            <Text style={styles.detailLabel}>使用目的:</Text>
            <Text style={styles.detailValue}>{request.purpose}</Text>
            
            <Text style={styles.detailLabel}>使用期限:</Text>
            <Text style={styles.detailValue}>{request.duration}</Text>
          </View>

          {request.status === 'pending' && (
            <View style={styles.requestActions}>
              <TouchableOpacity style={[styles.actionButton, styles.approveButton]}>
                <Text style={styles.approveText}>批准</Text>
              </TouchableOpacity>
              <TouchableOpacity style={[styles.actionButton, styles.denyButton]}>
                <Text style={styles.denyText}>拒绝</Text>
              </TouchableOpacity>
            </View>
          )}
        </View>
      ))}
    </ScrollView>
  ), []), []);

  // TODO: 将内联组件移到组件外部
const renderPrivacySettings = useMemo(() => useMemo(() => () => (
    <ScrollView style={styles.tabContent}>
      <Text style={styles.sectionTitle}>隐私设置</Text>

      <View style={styles.settingCard}>
        <View style={styles.settingItem}>
          <View style={styles.settingInfo}>
            <Text style={styles.settingTitle}>数据加密</Text>
            <Text style={styles.settingDesc}>使用端到端加密保护您的健康数据</Text>
          </View>
          <Switch
            value={encryptionEnabled}
            onValueChange={setEncryptionEnabled}
            trackColor={{ false: colors.border, true: colors.primary }}
          />
        </View>

        <View style={styles.settingItem}>
          <View style={styles.settingInfo}>
            <Text style={styles.settingTitle}>自动备份</Text>
            <Text style={styles.settingDesc}>定期将数据备份到区块链网络</Text>
          </View>
          <Switch
            value={autoBackup}
            onValueChange={setAutoBackup}
            trackColor={{ false: colors.border, true: colors.primary }}
          />
        </View>

        <View style={styles.settingItem}>
          <View style={styles.settingInfo}>
            <Text style={styles.settingTitle}>数据保留期</Text>
            <Text style={styles.settingDesc}>设置数据在区块链上的保留时间</Text>
          </View>
          <TouchableOpacity style={styles.valueSelector}>
            <Text style={styles.valueText}>{dataRetention}</Text>
            <Icon name="chevron-down" size={16} color={colors.textSecondary} />
          </TouchableOpacity>
        </View>
      </View>

      <View style={styles.privacyInfo}>
        <Icon name="information" size={20} color={colors.primary} />
        <Text style={styles.privacyText}>
          隐私保护：您的健康数据通过区块链技术进行分布式存储，确保数据的安全性、完整性和不可篡改性。
          只有您授权的医疗机构和研究机构才能访问相关数据。
        </Text>
      </View>
    </ScrollView>
  ), []), []);

  // TODO: 将内联组件移到组件外部
const renderBackupRestore = useMemo(() => useMemo(() => () => (
    <ScrollView style={styles.tabContent}>
      <Text style={styles.sectionTitle}>数据备份与恢复</Text>

      <View style={styles.backupCard}>
        <View style={styles.backupInfo}>
          <Icon name="cloud-check" size={32} color={colors.success} />
          <Text style={styles.backupTitle}>最近备份</Text>
          <Text style={styles.backupTime}>2024年1月15日 14:30</Text>
          <Text style={styles.backupSize}>数据大小: 2.3 MB</Text>
        </View>

        <TouchableOpacity 
          style={styles.backupButton}
          onPress={backupToBlockchain}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color="white" />
          ) : (
            <>
              <Icon name="backup-restore" size={20} color="white" />
              <Text style={styles.backupButtonText}>立即备份</Text>
            </>
          )}
        </TouchableOpacity>
      </View>

      <View style={styles.restoreSection}>
        <Text style={styles.restoreTitle}>从备份恢复</Text>
        <Text style={styles.restoreDesc}>
          如果您更换设备或重新安装应用，可以从区块链备份中恢复您的健康数据
        </Text>
        <TouchableOpacity style={styles.restoreButton}>
          <Icon name="download" size={20} color={colors.primary} />
          <Text style={styles.restoreButtonText}>恢复数据</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  ), []), []);

  const getRecordIcon = useMemo(() => useMemo(() => useCallback( (type: string) => {, []), []), []);
    switch (type) {
      case 'diagnosis': return 'stethoscope';
      case 'vitals': return 'heart-pulse';
      case 'medication': return 'pill';
      case 'exercise': return 'run';
      case 'diet': return 'food';
      default: return 'file-document';
    }
  };

  const getRecordColor = useMemo(() => useMemo(() => useCallback( (type: string) => {, []), []), []);
    switch (type) {
      case 'diagnosis': return colors.primary;
      case 'vitals': return colors.error;
      case 'medication': return colors.success;
      case 'exercise': return colors.warning;
      case 'diet': return '#8E44AD';
      default: return colors.textSecondary;
    }
  };

  // TODO: 将内联组件移到组件外部
const renderTabBar = useMemo(() => useMemo(() => () => (
    <View style={styles.tabBar}>
      {[
        { key: 'records', label: '数据记录', icon: 'database' },
        { key: 'sharing', label: '数据共享', icon: 'share-variant' },
        { key: 'privacy', label: '隐私设置', icon: 'shield-check' },
        { key: 'backup', label: '备份恢复', icon: 'backup-restore' },
      ].map((tab) => (
        <TouchableOpacity
          key={tab.key}
          style={[styles.tabButton, activeTab === tab.key && styles.activeTabButton]}
          onPress={() => setActiveTab(tab.key as any)}
        >
          <Icon 
            name={tab.icon} 
            size={20} 
            color={activeTab === tab.key ? colors.primary : colors.textSecondary} 
          />
          <Text style={[
            styles.tabText,
            activeTab === tab.key && styles.activeTabText,
          ]}>
            {tab.label}
          </Text>
        </TouchableOpacity>
      ))}
    </View>
  ), []), []);

  const renderContent = useMemo(() => useMemo(() => useCallback( () => {, []), []), []);
    switch (activeTab) {
      case 'records': return renderDataRecords();
      case 'sharing': return renderDataSharing();
      case 'privacy': return renderPrivacySettings();
      case 'backup': return renderBackupRestore();
      default: return renderDataRecords();
    }
  };

  return (
    <Modal visible={visible} animationType="slide" presentationStyle="pageSheet">
      <SafeAreaView style={styles.container}>
        {/* 头部 */}
        <View style={styles.header}>
          <TouchableOpacity onPress={onClose} style={styles.closeButton}>
            <Icon name="close" size={24} color={colors.text} />
          </TouchableOpacity>
          <View style={styles.headerContent}>
            <Text style={styles.title}>区块链健康数据</Text>
            <Text style={styles.subtitle}>安全、透明、不可篡改</Text>
          </View>
          <View style={styles.blockchainStatus}>
            <View style={styles.statusDot} />
            <Text style={styles.statusText}>已连接</Text>
          </View>
        </View>

        {/* 标签栏 */}
        {renderTabBar()}

        {/* 内容区域 */}
        {renderContent()}
      </SafeAreaView>
    </Modal>
  );
};

const styles = useMemo(() => useMemo(() => StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  closeButton: {
    padding: spacing.sm,
  },
  headerContent: {
    flex: 1,
    marginLeft: spacing.md,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: colors.text,
  },
  subtitle: {
    fontSize: 14,
    color: colors.textSecondary,
    marginTop: 2,
  },
  blockchainStatus: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: colors.success,
    marginRight: spacing.xs,
  },
  statusText: {
    fontSize: 12,
    color: colors.success,
    fontWeight: '600',
  },
  tabBar: {
    flexDirection: 'row',
    backgroundColor: colors.surface,
    paddingHorizontal: spacing.sm,
  },
  tabButton: {
    flex: 1,
    alignItems: 'center',
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.sm,
  },
  activeTabButton: {
    borderBottomWidth: 2,
    borderBottomColor: colors.primary,
  },
  tabText: {
    fontSize: 12,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  activeTabText: {
    color: colors.primary,
    fontWeight: '600',
  },
  tabContent: {
    flex: 1,
    padding: spacing.lg,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.lg,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: colors.text,
  },
  recordCard: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.md,
    marginBottom: spacing.md,
    borderLeftWidth: 4,
    borderLeftColor: colors.primary,
  },
  recordHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  recordInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  recordDetails: {
    marginLeft: spacing.md,
    flex: 1,
  },
  recordTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.text,
  },
  recordTime: {
    fontSize: 12,
    color: colors.textSecondary,
    marginTop: 2,
  },
  recordStatus: {
    flexDirection: 'row',
  },
  recordData: {
    marginBottom: spacing.sm,
  },
  dataLabel: {
    fontSize: 12,
    color: colors.textSecondary,
    marginBottom: 2,
  },
  dataHash: {
    fontSize: 12,
    fontFamily: 'monospace',
    color: colors.text,
    backgroundColor: colors.background,
    padding: spacing.xs,
    borderRadius: 4,
  },
  recordActions: {
    flexDirection: 'row',
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: colors.primary,
  },
  actionText: {
    fontSize: 12,
    color: colors.primary,
    marginLeft: spacing.xs,
  },
  requestCard: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.md,
    marginBottom: spacing.md,
  },
  requestHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  requesterName: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.text,
  },
  statusBadge: {
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: 12,
  },
  statusBadgeText: {
    fontSize: 12,
    color: 'white',
    fontWeight: '600',
  },
  requestDetails: {
    marginBottom: spacing.md,
  },
  detailLabel: {
    fontSize: 12,
    color: colors.textSecondary,
    marginBottom: 2,
    marginTop: spacing.sm,
  },
  detailValue: {
    fontSize: 14,
    color: colors.text,
  },
  requestActions: {
    flexDirection: 'row',
  },
  approveButton: {
    backgroundColor: colors.success,
    borderColor: colors.success,
  },
  denyButton: {
    backgroundColor: colors.error,
    borderColor: colors.error,
  },
  approveText: {
    color: 'white',
    fontSize: 14,
    fontWeight: '600',
  },
  denyText: {
    color: 'white',
    fontSize: 14,
    fontWeight: '600',
  },
  settingCard: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.md,
    marginBottom: spacing.lg,
  },
  settingItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  settingInfo: {
    flex: 1,
    marginRight: spacing.md,
  },
  settingTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.text,
    marginBottom: 2,
  },
  settingDesc: {
    fontSize: 12,
    color: colors.textSecondary,
  },
  valueSelector: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    backgroundColor: colors.background,
    borderRadius: 8,
  },
  valueText: {
    fontSize: 14,
    color: colors.text,
    marginRight: spacing.sm,
  },
  privacyInfo: {
    flexDirection: 'row',
    backgroundColor: colors.primary + '10',
    padding: spacing.md,
    borderRadius: 12,
    alignItems: 'flex-start',
  },
  privacyText: {
    flex: 1,
    fontSize: 14,
    color: colors.text,
    marginLeft: spacing.md,
    lineHeight: 20,
  },
  backupCard: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.lg,
    alignItems: 'center',
    marginBottom: spacing.lg,
  },
  backupInfo: {
    alignItems: 'center',
    marginBottom: spacing.lg,
  },
  backupTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: colors.text,
    marginTop: spacing.md,
  },
  backupTime: {
    fontSize: 14,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  backupSize: {
    fontSize: 12,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  backupButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.primary,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderRadius: 8,
  },
  backupButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
    marginLeft: spacing.sm,
  },
  restoreSection: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.lg,
  },
  restoreTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.text,
    marginBottom: spacing.sm,
  },
  restoreDesc: {
    fontSize: 14,
    color: colors.textSecondary,
    lineHeight: 20,
    marginBottom: spacing.lg,
  },
  restoreButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: colors.primary,
    paddingVertical: spacing.md,
    borderRadius: 8,
  },
  restoreButtonText: {
    color: colors.primary,
    fontSize: 16,
    fontWeight: '600',
    marginLeft: spacing.sm,
  },
}), []), []);

export default BlockchainHealthData; 