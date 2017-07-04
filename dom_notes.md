# Notes for Talk

## Welcome

* Thanks for inviting me - my research doesn't have an explicit focus on crowdsourcing or community participation *per se*, and I tend to have more of an interest in the mechanics of digital humanities and in particular databases.
  * This talk is somewhat at the geeky end of the discipline, but I want to be clear that I'm not just going to talk at you for twenty minutes about databases!
  * Instead, I'm going to discuss some of the ways that we link up data in DH, and introduce what may be a new type of datastore you've not come across - graph databases - and their potential for use in future digital humanities work.

##  The *Digital* in Digital Humanities

* This talk will focus on the "digital" in digital humanities.
  * Let's take a moment to reflect and see exactly what I mean by that: and how the "digital" and the "humanities" come together.
    * So, at their most fundamental level, computers are very simple machines that use the movement of electrons in a processor to perform logic. They combine the results of these movements, and store them, in order to process input and produce output.
    * By contrast, at the most sophisticated level, as users, we see computers do breathtaking things every day.
      * Routing
      * Social Media
      * Video Calling
    * As you might have guessed: quite a lot happens in this middle bit here, and it's quite important.
    * And, at the risk of simplifying massively, from a digital humanities perspective, this middle bit here is **what we do**.
    * If we look at a digital humanities project, for example the classic study of the Medici Family as a social network by Padgett and Ansell (1993) we can see how this works out.
      * At the very "humanities" end of the spectrum, we might have a question like "how was power wielded in 15th century Florence?"
      * And, digital end of the spectrum, we begin to model records of individuals and places in a network or graph, that we can process on a computer to model the properties of these entities, and reveal patterns of interactions that wouldn't be visible otherwise.

## **Brief** Historical Perspective: 3 Ages of the Digital in Digital Humanities

* Punch-card
* The WWW
* Big data
  * System of circles and arrows, where circles and arrows can stand for anything.
  * Graph database

## Databases Introduction: Relational vs. Graph

* Relational databases: what are they?
  * Relational algebra
  * Really bad at relationships
* Property graph model
  * Whiteboard friendly
  * Model the room, etc.?
* Index-free adjacency: lightening fast.

## Geographical Information in Digital Humanities

Now, in the humanities, we study people, events and their consequences. But, everything has to happen somewhere. How do we model the importance of this geographical information digitally?

* First off, how do we understand geographical information non-digitally?
  * Where am I? Lots of ways to answer that question.
* Each introduces its own biases etc.
  * Prime meridian
  * Ordinance survey
  * US land parcels
* These are modelled into our system
* How to link place and non-place data though?
  * especially volunteered geographical information
  * Examples of different types of place and non-place data.
* Circles and arrows, where circles and arrows can stand for anything.
  * Model spatial information, but in the same way as non-spatial information
  * Use circles and arrows
  * R-tree index
  * Messily link to streets, etc., etc.

## London Pubs Example

This is all very good in theory, but when I was putting together this talk, I decided I needed an example to demonstrate the possibilities for using these kinds of database.

So, I thought, summer students in London - what might be a nice example close to home that would interest you, and me, and hopefully all of us. What might we have experience of?

Then it dawned on me: the pub.

Combine sources of messy volunteered geographical information to a useful end. 
