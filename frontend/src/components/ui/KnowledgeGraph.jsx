import { useRef, useEffect, useState } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { motion, AnimatePresence } from 'framer-motion';
import { FiX, FiBook, FiPlayCircle, FiFileText, FiMessageSquare } from 'react-icons/fi';
import Button from './Button';
import Badge from './Badge';
import { kgService } from '../../services/kgService';
import React from 'react';

// Green: Mastered, Orange: Needs Revision, Red: Weak Topic, Blue: Current Topic
const NODE_COLORS = {
  mastered: '#10b981',   // emerald-500
  revision: '#f59e0b',   // amber-500
  weak: '#ef4444',       // red-500
  current: '#3b82f6'     // blue-500
};

const TopicDetailsModal = ({ node, details, onClose }) => {
  if (!node) return null;
  
  const getStatusText = (status) => {
    switch(status) {
      case 'mastered': return 'Mastered';
      case 'revision': return 'Needs Revision';
      case 'weak': return 'Weak Topic';
      case 'current': return 'Current Topic';
      default: return 'Unknown';
    }
  };

  const getStatusVariant = (status) => {
    switch(status) {
      case 'mastered': return 'success';
      case 'revision': return 'warning';
      case 'weak': return 'danger';
      case 'current': return 'neutral';
      default: return 'neutral';
    }
  };

  return (
    <AnimatePresence>
      <motion.div 
        initial={{ opacity: 0, x: 50 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: 50 }}
        className="absolute top-4 right-4 w-80 bg-[var(--color-bg-card)] border border-[var(--color-border-subtle)] shadow-md rounded-2xl overflow-hidden z-50 flex flex-col"
      >
        <div className="p-4 border-b border-[var(--color-border-subtle)] bg-gray-100/80 flex justify-between items-start">
          <div>
            <h3 className="font-bold text-lg text-gray-900 mb-1">{node.name}</h3>
            <Badge variant={getStatusVariant(node.status)}>{getStatusText(node.status)}</Badge>
          </div>
          <button onClick={onClose} className="p-1 text-gray-600 hover:text-gray-900 transition-colors">
            <FiX className="text-xl" />
          </button>
        </div>
        
        <div className="p-4 flex-1 overflow-y-auto space-y-4">
          <div>
            <p className="text-xs font-bold text-gray-600 uppercase tracking-wider mb-2">Topic Definition</p>
            <p className="text-sm text-gray-700">
              {node.name} is a dynamically extracted concept from your uploaded documents. 
              {details && ` Mastery level is ${details.mastery_level} with a difficulty of ${details.difficulty}.`}
            </p>
          </div>

          <div>
            <p className="text-xs font-bold text-gray-600 uppercase tracking-wider mb-2">Related Resources</p>
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm p-2 bg-gray-50 rounded-lg">
                <span className="flex items-center gap-2 text-gray-700"><FiBook /> Notes</span>
                <span className="text-blue-400 font-bold">{details?.related_notes || 0}</span>
              </div>
              <div className="flex items-center justify-between text-sm p-2 bg-gray-50 rounded-lg">
                <span className="flex items-center gap-2 text-gray-700"><FiFileText /> Flashcards</span>
                <span className="text-blue-400 font-bold">{details?.related_flashcards || 0}</span>
              </div>
              <div className="flex items-center justify-between text-sm p-2 bg-gray-50 rounded-lg">
                <span className="flex items-center gap-2 text-gray-700"><FiPlayCircle /> Quizzes</span>
                <span className="text-blue-400 font-bold">{details?.related_quizzes || 0}</span>
              </div>
            </div>
          </div>

          <div>
            <p className="text-xs font-bold text-gray-600 uppercase tracking-wider mb-2">AI Quick Actions</p>
            <div className="grid grid-cols-2 gap-2">
              <Button variant="secondary" className="text-xs py-1.5 px-2 justify-center"><FiBook className="mr-1"/> Gen Notes</Button>
              <Button variant="secondary" className="text-xs py-1.5 px-2 justify-center"><FiPlayCircle className="mr-1"/> Gen Quiz</Button>
              <Button variant="secondary" className="text-xs py-1.5 px-2 justify-center"><FiFileText className="mr-1"/> Gen Cards</Button>
              <Button variant="secondary" className="text-xs py-1.5 px-2 justify-center bg-blue-600/20 text-blue-400 border-blue-500/30 hover:bg-blue-600/40"><FiMessageSquare className="mr-1"/> Ask AI</Button>
            </div>
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
};

const KnowledgeGraph = () => {
  const containerRef = useRef();
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [selectedNode, setSelectedNode] = useState(null);
  const [selectedNodeDetails, setSelectedNodeDetails] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadGraphData();
  }, []);

  const loadGraphData = async () => {
    try {
      const data = await kgService.getGraph();
      if (data.nodes.length === 0) {
        // Fallback or empty state could go here
        setGraphData({ nodes: [], links: [] });
      } else {
        setGraphData(data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleNodeClick = async (node) => {
    setSelectedNode(node);
    setSelectedNodeDetails(null);
    try {
      const details = await kgService.getTopicDetails(node.id);
      setSelectedNodeDetails(details);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    if (containerRef.current) {
      const { width, height } = containerRef.current.getBoundingClientRect();
      setDimensions({ width, height });
    }
    
    const handleResize = () => {
      if (containerRef.current) {
        const { width, height } = containerRef.current.getBoundingClientRect();
        setDimensions({ width, height });
      }
    };
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  if (loading) {
    return <div className="w-full h-full flex items-center justify-center text-gray-600">Loading graph...</div>;
  }

  if (graphData.nodes.length === 0) {
    return (
      <div className="w-full h-full flex flex-col items-center justify-center text-gray-600 bg-white border border-gray-200 rounded-2xl">
        <FiBook className="text-4xl mb-4 opacity-50" />
        <p>No topics found. Upload a document to generate your knowledge graph!</p>
      </div>
    );
  }

  return (
    <div className="relative w-full h-full rounded-2xl overflow-hidden bg-white border border-gray-200 shadow-inner" ref={containerRef}>
      
      {/* Top Legend */}
      <div className="absolute top-4 left-4 z-10 bg-gray-100/80 backdrop-blur border border-gray-200 p-3 rounded-xl shadow-sm pointer-events-none">
        <h4 className="text-xs font-bold text-gray-900 mb-2 uppercase tracking-widest">Topic Mastery</h4>
        <div className="flex flex-col gap-2">
          <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]"></div><span className="text-xs text-gray-700">Mastered</span></div>
          <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.5)]"></div><span className="text-xs text-gray-700">Needs Revision</span></div>
          <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]"></div><span className="text-xs text-gray-700">Weak Topic</span></div>
          <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.5)]"></div><span className="text-xs text-gray-700">Current Focus</span></div>
        </div>
      </div>

      <ForceGraph2D
        width={dimensions.width}
        height={dimensions.height}
        graphData={graphData}
        nodeColor={(node) => NODE_COLORS[node.status] || '#94a3b8'}
        nodeRelSize={6}
        linkWidth={2}
        linkColor={() => 'rgba(148, 163, 184, 0.2)'}
        nodeLabel="name"
        onNodeClick={handleNodeClick}
        nodeCanvasObject={(node, ctx, globalScale) => {
          const label = node.name;
          const fontSize = 12 / globalScale;
          ctx.font = `${fontSize}px Inter, sans-serif`;
          const textWidth = ctx.measureText(label).width;
          const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.2);

          ctx.fillStyle = 'rgba(15, 23, 42, 0.8)';
          ctx.fillRect(node.x - bckgDimensions[0] / 2, node.y - bckgDimensions[1] / 2, ...bckgDimensions);

          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillStyle = NODE_COLORS[node.status] || '#fff';
          ctx.fillText(label, node.x, node.y);

          // Add a glow ring based on status
          ctx.beginPath();
          ctx.arc(node.x, node.y, bckgDimensions[0]/2 + 2, 0, 2 * Math.PI, false);
          ctx.strokeStyle = NODE_COLORS[node.status] || '#fff';
          ctx.lineWidth = 0.5;
          ctx.stroke();
        }}
      />

      {/* Interactive Modal */}
      {selectedNode && (
        <TopicDetailsModal 
          node={selectedNode} 
          details={selectedNodeDetails}
          onClose={() => setSelectedNode(null)} 
        />
      )}
      
    </div>
  );
};

export default KnowledgeGraph;
