/**
 * 健康数据隐私管理组件
 * 提供用户友好的隐私控制界面，集成零知识证明和区块链验证
 */
import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  Switch,
  Modal,
  ActivityIndicator,
  Dimensions,
  Animated,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons, MaterialIcons } from '@expo/vector-icons';
import { useTranslation } from 'react-i18next';
const { width, height } = Dimensions.get('window');
interface HealthDataRecord {
  record_id: string;
  user_id: string;
  data_type: string;
  data_hash: string;
  blockchain_tx_hash: string;
  ipfs_hash?: string;
  zkp_proof_id?: string;
  metadata: {
    privacy_level: string;
    data_size: number;
    encryption_algorithm: string;
    storage_locations: string[];
  };
  created_at: string;
  updated_at: string;
  access_permissions: string[];
  is_verified: boolean;
}
interface PrivacySettings {
  data_sharing_enabled: boolean;
  anonymization_level: 'none' | 'basic' | 'advanced';
  zkp_verification_required: boolean;
  blockchain_storage_enabled: boolean;
  ipfs_storage_enabled: boolean;
  auto_approve_research: boolean;
  retention_period_days: number;
}
interface ZKPProofInfo {
  proof_id: string;
  statement: string;
  created_at: string;
  expires_at: string;
  is_valid: boolean;
  verification_key: string;
  public_inputs_count: number;
}
const HealthDataPrivacyManager: React.FC = () => {
  const { t } = useTranslation();
  const [healthRecords, setHealthRecords] = useState<HealthDataRecord[]>([]);
  const [privacySettings, setPrivacySettings] = useState<PrivacySettings>({
    data_sharing_enabled: false,
    anonymization_level: 'basic',
    zkp_verification_required: true,
    blockchain_storage_enabled: true,
    ipfs_storage_enabled: true,
    auto_approve_research: false,
    retention_period_days: 365,
  });
  const [zkpProofs, setZkpProofs] = useState<ZKPProofInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedRecord, setSelectedRecord] = useState<HealthDataRecord | null>(null);
  const [showProofModal, setShowProofModal] = useState(false);
  const [showSettingsModal, setShowSettingsModal] = useState(false);
  const [animatedValue] = useState(new Animated.Value(0));
  useEffect(() => {
    loadHealthRecords();
    loadPrivacySettings();
    loadZKPProofs();
    // 启动动画
    Animated.timing(animatedValue, {
      toValue: 1,
      duration: 1000,
      useNativeDriver: true,
    }).start();
  }, []);
  const loadHealthRecords = async () => {
    try {
      setLoading(true);
      // 模拟API调用
      const mockRecords: HealthDataRecord[] = [
        {
          record_id: 'hdr_tongue_001',
          user_id: 'user_123',
          data_type: 'tongue_analysis',
          data_hash: 'sha256_hash_001',
          blockchain_tx_hash: '0xabc123...',
          ipfs_hash: 'QmXyz789...',
          zkp_proof_id: 'zkp_proof_001',
          metadata: {
            privacy_level: 'high',
            data_size: 2048,
            encryption_algorithm: 'AES-256-GCM',
            storage_locations: ['blockchain', 'ipfs'],
          },
          created_at: '2024-12-19T10:30:00Z',
          updated_at: '2024-12-19T10:30:00Z',
          access_permissions: ['user_123'],
          is_verified: true,
        },
        {
          record_id: 'hdr_metrics_002',
          user_id: 'user_123',
          data_type: 'health_metrics',
          data_hash: 'sha256_hash_002',
          blockchain_tx_hash: '0xdef456...',
          ipfs_hash: 'QmAbc123...',
          zkp_proof_id: 'zkp_proof_002',
          metadata: {
            privacy_level: 'high',
            data_size: 1024,
            encryption_algorithm: 'AES-256-GCM',
            storage_locations: ['blockchain', 'ipfs'],
          },
          created_at: '2024-12-19T11:00:00Z',
          updated_at: '2024-12-19T11:00:00Z',
          access_permissions: ['user_123'],
          is_verified: true,
        },
      ];
      setHealthRecords(mockRecords);
    } catch (error) {
      console.error('加载健康记录失败:', error);
      Alert.alert('错误', '加载健康记录失败');
    } finally {
      setLoading(false);
    }
  };
  const loadPrivacySettings = async () => {
    try {
      // 模拟从API加载隐私设置
      // 实际实现中会从后端获取用户的隐私设置
    } catch (error) {
      console.error('加载隐私设置失败:', error);
    }
  };
  const loadZKPProofs = async () => {
    try {
      // 模拟加载零知识证明信息
      const mockProofs: ZKPProofInfo[] = [
        {
          proof_id: 'zkp_proof_001',
          statement: '用户的舌象分析数据属于有效集合',
          created_at: '2024-12-19T10:30:00Z',
          expires_at: '2024-12-20T10:30:00Z',
          is_valid: true,
          verification_key: 'zkp_membership_abc123',
          public_inputs_count: 3,
        },
        {
          proof_id: 'zkp_proof_002',
          statement: '用户的健康指标数据在正常范围内',
          created_at: '2024-12-19T11:00:00Z',
          expires_at: '2024-12-20T11:00:00Z',
          is_valid: true,
          verification_key: 'zkp_range_def456',
          public_inputs_count: 4,
        },
      ];
      setZkpProofs(mockProofs);
    } catch (error) {
      console.error('加载ZKP证明失败:', error);
    }
  };
  const updatePrivacySetting = useCallback(async (key: keyof PrivacySettings, value: any) => {
    try {
      const newSettings = { ...privacySettings, [key]: value };
      setPrivacySettings(newSettings);
      // 模拟API调用保存设置
      console.log('更新隐私设置:', key, value);
      // 显示成功提示
      Alert.alert('成功', '隐私设置已更新');
    } catch (error) {
      console.error('更新隐私设置失败:', error);
      Alert.alert('错误', '更新隐私设置失败');
    }
  }, [privacySettings]);
  const verifyZKPProof = async (proofId: string) => {
    try {
      setLoading(true);
      // 模拟验证零知识证明
      await new Promise(resolve => setTimeout(resolve, 2000));
      // 更新证明状态
      setZkpProofs(prev => prev.map(proof =>))
        proof.proof_id === proofId
          ? { ...proof, is_valid: true }
          : proof
      ));
      Alert.alert('验证成功', '零知识证明验证通过');
    } catch (error) {
      console.error('验证ZKP证明失败:', error);
      Alert.alert('验证失败', '零知识证明验证失败');
    } finally {
      setLoading(false);
    }
  };
  const revokeDataAccess = async (recordId: string) => {
    try {
      Alert.alert('确认撤销',
        '确定要撤销对此数据的所有访问权限吗？',
        [
          { text: '取消', style: 'cancel' },
          {
            text: '确认',
            style: 'destructive',
            onPress: async () => {
              // 模拟撤销访问权限
              setHealthRecords(prev => prev.map(record =>))
                record.record_id === recordId
                  ? { ...record, access_permissions: [record.user_id] }
                  : record
              ));
              Alert.alert('成功', '访问权限已撤销');
            },
          },
        ]
      );
    } catch (error) {
      console.error('撤销访问权限失败:', error);
      Alert.alert('错误', '撤销访问权限失败');
    }
  };
  const getDataTypeIcon = (dataType: string) => {
    switch (dataType) {
      case 'tongue_analysis':
        return 'medical-outline';
      case 'health_metrics':
        return 'fitness-outline';
      case 'diagnosis':
        return 'document-text-outline';
      default:
        return 'folder-outline';
    }
  };
  const getDataTypeName = (dataType: string) => {
    switch (dataType) {
      case 'tongue_analysis':
        return '舌象分析';
      case 'health_metrics':
        return '健康指标';
      case 'diagnosis':
        return '诊断记录';
      default:
        return '其他数据';
    }
  };
  const getPrivacyLevelColor = (level: string) => {
    switch (level) {
      case 'high':
        return '#4CAF50';
      case 'medium':
        return '#FF9800';
      case 'low':
        return '#F44336';
      default:
        return '#9E9E9E';
    }
  };
  const renderHealthRecord = (record: HealthDataRecord) => ()
    <Animated.View
      key={record.record_id}
      style={{[
        styles.recordCard,
        {
          opacity: animatedValue,
          transform: [{
            translateY: animatedValue.interpolate({
              inputRange: [0, 1],
              outputRange: [50, 0],
            }}),
          }],
        },
      ]}
    >
      <View style={styles.recordHeader}>
        <View style={styles.recordInfo}>
          <Ionicons
            name={getDataTypeIcon(record.data_type) as any}
            size={24}
            color="#2196F3"
          />
          <View style={styles.recordText}>
            <Text style={styles.recordTitle}>
              {getDataTypeName(record.data_type)}
            </Text>
            <Text style={styles.recordDate}>
              {new Date(record.created_at).toLocaleDateString('zh-CN')}
            </Text>
          </View>
        </View>
        <View style={styles.recordStatus}>
          <View style={{[
            styles.privacyBadge,
            { backgroundColor: getPrivacyLevelColor(record.metadata.privacy_level) }}
          ]}>
            <Text style={styles.privacyText}>
              {record.metadata.privacy_level === 'high' ? '高隐私' : '标准'}
            </Text>
          </View>
          {record.is_verified  && <Ionicons name="shield-checkmark" size={20} color="#4CAF50" />
          )}
        </View>
      </View>
      <View style={styles.recordDetails}>
        <View style={styles.detailRow}>
          <Text style={styles.detailLabel}>存储位置:</Text>
          <View style={styles.storageIcons}>
            {record.metadata.storage_locations.includes('blockchain')  && <MaterialIcons name="link" size={16} color="#FF9800" />
            )}
            {record.metadata.storage_locations.includes('ipfs')  && <MaterialIcons name="cloud" size={16} color="#2196F3" />
            )}
          </View>
        </View>
        {record.zkp_proof_id  && <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>零知识证明:</Text>
            <TouchableOpacity
              style={styles.proofButton}
              onPress={() => {
                setSelectedRecord(record);
                setShowProofModal(true);
              }}
            >
              <Text style={styles.proofButtonText}>查看证明</Text>
            </TouchableOpacity>
          </View>
        )}
      </View>
      <View style={styles.recordActions}>
        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => revokeDataAccess(record.record_id)}
        >
          <Ionicons name="lock-closed" size={16} color="#F44336" />
          <Text style={styles.actionButtonText}>撤销访问</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.actionButton, styles.primaryAction]}
          onPress={() => {
            setSelectedRecord(record);
            // 显示详细信息
          }}
        >
          <Ionicons name="information-circle" size={16} color="#2196F3" />
          <Text style={[styles.actionButtonText, styles.primaryActionText]}>详情</Text>
        </TouchableOpacity>
      </View>
    </Animated.View>
  );
  const renderPrivacySettings = () => (
  <View style={styles.settingsContainer}>
      <Text style={styles.sectionTitle}>隐私设置</Text>
      <View style={styles.settingItem}>
        <View style={styles.settingInfo}>
          <Text style={styles.settingLabel}>数据分享</Text>
          <Text style={styles.settingDescription}>允许与研究机构分享匿名数据</Text>
        </View>
        <Switch
          value={privacySettings.data_sharing_enabled}
          onValueChange={(value) => updatePrivacySetting('data_sharing_enabled', value)}
          trackColor={{ false: '#E0E0E0', true: '#4CAF50' }}
          thumbColor={privacySettings.data_sharing_enabled ? '#FFFFFF' : '#FFFFFF'}
        />
      </View>
      <View style={styles.settingItem}>
        <View style={styles.settingInfo}>
          <Text style={styles.settingLabel}>零知识证明验证</Text>
          <Text style={styles.settingDescription}>要求零知识证明验证数据访问</Text>
        </View>
        <Switch
          value={privacySettings.zkp_verification_required}
          onValueChange={(value) => updatePrivacySetting('zkp_verification_required', value)}
          trackColor={{ false: '#E0E0E0', true: '#4CAF50' }}
          thumbColor={privacySettings.zkp_verification_required ? '#FFFFFF' : '#FFFFFF'}
        />
      </View>
      <View style={styles.settingItem}>
        <View style={styles.settingInfo}>
          <Text style={styles.settingLabel}>区块链存储</Text>
          <Text style={styles.settingDescription}>将数据哈希存储到区块链</Text>
        </View>
        <Switch
          value={privacySettings.blockchain_storage_enabled}
          onValueChange={(value) => updatePrivacySetting('blockchain_storage_enabled', value)}
          trackColor={{ false: '#E0E0E0', true: '#4CAF50' }}
          thumbColor={privacySettings.blockchain_storage_enabled ? '#FFFFFF' : '#FFFFFF'}
        />
      </View>
      <View style={styles.settingItem}>
        <View style={styles.settingInfo}>
          <Text style={styles.settingLabel}>IPFS分布式存储</Text>
          <Text style={styles.settingDescription}>使用IPFS存储加密数据</Text>
        </View>
        <Switch
          value={privacySettings.ipfs_storage_enabled}
          onValueChange={(value) => updatePrivacySetting('ipfs_storage_enabled', value)}
          trackColor={{ false: '#E0E0E0', true: '#4CAF50' }}
          thumbColor={privacySettings.ipfs_storage_enabled ? '#FFFFFF' : '#FFFFFF'}
        />
      </View>
    </View>
  );
  const renderZKPProofModal = () => (
  <Modal
      visible={showProofModal}
      animationType="slide"
      transparent={true}
      onRequestClose={() => setShowProofModal(false)}
    >
      <View style={styles.modalOverlay}>
        <View style={styles.modalContent}>
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>零知识证明详情</Text>
            <TouchableOpacity
              style={styles.closeButton}
              onPress={() => setShowProofModal(false)}
            >
              <Ionicons name="close" size={24} color="#666" />
            </TouchableOpacity>
          </View>
          {selectedRecord  && <ScrollView style={styles.modalBody}>
              {zkpProofs
                .filter(proof => proof.proof_id === selectedRecord.zkp_proof_id)
                .map(proof => ())
                  <View key={proof.proof_id} style={styles.proofDetails}>
                    <View style={styles.proofHeader}>
                      <Ionicons name="shield-checkmark" size={32} color="#4CAF50" />
                      <View style={styles.proofStatus}>
                        <Text style={styles.proofTitle}>证明有效</Text>
                        <Text style={styles.proofId}>ID: {proof.proof_id}</Text>
                      </View>
                    </View>
                    <Text style={styles.proofStatement}>{proof.statement}</Text>
                    <View style={styles.proofMetadata}>
                      <View style={styles.metadataRow}>
                        <Text style={styles.metadataLabel}>创建时间:</Text>
                        <Text style={styles.metadataValue}>
                          {new Date(proof.created_at).toLocaleString('zh-CN')}
                        </Text>
                      </View>
                      <View style={styles.metadataRow}>
                        <Text style={styles.metadataLabel}>过期时间:</Text>
                        <Text style={styles.metadataValue}>
                          {new Date(proof.expires_at).toLocaleString('zh-CN')}
                        </Text>
                      </View>
                      <View style={styles.metadataRow}>
                        <Text style={styles.metadataLabel}>公开输入数量:</Text>
                        <Text style={styles.metadataValue}>{proof.public_inputs_count}</Text>
                      </View>
                    </View>
                    <TouchableOpacity
                      style={styles.verifyButton}
                      onPress={() => verifyZKPProof(proof.proof_id)}
                      disabled={loading}
                    >
                      {loading ? ()
                        <ActivityIndicator color="#FFFFFF" />
                      ) : (
                        <>
                          <Ionicons name="checkmark-circle" size={20} color="#FFFFFF" />
                          <Text style={styles.verifyButtonText}>重新验证</Text>
                        </>
                      )}
                    </TouchableOpacity>
                  </View>
                ))}
            </ScrollView>
          )}
        </View>
      </View>
    </Modal>
  );
  return (
  <View style={styles.container}>
      <LinearGradient
        colors={['#667eea', '#764ba2']}
        style={styles.header}
      >
        <Text style={styles.headerTitle}>健康数据隐私管理</Text>
        <Text style={styles.headerSubtitle}>
          零知识证明 • 区块链存储 • 隐私保护
        </Text>
        <TouchableOpacity
          style={styles.settingsButton}
          onPress={() => setShowSettingsModal(true)}
        >
          <Ionicons name="settings" size={24} color="#FFFFFF" />
        </TouchableOpacity>
      </LinearGradient>
      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {loading ? ()
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color="#2196F3" />
            <Text style={styles.loadingText}>加载中...</Text>
          </View>
        ) : (
          <>
            <View style={styles.statsContainer}>
              <View style={styles.statCard}>
                <Text style={styles.statNumber}>{healthRecords.length}</Text>
                <Text style={styles.statLabel}>健康记录</Text>
              </View>
              <View style={styles.statCard}>
                <Text style={styles.statNumber}>
                  {healthRecords.filter(r => r.zkp_proof_id).length}
                </Text>
                <Text style={styles.statLabel}>ZKP保护</Text>
              </View>
              <View style={styles.statCard}>
                <Text style={styles.statNumber}>
                  {Math.round()
                    (healthRecords.filter(r => r.zkp_proof_id).length /)
                     Math.max(healthRecords.length, 1)) * 100
                  )}%
                </Text>
                <Text style={styles.statLabel}>隐私保护率</Text>
              </View>
            </View>
            <Text style={styles.sectionTitle}>我的健康数据</Text>
            {healthRecords.map(renderHealthRecord)}
            {renderPrivacySettings()}
          </>
        )}
      </ScrollView>
      {renderZKPProofModal()}
      <Modal
        visible={showSettingsModal}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setShowSettingsModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>隐私设置</Text>
              <TouchableOpacity
                style={styles.closeButton}
                onPress={() => setShowSettingsModal(false)}
              >
                <Ionicons name="close" size={24} color="#666" />
              </TouchableOpacity>
            </View>
            <ScrollView style={styles.modalBody}>
              {renderPrivacySettings()}
            </ScrollView>
          </View>
        </View>
      </Modal>
    </View>
  );
};
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  header: {
    paddingTop: 50,
    paddingBottom: 30,
    paddingHorizontal: 20,
    position: 'relative',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginBottom: 5,
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#FFFFFF',
    opacity: 0.9,
  },
  settingsButton: {
    position: 'absolute',
    top: 50,
    right: 20,
    padding: 8,
  },
  content: {
    flex: 1,
    paddingHorizontal: 20,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 50,
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#666',
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginVertical: 20,
  },
  statCard: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 20,
    alignItems: 'center',
    marginHorizontal: 5,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#2196F3',
    marginBottom: 5,
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginVertical: 15,
  },
  recordCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  recordHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  recordInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  recordText: {
    marginLeft: 12,
    flex: 1,
  },
  recordTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  recordDate: {
    fontSize: 12,
    color: '#666',
    marginTop: 2,
  },
  recordStatus: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  privacyBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    marginRight: 8,
  },
  privacyText: {
    fontSize: 10,
    color: '#FFFFFF',
    fontWeight: '600',
  },
  recordDetails: {
    marginBottom: 12,
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 6,
  },
  detailLabel: {
    fontSize: 12,
    color: '#666',
  },
  storageIcons: {
    flexDirection: 'row',
  },
  proofButton: {
    backgroundColor: '#E3F2FD',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
  },
  proofButtonText: {
    fontSize: 12,
    color: '#2196F3',
    fontWeight: '600',
  },
  recordActions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 8,
    backgroundColor: '#F5F5F5',
    flex: 1,
    marginHorizontal: 4,
    justifyContent: 'center',
  },
  primaryAction: {
    backgroundColor: '#E3F2FD',
  },
  actionButtonText: {
    fontSize: 12,
    color: '#666',
    marginLeft: 4,
    fontWeight: '600',
  },
  primaryActionText: {
    color: '#2196F3',
  },
  settingsContainer: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  settingItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F0F0F0',
  },
  settingInfo: {
    flex: 1,
    marginRight: 12,
  },
  settingLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 2,
  },
  settingDescription: {
    fontSize: 12,
    color: '#666',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    width: width * 0.9,
    maxHeight: height * 0.8,
    overflow: 'hidden',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#F0F0F0',
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  closeButton: {
    padding: 4,
  },
  modalBody: {
    padding: 20,
  },
  proofDetails: {
    alignItems: 'center',
  },
  proofHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  proofStatus: {
    marginLeft: 12,
  },
  proofTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#4CAF50',
  },
  proofId: {
    fontSize: 12,
    color: '#666',
    marginTop: 2,
  },
  proofStatement: {
    fontSize: 14,
    color: '#333',
    textAlign: 'center',
    marginBottom: 20,
    lineHeight: 20,
  },
  proofMetadata: {
    width: '100%',
    marginBottom: 20,
  },
  metadataRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#F0F0F0',
  },
  metadataLabel: {
    fontSize: 14,
    color: '#666',
  },
  metadataValue: {
    fontSize: 14,
    color: '#333',
    fontWeight: '600',
  },
  verifyButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#4CAF50',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
    justifyContent: 'center',
  },
  verifyButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8,
  },
});
export default HealthDataPrivacyManager;