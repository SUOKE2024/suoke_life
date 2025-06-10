import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import React, { useEffect, useState } from 'react';
import {
    Alert,
    Dimensions,
    ScrollView,
    StyleSheet,
    Text,
    TouchableOpacity,
    View
} from 'react-native';
import { SubscriptionService } from '../../services/business/SubscriptionService';
import { PersonalizedPricing, SubscriptionTier } from '../../types/business';

const { width } = Dimensions.get('window');

interface SubscriptionPlansScreenProps {
  userId: string;
  userProfile: any;
  onSubscribe: (tierId: string, pricing: PersonalizedPricing) => void;
}

export const SubscriptionPlansScreen: React.FC<SubscriptionPlansScreenProps> = ({
  userId,
  userProfile,
  onSubscribe
;}) => {
  const [subscriptionService] = useState(new SubscriptionService());
  const [tiers, setTiers] = useState<SubscriptionTier[]>([]);
  const [personalizedPricing, setPersonalizedPricing] = useState<{[key: string]: PersonalizedPricing;}>({});
  const [selectedPeriod, setSelectedPeriod] = useState<'monthly' | 'yearly'>('monthly');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSubscriptionData();
  }, []);

  const loadSubscriptionData = async () => {
    try {
      const allTiers = subscriptionService.getSubscriptionTiers();
      setTiers(allTiers);

      // 计算个性化定价
      const pricingData: {[key: string]: PersonalizedPricing;} = {};
      for (const tier of allTiers) {
        try {
          const pricing = subscriptionService.calculatePersonalizedPricing(
            userId,
            tier.id,
            userProfile
          );
          pricingData[tier.id] = pricing;
        } catch (error) {
          console.warn(`Failed to calculate pricing for ${tier.id}:`, error);
        }
      }
      setPersonalizedPricing(pricingData);
    } catch (error) {
      console.error('Failed to load subscription data:', error);

    } finally {
      setLoading(false);
    }
  };

  const handleSubscribe = (tier: SubscriptionTier) => {
    const pricing = personalizedPricing[tier.id];
    if (pricing) {
      onSubscribe(tier.id, pricing);
    } else {

    }
  };

  const getDisplayPrice = (tier: SubscriptionTier): number => {
    const pricing = personalizedPricing[tier.id];
    if (pricing) {
      return selectedPeriod === 'yearly' 
        ? pricing.finalPrice * 12 * (1 - (tier.price.discount || 0) / 100)
        : pricing.finalPrice;
    }
    return selectedPeriod === 'yearly' ? tier.price.yearly : tier.price.monthly;
  };

  const getOriginalPrice = (tier: SubscriptionTier): number => {
    return selectedPeriod === 'yearly' ? tier.price.yearly : tier.price.monthly;
  };

  const getSavings = (tier: SubscriptionTier): number => {
    const pricing = personalizedPricing[tier.id];
    if (pricing) {
      return selectedPeriod === 'yearly' 
        ? pricing.basePrice * 12 - getDisplayPrice(tier)
        : pricing.basePrice - pricing.finalPrice;
    }
    return 0;
  };

  const renderFeatureList = (features: SubscriptionTier['features']) => {
    return features.slice(0, 4).map((feature, index) => (
      <View key={feature.id;} style={styles.featureItem}>
        <Ionicons name="checkmark-circle" size={16} color="#4CAF50" />
        <Text style={styles.featureText}>{feature.name}</Text>
        {feature.usage && (
          <Text style={styles.featureLimit}>
            ({feature.usage.limit}/{feature.usage.period})
          </Text>
        )}
      </View>
    ));
  };

  const renderPricingAdjustments = (tierId: string) => {
    const pricing = personalizedPricing[tierId];
    if (!pricing || pricing.adjustments.length === 0) return null;

    return (
      <View style={styles.adjustmentsContainer}>
        <Text style={styles.adjustmentsTitle}>个性化优惠：</Text>
        {pricing.adjustments.slice(0, 2).map((adjustment, index) => (
          <View key={index} style={styles.adjustmentItem}>
            <Text style={styles.adjustmentText}>

            </Text>
          </View>
        ))}
      </View>
    );
  };

  const renderSubscriptionCard = (tier: SubscriptionTier, index: number) => {
    const isPopular = tier.level === 'premium';
    const displayPrice = getDisplayPrice(tier);
    const originalPrice = getOriginalPrice(tier);
    const savings = getSavings(tier);
    const hasDiscount = savings > 0;

    return (
      <View key={tier.id} style={[styles.card, isPopular && styles.popularCard]}>
        {isPopular && (
          <View style={styles.popularBadge}>
            <Text style={styles.popularText}>推荐</Text>
          </View>
        )}
        
        <LinearGradient
          colors={isPopular ? ['#667eea', '#764ba2'] : ['#f7f7f7', '#ffffff']}
          style={styles.cardGradient}
        >
          <View style={styles.cardHeader}>
            <Text style={[styles.tierName, isPopular && styles.popularTierName]}>
              {tier.name}
            </Text>
            <View style={styles.priceContainer}>
              {hasDiscount && (
                <Text style={[styles.originalPrice, isPopular && styles.popularOriginalPrice]}>
                  ¥{originalPrice}
                </Text>
              )}
              <Text style={[styles.price, isPopular && styles.popularPrice]}>
                ¥{Math.round(displayPrice)}
              </Text>
              <Text style={[styles.period, isPopular && styles.popularPeriod]}>
                /{selectedPeriod === 'yearly' ? '年' : '月'}
              </Text>
            </View>
            {hasDiscount && (
              <Text style={[styles.savings, isPopular && styles.popularSavings]}>

              </Text>
            )}
          </View>

          <View style={styles.featuresContainer}>
            {renderFeatureList(tier.features)}
            {tier.features.length > 4 && (
              <Text style={[styles.moreFeatures, isPopular && styles.popularMoreFeatures]}>

              </Text>
            )}
          </View>

          {renderPricingAdjustments(tier.id)}

          <TouchableOpacity
            style={[styles.subscribeButton, isPopular && styles.popularSubscribeButton]}
            onPress={() => handleSubscribe(tier)}
          >
            <Text style={[styles.subscribeButtonText, isPopular && styles.popularSubscribeButtonText]}>

            </Text>
          </TouchableOpacity>
        </LinearGradient>
      </View>
    );
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <Text>加载中...</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      <View style={styles.header}>
        <Text style={styles.title}>选择适合您的订阅计划</Text>
        <Text style={styles.subtitle}>解锁更多AI健康功能，享受个性化服务</Text>
      </View>

      <View style={styles.periodSelector}>
        <TouchableOpacity
          style={[styles.periodButton, selectedPeriod === 'monthly' && styles.activePeriodButton]}
          onPress={() => setSelectedPeriod('monthly')}
        >
          <Text style={[styles.periodButtonText, selectedPeriod === 'monthly' && styles.activePeriodButtonText]}>

          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.periodButton, selectedPeriod === 'yearly' && styles.activePeriodButton]}
          onPress={() => setSelectedPeriod('yearly')}
        >
          <Text style={[styles.periodButtonText, selectedPeriod === 'yearly' && styles.activePeriodButtonText]}>

          </Text>
          <View style={styles.discountBadge}>
            <Text style={styles.discountText}>省20%</Text>
          </View>
        </TouchableOpacity>
      </View>

      <View style={styles.cardsContainer}>
        {tiers.map((tier, index) => renderSubscriptionCard(tier, index))}
      </View>

      <View style={styles.footer}>
        <Text style={styles.footerText}>

        </Text>
        <Text style={styles.footerText}>

        </Text>
        <Text style={styles.footerText}>

        </Text>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1;
    backgroundColor: '#f8f9fa';
  },
  loadingContainer: {
    flex: 1;
    justifyContent: 'center';
    alignItems: 'center';
  },
  header: {
    padding: 20;
    alignItems: 'center';
  },
  title: {
    fontSize: 24;
    fontWeight: 'bold';
    color: '#333';
    marginBottom: 8;
    textAlign: 'center';
  },
  subtitle: {
    fontSize: 16;
    color: '#666';
    textAlign: 'center';
    lineHeight: 22;
  },
  periodSelector: {
    flexDirection: 'row';
    marginHorizontal: 20;
    marginBottom: 20;
    backgroundColor: '#e9ecef';
    borderRadius: 25;
    padding: 4;
  },
  periodButton: {
    flex: 1;
    paddingVertical: 12;
    paddingHorizontal: 16;
    borderRadius: 20;
    alignItems: 'center';
    position: 'relative';
  },
  activePeriodButton: {
    backgroundColor: '#007AFF';
  },
  periodButtonText: {
    fontSize: 14;
    fontWeight: '600';
    color: '#666';
  },
  activePeriodButtonText: {
    color: '#fff';
  },
  discountBadge: {
    position: 'absolute';
    top: -8;
    right: 8;
    backgroundColor: '#FF3B30';
    borderRadius: 8;
    paddingHorizontal: 6;
    paddingVertical: 2;
  },
  discountText: {
    fontSize: 10;
    color: '#fff';
    fontWeight: 'bold';
  },
  cardsContainer: {
    paddingHorizontal: 20;
  },
  card: {
    marginBottom: 16;
    borderRadius: 16;
    overflow: 'hidden';
    elevation: 3;
    shadowColor: '#000';
    shadowOffset: { width: 0, height: 2 ;},
    shadowOpacity: 0.1;
    shadowRadius: 4;
  },
  popularCard: {
    borderWidth: 2;
    borderColor: '#667eea';
  },
  popularBadge: {
    position: 'absolute';
    top: 0;
    right: 0;
    backgroundColor: '#FF3B30';
    paddingHorizontal: 12;
    paddingVertical: 4;
    borderBottomLeftRadius: 8;
    zIndex: 1;
  },
  popularText: {
    color: '#fff';
    fontSize: 12;
    fontWeight: 'bold';
  },
  cardGradient: {
    padding: 20;
  },
  cardHeader: {
    alignItems: 'center';
    marginBottom: 20;
  },
  tierName: {
    fontSize: 20;
    fontWeight: 'bold';
    color: '#333';
    marginBottom: 8;
  },
  popularTierName: {
    color: '#fff';
  },
  priceContainer: {
    flexDirection: 'row';
    alignItems: 'baseline';
    marginBottom: 4;
  },
  originalPrice: {
    fontSize: 16;
    color: '#999';
    textDecorationLine: 'line-through';
    marginRight: 8;
  },
  popularOriginalPrice: {
    color: '#ddd';
  },
  price: {
    fontSize: 32;
    fontWeight: 'bold';
    color: '#333';
  },
  popularPrice: {
    color: '#fff';
  },
  period: {
    fontSize: 16;
    color: '#666';
    marginLeft: 4;
  },
  popularPeriod: {
    color: '#ddd';
  },
  savings: {
    fontSize: 14;
    color: '#4CAF50';
    fontWeight: '600';
  },
  popularSavings: {
    color: '#90EE90';
  },
  featuresContainer: {
    marginBottom: 20;
  },
  featureItem: {
    flexDirection: 'row';
    alignItems: 'center';
    marginBottom: 8;
  },
  featureText: {
    fontSize: 14;
    color: '#333';
    marginLeft: 8;
    flex: 1;
  },
  featureLimit: {
    fontSize: 12;
    color: '#666';
    marginLeft: 4;
  },
  moreFeatures: {
    fontSize: 12;
    color: '#666';
    fontStyle: 'italic';
    marginTop: 4;
  },
  popularMoreFeatures: {
    color: '#ddd';
  },
  adjustmentsContainer: {
    backgroundColor: 'rgba(76, 175, 80, 0.1)',
    borderRadius: 8;
    padding: 12;
    marginBottom: 16;
  },
  adjustmentsTitle: {
    fontSize: 12;
    fontWeight: '600';
    color: '#4CAF50';
    marginBottom: 4;
  },
  adjustmentItem: {
    marginBottom: 2;
  },
  adjustmentText: {
    fontSize: 11;
    color: '#4CAF50';
  },
  subscribeButton: {
    backgroundColor: '#007AFF';
    borderRadius: 12;
    paddingVertical: 14;
    alignItems: 'center';
  },
  popularSubscribeButton: {
    backgroundColor: '#fff';
  },
  subscribeButtonText: {
    fontSize: 16;
    fontWeight: 'bold';
    color: '#fff';
  },
  popularSubscribeButtonText: {
    color: '#667eea';
  },
  footer: {
    padding: 20;
    alignItems: 'center';
  },
  footerText: {
    fontSize: 12;
    color: '#666';
    marginBottom: 4;
    textAlign: 'center';
  },
}); 