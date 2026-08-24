import { useState, useCallback } from 'react';
import { getProjects, createProject, createTask } from '../services/api';

export const useWorkspaceActions = (reportId, idea) => {
  const [isAddingTask, setIsAddingTask] = useState(false);

  const handleAddTask = useCallback(async (title, description, sourceMetadata) => {
    setIsAddingTask(true);
    try {
      // 1. Get existing projects
      const projects = await getProjects();
      let project = projects.find(p => p.report_id === reportId);
      
      // 2. If no project linked to this report exists, create one
      if (!project) {
        const projectName = idea ? `Project: ${idea.substring(0, 30)}...` : 'New Startup Project';
        project = await createProject(projectName, 'Auto-generated workspace from validation report.', reportId);
      }
      
      // 3. Create the task
      await createTask({
        project_id: project.id,
        title,
        description,
        source_metadata: sourceMetadata
      });
      
      return true;
    } catch (e) {
      console.error('[useWorkspaceActions] Failed to add task:', e);
      return false;
    } finally {
      setIsAddingTask(false);
    }
  }, [reportId, idea]);

  return { handleAddTask, isAddingTask };
};
