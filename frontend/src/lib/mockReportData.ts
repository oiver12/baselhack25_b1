import type { ReportData } from "./types";

export const mockReportData: ReportData = {
  question: "What are the main AI risks for businesses?",
  summary: "To address AI risks in business, we can enhance data quality, improve governance and compliance, and foster user adoption through education.",
  opinions: [
    "A significant group (35%) focused on data quality and governance concerns, including issues with training data, data silos, and governance gaps.",
    "Another vocal group (28%) emphasized technical and operational risks, such as model drift, security vulnerabilities, and monitoring blind spots.",
    "Regulatory and legal concerns were raised by many participants (20%), highlighting privacy risks, compliance issues, and legal exposure.",
    "Organizational and cultural challenges were identified by 17% of participants, including skill gaps, adoption hurdles, and workforce anxiety."
  ],
  messagePoints: [
    { id: '1434181807749988462', x: -0.17458857938537298, y: 0.6904559459311559, message: 'Unclear business case and ROI', user: 'Sämi', profilePicUrl: 'https://cdn.discordapp.com/embed/avatars/4.png' },
    { id: '1434182894431113227', x: 0.5900208360915571, y: -0.09939656006317549, message: 'Poor, sparse, or biased training data', user: 'Sämi', profilePicUrl: 'https://cdn.discordapp.com/embed/avatars/4.png' },
    { id: '1434182902509473943', x: 0.03923559509911314, y: 0.1165046428624596, message: 'Data silos blocking end-to-end signals', user: 'Sämi', profilePicUrl: 'https://cdn.discordapp.com/embed/avatars/4.png' },
    { id: '1434182912093458523', x: 0.862141028635115, y: -0.26233204802071136, message: 'Label noise and inconsistent ground truth', user: 'Sämi', profilePicUrl: 'https://cdn.discordapp.com/embed/avatars/4.png' },
    { id: '1434182925255053372', x: -0.9268800486854768, y: -0.38225586351189594, message: 'Privacy risks from sensitive data exposure', user: 'Sämi', profilePicUrl: 'https://cdn.discordapp.com/embed/avatars/4.png' },
    { id: '1434182935333965979', x: -0.47495929945950116, y: 0.4248068504520121, message: 'Regulatory uncertainty (sector + region specific)', user: 'Sämi', profilePicUrl: 'https://cdn.discordapp.com/embed/avatars/4.png' },
    { id: '1434182944443863224', x: -0.3197134159311516, y: -0.37690728616411234, message: 'Weak governance over models and data', user: 'Sämi', profilePicUrl: 'https://cdn.discordapp.com/embed/avatars/4.png' },
    { id: '1434182955009445999', x: -0.05451528583627554, y: 0.09065922331419317, message: 'Lack of explainability for key decisions', user: 'Sämi', profilePicUrl: 'https://cdn.discordapp.com/embed/avatars/4.png' },
    { id: '1434182963888656516', x: 0.22005213510224403, y: -0.7251063917655108, message: 'Model hallucinations undermining trust', user: 'Sämi', profilePicUrl: 'https://cdn.discordapp.com/embed/avatars/4.png' },
    { id: '1434182973103804506', x: 0.6244074845923918, y: 0.07868619181304522, message: 'Evaluation metrics misaligned with outcomes', user: 'Sämi', profilePicUrl: 'https://cdn.discordapp.com/embed/avatars/4.png' },
    { id: '1434182982989774898', x: 0.2635903432943341, y: -0.11784939739160365, message: 'Goodhart\'s law / metric gaming', user: 'Sämi', profilePicUrl: 'https://cdn.discordapp.com/embed/avatars/4.png' },
    { id: '1434182991692955813', x: 0.7409861442047108, y: -0.4891032017512651, message: 'Feedback loops amplifying existing bias', user: 'Sämi', profilePicUrl: 'https://cdn.discordapp.com/embed/avatars/4.png' },
    { id: '1434183000731422721', x: 0.4368613707902806, y: -0.9580862631487872, message: 'Model drift from changing user behavior', user: 'Sämi', profilePicUrl: 'https://cdn.discordapp.com/embed/avatars/4.png' },
    { id: '1434183009904365589', x: 0.1261247971168695, y: -0.49821111554190983, message: 'Data drift from upstream system changes', user: 'Sämi', profilePicUrl: 'https://cdn.discordapp.com/embed/avatars/4.png' },
    { id: '1434183025230348398', x: -0.10548730035693188, y: -0.13742582500133768, message: 'Fragile prompts; prompt injection attacks', user: 'Sämi', profilePicUrl: 'https://cdn.discordapp.com/embed/avatars/4.png' },
    { id: '1434183034638307479', x: -0.6438006125014969, y: -0.2988221414289096, message: 'Jailbreaks and content policy violations', user: 'Sämi', profilePicUrl: 'https://cdn.discordapp.com/embed/avatars/4.png' },
    { id: '1434183043014197439', x: 0.4096019376071252, y: -0.17353107404443507, message: 'IP leakage via training or outputs', user: 'Sämi', profilePicUrl: 'https://cdn.discordapp.com/embed/avatars/4.png' },
    { id: '1434183054837940285', x: -0.5037900421909021, y: 0.06961018193085264, message: 'Vendor lock-in and portability concerns', user: 'Sämi', profilePicUrl: 'https://cdn.discordapp.com/embed/avatars/4.png' },
    { id: '1434183075968847993', x: 0.4545578767658102, y: -0.061992890625023854, message: 'Hidden inference costs at scale', user: 'Sämi', profilePicUrl: 'https://cdn.discordapp.com/embed/avatars/4.png' },
    { id: '1434183085926387782', x: 0.16894982569442782, y: 0.6348315891535167, message: 'GPU/compute scarcity or underutilization', user: 'Sämi', profilePicUrl: 'https://cdn.discordapp.com/embed/avatars/4.png' },
    { id: '1434183095342334106', x: 0.41523185102208354, y: 0.30412319304585256, message: 'Latency too high for UX needs', user: 'Sämi', profilePicUrl: 'https://cdn.discordapp.com/embed/avatars/4.png' },
    { id: '1434183104582647879', x: 0.08426815952876711, y: 1.0, message: 'Availability/SLA gaps during peak demand', user: 'Sämi', profilePicUrl: 'https://cdn.discordapp.com/embed/avatars/4.png' },
    { id: '1434183138862563551', x: 0.32248152561385124, y: 0.2184551798945979, message: 'Monitoring blind spots in production', user: 'Sämi', profilePicUrl: 'https://cdn.discordapp.com/embed/avatars/4.png' },
    { id: '1434183147569942621', x: 0.06255914290080161, y: -0.37974203125472, message: 'Reproducibility issues across versions', user: 'Sämi', profilePicUrl: 'https://cdn.discordapp.com/embed/avatars/4.png' },
    { id: '1434183157154058392', x: 0.18604931388361584, y: -0.15664845174413292, message: 'Dependency churn in AI libraries', user: 'Sämi', profilePicUrl: 'https://cdn.discordapp.com/embed/avatars/4.png' },
    { id: '1434183166427533384', x: -0.41821522826794433, y: -0.6045615660799868, message: 'Security of model weights and endpoints', user: 'Sämi', profilePicUrl: 'https://cdn.discordapp.com/embed/avatars/4.png' },
    { id: '1434183175151816794', x: -0.587299173427999, y: -0.2926965219585836, message: 'Secret/API key management hygiene', user: 'Sämi', profilePicUrl: 'https://cdn.discordapp.com/embed/avatars/4.png' },
    { id: '1434183191995875592', x: -0.2004906153923567, y: 0.11142849563802253, message: 'Shadow AI tools bypassing IT controls', user: 'Sämi', profilePicUrl: 'https://cdn.discordapp.com/embed/avatars/4.png' },
    { id: '1434183201173147753', x: -0.2362894760974144, y: -0.08758379953631679, message: 'Change-management and user adoption hurdles', user: 'Sämi', profilePicUrl: 'https://cdn.discordapp.com/embed/avatars/4.png' },
    { id: '1434183211612766301', x: -0.10281315462357744, y: 0.14236994823922064, message: 'Workforce anxiety and resistance to AI', user: 'Sämi', profilePicUrl: 'https://cdn.discordapp.com/embed/avatars/4.png' },
    { id: '1434183222157246545', x: 0.5058767132504757, y: 0.3677746550557256, message: 'Skill gaps: ML, MLOps, prompt design', user: 'Sämi', profilePicUrl: 'https://cdn.discordapp.com/embed/avatars/4.png' },
    { id: '1434183230373761197', x: 0.19555479773081386, y: 0.5048712336010615, message: 'Inadequate human-in-the-loop processes', user: 'Sämi', profilePicUrl: 'https://cdn.discordapp.com/embed/avatars/4.png' },
    { id: '1434183238942724126', x: -0.18505671456997752, y: 0.06049151207621329, message: 'Ambiguous ownership: who fixes failures?', user: 'Sämi', profilePicUrl: 'https://cdn.discordapp.com/embed/avatars/4.png' },
    { id: '1434183247771861115', x: 0.25049437845392314, y: 0.4212757150562198, message: 'Fragmented MLOps/tooling across teams', user: 'Sämi', profilePicUrl: 'https://cdn.discordapp.com/embed/avatars/4.png' },
    { id: '1434183260782592030', x: -0.9178111815822789, y: 0.08687949144518041, message: 'Data residency and cross-border transfers', user: 'Sämi', profilePicUrl: 'https://cdn.discordapp.com/embed/avatars/4.png' },
    { id: '1434183268839850036', x: -0.41951134416189745, y: 0.04938868446269914, message: 'Legal exposure from automated decisions', user: 'Sämi', profilePicUrl: 'https://cdn.discordapp.com/embed/avatars/4.png' },
    { id: '1434183278344011777', x: -0.41384976468849327, y: -0.015263661722323315, message: 'Documentation debt (prompts, data lineage)', user: 'Sämi', profilePicUrl: 'https://cdn.discordapp.com/embed/avatars/4.png' },
    { id: '1434183291254214728', x: 0.26580833766545836, y: 0.07090750271519591, message: 'Testing edge cases and long-tail inputs', user: 'Sämi', profilePicUrl: 'https://cdn.discordapp.com/embed/avatars/4.png' },
    { id: '1434183338104721499', x: 0.3197537515791592, y: 0.13885813477028316, message: 'Multilingual/localization quality variance', user: 'Sämi', profilePicUrl: 'https://cdn.discordapp.com/embed/avatars/4.png' },
    { id: '1434183349265633311', x: 0.015983706588643797, y: 0.4684440101198517, message: 'Accessibility and inclusive design gaps', user: 'Sämi', profilePicUrl: 'https://cdn.discordapp.com/embed/avatars/4.png' },
    { id: '1434183358031855716', x: -0.5658497148849381, y: -0.28148494875313995, message: 'Content moderation and brand-safety risks', user: 'Sämi', profilePicUrl: 'https://cdn.discordapp.com/embed/avatars/4.png' },
    { id: '1434183368978731081', x: 0.08530450664700134, y: 0.13839435585496154, message: 'Environmental/energy cost of large models', user: 'Sämi', profilePicUrl: 'https://cdn.discordapp.com/embed/avatars/4.png' },
    { id: '1434183378537545828', x: -0.6937374862912606, y: 0.6778341762552444, message: 'Procurement friction (security, legal reviews)', user: 'Sämi', profilePicUrl: 'https://cdn.discordapp.com/embed/avatars/4.png' },
    { id: '1434183387899367474', x: 0.4136184107876327, y: -0.16614713413602097, message: 'Weak A/B testing and experimentation cadence', user: 'Sämi', profilePicUrl: 'https://cdn.discordapp.com/embed/avatars/4.png' },
    { id: '1434183400079757454', x: 0.6684225681554056, y: -0.26236846725588925, message: 'Misfit between open vs closed models', user: 'Sämi', profilePicUrl: 'https://cdn.discordapp.com/embed/avatars/4.png' },
    { id: '1434183408413577226', x: -0.730039364388813, y: -0.5460639268024661, message: 'Fine-tuning data ownership and consent', user: 'Sämi', profilePicUrl: 'https://cdn.discordapp.com/embed/avatars/4.png' },
    { id: '1434183416735072388', x: 0.033707548762537606, y: 0.5284495870206943, message: 'Misaligned incentives with implementation partners', user: 'Sämi', profilePicUrl: 'https://cdn.discordapp.com/embed/avatars/4.png' },
    { id: '1434183425312559296', x: -0.10143488416895259, y: -0.6294681107918544, message: 'Over-personalization creeping users out', user: 'Sämi', profilePicUrl: 'https://cdn.discordapp.com/embed/avatars/4.png' },
    { id: '1434183436540842169', x: 0.018002763774674736, y: 0.511125749384611, message: 'Inadequate incident response + red teaming', user: 'Sämi', profilePicUrl: 'https://cdn.discordapp.com/embed/avatars/4.png' },
    { id: '1434183453288431658', x: -0.003514164445811733, y: 0.09642242840124113, message: 'Treating AI as a project, not a product', user: 'Sämi', profilePicUrl: 'https://cdn.discordapp.com/embed/avatars/4.png' }
  ],
  solutions: [
    {
      id: "solution-1",
      title: "Enhance Data Quality",
      description: "Improve data governance, reduce bias, and ensure consistent quality across all AI models",
      pros: [
        "Improves model accuracy",
        "Reduces bias in outcomes"
      ],
      cons: [
        "Can be resource-intensive",
        "Requires ongoing maintenance"
      ],
      approvalPercentage: 70
    },
    {
      id: "solution-2",
      title: "Improve Governance and Compliance",
      description: "Establish clear governance frameworks and ensure compliance with regulations",
      pros: [
        "Mitigates legal risks",
        "Ensures ethical AI use"
      ],
      cons: [
        "May slow down innovation",
        "Can be complex to implement"
      ],
      approvalPercentage: 80
    },
    {
      id: "solution-3",
      title: "Foster User Adoption through Education",
      description: "Educate workforce and reduce resistance through targeted training and communication",
      pros: [
        "Reduces workforce anxiety",
        "Encourages proactive engagement with AI"
      ],
      cons: [
        "Requires time and investment",
        "Varied acceptance levels among employees"
      ],
      approvalPercentage: 60
    }
  ]
};
