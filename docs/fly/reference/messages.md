---
title: Messages
weight: 6
---

Fly sends a handful of its own messages that are not questions: what a
respondent gets when their answer is rejected, when they write in while the
survey is paused, and when they arrive after the survey has closed. All of them
can be rewritten — which matters most when your survey is not in English.

## Where you set them

**In Typeform, not in the Fly dashboard.** Open the form in Typeform and edit
its custom messages (under the form's language and messages settings). Fly reads
them when you import the form, so **re-import the form after changing them**.

You only need to set the ones you want to change; anything you leave alone keeps
its default English wording.

## The messages Fly uses

| Message key | When it is sent | Default |
|---|---|---|
| `label.error.mustSelect` | The respondent typed something instead of tapping one of the options — Multiple Choice, Yes/No, Legal, scales. | "Sorry, please use the buttons provided to answer the question." |
| `label.error.mustEnter` | A free-text or Date answer could not be accepted. Also the fallback for anything with no more specific message. | "Sorry, that answer is not valid. Please try to answer the question again." |
| `label.error.range` | A Number question got something that is not a number, or a number outside its `min`/`max`/`integer` rule. | "Sorry, please enter a valid number." |
| `label.error.emailAddress` | An Email question got something that is not an email address. | "Sorry, please enter a valid email address." |
| `label.error.phoneNumber` | A Phone Number question got something that is not a dialable number. | "Sorry, please enter a valid phone number." |
| `block.shortText.placeholder` | The respondent wrote in while the survey was paused on a statement, a wait, or a link — and that question has no `responseMessage` of its own. | "Sorry, I can't accept any responses now." |
| `label.buttonHint.default` | The friendly nudge sent to a respondent who has gone quiet. | "Hello, we just wanted to send a friendly follow up. If you would like to stop the survey, just ignore this message and we won't bother you again." |
| `label.error.mustAccept` | Anyone who writes in after the survey's End Time has passed. | "We're sorry, but this survey is now over and closed." |

::: warning

**One message is set per question, not here.** `responseMessage` — what a
respondent gets if they write in instead of tapping a link, watching a video, or
waiting — is written in that question's own Description box. See
[Question Types](/docs/fly/reference/questions/). Where a question sets
`responseMessage`, it is used in place of `block.shortText.placeholder`.
:::

## Survey over

The message sent to everyone who writes to the chatbot after the survey's End
Time is `label.error.mustAccept`. Set the End Time itself under
[Form Settings](/docs/fly/reference/settings/).
