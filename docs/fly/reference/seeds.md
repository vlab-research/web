---
title: Randomization
weight: 7
---

## Using Random Numbers for Randomizing Logic

Each respondent is given a set of random numbers, known as a "seed". Seeds work via hidden fields. Create a hidden field named `seed_N`, where `N` is replaced with the number of arms you wish to randomize. For example: `seed_2`, `seed_3`, `seed_4`, `seed_5`,..., `seed_100`.

This hidden field will have the assignment of each user, which will be an integer between 1 and N. For example, if you made a hidden field called `seed_3`, each user will have a value of that field equal to 1, 2, or 3.

Now use the hidden field in your logic jumps. If, for example, you create a hidden field called `seed_3`, then create logic jumps such that:

if `seed_3 == 1` do A, if `seed_3 == 2` do B, if `seed_3 == 3` do C.

## Using Multiple Random Numbers

Say you want to randomize twice in your survey, independently, what can you do? 

You can create multiple seeds, with the same bucket size, by using the format `seed_N_V` where `N` is replaced with the number of arms, as before, but `V` is used to represent a different version. For example: `seed_3`, `seed_3_1`, and `seed_3_2` will ensure that you can have three distinct random arms, each of which is independent from the other. 

## Testing Random Seeds

Random seeds can be tested just like any other hidden field, using the following format (testing seed_2):

https://m.me/YOURPAGEID?ref=form.YOURSHORTCODE.seed_2.YOURSEED

In this case, you should replace YOURSEED with either `1` or `2`.

## Analyzing seeds

Every user is given a long integer which is their random seed (i.e. 2843167128). A calculation is done on this integer to determine their `seed_N` or `seed_N_V`. In order to analyze the data, you will need to recreate this calculation. 

The formula for a basic `seed_N` is `seed_N = seed % N + 1`

For example: 

1. `seed_2 = seed % 2 + 1`
2. `seed_3 = seed % 3 + 1`

For multiple seeds, it gets a bit more complicated. In particular, you will need to first hash the integer `V` times using Farmhash 32-bit fingerprint, and then you apply the previous formula. 
