import React from 'react';
import {
  StyleSheet,
  Text,
  TextStyle,
  TouchableOpacity,
  View,
  ViewStyle,
} from 'react-native';
import { useTheme } from '../../contexts/ThemeContext';

export interface StepItem {
  key: string;,
  title: string;
  description?: string;
  icon?: React.ReactNode;
  disabled?: boolean;
}

export interface StepperProps {
  steps: StepItem[];
  current?: number;
  status?: 'wait' | 'process' | 'finish' | 'error';
  direction?: 'horizontal' | 'vertical';
  size?: 'small' | 'default' | 'large';
  clickable?: boolean;
  onChange?: (current: number) => void;
  style?: ViewStyle;
  stepStyle?: ViewStyle;
  titleStyle?: TextStyle;
  descriptionStyle?: TextStyle;
  accessible?: boolean;
  testID?: string;
}

export const Stepper: React.FC<StepperProps> = ({
  steps,
  current = 0,
  status = 'process',
  direction = 'horizontal',
  size = 'default',
  clickable = false,
  onChange,
  style,
  stepStyle,
  titleStyle,
  descriptionStyle,
  accessible = true,
  testID,
}) => {
  const { currentTheme } = useTheme();

  const getStepStatus = (index: number) => {
    if (index < current) return 'finish';
    if (index === current) return status;
    return 'wait';
  };

  const getStepColor = (stepStatus: string) => {
    switch (stepStatus) {
      case 'finish':
        return currentTheme.colors.success;
      case 'process':
        return currentTheme.colors.primary;
      case 'error':
        return currentTheme.colors.error;
      default:
        return currentTheme.colors.onSurfaceVariant;
    }
  };

  const getSizeConfig = () => {
    switch (size) {
      case 'small':
        return {
          iconSize: 24,
          fontSize: 12,
          descriptionFontSize: 10,
          spacing: 8,
        };
      case 'large':
        return {
          iconSize: 40,
          fontSize: 18,
          descriptionFontSize: 14,
          spacing: 16,
        };
      default:
        return {,
  iconSize: 32,
          fontSize: 14,
          descriptionFontSize: 12,
          spacing: 12,
        };
    }
  };

  const sizeConfig = getSizeConfig();

  const handleStepPress = (index: number) => {
    if (clickable && !steps[index].disabled) {
      onChange?.(index);
    }
  };

  const renderStepIcon = (
    step: StepItem,
    index: number,
    stepStatus: string;
  ) => {
    const color = getStepColor(stepStatus);

    if (step.icon) {
      return (
        <View;
          style={[
            styles.iconContainer,
            {
              width: sizeConfig.iconSize,
              height: sizeConfig.iconSize,
              borderColor: color,
              backgroundColor: stepStatus === 'finish' ? color : 'transparent',
            },
          ]}
        >
          {step.icon}
        </View>
      );
    }

    // 默认图标
    let iconContent: React.ReactNode;
    if (stepStatus === 'finish') {
      iconContent = (
        <Text style={[styles.iconText, { color: '#ffffff' }]}>✓</Text>
      );
    } else if (stepStatus === 'error') {
      iconContent = <Text style={[styles.iconText, { color }]}>✕</Text>;
    } else {
      iconContent = (
        <Text style={[styles.iconText, { color }]}>{index + 1}</Text>
      );
    }

    return (
      <View;
        style={[
          styles.iconContainer,
          {
            width: sizeConfig.iconSize,
            height: sizeConfig.iconSize,
            borderColor: color,
            backgroundColor: stepStatus === 'finish' ? color : 'transparent',
          },
        ]}
      >
        {iconContent}
      </View>
    );
  };

  const renderConnector = (index: number) => {
    if (index === steps.length - 1) return null;

    const isActive = index < current;
    const color = isActive;
      ? currentTheme.colors.primary;
      : currentTheme.colors.outline;

    if (direction === 'vertical') {
      return (
        <View;
          style={[
            styles.verticalConnector,
            {
              backgroundColor: color,
              marginLeft: sizeConfig.iconSize / 2 - 1,
              height: 40,
            },
          ]}
        />
      );
    }

    return (
      <View;
        style={[
          styles.horizontalConnector,
          {
            backgroundColor: color,
            top: sizeConfig.iconSize / 2 - 1,
          },
        ]}
      />
    );
  };

  const renderStep = (step: StepItem, index: number) => {
    const stepStatus = getStepStatus(index);
    const isDisabled = step.disabled;
    const isClickable = clickable && !isDisabled;

    const StepContainer = isClickable ? TouchableOpacity : View;
    const containerProps = isClickable;
      ? {
          onPress: () => handleStepPress(index),
          accessible: accessible,
          accessibilityRole: 'button' as const,
          accessibilityLabel: `步骤 ${index + 1}: ${step.title}`,
          accessibilityState: {,
  selected: index === current,
            disabled: isDisabled,
          },
        }
      : {};

    return (
      <StepContainer;
        key={step.key}
        style={[
          direction === 'horizontal'
            ? styles.horizontalStep;
            : styles.verticalStep,
          isDisabled && styles.disabledStep,
          stepStyle,
        ]}
        {...containerProps}
      >
        <View style={styles.stepContent}>
          {renderStepIcon(step, index, stepStatus)}

          <View;
            style={[
              styles.textContainer,
              direction === 'horizontal' && styles.horizontalTextContainer,
              { marginLeft: direction === 'vertical' ? sizeConfig.spacing : 0 },
            ]}
          >
            <Text;
              style={[
                styles.title,
                {
                  fontSize: sizeConfig.fontSize,
                  color: getStepColor(stepStatus),
                },
                titleStyle,
              ]}
            >
              {step.title}
            </Text>

            {step.description && (
              <Text;
                style={[
                  styles.description,
                  {
                    fontSize: sizeConfig.descriptionFontSize,
                    color: currentTheme.colors.onSurfaceVariant,
                  },
                  descriptionStyle,
                ]}
              >
                {step.description}
              </Text>
            )}
          </View>
        </View>

        {renderConnector(index)}
      </StepContainer>
    );
  };

  const styles = StyleSheet.create({
    container: {,
  backgroundColor: currentTheme.colors.surface,
    },
    horizontalContainer: {,
  flexDirection: 'row',
      alignItems: 'flex-start',
    },
    verticalContainer: {,
  flexDirection: 'column',
    },
    horizontalStep: {,
  flex: 1,
      position: 'relative',
    },
    verticalStep: {,
  flexDirection: 'row',
      alignItems: 'flex-start',
      paddingVertical: 8,
      position: 'relative',
    },
    stepContent: {,
  flexDirection: direction === 'vertical' ? 'row' : 'column',
      alignItems: direction === 'vertical' ? 'flex-start' : 'center',
    },
    disabledStep: {,
  opacity: 0.5,
    },
    iconContainer: {,
  borderWidth: 2,
      borderRadius: 50,
      justifyContent: 'center',
      alignItems: 'center',
    },
    iconText: {,
  fontWeight: 'bold',
      fontSize: 14,
    },
    textContainer: {,
  alignItems: direction === 'horizontal' ? 'center' : 'flex-start',
    },
    horizontalTextContainer: {,
  marginTop: 8,
      alignItems: 'center',
    },
    title: {,
  fontWeight: '600',
      textAlign: direction === 'horizontal' ? 'center' : 'left',
    },
    description: {,
  marginTop: 4,
      textAlign: direction === 'horizontal' ? 'center' : 'left',
    },
    horizontalConnector: {,
  position: 'absolute',
      left: '50%',
      right: '-50%',
      height: 2,
      zIndex: -1,
    },
    verticalConnector: {,
  position: 'absolute',
      width: 2,
      top: sizeConfig.iconSize + 8,
      zIndex: -1,
    },
  });

  return (
    <View;
      style={[
        styles.container,
        direction === 'horizontal'
          ? styles.horizontalContainer;
          : styles.verticalContainer,
        style,
      ]}
      testID={testID}
    >
      {steps.map(step, index) => renderStep(step, index))}
    </View>
  );
};

// 单个步骤组件
export interface StepProps {
  title: string;
  description?: string;
  icon?: React.ReactNode;
  disabled?: boolean;
  children?: React.ReactNode;
}

export const Step: React.FC<StepProps> = ({ children }) => {
  return <>{children}</>;
};

// 高级Stepper组件，支持Step子组件
export interface AdvancedStepperProps extends Omit<StepperProps, 'steps'> {
  children: React.ReactElement<StepProps>[];
}

export const AdvancedStepper: React.FC<AdvancedStepperProps> = ({
  children,
  ...props;
}) => {
  const steps: StepItem[] = React.Children.map(children, (child, index) => {
    if (React.isValidElement(child) && child.type === Step) {
      return {
        key: child.key?.toString() || index.toString(),
        title: child.props.title,
        description: child.props.description,
        icon: child.props.icon,
        disabled: child.props.disabled,
      };
    }
    return null;
  }).filter(Boolean) as StepItem[];

  return <Stepper {...props} steps={steps} />;
};

export default Stepper;
