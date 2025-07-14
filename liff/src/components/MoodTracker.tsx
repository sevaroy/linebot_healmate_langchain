import React, { useState, useEffect } from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend } from 'chart.js';
import { Line, Bar } from 'react-chartjs-2';

// 註冊 Chart.js 組件
ChartJS.register(
  CategoryScale, 
  LinearScale, 
  PointElement, 
  LineElement, 
  BarElement,
  Title, 
  Tooltip, 
  Legend
);

interface MoodTrackerProps {
  liff: any;
  userProfile: any;
}

interface MoodEntry {
  id: string;
  date: string;
  mood: 'happy' | 'calm' | 'sad' | 'angry' | 'neutral';
  intensity: number;  // 1-10
  note: string;
  tags: string[];
}

interface MoodStats {
  [key: string]: number;
}

const MoodTracker: React.FC<MoodTrackerProps> = ({ liff, userProfile }) => {
  const [moodEntries, setMoodEntries] = useState<MoodEntry[]>([]);
  const [currentMood, setCurrentMood] = useState<'happy' | 'calm' | 'sad' | 'angry' | 'neutral' | null>(null);
  const [moodIntensity, setMoodIntensity] = useState<number>(5);
  const [moodNote, setMoodNote] = useState<string>('');
  const [moodTags, setMoodTags] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [view, setView] = useState<'entry' | 'calendar' | 'stats'>('entry');
  const [moodStats, setMoodStats] = useState<MoodStats>({});
  const [selectedDate, setSelectedDate] = useState<string>(new Date().toISOString().substring(0, 10));
  
  // 獲取心情記錄數據
  useEffect(() => {
    const fetchMoodData = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        // 在實際實現中，這裡應該從後端 API 獲取心情記錄數據
        // 這裡僅用模擬數據作為示例
        
        // 生成過去 30 天的模擬數據
        const mockData: MoodEntry[] = [];
        const moods: Array<'happy' | 'calm' | 'sad' | 'angry' | 'neutral'> = ['happy', 'calm', 'sad', 'angry', 'neutral'];
        const tags = ['工作', '家庭', '交友', '健康', '學習', '休閒'];
        
        // 生成當前日期的前 30 天數據
        for (let i = 0; i < 30; i++) {
          const date = new Date();
          date.setDate(date.getDate() - i);
          const dateStr = date.toISOString().substring(0, 10);
          
          // 隨機生成心情數據
          const randomMood = moods[Math.floor(Math.random() * moods.length)];
          const randomIntensity = Math.floor(Math.random() * 10) + 1;
          const randomTags = tags
            .filter(() => Math.random() > 0.7)
            .slice(0, Math.floor(Math.random() * 3));
          
          mockData.push({
            id: `mood-${i}`,
            date: dateStr,
            mood: randomMood,
            intensity: randomIntensity,
            note: `這是 ${dateStr} 的心情記錄`,
            tags: randomTags
          });
        }
        
        // 計算心情統計數據
        const stats: MoodStats = {
          happy: 0,
          calm: 0,
          sad: 0,
          angry: 0,
          neutral: 0
        };
        
        mockData.forEach(entry => {
          stats[entry.mood] += 1;
        });
        
        setTimeout(() => {
          setMoodEntries(mockData);
          setMoodStats(stats);
          setIsLoading(false);
        }, 1000);
      } catch (err) {
        setError('獲取心情記錄失敗，請稍後再試。');
        console.error('Error fetching mood data:', err);
        setIsLoading(false);
      }
    };
    
    fetchMoodData();
  }, [userProfile]);
  
  // 提交心情記錄
  const handleSubmitMood = async () => {
    if (!currentMood) {
      setError('請選擇一個心情狀態');
      return;
    }
    if (!userProfile || !userProfile.userId) {
      setError('無法獲取用戶資訊，請重新登入。');
      return;
    }
    
    setIsSubmitting(true);
    setError(null);
    
    try {
      // ** REAL IMPLEMENTATION **
      // Send mood data to the backend API
      const response = await fetch('/mood', { // Assuming the backend is on the same host or proxied
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userProfile.userId,
          mood: currentMood,
          intensity: moodIntensity,
          note: moodNote,
          tags: moodTags.length > 0 ? moodTags : null, # Send null if no tags
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to save mood to the server.');
      }

      const result = await response.json();

      // Create a new entry for the local state
      const newMoodEntry: MoodEntry = {
        id: result.entry_id, // Use the ID from the backend
        date: selectedDate,
        mood: currentMood,
        intensity: moodIntensity,
        note: moodNote,
        tags: moodTags
      };
      
      // Update local state
      setMoodEntries(prev => [newMoodEntry, ...prev]);
      setMoodStats(prev => ({
        ...prev,
        [currentMood]: (prev[currentMood] || 0) + 1
      }));
      
      // Clear the form
      setCurrentMood(null);
      setMoodIntensity(5);
      setMoodNote('');
      setMoodTags([]);
      
      // Show success message
      alert('心情記錄已保存！');

    } catch (err) {
      setError('保存心情記錄失敗，請稍後再試。');
      console.error('Error submitting mood:', err);
    } finally {
      setIsSubmitting(false);
    }
  };
  
  // 獲取心情圖標
  const getMoodIcon = (mood: string) => {
    switch(mood) {
      case 'happy': return '😊';
      case 'calm': return '😌';
      case 'sad': return '😢';
      case 'angry': return '😠';
      case 'neutral': return '😐';
      default: return '❓';
    }
  };
  
  // 獲取心情顏色
  const getMoodColor = (mood: string) => {
    switch(mood) {
      case 'happy': return '#FFD700';
      case 'calm': return '#87CEFA';
      case 'sad': return '#B0C4DE';
      case 'angry': return '#FA8072';
      case 'neutral': return '#E0E0E0';
      default: return '#CCCCCC';
    }
  };
  
  // 統計圖表數據
  const statsData = {
    labels: ['開心', '平靜', '難過', '生氣', '中性'],
    datasets: [
      {
        label: '心情分布',
        data: [
          moodStats.happy || 0,
          moodStats.calm || 0,
          moodStats.sad || 0,
          moodStats.angry || 0,
          moodStats.neutral || 0
        ],
        backgroundColor: [
          '#FFD700',
          '#87CEFA',
          '#B0C4DE',
          '#FA8072',
          '#E0E0E0'
        ],
      },
    ],
  };

  // 心情趨勢數據 (過去14天)
  const trendData = {
    labels: moodEntries.slice(0, 14).reverse().map(entry => {
      const date = new Date(entry.date);
      return `${date.getMonth() + 1}/${date.getDate()}`;
    }),
    datasets: [
      {
        label: '心情強度',
        data: moodEntries.slice(0, 14).reverse().map(entry => entry.intensity),
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.3,
        fill: false,
      },
    ],
  };

  // 添加或移除標籤
  const toggleTag = (tag: string) => {
    if (moodTags.includes(tag)) {
      setMoodTags(moodTags.filter(t => t !== tag));
    } else {
      setMoodTags([...moodTags, tag]);
    }
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-10">
        <div className="animate-spin rounded-full h-12 w-12 border-t-4 border-green-600 border-solid mb-4"></div>
        <p>載入心情記錄中...</p>
      </div>
    );
  }

  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">心情日記</h2>
      
      {/* 頁籤切換 */}
      <div className="flex border-b border-gray-200 mb-4">
        <button 
          className={`py-2 px-4 ${view === 'entry' ? 'border-b-2 border-green-600 font-medium' : 'text-gray-600'}`}
          onClick={() => setView('entry')}
        >
          記錄心情
        </button>
        <button 
          className={`py-2 px-4 ${view === 'calendar' ? 'border-b-2 border-green-600 font-medium' : 'text-gray-600'}`}
          onClick={() => setView('calendar')}
        >
          心情日曆
        </button>
        <button 
          className={`py-2 px-4 ${view === 'stats' ? 'border-b-2 border-green-600 font-medium' : 'text-gray-600'}`}
          onClick={() => setView('stats')}
        >
          統計分析
        </button>
      </div>
      
      {/* 記錄心情視圖 */}
      {view === 'entry' && (
        <div>
          <div className="mb-4">
            <label className="block mb-2 font-medium">選擇日期</label>
            <input 
              type="date"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              className="border border-gray-300 rounded px-3 py-2 w-full"
            />
          </div>
          
          <div className="mb-4">
            <label className="block mb-2 font-medium">你現在的心情如何？</label>
            <div className="grid grid-cols-5 gap-2">
              {['happy', 'calm', 'sad', 'angry', 'neutral'].map((mood) => (
                <button
                  key={mood}
                  className={`p-3 rounded-lg flex flex-col items-center ${currentMood === mood ? 'ring-2 ring-green-600' : 'bg-gray-50'}`}
                  style={{ backgroundColor: currentMood === mood ? getMoodColor(mood) : undefined }}
                  onClick={() => setCurrentMood(mood as any)}
                >
                  <span className="text-2xl mb-1">{getMoodIcon(mood)}</span>
                  <span>
                    {mood === 'happy' && '開心'}
                    {mood === 'calm' && '平靜'}
                    {mood === 'sad' && '難過'}
                    {mood === 'angry' && '生氣'}
                    {mood === 'neutral' && '一般'}
                  </span>
                </button>
              ))}
            </div>
          </div>
          
          {currentMood && (
            <>
              <div className="mb-4">
                <label className="block mb-2 font-medium">強度 (1-10)</label>
                <input 
                  type="range" 
                  min="1" 
                  max="10"
                  value={moodIntensity}
                  onChange={(e) => setMoodIntensity(parseInt(e.target.value))}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-600">
                  <span>輕微</span>
                  <span>中等</span>
                  <span>強烈</span>
                </div>
              </div>
              
              <div className="mb-4">
                <label className="block mb-2 font-medium">添加標籤</label>
                <div className="flex flex-wrap gap-2">
                  {['工作', '家庭', '交友', '健康', '學習', '休閒'].map(tag => (
                    <button
                      key={tag}
                      className={`px-3 py-1 rounded-full text-sm ${moodTags.includes(tag) ? 'bg-green-600 text-white' : 'bg-gray-200 text-gray-800'}`}
                      onClick={() => toggleTag(tag)}
                    >
                      {tag}
                    </button>
                  ))}
                </div>
              </div>
              
              <div className="mb-4">
                <label className="block mb-2 font-medium">心情筆記</label>
                <textarea
                  value={moodNote}
                  onChange={(e) => setMoodNote(e.target.value)}
                  placeholder="寫下您今天的感受..."
                  className="border border-gray-300 rounded px-3 py-2 w-full h-32 resize-none"
                ></textarea>
              </div>
              
              <button
                onClick={handleSubmitMood}
                disabled={isSubmitting || !currentMood}
                className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition-colors w-full disabled:bg-gray-400"
              >
                {isSubmitting ? '保存中...' : '記錄心情'}
              </button>
            </>
          )}
        </div>
      )}
      
      {/* 心情日曆視圖 */}
      {view === 'calendar' && (
        <div>
          <h3 className="font-medium mb-3">最近 30 天的心情記錄</h3>
          <div className="grid grid-cols-7 gap-1">
            {['一', '二', '三', '四', '五', '六', '日'].map(day => (
              <div key={day} className="text-center text-sm font-medium py-1">
                {day}
              </div>
            ))}
            
            {/* 生成日曆視圖 */}
            {Array(35).fill(0).map((_, index) => {
              // 計算日期 (從今天開始往回倒30天，然後填充剩餘的格子)
              const today = new Date();
              const date = new Date();
              date.setDate(today.getDate() - (34 - index));
              const dateStr = date.toISOString().substring(0, 10);
              
              // 查找這一天的心情記錄
              const entry = moodEntries.find(e => e.date === dateStr);
              
              // 如果有記錄，顯示顏色；否則顯示空白
              return (
                <div 
                  key={index}
                  className="aspect-square rounded"
                  style={{ 
                    backgroundColor: entry ? getMoodColor(entry.mood) : '#F3F4F6',
                    opacity: entry ? (entry.intensity / 10) * 0.5 + 0.5 : 0.3
                  }}
                  title={entry ? `${dateStr}: ${entry.note}` : dateStr}
                >
                  <div className="text-xs text-center pt-1">
                    {date.getDate()}
                  </div>
                  {entry && (
                    <div className="flex justify-center items-center h-3/4 text-lg">
                      {getMoodIcon(entry.mood)}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
      
      {/* 統計分析視圖 */}
      {view === 'stats' && (
        <div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            {/* 心情分布圖 */}
            <div className="bg-white p-4 rounded-lg shadow">
              <h4 className="font-medium mb-3 text-center">心情分布</h4>
              <Bar 
                data={statsData}
                options={{
                  responsive: true,
                  plugins: {
                    legend: {
                      position: 'top' as const,
                      display: false
                    },
                    title: {
                      display: false
                    }
                  }
                }}
              />
            </div>
            
            {/* 心情趨勢圖 */}
            <div className="bg-white p-4 rounded-lg shadow">
              <h4 className="font-medium mb-3 text-center">過去 14 天心情強度趨勢</h4>
              <Line
                data={trendData}
                options={{
                  responsive: true,
                  plugins: {
                    legend: {
                      position: 'top' as const,
                    },
                    title: {
                      display: false
                    }
                  },
                  scales: {
                    y: {
                      min: 0,
                      max: 10
                    }
                  }
                }}
              />
            </div>
          </div>
          
          {/* 心情洞察 */}
          <div className="bg-green-50 border border-green-200 p-4 rounded-lg">
            <h4 className="font-medium mb-2">心情洞察</h4>
            <p>
              根據您過去 30 天的心情記錄，您有 {((moodStats.happy || 0) / moodEntries.length * 100).toFixed(0)}% 的時間感到開心，
              {((moodStats.calm || 0) / moodEntries.length * 100).toFixed(0)}% 的時間感到平靜。
              這個月您的心情整體趨於穩定，比上個月有所改善。
              <br/><br/>
              建議多參與讓您感到開心的活動，例如與朋友聚會或從事您喜愛的興趣愛好，這有助於維持良好的情緒。
            </p>
          </div>
        </div>
      )}
      
      {error && (
        <div className="bg-red-50 border border-red-200 p-3 rounded-lg mt-4 text-red-800">
          {error}
        </div>
      )}
    </div>
  );
};

export default MoodTracker;
