import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

interface DashboardProps {
  liff: any;
  userProfile: any;
}

interface RecentActivity {
  id: string;
  type: 'tarot' | 'zodiac' | 'mood';
  title: string;
  date: string;
  summary: string;
}

const Dashboard: React.FC<DashboardProps> = ({ liff, userProfile }) => {
  const [recentActivities, setRecentActivities] = useState<RecentActivity[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [todayFortune, setTodayFortune] = useState<string | null>(null);

  useEffect(() => {
    // 在實際實現中，這裡應該從後端 API 獲取數據
    // 這裡僅用模擬數據作為示例
    const mockActivities: RecentActivity[] = [
      {
        id: '1',
        type: 'tarot',
        title: '愚者正位',
        date: '2025-07-11',
        summary: '新的開始與冒險，無憂無慮地踏上旅程'
      },
      {
        id: '2',
        type: 'zodiac',
        title: '金牛座',
        date: '2025-07-10',
        summary: '財務運勢上升，工作中可能有意外收穫'
      },
      {
        id: '3',
        type: 'mood',
        title: '開心',
        date: '2025-07-09',
        summary: '今天是美好的一天，完成了許多計劃的事情'
      }
    ];

    // 模擬今日運勢
    const mockTodayFortune = "今天的整體運勢不錯，適合開展新的項目。心情將保持愉快，可能會收到好消息。建議多關注人際關係，可能有意外的社交機會。";

    // 模擬API請求延遲
    setTimeout(() => {
      setRecentActivities(mockActivities);
      setTodayFortune(mockTodayFortune);
      setIsLoading(false);
    }, 1000);

  }, [userProfile]);

  const getActivityIcon = (type: string) => {
    switch(type) {
      case 'tarot':
        return '🃏';
      case 'zodiac':
        return '⭐';
      case 'mood':
        return '😊';
      default:
        return '📝';
    }
  };

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-xl font-semibold mb-3">歡迎回來{userProfile?.displayName ? ', ' + userProfile.displayName : ''}!</h2>
        <div className="bg-gradient-to-r from-purple-100 to-blue-100 p-4 rounded-lg border border-purple-200">
          <h3 className="font-medium mb-2">今日運勢</h3>
          {isLoading ? (
            <div className="animate-pulse h-16 bg-gray-200 rounded"></div>
          ) : (
            <p>{todayFortune}</p>
          )}
        </div>
      </div>

      <div className="mb-6">
        <h3 className="text-lg font-medium mb-3">快速訪問</h3>
        <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
          <Link to="/tarot" className="bg-purple-600 text-white p-3 rounded-lg text-center hover:bg-purple-700 transition-colors">
            塔羅牌占卜
          </Link>
          <Link to="/zodiac" className="bg-blue-600 text-white p-3 rounded-lg text-center hover:bg-blue-700 transition-colors">
            星座運勢
          </Link>
          <Link to="/mood" className="bg-green-600 text-white p-3 rounded-lg text-center hover:bg-green-700 transition-colors">
            心情日記
          </Link>
          <Link to="/history" className="bg-gray-600 text-white p-3 rounded-lg text-center hover:bg-gray-700 transition-colors">
            歷史記錄
          </Link>
        </div>
      </div>

      <div>
        <h3 className="text-lg font-medium mb-3">最近活動</h3>
        {isLoading ? (
          <div className="space-y-3">
            {[1, 2, 3].map(i => (
              <div key={i} className="animate-pulse flex p-3 bg-gray-100 rounded-lg">
                <div className="h-10 w-10 bg-gray-300 rounded-full"></div>
                <div className="ml-3 flex-1">
                  <div className="h-3 bg-gray-300 rounded w-3/4 mb-2"></div>
                  <div className="h-3 bg-gray-300 rounded w-1/2"></div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="space-y-3">
            {recentActivities.map(activity => (
              <div key={activity.id} className="flex p-3 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors">
                <div className="h-10 w-10 bg-white rounded-full flex items-center justify-center text-xl">
                  {getActivityIcon(activity.type)}
                </div>
                <div className="ml-3">
                  <div className="font-medium">{activity.title}</div>
                  <div className="text-sm text-gray-600">{activity.date} - {activity.summary}</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
