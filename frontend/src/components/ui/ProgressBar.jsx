import { motion } from 'framer-motion';

const ProgressBar = ({ 
  progress = 0, 
  color = 'bg-[var(--color-primary)]', 
  height = 'h-2',
  showLabel = false,
  label
}) => {
  return (
    <div className="w-full">
      {showLabel && (
        <div className="flex justify-between items-center mb-2">
          {label && <span className="text-sm font-medium text-gray-700">{label}</span>}
          <span className="text-sm font-bold">{progress}%</span>
        </div>
      )}
      <div className={`w-full bg-gray-50 rounded-full overflow-hidden ${height}`}>
        <motion.div 
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 1, ease: 'easeOut' }}
          className={`${height} rounded-full ${color}`}
        />
      </div>
    </div>
  );
};

export default ProgressBar;
