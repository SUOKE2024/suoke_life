import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { colors, spacing, fonts } from '../../constants/theme';
import nativeModulesManager from '../../utils/nativeModules';
import notificationManager from '../../utils/notifications';



import React, { useState, useEffect } from 'react';
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Alert,
  Switch,
  ActivityIndicator,
} from 'react-native';

interface FeatureStatus {
  available: boolean;
  enabled: boolean;
  loading: boolean;
  error?: string;
}

interface NativeFeaturesState {
  camera: FeatureStatus;
  voice: FeatureStatus;
  location: FeatureStatus;
  notifications: FeatureStatus;
  permissions: {
    camera: boolean;
    microphone: boolean;
    location: boolean;
    notifications: boolean;
  };
}

const NativeFeaturesDemo: React.FC = () => {
  const [features, setFeatures] = useState<NativeFeaturesState>({
    camera: { available: false, enabled: false, loading: false },
    voice: { available: false, enabled: false, loading: false },
    location: { available: false, enabled: false, loading: false },
    notifications: { available: false, enabled: false, loading: false },
    permissions: {
      camera: false,
      microphone: false,
      location: false,
      notifications: false,
    },
  });

  const [isInitializing, setIsInitializing] = useState(true);

  useEffect(() => {
    initializeFeatures();
  }, []) // TODO: 检查依赖项 // TODO: 检查依赖项 // TODO: 检查依赖项 // TODO: 检查依赖项 // TODO: 检查依赖项;

  /**
   * 初始化所有原生功能
   */
  const initializeFeatures = async () => {
    setIsInitializing(true);
    
    try {
      // 检查原生模块状态
      const moduleStatus = nativeModulesManager.getModulesStatus();
      
      // 检查通知系统状态
      const notificationStatus = notificationManager.getNotificationStatus();
      
      // 初始化健康功能
      const healthFeatures = await nativeModulesManager.initializeHealthFeatures();
      
      setFeatures(prev => ({
        ...prev,
        camera: {
          available: moduleStatus.camera,
          enabled: false,
          loading: false,
        },
        voice: {
          available: moduleStatus.voice,
          enabled: false,
          loading: false,
        },
        location: {
          available: moduleStatus.location,
          enabled: false,
          loading: false,
        },
        notifications: {
          available: notificationStatus.modulesAvailable.local || notificationStatus.modulesAvailable.remote,
          enabled: false,
          loading: false,
        },
        permissions: {
          camera: healthFeatures.permissions.camera.granted,
          microphone: healthFeatures.permissions.microphone.granted,
          location: healthFeatures.permissions.location.granted,
          notifications: false, // 需要异步检查
        },
      }));

      console.log('🚀 原生功能初始化完成');
    } catch (error) {
      console.error('❌ 原生功能初始化失败:', error);
      Alert.alert('初始化失败', '部分原生功能可能无法正常使用');
    } finally {
      setIsInitializing(false);
    }
  };

  /**
   * 请求所有健康权限
   */
  const requestAllPermissions = async () => {
    setIsInitializing(true);
    
    try {
      const success = await nativeModulesManager.requestHealthPermissions();
      
      if (success) {
        // 重新检查权限状态
        await initializeFeatures();
      }
    } catch (error) {
      console.error('请求权限失败:', error);
    } finally {
      setIsInitializing(false);
    }
  };

  /**
   * 测试相机功能
   */
  const testCamera = async () => {
    setFeatures(prev => ({
      ...prev,
      camera: { ...prev.camera, loading: true },
    }));

    try {
      const photo = await nativeModulesManager.takePhoto({
        quality: 'high',
        cameraPosition: 'back',
      });

      if (photo) {
        Alert.alert('拍照成功', `照片已保存: ${photo.path}`);
        setFeatures(prev => ({
          ...prev,
          camera: { ...prev.camera, enabled: true, loading: false },
        }));
      } else {
        throw new Error('拍照失败');
      }
    } catch (error) {
      console.error('相机测试失败:', error);
      setFeatures(prev => ({
        ...prev,
        camera: { ...prev.camera, loading: false, error: '相机功能测试失败' },
      }));
    }
  };

  /**
   * 测试语音识别功能
   */
  const testVoiceRecognition = async () => {
    setFeatures(prev => ({
      ...prev,
      voice: { ...prev.voice, loading: true },
    }));

    try {
      await nativeModulesManager.startVoiceRecognition({
        locale: 'zh-CN',
        continuous: false,
        timeout: 5000,
      });

      // 模拟5秒后停止
      setTimeout(async () => {
        await nativeModulesManager.stopVoiceRecognition();
        setFeatures(prev => ({
          ...prev,
          voice: { ...prev.voice, enabled: true, loading: false },
        }));
        Alert.alert('语音识别测试', '语音识别功能测试完成');
      }, 5000);
    } catch (error) {
      console.error('语音识别测试失败:', error);
      setFeatures(prev => ({
        ...prev,
        voice: { ...prev.voice, loading: false, error: '语音识别功能测试失败' },
      }));
    }
  };

  /**
   * 测试位置服务功能
   */
  const testLocation = async () => {
    setFeatures(prev => ({
      ...prev,
      location: { ...prev.location, loading: true },
    }));

    try {
      const location = await nativeModulesManager.getCurrentLocation({
        accuracy: 'high',
        timeout: 10000,
      });

      if (location) {
        Alert.alert(
          '定位成功',
          `纬度: ${location.latitude.toFixed(6)}\n经度: ${location.longitude.toFixed(6)}\n精度: ${location.accuracy}米`
        );
        setFeatures(prev => ({
          ...prev,
          location: { ...prev.location, enabled: true, loading: false },
        }));
      } else {
        throw new Error('定位失败');
      }
    } catch (error) {
      console.error('位置服务测试失败:', error);
      setFeatures(prev => ({
        ...prev,
        location: { ...prev.location, loading: false, error: '位置服务功能测试失败' },
      }));
    }
  };

  /**
   * 测试推送通知功能
   */
  const testNotifications = async () => {
    setFeatures(prev => ({
      ...prev,
      notifications: { ...prev.notifications, loading: true },
    }));

    try {
      // 创建测试通知
      const success = await notificationManager.scheduleLocalNotification({
        id: 'test_notification',
        title: '测试通知',
        body: '这是一个测试通知，用于验证推送功能是否正常工作',
        date: new Date(Date.now() + 3000), // 3秒后
      });

      if (success) {
        Alert.alert('通知测试', '测试通知已安排，将在3秒后显示');
        setFeatures(prev => ({
          ...prev,
          notifications: { ...prev.notifications, enabled: true, loading: false },
        }));
      } else {
        throw new Error('通知安排失败');
      }
    } catch (error) {
      console.error('推送通知测试失败:', error);
      setFeatures(prev => ({
        ...prev,
        notifications: { ...prev.notifications, loading: false, error: '推送通知功能测试失败' },
      }));
    }
  };

  /**
   * 创建健康提醒
   */
  const createHealthReminders = async () => {
    try {
      await notificationManager.createCommonHealthReminders();
      Alert.alert('健康提醒', '常用健康提醒模板已创建，您可以在设置中启用');
    } catch (error) {
      console.error('创建健康提醒失败:', error);
      Alert.alert('创建失败', '健康提醒创建失败，请稍后重试');
    }
  };

  /**
   * 渲染功能状态指示器
   */
  const renderStatusIndicator = useCallback( (status: FeatureStatus) => {, []);
    if (status.loading) {
      return <ActivityIndicator size="small" color={colors.primary} />;
    }

    if (status.error) {
      return <Icon name="alert-circle" size={20} color={colors.error} />;
    }

    if (status.enabled) {
      return <Icon name="check-circle" size={20} color={colors.success} />;
    }

    if (status.available) {
      return <Icon name="circle-outline" size={20} color={colors.textSecondary} />;
    }

    return <Icon name="close-circle" size={20} color={colors.error} />;
  };

  /**
   * 渲染权限状态
   */
  const renderPermissionStatus = useCallback( (granted: boolean) => {, []);
    return (
      <Icon
        name={granted ? "shield-check" : "shield-alert"}
        size={16}
        color={granted ? colors.success : colors.warning}
      />
    );
  };

  if (isInitializing) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={styles.loadingText}>正在初始化原生功能...</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      <View style={styles.header}>
        <Icon name="cellphone-cog" size={32} color={colors.primary} />
        <Text style={styles.title}>原生功能演示</Text>
        <Text style={styles.subtitle}>测试设备权限和原生模块集成</Text>
      </View>

      {/* 权限状态 */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>权限状态</Text>
        <View style={styles.permissionGrid}>
          <View style={styles.permissionItem}>
            {renderPermissionStatus(features.permissions.camera)}
            <Text style={styles.permissionText}>相机</Text>
          </View>
          <View style={styles.permissionItem}>
            {renderPermissionStatus(features.permissions.microphone)}
            <Text style={styles.permissionText}>麦克风</Text>
          </View>
          <View style={styles.permissionItem}>
            {renderPermissionStatus(features.permissions.location)}
            <Text style={styles.permissionText}>位置</Text>
          </View>
          <View style={styles.permissionItem}>
            {renderPermissionStatus(features.permissions.notifications)}
            <Text style={styles.permissionText}>通知</Text>
          </View>
        </View>
        
        <TouchableOpacity
          style={styles.permissionButton}
          onPress={requestAllPermissions}
        >
          <Icon name="shield-key" size={20} color="white" />
          <Text style={styles.permissionButtonText}>请求所有权限</Text>
        </TouchableOpacity>
      </View>

      {/* 功能测试 */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>功能测试</Text>
        
        {/* 相机功能 */}
        <View style={styles.featureCard}>
          <View style={styles.featureHeader}>
            <Icon name="camera" size={24} color={colors.primary} />
            <Text style={styles.featureName}>相机功能</Text>
            {renderStatusIndicator(features.camera)}
          </View>
          <Text style={styles.featureDescription}>
            测试相机拍照功能，用于五诊中的望诊
          </Text>
          <TouchableOpacity
            style={[
              styles.testButton,
              !features.camera.available && styles.testButtonDisabled,
            ]}
            onPress={testCamera}
            disabled={!features.camera.available || features.camera.loading}
          >
            <Text style={styles.testButtonText}>测试拍照</Text>
          </TouchableOpacity>
        </View>

        {/* 语音识别功能 */}
        <View style={styles.featureCard}>
          <View style={styles.featureHeader}>
            <Icon name="microphone" size={24} color={colors.primary} />
            <Text style={styles.featureName}>语音识别</Text>
            {renderStatusIndicator(features.voice)}
          </View>
          <Text style={styles.featureDescription}>
            测试语音识别功能，用于五诊中的问诊
          </Text>
          <TouchableOpacity
            style={[
              styles.testButton,
              !features.voice.available && styles.testButtonDisabled,
            ]}
            onPress={testVoiceRecognition}
            disabled={!features.voice.available || features.voice.loading}
          >
            <Text style={styles.testButtonText}>
              {features.voice.loading ? '正在识别...' : '测试语音识别'}
            </Text>
          </TouchableOpacity>
        </View>

        {/* 位置服务功能 */}
        <View style={styles.featureCard}>
          <View style={styles.featureHeader}>
            <Icon name="map-marker" size={24} color={colors.primary} />
            <Text style={styles.featureName}>位置服务</Text>
            {renderStatusIndicator(features.location)}
          </View>
          <Text style={styles.featureDescription}>
            测试位置服务功能，用于基于位置的健康服务
          </Text>
          <TouchableOpacity
            style={[
              styles.testButton,
              !features.location.available && styles.testButtonDisabled,
            ]}
            onPress={testLocation}
            disabled={!features.location.available || features.location.loading}
          >
            <Text style={styles.testButtonText}>
              {features.location.loading ? '正在定位...' : '测试定位'}
            </Text>
          </TouchableOpacity>
        </View>

        {/* 推送通知功能 */}
        <View style={styles.featureCard}>
          <View style={styles.featureHeader}>
            <Icon name="bell" size={24} color={colors.primary} />
            <Text style={styles.featureName}>推送通知</Text>
            {renderStatusIndicator(features.notifications)}
          </View>
          <Text style={styles.featureDescription}>
            测试推送通知功能，用于健康提醒和消息推送
          </Text>
          <View style={styles.buttonRow}>
            <TouchableOpacity
              style={[
                styles.testButton,
                styles.halfButton,
                !features.notifications.available && styles.testButtonDisabled,
              ]}
              onPress={testNotifications}
              disabled={!features.notifications.available || features.notifications.loading}
            >
              <Text style={styles.testButtonText}>测试通知</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.testButton, styles.halfButton]}
              onPress={createHealthReminders}
            >
              <Text style={styles.testButtonText}>创建提醒</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>

      {/* 状态说明 */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>状态说明</Text>
        <View style={styles.legendContainer}>
          <View style={styles.legendItem}>
            <Icon name="check-circle" size={16} color={colors.success} />
            <Text style={styles.legendText}>功能已启用</Text>
          </View>
          <View style={styles.legendItem}>
            <Icon name="circle-outline" size={16} color={colors.textSecondary} />
            <Text style={styles.legendText}>功能可用</Text>
          </View>
          <View style={styles.legendItem}>
            <Icon name="close-circle" size={16} color={colors.error} />
            <Text style={styles.legendText}>功能不可用</Text>
          </View>
          <View style={styles.legendItem}>
            <Icon name="alert-circle" size={16} color={colors.error} />
            <Text style={styles.legendText}>功能错误</Text>
          </View>
        </View>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.background,
  },
  loadingText: {
    marginTop: spacing.md,
    fontSize: fonts.size.md,
    color: colors.textSecondary,
  },
  header: {
    alignItems: 'center',
    padding: spacing.lg,
    backgroundColor: colors.surface,
    marginBottom: spacing.md,
  },
  title: {
    fontSize: fonts.size.xl,
    fontWeight: '600',
    color: colors.text,
    marginTop: spacing.sm,
  },
  subtitle: {
    fontSize: fonts.size.md,
    color: colors.textSecondary,
    marginTop: spacing.xs,
    textAlign: 'center',
  },
  section: {
    backgroundColor: colors.surface,
    marginHorizontal: spacing.md,
    marginBottom: spacing.md,
    borderRadius: 12,
    padding: spacing.lg,
  },
  sectionTitle: {
    fontSize: fonts.size.lg,
    fontWeight: '600',
    color: colors.text,
    marginBottom: spacing.md,
  },
  permissionGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: spacing.md,
  },
  permissionItem: {
    width: '48%',
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing.sm,
    backgroundColor: colors.background,
    borderRadius: 8,
    marginBottom: spacing.sm,
  },
  permissionText: {
    marginLeft: spacing.sm,
    fontSize: fonts.size.sm,
    color: colors.text,
  },
  permissionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.primary,
    padding: spacing.md,
    borderRadius: 8,
  },
  permissionButtonText: {
    marginLeft: spacing.sm,
    fontSize: fonts.size.md,
    fontWeight: '600',
    color: 'white',
  },
  featureCard: {
    backgroundColor: colors.background,
    borderRadius: 8,
    padding: spacing.md,
    marginBottom: spacing.md,
  },
  featureHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  featureName: {
    flex: 1,
    marginLeft: spacing.sm,
    fontSize: fonts.size.md,
    fontWeight: '600',
    color: colors.text,
  },
  featureDescription: {
    fontSize: fonts.size.sm,
    color: colors.textSecondary,
    marginBottom: spacing.md,
    lineHeight: 18,
  },
  testButton: {
    backgroundColor: colors.primary,
    padding: spacing.md,
    borderRadius: 8,
    alignItems: 'center',
  },
  testButtonDisabled: {
    backgroundColor: colors.textSecondary,
    opacity: 0.5,
  },
  testButtonText: {
    fontSize: fonts.size.md,
    fontWeight: '600',
    color: 'white',
  },
  buttonRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  halfButton: {
    width: '48%',
  },
  legendContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
    width: '48%',
    marginBottom: spacing.sm,
  },
  legendText: {
    marginLeft: spacing.sm,
    fontSize: fonts.size.sm,
    color: colors.textSecondary,
  },
});

export default NativeFeaturesDemo; 