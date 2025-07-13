import React from 'react';

interface ErrorScreenProps {
  message: string;
  retry?: () => void;
}

const ErrorScreen: React.FC<ErrorScreenProps> = ({ message, retry }) => {
  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gray-100 p-4">
      <div className="bg-white p-6 rounded-lg shadow-md max-w-md w-full text-center">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-12 w-12 text-red-500 mx-auto mb-4"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
          />
        </svg>
        <h2 className="text-xl font-semibold text-gray-800 mb-2">發生錯誤</h2>
        <p className="text-gray-600 mb-4">{message}</p>
        {retry && (
          <button
            onClick={retry}
            className="bg-purple-700 text-white py-2 px-4 rounded hover:bg-purple-800 transition-colors"
          >
            重試
          </button>
        )}
      </div>
    </div>
  );
};

export default ErrorScreen;
