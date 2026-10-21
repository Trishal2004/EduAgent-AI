import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { Toaster } from 'react-hot-toast';
import ProtectedRoute from './components/ProtectedRoute';
import MainLayout from './components/layout/MainLayout';
import Login from './pages/Login';
import Register from './pages/Register';
import VerifyEmail from './pages/VerifyEmail';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';
import Dashboard from './pages/Dashboard';
import Chat from './pages/Chat';
import Upload from './pages/Upload';
import Documents from './pages/Documents';
import Flashcards from './pages/Flashcards';
import Notes from './pages/Notes';
import NoteDetail from './pages/NoteDetail';
import Quiz from './pages/Quiz';
import QuestionPaper from './pages/QuestionPaper';
import Graph from './pages/Graph';
import Analytics from './pages/Analytics';
import Mentor from './pages/Mentor';
import Workspace from './pages/Workspace';
import Settings from './pages/Settings';

function App() {
  return (
    <AuthProvider>
      <Toaster position="top-right" />
      <Router>
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/verify-email" element={<VerifyEmail />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/reset-password" element={<ResetPassword />} />
          {/* Protected Routes inside MainLayout */}
          <Route path="/dashboard" element={<ProtectedRoute><MainLayout><Dashboard /></MainLayout></ProtectedRoute>} />
          <Route path="/tutor" element={<ProtectedRoute><MainLayout><Chat /></MainLayout></ProtectedRoute>} />
          <Route path="/documents" element={<ProtectedRoute><MainLayout><Documents /></MainLayout></ProtectedRoute>} />
          <Route path="/upload" element={<ProtectedRoute><MainLayout><Upload /></MainLayout></ProtectedRoute>} />
          
          {/* Added missing module routes */}
          <Route path="/flashcards" element={<ProtectedRoute><MainLayout><Flashcards /></MainLayout></ProtectedRoute>} />
          <Route path="/notes" element={<ProtectedRoute><MainLayout><Notes /></MainLayout></ProtectedRoute>} />
          <Route path="/notes/:noteId" element={<ProtectedRoute><MainLayout><NoteDetail /></MainLayout></ProtectedRoute>} />
          <Route path="/quiz" element={<ProtectedRoute><MainLayout><Quiz /></MainLayout></ProtectedRoute>} />
          <Route path="/papers" element={<ProtectedRoute><MainLayout><QuestionPaper /></MainLayout></ProtectedRoute>} />
          <Route path="/knowledge-graph" element={<ProtectedRoute><MainLayout><Graph /></MainLayout></ProtectedRoute>} />
          <Route path="/analytics" element={<ProtectedRoute><MainLayout><Analytics /></MainLayout></ProtectedRoute>} />
          <Route path="/mentor" element={<ProtectedRoute><MainLayout><Mentor /></MainLayout></ProtectedRoute>} />
          <Route path="/workspace" element={<ProtectedRoute><MainLayout><Workspace /></MainLayout></ProtectedRoute>} />
          <Route path="/settings" element={<ProtectedRoute><MainLayout><Settings /></MainLayout></ProtectedRoute>} />
          <Route path="/profile" element={<Navigate to="/settings" replace />} />

          {/* Fallback Route - Redirects any unknown route to dashboard */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
