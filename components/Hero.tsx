"use client";

import { motion, useScroll, useTransform, MotionValue } from "framer-motion";
import { useEffect, useState, useRef } from "react";
import { ArrowRight, Github, Linkedin, Mail } from "lucide-react";
import { personalInfo } from "@/data/resume";

const typewriterPhrases = [
  "I build developer tools that developers love.",
  "I automate compliance at scale.",
  "I craft beautiful web experiences.",
  "I speak fluent Korean. 안녕하세요!",
  "I made music with millions of streams.",
];

function NameTransform({
  scrollY,
  nameRotate,
  nameScale,
  slashOpacity,
  textProgress
}: {
  scrollY: any;
  nameRotate: any;
  nameScale: any;
  slashOpacity: any;
  textProgress: any;
}) {
  const [displayText, setDisplayText] = useState("CHRISTOPHER KEARL");
  const [isFixed, setIsFixed] = useState(false);
  const [initialPosition, setInitialPosition] = useState({ top: 0, left: 0 });
  const [hasCapturedPosition, setHasCapturedPosition] = useState(false);
  const nameRef = useRef<HTMLDivElement>(null);

  // Capture position when becoming fixed and switch to fixed positioning
  useEffect(() => {
    const checkPosition = () => {
      if (!nameRef.current) return;

      const rect = nameRef.current.getBoundingClientRect();
      const scrollYValue = window.scrollY;

      // When the element reaches near the top of viewport
      if (!isFixed && rect.top <= 0) {
        // Only capture position the first time (or after reset)
        if (!hasCapturedPosition) {
          setInitialPosition({
            top: rect.top,
            left: rect.left
          });
          setHasCapturedPosition(true);
        }
        setIsFixed(true);
      } else if (isFixed && scrollYValue < 50) {
        // Reset when scrolling back to top - clear captured position so it re-captures fresh next time
        setIsFixed(false);
        setHasCapturedPosition(false);
        setInitialPosition({ top: 0, left: 0 });
      }
    };

    const unsubscribe = scrollY.on("change", checkPosition);
    return unsubscribe;
  }, [scrollY, isFixed, hasCapturedPosition]);

  // Update text based on scroll
  useEffect(() => {
    const unsubscribe = textProgress.on("change", (latest: number) => {
      if (latest < 0.3) {
        setDisplayText("CHRISTOPHER KEARL");
      } else if (latest < 0.6) {
        setDisplayText("C. KEARL");
      } else if (latest < 0.8) {
        setDisplayText("C.K.");
      } else {
        setDisplayText("CK");
      }
    });
    return unsubscribe;
  }, [textProgress]);

  // Create position transforms that move from captured position to bottom-left
  const targetX = 32; // 32px from left edge
  const targetY = typeof window !== 'undefined' ? window.innerHeight - 250 : 0; // Higher up to stay in view when rotated

  // Transform from initial position to target position - only applies when scrolling AFTER element becomes fixed
  // Using scrollY range [100, 1200] to match when the element becomes fixed
  const posX = useTransform(scrollY, [100, 1200], [initialPosition.left, targetX]);
  const posY = useTransform(scrollY, [100, 1200], [initialPosition.top, targetY]);

  return (
    <>
      {/* Invisible placeholder to maintain spacing when name is fixed */}
      {isFixed && (
        <div className="invisible pointer-events-none" aria-hidden="true">
          CHRISTOPHER KEARL
        </div>
      )}

      {/* The actual transforming name */}
      <motion.div
        ref={nameRef}
        style={{
          rotate: nameRotate,
          scale: nameScale,
          ...(isFixed ? {
            left: posX,
            top: posY,
          } : {})
        }}
        className={`${
          isFixed
            ? "fixed z-50"
            : "relative"
        } text-electric font-black tracking-tighter origin-bottom-left transition-none`}
      >
        <div className="flex items-center gap-3">
          <motion.div
            style={{ opacity: slashOpacity }}
            className="w-8 h-[2px] bg-electric"
          />
          <span className="whitespace-nowrap">
            {displayText}
          </span>
        </div>
      </motion.div>
    </>
  );
}

export default function Hero() {
  const [currentPhrase, setCurrentPhrase] = useState(0);
  const [currentText, setCurrentText] = useState("");
  const [isDeleting, setIsDeleting] = useState(false);
  const [isPaused, setIsPaused] = useState(false);

  // Scroll animations for name transformation
  const { scrollY } = useScroll();

  // Transform completes when About header is in middle of screen (roughly 1200px)
  // All transforms start at 100px (when element becomes fixed) and complete at 1200px
  const nameRotate = useTransform(scrollY, [100, 1200], [0, 90]);
  const nameScale = useTransform(scrollY, [100, 1200], [1, 0.25]);
  const slashOpacity = useTransform(scrollY, [600, 1200], [0, 1]);

  // Text transition progress
  const textProgress = useTransform(scrollY, [100, 1200], [0, 1]);

  useEffect(() => {
    const phrase = typewriterPhrases[currentPhrase];

    if (isPaused) {
      const pauseTimeout = setTimeout(() => {
        setIsPaused(false);
        setIsDeleting(true);
      }, 2000);
      return () => clearTimeout(pauseTimeout);
    }

    if (!isDeleting && currentText === phrase) {
      setIsPaused(true);
      return;
    }

    if (isDeleting && currentText === "") {
      setIsDeleting(false);
      setCurrentPhrase((prev) => (prev + 1) % typewriterPhrases.length);
      return;
    }

    const timeout = setTimeout(
      () => {
        setCurrentText((prev) =>
          isDeleting
            ? phrase.slice(0, prev.length - 1)
            : phrase.slice(0, prev.length + 1)
        );
      },
      isDeleting ? 30 : 60
    );

    return () => clearTimeout(timeout);
  }, [currentText, isDeleting, currentPhrase, isPaused]);

  return (
    <section
      id="hero"
      className="relative min-h-screen flex items-center justify-center overflow-hidden bg-dark"
    >
      {/* Large geometric shapes */}
      <motion.div
        className="absolute top-0 right-0 w-[800px] h-[800px] bg-electric/10 rotate-45"
        initial={{ x: 300, y: -300, rotate: 45 }}
        animate={{ x: 200, y: -200, rotate: 50 }}
        transition={{ duration: 20, repeat: Infinity, repeatType: "reverse" }}
      />

      <motion.div
        className="absolute bottom-0 left-0 w-[600px] h-[600px] bg-navy-700/5"
        initial={{ x: -200, y: 200 }}
        animate={{ x: -100, y: 100 }}
        transition={{ duration: 15, repeat: Infinity, repeatType: "reverse" }}
      />

      <motion.div
        className="absolute top-1/2 left-1/4 w-[300px] h-[300px] bg-azure/5 rounded-full blur-3xl"
        animate={{
          scale: [1, 1.3, 1],
          opacity: [0.3, 0.6, 0.3],
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
        }}
      />

      <div className="relative z-10 max-w-7xl mx-auto px-6 lg:px-8 w-full">
        <div className="grid lg:grid-cols-12 gap-8 items-center">
          {/* Left side - Main content */}
          <div className="lg:col-span-7">
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8 }}
            >
              {/* Small label */}
              <motion.div
                className="inline-block px-4 py-2 border border-electric/50 rounded-full mb-8"
                whileHover={{ borderColor: "rgba(65, 105, 225, 1)", scale: 1.05 }}
              >
                <span className="text-electric text-sm font-mono uppercase tracking-wider">
                  Open to collaborate
                </span>
              </motion.div>

              {/* Name - HUGE and bold - static with fade-in */}
              <h1 className="mb-6 relative">
                <motion.div
                  className="text-[clamp(3rem,10vw,7rem)] font-black leading-[0.9] tracking-tighter text-electric"
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2, duration: 0.6 }}
                >
                  <div className="flex flex-col">
                    <span>CHRISTOPHER</span>
                    <span>KEARL</span>
                  </div>
                  {/* Commented out scroll-based animation:
                  <NameTransform
                    scrollY={scrollY}
                    nameRotate={nameRotate}
                    nameScale={nameScale}
                    slashOpacity={slashOpacity}
                    textProgress={textProgress}
                  />
                  */}
                </motion.div>
              </h1>

              {/* Role */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.4, duration: 0.6 }}
                className="mb-8"
              >
                <p className="text-slate-200 text-2xl md:text-3xl font-light max-w-2xl">
                  Software Engineer{" "}
                  <span className="text-slate-400">×</span> Cloud Architect{" "}
                  <span className="text-slate-400">×</span> Creative
                </p>
              </motion.div>

              {/* Typewriter */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.6, duration: 0.6 }}
                className="mb-4 min-h-[60px]"
              >
                <p className="text-lg md:text-xl text-electric font-mono">
                  <span className="text-slate-500">&gt;</span> {currentText}
                  <span className="inline-block w-2 h-5 bg-electric ml-1 animate-pulse"></span>
                </p>
              </motion.div>

              {/* CTAs */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.8, duration: 0.6 }}
                className="flex flex-wrap gap-4 mb-4"
              >
                <motion.a
                  href="#projects"
                  className="group relative px-8 py-4 bg-electric text-dark rounded-none font-bold text-lg overflow-hidden"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <span className="relative z-10 flex items-center gap-2">
                    VIEW PROJECTS
                    <ArrowRight className="group-hover:translate-x-1 transition-transform" size={20} />
                  </span>
                  <motion.div
                    className="absolute inset-0 bg-azure"
                    initial={{ x: "-100%" }}
                    whileHover={{ x: 0 }}
                    transition={{ duration: 0.3 }}
                  />
                </motion.a>

                <motion.a
                  href={`mailto:${personalInfo.email}`}
                  className="px-8 py-4 border-2 border-slate-50 text-slate-50 rounded-none font-bold text-lg hover:bg-slate-50 hover:text-dark transition-all"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  GET IN TOUCH
                </motion.a>
              </motion.div>
            </motion.div>
          </div>

          {/* Right side - Visual element */}
          <div className="lg:col-span-5 relative h-[500px] hidden lg:block">
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.4, duration: 0.8 }}
              className="relative h-full"
            >
              {/* Stacked cards/blocks effect */}
              <motion.div
                className="absolute top-0 right-0 w-72 h-72 bg-gradient-to-br from-electric/20 to-transparent border border-electric/50 backdrop-blur-sm"
                animate={{ y: [0, -10, 0] }}
                transition={{ duration: 4, repeat: Infinity }}
              >
                <div className="p-6">
                  <p className="text-electric font-mono text-sm mb-2">// EXPERTISE</p>
                  <p className="text-slate-200 text-lg font-bold">Full-Stack Development</p>
                </div>
              </motion.div>

              <motion.div
                className="absolute top-24 right-16 w-72 h-72 bg-gradient-to-br from-navy-700/20 to-transparent border border-navy-700/50 backdrop-blur-sm"
                animate={{ y: [0, 10, 0] }}
                transition={{ duration: 5, repeat: Infinity }}
              >
                <div className="p-6">
                  <p className="text-navy-700 font-mono text-sm mb-2">// FOCUS</p>
                  <p className="text-slate-200 text-lg font-bold">Cloud & DevOps</p>
                </div>
              </motion.div>

              <motion.div
                className="absolute top-48 right-32 w-72 h-72 bg-gradient-to-br from-azure/20 to-transparent border border-azure/50 backdrop-blur-sm"
                animate={{ y: [0, -15, 0] }}
                transition={{ duration: 6, repeat: Infinity }}
              >
                <div className="p-6">
                  <p className="text-azure font-mono text-sm mb-2">// PASSION</p>
                  <p className="text-slate-200 text-lg font-bold">Dev Tools & Automation</p>
                </div>
              </motion.div>
            </motion.div>
          </div>
        </div>

        {/* Social bar at bottom */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1, duration: 0.6 }}
          className="bottom-12 left-6 right-6 lg:left-8 lg:right-8"
        >
          <div className="flex justify-between items-center border-t border-slate-400/20 pt-6">
            <div className="flex gap-6">
              {[
                { icon: Github, href: personalInfo.github, label: "GitHub" },
                { icon: Linkedin, href: personalInfo.linkedin, label: "LinkedIn" },
                { icon: Mail, href: `mailto:${personalInfo.email}`, label: "Email" },
              ].map((social, idx) => (
                <motion.a
                  key={idx}
                  href={social.href}
                  target={social.label !== "Email" ? "_blank" : undefined}
                  rel={social.label !== "Email" ? "noopener noreferrer" : undefined}
                  className="group flex items-center gap-2 text-slate-400 hover:text-electric transition-colors"
                  whileHover={{ x: 5 }}
                >
                  <social.icon size={20} />
                  <span className="text-sm font-mono hidden sm:block">{social.label}</span>
                </motion.a>
              ))}
            </div>
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
              className="text-slate-600 text-sm font-mono"
            >
              ⟳ SCROLL
            </motion.div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
