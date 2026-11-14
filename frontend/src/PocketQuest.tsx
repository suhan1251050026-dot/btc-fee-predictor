import { useEffect, useState } from "react";

/**
 * Slot for ThreeUI's Pocket Quest landing page (a ThreeUI *Pro* component).
 * Its official wrapper renders `/landing-pages/pocket-quest.html` in a sandboxed iframe;
 * this does the same. The page and its ~70 files are installed by the ThreeUI CLI with a
 * Pro account. Nothing here recreates or imitates it: if the files are absent we say so.
 */
const SRC = "/landing-pages/pocket-quest.html";

export default function PocketQuest() {
  const [state, setState] = useState<"checking" | "ready" | "missing">("checking");
  useEffect(() => {
    // Vite's dev server answers unknown paths with index.html, so check for the page's own markup.
    fetch(SRC, { cache: "no-store" })
      .then((r) => (r.ok ? r.text() : ""))
      .then((html) => setState(html.includes('id="pq-game"') ? "ready" : "missing"))
      .catch(() => setState("missing"));
  }, []);

  return (
    <section className="section" id="play" aria-labelledby="play-title">
      <div className="wrap">
        <div className="sec-head reveal">
          <span className="sec-no">03</span>
          <h2 id="play-title" className="display">Take a break</h2>
          <p>Pocket Quest by ThreeUI: a thirty-second memory game with six heroes, embedded with its original shaders, artwork and demo.</p>
        </div>
        {state === "ready" && (
          <div className="pq-frame reveal">
            <iframe src={SRC} title="Pocket Quest" loading="lazy" sandbox="allow-scripts allow-forms" />
          </div>
        )}
        {state === "checking" && <div className="skeleton" style={{ minHeight: 420 }} />}
        {state === "missing" && (
          <div className="panel pq-missing reveal" role="status">
            <div>
              <h3 className="display" style={{ margin: "0 0 12px", fontSize: "clamp(1.6rem,3vw,2.4rem)" }}>Pocket Quest isn't installed yet</h3>
              <p className="muted" style={{ marginTop: 0 }}>
                Pocket Quest is a ThreeUI <b>Pro</b> component. Its source and its 42 artwork and font files are only distributed to signed-in Pro members,
                so they can't ship inside this project. Once installed, it appears here automatically. No code changes needed.
              </p>
            </div>
            <div>
              <ol>
                <li>Have an active <b>ThreeUI Pro</b> membership (threeui.com/pricing).</li>
                <li>In the <b>frontend</b> folder, run the official CLI and sign in when the browser opens:</li>
              </ol>
              <pre className="code">npx @designcodeio/threeui-cli add pocket-quest-landing-page</pre>
              <ol start={3} style={{ marginTop: 14 }}>
                <li>Make sure the files land in <b>frontend/public/landing-pages/</b> (<b>pocket-quest.html</b> plus the <b>aura-2026-10-20-assets</b> folder), then rebuild.</li>
              </ol>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
