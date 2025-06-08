import React, { useState } from 'react';
import {
    Modal,
    ScrollView,
    StyleSheet,
    Text,
    TextStyle,
    TouchableOpacity,
    View,
    ViewStyle,
} from 'react-native';
import { useTheme } from '../../contexts/ThemeContext';

export interface ColorPickerProps {
  value?: string;
  colors?: string[];
  onColorChange?: (color: string) => void;
  disabled?: boolean;
  placeholder?: string;
  style?: ViewStyle;
  textStyle?: TextStyle;
  accessible?: boolean;
  accessibilityLabel?: string;
  testID?: string;
}

const DEFAULT_COLORS = [
  '#FF0000', '#FF8000', '#FFFF00', '#80FF00', '#00FF00', '#00FF80',
  '#00FFFF', '#0080FF', '#0000FF', '#8000FF', '#FF00FF', '#FF0080',
  '#800000', '#804000', '#808000', '#408000', '#008000', '#008040',
  '#008080', '#004080', '#000080', '#400080', '#800080', '#800040',
  '#400000', '#402000', '#404000', '#204000', '#004000', '#004020',
  '#004040', '#002040', '#000040', '#200040', '#400040', '#400020',
  '#000000', '#404040', '#808080', '#C0C0C0', '#FFFFFF',
];

export const ColorPicker: React.FC<ColorPickerProps> = ({
  value,
  colors = DEFAULT_COLORS,
  onColorChange,
  disabled = false,
  placeholder = '选择颜色',
  style,
  textStyle,
  accessible = true,
  accessibilityLabel,
  testID,
}) => {
  const { currentTheme } = useTheme();
  const [isVisible, setIsVisible] = useState(false);

  const handleColorSelect = (color: string) => {
    onColorChange?.(color);
    setIsVisible(false);
  };

  const renderColorGrid = () => {
    const rows = [];
    const colsPerRow = 6;
    
    for (let i = 0; i < colors.length; i += colsPerRow) {
      const rowColors = colors.slice(i, i + colsPerRow);
      rows.push(
        <View key={i} style={styles.colorRow}>
          {rowColors.map((color, index) => (
            <TouchableOpacity
              key={color}
              style={[
                styles.colorItem,
                { backgroundColor: color },
                value === color && styles.selectedColor,
              ]}
              onPress={() => handleColorSelect(color)}
              accessible={accessible}
              accessibilityRole="button"
              accessibilityLabel={`选择颜色 ${color}`}
              accessibilityState={{ selected: value === color }}
            />
          ))}
        </View>
      );
    }
    
    return rows;
  };

  const styles = StyleSheet.create({
    container: {
      borderWidth: 1,
      borderColor: currentTheme.colors.outline,
      borderRadius: 8,
      paddingHorizontal: 12,
      paddingVertical: 16,
      backgroundColor: currentTheme.colors.surface,
      minHeight: 48,
      flexDirection: 'row',
      alignItems: 'center',
    },
    containerDisabled: {
      backgroundColor: currentTheme.colors.surfaceVariant,
      opacity: 0.6,
    },
    colorPreview: {
      width: 24,
      height: 24,
      borderRadius: 4,
      marginRight: 12,
      borderWidth: 1,
      borderColor: currentTheme.colors.outline,
    },
    text: {
      fontSize: 16,
      color: currentTheme.colors.onSurface,
      flex: 1,
      ...textStyle,
    },
    placeholder: {
      fontSize: 16,
      color: currentTheme.colors.onSurfaceVariant,
      flex: 1,
    },
    modal: {
      flex: 1,
      backgroundColor: 'rgba(0, 0, 0, 0.5)',
      justifyContent: 'center',
      alignItems: 'center',
    },
    modalContent: {
      backgroundColor: currentTheme.colors.surface,
      borderRadius: 16,
      padding: 20,
      maxWidth: '90%',
      maxHeight: '80%',
    },
    modalHeader: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginBottom: 20,
    },
    modalTitle: {
      fontSize: 18,
      fontWeight: '600',
      color: currentTheme.colors.onSurface,
    },
    closeButton: {
      padding: 8,
    },
    closeButtonText: {
      fontSize: 16,
      color: currentTheme.colors.primary,
    },
    colorGrid: {
      alignItems: 'center',
    },
    colorRow: {
      flexDirection: 'row',
      marginBottom: 8,
    },
    colorItem: {
      width: 40,
      height: 40,
      borderRadius: 8,
      marginHorizontal: 4,
      borderWidth: 2,
      borderColor: 'transparent',
    },
    selectedColor: {
      borderColor: currentTheme.colors.primary,
      borderWidth: 3,
    },
    customColorSection: {
      marginTop: 20,
      paddingTop: 20,
      borderTopWidth: 1,
      borderTopColor: currentTheme.colors.outline,
    },
    customColorTitle: {
      fontSize: 16,
      fontWeight: '500',
      color: currentTheme.colors.onSurface,
      marginBottom: 12,
    },
    hexInput: {
      borderWidth: 1,
      borderColor: currentTheme.colors.outline,
      borderRadius: 8,
      paddingHorizontal: 12,
      paddingVertical: 8,
      fontSize: 16,
      color: currentTheme.colors.onSurface,
      backgroundColor: currentTheme.colors.surface,
    },
  });

  return (
    <>
      <TouchableOpacity
        style={[
          styles.container,
          disabled && styles.containerDisabled,
          style,
        ]}
        onPress={() => !disabled && setIsVisible(true)}
        disabled={disabled}
        accessible={accessible}
        accessibilityRole="button"
        accessibilityLabel={accessibilityLabel || `颜色选择器，当前值：${value || placeholder}`}
        accessibilityState={{ disabled }}
        testID={testID}
      >
        {value && (
          <View
            style={[styles.colorPreview, { backgroundColor: value }]}
          />
        )}
        <Text style={value ? styles.text : styles.placeholder}>
          {value || placeholder}
        </Text>
      </TouchableOpacity>

      <Modal
        visible={isVisible}
        transparent
        animationType="fade"
        onRequestClose={() => setIsVisible(false)}
      >
        <View style={styles.modal}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>选择颜色</Text>
              <TouchableOpacity
                style={styles.closeButton}
                onPress={() => setIsVisible(false)}
              >
                <Text style={styles.closeButtonText}>完成</Text>
              </TouchableOpacity>
            </View>

            <ScrollView style={styles.colorGrid}>
              {renderColorGrid()}
            </ScrollView>

            <View style={styles.customColorSection}>
              <Text style={styles.customColorTitle}>当前选择</Text>
              <View style={{ flexDirection: 'row', alignItems: 'center' }}>
                {value && (
                  <View
                    style={[
                      styles.colorPreview,
                      { backgroundColor: value, marginRight: 12 }
                    ]}
                  />
                )}
                <Text style={styles.text}>{value || '未选择'}</Text>
              </View>
            </View>
          </View>
        </View>
      </Modal>
    </>
  );
};

export default ColorPicker; 