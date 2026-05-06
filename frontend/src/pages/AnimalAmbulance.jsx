import React, { useState, useEffect } from 'react';
import { PawPrint, Bell, Heart, Sparkles, Clock, ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';
import Toast from '../components/Toast';

const AnimalAmbulance = () => {
  const [email, setEmail] = useState('');
  const [notified, setNotified] = useState(false);
  const [toast, setToast] = useState({ show: false, message: '', type: '' });
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (e) => {
      setMousePos({ x: e.clientX, y: e.clientY });
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  const handleNotify = (e) => {
    e.preventDefault();
    if (email.trim()) {
      setNotified(true);
      setToast({ show: true, message: "You'll be notified when Animal Ambulance launches!", type: 'success' });
      setEmail('');
    }
  };

  const features = [
    { icon: '🐕', title: 'Pet Emergency Pickup', desc: 'Rapid response for injured or sick animals' },
    { icon: '🏥', title: 'Vet Hospital Connect', desc: 'Direct routing to nearest veterinary hospital' },
    { icon: '🩺', title: 'On-board First Aid', desc: 'Trained paravet staff with essential equipment' },
    { icon: '📍', title: 'Live GPS Tracking', desc: 'Real-time tracking of ambulance location' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-violet-950 to-slate-950 relative overflow-hidden">
      {/* Animated background orbs */}
      <div
        className="absolute w-[600px] h-[600px] rounded-full opacity-20 blur-3xl pointer-events-none transition-transform duration-[3000ms]"
        style={{
          background: 'radial-gradient(circle, #a78bfa 0%, transparent 70%)',
          left: `${mousePos.x * 0.02}px`,
          top: `${mousePos.y * 0.02}px`,
        }}
      />
      <div
        className="absolute right-0 bottom-0 w-[500px] h-[500px] rounded-full opacity-15 blur-3xl pointer-events-none transition-transform duration-[3000ms]"
        style={{
          background: 'radial-gradient(circle, #f472b6 0%, transparent 70%)',
          transform: `translate(${mousePos.x * -0.01}px, ${mousePos.y * -0.01}px)`,
        }}
      />

      {/* Floating particles */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {[...Array(20)].map((_, i) => (
          <div
            key={i}
            className="absolute rounded-full animate-pulse"
            style={{
              width: `${Math.random() * 4 + 2}px`,
              height: `${Math.random() * 4 + 2}px`,
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              backgroundColor: ['#a78bfa', '#f472b6', '#818cf8', '#c084fc'][i % 4],
              opacity: Math.random() * 0.5 + 0.2,
              animationDuration: `${Math.random() * 3 + 2}s`,
              animationDelay: `${Math.random() * 2}s`,
            }}
          />
        ))}
      </div>

      <div className="relative z-10 max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Back button */}
        <Link
          to="/dashboard"
          className="inline-flex items-center gap-2 text-violet-300 hover:text-white transition-colors mb-8 group"
        >
          <ArrowLeft size={18} className="group-hover:-translate-x-1 transition-transform" />
          <span className="text-sm font-medium">Back to Dashboard</span>
        </Link>

        {/* Hero Section */}
        <div className="text-center mt-8 mb-16">
          {/* Animated badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-violet-500/10 border border-violet-500/20 backdrop-blur-sm mb-8 animate-bounce"
               style={{ animationDuration: '3s' }}>
            <Sparkles size={14} className="text-violet-400" />
            <span className="text-violet-300 text-xs font-semibold tracking-widest uppercase">Coming Soon</span>
            <Sparkles size={14} className="text-violet-400" />
          </div>

          {/* Animated paw icon */}
          <div className="relative inline-block mb-8">
            <div className="w-28 h-28 rounded-3xl bg-gradient-to-br from-violet-600 to-pink-600 flex items-center justify-center shadow-2xl shadow-violet-500/30 mx-auto"
                 style={{ animation: 'float 4s ease-in-out infinite' }}>
              <PawPrint size={56} className="text-white" />
            </div>
            <div className="absolute -top-2 -right-2 w-8 h-8 bg-gradient-to-br from-amber-400 to-orange-500 rounded-full flex items-center justify-center animate-pulse shadow-lg">
              <Heart size={14} className="text-white" />
            </div>
          </div>

          {/* Title */}
          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-extrabold mb-6">
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-violet-400 via-pink-400 to-violet-400"
                  style={{ backgroundSize: '200%', animation: 'shimmer 3s linear infinite' }}>
              Animal Ambulance
            </span>
          </h1>
          <p className="text-xl sm:text-2xl text-gray-400 max-w-2xl mx-auto mb-4 font-light">
            Emergency veterinary transport at your fingertips.
          </p>
          <p className="text-gray-500 max-w-lg mx-auto">
            We're building a dedicated ambulance service for your beloved pets and stray animals.
            Fast, compassionate, and professional care — coming to HopeOnWheel soon.
          </p>
        </div>

        {/* Feature Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-16">
          {features.map((feature, index) => (
            <div
              key={index}
              className="group relative bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6 hover:bg-white/10 hover:border-violet-500/30 transition-all duration-500 hover:-translate-y-1 hover:shadow-xl hover:shadow-violet-500/10"
              style={{ animationDelay: `${index * 150}ms` }}
            >
              <div className="text-4xl mb-4">{feature.icon}</div>
              <h3 className="text-white font-semibold text-lg mb-2">{feature.title}</h3>
              <p className="text-gray-400 text-sm leading-relaxed">{feature.desc}</p>
              <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-violet-500/0 to-pink-500/0 group-hover:from-violet-500/5 group-hover:to-pink-500/5 transition-all duration-500" />
            </div>
          ))}
        </div>

        {/* Notification Signup */}
        <div className="max-w-xl mx-auto text-center mb-16">
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-8 sm:p-10 shadow-2xl">
            <div className="w-14 h-14 bg-gradient-to-br from-violet-500 to-pink-500 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg shadow-violet-500/25">
              <Bell size={24} className="text-white" />
            </div>
            <h2 className="text-2xl font-bold text-white mb-3">Get Notified at Launch</h2>
            <p className="text-gray-400 mb-8 text-sm">
              Be the first to know when Animal Ambulance goes live. Drop your email and we'll ping you!
            </p>

            {notified ? (
              <div className="flex items-center justify-center gap-3 py-4 px-6 rounded-2xl bg-green-500/10 border border-green-500/20">
                <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center flex-shrink-0">
                  <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <span className="text-green-300 font-medium">You're on the list! We'll notify you.</span>
              </div>
            ) : (
              <form onSubmit={handleNotify} className="flex flex-col sm:flex-row gap-3">
                <input
                  type="email"
                  required
                  placeholder="Enter your email address"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="flex-1 px-5 py-3.5 rounded-xl bg-white/10 border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent transition-all text-sm"
                />
                <button
                  type="submit"
                  className="px-8 py-3.5 bg-gradient-to-r from-violet-600 to-pink-600 hover:from-violet-500 hover:to-pink-500 text-white font-semibold rounded-xl shadow-lg shadow-violet-500/25 hover:shadow-violet-500/40 transition-all duration-300 text-sm whitespace-nowrap hover:-translate-y-0.5"
                >
                  Notify Me
                </button>
              </form>
            )}
          </div>
        </div>

        {/* Timeline */}
        <div className="max-w-2xl mx-auto mb-16">
          <h3 className="text-center text-white font-bold text-xl mb-10 flex items-center justify-center gap-2">
            <Clock size={20} className="text-violet-400" />
            Development Roadmap
          </h3>
          <div className="relative">
            {/* Vertical line */}
            <div className="absolute left-6 top-0 bottom-0 w-px bg-gradient-to-b from-violet-500 via-pink-500 to-transparent" />

            {[
              { phase: 'Phase 1', title: 'Research & Planning', status: 'done', detail: 'Partnering with veterinary clinics' },
              { phase: 'Phase 2', title: 'Fleet Preparation', status: 'progress', detail: 'Equipping vehicles with pet-care essentials' },
              { phase: 'Phase 3', title: 'App Integration', status: 'upcoming', detail: 'Building booking flow into HopeOnWheel' },
              { phase: 'Phase 4', title: 'Beta Launch', status: 'upcoming', detail: 'Pilot testing in select cities' },
            ].map((item, i) => (
              <div key={i} className="relative flex items-start gap-6 mb-8 last:mb-0">
                <div className={`relative z-10 w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 shadow-lg ${
                  item.status === 'done'
                    ? 'bg-green-500 shadow-green-500/25'
                    : item.status === 'progress'
                    ? 'bg-violet-500 shadow-violet-500/25 animate-pulse'
                    : 'bg-gray-700 shadow-gray-700/25'
                }`}>
                  {item.status === 'done' ? (
                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M5 13l4 4L19 7" />
                    </svg>
                  ) : item.status === 'progress' ? (
                    <div className="w-3 h-3 bg-white rounded-full" />
                  ) : (
                    <div className="w-3 h-3 bg-gray-500 rounded-full" />
                  )}
                </div>
                <div className="pt-1">
                  <span className="text-xs font-bold tracking-widest uppercase text-violet-400">{item.phase}</span>
                  <h4 className="text-white font-semibold text-lg mt-1">{item.title}</h4>
                  <p className="text-gray-400 text-sm mt-1">{item.detail}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Footer note */}
        <div className="text-center pb-8">
          <p className="text-gray-600 text-xs">
            🐾 Every life matters — human or animal. HopeOnWheel is expanding its mission.
          </p>
        </div>
      </div>

      {toast.show && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast({ show: false, message: '', type: '' })}
        />
      )}

      {/* Inline keyframes for custom animations */}
      <style>{`
        @keyframes float {
          0%, 100% { transform: translateY(0px) rotate(0deg); }
          50% { transform: translateY(-12px) rotate(3deg); }
        }
        @keyframes shimmer {
          0% { background-position: 200% center; }
          100% { background-position: -200% center; }
        }
      `}</style>
    </div>
  );
};

export default AnimalAmbulance;
