import { useNavigation } from "@react-navigation/native";""/;,"/g"/;
import React, { useEffect, useRef, useState } from "react";";
import {;,}Animated,;
Dimensions,;
RefreshControl,;
ScrollView,;
StyleSheet,;
Text,;
TouchableOpacity,";"";
}
  View'}'';'';
} from "react-native";";
import { SafeAreaView } from "react-native-safe-area-context";";
import Icon from "react-native-vector-icons/MaterialCommunityIcons";""/;,"/g"/;
import { Button } from "../../components/ui/Button";""/;,"/g"/;
import {;,}borderRadius,;
colors,;
shadows,;
spacing,";"";
}
  typography'}'';'';
} from "../../constants/theme";""/;"/g"/;
';,'';
const { width: screenWidth ;} = Dimensions.get('window');';,'';
interface Recommendation {';,}id: string,';,'';
type: 'diet' | 'exercise' | 'lifestyle' | 'medical' | 'mental';','';
title: string,';,'';
description: string,';,'';
priority: 'high' | 'medium' | 'low';','';
confidence: number,;
tags: string[],;
const actionable = boolean;';,'';
estimatedTime?: string;';,'';
difficulty?: 'easy' | 'medium' | 'hard';';,'';
benefits: string[],;
icon: string,;
}
}
  const color = string;}
}

interface UserProfile {';,}age: number,';,'';
gender: 'male' | 'female';','';
healthGoals: string[],;
currentConditions: string[],;
lifestyle: string,;
}
}
  const activityLevel = string;}
}

const  SmartRecommendationScreen: React.FC = () => {const navigation = useNavigation();';,}const [refreshing, setRefreshing] = useState(false);';,'';
const [activeCategory, setActiveCategory] = useState<string>('all');';,'';
const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
const [userProfile] = useState<UserProfile>({';,)age: 28,';,}const gender = 'female';';'';

);
);
}
)}
  });

  // 动画值/;,/g/;
const fadeAnim = useRef(new Animated.Value(0)).current;
const slideAnim = useRef(new Animated.Value(50)).current;

  // 分类选项/;,/g/;
const  categories = [;]];
  ];

  // 初始化动画/;,/g/;
useEffect() => {Animated.parallel([;,)Animated.timing(fadeAnim, {)        toValue: 1,);,]duration: 800,);}}
        const useNativeDriver = true)}
      ;}),;
Animated.timing(slideAnim, {)toValue: 0,);,}duration: 800,);
}
        const useNativeDriver = true)}
      ;});
];
    ]).start();
loadRecommendations();
  }, []);

  // 加载推荐数据/;,/g/;
const  loadRecommendations = async () => {// 模拟AI生成的个性化推荐/;,}const  mockRecommendations: Recommendation[] = [;]';'/g'/;
      {';,}id: '1';','';
type: 'diet';','';
const description = ';'';
';,'';
priority: 'high';','';
confidence: 92,;
actionable: true,';'';
';,'';
difficulty: 'easy';','';'';
';,'';
icon: 'leaf';','';'';
}
        const color = colors.success}
      ;},';'';
      {';,}id: '2';','';
type: 'exercise';','';
const description = ';'';
';,'';
priority: 'high';','';
confidence: 88,;
actionable: true,';'';
';,'';
difficulty: 'easy';','';'';
';,'';
icon: 'neck';','';'';
}
        const color = colors.warning}
      ;},';'';
      {';,}id: '3';','';
type: 'mental';','';
const description = ';'';
';,'';
priority: 'medium';','';
confidence: 85,;
actionable: true,';'';
';,'';
difficulty: 'medium';','';'';
';,'';
icon: 'meditation';','';'';
}
        const color = colors.secondary}
      ;},';'';
      {';,}id: '4';','';
type: 'lifestyle';','';
const description = ';'';
';,'';
priority: 'medium';','';
confidence: 80,;
actionable: true,';'';
';,'';
difficulty: 'easy';','';'';
';,'';
icon: 'desk';','';'';
}
        const color = colors.info}
      ;},';'';
      {';,}id: '5';','';
type: 'medical';','';
const description = ';'';
';,'';
priority: 'low';','';
confidence: 75,;
actionable: true,';'';
';,'';
difficulty: 'easy';','';'';
';,'';
icon: 'stethoscope';','';'';
}
        const color = colors.error}
      ;}
];
    ];
setRecommendations(mockRecommendations);
  };

  // 刷新数据/;,/g/;
const  onRefresh = async () => {setRefreshing(true);,}const await = loadRecommendations();
}
    setRefreshing(false);}
  };
';'';
  // 过滤推荐'/;,'/g'/;
const filteredRecommendations = recommendations.filter(rec) => activeCategory === 'all' || rec.type === activeCategory;';'';
  );

  // 获取优先级颜色/;,/g/;
const  getPriorityColor = useCallback((priority: string) => {';,}switch (priority) {';,}case 'high': ';,'';
return colors.error;';,'';
case 'medium': ';,'';
return colors.warning;';,'';
case 'low': ';,'';
return colors.success;
default: ;
}
        return colors.textSecondary;}
    }
  };

  // 获取难度文本/;,/g/;
const  getDifficultyText = useCallback((difficulty?: string) => {';,}switch (difficulty) {';,}case 'easy': ';'';
';,'';
case 'medium': ';'';
';,'';
case 'hard': ';'';
';,'';
const default = ';'';
}
        return ';'}'';'';
    }
  };

  // 渲染分类标签/;,/g/;
const renderCategories = () => (<ScrollView;  />/;,)horizontal;,/g/;
showsHorizontalScrollIndicator={false}
      style={styles.categoriesContainer});
contentContainerStyle={styles.categoriesContent});
    >);
      {categories.map(category) => (<TouchableOpacity;}  />/;,)key={category.key}/g/;
          style={[;,]styles.categoryButton,;}}
            activeCategory === category.key && styles.activeCategoryButton,)}
            { borderColor: category.color ;});
];
          ]});
onPress={() => setActiveCategory(category.key)}
        >;
          <Icon;  />/;,/g/;
name={category.icon}
            size={20}
            color={}}
              activeCategory === category.key ? colors.white : category.color;}
            }
          />/;/g/;
          <Text;  />/;,/g/;
style={[;,]styles.categoryText}activeCategory === category.key && styles.activeCategoryText,;
              {color: ;,}activeCategory === category.key;
                    ? colors.white;
}
                    : category.color}
              }
];
            ]}
          >;
            {category.title}
          </Text>/;/g/;
        </TouchableOpacity>/;/g/;
      ))}
    </ScrollView>/;/g/;
  );

  // 渲染推荐卡片/;,/g,/;
  const: renderRecommendationCard = (recommendation: Recommendation,);
const index = number;);
  ) => (<Animated.View;  />/;,)key={recommendation.id}/g/;
      style={[;,]styles.recommendationCard,;}        {}}
          opacity: fadeAnim,}
];
const transform = [{ translateY: slideAnim ;}];
        }
      ]}
    >;
      {// 卡片头部}/;/g/;
      <View style={styles.cardHeader}>;
        <View;  />/;,/g/;
style={[;]';}}'';
            styles.iconContainer,'}'';'';
            { backgroundColor: recommendation.color + '20' ;}';'';
];
          ]}
        >;
          <Icon;  />/;,/g/;
name={recommendation.icon}
            size={24}
            color={recommendation.color}
          />/;/g/;
        </View>/;/g/;
        <View style={styles.headerInfo}>;
          <View style={styles.titleRow}>;
            <Text style={styles.cardTitle}>{recommendation.title}</Text>/;/g/;
            <View;)  />/;,/g/;
style={[;]);}}
                styles.priorityBadge,)}
                { backgroundColor: getPriorityColor(recommendation.priority) ;}
];
              ]}
            >';'';
              <Text style={styles.priorityText}>';'';
                {recommendation.priority === 'high'';}';'';
                  : recommendation.priority === 'medium'';'';

              </Text>/;/g/;
            </View>/;/g/;
}
          </View>}/;/g/;
          <View style={styles.metaInfo}>;
            <Text style={styles.confidenceText}>;

            </Text>/;/g/;
            {recommendation.difficulty && (<Text style={styles.difficultyText}>);
);
              </Text>)/;/g/;
            )}
          </View>/;/g/;
        </View>/;/g/;
      </View>/;/g/;

      {// 描述}/;/g/;
      <Text style={styles.description}>{recommendation.description}</Text>/;/g/;

      {// 标签}/;/g/;
      <View style={styles.tagsContainer}>;
        {recommendation.tags.map(tag, tagIndex) => (<View key={tagIndex} style={styles.tag}>);
            <Text style={styles.tagText}>{tag}</Text>)/;/g/;
          </View>)/;/g/;
        ))}
      </View>/;/g/;

      {// 预期效果}/;/g/;
      <View style={styles.benefitsContainer}>;
        <Text style={styles.benefitsTitle}>预期效果：</Text>'/;'/g'/;
        {recommendation.benefits.slice(0, 2).map(benefit, benefitIndex) => (<View key={benefitIndex} style={styles.benefitItem}>';)            <Icon name="check-circle" size={14} color={colors.success}  />")""/;"/g"/;
            <Text style={styles.benefitText}>{benefit}</Text>)/;/g/;
          </View>)/;/g/;
        ))}
      </View>/;/g/;

      {// 时间信息}"/;"/g"/;
      {recommendation.estimatedTime && (<View style={styles.timeInfo}>";)          <Icon name="clock-outline" size={16} color={colors.textSecondary}  />")""/;"/g"/;
          <Text style={styles.timeText}>{recommendation.estimatedTime}</Text>)/;/g/;
        </View>)/;/g/;
      )}

      {// 操作按钮}/;/g/;
      <View style={styles.cardActions}>;
        <Button;  />/;,/g/;
onPress={() => {}}
            // 查看详情}/;/g/;
          }}
        />/;/g/;
        <Button;  />/;,/g/;
onPress={() => {}}
            // 开始执行}/;/g/;
          }}
        />/;/g/;
      </View>/;/g/;
    </Animated.View>/;/g/;
  );

  // 渲染用户画像/;,/g/;
const  renderUserProfile = () => (<View style={styles.profileContainer}>;)      <Text style={styles.profileTitle}>个人画像</Text>/;/g/;
      <View style={styles.profileContent}>";"";
        <View style={styles.profileItem}>";"";
          <Icon name="account" size={16} color={colors.primary}  />"/;"/g"/;
          <Text style={styles.profileText}>;

          </Text>/;/g/;
        </View>"/;"/g"/;
        <View style={styles.profileItem}>";"";
          <Icon name="target" size={16} color={colors.primary}  />"/;"/g"/;
          <Text style={styles.profileText}>;

          </Text>/;/g/;
        </View>"/;"/g"/;
        <View style={styles.profileItem}>";"";
          <Icon name="run" size={16} color={colors.primary}  />"/;"/g"/;
          <Text style={styles.profileText}>;

          </Text>/;/g/;
        </View>)/;/g/;
      </View>)/;/g/;
    </View>)/;/g/;
  );
return (<SafeAreaView style={styles.container}>;)      {// 头部}/;/g/;
      <View style={styles.header}>);
        <TouchableOpacity;)  />/;,/g/;
style={styles.backButton});
onPress={() => navigation.goBack()}";"";
        >";"";
          <Icon name="arrow-left" size={24} color={colors.text}  />"/;"/g"/;
        </TouchableOpacity>/;/g/;
        <Text style={styles.headerTitle}>智能推荐</Text>"/;"/g"/;
        <TouchableOpacity style={styles.settingsButton}>";"";
          <Icon name="tune" size={24} color={colors.text}  />"/;"/g"/;
        </TouchableOpacity>/;/g/;
      </View>/;/g/;

      <ScrollView;  />/;,/g/;
style={styles.content}
        refreshControl={}
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh}  />/;/g/;
        }
      >;
        {// 用户画像}/;/g/;
        {renderUserProfile()}

        {// 分类标签}/;/g/;
        {renderCategories()}

        {// 推荐列表}/;/g/;
        <View style={styles.recommendationsContainer}>;
          <View style={styles.sectionHeader}>;
            <Text style={styles.sectionTitle}>;

            </Text>/;/g/;
            <TouchableOpacity>;
              <Text style={styles.refreshText}>刷新推荐</Text>/;/g/;
            </TouchableOpacity>/;/g/;
          </View>/;/g/;

          {filteredRecommendations.map(renderRecommendationCard)}
        </View>/;/g/;
      </ScrollView>/;/g/;
    </SafeAreaView>/;/g/;
  );
};
const  styles = StyleSheet.create({)container: {flex: 1,;
}
    const backgroundColor = colors.background}
  ;},";,"";
header: {,";,}flexDirection: 'row';','';
alignItems: 'center';','';
justifyContent: 'space-between';','';
paddingHorizontal: spacing.lg,;
paddingVertical: spacing.md,;
backgroundColor: colors.surface,;
borderBottomWidth: 1,;
}
    const borderBottomColor = colors.border}
  ;}
backButton: {width: 40,;
height: 40,;
borderRadius: 20,';,'';
backgroundColor: colors.gray100,';,'';
justifyContent: 'center';','';'';
}
    const alignItems = 'center'}'';'';
  ;}
headerTitle: {,';,}fontSize: typography.fontSize.lg,';,'';
fontWeight: '600' as const;','';'';
}
    const color = colors.text}
  ;}
settingsButton: {width: 40,;
height: 40,;
borderRadius: 20,';,'';
backgroundColor: colors.gray100,';,'';
justifyContent: 'center';','';'';
}
    const alignItems = 'center'}'';'';
  ;}
content: {,;}}
  const flex = 1}
  ;}
profileContainer: {backgroundColor: colors.surface,;
margin: spacing.lg,;
borderRadius: borderRadius.lg,;
const padding = spacing.lg;
}
    ...shadows.sm}
  }
profileTitle: {,';,}fontSize: typography.fontSize.base,';,'';
fontWeight: '600' as const;','';
color: colors.text,;
}
    const marginBottom = spacing.md}
  ;}
profileContent: {,;}}
  const gap = spacing.sm}
  ;},';,'';
profileItem: {,';,}flexDirection: 'row';','';'';
}
    const alignItems = 'center'}'';'';
  ;}
profileText: {fontSize: typography.fontSize.sm,;
color: colors.textSecondary,;
}
    const marginLeft = spacing.sm}
  ;}
categoriesContainer: {,;}}
  const marginBottom = spacing.lg}
  ;}
categoriesContent: {paddingHorizontal: spacing.lg,;
}
    const gap = spacing.sm}
  ;},';,'';
categoryButton: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';
paddingHorizontal: spacing.md,;
paddingVertical: spacing.sm,;
borderRadius: borderRadius.full,;
borderWidth: 1,;
}
    const backgroundColor = colors.surface}
  ;}
activeCategoryButton: {,;}}
  const backgroundColor = colors.primary}
  ;}
categoryText: {fontSize: typography.fontSize.sm,;
}
    const marginLeft = spacing.xs}
  ;}
activeCategoryText: {,;}}
  const color = colors.white}
  ;}
recommendationsContainer: {,;}}
  const paddingHorizontal = spacing.lg}
  ;},';,'';
sectionHeader: {,';,}flexDirection: 'row';','';
justifyContent: 'space-between';','';
alignItems: 'center';','';'';
}
    const marginBottom = spacing.lg}
  ;}
sectionTitle: {,';,}fontSize: typography.fontSize.lg,';,'';
fontWeight: '600' as const;','';'';
}
    const color = colors.text}
  ;}
refreshText: {fontSize: typography.fontSize.sm,;
}
    const color = colors.primary}
  ;}
recommendationCard: {backgroundColor: colors.surface,;
borderRadius: borderRadius.lg,;
padding: spacing.lg,;
const marginBottom = spacing.lg;
}
    ...shadows.sm}
  },';,'';
cardHeader: {,';,}flexDirection: 'row';','';'';
}
    const marginBottom = spacing.md}
  ;}
iconContainer: {width: 48,;
height: 48,';,'';
borderRadius: 24,';,'';
justifyContent: 'center';','';
alignItems: 'center';','';'';
}
    const marginRight = spacing.md}
  ;}
headerInfo: {,;}}
  const flex = 1}
  ;},';,'';
titleRow: {,';,}flexDirection: 'row';','';
justifyContent: 'space-between';','';
alignItems: 'flex-start';','';'';
}
    const marginBottom = spacing.xs}
  ;}
cardTitle: {,';,}fontSize: typography.fontSize.base,';,'';
fontWeight: '600' as const;','';
color: colors.text,;
flex: 1,;
}
    const marginRight = spacing.sm}
  ;}
priorityBadge: {paddingHorizontal: spacing.xs,;
paddingVertical: 2,;
}
    const borderRadius = borderRadius.sm}
  ;}
priorityText: {fontSize: typography.fontSize.xs,';,'';
color: colors.white,';'';
}
    const fontWeight = '600' as const'}'';'';
  ;},';,'';
metaInfo: {,';,}flexDirection: 'row';','';'';
}
    const gap = spacing.md}
  ;}
confidenceText: {fontSize: typography.fontSize.xs,;
}
    const color = colors.textSecondary}
  ;}
difficultyText: {fontSize: typography.fontSize.xs,;
}
    const color = colors.textSecondary}
  ;}
description: {fontSize: typography.fontSize.sm,;
color: colors.text,;
lineHeight: 20,;
}
    const marginBottom = spacing.md}
  ;},';,'';
tagsContainer: {,';,}flexDirection: 'row';','';
flexWrap: 'wrap';','';
gap: spacing.xs,;
}
    const marginBottom = spacing.md}
  ;}
tag: {backgroundColor: colors.gray100,;
paddingHorizontal: spacing.sm,;
paddingVertical: spacing.xs,;
}
    const borderRadius = borderRadius.sm}
  ;}
tagText: {fontSize: typography.fontSize.xs,;
}
    const color = colors.textSecondary}
  ;}
benefitsContainer: {,;}}
  const marginBottom = spacing.md}
  ;}
benefitsTitle: {,';,}fontSize: typography.fontSize.sm,';,'';
fontWeight: '600' as const;','';
color: colors.text,;
}
    const marginBottom = spacing.xs}
  ;},';,'';
benefitItem: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';'';
}
    const marginBottom = spacing.xs}
  ;}
benefitText: {fontSize: typography.fontSize.sm,;
color: colors.textSecondary,;
}
    const marginLeft = spacing.xs}
  ;},';,'';
timeInfo: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';'';
}
    const marginBottom = spacing.md}
  ;}
timeText: {fontSize: typography.fontSize.sm,;
color: colors.textSecondary,;
}
    const marginLeft = spacing.xs}
  ;},';,'';
cardActions: {,';,}flexDirection: 'row';','';
justifyContent: 'space-between';','';'';
}
    const gap = spacing.sm}
  ;}
actionButton: {,);}}
  const flex = 1)}
  ;});
});
export default SmartRecommendationScreen;';'';
''';