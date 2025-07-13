import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import liff from '@line/liff';
import { ApiService } from '../services/api';

interface LiffContextType {
  liffObject: typeof liff | null;
  isLoggedIn: boolean;
  userProfile: any;
  isLoading: boolean;
  error: string | null;
  login: () => Promise<void>;
  logout: () => void;
}

const LiffContext = createContext<LiffContextType>({
  liffObject: null,
  isLoggedIn: false,
  userProfile: null,
  isLoading: true,
  error: null,
  login: async () => {},
  logout: () => {},
});

interface LiffProviderProps {
  children: ReactNode;
  liffId: string;
}

export const LiffProvider: React.FC<LiffProviderProps> = ({ children, liffId }) => {
  const [liffObject, setLiffObject] = useState<typeof liff | null>(null);
  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(false);
  const [userProfile, setUserProfile] = useState<any>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // 初始化 LIFF
  useEffect(() => {
    const initializeLiff = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        // 初始化 LIFF SDK
        await liff.init({ liffId });
        setLiffObject(liff);
        
        // 檢查登入狀態
        const loggedIn = liff.isLoggedIn();
        setIsLoggedIn(loggedIn);
        
        if (loggedIn) {
          await fetchUserProfile();
        }
      } catch (err) {
        console.error('LIFF 初始化失敗:', err);
        setError('LIFF 初始化失敗，請稍後再試');
      } finally {
        setIsLoading(false);
      }
    };
    
    initializeLiff();
  }, [liffId]);
  
  // 獲取用戶資料
  const fetchUserProfile = async () => {
    try {
      // 獲取 LINE 用戶資料
      const profile = await liff.getProfile();
      
      // 獲取 LINE 訪問令牌
      const token = liff.getAccessToken();
      
      if (token) {
        // 儲存 token 到本地儲存
        localStorage.setItem('lineAccessToken', token);
        
        // 驗證用戶並獲取完整資料
        const response = await ApiService.verifyUser(token);
        if (response.success && response.data) {
          setUserProfile({
            ...profile,
            ...response.data
          });
        } else {
          // 如果後端驗證失敗，僅使用 LINE 提供的基本資料
          setUserProfile(profile);
        }
      } else {
        setUserProfile(profile);
      }
    } catch (err) {
      console.error('獲取用戶資料失敗:', err);
      setError('獲取用戶資料失敗');
    }
  };
  
  // 登入
  const login = async () => {
    try {
      if (!liffObject) {
        throw new Error('LIFF 尚未初始化');
      }
      
      if (!liffObject.isLoggedIn()) {
        // LINE 登入（會重定向到 LINE 登入頁面）
        liffObject.login();
      } else {
        // 已登入，獲取用戶資料
        setIsLoggedIn(true);
        await fetchUserProfile();
      }
    } catch (err) {
      console.error('登入失敗:', err);
      setError('登入失敗，請稍後再試');
    }
  };
  
  // 登出
  const logout = () => {
    try {
      if (!liffObject) {
        throw new Error('LIFF 尚未初始化');
      }
      
      if (liffObject.isLoggedIn()) {
        // 清除本地儲存的令牌
        localStorage.removeItem('lineAccessToken');
        
        // LINE 登出
        liffObject.logout();
        
        // 更新狀態
        setIsLoggedIn(false);
        setUserProfile(null);
      }
    } catch (err) {
      console.error('登出失敗:', err);
      setError('登出失敗，請稍後再試');
    }
  };
  
  const value = {
    liffObject,
    isLoggedIn,
    userProfile,
    isLoading,
    error,
    login,
    logout
  };
  
  return (
    <LiffContext.Provider value={value}>
      {children}
    </LiffContext.Provider>
  );
};

// 自定義 Hook，方便在組件中獲取 LIFF 上下文
export const useLiff = () => {
  const context = useContext(LiffContext);
  if (context === undefined) {
    throw new Error('useLiff must be used within a LiffProvider');
  }
  return context;
};

export default LiffContext;
