export const personalInfo = {
  name: "Christopher Kearl",
  email: "ctrkearl@gmail.com",
  phone: "(801) 809-1905",
  location: "Provo, UT",
  website: "ckearl.com",
  linkedin: "https://linkedin.com/in/christopher-kearl",
  github: "https://github.com/ckearl",
  tagline: "Software Engineer | MS Graduate | Musician",
  bio: "Software Engineer with an MS in Information Systems Management from BYU's Marriott School of Business, specializing in full-stack development, cloud engineering, and compliance automation. Former guitarist/pianist of Ritt Momney with millions of streams across platforms. Fluent in Korean. Passionate about building developer tools, automation systems, and creative solutions at the intersection of engineering and design.",
};

export const education = {
  degree: "Master of Science, Information Systems Management",
  school: "Brigham Young University - Marriott School of Business",
  location: "Provo, UT",
  duration: "Aug 2023 – Apr 2025 (Graduated)",
  gpa: "3.89 / 4.00 (Program), 3.67 / 4.00 (Overall)",
  activities: [
    "Co-President, Association for Information Systems",
    "Research Assistant, AI Modeling and API infrastructure",
  ],
  coursework: [
    "Enterprise Programming (JS/TS, React, React Native, Swift, Python, C#)",
    "Machine Learning",
    "Cloud Platform Engineering",
    "Managing Tech Startups",
    "Networking Systems",
    "Offensive/Defensive Cybersecurity",
  ],
};

export const experience = [
	{
		id: "marriott-engineer",
		title: "Compliance Automation Software Engineer",
		company: "Marriott International",
		location: "Bethesda, MD (Remote)",
		duration: "Aug 2024 – Present",
		type: "Full-time",
		description:
			"Engineering organization-wide compliance and security automation systems as sole software engineer, serving 30+ internal development teams across multi-cloud infrastructure.",
		responsibilities: [
			"Engineer organization-wide Compliance-ARC API as sole software engineer, providing security/compliance data, cloud service metadata, and vulnerability tracking across multi-cloud infrastructure to 30+ internal development teams",
			"Develop Python automation scripts for security remediation at scale, including the patching of 2,300+ EC2 instances with conditional security group updates based on tags, IP ranges, and ownership criteria",
		],
		technologies: [
			"Python",
			"FastAPI",
			"TypeScript",
			"React",
			"Next.js",
			"TailwindCSS",
			"AWS",
			"Docker",
			"Harness",
			"Terraform",
		],
	},
	{
		id: "marriott-fellow",
		title: "Graduate Student Fellow",
		company: "Marriott International",
		location: "Bethesda, MD",
		duration: "Jun – Aug 2024",
		type: "Internship",
		description:
			"Developed compliance dashboards and provided critical support during major infrastructure incidents.",
		responsibilities: [
			"Engineered React dashboard cataloging deployment requirements and L2 controls across AWS, Azure, Oracle, and Alibaba, standardizing NIST compliance documentation and reducing audit preparation time",
			"Restored 20 properties and 39 remote servers within 72 hours during international CrowdStrike outage, enabling transaction and reservation processing for 35,000+ guests",
		],
		technologies: [
			"React",
			"TypeScript",
			"AWS",
			"Azure",
			"Oracle Cloud",
			"Alibaba Cloud",
		],
	},
	{
		id: "byu-professor",
		title: "Adjunct Professor (IS 120)",
		company: "Brigham Young University",
		location: "Provo, UT",
		duration: "Dec 2023 – May 2025",
		type: "Part-time",
		description:
			"Restructured entire web development curriculum and taught 60+ students modern industry practices.",
		responsibilities: [
			"Restructured entire curriculum from scratch, creating course materials (lectures, assignments, and exams) aligned with current industry standards including mobile responsivity, ES6 JavaScript, and REST APIs",
			"Taught 60+ students with live coding demonstrations, achieving 84% satisfaction (5 points above department average)",
		],
		technologies: [
			"HTML5",
			"CSS",
			"TailwindCSS",
			"JavaScript",
			"REST API",
			"Git",
			"AWS API Gateway",
			"GitHub Classroom",
		],
	},
	{
		id: "pattern-intern",
		title: "Data Software Engineer Intern",
		company: "Pattern",
		location: "Lehi, UT",
		duration: "May 2023 – Aug 2023",
		type: "Internship",
		description:
			"Optimized e-commerce analytics systems and improved advertising ROI tracking.",
		responsibilities: [
			"Developed dynamic search keyword filters to categorize keywords by tracking period, resulting in an aggregate average of $0.50 in savings per advertisement space bid for partners while improving internal ROI analysis",
			"Reduced Amazon ad metrics dashboard load times by ~3 seconds by optimizing SQL generation and access controls",
		],
		technologies: [
			"Ruby",
			"Rails",
			"TypeScript",
			"MySQL",
			"Snowflake",
			"React",
			"Airflow",
			"Airbrake",
			"AWS S3",
			"Postman",
		],
	},
	{
		id: "contour-dev",
		title: "Software Developer",
		company: "Contour Software Developments",
		location: "Mesa, AZ (Remote)",
		duration: "Aug 2021 – Aug 2022",
		type: "Full-time",
		description:
			"Built field operations management platform and delivered workflow automation features.",
		responsibilities: [
			"Engineered AWS-hosted web application that replaced 40-page paper packets for field teams, saving 15-30 minutes per job across 20+ weekly operations while eliminating manual data entry times and risk of data loss",
			"Presented bimonthly demos to client executives, gathering requirements and delivering workflow automation features",
		],
		technologies: [
			"HTML",
			"CSS",
			"REST API",
			"JSON/XML",
			"JavaScript",
			"Bubble.io",
			"AWS S3",
		],
	},
];

export const skills = {
  proficient: [
    "TypeScript",
    "React",
    "Python",
    "TailwindCSS",
    "AWS",
    "Swift",
    "SwiftUI",
    "Scrum",
    "Git",
    "JavaScript",
    "MySQL",
    "Node.js",
  ],
  experienced: [
    "Rust",
    "Go",
    "R",
    "Ruby",
    "Rails",
    "Figma",
    "MongoDB",
    "Django",
    "FastAPI",
    "C#",
    "ASP.NET",
    "C++",
    "Tableau",
  ],
  categories: {
    "Languages": ["TypeScript", "Python", "JavaScript", "R", "Go", "Swift", "Ruby", "Rust", "C#", "C++", "SQL"],
    "Frontend": ["React", "Next.js", "TailwindCSS", "Framer Motion", "SwiftUI"],
    "Backend": [
      "Node.js",
      "FastAPI",
      "Django",
      "Rails",
      "Express",
      "ASP.NET",
      "GraphQL",
    ],
    "Cloud & DevOps": [
      "AWS",
      "Docker",
      "Terraform",
      "Harness",
      "Kubernetes",
      "Azure",
      "GCP",
      "GitHub Actions",
    ],
    "Databases": ["MySQL", "PostgreSQL", "MongoDB", "Snowflake", "Supabase", "Firebase"],
    "Tools": [ "Vim", "Git", "Figma", "Postman", "JIRA", "Airflow", "VS Code"],
  },
};

export const certifications = [
  {
    name: "AWS Certified Cloud Practitioner (CCP)",
    issuer: "Amazon Web Services",
    date: "May 2024",
    logo: "/certifications/aws.svg",
  },
  {
    name: "Professional Scrum Master I (PSM I)",
    issuer: "Scrum.org",
    date: "Oct 2023",
    logo: "/certifications/scrum.svg",
  },
];

export const achievements = [
  {
    title: "Korean Language Fluency",
    description:
      "Fluent speaker through 2 years of service in Busan, South Korea",
    icon: "globe",
  },
  {
    title: "Eagle Scout",
    description:
      "Collected and donated toys to Primary Children's Hospital for Eagle Scout project",
    icon: "award",
  },
  {
    title: "Music",
    description: "Avid guitarist and pianist. I collect vinyl records and concert stubs. Played guitar and piano in the indie band Ritt Momney way back when",
    icon: "music",
  },
];

export const service = {
  title: "Volunteer Representative",
  organization: "The Church of Jesus Christ of Latter-day Saints",
  location: "Busan, South Korea",
  duration: "Jun 2018 – Mar 2020",
  responsibilities: [
    "Trained 120 other volunteers of mixed ethnicities regarding rules and practices of Busan and its surrounding area",
    "Performed weekly community service activities including teaching English and cleaning Elderly nursing homes",
  ],
};
