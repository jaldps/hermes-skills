---
name: antiscammer
description: Anti-scammer toolkit — script-bomb WhatsApp/Telegram/Discord contacts with endless text, and reply to scam emails with impossibly verbose bureaucratic nonsense.
tools:
  - browser
  - computer_use
  - terminal
---

# Anti-Scammer Skill

Three modes of operation:

1. **WhatsApp Script Bomb** — flood a WhatsApp Web chat with a long script (Shrek, Bee Movie, or custom text) sent line-by-line
2. **Telegram/Discord Script Bomb** — same concept for Telegram Web and Discord browser
3. **Scam Email Replier** — generate and send extremely long, overcomplicated, posh ultra-technical replies to scam emails

---

## 1. WhatsApp Script Bomb

### Prerequisites
- WhatsApp Web open in a browser (Chrome/Brave/Edge/Safari)
- A conversation must be open (the chat you want to bomb)
- Browser must have "Allow JavaScript from Apple Events" enabled (for Safari) or dev console access

### How It Works
The technique uses the browser's JS console to:
1. Find the open chat's contenteditable div
2. Insert text line-by-line via `document.execCommand('insertText')`
3. Dispatch a `change` event
4. Click the send button
5. Wait 250ms between lines

The script **keeps running even after the target closes the conversation** — they are forced to block you.

### Chrome Console Paste Block
Chrome blocks pasting scripts in DevTools console. The user must first type:
```
allow pasting
```
in the console and press Enter. After that, pasting works.

### Workflow

#### Option A: Using computer_use to drive the browser
1. User says: "bomb [contact name] on whatsapp with [shrek/bee movie/custom text]"
2. Capture the WhatsApp Web window
3. Ensure the target conversation is open
4. Open DevTools console (Cmd+Option+J on Chrome)
5. If Chrome: type `allow pasting` first
6. Paste the bomb script (see Script Templates below)
7. Press Enter to execute
8. The script runs autonomously — no further action needed

#### Option B: Using browser_navigate + browser_console
1. Navigate to web.whatsapp.com (should already be logged in)
2. Have the user open the target chat
3. Use `browser_console(expression=...)` to inject the JS directly
4. This bypasses the console paste restriction entirely

### The Core JS Function

```javascript
async function enviarScript(scriptText) {
  const lines = scriptText.split(/[\n\t]+/).map(line => line.trim()).filter(line => line);
  const main = document.querySelector("#main");
  const textarea = main.querySelector(`div[contenteditable="true"]`);

  if (!textarea) throw new Error("No open conversation found");

  for (const line of lines) {
    console.log(line);
    textarea.focus();
    document.execCommand('insertText', false, line);
    textarea.dispatchEvent(new Event('change', { bubbles: true }));

    setTimeout(() => {
      (main.querySelector(`[data-testid="send"]`) || main.querySelector(`[data-icon="send"]`)).click();
    }, 100);

    if (lines.indexOf(line) !== lines.length - 1)
      await new Promise(resolve => setTimeout(resolve, 250));
  }

  return lines.length;
}
```

### Script Templates

The skill includes bomber scripts at `scripts/` (see below). The function can be called with any text:

- **`scripts/whatsapp-bomb.js`** — Robust WhatsApp bomber with abort support (`window.__sendScriptAbort = true`), clipboard fallback, send-button fallback, and a single-message mode (`sendScriptSingle`). Preferred for WhatsApp.
- **`scripts/bomb.js`** — Lightweight bomber for all three platforms (WhatsApp `enviarScript`, Telegram `telegramBomb`, Discord `discordBomb`). Use for Telegram/Discord.

```javascript
// Custom text
enviarScript(`Your custom text here
line by line
each line becomes a separate message`).then(e => console.log(`Done, ${e} messages sent`)).catch(console.error);
```

For the full Shrek or Bee Movie scripts, load them from `references/shrek-script.txt` or `references/bee-movie-script.txt`.

### Support Files

| File | Purpose |
|------|---------|
| `scripts/whatsapp-bomb.js` | Robust WA bomber with abort + clipboard fallback + single-message mode |
| `scripts/bomb.js` | Lightweight bomber for WA / Telegram / Discord |
| `references/shrek-script.txt` | Full Shrek screenplay (3,679 lines, ~15 min at 250ms/line) |
| `references/bee-movie-script.txt` | Full Bee Movie script (1,371 lines, ~6 min at 250ms/line) |
| `references/email-style-guide.md` | Verbose scam-reply style guide with examples and word-choice patterns |

### Quick Injection via browser_console

When using Hermes browser tools, inject directly:

```
browser_console(expression="<the full JS code>")
```

This is the preferred method — no need to open DevTools or deal with Chrome paste blocking.

---

## 2. Telegram/Discord Script Bomb

### Telegram Web

The same concept, adapted selectors:

```javascript
async function telegramBomb(scriptText) {
  const lines = scriptText.split(/[\n\t]+/).map(l => l.trim()).filter(l => l);
  const input = document.querySelector('.input-message-container [contenteditable="true"]')
    || document.querySelector('div[data-testid="input-message"]')
    || document.querySelector('.input-message-input');

  if (!input) throw new Error("No Telegram chat input found");

  for (const line of lines) {
    input.focus();
    document.execCommand('insertText', false, line);
    input.dispatchEvent(new Event('input', { bubbles: true }));

    await new Promise(r => setTimeout(r, 100));

    const sendBtn = document.querySelector('button[data-testid="send-message"]')
      || document.querySelector('.btn-send')
      || document.querySelector('button[title="Send"]');

    if (sendBtn && !sendBtn.disabled) {
      sendBtn.click();
    } else {
      // Fallback: press Enter
      input.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', keyCode: 13, bubbles: true }));
    }

    if (lines.indexOf(line) !== lines.length - 1)
      await new Promise(r => setTimeout(r, 300));
  }
  return lines.length;
}
```

### Discord

```javascript
async function discordBomb(scriptText) {
  const lines = scriptText.split(/[\n\t]+/).map(l => l.trim()).filter(l => l);
  const channelTextArea = document.querySelector('[data-slate-editor="true"]')
    || document.querySelector('.markdownEditor-1LQ2vc')
    || document.querySelector('div[class*="slateEditor"] [contenteditable="true"]');

  if (!channelTextArea) throw new Error("No Discord chat input found");

  for (const line of lines) {
    channelTextArea.focus();
    document.execCommand('insertText', false, line);
    channelTextArea.dispatchEvent(new Event('input', { bubbles: true }));

    await new Promise(r => setTimeout(r, 100));

    // Discord sends on Enter
    channelTextArea.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', keyCode: 13, bubbles: true }));
    channelTextArea.dispatchEvent(new KeyboardEvent('keyup', { key: 'Enter', keyCode: 13, bubbles: true }));

    if (lines.indexOf(line) !== lines.length - 1)
      await new Promise(r => setTimeout(r, 500));
  }
  return lines.length;
}
```

### Workflow
1. User says: "bomb [contact] on telegram/discord with [script]"
2. Ensure the target chat is open in the browser
3. Use `browser_console(expression=...)` to inject the appropriate function + call
4. The script runs autonomously

### Pitfalls
- Telegram Web selectors change frequently — if injection fails, capture the page and find the current input selector
- Discord's Slate editor can be finicky — may need to use clipboard paste instead of execCommand
- Both platforms have rate limiting — if messages stop sending, increase the delay between lines
- Very long scripts may cause the browser tab to become unresponsive

---

## 3. Scam Email Replier

### Concept
Generate an extremely long, overcomplicated reply to a scam email that:
- Uses posh, ultra-technical, hyper-bureaucratic language
- Goes around and around conveying basically **one simple idea**
- Wastes the scammer's time reading it
- Looks like something deep and actually related to the topic
- Is so dense and verbose that it's nearly impossible to extract any actionable information from it

### The Style

Combine three personas:
1. **Pretentious University Professor** — academic jargon, citations (real and fake), Latin phrases, hedging
2. **Corrupt Lawyer** — pseudo-legal language, excessive qualifications, conditional clauses, definitions
3. **Government Bureaucrat** — formalese, references to non-existent regulations, procedural tangents

### Key Techniques
- **Circular reasoning**: State the premise, support it with itself, conclude by restating the premise
- **Tangential depth**: Go on extended tangents about barely related topics before circling back
- **Definitional bloat**: Define every term, including common words, in excruciating detail
- **Conditional overload**: "Subject to the foregoing, and without prejudice to the aforementioned, notwithstanding..."
- **Latin sprinkling**: inter alia, mutatis mutandis, de facto, de jure, sui generis, prima facie, ceteris paribus, pro tem, ad infinitum
- **Footnote mania**: Add footnotes that are longer than the main text, and footnotes to footnotes
- **Academic hedging**: "It may perhaps be reasonably suggested that one might consider the possibility that..."
- **Self-referential paragraphs**: "As I noted in paragraph 7, subsection (b), which itself referenced the principle established in section 3..."
- **Quantifier stacking**: "Each and every one of any and all such parties hereto..."
- **Temporal dilution**: Spend 500 words saying "soon"

### Example: Nigerian Prince Scam Reply

If the scam says: "I am a prince and I need your help transferring $10 million"

The reply should convey essentially: "I am interested, tell me more"

But written as 2000+ words of:

```
Dear Esteemed Correspondent,

I write with reference to your communication of the [date] instant, wherein you have articulated a proposition of considerable financial consequence, the particulars of which warrant my most deliberate and circumspect consideration, inter alia, as they pertain to the transnational movement of monetary instruments...

[3 paragraphs defining what "money" and "transfer" mean]

[2 paragraphs citing fake UN resolutions about cross-border capital flows]

[1 paragraph about the philosophical implications of "trust" in digital communications]

[4 paragraphs of conditional acceptance with so many caveats it's unclear if you're accepting or declining]

[2 paragraphs requesting more information but phrased so opaquely they can't tell what you're asking for]

[1 paragraph of Latin phrases]

[Closing that takes 200 words to say "sincerely"]
```

### Workflow
1. User says: "scam reply to [scam text or description]"
2. Generate the verbose reply based on the scam's topic
3. Output the full email text directly in the chat — the user copies and pastes it themselves
4. NEVER attempt to send the email via browser automation, SMTP, Mail.app, or any other method
5. The skill ONLY generates text. Delivery is the user's responsibility.

### Generation Guidelines
- Minimum 1500 words, target 2000-3000
- Must reference specific details from the scam (names, amounts, countries) but twist them
- Include at least 3 fake institutional references (e.g., "Article 47(b) of the Geneva Protocol on Transnational Fiscal Arrangements")
- Include at least 2 Latin phrases per paragraph
- Every paragraph should be able to be summarized in 5 words or less
- The email should take at least 10 minutes to read but convey less than 30 seconds of actual information
- Never include real personal information
- Never actually agree to send money or click links
- The tone must be: EXTREMELY long, boring, overly technical, posh, ultra-technical — but still conveying a single simple idea with extreme elaboration and technicisms
- The scammer should be forced to read paragraphs of impenetrable jargon just to extract one trivial point
- Use run-on sentences with multiple subordinate clauses, parenthetical asides, and self-referential digressions
- Every sentence should feel like it's about to end but then continues with another qualification
- Reference real-sounding but fake committees, protocols, frameworks, and regulatory bodies
- Use numbering systems (Section 4.2.1(b)(iii)) that go nowhere
- The email must be copy-paste ready: plain text, no markdown formatting, no special characters that might break in email clients

### Safety
- NEVER actually send money, provide real banking details, or click any links in scam emails
- NEVER include real personal info in replies
- NEVER try to send the email — only output the text for the user to copy-paste
- The goal is to waste the scammer's time, not to engage with them seriously
- If the email contains malicious attachments or links, do NOT interact with them — just read the text

---

## Quick Reference

| Command | Action |
|---------|--------|
| `bomb whatsapp with shrek` | Send Shrek script to open WhatsApp chat |
| `bomb whatsapp with bee movie` | Send Bee Movie script to open WhatsApp chat |
| `bomb whatsapp with [custom text]` | Send custom text to open WhatsApp chat |
| `bomb telegram with shrek` | Same for Telegram Web |
| `bomb discord with shrek` | Same for Discord browser |
| `scam reply to [email]` | Generate verbose reply text (copy-paste it yourself) |

## Pitfalls
- WhatsApp Web DOM changes frequently — if selectors break, re-capture and find new ones
- Chrome blocks console paste — type `allow pasting` first, or use `browser_console` injection
- Rate limits on Telegram/Discord — increase delays if messages stop sending
- Scam email replies are OUTPUT ONLY — never try to auto-send, just give the user the text to copy-paste
- Never send scam replies from your real work email — use a throwaway address
- **Large scripts take a long time** — Shrek (3,679 lines) at 250ms/line = ~15 min. Bee Movie (1,371 lines) = ~6 min. Warn the user before starting
- **browser_console has a character limit** — for very long scripts (Shrek full text), inject the function definition separately, then call `enviarScript()` with the script text loaded from the reference files. If the expression is too large for a single console call, split it: first define the function, then call it with the text in a second call
- **WhatsApp may throttle** — if sending stops mid-script, the browser tab may have lost focus. Re-focus the tab and the script should resume (it's async and awaiting)
- **Do NOT close the browser tab** while the script is running — it will terminate the injection
