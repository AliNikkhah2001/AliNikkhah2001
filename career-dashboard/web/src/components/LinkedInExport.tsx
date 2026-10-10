import { useState, useEffect } from 'react'
import { CareerDatabase } from '../types'
import { api } from '../api'

interface LinkedInExportProps {
  db: CareerDatabase | null
}

export function LinkedInExport({ db }: LinkedInExportProps) {
  const [sections, setSections] = useState<any>({})
  const [copied, setCopied] = useState<string | null>(null)

  useEffect(() => {
    if (db) {
      api.exportLinkedIn().then(setSections)
    }
  }, [db])

  const copyToClipboard = (text: string, key: string) => {
    navigator.clipboard.writeText(text)
    setCopied(key)
    setTimeout(() => setCopied(null), 2000)
  }

  const formatExperience = (exp: any) => {
    let text = `${exp.title}\n${exp.company}\n${exp.location}\n${exp.duration}\n\n${exp.description}`
    return text
  }

  const formatEducation = (edu: any) => {
    let text = `${edu.school}\n${edu.degree}${edu.field ? `, ${edu.field}` : ''}\n${edu.dates}`
    if (edu.description) text += `\n${edu.description}`
    return text
  }

  const allExperienceText = sections.experience?.map(formatExperience).join('\n\n---\n\n') || ''
  const allEducationText = sections.education?.map(formatEducation).join('\n\n---\n\n') || ''
  const skillsText = sections.skills?.join(', ') || ''

  return (
    <div className="card">
      <h2 style={{ marginBottom: '1rem' }}>LinkedIn Profile Sections</h2>
      <p className="text-muted mb-4">
        Copy individual sections or the full profile. Paste directly into LinkedIn's profile editor.
        <br />
        <strong>Note:</strong> LinkedIn does not provide a public API for automated profile updates. This generates formatted text for manual copy-paste.
      </p>

      <div className="d-flex gap-2 mb-4 flex-wrap">
        <button className="btn btn-primary" onClick={() => copyToClipboard(allExperienceText, 'experience')}>
          Copy All Experience
        </button>
        <button className="btn btn-outline" onClick={() => copyToClipboard(allEducationText, 'education')}>
          Copy All Education
        </button>
        <button className="btn btn-outline" onClick={() => copyToClipboard(skillsText, 'skills')}>
          Copy Skills
        </button>
        <button className="btn btn-outline" onClick={() => copyToClipboard(sections.headline || '', 'headline')}>
          Copy Headline
        </button>
        <button className="btn btn-outline" onClick={() => copyToClipboard(sections.about || '', 'about')}>
          Copy About
        </button>
      </div>

      {copied && (
        <div className="alert alert-success" style={{ background: '#d1e7dd', border: '1px solid #badbcc', color: '#0f5132', padding: '0.75rem 1rem', borderRadius: 6, marginBottom: '1rem' }}>
          Copied to clipboard!
        </div>
      )}

      <hr style={{ margin: '1.5rem 0' }} />

      <h3>Headline</h3>
      <div className="linkedin-box">
        <div className="linkedin-box-header">
          <span className="linkedin-box-title">Headline</span>
          <button className="copy-btn btn btn-outline btn-sm" onClick={() => copyToClipboard(sections.headline || '', 'headline')}>
            {copied === 'headline' ? 'Copied!' : 'Copy'}
          </button>
        </div>
        <div className="linkedin-box-description">{sections.headline || '—'}</div>
      </div>

      <h3 className="mt-4">About</h3>
      <div className="linkedin-box">
        <div className="linkedin-box-header">
          <span className="linkedin-box-title">About</span>
          <button className="copy-btn btn btn-outline btn-sm" onClick={() => copyToClipboard(sections.about || '', 'about')}>
            {copied === 'about' ? 'Copied!' : 'Copy'}
          </button>
        </div>
        <div className="linkedin-box-description">{sections.about || '—'}</div>
      </div>

      <h3 className="mt-4">Experience ({sections.experience?.length || 0} entries)</h3>
      {sections.experience?.map((exp: any, i: number) => (
        <div key={i} className="linkedin-box">
          <div className="linkedin-box-header">
            <div>
              <div className="linkedin-box-title">{exp.title}</div>
              <div className="linkedin-box-company">{exp.company}</div>
            </div>
            <div className="d-flex gap-2">
              <span className="linkedin-box-duration">{exp.duration}</span>
              <button className="copy-btn btn btn-outline btn-sm" onClick={() => copyToClipboard(formatExperience(exp), `exp-${i}`)}>
                {copied === `exp-${i}` ? 'Copied!' : 'Copy'}
              </button>
            </div>
          </div>
          <div className="linkedin-box-description">{exp.description}</div>
          <div className="linkedin-box-duration">{exp.location}</div>
        </div>
      ))}

      <h3 className="mt-4">Education ({sections.education?.length || 0} entries)</h3>
      {sections.education?.map((edu: any, i: number) => (
        <div key={i} className="linkedin-box">
          <div className="linkedin-box-header">
            <div>
              <div className="linkedin-box-title">{edu.school}</div>
              <div className="linkedin-box-company">{edu.degree}{edu.field ? `, ${edu.field}` : ''}</div>
            </div>
            <div className="d-flex gap-2">
              <span className="linkedin-box-duration">{edu.dates}</span>
              <button className="copy-btn btn btn-outline btn-sm" onClick={() => copyToClipboard(formatEducation(edu), `edu-${i}`)}>
                {copied === `edu-${i}` ? 'Copied!' : 'Copy'}
              </button>
            </div>
          </div>
          {edu.description && <div className="linkedin-box-description">{edu.description}</div>}
        </div>
      ))}

      <h3 className="mt-4">Skills ({sections.skills?.length || 0})</h3>
      <div className="linkedin-box">
        <div className="linkedin-box-header">
          <span className="linkedin-box-title">Skills</span>
          <button className="copy-btn btn btn-outline btn-sm" onClick={() => copyToClipboard(skillsText, 'skills')}>
            {copied === 'skills' ? 'Copied!' : 'Copy'}
          </button>
        </div>
        <div className="linkedin-box-description" style={{ columns: '2', columnGap: '2rem' }}>
          {sections.skills?.map((skill: string, i: number) => (
            <div key={i} style={{ breakInside: 'avoid', padding: '0.25rem 0' }}>
              • {skill}
            </div>
          ))}
        </div>
      </div>

      <hr style={{ margin: '1.5rem 0' }} />

      <h3>Full Profile (All Sections Combined)</h3>
      <button className="btn btn-primary mb-3" onClick={() => copyToClipboard(
        `HEADLINE\n${sections.headline}\n\nABOUT\n${sections.about}\n\nEXPERIENCE\n${allExperienceText}\n\nEDUCATION\n${allEducationText}\n\nSKILLS\n${skillsText}`,
        'full'
      )}>
        Copy Complete Profile
      </button>

      <textarea
        readOnly
        style={{ width: '100%', height: 400, fontFamily: 'monospace', fontSize: '0.8rem', padding: '1rem', border: '1px solid #dee2e6', borderRadius: 6 }}
        value={`HEADLINE
${sections.headline}

ABOUT
${sections.about}

EXPERIENCE
${allExperienceText}

EDUCATION
${allEducationText}

SKILLS
${skillsText}`}
      />
    </div>
  )
}