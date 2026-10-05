"use client";

import { useState } from "react";

export default function CopyBox({ text, copyLabel, copiedLabel }: {
  text: string; copyLabel: string; copiedLabel: string;
}) {
  const [copied, setCopied] = useState(false);
  return (
    <div className="copybox">
      <code>{text}</code>
      <button
        type="button"
        onClick={() => {
          navigator.clipboard?.writeText(text).then(() => {
            setCopied(true);
            setTimeout(() => setCopied(false), 1600);
          });
        }}
      >
        {copied ? copiedLabel : copyLabel}
      </button>
    </div>
  );
}
