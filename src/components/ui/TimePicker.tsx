import React, { useState } from 'react';
import {;
  Modal,
  ScrollView,
  StyleSheet,
  Text,
  TextStyle,
  TouchableOpacity,
  View,
  ViewStyle
} from 'react-native';
import { useTheme } from '../../contexts/ThemeContext';

export interface TimePickerProps {
  value?: { hour: number; minute: number };
  format?: '12' | '24';
  minuteInterval?: 1 | 5 | 10 | 15 | 30;
  placeholder?: string;
  disabled?: boolean;
  onTimeChange?: (time: { hour: number; minute: number }) => void;
  style?: ViewStyle;
  textStyle?: TextStyle;
  placeholderStyle?: TextStyle;
  accessible?: boolean;
  accessibilityLabel?: string;
  testID?: string;
}

export const TimePicker: React.FC<TimePickerProps> = ({
  value,
  format = '24',
  minuteInterval = 1,
  placeholder = '请选择时间',
  disabled = false,
  onTimeChange,
  style,
  textStyle,
  placeholderStyle,
  accessible = true,
  accessibilityLabel,
  testID
}) => {
  const { currentTheme } = useTheme();
  const [isVisible, setIsVisible] = useState(false);
  const [selectedTime, setSelectedTime] = useState(
    value || { hour: new Date().getHours(), minute: new Date().getMinutes() }
  );
  const [isPM, setIsPM] = useState(selectedTime.hour >= 12);

  const formatTime = (time: { hour: number; minute: number }): string => {
    if (format === '12') {
      const hour12 =
        time.hour === 0 ? 12 : time.hour > 12 ? time.hour - 12 : time.hour;
      const period = time.hour >= 12 ? 'PM' : 'AM';
      return `${hour12.toString().padStart(2, '0')}:${time.minute.toString().padStart(2, '0')} ${period}`;
    } else {
      return `${time.hour.toString().padStart(2, '0')}:${time.minute.toString().padStart(2, '0')}`;
    }
  };

  const generateHours = () => {
    if (format === '12') {
      return Array.from({ length: 12 }, (_, i) => i + 1);
    } else {
      return Array.from({ length: 24 }, (_, i) => i);
    }
  };

  const generateMinutes = () => {
    const minutes = [];
    for (let i = 0; i < 60; i += minuteInterval) {
      minutes.push(i);
    }
    return minutes;
  };

  const handleConfirm = () => {
    let finalHour = selectedTime.hour;

    if (format === '12') {
      if (isPM && selectedTime.hour !== 12) {
        finalHour = selectedTime.hour + 12;
      } else if (!isPM && selectedTime.hour === 12) {
        finalHour = 0;
      }
    }

    onTimeChange?.({ hour: finalHour, minute: selectedTime.minute });
    setIsVisible(false);
  };

  const handleCancel = () => {
    setSelectedTime(
      value || { hour: new Date().getHours(), minute: new Date().getMinutes() }
    );
    setIsVisible(false);
  };

  const renderTimeSelector = () => {
    const hours = generateHours();
    const minutes = generateMinutes();

    return (
      <View style={styles.selectorContainer}>
        {// 小时选择器}
        <View style={styles.columnContainer}>
          <Text style={styles.columnTitle}>小时</Text>
          <ScrollView;
            style={styles.scrollContainer}
            showsVerticalScrollIndicator={false}
          >
            {hours.map(hour) => (
              <TouchableOpacity;
                key={hour}
                style={[
                  styles.timeItem,
                  selectedTime.hour === hour && styles.selectedTimeItem
                ]}
                onPress={() => setSelectedTime({ ...selectedTime, hour })}
              >
                <Text;
                  style={[
                    styles.timeText,
                    selectedTime.hour === hour && styles.selectedTimeText
                  ]}
                >
                  {hour.toString().padStart(2, '0')}
                </Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
        </View>

        {// 分钟选择器}
        <View style={styles.columnContainer}>
          <Text style={styles.columnTitle}>分钟</Text>
          <ScrollView;
            style={styles.scrollContainer}
            showsVerticalScrollIndicator={false}
          >
            {minutes.map(minute) => (
              <TouchableOpacity;
                key={minute}
                style={[
                  styles.timeItem,
                  selectedTime.minute === minute && styles.selectedTimeItem
                ]}
                onPress={() => setSelectedTime({ ...selectedTime, minute })}
              >
                <Text;
                  style={[
                    styles.timeText,
                    selectedTime.minute === minute && styles.selectedTimeText
                  ]}
                >
                  {minute.toString().padStart(2, '0')}
                </Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
        </View>

        {// 12小时制的AM/PM选择器}
        {format === '12' && (
          <View style={styles.columnContainer}>
            <Text style={styles.columnTitle}>时段</Text>
            <ScrollView;
              style={styles.scrollContainer}
              showsVerticalScrollIndicator={false}
            >
              {['AM', 'PM'].map(period) => (
                <TouchableOpacity;
                  key={period}
                  style={[
                    styles.timeItem,
                    (period === 'AM' && !isPM) || (period === 'PM' && isPM)) &&
                      styles.selectedTimeItem
                  ]}
                  onPress={() => setIsPM(period === 'PM')}
                >
                  <Text;
                    style={[
                      styles.timeText,
                      (period === 'AM' && !isPM) ||
                        (period === 'PM' && isPM)) &&
                        styles.selectedTimeText
                    ]}
                  >
                    {period}
                  </Text>
                </TouchableOpacity>
              ))}
            </ScrollView>
          </View>
        )}
      </View>
    );
  };

  const styles = StyleSheet.create({
    container: {,
  borderWidth: 1,
      borderColor: currentTheme.colors.outline,
      borderRadius: 8,
      paddingHorizontal: 12,
      paddingVertical: 16,
      backgroundColor: currentTheme.colors.surface,
      minHeight: 48,
      justifyContent: 'center'
    },
    containerDisabled: {,
  backgroundColor: currentTheme.colors.surfaceVariant,
      opacity: 0.6
    },
    text: {,
  fontSize: 16,
      color: currentTheme.colors.onSurface,
      ...textStyle
    },
    placeholder: {,
  fontSize: 16,
      color: currentTheme.colors.onSurfaceVariant,
      ...placeholderStyle
    },
    modal: {,
  flex: 1,
      backgroundColor: 'rgba(0, 0, 0, 0.5)',
      justifyContent: 'flex-end'
    },
    modalContent: {,
  backgroundColor: currentTheme.colors.surface,
      borderTopLeftRadius: 16,
      borderTopRightRadius: 16,
      maxHeight: '70%'
    },
    modalHeader: {,
  flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      paddingHorizontal: 16,
      paddingVertical: 16,
      borderBottomWidth: 1,
      borderBottomColor: currentTheme.colors.outline
    },
    headerButton: {,
  paddingHorizontal: 8,
      paddingVertical: 4
    },
    headerButtonText: {,
  fontSize: 16,
      color: currentTheme.colors.onSurface
    },
    headerTitle: {,
  fontSize: 18,
      fontWeight: '600',
      color: currentTheme.colors.onSurface
    },
    selectedTimeDisplay: {,
  padding: 16,
      alignItems: 'center'
    },
    selectedTimeDisplayText: {,
  fontSize: 32,
      fontWeight: '600',
      color: currentTheme.colors.primary
    },
    selectorContainer: {,
  flexDirection: 'row',
      paddingHorizontal: 16,
      paddingBottom: 16
    },
    columnContainer: {,
  flex: 1,
      marginHorizontal: 8
    },
    columnTitle: {,
  fontSize: 14,
      fontWeight: '500',
      color: currentTheme.colors.onSurface,
      textAlign: 'center',
      marginBottom: 8
    },
    scrollContainer: {,
  maxHeight: 200
    },
    timeItem: {,
  paddingVertical: 12,
      paddingHorizontal: 8,
      alignItems: 'center',
      borderRadius: 8,
      marginVertical: 2
    },
    selectedTimeItem: {,
  backgroundColor: currentTheme.colors.primary
    },
    timeText: {,
  fontSize: 16,
      color: currentTheme.colors.onSurface
    },
    selectedTimeText: {,
  color: currentTheme.colors.onPrimary,
      fontWeight: '600'
    }
  });

  return (
    <>
      <TouchableOpacity;
        style={[styles.container, disabled && styles.containerDisabled, style]}
        onPress={() => !disabled && setIsVisible(true)}
        disabled={disabled}
        accessible={accessible}
        accessibilityRole="button"
        accessibilityLabel={
          accessibilityLabel ||
          `时间选择器，当前值：${value ? formatTime(value) : placeholder}`
        }
        accessibilityState={ disabled }}
        testID={testID}
      >
        <Text style={value ? styles.text : styles.placeholder}>
          {value ? formatTime(value) : placeholder}
        </Text>
      </TouchableOpacity>

      <Modal;
        visible={isVisible}
        transparent;
        animationType="slide"
        onRequestClose={handleCancel}
      >
        <TouchableOpacity;
          style={styles.modal}
          activeOpacity={1}
          onPress={handleCancel}
        >
          <TouchableOpacity activeOpacity={1} onPress={() => {}}>
            <View style={styles.modalContent}>
              <View style={styles.modalHeader}>
                <TouchableOpacity;
                  onPress={handleCancel}
                  style={styles.headerButton}
                >
                  <Text style={styles.headerButtonText}>取消</Text>
                </TouchableOpacity>
                <Text style={styles.headerTitle}>选择时间</Text>
                <TouchableOpacity;
                  onPress={handleConfirm}
                  style={styles.headerButton}
                >
                  <Text;
                    style={[
                      styles.headerButtonText,
                      { color: currentTheme.colors.primary }
                    ]}
                  >
                    确定
                  </Text>
                </TouchableOpacity>
              </View>

              <View style={styles.selectedTimeDisplay}>
                <Text style={styles.selectedTimeDisplayText}>
                  {formatTime(selectedTime)}
                </Text>
              </View>

              {renderTimeSelector()}
            </View>
          </TouchableOpacity>
        </TouchableOpacity>
      </Modal>
    </>
  );
};

export default TimePicker;
