import React, { useEffect, useState, useCallback } from "react"
import { SafeAreaView  } from "react-native-safe-area-context"
import Icon from "react-native-vector-icons/MaterialIcons"
import { useMedicalResource } from "../../hooks/useMedicalResource"
import { MedicalResource, TimeSlot, Review } from "../../store/slices/medicalResourceSlice"
View,
Text,
StyleSheet,
ScrollView,
TouchableOpacity,
Image,
Linking,
Alert,
Modal,"
FlatList,
Dimensions;
} from "react-native;
const { width, height } = Dimensions.get('window');
interface MedicalResourceDetailScreenProps {navigation: any}route: {params: {,}
}
  const resourceId = string}
};
  };
}
const  MedicalResourceDetailScreen: React.FC<Suspense fallback={<LoadingSpinner  />}><MedicalResourceDetailScreenProps></Suspense> = ({/;))navigation,);/g/;
}
  route;)}
}) => {}
  const { resourceId } = route.params;
const {selectedResource}loading,
errors,
getResourceDetails,
quickBookAppointment,
};
clearSpecificError}
  } = useMedicalResource();
const [showBookingModal, setShowBookingModal] = useState(false);
const [selectedTimeSlot, setSelectedTimeSlot] = useState<TimeSlot | null>(null);
const [showImageModal, setShowImageModal] = useState(false);
const [selectedImageIndex, setSelectedImageIndex] = useState(0);
  // 加载资源详情
useEffect() => {if (resourceId) {}
      getResourceDetails(resourceId)}
    }
  }, [resourceId, getResourceDetails]);
  // 拨打电话
const handleCall = useCallback(phoneNumber: string) => {const url = `tel: ${phoneNumber;}`;````,```;
Linking.canOpenURL(url);
      .then(supported) => {if (supported) {}
          return Linking.openURL(url)}
        } else {}
}
        }
      });
  }, []);
  // 打开网站'/,'/g'/;
const handleOpenWebsite = useCallback(website: string) => {const url = website.startsWith('http') ? website : `https://${website;}`;```/`,`/g`/`;
Linking.canOpenURL(url);
      .then(supported) => {if (supported) {}
          return Linking.openURL(url)}
        } else {}
}
        }
      });
  }, []);
  // 预约时间段
const handleBookTimeSlot = useCallback(timeSlot: TimeSlot) => {setSelectedTimeSlot(timeSlot)}
    setShowBookingModal(true)}
  }, []);
  // 确认预约'
const handleConfirmBooking = useCallback(async () => {if (!selectedResource || !selectedTimeSlot) return;)'try {'const userId = 'current-user-id'; // 这里应该从用户状态获取'/,'/g'/;
const await = quickBookAppointment();
selectedResource.id,
selectedResource.name,
userId,
selectedTimeSlot.startTime,
        30,
      );
setShowBookingModal(false);
setSelectedTimeSlot(null);
}
}
    } catch (error) {}
}
    }
  }, [selectedResource, selectedTimeSlot, quickBookAppointment]);
  // 查看图片
const handleImagePress = useCallback(index: number) => {setSelectedImageIndex(index)}
    setShowImageModal(true)}
  }, []);
  // 渲染加载状态
if (loading.details) {}
    return (;)}
      <SafeAreaView style={styles.container}>;
        <View style={styles.loadingContainer}>;
          <Text>加载中...</Text>;
        </View>;
      </SafeAreaView>;
    );
  }
  // 渲染错误状态
if (errors.details) {}
    return (;)}
      <SafeAreaView style={styles.container}>;
        <View style={styles.errorContainer}>;
          <Text style={styles.errorText}>{errors.details}</Text>;
          <TouchableOpacity;'  />/,'/g'/;
style={styles.retryButton};
onPress={() => {clearSpecificError('details');';}}'';
              getResourceDetails(resourceId)}
            }
          >;
            <Text style={styles.retryButtonText}>重试</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }
  if (!selectedResource) {}
    return (;)}
      <SafeAreaView style={styles.container}>;
        <View style={styles.errorContainer}>;
          <Text style={styles.errorText}>资源不存在</Text>;
        </View>;
      </SafeAreaView>;
    );
  }
  // 渲染头部信息
const  renderHeader = () => (<View style={styles.header}>);
      <TouchableOpacity;)  />
style={styles.backButton};);
onPress={() => navigation.goBack()};
      >;
        <Icon name="arrow-back" size={24} color="#333"  />;"/;"/g"/;
      </TouchableOpacity>;
      <View style={styles.headerInfo}>;
        <Text style={styles.resourceName}>{selectedResource.name}</Text>;
        <Text style={styles.resourceType}>{getTypeLabel(selectedResource.type)}</Text>;
      </View>;"/;"/g"/;
      <View style={styles.ratingContainer}>;
        <Icon name="star" size={20} color="#FFD700"  />;"/;"/g"/;
        <Text style={styles.rating}>{selectedResource.rating.toFixed(1)}</Text>;
      </View>;
    </View>;
  );
  // 渲染图片轮播
const renderImages = () => {if (!selectedResource.images || selectedResource.images.length === 0) {return null}
    }
    return (;);
      <View style={styles.imageSection}>;
        <FlatList removeClippedSubviews={true} maxToRenderPerBatch={10} windowSize={10};  />
horizontal;
data={selectedResource.images};
renderItem={({  item, index  }) => (;)
            <TouchableOpacity onPress={() => handleImagePress(index)}>;
              <Image source={ uri: item ;}} style={styles.image} / loading="lazy" decoding="async"  />;"/;"/g"/;
            </TouchableOpacity>;
          )};
keyExtractor={(item, index) => index.toString()};
showsHorizontalScrollIndicator={false};
contentContainerStyle={styles.imageList};
        />;
      </View>;
    );
  };
  // 渲染基本信息"
const  renderBasicInfo = () => (<View style={styles.section}>;)      <Text style={styles.sectionTitle}>基本信息</Text>"/;"/g"/;
      <View style={styles.infoRow}>
        <Icon name="location-on" size={20} color="#666"  />"/;"/g"/;
        <Text style={styles.infoText}>{selectedResource.location.address}</Text>
      </View>"
      <View style={styles.infoRow}>
        <Icon;"  />"
name={selectedResource.availability.isOpen ? 'access-time' : 'schedule'}
size={20}
color={selectedResource.availability.isOpen ? '#4CAF50' : '#FF9800'}
        />
        <Text style={styles.infoText}>;
        </Text>'
      </View>'/;'/g'/;
      {selectedResource.specialty  && <View style={styles.infoRow}>'
          <Icon name="medical-services" size={20} color="#666"  />")
          <Text style={styles.infoText}>专科：{selectedResource.specialty}</Text>)
        </View>)
      )};
      {selectedResource.experience && (;)}
        <View style={styles.infoRow}>;
          <Icon name="work" size={20} color="#666"  />;"/;"/g"/;
          <Text style={styles.infoText}>从业经验：{selectedResource.experience}年</Text>;
        </View>;
      )};
      {selectedResource.consultationFee && (;)}
        <View style={styles.infoRow}>;
          <Icon name="attach-money" size={20} color="#666"  />;"/;"/g"/;
          <Text style={styles.infoText}>咨询费用：¥{selectedResource.consultationFee}</Text>;
        </View>;
      )};
    </View>;
  );
  // 渲染联系方式
const  renderContact = () => (<View style={styles.section}>;)      <Text style={styles.sectionTitle}>联系方式</Text>)
      <TouchableOpacity;)  />
style={styles.contactItem});
onPress={() => handleCall(selectedResource.contact.phone)}
      >
        <Icon name="phone" size={20} color="#007AFF"  />"/;"/g"/;
        <Text style={styles.contactText}>{selectedResource.contact.phone}</Text>"/;"/g"/;
        <Icon name="chevron-right" size={20} color="#ccc"  />"/;"/g"/;
      </TouchableOpacity>
      {selectedResource.contact.website  && <TouchableOpacity;}  />
style={styles.contactItem};
onPress={() => handleOpenWebsite(selectedResource.contact.website!)};
        >;
          <Icon name="language" size={20} color="#007AFF"  />;"/;"/g"/;
          <Text style={styles.contactText}>{selectedResource.contact.website}</Text>;"/;"/g"/;
          <Icon name="chevron-right" size={20} color="#ccc"  />;"/;"/g"/;
        </TouchableOpacity>;
      )};
      {selectedResource.contact.email && (;)}
        <View style={styles.contactItem}>;
          <Icon name="email" size={20} color="#666"  />;"/;"/g"/;
          <Text style={styles.contactText}>{selectedResource.contact.email}</Text>;
        </View>;
      )};
    </View>;
  );
  // 渲染服务项目
const renderServices = () => (;);
    <View style={styles.section}>;
      <Text style={styles.sectionTitle}>服务项目</Text>;
      <View style={styles.servicesContainer}>;
        {selectedResource.services.map(service, index) => (;))}
          <View key={index} style={styles.serviceTag}>;
            <Text style={styles.serviceText}>{service}</Text>;
          </View>;
        ))};
      </View>;
    </View>;
  );
  // 渲染可预约时间
const renderTimeSlots = () => {if (!selectedResource.availability.slots || selectedResource.availability.slots.length === 0) {return null}
    }
    return (<View style={styles.section}>);
        <Text style={styles.sectionTitle}>可预约时间</Text>)
        <View style={styles.timeSlotsContainer}>);
          {selectedResource.availability.slots.map(slot) => ()}
            <TouchableOpacity;}  />
key={slot.id}
              style={[]styles.timeSlot,}
                !slot.available && styles.timeSlotDisabled}
];
              ]}
              onPress={() => slot.available && handleBookTimeSlot(slot)};
disabled={!slot.available};
            >;
              <Text style={ />/;}[;];/g/;
}
                styles.timeSlotText,!slot.available && styles.timeSlotTextDisabled}
];
              ]}}>;
                {slot.startTime} - {slot.endTime};
              </Text>;
              {slot.price && (;)}
                <Text style={styles.timeSlotPrice}>¥{slot.price}</Text>;
              )};
            </TouchableOpacity>;
          ))};
        </View>;
      </View>;
    );
  };
  // 渲染描述
const renderDescription = () => {if (!selectedResource.description) return null}
    return (;)}
      <View style={styles.section}>;
        <Text style={styles.sectionTitle}>详细介绍</Text>;
        <Text style={styles.description}>{selectedResource.description}</Text>;
      </View>;
    );
  };
  // 渲染评价
const renderReviews = () => {if (!selectedResource.reviews || selectedResource.reviews.length === 0) {return null}
    }
    return (<View style={styles.section}>);
        <Text style={styles.sectionTitle}>用户评价</Text>)
        {selectedResource.reviews.slice(0, 3).map(review) => ()}
          <View key={review.id} style={styles.reviewItem}>;
            <View style={styles.reviewHeader}>;
              <Text style={styles.reviewUser}>{review.userName}</Text>
              <View style={styles.reviewRating}>;
                {[...Array(5)].map(_, i) => ())}
                  <Icon;}"  />"
key={i}","
name="star
size={14}","
color={i < review.rating ? '#FFD700' : '#E0E0E0'};
                   />;
                ))};
              </View>;
            </View>;
            <Text style={styles.reviewComment}>{review.comment}</Text>;
            <Text style={styles.reviewDate}>{review.date}</Text>;
          </View>;
        ))};
        {selectedResource.reviews.length > 3 && (;)}
          <TouchableOpacity style={styles.moreReviews}>;
            <Text style={styles.moreReviewsText}>查看更多评价</Text>;
          </TouchableOpacity>;
        )};
      </View>;
    );
  };
  // 渲染预约模态框'
const renderBookingModal = () => (<Modal;  />/,)visible={showBookingModal})','/g'/;
transparent;)'
animationType="slide");
onRequestClose={() => setShowBookingModal(false)}
    >;
      <View style={styles.modalOverlay}>;
        <View style={styles.modalContent}>;
          <Text style={styles.modalTitle}>确认预约</Text>
          <View style={styles.bookingInfo}>;
            <Text style={styles.bookingLabel}>医疗机构：</Text>
            <Text style={styles.bookingValue}>{selectedResource.name}</Text>
          </View>
          {selectedTimeSlot  && <View style={styles.bookingInfo}>;
              <Text style={styles.bookingLabel}>预约时间：</Text>
              <Text style={styles.bookingValue}>;
                {selectedTimeSlot.startTime} - {selectedTimeSlot.endTime}
              </Text>
            </View>
          )}
          {selectedTimeSlot?.price  && <View style={styles.bookingInfo}>;
              <Text style={styles.bookingLabel}>费用：</Text>
              <Text style={styles.bookingValue}>¥{selectedTimeSlot.price}</Text>
            </View>
          )}
          <View style={styles.modalButtons}>;
            <TouchableOpacity;  />
style={[styles.modalButton, styles.cancelButton]};
onPress={() => setShowBookingModal(false)};
            >;
              <Text style={styles.cancelButtonText}>取消</Text>;
            </TouchableOpacity>;
            <TouchableOpacity;  />
style={[styles.modalButton, styles.confirmButton]};
onPress={handleConfirmBooking};
            >;
              <Text style={styles.confirmButtonText}>确认预约</Text>;
            </TouchableOpacity>;
          </View>;
        </View>;
      </View>;
    </Modal>;
  );
  // 渲染图片查看模态框"
const renderImageModal = () => (<Modal;  />/,)visible={showImageModal})","/g"/;
transparent;)","
animationType="fade");
onRequestClose={() => setShowImageModal(false)}
    >;
      <View style={styles.imageModalOverlay}>;
        <TouchableOpacity;  />
style={styles.imageModalClose}
          onPress={() => setShowImageModal(false)}
        >
          <Icon name="close" size={30} color="#fff"  />"/;"/g"/;
        </TouchableOpacity>
        {selectedResource.images && (;)}
          <FlatList removeClippedSubviews={true} maxToRenderPerBatch={10} windowSize={10};  />
horizontal;
data={selectedResource.images};","
renderItem={({  item  }) => (;)
              <Image source={ uri: item ;}} style={styles.fullImage} / loading="lazy" decoding="async"  />;"/;"/g"/;
            )};
keyExtractor={(item, index) => index.toString()};
initialScrollIndex={selectedImageIndex};
showsHorizontalScrollIndicator={false};
pagingEnabled;
          />;
        )};
      </View>;
    </Modal>;
  );
  // 获取类型标签
const getTypeLabel = (type: string) => {const typeMap: { [key: string]: string ;} = {}
}
    };
return typeMap[type] || type;
  };
return (<SafeAreaView style={styles.container}>;);
      {renderHeader()};
      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>;
        {renderImages()};
        {renderBasicInfo()};
        {renderContact()};
        {renderServices()};
        {renderTimeSlots()};
        {renderDescription()};
        {renderReviews()};
      </ScrollView>;
      {renderBookingModal()};
      {renderImageModal()};
    </SafeAreaView>;
  );
};
const  styles = StyleSheet.create({)container: {,"flex: 1,";
}
    const backgroundColor = '#f5f5f5'}
  }
  // 加载和错误状态/,/g,/;
  loadingContainer: {,'flex: 1,'
justifyContent: 'center,'
}
    const alignItems = 'center'}
  }
errorContainer: {,'flex: 1,'
justifyContent: 'center,'
alignItems: 'center,'
}
    const paddingHorizontal = 20}
  }
errorText: {,'fontSize: 16,'
color: '#666,'
textAlign: 'center,'
}
    const marginBottom = 20}
  },'
retryButton: {,'backgroundColor: '#007AFF,'';
paddingHorizontal: 20,
paddingVertical: 10,
}
    const borderRadius = 8}
  },'
retryButtonText: {,'color: '#fff,'';
fontSize: 16,
}
    const fontWeight = '500'}
  }
  // 头部'/,'/g,'/;
  header: {,'flexDirection: 'row,'
alignItems: 'center,'';
paddingHorizontal: 16,
paddingVertical: 12,'
backgroundColor: '#fff,'';
borderBottomWidth: 1,
}
    const borderBottomColor = '#e0e0e0'}
  }
backButton: {padding: 8,
}
    const marginRight = 12}
  }
headerInfo: {,}
  const flex = 1}
  }
resourceName: {,'fontSize: 18,'
fontWeight: '600,'
color: '#333,'
}
    const marginBottom = 4}
  }
resourceType: {,'fontSize: 14,'
color: '#007AFF,'
}
    const fontWeight = '500'}
  ;},'
ratingContainer: {,'flexDirection: 'row,'
}
    const alignItems = 'center'}
  }
rating: {marginLeft: 4,
fontSize: 16,'
fontWeight: '500,'
}
    const color = '#333'}
  }
  // 内容区域/,/g,/;
  content: {,}
  const flex = 1}
  }
  // 图片区域'/,'/g,'/;
  imageSection: {,'backgroundColor: '#fff,'
}
    const marginBottom = 8}
  }
imageList: {paddingHorizontal: 16,
}
    const paddingVertical = 12}
  }
image: {width: 120,
height: 80,
borderRadius: 8,
}
    const marginRight = 12}
  }
  // 分区样式'/,'/g,'/;
  section: {,'backgroundColor: '#fff,'';
marginBottom: 8,
paddingHorizontal: 16,
}
    const paddingVertical = 16}
  }
sectionTitle: {,'fontSize: 16,'
fontWeight: '600,'
color: '#333,'
}
    const marginBottom = 12}
  }
  // 信息行'/,'/g,'/;
  infoRow: {,'flexDirection: 'row,'
alignItems: 'center,'
}
    const marginBottom = 12}
  }
infoText: {marginLeft: 12,
fontSize: 14,'
color: '#333,'
}
    const flex = 1}
  }
  // 联系方式'/,'/g,'/;
  contactItem: {,'flexDirection: 'row,'
alignItems: 'center,'';
paddingVertical: 12,
borderBottomWidth: 1,
}
    const borderBottomColor = '#f0f0f0'}
  }
contactText: {marginLeft: 12,
fontSize: 14,'
color: '#333,'
}
    const flex = 1}
  }
  // 服务项目'/,'/g,'/;
  servicesContainer: {,'flexDirection: 'row,'
}
    const flexWrap = 'wrap'}
  ;},'
serviceTag: {,'backgroundColor: '#f0f0f0,'';
paddingHorizontal: 12,
paddingVertical: 6,
borderRadius: 16,
marginRight: 8,
}
    const marginBottom = 8}
  }
serviceText: {,'fontSize: 12,
}
    const color = '#666'}
  }
  // 时间段'/,'/g,'/;
  timeSlotsContainer: {,'flexDirection: 'row,'
}
    const flexWrap = 'wrap'}
  ;},'
timeSlot: {,'backgroundColor: '#f8f8f8,'';
paddingHorizontal: 12,
paddingVertical: 8,
borderRadius: 8,
marginRight: 8,
marginBottom: 8,
borderWidth: 1,
}
    const borderColor = '#007AFF'}
  ;},'
timeSlotDisabled: {,'backgroundColor: '#f0f0f0,'
}
    const borderColor = '#ccc'}
  }
timeSlotText: {,'fontSize: 12,'
color: '#007AFF,'
}
    const fontWeight = '500'}
  ;},'
timeSlotTextDisabled: {,';}}
  const color = '#999'}
  }
timeSlotPrice: {,'fontSize: 10,'
color: '#FF6B35,'
}
    const marginTop = 2}
  }
  // 描述/,/g,/;
  description: {,'fontSize: 14,'
color: '#333,'
}
    const lineHeight = 20}
  }
  // 评价/,/g,/;
  reviewItem: {paddingVertical: 12,
borderBottomWidth: 1,
}
    const borderBottomColor = '#f0f0f0'}
  ;},'
reviewHeader: {,'flexDirection: 'row,'
justifyContent: 'space-between,'
alignItems: 'center,'
}
    const marginBottom = 8}
  }
reviewUser: {,'fontSize: 14,'
fontWeight: '500,'
}
    const color = '#333'}
  ;},'
reviewRating: {,';}}
  const flexDirection = 'row'}
  }
reviewComment: {,'fontSize: 14,'
color: '#333,'';
lineHeight: 18,
}
    const marginBottom = 6}
  }
reviewDate: {,'fontSize: 12,
}
    const color = '#999'}
  ;},'
moreReviews: {,'alignItems: 'center,'
}
    const paddingVertical = 12}
  }
moreReviewsText: {,'fontSize: 14,
}
    const color = '#007AFF'}
  }
  // 预约模态框)/,/g,/;
  modalOverlay: {,)'flex: 1,)'
backgroundColor: 'rgba(0, 0, 0, 0.5)','
justifyContent: 'center,'
}
    const alignItems = 'center'}
  ;},'
modalContent: {,'backgroundColor: '#fff,'';
borderRadius: 12,
padding: 20,
width: width * 0.85,
}
    const maxWidth = 400}
  }
modalTitle: {,'fontSize: 18,'
fontWeight: '600,'
color: '#333,'
textAlign: 'center,'
}
    const marginBottom = 20}
  },'
bookingInfo: {,'flexDirection: 'row,'
}
    const marginBottom = 12}
  }
bookingLabel: {,'fontSize: 14,'
color: '#666,'
}
    const width = 80}
  }
bookingValue: {,'fontSize: 14,'
color: '#333,'
}
    const flex = 1}
  },'
modalButtons: {,'flexDirection: 'row,'
}
    const marginTop = 20}
  }
modalButton: {flex: 1,
paddingVertical: 12,
borderRadius: 8,
}
    const alignItems = 'center'}
  ;},'
cancelButton: {,'backgroundColor: '#f0f0f0,'
}
    const marginRight = 8}
  },'
confirmButton: {,'backgroundColor: '#007AFF,'
}
    const marginLeft = 8}
  }
cancelButtonText: {,'fontSize: 16,'
color: '#666,'
}
    const fontWeight = '500'}
  }
confirmButtonText: {,'fontSize: 16,'
color: '#fff,'
}
    const fontWeight = '500'}
  }
  // 图片查看模态框/,/g,/;
  imageModalOverlay: {,'flex: 1,
}
    backgroundColor: 'rgba(0, 0, 0, 0.9)',justifyContent: 'center',alignItems: 'center}
  },imageModalClose: {,'position: "absolute,
}
      top: 50,right: 20,zIndex: 1,padding: 10;
  },fullImage: {width: width,height: height * 0.7,resizeMode: 'contain}
  };
});
export default MedicalResourceDetailScreen;