import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Switch,
  TextInput,
  TouchableOpacity,
  Alert,
  Modal,
} from 'react-native';
import {
  GATEWAY_FEATURES,
  GATEWAY_PERFORMANCE_CONFIG,
  GATEWAY_CACHE_CONFIG,
  getCurrentEnvConfig,
} from '../../constants/config';
import { useApiService } from '../../services/IntegratedApiService';

interface ConfigItem {
  key: string;
  label: string;
  type: 'boolean' | 'number' | 'string';
  value: any;
  description?: string;
  min?: number;
  max?: number;
}

interface ConfigSection {
  title: string;
  items: ConfigItem[];
}

const GatewayConfig: React.FC = () => {
  const { apiService } = useApiService();
  const [configs, setConfigs] = useState<ConfigSection[]>([]);
  const [isEditing, setIsEditing] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);

  // 初始化配置
  useEffect(() => {
    initializeConfigs();
  }, [])  // 检查是否需要添加依赖项;

  const initializeConfigs = () => {
    const configSections: ConfigSection[] = [
      {
        title: '功能特性',
        items: Object.entries(GATEWAY_FEATURES).map(([key, value]) => ({
          key: `features.${key}`,
          label: formatLabel(key),
          type: 'boolean',
          value,
          description: getFeatureDescription(key),
        })),
      },
      {
        title: '性能配置',
        items: [
          {
            key: 'performance.TIMEOUT',
            label: '请求超时时间',
            type: 'number',
            value: GATEWAY_PERFORMANCE_CONFIG.TIMEOUT,
            description: '单个请求的超时时间（毫秒）',
            min: 1000,
            max: 120000,
          },
          {
            key: 'performance.RETRY_ATTEMPTS',
            label: '重试次数',
            type: 'number',
            value: GATEWAY_PERFORMANCE_CONFIG.RETRY_ATTEMPTS,
            description: '请求失败时的重试次数',
            min: 0,
            max: 10,
          },
          {
            key: 'performance.RETRY_DELAY',
            label: '重试延迟',
            type: 'number',
            value: GATEWAY_PERFORMANCE_CONFIG.RETRY_DELAY,
            description: '重试之间的延迟时间（毫秒）',
            min: 100,
            max: 10000,
          },
          {
            key: 'performance.STREAM_TIMEOUT',
            label: '流式超时时间',
            type: 'number',
            value: GATEWAY_PERFORMANCE_CONFIG.STREAM_TIMEOUT,
            description: '流式请求的超时时间（毫秒）',
            min: 10000,
            max: 300000,
          },
        ],
      },
      {
        title: '熔断器配置',
        items: [
          {
            key: 'circuitBreaker.FAILURE_THRESHOLD',
            label: '失败阈值',
            type: 'number',
            value: GATEWAY_PERFORMANCE_CONFIG.CIRCUIT_BREAKER.FAILURE_THRESHOLD,
            description: '触发熔断的连续失败次数',
            min: 1,
            max: 20,
          },
          {
            key: 'circuitBreaker.RECOVERY_TIMEOUT',
            label: '恢复超时',
            type: 'number',
            value: GATEWAY_PERFORMANCE_CONFIG.CIRCUIT_BREAKER.RECOVERY_TIMEOUT,
            description: '熔断器恢复尝试的超时时间（毫秒）',
            min: 10000,
            max: 300000,
          },
          {
            key: 'circuitBreaker.MONITORING_PERIOD',
            label: '监控周期',
            type: 'number',
            value: GATEWAY_PERFORMANCE_CONFIG.CIRCUIT_BREAKER.MONITORING_PERIOD,
            description: '监控失败率的时间窗口（毫秒）',
            min: 5000,
            max: 120000,
          },
        ],
      },
      {
        title: '缓存配置',
        items: [
          {
            key: 'cache.TTL',
            label: '默认TTL',
            type: 'number',
            value: GATEWAY_CACHE_CONFIG.TTL,
            description: '缓存项的默认生存时间（毫秒）',
            min: 1000,
            max: 3600000,
          },
          {
            key: 'cache.MAX_SIZE',
            label: '最大缓存数',
            type: 'number',
            value: GATEWAY_CACHE_CONFIG.MAX_SIZE,
            description: '缓存中最大项目数',
            min: 10,
            max: 1000,
          },
          {
            key: 'cache.ENABLE_PERSISTENCE',
            label: '启用持久化',
            type: 'boolean',
            value: GATEWAY_CACHE_CONFIG.ENABLE_PERSISTENCE,
            description: '是否将缓存持久化到本地存储',
          },
        ],
      },
    ];

    setConfigs(configSections);
  };

  // 格式化标签
  const formatLabel = (key: string): string => {
    return key
      .replace('ENABLE_', '')
      .replace(/_/g, ' ')
      .toLowerCase()
      .replace(/\b\w/g, l => l.toUpperCase());
  };

  // 获取功能描述
  const getFeatureDescription = (key: string): string => {
    const descriptions: Record<string, string> = {
      ENABLE_STREAMING: '启用流式响应处理',
      ENABLE_MULTIMODAL: '启用多模态数据处理',
      ENABLE_TCM: '启用中医相关功能',
      ENABLE_OFFLINE: '启用离线模式支持',
      ENABLE_ANALYTICS: '启用分析和统计',
      ENABLE_CACHING: '启用响应缓存',
      ENABLE_CIRCUIT_BREAKER: '启用熔断器保护',
      ENABLE_RATE_LIMITING: '启用请求限流',
      ENABLE_AUTHENTICATION: '启用身份认证',
      ENABLE_MONITORING: '启用监控和日志',
    };
    return descriptions[key] || '功能开关';
  };

  // 更新配置值
  const updateConfigValue = (key: string, value: any) => {
    setConfigs(prevConfigs =>
      prevConfigs.map(section => ({
        ...section,
        items: section.items.map(item =>
          item.key === key ? { ...item, value } : item
        ),
      }))
    );
    setHasChanges(true);
  };

  // 保存配置
  const saveConfigs = async () => {
    try {
      // 这里应该调用API保存配置
      // 目前只是模拟保存到本地存储
      const configData = configs.reduce((acc, section) => {
        section.items.forEach(item => {
          acc[item.key] = item.value;
        });
        return acc;
      }, {} as Record<string, any>);

      // 保存到本地存储
      if (typeof localStorage !== 'undefined') {
        localStorage.setItem('gateway_config', JSON.stringify(configData));
      }

      Alert.alert('成功', '配置已保存');
      setHasChanges(false);
      setIsEditing(false);
    } catch (error) {
      Alert.alert('错误', '保存配置失败');
    }
  };

  // 重置配置
  const resetConfigs = () => {
    Alert.alert(
      '确认重置',
      '这将重置所有配置到默认值，确定继续吗？',
      [
        { text: '取消', style: 'cancel' },
        {
          text: '确定',
          style: 'destructive',
          onPress: () => {
            initializeConfigs();
            setHasChanges(false);
            setIsEditing(false);
          },
        },
      ]
    );
  };

  // 清除缓存
  const clearCache = () => {
    Alert.alert(
      '清除缓存',
      '确定要清除所有缓存数据吗？',
      [
        { text: '取消', style: 'cancel' },
        {
          text: '确定',
          onPress: () => {
            apiService.clearCache();
            Alert.alert('成功', '缓存已清除');
          },
        },
      ]
    );
  };

  // 渲染配置项
  const renderConfigItem = (item: ConfigItem) => {
    const { key, label, type, value, description, min, max } = item;

    return (
      <View key={key} style={styles.configItem}>
        <View style={styles.configHeader}>
          <Text style={styles.configLabel}>{label}</Text>
          {type === 'boolean' && (
            <Switch
              value={value}
              onValueChange={(newValue) => updateConfigValue(key, newValue)}
              disabled={!isEditing}
            />
          )}
        </View>

        {description && (
          <Text style={styles.configDescription}>{description}</Text>
        )}

        {type === 'number' && (
          <View style={styles.numberInputContainer}>
            <TextInput
              style={[styles.numberInput, !isEditing && styles.disabledInput]}
              value={value.toString()}
              onChangeText={(text) => {
                const numValue = parseInt(text) || 0;
                const clampedValue = Math.max(min || 0, Math.min(max || Infinity, numValue));
                updateConfigValue(key, clampedValue);
              }}
              keyboardType="numeric"
              editable={isEditing}
            />
            {min !== undefined && max !== undefined && (
              <Text style={styles.rangeText}>
                范围: {min} - {max}
              </Text>
            )}
          </View>
        )}

        {type === 'string' && (
          <TextInput
            style={[styles.textInput, !isEditing && styles.disabledInput]}
            value={value}
            onChangeText={(text) => updateConfigValue(key, text)}
            editable={isEditing}
          />
        )}
      </View>
    );
  };

  // 渲染配置节
  const renderConfigSection = (section: ConfigSection) => {
    return (
      <View key={section.title} style={styles.section}>
        <Text style={styles.sectionTitle}>{section.title}</Text>
        {section.items.map(renderConfigItem)}
      </View>
    );
  };

  return (
    <View style={styles.container}>
      {/* 头部 */}
      <View style={styles.header}>
        <Text style={styles.title}>网关配置</Text>
        <View style={styles.headerActions}>
          <TouchableOpacity
            style={[styles.actionButton, styles.clearButton]}
            onPress={clearCache}
          >
            <Text style={styles.actionButtonText}>清除缓存</Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={[styles.actionButton, styles.advancedButton]}
            onPress={() => setShowAdvanced(!showAdvanced)}
          >
            <Text style={styles.actionButtonText}>
              {showAdvanced ? '隐藏高级' : '显示高级'}
            </Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* 配置内容 */}
      <ScrollView style={styles.content}>
        {configs.map((section, index) => {
          // 高级配置只在显示高级时展示
          if (!showAdvanced && (index > 1)) return null;
          return renderConfigSection(section);
        })}
      </ScrollView>

      {/* 底部操作栏 */}
      <View style={styles.footer}>
        {!isEditing ? (
          <TouchableOpacity
            style={[styles.footerButton, styles.editButton]}
            onPress={() => setIsEditing(true)}
          >
            <Text style={styles.footerButtonText}>编辑配置</Text>
          </TouchableOpacity>
        ) : (
          <View style={styles.editActions}>
            <TouchableOpacity
              style={[styles.footerButton, styles.cancelButton]}
              onPress={() => {
                if (hasChanges) {
                  Alert.alert(
                    '放弃更改',
                    '有未保存的更改，确定要放弃吗？',
                    [
                      { text: '取消', style: 'cancel' },
                      {
                        text: '放弃',
                        style: 'destructive',
                        onPress: () => {
                          initializeConfigs();
                          setIsEditing(false);
                          setHasChanges(false);
                        },
                      },
                    ]
                  );
                } else {
                  setIsEditing(false);
                }
              }}
            >
              <Text style={styles.footerButtonText}>取消</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[styles.footerButton, styles.resetButton]}
              onPress={resetConfigs}
            >
              <Text style={styles.footerButtonText}>重置</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[
                styles.footerButton,
                styles.saveButton,
                !hasChanges && styles.disabledButton,
              ]}
              onPress={saveConfigs}
              disabled={!hasChanges}
            >
              <Text style={styles.footerButtonText}>保存</Text>
            </TouchableOpacity>
          </View>
        )}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: '#fff',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 12,
  },
  headerActions: {
    flexDirection: 'row',
    gap: 8,
  },
  actionButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 6,
    borderWidth: 1,
  },
  clearButton: {
    borderColor: '#f44336',
    backgroundColor: '#fff',
  },
  advancedButton: {
    borderColor: '#2196f3',
    backgroundColor: '#fff',
  },
  actionButtonText: {
    fontSize: 14,
    fontWeight: '500',
  },
  content: {
    flex: 1,
  },
  section: {
    margin: 16,
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 16,
  },
  configItem: {
    marginBottom: 16,
    paddingBottom: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  configHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  configLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    flex: 1,
  },
  configDescription: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  numberInputContainer: {
    marginTop: 8,
  },
  numberInput: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 6,
    padding: 12,
    fontSize: 16,
    backgroundColor: '#fff',
  },
  textInput: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 6,
    padding: 12,
    fontSize: 16,
    backgroundColor: '#fff',
    marginTop: 8,
  },
  disabledInput: {
    backgroundColor: '#f5f5f5',
    color: '#999',
  },
  rangeText: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
  },
  footer: {
    backgroundColor: '#fff',
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
  },
  footerButton: {
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 6,
    alignItems: 'center',
  },
  footerButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#fff',
  },
  editButton: {
    backgroundColor: '#2196f3',
  },
  editActions: {
    flexDirection: 'row',
    gap: 12,
  },
  cancelButton: {
    backgroundColor: '#9e9e9e',
    flex: 1,
  },
  resetButton: {
    backgroundColor: '#ff9800',
    flex: 1,
  },
  saveButton: {
    backgroundColor: '#4caf50',
    flex: 1,
  },
  disabledButton: {
    backgroundColor: '#ccc',
  },
});

export default GatewayConfig; 