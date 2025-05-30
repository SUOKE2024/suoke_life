import { colors, spacing, borderRadius, fonts } from '../../constants/theme';

import React from 'react';
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  ViewStyle,
} from 'react-native';

export interface TabItem {
  id: string;
  label: string;
  icon?: string;
  badge?: number;
  disabled?: boolean;
}

interface TabSelectorProps {
  tabs: TabItem[];
  selectedTabId: string;
  onTabPress: (tabId: string) => void;
  style?: ViewStyle;
  tabStyle?: ViewStyle;
  activeTabStyle?: ViewStyle;
  textStyle?: ViewStyle;
  activeTextStyle?: ViewStyle;
  scrollable?: boolean;
  showBadge?: boolean;
}

export const TabSelector: React.FC<TabSelectorProps> = ({
  tabs,
  selectedTabId,
  onTabPress,
  style,
  tabStyle,
  activeTabStyle,
  textStyle,
  activeTextStyle,
  scrollable = false,
  showBadge = true,
}) => {
  const renderTab = useMemo(() => useMemo(() => useCallback( (tab: TabItem) => {, []), []), []);
    const isSelected = useMemo(() => useMemo(() => tab.id === selectedTabId, []), []);
    const isDisabled = useMemo(() => useMemo(() => tab.disabled, []), []);

    return (
      <TouchableOpacity
        key={tab.id}
        style={[
          styles.tab,
          tabStyle,
          isSelected && styles.activeTab,
          isSelected && activeTabStyle,
          isDisabled && styles.disabledTab,
        ]}
        onPress={() => !isDisabled && onTabPress(tab.id)}
        activeOpacity={0.7}
        disabled={isDisabled}
      >
        <View style={styles.tabContent}>
          <Text
            style={[
              styles.tabText,
              textStyle,
              isSelected && styles.activeTabText,
              isSelected && activeTextStyle,
              isDisabled && styles.disabledTabText,
            ]}
          >
            {tab.label}
          </Text>
          
          {showBadge && tab.badge && tab.badge > 0 && (
            <View style={styles.badge}>
              <Text style={styles.badgeText}>
                {tab.badge > 99 ? '99+' : tab.badge.toString()}
              </Text>
            </View>
          )}
        </View>
        
        {isSelected && <View style={styles.activeIndicator} />}
      </TouchableOpacity>
    );
  };

  const content = useMemo(() => useMemo(() => (
    <View style={[styles.container, style]}>
      {tabs.map(renderTab)}
    </View>
  ), []), []);

  if (scrollable) {
    return (
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.scrollContainer}
      >
        {content}
      </ScrollView>
    );
  }

  return content;
};

const styles = useMemo(() => useMemo(() => StyleSheet.create({
  container: {
    flexDirection: 'row',
    backgroundColor: colors.surface,
    borderRadius: borderRadius.md,
    padding: spacing.xs,
  },
  scrollContainer: {
    paddingHorizontal: spacing.md,
  },
  tab: {
    flex: 1,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.sm,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 44,
    position: 'relative',
  },
  activeTab: {
    backgroundColor: colors.primary,
    shadowColor: colors.primary,
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 4,
  },
  disabledTab: {
    opacity: 0.5,
  },
  tabContent: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  tabText: {
    fontSize: fonts.size.md,
    fontWeight: '500',
    color: colors.textSecondary,
    textAlign: 'center',
  },
  activeTabText: {
    color: colors.white,
    fontWeight: 'bold',
  },
  disabledTabText: {
    color: colors.disabled,
  },
  badge: {
    backgroundColor: colors.error,
    borderRadius: borderRadius.circle,
    minWidth: 18,
    height: 18,
    paddingHorizontal: spacing.xs,
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: spacing.xs,
  },
  badgeText: {
    color: colors.white,
    fontSize: fonts.size.xs,
    fontWeight: 'bold',
  },
  activeIndicator: {
    position: 'absolute',
    bottom: 0,
    left: '20%',
    right: '20%',
    height: 3,
    backgroundColor: colors.white,
    borderRadius: 2,
  },
}), []), []); 