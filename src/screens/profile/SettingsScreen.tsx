import { useNavigation } from '@react-navigation/native';
import React, { useCallback } from 'react';
import {;
  Alert,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

export const SettingsScreen: React.FC = () => {
  const navigation = useNavigation();

  const handleLogout = useCallback(async () => {
    Alert.alert('确认退出', '确定要退出登录吗？', [
      { text: '取消', style: 'cancel' },
      {
        text: '确定',
        onPress: () => {
          // 这里应该调用实际的退出登录逻辑
          Alert.alert('提示', '退出登录功能待实现');
        }
      }
    ]);
  }, []);

  const navigateToServiceStatus = useCallback() => {
    navigation.navigate('ServiceStatus' as never);
  }, [navigation]);

  const navigateToServiceManagement = useCallback() => {
    navigation.navigate('ServiceManagement' as never);
  }, [navigation]);

  const navigateToDeveloperPanel = useCallback() => {
    navigation.navigate('DeveloperPanel' as never);
  }, [navigation]);

  const handleClearCache = useCallback() => {
    Alert.alert('确认清除', '确定要清除应用缓存吗？', [
      { text: '取消', style: 'cancel' },
      {
        text: '确定',
        onPress: () => {
          Alert.alert('成功', '缓存已清除');
        }
      }
    ]);
  }, []);

  const handleCheckUpdate = useCallback() => {
    Alert.alert('检查更新', '当前已是最新版本');
  }, []);

  const handleAbout = useCallback() => {
    Alert.alert(
      '关于索克生活',
      '版本: 1.0.0\n构建: 100\n\n索克生活是一个由人工智能智能体驱动的现代化健康管理平台。',
      [{ text: '确定' }]
    );
  }, []);

  const renderSettingItem = (title: string, onPress?: () => void) => (
    <TouchableOpacity style={styles.settingItem} onPress={onPress}>
      <Text style={styles.settingText}>{title}</Text>
      <Text style={styles.arrow}>›</Text>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Text style={styles.backButton}>←</Text>
        </TouchableOpacity>
        <Text style={styles.title}>设置</Text>
        <View style={styles.placeholder} />
      </View>

      <ScrollView style={styles.content}>
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>账户设置</Text>
          {renderSettingItem('个人资料')}
          {renderSettingItem('修改密码')}
          {renderSettingItem('隐私设置')}
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>应用设置</Text>
          {renderSettingItem('通知设置')}
          {renderSettingItem('语言设置')}
          {renderSettingItem('显示主题')}
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>系统与开发</Text>
          {renderSettingItem('服务状态', navigateToServiceStatus)}
          {renderSettingItem('服务管理', navigateToServiceManagement)}
          {renderSettingItem('开发者面板', navigateToDeveloperPanel)}
          {renderSettingItem('清除缓存', handleClearCache)}
          {renderSettingItem('检查更新', handleCheckUpdate)}
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>其他</Text>
          {renderSettingItem('关于我们', handleAbout)}
          {renderSettingItem('帮助与反馈')}
          {renderSettingItem('服务条款')}
        </View>

        <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
          <Text style={styles.logoutButtonText}>退出登录</Text>
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {,
  flex: 1,
    backgroundColor: '#F5F7FA'
  },
  header: {,
  flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 16,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E1E8ED'
  },
  backButton: {,
  fontSize: 24,
    color: '#2C3E50'
  },
  title: {,
  fontSize: 18,
    fontWeight: 'bold',
    color: '#2C3E50'
  },
  placeholder: {,
  width: 24
  },
  content: {,
  flex: 1,
    padding: 20
  },
  section: {,
  marginBottom: 24,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3
  },
  sectionTitle: {,
  fontSize: 16,
    fontWeight: 'bold',
    color: '#7F8C8D',
    marginBottom: 16,
    textTransform: 'uppercase',
    letterSpacing: 0.5
  },
  settingItem: {,
  flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#F8F9FA'
  },
  settingText: {,
  fontSize: 16,
    color: '#2C3E50'
  },
  arrow: {,
  fontSize: 20,
    color: '#BDC3C7'
  },
  logoutButton: {,
  marginVertical: 24,
    backgroundColor: '#E74C3C',
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3
  },
  logoutButtonText: {,
  color: '#FFFFFF',
    fontSize: 16,
    fontWeight: 'bold'
  }
});

export default SettingsScreen;
