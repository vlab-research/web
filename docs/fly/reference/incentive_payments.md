---
title: Incentive Payments
weight: 9
---

A payment question pauses the survey, sends the payment, and picks the survey
back up when the provider answers.

::: warning

**A payment result that comes back more than 24 hours later cannot be delivered
as an ordinary message**, on either channel. Most results are immediate and this
never arises — but a provider that is slow, retried, or down overnight can push
the reply outside the 24-hour messaging window, after which only an approved
template sends.

If a study pays after a wait, make the message that follows the payment a
[Utility Message](/docs/fly/reference/questions/#utility-message), or accept that a
minority of respondents will hear nothing back. See
[Timeouts](/docs/fly/reference/timeouts/#timeouts-over-24-hours).
:::

## Payment - Reloadly

JSON:
``` json
{
    "type": "wait",
    "wait": {
        "type": "external",
        "value": {
            "type": "payment:reloadly",
            "id": "PAYMENT_ID"
        }
    },
    "payment": {
        "provider": "reloadly",
        "key": "name-of-your-credentials",
        "details": {
            "mobile": "{{field:MOBILE_QUESTION|e164}}",
            "operator": @OPERATOR_QUESTION,
            "amount": 100,
            "tolerance": 30,
            "country": "IN",
            "id": "PAYMENT_ID",
            "custom_identifier": "survey_x_{{field:MOBILE_QUESTION|e164}}_1",
        }
    }
}
```

Notes:

1. The "wait" is not strictly necessary but likely desired!
2. `PAYMENT_ID` can be useful to keep track of multiple payments to the same person or different payments to different treatment arms (a unique id per treatment arm). You need to have the same PAYMENT_ID for both the "wait" and the "payment" blocks.
3. the `key` is the name you give the desired Reloadly credentials in the Fly dashboard.
4. `CUSTOM_IDENTIFIER` is a unique string that ensures that no payment is repeated. For example, if you only want to provide a payment to each phone once, you can make this a combination of the shortcode and the phone number.
5. Phone number answers may contain trailing text (e.g. `+254712345678 use this`). Use the `|e164` transform to normalize phone numbers to E.164 format before they reach the payment provider. This is especially important for `custom_identifier` — without normalization, two submissions of the same number with different trailing text produce different identifiers, breaking duplicate payment detection. See [Interpolation Transforms](/docs/fly/reference/hidden/#interpolation-transforms) for details.

You will have the following hidden fields that can be used for logic and error messages:

1. `e_payment_reloadly_success` - will be "true" if the payment succeeded.
2. `e_payment_reloadly_error_message` - an error message, in english, of why the payment failed.
3. `e_payment_reloadly_id` - the PAYMENT_ID

## Payment - DingConnect

[DingConnect](https://www.dingconnect.com) sends mobile airtime, data bundles, and
utility top-ups in most countries. Unlike Tremendous, it is a native provider, so
Fly maps its errors into readable messages for you.

JSON:
``` json
{
    "type": "wait",
    "wait": {
        "type": "external",
        "value": {
            "type": "payment:dingconnect",
            "id": "PAYMENT_ID"
        }
    },
    "payment": {
        "provider": "dingconnect",
        "key": "name-of-your-credentials",
        "details": {
            "id": "PAYMENT_ID",
            "sku_code": "MTNG10",
            "send_value": 5.00,
            "send_currency_iso": "USD",
            "account_number": "{{field:MOBILE_QUESTION|e164}}",
            "distributor_ref": "survey_x_{{field:MOBILE_QUESTION|e164}}_1"
        }
    }
}
```

Notes:

1. The "wait" is not strictly necessary but likely desired!
2. `PAYMENT_ID` can be useful to keep track of multiple payments to the same person
   or different payments to different treatment arms. You need the same PAYMENT_ID
   in both the "wait" and the "payment" blocks.
3. the `key` is the name of the Generic Secret holding your DingConnect API key
   (see [Setting up your DingConnect API key](#setting-up-your-dingconnect-api-key)
   below).
4. `sku_code` identifies exactly what is being sent — a specific amount from a
   specific operator. See [Finding a SKU code](#finding-a-sku-code) below.
5. **`distributor_ref` is what prevents double payments.** DingConnect rejects a
   repeated `distributor_ref` instead of sending twice, so make it unique per person
   per payment — a combination of your shortcode and the phone number works well. It
   plays the same role that `custom_identifier` does for Reloadly. If you make it
   change between attempts (by putting a timestamp or random value in it), a retried
   payment **will** be sent twice.
6. `send_currency_iso` is optional and defaults to USD.
7. Phone number answers may contain trailing text (e.g. `+254712345678 use this`).
   Use the `|e164` transform to normalize them before they reach the payment
   provider. This matters most for `distributor_ref` — without normalization, two
   submissions of the same number with different trailing text produce different
   references, which defeats the duplicate protection described above. See
   [Interpolation Transforms](/docs/fly/reference/hidden/#interpolation-transforms).

You will have the following hidden fields that can be used for logic and error messages:

1. `e_payment_dingconnect_success` - will be "true" if the payment succeeded.
2. `e_payment_dingconnect_error_message` - an error message describing why it failed.
3. `e_payment_dingconnect_error_code` - DingConnect's own error code, e.g.
   `AccountNumberInvalid` or `InsufficientBalance`. Useful for branching on the
   reason: `AccountNumberInvalid` means you should re-ask for the number, while
   `InsufficientBalance` means your account needs funding and re-asking will not help.
4. `e_payment_dingconnect_id` - the PAYMENT_ID

### Some products need extra information

Some products — utility top-ups especially — need more than a phone number. An
electricity product may require a meter ID. Pass these with `settings`:

``` json
"details": {
    "id": "PAYMENT_ID",
    "sku_code": "NG_4X_TopUp",
    "send_value": 5.00,
    "account_number": "{{field:MOBILE_QUESTION|e164}}",
    "distributor_ref": "survey_x_{{field:MOBILE_QUESTION|e164}}_1",
    "settings": [
        {"name": "MeterId", "value": "{{field:METER_QUESTION}}"}
    ]
}
```

If a product requires a setting and you leave it out, the payment fails. The CLI
below shows which settings each product requires.

### Finding a SKU code

`sku_code` is the single most important field to get right, and it is not
guessable. Use the
[go-dingconnect](https://github.com/vlab-research/go-dingconnect) CLI to browse the
catalogue:

``` sh
go install github.com/vlab-research/go-dingconnect/cmd/dingconnect@latest

export DINGCONNECT_API_KEY=your_key

# Which operators exist in a country?
dingconnect providers --country NG

# What can be sent, at what price?
dingconnect products --country NG --provider MTNG
```

```
SKU          PROVIDER  SEND             RECEIVE                COMM  MODE     REQUIRES
NG_4X_TopUp  4XNG      2.00-105.00 USD  2246.29-117930.31 NGN  3.0%  Instant  MeterId
2ANG44349    2ANG      12.08 USD        10.00 USD              3.0%  Instant
```

`SEND` is what your account is charged; `RECEIVE` is what the participant gets. A
range means the product accepts any amount between those bounds, so `send_value`
must fall inside it. A single figure means the amount is fixed and any other
`send_value` is rejected. `REQUIRES` lists the mandatory `settings` for that product.

You can also check which operator a specific number belongs to:

``` sh
dingconnect lookup +2348031234567
```

And confirm a payment would work before putting it in a survey. This validates
everything and checks your balance without sending money or spending anything:

``` sh
dingconnect send --sku 2ANG44349 --value 12.08 \
  --account 2348031234567 --ref test-001
```

### Setting up your DingConnect API key

DingConnect uses a **Generic Secret**, so you can set it up yourself — there is no
separate DingConnect screen to find.

1. In DingConnect, go to **Account Settings → Developer** and generate an API key.
2. In the Fly dashboard, open **Connected Accounts** and create a new **Generic
   Secret**. Give it any variable name you like — `DINGCONNECT_API_KEY` is a
   sensible choice — and paste the API key as the value.
3. In your survey, set `payment.key` to that same variable name:

``` json
"payment": {
    "provider": "dingconnect",
    "key": "DINGCONNECT_API_KEY",
    "details": { ... }
}
```

The name is yours to choose, so one account can hold several DingConnect keys for
different studies — just point each survey at the right one.

Note that `key` names the secret; it does not contain the API key. Never paste the
key itself into the survey, which is shared with your collaborators and may be made
public.

If the name in `payment.key` doesn't match a secret you've created, the payment
fails with an error saying which secret was missing, so check that first if
payments fail immediately.

If your account has no funds, every payment fails with
`e_payment_dingconnect_error_code` set to `InsufficientBalance`, no matter how
correct the survey is. Check the balance with `dingconnect balance` before
debugging anything else.

## Payment - Generic HTTP Payment Endpoint

This allows you to send payments to an external API via any http request.

JSON:
``` json
{
    "type": "wait",
    "wait": {
        "type": "external",
        "value": {
            "type": "payment:http",
            "id": "PAYMENT_ID"
        }
    },
    "payment": {
        "provider": "http",
        "details": {
            "id": "PAYMENT_ID",
            "method": "POST",
            "url": "https://mypaymentprovider.com/send/money",
            "headers": {"Authorization": "Bearer << MYPROVIDER_TOKEN >>"},
            "body": { "phone": "{{field:MOBILE_QUESTION|e164}}", "amount": 100, "transaction_id": "survey_x_payment_1" },
            "errorMessage": "path.to.error.message"
        }
    }
}
```

Notes:

1. The "wait" is not strictly necessary but likely desired!
2. `PAYMENT_ID` can be useful to keep track of multiple payments to the same person or different payments to different treatment arms (a unique id per treatment arm).
3. The `body` and `headers` properties are optional.
4. You can pass secrets into the url, the headers, and/or the body. This is done with templating which uses the delimeters `<<` and `>>`. The secrets available are the secrets you create in the dashboard under "Generic Secrets".
5. `errorMessage` is a "json path", in dot notation, to extract the message provided in `e_payment_http_error_message`. If the status code is not 2XX, the service will consider it an error and expect a JSON body response. If the body is `{"error": {"code": "BAD_NUMBER", "message": "Please provide a valid mobile number"}}` then the `errorMessage` property should be `error.message` in order to extract the message "Please provide a valid mobile number".
6. If your HTTP payment endpoint requires the phone number as a string, make sure to wrap the reference to the previous question in quotes (`""`).

You will have the following hidden fields that can be used for logic and error messages:

1. `e_payment_http_success` - will be "true" if the payment succeeded.
2. `e_payment_http_error_message` - an error message, extracted as specified from error json.
3. `e_payment_http_id` - the PAYMENT_ID
4. `e_payment_http_response` - the response from the payment API.

## Payment - Tremendous

We can use our Generic HTTP Payment Endpoint type to make a request to [Tremendous](https://tremendous.com) for giving out gift cards.

First, you will need to create a new "Generic Secret" under Connected Accounts on the home screen of the dashboard. Give your secret a variable name of "TREMENDOUS_API_KEY" and a value equal to the API key of your Tremendous account.

Second, you will use the following JSON. Replace `product_id_that_you_want` with the product_id from Tremendous and replace `your_funding_source_id` with the funding source id from Tremendous. You can read how to get your funding source id from the api [here](https://developers.tremendous.com/docs/paying-for-orders#funding-sources). NOTE: DO NOT REPLACE "TREMENDOUS_API_KEY", that is a variable that will be filled with the value from "Generic Secrets" in the Fly dashboard. This ensures that you don't put your secret API KEY in the survey, which will be shared with your collaborators and potentially made public.

JSON:
``` json

{
  "type": "wait",
  "wait": {
    "type": "external",
    "value": {
      "type": "payment:http",
      "id": "giftcard_1"
    }
  },
  "payment": {
    "provider": "http",
    "details": {
      "id": "giftcard_1",
      "method": "POST",
      "url": "https://www.tremendous.com/api/v2/orders",
      "headers": {
        "Authorization": "Bearer << TREMENDOUS_API_KEY >>",
        "Content-Type": "application/json"
      },
      "body": {
        "external_id": "{{hidden:id}}_my_shortcode"      
        "payment": { "funding_source_id": "your_funding_source_id" },
        "rewards": [{
          "value": { "denomination": 5.0, "currency_code": "EUR" },
          "delivery": { "method": "LINK" },
          "recipient": { "name": "Study Participant" },
          "products": ["product_id_that_you_want"]
        }]
      },
      "errorMessage": "errors.message",
      "responsePath": "order.rewards.0.delivery.link|@tostr"
    }
  }
}
```
