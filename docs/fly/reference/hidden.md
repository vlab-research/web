---
title: Hidden Fields
weight: 6
---

## What a respondent arrives with

Every respondent carries a set of hidden fields from the moment their
conversation starts. Some come from the link or ad that brought them; the rest
Fly sets itself.

| Hidden field | Where it comes from |
|---|---|
| `form` | The shortcode in the reference they arrived with. |
| *anything else in the reference* | The `key.value` pairs after the shortcode — `creative`, `gender`, whatever your ad carries. |
| `platform` | The channel: `messenger` or `whatsapp`. Fly sets this. |
| `pageid` | The messaging account they arrived on — a Facebook page id, or a WhatsApp number's id. Fly sets this. |
| `startTime` | When the conversation started. Fly sets this. |
| `seed` | The respondent's random seed. See [Randomization](/docs/fly/reference/seeds/). |
| `ad_id` | The id of the ad they clicked, when the platform told us. Fly sets this; it is not available for every arrival. |
| `vt` | The opaque attribution token, when the ad carried one. Fly sets this. See [what an ad's ref carries](/docs/vlab/study-configuration/destination/#what-an-ads-ref-carries). |
| `e_*` | Values delivered by external events — payment results, and metadata handed back by another app after a [handoff](/docs/fly/reference/questions/#passing-thread-control-handoff). |

You can read any of them in a question with `{{hidden:name}}`, and branch on any
of them with a Typeform logic jump.

::: note

**`vt` and `ad_id` belong to Fly and cannot be set from a link.** If a reference
contains `vt.something` or `ad_id.something`, that value is discarded rather than
used — otherwise anyone who could edit a link could attach a respondent to
somebody else's ad. On WhatsApp, where the reference is the respondent's own
editable message, this matters.
:::

## Long hidden fields

Sometimes we surface hidden fields that are too long to be added as hidden fields in Typeform. These can be accessed in the text of a question/statement using the following syntax:

```
{{hidden:e_payment_http_result_message_success}}
```

Where the "too long" hidden field is `e_payment_http_result_message_success` which would be populated, for example, if you had a http payment result that looked like this: `{"message": {"success": "foo"}}` and you wanted to show "foo".

## Interpolation

Fly supports mustache-style interpolation in question titles and descriptions. You can reference:

- **Hidden fields**: `{{hidden:field_name}}` — metadata from the user, referral params, or payment results
- **Previous answers**: `{{field:question_ref}}` — the raw answer to a previous question

### Interpolation Transforms

You can apply transforms to interpolated values using pipe syntax:

```
{{field:phone|e164}}
```

This looks up the answer to the `phone` question, then applies the `e164` transform to normalize it. Transforms are applied left-to-right, so chaining is possible:

```
{{field:phone|e164|lower}}
```

#### Available Transforms

| Transform | Description |
|-----------|-------------|
| `e164` | Normalizes a phone number to E.164 format (e.g. `+254712345678`). Strips trailing text and validates using the `phone` library. If the value cannot be normalized, the raw value is returned unchanged. |

#### Why `|e164` matters for payments

When a user answers a phone number question, their response may include trailing text — for example `+254712345678 use this` instead of just `+254712345678`. The raw answer is preserved as-is in the survey data, which is important for the audit trail.

However, payment providers require a clean E.164 phone number. Without the `|e164` transform, the messy raw value would be sent directly to the provider, which can cause:

1. **Payment failures** — the provider rejects the malformed number
2. **Duplicate payments** — two submissions of the same number with different trailing text produce different `custom_identifier` values, bypassing duplicate detection

To avoid these issues, always use `|e164` when referencing phone fields in payment details:

```json
"details": {
    "mobile": "{{field:phone|e164}}",
    "custom_identifier": "survey_x_{{field:phone|e164}}_1"
}
```

Without the transform, `{{field:phone}}` resolves to the raw stored value (e.g. `+254712345678 use this`). With `|e164`, it resolves to the normalized E.164 number (`+254712345678`).
