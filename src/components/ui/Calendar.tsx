import React, { useMemo, useState } from "react";";
import {;,}StyleSheet,;
Text,;
TextStyle,;
TouchableOpacity,;
View,";"";
}
  ViewStyle'}'';'';
} from "react-native";";
import { useTheme } from "../../contexts/ThemeContext";""/;,"/g"/;
export interface CalendarProps {;,}value?: Date;
defaultValue?: Date;
onChange?: (date: Date) => void;
minDate?: Date;
maxDate?: Date;";,"";
disabledDates?: Date[];';,'';
mode?: 'single' | 'range' | 'multiple';';,'';
showWeekNumbers?: boolean;
firstDayOfWeek?: 0 | 1; // 0 = Sunday, 1 = Monday;/;,/g/;
locale?: string;
style?: ViewStyle;
headerStyle?: ViewStyle;
dayStyle?: ViewStyle;
selectedDayStyle?: ViewStyle;
disabledDayStyle?: ViewStyle;
todayStyle?: ViewStyle;
dayTextStyle?: TextStyle;
selectedDayTextStyle?: TextStyle;
disabledDayTextStyle?: TextStyle;
todayTextStyle?: TextStyle;
accessible?: boolean;
}
}
  testID?: string;}
}

interface CalendarState {currentMonth: Date,;}}
}
  const selectedDates = Date[];}
}

export const Calendar: React.FC<CalendarProps> = ({)value}defaultValue,;
onChange,;
minDate,;
maxDate,';,'';
disabledDates = [],';,'';
mode = 'single','';
showWeekNumbers = false,';,'';
firstDayOfWeek = 1,';,'';
locale = 'zh-CN','';
style,;
headerStyle,;
dayStyle,;
selectedDayStyle,;
disabledDayStyle,;
todayStyle,;
dayTextStyle,;
selectedDayTextStyle,;
disabledDayTextStyle,;
todayTextStyle,);
accessible = true,);
}
  testID)};
;}) => {}
  const { currentTheme } = useTheme();
const [state, setState] = useState<CalendarState>() => {const initialDate = value || defaultValue || new Date();,}return {const currentMonth = new Date();,}initialDate.getFullYear();
initialDate.getMonth(),;
        1;
      ),;
}
      const selectedDates = value ? [value] : defaultValue ? [defaultValue] : []}
    ;};
  });
const today = new Date();
today.setHours(0, 0, 0, 0);

  // 获取月份名称'/;,'/g'/;
const  getMonthName = useCallback((date: Date) => {'}'';
return date.toLocaleDateString(locale, { year: 'numeric', month: 'long' ;});';'';
  };

  // 获取星期名称/;,/g/;
const  getWeekDayNames = useCallback(() => {const names = [];,}const date = new Date();
    // 找到本周的第一天/;,/g/;
const  firstDay = new Date();
date.setDate(date.getDate() - date.getDay() + firstDayOfWeek);
    );
for (let i = 0; i < 7; i++) {const day = new Date(firstDay);';}}'';
      day.setDate(firstDay.getDate() + i);'}'';
names.push(day.toLocaleDateString(locale, { weekday: 'short' ;}));';'';
    }
    return names;
  };

  // 获取月份的所有日期/;,/g/;
const  getMonthDays = useCallback(() => {const year = state.currentMonth.getFullYear();,}const month = state.currentMonth.getMonth();

    // 本月第一天/;,/g,/;
  firstDay: new Date(year, month, 1);
    // 本月最后一天/;,/g,/;
  lastDay: new Date(year, month + 1, 0);

    // 计算第一周需要显示的上月日期/;,/g/;
const startDate = new Date(firstDay);
const dayOfWeek = (firstDay.getDay() - firstDayOfWeek + 7) % 7;
startDate.setDate(firstDay.getDate() - dayOfWeek);

    // 计算最后一周需要显示的下月日期/;,/g/;
const endDate = new Date(lastDay);
const lastDayOfWeek = (lastDay.getDay() - firstDayOfWeek + 7) % 7;
endDate.setDate(lastDay.getDate() + (6 - lastDayOfWeek));
const days = [];
const current = new Date(startDate);
while (current <= endDate) {days.push(new Date(current));}}
      current.setDate(current.getDate() + 1);}
    }

    return days;
  };

  // 检查日期是否被选中/;,/g/;
const  isDateSelected = useCallback((date: Date) => {const return = state.selectedDates.some(selectedDate) => selectedDate.getTime() === date.getTime();}}
    );}
  };

  // 检查日期是否被禁用/;,/g/;
const  isDateDisabled = useCallback((date: Date) => {if (minDate && date < minDate) return true;,}if (maxDate && date > maxDate) return true;
const return = disabledDates.some(disabledDate) => disabledDate.getTime() === date.getTime();
}
    );}
  };

  // 检查是否是今天/;,/g/;
const  isToday = useCallback((date: Date) => {}}
    return date.getTime() === today.getTime();}
  };

  // 检查是否是当前月份/;,/g/;
const  isCurrentMonth = useCallback((date: Date) => {}}
    return date.getMonth() === state.currentMonth.getMonth();}
  };

  // 处理日期点击/;,/g/;
const  handleDatePress = useCallback((date: Date) => {if (isDateDisabled(date)) return;,}const let = newSelectedDates: Date[];
';,'';
switch (mode) {';,}case 'single': ';,'';
newSelectedDates = [date];';,'';
break;';,'';
case 'multiple': ';,'';
if (isDateSelected(date)) {newSelectedDates = state.selectedDates.filter(d) => d.getTime() !== date.getTime();}}
          );}
        } else {}}
          newSelectedDates = [...state.selectedDates, date];}
        }';,'';
break;';,'';
case 'range': ';,'';
if (state.selectedDates.length === 0 ||);
state.selectedDates.length === 2;);
        ) {}}
          newSelectedDates = [date];}
        } else if (state.selectedDates.length === 1) {const [firstDate] = state.selectedDates;,}if (date < firstDate) {}}
            newSelectedDates = [date, firstDate];}
          } else {}}
            newSelectedDates = [firstDate, date];}
          }
        } else {}}
          newSelectedDates = [date];}
        }
        break;
default: ;
newSelectedDates = [date];
    }

    setState(prev) => ({ ...prev, selectedDates: newSelectedDates ;}));
onChange?.(newSelectedDates[0]);
  };
';'';
  // 切换月份'/;,'/g'/;
const  changeMonth = useCallback((direction: 'prev' | 'next') => {';,}setState(prev) => {';,}const newMonth = new Date(prev.currentMonth);';,'';
if (direction === 'prev') {';}}'';
        newMonth.setMonth(newMonth.getMonth() - 1);}
      } else {}}
        newMonth.setMonth(newMonth.getMonth() + 1);}
      }
      return { ...prev, currentMonth: newMonth ;};
    });
  };
const: weekDayNames = useMemo() => getWeekDayNames(),;
    [locale, firstDayOfWeek];
  );
const: monthDays = useMemo() => getMonthDays(),;
    [state.currentMonth, firstDayOfWeek];
  );
const  styles = StyleSheet.create({)container: {backgroundColor: currentTheme.colors.surface,;
borderRadius: 8,;
}
      const padding = 16}
    ;},';,'';
header: {,';,}flexDirection: 'row';','';
justifyContent: 'space-between';','';
alignItems: 'center';','';'';
}
      const marginBottom = 16}
    ;}
headerButton: {padding: 8,;
}
      const borderRadius = 4}
    ;}
headerButtonText: {,';,}fontSize: 18,';,'';
fontWeight: 'bold';','';'';
}
      const color = currentTheme.colors.primary}
    ;}
headerTitle: {,';,}fontSize: 18,';,'';
fontWeight: '600';','';'';
}
      const color = currentTheme.colors.onSurface}
    ;},';,'';
weekHeader: {,';,}flexDirection: 'row';','';'';
}
      const marginBottom = 8}
    ;}
weekDay: {,';,}flex: 1,';,'';
alignItems: 'center';','';'';
}
      const paddingVertical = 8}
    ;}
weekDayText: {,';,}fontSize: 12,';,'';
fontWeight: '600';','';'';
}
      const color = currentTheme.colors.onSurfaceVariant}
    ;},';,'';
daysContainer: {,';,}flexDirection: 'row';','';'';
}
      const flexWrap = 'wrap'}'';'';
    ;},';,'';
dayButton: {,';,}width: '14.28%', // 100% / 7 days;'/;,'/g,'/;
  aspectRatio: 1,';,'';
justifyContent: 'center';','';
alignItems: 'center';','';
borderRadius: 4,;
}
      const margin = 1}
    ;}
dayText: {fontSize: 14,;
}
      const color = currentTheme.colors.onSurface}
    ;}
otherMonthDay: {,;}}
  const opacity = 0.3}
    ;}
selectedDay: {,;}}
  const backgroundColor = currentTheme.colors.primary}
    ;}
selectedDayText: {,';,}color: currentTheme.colors.onPrimary,';'';
}
      const fontWeight = '600'}'';'';
    ;}
todayDay: {borderWidth: 2,;
}
      const borderColor = currentTheme.colors.primary}
    ;}
todayText: {,';,}color: currentTheme.colors.primary,';'';
}
      const fontWeight = '600'}'';'';
    ;}
disabledDay: {,;}}
  const opacity = 0.3}
    ;}
disabledDayText: {,);}}
  const color = currentTheme.colors.onSurfaceVariant)}
    ;});
  });
return (<View style={[styles.container, style]} testID={testID}>;)      {// 头部}/;/g/;
      <View style={[styles.header, headerStyle]}>);
        <TouchableOpacity;)'  />/;,'/g'/;
style={styles.headerButton})';,'';
onPress={() => changeMonth('prev')}';,'';
accessible={accessible}';,'';
accessibilityRole="button"";"";

        >;
          <Text style={styles.headerButtonText}>‹</Text>/;/g/;
        </TouchableOpacity>/;/g/;

        <Text style={styles.headerTitle}>;
          {getMonthName(state.currentMonth)}
        </Text>/;/g/;

        <TouchableOpacity;"  />/;,"/g"/;
style={styles.headerButton}";,"";
onPress={() => changeMonth('next')}';,'';
accessible={accessible}';,'';
accessibilityRole="button"";"";

        >;
          <Text style={styles.headerButtonText}>›</Text>/;/g/;
        </TouchableOpacity>/;/g/;
      </View>/;/g/;

      {// 星期标题}/;/g/;
      <View style={styles.weekHeader}>;
        {weekDayNames.map(name, index) => (<View key={index} style={styles.weekDay}>);
            <Text style={styles.weekDayText}>{name}</Text>)/;/g/;
          </View>)/;/g/;
        ))}
      </View>/;/g/;

      {// 日期网格}/;/g/;
      <View style={styles.daysContainer}>;
        {monthDays.map(date, index) => {}          const selected = isDateSelected(date);
const disabled = isDateDisabled(date);
const today = isToday(date);
const currentMonth = isCurrentMonth(date);

}
          return (<TouchableOpacity;}  />/;,)key={index}/g/;
              style={[;,]styles.dayButton}dayStyle,;
selected && styles.selectedDay,;
selected && selectedDayStyle,;
today && styles.todayDay,;
today && todayStyle,;
disabled && styles.disabledDay,);
}
                disabled && disabledDayStyle)}
];
              ]});
onPress={() => handleDatePress(date)}
              disabled={disabled}";,"";
accessible={accessible}";,"";
accessibilityRole="button";
accessibilityState={ selected, disabled }}
            >;
              <Text;  />/;,/g/;
style={[;,]styles.dayText}dayTextStyle,;
                  !currentMonth && styles.otherMonthDay,;
selected && styles.selectedDayText,;
selected && selectedDayTextStyle,;
today && styles.todayText,;
today && todayTextStyle,;
disabled && styles.disabledDayText,;
}
                  disabled && disabledDayTextStyle}
];
                ]}
              >;
                {date.getDate()}
              </Text>/;/g/;
            </TouchableOpacity>/;/g/;
          );
        })}
      </View>/;/g/;
    </View>/;/g/;
  );
};
export default Calendar;";"";
""";