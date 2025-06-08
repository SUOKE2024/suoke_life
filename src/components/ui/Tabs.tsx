import React, { useRef, useState } from 'react';
import {
    Animated,
    ScrollView,
    StyleSheet,
    Text,
    TextStyle,
    TouchableOpacity,
    View,
    ViewStyle,
} from 'react-native';
import { useTheme } from '../../contexts/ThemeContext';

export interface TabItem {
  key: string;
  title: string;
  content: React.ReactNode;
  disabled?: boolean;
  badge?: string | number;
}

export interface TabsProps {
  items: TabItem[];
  activeKey?: string;
  defaultActiveKey?: string;
  onChange?: (key: string) => void;
  type?: 'line' | 'card' | 'button';
  position?: 'top' | 'bottom';
  scrollable?: boolean;
  animated?: boolean;
  style?: ViewStyle;
  tabBarStyle?: ViewStyle;
  tabStyle?: ViewStyle;
  activeTabStyle?: ViewStyle;
  tabTextStyle?: TextStyle;
  activeTabTextStyle?: TextStyle;
  contentStyle?: ViewStyle;
  accessible?: boolean;
  testID?: string;
}

export const Tabs: React.FC<TabsProps> = ({
  items,
  activeKey: controlledActiveKey,
  defaultActiveKey,
  onChange,
  type = 'line',
  position = 'top',
  scrollable = false,
  animated = true,
  style,
  tabBarStyle,
  tabStyle,
  activeTabStyle,
  tabTextStyle,
  activeTabTextStyle,
  contentStyle,
  accessible = true,
  testID,
}) => {
  const { currentTheme } = useTheme();
  const [internalActiveKey, setInternalActiveKey] = useState(
    defaultActiveKey || items[0]?.key || ''
  );
  
  const activeKey = controlledActiveKey !== undefined ? controlledActiveKey : internalActiveKey;
  const indicatorAnim = useRef(new Animated.Value(0)).current;
  const contentAnim = useRef(new Animated.Value(0)).current;

  const handleTabPress = (key: string, index: number) => {
    const item = items.find(item => item.key === key);
    if (item?.disabled) return;

    if (controlledActiveKey === undefined) {
      setInternalActiveKey(key);
    }
    onChange?.(key);

    if (animated) {
      Animated.parallel([
        Animated.spring(indicatorAnim, {
          toValue: index,
          useNativeDriver: true,
        }),
        Animated.timing(contentAnim, {
          toValue: index,
          duration: 200,
          useNativeDriver: true,
        }),
      ]).start();
    }
  };

  const activeIndex = items.findIndex(item => item.key === activeKey);
  const activeItem = items[activeIndex];

  const getTabBarStyles = () => {
    const baseStyle = {
      flexDirection: 'row' as const,
      backgroundColor: currentTheme.colors.surface,
    };

    switch (type) {
      case 'card':
        return {
          ...baseStyle,
          backgroundColor: currentTheme.colors.surfaceVariant,
          borderRadius: 8,
          padding: 4,
        };
      case 'button':
        return {
          ...baseStyle,
          backgroundColor: 'transparent',
        };
      default:
        return {
          ...baseStyle,
          borderBottomWidth: 1,
          borderBottomColor: currentTheme.colors.outline,
        };
    }
  };

  const getTabStyles = (isActive: boolean, isDisabled: boolean) => {
    const baseStyle = {
      paddingHorizontal: 16,
      paddingVertical: 12,
      alignItems: 'center' as const,
      justifyContent: 'center' as const,
      flex: scrollable ? 0 : 1,
      minWidth: scrollable ? 80 : undefined,
    };

    if (isDisabled) {
      return {
        ...baseStyle,
        opacity: 0.5,
      };
    }

    switch (type) {
      case 'card':
        return {
          ...baseStyle,
          backgroundColor: isActive ? currentTheme.colors.primary : 'transparent',
          borderRadius: 6,
          marginHorizontal: 2,
        };
      case 'button':
        return {
          ...baseStyle,
          backgroundColor: isActive ? currentTheme.colors.primary : currentTheme.colors.surfaceVariant,
          borderRadius: 8,
          marginHorizontal: 4,
        };
      default:
        return {
          ...baseStyle,
          borderBottomWidth: isActive ? 2 : 0,
          borderBottomColor: isActive ? currentTheme.colors.primary : 'transparent',
        };
    }
  };

  const getTabTextStyles = (isActive: boolean, isDisabled: boolean) => {
    const baseStyle = {
      fontSize: 16,
      fontWeight: isActive ? '600' as const : '400' as const,
    };

    if (isDisabled) {
      return {
        ...baseStyle,
        color: currentTheme.colors.onSurfaceVariant,
      };
    }

    switch (type) {
      case 'card':
      case 'button':
        return {
          ...baseStyle,
          color: isActive ? currentTheme.colors.onPrimary : currentTheme.colors.onSurface,
        };
      default:
        return {
          ...baseStyle,
          color: isActive ? currentTheme.colors.primary : currentTheme.colors.onSurface,
        };
    }
  };

  const renderTabBar = () => {
    const TabBarContainer = scrollable ? ScrollView : View;
    const containerProps = scrollable 
      ? { horizontal: true, showsHorizontalScrollIndicator: false }
      : {};

    return (
      <TabBarContainer
        style={[getTabBarStyles(), tabBarStyle]}
        {...containerProps}
      >
        {items.map((item, index) => {
          const isActive = item.key === activeKey;
          const isDisabled = item.disabled || false;

          return (
            <TouchableOpacity
              key={item.key}
              style={[
                getTabStyles(isActive, isDisabled),
                tabStyle,
                isActive && activeTabStyle,
              ]}
              onPress={() => handleTabPress(item.key, index)}
              disabled={isDisabled}
              accessible={accessible}
              accessibilityRole="tab"
              accessibilityLabel={item.title}
              accessibilityState={{ selected: isActive, disabled: isDisabled }}
            >
              <View style={{ flexDirection: 'row', alignItems: 'center' }}>
                <Text
                  style={[
                    getTabTextStyles(isActive, isDisabled),
                    tabTextStyle,
                    isActive && activeTabTextStyle,
                  ]}
                >
                  {item.title}
                </Text>
                {item.badge && (
                  <View style={styles.badge}>
                    <Text style={styles.badgeText}>{item.badge}</Text>
                  </View>
                )}
              </View>
            </TouchableOpacity>
          );
        })}
      </TabBarContainer>
    );
  };

  const renderContent = () => {
    if (!activeItem) return null;

    return (
      <View style={[styles.content, contentStyle]}>
        {activeItem.content}
      </View>
    );
  };

  const styles = StyleSheet.create({
    container: {
      flex: 1,
    },
    content: {
      flex: 1,
      padding: 16,
    },
    badge: {
      backgroundColor: currentTheme.colors.error,
      borderRadius: 10,
      paddingHorizontal: 6,
      paddingVertical: 2,
      marginLeft: 8,
      minWidth: 20,
      alignItems: 'center',
    },
    badgeText: {
      color: '#ffffff',
      fontSize: 12,
      fontWeight: '600',
    },
  });

  return (
    <View style={[styles.container, style]} testID={testID}>
      {position === 'top' && renderTabBar()}
      {renderContent()}
      {position === 'bottom' && renderTabBar()}
    </View>
  );
};

// TabPane 组件（用于更简洁的API）
export interface TabPaneProps {
  tab: string;
  key: string;
  disabled?: boolean;
  badge?: string | number;
  children: React.ReactNode;
}

export const TabPane: React.FC<TabPaneProps> = ({ children }) => {
  return <>{children}</>;
};

// 高级Tabs组件，支持TabPane子组件
export interface AdvancedTabsProps extends Omit<TabsProps, 'items'> {
  children: React.ReactElement<TabPaneProps>[];
}

export const AdvancedTabs: React.FC<AdvancedTabsProps> = ({
  children,
  ...props
}) => {
  const items: TabItem[] = React.Children.map(children, (child) => {
    if (React.isValidElement(child) && child.type === TabPane) {
      return {
        key: child.props.key || '',
        title: child.props.tab,
        content: child.props.children,
        disabled: child.props.disabled,
        badge: child.props.badge,
      };
    }
    return null;
  }).filter(Boolean) as TabItem[];

  return <Tabs {...props} items={items} />;
};

export default Tabs; 