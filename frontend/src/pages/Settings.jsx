import { useState, useEffect } from 'react';
import { FiUser, FiBell, FiMoon, FiSun, FiGlobe, FiLogOut, FiSave, FiShield, FiCamera } from 'react-icons/fi';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import { authService } from '../services/authService';

const Settings = () => {
  const [activeTab, setActiveTab] = useState('Profile');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [profile, setProfile] = useState(null);
  const [formData, setFormData] = useState({});
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  const [passwordData, setPasswordData] = useState({ current: '', new: '', confirm: '' });

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      setLoading(true);
      const data = await authService.getMe();
      setProfile(data);
      setFormData({
        full_name: data.full_name || '',
        theme: data.theme || 'dark',
        notifications_enabled: data.notifications_enabled,
        language: data.language || 'en',
        profile_picture_url: data.profile_picture_url || ''
      });
    } catch (err) {
      console.error(err);
      setError("Failed to load profile.");
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (e) => {
    e?.preventDefault();
    try {
      setSaving(true);
      setError('');
      setSuccess('');
      const updated = await authService.updateProfile(formData);
      setProfile(updated);
      setSuccess('Settings updated successfully!');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      console.error(err);
      setError('Failed to save settings.');
      setSaving(false);
    }
  };

  const handlePasswordChange = async (e) => {
    e.preventDefault();
    if (passwordData.new !== passwordData.confirm) {
      setError("New passwords do not match.");
      return;
    }
    try {
      setSaving(true);
      setError('');
      setSuccess('');
      await authService.changePassword(passwordData.current, passwordData.new, passwordData.confirm);
      setSuccess("Password updated successfully!");
      setPasswordData({ current: '', new: '', confirm: '' });
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      console.error(err);
      setError("Failed to change password. Please check your current password.");
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteAccount = async () => {
    if (!window.confirm("Are you absolutely sure you want to delete your account? This action cannot be undone.")) return;
    try {
      await authService.deleteAccount();
      window.location.href = '/login';
    } catch (err) {
      console.error(err);
      alert("Failed to delete account.");
    }
  };

  if (loading) return <div className="p-8 text-center text-gray-600">Loading Settings...</div>;

  return (
    <div className="max-w-5xl mx-auto space-y-8 pb-12">
      <div>
        <h1 className="text-3xl font-bold tracking-tight mb-2">Settings</h1>
        <p className="text-[var(--color-text-muted)]">Manage your account, preferences, and AI configurations.</p>
      </div>

      {error && <div className="p-4 bg-red-900/50 border border-red-500 rounded-xl text-red-200">{error}</div>}
      {success && <div className="p-4 bg-emerald-900/50 border border-emerald-500 rounded-xl text-emerald-200">{success}</div>}

      <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
        
        {/* Settings Sidebar */}
        <div className="md:col-span-1 space-y-2">
          {['Profile', 'Appearance', 'Notifications', 'Language', 'Security'].map((item) => (
            <button 
              key={item}
              onClick={() => setActiveTab(item)}
              className={`w-full text-left px-4 py-3 rounded-xl transition-all font-medium flex items-center justify-between group ${
                activeTab === item 
                  ? 'bg-blue-500 text-gray-900 shadow-sm' 
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              }`}
            >
              {item}
            </button>
          ))}
        </div>

        {/* Settings Content */}
        <div className="md:col-span-3 space-y-8">
          
          <form onSubmit={handleSave}>
            {activeTab === 'Profile' && (
              <Card hover={false} className="p-8">
                <h2 className="text-xl font-bold flex items-center gap-2 mb-8 text-gray-900">
                  <FiUser className="text-blue-500" /> Profile Settings
                </h2>
                <div className="flex flex-col sm:flex-row gap-8 items-start">
                  <div className="relative group">
                    {formData.profile_picture_url ? (
                      <img src={formData.profile_picture_url} alt="Profile" className="w-28 h-28 rounded-2xl object-cover shadow-sm" />
                    ) : (
                      <div className="w-28 h-28 rounded-2xl bg-gradient-to-br from-blue-500 to-indigo-600 text-white flex items-center justify-center text-4xl font-bold shadow-sm">
                        {formData.full_name?.charAt(0) || 'U'}
                      </div>
                    )}
                    <button type="button" onClick={() => {
                        const url = prompt("Enter Image URL");
                        if (url !== null) setFormData({...formData, profile_picture_url: url});
                      }} 
                      className="absolute inset-0 bg-black/60 rounded-2xl flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity text-gray-900 cursor-pointer"
                    >
                      <FiCamera className="text-2xl" />
                    </button>
                  </div>

                  <div className="flex-1 space-y-6 w-full">
                    <div>
                      <label className="block text-sm font-semibold mb-2 text-gray-700">Full Name</label>
                      <input 
                        type="text" 
                        value={formData.full_name} 
                        onChange={(e) => setFormData({...formData, full_name: e.target.value})}
                        className="w-full px-4 py-3 rounded-xl bg-white border border-gray-200 text-gray-900 focus:outline-none focus:border-blue-500 transition-colors shadow-inner" 
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-semibold mb-2 text-gray-700">Email Address</label>
                      <input type="email" value={profile.email} className="w-full px-4 py-3 rounded-xl bg-white border border-gray-200 text-gray-600 cursor-not-allowed shadow-inner" disabled />
                      <p className="text-xs text-gray-600 mt-2">Your email cannot be changed.</p>
                    </div>
                    <div className="pt-4 border-t border-gray-200">
                      <Button type="submit" variant="primary" icon={<FiSave />} disabled={saving}>
                        {saving ? 'Saving...' : 'Save Profile'}
                      </Button>
                    </div>
                  </div>
                </div>
              </Card>
            )}

            {activeTab === 'Appearance' && (
              <Card hover={false} className="p-8">
                <h2 className="text-xl font-bold flex items-center gap-2 mb-8 text-gray-900">
                  <FiSun className="text-blue-500" /> Appearance
                </h2>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-semibold mb-2 text-gray-700">Theme Preference</label>
                    <select 
                      value={formData.theme}
                      onChange={(e) => setFormData({...formData, theme: e.target.value})}
                      className="w-full px-4 py-3 rounded-xl bg-white border border-gray-200 text-gray-900 focus:outline-none focus:border-blue-500"
                    >
                      <option value="dark">Dark Mode (Premium)</option>
                      <option value="light">Light Mode</option>
                      <option value="system">System Default</option>
                    </select>
                  </div>
                  <div className="pt-4">
                    <Button type="submit" variant="primary" icon={<FiSave />} disabled={saving}>
                      {saving ? 'Saving...' : 'Save Theme'}
                    </Button>
                  </div>
                </div>
              </Card>
            )}

            {activeTab === 'Notifications' && (
              <Card hover={false} className="p-8">
                <h2 className="text-xl font-bold flex items-center gap-2 mb-8 text-gray-900">
                  <FiBell className="text-yellow-500" /> Notifications
                </h2>
                <div className="space-y-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-bold text-gray-900 mb-1">Push Notifications</h4>
                      <p className="text-sm text-gray-600">Receive alerts for upcoming exams and study goals.</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input 
                        type="checkbox" 
                        checked={formData.notifications_enabled} 
                        onChange={(e) => setFormData({...formData, notifications_enabled: e.target.checked})}
                        className="sr-only peer" 
                      />
                      <div className="w-11 h-6 bg-gray-100 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-500"></div>
                    </label>
                  </div>
                  <div className="pt-4 border-t border-gray-200">
                    <Button type="submit" variant="primary" icon={<FiSave />} disabled={saving}>
                      {saving ? 'Saving...' : 'Save Preferences'}
                    </Button>
                  </div>
                </div>
              </Card>
            )}

            {activeTab === 'Language' && (
              <Card hover={false} className="p-8">
                <h2 className="text-xl font-bold flex items-center gap-2 mb-8 text-gray-900">
                  <FiGlobe className="text-emerald-500" /> Language Settings
                </h2>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-semibold mb-2 text-gray-700">App Language</label>
                    <select 
                      value={formData.language}
                      onChange={(e) => setFormData({...formData, language: e.target.value})}
                      className="w-full px-4 py-3 rounded-xl bg-white border border-gray-200 text-gray-900 focus:outline-none focus:border-blue-500"
                    >
                      <option value="en">English (US)</option>
                      <option value="es">Spanish (ES)</option>
                      <option value="fr">French (FR)</option>
                      <option value="de">German (DE)</option>
                    </select>
                  </div>
                  <div className="pt-4">
                    <Button type="submit" variant="primary" icon={<FiSave />} disabled={saving}>
                      {saving ? 'Saving...' : 'Save Language'}
                    </Button>
                  </div>
                </div>
              </Card>
            )}

            {activeTab === 'Security' && (
              <Card hover={false} className="p-8 border-red-500/30">
                <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2 mb-8">
                  <FiShield className="text-red-500" /> Security & Data
                </h2>
                <p className="text-sm text-gray-600 mb-6">Manage your data, document embeddings, and account status. Proceed with caution.</p>
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 rounded-xl border border-gray-200 bg-gray-100">
                    <div>
                      <h4 className="font-bold text-gray-900 mb-1">Clear AI Knowledge Base</h4>
                      <p className="text-sm text-gray-600">Deletes all uploaded documents and generated vector embeddings.</p>
                    </div>
                    <Button type="button" variant="secondary" className="border-gray-300 hover:text-red-400">Clear Data</Button>
                  </div>

                  <div className="flex items-center justify-between p-4 rounded-xl border border-red-500/30 bg-red-500/5">
                    <div>
                      <h4 className="font-bold text-red-400 mb-1">Delete Account</h4>
                      <p className="text-sm text-gray-600">Permanently delete your account and all associated study data.</p>
                    </div>
                    <Button type="button" variant="danger" onClick={handleDeleteAccount}>Delete Account</Button>
                  </div>
                </div>
              </Card>
            )}
          </form>

          {activeTab === 'Security' && (
            <form onSubmit={handlePasswordChange}>
              <Card hover={false} className="p-8 mt-8 border-gray-200">
                <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2 mb-8">
                  <FiShield className="text-blue-500" /> Change Password
                </h2>
                <div className="space-y-4 max-w-md">
                  <div>
                    <label className="block text-sm font-semibold mb-2 text-gray-700">Current Password</label>
                    <input type="password" value={passwordData.current} onChange={(e) => setPasswordData({...passwordData, current: e.target.value})} className="w-full px-4 py-3 rounded-xl bg-white border border-gray-200 text-gray-900 focus:outline-none focus:border-blue-500" required />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold mb-2 text-gray-700">New Password</label>
                    <input type="password" value={passwordData.new} onChange={(e) => setPasswordData({...passwordData, new: e.target.value})} className="w-full px-4 py-3 rounded-xl bg-white border border-gray-200 text-gray-900 focus:outline-none focus:border-blue-500" required />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold mb-2 text-gray-700">Confirm New Password</label>
                    <input type="password" value={passwordData.confirm} onChange={(e) => setPasswordData({...passwordData, confirm: e.target.value})} className="w-full px-4 py-3 rounded-xl bg-white border border-gray-200 text-gray-900 focus:outline-none focus:border-blue-500" required />
                  </div>
                  <div className="pt-4">
                    <Button type="submit" variant="primary" disabled={saving}>
                      {saving ? 'Updating...' : 'Update Password'}
                    </Button>
                  </div>
                </div>
              </Card>
            </form>
          )}

        </div>
      </div>
    </div>
  );
};

export default Settings;
