## commentaire
Dans ce projet nous faisons utlisation des cla classe base view
## F()


## Handling race condition
If multiple users try to like the post simultaneously, the likes count may not update correctly due to race conditions.
handles in increase_like by doing a manyToMany in pst by adding likes_by
Key Improvements
Error Handling:

Used get_object_or_404 to handle the case where the Post object does not exist. This returns a 404 error instead of raising a server error.

Race Condition Prevention:

Used Django's F() expression to increment the likes field atomically. This ensures that concurrent requests do not overwrite each other.

Duplicate Like Prevention:

Added a check to ensure the user has not already liked the post. This is done by tracking users who liked the post in a ManyToManyField (see model changes below).

Dynamic Redirect:

The redirect URL ("post") is still hardcoded, but you can use Django's reverse function to make it more flexible:

## Request

## FBV (Function Based view)

## CBV

## concurence management with like button using F()

## Exceptions handling

## Features
index
blog
signin
signup
signout
create a post
profile
profile edit
view a post
add/save comment
delete comment
editpost
deletepost
increaselikes
decreaselikes