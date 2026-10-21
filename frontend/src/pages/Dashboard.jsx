import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  FiClock, FiTrendingUp, FiTarget, FiBookOpen, 
  FiPlayCircle, FiMessageSquare, FiFileText, FiAward,
  FiChevronRight, FiLoader, FiCalendar, FiCheckCircle
} from 'react-icons/fi';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import ProgressBar from '../components/ui/ProgressBar';
import { dashboardService } from '../services/dashboardService';
import {
  BarChart, Bar, LineChart, Line, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';
import { useNavigate } from 'react-router-dom';

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white border border-gray-200 p-3 rounded-lg shadow-md">
        <p className="text-gray-900 font-bold text-sm mb-1">{label}</p>
        {payload.map((entry, index) => (
          <p key={index} className="text-sm font-medium" style={{ color: entry.color }}>
            {entry.name}: {entry.value}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

const Dashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const result = await dashboardService.getDashboardMetrics();
        setData(result);
      } catch (err) {
        console.error("Failed to load dashboard data:", err);
        setError("Failed to load dashboard data.");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <FiLoader className="animate-spin text-4xl text-blue-500" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-red-500 bg-red-100 p-4 rounded-lg">
        {error}
      </div>
    );
  }

  const { username, greeting, stats, subjectProgress, continueLearning: rawContinueLearning, recommendations, recentActivity, badges, weeklyChartData, studyPlanQuizzes, weeklyGoal, quizPerformanceData } = data;

  const target = weeklyGoal?.target_hours || 10;
  const current = weeklyGoal?.current_hours || 0;
  const goalProgress = target > 0 ? Math.min(100, Math.round((current / target) * 100)) : 0;

  const continueLearning = rawContinueLearning.map(item => {
    let icon = <FiFileText />;
    let color = 'text-indigo-400';
    if (item.type === 'Chat') {
      icon = <FiMessageSquare />;
      color = 'text-blue-600';
    } else if (item.type === 'Quiz') {
      icon = <FiPlayCircle />;
      color = 'text-emerald-400';
    }
    return { ...item, icon, color };
  });

  return (
    <div className="-m-6 lg:-m-10 p-6 lg:p-10 bg-[#F7F8FA] text-gray-900 min-h-[calc(100vh-5rem)]" style={{ "--color-bg-card": "#FFFFFF", "--color-border-subtle": "#E5E7EB", "--color-text-main": "#1F2937", "--color-text-muted": "#6B7280" }}>
      <div className="space-y-8">
      {/* Welcome Banner */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative overflow-hidden rounded-3xl bg-blue-50 border border-blue-100 p-10 shadow-sm rounded-3xl"
      >
        
        
        <div className="relative z-10 flex flex-col md:flex-row justify-between items-start md:items-center gap-8">
          <div>
            <h1 className="text-4xl font-extrabold text-blue-900 mb-3 tracking-tight">{greeting}, {username} 👋</h1>
            <p className="text-blue-700 text-lg font-medium max-w-2xl">Continue your learning journey. "The expert in anything was once a beginner."</p>
          </div>
          <Button variant="primary" size="lg" className="shadow-sm whitespace-nowrap" icon={<FiPlayCircle className="text-xl" />}>Resume Study Session</Button>
        </div>
      </motion.div>

      {/* Today's Progress Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
        {[
          { label: 'Current Streak', value: `${stats.streak} Days`, icon: <FiTrendingUp className="text-orange-400" />, bg: "bg-orange-500/10", border: "border-orange-500/20" },
          { label: 'Total Study Time', value: stats.studyTime, icon: <FiClock className="text-blue-600" />, bg: "bg-blue-50", border: "border-blue-500/20" },
          { label: 'Next Exam In', value: stats.examCountdown, icon: <FiTarget className="text-red-400" />, bg: "bg-red-500/10", border: "border-red-500/20" },
          { label: 'Subjects Completed', value: stats.subjectsCompleted, icon: <FiAward className="text-emerald-400" />, bg: "bg-emerald-500/10", border: "border-emerald-500/20" }
        ].map((stat, idx) => (
          <motion.div
            key={idx}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.1 }}
          >
            <Card className="flex items-center gap-5 p-6 hover:shadow-sm transition-shadow" hover={true}>
              <div className={`p-4 rounded-2xl ${stat.bg} border ${stat.border} shadow-sm`}>
                <span className="text-3xl">{stat.icon}</span>
              </div>
              <div>
                <p className="text-sm font-semibold text-gray-600 mb-1 uppercase tracking-wider">{stat.label}</p>
                <h3 className="text-2xl font-bold text-gray-900 tracking-tight">{stat.value}</h3>
              </div>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Learning Analytics */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold tracking-tight text-gray-900 mb-6">Learning Analytics</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          
          {/* Weekly Activity */}
          <Card hover={false} className="p-6 border border-gray-200 bg-white flex flex-col h-80">
            <h3 className="font-bold text-gray-900 mb-4">Weekly Activity</h3>
            <div className="flex-1 w-full h-full min-h-0">
              {weeklyChartData && weeklyChartData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={weeklyChartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                    <XAxis dataKey="day" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                    <YAxis stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                    <Tooltip content={<CustomTooltip />} />
                    <Bar dataKey="hours" name="Hours" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-full flex flex-col items-center justify-center text-gray-600 text-sm text-center">
                  <FiClock className="text-3xl mb-2 opacity-50" />
                  No activity data this week.
                </div>
              )}
            </div>
          </Card>

          {/* Quiz Performance */}
          <Card hover={false} className="p-6 border border-gray-200 bg-white flex flex-col h-80">
            <h3 className="font-bold text-gray-900 mb-4">Quiz Performance</h3>
            <div className="flex-1 w-full h-full min-h-0">
              {quizPerformanceData && quizPerformanceData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={quizPerformanceData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                    <XAxis dataKey="date" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                    <YAxis stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} domain={[0, 100]} />
                    <Tooltip content={<CustomTooltip />} />
                    <Line type="monotone" dataKey="accuracy" name="Accuracy %" stroke="#10b981" strokeWidth={3} dot={{ fill: '#10b981', strokeWidth: 2, r: 4 }} activeDot={{ r: 6 }} />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-full flex flex-col items-center justify-center text-gray-600 text-sm text-center px-4">
                  <FiPlayCircle className="text-3xl mb-2 opacity-50" />
                  Take some quizzes to see your performance trend!
                </div>
              )}
            </div>
          </Card>

          {/* Subject Mastery */}
          <Card hover={false} className="p-6 border border-gray-200 bg-white flex flex-col h-80">
            <h3 className="font-bold text-gray-900 mb-4">Subject Mastery</h3>
            <div className="flex-1 w-full h-full min-h-0">
              {subjectProgress && subjectProgress.length > 2 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart cx="50%" cy="50%" outerRadius="70%" data={subjectProgress}>
                    <PolarGrid stroke="#e2e8f0" />
                    <PolarAngleAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                    <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                    <Radar name="Mastery" dataKey="progress" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.5} />
                    <Tooltip content={<CustomTooltip />} />
                  </RadarChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-full flex flex-col items-center justify-center text-gray-600 text-sm text-center px-4">
                  <FiTarget className="text-3xl mb-2 opacity-50" />
                  Study at least 3 subjects to unlock the mastery radar.
                </div>
              )}
            </div>
          </Card>

        </div>
      </section>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Column (2/3 width) */}
        <div className="lg:col-span-2 space-y-10">

          {/* Today's Study Plan */}
          <section>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold tracking-tight text-gray-900 flex items-center gap-2">
                <FiCalendar className="text-blue-600" /> Today's Study Plan
              </h2>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
              {studyPlanQuizzes && studyPlanQuizzes.length > 0 ? (
                studyPlanQuizzes.map((quiz, idx) => (
                  <Card key={idx} onClick={() => navigate('/quiz')} hover={true} className="flex flex-col justify-between border-t-4 border-t-blue-500 bg-white h-full cursor-pointer hover:-translate-y-1 transition-all p-5">
                    <div>
                      <div className="flex justify-between items-start mb-3">
                        <Badge variant="neutral" className="bg-blue-50 text-blue-600 text-xs font-semibold">{quiz.difficulty}</Badge>
                        {quiz.status === "Completed" ? (
                          <FiCheckCircle className="text-emerald-400 text-xl" />
                        ) : (
                          <FiPlayCircle className="text-gray-600 text-xl" />
                        )}
                      </div>
                      <h3 className="font-bold text-gray-900 text-md mb-1 leading-snug line-clamp-2">{quiz.topic}</h3>
                    </div>
                    <p className="text-sm text-gray-600 mt-4 font-medium">{quiz.total_questions} Questions</p>
                  </Card>
                ))
              ) : (
                 <div className="col-span-full flex flex-col items-center justify-center p-8 bg-gray-50 rounded-2xl border-2 border-gray-200 border-dashed text-center">
                    <FiCheckCircle className="text-4xl text-emerald-500 mb-3 opacity-80" />
                    <h3 className="text-lg font-bold text-gray-900 mb-1">All caught up for today!</h3>
                    <p className="text-gray-600 mb-4 text-sm max-w-xs">You have no pending daily quizzes. Generate a new study plan to add more tasks.</p>
                 </div>
              )}
            </div>
          </section>
          
          {/* Continue Learning */}
          <section>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold tracking-tight text-gray-900">Continue Learning</h2>
              <button onClick={() => navigate('/documents')} className="text-sm font-semibold text-blue-600 hover:text-blue-700 flex items-center gap-1 transition-colors bg-blue-50 px-3 py-1.5 rounded-lg hover:bg-blue-100">
                View All <FiChevronRight />
              </button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {continueLearning.length > 0 ? (
                continueLearning.map((item, idx) => (
                  <Card key={idx} onClick={() => navigate('/documents')} className="group flex flex-col justify-between h-full hover:shadow-md hover:-translate-y-1 transition-all duration-300 border border-gray-200 hover:border-blue-500/50 overflow-hidden relative cursor-pointer">
                    <div className="absolute top-0 right-0 w-24 h-24 bg-gradient-to-bl from-slate-700/30 to-transparent rounded-bl-full -mr-4 -mt-4 opacity-50 group-hover:from-blue-500/20 transition-colors" />
                    <div className="relative z-10">
                      <div className="flex items-center gap-3 mb-4">
                        <div className={`p-2 rounded-lg bg-white shadow-sm ${item.color.replace('text-', 'text-')} bg-opacity-50`}>
                          <span className={`text-xl ${item.color}`}>{item.icon}</span>
                        </div>
                        <Badge variant="neutral" className="bg-white text-xs font-semibold">{item.type}</Badge>
                      </div>
                      <h3 className="font-bold text-gray-900 text-lg group-hover:text-blue-600 transition-colors line-clamp-2 leading-snug">
                        {item.title}
                      </h3>
                    </div>
                    <p className="text-sm font-medium text-gray-600 mt-6 flex items-center gap-1">
                      <FiClock className="inline" /> {item.time}
                    </p>
                  </Card>
                ))
              ) : (
                <div className="col-span-full flex flex-col items-center justify-center p-12 bg-gray-50 rounded-2xl border-2 border-gray-200 border-dashed text-center">
                  <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center mb-4 shadow-inner">
                    <FiBookOpen className="text-3xl text-gray-600" />
                  </div>
                  <h3 className="text-lg font-bold text-gray-900 mb-2">No active study sessions</h3>
                  <p className="text-gray-600 mb-6 max-w-sm">You haven't opened any documents or quizzes yet. Upload your first document to get started.</p>
                  <Button variant="primary" size="md" icon={<FiFileText />}>Upload a Document</Button>
                </div>
              )}
            </div>
          </section>

          {/* Subject Progress */}
          <section>
            <h2 className="text-2xl font-bold tracking-tight text-gray-900 mb-6">Subject Progress</h2>
            <Card hover={false} className="p-8 border border-gray-200 bg-white">
              {subjectProgress.length > 0 ? (
                <div className="space-y-8">
                  {subjectProgress.map((sub, idx) => (
                    <div key={idx} className="relative">
                      <div className="flex justify-between items-center mb-2">
                        <span className="font-semibold text-gray-900">{sub.name}</span>
                        <span className="text-sm font-bold text-gray-600">{sub.progress}%</span>
                      </div>
                      <ProgressBar 
                        progress={sub.progress}
                        color={sub.color}
                        showLabel={false}
                        height="h-3"
                      />
                    </div>
                  ))}
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center py-8 text-center">
                  <FiTarget className="text-4xl text-gray-600 mb-3 opacity-50" />
                  <h3 className="text-lg font-bold text-gray-600 mb-1">No progress yet</h3>
                  <p className="text-gray-600">Take some quizzes to see your subject mastery here!</p>
                </div>
              )}
            </Card>
          </section>

          {/* Recent Activity Timeline */}
          <section>
            <h2 className="text-2xl font-bold tracking-tight text-gray-900 mb-6">Recent Activity</h2>
            <Card hover={false} className="p-8 border border-gray-200 bg-white">
              <div className="space-y-8 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-slate-700 before:to-transparent">
                {recentActivity.length > 0 ? (
                  recentActivity.map((activity, idx) => (
                    <div key={idx} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group">
                      {/* Timeline Dot */}
                      <div className="flex items-center justify-center w-10 h-10 rounded-full border-4 border-slate-900 bg-blue-500 text-slate-900 shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 z-10">
                         {activity.action.toLowerCase().includes('quiz') ? <FiPlayCircle size={16} className="text-gray-900"/> : 
                          activity.action.toLowerCase().includes('document') ? <FiFileText size={16} className="text-gray-900"/> : 
                          <FiMessageSquare size={16} className="text-gray-900"/>}
                      </div>
                      
                      <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] p-4 rounded-xl border border-gray-200 bg-white shadow-md transition-all hover:shadow-sm hover:border-gray-300">
                        <div className="flex items-center justify-between mb-1">
                          <span className="font-bold text-gray-900 text-sm">{activity.action}</span>
                          <span className="text-xs font-semibold text-blue-600 bg-blue-50 px-2 py-1 rounded-md">{activity.time}</span>
                        </div>
                        <p className="text-sm text-gray-600 font-medium mb-1">{activity.subject}</p>
                        <p className="text-sm text-gray-600">{activity.detail}</p>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="flex flex-col items-center justify-center py-12 text-center relative z-10 bg-white rounded-xl border border-gray-200">
                    <div className="w-12 h-12 rounded-full bg-white flex items-center justify-center mb-3">
                       <FiClock className="text-2xl text-gray-600" />
                    </div>
                    <p className="font-semibold text-gray-600 mb-1">No recent activity</p>
                    <p className="text-sm text-gray-600">Your study journey starts here. Start a quiz or open a document!</p>
                  </div>
                )}
              </div>
            </Card>
          </section>

        </div>

        {/* Right Column (1/3 width) */}
        <div className="space-y-10">
          
          {/* Weekly Study Goal */}
          <section>
            <h2 className="text-2xl font-bold tracking-tight text-gray-900 mb-6">Weekly Study Goal</h2>
            <Card hover={false} className="p-8 border border-gray-200 bg-white text-center relative overflow-hidden">
               
               <div className="relative z-10 flex flex-col items-center">
                 <div className="w-32 h-32 rounded-full border-8 border-gray-200 flex items-center justify-center mb-4 relative">
                   {/* Fake SVG Circle for progress */}
                   <svg className="absolute inset-0 w-full h-full -rotate-90" viewBox="0 0 100 100">
                     <circle cx="50" cy="50" r="46" fill="transparent" stroke="currentColor" strokeWidth="8" className="text-slate-700" />
                     <circle cx="50" cy="50" r="46" fill="transparent" stroke="currentColor" strokeWidth="8" strokeDasharray="289" strokeDashoffset={289 - (289 * goalProgress) / 100} className="text-blue-500 transition-all duration-1000 ease-out" strokeLinecap="round" />
                   </svg>
                   <div className="text-center">
                     <span className="text-3xl font-bold text-gray-900">{current}</span>
                     <span className="text-sm font-medium text-gray-600 block -mt-1">/ {target} hrs</span>
                   </div>
                 </div>
                 <h3 className="font-bold text-gray-900 text-lg">{goalProgress >= 100 ? "Goal Reached! 🎉" : "Keep it up!"}</h3>
                 <p className="text-sm text-gray-600 mt-1">You've completed {goalProgress}% of your weekly goal.</p>
               </div>
            </Card>
          </section>

          {/* AI Recommendations (Weak Subjects) */}
          <section>
            <h2 className="text-2xl font-bold tracking-tight text-gray-900 mb-6 flex items-center gap-2">
              <span className="p-2 bg-red-500/10 rounded-lg"><FiTarget className="text-red-400 text-xl" /></span> Focus Areas
            </h2>
            <div className="space-y-4">
              {recommendations.length > 0 ? (
                recommendations.map((rec, idx) => (
                  <Card key={idx} className="border-l-4 border-l-red-500 bg-gradient-to-r from-red-900/20 to-slate-800/50 hover:to-slate-800 hover:shadow-sm transition-all p-5">
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <h3 className="font-bold text-gray-900 mb-2 text-base">{rec.title}</h3>
                        <p className="text-sm text-gray-600 leading-relaxed mb-4">{rec.reason}</p>
                        <button className="text-sm font-bold text-red-400 hover:text-red-300 transition-colors flex items-center gap-1 group">
                          Review Topic <FiChevronRight className="group-hover:translate-x-1 transition-transform" />
                        </button>
                      </div>
                    </div>
                  </Card>
                ))
              ) : (
                <Card className="flex flex-col items-center justify-center p-8 text-center border border-gray-200 bg-white border-dashed">
                  <FiAward className="text-4xl text-emerald-400 mb-3 opacity-80" />
                  <h3 className="font-bold text-gray-900 mb-1">You're all caught up!</h3>
                  <p className="text-sm text-gray-600">No weak areas identified currently. Keep up the great work!</p>
                </Card>
              )}
            </div>
          </section>

          {/* Quick Actions List */}
          <section>
            <h2 className="text-2xl font-bold tracking-tight text-gray-900 mb-6">Quick Actions</h2>
            <Card hover={false} className="p-3 space-y-2 border border-gray-200 bg-white">
              {[
                { name: 'Upload Document', icon: <FiBookOpen className="text-emerald-400 text-xl" />, hoverBg: 'hover:bg-emerald-500/10', hoverText: 'group-hover:text-emerald-400', path: '/documents' },
                { name: 'Ask AI Assistant', icon: <FiMessageSquare className="text-blue-600 text-xl" />, hoverBg: 'hover:bg-blue-50', hoverText: 'group-hover:text-blue-600', path: '/tutor' },
                { name: 'Generate Notes', icon: <FiFileText className="text-indigo-400 text-xl" />, hoverBg: 'hover:bg-indigo-500/10', hoverText: 'group-hover:text-indigo-400', path: '/notes' },
                { name: 'Start a Quiz', icon: <FiPlayCircle className="text-orange-400 text-xl" />, hoverBg: 'hover:bg-orange-500/10', hoverText: 'group-hover:text-orange-400', path: '/quiz' },
                { name: 'Study Flashcards', icon: <FiAward className="text-purple-400 text-xl" />, hoverBg: 'hover:bg-purple-500/10', hoverText: 'group-hover:text-purple-400', path: '/flashcards' }
              ].map((action, idx) => (
                <button key={idx} onClick={() => navigate(action.path)} className={`w-full flex items-center justify-between px-4 py-4 rounded-xl transition-all duration-200 text-left group ${action.hoverBg}`}>
                  <div className="flex items-center gap-4">
                    <div className="p-3 bg-white shadow-sm rounded-xl transition-colors">
                      {action.icon}
                    </div>
                    <span className={`font-semibold text-gray-600 ${action.hoverText} transition-colors text-base`}>{action.name}</span>
                  </div>
                  <FiChevronRight className={`text-gray-600 ${action.hoverText} opacity-0 group-hover:opacity-100 group-hover:translate-x-1 transition-all`} />
                </button>
              ))}
            </Card>
          </section>
          
        </div>

      </div>
    </div>
    </div>
  );
};

export default Dashboard;
