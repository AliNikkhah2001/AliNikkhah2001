import { useRef, useState, type KeyboardEvent } from 'react'
import { marked } from 'marked'

marked.setOptions({ gfm: true, breaks: true })

interface MarkdownEditorProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
  minHeight?: number
}

type Mode = 'write' | 'preview' | 'split'

const TOOLBAR: Array<{
  label: string
  title: string
  action: 'wrap' | 'line'
  before?: string
  after?: string
  prefix?: string
}> = [
  { label: 'B', title: 'Bold', action: 'wrap', before: '**', after: '**' },
  { label: 'I', title: 'Italic', action: 'wrap', before: '*', after: '*' },
  { label: '`', title: 'Inline code', action: 'wrap', before: '`', after: '`' },
  { label: 'H1', title: 'Heading 1', action: 'line', prefix: '# ' },
  { label: 'H2', title: 'Heading 2', action: 'line', prefix: '## ' },
  { label: '•', title: 'Bullet list', action: 'line', prefix: '- ' },
  { label: '1.', title: 'Numbered list', action: 'line', prefix: '1. ' },
  { label: '❝', title: 'Quote', action: 'line', prefix: '> ' },
  { label: '🔗', title: 'Link', action: 'wrap', before: '[', after: '](https://)' },
  { label: '</>', title: 'Code block', action: 'wrap', before: '```\n', after: '\n```' },
  { label: '—', title: 'Horizontal rule', action: 'line', prefix: '---\n' },
]

export function MarkdownEditor({ value, onChange, placeholder, minHeight = 180 }: MarkdownEditorProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const [mode, setMode] = useState<Mode>('split')

  const applyFormat = (item: (typeof TOOLBAR)[number]) => {
    const ta = textareaRef.current
    if (!ta) return
    const { selectionStart: s, selectionEnd: e, value: v } = ta
    const selected = v.slice(s, e)

    let insertion: string
    let cursor: number

    if (item.action === 'wrap') {
      const inner = selected || 'text'
      insertion = `${item.before}${inner}${item.after}`
      cursor = s + (item.before?.length ?? 0) + inner.length
      if (!selected) {
        onChange(v.slice(0, s) + insertion + v.slice(e))
        requestAnimationFrame(() => {
          ta.focus()
          const start = s + (item.before?.length ?? 0)
          ta.setSelectionRange(start, start + inner.length)
        })
        return
      }
    } else {
      const lines = (selected || '').split('\n')
      const prefixed = lines.map((ln) => `${item.prefix}${ln}`).join('\n')
      insertion = selected ? prefixed : `${item.prefix}\n`
      cursor = s + insertion.length
    }

    onChange(v.slice(0, s) + insertion + v.slice(e))
    requestAnimationFrame(() => {
      ta.focus()
      ta.setSelectionRange(cursor, cursor)
    })
  }

  const onTab = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key !== 'Tab') return
    e.preventDefault()
    const ta = e.currentTarget
    const { selectionStart: s, selectionEnd: e2, value: v } = ta
    onChange(v.slice(0, s) + '  ' + v.slice(e2))
    requestAnimationFrame(() => ta.setSelectionRange(s + 2, s + 2))
  }

  const html = value.trim() ? marked.parse(value, { async: false }) : ''

  return (
    <div className="md-editor">
      <div className="md-toolbar">
        <div className="d-flex gap-2 flex-wrap">
          {TOOLBAR.map((item) => (
            <button
              key={item.title}
              type="button"
              className="md-btn"
              title={item.title}
              onClick={() => applyFormat(item)}
            >
              {item.label}
            </button>
          ))}
        </div>
        <div className="d-flex gap-2">
          {(['write', 'split', 'preview'] as Mode[]).map((m) => (
            <button
              key={m}
              type="button"
              className={`md-mode-btn ${mode === m ? 'active' : ''}`}
              onClick={() => setMode(m)}
            >
              {m}
            </button>
          ))}
        </div>
      </div>

      <div className={`md-body ${mode === 'split' ? 'md-split' : ''}`}>
        {mode !== 'preview' && (
          <textarea
            ref={textareaRef}
            className="md-textarea"
            style={{ minHeight }}
            value={value}
            placeholder={placeholder || 'Write markdown…'}
            onChange={(e) => onChange(e.target.value)}
            onKeyDown={onTab}
          />
        )}
        {mode !== 'write' && (
          <div
            className="md-preview"
            style={{ minHeight }}
            dangerouslySetInnerHTML={{ __html: html || '<p class="md-empty">Nothing to preview</p>' }}
          />
        )}
      </div>
    </div>
  )
}
