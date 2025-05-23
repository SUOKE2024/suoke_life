import React, { useState } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  Alert,
} from 'react-native';
import {
  Card,
  Title,
  Paragraph,
  Button,
  Text,
  Surface,
  Avatar,
  List,
  Divider,
  Switch,
  Badge,
} from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { useTheme } from 'react-native-paper';
import { useTranslation } from 'react-i18next';
import { useNavigation } from '@react-navigation/native';
import { useSelector } from 'react-redux';
import { useAppDispatch } from '../../hooks/redux';
import { logout } from '../../store/slices/userSlice';

const ProfileScreen = () => {
  const navigation = useNavigation<any>();
  const theme = useTheme();
  const { t } = useTranslation();
  const dispatch = useAppDispatch();
  const { currentUser } = useSelector((state: any) => state.user);
  
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [darkModeEnabled, setDarkModeEnabled] = useState(false);

  // 用户统计数据
  const userStats = {
    daysActive: 45,
    recordsCount: 128,
    assessmentsCount: 12,
    achievementsCount: 8,
  };

  // 菜单项
  const menuItems = [
    {
      title: '个人资料',
      description: '编辑个人信息和健康档案',
      icon: 'account-edit',
      route: 'ProfileSettings',
      badge: null,
    },
    {
      title: '健康数据',
      description: '查看和管理健康数据',
      icon: 'chart-line',
      route: 'HealthDataChart',
      badge: null,
    },
    {
      title: '对话历史',
      description: '查看与智能体的对话记录',
      icon: 'chat-processing',
      route: 'ChatHistory',
      badge: 3,
    },
    {
      title: '健康计划',
      description: '管理个人健康计划',
      icon: 'calendar-check',
      route: 'HealthPlan',
      badge: null,
    },
    {
      title: '成就徽章',
      description: '查看获得的健康成就',
      icon: 'medal',
      route: null,
      badge: userStats.achievementsCount,
    },
  ];

  const handleLogout = () => {
    Alert.alert(
      '确认退出',
      '您确定要退出登录吗？',
      [
        {
          text: '取消',
          style: 'cancel',
        },
        {
          text: '确定',
          onPress: () => {
            dispatch(logout());
          },
        },
      ]
    );
  };

  const renderUserInfo = () => (
    <Card style={styles.card}>
      <Card.Content>
        <View style={styles.userHeader}>
          <Avatar.Text
            size={64}
            label={currentUser?.name?.charAt(0) || 'U'}
            style={{ backgroundColor: theme.colors.primary }}
          />
          <View style={styles.userInfo}>
            <Title style={styles.userName}>{currentUser?.name || '用户'}</Title>
            <Text style={styles.userEmail}>{currentUser?.email || 'user@example.com'}</Text>
            <Text style={styles.userLevel}>健康达人 Lv.5</Text>
          </View>
        </View>

        {/* 用户统计 */}
        <View style={styles.statsContainer}>
          <View style={styles.statItem}>
            <Text style={styles.statNumber}>{userStats.daysActive}</Text>
            <Text style={styles.statLabel}>活跃天数</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statNumber}>{userStats.recordsCount}</Text>
            <Text style={styles.statLabel}>记录条数</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statNumber}>{userStats.assessmentsCount}</Text>
            <Text style={styles.statLabel}>评估次数</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statNumber}>{userStats.achievementsCount}</Text>
            <Text style={styles.statLabel}>获得成就</Text>
          </View>
        </View>
      </Card.Content>
    </Card>
  );

  const renderQuickActions = () => (
    <Card style={styles.card}>
      <Card.Content>
        <Title style={styles.cardTitle}>快捷操作</Title>
        <View style={styles.quickActions}>
          <Button
            mode="outlined"
            onPress={() => navigation.navigate('AgentSelection')}
            style={styles.actionButton}
            icon="robot"
          >
            智能体咨询
          </Button>
          <Button
            mode="outlined"
            onPress={() => navigation.navigate('HealthAssessment')}
            style={styles.actionButton}
            icon="clipboard-check"
          >
            健康评估
          </Button>
        </View>
      </Card.Content>
    </Card>
  );

  const renderMenuItems = () => (
    <Card style={styles.card}>
      <Card.Content style={styles.menuContent}>
        {menuItems.map((item, index) => (
          <View key={index}>
            <List.Item
              title={item.title}
              description={item.description}
              left={(props) => (
                <List.Icon {...props} icon={item.icon} color={theme.colors.primary} />
              )}
              right={(props) => (
                <View style={styles.listItemRight}>
                  {item.badge && (
                    <Badge style={styles.badge}>{item.badge}</Badge>
                  )}
                  <List.Icon {...props} icon="chevron-right" />
                </View>
              )}
              onPress={() => {
                if (item.route) {
                  navigation.navigate(item.route);
                }
              }}
              style={styles.listItem}
            />
            {index < menuItems.length - 1 && <Divider />}
          </View>
        ))}
      </Card.Content>
    </Card>
  );

  const renderSettings = () => (
    <Card style={styles.card}>
      <Card.Content style={styles.menuContent}>
        <Title style={styles.cardTitle}>设置</Title>
        
        <List.Item
          title="推送通知"
          description="接收健康提醒和消息通知"
          left={(props) => (
            <List.Icon {...props} icon="bell" color={theme.colors.primary} />
          )}
          right={() => (
            <Switch
              value={notificationsEnabled}
              onValueChange={setNotificationsEnabled}
            />
          )}
          style={styles.listItem}
        />
        
        <Divider />
        
        <List.Item
          title="深色模式"
          description="切换应用主题外观"
          left={(props) => (
            <List.Icon {...props} icon="theme-light-dark" color={theme.colors.primary} />
          )}
          right={() => (
            <Switch
              value={darkModeEnabled}
              onValueChange={setDarkModeEnabled}
            />
          )}
          style={styles.listItem}
        />
        
        <Divider />
        
        <List.Item
          title="语言设置"
          description="选择应用显示语言"
          left={(props) => (
            <List.Icon {...props} icon="translate" color={theme.colors.primary} />
          )}
          right={(props) => (
            <List.Icon {...props} icon="chevron-right" />
          )}
          onPress={() => {/* 语言设置 */}}
          style={styles.listItem}
        />
        
        <Divider />
        
        <List.Item
          title="隐私设置"
          description="管理数据隐私和权限"
          left={(props) => (
            <List.Icon {...props} icon="shield-account" color={theme.colors.primary} />
          )}
          right={(props) => (
            <List.Icon {...props} icon="chevron-right" />
          )}
          onPress={() => {/* 隐私设置 */}}
          style={styles.listItem}
        />
      </Card.Content>
    </Card>
  );

  const renderAbout = () => (
    <Card style={styles.card}>
      <Card.Content style={styles.menuContent}>
        <Title style={styles.cardTitle}>关于</Title>
        
        <List.Item
          title="帮助中心"
          description="使用指南和常见问题"
          left={(props) => (
            <List.Icon {...props} icon="help-circle" color={theme.colors.primary} />
          )}
          right={(props) => (
            <List.Icon {...props} icon="chevron-right" />
          )}
          onPress={() => {/* 帮助中心 */}}
          style={styles.listItem}
        />
        
        <Divider />
        
        <List.Item
          title="意见反馈"
          description="向我们提出建议和意见"
          left={(props) => (
            <List.Icon {...props} icon="message-text" color={theme.colors.primary} />
          )}
          right={(props) => (
            <List.Icon {...props} icon="chevron-right" />
          )}
          onPress={() => {/* 意见反馈 */}}
          style={styles.listItem}
        />
        
        <Divider />
        
        <List.Item
          title="关于索克生活"
          description="版本 1.0.0"
          left={(props) => (
            <List.Icon {...props} icon="information" color={theme.colors.primary} />
          )}
          right={(props) => (
            <List.Icon {...props} icon="chevron-right" />
          )}
          onPress={() => {/* 关于应用 */}}
          style={styles.listItem}
        />
      </Card.Content>
    </Card>
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Title style={styles.headerTitle}>个人中心</Title>
      </View>

      <ScrollView style={styles.content}>
        {renderUserInfo()}
        {renderQuickActions()}
        {renderMenuItems()}
        {renderSettings()}
        {renderAbout()}
        
        {/* 退出登录按钮 */}
        <Button
          mode="outlined"
          onPress={handleLogout}
          style={styles.logoutButton}
          textColor={theme.colors.error}
          icon="logout"
        >
          退出登录
        </Button>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    padding: 16,
    paddingBottom: 8,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  content: {
    flex: 1,
    padding: 16,
  },
  card: {
    marginBottom: 16,
    borderRadius: 12,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  userHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
  },
  userInfo: {
    flex: 1,
    marginLeft: 16,
  },
  userName: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  userEmail: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
  },
  userLevel: {
    fontSize: 12,
    color: '#FF9800',
    fontWeight: '500',
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
  },
  statItem: {
    alignItems: 'center',
  },
  statNumber: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#2196F3',
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
  },
  quickActions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  actionButton: {
    flex: 1,
    marginHorizontal: 4,
  },
  menuContent: {
    paddingHorizontal: 0,
  },
  listItem: {
    paddingHorizontal: 0,
  },
  listItemRight: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  badge: {
    marginRight: 8,
  },
  logoutButton: {
    marginTop: 16,
    marginBottom: 32,
    borderColor: '#F44336',
  },
});

export default ProfileScreen;