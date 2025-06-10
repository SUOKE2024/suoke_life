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
export interface StepItem {key: string}const title = string;
description?: string;
icon?: React.ReactNode;
}
}
  disabled?: boolean;}
}

export interface StepperProps {;,}const steps = StepItem[];";,"";
current?: number;';,'';
status?: 'wait' | 'process' | 'finish' | 'error';';,'';
direction?: 'horizontal' | 'vertical';';,'';
size?: 'small' | 'default' | 'large';';,'';
clickable?: boolean;
onChange?: (current: number) => void;
style?: ViewStyle;
stepStyle?: ViewStyle;
titleStyle?: TextStyle;
descriptionStyle?: TextStyle;
accessible?: boolean;
}
}
  testID?: string;}
}

export const Stepper: React.FC<StepperProps> = ({)steps,';,}current = 0,';,'';
status = 'process',';,'';
direction = 'horizontal',';,'';
size = 'default','';
clickable = false,;
onChange,;
style,;
stepStyle,;
titleStyle,;
descriptionStyle,);
accessible = true,);
}
  testID)};
;}) => {}
  const { currentTheme } = useTheme();
';,'';
const  getStepStatus = useCallback((index: number) => {';,}if (index < current) return 'finish';';,'';
if (index === current) return status;';'';
}
    return 'wait';'}'';'';
  };
const  getStepColor = useCallback((stepStatus: string) => {';,}switch (stepStatus) {';,}case 'finish': ';,'';
return currentTheme.colors.success;';,'';
case 'process': ';,'';
return currentTheme.colors.primary;';,'';
case 'error': ';,'';
return currentTheme.colors.error;
default: ;
}
        return currentTheme.colors.onSurfaceVariant;}
    }
  };
const  getSizeConfig = useCallback(() => {';,}switch (size) {';,}case 'small': ';,'';
return {iconSize: 24}fontSize: 12,;
descriptionFontSize: 10,;
}
          const spacing = 8}';'';
        ;};';,'';
case 'large': ';,'';
return {iconSize: 40}fontSize: 18,;
descriptionFontSize: 14,;
}
          const spacing = 16}
        ;};
default: return {iconSize: 32,;
fontSize: 14,;
descriptionFontSize: 12,;
}
          const spacing = 12}
        ;};
    }
  };
const sizeConfig = getSizeConfig();
const  handleStepPress = useCallback((index: number) => {if (clickable && !steps[index].disabled) {}}
      onChange?.(index);}
    }
  };
const: renderStepIcon = (step: StepItem,);
index: number,);
const stepStatus = string;);
  ) => {const color = getStepColor(stepStatus);,}if (step.icon) {return (<View;  />/;,)style={[;,]styles.iconContainer,;}            {width: sizeConfig.iconSize}height: sizeConfig.iconSize,';,'/g,'/;
  borderColor: color,';'';
}
              backgroundColor: stepStatus === 'finish' ? color : 'transparent'}'';'';
            ;}
];
          ]}
        >);
          {step.icon});
        </View>)/;/g/;
      );
    }

    // 默认图标'/;,'/g'/;
const let = iconContent: React.ReactNode;';,'';
if (stepStatus === 'finish') {'}'';
iconContent = (<Text style={[styles.iconText, { color: '#ffffff' ;}]}>✓</Text>')''/;'/g'/;
      );';'';
    } else if (stepStatus === 'error') {'}'';
iconContent = <Text style={[styles.iconText, { color }]}>✕</Text>;/;/g/;
    } else {}
      iconContent = (<Text style={[styles.iconText, { color }]}>{index + 1}</Text>)/;/g/;
      );
    }

    return (<View;  />/;,)style={[;,]styles.iconContainer,;}          {width: sizeConfig.iconSize}height: sizeConfig.iconSize,';,'/g,'/;
  borderColor: color,';'';
}
            backgroundColor: stepStatus === 'finish' ? color : 'transparent'}'';'';
          ;}
];
        ]}
      >);
        {iconContent});
      </View>)/;/g/;
    );
  };
const  renderConnector = useCallback((index: number) => {if (index === steps.length - 1) return null;,}const isActive = index < current;
const color = isActive;
      ? currentTheme.colors.primary;
      : currentTheme.colors.outline;';'';
';,'';
if (direction === 'vertical') {';,}return (<View;  />/;,)style={[;,]styles.verticalConnector,;}            {backgroundColor: color}marginLeft: sizeConfig.iconSize / 2 - 1,/;'/g'/;
}
              const height = 40}
            ;});
];
          ]});
        />)/;/g/;
      );
    }

    return (<View;  />/;,)style={[;,]styles.horizontalConnector,;}          {backgroundColor: color,;}}/g/;
            const top = sizeConfig.iconSize / 2 - 1}/;/g/;
          ;});
];
        ]});
      />)/;/g/;
    );
  };
const: renderStep = useCallback((step: StepItem, index: number) => {const stepStatus = getStepStatus(index);,}const isDisabled = step.disabled;
const isClickable = clickable && !isDisabled;
const StepContainer = isClickable ? TouchableOpacity : View;
const containerProps = isClickable;
      ? {onPress: () => handleStepPress(index),';,}accessible: accessible,';,'';
accessibilityRole: 'button' as const;','';
accessibilityState: {selected: index === current,;
}
            const disabled = isDisabled}
          ;}
        }
      : {};
return (<StepContainer;  />/;,)key={step.key}';,'/g'/;
style={[;]';,}direction === 'horizontal'';'';
            ? styles.horizontalStep;
            : styles.verticalStep,;
isDisabled && styles.disabledStep,;
}
          stepStyle}
];
        ]}
        {...containerProps});
      >);
        <View style={styles.stepContent}>);
          {renderStepIcon(step, index, stepStatus)}

          <View;  />/;,/g/;
style={[;]';,}styles.textContainer,';'';
}
              direction === 'horizontal' && styles.horizontalTextContainer,'}'';'';
              { marginLeft: direction === 'vertical' ? sizeConfig.spacing : 0 ;}';'';
];
            ]}
          >;
            <Text;  />/;,/g/;
style={[;,]styles.title,;}                {fontSize: sizeConfig.fontSize,;}}
                  const color = getStepColor(stepStatus)}
                ;}
titleStyle;
];
              ]}
            >;
              {step.title}
            </Text>/;/g/;

            {step.description && (<Text;  />/;,)style={[;,]styles.description,;}                  {fontSize: sizeConfig.descriptionFontSize,;}}/g/;
                    const color = currentTheme.colors.onSurfaceVariant}
                  ;}
descriptionStyle;
];
                ]}
              >);
                {step.description});
              </Text>)/;/g/;
            )}
          </View>/;/g/;
        </View>/;/g/;

        {renderConnector(index)}
      </StepContainer>/;/g/;
    );
  };
const  styles = StyleSheet.create({)container: {,;}}
  const backgroundColor = currentTheme.colors.surface}
    ;},';,'';
horizontalContainer: {,';,}flexDirection: 'row';','';'';
}
      const alignItems = 'flex-start'}'';'';
    ;},';,'';
verticalContainer: {,';}}'';
  const flexDirection = 'column'}'';'';
    ;}
horizontalStep: {,';,}flex: 1,';'';
}
      const position = 'relative'}'';'';
    ;},';,'';
verticalStep: {,';,}flexDirection: 'row';','';
alignItems: 'flex-start';','';
paddingVertical: 8,';'';
}
      const position = 'relative'}'';'';
    ;},';,'';
stepContent: {,';,}flexDirection: direction === 'vertical' ? 'row' : 'column';','';'';
}
      alignItems: direction === 'vertical' ? 'flex-start' : 'center'}'';'';
    ;}
disabledStep: {,;}}
  const opacity = 0.5}
    ;}
iconContainer: {borderWidth: 2,';,'';
borderRadius: 50,';,'';
justifyContent: 'center';','';'';
}
      const alignItems = 'center'}'';'';
    ;},';,'';
iconText: {,';,}fontWeight: 'bold';','';'';
}
      const fontSize = 14}
    ;},';,'';
textContainer: {,';}}'';
  alignItems: direction === 'horizontal' ? 'center' : 'flex-start'}'';'';
    ;}
horizontalTextContainer: {,';,}marginTop: 8,';'';
}
      const alignItems = 'center'}'';'';
    ;},';,'';
title: {,';,}fontWeight: '600';','';'';
}
      textAlign: direction === 'horizontal' ? 'center' : 'left'}'';'';
    ;}
description: {,';,}marginTop: 4,';'';
}
      textAlign: direction === 'horizontal' ? 'center' : 'left'}'';'';
    ;},';,'';
horizontalConnector: {,';,}position: 'absolute';','';
left: '50%';','';
right: '-50%';','';
height: 2,;
}
      const zIndex = -1}
    ;},';,'';
verticalConnector: {,';,}position: 'absolute';','';
width: 2,;
top: sizeConfig.iconSize + 8,);
}
      const zIndex = -1)}
    ;});
  });
return (<View;  />/;,)style={[;]';,}styles.container,';,'/g'/;
direction === 'horizontal'';'';
          ? styles.horizontalContainer;
          : styles.verticalContainer,;
}
        style}
];
      ]});
testID={testID});
    >);
      {steps.map(step, index) => renderStep(step, index))}
    </View>/;/g/;
  );
};

// 单个步骤组件/;,/g/;
export interface StepProps {;,}const title = string;
description?: string;
icon?: React.ReactNode;
disabled?: boolean;
}
}
  children?: React.ReactNode;}
}

export const Step: React.FC<StepProps> = ({ children ;}) => {}
  return <>{children}< />;/;/g/;
};
';'';
// 高级Stepper组件，支持Step子组件'/;,'/g'/;
export interface AdvancedStepperProps extends Omit<StepperProps, 'steps'> {';}}'';
  const children = React.ReactElement<StepProps>[];}
}

export const AdvancedStepper: React.FC<AdvancedStepperProps> = ({));,}children,);
}
  ...props;)}
}) => {const: steps: StepItem[] = React.Children.map(children, (child, index) => {}    if (React.isValidElement(child) && child.type === Step) {return {}        key: child.key?.toString() || index.toString(),;
title: child.props.title,;
description: child.props.description,;
icon: child.props.icon,;
}
        const disabled = child.props.disabled}
      ;};
    }
    return null;
  }).filter(Boolean) as StepItem[];
return <Stepper {...props} steps={steps}  />;/;/g/;
};
export default Stepper;';'';
''';