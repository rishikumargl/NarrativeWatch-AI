import React, { createContext, useState, useCallback, useEffect } from 'react'
import { apiGetJson, apiPostJson, apiPut, apiDelete } from '../utils/api_client'

export const ProjectContext = createContext()

export function ProjectProvider({ children }) {
  const [projects, setProjects] = useState([])
  const [currentProject, setCurrentProject] = useState(null)
  const [loading, setLoading] = useState(false)

  const loadProjects = useCallback(async () => {
    setLoading(true)
    try {
      const data = await apiGetJson('/api/projects')
      setProjects(data || [])
    } catch (error) {
      console.error('Failed to load projects:', error)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadProjects()
  }, [loadProjects])

  const createProject = useCallback(async (name, description = '') => {
    try {
      const data = await apiPostJson('/api/projects', { name, description })
      setProjects([...projects, data])
      return data
    } catch (error) {
      console.error('Failed to create project:', error)
      throw error
    }
  }, [projects])

  const updateProject = useCallback(async (projectId, name, description) => {
    try {
      const response = await apiPut(`/api/projects/${projectId}`, { name, description })
      const data = await response.json()
      setProjects(projects.map(p => p.id === projectId ? data : p))
      if (currentProject?.id === projectId) {
        setCurrentProject(data)
      }
      return data
    } catch (error) {
      console.error('Failed to update project:', error)
      throw error
    }
  }, [projects, currentProject])

  const deleteProject = useCallback(async (projectId) => {
    try {
      await apiDelete(`/api/projects/${projectId}`)
      setProjects(projects.filter(p => p.id !== projectId))
      if (currentProject?.id === projectId) {
        setCurrentProject(null)
      }
    } catch (error) {
      console.error('Failed to delete project:', error)
      throw error
    }
  }, [projects, currentProject])

  const value = {
    projects,
    currentProject,
    setCurrentProject,
    loading,
    createProject,
    updateProject,
    deleteProject,
    loadProjects
  }

  return (
    <ProjectContext.Provider value={value}>
      {children}
    </ProjectContext.Provider>
  )
}

export function useProjects() {
  const context = React.useContext(ProjectContext)
  if (!context) {
    throw new Error('useProjects must be used within ProjectProvider')
  }
  return context
}
