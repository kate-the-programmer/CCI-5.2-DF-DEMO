# 🔍 Digital Forensics Demonstration Platform

![GitHub repo size](https://img.shields.io/github/repo-size/kate-the-programmer/CCI-5.2-DF-DEMO?style=for-the-badge)  
![GitHub issues](https://img.shields.io/github/issues/kate-the-programmer/CCI-5.2-DF-DEMO?style=for-the-badge)  
![GitHub license](https://img.shields.io/github/license/kate-the-programmer/CCI-5.2-DF-DEMO?style=for-the-badge)

An interactive, **Raspberry Pi-based cybersecurity training environment** developed under **DOE CCI Subtask 5.2** at NCREPT. This platform unifies multiple **digital forensics and cybersecurity simulations** into a single Python GUI, designed for **classrooms, labs, and outreach events**.  

---

## 📖 Table of Contents
- [Features](#-features)
- [Modules](#-modules)
- [Requirements](#️-requirements)
- [Installation](#-installation)
- [Usage](#-usage)
- [Documentation](#-documentation)
- [Contributing](#-contributing)


---

## 🚀 Features
- Centralized **Tkinter GUI** with a hacker-themed design.  
- **10 interactive forensic modules** + **CTF challenges** for gamified learning.  
- **Open-source tools** integrated (Autopsy, Volatility, John the Ripper, Hashcat, Wireshark, Stegosuite, etc.).  
- **Safe, sandboxed simulations** for ransomware, malware, and password cracking.  
- **Portable Raspberry Pi build** with kiosk auto-launch for quick deployment.  

---

## 🧩 Modules

| #      | Module                              | Key Concepts                                               |
|--------|-------------------------------------|-----------------------------------------------------------|
| 2.1.1  | Autopsy Forensics                  | Disk image analysis, deleted file recovery                |
| 2.1.2  | Write Blocker Simulation           | Evidence integrity, hardware protections                  |
| 2.1.3  | Ransomware Simulation              | File encryption, backups, incident response               |
| 2.1.4  | Password Cracking                  | Dictionary & brute-force attacks, password security       |
| 2.1.5  | Memory Forensics                   | Volatility analysis of live processes and injected code   |
| 2.1.6  | Network Forensics                  | Packet analysis, threat hunting using Tshark              |
| 2.1.7  | Metadata Forensics                 | Hidden file metadata, timelines, GPS/device IDs           |
| 2.1.8  | Steganography Detection            | Hidden messages in images via Stegosuite                  |
| 2.1.9  | Malware Static Analysis            | Strings, imports, entropy checks, radare2 disassembly     |
| 2.1.10 | Capture The Flag (CTF) Challenges  | Gamified multi-tool investigation                         |

---

## ️🛠 Requirements
- **Hardware:** Raspberry Pi 4 (4GB+ recommended), keyboard, mouse, HDMI display.  
- **OS:** Kali Linux or compatible Debian-based OS.  
- **Dependencies:**  
  ```bash
  sudo apt update
  sudo apt install python3-tk autopsy volatility3 john hashcat tshark stegosuite radare2 exiftool make
  ```

---

## 📥 Installation
```bash
git clone https://github.com/kate-the-programmer/CCI-5.2-DF-DEMO.git
cd CCI-5.2-DF-DEMO
python3 main.py
```

For **auto-launch on boot**, add the startup command to your `.bashrc` or system startup scripts.

---

## 🎮 Usage
- **Dashboard:** Choose a demo module or CTF challenge.  
- **Keyboard Shortcuts:**  
  - `Ctrl+A` → Autopsy Demo  
  - `Ctrl+R` → RAID Demo  
  - `Ctrl+W` → Write Blocker Demo  
  - `Ctrl+Shift+Q` → Exit GUI  
- **CTF Mode:** Solve forensic challenges, find flags (`Flag{example}`), and score points.  
- **Documentation:** PDFs and ReadMe files for each module are available in `/Assets`.

---

## 📚 Documentation
Full user documentation is available in:
- `/Digital_Forensics_Documentation.docx`  
- `/Assets` for module-specific PDF guides and step-by-step instructions.

---

## 🤝 Contributing
We welcome contributions from the cybersecurity education community:
1. **Fork** the repo  
2. Create a **feature branch**  
3. Submit a **pull request** with detailed notes  
4. Open **issues** for bug reports or enhancements  

---

> ⚠️ **Disclaimer:** This project is for **educational use only**. Do not use forensic or offensive tools on unauthorized systems or live evidence.

