import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  FlatList,
  Image,
  Alert,
  RefreshControl,
  TextInput,
  Platform,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { colors, typography, spacing, borderRadius, shadows } from '../../constants/theme';
// import { Divider } from '../../components/ui';

// 联系人类型定义
export interface Contact {
  id: string;
  name: string;
  avatar?: string;
  type: 'agent' | 'doctor' | 'user' | 'supplier' | 'service';
  status: 'online' | 'offline' | 'busy' | 'away';
  lastMessage?: string;
  lastMessageTime?: string;
  unreadCount?: number;
  specialty?: string; // 医生专业或智能体特长
  verified?: boolean; // 是否认证
  vip?: boolean; // 是否VIP
}

// 联系人分组
export interface ContactGroup {
  id: string;
  title: string;
  icon: string;
  contacts: Contact[];
  collapsed?: boolean;
}

type MainTabParamList = {
  Home: undefined;
  Suoke: undefined;
  Explore: undefined;
  Life: undefined;
  Profile: undefined;
};

type HomeScreenNavigationProp = NativeStackNavigationProp<MainTabParamList, 'Home'>;

// 简单的分割线组件
const Divider: React.FC<{ style?: any }> = ({ style }) => (
  <View style={[{ height: 1, backgroundColor: colors.border }, style]} />
);

const HomeScreen: React.FC = () => {
  const navigation = useNavigation<HomeScreenNavigationProp>();
  
  const [searchText, setSearchText] = useState('');
  const [refreshing, setRefreshing] = useState(false);
  const [contactGroups, setContactGroups] = useState<ContactGroup[]>([]);
  const [filteredContacts, setFilteredContacts] = useState<Contact[]>([]);

  // 初始化联系人数据
  const initializeContacts = useCallback(() => {
    const groups: ContactGroup[] = [
      {
        id: 'agents',
        title: '四大智能体',
        icon: '🤖',
        contacts: [
          {
            id: 'xiaoai',
            name: '小艾',
            type: 'agent',
            status: 'online',
            lastMessage: '您好！我是小艾，您的健康管理助手',
            lastMessageTime: '刚刚',
            unreadCount: 0,
            specialty: '健康管理·AI助手',
            verified: true,
          },
          {
            id: 'xiaoke',
            name: '小克',
            type: 'agent',
            status: 'online',
            lastMessage: '为您提供专业的中医诊断服务',
            lastMessageTime: '2分钟前',
            unreadCount: 1,
            specialty: '中医诊断·辨证论治',
            verified: true,
          },
          {
            id: 'laoke',
            name: '老克',
            type: 'agent',
            status: 'online',
            lastMessage: '传统中医智慧，现代科技应用',
            lastMessageTime: '5分钟前',
            unreadCount: 0,
            specialty: '中医养生·经验传承',
            verified: true,
          },
          {
            id: 'soer',
            name: '索儿',
            type: 'agent',
            status: 'online',
            lastMessage: '生活方式指导，健康习惯养成',
            lastMessageTime: '10分钟前',
            unreadCount: 2,
            specialty: '生活指导·习惯养成',
            verified: true,
          },
        ],
      },
      {
        id: 'doctors',
        title: '名医专家',
        icon: '👨‍⚕️',
        contacts: [
          {
            id: 'doctor1',
            name: '张明华',
            type: 'doctor',
            status: 'online',
            lastMessage: '您的检查报告已出，建议...',
            lastMessageTime: '1小时前',
            unreadCount: 1,
            specialty: '中医内科·主任医师',
            verified: true,
            vip: true,
          },
          {
            id: 'doctor2',
            name: '李慧敏',
            type: 'doctor',
            status: 'busy',
            lastMessage: '今天的针灸治疗效果如何？',
            lastMessageTime: '2小时前',
            unreadCount: 0,
            specialty: '针灸科·副主任医师',
            verified: true,
          },
          {
            id: 'doctor3',
            name: '王德仁',
            type: 'doctor',
            status: 'offline',
            lastMessage: '按时服药，注意饮食调理',
            lastMessageTime: '昨天',
            unreadCount: 0,
            specialty: '中药调理·主治医师',
            verified: true,
          },
        ],
      },
      {
        id: 'users',
        title: '健康伙伴',
        icon: '👥',
        contacts: [
          {
            id: 'user1',
            name: '健康小组',
            type: 'user',
            status: 'online',
            lastMessage: '大家今天的运动打卡情况如何？',
            lastMessageTime: '30分钟前',
            unreadCount: 5,
            specialty: '健康交流群',
          },
          {
            id: 'user2',
            name: '陈晓明',
            type: 'user',
            status: 'away',
            lastMessage: '谢谢你的健康建议！',
            lastMessageTime: '1小时前',
            unreadCount: 0,
            specialty: '健康伙伴',
          },
        ],
      },
      {
        id: 'suppliers',
        title: '健康服务',
        icon: '🏪',
        contacts: [
          {
            id: 'supplier1',
            name: '索克健康商城',
            type: 'supplier',
            status: 'online',
            lastMessage: '您关注的产品有新优惠！',
            lastMessageTime: '3小时前',
            unreadCount: 1,
            specialty: '健康产品·官方商城',
            verified: true,
          },
          {
            id: 'supplier2',
            name: '中医养生馆',
            type: 'supplier',
            status: 'online',
            lastMessage: '本周养生课程安排已更新',
            lastMessageTime: '6小时前',
            unreadCount: 0,
            specialty: '养生服务·线下体验',
            verified: true,
          },
        ],
      },
      {
        id: 'services',
        title: '系统服务',
        icon: '⚙️',
        contacts: [
          {
            id: 'service1',
            name: '健康报告',
            type: 'service',
            status: 'online',
            lastMessage: '您的月度健康报告已生成',
            lastMessageTime: '今天',
            unreadCount: 1,
            specialty: '数据分析·健康报告',
          },
          {
            id: 'service2',
            name: '预约提醒',
            type: 'service',
            status: 'online',
            lastMessage: '明天下午2点的复诊提醒',
            lastMessageTime: '今天',
            unreadCount: 0,
            specialty: '智能提醒·预约管理',
          },
        ],
      },
    ];

    setContactGroups(groups);
  }, []);

  // 搜索联系人
  const searchContacts = useCallback((text: string) => {
    if (!text.trim()) {
      setFilteredContacts([]);
      return;
    }

    const allContacts = contactGroups.flatMap(group => group.contacts);
    const filtered = allContacts.filter(contact =>
      contact.name.toLowerCase().includes(text.toLowerCase()) ||
      contact.specialty?.toLowerCase().includes(text.toLowerCase())
    );
    setFilteredContacts(filtered);
  }, [contactGroups]);

  // 刷新联系人列表
  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    try {
      // 模拟网络请求
      await new Promise(resolve => setTimeout(resolve, 1000));
      initializeContacts();
    } catch (error) {
      Alert.alert('刷新失败', '请检查网络连接后重试');
    } finally {
      setRefreshing(false);
    }
  }, [initializeContacts]);

  // 切换分组折叠状态
  const toggleGroupCollapse = useCallback((groupId: string) => {
    setContactGroups(prev =>
      prev.map(group =>
        group.id === groupId
          ? { ...group, collapsed: !group.collapsed }
          : group
      )
    );
  }, []);

  // 处理联系人点击
  const handleContactPress = useCallback((contact: Contact) => {
    // TODO: 导航到聊天界面
    Alert.alert('开始聊天', `即将与 ${contact.name} 开始对话`);
  }, []);

  // 获取状态指示器颜色
  const getStatusColor = (status: Contact['status']) => {
    switch (status) {
      case 'online': return colors.success;
      case 'busy': return colors.warning;
      case 'away': return colors.gray400;
      case 'offline': return colors.gray300;
      default: return colors.gray300;
    }
  };

  // 获取联系人类型图标
  const getContactTypeIcon = (type: Contact['type']) => {
    switch (type) {
      case 'agent': return '🤖';
      case 'doctor': return '👨‍⚕️';
      case 'user': return '👤';
      case 'supplier': return '🏪';
      case 'service': return '⚙️';
      default: return '👤';
    }
  };

  // 渲染联系人项
  const renderContactItem = ({ item: contact }: { item: Contact }) => (
    <TouchableOpacity
      style={styles.contactItem}
      onPress={() => handleContactPress(contact)}
      activeOpacity={0.7}
    >
      <View style={styles.contactAvatar}>
        <View style={styles.avatarContainer}>
          <Text style={styles.avatarText}>
            {getContactTypeIcon(contact.type)}
          </Text>
          {contact.verified && (
            <View style={styles.verifiedBadge}>
              <Text style={styles.verifiedIcon}>✓</Text>
            </View>
          )}
        </View>
        <View style={[styles.statusIndicator, { backgroundColor: getStatusColor(contact.status) }]} />
      </View>

      <View style={styles.contactInfo}>
        <View style={styles.contactHeader}>
          <Text style={styles.contactName}>{contact.name}</Text>
          <View style={styles.contactMeta}>
            {contact.vip && (
              <View style={styles.vipBadge}>
                <Text style={styles.vipText}>VIP</Text>
              </View>
            )}
            {contact.lastMessageTime && (
              <Text style={styles.messageTime}>{contact.lastMessageTime}</Text>
            )}
          </View>
        </View>

        <View style={styles.contactDetails}>
          <Text style={styles.specialty} numberOfLines={1}>
            {contact.specialty}
          </Text>
          {contact.lastMessage && (
            <Text style={styles.lastMessage} numberOfLines={1}>
              {contact.lastMessage}
            </Text>
          )}
        </View>
      </View>

      {contact.unreadCount && contact.unreadCount > 0 && (
        <View style={styles.unreadBadge}>
          <Text style={styles.unreadText}>
            {contact.unreadCount > 99 ? '99+' : contact.unreadCount}
          </Text>
        </View>
      )}
    </TouchableOpacity>
  );

  // 渲染分组
  const renderContactGroup = (group: ContactGroup) => (
    <View key={group.id} style={styles.groupContainer}>
      <TouchableOpacity
        style={styles.groupHeader}
        onPress={() => toggleGroupCollapse(group.id)}
        activeOpacity={0.7}
      >
        <View style={styles.groupTitleContainer}>
          <Text style={styles.groupIcon}>{group.icon}</Text>
          <Text style={styles.groupTitle}>{group.title}</Text>
          <Text style={styles.groupCount}>({group.contacts.length})</Text>
        </View>
        <Text style={[styles.collapseIcon, group.collapsed && styles.collapseIconRotated]}>
          ▼
        </Text>
      </TouchableOpacity>

      {!group.collapsed && (
        <View style={styles.groupContent}>
          {group.contacts.map((contact, index) => (
            <View key={contact.id}>
              {renderContactItem({ item: contact })}
              {index < group.contacts.length - 1 && <Divider style={styles.contactDivider} />}
            </View>
          ))}
        </View>
      )}
    </View>
  );

  useEffect(() => {
    initializeContacts();
  }, [initializeContacts]);

  useEffect(() => {
    searchContacts(searchText);
  }, [searchText, searchContacts]);

  return (
    <SafeAreaView style={styles.container}>
      {/* 头部搜索栏 */}
      <View style={styles.header}>
        <View style={styles.searchContainer}>
          <Text style={styles.searchIcon}>🔍</Text>
          <TextInput
            style={styles.searchInput}
            placeholder="搜索联系人、专业、服务..."
            placeholderTextColor={colors.textSecondary}
            value={searchText}
            onChangeText={setSearchText}
            returnKeyType="search"
          />
          {searchText.length > 0 && (
            <TouchableOpacity
              style={styles.clearButton}
              onPress={() => setSearchText('')}
            >
              <Text style={styles.clearIcon}>✕</Text>
            </TouchableOpacity>
          )}
        </View>
      </View>

      {/* 联系人列表 */}
      <ScrollView
        style={styles.content}
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            tintColor={colors.primary}
            colors={[colors.primary]}
          />
        }
      >
        {searchText.length > 0 ? (
          // 搜索结果
          <View style={styles.searchResults}>
            <Text style={styles.searchResultsTitle}>
              搜索结果 ({filteredContacts.length})
            </Text>
            {filteredContacts.length > 0 ? (
              filteredContacts.map((contact, index) => (
                <View key={contact.id}>
                  {renderContactItem({ item: contact })}
                  {index < filteredContacts.length - 1 && <Divider style={styles.contactDivider} />}
                </View>
              ))
            ) : (
              <View style={styles.emptyState}>
                <Text style={styles.emptyIcon}>🔍</Text>
                <Text style={styles.emptyTitle}>未找到相关联系人</Text>
                <Text style={styles.emptyDescription}>
                  尝试使用其他关键词搜索
                </Text>
              </View>
            )}
          </View>
        ) : (
          // 分组联系人列表
          <View style={styles.groupsList}>
            {contactGroups.map(renderContactGroup)}
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },

  // 头部搜索栏
  header: {
    backgroundColor: colors.surface,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.gray100,
    borderRadius: borderRadius.lg,
    paddingHorizontal: spacing.md,
    height: 40,
  },
  searchIcon: {
    fontSize: typography.fontSize.base,
    marginRight: spacing.sm,
  },
  searchInput: {
    flex: 1,
    fontSize: typography.fontSize.base,
    color: colors.textPrimary,
    fontFamily: typography.fontFamily.regular,
  },
  clearButton: {
    padding: spacing.xs,
  },
  clearIcon: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
  },

  // 内容区域
  content: {
    flex: 1,
  },

  // 分组样式
  groupsList: {
    paddingVertical: spacing.sm,
  },
  groupContainer: {
    marginBottom: spacing.sm,
  },
  groupHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    backgroundColor: colors.surfaceSecondary,
  },
  groupTitleContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  groupIcon: {
    fontSize: typography.fontSize.lg,
    marginRight: spacing.sm,
  },
  groupTitle: {
    fontSize: typography.fontSize.base,
    fontWeight: typography.fontWeight.medium,
    color: colors.textPrimary,
    fontFamily: typography.fontFamily.medium,
  },
  groupCount: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    marginLeft: spacing.xs,
    fontFamily: typography.fontFamily.regular,
  },
  collapseIcon: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    transform: [{ rotate: '0deg' }],
  },
  collapseIconRotated: {
    transform: [{ rotate: '-90deg' }],
  },
  groupContent: {
    backgroundColor: colors.surface,
  },

  // 联系人项样式
  contactItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    backgroundColor: colors.surface,
  },
  contactAvatar: {
    position: 'relative',
    marginRight: spacing.md,
  },
  avatarContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: colors.gray100,
    justifyContent: 'center',
    alignItems: 'center',
    position: 'relative',
  },
  avatarText: {
    fontSize: typography.fontSize.xl,
  },
  verifiedBadge: {
    position: 'absolute',
    bottom: -2,
    right: -2,
    width: 16,
    height: 16,
    borderRadius: 8,
    backgroundColor: colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: colors.surface,
  },
  verifiedIcon: {
    fontSize: 8,
    color: colors.white,
    fontWeight: typography.fontWeight.bold,
  },
  statusIndicator: {
    position: 'absolute',
    top: 2,
    right: 2,
    width: 12,
    height: 12,
    borderRadius: 6,
    borderWidth: 2,
    borderColor: colors.surface,
  },

  // 联系人信息
  contactInfo: {
    flex: 1,
  },
  contactHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: spacing.xs,
  },
  contactName: {
    fontSize: typography.fontSize.base,
    fontWeight: typography.fontWeight.medium,
    color: colors.textPrimary,
    fontFamily: typography.fontFamily.medium,
  },
  contactMeta: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  vipBadge: {
    backgroundColor: colors.warning,
    paddingHorizontal: spacing.xs,
    paddingVertical: 2,
    borderRadius: borderRadius.sm,
    marginRight: spacing.xs,
  },
  vipText: {
    fontSize: 10,
    color: colors.white,
    fontWeight: typography.fontWeight.bold,
  },
  messageTime: {
    fontSize: typography.fontSize.xs,
    color: colors.textSecondary,
    fontFamily: typography.fontFamily.regular,
  },
  contactDetails: {
    gap: spacing.xs,
  },
  specialty: {
    fontSize: typography.fontSize.sm,
    color: colors.primary,
    fontFamily: typography.fontFamily.regular,
  },
  lastMessage: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    fontFamily: typography.fontFamily.regular,
  },

  // 未读消息徽章
  unreadBadge: {
    backgroundColor: colors.error,
    minWidth: 20,
    height: 20,
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: spacing.xs,
  },
  unreadText: {
    fontSize: typography.fontSize.xs,
    color: colors.white,
    fontWeight: typography.fontWeight.bold,
  },

  // 分割线
  contactDivider: {
    marginLeft: spacing.lg + 48 + spacing.md, // 对齐联系人信息
  },

  // 搜索结果
  searchResults: {
    padding: spacing.lg,
  },
  searchResultsTitle: {
    fontSize: typography.fontSize.lg,
    fontWeight: typography.fontWeight.medium,
    color: colors.textPrimary,
    marginBottom: spacing.md,
    fontFamily: typography.fontFamily.medium,
  },

  // 空状态
  emptyState: {
    alignItems: 'center',
    paddingVertical: spacing['2xl'],
  },
  emptyIcon: {
    fontSize: typography.fontSize['4xl'],
    marginBottom: spacing.md,
  },
  emptyTitle: {
    fontSize: typography.fontSize.lg,
    fontWeight: typography.fontWeight.medium,
    color: colors.textPrimary,
    marginBottom: spacing.sm,
    fontFamily: typography.fontFamily.medium,
  },
  emptyDescription: {
    fontSize: typography.fontSize.base,
    color: colors.textSecondary,
    textAlign: 'center',
    fontFamily: typography.fontFamily.regular,
  },
});

export default HomeScreen; 