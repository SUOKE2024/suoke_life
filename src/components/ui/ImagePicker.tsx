import React, { useState } from 'react';
import {
    Alert,
    Dimensions,
    Image,
    ImageStyle,
    Modal,
    StyleSheet,
    Text,
    TextStyle,
    TouchableOpacity,
    View,
    ViewStyle,
} from 'react-native';
import { useTheme } from '../../contexts/ThemeContext';

export interface ImagePickerProps {
  value?: string[];
  defaultValue?: string[];
  onChange?: (images: string[]) => void;
  maxCount?: number;
  maxSize?: number; // MB
  quality?: number; // 0-1
  allowedTypes?: string[];
  multiple?: boolean;
  showPreview?: boolean;
  previewSize?: number;
  placeholder?: string;
  disabled?: boolean;
  style?: ViewStyle;
  buttonStyle?: ViewStyle;
  buttonTextStyle?: TextStyle;
  previewStyle?: ViewStyle;
  imageStyle?: ImageStyle;
  accessible?: boolean;
  testID?: string;
}

export const ImagePicker: React.FC<ImagePickerProps> = ({
  value,
  defaultValue = [],
  onChange,
  maxCount = 9,
  maxSize = 10,
  quality = 0.8,
  allowedTypes = ['image/jpeg', 'image/png', 'image/gif'],
  multiple = true,
  showPreview = true,
  previewSize = 80,
  placeholder = '选择图片',
  disabled = false,
  style,
  buttonStyle,
  buttonTextStyle,
  previewStyle,
  imageStyle,
  accessible = true,
  testID,
}) => {
  const { currentTheme } = useTheme();
  const [images, setImages] = useState<string[]>(value || defaultValue);
  const [modalVisible, setModalVisible] = useState(false);
  const [previewImage, setPreviewImage] = useState<string | null>(null);

  const screenWidth = Dimensions.get('window').width;

  // 模拟图片选择功能
  const selectImages = () => {
    if (disabled) return;

    Alert.alert(
      '选择图片',
      '请选择图片来源',
      [
        { text: '取消', style: 'cancel' },
        { text: '相机', onPress: () => openCamera() },
        { text: '相册', onPress: () => openGallery() },
      ]
    );
  };

  const openCamera = () => {
    const mockImage = `https://picsum.photos/400/400?random=${Date.now()}`;
    addImage(mockImage);
  };

  const openGallery = () => {
    const mockImages = Array.from({ length: multiple ? Math.min(3, maxCount - images.length) : 1 }, 
      (_, index) => `https://picsum.photos/400/400?random=${Date.now() + index}`
    );
    
    if (multiple) {
      addImages(mockImages);
    } else {
      setImages(mockImages);
      onChange?.(mockImages);
    }
  };

  const addImage = (imageUri: string) => {
    if (images.length >= maxCount) {
      Alert.alert('提示', `最多只能选择${maxCount}张图片`);
      return;
    }

    const newImages = multiple ? [...images, imageUri] : [imageUri];
    setImages(newImages);
    onChange?.(newImages);
  };

  const addImages = (imageUris: string[]) => {
    const availableSlots = maxCount - images.length;
    const imagesToAdd = imageUris.slice(0, availableSlots);
    
    if (imageUris.length > availableSlots) {
      Alert.alert('提示', `最多只能选择${maxCount}张图片，已为您选择前${availableSlots}张`);
    }

    const newImages = [...images, ...imagesToAdd];
    setImages(newImages);
    onChange?.(newImages);
  };

  const removeImage = (index: number) => {
    const newImages = images.filter((_, i) => i !== index);
    setImages(newImages);
    onChange?.(newImages);
  };

  const previewImageModal = (imageUri: string) => {
    setPreviewImage(imageUri);
    setModalVisible(true);
  };

  const styles = StyleSheet.create({
    container: {
      backgroundColor: currentTheme.colors.surface,
    },
    previewContainer: {
      flexDirection: 'row',
      flexWrap: 'wrap',
      gap: 8,
    },
    addButton: {
      backgroundColor: currentTheme.colors.surfaceVariant,
      borderRadius: 8,
      borderWidth: 2,
      borderColor: currentTheme.colors.outline,
      borderStyle: 'dashed',
      justifyContent: 'center',
      alignItems: 'center',
      opacity: disabled ? 0.5 : 1,
    },
    addButtonText: {
      fontSize: 24,
      color: currentTheme.colors.onSurfaceVariant,
      marginBottom: 4,
    },
    addButtonLabel: {
      fontSize: 12,
      color: currentTheme.colors.onSurfaceVariant,
      textAlign: 'center',
    },
    imageContainer: {
      position: 'relative',
      borderRadius: 8,
      overflow: 'hidden',
    },
    imageButton: {
      width: '100%',
      height: '100%',
    },
    image: {
      borderRadius: 8,
    },
    removeButton: {
      position: 'absolute',
      top: -8,
      right: -8,
      width: 24,
      height: 24,
      borderRadius: 12,
      backgroundColor: currentTheme.colors.error,
      justifyContent: 'center',
      alignItems: 'center',
      elevation: 2,
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.25,
      shadowRadius: 3.84,
    },
    removeButtonText: {
      color: '#ffffff',
      fontSize: 16,
      fontWeight: 'bold',
      lineHeight: 16,
    },
    modal: {
      flex: 1,
      backgroundColor: 'rgba(0, 0, 0, 0.9)',
      justifyContent: 'center',
      alignItems: 'center',
    },
    modalContent: {
      width: screenWidth * 0.9,
      height: screenWidth * 0.9,
      backgroundColor: currentTheme.colors.surface,
      borderRadius: 8,
      overflow: 'hidden',
    },
    modalImage: {
      width: '100%',
      height: '100%',
    },
    modalHeader: {
      position: 'absolute',
      top: 0,
      left: 0,
      right: 0,
      height: 60,
      backgroundColor: 'rgba(0, 0, 0, 0.5)',
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      paddingHorizontal: 16,
      zIndex: 1,
    },
    modalTitle: {
      color: '#ffffff',
      fontSize: 16,
      fontWeight: '600',
    },
    modalCloseButton: {
      width: 32,
      height: 32,
      borderRadius: 16,
      backgroundColor: 'rgba(255, 255, 255, 0.2)',
      justifyContent: 'center',
      alignItems: 'center',
    },
    modalCloseText: {
      color: '#ffffff',
      fontSize: 18,
      fontWeight: 'bold',
    },
    infoContainer: {
      marginTop: 8,
      padding: 8,
      backgroundColor: currentTheme.colors.surfaceVariant,
      borderRadius: 4,
    },
    infoText: {
      fontSize: 12,
      color: currentTheme.colors.onSurfaceVariant,
      textAlign: 'center',
    },
  });

  const renderAddButton = () => {
    if (images.length >= maxCount) return null;

    return (
      <TouchableOpacity
        style={[styles.addButton, { width: previewSize, height: previewSize }, buttonStyle]}
        onPress={selectImages}
        disabled={disabled}
        accessible={accessible}
        accessibilityRole="button"
        accessibilityLabel={placeholder}
      >
        <Text style={[styles.addButtonText, buttonTextStyle]}>+</Text>
        <Text style={[styles.addButtonLabel, buttonTextStyle]}>{placeholder}</Text>
      </TouchableOpacity>
    );
  };

  const renderImagePreview = (imageUri: string, index: number) => {
    return (
      <View key={index} style={[styles.imageContainer, { width: previewSize, height: previewSize }]}>
        <TouchableOpacity
          onPress={() => previewImageModal(imageUri)}
          style={styles.imageButton}
        >
          <Image
            source={{ uri: imageUri }}
            style={[styles.image, { width: previewSize, height: previewSize }, imageStyle]}
            resizeMode="cover"
          />
        </TouchableOpacity>
        
        <TouchableOpacity
          style={styles.removeButton}
          onPress={() => removeImage(index)}
          accessible={accessible}
          accessibilityRole="button"
          accessibilityLabel={`删除第${index + 1}张图片`}
        >
          <Text style={styles.removeButtonText}>×</Text>
        </TouchableOpacity>
      </View>
    );
  };

  return (
    <View style={[styles.container, style]} testID={testID}>
      {showPreview && (
        <View style={[styles.previewContainer, previewStyle]}>
          {images.map((imageUri, index) => renderImagePreview(imageUri, index))}
          {renderAddButton()}
        </View>
      )}

      {!showPreview && (
        <TouchableOpacity
          style={[styles.addButton, { height: 48 }, buttonStyle]}
          onPress={selectImages}
          disabled={disabled}
          accessible={accessible}
          accessibilityRole="button"
          accessibilityLabel={placeholder}
        >
          <Text style={[styles.addButtonLabel, buttonTextStyle]}>{placeholder}</Text>
        </TouchableOpacity>
      )}

      <View style={styles.infoContainer}>
        <Text style={styles.infoText}>
          已选择 {images.length}/{maxCount} 张图片
          {maxSize && ` • 单张图片不超过 ${maxSize}MB`}
        </Text>
      </View>

      <Modal
        visible={modalVisible}
        transparent
        animationType="fade"
        onRequestClose={() => setModalVisible(false)}
      >
        <View style={styles.modal}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>图片预览</Text>
              <TouchableOpacity
                style={styles.modalCloseButton}
                onPress={() => setModalVisible(false)}
                accessible={accessible}
                accessibilityRole="button"
                accessibilityLabel="关闭预览"
              >
                <Text style={styles.modalCloseText}>×</Text>
              </TouchableOpacity>
            </View>
            
            {previewImage && (
              <Image
                source={{ uri: previewImage }}
                style={styles.modalImage}
                resizeMode="contain"
              />
            )}
          </View>
        </View>
      </Modal>
    </View>
  );
};

export default ImagePicker; 