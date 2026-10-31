"use client";

import { motion, useScroll, useTransform } from "framer-motion";
import { useRef } from "react";
import { Award } from "lucide-react";
import { skills, certifications } from "@/data/resume";

function SkillCard({
  skill,
  scrollProgress,
  startProgress,
  endProgress
}: {
  skill: string;
  scrollProgress: any;
  startProgress: number;
  endProgress: number;
}) {
  const cardX = useTransform(
    scrollProgress,
    [startProgress, endProgress],
    [300, 0]
  );

  const cardOpacity = useTransform(
    scrollProgress,
    [startProgress, endProgress],
    [0, 1]
  );

  return (
    <motion.div
      style={{ x: cardX, opacity: cardOpacity }}
      className="relative border-2 border-slate-400/30 bg-navy-950 p-4 text-center group cursor-default overflow-hidden"
    >
      <div
        className="absolute inset-0 bg-slate-50 scale-0 group-hover:scale-150 transition-transform duration-500 ease-out"
        style={{ transformOrigin: "0% 100%" }}
      />
      <span className="relative z-10 text-slate-300 group-hover:text-dark font-semibold text-sm transition-colors duration-300">
        {skill}
      </span>
    </motion.div>
  );
}

function CategorySkills({
  category,
  skillList,
  scrollProgress,
  cardOffset,
  totalCards,
  categoryIndex
}: {
  category: string;
  skillList: string[];
  scrollProgress: any;
  cardOffset: number;
  totalCards: number;
  categoryIndex: number;
}) {
  // Animate category title based on first card in category
  const titleStartProgress = 0.15 + (cardOffset / totalCards) * 0.5;
  const titleEndProgress = 0.15 + ((cardOffset + 2) / totalCards) * 0.5;

  const titleY = useTransform(
    scrollProgress,
    [titleStartProgress, titleEndProgress],
    [30, 0]
  );

  const titleOpacity = useTransform(
    scrollProgress,
    [titleStartProgress, titleEndProgress],
    [0, 1]
  );

  return (
    <div>
      <motion.h3
        style={{ y: titleY, opacity: titleOpacity }}
        className="text-2xl md:text-3xl font-black text-slate-50 uppercase mb-6 flex items-center gap-4"
      >
        <span className="text-electric">///</span>
        {category}
      </motion.h3>

      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
        {skillList.map((skill, idx) => {
          const cardIndex = cardOffset + idx;
          const startProgress = 0.2 + (cardIndex / totalCards) * 0.5;
          const endProgress = 0.2 + ((cardIndex + 1) / totalCards) * 0.5;

          return (
            <SkillCard
              key={skill}
              skill={skill}
              scrollProgress={scrollProgress}
              startProgress={startProgress}
              endProgress={endProgress}
            />
          );
        })}
      </div>
    </div>
  );
}

export default function Skills() {
  const ref = useRef(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "end start"]
  });

  const categories = Object.entries(skills.categories);

  // Calculate total cards across all categories
  const totalCards = categories.reduce((sum, [_, list]) => sum + list.length, 0);

  return (
    <section
      id="skills"
      ref={ref}
      className="py-32 bg-dark relative overflow-hidden"
    >
      <div className="absolute top-1/2 right-1/4 w-96 h-96 bg-azure/5 blur-3xl" />

      <div className="max-w-7xl mx-auto px-6 lg:px-8 relative z-10">
        <div className="mb-16">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-16 h-1 bg-electric" />
            <span className="text-electric font-mono text-sm uppercase tracking-widest">
              // TECHNICAL ARSENAL
            </span>
          </div>
          <h2 className="text-6xl md:text-7xl lg:text-8xl font-black text-slate-50 tracking-tighter">
            SKILLS
          </h2>
        </div>

        <div className="space-y-12">
          {categories.map(([category, skillList], catIdx) => {
            // Calculate the offset (how many cards came before this category)
            let cardOffset = 0;
            for (let i = 0; i < catIdx; i++) {
              cardOffset += categories[i][1].length;
            }

            return (
              <CategorySkills
                key={category}
                category={category}
                skillList={skillList}
                scrollProgress={scrollYProgress}
                cardOffset={cardOffset}
                totalCards={totalCards}
                categoryIndex={catIdx}
              />
            );
          })}
        </div>

        <div className="mt-20">
          <h3 className="text-2xl md:text-3xl font-black text-slate-50 uppercase mb-6 flex items-center gap-4">
            <span className="text-azure">///</span>
            CERTIFICATIONS
          </h3>

          <div className="grid md:grid-cols-2 gap-6">
            {certifications.map((cert) => (
              <div
                key={cert.name}
                className="border-2 border-azure/30 bg-navy-950 p-6 hover:border-azure hover:bg-navy-900 transition-all"
              >
                <div className="flex items-start gap-4">
                  <div className="p-3 bg-azure/10">
                    <Award className="text-azure" size={28} />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-black text-lg text-slate-50 mb-1 uppercase">
                      {cert.name}
                    </h4>
                    <p className="text-slate-400 text-sm mb-1">{cert.issuer}</p>
                    <p className="text-azure text-xs font-mono">{cert.date}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-12 border-l-4 border-navy-700 pl-6 py-4">
          <p className="text-slate-400 font-mono text-sm">
            <span className="text-navy-700 font-bold">NOTE:</span> All skills listed represent
            hands-on production experience and active project work. Constantly learning and
            expanding the toolkit.
          </p>
        </div>
      </div>
    </section>
  );
}
