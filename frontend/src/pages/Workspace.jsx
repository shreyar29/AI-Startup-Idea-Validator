import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { getProjects, getTasks, updateTask, createProject, createTask } from '../services/api';
import { FolderGit2, GripVertical, CheckCircle2, Circle, Clock, Plus, LayoutGrid, ShieldAlert } from 'lucide-react';
import ErrorState from '../components/ErrorState';

const Workspace = () => {
  const [projects, setProjects] = useState([]);
  const [activeProject, setActiveProject] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchWorkspace = async () => {
    try {
      setLoading(true);
      const projData = await getProjects();
      setProjects(projData);
      if (projData.length > 0) {
        setActiveProject(projData[0]);
        const taskData = await getTasks(projData[0].id);
        setTasks(taskData);
      }
    } catch (err) {
      // In this demo environment without actual auth, mock some data or show error
      console.error(err);
      setError('Could not connect to workspace. Please make sure you are logged in.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWorkspace();
  }, []);

  const handleStatusChange = async (taskId, newStatus) => {
    // Optimistic UI update
    setTasks(tasks.map(t => t.id === taskId ? { ...t, status: newStatus } : t));
    try {
      await updateTask(taskId, { status: newStatus });
    } catch (err) {
      console.error(err);
      fetchWorkspace(); // Revert on failure
    }
  };

  const columns = [
    { id: 'Todo', title: 'To Do', icon: Circle, color: 'text-slate-400' },
    { id: 'In Progress', title: 'In Progress', icon: Clock, color: 'text-blue-400' },
    { id: 'Done', title: 'Done', icon: CheckCircle2, color: 'text-green-400' }
  ];

  if (loading) return (
    <div className="min-h-screen pt-24 flex items-center justify-center">
      <div className="animate-spin w-8 h-8 border-4 border-primary border-t-transparent rounded-full"></div>
    </div>
  );

  if (error && projects.length === 0) return <ErrorState message={error} onRetry={fetchWorkspace} />;

  return (
    <div className="pt-24 pb-12 max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 min-h-screen">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-textMain tracking-tight">Founder Workspace</h1>
          <p className="text-textMuted mt-2">Manage your startup roadmap and strategic tasks.</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-primary hover:bg-primary/90 text-white rounded-lg font-medium transition-colors">
          <Plus className="w-4 h-4" />
          New Project
        </button>
      </div>

      {projects.length === 0 ? (
        <div className="glass-panel p-12 text-center rounded-2xl border-white/5">
          <FolderGit2 className="w-12 h-12 text-textMuted mx-auto mb-4 opacity-50" />
          <h3 className="text-lg font-bold text-textMain">No projects found</h3>
          <p className="text-textMuted mt-1 mb-6">Validate an idea to automatically create a workspace project.</p>
        </div>
      ) : (
        <div className="flex gap-6 h-[calc(100vh-200px)]">
          {/* Projects Sidebar */}
          <div className="w-64 flex-shrink-0 space-y-2">
            <h3 className="text-xs font-bold text-textMuted uppercase tracking-wider mb-4 px-2">Projects</h3>
            {projects.map(p => (
              <button
                key={p.id}
                onClick={async () => {
                  setActiveProject(p);
                  const taskData = await getTasks(p.id);
                  setTasks(taskData);
                }}
                className={`w-full text-left px-4 py-3 rounded-xl flex items-center gap-3 transition-colors ${
                  activeProject?.id === p.id ? 'bg-primary/10 text-primary font-medium' : 'hover:bg-surface/50 text-textMuted'
                }`}
              >
                <LayoutGrid className="w-4 h-4" />
                <span className="truncate">{p.name}</span>
              </button>
            ))}
          </div>

          {/* Kanban Board */}
          <div className="flex-grow flex gap-4 overflow-x-auto pb-4">
            {columns.map(col => {
              const colTasks = tasks.filter(t => t.status === col.id);
              
              return (
                <div key={col.id} className="flex-1 min-w-[320px] max-w-[400px] flex flex-col bg-surface/20 rounded-2xl border border-white/5 overflow-hidden">
                  <div className="p-4 border-b border-white/5 flex items-center justify-between bg-surface/40">
                    <div className="flex items-center gap-2">
                      <col.icon className={`w-4 h-4 ${col.color}`} />
                      <h3 className="font-bold text-textMain">{col.title}</h3>
                    </div>
                    <span className="text-xs font-medium px-2 py-0.5 bg-black/20 rounded-md text-textMuted">
                      {colTasks.length}
                    </span>
                  </div>
                  
                  <div className="flex-grow p-4 space-y-3 overflow-y-auto">
                    {colTasks.map(task => (
                      <motion.div
                        layoutId={task.id}
                        key={task.id}
                        className="glass-panel p-4 rounded-xl border border-white/5 hover:border-white/10 cursor-pointer group"
                      >
                        <div className="flex justify-between items-start gap-2 mb-2">
                          <h4 className="text-sm font-medium text-textMain leading-snug">{task.title}</h4>
                          <GripVertical className="w-4 h-4 text-textDim opacity-0 group-hover:opacity-100 transition-opacity" />
                        </div>
                        
                        {task.description && (
                          <p className="text-xs text-textMuted line-clamp-2 mb-3">{task.description}</p>
                        )}
                        
                        <div className="flex items-center justify-between mt-4">
                          <div className="flex items-center gap-2">
                            {task.priority && (
                              <span className={`text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded border ${
                                task.priority === 'Critical' ? 'border-error/30 text-error' :
                                task.priority === 'High' ? 'border-warning/30 text-warning' :
                                'border-primary/30 text-primary'
                              }`}>
                                {task.priority}
                              </span>
                            )}
                            {task.source_metadata?.agent && (
                              <span className="text-[10px] text-textMuted flex items-center gap-1">
                                <ShieldAlert className="w-3 h-3" />
                                {task.source_metadata.agent}
                              </span>
                            )}
                          </div>
                          
                          {/* Quick Actions (Mocked dragging) */}
                          <div className="flex gap-1">
                            {col.id !== 'Todo' && (
                              <button onClick={() => handleStatusChange(task.id, 'Todo')} className="p-1 hover:bg-white/10 rounded">
                                <Circle className="w-3 h-3 text-textDim" />
                              </button>
                            )}
                            {col.id !== 'In Progress' && (
                              <button onClick={() => handleStatusChange(task.id, 'In Progress')} className="p-1 hover:bg-white/10 rounded">
                                <Clock className="w-3 h-3 text-textDim" />
                              </button>
                            )}
                            {col.id !== 'Done' && (
                              <button onClick={() => handleStatusChange(task.id, 'Done')} className="p-1 hover:bg-white/10 rounded">
                                <CheckCircle2 className="w-3 h-3 text-textDim" />
                              </button>
                            )}
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default Workspace;
