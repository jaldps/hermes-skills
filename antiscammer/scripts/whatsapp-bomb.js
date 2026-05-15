/**
 * WhatsApp Web Script Bomb — Generic Inject Function
 *
 * Based on the technique from https://github.com/Matt-Fontes/SendScriptWhatsApp
 *
 * This script sends a long text line-by-line into the currently open
 * WhatsApp Web conversation. It keeps running even if the recipient
 * closes the conversation — they must block you to stop it.
 *
 * USAGE IN BROWSER CONSOLE:
 *
 *   1. Open WhatsApp Web (https://web.whatsapp.com)
 *   2. Open the conversation you want to send to
 *   3. Open DevTools Console (F12 → Console)
 *   4. If Chrome blocks pasting, type:  allow pasting
 *   5. Paste this entire script and press Enter
 *   6. Call:  sendScript("Your text here", 250)
 *
 * You can also load a script from a variable:
 *
 *   var myScript = `Line 1\nLine 2\nLine 3`;
 *   sendScript(myScript);
 *
 * Or use one of the built-in presets (if embedded):
 *   sendScript(SHREK_SCRIPT);
 *   sendScript(BEE_MOVIE_SCRIPT);
 */

/**
 * Core send function.
 *
 * @param {string} text - The full text to send. Lines are split on \n.
 * @param {number} lineDelay - Milliseconds between each line (default 250).
 * @param {number} sendDelay - Milliseconds to wait before clicking send after inserting text (default 100).
 * @returns {Promise<void>}
 */
async function sendScript(text, lineDelay = 250, sendDelay = 100) {
  // Verify we have an open conversation
  const main = document.querySelector("#main");
  if (!main) {
    console.error(
      "[SendScript] No conversation is open. Open a chat first, then re-run."
    );
    return;
  }

  // Find the message input box
  const input = main.querySelector('div[contenteditable="true"]');
  if (!input) {
    console.error(
      "[SendScript] Could not find the message input field. Make sure a conversation is open."
    );
    return;
  }

  // Split text into lines, filter out empty trailing lines
  const lines = text.split("\n").filter((line, idx, arr) => {
    // Keep all lines except trailing empty ones
    if (idx < arr.length - 1) return true;
    return line.trim().length > 0;
  });

  console.log(
    `[SendScript] Starting to send ${lines.length} lines with ${lineDelay}ms delay...`
  );
  console.log(
    "[SendScript] WARNING: Do not switch conversations while the script is running!"
  );
  console.log(
    "[SendScript] To stop early, close the browser tab or run: window.__sendScriptAbort = true"
  );

  let sent = 0;
  let skipped = 0;

  for (const line of lines) {
    // Check abort flag
    if (window.__sendScriptAbort) {
      console.log(
        `[SendScript] Aborted by user after sending ${sent} lines. Run window.__sendScriptAbort = false to reset.`
      );
      break;
    }

    // Re-acquire the input in case DOM changed
    const currentMain = document.querySelector("#main");
    if (!currentMain) {
      console.warn(
        "[SendScript] Conversation closed mid-send. Attempting to continue..."
      );
      await sleep(lineDelay * 2);
      continue;
    }

    const currentInput = currentMain.querySelector(
      'div[contenteditable="true"]'
    );
    if (!currentInput) {
      console.warn("[SendScript] Input field disappeared. Retrying...");
      await sleep(lineDelay * 2);
      continue;
    }

    // Focus the input
    currentInput.focus();

    // Insert text using execCommand (this is the key trick that works with WhatsApp)
    // execCommand('insertText') simulates typing, which WhatsApp's React handlers accept
    if (document.execCommand("insertText", false, line)) {
      // Dispatch input/change events so WhatsApp's state updates
      currentInput.dispatchEvent(
        new Event("input", { bubbles: true, cancelable: true })
      );
      currentInput.dispatchEvent(
        new Event("change", { bubbles: true, cancelable: true })
      );

      // Wait before clicking send
      await sleep(sendDelay);

      // Click the send button
      const sendButton =
        currentMain.querySelector('[data-testid="send"]') ||
        currentMain.querySelector('[data-icon="send"]');
      if (sendButton) {
        sendButton.click();
        sent++;
      } else {
        // Fallback: try pressing Enter
        console.warn(
          "[SendScript] Send button not found, trying Enter key fallback..."
        );
        currentInput.dispatchEvent(
          new KeyboardEvent("keydown", {
            key: "Enter",
            code: "Enter",
            keyCode: 13,
            which: 13,
            bubbles: true,
          })
        );
        sent++;
      }
    } else {
      // execCommand failed — try the clipboard approach as fallback
      console.warn(
        `[SendScript] execCommand failed for line ${sent + 1}. Trying clipboard fallback...`
      );
      try {
        await navigator.clipboard.writeText(line);
        document.execCommand("paste");
        currentInput.dispatchEvent(
          new Event("input", { bubbles: true, cancelable: true })
        );
        await sleep(sendDelay);

        const sendButton =
          currentMain.querySelector('[data-testid="send"]') ||
          currentMain.querySelector('[data-icon="send"]');
        if (sendButton) {
          sendButton.click();
          sent++;
        }
      } catch (e) {
        console.error(`[SendScript] Fallback also failed for line: "${line.substring(0, 50)}..."`, e);
        skipped++;
      }
    }

    // Wait between lines
    await sleep(lineDelay);
  }

  console.log(
    `[SendScript] Done! Sent ${sent} lines, skipped ${skipped} lines.`
  );
  window.__sendScriptAbort = false;
}

/**
 * Send text as a single message (all lines in one message).
 * Useful when you want to send the entire script as one giant block.
 *
 * @param {string} text - The text to send as a single message.
 * @param {number} chunkSize - Max chars per message (WhatsApp limit ~65536). Default 60000.
 */
async function sendScriptSingle(text, chunkSize = 60000) {
  const main = document.querySelector("#main");
  if (!main) {
    console.error("[SendScript] No conversation is open.");
    return;
  }

  const input = main.querySelector('div[contenteditable="true"]');
  if (!input) {
    console.error("[SendScript] Could not find message input.");
    return;
  }

  // Split into chunks if too long
  const chunks = [];
  for (let i = 0; i < text.length; i += chunkSize) {
    chunks.push(text.substring(i, i + chunkSize));
  }

  console.log(
    `[SendScript] Sending as ${chunks.length} message(s) (chunked at ${chunkSize} chars)...`
  );

  for (const chunk of chunks) {
    input.focus();
    document.execCommand("insertText", false, chunk);
    input.dispatchEvent(
      new Event("input", { bubbles: true, cancelable: true })
    );

    await sleep(100);

    const sendButton =
      main.querySelector('[data-testid="send"]') ||
      main.querySelector('[data-icon="send"]');
    if (sendButton) {
      sendButton.click();
    }

    await sleep(500);
  }

  console.log("[SendScript] All messages sent!");
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// Abort helper — run this in console to stop mid-send
// window.__sendScriptAbort = true;

console.log(
  "%c[SendScript WhatsApp] Ready! Usage:\n" +
    "  sendScript(text, lineDelay=250, sendDelay=100)  — send line-by-line\n" +
    "  sendScriptSingle(text, chunkSize=60000)         — send as one/two big messages\n" +
    "  window.__sendScriptAbort = true                 — abort mid-send",
  "color: #25D366; font-weight: bold; font-size: 14px;"
);
