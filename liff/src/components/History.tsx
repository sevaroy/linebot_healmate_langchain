import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

interface HistoryProps {
  liff: any;
  userProfile: any;
}

interface HistoryEntry {
  id: string;
  type: 'tarot' | 'zodiac' | 'mood';
  title: string;
  date: string;
  summary: string;
  content?: string;
  icon?: string;
}

const History: React.FC<HistoryProps> = ({ liff, userProfile }) => {
  const [historyEntries, setHistoryEntries] = useState<HistoryEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterType, setFilterType] = useState<'all' | 'tarot' | 'zodiac' | 'mood'>('all');
  const [selectedEntry, setSelectedEntry] = useState<HistoryEntry | null>(null);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    // 在實際實現中，這裡應該從後端 API 獲取歷史記錄數據
    // 這裡僅用模擬數據作為示例
    const fetchHistory = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        // 模擬 API 延遲
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // 模擬歷史記錄數據
        const mockHistory: HistoryEntry[] = [
          {
            id: 'tarot-1',
            type: 'tarot',
            title: '愚者 (正位)',
            date: '2025-07-11',
            summary: '新的開始與冒險',
            content: '愚者牌代表了新的開始和無限可能。您當前正處於一個人生的新階段，充滿了機遇和挑戰。保持開放的心態，勇敢地面對未知的旅程。不要害怕犯錯，因為每一步都是學習和成長的機會。',
            icon: '🃏'
          },
          {
            id: 'zodiac-1',
            type: 'zodiac',
            title: '金牛座週運',
            date: '2025-07-10',
            summary: '財務運勢上升',
            content: '本週金牛座的財務運勢特別好，可能會有意外的收入或投資機會。工作方面，您的努力將得到認可，可能有晉升或獎勵的機會。感情方面保持穩定，與伴侶的關係更加和諧。健康狀況良好，但要注意休息，避免過度勞累。',
            icon: '♉'
          },
          {
            id: 'mood-1',
            type: 'mood',
            title: '開心',
            date: '2025-07-09',
            summary: '今天完成了許多計劃的事情',
            content: '今天的心情非常好！完成了許多計劃中的事情，工作效率很高。與朋友共進晚餐，聊了很多有趣的話題。感覺自己充滿能量，對未來充滿期待。',
            icon: '😊'
          },
          {
            id: 'tarot-2',
            type: 'tarot',
            title: '星星 (正位)',
            date: '2025-07-08',
            summary: '希望與靈感',
            content: '星星牌象徵著希望、靈感和內在的指引。這張牌出現在您的占卜中，表示您正在經歷一段充滿希望和靈性覺醒的時期。相信宇宙的指引，保持樂觀的態度，即使在黑暗時刻也能看到光明。您的創造力正處於高峰期，是實現夢想的好時機。',
            icon: '🃏'
          },
          {
            id: 'zodiac-2',
            type: 'zodiac',
            title: '雙子座月運',
            date: '2025-07-05',
            summary: '溝通能力提升',
            content: '本月雙子座的溝通能力特別強，是表達想法和進行談判的好時機。社交圈可能會擴大，有機會認識有趣的新朋友。工作方面可能會有新的項目或合作機會。財務狀況穩定，但要避免衝動消費。健康方面要注意神經緊張，適當放鬆。',
            icon: '♊'
          },
          {
            id: 'mood-2',
            type: 'mood',
            title: '平靜',
            date: '2025-07-02',
            summary: '度過了寧靜的一天',
            content: '今天過得很平靜，花了一些時間獨處和思考。閱讀了一本好書，喝了喜歡的茶。雖然沒有特別的事情發生，但這種平靜的感覺很舒適。適當的獨處時間對心靈很有幫助。',
            icon: '😌'
          },
          {
            id: 'tarot-3',
            type: 'tarot',
            title: '正義 (逆位)',
            date: '2025-06-30',
            summary: '不公平與失衡',
            content: '正義牌逆位表示可能存在不公平或失衡的情況。您可能感到某些事情不太公平，或者在道德決策上面臨困難。這是一個檢視自己是否客觀公正的時刻，避免因主觀偏見而做出不公正的判斷。同時也要警惕他人可能的不誠實行為。',
            icon: '🃏'
          },
          {
            id: 'mood-3',
            type: 'mood',
            title: '難過',
            date: '2025-06-28',
            summary: '遇到了一些挫折',
            content: '今天心情不太好，工作上遇到了一些挫折。計劃的項目沒有按預期進行，感到有些沮喪。嘗試調整心態，明白這只是暫時的困難。明天會是新的一天，問題總會有解決的方法。',
            icon: '😢'
          }
        ];
        
        setHistoryEntries(mockHistory);
        setIsLoading(false);
      } catch (err) {
        setError('獲取歷史記錄失敗，請稍後再試');
        console.error('Error fetching history:', err);
        setIsLoading(false);
      }
    };
    
    fetchHistory();
  }, [userProfile]);

  // 篩選歷史記錄
  const filteredEntries = filterType === 'all'
    ? historyEntries
    : historyEntries.filter(entry => entry.type === filterType);

  // 查看詳細內容
  const viewDetail = (entry: HistoryEntry) => {
    setSelectedEntry(entry);
    setShowModal(true);
  };

  // 刪除歷史記錄
  const deleteEntry = async (id: string) => {
    if (window.confirm('確定要刪除這條記錄嗎？')) {
      try {
        // 在實際實現中，這裡應該向後端 API 發送刪除請求
        // 這裡僅模擬前端刪除
        setHistoryEntries(entries => entries.filter(entry => entry.id !== id));
        
        if (selectedEntry && selectedEntry.id === id) {
          setShowModal(false);
          setSelectedEntry(null);
        }
      } catch (err) {
        setError('刪除記錄失敗，請稍後再試');
        console.error('Error deleting entry:', err);
      }
    }
  };

  // 獲取類型圖標
  const getTypeIcon = (type: string) => {
    switch(type) {
      case 'tarot': return '🃏';
      case 'zodiac': return '⭐';
      case 'mood': return '😊';
      default: return '📝';
    }
  };
  
  // 獲取類型名稱
  const getTypeName = (type: string) => {
    switch(type) {
      case 'tarot': return '塔羅牌';
      case 'zodiac': return '星座運勢';
      case 'mood': return '心情日記';
      default: return '記錄';
    }
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-10">
        <div className="animate-spin rounded-full h-12 w-12 border-t-4 border-purple-700 border-solid mb-4"></div>
        <p>載入歷史記錄中...</p>
      </div>
    );
  }

  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">歷史記錄</h2>
      
      {/* 篩選選項 */}
      <div className="mb-4 flex space-x-2">
        <button
          className={`px-4 py-2 rounded-lg ${filterType === 'all' ? 'bg-purple-600 text-white' : 'bg-gray-200'}`}
          onClick={() => setFilterType('all')}
        >
          全部
        </button>
        <button
          className={`px-4 py-2 rounded-lg ${filterType === 'tarot' ? 'bg-purple-600 text-white' : 'bg-gray-200'}`}
          onClick={() => setFilterType('tarot')}
        >
          塔羅牌
        </button>
        <button
          className={`px-4 py-2 rounded-lg ${filterType === 'zodiac' ? 'bg-purple-600 text-white' : 'bg-gray-200'}`}
          onClick={() => setFilterType('zodiac')}
        >
          星座運勢
        </button>
        <button
          className={`px-4 py-2 rounded-lg ${filterType === 'mood' ? 'bg-purple-600 text-white' : 'bg-gray-200'}`}
          onClick={() => setFilterType('mood')}
        >
          心情日記
        </button>
      </div>
      
      {/* 歷史記錄列表 */}
      {filteredEntries.length > 0 ? (
        <div className="space-y-3">
          {filteredEntries.map(entry => (
            <div key={entry.id} className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex justify-between">
                <div className="flex items-start">
                  <div className="h-10 w-10 bg-gray-100 rounded-full flex items-center justify-center text-xl mr-3">
                    {entry.icon || getTypeIcon(entry.type)}
                  </div>
                  <div>
                    <h3 className="font-medium">{entry.title}</h3>
                    <div className="flex space-x-2 text-sm text-gray-600 mt-1">
                      <span>{entry.date}</span>
                      <span>•</span>
                      <span>{getTypeName(entry.type)}</span>
                    </div>
                    <p className="text-sm text-gray-700 mt-2">{entry.summary}</p>
                  </div>
                </div>
                <button 
                  onClick={() => viewDetail(entry)}
                  className="text-purple-700 hover:text-purple-900 text-sm"
                >
                  查看詳情
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-gray-50 p-8 text-center rounded-lg border border-gray-200">
          <p className="text-gray-600 mb-4">沒有找到相關記錄</p>
          {filterType !== 'all' && (
            <button
              className="text-purple-700 hover:text-purple-900"
              onClick={() => setFilterType('all')}
            >
              查看所有記錄
            </button>
          )}
        </div>
      )}
      
      {/* 詳情模態窗 */}
      {showModal && selectedEntry && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-lg w-full max-h-[80vh] overflow-y-auto">
            <div className="p-5">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-medium flex items-center">
                  <span className="mr-2">{selectedEntry.icon || getTypeIcon(selectedEntry.type)}</span>
                  {selectedEntry.title}
                </h3>
                <button 
                  onClick={() => setShowModal(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  ✕
                </button>
              </div>
              
              <div className="mb-4 text-sm text-gray-600">
                <div>{selectedEntry.date}</div>
                <div>{getTypeName(selectedEntry.type)}</div>
              </div>
              
              <div className="border-t border-gray-200 py-4">
                <p className="whitespace-pre-line">{selectedEntry.content}</p>
              </div>
              
              <div className="flex justify-between pt-4 border-t border-gray-200 mt-4">
                <button
                  onClick={() => deleteEntry(selectedEntry.id)}
                  className="text-red-600 hover:text-red-800 text-sm"
                >
                  刪除記錄
                </button>
                
                <button
                  onClick={() => setShowModal(false)}
                  className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors"
                >
                  關閉
                </button>
              </div>
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
  );
};

export default History;
