import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FiDownload, FiSettings, FiFileText, FiPrinter, FiAlertCircle } from 'react-icons/fi';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import { documentService } from '../services/documentService';
import { questionPaperService } from '../services/questionPaperService';

const QuestionPaper = () => {
  const [documents, setDocuments] = useState([]);
  const [selectedDocument, setSelectedDocument] = useState('');
  const [difficulty, setDifficulty] = useState('university');
  const [isGenerating, setIsGenerating] = useState(false);
  const [paper, setPaper] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');

  // Fetch documents for the setup dropdown
  useEffect(() => {
    const fetchDocs = async () => {
      try {
        const docs = await documentService.getDocuments();
        setDocuments(docs.filter(d => d.embedding_status === 'completed' || d.upload_status === 'completed'));
      } catch (err) {
        console.error("Failed to load documents", err);
      }
    };
    fetchDocs();
  }, []);

  const handleGenerate = async (e) => {
    e.preventDefault();
    if (!selectedDocument) return;

    setIsGenerating(true);
    setErrorMsg('');
    try {
      const result = await questionPaperService.generatePaper(selectedDocument, difficulty);
      // Ensure we set the full paper object to parse content_json correctly
      setPaper(result);
    } catch (err) {
      console.error(err);
      setErrorMsg(err.response?.data?.detail || "Failed to generate paper. Please try again.");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownload = async () => {
    if (!paper) return;
    try {
      await questionPaperService.downloadPaper(paper.id);
    } catch (err) {
      console.error(err);
      alert("Failed to download PDF.");
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight mb-2">Question Paper Generator</h1>
        <p className="text-[var(--color-text-muted)]">Generate realistic, properly formatted university-style exam papers.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Input Form */}
        <div className="lg:col-span-1 space-y-6">
          <Card hover={false} className="sticky top-28 p-6 space-y-6">
            <form onSubmit={handleGenerate} className="space-y-6">
              {errorMsg && (
                <div className="p-3 bg-red-500/10 border border-red-500/20 text-red-400 rounded-lg text-sm flex items-center gap-2">
                  <FiAlertCircle /> {errorMsg}
                </div>
              )}
              <div>
                <label className="block text-sm font-semibold mb-2 text-gray-700">Select Study Material</label>
                <select
                  value={selectedDocument}
                  onChange={(e) => setSelectedDocument(e.target.value)}
                  className="w-full px-4 py-3 rounded-xl bg-gray-50 border border-gray-200 focus:border-blue-500 focus:outline-none transition-colors"
                  required
                >
                  <option value="" disabled>Select a document...</option>
                  {documents.map(doc => (
                    <option key={doc.id} value={doc.id}>{doc.filename}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-semibold mb-3 text-gray-700">Target Standard</label>
                <div className="space-y-3">
                  {[
                    { id: 'university', label: 'University Final (End Sem)', desc: '100 Marks: MCQs, 2M, 5M, 10M, Case Study' },
                    { id: 'midterm', label: 'Mid-Term Exam', desc: '50 Marks: 2M, 5M, 10M' },
                    { id: 'internal', label: 'Internal Assessment', desc: '25 Marks: Short Answers & 1 Long Answer' }
                  ].map(type => (
                    <label 
                      key={type.id} 
                      className={`flex items-start p-3 rounded-xl border cursor-pointer transition-all ${
                        difficulty === type.id 
                          ? 'border-blue-500 bg-blue-500/10 shadow-[0_0_15px_rgba(37,99,235,0.15)]' 
                          : 'border-gray-200 bg-gray-100 hover:bg-gray-100'
                      }`}
                    >
                      <input 
                        type="radio" 
                        name="difficulty" 
                        value={type.id}
                        checked={difficulty === type.id}
                        onChange={() => setDifficulty(type.id)}
                        className="mt-1 mr-3" 
                      />
                      <div>
                        <div className={`font-semibold ${difficulty === type.id ? 'text-blue-400' : 'text-gray-800'}`}>
                          {type.label}
                        </div>
                        <div className="text-xs text-gray-600 mt-0.5">{type.desc}</div>
                      </div>
                    </label>
                  ))}
                </div>
              </div>

              <Button 
                type="submit"
                disabled={isGenerating || !selectedDocument}
                variant="primary"
                className="w-full"
                icon={<FiFileText />}
              >
                {isGenerating ? 'Drafting Paper...' : 'Generate Paper'}
              </Button>
            </form>
          </Card>
        </div>

        {/* Output Paper */}
        <div className="lg:col-span-2">
          {isGenerating ? (
            <Card hover={false} className="h-full min-h-[700px] flex flex-col items-center justify-center p-8 border-dashed border-2 bg-gray-50/30">
              <div className="relative w-20 h-20 mb-6">
                <FiSettings className="absolute inset-0 w-full h-full text-blue-500 animate-spin-slow" style={{ animationDuration: '3s' }} />
                <FiSettings className="absolute inset-0 w-10 h-10 m-auto text-indigo-400 animate-spin-slow" style={{ animationDirection: 'reverse', animationDuration: '2s' }} />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Drafting Examination Paper...</h3>
              <p className="text-gray-600">Structuring Sections A through E with appropriate difficulty.</p>
            </Card>
          ) : paper ? (
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-4"
            >
              <div className="flex justify-end gap-3">
                <Button variant="secondary" onClick={() => window.print()} icon={<FiPrinter />}>Print</Button>
                <Button variant="primary" onClick={handleDownload} icon={<FiDownload />}>Download PDF</Button>
              </div>

              {/* Realistic Paper Styling (White background to look like a real paper) */}
              <div className="bg-white text-black shadow-md rounded-sm overflow-hidden">
                {/* Header */}
                <div className="p-8 md:px-16 md:pt-16 pb-8 border-b-4 border-double border-black text-center font-serif">
                  <h1 className="text-3xl font-bold uppercase mb-4">{paper.content_json.title}</h1>
                  <div className="mt-4 text-xs italic text-center">
                    Note: Attempt all sections. Read questions carefully before answering.
                  </div>
                </div>

                {/* Body */}
                <div className="p-8 md:p-16 space-y-12 font-serif text-[15px] leading-relaxed">
                  {paper.content_json.sections.map((section, sIdx) => (
                    <div key={sIdx} className="space-y-6">
                      <h3 className="text-lg font-bold text-center underline underline-offset-4">{section.section_name}</h3>
                      <div className="text-center italic text-sm">{section.instructions}</div>
                      <div className="space-y-6 pl-4">
                        {section.questions.map((q, qIdx) => (
                          <div key={qIdx} className="flex justify-between">
                            <div className="whitespace-pre-line text-justify pr-4">
                              {qIdx + 1}. {q.question}
                            </div>
                            <div className="font-bold whitespace-nowrap">[{q.marks}]</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
                
                {/* Footer */}
                <div className="py-8 text-center font-bold tracking-widest text-gray-600 font-serif border-t border-slate-200 mx-16">
                  *** END OF PAPER ***
                </div>
              </div>
            </motion.div>
          ) : (
            <Card hover={false} className="h-full min-h-[700px] flex flex-col items-center justify-center p-8 border-dashed border-2 text-center bg-gray-50/30">
              <div className="w-24 h-24 bg-gray-50 rounded-full flex items-center justify-center text-gray-600 mb-6 shadow-inner border border-gray-200">
                <FiFileText className="text-5xl" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">No Paper Generated</h3>
              <p className="text-gray-600 max-w-sm">Select your course and exam standard to draft a complete, structured examination paper.</p>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default QuestionPaper;
