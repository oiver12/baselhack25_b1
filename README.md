# BaselHack25 Consensus Builder Backend

Frontend for building consensus through AI analysis of discussions. This project is part of the [BaselHack 2025 Collective Intelligence Challenge](https://www.baselhack.ch/challenges/collective-intelligence-building-consensus-through-ai).


## ✨ Features

### 🎨 Interactive Bubble Visualization
- **Physics-based layout** using D3-force for natural bubble positioning and collision detection
- **Dynamic sizing** based on suggestion strength and consensus level
- **Real-time updates** as new opinions and suggestions emerge
- **Hover interactions** to explore pros, cons, and individual opinions

### 💬 Real-Time Message Stream
- **Server-Sent Events (SSE)** for live updates
- **Toast notifications** that stack beautifully as new messages arrive
- **Automatic grouping** of simultaneous messages
- **Elegant animations** for appearance and dismissal

### 🧠 AI-Powered Consensus Analysis
- **Opinion classification**: Sophisticated, Simple, or Neutral
- **Pros/Cons extraction** from collective discussions
- **Suggestion strength calculation** based on consensus momentum
- **Progressive consensus building** visualized through evolving bubble sizes

## 🛠️ Tech Stack

- **Framework**: [Next.js 16](https://nextjs.org) (App Router)
- **Language**: [TypeScript](https://www.typescriptlang.org)
- **Styling**: [Tailwind CSS v4](https://tailwindcss.com)
- **Visualization**: [D3-Force](https://github.com/d3/d3-force) for physics simulation
- **Icons**: [Lucide React](https://lucide.dev)
- **Code Quality**: [Biome](https://biomejs.dev)

## 🚀 Getting Started

### Prerequisites

- [Bun](https://bun.sh) (recommended) or Node.js 18+
- A modern web browser

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd baselhack-25
```

2. Install dependencies:
```bash
bun install
# or
npm install
```

3. Run the development server:
```bash
bun dev
# or
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

### Build for Production

```bash
bun build
bun start
```

## 📁 Project Structure

```
baselhack-25/
├── src/
│   ├── app/
│   │   ├── api/
│   │   │   ├── suggestions/    # Suggestion data API (staged consensus)
│   │   │   └── webhook/        # Server-Sent Events stream
│   │   ├── components/
│   │   │   ├── MessageStream.tsx      # Real-time toast notifications
│   │   │   ├── SuggestionsDisplay.tsx  # Main bubble visualization
│   │   │   └── SuggestionCard.tsx     # Card view component
│   │   ├── layout.tsx         # Root layout
│   │   └── page.tsx           # Home page
│   └── lib/
│       └── types.ts           # TypeScript type definitions
├── public/                    # Static assets
├── package.json
└── README.md
```

## 🏗️ Architecture

### Data Flow

1. **Suggestion Collection**: The `/api/suggestions` endpoint returns staged suggestion data that simulates the progressive building of consensus
2. **Real-Time Updates**: The `/api/webhook` endpoint streams messages via Server-Sent Events
3. **Visualization**: The `SuggestionsDisplay` component renders suggestions as interactive bubbles with:
   - Parent bubbles (suggestions) sized by consensus strength
   - Child bubbles (opinions, pros, cons) orbiting around parents
   - Physics simulation preventing overlaps
   - Smooth animations and transitions

### Key Components

#### `SuggestionsDisplay`
- Renders suggestions as interactive bubble charts
- Uses D3-force for collision detection and smooth positioning
- Handles hover states to show detailed information
- Updates every second to show progressive consensus building

#### `MessageStream`
- Displays real-time messages as toast notifications
- Groups simultaneous messages together
- Auto-dismisses after a set duration
- Stacks messages with elegant animations

## 🎨 Visual Design

- **Modern glassmorphism** effects with backdrop blur
- **Gradient color schemes** for different suggestion types
- **Smooth animations** for bubble movement and appearance
- **Dark mode support** throughout
- **Responsive design** that adapts to different screen sizes

## 🔮 Future Enhancements

- [ ] Integration with Discord/Telegram bots for opinion collection
- [ ] Real AI-powered analysis using LLMs (e.g., OpenAI, Anthropic)
- [ ] Database persistence for suggestions and opinions
- [ ] User authentication and profiles
- [ ] Export consensus reports as PDFs
- [ ] Multi-topic support with topic switching
- [ ] Voting mechanisms to refine consensus
- [ ] Integration with Slack, Microsoft Teams, or other collaboration tools

## 📝 Development

### Code Formatting

```bash
bun run format
```

### Linting

```bash
bun run lint
```

## 🤝 Contributing

This project was built for BaselHack 2025. Contributions and improvements are welcome!

## 📄 License

[Add your license here]

## 🙏 Acknowledgments

- **BaselHack 2025** organizers for hosting the hackathon
- **Endress+Hauser** for sponsoring the challenge
- The open-source community for the amazing tools and libraries used in this project

---

**Built with ❤️ for BaselHack 2025**
