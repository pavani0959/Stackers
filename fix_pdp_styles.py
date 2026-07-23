import re

with open('src/screens/ProductDetail/ProductDetail.jsx', 'r') as f:
    content = f.read()

# Emojis -> Lucide
content = content.replace("import {\n  ArrowLeft,\n  Heart,\n  X,\n} from 'lucide-react';", 
"import {\n  ArrowLeft,\n  Heart,\n  X,\n  Shirt,\n  Sparkles,\n  Dna,\n} from 'lucide-react';")

content = content.replace("<span className=\"img-fallback-icon\" style={{ fontSize: '18px' }}>👕</span>",
"<Shirt className=\"img-fallback-icon\" size={18} />")

content = content.replace("<span style={{ marginRight: '6px' }}>✨</span> Try it on AR",
"<Sparkles size={16} style={{ marginRight: '6px' }} /> Try it on AR")

content = content.replace("<span style={{ fontSize: '16px' }}>🧬</span>",
"<Dna size={16} />")

# Inline styles -> classes
# AlternativeItem wrapper
content = content.replace("""    <article
      className="alt-item"
      style={{
        minWidth: '160px',
        padding: '10px',
        border: '1px solid var(--line-soft, #e7e7ec)',
        borderRadius: '12px',
      }}
    >""", '    <article className="alt-item det-alt-item">')

content = content.replace("""      <div style={{
        width: '100%',
        aspectRatio: '4 / 5',
        borderRadius: '8px',
        overflow: 'hidden',
        background: 'var(--surface-2)',
        position: 'relative'
      }}>""", '      <div className="det-alt-img-wrap">')

content = content.replace("""            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              display: 'block'
            }}""", '            className="det-alt-img"')

content = content.replace("style={{ padding: '8px' }}", 'className="det-alt-fallback"')
content = content.replace("style={{ fontSize: '10px' }}", 'className="det-alt-fallback-text"')

content = content.replace("<div style={{ fontSize: '0.8rem', marginTop: '8px' }}>", '<div className="det-alt-info">')
content = content.replace("<p style={{ margin: '4px 0 8px', color: 'var(--ink-500)', fontSize: '0.7rem' }}>", '<p className="det-alt-reason">')

content = content.replace("<div style={{ display: 'grid', gap: '6px' }}>", '<div className="det-alt-actions">')

# Header right buttons
content = content.replace("<div style={{ display: 'flex', gap: '8px' }}>", '<div className="det-header-actions">')

# AR action bar
content = content.replace("""<div className="det-action-bar" style={{ position: 'absolute', bottom: '16px', left: '0', right: '0', padding: '0 16px', display: 'flex', justifyContent: 'center' }}>""", '<div className="det-action-bar det-ar-bar">')

content = content.replace("""            style={{ background: 'rgba(255, 255, 255, 0.9)', backdropFilter: 'blur(4px)', border: '1px solid var(--border)', borderRadius: '999px', padding: '8px 16px', fontSize: '13px', fontWeight: '600', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}""", '')

# det-pr-row inner
content = content.replace("""            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>""", '<div className="det-price-wrap">')

# match pill
content = content.replace("""<div className="det-conf-pill-inline" style={{ display: 'flex', alignItems: 'center', gap: '6px', background: 'var(--surface-2)', padding: '6px 10px', borderRadius: 'var(--radius-pill)', border: '1px solid var(--border)' }}>""", '<div className="det-conf-pill-inline det-match-pill">')
content = content.replace("""<span className="det-score" style={{ fontSize: '14px', fontWeight: '800', color: 'var(--color-primary)' }}>{decision.overall_score}%</span>""", '<span className="det-score">{decision.overall_score}%</span>')
content = content.replace("""<span className="det-score-lbl" style={{ fontSize: '11px', fontWeight: '600', color: 'var(--text-2)' }}>Match</span>""", '<span className="det-score-lbl">Match</span>')

# Size selector
content = content.replace("""<section style={{ marginTop: '8px' }}>""", '<section className="det-size-section">')
content = content.replace("""<p className="size-label" style={{ fontSize: '14px', marginBottom: '8px' }}>Select Size</p>""", '<p className="size-label">Select Size</p>')

# DNA breakdown
content = content.replace("""<details className="conf-card-details" style={{ background: 'white', border: '1px solid var(--border)', borderRadius: 'var(--radius-md)', padding: '0', marginTop: '16px', overflow: 'hidden' }}>""", '<details className="conf-card-details det-dna-details">')
content = content.replace("""<summary style={{ padding: '16px', cursor: 'pointer', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontWeight: '700', listStyle: 'none' }}>""", '<summary className="det-dna-summary">')
content = content.replace("""<div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>""", '<div className="det-dna-summary-left">')
content = content.replace("""<span style={{ color: 'var(--text)', fontSize: '15px' }}>Fashion DNA Breakdown</span>""", '<span className="det-dna-title">Fashion DNA Breakdown</span>')
content = content.replace("""<span style={{ color: 'var(--text-3)' }}>▼</span>""", '<span className="det-dna-icon">▼</span>')

content = content.replace("""<div style={{ padding: '0 16px 16px', borderTop: '1px solid var(--surface-2)' }}>""", '<div className="det-dna-content">')
content = content.replace("""<p style={{ fontSize: '13px', color: 'var(--text-2)', margin: '12px 0 16px', lineHeight: '1.4' }}>""", '<p className="det-dna-desc">')

content = content.replace("""<div className="conf-row" key={name} style={{ marginBottom: '12px' }}>""", '<div className="conf-row" key={name}>')
content = content.replace("""<span className="conf-lbl" style={{ fontSize: '13px' }}>""", '<span className="conf-lbl">')
content = content.replace("""<span className="conf-pct" style={{ fontSize: '13px' }}>{component.score}%</span>""", '<span className="conf-pct">{component.score}%</span>')

content = content.replace("""              style={{ width: '100%', marginTop: '8px', padding: '12px', background: 'var(--surface-2)', border: 'none', borderRadius: 'var(--radius-sm)', fontWeight: '600', color: 'var(--text)', cursor: 'pointer' }}""", '')


with open('src/screens/ProductDetail/ProductDetail.jsx', 'w') as f:
    f.write(content)
