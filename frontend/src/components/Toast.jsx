import React, { useEffect } from 'react';
import { CheckCircle, XCircle, X } from 'lucide-react';

const Toast = ({ message, type = 'success', onClose }) => {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, 3000);
    return () => clearTimeout(timer);
  }, [onClose]);

  if (!message) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50 flex items-center p-4 mb-4 text-gray-500 bg-white rounded-lg shadow-lg border border-gray-100 animate-fade-in-up">
      <div className={`inline-flex items-center justify-center flex-shrink-0 w-8 h-8 rounded-lg ${type === 'success' ? 'text-green-500 bg-green-100' : 'text-red-500 bg-red-100'}`}>
        {type === 'success' ? <CheckCircle size={20} /> : <XCircle size={20} />}
      </div>
      <div className="ml-3 text-sm font-normal text-gray-800 pr-5">{message}</div>
      <button 
        type="button" 
        className="ml-auto -mx-1.5 -my-1.5 bg-white text-gray-400 hover:text-gray-900 rounded-lg focus:ring-2 focus:ring-gray-300 p-1.5 hover:bg-gray-100 inline-flex"
        onClick={onClose}
      >
        <span className="sr-only">Close</span>
        <X size={16} />
      </button>
    </div>
  );
};

export default Toast;
