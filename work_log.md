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

todo then:

- The user should be able to create, edit and delete costs (cost view)
-- Create the controller that power the editing of costs - DONE
-- Create the view that enables the user to create costs - DONE
- in LayerList, the user should be able to assign layers the corresponding costs - DONE

##Checking that things work as they are supposed to [12/30/2015].

I'm making a very quick overall check to see that things work as required as a user.

###Signup/login
Works.

###Project Navigation
- On create/open project it should move the user to the project's page. S.T. it is obvious that you are INSIDE a project and that you can track the status there.

###Wind Day
- Change icon in side bar

###Cost DB
- Change icon in side bar.

###Crane Path
- Layerlist should force at least ONE turbine and ONE boundary.
- we really need to implement the queue/task system.
- there's an error in the layerlist crap [TODO]

###Deployment
- No work done here yet. Should set up with docker compose