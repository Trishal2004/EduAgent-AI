import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiPlayCircle, FiChevronLeft, FiRefreshCw, FiLayers, FiPlus, FiFolder, FiCheck, FiX, FiAward, FiTrash2, FiMoreVertical, FiEdit2, FiStar } from 'react-icons/fi';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import ProgressBar from '../components/ui/ProgressBar';
import ConfirmDialog from '../components/common/ConfirmDialog';
import { srsFlashcardService } from '../services/srsFlashcardService';
import { documentService } from '../services/documentService';
import Quiz from './Quiz';
import React from 'react';

const Flashcards = () => {
  const [activeTab, setActiveTab] = useState('flashcards'); // flashcards, daily_quizzes
  const [decks, setDecks] = useState([]);
  const [selectedDeck, setSelectedDeck] = useState(null);
  const [dueCards, setDueCards] = useState([]);

  // Review Mode State
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [isReviewFinished, setIsReviewFinished] = useState(false);

  const searchParams = new URLSearchParams(window.location.search);
  const urlDocumentId = searchParams.get('doc');

  // Generator State
  const [topic, setTopic] = useState(urlDocumentId ? 'Document Deck' : '');
  const [selectedDocId, setSelectedDocId] = useState(urlDocumentId || '');
  const [documents, setDocuments] = useState([]);
  const [cardType, setCardType] = useState('definition');
  const [difficulty, setDifficulty] = useState('medium');
  const [numCards, setNumCards] = useState(10);
  const [isGenerating, setIsGenerating] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  // Delete State
  const [deckToDelete, setDeckToDelete] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);

  // Edit State
  const [editingDeck, setEditingDeck] = useState(null);
  const [editTitle, setEditTitle] = useState('');
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [activeDropdownMenu, setActiveDropdownMenu] = useState(null);

  useEffect(() => {
    loadDecks();
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      const data = await documentService.getDocuments();
      setDocuments(data);
    } catch (err) {
      console.error('Failed to load documents', err);
    }
  };

  const loadDecks = async () => {
    try {
      const data = await srsFlashcardService.getDecks();
      setDecks(data);
    } catch (err) {
      console.error(err);
    }
  };

  const startReview = async (deck) => {
    setSelectedDeck(deck);
    try {
      const cards = await srsFlashcardService.getDueCards(deck.id);
      setDueCards(cards);
      setCurrentIndex(0);
      setIsFlipped(false);
      setIsReviewFinished(false);
    } catch (err) {
      console.error(err);
    }
  };

  const submitScore = async (quality) => {
    try {
      const currentCard = dueCards[currentIndex];
      await srsFlashcardService.saveScore(currentCard.id, quality);

      if (currentIndex < dueCards.length - 1) {
        setIsFlipped(false);
        setTimeout(() => setCurrentIndex(prev => prev + 1), 150);
      } else {
        setIsReviewFinished(true);
        loadDecks(); // Refresh due counts
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleGenerate = async (e) => {
    e.preventDefault();
    
    // Topic is required unless a document is selected
    const finalTopic = topic.trim() || (selectedDocId ? 'Document Deck' : '');
    if (!finalTopic && !selectedDocId) return;

    setIsGenerating(true);
    setErrorMsg(null);

    try {
      const newDeck = await srsFlashcardService.generateDeck({
        topic: finalTopic,
        card_type: cardType,
        document_id: selectedDocId || null,
        difficulty: difficulty,
        number_of_cards: numCards
      });
      await loadDecks();
      setTopic(selectedDocId ? 'Document Deck' : '');
      startReview(newDeck);
    } catch (err) {
      console.error("Failed to generate and save deck", err);
      if (err.response?.status === 401) {
        setErrorMsg("Your session has expired. Please log in again.");
      } else if (err.response?.data?.detail) {
        const detail = err.response.data.detail;
        if (typeof detail === 'string') {
          setErrorMsg(detail);
        } else if (Array.isArray(detail)) {
          setErrorMsg(detail[0].msg);
        } else {
          setErrorMsg("Validation error occurred.");
        }
      } else {
        setErrorMsg("Failed to generate flashcards. Please try again.");
      }
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDeleteDeck = async () => {
    if (!deckToDelete) return;
    setIsDeleting(true);
    try {
      await srsFlashcardService.deleteDeck(deckToDelete.id);
      setDecks(prev => prev.filter(d => d.id !== deckToDelete.id));
      if (selectedDeck?.id === deckToDelete.id) {
        setSelectedDeck(null);
      }
      setDeckToDelete(null);
    } catch (err) {
      console.error("Failed to delete deck", err);
      // Optional: Add a toast notification for error here
    } finally {
      setIsDeleting(false);
    }
  };

  const handleUpdateDeck = async (e) => {
    e.preventDefault();
    if (!editingDeck || !editTitle.trim()) return;
    try {
      const updated = await srsFlashcardService.updateDeck(editingDeck.id, { title: editTitle });
      setDecks(prev => prev.map(d => d.id === editingDeck.id ? { ...d, ...updated, total_cards: d.total_cards, due_cards: d.due_cards } : d));
      setIsEditModalOpen(false);
      setEditingDeck(null);
    } catch (err) {
      console.error("Failed to update deck", err);
    }
  };

  const handleToggleFavorite = async (deck) => {
    try {
      const updated = await srsFlashcardService.updateDeck(deck.id, { is_favorite: !deck.is_favorite });
      setDecks(prev => prev.map(d => d.id === deck.id ? { ...d, ...updated, total_cards: d.total_cards, due_cards: d.due_cards } : d));
    } catch (err) {
      console.error("Failed to toggle favorite", err);
    }
  };

  const handleRegenerate = (deck) => {
    if (deck.document_id) {
      setSelectedDocId(deck.document_id);
    } else {
      setSelectedDocId('');
    }
    setTopic(deck.topic || deck.title);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const renderDeckList = () => (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Flashcard Library</h1>
        <p className="text-gray-600">Master concepts quickly with Spaced Repetition (SRS).</p>
      </div>

      {/* HORIZONTAL GENERATOR PANEL */}
      <div className="bg-gray-50/80 border border-gray-200/60 rounded-2xl p-6 shadow-md relative overflow-hidden">
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 to-indigo-500" />
        <h3 className="text-lg font-bold text-gray-900 mb-5 flex items-center gap-2">
          <FiLayers className="text-blue-400" /> Generate AI Deck
        </h3>
        
        {errorMsg && (
          <div className="mb-5 p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-sm flex items-start gap-3">
            <FiX className="shrink-0 mt-0.5" />
            <span>{errorMsg}</span>
          </div>
        )}
        
        <form onSubmit={handleGenerate} className="flex flex-col lg:flex-row gap-4 items-start lg:items-end">
          <div className="w-full lg:flex-1">
            <label className="block text-xs font-semibold text-gray-600 mb-2 uppercase tracking-wider">Source Document</label>
            <select
              value={selectedDocId}
              onChange={(e) => setSelectedDocId(e.target.value)}
              className="w-full px-4 py-3 text-sm rounded-xl bg-gray-50 border border-gray-200 text-gray-900 focus:outline-none focus:border-blue-500 transition-colors"
            >
              <option value="">General Knowledge (No Document)</option>
              {documents.map(doc => (
                <option key={doc.id} value={doc.id}>{doc.filename}</option>
              ))}
            </select>
          </div>
          
          <div className="w-full lg:flex-1">
            <label className="block text-xs font-semibold text-gray-600 mb-2 uppercase tracking-wider">Topic Focus</label>
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder={selectedDocId ? "Optional topic focus..." : "Required topic..."}
              className="w-full px-4 py-3 text-sm rounded-xl bg-gray-50 border border-gray-200 text-gray-900 focus:outline-none focus:border-blue-500 transition-colors"
            />
          </div>
          
          <div className="w-full sm:w-auto flex gap-4">
            <div className="w-32 shrink-0">
              <label className="block text-xs font-semibold text-gray-600 mb-2 uppercase tracking-wider">Difficulty</label>
              <select
                value={difficulty}
                onChange={(e) => setDifficulty(e.target.value)}
                className="w-full px-4 py-3 text-sm rounded-xl bg-gray-50 border border-gray-200 text-gray-900 focus:outline-none focus:border-blue-500 transition-colors"
              >
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
              </select>
            </div>
            
            <div className="w-32 shrink-0">
              <label className="block text-xs font-semibold text-gray-600 mb-2 uppercase tracking-wider">Count</label>
              <select
                value={numCards}
                onChange={(e) => setNumCards(Number(e.target.value))}
                className="w-full px-4 py-3 text-sm rounded-xl bg-gray-50 border border-gray-200 text-gray-900 focus:outline-none focus:border-blue-500 transition-colors"
              >
                <option value={5}>5 Cards</option>
                <option value={10}>10 Cards</option>
                <option value={20}>20 Cards</option>
              </select>
            </div>
          </div>
          
          <Button 
            type="submit" 
            disabled={(!topic.trim() && !selectedDocId) || isGenerating} 
            className="w-full lg:w-auto px-8 py-3 rounded-xl whitespace-nowrap h-[46px]" 
            icon={isGenerating ? <div className="w-4 h-4 rounded-full border-2 border-white border-t-transparent animate-spin" /> : <FiPlus />}
          >
            {isGenerating ? 'Generating...' : 'Create Deck'}
          </Button>
        </form>
      </div>

      {/* DECK GRID */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6 items-start">
        {decks.map(deck => {
          const masteredCount = deck.cards?.filter(c => c.review_history?.interval > 21).length || 0;
          const learningCount = deck.total_cards - masteredCount;
          const hasCardsToStudy = deck.due_cards > 0 || learningCount > 0;
          
          return (
          <div key={deck.id} className="bg-gray-50 border border-gray-200/60 rounded-2xl p-6 flex flex-col h-full shadow-sm relative group transition-all hover:border-gray-300/50 hover:shadow-md hover:-translate-y-1">
            <div className="absolute top-4 right-4 z-10 flex gap-2 items-center">
              <button 
                onClick={(e) => { e.stopPropagation(); handleToggleFavorite(deck); }}
                className={`p-2 rounded-lg transition-colors focus:outline-none ${deck.is_favorite ? 'text-yellow-400 opacity-100' : 'text-gray-400 hover:text-yellow-400 opacity-0 group-hover:opacity-100'}`}
                title="Favorite"
              >
                <FiStar className={deck.is_favorite ? "fill-yellow-400" : ""} size={18} />
              </button>
              
              <div className="relative">
                <button 
                  onClick={(e) => { 
                    e.stopPropagation(); 
                    setActiveDropdownMenu(activeDropdownMenu === deck.id ? null : deck.id); 
                  }}
                  className="p-2 rounded-lg text-gray-500 hover:bg-gray-200 transition-colors opacity-0 group-hover:opacity-100 focus:opacity-100"
                  title="Deck Actions"
                >
                  <FiMoreVertical size={18} />
                </button>
                
                {activeDropdownMenu === deck.id && (
                  <div 
                    className="absolute right-0 mt-2 w-48 bg-white rounded-xl shadow-lg border border-gray-100 py-1 z-20"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <button 
                      onClick={() => { setActiveDropdownMenu(null); startReview(deck); }}
                      className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2"
                    >
                      <FiPlayCircle /> Study Now
                    </button>
                    <button 
                      onClick={() => { 
                        setActiveDropdownMenu(null); 
                        setEditingDeck(deck);
                        setEditTitle(deck.title);
                        setIsEditModalOpen(true);
                      }}
                      className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2"
                    >
                      <FiEdit2 /> Edit Title
                    </button>
                    <button 
                      onClick={() => { setActiveDropdownMenu(null); handleRegenerate(deck); }}
                      className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2"
                    >
                      <FiRefreshCw /> Regenerate
                    </button>
                    <div className="border-t border-gray-100 my-1"></div>
                    <button 
                      onClick={() => { setActiveDropdownMenu(null); setDeckToDelete(deck); }}
                      className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center gap-2"
                    >
                      <FiTrash2 /> Delete
                    </button>
                  </div>
                )}
              </div>
            </div>

            <div className="flex justify-between items-start mb-4 pr-16">
              <div className="w-12 h-12 rounded-2xl bg-blue-500/10 text-blue-400 border border-blue-500/20 flex items-center justify-center text-2xl shrink-0">
                <FiFolder />
              </div>
            </div>
            
            <h3 className="text-xl font-bold text-gray-900 mb-2 line-clamp-2 leading-snug">{deck.title}</h3>
            <p className="text-sm font-medium text-gray-600 mb-6">{deck.total_cards} total cards</p>
            
            {/* Progress Stats */}
            <div className="space-y-3 mb-6 flex-1">
              <div className="flex justify-between text-xs font-bold uppercase tracking-wider">
                <span className="text-emerald-400 flex items-center gap-1.5"><FiCheck size={12}/> Mastered: {masteredCount}</span>
                <span className="text-blue-400 flex items-center gap-1.5"><FiLayers size={12}/> Learning: {learningCount}</span>
              </div>
              <div className="w-full h-2.5 bg-white rounded-full overflow-hidden flex shadow-inner">
                <div 
                  className="h-full bg-emerald-500 transition-all duration-1000" 
                  style={{ width: `${(masteredCount / (deck.total_cards || 1)) * 100}%` }}
                />
                <div 
                  className="h-full bg-blue-500 transition-all duration-1000" 
                  style={{ width: `${(learningCount / (deck.total_cards || 1)) * 100}%` }}
                />
              </div>
            </div>

            <button 
              onClick={() => startReview(deck)}
              className={`w-full py-3.5 px-4 rounded-xl font-bold text-sm text-center transition-all mt-auto flex items-center justify-center gap-2 ${hasCardsToStudy ? 'bg-blue-600 hover:bg-blue-500 text-gray-900 shadow-sm shadow-blue-900/30' : 'bg-gray-50/80 text-gray-600 hover:text-gray-900 hover:bg-gray-100'}`}
            >
              {hasCardsToStudy ? (
                <>
                  <FiPlayCircle size={18} />
                  {deck.due_cards > 0 ? `Study Now (${deck.due_cards} due)` : `Study Now (${learningCount} to review)`}
                </>
              ) : (
                <>
                  <FiCheck size={18} className="text-emerald-400" />
                  All caught up!
                </>
              )}
            </button>
          </div>
        )})}
      </div>

      <ConfirmDialog
        isOpen={!!deckToDelete}
        onClose={() => !isDeleting && setDeckToDelete(null)}
        onConfirm={handleDeleteDeck}
        title="Delete Flashcard Deck?"
        message={`Are you sure you want to delete '${deckToDelete?.title}'? This will permanently remove the deck and its flashcards.`}
        confirmText={isDeleting ? "Deleting..." : "Delete Deck"}
        confirmVariant="danger"
        isProcessing={isDeleting}
      />

      <AnimatePresence>
        {isEditModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-gray-900/40 backdrop-blur-sm">
            <motion.div 
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="bg-white rounded-2xl shadow-xl w-full max-w-md overflow-hidden"
            >
              <div className="p-6 border-b border-gray-100">
                <h3 className="text-xl font-bold text-gray-900">Edit Deck</h3>
              </div>
              <form onSubmit={handleUpdateDeck} className="p-6 space-y-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Deck Title</label>
                  <input
                    type="text"
                    value={editTitle}
                    onChange={(e) => setEditTitle(e.target.value)}
                    className="w-full px-4 py-3 rounded-xl bg-gray-50 border border-gray-200 text-gray-900 focus:outline-none focus:border-blue-500 transition-colors"
                    required
                  />
                </div>
                <div className="flex justify-end gap-3 pt-4">
                  <Button type="button" variant="neutral" onClick={() => setIsEditModalOpen(false)}>Cancel</Button>
                  <Button type="submit">Save Changes</Button>
                </div>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );

  const renderReviewMode = () => {
    if (isReviewFinished) {
      return (
        <Card hover={false} className="max-w-2xl mx-auto p-12 text-center flex flex-col items-center">
          <div className="w-24 h-24 bg-emerald-500/20 rounded-full flex items-center justify-center text-emerald-400 mb-6 border border-emerald-500/30 shadow-[0_0_30px_rgba(16,185,129,0.2)]">
            <FiAward className="text-5xl" />
          </div>
          <h2 className="text-3xl font-bold text-gray-900 mb-3">Session Complete!</h2>
          <p className="text-gray-600 mb-8 max-w-sm">You've successfully reviewed all due cards in <span className="text-gray-900 font-bold">{selectedDeck.title}</span>. The SRS algorithm will schedule them for your next optimal review time.</p>
          <Button variant="primary" onClick={() => setSelectedDeck(null)} icon={<FiChevronLeft />}>Back to Library</Button>
        </Card>
      );
    }

    if (dueCards.length === 0) {
      return (
        <div className="text-center py-20">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">No cards due for review!</h2>
          <Button onClick={() => setSelectedDeck(null)}>Back to Library</Button>
        </div>
      );
    }

    return (
      <div className="max-w-4xl mx-auto flex flex-col items-center space-y-8">
        <div className="w-full flex justify-between items-center">
          <button onClick={() => setSelectedDeck(null)} className="text-gray-600 hover:text-gray-900 flex items-center gap-2 transition-colors">
            <FiChevronLeft /> Back to Library
          </button>
          <Badge variant="neutral" className="px-4 py-1 text-sm bg-gray-50">
            Card {currentIndex + 1} of {dueCards.length}
          </Badge>
        </div>

        <div className="w-full max-w-2xl">
          <ProgressBar progress={((currentIndex) / dueCards.length) * 100} height="h-2" />
        </div>

        {/* 3D Flip Card */}
        <div
          className="relative w-full max-w-2xl h-96 perspective-[1000px] cursor-pointer group"
          onClick={() => !isFlipped && setIsFlipped(true)}
        >
          <motion.div
            className="w-full h-full relative preserve-3d transition-transform duration-500 ease-out"
            animate={{ rotateY: isFlipped ? 180 : 0 }}
          >
            {/* Front side (Question) */}
            <div className="absolute inset-0 backface-hidden glass-panel rounded-3xl flex flex-col justify-center items-center p-8 text-center bg-gray-50 border border-gray-200 shadow-md">
              <Badge variant="neutral" className="absolute top-6 left-6 uppercase tracking-wider text-xs">{dueCards[currentIndex].card_type}</Badge>
              <h3 className="text-2xl md:text-3xl font-bold text-gray-900 leading-tight">{dueCards[currentIndex].question}</h3>
              <p className="absolute bottom-8 text-sm text-gray-600 flex items-center gap-2 animate-pulse">
                <FiRefreshCw /> Click to reveal answer
              </p>
            </div>

            {/* Back side (Answer) */}
            <div className="absolute inset-0 backface-hidden glass-panel rounded-3xl flex flex-col justify-center items-center p-8 text-center bg-white border-2 border-blue-500/50 shadow-[0_0_30px_rgba(37,99,235,0.15)] transform rotate-y-180">
              <p className="text-sm text-blue-400 font-bold mb-6 tracking-widest uppercase">Answer</p>
              <p className="text-xl md:text-2xl font-medium text-gray-900 leading-relaxed whitespace-pre-line">{dueCards[currentIndex].answer}</p>
            </div>
          </motion.div>
        </div>

        {/* SRS Controls */}
        <div className="h-20 w-full max-w-2xl">
          {isFlipped ? (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="grid grid-cols-4 gap-3 sm:gap-4 w-full"
            >
              <button onClick={() => submitScore(1)} className="py-3 sm:py-4 px-2 sm:px-4 rounded-2xl bg-red-500/10 hover:bg-red-500/20 border border-red-500/50 text-red-500 font-bold flex flex-col items-center justify-center transition-all">
                <span className="text-base sm:text-lg mb-1">Again</span>
                <span className="text-[10px] sm:text-xs font-medium opacity-70">&lt; 1m</span>
              </button>
              <button onClick={() => submitScore(3)} className="py-3 sm:py-4 px-2 sm:px-4 rounded-2xl bg-orange-500/10 hover:bg-orange-500/20 border border-orange-500/50 text-orange-500 font-bold flex flex-col items-center justify-center transition-all">
                <span className="text-base sm:text-lg mb-1">Hard</span>
                <span className="text-[10px] sm:text-xs font-medium opacity-70">~ 2d</span>
              </button>
              <button onClick={() => submitScore(4)} className="py-3 sm:py-4 px-2 sm:px-4 rounded-2xl bg-blue-500/10 hover:bg-blue-500/20 border border-blue-500/50 text-blue-500 font-bold flex flex-col items-center justify-center transition-all shadow-[0_0_15px_rgba(37,99,235,0.1)]">
                <span className="text-base sm:text-lg mb-1">Good</span>
                <span className="text-[10px] sm:text-xs font-medium opacity-70">~ 4d</span>
              </button>
              <button onClick={() => submitScore(5)} className="py-3 sm:py-4 px-2 sm:px-4 rounded-2xl bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/50 text-emerald-500 font-bold flex flex-col items-center justify-center transition-all">
                <span className="text-base sm:text-lg mb-1">Easy</span>
                <span className="text-[10px] sm:text-xs font-medium opacity-70">~ 6d</span>
              </button>
            </motion.div>
          ) : (
            <div className="flex justify-center text-gray-600 text-sm">
              Think of the answer, then click the card to flip it.
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="max-w-6xl mx-auto pb-12">
      {/* Tabs */}
      {!selectedDeck && (
        <div className="flex border-b border-gray-200/50 mb-8">
          <button
            onClick={() => setActiveTab('flashcards')}
            className={`px-6 py-4 font-bold text-sm uppercase tracking-wider transition-colors border-b-2 ${activeTab === 'flashcards' ? 'text-blue-400 border-blue-500' : 'text-gray-600 border-transparent hover:text-gray-700'}`}
          >
            Flashcard Decks
          </button>
          <button
            onClick={() => setActiveTab('daily_quizzes')}
            className={`px-6 py-4 font-bold text-sm uppercase tracking-wider transition-colors border-b-2 ${activeTab === 'daily_quizzes' ? 'text-blue-400 border-blue-500' : 'text-gray-600 border-transparent hover:text-gray-700'}`}
          >
            Daily Quizzes
          </button>
        </div>
      )}

      {activeTab === 'flashcards' && (
        selectedDeck ? renderReviewMode() : renderDeckList()
      )}

      {activeTab === 'daily_quizzes' && !selectedDeck && (
        <Quiz mode="daily_only" />
      )}
    </div>
  );
};

export default Flashcards;
