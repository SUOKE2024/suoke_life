import { colors, spacing, borderRadius, shadows } from '../../constants/theme';

/**
 * 索克生活 - Modal组件
 * 模态框组件
 */

import React from 'react';
  Modal as RNModal,
  View,
  StyleSheet,
  ViewStyle,
  TouchableOpacity,
  TouchableWithoutFeedback,
  Dimensions,
} from 'react-native';

const { width: screenWidth, height: screenHeight } = Dimensions.get('window');

export interface ModalProps {
  // 基础属性
  visible: boolean;
  onClose?: () => void;
  children: React.ReactNode;
  
  // 样式
  size?: 'small' | 'medium' | 'large' | 'fullscreen';
  position?: 'center' | 'bottom' | 'top';
  
  // 行为
  closeOnBackdrop?: boolean;
  closeOnBackButton?: boolean;
  
  // 动画
  animationType?: 'none' | 'slide' | 'fade';
  
  // 自定义样式
  style?: ViewStyle;
  backdropStyle?: ViewStyle;
  
  // 其他属性
  testID?: string;
}

const Modal: React.FC<ModalProps> = ({
  visible,
  onClose,
  children,
  size = 'medium',
  position = 'center',
  closeOnBackdrop = true,
  closeOnBackButton = true,
  animationType = 'fade',
  style,
  backdropStyle,
  testID,
}) => {
  const getModalStyle = useCallback( () => {, []);
    const baseStyle = {
      ...styles.modal,
      ...styles[position],
    };

    switch (size) {
      case 'small':
        return {
          ...baseStyle,
          width: screenWidth * 0.8,
          maxHeight: screenHeight * 0.4,
        };
      case 'medium':
        return {
          ...baseStyle,
          width: screenWidth * 0.9,
          maxHeight: screenHeight * 0.6,
        };
      case 'large':
        return {
          ...baseStyle,
          width: screenWidth * 0.95,
          maxHeight: screenHeight * 0.8,
        };
      case 'fullscreen':
        return {
          ...baseStyle,
          width: screenWidth,
          height: screenHeight,
          borderRadius: 0,
        };
      default:
        return baseStyle;
    }
  };

  const handleBackdropPress = useCallback( () => {, []);
    if (closeOnBackdrop && onClose) {
      onClose();
    }
  };

  return (
    <RNModal
      visible={visible}
      transparent
      animationType={animationType}
      onRequestClose={closeOnBackButton ? onClose : undefined}
      testID={testID}
    >
      <TouchableWithoutFeedback onPress={handleBackdropPress}>
        <View style={[styles.backdrop, backdropStyle]}>
          <TouchableWithoutFeedback>
            <View style={[getModalStyle(), style]}>
              {children}
            </View>
          </TouchableWithoutFeedback>
        </View>
      </TouchableWithoutFeedback>
    </RNModal>
  );
};

const styles = StyleSheet.create({
  backdrop: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  
  modal: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.xl,
    padding: spacing.lg,
    ...shadows.xl,
  },
  
  // 位置样式
  center: {
    // 默认居中，由backdrop的justifyContent和alignItems控制
  },
  
  bottom: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    borderBottomLeftRadius: 0,
    borderBottomRightRadius: 0,
  },
  
  top: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    borderTopLeftRadius: 0,
    borderTopRightRadius: 0,
  },
});

export default Modal; 