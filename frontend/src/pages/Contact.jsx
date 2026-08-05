import React from 'react';
import { motion } from 'framer-motion';
import { Mail, MessageSquare, MapPin } from 'lucide-react';

const Contact = () => {
  return (
    <div className="min-h-screen pt-24 pb-12 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
      <div className="text-center max-w-2xl mx-auto mb-16">
        <motion.h1 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-4xl md:text-5xl font-bold mb-6"
        >
          Get in Touch
        </motion.h1>
        <motion.p 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="text-lg text-textMuted"
        >
          Have questions about the validation process? Need support with an enterprise account? We're here to help.
        </motion.p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="glass-panel p-8 rounded-3xl text-center flex flex-col items-center"
        >
          <div className="bg-primary/10 w-16 h-16 rounded-full flex items-center justify-center mb-6">
            <Mail className="h-8 w-8 text-primary" />
          </div>
          <h3 className="text-xl font-bold mb-2">Email Support</h3>
          <p className="text-textMuted mb-4">Please use the contact form below to reach our support team.</p>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="glass-panel p-8 rounded-3xl text-center flex flex-col items-center"
        >
          <div className="bg-secondary/10 w-16 h-16 rounded-full flex items-center justify-center mb-6">
            <MessageSquare className="h-8 w-8 text-secondary" />
          </div>
          <h3 className="text-xl font-bold mb-2">Live Chat</h3>
          <p className="text-textMuted mb-4">Available Mon-Fri, 9am - 5pm EST.</p>
          <button className="text-secondary font-medium hover:text-secondary/80 transition-colors">
            Start a Conversation
          </button>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="glass-panel p-8 rounded-3xl text-center flex flex-col items-center"
        >
          <div className="bg-accent/10 w-16 h-16 rounded-full flex items-center justify-center mb-6">
            <MapPin className="h-8 w-8 text-accent" />
          </div>
          <h3 className="text-xl font-bold mb-2">Global Team</h3>
          <p className="text-textMuted mb-4">We are a fully remote organization.</p>
        </motion.div>
      </div>

      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="max-w-2xl mx-auto glass-panel p-8 md:p-12 rounded-3xl"
      >
        <h3 className="text-2xl font-bold mb-6 text-center">Send a Message</h3>
        <form className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">First Name</label>
              <input type="text" className="w-full bg-surface/50 border border-white/10 rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-primary focus:border-primary transition-all" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Last Name</label>
              <input type="text" className="w-full bg-surface/50 border border-white/10 rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-primary focus:border-primary transition-all" />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Email Address</label>
            <input type="email" className="w-full bg-surface/50 border border-white/10 rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-primary focus:border-primary transition-all" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Message</label>
            <textarea rows="4" className="w-full bg-surface/50 border border-white/10 rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-primary focus:border-primary transition-all resize-none"></textarea>
          </div>
          <button type="button" className="w-full bg-primary hover:bg-primaryDark text-white font-bold py-4 rounded-xl transition-colors">
            Send Message
          </button>
        </form>
      </motion.div>
    </div>
  );
};

export default Contact;
