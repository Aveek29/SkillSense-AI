import React from 'react'

const Button = React.memo(function Button({
  children,
  variant = 'primary',
  size = 'md',
  icon: Icon,
  onClick,
  disabled = false,
  className = '',
  ...props
}) {
  const baseClasses = {
    primary: 'btn-interactive',
    outline: 'btn-outline',
    danger: 'btn-danger',
  }

  const sizeStyles = {
    sm: { padding: '8px 16px', fontSize: '0.8rem' },
    md: { padding: '12px 24px', fontSize: '0.95rem' },
    lg: { padding: '16px 32px', fontSize: '1.05rem' },
  }

  return (
    <button
      className={`${baseClasses[variant] || baseClasses.primary} ${className}`}
      style={{
        ...sizeStyles[size],
        display: 'inline-flex',
        alignItems: 'center',
        gap: '8px',
        opacity: disabled ? 0.5 : 1,
        pointerEvents: disabled ? 'none' : 'auto',
      }}
      onClick={onClick}
      disabled={disabled}
      {...props}
    >
      {Icon && <Icon size={size === 'sm' ? 14 : size === 'lg' ? 20 : 16} />}
      {children}
    </button>
  )
})

export default Button
