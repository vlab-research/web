---
title: Shortcodes
weight: 1.5
---

A shortcode is the name a **form** goes by. It is how Fly knows which survey to
start when someone arrives, and it is the thing a recruitment ad, a test link or
a [stitch](/docs/fly/reference/questions/#stitch) refers to.

A shortcode belongs to your Fly account, not to one messaging account: the same
shortcode can be started from any Facebook Page or WhatsApp number you have
connected. So a single form can serve a Messenger arm and a WhatsApp arm of the
same study.

Two things to bear in mind when choosing one:

- **Keep it to letters, digits, `_` and `-`.** Anything else cannot travel in a
  recruitment reference, and a WhatsApp destination will refuse to save.
- **A shortcode is shareable by design.** Anyone who knows it can start that
  survey by sending `form.<shortcode>` to your WhatsApp number, or by opening
  `m.me/<page>?ref=form.<shortcode>`. That is what makes testing easy; it also
  means a shortcode is not a secret.
