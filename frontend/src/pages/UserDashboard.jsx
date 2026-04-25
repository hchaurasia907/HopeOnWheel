import React, { useState, useContext } from 'react';
import api from '../config/api';
import { AuthContext } from '../context/AuthContext';
import Toast from '../components/Toast';
import { MapPin, Navigation, Car, AlertCircle } from 'lucide-react';

const UserDashboard = () => {
  const [source, setSource] = useState('');
  const [destination, setDestination] = useState('');
  const [tripData, setTripData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState({ show: false, message: '', type: '' });

  const { user, updateWalletBalance } = useContext(AuthContext);

  const showToast = (message, type) => {
    setToast({ show: true, message, type });
  };

  const calculateCost = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const { data } = await api.post('/trip/calculate', { source, destination });
      setTripData(data);
    } catch (error) {
      showToast(error.response?.data?.message || 'Error calculating trip', 'error');
    }
    setLoading(false);
  };

  const confirmTrip = async () => {
    setLoading(true);
    try {
      const { data } = await api.post('/trip/confirm', {
        distance: tripData.distance,
        cost: tripData.estimatedCost
      });
      updateWalletBalance(data.newBalance);
      showToast('Trip confirmed! Ambulance is on its way.', 'success');
      setTripData(null);
      setSource('');
      setDestination('');
    } catch (error) {
      showToast(error.response?.data?.message || 'Error confirming trip', 'error');
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-10">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Book an Ambulance</h1>
        
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="p-8">
            <form onSubmit={calculateCost} className="space-y-6">
              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                    <MapPin size={16} className="text-indigo-500" /> Pickup Location
                  </label>
                  <input
                    type="text"
                    required
                    className="appearance-none rounded-lg block w-full px-4 py-3 border border-gray-200 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-shadow"
                    placeholder="Enter pickup location"
                    value={source}
                    onChange={(e) => setSource(e.target.value)}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                    <Navigation size={16} className="text-pink-500" /> Destination
                  </label>
                  <input
                    type="text"
                    required
                    className="appearance-none rounded-lg block w-full px-4 py-3 border border-gray-200 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-shadow"
                    placeholder="Enter destination hospital"
                    value={destination}
                    onChange={(e) => setDestination(e.target.value)}
                  />
                </div>
              </div>
              <div className="pt-2">
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full flex justify-center items-center py-3 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 shadow-md transition-all disabled:opacity-50"
                >
                  {loading ? 'Calculating...' : 'Calculate Estimated Cost'}
                </button>
              </div>
            </form>

            {tripData && (
              <div className="mt-8 animate-fade-in-up border-t border-gray-100 pt-8">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Trip Summary</h3>
                <div className="bg-indigo-50 rounded-xl p-6 border border-indigo-100">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-white p-4 rounded-lg shadow-sm">
                      <p className="text-sm text-gray-500 font-medium">Estimated Distance</p>
                      <p className="text-2xl font-bold text-gray-900 mt-1">{tripData.distance} <span className="text-base font-normal">km</span></p>
                    </div>
                    <div className="bg-white p-4 rounded-lg shadow-sm">
                      <p className="text-sm text-gray-500 font-medium">Total Cost</p>
                      <p className="text-2xl font-bold text-gray-900 mt-1">₹{tripData.estimatedCost}</p>
                    </div>
                  </div>
                  
                  <div className="mt-6 flex items-center justify-between">
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <AlertCircle size={16} />
                      Current Wallet Balance: <span className="font-semibold text-gray-900">₹{user?.walletBalance}</span>
                    </div>
                    
                    {user?.walletBalance < tripData.estimatedCost ? (
                      <div className="text-sm text-red-600 font-medium">
                        Insufficient balance. Please add money to your wallet.
                      </div>
                    ) : (
                      <button
                        onClick={confirmTrip}
                        disabled={loading}
                        className="flex items-center gap-2 py-2.5 px-6 border border-transparent text-sm font-medium rounded-lg text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 shadow-sm transition-all"
                      >
                        <Car size={18} /> Confirm Booking
                      </button>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
      {toast.show && <Toast message={toast.message} type={toast.type} onClose={() => setToast({ show: false, message: '', type: '' })} />}
    </div>
  );
};

export default UserDashboard;
