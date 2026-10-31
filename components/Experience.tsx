"use client";

import { motion, useInView } from "framer-motion";
import { useRef, useState } from "react";
import { Calendar, MapPin, ArrowRight } from "lucide-react";
import { experience } from "@/data/resume";

export default function Experience() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-300px" });
  const [expandedId, setExpandedId] = useState<string | null>(experience[0].id);

  return (
    <section
      id="experience"
      ref={ref}
      className="py-32 bg-navy-950 relative overflow-hidden"
    >
      {/* Geometric background */}
      <div className="absolute bottom-0 right-0 w-96 h-96 bg-electric/5 blur-3xl" />

      <div className="max-w-7xl mx-auto px-6 lg:px-8 relative z-10">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
          className="mb-16"
        >
          <div className="flex items-center gap-4 mb-6">
            <div className="w-16 h-1 bg-navy-700" />
            <span className="text-navy-700 font-mono text-sm uppercase tracking-widest">
              // CAREER PATH
            </span>
          </div>
          <h2 className="text-6xl md:text-7xl lg:text-8xl font-black text-slate-50 tracking-tighter">
            EXPERIENCE
          </h2>
        </motion.div>

        {/* Experience List */}
        <div className="space-y-4">
          {experience.map((job, idx) => {
            const isExpanded = expandedId === job.id;

            return (
              <motion.div
                key={job.id}
                initial={{ opacity: 0, x: -80 }}
                animate={isInView ? { opacity: 1, x: 0 } : { opacity: 0, x: -80 }}
                transition={{ delay: idx * 0.15, duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
                whileHover={{ x: 8, transition: { duration: 0.3 } }}
                className={`border-2 transition-colors ${
                  isExpanded
                    ? "border-navy-700 bg-navy-900"
                    : "border-slate-400/20 bg-dark hover:border-navy-700/50"
                }`}
              >
                {/* Job Header - Always Visible */}
                <button
                  onClick={() => setExpandedId(isExpanded ? null : job.id)}
                  className="w-full p-8 text-left flex items-start justify-between gap-4"
                >
                  <div className="flex-1">
                    <div className="flex flex-wrap items-center gap-3 mb-2">
                      <h3 className="text-2xl md:text-3xl font-black text-slate-50 uppercase">
                        {job.title}
                      </h3>
                      <span className="px-3 py-1 bg-navy-700 text-dark text-xs font-bold uppercase tracking-wider">
                        {job.type}
                      </span>
                    </div>

                    <p className="text-navy-700 font-bold text-lg mb-3">{job.company}</p>

                    <div className="flex flex-wrap gap-4 text-sm text-slate-400">
                      <span className="flex items-center gap-2">
                        <Calendar size={16} />
                        {job.duration}
                      </span>
                      <span className="flex items-center gap-2">
                        <MapPin size={16} />
                        {job.location}
                      </span>
                    </div>
                  </div>

                  <div className={`transition-transform ${isExpanded ? "rotate-90" : ""}`}>
                    <ArrowRight className="text-navy-700" size={24} />
                  </div>
                </button>

                {/* Expanded Content */}
                <motion.div
                  initial={false}
                  animate={{
                    height: isExpanded ? "auto" : 0,
                    opacity: isExpanded ? 1 : 0,
                  }}
                  transition={{ duration: 0.3 }}
                  className="overflow-hidden"
                >
                  <div className="px-8 pb-8 space-y-6 border-t border-navy-700/30 pt-6">
                    {/* Description */}
                    <p className="text-slate-300 text-lg leading-relaxed">
                      {job.description}
                    </p>

                    {/* Responsibilities */}
                    <div>
                      <h4 className="text-electric font-bold text-sm uppercase tracking-wider mb-3">
                        KEY RESPONSIBILITIES
                      </h4>
                      <ul className="space-y-3">
                        {job.responsibilities.map((resp, idx) => (
                          <li key={idx} className="flex items-start gap-3 text-slate-300">
                            <span className="text-navy-700 mt-1 font-bold">▸</span>
                            <span>{resp}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Tech Stack */}
                    <div>
                      <h4 className="text-azure font-bold text-sm uppercase tracking-wider mb-3">
                        TECH STACK
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {job.technologies.map((tech, idx) => (
                          <span
                            key={idx}
                            className="px-3 py-2 bg-dark border border-azure/30 text-azure text-sm font-mono"
                          >
                            {tech}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </motion.div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
