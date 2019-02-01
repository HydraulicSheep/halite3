# Halite III
This is a repo for my Halite 3 Bot.

A huge thanks to TwoSigma and all the competition organizers for putting together such a great competition

## Writeup

I'm not particularly proud of my bot, considering that I only finished in place #503. However, I do believe that I had some good ideas going in my code and that I could have done better if I had spent more time.

The one feature that I am quite proud of was the selection of squares to move to. Although this didn't take into account enemy ship movements/positions, I used a solution to the [Assignment Problem](https://en.wikipedia.org/wiki/Assignment_problem). I did this through the Linear Optimization Algorithm in the Scipy library. This was quite efficient, I believe, giving me more time per turn to spend on computationally expensive calculations.
