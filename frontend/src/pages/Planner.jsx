import { useState } from 'react';
import { FiCalendar, FiClock, FiTarget, FiEdit2, FiDownload, FiCheckCircle } from 'react-icons/fi';
import { motion } from 'framer-motion';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import ProgressBar from '../components/ui/ProgressBar';
import { plannerService } from '../services/plannerService';

const Planner = () => {
  const [examDate, setExamDate] = useState('');
  const [subjects, setSubjects] = useState('');
  const [studyTime, setStudyTime] = useState('4');
  const [isGenerating, setIsGenerating] = useState(false);
  const [planGenerated, setPlanGenerated] = useState(false);
  const [weeklyPlan, setWeeklyPlan] = useState([]);
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    // Try to load existing plan
    plannerService.getPlan()
      .then(res => {
        setExamDate(new Date(res.target_exam_date).toISOString().split('T')[0]);
        setSubjects(res.subjects);
        setStudyTime(res.daily_hours.toString());
        setWeeklyPlan(res.plan_data);
        setPlanGenerated(true);
      })
      .catch(err => {
        // No active plan, ignore
      });
  }, []);

  const handleGenerate = async (e) => {
    e.preventDefault();
    setIsGenerating(true);
    setErrorMsg('');
    try {
      const res = await plannerService.generatePlan({
        exam_date: examDate,
        subjects: subjects,
        study_time: parseInt(studyTime)
      });
      setWeeklyPlan(res.plan_data);
      setPlanGenerated(true);
    } catch (err) {
      console.error(err);
      setErrorMsg(err.response?.data?.detail || "Failed to generate plan.");
    } finally {
      setIsGenerating(false);
    }
  };


  return (
    <div className="max-w-6xl mx-auto space-y-8">
      
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight mb-2">AI Study Planner</h1>
        <p className="text-[var(--color-text-muted)] text-lg">Generate a personalized, optimized revision schedule based on your exam dates and weak topics.</p>
      </div>

      {!planGenerated ? (
        <Card className="max-w-2xl mx-auto p-8 border-blue-500/20 bg-blue-900/10">
          <form onSubmit={handleGenerate} className="space-y-6">
            <h2 className="text-xl font-bold text-gray-900 mb-6">Create New Schedule</h2>
            
            {errorMsg && (
              <div className="p-3 bg-red-500/10 border border-red-500/20 text-red-400 rounded-lg text-sm mb-4">
                {errorMsg}
              </div>
            )}

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Target Exam Date</label>
                <input 
                  type="date" 
                  required
                  value={examDate}
                  onChange={(e) => setExamDate(e.target.value)}
                  className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-gray-900 focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Subjects / Topics to Cover</label>
                <input 
                  type="text" 
                  placeholder="e.g. Operating Systems, Databases"
                  value={subjects}
                  onChange={(e) => setSubjects(e.target.value)}
                  className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-gray-900 focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Daily Available Study Time (Hours)</label>
                <input 
                  type="range" 
                  min="1" max="12" 
                  value={studyTime}
                  onChange={(e) => setStudyTime(e.target.value)}
                  className="w-full accent-blue-500"
                />
                <p className="text-right text-blue-400 font-bold mt-1">{studyTime} Hours/Day</p>
              </div>
            </div>

            <Button 
              type="submit" 
              variant="primary" 
              className="w-full py-4 text-lg mt-8"
              disabled={isGenerating}
            >
              {isGenerating ? 'Analyzing Topics & Generating Plan...' : 'Generate Intelligent Study Plan'}
            </Button>
          </form>
        </Card>
      ) : (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-8">
          
          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card hover={false} className="flex items-center gap-4 bg-gradient-to-br from-blue-900/40 to-slate-900">
              <div className="p-3 bg-blue-500/20 rounded-xl text-blue-400"><FiTarget className="text-2xl" /></div>
              <div>
                <p className="text-sm text-gray-600">Next Topic</p>
                <p className="text-lg font-bold text-gray-900">{weeklyPlan.length > 0 ? weeklyPlan[0].topics[0] : 'Study Goal'}</p>
              </div>
            </Card>
            <Card hover={false} className="flex items-center gap-4">
              <div className="p-3 bg-emerald-500/20 rounded-xl text-emerald-400"><FiCheckCircle className="text-2xl" /></div>
              <div className="w-full">
                <p className="text-sm text-gray-600 mb-1">Plan Completion</p>
                <ProgressBar progress={35} height="h-2" color="bg-emerald-500" />
              </div>
            </Card>
            <Card hover={false} className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-orange-500/20 rounded-xl text-orange-400"><FiClock className="text-2xl" /></div>
                <div>
                  <p className="text-sm text-gray-600">Daily Allocation</p>
                  <p className="text-xl font-bold text-gray-900">{studyTime} Hours</p>
                </div>
              </div>
            </Card>
          </div>

          {/* Action Bar */}
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold">Your Generated Study Plan</h2>
            <div className="flex gap-3">
              <Button variant="ghost" className="border border-gray-200 text-gray-700" onClick={() => setPlanGenerated(false)}><FiEdit2 className="mr-2" /> New Plan</Button>
              <Button variant="secondary" onClick={() => window.print()}><FiDownload className="mr-2" /> Export PDF</Button>
            </div>
          </div>

          {/* Calendar / Timeline View */}
          <div className="space-y-4 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gray-100">
            {weeklyPlan.map((dayPlan, idx) => (
              <div key={idx} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group">
                <div className="flex items-center justify-center w-10 h-10 rounded-full border-4 border-[var(--color-bg-base)] bg-gray-50 group-hover:bg-blue-500 shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 transition-colors z-10 text-white font-bold text-sm">
                  {idx + 1}
                </div>
                
                <Card className="w-[calc(100%-3rem)] md:w-[calc(50%-2.5rem)] hover:-translate-y-1 transition-transform border-l-4 border-l-blue-500">
                  <div className="flex justify-between items-start mb-3">
                    <h3 className="font-bold text-lg text-gray-900">{dayPlan.day}</h3>
                    <Badge variant={dayPlan.type === 'Assessment' ? 'danger' : 'neutral'}>{dayPlan.type}</Badge>
                  </div>
                  <ul className="space-y-2 mb-4">
                    {dayPlan.topics.map((topic, i) => (
                      <li key={i} className="text-sm text-gray-700 flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-blue-400" /> {topic}
                      </li>
                    ))}
                  </ul>
                  <div className="text-xs font-bold text-gray-600 flex items-center gap-1">
                    <FiClock /> {dayPlan.time} allocated
                  </div>
                </Card>
              </div>
            ))}
          </div>

        </motion.div>
      )}
    </div>
  );
};

export default Planner;
