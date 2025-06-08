import React, { useCallback, useEffect, useRef, useState } from 'react';
import {
    Animated,
    FlatList,
    Keyboard,
    StyleSheet,
    Text,
    TextInput,
    TouchableOpacity,
    View
} from 'react-native';
import { useTheme } from '../../contexts/ThemeContext';

export interface SearchBarProps {
  /** 搜索值 */
  value?: string;
  /** 搜索值变化回调 */
  onChangeText?: (text: string) => void;
  /** 搜索提交回调 */
  onSearch?: (text: string) => void;
  /** 占位符文本 */
  placeholder?: string;
  /** 是否显示取消按钮 */
  showCancel?: boolean;
  /** 取消按钮文本 */
  cancelText?: string;
  /** 取消回调 */
  onCancel?: () => void;
  /** 是否自动聚焦 */
  autoFocus?: boolean;
  /** 自定义样式 */
  style?: any;
  /** 输入框样式 */
  inputStyle?: any;
  /** 是否显示搜索历史 */
  showHistory?: boolean;
  /** 搜索历史数据 */
  historyData?: string[];
  /** 历史记录点击回调 */
  onHistoryPress?: (item: string) => void;
  /** 清除历史记录回调 */
  onClearHistory?: () => void;
  /** 是否显示搜索建议 */
  showSuggestions?: boolean;
  /** 搜索建议数据 */
  suggestions?: string[];
  /** 建议点击回调 */
  onSuggestionPress?: (item: string) => void;
  /** 是否正在加载 */
  loading?: boolean;
  /** 最大长度 */
  maxLength?: number;
  /** 是否禁用 */
  disabled?: boolean;
}

export const SearchBar: React.FC<SearchBarProps> = ({
  value = '',
  onChangeText,
  onSearch,
  placeholder = '搜索...',
  showCancel = true,
  cancelText = '取消',
  onCancel,
  autoFocus = false,
  style,
  inputStyle,
  showHistory = false,
  historyData = [],
  onHistoryPress,
  onClearHistory,
  showSuggestions = false,
  suggestions = [],
  onSuggestionPress,
  loading = false,
  maxLength,
  disabled = false,
}) => {
  const { currentTheme } = useTheme();
  const styles = createStyles(currentTheme);

  const [isFocused, setIsFocused] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const inputRef = useRef<TextInput>(null);
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const scaleAnim = useRef(new Animated.Value(0.95)).current;

  useEffect(() => {
    if (showDropdown) {
      Animated.parallel([
        Animated.timing(fadeAnim, {
          toValue: 1,
          duration: 200,
          useNativeDriver: true,
        }),
        Animated.spring(scaleAnim, {
          toValue: 1,
          tension: 100,
          friction: 8,
          useNativeDriver: true,
        }),
      ]).start();
    } else {
      Animated.parallel([
        Animated.timing(fadeAnim, {
          toValue: 0,
          duration: 150,
          useNativeDriver: true,
        }),
        Animated.timing(scaleAnim, {
          toValue: 0.95,
          duration: 150,
          useNativeDriver: true,
        }),
      ]).start();
    }
  }, [showDropdown, fadeAnim, scaleAnim]);

  const handleFocus = useCallback(() => {
    setIsFocused(true);
    if (showHistory || showSuggestions) {
      setShowDropdown(true);
    }
  }, [showHistory, showSuggestions]);

  const handleBlur = useCallback(() => {
    setIsFocused(false);
    // 延迟隐藏下拉框，以便处理点击事件
    setTimeout(() => {
      setShowDropdown(false);
    }, 200);
  }, []);

  const handleChangeText = useCallback((text: string) => {
    onChangeText?.(text);
    if (showSuggestions && text.length > 0) {
      setShowDropdown(true);
    } else if (showHistory && text.length === 0) {
      setShowDropdown(true);
    } else {
      setShowDropdown(false);
    }
  }, [onChangeText, showSuggestions, showHistory]);

  const handleSubmit = useCallback(() => {
    if (value.trim()) {
      onSearch?.(value.trim());
      setShowDropdown(false);
      Keyboard.dismiss();
    }
  }, [value, onSearch]);

  const handleCancel = useCallback(() => {
    onCancel?.();
    setShowDropdown(false);
    inputRef.current?.blur();
  }, [onCancel]);

  const handleClear = useCallback(() => {
    onChangeText?.('');
    inputRef.current?.focus();
  }, [onChangeText]);

  const handleHistoryPress = useCallback((item: string) => {
    onHistoryPress?.(item);
    setShowDropdown(false);
  }, [onHistoryPress]);

  const handleSuggestionPress = useCallback((item: string) => {
    onSuggestionPress?.(item);
    setShowDropdown(false);
  }, [onSuggestionPress]);

  const renderHistoryItem = ({ item }: { item: string }) => (
    <TouchableOpacity
      style={styles.dropdownItem}
      onPress={() => handleHistoryPress(item)}
    >
      <Text style={styles.historyIcon}>🕒</Text>
      <Text style={styles.dropdownItemText}>{item}</Text>
    </TouchableOpacity>
  );

  const renderSuggestionItem = ({ item }: { item: string }) => (
    <TouchableOpacity
      style={styles.dropdownItem}
      onPress={() => handleSuggestionPress(item)}
    >
      <Text style={styles.suggestionIcon}>🔍</Text>
      <Text style={styles.dropdownItemText}>{item}</Text>
    </TouchableOpacity>
  );

  const renderDropdown = () => {
    if (!showDropdown) return null;

    const data = showSuggestions && value.length > 0 ? suggestions : historyData;
    const renderItem = showSuggestions && value.length > 0 ? renderSuggestionItem : renderHistoryItem;

    return (
      <Animated.View
        style={[
          styles.dropdown,
          {
            opacity: fadeAnim,
            transform: [{ scale: scaleAnim }],
          },
        ]}
      >
        {data.length > 0 ? (
          <>
            <FlatList
              data={data}
              renderItem={renderItem}
              keyExtractor={(item, index) => `${item}-${index}`}
              style={styles.dropdownList}
              showsVerticalScrollIndicator={false}
              keyboardShouldPersistTaps="handled"
            />
            {showHistory && historyData.length > 0 && (
              <TouchableOpacity
                style={styles.clearHistoryButton}
                onPress={onClearHistory}
              >
                <Text style={styles.clearHistoryText}>清除搜索历史</Text>
              </TouchableOpacity>
            )}
          </>
        ) : (
          <View style={styles.emptyDropdown}>
            <Text style={styles.emptyText}>
              {showSuggestions ? '暂无搜索建议' : '暂无搜索历史'}
            </Text>
          </View>
        )}
      </Animated.View>
    );
  };

  return (
    <View style={[styles.container, style]}>
      <View style={[styles.searchContainer, isFocused && styles.searchContainerFocused]}>
        <Text style={styles.searchIcon}>🔍</Text>
        
        <TextInput
          ref={inputRef}
          style={[styles.input, inputStyle]}
          value={value}
          onChangeText={handleChangeText}
          onFocus={handleFocus}
          onBlur={handleBlur}
          onSubmitEditing={handleSubmit}
          placeholder={placeholder}
          placeholderTextColor={currentTheme.colors.onSurfaceVariant}
          autoFocus={autoFocus}
          maxLength={maxLength}
          editable={!disabled}
          returnKeyType="search"
        />

        {value.length > 0 && (
          <TouchableOpacity
            style={styles.clearButton}
            onPress={handleClear}
          >
            <Text style={styles.clearIcon}>✕</Text>
          </TouchableOpacity>
        )}
      </View>

      {showCancel && isFocused && (
        <TouchableOpacity
          style={styles.cancelButton}
          onPress={handleCancel}
        >
          <Text style={styles.cancelText}>{cancelText}</Text>
        </TouchableOpacity>
      )}

      {renderDropdown()}
    </View>
  );
};

const createStyles = (theme: any) => {
  return StyleSheet.create({
    container: {
      position: 'relative',
    },
    searchContainer: {
      flexDirection: 'row',
      alignItems: 'center',
      backgroundColor: theme.colors.surfaceVariant,
      borderRadius: theme.borderRadius.lg,
      paddingHorizontal: theme.spacing.md,
      paddingVertical: theme.spacing.sm,
      borderWidth: 1,
      borderColor: 'transparent',
    },
    searchContainerFocused: {
      borderColor: theme.colors.primary,
      backgroundColor: theme.colors.surface,
    },
    searchIcon: {
      fontSize: 16,
      marginRight: theme.spacing.sm,
      color: theme.colors.onSurfaceVariant,
    },
    input: {
      flex: 1,
      fontSize: theme.typography.fontSize.base,
      color: theme.colors.onSurface,
      paddingVertical: 0,
    },
    clearButton: {
      padding: theme.spacing.xs,
      marginLeft: theme.spacing.sm,
    },
    clearIcon: {
      fontSize: 14,
      color: theme.colors.onSurfaceVariant,
    },
    cancelButton: {
      marginLeft: theme.spacing.md,
      paddingVertical: theme.spacing.sm,
    },
    cancelText: {
      fontSize: theme.typography.fontSize.base,
      color: theme.colors.primary,
    },
    dropdown: {
      position: 'absolute',
      top: '100%',
      left: 0,
      right: 0,
      backgroundColor: theme.colors.surface,
      borderRadius: theme.borderRadius.md,
      marginTop: theme.spacing.xs,
      maxHeight: 200,
      shadowColor: '#000',
      shadowOffset: {
        width: 0,
        height: 2,
      },
      shadowOpacity: 0.1,
      shadowRadius: 8,
      elevation: 5,
      zIndex: 1000,
    },
    dropdownList: {
      maxHeight: 160,
    },
    dropdownItem: {
      flexDirection: 'row',
      alignItems: 'center',
      paddingHorizontal: theme.spacing.md,
      paddingVertical: theme.spacing.sm,
      borderBottomWidth: 1,
      borderBottomColor: theme.colors.outline,
    },
    historyIcon: {
      fontSize: 14,
      marginRight: theme.spacing.sm,
      color: theme.colors.onSurfaceVariant,
    },
    suggestionIcon: {
      fontSize: 14,
      marginRight: theme.spacing.sm,
      color: theme.colors.primary,
    },
    dropdownItemText: {
      flex: 1,
      fontSize: theme.typography.fontSize.base,
      color: theme.colors.onSurface,
    },
    clearHistoryButton: {
      padding: theme.spacing.md,
      alignItems: 'center',
      borderTopWidth: 1,
      borderTopColor: theme.colors.outline,
    },
    clearHistoryText: {
      fontSize: theme.typography.fontSize.sm,
      color: theme.colors.error,
    },
    emptyDropdown: {
      padding: theme.spacing.lg,
      alignItems: 'center',
    },
    emptyText: {
      fontSize: theme.typography.fontSize.sm,
      color: theme.colors.onSurfaceVariant,
    },
  });
};

export default SearchBar; 