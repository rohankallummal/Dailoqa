"use client";

import { useState } from "react";
import { Tag, X } from "lucide-react";

const MAX_TAGS = 20;

export function IdentityTab({
  name,
  onNameChange,
  description,
  onDescriptionChange,
  tags,
  onTagsChange,
}: {
  name: string;
  onNameChange: (value: string) => void;
  description: string;
  onDescriptionChange: (value: string) => void;
  tags: string[];
  onTagsChange: (tags: string[]) => void;
}) {
  const [tagDraft, setTagDraft] = useState("");

  function addTag() {
    const value = tagDraft.trim();
    if (!value || tags.includes(value) || tags.length >= MAX_TAGS) {
      setTagDraft("");
      return;
    }
    onTagsChange([...tags, value]);
    setTagDraft("");
  }

  function removeTag(tag: string) {
    onTagsChange(tags.filter((t) => t !== tag));
  }

  return (
    <div className="rounded-xl border border-line bg-white p-6">
      <p className="text-xs font-semibold tracking-wide text-ink-muted">
        IDENTITY
      </p>

      <div className="mt-5 flex flex-col gap-1.5">
        <label htmlFor="pb-name" className="text-sm font-medium text-ink">
          Name
        </label>
        <input
          id="pb-name"
          value={name}
          onChange={(event) => onNameChange(event.target.value)}
          placeholder="e.g. Customer Research Pipeline"
          className="w-full rounded-lg border border-line bg-page px-3 py-2.5 text-sm text-ink outline-none transition-colors focus:border-accent placeholder:text-ink-muted"
        />
      </div>

      <div className="mt-5 flex flex-col gap-1.5">
        <label htmlFor="pb-desc" className="text-sm font-medium text-ink">
          Description
        </label>
        <textarea
          id="pb-desc"
          value={description}
          onChange={(event) => onDescriptionChange(event.target.value)}
          rows={4}
          placeholder="What does this playbook accomplish?"
          className="w-full resize-y rounded-lg border border-line bg-page px-3 py-2.5 text-sm text-ink outline-none transition-colors focus:border-accent placeholder:text-ink-muted"
        />
      </div>

      <div className="mt-5 flex flex-col gap-2">
        <label className="text-sm font-medium text-ink">Tags</label>
        <div className="flex flex-wrap items-center gap-2">
          {tags.map((tag) => (
            <span
              key={tag}
              className="inline-flex items-center gap-1 rounded-full bg-active px-2.5 py-1 text-xs font-medium text-accent"
            >
              {tag}
              <button
                type="button"
                onClick={() => removeTag(tag)}
                aria-label={`Remove ${tag}`}
                className="transition-opacity hover:opacity-70"
              >
                <X className="h-3 w-3" />
              </button>
            </span>
          ))}
          <div className="inline-flex items-center gap-1.5 rounded-full border border-dashed border-line px-2.5 py-1">
            <Tag className="h-3.5 w-3.5 text-ink-muted" />
            <input
              value={tagDraft}
              onChange={(event) => setTagDraft(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  event.preventDefault();
                  addTag();
                }
              }}
              onBlur={addTag}
              placeholder="Add tag"
              disabled={tags.length >= MAX_TAGS}
              className="w-20 bg-transparent text-xs text-ink outline-none placeholder:text-ink-muted disabled:cursor-not-allowed"
            />
          </div>
        </div>
        <p className="text-xs text-ink-muted">{tags.length}/{MAX_TAGS} tags</p>
      </div>
    </div>
  );
}
