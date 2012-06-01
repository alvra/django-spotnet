.. _views:

.. py:module:: spotnet.views

Views
=====

These are all the views included in this app.


.. py:function:: search(request, [search=None, [cats=None, [scats=None]]])

   Show a list of posts. Filter by passing the optional arguments.


.. py:function:: viewpost(request, id)

   Show a single post.


.. py:function:: download(request, id, [dls=None])

   Download a post using a download server.
   Pass a downloadserver name,
   or it will the default download server.


.. py:function:: downloaded(request)

   Show the list of all downloaded posts.


.. py:function:: download_nzb(request, id)

   Download the nzb file for a spot.


.. py:function:: update(request)

   Start updating the spot database.
   This only works if you set the optional setting
   ``SPOTNET_UPDATE_ALLOW_INPAGE`` to ``True``.


Helpers
-------

.. py:function:: view_related_post_list(request, objects, page, title, [extra_actions={}])

   This is a helper function that other views can call to show
   a list of model instances that have a foreign key to a spotnet post.

   The view :py:func:`downloaded <spotnet.views.downloaded>` uses this helper.
   View the source for details on how to use this.

   :param request: the ``HttpRequest`` object
   :param objects: the queryset for a model that has a ``ForeignKey``
                   field to the spotnet ``Post`` model called ``post``
   :param page: the page number in the paginator
   :param title: the title string for this page
   :param extra_actions: a dict mapping action names to ``Action``
                         instances that can be applied to the
                         related objects
