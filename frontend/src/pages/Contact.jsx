import { Mail, MessageSquare, MapPin } from 'lucide-react';

const Contact = () => {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="text-center mb-16">
        <h1 className="text-4xl font-bold text-white mb-4">Get in Touch</h1>
        <p className="text-lg text-textMuted max-w-2xl mx-auto">
          Have questions about the platform, enterprise integration, or just want to say hi? We'd love to hear from you.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
        <div className="space-y-8">
          <div className="flex items-start space-x-4">
            <div className="w-12 h-12 rounded-lg bg-surface flex items-center justify-center flex-shrink-0 border border-white/5">
              <Mail className="w-6 h-6 text-primary" />
            </div>
            <div>
              <h3 className="text-lg font-medium text-white mb-1">Email</h3>
              <p className="text-textMuted mb-2">Our friendly team is here to help.</p>
              <a href="mailto:hello@venturelens.ai" className="text-primary hover:text-primaryHover transition-colors">
                hello@venturelens.ai
              </a>
            </div>
          </div>

          <div className="flex items-start space-x-4">
            <div className="w-12 h-12 rounded-lg bg-surface flex items-center justify-center flex-shrink-0 border border-white/5">
              <MessageSquare className="w-6 h-6 text-primary" />
            </div>
            <div>
              <h3 className="text-lg font-medium text-white mb-1">Live Chat</h3>
              <p className="text-textMuted mb-2">Available Mon-Fri, 9am to 5pm EST.</p>
              <button className="text-primary hover:text-primaryHover transition-colors">
                Start a conversation
              </button>
            </div>
          </div>
          
          <div className="flex items-start space-x-4">
            <div className="w-12 h-12 rounded-lg bg-surface flex items-center justify-center flex-shrink-0 border border-white/5">
              <MapPin className="w-6 h-6 text-primary" />
            </div>
            <div>
              <h3 className="text-lg font-medium text-white mb-1">Office</h3>
              <p className="text-textMuted">
                123 Innovation Drive<br />
                Tech District<br />
                San Francisco, CA 94105
              </p>
            </div>
          </div>
        </div>

        <div className="glass-panel p-8 rounded-xl border border-white/5">
          <form className="space-y-6" onSubmit={(e) => e.preventDefault()}>
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-textMuted mb-2">Name</label>
              <input
                type="text"
                id="name"
                className="w-full bg-surface border border-white/10 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all"
                placeholder="John Doe"
              />
            </div>
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-textMuted mb-2">Email</label>
              <input
                type="email"
                id="email"
                className="w-full bg-surface border border-white/10 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all"
                placeholder="john@example.com"
              />
            </div>
            <div>
              <label htmlFor="message" className="block text-sm font-medium text-textMuted mb-2">Message</label>
              <textarea
                id="message"
                rows={4}
                className="w-full bg-surface border border-white/10 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all resize-none"
                placeholder="How can we help you?"
              ></textarea>
            </div>
            <button
              type="submit"
              className="w-full bg-primary hover:bg-primaryHover text-white font-medium py-3 px-4 rounded-lg transition-colors"
            >
              Send Message
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Contact;
