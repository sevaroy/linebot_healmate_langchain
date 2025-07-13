import React from 'react';

interface LoadingScreenProps {
  message?: string;
}

const LoadingScreen: React.FC<LoadingScreenProps> = ({ message = '載入中...' }) => {
  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gray-100">
      <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-purple-700 border-solid mb-4"></div>
      <p className="text-lg text-gray-700">{message}</p>
    </div>
  );
};

export default LoadingScreen;
