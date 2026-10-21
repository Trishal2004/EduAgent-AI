import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  FiTrendingUp, FiClock, FiTarget, FiActivity, FiBook, 
  FiFileText, FiAward, FiCheckCircle, FiAlertCircle, FiLoader
} from 'react-icons/fi';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, Legend, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar
} from 'recharts';
import Card from '../components/ui/Card';
import Badge from '../components/ui/Badge';
import ProgressBar from '../components/ui/ProgressBar';
import { analyticsService } from '../services/analyticsService';
import React from 'react';

// Map icon strings from backend to actual React Icons
const iconMap = {
    'FiClock': <FiClock className="text-blue-400" />,
    'FiTarget': <FiTarget className="text-emerald-400" />,
    'FiActivity': <FiActivity className="text-purple-400" />,
    'FiFileText': <FiFileText className="text-orange-400" />,
    'FiBook': <FiBook className="text-yellow-400" />,
    'FiAward': <FiAward className="text-rose-400" />,
    'FiAlertCircle': <FiAlertCircle className="text-orange-400" />
};

const AnalyticsDashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
      const loadAnalytics = async () => {
          try {
              const res = await analyticsService.getDashboardMetrics();
              setData(res);
          } catch (err) {
              console.error("Failed to load analytics", err);
          } finally {
              setLoading(false);
          }
      };
      loadAnalytics();
  }, []);

  // Simple Github-style heatmap generator
  const renderHeatmap = () => {
    const days = 35; // 5 weeks
    const blocks = Array.from({ length: days }).map((_, i) => {
      const intensity = Math.random();
      let color = 'bg-gray-50';
      if (intensity > 0.8) color = 'bg-emerald-400';
      else if (intensity > 0.5) color = 'bg-emerald-600';
      else if (intensity > 0.2) color = 'bg-emerald-800/60';
      return <div key={i} className={`w-3 h-3 rounded-sm ${color} transition-colors hover:ring-1 hover:ring-white`} title={`Activity level: ${Math.round(intensity*100)}%`} />;
    });

    return (
      <div className="flex gap-1 flex-wrap w-[240px]">
        {blocks}
      </div>
    );
  };

  if (loading) {
      return (
          <div className="flex justify-center items-center h-[50vh]">
              <FiLoader className="animate-spin text-4xl text-blue-500" />
          </div>
      );
  }

  if (!data) return null;

  const { scores, weeklyProgress, subjectRadar, quickStats, recommendations, streak, badges } = data;

  return (
    <div className="max-w-7xl mx-auto space-y-8 pb-12">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight mb-2">Learning Analytics</h1>
        <p className="text-[var(--color-text-muted)] text-lg">Track your progress, identify weak topics, and analyze quiz trends.</p>
      </div>

      {/* Top Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {quickStats.map((stat, i) => (
          <Card key={i} hover={false} className="p-4 flex flex-col items-center text-center justify-center bg-gradient-to-br from-slate-800 to-slate-900">
            <div className="text-2xl mb-2 bg-gray-50 p-2 rounded-xl shadow-inner border border-gray-200">
                {iconMap[stat.icon_name] || <FiActivity />}
            </div>
            <h3 className="text-2xl font-bold text-gray-900 tracking-tight">{stat.value}</h3>
            <p className="text-xs text-gray-600 font-medium mt-1">{stat.label}</p>
          </Card>
        ))}
      </div>

      {/* Main Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Col: Weekly Progress */}
        <div className="lg:col-span-2 space-y-8">
          <Card hover={false}>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-lg font-bold">Weekly Study Progress</h2>
              <Badge variant="neutral">Recent Activity</Badge>
            </div>
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={weeklyProgress} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorHours" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="name" stroke="#64748b" tick={{fill: '#94a3b8'}} axisLine={false} tickLine={false} />
                  <YAxis stroke="#64748b" tick={{fill: '#94a3b8'}} axisLine={false} tickLine={false} />
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#334155" />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '0.5rem' }}
                    itemStyle={{ color: '#f8fafc' }}
                  />
                  <Area type="monotone" dataKey="hours" stroke="#3b82f6" strokeWidth={3} fillOpacity={1} fill="url(#colorHours)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </Card>

          {/* Strong vs Weak Subjects Radar */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <Card hover={false} className="flex flex-col items-center">
              <h2 className="text-lg font-bold w-full text-left mb-2">Subject Mastery Mapping</h2>
              <div className="h-[250px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart cx="50%" cy="50%" outerRadius="70%" data={subjectRadar}>
                    <PolarGrid stroke="#334155" />
                    <PolarAngleAxis dataKey="subject" tick={{fill: '#94a3b8', fontSize: 12}} />
                    <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                    <Radar name="Strength" dataKey="strong" stroke="#10b981" fill="#10b981" fillOpacity={0.4} />
                    <Radar name="Weakness" dataKey="weak" stroke="#ef4444" fill="#ef4444" fillOpacity={0.2} />
                    <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155' }} />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </Card>

            <Card hover={false}>
              <h2 className="text-lg font-bold mb-6">Quiz Accuracy Trend</h2>
              <div className="h-[200px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={weeklyProgress}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#334155" />
                    <XAxis dataKey="name" stroke="#64748b" tick={{fontSize: 12}} axisLine={false} tickLine={false} />
                    <Tooltip cursor={{fill: '#334155', opacity: 0.4}} contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155' }} />
                    <Bar dataKey="accuracy" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </Card>
          </div>
        </div>

        {/* Right Col: Scores & Heatmap */}
        <div className="space-y-8">
          
          {/* Core Scores */}
          <Card hover={false}>
            <h2 className="text-lg font-bold mb-6">Overall AI Assessment</h2>
            <div className="space-y-6">
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm font-medium text-gray-700">Knowledge Score</span>
                  <span className="text-sm font-bold text-blue-400">{scores.knowledge}/100</span>
                </div>
                <ProgressBar progress={scores.knowledge} height="h-2" color="bg-blue-500" />
              </div>
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm font-medium text-gray-700">Learning Score</span>
                  <span className="text-sm font-bold text-emerald-400">{scores.learning}/100</span>
                </div>
                <ProgressBar progress={scores.learning} height="h-2" color="bg-emerald-500" />
              </div>
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm font-medium text-gray-700">Revision Score</span>
                  <span className="text-sm font-bold text-orange-400">{scores.revision}/100</span>
                </div>
                <ProgressBar progress={scores.revision} height="h-2" color="bg-orange-500" />
              </div>
            </div>
          </Card>

          {/* Daily Heatmap */}
          <Card hover={false} className="bg-white border-gray-200/50">
            <h2 className="text-sm font-bold mb-4 text-gray-600 uppercase tracking-wider">Daily Activity Heatmap</h2>
            <div className="flex justify-center">
              {renderHeatmap()}
            </div>
            <div className="flex justify-between text-[10px] text-gray-600 mt-4 px-2">
              <span>Less Activity</span>
              <div className="flex gap-1">
                <div className="w-3 h-3 bg-gray-50 rounded-sm" />
                <div className="w-3 h-3 bg-emerald-800/60 rounded-sm" />
                <div className="w-3 h-3 bg-emerald-600 rounded-sm" />
                <div className="w-3 h-3 bg-emerald-400 rounded-sm" />
              </div>
              <span>High Activity</span>
            </div>
          </Card>

          {/* Gamification: Badges & Streaks */}
          <Card hover={false} className="border-t-4 border-t-yellow-500">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-lg font-bold">Achievements</h2>
              <Badge variant="warning">{streak} Day Streak 🔥</Badge>
            </div>
            <div className="grid grid-cols-2 gap-3">
              {badges && badges.map((badge, i) => (
                <div key={i} className="flex flex-col items-center justify-center p-3 bg-gray-50 rounded-xl border border-gray-200 hover:border-yellow-500/50 transition-colors text-center group">
                  <div className="w-10 h-10 rounded-full bg-yellow-500/10 flex items-center justify-center mb-2 group-hover:scale-110 transition-transform">
                    <FiAward className="text-xl text-yellow-500" />
                  </div>
                  <span className="text-xs font-bold text-gray-700">{badge}</span>
                </div>
              ))}
              {!badges?.length && (
                <p className="text-xs text-gray-600 col-span-2 text-center py-2">Keep studying to earn badges!</p>
              )}
            </div>
          </Card>

          {/* AI Recommendations */}
          <Card hover={false} className="border-t-4 border-t-purple-500">
            <h2 className="text-lg font-bold mb-4">AI Recommendations</h2>
            <div className="space-y-3">
              {recommendations.map((rec, i) => (
                <div key={i} className="p-3 bg-gray-50 rounded-xl border border-gray-200 flex gap-3 items-start group hover:border-gray-300 transition-colors cursor-pointer">
                  <div className="mt-0.5 p-1.5 bg-white rounded shadow-inner">
                    {iconMap[rec.icon_name] || <FiBook className="text-blue-400" />}
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-gray-600 uppercase tracking-wider mb-1">{rec.type}</h4>
                    <p className="font-bold text-gray-900 text-sm group-hover:text-blue-400 transition-colors">{rec.title}</p>
                    <p className="text-xs text-gray-600 mt-1">{rec.desc}</p>
                  </div>
                </div>
              ))}
              {recommendations.length === 0 && <p className="text-sm text-gray-600">No new recommendations today.</p>}
            </div>
          </Card>

        </div>
      </div>
    </div>
  );
};

export default AnalyticsDashboard;
