import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  Modal,
  ActivityIndicator,
} from 'react-native';
import { 
  healthDataService, 
  ExportFormat,
  ImportFormat 
} from '../../services/healthDataService';

interface HealthDataImportExportProps {
  userId: string;
}

export const HealthDataImportExport: React.FC<HealthDataImportExportProps> = ({ userId }) => {
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [modalType, setModalType] = useState<'export' | 'import'>('export');
  const [selectedFormat, setSelectedFormat] = useState<ExportFormat | ImportFormat>(ExportFormat.JSON);

  const exportFormats = [
    { value: ExportFormat.JSON, label: 'JSON', description: '标准JSON格式，适合程序处理' },
    { value: ExportFormat.CSV, label: 'CSV', description: 'Excel兼容格式，适合数据分析' },
    { value: ExportFormat.PDF, label: 'PDF', description: '便于打印和分享的报告格式' },
    { value: ExportFormat.XML, label: 'XML', description: '结构化数据格式' }
  ];

  const importFormats = [
    { value: ImportFormat.JSON, label: 'JSON', description: '从JSON文件导入数据' },
    { value: ImportFormat.CSV, label: 'CSV', description: '从CSV文件导入数据' },
    { value: ImportFormat.APPLE_HEALTH, label: 'Apple Health', description: '从Apple Health导入' },
    { value: ImportFormat.GOOGLE_FIT, label: 'Google Fit', description: '从Google Fit导入' }
  ];

  const handleExport = async (format: ExportFormat) => {
    try {
      setLoading(true);
      
      const endDate = new Date().toISOString();
      const startDate = new Date();
      startDate.setFullYear(startDate.getFullYear() - 1); // 导出一年的数据
      
      const response = await healthDataService.exportHealthData(
        userId,
        format,
        startDate.toISOString(),
        endDate
      );

      if (response.data) {
        Alert.alert('导出成功', '健康数据已导出完成');
        // 这里可以添加文件下载或分享逻辑
      }
    } catch (error) {
      console.error('导出健康数据失败:', error);
      Alert.alert('导出失败', '导出健康数据时发生错误');
    } finally {
      setLoading(false);
      setModalVisible(false);
    }
  };

  const handleImport = async (format: ImportFormat) => {
    try {
      setLoading(true);
      
      // 这里应该打开文件选择器
      Alert.alert('功能提示', '文件选择功能需要集成文件选择器组件');
      
      // 模拟导入过程
      // const response = await healthDataService.importHealthData(userId, format, fileData);
      
    } catch (error) {
      console.error('导入健康数据失败:', error);
      Alert.alert('导入失败', '导入健康数据时发生错误');
    } finally {
      setLoading(false);
      setModalVisible(false);
    }
  };

  const openExportModal = () => {
    setModalType('export');
    setSelectedFormat(ExportFormat.JSON);
    setModalVisible(true);
  };

  const openImportModal = () => {
    setModalType('import');
    setSelectedFormat(ImportFormat.JSON);
    setModalVisible(true);
  };

  const renderFormatOption = (format: any, label: string, description: string) => (
    <TouchableOpacity
      key={format}
      style={[
        styles.formatOption,
        selectedFormat === format && styles.formatOptionSelected
      ]}
      onPress={() => setSelectedFormat(format)}
    >
      <View style={styles.formatOptionContent}>
        <Text style={[
          styles.formatLabel,
          selectedFormat === format && styles.formatLabelSelected
        ]}>
          {label}
        </Text>
        <Text style={[
          styles.formatDescription,
          selectedFormat === format && styles.formatDescriptionSelected
        ]}>
          {description}
        </Text>
      </View>
      <View style={[
        styles.radioButton,
        selectedFormat === format && styles.radioButtonSelected
      ]}>
        {selectedFormat === format && <View style={styles.radioButtonInner} />}
      </View>
    </TouchableOpacity>
  );

  const renderModal = () => (
    <Modal
      visible={modalVisible}
      animationType="slide"
      transparent={true}
      onRequestClose={() => setModalVisible(false)}
    >
      <View style={styles.modalOverlay}>
        <View style={styles.modalContent}>
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>
              {modalType === 'export' ? '导出健康数据' : '导入健康数据'}
            </Text>
            <TouchableOpacity
              style={styles.closeButton}
              onPress={() => setModalVisible(false)}
            >
              <Text style={styles.closeButtonText}>×</Text>
            </TouchableOpacity>
          </View>

          <ScrollView style={styles.modalScrollView}>
            <Text style={styles.sectionTitle}>选择格式</Text>
            
            {modalType === 'export' 
              ? exportFormats.map(format => 
                  renderFormatOption(format.value, format.label, format.description)
                )
              : importFormats.map(format => 
                  renderFormatOption(format.value, format.label, format.description)
                )
            }

            {modalType === 'export' && (
              <View style={styles.exportOptions}>
                <Text style={styles.sectionTitle}>导出选项</Text>
                <View style={styles.optionItem}>
                  <Text style={styles.optionLabel}>数据范围</Text>
                  <Text style={styles.optionValue}>最近一年</Text>
                </View>
                <View style={styles.optionItem}>
                  <Text style={styles.optionLabel}>包含内容</Text>
                  <Text style={styles.optionValue}>所有健康数据</Text>
                </View>
              </View>
            )}

            {modalType === 'import' && (
              <View style={styles.importOptions}>
                <Text style={styles.sectionTitle}>导入说明</Text>
                <Text style={styles.importNote}>
                  • 导入的数据将与现有数据合并{'\n'}
                  • 重复的数据将被自动去重{'\n'}
                  • 导入过程可能需要几分钟时间{'\n'}
                  • 建议在导入前先备份现有数据
                </Text>
              </View>
            )}
          </ScrollView>

          <View style={styles.modalButtons}>
            <TouchableOpacity
              style={[styles.modalButton, styles.cancelButton]}
              onPress={() => setModalVisible(false)}
            >
              <Text style={styles.modalButtonText}>取消</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.modalButton, styles.confirmButton]}
              onPress={() => {
                if (modalType === 'export') {
                  handleExport(selectedFormat as ExportFormat);
                } else {
                  handleImport(selectedFormat as ImportFormat);
                }
              }}
              disabled={loading}
            >
              {loading ? (
                <ActivityIndicator color="#fff" size="small" />
              ) : (
                <Text style={styles.modalButtonText}>
                  {modalType === 'export' ? '导出' : '导入'}
                </Text>
              )}
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>
  );

  const renderQuickActions = () => (
    <View style={styles.quickActionsSection}>
      <Text style={styles.sectionTitle}>快速操作</Text>
      
      <View style={styles.quickActionsGrid}>
        <TouchableOpacity style={styles.quickActionCard} onPress={openExportModal}>
          <View style={[styles.quickActionIcon, { backgroundColor: '#4CAF50' }]}>
            <Text style={styles.quickActionIconText}>↗</Text>
          </View>
          <Text style={styles.quickActionTitle}>导出数据</Text>
          <Text style={styles.quickActionDescription}>备份您的健康数据</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.quickActionCard} onPress={openImportModal}>
          <View style={[styles.quickActionIcon, { backgroundColor: '#2196F3' }]}>
            <Text style={styles.quickActionIconText}>↙</Text>
          </View>
          <Text style={styles.quickActionTitle}>导入数据</Text>
          <Text style={styles.quickActionDescription}>从其他平台导入数据</Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={styles.quickActionCard}
          onPress={() => Alert.alert('功能提示', '同步功能正在开发中')}
        >
          <View style={[styles.quickActionIcon, { backgroundColor: '#FF9800' }]}>
            <Text style={styles.quickActionIconText}>⟲</Text>
          </View>
          <Text style={styles.quickActionTitle}>同步数据</Text>
          <Text style={styles.quickActionDescription}>与云端同步</Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={styles.quickActionCard}
          onPress={() => Alert.alert('功能提示', '分享功能正在开发中')}
        >
          <View style={[styles.quickActionIcon, { backgroundColor: '#9C27B0' }]}>
            <Text style={styles.quickActionIconText}>⤴</Text>
          </View>
          <Text style={styles.quickActionTitle}>分享报告</Text>
          <Text style={styles.quickActionDescription}>分享健康报告</Text>
        </TouchableOpacity>
      </View>
    </View>
  );

  const renderDataStats = () => (
    <View style={styles.dataStatsSection}>
      <Text style={styles.sectionTitle}>数据统计</Text>
      
      <View style={styles.statsGrid}>
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>1,234</Text>
          <Text style={styles.statLabel}>健康记录</Text>
        </View>
        
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>56</Text>
          <Text style={styles.statLabel}>生命体征</Text>
        </View>
        
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>12</Text>
          <Text style={styles.statLabel}>中医诊断</Text>
        </View>
        
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>8</Text>
          <Text style={styles.statLabel}>健康报告</Text>
        </View>
      </View>
    </View>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>数据管理</Text>
        <Text style={styles.subtitle}>导入、导出和管理您的健康数据</Text>
      </View>

      <ScrollView style={styles.scrollView}>
        {renderQuickActions()}
        {renderDataStats()}
      </ScrollView>

      {renderModal()}
    </View>
  );
};

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
  quickActionsSection: {
    padding: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 16,
  },
  quickActionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  quickActionCard: {
    width: '48%',
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  quickActionIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  quickActionIconText: {
    color: '#fff',
    fontSize: 20,
    fontWeight: 'bold',
  },
  quickActionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
    textAlign: 'center',
  },
  quickActionDescription: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
  },
  dataStatsSection: {
    padding: 16,
    paddingTop: 0,
  },
  statsGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  statCard: {
    flex: 1,
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginHorizontal: 4,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#007AFF',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: '#fff',
    borderRadius: 12,
    width: '90%',
    maxHeight: '80%',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  closeButton: {
    width: 30,
    height: 30,
    borderRadius: 15,
    backgroundColor: '#f0f0f0',
    justifyContent: 'center',
    alignItems: 'center',
  },
  closeButtonText: {
    fontSize: 20,
    color: '#666',
  },
  modalScrollView: {
    maxHeight: '70%',
    padding: 20,
  },
  formatOption: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#e0e0e0',
    marginBottom: 12,
    backgroundColor: '#fff',
  },
  formatOptionSelected: {
    borderColor: '#007AFF',
    backgroundColor: '#f0f8ff',
  },
  formatOptionContent: {
    flex: 1,
  },
  formatLabel: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  formatLabelSelected: {
    color: '#007AFF',
  },
  formatDescription: {
    fontSize: 14,
    color: '#666',
  },
  formatDescriptionSelected: {
    color: '#0066cc',
  },
  radioButton: {
    width: 20,
    height: 20,
    borderRadius: 10,
    borderWidth: 2,
    borderColor: '#e0e0e0',
    justifyContent: 'center',
    alignItems: 'center',
  },
  radioButtonSelected: {
    borderColor: '#007AFF',
  },
  radioButtonInner: {
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: '#007AFF',
  },
  exportOptions: {
    marginTop: 20,
  },
  optionItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  optionLabel: {
    fontSize: 14,
    color: '#333',
  },
  optionValue: {
    fontSize: 14,
    color: '#666',
  },
  importOptions: {
    marginTop: 20,
  },
  importNote: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
  },
  modalButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    padding: 20,
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
  },
  modalButton: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: 8,
    marginHorizontal: 8,
    justifyContent: 'center',
    alignItems: 'center',
  },
  cancelButton: {
    backgroundColor: '#666',
  },
  confirmButton: {
    backgroundColor: '#007AFF',
  },
  modalButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '500',
  },
}); 