import React, { useState, useEffect, useContext } from 'react';
import api from '../config/api';
import { AuthContext } from '../context/AuthContext';
import Toast from '../components/Toast';
import { Plus, ArrowUpRight, ArrowDownRight, Wallet as WalletIcon } from 'lucide-react';

const WalletPage = () => {
  const [walletData, setWalletData] = useState({ balance: 0, transactions: [] });
  const [amountToAdd, setAmountToAdd] = useState('');
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState({ show: false, message: '', type: '' });

  const { updateWalletBalance } = useContext(AuthContext);

  const fetchWallet = async () => {
    try {
      const { data } = await api.get('/wallet');
      setWalletData(data);
    } catch (error) {
      showToast('Failed to fetch wallet data', 'error');
    }
  };

  useEffect(() => {
    fetchWallet();
  }, []);

  const showToast = (message, type) => {
    setToast({ show: true, message, type });
  };

  const handleAddMoney = async (e) => {
    e.preventDefault();
    if (!amountToAdd || amountToAdd <= 0) {
      showToast('Please enter a valid amount', 'error');
      return;
    }

    setLoading(true);
    try {
      const { data } = await api.post('/wallet/add-money', { amount: Number(amountToAdd) });
      setWalletData(prev => ({
        balance: data.balance,
        transactions: [data.transaction, ...prev.transactions]
      }));
      updateWalletBalance(data.balance);
      showToast('Money added successfully!', 'success');
      setAmountToAdd('');
    } catch (error) {
      showToast(error.response?.data?.message || 'Failed to add money', 'error');
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-10">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8 flex items-center gap-3">
          <WalletIcon className="text-indigo-600" size={32} /> My Wallet
        </h1>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Balance and Add Money Card */}
          <div className="md:col-span-1 space-y-6">
            {/* Balance Card */}
            <div className="bg-gradient-to-br from-indigo-600 to-purple-700 rounded-2xl p-6 text-white shadow-xl">
              <p className="text-indigo-100 text-sm font-medium mb-1">Available Balance</p>
              <h2 className="text-4xl font-bold">₹{walletData.balance}</h2>
            </div>
            
            {/* Add Money Card */}
            <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Add Money</h3>
              <form onSubmit={handleAddMoney}>
                <div className="relative mb-4">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <span className="text-gray-500 sm:text-sm">₹</span>
                  </div>
                  <input
                    type="number"
                    min="1"
                    className="focus:ring-indigo-500 focus:border-indigo-500 block w-full pl-7 pr-12 sm:text-sm border-gray-300 rounded-lg py-3 appearance-none border transition-colors bg-gray-50 focus:bg-white"
                    placeholder="0.00"
                    value={amountToAdd}
                    onChange={(e) => setAmountToAdd(e.target.value)}
                  />
                </div>
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full flex justify-center items-center py-2.5 px-4 border border-transparent shadow-sm text-sm font-medium rounded-lg text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-all disabled:opacity-50"
                >
                  <Plus size={16} className="mr-2" /> {loading ? 'Processing...' : 'Add to Wallet'}
                </button>
              </form>
            </div>
          </div>

          {/* Transaction History */}
          <div className="md:col-span-2">
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
              <div className="px-6 py-5 border-b border-gray-100">
                <h3 className="text-lg font-semibold text-gray-900">Transaction History</h3>
              </div>
              <ul className="divide-y divide-gray-100 max-h-[600px] overflow-y-auto">
                {walletData.transactions.length === 0 ? (
                  <li className="px-6 py-8 text-center text-gray-500">No transactions found.</li>
                ) : (
                  walletData.transactions.map((tx) => (
                    <li key={tx._id} className="px-6 py-4 hover:bg-gray-50 transition-colors">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center">
                          <div className={`p-2 rounded-full ${tx.type === 'credit' ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'}`}>
                            {tx.type === 'credit' ? <ArrowDownRight size={20} /> : <ArrowUpRight size={20} />}
                          </div>
                          <div className="ml-4">
                            <p className="text-sm font-medium text-gray-900 capitalize">{tx.type} to wallet</p>
                            <p className="text-xs text-gray-500">{new Date(tx.createdAt).toLocaleString()}</p>
                          </div>
                        </div>
                        <div className={`font-semibold ${tx.type === 'credit' ? 'text-green-600' : 'text-red-600'}`}>
                          {tx.type === 'credit' ? '+' : '-'}₹{tx.amount}
                        </div>
                      </div>
                    </li>
                  ))
                )}
              </ul>
            </div>
          </div>
        </div>
      </div>
      {toast.show && <Toast message={toast.message} type={toast.type} onClose={() => setToast({ show: false, message: '', type: '' })} />}
    </div>
  );
};

export default WalletPage;
