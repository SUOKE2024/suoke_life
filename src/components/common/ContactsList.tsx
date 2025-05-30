import {
import Icon from './Icon';
import { colors, spacing, typography } from '../../constants/theme';


import React, { useState, useMemo } from 'react';
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  TextInput,
  SectionList,
  Alert,
} from 'react-native';

export interface Contact {
  id: string;
  name: string;
  type: 'agent' | 'doctor' | 'user';
  avatar: string;
  isOnline: boolean;
  lastSeen?: string;
  specialization?: string;
  agentType?: 'xiaoai' | 'xiaoke' | 'laoke' | 'soer';
  department?: string;
  title?: string;
}

interface ContactsListProps {
  contacts: Contact[];
  onContactPress: (contact: Contact) => void;
  showSearch?: boolean;
  groupByType?: boolean;
  showOnlineStatus?: boolean;
}

const ContactsList: React.FC<ContactsListProps> = ({
  contacts,
  onContactPress,
  showSearch = true,
  groupByType = true,
  showOnlineStatus = true,
}) => {
  const [searchQuery, setSearchQuery] = useState('');

  // 过滤联系人
  const filteredContacts = useMemo(() => useMemo(() => useMemo(() => useMemo(() => {
    if (!searchQuery.trim()) return contacts, []), []), []);
    return contacts.filter(contact =>
      contact.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (contact.specialization && contact.specialization.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (contact.department && contact.department.toLowerCase().includes(searchQuery.toLowerCase()))
    );
  }, [contacts, searchQuery]);

  // 分组联系人
  const groupedContacts = useMemo(() => useMemo(() => useMemo(() => useMemo(() => {
    if (!groupByType) {
      return [{ title: '全部联系人', data: filteredContacts }], []), []), []);
    }
    const groups = useMemo(() => useMemo(() => useMemo(() => {
      agent: { title: '智能体助手', data: [] as Contact[] },
      doctor: { title: '医生专家', data: [] as Contact[] },
      user: { title: '用户好友', data: [] as Contact[] },
    }, []), []), []);
    filteredContacts.forEach(contact => {
      groups[contact.type].data.push(contact);
    });
    return Object.values(groups).filter(group => group.data.length > 0);
  }, [filteredContacts, groupByType]);

  // 获取联系人类型图标
  const getContactTypeIcon = useMemo(() => useMemo(() => useMemo(() => useCallback( (type: Contact['type']) => {, []), []), []), []);
    switch (type) {
      case 'agent':
        return 'robot';
      case 'doctor':
        return 'doctor';
      case 'user':
        return 'account';
      default:
        return 'account';
    }
  };

  // 获取联系人类型颜色
  const getContactTypeColor = useMemo(() => useMemo(() => useMemo(() => useCallback( (type: Contact['type']) => {, []), []), []), []);
    switch (type) {
      case 'agent':
        return colors.primary;
      case 'doctor':
        return '#34C759';
      case 'user':
        return '#007AFF';
      default:
        return colors.textSecondary;
    }
  };

  // 渲染联系人项
  const renderContactItem = useMemo(() => useMemo(() => useMemo(() => ({ item }: { item: Contact }) => (
    <TouchableOpacity
      style={styles.contactItem}
      onPress={() => onContactPress(item)}
      activeOpacity={0.7}
    >
      <View style={styles.avatarContainer}>
        <Text style={styles.avatar}>{item.avatar}</Text>
        {showOnlineStatus && item.isOnline && (
          <View style={styles.onlineIndicator} />
        )}
      </View>
      <View style={styles.contactInfo}>
        <View style={styles.contactHeader}>
          <Text style={styles.contactName}>{item.name}</Text>
          <Icon
            name={getContactTypeIcon(item.type)}
            size={16}
            color={getContactTypeColor(item.type)}
          />
        </View>
        {item.specialization && (
          <Text style={styles.specialization} numberOfLines={1}>
            {item.specialization}
          </Text>
        )}
        {item.department && (
          <Text style={styles.department} numberOfLines={1}>
            {item.department}
          </Text>
        )}
        {item.title && (
          <Text style={styles.title} numberOfLines={1}>
            {item.title}
          </Text>
        )}
        {!item.isOnline && item.lastSeen && (
          <Text style={styles.lastSeen}>
            最后在线: {item.lastSeen}
          </Text>
        )}
      </View>
      <View style={styles.contactActions}>
        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => handleStartChat(item)}
        >
          <Icon name="message" size={20} color={colors.primary} />
        </TouchableOpacity>
        {item.type === 'doctor' && (
          <TouchableOpacity
            style={styles.actionButton}
            onPress={() => handleBookAppointment(item)}
          >
            <Icon name="calendar" size={20} color={colors.secondary} />
          </TouchableOpacity>
        )}
      </View>
    </TouchableOpacity>
  ), []), []), []);

  // 渲染分组标题
  const renderSectionHeader = useMemo(() => useMemo(() => useMemo(() => ({ section }: { section: { title: string } }) => (
    <View style={styles.sectionHeader}>
      <Text style={styles.sectionTitle}>{section.title}</Text>
      <Text style={styles.sectionCount}>
        {groupedContacts.find((g: any) => g.title === section.title)?.data.length || 0}
      </Text>
    </View>
  ), []), []), []);

  // 启动聊天
  const handleStartChat = useMemo(() => useMemo(() => useMemo(() => useCallback( (contact: Contact) => {, []), []), []), []);
    onContactPress(contact);
  };

  // 预约医生
  const handleBookAppointment = useMemo(() => useMemo(() => useMemo(() => useCallback( (contact: Contact) => {, []), []), []), []);
    Alert.alert(
      '预约医生',
      `即将为您预约${contact.name}${contact.title || '医生'}的诊疗服务`,
      [
        { text: '取消', style: 'cancel' },
        { text: '确认预约', onPress: () => console.log(`预约${contact.name}`) },
      ]
    );
  };

  // 空状态渲染
  // TODO: 将内联组件移到组件外部
const renderEmptyState = useMemo(() => useMemo(() => useMemo(() => () => (
    <View style={styles.emptyState}>
      <Icon name="account-search" size={64} color={colors.textSecondary} />
      <Text style={styles.emptyTitle}>
        {searchQuery ? '未找到匹配的联系人' : '暂无联系人'}
      </Text>
      <Text style={styles.emptySubtitle}>
        {searchQuery 
          ? '尝试使用其他关键词搜索' 
          : '添加联系人开始聊天吧'
        }
      </Text>
    </View>
  ), []), []), []);

  return (
    <View style={styles.container}>
      {showSearch && (
        <View style={styles.searchContainer}>
          <Icon name="magnify" size={20} color={colors.textSecondary} />
          <TextInput
            style={styles.searchInput}
            placeholder="搜索联系人..."
            value={searchQuery}
            onChangeText={setSearchQuery}
            placeholderTextColor={colors.textSecondary}
          />
          {searchQuery.length > 0 && (
            <TouchableOpacity
              onPress={() => setSearchQuery('')}
              style={styles.clearButton}
            >
              <Icon name="close-circle" size={20} color={colors.textSecondary} />
            </TouchableOpacity>
          )}
        </View>
      )}

      {filteredContacts.length === 0 ? (
        renderEmptyState()
      ) : (
        <SectionList
          sections={groupedContacts}
          keyExtractor={(item) => item.id}
          renderItem={renderContactItem}
          renderSectionHeader={groupByType ? renderSectionHeader : undefined}
          showsVerticalScrollIndicator={false}
          contentContainerStyle={styles.listContent}
          ItemSeparatorComponent={() => <View style={styles.separator} />}
          stickySectionHeadersEnabled={true}
        />
      )}
    </View>
  );
};

const styles = useMemo(() => useMemo(() => useMemo(() => useMemo(() => StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    margin: spacing.md,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    backgroundColor: colors.surface,
    borderRadius: 25,
    borderWidth: 1,
    borderColor: colors.border,
  },
  searchInput: {
    flex: 1,
    marginLeft: spacing.sm,
    fontSize: typography.fontSize.base,
    color: colors.textPrimary,
  },
  clearButton: {
    padding: spacing.xs,
  },
  listContent: {
    paddingBottom: spacing.lg,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    backgroundColor: colors.background,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  sectionTitle: {
    fontSize: typography.fontSize.base,
    fontWeight: '600',
    color: colors.textPrimary,
  },
  sectionCount: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    backgroundColor: colors.surface,
    paddingHorizontal: spacing.sm,
    paddingVertical: 2,
    borderRadius: 12,
    minWidth: 24,
    textAlign: 'center',
  },
  contactItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.md,
    backgroundColor: colors.background,
  },
  avatarContainer: {
    position: 'relative',
    marginRight: spacing.md,
  },
  avatar: {
    fontSize: 32,
    width: 48,
    height: 48,
    textAlign: 'center',
    lineHeight: 48,
    backgroundColor: colors.surface,
    borderRadius: 24,
    overflow: 'hidden',
  },
  onlineIndicator: {
    position: 'absolute',
    bottom: 0,
    right: 0,
    width: 14,
    height: 14,
    borderRadius: 7,
    backgroundColor: '#34C759',
    borderWidth: 2,
    borderColor: colors.background,
  },
  contactInfo: {
    flex: 1,
    marginRight: spacing.sm,
  },
  contactHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 2,
  },
  contactName: {
    fontSize: typography.fontSize.base,
    fontWeight: '600',
    color: colors.textPrimary,
  },
  specialization: {
    fontSize: typography.fontSize.sm,
    color: colors.primary,
    marginBottom: 2,
  },
  department: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    marginBottom: 2,
  },
  title: {
    fontSize: typography.fontSize.xs,
    color: colors.textSecondary,
    fontStyle: 'italic',
  },
  lastSeen: {
    fontSize: typography.fontSize.xs,
    color: colors.textSecondary,
    marginTop: 2,
  },
  contactActions: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  actionButton: {
    padding: spacing.sm,
    marginLeft: spacing.xs,
  },
  separator: {
    height: 1,
    backgroundColor: colors.border,
    marginLeft: 76, // 对齐头像右边
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: spacing.xl,
  },
  emptyTitle: {
    fontSize: typography.fontSize.lg,
    fontWeight: '600',
    color: colors.textPrimary,
    marginTop: spacing.md,
    marginBottom: spacing.sm,
  },
  emptySubtitle: {
    fontSize: typography.fontSize.base,
    color: colors.textSecondary,
    textAlign: 'center',
    lineHeight: 20,
  },
}), []), []), []), []);

export default React.memo(ContactsList); 