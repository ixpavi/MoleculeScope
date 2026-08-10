import React from "react";

interface LogoProps {
  size?: number;
}

export const Logo: React.FC<LogoProps> = ({ size = 22 }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 32 32"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    style={{ flexShrink: 0 }}
  >
    <circle cx="16" cy="16" r="16" fill="#d98a3d" />
    <line x1="10" y1="20.5" x2="16" y2="10" stroke="#181310" strokeWidth="1.7" strokeLinecap="round" />
    <line x1="22" y1="20.5" x2="16" y2="10" stroke="#181310" strokeWidth="1.7" strokeLinecap="round" />
    <line x1="10" y1="20.5" x2="22" y2="20.5" stroke="#181310" strokeWidth="1.7" strokeLinecap="round" />
    <circle cx="16" cy="10" r="3.3" fill="#181310" />
    <circle cx="10" cy="20.5" r="2.6" fill="#181310" />
    <circle cx="22" cy="20.5" r="2.6" fill="#181310" />
  </svg>
);
