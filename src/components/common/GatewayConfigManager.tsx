import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, TextInput, Switch, Alert } from 'react-native';
import { configService } from '../../services/configService';
import { analyticsService } from '../../services/analyticsService';
import { syncService } from '../../services/syncService';
import { offlineService } from '../../services/offlineService';
interface ConfigSection {
  id: string;
  title: string;
  icon: string;
  configs: ConfigItem[];
}
interface ConfigItem {
  key: string;
  label: string;
  type: 'boolean' | 'number' | 'string' | 'select';
  value: any;
  description?: string;
  options?: { label: string; value: any;
}[];
  min?: number;
  max?: number;
  unit?: string;
}
interface GatewayConfigManagerProps {
  visible?: boolean;
  onClose?: () => void;
}
export const GatewayConfigManager: React.FC<GatewayConfigManagerProps> = ({
  visible = true,
  onClose,
}) => {
  const [configs, setConfigs] = useState<ConfigSection[]>([]);
  const [activeSection, setActiveSection] = useState('gateway');
  const [hasChanges, setHasChanges] = useState(false);
  const [saving, setSaving] = useState(false);
  useEffect() => {
    if (visible) {
      loadConfigurations();
    }
  }, [visible]);
  const loadConfigurations = async () => {
    try {
      // 加载各种配置
      const gatewayConfig = {
        timeout: configService.get('gateway.timeout', 30000),
        retryAttempts: configService.get('gateway.retryAttempts', 3),
        retryDelay: configService.get('gateway.retryDelay', 1000),
        enableCache: configService.get('gateway.enableCache', true),
        cacheTimeout: configService.get('gateway.cacheTimeout', 300000),
        enableCircuitBreaker: configService.get('gateway.enableCircuitBreaker', true),
      };
      const analyticsConfig = analyticsService.getConfig();
      const syncConfig = syncService.getConfig();
      const offlineConfig = offlineService.getSyncStatus();
      const configSections: ConfigSection[] = [
        {
      id: "gateway",
      title: 'API网关配置',
          icon: '🌐',
          configs: [
            {
      key: "timeout",
      label: '请求超时时间',
              type: 'number',
              value: gatewayConfig.timeout || 30000,
              description: '单个请求的最大等待时间',
              min: 1000,
              max: 120000,
              unit: 'ms',
            },
            {
      key: "retryAttempts",
      label: '重试次数',
              type: 'number',
              value: gatewayConfig.retryAttempts || 3,
              description: '请求失败时的重试次数',
              min: 0,
              max: 10,
            },
            {
      key: "retryDelay",
      label: '重试延迟',
              type: 'number',
              value: gatewayConfig.retryDelay || 1000,
              description: '重试之间的延迟时间',
              min: 100,
              max: 10000,
              unit: 'ms',
            },
            {
      key: "enableCache",
      label: '启用缓存',
              type: 'boolean',
              value: gatewayConfig.enableCache !== false,
              description: '是否启用响应缓存',
            },
            {
      key: "cacheTimeout",
      label: '缓存超时时间',
              type: 'number',
              value: gatewayConfig.cacheTimeout || 300000,
              description: '缓存数据的有效期',
              min: 10000,
              max: 3600000,
              unit: 'ms',
            },
            {
      key: "enableCircuitBreaker",
      label: '启用熔断器',
              type: 'boolean',
              value: gatewayConfig.enableCircuitBreaker !== false,
              description: '是否启用熔断器保护',
            },
          ],
        },
        {
      id: "analytics",
      title: '分析配置',
          icon: '📊',
          configs: [
            {
      key: "enabled",
      label: '启用分析',
              type: 'boolean',
              value: analyticsConfig.enabled,
              description: '是否收集分析数据',
            },
            {
      key: "batchSize",
      label: '批处理大小',
              type: 'number',
              value: analyticsConfig.batchSize,
              description: '批量发送事件的数量',
              min: 10,
              max: 200,
            },
            {
      key: "flushInterval",
      label: '刷新间隔',
              type: 'number',
              value: analyticsConfig.flushInterval,
              description: '自动发送数据的间隔',
              min: 5000,
              max: 300000,
              unit: 'ms',
            },
            {
      key: "enableUserTracking",
      label: '用户行为跟踪',
              type: 'boolean',
              value: analyticsConfig.enableUserTracking,
              description: '是否跟踪用户行为',
            },
            {
      key: "enablePerformanceTracking",
      label: '性能跟踪',
              type: 'boolean',
              value: analyticsConfig.enablePerformanceTracking,
              description: '是否跟踪性能指标',
            },
            {
      key: "enableErrorTracking",
      label: '错误跟踪',
              type: 'boolean',
              value: analyticsConfig.enableErrorTracking,
              description: '是否跟踪错误信息',
            },
          ],
        },
        {
      id: "sync",
      title: '同步配置',
          icon: '🔄',
          configs: [
            {
      key: "enabled",
      label: '启用同步',
              type: 'boolean',
              value: syncConfig.enabled,
              description: '是否启用数据同步',
            },
            {
      key: "autoSync",
      label: '自动同步',
              type: 'boolean',
              value: syncConfig.autoSync,
              description: '是否自动同步数据',
            },
            {
      key: "syncInterval",
      label: '同步间隔',
              type: 'number',
              value: syncConfig.syncInterval,
              description: '自动同步的时间间隔',
              min: 60000,
              max: 3600000,
              unit: 'ms',
            },
            {
      key: "batchSize",
      label: '批处理大小',
              type: 'number',
              value: syncConfig.batchSize,
              description: '批量同步的数据量',
              min: 10,
              max: 200,
            },
            {
      key: "conflictResolution",
      label: '冲突解决策略',
              type: 'select',
              value: syncConfig.conflictResolution,
              description: '数据冲突时的处理方式',
              options: [
                {
      label: "手动处理",
      value: 'manual' },
                {
      label: "使用本地数据",
      value: 'local' },
                {
      label: "使用远程数据",
      value: 'remote' },
                {
      label: "自动合并",
      value: 'merge' },
              ],
            },
            {
      key: "retryAttempts",
      label: '重试次数',
              type: 'number',
              value: syncConfig.retryAttempts,
              description: '同步失败时的重试次数',
              min: 0,
              max: 10,
            },
          ],
        },
        {
      id: "offline",
      title: '离线配置',
          icon: '📱',
          configs: [
            {
      key: "enableOffline",
      label: '启用离线模式',
              type: 'boolean',
              value: true, // 从离线服务状态推断
              description: '是否支持离线操作',
            },
            {
      key: "maxCacheSize",
      label: '最大缓存大小',
              type: 'number',
              value: 50, // 默认值
              description: '离线缓存的最大条目数',
              min: 10,
              max: 500,
            },
            {
      key: "cacheStrategy",
      label: '缓存策略',
              type: 'select',
              value: 'lru', // 默认值
              description: '缓存淘汰策略',
              options: [
                {
      label: "LRU (最近最少使用)",
      value: 'lru' },
                {
      label: "FIFO (先进先出)",
      value: 'fifo' },
                {
      label: "TTL (基于时间)",
      value: 'ttl' },
              ],
            },
            {
      key: "autoCleanup",
      label: '自动清理',
              type: 'boolean',
              value: true,
              description: '是否自动清理过期缓存',
            },
          ],
        },
      ];
      setConfigs(configSections);
    } catch (error) {
      console.error('Error loading configurations:', error);
      Alert.alert("错误",加载配置失败');
    }
  };
  const updateConfigValue = (sectionId: string, configKey: string, value: any) => {
    setConfigs(prevConfigs =>
      prevConfigs.map(section =>
        section.id === sectionId;
          ? {
              ...section,
              configs: section.configs.map(config =>
                config.key === configKey ? { ...config, value } : config,
              ),
            }
          : section,
      ),
    );
    setHasChanges(true);
  };
  const saveConfigurations = async () => {
    try {
      setSaving(true);
      // 构建配置对象
      const newConfigs: Record<string, any> = {};
      configs.forEach(section => {
        newConfigs[section.id] = {};
        section.configs.forEach(config => {
          newConfigs[section.id][config.key] = config.value;
        });
      });
      // 应用配置到各个服务
      if (newConfigs.gateway) {
        // 使用configService的set方法更新配置
        for (const [key, value] of Object.entries(newConfigs.gateway)) {
          await configService.set(`gateway.${key}`, value);
        }
      }
      if (newConfigs.analytics) {
        analyticsService.updateConfig(newConfigs.analytics);
      }
      if (newConfigs.sync) {
        syncService.updateConfig(newConfigs.sync);
      }
      // 记录配置更改事件
      analyticsService.trackEvent('system', {
      action: "config_updated",
      sections: Object.keys(newConfigs),
      });
      setHasChanges(false);
      Alert.alert("成功",配置已保存');
    } catch (error) {
      console.error('Error saving configurations:', error);
      Alert.alert("错误",保存配置失败');
    } finally {
      setSaving(false);
    }
  };
  const resetToDefaults = () => {
    Alert.alert(
      "重置配置",确定要重置所有配置到默认值吗？',
      [
        {
      text: "取消",
      style: 'cancel' },
        {
      text: "确定",
      style: 'destructive',
          onPress: () => {
            loadConfigurations();
            setHasChanges(false);
          },
        },
      ],
    );
  };
  const renderConfigItem = (sectionId: string, config: ConfigItem) => {
    const renderInput = () => {
      switch (config.type) {
        case 'boolean':
          return (
            <Switch;
              value={config.value}
              onValueChange={(value) => updateConfigValue(sectionId, config.key, value)}
              trackColor={
      false: "#e0e0e0",
      true: '#007AFF' }}
              thumbColor={config.value ? '#fff' : '#f4f3f4'}
            />
          );
        case 'number':
          return (
            <View style={styles.numberInput}>
              <TextInput;
                style={styles.textInput}
                value={String(config.value)}
                onChangeText={(text) => {
                  const num = parseInt(text) || 0;
                  const clampedValue = Math.max(
                    config.min || 0,
                    Math.min(config.max || Infinity, num),
                  );
                  updateConfigValue(sectionId, config.key, clampedValue);
                }}
                keyboardType="numeric"
                placeholder="0"
              />
              {config.unit && (
                <Text style={styles.unitText}>{config.unit}</Text>
              )}
            </View>
          );
        case 'string':
          return (
            <TextInput;
              style={styles.textInput}
              value={config.value}
              onChangeText={(value) => updateConfigValue(sectionId, config.key, value)}
              placeholder="输入值"
            />
          );
        case 'select':
          return (
            <View style={styles.selectContainer}>
              {config.options?.map((option => (
                <TouchableOpacity;
                  key={option.value}
                  style={[
                    styles.selectOption, config.value === option.value && styles.selectedOption,
                  ]}
                  onPress={() => updateConfigValue(sectionId, config.key, option.value)}
                >
                  <Text style={[
                    styles.selectOptionText,
                    config.value === option.value && styles.selectedOptionText,
                  ]}>
                    {option.label}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          );
        default:
          return null;
      }
    };
    return (
      <View key={config.key} style={styles.configItem}>
        <View style={styles.configHeader}>
          <Text style={styles.configLabel}>{config.label}</Text>
          {config.type !== 'select' && (
        <View style={styles.configInput}>
              {renderInput()}
            </View>
          )}
        </View>
        {config.description && (
          <Text style={styles.configDescription}>{config.description}</Text>
        )}
        {config.type === 'select' && (
        <View style={styles.configSelectWrapper}>
            {renderInput()}
          </View>
        )}
        {config.type === 'number' && config.min !== undefined && config.max !== undefined && (
          <Text style={styles.configRange}>
            范围: {config.min} - {config.max} {config.unit || ''}
          </Text>
        )}
      </View>
    );
  };
  const renderSection = (section: ConfigSection) => (
    <View key={section.id} style={styles.section}>
      <Text style={styles.sectionTitle}>
        {section.icon} {section.title}
      </Text>
      {section.configs.map(config => renderConfigItem(section.id, config))}
    </View>
  );
  if (!visible) return null;
  const activeConfigSection = configs.find(section => section.id === activeSection);
  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>网关配置管理</Text>
        <View style={styles.headerActions}>
          {hasChanges && (
            <TouchableOpacity;
              style={styles.saveButton}
              onPress={saveConfigurations}
              disabled={saving}
            >
              <Text style={styles.saveButtonText}>
                {saving ? '保存中...' : '💾 保存'}
              </Text>
            </TouchableOpacity>
          )}
          <TouchableOpacity;
            style={styles.resetButton}
            onPress={resetToDefaults}
          >
            <Text style={styles.resetButtonText}>🔄 重置</Text>
          </TouchableOpacity>
          {onClose && (
            <TouchableOpacity style={styles.closeButton} onPress={onClose}>
              <Text style={styles.closeText}>✕</Text>
            </TouchableOpacity>
          )}
        </View>
      </View>
      <View style={styles.body}>
        <View style={styles.sidebar}>
          <Text style={styles.sidebarTitle}>配置分类</Text>
          {configs.map((section => (
            <TouchableOpacity;
              key={section.id}
              style={[
                styles.sidebarItem, activeSection === section.id && styles.activeSidebarItem,
              ]}
              onPress={() => setActiveSection(section.id)}
            >
              <Text style={styles.sidebarIcon}>{section.icon}</Text>
              <Text style={[
                styles.sidebarText,
                activeSection === section.id && styles.activeSidebarText,
              ]}>
                {section.title}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
        <ScrollView style={styles.content}>
          {activeConfigSection && renderSection(activeConfigSection)}
        </ScrollView>
      </View>
      {hasChanges && (
        <View style={styles.changesBanner}>
          <Text style={styles.changesText}>⚠️ 有未保存的更改</Text>
        </View>
      )}
    </View>
  );
};
const styles = StyleSheet.create({
  container: {,
  flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {,
  flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  title: {,
  fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  headerActions: {,
  flexDirection: 'row',
    alignItems: 'center',
  },
  saveButton: {,
  paddingHorizontal: 12,
    paddingVertical: 6,
    backgroundColor: '#00aa00',
    borderRadius: 6,
    marginRight: 8,
  },
  saveButtonText: {,
  color: '#fff',
    fontSize: 14,
    fontWeight: '500',
  },
  resetButton: {,
  paddingHorizontal: 12,
    paddingVertical: 6,
    backgroundColor: '#ff8800',
    borderRadius: 6,
    marginRight: 8,
  },
  resetButtonText: {,
  color: '#fff',
    fontSize: 14,
    fontWeight: '500',
  },
  closeButton: {,
  padding: 8,
  },
  closeText: {,
  fontSize: 18,
    color: '#666',
  },
  body: {,
  flex: 1,
    flexDirection: 'row',
  },
  sidebar: {,
  width: 200,
    backgroundColor: '#fff',
    borderRightWidth: 1,
    borderRightColor: '#e0e0e0',
    padding: 16,
  },
  sidebarTitle: {,
  fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 16,
  },
  sidebarItem: {,
  flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 8,
    borderRadius: 6,
    marginBottom: 4,
  },
  activeSidebarItem: {,
  backgroundColor: '#e3f2fd',
  },
  sidebarIcon: {,
  fontSize: 16,
    marginRight: 8,
  },
  sidebarText: {,
  fontSize: 14,
    color: '#666',
    flex: 1,
  },
  activeSidebarText: {,
  color: '#007AFF',
    fontWeight: '500',
  },
  content: {,
  flex: 1,
    padding: 16,
  },
  section: {,
  backgroundColor: '#fff',
    borderRadius: 8,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  sectionTitle: {,
  fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 16,
  },
  configItem: {,
  marginBottom: 20,
    paddingBottom: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  configHeader: {,
  flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  configLabel: {,
  fontSize: 16,
    fontWeight: '500',
    color: '#333',
    flex: 1,
  },
  configInput: {,
  marginLeft: 16,
  },
  configDescription: {,
  fontSize: 12,
    color: '#666',
    marginBottom: 8,
  },
  configSelectWrapper: {,
  marginTop: 8,
  },
  configRange: {,
  fontSize: 11,
    color: '#999',
    marginTop: 4,
  },
  textInput: {,
  borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 6,
    paddingHorizontal: 12,
    paddingVertical: 8,
    fontSize: 14,
    backgroundColor: '#fff',
    minWidth: 120,
  },
  numberInput: {,
  flexDirection: 'row',
    alignItems: 'center',
  },
  unitText: {,
  fontSize: 12,
    color: '#666',
    marginLeft: 8,
  },
  selectContainer: {,
  flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  selectOption: {,
  paddingHorizontal: 12,
    paddingVertical: 6,
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 6,
    backgroundColor: '#fff',
  },
  selectedOption: {,
  backgroundColor: '#007AFF',
    borderColor: '#007AFF',
  },
  selectOptionText: {,
  fontSize: 12,
    color: '#666',
  },
  selectedOptionText: {,
  color: '#fff',
  },
  changesBanner: {,
  backgroundColor: '#fff3e0',
    padding: 12,
    borderTopWidth: 1,
    borderTopColor: '#ff8800',
    alignItems: 'center',
  },
  changesText: {,
  fontSize: 14,
    color: '#e65100',
    fontWeight: '500',
  },
});
export default GatewayConfigManager;
