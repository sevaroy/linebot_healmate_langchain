import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, RadialLinearScale, BarElement } from 'chart.js';
import { Line, Radar, Bar } from 'react-chartjs-2';

// 註冊 Chart.js 組件
ChartJS.register(
  CategoryScale, 
  LinearScale, 
  PointElement, 
  LineElement, 
  RadialLinearScale,
  BarElement,
  Title, 
  Tooltip, 
  Legend
);

interface ZodiacFortuneProps {
  liff: any;
  userProfile: any;
}

interface ZodiacSign {
  name: string;
  nameEn: string;
  element: string;
  dates: string;
  icon: string;
}

interface FortuneData {
  love: number;
  career: number;
  health: number;
  wealth: number;
  overall: number;
}

interface WeeklyFortune {
  day: string;
  overall: number;
}

const ZodiacFortune: React.FC<ZodiacFortuneProps> = ({ liff, userProfile }) => {
  const [selectedSign, setSelectedSign] = useState<string | null>(null);
  const [fortuneData, setFortuneData] = useState<FortuneData | null>(null);
  const [weeklyFortune, setWeeklyFortune] = useState<WeeklyFortune[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fortuneText, setFortuneText] = useState<string | null>(null);
  
  // 星座資料
  const zodiacSigns: ZodiacSign[] = [
    { name: '牡羊座', nameEn: 'Aries', element: '火象', dates: '3/21 - 4/19', icon: '♈' },
    { name: '金牛座', nameEn: 'Taurus', element: '土象', dates: '4/20 - 5/20', icon: '♉' },
    { name: '雙子座', nameEn: 'Gemini', element: '風象', dates: '5/21 - 6/21', icon: '♊' },
    { name: '巨蟹座', nameEn: 'Cancer', element: '水象', dates: '6/22 - 7/22', icon: '♋' },
    { name: '獅子座', nameEn: 'Leo', element: '火象', dates: '7/23 - 8/22', icon: '♌' },
    { name: '處女座', nameEn: 'Virgo', element: '土象', dates: '8/23 - 9/22', icon: '♍' },
    { name: '天秤座', nameEn: 'Libra', element: '風象', dates: '9/23 - 10/23', icon: '♎' },
    { name: '天蠍座', nameEn: 'Scorpio', element: '水象', dates: '10/24 - 11/22', icon: '♏' },
    { name: '射手座', nameEn: 'Sagittarius', element: '火象', dates: '11/23 - 12/21', icon: '♐' },
    { name: '摩羯座', nameEn: 'Capricorn', element: '土象', dates: '12/22 - 1/19', icon: '♑' },
    { name: '水瓶座', nameEn: 'Aquarius', element: '風象', dates: '1/20 - 2/18', icon: '♒' },
    { name: '雙魚座', nameEn: 'Pisces', element: '水象', dates: '2/19 - 3/20', icon: '♓' },
  ];

  // 選擇星座時獲取運勢資料
  const fetchFortuneData = async (sign: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      // 在實際實現中，這裡應該從後端 API 獲取星座運勢數據
      // 這裡僅用模擬數據作為示例
      
      // 模擬 API 延遲
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // 隨機生成運勢數據
      const mockFortuneData: FortuneData = {
        love: Math.floor(Math.random() * 30) + 70, // 70-100 之間的隨機數
        career: Math.floor(Math.random() * 30) + 70,
        health: Math.floor(Math.random() * 30) + 70,
        wealth: Math.floor(Math.random() * 30) + 70,
        overall: Math.floor(Math.random() * 30) + 70
      };
      
      // 隨機生成每週運勢數據
      const days = ['一', '二', '三', '四', '五', '六', '日'];
      const mockWeeklyFortune = days.map(day => ({
        day: `週${day}`,
        overall: Math.floor(Math.random() * 30) + 70
      }));
      
      // 模擬運勢文字描述
      const mockFortuneText = `今日整體運勢: ${mockFortuneData.overall}%\n
對於${sign}來說，今天是個充滿能量的日子。在感情方面，您可能會遇到意想不到的機會，保持開放的心態。
工作上，您的創意思維將幫助您解決複雜問題，同事們會對您的貢獻表示讚賞。
財務方面要保持謹慎，避免衝動消費。健康狀況良好，但記得保持規律的作息時間。
今天的幸運色是紫色，幸運數字是7。`;
      
      setFortuneData(mockFortuneData);
      setWeeklyFortune(mockWeeklyFortune);
      setFortuneText(mockFortuneText);
    } catch (err) {
      setError('獲取星座運勢資料失敗，請稍後再試。');
      console.error('Error fetching fortune data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // 用戶選擇星座
  const handleSelectSign = (sign: string) => {
    setSelectedSign(sign);
    fetchFortuneData(sign);
  };

  // 雷達圖配置
  const radarData = fortuneData ? {
    labels: ['愛情運', '事業運', '健康運', '財運', '整體運'],
    datasets: [
      {
        label: '今日運勢',
        data: [fortuneData.love, fortuneData.career, fortuneData.health, fortuneData.wealth, fortuneData.overall],
        backgroundColor: 'rgba(125, 46, 189, 0.2)',
        borderColor: 'rgba(125, 46, 189, 1)',
        borderWidth: 2,
      },
    ],
  } : null;
  
  // 折線圖配置
  const lineData = {
    labels: weeklyFortune.map(item => item.day),
    datasets: [
      {
        label: '每週運勢趨勢',
        data: weeklyFortune.map(item => item.overall),
        borderColor: 'rgba(46, 134, 193, 1)',
        backgroundColor: 'rgba(46, 134, 193, 0.2)',
        tension: 0.3,
      },
    ],
  };
  
  // 折線圖選項
  const lineOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: '每週運勢趨勢',
      },
    },
  };

  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">星座運勢</h2>
      
      {!selectedSign ? (
        <div>
          <h3 className="font-medium mb-3">請選擇您的星座</h3>
          <div className="grid grid-cols-3 md:grid-cols-4 gap-3">
            {zodiacSigns.map((sign) => (
              <button
                key={sign.name}
                className="bg-white border border-gray-200 rounded-lg p-3 hover:bg-purple-50 hover:border-purple-300 transition-colors text-center"
                onClick={() => handleSelectSign(sign.name)}
              >
                <div className="text-2xl mb-1">{sign.icon}</div>
                <div className="font-medium">{sign.name}</div>
                <div className="text-xs text-gray-600">{sign.dates}</div>
              </button>
            ))}
          </div>
        </div>
      ) : (
        <div>
          <div className="flex justify-between items-center mb-4">
            <h3 className="font-medium">
              {zodiacSigns.find(s => s.name === selectedSign)?.icon} {selectedSign} 運勢
            </h3>
            <button 
              className="text-sm text-purple-700 hover:text-purple-900"
              onClick={() => setSelectedSign(null)}
            >
              選擇其他星座
            </button>
          </div>
          
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-10">
              <div className="animate-spin rounded-full h-12 w-12 border-t-4 border-purple-700 border-solid mb-4"></div>
              <p>獲取星座運勢中...</p>
            </div>
          ) : (
            <div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                {/* 雷達圖 - 今日運勢 */}
                <div className="bg-white p-4 rounded-lg shadow">
                  <h4 className="font-medium mb-3 text-center">今日各項運勢</h4>
                  {radarData && <Radar data={radarData} />}
                </div>
                
                {/* 折線圖 - 每週運勢趨勢 */}
                <div className="bg-white p-4 rounded-lg shadow">
                  <h4 className="font-medium mb-3 text-center">每週運勢趨勢</h4>
                  <Line options={lineOptions} data={lineData} />
                </div>
              </div>
              
              {/* 運勢詳細解釋 */}
              <div className="bg-purple-50 border border-purple-200 p-4 rounded-lg">
                <h4 className="font-medium mb-2">運勢解析</h4>
                <p className="whitespace-pre-line">{fortuneText}</p>
              </div>
              
              {/* 相容星座 */}
              <div className="mt-6">
                <h4 className="font-medium mb-3">相容星座</h4>
                <div className="grid grid-cols-3 gap-2">
                  {/* 隨機選擇三個相容星座 */}
                  {zodiacSigns
                    .filter(sign => sign.name !== selectedSign)
                    .sort(() => 0.5 - Math.random())
                    .slice(0, 3)
                    .map(sign => (
                      <div key={sign.name} className="bg-white border border-gray-200 rounded-lg p-3 text-center">
                        <div className="text-xl">{sign.icon}</div>
                        <div>{sign.name}</div>
                      </div>
                    ))
                  }
                </div>
              </div>
            </div>
          )}
          
          {error && (
            <div className="bg-red-50 border border-red-200 p-3 rounded-lg mt-4 text-red-800">
              {error}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ZodiacFortune;
