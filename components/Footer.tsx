"use client";

import { motion } from "framer-motion";
import { Github, Linkedin, Mail, ArrowUp } from "lucide-react";
import { personalInfo } from "@/data/resume";

export default function Footer() {
  const currentYear = new Date().getFullYear();

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <footer className="bg-dark border-t-2 border-electric/20 py-16">
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        <div className="grid md:grid-cols-3 gap-12 mb-12">
          {/* Brand */}
          <div>
            <h3 className="text-3xl font-black text-slate-50 mb-4 tracking-tighter">
              <span className="text-electric">C</span>K
            </h3>
            <p className="text-slate-400 leading-relaxed mb-6">
              Software Engineer crafting elegant solutions at the intersection of technology and
              design.
            </p>
            <div className="flex gap-4">
              {[
                { icon: Github, href: personalInfo.github, color: "electric" },
                { icon: Linkedin, href: personalInfo.linkedin, color: "azure" },
                { icon: Mail, href: `mailto:${personalInfo.email}`, color: "navy-700" },
              ].map((social, idx) => (
                <motion.a
                  key={idx}
                  href={social.href}
                  target={social.icon !== Mail ? "_blank" : undefined}
                  rel={social.icon !== Mail ? "noopener noreferrer" : undefined}
                  className={`p-3 border-2 border-${social.color}/30 text-${social.color} hover:bg-${social.color}/10 hover:border-${social.color} transition-all`}
                  whileHover={{ scale: 1.1, y: -3 }}
                >
                  <social.icon size={20} />
                </motion.a>
              ))}
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-sm font-black text-slate-50 uppercase tracking-wider mb-4">
              QUICK LINKS
            </h4>
            <ul className="space-y-2">
              {[
                { name: "ABOUT", href: "#about" },
                { name: "WORK", href: "#experience" },
                { name: "PROJECTS", href: "#projects" },
                { name: "SKILLS", href: "#skills" },
                { name: "CONTACT", href: "#contact" },
              ].map((item) => (
                <li key={item.name}>
                  <a
                    href={item.href}
                    className="text-slate-400 hover:text-electric transition-colors text-sm font-mono"
                  >
                    // {item.name}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Info */}
          <div>
            <h4 className="text-sm font-black text-slate-50 uppercase tracking-wider mb-4">
              CONTACT INFO
            </h4>
            <ul className="space-y-3 text-sm">
              <li>
                <span className="text-slate-500 font-mono">EMAIL:</span>
                <br />
                <a
                  href={`mailto:${personalInfo.email}`}
                  className="text-slate-300 hover:text-electric transition-colors"
                >
                  {personalInfo.email}
                </a>
              </li>
              <li>
                <span className="text-slate-500 font-mono">PHONE:</span>
                <br />
                <a
                  href={`tel:${personalInfo.phone}`}
                  className="text-slate-300 hover:text-azure transition-colors"
                >
                  {personalInfo.phone}
                </a>
              </li>
              <li>
                <span className="text-slate-500 font-mono">LOCATION:</span>
                <br />
                <span className="text-slate-300">{personalInfo.location}</span>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-8 border-t border-slate-400/20 flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="text-sm text-slate-500 font-mono text-center md:text-left">
            <span className="text-electric">©</span> {currentYear} {personalInfo.name} • Built with{" "}
            <span className="text-navy-700">Next.js</span> &{" "}
            <span className="text-azure">TypeScript</span>
          </div>

          <button
            onClick={scrollToTop}
            className="group border-2 border-electric/30 p-3 hover:border-electric hover:bg-electric/10 transition-all"
          >
            <ArrowUp className="text-electric group-hover:scale-110 transition-transform" size={20} />
          </button>
        </div>
      </div>
    </footer>
  );
}
