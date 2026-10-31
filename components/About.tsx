"use client";

import { motion, useInView } from "framer-motion";
import { useRef } from "react";
import { Music, Globe, Award, Code2 } from "lucide-react";
import { personalInfo, education, achievements } from "@/data/resume";

const fadeInUp = {
  hidden: { opacity: 0, y: 60 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.8, ease: [0.22, 1, 0.36, 1] }
  },
};

export default function About() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-300px" });

  return (
    <section
      id="about"
      ref={ref}
      className="py-32 bg-navy-950 relative overflow-hidden"
    >
      {/* Geometric background */}
      <div className="absolute top-20 right-0 w-96 h-96 bg-navy-700/5 blur-3xl" />
      <div className="absolute bottom-20 left-0 w-96 h-96 bg-electric/5 blur-3xl" />

      <div className="max-w-7xl mx-auto px-6 lg:px-8 relative z-10">
        {/* Section Header */}
        <motion.div
          initial="hidden"
          animate={isInView ? "visible" : "hidden"}
          variants={fadeInUp}
          className="mb-16"
        >
          <div className="flex items-center gap-4 mb-6">
            <div className="w-16 h-1 bg-electric" />
            <span className="text-electric font-mono text-sm uppercase tracking-widest">
              // WHO I AM
            </span>
          </div>
          <h2 className="text-6xl md:text-7xl lg:text-8xl font-black text-slate-50 tracking-tighter">
            ABOUT
          </h2>
        </motion.div>

        <div className="grid lg:grid-cols-2 gap-12">
          {/* Left - Bio */}
          <motion.div
            initial="hidden"
            animate={isInView ? "visible" : "hidden"}
            variants={fadeInUp}
            className="space-y-8"
          >
            <p className="text-xl md:text-2xl text-slate-200 leading-relaxed">
              {personalInfo.bio}
            </p>

            {/* Education Block - Hero card style */}
            <div className="relative border-2 border-azure/30 bg-gradient-to-br from-azure/10 to-transparent backdrop-blur-sm p-6">
              <div className="flex items-start gap-4">
                <div className="p-3 bg-azure/10">
                  <Code2 className="text-azure flex-shrink-0" size={24} />
                </div>
                <div>
                  <p className="text-azure font-mono text-xs uppercase tracking-wider mb-2">
                    // EDUCATION
                  </p>
                  <h3 className="text-xl font-bold text-slate-50 mb-2">
                    {education.degree}
                  </h3>
                  <p className="text-slate-300 font-semibold mb-1">{education.school}</p>
                  <p className="text-sm text-slate-400 mb-3">
                    {education.duration} • GPA: {education.gpa}
                  </p>
                  <div className="space-y-1">
                    {education.activities.map((activity, idx) => (
                      <p key={idx} className="text-sm text-slate-400">
                        → {activity}
                      </p>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </motion.div>

          {/* Right - Achievements Grid */}
          <motion.div
            initial="hidden"
            animate={isInView ? "visible" : "hidden"}
            variants={fadeInUp}
            className="space-y-6"
          >
            {achievements.map((achievement, idx) => {
              const icons = { music: Music, globe: Globe, award: Award };
              const Icon = icons[achievement.icon as keyof typeof icons];
              const colors = ["electric", "navy-700", "azure"];
              const color = colors[idx % 3];

              return (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, x: 50 }}
                  animate={isInView ? { opacity: 1, x: 0 } : { opacity: 0, x: 50 }}
                  transition={{ delay: idx * 0.15, duration: 0.7, ease: "easeOut" }}
                  whileHover={{ scale: 1.02, y: -5 }}
                  className={`border-2 border-${color} bg-navy-900/30 p-6 hover:bg-navy-900/60 transition-colors group cursor-default`}
                >
                  <div className="flex items-start gap-4">
                    <div className={`p-3 bg-${color}/10 group-hover:bg-${color}/20 transition-colors`}>
                      <Icon className={`text-${color}`} size={28} />
                    </div>
                    <div>
                      <h4 className="text-lg font-bold text-slate-50 mb-2 uppercase tracking-wide">
                        {achievement.title}
                      </h4>
                      <p className="text-slate-300">{achievement.description}</p>
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </motion.div>
        </div>

        {/* Bottom Stats Bar */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
          transition={{ delay: 0.6 }}
          className="mt-20 grid grid-cols-2 md:grid-cols-4 gap-6"
        >
          {[
            { label: "YEARS CODING", value: "5+" },
            { label: "PROJECTS BUILT", value: "20+" },
            { label: "TECH STACKS", value: "15+" },
            { label: "AMAZING PEOPLE MET", value: "∞" },
          ].map((stat, idx) => (
            <div
              key={idx}
              className="text-center border border-slate-400/20 bg-dark/50 p-6"
            >
              <div className="text-4xl font-black text-electric mb-2">{stat.value}</div>
              <div className="text-xs text-slate-400 font-mono uppercase tracking-widest">
                {stat.label}
              </div>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
