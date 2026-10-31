"use client";

import { motion, useInView } from "framer-motion";
import { useRef, useState } from "react";
import { Mail, Github, Linkedin, Send, MapPin, Phone } from "lucide-react";
import { personalInfo } from "@/data/resume";

export default function Contact() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-300px" });
  const [formData, setFormData] = useState({ name: "", email: "", message: "" });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState<"idle" | "success" | "error">("idle");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    setTimeout(() => {
      console.log("Form submitted:", formData);
      setSubmitStatus("success");
      setIsSubmitting(false);
      setFormData({ name: "", email: "", message: "" });
      setTimeout(() => setSubmitStatus("idle"), 3000);
    }, 1500);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  return (
    <section
      id="contact"
      ref={ref}
      className="py-32 bg-navy-950 relative overflow-hidden"
    >
      {/* Geometric background */}
      <div className="absolute top-1/2 left-0 w-96 h-96 bg-navy-700/5 blur-3xl" />

      <div className="max-w-7xl mx-auto px-6 lg:px-8 relative z-10">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
          className="mb-16 text-center"
        >
          <div className="flex items-center justify-center gap-4 mb-6">
            <div className="w-16 h-1 bg-azure" />
            <span className="text-azure font-mono text-sm uppercase tracking-widest">
              // LET'S CONNECT
            </span>
            <div className="w-16 h-1 bg-azure" />
          </div>
          <h2 className="text-6xl md:text-7xl lg:text-8xl font-black text-slate-50 tracking-tighter">
            GET IN TOUCH
          </h2>
        </motion.div>

        <div className="grid lg:grid-cols-5 gap-12">
          {/* Left - Contact Info */}
          <motion.div
            initial={{ opacity: 0, x: -80 }}
            animate={isInView ? { opacity: 1, x: 0 } : { opacity: 0, x: -80 }}
            transition={{ delay: 0.2, duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
            className="lg:col-span-2 space-y-8"
          >
            {/* Contact Cards */}
            <div className="space-y-4">
              <a
                href={`mailto:${personalInfo.email}`}
                className="block border-2 border-electric/30 bg-dark p-6 hover:border-electric hover:bg-navy-900 transition-all group"
              >
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-electric/10 group-hover:bg-electric/20 transition-colors">
                    <Mail className="text-electric" size={24} />
                  </div>
                  <div>
                    <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">Email</p>
                    <p className="font-bold text-slate-50">{personalInfo.email}</p>
                  </div>
                </div>
              </a>

              <a
                href={`tel:${personalInfo.phone}`}
                className="block border-2 border-azure/30 bg-dark p-6 hover:border-azure hover:bg-navy-900 transition-all group"
              >
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-azure/10 group-hover:bg-azure/20 transition-colors">
                    <Phone className="text-azure" size={24} />
                  </div>
                  <div>
                    <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">Phone</p>
                    <p className="font-bold text-slate-50">{personalInfo.phone}</p>
                  </div>
                </div>
              </a>

              <div className="border-2 border-navy-700/30 bg-dark p-6">
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-navy-700/10">
                    <MapPin className="text-navy-700" size={24} />
                  </div>
                  <div>
                    <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">Location</p>
                    <p className="font-bold text-slate-50">{personalInfo.location}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Social Links */}
            <div className="space-y-4">
              <h3 className="text-slate-50 font-black uppercase text-lg">CONNECT</h3>
              <div className="flex gap-4">
                <a
                  href={personalInfo.linkedin}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex-1 border-2 border-slate-400/30 p-4 flex items-center justify-center gap-2 hover:border-electric hover:bg-navy-900 transition-all group"
                >
                  <Linkedin className="text-slate-400 group-hover:text-electric transition-colors" size={20} />
                </a>
                <a
                  href={personalInfo.github}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex-1 border-2 border-slate-400/30 p-4 flex items-center justify-center gap-2 hover:border-electric hover:bg-navy-900 transition-all group"
                >
                  <Github className="text-slate-400 group-hover:text-electric transition-colors" size={20} />
                </a>
              </div>
            </div>

            {/* Availability */}
            <div className="border-l-4 border-azure pl-6 py-4 bg-navy-900">
              <p className="text-azure font-bold text-sm uppercase tracking-wider mb-2">
                WANT TO CONNECT?
              </p>
              <p className="text-slate-300 text-sm leading-relaxed">
                Always open to collaborating on interesting projects and connecting with fellow developers.
              </p>
            </div>
          </motion.div>

          {/* Right - Contact Form */}
          <motion.div
            initial={{ opacity: 0, x: 80 }}
            animate={isInView ? { opacity: 1, x: 0 } : { opacity: 0, x: 80 }}
            transition={{ delay: 0.4, duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
            className="lg:col-span-3"
          >
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-bold text-slate-50 mb-2 uppercase tracking-wider">
                    NAME
                  </label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    required
                    className="w-full px-4 py-4 bg-dark border-2 border-slate-400/30 text-slate-50 focus:border-electric focus:outline-none transition-all"
                    placeholder="John Doe"
                  />
                </div>
                <div>
                  <label className="block text-sm font-bold text-slate-50 mb-2 uppercase tracking-wider">
                    EMAIL
                  </label>
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    required
                    className="w-full px-4 py-4 bg-dark border-2 border-slate-400/30 text-slate-50 focus:border-electric focus:outline-none transition-all"
                    placeholder="john@example.com"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-bold text-slate-50 mb-2 uppercase tracking-wider">
                  MESSAGE
                </label>
                <textarea
                  name="message"
                  value={formData.message}
                  onChange={handleChange}
                  required
                  rows={8}
                  className="w-full px-4 py-4 bg-dark border-2 border-slate-400/30 text-slate-50 focus:border-electric focus:outline-none transition-all resize-none"
                  placeholder="Tell me about your project..."
                />
              </div>

              <button
                type="submit"
                disabled={isSubmitting}
                className={`w-full px-8 py-4 font-bold text-lg uppercase tracking-wider flex items-center justify-center gap-3 transition-all ${
                  submitStatus === "success"
                    ? "bg-azure text-dark"
                    : "bg-electric text-dark hover:bg-azure"
                }`}
              >
                {isSubmitting ? (
                  <>
                    <motion.div
                      className="w-5 h-5 border-2 border-dark border-t-transparent rounded-full"
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                    />
                    SENDING...
                  </>
                ) : submitStatus === "success" ? (
                  "✓ MESSAGE SENT!"
                ) : (
                  <>
                    SEND MESSAGE
                    <Send size={20} />
                  </>
                )}
              </button>
            </form>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
