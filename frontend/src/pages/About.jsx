const About = () => {
  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <h1 className="text-4xl font-bold text-white mb-6">About VentureLens</h1>
      <div className="prose prose-invert max-w-none text-textMuted leading-relaxed space-y-6">
        <p>
          VentureLens is a Multi-Agent AI System designed to help entrepreneurs, builders, and investors validate startup ideas instantly. By leveraging the power of advanced LLMs and real-time web search capabilities, VentureLens transforms a simple sentence into a comprehensive market analysis report.
        </p>
        <h2 className="text-2xl font-semibold text-white mt-12 mb-4">How it works</h2>
        <ul className="list-disc pl-5 space-y-2">
          <li><strong>Query Agent:</strong> Analyzes the core concept to understand the industry, product, and target audience, formulating precise search queries.</li>
          <li><strong>Web Search Agent:</strong> Executes search strategies live on the web to gather data on competitors, market trends, and potential pain points.</li>
          <li><strong>Market Analysis:</strong> Processes the raw data to generate actionable insights, evaluating viability and calculating a confidence score.</li>
        </ul>
        <h2 className="text-2xl font-semibold text-white mt-12 mb-4">Architecture</h2>
        <p>
          Built with a robust FastAPI backend utilizing the OpenRouter API for LLM orchestration and Tavily for deep search. The frontend is powered by React, Tailwind CSS, and Framer Motion, delivering a seamless, modern SaaS experience.
        </p>
      </div>
    </div>
  );
};

export default About;
