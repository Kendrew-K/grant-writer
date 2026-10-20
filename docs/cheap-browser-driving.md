# Codex compatibility

The tool names and JavaScript examples below describe Claude in Chrome.
For Codex, follow `codex.md` and the active browser tool's documented APIs.
Retain the call budget, dedicated-tab rule and recovery limits, but do not
assume these payloads are supported or permitted in another browser tool.

# Cheap browser driving

How to drive Claude in Chrome while filling a grant portal without burning credit.
Referenced from [`apply-playbook.md`](apply-playbook.md) step 7. Written for a job-application
project and carried over; the portals differ but the cost model and payloads do not.

## Why this exists

Cost of a browser session is roughly **O(N^2) in tool-call count**, not
linear. Two reasons:

- A `computer` screenshot costs `width * height / 750` tokens — about 1,400
  for a 1280x800 viewport.
- Every tool call resends the whole conversation. By call 80 the context
  holds 80 screenshots (~110k tokens) and re-reads them every turn.

So the lever is **call count, not call cost**. Driving a Workday form with
~100 screenshot-and-click calls versus ~8 JavaScript calls is roughly a 100x
difference, not a 12x one.

## Rules

1. **Never screenshot to fill a form.** Screenshots are for one thing: the
   final review screen, so the user can see what they are about to submit.
2. **Read with `get_page_text`, not `read_page`.** The accessibility tree
   `read_page` returns runs 5-20k tokens on Workday. Page text is a fraction
   of that.
3. **Fill with `javascript_tool`.** One call to dump the fields, one call to
   set them. Not one call per field.
4. **Chain with `browser_batch`** when several actions must happen in order
   (click Next, wait, dump next page) so they cost one round-trip.
5. **Click by selector, not by coordinate.** Coordinate clicking needs a
   screenshot to aim; selector clicking does not.

## Payload 1: dump the form

Run via `javascript_tool`. Returns compact JSON of every visible, enabled,
unfilled field. Skips hidden and already-populated ones so the output stays
small.

```js
(() => {
  const label = (el) => {
    const id = el.id && document.querySelector('label[for="' + CSS.escape(el.id) + '"]');
    return (
      el.getAttribute('data-automation-id') ||
      (id && id.innerText.trim()) ||
      el.getAttribute('aria-label') ||
      (el.getAttribute('aria-labelledby') &&
        (document.getElementById(el.getAttribute('aria-labelledby')) || {}).innerText) ||
      (el.closest('label') && el.closest('label').innerText.trim()) ||
      el.placeholder || el.name || el.id || ''
    ).toString().trim().slice(0, 80);
  };
  const sel = (el) =>
    el.getAttribute('data-automation-id')
      ? '[data-automation-id="' + el.getAttribute('data-automation-id') + '"]'
      : el.id ? '#' + CSS.escape(el.id)
      : el.name ? '[name="' + CSS.escape(el.name) + '"]' : null;

  return JSON.stringify(
    [...document.querySelectorAll('input,select,textarea')]
      .filter((el) => {
        if (el.disabled || el.type === 'hidden') return false;
        if (!el.offsetParent && el.type !== 'file') return false;
        if (el.value && el.type !== 'file') return false;
        return true;
      })
      .map((el) => ({
        s: sel(el),
        l: label(el),
        t: el.type || el.tagName.toLowerCase(),
        req: el.required || el.getAttribute('aria-required') === 'true' || undefined,
        opts: el.tagName === 'SELECT'
          ? [...el.options].map((o) => o.text.trim()).slice(0, 40)
          : undefined,
      }))
      .filter((f) => f.s)
  );
})()
```

## Payload 2: set the fields

Setting `el.value` directly does **not** fire React's `onChange`. Submittable,
SmartSimple and most modern grant portals are React apps, so a direct assignment looks filled
on screen and submits empty. Use the native setter plus dispatched events:

```js
((data) => {
  const native = (el) => {
    const proto = el instanceof HTMLTextAreaElement
      ? HTMLTextAreaElement.prototype
      : el instanceof HTMLSelectElement
      ? HTMLSelectElement.prototype
      : HTMLInputElement.prototype;
    return Object.getOwnPropertyDescriptor(proto, 'value').set;
  };
  const out = [];
  for (const [s, v] of Object.entries(data)) {
    const el = document.querySelector(s);
    if (!el) { out.push([s, 'MISSING']); continue; }
    if (el.type === 'checkbox' || el.type === 'radio') {
      if (el.checked !== !!v) el.click();
    } else {
      native(el).call(el, v);
      el.dispatchEvent(new Event('input', { bubbles: true }));
      el.dispatchEvent(new Event('change', { bubbles: true }));
      el.dispatchEvent(new Event('blur', { bubbles: true }));
    }
    out.push([s, 'ok']);
  }
  return JSON.stringify(out);
})({
  "#org_name": "Riverside Youth Symphony",
  "#email": "..."
})
```

Read the returned array. Anything marked `MISSING` means the selector went
stale (the page re-rendered) — re-run payload 1 rather than guessing.

## Gotchas found in practice (Cresta/Greenhouse, 2026-09-13)

- **Never wrap a payload in `async (() => {...})()`.** The tool serializes the
  returned Promise as `{}` and you lose the result with no error. Top-level
  `await` works directly — write the bare expression last and let it return.
  Two calls were wasted on this before it was spotted.
- **Normalize before comparing.** A phone input reformats `(555) 555-0100` to
  `5555550100` on input and back on blur, so a strict `el.value === v` check
  reports `SET-FAILED` on a field that was set correctly. Compare on
  `String(v).replace(/\D/g,'')` for tel fields, or just re-read and eyeball.
- **Combobox widgets (react-select, intl-tel-input) ignore synthetic events.**
  Dispatching `mousedown`/`click`/`Enter` opens the menu and filters it, but
  the selection never commits — React only honours a trusted event here. Set
  the input text with the native setter, then fire one real
  `computer` `key` `Return`. That is a keystroke, not a screenshot, so it stays
  cheap. Budget two attempts, then leave the field for the user if optional.
- **`computer` `scroll` returns a screenshot on every call.** Scroll with
  `scrollTop` on the container from `javascript_tool` when you only need
  position; use `computer` scroll only when you actually want the picture.
- **File uploads work.** `file_upload` with an absolute path and a `find` ref
  attaches the PDF directly, no OS dialog. Asking the user to drag the file in
  is the fallback, not the default: try `file_upload` first.
- **Some forms swap the file input out after upload** (Greenhouse did), so the
  input reads `MISSING` on a re-dump. That is success, not failure. Confirm by matching
  `/[\w\-.]+\.pdf/` against the form's `innerText`.

- **A filled form is not safe in a tab you did not create.** Claude in Chrome
  drives the user's real browser, and the user browses in it at the same time.
  A completed Cresta form was lost when that tab got navigated away mid-run.
  Always `tabs_create_mcp` a fresh tab per grant, re-verify the tab's URL
  right before handing off, and never `navigate` a tab you did not open. A
  refill is cheap under this approach (about 7 calls, no screenshots), so
  re-do it rather than guessing whether the state survived.

## Rich text answer boxes (common on grant portals)

Long narrative questions are often a rich text editor (TinyMCE, CKEditor, Quill)
rather than a `<textarea>`, so payload 1 does not list them and payload 2 cannot
set them. Probe once:

```js
JSON.stringify({
  tinymce: !!window.tinymce && tinymce.editors.map((e) => e.id),
  ckeditor: !!window.CKEDITOR && Object.keys(CKEDITOR.instances),
  editable: [...document.querySelectorAll('[contenteditable="true"]')].length,
})
```

Then set the text with the editor's own API, which also updates the portal's
character counter:

- TinyMCE: `tinymce.get('<id>').setContent('<p>answer</p>'); tinymce.get('<id>').fire('change')`
- CKEditor 4: `CKEDITOR.instances['<name>'].setData('<p>answer</p>')`
- Plain `contenteditable` (Quill and others): focus the element, then
  `document.execCommand('insertText', false, text)`. It is deprecated but it is
  the one call that goes through the editor's own input handling.

Re-read the portal's character counter afterwards. If it disagrees with your
own count, trust the portal and trim.
