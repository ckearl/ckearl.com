"use client";

import { motion, useInView } from "framer-motion";
import { useRef, useState } from "react";
import { ExternalLink, Github, ArrowUpRight } from "lucide-react";
import { projects, projectCategories } from "@/data/projects";

export default function Projects() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-300px" });
  const [selectedCategory, setSelectedCategory] = useState("All");

  const filteredProjects =
    selectedCategory === "All"
      ? projects
      : projects.filter((project) => project.category === selectedCategory);

  return (
    <section
      id="projects"
      ref={ref}
      className="py-32 bg-dark relative overflow-hidden"
    >
      {/* Geometric shapes */}
      <div className="absolute top-0 left-1/4 w-72 h-72 bg-azure/5 blur-3xl" />

      <div className="max-w-7xl mx-auto px-6 lg:px-8 relative z-10">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
          className="mb-16"
        >
          <div className="flex items-center gap-4 mb-6">
            <div className="w-16 h-1 bg-azure" />
            <span className="text-azure font-mono text-sm uppercase tracking-widest">
              // WORK SHOWCASE
            </span>
          </div>
          <h2 className="text-6xl md:text-7xl lg:text-8xl font-black text-slate-50 tracking-tighter mb-8">
            PROJECTS
          </h2>

          {/* Category Filter */}
          <div className="flex flex-wrap gap-3">
            {projectCategories.map((category) => (
              <button
                key={category}
                onClick={() => setSelectedCategory(category)}
                className={`px-6 py-3 font-bold text-sm uppercase tracking-wider transition-all border-2 ${
                  selectedCategory === category
                    ? "bg-electric text-dark border-electric"
                    : "bg-transparent text-slate-400 border-slate-400/30 hover:border-electric hover:text-electric"
                }`}
              >
                {category}
              </button>
            ))}
          </div>
        </motion.div>

        {/* Projects Grid */}
        <div className="grid md:grid-cols-2 gap-8">
          {filteredProjects.map((project, idx) => (
            <motion.div
              key={project.id}
              initial={{ opacity: 0, y: 80 }}
              animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 80 }}
              transition={{ delay: idx * 0.2, duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
              whileHover={{ y: -8, transition: { duration: 0.3 } }}
              className="group bg-navy-950 border-2 border-slate-400/20 hover:border-electric overflow-hidden transition-colors"
            >
              {/* Image Placeholder */}
              <div className="relative aspect-video bg-gradient-to-br from-navy-900 to-dark overflow-hidden">
                <div className="absolute inset-0 flex flex-col items-center justify-center p-8 text-center">
                  <div className="w-20 h-20 border-4 border-electric/30 mb-6 flex items-center justify-center">
                    <ArrowUpRight className="text-electric" size={32} />
                  </div>
                  <p className="text-slate-400 font-mono text-sm uppercase tracking-wider">
                    Project Screenshot
                  </p>
                  <p className="text-slate-500 text-xs mt-2">{project.title}</p>
                </div>

                {/* Category badge */}
                <div className="absolute top-4 right-4 bg-navy-700 px-4 py-2 text-dark font-bold text-xs uppercase tracking-wider">
                  {project.category}
                </div>

                {/* Hover overlay with links */}
                <motion.div
                  initial={{ opacity: 0 }}
                  whileHover={{ opacity: 1 }}
                  className="absolute inset-0 bg-dark/90 flex items-center justify-center gap-4"
                >
                  {project.github && (
                    <a
                      href={project.github}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="p-4 border-2 border-electric text-electric hover:bg-electric hover:text-dark transition-all"
                    >
                      <Github size={24} />
                    </a>
                  )}
                  {project.demo && (
                    <a
                      href={project.demo}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="p-4 border-2 border-azure text-azure hover:bg-azure hover:text-dark transition-all"
                    >
                      <ExternalLink size={24} />
                    </a>
                  )}
                </motion.div>
              </div>

              {/* Project Info */}
              <div className="p-8">
                <div className="flex items-start justify-between mb-4">
                  <h3 className="text-3xl font-black text-slate-50 uppercase tracking-tight">
                    {project.title}
                  </h3>
                  <span className="text-electric font-mono text-sm">{project.year}</span>
                </div>

                <p className="text-slate-300 mb-6 leading-relaxed">
                  {project.description}
                </p>

                {/* Tech Stack */}
                <div className="flex flex-wrap gap-2 mb-4">
                  {project.technologies.slice(0, 5).map((tech, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1 bg-navy-900 text-electric text-xs font-mono border border-electric/30"
                    >
                      {tech}
                    </span>
                  ))}
                  {project.technologies.length > 5 && (
                    <span className="px-3 py-1 bg-navy-900 text-slate-400 text-xs font-mono border border-slate-400/30">
                      +{project.technologies.length - 5}
                    </span>
                  )}
                </div>

                {/* Meta */}
                <div className="pt-4 border-t border-slate-400/20 flex items-center justify-between text-sm">
                  <span className="text-slate-500 font-mono">{project.team} • {project.role}</span>
                  <div className="flex gap-3">
                    {project.github && (
                      <a
                        href={project.github}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-slate-500 hover:text-electric transition-colors"
                      >
                        <Github size={18} />
                      </a>
                    )}
                    {project.demo && (
                      <a
                        href={project.demo}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-slate-500 hover:text-azure transition-colors"
                      >
                        <ExternalLink size={18} />
                      </a>
                    )}
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* GitHub CTA */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={isInView ? { opacity: 1 } : { opacity: 0 }}
          transition={{ delay: 0.6 }}
          className="mt-16 text-center"
        >
          <a
            href="https://github.com/ckearl"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-3 px-8 py-4 border-2 border-slate-50 text-slate-50 font-bold text-lg uppercase tracking-wider hover:bg-slate-50 hover:text-dark transition-all group"
          >
            <Github size={24} />
            VIEW ALL ON GITHUB
            <ArrowUpRight className="group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform" size={20} />
          </a>
        </motion.div>
      </div>
    </section>
  );
}
