import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface TarotReaderProps {
  liff: any;
  userProfile: any;
}

interface TarotCard {
  id: number;
  name: string;
  image: string;
  uprightMeaning: string;
  reversedMeaning: string;
  description: string;
}

const TarotReader: React.FC<TarotReaderProps> = ({ liff, userProfile }) => {
  const [cards, setCards] = useState<TarotCard[]>([]);
  const [selectedCards, setSelectedCards] = useState<TarotCard[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isReading, setIsReading] = useState(false);
  const [readingResult, setReadingResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [spreadType, setSpreadType] = useState<'single' | 'three' | 'celtic'>('single');
  const [flippedCards, setFlippedCards] = useState<number[]>([]);

  useEffect(() => {
    // 在實際實現中，這裡應該從後端 API 獲取塔羅牌數據
    // 這裡僅用模擬數據作為示例
    const mockTarotCards: TarotCard[] = [
      {
        id: 0,
        name: '愚者',
        image: '/assets/tarot-cards/fool.jpg',
        uprightMeaning: '新的開始，冒險，純真',
        reversedMeaning: '魯莽，冒失，風險',
        description: '愚者是一張代表新開始和無限可能的牌。它象徵著旅程的開始，以及無憂無慮地追尋夢想的勇氣。'
      },
      {
        id: 1,
        name: '魔術師',
        image: '/assets/tarot-cards/magician.jpg',
        uprightMeaning: '創造力，技巧，機智',
        reversedMeaning: '操縱，欺騙，未實現的才能',
        description: '魔術師代表意識和潛能的力量，象徵著將想法轉化為現實的能力和掌握自己命運的力量。'
      },
      {
        id: 2,
        name: '女祭司',
        image: '/assets/tarot-cards/high-priestess.jpg',
        uprightMeaning: '直覺，潛意識，神秘',
        reversedMeaning: '秘密，隱藏的情感，表面知識',
        description: '女祭司代表內在的知識和直覺，象徵著對未知和神秘事物的理解，以及潛意識的力量。'
      },
      {
        id: 3,
        name: '皇后',
        image: '/assets/tarot-cards/empress.jpg',
        uprightMeaning: '豐饒，母性，創造力',
        reversedMeaning: '依賴，過度保護，創意阻塞',
        description: '皇后象徵著豐饒、成長和滋養。她代表著母性能量、創造力和自然的循環。'
      },
      {
        id: 4,
        name: '皇帝',
        image: '/assets/tarot-cards/emperor.jpg',
        uprightMeaning: '權威，結構，控制',
        reversedMeaning: '獨裁，僵化，過度控制',
        description: '皇帝代表權威和結構，象徵著邏輯思維、領導能力和建立秩序的能力。'
      }
      // 實際應用中應該有完整的78張塔羅牌
    ];

    setTimeout(() => {
      setCards(mockTarotCards);
      setIsLoading(false);
    }, 1000);
  }, []);

  const shuffleCards = () => {
    // 洗牌算法
    const shuffled = [...cards];
    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
      
      // 50% 機率牌面是逆位
      shuffled[i] = {
        ...shuffled[i],
        isReversed: Math.random() > 0.5
      };
    }
    return shuffled;
  };

  const startReading = () => {
    setIsReading(true);
    setReadingResult(null);
    setFlippedCards([]);
    
    const shuffled = shuffleCards();
    
    // 根據不同的牌陣選擇不同數量的卡片
    let numberOfCards = 1;
    if (spreadType === 'three') numberOfCards = 3;
    if (spreadType === 'celtic') numberOfCards = 10;
    
    setSelectedCards(shuffled.slice(0, numberOfCards));
  };

  const flipCard = (index: number) => {
    if (flippedCards.includes(index)) return;
    
    setFlippedCards(prev => [...prev, index]);
    
    // 如果所有卡片都被翻開，則生成解讀結果
    if (flippedCards.length + 1 === selectedCards.length) {
      generateReading();
    }
  };

  const generateReading = () => {
    // 在實際實現中，這裡應該調用後端 API 來生成塔羅牌解讀
    // 這裡僅用模擬數據作為示例
    setTimeout(() => {
      const result = `根據您抽到的牌，我看到您目前處於一個新的開始階段。愚者牌顯示您正在開始一段新的旅程，充滿可能性和機會。
      
      這段時期對您來說充滿了探索和發現。不要害怕未知，因為正是這種未知將帶給您成長和經驗。
      
      建議您保持開放的心態，接受新的挑戰，並且相信自己的直覺。雖然前方的道路可能不明確，但這正是成長的一部分。`;
      
      setReadingResult(result);
    }, 1500);
  };

  const handleSpreadTypeChange = (type: 'single' | 'three' | 'celtic') => {
    setSpreadType(type);
    setIsReading(false);
    setReadingResult(null);
    setSelectedCards([]);
    setFlippedCards([]);
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-10">
        <div className="animate-spin rounded-full h-12 w-12 border-t-4 border-purple-700 border-solid mb-4"></div>
        <p>載入塔羅牌資料中...</p>
      </div>
    );
  }

  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">塔羅牌閱讀</h2>
      
      {!isReading ? (
        <div className="mb-6">
          <div className="mb-4">
            <h3 className="font-medium mb-2">選擇牌陣</h3>
            <div className="flex flex-wrap gap-2">
              <button 
                className={`px-4 py-2 rounded ${spreadType === 'single' ? 'bg-purple-600 text-white' : 'bg-gray-200 text-gray-800'}`}
                onClick={() => handleSpreadTypeChange('single')}
              >
                單張牌陣
              </button>
              <button 
                className={`px-4 py-2 rounded ${spreadType === 'three' ? 'bg-purple-600 text-white' : 'bg-gray-200 text-gray-800'}`}
                onClick={() => handleSpreadTypeChange('three')}
              >
                三張牌陣
              </button>
              <button 
                className={`px-4 py-2 rounded ${spreadType === 'celtic' ? 'bg-purple-600 text-white' : 'bg-gray-200 text-gray-800'}`}
                onClick={() => handleSpreadTypeChange('celtic')}
              >
                凱爾特十字牌陣
              </button>
            </div>
          </div>
          
          <button 
            className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 transition-colors w-full"
            onClick={startReading}
          >
            開始塔羅牌閱讀
          </button>
          
          <p className="text-sm text-gray-600 mt-2">
            {spreadType === 'single' && '單張牌陣適合回答簡單、明確的問題。'}
            {spreadType === 'three' && '三張牌陣代表過去、現在和未來，適合了解特定情境的發展。'}
            {spreadType === 'celtic' && '凱爾特十字牌陣是複雜的牌陣，可以深入分析當前情況的多個方面。'}
          </p>
        </div>
      ) : (
        <div>
          <div className="flex justify-between items-center mb-4">
            <h3 className="font-medium">
              {spreadType === 'single' && '單張牌陣'}
              {spreadType === 'three' && '過去、現在與未來'}
              {spreadType === 'celtic' && '凱爾特十字牌陣'}
            </h3>
            <button 
              className="text-sm text-purple-700 hover:text-purple-900"
              onClick={() => setIsReading(false)}
            >
              重新開始
            </button>
          </div>
          
          <div className="flex flex-wrap justify-center gap-4 mb-6">
            {selectedCards.map((card, index) => (
              <div 
                key={index} 
                className={`tarot-card ${flippedCards.includes(index) ? 'flipped' : ''}`}
                onClick={() => flipCard(index)}
              >
                <div className="tarot-card-inner">
                  <div className="tarot-card-front flex items-center justify-center">
                    <span className="text-white text-lg">塔羅</span>
                  </div>
                  <div className="tarot-card-back p-2">
                    <h4 className="text-center font-medium text-sm mb-1">{card.name}</h4>
                    <div className="text-xs text-gray-600 text-center">
                      {card.isReversed ? '(逆位)' : '(正位)'}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          {flippedCards.length > 0 && flippedCards.length < selectedCards.length && (
            <p className="text-center text-sm text-gray-600 mb-4">
              點擊卡片翻開，已翻開 {flippedCards.length}/{selectedCards.length} 張卡片
            </p>
          )}
          
          {readingResult && (
            <div className="bg-purple-50 border border-purple-200 p-4 rounded-lg">
              <h3 className="font-medium mb-2">塔羅牌解讀</h3>
              <p className="whitespace-pre-line">{readingResult}</p>
            </div>
          )}
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

export default TarotReader;
