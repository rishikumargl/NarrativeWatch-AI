import { useState } from 'react'
import LoadingSpinner from './LoadingSpinner'
import './AnalysisForm.css'

function AnalysisForm({ onAnalysis, loading }) {
  const [formData, setFormData] = useState({
    type: 'post',
    url: '',
    username: '',
    includeContext: true,
    checkCampaigns: true
  })

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!formData.url && !formData.username) {
      alert('Please enter either a post URL or username')
      return
    }
    onAnalysis(formData)
  }

  return (
    <form className="analysis-form" onSubmit={handleSubmit}>
      <h2>Analyze Content</h2>

      <div className="form-group">
        <label htmlFor="type">Analysis Type</label>
        <select
          id="type"
          name="type"
          value={formData.type}
          onChange={handleChange}
        >
          <option value="post">Post Analysis</option>
          <option value="page">Page Analysis</option>
        </select>
      </div>

      {formData.type === 'post' ? (
        <div className="form-group">
          <label htmlFor="url">Post URL</label>
          <input
            id="url"
            type="text"
            name="url"
            placeholder="https://instagram.com/p/..."
            value={formData.url}
            onChange={handleChange}
          />
        </div>
      ) : (
        <div className="form-group">
          <label htmlFor="username">Username</label>
          <input
            id="username"
            type="text"
            name="username"
            placeholder="@username"
            value={formData.username}
            onChange={handleChange}
          />
        </div>
      )}

      <div className="form-group checkbox">
        <label htmlFor="includeContext">
          <input
            id="includeContext"
            type="checkbox"
            name="includeContext"
            checked={formData.includeContext}
            onChange={handleChange}
          />
          Include Context (RAG Analysis)
        </label>
      </div>

      <div className="form-group checkbox">
        <label htmlFor="checkCampaigns">
          <input
            id="checkCampaigns"
            type="checkbox"
            name="checkCampaigns"
            checked={formData.checkCampaigns}
            onChange={handleChange}
          />
          Check for Campaigns
        </label>
      </div>

      <button type="submit" className="submit-btn" disabled={loading}>
        {loading ? <LoadingSpinner /> : 'Analyze'}
      </button>
    </form>
  )
}

export default AnalysisForm
