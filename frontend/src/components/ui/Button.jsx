import { motion } from 'framer-motion';

const variants = {
  primary: 'bg-[var(--color-primary)] text-white hover:bg-blue-500 shadow-sm hover:shadow-[0_0_20px_rgba(37,99,235,0.5)] border border-blue-400/30',
  secondary: 'bg-[var(--color-bg-card)] text-[var(--color-text-main)] hover:bg-gray-100 border border-[var(--color-border-subtle)]',
  danger: 'bg-[var(--color-danger)]/10 text-[var(--color-danger)] hover:bg-[var(--color-danger)] hover:text-gray-900 border border-[var(--color-danger)]/30',
  ghost: 'bg-transparent text-[var(--color-text-muted)] hover:text-[var(--color-text-main)] hover:bg-gray-50',
};

const sizes = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-5 py-2.5 text-base',
  lg: 'px-8 py-3.5 text-lg font-semibold',
};

const Button = ({ 
  children, 
  variant = 'primary', 
  size = 'md', 
  className = '', 
  icon,
  onClick,
  disabled,
  type = 'button'
}) => {
  return (
    <motion.button
      type={type}
      whileHover={{ scale: disabled ? 1 : 1.02, y: disabled ? 0 : -1 }}
      whileTap={{ scale: disabled ? 1 : 0.98 }}
      onClick={onClick}
      disabled={disabled}
      className={`
        relative overflow-hidden rounded-xl font-medium transition-all duration-300
        flex items-center justify-center gap-2
        ${variants[variant]} 
        ${sizes[size]} 
        ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
        ${className}
      `}
    >
      {/* Subtle overlay for interactions */}
      <div className="absolute inset-0 bg-white opacity-0 hover:opacity-10 transition-opacity pointer-events-none" />
      
      {icon && <span className="text-xl">{icon}</span>}
      {children}
    </motion.button>
  );
};

export default Button;
