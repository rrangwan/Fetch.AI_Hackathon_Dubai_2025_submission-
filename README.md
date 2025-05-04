# Fetch.AI Hackathon Dubai 2025 Submission

![tag : innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)
[![Hackathon Link](https://img.shields.io/badge/Event-Fetch.AI_Hackathon_Dubai_2025-blue)](https://lu.ma/zjn0njeu?tk=p6Uvcy)

## 📋 Project Overview

**Project Name: CelebrityAi**

**Agent Name:** CelebrityAi**

**Agent Address:** [agent1qwcjyh288szzhny06d6th3j6qkauxeljp94ps5vhkxl8ej6dclg9kvq6lss]

**Team Name:**  CelebrityAi

**Track:** [Creator Economy Track / ASI-1 Mini Challenge / Other]

## 🌟 Problem Statement

Celebrities face significant time constraints while managing their extensive fan engagement across multiple platforms. Despite their desire to connect authentically with fans, the fragmentation of digital spaces creates inefficiencies that limit meaningful interactions. Our solution addresses this gap by streamlining celebrity-fan connections, allowing personalities to expand their reach without the corresponding time investment.

## 💡 Solution

Our agent, powered by Fetch.AI's technology, creates an authentic celebrity presence through advanced voice cloning. This AI-powered solution enables fans to interact with a highly accurate vocal representation of their favorite celebrities, providing personalized experiences at scale. The agent handles routine fan interactions, answers common questions, and delivers custom content in the celebrity's voice, allowing personalities to maintain a consistent presence across platforms without the time commitment typically required. This creates new revenue streams and engagement opportunities while preserving the celebrity's authentic connection with their audience.
## 🔧 Technical Architecture

Using a pretrained voice cloning *model created by Cambridge university, we made tweaks and hosted it on a server with API endpoints.  
The user will enter text they wish to be said by their celebrity. The celebrity’s voice has already been cloned by the model.  
A call is made to the Fetch ASI:One LLM, to verify the quality and validity of the user text. If approved, the user is charged 10 $FET, and the test message is sent via API to the model. The model then returns a link to a sound file hosted on the external server, from which the user can download and play the sound. 
* https://huggingface.co/spaces/mrfakename/E2-F5-TTS 

### **🚀Agent Capabilities**
- **Ethical Text Filtering**:
  - The agent uses ASI-1 Mini to perform ethical checks on user-submitted text, ensuring that all interactions adhere to predefined ethical guidelines.
- **Celebrity-Style Text Generation**:
  - The agent generates personalized, celebrity-style responses using ASI-1 Mini's advanced language modeling capabilities.
- **Voice Synthesis**:
   - The `waver_generate_sound` function integrates the **F5-TTS model** (sourced from Hugging Face and GitHub under the MIT license) to convert text into a realistic celebrity voice.
- **Multi-Step Task Execution**:
  - The agent performs multi-step workflows, including ethical checks, text generation, and voice synthesis, ensuring seamless task execution.
- **Memory and Context Awareness**:
  - The agent stores and retrieves past interactions using a database, enabling personalized and context-aware responses.
- **ChatProtocol Integration**:
  - The agent uses `ChatProtocol v0.3.0` to handle structured conversational workflows, including message acknowledgments and multi-turn dialogues.

## 🖥️ Installation & Setup

### Prerequisites

```
- Python 3.12+
- 
```

### Installation Steps

1. Clone the repository
   ```bash
   git clone https://github.com/rrangwan/Fetch.AI_Hackathon_Dubai_2025_submission-.git
   cd Fetch.AI_Hackathon_Dubai_2025_submission-
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   # Additional setup commands if needed
   ```
1. You have to install poetry. It's a python package manager.

2. Install all dependencies:
```bash
    poetry install
```

3. Create and fill up the .env file:
```bash
    PORT=8000
    SEED="123456"
    ASI1_API_KEY="ASI1_KEY"
    WAVER_ADDRESS="localhost:5000" # service that able to generate .wav file 
```

4. Run the agent in dev mode: 
```bash
    ./dev_run.sh
```

5. Test the agent by test.py
```bash
    poetry run python test.py
```
6. Clone and set up the F5-TTS model
   - Follow the instructions in the [F5-TTS GitHub repository](https://github.com/SWivid/F5-TTS) to clone and configure the model for voice synthesis.
   - We hosted it on a instance and made a PPT.
   

## 🎬 Demo

### Video Demo
[Link to demo video](https://github.com/rrangwan/Fetch.AI_Hackathon_Dubai_2025_submission-/blob/main/docs/demo.mp4)

### Screenshots
[screenshots showcasing agent in action](https://github.com/rrangwan/Fetch.AI_Hackathon_Dubai_2025_submission-/blob/main/docs/screenshots.pdf)

## 💼 Business Potential

Our celebrity voice agent platform unlocks significant market opportunities with diverse revenue streams:

### **Target Audience**
- Celebrities, public figures, and content creators seeking enhanced fan engagement.
- Entertainment companies managing artist portfolios.
- Sports personalities and fans desiring personalized interactions.

### **Revenue Streams**
- Subscription plans for celebrities based on interaction volume.
- Sharing of royalties from musical content generation.
- Premium fan experiences (e.g., personalized messages, custom content).
- Sponsored interactions via brand partnerships.
- White-label solutions for entertainment companies.

### **Scalability**
- Cloud-based architecture for rapid onboarding.
- Modular design for quick feature additions.
- API-first approach for seamless integration.
- Multi-language support for global reach.
- Automated training for cost-efficient voice profile creation.

## 👥 Team Information

### Team Members

- **[Member 1 Raj Rangwani]** - [Developer]
- **[Member 2 Joe Perinchery ]** - [Developer]
- **[Member 3 Timur Mazitov]** - [Developer]

## 📚 Additional Documentation

- [ Link to your project presentation/pitch deck](https://github.com/rrangwan/Fetch.AI_Hackathon_Dubai_2025_submission-/blob/main/docs/CelebrityAI.pdf)
- [Link to one-page project summary](https://github.com/rrangwan/Fetch.AI_Hackathon_Dubai_2025_submission-/blob/main/docs/CelebrityAI.pptx)
- [Summary](https://github.com/rrangwan/Fetch.AI_Hackathon_Dubai_2025_submission-/blob/main/docs/summary.pdf)

## 📊 Track-Specific Information

### For Creator Economy Track

We collaborated with N1yah, a celebrity who aspired to connect with her fans more effectively through a digital presence. She envisioned a solution that could replicate her voice and personality, enabling her to engage with her audience at scale while maintaining authenticity. After brainstorming together, we conceptualized and developed a digital voice clone powered by AI.

This AI-driven voice clone not only captures Niyah's tone and style but also performs a variety of tasks, including:
- Responding to fan messages in her voice.
- Delivering personalized content such as greetings or shoutouts.
- Creating an immersive and authentic fan experience.

Using Fetch.AI's agent framework, ASI-1 Mini and the F5-TTS model, we brought this vision to life. The agent performs ethical checks, generates celebrity-style responses, and converts them into a realistic voice using advanced voice synthesis. This solution allows Niyah to maintain a meaningful connection with her fans while saving time and effort, showcasing how digital clones can transform fan engagement in the creator economy.
### For ASI-1 Mini Challenge

During development, we faced challenges due to the lack of sample data for ASI-1 Mini. With guidance from mentors, we successfully integrated ASI-1 Mini for:
- Ethical text filtering to ensure guideline compliance.
- Celebrity-style text generation for engaging responses.

This integration showcases ASI-1 Mini's reasoning capabilities, enabling precise and efficient multi-step task execution.
## 📝 License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

---

*This project was developed for the Fetch.AI Hackathon Dubai 2025.*
