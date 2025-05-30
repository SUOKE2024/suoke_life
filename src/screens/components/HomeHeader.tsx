import Icon from '../../components/common/Icon';
import { colors, spacing, fonts, shadows } from '../../constants/theme';



import React, { memo } from 'react';
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
} from 'react-native';

interface HomeHeaderProps {
  title: string;
  unreadCount?: number;
  onContactsPress: () => void;
  onAccessibilityPress: () => void;
  onNavigationTestPress: () => void;
}

export const HomeHeader = memo<HomeHeaderProps>(({
  title,
  unreadCount = 0,
  onContactsPress,
  onAccessibilityPress,
  onNavigationTestPress,
}) => {
  return (
    <View style={styles.container}>
      <View style={styles.titleContainer}>
        <Text style={styles.title}>{title}</Text>
        {unreadCount > 0 && (
          <View style={styles.unreadBadge}>
            <Text style={styles.unreadText}>
              {unreadCount > 99 ? '99+' : unreadCount}
            </Text>
          </View>
        )}
      </View>

      <View style={styles.actions}>
        <TouchableOpacity
          style={styles.actionButton}
          onPress={onNavigationTestPress}
          activeOpacity={0.7}
        >
          <Icon name="navigation" size={24} color={colors.text} />
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.actionButton}
          onPress={onAccessibilityPress}
          activeOpacity={0.7}
        >
          <Icon name="accessibility" size={24} color={colors.text} />
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.actionButton}
          onPress={onContactsPress}
          activeOpacity={0.7}
        >
          <Icon name="account-group" size={24} color={colors.text} />
        </TouchableOpacity>
      </View>
    </View>
  );
});

HomeHeader.displayName = 'HomeHeader';

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    backgroundColor: colors.background,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
    ...shadows.sm,
  },
  titleContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  title: {
    fontSize: fonts.size.header,
    fontWeight: 'bold',
    color: colors.text,
  },
  unreadBadge: {
    backgroundColor: colors.error,
    borderRadius: 10,
    minWidth: 20,
    height: 20,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: spacing.xs,
    marginLeft: spacing.sm,
  },
  unreadText: {
    color: colors.white,
    fontSize: fonts.size.xs,
    fontWeight: 'bold',
  },
  actions: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  actionButton: {
    padding: spacing.sm,
    marginLeft: spacing.xs,
    borderRadius: 20,
    backgroundColor: colors.surface,
    ...shadows.sm,
  },
}); 