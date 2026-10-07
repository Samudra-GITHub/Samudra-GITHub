# Samudra Kar

**Computer Science engineering student · Builder · Systems, AI and product**

I build software across layers: an x86-64 kernel at the bottom, AI and computer-vision prototypes in the middle, product interfaces on top. I like to understand a system from the lowest level it touches, and I care about how it feels to use. Based in Bangalore.

---

## Currently building

### [Samagra OS](https://github.com/Samudra-GITHub/Samagra-OS) &nbsp;·&nbsp; समग्र OS

A real x86-64 operating system, built from first principles.

It boots into long mode and has physical and virtual memory management, interrupt and exception handling, a timer, and a preemptive round-robin scheduler running kernel tasks, all tested in QEMU. There is no user space, filesystem, networking or desktop yet, and the README says so.

`C` · `x86-64 assembly` · `Clang / LLD / NASM` · `QEMU`

It is developed through a human-directed AI engineering workflow: **Samudra** sets architecture and direction, and **Claude Code** and **Antigravity**, both AI engineering agents, implement against it. More on that [below](#engineering-with-ai).

---

## Selected work

**[PRAHARI](https://github.com/Samudra-GITHub/PRAHARI)**<br>
Mine safety and compliance monitoring. A role-based API, deterministic risk scoring with listed reasons, a hash-chained audit log that can be verified for tampering, and a copilot that only narrates permission-scoped data. Built for the Smart India Hackathon.<br>
`Next.js` · `Prisma` · `PostgreSQL` · `Docker`

**[AkashaLens](https://github.com/Samudra-GITHub/AkashaLens)**<br>
Cloud removal for satellite imagery. A PyTorch U-Net prototype that reconstructs cloud-covered Sentinel-2 scenes, with a cloud mask, a confidence heatmap and MAE / PSNR / SSIM evaluation behind a Flask demo. Built for ISRO Hackathon 2026. A prototype, trained on a tiny sample set.<br>
`PyTorch` · `scikit-image` · `Flask`

**[Tarang](https://github.com/Samudra-GITHub/Tarang)** &nbsp;·&nbsp; [live](https://tarang-ecru.vercel.app)<br>
A music web app built around a persistent floating player that expands into a full now-playing view, with a queue, time-synced lyrics and a documented design system. Frontend only, on seed data.<br>
`Next.js` · `TypeScript` · `Framer Motion` · `Zustand`

**[Rinti AI](https://github.com/Samudra-GITHub/Rinti-Ai)** &nbsp;·&nbsp; [live](https://rinti-ai.vercel.app)<br>
A chat workspace with per-user memory, a cited multi-step research mode and real account sessions: Argon2 password hashing, HttpOnly cookies and CSRF checks.<br>
`FastAPI` · `Next.js` · `Groq` · `Tavily`

**[Orbit OS](https://github.com/Samudra-GITHub/orbit-os)**<br>
An interface exploration: a personal dashboard that borrows from operating-system design, with a persistent shell, a command palette and a notification center. Not a real operating system, and mostly mock data.<br>
`Next.js` · `TypeScript` · `Framer Motion`

More on [GitHub](https://github.com/Samudra-GITHub?tab=repositories) and in my [portfolio](https://sam-sportfolio.vercel.app).

---

## Engineering with AI

I use AI engineering agents as part of my workflow, not as a replacement for engineering decisions. They are tools with defined responsibilities.

On Samagra OS:

- **Samudra**: architecture, direction, validation and integration
- **Claude Code**: UI, documentation, design and user-facing systems
- **Antigravity**: kernel, memory, interrupts, scheduling and low-level systems

The agents coordinate through the repository itself: shared docs, interface contracts, handoff notes and commits.

---

## What I work with

| | |
|---|---|
| **Languages** | TypeScript, JavaScript, Python, C, x86-64 assembly, HTML / CSS |
| **Systems** | Clang, LLD, NASM, QEMU, Git, Docker |
| **Web** | React, Next.js, Tailwind CSS, Framer Motion, GSAP, WebGL / Three.js |
| **Backend** | FastAPI, Flask, Prisma, PostgreSQL |
| **AI and vision** | PyTorch, NumPy, SciPy, scikit-image, LLM APIs |
| **Design** | Figma, design systems, motion design |

## Interests

Systems · AI and computer vision · Product engineering · UI/UX · Developer tools

---

## Connect

[Portfolio](https://sam-sportfolio.vercel.app) · [LinkedIn](https://www.linkedin.com/in/samudra-kar-a495951b5/) · [Email](mailto:hi.samsstudio@gmail.com) · [GitHub](https://github.com/Samudra-GITHub)

Computer Science Engineering at Chanakya University. Open to internships.
