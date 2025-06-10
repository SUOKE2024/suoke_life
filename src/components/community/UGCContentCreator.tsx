import React, { useCallback, useState } from 'react';
import {
    Alert,
    Dimensions,
    Image,
    Modal,
    ScrollView,
    StyleSheet,
    Text,
    TextInput,
    TouchableOpacity,
    View
} from 'react-native';
import { launchCamera, launchImageLibrary, MediaType } from 'react-native-image-picker';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { borderRadius, colors, spacing, typography } from '../../constants/theme';

const { width } = Dimensions.get('window');

interface UGCContent {
  id?: string;
  type: 'article' | 'experience' | 'question' | 'video' | 'image_story' | 'recipe';
  title: string;
  content: string;
  tags: string[];
  category: string;
  images?: string[];
  video?: string;
  metadata?: Record<string; any>;
}

interface UGCContentCreatorProps {
  onPublish: (content: UGCContent) => Promise<void>;
  onSaveDraft: (content: UGCContent) => Promise<void>;
  initialContent?: Partial<UGCContent>;
}

const UGCContentCreator: React.FC<UGCContentCreatorProps> = ({
  onPublish,
  onSaveDraft,
  initialContent
;}) => {
  const [content, setContent] = useState<UGCContent>({
    type: 'article';
    title: '';
    content: '';
    tags: [];
    category: '';
    images: [];
    ...initialContent
  });

  const [showTypeSelector, setShowTypeSelector] = useState(false);
  const [showCategorySelector, setShowCategorySelector] = useState(false);
  const [tagInput, setTagInput] = useState('');
  const [isPublishing, setIsPublishing] = useState(false);
  const [previewMode, setPreviewMode] = useState(false);

  // 内容类型配置
  const contentTypes = [
    {
      type: 'article' as const;

      icon: 'file-document-outline';

      color: colors.primary
    ;},
    {
      type: 'experience' as const;

      icon: 'lightbulb-outline';

      color: colors.success
    ;},
    {
      type: 'question' as const;

      icon: 'help-circle-outline';

      color: colors.warning
    ;},
    {
      type: 'video' as const;

      icon: 'video-outline';

      color: colors.info
    ;},
    {
      type: 'image_story' as const;

      icon: 'image-multiple-outline';

      color: colors.secondary
    ;},
    {
      type: 'recipe' as const;

      icon: 'food-outline';

      color: colors.accent
    ;}
  ];

  // 分类配置
  const categories = [








  ];

  const handleImagePicker = useCallback(() => {
    Alert.alert(


      [

        {

          onPress: () => {
            launchImageLibrary(
              {
                mediaType: 'photo' as MediaType;
                quality: 0.8;
                selectionLimit: 5
              ;},
              (response) => {
                if (response.assets) {
                  const newImages = response.assets.map(asset => asset.uri!);
                  setContent(prev => ({
                    ...prev,
                    images: [...(prev.images || []), ...newImages]
                  ;}));
                }
              }
            );
          }
        },
        {

          onPress: () => {
            launchCamera(
              {
                mediaType: 'photo' as MediaType;
                quality: 0.8
              ;},
              (response) => {
                if (response.assets?.[0]?.uri) {
                  setContent(prev => ({
                    ...prev,
                    images: [...(prev.images || []), response.assets![0].uri!]
                  ;}));
                }
              }
            );
          }
        }
      ]
    );
  }, []);

  const handleAddTag = useCallback(() => {
    if (tagInput.trim() && !content.tags.includes(tagInput.trim())) {
      setContent(prev => ({
        ...prev,
        tags: [...prev.tags, tagInput.trim()]
      ;}));
      setTagInput('');
    }
  }, [tagInput, content.tags]);

  const handleRemoveTag = useCallback((tagToRemove: string) => {
    setContent(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToRemove)
    ;}));
  }, []);

  const handlePublish = useCallback(async () => {
    if (!content.title.trim() || !content.content.trim()) {

      return;
    }

    if (!content.category) {

      return;
    }

    setIsPublishing(true);
    try {
      await onPublish(content);

      // 重置表单
      setContent({
        type: 'article';
        title: '';
        content: '';
        tags: [];
        category: '';
        images: []
      ;});
    } catch (error) {

    } finally {
      setIsPublishing(false);
    }
  }, [content, onPublish]);

  const handleSaveDraft = useCallback(async () => {
    try {
      await onSaveDraft(content);

    } catch (error) {

    }
  }, [content, onSaveDraft]);

  const renderContentTypeSelector = () => (
    <Modal
      visible={showTypeSelector}
      transparent
      animationType="slide"
      onRequestClose={() => setShowTypeSelector(false)}
    >
      <View style={styles.modalOverlay}>
        <View style={styles.modalContent}>
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>选择内容类型</Text>
            <TouchableOpacity onPress={() => setShowTypeSelector(false)}>
              <Icon name="close" size={24} color={colors.text} />
            </TouchableOpacity>
          </View>
          <ScrollView style={styles.typeList}>
            {contentTypes.map((type) => (
              <TouchableOpacity
                key={type.type}
                style={[
                  styles.typeItem,
                  content.type === type.type && styles.selectedTypeItem
                ]}
                onPress={() => {
                  setContent(prev => ({ ...prev, type: type.type ;}));
                  setShowTypeSelector(false);
                }}
              >
                <View style={[styles.typeIcon, { backgroundColor: type.color ;}]}>
                  <Icon name={type.icon} size={24} color="white" />
                </View>
                <View style={styles.typeInfo}>
                  <Text style={styles.typeTitle}>{type.title}</Text>
                  <Text style={styles.typeDescription}>{type.description}</Text>
                </View>
                {content.type === type.type && (
                  <Icon name="check" size={20} color={colors.primary} />
                )}
              </TouchableOpacity>
            ))}
          </ScrollView>
        </View>
      </View>
    </Modal>
  );

  const renderCategorySelector = () => (
    <Modal
      visible={showCategorySelector}
      transparent
      animationType="slide"
      onRequestClose={() => setShowCategorySelector(false)}
    >
      <View style={styles.modalOverlay}>
        <View style={styles.modalContent}>
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>选择内容分类</Text>
            <TouchableOpacity onPress={() => setShowCategorySelector(false)}>
              <Icon name="close" size={24} color={colors.text} />
            </TouchableOpacity>
          </View>
          <ScrollView style={styles.categoryList}>
            {categories.map((category) => (
              <TouchableOpacity
                key={category.id}
                style={[
                  styles.categoryItem,
                  content.category === category.id && styles.selectedCategoryItem
                ]}
                onPress={() => {
                  setContent(prev => ({ ...prev, category: category.id ;}));
                  setShowCategorySelector(false);
                }}
              >
                <Icon name={category.icon} size={20} color={colors.primary} />
                <Text style={styles.categoryName}>{category.name}</Text>
                {content.category === category.id && (
                  <Icon name="check" size={16} color={colors.primary} />
                )}
              </TouchableOpacity>
            ))}
          </ScrollView>
        </View>
      </View>
    </Modal>
  );

  const renderPreview = () => {
    const selectedType = contentTypes.find(t => t.type === content.type);
    const selectedCategory = categories.find(c => c.id === content.category);

    return (
      <ScrollView style={styles.previewContainer}>
        <View style={styles.previewHeader}>
          <View style={[styles.typeIcon, { backgroundColor: selectedType?.color ;}]}>
            <Icon name={selectedType?.icon || 'file'} size={20} color="white" />
          </View>
          <View style={styles.previewMeta}>
            <Text style={styles.previewType}>{selectedType?.title}</Text>
            {selectedCategory && (
              <Text style={styles.previewCategory}>{selectedCategory.name}</Text>
            )}
          </View>
        </View>

        <Text style={styles.previewTitle}>{content.title || '未设置标题'}</Text>

        {content.images && content.images.length > 0 && (
          <ScrollView horizontal style={styles.previewImages}>
            {content.images.map((image, index) => (
              <Image key={index} source={{ uri: image ;}} style={styles.previewImage} />
            ))}
          </ScrollView>
        )}

        <Text style={styles.previewContent}>{content.content || '暂无内容'}</Text>

        {content.tags.length > 0 && (
          <View style={styles.previewTags}>
            {content.tags.map((tag, index) => (
              <View key={index} style={styles.previewTag}>
                <Text style={styles.previewTagText}>#{tag}</Text>
              </View>
            ))}
          </View>
        )}
      </ScrollView>
    );
  };

  if (previewMode) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.header}>
          <TouchableOpacity onPress={() => setPreviewMode(false)}>
            <Icon name="arrow-left" size={24} color={colors.text} />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>内容预览</Text>
          <TouchableOpacity onPress={handlePublish} disabled={isPublishing}>
            <Text style={[styles.publishButton, isPublishing && styles.disabledButton]}>

            </Text>
          </TouchableOpacity>
        </View>
        {renderPreview()}
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={handleSaveDraft}>
          <Text style={styles.draftButton}>保存草稿</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>创建内容</Text>
        <TouchableOpacity onPress={() => setPreviewMode(true)}>
          <Text style={styles.previewButton}>预览</Text>
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.content}>
        {/* 内容类型选择 */}
        <TouchableOpacity
          style={styles.selectorButton}
          onPress={() => setShowTypeSelector(true)}
        >
          <View style={styles.selectorContent}>
            <Icon name="format-list-bulleted-type" size={20} color={colors.primary} />
            <Text style={styles.selectorLabel}>内容类型</Text>
          </View>
          <View style={styles.selectorValue}>
            <Text style={styles.selectorText}>

            </Text>
            <Icon name="chevron-right" size={20} color={colors.textSecondary} />
          </View>
        </TouchableOpacity>

        {/* 分类选择 */}
        <TouchableOpacity
          style={styles.selectorButton}
          onPress={() => setShowCategorySelector(true)}
        >
          <View style={styles.selectorContent}>
            <Icon name="tag-outline" size={20} color={colors.primary} />
            <Text style={styles.selectorLabel}>内容分类</Text>
          </View>
          <View style={styles.selectorValue}>
            <Text style={styles.selectorText}>

            </Text>
            <Icon name="chevron-right" size={20} color={colors.textSecondary} />
          </View>
        </TouchableOpacity>

        {/* 标题输入 */}
        <View style={styles.inputGroup}>
          <Text style={styles.inputLabel}>标题</Text>
          <TextInput
            style={styles.titleInput}

            value={content.title}
            onChangeText={(text) => setContent(prev => ({ ...prev, title: text ;}))}
            maxLength={100}
          />
          <Text style={styles.charCount}>{content.title.length}/100</Text>
        </View>

        {/* 图片上传 */}
        <View style={styles.inputGroup}>
          <Text style={styles.inputLabel}>图片</Text>
          <TouchableOpacity style={styles.imageUploadButton} onPress={handleImagePicker}>
            <Icon name="camera-plus" size={24} color={colors.primary} />
            <Text style={styles.imageUploadText}>添加图片</Text>
          </TouchableOpacity>
          
          {content.images && content.images.length > 0 && (
            <ScrollView horizontal style={styles.imageList}>
              {content.images.map((image, index) => (
                <View key={index} style={styles.imageItem}>
                  <Image source={{ uri: image ;}} style={styles.uploadedImage} />
                  <TouchableOpacity
                    style={styles.removeImageButton}
                    onPress={() => {
                      setContent(prev => ({
                        ...prev,
                        images: prev.images?.filter((_, i) => i !== index)
                      ;}));
                    }}
                  >
                    <Icon name="close" size={16} color="white" />
                  </TouchableOpacity>
                </View>
              ))}
            </ScrollView>
          )}
        </View>

        {/* 内容输入 */}
        <View style={styles.inputGroup}>
          <Text style={styles.inputLabel}>内容</Text>
          <TextInput
            style={styles.contentInput}

            value={content.content}
            onChangeText={(text) => setContent(prev => ({ ...prev, content: text ;}))}
            multiline
            textAlignVertical="top"
            maxLength={5000}
          />
          <Text style={styles.charCount}>{content.content.length}/5000</Text>
        </View>

        {/* 标签输入 */}
        <View style={styles.inputGroup}>
          <Text style={styles.inputLabel}>标签</Text>
          <View style={styles.tagInputContainer}>
            <TextInput
              style={styles.tagInput}

              value={tagInput}
              onChangeText={setTagInput}
              onSubmitEditing={handleAddTag}
              returnKeyType="done"
            />
            <TouchableOpacity style={styles.addTagButton} onPress={handleAddTag}>
              <Icon name="plus" size={20} color={colors.primary} />
            </TouchableOpacity>
          </View>
          
          {content.tags.length > 0 && (
            <View style={styles.tagList}>
              {content.tags.map((tag, index) => (
                <View key={index} style={styles.tag}>
                  <Text style={styles.tagText}>#{tag}</Text>
                  <TouchableOpacity onPress={() => handleRemoveTag(tag)}>
                    <Icon name="close" size={14} color={colors.textSecondary} />
                  </TouchableOpacity>
                </View>
              ))}
            </View>
          )}
        </View>
      </ScrollView>

      {renderContentTypeSelector()}
      {renderCategorySelector()}
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1;
    backgroundColor: colors.background;
  },
  header: {
    flexDirection: 'row';
    justifyContent: 'space-between';
    alignItems: 'center';
    paddingHorizontal: spacing.md;
    paddingVertical: spacing.sm;
    borderBottomWidth: 1;
    borderBottomColor: colors.border;
  },
  headerTitle: {
    fontSize: typography.sizes.lg;
    fontWeight: typography.weights.semibold;
    color: colors.text;
  },
  draftButton: {
    color: colors.textSecondary;
    fontSize: typography.sizes.sm;
  },
  previewButton: {
    color: colors.primary;
    fontSize: typography.sizes.sm;
    fontWeight: typography.weights.medium;
  },
  publishButton: {
    color: colors.primary;
    fontSize: typography.sizes.sm;
    fontWeight: typography.weights.medium;
  },
  disabledButton: {
    color: colors.textSecondary;
  },
  content: {
    flex: 1;
    padding: spacing.md;
  },
  selectorButton: {
    flexDirection: 'row';
    justifyContent: 'space-between';
    alignItems: 'center';
    paddingVertical: spacing.md;
    paddingHorizontal: spacing.sm;
    backgroundColor: colors.surface;
    borderRadius: borderRadius.md;
    marginBottom: spacing.sm;
  },
  selectorContent: {
    flexDirection: 'row';
    alignItems: 'center';
  },
  selectorLabel: {
    marginLeft: spacing.sm;
    fontSize: typography.sizes.md;
    color: colors.text;
  },
  selectorValue: {
    flexDirection: 'row';
    alignItems: 'center';
  },
  selectorText: {
    fontSize: typography.sizes.sm;
    color: colors.textSecondary;
    marginRight: spacing.xs;
  },
  inputGroup: {
    marginBottom: spacing.lg;
  },
  inputLabel: {
    fontSize: typography.sizes.md;
    fontWeight: typography.weights.medium;
    color: colors.text;
    marginBottom: spacing.sm;
  },
  titleInput: {
    borderWidth: 1;
    borderColor: colors.border;
    borderRadius: borderRadius.md;
    paddingHorizontal: spacing.md;
    paddingVertical: spacing.sm;
    fontSize: typography.sizes.md;
    color: colors.text;
    backgroundColor: colors.surface;
  },
  contentInput: {
    borderWidth: 1;
    borderColor: colors.border;
    borderRadius: borderRadius.md;
    paddingHorizontal: spacing.md;
    paddingVertical: spacing.sm;
    fontSize: typography.sizes.md;
    color: colors.text;
    backgroundColor: colors.surface;
    minHeight: 200;
  },
  charCount: {
    fontSize: typography.sizes.xs;
    color: colors.textSecondary;
    textAlign: 'right';
    marginTop: spacing.xs;
  },
  imageUploadButton: {
    flexDirection: 'row';
    alignItems: 'center';
    justifyContent: 'center';
    paddingVertical: spacing.lg;
    borderWidth: 2;
    borderColor: colors.border;
    borderStyle: 'dashed';
    borderRadius: borderRadius.md;
    backgroundColor: colors.surface;
  },
  imageUploadText: {
    marginLeft: spacing.sm;
    fontSize: typography.sizes.md;
    color: colors.primary;
  },
  imageList: {
    marginTop: spacing.sm;
  },
  imageItem: {
    position: 'relative';
    marginRight: spacing.sm;
  },
  uploadedImage: {
    width: 80;
    height: 80;
    borderRadius: borderRadius.sm;
  },
  removeImageButton: {
    position: 'absolute';
    top: -8;
    right: -8;
    backgroundColor: colors.error;
    borderRadius: 12;
    width: 24;
    height: 24;
    justifyContent: 'center';
    alignItems: 'center';
  },
  tagInputContainer: {
    flexDirection: 'row';
    alignItems: 'center';
  },
  tagInput: {
    flex: 1;
    borderWidth: 1;
    borderColor: colors.border;
    borderRadius: borderRadius.md;
    paddingHorizontal: spacing.md;
    paddingVertical: spacing.sm;
    fontSize: typography.sizes.md;
    color: colors.text;
    backgroundColor: colors.surface;
    marginRight: spacing.sm;
  },
  addTagButton: {
    padding: spacing.sm;
    backgroundColor: colors.surface;
    borderRadius: borderRadius.md;
    borderWidth: 1;
    borderColor: colors.border;
  },
  tagList: {
    flexDirection: 'row';
    flexWrap: 'wrap';
    marginTop: spacing.sm;
  },
  tag: {
    flexDirection: 'row';
    alignItems: 'center';
    backgroundColor: colors.primary + '20';
    paddingHorizontal: spacing.sm;
    paddingVertical: spacing.xs;
    borderRadius: borderRadius.sm;
    marginRight: spacing.xs;
    marginBottom: spacing.xs;
  },
  tagText: {
    fontSize: typography.sizes.sm;
    color: colors.primary;
    marginRight: spacing.xs;
  },
  modalOverlay: {
    flex: 1;
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'flex-end';
  },
  modalContent: {
    backgroundColor: colors.background;
    borderTopLeftRadius: borderRadius.lg;
    borderTopRightRadius: borderRadius.lg;
    maxHeight: '80%';
  },
  modalHeader: {
    flexDirection: 'row';
    justifyContent: 'space-between';
    alignItems: 'center';
    paddingHorizontal: spacing.md;
    paddingVertical: spacing.md;
    borderBottomWidth: 1;
    borderBottomColor: colors.border;
  },
  modalTitle: {
    fontSize: typography.sizes.lg;
    fontWeight: typography.weights.semibold;
    color: colors.text;
  },
  typeList: {
    padding: spacing.md;
  },
  typeItem: {
    flexDirection: 'row';
    alignItems: 'center';
    paddingVertical: spacing.md;
    paddingHorizontal: spacing.sm;
    borderRadius: borderRadius.md;
    marginBottom: spacing.sm;
  },
  selectedTypeItem: {
    backgroundColor: colors.primary + '10';
  },
  typeIcon: {
    width: 40;
    height: 40;
    borderRadius: 20;
    justifyContent: 'center';
    alignItems: 'center';
    marginRight: spacing.md;
  },
  typeInfo: {
    flex: 1;
  },
  typeTitle: {
    fontSize: typography.sizes.md;
    fontWeight: typography.weights.medium;
    color: colors.text;
  },
  typeDescription: {
    fontSize: typography.sizes.sm;
    color: colors.textSecondary;
    marginTop: spacing.xs;
  },
  categoryList: {
    padding: spacing.md;
  },
  categoryItem: {
    flexDirection: 'row';
    alignItems: 'center';
    paddingVertical: spacing.md;
    paddingHorizontal: spacing.sm;
    borderRadius: borderRadius.md;
    marginBottom: spacing.xs;
  },
  selectedCategoryItem: {
    backgroundColor: colors.primary + '10';
  },
  categoryName: {
    flex: 1;
    marginLeft: spacing.sm;
    fontSize: typography.sizes.md;
    color: colors.text;
  },
  previewContainer: {
    flex: 1;
    padding: spacing.md;
  },
  previewHeader: {
    flexDirection: 'row';
    alignItems: 'center';
    marginBottom: spacing.md;
  },
  previewMeta: {
    marginLeft: spacing.sm;
  },
  previewType: {
    fontSize: typography.sizes.sm;
    fontWeight: typography.weights.medium;
    color: colors.primary;
  },
  previewCategory: {
    fontSize: typography.sizes.xs;
    color: colors.textSecondary;
  },
  previewTitle: {
    fontSize: typography.sizes.xl;
    fontWeight: typography.weights.bold;
    color: colors.text;
    marginBottom: spacing.md;
  },
  previewImages: {
    marginBottom: spacing.md;
  },
  previewImage: {
    width: 120;
    height: 120;
    borderRadius: borderRadius.md;
    marginRight: spacing.sm;
  },
  previewContent: {
    fontSize: typography.sizes.md;
    color: colors.text;
    lineHeight: 24;
    marginBottom: spacing.md;
  },
  previewTags: {
    flexDirection: 'row';
    flexWrap: 'wrap';
  },
  previewTag: {
    backgroundColor: colors.primary + '20';
    paddingHorizontal: spacing.sm;
    paddingVertical: spacing.xs;
    borderRadius: borderRadius.sm;
    marginRight: spacing.xs;
    marginBottom: spacing.xs;
  },
  previewTagText: {
    fontSize: typography.sizes.sm;
    color: colors.primary;
  },
});

export default UGCContentCreator; 