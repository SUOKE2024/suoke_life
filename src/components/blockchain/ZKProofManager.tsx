import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  TextInput,
  Modal,
  ScrollView
} from 'react-native';
import { useBlockchainService } from '../../hooks/useBlockchainService';
import { ZKProof, VerifyWithZKPRequest } from '../../types/blockchain';

interface ZKProofManagerProps {
  userId: string;
}

export const ZKProofManager: React.FC<ZKProofManagerProps> = ({ userId }) => {
  const {
    generateZKProof,
    verifyWithZKP,
    isLoading,
    error,
    clearError
  } = useBlockchainService();

  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [showVerifyModal, setShowVerifyModal] = useState(false);
  const [generatedProofs, setGeneratedProofs] = useState<Array<{
    id: string;
    proof: ZKProof;
    dataType: string;
    circuitType: string;
    timestamp: number;
  }>>([]);

  const handleGenerateProof = async (
    dataType: string,
    privateInputs: Record<string, any>,
    circuitType: string
  ) => {
    try {
      const proof = await generateZKProof(userId, dataType, privateInputs, circuitType);
      
      const proofRecord = {
        id: Date.now().toString(),
        proof,
        dataType,
        circuitType,
        timestamp: Date.now()
      };
      
      setGeneratedProofs(prev => [proofRecord, ...prev]);
      Alert.alert('成功', '零知识证明生成成功');
      setShowGenerateModal(false);
    } catch (error) {
      Alert.alert('错误', `生成证明失败: ${error instanceof Error ? error.message : '未知错误'}`);
    }
  };

  const handleVerifyProof = async (request: VerifyWithZKPRequest) => {
    try {
      const result = await verifyWithZKP(request);
      Alert.alert(
        '验证结果',
        result.valid ? '零知识证明验证通过' : '零知识证明验证失败',
        [
          {
            text: '查看详情',
            onPress: () => {
              Alert.alert('验证详情', JSON.stringify(result.verificationDetails, null, 2));
            }
          },
          { text: '确定' }
        ]
      );
      setShowVerifyModal(false);
    } catch (error) {
      Alert.alert('错误', `验证失败: ${error instanceof Error ? error.message : '未知错误'}`);
    }
  };

  const formatProofHash = (proof: Uint8Array) => {
    return Array.from(proof.slice(0, 8))
      .map(b => b.toString(16).padStart(2, '0'))
      .join('') + '...';
  };

  return (
    <View style={styles.container}>
      {/* 头部统计 */}
      <View style={styles.statsContainer}>
        <View style={styles.statItem}>
          <Text style={styles.statValue}>{generatedProofs.length}</Text>
          <Text style={styles.statLabel}>生成的证明</Text>
        </View>
        <View style={styles.statItem}>
          <Text style={styles.statValue}>
            {new Set(generatedProofs.map(p => p.circuitType)).size}
          </Text>
          <Text style={styles.statLabel}>电路类型</Text>
        </View>
        <View style={styles.statItem}>
          <Text style={styles.statValue}>
            {generatedProofs.length > 0 ? 
              new Date(Math.max(...generatedProofs.map(p => p.timestamp))).toLocaleDateString('zh-CN') : 
              '-'
            }
          </Text>
          <Text style={styles.statLabel}>最新证明</Text>
        </View>
      </View>

      {/* 操作按钮 */}
      <View style={styles.actionContainer}>
        <TouchableOpacity
          style={styles.generateButton}
          onPress={() => setShowGenerateModal(true)}
        >
          <Text style={styles.generateButtonText}>+ 生成证明</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.verifyButton}
          onPress={() => setShowVerifyModal(true)}
        >
          <Text style={styles.verifyButtonText}>验证证明</Text>
        </TouchableOpacity>
      </View>

      {/* 错误显示 */}
      {error && (
        <View style={styles.errorContainer}>
          <Text style={styles.errorText}>{error.message}</Text>
          <TouchableOpacity onPress={clearError} style={styles.errorCloseButton}>
            <Text style={styles.errorCloseText}>×</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* 证明列表 */}
      <ScrollView style={styles.proofsList} showsVerticalScrollIndicator={false}>
        {generatedProofs.length === 0 ? (
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>暂无生成的零知识证明</Text>
            <Text style={styles.emptySubtext}>点击"生成证明"开始创建您的第一个零知识证明</Text>
          </View>
        ) : (
          generatedProofs.map((proofRecord) => (
            <View key={proofRecord.id} style={styles.proofCard}>
              <View style={styles.proofHeader}>
                <Text style={styles.proofDataType}>{proofRecord.dataType}</Text>
                <Text style={styles.proofTime}>
                  {new Date(proofRecord.timestamp).toLocaleString('zh-CN')}
                </Text>
              </View>

              <View style={styles.proofContent}>
                <View style={styles.proofRow}>
                  <Text style={styles.proofLabel}>电路类型:</Text>
                  <Text style={styles.proofValue}>{proofRecord.circuitType}</Text>
                </View>

                <View style={styles.proofRow}>
                  <Text style={styles.proofLabel}>证明哈希:</Text>
                  <Text style={styles.proofValue}>{formatProofHash(proofRecord.proof.proof)}</Text>
                </View>

                <View style={styles.proofRow}>
                  <Text style={styles.proofLabel}>验证密钥:</Text>
                  <Text style={styles.proofValue}>{proofRecord.proof.verificationKey.slice(0, 16)}...</Text>
                </View>
              </View>
            </View>
          ))
        )}
      </ScrollView>

      {/* 生成证明模态框 */}
      <GenerateProofModal
        visible={showGenerateModal}
        onClose={() => setShowGenerateModal(false)}
        onSubmit={handleGenerateProof}
        isLoading={isLoading}
      />

      {/* 验证证明模态框 */}
      <VerifyProofModal
        visible={showVerifyModal}
        onClose={() => setShowVerifyModal(false)}
        onSubmit={handleVerifyProof}
        isLoading={isLoading}
        userId={userId}
      />
    </View>
  );
};

// 生成证明模态框
const GenerateProofModal: React.FC<{
  visible: boolean;
  onClose: () => void;
  onSubmit: (dataType: string, privateInputs: Record<string, any>, circuitType: string) => void;
  isLoading: boolean;
}> = ({ visible, onClose, onSubmit, isLoading }) => {
  const [dataType, setDataType] = useState('');
  const [circuitType, setCircuitType] = useState('age_verification');
  const [privateInputs, setPrivateInputs] = useState('');

  const handleSubmit = () => {
    if (!dataType.trim() || !privateInputs.trim()) {
      Alert.alert('错误', '请填写所有必填字段');
      return;
    }

    try {
      const inputs = JSON.parse(privateInputs);
      onSubmit(dataType.trim(), inputs, circuitType);
    } catch (error) {
      Alert.alert('错误', '私有输入格式不正确，请输入有效的JSON');
    }
  };

  return (
    <Modal visible={visible} animationType="slide" presentationStyle="pageSheet">
      <View style={styles.modalContainer}>
        <View style={styles.modalHeader}>
          <Text style={styles.modalTitle}>生成零知识证明</Text>
          <TouchableOpacity onPress={onClose}>
            <Text style={styles.modalCloseText}>取消</Text>
          </TouchableOpacity>
        </View>

        <ScrollView style={styles.modalContent}>
          <View style={styles.inputGroup}>
            <Text style={styles.inputLabel}>数据类型 *</Text>
            <TextInput
              style={styles.textInput}
              value={dataType}
              onChangeText={setDataType}
              placeholder="例如: age, health_score, medical_record"
            />
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.inputLabel}>私有输入 (JSON格式) *</Text>
            <TextInput
              style={[styles.textInput, styles.textArea]}
              value={privateInputs}
              onChangeText={setPrivateInputs}
              placeholder='例如: {"age": 25, "health_score": 85}'
              multiline
              numberOfLines={8}
            />
          </View>

          <TouchableOpacity
            style={[styles.submitButton, isLoading && styles.submitButtonDisabled]}
            onPress={handleSubmit}
            disabled={isLoading}
          >
            {isLoading ? (
              <ActivityIndicator size="small" color="#FFFFFF" />
            ) : (
              <Text style={styles.submitButtonText}>生成证明</Text>
            )}
          </TouchableOpacity>
        </ScrollView>
      </View>
    </Modal>
  );
};

// 验证证明模态框
const VerifyProofModal: React.FC<{
  visible: boolean;
  onClose: () => void;
  onSubmit: (request: VerifyWithZKPRequest) => void;
  isLoading: boolean;
  userId: string;
}> = ({ visible, onClose, onSubmit, isLoading, userId }) => {
  const [verifierId, setVerifierId] = useState('');
  const [dataType, setDataType] = useState('');
  const [proofData, setProofData] = useState('');
  const [publicInputs, setPublicInputs] = useState('');

  const handleSubmit = () => {
    if (!verifierId.trim() || !dataType.trim() || !proofData.trim() || !publicInputs.trim()) {
      Alert.alert('错误', '请填写所有字段');
      return;
    }

    try {
      const proof = new Uint8Array(JSON.parse(proofData));
      const inputs = new Uint8Array(JSON.parse(publicInputs));

      const request: VerifyWithZKPRequest = {
        userId,
        verifierId: verifierId.trim(),
        dataType: dataType.trim(),
        proof,
        publicInputs: inputs
      };

      onSubmit(request);
    } catch (error) {
      Alert.alert('错误', '证明数据格式不正确');
    }
  };

  return (
    <Modal visible={visible} animationType="slide" presentationStyle="pageSheet">
      <View style={styles.modalContainer}>
        <View style={styles.modalHeader}>
          <Text style={styles.modalTitle}>验证零知识证明</Text>
          <TouchableOpacity onPress={onClose}>
            <Text style={styles.modalCloseText}>取消</Text>
          </TouchableOpacity>
        </View>

        <ScrollView style={styles.modalContent}>
          <View style={styles.inputGroup}>
            <Text style={styles.inputLabel}>验证者ID *</Text>
            <TextInput
              style={styles.textInput}
              value={verifierId}
              onChangeText={setVerifierId}
              placeholder="验证者的唯一标识"
            />
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.inputLabel}>数据类型 *</Text>
            <TextInput
              style={styles.textInput}
              value={dataType}
              onChangeText={setDataType}
              placeholder="要验证的数据类型"
            />
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.inputLabel}>证明数据 (数组格式) *</Text>
            <TextInput
              style={[styles.textInput, styles.textArea]}
              value={proofData}
              onChangeText={setProofData}
              placeholder="例如: [123, 45, 67, 89, ...]"
              multiline
              numberOfLines={6}
            />
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.inputLabel}>公开输入 (数组格式) *</Text>
            <TextInput
              style={[styles.textInput, styles.textArea]}
              value={publicInputs}
              onChangeText={setPublicInputs}
              placeholder="例如: [18, 100, ...]"
              multiline
              numberOfLines={4}
            />
          </View>

          <TouchableOpacity
            style={[styles.submitButton, isLoading && styles.submitButtonDisabled]}
            onPress={handleSubmit}
            disabled={isLoading}
          >
            {isLoading ? (
              <ActivityIndicator size="small" color="#FFFFFF" />
            ) : (
              <Text style={styles.submitButtonText}>验证证明</Text>
            )}
          </TouchableOpacity>
        </ScrollView>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F9FA',
  },
  statsContainer: {
    flexDirection: 'row',
    backgroundColor: '#FFFFFF',
    padding: 16,
    marginBottom: 8,
  },
  statItem: {
    flex: 1,
    alignItems: 'center',
  },
  statValue: {
    fontSize: 18,
    fontWeight: '700',
    color: '#2C3E50',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: '#6C757D',
    textAlign: 'center',
  },
  actionContainer: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    paddingVertical: 8,
    gap: 12,
  },
  generateButton: {
    flex: 1,
    backgroundColor: '#8E44AD',
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  generateButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  verifyButton: {
    flex: 1,
    backgroundColor: '#3498DB',
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  verifyButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  errorContainer: {
    backgroundColor: '#FFE6E6',
    padding: 12,
    marginHorizontal: 16,
    marginVertical: 8,
    borderRadius: 8,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  errorText: {
    color: '#D32F2F',
    fontSize: 14,
    flex: 1,
  },
  errorCloseButton: {
    padding: 4,
  },
  errorCloseText: {
    color: '#D32F2F',
    fontSize: 18,
    fontWeight: 'bold',
  },
  proofsList: {
    flex: 1,
    paddingHorizontal: 16,
  },
  proofCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginVertical: 4,
    borderLeftWidth: 4,
    borderLeftColor: '#8E44AD',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  proofHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  proofDataType: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2C3E50',
  },
  proofTime: {
    fontSize: 12,
    color: '#6C757D',
  },
  proofContent: {
    marginBottom: 12,
  },
  proofRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  proofLabel: {
    fontSize: 14,
    color: '#6C757D',
    flex: 1,
  },
  proofValue: {
    fontSize: 14,
    color: '#2C3E50',
    flex: 2,
    textAlign: 'right',
    fontFamily: 'monospace',
  },
  emptyContainer: {
    padding: 32,
    alignItems: 'center',
  },
  emptyText: {
    fontSize: 16,
    color: '#6C757D',
    marginBottom: 8,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#ADB5BD',
    textAlign: 'center',
  },
  modalContainer: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#DEE2E6',
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#2C3E50',
  },
  modalCloseText: {
    fontSize: 16,
    color: '#007AFF',
  },
  modalContent: {
    flex: 1,
    padding: 16,
  },
  inputGroup: {
    marginBottom: 20,
  },
  inputLabel: {
    fontSize: 14,
    fontWeight: '500',
    color: '#2C3E50',
    marginBottom: 8,
  },
  textInput: {
    borderWidth: 1,
    borderColor: '#DEE2E6',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    backgroundColor: '#FFFFFF',
  },
  textArea: {
    height: 120,
    textAlignVertical: 'top',
  },
  submitButton: {
    backgroundColor: '#8E44AD',
    paddingVertical: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 20,
  },
  submitButtonDisabled: {
    backgroundColor: '#ADB5BD',
  },
  submitButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
}); 