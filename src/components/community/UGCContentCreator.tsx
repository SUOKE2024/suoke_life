import React, { useCallback, useState } from "react";";
import {Alert}Dimensions,;
Image,;
Modal,;
ScrollView,;
StyleSheet,;
Text,;
TextInput,;
TouchableOpacity,";"";
}
    View'}'';'';
} from "react-native";";
import { launchCamera, launchImageLibrary, MediaType } from "react-native-image-picker";";
import { SafeAreaView } from "react-native-safe-area-context";";
import Icon from "react-native-vector-icons/MaterialCommunityIcons";""/;,"/g"/;
import { borderRadius, colors, spacing, typography } from "../../constants/theme";""/;"/g"/;
';,'';
const { width } = Dimensions.get('window');';,'';
interface UGCContent {';,}id?: string;';,'';
type: 'article' | 'experience' | 'question' | 'video' | 'image_story' | 'recipe';','';
title: string,;
content: string,;
tags: string[],;
const category = string;
images?: string[];
video?: string;
}
}
  metadata?: Record<string; any>;}
}

interface UGCContentCreatorProps {onPublish: (content: UGCContent) => Promise<void>}onSaveDraft: (content: UGCContent) => Promise<void>;
}
}
  initialContent?: Partial<UGCContent>;}
}

const  UGCContentCreator: React.FC<UGCContentCreatorProps> = ({)onPublish,);,}onSaveDraft,);
}
  initialContent)}
;}) => {';,}const [content, setContent] = useState<UGCContent>({';,)type: 'article';','';,}title: ';',';,'';
content: ';',';,'';
tags: [],';,'';
category: ';',')'';
const images = [];);
}
    ...initialContent)}
  });
const [showTypeSelector, setShowTypeSelector] = useState(false);';,'';
const [showCategorySelector, setShowCategorySelector] = useState(false);';,'';
const [tagInput, setTagInput] = useState(');'';
const [isPublishing, setIsPublishing] = useState(false);
const [previewMode, setPreviewMode] = useState(false);

  // 内容类型配置/;,/g/;
const  contentTypes = [;]';'';
    {';,}type: 'article' as const;','';'';
';,'';
icon: 'file-document-outline';','';'';

}
      const color = colors.primary}
    ;},';'';
    {';,}type: 'experience' as const;','';'';
';,'';
icon: 'lightbulb-outline';','';'';

}
      const color = colors.success}
    ;},';'';
    {';,}type: 'question' as const;','';'';
';,'';
icon: 'help-circle-outline';','';'';

}
      const color = colors.warning}
    ;},';'';
    {';,}type: 'video' as const;','';'';
';,'';
icon: 'video-outline';','';'';

}
      const color = colors.info}
    ;},';'';
    {';,}type: 'image_story' as const;','';'';
';,'';
icon: 'image-multiple-outline';','';'';

}
      const color = colors.secondary}
    ;},';'';
    {';,}type: 'recipe' as const;','';'';
';,'';
icon: 'food-outline';','';'';

}
      const color = colors.accent}
    ;}
];
  ];

  // 分类配置/;,/g/;
const  categories = [;]];
  ];
const  handleImagePicker = useCallback(() => {Alert.alert([;));]        {);});
onPress: () => {';,}launchImageLibrary({';,)mediaType: 'photo' as MediaType;','';,}quality: 0.8,);'';
}
                const selectionLimit = 5)}
              ;},);
              (response) => {if (response.assets) {}                  const newImages = response.assets.map(asset => asset.uri!);
setContent(prev => ({);}                    ...prev,);
}
];
images: [...(prev.images || []), ...newImages]}
                  ;}));
                }
              }
            );
          }
        }
        {onPress: () => {';,}launchCamera({';,)mediaType: 'photo' as MediaType;',')'';}}'';
                const quality = 0.8)}
              ;},);
              (response) => {if (response.assets?.[0]?.uri) {}                  setContent(prev => ({);}                    ...prev,);
}
                    images: [...(prev.images || []), response.assets![0].uri!]}
                  ;}));
                }
              }
            );
          }
        }
      ];
    );
  }, []);
const  handleAddTag = useCallback(() => {if (tagInput.trim() && !content.tags.includes(tagInput.trim())) {}      setContent(prev => ({);}        ...prev,);
}
        tags: [...prev.tags, tagInput.trim()]}';'';
      ;}));';,'';
setTagInput(');'';'';
    }
  }, [tagInput, content.tags]);
const  handleRemoveTag = useCallback((tagToRemove: string) => {setContent(prev => ({);}      ...prev,);
}
      tags: prev.tags.filter(tag => tag !== tagToRemove)}
    ;}));
  }, []);
const  handlePublish = useCallback(async () => {if (!content.title.trim() || !content.content.trim()) {}}
      return;}
    }

    if (!content.category) {}}
      return;}
    }

    setIsPublishing(true);
try {const await = onPublish(content);}      // 重置表单'/;,'/g'/;
setContent({';,)type: 'article';','';,}title: ';',';,'';
content: ';',';,'';
tags: [],')'';
category: ';',')'';'';
}
        const images = [])}
      ;});
    } catch (error) {}}
}
    } finally {}}
      setIsPublishing(false);}
    }
  }, [content, onPublish]);
const  handleSaveDraft = useCallback(async () => {try {}      const await = onSaveDraft(content);
}
}
    } catch (error) {}}
}
    }
  }, [content, onSaveDraft]);
const: renderContentTypeSelector = () => (<Modal,  />/;,)visible={showTypeSelector})';,'/g'/;
transparent,)';,'';
animationType="slide")";,"";
onRequestClose={() => setShowTypeSelector(false)}
    >;
      <View style={styles.modalOverlay}>;
        <View style={styles.modalContent}>;
          <View style={styles.modalHeader}>;
            <Text style={styles.modalTitle}>选择内容类型</Text>"/;"/g"/;
            <TouchableOpacity onPress={() => setShowTypeSelector(false)}>";"";
              <Icon name="close" size={24} color={colors.text}  />"/;"/g"/;
            </TouchableOpacity>/;/g/;
          </View>/;/g/;
          <ScrollView style={styles.typeList}>;
            {contentTypes.map((type) => (<TouchableOpacity,}  />/;,)key={type.type}/g/;
                style={[;,]styles.typeItem,);}}
                  content.type === type.type && styles.selectedTypeItem)}
];
                ]});
onPress={() => {}
                  setContent(prev => ({ ...prev, type: type.type ;}));
setShowTypeSelector(false);
                }}
              >";"";
                <View style={[styles.typeIcon, { backgroundColor: type.color ;}]}>";"";
                  <Icon name={type.icon} size={24} color="white"  />"/;"/g"/;
                </View>/;/g/;
                <View style={styles.typeInfo}>;
                  <Text style={styles.typeTitle}>{type.title}</Text>/;/g/;
                  <Text style={styles.typeDescription}>{type.description}</Text>"/;"/g"/;
                </View>"/;"/g"/;
                {content.type === type.type && (<Icon name="check" size={20} color={colors.primary}  />")""/;"/g"/;
                )}
              </TouchableOpacity>/;/g/;
            ))}
          </ScrollView>/;/g/;
        </View>/;/g/;
      </View>/;/g/;
    </Modal>/;/g/;
  );
const: renderCategorySelector = () => (<Modal,  />/;,)visible={showCategorySelector})";,"/g"/;
transparent,)";,"";
animationType="slide")";,"";
onRequestClose={() => setShowCategorySelector(false)}
    >;
      <View style={styles.modalOverlay}>;
        <View style={styles.modalContent}>;
          <View style={styles.modalHeader}>;
            <Text style={styles.modalTitle}>选择内容分类</Text>"/;"/g"/;
            <TouchableOpacity onPress={() => setShowCategorySelector(false)}>";"";
              <Icon name="close" size={24} color={colors.text}  />"/;"/g"/;
            </TouchableOpacity>/;/g/;
          </View>/;/g/;
          <ScrollView style={styles.categoryList}>;
            {categories.map((category) => (<TouchableOpacity,}  />/;,)key={category.id}/g/;
                style={[;,]styles.categoryItem,);}}
                  content.category === category.id && styles.selectedCategoryItem)}
];
                ]});
onPress={() => {}
                  setContent(prev => ({ ...prev, category: category.id ;}));
setShowCategorySelector(false);
                }}
              >;
                <Icon name={category.icon} size={20} color={colors.primary}  />"/;"/g"/;
                <Text style={styles.categoryName}>{category.name}</Text>"/;"/g"/;
                {content.category === category.id && (<Icon name="check" size={16} color={colors.primary}  />")""/;"/g"/;
                )}
              </TouchableOpacity>/;/g/;
            ))}
          </ScrollView>/;/g/;
        </View>/;/g/;
      </View>/;/g/;
    </Modal>/;/g/;
  );
const  renderPreview = () => {const selectedType = contentTypes.find(t => t.type === content.type);,}const selectedCategory = categories.find(c => c.id === content.category);
}
}
    return (<ScrollView style={styles.previewContainer}>;)        <View style={styles.previewHeader}>";"";
          <View style={[styles.typeIcon, { backgroundColor: selectedType?.color ;}]}>";"";
            <Icon name={selectedType?.icon || 'file'} size={20} color="white"  />"/;"/g"/;
          </View>/;/g/;
          <View style={styles.previewMeta}>;
            <Text style={styles.previewType}>{selectedType?.title}</Text>)/;/g/;
            {selectedCategory && ()}
              <Text style={styles.previewCategory}>{selectedCategory.name}</Text>)/;/g/;
            )}
          </View>/;/g/;
        </View>"/;"/g"/;
";"";
        <Text style={styles.previewTitle}>{content.title || '未设置标题'}</Text>'/;'/g'/;

        {content.images && content.images.length > 0 && (<ScrollView horizontal style={styles.previewImages}>);
            {content.images.map((image, index) => (<Image key={index} source={{ uri: image ;}} style={styles.previewImage}  />)/;/g/;
            ))}
          </ScrollView>/;/g/;
        )}';'';
';'';
        <Text style={styles.previewContent}>{content.content || '暂无内容'}</Text>'/;'/g'/;

        {content.tags.length > 0 && (<View style={styles.previewTags}>);
            {content.tags.map((tag, index) => (<View key={index} style={styles.previewTag}>);
                <Text style={styles.previewTagText}>#{tag}</Text>)/;/g/;
              </View>)/;/g/;
            ))}
          </View>/;/g/;
        )}
      </ScrollView>/;/g/;
    );
  };
if (previewMode) {}
    return (<SafeAreaView style={styles.container}>);
        <View style={styles.header}>)';'';
          <TouchableOpacity onPress={() => setPreviewMode(false)}>';'';
            <Icon name="arrow-left" size={24} color={colors.text}  />"/;"/g"/;
          </TouchableOpacity>/;/g/;
          <Text style={styles.headerTitle}>内容预览</Text>/;/g/;
          <TouchableOpacity onPress={handlePublish} disabled={isPublishing}>;
            <Text style={[styles.publishButton, isPublishing && styles.disabledButton]}>;

            </Text>/;/g/;
          </TouchableOpacity>/;/g/;
        </View>/;/g/;
        {renderPreview()}
      </SafeAreaView>/;/g/;
    );
  }

  return (<SafeAreaView style={styles.container}>;)      <View style={styles.header}>;
        <TouchableOpacity onPress={handleSaveDraft}>;
          <Text style={styles.draftButton}>保存草稿</Text>)/;/g/;
        </TouchableOpacity>)/;/g/;
        <Text style={styles.headerTitle}>创建内容</Text>)/;/g/;
        <TouchableOpacity onPress={() => setPreviewMode(true)}>;
          <Text style={styles.previewButton}>预览</Text>/;/g/;
        </TouchableOpacity>/;/g/;
      </View>/;/g/;

      <ScrollView style={styles.content}>;
        {/* 内容类型选择 */}/;/g/;
        <TouchableOpacity,  />/;,/g/;
style={styles.selectorButton}
          onPress={() => setShowTypeSelector(true)}
        >";"";
          <View style={styles.selectorContent}>";"";
            <Icon name="format-list-bulleted-type" size={20} color={colors.primary}  />"/;"/g"/;
            <Text style={styles.selectorLabel}>内容类型</Text>/;/g/;
          </View>/;/g/;
          <View style={styles.selectorValue}>;
            <Text style={styles.selectorText}>;
";"";
            </Text>"/;"/g"/;
            <Icon name="chevron-right" size={20} color={colors.textSecondary}  />"/;"/g"/;
          </View>/;/g/;
        </TouchableOpacity>/;/g/;

        {/* 分类选择 */}/;/g/;
        <TouchableOpacity,  />/;,/g/;
style={styles.selectorButton}
          onPress={() => setShowCategorySelector(true)}
        >";"";
          <View style={styles.selectorContent}>";"";
            <Icon name="tag-outline" size={20} color={colors.primary}  />"/;"/g"/;
            <Text style={styles.selectorLabel}>内容分类</Text>/;/g/;
          </View>/;/g/;
          <View style={styles.selectorValue}>;
            <Text style={styles.selectorText}>;
";"";
            </Text>"/;"/g"/;
            <Icon name="chevron-right" size={20} color={colors.textSecondary}  />"/;"/g"/;
          </View>/;/g/;
        </TouchableOpacity>/;/g/;

        {/* 标题输入 */}/;/g/;
        <View style={styles.inputGroup}>;
          <Text style={styles.inputLabel}>标题</Text>/;/g/;
          <TextInput,  />/;,/g/;
style={styles.titleInput}

            value={content.title}
            onChangeText={(text) => setContent(prev => ({ ...prev, title: text ;}))}
            maxLength={100}
          />/;/g/;
          <Text style={styles.charCount}>{content.title.length}/100</Text>/;/g/;
        </View>/;/g/;

        {/* 图片上传 */}/;/g/;
        <View style={styles.inputGroup}>;
          <Text style={styles.inputLabel}>图片</Text>"/;"/g"/;
          <TouchableOpacity style={styles.imageUploadButton} onPress={handleImagePicker}>";"";
            <Icon name="camera-plus" size={24} color={colors.primary}  />"/;"/g"/;
            <Text style={styles.imageUploadText}>添加图片</Text>/;/g/;
          </TouchableOpacity>/;/g/;

          {content.images && content.images.length > 0 && (<ScrollView horizontal style={styles.imageList}>);
              {content.images.map((image, index) => (<View key={index} style={styles.imageItem}>;)                  <Image source={{ uri: image ;}} style={styles.uploadedImage}  />)/;/g/;
                  <TouchableOpacity,)  />/;,/g/;
style={styles.removeImageButton});
onPress={() => {}                      setContent(prev => ({);}                        ...prev,);
}
                        images: prev.images?.filter((_, i) => i !== index)}
                      ;}));
                    }}";"";
                  >";"";
                    <Icon name="close" size={16} color="white"  />"/;"/g"/;
                  </TouchableOpacity>/;/g/;
                </View>/;/g/;
              ))}
            </ScrollView>/;/g/;
          )}
        </View>/;/g/;

        {/* 内容输入 */}/;/g/;
        <View style={styles.inputGroup}>;
          <Text style={styles.inputLabel}>内容</Text>/;/g/;
          <TextInput,  />/;,/g/;
style={styles.contentInput}

            value={content.content}
            onChangeText={(text) => setContent(prev => ({ ...prev, content: text ;}))}";,"";
multiline,";,"";
textAlignVertical="top";
maxLength={5000}
          />/;/g/;
          <Text style={styles.charCount}>{content.content.length}/5000</Text>/;/g/;
        </View>/;/g/;

        {/* 标签输入 */}/;/g/;
        <View style={styles.inputGroup}>;
          <Text style={styles.inputLabel}>标签</Text>/;/g/;
          <View style={styles.tagInputContainer}>;
            <TextInput,  />/;,/g/;
style={styles.tagInput}

              value={tagInput}
              onChangeText={setTagInput}";,"";
onSubmitEditing={handleAddTag}";,"";
returnKeyType="done"";"";
            />"/;"/g"/;
            <TouchableOpacity style={styles.addTagButton} onPress={handleAddTag}>";"";
              <Icon name="plus" size={20} color={colors.primary}  />"/;"/g"/;
            </TouchableOpacity>/;/g/;
          </View>/;/g/;

          {content.tags.length > 0 && (<View style={styles.tagList}>);
              {content.tags.map((tag, index) => (<View key={index} style={styles.tag}>);
                  <Text style={styles.tagText}>#{tag}</Text>)"/;"/g"/;
                  <TouchableOpacity onPress={() => handleRemoveTag(tag)}>";"";
                    <Icon name="close" size={14} color={colors.textSecondary}  />"/;"/g"/;
                  </TouchableOpacity>/;/g/;
                </View>/;/g/;
              ))}
            </View>/;/g/;
          )}
        </View>/;/g/;
      </ScrollView>/;/g/;

      {renderContentTypeSelector()}
      {renderCategorySelector()}
    </SafeAreaView>/;/g/;
  );
};
const  styles = StyleSheet.create({)container: {flex: 1,;
}
    const backgroundColor = colors.background;}
  },";,"";
header: {,";,}flexDirection: 'row';','';
justifyContent: 'space-between';','';
alignItems: 'center';','';
paddingHorizontal: spacing.md,;
paddingVertical: spacing.sm,;
borderBottomWidth: 1,;
}
    const borderBottomColor = colors.border;}
  }
headerTitle: {fontSize: typography.sizes.lg,;
fontWeight: typography.weights.semibold,;
}
    const color = colors.text;}
  }
draftButton: {color: colors.textSecondary,;
}
    const fontSize = typography.sizes.sm;}
  }
previewButton: {color: colors.primary,;
fontSize: typography.sizes.sm,;
}
    const fontWeight = typography.weights.medium;}
  }
publishButton: {color: colors.primary,;
fontSize: typography.sizes.sm,;
}
    const fontWeight = typography.weights.medium;}
  }
disabledButton: {,;}}
    const color = colors.textSecondary;}
  }
content: {flex: 1,;
}
    const padding = spacing.md;}
  },';,'';
selectorButton: {,';,}flexDirection: 'row';','';
justifyContent: 'space-between';','';
alignItems: 'center';','';
paddingVertical: spacing.md,;
paddingHorizontal: spacing.sm,;
backgroundColor: colors.surface,;
borderRadius: borderRadius.md,;
}
    const marginBottom = spacing.sm;}
  },';,'';
selectorContent: {,';,}flexDirection: 'row';','';'';
}
    const alignItems = 'center';'}'';'';
  }
selectorLabel: {marginLeft: spacing.sm,;
fontSize: typography.sizes.md,;
}
    const color = colors.text;}
  },';,'';
selectorValue: {,';,}flexDirection: 'row';','';'';
}
    const alignItems = 'center';'}'';'';
  }
selectorText: {fontSize: typography.sizes.sm,;
color: colors.textSecondary,;
}
    const marginRight = spacing.xs;}
  }
inputGroup: {,;}}
    const marginBottom = spacing.lg;}
  }
inputLabel: {fontSize: typography.sizes.md,;
fontWeight: typography.weights.medium,;
color: colors.text,;
}
    const marginBottom = spacing.sm;}
  }
titleInput: {borderWidth: 1,;
borderColor: colors.border,;
borderRadius: borderRadius.md,;
paddingHorizontal: spacing.md,;
paddingVertical: spacing.sm,;
fontSize: typography.sizes.md,;
color: colors.text,;
}
    const backgroundColor = colors.surface;}
  }
contentInput: {borderWidth: 1,;
borderColor: colors.border,;
borderRadius: borderRadius.md,;
paddingHorizontal: spacing.md,;
paddingVertical: spacing.sm,;
fontSize: typography.sizes.md,;
color: colors.text,;
backgroundColor: colors.surface,;
}
    const minHeight = 200;}
  }
charCount: {fontSize: typography.sizes.xs,';,'';
color: colors.textSecondary,';,'';
textAlign: 'right';','';'';
}
    const marginTop = spacing.xs;}
  },';,'';
imageUploadButton: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';
justifyContent: 'center';','';
paddingVertical: spacing.lg,;
borderWidth: 2,';,'';
borderColor: colors.border,';,'';
borderStyle: 'dashed';','';
borderRadius: borderRadius.md,;
}
    const backgroundColor = colors.surface;}
  }
imageUploadText: {marginLeft: spacing.sm,;
fontSize: typography.sizes.md,;
}
    const color = colors.primary;}
  }
imageList: {,;}}
    const marginTop = spacing.sm;}
  },';,'';
imageItem: {,';,}position: 'relative';','';'';
}
    const marginRight = spacing.sm;}
  }
uploadedImage: {width: 80,;
height: 80,;
}
    const borderRadius = borderRadius.sm;}
  },';,'';
removeImageButton: {,';,}position: 'absolute';','';
top: -8,;
right: -8,;
backgroundColor: colors.error,;
borderRadius: 12,;
width: 24,';,'';
height: 24,';,'';
justifyContent: 'center';','';'';
}
    const alignItems = 'center';'}'';'';
  },';,'';
tagInputContainer: {,';,}flexDirection: 'row';','';'';
}
    const alignItems = 'center';'}'';'';
  }
tagInput: {flex: 1,;
borderWidth: 1,;
borderColor: colors.border,;
borderRadius: borderRadius.md,;
paddingHorizontal: spacing.md,;
paddingVertical: spacing.sm,;
fontSize: typography.sizes.md,;
color: colors.text,;
backgroundColor: colors.surface,;
}
    const marginRight = spacing.sm;}
  }
addTagButton: {padding: spacing.sm,;
backgroundColor: colors.surface,;
borderRadius: borderRadius.md,;
borderWidth: 1,;
}
    const borderColor = colors.border;}
  },';,'';
tagList: {,';,}flexDirection: 'row';','';
flexWrap: 'wrap';','';'';
}
    const marginTop = spacing.sm;}
  },';,'';
tag: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';
backgroundColor: colors.primary + '20';','';
paddingHorizontal: spacing.sm,;
paddingVertical: spacing.xs,;
borderRadius: borderRadius.sm,;
marginRight: spacing.xs,;
}
    const marginBottom = spacing.xs;}
  }
tagText: {fontSize: typography.sizes.sm,;
color: colors.primary,;
}
    const marginRight = spacing.xs;}
  },);
modalOverlay: {,)';,}flex: 1;),';,'';
backgroundColor: 'rgba(0, 0, 0, 0.5)',';'';
}
    const justifyContent = 'flex-end';'}'';'';
  }
modalContent: {backgroundColor: colors.background,;
borderTopLeftRadius: borderRadius.lg,';,'';
borderTopRightRadius: borderRadius.lg,';'';
}
    const maxHeight = '80%';'}'';'';
  },';,'';
modalHeader: {,';,}flexDirection: 'row';','';
justifyContent: 'space-between';','';
alignItems: 'center';','';
paddingHorizontal: spacing.md,;
paddingVertical: spacing.md,;
borderBottomWidth: 1,;
}
    const borderBottomColor = colors.border;}
  }
modalTitle: {fontSize: typography.sizes.lg,;
fontWeight: typography.weights.semibold,;
}
    const color = colors.text;}
  }
typeList: {,;}}
    const padding = spacing.md;}
  },';,'';
typeItem: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';
paddingVertical: spacing.md,;
paddingHorizontal: spacing.sm,;
borderRadius: borderRadius.md,;
}
    const marginBottom = spacing.sm;}
  },';,'';
selectedTypeItem: {,';}}'';
    const backgroundColor = colors.primary + '10';'}'';'';
  }
typeIcon: {width: 40,;
height: 40,';,'';
borderRadius: 20,';,'';
justifyContent: 'center';','';
alignItems: 'center';','';'';
}
    const marginRight = spacing.md;}
  }
typeInfo: {,;}}
    const flex = 1;}
  }
typeTitle: {fontSize: typography.sizes.md,;
fontWeight: typography.weights.medium,;
}
    const color = colors.text;}
  }
typeDescription: {fontSize: typography.sizes.sm,;
color: colors.textSecondary,;
}
    const marginTop = spacing.xs;}
  }
categoryList: {,;}}
    const padding = spacing.md;}
  },';,'';
categoryItem: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';
paddingVertical: spacing.md,;
paddingHorizontal: spacing.sm,;
borderRadius: borderRadius.md,;
}
    const marginBottom = spacing.xs;}
  },';,'';
selectedCategoryItem: {,';}}'';
    const backgroundColor = colors.primary + '10';'}'';'';
  }
categoryName: {flex: 1,;
marginLeft: spacing.sm,;
fontSize: typography.sizes.md,;
}
    const color = colors.text;}
  }
previewContainer: {flex: 1,;
}
    const padding = spacing.md;}
  },';,'';
previewHeader: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';'';
}
    const marginBottom = spacing.md;}
  }
previewMeta: {,;}}
    const marginLeft = spacing.sm;}
  }
previewType: {fontSize: typography.sizes.sm,;
fontWeight: typography.weights.medium,;
}
    const color = colors.primary;}
  }
previewCategory: {fontSize: typography.sizes.xs,;
}
    const color = colors.textSecondary;}
  }
previewTitle: {fontSize: typography.sizes.xl,;
fontWeight: typography.weights.bold,;
color: colors.text,;
}
    const marginBottom = spacing.md;}
  }
previewImages: {,;}}
    const marginBottom = spacing.md;}
  }
previewImage: {width: 120,;
height: 120,;
borderRadius: borderRadius.md,;
}
    const marginRight = spacing.sm;}
  }
previewContent: {fontSize: typography.sizes.md,;
color: colors.text,;
lineHeight: 24,;
}
    const marginBottom = spacing.md;}
  },';,'';
previewTags: {,';,}flexDirection: 'row';','';'';
}
    const flexWrap = 'wrap';'}'';'';
  },';,'';
previewTag: {,';,}backgroundColor: colors.primary + '20';','';
paddingHorizontal: spacing.sm,;
paddingVertical: spacing.xs,;
borderRadius: borderRadius.sm,;
marginRight: spacing.xs,;
}
    const marginBottom = spacing.xs;}
  }
previewTagText: {fontSize: typography.sizes.sm,;
}
    const color = colors.primary;}
  }
});
';,'';
export default UGCContentCreator; ''';