#TODO

##Store features as DB documents

-Project
--WindStuff
--CraneStuff
---Features
---Turbines
---Boundary
---Solution
---

Idea, let's wrap our original features to mongoengine documents What's the most appropiate way to do so?

Test: The easiest test is for the time being to wrap a project and store the information.

Current issue: On freaking dereference, the class doesn't load properly... I need to find out why. We know that it is stored properly in Mongo, we know that it is correctly linked to the parent project, it seems to be an issue of casting the data into the Document

So it fetches the information correctly, the issue is when casting it to its document class. Error should be in _document._from_son

Potential solution: Removing the __init__ call in features makes it kind of work. This is mostly solved!!

Now, why do we have such a SHITTY solution?

Good freaking lord, now we have a decent solution!


##Creating the Cost DB

I've created the backend part, not a big deal, I intend to have the cost managed using an angular x-editable thing. this way the user can crea/update/delete at will and in a single view. I've decided, for the time being, to use only a single cost page for it, rather than giving the user to create new costs in the layerlist view. 