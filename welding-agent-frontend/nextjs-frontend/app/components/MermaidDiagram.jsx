'use client';

import { useEffect, useRef, useState } from 'react';

export default function MermaidDiagram({ chart }) {
  const containerRef = useRef(null);
  const [svg, setSvg] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!chart) return;

    let cancelled = false;

    const render = async () => {
      try {
        const mermaid = (await import('mermaid')).default;
        
        // Initialize mermaid once (if not already)
        if (!mermaid.getConfig) {
          mermaid.initialize({
            startOnLoad: false,
            theme: 'default',
            securityLevel: 'loose',
          });
        }

        const id = `mermaid-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
        const { svg: svgContent } = await mermaid.render(id, chart);
        
        if (!cancelled) setSvg(svgContent);
      } catch (err) {
        console.error('Mermaid render error:', err);
        if (!cancelled) setError('Failed to render diagram');
      }
    };

    render();

    return () => { cancelled = true; };
  }, [chart]);

  if (error) {
    return (
      <div style={{ border: '1px solid #f87171', borderRadius: 8, padding: 12, background: '#fef2f2', fontSize: 12 }}>
        <div style={{ color: '#dc2626', marginBottom: 8 }}>⚠️ {error}</div>
        <pre style={{ margin: 0, whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
          {chart}
        </pre>
      </div>
    );
  }

  if (!svg) {
    return (
      <div style={{ textAlign: 'center', padding: 24, color: '#64748b' }}>
        <div className="typing-dots" style={{ display: 'flex', gap: 4, justifyContent: 'center' }}>
          <span style={{ width: 8, height: 8, background: '#64748b', borderRadius: '50%', animation: 'bounce 1.4s infinite ease-in-out' }}></span>
          <span style={{ width: 8, height: 8, background: '#64748b', borderRadius: '50%', animation: 'bounce 1.4s infinite ease-in-out', animationDelay: 0.2 }}></span>
          <span style={{ width: 8, height: 8, background: '#64748b', borderRadius: '50%', animation: 'bounce 1.4s infinite ease-in-out', animationDelay: 0.4 }}></span>
        </div>
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      dangerouslySetInnerHTML={{ __html: svg }}
      style={{ textAlign: 'center', overflow: 'auto', padding: '1rem', background: '#f8fafc', borderRadius: 8 }}
    />
  );
}