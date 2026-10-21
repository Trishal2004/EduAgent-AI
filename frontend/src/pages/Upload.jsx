import { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { FiUploadCloud, FiFileText, FiCheckCircle, FiLoader, FiDatabase, FiCpu, FiAlertCircle } from 'react-icons/fi';
import Card from '../components/ui/Card';
import ProgressBar from '../components/ui/ProgressBar';
import Button from '../components/ui/Button';
import { documentService } from '../services/documentService';

const Upload = () => {
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState(null);
  const [uploadState, setUploadState] = useState('idle'); // idle, processing, complete, error
  const [processStep, setProcessStep] = useState(0);
  const [errorMsg, setErrorMsg] = useState('');

  const steps = [
    { label: 'Uploading file to secure server...', icon: <FiUploadCloud /> },
    { label: 'Reading PDF & Extracting text...', icon: <FiFileText /> },
    { label: 'Creating AI Embeddings (Agentic RAG)...', icon: <FiCpu /> },
    { label: 'Saving to Vector Database...', icon: <FiDatabase /> }
  ];

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragging(true);
    } else if (e.type === 'dragleave') {
      setIsDragging(false);
    }
  }, []);

  const processFile = async (selectedFile) => {
    setUploadState('processing');
    setProcessStep(0);
    setErrorMsg('');
    
    try {
      // Step 1: Upload
      setProcessStep(0);
      const docRes = await documentService.uploadDocument(selectedFile);
      
      // Step 2 & 3 & 4: Process and Extract
      setProcessStep(1);
      // We simulate a bit of delay just for UI so user sees steps
      await new Promise(resolve => setTimeout(resolve, 800));
      setProcessStep(2);
      
      await documentService.processDocument(docRes.id);
      
      setProcessStep(3);
      await new Promise(resolve => setTimeout(resolve, 800));
      
      setUploadState('complete');
    } catch (error) {
      console.error("Upload failed", error);
      setErrorMsg(error.response?.data?.detail || "An error occurred during upload/processing.");
      setUploadState('error');
    }
  };

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const selectedFile = e.dataTransfer.files[0];
      setFile(selectedFile);
      processFile(selectedFile);
    }
  }, []);

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      processFile(selectedFile);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold tracking-tight mb-2">Knowledge Base Upload</h1>
        <p className="text-[var(--color-text-muted)] text-lg">Upload your course materials to train your personal AI agent.</p>
      </div>

      <Card hover={false} className="p-1">
        <div 
          className={`
            border-2 border-dashed rounded-xl p-12 text-center transition-all duration-300 relative overflow-hidden
            ${isDragging 
              ? 'border-blue-500 bg-blue-500/10 scale-[0.99] shadow-[0_0_30px_rgba(37,99,235,0.2)]' 
              : 'border-gray-200 hover:border-gray-300 bg-gray-50/30'
            }
          `}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          {uploadState === 'idle' && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex flex-col items-center">
              <div className="w-24 h-24 mb-6 rounded-full bg-gray-50 border border-gray-200 flex items-center justify-center text-4xl text-blue-400 shadow-[0_0_15px_rgba(37,99,235,0.2)]">
                <FiUploadCloud />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">Drag & Drop your files here</h3>
              <p className="text-gray-600 mb-8">Supported formats: PDF, DOCX, PPTX, TXT (Max 100MB)</p>
              
              <input 
                type="file" 
                id="file-upload" 
                className="hidden" 
                onChange={handleFileSelect}
                accept=".pdf,.docx,.pptx,.txt"
              />
              <label htmlFor="file-upload" className="cursor-pointer">
                <Button variant="secondary" onClick={() => document.getElementById('file-upload').click()}>
                  Browse Files
                </Button>
              </label>
            </motion.div>
          )}

          {uploadState === 'processing' && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex flex-col items-center py-8">
              <div className="relative w-24 h-24 mb-8">
                <svg className="animate-spin w-full h-full text-blue-500" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <div className="absolute inset-0 flex items-center justify-center text-2xl text-gray-900">
                  {steps[processStep]?.icon}
                </div>
              </div>
              
              <h3 className="text-xl font-bold text-gray-900 mb-2">{file?.name}</h3>
              <p className="text-blue-400 font-medium mb-8 flex items-center gap-2">
                <FiLoader className="animate-spin" /> {steps[processStep]?.label}
              </p>

              <div className="w-full max-w-md">
                <ProgressBar progress={((processStep + 1) / steps.length) * 100} height="h-3" color="bg-blue-500" />
              </div>
            </motion.div>
          )}

          {uploadState === 'complete' && (
            <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} className="flex flex-col items-center py-8">
              <div className="w-24 h-24 mb-6 rounded-full bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center text-5xl text-emerald-400 shadow-[0_0_30px_rgba(16,185,129,0.3)]">
                <FiCheckCircle />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">Upload Successful!</h3>
              <p className="text-gray-600 mb-8 max-w-md">"{file?.name}" has been successfully processed and indexed into your AI knowledge base.</p>
              
              <div className="flex gap-4">
                <Button variant="secondary" onClick={() => { setFile(null); setUploadState('idle'); }}>
                  Upload Another
                </Button>
                <Button variant="primary" onClick={() => window.location.href='/chat'}>
                  Ask AI About This
                </Button>
              </div>
            </motion.div>
          )}

          {uploadState === 'error' && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex flex-col items-center py-8">
              <div className="w-24 h-24 mb-6 rounded-full bg-red-500/20 border border-red-500/30 flex items-center justify-center text-5xl text-red-400 shadow-[0_0_30px_rgba(239,68,68,0.3)]">
                <FiAlertCircle />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">Upload Failed</h3>
              <p className="text-red-400 mb-8 max-w-md">{errorMsg}</p>
              
              <div className="flex gap-4">
                <Button variant="secondary" onClick={() => { setFile(null); setUploadState('idle'); }}>
                  Try Again
                </Button>
              </div>
            </motion.div>
          )}
        </div>
      </Card>
    </div>
  );
};

export default Upload;
