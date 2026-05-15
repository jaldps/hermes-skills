// Generic WhatsApp Web Script Bomber
// Usage: Call enviarScript("your text here") — each line becomes a separate message
// Requirements: Must have a conversation open in WhatsApp Web

async function enviarScript(scriptText) {
  const lines = scriptText.split(/[\n\t]+/).map(line => line.trim()).filter(line => line);
  const main = document.querySelector("#main");
  const textarea = main.querySelector(`div[contenteditable="true"]`);

  if (!textarea) throw new Error("Não há uma conversa aberta / No open conversation found");

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

// Telegram Web Script Bomber
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
      || document.querySelector('.btn-send');

    if (sendBtn && !sendBtn.disabled) {
      sendBtn.click();
    } else {
      input.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', keyCode: 13, bubbles: true }));
    }

    if (lines.indexOf(line) !== lines.length - 1)
      await new Promise(r => setTimeout(r, 300));
  }
  return lines.length;
}

// Discord Script Bomber
async function discordBomb(scriptText) {
  const lines = scriptText.split(/[\n\t]+/).map(l => l.trim()).filter(l => l);
  const editor = document.querySelector('[data-slate-editor="true"]')
    || document.querySelector('div[class*="slateEditor"] [contenteditable="true"]');

  if (!editor) throw new Error("No Discord chat input found");

  for (const line of lines) {
    editor.focus();
    document.execCommand('insertText', false, line);
    editor.dispatchEvent(new Event('input', { bubbles: true }));

    await new Promise(r => setTimeout(r, 100));

    editor.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', keyCode: 13, bubbles: true }));
    editor.dispatchEvent(new KeyboardEvent('keyup', { key: 'Enter', keyCode: 13, bubbles: true }));

    if (lines.indexOf(line) !== lines.length - 1)
      await new Promise(r => setTimeout(r, 500));
  }
  return lines.length;
}

// Export for use
console.log("Script bomber loaded. Functions: enviarScript(text), telegramBomb(text), discordBomb(text)");
