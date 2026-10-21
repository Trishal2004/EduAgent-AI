import { motion } from 'framer-motion';

const Card = ({ children, className = '', hover = true, onClick }) => {
  const Component = onClick ? motion.button : motion.div;
  
  return (
    <Component
      onClick={onClick}
      whileHover={hover && onClick ? { y: -4, scale: 1.01 } : hover ? { y: -4 } : {}}
      className={`glass-card p-6 text-left w-full ${onClick ? 'cursor-pointer' : ''} ${className}`}
    >
      {children}
    </Component>
  );
};

export default Card;
