import { useCallback, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch } from '../store';
import {
  // Actions
  searchMedicalResources,
  getMedicalResourceDetails,
  bookAppointment,
  getUserAppointments,
  getNearbyResources,
  checkServiceHealth,
  setSelectedResource,
  setSelectedAppointment,
  updateSearchQuery,
  updateFilters,
  addToSearchHistory,
  clearSearchHistory,
  toggleFilters,
  toggleMap,
  setViewMode,
  clearError,
  clearAllErrors,
  resetState,
  
  // Selectors
  selectMedicalResources,
  selectSearchResults,
  selectSelectedResource,
  selectNearbyResources,
  selectAppointments,
  selectSelectedAppointment,
  selectSearchQuery,
  selectFilters,
  selectSearchHistory,
  selectLoading,
  selectErrors,
  selectUI,
  selectPagination,
  selectServiceHealth,
  
  // Types
  MedicalResource,
  Appointment,
  SearchQuery,
  ResourceFilters,
} from '../store/slices/medicalResourceSlice';

export const useMedicalResource = () => {
  const dispatch = useDispatch<AppDispatch>();
  
  // Selectors
  const resources = useSelector(selectMedicalResources);
  const searchResults = useSelector(selectSearchResults);
  const selectedResource = useSelector(selectSelectedResource);
  const nearbyResources = useSelector(selectNearbyResources);
  const appointments = useSelector(selectAppointments);
  const selectedAppointment = useSelector(selectSelectedAppointment);
  const searchQuery = useSelector(selectSearchQuery);
  const filters = useSelector(selectFilters);
  const searchHistory = useSelector(selectSearchHistory);
  const loading = useSelector(selectLoading);
  const errors = useSelector(selectErrors);
  const ui = useSelector(selectUI);
  const pagination = useSelector(selectPagination);
  const serviceHealth = useSelector(selectServiceHealth);
  
  // Actions
  const search = useCallback((query: SearchQuery) => {
    if (query.keyword) {
      dispatch(addToSearchHistory(query.keyword));
    }
    return dispatch(searchMedicalResources(query));
  }, [dispatch]);
  
  const getResourceDetails = useCallback((resourceId: string) => {
    return dispatch(getMedicalResourceDetails(resourceId));
  }, [dispatch]);
  
  const createAppointment = useCallback((appointmentData: Omit<Appointment, 'id' | 'status'>) => {
    return dispatch(bookAppointment(appointmentData));
  }, [dispatch]);
  
  const getAppointments = useCallback((userId: string) => {
    return dispatch(getUserAppointments(userId));
  }, [dispatch]);
  
  const findNearbyResources = useCallback((location: { lat: number; lng: number; radius?: number }) => {
    return dispatch(getNearbyResources(location));
  }, [dispatch]);
  
  const healthCheck = useCallback(() => {
    return dispatch(checkServiceHealth());
  }, [dispatch]);
  
  const selectResource = useCallback((resource: MedicalResource | null) => {
    dispatch(setSelectedResource(resource));
  }, [dispatch]);
  
  const selectAppointment = useCallback((appointment: Appointment | null) => {
    dispatch(setSelectedAppointment(appointment));
  }, [dispatch]);
  
  const updateQuery = useCallback((query: Partial<SearchQuery>) => {
    dispatch(updateSearchQuery(query));
  }, [dispatch]);
  
  const updateResourceFilters = useCallback((newFilters: Partial<ResourceFilters>) => {
    dispatch(updateFilters(newFilters));
  }, [dispatch]);
  
  const clearHistory = useCallback(() => {
    dispatch(clearSearchHistory());
  }, [dispatch]);
  
  const toggleFiltersPanel = useCallback(() => {
    dispatch(toggleFilters());
  }, [dispatch]);
  
  const toggleMapView = useCallback(() => {
    dispatch(toggleMap());
  }, [dispatch]);
  
  const changeViewMode = useCallback((mode: 'list' | 'grid' | 'map') => {
    dispatch(setViewMode(mode));
  }, [dispatch]);
  
  const clearSpecificError = useCallback((errorType: keyof typeof errors) => {
    dispatch(clearError(errorType));
  }, [dispatch, errors]);
  
  const clearErrors = useCallback(() => {
    dispatch(clearAllErrors());
  }, [dispatch]);
  
  const reset = useCallback(() => {
    dispatch(resetState());
  }, [dispatch]);
  
  // 便捷方法
  const searchByKeyword = useCallback((keyword: string, additionalFilters?: Partial<ResourceFilters>) => {
    const query: SearchQuery = {
      keyword,
      filters: { ...filters, ...additionalFilters },
      page: 1,
      limit: 20,
    };
    return search(query);
  }, [search, filters]);
  
  const searchByLocation = useCallback((location: { lat: number; lng: number; radius?: number }, resourceType?: string[]) => {
    const query: SearchQuery = {
      filters: {
        location: {
          lat: location.lat,
          lng: location.lng,
          radius: location.radius || 5000, // 默认5km
        },
        type: resourceType,
      },
      page: 1,
      limit: 20,
    };
    return search(query);
  }, [search]);
  
  const searchByType = useCallback((type: string[], additionalFilters?: Partial<ResourceFilters>) => {
    const query: SearchQuery = {
      filters: { ...filters, type, ...additionalFilters },
      page: 1,
      limit: 20,
    };
    return search(query);
  }, [search, filters]);
  
  const loadMoreResults = useCallback(() => {
    if (pagination.hasMore && !loading.search) {
      const nextPageQuery: SearchQuery = {
        ...searchQuery,
        page: pagination.currentPage + 1,
      };
      return search(nextPageQuery);
    }
  }, [search, searchQuery, pagination, loading.search]);
  
  const refreshResults = useCallback(() => {
    const refreshQuery: SearchQuery = {
      ...searchQuery,
      page: 1,
    };
    return search(refreshQuery);
  }, [search, searchQuery]);
  
  // 预约相关便捷方法
  const quickBookAppointment = useCallback((
    resourceId: string,
    resourceName: string,
    userId: string,
    serviceType: string,
    scheduledTime: string,
    duration: number = 30,
    notes?: string
  ) => {
    const appointmentData: Omit<Appointment, 'id' | 'status'> = {
      resourceId,
      resourceName,
      userId,
      serviceType,
      scheduledTime,
      duration,
      notes,
    };
    return createAppointment(appointmentData);
  }, [createAppointment]);
  
  const cancelAppointment = useCallback(async (appointmentId: string) => {
    try {
      const response = await fetch(`/api/v1/medical-resources/appointments/${appointmentId}`, {
        method: 'DELETE',
      });
      
      if (!response.ok) {
        throw new Error('取消预约失败');
      }
      
      // 重新获取预约列表
      const currentUser = ''; // 这里需要从用户状态获取
      if (currentUser) {
        getAppointments(currentUser);
      }
      
      return true;
    } catch (error) {
      console.error('取消预约失败:', error);
      return false;
    }
  }, [getAppointments]);
  
  // 筛选相关便捷方法
  const filterByRating = useCallback((minRating: number) => {
    updateResourceFilters({ rating: minRating });
  }, [updateResourceFilters]);
  
  const filterByPriceRange = useCallback((min: number, max: number) => {
    updateResourceFilters({ priceRange: { min, max } });
  }, [updateResourceFilters]);
  
  const filterByAvailability = useCallback((availability: 'now' | 'today' | 'week') => {
    updateResourceFilters({ availability });
  }, [updateResourceFilters]);
  
  const sortResults = useCallback((sortBy: 'distance' | 'rating' | 'price' | 'availability') => {
    updateResourceFilters({ sortBy });
  }, [updateResourceFilters]);
  
  const clearFilters = useCallback(() => {
    updateResourceFilters({});
  }, [updateResourceFilters]);
  
  // 自动健康检查
  useEffect(() => {
    const checkInterval = setInterval(() => {
      healthCheck();
    }, 5 * 60 * 1000); // 每5分钟检查一次
    
    // 初始检查
    healthCheck();
    
    return () => clearInterval(checkInterval);
  }, [healthCheck]);
  
  // 计算派生状态
  const hasResults = searchResults.length > 0;
  const hasNearbyResources = nearbyResources.length > 0;
  const hasAppointments = appointments.length > 0;
  const hasErrors = Object.values(errors).some(error => error !== null);
  const isLoading = Object.values(loading).some(isLoading => isLoading);
  const isHealthy = serviceHealth.status === 'healthy';
  
  const upcomingAppointments = appointments.filter(
    appointment => appointment.status === 'confirmed' && 
    new Date(appointment.scheduledTime) > new Date()
  );
  
  const pastAppointments = appointments.filter(
    appointment => appointment.status === 'completed' || 
    new Date(appointment.scheduledTime) < new Date()
  );
  
  return {
    // 数据
    resources,
    searchResults,
    selectedResource,
    nearbyResources,
    appointments,
    selectedAppointment,
    searchQuery,
    filters,
    searchHistory,
    
    // 状态
    loading,
    errors,
    ui,
    pagination,
    serviceHealth,
    
    // 派生状态
    hasResults,
    hasNearbyResources,
    hasAppointments,
    hasErrors,
    isLoading,
    isHealthy,
    upcomingAppointments,
    pastAppointments,
    
    // 基础操作
    search,
    getResourceDetails,
    createAppointment,
    getAppointments,
    findNearbyResources,
    healthCheck,
    selectResource,
    selectAppointment,
    updateQuery,
    updateResourceFilters,
    clearHistory,
    toggleFiltersPanel,
    toggleMapView,
    changeViewMode,
    clearSpecificError,
    clearErrors,
    reset,
    
    // 便捷方法
    searchByKeyword,
    searchByLocation,
    searchByType,
    loadMoreResults,
    refreshResults,
    quickBookAppointment,
    cancelAppointment,
    filterByRating,
    filterByPriceRange,
    filterByAvailability,
    sortResults,
    clearFilters,
  };
};

export default useMedicalResource; 