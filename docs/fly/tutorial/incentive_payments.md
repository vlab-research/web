---
title: "Incentive Payment Tutorial: Tremendous"
weight: 5
---

We will assume you are starting with a form in Typeform as per the Quickstart.

## Create hidden fields

First, update your form, adding several [hidden fields](https://www.typeform.com/help/a/using-hidden-fields-360052676612/):

1. e_payment_http_success
2. e_payment_http_response
3. e_payment_http_error_message

That should look like this:

![](/docs/images/typeform-form-hidden-fields-for-payment.png)

---

## Update the form with questions

Second, update your survey in Typeform to have the following questions:

| Question Type   | Text                                                                                                 | Answers              |
|-----------------|------------------------------------------------------------------------------------------------------|----------------------|
| Multiple Choice | Which do you prefer:                                                                                 | A) Mountain B) Ocean |
| Statement       | That's cool!                                                                                         |                      |
| Multiple Choice | Thanks. You have now qualified for a big payment.”                                                   | A) OK                |
| Statement       | Please wait. We are creating a gift card for you and will provide it to you in the next few minutes. |                      |
| Statement       | We're sorry, your payment has failed with: @e_payment_http_error_message                             |                      |
| Statement       | It worked! Find your gift card here: @e_payment_http_response                                        |                      |
| Ending          | Thanks, that was a great chat.                                                                       |                      |

Note that the `@` symbol should cause Typeform to prompt you to select from your hidden fields.

---

## Adding the "Fly code" to the Typeform

Copy the example JSON from the [Tremendous Payment Reference](/docs/fly/reference/incentive_payments/) and place it in the description of the statement that beings with "Please wait. We are creating a gift card...". NOTE: you don't need to follow the instructions to replace any of the variables just yet, or perform anything else under that documentation. We will do that at the end.

![](/docs/images/typeform-payment-tremendous-json.png)

---

## Final form

Your Typeform should now look like this:

![](/docs/images/typeform-form-for-payment.png)

---

## Adding Logic - Step 1

Now go over to the logic and create some logic jumps. The first jump:

1. After the "Please wait..." statement, add logic that moves to "It worked!" if `e_payment_http_success` is equal to `true` and moves to "We're sorry..." otherwise:

![](/docs/images/typeform-payment-logic-1.png)

---

## Adding Logic - Step 2

Now the second jump:

2. After the "We're sorry..." statement, add logic that always goes back to "Thanks. You have now qualified..."

You'll realize that it's important to have this Multiple Choice question because we want to user input before trying again. Otherwise, on any error, it will loop infinitely without user input, which would create a very annoying user experience!

Your logic should now look like this:

![](/docs/images/typeform-payment-logic-2.png)

---

## Publish and Test

Use the follow steps to test out your payment flow:

1. Publish the form on Typeform.
2. Create a new form in fly.vlab.digital (it can be under the same Survey Name if you wish).
3. Test it out.

![](/docs/images/fly-tutorial-created-pay-form.png)

---

## Add the Tremendous information

Your form should work in Messenger, however, you should notice that you get an error! There are multiple things wrong:

1. You probably don't have a Generic Secret called `TREMENDOUS_API_KEY`, which is what that example code expects.
2. You need to replace the variables `your_funding_source_id` and `product_id_that_you_want` with the correct IDs from Tremendous.

Now, return to the [Tremendous Payment Reference](/docs/fly/reference/incentive_payments/#payment---tremendous) documentation and fix the two problems. After you do that, you should be able to test out the survey with a paid gift card!

Congrats, you have now paid your study participants.
