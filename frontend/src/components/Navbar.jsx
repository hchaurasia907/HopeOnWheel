import React, { useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { LogOut, Wallet, User, ShieldAlert, PawPrint } from 'lucide-react';

const Navbar = () => {
  const { user, logout } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="bg-white shadow-md border-b border-gray-100 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link to={user?.role === 'admin' ? '/admin' : '/dashboard'} className="flex-shrink-0 flex items-center">
              <span className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600">
                HopeOnWheel
              </span>
            </Link>
          </div>
          
          <div className="flex items-center space-x-4">
            {user ? (
              <>
                {user.role === 'admin' && (
                  <Link to="/admin" className="text-gray-500 hover:text-indigo-600 px-3 py-2 rounded-md text-sm font-medium flex items-center gap-1 transition-colors">
                    <ShieldAlert size={18} /> Admin
                  </Link>
                )}
                {user.role === 'user' && (
                  <>
                    <Link to="/dashboard" className="text-gray-500 hover:text-indigo-600 px-3 py-2 rounded-md text-sm font-medium transition-colors">
                      Book Trip
                    </Link>
                    <Link to="/animal-ambulance" className="relative text-gray-500 hover:text-violet-600 px-3 py-2 rounded-md text-sm font-medium flex items-center gap-1 transition-colors">
                      <PawPrint size={18} /> Animal
                      <span className="absolute -top-1 -right-1 px-1.5 py-0.5 text-[10px] font-bold bg-gradient-to-r from-violet-500 to-pink-500 text-white rounded-full leading-none">
                        NEW
                      </span>
                    </Link>
                    <Link to="/wallet" className="text-gray-500 hover:text-indigo-600 px-3 py-2 rounded-md text-sm font-medium flex items-center gap-1 transition-colors">
                      <Wallet size={18} /> ₹{user.walletBalance || 0}
                    </Link>
                    <Link to="/feedback" className="text-gray-500 hover:text-indigo-600 px-3 py-2 rounded-md text-sm font-medium transition-colors">
                      Feedback
                    </Link>
                  </>
                )}
                
                <div className="relative ml-3 group">
                  <div className="flex items-center gap-2 cursor-pointer text-gray-700 hover:text-gray-900 transition-colors">
                    <div className="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-600">
                      <User size={18} />
                    </div>
                    <span className="text-sm font-medium hidden sm:block">{user.name}</span>
                  </div>
                  
                  {/* Dropdown - Simple hover based */}
                  <div className="absolute right-0 w-48 mt-2 origin-top-right bg-white rounded-md shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 border border-gray-100">
                    <div className="py-1">
                      <button
                        onClick={handleLogout}
                        className="flex w-full items-center px-4 py-2 text-sm text-red-600 hover:bg-gray-50"
                      >
                        <LogOut size={16} className="mr-2" />
                        Sign out
                      </button>
                    </div>
                  </div>
                </div>
              </>
            ) : (
              <div className="space-x-2">
                <Link to="/login" className="text-gray-600 hover:text-indigo-600 px-3 py-2 text-sm font-medium transition-colors">Login</Link>
                <Link to="/register" className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors shadow-sm">Register</Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
