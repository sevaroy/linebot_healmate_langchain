import axios, { AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';

// API 基本路徑
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// 創建 axios 實例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 請求攔截器 - 為每個請求添加驗證 token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('lineAccessToken');
    if (token && config.headers) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 響應攔截器 - 處理常見錯誤
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response) {
      const { status } = error.response;
      if (status === 401) {
        // 未授權，重新登錄
        localStorage.removeItem('lineAccessToken');
        // 可以在這裡重新初始化 LIFF
      } else if (status >= 500) {
        // 伺服器錯誤
        console.error('Server error:', error.response.data);
      }
    }
    return Promise.reject(error);
  }
);

// API 接口類型定義
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
}

// 用戶相關接口
export interface UserProfile {
  userId: string;
  displayName: string;
  pictureUrl?: string;
  statusMessage?: string;
  email?: string;
  zodiacSign?: string;
  preferences?: Record<string, any>;
}

// 塔羅牌相關接口
export interface TarotCard {
  id: number;
  name: string;
  name_cn: string;
  arcana: 'major' | 'minor';
  suit?: string;
  value?: number;
  upright_meaning: string;
  reversed_meaning: string;
  image_url: string;
}

export interface TarotReading {
  id: string;
  userId: string;
  date: string;
  question: string;
  spread: 'single' | 'three-card' | 'celtic-cross';
  cards: Array<{
    card: TarotCard;
    position: string;
    isReversed: boolean;
  }>;
  interpretation: string;
}

// 星座運勢相關接口
export interface ZodiacFortune {
  id: string;
  userId: string;
  date: string;
  sign: string;
  overall: number;
  love: number;
  career: number;
  health: number;
  wealth: number;
  description: string;
  luckyNumbers: number[];
  compatibleSigns: string[];
}

// 心情日記相關接口
export interface MoodEntry {
  id: string;
  userId: string;
  date: string;
  mood: 'happy' | 'calm' | 'sad' | 'angry' | 'neutral';
  intensity: number;
  note: string;
  tags: string[];
}

// API 服務類
export const ApiService = {
  // 用戶認證
  async verifyUser(lineAccessToken: string): Promise<ApiResponse<UserProfile>> {
    try {
      const response = await apiClient.post<ApiResponse<UserProfile>>('/api/auth/verify', { lineAccessToken });
      return response.data;
    } catch (error) {
      console.error('Error verifying user:', error);
      return { success: false, message: '用戶驗證失敗' };
    }
  },

  // 更新用戶資料
  async updateUserProfile(profile: Partial<UserProfile>): Promise<ApiResponse<UserProfile>> {
    try {
      const response = await apiClient.put<ApiResponse<UserProfile>>('/api/users/profile', profile);
      return response.data;
    } catch (error) {
      console.error('Error updating profile:', error);
      return { success: false, message: '更新資料失敗' };
    }
  },

  // 塔羅牌占卜
  async getTarotCards(): Promise<ApiResponse<TarotCard[]>> {
    try {
      const response = await apiClient.get<ApiResponse<TarotCard[]>>('/api/tarot/cards');
      return response.data;
    } catch (error) {
      console.error('Error getting tarot cards:', error);
      return { success: false, message: '獲取塔羅牌資料失敗' };
    }
  },

  async createTarotReading(data: {
    question: string;
    spread: 'single' | 'three-card' | 'celtic-cross';
  }): Promise<ApiResponse<TarotReading>> {
    try {
      const response = await apiClient.post<ApiResponse<TarotReading>>('/api/tarot/readings', data);
      return response.data;
    } catch (error) {
      console.error('Error creating tarot reading:', error);
      return { success: false, message: '創建塔羅牌占卜失敗' };
    }
  },

  async getTarotReadings(params?: {
    limit?: number;
    offset?: number;
  }): Promise<ApiResponse<TarotReading[]>> {
    try {
      const response = await apiClient.get<ApiResponse<TarotReading[]>>('/api/tarot/readings', { params });
      return response.data;
    } catch (error) {
      console.error('Error getting tarot readings:', error);
      return { success: false, message: '獲取塔羅牌占卜歷史失敗' };
    }
  },

  async getTarotReadingById(id: string): Promise<ApiResponse<TarotReading>> {
    try {
      const response = await apiClient.get<ApiResponse<TarotReading>>(`/api/tarot/readings/${id}`);
      return response.data;
    } catch (error) {
      console.error('Error getting tarot reading:', error);
      return { success: false, message: '獲取塔羅牌占卜詳情失敗' };
    }
  },

  // 星座運勢
  async getZodiacFortune(sign: string, date?: string): Promise<ApiResponse<ZodiacFortune>> {
    try {
      const response = await apiClient.get<ApiResponse<ZodiacFortune>>('/api/zodiac/fortune', {
        params: { sign, date }
      });
      return response.data;
    } catch (error) {
      console.error('Error getting zodiac fortune:', error);
      return { success: false, message: '獲取星座運勢失敗' };
    }
  },

  async getZodiacFortuneHistory(params?: {
    sign?: string;
    limit?: number;
    offset?: number;
  }): Promise<ApiResponse<ZodiacFortune[]>> {
    try {
      const response = await apiClient.get<ApiResponse<ZodiacFortune[]>>('/api/zodiac/history', { params });
      return response.data;
    } catch (error) {
      console.error('Error getting zodiac fortune history:', error);
      return { success: false, message: '獲取星座運勢歷史失敗' };
    }
  },

  // 心情日記
  async createMoodEntry(data: Omit<MoodEntry, 'id' | 'userId'>): Promise<ApiResponse<MoodEntry>> {
    try {
      const response = await apiClient.post<ApiResponse<MoodEntry>>('/api/mood/entries', data);
      return response.data;
    } catch (error) {
      console.error('Error creating mood entry:', error);
      return { success: false, message: '保存心情記錄失敗' };
    }
  },

  async getMoodEntries(params?: {
    startDate?: string;
    endDate?: string;
    limit?: number;
    offset?: number;
  }): Promise<ApiResponse<MoodEntry[]>> {
    try {
      const response = await apiClient.get<ApiResponse<MoodEntry[]>>('/api/mood/entries', { params });
      return response.data;
    } catch (error) {
      console.error('Error getting mood entries:', error);
      return { success: false, message: '獲取心情記錄失敗' };
    }
  },

  async getMoodStats(params?: {
    startDate?: string;
    endDate?: string;
  }): Promise<ApiResponse<Record<string, any>>> {
    try {
      const response = await apiClient.get<ApiResponse<Record<string, any>>>('/api/mood/stats', { params });
      return response.data;
    } catch (error) {
      console.error('Error getting mood stats:', error);
      return { success: false, message: '獲取心情統計數據失敗' };
    }
  },

  async deleteMoodEntry(id: string): Promise<ApiResponse<void>> {
    try {
      const response = await apiClient.delete<ApiResponse<void>>(`/api/mood/entries/${id}`);
      return response.data;
    } catch (error) {
      console.error('Error deleting mood entry:', error);
      return { success: false, message: '刪除心情記錄失敗' };
    }
  },

  // 歷史記錄 - 綜合查詢
  async getUserHistory(params?: {
    type?: 'tarot' | 'zodiac' | 'mood';
    limit?: number;
    offset?: number;
    startDate?: string;
    endDate?: string;
  }): Promise<ApiResponse<any[]>> {
    try {
      const response = await apiClient.get<ApiResponse<any[]>>('/api/history', { params });
      return response.data;
    } catch (error) {
      console.error('Error getting user history:', error);
      return { success: false, message: '獲取歷史記錄失敗' };
    }
  }
};

export default ApiService;
