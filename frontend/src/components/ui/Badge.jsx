const variants = {
  success: 'bg-[var(--color-success)]/10 text-[var(--color-success)] border-[var(--color-success)]/20',
  warning: 'bg-[var(--color-warning)]/10 text-[var(--color-warning)] border-[var(--color-warning)]/20',
  danger: 'bg-[var(--color-danger)]/10 text-[var(--color-danger)] border-[var(--color-danger)]/20',
  primary: 'bg-[var(--color-primary)]/10 text-blue-400 border-[var(--color-primary)]/20',
  neutral: 'bg-gray-50 text-gray-700 border-gray-200',
};

const Badge = ({ children, variant = 'neutral', className = '', icon }) => {
  return (
    <span className={`
      inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold border
      ${variants[variant]}
      ${className}
    `}>
      {icon && <span className="text-sm">{icon}</span>}
      {children}
    </span>
  );
};

export default Badge;
