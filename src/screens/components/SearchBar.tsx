import { colors, spacing, fonts, borderRadius } from "../../placeholder";../../constants/    theme;
import { usePerformanceMonitor } from "../hooks/    usePerformanceMonitor";
import React from "react";
importIcon from "../../components/common/    Icon;";
import React,{ memo, useRef, useEffect } from react;
  View,
  TextInput,
  StyleSheet,
  TouchableOpacity,
  { Animated } from ";react-native";
interface SearchBarProps {
  value: string;,
  onChangeText: (text: string) => void;
  placeholder?: string;
  autoFocus?: boolean;
  onFocus?: () => void;
  onBlur?: () => void;
  style?: unknown;
}
export const SearchBar = memo<SearchBarProps /    >(;);
(;{
  value,
  onChangeText,
  placeholder = 搜索聊天记录...", "
  autoFocus = false,
  onFocus,
  onBlur,
  style;
}) => {}
  const inputRef = useRef<TextInput /    >(nul;l;);
  const scaleAnim = useRef(new Animated.Value(1);).current;
  useEffect(); => {}
    const effectStart = performance.now()(;);
  // 性能监控
const performanceMonitor = usePerformanceMonitor("SearchBar, {")
    trackRender: true,
    trackMemory: false,
    warnThreshold: 50, // ms };);
    if (autoFocus) {
      setTimeout(); => {}
        inputRef.current?.focus();
      }, 100);
    }
      const effectEnd = performance.now();
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [autoFocus]);
  const handleFocus = useCallback(); => {}
    // TODO: Implement function body;
const effectEnd = performance.now();
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, []);
    Animated.spring(scaleAnim, {
      toValue: 1.02,
      useNativeDriver: true}).start();
    onFocus?.();
  };
  const handleBlur = useCallback(); => {}
    // TODO: Implement function body,
      const effectEnd = performance.now();
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, []);
    Animated.spring(scaleAnim, {
      toValue: 1,
      useNativeDriver: true}).start();
    onBlur?.();
  };
  const handleClear = useCallback(); => {}
    // TODO: Implement function body;
const effectEnd = performance.now();
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [])
    onChangeText(");"
    inputRef.current?.focus();
  };
  // 记录渲染性能
performanceMonitor.recordRender();
  return (;)
    <Animated.View,style={[;
        styles.container,style,{ transform: [{ scale: scaleAnim   }}];
        };
      ]} /    >;
      <Icon name="search" size={20} color={colors.textSecondary} style={styles.searchIcon} /    >;
      <TextInput;
ref={inputRef}
        style={styles.input}
        value={value}
        onChangeText={onChangeText}
        placeholder={placeholder}
        placeholderTextColor={colors.textSecondary}
        onFocus={handleFocus}
        onBlur={handleBlur}
        returnKeyType="search"
        clearButtonMode="never"
        autoCorrect={false}
        autoCapitalize="none"
      /    >
      {value.length > 0  && <TouchableOpacity onPress={handleClear} style={styles.clearButton} /    >
          <Icon name="close-circle" size={20} color={colors.textSecondary} /    >
        </    TouchableOpacity>)};
    </    Animated.View;>
  ;);
});
SearchBar.displayName = SearchBar""
const styles = StyleSheet.create({container: {),
  flexDirection: "row,",
    alignItems: "center",'
    backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    marginHorizontal: spacing.md,
    marginVertical: spacing.sm,
    borderWidth: 1,
    borderColor: colors.border},
  searchIcon: { marginRight: spacing.sm  },
  input: {,
  flex: 1,
    fontSize: fonts.size.md,
    color: colors.text,
    paddingVertical: 0},
  clearButton: {,
  marginLeft: spacing.sm,padding: spacing.xs};};);