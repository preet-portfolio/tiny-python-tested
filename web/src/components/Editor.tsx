"use client";

import { useEffect, useRef } from "react";
import { EditorView, basicSetup } from "codemirror";
import { python } from "@codemirror/lang-python";
import { EditorState, StateEffect, StateField } from "@codemirror/state";
import { Decoration, type DecorationSet, keymap } from "@codemirror/view";
import { HighlightStyle, syntaxHighlighting } from "@codemirror/language";
import { tags as t } from "@lezer/highlight";

const highlight = HighlightStyle.define([
  { tag: t.keyword, color: "var(--code-keyword)", fontWeight: "600" },
  { tag: [t.string, t.special(t.string)], color: "var(--code-string)" },
  { tag: t.comment, color: "var(--code-comment)", fontStyle: "italic" },
  { tag: [t.number, t.bool, t.null], color: "var(--code-number)" },
  { tag: [t.function(t.variableName), t.definition(t.variableName)], color: "var(--code-def)" },
]);

const theme = EditorView.theme({
  "&": { backgroundColor: "var(--surface)", color: "var(--ink)", height: "100%" },
  ".cm-content": { fontFamily: "var(--font-mono)", fontSize: "14px", caretColor: "var(--ink)" },
  ".cm-gutters": {
    backgroundColor: "var(--surface)",
    color: "var(--muted)",
    borderRight: "1px solid var(--rule)",
  },
  ".cm-activeLine, .cm-activeLineGutter": { backgroundColor: "var(--active-line)" },
  "&.cm-focused": { outline: "none" },
  ".cm-selectionBackground, &.cm-focused .cm-selectionBackground": {
    backgroundColor: "var(--selection) !important",
  },
  ".cm-mutant-line": { backgroundColor: "var(--mutant-wash)" },
});

const setMarked = StateEffect.define<number | null>();
const markedLine = StateField.define<DecorationSet>({
  create: () => Decoration.none,
  update(deco, tr) {
    for (const e of tr.effects) {
      if (e.is(setMarked)) {
        if (e.value == null || e.value < 1 || e.value > tr.state.doc.lines) return Decoration.none;
        const line = tr.state.doc.line(e.value);
        return Decoration.set([Decoration.line({ class: "cm-mutant-line" }).range(line.from)]);
      }
    }
    return deco.map(tr.changes);
  },
  provide: (f) => EditorView.decorations.from(f),
});

type Props = {
  value: string;
  onChange: (v: string) => void;
  onRun: () => void;
  markLine?: number | null;
  label: string;
};

export function Editor({ value, onChange, onRun, markLine, label }: Props) {
  const host = useRef<HTMLDivElement>(null);
  const view = useRef<EditorView | null>(null);
  const cb = useRef({ onChange, onRun });
  cb.current = { onChange, onRun };

  useEffect(() => {
    if (!host.current) return;
    const v = new EditorView({
      parent: host.current,
      state: EditorState.create({
        doc: value,
        extensions: [
          keymap.of([
            { key: "Mod-Enter", run: () => (cb.current.onRun(), true) },
          ]),
          basicSetup,
          python(),
          syntaxHighlighting(highlight),
          theme,
          markedLine,
          EditorView.contentAttributes.of({ "aria-label": label }),
          EditorView.updateListener.of((u) => {
            if (u.docChanged) cb.current.onChange(u.state.doc.toString());
          }),
        ],
      }),
    });
    view.current = v;
    return () => v.destroy();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const v = view.current;
    if (v && v.state.doc.toString() !== value) {
      v.dispatch({ changes: { from: 0, to: v.state.doc.length, insert: value } });
    }
  }, [value]);

  useEffect(() => {
    const v = view.current;
    if (!v) return;
    v.dispatch({ effects: setMarked.of(markLine ?? null) });
    if (markLine && markLine <= v.state.doc.lines) {
      v.dispatch({ effects: EditorView.scrollIntoView(v.state.doc.line(markLine).from, { y: "center" }) });
    }
  }, [markLine]);

  return <div className="editor" ref={host} />;
}
