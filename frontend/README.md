# Frontend — React Application

Self-service web UI for Proxmox ISP. Built with React 18, TypeScript, TanStack Query, Tailwind CSS, and shadcn/ui.

## Quick Start

```bash
npm install

# Set API URL (or create .env.local)
export VITE_API_URL=http://localhost:8000/api/v1

# Start dev server
npm run dev
```

- **Dev server:** http://localhost:5173
- **Production build:** `npm run build` → `dist/`

## Architecture

```
src/
├── components/          # Reusable UI components
│   └── ui/              # shadcn/ui primitives
├── pages/               # Route-level page components
├── services/            # API client (api.ts)
├── hooks/               # Custom React hooks
├── lib/                 # Utilities, types, constants
└── App.tsx              # Router and layout
```

## Development

```bash
# Lint
npm run lint

# Format
npm run format

# Type check
npx tsc --noEmit

# Build for production
npm run build
```

## API Integration

All API calls go through `services/api.ts`. The client uses the `VITE_API_URL` environment variable.

```typescript
import { api } from '@/services/api'

// Authenticated request (token from localStorage)
const vms = await api.vms.list(orgId)

// Create VM
const vm = await api.vms.create(orgId, { name: 'my-vm', cpu_cores: 2, ... })
```

## Conventions

- TypeScript strict mode
- TanStack Query for server state (caching, auto-refresh)
- shadcn/ui for component primitives
- Tailwind CSS for styling
- React Router for navigation
- All API endpoints typed in `services/api.ts`
