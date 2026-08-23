# Frontend Testing — Swiss Data Airlock

The frontend is a React 18 + Vite + Tailwind CSS SPA. Since it's a hackathon MVP,
automated frontend tests are optional. Below are guidelines for manual and E2E testing.

## Manual Testing Checklist

### 1. Smoke Test — App Loads
- [ ] Open `http://localhost:5173` (dev) or `http://localhost:8000` (prod)
- [ ] Header shows "Swiss Data Airlock"
- [ ] Tab navigation visible: Demo, Vault, Stats, Audit

### 2. Demo Tab — Core Flow
- [ ] Type a prompt with PII: `"Contact Hans Peter at hans@example.com"`
- [ ] Click Send
- [ ] **Input panel** shows original text
- [ ] **Masked panel** shows tokens (e.g. `[PERSON_1]`, `[EMAIL_1]`)
- [ ] **Response panel** shows LLM response
- [ ] **Entity tags** show detected PII types

### 3. Role Switching
- [ ] Switch role to "Auditor"
- [ ] Send a new prompt with PII
- [ ] Response panel shows **masked** text (tokens, not originals)
- [ ] Switch back to "Admin"
- [ ] Response panel shows **restored** text (originals)

### 4. Vault Inspector Tab
- [ ] Navigate to Vault tab
- [ ] Enter a session ID from a previous chat
- [ ] Click Load
- [ ] Vault shows token-to-value mappings
- [ ] Session info shows request count, token count

### 5. Stats Tab
- [ ] Navigate to Stats tab
- [ ] Vault stats show active sessions, total stores
- [ ] LLM stats show mock mode
- [ ] Audit stats show request count

### 6. Audit Log Tab
- [ ] Navigate to Audit tab
- [ ] Shows recent chat entries
- [ ] Each entry shows: role, masked prompt, LLM response, latency

### 7. Toast Notifications
- [ ] Trigger an error (e.g., invalid session ID in Vault)
- [ ] Red toast appears at bottom-right
- [ ] Toast auto-dismisses after ~5 seconds
- [ ] Toast can be manually dismissed by clicking X

### 8. Responsive Layout
- [ ] Resize browser to mobile width
- [ ] Layout adapts (panels stack vertically)
- [ ] All controls remain accessible

## E2E Scenario: Full Data Flow

```
1. Open app
2. Enter: "Invoice for Hans Peter, email hans@example.com, IBAN CH9300762011623852957"
3. Role: Admin
4. Send → verify masked_payload has [PERSON_1], [EMAIL_1], [IBAN_1]
5. Verify final_response has "Hans Peter", "hans@example.com", "CH9300762011623852957"
6. Copy session_id
7. Go to Vault tab → paste session_id → Load → see all 3 mappings
8. Switch to Auditor role → send same prompt → final_response keeps tokens
9. Go to Audit tab → see both entries (admin + auditor)
```

## Future: Vitest Unit Tests

If you want to add automated component tests later:

```bash
# Install
npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom

# Add to vite.config.js:
# test: { environment: 'jsdom' }

# Run
npx vitest
```

Example test:
```jsx
import { render, screen } from '@testing-library/react'
import Header from '../src/components/Header'

test('renders app title', () => {
  render(<Header />)
  expect(screen.getByText(/Swiss Data Airlock/)).toBeInTheDocument()
})
```
