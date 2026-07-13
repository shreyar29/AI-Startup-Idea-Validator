const Dashboard = () => {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Dashboard</h1>
        <p className="text-textMuted">View your previously validated startup ideas and generated reports.</p>
      </div>
      
      <div className="glass-panel rounded-xl p-12 text-center border border-white/5">
        <div className="w-16 h-16 mx-auto bg-surface rounded-full flex items-center justify-center mb-4">
          <span className="text-textMuted text-2xl">📋</span>
        </div>
        <h3 className="text-xl font-medium text-white mb-2">No reports yet</h3>
        <p className="text-textMuted max-w-md mx-auto">
          You haven't validated any startup ideas yet. Head over to the validation page to get started.
        </p>
      </div>
    </div>
  );
};

export default Dashboard;
