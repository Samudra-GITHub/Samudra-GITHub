<div align="center">

<picture><source media="(prefers-color-scheme: dark)" srcset="./assets/readme/dark/hero.svg"><img src="./assets/readme/light/hero.svg" width="100%" alt="SAMUDRA KAR. Computer Science engineering student building across systems, AI and product, from first principles. A turning wireframe Earth with a moon and a satellite in orbit."></picture>

<sub><a href="#flagship">Flagship</a> &nbsp;·&nbsp; <a href="#samagra">Samagra OS</a> &nbsp;·&nbsp; <a href="#projects">All projects</a> &nbsp;·&nbsp; <a href="#engineering-with-ai">Engineering with AI</a> &nbsp;·&nbsp; <a href="#stack">Stack</a> &nbsp;·&nbsp; <a href="#contact">Contact</a></sub>

</div>

<br>

<a id="flagship"></a>

<picture><source media="(prefers-color-scheme: dark)" srcset="./assets/readme/dark/sec-flagship.svg"><img src="./assets/readme/light/sec-flagship.svg" width="100%" alt="01 Flagship"></picture>

<a href="https://github.com/Samudra-GITHub/W.E.D.N.E.S.D.A.Y."><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/readme/dark/wed-hero.svg"><img src="./assets/readme/light/wed-hero.svg" width="100%" alt="W.E.D.N.E.S.D.A.Y.: Watchful Earth-Data Navigator, Entirely Self-hosted Desktop Assistant for You. A personal AI assistant that runs on your own computer, with a living Earth at its centre."></picture></a>

**[W.E.D.N.E.S.D.A.Y.](https://github.com/Samudra-GITHub/W.E.D.N.E.S.D.A.Y.)** is my flagship: a desktop assistant for Windows 11 that answers with a language model running on your own machine through Ollama. It can use tools (the time, your workspace, earthquakes, weather, nearby places), but every call goes through a capability broker that denies by default, and anything with consequences waits for your approval. Around it sits a full 3D Earth of live public data, and now a Moon.

<a href="https://github.com/Samudra-GITHub/W.E.D.N.E.S.D.A.Y."><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/readme/dark/wed-moon.svg"><img src="./assets/readme/light/wed-moon.svg" width="100%" alt="Lunar Intelligence, new in W.E.D.N.E.S.D.A.Y.: an interactive 3D Moon with NASA Moon Trek LRO imagery, live JPL Horizons ephemeris for LRO, Chandrayaan-2 and Danuri, and a source-attributed NSSDCA catalogue of landing and impact sites."></picture></a>

<a href="https://github.com/Samudra-GITHub/W.E.D.N.E.S.D.A.Y."><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/readme/dark/wed-pipeline.svg"><img src="./assets/readme/light/wed-pipeline.svg" width="100%" alt="Ask the Earth: you ask, the local model picks a tool, the capability broker checks it, the tool fetches public records with source and time, and a typed request goes to the globe, which confirms it at the backend, app and globe."></picture></a>

<a href="https://github.com/Samudra-GITHub/W.E.D.N.E.S.D.A.Y."><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/readme/dark/wed-modes.svg"><img src="./assets/readme/light/wed-modes.svg" width="100%" alt="Mind: conversation, voice and approvals on a local model. World: the living Earth in Live, Time and Orbit. Pulse: significant records with source and time. Private: the core binds to 127.0.0.1."></picture></a>

- **A living Earth.** A CesiumJS globe lit by the real sun: live aircraft, about 800 tracked satellites, USGS earthquakes, NASA EONET events, GDACS alerts and more, each layer showing its source and how fresh it is.
- **Lunar Intelligence.** A 3D Moon on NASA Moon Trek LRO imagery, live JPL Horizons positions for LRO, Chandrayaan-2 and Danuri, and an NSSDCA catalogue of landing and impact sites with sources attached.
- **Ask the Earth.** Plain-language questions become typed requests the globe must confirm. The model can't send code, and records it invents are flagged.
- **Time and Orbit.** Play back up to 92 days of history or compare two periods; follow what's in orbit, including the ISS.
- **Private by design.** Local model, local speech, push-to-talk with no wake word, and a core that listens only on `127.0.0.1`.

<p>
<img src="https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.12">
<img src="https://img.shields.io/badge/FastAPI-local_core-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI">
<img src="https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black" alt="React 18">
<img src="https://img.shields.io/badge/CesiumJS-3D_Earth-6CADDF?style=flat-square&logo=cesium&logoColor=white" alt="CesiumJS">
<img src="https://img.shields.io/badge/Ollama-qwen2.5:7b-1E1E2E?style=flat-square&logo=ollama&logoColor=white" alt="Ollama qwen2.5:7b">
</p>

**[Explore the repository →](https://github.com/Samudra-GITHub/W.E.D.N.E.S.D.A.Y.)**

<br>

<a id="samagra"></a>

<picture><source media="(prefers-color-scheme: dark)" srcset="./assets/readme/dark/sec-samagra.svg"><img src="./assets/readme/light/sec-samagra.svg" width="100%" alt="02 Also building"></picture>

<a href="https://github.com/Samudra-GITHub/Samagra-OS"><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/readme/dark/samagra-os.svg"><img src="./assets/readme/light/samagra-os.svg" width="100%" alt="Samagra OS: a real x86-64 operating system built from first principles. Boot stages, physical page frames and a preemptive scheduler, animated."></picture></a>

**[Samagra OS](https://github.com/Samudra-GITHub/Samagra-OS)** is a real x86-64 operating system, built from first principles. It boots into long mode, manages physical and virtual memory, handles CPU exceptions and hardware interrupts, and runs a preemptive scheduler over kernel tasks. Early user-mode support has started: Ring 3, per-process address spaces, a small system-call interface and a non-persistent RAM filesystem. Persistent storage, networking and a native desktop are still to come.

<br>

<a id="projects"></a>

<picture><source media="(prefers-color-scheme: dark)" srcset="./assets/readme/dark/sec-projects.svg"><img src="./assets/readme/light/sec-projects.svg" width="100%" alt="03 All projects"></picture>

Every other public repository, two per row. Each card is a small animated scene of what the project does; the readings inside them are illustrative, not live data.

<table>
<tr><td width="50%" valign="top"><a href="https://github.com/Samudra-GITHub/arthayukti"><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/readme/dark/arthayukti.svg"><img src="./assets/readme/light/arthayukti.svg" width="100%" alt="ArthaYukti: animated project card"></picture></a><br><sub>Multi-goal financial planning under uncertainty: when income can't cover every goal, it shows which goal slips, by how long, and the smallest fix, and the engine re-checks every fix. An AI advisor explains the trade-offs; the engine does the arithmetic. English and हिन्दी. Built for Srujana Hackathon 2026.</sub><br><sub>FastAPI · React · TypeScript · Tailwind · Gemini &nbsp;·&nbsp; <a href="https://github.com/Samudra-GITHub/arthayukti">GitHub ↗</a> &nbsp;·&nbsp; <a href="https://arthayukti.vercel.app">Live ↗</a></sub></td><td width="50%" valign="top"><a href="https://github.com/Samudra-GITHub/PRAHARI"><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/readme/dark/prahari.svg"><img src="./assets/readme/light/prahari.svg" width="100%" alt="PRAHARI: animated project card"></picture></a><br><sub>Mine safety and compliance monitoring: explainable risk scores, a tamper-evident audit log, and a copilot limited to permission-scoped data. Built for the Smart India Hackathon.</sub><br><sub>Next.js · Prisma · PostgreSQL · Docker &nbsp;·&nbsp; <a href="https://github.com/Samudra-GITHub/PRAHARI">GitHub ↗</a></sub></td></tr>
<tr><td width="50%" valign="top"><a href="https://github.com/Samudra-GITHub/AkashaLens"><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/readme/dark/akashalens.svg"><img src="./assets/readme/light/akashalens.svg" width="100%" alt="AkashaLens: animated project card"></picture></a><br><sub>A PyTorch U-Net prototype that reconstructs cloud-covered Sentinel-2 satellite scenes. Built for ISRO Hackathon 2026, and trained on a tiny sample set.</sub><br><sub>PyTorch · scikit-image · Flask &nbsp;·&nbsp; <a href="https://github.com/Samudra-GITHub/AkashaLens">GitHub ↗</a></sub></td><td width="50%" valign="top"><a href="https://github.com/Samudra-GITHub/Tarang"><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/readme/dark/tarang.svg"><img src="./assets/readme/light/tarang.svg" width="100%" alt="Tarang: animated project card"></picture></a><br><sub>A music web app built around one persistent player that expands into a full now-playing view, with time-synced lyrics and a documented design system. Frontend only, on seed data.</sub><br><sub>Next.js · TypeScript · Framer Motion · Zustand &nbsp;·&nbsp; <a href="https://github.com/Samudra-GITHub/Tarang">GitHub ↗</a> &nbsp;·&nbsp; <a href="https://tarang-ecru.vercel.app">Live ↗</a></sub></td></tr>
<tr><td width="50%" valign="top"><a href="https://github.com/Samudra-GITHub/Rinti-Ai"><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/readme/dark/rinti-ai.svg"><img src="./assets/readme/light/rinti-ai.svg" width="100%" alt="Rinti AI: animated project card"></picture></a><br><sub>A chat workspace with per-user memory, cited multi-step research and real account sessions: Argon2 hashing, HttpOnly cookies, CSRF checks.</sub><br><sub>FastAPI · Next.js · Groq · Tavily &nbsp;·&nbsp; <a href="https://github.com/Samudra-GITHub/Rinti-Ai">GitHub ↗</a> &nbsp;·&nbsp; <a href="https://rinti-ai.vercel.app">Live ↗</a></sub></td><td width="50%" valign="top"><a href="https://github.com/Samudra-GITHub/orbit-os"><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/readme/dark/orbit-os.svg"><img src="./assets/readme/light/orbit-os.svg" width="100%" alt="orbit-os: animated project card"></picture></a><br><sub>A personal dashboard that borrows from operating-system design. An interface exploration with mock data, not a real operating system.</sub><br><sub>Next.js · TypeScript · Framer Motion &nbsp;·&nbsp; <a href="https://github.com/Samudra-GITHub/orbit-os">GitHub ↗</a></sub></td></tr>
<tr><td width="50%" valign="top"><a href="https://github.com/Samudra-GITHub/Krama"><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/readme/dark/krama.svg"><img src="./assets/readme/light/krama.svg" width="100%" alt="Krama: animated project card"></picture></a><br><sub>A luxury sneaker marketplace, told as a story.</sub><br><sub>Next.js · TypeScript · GSAP &nbsp;·&nbsp; <a href="https://github.com/Samudra-GITHub/Krama">GitHub ↗</a></sub></td><td width="50%" valign="top"><a href="https://github.com/Samudra-GITHub/Niriksh-AI"><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/readme/dark/niriksh-ai.svg"><img src="./assets/readme/light/niriksh-ai.svg" width="100%" alt="Niriksh AI: animated project card"></picture></a><br><sub>An AI operations teammate for merchants.</sub><br><sub>Next.js · TypeScript &nbsp;·&nbsp; <a href="https://github.com/Samudra-GITHub/Niriksh-AI">GitHub ↗</a></sub></td></tr>
<tr><td width="50%" valign="top"><a href="https://github.com/Samudra-GITHub/SkyCast-Weather-App"><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/readme/dark/skycast.svg"><img src="./assets/readme/light/skycast.svg" width="100%" alt="SkyCast: animated project card"></picture></a><br><sub>One screen of weather: conditions, forecast, UV and air quality for any city, over OpenWeatherMap.</sub><br><sub>Python · Flask &nbsp;·&nbsp; <a href="https://github.com/Samudra-GITHub/SkyCast-Weather-App">GitHub ↗</a></sub></td><td width="50%" valign="top"><a href="https://github.com/Samudra-GITHub/Sam-s_Portfolio"><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/readme/dark/sams-portfolio.svg"><img src="./assets/readme/light/sams-portfolio.svg" width="100%" alt="Sam's Portfolio: animated project card"></picture></a><br><sub>My current portfolio: a single-screen WebGL glass-drop homepage, an exhibition of 16 projects with interactive case-study worlds, and an optional generated soundtrack.</sub><br><sub>React 19 · Vite · GSAP · WebGL · Web Audio &nbsp;·&nbsp; <a href="https://github.com/Samudra-GITHub/Sam-s_Portfolio">GitHub ↗</a> &nbsp;·&nbsp; <a href="https://sam-sportfolio.vercel.app">Live ↗</a></sub></td></tr>
<tr><td width="50%" valign="top"><a href="https://github.com/Samudra-GITHub/samudra-kar-portfolio"><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/readme/dark/samudra-kar-portfolio.svg"><img src="./assets/readme/light/samudra-kar-portfolio.svg" width="100%" alt="samudra-kar-portfolio: animated project card"></picture></a><br><sub>An earlier interactive developer portfolio.</sub><br><sub>TypeScript &nbsp;·&nbsp; <a href="https://github.com/Samudra-GITHub/samudra-kar-portfolio">GitHub ↗</a> &nbsp;·&nbsp; <a href="https://samudra-kar-portfolio.vercel.app">Live ↗</a></sub></td><td width="50%" valign="top"><a href="https://github.com/Samudra-GITHub/noir-cafe"><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/readme/dark/noir-cafe.svg"><img src="./assets/readme/light/noir-cafe.svg" width="100%" alt="noir-cafe: animated project card"></picture></a><br><sub>A cinematic specialty-coffee site.</sub><br><sub>Next.js · TypeScript · Tailwind · Framer Motion · Lenis &nbsp;·&nbsp; <a href="https://github.com/Samudra-GITHub/noir-cafe">GitHub ↗</a></sub></td></tr>
<tr><td width="50%" valign="top"><a href="https://github.com/Samudra-GITHub/the-waffle-house"><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/readme/dark/the-waffle-house.svg"><img src="./assets/readme/light/the-waffle-house.svg" width="100%" alt="the-waffle-house: animated project card"></picture></a><br><sub>A restaurant landing page.</sub><br><sub>TypeScript &nbsp;·&nbsp; <a href="https://github.com/Samudra-GITHub/the-waffle-house">GitHub ↗</a> &nbsp;·&nbsp; <a href="https://the-waffle-house.vercel.app">Live ↗</a></sub></td><td width="50%" valign="top"><a href="https://github.com/Samudra-GITHub/singularity-login"><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/readme/dark/singularity-login.svg"><img src="./assets/readme/light/singularity-login.svg" width="100%" alt="singularity-login: animated project card"></picture></a><br><sub>A glassmorphism sign-in UI.</sub><br><sub>Next.js · TypeScript · Tailwind &nbsp;·&nbsp; <a href="https://github.com/Samudra-GITHub/singularity-login">GitHub ↗</a></sub></td></tr>
<tr><td width="50%" valign="top"><a href="https://github.com/Samudra-GITHub/speed-of-numbers-fca"><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/readme/dark/speed-of-numbers-fca.svg"><img src="./assets/readme/light/speed-of-numbers-fca.svg" width="100%" alt="speed-of-numbers-fca: animated project card"></picture></a><br><sub>A team lab on numeric representation and execution speed on the ESP32.</sub><br><sub>Arduino · TeX &nbsp;·&nbsp; <a href="https://github.com/Samudra-GITHub/speed-of-numbers-fca">GitHub ↗</a></sub></td><td width="50%" valign="top"><a href="https://github.com/Samudra-GITHub/website"><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/readme/dark/website.svg"><img src="./assets/readme/light/website.svg" width="100%" alt="website: animated project card"></picture></a><br><sub>An early website experiment.</sub><br><sub>HTML &nbsp;·&nbsp; <a href="https://github.com/Samudra-GITHub/website">GitHub ↗</a></sub></td></tr>
<tr><td width="50%" valign="top"><a href="https://github.com/Samudra-GITHub/vyom"><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/readme/dark/vyom.svg"><img src="./assets/readme/light/vyom.svg" width="100%" alt="vyom: animated project card"></picture></a><br><sub>Work in progress.</sub><br><sub><a href="https://github.com/Samudra-GITHub/vyom">GitHub ↗</a></sub></td><td width="50%" valign="top"><a href="https://github.com/Samudra-GITHub/Samudra-GITHub"><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/readme/dark/samudra-github.svg"><img src="./assets/readme/light/samudra-github.svg" width="100%" alt="Samudra-GITHub: animated project card"></picture></a><br><sub>This profile README and the generator behind its artwork: every SVG here is drawn by <code>tools/build_readme.py</code>, in a dark and a light version.</sub><br><sub>Python &nbsp;·&nbsp; <a href="https://github.com/Samudra-GITHub/Samudra-GITHub">GitHub ↗</a></sub></td></tr>
</table>

<br>

<a id="engineering-with-ai"></a>

<picture><source media="(prefers-color-scheme: dark)" srcset="./assets/readme/dark/sec-ai.svg"><img src="./assets/readme/light/sec-ai.svg" width="100%" alt="04 Engineering with AI"></picture>

<picture><source media="(prefers-color-scheme: dark)" srcset="./assets/readme/dark/ai-workflow.svg"><img src="./assets/readme/light/ai-workflow.svg" width="100%" alt="Engineering with AI: Samudra directs two AI engineering agents. Claude Code works on UI, UX, design tokens and docs; Antigravity on boot, memory, interrupts, scheduler and drivers. Both share one repository with docs, API contracts, handoff notes and commits, and a review, run, accept or reject loop returns to Samudra."></picture>

Claude Code and Antigravity are AI engineering agents, not people. I use them as part of my workflow, not as a replacement for engineering decisions: I set architecture, direction and validation, and they implement. They coordinate through the repository itself: shared docs, interface contracts, handoff notes and commits.

<br>

<a id="stack"></a>

<picture><source media="(prefers-color-scheme: dark)" srcset="./assets/readme/dark/sec-stack.svg"><img src="./assets/readme/light/sec-stack.svg" width="100%" alt="05 Stack"></picture>

<picture><source media="(prefers-color-scheme: dark)" srcset="./assets/readme/dark/stack.svg"><img src="./assets/readme/light/stack.svg" width="100%" alt="Stack. Languages: TypeScript, JavaScript, Python, C, x86-64 Assembly. Systems: Clang, LLD, NASM, QEMU, Git, Docker. Web: React, Next.js, Tailwind, Framer Motion, GSAP, Three.js, CesiumJS. AI and vision: PyTorch, NumPy, SciPy, scikit-image, LLM APIs, Ollama. Design: Figma, design systems, motion design."></picture>

**Interests** &nbsp; Systems · AI / Computer Vision · Product Engineering · UI / UX · Developer Tools

<br>

<a id="contact"></a>

<picture><source media="(prefers-color-scheme: dark)" srcset="./assets/readme/dark/sec-contact.svg"><img src="./assets/readme/light/sec-contact.svg" width="100%" alt="06 Contact"></picture>

<picture><source media="(prefers-color-scheme: dark)" srcset="./assets/readme/dark/closing.svg"><img src="./assets/readme/light/closing.svg" width="100%" alt="Let's build something real. Samudra Kar, open to internships. Bangalore, India. Chanakya University."></picture>

<p align="center"><a href="https://sam-sportfolio.vercel.app">Portfolio</a> &nbsp;·&nbsp; <a href="https://www.linkedin.com/in/samudra-kar-a495951b5/">LinkedIn</a> &nbsp;·&nbsp; <a href="https://github.com/Samudra-GITHub">GitHub</a> &nbsp;·&nbsp; <a href="mailto:hi.samsstudio@gmail.com">Email</a></p>
