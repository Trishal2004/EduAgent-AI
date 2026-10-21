import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { FiBookOpen, FiMessageSquare, FiFileText, FiCheckCircle } from 'react-icons/fi';

const features = [
  {
    icon: <FiBookOpen className="text-3xl text-primary mb-4" />,
    title: 'Generate Notes',
    description: 'Instantly convert your lecture PDFs and PPTs into concise, organized study notes.',
  },
  {
    icon: <FiMessageSquare className="text-3xl text-accent mb-4" />,
    title: 'Ask AI Questions',
    description: 'Chat directly with your course materials and get instant, accurate answers with source citations.',
  },
  {
    icon: <FiFileText className="text-3xl text-primary mb-4" />,
    title: 'Question Papers',
    description: 'Automatically generate university-style question papers and quizzes tailored to your syllabus.',
  },
];

const Home = () => {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Basic Home Navbar */}
      <nav className="flex justify-between items-center p-6 lg:px-12 glass-card rounded-none border-t-0 border-x-0 sticky top-0 z-50">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-blue-400 flex items-center justify-center text-gray-900 font-bold text-xl">E</div>
          <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-blue-500">EduAgent AI</span>
        </div>
        <div className="flex space-x-4">
          <Link to="/login" className="px-5 py-2 rounded-full font-medium text-slate-600 dark:text-gray-700 hover:bg-slate-100 dark:hover:bg-gray-50 transition">Login</Link>
          <Link to="/dashboard" className="px-5 py-2 rounded-full font-medium bg-primary text-gray-900 hover:bg-blue-700 shadow-sm shadow-blue-500/30 transition">Get Started</Link>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="flex-grow flex flex-col items-center justify-center p-6 text-center mt-12 mb-24">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="max-w-4xl"
        >
          <h1 className="text-5xl lg:text-7xl font-extrabold tracking-tight mb-6 leading-tight">
            AI-Powered <br className="hidden md:block" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-accent">University Course Assistant</span>
          </h1>
          <p className="text-lg lg:text-xl text-slate-600 dark:text-gray-600 mb-10 max-w-2xl mx-auto">
            Upload lecture notes, ask AI questions, and effortlessly generate study notes, MCQs, and university question papers.
          </p>
          <div className="flex flex-col sm:flex-row justify-center space-y-4 sm:space-y-0 sm:space-x-6">
            <Link to="/dashboard" className="px-8 py-4 rounded-full text-lg font-semibold bg-primary text-gray-900 hover:bg-blue-700 shadow-md shadow-blue-500/30 transition transform hover:-translate-y-1">
              Start Learning Now
            </Link>
          </div>
        </motion.div>

        {/* Features Section */}
        <motion.div 
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-24 max-w-6xl w-full px-4"
        >
          {features.map((feature, index) => (
            <div key={index} className="glass-card p-8 flex flex-col items-start text-left hover:shadow-md transition duration-300 group">
              <div className="p-3 bg-blue-50 dark:bg-gray-100 rounded-2xl mb-6 group-hover:scale-110 transition-transform">
                {feature.icon}
              </div>
              <h3 className="text-2xl font-bold mb-3">{feature.title}</h3>
              <p className="text-slate-600 dark:text-gray-600 leading-relaxed">{feature.description}</p>
            </div>
          ))}
        </motion.div>
      </main>

      {/* Footer */}
      <footer className="py-8 text-center text-gray-600 dark:text-gray-600 border-t border-slate-200 dark:border-gray-200">
        <p>&copy; {new Date().getFullYear()} EduAgent AI. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default Home;
