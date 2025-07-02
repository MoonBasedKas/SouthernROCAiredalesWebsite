So this will be a website with a few pages.

We'll have a page with the males and females, a home page, about, breeding garuntee, contact us?

There is a logo its on their facebook page.

They want the main colors to be black and white.


# Research

Every website nowadays had that stupid nav bar at the top.
- For mobile websites the nav bar is often collapsed into a menu.
    - It seems that a common technique is whenever the screen is small have it display vertically and horizontally on larger screens.
    - Luckily css can handle this for us
        - @media screen and (max-width: 600px)
        - https://www.w3schools.com/howto/howto_js_topnav_responsive.asp
- I did find one website that just straight up gave the user the desktop verison though. (BAD IDEA)

For breeders that have multiple breeds they do a section for each breed.

Will want the date of birth, the gender, name, picture of the dog, and a way to contact on the page.

A blog has appeared on some.

Generally the entire page is not used rather its more like 50-75% of it.

Big 3 pages are home, about, and contact.

Reviews section if possibler would be nice.

Domain Name: AirdalesofSouthernROC.com

Writing the website with wordpress seems like it's going to be the choice as most the simplest options that include a domain
do wordpress.


# Techinical Requirements
## Must have
- Some serverlet
    - We are going to attempt using flask however, this is flexible. I can definitly change if needed.
- Sql database
- Domain name
- Hosting 
    - Pythonanywhere
        - I'll personally expirement with this
    - Hosting.com
        - VPS however, there is a good chance it only does php, which honestly could be fine
        - They do offer a free domain for a year.
        - SSL certs
    - Google cloud
        - I think its cheap, but I honestly don't know how much traffic southern gets.
        - pay per use
    - Azure
        - Could use ASP.
        - pay as you go.
    - AWS
        - If I could figure out what service I'd need
    - https://flask.palletsprojects.com/en/stable/deploying/
        - Recommended by flask
    - GoDaddy
        - Recommended by client


## Would be nice but not required
- Log in for admin.
    - Allow Southern to be able to partially maintain her website.
    - Obviously allow to add new dogs
    - Edit dogs already in.
    - Dog status.
- Secure file upload.

## Unlikely to add but could be useful.
- Allow admin to write blog posts.


## Meeting 2 notes
