import React, { useState, useEffect } from 'react';
import api from '../config/api';
import Toast from '../components/Toast';
import { Users, Trash2, Edit2, ShieldBan, ShieldAlert, Star } from 'lucide-react';

const AdminDashboard = () => {
  const [users, setUsers] = useState([]);
  const [feedbacks, setFeedbacks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState({ show: false, message: '', type: '' });
  const [activeTab, setActiveTab] = useState('users'); // 'users' or 'feedback'

  // Edit User Modal State
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [editingUser, setEditingUser] = useState({ id: '', name: '', email: '' });

  const showToast = (message, type) => {
    setToast({ show: true, message, type });
  };

  const fetchData = async () => {
    setLoading(true);
    try {
      if (activeTab === 'users') {
        const { data } = await api.get('/admin/users');
        setUsers(data);
      } else {
        const { data } = await api.get('/feedback');
        setFeedbacks(data);
      }
    } catch (error) {
      showToast(`Failed to load ${activeTab}`, 'error');
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchData();
  }, [activeTab]);

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this user?')) return;
    try {
      await api.delete(`/admin/users/${id}`);
      setUsers(users.filter(u => u._id !== id));
      showToast('User deleted successfully', 'success');
    } catch (error) {
      showToast(error.response?.data?.message || 'Failed to delete user', 'error');
    }
  };

  const handleToggleBlock = async (id, currentStatus) => {
    const action = currentStatus === 'active' ? 'block' : 'unblock';
    if (!window.confirm(`Are you sure you want to ${action} this user?`)) return;
    
    try {
      const { data } = await api.patch(`/admin/users/${id}/block`);
      setUsers(users.map(u => u._id === id ? { ...u, status: data.status } : u));
      showToast(data.message, 'success');
    } catch (error) {
      showToast(error.response?.data?.message || `Failed to ${action} user`, 'error');
    }
  };

  const handleEditSubmit = async (e) => {
    e.preventDefault();
    try {
      const { data } = await api.put(`/admin/users/${editingUser.id}`, {
        name: editingUser.name,
        email: editingUser.email
      });
      setUsers(users.map(u => u._id === data._id ? data : u));
      setIsEditModalOpen(false);
      showToast('User updated successfully', 'success');
    } catch (error) {
      showToast(error.response?.data?.message || 'Failed to update user', 'error');
    }
  };

  const renderStars = (rating) => {
    return (
      <div className="flex items-center text-yellow-400">
        {[...Array(5)].map((_, i) => (
          <Star key={i} size={16} className={i < rating ? 'fill-current' : 'text-gray-300'} />
        ))}
      </div>
    );
  };

  const calcAverageRating = () => {
    if (feedbacks.length === 0) return 0;
    const total = feedbacks.reduce((acc, curr) => acc + curr.rating, 0);
    return (total / feedbacks.length).toFixed(1);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        <div className="mb-8 flex justify-between items-end">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
              <ShieldAlert className="text-indigo-600" size={32} /> Admin Control Panel
            </h1>
            <p className="mt-2 text-sm text-gray-600">Manage users and view system feedback.</p>
          </div>
        </div>

        <div className="bg-white rounded-t-xl border-b border-gray-200">
          <nav className="flex space-x-8 px-6" aria-label="Tabs">
            <button
              onClick={() => setActiveTab('users')}
              className={`${
                activeTab === 'users'
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center gap-2`}
            >
              <Users size={18} /> User Management
            </button>
            <button
              onClick={() => setActiveTab('feedback')}
              className={`${
                activeTab === 'feedback'
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center gap-2`}
            >
              <Star size={18} /> Feedbacks ({feedbacks.length})
            </button>
          </nav>
        </div>

        <div className="bg-white rounded-b-xl shadow-sm border border-t-0 border-gray-200 overflow-hidden">
          {loading ? (
            <div className="p-10 text-center text-gray-500">Loading...</div>
          ) : activeTab === 'users' ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Role</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {users.map((u) => (
                    <tr key={u._id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{u.name}</div>
                        <div className="text-sm text-gray-500">{u.email}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${u.role === 'admin' ? 'bg-purple-100 text-purple-800' : 'bg-blue-100 text-blue-800'}`}>
                          {u.role}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${u.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                          {u.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex justify-end gap-3">
                          <button
                            onClick={() => {
                              setEditingUser({ id: u._id, name: u.name, email: u.email });
                              setIsEditModalOpen(true);
                            }}
                            className="text-indigo-600 hover:text-indigo-900"
                            title="Edit User"
                          >
                            <Edit2 size={18} />
                          </button>
                          
                          {u.role !== 'admin' && (
                            <>
                              <button
                                onClick={() => handleToggleBlock(u._id, u.status)}
                                className={`${u.status === 'active' ? 'text-amber-600 hover:text-amber-900' : 'text-green-600 hover:text-green-900'}`}
                                title={u.status === 'active' ? 'Block User' : 'Unblock User'}
                              >
                                <ShieldBan size={18} />
                              </button>
                              <button
                                onClick={() => handleDelete(u._id)}
                                className="text-red-600 hover:text-red-900"
                                title="Delete User"
                              >
                                <Trash2 size={18} />
                              </button>
                            </>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                  {users.length === 0 && (
                    <tr><td colSpan="4" className="px-6 py-10 text-center text-gray-500">No users found.</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="p-6">
              <div className="mb-6 flex justify-between items-center bg-gray-50 p-4 rounded-lg border border-gray-100">
                <span className="text-gray-700 font-medium">System Average Rating</span>
                <div className="flex items-center gap-2">
                  <span className="text-2xl font-bold text-gray-900">{calcAverageRating()}</span>
                  <Star className="text-yellow-400 fill-yellow-400" size={24} />
                </div>
              </div>
              <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {feedbacks.map((fb) => (
                  <div key={fb._id} className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <h4 className="text-sm font-bold text-gray-900">{fb.userId?.name || 'Unknown User'}</h4>
                        <p className="text-xs text-gray-500">{fb.userId?.email}</p>
                      </div>
                      {renderStars(fb.rating)}
                    </div>
                    <p className="text-gray-700 text-sm mt-3 bg-gray-50 p-3 rounded-lg border border-gray-100">"{fb.message}"</p>
                    <p className="text-xs text-gray-400 mt-4">{new Date(fb.createdAt).toLocaleDateString()}</p>
                  </div>
                ))}
                {feedbacks.length === 0 && (
                  <div className="col-span-full py-10 text-center text-gray-500">No feedbacks available yet.</div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Edit User Modal */}
      {isEditModalOpen && (
        <div className="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
          <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={() => setIsEditModalOpen(false)}></div>
            <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4" id="modal-title">Edit User</h3>
                <form onSubmit={handleEditSubmit}>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Name</label>
                      <input
                        type="text"
                        required
                        className="mt-1 appearance-none rounded-lg relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                        value={editingUser.name}
                        onChange={(e) => setEditingUser({...editingUser, name: e.target.value})}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Email</label>
                      <input
                        type="email"
                        required
                        className="mt-1 appearance-none rounded-lg relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                        value={editingUser.email}
                        onChange={(e) => setEditingUser({...editingUser, email: e.target.value})}
                      />
                    </div>
                  </div>
                  <div className="mt-5 sm:mt-6 sm:flex sm:flex-row-reverse">
                    <button type="submit" className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-indigo-600 text-base font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:ml-3 sm:w-auto sm:text-sm">
                      Save Changes
                    </button>
                    <button type="button" onClick={() => setIsEditModalOpen(false)} className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm">
                      Cancel
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
      )}

      {toast.show && <Toast message={toast.message} type={toast.type} onClose={() => setToast({ show: false, message: '', type: '' })} />}
    </div>
  );
};

export default AdminDashboard;
