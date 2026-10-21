import KnowledgeGraph from '../components/ui/KnowledgeGraph';

const Graph = () => {
  return (
    <div className="h-[calc(100vh-6rem)] -mt-4 -mb-8 -mx-4 md:-mx-8 flex flex-col bg-[var(--color-bg-base)]">
      <div className="p-6 shrink-0">
        <h1 className="text-3xl font-bold tracking-tight mb-2">Interactive Knowledge Graph</h1>
        <p className="text-[var(--color-text-muted)] text-lg">Explore how concepts are interconnected. Click any topic to access related notes, flashcards, and quizzes.</p>
      </div>
      <div className="flex-1 px-6 pb-6 relative overflow-hidden">
        <KnowledgeGraph />
      </div>
    </div>
  );
};

export default Graph;
