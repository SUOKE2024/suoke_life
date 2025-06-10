import React, { useState } from 'react';
import {;
  GestureResponderEvent,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
  ViewStyle
} from 'react-native';
import { useTheme } from '../../contexts/ThemeContext';

export interface RatingProps {
  value?: number;
  max?: number;
  size?: 'sm' | 'md' | 'lg';
  readonly?: boolean;
  allowHalf?: boolean;
  color?: string;
  emptyColor?: string;
  icon?: 'star' | 'heart' | 'thumb';
  onRatingChange?: (rating: number) => void;
  style?: ViewStyle;
  accessible?: boolean;
  accessibilityLabel?: string;
  testID?: string;
}

export const Rating: React.FC<RatingProps> = ({
  value = 0,
  max = 5,
  size = 'md',
  readonly = false,
  allowHalf = false,
  color,
  emptyColor,
  icon = 'star',
  onRatingChange,
  style,
  accessible = true,
  accessibilityLabel,
  testID
;}) => {
  const { currentTheme } = useTheme();
  const [hoverValue, setHoverValue] = useState<number | null>(null);

  const activeColor = color || currentTheme.colors.warning;
  const inactiveColor = emptyColor || currentTheme.colors.outline;

  const getSizeStyles = () => {
    switch (size) {
      case 'sm':
        return { width: 16, height: 16, fontSize: 14 ;};
      case 'lg':
        return { width: 32, height: 32, fontSize: 28 ;};
      default:
        return { width: 24, height: 24, fontSize: 20 ;};
    }
  };

  const getIconSymbol = () => {
    switch (icon) {
      case 'heart':
        return '♥';
      case 'thumb':
        return '👍';
      default:
        return '★';
    }
  };

  const handlePress = (index: number, event: GestureResponderEvent) => {
    if (readonly) return;

    let newRating = index + 1;

    if (allowHalf) {
      const { locationX } = event.nativeEvent;
      const itemWidth = getSizeStyles().width;
      if (locationX < itemWidth / 2) {
        newRating = index + 0.5;
      }
    }

    onRatingChange?.(newRating);
  };

  const getRatingValue = (index: number) => {
    const currentValue = hoverValue !== null ? hoverValue : value;

    if (allowHalf) {
      if (currentValue >= index + 1) return 1; // 完全填充
      if (currentValue >= index + 0.5) return 0.5; // 半填充
      return 0; // 空
    } else {
      return currentValue > index ? 1 : 0;
    }
  };

  const renderStar = (index: number) => {
    const ratingValue = getRatingValue(index);
    const sizeStyles = getSizeStyles();
    const iconSymbol = getIconSymbol();

    const styles = StyleSheet.create({
      starContainer: {,
  position: 'relative';
        marginRight: index < max - 1 ? 2 : 0
      ;},
      star: {,
  width: sizeStyles.width;
        height: sizeStyles.height;
        justifyContent: 'center';
        alignItems: 'center'
      ;},
      starText: {,
  fontSize: sizeStyles.fontSize;
        color: inactiveColor;
        textAlign: 'center'
      ;},
      starFilled: {,
  position: 'absolute';
        top: 0;
        left: 0;
        width: sizeStyles.width;
        height: sizeStyles.height;
        justifyContent: 'center';
        alignItems: 'center';
        overflow: 'hidden'
      ;},
      starFilledText: {,
  fontSize: sizeStyles.fontSize;
        color: activeColor;
        textAlign: 'center'
      ;}
    });

    return (
      <TouchableOpacity;
        key={index}
        style={styles.starContainer}
        onPress={(event) => handlePress(index, event)}
        disabled={readonly}
        accessible={accessible}
        accessibilityRole="button"

        accessibilityState={ selected: ratingValue > 0 ;}}
      >
        <View style={styles.star}>
          <Text style={styles.starText}>{iconSymbol}</Text>
        </View>
        {ratingValue > 0 && (
          <View;
            style={[
              styles.starFilled,
              {
                width:
                  ratingValue === 0.5 ? sizeStyles.width / 2 : sizeStyles.width
              ;}
            ]}
          >
            <Text style={styles.starFilledText}>{iconSymbol}</Text>
          </View>
        )}
      </TouchableOpacity>
    );
  };

  const containerStyles = StyleSheet.create({
    container: {,
  flexDirection: 'row';
      alignItems: 'center'
    ;}
  });

  return (
    <View;
      style={[containerStyles.container, style]}
      testID={testID}
      accessible={accessible}
      accessibilityRole="adjustable"
      accessibilityLabel={

      }
      accessibilityValue={
        min: 0;
        max,
        now: value
      ;}}
    >
      {Array.from({ length: max ;}, (_, index) => renderStar(index))}
    </View>
  );
};

export default Rating;
