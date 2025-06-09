import { useNavigation } from '@react-navigation/native';
import React, { useState } from 'react';
import {
  Alert,
  ScrollView,
  Share,
  StyleSheet,
  Switch,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { Button } from '../../components/ui/Button';
import {
  borderRadius,
  colors,
  shadows,
  spacing,
  typography,
} from '../../constants/theme';

interface SettingItem {
  id: string;,
  title: string;
  subtitle?: string;
  icon: string;,
  type: 'navigation' | 'switch' | 'action';
  value?: boolean;
  onPress?: () => void;
  onValueChange?: (value: boolean) => void;
  color?: string;
  badge?: string;
  disabled?: boolean;
}

interface SettingSection {
  id: string;,
  title: string;,
  items: SettingItem[];
}

const EnhancedSettingsScreen: React.FC = () => {
  const navigation = useNavigation();

  // 设置状态
  const [settings, setSettings] = useState({
    notifications: {,
  push: true,
      email: false,
      sms: false,
      healthReminders: true,
      medicationAlerts: true,
      appointmentReminders: true,
    },
    privacy: {,
  dataSharing: false,
      analytics: true,
      locationTracking: false,
      biometricAuth: true,
    },
    preferences: {,
  darkMode: false,
      language: 'zh-CN',
      units: 'metric',
      autoSync: true,
    },
  });

  // 用户信息
  const [userInfo] = useState({
    name: '张小明',
    email: 'zhangxiaoming@example.com',
    phone: '+86 138****8888',
    membershipLevel: 'Premium',
    joinDate: '2023-01-15',
  });

  // 更新设置
  const updateSetting = (category: string, key: string, value: boolean) => {
    setSettings(prev) => ({
      ...prev,
      [category]: {
        ...prev[category as keyof typeof prev],
        [key]: value,
      },
    }));
  };

  // 处理数据导出
  const handleExportData = () => {
    Alert.alert('导出数据', '选择导出格式', [
      { text: 'PDF报告', onPress: () => console.log('导出PDF') },
      { text: 'JSON数据', onPress: () => console.log('导出JSON') },
      { text: '取消', style: 'cancel' },
    ]);
  };

  // 处理清除缓存
  const handleClearCache = () => {
    Alert.alert('清除缓存', '确定要清除应用缓存吗？这不会删除您的个人数据。', [
      { text: '取消', style: 'cancel' },
      {
        text: '确定',
        onPress: () => {
          Alert.alert('成功', '缓存已清除');
        },
      },
    ]);
  };

  // 处理联系客服
  const handleContactSupport = () => {
    Alert.alert('联系客服', '选择联系方式', [
      { text: '在线客服', onPress: () => console.log('在线客服') },
      { text: '电话客服', onPress: () => console.log('电话客服') },
      { text: '取消', style: 'cancel' },
    ]);
  };

  // 处理分享应用
  const handleShareApp = async () => {
    try {
      await Share.share({
        message: '推荐一款很棒的健康管理应用 - 索克生活，快来下载体验吧！',
        url: 'https://example.com/download',
      });
    } catch (error) {
      console.error('分享失败:', error);
    }
  };

  // 处理退出登录
  const handleLogout = () => {
    Alert.alert('退出登录', '确定要退出当前账户吗？', [
      { text: '取消', style: 'cancel' },
      {
        text: '退出',
        style: 'destructive',
        onPress: () => {
          navigation.navigate('Auth' as never);
        },
      },
    ]);
  };

  // 设置项配置
  const settingSections: SettingSection[] = [
    {
      id: 'account',
      title: '账户信息',
      items: [
        {
          id: 'profile',
          title: '个人资料',
          subtitle: '编辑个人信息和头像',
          icon: 'account-edit',
          type: 'navigation',
          onPress: () => navigation.navigate('Profile' as never),
        },
        {
          id: 'membership',
          title: '会员中心',
          subtitle: `${userInfo.membershipLevel} 会员`,
          icon: 'crown',
          type: 'navigation',
          color: colors.warning,
          badge: 'Premium',
          onPress: () => navigation.navigate('Membership' as never),
        },
        {
          id: 'security',
          title: '账户安全',
          subtitle: '密码、双重验证',
          icon: 'shield-account',
          type: 'navigation',
          onPress: () => navigation.navigate('Security' as never),
        },
      ],
    },
    {
      id: 'notifications',
      title: '通知设置',
      items: [
        {
          id: 'push',
          title: '推送通知',
          subtitle: '接收应用推送消息',
          icon: 'bell',
          type: 'switch',
          value: settings.notifications.push,
          onValueChange: (value) =>
            updateSetting('notifications', 'push', value),
        },
        {
          id: 'email',
          title: '邮件通知',
          subtitle: '接收邮件提醒',
          icon: 'email',
          type: 'switch',
          value: settings.notifications.email,
          onValueChange: (value) =>
            updateSetting('notifications', 'email', value),
        },
        {
          id: 'healthReminders',
          title: '健康提醒',
          subtitle: '运动、饮水、用药提醒',
          icon: 'heart-pulse',
          type: 'switch',
          value: settings.notifications.healthReminders,
          onValueChange: (value) =>
            updateSetting('notifications', 'healthReminders', value),
        },
        {
          id: 'appointmentReminders',
          title: '预约提醒',
          subtitle: '医生预约、体检提醒',
          icon: 'calendar-clock',
          type: 'switch',
          value: settings.notifications.appointmentReminders,
          onValueChange: (value) =>
            updateSetting('notifications', 'appointmentReminders', value),
        },
      ],
    },
    {
      id: 'privacy',
      title: '隐私与安全',
      items: [
        {
          id: 'biometricAuth',
          title: '生物识别',
          subtitle: '使用指纹或面容解锁',
          icon: 'fingerprint',
          type: 'switch',
          value: settings.privacy.biometricAuth,
          onValueChange: (value) =>
            updateSetting('privacy', 'biometricAuth', value),
        },
        {
          id: 'dataSharing',
          title: '数据共享',
          subtitle: '与医疗机构共享健康数据',
          icon: 'share-variant',
          type: 'switch',
          value: settings.privacy.dataSharing,
          onValueChange: (value) =>
            updateSetting('privacy', 'dataSharing', value),
        },
        {
          id: 'analytics',
          title: '使用分析',
          subtitle: '帮助改善应用体验',
          icon: 'chart-line',
          type: 'switch',
          value: settings.privacy.analytics,
          onValueChange: (value) =>
            updateSetting('privacy', 'analytics', value),
        },
        {
          id: 'locationTracking',
          title: '位置追踪',
          subtitle: '用于运动轨迹记录',
          icon: 'map-marker',
          type: 'switch',
          value: settings.privacy.locationTracking,
          onValueChange: (value) =>
            updateSetting('privacy', 'locationTracking', value),
        },
      ],
    },
    {
      id: 'preferences',
      title: '偏好设置',
      items: [
        {
          id: 'darkMode',
          title: '深色模式',
          subtitle: '使用深色主题',
          icon: 'theme-light-dark',
          type: 'switch',
          value: settings.preferences.darkMode,
          onValueChange: (value) =>
            updateSetting('preferences', 'darkMode', value),
        },
        {
          id: 'language',
          title: '语言设置',
          subtitle: '简体中文',
          icon: 'translate',
          type: 'navigation',
          onPress: () => {
            /* 语言设置 */
          },
        },
        {
          id: 'units',
          title: '单位设置',
          subtitle: '公制单位',
          icon: 'ruler',
          type: 'navigation',
          onPress: () => {
            /* 单位设置 */
          },
        },
        {
          id: 'autoSync',
          title: '自动同步',
          subtitle: '自动同步健康数据',
          icon: 'sync',
          type: 'switch',
          value: settings.preferences.autoSync,
          onValueChange: (value) =>
            updateSetting('preferences', 'autoSync', value),
        },
      ],
    },
    {
      id: 'data',
      title: '数据管理',
      items: [
        {
          id: 'export',
          title: '导出数据',
          subtitle: '导出个人健康数据',
          icon: 'export',
          type: 'action',
          onPress: () => handleExportData(),
        },
        {
          id: 'backup',
          title: '备份与恢复',
          subtitle: '云端备份健康数据',
          icon: 'backup-restore',
          type: 'navigation',
          onPress: () => {
            /* 备份设置 */
          },
        },
        {
          id: 'clear',
          title: '清除缓存',
          subtitle: '清理应用缓存数据',
          icon: 'delete-sweep',
          type: 'action',
          onPress: () => handleClearCache(),
        },
      ],
    },
    {
      id: 'support',
      title: '帮助与支持',
      items: [
        {
          id: 'help',
          title: '帮助中心',
          subtitle: '常见问题与使用指南',
          icon: 'help-circle',
          type: 'navigation',
          onPress: () => navigation.navigate('Help' as never),
        },
        {
          id: 'feedback',
          title: '意见反馈',
          subtitle: '提交建议或问题反馈',
          icon: 'message-text',
          type: 'navigation',
          onPress: () => navigation.navigate('Feedback' as never),
        },
        {
          id: 'contact',
          title: '联系客服',
          subtitle: '在线客服支持',
          icon: 'headset',
          type: 'action',
          onPress: () => handleContactSupport(),
        },
        {
          id: 'share',
          title: '分享应用',
          subtitle: '推荐给朋友',
          icon: 'share',
          type: 'action',
          onPress: () => handleShareApp(),
        },
      ],
    },
    {
      id: 'about',
      title: '关于',
      items: [
        {
          id: 'version',
          title: '版本信息',
          subtitle: 'v1.0.0 (Build 100)',
          icon: 'information',
          type: 'navigation',
          onPress: () => {
            /* 版本信息 */
          },
        },
        {
          id: 'terms',
          title: '服务条款',
          subtitle: '用户协议与隐私政策',
          icon: 'file-document',
          type: 'navigation',
          onPress: () => navigation.navigate('Terms' as never),
        },
        {
          id: 'licenses',
          title: '开源许可',
          subtitle: '第三方库许可信息',
          icon: 'license',
          type: 'navigation',
          onPress: () => navigation.navigate('Licenses' as never),
        },
      ],
    },
  ];

  // 渲染设置项
  const renderSettingItem = (item: SettingItem) => {
    return (
      <TouchableOpacity;
        key={item.id}
        style={[styles.settingItem, item.disabled && styles.disabledItem]}
        onPress={item.onPress}
        disabled={item.disabled || item.type === 'switch'}
      >
        <View style={styles.itemLeft}>
          <View;
            style={[
              styles.iconContainer,
              item.color && { backgroundColor: item.color + '20' },
            ]}
          >
            <Icon;
              name={item.icon}
              size={20}
              color={item.color || colors.primary}
            />
          </View>
          <View style={styles.itemContent}>
            <View style={styles.titleRow}>
              <Text;
                style={[styles.itemTitle, item.disabled && styles.disabledText]}
              >
                {item.title}
              </Text>
              {item.badge && (
                <View;
                  style={[
                    styles.badge,
                    { backgroundColor: item.color || colors.primary },
                  ]}
                >
                  <Text style={styles.badgeText}>{item.badge}</Text>
                </View>
              )}
            </View>
            {item.subtitle && (
              <Text;
                style={[
                  styles.itemSubtitle,
                  item.disabled && styles.disabledText,
                ]}
              >
                {item.subtitle}
              </Text>
            )}
          </View>
        </View>

        <View style={styles.itemRight}>
          {item.type === 'switch' && (
            <Switch;
              value={item.value}
              onValueChange={item.onValueChange}
              trackColor={
                false: colors.gray300,
                true: colors.primary + '40',
              }}
              thumbColor={item.value ? colors.primary : colors.gray400}
              disabled={item.disabled}
            />
          )}
          {item.type === 'navigation' && (
            <Icon name="chevron-right" size={20} color={colors.textSecondary} />
          )}
        </View>
      </TouchableOpacity>
    );
  };

  // 渲染设置分组
  const renderSettingSection = (section: SettingSection) => {
    return (
      <View key={section.id} style={styles.section}>
        <Text style={styles.sectionTitle}>{section.title}</Text>
        <View style={styles.sectionContent}>
          {section.items.map(renderSettingItem)}
        </View>
      </View>
    );
  };

  // 渲染用户信息卡片
  const renderUserCard = () => (
    <View style={styles.userCard}>
      <View style={styles.userAvatar}>
        <Icon name="account" size={32} color={colors.white} />
      </View>
      <View style={styles.userInfo}>
        <Text style={styles.userName}>{userInfo.name}</Text>
        <Text style={styles.userEmail}>{userInfo.email}</Text>
        <View style={styles.membershipBadge}>
          <Icon name="crown" size={14} color={colors.warning} />
          <Text style={styles.membershipText}>
            {userInfo.membershipLevel} 会员
          </Text>
        </View>
      </View>
      <TouchableOpacity style={styles.editButton}>
        <Icon name="pencil" size={20} color={colors.primary} />
      </TouchableOpacity>
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      {/* 头部 */}
      <View style={styles.header}>
        <TouchableOpacity;
          style={styles.backButton}
          onPress={() => navigation.goBack()}
        >
          <Icon name="arrow-left" size={24} color={colors.text} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>设置</Text>
        <View style={styles.placeholder} />
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* 用户信息卡片 */}
        {renderUserCard()}

        {/* 设置分组 */}
        {settingSections.map(renderSettingSection)}

        {/* 退出登录按钮 */}
        <View style={styles.logoutContainer}>
          <Button title="退出登录" onPress={handleLogout} />
        </View>

        {/* 底部间距 */}
        <View style={styles.bottomSpacing} />
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {,
  flex: 1,
    backgroundColor: colors.background,
  },
  header: {,
  flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    backgroundColor: colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  backButton: {,
  width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.gray100,
    justifyContent: 'center',
    alignItems: 'center',
  },
  headerTitle: {,
  fontSize: typography.fontSize.lg,
    fontWeight: '600' as const,
    color: colors.text,
  },
  placeholder: {,
  width: 40,
  },
  content: {,
  flex: 1,
  },
  userCard: {,
  flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surface,
    margin: spacing.lg,
    padding: spacing.lg,
    borderRadius: borderRadius.lg,
    ...shadows.sm,
  },
  userAvatar: {,
  width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
  },
  userInfo: {,
  flex: 1,
    marginLeft: spacing.md,
  },
  userName: {,
  fontSize: typography.fontSize.lg,
    fontWeight: '600' as const,
    color: colors.text,
    marginBottom: spacing.xs,
  },
  userEmail: {,
  fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
  },
  membershipBadge: {,
  flexDirection: 'row',
    alignItems: 'center',
  },
  membershipText: {,
  fontSize: typography.fontSize.xs,
    color: colors.warning,
    marginLeft: spacing.xs,
    fontWeight: '600' as const,
  },
  editButton: {,
  width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: colors.gray100,
    justifyContent: 'center',
    alignItems: 'center',
  },
  section: {,
  marginBottom: spacing.lg,
  },
  sectionTitle: {,
  fontSize: typography.fontSize.sm,
    fontWeight: '600' as const,
    color: colors.textSecondary,
    marginHorizontal: spacing.lg,
    marginBottom: spacing.sm,
    textTransform: 'uppercase',
  },
  sectionContent: {,
  backgroundColor: colors.surface,
    marginHorizontal: spacing.lg,
    borderRadius: borderRadius.lg,
    ...shadows.sm,
  },
  settingItem: {,
  flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  disabledItem: {,
  opacity: 0.5,
  },
  itemLeft: {,
  flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  iconContainer: {,
  width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: colors.primary + '20',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.md,
  },
  itemContent: {,
  flex: 1,
  },
  titleRow: {,
  flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  itemTitle: {,
  fontSize: typography.fontSize.base,
    fontWeight: '500' as const,
    color: colors.text,
    flex: 1,
  },
  itemSubtitle: {,
  fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    marginTop: 2,
  },
  disabledText: {,
  color: colors.textSecondary,
  },
  badge: {,
  paddingHorizontal: spacing.xs,
    paddingVertical: 2,
    borderRadius: borderRadius.sm,
    marginLeft: spacing.sm,
  },
  badgeText: {,
  fontSize: typography.fontSize.xs,
    color: colors.white,
    fontWeight: '600' as const,
  },
  itemRight: {,
  marginLeft: spacing.md,
  },
  logoutContainer: {,
  margin: spacing.lg,
  },
  bottomSpacing: {,
  height: spacing.xl,
  },
});

export default EnhancedSettingsScreen;
