import React, { useCallback, useRef, useState } from 'react';
import {
    Alert,
    Animated,
    Dimensions,
    FlatList,
    Image,
    StyleSheet,
    Text,
    TouchableOpacity,
    View,
} from 'react-native';
import { useTheme } from '../../contexts/ThemeContext';
import { Button } from './Button';
import { Modal } from './Modal';
import { Progress } from './Progress';

export interface FileItem {
  id: string;
  name: string;
  size: number;
  type: string;
  uri: string;
  uploadProgress?: number;
  uploadStatus?: 'pending' | 'uploading' | 'success' | 'error';
  error?: string;
}

export interface FileUploadProps {
  /** 是否允许多文件选择 */
  multiple?: boolean;
  /** 允许的文件类型 */
  accept?: string[];
  /** 最大文件大小（字节） */
  maxSize?: number;
  /** 最大文件数量 */
  maxFiles?: number;
  /** 是否显示预览 */
  showPreview?: boolean;
  /** 是否支持拖拽上传 */
  dragAndDrop?: boolean;
  /** 上传函数 */
  onUpload?: (files: FileItem[]) => Promise<void>;
  /** 文件选择回调 */
  onFilesChange?: (files: FileItem[]) => void;
  /** 文件删除回调 */
  onFileRemove?: (fileId: string) => void;
  /** 自定义样式 */
  style?: any;
  /** 是否禁用 */
  disabled?: boolean;
  /** 占位文本 */
  placeholder?: string;
}

export const FileUpload: React.FC<FileUploadProps> = ({
  multiple = false,
  accept = [],
  maxSize = 10 * 1024 * 1024, // 10MB
  maxFiles = 5,
  showPreview = true,
  dragAndDrop = true,
  onUpload,
  onFilesChange,
  onFileRemove,
  style,
  disabled = false,
  placeholder = '点击选择文件或拖拽文件到此处',
}) => {
  const { theme } = useTheme();
  const [files, setFiles] = useState<FileItem[]>([]);
  const [isDragOver, setIsDragOver] = useState(false);
  const [previewFile, setPreviewFile] = useState<FileItem | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const dragAnimation = useRef(new Animated.Value(0)).current;

  const styles = createStyles(theme);

  // 格式化文件大小
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // 验证文件
  const validateFile = (file: any): string | null => {
    if (accept.length > 0 && !accept.includes(file.type)) {
      return `不支持的文件类型: ${file.type}`;
    }
    if (file.size > maxSize) {
      return `文件大小超过限制: ${formatFileSize(maxSize)}`;
    }
    return null;
  };

  // 处理文件选择
  const handleFileSelect = useCallback(async () => {
    if (disabled) return;

    try {
      // 这里应该使用 react-native-document-picker 或类似库
      // 为了演示，我们模拟文件选择
      const mockFile: FileItem = {
        id: Date.now().toString(),
        name: 'example.jpg',
        size: 1024 * 1024, // 1MB
        type: 'image/jpeg',
        uri: 'https://via.placeholder.com/300x200',
        uploadStatus: 'pending',
      };

      const error = validateFile(mockFile);
      if (error) {
        Alert.alert('文件验证失败', error);
        return;
      }

      const newFiles = multiple ? [...files, mockFile] : [mockFile];
      
      if (newFiles.length > maxFiles) {
        Alert.alert('文件数量超限', `最多只能选择 ${maxFiles} 个文件`);
        return;
      }

      setFiles(newFiles);
      onFilesChange?.(newFiles);
    } catch (error) {
      Alert.alert('文件选择失败', '请重试');
    }
  }, [disabled, files, multiple, maxFiles, onFilesChange, accept, maxSize]);

  // 处理文件删除
  const handleFileRemove = useCallback((fileId: string) => {
    const newFiles = files.filter(file => file.id !== fileId);
    setFiles(newFiles);
    onFilesChange?.(newFiles);
    onFileRemove?.(fileId);
  }, [files, onFilesChange, onFileRemove]);

  // 处理文件上传
  const handleUpload = useCallback(async () => {
    if (!onUpload || files.length === 0 || isUploading) return;

    setIsUploading(true);
    
    try {
      // 更新文件状态为上传中
      const uploadingFiles = files.map(file => ({
        ...file,
        uploadStatus: 'uploading' as const,
        uploadProgress: 0,
      }));
      setFiles(uploadingFiles);

      // 模拟上传进度
      for (let i = 0; i <= 100; i += 10) {
        await new Promise(resolve => setTimeout(resolve, 100));
        setFiles(prev => prev.map(file => ({
          ...file,
          uploadProgress: i,
        })));
      }

      // 调用上传函数
      await onUpload(files);

      // 更新文件状态为成功
      setFiles(prev => prev.map(file => ({
        ...file,
        uploadStatus: 'success' as const,
        uploadProgress: 100,
      })));
    } catch (error) {
      // 更新文件状态为失败
      setFiles(prev => prev.map(file => ({
        ...file,
        uploadStatus: 'error' as const,
        error: error instanceof Error ? error.message : '上传失败',
      })));
    } finally {
      setIsUploading(false);
    }
  }, [onUpload, files, isUploading]);

  // 渲染文件项
  const renderFileItem = ({ item }: { item: FileItem }) => (
    <View style={styles.fileItem}>
      {showPreview && item.type.startsWith('image/') && (
        <TouchableOpacity
          onPress={() => setPreviewFile(item)}
          style={styles.filePreview}
        >
          <Image source={{ uri: item.uri }} style={styles.previewImage} />
        </TouchableOpacity>
      )}
      
      <View style={styles.fileInfo}>
        <Text style={styles.fileName} numberOfLines={1}>
          {item.name}
        </Text>
        <Text style={styles.fileSize}>
          {formatFileSize(item.size)}
        </Text>
        
        {item.uploadStatus === 'uploading' && (
          <Progress
            value={item.uploadProgress || 0}
            size="sm"
            style={styles.uploadProgress}
          />
        )}
        
        {item.uploadStatus === 'error' && (
          <Text style={styles.errorText}>
            {item.error || '上传失败'}
          </Text>
        )}
      </View>
      
      <View style={styles.fileActions}>
        {item.uploadStatus === 'success' && (
          <Text style={styles.successText}>✓</Text>
        )}
        <TouchableOpacity
          onPress={() => handleFileRemove(item.id)}
          style={styles.removeButton}
          disabled={isUploading}
        >
          <Text style={styles.removeButtonText}>×</Text>
        </TouchableOpacity>
      </View>
    </View>
  );

  const dragStyle = {
    borderColor: dragAnimation.interpolate({
      inputRange: [0, 1],
      outputRange: [theme.colors.border, theme.colors.primary],
    }),
    backgroundColor: dragAnimation.interpolate({
      inputRange: [0, 1],
      outputRange: [theme.colors.surface, theme.colors.primary + '10'],
    }),
  };

  return (
    <View style={[styles.container, style]}>
      {/* 上传区域 */}
      <Animated.View style={[styles.uploadArea, dragStyle]}>
        <TouchableOpacity
          onPress={handleFileSelect}
          style={styles.uploadButton}
          disabled={disabled}
          activeOpacity={0.7}
        >
          <Text style={styles.uploadIcon}>📁</Text>
          <Text style={styles.uploadText}>
            {placeholder}
          </Text>
          <Text style={styles.uploadHint}>
            {accept.length > 0 && `支持格式: ${accept.join(', ')}`}
            {maxSize && ` • 最大 ${formatFileSize(maxSize)}`}
            {multiple && ` • 最多 ${maxFiles} 个文件`}
          </Text>
        </TouchableOpacity>
      </Animated.View>

      {/* 文件列表 */}
      {files.length > 0 && (
        <View style={styles.fileList}>
          <FlatList
            data={files}
            renderItem={renderFileItem}
            keyExtractor={(item) => item.id}
            showsVerticalScrollIndicator={false}
          />
          
          {/* 上传按钮 */}
          {onUpload && (
            <Button
              title={isUploading ? '上传中...' : '开始上传'}
              onPress={handleUpload}
              disabled={isUploading || files.every(f => f.uploadStatus === 'success')}
              style={styles.uploadActionButton}
              loading={isUploading}
            />
          )}
        </View>
      )}

      {/* 预览模态框 */}
      {previewFile && (
        <Modal
          visible={!!previewFile}
          onClose={() => setPreviewFile(null)}
          title="文件预览"
        >
          <View style={styles.previewModal}>
            <Image
              source={{ uri: previewFile.uri }}
              style={styles.previewModalImage}
              resizeMode="contain"
            />
            <Text style={styles.previewFileName}>
              {previewFile.name}
            </Text>
            <Text style={styles.previewFileSize}>
              {formatFileSize(previewFile.size)}
            </Text>
          </View>
        </Modal>
      )}
    </View>
  );
};

const createStyles = (theme: any) => {
  const { width } = Dimensions.get('window');
  
  return StyleSheet.create({
    container: {
      flex: 1,
    },
    uploadArea: {
      borderWidth: 2,
      borderStyle: 'dashed',
      borderRadius: theme.borderRadius.lg,
      padding: theme.spacing.xl,
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: 120,
    },
    uploadButton: {
      alignItems: 'center',
      justifyContent: 'center',
    },
    uploadIcon: {
      fontSize: 32,
      marginBottom: theme.spacing.sm,
    },
    uploadText: {
      fontSize: theme.typography.body1.fontSize,
      fontWeight: theme.typography.body1.fontWeight,
      color: theme.colors.text,
      textAlign: 'center',
      marginBottom: theme.spacing.xs,
    },
    uploadHint: {
      fontSize: theme.typography.caption.fontSize,
      color: theme.colors.textSecondary,
      textAlign: 'center',
    },
    fileList: {
      marginTop: theme.spacing.lg,
    },
    fileItem: {
      flexDirection: 'row',
      alignItems: 'center',
      padding: theme.spacing.md,
      backgroundColor: theme.colors.surface,
      borderRadius: theme.borderRadius.md,
      marginBottom: theme.spacing.sm,
      borderWidth: 1,
      borderColor: theme.colors.border,
    },
    filePreview: {
      marginRight: theme.spacing.md,
    },
    previewImage: {
      width: 40,
      height: 40,
      borderRadius: theme.borderRadius.sm,
    },
    fileInfo: {
      flex: 1,
    },
    fileName: {
      fontSize: theme.typography.body2.fontSize,
      fontWeight: theme.typography.body2.fontWeight,
      color: theme.colors.text,
      marginBottom: theme.spacing.xs,
    },
    fileSize: {
      fontSize: theme.typography.caption.fontSize,
      color: theme.colors.textSecondary,
    },
    uploadProgress: {
      marginTop: theme.spacing.xs,
    },
    errorText: {
      fontSize: theme.typography.caption.fontSize,
      color: theme.colors.error,
      marginTop: theme.spacing.xs,
    },
    fileActions: {
      flexDirection: 'row',
      alignItems: 'center',
    },
    successText: {
      fontSize: 16,
      color: theme.colors.success,
      marginRight: theme.spacing.sm,
    },
    removeButton: {
      width: 24,
      height: 24,
      borderRadius: 12,
      backgroundColor: theme.colors.error,
      alignItems: 'center',
      justifyContent: 'center',
    },
    removeButtonText: {
      color: theme.colors.onError,
      fontSize: 16,
      fontWeight: 'bold',
    },
    uploadActionButton: {
      marginTop: theme.spacing.lg,
    },
    previewModal: {
      alignItems: 'center',
      padding: theme.spacing.lg,
    },
    previewModalImage: {
      width: width - 80,
      height: 300,
      borderRadius: theme.borderRadius.md,
      marginBottom: theme.spacing.md,
    },
    previewFileName: {
      fontSize: theme.typography.h6.fontSize,
      fontWeight: theme.typography.h6.fontWeight,
      color: theme.colors.text,
      marginBottom: theme.spacing.xs,
      textAlign: 'center',
    },
    previewFileSize: {
      fontSize: theme.typography.body2.fontSize,
      color: theme.colors.textSecondary,
      textAlign: 'center',
    },
  });
};

// 默认导出
export default FileUpload;

// 导出类型
export type { FileItem, FileUploadProps };
