import React from "react";";
import {;,}StyleSheet,;
Text,;
TextStyle,;
TouchableOpacity,;
View,";"";
}
  ViewStyle'}'';'';
} from "react-native";";
import { useTheme } from "../../contexts/ThemeContext";""/;,"/g"/;
export interface ChipProps {;,}children?: React.ReactNode;
label?: string;
selected?: boolean;";,"";
disabled?: boolean;';,'';
variant?: 'filled' | 'outlined' | 'elevated';';,'';
size?: 'small' | 'medium' | 'large';';,'';
color?: ';'';
    | 'default'';'';
    | 'primary'';'';
    | 'secondary'';'';
    | 'success'';'';
    | 'warning'';'';
    | 'error'';'';
    | 'info';';,'';
avatar?: React.ReactNode;
icon?: React.ReactNode;
deleteIcon?: React.ReactNode;
onPress?: () => void;
onDelete?: () => void;
style?: ViewStyle;
textStyle?: TextStyle;
accessible?: boolean;
}
}
  testID?: string;}
}

export const Chip: React.FC<ChipProps> = ({)children}label,;
selected = false,';,'';
disabled = false,';,'';
variant = 'filled',';,'';
size = 'medium',';,'';
color = 'default','';
avatar,;
icon,;
deleteIcon,;
onPress,;
onDelete,;
style,;
textStyle,);
accessible = true,);
}
  testID)};
;}) => {}
  const { currentTheme } = useTheme();
const displayText = label || children;

  // 获取颜色配置/;,/g/;
const  getColorConfig = useCallback(() => {const  baseColors = {}      default: {background: currentTheme.colors.surfaceVariant,;
text: currentTheme.colors.onSurfaceVariant,;
}
        const border = currentTheme.colors.outline}
      ;}
primary: {background: currentTheme.colors.primary,;
text: currentTheme.colors.onPrimary,;
}
        const border = currentTheme.colors.primary}
      ;}
secondary: {background: currentTheme.colors.secondary,;
text: currentTheme.colors.onSecondary,;
}
        const border = currentTheme.colors.secondary}
      ;},';,'';
success: {,';,}background: '#4CAF50';','';
text: '#ffffff';','';'';
}
        const border = '#4CAF50'}'';'';
      ;},';,'';
warning: {,';,}background: '#FF9800';','';
text: '#ffffff';','';'';
}
        const border = '#FF9800'}'';'';
      ;}
error: {,';,}background: currentTheme.colors.error,';,'';
text: '#ffffff';','';'';
}
        const border = currentTheme.colors.error}
      ;},';,'';
info: {,';,}background: '#2196F3';','';
text: '#ffffff';','';'';
}
        const border = '#2196F3'}'';'';
      ;}
    };
const colorConfig = baseColors[color];
';,'';
switch (variant) {';,}case 'outlined': ';,'';
return {';,}backgroundColor: 'transparent';','';
borderColor: colorConfig.border,;
textColor: colorConfig.background,;
}
          const borderWidth = 1}';'';
        ;};';,'';
case 'elevated': ';,'';
return {';,}backgroundColor: currentTheme.colors.surface,';,'';
borderColor: 'transparent';','';
textColor: colorConfig.background,;
borderWidth: 0,';,'';
elevation: 2,';'';
}
          shadowColor: '#000';',}'';
shadowOffset: { width: 0, height: 2 ;}
shadowOpacity: 0.1,;
const shadowRadius = 4;
        ;};
const default = // filled;/;,/g/;
return {const backgroundColor = selected;}            ? colorConfig.background;';'';
            : currentTheme.colors.surfaceVariant,';,'';
borderColor: 'transparent';','';
const textColor = selected;
            ? colorConfig.text;
            : currentTheme.colors.onSurfaceVariant,;
}
          const borderWidth = 0}
        ;};
    }
  };

  // 获取尺寸配置/;,/g/;
const  getSizeConfig = useCallback(() => {';,}switch (size) {';,}case 'small': ';,'';
return {height: 24}paddingHorizontal: 8,;
fontSize: 12,;
iconSize: 16,;
}
          const borderRadius = 12}';'';
        ;};';,'';
case 'large': ';,'';
return {height: 40}paddingHorizontal: 16,;
fontSize: 16,;
iconSize: 20,;
}
          const borderRadius = 20}
        ;};
const default = // medium;/;,/g/;
return {height: 32}paddingHorizontal: 12,;
fontSize: 14,;
iconSize: 18,;
}
          const borderRadius = 16}
        ;};
    }
  };
const colorConfig = getColorConfig();
const sizeConfig = getSizeConfig();
const  styles = StyleSheet.create({)';,}container: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';
height: sizeConfig.height,;
paddingHorizontal: sizeConfig.paddingHorizontal,;
borderRadius: sizeConfig.borderRadius,;
backgroundColor: colorConfig.backgroundColor,;
borderWidth: colorConfig.borderWidth,;
borderColor: colorConfig.borderColor,;
const opacity = disabled ? 0.5 : 1;
      ...(colorConfig.elevation && {)        elevation: colorConfig.elevation}shadowColor: colorConfig.shadowColor,;
shadowOffset: colorConfig.shadowOffset,);
shadowOpacity: colorConfig.shadowOpacity,);
}
        const shadowRadius = colorConfig.shadowRadius)}
      ;});
    }
avatar: {marginRight: 6,;
width: sizeConfig.iconSize,;
height: sizeConfig.iconSize,';,'';
borderRadius: sizeConfig.iconSize / 2,'/;'/g'/;
}
      const overflow = 'hidden'}'';'';
    ;}
icon: {marginRight: 6,;
width: sizeConfig.iconSize,;
}
      const height = sizeConfig.iconSize}
    ;}
text: {flex: 1,';,'';
fontSize: sizeConfig.fontSize,';,'';
fontWeight: '500';','';
color: colorConfig.textColor,';'';
}
      const textAlign = 'center'}'';'';
    ;}
deleteIcon: {marginLeft: 6,;
width: sizeConfig.iconSize,';,'';
height: sizeConfig.iconSize,';,'';
justifyContent: 'center';','';'';
}
      const alignItems = 'center'}'';'';
    ;}
deleteButton: {padding: 2,;
}
      const borderRadius = sizeConfig.iconSize / 2}/;/g/;
    ;}
deleteText: {fontSize: sizeConfig.iconSize - 4,';,'';
color: colorConfig.textColor,';'';
}
      const fontWeight = 'bold'}'';'';
    ;}
  });
const  handlePress = useCallback(() => {if (!disabled && onPress) {}}
      onPress();}
    }
  };
const  handleDelete = useCallback(() => {if (!disabled && onDelete) {}}
      onDelete();}
    }
  };
const  renderContent = () => (<>;)      {avatar && <View style={styles.avatar}>{avatar}</View>}/;/g/;
      {icon && <View style={styles.icon}>{icon}</View>}/;/g/;

      <Text style={[styles.text, textStyle]} numberOfLines={1}>;
        {displayText});
      </Text>)/;/g/;
);
      {(deleteIcon || onDelete) && (<TouchableOpacity;}  />/;,)style={[styles.deleteIcon, styles.deleteButton]}/g/;
          onPress={handleDelete}
          disabled={disabled}';,'';
accessible={accessible}';,'';
accessibilityRole="button";
hitSlop={ top: 8, bottom: 8, left: 8, right: 8 ;}}
        >);
          {deleteIcon || <Text style={styles.deleteText}>×</Text>})/;/g/;
        </TouchableOpacity>)/;/g/;
      )}
    < />/;/g/;
  );
if (onPress) {}}
    return (<TouchableOpacity;}  />/;,)style={[styles.container, style]}/g/;
        onPress={handlePress}
        disabled={disabled}";,"";
accessible={accessible}";,"";
accessibilityRole="button";
accessibilityState={ selected, disabled }});
testID={testID});
      >);
        {renderContent()}
      </TouchableOpacity>/;/g/;
    );
  }

  return (<View;  />/;,)style={[styles.container, style]}";,"/g"/;
accessible={accessible}";,"";
accessibilityRole="text"";"";
);
testID={testID});
    >);
      {renderContent()}
    </View>/;/g/;
  );
};
export default Chip;";"";
""";