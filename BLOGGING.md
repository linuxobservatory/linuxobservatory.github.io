# Writing your Linux Observatory blog

The blog lives at https://linuxobservatory.github.io/blog/.

## Publish with ChatGPT

Send your text and ask: “Publish this as a blog post on Linux Observatory.” Include the title and any images. Ask for a draft first if you want to review it before publication.

## Publish yourself on GitHub

1. Sign in to GitHub and open this repository’s `_posts` folder.
2. Choose **Add file → Create new file**.
3. Name it `YYYY-MM-DD-your-post-title.md`, using the publication date (for example `2026-11-11-a-new-observation.md`).
4. Copy the front matter below, then write your post underneath it.
5. Commit to `main`. GitHub Pages builds and publishes the post automatically, usually within a few minutes.

```markdown
---
title: "Your post title"
description: "A short description of your post."
tags: [Linux, Personal]
---
Your opening paragraph goes here.

## A section heading

Write naturally. **Bold**, *italics*, lists and links work.
```

The post gets a dated URL. The blog index lists newest posts first; RSS and the XML sitemap update automatically. The layout supplies your name and publication date. You do not need to edit HTML, navigation, RSS or sitemap files for each post.

## Images and videos

Upload images to `assets/blog/`, then insert `![Description of the image](/assets/blog/filename.webp)`. Use a descriptive alt text and suitably sized images. Link to videos using `[Watch the recording](https://www.youtube.com/watch?v=VIDEO_ID)`.

## Drafts and edits

Use `_drafts/post-template.md` as a starting point. Files in `_drafts` do not appear on the website. **This is a public repository: draft files are visible on GitHub.** Keep private drafts outside this repository.

To publish a draft, move it to `_posts` with a date-prefixed filename, replace all placeholder text, and commit. To keep a file in `_posts` unpublished, add `published: false` to its front matter; remove it when ready.

To edit a live post, edit its Markdown file and commit. Keep the filename unchanged to preserve its URL. For a title containing a colon or quotation marks, keep valid YAML quoting (double quotes must be escaped inside a double-quoted title).

Future-dated posts are not published until a site build occurs on or after that date. This is not an automatic scheduling system.

## Scope

GitHub handles author sign-in and editing. The public website has no separate admin login or comments system. This keeps it simple, fast and compatible with the existing GitHub Pages hosting.
