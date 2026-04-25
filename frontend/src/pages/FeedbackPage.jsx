import React, { useState } from 'react';
import api from '../config/api';
import Toast from '../components/Toast';
import { Star, MessageSquare } from 'lucide-react';

const FeedbackPage = () => {
  const [rating, setRating] = useState(0);
  const [hoverRating, setHoverRating] = useState(0);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState({ show: false, message: '', type: '' });

  const showToast = (toastMessage, type) => {
    setToast({ show: true, message: toastMessage, type });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (rating === 0) {
      showToast('Please select a star rating', 'error');
      return;
    }

    setLoading(true);
    try {
      await api.post('/feedback', { rating, message });
      showToast('Thank you for your feedback!', 'success');
      setRating(0);
      setMessage('');
    } catch (error) {
      showToast(error.response?.data?.message || 'Failed to submit feedback', 'error');
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-10">
      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8 text-center">Share Your Experience</h1>
        
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8">
          <form onSubmit={handleSubmit} className="space-y-8">
            {/* Star Rating System */}
            <div className="flex flex-col items-center">
              <label className="block text-sm font-medium text-gray-700 mb-4">How was your trip?</label>
              <div className="flex items-center space-x-2 cursor-pointer">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    type="button"
                    onClick={() => setRating(star)}
                    onMouseEnter={() => setHoverRating(star)}
                    onMouseLeave={() => setHoverRating(0)}
                    className="focus:outline-none transition-transform hover:scale-110"
                  >
                    <Star
                      size={40}
                      className={(hoverRating || rating) >= star ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'}
                    />
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                <MessageSquare size={16} className="text-indigo-500" /> Additional Comments
              </label>
              <textarea
                required
                rows="4"
                className="appearance-none rounded-lg block w-full px-4 py-3 border border-gray-200 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-shadow resize-none"
                placeholder="Tell us what you loved or what we can improve..."
                value={message}
                onChange={(e) => setMessage(e.target.value)}
              ></textarea>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 shadow-md transition-all disabled:opacity-50"
            >
              {loading ? 'Submitting...' : 'Submit Feedback'}
            </button>
          </form>
        </div>
      </div>
      {toast.show && <Toast message={toast.message} type={toast.type} onClose={() => setToast({ show: false, message: '', type: '' })} />}
    </div>
  );
};

export default FeedbackPage;
