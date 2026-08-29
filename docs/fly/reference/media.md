---
title: Media Library
weight: 4.5
---

The **Media** tab in the dashboard is where you upload the images, videos, audio
and documents your survey sends to respondents. You upload a file, you copy the
URL it gives you back, and you paste that URL into your survey. That is the whole
feature.

The URLs it produces work on **every channel Fly supports** — WhatsApp and
Messenger — with no per-channel setup and no per-channel copy of the file.

## Uploading a file

1. Open **Media** in the dashboard navigation.
2. Drag a file onto the upload box (or click it to pick one).
3. The file appears in the list below with a **URL** next to it. Click the URL to
   copy it.
4. Paste that URL into the `url` field of an attachment question. See
   [Question Types](/docs/fly/reference/questions/#attachments-image-video-audio-document)
   for the JSON.

The URL looks like this:

```
https://media.vlab.digital/a/550e8400-e29b-41d4-a716-446655440000/welcome.png
```

**You do not need a connected Facebook page or WhatsApp number to upload.** You
can build your whole survey's media library before you connect any account at
all.

If you upload the same file twice, you get the same entry back rather than a
duplicate — the library tells you it was already there and shows you its
existing URL.

## Supported formats and size limits

A file is accepted only if it is one of the formats below. Limits are the
strictest of any platform we send on, so **anything the library accepts is
guaranteed to send on WhatsApp and Messenger alike**.

| Kind | Formats accepted | Maximum size |
|---|---|---|
| Image | JPEG, PNG | 5 MB |
| Video | MP4, 3GPP | 16 MB |
| Audio | AAC, M4A, MP3, AMR, OGG | 16 MB |
| Document | PDF, DOCX, XLSX, PPTX | 100 MB |

Some formats you might expect are **deliberately not accepted**:

- **GIF and WebP images** — not supported across all the messaging platforms we
  send on. Convert to PNG or JPEG, or to MP4 for an animation.
- **Plain text files (`.txt`), `.doc`, `.xls`, `.ppt`** — send a PDF or the
  modern Office format (`.docx`, `.xlsx`, `.pptx`) instead.

We never resize, transcode or convert your files. If a file is refused, the
error tells you exactly why — fix the file and upload it again.

::: note

We check what a file **actually is**, not what it is named. Renaming a `.gif` to
`.png` will not get it accepted, and a correctly-formatted file with a missing or
wrong extension will still be accepted for what it is.
:::

## Who can see these files

::: warning

**Anyone with the link can open the file, forever.** These URLs are not listed
anywhere and cannot be guessed, but they are not password-protected: anyone you
send one to — or anyone it is forwarded to — can open the file, indefinitely.

Do not upload anything confidential. Media meant for respondents to receive is
exactly the right thing to put here.
:::

There is also **no delete button**. A survey can reference an asset by URL, and
deleting the file would silently break every live survey pointing at it. If you
need something removed, contact us and we will handle it.

## Filenames matter for documents

The filename is part of the URL, and on WhatsApp it is **what the respondent sees
when a document arrives**. Upload `consent-form-2026.pdf` and that is the name
in their chat; upload `final_v3_FINAL.pdf` and that is what they get.

Name documents the way you want respondents to read them, before you upload.

For images, video and audio the filename is cosmetic.

## Using a URL from somewhere else

You can still point an attachment question at any public URL you control instead
of uploading:

```json
{"type": "attachment",
 "keepMoving": true,
 "attachment": {
    "type": "image",
    "url": "https://example.org/my-image.png"
 }
}
```

That works, with three conditions you own rather than us:

- It must be **HTTPS** and publicly reachable — no login, no IP allowlist.
- It must **stay** reachable for the life of the survey. If it moves or 404s,
  respondents get nothing.
- It must be within the format and size limits above, which we cannot check for
  you in advance — a file that is too large fails at send time, per respondent,
  rather than at upload time, once.

Media uploaded to the library avoids all three problems, and sends measurably
faster (see below). Prefer it.

## What happens behind the scenes

You do not need to know any of this to use the feature — it is here so the
behaviour is not mysterious.

When you upload a file, Fly stores it and then, in the background, pre-uploads a
copy to every messaging account you have connected — each WhatsApp number, each
Facebook page. When your survey sends that media, we send the pre-uploaded copy
by reference rather than making the platform fetch your URL, which is faster and
far less likely to fail.

Consequences worth knowing:

- **You never configure this.** There is no platform selector and no per-account
  upload step. Connect an account later and the pre-uploads happen on their own,
  usually within the hour.
- **It cannot break your survey.** If a pre-upload has not happened yet, or has
  expired, or fails outright, we fall back to sending your URL. The message still
  goes out.
- **The same JSON works everywhere.** One `url` in your survey covers every
  channel and every account.

One thing does differ by channel: on WhatsApp the question's title is sent as the
attachment's **caption**, and a document's **filename** is what the respondent
sees. On Messenger neither is shown. See
[Channels](/docs/fly/reference/channels/#captions-on-attachments).

::: note

**If you have used `attachment_id` before:** that was the old way of referencing
a file pre-uploaded to a specific Facebook page. It still works on Messenger for
surveys that already use it, but it does nothing on WhatsApp and should not be
used in new surveys. Upload the file to the Media library and use its URL
instead — you get the same speed benefit, on every platform, with no manual
step.
:::
