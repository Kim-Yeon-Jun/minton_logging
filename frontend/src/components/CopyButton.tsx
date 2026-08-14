import { useState } from 'react';

export interface CopyButtonProps {
  value: string;
  label?: string;
  variant?: 'icon' | 'text';
}

export default function CopyButton({ value, label = '복사하기', variant = 'icon' }: CopyButtonProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(value);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      // 클립보드 접근이 차단된 환경(비보안 컨텍스트 등)에서는 조용히 무시합니다.
    }
  };

  if (variant === 'text') {
    return (
      <button type="button" className="copy-button-text" onClick={handleCopy} aria-label={label}>
        {copied ? '✅ 복사되었습니다' : `📋 ${label}`}
      </button>
    );
  }

  return (
    <button
      type="button"
      className="copy-button"
      onClick={handleCopy}
      aria-label={label}
      title={copied ? '복사되었습니다' : label}
    >
      {copied ? '✅' : '📋'}
    </button>
  );
}
