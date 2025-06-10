import { useNavigation } from "@react-navigation/native";""/;,"/g"/;
import React, { useEffect, useRef, useState } from "react";";
import {;,}Animated,;
Dimensions,;
ScrollView,;
StyleSheet,;
Text,;
TouchableOpacity,";"";
}
  View'}'';'';
} from "react-native";";
import { SafeAreaView } from "react-native-safe-area-context";";
import Icon from "react-native-vector-icons/MaterialCommunityIcons";""/;,"/g"/;
import {;,}borderRadius,;
colors,;
shadows,;
spacing,";"";
}
  typography'}'';'';
} from "../../constants/theme";""/;"/g"/;
';,'';
const { width } = Dimensions.get('window');';,'';
const  LifestyleManagementScreen: React.FC = () => {const navigation = useNavigation();';,}const [activeCategory, setActiveCategory] = useState<';'';
    'diet' | 'exercise' | 'sleep' | 'habits'';'';
  >('diet');';'';

  // 动画值/;,/g/;
const fadeAnim = useRef(new Animated.Value(0)).current;
const slideAnim = useRef(new Animated.Value(50)).current;

  // 今日数据/;/g/;
}
  const  todayData = {}
    calories: { consumed: 1650, target: 2000 ;}
water: { consumed: 6, target: 8 ;}
exercise: { minutes: 45, target: 60 ;}
sleep: { hours: 7.5, target: 8 ;}
steps: { count: 8500, target: 10000 ;}
  };

  // 饮食记录/;,/g/;
const  dietRecords = [;]';'';
    {';,}id: '1';','';'';
';,'';
time: '08:00';','';'';
';,'';
calories: 420,';'';
}
      const icon = 'weather-sunny'}'';'';
    ;},';'';
    {';,}id: '2';','';'';
';,'';
time: '12:30';','';'';
';,'';
calories: 650,';'';
}
      const icon = 'weather-partly-cloudy'}'';'';
    ;},';'';
    {';,}id: '3';','';'';
';,'';
time: '18:00';','';'';
';,'';
calories: 580,';'';
}
      const icon = 'weather-night'}'';'';
    ;}
];
  ];

  // 运动计划/;,/g/;
const  exercisePlans = [;]';'';
    {';,}id: '1';','';
duration: 30,';,'';
calories: 250,';,'';
status: 'completed';','';
time: '07:00';','';'';
}
      const icon = 'run'}'';'';
    ;},';'';
    {';,}id: '2';','';
duration: 45,';,'';
calories: 180,';,'';
status: 'pending';','';
time: '19:00';','';'';
}
      const icon = 'dumbbell'}'';'';
    ;},';'';
    {';,}id: '3';','';
duration: 20,';,'';
calories: 80,';,'';
status: 'pending';','';
time: '21:00';','';'';
}
      const icon = 'yoga'}'';'';
    ;}
];
  ];

  // 睡眠数据'/;,'/g'/;
const  sleepData = {';,}bedtime: '23:00';','';
wakeup: '06:30';','';
duration: 7.5,;
quality: 85,;
deepSleep: 2.1,;
lightSleep: 4.2,;
}
    const rem = 1.2}
  ;};

  // 健康习惯/;,/g/;
const  healthHabits = [;]';'';
    {';,}id: '1';','';
completed: true,';,'';
streak: 15,';'';
}
      const icon = 'water'}'';'';
    ;},';'';
    {';,}id: '2';','';
completed: false,';,'';
streak: 8,';'';
}
      const icon = 'meditation'}'';'';
    ;},';'';
    {';,}id: '3';','';
completed: true,';,'';
streak: 22,';'';
}
      const icon = 'pill'}'';'';
    ;},';'';
    {';,}id: '4';','';
completed: false,';,'';
streak: 5,';'';
}
      const icon = 'face-woman'}'';'';
    ;}
];
  ];
useEffect() => {Animated.parallel([;,)Animated.timing(fadeAnim, {)        toValue: 1,);,]duration: 800,);}}
        const useNativeDriver = true)}
      ;}),;
Animated.timing(slideAnim, {)toValue: 0,);,}duration: 800,);
}
        const useNativeDriver = true)}
      ;});
];
    ]).start();
  }, []);

  // 渲染分类标签/;,/g/;
const  renderCategoryTabs = useCallback(() => {const  categories = [;]];}    ];
return (<ScrollView;  />/;)}/g/;
        horizontal;}
        showsHorizontalScrollIndicator={false}
        style={styles.categoryContainer});
contentContainerStyle={styles.categoryContent});
      >);
        {categories.map(category) => (<TouchableOpacity;}  />/;,)key={category.key}/g/;
            style={[;,]styles.categoryTab,);}}
              activeCategory === category.key && styles.activeCategoryTab)}
];
            ]});
onPress={() => setActiveCategory(category.key as any)}
          >;
            <Icon;  />/;,/g/;
name={category.icon}
              size={20}
              color={}}
                activeCategory === category.key ? colors.white : colors.primary;}
              }
            />/;/g/;
            <Text;  />/;,/g/;
style={[;,]styles.categoryText,;}}
                activeCategory === category.key && styles.activeCategoryText}
];
              ]}
            >;
              {category.title}
            </Text>/;/g/;
          </TouchableOpacity>/;/g/;
        ))}
      </ScrollView>/;/g/;
    );
  };

  // 渲染今日概览/;,/g/;
const  renderTodayOverview = () => (<View style={styles.overviewContainer}>;)      <Text style={styles.sectionTitle}>今日概览</Text>/;/g/;
      <View style={styles.overviewGrid}>';'';
        <View style={styles.overviewCard}>';'';
          <Icon name="food" size={24} color={colors.primary}  />"/;"/g"/;
          <Text style={styles.overviewValue}>;
            {todayData.calories.consumed}/{todayData.calories.target}/;/g/;
          </Text>/;/g/;
          <Text style={styles.overviewLabel}>卡路里</Text>/;/g/;
        </View>"/;"/g"/;
        <View style={styles.overviewCard}>";"";
          <Icon name="water" size={24} color={colors.info}  />"/;"/g"/;
          <Text style={styles.overviewValue}>;
            {todayData.water.consumed}/{todayData.water.target}/;/g/;
          </Text>/;/g/;
          <Text style={styles.overviewLabel}>杯水</Text>/;/g/;
        </View>"/;"/g"/;
        <View style={styles.overviewCard}>";"";
          <Icon name="run" size={24} color={colors.success}  />"/;"/g"/;
          <Text style={styles.overviewValue}>;
            {todayData.exercise.minutes}/{todayData.exercise.target}/;/g/;
          </Text>/;/g/;
          <Text style={styles.overviewLabel}>分钟</Text>/;/g/;
        </View>"/;"/g"/;
        <View style={styles.overviewCard}>";"";
          <Icon name="sleep" size={24} color={colors.secondary}  />"/;"/g"/;
          <Text style={styles.overviewValue}>;
            {todayData.sleep.hours}/{todayData.sleep.target}/;/g/;
          </Text>/;/g/;
          <Text style={styles.overviewLabel}>小时</Text>/;/g/;
        </View>)/;/g/;
      </View>)/;/g/;
    </View>)/;/g/;
  );

  // 渲染饮食管理/;,/g/;
const  renderDietManagement = () => (<View style={styles.contentSection}>;)      <View style={styles.sectionHeader}>;
        <Text style={styles.sectionTitle}>饮食记录</Text>"/;"/g"/;
        <TouchableOpacity style={styles.addButton}>";"";
          <Icon name="plus" size={20} color={colors.primary}  />"/;"/g"/;
        </TouchableOpacity>)/;/g/;
      </View>)/;/g/;
);
      {dietRecords.map(record) => (<View key={record.id} style={styles.dietCard}>;)          <View style={styles.dietHeader}>;
            <View style={styles.mealInfo}>;
              <Icon name={record.icon} size={20} color={colors.primary}  />/;/g/;
              <Text style={styles.mealName}>{record.meal}</Text>/;/g/;
              <Text style={styles.mealTime}>{record.time}</Text>/;/g/;
            </View>/;/g/;
            <Text style={styles.caloriesText}>{record.calories} kcal</Text>)/;/g/;
          </View>)/;/g/;
          <View style={styles.foodList}>);
            {record.foods.map(food, index) => (<Text key={index} style={styles.foodItem}>);
                • {food});
              </Text>)/;/g/;
            ))}
          </View>/;/g/;
        </View>/;/g/;
      ))}

      <View style={styles.nutritionSummary}>;
        <Text style={styles.summaryTitle}>营养摄入</Text>/;/g/;
        <View style={styles.nutritionBar}>;
          <View style={styles.nutritionItem}>;
            <Text style={styles.nutritionLabel}>蛋白质</Text>/;/g/;
            <View style={styles.progressBar}>;
              <View;  />/;,/g/;
style={[;]";}}"";
                  styles.progressFill,"}"";"";
                  { width: '75%', backgroundColor: colors.primary ;}';'';
];
                ]}
              />/;/g/;
            </View>/;/g/;
            <Text style={styles.nutritionValue}>75g</Text>/;/g/;
          </View>/;/g/;
          <View style={styles.nutritionItem}>;
            <Text style={styles.nutritionLabel}>碳水化合物</Text>/;/g/;
            <View style={styles.progressBar}>;
              <View;  />/;,/g/;
style={[;]';}}'';
                  styles.progressFill,'}'';'';
                  { width: '60%', backgroundColor: colors.warning ;}';'';
];
                ]}
              />/;/g/;
            </View>/;/g/;
            <Text style={styles.nutritionValue}>180g</Text>/;/g/;
          </View>/;/g/;
          <View style={styles.nutritionItem}>;
            <Text style={styles.nutritionLabel}>脂肪</Text>/;/g/;
            <View style={styles.progressBar}>;
              <View;  />/;,/g/;
style={[;]';}}'';
                  styles.progressFill,'}'';'';
                  { width: '45%', backgroundColor: colors.error ;}';'';
];
                ]}
              />/;/g/;
            </View>/;/g/;
            <Text style={styles.nutritionValue}>35g</Text>/;/g/;
          </View>/;/g/;
        </View>/;/g/;
      </View>/;/g/;
    </View>/;/g/;
  );

  // 渲染运动计划/;,/g/;
const  renderExercisePlan = () => (<View style={styles.contentSection}>;)      <View style={styles.sectionHeader}>;
        <Text style={styles.sectionTitle}>运动计划</Text>'/;'/g'/;
        <TouchableOpacity style={styles.addButton}>';'';
          <Icon name="plus" size={20} color={colors.primary}  />"/;"/g"/;
        </TouchableOpacity>)/;/g/;
      </View>)/;/g/;
);
      {exercisePlans.map(plan) => (<View key={plan.id} style={styles.exerciseCard}>;)          <View style={styles.exerciseHeader}>;
            <View style={styles.exerciseInfo}>;
              <Icon name={plan.icon} size={24} color={colors.primary}  />/;/g/;
              <View style={styles.exerciseDetails}>;
                <Text style={styles.exerciseName}>{plan.name}</Text>/;/g/;
                <Text style={styles.exerciseTime}>;

                </Text>/;/g/;
              </View>/;/g/;
            </View>/;/g/;
            <View style={styles.exerciseStatus}>;
              <Text style={styles.caloriesText}>{plan.calories} kcal</Text>/;/g/;
              <Icon;"  />/;,"/g"/;
name={";}}"";
                  plan.status === 'completed' ? 'check-circle' : 'clock-outline'}'';'';
                }
                size={20}';,'';
color={';,}plan.status === 'completed'';'';
                    ? colors.success;
}
                    : colors.textSecondary;}
                }
              />/;/g/;
            </View>)/;/g/;
          </View>)/;/g/;
        </View>)/;/g/;
      ))}

      <View style={styles.exerciseStats}>;
        <Text style={styles.summaryTitle}>运动统计</Text>/;/g/;
        <View style={styles.statsGrid}>;
          <View style={styles.statCard}>;
            <Text style={styles.statValue}>{todayData.steps.count}</Text>/;/g/;
            <Text style={styles.statLabel}>步数</Text>/;/g/;
            <View style={styles.progressBar}>;
              <View;  />/;,/g/;
style={[;,]styles.progressFill,;}}
                  {}
                    width: `${(todayData.steps.count / todayData.steps.target) * 100;}%`,```/`;,`/g`/`;
const backgroundColor = colors.success;
                  ;}
];
                ]}
              />/;/g/;
            </View>/;/g/;
          </View>/;/g/;
          <View style={styles.statCard}>;
            <Text style={styles.statValue}>510</Text>/;/g/;
            <Text style={styles.statLabel}>消耗卡路里</Text>/;/g/;
            <View style={styles.progressBar}>;
              <View;  />/;,/g/;
style={[;]';}}'';
                  styles.progressFill,'}'';'';
                  { width: '85%', backgroundColor: colors.error ;}';'';
];
                ]}
              />/;/g/;
            </View>/;/g/;
          </View>/;/g/;
        </View>/;/g/;
      </View>/;/g/;
    </View>/;/g/;
  );

  // 渲染睡眠监测/;,/g/;
const  renderSleepMonitoring = () => (<View style={styles.contentSection}>;)      <View style={styles.sectionHeader}>;
        <Text style={styles.sectionTitle}>睡眠监测</Text>'/;'/g'/;
        <TouchableOpacity style={styles.addButton}>';'';
          <Icon name="chart-line" size={20} color={colors.primary}  />"/;"/g"/;
        </TouchableOpacity>/;/g/;
      </View>/;/g/;

      <View style={styles.sleepCard}>;
        <View style={styles.sleepHeader}>;
          <View style={styles.sleepTime}>;
            <Text style={styles.sleepLabel}>就寝时间</Text>/;/g/;
            <Text style={styles.sleepValue}>{sleepData.bedtime}</Text>/;/g/;
          </View>/;/g/;
          <View style={styles.sleepDuration}>;
            <Text style={styles.sleepDurationText}>{sleepData.duration}h</Text>/;/g/;
            <Text style={styles.sleepQuality}>;

            </Text>/;/g/;
          </View>/;/g/;
          <View style={styles.sleepTime}>;
            <Text style={styles.sleepLabel}>起床时间</Text>/;/g/;
            <Text style={styles.sleepValue}>{sleepData.wakeup}</Text>/;/g/;
          </View>/;/g/;
        </View>/;/g/;

        <View style={styles.sleepPhases}>;
          <Text style={styles.summaryTitle}>睡眠阶段</Text>/;/g/;
          <View style={styles.phaseBar}>;
            <View;  />/;,/g/;
style={}[;]}
                styles.phaseSegment,}
                { flex: sleepData.deepSleep, backgroundColor: colors.primary ;}
];
              ]}
            />/;/g/;
            <View;  />/;,/g/;
style={}[;]}
                styles.phaseSegment,}
                { flex: sleepData.lightSleep, backgroundColor: colors.info ;}
];
              ]}
            />/;/g/;
            <View;  />/;,/g/;
style={}[;]}
                styles.phaseSegment,}
                { flex: sleepData.rem, backgroundColor: colors.warning ;}
];
              ]}
            />/;/g/;
          </View>/;/g/;
          <View style={styles.phaseLegend}>;
            <View style={styles.legendItem}>;
              <View;  />/;,/g/;
style={}[;]}
                  styles.legendColor,}
                  { backgroundColor: colors.primary ;}
];
                ]}
              />/;/g/;
              <Text style={styles.legendText}>深睡 {sleepData.deepSleep}h</Text>/;/g/;
            </View>/;/g/;
            <View style={styles.legendItem}>;
              <View;  />/;,/g/;
style={[styles.legendColor, { backgroundColor: colors.info ;}]}
              />/;/g/;
              <Text style={styles.legendText}>;

              </Text>/;/g/;
            </View>/;/g/;
            <View style={styles.legendItem}>;
              <View;  />/;,/g/;
style={}[;]}
                  styles.legendColor,}
                  { backgroundColor: colors.warning ;}
];
                ]}
              />/;/g/;
              <Text style={styles.legendText}>REM {sleepData.rem}h</Text>/;/g/;
            </View>/;/g/;
          </View>/;/g/;
        </View>)/;/g/;
      </View>)/;/g/;
    </View>)/;/g/;
  );

  // 渲染健康习惯/;,/g/;
const  renderHealthHabits = () => (<View style={styles.contentSection}>;)      <View style={styles.sectionHeader}>;
        <Text style={styles.sectionTitle}>健康习惯</Text>"/;"/g"/;
        <TouchableOpacity style={styles.addButton}>";"";
          <Icon name="plus" size={20} color={colors.primary}  />"/;"/g"/;
        </TouchableOpacity>)/;/g/;
      </View>)/;/g/;
);
      {healthHabits.map(habit) => (<View key={habit.id} style={styles.habitCard}>;)          <View style={styles.habitHeader}>;
            <View style={styles.habitInfo}>;
              <Icon name={habit.icon} size={24} color={colors.primary}  />/;/g/;
              <View style={styles.habitDetails}>;
                <Text style={styles.habitName}>{habit.name}</Text>/;/g/;
                <Text style={styles.habitDescription}>{habit.description}</Text>/;/g/;
              </View>/;/g/;
            </View>/;/g/;
            <View style={styles.habitStatus}>;
              <Text style={styles.streakText}>{habit.streak}天</Text>/;/g/;
              <TouchableOpacity style={styles.checkButton}>";"";
                <Icon;"  />/;,"/g"/;
name={habit.completed ? 'check-circle' : 'circle-outline'}';,'';
size={24}
                  color={}}
                    habit.completed ? colors.success : colors.textSecondary;}
                  }
                />/;/g/;
              </TouchableOpacity>/;/g/;
            </View>)/;/g/;
          </View>)/;/g/;
        </View>)/;/g/;
      ))}

      <View style={styles.habitsSummary}>;
        <Text style={styles.summaryTitle}>习惯完成度</Text>/;/g/;
        <View style={styles.completionRate}>;
          <Text style={styles.completionText}>今日完成 2/4</Text>/;/g/;
          <View style={styles.progressBar}>;
            <View;  />/;,/g/;
style={[;]';}}'';
                styles.progressFill,'}'';'';
                { width: '50%', backgroundColor: colors.success ;}';'';
];
              ]}
            />/;/g/;
          </View>/;/g/;
          <Text style={styles.completionPercentage}>50%</Text>/;/g/;
        </View>/;/g/;
      </View>/;/g/;
    </View>/;/g/;
  );

  // 渲染内容/;,/g/;
const  renderContent = useCallback(() => {';,}switch (activeCategory) {';,}case 'diet': ';,'';
return renderDietManagement();';,'';
case 'exercise': ';,'';
return renderExercisePlan();';,'';
case 'sleep': ';,'';
return renderSleepMonitoring();';,'';
case 'habits': ';,'';
return renderHealthHabits();
default: ;
}
        return null;}
    }
  };
return (<SafeAreaView style={styles.container}>;)      {// 头部}/;/g/;
      <View style={styles.header}>);
        <TouchableOpacity;)  />/;,/g/;
style={styles.backButton});
onPress={() => navigation.goBack()}';'';
        >';'';
          <Icon name="arrow-left" size={24} color={colors.text}  />"/;"/g"/;
        </TouchableOpacity>/;/g/;
        <Text style={styles.headerTitle}>生活方式管理</Text>"/;"/g"/;
        <TouchableOpacity style={styles.settingsButton}>";"";
          <Icon name="cog-outline" size={24} color={colors.text}  />"/;"/g"/;
        </TouchableOpacity>/;/g/;
      </View>/;/g/;

      <ScrollView;  />/;,/g/;
style={styles.scrollContainer}
        showsVerticalScrollIndicator={false}
      >;
        {// 今日概览}/;/g/;
        {renderTodayOverview()}

        {// 分类标签}/;/g/;
        {renderCategoryTabs()}

        {// 内容区域}/;/g/;
        <Animated.View;  />/;,/g/;
style={[;,]styles.contentContainer,;}            {}}
              opacity: fadeAnim,}
];
const transform = [{ translateY: slideAnim ;}];
            }
          ]}
        >;
          {renderContent()}
        </Animated.View>/;/g/;
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
scrollContainer: {,;}}
  const flex = 1}
  ;}
overviewContainer: {padding: spacing.lg,;
}
    const backgroundColor = colors.surface}
  ;}
sectionTitle: {,';,}fontSize: typography.fontSize.lg,';,'';
fontWeight: '600' as const;','';
color: colors.text,;
}
    const marginBottom = spacing.md}
  ;},';,'';
overviewGrid: {,';,}flexDirection: 'row';','';
flexWrap: 'wrap';','';'';
}
    const gap = spacing.md}
  ;},);
overviewCard: {,);,}flex: 1,);
minWidth: (width - spacing.lg * 3) / 2,/;,/g,/;
  backgroundColor: colors.gray50,;
borderRadius: borderRadius.lg,';,'';
padding: spacing.md,';,'';
const alignItems = 'center';';'';
}
    ...shadows.sm}
  }
overviewValue: {,';,}fontSize: typography.fontSize.lg,';,'';
fontWeight: '700' as const;','';
color: colors.text,;
}
    const marginTop = spacing.sm}
  ;}
overviewLabel: {fontSize: typography.fontSize.sm,;
color: colors.textSecondary,;
}
    const marginTop = spacing.xs}
  ;}
categoryContainer: {backgroundColor: colors.surface,;
borderBottomWidth: 1,;
}
    const borderBottomColor = colors.border}
  ;}
categoryContent: {paddingHorizontal: spacing.lg,;
paddingVertical: spacing.md,;
}
    const gap = spacing.md}
  ;},';,'';
categoryTab: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';
paddingHorizontal: spacing.md,;
paddingVertical: spacing.sm,';,'';
borderRadius: borderRadius.lg,';,'';
backgroundColor: colors.primary + '20';','';'';
}
    const gap = spacing.xs}
  ;}
activeCategoryTab: {,;}}
  const backgroundColor = colors.primary}
  ;}
categoryText: {fontSize: typography.fontSize.sm,';,'';
color: colors.primary,';'';
}
    const fontWeight = '600' as const'}'';'';
  ;}
activeCategoryText: {,;}}
  const color = colors.white}
  ;}
contentContainer: {,;}}
  const flex = 1}
  ;}
contentSection: {,;}}
  const padding = spacing.lg}
  ;},';,'';
sectionHeader: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';
justifyContent: 'space-between';','';'';
}
    const marginBottom = spacing.lg}
  ;}
addButton: {width: 32,;
height: 32,';,'';
borderRadius: 16,';,'';
backgroundColor: colors.primary + '20';','';
justifyContent: 'center';','';'';
}
    const alignItems = 'center'}'';'';
  ;}
dietCard: {backgroundColor: colors.surface,;
borderRadius: borderRadius.lg,;
padding: spacing.lg,;
const marginBottom = spacing.md;
}
    ...shadows.sm}
  },';,'';
dietHeader: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';
justifyContent: 'space-between';','';'';
}
    const marginBottom = spacing.md}
  ;},';,'';
mealInfo: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';'';
}
    const gap = spacing.sm}
  ;}
mealName: {,';,}fontSize: typography.fontSize.base,';,'';
fontWeight: '600' as const;','';'';
}
    const color = colors.text}
  ;}
mealTime: {fontSize: typography.fontSize.sm,;
}
    const color = colors.textSecondary}
  ;}
caloriesText: {,';,}fontSize: typography.fontSize.sm,';,'';
fontWeight: '600' as const;','';'';
}
    const color = colors.primary}
  ;}
foodList: {,;}}
  const gap = spacing.xs}
  ;}
foodItem: {fontSize: typography.fontSize.sm,;
}
    const color = colors.textSecondary}
  ;}
nutritionSummary: {backgroundColor: colors.surface,;
borderRadius: borderRadius.lg,;
padding: spacing.lg,;
const marginTop = spacing.md;
}
    ...shadows.sm}
  }
summaryTitle: {,';,}fontSize: typography.fontSize.base,';,'';
fontWeight: '600' as const;','';
color: colors.text,;
}
    const marginBottom = spacing.md}
  ;}
nutritionBar: {,;}}
  const gap = spacing.md}
  ;},';,'';
nutritionItem: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';'';
}
    const gap = spacing.md}
  ;}
nutritionLabel: {fontSize: typography.fontSize.sm,;
color: colors.text,;
}
    const width = 80}
  ;}
progressBar: {flex: 1,;
height: 8,;
backgroundColor: colors.gray200,';,'';
borderRadius: 4,';'';
}
    const overflow = 'hidden'}'';'';
  ;},';,'';
progressFill: {,';,}height: '100%';','';'';
}
    const borderRadius = 4}
  ;}
nutritionValue: {,';,}fontSize: typography.fontSize.sm,';,'';
fontWeight: '600' as const;','';
color: colors.text,';,'';
width: 40,';'';
}
    const textAlign = 'right'}'';'';
  ;}
exerciseCard: {backgroundColor: colors.surface,;
borderRadius: borderRadius.lg,;
padding: spacing.lg,;
const marginBottom = spacing.md;
}
    ...shadows.sm}
  },';,'';
exerciseHeader: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';'';
}
    const justifyContent = 'space-between'}'';'';
  ;},';,'';
exerciseInfo: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';'';
}
    const gap = spacing.md}
  ;}
exerciseDetails: {,;}}
  const flex = 1}
  ;}
exerciseName: {,';,}fontSize: typography.fontSize.base,';,'';
fontWeight: '600' as const;','';'';
}
    const color = colors.text}
  ;}
exerciseTime: {fontSize: typography.fontSize.sm,;
color: colors.textSecondary,;
}
    const marginTop = 2}
  ;},';,'';
exerciseStatus: {,';,}alignItems: 'flex-end';','';'';
}
    const gap = spacing.xs}
  ;}
exerciseStats: {backgroundColor: colors.surface,;
borderRadius: borderRadius.lg,;
padding: spacing.lg,;
const marginTop = spacing.md;
}
    ...shadows.sm}
  },';,'';
statsGrid: {,';,}flexDirection: 'row';','';'';
}
    const gap = spacing.md}
  ;}
statCard: {,';,}flex: 1,';'';
}
    const alignItems = 'center'}'';'';
  ;}
statValue: {,';,}fontSize: typography.fontSize.xl,';,'';
fontWeight: '700' as const;','';'';
}
    const color = colors.text}
  ;}
statLabel: {fontSize: typography.fontSize.sm,;
color: colors.textSecondary,;
marginTop: spacing.xs,;
}
    const marginBottom = spacing.sm}
  ;}
sleepCard: {backgroundColor: colors.surface,;
borderRadius: borderRadius.lg,;
const padding = spacing.lg;
}
    ...shadows.sm}
  },';,'';
sleepHeader: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';
justifyContent: 'space-between';','';'';
}
    const marginBottom = spacing.lg}
  ;},';,'';
sleepTime: {,';}}'';
  const alignItems = 'center'}'';'';
  ;}
sleepLabel: {fontSize: typography.fontSize.sm,;
}
    const color = colors.textSecondary}
  ;}
sleepValue: {,';,}fontSize: typography.fontSize.lg,';,'';
fontWeight: '600' as const;','';
color: colors.text,;
}
    const marginTop = spacing.xs}
  ;},';,'';
sleepDuration: {,';}}'';
  const alignItems = 'center'}'';'';
  ;},';,'';
sleepDurationText: {,';,}fontSize: typography.fontSize['3xl'];','';
fontWeight: '700' as const;','';'';
}
    const color = colors.primary}
  ;}
sleepQuality: {fontSize: typography.fontSize.sm,;
color: colors.textSecondary,;
}
    const marginTop = spacing.xs}
  ;}
sleepPhases: {,;}}
  const marginTop = spacing.lg}
  ;},';,'';
phaseBar: {,';,}flexDirection: 'row';','';
height: 20,';,'';
borderRadius: 10,';,'';
overflow: 'hidden';','';'';
}
    const marginBottom = spacing.md}
  ;},';,'';
phaseSegment: {,';}}'';
  const height = '100%'}'';'';
  ;},';,'';
phaseLegend: {,';,}flexDirection: 'row';','';'';
}
    const justifyContent = 'space-around'}'';'';
  ;},';,'';
legendItem: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';'';
}
    const gap = spacing.xs}
  ;}
legendColor: {width: 12,;
height: 12,;
}
    const borderRadius = 6}
  ;}
legendText: {fontSize: typography.fontSize.xs,;
}
    const color = colors.textSecondary}
  ;}
habitCard: {backgroundColor: colors.surface,;
borderRadius: borderRadius.lg,;
padding: spacing.lg,;
const marginBottom = spacing.md;
}
    ...shadows.sm}
  },';,'';
habitHeader: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';'';
}
    const justifyContent = 'space-between'}'';'';
  ;},';,'';
habitInfo: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';
gap: spacing.md,;
}
    const flex = 1}
  ;}
habitDetails: {,;}}
  const flex = 1}
  ;}
habitName: {,';,}fontSize: typography.fontSize.base,';,'';
fontWeight: '600' as const;','';'';
}
    const color = colors.text}
  ;}
habitDescription: {fontSize: typography.fontSize.sm,;
color: colors.textSecondary,;
}
    const marginTop = 2}
  ;},';,'';
habitStatus: {,';,}alignItems: 'center';','';'';
}
    const gap = spacing.xs}
  ;}
streakText: {,';,}fontSize: typography.fontSize.sm,';,'';
fontWeight: '600' as const;','';'';
}
    const color = colors.primary}
  ;}
checkButton: {,;}}
  const padding = spacing.xs}
  ;}
habitsSummary: {backgroundColor: colors.surface,;
borderRadius: borderRadius.lg,;
padding: spacing.lg,;
const marginTop = spacing.md;
}
    ...shadows.sm}
  },';,'';
completionRate: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';'';
}
    const gap = spacing.md}
  ;}
completionText: {fontSize: typography.fontSize.sm,;
color: colors.text,;
}
    const width = 80}
  ;}
completionPercentage: {,';,}fontSize: typography.fontSize.sm,';,'';
fontWeight: '600' as const;','';
color: colors.text,';,'';
width: 40,';'';
}
    const textAlign = 'right'}'';'';
  ;}
});
export default LifestyleManagementScreen;';'';
''';